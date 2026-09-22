"""
Creative Operations Hub node functions.

Each node reads from CreativeOperationState, executes a specific creative
intent, and returns an updated state dict. All external calls are wrapped
in try/except — nodes never raise.

""
"""

from __future__ import annotations

import logging
import time

logger = logging.getLogger(__name__)


def entry_node(state: dict) -> dict:
    """Validate intent, build FashionContext, optionally enhance prompt.

    Sets fashion_context in state for downstream nodes to use.
    Returns error state if intent is unrecognized.
    """
    start = time.monotonic()
    intent = state.get("intent", "")
    sku = state.get("sku", "")
    params = state.get("params", {})

    try:
        from .state import CreativeIntent

        valid_intents = {e.value for e in CreativeIntent}
        if intent not in valid_intents:
            return {
                "status": "error",
                "error": f"Unknown intent: {intent!r}. Valid intents: {sorted(valid_intents)}",
                "stage_timings": {
                    **state.get("stage_timings", {}),
                    "entry": time.monotonic() - start,
                },
            }

        # Build FashionContext if we have enough info
        fashion_context: dict | None = None
        if sku or params.get("garment_type") or params.get("collection"):
            try:
                from skyyrose.elite_studio.fashion.context import FashionContextBuilder

                builder = FashionContextBuilder()
                if sku:
                    ctx = builder.build_from_product_catalog(sku)
                else:
                    ctx = builder.build(
                        garment_type=params.get("garment_type", ""),
                        collection=params.get("collection", ""),
                        season=params.get("season", "FW26"),
                    )
                fashion_context = {
                    "garment_type": ctx.garment_type,
                    "fabric": ctx.fabric,
                    "collection_dna": ctx.collection_dna,
                    "season": ctx.season,
                    "photography_style": ctx.photography_style,
                    "color_palette": list(ctx.color_palette),
                    "styling_notes": ctx.styling_notes,
                    "size_range": ctx.size_range,
                    "rendering_spec": ctx.rendering_spec,
                    "trend_alignment": list(ctx.trend_alignment),
                }
            except Exception as exc:
                logger.warning("FashionContext build failed (non-fatal): %s", exc)

        elapsed = time.monotonic() - start
        return {
            "fashion_context": fashion_context,
            "stage_timings": {**state.get("stage_timings", {}), "entry": elapsed},
        }

    except Exception as exc:
        logger.exception("entry_node failed: %s", exc)
        return {
            "status": "error",
            "error": f"entry_node failed: {exc}",
            "stage_timings": {**state.get("stage_timings", {}), "entry": time.monotonic() - start},
        }


def product_render_node(state: dict) -> dict:
    """Run the LangGraph Elite Studio pipeline for a single SKU render."""
    start = time.monotonic()
    sku = state.get("sku", "")
    params = state.get("params", {})
    view = params.get("view", "front")

    try:
        from skyyrose.elite_studio.graph.builder import GraphConfig
        from skyyrose.elite_studio.graph.runner import run_single

        config = GraphConfig(
            enable_compositor=params.get("enable_compositor", False),
            enable_tryon=params.get("enable_tryon", False),
        )
        result = run_single(sku=sku, view=view, config=config)
        render_result = {
            "success": result.status == "success",
            "sku": result.sku,
            "view": result.view,
            "status": result.status,
            "output_path": result.output_path,
            "error": result.error,
        }
        elapsed = time.monotonic() - start
        return {
            "render_result": render_result,
            "stage_timings": {**state.get("stage_timings", {}), "product_render": elapsed},
        }

    except Exception as exc:
        logger.exception("product_render_node failed: %s", exc)
        elapsed = time.monotonic() - start
        return {
            "render_result": {"success": False, "error": str(exc)},
            "status": "error",
            "error": f"product_render failed: {exc}",
            "stage_timings": {**state.get("stage_timings", {}), "product_render": elapsed},
        }


def three_d_model_node(state: dict) -> dict:
    """Generate a 3D model from the product render.

    Phase B1: routes through SDKGarment3DAgent first when state.params.use_sdk_agent
    is set, falling back to ThreeDGenerationPipeline. The SDK agent's prompt (in
    agents/claude_sdk/domain_agents/immersive.py) declares a write convention of
    `generated_assets/3d/{sku}/`; after execute we look there for *.glb / *.usdz
    artifacts. If none found, we fall back to the deterministic pipeline so the
    LangGraph state machine never silently produces an empty 3D result.

    State output keys (Phase B1 expansion):
      - model_3d_result: legacy summary dict (kept for backwards compat)
      - model_output_path: local GLB path (primary 3D artifact)
      - glb_url: hosted GLB URL when available
      - usdz_url: hosted USDZ URL when available
    """
    import asyncio
    from pathlib import Path

    start = time.monotonic()
    params = state.get("params", {})
    image_path = params.get("image_path", "")
    sku = state.get("sku") or params.get("sku") or ""
    collection = params.get("collection", "")
    prompt = params.get("prompt", "")
    use_sdk_agent = bool(params.get("use_sdk_agent", False))

    sdk_result_payload: dict | None = None
    sdk_glb_path: str | None = None
    sdk_usdz_path: str | None = None

    # ---- Stage 1: Try SDK agent path (opt-in) ----
    if use_sdk_agent and sku:
        try:
            from agents.claude_sdk.domain_agents.immersive import SDKGarment3DAgent

            sdk_agent = SDKGarment3DAgent()
            task = (
                f"Generate a production-quality 3D garment model for SKU {sku}. "
                f"Use the source image at {image_path}. Export GLB (web) + USDZ (AR) "
                f"to generated_assets/3d/{sku}/."
            )
            sdk_result_payload = asyncio.run(
                sdk_agent.execute(
                    task,
                    sku=sku,
                    collection=collection,
                    image_path=image_path,
                    prompt=prompt,
                )
            )

            # Honest handshake: read the agent's declared output dir
            sdk_output_dir = Path(f"generated_assets/3d/{sku}")
            if sdk_result_payload.get("success") and sdk_output_dir.is_dir():
                glbs = sorted(sdk_output_dir.glob("*.glb"))
                usdzs = sorted(sdk_output_dir.glob("*.usdz"))
                if glbs:
                    sdk_glb_path = str(glbs[-1])  # newest by sort order
                if usdzs:
                    sdk_usdz_path = str(usdzs[-1])
        except Exception as exc:
            logger.warning("SDK 3D path failed, falling back to pipeline: %s", exc)
            sdk_result_payload = {"success": False, "error": str(exc)}

    # ---- Stage 2: SDK succeeded with concrete artifacts ----
    if sdk_glb_path:
        elapsed = time.monotonic() - start
        return {
            "model_3d_result": {
                "success": True,
                "model_path": sdk_glb_path,
                "execution_mode": "sdk_agent",
                "session_dir": (
                    sdk_result_payload.get("session_dir") if sdk_result_payload else None
                ),
                "error": "",
            },
            "model_output_path": sdk_glb_path,
            "glb_url": sdk_glb_path,
            "usdz_url": sdk_usdz_path,
            "stage_timings": {**state.get("stage_timings", {}), "three_d_model": elapsed},
        }

    # ---- Stage 3: Deterministic pipeline (fallback or default) ----
    try:
        from ai_3d.generation_pipeline import ThreeDGenerationPipeline

        pipeline = ThreeDGenerationPipeline()
        result = asyncio.run(
            pipeline.generate_from_image(
                image_path=image_path,
                prompt=prompt,
            )
        )
        model_path = getattr(result, "model_path", "") or ""
        elapsed = time.monotonic() - start
        return {
            "model_3d_result": {
                "success": result.success,
                "model_path": model_path,
                "execution_mode": "pipeline_fallback" if use_sdk_agent else "pipeline",
                "error": getattr(result, "error", ""),
            },
            "model_output_path": model_path,
            "glb_url": model_path if model_path.endswith(".glb") else None,
            "usdz_url": model_path if model_path.endswith(".usdz") else None,
            "stage_timings": {**state.get("stage_timings", {}), "three_d_model": elapsed},
        }

    except Exception as exc:
        logger.exception("three_d_model_node failed: %s", exc)
        elapsed = time.monotonic() - start
        return {
            "model_3d_result": {"success": False, "error": str(exc)},
            "model_output_path": None,
            "glb_url": None,
            "usdz_url": None,
            "status": "error",
            "error": f"3d_model failed: {exc}",
            "stage_timings": {**state.get("stage_timings", {}), "three_d_model": elapsed},
        }


def social_pack_node(state: dict) -> dict:
    """Generate a multi-platform social media campaign via SocialMediaAgent."""
    start = time.monotonic()
    params = state.get("params", {})
    fashion_context = state.get("fashion_context") or {}
    collection = params.get("collection", "") or _extract_collection(fashion_context)

    try:
        from agents.social_media_agent import SocialMediaAgent

        agent = SocialMediaAgent()
        campaign = agent.generate_campaign(
            collection=collection,
            campaign_name=params.get("campaign_name", "Collection Drop"),
            max_products=params.get("max_products", 5),
            platforms=params.get("platforms"),
        )
        social_result = {
            "success": True,
            "campaign_name": campaign.name,
            "collection": campaign.collection,
            "post_count": len(campaign.posts) if hasattr(campaign, "posts") else 0,
        }
        elapsed = time.monotonic() - start
        return {
            "social_result": social_result,
            "stage_timings": {**state.get("stage_timings", {}), "social_pack": elapsed},
        }

    except Exception as exc:
        logger.exception("social_pack_node failed: %s", exc)
        elapsed = time.monotonic() - start
        return {
            "social_result": {"success": False, "error": str(exc)},
            "status": "error",
            "error": f"social_pack failed: {exc}",
            "stage_timings": {**state.get("stage_timings", {}), "social_pack": elapsed},
        }


def product_copy_node(state: dict) -> dict:
    """Generate SEO-optimized product copy using LLM."""
    start = time.monotonic()
    params = state.get("params", {})
    sku = state.get("sku", "")
    fashion_context = state.get("fashion_context") or {}

    try:
        garment_type = params.get("garment_type") or fashion_context.get("garment_type", "product")
        collection = params.get("collection") or _extract_collection(fashion_context)
        product_name = params.get("product_name", f"SkyyRose {garment_type.title()}")
        price = params.get("price", 0)

        collection_display = collection.replace("-", " ").title() if collection else "SkyyRose"
        dna = fashion_context.get("collection_dna", "")
        _ = fashion_context.get("color_palette", [])

        short_description = (
            f"Elevate your look with the {product_name}. "
            f"{collection_display} collection — {dna.split('.')[0] if dna else 'luxury streetwear'}. "
            f"'' "
        )

        long_description = (
            f"The {product_name} is the cornerstone of SkyyRose's {collection_display} collection. "
            f"Crafted with premium {fashion_context.get('fabric', 'materials')}, "
            f"this piece embodies the SkyyRose ethos: luxury grown from Oakland's concrete foundations. "
            f"{dna} "
            f"Available in sizes {fashion_context.get('size_range', 'S–3XL')}. "
            f"{'Pre-order now — limited edition.' if params.get('is_preorder') else 'Shop now.'}"
        )

        meta_title = f"{product_name} — SkyyRose {collection_display} | Luxury Streetwear"
        meta_description = (
            f"Shop the {product_name} from SkyyRose's {collection_display} collection. "
            f"Premium luxury streetwear from Oakland. "
            f"{'Pre-order available.' if params.get('is_preorder') else 'Free shipping on orders $100+.'}"
        )

        keywords = [
            "SkyyRose",
            "luxury streetwear",
            f"{collection_display} collection",
            garment_type,
            "Oakland fashion",
            "premium streetwear",
            "",
        ]
        if sku:
            keywords.append(sku)

        copy_result = {
            "success": True,
            "sku": sku,
            "product_name": product_name,
            "short_description": short_description.strip(),
            "long_description": long_description.strip(),
            "meta_title": meta_title[:70],
            "meta_description": meta_description[:160],
            "keywords": keywords,
            "price": price,
        }
        elapsed = time.monotonic() - start
        return {
            "copy_result": copy_result,
            "stage_timings": {**state.get("stage_timings", {}), "product_copy": elapsed},
        }

    except Exception as exc:
        logger.exception("product_copy_node failed: %s", exc)
        elapsed = time.monotonic() - start
        return {
            "copy_result": {"success": False, "error": str(exc)},
            "status": "error",
            "error": f"product_copy failed: {exc}",
            "stage_timings": {**state.get("stage_timings", {}), "product_copy": elapsed},
        }


def character_node(state: dict) -> dict:
    """Generate a character sheet via CharacterCreationAgent."""
    start = time.monotonic()
    params = state.get("params", {})

    try:
        from skyyrose.elite_studio.character.agent import CharacterCreationAgent
        from skyyrose.elite_studio.character.models import CharacterSpec

        agent = CharacterCreationAgent()

        # Use Rosie (canonical mascot) if no custom spec provided
        if not params.get("character_name"):
            sheet = agent.create_skyyrose_rosie()
        else:
            spec = CharacterSpec(
                name=params.get("character_name", "Custom Character"),
                style=params.get("style", "realistic"),
                body_description=params.get("body_description", ""),
                face_features=params.get("face_features", ""),
                outfit_base=params.get("outfit_base", "SkyyRose hoodie and joggers"),
                brand_elements=tuple(params.get("brand_elements", ["SkyyRose rose motif"])),
                reference_paths=tuple(params.get("reference_paths", [])),
            )
            sheet = agent.create_sheet(spec)

        character_result = {
            "success": sheet.success,
            "character_name": sheet.spec.name,
            "front_view_prompt": sheet.front_view_prompt,
            "side_view_prompt": sheet.side_view_prompt,
            "back_view_prompt": sheet.back_view_prompt,
            "expression_grid_prompt": sheet.expression_grid_prompt,
            "sprite_description": sheet.sprite_description,
            "error": sheet.error,
        }
        elapsed = time.monotonic() - start
        return {
            "character_result": character_result,
            "stage_timings": {**state.get("stage_timings", {}), "character": elapsed},
        }

    except Exception as exc:
        logger.exception("character_node failed: %s", exc)
        elapsed = time.monotonic() - start
        return {
            "character_result": {"success": False, "error": str(exc)},
            "status": "error",
            "error": f"character_sheet failed: {exc}",
            "stage_timings": {**state.get("stage_timings", {}), "character": elapsed},
        }


def scene_composite_node(state: dict) -> dict:
    """Run scene compositing via CompositorAgent."""
    start = time.monotonic()
    params = state.get("params", {})
    sku = state.get("sku", "")

    try:
        from skyyrose.elite_studio.agents.compositor_agent import CompositorAgent

        agent = CompositorAgent()
        scene_image_path = params.get("scene_image_path", "")
        model_image_path = params.get("model_image_path") or scene_image_path
        if not scene_image_path or not model_image_path:
            raise RuntimeError(
                "scene_composite_node requires scene_image_path and model_image_path in params"
            )
        result = agent.composite(
            sku=sku,
            scene_image_path=scene_image_path,
            model_image_path=model_image_path,
            collection=params.get("collection", ""),
            scene_name=params.get("scene_name", ""),
            output_dir=params.get("output_dir") or "renders/output/compositor",
        )
        composite_result = {
            "success": result.success,
            "output_path": result.output_path,
            "qa_status": result.qa_status,
            "collection": result.collection,
            "error": result.error,
        }
        elapsed = time.monotonic() - start
        return {
            "composite_result": composite_result,
            "stage_timings": {**state.get("stage_timings", {}), "scene_composite": elapsed},
        }

    except Exception as exc:
        logger.exception("scene_composite_node failed: %s", exc)
        elapsed = time.monotonic() - start
        return {
            "composite_result": {"success": False, "error": str(exc)},
            "status": "error",
            "error": f"scene_composite failed: {exc}",
            "stage_timings": {**state.get("stage_timings", {}), "scene_composite": elapsed},
        }


def design_ideation_node(state: dict) -> dict:
    """Generate design concepts via DesignIdeationAgent."""
    start = time.monotonic()
    params = state.get("params", {})
    fashion_context = state.get("fashion_context") or {}

    try:
        from skyyrose.elite_studio.fashion.design.ideation import DesignBrief, DesignIdeationAgent

        agent = DesignIdeationAgent()
        brief = DesignBrief(
            collection=params.get("collection") or _extract_collection(fashion_context),
            garment_type=params.get("garment_type")
            or fashion_context.get("garment_type", "hoodie"),
            season=params.get("season", "FW26"),
            target_price_usd=float(params.get("target_price_usd", 65.0)),
            design_intent=params.get("design_intent", "Premium SkyyRose luxury streetwear"),
            colorway_preference=params.get("colorway_preference", ""),
            reference_tags=tuple(params.get("reference_tags", [])),
        )
        concept = agent.generate_concept(brief)
        design_result = {
            "success": True,
            "concept_id": concept.concept_id,
            "concept_name": concept.concept_name,
            "headline_description": concept.headline_description,
            "full_description": concept.full_description,
            "colorway_hex": list(concept.colorway_hex),
            "key_design_elements": list(concept.key_design_elements),
            "fabric_specification": concept.fabric_specification,
            "generation_prompt": concept.generation_prompt,
        }
        elapsed = time.monotonic() - start
        return {
            "design_result": design_result,
            "stage_timings": {**state.get("stage_timings", {}), "design_ideation": elapsed},
        }

    except Exception as exc:
        logger.exception("design_ideation_node failed: %s", exc)
        elapsed = time.monotonic() - start
        return {
            "design_result": {"success": False, "error": str(exc)},
            "status": "error",
            "error": f"design_ideation failed: {exc}",
            "stage_timings": {**state.get("stage_timings", {}), "design_ideation": elapsed},
        }


def collection_plan_node(state: dict) -> dict:
    """Generate a collection plan via CollectionPlanner."""
    start = time.monotonic()
    params = state.get("params", {})
    fashion_context = state.get("fashion_context") or {}

    try:
        from skyyrose.elite_studio.fashion.design.collection_planner import CollectionPlanner

        planner = CollectionPlanner()
        collection = (
            params.get("collection") or _extract_collection(fashion_context) or "black-rose"
        )
        plan = planner.plan_collection(
            collection=collection,
            season=params.get("season", "FW26"),
            theme=params.get("theme", ""),
            target_skus_count=int(params.get("target_skus_count", 8)),
        )
        collection_plan_result = {
            "success": True,
            "plan_id": plan.plan_id,
            "collection": plan.collection,
            "season": plan.season,
            "theme": plan.theme,
            "product_categories": list(plan.product_categories),
            "hero_pieces": list(plan.hero_pieces),
            "colorway_strategy": plan.colorway_strategy,
            "pricing_strategy": plan.pricing_strategy,
            "trend_hooks": list(plan.trend_hooks),
            "launch_sequence": list(plan.launch_sequence),
            "editorial_direction": plan.editorial_direction,
        }
        elapsed = time.monotonic() - start
        return {
            "collection_plan_result": collection_plan_result,
            "stage_timings": {**state.get("stage_timings", {}), "collection_plan": elapsed},
        }

    except Exception as exc:
        logger.exception("collection_plan_node failed: %s", exc)
        elapsed = time.monotonic() - start
        return {
            "collection_plan_result": {"success": False, "error": str(exc)},
            "status": "error",
            "error": f"collection_plan failed: {exc}",
            "stage_timings": {**state.get("stage_timings", {}), "collection_plan": elapsed},
        }


def tripo_generate_node(state: dict) -> dict:
    """Generate multiview product imagery via Tripo3D for a single SKU.

    Expects params to contain:
      - image_path (str): absolute path to source garment flat image

    STOP-AND-SHOW confirmation must be obtained before invoking this node.
    Use scripts/tripo_dispatch.py which enforces the gate at the dispatch layer.

    Returns tripo_result matching render_result shape plus a views list.
    """
    import asyncio

    start = time.monotonic()
    sku = state.get("sku", "")
    params = state.get("params", {})
    image_path = params.get("image_path", "")

    if not image_path:
        elapsed = time.monotonic() - start
        return {
            "tripo_result": {"success": False, "error": "params.image_path is required"},
            "status": "error",
            "error": "tripo_generate_node requires params.image_path",
            "stage_timings": {**state.get("stage_timings", {}), "tripo_generate": elapsed},
        }

    try:
        from skyyrose.elite_studio.agents.tripo_agent import TripoGenerateAgent

        agent = TripoGenerateAgent()
        result = asyncio.run(agent.generate_multiview(sku=sku, image_path=image_path))

        tripo_result = {
            "success": result.success,
            "sku": result.sku,
            "view": "multiview",
            "status": "success" if result.success else "error",
            "output_path": result.output_dir,
            "views": result.views,
            "task_id": result.task_id,
            "credits_used": result.credits_used,
            "error": result.error,
        }
        elapsed = time.monotonic() - start
        return {
            "tripo_result": tripo_result,
            "stage_timings": {**state.get("stage_timings", {}), "tripo_generate": elapsed},
        }

    except Exception as exc:
        logger.exception("tripo_generate_node failed: %s", exc)
        elapsed = time.monotonic() - start
        return {
            "tripo_result": {"success": False, "error": str(exc)},
            "status": "error",
            "error": f"tripo_generate failed: {exc}",
            "stage_timings": {**state.get("stage_timings", {}), "tripo_generate": elapsed},
        }


def finalize_node(state: dict) -> dict:
    """Set final status and log stage timings."""
    if state.get("status") == "error":
        return {}  # preserve error state as-is

    return {"status": "success"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _extract_collection(fashion_context: dict) -> str:
    """Extract collection slug from fashion context data."""
    dna = fashion_context.get("collection_dna", "")
    if "Black Rose" in dna:
        return "black-rose"
    if "Love Hurts" in dna:
        return "love-hurts"
    if "Signature" in dna:
        return "signature"
    if "Kids Capsule" in dna:
        return "kids-capsule"
    return ""
