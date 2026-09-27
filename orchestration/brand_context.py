"""
SkyyRose Brand Context Layer
============================

Injects brand DNA into all LLM interactions for consistent voice.

Features:
- Brand knowledge base (colors, tone, values)
- System prompt injection
- Product catalog context
- Collection-specific styling

Author: DevSkyy Platform Team
Version: 1.0.0
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from typing import Any

from llm import Message

logger = logging.getLogger(__name__)

# ~2000 tokens for English prose at ~4 chars/token. The ceiling exists so the
# catalog digest never crowds out the agent's real system prompt. Truncation
# inside compile_catalog_digest guarantees the block stays within budget.
_CATALOG_DIGEST_CHAR_BUDGET: int = 7500


# =============================================================================
# Brand Knowledge Base
# =============================================================================


class Collection(StrEnum):
    """SkyyRose collections."""

    BLACK_ROSE = "BLACK_ROSE"
    SIGNATURE = "SIGNATURE"
    MIDNIGHT_BLOOM = "MIDNIGHT_BLOOM"
    LOVE_HURTS = "LOVE_HURTS"


SKYYROSE_BRAND: dict[str, Any] = {
    "name": "The Skyy Rose Collection",
    "tagline": "Luxury Streetwear with Soul",
    "philosophy": "",
    "location": "Oakland, California",
    "tone": {
        "primary": "Elegant, empowering, romantic, bold",
        "descriptors": [
            "sophisticated yet accessible",
            "poetic but not pretentious",
            "confident without arrogance",
            "romantic with edge",
        ],
        "avoid": [
            "generic fashion buzzwords",
            "overly casual language",
            "aggressive or harsh tones",
            "clichéd luxury language",
        ],
    },
    "colors": {
        "primary": {"name": "Black Rose", "hex": "#1A1A1A", "rgb": "26, 26, 26"},
        "accent": {"name": "Rose Gold", "hex": "#D4AF37", "rgb": "212, 175, 55"},
        "highlight": {"name": "Deep Rose", "hex": "#8B0000", "rgb": "139, 0, 0"},
        "ivory": {"name": "Ivory", "hex": "#F5F5F0", "rgb": "245, 245, 240"},
        "obsidian": {"name": "Obsidian", "hex": "#0D0D0D", "rgb": "13, 13, 13"},
    },
    "typography": {
        "heading": "Playfair Display",
        "body": "Inter",
        "accent": "Cormorant Garamond",
    },
    "target_audience": {
        "age_range": "18-35",
        "description": "Fashion-forward individuals who value self-expression",
        "interests": ["streetwear", "luxury fashion", "self-expression", "art", "music"],
        "values": ["authenticity", "quality", "individuality", "emotional connection"],
    },
    "product_types": [
        "hoodies",
        "tees",
        "bombers",
        "track pants",
        "accessories",
        "caps",
        "beanies",
    ],
    "quality_descriptors": [
        "premium heavyweight cotton",
        "meticulous construction",
        "attention to detail",
        "limited edition exclusivity",
        "elevated street poetry",
    ],
}


COLLECTION_CONTEXT: dict[Collection, dict[str, Any]] = {
    Collection.BLACK_ROSE: {
        "name": "Black Rose",
        "tagline": "Limited Edition Exclusivity",
        "mood": "mysterious, sophisticated, rare, coveted",
        "colors": "deep black, subtle rose gold accents, matte finish",
        "style": "dark elegance, limited edition, exclusive drops",
        "description": "The pinnacle of SkyyRose luxury. Each Black Rose piece is a limited release, crafted for those who understand that true style is rare.",
    },
    Collection.SIGNATURE: {
        "name": "Signature",
        "tagline": "Timeless Essentials",
        "mood": "classic, versatile, foundational, elevated basics",
        "colors": "clean neutrals, rose gold details, ivory accents",
        "style": "essential wardrobe, everyday luxury, refined simplicity",
        "description": "The foundation of SkyyRose style. Signature pieces are the building blocks of a discerning wardrobe—timeless, versatile, unmistakably premium.",
    },
    Collection.MIDNIGHT_BLOOM: {
        "name": "Midnight Bloom",
        "tagline": "Beauty in Darkness",
        "mood": "romantic, mysterious, nocturnal, blooming",
        "colors": "deep purples, midnight blue, silver accents",
        "style": "romantic darkness, floral motifs, night-inspired",
        "description": "For those who find beauty in the shadows. Midnight Bloom celebrates the romance of darkness, where flowers bloom under moonlight.",
    },
    Collection.LOVE_HURTS: {
        "name": "Love Hurts",
        "tagline": "Feel Everything",
        "mood": "passionate, vulnerable, powerful, emotional",
        "colors": "deep reds, black, heart motifs, distressed textures",
        "style": "emotional expression, storytelling through design",
        "description": "Raw emotion worn proudly. Love Hurts transforms the beautiful pain of human experience into wearable art.",
    },
}


# System prompt template
BRAND_SYSTEM_PROMPT = """You are an AI assistant for The Skyy Rose Collection, a luxury streetwear brand based in Oakland, California.

## Brand Voice
{tone_primary}

When writing for SkyyRose:
{tone_descriptors}

Avoid:
{tone_avoid}

## Brand Colors
- Primary: {color_primary} ({color_primary_hex})
- Accent: {color_accent} ({color_accent_hex})
- Highlight: {color_highlight} ({color_highlight_hex})

## Target Audience
{target_audience}

## Quality Language
Use these descriptors: {quality_descriptors}

{collection_context}

Maintain consistent brand voice across all content. Be {tone_primary}."""


# =============================================================================
# Brand Context Injector
# =============================================================================


@dataclass
class BrandContextInjector:
    """
    Injects SkyyRose brand context into LLM prompts.

    Usage:
        injector = BrandContextInjector()

        # Inject brand context into messages
        messages = injector.inject([
            Message.user("Write a product description for the Black Rose Hoodie")
        ])

        # With specific collection
        messages = injector.inject(
            [Message.user("Write marketing copy")],
            collection=Collection.LOVE_HURTS
        )
    """

    include_colors: bool = True
    include_audience: bool = True
    include_quality: bool = True
    compact_mode: bool = False

    def get_system_prompt(self, collection: Collection | None = None) -> str:
        """
        Generate brand-aware system prompt.

        Args:
            collection: Optional specific collection context

        Returns:
            Formatted system prompt with brand DNA
        """
        brand = SKYYROSE_BRAND

        # Format tone descriptors
        tone_descriptors = "\n".join(f"- {d}" for d in brand["tone"]["descriptors"])
        tone_avoid = "\n".join(f"- {a}" for a in brand["tone"]["avoid"])

        # Collection context
        collection_context = ""
        if collection:
            coll = COLLECTION_CONTEXT[collection]
            collection_context = f"""
## Current Collection: {coll["name"]}
Tagline: {coll["tagline"]}
Mood: {coll["mood"]}
Colors: {coll["colors"]}
Style: {coll["style"]}
Description: {coll["description"]}"""

        # Format quality descriptors
        quality = ", ".join(brand["quality_descriptors"][:4])

        # Target audience
        audience = brand["target_audience"]
        audience_str = f"{audience['description']} (ages {audience['age_range']})"

        prompt = BRAND_SYSTEM_PROMPT.format(
            tone_primary=brand["tone"]["primary"],
            tone_descriptors=tone_descriptors,
            tone_avoid=tone_avoid,
            color_primary=brand["colors"]["primary"]["name"],
            color_primary_hex=brand["colors"]["primary"]["hex"],
            color_accent=brand["colors"]["accent"]["name"],
            color_accent_hex=brand["colors"]["accent"]["hex"],
            color_highlight=brand["colors"]["highlight"]["name"],
            color_highlight_hex=brand["colors"]["highlight"]["hex"],
            target_audience=audience_str,
            quality_descriptors=quality,
            collection_context=collection_context,
        )

        return prompt.strip()

    def get_compact_prompt(self, collection: Collection | None = None) -> str:
        """Get a compact version of the brand prompt."""
        brand = SKYYROSE_BRAND

        prompt = f"""SkyyRose Brand Voice: {brand["tone"]["primary"]}
Colors: Black Rose (#1A1A1A), Rose Gold (#D4AF37), Deep Rose (#8B0000)
Style: Luxury streetwear, Oakland CA. {brand["tagline"]}."""

        if collection:
            coll = COLLECTION_CONTEXT[collection]
            prompt += f"\nCollection: {coll['name']} - {coll['tagline']}. {coll['mood']}."

        return prompt

    def inject(
        self,
        messages: list[Message],
        collection: Collection | None = None,
        prepend_system: bool = True,
    ) -> list[Message]:
        """
        Inject brand context into message list.

        Args:
            messages: Original messages
            collection: Optional collection context
            prepend_system: Whether to add system message at start

        Returns:
            Messages with brand context injected
        """
        if not prepend_system:
            return messages

        # Get appropriate prompt
        if self.compact_mode:
            system_content = self.get_compact_prompt(collection)
        else:
            system_content = self.get_system_prompt(collection)

        # Check if first message is already a system message
        if messages and messages[0].role == "system":
            # Prepend brand context to existing system message
            enhanced = Message.system(f"{system_content}\n\n{messages[0].content}")
            return [enhanced] + list(messages[1:])

        # Add new system message
        return [Message.system(system_content)] + list(messages)

    def get_product_context(
        self,
        product_name: str,
        product_type: str,
        collection: Collection | None = None,
        price: float | None = None,
    ) -> str:
        """
        Generate product-specific context for LLM.

        Args:
            product_name: Name of the product
            product_type: Type (hoodie, tee, bomber, etc.)
            collection: Which collection it belongs to
            price: Optional price point

        Returns:
            Product context string
        """
        context = f"Product: {product_name}\nType: {product_type}"

        if collection:
            coll = COLLECTION_CONTEXT[collection]
            context += f"\nCollection: {coll['name']} ({coll['tagline']})"
            context += f"\nMood: {coll['mood']}"

        if price:
            context += f"\nPrice Point: ${price:.2f}"

        # Add relevant quality descriptors
        if product_type.lower() in ["hoodie", "sweatshirt"]:
            context += "\nQuality: Premium heavyweight cotton, meticulous construction"
        elif product_type.lower() in ["bomber", "jacket"]:
            context += "\nQuality: Premium materials, satin lining, quality hardware"
        elif product_type.lower() in ["tee", "t-shirt"]:
            context += "\nQuality: Heavyweight cotton, relaxed fit, quality construction"

        return context

    def get_3d_generation_context(
        self,
        product_name: str,
        product_type: str,
        collection: Collection | None = None,
        garment_type: str | None = None,
    ) -> str:
        """
        Generate 3D generation-specific context for Tripo3D/FASHN.

        Args:
            product_name: Name of the product
            product_type: Type (hoodie, tee, bomber, etc.)
            collection: Which collection it belongs to
            garment_type: Specific garment type for try-on

        Returns:
            3D generation context string
        """
        brand = SKYYROSE_BRAND
        context = f"""3D Asset Generation Context for {product_name}

## Brand Aesthetic
- Maintain SkyyRose brand DNA: {brand["tone"]["primary"]}
- Primary Color: {brand["colors"]["primary"]["name"]} {brand["colors"]["primary"]["hex"]}
- Accent Color: {brand["colors"]["accent"]["name"]} {brand["colors"]["accent"]["hex"]}
- Highlight Color: {brand["colors"]["highlight"]["name"]} {brand["colors"]["highlight"]["hex"]}
- Style: Luxury streetwear with meticulous construction

## Product Details
- Name: {product_name}
- Type: {product_type}
- Quality Level: Premium, production-ready 3D model"""

        if collection:
            coll = COLLECTION_CONTEXT[collection]
            context += f"\n- Collection: {coll['name']}"
            context += f"\n- Collection Mood: {coll['mood']}"
            context += f"\n- Collection Colors: {coll['colors']}"

        if garment_type:
            context += f"\n- Garment Type: {garment_type}"

        context += """

## 3D Generation Requirements
- Format: GLB (web-optimized), USDZ (AR-compatible)
- Quality: High-poly, production-ready geometry
- Textures: Premium finish, brand-aligned materials
- Details: Seams, stitching, fabric drape authenticity
- Color Accuracy: Match brand color palette precisely
- Lighting: Professional studio lighting ready

## File Specifications
- Polycount: Optimized for web (target: 50k-200k polygons)
- Texture Resolution: 2048x2048 minimum
- File Size: Optimized for fast loading
- Metadata: Brand-tagged, collection-categorized"""

        return context.strip()


# =============================================================================
# Catalog Context — live CSV-backed digest for agent system prompts
# =============================================================================


@dataclass(frozen=True)
class CatalogSummary:
    """Aggregated facts about the current catalog state for one collection."""

    collection: str
    sku_count: int
    live_count: int
    preorder_count: int
    draft_count: int
    price_min: float | None
    price_max: float | None
    sample_names: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class CatalogContext:
    """Immutable snapshot of the canonical catalog, keyed by collection slug."""

    csv_mtime_ns: int
    summaries: tuple[CatalogSummary, ...]

    @property
    def total_skus(self) -> int:
        return sum(s.sku_count for s in self.summaries)


# Role-specific focus: each tuple is the subset of facts a role needs most.
# Roles not listed here fall through to DEFAULT_ROLE_FOCUS.
_ROLE_FOCUS: dict[str, tuple[str, ...]] = {
    "imagery": ("collection", "sku_count", "sample_names"),
    "ecommerce_photography": ("collection", "sku_count", "sample_names"),
    "social_media": ("collection", "sku_count", "live_count", "preorder_count"),
    "competitor_scout": ("collection", "sku_count", "price_min", "price_max"),
    "theme_builder": ("collection", "sku_count", "live_count", "draft_count"),
    "garment_3d": ("collection", "sku_count", "sample_names"),
    "seo_content": ("collection", "sku_count", "price_min", "price_max"),
    "qa": ("collection", "sku_count", "live_count", "preorder_count", "draft_count"),
}
_DEFAULT_ROLE_FOCUS: tuple[str, ...] = (
    "collection",
    "sku_count",
    "live_count",
    "preorder_count",
)


def _canonical_catalog_path() -> Path:
    """Path to the canonical catalog CSV.

    Prefers skyyrose.core.catalog_loader.CATALOG_CSV (the shared constant)
    and honors SKYYROSE_CATALOG_PATH env override for tests / migrations.
    Falls back to a computed path if skyyrose.core isn't importable (e.g.
    isolated test harness).
    """
    override = os.environ.get("SKYYROSE_CATALOG_PATH")
    if override:
        return Path(override)
    try:
        from skyyrose.core.catalog_loader import CATALOG_CSV

        return CATALOG_CSV
    except ImportError:
        here = Path(__file__).resolve()
        return (
            here.parents[1]
            / "wordpress-theme"
            / "skyyrose-flagship"
            / "data"
            / "skyyrose-catalog.csv"
        )


def _catalog_mtime_ns(path: Path) -> int:
    """mtime of the canonical CSV, or 0 if missing. Drives cache invalidation."""
    try:
        return path.stat().st_mtime_ns
    except FileNotFoundError:
        return 0


def load_catalog_context(path: Path | None = None) -> CatalogContext:
    """Read the canonical catalog CSV and build a CatalogContext snapshot.

    Uses skyyrose.core.catalog_loader when available (shared canonical reader);
    falls back to the stdlib csv module so this function works even in
    environments where skyyrose.core isn't on the import path (e.g. isolated
    test harnesses).
    """
    csv_path = path or _canonical_catalog_path()
    mtime = _catalog_mtime_ns(csv_path)

    rows = _read_rows(csv_path)
    by_collection: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        collection = (row.get("collection") or "").strip().lower() or "unknown"
        by_collection.setdefault(collection, []).append(row)

    summaries: list[CatalogSummary] = []
    for collection, items in sorted(by_collection.items()):
        prices: list[float] = []
        live = preorder = draft = 0
        names: list[str] = []
        for row in items:
            try:
                price = float((row.get("price") or "").strip() or 0.0)
                if price > 0:
                    prices.append(price)
            except ValueError:
                pass
            published = (row.get("published") or "").strip() == "1"
            is_preorder = (row.get("is_preorder") or "").strip() == "1"
            if is_preorder:
                preorder += 1
            elif published:
                live += 1
            else:
                draft += 1
            name = (row.get("name") or "").strip()
            if name and len(names) < 3:
                names.append(name)

        summaries.append(
            CatalogSummary(
                collection=collection,
                sku_count=len(items),
                live_count=live,
                preorder_count=preorder,
                draft_count=draft,
                price_min=min(prices) if prices else None,
                price_max=max(prices) if prices else None,
                sample_names=tuple(names),
            )
        )

    return CatalogContext(
        csv_mtime_ns=mtime,
        summaries=tuple(summaries),
    )


def _read_rows(csv_path: Path) -> list[dict[str, str]]:
    """Read catalog rows. Prefer the shared canonical loader; fall back gracefully."""
    try:
        from skyyrose.core.catalog_loader import read_catalog_rows
    except ImportError:
        import csv

        if not csv_path.exists():
            return []
        with csv_path.open(newline="", encoding="utf-8") as f:
            return [row for row in csv.DictReader(f) if (row.get("sku") or "").strip()]
    return read_catalog_rows(csv_path)


def _format_summary(summary: CatalogSummary, focus: tuple[str, ...]) -> str:
    """Render a CatalogSummary as a compact text block, filtered by role focus."""
    lines: list[str] = [f"### {summary.collection.replace('-', ' ').title()}"]
    if "sku_count" in focus:
        lines.append(f"- SKUs: {summary.sku_count}")
    status_parts: list[str] = []
    if "live_count" in focus:
        status_parts.append(f"{summary.live_count} live")
    if "preorder_count" in focus:
        status_parts.append(f"{summary.preorder_count} pre-order")
    if "draft_count" in focus:
        status_parts.append(f"{summary.draft_count} draft")
    if status_parts:
        lines.append(f"- Status: {', '.join(status_parts)}")
    if (
        ("price_min" in focus or "price_max" in focus)
        and summary.price_min is not None
        and summary.price_max is not None
    ):
        lines.append(f"- Price range: ${summary.price_min:.0f}–${summary.price_max:.0f}")
    if "sample_names" in focus and summary.sample_names:
        sample = ", ".join(summary.sample_names)
        lines.append(f"- Featured: {sample}")
    return "\n".join(lines)


# Cache the context so digest regeneration doesn't re-parse the CSV each time.
# maxsize=4 is generous — the key is mtime, which changes only when the CSV is
# edited, and only one or two mtimes are live at once in practice.
@lru_cache(maxsize=4)
def _cached_catalog_context(mtime_ns: int) -> CatalogContext:
    return load_catalog_context()


# 13 roles × a handful of live mtimes → maxsize=16 is right-sized.
@lru_cache(maxsize=16)
def _cached_digest(role: str, mtime_ns: int) -> str:
    """Compile the digest; keyed on (role, csv_mtime_ns) so edits invalidate."""
    context = _cached_catalog_context(mtime_ns)
    focus = _ROLE_FOCUS.get(role, _DEFAULT_ROLE_FOCUS)

    header = (
        f"## SkyyRose Catalog Digest — live from canonical CSV\n"
        f"Total SKUs: {context.total_skus} across {len(context.summaries)} collections. "
        f'Brand philosophy: "{SKYYROSE_BRAND["philosophy"]}".\n'
    )
    sections = [_format_summary(s, focus) for s in context.summaries]
    block = header + "\n" + "\n\n".join(sections)

    if len(block) > _CATALOG_DIGEST_CHAR_BUDGET:
        # Truncate on a UTF-8 code-point boundary so we never split a multi-byte
        # sequence (e.g. accented brand names, em-dashes in collection taglines).
        encoded = block.encode("utf-8")[: _CATALOG_DIGEST_CHAR_BUDGET - 3]
        block = encoded.decode("utf-8", errors="ignore") + "..."
    return block


def compile_catalog_digest(role: str) -> str:
    """Return a compact catalog digest tailored to the given agent role.

    The block is deterministic for a given CSV state — it changes only when
    the CSV's mtime changes. Cached via lru_cache keyed on (role, mtime).
    Always stays within _CATALOG_DIGEST_CHAR_BUDGET characters.
    """
    return _cached_digest(role, _catalog_mtime_ns(_canonical_catalog_path()))


def get_brand_context(
    role: str,
    collection: Collection | None = None,
    *,
    include_catalog: bool | None = None,
) -> str:
    """Unified brand + catalog context block for any agent's system prompt.

    Combines the compact brand prompt (BrandContextInjector.get_compact_prompt)
    with the role-tuned catalog digest. The catalog digest can be disabled
    globally via SKYYROSE_BRAND_INJECT=0.

    Args:
        role: Agent role name — drives catalog digest focus
        collection: Optional active collection for the compact brand prompt
        include_catalog: Explicit override. None = respect env var
    """
    if include_catalog is None:
        include_catalog = os.environ.get("SKYYROSE_BRAND_INJECT", "1") != "0"

    brand_block = BrandContextInjector(compact_mode=True).get_compact_prompt(collection)
    if not include_catalog:
        return brand_block
    try:
        digest = compile_catalog_digest(role)
    except Exception as exc:  # noqa: BLE001 — degrade gracefully if CSV missing
        logger.warning("catalog digest unavailable for role=%s: %s", role, exc)
        return brand_block
    return f"{brand_block}\n\n{digest}"


# =============================================================================
# Convenience Functions
# =============================================================================


def get_brand_system_prompt(collection: Collection | None = None) -> str:
    """Get SkyyRose brand system prompt."""
    return BrandContextInjector().get_system_prompt(collection)


def inject_brand_context(
    messages: list[Message],
    collection: Collection | None = None,
) -> list[Message]:
    """Inject brand context into messages."""
    return BrandContextInjector().inject(messages, collection)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "BrandContextInjector",
    "CatalogContext",
    "CatalogSummary",
    "Collection",
    "SKYYROSE_BRAND",
    "COLLECTION_CONTEXT",
    "compile_catalog_digest",
    "get_brand_context",
    "get_brand_system_prompt",
    "inject_brand_context",
    "load_catalog_context",
]
