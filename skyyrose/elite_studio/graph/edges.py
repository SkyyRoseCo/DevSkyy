"""
Conditional edge functions for the Elite Studio graph.

Each function takes the current state and returns the name of the
next node to execute. LangGraph uses these as routing decisions
at conditional branch points.

Layer 4 addition: after_quality_v2 replaces after_quality in configs
that enable human review or visual regression.
"""

from __future__ import annotations

from .state import EliteStudioState

# Node name constants
END = "__end__"
PREFLIGHT = "preflight"
GENERATOR = "generator"
QUALITY = "quality"
THREE_D = "three_d"
COMPOSITOR = "compositor"
GHOST_MANNEQUIN_COMPOSITE = "ghost_mannequin_composite"
FINALIZE = "finalize"
HUMAN_REVIEW = "human_review"

# Layer 2 node name constants
PROMPT_ENRICHMENT = "prompt_enrichment"
SAFETY = "safety"
UPSCALING = "upscaling"
COLOR_CORRECTION = "color_correction"
VARIANTS = "variant_generation"
ERROR_END = "__end__"


def after_vision(state: EliteStudioState) -> str:
    """Route after vision analysis: continue or stop."""
    vision = state.get("vision_result")
    if not vision or not vision.success:
        return END
    return GENERATOR


def after_generation(state: EliteStudioState) -> str:
    """Route after image generation: continue or stop."""
    gen = state.get("generation_result")
    if not gen or not gen.success:
        return END
    return QUALITY


def after_quality(state: EliteStudioState) -> str:
    """Route after QC: retry generation, go to compositor, or finalize.

    Retry conditions:
        - QC recommendation is "regenerate"
        - retry_count < max_retries

    Compositor conditions:
        - enable_compositor is True
        - Generation succeeded
    """
    qc = state.get("quality_result")
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 2)

    # Check if QC recommends regeneration and we have retries left
    if qc and qc.success and qc.recommendation == "regenerate" and retry_count < max_retries:
        return GENERATOR

    # Check if compositor is enabled
    qc = state.get("quality_result")
    if not (qc and qc.success and qc.overall_status == "pass" and qc.recommendation == "approve"):
        return FINALIZE  # finalize preserves failed QA, never promotes it

    if state.get("enable_compositor", False):
        return COMPOSITOR

    return FINALIZE


def after_quality_v2(state: EliteStudioState) -> str:
    """Layer 4 routing after dual-QC quality node.

    Routing priority:
    1. Low classifier confidence + human review enabled → human_review node.
    2. QC recommends regenerate + retries remaining → generator.
    3. Compositor enabled → compositor.
    4. Otherwise → finalize.

    Args:
        state: Current graph state.

    Returns:
        Next node name.
    """
    qc = state.get("quality_result")
    classifier = state.get("classifier_result")
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 2)

    enable_human_review: bool = state.get("enable_human_review", False)  # type: ignore[assignment]
    review_threshold: float = state.get("review_confidence_threshold", 0.6)  # type: ignore[assignment]

    # --- Rule 1: Escalate to human review when classifier is uncertain ---
    if (
        enable_human_review
        and classifier is not None
        and classifier.confidence < review_threshold
        and state.get("human_review_result") is None  # not yet reviewed
    ):
        return HUMAN_REVIEW

    # --- Rule 2: QC says regenerate and retries remain ---
    if qc and qc.success and qc.recommendation == "regenerate" and retry_count < max_retries:
        return GENERATOR

    # --- Rule 3: Compositor enabled ---
    qc = state.get("quality_result")
    if not (qc and qc.success and qc.overall_status == "pass" and qc.recommendation == "approve"):
        return FINALIZE  # finalize preserves failed QA, never promotes it

    if state.get("enable_compositor", False):
        return COMPOSITOR

    return FINALIZE


def after_human_review(state: EliteStudioState) -> str:
    """Route after human review decision.

    - Reject → generator (if retries left), else finalize.
    - Approve / timeout → compositor or finalize.
    """
    decision = state.get("human_review_result")
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 2)

    if decision and decision.decision == "reject" and retry_count < max_retries:
        return GENERATOR

    qc = state.get("quality_result")
    if not (qc and qc.success and qc.overall_status == "pass" and qc.recommendation == "approve"):
        return FINALIZE  # finalize preserves failed QA, never promotes it

    if state.get("enable_compositor", False):
        return COMPOSITOR

    return FINALIZE


def after_compositor(state: EliteStudioState) -> str:
    """Always finalize after compositing."""
    return FINALIZE


def after_safety(state: EliteStudioState) -> str:
    """Route after safety check: halt on flagged content, else continue to quality.

    Returns 'error_end' (mapped to END) if the safety filter was triggered,
    otherwise returns 'quality' to proceed with QC.
    """
    safety = state.get("safety_result")
    if safety and safety.success and safety.flagged:
        return "error_end"
    # Also catch the case where safety set status=error directly
    if state.get("status") == "error" and state.get("failed_step") == "safety_filter":
        return "error_end"
    return QUALITY


def after_upscaling(state: EliteStudioState) -> str:
    """Always proceed to color correction (or finalize) after upscaling."""
    return FINALIZE


def after_color_correction(state: EliteStudioState) -> str:
    """Always proceed to compositor/finalize after color correction."""
    return FINALIZE
