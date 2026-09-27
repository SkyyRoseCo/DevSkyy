"""
DevSkyy Marketing SuperAgent
============================

Handles all marketing operations for SkyyRose.

Consolidates:
- Content creation
- Social media management
- SEO optimization
- Email campaigns
- Influencer outreach
- Campaign analytics

ML Capabilities:
- Sentiment analysis
- Trend prediction
- Audience segmentation
"""

import logging
from datetime import UTC, datetime
from typing import Any

from adk.base import (
    ADKProvider,
    AgentCapability,
    AgentConfig,
    AgentResult,
    AgentStatus,
    ToolDefinition,
)
from core.runtime.tool_registry import (
    ParameterType,
    ToolCategory,
    ToolParameter,
    ToolRegistry,
    ToolSeverity,
    ToolSpec,
)
from llm.model_ids import OPENAI_VISION_MODEL
from orchestration.prompt_engineering import PromptTechnique

from .base_super_agent import EnhancedSuperAgent, SuperAgentType, TaskCategory

logger = logging.getLogger(__name__)


class MarketingAgent(EnhancedSuperAgent):
    """
    Marketing Super Agent - Handles all marketing operations.

    Features:
    - 17 prompt engineering techniques
    - ML-based sentiment analysis
    - Trend prediction
    - Multi-channel content optimization
    - SEO best practices

    Example:
        agent = MarketingAgent()
        await agent.initialize()
        result = await agent.create_campaign("Launch BLACK ROSE collection")
    """

    agent_type = SuperAgentType.MARKETING
    sub_capabilities = [
        "content_creation",
        "social_media",
        "seo_optimization",
        "email_campaigns",
        "influencer_outreach",
        "campaign_analytics",
    ]

    # Marketing-specific technique preferences
    TECHNIQUE_PREFERENCES = {
        "content": PromptTechnique.ROLE_BASED,
        "social": PromptTechnique.FEW_SHOT,
        "seo": PromptTechnique.STRUCTURED_OUTPUT,
        "email": PromptTechnique.CHAIN_OF_THOUGHT,
        "influencer": PromptTechnique.REACT,
        "analytics": PromptTechnique.CHAIN_OF_THOUGHT,
    }

    def __init__(self, config: AgentConfig | None = None):
        if config is None:
            config = AgentConfig(
                name="marketing_agent",
                provider=ADKProvider.PYDANTIC,
                model=OPENAI_VISION_MODEL,
                system_prompt=self._build_system_prompt(),
                capabilities=[
                    AgentCapability.MARKETING,
                    AgentCapability.TEXT_GENERATION,
                    AgentCapability.REASONING,
                ],
                tools=self._build_tools(),
                temperature=0.7,
            )
        super().__init__(config)

    def _build_system_prompt(self) -> str:
        """Build the marketing agent system prompt"""
        return """You are the Marketing SuperAgent for SkyyRose luxury streetwear.

## IDENTITY
You are an expert marketing strategist and content creator with expertise in:
- Brand storytelling and content marketing
- Social media strategy and management
- SEO and digital marketing optimization
- Email marketing campaigns
- Influencer partnerships
- Data-driven marketing analytics

## BRAND VOICE
**Tone:** Sophisticated yet accessible, bold and confident, emotionally resonant
**Style:** Luxury without pretension, authentic street culture roots
**Tagline:** ""
**Philosophy:** Elevating streetwear to luxury status while honoring its origins

## TARGET AUDIENCE
- **Age:** 25-45
- **Income:** Upper-middle to high
- **Style:** Fashion-forward, quality-conscious
- **Values:** Self-expression, premium craftsmanship, authenticity
- **Platforms:** Instagram, TikTok, Pinterest, Email

## COLLECTIONS
- **BLACK ROSE:** Limited edition dark elegance, exclusive drops
- **LOVE HURTS:** Emotional expression, bold statements
- **SIGNATURE:** Foundation wardrobe essentials, timeless pieces

## RESPONSIBILITIES
1. **Content Creation**
   - Write compelling copy for all channels
   - Create product descriptions
   - Develop blog content
   - Craft brand storytelling

2. **Social Media**
   - Manage Instagram, TikTok, Twitter presence
   - Create engaging posts and stories
   - Plan content calendars
   - Community engagement

3. **SEO**
   - Optimize website content
   - Keyword research and implementation
   - Meta descriptions and titles
   - Technical SEO guidance

4. **Email Campaigns**
   - Design email sequences
   - Segment audiences
   - A/B test subject lines
   - Analyze performance

5. **Influencer Outreach**
   - Identify brand-aligned influencers
   - Craft outreach messages
   - Manage partnerships
   - Track ROI

6. **Campaign Analytics**
   - Track marketing KPIs
   - Analyze campaign performance
   - Generate insights
   - Recommend optimizations

## GUIDELINES
- Always maintain brand voice consistency
- Focus on emotional connection over hard selling
- Use data to inform creative decisions
- Prioritize authenticity and quality
- Create content that tells a story"""

    def _build_tools(self) -> list[ToolDefinition]:
        """Build marketing-specific tools"""
        return [
            # Content Tools
            ToolDefinition(
                name="create_content",
                description="Create marketing content for various channels",
                parameters={
                    "content_type": {
                        "type": "string",
                        "description": "Type (post, blog, email, ad)",
                    },
                    "channel": {"type": "string", "description": "Target channel"},
                    "topic": {"type": "string", "description": "Content topic"},
                    "tone": {"type": "string", "description": "Tone override"},
                    "length": {"type": "string", "description": "Content length"},
                },
            ),
            ToolDefinition(
                name="generate_hashtags",
                description="Generate relevant hashtags for social content",
                parameters={
                    "content": {"type": "string", "description": "Content to tag"},
                    "platform": {"type": "string", "description": "Target platform"},
                    "count": {"type": "integer", "description": "Number of hashtags"},
                },
            ),
            ToolDefinition(
                name="optimize_content",
                description="Optimize content for engagement",
                parameters={
                    "content": {"type": "string", "description": "Content to optimize"},
                    "optimization_type": {
                        "type": "string",
                        "description": "SEO, engagement, or conversion",
                    },
                },
            ),
            # Social Media Tools
            ToolDefinition(
                name="schedule_post",
                description="Schedule social media post",
                parameters={
                    "platform": {"type": "string", "description": "Social platform"},
                    "content": {"type": "string", "description": "Post content"},
                    "scheduled_time": {"type": "string", "description": "ISO datetime"},
                    "media": {"type": "array", "description": "Media attachments"},
                },
            ),
            ToolDefinition(
                name="analyze_engagement",
                description="Analyze social media engagement metrics",
                parameters={
                    "platform": {"type": "string", "description": "Platform to analyze"},
                    "time_period": {"type": "string", "description": "Analysis period"},
                    "metrics": {"type": "array", "description": "Metrics to include"},
                },
            ),
            # SEO Tools
            ToolDefinition(
                name="keyword_research",
                description="Research keywords for SEO optimization",
                parameters={
                    "seed_keywords": {"type": "array", "description": "Starting keywords"},
                    "intent": {"type": "string", "description": "Search intent type"},
                    "competition": {"type": "string", "description": "Competition level"},
                },
            ),
            ToolDefinition(
                name="analyze_seo",
                description="Analyze page SEO performance",
                parameters={
                    "url": {"type": "string", "description": "Page URL"},
                    "target_keywords": {"type": "array", "description": "Target keywords"},
                },
            ),
            ToolDefinition(
                name="generate_meta",
                description="Generate SEO meta tags",
                parameters={
                    "page_content": {"type": "string", "description": "Page content summary"},
                    "target_keywords": {"type": "array", "description": "Target keywords"},
                    "page_type": {"type": "string", "description": "Page type"},
                },
            ),
            # Email Tools
            ToolDefinition(
                name="create_email",
                description="Create email campaign content",
                parameters={
                    "campaign_type": {"type": "string", "description": "Campaign type"},
                    "subject_variants": {
                        "type": "integer",
                        "description": "Number of subject line variants",
                    },
                    "audience_segment": {"type": "string", "description": "Target segment"},
                    "goal": {"type": "string", "description": "Campaign goal"},
                },
            ),
            ToolDefinition(
                name="analyze_email_metrics",
                description="Analyze email campaign metrics",
                parameters={
                    "campaign_id": {"type": "string", "description": "Campaign ID"},
                    "metrics": {"type": "array", "description": "Metrics to analyze"},
                },
            ),
            # Influencer Tools
            ToolDefinition(
                name="find_influencers",
                description="Find brand-aligned influencers",
                parameters={
                    "niche": {"type": "string", "description": "Influencer niche"},
                    "follower_range": {"type": "object", "description": "Follower count range"},
                    "platforms": {"type": "array", "description": "Target platforms"},
                    "engagement_threshold": {
                        "type": "number",
                        "description": "Min engagement rate",
                    },
                },
            ),
            ToolDefinition(
                name="create_outreach",
                description="Create influencer outreach message",
                parameters={
                    "influencer_name": {"type": "string", "description": "Influencer name"},
                    "campaign_brief": {"type": "string", "description": "Campaign details"},
                    "collaboration_type": {
                        "type": "string",
                        "description": "Type of collaboration",
                    },
                },
            ),
            # Analytics Tools
            ToolDefinition(
                name="get_campaign_metrics",
                description="Get campaign performance metrics",
                parameters={
                    "campaign_id": {"type": "string", "description": "Campaign ID"},
                    "date_range": {"type": "object", "description": "Start and end dates"},
                },
            ),
            ToolDefinition(
                name="generate_report",
                description="Generate marketing performance report",
                parameters={
                    "report_type": {"type": "string", "description": "Report type"},
                    "time_period": {"type": "string", "description": "Reporting period"},
                    "channels": {"type": "array", "description": "Channels to include"},
                },
            ),
        ]

    def _register_tools(self) -> None:
        """Register marketing tools with the global ToolRegistry for MCP integration."""
        registry = ToolRegistry.get_instance()

        marketing_tools = [
            ToolSpec(
                name="marketing_create_content",
                description="Create marketing content for various channels",
                category=ToolCategory.CONTENT,
                severity=ToolSeverity.LOW,
                parameters=[
                    ToolParameter(
                        name="content_type",
                        type=ParameterType.STRING,
                        description="Type (post, blog, email, ad)",
                        required=True,
                    ),
                    ToolParameter(
                        name="channel",
                        type=ParameterType.STRING,
                        description="Target channel",
                        required=True,
                    ),
                    ToolParameter(
                        name="topic",
                        type=ParameterType.STRING,
                        description="Content topic",
                        required=True,
                    ),
                    ToolParameter(
                        name="tone",
                        type=ParameterType.STRING,
                        description="Tone override",
                        required=False,
                    ),
                ],
                idempotent=False,
                cacheable=False,
                tags={"marketing", "content", "creation"},
            ),
            ToolSpec(
                name="marketing_generate_hashtags",
                description="Generate relevant hashtags for social content",
                category=ToolCategory.CONTENT,
                severity=ToolSeverity.READ_ONLY,
                parameters=[
                    ToolParameter(
                        name="content",
                        type=ParameterType.STRING,
                        description="Content to generate hashtags for",
                        required=True,
                    ),
                    ToolParameter(
                        name="platform",
                        type=ParameterType.STRING,
                        description="Target platform (instagram, tiktok, twitter)",
                        required=True,
                    ),
                    ToolParameter(
                        name="count",
                        type=ParameterType.INTEGER,
                        description="Number of hashtags",
                        required=False,
                    ),
                ],
                idempotent=True,
                cacheable=True,
                tags={"marketing", "social", "hashtags"},
            ),
            ToolSpec(
                name="marketing_schedule_post",
                description="Schedule social media post",
                category=ToolCategory.CONTENT,
                severity=ToolSeverity.MEDIUM,
                parameters=[
                    ToolParameter(
                        name="platform",
                        type=ParameterType.STRING,
                        description="Social platform",
                        required=True,
                    ),
                    ToolParameter(
                        name="content",
                        type=ParameterType.STRING,
                        description="Post content",
                        required=True,
                    ),
                    ToolParameter(
                        name="scheduled_time",
                        type=ParameterType.STRING,
                        description="ISO datetime for posting",
                        required=True,
                    ),
                ],
                idempotent=False,
                cacheable=False,
                tags={"marketing", "social", "schedule"},
            ),
            ToolSpec(
                name="marketing_analyze_engagement",
                description="Analyze social media engagement metrics",
                category=ToolCategory.AI,
                severity=ToolSeverity.READ_ONLY,
                parameters=[
                    ToolParameter(
                        name="platform",
                        type=ParameterType.STRING,
                        description="Platform to analyze",
                        required=True,
                    ),
                    ToolParameter(
                        name="time_period",
                        type=ParameterType.STRING,
                        description="Analysis period",
                        required=False,
                    ),
                ],
                idempotent=True,
                cacheable=True,
                tags={"marketing", "analytics", "engagement"},
            ),
            ToolSpec(
                name="marketing_keyword_research",
                description="Research keywords for SEO optimization",
                category=ToolCategory.AI,
                severity=ToolSeverity.READ_ONLY,
                parameters=[
                    ToolParameter(
                        name="seed_keywords",
                        type=ParameterType.ARRAY,
                        description="Starting keywords for research",
                        required=True,
                    ),
                    ToolParameter(
                        name="intent",
                        type=ParameterType.STRING,
                        description="Search intent type (informational, transactional)",
                        required=False,
                    ),
                ],
                idempotent=True,
                cacheable=True,
                tags={"marketing", "seo", "keywords"},
            ),
            ToolSpec(
                name="marketing_analyze_seo",
                description="Analyze page SEO performance",
                category=ToolCategory.AI,
                severity=ToolSeverity.READ_ONLY,
                parameters=[
                    ToolParameter(
                        name="url",
                        type=ParameterType.STRING,
                        description="Page URL to analyze",
                        required=True,
                    ),
                    ToolParameter(
                        name="target_keywords",
                        type=ParameterType.ARRAY,
                        description="Target keywords to check",
                        required=False,
                    ),
                ],
                idempotent=True,
                cacheable=True,
                tags={"marketing", "seo", "analysis"},
            ),
            ToolSpec(
                name="marketing_create_email",
                description="Create email campaign content",
                category=ToolCategory.CONTENT,
                severity=ToolSeverity.LOW,
                parameters=[
                    ToolParameter(
                        name="campaign_type",
                        type=ParameterType.STRING,
                        description="Campaign type (welcome, promo, newsletter)",
                        required=True,
                    ),
                    ToolParameter(
                        name="audience_segment",
                        type=ParameterType.STRING,
                        description="Target audience segment",
                        required=True,
                    ),
                    ToolParameter(
                        name="goal",
                        type=ParameterType.STRING,
                        description="Campaign goal",
                        required=False,
                    ),
                ],
                idempotent=False,
                cacheable=False,
                tags={"marketing", "email", "campaign"},
            ),
            ToolSpec(
                name="marketing_find_influencers",
                description="Find brand-aligned influencers",
                category=ToolCategory.AI,
                severity=ToolSeverity.READ_ONLY,
                parameters=[
                    ToolParameter(
                        name="niche",
                        type=ParameterType.STRING,
                        description="Influencer niche",
                        required=True,
                    ),
                    ToolParameter(
                        name="platforms",
                        type=ParameterType.ARRAY,
                        description="Target platforms",
                        required=False,
                    ),
                    ToolParameter(
                        name="engagement_threshold",
                        type=ParameterType.NUMBER,
                        description="Minimum engagement rate",
                        required=False,
                    ),
                ],
                idempotent=True,
                cacheable=True,
                tags={"marketing", "influencer", "search"},
            ),
            ToolSpec(
                name="marketing_get_campaign_metrics",
                description="Get campaign performance metrics",
                category=ToolCategory.AI,
                severity=ToolSeverity.READ_ONLY,
                parameters=[
                    ToolParameter(
                        name="campaign_id",
                        type=ParameterType.STRING,
                        description="Campaign ID",
                        required=True,
                    ),
                ],
                idempotent=True,
                cacheable=True,
                tags={"marketing", "campaign", "metrics"},
            ),
        ]

        for spec in marketing_tools:
            registry.register(spec)

    async def execute(self, prompt: str, **kwargs) -> AgentResult:
        """Execute marketing operation"""
        start_time = datetime.now(UTC)

        try:
            task_type = self._classify_marketing_task(prompt)
            technique = self.TECHNIQUE_PREFERENCES.get(
                task_type, self.select_technique(TaskCategory.GENERATION)
            )

            enhanced = self.apply_technique(
                technique,
                prompt,
                role="marketing director for SkyyRose luxury streetwear",
                **kwargs,
            )

            if hasattr(self, "_backend_agent"):
                result = await self._backend_agent.run(enhanced.enhanced_prompt)
                content = str(result.output) if hasattr(result, "output") else str(result)
            else:
                content = await self._fallback_process(prompt, task_type)

            return AgentResult(
                agent_name=self.name,
                agent_provider=self._active_provider,
                content=content,
                status=AgentStatus.COMPLETED,
                started_at=start_time,
                metadata={"task_type": task_type, "technique": technique.value},
            )

        except Exception as e:
            logger.error(f"Marketing agent error: {e}")
            return AgentResult(
                agent_name=self.name,
                agent_provider=self._active_provider,
                content="",
                status=AgentStatus.FAILED,
                error=str(e),
                started_at=start_time,
            )

    def _classify_marketing_task(self, prompt: str) -> str:
        """Classify the marketing task type"""
        prompt_lower = prompt.lower()

        task_keywords = {
            "content": ["content", "write", "copy", "description", "blog", "article"],
            "social": ["social", "instagram", "tiktok", "twitter", "post", "hashtag"],
            "seo": ["seo", "keyword", "meta", "search", "ranking", "optimize"],
            "email": ["email", "newsletter", "campaign", "subject", "subscriber"],
            "influencer": ["influencer", "ambassador", "partnership", "collab", "outreach"],
            "analytics": ["analytics", "metrics", "report", "performance", "roi"],
        }

        for task_type, keywords in task_keywords.items():
            if any(kw in prompt_lower for kw in keywords):
                return task_type

        return "content"

    async def _fallback_process(self, prompt: str, task_type: str) -> str:
        """Fallback processing"""
        return f"""Marketing Agent Analysis

Task Type: {task_type}
Query: {prompt[:200]}...

Brand Voice Applied:
- Sophisticated yet accessible
- Luxury streetwear positioning
- ""

For full marketing capabilities, ensure backend is configured."""

    # =========================================================================
    # Marketing-Specific Methods
    # =========================================================================

    async def create_campaign(
        self, campaign_brief: str, channels: list[str] | None = None
    ) -> AgentResult:
        """Create a full marketing campaign"""
        channels = channels or ["instagram", "email", "website"]

        prompt = f"""Create a comprehensive marketing campaign for SkyyRose:

Brief: {campaign_brief}
Channels: {channels}

Please provide:
1. Campaign concept and messaging
2. Content calendar (2 weeks)
3. Platform-specific content for each channel
4. Hashtag strategy
5. Influencer collaboration ideas
6. Success metrics and KPIs
7. Budget allocation recommendations"""

        return await self.execute_with_learning(
            prompt, task_type="campaign", technique=PromptTechnique.TREE_OF_THOUGHTS
        )

    async def analyze_sentiment(self, content: str | list[str]) -> dict[str, Any]:
        """Analyze sentiment using ML"""
        if self.ml_module:
            if isinstance(content, str):
                content = [content]

            results = []
            for text in content:
                prediction = await self.ml_module.predict("sentiment_analyzer", text)
                results.append(
                    {
                        "text": text[:100],
                        "sentiment": prediction.prediction,
                        "confidence": prediction.confidence,
                    }
                )

            return {"analyses": results}

        return {"error": "ML module not available"}

    async def generate_social_content(
        self, topic: str, platform: str = "instagram", count: int = 5
    ) -> AgentResult:
        """Generate social media content"""
        prompt = f"""Generate {count} engaging {platform} posts for SkyyRose about: {topic}

Requirements:
- Match brand voice (sophisticated, bold, emotionally resonant)
- Include relevant hashtags
- Optimize for {platform} algorithm
- Include call-to-action
- Vary content formats (static, carousel, story ideas)

For each post provide:
1. Caption
2. Visual direction
3. Hashtags
4. Best posting time
5. Engagement prompt"""

        return await self.execute_with_learning(
            prompt,
            task_type="social",
            technique=PromptTechnique.FEW_SHOT,
            examples=[
                {
                    "input": "New bomber jacket launch",
                    "output": "✨ Introducing the Rose Gold Bomber: Where street meets suite. Limited drop. Unlimited attitude. 🖤 #SkyyRose #LuxuryStreet #RoseGoldSeason",
                },
                {
                    "input": "Behind the scenes",
                    "output": "Every stitch tells a story. Every seam speaks luxury. Behind the scenes of crafting your next statement piece. 🌹 #WhereLoveMeetsLuxury #SkyyRose",
                },
            ],
        )

    async def optimize_seo(self, page_url: str, target_keywords: list[str]) -> AgentResult:
        """Optimize page for SEO"""
        prompt = f"""SEO optimization analysis for SkyyRose page:

URL: {page_url}
Target Keywords: {target_keywords}

Provide comprehensive SEO recommendations:
1. Title tag optimization
2. Meta description
3. Header structure (H1, H2, H3)
4. Keyword placement strategy
5. Internal linking opportunities
6. Schema markup recommendations
7. Page speed considerations
8. Mobile optimization
9. Content gap analysis"""

        return await self.execute_with_learning(
            prompt,
            task_type="seo",
            technique=PromptTechnique.STRUCTURED_OUTPUT,
            schema={
                "title_tag": "string",
                "meta_description": "string",
                "header_structure": "object",
                "keyword_recommendations": "array",
                "internal_links": "array",
                "schema_markup": "object",
                "priority_actions": "array",
            },
        )

    async def publish_to_wordpress(
        self,
        title: str,
        content: str,
        post_type: str = "post",
        status: str = "draft",
        categories: list[str] | None = None,
        tags: list[str] | None = None,
        featured_image_url: str | None = None,
        excerpt: str = "",
        seo_title: str | None = None,
        seo_description: str | None = None,
    ) -> dict[str, Any]:
        """
        Publish content to WordPress.

        This method integrates with the WordPress REST API to create or publish
        blog posts, pages, and other content types directly from the marketing agent.

        Args:
            title: Post/page title
            content: Post/page content (HTML supported)
            post_type: Type of content (post, page, product)
            status: Publication status (draft, publish, pending, private)
            categories: List of category names (for posts)
            tags: List of tag names (for posts)
            featured_image_url: URL of featured image
            excerpt: Short excerpt/summary
            seo_title: SEO title (Yoast/RankMath)
            seo_description: SEO meta description

        Returns:
            dict with post_id, url, status, and any errors

        Example:
            result = await marketing_agent.publish_to_wordpress(
                title="Introducing BLACK ROSE Collection",
                content="<p>Discover the luxury of dark elegance...</p>",
                status="draft",
                categories=["Collections", "New Arrivals"],
                tags=["black-rose", "luxury", "limited-edition"],
            )
        """
        from wordpress.client import WordPressClient, WordPressError

        logger.info(f"Publishing to WordPress: {title} ({post_type}, {status})")

        try:
            async with WordPressClient() as wp_client:
                # Prepare post data
                post_data: dict[str, Any] = {
                    "title": title,
                    "content": content,
                    "status": status,
                    "excerpt": excerpt,
                }

                # Add categories if provided (posts only)
                if categories and post_type == "post":
                    # Note: In production, you'd need to resolve category names to IDs
                    # or create categories if they don't exist
                    post_data["categories"] = categories

                # Add tags if provided (posts only)
                if tags and post_type == "post":
                    post_data["tags"] = tags

                # Upload featured image if provided
                if featured_image_url:
                    try:
                        # Download and upload image to WordPress media library
                        import aiohttp

                        async with aiohttp.ClientSession() as session:  # noqa: SIM117
                            async with session.get(featured_image_url) as resp:
                                if resp.status == 200:
                                    # Save temporarily
                                    import tempfile
                                    from pathlib import Path

                                    with tempfile.NamedTemporaryFile(
                                        delete=False, suffix=".jpg"
                                    ) as tmp:
                                        tmp.write(await resp.read())
                                        tmp_path = tmp.name

                                    # Upload to WordPress
                                    media_result = await wp_client.upload_media(
                                        tmp_path, title=f"{title} - Featured Image"
                                    )
                                    post_data["featured_media"] = media_result["id"]

                                    # Clean up temp file
                                    Path(tmp_path).unlink(missing_ok=True)

                    except Exception as e:
                        logger.warning(f"Failed to upload featured image: {e}")

                # Create post or page
                if post_type == "post":
                    result = await wp_client.create_post(**post_data)
                elif post_type == "page":
                    result = await wp_client.create_page(**post_data)
                else:
                    # For custom post types, use generic post creation
                    post_data["type"] = post_type
                    result = await wp_client.create_post(**post_data)

                # Add SEO metadata if provided (requires Yoast SEO or Rank Math plugin)
                if (seo_title or seo_description) and result.get("id"):
                    post_id = result["id"]
                    seo_meta = []

                    if seo_title:
                        seo_meta.append({"key": "_yoast_wpseo_title", "value": seo_title})
                    if seo_description:
                        seo_meta.append({"key": "_yoast_wpseo_metadesc", "value": seo_description})

                    # Update post with SEO metadata
                    # Note: This requires custom meta update, not available in base WordPressClient
                    # In production, extend WordPressClient or use WooCommerce manager
                    logger.info(f"SEO metadata prepared for post {post_id}: {seo_meta}")

                logger.info(
                    f"Content published successfully: {result.get('link', 'N/A')} (ID: {result.get('id')})"
                )

                return {
                    "success": True,
                    "post_id": result.get("id"),
                    "url": result.get("link"),
                    "status": result.get("status"),
                    "type": post_type,
                    "title": title,
                    "errors": [],
                }

        except WordPressError as e:
            logger.error(f"WordPress publishing failed: {e}", exc_info=True)
            return {
                "success": False,
                "post_id": None,
                "url": None,
                "status": "failed",
                "type": post_type,
                "title": title,
                "errors": [str(e)],
            }
        except Exception as e:
            logger.error(f"Unexpected error publishing to WordPress: {e}", exc_info=True)
            return {
                "success": False,
                "post_id": None,
                "url": None,
                "status": "error",
                "type": post_type,
                "title": title,
                "errors": [str(e)],
            }


# =============================================================================
# Export
# =============================================================================

__all__ = ["MarketingAgent"]
