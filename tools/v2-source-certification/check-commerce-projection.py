#!/usr/bin/env python3
"""Reproduce historical WooCommerce projection receipts; no network writes.

This compiler intentionally reads the immutable historical snapshot, not current
product facts. It is not a live synchronization source. Use the unified
skyyrose.core.product.get_product entry point for current product reads.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from inputs import load_product_sot  # noqa: E402

OUTPUT_PATH = Path(__file__).with_name("inputs") / "woocommerce-product-sync.json"

SCHEMA = "skyyrose.woocommerce-product-sync.v1"
COLLECTION_NAMES = {
    "signature": "Signature",
    "black-rose": "Black Rose",
    "love-hurts": "Love Hurts",
    "kids-capsule": "Kids Capsule",
    "pre-order": "Pre-Order",
}
IMAGE_ROLES = (
    ("featured", "on_model_front"),
    ("packshot_front", "packshot_front"),
    ("on_model_back", "on_model_back"),
    ("packshot_back", "packshot_back"),
)


def _slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "product"


def _meta(key: str, value: Any) -> dict[str, Any]:
    return {"key": key, "value": value}


def _image_roles(record: dict[str, Any]) -> list[dict[str, str]]:
    images: list[dict[str, str]] = []
    seen: set[str] = set()
    for role, media_role in IMAGE_ROLES:
        artifact = record["media"].get(media_role)
        if not artifact:
            continue
        source_path = artifact["path"]
        if source_path in seen:
            continue
        seen.add(source_path)
        images.append(
            {
                "role": role,
                "source_path": source_path,
                "sha256": artifact["sha256"],
                "product_hash": record["product_hash"],
            }
        )
    return images


def _catalog_meta(record: dict[str, Any]) -> list[dict[str, Any]]:
    identity = record["identity"]
    commerce = record["commerce"]
    garment = record["garment"]
    rendering = record["rendering"]
    merchandising = record["merchandising"]
    media = record["media"]
    source = record["source"]
    values = (
        ("_skyyrose_collection", identity["collection"]),
        ("_skyyrose_series_slug", merchandising["series_slug"]),
        ("_skyyrose_series_region", merchandising["series_region"]),
        ("_skyyrose_series_order", merchandising["series_order"]),
        ("_skyyrose_badge", identity["badge"]),
        ("_skyyrose_edition_size", commerce["edition_size"]),
        ("_skyyrose_front_model_image", media.get("on_model_front", {}).get("path", "")),
        ("_skyyrose_back_image", media.get("packshot_back", {}).get("path", "")),
        ("_skyyrose_back_model_image", media.get("on_model_back", {}).get("path", "")),
        ("_skyyrose_dossier_slug", Path(source["dossier"]).stem),
        ("_skyyrose_engine_override", rendering["engine_override"]),
        ("_skyyrose_branding_spec", garment["branding_summary"]),
        ("_skyyrose_render_output_slug", rendering["output_slug"]),
        ("_skyyrose_render_source_override", rendering["source_override"]),
        ("_skyyrose_render_back_source_override", rendering["back_source_override"]),
        ("_skyyrose_render_is_tech_flat", "1" if rendering["is_tech_flat"] else "0"),
        ("_skyyrose_render_is_accessory", "1" if rendering["is_accessory"] else "0"),
        ("_skyyrose_garment_type_lock", garment["type_lock"]),
        ("_skyyrose_product_sot_hash", record["product_hash"]),
        ("_skyyrose_product_sot_dossier_hash", source["dossier_sha256"]),
    )
    meta = [_meta(key, value) for key, value in values]
    is_preorder = commerce["is_preorder"]
    edition_size = commerce["edition_size"]
    meta.append(_meta("_is_preorder", "1" if is_preorder else "0"))
    meta.append(_meta("_preorder_edition_size", edition_size if is_preorder else ""))
    return meta


def _variation_payload(*, sku: str, size: str, price: str, menu_order: int) -> dict[str, Any]:
    return {
        "description": "",
        "sku": f"{sku}-{_slug(size).upper()}",
        "regular_price": price,
        "sale_price": "",
        "date_on_sale_from": None,
        "date_on_sale_to": None,
        "status": "publish",
        "virtual": False,
        "downloadable": False,
        "downloads": [],
        "download_limit": -1,
        "download_expiry": -1,
        "tax_status": "taxable",
        "tax_class": "",
        "manage_stock": False,
        "stock_quantity": None,
        "stock_status": "instock",
        "backorders": "no",
        "weight": "",
        "dimensions": {"length": "", "width": "", "height": ""},
        "shipping_class": "",
        "image": None,
        "attributes": [{"name": "Size", "option": size}],
        "menu_order": menu_order,
        "meta_data": [],
    }


def build_product_record(record: dict[str, Any]) -> dict[str, Any]:
    sku = record["sku"]
    identity = record["identity"]
    commerce = record["commerce"]
    name = identity["name"]
    description = identity["description"]
    price = commerce["price"]
    sizes = commerce["sizes"]
    colors = commerce["colors"]
    variable = len(sizes) > 1 and sizes != ["One Size"]
    published = commerce["published"]
    is_preorder = commerce["is_preorder"]

    category_slugs = [identity["collection"]]
    if is_preorder:
        category_slugs.append("pre-order")

    attributes: list[dict[str, Any]] = []
    if sizes:
        attributes.append(
            {
                "name": "Size",
                "position": 0,
                "visible": True,
                "variation": variable,
                "options": sizes,
            }
        )
    if colors:
        attributes.append(
            {
                "name": "Color",
                "position": 1,
                "visible": True,
                "variation": False,
                "options": colors,
            }
        )

    product = {
        "name": name,
        "slug": sku.lower(),
        "type": "variable" if variable else "simple",
        "status": "publish" if published else "draft",
        "featured": False,
        "catalog_visibility": "visible" if published else "hidden",
        "description": description,
        "short_description": description[:200],
        "sku": sku,
        "regular_price": "" if variable else price,
        "sale_price": "",
        "date_on_sale_from": None,
        "date_on_sale_to": None,
        "virtual": False,
        "downloadable": False,
        "downloads": [],
        "download_limit": -1,
        "download_expiry": -1,
        "external_url": "",
        "button_text": "",
        "tax_status": "taxable",
        "tax_class": "",
        "manage_stock": False,
        "stock_quantity": None,
        "stock_status": "instock",
        "backorders": "no",
        "sold_individually": False,
        "weight": "",
        "dimensions": {"length": "", "width": "", "height": ""},
        "shipping_class": "",
        "reviews_allowed": True,
        "upsell_ids": [],
        "cross_sell_ids": [],
        "purchase_note": "",
        "categories": [],
        "tags": [],
        "images": [],
        "attributes": attributes,
        "default_attributes": [],
        "menu_order": 0,
        "meta_data": _catalog_meta(record),
    }

    create_only_meta = []
    if is_preorder:
        create_only_meta.append(_meta("_preorder_available", commerce["edition_size"]))

    variations = (
        [
            _variation_payload(sku=sku, size=size, price=price, menu_order=index)
            for index, size in enumerate(sizes)
        ]
        if variable
        else []
    )

    return {
        "sku": sku,
        "product_sot_hash": record["product_hash"],
        "category_slugs": category_slugs,
        "image_roles": _image_roles(record),
        "dossier": {
            "path": record["source"]["dossier"],
            "sha256": record["source"]["dossier_sha256"],
            "references": record["references"],
        },
        "product": product,
        "create_only_meta_data": create_only_meta,
        "variations": variations,
    }


def build_contract() -> dict[str, Any]:
    manifest, serialized = load_product_sot()
    rendered = serialized.encode("utf-8")
    return {
        "schema": SCHEMA,
        "sources": {
            "product_sot": "data/product-sot.json",
            "product_sot_sha256": hashlib.sha256(rendered).hexdigest(),
        },
        "category_names": COLLECTION_NAMES,
        "products": [build_product_record(record) for record in manifest["products"].values()],
    }


def serialize_contract() -> str:
    return json.dumps(build_contract(), indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if output is stale")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args(argv)
    contract = build_contract()
    rendered = json.dumps(contract, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != rendered:
            print(f"STALE: {args.output}", file=sys.stderr)
            return 1
        print(f"PASS: {args.output} matches the pinned historical projection")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"Wrote {len(contract['products'])} products to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
