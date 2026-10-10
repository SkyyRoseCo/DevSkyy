"""
Layer 1 graph nodes — core pipeline stages.

vision, generator, quality, human_review, compositor, tryon, finalize.
All functions are module-level; no classes, no logic duplication with _shared.
"""

from __future__ import annotations

import logging
import time

from ...agents.compositor_agent import CompositorAgent as CompositorAgent  # re-exported
from ...agents.generator_agent import GeneratorAgent as GeneratorAgent  # re-exported
from ...agents.quality_agent import QualityAgent as QualityAgent  # re-exported
from ...agents.tryon_agent import TryOnAgent as TryOnAgent  # re-exported
from ...agents.tryon_agent import _find_garment_image as _find_garment_image  # re-exported
from ...agents.tryon_agent import ensure_public_url as ensure_public_url  # re-exported
from ...agents.vision_agent import VisionAgent as VisionAgent  # re-exported
from ...quality.human_review import HumanReviewGate as HumanReviewGate  # re-exported
from ...quality.ml_classifier import QualityClassifier as QualityClassifier  # re-exported
from ..state import EliteStudioState
from ._shared import (
    _ADK_RENDER_EST_COST_USD,
    _CLASSIFIER_CONFIDENCE_THRESHOLD,
    _COMPOSITOR_EST_COST_USD,
    _COMPOSITOR_TOKENS_ESTIMATE,
    _GENERATION_TOKENS_ESTIMATE,
    _GENERATOR_EST_COST_USD,
    _QC_TOKENS_ESTIMATE,
    _TRYON_EST_COST_USD,
    _VISION_TOKENS_ESTIMATE,
    _record_cost,
    run_sync,
)

logger = logging.getLogger(__name__)


def _shim():
    """Return the public ``graph.nodes`` shim module.

    Agent classes (``VisionAgent``, ``GeneratorAgent``, ``QualityAgent``,
    ``CompositorAgent``, ``TryOnAgent``, ``HumanReviewGate``) and helpers
    like ``_find_garment_image`` are looked up here through the shim so
    that ``patch("skyyrose.elite_studio.graph.nodes.VisionAgent", ...)``
    in tests affects the binding used at call time. Importing the shim
    module (not its attributes) inside this helper keeps the lookup
    lazy and avoids the circular import that would arise from a
    module-level ``from ..nodes import VisionAgent``.
    """
    from .. import nodes as _nodes_shim

    return _nodes_shim


# Lazy import guard so nodes remain testable without prometheus_client installed.
try:
    from monitoring.elite_studio_metrics import record_stage_duration as _record_stage_duration
except ImportError:  # pragma: no cover

    def _record_stage_duration(stage: str, duration_s: float) -> None:  # type: ignore[misc]
        pass


def vision_node(state: EliteStudioState) -> dict:
    """Analyze product images via dual-provider vision (Gemini + OpenAI)."""
    start = time.monotonic()
    agent = _shim().VisionAgent()
    result = run_sync(agent.analyze(state["sku"], state["view"]))
    elapsed = time.monotonic() - start

    job_id: str | None = state.get("job_id")  # type: ignore[assignment]
    _record_cost(job_id, "gemini", _VISION_TOKENS_ESTIMATE // 2)
    _record_cost(job_id, "openai", _VISION_TOKENS_ESTIMATE // 2)

    timings = dict(state.get("stage_timings", {}))
    timings["vision"] = round(elapsed, 2)
    _record_stage_duration("vision", elapsed)

    if not result.success:
        return {
            "vision_result": result,
            "status": "error",
            "error": result.error,
            "failed_step": "vision",
            "stage_timings": timings,
        }

    return {
        "vision_result": result,
        "stage_timings": timings,
    }


def generator_node(state: EliteStudioState) -> dict:
    """Generate fashion model image from vision specification.

    Branches on state["engine"]:
        "legacy"     → GeneratorAgent (default)
        "adk-render" → ADK render_pipeline root_agent (P7)
    """
    from ...budget import BudgetExceededError

    start = time.monotonic()

    engine_selector = state.get("engine", "legacy")
    vision = state.get("vision_result")

    # Legacy path requires a vision_result; ADK path can run without one
    # because the ADK pipeline does its own dossier-driven prompting.
    if engine_selector == "legacy" and (not vision or not vision.success):
        return {
            "status": "error",
            "error": "No vision result available for generation",
            "failed_step": "generation",
        }

    # ADK pipeline runs its own QA + refine loop internally; the cost ceiling
    # there is ~$0.20/view (gen+QA+refine), markedly higher than the legacy
    # $0.04/image estimate. Use the higher number for the budget pre-check
    # when the ADK engine is selected.
    est_cost = (
        _ADK_RENDER_EST_COST_USD if engine_selector == "adk-render" else _GENERATOR_EST_COST_USD
    )

    budget = state.get("budget")
    if budget is not None and hasattr(budget, "ensure_within_budget"):
        try:
            budget.ensure_within_budget(est_cost, stage="generation")
        except BudgetExceededError as exc:
            return {
                "status": "error",
                "error": f"budget exceeded before generation: {exc}",
                "failed_step": "generation",
            }

    if engine_selector == "adk-render":
        # Resolve through the shim so test patches on graph.nodes apply at call time
        result = _shim()._invoke_adk_render_engine(state["sku"], state["view"])
    else:
        agent = _shim().GeneratorAgent()
        result = run_sync(
            agent.generate(
                sku=state["sku"],
                view=state["view"],
                generation_spec=vision.unified_spec,
            )
        )
    elapsed = time.monotonic() - start

    if budget is not None and hasattr(budget, "spend") and getattr(result, "success", False):
        # For the ADK engine prefer the per-run actual cost reported back; fall
        # back to the est_cost so we never under-account.
        actual_cost = est_cost
        if engine_selector == "adk-render":
            reported = getattr(result, "metadata", {}).get("cost_usd")
            if isinstance(reported, (int, float)) and reported > 0:
                actual_cost = float(reported)
        budget.spend(actual_cost, stage="generation")

    job_id: str | None = state.get("job_id")  # type: ignore[assignment]
    _record_cost(job_id, "gemini", _GENERATION_TOKENS_ESTIMATE)

    timings = dict(state.get("stage_timings", {}))
    timings["generation"] = round(elapsed, 2)
    _record_stage_duration("generation", elapsed)

    if not result.success:
        return {
            "generation_result": result,
            "status": "error",
            "error": result.error,
            "failed_step": "generation",
            "stage_timings": timings,
        }

    return {
        "generation_result": result,
        "stage_timings": timings,
    }


def quality_node(state: EliteStudioState) -> dict:
    """Dual-QC: classifier can reject early; approval always needs both vision judges.

    Phase 16 Upgrade: Inspects audit_result from FLUX synthesis first. If
    blocking violations exist, fails immediately without calling ML/LLM.
    """
    start = time.monotonic()

    gen = state.get("generation_result")
    vision = state.get("vision_result")
    if not gen or not gen.success or not vision:
        return {
            "status": "error",
            "error": "No generated image available for QC",
            "failed_step": "quality",
        }

    # --- Stage 0: Fidelity Audit check (Phase 16) ---
    audit_data = gen.metadata.get("audit_result")
    if audit_data:
        from ...agents.vision_audit_agent import VisionAuditResult, VisionAuditViolation

        # Reconstruct violations first
        violation_dicts = audit_data.get("violations", [])
        violations_objs = [VisionAuditViolation(**v) for v in violation_dicts]

        # Reconstruct result object
        audit = VisionAuditResult(
            matches_dossier=bool(audit_data.get("matches_dossier", False)),
            violations=violations_objs,
            raw_text=audit_data.get("raw_text", ""),
            model=audit_data.get("model", ""),
            error=audit_data.get("error", ""),
        )

        if not audit.ok:
            logger.info("[QC] Fidelity audit failed (blocking violations found)")
            from ...models import QualityVerification

            violations = [v.element for v in audit.violations if v.is_blocking]
            quality_result = QualityVerification(
                success=True,
                provider="fidelity_audit",
                model=audit.model,
                overall_status="fail",
                recommendation="regenerate",
                details={
                    "violations": [v.to_dict() for v in audit.violations],
                    "blocking_elements": violations,
                    "reason": "fidelity audit failed",
                },
            )
            elapsed = time.monotonic() - start
            timings = dict(state.get("stage_timings", {}))
            timings["quality"] = round(elapsed, 2)
            return {
                "quality_result": quality_result,
                "stage_timings": timings,
            }

    # --- Stage 1: ML classifier ---
    classifier = _shim().QualityClassifier()
    classifier_result = classifier.predict(gen.output_path)
    logger.info(
        "[QC] classifier: sku=%s score=%.3f confidence=%.3f label=%s",
        state["sku"],
        classifier_result.score,
        classifier_result.confidence,
        classifier_result.label,
    )

    job_id: str | None = state.get("job_id")  # type: ignore[assignment]
    _record_cost(job_id, "anthropic", _QC_TOKENS_ESTIMATE)

    timings = dict(state.get("stage_timings", {}))

    # --- Stage 2: LLM QC (only when classifier is uncertain) ---
    quality_result = None
    if (
        classifier_result.confidence >= _CLASSIFIER_CONFIDENCE_THRESHOLD
        and classifier_result.score < 0.7
    ):
        logger.info(
            "[QC] High-confidence classifier rejection — skipping LLM QC (confidence=%.3f)",
            classifier_result.confidence,
        )
        # Synthesise a QualityVerification from classifier result alone
        from ...models import QualityVerification

        passed = classifier_result.score >= 0.7
        quality_result = QualityVerification(
            success=True,
            provider="clip",
            model="openai/clip-vit-base-patch32",
            overall_status="pass" if passed else "fail",
            recommendation="approve" if passed else "regenerate",
            details={
                "classifier_score": classifier_result.score,
                "classifier_confidence": classifier_result.confidence,
                "classifier_label": classifier_result.label,
                "source": "ml_classifier",
            },
        )
    else:
        logger.info(
            "[QC] Candidate requires dual-vision evidence (classifier confidence %.3f)",
            classifier_result.confidence,
        )
        llm_agent = _shim().QualityAgent()
        quality_result = run_sync(
            llm_agent.verify(
                image_path=gen.output_path,
                expected_spec=vision.unified_spec,
                sku=state["sku"],
                view=state.get("view", "front"),
            )
        )

    elapsed = time.monotonic() - start
    timings["quality"] = round(elapsed, 2)
    _record_stage_duration("quality", elapsed)

    return {
        "quality_result": quality_result,
        "classifier_result": classifier_result,
        "stage_timings": timings,
    }


def human_review_node(state: EliteStudioState) -> dict:
    """Submit generated image to HumanReviewGate and wait for decision.

    On timeout or queue unavailability, defaults to approve so production
    is never blocked indefinitely.

    The review decision is stored in human_review_result. If the reviewer
    rejects the image, quality_result.recommendation is set to "regenerate"
    so the after_quality_v2 edge can trigger a retry.
    """
    start = time.monotonic()

    gen = state.get("generation_result")
    if not gen or not gen.success:
        return {
            "status": "error",
            "error": "No generated image to submit for human review",
            "failed_step": "human_review",
        }

    gate = _shim().HumanReviewGate()
    sku = state["sku"]
    job_id = state.get("workflow_id", sku)

    review_id = gate.submit_for_review(sku=sku, image_path=gen.output_path, job_id=job_id)
    decision = gate.get_decision(review_id)

    logger.info(
        "[HumanReview] sku=%s decision=%s reviewer=%s",
        sku,
        decision.decision,
        decision.reviewer,
    )

    elapsed = time.monotonic() - start
    timings = dict(state.get("stage_timings", {}))
    timings["human_review"] = round(elapsed, 2)

    # If reviewer rejected: override quality recommendation to trigger regeneration
    if decision.decision == "reject":
        existing_qc = state.get("quality_result")
        if existing_qc:
            from ...models import QualityVerification

            updated_qc = QualityVerification(
                success=existing_qc.success,
                provider=existing_qc.provider,
                model=existing_qc.model,
                overall_status="fail",
                recommendation="regenerate",
                details={**existing_qc.details, "human_rejected": True, "notes": decision.notes},
                error=existing_qc.error,
            )
            return {
                "human_review_result": decision,
                "quality_result": updated_qc,
                "stage_timings": timings,
            }

    return {
        "human_review_result": decision,
        "stage_timings": timings,
    }


def compositor_node(state: EliteStudioState) -> dict:  # noqa: C901
    """Composite generated model into scene backgrounds."""
    from ...budget import BudgetExceededError

    start = time.monotonic()

    gen = state.get("generation_result")
    if not gen or not gen.success:
        elapsed = time.monotonic() - start
        timings = dict(state.get("stage_timings", {}))
        timings["compositing"] = round(elapsed, 2)
        return {
            "compositor_result": None,
            "stage_timings": timings,
        }

    # Budget guard — 6-stage compositor dispatches Gemini, IC-Light, and FLUX;
    # pre-check before any provider fires.
    budget = state.get("budget")
    if budget is not None and hasattr(budget, "ensure_within_budget"):
        try:
            budget.ensure_within_budget(_COMPOSITOR_EST_COST_USD, stage="compositing")
        except BudgetExceededError as exc:
            return {
                "status": "error",
                "error": f"budget exceeded before compositing: {exc}",
                "failed_step": "compositing",
            }

    agent = _shim().CompositorAgent()
    comp_result = None

    try:
        from ...agents.compositor_agent import SCENE_LOOKBOOK
        from ...utils import discover_scene_images

        for scene_name, sku_prefix in SCENE_LOOKBOOK.items():
            if state["sku"].startswith(sku_prefix):
                collection = (
                    scene_name.rsplit("-", 2)[0] if scene_name.count("-") > 2 else scene_name
                )
                scenes = discover_scene_images(collection)
                if scenes:
                    # composite() is sync since the Phase B2 rewrite — no
                    # run_sync wrapper needed. The model image is the B1
                    # generator output; the scene image is the first scene
                    # discovered for the collection.
                    comp_result = agent.composite(
                        sku=state["sku"],
                        scene_image_path=str(scenes[0]),
                        model_image_path=gen.output_path,
                        scene_name=scene_name,
                        collection=collection,
                        budget=budget,
                    )
                break
    except Exception:
        # Don't crash the graph if compositing breaks — but DO surface the
        # failure. Bare ``pass`` here previously masked real provider errors
        # and made the compositor stage look like a no-op when it had failed.
        logger.exception("compositor_node: composite() raised for sku=%s", state.get("sku"))

    elapsed = time.monotonic() - start

    if comp_result and comp_result.success:
        job_id: str | None = state.get("job_id")  # type: ignore[assignment]
        _record_cost(job_id, "gemini", _COMPOSITOR_TOKENS_ESTIMATE)
        if budget is not None and hasattr(budget, "spend"):
            budget.spend(_COMPOSITOR_EST_COST_USD, stage="compositing")

    timings = dict(state.get("stage_timings", {}))
    timings["compositing"] = round(elapsed, 2)
    _record_stage_duration("compositing", elapsed)

    return {
        "compositor_result": comp_result,
        "stage_timings": timings,
    }


def tryon_node(state: EliteStudioState) -> dict:
    """Run virtual try-on in parallel with compositor (additive — never fails the job).

    Skips silently when:
    - generation_result is absent or unsuccessful
    - no garment image can be found for the SKU
    - budget ceiling would be exceeded
    """
    from ...budget import BudgetExceededError

    start = time.monotonic()
    timings = dict(state.get("stage_timings", {}))

    gen = state.get("generation_result")
    if not gen or not gen.success:
        logger.debug("tryon_node: skipping — no successful generation result")
        timings["tryon"] = round(time.monotonic() - start, 2)
        return {"tryon_result": None, "stage_timings": timings}

    sku = state["sku"]
    garment_path = _shim()._find_garment_image(sku)
    if not garment_path:
        logger.debug("tryon_node: skipping — no garment image found for %s", sku)
        timings["tryon"] = round(time.monotonic() - start, 2)
        return {"tryon_result": None, "stage_timings": timings}

    # Budget guard — FASHN tryon incurs real per-call cost; check ceiling before dispatch.
    budget = state.get("budget")
    if budget is not None and hasattr(budget, "ensure_within_budget"):
        try:
            budget.ensure_within_budget(_TRYON_EST_COST_USD, stage="tryon")
        except BudgetExceededError as exc:
            logger.warning("tryon_node: skipping — %s", exc)
            timings["tryon"] = round(time.monotonic() - start, 2)
            return {"tryon_result": None, "stage_timings": timings}

    category = state.get("tryon_category", "upper_body")
    agent = _shim().TryOnAgent()
    try:
        garment_url = _shim().ensure_public_url(garment_path, sku=sku)
        model_url = _shim().ensure_public_url(gen.output_path, sku=sku)
        result = run_sync(
            agent.execute_tryon(
                garment_image_path=garment_url,
                model_image_path=model_url,
                category=category,
                garment_sku=sku,
            )
        )
    except Exception as exc:
        # Additive stage — never let an upload or FASHN failure crash the job.
        logger.warning("tryon_node: skipping for %s — %s", sku, exc)
        timings["tryon"] = round(time.monotonic() - start, 2)
        return {"tryon_result": None, "stage_timings": timings}

    if budget is not None and hasattr(budget, "spend") and getattr(result, "success", False):
        budget.spend(_TRYON_EST_COST_USD, stage="tryon")

    timings["tryon"] = round(time.monotonic() - start, 2)
    return {"tryon_result": result, "stage_timings": timings}


def finalize_node(state: EliteStudioState) -> dict:
    """Set final status + persist the run summary for downstream auditing.

    Always emits a summary JSON — success or error — so post-run analysis
    can reconstruct what each SKU's pipeline did, what it spent, and
    where it failed. Telemetry write is best-effort: a failed write
    never overrides the run status.
    """
    from ...telemetry import write_run_summary

    qc = state.get("quality_result")
    approved = bool(
        qc and qc.success and qc.overall_status == "pass" and qc.recommendation == "approve"
    )
    final_status = "success" if state.get("status") != "error" and approved else "error"

    budget = state.get("budget")
    budget_snap = budget.snapshot() if budget is not None and hasattr(budget, "snapshot") else None

    qa = state.get("quality_result")
    gen = state.get("generation_result")
    three_d_score = state.get("three_d_fidelity_score") or 0.0

    summary = {
        "workflow_id": state.get("workflow_id"),
        "sku": state.get("sku"),
        "view": state.get("view"),
        "style": state.get("style"),
        "status": final_status,
        "error": state.get("error", ""),
        "failed_step": state.get("failed_step", ""),
        "generation_engine": getattr(gen, "provider", None) or getattr(gen, "model", None),
        "qa_score": qa.details.get("min_score") if qa else None,
        "qa_passed": approved,
        "three_d_fidelity_score": three_d_score,
        "three_d_model_path": state.get("three_d_model_path", ""),
        "budget": budget_snap,
        "stage_timings": dict(state.get("stage_timings", {}) or {}),
    }

    workflow_id = state.get("workflow_id") or "unknown"
    summary_path = write_run_summary(workflow_id, summary)

    out: dict = {"status": final_status}
    if not approved and state.get("status") != "error":
        out.update(error="Quality gate did not approve candidate", failed_step="quality")
    if summary_path is not None:
        out["run_summary_path"] = str(summary_path)
    return out
