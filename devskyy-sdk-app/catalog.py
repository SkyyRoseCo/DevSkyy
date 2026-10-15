"""SkyyRose product catalog for the Agent SDK commerce agent.

Product facts come from the ONE product source of truth — the product registry at
`wordpress-theme/skyyrose-flagship/data/logo-registry.json` (the same record
`skyyrose.core.product.get_product(sku)` serves; `python -m skyyrose.core.product <sku>`
prints it). This app runs in its own uv environment and cannot import the `skyyrose`
package, so it reads the registry JSON directly, mapping only fields the registry
actually holds. Nothing here is invented: no demo products, no stock counts.

It fails closed. A missing or malformed registry raises `CatalogUnavailableError` at
import time — an empty catalog would let the agent tell customers "nothing matched"
about products that exist.

Each product is an immutable record (a frozen dataclass). Lookups return new lists;
nothing here mutates the catalog in place.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

# repo root = parents[1] of devskyy-sdk-app/catalog.py
REGISTRY_PATH = (
    Path(__file__).resolve().parents[1]
    / "wordpress-theme"
    / "skyyrose-flagship"
    / "data"
    / "logo-registry.json"
)


class CatalogUnavailableError(RuntimeError):
    """The product registry cannot be read; there is no fallback catalog."""


@dataclass(frozen=True)
class CollectionMeta:
    """Per-collection canon, read from the registry's ``collections`` section so the
    agent quotes the registered story rather than paraphrasing canon from memory.
    """

    accent: str  # collections[slug].palette.accent
    story: str  # collections[slug].story.seed — this collection's line alone
    story_ref: str  # collections[slug].story.doc_ref — the full founder story


def collection_meta(name: str) -> tuple[str, CollectionMeta] | None:
    """Resolve a collection name case-insensitively to (canonical_name, meta), or None."""
    target = name.strip().lower()
    for canonical, meta in COLLECTIONS.items():
        if canonical.lower() == target:
            return canonical, meta
    return None


# Availability is derived ONLY from registry fields. The registry holds no stock
# counts, so the agent never claims "in stock" / "sold out".
PRE_ORDER = "pre-order"
AVAILABLE = "available"
UNPUBLISHED = "unpublished"


@dataclass(frozen=True)
class Product:
    """One registry product. Frozen so a tool handler can never accidentally mutate the catalog."""

    sku: str
    name: str  # catalog.name
    collection: str  # collections[catalog.collection].name
    price_usd: float  # catalog.price
    sizes: tuple[str, ...]  # garment.available_sizes
    availability: str  # PRE_ORDER | AVAILABLE | UNPUBLISHED, from catalog.is_preorder / published
    description: str  # catalog.description


def _availability(catalog: dict) -> str:
    if catalog.get("is_preorder") == "1":
        return PRE_ORDER
    if catalog.get("published") == "1":
        return AVAILABLE
    return UNPUBLISHED


def _collection_meta(slug: str, record: dict) -> CollectionMeta:
    """Map one registry collection; an absent fact is an error, never a blank."""
    try:
        return CollectionMeta(
            accent=record["palette"]["accent"],
            story=record["story"]["seed"],
            story_ref=record["story"]["doc_ref"],
        )
    except (KeyError, TypeError) as exc:
        raise CatalogUnavailableError(
            f"Registry collection {slug!r} is missing a fact: {exc!r}"
        ) from exc


def _product(sku: str, record: dict, collections: dict) -> Product:
    """Map one registry record to a Product; any absent fact is an error, never a blank."""
    try:
        catalog = record["catalog"]
        garment = record["garment"]
        collection = collections[catalog["collection"]]["name"]
        product = Product(
            sku=sku,
            name=catalog["name"],
            collection=collection,
            price_usd=float(catalog["price"]),
            sizes=tuple(garment["available_sizes"]),
            availability=_availability(catalog),
            description=catalog["description"].strip(),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise CatalogUnavailableError(
            f"Registry product {sku!r} is missing a fact: {exc!r}"
        ) from exc
    return product


def _read_registry(path: Path) -> tuple[dict, dict]:
    """The registry's products and collections. Fails closed on anything missing."""
    if not path.is_file():
        raise CatalogUnavailableError(
            f"Product registry not found at {path}. This agent reads the SkyyRose product "
            "source of truth directly and has no demo catalog to fall back on."
        )
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise CatalogUnavailableError(f"Product registry at {path} is unreadable: {exc}") from exc
    products = raw.get("products")
    collections = raw.get("collections")
    if not isinstance(products, dict) or not products or not isinstance(collections, dict):
        raise CatalogUnavailableError(f"Product registry at {path} has no products/collections")
    return products, collections


def load_products(path: Path = REGISTRY_PATH) -> tuple[Product, ...]:
    """Read every product from the registry, sorted by SKU. Fails closed."""
    products, collections = _read_registry(path)
    return tuple(_product(sku, record, collections) for sku, record in sorted(products.items()))


def load_collections(path: Path = REGISTRY_PATH) -> dict[str, CollectionMeta]:
    """Each collection's canon keyed by its display name. Fails closed."""
    _, collections = _read_registry(path)
    if not collections:
        raise CatalogUnavailableError(f"Product registry at {path} has no collections")
    return {
        record.get("name") or slug: _collection_meta(slug, record)
        for slug, record in sorted(collections.items())
    }


COLLECTIONS: dict[str, CollectionMeta] = load_collections()
PRODUCTS: tuple[Product, ...] = load_products()


# Index by SKU once, at import time, for O(1) exact lookups.
_BY_SKU: dict[str, Product] = {p.sku: p for p in PRODUCTS}


def find_products(query: str) -> list[Product]:
    """Return products whose SKU or name matches `query` (case-insensitive substring).

    An exact SKU match short-circuits to a single result; otherwise we substring-match
    against both SKU and name so "rose" finds every Black Rose piece by name.
    """
    q = query.strip().lower()
    if not q:
        return []

    exact = _BY_SKU.get(q)
    if exact is not None:
        return [exact]

    return [p for p in PRODUCTS if q in p.sku.lower() or q in p.name.lower()]


def products_in_collection(collection: str) -> list[Product]:
    """Return every product in `collection`, matched case-insensitively against the
    registry's collection display names (the COLLECTIONS keys)."""
    target = collection.strip().lower()
    return [p for p in PRODUCTS if p.collection.lower() == target]
