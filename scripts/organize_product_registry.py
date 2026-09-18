#!/usr/bin/env python3
"""Keep the product registry organized: schema-valid, ordered, and diffable.

A source of truth that 116 files read has to stay predictable. This script
enforces three properties:

1. **Schema-valid** -- every record matches ``logo-registry.schema.json``:
   required fields present, SKU pattern correct, collection slug from the
   enum, booleans as ``"0"``/``"1"`` strings, no stray keys. ``additionalProperties:
   false`` means a typo'd key is an error, not a silent new field.

2. **Canonically ordered** -- top-level sections, per-product sections, and
   ``catalog`` keys all appear in a fixed order, and SKUs sort by collection then
   number. A founder edit then shows up as one changed line instead of a
   reshuffled file, which is what makes review and ``git blame`` usable on a
   436 KB JSON.

3. **Internally consistent** -- ``catalog.sku`` matches its key, ``catalog_columns``
   matches the catalog field set, and every image path the registry declares
   exists on disk.

Usage::

    python scripts/organize_product_registry.py --check   # report, exit 1 on any finding
    python scripts/organize_product_registry.py --apply   # rewrite in canonical order

``--check`` is what the drift-guard hook and CI run. ``--apply`` rewrites the
registry, so it is a deliberate, reviewed action -- run it, then read the diff.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, NamedTuple

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY = REPO_ROOT / "wordpress-theme/skyyrose-flagship/data/logo-registry.json"
SCHEMA = REPO_ROOT / "wordpress-theme/skyyrose-flagship/data/logo-registry.schema.json"
THEME_ROOT = REGISTRY.parent.parent

# Top-level order: what the file IS, then who governs it, then the brand, then
# the products, then the graphics, then the generated-projection contracts, then
# history. Reading top to bottom should explain the file.
TOP_LEVEL_ORDER = (
    "$schema",
    "version",
    "updated",
    "product_registry_schema_version",
    "authority_contract",
    "brand_primary",
    "brand",
    "collections",
    "products",
    "logos",
    "sku_logos",
    "sku_folders",
    "render_components",
    "render_source_aliases",
    "three_rose_cluster_colorways",
    "jersey_patch_standard",
    "catalog_columns",
    "gaps",
    "changelog",
)

# Per-product order: commerce, then the physical garment, then the founder's
# specification, then what represents it, then what it is made from, then copy,
# then corrections, then who vouches for all of it.
PRODUCT_ORDER = (
    "catalog",
    "garment",
    "dossier",
    "images",
    "render_sources",
    "content",
    "corrections",
    "render_policy",
    "authority",
    "asset_reconciliation",
    "render_source_migration",
)

GARMENT_ORDER = ("color", "available_sizes", "fit", "materials", "features", "sizing_references")
IMAGES_ORDER = ("image", "front_model_image", "back_image", "back_model_image")
RENDER_SOURCES_ORDER = ("front", "back", "reference")

# SKU sort: collection groups in brand order, then numerically inside each.
COLLECTION_ORDER = ("sg", "br", "lh", "kids")


class Finding(NamedTuple):
    """One thing wrong with the registry: what kind, where, and what to fix."""

    kind: str
    where: str
    message: str


def _ordered(data: dict[str, Any], order: tuple[str, ...]) -> dict[str, Any]:
    """Re-key ``data`` into ``order``, keeping any unlisted keys after, sorted."""
    known = [k for k in order if k in data]
    extra = sorted(k for k in data if k not in order)
    return {k: data[k] for k in [*known, *extra]}


def sku_sort_key(sku: str) -> tuple[int, int, str]:
    prefix, _, number = sku.partition("-")
    group = COLLECTION_ORDER.index(prefix) if prefix in COLLECTION_ORDER else len(COLLECTION_ORDER)
    return (group, int(number) if number.isdigit() else 0, sku)


def organize(registry: dict[str, Any]) -> dict[str, Any]:
    """Return the registry in canonical order. Values are untouched."""
    products = registry.get("products", {})
    ordered_products = {}
    for sku in sorted(products, key=sku_sort_key):
        product = _ordered(products[sku], PRODUCT_ORDER)
        catalog_order = tuple(registry.get("catalog_columns", ()))
        if isinstance(product.get("catalog"), dict) and catalog_order:
            product["catalog"] = _ordered(product["catalog"], catalog_order)
        for section, order in (
            ("garment", GARMENT_ORDER),
            ("images", IMAGES_ORDER),
            ("render_sources", RENDER_SOURCES_ORDER),
        ):
            if isinstance(product.get(section), dict):
                product[section] = _ordered(product[section], order)
        ordered_products[sku] = product

    out = _ordered(registry, TOP_LEVEL_ORDER)
    out["products"] = ordered_products
    return out


def check_schema(registry: dict[str, Any]) -> list[Finding]:
    from jsonschema import Draft202012Validator

    schema = json.loads(SCHEMA.read_text())
    validator = Draft202012Validator(schema)
    return [
        Finding("schema", ".".join(str(p) for p in error.path) or "<root>", error.message)
        for error in sorted(validator.iter_errors(registry), key=lambda e: list(e.path))
    ]


def check_consistency(registry: dict[str, Any]) -> list[Finding]:
    """Cross-field invariants a schema cannot express."""
    findings: list[Finding] = []
    products = registry.get("products", {})

    columns = set(registry.get("catalog_columns", ()))
    for sku, product in products.items():
        catalog = product.get("catalog", {})
        if catalog.get("sku") != sku:
            findings.append(
                Finding("consistency", f"products.{sku}", f"catalog.sku is {catalog.get('sku')!r}")
            )

        missing = columns - set(catalog) - {"fit", "materials", "features", "sizing_references"}
        if missing:
            findings.append(
                Finding(
                    "consistency",
                    f"products.{sku}.catalog",
                    f"catalog_columns declares fields this record lacks: {sorted(missing)}",
                )
            )

        for role, binding in (product.get("images") or {}).items():
            path = (binding or {}).get("path")
            if path and not (THEME_ROOT / path).exists():
                findings.append(
                    Finding(
                        "missing-asset",
                        f"products.{sku}.images.{role}",
                        f"declared image does not exist on disk: {path}",
                    )
                )
    return findings


def check_order(registry: dict[str, Any]) -> list[Finding]:
    """Report every place the on-disk order differs from canonical."""
    findings: list[Finding] = []
    canonical = organize(registry)

    if list(registry) != list(canonical):
        findings.append(Finding("order", "<root>", "top-level sections are not in canonical order"))

    if list(registry.get("products", {})) != list(canonical["products"]):
        findings.append(
            Finding("order", "products", "SKUs are not sorted by collection then number")
        )

    for sku, product in registry.get("products", {}).items():
        if list(product) != list(canonical["products"][sku]):
            findings.append(
                Finding("order", f"products.{sku}", "sections are not in canonical order")
            )
        for section in ("catalog", "garment", "images", "render_sources"):
            on_disk = product.get(section)
            if isinstance(on_disk, dict) and list(on_disk) != list(
                canonical["products"][sku][section]
            ):
                findings.append(
                    Finding("order", f"products.{sku}.{section}", "keys are not in canonical order")
                )
    return findings


def _serialize(registry: dict[str, Any]) -> str:
    return json.dumps(registry, indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="report findings, exit 1 on any")
    mode.add_argument("--apply", action="store_true", help="rewrite in canonical order")
    parser.add_argument("--quiet", action="store_true", help="only print the summary line")
    args = parser.parse_args(argv)

    registry = json.loads(REGISTRY.read_text())
    findings = check_schema(registry) + check_consistency(registry) + check_order(registry)

    if args.apply:
        blocking = [f for f in findings if f.kind != "order"]
        if blocking:
            print(f"refusing to reorder: {len(blocking)} non-order finding(s) must be fixed first")
            for finding in blocking[:20]:
                print(f"  [{finding.kind}] {finding.where}: {finding.message}")
            return 1
        REGISTRY.write_text(_serialize(organize(registry)))
        print(f"registry rewritten in canonical order: {REGISTRY.relative_to(REPO_ROOT)}")
        return 0

    if not findings:
        print(
            f"registry organized: {len(registry.get('products', {}))} SKUs, schema-valid, in order"
        )
        return 0

    if not args.quiet:
        for finding in findings[:40]:
            print(f"  [{finding.kind}] {finding.where}: {finding.message}")
        if len(findings) > 40:
            print(f"  ... {len(findings) - 40} more")
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.kind] = counts.get(finding.kind, 0) + 1
    print(f"registry findings: {', '.join(f'{v} {k}' for k, v in sorted(counts.items()))}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
