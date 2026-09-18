"""
SDK Supply Chain Domain Agent
================================

SDK-powered agent for supply chain visibility, demand forecasting,
supplier management, and fulfillment optimization.

Tailored for SkyyRose's pre-order model where production starts
after demand signals are collected.

Agent:
    SDKSupplyChainAgent — Inventory, forecasting, supplier, fulfillment
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agents.claude_sdk.sdk_sub_agent import SDKSubAgent
from agents.claude_sdk.tool_bridge import ToolProfile
from agents.core.base import CoreAgentType


class SDKSupplyChainAgent(SDKSubAgent):
    """Supply chain analyst with data and research access.

    Tracks inventory levels, forecasts demand from pre-order
    signals, manages supplier timelines, and optimizes
    fulfillment logistics for SkyyRose's made-to-order model.
    """

    name = "sdk_supply_chain"
    parent_type = CoreAgentType.COMMERCE
    description = "Supply chain visibility, demand forecasting, and fulfillment"
    capabilities = [
        "inventory_track",
        "demand_forecast",
        "supplier_manage",
        "fulfillment_optimize",
        "lead_time_estimate",
        "reorder_alert",
    ]
    sdk_tools = ToolProfile.COMMERCE + ["WebSearch"]
    sdk_model = "sonnet"
    sdk_output_base = Path("data/sdk_sessions/supply_chain")

    def _sdk_default_prompt(self) -> str:
        return (
            "You are the DevSkyy Supply Chain agent for SkyyRose.\n\n"
            "Business model context:\n"
            "- Pre-order model: most products are pre-order, production "
            "starts after demand is collected\n"
            "- Jersey exclusives: 80-piece limited runs (br-008 through br-011)\n"
            "- Kids Capsule: ready-to-ship inventory (kids-001, kids-002)\n"
            "- 31 products across 4 collections\n\n"
            "You manage:\n"
            "- Pre-order to production pipeline tracking\n"
            "- Demand forecasting from pre-order velocity and trends\n"
            "- Supplier lead time estimation and timeline management\n"
            "- Fulfillment optimization (batch shipping vs individual)\n"
            "- Reorder point alerts for ready-to-ship items\n"
            "- Production capacity planning across collections\n\n"
            "Data sources:\n"
            "- Product catalog: skyyrose.core.product.get_product(sku) — the ONE product lookup (CLI: python -m skyyrose.core.product <sku> | --all | --skus); "
            "pre-order status is catalog.is_preorder\n"
            "- Order/inventory data: data/ directory\n"
            "- Supplier/manufacturer research via web search\n\n"
            "Key metrics: lead time, fill rate, pre-order conversion, "
            "days-to-fulfill, production batch efficiency. "
            "Always read current catalog data before making forecasts."
        )

    def _build_task_prompt(self, task: str, **kwargs: Any) -> str:
        """Enrich with collection or SKU context."""
        base = super()._build_task_prompt(task, **kwargs)
        collection = kwargs.get("collection")
        sku = kwargs.get("sku")
        if collection:
            base += f"\n\nFocus collection: {collection}\n"
        if sku:
            base += f"Specific SKU: {sku}\n"
        return base


__all__ = [
    "SDKSupplyChainAgent",
]
