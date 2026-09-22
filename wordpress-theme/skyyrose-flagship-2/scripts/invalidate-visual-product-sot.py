#!/usr/bin/env python3
"""Rebind media manifests after visual product truth changes, fail closed.

Unlike ``rebind-nonvisual-product-sot.py``, this command never carries an
approved asset across a changed product hash. Any changed SKU with approved
views is cleared and marked ``STALE_PRODUCT_HASH`` for regeneration and
founder review. Already-blocked SKU records keep their existing status and
reason. Unchanged SKU approvals remain hash-bound and intact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
PRODUCT_SOT = ROOT / "data/product-sot.json"
MEDIA_MANIFESTS = (
    ROOT / "wordpress-theme/skyyrose-flagship-2/data/opening-product-media.json",
    ROOT / "wordpress-theme/skyyrose-flagship/data/opening-product-media.json",
)
SCENE_BLUEPRINT = ROOT / "wordpress-theme/skyyrose-flagship-2/data/scene-narrative-blueprints.json"
SCENE_MANIFEST = (
    ROOT
    / "wordpress-theme/skyyrose-flagship-2/assets/scroll-world/generated-candidates"
    / "founder-commerce-scenes-v1/manifest.json"
)
BLOCKED_STATUSES = {
    "MISSING_APPROVED_ON_MODEL_FRONT",
    "REJECTED_AUTHENTICITY",
    "FOUNDER_REVIEW_REQUIRED",
    "STALE_PRODUCT_HASH",
}


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _invalidate_manifest(
    manifest: dict[str, Any],
    current_products: dict[str, Any],
    product_sot_sha256: str,
    audited_at: str,
) -> tuple[dict[str, Any], list[str], list[str]]:
    media_products = manifest.get("products", {})
    previous_hashes = manifest.get("product_hashes", {})
    asset_integrity = manifest.get("asset_integrity", {})
    if not all(
        isinstance(value, dict) for value in (media_products, previous_hashes, asset_integrity)
    ):
        raise ValueError("media manifest product maps are malformed")
    if set(current_products) != set(media_products) or set(current_products) != set(
        previous_hashes
    ):
        raise ValueError("media manifest SKU set differs from product SOT")

    invalidated: list[str] = []
    changed_blocked: list[str] = []
    for sku, current in current_products.items():
        current_hash = current.get("product_hash")
        if not isinstance(current_hash, str) or len(current_hash) != 64:
            raise ValueError(f"product SOT hash is invalid: {sku}")
        if previous_hashes.get(sku) == current_hash:
            continue

        record = media_products[sku]
        if not isinstance(record, dict):
            raise ValueError(f"media record is malformed: {sku}")
        views = record.get("views", [])
        if not isinstance(views, list):
            raise ValueError(f"media views are malformed: {sku}")
        if views:
            record["status"] = "STALE_PRODUCT_HASH"
            record["reason"] = (
                "Founder flatlay/techflat audit changed the product visual contract; "
                "previous media must be regenerated and reviewed against the new hash."
            )
            record["views"] = []
            asset_integrity.pop(sku, None)
            invalidated.append(sku)
        else:
            if record.get("status") not in BLOCKED_STATUSES or not record.get("reason"):
                raise ValueError(f"changed unapproved SKU is not fail-closed: {sku}")
            changed_blocked.append(sku)

    if not invalidated and not changed_blocked:
        previous_audit = manifest.get("visual_contract_audit", {})
        invalidated = list(previous_audit.get("changed_approved_skus_invalidated", []))
        changed_blocked = list(previous_audit.get("changed_blocked_skus_preserved", []))

    manifest["product_sot_sha256"] = product_sot_sha256
    manifest["product_hashes"] = {
        sku: product["product_hash"] for sku, product in current_products.items()
    }
    manifest["visual_contract_audit"] = {
        "kind": "founder_flatlay_techflat_dossier_reconciliation",
        "audited_at": audited_at,
        "changed_approved_skus_invalidated": invalidated,
        "changed_blocked_skus_preserved": changed_blocked,
        "unchanged_approvals_preserved": True,
        "visual_assets_changed": False,
    }
    return manifest, invalidated, changed_blocked


def _rebind_scene_contracts(
    product_sot_sha256: str,
    audited_at: str,
    changed_skus: list[str],
) -> list[str]:
    blueprint = _load(SCENE_BLUEPRINT)
    manifest = _load(SCENE_MANIFEST)
    affected_scene_ids: list[str] = []
    changed = set(changed_skus)

    for collection in blueprint.get("collections", {}).values():
        for scene in collection.get("commerce_scene_chapters", []):
            if changed.intersection(scene.get("product_bindings", [])):
                scene_id = scene["scene_id"]
                affected_scene_ids.append(scene_id)
                scene["generation_gate"] = "CORRECTED_PRODUCT_LAYERS_REQUIRED"
                scene["generation_state"] = "PRODUCT_VISUAL_CONTRACT_CHANGED_REVIEW_REQUIRED"

    for scene in manifest.get("scenes", []):
        if scene.get("scene_id") in affected_scene_ids:
            if not str(scene.get("plate_state", "")).startswith("FOUNDER_APPROVED"):
                raise ValueError(
                    f"affected scene plate is not founder approved: {scene['scene_id']}"
                )
            scene["composite_state"] = "PENDING_CORRECTED_PRODUCT_LAYERS"

    audit = {
        "kind": "visual_product_sot_scene_rebind",
        "audited_at": audited_at,
        "changed_skus": sorted(changed),
        "affected_scene_ids": sorted(set(affected_scene_ids)),
        "plate_assets_changed": False,
        "product_layers_require_founder_review": True,
    }
    blueprint["product_sot_sha256"] = product_sot_sha256
    blueprint["visual_product_sot_rebind"] = audit
    manifest["product_sot_sha256"] = product_sot_sha256
    manifest["visual_product_sot_rebind"] = audit
    SCENE_BLUEPRINT.write_text(
        json.dumps(blueprint, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    SCENE_MANIFEST.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return sorted(set(affected_scene_ids))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", required=True, help="Recorded YYYY-MM-DD audit date")
    args = parser.parse_args()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date):
        raise ValueError("--date must use YYYY-MM-DD")

    product_sot_bytes = PRODUCT_SOT.read_bytes()
    product_sot = json.loads(product_sot_bytes)
    current_products = product_sot.get("products", {})
    if not isinstance(current_products, dict) or not current_products:
        raise ValueError("product SOT has no products")

    invalidated_by_manifest: dict[str, list[str]] = {}
    blocked_by_manifest: dict[str, list[str]] = {}
    product_sot_sha256 = _sha256(product_sot_bytes)
    for path in MEDIA_MANIFESTS:
        manifest, invalidated, changed_blocked = _invalidate_manifest(
            _load(path), current_products, product_sot_sha256, args.date
        )
        path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        invalidated_by_manifest[str(path.relative_to(ROOT))] = invalidated
        blocked_by_manifest[str(path.relative_to(ROOT))] = changed_blocked

    print(
        f"Rebound {len(current_products)} product hashes; invalidated "
        f"{sum(len(value) for value in invalidated_by_manifest.values())} stale "
        f"approved manifest record(s); preserved "
        f"{sum(len(value) for value in blocked_by_manifest.values())} changed "
        f"blocked manifest record(s)."
    )
    for path, skus in invalidated_by_manifest.items():
        if skus:
            print(f"invalidated in {path}: " + ", ".join(skus))
    changed_skus = sorted(
        {
            sku
            for values in (*invalidated_by_manifest.values(), *blocked_by_manifest.values())
            for sku in values
        }
    )
    affected_scenes = _rebind_scene_contracts(product_sot_sha256, args.date, changed_skus)
    if affected_scenes:
        print("scene product layers require renewed founder review: " + ", ".join(affected_scenes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
