"""
Creative Operations Hub node functions.

Each node reads from CreativeOperationState, executes a specific creative
intent, and returns an updated state dict. Legacy provider paths fail closed before imports. Local copy and finalization
remain available to direct callers.

"Luxury Grows from Concrete."
"""

from __future__ import annotations

import logging
import time

logger = logging.getLogger(__name__)


def unsupported_paid_route(state: dict, route: str) -> dict:
    """Caller-supplied approval fields never confer provider authority."""
    return {
        "status": "error",
        "paid_action_status": "UNSUPPORTED",
        "error_code": "PAID_GOVERNOR_REQUIRED",
        "error": f"Legacy creative route {route} is disabled: no governed provider adapter",
        "operation_id": state.get("operation_id", ""),
        "provider_called": False,
        "resumable": False,
    }


def entry_node(state: dict) -> dict:
    """Deny the legacy provider path before imports or external work."""
    return unsupported_paid_route(state, "entry_node")


def product_render_node(state: dict) -> dict:
    """Deny the legacy provider path before imports or external work."""
    return unsupported_paid_route(state, "product_render_node")


def three_d_model_node(state: dict) -> dict:
    """Deny the legacy provider path before imports or external work."""
    return unsupported_paid_route(state, "three_d_model_node")


def social_pack_node(state: dict) -> dict:
    """Deny the legacy provider path before imports or external work."""
    return unsupported_paid_route(state, "social_pack_node")


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
        dna = fashion_context.get("collection_dna", "Luxury Grows from Concrete.")
        _ = fashion_context.get("color_palette", [])

        short_description = (
            f"Elevate your look with the {product_name}. "
            f"{collection_display} collection — {dna.split('.')[0] if dna else 'luxury streetwear'}. "
            f"'Luxury Grows from Concrete.' "
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
            "Luxury Grows from Concrete",
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
    """Deny the legacy provider path before imports or external work."""
    return unsupported_paid_route(state, "character_node")


def scene_composite_node(state: dict) -> dict:
    """Deny the legacy provider path before imports or external work."""
    return unsupported_paid_route(state, "scene_composite_node")


def design_ideation_node(state: dict) -> dict:
    """Deny the legacy provider path before imports or external work."""
    return unsupported_paid_route(state, "design_ideation_node")


def collection_plan_node(state: dict) -> dict:
    """Deny the legacy provider path before imports or external work."""
    return unsupported_paid_route(state, "collection_plan_node")


def tripo_generate_node(state: dict) -> dict:
    """Deny the legacy provider path before imports or external work."""
    return unsupported_paid_route(state, "tripo_generate_node")


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
