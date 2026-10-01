"""
Material rendering specifications for SkyyRose Elite Studio.

Fabric-specific AI rendering instructions, texture validation, and prompt
keyword generation. All objects are frozen (immutable).

"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RenderingSpec:
    """Immutable AI rendering specification for a fabric type."""

    fabric: str
    texture_keywords: tuple[str, ...]
    avoid_keywords: tuple[str, ...]
    reference_description: str
    common_ai_errors: tuple[str, ...]


# ---------------------------------------------------------------------------
# Rendering specification catalogue
# ---------------------------------------------------------------------------

_SPECS: tuple[RenderingSpec, ...] = (
    RenderingSpec(
        fabric="sherpa",
        texture_keywords=(
            "dense pile texture",
            "lofted cloud-like surface",
            "visible fiber clusters",
            "deep micro-shadows between fibers",
            "plush three-dimensional pile",
            "heavyweight warmth",
        ),
        avoid_keywords=(
            "flat",
            "smooth",
            "thin",
            "jersey-like",
            "glossy",
            "flat cotton appearance",
        ),
        reference_description=(
            "Thick, densely lofted pile fabric resembling a sheepskin interior. "
            "Individual fiber clusters cast micro-shadows creating visible depth. "
            "Pile profile clearly visible at collar and cuff edges. "
            "Surface has a slightly matte, warm appearance — not synthetic-shiny."
        ),
        common_ai_errors=(
            "Rendering sherpa as flat cotton or jersey knit",
            "Missing pile texture — appears smooth instead of lofted",
            "Over-brightening that flattens the depth of pile clusters",
            "Losing the pile profile at edges and seams",
        ),
    ),
    RenderingSpec(
        fabric="french terry",
        texture_keywords=(
            "smooth knit face",
            "structured hand-feel",
            "visible ribbing at cuffs and hem",
            "soft matte surface",
            "premium knit weight",
            "slight surface variation",
        ),
        avoid_keywords=(
            "shiny",
            "thin tissue-weight",
            "waffle texture",
            "flat synthetic",
            "paper-thin",
        ),
        reference_description=(
            "Premium knit fabric with a smooth face and looped pile on the reverse. "
            "Face is clean and slightly textured — not perfectly smooth like jersey. "
            "Cuffs and hem show distinct rib structure. Weight reads as 280–400gsm — "
            "substantial, structured, premium feel."
        ),
        common_ai_errors=(
            "Rendering french terry as thin jersey knit",
            "Missing ribbed rib structure at cuffs and hem",
            "Over-smoothing the face — should have subtle surface texture",
            "Under-weighting — should look thick and premium, not light",
        ),
    ),
    RenderingSpec(
        fabric="mesh",
        texture_keywords=(
            "open-weave grid pattern",
            "semi-transparent surface",
            "athletic mesh",
            "visible grid holes",
            "breathable open structure",
            "slight synthetic sheen",
        ),
        avoid_keywords=(
            "solid",
            "opaque",
            "flat color",
            "cotton appearance",
            "no texture",
        ),
        reference_description=(
            "Open-hole grid pattern visible throughout fabric. "
            "Mesh is semi-transparent — underlying color or skin slightly visible through holes. "
            "Grid openings are 2–4mm for standard athletic mesh. "
            "Slight synthetic sheen on face — not matte, not high-gloss."
        ),
        common_ai_errors=(
            "Rendering mesh as solid opaque fabric",
            "Missing the open grid hole pattern",
            "No visible semi-transparency through the fabric",
            "Treating mesh like cotton jersey — completely flat",
        ),
    ),
    RenderingSpec(
        fabric="satin",
        texture_keywords=(
            "high-gloss specular highlights",
            "fluid drape",
            "dramatic light reflection",
            "glossy face with matte reverse",
            "sharp highlight ridges on folds",
            "rich color saturation at peaks",
        ),
        avoid_keywords=(
            "matte",
            "flat",
            "cotton-like drape",
            "dull",
            "uniform brightness",
        ),
        reference_description=(
            "High-gloss fabric with liquid-like surface sheen. "
            "Specular highlights appear bright white at peak angles. "
            "Color deepens dramatically in shadow areas. "
            "Folds create sharp bright ridges alternating with deep shadow valleys. "
            "Reverse side is matte and visible at rolled edges."
        ),
        common_ai_errors=(
            "Muting the specular highlights — satin should be dramatically shiny",
            "Uniform brightness across surface — should have high contrast light/shadow",
            "Flat fold rendering — real satin has crisp bright ridges",
            "Not showing matte reverse at edges and openings",
        ),
    ),
    RenderingSpec(
        fabric="fleece",
        texture_keywords=(
            "brushed surface nap",
            "soft pile texture",
            "slight color desaturation from surface fuzz",
            "visible nap at seam edges",
            "warm matte appearance",
        ),
        avoid_keywords=(
            "sherpa-dense",
            "flat cotton",
            "synthetic shiny",
            "smooth",
            "jersey-weight",
        ),
        reference_description=(
            "Brushed fabric with a soft, slightly fuzzy surface nap. "
            "Lighter and less structured than sherpa — nap is finer and less lofted. "
            "Colors appear slightly softer/more muted due to surface fuzz. "
            "Visible texture at seam edges and folds. Weight: 200–400gsm."
        ),
        common_ai_errors=(
            "Confusing fleece with sherpa — fleece has lighter, finer nap",
            "Over-smoothing — surface fuzz is a key texture cue",
            "Making fleece too shiny — it's a warm matte fabric",
        ),
    ),
    RenderingSpec(
        fabric="jersey knit",
        texture_keywords=(
            "fine smooth knit surface",
            "subtle horizontal rib structure",
            "soft drape",
            "slight stretch visible",
            "clean uniform face",
        ),
        avoid_keywords=(
            "thick",
            "rough",
            "woven texture",
            "sherpa pile",
            "heavy weight appearance",
        ),
        reference_description=(
            "Fine single-jersey knit with clean, smooth face. "
            "Subtle horizontal rib structure visible up close. "
            "Softer drape than french terry — lightweight, excellent stretch. "
            "Athletic feel — clean and performance-oriented."
        ),
        common_ai_errors=(
            "Rendering jersey knit with heavy french terry weight",
            "Over-texturing — jersey should be cleaner than terry",
            "Losing the subtle horizontal rib structure at close range",
        ),
    ),
    RenderingSpec(
        fabric="cotton",
        texture_keywords=(
            "matte surface",
            "natural hand-feel",
            "slight natural fiber variation",
            "relaxed drape",
            "clean flat face",
        ),
        avoid_keywords=(
            "shiny",
            "synthetic",
            "napped texture",
            "lofted pile",
            "stiff",
        ),
        reference_description=(
            "Clean, matte cotton surface without specular highlights. "
            "Natural fiber variation creates slight texture difference vs synthetic. "
            "Relaxed drape with natural wrinkle folds. "
            "Weight: 140–200gsm — not paper-thin, not premium heavy."
        ),
        common_ai_errors=(
            "Adding synthetic sheen — cotton is matte",
            "Over-textured surface — standard cotton is relatively clean",
            "Under-weighting for premium SkyyRose cotton — should look quality",
        ),
    ),
)

_SPEC_MAP: dict[str, RenderingSpec] = {s.fabric: s for s in _SPECS}

# Fabric aliases
_FABRIC_ALIASES: dict[str, str] = {
    "terry": "french terry",
    "french-terry": "french terry",
    "athletic mesh": "mesh",
    "polyester mesh": "mesh",
    "fleece fabric": "fleece",
    "sherpa fleece": "sherpa",
    "satin fabric": "satin",
    "jersey": "jersey knit",
    "cotton jersey": "jersey knit",
    "knit": "jersey knit",
}


class MaterialsExpert:
    """Material rendering expert for SkyyRose Elite Studio.

    Provides AI-ready rendering specifications, texture validation guidance,
    and prompt keyword extraction for each fabric type.
    """

    def get_rendering_spec(self, fabric: str) -> RenderingSpec | None:
        """Return rendering spec for a fabric type.

        Resolves aliases. Returns None for unrecognized fabrics.
        """
        normalized = fabric.lower().strip()
        resolved = _FABRIC_ALIASES.get(normalized, normalized)
        return _SPEC_MAP.get(resolved)

    def validate_texture(self, fabric: str, image_description: str) -> bool:
        """Validate that an image description indicates correct texture for a fabric.

        Checks that texture keywords are present and avoid keywords are absent.
        Uses simple substring matching — suitable for LLM-generated descriptions.
        """
        spec = self.get_rendering_spec(fabric)
        if not spec:
            return True  # Unknown fabric — pass by default

        desc_lower = image_description.lower()

        # Check for avoid keywords — any hit = fail
        for avoid in spec.avoid_keywords:
            if avoid.lower() in desc_lower:
                return False

        # Check for at least one texture keyword — need at least one hit
        texture_hits = sum(1 for kw in spec.texture_keywords if kw.lower() in desc_lower)
        return texture_hits >= 1

    def get_prompt_keywords(self, fabric: str) -> tuple[str, ...]:
        """Return texture prompt keywords for a fabric type.

        Returns empty tuple for unrecognized fabrics.
        """
        spec = self.get_rendering_spec(fabric)
        if spec:
            return spec.texture_keywords
        return ()

    def get_avoid_keywords(self, fabric: str) -> tuple[str, ...]:
        """Return keywords to avoid in generation prompts for a fabric.

        Returns empty tuple for unrecognized fabrics.
        """
        spec = self.get_rendering_spec(fabric)
        if spec:
            return spec.avoid_keywords
        return ()

    def get_error_warnings(self, fabric: str) -> tuple[str, ...]:
        """Return common AI rendering errors for a fabric type."""
        spec = self.get_rendering_spec(fabric)
        if spec:
            return spec.common_ai_errors
        return ()

    def list_fabrics(self) -> list[str]:
        """Return all fabric types with registered rendering specs."""
        return list(_SPEC_MAP.keys())

    def build_texture_prompt_segment(self, fabric: str) -> str:
        """Build a concise texture description segment for AI generation prompts."""
        spec = self.get_rendering_spec(fabric)
        if not spec:
            return ""
        keywords = ", ".join(spec.texture_keywords[:4])
        avoids = ", ".join(f"NOT {kw}" for kw in spec.avoid_keywords[:2])
        return f"Fabric texture: {keywords}. {avoids}."
