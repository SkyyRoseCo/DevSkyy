"""One-request Runway Router preflight through the existing spend ledger.

This adapter accounts for a non-billable provider API request as its own scarce
resource. It does not grant authority: a verified, owner-signed SpendGrant must
already be installed in the shared ledger. The provider key and transport stay
on the trusted Python host. This module is not a process sandbox.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any, Literal, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from .spend_ledger import SpendDenied, SpendLedger

RUNWAY_API_ORIGIN = "https://api.dev.runwayml.com"
RUNWAY_API_VERSION = "2024-11-06"
RUNWAY_IMAGE_ENDPOINT = f"{RUNWAY_API_ORIGIN}/v1/generate/image"
RUNWAY_MODEL = "gpt_image_2_5_sunburst"
RUNWAY_PURPOSE = "router_dry_run"
RUNWAY_PROVIDER = "runway_dev"
RUNWAY_QUOTA_UNIT = "provider_api_requests"
RUNWAY_MAX_IMAGE_CREDITS = Decimal("76")
RUNWAY_DRY_RUN_PROMPT = (
    "A neutral studio still life of one unbranded ceramic vessel on a plain "
    "warm-gray background. No text, logos, or people."
)
MAX_PROVIDER_RESPONSE_BYTES = 64 * 1024
MAX_ROUTER_SNAPSHOT_AGE = timedelta(minutes=15)
MAX_GRANT_LIFETIME = timedelta(hours=1)
_SHA256_RE = re.compile(r"^[a-f0-9]{64}$")


class RunwayQuotaDenied(PermissionError):
    """A preflight lacks current qualification, a scoped grant, or safe state."""


class RunwayDryRunFailed(RuntimeError):
    """The one authorized request returned an invalid or rejected response."""


def canonical_json(value: Any) -> bytes:
    """Canonical local contract bytes: UTF-8, sorted keys, compact, no NaN."""
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_hex(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


class RouterSnapshot(BaseModel):
    """A bounded, point-in-time Developer API router observation."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    project_id: str = Field(pattern=r"^[0-9a-f-]{36}$")
    router_id: str = Field(pattern=r"^[0-9a-f-]{36}$")
    slug: str = Field(pattern=r"^[a-z][a-z0-9_-]{0,63}$")
    version: int = Field(ge=1)
    model_id: Literal["gpt_image_2_5_sunburst"]
    image_ceiling: int = Field(gt=0, le=76)
    optimize_for: Literal["quality"]
    observed_at: datetime
    configuration_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    authentication_scope: Literal["VERIFIED_LIVE_DEV_MCP_READ_ONLY"]

    def canonical_settings(self) -> dict[str, Any]:
        return {
            "schemaVersion": 1,
            "optimizeFor": self.optimize_for,
            "models": {"mode": "allowlist_only", "ids": [self.model_id]},
            "fallback": {"onCapacity": False},
            "maxCreditsPerGeneration": {"image": self.image_ceiling},
        }

    def digest_payload(self) -> dict[str, Any]:
        return {
            "projectId": self.project_id,
            "router": {
                "id": self.router_id,
                "slug": self.slug,
                "version": self.version,
                "settings": self.canonical_settings(),
            },
        }

    def verify(self, *, now: datetime) -> None:
        if self.observed_at.tzinfo is None:
            raise RunwayQuotaDenied("Router snapshot timestamp must include a timezone")
        age = now.astimezone(UTC) - self.observed_at.astimezone(UTC)
        if age < timedelta(0) or age > MAX_ROUTER_SNAPSHOT_AGE:
            raise RunwayQuotaDenied("Router snapshot is stale or from the future")
        expected = sha256_hex(canonical_json(self.digest_payload()))
        if expected != self.configuration_digest:
            raise RunwayQuotaDenied("Router configuration digest mismatch")


class RunwayDryRunCommand(BaseModel):
    """Internal bridge intent; it contains no prompt, URL, file, or model field."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, populate_by_name=True)

    operation_id: UUID = Field(alias="operationId")
    principal_ref: str = Field(alias="principalRef", pattern=r"^[a-f0-9]{64}$")
    aspect_ratio: Literal["4:5"] = Field(default="4:5", alias="aspectRatio")

    @field_validator("operation_id", mode="before")
    @classmethod
    def parse_canonical_operation_id(cls, value: Any) -> UUID:
        if isinstance(value, UUID):
            return value
        if not isinstance(value, str):
            raise ValueError("operation_id must be a canonical UUID")
        try:
            parsed = UUID(value)
        except (ValueError, AttributeError) as exc:
            raise ValueError("operation_id must be a canonical UUID") from exc
        if str(parsed) != value:
            raise ValueError("operation_id must be a canonical lowercase UUID")
        return parsed


@dataclass(frozen=True)
class TransportResponse:
    status_code: int
    body: bytes
    body_too_large: bool = False


class DryRunTransport(Protocol):
    async def post(self, payload: dict[str, Any]) -> TransportResponse: ...


class RunwayHttpDryRunTransport:
    """Disabled until the provider supports immutable router revision binding.

    A snapshot digest does not pin the remote configId. No HTTP client, credential
    storage, or network request is available through this recovered candidate.
    """

    def __init__(self, api_secret: str):
        # Retain the historical constructor shape, but do not retain the secret.
        pass

    async def post(self, payload: dict[str, Any]) -> TransportResponse:
        raise RunwayQuotaDenied("IMMUTABLE_ROUTER_BINDING_UNQUALIFIED")


def _decimal(value: Any) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (Decimal, int)):
        raise RunwayDryRunFailed("INVALID_PROVIDER_RESPONSE")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise RunwayDryRunFailed("INVALID_PROVIDER_RESPONSE") from exc
    if not number.is_finite() or number < 0:
        raise RunwayDryRunFailed("INVALID_PROVIDER_RESPONSE")
    return number


def _parse_json(body: bytes) -> Any:
    def reject_constant(_value: str) -> None:
        raise ValueError("non-finite JSON number")

    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise ValueError("duplicate JSON object key")
            value[key] = item
        return value

    try:
        return json.loads(
            body,
            parse_float=Decimal,
            parse_int=Decimal,
            parse_constant=reject_constant,
            object_pairs_hook=reject_duplicate_keys,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError, TypeError) as exc:
        raise RunwayDryRunFailed("INVALID_PROVIDER_RESPONSE") from exc


def validate_dry_run_response(
    value: Any,
    *,
    snapshot: RouterSnapshot,
    aspect_ratio: str,
) -> dict[str, Any]:
    """Validate the locally tested fixture contract; live conformance is unqualified."""
    if not isinstance(value, dict) or set(value) != {"dryRun", "routing"}:
        raise RunwayDryRunFailed("INVALID_PROVIDER_RESPONSE")
    if value["dryRun"] is not True:
        raise RunwayDryRunFailed("DRY_RUN_NOT_CONFIRMED")
    routing = value["routing"]
    required = {
        "model",
        "provider",
        "configId",
        "resolvedSettings",
        "resolvedInput",
        "estimatedCost",
    }
    if not isinstance(routing, dict) or set(routing) != required:
        raise RunwayDryRunFailed("INVALID_PROVIDER_RESPONSE")
    if routing["model"] != snapshot.model_id or routing["configId"] != snapshot.slug:
        raise RunwayDryRunFailed("ROUTER_IDENTITY_MISMATCH")
    if not isinstance(routing["provider"], str) or not routing["provider"].strip():
        raise RunwayDryRunFailed("INVALID_PROVIDER_RESPONSE")

    settings = routing["resolvedSettings"]
    if not isinstance(settings, dict) or set(settings) != {"optimizeFor", "priceCeiling"}:
        raise RunwayDryRunFailed("INVALID_PROVIDER_RESPONSE")
    if settings["optimizeFor"] != snapshot.optimize_for:
        raise RunwayDryRunFailed("ROUTER_SETTINGS_MISMATCH")
    if settings["priceCeiling"] is None:
        raise RunwayDryRunFailed("PRICE_CEILING_MISSING")
    ceiling = _decimal(settings["priceCeiling"])
    if ceiling != Decimal(snapshot.image_ceiling) or ceiling > RUNWAY_MAX_IMAGE_CREDITS:
        raise RunwayDryRunFailed("PRICE_CEILING_MISMATCH")

    resolved = routing["resolvedInput"]
    if not isinstance(resolved, dict) or set(resolved) != {"ratio", "aspectRatio", "resolution"}:
        raise RunwayDryRunFailed("INVALID_PROVIDER_RESPONSE")
    if (
        not isinstance(resolved["ratio"], str)
        or not resolved["ratio"].strip()
        or resolved["aspectRatio"] != aspect_ratio
        or resolved["resolution"] != "2k"
    ):
        raise RunwayDryRunFailed("RESOLVED_INPUT_MISMATCH")

    estimated = routing["estimatedCost"]
    if not isinstance(estimated, dict) or set(estimated) != {"credits"}:
        raise RunwayDryRunFailed("INVALID_PROVIDER_RESPONSE")
    estimated_credits = _decimal(estimated["credits"])
    if estimated_credits > ceiling:
        raise RunwayDryRunFailed("ESTIMATE_EXCEEDS_CEILING")

    return {
        "model": snapshot.model_id,
        "provider": routing["provider"],
        "configId": snapshot.slug,
        "optimizeFor": snapshot.optimize_for,
        "estimatedCostCredits": str(estimated_credits),
        "routerCeilingCredits": str(ceiling),
        "generationCreditsReserved": "0",
        "providerApiRequests": 1,
        "aspectRatio": aspect_ratio,
        "resolvedRatio": resolved["ratio"],
        "resolution": "2k",
    }


def _job_id(*, grant_id: str, principal_ref: str, project_id: str, router_digest: str) -> str:
    return "runway-dry-run:" + sha256_hex(
        canonical_json(
            {
                "grant_id": grant_id,
                "principal_ref": principal_ref,
                "project_id": project_id,
                "provider": RUNWAY_PROVIDER,
                "purpose": RUNWAY_PURPOSE,
                "resource": RUNWAY_QUOTA_UNIT,
                "router_configuration_digest": router_digest,
            }
        )
    )


class RunwayDevDryRunGovernor:
    """One exact synthetic dry-run authorized by an existing signed grant."""

    def __init__(
        self,
        ledger: SpendLedger,
        grant_id: str,
        snapshot: RouterSnapshot,
        transport: DryRunTransport,
        *,
        clock=lambda: datetime.now(UTC),
        checkpoint: Callable[[], None] | None = None,
    ):
        self._ledger = ledger
        self._grant_id = grant_id
        self._snapshot = snapshot
        self._transport = transport
        self._clock = clock
        self._checkpoint = checkpoint or (lambda: None)
        self._validate_grant()

    def _validate_grant(self) -> dict[str, Any]:
        try:
            grant = self._ledger.report(self._grant_id)["grant"]
        except (KeyError, SpendDenied) as exc:
            raise RunwayQuotaDenied("No installed signed provider-quota grant") from exc
        if (
            grant.get("providers") != [RUNWAY_PROVIDER]
            or grant.get("purposes") != [RUNWAY_PURPOSE]
            or grant.get("limits") != {RUNWAY_QUOTA_UNIT: "1"}
            or grant.get("max_single_call") != {RUNWAY_QUOTA_UNIT: "1"}
            or grant.get("direction_limits") != {}
            or grant.get("stage_limits") != {}
            or grant.get("issued_by") != "owner_authority"
        ):
            raise RunwayQuotaDenied("Grant exceeds the one-request dry-run scope")
        now = self._clock().astimezone(UTC)
        try:
            expires = datetime.fromisoformat(grant["valid_until"].replace("Z", "+00:00"))
        except (KeyError, AttributeError, ValueError) as exc:
            raise RunwayQuotaDenied("Grant expiry is invalid") from exc
        if expires.tzinfo is None or not now < expires.astimezone(UTC) <= now + MAX_GRANT_LIFETIME:
            raise RunwayQuotaDenied("Grant must have a current expiry within one hour")
        return grant

    async def execute(self, command: RunwayDryRunCommand | dict[str, Any]) -> dict[str, Any]:
        """Fail before reservation, checkpoint, or egress; live control is unqualified."""
        raise RunwayQuotaDenied("IMMUTABLE_ROUTER_BINDING_UNQUALIFIED")

    async def simulate(self, command: RunwayDryRunCommand | dict[str, Any]) -> dict[str, Any]:
        """Exercise the contract with an injected offline fixture transport only.

        The caller must isolate this verification harness from network access.
        An injected Python object is not a process sandbox or provider authority.
        """
        try:
            intent = RunwayDryRunCommand.model_validate(command)
        except ValidationError as exc:
            raise RunwayQuotaDenied("Invalid internal dry-run intent") from exc

        now = self._clock().astimezone(UTC)
        self._snapshot.verify(now=now)
        grant = self._validate_grant()
        expected_job = _job_id(
            grant_id=self._grant_id,
            principal_ref=intent.principal_ref,
            project_id=self._snapshot.project_id,
            router_digest=self._snapshot.configuration_digest,
        )
        if grant.get("job_id") != expected_job:
            raise RunwayQuotaDenied("Signed grant is bound to a different principal or router")

        payload = {
            "configId": self._snapshot.slug,
            "dryRun": True,
            "input": {
                "promptText": RUNWAY_DRY_RUN_PROMPT,
                "aspectRatio": intent.aspect_ratio,
                "resolution": "2k",
                "outputCount": 1,
            },
        }
        operation_contract = {
            "operation_id": str(intent.operation_id),
            "principal_ref": intent.principal_ref,
            "project_id": self._snapshot.project_id,
            "router_id": self._snapshot.router_id,
            "router_slug": self._snapshot.slug,
            "router_version_observed": self._snapshot.version,
            "router_configuration_digest": self._snapshot.configuration_digest,
            "purpose": RUNWAY_PURPOSE,
            "quota_resource": RUNWAY_QUOTA_UNIT,
            "quota_units_authorized": "1",
            "generation_credits_reserved": "0",
            "request_payload": payload,
            "simulated": True,
            "evidence_mode": "OFFLINE_SIMULATION_ONLY",
            "provider_qualified": False,
            "provider_api_calls": 0,
        }
        request_digest = sha256_hex(canonical_json(payload))
        contract_digest = sha256_hex(canonical_json(operation_contract))

        try:
            existing = self._ledger.reserve(
                operation_id=str(intent.operation_id),
                grant_id=self._grant_id,
                job_id=expected_job,
                provider=RUNWAY_PROVIDER,
                purpose=RUNWAY_PURPOSE,
                direction=self._snapshot.configuration_digest,
                stage="DRY_RUN_PREFLIGHT",
                maximum={RUNWAY_QUOTA_UNIT: "1"},
                reason="One offline fixture preflight with simulated quota usage",
                contract_digest=contract_digest,
                metadata={
                    "kind": "RUNWAY_ROUTER_DRY_RUN",
                    "principal_ref": intent.principal_ref,
                    "project_id": self._snapshot.project_id,
                    "router_id": self._snapshot.router_id,
                    "router_slug": self._snapshot.slug,
                    "router_version_observed": self._snapshot.version,
                    "router_configuration_digest": self._snapshot.configuration_digest,
                    "request_identity": request_digest,
                    "quota_resource": RUNWAY_QUOTA_UNIT,
                    "quota_units_authorized": "1",
                    "generation_credits_reserved": "0",
                    "request_payload": payload,
                    "simulated": True,
                    "evidence_mode": "OFFLINE_SIMULATION_ONLY",
                    "provider_qualified": False,
                    "provider_api_calls": 0,
                },
            )
            self._checkpoint()
            if existing["state"] != "RESERVED":
                raise RunwayQuotaDenied("This one-use operation was already submitted")
            self._ledger.mark_submitted(str(intent.operation_id))
            self._checkpoint()
        except (SpendDenied, KeyError) as exc:
            raise RunwayQuotaDenied("Provider API quota grant unavailable or already used") from exc

        try:
            response = await self._transport.post(payload)
        except asyncio.CancelledError:
            self._record_unknown(intent, request_digest)
            raise
        except Exception as exc:
            self._record_unknown(intent, request_digest)
            raise RunwayDryRunFailed("RUNWAY_REQUEST_OUTCOME_UNKNOWN") from exc

        response_digest = sha256_hex(response.body)
        evidence_ref = f"fixture-response-sha256:{response_digest}"
        if response.body_too_large:
            self._settle_response(
                intent,
                response_digest,
                provider_state="RESPONSE_TOO_LARGE",
                outcome="FAILED",
            )
            raise RunwayDryRunFailed("PROVIDER_RESPONSE_TOO_LARGE")

        if response.status_code != 200:
            self._settle_response(
                intent,
                response_digest,
                provider_state=f"HTTP_{response.status_code}",
                outcome="FAILED",
            )
            raise RunwayDryRunFailed("RUNWAY_DRY_RUN_REJECTED")

        try:
            provider_value = _parse_json(response.body)
            decision = validate_dry_run_response(
                provider_value,
                snapshot=self._snapshot,
                aspect_ratio=intent.aspect_ratio,
            )
        except RunwayDryRunFailed:
            self._settle_response(
                intent,
                response_digest,
                provider_state="INVALID_DRY_RUN_RESPONSE",
                outcome="FAILED",
            )
            raise

        self._settle_response(
            intent,
            response_digest,
            provider_state="FIXTURE_DRY_RUN_ROUTED",
            outcome="COMPLETED",
        )
        return {
            "status": "OFFLINE_SIMULATION_VERIFIED",
            "provider_api_calls": 0,
            "evidence_mode": "OFFLINE_SIMULATION_ONLY",
            "provider_qualified": False,
            "decision": {
                **decision,
                "providerApiRequests": 0,
                "simulatedProviderApiRequests": 1,
                "operationId": str(intent.operation_id),
                "requestIdentity": request_digest,
                "contractDigest": contract_digest,
                "routerConfigurationDigest": self._snapshot.configuration_digest,
                "routerVersionObserved": self._snapshot.version,
                "quotaUsageEvidence": evidence_ref,
                "providerResponseSha256": response_digest,
            },
        }

    def _record_unknown(self, intent: RunwayDryRunCommand, request_digest: str) -> None:
        self._ledger.record_outcome(
            str(intent.operation_id),
            "RECONCILIATION_REQUIRED",
            provider_state="TRANSPORT_RESULT_UNKNOWN",
            evidence={
                "request_identity": request_digest,
                "quota_usage": "SIMULATED_OUTCOME_UNKNOWN",
                "simulated": True,
                "evidence_mode": "OFFLINE_SIMULATION_ONLY",
                "provider_qualified": False,
                "provider_api_calls": 0,
                "generation_credits_reserved": "0",
            },
        )
        self._checkpoint()

    def _settle_response(
        self,
        intent: RunwayDryRunCommand,
        response_digest: str,
        *,
        provider_state: str,
        outcome: Literal["COMPLETED", "FAILED"],
    ) -> None:
        self._ledger.record_outcome(
            str(intent.operation_id),
            outcome,
            provider_state=provider_state,
            evidence={
                "provider_response_sha256": response_digest,
                "quota_usage": "ONE_FIXTURE_RESPONSE_RECEIVED",
                "simulated": True,
                "evidence_mode": "OFFLINE_SIMULATION_ONLY",
                "provider_qualified": False,
                "provider_api_calls": 0,
                "generation_credits_reserved": "0",
            },
        )
        # The ledger field is historically named billing_reference. Here it is a
        # local receipt for the non-financial API-request unit, never a provider
        # billing receipt or evidence about account-wide rate-limit usage.
        self._ledger.reconcile(
            str(intent.operation_id),
            {RUNWAY_QUOTA_UNIT: "1"},
            f"fixture-response-sha256:{response_digest}",
        )
        self._checkpoint()


def load_router_snapshot(path: str) -> RouterSnapshot:
    """Load a source-controlled runtime snapshot without reading credentials."""
    try:
        with open(path, "rb") as stream:
            raw = stream.read(16 * 1024 + 1)
        if len(raw) > 16 * 1024:
            raise ValueError("router snapshot too large")
        return RouterSnapshot.model_validate_json(raw)
    except (OSError, json.JSONDecodeError, ValidationError, TypeError, ValueError) as exc:
        raise RunwayQuotaDenied("Router qualification snapshot is unavailable") from exc


def build_job_id_for_grant(*, grant_id: str, principal_ref: str, snapshot: RouterSnapshot) -> str:
    """Public helper for owner-side quota grant preparation and reproducible tests."""
    if not _SHA256_RE.fullmatch(principal_ref):
        raise ValueError("principal_ref must be a redacted HMAC-SHA256 reference")
    return _job_id(
        grant_id=grant_id,
        principal_ref=principal_ref,
        project_id=snapshot.project_id,
        router_digest=snapshot.configuration_digest,
    )
