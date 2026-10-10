"""SkyyRose Content Agent for DevSkyy Platform.

Handles WordPress content creation and page management for the
SkyyRose website. Uses Gemini as its primary LLM, pre-gathers
brand DNA and existing assets before any content generation,
and continuously learns from performance to improve output.

Author: DevSkyy Platform Team
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from adk.base import ADKProvider, AgentResult, AgentStatus
from agents.base_super_agent import EnhancedSuperAgent, LearningRecord, SuperAgentType
from llm.base import CompletionResponse, Message
from llm.model_ids import GEMINI_VISION_MODEL
from llm.providers.google import GoogleClient
from orchestration.brand_context import BrandContextInjector, Collection

logger = logging.getLogger(__name__)


# =============================================================================
# Data Models
# =============================================================================


class ContentType(StrEnum):
    """Types of WordPress content."""

    PAGE = "page"
    PRODUCT_DESCRIPTION = "product_description"
    COLLECTION_PAGE = "collection_page"
    BLOG_POST = "blog_post"
    HERO_COPY = "hero_copy"
    LANDING_PAGE = "landing_page"
    SEO_META = "seo_meta"
    EMAIL_CAMPAIGN = "email_campaign"


class ContentStatus(StrEnum):
    """Content lifecycle status."""

    DRAFTED = "drafted"
    REVIEWED = "reviewed"
    PUBLISHED = "published"
    UPDATED = "updated"
    ARCHIVED = "archived"


def _safe_collection_value(collection: Collection | str | None) -> str:
    """Safely extract collection string value from enum or string.

    Args:
        collection: Collection enum, string representation, or None

    Returns:
        Lowercase hyphenated collection string (e.g., "signature", "black-rose")
        Empty string if collection is None

    Examples:
        >>> _safe_collection_value(Collection.SIGNATURE)
        'signature'
        >>> _safe_collection_value("SIGNATURE")
        'signature'
        >>> _safe_collection_value("signature")
        'signature'
        >>> _safe_collection_value(None)
        ''
    """
    if collection is None:
        return ""

    if isinstance(collection, Collection):
        return collection.value

    if isinstance(collection, str):
        # Handle both formats: "SIGNATURE" (enum name) or "signature" (enum value)
        # First try to convert to enum
        try:
            normalized = collection.upper().replace("-", "_")
            return Collection[normalized].value
        except (KeyError, AttributeError):
            # If it's already in value format (lowercase with hyphens), return as-is
            return collection.lower().replace("_", "-")

    return ""


@dataclass
class BrandDNA:
    """Accumulated brand awareness gathered before content creation.

    The Content Agent NEVER generates content without first loading
    all available brand DNA. This ensures consistency across every
    piece of content.
    """

    brand_name: str = "SkyyRose"
    origin: str = "Oakland, CA"

    # Visual identity loaded from brand context
    primary_color: str = "#B76E79"
    secondary_color: str = "#1A1A1A"
    accent_gold: str = "#C9A962"

    # Tone and voice
    tone_descriptors: list[str] = field(
        default_factory=lambda: [
            "sophisticated",
            "bold",
            "romantic",
            "empowering",
            "Oakland-rooted",
            "luxury streetwear with soul",
        ]
    )
    tone_avoid: list[str] = field(
        default_factory=lambda: [
            "generic",
            "corporate",
            "mass-market",
            "impersonal",
            "overly casual",
        ]
    )

    # Collections
    collections: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {
            "signature": {
                "name": "Signature Collection",
                "mood": "Regal, timeless, commanding",
                "metal": "18k Gold",
                "color": "#C9A962",
                "tagline": "Define a generation of discerning taste",
            },
            "black-rose": {
                "name": "Black Rose Collection",
                "mood": "Gothic elegance, mysterious, shadow and light",
                "metal": "925 Sterling Silver",
                "color": "#C0C0C0",
                "tagline": "Where shadow dances with silver",
            },
            "love-hurts": {
                "name": "Love Hurts Collection",
                "mood": "Passionate vulnerability, tender romance",
                "metal": "Rose Gold",
                "color": "#B76E79",
                "tagline": "Where passion meets fragility",
            },
        }
    )

    # Existing site context (gathered from live site)
    existing_pages: list[str] = field(default_factory=list)
    existing_products: list[str] = field(default_factory=list)
    site_navigation_structure: dict[str, Any] = field(default_factory=dict)

    # Audience insights
    target_audience: str = "Discerning luxury fashion consumers aged 25-45"
    value_proposition: str = "Limited edition luxury pieces that tell a story"

    # Content performance history (for continuous learning)
    top_performing_headlines: list[str] = field(default_factory=list)
    top_performing_themes: list[str] = field(default_factory=list)
    content_feedback_scores: dict[str, float] = field(default_factory=dict)

    gathered_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_prompt_context(self) -> str:
        """Convert brand DNA to a comprehensive prompt context block."""
        collections_text = "\n".join(
            f"  - {data['name']}: {data['mood']}. Metal: {data['metal']}. "
            f"Tagline: {data['tagline']}"
            for data in self.collections.values()
        )

        learning_context = ""
        if self.top_performing_headlines:
            learning_context += (
                "\nPREVIOUS HIGH-PERFORMING HEADLINES (learn from these patterns):\n"
                + "\n".join(f"  - {h}" for h in self.top_performing_headlines[:5])
            )
        if self.top_performing_themes:
            learning_context += "\nRECURRING SUCCESSFUL THEMES:\n" + "\n".join(
                f"  - {t}" for t in self.top_performing_themes[:5]
            )

        return f"""
BRAND DNA — SKYYROSE
====================
Brand: {self.brand_name}
Origin: {self.origin}
Target: {self.target_audience}
Value Proposition: {self.value_proposition}

VISUAL IDENTITY:
  Primary: {self.primary_color} | Secondary: {self.secondary_color} | Accent: {self.accent_gold}

VOICE & TONE:
  Embody: {", ".join(self.tone_descriptors)}
  Avoid: {", ".join(self.tone_avoid)}

COLLECTIONS:
{collections_text}

SITE CONTEXT:
  Existing Pages: {", ".join(self.existing_pages) if self.existing_pages else "N/A"}
  Navigation: {json.dumps(self.site_navigation_structure) if self.site_navigation_structure else "Standard"}
{learning_context}
"""


@dataclass
class ContentRequest:
    """Request for content generation."""

    content_type: ContentType
    collection: Collection | None = None
    title: str = ""
    target_url: str = ""
    seo_keywords: list[str] = field(default_factory=list)
    additional_direction: str = ""
    reference_imagery: list[str] = field(default_factory=list)
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GeneratedContent:
    """Generated content ready for WordPress."""

    content_type: ContentType
    content_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    collection: Collection | None = None
    title: str = ""
    body_html: str = ""
    excerpt: str = ""
    seo_title: str = ""
    seo_description: str = ""
    seo_keywords: list[str] = field(default_factory=list)
    status: ContentStatus = ContentStatus.DRAFTED
    wp_post_id: int | None = None
    correlation_id: str = ""
    prompt_hash: str = ""
    gemini_tokens_used: int = 0
    feedback_score: float | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Agent
# =============================================================================


class SkyyRoseContentAgent(EnhancedSuperAgent):
    """Content Agent for SkyyRose WordPress pages and content.

    Uses Gemini as its primary LLM engine. Before generating ANY content,
    this agent performs a full brand DNA gathering pass — pulling existing
    site context, brand assets, collection metadata, and performance
    history to ensure perfect brand consistency.

    Continuous Learning:
    - Tracks content performance via feedback scores
    - Records top-performing headlines and themes
    - Adjusts generation patterns based on what resonates
    - Persists learning state across sessions

    WordPress Integration (wordpress-ops):
    - Creates/updates posts and pages via REST API
    - Follows wordpress-ops URL patterns (index.php?rest_route=)
    - Tags content with _skyyrose_collection metadata
    - Creates products as draft for review

    Capabilities:
    - Full page content generation (hero, landing, collection)
    - Product descriptions with brand voice
    - SEO-optimized meta tags
    - Blog posts and campaign copy
    - Continuous learning from content performance
    """

    agent_type = SuperAgentType.CREATIVE
    AGENT_NAME = "skyyrose_content_agent"
    AGENT_VERSION = "1.0.0"

    SYSTEM_PROMPT = """You are the SkyyRose Content Agent for DevSkyy.

Your purpose: Create WordPress content and pages for https://skyyrose.co
that are perfectly on-brand, SEO-optimized, and conversion-focused.

CRITICAL RULE: You NEVER generate content without first having Brand DNA loaded.
The Brand DNA context will be provided before every generation call.
Read it thoroughly — it contains everything you need.

Brand: SkyyRose — Oakland-inspired luxury fashion.

Your workflow:
1. Brand DNA is pre-loaded (brand context, collections, performance history)
2. Analyze the content request against brand standards
3. Generate content that embodies the brand voice
4. Include SEO optimization (title, meta, keywords)
5. Structure for WordPress page/post deployment
6. Output structured JSON for wordpress-ops integration

Content Voice Rules:
- Sophisticated but accessible
- Bold and confident, never arrogant
- Romantic undertones without being cloying
- Oakland authenticity meets global luxury
- Every sentence should make someone FEEL something
- Short paragraphs. White space matters.

SEO Rules:
- Include target keywords naturally
- Meta descriptions under 160 characters
- Title tags under 60 characters
- Heading hierarchy (H1 → H2 → H3) must be logical
- Internal links to other collections when relevant
"""

    def __init__(self, config: Any = None, **kwargs: Any) -> None:
        """Initialize SkyyRose Content Agent."""
        from adk.base import ADKProvider as _ADKProvider
        from adk.base import AgentConfig as _AgentConfig

        # Extract agent-specific kwargs before passing to super
        self._default_wp_client: Any = kwargs.pop("wp_client", None)

        if config is None:
            config = _AgentConfig(
                name=self.AGENT_NAME,
                provider=_ADKProvider.PYDANTIC,
                system_prompt=self.SYSTEM_PROMPT,
            )
        super().__init__(config, **kwargs)
        self.brand_context = BrandContextInjector(
            include_colors=True,
            include_audience=True,
            include_quality=True,
        )
        self._gemini: GoogleClient | None = None
        self._brand_dna: BrandDNA | None = None
        self._content_log: list[GeneratedContent] = []
        self._learning_records: list[LearningRecord] = []
        self._learning_state_path = os.getenv(
            "SKYYROSE_CONTENT_LEARNING_PATH",
            ".skyyrose_content_learning.json",
        )

    async def execute(self, prompt: str, **kwargs: Any) -> AgentResult:
        """Execute content generation task from a text prompt."""
        content_type_str = kwargs.get("content_type", "page")
        collection_name = kwargs.get("collection")
        request = ContentRequest(
            content_type=ContentType(content_type_str),
            collection=Collection(collection_name) if collection_name else None,
            additional_direction=prompt,
        )
        content = await self.generate_content(request)
        return AgentResult(
            agent_name="skyyrose_content_agent",
            agent_provider=ADKProvider.INTERNAL,
            content=content.body_html,
            structured_output={
                "content_id": content.content_id,
                "title": content.title,
                "status": content.status.value,
            },
            status=AgentStatus.COMPLETED if content.body_html else AgentStatus.FAILED,
        )

    # =========================================================================
    # Gemini Client
    # =========================================================================

    async def _get_gemini(self) -> GoogleClient:
        """Lazy-initialize Gemini client."""
        if not self._gemini:
            self._gemini = GoogleClient(
                api_key=os.getenv("GOOGLE_API_KEY"),
            )
            await self._gemini.connect()
        return self._gemini

    # =========================================================================
    # Brand DNA Gathering (MUST run before content generation)
    # =========================================================================

    async def gather_brand_dna(
        self,
        wp_client: Any | None = None,
        refresh: bool = False,
    ) -> BrandDNA:
        """Gather comprehensive brand DNA before any content generation.

        This is the core pre-generation step. Pulls:
        - Brand identity from BrandContextInjector
        - Existing site structure (if wp_client provided)
        - Collection metadata and visual identity
        - Performance history from learning state
        - Audience and positioning data

        Args:
            wp_client: Optional WordPressComClient for live site data
            refresh: Force refresh even if DNA already loaded

        Returns:
            Fully populated BrandDNA instance
        """
        if self._brand_dna and not refresh:
            logger.info(f"{self.AGENT_NAME}: Brand DNA already loaded, using cached")
            return self._brand_dna

        logger.info(f"{self.AGENT_NAME}: Gathering brand DNA...")

        dna = BrandDNA()

        # Load from BrandContextInjector
        brand_prompt = self.brand_context.get_system_prompt()
        logger.debug(f"{self.AGENT_NAME}: Loaded brand system prompt ({len(brand_prompt)} chars)")

        # Gather existing site context from WordPress (if client available)
        if wp_client:
            try:
                # Fetch existing posts/pages for context
                existing = await wp_client._wp_request(
                    "GET",
                    "/wp-json/wp/v2/pages?per_page=50&status=publish",
                )
                if existing:
                    dna.existing_pages = [
                        p.get("title", {}).get("rendered", "") for p in existing if p.get("title")
                    ]
                    dna.site_navigation_structure = {
                        p.get("slug", ""): p.get("link", "") for p in existing
                    }
                    logger.info(
                        f"{self.AGENT_NAME}: Gathered {len(dna.existing_pages)} existing pages"
                    )
            except Exception as e:
                logger.warning(f"{self.AGENT_NAME}: Could not fetch live site data: {e}")

        # Load continuous learning state
        self._load_learning_state(dna)

        self._brand_dna = dna
        logger.info(
            f"{self.AGENT_NAME}: Brand DNA gathered. "
            f"Collections: {len(dna.collections)}, "
            f"Top headlines: {len(dna.top_performing_headlines)}, "
            f"Existing pages: {len(dna.existing_pages)}"
        )

        return dna

    # =========================================================================
    # Content Generation via Gemini
    # =========================================================================

    async def generate_content(
        self,
        request: ContentRequest,
        wp_client: Any | None = None,
    ) -> GeneratedContent:
        """Generate content using Gemini with full brand DNA context.

        Workflow:
        1. Ensure Brand DNA is gathered
        2. Build brand-aware prompt for Gemini
        3. Call Gemini with structured output expectations
        4. Parse and structure the response
        5. Record for continuous learning

        Args:
            request: Content generation request
            wp_client: Optional WP client for brand DNA gathering

        Returns:
            GeneratedContent ready for WordPress deployment

        Raises:
            RuntimeError: If brand DNA not gathered
        """
        # CRITICAL: Ensure brand DNA is loaded
        if not self._brand_dna:
            await self.gather_brand_dna(wp_client=wp_client)

        if not self._brand_dna:
            raise RuntimeError(
                "Brand DNA could not be gathered. Cannot generate content without brand context."
            )

        logger.info(
            f"{self.AGENT_NAME}: Generating {request.content_type.value} content "
            f"[corr={request.correlation_id}]"
        )

        # Build the full prompt with brand DNA
        messages = self._build_generation_messages(request)

        # Call Gemini
        gemini = await self._get_gemini()
        response = await gemini.complete(
            messages=messages,
            model=GEMINI_VISION_MODEL,
            temperature=0.7,
            max_tokens=4096,
        )

        # Parse structured response
        content = self._parse_gemini_response(response, request)

        # Brand-copy quality gate — soft-signal, opt-in via COPY_EVAL_ENABLED. Never blocks.
        content = await self._maybe_eval_copy(content, request)

        # Record for learning
        self._record_generation(content, request, response)

        logger.info(
            f"{self.AGENT_NAME}: Content generated — {content.title} "
            f"[tokens={content.gemini_tokens_used}]"
        )

        return content

    def _build_copy_brief(self, content: GeneratedContent, request: ContentRequest) -> Any:
        """Assemble the CopyBrief the evaluator scores against (pure field mapping)."""
        from evaluation.domains.copy import CopyBrief

        return CopyBrief(
            collection=content.collection.value if content.collection else None,
            content_type=request.content_type.value,
            product_name=request.title or None,
            brand_voice_context=(self._brand_dna.to_prompt_context() if self._brand_dna else ""),
            additional_direction=request.additional_direction or "",
        )

    async def _maybe_eval_copy(
        self,
        content: GeneratedContent,
        request: ContentRequest,
        *,
        evaluator: Any = None,
    ) -> GeneratedContent:
        """Soft-signal brand-copy quality gate.

        Opt-in via the COPY_EVAL_ENABLED env flag. When enabled, scores the generated
        body against brand canon with the Claude copy judge and records the verdict in
        ``content.metadata['copy_eval']``. It NEVER blocks — failing copy is returned
        unchanged (the judge is uncalibrated; promote to a hard gate only after a
        calibration run, per evaluation.calibration.decide_mode). ``evaluator`` is a
        dependency-injection seam for tests; production builds the real judge lazily.
        """
        if not os.getenv("COPY_EVAL_ENABLED"):
            return content
        if evaluator is None:
            from evaluation.agents import CopyEvaluator
            from evaluation.judge import ClaudeJudge, make_client

            judge = ClaudeJudge(client=make_client(), model="claude-sonnet-4-6")
            evaluator = CopyEvaluator(judge_fn=lambda req: judge.run(**req))

        try:
            brief = self._build_copy_brief(content, request)
            verdict = await evaluator.evaluate(subject=content.body_html, ref=brief)
            logger.info(
                "%s: copy_eval passed=%s score=%.2f cost=$%.4f tags=%s",
                self.AGENT_NAME,
                verdict.passed,
                verdict.score,
                verdict.cost_usd,
                list(verdict.failure_tags),
            )
            content.metadata["copy_eval"] = {
                "passed": verdict.passed,
                "score": verdict.score,
                "failure_tags": list(verdict.failure_tags),
                "reason": verdict.reason,
                "cost_usd": verdict.cost_usd,
            }
        except Exception as exc:  # noqa: BLE001 — advisory gate must never block generation
            logger.warning(
                "%s: copy_eval skipped — evaluator raised %s: %s",
                self.AGENT_NAME,
                type(exc).__name__,
                exc,
            )
            content.metadata["copy_eval"] = {"error": f"{type(exc).__name__}: {exc}"}
        return content

    def _build_generation_messages(self, request: ContentRequest) -> list[Message]:
        """Build Gemini messages with full brand DNA context.

        Args:
            request: Content request

        Returns:
            List of Messages with system (brand DNA) + user (request)
        """
        dna = self._brand_dna

        # System message: brand DNA as context
        system_content = (
            f"{self.SYSTEM_PROMPT}\n\n{'=' * 60}\n{dna.to_prompt_context()}\n{'=' * 60}"
        )

        # Collection-specific brand context
        if request.collection:
            collection_context = self.brand_context.get_product_context(
                product_name=request.title
                or f"{_safe_collection_value(request.collection).replace('-', ' ').title()} Content",
                product_type=request.content_type.value,
                collection=request.collection,
            )
            system_content += f"\n\nCOLLECTION-SPECIFIC CONTEXT:\n{collection_context}"

        # User message: specific content request
        user_content = (
            f"CONTENT REQUEST:\n"
            f"Type: {request.content_type.value}\n"
            f"Title Direction: {request.title or 'Determine the best title'}\n"
        )

        if request.collection:
            user_content += f"Collection: {_safe_collection_value(request.collection).replace('-', ' ').title()}\n"

        if request.target_url:
            user_content += f"Target URL: {request.target_url}\n"

        if request.seo_keywords:
            user_content += f"SEO Keywords: {', '.join(request.seo_keywords)}\n"

        if request.reference_imagery:
            user_content += (
                f"Reference Imagery Available: {len(request.reference_imagery)} images\n"
                f"(These will be featured alongside this content)\n"
            )

        if request.additional_direction:
            user_content += f"\nAdditional Direction: {request.additional_direction}\n"

        user_content += (
            "\n\nPLEASE GENERATE:\n"
            "1. A compelling H1 title\n"
            "2. Full HTML body content with proper heading hierarchy\n"
            "3. A short excerpt (2-3 sentences)\n"
            "4. SEO title (under 60 chars)\n"
            "5. SEO meta description (under 160 chars)\n"
            "6. Suggested SEO keywords (5-7 terms)\n\n"
            "Format your response as JSON with this structure:\n"
            '{"title": "...", "body_html": "...", "excerpt": "...", '
            '"seo_title": "...", "seo_description": "...", "seo_keywords": [...]}\n'
        )

        messages = [
            Message.system(system_content),
            Message.user(user_content),
        ]

        # Inject brand context into messages via injector
        messages = self.brand_context.inject(
            messages,
            collection=request.collection,
            prepend_system=False,  # Already included in system message
        )

        return messages

    def _parse_gemini_response(
        self,
        response: CompletionResponse,
        request: ContentRequest,
    ) -> GeneratedContent:
        """Parse Gemini's response into structured content.

        Args:
            response: Gemini completion response
            request: Original request

        Returns:
            Structured GeneratedContent
        """
        content_str = response.content.strip()

        # Extract JSON from response (may be wrapped in markdown code blocks)
        if "```json" in content_str:
            content_str = content_str.split("```json")[1].split("```")[0].strip()
        elif "```" in content_str:
            content_str = content_str.split("```")[1].split("```")[0].strip()

        try:
            parsed = json.loads(content_str)
        except json.JSONDecodeError:
            # Fallback: treat entire response as body HTML
            parsed = {
                "title": request.title or "SkyyRose Content",
                "body_html": content_str,
                "excerpt": content_str[:300],
                "seo_title": request.title or "SkyyRose",
                "seo_description": content_str[:160],
                "seo_keywords": request.seo_keywords,
            }

        # Build prompt hash for learning tracking
        prompt_hash = hashlib.sha256(
            json.dumps(
                {"type": request.content_type.value, "collection": str(request.collection)}
            ).encode()
        ).hexdigest()[:16]

        return GeneratedContent(
            content_type=request.content_type,
            collection=request.collection,
            title=parsed.get("title", request.title),
            body_html=parsed.get("body_html", ""),
            excerpt=parsed.get("excerpt", ""),
            seo_title=parsed.get("seo_title", ""),
            seo_description=parsed.get("seo_description", ""),
            seo_keywords=parsed.get("seo_keywords", request.seo_keywords),
            correlation_id=request.correlation_id,
            prompt_hash=prompt_hash,
            gemini_tokens_used=response.total_tokens,
            metadata={
                "gemini_model": response.model,
                "provider": response.provider,
                "latency_ms": response.latency_ms,
            },
        )

    # =========================================================================
    # WordPress Deployment (wordpress-ops integration)
    # =========================================================================

    async def publish_to_wordpress(
        self,
        content: GeneratedContent,
        wp_client: Any,
        status: str = "draft",
    ) -> GeneratedContent:
        """Publish generated content to WordPress.

        Follows wordpress-ops patterns:
        - Creates as draft first (always review before publish)
        - Tags with _skyyrose_collection metadata
        - Includes SEO fields

        Args:
            content: Generated content to publish
            wp_client: WordPressComClient
            status: WordPress post status (draft, publish)

        Returns:
            Updated content with wp_post_id
        """
        logger.info(f"{self.AGENT_NAME}: Publishing '{content.title}' to WordPress as {status}")

        try:
            # Build WordPress post payload with brand meta
            collection_value = _safe_collection_value(content.collection)

            wp_response = await wp_client.create_post(
                title=content.title,
                content=content.body_html,
                status=status,
                excerpt=content.excerpt,
                meta={
                    "_skyyrose_collection": collection_value,
                    "_skyyrose_content_agent": True,
                    "_skyyrose_seo_title": content.seo_title,
                    "_skyyrose_seo_description": content.seo_description,
                    "_skyyrose_content_id": content.content_id,
                },
            )

            content.wp_post_id = wp_response.get("id")
            content.status = (
                ContentStatus.PUBLISHED if status == "publish" else ContentStatus.DRAFTED
            )

            logger.info(f"{self.AGENT_NAME}: Published to WP post ID {content.wp_post_id}")

            return content

        except Exception as e:
            logger.error(f"{self.AGENT_NAME}: WordPress publish failed: {e}")
            raise

    # =========================================================================
    # Continuous Learning System
    # =========================================================================

    def _record_generation(
        self,
        content: GeneratedContent,
        request: ContentRequest,
        response: CompletionResponse,
    ) -> None:
        """Record a generation event for continuous learning.

        Args:
            content: Generated content
            request: Original request
            response: Gemini response with token usage
        """
        record = LearningRecord(
            task_id=content.content_id,
            task_type=request.content_type.value,
            prompt_hash=content.prompt_hash,
            technique_used="gemini_direct",
            llm_provider="google",
            success=True,
            latency_ms=response.latency_ms,
            cost_usd=response.cost_usd or 0.0,
        )

        self._learning_records.append(record)
        self._content_log.append(content)

        logger.debug(f"{self.AGENT_NAME}: Recorded generation for learning")

    def record_feedback(
        self,
        content_id: str,
        score: float,
        notes: str = "",
    ) -> None:
        """Record feedback on generated content for learning.

        Higher scores (1.0) = content performed well, repeat patterns.
        Lower scores (0.0) = content missed the mark, adjust approach.

        Args:
            content_id: Content ID to score
            score: Performance score (0.0 - 1.0)
            notes: Optional feedback notes
        """
        # Update content record
        for content in self._content_log:
            if content.content_id == content_id:
                content.feedback_score = score
                break

        # Update learning records
        for record in self._learning_records:
            if record.task_id == content_id:
                record.user_feedback = score
                break

        # Update brand DNA with high performers
        if self._brand_dna and score >= 0.8:
            # Find the content
            for content in self._content_log:
                if content.content_id == content_id:
                    if (
                        content.title
                        and content.title not in self._brand_dna.top_performing_headlines
                    ):
                        self._brand_dna.top_performing_headlines.append(content.title)
                        # Keep top 20
                        self._brand_dna.top_performing_headlines = (
                            self._brand_dna.top_performing_headlines[:20]
                        )
                    if content.content_type.value not in self._brand_dna.top_performing_themes:
                        self._brand_dna.top_performing_themes.append(content.content_type.value)
                    break

        # Persist learning state
        self._save_learning_state()

        logger.info(f"{self.AGENT_NAME}: Feedback recorded for {content_id} (score={score})")

    def _save_learning_state(self) -> None:
        """Persist learning state to disk for cross-session continuity."""
        if not self._brand_dna:
            return

        state = {
            "top_performing_headlines": self._brand_dna.top_performing_headlines,
            "top_performing_themes": self._brand_dna.top_performing_themes,
            "content_feedback_scores": {
                c.content_id: c.feedback_score
                for c in self._content_log
                if c.feedback_score is not None
            },
            "generation_count": len(self._content_log),
            "last_updated": datetime.now(UTC).isoformat(),
            "learning_records": [
                {
                    "task_id": r.task_id,
                    "task_type": r.task_type,
                    "success": r.success,
                    "feedback": r.user_feedback,
                    "latency_ms": r.latency_ms,
                }
                for r in self._learning_records[-100:]  # Keep last 100
            ],
        }

        try:
            with open(self._learning_state_path, "w") as f:
                json.dump(state, f, indent=2)
            logger.debug(f"{self.AGENT_NAME}: Learning state saved")
        except Exception as e:
            logger.warning(f"{self.AGENT_NAME}: Could not save learning state: {e}")

    def _load_learning_state(self, dna: BrandDNA) -> None:
        """Load persisted learning state into brand DNA.

        Args:
            dna: BrandDNA instance to populate
        """
        try:
            if not os.path.exists(self._learning_state_path):
                return

            with open(self._learning_state_path) as f:
                state = json.load(f)

            dna.top_performing_headlines = state.get("top_performing_headlines", [])
            dna.top_performing_themes = state.get("top_performing_themes", [])
            dna.content_feedback_scores = state.get("content_feedback_scores", {})

            logger.info(
                f"{self.AGENT_NAME}: Loaded learning state — "
                f"{len(dna.top_performing_headlines)} top headlines, "
                f"{len(dna.top_performing_themes)} top themes"
            )
        except Exception as e:
            logger.warning(f"{self.AGENT_NAME}: Could not load learning state: {e}")

    # =========================================================================
    # Convenience Methods
    # =========================================================================

    async def create_collection_page(
        self,
        collection: Collection,
        wp_client: Any | None = None,
        publish: bool = False,
    ) -> GeneratedContent:
        """Generate a full collection landing page.

        Args:
            collection: Which collection to create a page for
            wp_client: Optional WP client
            publish: Whether to publish immediately (default: draft)

        Returns:
            Generated collection page content
        """
        request = ContentRequest(
            content_type=ContentType.COLLECTION_PAGE,
            collection=collection,
            title=f"{_safe_collection_value(collection).replace('-', ' ').title()} Collection",
            target_url=f"/collection/{_safe_collection_value(collection)}/",
            seo_keywords=[
                f"skyyrose {_safe_collection_value(collection).replace('-', ' ')}",
                f"luxury {_safe_collection_value(collection).replace('-', ' ')} jewelry",
                "skyyrose collection",
                "luxury fashion oakland",
            ],
        )

        content = await self.generate_content(request, wp_client=wp_client)

        if publish and wp_client:
            content = await self.publish_to_wordpress(content, wp_client, status="draft")

        return content

    async def create_product_description(
        self,
        product_name: str,
        collection: Collection,
        price: str,
        details: str = "",
        wp_client: Any | None = None,
    ) -> GeneratedContent:
        """Generate a product description.

        Args:
            product_name: Name of the product
            collection: Product's collection
            price: Product price
            details: Additional product details
            wp_client: Optional WP client

        Returns:
            Generated product description
        """
        request = ContentRequest(
            content_type=ContentType.PRODUCT_DESCRIPTION,
            collection=collection,
            title=product_name,
            seo_keywords=[
                product_name.lower(),
                f"skyyrose {product_name.lower()}",
                f"{_safe_collection_value(collection).replace('-', ' ')} {product_name.split()[-1].lower()}",
            ],
            additional_direction=(
                f"Price: ${price}\n"
                f"This is a limited edition piece.\n"
                f"{'Additional details: ' + details if details else ''}\n"
                f"Include sensory language — make the reader feel the luxury."
            ),
        )

        return await self.generate_content(request, wp_client=wp_client)

    def get_content_log(self) -> list[GeneratedContent]:
        """Get all generated content for this session."""
        return list(self._content_log)

    def get_learning_summary(self) -> dict[str, Any]:
        """Get a summary of the learning state."""
        return {
            "total_generations": len(self._content_log),
            "total_feedback_records": len(
                [r for r in self._learning_records if r.user_feedback is not None]
            ),
            "top_headlines": (
                self._brand_dna.top_performing_headlines[:5] if self._brand_dna else []
            ),
            "top_themes": self._brand_dna.top_performing_themes if self._brand_dna else [],
            "avg_feedback_score": (
                sum(r.user_feedback for r in self._learning_records if r.user_feedback)
                / max(1, len([r for r in self._learning_records if r.user_feedback]))
            ),
        }
