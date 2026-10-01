"""
Photography direction standards for SkyyRose Elite Studio.

Defines per-style photography standards and garment-specific recommendations
aligned with SkyyRose luxury brand aesthetics.

"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PhotographyStandard:
    """Immutable descriptor for a photography style and its technical directives."""

    style: str
    lighting: str
    background: str
    camera_angle: str
    model_direction: str
    post_processing: str
    fabric_specific_notes: dict[str, str]


# ---------------------------------------------------------------------------
# Photography style catalogue
# ---------------------------------------------------------------------------

_STANDARDS: tuple[PhotographyStandard, ...] = (
    PhotographyStandard(
        style="ecommerce",
        lighting=(
            "Soft, even diffused lighting from two sides at 45 degrees. "
            "Minimal shadows — goal is accurate color and texture representation. "
            "Slight top-front key light to eliminate flat appearance."
        ),
        background="Pure white (#FFFFFF) or light gray (#F5F5F5). No gradients or props.",
        camera_angle=(
            "Straight-on front, eye-level to center of garment. "
            "Back view at same angle. Detail shots at 45-degree close-up."
        ),
        model_direction=(
            "Neutral standing pose, arms slightly away from body to show garment silhouette. "
            "No extreme poses — clarity over drama."
        ),
        post_processing=(
            "Color-accurate to physical product. Minimal retouching. "
            "Fabric texture must remain visible. No liquify or distortion."
        ),
        fabric_specific_notes={
            "sherpa": "Critical: pile texture must be visible — reject flat renders",
            "mesh": "Grid openings must render as semi-transparent, not solid",
            "satin": "Specular highlight must be visible on face; matte reverse at rolled edges",
            "french terry": "Ribbed cuffs and hem must show clear rib structure",
            "fleece": "Brushed nap texture must differentiate from flat cotton",
            "knit": "Rib wale pattern must be visible at neck and cuffs",
        },
    ),
    PhotographyStandard(
        style="editorial",
        lighting=(
            "Dramatic directional lighting — single key from 45-60 degrees. "
            "Deep shadows allowed and encouraged. High contrast to create mood. "
            "Practical lights (candles, neon, street lamps) for scene atmosphere."
        ),
        background=(
            "Environment-specific: urban concrete, brick walls, rooftop cityscape. "
            "SkyyRose collections: Black Rose = dark alleys/night Oakland, "
            "Love Hurts = moody interiors/rain-slicked streets, "
            "Signature = SF Bay Area architecture/golden hour."
        ),
        camera_angle=(
            "Varied — low angles for power, Dutch tilt for tension, wide shots for context. "
            "Product detail inserts at 50mm equivalent to show fabric quality."
        ),
        model_direction=(
            "Emotional, intentional poses. Movement-forward. "
            "Character storytelling over pure product display."
        ),
        post_processing=(
            "Collection-specific color grading. "
            "Black Rose: desaturated with silver and black boost, deep shadows. "
            "Love Hurts: warm crimson tones, high contrast, film grain. "
            "Signature: golden warm grade, soft glow in highlights."
        ),
        fabric_specific_notes={
            "sherpa": "Show pile catching light — creates dramatic texture in directional lighting",
            "satin": "Specular highlights become feature — angle to create flowing light bands",
            "mesh": "Backlit mesh creates halo effect — useful for athletic editorial",
            "french terry": "Weight and structure visible in motion blur or billowing shots",
            "fleece": "Soft texture contrasts beautifully with hard urban environments",
        },
    ),
    PhotographyStandard(
        style="lookbook",
        lighting=(
            "Natural or natural-simulating soft light. "
            "Window light or overcast outdoor. "
            "Warm for Signature, cool-neutral for Black Rose, golden dusk for Love Hurts."
        ),
        background=(
            "Lifestyle environments relevant to each collection. "
            "Black Rose: nighttime Oakland streets, Bay Bridge at night. "
            "Love Hurts: intimate indoor spaces, rain-soaked exterior. "
            "Signature: San Francisco daytime, Golden Gate area, Bay views."
        ),
        camera_angle=(
            "Medium shots showing full outfit context. "
            "Street-style aesthetic — candid-feeling despite being staged."
        ),
        model_direction=(
            "Natural movement — walking, leaning, laughing. "
            "Multiple people for social/community shots. "
            "The luxury of ease — not trying too hard."
        ),
        post_processing=(
            "Light, clean grade preserving natural color. "
            "Preserve fabric texture throughout. "
            "Slight warmth on Signature; slight coolness on Black Rose."
        ),
        fabric_specific_notes={
            "sherpa": "Overhead outdoor shot shows pile texture against sky",
            "cotton": "Natural light renders most accurately — avoid artificial over-brightening",
            "french terry": "Movement shots show drape and weight clearly",
        },
    ),
    PhotographyStandard(
        style="lifestyle",
        lighting=(
            "Ambient and natural. Mixed practical + fill. "
            "Captures real-world wear conditions — indoor ambient, outdoor golden hour."
        ),
        background=(
            "Real-world environments: cafe, city block, gym adjacent, car interior. "
            "SkyyRose community lens: Oakland and SF locations prioritized."
        ),
        camera_angle=(
            "Documentary-style 35mm-equivalent. Context-first framing. "
            "Product visible but not forced."
        ),
        model_direction=(
            "Candid-feeling activity: scrolling phone, holding coffee, laughing mid-walk. "
            "Product is part of life, not the sole focus."
        ),
        post_processing=(
            "Light mobile-style grade — bright, airy or moody depending on collection. "
            "Instagram-optimized aspect ratios. Real skin tones preserved."
        ),
        fabric_specific_notes={
            "mesh": "Movement in lifestyle reveals athletic function",
            "fleece": "Shows packability and casual wear intent",
            "satin": "Even small specular flashes read as premium in casual context",
        },
    ),
    PhotographyStandard(
        style="flat-lay",
        lighting=(
            "Even overhead diffused lighting from above. "
            "No shadows — shoot in diffuse box or against window with reflector below. "
            "Color accuracy is primary goal."
        ),
        background=(
            "Clean surfaces: white marble, dark concrete, branded tissue paper, "
            "raw wood. Collection-appropriate: "
            "Black Rose = dark stone/black velvet, Signature = marble/clean white."
        ),
        camera_angle=(
            "Direct overhead at 90 degrees. "
            "Phone/tablet held perfectly parallel to surface. "
            "No parallax distortion."
        ),
        model_direction="N/A — no model. Garment styled flat with care.",
        post_processing=(
            "Color accurate. Fabric texture preserved. "
            "Minimal background texture competing with garment. "
            "Consistent with product ecommerce colors."
        ),
        fabric_specific_notes={
            "french terry": "Smooth face up; ribbed cuffs folded to show detail",
            "sherpa": "Fluffed pile visible in flat lay — use props to maintain loft",
            "satin": "Arrange to show specular face — avoid showing matte reverse",
            "mesh": "Lay flat against contrasting background to show grid pattern",
            "jersey knit": "Stretch to natural dimensions — avoid bunching",
        },
    ),
)

_STYLE_MAP: dict[str, PhotographyStandard] = {s.style: s for s in _STANDARDS}

# Garment-to-recommended-style mapping
_GARMENT_STYLE_MAP: dict[str, str] = {
    "hoodie": "ecommerce",
    "crewneck": "ecommerce",
    "jersey": "editorial",
    "joggers": "ecommerce",
    "sweatpants": "ecommerce",
    "shorts": "ecommerce",
    "shirt": "ecommerce",
    "jacket": "editorial",
    "varsity jacket": "editorial",
    "beanie": "flat-lay",
    "fanny pack": "flat-lay",
    "set": "lookbook",
}

# Collection-to-preferred-style mapping
_COLLECTION_STYLE_MAP: dict[str, str] = {
    "black-rose": "editorial",
    "love-hurts": "editorial",
    "signature": "lookbook",
    "kids-capsule": "lifestyle",
}


class PhotographyDirector:
    """Photography direction expert for SkyyRose Elite Studio.

    Provides per-style standards, garment recommendations, and fabric
    lighting notes for AI image generation prompts.
    """

    def get_standard(self, style: str) -> PhotographyStandard | None:
        """Return the PhotographyStandard for a named style, or None if unknown."""
        return _STYLE_MAP.get(style.lower())

    def recommend_style(self, garment_type: str, collection: str = "") -> str:
        """Recommend a photography style for a garment, considering collection.

        Collection takes precedence over garment type for editorial collections.
        Falls back to garment default, then 'ecommerce'.
        """
        collection_style = _COLLECTION_STYLE_MAP.get(collection.lower(), "")
        if collection_style:
            # For editorial collections, only override if collection wants editorial
            # but garment normally uses flat-lay (accessories stay flat-lay)
            garment_style = _GARMENT_STYLE_MAP.get(garment_type.lower(), "ecommerce")
            if garment_style == "flat-lay":
                return "flat-lay"
            return collection_style

        return _GARMENT_STYLE_MAP.get(garment_type.lower(), "ecommerce")

    def get_fabric_lighting_notes(self, fabric: str) -> str:
        """Return consolidated fabric lighting notes across all styles."""
        notes: list[str] = []
        for standard in _STANDARDS:
            note = standard.fabric_specific_notes.get(fabric.lower(), "")
            if note:
                notes.append(f"[{standard.style}] {note}")
        return " | ".join(notes) if notes else f"Standard lighting applicable for {fabric}."

    def get_prompt_additions(self, style: str, collection: str = "") -> str:
        """Return photography prompt additions for AI generation."""
        standard = self.get_standard(style)
        if not standard:
            return ""
        parts = [
            f"Lighting: {standard.lighting}",
            f"Background: {standard.background}",
            f"Camera angle: {standard.camera_angle}",
            f"Post-processing: {standard.post_processing}",
        ]
        return "; ".join(parts)

    def list_styles(self) -> list[str]:
        """Return all available photography style names."""
        return list(_STYLE_MAP.keys())
