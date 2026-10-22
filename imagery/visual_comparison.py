"""Visual Comparison Engine for Asset Fidelity.

Provides real visual similarity metrics between reference images and generated assets:
- SSIM (Structural Similarity Index)
- Color histogram matching
- Perceptual hash distance
- Aggregated fidelity score with 90% threshold

Author: DevSkyy Platform Team
Version: 1.0.0
"""

from __future__ import annotations

import importlib.util
import logging
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

import numpy as np
from PIL import Image
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Optional imports with availability flags
try:
    from skimage import img_as_float
    from skimage.metrics import structural_similarity as ssim

    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False
    logger.warning("scikit-image not available. SSIM comparison disabled.")

try:
    import imagehash

    IMAGEHASH_AVAILABLE = True
except ImportError:
    IMAGEHASH_AVAILABLE = False
    logger.warning("imagehash not available. Perceptual hash comparison disabled.")

try:
    import cv2

    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("OpenCV not available. Color histogram comparison disabled.")


def _module_available(name: str) -> bool:
    """True when ``name`` is importable, without importing it.

    A meta-path finder may raise instead of returning None (the ML-optional test
    blocks modules that way), and find_spec raises ValueError for a module whose
    ``__spec__`` is unset — both mean "not available", never a crash at import.
    """
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False


# Probe CLIP dependencies without importing them; load the libraries only when
# a CLIP comparison is requested.
CLIP_AVAILABLE = _module_available("torch") and _module_available("transformers")
if not CLIP_AVAILABLE:
    logger.warning("transformers/torch not available. CLIP semantic comparison disabled.")
_clip_model: object | None = None
_clip_processor: object | None = None


class ComparisonConfidence(StrEnum):
    """Confidence level of comparison result."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ComparisonResult(BaseModel):
    """Result of visual comparison between reference and generated asset."""

    ssim_score: float | None = Field(
        None, ge=0.0, le=1.0, description="Structural similarity (0-1)"
    )
    color_similarity: float | None = Field(
        None, ge=0.0, le=1.0, description="Color histogram match (0-1)"
    )
    perceptual_hash_distance: int | None = Field(
        None, ge=0, description="Hash distance (0=identical, 64=opposite)"
    )
    perceptual_similarity: float | None = Field(
        None, ge=0.0, le=1.0, description="Perceptual hash as similarity (0-1)"
    )
    clip_score: float | None = Field(
        None, ge=0.0, le=1.0, description="CLIP cosine similarity — semantic alignment (0-1)"
    )

    overall_similarity: float = Field(..., ge=0.0, le=100.0, description="Weighted average (0-100)")
    passed: bool = Field(..., description="True if >= threshold")
    threshold_used: float = Field(default=90.0, description="Threshold percentage")
    confidence: ComparisonConfidence = Field(default=ComparisonConfidence.MEDIUM)

    metrics_used: list[str] = Field(default_factory=list, description="Which metrics were computed")
    issues: list[str] = Field(default_factory=list, description="Problems detected")
    recommendations: list[str] = Field(
        default_factory=list, description="Suggestions for improvement"
    )

    reference_path: str | None = None
    asset_path: str | None = None


@dataclass
class ComparisonWeights:
    """Weights for aggregating similarity metrics."""

    ssim: float = 0.30
    color: float = 0.25
    perceptual: float = 0.20
    clip: float = 0.25  # semantic alignment — catches style/content drift

    def normalize(self, available_metrics: list[str]) -> dict[str, float]:
        """Normalize weights based on available metrics."""
        weights = {}
        if "ssim" in available_metrics:
            weights["ssim"] = self.ssim
        if "color" in available_metrics:
            weights["color"] = self.color
        if "perceptual" in available_metrics:
            weights["perceptual"] = self.perceptual
        if "clip" in available_metrics:
            weights["clip"] = self.clip

        total = sum(weights.values()) if weights else 1.0
        return {k: v / total for k, v in weights.items()}


class VisualComparisonEngine:
    """Engine for comparing visual similarity between images.

    Combines multiple metrics for robust comparison:
    - SSIM for structural similarity
    - Color histogram for color distribution
    - Perceptual hash for overall likeness
    """

    DEFAULT_THRESHOLD = 90.0  # 90% similarity required

    def __init__(
        self,
        threshold: float = DEFAULT_THRESHOLD,
        weights: ComparisonWeights | None = None,
    ) -> None:
        """Initialize comparison engine.

        Args:
            threshold: Minimum similarity percentage to pass (0-100)
            weights: Custom weights for metric aggregation
        """
        self.threshold = threshold
        self.weights = weights or ComparisonWeights()
        self._check_dependencies()

    def _check_dependencies(self) -> None:
        """Log available comparison capabilities."""
        available = []
        if SKIMAGE_AVAILABLE:
            available.append("SSIM")
        if CV2_AVAILABLE:
            available.append("ColorHistogram")
        if IMAGEHASH_AVAILABLE:
            available.append("PerceptualHash")
        if CLIP_AVAILABLE:
            available.append("CLIP")

        if not available:
            logger.warning("No visual comparison backends available!")
        else:
            logger.info(f"Visual comparison backends: {', '.join(available)}")

    def _load_image(self, path: Path | str) -> Image.Image:
        """Load image from path."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")
        return Image.open(path).convert("RGB")

    def _prepare_images(
        self,
        reference: Image.Image,
        generated: Image.Image,
        target_size: tuple[int, int] = (512, 512),
    ) -> tuple[np.ndarray, np.ndarray]:
        """Prepare images for comparison by resizing to same dimensions."""
        ref_resized = reference.resize(target_size, Image.Resampling.LANCZOS)
        gen_resized = generated.resize(target_size, Image.Resampling.LANCZOS)
        return np.array(ref_resized), np.array(gen_resized)

    def compute_ssim(
        self,
        reference: np.ndarray,
        generated: np.ndarray,
    ) -> float | None:
        """Compute Structural Similarity Index (SSIM).

        Args:
            reference: Reference image array (RGB)
            generated: Generated image array (RGB)

        Returns:
            SSIM score (0-1) or None if unavailable
        """
        if not SKIMAGE_AVAILABLE:
            return None

        try:
            # Convert to float and grayscale for SSIM
            ref_gray = img_as_float(np.mean(reference, axis=2))
            gen_gray = img_as_float(np.mean(generated, axis=2))

            # Compute SSIM
            score = ssim(ref_gray, gen_gray, data_range=1.0)
            return float(max(0.0, min(1.0, score)))
        except Exception as e:
            logger.error(f"SSIM computation failed: {e}")
            return None

    def compute_color_similarity(
        self,
        reference: np.ndarray,
        generated: np.ndarray,
        bins: int = 64,
    ) -> float | None:
        """Compare color histograms using correlation.

        Args:
            reference: Reference image array (RGB)
            generated: Generated image array (RGB)
            bins: Number of histogram bins per channel

        Returns:
            Color similarity (0-1) or None if unavailable
        """
        if not CV2_AVAILABLE:
            return None

        try:
            # Convert RGB to BGR for OpenCV
            ref_bgr = cv2.cvtColor(reference, cv2.COLOR_RGB2BGR)
            gen_bgr = cv2.cvtColor(generated, cv2.COLOR_RGB2BGR)

            # Compute histograms for each channel
            similarities = []
            for i in range(3):
                ref_hist = cv2.calcHist([ref_bgr], [i], None, [bins], [0, 256])
                gen_hist = cv2.calcHist([gen_bgr], [i], None, [bins], [0, 256])

                # Normalize histograms
                cv2.normalize(ref_hist, ref_hist, 0, 1, cv2.NORM_MINMAX)
                cv2.normalize(gen_hist, gen_hist, 0, 1, cv2.NORM_MINMAX)

                # Compare using correlation
                corr = cv2.compareHist(ref_hist, gen_hist, cv2.HISTCMP_CORREL)
                similarities.append(max(0.0, corr))  # Correlation can be negative

            # Average across channels
            return float(sum(similarities) / len(similarities))
        except Exception as e:
            logger.error(f"Color histogram comparison failed: {e}")
            return None

    def compute_perceptual_hash(
        self,
        reference: Image.Image,
        generated: Image.Image,
    ) -> tuple[int | None, float | None]:
        """Compute perceptual hash distance.

        Args:
            reference: Reference PIL image
            generated: Generated PIL image

        Returns:
            Tuple of (hash_distance, similarity) or (None, None) if unavailable
        """
        if not IMAGEHASH_AVAILABLE:
            return None, None

        try:
            # Compute perceptual hashes
            ref_hash = imagehash.phash(reference)
            gen_hash = imagehash.phash(generated)

            # Hamming distance (0 = identical, 64 = completely different)
            distance = ref_hash - gen_hash

            # Convert to similarity (0-1)
            similarity = 1.0 - (distance / 64.0)

            return int(distance), float(similarity)
        except Exception as e:
            logger.error(f"Perceptual hash comparison failed: {e}")
            return None, None

    def compute_clip_score(
        self,
        reference: Image.Image,
        generated: Image.Image,
    ) -> float | None:
        """Compute CLIP cosine similarity — semantic alignment between two images.

        Uses openai/clip-vit-base-patch32. The model is lazy-loaded and cached
        at module level so repeated calls within a session don't reload weights.

        Returns:
            Cosine similarity in [0, 1] or None if transformers/torch unavailable.
            Interpretation: >0.28 pass, 0.22-0.28 human queue, <0.22 regenerate.
        """
        if not CLIP_AVAILABLE:
            return None

        global _clip_model, _clip_processor
        try:
            import torch
            from transformers import CLIPModel, CLIPProcessor

            if _clip_model is None or _clip_processor is None:
                _clip_model = CLIPModel.from_pretrained(
                    "openai/clip-vit-base-patch32"
                )  # nosec B615 — well-known public model from OpenAI
                _clip_processor = CLIPProcessor.from_pretrained(
                    "openai/clip-vit-base-patch32"
                )  # nosec B615 — same
                _clip_model.eval()

            inputs = _clip_processor(
                images=[reference, generated], return_tensors="pt", padding=True
            )
            with torch.no_grad():
                features = _clip_model.get_image_features(**inputs)
                features = features / features.norm(dim=-1, keepdim=True)
                similarity = (features[0] @ features[1]).item()

            # Cosine similarity is in [-1, 1]; clamp to [0, 1] for consistent scoring
            return float(max(0.0, similarity))
        except Exception as e:
            logger.warning(f"CLIP scoring failed: {e}")
            return None

    def compare(
        self,
        reference_path: Path | str,
        generated_path: Path | str,
    ) -> ComparisonResult:
        """Compare reference image with generated asset.

        Args:
            reference_path: Path to reference/source image
            generated_path: Path to generated asset image

        Returns:
            ComparisonResult with similarity scores and pass/fail status
        """
        issues: list[str] = []
        recommendations: list[str] = []
        metrics_used: list[str] = []
        scores: dict[str, float] = {}

        try:
            # Load images
            ref_img = self._load_image(reference_path)
            gen_img = self._load_image(generated_path)

            # Prepare for comparison
            ref_arr, gen_arr = self._prepare_images(ref_img, gen_img)

            # Compute SSIM
            ssim_score = self.compute_ssim(ref_arr, gen_arr)
            if ssim_score is not None:
                scores["ssim"] = ssim_score
                metrics_used.append("ssim")
                if ssim_score < 0.5:
                    issues.append(f"Low structural similarity: {ssim_score:.1%}")
                    recommendations.append("Check if generated asset captures main shapes/features")

            # Compute color similarity
            color_score = self.compute_color_similarity(ref_arr, gen_arr)
            if color_score is not None:
                scores["color"] = color_score
                metrics_used.append("color")
                if color_score < 0.5:
                    issues.append(f"Poor color match: {color_score:.1%}")
                    recommendations.append("Adjust color/material settings in generation")

            # Compute perceptual hash
            hash_distance, hash_similarity = self.compute_perceptual_hash(ref_img, gen_img)
            if hash_similarity is not None:
                scores["perceptual"] = hash_similarity
                metrics_used.append("perceptual")
                if hash_similarity < 0.6:
                    issues.append(f"Low perceptual similarity: {hash_similarity:.1%}")
                    recommendations.append("Generated asset may not resemble reference overall")

            # Compute CLIP semantic alignment
            clip_score = self.compute_clip_score(ref_img, gen_img)
            if clip_score is not None:
                scores["clip"] = clip_score
                metrics_used.append("clip")
                if clip_score < 0.22:
                    issues.append(f"Semantic mismatch (CLIP={clip_score:.3f}) — regenerate")
                    recommendations.append(
                        "Generated asset is semantically different from reference; trigger regeneration"
                    )
                elif clip_score < 0.28:
                    issues.append(
                        f"Low semantic alignment (CLIP={clip_score:.3f}) — human review recommended"
                    )
                    recommendations.append(
                        "Queue for manual review; asset may differ in style or subject"
                    )

            # Compute weighted overall score
            if scores:
                normalized_weights = self.weights.normalize(metrics_used)
                overall = sum(scores[k] * normalized_weights[k] for k in scores)
                overall_pct = overall * 100
            else:
                overall_pct = 0.0
                issues.append("No comparison metrics available")
                recommendations.append("Install scikit-image, imagehash, or opencv-python")

            # Determine confidence
            if len(metrics_used) >= 3:
                confidence = ComparisonConfidence.HIGH
            elif len(metrics_used) >= 2:
                confidence = ComparisonConfidence.MEDIUM
            else:
                confidence = ComparisonConfidence.LOW

            passed = overall_pct >= self.threshold

            return ComparisonResult(
                ssim_score=ssim_score,
                color_similarity=color_score,
                perceptual_hash_distance=hash_distance,
                perceptual_similarity=hash_similarity,
                clip_score=clip_score,
                overall_similarity=round(overall_pct, 2),
                passed=passed,
                threshold_used=self.threshold,
                confidence=confidence,
                metrics_used=metrics_used,
                issues=issues,
                recommendations=recommendations,
                reference_path=str(reference_path),
                asset_path=str(generated_path),
            )

        except FileNotFoundError as e:
            return ComparisonResult(
                overall_similarity=0.0,
                passed=False,
                threshold_used=self.threshold,
                confidence=ComparisonConfidence.LOW,
                issues=[str(e)],
                recommendations=["Ensure both reference and generated images exist"],
                reference_path=str(reference_path),
                asset_path=str(generated_path),
            )
        except Exception as e:
            logger.exception(f"Comparison failed: {e}")
            return ComparisonResult(
                overall_similarity=0.0,
                passed=False,
                threshold_used=self.threshold,
                confidence=ComparisonConfidence.LOW,
                issues=[f"Comparison error: {e}"],
                recommendations=["Check image formats and validity"],
                reference_path=str(reference_path),
                asset_path=str(generated_path),
            )

    def compare_colors_only(
        self,
        reference_path: Path | str,
        generated_path: Path | str,
    ) -> ComparisonResult:
        """Compare only color distribution (faster, less accurate).

        Useful for quick checks or when structural comparison isn't needed.
        """
        try:
            ref_img = self._load_image(reference_path)
            gen_img = self._load_image(generated_path)
            ref_arr, gen_arr = self._prepare_images(ref_img, gen_img)

            color_score = self.compute_color_similarity(ref_arr, gen_arr)
            if color_score is None:
                return ComparisonResult(
                    overall_similarity=0.0,
                    passed=False,
                    threshold_used=self.threshold,
                    issues=["Color comparison unavailable"],
                )

            overall_pct = color_score * 100
            return ComparisonResult(
                color_similarity=color_score,
                overall_similarity=round(overall_pct, 2),
                passed=overall_pct >= self.threshold,
                threshold_used=self.threshold,
                confidence=ComparisonConfidence.LOW,
                metrics_used=["color"],
                reference_path=str(reference_path),
                asset_path=str(generated_path),
            )
        except Exception as e:
            return ComparisonResult(
                overall_similarity=0.0,
                passed=False,
                threshold_used=self.threshold,
                issues=[str(e)],
            )

    async def compare_async(
        self,
        reference_path: Path | str,
        generated_path: Path | str,
    ) -> ComparisonResult:
        """Async wrapper for compare() method."""
        import asyncio

        return await asyncio.get_event_loop().run_in_executor(
            None, self.compare, reference_path, generated_path
        )


# Convenience function
def compare_images(
    reference: Path | str,
    generated: Path | str,
    threshold: float = 90.0,
) -> ComparisonResult:
    """Compare two images and return similarity result.

    Args:
        reference: Path to reference image
        generated: Path to generated/compared image
        threshold: Minimum similarity percentage to pass (0-100)

    Returns:
        ComparisonResult with scores and pass/fail status

    Example:
        >>> result = compare_images("product.jpg", "generated_3d_render.png")
        >>> if result.passed:
        ...     print(f"Match! {result.overall_similarity:.1f}%")
        >>> else:
        ...     print(f"Mismatch: {result.issues}")
    """
    engine = VisualComparisonEngine(threshold=threshold)
    return engine.compare(reference, generated)


__all__ = [
    "VisualComparisonEngine",
    "ComparisonResult",
    "ComparisonConfidence",
    "ComparisonWeights",
    "compare_images",
]
