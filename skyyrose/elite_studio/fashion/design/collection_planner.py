"""
Collection planning tools for SkyyRose Elite Studio.

CollectionPlanner builds structured collection plans from brief inputs,
using fashion intelligence and product catalog data.

"""

from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class CollectionPlan:
    """Immutable structured plan for a SkyyRose collection."""

    plan_id: str
    collection: str
    season: str
    theme: str
    product_categories: tuple[str, ...]  # garment types to include
    hero_pieces: tuple[str, ...]  # 2-3 hero SKU names or descriptions
    colorway_strategy: str
    pricing_strategy: str
    trend_hooks: tuple[str, ...]
    photography_approach: str
    launch_sequence: tuple[str, ...]  # ordered product launch order
    editorial_direction: str
    target_skus_count: int


class CollectionPlanner:
    """Plans SkyyRose collection rollouts using fashion intelligence.

    Produces structured CollectionPlan objects ready for product team review.
    """

    def __init__(self) -> None:
        from ..colorway import ColorAdvisor
        from ..editorial import EditorialDirector
        from ..photography import PhotographyDirector
        from ..trends import TrendAdvisor

        self._trends = TrendAdvisor()
        self._color = ColorAdvisor()
        self._editorial = EditorialDirector()
        self._photography = PhotographyDirector()

    def plan_collection(
        self,
        collection: str,
        season: str,
        theme: str,
        target_skus_count: int = 8,
    ) -> CollectionPlan:
        """Build a collection plan for a given collection and season."""
        plan_id = str(uuid.uuid4())[:8]

        # Get palette
        palette = self._color.get_collection_palette(collection)

        # Get editorial direction
        editorial_notes = self._editorial.get_collection_editorial_notes(collection)

        # Trend hooks for this collection
        all_trends = self._trends.get_current_trends(season)
        rising_trends = [t for t in all_trends if t.direction in ("rising", "peak")]
        trend_hooks = tuple(t.name for t in rising_trends[:4])

        # Collection-specific product category strategy
        category_map = {
            "black-rose": ("hoodie", "crewneck", "jersey", "joggers", "shorts", "jacket"),
            "love-hurts": ("joggers", "shorts", "varsity jacket", "fanny pack"),
            "signature": (
                "shirt",
                "shorts",
                "hoodie",
                "crewneck",
                "sweatpants",
                "beanie",
                "jacket",
            ),
            "kids-capsule": ("set",),
        }
        product_categories = category_map.get(collection.lower(), ("hoodie", "joggers", "shorts"))

        # Hero pieces
        hero_map = {
            "black-rose": (
                "BLACK Rose Sherpa Jacket — outerwear hero",
                "BLACK is Beautiful Jersey Series — cultural statement",
                "BLACK Rose Hoodie Signature Edition — premium anchor",
            ),
            "love-hurts": (
                "Love Hurts Varsity Jacket — collection hero ($265)",
                "Love Hurts Joggers — premium bottom ($95)",
                "The Fannie — accessible entry point ($45)",
            ),
            "signature": (
                "The Sherpa Jacket — outerwear statement",
                "Stay Golden Shirt + Shorts Set — Bay Area hero",
                "Mint & Lavender trio (Hoodie + Crewneck + Sweatpants)",
            ),
            "kids-capsule": (
                "Kids Red Set — colorblock hero",
                "Kids Purple Set — colorblock hero",
            ),
        }
        hero_pieces = hero_map.get(collection.lower(), ("Hero piece TBD",))

        # Pricing strategy
        pricing_map = {
            "black-rose": f"Entry ${25}–${65} (tees/crewneck), mid ${50}–${65} (joggers/shorts), premium ${95}+ (jacket/jersey series)",
            "love-hurts": f"Entry ${45} (fanny pack), mid ${75}–${95} (shorts/joggers), hero ${265} (varsity jacket)",
            "signature": f"Entry ${25}–${30} (tees/beanie), mid ${40}–${65} (hoodies/shorts), premium ${80}–${195} (jacket/set)",
            "kids-capsule": f"Single price point ${40} per set",
        }
        pricing_strategy = pricing_map.get(
            collection.lower(), "Tiered entry, mid, and hero pricing"
        )

        # Photography approach
        photo_style = self._photography.recommend_style("hoodie", collection)
        photo_notes = self._photography.get_prompt_additions(photo_style, collection)
        photography_approach = f"Lead with {photo_style} for hero pieces. {photo_notes[:100]}..."

        # Launch sequence — hero first, then supporting
        launch_sequences = {
            "black-rose": (
                "1. Pre-announce: BLACK Rose Sherpa Jacket (br-006)",
                "2. Drop: BLACK is Beautiful Jersey Series (br-008–011) simultaneous",
                "3. Follow: BLACK Rose Hoodie Signature Edition (br-005)",
                "4. Complete: Crewneck, Joggers, Shorts",
            ),
            "love-hurts": (
                "1. Hero launch: Love Hurts Varsity Jacket (lh-004)",
                "2. Drop: Love Hurts Joggers (lh-002) + Basketball Shorts (lh-003)",
                "3. Accessory: The Fannie (lh-006)",
            ),
            "signature": (
                "1. Hero: The Sherpa Jacket (sg-009)",
                "2. Color story: Mint & Lavender trio (sg-006, sg-013, sg-014)",
                "3. Bay Area: Stay Golden set (sg-002, sg-003)",
                "4. Essentials: Tees, Beanie, remaining pieces",
            ),
            "kids-capsule": ("1. Simultaneous drop: Red Set (kids-001) + Purple Set (kids-002)",),
        }
        launch_sequence = launch_sequences.get(
            collection.lower(), ("1. Hero launch", "2. Full collection drop")
        )

        # Colorway strategy
        colorway_strategy = (
            f"Primary: {palette.primary} ({palette.mood}). "
            f"Secondary: {palette.secondary}. "
            f"Accent: {palette.accent}. "
            f"Maintain consistent colorway across all pieces for cohesive collection identity."
        )

        return CollectionPlan(
            plan_id=plan_id,
            collection=collection,
            season=season,
            theme=theme,
            product_categories=product_categories,
            hero_pieces=hero_pieces,
            colorway_strategy=colorway_strategy,
            pricing_strategy=pricing_strategy,
            trend_hooks=trend_hooks,
            photography_approach=photography_approach,
            launch_sequence=launch_sequence,
            editorial_direction=editorial_notes,
            target_skus_count=target_skus_count,
        )

    def plan_all_collections(self, season: str = "FW26") -> list[CollectionPlan]:
        """Generate collection plans for all four SkyyRose collections."""
        themes = {
            "black-rose": "Gothic luxury meets Oakland concrete. Darkness as elevation.",
            "love-hurts": "Raw emotion as luxury. Vulnerability is the ultimate strength.",
            "signature": "West Coast prestige. Daily elevation through refined essentials.",
            "kids-capsule": "Little ones deserve luxury too. Next-gen SkyyRose.",
        }
        return [
            self.plan_collection(collection, season, theme) for collection, theme in themes.items()
        ]
