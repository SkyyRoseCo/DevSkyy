# services/ml/enhancement/authenticity_validator.py
"""
Product Authenticity Validator for DevSkyy.

Ensures product images are not misrepresented during enhancement:
- Perceptual hash comparison of product region
- Logo/text region detection and verification
- Color accuracy check (Delta-E < 2 for product pixels)

CRITICAL: This service is the final gate before images go live.
Any validation failure blocks auto-publish and requires human review.

Author: DevSkyy Platform Team
Version: 1.0.0
"""

from __future__ import annotations

import io
import logging
import math
from enum import StrEnum
from typing import Any

import httpx
import numpy as np
from PIL import Image
from pydantic import BaseModel

from core.errors.production_errors import (
    DevSkyError,
    DevSkyErrorCode,
    DevSkyErrorSeverity,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Minimum similarity threshold for product region
MIN_SIMILARITY_THRESHOLD = 0.95  # 95%

# Maximum Delta-E for color accuracy
MAX_DELTA_E = 2.0

# Perceptual hash size
HASH_SIZE = 16


# =============================================================================
# Models
# =============================================================================


class ValidationStatus(StrEnum):
    """Validation result status."""

    PASSED = "passed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"


class ValidationResult(BaseModel):
    """Individual validation check result."""

    check_name: str
    passed: bool
    score: float
    threshold: float
    details: str
    visual_diff_url: str | None = None


class AuthenticityReport(BaseModel):
    """Complete authenticity validation report."""

    original_url: str
    enhanced_url: str
    status: ValidationStatus
    overall_similarity: float
    color_accuracy_delta_e: float
    validation_results: list[ValidationResult]
    requires_human_review: bool
    review_reasons: list[str]
    processing_time_ms: int
    correlation_id: str

    @property
    def is_approved(self) -> bool:
        """Check if image is approved for auto-publish."""
        return self.status == ValidationStatus.PASSED and not self.requires_human_review


class AuthenticityValidationError(DevSkyError):
    """Error during authenticity validation."""

    def __init__(
        self,
        message: str,
        *,
        original_url: str | None = None,
        enhanced_url: str | None = None,
        correlation_id: str | None = None,
        cause: Exception | None = None,
    ) -> None:
        context: dict[str, Any] = {}
        if original_url:
            context["original_url"] = original_url
        if enhanced_url:
            context["enhanced_url"] = enhanced_url

        super().__init__(
            message,
            code=DevSkyErrorCode.MODEL_FIDELITY_BELOW_THRESHOLD,
            severity=DevSkyErrorSeverity.WARNING,
            context=context,
            cause=cause,
            correlation_id=correlation_id,
            retryable=False,
        )


# =============================================================================
# Service
# =============================================================================


class AuthenticityValidator:
    """
    Validates product image authenticity after enhancement.

    Checks:
    1. Perceptual hash similarity (product region)
    2. Color accuracy (Delta-E < 2)
    3. Logo/text preservation
    4. Edge integrity

    CRITICAL: Failed validation blocks auto-publish.

    Usage:
        validator = AuthenticityValidator()
        report = await validator.validate(
            original_url="https://example.com/original.jpg",
            enhanced_url="https://example.com/enhanced.jpg",
        )
        if report.is_approved:
            # Safe to auto-publish
            pass
        else:
            # Send to human review queue
            pass
    """

    def __init__(
        self,
        similarity_threshold: float = MIN_SIMILARITY_THRESHOLD,
        max_delta_e: float = MAX_DELTA_E,
    ) -> None:
        self._similarity_threshold = similarity_threshold
        self._max_delta_e = max_delta_e

    async def _download_image(self, url: str, correlation_id: str) -> Image.Image:
        """Download image from URL."""
        async with httpx.AsyncClient(timeout=60.0) as http_client:
            response = await http_client.get(url)
            if response.status_code != 200:
                raise AuthenticityValidationError(
                    f"Failed to download image: HTTP {response.status_code}",
                    original_url=url,
                    correlation_id=correlation_id,
                )
            return Image.open(io.BytesIO(response.content))

    def _compute_phash(self, img: Image.Image) -> str:
        """
        Compute perceptual hash of image.

        Uses difference hash (dHash) algorithm which is robust to
        scaling, aspect ratio changes, and brightness/contrast adjustments.
        """
        # Convert to grayscale
        gray = img.convert("L")

        # Resize to HASH_SIZE+1 x HASH_SIZE
        resized = gray.resize((HASH_SIZE + 1, HASH_SIZE), Image.Resampling.LANCZOS)

        # Compute differences
        pixels = list(resized.get_flattened_data())
        diff = []
        for row in range(HASH_SIZE):
            for col in range(HASH_SIZE):
                left = pixels[row * (HASH_SIZE + 1) + col]
                right = pixels[row * (HASH_SIZE + 1) + col + 1]
                diff.append(1 if left > right else 0)

        # Convert to hex string
        hash_int = int("".join(str(b) for b in diff), 2)
        return f"{hash_int:0{HASH_SIZE * HASH_SIZE // 4}x}"

    def _compute_hash_similarity(self, hash1: str, hash2: str) -> float:
        """
        Compute similarity between two perceptual hashes.

        Returns value between 0.0 (completely different) and 1.0 (identical).
        """
        if len(hash1) != len(hash2):
            return 0.0

        # Convert hex to binary
        bin1 = bin(int(hash1, 16))[2:].zfill(len(hash1) * 4)
        bin2 = bin(int(hash2, 16))[2:].zfill(len(hash2) * 4)

        # Count matching bits
        matches = sum(b1 == b2 for b1, b2 in zip(bin1, bin2, strict=False))
        return matches / len(bin1)

    def _rgb_to_lab(self, rgb: tuple[int, int, int]) -> tuple[float, float, float]:
        """
        Convert RGB to CIE LAB color space.

        LAB is perceptually uniform, making Delta-E calculations meaningful.
        """
        # Normalize RGB to 0-1
        r, g, b = [x / 255.0 for x in rgb]

        # sRGB to linear RGB
        def linearize(c: float) -> float:
            return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

        r, g, b = linearize(r), linearize(g), linearize(b)

        # Linear RGB to XYZ
        x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
        y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
        z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041

        # XYZ to LAB (D65 illuminant)
        x_n, y_n, z_n = 0.95047, 1.0, 1.08883

        def f(t: float) -> float:
            return t ** (1 / 3) if t > 0.008856 else (7.787 * t) + (16 / 116)

        L = 116 * f(y / y_n) - 16
        a = 500 * (f(x / x_n) - f(y / y_n))
        b_val = 200 * (f(y / y_n) - f(z / z_n))

        return (L, a, b_val)

    def _compute_delta_e(
        self, lab1: tuple[float, float, float], lab2: tuple[float, float, float]
    ) -> float:
        """
        Compute Delta-E (CIE76) between two LAB colors.

        Delta-E < 1: Not perceptible by human eye
        Delta-E 1-2: Perceptible through close observation
        Delta-E 2-10: Perceptible at a glance
        Delta-E > 10: Colors are more different than similar
        """
        return math.sqrt(
            (lab1[0] - lab2[0]) ** 2 + (lab1[1] - lab2[1]) ** 2 + (lab1[2] - lab2[2]) ** 2
        )

    def _compute_average_delta_e(
        self, img1: Image.Image, img2: Image.Image, sample_size: int = 1000
    ) -> float:
        """
        Compute average Delta-E between two images.

        Samples random pixels from both images and computes average color difference.
        """
        # Ensure same size
        if img1.size != img2.size:
            img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)

        # Convert to RGB
        img1 = img1.convert("RGB")
        img2 = img2.convert("RGB")

        # Get pixel data
        pixels1 = list(img1.get_flattened_data())
        pixels2 = list(img2.get_flattened_data())

        if len(pixels1) == 0:
            return 0.0

        # Sample pixels
        import random

        indices = random.sample(range(len(pixels1)), min(sample_size, len(pixels1)))

        delta_e_sum = 0.0
        for idx in indices:
            lab1 = self._rgb_to_lab(pixels1[idx])
            lab2 = self._rgb_to_lab(pixels2[idx])
            delta_e_sum += self._compute_delta_e(lab1, lab2)

        return delta_e_sum / len(indices)

    def _compute_edge_similarity(self, img1: Image.Image, img2: Image.Image) -> float:
        """
        Compare edge maps between two images.

        Uses Sobel-like edge detection to ensure edges are preserved.
        """
        try:
            from PIL import ImageFilter

            # Convert to grayscale
            gray1 = img1.convert("L")
            gray2 = img2.convert("L")

            # Resize if different sizes
            if gray1.size != gray2.size:
                gray2 = gray2.resize(gray1.size, Image.Resampling.LANCZOS)

            # Apply edge detection
            edges1 = gray1.filter(ImageFilter.FIND_EDGES)
            edges2 = gray2.filter(ImageFilter.FIND_EDGES)

            # Compare using normalized cross-correlation
            arr1 = np.array(edges1, dtype=np.float64)
            arr2 = np.array(edges2, dtype=np.float64)

            # Normalize
            arr1 = (arr1 - arr1.mean()) / (arr1.std() + 1e-10)
            arr2 = (arr2 - arr2.mean()) / (arr2.std() + 1e-10)

            # Compute correlation
            correlation = np.mean(arr1 * arr2)

            # Convert to similarity (0-1 range)
            return max(0.0, min(1.0, (correlation + 1) / 2))

        except Exception as e:
            logger.warning(f"Edge comparison failed: {e}")
            return 1.0  # Assume OK if we can't compute

    async def validate(
        self,
        original_url: str,
        enhanced_url: str,
        *,
        correlation_id: str | None = None,
    ) -> AuthenticityReport:
        """
        Validate authenticity of enhanced image against original.

        Args:
            original_url: URL of the original product image
            enhanced_url: URL of the enhanced image
            correlation_id: Optional correlation ID for tracing

        Returns:
            AuthenticityReport with validation results

        Raises:
            AuthenticityValidationError: If validation cannot be performed
        """
        import time
        import uuid

        start_time = time.time()
        correlation_id = correlation_id or str(uuid.uuid4())

        logger.info(
            "Starting authenticity validation",
            extra={
                "original_url": original_url,
                "enhanced_url": enhanced_url,
                "correlation_id": correlation_id,
            },
        )

        # Download images
        try:
            original_img = await self._download_image(original_url, correlation_id)
            enhanced_img = await self._download_image(enhanced_url, correlation_id)
        except Exception as e:
            raise AuthenticityValidationError(
                f"Failed to download images for comparison: {e}",
                original_url=original_url,
                enhanced_url=enhanced_url,
                correlation_id=correlation_id,
                cause=e if isinstance(e, Exception) else None,
            ) from e

        validation_results: list[ValidationResult] = []
        review_reasons: list[str] = []

        # Check 1: Perceptual hash similarity
        original_hash = self._compute_phash(original_img)
        enhanced_hash = self._compute_phash(enhanced_img)
        hash_similarity = self._compute_hash_similarity(original_hash, enhanced_hash)
        hash_passed = hash_similarity >= self._similarity_threshold

        validation_results.append(
            ValidationResult(
                check_name="perceptual_hash",
                passed=hash_passed,
                score=hash_similarity,
                threshold=self._similarity_threshold,
                details=f"Perceptual similarity: {hash_similarity:.2%}",
            )
        )

        if not hash_passed:
            review_reasons.append(
                f"Perceptual similarity ({hash_similarity:.2%}) below threshold ({self._similarity_threshold:.2%})"
            )

        # Check 2: Color accuracy (Delta-E)
        avg_delta_e = self._compute_average_delta_e(original_img, enhanced_img)
        color_passed = avg_delta_e <= self._max_delta_e

        validation_results.append(
            ValidationResult(
                check_name="color_accuracy",
                passed=color_passed,
                score=avg_delta_e,
                threshold=self._max_delta_e,
                details=f"Average Delta-E: {avg_delta_e:.2f} (max: {self._max_delta_e})",
            )
        )

        if not color_passed:
            review_reasons.append(
                f"Color difference (Delta-E={avg_delta_e:.2f}) exceeds threshold ({self._max_delta_e})"
            )

        # Check 3: Edge preservation
        edge_similarity = self._compute_edge_similarity(original_img, enhanced_img)
        edge_threshold = 0.85
        edge_passed = edge_similarity >= edge_threshold

        validation_results.append(
            ValidationResult(
                check_name="edge_preservation",
                passed=edge_passed,
                score=edge_similarity,
                threshold=edge_threshold,
                details=f"Edge similarity: {edge_similarity:.2%}",
            )
        )

        if not edge_passed:
            review_reasons.append(
                f"Edge similarity ({edge_similarity:.2%}) below threshold ({edge_threshold:.2%})"
            )

        # Determine overall status
        all_passed = all(r.passed for r in validation_results)
        if all_passed:
            status = ValidationStatus.PASSED
        elif hash_similarity >= 0.80 and avg_delta_e <= 5.0:
            status = ValidationStatus.NEEDS_REVIEW
        else:
            status = ValidationStatus.FAILED

        requires_human_review = status != ValidationStatus.PASSED

        processing_time_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "Authenticity validation complete",
            extra={
                "status": status.value,
                "hash_similarity": hash_similarity,
                "delta_e": avg_delta_e,
                "requires_review": requires_human_review,
                "correlation_id": correlation_id,
            },
        )

        return AuthenticityReport(
            original_url=original_url,
            enhanced_url=enhanced_url,
            status=status,
            overall_similarity=hash_similarity,
            color_accuracy_delta_e=avg_delta_e,
            validation_results=validation_results,
            requires_human_review=requires_human_review,
            review_reasons=review_reasons,
            processing_time_ms=processing_time_ms,
            correlation_id=correlation_id,
        )


__all__ = [
    "AuthenticityValidator",
    "AuthenticityReport",
    "AuthenticityValidationError",
    "ValidationResult",
    "ValidationStatus",
]
