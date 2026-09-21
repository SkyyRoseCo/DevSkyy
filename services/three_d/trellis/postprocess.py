"""Mesh post-processing: cleanup, decimation, AR export.

TRELLIS outputs a high-quality GLB, but production e-commerce delivery wants:

- Reasonable polycount for the target device (mobile / desktop / AR)
- Texture compression (KTX2 / WebP) to keep page weight in check
- Normalized bounding box (unit cube centered on origin) so it drops into a
  Three.js scene without extra transforms
- USDZ export for iOS Quick Look AR
- Optional PLY export for research / archival

This module wraps :mod:`trimesh` (and falls back to pure-Python copy ops when
``trimesh`` isn't installed, so the pipeline still runs end-to-end with
slightly larger files).

Author: DevSkyy Platform Team
Version: 1.0.0
"""

from __future__ import annotations

import logging
import shutil
import subprocess  # noqa: S404 — invoked with no untrusted input
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from services.three_d.trellis.config import TrellisConfig, TrellisSamplingParams
from services.three_d.trellis.garment_aware import GarmentCategory, knowledge_for

logger = logging.getLogger(__name__)


# =============================================================================
# Results
# =============================================================================


@dataclass(slots=True)
class PostprocessResult:
    """Output bundle from postprocessing."""

    glb_path: str
    usdz_path: str | None = None
    ply_path: str | None = None
    thumbnail_path: str | None = None
    polycount: int | None = None
    file_size_bytes: int | None = None
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Postprocessor
# =============================================================================


class MeshPostprocessor:
    """Garment-aware mesh postprocessing.

    Usage:
        post = MeshPostprocessor(TrellisConfig())
        result = post.process(
            raw_glb="/tmp/trellis_out.glb",  # nosec B108 — docstring example only, not executed
            category=GarmentCategory.HOODIE,
            sampling=config.sampling,
        )
    """

    def __init__(self, config: TrellisConfig | None = None) -> None:
        self.config = config or TrellisConfig.from_env()
        self.config.ensure_dirs()

    def process(
        self,
        *,
        raw_glb: str | Path,
        category: GarmentCategory,
        sampling: TrellisSamplingParams,
        artifact_id: str,
    ) -> PostprocessResult:
        """Run the full postprocessing chain on ``raw_glb``."""
        src = Path(raw_glb)
        if not src.exists():
            raise FileNotFoundError(f"Raw GLB not found: {src}")

        warnings: list[str] = []
        out_dir = Path(self.config.output_dir)
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        stem = f"{artifact_id}_{timestamp}"

        glb_out = out_dir / f"{stem}.glb"

        if not self.config.enable_postprocess:
            shutil.copy2(src, glb_out)
            warnings.append("postprocessing disabled — raw GLB copied through")
            return PostprocessResult(
                glb_path=str(glb_out),
                file_size_bytes=glb_out.stat().st_size,
                warnings=warnings,
            )

        polycount, glb_bytes = self._clean_and_decimate(
            src=src,
            dst=glb_out,
            category=category,
            sampling=sampling,
            warnings=warnings,
        )

        usdz_path = None
        if self.config.export_usdz_for_ios:
            usdz_path = self._maybe_export_usdz(glb_out, stem, warnings)

        thumbnail_path = self._render_thumbnail(glb_out, stem, warnings)

        return PostprocessResult(
            glb_path=str(glb_out),
            usdz_path=str(usdz_path) if usdz_path else None,
            thumbnail_path=str(thumbnail_path) if thumbnail_path else None,
            polycount=polycount,
            file_size_bytes=glb_bytes,
            warnings=warnings,
            metadata={
                "category": category.value,
                "target_polycount": sampling.target_polycount,
                "texture_size": sampling.texture_size,
            },
        )

    # ---------------------------------------------------------------------
    # Pipeline stages
    # ---------------------------------------------------------------------

    def _clean_and_decimate(
        self,
        *,
        src: Path,
        dst: Path,
        category: GarmentCategory,
        sampling: TrellisSamplingParams,
        warnings: list[str],
    ) -> tuple[int | None, int]:
        """Load → fix normals → decimate → normalize bbox → write.

        Returns ``(polycount, file_size_bytes)``. Polycount may be ``None`` if
        trimesh isn't installed (we just copy the file through).
        """
        try:
            import numpy as np
            import trimesh
        except ImportError:
            warnings.append("trimesh / numpy not installed — copying GLB unchanged")
            shutil.copy2(src, dst)
            return None, dst.stat().st_size

        try:
            scene_or_mesh = trimesh.load(str(src), force="scene")
        except Exception as exc:  # noqa: BLE001 — trimesh raises broadly
            warnings.append(f"trimesh load failed: {exc} — copying through")
            shutil.copy2(src, dst)
            return None, dst.stat().st_size

        meshes: list[trimesh.Trimesh] = self._gather_meshes(scene_or_mesh)
        if not meshes:
            warnings.append("no geometry found in GLB — copying through")
            shutil.copy2(src, dst)
            return None, dst.stat().st_size

        target = self._target_polycount(category, sampling)
        for i, mesh in enumerate(meshes):
            mesh.fix_normals()
            mesh.update_faces(mesh.nondegenerate_faces())
            mesh.remove_unreferenced_vertices()
            if mesh.faces.shape[0] > target:
                try:
                    decimated = mesh.simplify_quadric_decimation(face_count=target)
                    if decimated is not None and decimated.faces.shape[0] > 0:
                        meshes[i] = decimated
                except Exception as exc:  # noqa: BLE001
                    warnings.append(f"decimation failed for mesh #{i}: {exc}")

        normalized = self._merge_and_normalize(meshes, np, trimesh)

        try:
            normalized.export(str(dst), file_type="glb")
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"GLB export failed: {exc} — copying source")
            shutil.copy2(src, dst)
            return None, dst.stat().st_size

        return int(normalized.faces.shape[0]), dst.stat().st_size

    def _gather_meshes(self, loaded: Any) -> list[Any]:
        try:
            import trimesh
        except ImportError:
            return []

        if isinstance(loaded, trimesh.Scene):
            return [g for g in loaded.geometry.values() if isinstance(g, trimesh.Trimesh)]
        if isinstance(loaded, trimesh.Trimesh):
            return [loaded]
        return []

    def _merge_and_normalize(
        self,
        meshes: list[Any],
        np: Any,
        trimesh: Any,
    ) -> Any:
        """Concatenate, then translate + scale into a unit cube at origin."""
        merged = trimesh.util.concatenate(meshes) if len(meshes) > 1 else meshes[0]

        bounds = merged.bounds  # (2, 3)
        center = bounds.mean(axis=0)
        merged.apply_translation(-center)

        extent = float((merged.bounds[1] - merged.bounds[0]).max())
        if extent > 0:
            merged.apply_scale(1.0 / extent)
        return merged

    def _target_polycount(
        self,
        category: GarmentCategory,
        sampling: TrellisSamplingParams,
    ) -> int:
        """Pick a decimation target combining category prior + quality preset."""
        kn = knowledge_for(category)
        # Quality preset wins, but never go below 60% of the category hint.
        floor = int(kn.polycount_hint * 0.6)
        return max(floor, sampling.target_polycount)

    # ---------------------------------------------------------------------
    # USDZ
    # ---------------------------------------------------------------------

    def _maybe_export_usdz(
        self,
        glb_path: Path,
        stem: str,
        warnings: list[str],
    ) -> Path | None:
        """Try usd-core, then fall back to ``usd_from_gltf`` CLI if available."""
        usdz_out = Path(self.config.output_dir) / f"{stem}.usdz"

        if self._export_usdz_via_python(glb_path, usdz_out, warnings):
            return usdz_out
        if self._export_usdz_via_cli(glb_path, usdz_out, warnings):
            return usdz_out

        warnings.append("USDZ export skipped — install `usd-core` or `usd_from_gltf` to enable")
        return None

    def _export_usdz_via_python(
        self,
        glb_path: Path,
        usdz_out: Path,
        warnings: list[str],
    ) -> bool:
        try:
            from pxr import Usd  # type: ignore[import-not-found]  # noqa: F401
        except ImportError:
            return False
        # Real USD conversion requires shader translation; out of scope for v1.
        # We surface a warning so callers know the path is unimplemented but
        # the dependency is present.
        warnings.append(
            "pxr.Usd available but GLB→USDZ shader translation not wired up — "
            "falling through to CLI"
        )
        return False

    def _export_usdz_via_cli(
        self,
        glb_path: Path,
        usdz_out: Path,
        warnings: list[str],
    ) -> bool:
        binary = shutil.which("usd_from_gltf")
        if not binary:
            return False
        try:
            subprocess.run(
                [binary, str(glb_path), str(usdz_out)],
                check=True,
                capture_output=True,
                timeout=60,
            )
        except subprocess.CalledProcessError as exc:
            warnings.append(f"usd_from_gltf failed: {exc.stderr.decode(errors='ignore')[:200]}")
            return False
        except subprocess.TimeoutExpired:
            warnings.append("usd_from_gltf timed out")
            return False
        return usdz_out.exists()

    # ---------------------------------------------------------------------
    # Thumbnail
    # ---------------------------------------------------------------------

    def _render_thumbnail(
        self,
        glb_path: Path,
        stem: str,
        warnings: list[str],
    ) -> Path | None:
        """Headless thumbnail via trimesh's offscreen renderer.

        Falls through silently if pyglet/pyrender aren't installed; the web
        viewer can synthesize its own preview from the GLB anyway.
        """
        try:
            import trimesh
        except ImportError:
            return None

        try:
            scene = trimesh.load(str(glb_path), force="scene")
            png_bytes = scene.save_image(resolution=(512, 512), visible=True)
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"thumbnail render skipped: {exc}")
            return None

        if not png_bytes:
            return None

        thumb_path = Path(self.config.output_dir) / f"{stem}_preview.png"
        thumb_path.write_bytes(png_bytes)
        return thumb_path


__all__ = [
    "MeshPostprocessor",
    "PostprocessResult",
]
