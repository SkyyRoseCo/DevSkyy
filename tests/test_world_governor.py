"""Real local SQLite, synthetic signed grants, bounded files, and no networking."""

from datetime import UTC, datetime, timedelta
from hashlib import sha256

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from pydantic import ValidationError

from skyyrose.elite_studio.creative.governor_reporting import ReadOnlyLedger
from skyyrose.elite_studio.creative.spend_ledger import (
    SpendAuthority,
    SpendDenied,
    SpendGrant,
    SpendLedger,
)
from skyyrose.elite_studio.creative.world_governor import (
    MAX_EVIDENCE_BYTES,
    LocalEvidence,
    OfflineWorldGovernor,
    WorldContext,
    WorldFixtureRequest,
    WorldGovernorDenied,
)

NOW = datetime(2026, 10, 1, tzinfo=UTC)
INTEGRITY = b"world-fixture-integrity-key" * 2


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    import socket

    def denied(*args, **kwargs):
        raise AssertionError("World Governor tests must not use network")

    monkeypatch.setattr(socket.socket, "connect", denied)
    monkeypatch.setattr(socket, "getaddrinfo", denied)


@pytest.fixture
def harness(tmp_path):
    (tmp_path / "source.json").write_bytes(b'{"fixture":"synthetic-context"}')
    (tmp_path / "receipt.json").write_bytes(b'{"fixture":"synthetic-result"}')

    def evidence(name):
        return LocalEvidence(path=name, sha256=sha256((tmp_path / name).read_bytes()).hexdigest())

    context = WorldContext(
        job_id="synthetic-world-job",
        brand="synthetic-brand",
        world_id="synthetic-world",
        asset_id="synthetic-hero",
        hero_probe_asset_id="synthetic-hero",
        source=evidence("source.json"),
    )
    authority = SpendAuthority(Ed25519PrivateKey.generate())
    ledger = SpendLedger(
        tmp_path / "world.sqlite", authority.public_key, INTEGRITY, clock=lambda: NOW
    )
    ledger.install_grant(
        authority.issue(
            SpendGrant(
                grant_id="fixture-grant",
                job_id=context.job_id,
                providers=("offline_fixture",),
                purposes=("world_asset_fixture",),
                limits={"provider_api_requests": 1},
                max_single_call={"provider_api_requests": 1},
                valid_until=(NOW + timedelta(minutes=10)).isoformat(),
            )
        )
    )
    request = WorldFixtureRequest(
        operation_id="fixture-operation",
        grant_id="fixture-grant",
        context=context,
        context_digest=context.digest(),
        fixture=evidence("receipt.json"),
    )
    checkpoints = []
    governor = OfflineWorldGovernor(
        ledger,
        evidence_root=tmp_path,
        resolve_context=lambda: context,
        ledger_checkpoint=lambda: checkpoints.append(ledger.checkpoint()),
    )
    return governor, ledger, request, authority, checkpoints


@pytest.mark.parametrize("method", ["execute", "lookup", "cancel"])
def test_all_live_methods_deny_before_context_ledger_or_checkpoint(harness, method, monkeypatch):
    governor, ledger, request, _, checkpoints = harness
    before = ledger.checkpoint()
    monkeypatch.setattr(
        governor, "_resolve_context", lambda: pytest.fail("Context resolver reached")
    )
    with pytest.raises(WorldGovernorDenied, match="PROVIDER_EXECUTION_UNQUALIFIED"):
        getattr(governor, method)(request, approved=True, simulation_mode=True)
    assert ledger.checkpoint() == before
    assert checkpoints == []


@pytest.mark.parametrize(
    "field", ["job_id", "brand", "world_id", "asset_id", "hero_probe_asset_id"]
)
def test_destination_scope_changes_deny_before_reservation(harness, monkeypatch, field):
    governor, ledger, request, _, checkpoints = harness
    changed = request.context.model_copy(update={field: "other-scope"})
    monkeypatch.setattr(governor, "_resolve_context", lambda: changed)
    before = ledger.checkpoint()
    with pytest.raises(WorldGovernorDenied, match="WORLD_CONTEXT"):
        governor.simulate(request)
    assert ledger.checkpoint() == before
    assert checkpoints == []


@pytest.mark.parametrize(
    "update",
    [
        {"context_digest": "a" * 64},
        {"stage": "FINAL_PRODUCTION"},
        {"provider": "runway_dev"},
        {"operation_id": "bad/id"},
        {"context_digest": "old-digest"},
    ],
)
def test_stale_or_forged_model_copy_cannot_reserve(harness, update):
    governor, ledger, request, _, checkpoints = harness
    before = ledger.checkpoint()
    with pytest.raises((WorldGovernorDenied, ValidationError, ValueError)):
        governor.simulate(request.model_copy(update=update))
    assert ledger.checkpoint() == before
    assert checkpoints == []


def test_nested_model_copy_cannot_claim_product_generation(harness):
    governor, ledger, request, _, _ = harness
    before = ledger.checkpoint()
    context = request.context.model_copy(update={"representation": "EXACT_PRODUCT"})
    with pytest.raises(ValidationError):
        governor.simulate(request.model_copy(update={"context": context}))
    assert ledger.checkpoint() == before


@pytest.mark.parametrize("mutation", ["changed", "escape", "oversized"])
def test_bounded_evidence_rejects_changed_bytes_symlink_escape_and_size(
    harness, tmp_path, mutation
):
    governor, ledger, request, _, checkpoints = harness
    source = tmp_path / "source.json"
    if mutation == "changed":
        source.write_bytes(b"changed")
    elif mutation == "escape":
        outside = tmp_path.parent / (tmp_path.name + "-outside.json")
        outside.write_bytes(b"outside fixture")
        source.unlink()
        source.symlink_to(outside)
    else:
        source.write_bytes(b"x" * (MAX_EVIDENCE_BYTES + 1))
    before = ledger.checkpoint()
    with pytest.raises(WorldGovernorDenied):
        governor.simulate(request)
    assert ledger.checkpoint() == before
    assert checkpoints == []


@pytest.mark.parametrize("kind", ["missing", "revoked", "expired", "wrong-job", "wrong-provider"])
def test_current_signed_grant_scope_is_required(harness, tmp_path, kind):
    governor, ledger, request, authority, checkpoints = harness
    if kind == "missing":
        request = request.model_copy(update={"grant_id": "absent-grant"})
    elif kind == "revoked":
        ledger.apply_authority(
            authority.command("REVOKE_GRANT", request.grant_id, "fixture", "revoke1")
        )
    elif kind == "expired":
        ledger._clock = lambda: NOW + timedelta(hours=1)
    else:
        ledger.install_grant(
            authority.issue(
                SpendGrant(
                    grant_id="different-grant",
                    job_id="other-job" if kind == "wrong-job" else request.context.job_id,
                    providers=(
                        ("other-provider",) if kind == "wrong-provider" else ("offline_fixture",)
                    ),
                    purposes=("world_asset_fixture",),
                    limits={"provider_api_requests": 1},
                    max_single_call={"provider_api_requests": 1},
                    valid_until=(NOW + timedelta(minutes=10)).isoformat(),
                )
            )
        )
        request = request.model_copy(update={"grant_id": "different-grant"})
    before = ledger.checkpoint()
    with pytest.raises(SpendDenied):
        governor.simulate(request)
    assert ledger.checkpoint() == before
    assert checkpoints == []


def test_fixture_provenance_survives_restart_and_current_readonly_projection(harness, tmp_path):
    governor, ledger, request, authority, checkpoints = harness
    result = governor.simulate(request)
    assert result["provider_api_calls"] == 0
    assert result["simulated_provider_api_requests"] == 1
    checkpoint = ledger.checkpoint()
    restored = SpendLedger(
        tmp_path / "world.sqlite",
        authority.public_key,
        INTEGRITY,
        clock=lambda: NOW,
        minimum_checkpoint=checkpoint,
    )
    restarted = OfflineWorldGovernor(
        restored,
        evidence_root=tmp_path,
        resolve_context=lambda: request.context,
        ledger_checkpoint=lambda: None,
    )
    assert restarted.recover_fixture(request) == result
    assert restored.checkpoint() == checkpoint
    with pytest.raises(SpendDenied):
        restarted.simulate(request)
    report = ReadOnlyLedger(
        tmp_path / "world.sqlite", authority.public_key, INTEGRITY, minimum_checkpoint=checkpoint
    ).report(job_id=request.context.job_id, grant_id=request.grant_id)
    assert report["evidence_mode"] == "SIMULATED"
    assert report["actual_spend"] is None
    assert report["current_provider_execution"] is None
    assert report["stopped"] is True
    operation = restored.operation(request.operation_id)
    assert operation["metadata"]["provider_qualified"] is False
    assert operation["outcome_evidence"]["provider_api_calls"] == 0
    assert len(checkpoints) == 5


@pytest.mark.parametrize("failure_at", [1, 2, 3, 4, 5])
def test_restart_recovers_partial_fixture_steps_without_resubmission(harness, tmp_path, failure_at):
    governor, ledger, request, authority, checkpoints = harness

    def fail_checkpoint():
        checkpoints.append(ledger.checkpoint())
        if len(checkpoints) == failure_at:
            raise RuntimeError("isolated checkpoint fixture interruption")

    governor._checkpoint = fail_checkpoint
    with pytest.raises(RuntimeError, match="checkpoint fixture interruption"):
        governor.simulate(request)
    assert len([e for e in ledger.events() if e["type"] == "BUDGET_RESERVED"]) == 1
    restored = SpendLedger(
        tmp_path / "world.sqlite",
        authority.public_key,
        INTEGRITY,
        clock=lambda: NOW,
        minimum_checkpoint=ledger.checkpoint(),
    )
    restarted = OfflineWorldGovernor(
        restored,
        evidence_root=tmp_path,
        resolve_context=lambda: request.context,
        ledger_checkpoint=lambda: None,
    )
    with pytest.raises(SpendDenied):
        restarted.simulate(request)
    bad = request.model_copy(update={"grant_id": "other-grant"})
    before = restored.checkpoint()
    with pytest.raises(WorldGovernorDenied, match="RECOVERY_IDENTITY"):
        restarted.recover_fixture(bad)
    assert restored.checkpoint() == before
    result = restarted.recover_fixture(request)
    assert result["provider_api_calls"] == 0
    assert len([e for e in restored.events() if e["type"] == "BUDGET_RESERVED"]) == 1
    assert (
        restored.operation(request.operation_id)["provider_operation_id"]
        == "fixture-fixture-operation"
    )


def test_reserved_fixture_recovery_rechecks_revocation(harness):
    governor, ledger, request, authority, _ = harness

    def interrupted():
        raise RuntimeError("fixture checkpoint unavailable")

    governor._checkpoint = interrupted
    with pytest.raises(RuntimeError):
        governor.simulate(request)
    assert ledger.operation(request.operation_id)["state"] == "RESERVED"
    ledger.apply_authority(
        authority.command("REVOKE_GRANT", request.grant_id, "fixture revoke", "revoke-reserved")
    )
    before = ledger.checkpoint()
    with pytest.raises(SpendDenied):
        governor.recover_fixture(request)
    assert ledger.checkpoint() == before
