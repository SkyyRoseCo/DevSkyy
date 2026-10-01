"""Deterministic accounting tests; all charges are synthetic, no provider execution."""

import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from skyyrose.elite_studio.creative.spend_ledger import (
    LedgerError,
    SpendAuthority,
    SpendDenied,
    SpendGrant,
    SpendLedger,
)


@pytest.fixture
def setup(tmp_path):
    now = datetime(2026, 9, 24, tzinfo=UTC)
    authority = SpendAuthority(Ed25519PrivateKey.generate())
    key = b"synthetic-test-integrity-key-only!" * 2
    ledger = SpendLedger(tmp_path / "ledger.sqlite", authority.public_key, key, clock=lambda: now)
    grant = SpendGrant(
        "g1",
        "job",
        ("simulator",),
        ("test",),
        {"usd": "10", "renders": "20"},
        {"usd": "4", "renders": "2"},
        (now + timedelta(hours=1)).isoformat(),
        direction_limits={"A": {"usd": "6"}, "B": {"usd": "6"}},
        stage_limits={"PROBE": {"usd": "8"}, "FINAL": {"usd": "2"}},
    )
    ledger.install_grant(authority.issue(grant))
    return ledger, authority, grant, now, key


def reserve(ledger, operation_id="op1", **changes):
    defaults = dict(
        grant_id="g1",
        job_id="job",
        provider="simulator",
        purpose="test",
        direction="A",
        stage="PROBE",
        maximum={"usd": "2", "renders": "1"},
        reason="Synthetic probe",
        contract_digest="synthetic-contract-sha",
        metadata={"contract": {"version": 1}},
    )
    return ledger.reserve(operation_id, **(defaults | changes))


def finish(ledger, operation_id="op1", actual=None, outcome="COMPLETED", review=True):
    ledger.mark_submitted(operation_id)
    ledger.record_outcome(operation_id, outcome, provider_operation_id="sim-" + operation_id)
    ledger.reconcile(
        operation_id, actual or {"usd": "2", "renders": "1"}, "synthetic-billing-" + operation_id
    )
    if review:
        ledger.record_review(operation_id, {"status": "PASS", "reviewer": "simulator-independent"})


def test_atomic_concurrency_only_one_unresolved_call(setup):
    ledger, *_ = setup

    def attempt(index):
        try:
            reserve(ledger, "op" + str(index))
            return True
        except SpendDenied:
            return False

    with ThreadPoolExecutor(max_workers=3) as pool:
        assert sum(pool.map(attempt, range(3))) == 1
    assert ledger.report("g1")["held"]["usd"] == Decimal("2")


def test_delayed_billing_does_not_release_and_unreviewed_blocks(setup):
    ledger, *_ = setup
    reserve(ledger)
    ledger.mark_submitted("op1")
    ledger.record_outcome("op1", "COMPLETED")
    ledger.record_review("op1", {"status": "PASS"})
    assert ledger.report("g1")["available"]["usd"] == 8
    with pytest.raises(SpendDenied):
        reserve(ledger, "op2")
    ledger.reconcile("op1", {"usd": "1.25", "renders": 1}, "synthetic invoice")
    assert ledger.report("g1")["available"]["usd"] == Decimal("8.75")
    reserve(ledger, "op2")
    finish(ledger, "op2", review=False)
    with pytest.raises(SpendDenied):
        reserve(ledger, "op3")


@pytest.mark.parametrize(
    "maximum",
    [
        {},
        {"usd": "NaN", "renders": 1},
        {"usd": -1, "renders": 1},
        {"usd": 0.1, "renders": 1},
        {"usd": "Infinity", "renders": 1},
        {"usd": "1e100", "renders": 1},
        {"usd": 1},
        {"made_up_unit": 1},
    ],
)
def test_unknown_or_unbounded_cost_denied(setup, maximum):
    ledger, *_ = setup
    with pytest.raises(LedgerError):
        reserve(ledger, maximum=maximum)
    assert not ledger.operations("job")


def test_most_restrictive_caps_and_decimal_precision(setup):
    ledger, *_ = setup
    with pytest.raises(SpendDenied):
        reserve(ledger, maximum={"usd": "4.01", "renders": 1})
    with pytest.raises(SpendDenied):
        reserve(ledger, stage="FINAL", maximum={"usd": "2.01", "renders": 1})
    reserve(ledger, maximum={"usd": "3", "renders": 1})
    finish(ledger, actual={"usd": "3", "renders": 1})
    reserve(ledger, "op2", maximum={"usd": "3", "renders": 1})
    finish(ledger, "op2", actual={"usd": "3", "renders": 1})
    with pytest.raises(SpendDenied):
        reserve(ledger, "op3", maximum={"usd": ".000000000000000001", "renders": 1})
    reserve(ledger, "op3", direction="B")
    finish(ledger, "op3")
    with pytest.raises(SpendDenied):
        reserve(ledger, "op4", direction="B", maximum={"usd": ".1", "renders": 1})


def test_signed_grants_cannot_be_injected_or_changed(setup):
    ledger, authority, grant, *_ = setup
    envelope = authority.issue(grant)
    envelope["body"]["grant"]["limits"]["usd"] = "99999"
    with pytest.raises(SpendDenied):
        ledger.install_grant(envelope)
    with pytest.raises(SpendDenied):
        ledger.install_grant({"authorized": True, "limits": {"usd": "99999"}})
    with pytest.raises(SpendDenied):
        ledger.install_grant(
            authority.issue(replace(grant, limits={"usd": "99999", "renders": 20}))
        )
    other_authority = SpendAuthority(Ed25519PrivateKey.generate())
    with pytest.raises(SpendDenied):
        ledger.install_grant(other_authority.issue(grant))
    assert ledger.report("g1")["authorized"]["usd"] == 10


@pytest.mark.parametrize(
    "field,value",
    [
        ("job_id", "other-job"),
        ("provider", "expensive-fallback"),
        ("purpose", "publish"),
        ("direction", "C"),
        ("stage", "UNALLOCATED"),
    ],
)
def test_scope_cannot_escape(setup, field, value):
    ledger, *_ = setup
    with pytest.raises(SpendDenied):
        reserve(ledger, **{field: value})


def test_expiry_revocation_closure_stop_submission_not_accounting(setup):
    ledger, authority, grant, now, key = setup
    reserve(ledger)
    ledger.apply_authority(authority.command("REVOKE_GRANT", "g1", "Owner revokes", "revoke1"))
    with pytest.raises(SpendDenied):
        ledger.mark_submitted("op1")
    ledger.release_unsubmitted("op1", "Revoked before any submission")
    assert ledger.report("g1")["held"]["usd"] == 0
    ledger.install_grant(authority.issue(replace(grant, grant_id="g2")))
    ledger.apply_authority(authority.command("CLOSE_JOB", "job", "Done", "close1"))
    with pytest.raises(SpendDenied):
        reserve(ledger, "op2", grant_id="g2")
    expired = SpendLedger(
        ledger.database, authority.public_key, key, clock=lambda: now + timedelta(days=1)
    )
    with pytest.raises(SpendDenied):
        reserve(expired, "op3", grant_id="g2")


def test_expired_grant_alone_denies(setup):
    ledger, authority, _, now, key = setup
    restarted = SpendLedger(
        ledger.database, authority.public_key, key, clock=lambda: now + timedelta(days=1)
    )
    with pytest.raises(SpendDenied, match="expired"):
        reserve(restarted)


def test_restart_recovery_and_idempotency(setup):
    ledger, authority, _, now, key = setup
    initial = reserve(ledger)
    assert reserve(ledger) == initial
    with pytest.raises(SpendDenied):
        reserve(ledger, maximum={"usd": "3", "renders": 1})
    ledger.mark_submitted("op1")
    restarted = SpendLedger(ledger.database, authority.public_key, key, clock=lambda: now)
    assert restarted.recovery_required("job")[0]["idempotency_key"] == "op1"
    with pytest.raises(SpendDenied):
        restarted.mark_submitted("op1")
    with pytest.raises(SpendDenied):
        reserve(restarted, "new-after-crash")
    restarted.record_outcome("op1", "RECONCILIATION_REQUIRED", evidence={"timeout": True})
    restarted.record_outcome(
        "op1", "COMPLETED", provider_operation_id="recovered-existing-provider-op"
    )
    restarted.reconcile("op1", {"usd": "1", "renders": 1}, "recovered-billing")
    restarted.record_review("op1", {"status": "PASS"})
    reserve(restarted, "op2")


@pytest.mark.parametrize("outcome", ["FAILED", "CANCELED"])
def test_failed_canceled_calls_remain_held_and_chargeable(setup, outcome):
    ledger, authority, *_ = setup
    reserve(ledger)
    ledger.mark_submitted("op1")
    ledger.apply_authority(authority.command("REVOKE_GRANT", "g1", "Stop now", "stop"))
    ledger.record_outcome(
        "op1", outcome, provider_operation_id="known-id", provider_state="partial compute"
    )
    with pytest.raises(SpendDenied):
        ledger.release_unsubmitted("op1", "Pretend free cancellation")
    assert ledger.report("g1")["held"]["usd"] == 2
    ledger.reconcile("op1", {"usd": "1.5", "renders": 1}, "provider charge")
    assert ledger.report("g1")["consumed"]["usd"] == Decimal("1.5")


def test_unexpected_overage_records_truth_then_stops(setup):
    ledger, *_ = setup
    reserve(ledger)
    finish(ledger, actual={"usd": "11", "renders": 1})
    report = ledger.report("g1")
    assert report["consumed"]["usd"] == 11
    assert report["available"]["usd"] == -1
    assert report["stop_reason"]
    with pytest.raises(SpendDenied):
        reserve(ledger, "op2")


def test_nested_paid_evaluator_counts_and_blocks_generation(setup):
    ledger, *_ = setup
    reserve(ledger)
    finish(ledger, review=False)
    reserve(
        ledger,
        "critic",
        parent_operation_id="op1",
        metadata={"kind": "EVALUATION"},
        maximum={"usd": ".5", "renders": 0},
    )
    finish(ledger, "critic", actual={"usd": ".5", "renders": 0})
    assert ledger.report("g1")["consumed"]["usd"] == Decimal("2.5")
    with pytest.raises(SpendDenied):
        reserve(ledger, "op2")
    ledger.record_review("op1", {"status": "PASS", "evaluator_operation": "critic"})
    reserve(ledger, "op2")


def test_review_and_policy_metadata_are_immutable_and_callback_atomic(setup):
    ledger, *_ = setup
    reserve(ledger)
    finish(ledger)
    with pytest.raises(LedgerError):
        ledger.record_review("op1", {"status": "REJECT"})

    def deny(history):
        assert history[0]["metadata"]["contract"]["version"] == 1
        raise SpendDenied("Creative objective already answered")

    with pytest.raises(SpendDenied):
        reserve(ledger, "op2", validate_history=deny)
    assert len(ledger.operations("job")) == 1
    ledger.stop("job", "Enough evidence", goal_satisfied=True)
    assert ledger.report("g1")["unspent_authorization"]["renders"] == 19
    assert ledger.events()[-1]["type"] == "GOAL_SATISFIED"


def test_append_only_and_tamper_detected(setup):
    ledger, authority, _, now, key = setup
    reserve(ledger)
    with sqlite3.connect(ledger.database) as conn:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("DELETE FROM economic_events")
        conn.execute("DROP TRIGGER no_event_update")
        conn.execute(
            "UPDATE economic_events SET payload=? WHERE sequence=2", (json.dumps({"fake": True}),)
        )
    with pytest.raises(LedgerError, match="integrity"):
        SpendLedger(ledger.database, authority.public_key, key, clock=lambda: now)


def test_tail_truncation_and_external_rollback_checkpoint(setup):
    ledger, authority, _, now, key = setup
    reserve(ledger)
    checkpoint = ledger.checkpoint()
    with sqlite3.connect(ledger.database) as conn:
        conn.execute("DROP TRIGGER no_event_delete")
        conn.execute("DELETE FROM economic_events WHERE sequence=2")
    with pytest.raises(LedgerError, match="head mismatch"):
        ledger.report("g1")
    with sqlite3.connect(ledger.database) as conn:
        row = conn.execute(
            "SELECT sequence,event_hash FROM economic_events ORDER BY sequence DESC LIMIT 1"
        ).fetchone()
        conn.execute("UPDATE ledger_head SET sequence=?,hash=? WHERE id=1", row)
    with pytest.raises(LedgerError, match="rollback"):
        SpendLedger(
            ledger.database,
            authority.public_key,
            key,
            clock=lambda: now,
            minimum_checkpoint=checkpoint,
        )


def test_explicit_signed_override_needs_new_grant_and_preserves_stop(setup):
    ledger, authority, grant, *_ = setup
    reserve(ledger)
    finish(ledger)
    ledger.stop("job", "Direction failed twice")
    with pytest.raises(SpendDenied):
        ledger.apply_authority(
            authority.command("OVERRIDE_STOP", "job", "Continue", "bad", new_grant_id="g1")
        )
    ledger.install_grant(authority.issue(replace(grant, grant_id="explicit-override")))
    with pytest.raises(SpendDenied):
        reserve(ledger, "op2", grant_id="explicit-override")
    ledger.apply_authority(
        authority.command(
            "OVERRIDE_STOP",
            "job",
            "Owner deliberately authorizes bounded continuation",
            "override1",
            new_grant_id="explicit-override",
        )
    )
    assert ledger.report("g1")["stop_reason"] == "Direction failed twice"
    with pytest.raises(SpendDenied):
        reserve(ledger, "op2", grant_id="g1")
    reserve(ledger, "op2", grant_id="explicit-override")
    ledger.mark_submitted("op2")
    ledger.stop("job", "Uncertain provider state")
    ledger.install_grant(authority.issue(replace(grant, grant_id="another-override")))
    ledger.apply_authority(
        authority.command(
            "OVERRIDE_STOP", "job", "Explicit", "override2", new_grant_id="another-override"
        )
    )
    with pytest.raises(SpendDenied, match="recovery"):
        reserve(ledger, "op3", grant_id="another-override")
    ledger.apply_authority(authority.command("CLOSE_JOB", "job", "Closed", "close"))
    ledger.install_grant(authority.issue(replace(grant, grant_id="after-close")))
    with pytest.raises(SpendDenied):
        ledger.apply_authority(
            authority.command(
                "OVERRIDE_STOP", "job", "Cannot reopen", "override3", new_grant_id="after-close"
            )
        )


def test_provider_identity_cannot_change_during_recovery(setup):
    ledger, *_ = setup
    reserve(ledger)
    with pytest.raises(LedgerError, match="nonempty"):
        ledger.mark_submitted("op1", provider_operation_id="")
    ledger.mark_submitted("op1")
    ledger.record_outcome("op1", "PROVIDER_RUNNING", provider_operation_id="provider-original")
    with pytest.raises(LedgerError, match="identity is immutable"):
        ledger.record_outcome("op1", "COMPLETED", provider_operation_id="provider-other")
    ledger.record_outcome("op1", "RECONCILIATION_REQUIRED")
    assert ledger.operation("op1")["provider_operation_id"] == "provider-original"
    ledger.record_outcome("op1", "COMPLETED", provider_operation_id="provider-original")
    ledger.reconcile("op1", {"usd": "2", "renders": 1}, "original-provider-invoice")


def test_review_and_stop_are_one_atomic_transaction(setup, monkeypatch):
    ledger, *_ = setup
    reserve(ledger)
    finish(ledger, review=False)
    before = ledger.checkpoint()
    append = ledger._append

    def interrupt_stop(connection, state, event, payload):
        if event == "PAID_STOP":
            raise RuntimeError("Synthetic process failure before stop write")
        return append(connection, state, event, payload)

    monkeypatch.setattr(ledger, "_append", interrupt_stop)
    with pytest.raises(RuntimeError, match="Synthetic"):
        ledger.record_review("op1", {"status": "REJECT"}, stop_reason="Wrong artifact")
    assert ledger.operation("op1")["review"] is None
    assert ledger.checkpoint() == before
    with pytest.raises(SpendDenied, match="review required"):
        reserve(ledger, "op2", direction="B")
    monkeypatch.setattr(ledger, "_append", append)
    ledger.record_review("op1", {"status": "REJECT"}, stop_reason="Wrong artifact")
    assert ledger.operation("op1")["review"]["status"] == "REJECT"
    assert ledger.report("g1")["stop_reason"] == "Wrong artifact"
    with pytest.raises(SpendDenied, match="PAID_STOP"):
        reserve(ledger, "op2", direction="B")
    checkpoint = ledger.checkpoint()
    ledger.record_review("op1", {"status": "REJECT"}, stop_reason="Wrong artifact")
    assert ledger.checkpoint() == checkpoint


def test_identical_review_replay_can_add_missing_stop(setup):
    ledger, *_ = setup
    reserve(ledger)
    finish(ledger, review=False)
    review = {"status": "PASS", "reviewer": "Synthetic"}
    ledger.record_review("op1", review)
    ledger.record_review("op1", review, stop_reason="Goal answered", goal_satisfied=True)
    assert ledger.events()[-1]["type"] == "GOAL_SATISFIED"
    assert ledger.report("g1")["stop_reason"] == "Goal answered"
    with pytest.raises(SpendDenied):
        reserve(ledger, "op2")
