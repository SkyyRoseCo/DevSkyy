"""
Social Media Sub-Agent (Enhanced)
==================================

Wraps agents/social_media_agent.py into the core hierarchy with:
- Brand Learning Loop integration (emits signals on content generation)
- Engagement feedback tracking (feeds performance back to learning loop)
- A/B content variant generation for brand voice optimization
- Platform-specific brand voice tuning based on learned insights

Parent: Marketing Core Agent
"""

from __future__ import annotations

import logging
from typing import Any

from agents.core.base import CoreAgentType
from agents.core.sub_agent import SubAgent

logger = logging.getLogger(__name__)


class SocialMediaSubAgent(SubAgent):
    """
    Social media management with autonomous brand learning.

    Extends the base social media agent with:
    1. Brand signal emission — every generated post is a learning signal
    2. Engagement feedback — published post metrics flow back to the loop
    3. Content variants — A/B test brand voice approaches
    4. Adaptive voice — uses learned insights to tune platform prompts
    """

    name = "social_media"
    parent_type = CoreAgentType.MARKETING
    description = "Post scheduling, engagement tracking, brand-learning content generation"
    capabilities = [
        "generate_post",
        "generate_campaign",
        "track_engagement",
        "analyze_performance",
        "generate_variants",
        "schedule_post",
        "publish_post",
    ]

    # Aliases for backward compatibility with routing
    ALIASES = ["social", "social_media_agent"]

    system_prompt = (
        "You are the Social Media specialist for SkyyRose luxury fashion. "
        "No brand slogan is authorized. "
        "Platforms: Instagram (primary), TikTok, Pinterest, X/Twitter. "
        "Brand voice: aspirational yet authentic, street luxury meets haute couture. "
        "Colors: rose gold #B76E79, dark #0A0A0A, gold #D4AF37, crimson #DC143C. "
        "3 Collections: Black Rose (gothic/Oakland), Love Hurts (passionate/B&B), "
        "Signature (Bay Area/SF golden hour). "
        "Create captions, schedule content, analyze engagement, generate hashtag strategies. "
        "Always include visual direction notes. Never use retired tagline 'Where Love Meets Luxury'."
    )

    def __init__(
        self,
        *,
        parent: Any | None = None,
        correlation_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent=parent, correlation_id=correlation_id, **kwargs)
        self._agent: Any = None
        self._learning_loop: Any = None

    # -------------------------------------------------------------------------
    # Lazy initialization
    # -------------------------------------------------------------------------

    def _get_agent(self) -> Any:
        """Lazy-load the standalone SocialMediaAgent."""
        if self._agent is None:
            from agents.social_media_agent import SocialMediaAgent

            self._agent = SocialMediaAgent(correlation_id=self.correlation_id)
        return self._agent

    def _get_learning_loop(self) -> Any:
        """Lazy-load the brand learning loop (if available)."""
        if self._learning_loop is None:
            try:
                from orchestration.brand_learning import create_brand_learning_loop

                self._learning_loop = create_brand_learning_loop(auto_connect=True)
            except ImportError:
                logger.debug("[%s] Brand learning loop unavailable", self.name)
        return self._learning_loop

    # -------------------------------------------------------------------------
    # Core execution
    # -------------------------------------------------------------------------

    async def execute(self, task: str, **kwargs: Any) -> dict[str, Any]:
        """
        Route social media tasks to the appropriate handler.

        Supports natural language tasks like:
        - "Generate an Instagram post for br-001"
        - "Create a campaign for the Black Rose collection"
        - "Record engagement: post X got 500 likes"
        - "Generate 3 caption variants for sg-002"
        """
        task_lower = task.lower()

        # Route to specific handlers
        if "variant" in task_lower or "a/b" in task_lower:
            return await self._generate_variants(task, **kwargs)

        if "campaign" in task_lower:
            return self._generate_campaign(task, **kwargs)

        if "engagement" in task_lower or "metric" in task_lower:
            return self._record_engagement(task, **kwargs)

        if "analytics" in task_lower or "performance" in task_lower:
            return self._get_performance(**kwargs)

        if "schedule" in task_lower:
            return self._schedule_post(task, **kwargs)

        if "publish" in task_lower:
            return self._publish_post(task, **kwargs)

        # Default: generate a post
        return self._generate_post(task, **kwargs)

    # -------------------------------------------------------------------------
    # Post Generation (with brand learning signal emission)
    # -------------------------------------------------------------------------

    def _generate_post(self, task: str, **kwargs: Any) -> dict[str, Any]:
        """Generate a post and emit a brand signal."""
        agent = self._get_agent()

        product_sku = kwargs.get("product_sku", "")
        platform = kwargs.get("platform", "instagram")
        content_type = kwargs.get("content_type", "product_launch")

        if not product_sku:
            # Try to extract SKU from task
            product_sku = self._extract_sku(task)

        if not product_sku:
            return {
                "success": False,
                "error": "No product_sku provided or found in task",
                "agent": self.name,
            }

        post = agent.generate_post(
            product_sku,
            platform,
            content_type,
            correlation_id=self.correlation_id,
        )

        if post is None:
            return {
                "success": False,
                "error": f"Failed to generate post for {product_sku} on {platform}",
                "agent": self.name,
            }

        # Emit brand signal
        self._emit_signal(
            signal_type="social_post",
            collection=post.collection,
            sku=product_sku,
            content=post.caption,
        )

        return {
            "success": True,
            "post": post.to_dict(),
            "agent": self.name,
        }

    def _generate_campaign(self, task: str, **kwargs: Any) -> dict[str, Any]:
        """Generate a multi-platform campaign."""
        agent = self._get_agent()

        collection = kwargs.get("collection", "")
        if not collection:
            collection = self._extract_collection(task)

        campaign_name = kwargs.get("campaign_name", "Collection Drop")

        campaign = agent.generate_campaign(
            collection,
            campaign_name,
            max_products=kwargs.get("max_products", 5),
            platforms=kwargs.get("platforms"),
            correlation_id=self.correlation_id,
        )

        # Emit signals for all campaign posts
        for post in campaign.posts:
            self._emit_signal(
                signal_type="social_post",
                collection=post.collection,
                sku=post.product_sku,
                content=post.caption,
            )

        return {
            "success": True,
            "campaign": campaign.to_dict(),
            "post_count": len(campaign.posts),
            "agent": self.name,
        }

    def _schedule_post(self, task: str, **kwargs: Any) -> dict[str, Any]:
        """Schedule a post for publishing."""
        agent = self._get_agent()
        post_id = kwargs.get("post_id", "")
        scheduled_at = kwargs.get("scheduled_at", "")

        if not post_id or not scheduled_at:
            return {
                "success": False,
                "error": "post_id and scheduled_at are required",
                "agent": self.name,
            }

        success = agent.schedule_post(
            post_id,
            scheduled_at,
            correlation_id=self.correlation_id,
        )

        return {"success": success, "post_id": post_id, "agent": self.name}

    def _publish_post(self, task: str, **kwargs: Any) -> dict[str, Any]:
        """Publish a post and track it."""
        agent = self._get_agent()
        post_id = kwargs.get("post_id", "")

        if not post_id:
            return {
                "success": False,
                "error": "post_id is required",
                "agent": self.name,
            }

        success = agent.publish_post(post_id, correlation_id=self.correlation_id)

        return {"success": success, "post_id": post_id, "agent": self.name}

    # -------------------------------------------------------------------------
    # A/B Variant Generation
    # -------------------------------------------------------------------------

    async def _generate_variants(self, task: str, **kwargs: Any) -> dict[str, Any]:
        """
        Generate multiple caption variants for A/B testing brand voice.

        Uses LLM to create variations — one closer to current brand voice,
        one pushing the boundaries slightly, one focusing on product features.
        """
        product_sku = kwargs.get("product_sku", "") or self._extract_sku(task)
        platform = kwargs.get("platform", "instagram")
        num_variants = kwargs.get("num_variants", 3)

        if not product_sku:
            return {
                "success": False,
                "error": "No product_sku provided",
                "agent": self.name,
            }

        agent = self._get_agent()
        product = agent._get_product(product_sku)
        if not product:
            return {
                "success": False,
                "error": f"Product not found: {product_sku}",
                "agent": self.name,
            }

        variant_prompt = (
            f"Generate {num_variants} distinct {platform} caption variants for "
            f"the product '{product.get('name', product_sku)}' from the "
            f"{product.get('collection', 'signature')} collection.\n\n"
            f"Variant A: Classic brand voice — elegant, aspirational, on-brand\n"
            f"Variant B: Edgy/experimental — push boundaries while staying luxury\n"
            f"Variant C: Product-focused — emphasize quality, materials, exclusivity\n\n"
            f"Brand: SkyyRose. No brand slogan is authorized.\n"
            f"Platform: {platform}. Keep within character limits.\n"
            f"Return each variant clearly labeled."
        )

        try:
            result = await self._llm_execute(variant_prompt)
            variants_content = result.get("result", "")

            # Emit signal for variant generation
            self._emit_signal(
                signal_type="content_generated",
                collection=product.get("collection", ""),
                sku=product_sku,
                content=variants_content,
                metadata={"variant_count": num_variants, "platform": platform},
            )

            return {
                "success": True,
                "variants": variants_content,
                "product_sku": product_sku,
                "platform": platform,
                "provider": result.get("provider"),
                "agent": self.name,
            }

        except Exception as exc:
            logger.error("[%s] Variant generation failed: %s", self.name, exc)
            return {
                "success": False,
                "error": str(exc),
                "agent": self.name,
            }

    # -------------------------------------------------------------------------
    # Engagement Tracking (feeds back to learning loop)
    # -------------------------------------------------------------------------

    def _record_engagement(self, task: str, **kwargs: Any) -> dict[str, Any]:
        """
        Record engagement metrics for a published post.

        Feeds engagement data back to the brand learning loop as
        a customer_feedback signal, closing the learning cycle.
        """
        post_id = kwargs.get("post_id", "")
        metrics = kwargs.get("metrics", {})
        accepted = kwargs.get("accepted")  # Human judgment: did this post perform well?

        if not post_id:
            return {
                "success": False,
                "error": "post_id is required",
                "agent": self.name,
            }

        agent = self._get_agent()
        post_data = agent.get_post(post_id)

        if not post_data:
            return {
                "success": False,
                "error": f"Post not found: {post_id}",
                "agent": self.name,
            }

        # Calculate quality score from engagement metrics
        quality_score = self._calculate_engagement_quality(metrics, post_data.get("platform", ""))

        # Emit feedback signal to learning loop
        self._emit_signal(
            signal_type="customer_feedback",
            collection=post_data.get("collection", ""),
            sku=post_data.get("product_sku", ""),
            content=post_data.get("caption", ""),
            quality_score=quality_score,
            accepted=accepted,
            metadata={
                "post_id": post_id,
                "platform": post_data.get("platform", ""),
                "metrics": metrics,
            },
        )

        return {
            "success": True,
            "post_id": post_id,
            "quality_score": quality_score,
            "metrics": metrics,
            "agent": self.name,
        }

    def _get_performance(self, **kwargs: Any) -> dict[str, Any]:
        """Get social media performance analytics."""
        agent = self._get_agent()
        analytics = agent.get_analytics()

        # Augment with brand health if learning loop available
        loop = self._get_learning_loop()
        brand_health = None
        if loop:
            brand_health = loop.get_brand_health_report()

        return {
            "success": True,
            "analytics": analytics,
            "brand_health": brand_health,
            "agent": self.name,
        }

    # -------------------------------------------------------------------------
    # Brand Learning Integration
    # -------------------------------------------------------------------------

    def _emit_signal(
        self,
        *,
        signal_type: str,
        collection: str = "",
        sku: str = "",
        content: str = "",
        quality_score: float = 0.0,
        accepted: bool | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Emit a brand signal to the learning loop."""
        loop = self._get_learning_loop()
        if loop is None:
            return

        try:
            from orchestration.brand_learning import BrandSignal, SignalType

            type_map = {
                "social_post": SignalType.SOCIAL_POST,
                "content_generated": SignalType.CONTENT_GENERATED,
                "customer_feedback": SignalType.CUSTOMER_FEEDBACK,
            }

            loop.observe(
                BrandSignal(
                    signal_type=type_map.get(signal_type, SignalType.CONTENT_GENERATED),
                    collection=collection,
                    sku=sku,
                    content=content[:500],  # Truncate for storage efficiency
                    agent_id=self.name,
                    quality_score=quality_score,
                    accepted=accepted,
                    metadata=metadata or {},
                )
            )
        except Exception as exc:
            # Learning loop errors should never break content generation
            logger.debug("[%s] Brand signal emission failed (non-fatal): %s", self.name, exc)

    @staticmethod
    def _calculate_engagement_quality(
        metrics: dict[str, int],
        platform: str,
    ) -> float:
        """
        Calculate a 0-100 quality score from engagement metrics.

        Uses platform-specific weighting since engagement norms differ.
        """
        if not metrics:
            return 0.0

        # Platform-specific metric weights
        weights: dict[str, dict[str, float]] = {
            "instagram": {
                "likes": 1.0,
                "comments": 3.0,
                "shares": 5.0,
                "saves": 4.0,
                "reach": 0.01,
            },
            "tiktok": {"views": 0.01, "likes": 1.0, "comments": 3.0, "shares": 5.0},
            "twitter": {"likes": 1.0, "retweets": 3.0, "replies": 2.0, "impressions": 0.005},
            "facebook": {"likes": 1.0, "comments": 2.0, "shares": 4.0, "reach": 0.005},
        }

        platform_weights = weights.get(platform, weights["instagram"])

        weighted_sum = sum(
            metrics.get(metric, 0) * weight for metric, weight in platform_weights.items()
        )

        # Normalize to 0-100 scale (sigmoid-like curve)
        # 50 weighted points = score of 50, 200 points = ~87
        score = 100 * (1 - 1 / (1 + weighted_sum / 100))
        return min(round(score, 1), 100.0)

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def _extract_sku(task: str) -> str:
        """Try to extract a product SKU from a natural language task."""
        import re

        patterns = [
            r"\b(br-\d{3})\b",
            r"\b(lh-\d{3})\b",
            r"\b(sg-\d{3})\b",
            r"\b(kids-\d{3})\b",
        ]
        for pattern in patterns:
            match = re.search(pattern, task, re.IGNORECASE)
            if match:
                return match.group(1).lower()
        return ""

    @staticmethod
    def _extract_collection(task: str) -> str:
        """Try to extract a collection name from a natural language task."""
        task_lower = task.lower()
        if "black rose" in task_lower or "black-rose" in task_lower:
            return "black-rose"
        if "love hurts" in task_lower or "love-hurts" in task_lower:
            return "love-hurts"
        if "signature" in task_lower:
            return "signature"
        if "kids" in task_lower:
            return "kids-capsule"
        return "signature"  # Default


__all__ = ["SocialMediaSubAgent"]
