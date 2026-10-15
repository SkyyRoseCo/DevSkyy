"""
Brand Secret Intelligence Agent
=================================

Covert competitive intelligence for SkyyRose brand strategy.

Capabilities:
- Competitor profiling: SWOT analysis per competitor brand
- Price gap analysis: where SkyyRose sits vs competitors by product type
- Style trend mapping: what aesthetics competitors are converging on
- Opportunity detection: whitespace in the market nobody is filling
- Threat assessment: who is encroaching on SkyyRose's positioning
- Strategic briefings: actionable intel reports for brand decisions
- Comparative scoring: grade competitors across brand dimensions

Integrates with:
- services/competitive/ (CompetitorAnalysisService for data)
- orchestration/brand_learning.py (emit competitive_intel signals)
- orchestration/brand_context.py (SkyyRose brand DNA for comparison)

Parent: Analytics Core Agent
"""

from __future__ import annotations

import logging
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from agents.core.base import CoreAgentType
from agents.core.sub_agent import SubAgent

logger = logging.getLogger(__name__)


# =============================================================================
# Data Models
# =============================================================================


@dataclass
class CompetitorProfile:
    """Full intelligence profile for a competitor."""

    name: str
    category: str = ""  # direct, indirect, aspirational, emerging
    price_positioning: str = ""
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    opportunities: list[str] = field(default_factory=list)
    threats: list[str] = field(default_factory=list)
    style_signature: str = ""
    price_range: dict[str, float] = field(default_factory=dict)
    product_types: list[str] = field(default_factory=list)
    threat_level: float = 0.0  # 0-100
    overlap_score: float = 0.0  # 0-100: how much they overlap with SkyyRose
    assessed_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class MarketGap:
    """An identified gap in the competitive landscape."""

    gap_type: str  # price_gap, style_gap, audience_gap, product_gap
    description: str
    opportunity_score: float = 0.0  # 0-100
    relevant_collections: list[str] = field(default_factory=list)
    competitor_context: str = ""
    recommended_action: str = ""


@dataclass
class PricePosition:
    """SkyyRose's position in a price map."""

    product_type: str
    skyyrose_avg: float
    market_avg: float
    market_min: float
    market_max: float
    position: str = ""  # "below_market", "at_market", "above_market", "premium"
    gap_pct: float = 0.0  # % difference from market avg


@dataclass
class ThreatAssessment:
    """Threat level assessment for a competitor."""

    competitor_name: str
    threat_level: str = "low"  # low, moderate, high, critical
    threat_score: float = 0.0  # 0-100
    encroachment_areas: list[str] = field(default_factory=list)
    defensive_actions: list[str] = field(default_factory=list)


@dataclass
class IntelBriefing:
    """Strategic intelligence briefing."""

    title: str
    generated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    competitor_count: int = 0
    asset_count: int = 0
    top_threats: list[ThreatAssessment] = field(default_factory=list)
    market_gaps: list[MarketGap] = field(default_factory=list)
    price_positions: list[PricePosition] = field(default_factory=list)
    style_trends: dict[str, int] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)


# =============================================================================
# Brand Secret Intelligence Agent
# =============================================================================


class BrandIntelAgent(SubAgent):
    """
    Brand intelligence agent — investigates competitors, analyzes strengths
    and weaknesses, maps market positioning, and plans counter-strategy.

    This is the "secret service" of the SkyyRose brand ecosystem.
    """

    name = "brand_intel"
    parent_type = CoreAgentType.ANALYTICS
    description = (
        "Competitive intelligence: SWOT analysis, price mapping, "
        "threat assessment, market gap detection, strategic briefings"
    )
    capabilities = [
        "profile_competitor",
        "analyze_price_gaps",
        "detect_market_gaps",
        "assess_threats",
        "generate_briefing",
        "compare_styles",
        "score_competitors",
    ]

    ALIASES = ["brand_intelligence", "competitive_intel", "intel"]

    # SkyyRose reference data for comparison
    SKYYROSE_PRICE_MAP: dict[str, dict[str, float]] = {
        "hoodie": {"min": 40, "max": 65, "avg": 50},
        "crewneck": {"min": 35, "max": 40, "avg": 37.5},
        "joggers": {"min": 50, "max": 95, "avg": 72.5},
        "shorts": {"min": 60, "max": 195, "avg": 91.25},
        "jacket": {"min": 80, "max": 265, "avg": 135},
        "jersey": {"min": 45, "max": 115, "avg": 97.5},
        "tee": {"min": 25, "max": 30, "avg": 27.5},
        "beanie": {"min": 25, "max": 25, "avg": 25},
    }

    SKYYROSE_STYLES = ["streetwear", "gothic", "romantic", "edgy", "classic"]

    system_prompt = (
        "You are the Brand Intelligence Agent for SkyyRose luxury fashion. "
        "Brand: luxury streetwear, Oakland CA. "
        "3 collections: Black Rose (gothic), Love Hurts (passionate), Signature (Bay Area golden). "
        "Your mission: investigate competitors ruthlessly but analytically. "
        "Identify what they do well, where they're weak, and how SkyyRose can dominate. "
        "Be specific with numbers and actionable with recommendations. "
        "Frame everything as strategic advantage for SkyyRose."
    )

    def __init__(
        self,
        *,
        parent: Any | None = None,
        correlation_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent=parent, correlation_id=correlation_id, **kwargs)
        self._comp_service: Any = None
        self._learning_loop: Any = None

    # -------------------------------------------------------------------------
    # Lazy init
    # -------------------------------------------------------------------------

    def _get_comp_service(self) -> Any:
        if self._comp_service is None:
            try:
                from services.competitive.competitor_analysis import (
                    CompetitorAnalysisService,
                )

                self._comp_service = CompetitorAnalysisService()
            except ImportError:
                logger.debug("[%s] CompetitorAnalysisService unavailable", self.name)
        return self._comp_service

    def _get_learning_loop(self) -> Any:
        if self._learning_loop is None:
            try:
                from orchestration.brand_learning import create_brand_learning_loop

                self._learning_loop = create_brand_learning_loop(auto_connect=True)
            except ImportError:
                pass
        return self._learning_loop

    # -------------------------------------------------------------------------
    # Core execution
    # -------------------------------------------------------------------------

    async def execute(self, task: str, **kwargs: Any) -> dict[str, Any]:
        task_lower = task.lower()

        if "briefing" in task_lower or "report" in task_lower:
            return await self.generate_briefing(**kwargs)

        if "swot" in task_lower or "profile" in task_lower:
            return await self.profile_competitor(task, **kwargs)

        if "price" in task_lower and ("gap" in task_lower or "map" in task_lower):
            return self.analyze_price_gaps(**kwargs)

        if "threat" in task_lower:
            return self.assess_threats(**kwargs)

        if "gap" in task_lower or "opportunity" in task_lower or "whitespace" in task_lower:
            return self.detect_market_gaps(**kwargs)

        if "style" in task_lower or "trend" in task_lower:
            return self.compare_styles(**kwargs)

        if "score" in task_lower or "grade" in task_lower:
            return self.score_competitors(**kwargs)

        # Default: LLM-powered competitive analysis
        return await self._llm_execute(task)

    # -------------------------------------------------------------------------
    # SWOT Profiling
    # -------------------------------------------------------------------------

    async def profile_competitor(self, task: str, **kwargs: Any) -> dict[str, Any]:
        """Generate a SWOT profile for a competitor using LLM analysis."""
        competitor_name = kwargs.get("competitor_name", "")
        competitor_data = kwargs.get("competitor_data", {})

        prompt = (
            f"Generate a SWOT analysis for competitor '{competitor_name}' "
            f"from SkyyRose's perspective.\n\n"
            f"Competitor data: {competitor_data}\n\n"
            f"SkyyRose context: luxury streetwear, Oakland CA, price range $25-$265, "
            f"3 collections (Black Rose gothic, Love Hurts passionate, Signature Bay Area). "
            f"31 products across hoodies, jerseys, joggers, shorts, jackets.\n\n"
            f"Analyze:\n"
            f"1. STRENGTHS: What do they do better than SkyyRose?\n"
            f"2. WEAKNESSES: Where are they vulnerable?\n"
            f"3. OPPORTUNITIES: How can SkyyRose exploit their gaps?\n"
            f"4. THREATS: How could they hurt SkyyRose's position?\n"
            f"5. Threat level (0-100) and overlap score (0-100)\n\n"
            f"Be specific and actionable."
        )

        result = await self._llm_execute(prompt)

        self._emit_intel_signal(
            f"SWOT profile generated for {competitor_name}",
            {"competitor": competitor_name},
        )

        return {
            "success": True,
            "analysis": result.get("result", ""),
            "competitor": competitor_name,
            "type": "swot_profile",
            "agent": self.name,
        }

    # -------------------------------------------------------------------------
    # Price Gap Analysis
    # -------------------------------------------------------------------------

    def analyze_price_gaps(
        self,
        *,
        competitor_prices: dict[str, dict[str, list[float]]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Map SkyyRose's pricing vs competitor landscape.

        Args:
            competitor_prices: {competitor: {product_type: [prices]}}

        Returns:
            Price position analysis with gap recommendations
        """
        if not competitor_prices:
            return {
                "success": True,
                "positions": [],
                "summary": "No competitor price data provided. Use with competitor_prices kwarg.",
                "skyyrose_reference": self.SKYYROSE_PRICE_MAP,
                "agent": self.name,
            }

        # Aggregate market prices by product type
        market_prices: dict[str, list[float]] = defaultdict(list)
        for comp_data in competitor_prices.values():
            for product_type, prices in comp_data.items():
                market_prices[product_type].extend(prices)

        positions: list[dict[str, Any]] = []

        for product_type, prices in market_prices.items():
            if not prices:
                continue

            skyyrose = self.SKYYROSE_PRICE_MAP.get(product_type)
            if not skyyrose:
                continue

            market_avg = statistics.mean(prices)
            market_min = min(prices)
            market_max = max(prices)
            sr_avg = skyyrose["avg"]

            gap_pct = ((sr_avg - market_avg) / market_avg * 100) if market_avg > 0 else 0

            if gap_pct > 20:
                position = "premium"
            elif gap_pct > 5:
                position = "above_market"
            elif gap_pct > -5:
                position = "at_market"
            else:
                position = "below_market"

            pos = PricePosition(
                product_type=product_type,
                skyyrose_avg=sr_avg,
                market_avg=round(market_avg, 2),
                market_min=market_min,
                market_max=market_max,
                position=position,
                gap_pct=round(gap_pct, 1),
            )
            positions.append(
                {
                    "product_type": pos.product_type,
                    "skyyrose_avg": pos.skyyrose_avg,
                    "market_avg": pos.market_avg,
                    "market_range": f"${pos.market_min}-${pos.market_max}",
                    "position": pos.position,
                    "gap_pct": f"{pos.gap_pct:+.1f}%",
                }
            )

        self._emit_intel_signal(
            f"Price gap analysis: {len(positions)} product types mapped",
            {"product_types": len(positions)},
        )

        return {
            "success": True,
            "positions": positions,
            "total_competitors": len(competitor_prices),
            "agent": self.name,
        }

    # -------------------------------------------------------------------------
    # Market Gap Detection
    # -------------------------------------------------------------------------

    def detect_market_gaps(
        self,
        *,
        competitor_products: dict[str, list[str]] | None = None,
        competitor_styles: dict[str, list[str]] | None = None,
        competitor_audiences: dict[str, list[str]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Find whitespace in the competitive landscape.

        Looks for product types, styles, and audiences that competitors
        aren't serving well — opportunities for SkyyRose.
        """
        gaps: list[dict[str, Any]] = []

        # Product gap analysis
        if competitor_products:
            all_types: Counter[str] = Counter()
            for products in competitor_products.values():
                all_types.update(products)

            skyyrose_types = {
                "hoodie",
                "crewneck",
                "joggers",
                "shorts",
                "jacket",
                "jersey",
                "tee",
                "beanie",
                "windbreaker",
            }

            # Types SkyyRose has that few competitors offer
            for sr_type in skyyrose_types:
                comp_count = all_types.get(sr_type, 0)
                if comp_count <= 1:
                    gaps.append(
                        {
                            "gap_type": "product_gap",
                            "description": (
                                f"SkyyRose's {sr_type} category has minimal competition "
                                f"({comp_count} competitors). Strong differentiation opportunity."
                            ),
                            "opportunity_score": 80 - comp_count * 20,
                            "relevant_collections": ["all"],
                            "recommended_action": f"Double down on {sr_type} marketing and exclusivity",
                        }
                    )

            # Types competitors have that SkyyRose doesn't
            for product_type, count in all_types.most_common():
                if product_type not in skyyrose_types and count >= 3:
                    gaps.append(
                        {
                            "gap_type": "product_gap",
                            "description": (
                                f"{count} competitors offer {product_type} but SkyyRose doesn't. "
                                f"Evaluate if this fits the brand."
                            ),
                            "opportunity_score": min(count * 15, 75),
                            "relevant_collections": ["signature"],
                            "recommended_action": f"Research {product_type} demand in SkyyRose audience",
                        }
                    )

        # Style gap analysis
        if competitor_styles:
            all_styles: Counter[str] = Counter()
            for styles in competitor_styles.values():
                all_styles.update(styles)

            for sr_style in self.SKYYROSE_STYLES:
                style_count = all_styles.get(sr_style, 0)
                total_comps = len(competitor_styles)
                saturation = style_count / total_comps if total_comps > 0 else 0

                if saturation > 0.6:
                    gaps.append(
                        {
                            "gap_type": "style_gap",
                            "description": (
                                f"'{sr_style}' is oversaturated ({style_count}/{total_comps} "
                                f"competitors). SkyyRose needs stronger differentiation here."
                            ),
                            "opportunity_score": 30,
                            "recommended_action": (
                                f"Evolve beyond generic {sr_style} — "
                                f"lean into SkyyRose's unique Oakland heritage"
                            ),
                        }
                    )
                elif saturation < 0.2 and sr_style in ("gothic", "romantic"):
                    gaps.append(
                        {
                            "gap_type": "style_gap",
                            "description": (
                                f"'{sr_style}' aesthetic is underserved — only {style_count} "
                                f"competitors. This is SkyyRose's natural territory."
                            ),
                            "opportunity_score": 85,
                            "relevant_collections": (
                                ["BLACK_ROSE"] if sr_style == "gothic" else ["LOVE_HURTS"]
                            ),
                            "recommended_action": f"Own the {sr_style} luxury streetwear niche",
                        }
                    )

        if not gaps:
            gaps.append(
                {
                    "gap_type": "data_needed",
                    "description": "Provide competitor_products and/or competitor_styles for gap analysis",
                    "opportunity_score": 0,
                    "recommended_action": "Collect competitor data first",
                }
            )

        self._emit_intel_signal(
            f"Market gap analysis: {len(gaps)} gaps identified",
            {"gap_count": len(gaps)},
        )

        return {
            "success": True,
            "gaps": sorted(gaps, key=lambda g: g.get("opportunity_score", 0), reverse=True),
            "agent": self.name,
        }

    # -------------------------------------------------------------------------
    # Threat Assessment
    # -------------------------------------------------------------------------

    def assess_threats(
        self,
        *,
        competitors: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Score threat level of each competitor to SkyyRose.

        Args:
            competitors: List of {"name": ..., "category": ...,
                         "price_positioning": ..., "styles": [...],
                         "product_types": [...], "growth_rate": ...}
        """
        if not competitors:
            return {"success": False, "error": "No competitors provided", "agent": self.name}

        assessments: list[dict[str, Any]] = []

        for comp in competitors:
            name = comp.get("name", "Unknown")
            score = 0.0
            encroachments: list[str] = []
            defenses: list[str] = []

            # Category weight
            cat_scores = {"direct": 30, "indirect": 15, "emerging": 20, "aspirational": 5}
            score += cat_scores.get(comp.get("category", ""), 10)

            # Price overlap
            price_pos = comp.get("price_positioning", "")
            if price_pos in ("premium", "luxury"):
                score += 20
                encroachments.append("Same price tier — direct price competition")
                defenses.append("Emphasize SkyyRose exclusivity and Oakland heritage")

            # Style overlap
            comp_styles = set(comp.get("styles", []))
            overlap = comp_styles & set(self.SKYYROSE_STYLES)
            style_overlap_pct = (
                len(overlap) / len(self.SKYYROSE_STYLES) * 100 if self.SKYYROSE_STYLES else 0
            )
            score += style_overlap_pct * 0.3
            if overlap:
                encroachments.append(f"Style overlap in: {', '.join(overlap)}")
                defenses.append("Lean into unique collection narratives (Oakland, B&B, Bay)")

            # Product overlap
            comp_products = set(comp.get("product_types", []))
            sr_products = {"hoodie", "crewneck", "joggers", "shorts", "jacket", "jersey", "tee"}
            product_overlap = comp_products & sr_products
            if len(product_overlap) > 3:
                score += 15
                encroachments.append(f"Product overlap: {', '.join(product_overlap)}")
                defenses.append("Focus on limited-edition drops and jersey exclusivity")

            # Growth factor
            growth = comp.get("growth_rate", 0)
            if growth > 20:
                score += 15
                encroachments.append(f"Fast growth ({growth}% YoY) — gaining market share")
                defenses.append("Accelerate social media presence and community building")

            score = min(score, 100)

            if score >= 70:
                level = "critical"
            elif score >= 50:
                level = "high"
            elif score >= 30:
                level = "moderate"
            else:
                level = "low"

            assessments.append(
                {
                    "competitor": name,
                    "threat_level": level,
                    "threat_score": round(score, 1),
                    "encroachment_areas": encroachments,
                    "defensive_actions": defenses,
                }
            )

        assessments.sort(key=lambda a: a["threat_score"], reverse=True)

        self._emit_intel_signal(
            f"Threat assessment: {len(assessments)} competitors evaluated",
            {"critical_threats": sum(1 for a in assessments if a["threat_level"] == "critical")},
        )

        return {
            "success": True,
            "assessments": assessments,
            "summary": {
                "total": len(assessments),
                "critical": sum(1 for a in assessments if a["threat_level"] == "critical"),
                "high": sum(1 for a in assessments if a["threat_level"] == "high"),
                "moderate": sum(1 for a in assessments if a["threat_level"] == "moderate"),
                "low": sum(1 for a in assessments if a["threat_level"] == "low"),
            },
            "agent": self.name,
        }

    # -------------------------------------------------------------------------
    # Style Comparison
    # -------------------------------------------------------------------------

    def compare_styles(
        self,
        *,
        competitor_styles: dict[str, list[str]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Map style trends across the competitive landscape."""
        if not competitor_styles:
            return {"success": False, "error": "No style data provided", "agent": self.name}

        all_styles: Counter[str] = Counter()
        for styles in competitor_styles.values():
            all_styles.update(styles)

        skyyrose_unique = set(self.SKYYROSE_STYLES) - set(all_styles.keys())
        oversaturated = [s for s, c in all_styles.items() if c >= len(competitor_styles) * 0.5]

        return {
            "success": True,
            "style_frequency": dict(all_styles.most_common()),
            "skyyrose_styles": self.SKYYROSE_STYLES,
            "unique_to_skyyrose": list(skyyrose_unique),
            "oversaturated": oversaturated,
            "recommendation": (
                f"SkyyRose owns {len(skyyrose_unique)} unique style(s). "
                f"Avoid competing on {', '.join(oversaturated[:3])} — differentiate instead."
                if oversaturated
                else "Market is fragmented — SkyyRose can define the category."
            ),
            "agent": self.name,
        }

    # -------------------------------------------------------------------------
    # Competitor Scoring (report card)
    # -------------------------------------------------------------------------

    def score_competitors(
        self,
        *,
        competitors: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Grade competitors across brand dimensions.

        Dimensions: brand_strength, product_range, price_value,
                   visual_quality, social_presence, innovation
        """
        if not competitors:
            return {"success": False, "error": "No competitors provided", "agent": self.name}

        dimensions = [
            "brand_strength",
            "product_range",
            "price_value",
            "visual_quality",
            "social_presence",
            "innovation",
        ]

        scorecards: list[dict[str, Any]] = []

        for comp in competitors:
            name = comp.get("name", "Unknown")
            scores: dict[str, float] = {}

            for dim in dimensions:
                # Use provided score or estimate from available data
                scores[dim] = comp.get(dim, 50.0)

            overall = statistics.mean(scores.values())

            scorecards.append(
                {
                    "competitor": name,
                    "scores": scores,
                    "overall": round(overall, 1),
                    "grade": self._score_to_grade(overall),
                    "vs_skyyrose": (
                        "above" if overall > 70 else ("par" if overall > 50 else "below")
                    ),
                }
            )

        scorecards.sort(key=lambda s: s["overall"], reverse=True)

        return {
            "success": True,
            "scorecards": scorecards,
            "dimensions": dimensions,
            "agent": self.name,
        }

    # -------------------------------------------------------------------------
    # Strategic Briefing (full report)
    # -------------------------------------------------------------------------

    async def generate_briefing(self, **kwargs: Any) -> dict[str, Any]:
        """Generate a full strategic intelligence briefing using LLM."""
        competitors = kwargs.get("competitors", [])
        market_data = kwargs.get("market_data", {})

        prompt = (
            "Generate a Strategic Intelligence Briefing for SkyyRose luxury fashion.\n\n"
            f"Brand: SkyyRose — luxury streetwear, Oakland CA.\n"
            f"Collections: Black Rose (gothic/Oakland), Love Hurts (passionate/B&B), "
            f"Signature (Bay Area/SF golden hour)\n"
            f"31 products, price range $25-$265\n\n"
            f"Competitor data: {competitors}\n"
            f"Market context: {market_data}\n\n"
            "Structure the briefing as:\n"
            "1. EXECUTIVE SUMMARY (2-3 sentences)\n"
            "2. THREAT LANDSCAPE (top 3 threats with severity)\n"
            "3. OPPORTUNITY MAP (top 3 market gaps)\n"
            "4. PRICE INTELLIGENCE (positioning recommendations)\n"
            "5. STYLE TRENDS (what's emerging, what's dying)\n"
            "6. STRATEGIC RECOMMENDATIONS (3-5 actionable items)\n\n"
            "Be specific, data-driven, and ruthlessly focused on SkyyRose advantage."
        )

        result = await self._llm_execute(prompt)

        self._emit_intel_signal(
            "Strategic briefing generated",
            {"competitor_count": len(competitors)},
        )

        return {
            "success": True,
            "briefing": result.get("result", ""),
            "type": "strategic_briefing",
            "agent": self.name,
        }

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def _score_to_grade(score: float) -> str:
        if score >= 90:
            return "A+"
        if score >= 85:
            return "A"
        if score >= 80:
            return "A-"
        if score >= 75:
            return "B+"
        if score >= 70:
            return "B"
        if score >= 65:
            return "B-"
        if score >= 60:
            return "C+"
        if score >= 55:
            return "C"
        if score >= 50:
            return "C-"
        if score >= 40:
            return "D"
        return "F"

    def _emit_intel_signal(self, content: str, metadata: dict[str, Any]) -> None:
        """Emit competitive intelligence signal to brand learning loop."""
        loop = self._get_learning_loop()
        if loop is None:
            return
        try:
            from orchestration.brand_learning import BrandSignal, SignalType

            loop.observe(
                BrandSignal(
                    signal_type=SignalType.COMPETITIVE_INTEL,
                    agent_id=self.name,
                    content=content[:500],
                    metadata=metadata,
                )
            )
        except Exception as exc:
            logger.debug("[%s] Intel signal emission failed: %s", self.name, exc)


__all__ = ["BrandIntelAgent"]
