#!/usr/bin/env python3
"""
Product Image Enhancement Pipeline for SkyyRose Non-Premier Products
=====================================================================

Production-grade image enhancement pipeline for ~47-53 non-premier products.
Implements 5-stage processing: Background Removal, Upscaling, Color Correction,
Shadow Generation, and Multi-Format Export.

Source Collections:
    - /assets/3d-models/signature/ (27 items)
    - /assets/3d-models/love-hurts/ (24 items)
    - /assets/3d-models/black-rose/ (11 items)

Output Structure:
    /assets/enhanced-images/{collection}/{sku}/
        - {sku}_main.jpg       (1200x1200)
        - {sku}_thumb.jpg      (300x300)
        - {sku}_gallery.jpg    (800x800)
        - {sku}_retina.jpg     (2400x2400)
        - {sku}_transparent.png (with alpha)

Usage:
    # Process test batch (3 images per collection)
    python scripts/enhance_product_images.py --test-batch

    # Process specific collection
    python scripts/enhance_product_images.py --collection signature

    # Process all collections
    python scripts/enhance_product_images.py --all

    # Dry run (analyze only)
    python scripts/enhance_product_images.py --all --dry-run

Author: DevSkyy Platform Team
Version: 1.0.0
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import logging
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, NamedTuple

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# Install dependencies if needed
def ensure_dependencies() -> None:
    """Ensure all required dependencies are installed."""
    required = ["rembg", "Pillow", "numpy"]
    missing = []

    for pkg in required:
        try:
            if pkg == "Pillow":
                __import__("PIL")
            else:
                __import__(pkg)
        except ImportError:
            missing.append(pkg)

    if missing:
        print(f"Installing missing dependencies: {', '.join(missing)}")
        subprocess.run(
            [sys.executable, "-m", "pip", "install"] + missing + ["-q"],
            check=True,
        )


ensure_dependencies()

import numpy as np  # noqa: E402
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageStat  # noqa: E402

try:
    from rembg import new_session, remove

    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False
    print("Warning: rembg not available, background removal will be limited")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# SkyyRose Brand Colors
BRAND_COLORS = {
    "primary": (183, 110, 121),  # #B76E79 - Rose Gold
    "secondary": (26, 26, 26),  # #1A1A1A - Black
    "accent": (212, 175, 55),  # #D4AF37 - Gold
    "neutral": (245, 245, 245),  # #F5F5F5 - Off White
}


class ExportSize(NamedTuple):
    """Export size configuration."""

    name: str
    width: int
    height: int
    suffix: str
    format: str
    quality: int


# Export size configurations
EXPORT_SIZES = [
    ExportSize("main", 1200, 1200, "main", "JPEG", 92),
    ExportSize("thumb", 300, 300, "thumb", "JPEG", 85),
    ExportSize("gallery", 800, 800, "gallery", "JPEG", 90),
    ExportSize("retina", 2400, 2400, "retina", "JPEG", 95),
]


@dataclass
class EnhancementConfig:
    """Configuration for image enhancement pipeline."""

    # Background removal
    bg_removal_model: str = "isnet-general-use"
    bg_removal_fallback: str = "u2net"

    # Upscaling
    target_resolution: int = 2400  # For retina
    upscale_method: str = "lanczos"  # lanczos, bicubic

    # Color correction
    auto_white_balance: bool = True
    auto_exposure: bool = True
    brand_color_matching: bool = True
    brand_primary_color: tuple[int, int, int] = BRAND_COLORS["primary"]
    contrast_factor: float = 1.05
    saturation_factor: float = 1.08
    sharpness_factor: float = 1.15

    # Shadow generation
    add_shadow: bool = True
    shadow_angle: int = 45  # degrees from right
    shadow_distance: int = 15
    shadow_blur: int = 25
    shadow_opacity: float = 0.35
    shadow_color: tuple[int, int, int] = (0, 0, 0)

    # Output
    jpeg_quality: int = 92
    png_compression: int = 6

    @classmethod
    def production(cls) -> EnhancementConfig:
        """Create production-quality configuration."""
        return cls()

    @classmethod
    def fast(cls) -> EnhancementConfig:
        """Create fast configuration for testing."""
        return cls(
            bg_removal_model="u2net",
            target_resolution=1200,
            add_shadow=False,
        )


@dataclass
class EnhancementResult:
    """Result of image enhancement."""

    source_path: Path
    sku: str
    collection: str
    success: bool
    output_paths: dict[str, Path] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    duration_seconds: float = 0.0


class ImageEnhancementPipeline:
    """
    Production-grade image enhancement pipeline for SkyyRose products.

    Pipeline stages:
    1. Background Removal (rembg with isnet-general-use)
    2. AI Upscaling (Lanczos high-quality interpolation)
    3. Color Correction (white balance, exposure, brand matching)
    4. Shadow Generation (soft drop shadow, 45 deg bottom-right)
    5. Format Export (main, thumb, gallery, retina, transparent)
    """

    def __init__(self, config: EnhancementConfig | None = None):
        """Initialize the enhancement pipeline."""
        self.config = config or EnhancementConfig.production()
        self._rembg_session = None

        # Collection mappings
        self.collections = {
            "signature": PROJECT_ROOT / "assets" / "3d-models" / "signature",
            "love-hurts": PROJECT_ROOT / "assets" / "3d-models" / "love-hurts",
            "black-rose": PROJECT_ROOT / "assets" / "3d-models" / "black-rose",
        }

        self.output_base = PROJECT_ROOT / "assets" / "enhanced-images"

    def _get_rembg_session(self) -> Any:
        """Get or create rembg session for background removal."""
        if self._rembg_session is None and REMBG_AVAILABLE:
            try:
                self._rembg_session = new_session(self.config.bg_removal_model)
            except Exception as e:
                logger.warning(f"Failed to create session with {self.config.bg_removal_model}: {e}")
                try:
                    self._rembg_session = new_session(self.config.bg_removal_fallback)
                except Exception as e2:
                    logger.error(f"Failed to create fallback session: {e2}")
        return self._rembg_session

    def _generate_sku(self, image_path: Path, collection: str) -> str:
        """Generate a unique SKU for the product image."""
        # Clean the filename to create a readable SKU
        name = image_path.stem

        # Remove common prefixes
        prefixes_to_remove = [
            "_Signature Collection_",
            "_Love Hurts Collection_",
            "_BLACK Rose Collection_",
            "_The Signature Collection_",
            "PhotoRoom_",
            "Photo ",
            "IMG_",
        ]

        for prefix in prefixes_to_remove:
            if name.startswith(prefix):
                name = name[len(prefix) :]

        # Clean up the name
        name = name.strip("_").strip()
        name = name.replace(" ", "_").replace("-", "_")
        name = "".join(c for c in name if c.isalnum() or c == "_")
        name = "_".join(part for part in name.split("_") if part)

        if not name or name.isdigit():
            # Generate hash-based SKU for unnamed files
            hash_id = hashlib.md5(str(image_path).encode(), usedforsecurity=False).hexdigest()[:8]
            name = f"PROD_{hash_id}"

        # Add collection prefix
        collection_prefix = {
            "signature": "SIG",
            "love-hurts": "LH",
            "black-rose": "BR",
        }.get(collection, "SKY")

        return f"{collection_prefix}_{name[:30]}".upper()

    def find_images(self, collection: str) -> list[Path]:
        """Find all product images in a collection."""
        collection_path = self.collections.get(collection)
        if not collection_path or not collection_path.exists():
            logger.error(f"Collection not found: {collection}")
            return []

        # Image extensions to process
        image_exts = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".bmp"}

        # Patterns to skip (logos, duplicates, non-product files)
        skip_patterns = [
            "logo",
            "skyyrosedad",
            "thumbnail",
            "thumb",
            "_1-001",
            "uuid",
            ".html",
            ".zip",
            ".mov",
            ".mp4",
            ".heic",
        ]

        images = []
        for item in collection_path.rglob("*"):
            if not item.is_file():
                continue
            if item.suffix.lower() not in image_exts:
                continue

            name_lower = item.name.lower()
            if any(skip in name_lower for skip in skip_patterns):
                continue

            images.append(item)

        return sorted(images, key=lambda p: p.name)

    # =========================================================================
    # Stage 1: Background Removal
    # =========================================================================

    def remove_background(self, image: Image.Image) -> Image.Image:
        """
        Remove background from product image using AI.

        Uses rembg with isnet-general-use model for high-quality
        product isolation.
        """
        if not REMBG_AVAILABLE:
            logger.warning("rembg not available, returning original image")
            return image.convert("RGBA")

        try:
            session = self._get_rembg_session()
            result = remove(image, session=session)
            return result
        except Exception as e:
            logger.error(f"Background removal failed: {e}")
            return image.convert("RGBA")

    # =========================================================================
    # Stage 2: AI Upscaling
    # =========================================================================

    def upscale_image(self, image: Image.Image, target_size: int) -> Image.Image:
        """
        Upscale image to target resolution using high-quality interpolation.

        Uses Lanczos resampling for best quality when Real-ESRGAN
        is not available.
        """
        width, height = image.size
        min_dim = min(width, height)

        if min_dim >= target_size:
            return image

        # Calculate scale factor
        scale = target_size / min_dim
        new_width = int(width * scale)
        new_height = int(height * scale)

        # Use LANCZOS for best quality
        resampling = Image.Resampling.LANCZOS
        return image.resize((new_width, new_height), resampling)

    # =========================================================================
    # Stage 3: Color Correction
    # =========================================================================

    def apply_auto_white_balance(self, image: Image.Image) -> Image.Image:
        """Apply automatic white balance correction."""
        if image.mode == "RGBA":
            r, g, b, a = image.split()
            rgb = Image.merge("RGB", (r, g, b))
        else:
            rgb = image.convert("RGB")
            a = None

        # Calculate channel means
        np_img = np.array(rgb, dtype=np.float32)
        avg_r = np.mean(np_img[:, :, 0])
        avg_g = np.mean(np_img[:, :, 1])
        avg_b = np.mean(np_img[:, :, 2])

        # Calculate gray world correction factors
        avg = (avg_r + avg_g + avg_b) / 3
        if avg_r > 0 and avg_g > 0 and avg_b > 0:
            scale_r = avg / avg_r
            scale_g = avg / avg_g
            scale_b = avg / avg_b

            # Apply corrections (clamped)
            np_img[:, :, 0] = np.clip(np_img[:, :, 0] * scale_r, 0, 255)
            np_img[:, :, 1] = np.clip(np_img[:, :, 1] * scale_g, 0, 255)
            np_img[:, :, 2] = np.clip(np_img[:, :, 2] * scale_b, 0, 255)

        rgb = Image.fromarray(np_img.astype(np.uint8), "RGB")

        if a is not None:
            r, g, b = rgb.split()
            return Image.merge("RGBA", (r, g, b, a))
        return rgb

    def apply_auto_exposure(self, image: Image.Image) -> Image.Image:
        """Apply automatic exposure correction."""
        if image.mode == "RGBA":
            r, g, b, a = image.split()
            rgb = Image.merge("RGB", (r, g, b))
        else:
            rgb = image.convert("RGB")
            a = None

        # Get current brightness
        stat = ImageStat.Stat(rgb)
        current_brightness = sum(stat.mean) / 3

        # Target brightness (mid-tone)
        target_brightness = 128

        # Calculate adjustment factor
        if current_brightness > 0:
            factor = target_brightness / current_brightness
            # Limit adjustment range
            factor = max(0.7, min(1.5, factor))
        else:
            factor = 1.0

        if abs(factor - 1.0) > 0.05:
            rgb = ImageEnhance.Brightness(rgb).enhance(factor)

        if a is not None:
            r, g, b = rgb.split()
            return Image.merge("RGBA", (r, g, b, a))
        return rgb

    def apply_brand_color_matching(self, image: Image.Image) -> Image.Image:
        """
        Subtly warm the image toward the brand's rose gold color.

        This adds a subtle brand tint without overwhelming the product colors.
        """
        if image.mode == "RGBA":
            r, g, b, a = image.split()
            rgb = Image.merge("RGB", (r, g, b))
        else:
            rgb = image.convert("RGB")
            a = None

        # Create rose gold overlay
        rose_gold = Image.new("RGB", rgb.size, self.config.brand_primary_color)

        # Very subtle blend (5% tint)
        blend_factor = 0.03
        np_img = np.array(rgb, dtype=np.float32)
        np_rose = np.array(rose_gold, dtype=np.float32)

        blended = np_img * (1 - blend_factor) + np_rose * blend_factor
        rgb = Image.fromarray(blended.astype(np.uint8), "RGB")

        if a is not None:
            r, g, b = rgb.split()
            return Image.merge("RGBA", (r, g, b, a))
        return rgb

    def apply_enhancements(self, image: Image.Image) -> Image.Image:
        """Apply contrast, saturation, and sharpness enhancements."""
        if image.mode == "RGBA":
            r, g, b, a = image.split()
            rgb = Image.merge("RGB", (r, g, b))
        else:
            rgb = image.convert("RGB")
            a = None

        # Contrast
        if self.config.contrast_factor != 1.0:
            rgb = ImageEnhance.Contrast(rgb).enhance(self.config.contrast_factor)

        # Saturation
        if self.config.saturation_factor != 1.0:
            rgb = ImageEnhance.Color(rgb).enhance(self.config.saturation_factor)

        # Sharpness (using UnsharpMask for better quality)
        rgb = rgb.filter(ImageFilter.UnsharpMask(radius=1.5, percent=50, threshold=3))

        if a is not None:
            r, g, b = rgb.split()
            return Image.merge("RGBA", (r, g, b, a))
        return rgb

    def color_correct(self, image: Image.Image) -> Image.Image:
        """Apply full color correction pipeline."""
        if self.config.auto_white_balance:
            image = self.apply_auto_white_balance(image)

        if self.config.auto_exposure:
            image = self.apply_auto_exposure(image)

        if self.config.brand_color_matching:
            image = self.apply_brand_color_matching(image)

        image = self.apply_enhancements(image)

        return image

    # =========================================================================
    # Stage 4: Shadow Generation
    # =========================================================================

    def add_drop_shadow(self, image: Image.Image) -> Image.Image:
        """
        Add a soft drop shadow to the product image.

        Creates a realistic shadow at 45 degrees bottom-right.
        """
        if not self.config.add_shadow:
            return image

        if image.mode != "RGBA":
            image = image.convert("RGBA")

        # Get alpha channel for shadow shape
        alpha = image.split()[3]

        # Calculate shadow offset (45 degrees = equal x and y offset)
        import math

        angle_rad = math.radians(self.config.shadow_angle)
        offset_x = int(self.config.shadow_distance * math.cos(angle_rad))
        offset_y = int(self.config.shadow_distance * math.sin(angle_rad))

        # Create shadow layer
        shadow_color_with_alpha = self.config.shadow_color + (
            int(255 * self.config.shadow_opacity),
        )

        # Create larger canvas for shadow
        padding = self.config.shadow_blur * 2 + abs(offset_x) + abs(offset_y)
        new_width = image.width + padding * 2
        new_height = image.height + padding * 2

        # Shadow image
        shadow = Image.new("RGBA", (new_width, new_height), (0, 0, 0, 0))

        # Create shadow from alpha
        shadow_alpha = Image.new("L", alpha.size, 0)
        shadow_alpha.paste(alpha, (0, 0))

        # Create shadow color layer
        shadow_layer = Image.new("RGBA", alpha.size, shadow_color_with_alpha)
        shadow_layer.putalpha(ImageOps.invert(shadow_alpha))
        shadow_layer.putalpha(alpha)

        # Paste shadow with offset
        shadow.paste(shadow_layer, (padding + offset_x, padding + offset_y))

        # Apply Gaussian blur to shadow
        shadow = shadow.filter(ImageFilter.GaussianBlur(self.config.shadow_blur))

        # Create final composite
        result = Image.new("RGBA", (new_width, new_height), (255, 255, 255, 255))
        result.paste(shadow, (0, 0), shadow)
        result.paste(image, (padding, padding), image)

        # Crop to fit content with minimal padding
        bbox = result.getbbox()
        if bbox:
            # Add small padding
            pad = 20
            bbox = (
                max(0, bbox[0] - pad),
                max(0, bbox[1] - pad),
                min(result.width, bbox[2] + pad),
                min(result.height, bbox[3] + pad),
            )
            result = result.crop(bbox)

        return result

    # =========================================================================
    # Stage 5: Format Export
    # =========================================================================

    def resize_for_export(
        self,
        image: Image.Image,
        width: int,
        height: int,
        maintain_aspect: bool = True,
    ) -> Image.Image:
        """Resize image for export, centering on canvas."""
        if maintain_aspect:
            # Calculate size that fits within bounds
            img_ratio = image.width / image.height
            target_ratio = width / height

            if img_ratio > target_ratio:
                new_width = width
                new_height = int(width / img_ratio)
            else:
                new_height = height
                new_width = int(height * img_ratio)

            resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Center on canvas
            canvas = Image.new("RGBA", (width, height), (255, 255, 255, 255))
            x = (width - new_width) // 2
            y = (height - new_height) // 2
            canvas.paste(resized, (x, y), resized if resized.mode == "RGBA" else None)
            return canvas
        else:
            return image.resize((width, height), Image.Resampling.LANCZOS)

    def export_formats(
        self,
        image_with_shadow: Image.Image,
        transparent_image: Image.Image,
        output_dir: Path,
        sku: str,
    ) -> dict[str, Path]:
        """Export image in all required formats."""
        output_dir.mkdir(parents=True, exist_ok=True)
        output_paths = {}

        # Export sized JPEGs (with shadow, white background)
        for size in EXPORT_SIZES:
            resized = self.resize_for_export(image_with_shadow, size.width, size.height)

            # Convert to RGB for JPEG
            if resized.mode == "RGBA":
                background = Image.new("RGB", resized.size, (255, 255, 255))
                background.paste(resized, mask=resized.split()[3])
                resized = background

            output_path = output_dir / f"{sku}_{size.suffix}.jpg"
            resized.save(output_path, "JPEG", quality=size.quality, optimize=True)
            output_paths[size.name] = output_path
            logger.debug(f"  Exported {size.name}: {output_path}")

        # Export transparent PNG
        png_path = output_dir / f"{sku}_transparent.png"
        transparent_image.save(png_path, "PNG", compress_level=self.config.png_compression)
        output_paths["transparent"] = png_path
        logger.debug(f"  Exported transparent: {png_path}")

        return output_paths

    # =========================================================================
    # Main Enhancement Pipeline
    # =========================================================================

    async def enhance_image(
        self,
        image_path: Path,
        collection: str,
    ) -> EnhancementResult:
        """
        Run the full enhancement pipeline on a single image.

        Pipeline:
        1. Background Removal
        2. Upscaling
        3. Color Correction
        4. Shadow Generation
        5. Format Export
        """
        start_time = time.time()
        sku = self._generate_sku(image_path, collection)
        output_dir = self.output_base / collection / sku

        result = EnhancementResult(
            source_path=image_path,
            sku=sku,
            collection=collection,
            success=False,
        )

        try:
            logger.info(f"Processing: {image_path.name} -> {sku}")

            # Load image
            image = Image.open(image_path)
            original_size = image.size
            result.metrics["original_size"] = f"{original_size[0]}x{original_size[1]}"

            # Stage 1: Background Removal
            logger.debug("  Stage 1: Background removal")
            transparent = self.remove_background(image)

            # Stage 2: Upscaling
            logger.debug("  Stage 2: Upscaling")
            transparent = self.upscale_image(transparent, self.config.target_resolution)
            result.metrics["upscaled_size"] = f"{transparent.width}x{transparent.height}"

            # Stage 3: Color Correction
            logger.debug("  Stage 3: Color correction")
            transparent = self.color_correct(transparent)

            # Store transparent version before shadow
            transparent_clean = transparent.copy()

            # Stage 4: Shadow Generation
            logger.debug("  Stage 4: Shadow generation")
            with_shadow = self.add_drop_shadow(transparent)

            # Stage 5: Format Export
            logger.debug("  Stage 5: Format export")
            output_paths = self.export_formats(
                with_shadow,
                transparent_clean,
                output_dir,
                sku,
            )

            result.output_paths = output_paths
            result.success = True
            result.metrics["exports"] = len(output_paths)

            logger.info(f"  Success: {len(output_paths)} files exported to {output_dir}")

        except Exception as e:
            logger.error(f"  Failed: {e}")
            result.errors.append(str(e))

        result.duration_seconds = time.time() - start_time
        return result

    async def enhance_collection(
        self,
        collection: str,
        limit: int = 0,
        dry_run: bool = False,
    ) -> list[EnhancementResult]:
        """Enhance all images in a collection."""
        images = self.find_images(collection)

        if limit > 0:
            images = images[:limit]

        logger.info(f"\n{'=' * 60}")
        logger.info(f"COLLECTION: {collection.upper()}")
        logger.info(f"{'=' * 60}")
        logger.info(f"Found {len(images)} images to process")

        if dry_run:
            logger.info("\n[DRY RUN] Would process:")
            for img in images:
                sku = self._generate_sku(img, collection)
                logger.info(f"  - {img.name} -> {sku}")
            return []

        results = []
        for i, image_path in enumerate(images, 1):
            logger.info(f"\n[{i}/{len(images)}] {image_path.name}")
            result = await self.enhance_image(image_path, collection)
            results.append(result)

        # Summary
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        logger.info(f"\nCollection complete: {successful} successful, {failed} failed")

        return results

    async def enhance_all(
        self,
        limit_per_collection: int = 0,
        dry_run: bool = False,
    ) -> dict[str, list[EnhancementResult]]:
        """Enhance all collections."""
        all_results = {}

        for collection in self.collections:
            results = await self.enhance_collection(
                collection,
                limit=limit_per_collection,
                dry_run=dry_run,
            )
            all_results[collection] = results

        # Final summary
        if not dry_run:
            logger.info("\n" + "=" * 60)
            logger.info("FINAL SUMMARY")
            logger.info("=" * 60)

            total_success = 0
            total_failed = 0

            for collection, results in all_results.items():
                success = sum(1 for r in results if r.success)
                failed = len(results) - success
                total_success += success
                total_failed += failed
                logger.info(f"  {collection}: {success} success, {failed} failed")

            logger.info(f"\nTotal: {total_success} successful, {total_failed} failed")
            logger.info(f"Output: {self.output_base}")

        return all_results

    def save_manifest(self, results: dict[str, list[EnhancementResult]]) -> Path:
        """Save enhancement manifest JSON."""
        manifest_path = self.output_base / "ENHANCEMENT_MANIFEST.json"

        manifest = {
            "timestamp": datetime.now().isoformat(),
            "config": {
                "bg_removal_model": self.config.bg_removal_model,
                "target_resolution": self.config.target_resolution,
                "brand_color": f"#{self.config.brand_primary_color[0]:02x}{self.config.brand_primary_color[1]:02x}{self.config.brand_primary_color[2]:02x}",
            },
            "collections": {},
            "summary": {
                "total_processed": 0,
                "total_successful": 0,
                "total_failed": 0,
            },
        }

        for collection, coll_results in results.items():
            manifest["collections"][collection] = {
                "total": len(coll_results),
                "successful": sum(1 for r in coll_results if r.success),
                "failed": sum(1 for r in coll_results if not r.success),
                "items": [
                    {
                        "sku": r.sku,
                        "source": str(r.source_path.name),
                        "success": r.success,
                        "outputs": {k: str(v.name) for k, v in r.output_paths.items()},
                        "duration_seconds": round(r.duration_seconds, 2),
                        "errors": r.errors,
                    }
                    for r in coll_results
                ],
            }
            manifest["summary"]["total_processed"] += len(coll_results)
            manifest["summary"]["total_successful"] += sum(1 for r in coll_results if r.success)
            manifest["summary"]["total_failed"] += sum(1 for r in coll_results if not r.success)

        self.output_base.mkdir(parents=True, exist_ok=True)
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        logger.info(f"\nManifest saved: {manifest_path}")
        return manifest_path


def print_banner() -> None:
    """Print CLI banner."""
    banner = """
================================================================================
                   SKYYROSE PRODUCT IMAGE ENHANCEMENT PIPELINE

================================================================================

Pipeline Stages:
  1. Background Removal    (rembg isnet-general-use)
  2. AI Upscaling         (Lanczos high-quality)
  3. Color Correction     (white balance, exposure, brand matching #B76E79)
  4. Shadow Generation    (soft drop shadow, 45 deg bottom-right)
  5. Format Export        (main 1200, thumb 300, gallery 800, retina 2400)

================================================================================
"""
    print(banner)


async def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Product Image Enhancement Pipeline for SkyyRose",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--collection",
        choices=["signature", "love-hurts", "black-rose"],
        help="Process specific collection",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all collections",
    )
    parser.add_argument(
        "--test-batch",
        action="store_true",
        help="Process test batch (3 images per collection)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit images per collection",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview only (no processing)",
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Use fast configuration (lower quality)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    print_banner()

    # Create pipeline with appropriate config
    config = EnhancementConfig.fast() if args.fast else EnhancementConfig.production()
    pipeline = ImageEnhancementPipeline(config)

    if args.test_batch:
        # Process 3 images per collection
        logger.info("Running test batch: 3 images per collection")
        results = await pipeline.enhance_all(limit_per_collection=3, dry_run=args.dry_run)
        if not args.dry_run:
            pipeline.save_manifest(results)
        return 0

    elif args.all:
        # Process all collections
        results = await pipeline.enhance_all(
            limit_per_collection=args.limit,
            dry_run=args.dry_run,
        )
        if not args.dry_run:
            pipeline.save_manifest(results)
        return 0

    elif args.collection:
        # Process specific collection
        results = await pipeline.enhance_collection(
            args.collection,
            limit=args.limit,
            dry_run=args.dry_run,
        )
        if not args.dry_run:
            pipeline.save_manifest({args.collection: results})
        return 0

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
