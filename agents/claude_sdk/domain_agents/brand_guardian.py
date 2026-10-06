"""
SDK Brand Guardian Domain Agent
==================================

SDK-powered agent that enforces brand consistency across all
touchpoints — copy, visuals, code, and external communications.

Acts as the brand's immune system: detects deviations, flags
violations, and auto-corrects common drift patterns.

Agent:
    SDKBrandGuardianAgent — Brand consistency, tone, compliance
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agents.claude_sdk.sdk_sub_agent import SDKSubAgent
from agents.claude_sdk.tool_bridge import ToolProfile
from agents.core.base import CoreAgentType


class SDKBrandGuardianAgent(SDKSubAgent):
    """Brand guardian with full codebase and content access.

    Scans files for brand violations (wrong tagline, off-brand
    colors, inconsistent tone), audits external mentions, and
    enforces the SkyyRose brand bible across all channels.
    """

    name = "sdk_brand_guardian"
    parent_type = CoreAgentType.CREATIVE
    description = "Brand consistency enforcement and compliance auditing"
    capabilities = [
        "brand_audit",
        "tagline_enforce",
        "tone_monitor",
        "color_compliance",
        "copy_review",
        "brand_drift_detect",
    ]
    sdk_tools = ToolProfile.OPERATIONS + ["WebSearch"]
    sdk_model = "sonnet"
    sdk_output_base = Path("data/sdk_sessions/brand_guardian")

    def _sdk_default_prompt(self) -> str:
        return (
            "You are the DevSkyy Brand Guardian for SkyyRose.\n\n"
            "BRAND BIBLE (violations are CRITICAL):\n"
            "- NO tagline is authorised anywhere — flag any tagline use\n"
            "- RETIRED tagline: 'Where Love Meets Luxury' — NEVER appears anywhere\n"
            "- Colors: #B76E79 rose gold, #0A0A0A dark, #C0C0C0 silver, "
            "#DC143C crimson, #D4AF37 gold\n"
            "- Voice: confident, poetic, streetwear-meets-haute-couture\n"
            "- Founder: Corey Foster\n"
            "- Collections: Black Rose (gothic/Oakland), Love Hurts "
            "(passionate/B&B), Signature (Bay Area/SF), Kids Capsule\n\n"
            "Audit scope:\n"
            "- Grep codebase for retired taglines, wrong color codes, off-brand copy\n"
            "- Review WordPress theme templates for brand consistency\n"
            "- Check product descriptions against brand voice guidelines\n"
            "- Scan social media content templates for tone alignment\n"
            "- Verify meta tags, OG images, and email templates match brand\n\n"
            "Severity levels:\n"
            "- CRITICAL: wrong tagline in production, incorrect brand name\n"
            "- HIGH: off-palette colors in customer-facing UI\n"
            "- MEDIUM: tone inconsistency in copy\n"
            "- LOW: missing brand element (e.g., no tagline on a page)\n\n"
            "Key files to audit:\n"
            "- wordpress-theme/skyyrose-flagship/ (templates, CSS)\n"
            "- frontend/src/ (Next.js components)\n"
            "- agents/ (prompt templates mentioning brand)\n"
            "- scripts/ (output templates)\n\n"
            "Use Grep to search for violations. Report file:line for each finding."
        )

    def _build_task_prompt(self, task: str, **kwargs: Any) -> str:
        """Enrich with audit scope."""
        base = super()._build_task_prompt(task, **kwargs)
        scope = kwargs.get("scope")
        if scope:
            base += (
                f"\n\nAudit scope: {scope}\nFocus your brand compliance scan on this specific area."
            )
        return base


__all__ = [
    "SDKBrandGuardianAgent",
]
