"""
Fashion context builder for SkyyRose Elite Studio.

Assembles a complete FashionContext from SKU, garment type, collection,
and season. Loads product data from the product catalog CSV.

""
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Product catalog path
# ---------------------------------------------------------------------------

from skyyrose.core.catalog_loader import CATALOG_CSV as _CATALOG_PATH
from skyyrose.core.catalog_loader import read_catalog_rows

_DEFAULT_SEASON = "FW26"

# Compatibility handle for callers; each read follows current registry facts.
_catalog_cache: dict[str, dict[str, str]] | None = None


def _load_catalog() -> dict[str, dict[str, str]]:
    """Load current registry product facts into a dict keyed by SKU."""
    global _catalog_cache
    catalog: dict[str, dict[str, str]] = {}
    try:
        for row in read_catalog_rows(_CATALOG_PATH):
            sku = row["sku"].strip().lower()
            if not sku:
                continue
            catalog[sku] = {key: value or "" for key, value in row.items()}
    except FileNotFoundError:
        logger.warning("Product catalog not found at %s", _CATALOG_PATH)
    except Exception as exc:
        logger.warning("Failed to load product catalog: %s", exc)

    _catalog_cache = catalog
    return catalog


# ---------------------------------------------------------------------------
# Garment type inference from catalog data
# ---------------------------------------------------------------------------

_GARMENT_TYPE_KEYWORDS: dict[str, str] = {
    "hoodie": "hoodie",
    "crewneck": "crewneck",
    "jersey": "jersey",
    "joggers": "joggers",
    "sweatpants": "sweatpants",
    "shorts": "shorts",
    "shirt": "shirt",
    "tee": "shirt",
    "sherpa jacket": "jacket",
    "varsity jacket": "varsity jacket",
    "jacket": "jacket",
    "beanie": "beanie",
    "fanny": "fanny pack",
    "set": "set",
}


def _infer_garment_type(product_name: str) -> str:
    """Infer garment type from product name."""
    name_lower = product_name.lower()
    for keyword, garment_type in _GARMENT_TYPE_KEYWORDS.items():
        if keyword in name_lower:
            return garment_type
    return "garment"


# ---------------------------------------------------------------------------
# Frozen context dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FashionContext:
    """Immutable assembled fashion context for a product render task.

    Combines garment knowledge, trend signals, photography direction,
    color palette, and styling rules into a single coherent context block.
    """

    garment_type: str
    fabric: str
    collection_dna: str
    season: str
    photography_style: str
    color_palette: tuple[str, ...]  # ordered hex values: primary, secondary, accent
    styling_notes: str
    size_range: str
    rendering_spec: str
    trend_alignment: tuple[str, ...]


# ---------------------------------------------------------------------------
# Context builder
# ---------------------------------------------------------------------------


class FashionContextBuilder:
    """Builds a FashionContext by assembling all fashion intelligence modules.

    Instantiates the underlying advisors lazily on first use.
    """

    def __init__(self) -> None:
        self._kb = None
        self._trends = None
        self._photography = None
        self._sizing = None
        self._color = None
        self._editorial = None
        self._materials = None

    def _get_kb(self):  # type: ignore[return]
        if self._kb is None:
            from .knowledge import FashionKnowledgeBase

            self._kb = FashionKnowledgeBase()
        return self._kb

    def _get_trends(self):  # type: ignore[return]
        if self._trends is None:
            from .trends import TrendAdvisor

            self._trends = TrendAdvisor()
        return self._trends

    def _get_photography(self):  # type: ignore[return]
        if self._photography is None:
            from .photography import PhotographyDirector

            self._photography = PhotographyDirector()
        return self._photography

    def _get_sizing(self):  # type: ignore[return]
        if self._sizing is None:
            from .sizing import SizingAdvisor

            self._sizing = SizingAdvisor()
        return self._sizing

    def _get_color(self):  # type: ignore[return]
        if self._color is None:
            from .colorway import ColorAdvisor

            self._color = ColorAdvisor()
        return self._color

    def _get_editorial(self):  # type: ignore[return]
        if self._editorial is None:
            from .editorial import EditorialDirector

            self._editorial = EditorialDirector()
        return self._editorial

    def _get_materials(self):  # type: ignore[return]
        if self._materials is None:
            from .materials import MaterialsExpert

            self._materials = MaterialsExpert()
        return self._materials

    def build(
        self,
        sku: str = "",
        garment_type: str = "",
        collection: str = "",
        season: str = _DEFAULT_SEASON,
    ) -> FashionContext:
        """Build a FashionContext from explicit parameters.

        Args:
            sku: Optional SKU — used for logging only here.
            garment_type: Garment type name (hoodie, joggers, etc.)
            collection: Collection slug (black-rose, love-hurts, signature, kids-capsule)
            season: Season code (FW26, SS27)

        Returns:
            Fully assembled FashionContext.
        """
        kb = self._get_kb()
        garment = kb.get_garment(garment_type) if garment_type else None
        fabric = (
            garment.default_fabric if garment else kb.get_default_fabric_for_garment(garment_type)
        )

        # Photography direction
        photo_dir = self._get_photography()
        photo_style = photo_dir.recommend_style(garment_type, collection)

        # Color palette
        color_adv = self._get_color()
        palette = color_adv.get_collection_palette(collection)
        color_tuple = (palette.primary, palette.secondary, palette.accent)

        # Collection DNA
        from skyyrose.elite_studio.prompts.templates import COLLECTION_DNA

        from .knowledge import BRAND_TAGLINE

        dna_data = COLLECTION_DNA.get(collection.lower(), {})
        collection_dna = (
            f"{dna_data.get('name', collection)}: {dna_data.get('aesthetic', '')}. "
            f"Mood: {dna_data.get('mood', '')}. "
            f"Tagline: {dna_data.get('tagline', BRAND_TAGLINE)}"
        ).strip()

        # Sizing
        sizing_adv = self._get_sizing()
        sizing_guide = sizing_adv.get_guideline(garment_type, collection)

        # Material rendering spec
        materials = self._get_materials()
        spec = materials.get_rendering_spec(fabric)
        rendering_spec = spec.reference_description if spec else f"Standard rendering for {fabric}."

        # Trend alignment
        trends = self._get_trends()
        trend_notes = trends.get_trend_notes_for_garment(garment_type)
        trend_alignment = tuple(trend_notes[:3]) if trend_notes else ()

        # Styling notes
        editorial = self._get_editorial()
        styling_rule = editorial.get_styling(garment_type, collection)
        styling_notes = (
            f"Pairings: {', '.join(styling_rule.pairing_suggestions[:2])}. "
            f"Occasion: {styling_rule.occasion}. "
            f"Context: {styling_rule.collection_context}"
        )

        return FashionContext(
            garment_type=garment_type or "garment",
            fabric=fabric,
            collection_dna=collection_dna,
            season=season,
            photography_style=photo_style,
            color_palette=color_tuple,
            styling_notes=styling_notes,
            size_range=sizing_guide.size_range,
            rendering_spec=rendering_spec,
            trend_alignment=trend_alignment,
        )

    def build_from_product_catalog(self, sku: str) -> FashionContext:
        """Build a FashionContext by loading product data from the catalog CSV.

        Args:
            sku: Product SKU (e.g. "br-001").

        Returns:
            FashionContext assembled from catalog data.
            Falls back to generic context if SKU not found.
        """
        catalog = _load_catalog()
        sku_normalized = sku.strip().lower()
        row = catalog.get(sku_normalized)

        if not row:
            logger.warning("SKU %s not found in product catalog — using defaults", sku)
            return self.build(
                sku=sku, garment_type="garment", collection="", season=_DEFAULT_SEASON
            )

        collection = row.get("collection", "").strip()
        product_name = row.get("name", "")
        garment_type = _infer_garment_type(product_name)

        return self.build(
            sku=sku_normalized,
            garment_type=garment_type,
            collection=collection,
            season=_DEFAULT_SEASON,
        )
