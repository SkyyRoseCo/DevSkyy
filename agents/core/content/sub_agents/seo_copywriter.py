"""
SEO & Copywriter Sub-Agent (Consolidated)
============================================

Consolidates: seo_content, copywriter.
Wraps agents/skyyrose_content_agent.py for SEO and copy tasks.

Parent: Content Core Agent
Capabilities: Meta tags, schema.org, product copy, CTAs, blog posts.
"""

from __future__ import annotations

from typing import Any

from agents.core.base import CoreAgentType
from agents.core.sub_agent import SubAgent


class SeoCopywriterSubAgent(SubAgent):
    """SEO optimization and brand copywriting."""

    name = "seo_copywriter"
    parent_type = CoreAgentType.CONTENT
    description = "SEO meta tags, schema.org structured data, brand copy, product descriptions"
    capabilities = [
        # seo_content
        "meta_tags",
        "schema_org",
        "sitemap",
        "og_tags",
        "heading_hierarchy",
        # copywriter
        "product_description",
        "page_copy",
        "cta_copy",
        "blog_post",
        "brand_voice",
    ]

    ALIASES = ("seo_content", "copywriter")

    system_prompt = (
        "You are the SEO & Copywriting specialist for SkyyRose luxury fashion. "
        "Brand voice: confident, poetic, streetwear-meets-haute-couture. "
        "No brand slogan is authorized. Color: #B76E79 rose gold. "
        "You write SEO meta tags, schema.org structured data, product descriptions, "
        "blog posts, and CTAs. Always optimize for luxury fashion keywords. "
        "Return content in structured format with meta title, description, and body."
    )

    async def execute(self, task: str, **kwargs: Any) -> dict[str, Any]:
        return await self._llm_execute(task)


__all__ = ["SeoCopywriterSubAgent"]
