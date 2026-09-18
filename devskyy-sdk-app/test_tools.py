"""Offline checks for the catalog tools and agent wiring.

These run WITHOUT contacting the Claude API — they call the tool handlers directly and
construct the agent options, which is enough to catch import errors, schema typos, and
broken handler logic for free. Run with:  python test_tools.py
(or `pytest test_tools.py`).

We do NOT call query() here: that spawns the agent and makes a billed API call.

The catalog is the product registry, so the values asserted here are registry facts
(br-001 is the BLACK Rose Crewneck at $35; lh-006 is the white Love Hurts Joggers).
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from catalog import (
    AVAILABLE,
    PRE_ORDER,
    CatalogUnavailableError,
    find_products,
    load_products,
    products_in_collection,
)
from tools import catalog_server, collection_canon, list_collection, lookup_product

# `@tool` returns an SdkMcpTool dataclass, not the raw function. The async handler is `.handler`;
# that's what the SDK invokes by tool name. We call it directly here to test the logic offline.
lookup_handler = lookup_product.handler
list_handler = list_collection.handler
canon_handler = collection_canon.handler


def _text(result: dict) -> str:
    """Pull the concatenated text out of a tool result's content blocks."""
    return "\n".join(b["text"] for b in result["content"] if b["type"] == "text")


async def _checks() -> None:
    # --- catalog layer (registry facts, never demo data) ----------------------
    (br_001,) = find_products("br-001")
    assert br_001.name == "BLACK Rose Crewneck", br_001
    assert br_001.collection == "Black Rose" and br_001.price_usd == 35.0, br_001
    assert br_001.sizes == ("S", "M", "L", "XL", "2XL", "3XL"), br_001
    assert br_001.availability == AVAILABLE, br_001

    (lh_006,) = find_products("lh-006")
    assert lh_006.name == "Love Hurts Joggers (White)", lh_006
    assert "Fannie" not in lh_006.description, "retired side-store copy must not leak in"

    (sg_001,) = find_products("sg-001")
    assert sg_001.availability == PRE_ORDER, "catalog.is_preorder=1 must surface as pre-order"

    assert find_products("rose"), "keyword 'rose' should match at least one product"
    assert find_products("nope-404") == [], "unknown query returns empty list"
    for fabricated in ("lh-009", "kc-003", "sg-004"):
        assert find_products(fabricated) == [], f"{fabricated} is not a registry SKU"
    assert products_in_collection("Love Hurts"), "Love Hurts should have products"
    assert products_in_collection("kids capsule"), "Kids Capsule should have products"
    assert products_in_collection("Nonexistent") == [], "bad collection returns empty list"

    # --- fail closed: no registry means no catalog, not an empty one --------------
    try:
        load_products(Path("/nonexistent/logo-registry.json"))
    except CatalogUnavailableError as exc:
        assert "Product registry not found" in str(exc)
    else:
        raise AssertionError("a missing registry must raise, never yield an empty catalog")

    # --- lookup_product tool -------------------------------------------------
    hit = await lookup_handler({"query": "br-001"})
    hit_text = _text(hit)
    assert "br-001" in hit_text and not hit.get("is_error"), hit
    assert "BLACK Rose Crewneck" in hit_text, "name must be the registry name"
    assert "$35.00" in hit_text, "price must be quoted exactly from the registry"
    assert "available" in hit_text and "SOLD OUT" not in hit_text and "in stock" not in hit_text

    pre = await lookup_handler({"query": "sg-001"})
    assert "pre-order" in _text(pre), pre

    miss = await lookup_handler({"query": "zzz"})
    assert "No products matched" in _text(miss), miss
    assert not miss.get("is_error"), "a clean no-match is data, not an error"

    empty = await lookup_handler({"query": "   "})
    assert empty.get("is_error") is True, "empty query is a usage error"

    # --- list_collection tool ------------------------------------------------
    coll = await list_handler({"collection": "love hurts"})  # case-insensitive
    coll_text = _text(coll)
    assert "Love Hurts" in coll_text and not coll.get("is_error"), coll
    assert "lh-006" in coll_text, "registry products must list under their collection"
    assert "#DC143C" in coll_text, "list output should surface the collection accent"
    assert (
        "told from the Beast's perspective" in coll_text
    ), "list output should carry the registry story"

    bad = await list_handler({"collection": "Sweaters"})
    assert bad.get("is_error") is True, "invalid collection is an error"
    assert "Valid:" in _text(bad), "should list valid collections"

    # --- collection_canon tool -----------------------------------------------
    canon = await canon_handler({"collection": "Black Rose"})
    canon_text = _text(canon)
    assert not canon.get("is_error"), canon
    assert (
        "Defining beauty through the color black." in canon_text
    ), "Black Rose story from the registry"
    assert (
        "docs/brand/collection-stories.md#black-rose" in canon_text
    ), "canon should name its source"
    assert "#C0C0C0" in canon_text, "canon should include the accent token"
    # Canon must NOT cross-wire: Love Hurts' line must never appear under Black Rose.
    assert "Beast" not in canon_text, "collection canon must not cross-wire"

    canon_bad = await canon_handler({"collection": ""})
    assert canon_bad.get("is_error") is True, "empty collection is a usage error"

    # --- server build --------------------------------------------------------
    assert catalog_server is not None, "create_sdk_mcp_server must return a server object"

    print("All offline tool checks passed.")


def test_offline_tool_checks() -> None:
    """pytest entry point; `python test_tools.py` runs the same checks."""
    asyncio.run(_checks())


if __name__ == "__main__":
    asyncio.run(_checks())
