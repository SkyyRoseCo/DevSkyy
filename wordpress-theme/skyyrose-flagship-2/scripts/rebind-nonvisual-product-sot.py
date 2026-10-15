#!/usr/bin/env python3
"""Rebind derived V2 artifacts after a provably nonvisual product-SOT change.

This command refuses to run when identity, commerce, garment, scene, rendering,
logo, reference, media, verification, source, or consumer-contract data changes.
It exists for canonical merchandising metadata migrations that necessarily
change the full product hash without changing an already-reviewed visual asset.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from skyyrose.core import product_sot  # noqa: E402

MEDIA_MANIFESTS = (
    ROOT / "wordpress-theme/skyyrose-flagship-2/data/opening-product-media.json",
    ROOT / "wordpress-theme/skyyrose-flagship/data/opening-product-media.json",
)
SCENE_MANIFEST = (
    ROOT
    / "wordpress-theme/skyyrose-flagship-2/assets/scroll-world/generated-candidates"
    / "scene-candidate-manifest.json"
)


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _visual_record(record: dict[str, Any]) -> dict[str, Any]:
    comparable = copy.deepcopy(record)
    comparable.pop("merchandising", None)
    comparable.pop("product_hash", None)
    return comparable


def _assert_nonvisual_change(previous: dict[str, Any], current: dict[str, Any]) -> None:
    for field in ("schema", "generated_by", "authority"):
        if previous.get(field) != current.get(field):
            raise ValueError(f"product SOT changed outside merchandising: {field}")

    previous_sources = previous.get("sources", {})
    current_sources = current.get("sources", {})
    for field in ("catalog", "logo_registry", "logo_registry_sha256"):
        if previous_sources.get(field) != current_sources.get(field):
            raise ValueError(f"product SOT source changed outside catalog content: {field}")

    previous_products = previous.get("products", {})
    current_products = current.get("products", {})
    if set(previous_products) != set(current_products):
        raise ValueError("product SOT SKU set changed")
    for sku in previous_products:
        if _visual_record(previous_products[sku]) != _visual_record(current_products[sku]):
            raise ValueError(f"visual or commerce product facts changed for {sku}")


def _rebind_media_manifest(
    manifest: dict[str, Any],
    previous_sot: dict[str, Any],
    current_sot: dict[str, Any],
    previous_sha: str,
    current_sha: str,
    rebound_at: str,
) -> dict[str, Any]:
    previous_products = previous_sot["products"]
    current_products = current_sot["products"]
    previous_hashes = {sku: product["product_hash"] for sku, product in previous_products.items()}
    if manifest.get("product_sot_sha256") != previous_sha:
        raise ValueError("media manifest is not bound to the previous product SOT")
    if manifest.get("product_hashes") != previous_hashes:
        raise ValueError("media manifest product hashes do not match the previous product SOT")

    rebound = copy.deepcopy(manifest)
    rebound["product_sot_sha256"] = current_sha
    rebound["product_hashes"] = {
        sku: product["product_hash"] for sku, product in current_products.items()
    }
    rebound["rebind_provenance"] = {
        "kind": "nonvisual_merchandising_metadata_rebind",
        "rebound_at": rebound_at,
        "previous_product_sot_sha256": previous_sha,
        "current_product_sot_sha256": current_sha,
        "preserved_visual_reviewed_at": manifest.get("reviewed_at", ""),
        "visual_assets_changed": False,
        "allowed_changes": [
            "catalog source hash",
            "merchandising series metadata",
            "derived product hashes",
        ],
    }
    return rebound


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", required=True, help="Recorded YYYY-MM-DD rebind date")
    args = parser.parse_args()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date):
        raise ValueError("--date must use YYYY-MM-DD")

    previous_bytes = product_sot.MANIFEST_PATH.read_bytes()
    previous = json.loads(previous_bytes)
    current = product_sot.build_manifest()
    current_text = product_sot.serialize_manifest(current)
    current_bytes = current_text.encode("utf-8")
    if previous_bytes == current_bytes:
        raise ValueError("product SOT is already current; no rebind is required")
    _assert_nonvisual_change(previous, current)

    media_documents = [json.loads(path.read_text(encoding="utf-8")) for path in MEDIA_MANIFESTS]
    if media_documents[0] != media_documents[1]:
        raise ValueError("V2 and production media manifests differ before rebind")

    previous_sha = _sha256(previous_bytes)
    current_sha = _sha256(current_bytes)
    rebound = _rebind_media_manifest(
        media_documents[0],
        previous,
        current,
        previous_sha,
        current_sha,
        args.date,
    )

    scene: dict[str, Any] | None = None
    if SCENE_MANIFEST.is_file():
        scene = json.loads(SCENE_MANIFEST.read_text(encoding="utf-8"))
        if scene.get("product_sot_sha256") != previous_sha:
            raise ValueError("scene manifest is not bound to the previous product SOT")
        scene["product_sot_sha256"] = current_sha
        scene["product_sot_rebind"] = rebound["rebind_provenance"]

    product_sot.MANIFEST_PATH.write_text(current_text, encoding="utf-8")
    rendered_media = json.dumps(rebound, indent=2, ensure_ascii=False) + "\n"
    for path in MEDIA_MANIFESTS:
        path.write_text(rendered_media, encoding="utf-8")

    if scene is not None:
        SCENE_MANIFEST.write_text(
            json.dumps(scene, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    print(
        "Rebound nonvisual merchandising metadata: "
        f"{previous_sha} -> {current_sha} ({len(current['products'])} products)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
