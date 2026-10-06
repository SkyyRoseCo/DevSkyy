"""
Product Operations Sub-Agent (Consolidated)
=============================================

Consolidates: product_manager, pricing_engine, inventory_tracker, order_processor.
Wraps agents/skyyrose_product_agent.py into the new hierarchy.

Parent: Commerce Core Agent
Capabilities: Product CRUD, pricing, inventory, order processing.
"""

from __future__ import annotations

from typing import Any

from agents.core.base import CoreAgentType
from agents.core.sub_agent import SubAgent


class ProductOpsSubAgent(SubAgent):
    """Consolidated product operations: CRUD, pricing, inventory, orders."""

    name = "product_ops"
    parent_type = CoreAgentType.COMMERCE
    description = "Product management, pricing, inventory tracking, order processing"
    capabilities = [
        # product_manager
        "create_product",
        "update_product",
        "delete_product",
        "list_products",
        # pricing_engine
        "set_price",
        "bulk_pricing",
        "discount_rules",
        # inventory_tracker
        "stock_check",
        "reorder_alert",
        "inventory_sync",
        # order_processor
        "process_order",
        "order_status",
        "refund",
    ]

    # Routing aliases so the parent's keyword routing still works
    ALIASES = ("product_manager", "pricing_engine", "inventory_tracker", "order_processor")

    system_prompt = (
        "You are the Product Operations specialist for SkyyRose, a luxury fashion "
        "e-commerce brand (#B76E79 rose gold). "
        "You handle product CRUD, pricing strategies, inventory tracking, and order "
        "processing. Collections: Black Rose, Love Hurts, Signature, Kids Capsule. "
        "Respond with structured, actionable data. Use JSON when returning product data."
    )

    async def execute(self, task: str, **kwargs: Any) -> dict[str, Any]:
        return await self._llm_execute(task)


__all__ = ["ProductOpsSubAgent"]
