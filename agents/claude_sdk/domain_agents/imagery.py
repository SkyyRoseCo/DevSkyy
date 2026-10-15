"""
SDK Imagery Domain Agents
===========================

SDK-powered sub-agents for the Imagery core domain.
These agents can invoke the actual image generation pipelines,
run VTON operations, and manage the compositor workflow.

Agents:
    SDKVirtualTryOnAgent   — Run VTON via nano-banana pipeline
    SDKCompositorAgent     — 6-stage compositor pipeline execution
    SDKImageGenAgent       — Generate product renders via FLUX/Gemini
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agents.claude_sdk.sdk_sub_agent import SDKSubAgent
from agents.claude_sdk.tool_bridge import ToolProfile
from agents.core.base import CoreAgentType


class SDKVirtualTryOnAgent(SDKSubAgent):
    """Virtual try-on specialist with pipeline access.

    Executes the nano-banana VTON pipeline for product renders.
    Can generate front/back/branding views for any SKU.
    """

    name = "sdk_virtual_tryon"
    parent_type = CoreAgentType.IMAGERY
    description = "Run VTON pipeline for product renders"
    capabilities = [
        "vton_render",
        "batch_render",
        "model_composite",
        "garment_analysis",
        "render_verify",
    ]
    sdk_tools = ToolProfile.IMAGERY + ["Grep"]
    sdk_model = "sonnet"
    sdk_output_base = Path("data/sdk_sessions/imagery/vton")

    def _sdk_default_prompt(self) -> str:
        return (
            "You are the DevSkyy Virtual Try-On Agent for SkyyRose.\n\n"
            "Pipeline: scripts/oai_render — new renders are OpenAI gpt-image-2 "
            "ONLY (paid; generate needs --yes and founder confirmation)\n\n"
            "Output format: {sku}-render-{front|back|branding}.webp\n"
            "Output dir: assets/images/products/\n"
            "Existing renders: 234 across 36 SKUs\n"
            "After writing a front or back render, bind it in the product "
            "registry: skyyrose.core.product_registry.update_catalog_fields("
            "sku, {'front_model_image' | 'back_model_image': path}), then run "
            "python scripts/sync_product_registry.py so the projections "
            "(catalog CSV, per-collection sot.json, data/sot-images.json) "
            "follow. Branding renders are supplementary assets with no SOT "
            "role — NEVER register one as a front/back image. Renders are "
            "discovered via get_product(sku)['images'], not filename "
            "convention.\n\n"
            "Product facts: skyyrose.core.product.get_product(sku) — the ONE product lookup (CLI: python -m skyyrose.core.product <sku> | --all | --skus). "
            "Garment color is get_product(sku)['garment']['color']; existing "
            "renders per role are get_product(sku)['images'].\n\n"
            "Rules:\n"
            "- Read get_product(sku) before rendering — NEVER invent SKUs\n"
            "- Check existing renders before re-generating\n"
            "- Verify output files exist after generation\n"
            "- Use .venv-imagery/ for image processing dependencies\n"
            "- Report render dimensions, file size, and quality score"
        )

    def _build_task_prompt(self, task: str, **kwargs: Any) -> str:
        """Enrich with SKU context for targeted rendering."""
        base = super()._build_task_prompt(task, **kwargs)
        sku = kwargs.get("sku")
        if sku:
            base += (
                f"\n\nTarget SKU: {sku}\n"
                "Read get_product(sku) (python -m skyyrose.core.product "
                f"{sku}) for this SKU's facts before rendering."
            )
        return base


class SDKCompositorAgent(SDKSubAgent):
    """6-stage compositor pipeline executor.

    Manages the full compositing workflow:
    BRIA bg-removal → Claude prompt engineering → IC-Light relighting
    → FLUX inpainting → GPSDiffusion shadows → Gemini QA gate.
    """

    name = "sdk_compositor"
    parent_type = CoreAgentType.IMAGERY
    description = "Execute 6-stage compositor pipeline for scene composites"
    capabilities = [
        "bg_removal",
        "scene_composite",
        "relight",
        "shadow_gen",
        "qa_gate",
        "batch_composite",
    ]
    sdk_tools = ToolProfile.IMAGERY + ["Grep"]
    sdk_model = "opus"
    sdk_output_base = Path("data/sdk_sessions/imagery/compositor")

    def _sdk_default_prompt(self) -> str:
        return (
            "You are the DevSkyy Compositor Agent for SkyyRose.\n\n"
            "6-Stage Pipeline:\n"
            "1. BRIA RMBG 2.0 → alpha matte (background removal)\n"
            "2. Claude Opus 4.6 → prompt engineering (scene+subject → FLUX prompt)\n"
            "3. IC-Light / libcom → relighting (match subject to scene)\n"
            "4. FLUX Fill Pro → inpainting (subject into scene)\n"
            "   Fallbacks: Kontext → Replicate\n"
            "5. GPSDiffusion → contact shadows (fallback: PIL gaussian)\n"
            "6. Gemini 3 Pro → visual QA gate\n\n"
            "Config: skyyrose/elite_studio/config.py\n"
            "Agent: skyyrose/elite_studio/agents/compositor_agent.py\n\n"
            "Rules:\n"
            "- Read config.py for API keys and model settings\n"
            "- Run each stage sequentially — verify output before next\n"
            "- Log stage timing for performance tracking\n"
            "- QA gate must PASS before saving final composite\n"
            "- Output to assets/images/composites/{sku}/"
        )


class SDKImageGenAgent(SDKSubAgent):
    """Image generation specialist with multi-model access.

    Generates product imagery using FLUX, Gemini, and other
    models. Handles the FLUX orchestrator pipeline.
    """

    name = "sdk_image_gen"
    parent_type = CoreAgentType.IMAGERY
    description = "Generate product renders via FLUX/Gemini pipelines"
    capabilities = [
        "flux_generate",
        "gemini_generate",
        "upscale",
        "style_transfer",
        "batch_generate",
    ]
    sdk_tools = ToolProfile.IMAGERY + ["WebFetch"]
    sdk_model = "sonnet"
    sdk_output_base = Path("data/sdk_sessions/imagery/generation")

    def _sdk_default_prompt(self) -> str:
        return (
            "You are the DevSkyy Image Generation Agent for SkyyRose.\n\n"
            "Available models:\n"
            "- FLUX.2-pro (primary high-quality)\n"
            "- FLUX.1-schnell-Free (fast iteration)\n"
            "- gemini-2.5-flash-image (Gemini vision)\n"
            "- imagen-4.0-ultra-generate-001 (Google Imagen)\n"
            "- gpt-image-1.5 (OpenAI)\n\n"
            "Pipelines:\n"
            "- FLUX Orchestrator: pipelines/skyyrose_master_orchestrator.py\n"
            "- Luxury Pipeline: pipelines/skyyrose_luxury_pipeline.py\n"
            "- HuggingFace Space: damBruh/skyyrose-flux-upscaler\n\n"
            "Brand colors: #B76E79 rose gold, #0A0A0A dark, "
            "#D4AF37 gold, #DC143C crimson\n\n"
            "Rules:\n"
            "- Use .venv-imagery/ for image processing\n"
            "- Verify prompt includes brand-consistent aesthetics\n"
            "- Output as .webp with quality 90+\n"
            "- Log model used, generation time, and dimensions"
        )


__all__ = [
    "SDKVirtualTryOnAgent",
    "SDKCompositorAgent",
    "SDKImageGenAgent",
]
