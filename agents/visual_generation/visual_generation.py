"""
Visual Generation Module
========================

Unified visual generation using Google and HuggingFace APIs.

Providers:
- Google Imagen 3: Text-to-image generation
- Google Veo 2: Text-to-video generation
- HuggingFace FLUX.1: High-quality image generation
- Tripo3D: 3D model generation (existing)
- FASHN: Virtual try-on (existing)

CRITICAL RULE: Google + HuggingFace handle ALL imagery/video/AI model
generation with SkyyRose brand assets - NO EXCEPTIONS.

Author: DevSkyy Platform Team
Version: 1.0.0
"""

from __future__ import annotations

import asyncio
import base64
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

import aiohttp

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================


class VisualProvider(StrEnum):
    """Visual generation providers"""

    GOOGLE_IMAGEN = "google_imagen"
    GOOGLE_VEO = "google_veo"
    HUGGINGFACE_FLUX = "huggingface_flux"
    HUGGINGFACE_SD = "huggingface_sd"  # Stable Diffusion
    REPLICATE_LORA = "replicate_lora"  # SkyyRose custom LoRA (exact products)
    TRIPO3D = "tripo3d"
    FASHN = "fashn"


class GenerationType(StrEnum):
    """Type of visual generation"""

    IMAGE_FROM_TEXT = "image_from_text"
    IMAGE_FROM_IMAGE = "image_from_image"
    VIDEO_FROM_TEXT = "video_from_text"
    VIDEO_FROM_IMAGE = "video_from_image"
    MODEL_3D = "model_3d"
    VIRTUAL_TRYON = "virtual_tryon"
    EXACT_PRODUCT = "exact_product"  # LoRA-based exact product generation


class AspectRatio(StrEnum):
    """Supported aspect ratios"""

    SQUARE = "1:1"
    PORTRAIT = "9:16"
    LANDSCAPE = "16:9"
    WIDE = "21:9"
    STANDARD = "4:3"


class ImageQuality(StrEnum):
    """Image quality levels"""

    DRAFT = "draft"
    STANDARD = "standard"
    HIGH = "high"
    ULTRA = "ultra"


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class GenerationRequest:
    """Request for visual generation"""

    id: str = field(default_factory=lambda: str(uuid4())[:16])
    prompt: str = ""
    negative_prompt: str = ""
    provider: VisualProvider = VisualProvider.GOOGLE_IMAGEN
    generation_type: GenerationType = GenerationType.IMAGE_FROM_TEXT
    aspect_ratio: AspectRatio = AspectRatio.SQUARE
    quality: ImageQuality = ImageQuality.STANDARD
    width: int = 1024
    height: int = 1024
    num_outputs: int = 1
    guidance_scale: float = 7.5
    num_inference_steps: int = 50
    seed: int | None = None
    style_preset: str | None = None
    input_image_url: str | None = None
    input_video_url: str | None = None
    duration_seconds: int = 5
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class GenerationResult:
    """Result from visual generation"""

    id: str
    request_id: str
    provider: VisualProvider
    success: bool
    output_url: str | None = None
    output_urls: list[str] = field(default_factory=list)
    output_base64: str | None = None
    content_type: str = "image/png"
    width: int = 0
    height: int = 0
    duration_seconds: float = 0.0
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    error: str | None = None
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# Brand DNA for Prompt Enhancement
# =============================================================================


SKYYROSE_BRAND_DNA = {
    "name": "SkyyRose",
    "location": "Oakland, California",
    "aesthetic": "luxury streetwear",
    "colors": {
        "primary": "#B76E79",  # Rose gold
        "secondary": "#1A1A1A",  # Obsidian black
        "accent": "#FFFFFF",  # White/ivory
        "metallic": "#D4AF37",  # Gold accent
    },
    "style_keywords": [
        "premium",
        "sophisticated",
        "bold",
        "elegant",
        "luxury",
        "refined",
        "exclusive",
        "rose gold",
        "modern",
        "editorial",
        "high-fashion",
    ],
    "avoid_keywords": [
        "cheap",
        "basic",
        "generic",
        "low-quality",
        "budget",
        "discount",
        "mass-produced",
    ],
    "collections": {
        "BLACK ROSE": "dark elegance, mysterious, limited edition",
        "LOVE HURTS": "emotional expression, bold statements, heart motifs",
        "SIGNATURE": "timeless essentials, foundation wardrobe",
    },
}


# =============================================================================
# Provider Clients
# =============================================================================


class GoogleImagenClient:
    """
    Google Imagen 3 API client.

    Requires GOOGLE_API_KEY or VERTEX_AI credentials.
    """

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.warning("Google API key not configured")

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate image using Imagen 3"""
        start_time = time.time()
        result_id = str(uuid4())[:16]

        if not self.api_key:
            return GenerationResult(
                id=result_id,
                request_id=request.id,
                provider=VisualProvider.GOOGLE_IMAGEN,
                success=False,
                error="Google API key not configured",
            )

        try:
            # Enhance prompt with brand DNA
            enhanced_prompt = self._enhance_prompt(request.prompt)

            # Build request payload
            payload = {
                "prompt": enhanced_prompt,
                "negativePrompt": request.negative_prompt or self._default_negative_prompt(),
                "numberOfImages": request.num_outputs,
                "aspectRatio": request.aspect_ratio.value,
                "personGeneration": "allow_adult",
                "safetyFilterLevel": "block_low_and_above",
            }

            # Make API request
            url = f"{self.BASE_URL}/models/imagen-3.0-generate-001:generateImage"
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key,
            }

            async with (
                aiohttp.ClientSession() as session,
                session.post(url, json=payload, headers=headers) as response,
            ):
                if response.status != 200:
                    error_text = await response.text()
                    return GenerationResult(
                        id=result_id,
                        request_id=request.id,
                        provider=VisualProvider.GOOGLE_IMAGEN,
                        success=False,
                        error=f"API error {response.status}: {error_text[:200]}",
                    )

                data = await response.json()

            # Parse response
            images = data.get("images", [])
            output_urls = []

            for img in images:
                if "bytesBase64Encoded" in img:
                    # Store base64 or convert to URL
                    output_urls.append(
                        f"data:image/png;base64,{img['bytesBase64Encoded'][:100]}..."
                    )

            latency = (time.time() - start_time) * 1000

            return GenerationResult(
                id=result_id,
                request_id=request.id,
                provider=VisualProvider.GOOGLE_IMAGEN,
                success=True,
                output_urls=output_urls,
                output_base64=images[0].get("bytesBase64Encoded") if images else None,
                width=request.width,
                height=request.height,
                latency_ms=latency,
                cost_usd=0.04 * request.num_outputs,  # Estimated cost
                metadata={"enhanced_prompt": enhanced_prompt},
            )

        except Exception as e:
            logger.error(f"Google Imagen error: {e}")
            return GenerationResult(
                id=result_id,
                request_id=request.id,
                provider=VisualProvider.GOOGLE_IMAGEN,
                success=False,
                error=str(e),
                latency_ms=(time.time() - start_time) * 1000,
            )

    def _enhance_prompt(self, prompt: str) -> str:
        """Enhance prompt with SkyyRose brand DNA"""
        brand_context = """
        Style: luxury streetwear, premium quality, editorial photography
        Colors: rose gold accents (#B76E79), black foundation (#1A1A1A), white highlights
        Aesthetic: sophisticated, bold, elegant, high-fashion
        Brand: SkyyRose
        """
        return f"{prompt}. {brand_context}"

    def _default_negative_prompt(self) -> str:
        """Default negative prompt for brand consistency"""
        return ", ".join(
            [
                "low quality",
                "blurry",
                "pixelated",
                "cheap looking",
                "amateur",
                "distorted",
                "watermark",
                "text",
                "logo",
                "ugly",
                "deformed",
                "noisy",
                "grainy",
            ]
        )


class GoogleVeoClient:
    """
    Google Veo 2 API client for video generation.

    Requires GOOGLE_API_KEY or VERTEX_AI credentials.
    """

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate video using Veo 2"""
        start_time = time.time()
        result_id = str(uuid4())[:16]

        if not self.api_key:
            return GenerationResult(
                id=result_id,
                request_id=request.id,
                provider=VisualProvider.GOOGLE_VEO,
                success=False,
                error="Google API key not configured",
            )

        try:
            # Enhance prompt
            enhanced_prompt = self._enhance_video_prompt(request.prompt)

            payload = {
                "prompt": enhanced_prompt,
                "aspectRatio": request.aspect_ratio.value,
                "durationSeconds": request.duration_seconds,
            }

            url = f"{self.BASE_URL}/models/veo-002:generateVideo"
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key,
            }

            async with (
                aiohttp.ClientSession() as session,
                session.post(url, json=payload, headers=headers) as response,
            ):
                if response.status != 200:
                    error_text = await response.text()
                    return GenerationResult(
                        id=result_id,
                        request_id=request.id,
                        provider=VisualProvider.GOOGLE_VEO,
                        success=False,
                        error=f"API error {response.status}: {error_text[:200]}",
                    )

                data = await response.json()

            # Handle async operation
            operation_name = data.get("name")
            if operation_name:
                # Poll for completion
                video_url = await self._poll_operation(operation_name)
            else:
                video_url = data.get("video", {}).get("uri")

            latency = (time.time() - start_time) * 1000

            return GenerationResult(
                id=result_id,
                request_id=request.id,
                provider=VisualProvider.GOOGLE_VEO,
                success=True,
                output_url=video_url,
                content_type="video/mp4",
                duration_seconds=request.duration_seconds,
                latency_ms=latency,
                cost_usd=0.10 * request.duration_seconds,  # Estimated
                metadata={"enhanced_prompt": enhanced_prompt},
            )

        except Exception as e:
            logger.error(f"Google Veo error: {e}")
            return GenerationResult(
                id=result_id,
                request_id=request.id,
                provider=VisualProvider.GOOGLE_VEO,
                success=False,
                error=str(e),
                latency_ms=(time.time() - start_time) * 1000,
            )

    async def _poll_operation(self, operation_name: str, timeout: int = 120) -> str | None:
        """Poll for async operation completion"""
        url = f"{self.BASE_URL}/{operation_name}"
        headers = {"x-goog-api-key": self.api_key}

        start = time.time()
        async with aiohttp.ClientSession() as session:
            while time.time() - start < timeout:
                async with session.get(url, headers=headers) as response:
                    data = await response.json()

                    if data.get("done"):
                        return data.get("response", {}).get("video", {}).get("uri")

                await asyncio.sleep(5)

        return None

    def _enhance_video_prompt(self, prompt: str) -> str:
        """Enhance video prompt with brand context"""
        return f"""
        {prompt}

        Style: Luxury streetwear brand video, editorial quality
        Movement: Smooth camera movements, professional cinematography
        Lighting: High-end fashion lighting, dramatic shadows
        Brand: SkyyRose - premium streetwear
        Colors: Rose gold, black, white accents
        Quality: 4K, cinematic, professional
        """


class HuggingFaceFluxClient:
    """
    HuggingFace FLUX.1 API client.

    Uses HuggingFace Inference API for FLUX.1 models.
    """

    BASE_URL = "https://api-inference.huggingface.co/models"
    MODEL = "black-forest-labs/FLUX.1-schnell"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate image using FLUX.1"""
        start_time = time.time()
        result_id = str(uuid4())[:16]

        if not self.api_key:
            return GenerationResult(
                id=result_id,
                request_id=request.id,
                provider=VisualProvider.HUGGINGFACE_FLUX,
                success=False,
                error="HuggingFace API key not configured",
            )

        try:
            # Enhance prompt
            enhanced_prompt = self._enhance_prompt(request.prompt)

            payload = {
                "inputs": enhanced_prompt,
                "parameters": {
                    "width": request.width,
                    "height": request.height,
                    "guidance_scale": request.guidance_scale,
                    "num_inference_steps": request.num_inference_steps,
                },
            }

            if request.seed:
                payload["parameters"]["seed"] = request.seed

            if request.negative_prompt:
                payload["parameters"]["negative_prompt"] = request.negative_prompt

            url = f"{self.BASE_URL}/{self.MODEL}"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            async with (
                aiohttp.ClientSession() as session,
                session.post(url, json=payload, headers=headers) as response,
            ):
                if response.status != 200:
                    error_text = await response.text()
                    return GenerationResult(
                        id=result_id,
                        request_id=request.id,
                        provider=VisualProvider.HUGGINGFACE_FLUX,
                        success=False,
                        error=f"API error {response.status}: {error_text[:200]}",
                    )

                # Response is binary image data
                image_data = await response.read()
                image_base64 = base64.b64encode(image_data).decode()

            latency = (time.time() - start_time) * 1000

            return GenerationResult(
                id=result_id,
                request_id=request.id,
                provider=VisualProvider.HUGGINGFACE_FLUX,
                success=True,
                output_base64=image_base64,
                content_type="image/png",
                width=request.width,
                height=request.height,
                latency_ms=latency,
                cost_usd=0.01,  # HF inference costs
                metadata={"enhanced_prompt": enhanced_prompt, "model": self.MODEL},
            )

        except Exception as e:
            logger.error(f"HuggingFace FLUX error: {e}")
            return GenerationResult(
                id=result_id,
                request_id=request.id,
                provider=VisualProvider.HUGGINGFACE_FLUX,
                success=False,
                error=str(e),
                latency_ms=(time.time() - start_time) * 1000,
            )

    def _enhance_prompt(self, prompt: str) -> str:
        """Enhance prompt for FLUX.1"""
        style = ", ".join(SKYYROSE_BRAND_DNA["style_keywords"][:5])
        return f"{prompt}, {style}, high quality, professional photography"


class ReplicateLoRAClient:
    """
    Replicate LoRA client for exact SkyyRose product generation.

    Uses custom-trained LoRA (v3) on 390 exact product images.
    Model: devskyy/skyyrose-lora-v3
    Trigger word: skyyrose
    """

    MODEL_ID = "devskyy/skyyrose-lora-v3"
    MODEL_VERSION = "64dbb859fed83670e7cde81fc161c183bd9d0607fb7028b01bfc0a000ec114b4"  # pragma: allowlist secret
    TRIGGER_WORD = "skyyrose"
    API_BASE = "https://api.replicate.com/v1"

    # Collection style mappings
    COLLECTION_STYLES = {
        "SIGNATURE": {
            "style": "signature collection, lavender rose, classic elegant, timeless",
            "colors": "lavender, rose gold, soft pastels, cream white",
        },
        "BLACK_ROSE": {
            "style": "black_rose collection, dark elegance, gothic luxury, midnight",
            "colors": "obsidian black, deep burgundy, silver accents",
        },
        "LOVE_HURTS": {
            "style": "love_hurts collection, bold red, emotional expression, urban",
            "colors": "vivid red, black contrast, white accents",
        },
    }

    def __init__(self, api_token: str | None = None):
        self.api_token = api_token or os.getenv("REPLICATE_API_TOKEN")
        if not self.api_token:
            logger.warning("REPLICATE_API_TOKEN not configured for LoRA")

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate exact product image using trained LoRA."""
        start_time = time.time()
        result_id = str(uuid4())[:16]

        if not self.api_token:
            return GenerationResult(
                id=result_id,
                request_id=request.id,
                provider=VisualProvider.REPLICATE_LORA,
                success=False,
                error="REPLICATE_API_TOKEN not configured",
            )

        try:
            import httpx

            # Extract collection from metadata or default
            collection = request.metadata.get("collection", "SIGNATURE").upper()
            garment_type = request.metadata.get("garment_type", "")

            # Build enhanced prompt with LoRA trigger word
            enhanced_prompt = self._build_prompt(request.prompt, collection, garment_type)

            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
            }

            input_params = {
                "prompt": enhanced_prompt,
                "num_outputs": min(request.num_outputs, 4),
                "guidance_scale": request.guidance_scale or 3.5,
                "num_inference_steps": request.num_inference_steps or 28,
                "output_format": "webp",
                "output_quality": 90,
                "disable_safety_checker": False,
            }

            if request.seed is not None:
                input_params["seed"] = request.seed

            # Create prediction
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.API_BASE}/predictions",
                    headers=headers,
                    json={
                        "version": self.MODEL_VERSION,
                        "input": input_params,
                    },
                )

                if response.status_code not in (200, 201):
                    return GenerationResult(
                        id=result_id,
                        request_id=request.id,
                        provider=VisualProvider.REPLICATE_LORA,
                        success=False,
                        error=f"API error {response.status_code}: {response.text[:200]}",
                        latency_ms=(time.time() - start_time) * 1000,
                    )

                prediction = response.json()
                pred_id = prediction.get("id")

                # Poll for completion
                status = prediction.get("status")
                while status in ("starting", "processing"):
                    await asyncio.sleep(2)

                    poll_response = await client.get(
                        f"{self.API_BASE}/predictions/{pred_id}",
                        headers=headers,
                    )
                    if poll_response.status_code == 200:
                        prediction = poll_response.json()
                        status = prediction.get("status")

                if status == "succeeded":
                    output = prediction.get("output", [])
                    output_urls = list(output) if isinstance(output, list) else [output]

                    latency_ms = (time.time() - start_time) * 1000
                    cost_usd = 0.003 * request.num_outputs  # Estimated Flux LoRA cost

                    return GenerationResult(
                        id=result_id,
                        request_id=request.id,
                        provider=VisualProvider.REPLICATE_LORA,
                        success=True,
                        output_urls=output_urls,
                        output_url=output_urls[0] if output_urls else None,
                        content_type="image/webp",
                        width=request.width,
                        height=request.height,
                        latency_ms=latency_ms,
                        cost_usd=cost_usd,
                        metadata={
                            "prediction_id": pred_id,
                            "model": f"{self.MODEL_ID}:{self.MODEL_VERSION[:12]}",
                            "enhanced_prompt": enhanced_prompt,
                            "collection": collection,
                            "garment_type": garment_type,
                        },
                    )
                else:
                    return GenerationResult(
                        id=result_id,
                        request_id=request.id,
                        provider=VisualProvider.REPLICATE_LORA,
                        success=False,
                        error=prediction.get("error") or f"Generation failed: {status}",
                        latency_ms=(time.time() - start_time) * 1000,
                    )

        except Exception as e:
            logger.exception(f"Replicate LoRA error: {e}")
            return GenerationResult(
                id=result_id,
                request_id=request.id,
                provider=VisualProvider.REPLICATE_LORA,
                success=False,
                error=str(e),
                latency_ms=(time.time() - start_time) * 1000,
            )

    def _build_prompt(self, prompt: str, collection: str, garment_type: str = "") -> str:
        """Build enhanced prompt with brand DNA and trigger word."""
        parts = [self.TRIGGER_WORD]

        # Add collection style
        collection_data = self.COLLECTION_STYLES.get(
            collection, self.COLLECTION_STYLES["SIGNATURE"]
        )
        parts.append(collection_data["style"])

        # Add garment description if specified
        if garment_type:
            parts.append(garment_type)

        # Add user prompt
        parts.append(prompt)

        # Add quality keywords
        parts.extend(
            [
                "luxury streetwear",
                "product photography",
                "studio lighting",
                "white background",
                "high quality",
                "professional photo",
            ]
        )

        return ", ".join(parts)


# =============================================================================
# Visual Generation Router
# =============================================================================


class VisualGenerationRouter:
    """
    Routes visual generation tasks to appropriate providers.

    CRITICAL: Google + HuggingFace handle ALL imagery/video generation.

    Routing Logic:
    - Image from text: Google Imagen (primary), FLUX.1 (secondary)
    - Video from text: Google Veo (exclusive)
    - 3D models: Tripo3D (existing)
    - Virtual try-on: FASHN (existing)
    """

    # Provider routing configuration
    ROUTING = {
        GenerationType.IMAGE_FROM_TEXT: [
            VisualProvider.GOOGLE_IMAGEN,
            VisualProvider.HUGGINGFACE_FLUX,
            VisualProvider.REPLICATE_LORA,  # Fallback for brand-specific
        ],
        GenerationType.IMAGE_FROM_IMAGE: [
            VisualProvider.GOOGLE_IMAGEN,
            VisualProvider.HUGGINGFACE_FLUX,
        ],
        GenerationType.VIDEO_FROM_TEXT: [
            VisualProvider.GOOGLE_VEO,
        ],
        GenerationType.VIDEO_FROM_IMAGE: [
            VisualProvider.GOOGLE_VEO,
        ],
        GenerationType.MODEL_3D: [
            VisualProvider.TRIPO3D,
        ],
        GenerationType.VIRTUAL_TRYON: [
            VisualProvider.FASHN,
        ],
        GenerationType.EXACT_PRODUCT: [
            VisualProvider.REPLICATE_LORA,  # Primary: exact product match
            VisualProvider.GOOGLE_IMAGEN,  # Fallback: generic generation
        ],
    }

    def __init__(self):
        self._clients: dict[VisualProvider, Any] = {}
        self._history: list[GenerationResult] = []

    async def initialize(self):
        """Initialize provider clients"""
        # Initialize Google clients
        self._clients[VisualProvider.GOOGLE_IMAGEN] = GoogleImagenClient()
        self._clients[VisualProvider.GOOGLE_VEO] = GoogleVeoClient()

        # Initialize HuggingFace client
        self._clients[VisualProvider.HUGGINGFACE_FLUX] = HuggingFaceFluxClient()

        # Initialize Replicate LoRA client (exact product generation)
        self._clients[VisualProvider.REPLICATE_LORA] = ReplicateLoRAClient()

        logger.info("Visual generation router initialized with LoRA support")

    def get_providers_for_type(self, generation_type: GenerationType) -> list[VisualProvider]:
        """Get available providers for a generation type"""
        return self.ROUTING.get(generation_type, [VisualProvider.GOOGLE_IMAGEN])

    async def generate(
        self,
        request: GenerationRequest,
        provider: VisualProvider | None = None,
        fallback: bool = True,
    ) -> GenerationResult:
        """
        Generate visual content.

        Args:
            request: Generation request
            provider: Specific provider (auto-selected if None)
            fallback: Whether to try fallback providers on failure

        Returns:
            GenerationResult
        """
        # Auto-select provider if not specified
        if provider is None:
            providers = self.get_providers_for_type(request.generation_type)
            provider = providers[0] if providers else VisualProvider.GOOGLE_IMAGEN

        # Get client
        client = self._clients.get(provider)
        if not client:
            return GenerationResult(
                id=str(uuid4())[:16],
                request_id=request.id,
                provider=provider,
                success=False,
                error=f"Provider {provider.value} not configured",
            )

        # Generate
        result = await client.generate(request)

        # Try fallback if failed and fallback enabled
        if not result.success and fallback:
            providers = self.get_providers_for_type(request.generation_type)
            for fallback_provider in providers[1:]:
                fallback_client = self._clients.get(fallback_provider)
                if fallback_client:
                    logger.info(f"Trying fallback provider: {fallback_provider.value}")
                    result = await fallback_client.generate(request)
                    if result.success:
                        break

        # Record history
        self._history.append(result)
        if len(self._history) > 1000:
            self._history = self._history[-1000:]

        return result

    async def generate_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        provider: VisualProvider | None = None,
        **kwargs,
    ) -> GenerationResult:
        """
        Convenience method for image generation.

        Args:
            prompt: Image description
            width: Image width
            height: Image height
            provider: Specific provider (Google Imagen default)
            **kwargs: Additional parameters
        """
        request = GenerationRequest(
            prompt=prompt,
            generation_type=GenerationType.IMAGE_FROM_TEXT,
            provider=provider or VisualProvider.GOOGLE_IMAGEN,
            width=width,
            height=height,
            **kwargs,
        )
        return await self.generate(request, provider)

    async def generate_video(
        self,
        prompt: str,
        duration: int = 5,
        aspect_ratio: AspectRatio = AspectRatio.LANDSCAPE,
        **kwargs,
    ) -> GenerationResult:
        """
        Convenience method for video generation.

        Uses Google Veo exclusively.
        """
        request = GenerationRequest(
            prompt=prompt,
            generation_type=GenerationType.VIDEO_FROM_TEXT,
            provider=VisualProvider.GOOGLE_VEO,
            duration_seconds=duration,
            aspect_ratio=aspect_ratio,
            **kwargs,
        )
        return await self.generate(request, VisualProvider.GOOGLE_VEO)

    async def generate_product_image(
        self,
        product_name: str,
        collection: str = "SIGNATURE",
        style: str = "product photography",
        background: str = "white studio background",
        **kwargs,
    ) -> GenerationResult:
        """
        Generate product image with SkyyRose branding.

        Args:
            product_name: Name/description of product
            collection: SkyyRose collection (BLACK ROSE, LOVE HURTS, SIGNATURE)
            style: Photography style
            background: Background setting
        """
        collection_style = SKYYROSE_BRAND_DNA["collections"].get(collection, "luxury streetwear")

        prompt = f"""
        {product_name} for SkyyRose luxury streetwear brand
        Collection: {collection} - {collection_style}
        Style: {style}
        Background: {background}
        Colors: Rose gold accents, black, premium fabric
        Quality: High-end e-commerce product photography
        Lighting: Professional studio lighting
        """

        return await self.generate_image(prompt.strip(), **kwargs)

    async def generate_exact_product(
        self,
        product_description: str,
        collection: str = "SIGNATURE",
        garment_type: str = "",
        num_outputs: int = 1,
        **kwargs,
    ) -> GenerationResult:
        """
        Generate EXACT SkyyRose product using trained LoRA.

        Uses the custom LoRA trained on 390 real product images.
        This produces images that match actual products, not generic generations.

        Args:
            product_description: What to generate (e.g., "lavender beanie with rose embroidery")
            collection: SkyyRose collection (SIGNATURE, BLACK_ROSE, LOVE_HURTS)
            garment_type: Type of garment (hoodie, tee, beanie, shorts, jacket, etc.)
            num_outputs: Number of images to generate (1-4)

        Returns:
            GenerationResult with exact product images
        """
        request = GenerationRequest(
            prompt=product_description,
            generation_type=GenerationType.EXACT_PRODUCT,
            provider=VisualProvider.REPLICATE_LORA,
            num_outputs=min(num_outputs, 4),
            metadata={
                "collection": collection.upper(),
                "garment_type": garment_type,
            },
            **kwargs,
        )
        return await self.generate(request, VisualProvider.REPLICATE_LORA, fallback=True)

    async def generate_campaign_video(
        self, concept: str, collection: str = "SIGNATURE", duration: int = 10, **kwargs
    ) -> GenerationResult:
        """
        Generate marketing campaign video.

        Args:
            concept: Video concept/theme
            collection: SkyyRose collection
            duration: Video duration in seconds
        """
        collection_style = SKYYROSE_BRAND_DNA["collections"].get(collection, "luxury streetwear")

        prompt = f"""
        SkyyRose luxury streetwear campaign video
        Concept: {concept}
        Collection: {collection} - {collection_style}
        Brand: SkyyRose
        Style: Cinematic, editorial, high-fashion
        Colors: Rose gold, black, dramatic lighting
        Movement: Smooth, professional camera work
        Quality: 4K, fashion film aesthetic
        """

        return await self.generate_video(prompt.strip(), duration, **kwargs)

    def get_history(self, limit: int = 100) -> list[GenerationResult]:
        """Get generation history"""
        return self._history[-limit:]

    def get_stats(self) -> dict[str, Any]:
        """Get generation statistics"""
        stats: dict[str, dict] = {
            p.value: {"count": 0, "success": 0, "total_cost": 0.0} for p in VisualProvider
        }

        for result in self._history:
            p = result.provider.value
            stats[p]["count"] += 1
            if result.success:
                stats[p]["success"] += 1
            stats[p]["total_cost"] += result.cost_usd

        # Calculate success rates
        for _p, s in stats.items():
            s["success_rate"] = s["success"] / s["count"] if s["count"] > 0 else 0.0

        return stats


# =============================================================================
# Factory and Exports
# =============================================================================


async def create_visual_router() -> VisualGenerationRouter:
    """Factory function to create and initialize visual router"""
    router = VisualGenerationRouter()
    await router.initialize()
    return router


__all__ = [
    # Enums
    "VisualProvider",
    "GenerationType",
    "AspectRatio",
    "ImageQuality",
    # Data classes
    "GenerationRequest",
    "GenerationResult",
    # Brand DNA
    "SKYYROSE_BRAND_DNA",
    # Clients
    "GoogleImagenClient",
    "GoogleVeoClient",
    "HuggingFaceFluxClient",
    "ReplicateLoRAClient",
    # Router
    "VisualGenerationRouter",
    # Factory
    "create_visual_router",
]
