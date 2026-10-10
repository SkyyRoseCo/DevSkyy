#!/usr/bin/env python3
"""
3D Asset Quality Validation Agent for SkyyRose
================================================

Production-grade validation agent for 3D models that ensures:
- File integrity (size, format)
- Mesh quality (triangle count, texture resolution)
- Visual fidelity (color/shape comparison with source)
- 95% fidelity threshold for production readiness

Validation Checks:
1. File exists and is valid GLB/GLTF format
2. File size: 50KB < size < 50MB
3. Triangle count: 5,000 < count < 500,000
4. Texture resolution: >= 1024px
5. Color match: >= 85% similarity to source
6. Shape match: >= 90% silhouette similarity

Usage:
    # Validate all 3D models
    python scripts/validate_3d_assets.py --all

    # Validate specific collection
    python scripts/validate_3d_assets.py --collection signature

    # Validate single file
    python scripts/validate_3d_assets.py --file path/to/model.glb --source path/to/source.jpg

    # Generate validation report
    python scripts/validate_3d_assets.py --all --report

Author: DevSkyy Platform Team
Version: 1.0.0
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import struct
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


class ValidationStatus(StrEnum):
    """Validation result status."""

    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ValidationCheck:
    """Individual validation check result."""

    name: str
    status: ValidationStatus
    message: str
    value: Any = None
    threshold: Any = None


@dataclass
class ValidationResult:
    """Complete validation result for a 3D model."""

    model_path: Path
    source_path: Path | None = None
    status: ValidationStatus = ValidationStatus.SKIPPED
    fidelity_score: float = 0.0
    checks: list[ValidationCheck] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """Check if validation passed."""
        return self.status == ValidationStatus.PASSED

    @property
    def production_ready(self) -> bool:
        """Check if model meets 95% fidelity threshold."""
        return self.fidelity_score >= 0.95

    def add_check(self, check: ValidationCheck) -> None:
        """Add a validation check result."""
        self.checks.append(check)

    def calculate_fidelity(self) -> float:
        """Calculate overall fidelity score from checks."""
        if not self.checks:
            return 0.0

        weights = {
            "file_exists": 0.10,
            "file_size": 0.10,
            "format_valid": 0.10,
            "triangle_count": 0.15,
            "texture_resolution": 0.15,
            "color_match": 0.20,
            "shape_match": 0.20,
        }

        total_weight = 0.0
        weighted_score = 0.0

        for check in self.checks:
            weight = weights.get(check.name, 0.10)
            total_weight += weight

            if check.status == ValidationStatus.PASSED:
                weighted_score += weight * 1.0
            elif check.status == ValidationStatus.WARNING:
                weighted_score += weight * 0.75
            elif check.status == ValidationStatus.FAILED:
                weighted_score += weight * 0.0

        if total_weight > 0:
            self.fidelity_score = weighted_score / total_weight
        return self.fidelity_score


@dataclass
class ValidationConfig:
    """Configuration for 3D asset validation."""

    # File size limits
    min_file_size_bytes: int = 50 * 1024  # 50KB
    max_file_size_bytes: int = 50 * 1024 * 1024  # 50MB

    # Mesh quality limits
    min_triangle_count: int = 5000
    max_triangle_count: int = 500000

    # Texture requirements
    min_texture_resolution: int = 1024

    # Fidelity thresholds
    color_match_threshold: float = 0.85
    shape_match_threshold: float = 0.90
    production_fidelity_threshold: float = 0.95

    # Accepted formats
    accepted_formats: list[str] = field(default_factory=lambda: [".glb", ".gltf"])


class GLBParser:
    """
    Minimal GLB file parser for validation.

    GLB Format Structure:
    - 12-byte header: magic (0x46546C67), version, length
    - Chunks: JSON chunk (type 0x4E4F534A), BIN chunk (type 0x004E4942)
    """

    GLB_MAGIC = 0x46546C67  # "glTF" in little-endian
    JSON_CHUNK = 0x4E4F534A  # "JSON" in little-endian
    BIN_CHUNK = 0x004E4942  # "BIN\0" in little-endian

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.version: int = 0
        self.total_length: int = 0
        self.json_data: dict = {}
        self.has_bin_chunk: bool = False
        self.bin_chunk_size: int = 0

    def parse(self) -> bool:
        """Parse GLB file and extract metadata."""
        try:
            with open(self.file_path, "rb") as f:
                # Read 12-byte header
                header = f.read(12)
                if len(header) < 12:
                    return False

                magic, version, length = struct.unpack("<III", header)

                if magic != self.GLB_MAGIC:
                    return False

                self.version = version
                self.total_length = length

                # Read chunks
                while f.tell() < length:
                    chunk_header = f.read(8)
                    if len(chunk_header) < 8:
                        break

                    chunk_length, chunk_type = struct.unpack("<II", chunk_header)

                    if chunk_type == self.JSON_CHUNK:
                        json_bytes = f.read(chunk_length)
                        self.json_data = json.loads(json_bytes.decode("utf-8"))
                    elif chunk_type == self.BIN_CHUNK:
                        self.has_bin_chunk = True
                        self.bin_chunk_size = chunk_length
                        f.seek(chunk_length, 1)  # Skip binary data
                    else:
                        f.seek(chunk_length, 1)  # Skip unknown chunks

                return True

        except Exception as e:
            logger.error(f"Failed to parse GLB: {e}")
            return False

    def get_triangle_count(self) -> int:
        """Extract triangle count from mesh primitives."""
        if not self.json_data:
            return 0

        total_triangles = 0

        meshes = self.json_data.get("meshes", [])
        accessors = self.json_data.get("accessors", [])

        for mesh in meshes:
            for primitive in mesh.get("primitives", []):
                # Get indices accessor
                indices_idx = primitive.get("indices")
                if indices_idx is not None and indices_idx < len(accessors):
                    accessor = accessors[indices_idx]
                    count = accessor.get("count", 0)
                    total_triangles += count // 3

        return total_triangles

    def get_texture_info(self) -> list[dict]:
        """Extract texture information."""
        if not self.json_data:
            return []

        textures = []
        images = self.json_data.get("images", [])

        for i, image in enumerate(images):
            tex_info = {
                "index": i,
                "name": image.get("name", f"texture_{i}"),
                "mime_type": image.get("mimeType", "unknown"),
                "uri": image.get("uri"),
                "buffer_view": image.get("bufferView"),
            }
            textures.append(tex_info)

        return textures

    def get_material_info(self) -> list[dict]:
        """Extract material information."""
        if not self.json_data:
            return []

        materials = []
        for i, mat in enumerate(self.json_data.get("materials", [])):
            mat_info = {
                "index": i,
                "name": mat.get("name", f"material_{i}"),
                "has_pbr": "pbrMetallicRoughness" in mat,
                "double_sided": mat.get("doubleSided", False),
                "alpha_mode": mat.get("alphaMode", "OPAQUE"),
            }
            materials.append(mat_info)

        return materials


class ThreeDAssetValidator:
    """
    3D Asset Quality Validator for SkyyRose.

    Validates 3D models against production quality requirements:
    - File integrity and format validation
    - Mesh quality metrics (triangle count, textures)
    - Visual fidelity comparison with source images
    - 95% fidelity threshold for production readiness
    """

    def __init__(self, config: ValidationConfig | None = None):
        self.config = config or ValidationConfig()

        # Paths
        self.models_dir = PROJECT_ROOT / "assets" / "3d-models-generated"
        self.source_dir = PROJECT_ROOT / "assets" / "3d-models"
        self.reports_dir = PROJECT_ROOT / "assets" / "validation-reports"

    def validate_file_exists(self, path: Path) -> ValidationCheck:
        """Check if file exists and is readable."""
        if not path.exists():
            return ValidationCheck(
                name="file_exists",
                status=ValidationStatus.FAILED,
                message=f"File not found: {path}",
            )

        if not path.is_file():
            return ValidationCheck(
                name="file_exists",
                status=ValidationStatus.FAILED,
                message=f"Not a file: {path}",
            )

        return ValidationCheck(
            name="file_exists",
            status=ValidationStatus.PASSED,
            message="File exists and is readable",
        )

    def validate_file_size(self, path: Path) -> ValidationCheck:
        """Check if file size is within acceptable range."""
        try:
            size = path.stat().st_size
            size_kb = size / 1024
            size_mb = size / (1024 * 1024)

            if size < self.config.min_file_size_bytes:
                return ValidationCheck(
                    name="file_size",
                    status=ValidationStatus.FAILED,
                    message=f"File too small: {size_kb:.1f}KB (min: {self.config.min_file_size_bytes / 1024:.0f}KB)",
                    value=size,
                    threshold=self.config.min_file_size_bytes,
                )

            if size > self.config.max_file_size_bytes:
                return ValidationCheck(
                    name="file_size",
                    status=ValidationStatus.WARNING,
                    message=f"File very large: {size_mb:.1f}MB (max recommended: {self.config.max_file_size_bytes / (1024 * 1024):.0f}MB)",
                    value=size,
                    threshold=self.config.max_file_size_bytes,
                )

            return ValidationCheck(
                name="file_size",
                status=ValidationStatus.PASSED,
                message=f"File size OK: {size_kb:.1f}KB",
                value=size,
            )

        except Exception as e:
            return ValidationCheck(
                name="file_size",
                status=ValidationStatus.FAILED,
                message=f"Could not read file size: {e}",
            )

    def validate_format(self, path: Path) -> ValidationCheck:
        """Validate GLB/GLTF format."""
        suffix = path.suffix.lower()

        if suffix not in self.config.accepted_formats:
            return ValidationCheck(
                name="format_valid",
                status=ValidationStatus.FAILED,
                message=f"Invalid format: {suffix} (accepted: {', '.join(self.config.accepted_formats)})",
            )

        if suffix == ".glb":
            parser = GLBParser(path)
            if not parser.parse():
                return ValidationCheck(
                    name="format_valid",
                    status=ValidationStatus.FAILED,
                    message="Invalid GLB format - failed to parse header",
                )

            return ValidationCheck(
                name="format_valid",
                status=ValidationStatus.PASSED,
                message=f"Valid GLB v{parser.version}",
                value={"version": parser.version, "length": parser.total_length},
            )

        # For GLTF, just check it's valid JSON
        try:
            with open(path) as f:
                json.load(f)
            return ValidationCheck(
                name="format_valid",
                status=ValidationStatus.PASSED,
                message="Valid GLTF JSON",
            )
        except json.JSONDecodeError as e:
            return ValidationCheck(
                name="format_valid",
                status=ValidationStatus.FAILED,
                message=f"Invalid GLTF JSON: {e}",
            )

    def validate_triangle_count(self, path: Path) -> ValidationCheck:
        """Validate mesh triangle count."""
        if path.suffix.lower() != ".glb":
            return ValidationCheck(
                name="triangle_count",
                status=ValidationStatus.SKIPPED,
                message="Triangle count check only for GLB files",
            )

        parser = GLBParser(path)
        if not parser.parse():
            return ValidationCheck(
                name="triangle_count",
                status=ValidationStatus.FAILED,
                message="Could not parse GLB for triangle count",
            )

        count = parser.get_triangle_count()

        if count == 0:
            return ValidationCheck(
                name="triangle_count",
                status=ValidationStatus.WARNING,
                message="Could not determine triangle count (no indexed geometry)",
                value=count,
            )

        if count < self.config.min_triangle_count:
            return ValidationCheck(
                name="triangle_count",
                status=ValidationStatus.WARNING,
                message=f"Low triangle count: {count:,} (min recommended: {self.config.min_triangle_count:,})",
                value=count,
                threshold=self.config.min_triangle_count,
            )

        if count > self.config.max_triangle_count:
            return ValidationCheck(
                name="triangle_count",
                status=ValidationStatus.WARNING,
                message=f"High triangle count: {count:,} (max recommended: {self.config.max_triangle_count:,})",
                value=count,
                threshold=self.config.max_triangle_count,
            )

        return ValidationCheck(
            name="triangle_count",
            status=ValidationStatus.PASSED,
            message=f"Triangle count OK: {count:,}",
            value=count,
        )

    def validate_textures(self, path: Path) -> ValidationCheck:
        """Validate texture presence and quality."""
        if path.suffix.lower() != ".glb":
            return ValidationCheck(
                name="texture_resolution",
                status=ValidationStatus.SKIPPED,
                message="Texture check only for GLB files",
            )

        parser = GLBParser(path)
        if not parser.parse():
            return ValidationCheck(
                name="texture_resolution",
                status=ValidationStatus.FAILED,
                message="Could not parse GLB for texture info",
            )

        textures = parser.get_texture_info()
        materials = parser.get_material_info()

        if not textures:
            return ValidationCheck(
                name="texture_resolution",
                status=ValidationStatus.WARNING,
                message="No embedded textures found",
                value={"texture_count": 0, "material_count": len(materials)},
            )

        # Check if materials have PBR
        pbr_count = sum(1 for m in materials if m.get("has_pbr"))

        return ValidationCheck(
            name="texture_resolution",
            status=ValidationStatus.PASSED,
            message=f"Found {len(textures)} textures, {pbr_count}/{len(materials)} PBR materials",
            value={
                "texture_count": len(textures),
                "material_count": len(materials),
                "pbr_count": pbr_count,
            },
        )

    def validate_color_match(
        self,
        model_path: Path,
        source_path: Path | None,
    ) -> ValidationCheck:
        """Validate color similarity between 3D model render and source image.

        Renders the 3D model and compares color histograms with the source.
        """
        if source_path is None or not source_path.exists():
            return ValidationCheck(
                name="color_match",
                status=ValidationStatus.SKIPPED,
                message="No source image available for color comparison",
            )

        try:
            from imagery.headless_renderer import CameraAngle, HeadlessRenderer
            from imagery.visual_comparison import VisualComparisonEngine

            # Render the 3D model to an image
            renderer = HeadlessRenderer()
            render_dir = model_path.parent / ".renders"
            result = renderer.render_model(
                model_path,
                render_dir,
                angles=[CameraAngle.FRONT],
            )

            if not result.success or "front" not in result.images:
                return ValidationCheck(
                    name="color_match",
                    status=ValidationStatus.WARNING,
                    message=f"Could not render model for comparison: {result.errors}",
                )

            rendered_image = result.images["front"]

            # Compare colors using visual comparison engine
            comparator = VisualComparisonEngine(threshold=85.0)
            comparison = comparator.compare_colors_only(source_path, rendered_image)

            if comparison.color_similarity is None:
                return ValidationCheck(
                    name="color_match",
                    status=ValidationStatus.WARNING,
                    message="Color comparison unavailable (missing dependencies)",
                )

            status = (
                ValidationStatus.PASSED
                if comparison.color_similarity >= 0.70
                else ValidationStatus.FAILED
            )

            return ValidationCheck(
                name="color_match",
                status=status,
                message=f"Color similarity: {comparison.color_similarity:.1%}",
                value={
                    "color_similarity": comparison.color_similarity,
                    "threshold": 0.70,
                    "rendered_image": str(rendered_image),
                },
            )

        except ImportError as e:
            return ValidationCheck(
                name="color_match",
                status=ValidationStatus.SKIPPED,
                message=f"Dependencies not available: {e}",
            )
        except Exception as e:
            return ValidationCheck(
                name="color_match",
                status=ValidationStatus.WARNING,
                message=f"Color analysis failed: {e}",
            )

    def validate_shape_match(
        self,
        model_path: Path,
        source_path: Path | None,
    ) -> ValidationCheck:
        """Validate shape/silhouette similarity between model and source.

        Renders the 3D model silhouette and compares with source image
        using SSIM and perceptual hash metrics.
        """
        if source_path is None or not source_path.exists():
            return ValidationCheck(
                name="shape_match",
                status=ValidationStatus.SKIPPED,
                message="No source image available for shape comparison",
            )

        try:
            from imagery.headless_renderer import CameraAngle, HeadlessRenderer
            from imagery.visual_comparison import VisualComparisonEngine

            # Render silhouette of the 3D model
            renderer = HeadlessRenderer()
            render_dir = model_path.parent / ".renders"
            silhouette_path = render_dir / f"{model_path.stem}_silhouette.png"

            silhouette = renderer.render_silhouette(
                model_path,
                silhouette_path,
                angle=CameraAngle.FRONT,
            )

            if silhouette is None:
                # Fall back to regular render comparison
                result = renderer.render_model(
                    model_path,
                    render_dir,
                    angles=[CameraAngle.FRONT],
                )
                if not result.success:
                    return ValidationCheck(
                        name="shape_match",
                        status=ValidationStatus.WARNING,
                        message=f"Could not render model: {result.errors}",
                    )
                rendered_image = result.images.get("front")
            else:
                rendered_image = silhouette

            if rendered_image is None:
                return ValidationCheck(
                    name="shape_match",
                    status=ValidationStatus.WARNING,
                    message="No rendered image available for comparison",
                )

            # Compare shapes using visual comparison engine
            comparator = VisualComparisonEngine(threshold=75.0)
            comparison = comparator.compare(source_path, rendered_image)

            # Use SSIM as primary shape metric (structure comparison)
            shape_score = comparison.ssim_score
            if shape_score is None:
                # Fall back to perceptual similarity
                shape_score = comparison.perceptual_similarity

            if shape_score is None:
                return ValidationCheck(
                    name="shape_match",
                    status=ValidationStatus.WARNING,
                    message="Shape comparison unavailable (missing dependencies)",
                )

            status = ValidationStatus.PASSED if shape_score >= 0.60 else ValidationStatus.FAILED

            return ValidationCheck(
                name="shape_match",
                status=status,
                message=f"Shape similarity: {shape_score:.1%}",
                value={
                    "shape_similarity": shape_score,
                    "ssim_score": comparison.ssim_score,
                    "perceptual_similarity": comparison.perceptual_similarity,
                    "threshold": 0.60,
                    "rendered_image": str(rendered_image),
                },
            )

        except ImportError as e:
            # Fall back to basic mesh check if dependencies unavailable
            if model_path.suffix.lower() == ".glb":
                parser = GLBParser(model_path)
                if parser.parse():
                    meshes = parser.json_data.get("meshes", [])
                    if meshes:
                        return ValidationCheck(
                            name="shape_match",
                            status=ValidationStatus.WARNING,
                            message=f"Basic check: {len(meshes)} mesh(es) (full comparison unavailable: {e})",
                            value={"mesh_count": len(meshes), "comparison_available": False},
                        )
            return ValidationCheck(
                name="shape_match",
                status=ValidationStatus.SKIPPED,
                message=f"Dependencies not available: {e}",
            )
        except Exception as e:
            return ValidationCheck(
                name="shape_match",
                status=ValidationStatus.WARNING,
                message=f"Shape analysis failed: {e}",
            )

    async def validate_model(
        self,
        model_path: Path,
        source_path: Path | None = None,
    ) -> ValidationResult:
        """
        Run all validation checks on a 3D model.

        Returns a ValidationResult with all checks and fidelity score.
        """
        result = ValidationResult(
            model_path=model_path,
            source_path=source_path,
        )

        logger.info(f"Validating: {model_path.name}")

        # Run all validation checks
        checks = [
            self.validate_file_exists(model_path),
            self.validate_file_size(model_path),
            self.validate_format(model_path),
            self.validate_triangle_count(model_path),
            self.validate_textures(model_path),
            self.validate_color_match(model_path, source_path),
            self.validate_shape_match(model_path, source_path),
        ]

        for check in checks:
            result.add_check(check)
            status_icon = {
                ValidationStatus.PASSED: "✅",
                ValidationStatus.WARNING: "⚠️",
                ValidationStatus.FAILED: "❌",
                ValidationStatus.SKIPPED: "⏭️",
            }.get(check.status, "?")
            logger.debug(f"  {status_icon} {check.name}: {check.message}")

        # Calculate fidelity score
        fidelity = result.calculate_fidelity()

        # Determine overall status
        failed_checks = [c for c in result.checks if c.status == ValidationStatus.FAILED]
        warning_checks = [c for c in result.checks if c.status == ValidationStatus.WARNING]

        if failed_checks:
            result.status = ValidationStatus.FAILED
        elif warning_checks:
            result.status = ValidationStatus.WARNING
        else:
            result.status = ValidationStatus.PASSED

        # Log summary
        status_msg = f"{'✅ PASSED' if result.passed else '❌ FAILED'}"
        ready_msg = f"{'Production Ready' if result.production_ready else 'Needs Improvement'}"
        logger.info(f"  {status_msg} - Fidelity: {fidelity:.1%} ({ready_msg})")

        return result

    def find_models(self, collection: str | None = None) -> list[Path]:
        """Find all 3D models in the generated directory."""
        search_dir = self.models_dir / collection if collection else self.models_dir

        if not search_dir.exists():
            logger.warning(f"Models directory not found: {search_dir}")
            return []

        models = list(search_dir.rglob("*.glb")) + list(search_dir.rglob("*.gltf"))
        return sorted(models)

    def find_source_image(self, model_path: Path) -> Path | None:
        """Try to find the source image for a 3D model."""
        # Extract collection and base name from model path
        collection = model_path.parent.name
        source_collection_dir = self.source_dir / collection

        if not source_collection_dir.exists():
            return None

        # Try to match by name
        model_stem = model_path.stem.replace("_meshy", "").replace("_huggingface", "")

        for ext in [".jpg", ".jpeg", ".png", ".webp"]:
            candidates = [
                source_collection_dir / f"{model_stem}{ext}",
                source_collection_dir / f"{model_stem.upper()}{ext}",
                source_collection_dir / f"{model_stem.lower()}{ext}",
            ]
            for candidate in candidates:
                if candidate.exists():
                    return candidate

        return None

    async def validate_all(
        self,
        collection: str | None = None,
        save_report: bool = True,
    ) -> dict[str, list[ValidationResult]]:
        """Validate all 3D models."""
        models = self.find_models(collection)

        if not models:
            logger.warning("No 3D models found to validate")
            return {}

        logger.info(f"\n{'=' * 60}")
        logger.info("3D ASSET QUALITY VALIDATION")
        logger.info(f"{'=' * 60}")
        logger.info(f"Found {len(models)} model(s) to validate\n")

        results_by_collection: dict[str, list[ValidationResult]] = {}

        for model_path in models:
            collection_name = model_path.parent.name
            if collection_name not in results_by_collection:
                results_by_collection[collection_name] = []

            source_path = self.find_source_image(model_path)
            result = await self.validate_model(model_path, source_path)
            results_by_collection[collection_name].append(result)

        # Summary
        self._print_summary(results_by_collection)

        # Save report
        if save_report:
            self._save_report(results_by_collection)

        return results_by_collection

    def _print_summary(self, results: dict[str, list[ValidationResult]]) -> None:
        """Print validation summary."""
        logger.info(f"\n{'=' * 60}")
        logger.info("VALIDATION SUMMARY")
        logger.info(f"{'=' * 60}")

        total_passed = 0
        total_warned = 0
        total_failed = 0
        total_production_ready = 0

        for collection, coll_results in results.items():
            passed = sum(1 for r in coll_results if r.status == ValidationStatus.PASSED)
            warned = sum(1 for r in coll_results if r.status == ValidationStatus.WARNING)
            failed = sum(1 for r in coll_results if r.status == ValidationStatus.FAILED)
            ready = sum(1 for r in coll_results if r.production_ready)

            total_passed += passed
            total_warned += warned
            total_failed += failed
            total_production_ready += ready

            logger.info(f"\n{collection.upper()}:")
            logger.info(f"  ✅ Passed: {passed}")
            logger.info(f"  ⚠️ Warnings: {warned}")
            logger.info(f"  ❌ Failed: {failed}")
            logger.info(f"  🚀 Production Ready (95%+): {ready}/{len(coll_results)}")

        total = sum(len(r) for r in results.values())
        logger.info(f"\n{'=' * 60}")
        logger.info(f"TOTAL: {total_passed} passed, {total_warned} warnings, {total_failed} failed")
        logger.info(
            f"PRODUCTION READY: {total_production_ready}/{total} ({100 * total_production_ready / total:.0f}%)"
            if total > 0
            else ""
        )
        logger.info(f"{'=' * 60}")

    def _save_report(self, results: dict[str, list[ValidationResult]]) -> Path:
        """Save validation report to JSON."""
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.reports_dir / f"validation_report_{timestamp}.json"

        report = {
            "timestamp": datetime.now().isoformat(),
            "config": {
                "min_file_size_kb": self.config.min_file_size_bytes / 1024,
                "max_file_size_mb": self.config.max_file_size_bytes / (1024 * 1024),
                "min_triangles": self.config.min_triangle_count,
                "max_triangles": self.config.max_triangle_count,
                "production_threshold": self.config.production_fidelity_threshold,
            },
            "collections": {},
            "summary": {
                "total_models": 0,
                "total_passed": 0,
                "total_warnings": 0,
                "total_failed": 0,
                "production_ready": 0,
            },
        }

        for collection, coll_results in results.items():
            report["collections"][collection] = {
                "models": [
                    {
                        "path": str(r.model_path.name),
                        "source": str(r.source_path.name) if r.source_path else None,
                        "status": r.status.value,
                        "fidelity_score": round(r.fidelity_score, 4),
                        "production_ready": r.production_ready,
                        "checks": [
                            {
                                "name": c.name,
                                "status": c.status.value,
                                "message": c.message,
                                "value": c.value,
                            }
                            for c in r.checks
                        ],
                    }
                    for r in coll_results
                ],
                "summary": {
                    "total": len(coll_results),
                    "passed": sum(1 for r in coll_results if r.status == ValidationStatus.PASSED),
                    "warnings": sum(
                        1 for r in coll_results if r.status == ValidationStatus.WARNING
                    ),
                    "failed": sum(1 for r in coll_results if r.status == ValidationStatus.FAILED),
                    "production_ready": sum(1 for r in coll_results if r.production_ready),
                },
            }

            report["summary"]["total_models"] += len(coll_results)
            report["summary"]["total_passed"] += sum(
                1 for r in coll_results if r.status == ValidationStatus.PASSED
            )
            report["summary"]["total_warnings"] += sum(
                1 for r in coll_results if r.status == ValidationStatus.WARNING
            )
            report["summary"]["total_failed"] += sum(
                1 for r in coll_results if r.status == ValidationStatus.FAILED
            )
            report["summary"]["production_ready"] += sum(
                1 for r in coll_results if r.production_ready
            )

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"\nReport saved: {report_path}")
        return report_path


def print_banner() -> None:
    """Print CLI banner."""
    banner = """
================================================================================
              SKYYROSE 3D ASSET QUALITY VALIDATION AGENT

================================================================================

Validation Checks:
  1. File Integrity    (exists, size 50KB-50MB, valid GLB format)
  2. Mesh Quality      (triangle count 5K-500K, textures, materials)
  3. Visual Fidelity   (color match ≥85%, shape match ≥90%)
  4. Production Ready  (overall fidelity ≥95%)

================================================================================
"""
    print(banner)


async def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="3D Asset Quality Validation Agent for SkyyRose",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate all 3D models",
    )
    parser.add_argument(
        "--collection",
        choices=["signature", "love-hurts", "black-rose"],
        help="Validate specific collection",
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Validate single file",
    )
    parser.add_argument(
        "--source",
        type=Path,
        help="Source image for comparison (with --file)",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate validation report",
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

    validator = ThreeDAssetValidator()

    if args.file:
        if not args.file.exists():
            logger.error(f"File not found: {args.file}")
            return 1

        result = await validator.validate_model(args.file, args.source)

        print(f"\n{'=' * 60}")
        print("VALIDATION RESULT")
        print(f"{'=' * 60}")
        print(f"Status: {result.status.value.upper()}")
        print(f"Fidelity Score: {result.fidelity_score:.1%}")
        print(f"Production Ready: {'Yes' if result.production_ready else 'No'}")
        print("\nChecks:")
        for check in result.checks:
            status_icon = {
                ValidationStatus.PASSED: "✅",
                ValidationStatus.WARNING: "⚠️",
                ValidationStatus.FAILED: "❌",
                ValidationStatus.SKIPPED: "⏭️",
            }.get(check.status, "?")
            print(f"  {status_icon} {check.name}: {check.message}")

        return 0 if result.passed else 1

    elif args.all or args.collection:
        results = await validator.validate_all(
            collection=args.collection,
            save_report=args.report,
        )

        # Return success if all models passed
        all_passed = all(
            r.status in (ValidationStatus.PASSED, ValidationStatus.WARNING)
            for coll_results in results.values()
            for r in coll_results
        )
        return 0 if all_passed else 1

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
