"""THE single entry point for product facts. One call, one complete record.

Every agent, pipeline, render job, ad build, and content task that needs to know
anything about a SkyyRose product calls :func:`get_product` here — nothing else.
Not the CSV, not a dossier file, not ``product-content.json``, not a hardcoded
``assets/images/products/...`` path.

    >>> from skyyrose.core.product import get_product
    >>> p = get_product("br-001")
    >>> p["name"], p["images"]["front"]["path"], p["gaps"]

Non-Python callers get the identical record over the CLI::

    python -m skyyrose.core.product br-001          # one SKU as JSON
    python -m skyyrose.core.product --all           # every SKU
    python -m skyyrose.core.product --gaps          # only the gap report

This module assembles the record from the authored product registry
(``logo-registry.json``) plus the authored side-stores that have not been folded
into it yet. The section names match the registry's own, so when those stores
merge in, the assembly collapses to a single registry read and **no caller
changes**. The API is the contract; the file layout is an implementation detail.

Fail-closed, always (bug-230). A fact is either present or named in ``gaps`` —
never silently blank:

* unknown SKU                  -> ``KeyError``
* SKU with no dossier          -> ``DossierMissingError``
* image role with no asset     -> ``None`` + a ``gaps`` entry
* a role served by a lesser asset (flat packshot for an on-model front)
  -> ``role_asset: False`` + ``images.<role>.fallback`` in ``gaps``
* copy served by the base layer rather than the editorial one
  -> ``enriched: False`` + ``content.<field>.enriched`` in ``gaps``
* copy with no source at all   -> ``None`` + a ``gaps`` entry

Every SKU has a description; all 33 carry one in the registry, and that is the
copy the live storefront serves. What varies is the layer: 19 SKUs also have
enriched editorial copy, SEO meta, and social captions. A caller is always told
which layer it received, so an editorial task can tell finished copy from the
one-line base description.

An agent handed ``description: ""`` invents copy. An agent handed the base line
tagged ``enriched: False`` knows exactly what it is holding. That difference is
the point of this module.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

from skyyrose.core.dossier_loader import get_product_with_dossier
from skyyrose.core.paths import REPO_ROOT
from skyyrose.core.product_registry import PRODUCT_REGISTRY, load_registry
from skyyrose.core.sot_images import _ROLE_KEYS, Role

__all__ = [
    "IMAGE_ROLES",
    "all_skus",
    "gap_report",
    "get_all_products",
    "get_product",
    "provenance",
]

IMAGE_ROLES: tuple[Role, ...] = ("front", "back", "packshot", "back_packshot")

# Authored side-stores not yet folded into the registry. Each is tracked; an
# absent file is a broken checkout, not "this SKU has no copy" -- so reads raise
# rather than report 33 phantom gaps.
_CONTENT_JSON = REPO_ROOT / "skyyrose" / "assets" / "data" / "product-content.json"
_ALT_TEXT_JSON = REPO_ROOT / "skyyrose" / "assets" / "data" / "alt-text.json"
_CORRECTIONS_JSON = (
    REPO_ROOT / "wordpress-theme" / "skyyrose-flagship" / "data" / "render-corrections.json"
)

_CONTENT_FIELDS = ("description", "short_description", "seo_meta", "instagram", "tiktok")

# Fields the registry's own catalog.description can legitimately stand in for.
# Social captions and SEO meta are their own craft -- a product description is
# not a TikTok caption, so those stay absent rather than borrow.
_BASE_BACKED_FIELDS = frozenset({"description", "short_description"})

_CONTENT_SOURCE = "product-content.json"
_REGISTRY_SOURCE = "registry.catalog.description"


class ProductSourceMissingError(FileNotFoundError):
    """An authored product source file is absent from the checkout."""


@lru_cache(maxsize=16)
def _stamp(path: str, mtime_ns: int, size: int) -> dict[str, Any]:
    """Content digest for one authored source. Cached on (path, mtime, size)."""
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    return {
        "sha256": digest[:16],
        "modified": datetime.fromtimestamp(mtime_ns / 1e9, tz=UTC).isoformat(),
        "bytes": size,
    }


def provenance() -> dict[str, Any]:
    """Which files this record was assembled from, and their current state.

    Every record carries this, so a caller can prove the facts it is holding
    match what is on disk right now rather than a stale cache. ``generated`` is
    when the record was assembled; each source's ``sha256`` and ``modified``
    change the moment the founder edits it.
    """
    sources: dict[str, Any] = {}
    for label, path in (
        ("registry", PRODUCT_REGISTRY),
        ("content", _CONTENT_JSON),
        ("alt_text", _ALT_TEXT_JSON),
        ("corrections", _CORRECTIONS_JSON),
    ):
        if not path.exists():
            raise ProductSourceMissingError(f"authored product source missing: {path}")
        info = path.stat()
        sources[label] = {
            "path": str(path.relative_to(REPO_ROOT)),
            **_stamp(str(path), info.st_mtime_ns, info.st_size),
        }
    return {
        "generated": datetime.now(tz=UTC).isoformat(),
        "entry_point": "skyyrose.core.product.get_product",
        "sources": sources,
    }


def _load_json(path: Path) -> dict[str, Any]:
    """Read an authored source, or fail loudly. Never degrade to an empty dict."""
    if not path.exists():
        raise ProductSourceMissingError(
            f"authored product source missing: {path}. "
            "Restore it before reading product facts -- an empty read would "
            "report every SKU as having no content."
        )
    return json.loads(path.read_text())


def all_skus() -> list[str]:
    """Every SKU in the product registry, sorted."""
    return sorted(load_registry()["products"])


def _images_for(product: dict[str, Any], sku: str) -> tuple[dict[str, Any], list[str]]:
    """Resolved image per role, plus gaps for roles with no asset of their own.

    ``source_key`` names the registry field that actually supplied the path, and
    ``role_asset`` is False when the role fell back to a lesser asset (a flat
    packshot standing in for an on-model front). A render agent asking for a back
    view must receive "absent", never a silently substituted front -- that
    substitution is the mechanism behind the wrong-garment defect class.
    """
    images = product.get("images", {})
    resolved: dict[str, Any] = {}
    gaps: list[str] = []
    for role in IMAGE_ROLES:
        keys = _ROLE_KEYS[role]
        hit = next(
            (
                (key, entry["path"])
                for key in keys
                if isinstance(entry := images.get(key), dict) and entry.get("path")
            ),
            None,
        )
        if hit is None:
            resolved[role] = None
            gaps.append(f"images.{role}")
            continue
        key, path = hit
        resolved[role] = {
            "path": path,
            "source_key": key,
            "role_asset": key == keys[0],
        }
        if key != keys[0]:
            gaps.append(f"images.{role}.fallback")
    return resolved, gaps


def _logos_for(sku: str) -> dict[str, Any]:
    """Graphics, placements, and decoration dimensions from the registry."""
    from skyyrose.elite_studio.logo_registry import LogoRegistry

    registry = LogoRegistry.load()
    if not registry.has_sku(sku):
        return {"placements": [], "decoration_sizing": {}, "primary_reference": None}
    reference = registry.primary_reference_for(sku)
    return {
        "placements": registry.placements_for(sku),
        "decoration_sizing": registry.decoration_sizing_for(sku),
        "primary_reference": _relative(reference),
        "reference_kind": registry.reference_kind_for(sku),
        "patch_sport": registry.patch_sport_for(sku),
        "sku_folder": registry.sku_folder(sku),
    }


def _relative(path: Path | None) -> str | None:
    """Repo-relative string for JSON, or None. Absolute paths never leave here."""
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _content_for(
    sku: str, catalog: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, str], list[str]]:
    """Marketing copy resolved through its layers, with the source named.

    Copy exists in two layers and a caller needs to know which one it got:

    1. ``product-content.json`` -- the enriched editorial layer: long-form
       description, a distinct short description, SEO meta, and social captions.
    2. the registry's own ``catalog.description`` -- the base line every SKU
       has, and the copy the live storefront currently serves.

    Same rule as imagery: the lesser layer may stand in, but never silently. A
    field filled from the base layer is tagged ``enriched: False`` and named in
    gaps as ``content.<field>.enriched``, so an editorial or SEO task can tell
    "this is the one-line base description" from "this is finished copy".
    """
    entry = _load_json(_CONTENT_JSON).get(sku) or {}
    alt = _load_json(_ALT_TEXT_JSON).get(sku) or {}
    base = (catalog.get("description") or "").strip() or None

    content: dict[str, Any] = {}
    gaps: list[str] = []
    for field in _CONTENT_FIELDS:
        value = (entry.get(field) or "").strip() or None
        if value:
            content[field] = {"value": value, "source": _CONTENT_SOURCE, "enriched": True}
            continue
        if base and field in _BASE_BACKED_FIELDS:
            content[field] = {"value": base, "source": _REGISTRY_SOURCE, "enriched": False}
            gaps.append(f"content.{field}.enriched")
            continue
        content[field] = None
        gaps.append(f"content.{field}")

    if not alt:
        gaps.append("content.alt_text")
    return content, alt, gaps


def _corrections_for(sku: str) -> list[dict[str, str]]:
    """Founder-verbatim render corrections. Wording is preserved exactly."""
    raw = _load_json(_CORRECTIONS_JSON).get("corrections", {}).get(sku) or []
    return [{"text": line, "authority": "FOUNDER_VERBATIM"} for line in raw]


def get_product(sku: str) -> dict[str, Any]:
    """Everything known about ``sku``, in one verified record.

    Sections: ``catalog`` (commerce), ``garment`` (color, sizes, fit, materials,
    features, sizing references), ``dossier`` (the founder's design
    specification), ``images`` (every role, resolved), ``render_sources``,
    ``logos`` (graphics, placements, decoration dimensions), ``content``
    (marketing copy and SEO), ``alt_text``, ``corrections`` (founder-verbatim),
    ``authority``, and ``gaps``.

    Raises:
        KeyError: ``sku`` is not in the product registry.
        DossierMissingError: the SKU has no design specification bound.
        ProductSourceMissingError: an authored source file is absent.
    """
    products = load_registry()["products"]
    if sku not in products:
        raise KeyError(
            f"SKU {sku!r} is not in the product registry. Known SKUs: {', '.join(sorted(products))}"
        )
    product = products[sku]
    merged = get_product_with_dossier(sku)
    catalog = product.get("catalog", {})
    images, image_gaps = _images_for(product, sku)
    content, alt_text, content_gaps = _content_for(sku, catalog)

    return {
        "sku": sku,
        "name": catalog.get("name"),
        "collection": catalog.get("collection"),
        "catalog": catalog,
        "garment": product.get("garment", {}),
        "dossier": merged["dossier"],
        "images": images,
        "render_sources": product.get("render_sources", {}),
        "logos": _logos_for(sku),
        "content": content,
        "alt_text": alt_text,
        "corrections": _corrections_for(sku),
        "authority": product.get("authority"),
        "gaps": image_gaps + content_gaps,
        "provenance": provenance(),
    }


def get_all_products() -> dict[str, dict[str, Any]]:
    """Every product record, keyed by SKU."""
    return {sku: get_product(sku) for sku in all_skus()}


def gap_report() -> dict[str, list[str]]:
    """SKU -> its declared gaps, for SKUs that have any. Empty dict means clean."""
    return {sku: rec["gaps"] for sku, rec in get_all_products().items() if rec["gaps"]}


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m skyyrose.core.product",
        description="The single source for SkyyRose product facts.",
    )
    parser.add_argument("sku", nargs="?", help="SKU to describe, e.g. br-001")
    parser.add_argument("--all", action="store_true", help="every product record")
    parser.add_argument("--gaps", action="store_true", help="only the gap report")
    parser.add_argument("--skus", action="store_true", help="list every known SKU")
    args = parser.parse_args(argv)

    if args.skus:
        payload: Any = all_skus()
    elif args.gaps:
        payload = gap_report()
    elif args.all:
        payload = get_all_products()
    elif args.sku:
        payload = get_product(args.sku)
    else:
        parser.print_help()
        return 2
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
