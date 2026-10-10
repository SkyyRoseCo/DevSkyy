# api/v1/descriptions.py
"""API endpoints for image-to-description pipeline.

Implements US-029: Image-to-description pipeline.

Author: DevSkyy Platform Team
Version: 1.0.0
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from services.ml.image_description_pipeline import (
    ImageDescriptionPipeline,
    VisionModelClient,
)
from services.ml.schemas.description import (
    BatchDescriptionOutput,
    BatchDescriptionRequest,
    DescriptionOutput,
    DescriptionRequest,
    DescriptionStyle,
    ExtractedFeatures,
    FeatureExtractionRequest,
    ProductType,
    VisionModel,
)

from security.jwt_oauth2_auth import TokenPayload, get_current_user
from security.ssrf_protection import ssrf_protection

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/descriptions", tags=["descriptions"])


# =============================================================================
# Dependency Injection
# =============================================================================


def get_vision_client() -> VisionModelClient:
    """Get vision model client."""
    return VisionModelClient()


def get_pipeline(
    vision_client: VisionModelClient = Depends(get_vision_client),
) -> ImageDescriptionPipeline:
    """Get description pipeline."""
    return ImageDescriptionPipeline(vision_client=vision_client)


# =============================================================================
# Request/Response Models
# =============================================================================


class QuickDescriptionRequest(DescriptionRequest):
    """Simplified request for quick description generation."""

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "image_url": "https://example.com/product.jpg",
                "product_name": "Black Rose Midi Dress",
                "product_type": "apparel",
                "style": "luxury",
                "target_word_count": 150,
            }
        }


class BatchStatusResponse(BatchDescriptionOutput):
    """Batch job status response."""

    webhook_sent: bool = False
    webhook_url: str | None = None


# =============================================================================
# Endpoints
# =============================================================================


@router.post("/generate", response_model=DescriptionOutput)
async def generate_description(
    request: DescriptionRequest,
    pipeline: ImageDescriptionPipeline = Depends(get_pipeline),
    current_user: TokenPayload = Depends(get_current_user),
) -> DescriptionOutput:
    """Generate product description from image.

    Analyzes the image and generates:
    - Full product description (100-200 words)
    - Short description (< 50 words)
    - Bullet points (5-7)
    - SEO content (title, meta description, keywords)
    - Suggested tags (10-15)
    - Extracted visual features (colors, materials, style)
    """
    try:
        logger.info(
            f"Generating description for {request.image_url} "
            f"(user: {current_user.sub}, style: {request.style})"
        )

        result = await pipeline.generate_description(request)

        logger.info(
            f"Generated description: {result.word_count} words in {result.processing_time_ms}ms"
        )

        return result

    except Exception as e:
        logger.error(f"Description generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/quick", response_model=DescriptionOutput)
async def generate_quick_description(
    image_url: str = Query(..., description="URL of image to analyze"),
    product_type: ProductType = Query(ProductType.APPAREL),
    style: DescriptionStyle = Query(DescriptionStyle.LUXURY),
    pipeline: ImageDescriptionPipeline = Depends(get_pipeline),
    current_user: TokenPayload = Depends(get_current_user),
) -> DescriptionOutput:
    """Quick description generation with minimal parameters.

    Simplified endpoint using Gemini Flash (no rate limiting issues).
    """
    request = DescriptionRequest(
        image_url=image_url,
        product_type=product_type,
        style=style,
        model=VisionModel.GEMINI_FLASH,  # Use Gemini (no rate limits)
        target_word_count=100,  # Shorter target
    )

    return await generate_description(request, pipeline, current_user)


@router.post("/generate/batch", response_model=BatchStatusResponse)
async def generate_batch_descriptions(
    request: BatchDescriptionRequest,
    background_tasks: BackgroundTasks,
    pipeline: ImageDescriptionPipeline = Depends(get_pipeline),
    current_user: TokenPayload = Depends(get_current_user),
) -> BatchStatusResponse:
    """Generate descriptions for multiple images.

    Processes up to 50 images in a single request.
    If callback_url is provided, sends results via webhook when complete.
    """
    try:
        logger.info(
            f"Starting batch description: {len(request.requests)} images (user: {current_user.sub})"
        )

        # Process batch
        result = await pipeline.generate_batch(request, max_concurrent=5)

        # Send webhook if configured
        webhook_sent = False
        if request.callback_url:
            background_tasks.add_task(
                _send_webhook,
                request.callback_url,
                result.model_dump(),
            )
            webhook_sent = True

        return BatchStatusResponse(
            **result.model_dump(),
            webhook_sent=webhook_sent,
            webhook_url=request.callback_url,
        )

    except Exception as e:
        logger.error(f"Batch description failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/extract-features", response_model=ExtractedFeatures)
async def extract_features(
    request: FeatureExtractionRequest,
    pipeline: ImageDescriptionPipeline = Depends(get_pipeline),
    current_user: TokenPayload = Depends(get_current_user),
) -> ExtractedFeatures:
    """Extract visual features from image without generating description.

    Returns:
    - Colors (name, hex, category, prominence)
    - Materials (name, texture, quality indicator)
    - Style attributes (aesthetic, mood, occasion, season)
    - Detected elements
    """
    try:
        logger.info(f"Extracting features from {request.image_url}")

        result = await pipeline.extract_features(request)

        return result

    except Exception as e:
        logger.error(f"Feature extraction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/models", response_model=list[dict[str, Any]])
async def list_models(
    current_user: TokenPayload = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """List available vision models.

    Returns available models with their characteristics.
    Gemini models recommended (no rate limiting issues).
    """
    return [
        # Gemini models (RECOMMENDED)
        {
            "id": VisionModel.GEMINI_PRO.value,
            "name": "Gemini Pro 2.5",
            "description": "Most capable, best quality analysis (RECOMMENDED)",
            "provider": "google",
            "speed": "medium",
            "quality": "highest",
            "rate_limited": False,
            "recommended_for": ["full descriptions", "luxury content", "detailed analysis"],
        },
        {
            "id": VisionModel.GEMINI_FLASH.value,
            "name": "Gemini Flash 2.5",
            "description": "Fast and reliable, excellent quality (RECOMMENDED)",
            "provider": "google",
            "speed": "fast",
            "quality": "high",
            "rate_limited": False,
            "recommended_for": ["quick descriptions", "batch processing", "high volume"],
        },
        # Replicate models (may have rate limits)
        {
            "id": VisionModel.LLAVA_34B.value,
            "name": "LLaVA 34B",
            "description": "High quality (Replicate - may have rate limits)",
            "provider": "replicate",
            "speed": "slow",
            "quality": "highest",
            "rate_limited": True,
            "recommended_for": ["full descriptions", "luxury content"],
        },
        {
            "id": VisionModel.LLAVA_13B.value,
            "name": "LLaVA 13B",
            "description": "Good balance (Replicate - may have rate limits)",
            "provider": "replicate",
            "speed": "medium",
            "quality": "high",
            "rate_limited": True,
            "recommended_for": ["quick descriptions", "feature extraction"],
        },
        {
            "id": VisionModel.BLIP2.value,
            "name": "BLIP-2",
            "description": "Fast fallback (Replicate - may have rate limits)",
            "provider": "replicate",
            "speed": "fast",
            "quality": "good",
            "rate_limited": True,
            "recommended_for": ["fallback", "basic captions"],
        },
    ]


@router.get("/styles", response_model=list[dict[str, Any]])
async def list_styles(
    current_user: TokenPayload = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """List available description styles.

    Returns available writing styles with examples.
    """
    return [
        {
            "id": DescriptionStyle.LUXURY.value,
            "name": "Luxury",
            "description": "Sophisticated, evocative language for high-end fashion",
            "brand_voice": "SkyyRose",
            "example_tone": "Crafted with precision, this piece embodies effortless elegance...",
        },
        {
            "id": DescriptionStyle.CASUAL.value,
            "name": "Casual",
            "description": "Friendly, approachable language for everyday wear",
            "example_tone": "Your new go-to piece that works with everything in your closet...",
        },
        {
            "id": DescriptionStyle.TECHNICAL.value,
            "name": "Technical",
            "description": "Detailed specifications and construction information",
            "example_tone": "Constructed from 100% organic cotton with reinforced stitching...",
        },
        {
            "id": DescriptionStyle.MINIMAL.value,
            "name": "Minimal",
            "description": "Clean, essential descriptions with no fluff",
            "example_tone": "Black silk midi. Relaxed fit. Hidden zip.",
        },
        {
            "id": DescriptionStyle.STORYTELLING.value,
            "name": "Storytelling",
            "description": "Narrative-driven descriptions that create emotional connection",
            "example_tone": "She walks into the room and everything stops...",
        },
    ]


@router.get("/health")
async def health_check(
    vision_client: VisionModelClient = Depends(get_vision_client),
) -> dict[str, Any]:
    """Check health of description service.

    Returns status of vision models and service availability.
    Prioritizes Gemini models (recommended, no rate limits).
    """
    # Check Gemini models (primary - no rate limits)
    gemini_flash_ok = await vision_client.health_check(VisionModel.GEMINI_FLASH)
    gemini_pro_ok = await vision_client.health_check(VisionModel.GEMINI_PRO)

    # Check Replicate models (fallback)
    llava_ok = await vision_client.health_check(VisionModel.LLAVA_34B)

    # Service is healthy if Gemini is available
    is_healthy = gemini_flash_ok or gemini_pro_ok or llava_ok

    return {
        "status": "healthy" if is_healthy else "degraded",
        "recommended_provider": "gemini" if (gemini_flash_ok or gemini_pro_ok) else "replicate",
        "models": {
            # Gemini (recommended)
            "gemini_flash": "available" if gemini_flash_ok else "unavailable",
            "gemini_pro": "available" if gemini_pro_ok else "unavailable",
            # Replicate (may be rate limited)
            "llava_34b": "available" if llava_ok else "unavailable",
        },
        "service": "descriptions",
        "version": "1.1.0",  # Updated with Gemini support
    }


# =============================================================================
# Helper Functions
# =============================================================================


async def _send_webhook(url: str, data: dict[str, Any]) -> None:
    """Send webhook notification.

    Args:
        url: Webhook URL
        data: Data to send
    """
    try:
        response = await ssrf_protection.safe_request(
            "POST",
            url,
            json=data,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        logger.info(f"Webhook sent to {url}: {response.status_code}")
    except Exception as e:
        logger.error(f"Webhook failed: {e}")
