"""
SkyyRose Social Media Agent
============================

Generates platform-optimized content for Instagram, TikTok, X/Twitter, Facebook.
Uses LLM routing to generate brand-voice captions, hashtag strategies, and campaign content.

Features:
- Platform-specific formatting (character limits, hashtag strategies, media recommendations)
- Campaign generation (multi-product, multi-platform)
- Brand voice enforcement (SkyyRose luxury fashion, "Luxury Grows from Concrete.", rose gold #B76E79)
- Content types: product_launch, collection_drop, behind_scenes, lifestyle, engagement
- Scheduling recommendations based on platform best practices
- 3 collections: Black Rose (gothic luxury), Love Hurts (street passion), Signature (West Coast luxury)

Author: DevSkyy Platform Team
Version: 2.0.0
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


# =============================================================================
# Constants & Configuration
# =============================================================================

# Maximum in-memory tracking size (LRU eviction for unbounded collections)
_MAX_QUEUE_SIZE = 5000
_MAX_PUBLISHED_SIZE = 10000

BRAND_NAME = "SkyyRose"
BRAND_TAGLINE = "Luxury Grows from Concrete."
BRAND_PRIMARY_COLOR = "#B76E79"  # Rose gold
BRAND_ORIGIN = "Oakland, CA"
BRAND_SITE = "skyyrose.co"


class Platform(StrEnum):
    """Supported social media platforms."""

    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"


class ContentType(StrEnum):
    """Social media content types."""

    PRODUCT_LAUNCH = "product_launch"
    COLLECTION_DROP = "collection_drop"
    BEHIND_SCENES = "behind_scenes"
    LIFESTYLE = "lifestyle"
    ENGAGEMENT = "engagement"


class PostStatus(StrEnum):
    """Post lifecycle status."""

    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"


# Platform-specific configuration
PLATFORMS: dict[str, dict[str, Any]] = {
    Platform.INSTAGRAM: {
        "name": "Instagram",
        "max_caption_length": 2200,
        "max_hashtags": 30,
        "optimal_hashtags": 15,
        "content_types": ["post", "story", "reel", "carousel"],
        "image_sizes": {
            "square": "1080x1080",
            "portrait": "1080x1350",
            "landscape": "1080x608",
            "story": "1080x1920",
            "reel": "1080x1920",
        },
        "best_posting_times": {
            "monday": ["11:00", "14:00"],
            "tuesday": ["10:00", "14:00"],
            "wednesday": ["11:00", "14:00"],
            "thursday": ["11:00", "14:00", "15:00"],
            "friday": ["10:00", "14:00"],
            "saturday": ["10:00", "13:00"],
            "sunday": ["10:00", "14:00"],
        },
        "engagement_tips": [
            "Use carousel posts for higher engagement",
            "Reels get 2x more reach than static posts",
            "Include a CTA in every caption",
            "First line should hook — newlines after for readability",
        ],
    },
    Platform.TIKTOK: {
        "name": "TikTok",
        "max_caption_length": 2200,
        "max_hashtags": 5,
        "optimal_hashtags": 4,
        "content_types": ["video", "photo", "story"],
        "video_max_duration": 180,
        "image_sizes": {
            "video": "1080x1920",
            "photo": "1080x1920",
        },
        "best_posting_times": {
            "monday": ["12:00", "16:00"],
            "tuesday": ["09:00", "12:00", "19:00"],
            "wednesday": ["12:00", "19:00"],
            "thursday": ["12:00", "15:00", "19:00"],
            "friday": ["12:00", "15:00"],
            "saturday": ["11:00", "19:00"],
            "sunday": ["11:00", "16:00"],
        },
        "engagement_tips": [
            "Hook within first 1-2 seconds",
            "Trending sounds boost discoverability",
            "Behind-the-scenes content performs well for fashion",
            "Show the product in motion — textures, drape, fit",
        ],
    },
    Platform.TWITTER: {
        "name": "X / Twitter",
        "max_caption_length": 280,
        "max_hashtags": 3,
        "optimal_hashtags": 2,
        "content_types": ["tweet", "thread", "media"],
        "image_sizes": {
            "single": "1200x675",
            "two_images": "700x800",
            "card": "800x418",
        },
        "best_posting_times": {
            "monday": ["08:00", "12:00"],
            "tuesday": ["09:00", "12:00"],
            "wednesday": ["09:00", "12:00"],
            "thursday": ["09:00", "12:00"],
            "friday": ["09:00", "11:00"],
            "saturday": ["09:00"],
            "sunday": ["09:00"],
        },
        "engagement_tips": [
            "Keep it punchy — luxury in few words",
            "Threads for storytelling (collection drops)",
            "Quote tweets for community engagement",
            "Pin new product tweets for 48h",
        ],
    },
    Platform.FACEBOOK: {
        "name": "Facebook",
        "max_caption_length": 63206,
        "max_hashtags": 10,
        "optimal_hashtags": 5,
        "content_types": ["post", "story", "reel", "event"],
        "image_sizes": {
            "post": "1200x630",
            "story": "1080x1920",
            "event_cover": "1920x1005",
        },
        "best_posting_times": {
            "monday": ["09:00", "12:00"],
            "tuesday": ["09:00", "12:00", "15:00"],
            "wednesday": ["09:00", "12:00"],
            "thursday": ["09:00", "12:00", "14:00"],
            "friday": ["09:00", "11:00"],
            "saturday": ["10:00"],
            "sunday": ["10:00"],
        },
        "engagement_tips": [
            "Longer captions perform well on Facebook",
            "Video content gets 6x more engagement",
            "Ask questions to drive comments",
            "Use Facebook Events for collection drops",
        ],
    },
}


# Collection-specific brand context
COLLECTIONS: dict[str, dict[str, Any]] = {
    "black-rose": {
        "name": "Black Rose",
        "full_name": "Black Rose Collection",
        "mood": "Gothic luxury, dark elegance, shadow and light",
        "aesthetic": "Cathedral ceilings, stained glass, midnight gardens",
        "tone": "Mysterious, commanding, unapologetically dark",
        "color_palette": ["#1A1A1A", "#C0C0C0", "#8B0000"],
        "hashtags": [
            "#SkyyRose",
            "#BlackRoseCollection",
            "#GothicLuxury",
            "#DarkRomance",
            "#LuxuryGrowsFromConcrete",
            "#DarkAesthetic",
            "#WearableArt",
            "#LuxuryStreetwear",
            "#BayAreaFashion",
            "#LimitedEdition",
            "#DarkElegance",
            "#SkyyRoseBlackRose",
        ],
        "caption_hooks": [
            "From the shadows, beauty rises.",
            "Not everyone can wear the dark.",
            "Where gothic meets gold.",
            "Born in darkness. Draped in luxury.",
        ],
    },
    "love-hurts": {
        "name": "Love Hurts",
        "full_name": "Love Hurts Collection",
        "mood": "Street passion, tender rebellion, emotional rawness",
        "aesthetic": "Oakland streets, neon nights, raw emotion",
        "tone": "Passionate, vulnerable yet fierce, authentic",
        "color_palette": ["#B76E79", "#FF1744", "#1A1A1A"],
        "hashtags": [
            "#SkyyRose",
            "#LoveHurts",
            "#OaklandFashion",
            "#LuxuryGrowsFromConcrete",
            "#GritAndGrace",
            "#UrbanLuxury",
            "#BayAreaStyle",
            "#StreetwearFashion",
            "#Authentic",
            "#PassionWearable",
            "#LoveHurtsCollection",
            "#SkyyRoseLH",
        ],
        "caption_hooks": [
            "Love hurts. But it looks incredible.",
            "Wear your heart on your sleeve. Literally.",
            "Passion stitched into every thread.",
            "For those who feel everything and hide nothing.",
        ],
    },
    "signature": {
        "name": "Signature",
        "full_name": "Signature Collection",
        "mood": "West Coast luxury, golden hour vibes, timeless elevation",
        "aesthetic": "Bay Area bridges, coastal sunsets, elevated streetwear",
        "tone": "Confident, aspirational, effortlessly cool",
        "color_palette": ["#C9A962", "#1A1A1A", "#FFFFFF"],
        "hashtags": [
            "#SkyyRose",
            "#SignatureCollection",
            "#LuxuryFashion",
            "#LuxuryGrowsFromConcrete",
            "#BayAreaLuxury",
            "#WestCoastStyle",
            "#CoutureStreetwear",
            "#ElevatedStyle",
            "#PrestigeWear",
            "#StayGolden",
            "#SignatureSkyy",
            "#TheSignature",
        ],
        "caption_hooks": [
            "Signature. Not just a name \u2014 a standard.",
            "West Coast luxury, worldwide respect.",
            "Stay golden. Stay elevated.",
            "The signature of a generation.",
        ],
    },
}


# Product catalog — loaded from the canonical skyyrose-catalog.csv (single source of truth)
def _load_catalog() -> dict[str, dict[str, str]]:
    from skyyrose.core.catalog_loader import CATALOG_CSV, read_catalog_rows

    catalog: dict[str, dict[str, str]] = {}
    try:
        # read_catalog_rows() opens the canonical CSV and skips blank-SKU rows;
        # it is @cache-memoized, so repeated callers share one parse.
        for row in read_catalog_rows():
            catalog[row["sku"].strip()] = {
                "name": row["name"].strip(),
                "collection": row["collection"].strip(),
            }
    except FileNotFoundError:
        logger.warning(
            "PRODUCT_CATALOG empty — %s not generated. Run "
            "'python scripts/sync_product_registry.py'; product facts come only from "
            "the product registry (skyyrose.core.product.get_product).",
            CATALOG_CSV,
        )
    return catalog


PRODUCT_CATALOG: dict[str, dict[str, str]] = _load_catalog()


# Content type templates
CONTENT_TEMPLATES: dict[str, dict[str, Any]] = {
    ContentType.PRODUCT_LAUNCH: {
        "description": "New product announcement with excitement and urgency",
        "platforms": [Platform.INSTAGRAM, Platform.TIKTOK, Platform.TWITTER, Platform.FACEBOOK],
        "tone_modifier": "exciting, exclusive, urgent",
        "cta": "Pre-order now at {site}",
    },
    ContentType.COLLECTION_DROP: {
        "description": "Full collection release with storytelling",
        "platforms": [Platform.INSTAGRAM, Platform.TIKTOK, Platform.TWITTER, Platform.FACEBOOK],
        "tone_modifier": "epic, narrative, cinematic",
        "cta": "Explore the collection at {site}",
    },
    ContentType.BEHIND_SCENES: {
        "description": "Behind the scenes of creation process",
        "platforms": [Platform.INSTAGRAM, Platform.TIKTOK],
        "tone_modifier": "intimate, authentic, process-focused",
        "cta": "Follow the journey",
    },
    ContentType.LIFESTYLE: {
        "description": "Lifestyle content connecting brand to culture",
        "platforms": [Platform.INSTAGRAM, Platform.FACEBOOK],
        "tone_modifier": "aspirational, cultural, storytelling",
        "cta": "Live the luxury at {site}",
    },
    ContentType.ENGAGEMENT: {
        "description": "Community engagement and conversation starters",
        "platforms": [Platform.INSTAGRAM, Platform.TWITTER, Platform.TIKTOK, Platform.FACEBOOK],
        "tone_modifier": "conversational, inclusive, question-driven",
        "cta": "Drop your take below",
    },
}


# =============================================================================
# Data Models
# =============================================================================


@dataclass
class SocialPost:
    """Represents a social media post in the pipeline."""

    id: str = ""
    platform: str = ""
    content_type: str = "product_launch"
    caption: str = ""
    hashtags: list[str] = field(default_factory=list)
    media_urls: list[str] = field(default_factory=list)
    product_sku: str = ""
    collection: str = ""
    scheduled_at: str | None = None
    published_at: str | None = None
    status: str = PostStatus.DRAFT
    engagement: dict[str, int] = field(default_factory=dict)
    media_recommendations: dict[str, str] = field(default_factory=dict)
    scheduling_recommendation: str | None = None
    correlation_id: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def __post_init__(self) -> None:
        if not self.id:
            raw = f"{self.platform}:{self.product_sku}:{uuid.uuid4().hex[:8]}"
            self.id = hashlib.sha256(raw.encode()).hexdigest()[:12]

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for API responses."""
        return {
            "id": self.id,
            "platform": self.platform,
            "content_type": self.content_type,
            "caption": self.caption,
            "hashtags": self.hashtags,
            "media_urls": self.media_urls,
            "product_sku": self.product_sku,
            "collection": self.collection,
            "scheduled_at": self.scheduled_at,
            "published_at": self.published_at,
            "status": self.status,
            "engagement": self.engagement,
            "media_recommendations": self.media_recommendations,
            "scheduling_recommendation": self.scheduling_recommendation,
            "created_at": self.created_at,
        }


@dataclass
class Campaign:
    """Represents a multi-platform campaign."""

    id: str = ""
    name: str = ""
    collection: str = ""
    posts: list[SocialPost] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    status: str = "draft"
    correlation_id: str | None = None

    def __post_init__(self) -> None:
        if not self.id:
            self.id = hashlib.sha256(
                f"{self.name}:{self.collection}:{uuid.uuid4().hex[:8]}".encode()
            ).hexdigest()[:12]

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "collection": self.collection,
            "posts": [p.to_dict() for p in self.posts],
            "created_at": self.created_at,
            "status": self.status,
        }


# =============================================================================
# Social Media Agent
# =============================================================================


class SocialMediaAgent:
    """
    SkyyRose Social Media Agent.

    Manages social media content lifecycle:
    - Generate platform-optimized captions with brand voice enforcement
    - Schedule posts with platform-specific timing recommendations
    - Track engagement analytics across all platforms
    - Generate multi-product, multi-platform campaigns
    - Enforce SkyyRose brand identity in every piece of content

    Uses LLM routing when available, falls back to template-based generation.

    Example:
        agent = SocialMediaAgent()
        post = agent.generate_post(
            product_sku="br-001",
            platform="instagram",
            content_type="product_launch",
            correlation_id="abc123",
        )
    """

    def __init__(
        self,
        product_data_path: str | None = None,
        *,
        correlation_id: str | None = None,
    ) -> None:
        self._correlation_id = correlation_id
        if product_data_path is not None:
            logger.warning(
                "product_data_path is ignored: product facts now resolve through "
                "skyyrose.core.product.get_product, the single product entry point."
            )

        # Post queue with bounded size (LRU eviction to prevent memory exhaustion)
        self._post_queue: OrderedDict[str, SocialPost] = OrderedDict()
        self._published: OrderedDict[str, SocialPost] = OrderedDict()
        self._campaigns: OrderedDict[str, Campaign] = OrderedDict()

        # Platform analytics
        self._analytics: dict[str, dict[str, int]] = {
            Platform.INSTAGRAM: {"posts": 0, "likes": 0, "comments": 0, "shares": 0, "reach": 0},
            Platform.TIKTOK: {"posts": 0, "views": 0, "likes": 0, "shares": 0},
            Platform.TWITTER: {"posts": 0, "likes": 0, "retweets": 0, "impressions": 0},
            Platform.FACEBOOK: {"posts": 0, "likes": 0, "comments": 0, "shares": 0, "reach": 0},
        }

        # LLM client (lazy-loaded)
        self._llm_client: Any = None

    # =========================================================================
    # Product Data
    # =========================================================================

    def _get_product(self, sku: str) -> dict[str, Any] | None:
        """Product facts for `sku`, read through the single entry point.

        Returns the fields caption generation needs, flattened from the record
        that ``skyyrose.core.product.get_product`` assembles. That call is the
        one read path for product facts -- this agent no longer keeps its own
        merge of a CSV projection and a side-store, so it cannot drift from the
        registry or invent its own precedence between them.

        ``caption_is_authored`` tells the caller whether a platform caption was
        actually written for this SKU. 14 of 33 products have no social copy
        yet; the record names that in its ``gaps`` rather than returning an
        empty string, so a generated caption is never mistaken for an authored
        one.

        Returns None when the SKU is not in the registry -- never a fabricated
        record.
        """
        from skyyrose.core.product import get_product

        try:
            record = get_product(sku)
        except KeyError:
            logger.warning("SKU %s is not in the product registry", sku)
            return None

        content = record["content"]

        def _value(field: str) -> str | None:
            entry = content.get(field)
            return entry["value"] if entry else None

        return {
            "sku": sku,
            "name": record["name"],
            "collection": record["collection"],
            "short_description": _value("short_description") or "",
            "instagram": _value("instagram"),
            "tiktok": _value("tiktok"),
            "caption_is_authored": {
                Platform.INSTAGRAM: _value("instagram") is not None,
                Platform.TIKTOK: _value("tiktok") is not None,
            },
            "gaps": record["gaps"],
        }

    # =========================================================================
    # Caption Generation
    # =========================================================================

    def _generate_caption(
        self,
        product: dict[str, Any],
        platform: str,
        content_type: str,
        *,
        correlation_id: str | None = None,
    ) -> str:
        """Generate a platform-optimized caption with SkyyRose brand voice.

        Falls back to template-based generation when LLM is unavailable.

        Args:
            product: Product data dictionary
            platform: Target platform
            content_type: Type of content
            correlation_id: Tracing correlation ID

        Returns:
            Brand-voice caption string
        """
        name = product.get("name", "SkyyRose")
        collection_key = product.get("collection", "signature")
        collection = COLLECTIONS.get(collection_key, COLLECTIONS["signature"])
        short_desc = product.get("short_description", "")
        platform_config = PLATFORMS.get(platform, PLATFORMS[Platform.INSTAGRAM])

        # Check for pre-written platform captions in product data
        if platform == Platform.INSTAGRAM and product.get("instagram"):
            return str(product["instagram"])
        if platform == Platform.TIKTOK and product.get("tiktok"):
            return str(product["tiktok"])

        # Template-based generation (brand voice enforced)
        caption_parts: list[str] = []

        # Hook — use collection-specific hooks
        hooks = collection.get("caption_hooks", [])
        if hooks:
            # Deterministic selection based on product name hash
            hook_idx = int(
                hashlib.md5(name.encode(), usedforsecurity=False).hexdigest()[:8], 16
            ) % len(hooks)
            caption_parts.append(hooks[hook_idx])

        # Platform-specific formatting
        if platform == Platform.TWITTER:
            # Twitter: ultra-concise, punchy
            if short_desc:
                truncated = short_desc[:120]
                caption_parts.append(f"\n\n{name}. {truncated}")
            else:
                caption_parts.append(f"\n\n{name} \u2014 {collection['full_name']}.")
            caption_parts.append(f"\n\n{BRAND_SITE}")

        elif platform == Platform.TIKTOK:
            # TikTok: short, trending, video-first
            caption_parts.append(f"\n\n{name}")
            if short_desc:
                caption_parts.append(f"\n{short_desc[:200]}")
            caption_parts.append(f"\n\nPre-order: {BRAND_SITE}")

        elif platform == Platform.INSTAGRAM:
            # Instagram: storytelling with structure
            caption_parts.append(f"\n\nIntroducing {name}")
            caption_parts.append(f"from the {collection['full_name']}.")
            if short_desc:
                caption_parts.append(f"\n\n{short_desc[:500]}")
            caption_parts.append(f"\n\n{BRAND_TAGLINE}")
            cta = (
                CONTENT_TEMPLATES.get(content_type, CONTENT_TEMPLATES[ContentType.PRODUCT_LAUNCH])
                .get("cta", "")
                .format(site=BRAND_SITE)
            )
            if cta:
                caption_parts.append(f"\n\n{cta}")

        else:
            # Facebook: longer form
            caption_parts.append(f"\n\n{name}")
            caption_parts.append(f"Part of the {collection['full_name']}.")
            caption_parts.append(f"\n\n{collection['mood']}")
            if short_desc:
                caption_parts.append(f"\n\n{short_desc[:800]}")
            caption_parts.append(f'\n\n"{BRAND_TAGLINE}" \u2014 {BRAND_NAME}')
            cta = (
                CONTENT_TEMPLATES.get(content_type, CONTENT_TEMPLATES[ContentType.PRODUCT_LAUNCH])
                .get("cta", "")
                .format(site=BRAND_SITE)
            )
            if cta:
                caption_parts.append(f"\n\n{cta}")

        caption = " ".join(caption_parts).strip()

        # Enforce character limit
        max_len = platform_config.get("max_caption_length", 2200)
        if len(caption) > max_len:
            caption = caption[: max_len - 3] + "..."

        return caption

    def _select_hashtags(
        self,
        collection_key: str,
        platform: str,
        content_type: str,
    ) -> list[str]:
        """Select platform-appropriate hashtags for a collection.

        Uses optimal hashtag count per platform, not just the maximum.

        Args:
            collection_key: Collection identifier
            platform: Target platform
            content_type: Content type for additional tags

        Returns:
            List of hashtag strings
        """
        collection = COLLECTIONS.get(collection_key, COLLECTIONS["signature"])
        platform_config = PLATFORMS.get(platform, PLATFORMS[Platform.INSTAGRAM])

        # Base collection hashtags
        base_tags = list(collection.get("hashtags", []))

        # Add content-type specific tags
        content_tags: dict[str, list[str]] = {
            ContentType.PRODUCT_LAUNCH: ["#NewArrival", "#JustDropped", "#PreOrder"],
            ContentType.COLLECTION_DROP: ["#CollectionDrop", "#NewCollection", "#FashionDrop"],
            ContentType.BEHIND_SCENES: ["#BTS", "#BehindTheScenes", "#MakingOf"],
            ContentType.LIFESTYLE: ["#StreetStyle", "#OOTD", "#FashionLife"],
            ContentType.ENGAGEMENT: ["#FashionCommunity", "#StyleTalk"],
        }
        base_tags.extend(content_tags.get(content_type, []))

        # Trim to optimal count for platform
        optimal = platform_config.get("optimal_hashtags", 10)
        return base_tags[:optimal]

    def _get_media_recommendations(self, platform: str) -> dict[str, str]:
        """Get media size and format recommendations for a platform.

        Args:
            platform: Target platform

        Returns:
            Dictionary with recommended sizes and tips
        """
        config = PLATFORMS.get(platform, PLATFORMS[Platform.INSTAGRAM])
        sizes = config.get("image_sizes", {})
        tips = config.get("engagement_tips", [])

        recommendations = {"sizes": json.dumps(sizes)}
        if tips:
            recommendations["tip"] = tips[0]  # Lead tip
        return recommendations

    def _get_scheduling_recommendation(self, platform: str) -> str:
        """Get the next optimal posting time for a platform.

        Args:
            platform: Target platform

        Returns:
            Human-readable scheduling recommendation
        """
        config = PLATFORMS.get(platform, PLATFORMS[Platform.INSTAGRAM])
        times = config.get("best_posting_times", {})

        now = datetime.now(UTC)
        day_name = now.strftime("%A").lower()
        today_times = times.get(day_name, [])

        if today_times:
            # Find the next available time today
            current_hour = now.strftime("%H:%M")
            future_times = [t for t in today_times if t > current_hour]
            if future_times:
                return f"Recommended: Today at {future_times[0]} UTC"

        # Suggest tomorrow's first slot
        tomorrow = now + timedelta(days=1)
        tomorrow_name = tomorrow.strftime("%A").lower()
        tomorrow_times = times.get(tomorrow_name, ["10:00"])
        return f"Recommended: {tomorrow.strftime('%A')} at {tomorrow_times[0]} UTC"

    # =========================================================================
    # Post Generation
    # =========================================================================

    def generate_post(
        self,
        product_sku: str,
        platform: str,
        content_type: str = ContentType.PRODUCT_LAUNCH,
        *,
        correlation_id: str | None = None,
    ) -> SocialPost | None:
        """Generate a social media post for a product on a specific platform.

        Args:
            product_sku: Product SKU from catalog
            platform: Target platform (instagram, tiktok, twitter, facebook)
            content_type: Content type for tone/formatting
            correlation_id: Tracing correlation ID

        Returns:
            SocialPost if successful, None if product/platform invalid
        """
        cid = correlation_id or self._correlation_id

        # Validate platform
        if platform not in PLATFORMS:
            logger.error(
                "Unknown platform: %s [correlation_id=%s]",
                platform,
                cid,
            )
            return None

        # Validate product
        product = self._get_product(product_sku)
        if not product:
            logger.error(
                "Product not found: %s [correlation_id=%s]",
                product_sku,
                cid,
            )
            return None

        collection_key = product.get("collection", "signature")

        # Generate caption
        caption = self._generate_caption(
            product,
            platform,
            content_type,
            correlation_id=cid,
        )

        # Select hashtags
        hashtags = self._select_hashtags(collection_key, platform, content_type)

        # Media recommendations
        media_recs = self._get_media_recommendations(platform)

        # Scheduling recommendation
        schedule_rec = self._get_scheduling_recommendation(platform)

        post = SocialPost(
            platform=platform,
            content_type=content_type,
            caption=caption,
            hashtags=hashtags,
            product_sku=product_sku,
            collection=collection_key,
            status=PostStatus.DRAFT,
            media_recommendations=media_recs,
            scheduling_recommendation=schedule_rec,
            correlation_id=cid,
        )

        # Add to queue with bounded size
        self._post_queue[post.id] = post
        while len(self._post_queue) > _MAX_QUEUE_SIZE:
            self._post_queue.popitem(last=False)  # FIFO eviction

        logger.info(
            "Generated %s post for %s on %s: %s [correlation_id=%s]",
            content_type,
            product_sku,
            platform,
            post.id,
            cid,
        )
        return post

    # =========================================================================
    # Campaign Generation
    # =========================================================================

    def generate_campaign(
        self,
        collection: str,
        campaign_name: str = "Collection Drop",
        *,
        max_products: int = 5,
        platforms: list[str] | None = None,
        correlation_id: str | None = None,
    ) -> Campaign:
        """Generate a multi-platform campaign for an entire collection.

        Creates posts for each product in the collection across all
        specified platforms.

        Args:
            collection: Collection key (black-rose, love-hurts, signature)
            campaign_name: Human-readable campaign name
            max_products: Maximum products to include (default 5)
            platforms: Platforms to target (default: all 4)
            correlation_id: Tracing correlation ID

        Returns:
            Campaign with generated posts
        """
        cid = correlation_id or self._correlation_id
        target_platforms = platforms or [
            Platform.INSTAGRAM,
            Platform.TIKTOK,
            Platform.TWITTER,
            Platform.FACEBOOK,
        ]

        # Find products in collection
        collection_products = [
            (sku, prod)
            for sku, prod in PRODUCT_CATALOG.items()
            if prod.get("collection") == collection
        ]

        campaign = Campaign(
            name=campaign_name,
            collection=collection,
            correlation_id=cid,
        )

        if not collection_products:
            logger.warning(
                "No products found for collection: %s [correlation_id=%s]",
                collection,
                cid,
            )
            return campaign

        # Generate posts for each product across platforms
        for sku, _ in collection_products[:max_products]:
            for platform in target_platforms:
                post = self.generate_post(
                    sku,
                    platform,
                    ContentType.COLLECTION_DROP,
                    correlation_id=cid,
                )
                if post:
                    campaign.posts.append(post)

        # Store campaign with bounded size
        self._campaigns[campaign.id] = campaign
        while len(self._campaigns) > 500:
            self._campaigns.popitem(last=False)

        logger.info(
            "Generated campaign '%s' with %d posts for %s [correlation_id=%s]",
            campaign_name,
            len(campaign.posts),
            collection,
            cid,
        )
        return campaign

    # =========================================================================
    # Scheduling & Publishing
    # =========================================================================

    def schedule_post(
        self,
        post_id: str,
        scheduled_at: str,
        *,
        correlation_id: str | None = None,
    ) -> bool:
        """Schedule a post for publishing at a specific time.

        Args:
            post_id: Post identifier
            scheduled_at: ISO 8601 datetime string
            correlation_id: Tracing correlation ID

        Returns:
            True if scheduled, False if post not found
        """
        cid = correlation_id or self._correlation_id

        if post_id not in self._post_queue:
            logger.error(
                "Post not found for scheduling: %s [correlation_id=%s]",
                post_id,
                cid,
            )
            return False

        post = self._post_queue[post_id]
        post.scheduled_at = scheduled_at
        post.status = PostStatus.SCHEDULED

        logger.info(
            "Scheduled post %s for %s [correlation_id=%s]",
            post_id,
            scheduled_at,
            cid,
        )
        return True

    def publish_post(
        self,
        post_id: str,
        *,
        correlation_id: str | None = None,
    ) -> bool:
        """Publish a post (stub for actual platform API integration).

        In production, this would call the platform's API to actually
        publish the content. Currently marks the post as published
        and updates analytics.

        Args:
            post_id: Post identifier
            correlation_id: Tracing correlation ID

        Returns:
            True if published, False if post not found
        """
        cid = correlation_id or self._correlation_id

        if post_id not in self._post_queue:
            logger.error(
                "Post not found for publishing: %s [correlation_id=%s]",
                post_id,
                cid,
            )
            return False

        post = self._post_queue.pop(post_id)
        post.published_at = datetime.now(UTC).isoformat()
        post.status = PostStatus.PUBLISHED

        # Move to published tracking
        self._published[post.id] = post
        while len(self._published) > _MAX_PUBLISHED_SIZE:
            self._published.popitem(last=False)

        # Update analytics
        if post.platform in self._analytics:
            self._analytics[post.platform]["posts"] += 1

        logger.info(
            "Published post %s on %s [correlation_id=%s]",
            post_id,
            post.platform,
            cid,
        )
        return True

    # =========================================================================
    # Queue & Analytics
    # =========================================================================

    def get_queue(self) -> list[dict[str, Any]]:
        """Get all posts currently in the queue.

        Returns:
            List of serialized post dictionaries
        """
        return [post.to_dict() for post in self._post_queue.values()]

    def get_analytics(self) -> dict[str, Any]:
        """Get analytics summary across all platforms.

        Returns:
            Dictionary with platform stats, totals, and queue size
        """
        return {
            "platforms": dict(self._analytics),
            "total_posts": sum(stats.get("posts", 0) for stats in self._analytics.values()),
            "total_queue": len(self._post_queue),
            "total_published": len(self._published),
        }

    def get_post(self, post_id: str) -> dict[str, Any] | None:
        """Get a specific post by ID from queue or published.

        Args:
            post_id: Post identifier

        Returns:
            Serialized post dictionary or None
        """
        if post_id in self._post_queue:
            return self._post_queue[post_id].to_dict()
        if post_id in self._published:
            return self._published[post_id].to_dict()
        return None

    def get_platform_config(self, platform: str) -> dict[str, Any] | None:
        """Get configuration for a specific platform.

        Args:
            platform: Platform identifier

        Returns:
            Platform configuration dictionary or None
        """
        return PLATFORMS.get(platform)

    def get_collection_context(self, collection: str) -> dict[str, Any] | None:
        """Get brand context for a specific collection.

        Args:
            collection: Collection key

        Returns:
            Collection context dictionary or None
        """
        return COLLECTIONS.get(collection)


# =============================================================================
# Singleton Instance
# =============================================================================

social_media_agent = SocialMediaAgent()

__all__ = [
    "SocialMediaAgent",
    "SocialPost",
    "Campaign",
    "Platform",
    "ContentType",
    "PostStatus",
    "PLATFORMS",
    "COLLECTIONS",
    "PRODUCT_CATALOG",
    "CONTENT_TEMPLATES",
    "social_media_agent",
]
