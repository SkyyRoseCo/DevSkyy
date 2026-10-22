"""
Tests for CostTracker.

Uses fakeredis to avoid requiring a live Redis instance.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import fakeredis
import pytest

from skyyrose.elite_studio.queue.cost_tracker import (
    _COST_KEY_PREFIX,
    _COST_TTL_SECONDS,
    _TOTAL_COST_SORTED_SET,
    PRICING_PER_1K,
    CostBudgetExceeded,
    CostTracker,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def fake_redis_server():
    return fakeredis.FakeServer()


@pytest.fixture()
def fake_redis(fake_redis_server):
    return fakeredis.FakeRedis(server=fake_redis_server, decode_responses=True)


@pytest.fixture()
def tracker(fake_redis):
    ct = CostTracker()
    ct._redis = fake_redis
    return ct


@pytest.fixture(autouse=True)
def isolated_budget_configuration(monkeypatch):
    monkeypatch.delenv("ELITE_STUDIO_COST_CAP_USD", raising=False)
    monkeypatch.delenv("ELITE_STUDIO_COST_CAP_ALLOW_DEGRADED", raising=False)


# ---------------------------------------------------------------------------
# record()
# ---------------------------------------------------------------------------


def test_record_stores_token_count(tracker, fake_redis):
    tracker.record("job-1", "gemini", 1000, 0.075)

    val = fake_redis.hget(f"{_COST_KEY_PREFIX}job-1", "gemini_tokens")
    assert float(val) == 1000.0


def test_record_accumulates_total_usd(tracker, fake_redis):
    tracker.record("job-1", "gemini", 1000, 0.075)
    tracker.record("job-1", "openai", 500, 2.50)

    total = float(fake_redis.hget(f"{_COST_KEY_PREFIX}job-1", "total_usd"))
    assert abs(total - 2.575) < 1e-6


def test_record_multiple_providers(tracker, fake_redis):
    tracker.record("job-2", "gemini", 2000, 0.15)
    tracker.record("job-2", "anthropic", 1000, 3.0)
    tracker.record("job-2", "openai", 500, 2.5)

    total = float(fake_redis.hget(f"{_COST_KEY_PREFIX}job-2", "total_usd"))
    assert abs(total - 5.65) < 1e-5


def test_record_sets_ttl(tracker, fake_redis):
    tracker.record("job-ttl", "gemini", 100, 0.01)
    ttl = fake_redis.ttl(f"{_COST_KEY_PREFIX}job-ttl")
    assert ttl > 0


def test_record_adds_to_timeline(tracker, fake_redis):
    tracker.record("job-tl", "openai", 200, 1.0)
    count = fake_redis.zcard(_TOTAL_COST_SORTED_SET)
    assert count >= 1


def test_record_bounds_timeline_retention_without_losing_recent_calls(
    tracker, fake_redis, monkeypatch
):
    now = datetime.now(UTC)
    monkeypatch.setattr(
        "skyyrose.elite_studio.queue.cost_tracker.datetime", SimpleNamespace(now=lambda tz: now)
    )
    cutoff = now.timestamp() - _COST_TTL_SECONDS
    fake_redis.zadd(
        _TOTAL_COST_SORTED_SET,
        {
            "expired:openai:99.000000": cutoff - 1,
            "boundary:openai:3.000000": cutoff,
            "retained:openai:4.000000": cutoff + 1,
            "yesterday:openai:5.000000": (now - timedelta(hours=25)).timestamp(),
        },
    )

    tracker.record("same-job", "openai", 100, 1.0)
    tracker.record("same-job", "openai", 100, 1.0)

    assert fake_redis.zscore(_TOTAL_COST_SORTED_SET, "expired:openai:99.000000") is None
    assert fake_redis.zscore(_TOTAL_COST_SORTED_SET, "boundary:openai:3.000000") == cutoff
    assert fake_redis.zcard(_TOTAL_COST_SORTED_SET) == 5
    assert tracker.get_total_cost() == 2.0
    assert tracker.get_total_cost(since_hours=168) == 14.0


def test_record_refreshes_timeline_expiry(tracker, fake_redis):
    tracker.record("first", "openai", 100, 1.0)
    assert 0 < fake_redis.ttl(_TOTAL_COST_SORTED_SET) <= _COST_TTL_SECONDS
    fake_redis.expire(_TOTAL_COST_SORTED_SET, 1)

    tracker.record("second", "openai", 100, 1.0)

    assert fake_redis.ttl(_TOTAL_COST_SORTED_SET) > 1
    assert tracker.get_total_cost() == 2.0


def test_timeline_expires_after_inactivity(tracker, fake_redis, monkeypatch):
    tracker.record("first", "openai", 100, 1.0)
    after_retention = datetime.now(UTC).timestamp() + _COST_TTL_SECONDS + 1

    with monkeypatch.context() as clock:
        clock.setattr("time.time", lambda: after_retention)
        assert not fake_redis.exists(_TOTAL_COST_SORTED_SET)


def test_record_degrades_when_redis_unavailable(monkeypatch):
    """record() must not raise when Redis is down."""
    ct = CostTracker()

    def unavailable():
        raise RuntimeError("synthetic Redis unavailable")

    monkeypatch.setattr(ct, "_get_redis", unavailable)
    # Should log a warning but not raise
    ct.record("job-x", "gemini", 100, 0.01)


# ---------------------------------------------------------------------------
# get_job_cost()
# ---------------------------------------------------------------------------


def test_get_job_cost_returns_accumulated_total(tracker):
    tracker.record("job-gc", "gemini", 1000, 0.5)
    tracker.record("job-gc", "anthropic", 500, 1.5)

    cost = tracker.get_job_cost("job-gc")
    assert abs(cost - 2.0) < 1e-6


def test_get_job_cost_returns_zero_for_unknown_job(tracker):
    assert tracker.get_job_cost("nonexistent-job") == 0.0


def test_get_job_cost_returns_zero_when_redis_unavailable(monkeypatch):
    ct = CostTracker()
    # Patch _get_redis to simulate total unavailability (setting _redis=None
    # alone doesn't prevent reconnection when a live Redis is present in CI).
    monkeypatch.setattr(ct, "_get_redis", lambda: None)
    assert ct.get_job_cost("job-x") == 0.0


# ---------------------------------------------------------------------------
# get_total_cost()
# ---------------------------------------------------------------------------


def test_get_total_cost_sums_within_window(tracker, fake_redis):
    tracker.record("job-tc1", "gemini", 1000, 1.0)
    tracker.record("job-tc2", "openai", 500, 2.0)

    total = tracker.get_total_cost(since_hours=24)
    assert total >= 3.0


def test_get_total_cost_excludes_old_entries(tracker, fake_redis):
    # Insert a timeline entry with an old timestamp (25 hours ago)
    old_score = (datetime.now(UTC) - timedelta(hours=25)).timestamp()
    fake_redis.zadd(_TOTAL_COST_SORTED_SET, {"old-job:gemini:9.99": old_score})

    # Only add a fresh entry
    tracker.record("job-fresh", "anthropic", 100, 0.30)

    total = tracker.get_total_cost(since_hours=24)
    assert total < 9.99 + 0.30 + 0.01  # old entry must be excluded


def test_get_total_cost_returns_zero_when_redis_unavailable(monkeypatch):
    ct = CostTracker()
    # Patch _get_redis to simulate total unavailability (setting _redis=None
    # alone doesn't prevent reconnection when a live Redis is present in CI).
    monkeypatch.setattr(ct, "_get_redis", lambda: None)
    assert ct.get_total_cost() == 0.0


def test_get_total_cost_empty_timeline_returns_zero(tracker):
    assert tracker.get_total_cost(since_hours=1) == 0.0


def test_identical_calls_both_count_in_rolling_total(tracker, fake_redis):
    tracker.record("same-job", "openai", 100, 1.0)
    tracker.record("same-job", "openai", 100, 1.0)
    assert tracker.get_job_cost("same-job") == 2.0
    assert tracker.get_total_cost() == 2.0
    assert fake_redis.zcard(_TOTAL_COST_SORTED_SET) == 2


def test_repeated_calls_cannot_bypass_budget(tracker, monkeypatch):
    monkeypatch.setenv("ELITE_STUDIO_COST_CAP_USD", "1.5")
    tracker.record("same-job", "openai", 100, 1.0)
    tracker.record("same-job", "openai", 100, 1.0)
    with pytest.raises(CostBudgetExceeded):
        tracker.check_budget()


def test_cached_redis_query_failure_denies_budget_but_report_degrades(tracker, monkeypatch):
    def unavailable(*args, **kwargs):
        raise ConnectionError("synthetic query failure")

    monkeypatch.setattr(tracker._redis, "zrangebyscore", unavailable)
    with pytest.raises(CostBudgetExceeded):
        tracker.check_budget(1.0)
    assert tracker.get_total_cost() == 0.0


def test_query_failure_requires_explicit_degraded_opt_in(tracker, monkeypatch):
    def unavailable(*args, **kwargs):
        raise ConnectionError("synthetic query failure")

    monkeypatch.setattr(tracker._redis, "zrangebyscore", unavailable)
    monkeypatch.setenv("ELITE_STUDIO_COST_CAP_ALLOW_DEGRADED", "1")
    tracker.check_budget(1.0)


@pytest.mark.parametrize(
    "entry",
    [
        "broken",
        "broken:0",
        "job:bogus:0",
        ":openai:0",
        " :openai:0",
        "job::0",
        "job:openai::0",
        "job:openai:not-a-uuid:0",
        "job:openai:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA:0",
        "job:bogus:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa:0",
        "job:openai:garbage",
        "job:openai:nan",
        "job:openai:inf",
        "job:openai:-1",
    ],
)
def test_invalid_timeline_data_denies_budget(tracker, fake_redis, entry):
    fake_redis.zadd(_TOTAL_COST_SORTED_SET, {entry: datetime.now(UTC).timestamp()})
    with pytest.raises(CostBudgetExceeded):
        tracker.check_budget(1.0)


@pytest.mark.parametrize(
    "entry",
    [
        "elite:br-001:legacy:openai:2.000000",
        "job:openai:anthropic:2.000000",
        "elite:br-001:current:openai:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa:2.000000",
    ],
)
def test_timeline_accepts_supported_suffixes_with_colons_in_job_ids(tracker, fake_redis, entry):
    fake_redis.zadd(_TOTAL_COST_SORTED_SET, {entry: datetime.now(UTC).timestamp()})

    assert tracker.get_total_cost() == 2.0
    tracker.check_budget(1.0)


def test_reporting_rejects_windows_beyond_retained_history(tracker):
    with pytest.raises(ValueError, match="retention"):
        tracker.get_total_cost(since_hours=169)


def test_overflowed_timeline_denies_budget_but_report_degrades(tracker, fake_redis):
    now = datetime.now(UTC).timestamp()
    fake_redis.zadd(
        _TOTAL_COST_SORTED_SET,
        {"first:openai:1e308": now, "second:openai:1e308": now},
    )

    with pytest.raises(CostBudgetExceeded):
        tracker.check_budget()
    assert tracker.get_total_cost() == 0.0


def test_legacy_members_and_new_records_share_window(tracker, fake_redis):
    now = datetime.now(UTC)
    fake_redis.zadd(
        _TOTAL_COST_SORTED_SET,
        {
            "legacy:openai:2.000000": now.timestamp(),
            "old:openai:9.000000": (now - timedelta(hours=25)).timestamp(),
        },
    )
    tracker.record("current", "openai", 100, 1.0)
    assert tracker.get_total_cost() == 3.0


def test_verified_total_and_projected_cost_enforce_cap(tracker, monkeypatch):
    monkeypatch.setenv("ELITE_STUDIO_COST_CAP_USD", "2")
    tracker.record("job", "openai", 100, 1.0)
    tracker.check_budget(1.0)
    with pytest.raises(CostBudgetExceeded):
        tracker.check_budget(1.01)


# ---------------------------------------------------------------------------
# estimate_cost() — static helper
# ---------------------------------------------------------------------------


def test_estimate_cost_gemini():
    cost = CostTracker.estimate_cost("gemini", 1000)
    assert abs(cost - PRICING_PER_1K["gemini"]) < 1e-9


def test_estimate_cost_openai():
    cost = CostTracker.estimate_cost("openai", 1000)
    assert abs(cost - PRICING_PER_1K["openai"]) < 1e-9


def test_estimate_cost_anthropic():
    cost = CostTracker.estimate_cost("anthropic", 1000)
    assert abs(cost - PRICING_PER_1K["anthropic"]) < 1e-9


def test_estimate_cost_unknown_provider_returns_zero():
    cost = CostTracker.estimate_cost("unknown_provider", 1000)
    assert cost == 0.0


def test_estimate_cost_zero_tokens():
    assert CostTracker.estimate_cost("gemini", 0) == 0.0
