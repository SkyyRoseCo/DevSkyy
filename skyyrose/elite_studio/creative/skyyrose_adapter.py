"""SkyyRose adapter; canonical product reads remain in the Context Resolver."""

from __future__ import annotations

from dataclasses import dataclass
import json

from skyyrose.core.context_resolver import ResolutionRequest, SourceReference
from skyyrose.core.creative_job import (
    JobPlan,
    audit_bundle,
    build_job,
    execution_bundle,
    check_reference,
)
from skyyrose.core.paths import REPO_ROOT, THEME_ROOT

from .editorial import ResolvedEditorial
from .local_composite import AssetRef


@dataclass(frozen=True)
class SkyyRoseEditorialAdapter:
    request: ResolutionRequest
    plan: JobPlan
    source_role: str
    observed_view: str
    source_review: SourceReference

    def resolve(self) -> ResolvedEditorial:
        job = build_job(self.request, self.plan)
        if job.blockers:
            raise ValueError(f"Blocked job: {job.blockers}")
        if len(job.context.execution_products) != 1:
            raise ValueError("Local still adapter requires exactly one bound product")
        execution = execution_bundle(job)
        product = execution["products"][0]
        ref = product["references"].get(self.source_role)
        if not ref or not ref.get("sha256"):
            raise ValueError("Required canonical source identity missing")
        if self.observed_view != "front":
            raise ValueError("This reviewed source adapter supports front-view stills only")
        source = (THEME_ROOT / ref["path"]).resolve()
        if not source.is_relative_to(REPO_ROOT):
            raise ValueError("Canonical source escapes repository")
        check_reference(self.source_review)
        review = json.loads((REPO_ROOT / self.source_review.path).read_text())
        if (
            review.get("source_sha256") != ref["sha256"]
            or review.get("role") != self.source_role
            or review.get("observed_view") != self.observed_view
            or review.get("sku") != product["sku"]
            or review.get("status") != "PASS"
            or not review.get("reviewer")
            or not review.get("method")
        ):
            raise ValueError("Missing or mismatched source visual-review evidence")
        product["selected_source"] = {
            "review_evidence": self.source_review.model_dump(),
            "role": self.source_role,
            "observed_view": self.observed_view,
            "identity_basis": "canonical role binding plus recorded visual source review",
            "path": str(source.relative_to(REPO_ROOT)),
            "sha256": ref["sha256"],
        }
        audit = audit_bundle(job)
        # Include adapter augmentation in the linked audit identity, not a stale pre-adapter digest.
        from .editorial import identity

        audit["adapter"] = {"selected_source": product["selected_source"]}
        audit["execution_digest"] = identity(execution)
        return ResolvedEditorial(
            execution, audit, AssetRef(str(source.relative_to(REPO_ROOT)), ref["sha256"])
        )
