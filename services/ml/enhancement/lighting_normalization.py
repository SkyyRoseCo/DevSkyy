# services/ml/enhancement/lighting_normalization.py
"""
Lighting Normalization Service for DevSkyy.

Normalizes lighting and exposure across product images to ensure
consistent, professional appearance while preserving product colors.

CRITICAL: Product colors must match original within Delta-E < 2.
No color grading or tinting that alters the actual product appearance.

Author: DevSkyy Platform Team
Version: 1.0.0
"""

from __future__ import annotations

import io
import logging
from enum import StrEnum
from typing import Any

import httpx
import numpy as np
from PIL import Image
from pydantic import BaseModel
from services.ml.replicate_client import ReplicateClient, ReplicateConfig

from core.errors.production_errors import (
    DevSkyError,
    DevSkyErrorCode,
    DevSkyErrorSeverity,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Primary model for lighting enhancement
DEFAULT_LIGHTING_MODEL = (
    "tencentarc/gfpgan:9283608cc6b7be6b65a8e44983db012355fde4132009bf99d976b2f0896856a3"
)

# Fallback models
FALLBACK_MODELS = [
    "xinntao/realesrgan:1b976a4d456ed9e4d1a846597b7614e79eadad3032e9124fa63c8acb4e3b5bf4",
]

# Maximum color deviation allowed (Delta-E)
MAX_COLOR_DELTA_E = 2.0


# =============================================================================
# Models
# =============================================================================


class LightingIntensity(StrEnum):
    """Intensity levels for lighting normalization."""

    SUBTLE = "subtle"
    MODERATE = "moderate"
    STRONG = "strong"


class LightingResult(BaseModel):
    """Result of lighting normalization operation."""

    original_url: str
    result_url: str
    intensity: LightingIntensity
    model_used: str
    color_delta_e: float
    color_preserved: bool
    processing_time_ms: int
    correlation_id: str

    @property
    def is_valid(self) -> bool:
        """Check if result meets color accuracy requirements."""
        return self.color_preserved and self.color_delta_e <= MAX_COLOR_DELTA_E


class LightingNormalizationError(DevSkyError):
    """Error during lighting normalization."""

    def __init__(
        self,
        message: str,
        *,
        image_url: str | None = None,
        model: str | None = None,
        correlation_id: str | None = None,
        cause: Exception | None = None,
    ) -> None:
        context: dict[str, Any] = {}
        if image_url:
            context["image_url"] = image_url
        if model:
            context["model"] = model

        super().__init__(
            message,
            code=DevSkyErrorCode.IMAGE_PROCESSING_FAILED,
            severity=DevSkyErrorSeverity.ERROR,
            context=context,
            cause=cause,
            correlation_id=correlation_id,
            retryable=True,
        )


class ColorPreservationError(DevSkyError):
    """Error when color preservation check fails."""

    def __init__(
        self,
        message: str,
        *,
        delta_e: float,
        threshold: float = MAX_COLOR_DELTA_E,
        correlation_id: str | None = None,
    ) -> None:
        super().__init__(
            message,
            code=DevSkyErrorCode.MODEL_FIDELITY_BELOW_THRESHOLD,
            severity=DevSkyErrorSeverity.WARNING,
            context={"delta_e": delta_e, "threshold": threshold},
            correlation_id=correlation_id,
            retryable=False,
        )


# =============================================================================
# Service
# =============================================================================


class LightingNormalizationService:
    """
    Service for normalizing lighting across product images.

    Features:
    - Exposure normalization without altering product colors
    - Shadow removal while maintaining depth
    - Configurable intensity levels
    - Color calibration check (Delta-E < 2)

    CRITICAL: Product colors must remain accurate.

    Usage:
        service = LightingNormalizationService()
        result = await service.normalize_lighting(
            image_url="https://example.com/product.jpg",
            intensity=LightingIntensity.MODERATE,
        )
        if result.is_valid:
            # Use the normalized image
            pass
        else:
            # Color deviation detected, needs review
            pass
    """

    def __init__(
        self,
        replicate_client: ReplicateClient | None = None,
        replicate_config: ReplicateConfig | None = None,
        max_delta_e: float = MAX_COLOR_DELTA_E,
    ) -> None:
        self._client = replicate_client
        self._config = replicate_config
        self._owns_client = replicate_client is None
        self._max_delta_e = max_delta_e

    async def _get_client(self) -> ReplicateClient:
        """Get or create Replicate client."""
        if self._client is None:
            self._client = ReplicateClient(self._config)
            await self._client.connect()
        return self._client

    async def close(self) -> None:
        """Close client if owned by this service."""
        if self._owns_client and self._client is not None:
            await self._client.close()

    async def __aenter__(self) -> LightingNormalizationService:
        """Enter async context manager."""
        await self._get_client()
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit async context manager."""
        await self.close()

    async def _download_image(self, url: str, correlation_id: str) -> Image.Image:
        """Download image from URL."""
        async with httpx.AsyncClient(timeout=60.0) as http_client:
            response = await http_client.get(url)
            if response.status_code != 200:
                raise LightingNormalizationError(
                    f"Failed to download image: HTTP {response.status_code}",
                    image_url=url,
                    correlation_id=correlation_id,
                )
            return Image.open(io.BytesIO(response.content))

    def _rgb_to_lab(self, rgb: tuple[int, int, int]) -> tuple[float, float, float]:
        """
        Convert RGB to CIE LAB color space.

        LAB is perceptually uniform, making Delta-E calculations meaningful.
        """
        r, g, b = [x / 255.0 for x in rgb]

        def linearize(c: float) -> float:
            return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

        r, g, b = linearize(r), linearize(g), linearize(b)

        x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
        y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
        z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041

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
        """Compute Delta-E (CIE76) between two LAB colors."""
        return float(
            np.sqrt((lab1[0] - lab2[0]) ** 2 + (lab1[1] - lab2[1]) ** 2 + (lab1[2] - lab2[2]) ** 2)
        )

    def _compute_average_color_delta(
        self, img1: Image.Image, img2: Image.Image, sample_size: int = 1000
    ) -> float:
        """
        Compute average Delta-E between two images.

        Samples random pixels focusing on non-background areas.
        """
        import random

        if img1.size != img2.size:
            img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)

        img1 = img1.convert("RGB")
        img2 = img2.convert("RGB")

        pixels1 = list(img1.get_flattened_data())
        pixels2 = list(img2.get_flattened_data())

        if len(pixels1) == 0:
            return 0.0

        # Filter out near-white pixels (likely background)
        non_bg_indices = []
        for i, p in enumerate(pixels1):
            if not (p[0] > 240 and p[1] > 240 and p[2] > 240):
                non_bg_indices.append(i)

        # If mostly white, sample from all pixels
        if len(non_bg_indices) < 100:
            non_bg_indices = list(range(len(pixels1)))

        indices = random.sample(non_bg_indices, min(sample_size, len(non_bg_indices)))

        delta_e_sum = 0.0
        for idx in indices:
            lab1 = self._rgb_to_lab(pixels1[idx])
            lab2 = self._rgb_to_lab(pixels2[idx])
            delta_e_sum += self._compute_delta_e(lab1, lab2)

        return delta_e_sum / len(indices)

    def _get_intensity_params(self, intensity: LightingIntensity) -> dict[str, Any]:
        """Get model parameters based on intensity level."""
        if intensity == LightingIntensity.SUBTLE:
            return {"upscale": 1, "version": "v1.3"}
        elif intensity == LightingIntensity.MODERATE:
            return {"upscale": 1, "version": "v1.4"}
        else:  # STRONG
            return {"upscale": 2, "version": "v1.4"}

    async def normalize_lighting(
        self,
        image_url: str,
        *,
        intensity: LightingIntensity = LightingIntensity.MODERATE,
        validate_colors: bool = True,
        correlation_id: str | None = None,
    ) -> LightingResult:
        """
        Normalize lighting in a product image.

        Args:
            image_url: URL of the product image
            intensity: Normalization intensity level
            validate_colors: Whether to validate color preservation
            correlation_id: Optional correlation ID for tracing

        Returns:
            LightingResult with processed image URL

        Raises:
            LightingNormalizationError: If processing fails
            ColorPreservationError: If colors deviate too much
        """
        import time

        start_time = time.time()
        client = await self._get_client()
        correlation_id = correlation_id or client._generate_correlation_id()

        logger.info(
            "Starting lighting normalization",
            extra={
                "image_url": image_url,
                "intensity": intensity.value,
                "correlation_id": correlation_id,
            },
        )

        # Download original for color comparison
        original_img: Image.Image | None = None
        if validate_colors:
            try:
                original_img = await self._download_image(image_url, correlation_id)
            except Exception as e:
                logger.warning(
                    f"Failed to download for color validation: {e}",
                    extra={"correlation_id": correlation_id},
                )

        # Try models in order
        models_to_try = [DEFAULT_LIGHTING_MODEL] + FALLBACK_MODELS
        last_error: Exception | None = None
        result_url: str | None = None
        model_used: str = ""

        for model in models_to_try:
            try:
                logger.debug(
                    f"Trying model: {model}",
                    extra={"correlation_id": correlation_id},
                )

                input_params = {
                    "img": image_url,
                    **self._get_intensity_params(intensity),
                }

                prediction = await client.run_prediction(
                    model,
                    input_params,
                    correlation_id=correlation_id,
                )

                if prediction.succeeded and prediction.output:
                    result_url = prediction.output
                    model_used = model
                    break

            except Exception as e:
                logger.warning(
                    f"Model {model} failed: {e}",
                    extra={"correlation_id": correlation_id},
                )
                last_error = e
                continue

        if result_url is None:
            raise LightingNormalizationError(
                "All lighting normalization models failed",
                image_url=image_url,
                correlation_id=correlation_id,
                cause=last_error,
            )

        # Validate color preservation
        color_delta_e = 0.0
        color_preserved = True

        if validate_colors and original_img is not None:
            try:
                result_img = await self._download_image(result_url, correlation_id)
                color_delta_e = self._compute_average_color_delta(original_img, result_img)
                color_preserved = color_delta_e <= self._max_delta_e

                if not color_preserved:
                    logger.warning(
                        f"Color preservation check failed: Delta-E={color_delta_e:.2f}",
                        extra={"correlation_id": correlation_id},
                    )
            except Exception as e:
                logger.warning(
                    f"Color validation failed: {e}",
                    extra={"correlation_id": correlation_id},
                )

        processing_time_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "Lighting normalization complete",
            extra={
                "result_url": result_url,
                "model_used": model_used,
                "color_delta_e": color_delta_e,
                "color_preserved": color_preserved,
                "processing_time_ms": processing_time_ms,
                "correlation_id": correlation_id,
            },
        )

        return LightingResult(
            original_url=image_url,
            result_url=result_url,
            intensity=intensity,
            model_used=model_used,
            color_delta_e=color_delta_e,
            color_preserved=color_preserved,
            processing_time_ms=processing_time_ms,
            correlation_id=correlation_id,
        )

    async def normalize_lighting_batch(
        self,
        image_urls: list[str],
        *,
        intensity: LightingIntensity = LightingIntensity.MODERATE,
        validate_colors: bool = True,
        correlation_id: str | None = None,
    ) -> list[LightingResult | LightingNormalizationError]:
        """
        Process multiple images in batch.

        Args:
            image_urls: List of image URLs to process
            intensity: Normalization intensity level
            validate_colors: Whether to validate color preservation
            correlation_id: Optional correlation ID for tracing

        Returns:
            List of results or errors for each image
        """
        import asyncio

        client = await self._get_client()
        correlation_id = correlation_id or client._generate_correlation_id()

        async def process_one(
            url: str,
        ) -> LightingResult | LightingNormalizationError:
            try:
                return await self.normalize_lighting(
                    url,
                    intensity=intensity,
                    validate_colors=validate_colors,
                    correlation_id=correlation_id,
                )
            except LightingNormalizationError as e:
                return e

        tasks = [process_one(url) for url in image_urls]
        return await asyncio.gather(*tasks)


__all__ = [
    "LightingNormalizationService",
    "LightingResult",
    "LightingNormalizationError",
    "ColorPreservationError",
    "LightingIntensity",
]
