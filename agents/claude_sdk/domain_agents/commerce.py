"""
SDK Commerce Domain Agents
=============================

SDK-powered sub-agents for the Commerce core domain.
These agents can read product catalogs, query files,
analyze pricing data, and manage catalog operations.

Agents:
    SDKCatalogManagerAgent — Read/update product catalog data
    SDKPriceOptimizerAgent — Analyze pricing with real data access
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agents.claude_sdk.sdk_sub_agent import SDKSubAgent
from agents.claude_sdk.tool_bridge import ToolProfile
from agents.core.base import CoreAgentType


class SDKCatalogManagerAgent(SDKSubAgent):
    """Product catalog manager with file access.

    Can read the product catalog source files, verify SKUs,
    cross-reference collections, and generate catalog reports.
    """

    name = "sdk_catalog_manager"
    parent_type = CoreAgentType.COMMERCE
    description = "Manage product catalog with file access and verification"
    capabilities = [
        "catalog_read",
        "sku_verify",
        "collection_audit",
        "inventory_report",
        "product_export",
    ]
    sdk_tools = ToolProfile.COMMERCE
    sdk_model = "sonnet"
    sdk_output_base = Path("data/sdk_sessions/commerce/catalog")

    def _sdk_default_prompt(self) -> str:
        return (
            "You are the DevSkyy Catalog Manager for SkyyRose.\n\n"
            "Product data source (READ THIS — never invent SKUs):\n"
            "- skyyrose.core.product.get_product(sku) — the ONE product lookup (CLI: python -m skyyrose.core.product <sku> | --all | --skus). "
            "One record per SKU: catalog (name, price, collection, description, "
            "published, is_preorder), garment (color, available_sizes, fit, "
            "materials, features), dossier, images, content, and a gaps list "
            "naming anything absent. Garment color is "
            "get_product(sku)['garment']['color'].\n"
            "- The registry behind it is "
            "wordpress-theme/skyyrose-flagship/data/logo-registry.json; "
            "skyyrose-catalog.csv is a generated projection of it.\n\n"
            "Collections: black-rose, love-hurts, signature, kids-capsule. "
            "List the SKUs in each with python -m skyyrose.core.product --skus "
            "or get_all_products() — never from memory.\n\n"
            "Rules:\n"
            "- NEVER fabricate SKU IDs or product names\n"
            "- NEVER guess prices — read from source\n"
            "- Always cross-reference get_product(sku) before reporting\n"
            "- Pre-order status is authoritative from catalog.is_preorder"
        )


class SDKPriceOptimizerAgent(SDKSubAgent):
    """Pricing analyst with data access and research.

    Can read current pricing, research competitor prices,
    analyze margins, and recommend pricing strategies.
    """

    name = "sdk_price_optimizer"
    parent_type = CoreAgentType.COMMERCE
    description = "Pricing analysis with catalog access and market research"
    capabilities = [
        "price_analysis",
        "margin_calculate",
        "competitor_compare",
        "bundle_pricing",
        "discount_strategy",
    ]
    sdk_tools = ToolProfile.COMMERCE + ["WebSearch", "WebFetch"]
    sdk_model = "sonnet"
    sdk_output_base = Path("data/sdk_sessions/commerce/pricing")

    def _sdk_default_prompt(self) -> str:
        return (
            "You are the DevSkyy Price Optimizer for SkyyRose.\n\n"
            "Current price ranges:\n"
            "- Black Rose: $35-$115\n"
            "- Love Hurts: $45-$265\n"
            "- Signature: $25-$195\n"
            "- Kids Capsule: $40\n\n"
            "You can:\n"
            "- Read current pricing from skyyrose.core.product.get_product(sku) — the ONE product lookup (CLI: python -m skyyrose.core.product <sku> | --all | --skus): "
            "price = get_product(sku)['catalog']['price']\n"
            "- Research competitor pricing via web search\n"
            "- Calculate margins and optimize price points\n"
            "- Recommend bundle pricing strategies\n"
            "- Analyze price elasticity based on market data\n\n"
            "Always read current prices from the product registry first. "
            "Never guess — verify from get_product(sku)."
        )

    def _build_task_prompt(self, task: str, **kwargs: Any) -> str:
        """Enrich with collection context for targeted analysis."""
        base = super()._build_task_prompt(task, **kwargs)
        collection = kwargs.get("collection")
        if collection:
            base += (
                f"\n\nFocus on: {collection} collection\n"
                "Read get_product(sku)['catalog']['price'] (python -m "
                "skyyrose.core.product --all) for every SKU whose "
                "collection matches — current prices for this collection."
            )
        return base


__all__ = [
    "SDKCatalogManagerAgent",
    "SDKPriceOptimizerAgent",
]
