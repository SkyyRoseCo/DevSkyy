"""
ThreeDAgent — Phase 16 Legendary 3D Architect.

Promoted to ADK SuperAgent for comprehensive "Back Data" (telemetry) and
high-fidelity 3D replica generation using Blender + Gemini RAS.

Inherits from CreativeAgent to leverage standardized enterprise tools
and observability via Google ADK.
"""

from __future__ import annotations

import asyncio
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import httpx

from adk.base import ADKProvider, AgentConfig
from adk.super_agents import CreativeAgent
from ai_3d.generation_pipeline import (
    ThreeDGenerationPipeline,
)
from ai_3d.providers.meshy import MeshyClient
from ai_3d.virtual_photoshoot import VirtualPhotoshootGenerator

from ..config import GEMINI_VISION_MODEL, OUTPUT_DIR
from ..models import GenerationResult

logger = logging.getLogger(__name__)

_DEFAULT_3D_OUTPUT_DIR = "renders/3d"


def _compute_fidelity(
    meshy_succeeded: bool, blender_fallback_used: bool, synthesis_succeeded: bool
) -> float:
    """Score derived from pipeline stage outcomes (0–100). Never hardcoded."""
    base = 100.0 if meshy_succeeded else 60.0
    if blender_fallback_used:
        base -= 20.0
    if not synthesis_succeeded:
        base -= 40.0
    return max(0.0, min(100.0, base))


class ThreeDAgent(CreativeAgent):
    """The Architect of 3D Digital Replicas - Promoted to ADK SuperAgent."""

    def __init__(
        self,
        output_dir_3d: str = _DEFAULT_3D_OUTPUT_DIR,
        output_dir_2d: str | None = None,
        config: AgentConfig | None = None,
    ) -> None:
        # Default config if not provided
        if config is None:
            config = AgentConfig(
                name="legendary_3d_architect",
                provider=ADKProvider.GOOGLE,
                model=GEMINI_VISION_MODEL,
                system_prompt="You are the Legendary 3D Architect for SkyyRose. Your mission is 100% accurate digital replicas.",
            )

        # Initialize BaseSuperAgent/CreativeAgent
        super().__init__(config)

        self.output_dir_3d = Path(output_dir_3d)
        # Use canonical project output dir if not provided
        self.output_dir_2d = Path(output_dir_2d) if output_dir_2d else OUTPUT_DIR

        self.output_dir_3d.mkdir(parents=True, exist_ok=True)
        self.output_dir_2d.mkdir(parents=True, exist_ok=True)

        self.pipeline = ThreeDGenerationPipeline()
        self.photoshoot = VirtualPhotoshootGenerator(
            output_dir=self.output_dir_2d, models_dir=self.output_dir_3d
        )

    async def generate_replica(
        self, sku: str, techflat_path: str, style: str = "flat_lay"
    ) -> dict[str, Any]:
        """
        Legendary Replica Workflow:
        1. Digitization: Image -> 3D (.glb)
        2. Scaffolding: 3D -> Headless Blender Render (.png)
        3. Synthesis: Scaffold + Techflat -> Professional Render (.webp)

        Reads the per-product design dossier (hard-fail on missing — see
        skyyrose.core.dossier_loader.DossierMissingError) and feeds its
        garment_type_lock, branding_block, and negative_block verbatim into
        the RAS prompt. The thin canonical-CSV ``branding_spec`` column is
        NOT a fallback.
        """
        from skyyrose.core.product import get_product, render_reference

        # --- Stage 0: ADK Observer ---
        logger.info(f"Starting Legendary 3D-First Workflow for {sku}")

        # Load dossier — hard-fails (DossierMissingError) if absent (H1).
        product = get_product(sku)
        reference = render_reference(product, "front")
        if Path(techflat_path).resolve() != Path(reference["path"]):
            raise ValueError("Techflat must match the registry front binding")
        techflat_path = reference["path"]
        dossier = dict(product["dossier"])
        dossier["product_corrections"] = product["corrections"]
        dossier["product_provenance"] = product["provenance"]

        # Capture "Back Data" via ADK run (non-blocking, captures reasoning)
        try:
            adk_prompt = (
                f"REPLICA TASK: {dossier['name']} (SKU {sku}). "
                f"GARMENT LOCK: {dossier['garment_type_lock']}"
            )
            adk_result = await self.execute(adk_prompt)
            metadata = adk_result.to_dict() if hasattr(adk_result, "to_dict") else {}
        except Exception as e:
            logger.warning(f"ADK Telemetry failed for {sku}: {e}")
            metadata = {}

        sku_dir = self.output_dir_2d / sku
        sku_dir.mkdir(parents=True, exist_ok=True)

        # --- Stage 1: 3D Digitization ---
        # Two paths into the round-table-or-Meshy substrate:
        #   ELITE_STUDIO_USE_ROUND_TABLE=1 -> tournament (Meshy + Tripo + TRELLIS_local
        #                                     + AniGen with circuit-breaker health).
        #   default (unset/0)              -> direct MeshyClient (existing behaviour).
        # The round-table path is opt-in until end-to-end smoke runs validate the
        # winner selection on a representative SKU set. See tasks/phase-e-manifest.md.
        use_round_table = os.environ.get("ELITE_STUDIO_USE_ROUND_TABLE", "0").lower() in (
            "1",
            "true",
            "yes",
        )

        if use_round_table:
            logger.info(f"[{sku}] Stage 1: 3D Digitization (round-table tournament)...")
            try:
                from orchestration.threed_round_table import ThreeDRoundTable

                round_table = ThreeDRoundTable(output_dir=str(self.output_dir_3d))
                rt_result = await round_table.compete_image_to_3d(
                    image_path=techflat_path,
                    task_id=sku,
                )
                winner = rt_result.winner
                if winner is None or not winner.output_path:
                    return {
                        "success": False,
                        "error": "3D Generation failed: round-table produced no winner",
                        "sku": sku,
                    }
                glb_path = Path(winner.output_path)
                thumbnail_url = (winner.metadata or {}).get("thumbnail_url")
                logger.info(
                    f"[{sku}] round-table winner: provider={winner.provider} "
                    f"model_id={winner.model_id}"
                )
            except Exception as exc:
                logger.exception(f"[{sku}] round-table dispatch failed: {exc}")
                return {
                    "success": False,
                    "error": f"3D Generation failed (round-table): {exc}",
                    "sku": sku,
                }
        else:
            logger.info(f"[{sku}] Stage 1: 3D Digitization (Meshy AI)...")
            async with MeshyClient() as client:
                meshy_result = await client.generate_from_image(
                    image_path=techflat_path,
                    output_dir=str(self.output_dir_3d),
                )

            if not meshy_result:
                return {
                    "success": False,
                    "error": "3D Generation failed: Meshy returned no result",
                    "sku": sku,
                }

            glb_path = Path(meshy_result["model_path"])
            thumbnail_url = meshy_result.get("thumbnail_url")

        # --- Stage 1.5: bpy GLB cleanup (decimate + smooth normals) ---
        glb_path = await self._blender_glb_cleanup(glb_path, sku)

        # --- Stage 2: Headless Blender Scaffolding ---
        logger.info(f"[{sku}] Stage 2: Headless Blender Scaffolding...")
        scaffold_path = sku_dir / f"{sku}_scaffold.png"

        # Call the verified Blender script
        render_cmd = [
            "blender",
            "-b",
            "-P",
            "scripts/render_professional.py",
            "--",
            str(glb_path),
            str(scaffold_path),
            "front",
        ]

        used_blender_fallback = False
        try:
            # asyncio.to_thread frees the event loop while Blender renders (~30-120s).
            # Without this, concurrent generate_replica calls under ainvoke() would
            # serialize on the GIL/event loop and time out at the LangGraph layer.
            await asyncio.to_thread(
                subprocess.run, render_cmd, check=True, capture_output=True, timeout=120
            )
            logger.info(f"[{sku}] Scaffold generated at {scaffold_path}")
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ) as blender_err:
            logger.warning(
                f"[{sku}] Blender rendering failed ({blender_err}); falling back to scaffold"
            )
            used_blender_fallback = True
            if thumbnail_url:
                async with httpx.AsyncClient(timeout=30.0) as http:
                    resp = await http.get(thumbnail_url)
                    resp.raise_for_status()
                    scaffold_path.write_bytes(resp.content)
            else:
                scaffold_path = Path(techflat_path)

        # --- Stage 3+: FLUX Synthesis (Kontext → mask → Fill → audit) ---
        # GeneratorAgent (Gemini RAS) is replaced by the dossier-aware FLUX
        # pipeline. The Meshy GLB above remains for Three.js immersive scenes;
        # FLUX produces the 2D e-commerce renders independently.
        logger.info(f"[{sku}] Stage 3: FLUX Synthesis pipeline...")

        from skyyrose.core.dossier_loader import DOSSIERS_DIR

        from ..synthesis import render as flux_render

        dossier["_dossier_path"] = (
            str(DOSSIERS_DIR / f"{dossier['slug']}.md") if dossier.get("slug") else ""
        )

        flux_result = await flux_render(
            sku=sku,
            view="front",
            dossier=dossier,
            techflat_path=techflat_path,
            out_dir=sku_dir,
        )

        if flux_result.error and not flux_result.output_path and not flux_result.quarantine_path:
            return {"success": False, "error": flux_result.error, "sku": sku}

        front_final = flux_result.output_path or flux_result.quarantine_path
        audit_result = flux_result.audit_result

        if not flux_result.ok:
            logger.warning(
                f"[{sku}] FLUX render quarantined to {flux_result.quarantine_path} "
                f"after {flux_result.attempts} attempt(s)"
            )

        return {
            "success": flux_result.ok,
            "glb_path": str(glb_path),
            "renders": {"front": str(front_final), "scaffold": str(scaffold_path)},
            "vision_audit": audit_result.to_dict() if audit_result else {},
            "manifest_path": str(flux_result.manifest.get("output_path", "")),
            "fidelity_score": _compute_fidelity(
                meshy_succeeded=True,
                blender_fallback_used=used_blender_fallback,
                synthesis_succeeded=flux_result.ok,
            ),
            "provider": "flux",
            "adk_metadata": metadata,
            "reference_evidence": reference,
        }

    def generate_result_bridge(
        self, photoshoot_output: dict[str, Any], view: str
    ) -> GenerationResult:
        """Helper to convert photoshoot output back to EliteStudio GenerationResult."""
        path = photoshoot_output["renders"].get(view)
        if not path:
            # Fallback to 'front' if specific view missing
            path = photoshoot_output["renders"].get("front", "")

        return GenerationResult(
            success=photoshoot_output["success"],
            provider=f"3d-render/{photoshoot_output.get('provider', 'unknown')}",
            model="ai_3d-replica-v1",
            output_path=path,
            metadata=photoshoot_output.get("adk_metadata", {}),
        )

    async def _blender_glb_cleanup(self, glb_path: Path, sku: str) -> Path:
        """Decimate + smooth-normal the Meshy GLB via a self-contained bpy script.

        CLI-Anything Blender only builds primitive scenes from JSON — it has no
        import_scene.gltf path. We bypass its harness entirely and call
        ``blender -b --python <tempscript>`` with a standalone bpy snippet that
        uses the full bpy API. Non-fatal: returns ``glb_path`` unchanged when
        blender is absent, errors, or times out.
        """
        cleaned_path = glb_path.parent / f"{sku}_clean.glb"
        bpy_script = (
            "import bpy, sys\n"
            "args = sys.argv[sys.argv.index('--') + 1:]\n"
            "glb_in, glb_out = args[0], args[1]\n"
            "bpy.ops.wm.read_factory_settings(use_empty=True)\n"
            "bpy.ops.import_scene.gltf(filepath=glb_in)\n"
            "for obj in list(bpy.data.objects):\n"
            "    if obj.type == 'MESH':\n"
            "        bpy.context.view_layer.objects.active = obj\n"
            "        obj.select_set(True)\n"
            "        mod = obj.modifiers.new(name='Decimate', type='DECIMATE')\n"
            "        mod.ratio = 0.5\n"
            "        bpy.ops.object.modifier_apply(modifier='Decimate')\n"
            "        bpy.ops.object.shade_smooth()\n"
            "        obj.select_set(False)\n"
            "bpy.ops.export_scene.gltf(filepath=glb_out, export_format='GLB')\n"
        )
        tmp_path: str | None = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
                tmp.write(bpy_script)
                tmp_path = tmp.name

            cmd = [
                "blender",
                "-b",
                "--python",
                tmp_path,
                "--",
                str(glb_path),
                str(cleaned_path),
            ]
            await asyncio.to_thread(
                subprocess.run, cmd, check=True, capture_output=True, timeout=90
            )
            if cleaned_path.is_file():
                logger.info("[%s] bpy GLB cleanup → %s", sku, cleaned_path)
                return cleaned_path
            return glb_path
        except FileNotFoundError:
            logger.info("[%s] blender not found; skipping GLB cleanup", sku)
            return glb_path
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            logger.warning("[%s] bpy GLB cleanup skipped: %s", sku, exc)
            return glb_path
        except Exception as exc:  # pragma: no cover
            logger.warning("[%s] bpy GLB cleanup unexpected error: %s", sku, exc)
            return glb_path
        finally:
            if tmp_path:
                Path(tmp_path).unlink(missing_ok=True)
