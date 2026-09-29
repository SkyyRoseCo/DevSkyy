"""
Frozen dataclasses for the Elite Studio pipeline.

All results are immutable — prevents hidden side effects between pipeline stages.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProductData:
    """Product metadata loaded from override JSON."""

    sku: str
    collection: str
    garment_type_lock: str = ""
    logo_fingerprint: dict[str, Any] = field(default_factory=dict)
    branding_tech: dict[str, Any] = field(default_factory=dict)
    reference_images: tuple[str, ...] = ()

    @classmethod
    def from_override(cls, sku: str, data: dict[str, Any]) -> ProductData:
        """Create from override JSON data."""
        return cls(
            sku=sku.strip().lower(),
            collection=data.get("collection", "unknown"),
            garment_type_lock=data.get("garmentTypeLock", ""),
            logo_fingerprint=data.get("logoFingerprint", {}),
            branding_tech=data.get("brandingTech", {}),
            reference_images=tuple(data.get("referenceImages", [])),
        )


@dataclass(frozen=True)
class VisionAnalysis:
    """Result from a single vision provider."""

    success: bool
    provider: str
    model: str
    analysis: str = ""
    error: str = ""
    char_count: int = 0


@dataclass(frozen=True)
class SynthesizedVision:
    """Merged result from multiple vision providers."""

    success: bool
    unified_spec: str = ""
    providers_used: tuple[str, ...] = ()
    individual_results: tuple[VisionAnalysis, ...] = ()
    error: str = ""
    reference_evidence: dict[str, Any] = field(default_factory=dict)

    @property
    def provider_count(self) -> int:
        return len(self.providers_used)


@dataclass(frozen=True)
class GenerationResult:
    """Result from image generation."""

    success: bool
    provider: str = ""
    model: str = ""
    output_path: str = ""
    error: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class QualityVerification:
    """Result from quality control verification."""

    success: bool
    provider: str = ""
    model: str = ""
    overall_status: str = ""  # pass, warn, fail
    recommendation: str = ""  # approve, regenerate, manual_review
    details: dict[str, Any] = field(default_factory=dict)
    error: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CompositorResult:
    """Result from scene compositing pipeline."""

    success: bool = False
    provider: str = ""  # "fal", "replicate", "fal-kontext"
    model: str = ""  # "flux-fill-pro", "flux-kontext"
    error: str = ""
    scene_name: str = ""
    collection: str = ""
    output_path: str = ""
    alpha_path: str = ""
    qa_status: str = ""  # pass/warn/fail from Gemini QA
    qa_details: dict[str, Any] = field(default_factory=dict)
    stages_completed: int = 0
    audit_log_path: str = ""
    used_fallback: bool = False
    fallback_provider: str = ""


@dataclass(frozen=True)
class TryOnResult:
    """Result from virtual try-on via FASHN API."""

    success: bool
    output_path: str = ""
    garment_sku: str = ""
    model_image_path: str = ""
    provider: str = "fashn"
    latency_s: float = 0.0
    error: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProductionResult:
    """Complete production result for a single product."""

    sku: str
    view: str
    status: str  # success, error
    output_path: str = ""
    vision: SynthesizedVision | None = None
    generation: GenerationResult | None = None
    quality: QualityVerification | None = None
    compositing: CompositorResult | None = None
    tryon: TryOnResult | None = None
    error: str = ""
    step: str = ""  # which step failed (vision, generation, quality)


# ---------------------------------------------------------------------------
# Layer 2 models — optional pipeline stages
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EnrichedPrompt:
    """Result from rule-based prompt enrichment."""

    success: bool
    original_spec: str = ""
    enriched_spec: str = ""
    additions: tuple[str, ...] = ()
    error: str = ""


@dataclass(frozen=True)
class UpscaleResult:
    """Result from image upscaling."""

    success: bool
    output_path: str = ""
    original_resolution: tuple[int, int] = (0, 0)
    final_resolution: tuple[int, int] = (0, 0)
    provider: str = ""  # "replicate" or "pil_lanczos"
    error: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ColorCorrectionResult:
    """Result from PIL-based color correction."""

    success: bool
    output_path: str = ""
    adjustments_applied: tuple[str, ...] = ()
    error: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SafetyResult:
    """Result from content safety check."""

    success: bool
    flagged: bool = False
    categories: tuple[str, ...] = ()
    error: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class VariantSpec:
    """Specification for a single image variant."""

    name: str
    prompt_modifier: str


@dataclass(frozen=True)
class VariantResult:
    """Result for a single generated variant."""

    success: bool
    variant_name: str = ""
    output_path: str = ""
    error: str = ""


# ---------------------------------------------------------------------------
# Phase B2 models — dual-agent pipeline
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DualAgentResult:
    """Structured output from any dual-agent stage."""

    verdict: str  # "consensus" | "disagreement" | "blocked"
    agent_a_output: str
    agent_b_output: str
    winner: str | None  # "a" | "b" | None (for consensus modes)
    reasoning: list[str]


@dataclass(frozen=True)
class PreflightResult:
    """Result of the pre-flight dual-vision reference verification."""

    passed: bool
    sku: str
    agent_a_verdict: str  # "YES: ..." or "NO: ..."
    agent_b_verdict: str
    blocking_reason: str = ""  # set when passed=False
    reference_evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GhostMannequinCompositeResult:
    """Result from the neck-in composite step."""

    success: bool
    output_path: str = ""
    front_path: str = ""
    back_path: str = ""
    neck_in_applied: bool = False  # False for non-collar garments
    error: str = ""
