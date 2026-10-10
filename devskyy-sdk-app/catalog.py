"""Sample SkyyRose product catalog for the Agent SDK starter.

IMPORTANT — this is DEMO data, decoupled on purpose.
The canonical SkyyRose catalog is `skyyrose-catalog.csv` (the project's source of truth).
This module hard-codes a tiny, self-contained sample so the starter runs anywhere without
the SOT files. When you wire this agent to the real store, replace `PRODUCTS` with a loader
that reads the canonical CSV / WooCommerce REST instead of editing these literals.

Each product is an immutable record (a frozen dataclass). Lookups return new lists; nothing
here mutates the catalog in place.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CollectionMeta:
    """Per-collection canon. Lives in data (behind a tool) so the agent fetches EXACT
    grounded text rather than paraphrasing brand canon from memory — the source of
    cross-collection mix-ups. For production, confirm against the brand docs / identity.json.
    """

    accent: str  # brand hex token
    ethos: str  # the one-line canon for THIS collection — never cross-wire between collections
    lineage: str  # what the collection draws from / who it's for


# Brand collections, accent tokens, and per-collection canon (SkyyRose brand canon).
# Each ethos is collection-specific: "the bloodline that raised me" is Love Hurts ONLY;
# Black Rose is armor. Never attribute one collection's line to another.
COLLECTIONS: dict[str, CollectionMeta] = {
    "Signature": CollectionMeta(
        accent="#D4AF37",  # Gold
        ethos="The flagship line — where '' begins. "
        "Foundational pieces built to outlast the trend cycle.",
        lineage="Gold-standard staples; the bedrock of the house.",
    ),
    "Black Rose": CollectionMeta(
        accent="#C0C0C0",  # Silver
        ethos="Armor. Cut for the days that demand it — beauty with a hard edge.",
        lineage="Matte black, silver hardware, protective tailoring.",
    ),
    "Love Hurts": CollectionMeta(
        accent="#DC143C",  # Crimson
        ethos="The bloodline that raised me — love and damage stitched into the same seam.",
        lineage="Crimson heat, varsity weight, worn-in emotion.",
    ),
    "Kids Capsule": CollectionMeta(
        accent="#B76E79",  # Rose Gold
        ethos="For the next generation — the same concrete-born luxury, sized small.",
        lineage="Rose-gold softness; built for kids who outgrow nothing about it.",
    ),
}


def collection_meta(name: str) -> tuple[str, CollectionMeta] | None:
    """Resolve a collection name case-insensitively to (canonical_name, meta), or None."""
    target = name.strip().lower()
    for canonical, meta in COLLECTIONS.items():
        if canonical.lower() == target:
            return canonical, meta
    return None


@dataclass(frozen=True)
class Product:
    """One catalog entry. Frozen so a tool handler can never accidentally mutate the catalog."""

    sku: str
    name: str
    collection: str
    price_usd: float
    sizes: tuple[str, ...]
    in_stock: bool
    description: str


# Sample inventory — a few products per collection. Illustrative, not canonical.
PRODUCTS: tuple[Product, ...] = (
    Product(
        sku="sg-001",
        name="Concrete Rose Hoodie",
        collection="Signature",
        price_usd=185.00,
        sizes=("S", "M", "L", "XL"),
        in_stock=True,
        description="Heavyweight French-terry hoodie with gold foil rose embroidery at the chest.",
    ),
    Product(
        sku="sg-007",
        name="Foundation Cargo Pant",
        collection="Signature",
        price_usd=210.00,
        sizes=("28", "30", "32", "34", "36"),
        in_stock=True,
        description="Structured cargo with reinforced knees and a tonal gold zip pull.",
    ),
    Product(
        sku="br-001",
        name="Black Rose Bomber",
        collection="Black Rose",
        price_usd=320.00,
        sizes=("S", "M", "L", "XL"),
        in_stock=False,
        description="Satin-lined bomber in matte black with a silver-thread rose on the back panel.",
    ),
    Product(
        sku="br-012",
        name="Armor Knit Crew",
        collection="Black Rose",
        price_usd=145.00,
        sizes=("S", "M", "L", "XL", "XXL"),
        in_stock=True,
        description="Ribbed knit crewneck; silver hardware at the cuffs. Built like armor.",
    ),
    Product(
        sku="lh-005",
        name="Love Hurts Varsity Jacket",
        collection="Love Hurts",
        price_usd=395.00,
        sizes=("S", "M", "L", "XL"),
        in_stock=True,
        description="Wool-body varsity with crimson leather sleeves and chain-stitch lettering.",
    ),
    Product(
        sku="lh-009",
        name="Bloodline Graphic Tee",
        collection="Love Hurts",
        price_usd=75.00,
        sizes=("S", "M", "L", "XL"),
        in_stock=True,
        description="Boxy cotton tee, crimson screen-print across the chest.",
    ),
    Product(
        sku="kc-003",
        name="Little Concrete Joggers",
        collection="Kids Capsule",
        price_usd=68.00,
        sizes=("2T", "3T", "4T", "5"),
        in_stock=True,
        description="Soft fleece joggers with a rose-gold drawcord. Sized for the next generation.",
    ),
)


# Index by SKU once, at import time, for O(1) exact lookups.
_BY_SKU: dict[str, Product] = {p.sku: p for p in PRODUCTS}


def find_products(query: str) -> list[Product]:
    """Return products whose SKU or name matches `query` (case-insensitive substring).

    An exact SKU match short-circuits to a single result; otherwise we substring-match
    against both SKU and name so "rose" finds the Concrete Rose Hoodie and the Black Rose Bomber.
    """
    q = query.strip().lower()
    if not q:
        return []

    exact = _BY_SKU.get(q)
    if exact is not None:
        return [exact]

    return [p for p in PRODUCTS if q in p.sku.lower() or q in p.name.lower()]


def products_in_collection(collection: str) -> list[Product]:
    """Return every product in `collection`, matched case-insensitively against COLLECTIONS keys."""
    target = collection.strip().lower()
    return [p for p in PRODUCTS if p.collection.lower() == target]
