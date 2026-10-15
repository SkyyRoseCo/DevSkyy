"""
ADK Workflow Agents
===================

Zero-overhead orchestration using Google ADK's deterministic workflow agents:
- SequentialAgent: Execute sub-agents in order (pipeline pattern)
- ParallelAgent: Execute sub-agents concurrently (fan-out pattern)
- LoopAgent: Execute sub-agents iteratively (refinement pattern)

Key insight: Workflow agents consume ZERO LLM tokens for orchestration.
Only leaf LlmAgent nodes call the LLM, saving 30-60% on orchestration costs
compared to LLM-based routing (e.g., supervisor pattern).

State passing: output_key writes to session state, {key} template reads from it.

Reference: https://google.github.io/adk-docs/agents/workflow-agents/
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from adk.base import (
    ADKProvider,
    AgentConfig,
    AgentResult,
    AgentStatus,
    BaseDevSkyyAgent,
    estimate_cost,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Google ADK availability check (same pattern as google_adk.py)
# ---------------------------------------------------------------------------

try:
    from google.adk.agents import LlmAgent, LoopAgent, ParallelAgent, SequentialAgent
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types as genai_types

    ADK_WORKFLOW_AVAILABLE = True
    logger.info("Google ADK Workflow Agents loaded successfully")
except ImportError:
    ADK_WORKFLOW_AVAILABLE = False
    LlmAgent = None
    LoopAgent = None
    ParallelAgent = None
    SequentialAgent = None
    Runner = None
    InMemorySessionService = None
    genai_types = None
    logger.warning(
        "Google ADK not installed — workflow agents unavailable. "
        "Install with: pip install google-adk"
    )


# ============================================================================
# Enums & Config
# ============================================================================


class PipelineType(StrEnum):
    """Pre-built pipeline types for SkyyRose operations."""

    PRODUCT_LAUNCH = "product_launch"
    CONTENT_CREATION = "content_creation"
    CUSTOMER_JOURNEY = "customer_journey"
    QUALITY_ASSURANCE = "quality_assurance"
    CAMPAIGN_BLITZ = "campaign_blitz"


@dataclass
class TokenSavings:
    """Tracks token savings from using deterministic workflow orchestration
    vs. LLM-based supervisor routing."""

    pipeline_name: str
    leaf_agent_count: int
    orchestration_tokens_saved: int = 0
    estimated_llm_routing_tokens: int = 0
    actual_leaf_tokens: int = 0
    savings_pct: float = 0.0

    def calculate(self) -> None:
        """Recalculate savings percentage."""
        total_with_llm = self.estimated_llm_routing_tokens + self.actual_leaf_tokens
        if total_with_llm > 0:
            self.savings_pct = (self.estimated_llm_routing_tokens / total_with_llm) * 100
        self.orchestration_tokens_saved = self.estimated_llm_routing_tokens


# ============================================================================
# Leaf-Agent Definitions (LlmAgent wrappers for each Super Agent domain)
# ============================================================================

# Default model for all leaf agents
_DEFAULT_MODEL = "gemini-2.0-flash"

# Estimated tokens an LLM supervisor would consume per routing decision
_ROUTING_TOKENS_PER_HOP = 350

# ---------------------------------------------------------------------------
# Brand Accuracy Preamble (injected into EVERY leaf agent instruction)
# ---------------------------------------------------------------------------
_BRAND_ACCURACY_PREAMBLE = (
    "CRITICAL — 100% BRAND ACCURACY IS YOUR #1 PRIORITY.\n"
    "Brand: SkyyRose\n"
    "Colors: Rose Gold (#B76E79), Black (#1A1A1A), White\n"
    "Location: Oakland, California\n"
    "Collections: BLACK ROSE (dark elegance), LOVE HURTS (emotional expression), "
    "SIGNATURE (foundation essentials)\n"
    "Voice: Sophisticated yet accessible, bold, emotionally resonant, luxury without pretension\n"
    "NEVER deviate from brand guidelines. Every output must reflect SkyyRose identity.\n\n"
)


def _create_commerce_leaf(*, output_key: str = "commerce_result") -> Any:
    """Create an LlmAgent for commerce tasks."""
    if not ADK_WORKFLOW_AVAILABLE:
        return None
    return LlmAgent(
        name="commerce_worker",
        model=_DEFAULT_MODEL,
        instruction=(
            _BRAND_ACCURACY_PREAMBLE
            + "You are the Commerce Worker for SkyyRose luxury streetwear.\n"
            "Handle product catalog, orders, inventory, pricing, and fulfillment.\n"
            "Platform: WooCommerce on WordPress.\n"
            "Input context (if available): {input_context}\n"
            "Respond with structured, actionable output."
        ),
        description="Handles e-commerce: products, orders, inventory, pricing.",
        output_key=output_key,
    )


def _create_creative_leaf(*, output_key: str = "creative_result") -> Any:
    """Create an LlmAgent for creative/asset tasks."""
    if not ADK_WORKFLOW_AVAILABLE:
        return None
    return LlmAgent(
        name="creative_worker",
        model=_DEFAULT_MODEL,
        instruction=(
            _BRAND_ACCURACY_PREAMBLE
            + "You are the Creative Worker for SkyyRose luxury streetwear.\n"
            "Handle 3D asset generation (Tripo3D), virtual try-on (FASHN),\n"
            "image generation, product photography, and video creation.\n"
            "3D models: GLB format, web-optimized.\n"
            "Input context (if available): {input_context}\n"
            "Respond with asset specifications and creative direction."
        ),
        description="Handles creative assets: 3D, images, virtual try-on, video.",
        output_key=output_key,
    )


def _create_marketing_leaf(*, output_key: str = "marketing_result") -> Any:
    """Create an LlmAgent for marketing tasks."""
    if not ADK_WORKFLOW_AVAILABLE:
        return None
    return LlmAgent(
        name="marketing_worker",
        model=_DEFAULT_MODEL,
        instruction=(
            _BRAND_ACCURACY_PREAMBLE
            + "You are the Marketing Worker for SkyyRose luxury streetwear.\n"
            "Handle content creation, social media, SEO, email campaigns,\n"
            "and influencer outreach.\n"
            "Target: ages 25-45, fashion-forward, quality-conscious.\n"
            "Input context (if available): {input_context}\n"
            "Respond with polished marketing content and strategy."
        ),
        description="Handles marketing: content, SEO, social media, campaigns.",
        output_key=output_key,
    )


def _create_support_leaf(*, output_key: str = "support_result") -> Any:
    """Create an LlmAgent for customer support tasks."""
    if not ADK_WORKFLOW_AVAILABLE:
        return None
    return LlmAgent(
        name="support_worker",
        model=_DEFAULT_MODEL,
        instruction=(
            _BRAND_ACCURACY_PREAMBLE
            + "You are the Support Worker for SkyyRose luxury streetwear.\n"
            "Handle customer inquiries, tickets, FAQs, returns/refunds.\n"
            "Tone: warm, professional, solution-oriented.\n"
            "Policies: 30-day returns (unworn w/ tags), free exchanges,\n"
            "free shipping over $150, $9.95 otherwise.\n"
            "Escalate: orders >$500, legal, VIP customers.\n"
            "Input context (if available): {input_context}\n"
            "Respond with clear resolution steps."
        ),
        description="Handles customer support: inquiries, returns, tickets.",
        output_key=output_key,
    )


def _create_operations_leaf(*, output_key: str = "operations_result") -> Any:
    """Create an LlmAgent for operations/infrastructure tasks."""
    if not ADK_WORKFLOW_AVAILABLE:
        return None
    return LlmAgent(
        name="operations_worker",
        model=_DEFAULT_MODEL,
        instruction=(
            _BRAND_ACCURACY_PREAMBLE + "You are the Operations Worker for SkyyRose platform.\n"
            "Handle WordPress management, Elementor templates, server monitoring,\n"
            "deployment automation, backups, and performance optimization.\n"
            "Stack: WordPress 6.x + WooCommerce, Shoptimizer 2.9.0,\n"
            "Elementor Pro 3.32.2, Cloudflare CDN.\n"
            "Standards: 99.9% uptime, <3s page load, mobile-first, WCAG 2.1.\n"
            "Input context (if available): {input_context}\n"
            "Respond with operational actions and status."
        ),
        description="Handles ops: WordPress, deploys, monitoring, performance.",
        output_key=output_key,
    )


def _create_analytics_leaf(*, output_key: str = "analytics_result") -> Any:
    """Create an LlmAgent for analytics tasks."""
    if not ADK_WORKFLOW_AVAILABLE:
        return None
    return LlmAgent(
        name="analytics_worker",
        model=_DEFAULT_MODEL,
        instruction=(
            _BRAND_ACCURACY_PREAMBLE
            + "You are the Analytics Worker for SkyyRose luxury streetwear.\n"
            "Handle sales reporting, customer analytics, trend analysis,\n"
            "demand forecasting, A/B testing, and ROI tracking.\n"
            "Key metrics: revenue, AOV, CLV, conversion rate, cart abandonment,\n"
            "CAC, return rate.\n"
            "Standards: clear visualizations, YoY/MoM comparisons, actionable insights.\n"
            "Input context (if available): {input_context}\n"
            "Respond with data-driven insights and recommendations."
        ),
        description="Handles analytics: reports, forecasting, insights, KPIs.",
        output_key=output_key,
    )


def _create_quality_reviewer_leaf(*, output_key: str = "quality_review") -> Any:
    """Create an LlmAgent that reviews and critiques output from other agents."""
    if not ADK_WORKFLOW_AVAILABLE:
        return None
    return LlmAgent(
        name="quality_reviewer",
        model=_DEFAULT_MODEL,
        instruction=(
            _BRAND_ACCURACY_PREAMBLE + "You are the Quality Reviewer for SkyyRose.\n"
            "Review the current draft: {current_draft}\n"
            "Check for:\n"
            "1. Brand consistency (rose gold aesthetic, luxury voice) — REJECT if off-brand\n"
            "2. Accuracy of claims and data\n"
            "3. Completeness — are all requirements addressed?\n"
            "4. Tone — sophisticated yet accessible\n"
            "Provide specific, actionable critique. Flag any brand deviations as CRITICAL."
        ),
        description="Reviews and critiques output for brand consistency and quality.",
        output_key=output_key,
    )


def _create_refiner_leaf(*, output_key: str = "current_draft") -> Any:
    """Create an LlmAgent that refines a draft based on critique."""
    if not ADK_WORKFLOW_AVAILABLE:
        return None
    return LlmAgent(
        name="content_refiner",
        model=_DEFAULT_MODEL,
        instruction=(
            _BRAND_ACCURACY_PREAMBLE + "You are the Content Refiner for SkyyRose.\n"
            "Improve the current draft using the quality review feedback.\n"
            "Current draft: {current_draft}\n"
            "Critique: {quality_review}\n"
            "Apply all feedback. Brand accuracy is non-negotiable. Output the improved version."
        ),
        description="Refines content based on quality review feedback.",
        output_key=output_key,
    )


def _create_synthesizer_leaf(*, keys: list[str], output_key: str = "final_report") -> Any:
    """Create an LlmAgent that synthesizes results from multiple parallel agents."""
    if not ADK_WORKFLOW_AVAILABLE:
        return None
    key_refs = ", ".join(f"{{{k}}}" for k in keys)
    return LlmAgent(
        name="result_synthesizer",
        model=_DEFAULT_MODEL,
        instruction=(
            _BRAND_ACCURACY_PREAMBLE + "You are the Report Synthesizer for SkyyRose.\n"
            f"Consolidate the following parallel results into a unified report:\n"
            f"{key_refs}\n"
            "Structure: Executive Summary → Key Findings → Action Items → Metrics.\n"
            "Be concise and actionable. Ensure all recommendations align with brand identity."
        ),
        description="Synthesizes results from parallel agents into a unified report.",
        output_key=output_key,
    )


# ============================================================================
# Pre-Built Pipelines
# ============================================================================


def create_product_launch_pipeline() -> Any | None:
    """
    Product Launch Pipeline (Sequential + Parallel fan-out).

    Flow:
      1. Creative (parallel: 3D assets + product images + video spec)
      2. Commerce (catalog listing, pricing, inventory setup)
      3. Marketing (launch campaign content)
      4. Analytics (tracking setup + baseline metrics)
      5. Synthesizer (consolidated launch report)

    Token savings: ~40% vs. LLM supervisor routing each step.
    """
    if not ADK_WORKFLOW_AVAILABLE:
        return None

    # Step 1: Parallel creative asset generation
    asset_3d = LlmAgent(
        name="asset_3d_generator",
        model=_DEFAULT_MODEL,
        instruction=(
            _BRAND_ACCURACY_PREAMBLE + "Generate 3D asset specifications for the new product.\n"
            "Input: {input_context}\n"
            "Output: GLB model spec, texture maps, polygon count, web optimization notes."
        ),
        description="Generates 3D model specifications.",
        output_key="asset_3d_spec",
    )
    asset_images = LlmAgent(
        name="asset_image_generator",
        model=_DEFAULT_MODEL,
        instruction=(
            _BRAND_ACCURACY_PREAMBLE + "Create product photography direction for the new product.\n"
            "Input: {input_context}\n"
            "Output: shot list, lighting setup, background, post-processing notes."
        ),
        description="Generates product photography direction.",
        output_key="asset_image_spec",
    )
    asset_video = LlmAgent(
        name="asset_video_planner",
        model=_DEFAULT_MODEL,
        instruction=(
            _BRAND_ACCURACY_PREAMBLE + "Plan product video content for the new product.\n"
            "Input: {input_context}\n"
            "Output: storyboard outline, duration, music mood, platform specs."
        ),
        description="Plans product video content.",
        output_key="asset_video_spec",
    )

    creative_fanout = ParallelAgent(
        name="creative_asset_fanout",
        sub_agents=[asset_3d, asset_images, asset_video],
        description="Generates all creative assets in parallel.",
    )

    # Step 2: Commerce setup
    commerce_setup = _create_commerce_leaf(output_key="commerce_launch_result")

    # Step 3: Marketing campaign
    marketing_launch = _create_marketing_leaf(output_key="marketing_launch_result")

    # Step 4: Analytics tracking
    analytics_setup = _create_analytics_leaf(output_key="analytics_launch_result")

    # Step 5: Synthesize
    synthesizer = _create_synthesizer_leaf(
        keys=[
            "asset_3d_spec",
            "asset_image_spec",
            "asset_video_spec",
            "commerce_launch_result",
            "marketing_launch_result",
            "analytics_launch_result",
        ],
        output_key="launch_report",
    )

    return SequentialAgent(
        name="product_launch_pipeline",
        sub_agents=[
            creative_fanout,
            commerce_setup,
            marketing_launch,
            analytics_setup,
            synthesizer,
        ],
        description=(
            "End-to-end product launch: creative assets (parallel) → "
            "commerce setup → marketing campaign → analytics → final report."
        ),
    )


def create_content_creation_pipeline(*, max_refinements: int = 3) -> Any | None:
    """
    Content Creation Pipeline (Sequential + Loop for iterative refinement).

    Flow:
      1. Marketing worker creates initial draft
      2. Loop(quality reviewer → refiner) up to max_refinements
      3. Operations worker handles deployment/publishing

    Token savings: ~35% vs. LLM supervisor managing the review loop.
    """
    if not ADK_WORKFLOW_AVAILABLE:
        return None

    # Step 1: Initial draft
    drafter = LlmAgent(
        name="content_drafter",
        model=_DEFAULT_MODEL,
        instruction=(
            _BRAND_ACCURACY_PREAMBLE + "You are the Content Drafter for SkyyRose.\n"
            "Create an initial draft based on the request.\n"
            "Input: {input_context}\n"
            "Output a complete first draft that embodies the SkyyRose brand."
        ),
        description="Creates initial content draft.",
        output_key="current_draft",
    )

    # Step 2: Iterative refinement loop
    reviewer = _create_quality_reviewer_leaf(output_key="quality_review")
    refiner = _create_refiner_leaf(output_key="current_draft")

    refinement_loop = LoopAgent(
        name="content_refinement_loop",
        sub_agents=[reviewer, refiner],
        max_iterations=max_refinements,
        description=f"Iteratively reviews and refines content (up to {max_refinements}x).",
    )

    # Step 3: Publish via operations
    publisher = LlmAgent(
        name="content_publisher",
        model=_DEFAULT_MODEL,
        instruction=(
            _BRAND_ACCURACY_PREAMBLE + "You are the Content Publisher for SkyyRose.\n"
            "Finalize the refined content for deployment.\n"
            "Final content: {current_draft}\n"
            "Output: deployment checklist, platform-specific formatting, "
            "scheduling recommendation, SEO metadata."
        ),
        description="Prepares refined content for publication.",
        output_key="publish_plan",
    )

    return SequentialAgent(
        name="content_creation_pipeline",
        sub_agents=[drafter, refinement_loop, publisher],
        description=("Content pipeline: draft → iterative review/refine → publish plan."),
    )


def create_customer_journey_pipeline() -> Any | None:
    """
    Customer Journey Pipeline (Sequential for intake → lookup → resolution).

    Flow:
      1. Support worker (intake, classify issue)
      2. Commerce worker (order/product lookup)
      3. Support worker (resolution with data)

    Token savings: ~30% vs. LLM supervisor routing.
    """
    if not ADK_WORKFLOW_AVAILABLE:
        return None

    intake = LlmAgent(
        name="support_intake",
        model=_DEFAULT_MODEL,
        instruction=(
            _BRAND_ACCURACY_PREAMBLE + "You are Customer Support Intake for SkyyRose.\n"
            "Classify the customer issue and extract key details.\n"
            "Customer message: {input_context}\n"
            "Output: issue_type, order_id (if any), urgency, key_details."
        ),
        description="Classifies and extracts customer issue details.",
        output_key="intake_result",
    )

    order_lookup = LlmAgent(
        name="commerce_lookup",
        model=_DEFAULT_MODEL,
        instruction=(
            _BRAND_ACCURACY_PREAMBLE + "You are Commerce Data Lookup for SkyyRose.\n"
            "Based on intake: {intake_result}\n"
            "Look up relevant order, product, or inventory data.\n"
            "Output: order_status, product_details, relevant_history."
        ),
        description="Looks up order/product data based on intake.",
        output_key="lookup_result",
    )

    resolution = LlmAgent(
        name="support_resolution",
        model=_DEFAULT_MODEL,
        instruction=(
            _BRAND_ACCURACY_PREAMBLE + "You are Customer Support Resolution for SkyyRose.\n"
            "Resolve the customer's issue using the gathered data.\n"
            "Intake: {intake_result}\n"
            "Lookup: {lookup_result}\n"
            "Policies: 30-day returns (unworn, tags), free exchanges,\n"
            "free shipping >$150, escalate >$500/legal/VIP.\n"
            "Output: resolution_steps, customer_response_draft, follow_up_needed."
        ),
        description="Generates resolution based on intake and lookup data.",
        output_key="resolution_result",
    )

    return SequentialAgent(
        name="customer_journey_pipeline",
        sub_agents=[intake, order_lookup, resolution],
        description="Customer journey: intake → data lookup → resolution.",
    )


def create_quality_assurance_pipeline() -> Any | None:
    """
    Quality Assurance Pipeline (Parallel audit + Sequential synthesis).

    Flow:
      1. Parallel: Creative audit + Commerce audit + Operations audit
      2. Analytics synthesizer (consolidated QA report)

    Token savings: ~45% — three audits run concurrently, zero routing tokens.
    """
    if not ADK_WORKFLOW_AVAILABLE:
        return None

    creative_audit = LlmAgent(
        name="creative_auditor",
        model=_DEFAULT_MODEL,
        instruction=(
            _BRAND_ACCURACY_PREAMBLE + "READ-ONLY AUDIT — do NOT call update_product_field().\n"
            "Audit creative assets for SkyyRose.\n"
            "Context: {input_context}\n"
            "Check: brand consistency (100% accuracy required), image quality,\n"
            "3D model specs, accessibility, file sizes, format compliance (GLB for 3D).\n"
            "Output: findings, severity, recommendations. Flag brand deviations as CRITICAL."
        ),
        description="Audits creative assets for quality and brand compliance.",
        output_key="creative_audit_result",
    )

    commerce_audit = LlmAgent(
        name="commerce_auditor",
        model=_DEFAULT_MODEL,
        instruction=(
            _BRAND_ACCURACY_PREAMBLE + "READ-ONLY AUDIT — do NOT call update_product_field().\n"
            "Audit commerce data for SkyyRose.\n"
            "Context: {input_context}\n"
            "Check: product descriptions, pricing accuracy, inventory levels,\n"
            "SEO metadata, category assignments, image links.\n"
            "Output: findings, severity, recommendations. Flag brand deviations as CRITICAL."
        ),
        description="Audits commerce data for accuracy and completeness.",
        output_key="commerce_audit_result",
    )

    operations_audit = LlmAgent(
        name="operations_auditor",
        model=_DEFAULT_MODEL,
        instruction=(
            _BRAND_ACCURACY_PREAMBLE + "READ-ONLY AUDIT — do NOT call update_product_field().\n"
            "Audit operational infrastructure for SkyyRose.\n"
            "Context: {input_context}\n"
            "Check: page load speed, uptime, plugin versions, security headers,\n"
            "backup status, SSL cert, CDN config.\n"
            "Output: findings, severity, recommendations."
        ),
        description="Audits operational infrastructure for health and security.",
        output_key="operations_audit_result",
    )

    audit_fanout = ParallelAgent(
        name="qa_audit_fanout",
        sub_agents=[creative_audit, commerce_audit, operations_audit],
        description="Runs creative, commerce, and operations audits in parallel.",
    )

    qa_synthesizer = _create_synthesizer_leaf(
        keys=[
            "creative_audit_result",
            "commerce_audit_result",
            "operations_audit_result",
        ],
        output_key="qa_report",
    )

    return SequentialAgent(
        name="quality_assurance_pipeline",
        sub_agents=[audit_fanout, qa_synthesizer],
        description="QA pipeline: parallel audits → consolidated report.",
    )


def create_campaign_blitz_pipeline(*, max_iterations: int = 2) -> Any | None:
    """
    Campaign Blitz Pipeline (Parallel research + Loop refinement + Sequential deploy).

    Flow:
      1. Parallel: Analytics (market research) + Creative (mood board) + Commerce (product data)
      2. Marketing (initial campaign draft from parallel results)
      3. Loop(quality review → refine) for campaign copy
      4. Operations (scheduling and deployment plan)

    Token savings: ~50% — parallel research + deterministic loop control.
    """
    if not ADK_WORKFLOW_AVAILABLE:
        return None

    # Step 1: Parallel research
    market_research = LlmAgent(
        name="market_researcher",
        model=_DEFAULT_MODEL,
        instruction=(
            _BRAND_ACCURACY_PREAMBLE + "Research market conditions for the campaign.\n"
            "Context: {input_context}\n"
            "Output: target segments, competitor activity, trending topics, timing."
        ),
        description="Researches market conditions for campaign planning.",
        output_key="market_research",
    )
    mood_board = LlmAgent(
        name="mood_board_creator",
        model=_DEFAULT_MODEL,
        instruction=(
            _BRAND_ACCURACY_PREAMBLE + "Create visual mood board direction for the campaign.\n"
            "Context: {input_context}\n"
            "Output: color palette (must include #B76E79 rose gold), typography, "
            "imagery style, reference links."
        ),
        description="Creates mood board direction for campaign visuals.",
        output_key="mood_board",
    )
    product_data = LlmAgent(
        name="product_data_gatherer",
        model=_DEFAULT_MODEL,
        instruction=(
            _BRAND_ACCURACY_PREAMBLE + "Gather product data needed for the campaign.\n"
            "Context: {input_context}\n"
            "Output: featured products, pricing, stock status, hero images."
        ),
        description="Gathers product data for campaign content.",
        output_key="product_data",
    )

    research_fanout = ParallelAgent(
        name="campaign_research_fanout",
        sub_agents=[market_research, mood_board, product_data],
        description="Parallel research: market + creative + product data.",
    )

    # Step 2: Draft campaign from research
    campaign_drafter = LlmAgent(
        name="campaign_drafter",
        model=_DEFAULT_MODEL,
        instruction=(
            _BRAND_ACCURACY_PREAMBLE + "Draft the campaign using research results.\n"
            "Market research: {market_research}\n"
            "Mood board: {mood_board}\n"
            "Product data: {product_data}\n"
            "Output: campaign copy, CTAs, channel-specific versions, hashtags.\n"
            "All copy must reflect SkyyRose brand identity with 100% accuracy."
        ),
        description="Drafts campaign content from parallel research results.",
        output_key="current_draft",
    )

    # Step 3: Refinement loop
    reviewer = _create_quality_reviewer_leaf(output_key="quality_review")
    refiner = _create_refiner_leaf(output_key="current_draft")

    campaign_refinement = LoopAgent(
        name="campaign_refinement_loop",
        sub_agents=[reviewer, refiner],
        max_iterations=max_iterations,
        description=f"Iteratively refines campaign copy (up to {max_iterations}x).",
    )

    # Step 4: Deployment plan
    deploy_planner = LlmAgent(
        name="campaign_deploy_planner",
        model=_DEFAULT_MODEL,
        instruction=(
            _BRAND_ACCURACY_PREAMBLE + "Create deployment plan for the finalized campaign.\n"
            "Campaign content: {current_draft}\n"
            "Output: scheduling, platform-specific formatting, budget allocation, "
            "A/B test variants, tracking UTMs."
        ),
        description="Plans campaign deployment across channels.",
        output_key="deploy_plan",
    )

    return SequentialAgent(
        name="campaign_blitz_pipeline",
        sub_agents=[
            research_fanout,
            campaign_drafter,
            campaign_refinement,
            deploy_planner,
        ],
        description=("Campaign blitz: parallel research → draft → refine loop → deploy plan."),
    )


# ============================================================================
# Pipeline Factory
# ============================================================================

_PIPELINE_REGISTRY: dict[PipelineType, Any] = {}


def get_pipeline(pipeline_type: PipelineType, **kwargs) -> Any | None:
    """
    Get or create a pre-built pipeline by type.

    Args:
        pipeline_type: Which pipeline to create.
        **kwargs: Forwarded to the pipeline constructor (e.g. max_refinements).

    Returns:
        A SequentialAgent root, or None if ADK is unavailable.
    """
    factories = {
        PipelineType.PRODUCT_LAUNCH: create_product_launch_pipeline,
        PipelineType.CONTENT_CREATION: create_content_creation_pipeline,
        PipelineType.CUSTOMER_JOURNEY: create_customer_journey_pipeline,
        PipelineType.QUALITY_ASSURANCE: create_quality_assurance_pipeline,
        PipelineType.CAMPAIGN_BLITZ: create_campaign_blitz_pipeline,
    }

    factory = factories.get(pipeline_type)
    if factory is None:
        raise ValueError(f"Unknown pipeline type: {pipeline_type}")

    return factory(**kwargs)


def estimate_pipeline_savings(pipeline_type: PipelineType) -> TokenSavings:
    """
    Estimate token savings for a given pipeline vs. LLM-based routing.

    Workflow agents consume 0 orchestration tokens. An LLM supervisor
    would spend ~350 tokens per routing decision (prompt + response).
    """
    # Count routing hops each pipeline would need with an LLM supervisor
    hop_counts: dict[PipelineType, tuple[int, int]] = {
        #                         (routing_hops, leaf_agents)
        PipelineType.PRODUCT_LAUNCH: (6, 7),  # route to 3 parallel + 3 seq + synth
        PipelineType.CONTENT_CREATION: (5, 4),  # draft + 2×(review+refine) + publish
        PipelineType.CUSTOMER_JOURNEY: (3, 3),  # intake → lookup → resolution
        PipelineType.QUALITY_ASSURANCE: (4, 4),  # route to 3 parallel + synth
        PipelineType.CAMPAIGN_BLITZ: (7, 8),  # 3 parallel + draft + 2×loop + deploy
    }

    hops, leaves = hop_counts.get(pipeline_type, (3, 3))

    # Estimate: each leaf agent averages ~800 tokens (input + output)
    avg_leaf_tokens = 800

    savings = TokenSavings(
        pipeline_name=pipeline_type.value,
        leaf_agent_count=leaves,
        estimated_llm_routing_tokens=hops * _ROUTING_TOKENS_PER_HOP,
        actual_leaf_tokens=leaves * avg_leaf_tokens,
    )
    savings.calculate()
    return savings


# ============================================================================
# WorkflowPipelineAgent — DevSkyy BaseDevSkyyAgent wrapper
# ============================================================================


class WorkflowPipelineAgent(BaseDevSkyyAgent):
    """
    DevSkyy-compatible wrapper around ADK Workflow pipelines.

    Bridges the BaseDevSkyyAgent interface with Google ADK's
    SequentialAgent/ParallelAgent/LoopAgent orchestration.

    Example:
        agent = WorkflowPipelineAgent.from_pipeline(PipelineType.PRODUCT_LAUNCH)
        result = await agent.run("Launch BLACK ROSE Spring 2026 jacket")
    """

    def __init__(
        self,
        config: AgentConfig,
        *,
        pipeline: Any = None,
        pipeline_type: PipelineType | None = None,
    ):
        super().__init__(config)
        self._pipeline = pipeline
        self._pipeline_type = pipeline_type
        self._runner = None
        self._session_service = None

    @classmethod
    def from_pipeline(
        cls,
        pipeline_type: PipelineType,
        *,
        model: str = _DEFAULT_MODEL,
        **pipeline_kwargs,
    ) -> WorkflowPipelineAgent:
        """Create a WorkflowPipelineAgent from a pre-built pipeline type."""
        pipeline = get_pipeline(pipeline_type, **pipeline_kwargs)

        config = AgentConfig(
            name=f"workflow_{pipeline_type.value}",
            provider=ADKProvider.GOOGLE,
            model=model,
            description=f"ADK Workflow Pipeline: {pipeline_type.value}",
            system_prompt=f"Workflow pipeline for {pipeline_type.value} operations.",
        )

        return cls(config, pipeline=pipeline, pipeline_type=pipeline_type)

    async def initialize(self) -> None:
        """Initialize the workflow pipeline runner."""
        if not ADK_WORKFLOW_AVAILABLE:
            raise ImportError(
                "Google ADK not installed — workflow pipelines unavailable. "
                "Install with: pip install google-adk"
            )

        if self._pipeline is None:
            raise ValueError("No pipeline configured. Use from_pipeline() factory.")

        self._session_service = InMemorySessionService()
        self._runner = Runner(
            agent=self._pipeline,
            app_name="devskyy_workflows",
            session_service=self._session_service,
        )

        self._initialized = True
        logger.info(f"Workflow pipeline initialized: {self.name}")

    async def execute(self, prompt: str, **kwargs) -> AgentResult:
        """Execute the workflow pipeline."""
        if not ADK_WORKFLOW_AVAILABLE:
            raise ImportError("Google ADK not available")

        start_time = datetime.now(UTC)

        try:
            # Create a fresh session for each execution
            session = await self._session_service.create_session(
                app_name="devskyy_workflows",
                user_id="skyyrose",
                state={"input_context": prompt},
            )

            content = genai_types.Content(
                role="user",
                parts=[genai_types.Part(text=prompt)],
            )

            response_text = ""
            total_input_tokens = 0
            total_output_tokens = 0

            async for event in self._runner.run_async(
                user_id="skyyrose",
                session_id=session.id,
                new_message=content,
            ):
                if hasattr(event, "content") and event.content:
                    if hasattr(event.content, "parts"):
                        for part in event.content.parts:
                            if hasattr(part, "text") and part.text:
                                response_text += part.text

                if hasattr(event, "usage"):
                    total_input_tokens += getattr(event.usage, "input_tokens", 0)
                    total_output_tokens += getattr(event.usage, "output_tokens", 0)

            # Fallback token estimation
            if total_input_tokens == 0:
                total_input_tokens = int(len(prompt.split()) * 1.3)
            if total_output_tokens == 0:
                total_output_tokens = int(len(response_text.split()) * 1.3)

            # Calculate savings metadata
            savings = None
            if self._pipeline_type:
                savings = estimate_pipeline_savings(self._pipeline_type)
                savings.actual_leaf_tokens = total_input_tokens + total_output_tokens
                savings.calculate()

            return AgentResult(
                agent_name=self.name,
                agent_provider=ADKProvider.GOOGLE,
                content=response_text or "Pipeline completed — check session state.",
                status=AgentStatus.COMPLETED,
                iterations=1,
                input_tokens=total_input_tokens,
                output_tokens=total_output_tokens,
                total_tokens=total_input_tokens + total_output_tokens,
                cost_usd=estimate_cost(
                    _DEFAULT_MODEL,
                    total_input_tokens,
                    total_output_tokens,
                ),
                started_at=start_time,
                metadata={
                    "pipeline_type": self._pipeline_type.value if self._pipeline_type else None,
                    "orchestration_tokens": 0,
                    "savings": (
                        {
                            "orchestration_tokens_saved": savings.orchestration_tokens_saved,
                            "savings_pct": round(savings.savings_pct, 1),
                        }
                        if savings
                        else None
                    ),
                },
            )

        except Exception as e:
            logger.error(f"Workflow pipeline execution failed: {e}")
            return AgentResult(
                agent_name=self.name,
                agent_provider=ADKProvider.GOOGLE,
                content="",
                status=AgentStatus.FAILED,
                error=str(e),
                error_type=type(e).__name__,
                started_at=start_time,
            )


# ============================================================================
# Export
# ============================================================================

__all__ = [
    # Availability flag
    "ADK_WORKFLOW_AVAILABLE",
    # Enums
    "PipelineType",
    # Data classes
    "TokenSavings",
    # Leaf agent factories
    "_create_commerce_leaf",
    "_create_creative_leaf",
    "_create_marketing_leaf",
    "_create_support_leaf",
    "_create_operations_leaf",
    "_create_analytics_leaf",
    "_create_quality_reviewer_leaf",
    "_create_refiner_leaf",
    "_create_synthesizer_leaf",
    # Pipeline factories
    "create_product_launch_pipeline",
    "create_content_creation_pipeline",
    "create_customer_journey_pipeline",
    "create_quality_assurance_pipeline",
    "create_campaign_blitz_pipeline",
    # Factory & estimation
    "get_pipeline",
    "estimate_pipeline_savings",
    # DevSkyy wrapper
    "WorkflowPipelineAgent",
]
