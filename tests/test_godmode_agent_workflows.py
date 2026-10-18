"""Behavioral qualification of the GOD MODE worker/reviewer boundary (offline fixtures)."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest

from skyyrose.godmode_runtime import RuntimeConflict
from skyyrose.godmode_runtime.agent_packets import verify_coverage
from tests.test_godmode_runtime import runtime  # noqa: F401


@pytest.fixture
def configured(runtime, monkeypatch):  # noqa: F811
    plan = {
        "scope": "BOUNDED_AGENT_ANALYSIS_NO_PRODUCTION",
        "provider_dispatch": True,
        "paid_calls": True,
        "agent_contract": {
            "available": True,
            "claude_model": "claude-opus-5-5",
            "codex_model": "gpt-6.1-sol",
            "timeout_seconds": 5,
        },
        "source_packet": {
            "required_skus": ["br-001", "sg-001"],
            "products": [],
            "memory_snapshot": [],
        },
        "allowance": {"claude_max_budget_usd": 1.0},
    }
    monkeypatch.setattr(runtime, "_agent_plan", lambda workflow: copy.deepcopy(plan))
    return runtime, plan


def test_no_model_dispatch_without_exact_approval(configured, monkeypatch):
    r, _ = configured
    calls = []
    monkeypatch.setattr(r, "_agent_step", lambda row, stage: calls.append(stage))
    run = r.create("skyyrose", "fashion-campaign-analysis", "agent-test-1", "operator")
    with pytest.raises(RuntimeConflict):
        r.execute(run["id"], run["plan_hash"], "operator")
    assert calls == []


def test_approved_worker_then_separate_review_once(configured, monkeypatch):
    r, _ = configured
    calls = []

    def stage(row, name):
        calls.append(name)
        return {
            "id": name,
            "status": "PASSED",
            "artifact": (
                {"covered_skus": ["br-001", "sg-001"]}
                if name == "claude-worker"
                else {"verdict": "PASS"}
            ),
            "human_acceptance": "NOT_GRANTED",
        }

    monkeypatch.setattr(r, "_agent_step", stage)
    run = r.create("skyyrose", "fashion-campaign-analysis", "agent-test-2", "operator")
    r.approve(run["id"], run["plan_hash"], "owner")
    out = r.execute(run["id"], run["plan_hash"], "operator")
    assert out["status"] == "SUCCEEDED" and calls == ["claude-worker", "codex-reviewer"]
    assert out["reviews"] == []
    assert sum(e["kind"] == "AGENT_ALLOWANCE_RESERVED" for e in out["events"]) == 1
    assert out["approval"] is None
    with pytest.raises(RuntimeConflict):
        r.execute(run["id"], run["plan_hash"], "operator")
    assert len(calls) == 2


def test_changed_model_revokes_approval_before_dispatch(configured, monkeypatch):
    r, plan = configured
    run = r.create("skyyrose", "fashion-skill-analysis", "agent-model-3", "operator")
    r.approve(run["id"], run["plan_hash"], "owner")
    plan["agent_contract"]["claude_model"] = "other-model"
    with pytest.raises(RuntimeConflict):
        r.execute(run["id"], run["plan_hash"], "operator")
    assert r.get(run["id"])["status"] == "INVALIDATED"
    assert not any(e["kind"] == "AGENT_ALLOWANCE_RESERVED" for e in r.get(run["id"])["events"])


def test_failed_reviewer_blocks_workflow(configured, monkeypatch):
    r, _ = configured
    monkeypatch.setattr(
        r,
        "_agent_step",
        lambda row, stage: {
            "id": stage,
            "status": "FAILED" if stage == "codex-reviewer" else "PASSED",
            "artifact": {},
        },
    )
    run = r.create("skyyrose", "fashion-skill-analysis", "review-fail-4", "operator")
    r.approve(run["id"], run["plan_hash"], "owner")
    assert r.execute(run["id"], run["plan_hash"], "operator")["status"] == "FAILED"


def test_every_preorder_exactly_once():
    p = {"required_skus": ["br-001", "sg-001"]}
    verify_coverage(p, {"covered_skus": ["sg-001", "br-001"]})
    for covered in [["br-001"], ["br-001", "br-001"], ["br-001", "sg-001", "invented"]]:
        with pytest.raises(ValueError):
            verify_coverage(p, {"covered_skus": covered})


def test_review_receipt_cannot_grant_human_acceptance(configured, monkeypatch):
    r, plan = configured
    from skyyrose.godmode_runtime import agent_adapters as adapters

    monkeypatch.setattr(
        adapters,
        "run_stage",
        lambda *args, **kwargs: {
            "id": "claude-worker",
            "status": "PASSED",
            "artifact": {"covered_skus": ["br-001", "sg-001"]},
        },
    )
    run = r.create("skyyrose", "fashion-skill-analysis", "human-gate-5", "operator")
    with r.connect() as c:
        row = r._get(c, run["id"])
    result = r._agent_step(row, "claude-worker")
    assert result["human_acceptance"] == "NOT_GRANTED" and result["production_authority"] is False


def test_actual_canonical_packets_cover_every_preorder(tmp_path):
    from skyyrose.godmode_runtime.agent_packets import build_packet
    from skyyrose.godmode_runtime.service import Runtime

    root = Path(__file__).resolve().parents[1]
    team = Path("/Users/theceo/plugins/fashion-theme-team")
    if not team.exists():
        pytest.skip("Workstation canonical Fashion package unavailable")
    r = Runtime(root, team, tmp_path / "state.sqlite")
    for workflow in ["fashion-campaign-analysis", "fashion-skill-analysis"]:
        p = build_packet(root, team, workflow, r._sources(), [])
        assert len(p["products"]) == len(p["required_skus"]) > 0
        assert len({p["sku"] for p in p["products"]}) == len(p["required_skus"])
        assert p["memory_snapshot"] == []
        assert p == build_packet(root, team, workflow, r._sources(), [])


def test_reservation_limit_retained_after_failed_run(configured, monkeypatch):
    r, _ = configured
    monkeypatch.setattr(
        r, "_agent_step", lambda row, stage: {"id": stage, "status": "FAILED", "usage": "UNKNOWN"}
    )
    for index in range(2):
        run = r.create("skyyrose", "fashion-skill-analysis", f"reserve-fail-{index}", "operator")
        r.approve(run["id"], run["plan_hash"], "owner")
        assert r.execute(run["id"], run["plan_hash"], "operator")["status"] == "FAILED"
    run = r.create("skyyrose", "fashion-skill-analysis", "third-reservation", "operator")
    r.approve(run["id"], run["plan_hash"], "owner")
    with pytest.raises(RuntimeConflict, match="allowance exhausted"):
        r.execute(run["id"], run["plan_hash"], "operator")


def test_pretransport_attestation_is_one_replacement_and_timeout_stays_reserved(
    configured, monkeypatch
):
    r, _ = configured
    monkeypatch.setattr(
        r,
        "_agent_step",
        lambda row, stage: {
            "id": stage,
            "status": "FAILED",
            "error_code": "timeout",
            "usage": "UNKNOWN",
        },
    )
    ids = []
    for index in range(2):
        run = r.create("skyyrose", "fashion-skill-analysis", f"reconcile-{index}", "operator")
        r.approve(run["id"], run["plan_hash"], "owner")
        r.execute(run["id"], run["plan_hash"], "operator")
        ids.append(run["id"])
    # Trusted offline-harness attestation; no browser/API method can create it.
    for _ in range(2):
        with r.transaction() as conn:
            if not conn.execute(
                "SELECT 1 FROM events WHERE run_id=? AND kind='AGENT_NO_DISPATCH_CONFIRMED'",
                (ids[0],),
            ).fetchone():
                r.event(
                    conn,
                    ids[0],
                    "AGENT_NO_DISPATCH_CONFIRMED",
                    "trusted-local-proof",
                    {"branch": "installed_sdk_pretransport_validation"},
                )
    replacement = r.create("skyyrose", "fashion-skill-analysis", "replacement-one", "operator")
    r.approve(replacement["id"], replacement["plan_hash"], "owner")
    r.execute(replacement["id"], replacement["plan_hash"], "operator")
    extra = r.create("skyyrose", "fashion-skill-analysis", "replacement-two", "operator")
    r.approve(extra["id"], extra["plan_hash"], "owner")
    with pytest.raises(RuntimeConflict, match="allowance exhausted"):
        r.execute(extra["id"], extra["plan_hash"], "operator")
    events = r.get(ids[0])["events"]
    assert sum(e["kind"] == "AGENT_ALLOWANCE_RESERVED" for e in events) == 1
    assert sum(e["kind"] == "AGENT_NO_DISPATCH_CONFIRMED" for e in events) == 1
    assert not any(e["kind"] == "AGENT_NO_DISPATCH_CONFIRMED" for e in r.get(ids[1])["events"])
