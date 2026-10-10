"""
SDK Community & Loyalty Domain Agent
========================================

SDK-powered agent for community engagement, loyalty program
management, referral tracking, and customer retention.

Designed for SkyyRose's community-first brand strategy where
customers are co-creators and ambassadors, not just buyers.

Agent:
    SDKCommunityLoyaltyAgent — Engagement, loyalty tiers, referrals
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agents.claude_sdk.sdk_sub_agent import SDKSubAgent
from agents.claude_sdk.tool_bridge import ToolProfile
from agents.core.base import CoreAgentType


class SDKCommunityLoyaltyAgent(SDKSubAgent):
    """Community and loyalty program manager with data + web access.

    Tracks community engagement, manages loyalty tier progression,
    designs referral incentives, and monitors community health
    metrics across platforms.
    """

    name = "sdk_community_loyalty"
    parent_type = CoreAgentType.MARKETING
    description = "Community engagement, loyalty tiers, and referral programs"
    capabilities = [
        "engagement_track",
        "loyalty_tier",
        "referral_program",
        "community_health",
        "retention_strategy",
        "ambassador_manage",
    ]
    sdk_tools = ToolProfile.MARKETING + ["Glob", "Grep"]
    sdk_model = "sonnet"
    sdk_output_base = Path("data/sdk_sessions/community")

    def _sdk_default_prompt(self) -> str:
        return (
            "You are the DevSkyy Community & Loyalty agent for SkyyRose.\n\n"
            "Community philosophy:\n"
            "- Customers are co-creators, not just buyers\n"
            "- Pre-order model creates natural community (early supporters)\n"
            "- Jersey exclusives (80 pcs) create collector community\n\n"
            "Loyalty tiers (design/manage):\n"
            "- Concrete: first purchase (welcome, community access)\n"
            "- Rose: 3+ purchases or 1 exclusive (early access, events)\n"
            "- Gold: 5+ purchases or $500+ LTV (VIP drops, founder access)\n"
            "- Black Rose: invite-only (co-design, first-look, events)\n\n"
            "You manage:\n"
            "- Community engagement metrics (comments, shares, UGC)\n"
            "- Loyalty tier progression and reward fulfillment\n"
            "- Referral program design and tracking\n"
            "- Ambassador identification and management\n"
            "- Retention campaigns (re-engagement, win-back)\n"
            "- Community health scoring (NPS, churn risk, advocacy rate)\n\n"
            "WordPress integration:\n"
            "- Referral dashboard: template-parts/referral-dashboard.php\n"
            "- Klaviyo capture: template-parts/klaviyo-capture.php\n"
            "- Read these templates when designing loyalty features.\n\n"
            "Always ground engagement strategies in data. Reference "
            "specific collection affinities when targeting segments."
        )

    def _build_task_prompt(self, task: str, **kwargs: Any) -> str:
        """Enrich with tier or program context."""
        base = super()._build_task_prompt(task, **kwargs)
        tier = kwargs.get("tier")
        program = kwargs.get("program")
        if tier:
            base += f"\n\nFocus loyalty tier: {tier}\n"
        if program:
            base += f"Program type: {program}\n"
        return base


__all__ = [
    "SDKCommunityLoyaltyAgent",
]
