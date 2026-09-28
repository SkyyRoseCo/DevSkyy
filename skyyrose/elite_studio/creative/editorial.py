"""Bounded local editorial route for the existing Creative Operations Hub.

Brand adapters resolve facts; this coordinator only consumes execution contracts.
No provider, upload, publication or market-experiment execution exists here.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .local_composite import (
    AssetRef,
    CompositeRequest,
    LocalCompositeGrant,
    Placement,
    compose,
    verify_composite,
)


class ExperimentPlan(BaseModel):
    """Planning only for market/experience/execution classes; no traffic action."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    experiment_class: Literal["creative_direction", "experience", "execution", "market"]
    hypothesis: str = Field(min_length=1)
    assignment_exposure: str | None = None
    primary_metric: str | None = None
    guardrails: str | None = None
    measurement_validity: str | None = None
    sample_horizon: str | None = None
    stopping_rule: str | None = None
    budget: str | None = None
    approval_reference: str | None = None

    @model_validator(mode="after")
    def market_plan_complete(self):
        if self.experiment_class == "market":
            for field in (
                "assignment_exposure",
                "primary_metric",
                "guardrails",
                "measurement_validity",
                "sample_horizon",
                "stopping_rule",
                "budget",
                "approval_reference",
            ):
                if not (getattr(self, field) or "").strip():
                    raise ValueError(f"Market planning requires {field}; no experiment launched")
        return self


def identity(value: dict) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


@dataclass(frozen=True)
class ResolvedEditorial:
    execution: dict
    audit: dict
    source: AssetRef


class BrandAdapter(Protocol):
    def resolve(self) -> ResolvedEditorial: ...


@dataclass(frozen=True)
class Direction:
    key: str
    hypothesis: str
    authored_connection: str
    environment: str
    composition: str
    product_role: str
    emotional_effect: str
    novelty: str
    risk: str
    background: AssetRef
    mask: AssetRef
    placement: Placement

    def __post_init__(self):
        if not self.key.isalnum() or not all(
            getattr(self, field).strip()
            for field in (
                "hypothesis",
                "authored_connection",
                "environment",
                "composition",
                "product_role",
                "emotional_effect",
                "novelty",
                "risk",
            )
        ):
            raise ValueError(
                "Direction requires an alphanumeric key and complete creative rationale"
            )


def _persist(path: Path, value: dict) -> None:
    data = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if path.exists():
        if path.read_text() != data:
            raise ValueError(f"Existing evidence differs: {path.name}; use a new run directory")
        return
    with path.open("x") as stream:
        stream.write(data)


def run_editorial(
    adapter: BrandAdapter,
    directions: list[Direction],
    *,
    root: Path,
    output_dir: Path,
    grant: LocalCompositeGrant,
) -> dict:
    """Resolve afresh, persist linked evidence, produce immutable local candidates.

    Grant is supplied by trusted invocation code, never parsed from a creative brief.
    The caller chooses a new run directory for changed sources/rules/directions.
    """
    resolved = adapter.resolve()
    execution = resolved.execution
    if resolved.audit.get("execution_digest") != identity(execution):
        raise ValueError("Compact/audit contract mismatch")
    job = execution["job"]
    if job["status"] == "BLOCKED":
        raise ValueError("Blocked resolved job")
    intent = execution["intent"]
    if (
        intent["medium"],
        intent["production_type"],
        execution["production_method"]["technique"],
    ) != ("image", "editorial_still", "SOURCE_COMPOSITE"):
        raise NotImplementedError(
            "Execution capability: image/editorial_still/SOURCE_COMPOSITE only"
        )
    if not execution["brand"].get("rules"):
        raise ValueError("Compact contract lacks operative rules")
    if not directions or len(directions) > 3 or len({d.key for d in directions}) != len(directions):
        raise ValueError("One to three uniquely identified directions required")
    if len({d.hypothesis for d in directions}) != len(directions):
        raise ValueError("Directions need distinct hypotheses")
    root = root.resolve()
    output_dir = output_dir.resolve()
    if not output_dir.is_relative_to(root):
        raise ValueError("Output directory escapes artifact root")
    # Validate the separately supplied grant before writing any production artifacts.
    if not isinstance(grant, LocalCompositeGrant):
        raise PermissionError("Trusted local creation grant required")
    if (
        grant.job_id != job["id"]
        or grant.source_sha256 != resolved.source.sha256
        or grant.action != "local_composite"
        or not grant.approval_reference.strip()
    ):
        raise PermissionError("Missing or mismatched local creation grant")
    if not output_dir.is_relative_to((root / grant.output_root).resolve()):
        raise PermissionError("Output outside granted destination")
    output_dir.mkdir(parents=True, exist_ok=True)
    # Bind both complete records, not a digest without a retrievable payload.
    linkage = {"execution_sha256": identity(execution), "audit_sha256": identity(resolved.audit)}
    _persist(output_dir / "execution.json", execution)
    _persist(output_dir / "audit.json", resolved.audit)
    _persist(output_dir / "context-link.json", linkage)
    records = []
    for direction in directions:
        request = CompositeRequest(
            job_id=job["id"],
            source=resolved.source,
            mask=direction.mask,
            background=direction.background,
            placement=direction.placement,
            output_path=str((output_dir / f"{direction.key}.png").relative_to(root)),
        )
        # Failures propagate; a failed render never becomes a successful manifest row.
        budget_key = identity(
            {
                "job_id": grant.job_id,
                "source": grant.source_sha256,
                "approval": grant.approval_reference,
            }
        )
        budget_root = root / ".artifacts" / "creative-os-authority"
        budget_root.mkdir(parents=True, exist_ok=True)
        budget_path = budget_root / f"{budget_key}.json"
        lock_path = budget_path.with_suffix(".lock")
        with lock_path.open("a+") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            budget = (
                json.loads(budget_path.read_text())
                if budget_path.exists()
                else {"job_id": job["id"], "maximum": 9, "per_direction": 3, "attempts": []}
            )
            if budget["job_id"] != job["id"]:
                raise ValueError("Budget belongs to a different job")
            existing = (root / request.output_path).exists()
            if not existing:
                if (
                    len(budget["attempts"]) >= 9
                    or sum(a["direction"] == direction.key for a in budget["attempts"]) >= 3
                ):
                    raise PermissionError("Local pilot render budget exhausted")
                budget["attempts"].append(
                    {"direction": direction.key, "output": request.output_path}
                )
                temporary = budget_path.with_suffix(".tmp")
                temporary.write_text(json.dumps(budget, indent=2) + "\n")
                temporary.replace(budget_path)
            receipt = compose(request, root=root, grant=grant)
        verification = verify_composite(request, receipt, root=root)
        _persist(output_dir / f"{direction.key}-verification.json", verification)
        records.append(
            {
                "direction": direction.key,
                "hypothesis": direction.hypothesis,
                "authored_connection": direction.authored_connection,
                "environment": direction.environment,
                "composition": direction.composition,
                "product_role": direction.product_role,
                "emotional_effect": direction.emotional_effect,
                "novelty": direction.novelty,
                "risk": direction.risk,
                "receipt": receipt,
                "technical_verification": verification,
                "visual_review": "NOT RUN",
                "creative_assessment": "REVISE",
            }
        )
    result = {
        "version": "1.0",
        "context": linkage,
        "job_id": job["id"],
        "experiment_class": "creative_direction",
        "market_results": None,
        "candidates": records,
        "pilot": "incomplete_pending_visual_review",
        "capabilities": {
            "editorial_still_source_composite": "IMPLEMENTED",
            "film": "PLANNING_ONLY",
            "3d": "PLANNING_ONLY",
            "interactive": "PLANNING_ONLY",
        },
        "authority": {
            "local_composite": grant.approval_reference,
            "provider_generation": False,
            "source_upload": False,
            "spend": False,
            "publication": False,
            "deployment": False,
            "messaging": False,
            "ad_spend": False,
        },
    }
    _persist(output_dir / "production.json", result)
    return result


def verify_context_link(directory: Path) -> bool:
    """Fail on absent or modified compact/audit records."""
    link = json.loads((directory / "context-link.json").read_text())
    for name in ("execution", "audit"):
        if identity(json.loads((directory / f"{name}.json").read_text())) != link[f"{name}_sha256"]:
            raise ValueError(f"Changed {name} record")
    return True


def assess_editorial_review(
    directory: Path,
    reviews: dict,
    *,
    root: Path,
    adapter: BrandAdapter,
    producer_implementation: AssetRef | None = None,
) -> dict:
    """Combine fresh objective checks with explicitly attributed visual judgments.

    Review records are caller-supplied evidence, not authenticated human approvals.
    This local function cannot approve publication or change the Constitution.
    """
    verify_context_link(directory)
    production = json.loads((directory / "production.json").read_text())
    execution = json.loads((directory / "execution.json").read_text())
    current = adapter.resolve().execution
    prior_contract = execution.get("job", {}).get("contract_id")
    current_contract = current.get("job", {}).get("contract_id")
    if prior_contract or current_contract:
        if not prior_contract or prior_contract != current_contract:
            raise ValueError("Current authority differs; previous evidence is stale")
    elif identity(current) != identity(execution):
        raise ValueError("Current authority differs; previous evidence is stale")

    link = json.loads((directory / "context-link.json").read_text())
    if production.get("context") != link or production.get("job_id") != execution["job"]["id"]:
        raise ValueError("Production/context linkage mismatch")
    candidates = production["candidates"]
    if not candidates or len(candidates) > 3:
        raise ValueError("Invalid candidate count")
    for values in (
        [c["direction"] for c in candidates],
        [c["receipt"]["output_path"] for c in candidates],
        [c["receipt"]["output_sha256"] for c in candidates],
    ):
        if len(set(values)) != len(candidates):
            raise ValueError("Duplicate candidate direction, output or artifact")
    bound_sources = [p.get("selected_source", {}) for p in execution.get("products", [])]

    required = {
        "source_view",
        "silhouette",
        "trim",
        "artwork_placement",
        "proportions_construction",
        "color_material",
        "occlusion",
        "canvas_clipping",
        "boundary",
    }
    results = []
    for candidate in production["candidates"]:
        key = candidate["direction"]
        receipt = candidate["receipt"]
        r = receipt["request"]
        if (
            receipt.get("job_id") != execution["job"]["id"]
            or r.get("job_id") != execution["job"]["id"]
            or not any(
                source.get("path") == r["source"]["path"]
                and source.get("sha256") == r["source"]["sha256"]
                for source in bound_sources
            )
        ):
            raise ValueError("Receipt job/source differs from resolved contract")
        request = CompositeRequest(
            r["job_id"],
            AssetRef(**r["source"]),
            AssetRef(**r["mask"]),
            AssetRef(**r["background"]),
            Placement(**r["placement"]),
            r["output_path"],
        )
        technical = verify_composite(
            request, receipt, root=root, producer_implementation=producer_implementation
        )
        visual = reviews.get(key, {})
        criteria = visual.get("criteria", {})
        visual_pass = (
            visual.get("artifact_sha256") == technical.get("output_sha256")
            and bool(visual.get("reviewer"))
            and bool(visual.get("method"))
            and required <= criteria.keys()
            and all(
                criteria[k].get("result") == "PASS" and criteria[k].get("evidence")
                for k in required
            )
        )
        visual_pass = visual_pass and all(
            (
                item.get("result") == "PASS" and bool(item.get("evidence"))
                if item.get("applicable", True)
                else bool(item.get("reason"))
            )
            for item in criteria.values()
        )
        creative = visual.get("creative_assessment", "REVISE")
        if creative not in ("RECOMMENDED", "REVISE", "REJECT"):
            raise ValueError("Creative judgment cannot manufacture owner approval")
        results.append(
            {
                "direction": key,
                "technical": technical,
                "visible_fidelity": "PASS" if visual_pass else "BLOCKED",
                "visual_evidence": visual,
                "creative_assessment": creative,
            }
        )
    passed = all(
        r["technical"]["status"] == "PASS" and r["visible_fidelity"] == "PASS" for r in results
    )
    return {
        "job_id": production["job_id"],
        "results": results,
        "pilot": "produced_and_checked" if passed and len(results) == 3 else "incomplete",
        "creative_direction": (
            "revision_required"
            if any(r["creative_assessment"] != "RECOMMENDED" for r in results)
            else "recommended"
        ),
        "market_results": None,
        "owner_approved": False,
        "publication_authorized": False,
        "spend_authorized": False,
    }
