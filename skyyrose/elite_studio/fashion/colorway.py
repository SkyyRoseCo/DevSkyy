"""
Color palette and colorway advisor for SkyyRose Elite Studio.

Provides per-collection palettes, colorway suggestions, and color fidelity
validation for AI renders. All objects are frozen (immutable).

"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class ColorPalette:
    """Immutable descriptor for a SkyyRose color palette."""

    name: str
    primary: str  # hex
    secondary: str  # hex
    accent: str  # hex
    neutrals: tuple[str, ...]  # hex values
    collection: str  # collection slug or "global"
    season_affinity: tuple[str, ...]  # ("FW26",) or ("SS27", "FW26")
    mood: str


# ---------------------------------------------------------------------------
# SkyyRose brand palettes
# ---------------------------------------------------------------------------

# Global brand anchor colors
_BRAND_COLORS = {
    "dark": "#0A0A0A",
    "rose_gold": "#B76E79",
    "gold": "#D4AF37",
    "crimson": "#DC143C",
    "silver": "#C0C0C0",
    "charcoal": "#1C1C1C",
    "smoke": "#2D2D2D",
    "off_white": "#F5F4F0",
    "cream": "#F9F5EC",
}

_PALETTES: tuple[ColorPalette, ...] = (
    # -----------------------------------------------------------------------
    # Global / Brand
    # -----------------------------------------------------------------------
    ColorPalette(
        name="SkyyRose Brand",
        primary="#0A0A0A",
        secondary="#B76E79",
        accent="#D4AF37",
        neutrals=("#1C1C1C", "#2D2D2D", "#F5F4F0"),
        collection="global",
        season_affinity=("FW26", "SS27"),
        mood="dark luxury, elevated concrete, timeless premium",
    ),
    # -----------------------------------------------------------------------
    # Black Rose collection
    # -----------------------------------------------------------------------
    ColorPalette(
        name="Black Rose Core",
        primary="#0A0A0A",
        secondary="#C0C0C0",
        accent="#B76E79",
        neutrals=("#1C1C1C", "#2D2D2D", "#3A3A3A"),
        collection="black-rose",
        season_affinity=("FW26",),
        mood="gothic luxury, noir elegance, Oakland darkness",
    ),
    ColorPalette(
        name="Black Rose Night",
        primary="#050505",
        secondary="#8A8A8A",
        accent="#DC143C",
        neutrals=("#1C1C1C", "#2D2D2D", "#0F0F0F"),
        collection="black-rose",
        season_affinity=("FW26",),
        mood="midnight drama, deep shadow, rose in darkness",
    ),
    ColorPalette(
        name="Black Rose Jersey SF",
        primary="#AA0000",
        secondary="#FFFFFF",
        accent="#B76E79",
        neutrals=("#1C1C1C", "#888888", "#F0F0F0"),
        collection="black-rose",
        season_affinity=("FW26", "SS27"),
        mood="SF 49ers inspired, rose fill on numbers, sport-luxury",
    ),
    ColorPalette(
        name="Black Rose Jersey Oakland",
        primary="#FFFFFF",
        secondary="#0A0A0A",
        accent="#B76E79",
        neutrals=("#CCCCCC", "#888888", "#444444"),
        collection="black-rose",
        season_affinity=("FW26", "SS27"),
        mood="LAST OAKLAND tribute, white and black with rose fill",
    ),
    ColorPalette(
        name="Black Rose Bay Basketball",
        primary="#FFFFFF",
        secondary="#D4AF37",
        accent="#B76E79",
        neutrals=("#C0C0C0", "#888888", "#F0F0F0"),
        collection="black-rose",
        season_affinity=("FW26", "SS27"),
        mood="THE BAY, gold and silver Bay Area pride",
    ),
    ColorPalette(
        name="Black Rose Hockey Teal",
        primary="#0A0A0A",
        secondary="#007B89",
        accent="#B76E79",
        neutrals=("#1C1C1C", "#2D2D2D", "#00637A"),
        collection="black-rose",
        season_affinity=("FW26",),
        mood="San Jose Sharks inspired, hooded hockey elegance",
    ),
    # -----------------------------------------------------------------------
    # Love Hurts collection
    # -----------------------------------------------------------------------
    ColorPalette(
        name="Love Hurts Core",
        primary="#0A0A0A",
        secondary="#DC143C",
        accent="#B76E79",
        neutrals=("#1C1C1C", "#2D2D2D", "#8B0000"),
        collection="love-hurts",
        season_affinity=("FW26", "SS27"),
        mood="raw emotion, crimson passion, vulnerability as strength",
    ),
    ColorPalette(
        name="Love Hurts Varsity",
        primary="#0A0A0A",
        secondary="#DC143C",
        accent="#C0C0C0",
        neutrals=("#1C1C1C", "#8B0000", "#2D2D2D"),
        collection="love-hurts",
        season_affinity=("FW26",),
        mood="satin shell drama, fire-red script, hidden rose garden",
    ),
    # -----------------------------------------------------------------------
    # Signature collection
    # -----------------------------------------------------------------------
    ColorPalette(
        name="Signature Core",
        primary="#0A0A0A",
        secondary="#D4AF37",
        accent="#B76E79",
        neutrals=("#1C1C1C", "#C0C0C0", "#F5F4F0"),
        collection="signature",
        season_affinity=("FW26", "SS27"),
        mood="everyday luxury, West Coast prestige, understated confidence",
    ),
    ColorPalette(
        name="Signature Mint & Lavender",
        primary="#A8D5BA",
        secondary="#C9A8E5",
        accent="#B76E79",
        neutrals=("#0A0A0A", "#F5F4F0", "#D8D8D8"),
        collection="signature",
        season_affinity=("SS27",),
        mood="pastel luxury, fresh elevation, mint-lavender duality",
    ),
    ColorPalette(
        name="Signature Stay Golden",
        primary="#D4AF37",
        secondary="#0A0A0A",
        accent="#B76E79",
        neutrals=("#1C1C1C", "#BF9D2D", "#F5F4F0"),
        collection="signature",
        season_affinity=("SS27", "FW26"),
        mood="Bay Area golden hour, SF prestige, stay golden philosophy",
    ),
    ColorPalette(
        name="Signature Bay Bridge",
        primary="#1B3A5C",
        secondary="#D4AF37",
        accent="#B76E79",
        neutrals=("#0A0A0A", "#2D5A8E", "#C0C0C0"),
        collection="signature",
        season_affinity=("SS27",),
        mood="Bay Bridge blue, Oakland-to-SF crossing, West Coast pride",
    ),
    ColorPalette(
        name="Signature Rose Gold",
        primary="#B76E79",
        secondary="#0A0A0A",
        accent="#D4AF37",
        neutrals=("#C8848F", "#9B5A65", "#F5F4F0"),
        collection="signature",
        season_affinity=("FW26", "SS27"),
        mood="rose gold warmth, brand identity anchor, signature warmth",
    ),
    # -----------------------------------------------------------------------
    # Kids Capsule collection
    # -----------------------------------------------------------------------
    ColorPalette(
        name="Kids Capsule Red",
        primary="#CC1111",
        secondary="#0A0A0A",
        accent="#B76E79",
        neutrals=("#AA0000", "#1C1C1C", "#F5F4F0"),
        collection="kids-capsule",
        season_affinity=("FW26", "SS27"),
        mood="bold red energy, V-chevron power, joyful luxury",
    ),
    ColorPalette(
        name="Kids Capsule Purple",
        primary="#6B2FA0",
        secondary="#0A0A0A",
        accent="#B76E79",
        neutrals=("#5A2684", "#1C1C1C", "#F5F4F0"),
        collection="kids-capsule",
        season_affinity=("FW26", "SS27"),
        mood="rich purple royalty, V-chevron confidence, next-gen luxury",
    ),
)

_PALETTE_MAP: dict[str, list[ColorPalette]] = {}
for _pal in _PALETTES:
    _PALETTE_MAP.setdefault(_pal.collection, []).append(_pal)


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return (128, 128, 128)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _rgb_distance(rgb1: tuple[int, int, int], rgb2: tuple[int, int, int]) -> float:
    """Approximate perceptual color distance using weighted Euclidean RGB distance.

    This is a simplified approximation of CIE deltaE. Accurate delta E requires
    Lab color space conversion; this approximation is sufficient for QA gating.
    """
    r_mean = (rgb1[0] + rgb2[0]) / 2
    dr = rgb1[0] - rgb2[0]
    dg = rgb1[1] - rgb2[1]
    db = rgb1[2] - rgb2[2]
    weight_r = 2 + r_mean / 256
    weight_b = 2 + (255 - r_mean) / 256
    return math.sqrt(weight_r * dr**2 + 4 * dg**2 + weight_b * db**2)


class ColorAdvisor:
    """Color palette advisor for SkyyRose Elite Studio.

    Provides per-collection palettes, colorway suggestions, and color
    fidelity validation.
    """

    def get_collection_palette(self, collection: str) -> ColorPalette:
        """Return the primary (first) color palette for a collection.

        Falls back to global brand palette for unknown collections.
        """
        palettes = _PALETTE_MAP.get(collection.lower(), [])
        if palettes:
            return palettes[0]
        return _PALETTES[0]  # global brand palette

    def get_all_palettes_for_collection(self, collection: str) -> list[ColorPalette]:
        """Return all color palettes registered for a collection."""
        return _PALETTE_MAP.get(collection.lower(), [_PALETTES[0]])

    def suggest_colorways(
        self, garment_type: str, collection: str, n: int = 3
    ) -> list[ColorPalette]:
        """Suggest up to n colorway palettes for a garment in a collection.

        Prioritizes collection-specific palettes, falls back to global.
        """
        collection_palettes = _PALETTE_MAP.get(collection.lower(), [])
        global_palettes = _PALETTE_MAP.get("global", [])

        combined = collection_palettes + global_palettes
        return combined[:n]

    def validate_color_fidelity(
        self, target_hex: str, rendered_hex: str, max_delta_e: float = 5.0
    ) -> bool:
        """Validate that a rendered color is within acceptable distance of the target.

        Uses weighted Euclidean RGB distance as an approximation of CIE deltaE.
        A max_delta_e of 5.0 corresponds to ~10 in weighted RGB distance units.

        Returns True if the colors are within acceptable range.
        """
        target_rgb = _hex_to_rgb(target_hex)
        rendered_rgb = _hex_to_rgb(rendered_hex)
        # Scale max_delta_e to approximate RGB distance space (factor ~2.0)
        threshold = max_delta_e * 2.0
        return _rgb_distance(target_rgb, rendered_rgb) <= threshold

    def get_color_prompt_notes(self, collection: str) -> str:
        """Return color specification notes for AI generation prompts."""
        palette = self.get_collection_palette(collection)
        return (
            f"Primary color: {palette.primary}. "
            f"Secondary: {palette.secondary}. "
            f"Accent: {palette.accent}. "
            f"Neutrals: {', '.join(palette.neutrals)}. "
            f"Mood: {palette.mood}."
        )

    def list_collections(self) -> list[str]:
        """Return all collection slugs with registered palettes."""
        return list(_PALETTE_MAP.keys())
