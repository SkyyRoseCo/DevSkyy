"""
Moodboard composition for SkyyRose Elite Studio.

MoodboardComposer assembles structured moodboard specifications combining
visual references, color stories, texture palettes, and editorial direction.

""
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class Moodboard:
    """Immutable moodboard specification for a collection or concept."""

    moodboard_id: str
    title: str
    collection: str
    season: str
    concept_summary: str
    color_story: tuple[str, ...]  # hex colors in order of prominence
    texture_references: tuple[str, ...]  # fabric texture descriptions
    visual_references: tuple[str, ...]  # scene/imagery descriptions
    typography_direction: str
    lighting_mood: str
    location_references: tuple[str, ...]  # real places to reference
    cultural_touchpoints: tuple[str, ...]  # cultural references
    brand_anchors: tuple[str, ...]  # core brand elements to embed
    generation_prompt_block: str  # complete prompt block for AI moodboard generation


class MoodboardComposer:
    """Composes SkyyRose moodboards combining brand DNA, trend data, and location references.

    Produces structured Moodboard objects suitable for creative direction briefing
    and AI moodboard generation.
    """

    def __init__(self) -> None:
        from ..colorway import ColorAdvisor
        from ..editorial import EditorialDirector
        from ..photography import PhotographyDirector
        from ..trends import TrendAdvisor

        self._color = ColorAdvisor()
        self._trends = TrendAdvisor()
        self._editorial = EditorialDirector()
        self._photography = PhotographyDirector()

    # -----------------------------------------------------------------------
    # Location reference data per collection
    # -----------------------------------------------------------------------

    _LOCATION_REFS = {
        "black-rose": (
            "Bay Bridge at night — Oakland side, concrete pillars, amber light",
            "East Oakland murals — concrete walls, street art, urban texture",
            "Uptown Oakland alley — rose gold sunset on concrete",
            "Oakland Coliseum exterior — industrial architecture, night",
        ),
        "love-hurts": (
            "Rain-slicked Telegraph Ave, Oakland — neon reflection on wet pavement",
            "Dark velvet interior — moody lounge lighting, candlelight",
            "Gothic red rose garden — thorns and petals against black background",
            "Late night street corner — fog, crimson glow, urban isolation",
        ),
        "signature": (
            "Golden Gate Bridge at golden hour — warm light, fog through cables",
            "Embarcadero waterfront — SF skyline, open sky, polished luxury",
            "Bay Bridge day shot — steel blue water, San Francisco backdrop",
            "Twin Peaks overlook — panoramic SF view, golden afternoon",
        ),
        "kids-capsule": (
            "Colorful Oakland neighborhood mural — bright, community, joy",
            "City playground — concrete + color, joyful textures",
            "Family front stoop — Oakland streets, community warmth",
        ),
    }

    _CULTURAL_TOUCHPOINTS = {
        "black-rose": (
            "Oakland Raider Nation legacy",
            "East Bay hip-hop — Too $hort, E-40, Kamaiyah",
            "Black excellence and Black luxury",
            "Gothic Victorian architecture meets urban grit",
        ),
        "love-hurts": (
            "B-boy and b-girl culture — Oakland roots",
            "Passionate Oakland Warriors championship energy",
            "Hurts family legacy — emotional legacy as brand",
            "Beauty and the Beast mythology — beast perspective",
        ),
        "signature": (
            "Bay Area tech wealth meets street origin",
            "Golden State Warriors dynasty — West Coast prestige",
            "SF fashion culture — refined, confident, West Coast native",
            "Bay Area food culture as luxury — farm to table elevated",
        ),
        "kids-capsule": (
            "Next generation of Oakland luxury",
            "Family legacy — passing down the culture",
            "Bold youth fashion — no compromise on quality",
        ),
    }

    def compose(self, collection: str, season: str, concept: str = "") -> Moodboard:
        """Compose a moodboard for a collection and season."""
        moodboard_id = str(uuid.uuid4())[:8]

        # Color story
        palettes = self._color.get_all_palettes_for_collection(collection)
        color_story = tuple(
            f"{p.name}: primary {p.primary}, secondary {p.secondary}, accent {p.accent}"
            for p in palettes[:3]
        )

        # Texture references
        texture_refs_map = {
            "black-rose": (
                "Dense sherpa pile — plush darkness, depth",
                "Open mesh grid — athletic transparency",
                "High-gloss satin — liquid black surface",
                "Embroidered rose — raised thread catching light",
            ),
            "love-hurts": (
                "Satin varsity shell — crimson sheen, fluid",
                "French terry weight — premium knit heft",
                "Embroidered rose — crimson thread on darkness",
                "Open mesh — breathable sport texture",
            ),
            "signature": (
                "Plush sherpa — cream warmth, West Coast",
                "Smooth french terry — premium everyday weight",
                "Fine jersey knit — clean athletic face",
                "Brushed fleece — soft luxury nap",
            ),
            "kids-capsule": (
                "Fleece colorblock — bold, soft, tactile",
                "Rib knit trim — structure with stretch",
                "Smooth jersey — clean kids surface",
            ),
        }
        texture_refs = texture_refs_map.get(collection.lower(), ("Premium fabric textures",))

        # Visual references
        visual_refs_map = {
            "black-rose": (
                "Black rose bloom — single rose, midnight backdrop, silver dew drops",
                "Night city skyline — Oakland lights reflected in dark water",
                "Silhouette against lit wall — urban shadow, concrete luxury",
                "Close-up embroidery — rose thread detail, dark fabric base",
            ),
            "love-hurts": (
                "Red rose petals on black marble — crimson on darkness",
                "Varsity jacket open in wind — satin catches neon light",
                "Joggers in motion — urban movement, grit and luxury",
                "Single crimson rose — thorns prominent, petals perfect",
            ),
            "signature": (
                "Golden Gate cables in fog — gold architecture, diffused light",
                "Bay Bridge silhouette — blue hour, bridge geometry",
                "Bay Area lifestyle — sun-drenched streets, elevated casual",
                "Stay Golden palette — warm afternoon light on urban surface",
            ),
            "kids-capsule": (
                "Bold colorblock on concrete — red/black or purple/black V-chevron",
                "Child in full set — confident, joyful, luxury without compromise",
                "Family on Oakland street — multi-generational, brand passing forward",
            ),
        }
        visual_references = visual_refs_map.get(
            collection.lower(), ("Collection visual references TBD",)
        )

        # Typography
        typography_map = {
            "black-rose": "SkyyRose Black Rose Script for the name + Cinzel engraved caps + Archivo display — gothic elegance. Silver on black.",
            "love-hurts": "SkyyRose Love Hurts Graffiti script + Archivo display — raw expressive lettering meets clean expanded sans, italic accents for emotion. Crimson on dark.",
            "signature": "Pinyon Script + Archivo — refined script meets clean expanded editorial sans, Anton for caps. Gold on dark.",
            "kids-capsule": "Grand Hotel script + Archivo — approachable, friendly, still premium. Rose gold on dark.",
        }
        typography = typography_map.get(collection.lower(), "Archivo — SkyyRose standard display.")

        # Lighting
        lighting_map = {
            "black-rose": "Directional night light — sodium street lamp warmth, deep shadow, silver rim light",
            "love-hurts": "Moody interior — warm practical light, dramatic shadow, crimson cast practical",
            "signature": "Golden hour California — warm directional sunlight, lens flare, bright shadow-free",
            "kids-capsule": "Bright, even, joyful — clean natural light, no dramatic shadow",
        }
        lighting = lighting_map.get(collection.lower(), "Collection-appropriate lighting")

        # Locations and cultural touchpoints
        locations = self._LOCATION_REFS.get(collection.lower(), ("Oakland/Bay Area locations",))
        cultural = self._CULTURAL_TOUCHPOINTS.get(collection.lower(), ("SkyyRose brand culture",))

        # Brand anchors
        brand_anchors = (
            "SkyyRose rose motif — embroidered, bold",
            f"{collection.replace('-', ' ').title()} collection identity",
            "Oakland roots, West Coast prestige",
        )

        # Generation prompt block
        collection_display = collection.replace("-", " ").title()
        concept_text = concept if concept else f"{collection_display} luxury streetwear editorial"
        main_palette = palettes[0] if palettes else None
        primary_color = main_palette.primary if main_palette else "#0A0A0A"
        accent_color = main_palette.accent if main_palette else "#B76E79"

        generation_prompt_block = (
            f"SkyyRose luxury streetwear moodboard — {collection_display} collection, {season}. "
            f"{concept_text}. "
            f"Color palette: {primary_color} primary, {accent_color} accent. "
            f"Location: {locations[0] if locations else 'urban Bay Area'}. "
            f"Lighting: {lighting}. "
            f"Typography: {typography}. "
            f"Brand: '' Oakland streetwear luxury. "
            f"High-end editorial moodboard aesthetic."
        )

        title = f"{collection_display} {season} Moodboard"
        if concept:
            title = f"{concept} — {collection_display} {season}"

        return Moodboard(
            moodboard_id=moodboard_id,
            title=title,
            collection=collection,
            season=season,
            concept_summary=concept_text,
            color_story=color_story,
            texture_references=texture_refs,
            visual_references=visual_references,
            typography_direction=typography,
            lighting_mood=lighting,
            location_references=locations,
            cultural_touchpoints=cultural,
            brand_anchors=brand_anchors,
            generation_prompt_block=generation_prompt_block,
        )

    def compose_all_collections(self, season: str = "FW26") -> list[Moodboard]:
        """Compose moodboards for all four SkyyRose collections."""
        collections = ["black-rose", "love-hurts", "signature", "kids-capsule"]
        return [self.compose(c, season) for c in collections]
