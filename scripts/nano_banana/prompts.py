"""Prompt templates and logo treatment metadata.

All prompts take product dict so the model knows EXACTLY what garment
it's rendering, which collection it belongs to, and what branding to expect.

Brand DNA: SkyyRose is Oakland luxury streetwear. Dark, cinematic, raw.
Not generic e-commerce — every render should feel editorial.
"""

from __future__ import annotations

import logging
from pathlib import Path

log = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# -- Anti-hallucination constraints (appended to every prompt) ----------------

ANTI_HALLUCINATION = (
    "\n\nSTRICT RULES — NON-NEGOTIABLE:\n"
    "- FIDELITY: Only reproduce what is visible in the reference photo AND listed in the REQUIRED BRANDING section above. Nothing else.\n"
    "- TEXT MUST BE CHARACTER-PERFECT: Every letter, number, and symbol must be spelled EXACTLY as shown in the reference or REQUIRED BRANDING. "
    "No missing letters. No extra letters. No garbled glyphs. No substituted characters. No mirrored or flipped text. "
    "If the reference or spec says 'BLACK IS BEAUTIFUL', the output MUST show 'BLACK IS BEAUTIFUL' — not 'BLACK S BEAUTIFUL', not 'BLACK IS BEADTIFUL', not 'GEDDIFUL'. "
    "If you cannot render a word legibly and accurately, DO NOT render the image — return blank rather than produce misspelled text.\n"
    "- DO NOT INVENT TEXT: Do not add any word, brand name, number, or phrase not in the reference or REQUIRED BRANDING. No placeholder lorem ipsum, no made-up taglines.\n"
    "- DO NOT INVENT GRAPHICS: Do not add logos, patches, roses, embroidery, or designs not in the reference or REQUIRED BRANDING.\n"
    "- PATCH / BADGE PLACEMENT IS MANDATORY: If REQUIRED BRANDING names a patch, badge, or logo with a specific location (e.g. 'bottom left', 'upper-right chest', 'below waistband'), that element MUST appear in the output, in EXACTLY that position, at the specified size. "
    "Do NOT move it, mirror it, center it, duplicate it, or omit it. A jersey without its woven patch is a FAIL.\n"
    "- GARMENT INTEGRITY: Do not change garment type, silhouette, cut, or colors. Match the reference hex values exactly.\n"
    "- VIEW LOCK: Render ONLY the side specified (front or back). Never show both.\n"
    "- CONFLICT RESOLUTION: If the reference photo and REQUIRED BRANDING disagree on a detail, trust REQUIRED BRANDING (it is the spec of record). If both are unclear, leave the detail out — never guess.\n"
)

ENHANCED_SUFFIX = (
    " CRITICAL: Copy the reference photo exactly. "
    "Preserve every pixel of color, pattern, design element, text character, logo, and patch. "
    "All text must be character-perfect (spelling, case, kerning). "
    "All patches and badges must appear at the exact location and size specified."
    + ANTI_HALLUCINATION
)

# -- Collection lighting profiles --------------------------------------------
# Each collection has a distinct visual identity that shows even in flat shots.

COLLECTION_LIGHTING = {
    "black-rose": {
        "bg": "Deep matte black (#0A0A0A) backdrop with subtle charcoal gradient",
        "light": "Cool silver key light from upper-left, black fill, thin silver rim light creating metallic edge highlights",
        "mood": "Dark, authoritative, monochrome luxury — the garment commands the frame",
        "shadow": "Deep pooling shadow beneath, barely visible floor plane",
    },
    "love-hurts": {
        "bg": "Rich black (#0A0A0A) backdrop with barely perceptible crimson warmth in the shadows",
        "light": "Warm dramatic key light upper-left with subtle crimson gel, dark fill, strong rim light for edge separation",
        "mood": "Emotionally charged, intimate, the fabric tells a story",
        "shadow": "Soft directional shadow, warm-toned edges",
    },
    "signature": {
        "bg": "Warm charcoal (#1A1A1A) fading to deep black, hint of golden hour warmth",
        "light": "Golden-warm key light upper-left, soft neutral fill, warm rim light creating a premium glow",
        "mood": "Refined, approachable luxury — the everyday elevated",
        "shadow": "Clean soft shadow, subtle warm floor reflection",
    },
    "kids-capsule": {
        "bg": "Clean dark gray (#1C1C1C) with subtle warmth",
        "light": "Bright but not flat — angled key light, soft fill, playful rim highlights",
        "mood": "Premium and confident — scaled down, never dumbed down",
        "shadow": "Crisp shadow, energetic composition",
    },
}


# -- View prompts -------------------------------------------------------------


def _branding_block(treatment: str) -> str:
    """Format the REQUIRED BRANDING section injected into view prompts."""
    if not treatment:
        return ""
    return (
        f"\n\n═══ REQUIRED BRANDING (MANDATORY — must appear exactly as specified) ═══\n"
        f"{treatment}\n"
        f"Every element above MUST be rendered in the output. Any patch, badge, text, "
        f"or logo named here must appear at the specified location, at the specified size, "
        f"with text spelled character-perfect. This is non-negotiable.\n"
    )


def front_prompt(product: dict) -> str:
    """Build a front-view product shot prompt with collection-specific styling."""
    name = product["name"]
    collection = product["collection"]
    sku = product.get("sku", "")
    lighting = COLLECTION_LIGHTING.get(collection, COLLECTION_LIGHTING["black-rose"])
    treatment = LOGO_TREATMENTS.get(sku, "")

    return (
        f"Generate a photorealistic product render of this garment — FRONT VIEW ONLY.\n"
        f"The provided photo is the ONLY reference. Copy it exactly.\n\n"
        f"VIEW: Front panel only.\n\n"
        f"PRESENTATION:\n"
        f"- No model, no person, no mannequin. Garment floating on invisible form with natural drape.\n"
        f"- {lighting['bg']}.\n"
        f"- {lighting['light']}.\n"
        f"- {lighting['shadow']}.\n"
        f"- Photorealistic fabric texture.\n\n"
        f"FIDELITY: Copy the reference photo exactly. Same colors, same graphics, same construction."
        f"{_branding_block(treatment)}" + ANTI_HALLUCINATION
    )


def back_prompt(product: dict) -> str:
    """Build a back-view product shot prompt with collection-specific styling."""
    name = product["name"]
    collection = product["collection"]
    sku = product.get("sku", "")
    lighting = COLLECTION_LIGHTING.get(collection, COLLECTION_LIGHTING["black-rose"])
    treatment = LOGO_TREATMENTS.get(sku, "")

    return (
        f"Generate a photorealistic product render of this garment — BACK VIEW ONLY.\n"
        f"The provided photo is the ONLY reference. Copy it exactly.\n\n"
        f"VIEW: Back panel only. Garment facing away from camera.\n\n"
        f"PRESENTATION:\n"
        f"- No model, no person, no mannequin. Garment floating on invisible form, back-facing, natural drape.\n"
        f"- {lighting['bg']}.\n"
        f"- {lighting['light']}.\n"
        f"- Photorealistic fabric texture.\n\n"
        f"FIDELITY: Copy the reference photo exactly."
        f"{_branding_block(treatment)}" + ANTI_HALLUCINATION
    )


def accessory_prompt(product: dict) -> str:
    """Build a prompt for accessories (beanies, fanny packs, etc.)."""
    name = product["name"]
    collection = product["collection"]
    sku = product.get("sku", "")
    lighting = COLLECTION_LIGHTING.get(collection, COLLECTION_LIGHTING["signature"])
    treatment = LOGO_TREATMENTS.get(sku, "")

    return (
        f"Generate a photorealistic product render of this accessory — HERO ANGLE.\n"
        f"The provided photo is the ONLY reference. Copy it exactly.\n\n"
        f"PRESENTATION:\n"
        f"- No model. Product only, slightly angled for dimension.\n"
        f"- {lighting['bg']}.\n"
        f"- {lighting['light']}.\n"
        f"- Tight framing — the accessory fills the frame.\n\n"
        f"FIDELITY: Copy the reference photo exactly."
        f"{_branding_block(treatment)}" + ANTI_HALLUCINATION
    )


# -- Branding (lifestyle) prompts per collection ------------------------------
# These are editorial shots — models wearing the product in a brand-aligned environment.
# The key is OAKLAND AUTHENTICITY, not generic fashion photography.

BRANDING_TEMPLATES = {
    "black-rose": (
        "The reference image shows a {name}. Generate a fashion editorial photo:\n\n"
        "MODEL: Confident, diverse model wearing this EXACT {name}. The garment must be "
        "100%% identical to the reference — every logo, color, panel, stitch.\n\n"
        "SETTING: Oakland industrial — concrete walls, steel beams, raw textures. "
        "Night. The only light is silver-toned spotlights carving the model from darkness. "
        "LIGHTING: Dramatic chiaroscuro. Hard silver key light, deep black shadows. "
        "No color — only silver (#C0C0C0) tones. The darkness is the point.\n\n"
        "MOOD: Quiet authority. This person doesn't announce themselves — they command "
        "presence the way Oakland taught them. Unshakable.\n\n"
        "COMPOSITION: 3/4 body shot, cinematic aspect ratio. "
        "Slight dutch angle. Film grain. The garment is the hero.{treatment_note}"
    ),
    "love-hurts": (
        "The reference image shows a {name}. Generate a fashion editorial photo:\n\n"
        "MODEL: Confident, diverse model wearing this EXACT {name}. The garment must be "
        "100%% identical to the reference.\n\n"
        "SETTING: Raw emotional space — cracked concrete, weathered brick, "
        "a single red neon glow in the background. Oakland at 2 AM. "
        "This collection is named after the founder's family name — it's personal.\n\n"
        "LIGHTING: Warm dramatic — deep crimson (#DC143C) accent light from one side, "
        "hard shadows on the other. The light catches the branding. Vulnerable but strong.\n\n"
        "MOOD: Pain transformed into beauty. Vulnerability as strength. "
        "The model wears their scars like armor.\n\n"
        "COMPOSITION: 3/4 body, cinematic. Close enough to see the fabric. "
        "The emotion is in the details.{treatment_note}"
    ),
    "signature": (
        "The reference image shows a {name}. Generate a fashion editorial photo:\n\n"
        "MODEL: Confident, diverse model wearing this EXACT {name}. The garment must be "
        "100%% identical to the reference.\n\n"
        "SETTING: Oakland golden hour — Bay Bridge or city skyline in soft focus background. "
        "Warm pavement, late afternoon sun. This is where it all started — a father "
        "with a daughter's name and a refusal to quit.\n\n"
        "LIGHTING: Golden hour warmth — rich amber key light, soft gold (#D4AF37) tones. "
        "Natural, elevated, the everyday made extraordinary.\n\n"
        "MOOD: Understated confidence. Not shouting — just built different. "
        "The foundation wardrobe for someone who already knows who they are.\n\n"
        "COMPOSITION: 3/4 body, warm cinematic. Bay Area light. "
        "The gold in the fabric catches the sun.{treatment_note}"
    ),
    "kids-capsule": (
        "The reference image shows a {name}. Generate a fashion editorial photo:\n\n"
        "MODEL: CHILD model (age 8-12) wearing this EXACT {name}. 100%% identical "
        "to reference. This child carries themselves with confidence.\n\n"
        "SETTING: Clean Oakland street — mural wall or playground with premium feel. "
        "No pastels, no cartoons. Real streetwear scaled down, not dumbed down.\n\n"
        "LIGHTING: Bright but cinematic — the child stands in a pool of warm light. "
        "Premium energy, playful confidence.\n\n"
        "MOOD: Legacy. This brand is named after the founder's daughter, Skyy Rose. "
        "Kids Capsule is the promise made real.\n\n"
        "COMPOSITION: 3/4 body, eye-level with the child. Respectful, powerful.{treatment_note}"
    ),
}

ACCESSORY_BRANDING_TEMPLATES = {
    "love-hurts": (
        "The reference image shows a {name}. Display this EXACT {name} in a "
        "moody Oakland editorial — cracked concrete surface, single crimson accent light, "
        "deep shadows. Raw emotion. 100%% identical to reference. "
        "Cinematic product photography. The accessory tells the story.{treatment_note}"
    ),
    "signature": (
        "The reference image shows a {name}. Display this EXACT {name} in a "
        "golden hour Oakland editorial — warm pavement, Bay Area light, subtle gold tones. "
        "100%% identical to reference. Premium product photography. "
        "Everyday luxury.{treatment_note}"
    ),
}


# -- Composite prompts --------------------------------------------------------


def composite_prompt(name: str, sku: str, view: str = "front") -> str:
    """Build a prompt for compositing real branding onto an AI lifestyle shot."""
    treatment = LOGO_TREATMENTS.get(sku, "")
    treatment_note = f" The real product's logo/branding is {treatment}." if treatment else ""
    return (
        f"I am providing TWO images. "
        f"IMAGE 1 (the AI render): A professional fashion photo of a model wearing a {name}. "
        f"Keep this composition, pose, lighting, and background. "
        f"IMAGE 2 (the REAL product): The actual {name} showing the TRUE logo.{treatment_note} "
        f"YOUR TASK: Generate a new image keeping the EXACT same model, pose, and background "
        f"from Image 1 — but correct the garment's logo/branding to match Image 2 exactly. "
        f"Study the logo closely: light interaction, shadows, raised/flat, glossy/matte finish. "
        f"Reproduce these visual properties exactly. Only the garment branding changes."
    )


# -- FLUX prompts (text-to-image, no reference) -------------------------------


def flux_prompt(name: str, view: str, source_desc: str = "") -> str:
    """Build a FLUX prompt for converting tech flats to photorealistic shots."""
    view_label = {
        "front": "FRONT VIEW",
        "back": "BACK VIEW",
        "branding": "cinematic editorial shot",
    }.get(view, "FRONT VIEW")

    base = f"Professional luxury product photography of a {name} on invisible ghost mannequin, {view_label}. "
    if source_desc:
        base += f"{source_desc} "

    if "branding" in view:
        base += (
            "Oakland industrial setting — concrete walls, dramatic silver spotlights, "
            "deep black shadows. Gothic luxury. Cinematic composition, slight floor reflection. "
        )
    else:
        base += (
            "Deep matte black (#0A0A0A) studio background. "
            "Silver key light upper-left, dark fill, thin rim light for metallic edge highlights. "
            "Luxury fashion photography — the garment commands the frame. "
        )

    base += "Photorealistic fabric texture with natural 3D shape and drape. All text and logos perfectly legible."
    return base


# -- Prompt router ------------------------------------------------------------


def get_prompt(product: dict, view: str) -> str:
    """Select the right prompt for a product + view combination."""
    name = product["name"]
    collection = product["collection"]
    sku = product.get("sku", "")
    is_accessory = product.get("is_accessory", False)

    if view == "branding":
        treatment = LOGO_TREATMENTS.get(sku, "")
        treatment_note = f"\n\nBRANDING TO PRESERVE: {treatment}" if treatment else ""

        if is_accessory:
            tpl = ACCESSORY_BRANDING_TEMPLATES.get(
                collection,
                BRANDING_TEMPLATES.get(collection, BRANDING_TEMPLATES["black-rose"]),
            )
            return tpl.format(name=name, treatment_note=treatment_note) + ANTI_HALLUCINATION
        tpl = BRANDING_TEMPLATES.get(collection, BRANDING_TEMPLATES["black-rose"])
        return tpl.format(name=name, treatment_note=treatment_note) + ANTI_HALLUCINATION

    if is_accessory:
        return accessory_prompt(product)
    if view == "front":
        return front_prompt(product)
    return back_prompt(product)


# -- Logo treatment metadata --------------------------------------------------
# Loaded from data/product-specs.json — the SINGLE SOURCE OF TRUTH.
# Do NOT hardcode branding here. Edit product-specs.json instead.


def _load_logo_treatments() -> dict[str, str]:
    """Load branding specs from the canonical product-specs.json."""
    specs_path = PROJECT_ROOT / "data" / "product-specs.json"
    if not specs_path.exists():
        log.warning("product-specs.json not found at %s", specs_path)
        return {}
    import json

    data = json.loads(specs_path.read_text())
    return {
        sku: entry.get("branding", "")
        for sku, entry in data.get("products", {}).items()
        if entry.get("branding")
    }


LOGO_TREATMENTS = _load_logo_treatments()
