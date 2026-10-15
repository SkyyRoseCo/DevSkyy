"""
Gemini Native Image Generation - Prompt Optimization Patterns
==============================================================

Custom prompt engineering patterns optimized for Gemini's native image
generation models (gemini-2.5-flash-image and gemini-3-pro-image-preview).

Implements 5 specialized patterns:
1. Tree of Thoughts for Complex Visuals - Explore creative directions
2. Negative Prompting Engine - Brand consistency enforcement
3. Collection-Aware Prompt Templates - SkyyRose collection specifics
4. Thinking Mode Constructor - Step-by-step concept analysis (Pro only)
5. Google Search Grounding Optimizer - Real-time trend integration

Based on official Google Gemini prompt engineering best practices:
- Hyper-specific descriptions
- Camera control language (wide-angle, macro, cinematic lighting)
- Semantic negative prompts (describe what you WANT)
- Step-by-step composition instructions
- Product photography templates with lighting specifications

Created: 2026-01-08
Status: Phase 2 - Prompt Optimization
"""

from enum import StrEnum

import structlog

from orchestration.brand_context import BrandContextInjector, Collection

logger = structlog.get_logger(__name__)


class VisualUseCase(StrEnum):
    """Visual generation use cases for template selection."""

    PRODUCT_PHOTOGRAPHY = "product_photography"
    CAMPAIGN_IMAGERY = "campaign_imagery"
    AI_MODEL_GENERATION = "ai_model_generation"
    EDITORIAL_FASHION = "editorial_fashion"
    LIFESTYLE_CONTENT = "lifestyle_content"
    SOCIAL_MEDIA = "social_media"


class CameraAngle(StrEnum):
    """Camera angle specifications for product photography."""

    STRAIGHT_ON = "straight-on at eye level"
    LOW_ANGLE = "low-angle perspective"
    HIGH_ANGLE = "high-angle overhead shot"
    THREE_QUARTER = "three-quarter angle"
    CLOSE_UP = "close-up macro shot"
    WIDE_ANGLE = "wide-angle establishing shot"


class LightingSetup(StrEnum):
    """Professional lighting setups for product photography."""

    THREE_POINT_SOFTBOX = "three-point softbox setup"
    NATURAL_WINDOW = "natural window lighting with diffuser"
    DRAMATIC_CHIAROSCURO = "dramatic chiaroscuro with single key light"
    STUDIO_FLAT = "flat studio lighting for even exposure"
    CINEMATIC_MOODY = "cinematic moody lighting with rim light"
    GOLDEN_HOUR = "warm golden hour natural lighting"


# =============================================================================
# Pattern 1: Tree of Thoughts for Complex Visuals
# =============================================================================


class GeminiTreeOfThoughtsVisual:
    """
    Tree of Thoughts pattern for complex visual generation.

    Explores 3 creative directions in parallel, evaluates each, then
    synthesizes the best elements into a final cohesive image prompt.

    Use cases:
    - Campaign imagery requiring creative exploration
    - AI model generation with multiple styling options
    - Editorial fashion spreads with artistic direction
    """

    @staticmethod
    def create_prompt(
        product_type: str,
        collection: Collection | None = None,
        focus_areas: list[str] | None = None,
        use_case: VisualUseCase = VisualUseCase.CAMPAIGN_IMAGERY,
    ) -> str:
        """
        Create Tree of Thoughts visual prompt exploring 3 creative directions.

        Args:
            product_type: Type of product (e.g., "hoodie", "t-shirt")
            collection: SkyyRose collection for brand context
            focus_areas: Specific areas to emphasize (e.g., ["fabric texture", "rose gold details"])
            use_case: Visual generation use case

        Returns:
            Comprehensive prompt with 3 directions + synthesis
        """
        focus_str = ", ".join(focus_areas) if focus_areas else "overall aesthetic"

        # Collection-specific creative directions
        if collection == Collection.BLACK_ROSE:
            direction_1 = "editorial gothic romance: dramatic chiaroscuro lighting, rose garden backdrop, mysterious elegance"
            direction_2 = "luxury streetwear: dark urban environment, neon rose gold accents, exclusive nightlife aesthetic"
            direction_3 = "high-fashion editorial: minimalist black studio, sculptural draping, timeless sophistication"
        elif collection == Collection.SIGNATURE:
            direction_1 = "clean studio minimalism: white backdrop, three-point softbox lighting, versatile essentials focus"
            direction_2 = "lifestyle versatility: natural outdoor setting, golden hour lighting, everyday luxury"
            direction_3 = (
                "premium basics: monochromatic palette, texture emphasis, timeless quality showcase"
            )
        elif collection == Collection.LOVE_HURTS:
            direction_1 = (
                "emotional vulnerability: soft lighting, intimate close-up, passionate expression"
            )
            direction_2 = "powerful resilience: dramatic rim lighting, confident pose, strength through emotion"
            direction_3 = "artistic expression: creative composition, color splash on rose gold, storytelling focus"
        else:
            direction_1 = (
                "studio professional: clean lighting, product-focused, commercial photography"
            )
            direction_2 = (
                "lifestyle authentic: natural environment, casual styling, relatable context"
            )
            direction_3 = "editorial creative: artistic composition, bold lighting, fashion-forward"

        prompt = f"""Think step-by-step about photographing a SkyyRose {product_type} for {use_case.value}.

Direction 1 ({direction_1}):
- Focus on {focus_str}
- Camera: {CameraAngle.THREE_QUARTER.value}, {LightingSetup.DRAMATIC_CHIAROSCURO.value}

Direction 2 ({direction_2}):
- Focus on {focus_str}
- Camera: {CameraAngle.LOW_ANGLE.value}, {LightingSetup.CINEMATIC_MOODY.value}

Direction 3 ({direction_3}):
- Focus on {focus_str}
- Camera: {CameraAngle.STRAIGHT_ON.value}, {LightingSetup.THREE_POINT_SOFTBOX.value}

Evaluation:
- Direction 1 strengths: [atmosphere, mood, exclusivity]
- Direction 2 strengths: [boldness, modern appeal, lifestyle context]
- Direction 3 strengths: [clarity, versatility, timeless elegance]

Synthesized Final Image:
Combine the best elements from all three directions. Create a high-resolution image that:
- Uses the most compelling composition and camera angle
- Applies the most flattering lighting setup
- Emphasizes {focus_str} with hyper-specific detail
- Maintains SkyyRose brand DNA (premium, sophisticated, bold)
- Ultra-realistic, sharp focus, professional photography quality
"""

        logger.info(
            "tree_of_thoughts_visual_prompt_created",
            product_type=product_type,
            collection=collection.value if collection else None,
            use_case=use_case.value,
        )

        return prompt


# =============================================================================
# Pattern 2: Negative Prompting Engine for Brand Consistency
# =============================================================================


class GeminiNegativePromptEngine:
    """
    Negative prompting engine for brand consistency.

    Implements semantic negative prompts (describe what you WANT to avoid,
    not just "no X") following Google's best practices.

    Enforces SkyyRose aesthetic standards across all generations.
    """

    # Base quality negatives (universal)
    BASE_NEGATIVES = [
        "low quality, blurry, out of focus, pixelated",
        "distorted proportions, anatomical errors, unrealistic",
        "poor lighting, flat lighting, harsh shadows, overexposed",
        "amateur photography, phone camera quality, poor composition",
        "watermarks, text overlays, logos (except SkyyRose)",
        "cluttered background, distracting elements, busy composition",
    ]

    # Collection-specific brand negatives
    COLLECTION_NEGATIVES = {
        Collection.BLACK_ROSE: [
            "bright cheerful colors, pastel tones, light mood",
            "daylight outdoor setting, sunny atmosphere",
            "casual relaxed styling, overly casual context",
            "minimalist bare aesthetic, stark white backgrounds",
        ],
        Collection.SIGNATURE: [
            "overly trendy, fast fashion aesthetic",
            "excessive branding, loud logos, flashy elements",
            "dark moody lighting, gothic atmosphere",
            "overly editorial, avant-garde, experimental styling",
        ],
        Collection.LOVE_HURTS: [
            "emotionless expression, clinical detachment",
            "corporate professional setting, sterile environment",
            "overly dark gothic mood, aggressive styling",
            "cold color temperature, harsh blue tones",
        ],
    }

    @staticmethod
    def get_base_negatives() -> list[str]:
        """Get universal base negative prompts for quality."""
        return GeminiNegativePromptEngine.BASE_NEGATIVES.copy()

    @staticmethod
    def get_collection_negatives(collection: Collection | None = None) -> list[str]:
        """
        Get collection-specific negative prompts for brand consistency.

        Args:
            collection: SkyyRose collection (BLACK_ROSE, SIGNATURE, LOVE_HURTS)

        Returns:
            List of semantic negative prompts to avoid
        """
        if collection and collection in GeminiNegativePromptEngine.COLLECTION_NEGATIVES:
            return GeminiNegativePromptEngine.COLLECTION_NEGATIVES[collection].copy()
        return []

    @staticmethod
    def build_negative_prompt(collection: Collection | None = None) -> str:
        """
        Build comprehensive negative prompt for image generation.

        Args:
            collection: SkyyRose collection for brand-specific negatives

        Returns:
            Comma-separated negative prompt string
        """
        negatives = GeminiNegativePromptEngine.get_base_negatives()

        if collection:
            collection_negatives = GeminiNegativePromptEngine.get_collection_negatives(collection)
            negatives.extend(collection_negatives)

        logger.info(
            "negative_prompt_built",
            collection=collection.value if collection else None,
            negative_count=len(negatives),
        )

        return ", ".join(negatives)


# =============================================================================
# Pattern 3: Collection-Aware Prompt Templates
# =============================================================================


class CollectionPromptBuilder:
    """
    Collection-aware prompt templates for SkyyRose brand.

    Implements hyper-specific product photography templates with:
    - Collection-specific mood, lighting, and composition
    - Camera control language (wide-angle, macro, cinematic)
    - Step-by-step composition instructions
    - Brand DNA integration
    """

    # Product photography template (Context7 best practice)
    PRODUCT_PHOTOGRAPHY_TEMPLATE = """A high-resolution, {lighting} product photograph of a {product_description} on a {background}. The lighting is a {lighting_setup} to {lighting_purpose}. The camera angle is a {camera_angle} to showcase {showcase_feature}. Ultra-realistic, with sharp focus on {focus_detail}. {mood_keywords}. Professional commercial photography. {aspect_ratio}."""

    # Collection-specific configurations
    COLLECTION_CONFIGS = {
        Collection.BLACK_ROSE: {
            "lighting": "dramatically lit, moody",
            "background": "dark textured surface with subtle rose gold accents",
            "lighting_setup": LightingSetup.DRAMATIC_CHIAROSCURO.value,
            "lighting_purpose": "create mysterious depth and exclusive luxury appeal",
            "camera_angle": CameraAngle.LOW_ANGLE.value,
            "showcase_feature": "the premium fabric texture and rose gold hardware details",
            "focus_detail": "embroidered rose motifs and metallic finishes",
            "mood_keywords": "Mysterious, exclusive, coveted, gothic elegance",
            "aspect_ratio": "16:9 cinematic",
        },
        Collection.SIGNATURE: {
            "lighting": "clean studio-lit",
            "background": "white seamless backdrop with soft shadows",
            "lighting_setup": LightingSetup.THREE_POINT_SOFTBOX.value,
            "lighting_purpose": "ensure even, flattering illumination on all product details",
            "camera_angle": CameraAngle.STRAIGHT_ON.value,
            "showcase_feature": "the versatile design and timeless silhouette",
            "focus_detail": "clean stitching and premium fabric quality",
            "mood_keywords": "Timeless, essential, versatile, sophisticated basics",
            "aspect_ratio": "4:5 portrait",
        },
        Collection.LOVE_HURTS: {
            "lighting": "warm, emotionally lit",
            "background": "soft gradient backdrop with rose gold highlights",
            "lighting_setup": LightingSetup.GOLDEN_HOUR.value,
            "lighting_purpose": "create warm, passionate, emotionally resonant atmosphere",
            "camera_angle": CameraAngle.CLOSE_UP.value,
            "showcase_feature": "the expressive graphic design and emotional messaging",
            "focus_detail": "heart motifs and passionate typography",
            "mood_keywords": "Emotional, passionate, vulnerable yet powerful",
            "aspect_ratio": "1:1 square",
        },
    }

    @staticmethod
    def build_prompt(
        product_name: str,
        collection: Collection | None = None,
        use_case: VisualUseCase = VisualUseCase.PRODUCT_PHOTOGRAPHY,
        custom_overrides: dict[str, str] | None = None,
    ) -> str:
        """
        Build collection-aware prompt for product photography.

        Args:
            product_name: Product name/description (e.g., "SkyyRose BLACK ROSE hoodie")
            collection: SkyyRose collection
            use_case: Visual generation use case
            custom_overrides: Optional overrides for template variables

        Returns:
            Hyper-specific product photography prompt
        """
        if use_case == VisualUseCase.PRODUCT_PHOTOGRAPHY:
            # Get collection config or default
            config = (
                CollectionPromptBuilder.COLLECTION_CONFIGS.get(collection, {}) if collection else {}
            )

            # Apply custom overrides
            if custom_overrides:
                config.update(custom_overrides)

            # Build prompt from template
            prompt = CollectionPromptBuilder.PRODUCT_PHOTOGRAPHY_TEMPLATE.format(
                product_description=product_name,
                lighting=config.get("lighting", "professionally lit"),
                background=config.get("background", "neutral backdrop"),
                lighting_setup=config.get(
                    "lighting_setup", LightingSetup.THREE_POINT_SOFTBOX.value
                ),
                lighting_purpose=config.get("lighting_purpose", "highlight product details"),
                camera_angle=config.get("camera_angle", CameraAngle.THREE_QUARTER.value),
                showcase_feature=config.get("showcase_feature", "the product design"),
                focus_detail=config.get("focus_detail", "key product features"),
                mood_keywords=config.get("mood_keywords", "Premium, sophisticated"),
                aspect_ratio=config.get("aspect_ratio", "1:1 square"),
            )

            logger.info(
                "collection_prompt_built",
                product_name=product_name,
                collection=collection.value if collection else None,
                use_case=use_case.value,
            )

            return prompt

        # For other use cases, return basic prompt (can be extended)
        return f"A professional photograph of {product_name}"


# =============================================================================
# Pattern 4: Thinking Mode Constructor (Pro Model Only)
# =============================================================================


class ThinkingModeConstructor:
    """
    Thinking mode constructor for gemini-3-pro-image-preview.

    Implements step-by-step visual concept analysis with interim "thought images"
    showing the model's reasoning process.

    Only supported by gemini-3-pro-image-preview, not gemini-2.5-flash-image.
    """

    @staticmethod
    def create_thinking_prompt(
        concept: str,
        collection: Collection | None = None,
        complexity_level: str = "moderate",
    ) -> str:
        """
        Create thinking mode prompt for complex visual concepts.

        Args:
            concept: Visual concept to analyze (e.g., "AI model wearing BLACK ROSE collection")
            collection: SkyyRose collection for brand context
            complexity_level: "simple", "moderate", "complex"

        Returns:
            Prompt with step-by-step reasoning instructions
        """
        collection_context = ""
        if collection:
            injector = BrandContextInjector()
            collection_context = injector.get_compact_prompt(collection)

        prompt = f"""Think step-by-step about creating this visual concept: {concept}

Step 1: Visual Concept Analysis
- What is the core message or emotion to convey?
- What visual elements are essential to the concept?
- What brand DNA elements must be preserved?
{collection_context}

Step 2: Composition Planning
- What camera angle best serves this concept?
- What lighting setup creates the desired mood?
- How should the subject be positioned in the frame?

Step 3: Brand DNA Integration Strategy
- How to incorporate rose gold (#B76E79) accents naturally?
- How to maintain premium, sophisticated aesthetic?
- How to ensure SkyyRose brand recognition?

Step 4: Technical Execution
- Resolution: 4K for maximum detail
- Focus areas: [list key areas requiring sharp focus]
- Post-processing style: [describe desired treatment]

Step 5: Final Synthesis
Now generate the image incorporating all analyzed elements.
"""

        logger.info(
            "thinking_mode_prompt_created",
            concept=concept,
            collection=collection.value if collection else None,
            complexity_level=complexity_level,
        )

        return prompt


# =============================================================================
# Pattern 5: Google Search Grounding Optimizer (Pro Model Only)
# =============================================================================


class GoogleSearchGroundingOptimizer:
    """
    Google Search grounding optimizer for gemini-3-pro-image-preview.

    Integrates real-time information from Google Search to:
    - Incorporate current fashion trends
    - Add Oakland cultural context
    - Synthesize contemporary yet timeless visuals

    Only supported by gemini-3-pro-image-preview, not gemini-2.5-flash-image.
    """

    @staticmethod
    def create_grounded_prompt(
        product_type: str,
        trend_keywords: list[str] | None = None,
        location_context: str = "Oakland, CA",
    ) -> str:
        """
        Create Google Search grounded prompt for trend-aware visuals.

        Args:
            product_type: Type of product (e.g., "hoodie", "t-shirt")
            trend_keywords: Fashion trend keywords to ground with (e.g., ["Y2K", "streetwear"])
            location_context: Geographic context for cultural relevance

        Returns:
            Prompt with search grounding instructions
        """
        trends_str = ", ".join(trend_keywords) if trend_keywords else "current fashion trends"

        prompt = f"""Use Google Search to inform this image generation:

Search Context:
- Product: SkyyRose {product_type}
- Trends: {trends_str}
- Location: {location_context}
- Brand: Luxury streetwear

Search for:
1. Current {trends_str} in premium streetwear photography
2. {location_context} street style and cultural aesthetic
3. Fashion editorial lighting techniques 2026

Synthesize:
- Contemporary trend-aware styling
- Oakland cultural authenticity
- Timeless SkyyRose brand sophistication

Generate an image that feels current yet timeless, incorporating real-world trend insights.
"""

        logger.info(
            "search_grounding_prompt_created",
            product_type=product_type,
            trend_keywords=trend_keywords,
            location_context=location_context,
        )

        return prompt


# =============================================================================
# Main Prompt Optimizer Class
# =============================================================================


class GeminiPromptOptimizer:
    """
    Main prompt optimizer for Gemini native image generation.

    Provides unified interface to all 5 prompt patterns:
    1. Tree of Thoughts for Complex Visuals
    2. Negative Prompting Engine
    3. Collection-Aware Templates
    4. Thinking Mode Constructor
    5. Google Search Grounding
    """

    def __init__(self, brand_injector: BrandContextInjector | None = None):
        """
        Initialize prompt optimizer.

        Args:
            brand_injector: Optional brand context injector for DNA integration
        """
        self.brand_injector = brand_injector or BrandContextInjector()
        logger.info("gemini_prompt_optimizer_initialized")

    def optimize_for_tree_of_thoughts(
        self,
        product_type: str,
        collection: Collection | None = None,
        focus_areas: list[str] | None = None,
        use_case: VisualUseCase = VisualUseCase.CAMPAIGN_IMAGERY,
    ) -> dict[str, str]:
        """
        Optimize prompt using Tree of Thoughts pattern.

        Returns:
            Dict with "prompt" and "negative_prompt" keys
        """
        prompt = GeminiTreeOfThoughtsVisual.create_prompt(
            product_type=product_type,
            collection=collection,
            focus_areas=focus_areas,
            use_case=use_case,
        )

        negative_prompt = GeminiNegativePromptEngine.build_negative_prompt(collection=collection)

        return {"prompt": prompt, "negative_prompt": negative_prompt}

    def optimize_for_product_photography(
        self,
        product_name: str,
        collection: Collection | None = None,
        custom_overrides: dict[str, str] | None = None,
    ) -> dict[str, str]:
        """
        Optimize prompt for product photography.

        Returns:
            Dict with "prompt" and "negative_prompt" keys
        """
        prompt = CollectionPromptBuilder.build_prompt(
            product_name=product_name,
            collection=collection,
            use_case=VisualUseCase.PRODUCT_PHOTOGRAPHY,
            custom_overrides=custom_overrides,
        )

        negative_prompt = GeminiNegativePromptEngine.build_negative_prompt(collection=collection)

        return {"prompt": prompt, "negative_prompt": negative_prompt}

    def optimize_for_thinking_mode(
        self,
        concept: str,
        collection: Collection | None = None,
        complexity_level: str = "moderate",
    ) -> dict[str, str]:
        """
        Optimize prompt for thinking mode (Pro model only).

        Returns:
            Dict with "prompt" and "negative_prompt" keys
        """
        prompt = ThinkingModeConstructor.create_thinking_prompt(
            concept=concept,
            collection=collection,
            complexity_level=complexity_level,
        )

        negative_prompt = GeminiNegativePromptEngine.build_negative_prompt(collection=collection)

        return {"prompt": prompt, "negative_prompt": negative_prompt}

    def optimize_for_search_grounding(
        self,
        product_type: str,
        trend_keywords: list[str] | None = None,
        location_context: str = "Oakland, CA",
        collection: Collection | None = None,
    ) -> dict[str, str]:
        """
        Optimize prompt for Google Search grounding (Pro model only).

        Returns:
            Dict with "prompt" and "negative_prompt" keys
        """
        prompt = GoogleSearchGroundingOptimizer.create_grounded_prompt(
            product_type=product_type,
            trend_keywords=trend_keywords,
            location_context=location_context,
        )

        negative_prompt = GeminiNegativePromptEngine.build_negative_prompt(collection=collection)

        return {"prompt": prompt, "negative_prompt": negative_prompt}
