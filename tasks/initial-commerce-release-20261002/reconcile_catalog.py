"""Offline evidence projection from the canonical reader and authenticated Woo snapshots."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from skyyrose.core.product import all_skus, get_product, provenance  # noqa: E402


def reconcile(snapshot: dict) -> dict:
    if snapshot.get("home") not in {
        "https://staging-7e48-skyyrose.wpcomstaging.com",
        "https://skyyrose.co",
    }:
        raise ValueError("UNVERIFIED_TARGET")
    records = snapshot["records"]
    if len({row["id"] for row in records}) != len(records):
        raise ValueError("DUPLICATE_RECORD_ID")
    parents = [r for r in records if r["parent_id"] == 0 and r["status"] == "publish"]
    by_sku = {}
    for row in parents:
        sku = row["sku"].strip().lower()
        if not sku or sku in by_sku:
            raise ValueError("AMBIGUOUS_PUBLISHED_SKU")
        by_sku[sku] = row
    canonical = set(all_skus())
    products = []
    for sku in sorted(canonical & by_sku.keys()):
        product = get_product(sku)
        row = by_sku[sku]
        card = product["images"]["card_front"]
        path = ROOT / "wordpress-theme/skyyrose-flagship-2" / card["path"]
        image_hash_matches = hashlib.sha256(path.read_bytes()).hexdigest() == card["sha256"]
        attributes = row["attributes"]
        size_attributes = [
            v for k, v in attributes.items() if "size" in k.lower() and isinstance(v, dict)
        ]
        woo_sizes = [s for a in size_attributes for s in a["options"]]
        canonical_sizes = product["garment"]["available_sizes"]
        children = [r for r in records if r["parent_id"] == row["id"] and r["status"] == "publish"]
        products.append(
            {
                "sku": sku,
                "woo_id": row["id"],
                "type": row["type"],
                "price_matches": Decimal(row["price"]) == Decimal(product["catalog"]["price"]),
                "native_price": row["price"],
                "preorder_matches": row["preorder"]["_is_preorder"]
                == product["catalog"]["is_preorder"],
                "preorder": row["preorder"],
                "stock": {
                    k: row[k]
                    for k in ["manage_stock", "stock_quantity", "stock_status", "backorders"]
                },
                "purchasable": row["purchasable"],
                "declared_sizes_match": sorted(woo_sizes) == sorted(canonical_sizes),
                "native_variation_ids": [r["id"] for r in children],
                "size_selection_and_order_persistence": "NOT_RUN_CURRENT_RUNTIME",
                "native_attachment_ids": [r["id"] for r in row["images"]],
                "card_front": {**card, "local_hash_matches": image_hash_matches},
                "fidelity": (
                    "EXCLUDED_CARD_FRONT_REQUIRES_FAITHFUL_FALLBACK_VERIFICATION"
                    if card.get("current_fidelity_status") == "BLOCKED_PRODUCT_MISMATCH"
                    else "RECORDED_SOURCE_BINDING_ONLY_FULL_PIXEL_REVIEW_NOT_RERUN"
                ),
            }
        )
    return {
        "schema": 1,
        "target": snapshot["home"],
        "snapshot_recorded_at_utc": snapshot["recorded_at_utc"],
        "canonical_provenance": provenance(),
        "counts": {
            "records": len(records),
            "published_parents": len(parents),
            "canonical_skus": len(canonical),
        },
        "missing_canonical_skus": sorted(canonical - by_sku.keys()),
        "unexpected_published_skus": sorted(by_sku.keys() - canonical),
        "products": products,
        "gateways": snapshot["gateways"],
        "limits": [
            "Native prices authoritative; comparison writes nothing",
            "Declared size attributes do not prove purchasable variations or selected-size persistence",
            "Edition size is not remaining stock or reservation",
            "Image identity hashes do not establish garment fidelity",
            "Gateway enabled/test flags do not establish successful payment, settlement, refunds or webhook processing",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = reconcile(json.loads(args.snapshot.read_text()))
    result["snapshot_sha256"] = hashlib.sha256(args.snapshot.read_bytes()).hexdigest()
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {
                "target": result["target"],
                **result["counts"],
                "prices_match": sum(p["price_matches"] for p in result["products"]),
                "preorders_match": sum(p["preorder_matches"] for p in result["products"]),
                "sizes_declared_match": sum(p["declared_sizes_match"] for p in result["products"]),
            }
        )
    )


if __name__ == "__main__":
    main()
