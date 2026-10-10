"""
SDK Content Domain Agents
===========================

SDK-powered sub-agents for the Content core domain.
These agents can read existing site content, write optimized copy,
generate schema.org markup, and publish via WordPress API.

Agents:
    SDKSeoWriterAgent          — Read pages, optimize SEO, write meta
    SDKCollectionPublisherAgent — Generate + publish collection content
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agents.claude_sdk.sdk_sub_agent import SDKSubAgent
from agents.claude_sdk.tool_bridge import ToolProfile
from agents.core.base import CoreAgentType


class SDKSeoWriterAgent(SDKSubAgent):
    """SEO specialist with file + web access.

    Can read existing page templates, analyze competitor SEO,
    write optimized meta tags, and update files directly.
    """

    name = "sdk_seo_writer"
    parent_type = CoreAgentType.CONTENT
    description = "SEO optimization with file access and web research"
    capabilities = [
        "meta_optimize",
        "schema_org_generate",
        "keyword_research",
        "content_audit",
        "heading_hierarchy",
        "og_tags",
    ]
    sdk_tools = ToolProfile.CONTENT
    sdk_model = "sonnet"
    sdk_output_base = Path("data/sdk_sessions/content/seo")

    def _sdk_default_prompt(self) -> str:
        return (
            "You are the DevSkyy SEO Writer for SkyyRose luxury fashion.\n\n"
            "Brand context:\n"
            "- Colors: #B76E79 rose gold, #0A0A0A dark, #D4AF37 gold\n"
            "- Collections: Black Rose (gothic/Oakland), Love Hurts "
            "(passionate/B&B), Signature (Bay Area/SF)\n"
            "- Voice: confident, poetic, streetwear-meets-haute-couture\n\n"
            "Capabilities:\n"
            "- Read existing templates in wordpress-theme/skyyrose-flagship/\n"
            "- Write schema.org JSON-LD for products and collections\n"
            "- Generate SEO meta titles (≤60 chars) and descriptions (≤155 chars)\n"
            "- Optimize heading hierarchy (H1→H2→H3)\n"
            "- Research luxury fashion keywords via web search\n\n"
            "Output structured JSON for each page with: title, description, "
            "og_title, og_description, schema_json_ld, keyword_targets"
        )


class SDKCollectionPublisherAgent(SDKSubAgent):
    """Collection content generator with write + publish access.

    Can read product data, generate collection descriptions,
    create landing page copy, and write output files.
    """

    name = "sdk_collection_publisher"
    parent_type = CoreAgentType.CONTENT
    description = "Generate and publish collection content with product data"
    capabilities = [
        "collection_description",
        "landing_page_copy",
        "product_story",
        "lookbook_copy",
        "press_release",
    ]
    sdk_tools = ToolProfile.CONTENT
    sdk_model = "sonnet"
    sdk_output_base = Path("data/sdk_sessions/content/collections")

    def _sdk_default_prompt(self) -> str:
        return (
            "You are the DevSkyy Collection Publisher for SkyyRose.\n\n"
            "You have access to read product data and brand assets, "
            "research trends, and write publication-ready content.\n\n"
            "Collections:\n"
            "- Black Rose (11 products): gothic luxury, Oakland roots, "
            "night imagery, jersey exclusives\n"
            "- Love Hurts (5 products): Beauty & Beast theme, passion, "
            "varsity + windbreaker statement pieces\n"
            "- Signature (13 products): Bay Area pride, Golden Gate, "
            "golden hour, everyday luxury\n"
            "- Kids Capsule (2 products): next-gen luxury\n\n"
            "Brand voice: confident, poetic, never generic. "
            "Reference Oakland, the Bay, concrete, roses.\n\n"
            "Read product files before writing content. Cross-reference "
            "with wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv for "
            "accurate SKUs and descriptions."
        )

    def _build_task_prompt(self, task: str, **kwargs: Any) -> str:
        """Enrich with collection context when specified."""
        base = super()._build_task_prompt(task, **kwargs)
        collection = kwargs.get("collection")
        if collection:
            base += (
                f"\n\nTarget collection: {collection}\n"
                "Read the product catalog to get accurate product "
                "names, prices, and descriptions for this collection."
            )
        return base


__all__ = [
    "SDKSeoWriterAgent",
    "SDKCollectionPublisherAgent",
]
