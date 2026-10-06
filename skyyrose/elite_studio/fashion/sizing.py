"""
Sizing guidelines for SkyyRose Elite Studio.

Per-garment sizing guidelines and size charts for accurate product renders
and product descriptions.

"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SizingGuideline:
    """Immutable sizing guideline for a garment category in a collection."""

    size_range: str
    fit: str
    model_representation: str  # what size model wears for imagery
    rendering_notes: str


# ---------------------------------------------------------------------------
# Size chart data
# ---------------------------------------------------------------------------

# Adult unisex size charts (measurements in inches)
_SIZE_CHARTS: dict[str, dict[str, dict[str, str]]] = {
    "hoodie": {
        "S": {"chest": "36-38", "body_length": "26", "sleeve": "34"},
        "M": {"chest": "39-41", "body_length": "27", "sleeve": "35"},
        "L": {"chest": "42-44", "body_length": "28", "sleeve": "36"},
        "XL": {"chest": "45-47", "body_length": "29", "sleeve": "37"},
        "2XL": {"chest": "48-50", "body_length": "30", "sleeve": "38"},
        "3XL": {"chest": "51-53", "body_length": "31", "sleeve": "39"},
    },
    "crewneck": {
        "S": {"chest": "36-38", "body_length": "25", "shoulder": "18"},
        "M": {"chest": "39-41", "body_length": "26", "shoulder": "19"},
        "L": {"chest": "42-44", "body_length": "27", "shoulder": "20"},
        "XL": {"chest": "45-47", "body_length": "28", "shoulder": "21"},
        "2XL": {"chest": "48-50", "body_length": "29", "shoulder": "22"},
        "3XL": {"chest": "51-53", "body_length": "30", "shoulder": "23"},
    },
    "jersey": {
        "S": {"chest": "36-38", "body_length": "28", "shoulder": "18"},
        "M": {"chest": "39-41", "body_length": "29", "shoulder": "19"},
        "L": {"chest": "42-44", "body_length": "30", "shoulder": "20"},
        "XL": {"chest": "45-47", "body_length": "31", "shoulder": "21"},
        "2XL": {"chest": "48-50", "body_length": "32", "shoulder": "22"},
        "3XL": {"chest": "51-53", "body_length": "33", "shoulder": "23"},
    },
    "joggers": {
        "S": {"waist": "26-28", "hip": "36-38", "inseam": "29", "leg_opening": "7"},
        "M": {"waist": "29-31", "hip": "39-41", "inseam": "30", "leg_opening": "7"},
        "L": {"waist": "32-34", "hip": "42-44", "inseam": "30", "leg_opening": "7.5"},
        "XL": {"waist": "35-37", "hip": "45-47", "inseam": "31", "leg_opening": "8"},
        "2XL": {"waist": "38-40", "hip": "48-50", "inseam": "31", "leg_opening": "8.5"},
        "3XL": {"waist": "41-43", "hip": "51-53", "inseam": "31", "leg_opening": "9"},
    },
    "sweatpants": {
        "S": {"waist": "26-28", "hip": "38-40", "inseam": "30", "leg_opening": "9"},
        "M": {"waist": "29-31", "hip": "41-43", "inseam": "31", "leg_opening": "9.5"},
        "L": {"waist": "32-34", "hip": "44-46", "inseam": "31", "leg_opening": "10"},
        "XL": {"waist": "35-37", "hip": "47-49", "inseam": "32", "leg_opening": "10.5"},
        "2XL": {"waist": "38-40", "hip": "50-52", "inseam": "32", "leg_opening": "11"},
        "3XL": {"waist": "41-43", "hip": "53-55", "inseam": "32", "leg_opening": "11.5"},
    },
    "shorts": {
        "S": {"waist": "26-28", "hip": "36-38", "inseam": "7"},
        "M": {"waist": "29-31", "hip": "39-41", "inseam": "7.5"},
        "L": {"waist": "32-34", "hip": "42-44", "inseam": "8"},
        "XL": {"waist": "35-37", "hip": "45-47", "inseam": "8.5"},
        "2XL": {"waist": "38-40", "hip": "48-50", "inseam": "9"},
        "3XL": {"waist": "41-43", "hip": "51-53", "inseam": "9"},
    },
    "shirt": {
        "XS": {"chest": "33-35", "body_length": "26", "sleeve": "32"},
        "S": {"chest": "36-38", "body_length": "27", "sleeve": "33"},
        "M": {"chest": "39-41", "body_length": "28", "sleeve": "34"},
        "L": {"chest": "42-44", "body_length": "29", "sleeve": "35"},
        "XL": {"chest": "45-47", "body_length": "30", "sleeve": "36"},
        "2XL": {"chest": "48-50", "body_length": "31", "sleeve": "37"},
    },
    "jacket": {
        "S": {"chest": "38-40", "body_length": "27", "sleeve": "34"},
        "M": {"chest": "41-43", "body_length": "28", "sleeve": "35"},
        "L": {"chest": "44-46", "body_length": "29", "sleeve": "36"},
        "XL": {"chest": "47-49", "body_length": "30", "sleeve": "37"},
        "2XL": {"chest": "50-52", "body_length": "31", "sleeve": "38"},
        "3XL": {"chest": "53-55", "body_length": "32", "sleeve": "39"},
    },
    "varsity jacket": {
        "S": {"chest": "40-42", "body_length": "27", "sleeve": "34"},
        "M": {"chest": "43-45", "body_length": "28", "sleeve": "35"},
        "L": {"chest": "46-48", "body_length": "29", "sleeve": "36"},
        "XL": {"chest": "49-51", "body_length": "30", "sleeve": "37"},
        "2XL": {"chest": "52-54", "body_length": "31", "sleeve": "38"},
        "3XL": {"chest": "55-57", "body_length": "32", "sleeve": "39"},
    },
    "beanie": {
        "One Size": {"circumference": "21-23", "depth": "9"},
    },
    "fanny pack": {
        "One Size": {"strap_length": "26-46 (adjustable)", "main_compartment": "7x5x2"},
    },
    "set": {
        "2T": {"chest": "21", "waist": "20", "height": "33-35"},
        "3T": {"chest": "22", "waist": "21", "height": "36-38"},
        "4T": {"chest": "23", "waist": "21.5", "height": "39-41"},
        "5": {"chest": "24", "waist": "22", "height": "42-44"},
        "6": {"chest": "25", "waist": "22.5", "height": "45-47"},
        "7": {"chest": "26", "waist": "23", "height": "48-50"},
    },
}

# Sizing guidelines per garment + collection combination
_GUIDELINES: dict[str, SizingGuideline] = {
    "hoodie": SizingGuideline(
        size_range="S–3XL",
        fit="Relaxed unisex oversized fit. Drop shoulder silhouette.",
        model_representation="Size L on a 6'0\" model showing intended oversized silhouette.",
        rendering_notes=(
            "Render with visible drop shoulder. Body length extends past hip. "
            "Kangaroo pocket shows volume. Hood drapes naturally when down."
        ),
    ),
    "crewneck": SizingGuideline(
        size_range="S–3XL",
        fit="Relaxed unisex fit. Slightly boxy silhouette.",
        model_representation="Size M/L on 5'9\"–6'0\" model.",
        rendering_notes=(
            "Chest width reads relaxed without being baggy. "
            "Ribbed crew neck sits close to neck. Hem falls at hip."
        ),
    ),
    "jersey": SizingGuideline(
        size_range="S–3XL",
        fit="Athletic unisex fit. Slightly relaxed through chest and body.",
        model_representation="Size L on 6'0\" male-presenting or 5'8\" female-presenting model.",
        rendering_notes=(
            "Number and lettering placement must be visible and readable. "
            "Side vents show at hem. Athletic structure — not boxy."
        ),
    ),
    "joggers": SizingGuideline(
        size_range="S–3XL",
        fit="Relaxed through thigh, tapered at ankle with ribbed cuff.",
        model_representation="Size M/L on 5'9\"–6'0\" model.",
        rendering_notes=(
            "Taper visible from mid-thigh to ankle cuff. "
            "Waistband shows fold-over or drawstring. "
            "Ribbed ankle cuff sits 1–2 inches above ankle."
        ),
    ),
    "sweatpants": SizingGuideline(
        size_range="S–3XL",
        fit="Relaxed throughout with ribbed ankle cuff.",
        model_representation="Size M/L on 5'9\"–6'0\" model.",
        rendering_notes=(
            "Full relaxed leg through to cuff. "
            "More volume than joggers. "
            "Pockets create slight break in side seam silhouette."
        ),
    ),
    "shorts": SizingGuideline(
        size_range="S–3XL",
        fit="Athletic relaxed fit. 7–9 inch inseam. Elastic waistband.",
        model_representation="Size M/L on 6'0\" model at mid-thigh length.",
        rendering_notes=(
            "Hem falls mid-thigh. Elastic waist visible at top. "
            "Side pockets create slight silhouette break. "
            "Mesh construction shows through in highlights."
        ),
    ),
    "shirt": SizingGuideline(
        size_range="XS–2XL",
        fit="Regular to slightly relaxed unisex fit.",
        model_representation="Size M on 5'9\"–6'0\" model.",
        rendering_notes=(
            "Shoulder seam sits at natural shoulder. "
            "Graphics and print placement centered and clearly visible. "
            "Hem at hip, slightly longer in back for premium drape."
        ),
    ),
    "jacket": SizingGuideline(
        size_range="S–3XL",
        fit="Layer-friendly relaxed fit. One size up from hoodie recommended.",
        model_representation="Size L on 6'0\" model, worn over light layer.",
        rendering_notes=(
            "Show worn over a base layer to communicate layering intent. "
            "Collar and cuff lining detail visible. "
            "Zip or snap closure in neutral position."
        ),
    ),
    "varsity jacket": SizingGuideline(
        size_range="S–3XL",
        fit="Oversized varsity fit. Intentionally roomy through body and sleeves.",
        model_representation="Size L on 6'0\" model for full oversized drape.",
        rendering_notes=(
            "Satin shell drapes with premium fluid movement. "
            "Ribbed collar, cuffs, and hem contrast visible. "
            "Chenille lettering or embroidery shows raised texture. "
            "Show closed at front to maximize visual impact."
        ),
    ),
    "beanie": SizingGuideline(
        size_range="One Size",
        fit="One-size-fits-most. Double-layer rib-knit with stretch.",
        model_representation="On-head for all lifestyle shots. Flat lay for ecommerce.",
        rendering_notes=(
            "Fits down to brow level on head shots. "
            "Folded cuff shows double-layer construction. "
            "Embroidery detail faces camera in head-on shots."
        ),
    ),
    "fanny pack": SizingGuideline(
        size_range="One Size",
        fit="One Size. Adjustable strap fits waist 26–46 inches.",
        model_representation="Worn at hip level for lifestyle; flat lay for ecommerce.",
        rendering_notes=(
            "Strap feeds through hardware clips visibly. "
            "Main zipper compartment shows as closed default. "
            "Embroidery or branding detail center-front."
        ),
    ),
    "set": SizingGuideline(
        size_range="Kids 2T–7",
        fit="Kids relaxed fit. Both pieces coordinated.",
        model_representation="Age-appropriate child model wearing matching set.",
        rendering_notes=(
            "Show both pieces together — top and bottom coordinated. "
            "V-chevron colorblock pattern must align at waist. "
            "Bright, clear colors render accurately."
        ),
    ),
}


class SizingAdvisor:
    """Sizing guideline advisor for SkyyRose product renders and descriptions.

    Stateless — all data is embedded. Safe to instantiate freely.
    """

    def get_guideline(self, garment_type: str, collection: str = "") -> SizingGuideline:
        """Return the sizing guideline for a garment type.

        Collection parameter reserved for future per-collection size overrides.
        Returns a generic guideline if garment_type is unknown.
        """
        return _GUIDELINES.get(
            garment_type.lower(),
            SizingGuideline(
                size_range="S–3XL",
                fit="Relaxed unisex fit.",
                model_representation="Size L on 6'0\" model.",
                rendering_notes="Standard render — show garment silhouette clearly.",
            ),
        )

    def get_size_chart(self, garment_type: str) -> dict[str, dict[str, str]]:
        """Return the measurement size chart for a garment type.

        Returns empty dict if garment type has no size chart.
        """
        return _SIZE_CHARTS.get(garment_type.lower(), {})

    def list_garment_types(self) -> list[str]:
        """Return all garment types with size chart data."""
        return list(_SIZE_CHARTS.keys())
