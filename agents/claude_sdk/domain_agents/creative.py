"""
SDK Creative Domain Agents
=============================

SDK-powered sub-agents for the Creative core domain.
These agents manage brand assets, design system tokens,
and creative content generation.

Agents:
    SDKBrandAssetAgent   — Manage brand assets, verify brand compliance
    SDKDesignSystemAgent — Design tokens, color palettes, typography rules
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agents.claude_sdk.sdk_sub_agent import SDKSubAgent
from agents.claude_sdk.tool_bridge import ToolProfile
from agents.core.base import CoreAgentType


class SDKBrandAssetAgent(SDKSubAgent):
    """Brand asset manager with file access.

    Manages brand assets (logos, patches, avatars), verifies
    brand compliance in templates, and audits asset usage.
    """

    name = "sdk_brand_asset"
    parent_type = CoreAgentType.CREATIVE
    description = "Manage brand assets, verify brand compliance"
    capabilities = [
        "asset_audit",
        "brand_compliance",
        "asset_catalog",
        "color_verify",
        "logo_usage",
    ]
    sdk_tools = ToolProfile.CREATIVE + ["Grep"]
    sdk_model = "sonnet"
    sdk_output_base = Path("data/sdk_sessions/creative/brand")

    def _sdk_default_prompt(self) -> str:
        return (
            "You are the DevSkyy Brand Asset Manager for SkyyRose.\n\n"
            "Brand identity:\n"
            "- Tagline: 'Luxury Grows from Concrete.' (ONLY tagline)\n"
            "- RETIRED: 'Where Love Meets Luxury' — NEVER use\n"
            "- Colors: #B76E79 rose gold, #0A0A0A dark, #C0C0C0 silver, "
            "#DC143C crimson, #D4AF37 gold\n"
            "- Founder: Corey Foster\n\n"
            "Asset locations:\n"
            "- Patch images: brand-assets/patch-{mlb,nfl,nba,hockey}*.jpeg\n"
            "- Avatar reference: source-products/brand-assets/"
            "skyyrose-avatar-reference.jpeg\n"
            "- Mascot sprites: assets/images/mascot/skyyrose-mascot-*.png "
            "(7 poses + idle + fallback SVG)\n"
            "- Product renders: resolve via skyyrose.core.product."
            "get_product(sku)['images'][role] (data/sot-images.json is a "
            "generated projection of the same bindings, for non-Python "
            "consumers only) — never assume a literal filename pattern, the "
            "actual render may be named differently or be a hub-verified "
            "override.\n\n"
            "Rules:\n"
            "- Verify brand colors are used correctly in templates\n"
            "- Check that retired tagline is NOT present anywhere\n"
            "- Audit alt text on images for accessibility\n"
            "- Verify logo usage follows brand guidelines"
        )

    def _build_task_prompt(self, task: str, **kwargs: Any) -> str:
        """Enrich with asset type context."""
        base = super()._build_task_prompt(task, **kwargs)
        asset_type = kwargs.get("asset_type")
        if asset_type:
            base += (
                f"\n\nFocus on: {asset_type} assets\n"
                "Read the relevant directories and verify "
                "all assets match brand guidelines."
            )
        return base


class SDKDesignSystemAgent(SDKSubAgent):
    """Design system manager with file access.

    Manages design tokens, verifies CSS consistency,
    and generates design system documentation.
    """

    name = "sdk_design_system"
    parent_type = CoreAgentType.CREATIVE
    description = "Design tokens, color palettes, CSS consistency"
    capabilities = [
        "token_audit",
        "css_consistency",
        "typography_check",
        "spacing_audit",
        "theme_generation",
    ]
    sdk_tools = ToolProfile.CREATIVE + ["Grep", "Edit"]
    sdk_model = "sonnet"
    sdk_output_base = Path("data/sdk_sessions/creative/design_system")

    def _sdk_default_prompt(self) -> str:
        return (
            "You are the DevSkyy Design System Agent for SkyyRose.\n\n"
            "Design tokens:\n"
            "- Rose Gold: #B76E79 (primary brand)\n"
            "- Dark: #0A0A0A (backgrounds)\n"
            "- Silver: #C0C0C0 (accents)\n"
            "- Crimson: #DC143C (Love Hurts collection)\n"
            "- Gold: #D4AF37 (Signature collection)\n\n"
            "Theme location: wordpress-theme/skyyrose-flagship/\n"
            "CSS files: assets/css/ (112 files + minified)\n"
            "JS files: assets/js/ (88 files + minified)\n\n"
            "Responsibilities:\n"
            "- Audit CSS for consistent color usage\n"
            "- Verify typography scale across templates\n"
            "- Check spacing/sizing consistency\n"
            "- Generate CSS custom property definitions\n"
            "- Detect hardcoded colors that should be tokens\n"
            "- Ensure dark mode / light mode consistency"
        )


__all__ = [
    "SDKBrandAssetAgent",
    "SDKDesignSystemAgent",
]
