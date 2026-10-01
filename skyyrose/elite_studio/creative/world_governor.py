"""Offline World OS reconciliation boundary; no provider transport or bootstrap.

Reexpresses the recovered contract/context checks using the current SpendLedger.
The host supplies fresh destination context, not historical approvals or product
facts. Fixture accounting is simulation evidence, never paid execution authority.
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .runway_quota import canonical_json
from .spend_ledger import SpendDenied, SpendLedger, identifier

MAX_EVIDENCE_BYTES = 1_048_576
PROVENANCE = {
    "simulated": True,
    "evidence_mode": "OFFLINE_SIMULATION_ONLY",
    "provider_qualified": False,
    "provider_api_calls": 0,
}


class WorldGovernorDenied(PermissionError):
    """World context, local evidence, or execution authority is unavailable."""


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    def digest(self) -> str:
        return hashlib.sha256(canonical_json(self.model_dump(mode="json"))).hexdigest()


class LocalEvidence(Record):
    path: str = Field(min_length=1, max_length=1024)
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")

    def read(self, root: Path) -> bytes:
        """Bound reads to ordinary files within the trusted local evidence root."""
        path = (root / self.path).resolve(strict=True)
        if not path.is_relative_to(root) or not path.is_file():
            raise WorldGovernorDenied("EVIDENCE_OUTSIDE_ROOT")
        with path.open("rb") as stream:
            data = stream.read(MAX_EVIDENCE_BYTES + 1)
        if len(data) > MAX_EVIDENCE_BYTES:
            raise WorldGovernorDenied("EVIDENCE_TOO_LARGE")
        if hashlib.sha256(data).hexdigest() != self.sha256:
            raise WorldGovernorDenied("EVIDENCE_CHANGED")
        return data


class WorldContext(Record):
    """Destination-resolved non-product fixture scope; contains no garment facts."""

    job_id: str
    brand: str
    world_id: str
    asset_id: str
    hero_probe_asset_id: str
    status: Literal["READY"] = "READY"
    representation: Literal["BRAND_ABSTRACT"] = "BRAND_ABSTRACT"
    method: Literal["GENERATED_ENVIRONMENT"] = "GENERATED_ENVIRONMENT"
    source: LocalEvidence

    @field_validator("job_id", "brand", "world_id", "asset_id", "hero_probe_asset_id")
    @classmethod
    def bounded_identity(cls, value: str) -> str:
        return identifier(value)


class WorldFixtureRequest(Record):
    # Leave room for the stable fixture- task prefix within ledger's 128 limit.
    operation_id: str = Field(max_length=120)
    grant_id: str
    context: WorldContext
    context_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    artifact_type: Literal["WORLD_ASSET"] = "WORLD_ASSET"
    stage: Literal["PAID_PROBE"] = "PAID_PROBE"
    purpose: Literal["world_asset_fixture"] = "world_asset_fixture"
    provider: Literal["offline_fixture"] = "offline_fixture"
    fixture: LocalEvidence

    @field_validator("operation_id", "grant_id")
    @classmethod
    def bounded_identity(cls, value: str) -> str:
        return identifier(value)


class OfflineWorldGovernor:
    """One local fixture per immutable request, with restart-safe recovery.

    No callable provider object is accepted. All public live methods deny before
    inspecting inputs, resolving context, reserving, or checkpointing. This is a
    trusted host boundary, not a sandbox against arbitrary local Python code.
    """

    def __init__(
        self,
        ledger: SpendLedger,
        *,
        evidence_root: Path,
        resolve_context: Callable[[], WorldContext],
        ledger_checkpoint: Callable[[], None],
    ):
        self._ledger = ledger
        self._root = evidence_root.resolve(strict=True)
        self._resolve_context = resolve_context
        self._checkpoint = ledger_checkpoint

    def execute(self, *_args: object, **_kwargs: object) -> dict:
        raise WorldGovernorDenied("PROVIDER_EXECUTION_UNQUALIFIED")

    def lookup(self, *_args: object, **_kwargs: object) -> dict:
        raise WorldGovernorDenied("PROVIDER_EXECUTION_UNQUALIFIED")

    def cancel(self, *_args: object, **_kwargs: object) -> dict:
        raise WorldGovernorDenied("PROVIDER_EXECUTION_UNQUALIFIED")

    def _validate(self, request: WorldFixtureRequest) -> WorldFixtureRequest:
        # model_copy and nested models can bypass validators: reconstruct both.
        request = WorldFixtureRequest.model_validate(request.model_dump(mode="python"))
        resolved = self._resolve_context()
        current = WorldContext.model_validate(resolved.model_dump(mode="python"))
        current.source.read(self._root)
        request.context.source.read(self._root)
        request.fixture.read(self._root)
        if (
            request.context != current
            or request.context_digest != current.digest()
            or current.asset_id != current.hero_probe_asset_id
        ):
            raise WorldGovernorDenied("WORLD_CONTEXT_CHANGED_OR_SCOPE_MISMATCH")
        return request

    def simulate(self, request: WorldFixtureRequest) -> dict:
        request = self._validate(request)
        if any(
            op["operation_id"] == request.operation_id
            for op in self._ledger.operations(request.context.job_id)
        ):
            raise SpendDenied("Fixture operation exists; recover without resubmission")
        self._ledger.reserve(
            request.operation_id,
            grant_id=request.grant_id,
            job_id=request.context.job_id,
            provider=request.provider,
            purpose=request.purpose,
            direction=request.context.world_id,
            stage=request.stage,
            maximum={"provider_api_requests": 1},
            reason="Offline World OS boundary fixture",
            contract_digest=request.digest(),
            metadata={**PROVENANCE, "request": request.model_dump(mode="json")},
        )
        self._checkpoint()
        self._ledger.mark_submitted(request.operation_id, "fixture-" + request.operation_id)
        # A checkpoint failure leaves the immutable submitted identity held. The
        # separate recovery path reads that identity; it never resubmits a task.
        self._checkpoint()
        return self._finish(request)

    def recover_fixture(self, request: WorldFixtureRequest) -> dict:
        request = self._validate(request)
        operation = self._ledger.operation(request.operation_id)
        expected_task = (
            None if operation["state"] == "RESERVED" else "fixture-" + request.operation_id
        )
        if (
            operation["contract_digest"] != request.digest()
            or operation["metadata"] != {**PROVENANCE, "request": request.model_dump(mode="json")}
            or operation["grant_id"] != request.grant_id
            or operation["job_id"] != request.context.job_id
            or operation["provider_operation_id"] != expected_task
        ):
            raise WorldGovernorDenied("FIXTURE_RECOVERY_IDENTITY_MISMATCH")
        if operation["state"] == "RESERVED":
            # Only a local fixture can advance here. The ledger rechecks current
            # expiry/revocation/stop before assigning the stable fixture identity.
            self._ledger.mark_submitted(request.operation_id, "fixture-" + request.operation_id)
            self._checkpoint()
        return self._finish(request)

    def _finish(self, request: WorldFixtureRequest) -> dict:
        operation = self._ledger.operation(request.operation_id)
        receipt = "fixture-response-sha256:" + request.fixture.sha256
        if operation["state"] == "SUBMITTED":
            self._ledger.record_outcome(
                request.operation_id,
                "COMPLETED",
                provider_state="LOCAL_FIXTURE_ONLY",
                evidence={**PROVENANCE, "fixture_receipt": receipt},
            )
            self._checkpoint()
            operation = self._ledger.operation(request.operation_id)
        if operation["state"] != "COMPLETED":
            raise WorldGovernorDenied("UNSUPPORTED_FIXTURE_RECOVERY_STATE")
        if operation["billing_state"] != "FINALIZED":
            self._ledger.reconcile(request.operation_id, {"provider_api_requests": 1}, receipt)
            self._checkpoint()
        self._ledger.record_review(
            request.operation_id,
            {**PROVENANCE, "status": "SIMULATED_FIXTURE", "fixture_receipt": receipt},
            stop_reason="OFFLINE_FIXTURE_COMPLETE",
        )
        self._checkpoint()
        return {
            **PROVENANCE,
            "operation_id": request.operation_id,
            "fixture_receipt": receipt,
            "simulated_provider_api_requests": 1,
            "actual_spend": None,
            "current_provider_execution": None,
        }
