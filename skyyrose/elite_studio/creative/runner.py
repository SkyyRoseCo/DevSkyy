"""Legacy Creative Operations Hub entrypoints fail closed pending qualification.

Caller parameters cannot authorize paid providers. No graph, observability,
provider or Postgres saver is initialized by these compatibility entrypoints.
"""

from __future__ import annotations

from .nodes import unsupported_paid_route
from .state import create_initial_state


def run_creative(intent: str, params: dict, sku: str = "", tenant_id: str = "") -> dict:
    """Return an explicit denial without constructing the legacy graph."""
    initial = create_initial_state(intent=intent, params=params, sku=sku, tenant_id=tenant_id)
    return {**initial, **unsupported_paid_route(initial, "run_creative")}


async def arun_creative(intent: str, params: dict, sku: str = "", tenant_id: str = "") -> dict:
    """Async compatibility denial before graph/checkpointer imports."""
    return run_creative(intent, params, sku, tenant_id)


async def resume_creative(operation_id: str) -> dict:
    """Historical checkpoints do not grant present provider authority."""
    return unsupported_paid_route({"operation_id": operation_id}, "resume_creative")
