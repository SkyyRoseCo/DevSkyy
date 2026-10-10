#!/usr/bin/env python3
"""Fail closed when approved V2 card media drifts from product or asset truth."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
THEME = Path(__file__).resolve().parents[1]
SOURCE_THEME = ROOT / "wordpress-theme/skyyrose-flagship"
sys.path.insert(0, str(ROOT / "tools/v2-source-certification"))
from inputs import SOT as PRODUCT_SOT
from inputs import load_product_sot

MEDIA_MANIFEST = THEME / "data/opening-product-media.json"

ALLOWED_ROLES = {
    "on_model_front",
    "on_model_back",
    "mannequin_front",
    "mannequin_back",
    "render_3d",
    "packshot",
}
BLOCKED_STATUSES = {
    "MISSING_APPROVED_ON_MODEL_FRONT",
    "REJECTED_AUTHENTICITY",
    "FOUNDER_REVIEW_REQUIRED",
    "STALE_PRODUCT_HASH",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_asset(root: Path, raw: object, label: str) -> Path:
    if not isinstance(raw, str) or not raw or Path(raw).is_absolute() or ".." in Path(raw).parts:
        raise ValueError(f"{label} is not a safe relative asset path")
    resolved_root = root.resolve()
    resolved = (root / raw).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as error:
        raise ValueError(f"{label} escapes its approved asset root") from error
    if not resolved.is_file():
        raise ValueError(f"{label} does not resolve: {raw}")
    return resolved


def validate_integrity(path: Path, integrity: dict, field: str, label: str) -> None:
    expected_sha = integrity.get(f"{field}_sha256")
    expected_bytes = integrity.get(f"{field}_bytes")
    if not isinstance(expected_sha, str) or len(expected_sha) != 64:
        raise ValueError(f"{label} has no valid {field} SHA-256")
    if not isinstance(expected_bytes, int) or expected_bytes <= 0:
        raise ValueError(f"{label} has no valid {field} byte count")
    if path.stat().st_size != expected_bytes or sha256(path) != expected_sha:
        raise ValueError(f"{label} {field} asset integrity drift")


def main() -> int:
    load_product_sot()
    product_sot_bytes = PRODUCT_SOT.read_bytes()
    product_sot = json.loads(product_sot_bytes)
    media = json.loads(MEDIA_MANIFEST.read_text(encoding="utf-8"))
    expected_sha = hashlib.sha256(product_sot_bytes).hexdigest()
    if media.get("schema") != "skyyrose.sot.product-card-media.v2":
        raise ValueError("opening product-media schema is unsupported")
    if media.get("product_sot_sha256") != expected_sha:
        raise ValueError("opening-product-media.json is not bound to the current product SOT")

    products = product_sot.get("products", {})
    media_products = media.get("products", {})
    product_hashes = media.get("product_hashes", {})
    asset_integrity = media.get("asset_integrity", {})
    if not isinstance(products, dict) or not isinstance(media_products, dict):
        raise ValueError("product SOT or opening product-media products are malformed")
    if set(products) != set(media_products) or set(products) != set(product_hashes):
        raise ValueError("opening product-media SKU set differs from the product SOT")
    if not isinstance(asset_integrity, dict):
        raise ValueError("opening product-media asset integrity map is malformed")

    derivative_budget = media.get("delivery", {}).get("max_bytes")
    if not isinstance(derivative_budget, int) or derivative_budget <= 0:
        raise ValueError("opening product-media derivative budget is invalid")

    view_skus: set[str] = set()
    for sku, product in products.items():
        record = media_products[sku]
        if not isinstance(record, dict):
            raise ValueError(f"opening product-media record is malformed: {sku}")
        expected_product_hash = product.get("product_hash")
        if not expected_product_hash or product_hashes.get(sku) != expected_product_hash:
            raise ValueError(f"opening product-media approval is stale for {sku}")
        expected_collection = product.get("identity", {}).get("collection")
        if record.get("collection") != expected_collection:
            raise ValueError(f"opening product-media collection drift for {sku}")

        views = record.get("views", [])
        if not isinstance(views, list):
            raise ValueError(f"opening product-media views are malformed: {sku}")
        if not views:
            if record.get("status") not in BLOCKED_STATUSES or not record.get("reason"):
                raise ValueError(
                    f"unapproved product media needs a blocked status and reason: {sku}"
                )
            if sku in asset_integrity:
                raise ValueError(
                    f"blocked product unexpectedly has approved asset integrity: {sku}"
                )
            continue

        view_skus.add(sku)
        if record.get("status") not in (None, "APPROVED"):
            raise ValueError(f"approved product has a blocked status: {sku}")
        if views[0].get("role") != "on_model_front":
            raise ValueError(f"approved product does not open on an on-model front: {sku}")
        roles = [view.get("role") for view in views]
        if any(role not in ALLOWED_ROLES for role in roles) or len(roles) != len(set(roles)):
            raise ValueError(f"opening product-media roles are invalid or duplicated: {sku}")
        integrity_roles = asset_integrity.get(sku)
        if not isinstance(integrity_roles, dict) or set(integrity_roles) != set(roles):
            raise ValueError(
                f"opening product-media integrity roles differ from approved views: {sku}"
            )

        for view in views:
            role = view["role"]
            integrity = integrity_roles[role]
            if not isinstance(integrity, dict):
                raise ValueError(
                    f"opening product-media integrity record is malformed: {sku} {role}"
                )
            source = resolve_asset(SOURCE_THEME, view.get("source"), f"{sku} {role} source")
            validate_integrity(source, integrity, "source", f"{sku} {role}")
            derivative_raw = view.get("derivative")
            if derivative_raw:
                derivative = resolve_asset(THEME, derivative_raw, f"{sku} {role} derivative")
                validate_integrity(derivative, integrity, "derivative", f"{sku} {role}")
                if (
                    derivative.suffix.lower() != ".webp"
                    or derivative.stat().st_size > derivative_budget
                ):
                    raise ValueError(f"{sku} {role} derivative violates delivery policy")
            elif any(key.startswith("derivative_") for key in integrity):
                raise ValueError(f"{sku} {role} records derivative integrity without a derivative")

    if set(asset_integrity) != view_skus:
        raise ValueError(
            "opening product-media asset integrity SKU set differs from approved views"
        )

    print(
        f"Opening product media is hash-bound to {len(products)} products and {len(view_skus)} approved SKU asset sets."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
