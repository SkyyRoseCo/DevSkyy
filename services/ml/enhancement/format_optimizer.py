# services/ml/enhancement/format_optimizer.py
"""
Format Optimization Service for DevSkyy.

Generates optimized image variants for all platforms:
- WebP for web (quality 85, < 500KB target)
- JPEG fallback (quality 90)
- Print-ready TIFF (300 DPI)
- Social media variants (Instagram, Pinterest)
- Thumbnails (150x150, 300x300, 600x600)

Author: DevSkyy Platform Team
Version: 1.0.0
"""

from __future__ import annotations

import io
import logging
from enum import StrEnum
from typing import Any

import httpx
from PIL import Image
from pydantic import BaseModel
from services.storage.r2_client import R2Client, R2Config

from core.errors.production_errors import (
    DevSkyError,
    DevSkyErrorCode,
    DevSkyErrorSeverity,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

WEBP_QUALITY = 85
JPEG_QUALITY = 90
WEBP_TARGET_SIZE_KB = 500
PRINT_DPI = 300

THUMBNAIL_SIZES = [
    (150, 150),
    (300, 300),
    (600, 600),
]

SOCIAL_VARIANTS = {
    "instagram_square": (1080, 1080),
    "pinterest": (1000, 1500),
    "facebook_feed": (1200, 630),
    "twitter": (1200, 675),
}


# =============================================================================
# Models
# =============================================================================


class OutputFormat(StrEnum):
    """Supported output formats."""

    WEBP = "webp"
    JPEG = "jpeg"
    PNG = "png"
    TIFF = "tiff"


class ImageVariant(BaseModel):
    """A generated image variant."""

    name: str
    format: OutputFormat
    width: int
    height: int
    size_bytes: int
    url: str
    key: str
    content_type: str
    quality: int | None = None
    dpi: int | None = None


class FormatOptimizationResult(BaseModel):
    """Result of format optimization operation."""

    original_url: str
    original_dimensions: tuple[int, int]
    variants: list[ImageVariant]
    total_size_bytes: int
    processing_time_ms: int
    correlation_id: str

    @property
    def web_variant(self) -> ImageVariant | None:
        """Get WebP web variant."""
        for v in self.variants:
            if v.format == OutputFormat.WEBP and v.name == "web":
                return v
        return None

    @property
    def print_variant(self) -> ImageVariant | None:
        """Get TIFF print variant."""
        for v in self.variants:
            if v.format == OutputFormat.TIFF:
                return v
        return None


class FormatOptimizationError(DevSkyError):
    """Error during format optimization."""

    def __init__(
        self,
        message: str,
        *,
        image_url: str | None = None,
        correlation_id: str | None = None,
        cause: Exception | None = None,
    ) -> None:
        context: dict[str, Any] = {}
        if image_url:
            context["image_url"] = image_url

        super().__init__(
            message,
            code=DevSkyErrorCode.IMAGE_PROCESSING_FAILED,
            severity=DevSkyErrorSeverity.ERROR,
            context=context,
            cause=cause,
            correlation_id=correlation_id,
            retryable=True,
        )


# =============================================================================
# Service
# =============================================================================


class FormatOptimizer:
    """
    Service for generating optimized image variants.

    Generates:
    - WebP for web (quality 85, < 500KB target)
    - JPEG fallback (quality 90)
    - Print-ready TIFF (300 DPI, uncompressed)
    - Social variants: Instagram (1080x1080), Pinterest (1000x1500)
    - Thumbnails: 150x150, 300x300, 600x600

    Features:
    - EXIF preservation for print files, stripped for web
    - Consistent naming convention
    - R2 storage integration

    Usage:
        optimizer = FormatOptimizer(r2_client=r2)
        result = await optimizer.optimize(
            image_url="https://example.com/product.jpg",
            product_id="SKU-123",
        )
        for variant in result.variants:
            print(f"{variant.name}: {variant.url}")
    """

    def __init__(
        self,
        r2_client: R2Client | None = None,
        r2_config: R2Config | None = None,
    ) -> None:
        self._r2_client = r2_client
        self._r2_config = r2_config
        self._owns_client = r2_client is None

    def _get_r2_client(self) -> R2Client:
        """Get or create R2 client."""
        if self._r2_client is None:
            self._r2_client = R2Client(self._r2_config)
        return self._r2_client

    async def _download_image(self, url: str, correlation_id: str) -> Image.Image:
        """Download image from URL."""
        async with httpx.AsyncClient(timeout=60.0) as http_client:
            response = await http_client.get(url)
            if response.status_code != 200:
                raise FormatOptimizationError(
                    f"Failed to download image: HTTP {response.status_code}",
                    image_url=url,
                    correlation_id=correlation_id,
                )
            return Image.open(io.BytesIO(response.content))

    def _resize_image(
        self,
        img: Image.Image,
        target_size: tuple[int, int],
        maintain_aspect: bool = True,
    ) -> Image.Image:
        """
        Resize image to target size.

        Args:
            img: PIL Image
            target_size: (width, height) target
            maintain_aspect: If True, fit within target maintaining aspect ratio

        Returns:
            Resized PIL Image
        """
        if maintain_aspect:
            img.thumbnail(target_size, Image.Resampling.LANCZOS)
            return img
        else:
            return img.resize(target_size, Image.Resampling.LANCZOS)

    def _create_thumbnail(
        self,
        img: Image.Image,
        size: tuple[int, int],
    ) -> Image.Image:
        """Create square thumbnail with center crop."""
        # Make a copy to avoid modifying original
        thumb = img.copy()

        # Calculate crop box for center square
        width, height = thumb.size
        min_dim = min(width, height)
        left = (width - min_dim) // 2
        top = (height - min_dim) // 2
        right = left + min_dim
        bottom = top + min_dim

        # Crop to square and resize
        thumb = thumb.crop((left, top, right, bottom))
        thumb = thumb.resize(size, Image.Resampling.LANCZOS)
        return thumb

    def _convert_to_format(
        self,
        img: Image.Image,
        output_format: OutputFormat,
        quality: int | None = None,
        dpi: int | None = None,
        strip_exif: bool = True,
    ) -> tuple[bytes, str]:
        """
        Convert image to specified format.

        Returns:
            Tuple of (image bytes, content type)
        """
        buffer = io.BytesIO()

        # Ensure RGB for JPEG
        if output_format in (OutputFormat.JPEG, OutputFormat.WEBP):
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

        save_kwargs: dict[str, Any] = {}

        if output_format == OutputFormat.WEBP:
            save_kwargs["format"] = "WEBP"
            save_kwargs["quality"] = quality or WEBP_QUALITY
            content_type = "image/webp"
        elif output_format == OutputFormat.JPEG:
            save_kwargs["format"] = "JPEG"
            save_kwargs["quality"] = quality or JPEG_QUALITY
            content_type = "image/jpeg"
        elif output_format == OutputFormat.PNG:
            save_kwargs["format"] = "PNG"
            content_type = "image/png"
        elif output_format == OutputFormat.TIFF:
            save_kwargs["format"] = "TIFF"
            save_kwargs["compression"] = "none"
            if dpi:
                save_kwargs["dpi"] = (dpi, dpi)
            content_type = "image/tiff"
        else:
            raise ValueError(f"Unsupported format: {output_format}")

        # Strip EXIF if requested
        if strip_exif:
            # Create new image without EXIF
            data = list(img.get_flattened_data())
            clean_img = Image.new(img.mode, img.size)
            clean_img.putdata(data)
            clean_img.save(buffer, **save_kwargs)
        else:
            img.save(buffer, **save_kwargs)

        return buffer.getvalue(), content_type

    def _generate_key(
        self,
        product_id: str,
        variant_name: str,
        extension: str,
    ) -> str:
        """Generate storage key for variant."""
        from datetime import datetime

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"enhanced/{product_id}/{timestamp}_{variant_name}.{extension}"

    async def optimize(
        self,
        image_url: str,
        product_id: str,
        *,
        generate_thumbnails: bool = True,
        generate_social: bool = True,
        generate_print: bool = True,
        correlation_id: str | None = None,
    ) -> FormatOptimizationResult:
        """
        Generate optimized image variants.

        Args:
            image_url: URL of the source image
            product_id: Product SKU for storage organization
            generate_thumbnails: Generate thumbnail sizes
            generate_social: Generate social media variants
            generate_print: Generate print-ready TIFF
            correlation_id: Optional correlation ID for tracing

        Returns:
            FormatOptimizationResult with all generated variants

        Raises:
            FormatOptimizationError: If processing fails
        """
        import time
        import uuid

        start_time = time.time()
        correlation_id = correlation_id or str(uuid.uuid4())
        r2 = self._get_r2_client()

        logger.info(
            "Starting format optimization",
            extra={
                "image_url": image_url,
                "product_id": product_id,
                "correlation_id": correlation_id,
            },
        )

        # Download source image
        try:
            img = await self._download_image(image_url, correlation_id)
        except Exception as e:
            raise FormatOptimizationError(
                f"Failed to download image: {e}",
                image_url=image_url,
                correlation_id=correlation_id,
                cause=e if isinstance(e, Exception) else None,
            ) from e

        original_dims = img.size
        variants: list[ImageVariant] = []
        total_size = 0

        # Generate WebP for web
        try:
            webp_data, webp_ct = self._convert_to_format(
                img, OutputFormat.WEBP, quality=WEBP_QUALITY, strip_exif=True
            )
            key = self._generate_key(product_id, "web", "webp")
            result = r2.upload_bytes(
                webp_data, key, content_type=webp_ct, correlation_id=correlation_id
            )
            variants.append(
                ImageVariant(
                    name="web",
                    format=OutputFormat.WEBP,
                    width=img.size[0],
                    height=img.size[1],
                    size_bytes=len(webp_data),
                    url=result.url,
                    key=key,
                    content_type=webp_ct,
                    quality=WEBP_QUALITY,
                )
            )
            total_size += len(webp_data)
        except Exception as e:
            logger.error(f"Failed to generate WebP: {e}")

        # Generate JPEG fallback
        try:
            jpeg_data, jpeg_ct = self._convert_to_format(
                img, OutputFormat.JPEG, quality=JPEG_QUALITY, strip_exif=True
            )
            key = self._generate_key(product_id, "fallback", "jpg")
            result = r2.upload_bytes(
                jpeg_data, key, content_type=jpeg_ct, correlation_id=correlation_id
            )
            variants.append(
                ImageVariant(
                    name="fallback",
                    format=OutputFormat.JPEG,
                    width=img.size[0],
                    height=img.size[1],
                    size_bytes=len(jpeg_data),
                    url=result.url,
                    key=key,
                    content_type=jpeg_ct,
                    quality=JPEG_QUALITY,
                )
            )
            total_size += len(jpeg_data)
        except Exception as e:
            logger.error(f"Failed to generate JPEG: {e}")

        # Generate print-ready TIFF
        if generate_print:
            try:
                tiff_data, tiff_ct = self._convert_to_format(
                    img, OutputFormat.TIFF, dpi=PRINT_DPI, strip_exif=False
                )
                key = self._generate_key(product_id, "print", "tiff")
                result = r2.upload_bytes(
                    tiff_data, key, content_type=tiff_ct, correlation_id=correlation_id
                )
                variants.append(
                    ImageVariant(
                        name="print",
                        format=OutputFormat.TIFF,
                        width=img.size[0],
                        height=img.size[1],
                        size_bytes=len(tiff_data),
                        url=result.url,
                        key=key,
                        content_type=tiff_ct,
                        dpi=PRINT_DPI,
                    )
                )
                total_size += len(tiff_data)
            except Exception as e:
                logger.error(f"Failed to generate TIFF: {e}")

        # Generate thumbnails
        if generate_thumbnails:
            for size in THUMBNAIL_SIZES:
                try:
                    thumb = self._create_thumbnail(img, size)
                    thumb_data, thumb_ct = self._convert_to_format(
                        thumb, OutputFormat.WEBP, quality=WEBP_QUALITY, strip_exif=True
                    )
                    name = f"thumb_{size[0]}x{size[1]}"
                    key = self._generate_key(product_id, name, "webp")
                    result = r2.upload_bytes(
                        thumb_data, key, content_type=thumb_ct, correlation_id=correlation_id
                    )
                    variants.append(
                        ImageVariant(
                            name=name,
                            format=OutputFormat.WEBP,
                            width=size[0],
                            height=size[1],
                            size_bytes=len(thumb_data),
                            url=result.url,
                            key=key,
                            content_type=thumb_ct,
                            quality=WEBP_QUALITY,
                        )
                    )
                    total_size += len(thumb_data)
                except Exception as e:
                    logger.error(f"Failed to generate thumbnail {size}: {e}")

        # Generate social variants
        if generate_social:
            for variant_name, size in SOCIAL_VARIANTS.items():
                try:
                    social_img = self._resize_image(img.copy(), size, maintain_aspect=False)
                    social_data, social_ct = self._convert_to_format(
                        social_img, OutputFormat.JPEG, quality=JPEG_QUALITY, strip_exif=True
                    )
                    key = self._generate_key(product_id, variant_name, "jpg")
                    result = r2.upload_bytes(
                        social_data, key, content_type=social_ct, correlation_id=correlation_id
                    )
                    variants.append(
                        ImageVariant(
                            name=variant_name,
                            format=OutputFormat.JPEG,
                            width=size[0],
                            height=size[1],
                            size_bytes=len(social_data),
                            url=result.url,
                            key=key,
                            content_type=social_ct,
                            quality=JPEG_QUALITY,
                        )
                    )
                    total_size += len(social_data)
                except Exception as e:
                    logger.error(f"Failed to generate social variant {variant_name}: {e}")

        processing_time_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "Format optimization complete",
            extra={
                "variants_count": len(variants),
                "total_size_bytes": total_size,
                "processing_time_ms": processing_time_ms,
                "correlation_id": correlation_id,
            },
        )

        return FormatOptimizationResult(
            original_url=image_url,
            original_dimensions=original_dims,
            variants=variants,
            total_size_bytes=total_size,
            processing_time_ms=processing_time_ms,
            correlation_id=correlation_id,
        )


__all__ = [
    "FormatOptimizer",
    "FormatOptimizationResult",
    "FormatOptimizationError",
    "ImageVariant",
    "OutputFormat",
]
