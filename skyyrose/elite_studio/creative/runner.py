"""
Creative Operations Hub public API.

run_creative() is the sync entry point (no checkpointing).
arun_creative() is the async entry point with PG checkpointing,
and resume_creative() picks up an interrupted run by operation_id.

""
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def run_creative(
    intent: str,
    params: dict,
    sku: str = "",
    tenant_id: str = "",
) -> dict:
    """Run a creative operation end-to-end (sync, no checkpointing).

    Args:
        intent: One of the CreativeIntent enum values (e.g. "product-render").
        params: Operation-specific parameters dict.
        sku: Product SKU (optional — required for render/tryon intents).
        tenant_id: Tenant identifier for multi-tenant contexts.

    Returns:
        Final CreativeOperationState dict with all result fields populated.
        Always contains 'status' (success/error) and 'operation_id'.
        On error, also contains 'error' with a description.
    """
    from .state import create_initial_state

    initial_state = create_initial_state(
        intent=intent,
        params=params,
        sku=sku,
        tenant_id=tenant_id,
    )

    try:
        from .._observability import langfuse_config
        from .router import get_creative_graph

        graph = get_creative_graph()
        final_state = graph.invoke(initial_state, config=langfuse_config())
        return dict(final_state)
    except Exception as exc:
        logger.exception("run_creative failed for intent=%s sku=%s: %s", intent, sku, exc)
        return {
            **dict(initial_state),
            "status": "error",
            "error": f"Graph execution failed: {exc}",
        }


async def arun_creative(
    intent: str,
    params: dict,
    sku: str = "",
    tenant_id: str = "",
) -> dict:
    """Run a creative operation end-to-end with PG checkpointing.

    Each node's output is persisted to Postgres (when `DATABASE_URL` is
    configured) keyed by `operation_id`. If the run fails mid-pipeline,
    call `resume_creative(operation_id)` to pick up from the last
    successful node.

    Returns the same shape as `run_creative()`.
    """
    from .router import get_creative_graph_async
    from .state import create_initial_state

    initial_state = create_initial_state(
        intent=intent,
        params=params,
        sku=sku,
        tenant_id=tenant_id,
    )
    operation_id = initial_state["operation_id"]
    config = {"configurable": {"thread_id": operation_id}}

    try:
        from .._observability import langfuse_config

        graph = await get_creative_graph_async()
        final_state = await graph.ainvoke(initial_state, config=langfuse_config(config))
        return dict(final_state)
    except Exception as exc:
        logger.exception("arun_creative failed for intent=%s sku=%s: %s", intent, sku, exc)
        return {
            **dict(initial_state),
            "status": "error",
            "error": f"Graph execution failed: {exc}",
            "resumable": True,
        }


async def resume_creative(operation_id: str) -> dict:
    """Resume an interrupted creative operation from its last checkpoint.

    Args:
        operation_id: The operation_id returned in the original failed run.

    Returns:
        The final state after resumption, or a dict with status=error if
        no checkpoint exists.
    """
    from .router import get_creative_graph_async

    config = {"configurable": {"thread_id": operation_id}}

    try:
        from .._observability import langfuse_config

        graph = await get_creative_graph_async()
        # Passing None tells LangGraph to resume from the last checkpoint
        # under this thread_id without any new input.
        final_state = await graph.ainvoke(None, config=langfuse_config(config))
        return dict(final_state)
    except Exception as exc:
        logger.exception("resume_creative failed for operation_id=%s: %s", operation_id, exc)
        return {
            "operation_id": operation_id,
            "status": "error",
            "error": f"Resume failed: {exc}",
        }
