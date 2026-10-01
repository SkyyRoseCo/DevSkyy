from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from skyyrose.elite_studio.creative.runway_quota import (
    RUNWAY_MODEL,
    RUNWAY_PROVIDER,
    RUNWAY_PURPOSE,
    RUNWAY_QUOTA_UNIT,
    RouterSnapshot,
    RunwayDevDryRunGovernor,
    RunwayDryRunCommand,
    RunwayDryRunFailed,
    RunwayQuotaDenied,
    TransportResponse,
    build_job_id_for_grant,
    canonical_json,
    sha256_hex,
    validate_dry_run_response,
)
from skyyrose.elite_studio.creative.spend_ledger import SpendAuthority, SpendGrant, SpendLedger

NOW = datetime(2026, 9, 26, 14, 0, tzinfo=UTC)
PRINCIPAL_REF = "a" * 64


@pytest.fixture(autouse=True)
def deny_network(monkeypatch):
    """Every case is offline, including the historical provider-shaped fixtures."""
    import socket

    def denied(*args, **kwargs):
        raise AssertionError("Network is forbidden in quota verification")

    monkeypatch.setattr(socket.socket, "connect", denied)
    monkeypatch.setattr(socket, "getaddrinfo", denied)


@pytest.mark.asyncio
async def test_live_execution_is_denied_before_reservation_or_transport(tmp_path):
    governor, ledger, transport, _snapshot = make_governor(tmp_path)
    before = ledger.checkpoint()
    with pytest.raises(RunwayQuotaDenied, match="IMMUTABLE_ROUTER_BINDING_UNQUALIFIED"):
        await governor.execute({"operation_id": str(uuid4()), "principal_ref": PRINCIPAL_REF})
    assert transport.calls == 0
    assert ledger.checkpoint() == before


@pytest.mark.asyncio
async def test_http_transport_cannot_send_even_with_a_credential():
    from skyyrose.elite_studio.creative.runway_quota import RunwayHttpDryRunTransport

    transport = RunwayHttpDryRunTransport("synthetic-secret")
    assert "synthetic-secret" not in repr(vars(transport))
    with pytest.raises(RunwayQuotaDenied, match="IMMUTABLE_ROUTER_BINDING_UNQUALIFIED"):
        await transport.post({"configId": "mutable-router", "dryRun": True})


def make_snapshot(*, observed_at: datetime | None = None) -> RouterSnapshot:
    settings = {
        "schemaVersion": 1,
        "optimizeFor": "quality",
        "models": {"mode": "allowlist_only", "ids": [RUNWAY_MODEL]},
        "fallback": {"onCapacity": False},
        "maxCreditsPerGeneration": {"image": 76},
    }
    payload = {
        "projectId": "149ffed4-4b00-44d5-8e69-2536c30db85e",
        "router": {
            "id": "54fdc045-5501-4331-a22b-5b55ad6d349a",
            "slug": "skyyrose-sunburst-dry-run",
            "version": 2,
            "settings": settings,
        },
    }
    return RouterSnapshot(
        project_id=payload["projectId"],
        router_id=payload["router"]["id"],
        slug=payload["router"]["slug"],
        version=2,
        model_id=RUNWAY_MODEL,
        image_ceiling=76,
        optimize_for="quality",
        observed_at=observed_at or NOW - timedelta(minutes=1),
        configuration_digest=sha256_hex(canonical_json(payload)),
        authentication_scope="VERIFIED_LIVE_DEV_MCP_READ_ONLY",
    )


def provider_response(**overrides):
    routing = {
        "model": RUNWAY_MODEL,
        "provider": "openai",
        "configId": "skyyrose-sunburst-dry-run",
        "resolvedSettings": {"optimizeFor": "quality", "priceCeiling": 76},
        "resolvedInput": {
            "ratio": "1024:1280",
            "aspectRatio": "4:5",
            "resolution": "2k",
        },
        "estimatedCost": {"credits": 16},
    }
    routing.update(overrides)
    return {"dryRun": True, "routing": routing}


class FixtureTransport:
    def __init__(self, response: TransportResponse | None = None, error: Exception | None = None):
        self.response = response or TransportResponse(
            200, json.dumps(provider_response()).encode("utf-8")
        )
        self.error = error
        self.calls = 0
        self.entered = asyncio.Event()

    async def post(self, _payload):
        self.calls += 1
        self.entered.set()
        if self.error:
            raise self.error
        return self.response


def make_governor(
    tmp_path,
    *,
    transport=None,
    principal_ref=PRINCIPAL_REF,
    grant_job_override=None,
    authority=None,
):
    authority = authority or SpendAuthority(Ed25519PrivateKey.generate())
    ledger = SpendLedger(
        tmp_path / "governor.sqlite",
        authority.public_key,
        b"integrity-key" * 4,
        clock=lambda: NOW,
    )
    snapshot = make_snapshot()
    grant_id = "runway-preflight-once"
    job_id = grant_job_override or build_job_id_for_grant(
        grant_id=grant_id,
        principal_ref=principal_ref,
        snapshot=snapshot,
    )
    grant = SpendGrant(
        grant_id=grant_id,
        job_id=job_id,
        providers=(RUNWAY_PROVIDER,),
        purposes=(RUNWAY_PURPOSE,),
        limits={RUNWAY_QUOTA_UNIT: Decimal("1")},
        max_single_call={RUNWAY_QUOTA_UNIT: Decimal("1")},
        valid_until=(NOW + timedelta(minutes=30)).isoformat(),
    )
    ledger.install_grant(authority.issue(grant))
    transport = transport or FixtureTransport()
    governor = RunwayDevDryRunGovernor(
        ledger,
        grant_id,
        snapshot,
        transport,
        clock=lambda: NOW,
    )
    return governor, ledger, transport, snapshot


@pytest.mark.asyncio
async def test_different_operations_share_one_request_budget(tmp_path):
    governor, _ledger, transport, _snapshot = make_governor(tmp_path)
    results = await asyncio.gather(
        *(
            governor.simulate({"operation_id": str(uuid4()), "principal_ref": PRINCIPAL_REF})
            for _ in range(2)
        ),
        return_exceptions=True,
    )
    assert sum(isinstance(result, dict) for result in results) == 1
    assert sum(isinstance(result, RunwayQuotaDenied) for result in results) == 1
    assert transport.calls == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("control", ["revoke", "stop"])
async def test_owner_stop_or_revocation_before_reservation_denies_simulation(tmp_path, control):
    authority = SpendAuthority(Ed25519PrivateKey.generate())
    governor, ledger, transport, _snapshot = make_governor(tmp_path, authority=authority)
    if control == "revoke":
        ledger.apply_authority(
            authority.command("REVOKE_GRANT", "runway-preflight-once", "Synthetic stop", "stop1")
        )
    else:
        ledger.stop(ledger.report("runway-preflight-once")["grant"]["job_id"], "Synthetic stop")
    with pytest.raises(RunwayQuotaDenied):
        await governor.simulate({"operation_id": str(uuid4()), "principal_ref": PRINCIPAL_REF})
    assert transport.calls == 0


@pytest.mark.asyncio
async def test_expired_grant_denied_with_fresh_snapshot(tmp_path):
    governor, _ledger, transport, _snapshot = make_governor(tmp_path)
    governor._clock = lambda: NOW + timedelta(minutes=31)
    governor._snapshot = make_snapshot(observed_at=NOW + timedelta(minutes=30))
    with pytest.raises(RunwayQuotaDenied, match="expiry"):
        await governor.simulate({"operation_id": str(uuid4()), "principal_ref": PRINCIPAL_REF})
    assert transport.calls == 0


@pytest.mark.asyncio
async def test_restart_retains_consumed_budget_and_checkpoint(tmp_path):
    authority = SpendAuthority(Ed25519PrivateKey.generate())
    governor, ledger, transport, snapshot = make_governor(tmp_path, authority=authority)
    await governor.simulate({"operation_id": str(uuid4()), "principal_ref": PRINCIPAL_REF})
    checkpoint = ledger.checkpoint()
    restored = SpendLedger(
        tmp_path / "governor.sqlite",
        authority.public_key,
        b"integrity-key" * 4,
        clock=lambda: NOW,
        minimum_checkpoint=checkpoint,
    )
    restarted = RunwayDevDryRunGovernor(
        restored, "runway-preflight-once", snapshot, transport, clock=lambda: NOW
    )
    with pytest.raises(RunwayQuotaDenied):
        await restarted.simulate({"operation_id": str(uuid4()), "principal_ref": PRINCIPAL_REF})
    assert transport.calls == 1
    assert restored.checkpoint() == checkpoint


@pytest.mark.asyncio
async def test_readonly_report_marks_durable_fixture_records_simulated(tmp_path):
    from skyyrose.elite_studio.creative.governor_reporting import ReadOnlyLedger

    authority = SpendAuthority(Ed25519PrivateKey.generate())
    governor, ledger, _transport, _snapshot = make_governor(tmp_path, authority=authority)
    await governor.simulate({"operation_id": str(uuid4()), "principal_ref": PRINCIPAL_REF})
    reader = ReadOnlyLedger(
        tmp_path / "governor.sqlite",
        authority.public_key,
        b"integrity-key" * 4,
        minimum_checkpoint=ledger.checkpoint(),
    )
    report = reader.report(
        job_id=ledger.report("runway-preflight-once")["grant"]["job_id"],
        grant_id="runway-preflight-once",
    )
    assert report["evidence_mode"] == "SIMULATED"
    assert report["actual_spend"] is None
    assert report["current_provider_execution"] is None


@pytest.mark.asyncio
async def test_one_request_uses_existing_signed_ledger_and_keeps_credit_estimate_separate(tmp_path):
    governor, ledger, transport, _snapshot = make_governor(tmp_path)
    operation_id = str(uuid4())
    result = await governor.simulate(
        {"operation_id": operation_id, "principal_ref": PRINCIPAL_REF, "aspect_ratio": "4:5"}
    )

    operation = ledger.operation(operation_id)
    assert transport.calls == 1
    assert result["status"] == "OFFLINE_SIMULATION_VERIFIED"
    assert result["decision"]["estimatedCostCredits"] == "16"
    assert result["decision"]["routerCeilingCredits"] == "76"
    assert result["decision"]["generationCreditsReserved"] == "0"
    assert result["decision"]["providerApiRequests"] == 0
    assert result["decision"]["simulatedProviderApiRequests"] == 1
    assert operation["metadata"]["simulated"] is True
    assert operation["metadata"]["provider_api_calls"] == 0
    assert operation["metadata"]["evidence_mode"] == "OFFLINE_SIMULATION_ONLY"
    assert operation["state"] == "COMPLETED"
    assert operation["billing_state"] == "FINALIZED"
    assert operation["actual"] == {RUNWAY_QUOTA_UNIT: "1"}
    assert operation["metadata"]["request_payload"]["input"]["outputCount"] == 1
    assert "referenceImages" not in operation["metadata"]["request_payload"]["input"]
    assert "quality" not in operation["metadata"]["request_payload"]["input"]


@pytest.mark.asyncio
@pytest.mark.parametrize("duplicate", [True, False])
async def test_competitor_denied_while_first_fixture_is_in_flight(tmp_path, duplicate):
    release = asyncio.Event()

    class BlockingTransport(FixtureTransport):
        async def post(self, payload):
            self.calls += 1
            self.entered.set()
            await release.wait()
            return self.response

    transport = BlockingTransport()
    governor, _ledger, _transport, _snapshot = make_governor(tmp_path, transport=transport)
    command = {"operation_id": str(uuid4()), "principal_ref": PRINCIPAL_REF}
    first = asyncio.create_task(governor.simulate(command))
    try:
        await asyncio.wait_for(transport.entered.wait(), 1)
        competing = command if duplicate else {**command, "operation_id": str(uuid4())}
        with pytest.raises(RunwayQuotaDenied):
            await governor.simulate(competing)
        assert not first.done()
        assert transport.calls == 1
    finally:
        release.set()
        await first


@pytest.mark.asyncio
async def test_replay_and_concurrent_duplicate_cannot_submit_twice(tmp_path):
    governor, _ledger, transport, _snapshot = make_governor(tmp_path)
    operation_id = str(uuid4())
    command = {"operation_id": operation_id, "principal_ref": PRINCIPAL_REF, "aspect_ratio": "4:5"}
    results = await asyncio.gather(
        governor.simulate(command), governor.simulate(command), return_exceptions=True
    )

    assert sum(isinstance(value, dict) for value in results) == 1
    assert sum(isinstance(value, RunwayQuotaDenied) for value in results) == 1
    assert transport.calls == 1
    with pytest.raises(RunwayQuotaDenied):
        await governor.simulate(command)
    assert transport.calls == 1


@pytest.mark.asyncio
async def test_signed_grant_is_bound_to_principal_and_router_snapshot(tmp_path):
    other_principal = "b" * 64
    governor, _ledger, transport, _snapshot = make_governor(
        tmp_path,
        grant_job_override=build_job_id_for_grant(
            grant_id="runway-preflight-once",
            principal_ref=other_principal,
            snapshot=make_snapshot(),
        ),
    )
    with pytest.raises(RunwayQuotaDenied, match="different principal or router"):
        await governor.simulate(
            {"operation_id": str(uuid4()), "principal_ref": PRINCIPAL_REF, "aspect_ratio": "4:5"}
        )
    assert transport.calls == 0


@pytest.mark.asyncio
async def test_transport_uncertainty_stays_held_and_never_retries(tmp_path):
    governor, ledger, transport, _snapshot = make_governor(
        tmp_path, transport=FixtureTransport(error=TimeoutError("fixture timeout"))
    )
    operation_id = str(uuid4())
    command = {"operation_id": operation_id, "principal_ref": PRINCIPAL_REF, "aspect_ratio": "4:5"}
    with pytest.raises(RunwayDryRunFailed, match="RUNWAY_REQUEST_OUTCOME_UNKNOWN"):
        await governor.simulate(command)

    operation = ledger.operation(operation_id)
    assert transport.calls == 1
    assert operation["state"] == "RECONCILIATION_REQUIRED"
    assert operation["billing_state"] == "PENDING_ACTUAL"
    assert ledger.report("runway-preflight-once")["held"][RUNWAY_QUOTA_UNIT] == Decimal("1")
    with pytest.raises(RunwayQuotaDenied):
        await governor.simulate(command)
    assert transport.calls == 1


def test_provider_response_rejects_task_artifacts_wrong_router_and_bad_cost():
    snapshot = make_snapshot()
    with pytest.raises(RunwayDryRunFailed, match="INVALID_PROVIDER_RESPONSE"):
        validate_dry_run_response(
            {**provider_response(), "task": {"id": "unexpected"}},
            snapshot=snapshot,
            aspect_ratio="4:5",
        )
    with pytest.raises(RunwayDryRunFailed, match="ROUTER_IDENTITY_MISMATCH"):
        validate_dry_run_response(
            provider_response(configId="other-router"),
            snapshot=snapshot,
            aspect_ratio="4:5",
        )
    with pytest.raises(RunwayDryRunFailed, match="INVALID_PROVIDER_RESPONSE"):
        validate_dry_run_response(
            provider_response(estimatedCost={"credits": float("nan")}),
            snapshot=snapshot,
            aspect_ratio="4:5",
        )


@pytest.mark.asyncio
async def test_stale_router_snapshot_blocks_before_provider_request(tmp_path):
    governor, _ledger, transport, _snapshot = make_governor(tmp_path)
    governor._snapshot = make_snapshot(observed_at=NOW - timedelta(minutes=16))
    with pytest.raises(RunwayQuotaDenied, match="stale"):
        await governor.simulate(
            {"operation_id": str(uuid4()), "principal_ref": PRINCIPAL_REF, "aspect_ratio": "4:5"}
        )
    assert transport.calls == 0


def test_internal_command_rejects_overrides_and_noncanonical_uuid():
    with pytest.raises(Exception):
        RunwayDryRunCommand.model_validate(
            {
                "operation_id": "57A956EA-0A20-4F57-8E69-8EFC6C2D4040",
                "principal_ref": PRINCIPAL_REF,
                "aspect_ratio": "4:5",
            }
        )
    with pytest.raises(Exception):
        RunwayDryRunCommand.model_validate(
            {
                "operation_id": str(uuid4()),
                "principal_ref": PRINCIPAL_REF,
                "aspect_ratio": "4:5",
                "prompt": "caller override",
            }
        )
