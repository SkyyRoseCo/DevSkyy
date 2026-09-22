#!/usr/bin/env python3
"""Generate the V2 presentation registry from the canonical product SOT.

This is a build-time adapter. WooCommerce remains responsible for product IDs,
prices, stock, variations, and visibility; SOT media remains responsible for
approved product visuals. Merchandising-series membership, region, and order
come only from the canonical product SOT.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

sys.path.insert(0, str(ROOT / "tools/v2-source-certification"))
from inputs import garment_types, load_product_sot  # noqa: E402

from skyyrose.core.product import get_product, provenance  # noqa: E402

OUTPUT = Path(__file__).resolve().parents[1] / "data/product-presentation-registry.json"
ALLOWED_COLLECTIONS = {"black-rose", "kids-capsule", "love-hurts", "signature"}
ALLOWED_SERIES = {"jersey-series"}


def build_registry() -> dict[str, object]:
    manifest, expected = load_product_sot()
    garments = garment_types(manifest)
    products: dict[str, dict[str, object]] = {}
    series_members: dict[str, list[tuple[int, str]]] = {
        series_slug: [] for series_slug in ALLOWED_SERIES
    }
    series_orders: dict[str, set[int]] = {series_slug: set() for series_slug in ALLOWED_SERIES}
    for sku, product in manifest["products"].items():
        current_record = get_product(sku)
        current = current_record["catalog"]
        collection = current["collection"]
        if not sku or sku in products:
            raise ValueError(f"Product SOT contains an empty or duplicate SKU: {sku!r}")
        if collection not in ALLOWED_COLLECTIONS:
            raise ValueError(f"Unknown collection for {sku}: {collection!r}")
        merchandising = current_record["merchandising"]
        if not isinstance(merchandising, dict):
            raise ValueError(f"Canonical registry merchandising record is invalid for {sku}")
        series_slug = str(merchandising.get("series_slug", ""))
        series_region = str(merchandising.get("series_region", ""))
        series_order = merchandising.get("series_order", 0)
        if not isinstance(series_order, int) or isinstance(series_order, bool):
            raise ValueError(f"Series order is invalid for {sku}: {series_order!r}")
        if series_slug and series_slug not in ALLOWED_SERIES:
            raise ValueError(f"Unknown merchandising series for {sku}: {series_slug!r}")
        if series_slug:
            if not series_region or series_order <= 0:
                raise ValueError(f"Series metadata is incomplete for {sku}")
            if series_order in series_orders[series_slug]:
                raise ValueError(f"Duplicate {series_slug} series order: {series_order}")
            series_orders[series_slug].add(series_order)
            series_members[series_slug].append((series_order, sku))
        elif series_region or series_order:
            raise ValueError(f"Non-series product has series metadata: {sku}")

        presentation = series_slug or collection
        record: dict[str, object] = {
            "collection": collection,
            "garment_type": garments[sku],
            "presentation": presentation,
            "route": f"/{series_slug}/" if series_slug else f"/collections/{collection}/",
            "is_preorder": current["is_preorder"].strip() == "1",
            "product_sot_hash": product["product_hash"],
            "media_proof_level": product["verification"]["proof_level"],
        }
        if series_slug:
            record["series_region"] = series_region
            record["series_order"] = series_order
        products[sku] = record

    supplements = {
        f"{series_slug.replace('-', '_')}_skus": [sku for _order, sku in sorted(members)]
        for series_slug, members in sorted(series_members.items())
    }
    return {
        "schema_version": "2.0.0",
        "kind": "skyyrose-v2-product-presentation-registry",
        "generated_from": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "product_registry_sha256": provenance()["sources"]["registry"]["sha256"],
        "product_sot_scope": "historical_media_binding_only",
        "product_sot_sha256": hashlib.sha256(expected.encode()).hexdigest(),
        "supplements": supplements,
        "products": dict(sorted(products.items())),
    }


def main() -> int:
    artifact = build_registry()
    rendered = json.dumps(artifact, indent=2, sort_keys=True) + "\n"
    if "--check" in sys.argv:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != rendered:
            print(
                "Product presentation registry is stale. Run this script without --check.",
                file=sys.stderr,
            )
            return 1
        print(f"Product presentation registry is current ({len(artifact['products'])} SKUs).")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"Wrote {OUTPUT} ({len(artifact['products'])} SKUs).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
