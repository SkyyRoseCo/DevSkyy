"""
Creative Operations Hub LangGraph router.

Builds the unified StateGraph for all 14 creative intents.

The graph supports optional PostgreSQL checkpointing via
`get_creative_graph_async()`. When a Postgres `DATABASE_URL` is
configured, the graph persists state after every node — letting a
failed run (e.g., a Tripo3D 5xx) resume from the last successful node
instead of silently losing the whole pipeline. Without `DATABASE_URL`,
the graph runs without checkpointing (the original behaviour).

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from langgraph.graph import END, StateGraph

if TYPE_CHECKING:
    from langgraph.checkpoint.base import BaseCheckpointSaver

from .edges import (
    CHARACTER,
    COLLECTION_PLAN,
    DESIGN_IDEATION,
    ENTRY,
    FINALIZE,
    PRODUCT_COPY,
    PRODUCT_RENDER,
    SCENE_COMPOSITE,
    SOCIAL_PACK,
    THREE_D_MODEL,
    TRIPO_GENERATE,
    after_any,
    after_render,
    route_intent,
)
from .nodes import (
    character_node,
    collection_plan_node,
    design_ideation_node,
    entry_node,
    finalize_node,
    product_copy_node,
    product_render_node,
    scene_composite_node,
    social_pack_node,
    three_d_model_node,
    tripo_generate_node,
)
from .state import CreativeOperationState


def build_creative_graph(checkpointer: BaseCheckpointSaver | None = None):  # type: ignore[return]
    """Build and compile the unified creative operations graph.

    Args:
        checkpointer: Optional LangGraph checkpoint saver. When provided,
            the graph persists state after every node so failed runs can
            resume. Pass `None` (default) for the legacy in-memory mode.

    Topology:
        entry
          → route_intent (conditional)
            → product_render → [after_render: social_pack | finalize]
            → three_d_model  → finalize
            → social_pack    → finalize
            → product_copy   → finalize
            → character      → finalize
            → scene_composite → finalize
            → design_ideation → finalize
            → collection_plan → finalize
          → finalize → END

    Returns:
        Compiled LangGraph StateGraph ready for invocation.
    """
    graph = StateGraph(CreativeOperationState)

    # Register all nodes
    graph.add_node(ENTRY, entry_node)
    graph.add_node(PRODUCT_RENDER, product_render_node)
    graph.add_node(THREE_D_MODEL, three_d_model_node)
    graph.add_node(SOCIAL_PACK, social_pack_node)
    graph.add_node(PRODUCT_COPY, product_copy_node)
    graph.add_node(CHARACTER, character_node)
    graph.add_node(SCENE_COMPOSITE, scene_composite_node)
    graph.add_node(DESIGN_IDEATION, design_ideation_node)
    graph.add_node(COLLECTION_PLAN, collection_plan_node)
    graph.add_node(TRIPO_GENERATE, tripo_generate_node)
    graph.add_node(FINALIZE, finalize_node)

    # Entry point
    graph.set_entry_point(ENTRY)

    # entry → route_intent (conditional dispatch to all specialized nodes)
    graph.add_conditional_edges(
        ENTRY,
        route_intent,
        {
            PRODUCT_RENDER: PRODUCT_RENDER,
            THREE_D_MODEL: THREE_D_MODEL,
            SOCIAL_PACK: SOCIAL_PACK,
            PRODUCT_COPY: PRODUCT_COPY,
            CHARACTER: CHARACTER,
            SCENE_COMPOSITE: SCENE_COMPOSITE,
            DESIGN_IDEATION: DESIGN_IDEATION,
            COLLECTION_PLAN: COLLECTION_PLAN,
            TRIPO_GENERATE: TRIPO_GENERATE,
            FINALIZE: FINALIZE,
        },
    )

    # product_render can chain to social_pack (full_product_launch) or finalize
    graph.add_conditional_edges(
        PRODUCT_RENDER,
        after_render,
        {SOCIAL_PACK: SOCIAL_PACK, FINALIZE: FINALIZE},
    )

    # All other nodes go directly to finalize
    for node in (
        THREE_D_MODEL,
        SOCIAL_PACK,
        PRODUCT_COPY,
        CHARACTER,
        SCENE_COMPOSITE,
        DESIGN_IDEATION,
        COLLECTION_PLAN,
        TRIPO_GENERATE,
    ):
        graph.add_conditional_edges(node, after_any, {FINALIZE: FINALIZE})

    # Terminal edge
    graph.add_edge(FINALIZE, END)

    if checkpointer is not None:
        return graph.compile(checkpointer=checkpointer)
    return graph.compile()


# Module-level singletons — compiled once, reused across all requests.
# Two cache slots: one for the no-checkpointer path (sync entry point),
# one for the PG-checkpointed path (async entry point).
_CREATIVE_GRAPH = None
_CREATIVE_GRAPH_CHECKPOINTED = None


def get_creative_graph():
    """Return the cached compiled graph (no checkpointing, building on first call).

    Use this entry point for short, in-process runs that do not need
    to survive a process restart. For production runs, prefer
    `get_creative_graph_async()` which auto-attaches the PG checkpointer
    when `DATABASE_URL` is configured.
    """
    global _CREATIVE_GRAPH
    if _CREATIVE_GRAPH is None:
        _CREATIVE_GRAPH = build_creative_graph()
    return _CREATIVE_GRAPH


async def get_creative_graph_async():
    """Return the cached compiled graph, attaching PG checkpointing when available.

    On first call:
      - If `DATABASE_URL` points at Postgres, lazy-create an
        `AsyncPostgresSaver` (singleton pool) and compile the graph
        with it as the checkpointer.
      - Otherwise, fall back to the no-checkpointer compile.

    Subsequent calls return the cached graph.
    """
    global _CREATIVE_GRAPH_CHECKPOINTED
    if _CREATIVE_GRAPH_CHECKPOINTED is not None:
        return _CREATIVE_GRAPH_CHECKPOINTED

    from .checkpointer import get_checkpointer

    checkpointer = await get_checkpointer()
    _CREATIVE_GRAPH_CHECKPOINTED = build_creative_graph(checkpointer=checkpointer)
    return _CREATIVE_GRAPH_CHECKPOINTED
