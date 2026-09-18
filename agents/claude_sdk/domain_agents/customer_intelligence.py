"""
SDK Customer Intelligence Domain Agent
==========================================

SDK-powered agent for deep customer analytics, segmentation,
behavior analysis, and lifetime value scoring.

Uses data files, web research, and internal analytics to build
actionable customer profiles and predict behavior patterns.

Agent:
    SDKCustomerIntelAgent — Customer segmentation, CLV, churn prediction
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agents.claude_sdk.sdk_sub_agent import SDKSubAgent
from agents.claude_sdk.tool_bridge import ToolProfile
from agents.core.base import CoreAgentType


class SDKCustomerIntelAgent(SDKSubAgent):
    """Customer intelligence analyst with data and web access.

    Segments customers by behavior, scores lifetime value,
    predicts churn risk, and identifies growth opportunities.
    Reads order data, engagement metrics, and researches
    luxury fashion consumer trends.
    """

    name = "sdk_customer_intel"
    parent_type = CoreAgentType.ANALYTICS
    description = "Customer segmentation, CLV scoring, and behavior analysis"
    capabilities = [
        "customer_segment",
        "clv_score",
        "churn_predict",
        "cohort_analysis",
        "persona_build",
        "purchase_pattern",
    ]
    sdk_tools = ToolProfile.ANALYTICS + ["WebSearch", "WebFetch"]
    sdk_model = "sonnet"
    sdk_output_base = Path("data/sdk_sessions/customer_intelligence")

    def _sdk_default_prompt(self) -> str:
        return (
            "You are the DevSkyy Customer Intelligence agent for SkyyRose.\n\n"
            "SkyyRose customer profile:\n"
            "- Age: 18-35, urban, fashion-forward\n"
            "- Bay Area roots, streetwear-meets-haute-couture\n"
            "- Pre-order model — customers commit before production\n"
            "- 31 products across 4 collections ($25-$265 range)\n"
            "- Jersey exclusives: 80-piece limited runs ($115)\n\n"
            "You analyze:\n"
            "- Customer segments (by collection affinity, spend tier, frequency)\n"
            "- Customer lifetime value (CLV) with cohort-based projections\n"
            "- Churn risk indicators (purchase gaps, engagement drops)\n"
            "- Purchase patterns (cross-collection buying, upsell paths)\n"
            "- Persona profiles for marketing targeting\n\n"
            "Data sources:\n"
            "- Read order/analytics data from data/ directory\n"
            "- Research luxury streetwear consumer trends via web\n"
            "- Cross-reference product facts via skyyrose.core.product.get_product(sku) — the ONE product lookup (CLI: python -m skyyrose.core.product <sku> | --all | --skus)\n\n"
            "Always quantify insights: percentages, dollar values, timeframes. "
            "Segment by collection affinity: Black Rose (edgy/exclusive), "
            "Love Hurts (romantic/bold), Signature (everyday/accessible)."
        )

    def _build_task_prompt(self, task: str, **kwargs: Any) -> str:
        """Enrich with segment or collection focus."""
        base = super()._build_task_prompt(task, **kwargs)
        segment = kwargs.get("segment")
        if segment:
            base += (
                f"\n\nFocus on customer segment: {segment}\n"
                "Pull relevant data for this segment and compare "
                "against overall customer base metrics."
            )
        return base


__all__ = [
    "SDKCustomerIntelAgent",
]
