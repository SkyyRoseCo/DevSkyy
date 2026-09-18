"""
SDK Immersive 3D/AR Experience Agents
=======================================

The crown jewel of the SkyyRose dashboard — SDK-powered agents that
build immersive 3D shopping experiences end-to-end.

Pipeline:
    1. SDKGarment3DAgent    → Generate 3D clothing models (Tripo API)
    2. SDKSceneBuilderAgent → Build Three.js immersive shopping worlds
    3. SDKAvatarStylistAgent → Dress the SkyyRose Pixar avatar in outfits

These agents compose the full experience:
    Garment → 3D model (GLB) → Scene placement → Avatar try-on

Agents:
    SDKGarment3DAgent       — Text/image → 3D garment (Tripo3D API)
    SDKSceneBuilderAgent    — Build Three.js immersive shopping environments
    SDKAvatarStylistAgent   — Dress SkyyRose avatar, swap outfits, animate
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from claude_agent_sdk import AgentDefinition

from agents.claude_sdk.sdk_sub_agent import SDKSubAgent
from agents.claude_sdk.tool_bridge import ToolProfile
from agents.core.base import CoreAgentType


class SDKGarment3DAgent(SDKSubAgent):
    """3D garment generation specialist.

    Converts product images or descriptions into 3D models using
    Tripo3D API. Outputs GLB for web, USDZ for Apple AR.

    Pipeline: Product data → brand-aware prompt → Tripo3D → GLB/USDZ
    Post-processing: PBR textures, optimized polycount, web-ready.
    """

    name = "sdk_garment_3d"
    parent_type = CoreAgentType.IMAGERY
    description = "Generate 3D garment models from images/text via Tripo3D"
    capabilities = [
        "garment_to_3d",
        "image_to_3d",
        "text_to_3d",
        "model_optimize",
        "ar_export",
        "batch_3d",
    ]
    sdk_tools = ToolProfile.IMAGERY + ["WebFetch", "Grep"]
    sdk_model = "sonnet"
    sdk_output_base = Path("data/sdk_sessions/immersive/garment_3d")

    def _sdk_default_prompt(self) -> str:
        return (
            "You are the SkyyRose 3D Garment Generator — you create production-"
            "quality 3D clothing models for immersive shopping experiences.\n\n"
            "Pipeline:\n"
            "1. Read product data from skyyrose.core.product.get_product(sku) — the ONE product lookup (CLI: python -m skyyrose.core.product <sku> | --all | --skus)\n"
            "2. Resolve existing renders via get_product(sku)['images'][role] "
            "(data/sot-images.json is a generated projection of the same "
            "bindings, for non-Python consumers only) — never assume a "
            "literal filename pattern, the actual render may be named "
            "differently or be a hub-verified override.\n"
            "3. Build a brand-aware 3D prompt with collection aesthetics\n"
            "4. Call Tripo3D API via agents/tripo_agent.py patterns\n"
            "5. Export as GLB (web) + USDZ (Apple AR)\n"
            "6. Validate: polycount <100K, textures ≤2048px, PBR materials\n\n"
            "Tripo Config:\n"
            "- Agent: agents/tripo_agent.py (TripoConfig, GARMENT_TEMPLATES)\n"
            "- API: https://api.tripo3d.ai/v2\n"
            "- Key: TRIPO_API_KEY env var\n"
            "- Output: generated_assets/3d/{sku}/\n"
            "- Formats: GLB (primary), USDZ (AR), FBX (editor)\n\n"
            "Collection aesthetics (use in prompts):\n"
            "- Black Rose: dark elegance, matte black, rose gold accents\n"
            "- Love Hurts: deep reds, heart motifs, passionate textures\n"
            "- Signature: clean neutrals, golden details, Bay Area vibes\n\n"
            "Quality gates:\n"
            "- Polycount: 10K-100K (web-optimized, not raw sculpt)\n"
            "- Textures: PBR (albedo + normal + roughness + metallic)\n"
            "- UV mapping: clean, no overlaps, 0-1 space\n"
            "- File size: GLB <5MB, USDZ <10MB\n"
            "- Visual QA: Compare 3D render to source product image"
        )

    def _build_task_prompt(self, task: str, **kwargs: Any) -> str:
        """Enrich with SKU and collection context."""
        base = super()._build_task_prompt(task, **kwargs)
        sku = kwargs.get("sku")
        collection = kwargs.get("collection")
        if sku:
            base += (
                f"\n\nTarget SKU: {sku}\n"
                "Read get_product(sku) for this SKU's facts, then resolve "
                "existing renders via get_product(sku)['images'][role] for "
                "reference images — never assume a literal filename pattern."
            )
        if collection:
            base += f"\nCollection: {collection} — match the collection aesthetics.\n"
        return base


class SDKSceneBuilderAgent(SDKSubAgent):
    """Immersive 3D scene builder for shopping environments.

    Creates Three.js scenes that bring each collection to life as a
    walkable/scrollable 3D world. Products are placed naturally in
    the scene with interactive hotspots.

    Scene types:
    - Black Rose: Bay Bridge night scene, Oakland streets, neon + fog
    - Love Hurts: Enchanted cathedral, gothic rose dome, beast's lair
    - Signature: Golden Gate golden hour, SF fashion runway, fog cables
    """

    name = "sdk_scene_builder"
    parent_type = CoreAgentType.WEB_BUILDER
    description = "Build Three.js immersive shopping environments"
    capabilities = [
        "scene_create",
        "scene_edit",
        "hotspot_place",
        "lighting_setup",
        "particle_effects",
        "scroll_animation",
        "scene_optimize",
    ]
    sdk_tools = ToolProfile.WEB_BUILDER + ["WebFetch"]
    sdk_model = "opus"
    sdk_output_base = Path("data/sdk_sessions/immersive/scenes")

    def _sdk_default_prompt(self) -> str:
        return (
            "You are the SkyyRose Immersive Scene Builder — you create "
            "Three.js 3D shopping worlds that make buying feel like an "
            "experience, not a transaction.\n\n"
            "Engine: wordpress-theme/skyyrose-flagship/assets/js/immersive-world.js\n"
            "CSS: assets/css/immersive-world.css\n"
            "Templates: template-parts/immersive-loader.php\n"
            "Three.js CDN: v0.172.0 (via module import)\n\n"
            "Scene Architecture (from immersive-world.js):\n"
            "- config from #world-config JSON element\n"
            "- Scroll-driven camera (scrollProgress 0→1)\n"
            "- Product hotspots (3D positioned, click-to-buy)\n"
            "- Particle systems (per-collection atmospheric effects)\n"
            "- Scene layers (parallax depth groups)\n"
            "- Narrative panels (text that appears on scroll)\n"
            "- Avatar hotspot (hidden SkyyRose mascot easter egg)\n\n"
            "Collection Worlds:\n"
            "- Black Rose: BAY BRIDGE at night. Oakland East Bay. Street "
            "luxury. Neon signs, fog, bridge cables, car headlights. "
            "Product hotspots on bridge walkway.\n"
            "- Love Hurts: Beauty & Beast from BEAST's perspective. "
            "Enchanted rose under glass dome. Gothic cathedral. Candles, "
            "petals, stained glass light.\n"
            "- Signature: GOLDEN GATE at golden hour. Fashion runway "
            "through fog. Cable silhouettes, sunset gradient, fog wisps.\n\n"
            "Rules:\n"
            "- Read immersive-world.js BEFORE writing — match its API\n"
            "- Config format: {collection, products[], hotspots[], "
            "particles, lighting, camera_path}\n"
            "- Products placed NATURALLY in scene (on racks, on bridge, "
            "in rose dome) — never floating grids\n"
            "- Progressive enhancement: fallback to immersive.js for no-WebGL\n"
            "- Performance: <60MB scene total, LOD for distant objects, "
            "instanced meshes for repeated elements\n"
            "- Mobile: touch-scroll, reduced particles, lower resolution\n"
            "- Avatar easter egg: place the SkyyRose mascot hidden in scene"
        )

    def _build_task_prompt(self, task: str, **kwargs: Any) -> str:
        """Enrich with collection world context."""
        base = super()._build_task_prompt(task, **kwargs)
        collection = kwargs.get("collection")
        if collection:
            worlds = {
                "black_rose": "Bay Bridge night scene — Oakland, neon, fog, street luxury",
                "love_hurts": "Enchanted cathedral — rose dome, gothic, candlelight",
                "signature": "Golden Gate golden hour — SF, runway, fog through cables",
            }
            world_desc = worlds.get(collection.lower().replace(" ", "_"), "")
            if world_desc:
                base += f"\n\nTarget world: {collection} — {world_desc}\n"
        return base

    async def execute(self, task: str, **kwargs: Any) -> dict[str, Any]:
        """Build scene with multi-agent delegation when complex."""
        collection = kwargs.get("collection")
        if collection and "full" in task.lower():
            # Complex scene build: delegate to sub-agents
            agents: dict[str, AgentDefinition] = {
                "environment_artist": AgentDefinition(
                    model="sonnet",
                    tools=ToolProfile.WEB_BUILDER,
                    prompt=(
                        "You build the base Three.js environment: sky, ground, "
                        "lighting, fog, major landmarks. Write to the session "
                        "directory as scene_environment.json."
                    ),
                ),
                "product_placer": AgentDefinition(
                    model="haiku",
                    tools=["Read", "Write", "Glob"],
                    prompt=(
                        "You read the product catalog and place product hotspots "
                        "naturally within the 3D scene. Output product_hotspots.json "
                        "with 3D positions, rotations, and WooCommerce product IDs."
                    ),
                ),
                "fx_artist": AgentDefinition(
                    model="haiku",
                    tools=["Read", "Write"],
                    prompt=(
                        "You add atmospheric effects: particles, volumetric fog, "
                        "dynamic lighting, scroll-triggered animations. Output "
                        "scene_effects.json matching immersive-world.js format."
                    ),
                ),
            }
            result = await self._sdk_delegate(
                self._build_task_prompt(task, **kwargs),
                agents=agents,
                label="scene_build",
            )
            return {
                "success": result.success,
                "result": result.response,
                "agent": self.name,
                "execution_mode": "sdk_delegation",
                "metrics": result.metrics,
                "error": result.error,
            }

        # Simple scene edits: direct execution
        return await super().execute(task, **kwargs)


class SDKAvatarStylistAgent(SDKSubAgent):
    """SkyyRose avatar outfit stylist.

    Manages the Pixar-quality SkyyRose avatar — a little Black girl
    who serves as the brand mascot. This agent dresses her in any
    outfit from the catalog and generates the styled views.

    Pipeline:
        Avatar base → Outfit selection → FASHN try-on → 3D pose render
        → Sprite sheet generation → Scene placement

    The avatar appears as an easter egg in each immersive world.
    Finding all 3 = intro animation reveal.
    """

    name = "sdk_avatar_stylist"
    parent_type = CoreAgentType.IMAGERY
    description = "Dress SkyyRose avatar in outfits, generate styled poses"
    capabilities = [
        "outfit_change",
        "pose_render",
        "sprite_generate",
        "avatar_3d",
        "easter_egg_place",
        "lookbook_generate",
    ]
    sdk_tools = ToolProfile.IMAGERY + ["WebFetch", "Grep"]
    sdk_model = "sonnet"
    sdk_output_base = Path("data/sdk_sessions/immersive/avatar")

    def _sdk_default_prompt(self) -> str:
        return (
            "You are the SkyyRose Avatar Stylist — you dress and animate "
            "the brand mascot: a little Black girl, Pixar quality, full of "
            "personality and confidence.\n\n"
            "Avatar assets:\n"
            "- Reference: source-products/brand-assets/"
            "skyyrose-avatar-reference.jpeg\n"
            "- Mascot sprites: assets/images/mascot/"
            "skyyrose-mascot-*.png (7 poses + idle + fallback SVG)\n"
            "- Poses: idle, wave, dance, point, sit, peek, celebrate\n\n"
            "FASHN Try-On (for outfit changes):\n"
            "- Agent: agents/fashn_agent.py (FashnTryOnAgent)\n"
            "- API: https://api.fashn.ai/v1\n"
            "- Key: FASHN_API_KEY env var\n"
            "- Categories: tops, bottoms, outerwear, full_body\n"
            "- Output: generated_assets/tryon/\n\n"
            "Workflow for outfit change:\n"
            "1. Read get_product(sku) for target SKU details\n"
            "2. Get garment flat image via get_product(sku)['images']"
            "['packshot'] — never assume a literal filename pattern, the "
            "actual render may be named differently or be a hub-verified "
            "override.\n"
            "3. Use avatar reference as model image\n"
            "4. Call FASHN try-on: garment + avatar → styled avatar\n"
            "5. Generate sprite sheet (all 7 poses) in the new outfit\n"
            "6. Save to assets/images/mascot/styled/{sku}/ directory\n\n"
            "Easter egg system:\n"
            "- Avatar is HIDDEN in each immersive world scene\n"
            "- Black Rose: avatar peeks from behind bridge cable\n"
            "- Love Hurts: avatar sits inside the rose dome\n"
            "- Signature: avatar walks across Golden Gate\n"
            "- Find all 3 = intro animation with brand reveal\n\n"
            "Rules:\n"
            "- NEVER change the avatar's appearance (skin tone, hair, etc.)\n"
            "- ONLY change clothing/accessories from the catalog\n"
            "- Maintain Pixar quality — clean lines, vibrant, expressive\n"
            "- Each pose must be consistent with the outfit\n"
            "- Sprite dimensions: 256x384px per frame, transparent BG"
        )

    def _build_task_prompt(self, task: str, **kwargs: Any) -> str:
        """Enrich with outfit and pose context."""
        base = super()._build_task_prompt(task, **kwargs)
        sku = kwargs.get("sku")
        pose = kwargs.get("pose")
        if sku:
            base += (
                f"\n\nOutfit SKU: {sku}\n"
                "Read product catalog for this item, then get the "
                "garment flat image for FASHN try-on input."
            )
        if pose:
            base += f"\nTarget pose: {pose}\n"
        return base

    async def execute(self, task: str, **kwargs: Any) -> dict[str, Any]:
        """Execute with optional multi-agent delegation for full lookbook."""
        if "lookbook" in task.lower() or "all outfits" in task.lower():
            agents: dict[str, AgentDefinition] = {
                "catalog_reader": AgentDefinition(
                    model="haiku",
                    tools=["Read", "Glob", "Grep"],
                    prompt=(
                        "Read the product catalog with "
                        "python -m skyyrose.core.product --all and list "
                        "all SKUs with their garment categories "
                        "(catalog.garment_type_lock). Save to "
                        "session_dir/catalog_items.json."
                    ),
                ),
                "outfit_renderer": AgentDefinition(
                    model="sonnet",
                    tools=ToolProfile.IMAGERY + ["WebFetch"],
                    prompt=(
                        "For each outfit in catalog_items.json, render "
                        "the SkyyRose avatar wearing it using FASHN "
                        "try-on. Save renders to session_dir/lookbook/."
                    ),
                ),
            }
            result = await self._sdk_delegate(
                self._build_task_prompt(task, **kwargs),
                agents=agents,
                label="lookbook",
            )
            return {
                "success": result.success,
                "result": result.response,
                "agent": self.name,
                "execution_mode": "sdk_delegation",
                "metrics": result.metrics,
                "error": result.error,
            }

        return await super().execute(task, **kwargs)


__all__ = [
    "SDKGarment3DAgent",
    "SDKSceneBuilderAgent",
    "SDKAvatarStylistAgent",
]
