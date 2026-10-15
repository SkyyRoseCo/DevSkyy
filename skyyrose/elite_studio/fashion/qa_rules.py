"""
QA rules for SkyyRose Elite Studio fashion renders.

Defines per-category quality assurance rules for fabric accuracy, color
fidelity, styling coherence, photography standards, and brand consistency.
All objects are frozen (immutable).

"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QARule:
    """Immutable quality assurance rule for fashion image evaluation."""

    name: str
    category: str  # fabric, color, styling, photography, brand
    check_description: str
    pass_criteria: str
    fail_examples: tuple[str, ...]


# ---------------------------------------------------------------------------
# QA rule catalogue
# ---------------------------------------------------------------------------

_RULES: tuple[QARule, ...] = (
    # -----------------------------------------------------------------------
    # Fabric accuracy rules
    # -----------------------------------------------------------------------
    QARule(
        name="Sherpa Pile Visibility",
        category="fabric",
        check_description="Verify that sherpa fabric shows visible pile texture depth.",
        pass_criteria=(
            "Individual fiber clusters visible with micro-shadows between them. "
            "Pile profile visible at collar, cuff, and hem edges. Surface not flat."
        ),
        fail_examples=(
            "Sherpa rendered as smooth cotton or jersey",
            "Flat uniform surface with no pile depth",
            "Missing pile profile at garment edges",
        ),
    ),
    QARule(
        name="Mesh Grid Pattern",
        category="fabric",
        check_description="Verify that mesh fabric shows open-weave grid pattern.",
        pass_criteria=(
            "Grid hole pattern clearly visible across fabric surface. "
            "Semi-transparency through openings detectable. "
            "Not rendered as solid opaque color."
        ),
        fail_examples=(
            "Mesh rendered as solid opaque fabric",
            "No visible grid holes in surface",
            "Treated as flat cotton jersey",
        ),
    ),
    QARule(
        name="Satin Specular Highlight",
        category="fabric",
        check_description="Verify that satin fabric shows high-gloss specular highlights.",
        pass_criteria=(
            "Bright specular highlights visible on face. "
            "Clear contrast between illuminated peaks and shadowed valleys. "
            "Fluid drape with sharp highlight ridges."
        ),
        fail_examples=(
            "Satin rendered as matte cotton",
            "Uniform brightness without highlights",
            "Flat non-glossy appearance",
        ),
    ),
    QARule(
        name="French Terry Ribbing",
        category="fabric",
        check_description="Verify french terry shows ribbed structure at cuffs and hem.",
        pass_criteria=(
            "Distinct rib wale pattern visible at cuffs, hem, and collar. "
            "Face is smooth-textured but not flat. "
            "Fabric reads as substantial weight, not thin jersey."
        ),
        fail_examples=(
            "Ribbed sections look same as body — no rib definition",
            "Fabric appears paper-thin or jersey-weight",
            "Missing distinction between body and ribbed areas",
        ),
    ),
    QARule(
        name="Embroidery Texture",
        category="fabric",
        check_description="Verify embroidery shows raised thread texture and definition.",
        pass_criteria=(
            "Embroidered elements show raised 3D thread texture. "
            "Individual thread runs or fill stitches visible. "
            "Clear contrast between embroidery and base fabric."
        ),
        fail_examples=(
            "Embroidery rendered flat as print or decal",
            "No raised texture visible on embroidered areas",
            "Thread detail lost — reads as flat graphic",
        ),
    ),
    # -----------------------------------------------------------------------
    # Color fidelity rules
    # -----------------------------------------------------------------------
    QARule(
        name="Black Rose Dark Tone",
        category="color",
        check_description="Verify Black Rose products render in correct near-black (#0A0A0A).",
        pass_criteria=(
            "Primary garment color is near-black, not washed-out gray or navy. "
            "Shadow areas maintain depth without crushing to pure black. "
            "Silver (#C0C0C0) accent appears correctly where specified."
        ),
        fail_examples=(
            "Black renders as medium gray",
            "Dark areas crush completely to #000000 with no detail",
            "Silver accent appears white or gold",
        ),
    ),
    QARule(
        name="Love Hurts Crimson Accuracy",
        category="color",
        check_description="Verify Love Hurts crimson accent (#DC143C) renders accurately.",
        pass_criteria=(
            "Crimson accent color visible and distinct from dark base. "
            "Color is saturated red-crimson, not orange-red or pink. "
            "Hex approximate #DC143C within visual tolerance."
        ),
        fail_examples=(
            "Crimson renders as orange-red",
            "Crimson too muted or desaturated",
            "Crimson accent invisible against dark base",
        ),
    ),
    QARule(
        name="Signature Gold Fidelity",
        category="color",
        check_description="Verify Signature collection gold (#D4AF37) renders accurately.",
        pass_criteria=(
            "Gold accent is warm, rich gold — not yellow, not bronze. "
            "Approximate hex #D4AF37. "
            "Maintains warmth without washing out."
        ),
        fail_examples=(
            "Gold renders as bright yellow",
            "Gold appears dull brown or bronze",
            "Gold too desaturated",
        ),
    ),
    QARule(
        name="Rose Gold Brand Accent",
        category="color",
        check_description="Verify rose gold accent (#B76E79) renders correctly in brand elements.",
        pass_criteria=(
            "Rose gold is warm blush-pink with gold undertone. "
            "Approximate hex #B76E79. "
            "Visible as distinct accent color, not washed out."
        ),
        fail_examples=(
            "Rose gold appears as hot pink",
            "Rose gold washes out to pale pink",
            "Rose gold too orange or too purple",
        ),
    ),
    # -----------------------------------------------------------------------
    # Styling coherence rules
    # -----------------------------------------------------------------------
    QARule(
        name="Garment Proportion Accuracy",
        category="styling",
        check_description="Verify garment proportions match SkyyRose sizing guidelines.",
        pass_criteria=(
            "Oversized garments show relaxed drop-shoulder silhouette. "
            "Joggers show taper from thigh to ribbed ankle cuff. "
            "Shorts fall at mid-thigh length. "
            "No distorted proportions."
        ),
        fail_examples=(
            "Hoodie looks fitted when it should be oversized",
            "Jogger leg appears straight, not tapered",
            "Shorts render at knee length instead of mid-thigh",
        ),
    ),
    QARule(
        name="Construction Detail Visibility",
        category="styling",
        check_description="Verify key construction details are visible in renders.",
        pass_criteria=(
            "Drawstrings visible at waistbands and hoods. "
            "Pocket openings visible on joggers and shorts. "
            "Zip or snap closures visible on jackets. "
            "Hardware details visible on fanny pack."
        ),
        fail_examples=(
            "Hoodie drawstring missing or invisible",
            "Pockets not indicated in silhouette",
            "Jacket closure hardware invisible",
        ),
    ),
    QARule(
        name="Jersey Number Placement",
        category="styling",
        check_description="Verify jersey series shows correct number and lettering detail.",
        pass_criteria=(
            "Number clearly readable on front and back. "
            "Alternating rose fill pattern visible on number fills where specified. "
            "Lettering on chest or back legible."
        ),
        fail_examples=(
            "Jersey number too small to read",
            "Rose fill alternating pattern not visible",
            "Lettering blurred or distorted",
        ),
    ),
    # -----------------------------------------------------------------------
    # Photography standards rules
    # -----------------------------------------------------------------------
    QARule(
        name="Ecommerce Background",
        category="photography",
        check_description="Verify ecommerce renders use clean white or light gray background.",
        pass_criteria=(
            "Background is pure white (#FFFFFF) or light gray (#F5F5F5). "
            "No props, environment elements, or gradient backgrounds. "
            "Subject cleanly separated from background."
        ),
        fail_examples=(
            "Textured or patterned background on ecommerce render",
            "Environmental elements intruding into frame",
            "Vignette or gradient background",
        ),
    ),
    QARule(
        name="Editorial Lighting Mood",
        category="photography",
        check_description="Verify editorial renders use collection-appropriate dramatic lighting.",
        pass_criteria=(
            "Directional light creating visible shadow play. "
            "Collection-appropriate color grade applied. "
            "Black Rose: cool/silver-dark grade. Love Hurts: warm crimson-dark. "
            "Signature: golden warm grade."
        ),
        fail_examples=(
            "Flat even lighting on editorial render",
            "Wrong collection color grade applied",
            "Missing dramatic shadow contrast",
        ),
    ),
    QARule(
        name="Flat Lay Overhead Angle",
        category="photography",
        check_description="Verify flat lay renders are at true overhead 90-degree angle.",
        pass_criteria=(
            "Camera angle is true overhead — no parallax. "
            "Garment laid flat without extreme bunching. "
            "Both front and back views captured."
        ),
        fail_examples=(
            "Flat lay at angled perspective instead of true overhead",
            "Garment severely bunched or folded",
            "Only one view captured for ecommerce",
        ),
    ),
    # -----------------------------------------------------------------------
    # Brand consistency rules
    # -----------------------------------------------------------------------
    QARule(
        name="SkyyRose Branding Visibility",
        category="brand",
        check_description="Verify SkyyRose branding elements are visible and accurate.",
        pass_criteria=(
            "Logo or wordmark legible where specified. "
            "Rose motif renders with correct petal structure. "
            "Brand colors match SkyyRose hex values within tolerance."
        ),
        fail_examples=(
            "Logo distorted or pixelated",
            "Rose petal count or shape inaccurate",
            "Brand colors drifted outside acceptable delta-E range",
        ),
    ),
    QARule(
        name="Collection DNA Consistency",
        category="brand",
        check_description="Verify the render communicates correct collection identity.",
        pass_criteria=(
            "Black Rose: gothic luxury, dark, silver accents, Oakland edge. "
            "Love Hurts: crimson passion, raw emotion, vulnerability. "
            "Signature: West Coast prestige, gold, Bay Area pride. "
            "Kids Capsule: bold colorblock, playful luxury."
        ),
        fail_examples=(
            "Black Rose render looks soft or bright — missing gothic darkness",
            "Love Hurts render has no emotional tension",
            "Signature render looks generic without West Coast identity",
            "Kids render looks dull or adult-focused",
        ),
    ),
    QARule(
        name="No Placeholder or Watermark",
        category="brand",
        check_description="Verify no watermarks, placeholders, or AI-generated artifacts visible.",
        pass_criteria=(
            "No watermarks from image generation services. "
            "No placeholder text or graphics. "
            "No obvious AI generation artifacts (duplicated elements, merged faces)."
        ),
        fail_examples=(
            "Midjourney or DALL-E watermark visible",
            "Placeholder text in graphic area",
            "AI merge artifact in garment pattern",
        ),
    ),
    QARule(
        name="Kids Capsule Age Appropriateness",
        category="brand",
        check_description="Verify Kids Capsule renders show age-appropriate sizing and styling.",
        pass_criteria=(
            "Sizing reads as kids 2T–7, not adult. "
            "V-chevron colorblock aligned at waist seam. "
            "Colors bold and correct — red/black or purple/black."
        ),
        fail_examples=(
            "Kids set renders in adult proportions",
            "V-chevron colorblock misaligned or missing",
            "Colors wrong — wrong colorway rendered",
        ),
    ),
)

# Build lookup indices
_BY_CATEGORY: dict[str, list[QARule]] = {}
_BY_GARMENT: dict[str, list[QARule]] = {
    "jersey": ["Jersey Number Placement", "Mesh Grid Pattern", "Embroidery Texture"],
    "hoodie": [
        "French Terry Ribbing",
        "Garment Proportion Accuracy",
        "Construction Detail Visibility",
        "SkyyRose Branding Visibility",
    ],
    "crewneck": ["French Terry Ribbing", "Garment Proportion Accuracy", "Embroidery Texture"],
    "joggers": [
        "French Terry Ribbing",
        "Garment Proportion Accuracy",
        "Construction Detail Visibility",
    ],
    "sweatpants": ["French Terry Ribbing", "Garment Proportion Accuracy"],
    "shorts": [
        "Mesh Grid Pattern",
        "Garment Proportion Accuracy",
        "Construction Detail Visibility",
    ],
    "shirt": ["No Placeholder or Watermark", "Garment Proportion Accuracy"],
    "jacket": [
        "Sherpa Pile Visibility",
        "Construction Detail Visibility",
        "Garment Proportion Accuracy",
    ],
    "varsity jacket": [
        "Satin Specular Highlight",
        "Embroidery Texture",
        "Construction Detail Visibility",
    ],
    "beanie": ["Embroidery Texture", "SkyyRose Branding Visibility"],
    "fanny pack": ["Construction Detail Visibility", "SkyyRose Branding Visibility"],
    "set": ["Kids Capsule Age Appropriateness", "Garment Proportion Accuracy"],
}

_BY_COLLECTION: dict[str, list[str]] = {
    "black-rose": [
        "Black Rose Dark Tone",
        "Sherpa Pile Visibility",
        "Mesh Grid Pattern",
        "Jersey Number Placement",
        "Collection DNA Consistency",
        "Embroidery Texture",
    ],
    "love-hurts": [
        "Love Hurts Crimson Accuracy",
        "Satin Specular Highlight",
        "Collection DNA Consistency",
        "Embroidery Texture",
    ],
    "signature": [
        "Signature Gold Fidelity",
        "Rose Gold Brand Accent",
        "Collection DNA Consistency",
        "Sherpa Pile Visibility",
    ],
    "kids-capsule": [
        "Kids Capsule Age Appropriateness",
        "Collection DNA Consistency",
        "Rose Gold Brand Accent",
    ],
}

_RULE_NAME_MAP: dict[str, QARule] = {r.name: r for r in _RULES}

for _rule in _RULES:
    _BY_CATEGORY.setdefault(_rule.category, []).append(_rule)


class FashionQA:
    """Fashion QA rule advisor for SkyyRose Elite Studio.

    Provides categorized QA rules for evaluating AI-generated renders
    against SkyyRose quality standards.
    """

    def get_rules(self, category: str = "") -> list[QARule]:
        """Return all QA rules, optionally filtered by category.

        Categories: fabric, color, styling, photography, brand.
        """
        if not category:
            return list(_RULES)
        return _BY_CATEGORY.get(category.lower(), [])

    def get_rules_for_garment(self, garment_type: str) -> list[QARule]:
        """Return QA rules relevant for a garment type."""
        rule_names = _BY_GARMENT.get(garment_type.lower(), [])
        result = [_RULE_NAME_MAP[n] for n in rule_names if n in _RULE_NAME_MAP]
        # Always add brand and photography basics
        brand_rules = [r for r in _RULES if r.category == "brand"]
        existing_names = {r.name for r in result}
        for rule in brand_rules:
            if rule.name not in existing_names:
                result.append(rule)
        return result

    def get_rules_for_collection(self, collection: str) -> list[QARule]:
        """Return QA rules relevant for a collection."""
        rule_names = _BY_COLLECTION.get(collection.lower(), [])
        return [_RULE_NAME_MAP[n] for n in rule_names if n in _RULE_NAME_MAP]

    def get_rule(self, name: str) -> QARule | None:
        """Return a specific QA rule by name."""
        return _RULE_NAME_MAP.get(name)

    def list_categories(self) -> list[str]:
        """Return all QA categories."""
        return list(_BY_CATEGORY.keys())

    def list_garment_types(self) -> list[str]:
        """Return all garment types with specific QA rules."""
        return list(_BY_GARMENT.keys())
