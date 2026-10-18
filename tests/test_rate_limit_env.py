"""Env-configurable default rate limits (security/rate_limiting.py).

The limiter reads its defaults when it is constructed, so each test sets the
environment and then builds a fresh AdvancedRateLimiter.
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from security.rate_limiting import DEFAULT_RULE_LIMITS, AdvancedRateLimiter, RateLimitType

_ENV_NAMES = [
    f"RATE_LIMIT_{prefix}_{suffix}"
    for prefix, _ in DEFAULT_RULE_LIMITS.values()
    for suffix in ("PER_MINUTE", "PER_HOUR", "BURST")
]


@pytest.fixture(autouse=True)
def _clean_rate_limit_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in _ENV_NAMES:
        monkeypatch.delenv(name, raising=False)


def _limits(limiter: AdvancedRateLimiter, limit_type: RateLimitType) -> tuple[int, int, int]:
    rule = limiter.default_rules[limit_type]
    return rule.requests_per_minute, rule.requests_per_hour, rule.burst_limit


def test_defaults_unchanged_without_env() -> None:
    limiter = AdvancedRateLimiter()

    assert _limits(limiter, RateLimitType.IP_BASED) == (100, 6000, 200)
    assert _limits(limiter, RateLimitType.USER_BASED) == (200, 12000, 400)
    assert _limits(limiter, RateLimitType.API_KEY_BASED) == (1000, 60000, 2000)
    assert [rule.name for rule in limiter.default_rules.values()] == [
        "default_ip",
        "default_user",
        "default_api_key",
    ]


def test_per_minute_override_scales_hour_and_burst(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RATE_LIMIT_IP_PER_MINUTE", "300")

    limiter = AdvancedRateLimiter()

    assert _limits(limiter, RateLimitType.IP_BASED) == (300, 18000, 600)
    assert _limits(limiter, RateLimitType.USER_BASED) == (200, 12000, 400)


def test_explicit_hour_and_burst_win(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RATE_LIMIT_API_KEY_PER_MINUTE", "2500")
    monkeypatch.setenv("RATE_LIMIT_API_KEY_PER_HOUR", "90000")
    monkeypatch.setenv("RATE_LIMIT_API_KEY_BURST", "4000")

    limiter = AdvancedRateLimiter()

    assert _limits(limiter, RateLimitType.API_KEY_BASED) == (2500, 90000, 4000)


def test_blank_value_uses_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RATE_LIMIT_USER_PER_MINUTE", "   ")

    limiter = AdvancedRateLimiter()

    assert _limits(limiter, RateLimitType.USER_BASED) == (200, 12000, 400)


@pytest.mark.parametrize("raw", ["abc", "12.5", "0", "-5"])
def test_invalid_value_fails_closed(monkeypatch: pytest.MonkeyPatch, raw: str) -> None:
    monkeypatch.setenv("RATE_LIMIT_IP_PER_MINUTE", raw)

    with pytest.raises(ValueError, match="RATE_LIMIT_IP_PER_MINUTE must be a positive integer"):
        AdvancedRateLimiter()


def _app_with(limiter: AdvancedRateLimiter) -> FastAPI:
    app = FastAPI()

    @app.middleware("http")
    async def rate_limit(request: Request, call_next):
        from fastapi.responses import JSONResponse
        from starlette.exceptions import HTTPException

        try:
            await limiter.enforce_rate_limit(request)
        except HTTPException as exc:
            return JSONResponse(
                {"detail": exc.detail}, status_code=exc.status_code, headers=exc.headers
            )
        return await call_next(request)

    @app.get("/ping")
    async def ping() -> dict[str, str]:
        return {"ok": "yes"}

    return app


def test_ip_override_is_enforced_over_http(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RATE_LIMIT_IP_PER_MINUTE", "3")
    client = TestClient(_app_with(AdvancedRateLimiter()))

    statuses = [client.get("/ping").status_code for _ in range(4)]

    assert statuses == [200, 200, 200, 429]
    blocked = client.get("/ping")
    assert blocked.headers["X-RateLimit-Limit"] == "3"


def test_raised_ip_limit_admits_more_than_old_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RATE_LIMIT_IP_PER_MINUTE", "150")
    client = TestClient(_app_with(AdvancedRateLimiter()))

    statuses = [client.get("/ping").status_code for _ in range(150)]

    assert statuses.count(200) == 150
    assert client.get("/ping").status_code == 429
