# services/ml/prompts/vision_prompts.py
"""Vision model prompts for image-to-description pipeline.

Implements US-029: Image-to-description pipeline.

Author: DevSkyy Platform Team
Version: 1.0.0
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.ml.schemas.description import DescriptionStyle, ProductType


# =============================================================================
# Feature Extraction Prompt
# =============================================================================

FEATURE_EXTRACTION_PROMPT = """Analyze this product image and extract the following visual features in JSON format:

1. **Colors**: List all colors visible, including:
   - name: Descriptive color name (e.g., "charcoal black", "rose gold")
   - category: neutral/warm/cool
   - prominence: 0.0-1.0 (how prominent in the image)

2. **Materials**: Identify visible materials:
   - name: Material name (e.g., "premium cotton", "genuine leather")
   - texture: Texture description (e.g., "smooth", "textured", "matte")
   - quality_indicator: luxury/premium/standard

3. **Style Attributes**:
   - aesthetic: Overall aesthetic (minimalist, bold, classic, avant-garde, etc.)
   - mood: Mood conveyed (sophisticated, casual, edgy, romantic, etc.)
   - occasion: Suitable occasions (everyday, formal, evening, special event)
   - season: Suitable seasons (spring, summer, fall, winter, all-season)

4. **Detected Elements**: List visible elements (buttons, zippers, embroidery, patterns, etc.)

Respond ONLY with valid JSON in this exact format:
{
  "colors": [{"name": "", "category": "", "prominence": 0.0}],
  "materials": [{"name": "", "texture": "", "quality_indicator": ""}],
  "style": {"aesthetic": "", "mood": "", "occasion": [], "season": []},
  "detected_elements": []
}"""


# =============================================================================
# Description Prompts by Style
# =============================================================================

DESCRIPTION_PROMPTS: dict[str, str] = {
    "luxury": """You are a luxury fashion copywriter for SkyyRose, a high-end fashion brand.

Analyze this product image and write a compelling product description that:
- Evokes emotion and desire
- Highlights craftsmanship and quality
- Uses sensory language (touch, feel, movement)
- Maintains an air of exclusivity
- Targets affluent, style-conscious consumers

Brand Voice: Sophisticated, bold, romantic, Oakland-inspired luxury.

Write a {word_count}-word description for this {product_type}.
{brand_context}

Focus on:
1. The silhouette and fit
2. Material quality and texture
3. Unique design elements
4. How it makes the wearer feel
5. Styling possibilities

Do NOT mention specific prices. Do NOT use generic phrases like "high-quality" without specifics.""",
    "casual": """You are a friendly fashion copywriter.

Analyze this product image and write an approachable product description that:
- Feels conversational and relatable
- Highlights comfort and versatility
- Emphasizes everyday wearability
- Uses clear, simple language

Write a {word_count}-word description for this {product_type}.
{brand_context}

Focus on practical benefits and how it fits into daily life.""",
    "technical": """You are a technical fashion writer.

Analyze this product image and write a detailed product description that:
- Lists specific materials and construction
- Provides precise measurements/fit information
- Describes care instructions
- Uses industry-standard terminology

Write a {word_count}-word description for this {product_type}.
{brand_context}

Be precise and factual. Avoid marketing language.""",
    "minimal": """Analyze this product image and write a concise, minimal product description.

Style: Clean, essential, no fluff.
Length: {word_count} words maximum.
Product type: {product_type}
{brand_context}

Focus only on what matters: silhouette, material, color, key feature.""",
    "storytelling": """You are a narrative fashion writer for SkyyRose.

Analyze this product image and craft a story-driven product description that:
- Creates a narrative around the piece
- Imagines the woman who wears it
- Evokes a specific moment or feeling
- Weaves in brand heritage

Brand: SkyyRose - Oakland-inspired luxury fashion.

Write a {word_count}-word narrative description for this {product_type}.
{brand_context}

Make the reader see themselves in the story.""",
}


# =============================================================================
# Bullet Points Prompt
# =============================================================================

BULLET_POINTS_PROMPT = """Based on the product image, generate 5-7 bullet points for the product listing.

Each bullet point should be:
- Concise (under 15 words)
- Feature-focused
- Customer-benefit oriented

Categories to cover:
- Material/fabric composition
- Fit and silhouette
- Special features (pockets, closures, details)
- Care instructions (if determinable)
- Styling suggestions

Format each bullet as:
CATEGORY: Bullet point text

Example:
MATERIAL: Premium heavyweight cotton with a soft, brushed interior
FIT: Relaxed oversized silhouette for effortless layering
FEATURE: Hidden interior pocket for secure storage"""


# =============================================================================
# SEO Prompt
# =============================================================================

SEO_PROMPT = """Analyze this product image and generate SEO content.

Generate:
1. **SEO Title** (under 60 characters): Include product type and key attribute
2. **Meta Description** (under 160 characters): Compelling summary with call-to-action
3. **Focus Keyword**: Primary search term to target
4. **Secondary Keywords**: 3-5 related search terms

Consider:
- Search intent (what would someone search to find this?)
- Competitor keywords
- Long-tail opportunities

Product type: {product_type}
{brand_context}

Format response as JSON:
{{
  "title": "",
  "meta_description": "",
  "focus_keyword": "",
  "secondary_keywords": []
}}"""


# =============================================================================
# Tags Prompt
# =============================================================================

TAGS_PROMPT = """Analyze this product image and generate relevant tags for categorization and search.

Generate 10-15 tags including:
- Product category (dress, top, jacket, etc.)
- Style descriptors (minimalist, bold, romantic, etc.)
- Occasion tags (casual, formal, evening, etc.)
- Season tags (summer, winter, all-season, etc.)
- Color tags
- Material tags
- Trend tags (if applicable)

Return as a comma-separated list of lowercase tags.
Example: black dress, midi length, evening wear, formal, elegant, silk, minimalist, date night"""


# =============================================================================
# Helper Functions
# =============================================================================


def get_description_prompt(
    style: DescriptionStyle,
    product_type: ProductType,
    word_count: int,
    brand_context: str | None = None,
) -> str:
    """Get formatted description prompt for given style.

    Args:
        style: Writing style to use
        product_type: Type of product being described
        word_count: Target word count
        brand_context: Optional brand-specific context

    Returns:
        Formatted prompt string
    """
    template = DESCRIPTION_PROMPTS.get(style.value, DESCRIPTION_PROMPTS["luxury"])

    context_str = f"\nAdditional brand context: {brand_context}" if brand_context else ""

    return template.format(
        word_count=word_count,
        product_type=product_type.value,
        brand_context=context_str,
    )


def get_feature_prompt() -> str:
    """Get the feature extraction prompt.

    Returns:
        Feature extraction prompt string
    """
    return FEATURE_EXTRACTION_PROMPT
