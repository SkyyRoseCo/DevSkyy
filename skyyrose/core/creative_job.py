"""Content-bound creative job contracts and verification records (no release actions)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, model_validator

from skyyrose.core.content_intent import DerivativePlan
from skyyrose.core.context_resolver import (
    Contract,
    ResolutionRequest,
    ResolvedContext,
    SourceReference,
    resolve_context,
)
from skyyrose.core.execution_policy import LOCAL_TERRITORY, LifecycleStatus
from skyyrose.core.paths import REPO_ROOT, THEME_ROOT

Gate = Literal[
    "CONSTITUTION",
    "PRODUCT_FIDELITY",
    "FACTUAL_CLAIMS",
    "RIGHTS_APPROVALS",
    "CHANNEL",
    "CREATIVE_QA",
    "TECHNICAL_QA",
    "ACCESSIBILITY",
    "COMMERCE_INTEGRITY",
]
GATES = (
    "CONSTITUTION",
    "PRODUCT_FIDELITY",
    "FACTUAL_CLAIMS",
    "RIGHTS_APPROVALS",
    "CHANNEL",
    "CREATIVE_QA",
    "TECHNICAL_QA",
    "ACCESSIBILITY",
    "COMMERCE_INTEGRITY",
)
FIDELITY = (
    "silhouette",
    "proportions",
    "construction_cut_geometry",
    "colorway",
    "artwork",
    "logo",
    "placement",
    "material_appearance",
    "front_back",
    "dimensions",
    "trims_stitching_relevant_detail",
)


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def check_reference(ref: SourceReference, root: Path = REPO_ROOT) -> None:
    path = (root / ref.path).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Evidence path escapes source root")
    if hashlib.sha256(path.read_bytes()).hexdigest() != ref.sha256:
        raise ValueError(f"Stale evidence: {ref.path}")


class ProductionMethod(Contract):
    technique: Literal[
        "SOURCE_PHOTOGRAPHY",
        "SOURCE_COMPOSITE",
        "VALIDATED_3D",
        "CONTROLLED_RENDER",
        "PRODUCT_SCAN",
        "VERIFIED_WORKFLOW",
        "ABSTRACT",
        "UNRESOLVED",
    ]
    rationale: str = Field(min_length=1)
    inputs: list[SourceReference]
    # Documented feasibility, not a claim of permission to execute or spend.
    feasibility_evidence: list[SourceReference]


class JobPlan(Contract):
    deliverables: list[str] = Field(min_length=1)
    experience_outcome: str = Field(min_length=1)
    authored_meaning: str = Field(min_length=1)
    production_method: ProductionMethod
    success_evidence: list[str] = Field(min_length=1)
    channel_requirements: list[str] = Field(min_length=1)
    approval_requirements: list[str] = Field(min_length=1)
    novelty_dimensions: list[str]
    major_initiative: bool
    accessibility_applicable: bool
    accessibility_reason: str = Field(min_length=1)
    commerce_applicable: bool
    commerce_reason: str = Field(min_length=1)
    open_issues: list[str] = Field(default_factory=list)
    high_cost_source: bool = False
    derivative_plan: DerivativePlan | None = None
    saturation_evidence: list[SourceReference] = Field(default_factory=list)
    recent_devices: list[str] = Field(default_factory=list)
    saturation_classifications: dict[str, str] = Field(default_factory=dict)
    exploration_practical: bool = True
    exploration_exception_reason: str | None = None


class JobContract(Contract):
    contract_id: str
    version: Literal["1.0"] = "1.0"
    job_id: str
    resolved_context_digest: str
    context: ResolvedContext
    plan: JobPlan
    production_path_ready: bool
    status: LifecycleStatus
    blockers: list[str]
    action_authorized: Literal[False] = False

    @model_validator(mode="after")
    def lifecycle_consistency(self):
        expected = (
            "BLOCKED"
            if self.blockers
            else (
                "PRODUCTION_READY"
                if self.context.request_snapshot["lifecycle_stage"] in ("M5", "M6", "M7")
                else self.context.status
            )
        )
        if self.status != expected or self.production_path_ready != (not self.blockers):
            raise ValueError("Job lifecycle/status contradicts resolved blockers")
        if self.context.status == "BLOCKED" and not self.blockers:
            raise ValueError("Blocked context cannot have an unblocked job")
        return self


def contract_payload(context: ResolvedContext, plan: JobPlan, blockers: list[str]) -> dict:
    snapshot = context.model_dump(exclude={"resolved_at"})
    return {
        "context": snapshot,
        "plan": plan.model_dump(),
        "blockers": blockers,
        "version": "1.0",
        "implementation_digest": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def build_job(request: ResolutionRequest, plan: JobPlan) -> JobContract:
    updates = request.model_dump()
    blockers = list(plan.open_issues)
    if (
        request.production_method is not None
        and request.production_method != plan.production_method.technique
    ):
        blockers.append("Request production method contradicts job plan")
    else:
        updates["production_method"] = plan.production_method.technique
    if request.major_initiative and not plan.major_initiative:
        blockers.append("Major-initiative request contradicts job plan")
    updates["major_initiative"] = plan.major_initiative
    request = ResolutionRequest.model_validate(updates)
    context = resolve_context(request)
    if (
        plan.high_cost_source
        or request.content_intent.production_type
        in (
            "photoshoot",
            "editorial_shoot",
            "commercial",
            "short_film",
            "3d_asset",
            "product_scan",
            "location_production",
            "character_system",
            "campaign_environment",
        )
    ) and plan.derivative_plan is None:
        blockers.append("High-cost production requires derivative coverage planning")
    if (
        plan.major_initiative
        and not plan.exploration_practical
        and not (plan.exploration_exception_reason or "").strip()
    ):
        blockers.append("A/B/n exception requires an explicit practicality reason")
    for ref in plan.saturation_evidence:
        try:
            check_reference(ref)
        except (OSError, ValueError) as exc:
            blockers.append(str(exc))
    if (
        request.lifecycle_stage in ("M5", "M6", "M7")
        and plan.major_initiative
        and not plan.saturation_evidence
    ):
        blockers.append("Major production requires recent-work saturation evidence")
    if plan.derivative_plan:
        for application in plan.derivative_plan.applications:
            if (
                request.representation_mode == "EXACT_PRODUCT"
                and application.content_intent.representation_mode == "PRODUCT_CONCEPT"
            ):
                blockers.append("Derivative cannot relabel actual product as a concept")
    if "ACCESSIBILITY" in context.verification_requirements and not plan.accessibility_applicable:
        blockers.append("Content intent requires accessibility verification")
    if "COMMERCE_INTEGRITY" in context.verification_requirements and not plan.commerce_applicable:
        blockers.append("Content intent requires commerce-integrity verification")
    if context.status == "BLOCKED":
        blockers.append("Resolved context is BLOCKED")
    method = plan.production_method
    exact = request.representation_mode == "EXACT_PRODUCT"
    if method.technique == "UNRESOLVED" or (exact and method.technique == "ABSTRACT"):
        blockers.append("No credible fidelity-preserving production method")
    if exact and (not method.inputs or not method.feasibility_evidence):
        blockers.append("Exact-product production requires inputs and feasibility evidence")
    if plan.major_initiative and not plan.novelty_dimensions:
        blockers.append("Major initiative requires meaningful novelty dimensions")
    for ref in method.inputs + method.feasibility_evidence:
        try:
            check_reference(ref)
        except (OSError, ValueError) as exc:
            blockers.append(str(exc))
    if exact and method.technique in ("SOURCE_PHOTOGRAPHY", "SOURCE_COMPOSITE"):
        required_paths = {
            str((THEME_ROOT / image["path"]).resolve())
            for product in context.products
            for requirement in request.products
            if product["sku"] == requirement.sku
            for view in requirement.required_views
            if (image := product["images"].get(view))
        }
        required_assets = {
            (s["path"], s["sha256"]) for s in context.source_manifest if s["path"] in required_paths
        }
        supplied = {(str((REPO_ROOT / ref.path).resolve()), ref.sha256) for ref in method.inputs}
        if not required_assets or not required_assets <= supplied:
            blockers.append(
                "Source photography/composite requires every requested canonical view input"
            )
    payload = contract_payload(context, plan, blockers)
    return JobContract(
        contract_id=digest(payload),
        job_id=request.job_id,
        resolved_context_digest=digest(payload["context"]),
        context=context,
        plan=plan,
        production_path_ready=not blockers,
        status=(
            "BLOCKED"
            if blockers
            else (
                "PRODUCTION_READY"
                if request.lifecycle_stage in ("M5", "M6", "M7")
                else context.status
            )
        ),
        blockers=blockers,
    )


class Criterion(Contract):
    result: Literal["PASS", "FAIL", "BLOCKED"] | None
    applicable: bool
    reason: str = Field(min_length=1)

    @model_validator(mode="after")
    def applicability(self):
        if self.applicable != (self.result is not None):
            raise ValueError("Criterion applicability/result mismatch")
        return self


class VerificationRecord(Contract):
    gate: Gate
    contract_id: str = Field(pattern=r"^[0-9a-f]{64}$")
    artifact: SourceReference
    applicable: bool
    applicability_reason: str = Field(min_length=1)
    result: Literal["PASS", "FAIL", "BLOCKED"] | None
    reviewer: str = Field(min_length=1)
    method: str = Field(min_length=1)
    recorded_at: str = Field(min_length=1)
    observations: str = Field(min_length=1)
    evidence: list[SourceReference]
    criteria: dict[str, Criterion] = Field(default_factory=dict)

    @model_validator(mode="after")
    def applicability(self):
        if self.applicable != (self.result is not None):
            raise ValueError("Gate applicability/result mismatch")
        if self.result == "PASS" and not self.evidence:
            raise ValueError("PASS requires evidence")
        return self


class VerificationAssessment(Contract):
    release_ready: bool
    action_authorized: Literal[False] = False
    blockers: list[str]
    status: LifecycleStatus


def assess_artifact(
    job: JobContract,
    artifact: SourceReference,
    records: list[VerificationRecord],
    *,
    novelty_evidence: list[SourceReference],
    experiment_evidence: list[SourceReference],
    experiment_applicability_reason: str,
    root: Path = REPO_ROOT,
) -> VerificationAssessment:
    """Validate evidence bookkeeping, not pixels or reviewer identity/authentication.

    Caller supplies trusted reviewer records. Never call this an automated fidelity test.
    """
    blockers = list(job.blockers)
    if job.context.request_snapshot["lifecycle_stage"] not in ("M6", "M7"):
        blockers.append("Lifecycle has not reached release-candidate review")
    payload = contract_payload(job.context, job.plan, job.blockers)
    if (
        digest(payload) != job.contract_id
        or digest(payload["context"]) != job.resolved_context_digest
    ):
        blockers.append("Job contract changed after binding")
    try:
        fresh = build_job(ResolutionRequest.model_validate(job.context.request_snapshot), job.plan)
        if fresh.contract_id != job.contract_id:
            blockers.append("Contract/source resolution is stale or inconsistent")
        blockers.extend(fresh.blockers)
        for ref in (
            [artifact]
            + job.plan.production_method.inputs
            + job.plan.production_method.feasibility_evidence
        ):
            check_reference(ref, root)
    except (OSError, ValueError, KeyError) as exc:
        blockers.append(str(exc))
    if job.plan.major_initiative and not novelty_evidence:
        blockers.append("Novelty/saturation evidence missing")
    if not experiment_evidence and not experiment_applicability_reason.strip():
        blockers.append("Experiment evidence or explicit non-applicability reason required")
    applicable = dict.fromkeys(GATES, True)
    applicable["PRODUCT_FIDELITY"] = (
        job.context.request_snapshot["representation_mode"] == "EXACT_PRODUCT"
    )
    applicable["ACCESSIBILITY"] = (
        job.plan.accessibility_applicable
        or "ACCESSIBILITY" in job.context.verification_requirements
    )
    applicable["COMMERCE_INTEGRITY"] = (
        job.plan.commerce_applicable
        or "COMMERCE_INTEGRITY" in job.context.verification_requirements
    )
    by_gate = {r.gate: r for r in records}
    if len(by_gate) != len(records):
        blockers.append("Duplicate gate records")
    for gate in GATES:
        record = by_gate.get(gate)
        if record is None:
            blockers.append(f"{gate}: missing record")
            continue
        if record.contract_id != job.contract_id or record.artifact != artifact:
            blockers.append(f"{gate}: stale artifact or contract binding")
        if record.applicable != applicable[gate]:
            blockers.append(f"{gate}: applicability contradicts job")
        if applicable[gate] and record.result != "PASS":
            blockers.append(f"{gate}: {record.result}")
        if any(c.applicable and c.result != "PASS" for c in record.criteria.values()):
            blockers.append(f"{gate}: criterion did not pass")
        required_criteria = set(job.context.verification_requirements.get(gate, []))
        if gate == "PRODUCT_FIDELITY":
            required_criteria.discard("exact_product_fidelity")
        if applicable[gate] and not required_criteria <= set(record.criteria):
            blockers.append(f"{gate}: missing intent-specific evidence criteria")
        if applicable[gate] and any(
            not record.criteria[c].applicable for c in required_criteria & set(record.criteria)
        ):
            blockers.append(f"{gate}: required intent criterion marked inapplicable")
        if gate == "PRODUCT_FIDELITY" and applicable[gate]:
            if not set(FIDELITY) <= set(record.criteria):
                blockers.append("PRODUCT_FIDELITY: incomplete criteria")
            if any(c.applicable and c.result != "PASS" for c in record.criteria.values()):
                blockers.append("PRODUCT_FIDELITY: criterion did not pass")
            if not any(c.applicable for c in record.criteria.values()):
                blockers.append("PRODUCT_FIDELITY: no applicable criteria")
        for ref in record.evidence:
            try:
                check_reference(ref, root)
            except (OSError, ValueError) as exc:
                blockers.append(str(exc))
    for ref in novelty_evidence + experiment_evidence:
        try:
            check_reference(ref, root)
        except (OSError, ValueError) as exc:
            blockers.append(str(exc))
    return VerificationAssessment(
        release_ready=not blockers,
        blockers=blockers,
        status="BLOCKED" if blockers else "RELEASE_CANDIDATE",
    )


def execution_bundle(job: JobContract) -> dict:
    """Compact safe default; conflicting/raw prose lives only in audit_bundle()."""
    job = JobContract.model_validate(job.model_dump())
    request = job.context.request_snapshot
    selected = set(job.context.execution_rule_ids)
    return {
        "schema_version": "1.0",
        "job": {
            "id": job.job_id,
            "contract_id": job.contract_id,
            "lifecycle": request["lifecycle_stage"],
            "status": job.status,
        },
        "intent": request["content_intent"],
        "brand": {
            "required_rules": job.context.execution_rule_ids,
            "constitution_version": job.context.constitution_version,
            "constitution_sha256": job.context.constitution_digest,
            "rule_source": "docs/brand/constitution-v1/constitution.json",
            "why": {
                r["id"]: r["reason"] for r in job.context.rule_explanations if r["id"] in selected
            },
        },
        "products": job.context.execution_products,
        "production_method": job.plan.production_method.model_dump(),
        "creative": {
            "objective": request["objective"],
            "authored_meaning": job.plan.authored_meaning,
            "experience_outcome": job.plan.experience_outcome,
            "deliverables": job.plan.deliverables,
            "novelty": job.plan.novelty_dimensions,
            "freedom": {
                "environment": "HIGH",
                "lighting": "HIGH",
                "composition": "HIGH",
                "product": (
                    "NONE"
                    if request["representation_mode"] == "EXACT_PRODUCT"
                    else "NO_REAL_PRODUCT"
                ),
            },
            "local_discovery": (
                {
                    "instruction": "Explore relevant local territory; no landmark is mandatory",
                    "territories": LOCAL_TERRITORY,
                }
                if request["place_relevant"]
                else None
            ),
        },
        "palette": job.context.palette_policies,
        "constraints": request["constraints"],
        "verification_requirements": job.context.verification_requirements,
        "missing_context": job.context.missing_context,
        "explicit_absences": {
            k: v
            for k, v in request["absence_reasons"].items()
            if not (k == "collection_context" and job.context.applicable_context)
        },
        "resolved_collection_context": job.context.applicable_context,
        "blockers": job.blockers,
        "leverage": job.plan.derivative_plan.model_dump() if job.plan.derivative_plan else None,
        "saturation": {
            "status": "EVIDENCED" if job.plan.saturation_evidence else "UNKNOWN_NOT_REVIEWED",
            "recent_devices": job.plan.recent_devices if job.plan.saturation_evidence else [],
            "classifications": (
                job.plan.saturation_classifications if job.plan.saturation_evidence else {}
            ),
            "evidence": [r.model_dump() for r in job.plan.saturation_evidence],
            "abn_required": job.plan.major_initiative and job.plan.exploration_practical,
            "exception": job.plan.exploration_exception_reason,
            "similarity_is_brand_gate": False,
        },
        "audit_reference": {
            "resolution_id": job.context.resolution_id,
            "context_digest": job.resolved_context_digest,
        },
        "release": {
            "publication_authorized": False,
            "deployment_authorized": False,
            "spend_authorized": False,
            "release_ready": False,
        },
    }


def audit_bundle(job: JobContract) -> dict:
    return {
        "schema_version": "1.0",
        "job": job.model_dump(),
        "considered_rules": job.context.rule_explanations,
        "raw_product_snapshots": job.context.products,
        "authority_conflicts": job.context.product_conflicts,
        "execution_digest": digest(execution_bundle(job)),
    }


def render_brief(job: JobContract, *, debug: bool = False) -> str:
    """Default to the execution projection; full audit requires explicit debug mode."""
    bundle = audit_bundle(job) if debug else execution_bundle(job)
    return (
        "# "
        + ("Audit bundle" if debug else "Execution brief")
        + "\n\n"
        + json.dumps(bundle, indent=2, ensure_ascii=False)
    )
