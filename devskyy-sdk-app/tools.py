"""In-process MCP tools for the SkyyRose commerce agent.

These run *inside* this Python process (not a subprocess). The Agent SDK's bundled CLI
calls back into them when Claude decides to use a tool. Each handler is a plain async
function that returns the MCP `CallToolResult` shape:

    {"content": [{"type": "text", "text": "..."}], "is_error": <bool, optional>}

Note the Python field is `is_error` (snake_case). The TypeScript SDK uses `isError`.

Three tools, each read-only:
- lookup_product   — a specific item, by SKU or name keyword
- list_collection  — browse a collection (products + its canon)
- collection_canon — the brand story/voice for a collection, WITHOUT listing products
"""

from __future__ import annotations

from typing import Any

from claude_agent_sdk import ToolAnnotations, create_sdk_mcp_server, tool

from catalog import (
    COLLECTIONS,
    Product,
    collection_meta,
    find_products,
    products_in_collection,
)


def _format_product(p: Product) -> str:
    """Render one product as a compact, model-readable line.

    Availability is the registry's own status (pre-order / available / unpublished);
    the registry holds no stock counts, so none are ever shown.
    """
    sizes = ", ".join(p.sizes)
    return (
        f"{p.sku} — {p.name} ({p.collection}) | ${p.price_usd:.2f} | {p.availability} | "
        f"sizes: {sizes}\n    {p.description}"
    )


@tool(
    "lookup_product",
    "Look up SkyyRose products by SKU (e.g. 'br-001') or by name keyword (e.g. 'rose crewneck'). "
    "Returns matching products with price, availability (pre-order / available / unpublished), "
    "sizes, and description, straight from the product registry.",
    {"query": str},
    annotations=ToolAnnotations(readOnlyHint=True),  # read-only -> safe to batch in parallel
)
async def lookup_product(args: dict[str, Any]) -> dict[str, Any]:
    """Search the catalog. Returns a not-found result (not an error) when nothing matches."""
    query = str(args.get("query", "")).strip()
    if not query:
        # Empty input is a usage error -> mark is_error so Claude asks the user to refine.
        return {
            "content": [
                {"type": "text", "text": "No query provided. Pass a SKU or a name keyword."}
            ],
            "is_error": True,
        }

    matches = find_products(query)
    if not matches:
        # A clean "no results" is normal data, NOT an error: Claude should relay it, not retry.
        return {
            "content": [{"type": "text", "text": f"No products matched '{query}'."}],
        }

    body = "\n".join(_format_product(p) for p in matches)
    header = f"{len(matches)} product(s) matched '{query}':"
    return {"content": [{"type": "text", "text": f"{header}\n{body}"}]}


@tool(
    "list_collection",
    "List every SkyyRose product in a collection, with the collection's canon. Valid "
    "collections: Signature, Black Rose, Love Hurts, Kids Capsule.",
    {"collection": str},
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def list_collection(args: dict[str, Any]) -> dict[str, Any]:
    """List products for a named collection, or report the valid names when given a bad one."""
    collection = str(args.get("collection", "")).strip()
    valid = ", ".join(COLLECTIONS)

    if not collection:
        return {
            "content": [{"type": "text", "text": f"No collection provided. Valid: {valid}."}],
            "is_error": True,
        }

    resolved = collection_meta(collection)
    if resolved is None:
        return {
            "content": [
                {"type": "text", "text": f"'{collection}' is not a collection. Valid: {valid}."}
            ],
            "is_error": True,
        }

    name, meta = resolved
    products = products_in_collection(name)
    body = "\n".join(_format_product(p) for p in products) or "    (no products listed yet)"
    header = f"{name} (accent {meta.accent}) — {meta.story}\n{len(products)} product(s):"
    return {"content": [{"type": "text", "text": f"{header}\n{body}"}]}


@tool(
    "collection_canon",
    "Get the brand canon for a single collection — its story line, accent color, and the "
    "founder story it comes from — "
    "WITHOUT listing products. Use this when the user asks what a collection is about, its "
    "story, or its vibe. Valid: Signature, Black Rose, Love Hurts, Kids Capsule.",
    {"collection": str},
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def collection_canon(args: dict[str, Any]) -> dict[str, Any]:
    """Return one collection's grounded canon so the agent never paraphrases it from memory."""
    collection = str(args.get("collection", "")).strip()
    valid = ", ".join(COLLECTIONS)

    resolved = collection_meta(collection) if collection else None
    if resolved is None:
        return {
            "content": [
                {"type": "text", "text": f"'{collection}' is not a collection. Valid: {valid}."}
            ],
            "is_error": True,
        }

    name, meta = resolved
    text = f"{name}\n  accent : {meta.accent}\n  story  : {meta.story}\n  source : {meta.story_ref}"
    return {"content": [{"type": "text", "text": text}]}


# Wrap all three tools in one in-process MCP server. The key you mount this under in
# ClaudeAgentOptions.mcp_servers becomes the {server_name} segment of the fully
# qualified tool name: mcp__{server_name}__{tool_name}.
catalog_server = create_sdk_mcp_server(
    name="catalog",
    version="1.1.0",
    tools=[lookup_product, list_collection, collection_canon],
)
