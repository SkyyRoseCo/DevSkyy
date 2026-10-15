"""SkyyRose Imagery Agent for DevSkyy Platform.

Generates on-brand placeholder imagery for the WordPress theme.
Creates AI model photos wearing brand assets with collection-specific
styling to complete the visual identity of the site.

Author: DevSkyy Platform Team
Version: 1.0.0
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from services.three_d.gemini_provider import GeminiImageProvider
from services.three_d.provider_factory import ThreeDProviderFactory, get_provider_factory
from services.three_d.provider_interface import QualityLevel, ThreeDRequest

from adk.base import ADKProvider, AgentResult, AgentStatus
from agents.base_super_agent import EnhancedSuperAgent, SuperAgentType
from orchestration.brand_context import BrandContextInjector, Collection

logger = logging.getLogger(__name__)


# =============================================================================
# Data Models
# =============================================================================


class ImageryPurpose(StrEnum):
    """Purpose of generated imagery."""

    HERO_BANNER = "hero_banner"
    COLLECTION_SHOWCASE = "collection_showcase"
    PRODUCT_MODEL = "product_model"
    LIFESTYLE = "lifestyle"
    CAMPAIGN = "campaign"
    BACKGROUND = "background"


class ModelPose(StrEnum):
    """AI model pose styles."""

    EDITORIAL = "editorial"
    RUNWAY = "runway"
    CASUAL_ELEGANT = "casual_elegant"
    DRAMATIC = "dramatic"
    MINIMAL = "minimal"


@dataclass
class ImageryRequest:
    """Request for brand imagery generation."""

    purpose: ImageryPurpose
    collection: Collection
    model_pose: ModelPose = ModelPose.EDITORIAL
    brand_assets: list[str] = field(default_factory=list)
    additional_context: str = ""
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GeneratedImage:
    """Result of image generation."""

    url: str
    purpose: ImageryPurpose
    collection: Collection
    model_pose: ModelPose
    prompt_used: str
    provider: str
    wp_media_id: int | None = None
    uploaded_at: datetime | None = None
    correlation_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ImageryBatch:
    """Batch of generated images."""

    batch_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    images: list[GeneratedImage] = field(default_factory=list)
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    errors: list[str] = field(default_factory=list)


# =============================================================================
# Brand Prompt Templates
# =============================================================================

COLLECTION_PROMPTS = {
    Collection.SIGNATURE: {
        "setting": "luxurious gold-lit studio, marble surfaces, soft amber lighting",
        "palette": "gold, cream, champagne, warm blacks",
        "mood": "regal, timeless, commanding presence",
        "accessories": "18k gold jewelry, premium silk fabrics, understated elegance",
    },
    Collection.BLACK_ROSE: {
        "setting": "midnight garden, dramatic silver moonlight, gothic archways, dark roses",
        "palette": "black, silver, deep violet, midnight blue",
        "mood": "mysterious, gothic elegance, shadow and light",
        "accessories": "sterling silver pieces, dark leather, black roses as props",
    },
    Collection.LOVE_HURTS: {
        "setting": "candlelit castle, rose petals, soft pink fog, romantic haze",
        "palette": "rose gold, blush pink, deep crimson, soft whites",
        "mood": "passionate vulnerability, tender romance, bittersweet beauty",
        "accessories": "rose gold jewelry, flowing fabrics, red roses, candles",
    },
}

PURPOSE_DIRECTIVES = {
    ImageryPurpose.HERO_BANNER: (
        "Full-width editorial shot. Model should be prominently positioned "
        "with space for text overlay on one side. Cinematic composition."
    ),
    ImageryPurpose.COLLECTION_SHOWCASE: (
        "Showcase the collection's aesthetic. Model in full outfit, "
        "styled to highlight the collection's unique identity. "
        "Strong visual hierarchy."
    ),
    ImageryPurpose.PRODUCT_MODEL: (
        "Close-up or three-quarter shot focusing on the brand assets "
        "and accessories the model is wearing. Product is the hero."
    ),
    ImageryPurpose.LIFESTYLE: (
        "Candid, aspirational lifestyle moment. Model in a setting that "
        "reflects the brand's Oakland roots meets luxury aesthetic. "
        "Natural, authentic feel."
    ),
    ImageryPurpose.CAMPAIGN: (
        "High-impact campaign imagery. Bold, striking, memorable. "
        "Could be used as the face of a marketing push. "
        "Emotional resonance is key."
    ),
    ImageryPurpose.BACKGROUND: (
        "Abstract or environmental shot that captures the collection's mood "
        "without a model. Texture, atmosphere, and brand colors take center stage."
    ),
}

POSE_DIRECTIVES = {
    ModelPose.EDITORIAL: "posed with editorial confidence, fashion-forward stance",
    ModelPose.RUNWAY: "mid-stride runway walk, dynamic movement, fierce energy",
    ModelPose.CASUAL_ELEGANT: "relaxed yet refined posture, effortless style",
    ModelPose.DRAMATIC: "dramatic pose with tension and emotion, theatrical lighting",
    ModelPose.MINIMAL: "clean, minimalist pose, architectural stillness",
}


# =============================================================================
# Agent
# =============================================================================


class SkyyRoseImageryAgent(EnhancedSuperAgent):
    """Imagery Agent specialized for SkyyRose brand visual generation.

    Generates on-brand placeholder imagery featuring AI models wearing
    brand assets. Each image is collection-specific, styled to match
    the visual DNA of the SkyyRose WordPress theme.

    Capabilities:
    - AI model photo generation with brand styling
    - Collection-specific imagery (Signature, Black Rose, Love Hurts)
    - Hero banners, product shots, lifestyle, campaign imagery
    - WordPress media library integration via wordpress-ops
    - Batch generation for full theme rollouts

    Integration:
    - GeminiImageProvider for AI image generation
    - ThreeDProviderFactory for fallback providers
    - BrandContextInjector for prompt engineering
    - WordPressComClient for media uploads
    """

    agent_type = SuperAgentType.CREATIVE
    AGENT_NAME = "skyyrose_imagery_agent"
    AGENT_VERSION = "1.0.0"

    SYSTEM_PROMPT = """You are the SkyyRose Imagery Agent for DevSkyy.

Your sole purpose: Generate on-brand placeholder imagery for the SkyyRose WordPress theme.
You create AI model photos that wear and showcase brand assets, styled per collection identity.

Brand: SkyyRose — Oakland-inspired luxury fashion.

Collections:
- Signature: Gold luxury, regal, timeless. 18k gold accents.
- Black Rose: Gothic elegance, silver, midnight mystery. Sterling silver.
- Love Hurts: Romantic vulnerability, rose gold, passionate beauty.

Your workflow:
1. Analyze the imagery request (purpose, collection, pose)
2. Pull collection-specific visual DNA
3. Construct a detailed, brand-accurate image prompt
4. Generate via Gemini image provider (with fallback)
5. Upload to WordPress media library (wordpress-ops pattern)
6. Return generated image metadata

Rules:
- NEVER generate imagery without collection context loaded
- ALWAYS include brand color palette in prompts
- Model must wear/showcase brand assets (jewelry, fashion pieces)
- Oakland roots + luxury fashion aesthetic throughout
- Every image must feel like it belongs on https://skyyrose.co
"""

    def __init__(self, config: Any = None, **kwargs: Any) -> None:
        """Initialize SkyyRose Imagery Agent."""
        from adk.base import ADKProvider as _ADKProvider
        from adk.base import AgentConfig as _AgentConfig

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
        self._gemini: GeminiImageProvider | None = None
        self._provider_factory: ThreeDProviderFactory | None = None
        self._generation_log: list[GeneratedImage] = []

    async def execute(self, prompt: str, **kwargs: Any) -> AgentResult:
        """Execute imagery generation task from a text prompt."""
        collection_name = kwargs.get("collection", "signature")
        purpose = kwargs.get("purpose", "hero_banner")
        request = ImageryRequest(
            purpose=ImageryPurpose(purpose),
            collection=Collection(collection_name),
        )
        image = await self.generate_image(request)
        return AgentResult(
            agent_name="skyyrose_imagery_agent",
            agent_provider=ADKProvider.INTERNAL,
            content=f"Generated {purpose} imagery for {collection_name}",
            structured_output={"image_url": image.url, "image_id": image.image_id},
            status=AgentStatus.COMPLETED if image.url else AgentStatus.FAILED,
        )

    # =========================================================================
    # Initialization & Provider Access
    # =========================================================================

    async def _get_gemini(self) -> GeminiImageProvider:
        """Lazy-initialize Gemini image provider."""
        if not self._gemini:
            self._gemini = GeminiImageProvider()
        return self._gemini

    async def _get_provider_factory(self) -> ThreeDProviderFactory:
        """Lazy-initialize provider factory for fallback."""
        if not self._provider_factory:
            self._provider_factory = get_provider_factory()
            await self._provider_factory.initialize()
        return self._provider_factory

    # =========================================================================
    # Prompt Engineering
    # =========================================================================

    def _build_imagery_prompt(self, request: ImageryRequest) -> str:
        """Build a detailed, brand-accurate image generation prompt.

        Pulls collection DNA, purpose directives, and pose styles
        to construct a prompt that will produce on-brand imagery.

        Args:
            request: Imagery generation request

        Returns:
            Fully constructed image prompt string
        """
        collection_data = COLLECTION_PROMPTS.get(request.collection, {})
        purpose_directive = PURPOSE_DIRECTIVES.get(request.purpose, "")
        pose_directive = POSE_DIRECTIVES.get(request.model_pose, "")

        # Core brand context from injector
        brand_prompt = self.brand_context.get_3d_generation_context(
            product_name=f"{request.collection.value.replace('_', ' ').title()} Collection",
            product_type="fashion imagery",
            collection=request.collection,
        )

        prompt = (
            f"Professional fashion photography for SkyyRose luxury brand. "
            f"\n\n"
            f"BRAND CONTEXT:\n{brand_prompt}"
            f"\n\n"
            f"COLLECTION: {request.collection.value.replace('_', ' ').title()}\n"
            f"Setting: {collection_data.get('setting', '')}\n"
            f"Color Palette: {collection_data.get('palette', '')}\n"
            f"Mood: {collection_data.get('mood', '')}\n"
            f"Accessories & Assets: {collection_data.get('accessories', '')}\n"
            f"\n\n"
            f"PURPOSE: {purpose_directive}\n"
            f"\n"
            f"MODEL: Beautiful, diverse AI model {pose_directive}.\n"
            f"The model is wearing {collection_data.get('accessories', 'brand assets')}.\n"
            f"\n\n"
            f"STYLE REQUIREMENTS:\n"
            f"- High-end fashion editorial quality\n"
            f"- Cinematic lighting and composition\n"
            f"- Brand colors must be present: {collection_data.get('palette', '')}\n"
            f"- Oakland luxury streetwear aesthetic meets high fashion\n"
            f"- Image should feel like it belongs on https://skyyrose.co\n"
            f"- No watermarks, no logos, clean production value\n"
            f"\n\n"
            f"RESOLUTION: High resolution, 1920x1080 or higher aspect ratio appropriate for {request.purpose.value}.\n"
        )

        # Append any brand assets the user specified
        if request.brand_assets:
            prompt += f"\nSPECIFIC BRAND ASSETS TO FEATURE: {', '.join(request.brand_assets)}\n"

        # Additional context
        if request.additional_context:
            prompt += f"\nADDITIONAL DIRECTION: {request.additional_context}\n"

        logger.info(
            f"{self.AGENT_NAME}: Built imagery prompt for {request.collection.value} "
            f"[{request.purpose.value}] len={len(prompt)}"
        )

        return prompt

    # =========================================================================
    # Image Generation
    # =========================================================================

    async def generate_image(self, request: ImageryRequest) -> GeneratedImage:
        """Generate a single brand image.

        Args:
            request: Imagery generation request with collection, purpose, pose

        Returns:
            GeneratedImage with URL, metadata, and prompt used

        Raises:
            Exception: If all providers fail
        """
        logger.info(
            f"{self.AGENT_NAME}: Generating {request.purpose.value} image "
            f"for {request.collection.value} [corr={request.correlation_id}]"
        )

        prompt = self._build_imagery_prompt(request)

        # Primary: Gemini image generation
        try:
            gemini = await self._get_gemini()
            response = await gemini.generate_product_image(
                prompt=prompt,
                product_name=f"SkyyRose {request.collection.value.replace('_', ' ').title()}",
                collection=request.collection.value,
                quality=QualityLevel.PRODUCTION,
            )

            image = GeneratedImage(
                url=response.image_url if hasattr(response, "image_url") else response.model_url,
                purpose=request.purpose,
                collection=request.collection,
                model_pose=request.model_pose,
                prompt_used=prompt,
                provider="gemini",
                correlation_id=request.correlation_id,
            )

            self._generation_log.append(image)
            logger.info(
                f"{self.AGENT_NAME}: Generated image via Gemini [corr={request.correlation_id}]"
            )
            return image

        except Exception as e:
            logger.warning(f"{self.AGENT_NAME}: Gemini failed, trying fallback providers: {e}")

        # Fallback: ThreeDProviderFactory
        try:
            factory = await self._get_provider_factory()
            three_d_request = ThreeDRequest(
                prompt=prompt,
                product_name=f"SkyyRose {request.collection.value.replace('_', ' ').title()}",
                collection=request.collection.value,
                correlation_id=request.correlation_id,
            )
            response = await factory.generate(
                three_d_request, correlation_id=request.correlation_id
            )

            image = GeneratedImage(
                url=response.thumbnail_url or response.model_url or "",
                purpose=request.purpose,
                collection=request.collection,
                model_pose=request.model_pose,
                prompt_used=prompt,
                provider=response.provider,
                correlation_id=request.correlation_id,
            )

            self._generation_log.append(image)
            logger.info(
                f"{self.AGENT_NAME}: Generated image via fallback [corr={request.correlation_id}]"
            )
            return image

        except Exception as e:
            logger.error(
                f"{self.AGENT_NAME}: All providers failed [corr={request.correlation_id}]: {e}"
            )
            raise

    async def generate_batch(
        self,
        requests: list[ImageryRequest],
    ) -> ImageryBatch:
        """Generate a batch of brand images.

        Useful for rolling out a full collection theme with all
        necessary imagery assets.

        Args:
            requests: List of imagery requests

        Returns:
            ImageryBatch with all results and any errors
        """
        batch = ImageryBatch()
        logger.info(
            f"{self.AGENT_NAME}: Starting batch of {len(requests)} images [batch={batch.batch_id}]"
        )

        for request in requests:
            try:
                image = await self.generate_image(request)
                batch.images.append(image)
            except Exception as e:
                batch.errors.append(f"[{request.collection.value}/{request.purpose.value}] {e}")
                logger.warning(f"{self.AGENT_NAME}: Batch item failed: {e}")

        batch.completed_at = datetime.now(UTC)
        logger.info(
            f"{self.AGENT_NAME}: Batch complete. "
            f"Success: {len(batch.images)}, Errors: {len(batch.errors)}"
        )
        return batch

    # =========================================================================
    # WordPress Media Upload (wordpress-ops integration)
    # =========================================================================

    async def upload_to_wordpress(
        self,
        image: GeneratedImage,
        wp_client: Any,
    ) -> GeneratedImage:
        """Upload generated image to WordPress media library.

        Follows wordpress-ops patterns:
        - Downloads image from generation URL
        - Uploads with brand-appropriate alt text and title
        - Tags with collection metadata

        Args:
            image: Generated image to upload
            wp_client: WordPressComClient instance

        Returns:
            Updated GeneratedImage with wp_media_id
        """
        import os
        import tempfile

        import httpx

        logger.info(
            f"{self.AGENT_NAME}: Uploading {image.purpose.value} to WordPress "
            f"[{image.collection.value}]"
        )

        try:
            # Download generated image
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.get(image.url)
                resp.raise_for_status()
                image_data = resp.content
                content_type = resp.headers.get("content-type", "image/jpeg")

            # Determine extension
            ext_map = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}
            ext = ext_map.get(content_type, "jpg")

            # Build descriptive filename and alt text
            collection_name = image.collection.value.replace("_", " ").title()
            purpose_name = image.purpose.value.replace("_", " ").title()
            title = f"SkyyRose {collection_name} {purpose_name}"
            alt_text = (
                f"SkyyRose {collection_name} collection {purpose_name.lower()} — "
                f"luxury fashion editorial photography"
            )
            slug = f"skyyrose-{image.collection.value}-{image.purpose.value}"
            filename = f"{slug}.{ext}"

            # Write to temp file for upload
            tmp_path = os.path.join(tempfile.gettempdir(), filename)
            with open(tmp_path, "wb") as f:
                f.write(image_data)

            # Upload via wordpress-ops pattern
            media_response = await wp_client.upload_media(
                file_path=tmp_path,
                title=title,
                alt_text=alt_text,
            )

            # Cleanup temp file
            os.unlink(tmp_path)

            # Update image record
            image.wp_media_id = media_response.get("id")
            image.uploaded_at = datetime.now(UTC)
            image.metadata["wp_media"] = media_response

            logger.info(f"{self.AGENT_NAME}: Uploaded to WP media ID {image.wp_media_id}")

            return image

        except Exception as e:
            logger.error(f"{self.AGENT_NAME}: WordPress upload failed: {e}")
            raise

    # =========================================================================
    # Theme-Ready Generation
    # =========================================================================

    async def generate_theme_assets(
        self,
        collections: list[Collection] | None = None,
    ) -> ImageryBatch:
        """Generate a complete set of imagery for the WordPress theme.

        Creates the full suite of images needed per collection:
        - Hero banner
        - Collection showcase
        - Product model shots
        - Lifestyle imagery
        - Campaign hero

        Args:
            collections: Collections to generate for. Defaults to all.

        Returns:
            ImageryBatch with all theme assets
        """
        if not collections:
            collections = [Collection.SIGNATURE, Collection.BLACK_ROSE, Collection.LOVE_HURTS]

        requests: list[ImageryRequest] = []

        for collection in collections:
            # Hero banner for collection page
            requests.append(
                ImageryRequest(
                    purpose=ImageryPurpose.HERO_BANNER,
                    collection=collection,
                    model_pose=ModelPose.EDITORIAL,
                )
            )
            # Collection showcase
            requests.append(
                ImageryRequest(
                    purpose=ImageryPurpose.COLLECTION_SHOWCASE,
                    collection=collection,
                    model_pose=ModelPose.RUNWAY,
                )
            )
            # Product model shot
            requests.append(
                ImageryRequest(
                    purpose=ImageryPurpose.PRODUCT_MODEL,
                    collection=collection,
                    model_pose=ModelPose.CASUAL_ELEGANT,
                )
            )
            # Lifestyle
            requests.append(
                ImageryRequest(
                    purpose=ImageryPurpose.LIFESTYLE,
                    collection=collection,
                    model_pose=ModelPose.CASUAL_ELEGANT,
                )
            )
            # Campaign hero
            requests.append(
                ImageryRequest(
                    purpose=ImageryPurpose.CAMPAIGN,
                    collection=collection,
                    model_pose=ModelPose.DRAMATIC,
                )
            )

        logger.info(
            f"{self.AGENT_NAME}: Generating {len(requests)} theme assets "
            f"for {len(collections)} collections"
        )

        return await self.generate_batch(requests)

    # =========================================================================
    # Generation Log
    # =========================================================================

    def get_generation_log(self) -> list[GeneratedImage]:
        """Get full generation history for this session."""
        return list(self._generation_log)

    def get_log_by_collection(self, collection: Collection) -> list[GeneratedImage]:
        """Get generation log filtered by collection."""
        return [img for img in self._generation_log if img.collection == collection]
