"""SkyyRose JSON scene schema for gpt-image-2 render pipeline.

Defines structured scene descriptions that are injected into prompts AFTER the
PRODUCT line and BEFORE the REFERENCE IMAGES section in build_prompt().

Schema keys:
    subject     — garment + model description
    model       — human subject descriptor and pose
    environment — physical setting
    lighting    — key/fill/accent light sources
    camera      — lens, aperture, angle, depth_of_field
    style       — photographic style descriptor
    mood        — emotional / atmospheric tone
    color_palette — hex list anchored on brand tokens
    constraints — always-on guardrails (never blank, no watermark, etc.)
"""

from __future__ import annotations

from .prompt import SceneError

# ---------------------------------------------------------------------------
# Ghost / flatlay studio defaults
# ---------------------------------------------------------------------------

_GHOST_LIGHTING: dict[str, str] = {
    "key": "large softbox 45° camera-left, diffused",
    "fill": "white bounce card camera-right, 1:3 ratio",
    "accent": "rim light rear-left, subtle separation",
}

_GHOST_CAMERA: dict[str, str | float] = {
    "lens": "85mm portrait",
    "aperture": "f/8",
    "angle": "straight-on eye-level",
    "depth_of_field": "full garment sharp, background soft",
}

# Flatlay is a top-down shot — its camera angle MUST match the flatlay
# PRESENTATION ("laid flat, top-down"); reusing the ghost eye-level camera would
# contradict it inside the same prompt.
_FLATLAY_CAMERA: dict[str, str | float] = {
    "lens": "50mm",
    "aperture": "f/8",
    "angle": "top-down overhead, lens perpendicular to the surface",
    "depth_of_field": "entire garment evenly sharp",
}

_GHOST_ENVIRONMENT: str = "seamless studio cyclorama"

# ---------------------------------------------------------------------------
# On-model per-collection defaults  (keyed by collection slug)
# ---------------------------------------------------------------------------

_ONMODEL_DEFAULTS: dict[str, dict[str, object]] = {
    "signature": {
        "environment": "Golden Gate Bridge and Bay Area skyline at golden hour, confident West-Coast street-luxury energy, warm sunlight",
        "lighting": {
            "key": "warm golden-hour sun, high-right",
            "fill": "open sky fill, soft shadow",
            "accent": "specular rim from reflective concrete",
        },
        "camera": {
            "lens": "85mm",
            "aperture": "f/2.8",
            "angle": "slightly low, looking up",
            "depth_of_field": "subject sharp, background bokeh",
        },
        "film_stock": "Kodak Portra 400",
        "color_palette": ["#D4AF37", "#B76E79", "#0A0A0A", "#F5E6C8"],
        "mood": "aspirational, grounded luxury, effortless swag",
    },
    "black-rose": {
        "environment": "Oakland shoreline at blue hour, Bay Bridge silhouetted behind, moody black-rose garden with roses in deep shadow",
        "lighting": {
            "key": "dramatic blue-hour ambient, deep shadow",
            "fill": "minimal fill, dark romantic low light",
            "accent": "rim from city lights across the bay",
        },
        "camera": {
            "lens": "50mm",
            "aperture": "f/4",
            "angle": "straight-on, slight upward tilt",
            "depth_of_field": "full body sharp, dark BG",
        },
        "film_stock": "Kodak Portra 800",
        "color_palette": ["#C0C0C0", "#B76E79", "#0A0A0A", "#1A1A1A"],
        "mood": "dark romantic luxury, armor, defiance",
    },
    "love-hurts": {
        "environment": "candlelit gothic château interior, ornate and brooding, shadow-heavy — Beauty-and-the-Beast setting from the Beast's point of view",
        "lighting": {
            "key": "candlelight, warm and directional, low",
            "fill": "deep shadow, emotionally intense",
            "accent": "subtle rim from distant candelabra",
        },
        "camera": {
            "lens": "35mm",
            "aperture": "f/2.0",
            "angle": "hip-level, slight Dutch tilt",
            "depth_of_field": "mid-body sharp, foreground soft",
        },
        "film_stock": "Kodak Portra 800",
        "color_palette": ["#DC143C", "#B76E79", "#0A0A0A", "#8B0000"],
        "mood": "dark romance, brooding intensity, emotionally raw",
    },
    "kids-capsule": {
        "environment": "opulent throne room, gold-and-velvet palace setting, heir to the throne — playful young-royalty grandeur",
        "lighting": {
            "key": "warm cinematic overhead, regal and theatrical",
            "fill": "reflected gold from velvet drapery",
            "accent": "crown highlight, soft and warm",
        },
        "camera": {
            "lens": "50mm",
            "aperture": "f/5.6",
            "angle": "eye-level to child subject",
            "depth_of_field": "subject sharp, background soft",
        },
        "film_stock": "Kodak Ektar 100",
        "color_palette": ["#B76E79", "#D4AF37", "#F5C6CB", "#FFFFFF"],
        "mood": "playful royalty, joyful grandeur, family warmth",
    },
}

# ---------------------------------------------------------------------------
# Always-on constraints
# ---------------------------------------------------------------------------

_CONSTRAINTS: dict[str, object] = {
    "no_text_overlays": True,
    "no_watermarks": True,
    "no_mannequin_visible": True,
    "seamless_background_required": True,
    "garment_must_be_protagonist": True,
    "brand": "SkyyRose",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_scene(
    sku: str,
    name: str,
    collection: str,
    style: str,
    *,
    garment_color: str | None = None,
    garment_details: str | None = None,
) -> dict:
    """Return a fresh scene dict for the given SKU and style.

    Parameters
    ----------
    sku:             Product SKU (e.g. "br-001").
    name:            Sanitized garment name (e.g. "The Black Rose Varsity").
    collection:      Collection slug (e.g. "black-rose").
    style:           Render style key — "ghost" or "flatlay" → clean studio
                     (no model); any other value → on-model editorial.
    garment_color:   Primary garment colorway if known (optional).
    garment_details: Brief garment description for subject field (optional).

    Returns
    -------
    dict following the SkyyRose scene schema. Always a new object; no shared
    state with module-level constants.

    Raises
    ------
    SceneError: for an on-model render of a collection with no defined scene —
                mirrors prompt._background_for; never silently substitutes one.
    """
    color_desc = garment_color or "as shown in references"
    details_desc = garment_details or name

    if style in ("ghost", "flatlay"):
        is_flatlay = style == "flatlay"
        return {
            "subject": {
                "type": "flatlay" if is_flatlay else "ghost-mannequin",
                "garment": details_desc,
                "color": color_desc,
                "sku": sku,
            },
            "model": None,
            "environment": _GHOST_ENVIRONMENT,
            "lighting": dict(_GHOST_LIGHTING),
            "camera": dict(_FLATLAY_CAMERA if is_flatlay else _GHOST_CAMERA),
            "style": "clean commercial product photography",
            "mood": "precise, editorial, luxury retail",
            "color_palette": ["#B76E79", "#FFFFFF", "#0A0A0A"],
            "constraints": dict(_CONSTRAINTS),
        }

    col_key = collection.lower()
    defaults = _ONMODEL_DEFAULTS.get(col_key)
    if defaults is None:
        raise SceneError(
            f"No on-model scene for collection {collection!r}; refusing a generic "
            f"fallback. Add it to _ONMODEL_DEFAULTS. Known: {sorted(_ONMODEL_DEFAULTS)}"
        )

    return {
        "subject": {
            "type": "on-model",
            "garment": details_desc,
            "color": color_desc,
            "sku": sku,
        },
        "model": {
            "descriptor": "professional fashion model, confident pose",
            "pose": "full-body editorial stance",
            "expression": "intense, aspirational",
        },
        "environment": defaults["environment"],
        "lighting": dict(defaults["lighting"]),  # type: ignore[arg-type]
        "camera": dict(defaults["camera"]),  # type: ignore[arg-type]
        "style": f"editorial fashion photography, {defaults.get('film_stock', 'natural')}",
        "mood": defaults["mood"],
        "color_palette": list(defaults["color_palette"]),  # type: ignore[arg-type]
        "constraints": dict(_CONSTRAINTS),
    }


def scene_to_prompt_block(scene: dict) -> str:
    """Serialize a scene dict to a prompt injection string.

    The returned block is designed to be inserted between the PRODUCT line and
    the REFERENCE IMAGES section in build_prompt().

    Parameters
    ----------
    scene: dict produced by build_scene().

    Returns
    -------
    Multi-line string beginning with "SCENE SPEC (JSON):".
    """
    import json

    lines = ["SCENE SPEC (JSON) — photograph this scene exactly:"]
    lines.append(json.dumps(scene, indent=2, ensure_ascii=False))
    return "\n".join(lines)
