"""
Creative Operations Hub node functions.

Each node reads from CreativeOperationState, executes a specific creative
intent, and returns an updated state dict. Legacy provider paths fail closed before imports. Local copy and finalization
remain available to direct callers.
"""

from __future__ import annotations

import logging
import time

from skyyrose.core.product import get_product

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
    """Return existing SKU copy from the registry without generation or fallback facts.

    This is an existing-product reader, not a new-design ideation route. Missing
    authored descriptions fail closed. Missing SEO stays absent and named in gaps.
    Caller params and fashion_context never override the founder's record.
    """
    start = time.monotonic()
    sku = state.get("sku", "")
    try:
        if not isinstance(sku, str) or not sku.strip():
            raise ValueError("An existing product SKU is required")
        product = get_product(sku)
        content = product["content"]
        required = ("short_description", "description")
        missing = [
            f"content.{field}"
            for field in required
            if not content.get(field) or not content[field].get("value")
        ]
        if missing:
            raise ValueError(f"Authoritative product copy is absent: {', '.join(missing)}")
        if not product.get("name") or product["catalog"].get("price") is None:
            raise ValueError("Authoritative product name or price is absent")

        seo = content.get("seo_meta")
        copy_result = {
            "success": True,
            "sku": product["sku"],
            "product_name": product["name"],
            "short_description": content["short_description"]["value"],
            "long_description": content["description"]["value"],
            "meta_title": product["name"],
            "meta_description": seo["value"] if seo else None,
            "keywords": [],
            "price": product["catalog"]["price"],
            "gaps": list(dict.fromkeys([*product["gaps"], "copy.keywords"])),
            "content_sources": content,
            "authority": product["authority"],
            "provenance": product["provenance"],
        }
        return {
            "copy_result": copy_result,
            "stage_timings": {
                **state.get("stage_timings", {}),
                "product_copy": time.monotonic() - start,
            },
        }
    except Exception as exc:
        logger.exception("product_copy_node failed: %s", exc)
        return {
            "copy_result": {"success": False, "error": str(exc)},
            "status": "error",
            "error": f"product_copy failed: {exc}",
            "stage_timings": {
                **state.get("stage_timings", {}),
                "product_copy": time.monotonic() - start,
            },
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
