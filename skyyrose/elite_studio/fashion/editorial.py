"""
Editorial direction for SkyyRose Elite Studio.

Styling rules, lookbook sequencing, and on-model vs flat-lay recommendations.
All objects are frozen (immutable).

""
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StylingRule:
    """Immutable styling rule for a garment type in a collection context."""

    garment_type: str
    pairing_suggestions: tuple[str, ...]
    layering_notes: str
    occasion: str
    collection_context: str


# ---------------------------------------------------------------------------
# Styling rules catalogue
# ---------------------------------------------------------------------------

_RULES: dict[tuple[str, str], StylingRule] = {
    ("hoodie", "black-rose"): StylingRule(
        garment_type="hoodie",
        pairing_suggestions=(
            "Black Rose Joggers (br-002)",
            "BLACK Rose x Love Hurts Basketball Shorts (br-007)",
            "Signature Beanie (sg-007)",
        ),
        layering_notes=(
            "Layer under BLACK Rose Sherpa Jacket (br-006) for elevated layered look. "
            "Hood-down default; hood-up adds streetwear edge."
        ),
        occasion="Street luxury, nighttime Oakland, casual premium",
        collection_context=(
            "Black Rose hoodie anchors the gothic-luxury look. "
            "Dark palette throughout — resist bright conflicting accessories."
        ),
    ),
    ("hoodie", "signature"): StylingRule(
        garment_type="hoodie",
        pairing_suggestions=(
            "Signature joggers or sweatpants",
            "The Signature Beanie (sg-007)",
            "Bay Bridge Shorts (sg-001) for contrast pairing",
        ),
        layering_notes=(
            "Layer Mint & Lavender Hoodie (sg-006) over matching crewneck (sg-013) "
            "for monochromatic depth. Rose Gold Hoodie (sg-004) pairs with any neutral."
        ),
        occasion="Daily luxury, West Coast casual, Bay Area commute",
        collection_context=(
            "Signature hoodies are versatile anchors. "
            "Match or tonal contrast with Signature bottoms for cohesive look."
        ),
    ),
    ("joggers", "black-rose"): StylingRule(
        garment_type="joggers",
        pairing_suggestions=(
            "BLACK Rose Hoodie (br-004) or Crewneck (br-001)",
            "BLACK Rose Hoodie Signature Edition (br-005) for premium set",
            "Sherpa Jacket (br-006) as outerwear over set",
        ),
        layering_notes=(
            "Create full monochromatic look with matching BLACK Rose top. "
            "Add br-006 Sherpa Jacket as outerwear layer for winter editorial."
        ),
        occasion="Luxury loungewear, elevated streetwear, premium casual",
        collection_context=(
            "Black Rose Joggers ground the gothic collection. "
            "All-black monochromatic set is the signature Black Rose look."
        ),
    ),
    ("joggers", "love-hurts"): StylingRule(
        garment_type="joggers",
        pairing_suggestions=(
            "Pair with future Love Hurts hooded tops for set look",
            "Layer with Love Hurts Varsity Jacket (lh-004) for statement",
            "Signature tops for cross-collection styling",
        ),
        layering_notes=(
            "Love Hurts Joggers at $95 are a statement piece. "
            "Minimal top lets the jogger take focus. "
            "Add lh-004 Varsity Jacket for full editorial impact."
        ),
        occasion="Editorial, premium street, elevated sport",
        collection_context=(
            "Love Hurts Joggers carry the crimson accent. "
            "High price point positions as a hero bottom."
        ),
    ),
    ("shorts", "black-rose"): StylingRule(
        garment_type="shorts",
        pairing_suggestions=(
            "BLACK Rose Hoodie (br-004) for full sport-luxury look",
            "BLACK is Beautiful Jersey (br-003) for athletic editorial",
            "Cross-collection: Signature tee on top",
        ),
        layering_notes=(
            "br-007 Cross-collection shorts bridge Black Rose and Love Hurts. "
            "Layer with matching hoodie for casual sport-luxury or jersey for athletic editorial."
        ),
        occasion="Athletic luxury, sport editorial, cross-collection",
        collection_context=(
            "BLACK Rose x Love Hurts collab shorts — dual collection energy. "
            "Respect both Black Rose dark palette and Love Hurts crimson accent."
        ),
    ),
    ("jersey", "black-rose"): StylingRule(
        garment_type="jersey",
        pairing_suggestions=(
            "BLACK Rose x Love Hurts Basketball Shorts (br-007)",
            "Love Hurts Basketball Shorts (lh-003)",
            "Layered under BLACK Rose Sherpa Jacket (br-006) open for style",
        ),
        layering_notes=(
            "Jersey as statement piece — let it lead. "
            "Matching shorts beneath completes the athletic set. "
            "Number detail (jersey series br-008–011) must be visible — front-facing shots."
        ),
        occasion="Athletic editorial, sport-luxury, collection statement",
        collection_context=(
            "BLACK is Beautiful Jersey Series is the Black Rose hero product. "
            "Each jersey honors Oakland/SF sports culture. "
            "Alternating rose fill on numbers is a key visual signature."
        ),
    ),
    ("jacket", "black-rose"): StylingRule(
        garment_type="jacket",
        pairing_suggestions=(
            "BLACK Rose Hoodie (br-004) underneath",
            "BLACK Rose Joggers (br-002) for full set",
            "BLACK Rose Crewneck (br-001) for cleaner silhouette",
        ),
        layering_notes=(
            "Sherpa Jacket is the outerwear anchor for Black Rose. "
            "Show over hoodie (layered) or as statement piece worn alone. "
            "Open-front styling shows the lining and interior detail."
        ),
        occasion="Outerwear hero, winter editorial, premium layering",
        collection_context=(
            "BLACK Rose Sherpa Jacket (br-006) at $95 is the collection's premium outerwear. "
            "Lustrous black satin exterior with plush sherpa lining — show both in renders."
        ),
    ),
    ("varsity jacket", "love-hurts"): StylingRule(
        garment_type="varsity jacket",
        pairing_suggestions=(
            "Love Hurts Joggers (lh-002) beneath for full editorial",
            "Love Hurts Basketball Shorts (lh-003) for sport-elevated look",
            "Simple black tee underneath to let jacket lead",
        ),
        layering_notes=(
            "Varsity Jacket is Love Hurts' hero piece at $265. "
            "Show snapped closed for hero shots. "
            "Show open with hood interior visible for lifestyle shots. "
            "Chenille lettering reads best in editorial lighting."
        ),
        occasion="Statement editorial, premium casual, collection anchor",
        collection_context=(
            "lh-004 Love Hurts Varsity Jacket: satin shell, fire-red script, "
            "hidden rose garden in hood. The emotional centerpiece of Love Hurts. "
            "Bold and unapologetic — raw emotion as luxury."
        ),
    ),
    ("shirt", "signature"): StylingRule(
        garment_type="shirt",
        pairing_suggestions=(
            "Bridge Series Shorts (sg-001 or sg-003) for matching set",
            "Signature Beanie (sg-007) as accessory",
            "Mint & Lavender sweatpants (sg-014) for cross-piece styling",
        ),
        layering_notes=(
            "Stay Golden Shirt (sg-002) and Bay Bridge Shirt (sg-005) are the Signature "
            "graphic tee anchors. Layer under Signature or Sherpa Jacket for seasonal versatility. "
            "Stand-alone in warmer months."
        ),
        occasion="Bay Area daily, West Coast casual, warm weather luxury",
        collection_context=(
            "Signature shirts celebrate Bay Area geography and culture. "
            "Golden Gate Bridge, Bay Bridge iconography. Wear with pride."
        ),
    ),
    ("beanie", "signature"): StylingRule(
        garment_type="beanie",
        pairing_suggestions=(
            "Any Black Rose or Signature hoodie for full look",
            "Love Hurts Varsity Jacket for cross-collection styling",
            "Solo accessory shot on clean background",
        ),
        layering_notes=(
            "Signature Beanie (sg-007) is the universal SkyyRose accessory. "
            "Pairs across all collections. Show on-head in lifestyle, flat for ecommerce."
        ),
        occasion="West Coast warmth, casual luxury, everyday accessory",
        collection_context=(
            "Embroidered signature rose — simple and iconic. "
            "The perfect SkyyRose entry-point product."
        ),
    ),
    ("fanny pack", "love-hurts"): StylingRule(
        garment_type="fanny pack",
        pairing_suggestions=(
            "Love Hurts Joggers (lh-002) — hip-worn over waistband",
            "Love Hurts Basketball Shorts (lh-003) for sport styling",
            "Any SkyyRose top for lifestyle shot",
        ),
        layering_notes=(
            "The Fannie (lh-006) at $45 is Love Hurts' accessible entry-point product. "
            "Wear at hip or cross-body. Show hardware hardware and embroidery detail in close-up."
        ),
        occasion="Daily carry, sport-luxury, festival, Oakland utility",
        collection_context=(
            "Oakland luxury meets everyday utility. Love Hurts embroidery on a functional form."
        ),
    ),
    ("set", "kids-capsule"): StylingRule(
        garment_type="set",
        pairing_suggestions=(
            "White sneakers for bright, clean look",
            "Simple white or black tee visible under zip hoodie",
            "Accessories: mini backpack, cap",
        ),
        layering_notes=(
            "Kids sets are complete outfits — show both hoodie and jogger together. "
            "V-chevron colorblock must align at waist seam. "
            "Kids Red (kids-001) and Purple (kids-002) can be shown together for sibling editorial."
        ),
        occasion="School, play, family luxury, gifting",
        collection_context=(
            "Kids Capsule: little ones deserve luxury too. "
            "Bold V-chevron colorblock in red/black or purple/black. "
            "Playful but premium — not juvenile."
        ),
    ),
}

# Default fallback for unknown combinations
_DEFAULT_RULE = StylingRule(
    garment_type="garment",
    pairing_suggestions=("Coordinate with same-collection pieces for cohesive look",),
    layering_notes="Layer thoughtfully — lighter pieces beneath, heavier outerwear on top.",
    occasion="Versatile across casual and elevated casual occasions",
    collection_context="Anchor with SkyyRose brand colors: dark base, collection accent.",
)

# Lookbook sequence templates per collection
_LOOKBOOK_SEQUENCES: dict[str, list[str]] = {
    "black-rose": [
        "Hero shot: br-005 Signature Edition Hoodie + br-002 Joggers (full monochrome)",
        "Statement: br-006 Sherpa Jacket open over br-004 Hoodie",
        "Jersey feature: br-008 or br-009 on the court, shorts below",
        "Close-up: br-001 Crewneck embroidery detail",
        "Lifestyle: br-007 cross-collection shorts in motion",
        "Editorial close: full-length against Oakland concrete wall",
    ],
    "love-hurts": [
        "Hero shot: lh-004 Varsity Jacket snapped closed — full editorial",
        "Motion: lh-002 Joggers in movement, crimson rose visible",
        "Sport: lh-003 Basketball Shorts on court",
        "Accessory: lh-006 The Fannie at hip",
        "Lifestyle: Varsity open showing hood lining detail",
        "Editorial close: embroidery detail shot on all pieces",
    ],
    "signature": [
        "Golden hour: sg-002 Stay Golden Shirt + sg-003 Stay Golden Shorts",
        "Tonal: sg-006 Mint & Lavender Hoodie + sg-014 Sweatpants + sg-013 Crewneck",
        "Accessory: sg-007 Beanie on Bay Bridge backdrop",
        "Active: sg-001 Bay Bridge Shorts in motion",
        "Premium: sg-009 Sherpa Jacket as outerwear statement",
        "Label series: sg-011 White Label Tee + sg-012 Orchid Label Tee side by side",
    ],
    "kids-capsule": [
        "Hero: kids-001 Red Set full body, V-chevron visible",
        "Hero: kids-002 Purple Set full body",
        "Sibling: kids-001 and kids-002 together",
        "Detail: V-chevron colorblock close-up",
        "Lifestyle: playing in full set",
    ],
}

# Flat-lay preferred garment types
_FLAT_LAY_PREFERRED = {"beanie", "fanny pack", "shirt"}
_ON_MODEL_PREFERRED = {
    "hoodie",
    "crewneck",
    "joggers",
    "sweatpants",
    "shorts",
    "jacket",
    "varsity jacket",
    "set",
    "jersey",
}


class EditorialDirector:
    """Editorial direction expert for SkyyRose Elite Studio.

    Provides styling rules, lookbook sequencing, and on-model vs flat-lay
    recommendations for product renders and campaign planning.
    """

    def get_styling(self, garment_type: str, collection: str) -> StylingRule:
        """Return the styling rule for a garment/collection combination.

        Falls back to same-garment any-collection, then default.
        """
        key = (garment_type.lower(), collection.lower())
        rule = _RULES.get(key)
        if rule:
            return rule
        # Try any collection with matching garment
        for (gt, _col), r in _RULES.items():
            if gt == garment_type.lower():
                return r
        return _DEFAULT_RULE

    def plan_lookbook_sequence(self, products: list[str], collection: str) -> list[dict]:
        """Plan a lookbook sequence for a set of product SKUs in a collection.

        Returns ordered list of dicts with shot description and product SKU.
        """
        sequence_template = _LOOKBOOK_SEQUENCES.get(collection.lower(), [])
        result: list[dict] = []
        for i, shot_description in enumerate(sequence_template):
            sku = products[i] if i < len(products) else ""
            result.append(
                {
                    "shot": i + 1,
                    "description": shot_description,
                    "sku": sku,
                    "collection": collection,
                }
            )
        # Append any extra products not in template
        for j, extra_sku in enumerate(
            products[len(sequence_template) :], start=len(sequence_template) + 1
        ):
            result.append(
                {
                    "shot": j,
                    "description": f"Additional product shot: {extra_sku}",
                    "sku": extra_sku,
                    "collection": collection,
                }
            )
        return result

    def recommend_flat_vs_on_model(self, garment_type: str) -> str:
        """Recommend whether to use flat-lay or on-model photography.

        Returns 'flat-lay', 'on-model', or 'both'.
        """
        gt = garment_type.lower()
        if gt in _FLAT_LAY_PREFERRED:
            return "both"  # accessories do both
        if gt in _ON_MODEL_PREFERRED:
            return "on-model"
        return "both"

    def get_collection_editorial_notes(self, collection: str) -> str:
        """Return high-level editorial notes for a collection."""
        notes = {
            "black-rose": (
                "Gothic luxury meets Oakland concrete. Dark, dramatic, noir. "
                "Deep shadows, silver accents, embroidered roses. "
                "Location: nighttime Oakland — Bay Bridge, city streets."
            ),
            "love-hurts": (
                "Raw emotion as luxury. Crimson and darkness. "
                "Vulnerability is strength — show it. "
                "Moody interiors, rain-soaked streets. Varsity jacket leads."
            ),
            "signature": (
                "Understated West Coast prestige. Golden hour SF. "
                "Daily elevation — luxury is in the details. "
                "Bay Bridge, Golden Gate, Bay Area sunshine."
            ),
            "kids-capsule": (
                "Playful luxury. Bold colorblock, joyful energy. "
                "Little ones deserve luxury too. "
                "Bright, clean, family-forward."
            ),
        }
        return notes.get(
            collection.lower(), "SkyyRose brand aesthetic — "
        )
