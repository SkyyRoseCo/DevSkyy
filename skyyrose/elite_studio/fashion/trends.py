"""
Trend intelligence for SkyyRose Elite Studio.

FW26 / SS27 trend signals mapped to SkyyRose brand DNA and product categories.
All objects are frozen (immutable).

"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TrendSignal:
    """Immutable descriptor for a single fashion trend signal."""

    name: str
    category: str  # silhouette, fabric, color, styling, cultural
    direction: str  # "rising", "peak", "declining"
    season: str  # "FW26", "SS27", or "FW26/SS27"
    description: str
    relevance_to_skyyrose: str


# ---------------------------------------------------------------------------
# FW26 / SS27 trend data
# ---------------------------------------------------------------------------

_TRENDS: tuple[TrendSignal, ...] = (
    TrendSignal(
        name="Oversized Silhouettes",
        category="silhouette",
        direction="peak",
        season="FW26/SS27",
        description=(
            "Exaggerated proportions dominate across all categories — oversized hoodies, "
            "balloon joggers, boxy tees. Drop shoulders and extended hems signal luxury effortlessness."
        ),
        relevance_to_skyyrose=(
            "High relevance. All Black Rose, Love Hurts, and Signature hoodies, crewnecks, "
            "and joggers already lean oversized. Lean into exaggerated drop-shoulder and "
            "extended body length in renders."
        ),
    ),
    TrendSignal(
        name="Earth Tones & Muted Palettes",
        category="color",
        direction="rising",
        season="FW26",
        description=(
            "Warm neutrals — clay, sand, tobacco, mushroom — replace maximalist brights. "
            "Muted olives and sage greens cross into streetwear. Black remains anchor."
        ),
        relevance_to_skyyrose=(
            "Moderate relevance. SkyyRose's dark #0A0A0A base aligns. Mint & Lavender Signature "
            "collection bridges the muted pastel trend. Future colorways should consider clay/sand options."
        ),
    ),
    TrendSignal(
        name="Sherpa & Fleece Comeback",
        category="fabric",
        direction="rising",
        season="FW26",
        description=(
            "Plush textures reclaim their position as premium-casual markers. "
            "Sherpa panels, fleece-lined outerwear, and sherpa-trim jackets signal warmth-as-luxury."
        ),
        relevance_to_skyyrose=(
            "Direct relevance. BLACK Rose Sherpa Jacket (br-006) and The Sherpa Jacket (sg-009) "
            "are perfectly positioned. Emphasize plush pile texture in all renders and copy."
        ),
    ),
    TrendSignal(
        name="Sport-Luxury Crossover",
        category="styling",
        direction="peak",
        season="FW26/SS27",
        description=(
            "Athletic silhouettes elevated with premium materials and branding. Basketball shorts "
            "with tailored outerwear, jersey-as-statement-piece, jogger-as-trouser."
        ),
        relevance_to_skyyrose=(
            "Core relevance — this IS SkyyRose's DNA. Jersey Series (br-008–011), Basketball Shorts "
            "across collections, and all jogger/shorts SKUs sit at this intersection. "
            "Lean into sport-meets-elevated styling in editorial direction."
        ),
    ),
    TrendSignal(
        name="Gender-Neutral Dressing",
        category="silhouette",
        direction="rising",
        season="FW26/SS27",
        description=(
            "Unisex sizing and silhouettes are no longer a niche offering — relaxed fits, "
            "neutral color palettes, and non-gendered branding are table stakes for premium streetwear."
        ),
        relevance_to_skyyrose=(
            "High relevance. All SkyyRose adult products are listed as unisex. "
            "Reinforce in styling direction: show both feminine and masculine styling in renders."
        ),
    ),
    TrendSignal(
        name="Y2K Revival",
        category="styling",
        direction="rising",
        season="SS27",
        description=(
            "Early 2000s nostalgia: varsity jackets, metallic accents, baby-tees, low-rise references. "
            "Gen-Z driven trend anchored in remix culture."
        ),
        relevance_to_skyyrose=(
            "Moderate relevance. Love Hurts Varsity Jacket (lh-004) directly captures this. "
            "Satin + metallic accents in BLACK Rose collection align with Y2K metallic revival."
        ),
    ),
    TrendSignal(
        name="Monochromatic Dressing",
        category="styling",
        direction="peak",
        season="FW26/SS27",
        description=(
            "Head-to-toe single-color outfits as a status signal. Matching sets — hoodie + "
            "jogger, top + shorts — in tonal colorways signal intentional luxury."
        ),
        relevance_to_skyyrose=(
            "Direct relevance. Kids Capsule sets, Mint & Lavender three-piece (hoodie + crewneck + "
            "sweatpants), and all-black Black Rose sets embody this. Push monochrome styling in lookbooks."
        ),
    ),
    TrendSignal(
        name="Bay Area Cultural Pride",
        category="cultural",
        direction="rising",
        season="FW26/SS27",
        description=(
            "Regional identity as luxury signal. Oakland roots, SF iconography, Bay Area specificity "
            "becoming markers of authenticity in streetwear. Anti-generic, hyper-local."
        ),
        relevance_to_skyyrose=(
            "Core identity marker. The Bridge Series (Bay Bridge, Golden Gate references), "
            "LAST OAKLAND jersey (br-009), THE BAY basketball jersey (br-010), "
            "all validate SkyyRose's Oakland-rooted luxury positioning."
        ),
    ),
    TrendSignal(
        name="Elevated Embroidery",
        category="fabric",
        direction="peak",
        season="FW26/SS27",
        description=(
            "Chenille, 3D puff, and tonal embroidery as premium signifiers. "
            "Embroidered logos and motifs replacing screen print as quality indicator."
        ),
        relevance_to_skyyrose=(
            "High relevance. Embroidered roses are central to SkyyRose brand identity across "
            "Black Rose and Love Hurts. Ensure embroidery texture renders crisply — "
            "it's a key differentiator from mass-market product."
        ),
    ),
    TrendSignal(
        name="Kids Luxury Fashion",
        category="cultural",
        direction="rising",
        season="SS27",
        description=(
            "Mini-me luxury collections growing as parents invest in matching family aesthetics. "
            "Premium colorblock sets for children seeing strong demand."
        ),
        relevance_to_skyyrose=(
            "Direct relevance. Kids Capsule (kids-001, kids-002) positions SkyyRose in this space. "
            'Lean into "little ones deserve luxury too" messaging.'
        ),
    ),
)

# Build category and season lookup maps
_BY_CATEGORY: dict[str, list[TrendSignal]] = {}
_BY_SEASON: dict[str, list[TrendSignal]] = {}

for _trend in _TRENDS:
    _BY_CATEGORY.setdefault(_trend.category, []).append(_trend)
    for _s in _trend.season.split("/"):
        _BY_SEASON.setdefault(_s, []).append(_trend)

# Garment relevance scoring — how many rising/peak trends apply
_GARMENT_TREND_SCORES: dict[str, list[str]] = {
    "hoodie": [
        "Oversized Silhouettes",
        "Sport-Luxury Crossover",
        "Monochromatic Dressing",
        "Elevated Embroidery",
    ],
    "crewneck": ["Oversized Silhouettes", "Monochromatic Dressing", "Elevated Embroidery"],
    "jersey": ["Sport-Luxury Crossover", "Bay Area Cultural Pride", "Elevated Embroidery"],
    "joggers": ["Oversized Silhouettes", "Sport-Luxury Crossover", "Monochromatic Dressing"],
    "sweatpants": [
        "Oversized Silhouettes",
        "Monochromatic Dressing",
        "Earth Tones & Muted Palettes",
    ],
    "shorts": ["Sport-Luxury Crossover", "Monochromatic Dressing"],
    "shirt": ["Oversized Silhouettes", "Sport-Luxury Crossover", "Bay Area Cultural Pride"],
    "jacket": ["Sherpa & Fleece Comeback", "Sport-Luxury Crossover"],
    "varsity jacket": ["Y2K Revival", "Bay Area Cultural Pride", "Elevated Embroidery"],
    "beanie": ["Monochromatic Dressing"],
    "fanny pack": ["Sport-Luxury Crossover", "Y2K Revival"],
    "set": ["Monochromatic Dressing", "Gender-Neutral Dressing", "Kids Luxury Fashion"],
}

_TREND_NAME_MAP: dict[str, TrendSignal] = {t.name: t for t in _TRENDS}


class TrendAdvisor:
    """Trend signal advisor for SkyyRose product rendering and styling decisions.

    Stateless — all data is embedded. Safe to instantiate freely.
    """

    def get_current_trends(self, season: str = "") -> list[TrendSignal]:
        """Return all trend signals, optionally filtered by season (e.g. 'FW26')."""
        if not season:
            return list(_TRENDS)
        return _BY_SEASON.get(season.upper(), [])

    def get_trends_for_category(self, category: str) -> list[TrendSignal]:
        """Return all trend signals in a category (silhouette, fabric, color, styling, cultural)."""
        return _BY_CATEGORY.get(category.lower(), [])

    def get_relevance_score(self, garment_type: str, season: str = "") -> float:
        """Compute a trend relevance score (0.0–1.0) for a garment in a given season.

        Score is the fraction of relevant trends that are 'rising' or 'peak'.
        """
        applicable_names = _GARMENT_TREND_SCORES.get(garment_type.lower(), [])
        if not applicable_names:
            return 0.3  # unknown garment type — baseline score

        applicable_trends = [_TREND_NAME_MAP[n] for n in applicable_names if n in _TREND_NAME_MAP]

        if season:
            season_upper = season.upper()
            applicable_trends = [t for t in applicable_trends if season_upper in t.season.upper()]

        if not applicable_trends:
            return 0.3

        active = sum(1 for t in applicable_trends if t.direction in ("rising", "peak"))
        return round(active / len(applicable_trends), 2)

    def get_trend_notes_for_garment(self, garment_type: str) -> list[str]:
        """Return skyyrose-specific trend relevance notes for a garment type."""
        applicable_names = _GARMENT_TREND_SCORES.get(garment_type.lower(), [])
        return [
            _TREND_NAME_MAP[n].relevance_to_skyyrose
            for n in applicable_names
            if n in _TREND_NAME_MAP
        ]
