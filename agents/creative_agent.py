"""
DevSkyy Creative SuperAgent
===========================

Handles all creative and asset operations for SkyyRose.

Consolidates:
- 3D model generation (Tripo3D)
- Virtual try-on (FASHN/IDM-VTON)
- Image generation (Google Imagen, HuggingFace FLUX.1)
- Video generation (Google Veo)
- Product photography
- Brand asset management

Visual Generation Rule:
Google + HuggingFace handle ALL imagery/video/AI model generation
with SkyyRose brand assets (NO EXCEPTIONS)
"""

import logging
from datetime import UTC, datetime
from enum import StrEnum
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

from .base_super_agent import EnhancedSuperAgent, SuperAgentType
from .multimodal_capabilities import (
    AnalysisType,
    get_multimodal_capabilities,
)

logger = logging.getLogger(__name__)


class VisualProvider(StrEnum):
    """Visual generation providers"""

    GOOGLE_IMAGEN = "google_imagen"
    GOOGLE_VEO = "google_veo"
    HUGGINGFACE_FLUX = "huggingface_flux"
    TRIPO3D = "tripo3d"
    FASHN = "fashn"


class VisualTaskType(StrEnum):
    """Types of visual tasks"""

    IMAGE_FROM_TEXT = "image_from_text"
    VIDEO_FROM_TEXT = "video_from_text"
    IMAGE_EDITING = "image_editing"
    MODEL_3D_FROM_TEXT = "3d_from_text"
    MODEL_3D_FROM_IMAGE = "3d_from_image"
    VIRTUAL_TRYON = "virtual_tryon"
    AI_MODEL_PHOTO = "ai_model_photo"
    BACKGROUND_REMOVAL = "background_removal"
    STYLE_TRANSFER = "style_transfer"


class CreativeAgent(EnhancedSuperAgent):
    """
    Creative Super Agent - Handles all creative/asset operations.

    Features:
    - 17 prompt engineering techniques
    - Multi-provider visual generation routing
    - Google Imagen + Veo integration
    - HuggingFace FLUX.1 integration
    - Tripo3D 3D model generation
    - FASHN virtual try-on

    Visual Generation Rules:
    - Google Imagen: Text-to-image, AI model photos
    - Google Veo: Text-to-video, product videos
    - HuggingFace FLUX.1: High-quality image generation
    - Tripo3D: 3D model generation
    - FASHN: Virtual try-on, background removal

    Example:
        agent = CreativeAgent()
        await agent.initialize()
        result = await agent.generate_image("Rose gold bomber jacket on white background")
    """

    agent_type = SuperAgentType.CREATIVE
    sub_capabilities = [
        "image_generation",
        "video_generation",
        "3d_generation",
        "virtual_tryon",
        "product_photography",
        "asset_management",
    ]

    # Visual task routing - Google + HuggingFace for ALL imagery
    VISUAL_ROUTING: dict[VisualTaskType, list[VisualProvider]] = {
        VisualTaskType.IMAGE_FROM_TEXT: [
            VisualProvider.GOOGLE_IMAGEN,
            VisualProvider.HUGGINGFACE_FLUX,
        ],
        VisualTaskType.VIDEO_FROM_TEXT: [
            VisualProvider.GOOGLE_VEO,
        ],
        VisualTaskType.IMAGE_EDITING: [
            VisualProvider.GOOGLE_IMAGEN,
            VisualProvider.HUGGINGFACE_FLUX,
        ],
        VisualTaskType.MODEL_3D_FROM_TEXT: [
            VisualProvider.TRIPO3D,
        ],
        VisualTaskType.MODEL_3D_FROM_IMAGE: [
            VisualProvider.TRIPO3D,
        ],
        VisualTaskType.VIRTUAL_TRYON: [
            VisualProvider.FASHN,
        ],
        VisualTaskType.AI_MODEL_PHOTO: [
            VisualProvider.GOOGLE_IMAGEN,
            VisualProvider.FASHN,
        ],
        VisualTaskType.BACKGROUND_REMOVAL: [
            VisualProvider.FASHN,
        ],
        VisualTaskType.STYLE_TRANSFER: [
            VisualProvider.GOOGLE_IMAGEN,
            VisualProvider.HUGGINGFACE_FLUX,
        ],
    }

    # Brand DNA for visual generation
    SKYYROSE_BRAND_DNA = {
        "primary_colors": ["#B76E79", "#1A1A1A", "#FFFFFF"],
        "color_names": ["rose_gold", "obsidian_black", "ivory"],
        "aesthetic": "luxury streetwear",
        "style": "bold, sophisticated, emotionally resonant",
        "quality": "premium, high-resolution, editorial",
        "tagline": "",
        "collections": {
            "BLACK ROSE": "dark elegance, limited edition, mysterious allure",
            "LOVE HURTS": "emotional expression, bold statements, vulnerable strength",
            "SIGNATURE": "foundation wardrobe, timeless essentials, everyday luxury",
        },
    }

    def __init__(self, config: AgentConfig | None = None):
        if config is None:
            config = AgentConfig(
                name="creative_agent",
                provider=ADKProvider.PYDANTIC,
                model=OPENAI_VISION_MODEL,
                system_prompt=self._build_system_prompt(),
                capabilities=[
                    AgentCapability.THREE_D_GENERATION,
                    AgentCapability.VIRTUAL_TRYON,
                    AgentCapability.IMAGE_GENERATION,
                    AgentCapability.VISION,
                ],
                tools=self._build_tools(),
                temperature=0.7,  # Higher for creativity
            )
        super().__init__(config)

        # Visual provider configurations
        self._visual_configs: dict[VisualProvider, dict] = {}

    def _build_system_prompt(self) -> str:
        """Build the creative agent system prompt"""
        return """You are the Creative SuperAgent for SkyyRose luxury streetwear.

## IDENTITY
You are an expert creative director and visual artist with mastery of:
- AI-powered image generation
- 3D modeling and visualization
- Video production
- Virtual fashion try-on
- Brand visual identity
- Product photography

## BRAND VISUAL IDENTITY
**Colors:**
- Rose Gold (#B76E79) - Primary accent, luxury warmth
- Obsidian Black (#1A1A1A) - Sophistication, foundation
- Ivory (#FFFFFF) - Clean, premium contrast

**Aesthetic:**
- Luxury streetwear fusion
- Bold yet sophisticated
- Emotionally resonant imagery
- High-contrast, editorial quality
- Premium craftsmanship focus

**Collections Visual Themes:**
- BLACK ROSE: Dark elegance, mysterious allure, rose motifs, limited edition feel
- LOVE HURTS: Emotional expression, heart imagery, vulnerable strength
- SIGNATURE: Clean lines, foundation wardrobe, timeless elegance

## VISUAL GENERATION RULES (CRITICAL)
Google + HuggingFace handle ALL imagery/video/AI model generation - NO EXCEPTIONS:
- **Google Imagen**: Text-to-image, AI model photos, marketing visuals
- **Google Veo**: Product videos, campaign videos, animations
- **HuggingFace FLUX.1**: High-quality image generation, style variations
- **Tripo3D**: 3D model generation from images
- **FASHN**: Virtual try-on, AI model fitting

## RESPONSIBILITIES
1. **Image Generation**
   - Product imagery for e-commerce
   - Marketing and campaign visuals
   - Social media content
   - Brand assets

2. **Video Generation**
   - Product showcase videos
   - Campaign videos
   - Social media reels
   - 3D product animations

3. **3D Asset Generation**
   - Product 3D models for web
   - AR/VR ready assets
   - 360° product views
   - Interactive visualizations

4. **Virtual Try-On**
   - AI model fitting
   - Customer virtual try-on
   - Size visualization
   - Style combinations

5. **Asset Management**
   - Organize brand assets
   - Maintain asset library
   - Version control
   - Format optimization

## OUTPUT REQUIREMENTS
- Images: High-resolution (min 1024x1024), web-optimized
- Videos: 1080p or 4K, optimized for web delivery
- 3D Models: GLB/GLTF format, web-optimized
- All assets must align with brand DNA
- Include proper metadata and descriptions"""

    def _build_tools(self) -> list[ToolDefinition]:
        """Build creative-specific tools"""
        return [
            # Image Generation Tools
            ToolDefinition(
                name="generate_image_google",
                description="Generate image using Google Imagen 3",
                parameters={
                    "prompt": {"type": "string", "description": "Image generation prompt"},
                    "style": {"type": "string", "description": "Style preset"},
                    "aspect_ratio": {
                        "type": "string",
                        "description": "Aspect ratio (1:1, 16:9, etc.)",
                    },
                    "negative_prompt": {"type": "string", "description": "What to avoid"},
                },
            ),
            ToolDefinition(
                name="generate_image_flux",
                description="Generate image using HuggingFace FLUX.1",
                parameters={
                    "prompt": {"type": "string", "description": "Image generation prompt"},
                    "width": {"type": "integer", "description": "Image width"},
                    "height": {"type": "integer", "description": "Image height"},
                    "guidance_scale": {"type": "number", "description": "Guidance scale"},
                    "num_inference_steps": {"type": "integer", "description": "Number of steps"},
                },
            ),
            # Video Generation Tools
            ToolDefinition(
                name="generate_video_veo",
                description="Generate video using Google Veo 2",
                parameters={
                    "prompt": {"type": "string", "description": "Video generation prompt"},
                    "duration": {"type": "integer", "description": "Duration in seconds"},
                    "aspect_ratio": {"type": "string", "description": "Aspect ratio"},
                    "style": {"type": "string", "description": "Visual style"},
                },
            ),
            # 3D Generation Tools
            ToolDefinition(
                name="generate_3d_model",
                description="Generate 3D model from image using Tripo3D",
                parameters={
                    "image_url": {"type": "string", "description": "Source image URL"},
                    "quality": {
                        "type": "string",
                        "description": "Quality level (draft, standard, premium)",
                    },
                    "format": {"type": "string", "description": "Output format (glb, gltf, fbx)"},
                    "texture_quality": {"type": "string", "description": "Texture quality"},
                },
            ),
            ToolDefinition(
                name="generate_3d_from_text",
                description="Generate 3D model from text description",
                parameters={
                    "prompt": {"type": "string", "description": "3D model description"},
                    "style": {"type": "string", "description": "Visual style"},
                    "format": {"type": "string", "description": "Output format"},
                },
            ),
            # Virtual Try-On Tools
            ToolDefinition(
                name="virtual_tryon",
                description="Apply garment to model image using FASHN",
                parameters={
                    "garment_image": {"type": "string", "description": "Garment image URL"},
                    "model_image": {"type": "string", "description": "Model/person image URL"},
                    "category": {
                        "type": "string",
                        "description": "Garment category (tops, bottoms, dresses)",
                    },
                    "adjust_hands": {"type": "boolean", "description": "Adjust hand positioning"},
                },
            ),
            ToolDefinition(
                name="generate_ai_model",
                description="Generate AI fashion model wearing garment",
                parameters={
                    "garment_image": {"type": "string", "description": "Garment image URL"},
                    "model_attributes": {"type": "object", "description": "Model characteristics"},
                    "pose": {"type": "string", "description": "Model pose"},
                    "background": {"type": "string", "description": "Background setting"},
                },
            ),
            # Image Processing Tools
            ToolDefinition(
                name="remove_background",
                description="Remove background from image",
                parameters={
                    "image_url": {"type": "string", "description": "Image URL"},
                    "output_format": {"type": "string", "description": "Output format (png, webp)"},
                },
            ),
            ToolDefinition(
                name="enhance_image",
                description="Enhance and optimize image",
                parameters={
                    "image_url": {"type": "string", "description": "Image URL"},
                    "enhancements": {"type": "array", "description": "Enhancement types"},
                    "target_resolution": {"type": "string", "description": "Target resolution"},
                },
            ),
            # Asset Management Tools
            ToolDefinition(
                name="upload_asset",
                description="Upload asset to WordPress media library",
                parameters={
                    "file_url": {"type": "string", "description": "Asset URL or path"},
                    "title": {"type": "string", "description": "Asset title"},
                    "alt_text": {"type": "string", "description": "Alt text for accessibility"},
                    "categories": {"type": "array", "description": "Asset categories"},
                },
            ),
            ToolDefinition(
                name="search_assets",
                description="Search brand asset library",
                parameters={
                    "query": {"type": "string", "description": "Search query"},
                    "asset_type": {
                        "type": "string",
                        "description": "Type filter (image, video, 3d)",
                    },
                    "collection": {"type": "string", "description": "Collection filter"},
                },
            ),
            # Multimodal Analysis Tools (LlamaIndex-powered)
            ToolDefinition(
                name="analyze_product_image",
                description="AI-powered product image analysis with detailed description generation",
                parameters={
                    "image_path": {"type": "string", "description": "Path or URL to product image"},
                    "product_type": {
                        "type": "string",
                        "description": "Type of product (clothing, jewelry, accessory)",
                    },
                    "include_technical": {
                        "type": "boolean",
                        "description": "Include technical details like dimensions",
                    },
                },
            ),
            ToolDefinition(
                name="check_brand_compliance",
                description="Check if image complies with SkyyRose brand guidelines",
                parameters={
                    "image_path": {"type": "string", "description": "Path or URL to image"},
                    "check_colors": {"type": "boolean", "description": "Check color compliance"},
                    "check_quality": {"type": "boolean", "description": "Check image quality"},
                },
            ),
            ToolDefinition(
                name="extract_image_colors",
                description="Extract dominant colors from image for palette analysis",
                parameters={
                    "image_path": {"type": "string", "description": "Path or URL to image"},
                },
            ),
            ToolDefinition(
                name="analyze_visual_quality",
                description="Analyze image quality, resolution, and technical specifications",
                parameters={
                    "image_path": {"type": "string", "description": "Path or URL to image"},
                },
            ),
        ]

    def _register_tools(self) -> None:
        """Register creative tools with the global ToolRegistry for MCP integration."""
        registry = ToolRegistry.get_instance()

        creative_tools = [
            ToolSpec(
                name="creative_generate_image_google",
                description="Generate image using Google Imagen 3",
                category=ToolCategory.MEDIA,
                severity=ToolSeverity.LOW,
                parameters=[
                    ToolParameter(
                        name="prompt",
                        type=ParameterType.STRING,
                        description="Image generation prompt",
                        required=True,
                    ),
                    ToolParameter(
                        name="style",
                        type=ParameterType.STRING,
                        description="Style preset",
                        required=False,
                    ),
                    ToolParameter(
                        name="aspect_ratio",
                        type=ParameterType.STRING,
                        description="Aspect ratio (1:1, 16:9, etc.)",
                        required=False,
                    ),
                    ToolParameter(
                        name="negative_prompt",
                        type=ParameterType.STRING,
                        description="What to avoid in generation",
                        required=False,
                    ),
                ],
                idempotent=False,
                cacheable=False,
                tags={"creative", "image", "google", "generation"},
            ),
            ToolSpec(
                name="creative_generate_image_flux",
                description="Generate image using HuggingFace FLUX.1",
                category=ToolCategory.MEDIA,
                severity=ToolSeverity.LOW,
                parameters=[
                    ToolParameter(
                        name="prompt",
                        type=ParameterType.STRING,
                        description="Image generation prompt",
                        required=True,
                    ),
                    ToolParameter(
                        name="width",
                        type=ParameterType.INTEGER,
                        description="Image width in pixels",
                        required=False,
                    ),
                    ToolParameter(
                        name="height",
                        type=ParameterType.INTEGER,
                        description="Image height in pixels",
                        required=False,
                    ),
                    ToolParameter(
                        name="guidance_scale",
                        type=ParameterType.NUMBER,
                        description="Guidance scale for generation",
                        required=False,
                    ),
                ],
                idempotent=False,
                cacheable=False,
                tags={"creative", "image", "flux", "huggingface"},
            ),
            ToolSpec(
                name="creative_generate_video",
                description="Generate video using Google Veo 2",
                category=ToolCategory.MEDIA,
                severity=ToolSeverity.LOW,
                parameters=[
                    ToolParameter(
                        name="prompt",
                        type=ParameterType.STRING,
                        description="Video generation prompt",
                        required=True,
                    ),
                    ToolParameter(
                        name="duration",
                        type=ParameterType.INTEGER,
                        description="Duration in seconds",
                        required=False,
                    ),
                    ToolParameter(
                        name="aspect_ratio",
                        type=ParameterType.STRING,
                        description="Aspect ratio",
                        required=False,
                    ),
                ],
                idempotent=False,
                cacheable=False,
                tags={"creative", "video", "google", "veo"},
            ),
            ToolSpec(
                name="creative_generate_3d_model",
                description="Generate 3D model from image using Tripo3D",
                category=ToolCategory.MEDIA,
                severity=ToolSeverity.LOW,
                parameters=[
                    ToolParameter(
                        name="image_url",
                        type=ParameterType.STRING,
                        description="Source image URL",
                        required=True,
                    ),
                    ToolParameter(
                        name="quality",
                        type=ParameterType.STRING,
                        description="Quality level (draft, standard, premium)",
                        required=False,
                    ),
                    ToolParameter(
                        name="format",
                        type=ParameterType.STRING,
                        description="Output format (glb, gltf, fbx)",
                        required=False,
                    ),
                ],
                idempotent=False,
                cacheable=False,
                tags={"creative", "3d", "tripo", "generation"},
            ),
            ToolSpec(
                name="creative_virtual_tryon",
                description="Apply garment to model image using FASHN",
                category=ToolCategory.MEDIA,
                severity=ToolSeverity.LOW,
                parameters=[
                    ToolParameter(
                        name="garment_image",
                        type=ParameterType.STRING,
                        description="Garment image URL",
                        required=True,
                    ),
                    ToolParameter(
                        name="model_image",
                        type=ParameterType.STRING,
                        description="Model/person image URL",
                        required=True,
                    ),
                    ToolParameter(
                        name="category",
                        type=ParameterType.STRING,
                        description="Garment category (tops, bottoms, dresses)",
                        required=False,
                    ),
                ],
                idempotent=True,
                cacheable=True,
                tags={"creative", "tryon", "fashn", "virtual"},
            ),
            ToolSpec(
                name="creative_remove_background",
                description="Remove background from image",
                category=ToolCategory.MEDIA,
                severity=ToolSeverity.READ_ONLY,
                parameters=[
                    ToolParameter(
                        name="image_url",
                        type=ParameterType.STRING,
                        description="Image URL to process",
                        required=True,
                    ),
                    ToolParameter(
                        name="output_format",
                        type=ParameterType.STRING,
                        description="Output format (png, webp)",
                        required=False,
                    ),
                ],
                idempotent=True,
                cacheable=True,
                tags={"creative", "image", "processing"},
            ),
            ToolSpec(
                name="creative_upload_asset",
                description="Upload asset to WordPress media library",
                category=ToolCategory.CONTENT,
                severity=ToolSeverity.MEDIUM,
                parameters=[
                    ToolParameter(
                        name="file_url",
                        type=ParameterType.STRING,
                        description="Asset URL or path",
                        required=True,
                    ),
                    ToolParameter(
                        name="title",
                        type=ParameterType.STRING,
                        description="Asset title",
                        required=True,
                    ),
                    ToolParameter(
                        name="alt_text",
                        type=ParameterType.STRING,
                        description="Alt text for accessibility",
                        required=False,
                    ),
                ],
                idempotent=False,
                cacheable=False,
                tags={"creative", "asset", "wordpress", "upload"},
            ),
            ToolSpec(
                name="creative_search_assets",
                description="Search brand asset library",
                category=ToolCategory.CONTENT,
                severity=ToolSeverity.READ_ONLY,
                parameters=[
                    ToolParameter(
                        name="query",
                        type=ParameterType.STRING,
                        description="Search query",
                        required=True,
                    ),
                    ToolParameter(
                        name="asset_type",
                        type=ParameterType.STRING,
                        description="Type filter (image, video, 3d)",
                        required=False,
                    ),
                    ToolParameter(
                        name="collection",
                        type=ParameterType.STRING,
                        description="Collection filter",
                        required=False,
                    ),
                ],
                idempotent=True,
                cacheable=True,
                tags={"creative", "asset", "search"},
            ),
        ]

        for spec in creative_tools:
            registry.register(spec)

    async def execute(self, prompt: str, **kwargs) -> AgentResult:
        """Execute creative operation"""
        start_time = datetime.now(UTC)

        try:
            # Determine visual task type
            task_type = self._classify_visual_task(prompt)

            # Select appropriate technique
            technique = self._select_creative_technique(task_type)

            # Apply technique to enhance prompt
            enhanced = self.apply_technique(
                technique,
                prompt,
                role="creative director for SkyyRose luxury streetwear",
                background=f"Brand DNA: {self.SKYYROSE_BRAND_DNA}",
                **kwargs,
            )

            # Execute with backend
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
                metadata={
                    "task_type": task_type,
                    "technique": technique.value,
                    "providers": [p.value for p in self._get_providers_for_task(task_type)],
                },
            )

        except Exception as e:
            logger.error(f"Creative agent error: {e}")
            return AgentResult(
                agent_name=self.name,
                agent_provider=self._active_provider,
                content="",
                status=AgentStatus.FAILED,
                error=str(e),
                started_at=start_time,
            )

    def _classify_visual_task(self, prompt: str) -> VisualTaskType:
        """Classify the visual task type"""
        prompt_lower = prompt.lower()

        if any(kw in prompt_lower for kw in ["video", "animate", "motion", "clip"]):
            return VisualTaskType.VIDEO_FROM_TEXT
        if any(kw in prompt_lower for kw in ["3d", "model", "mesh", "glb"]):
            if "image" in prompt_lower:
                return VisualTaskType.MODEL_3D_FROM_IMAGE
            return VisualTaskType.MODEL_3D_FROM_TEXT
        if any(kw in prompt_lower for kw in ["try on", "tryon", "fitting", "wear"]):
            return VisualTaskType.VIRTUAL_TRYON
        if any(kw in prompt_lower for kw in ["ai model", "fashion model", "person wearing"]):
            return VisualTaskType.AI_MODEL_PHOTO
        if any(kw in prompt_lower for kw in ["remove background", "transparent", "cutout"]):
            return VisualTaskType.BACKGROUND_REMOVAL
        if any(kw in prompt_lower for kw in ["style", "transfer", "apply style"]):
            return VisualTaskType.STYLE_TRANSFER

        return VisualTaskType.IMAGE_FROM_TEXT

    def _select_creative_technique(self, task_type: VisualTaskType) -> PromptTechnique:
        """Select prompt technique for creative task"""
        # Creative tasks benefit from Tree of Thoughts for exploration
        if task_type in [VisualTaskType.IMAGE_FROM_TEXT, VisualTaskType.VIDEO_FROM_TEXT]:
            return PromptTechnique.TREE_OF_THOUGHTS
        # Role-based for AI model generation
        if task_type == VisualTaskType.AI_MODEL_PHOTO:
            return PromptTechnique.ROLE_BASED
        # Structured output for 3D generation parameters
        if task_type in [VisualTaskType.MODEL_3D_FROM_TEXT, VisualTaskType.MODEL_3D_FROM_IMAGE]:
            return PromptTechnique.STRUCTURED_OUTPUT
        # Few-shot for virtual try-on
        if task_type == VisualTaskType.VIRTUAL_TRYON:
            return PromptTechnique.FEW_SHOT

        return PromptTechnique.ROLE_BASED

    def _get_providers_for_task(self, task_type: VisualTaskType) -> list[VisualProvider]:
        """Get the appropriate visual providers for a task"""
        return self.VISUAL_ROUTING.get(task_type, [VisualProvider.GOOGLE_IMAGEN])

    async def _fallback_process(self, prompt: str, task_type: VisualTaskType) -> str:
        """Fallback processing when backend unavailable"""
        providers = self._get_providers_for_task(task_type)
        return f"""Creative Agent Analysis

Task Type: {task_type.value}
Query: {prompt[:200]}...
Recommended Providers: {[p.value for p in providers]}

Brand Guidelines Applied:
- Colors: Rose Gold, Obsidian Black, Ivory
- Aesthetic: Luxury Streetwear
- Quality: Premium, High-Resolution

For full visual generation, ensure visual APIs are configured."""

    # =========================================================================
    # Creative-Specific Methods
    # =========================================================================

    async def generate_image(
        self, prompt: str, provider: VisualProvider = VisualProvider.GOOGLE_IMAGEN, **kwargs
    ) -> dict[str, Any]:
        """
        Generate image using specified provider.

        Args:
            prompt: Image generation prompt
            provider: Visual provider to use
            **kwargs: Provider-specific parameters

        Returns:
            Generated image info
        """
        # Enhance prompt with brand DNA
        enhanced_prompt = self._enhance_visual_prompt(prompt)

        task_prompt = f"""Generate an image using {provider.value}:

Prompt: {enhanced_prompt}
Brand: SkyyRose""
Style: Luxury streetwear, editorial quality
Colors: Rose gold accents, black foundation, white contrast

Parameters: {kwargs}

Return the generation command and expected result."""

        result = await self.execute_with_learning(
            task_prompt,
            task_type="image_generation",
            technique=PromptTechnique.STRUCTURED_OUTPUT,
            schema={
                "provider": "string",
                "prompt_used": "string",
                "parameters": "object",
                "expected_output": "object",
            },
        )

        return {"provider": provider.value, "prompt": enhanced_prompt, "result": result.content}

    async def generate_video(self, prompt: str, duration: int = 5, **kwargs) -> dict[str, Any]:
        """
        Generate video using Google Veo.

        Args:
            prompt: Video generation prompt
            duration: Video duration in seconds
            **kwargs: Additional parameters
        """
        enhanced_prompt = self._enhance_visual_prompt(prompt)

        task_prompt = f"""Generate a video using Google Veo 2:

Prompt: {enhanced_prompt}
Duration: {duration} seconds
Brand: SkyyRose luxury streetwear

The video should:
- Showcase the product elegantly
- Use smooth camera movements
- Highlight texture and details
- Match brand aesthetic

Parameters: {kwargs}"""

        result = await self.execute_with_learning(
            task_prompt,
            task_type="video_generation",
            technique=PromptTechnique.ROLE_BASED,
            role="video production director",
        )

        return {
            "provider": "google_veo",
            "prompt": enhanced_prompt,
            "duration": duration,
            "result": result.content,
        }

    async def generate_3d_model(
        self, image_url: str, quality: str = "standard", **kwargs
    ) -> dict[str, Any]:
        """
        Generate 3D model from image using Tripo3D.

        Args:
            image_url: Source product image
            quality: Quality level (draft, standard, premium)
            **kwargs: Additional parameters
        """
        task_prompt = f"""Generate a 3D model from image using Tripo3D:

Image URL: {image_url}
Quality: {quality}
Format: GLB (web-optimized)

The 3D model should:
- Capture accurate product geometry
- Include high-quality textures
- Be optimized for web display
- Support AR/VR viewing

Parameters: {kwargs}"""

        result = await self.execute_with_learning(
            task_prompt, task_type="3d_generation", technique=PromptTechnique.STRUCTURED_OUTPUT
        )

        return {
            "provider": "tripo3d",
            "source_image": image_url,
            "quality": quality,
            "result": result.content,
        }

    async def virtual_tryon(
        self, garment_image: str, model_image: str, category: str = "tops", **kwargs
    ) -> dict[str, Any]:
        """
        Apply virtual try-on using FASHN.

        Args:
            garment_image: Garment/product image URL
            model_image: Model/person image URL
            category: Garment category
            **kwargs: Additional parameters
        """
        task_prompt = f"""Perform virtual try-on using FASHN API:

Garment Image: {garment_image}
Model Image: {model_image}
Category: {category}

The try-on should:
- Realistically fit the garment to the model
- Preserve natural body proportions
- Handle fabric draping accurately
- Maintain garment details and textures

Parameters: {kwargs}"""

        result = await self.execute_with_learning(
            task_prompt,
            task_type="virtual_tryon",
            technique=PromptTechnique.REACT,
            tools=["fashn_tryon", "adjust_fit", "quality_check"],
        )

        return {
            "provider": "fashn",
            "garment": garment_image,
            "model": model_image,
            "category": category,
            "result": result.content,
        }

    def _enhance_visual_prompt(self, prompt: str) -> str:
        """Enhance prompt with brand DNA"""
        brand_context = f"""
Brand: SkyyRose""
Aesthetic: {self.SKYYROSE_BRAND_DNA["aesthetic"]}
Style: {self.SKYYROSE_BRAND_DNA["style"]}
Quality: {self.SKYYROSE_BRAND_DNA["quality"]}
Colors: Rose gold (#B76E79), black (#1A1A1A), white (#FFFFFF)
"""
        return f"{prompt}\n\n{brand_context}"

    async def route_visual_task(self, prompt: str, **kwargs) -> dict[str, Any]:
        """
        Automatically route visual task to appropriate provider.

        Determines task type and selects best provider(s).
        """
        task_type = self._classify_visual_task(prompt)
        providers = self._get_providers_for_task(task_type)

        logger.info(f"Routing {task_type.value} to providers: {[p.value for p in providers]}")

        # Use Round Table if multiple providers available
        if len(providers) > 1 and self.round_table:
            # Register provider generators
            # Note: Use default argument to capture provider value (avoid closure issue)
            for provider in providers:
                self.round_table.register_provider(
                    provider.value,
                    lambda p, c, prov=provider: self._execute_visual_provider(prov, p, c),
                )

            result = await self.round_table.compete(prompt)
            return {
                "task_type": task_type.value,
                "winner": result.winner.provider,
                "result": result.winner.response,
            }

        # Single provider - execute directly
        primary_provider = providers[0]
        result = await self.execute(prompt, provider=primary_provider, **kwargs)

        return {
            "task_type": task_type.value,
            "provider": primary_provider.value,
            "result": result.content,
        }

    async def _execute_visual_provider(
        self, provider: VisualProvider, prompt: str, context: dict | None
    ) -> dict[str, Any]:
        """Execute visual generation with specific provider"""
        # Provider-specific execution logic
        return {
            "provider": provider.value,
            "prompt": prompt,
            "text": f"Generated with {provider.value}: {prompt[:100]}...",
            "cost": 0.01,
        }

    # =========================================================================
    # Multimodal Analysis Methods (LlamaIndex Integration)
    # =========================================================================

    async def analyze_product_image_tool(
        self, image_path: str, product_type: str = "clothing", include_technical: bool = True
    ) -> dict[str, Any]:
        """
        Tool handler for product image analysis.

        Uses LlamaIndex multimodal capabilities to analyze product images
        and generate detailed e-commerce descriptions.

        Args:
            image_path: Path or URL to product image
            product_type: Type of product (clothing, jewelry, accessory)
            include_technical: Include technical details

        Returns:
            Analysis result with product description
        """
        try:
            capabilities = get_multimodal_capabilities()
            await capabilities.initialize()

            result = await capabilities.analyze_product_image(
                image_path=image_path,
                product_type=product_type,
                include_technical=include_technical,
            )

            return {
                "success": True,
                "product_type": product_type,
                "description": result.text_response,
                "confidence": result.confidence,
                "provider": result.provider.value,
                "processing_time_ms": result.processing_time_ms,
                "metadata": result.metadata,
            }

        except Exception as e:
            logger.error(f"Product image analysis failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
            }

    async def check_brand_compliance_tool(
        self, image_path: str, check_colors: bool = True, check_quality: bool = True
    ) -> dict[str, Any]:
        """
        Tool handler for brand compliance checking.

        Analyzes images against SkyyRose brand guidelines.

        Args:
            image_path: Path or URL to image
            check_colors: Check color compliance
            check_quality: Check image quality

        Returns:
            Compliance analysis result
        """
        try:
            capabilities = get_multimodal_capabilities()
            await capabilities.initialize()

            result = await capabilities.check_brand_compliance(
                image_path=image_path,
                brand_colors=self.SKYYROSE_BRAND_DNA["primary_colors"],
                brand_style=self.SKYYROSE_BRAND_DNA["aesthetic"],
            )

            return {
                "success": True,
                "compliant": "✓ PASS" in result.text_response,
                "analysis": result.text_response,
                "provider": result.provider.value,
                "processing_time_ms": result.processing_time_ms,
                "checks": {
                    "colors": check_colors,
                    "quality": check_quality,
                },
            }

        except Exception as e:
            logger.error(f"Brand compliance check failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
            }

    async def extract_image_colors_tool(self, image_path: str) -> dict[str, Any]:
        """
        Tool handler for color extraction.

        Analyzes and extracts dominant colors from images.

        Args:
            image_path: Path or URL to image

        Returns:
            Color analysis result
        """
        try:
            capabilities = get_multimodal_capabilities()
            await capabilities.initialize()

            result = await capabilities.extract_colors(image_path=image_path)

            return {
                "success": True,
                "colors": result.text_response,
                "provider": result.provider.value,
                "processing_time_ms": result.processing_time_ms,
            }

        except Exception as e:
            logger.error(f"Color extraction failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
            }

    async def analyze_visual_quality_tool(self, image_path: str) -> dict[str, Any]:
        """
        Tool handler for visual quality analysis.

        Analyzes image quality, resolution, and technical specifications.

        Args:
            image_path: Path or URL to image

        Returns:
            Quality analysis result
        """
        try:
            capabilities = get_multimodal_capabilities()
            await capabilities.initialize()

            prompt = """Analyze this image's technical quality:

1. **Resolution & Size**: Estimate resolution and dimensions
2. **Image Quality**: Sharpness, clarity, compression artifacts
3. **Lighting**: Lighting quality and consistency
4. **Composition**: Framing, subject placement, background
5. **Color Accuracy**: Color saturation, balance, accuracy
6. **Technical Issues**: Any defects, noise, or problems

Provide a quality score (1-10) and detailed recommendations."""

            result = await capabilities.analyze_image(
                image_path=image_path,
                analysis_type=AnalysisType.QUALITY_CHECK,
                prompt=prompt,
            )

            return {
                "success": True,
                "analysis": result.text_response,
                "provider": result.provider.value,
                "processing_time_ms": result.processing_time_ms,
            }

        except Exception as e:
            logger.error(f"Quality analysis failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
            }


# =============================================================================
# Export
# =============================================================================

__all__ = [
    "CreativeAgent",
    "VisualProvider",
    "VisualTaskType",
]
