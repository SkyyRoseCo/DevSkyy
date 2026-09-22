#!/usr/bin/env python3
"""Fail closed when the founder commerce review batch loses provenance."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image

THEME_DIR = Path(__file__).resolve().parent.parent
REVIEW_DIR = (
    THEME_DIR
    / "assets/scroll-world/generated-candidates/founder-commerce-scenes-v1/founder-review-batch-v2"
)
MANIFEST_FILE = REVIEW_DIR / "manifest.json"
EXPECTED_CASTS = {
    "br-commerce-1": ["br-001", "br-002"],
    "br-commerce-2": ["br-005", "br-007"],
    "lh-commerce-1": ["lh-004", "lh-002", "lh-006"],
    "lh-commerce-2": ["lh-003"],
    "lh-commerce-3": ["lh-005"],
    "sig-commerce-1": ["sg-009", "sg-007"],
    "sig-commerce-2": ["sg-013", "sg-014", "sg-006"],
    "sig-commerce-3": ["sg-005", "sg-001", "sg-015", "sg-002", "sg-003"],
}
REQUIRED_FIDELITY_CONTRACTS = {
    "br-commerce-2": {
        "br-005: raised tonal silicone cut-out at wearer-right chest",
        "br-005: large embroidered rose artwork on side body, never sleeve or arm",
        "br-007: narrow white side construction, never broad white front-leg panel",
        "br-007: complete Love Hurts script on black field above narrow white insert",
    },
    "sig-commerce-3": {
        "sg-005 + sg-001: complete Bay Bridge shirt-and-shorts look must be visually prominent and readable",
        "sg-001: blue waistband, white drawstring, daytime Bay Bridge wrap, blue rose at lower wearer-left leg",
        "sg-005: white tee with large blue Bay Bridge rose-cluster centered on chest",
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL {message}")


def theme_path(relative: str) -> Path:
    return (THEME_DIR / relative).resolve()


def main() -> None:
    manifest = load_json(MANIFEST_FILE)
    require(
        manifest.get("approval_state") == "FOUNDER_REVIEW_REQUIRED",
        "batch must remain founder-review-only",
    )
    require(manifest.get("production_wired") is False, "batch must not claim production wiring")

    product_sot_record = manifest["product_sot"]
    product_sot_file = theme_path(product_sot_record["file"])
    require(sha256(product_sot_file) == product_sot_record["sha256"], "product SOT hash drift")
    product_sot = load_json(product_sot_file)
    product_values = product_sot["products"]
    if isinstance(product_values, dict):
        product_values = product_values.values()
    products_by_sku = {product["sku"]: product for product in product_values}

    opening_record = manifest["opening_product_media"]
    opening_file = theme_path(opening_record["file"])
    require(sha256(opening_file) == opening_record["sha256"], "opening-media hash drift")
    opening = load_json(opening_file)
    require(
        opening_record["product_sot_sha256"] == product_sot_record["sha256"],
        "manifest product SOT hashes disagree",
    )
    require(
        opening["product_sot_sha256"] == product_sot_record["sha256"],
        "opening-media registry is stale against product SOT",
    )

    scenes = manifest["scenes"]
    require(
        len(scenes) == len(EXPECTED_CASTS), "review batch must contain the remaining eight scenes"
    )
    require(
        {scene["scene_id"] for scene in scenes} == set(EXPECTED_CASTS),
        "scene IDs do not match the remaining-eight contract",
    )

    layer_count = 0
    product_count = 0
    for scene in scenes:
        scene_id = scene["scene_id"]
        require(scene["approval_state"] == "FOUNDER_REVIEW_REQUIRED", f"{scene_id} state drift")
        require(
            scene["upstream_plate_state"].startswith("FOUNDER_APPROVED"),
            f"{scene_id} plate is not approved",
        )
        require(scene["dimensions"] == [1672, 941], f"{scene_id} dimensions drift")

        output_file = theme_path(scene["output"])
        require(sha256(output_file) == scene["output_sha256"], f"{scene_id} output hash drift")
        with Image.open(output_file) as image:
            require(list(image.size) == scene["dimensions"], f"{scene_id} output size mismatch")

        actual_skus = [product["sku"] for product in scene["products"]]
        require(actual_skus == EXPECTED_CASTS[scene_id], f"{scene_id} SKU cast drift")
        required_contracts = REQUIRED_FIDELITY_CONTRACTS.get(scene_id, set())
        require(
            required_contracts.issubset(set(scene.get("fidelity_contracts", []))),
            f"{scene_id} semantic fidelity contract drift",
        )
        product_count += len(actual_skus)
        for record in scene["products"]:
            sku = record["sku"]
            product = products_by_sku[sku]
            opening_product = opening["products"][sku]
            require(record["product_hash"] == product["product_hash"], f"{sku} product hash drift")
            require(
                record["dossier_sha256"] == product["source"]["dossier_sha256"],
                f"{sku} dossier hash drift",
            )
            require(record["references"] == product["references"], f"{sku} reference stack drift")
            for reference in record["references"]:
                reference_file = (THEME_DIR.parents[1] / reference["path"]).resolve()
                require(reference_file.is_file(), f"{sku} reference missing: {reference['path']}")
                require(
                    sha256(reference_file) == reference["sha256"],
                    f"{sku} reference hash drift: {reference['path']}",
                )
            expected_opening_state = opening_product.get("status", "APPROVED_OPENING_MEDIA")
            expected_opening_reason = opening_product.get(
                "reason", "Opening media provides one or more approved product views."
            )
            require(
                record["opening_media_state"] == expected_opening_state,
                f"{sku} opening-media state drift",
            )
            require(
                record["opening_media_reason"] == expected_opening_reason,
                f"{sku} opening-media reason drift",
            )

        layer_skus: list[str] = []
        for layer in scene["layers"]:
            layer_count += 1
            require(layer.get("skus"), f"{scene_id} layer lacks explicit SKU coverage")
            layer_skus.extend(layer["skus"])
            layer_file = theme_path(layer["file"])
            receipt_file = theme_path(layer["protected_layer_receipt"])
            require(sha256(layer_file) == layer["sha256"], f"{scene_id} layer hash drift")
            require(
                sha256(receipt_file) == layer["protected_layer_receipt_sha256"],
                f"{scene_id} layer receipt hash drift",
            )
            receipt = load_json(receipt_file)
            require(
                receipt["output_sha256"] == layer["sha256"], f"{scene_id} receipt/output mismatch"
            )
            require(
                receipt["source_sha256"] == layer["protected_source_sha256"],
                f"{scene_id} source hash drift",
            )
            require(receipt["rgb_preserved"] is True, f"{scene_id} RGB preservation failed")
            with Image.open(layer_file) as image:
                require(image.mode == "RGBA", f"{scene_id} layer is not real RGBA")
                alpha = image.getchannel("A")
                alpha_min, alpha_max = alpha.getextrema()
                require(
                    alpha_min == 0 and alpha_max == 255,
                    f"{scene_id} layer alpha is not a real cutout",
                )
        require(
            sorted(layer_skus) == sorted(EXPECTED_CASTS[scene_id]),
            f"{scene_id} layer SKU coverage does not match its cast",
        )

    br005 = products_by_sku["br-005"]
    br005_regions = br005["garment"]["branding_regions"]
    require(
        any(
            region["region"] == "front-right-chest" and region["technique"] == "silicone"
            for region in br005_regions
        ),
        "br-005 raised silicone chest contract missing",
    )
    require(
        any("side body" in region["region"] for region in br005_regions),
        "br-005 side-body artwork contract missing",
    )
    require(
        not any(
            "forearm" in region["region"] or "sleeve" in region["region"]
            for region in br005_regions
        ),
        "br-005 still permits arm or sleeve artwork",
    )
    br007 = products_by_sku["br-007"]
    require(
        "narrow white mesh side constructions/inserts" in br007["garment"]["type_lock"],
        "br-007 narrow side construction contract missing",
    )
    normalized_br007_regions = " ".join(
        " ".join(region["description"].replace("**", "").split())
        for region in br007["garment"]["branding_regions"]
    )
    require(
        "above the narrow white side construction" in normalized_br007_regions,
        "br-007 Love Hurts placement contract missing",
    )

    prompt_record = manifest["image_model_prompt_contract"]
    require(prompt_record["format"] in {"json", "html"}, "prompt contract format is not allowed")
    require(
        prompt_record["direct_untracked_chat_prompt_forbidden"] is True,
        "untracked image-model prompts are not forbidden",
    )
    prompt_file = theme_path(prompt_record["file"])
    require(sha256(prompt_file) == prompt_record["sha256"], "prompt contract hash drift")
    prompt_contract = load_json(prompt_file)
    require(
        prompt_contract["product_sot_sha256"] == product_sot_record["sha256"],
        "prompt contract is stale against product SOT",
    )
    require(
        prompt_contract["policy"]["direct_untracked_chat_prompt_forbidden"] is True,
        "prompt policy allows direct chat prompts",
    )
    for scene in scenes:
        prompt = prompt_contract["prompts"].get(scene["prompt_contract_id"])
        require(prompt is not None, f"{scene['scene_id']} prompt record missing")
        require(prompt["scene_id"] == scene["scene_id"], f"{scene['scene_id']} prompt ID drift")
        require(
            prompt["skus"] == EXPECTED_CASTS[scene["scene_id"]],
            f"{scene['scene_id']} prompt SKU cast drift",
        )

    for key in ("contact_sheet", "product_detail_sheet"):
        record = manifest[key]
        sheet_file = theme_path(record["output"])
        require(sha256(sheet_file) == record["sha256"], f"{key} hash drift")
        with Image.open(sheet_file) as image:
            require(list(image.size) == record["dimensions"], f"{key} dimensions drift")

    approved = manifest["already_approved_scene"]
    require(approved["scene_id"] == "BR-COMMERCE-3", "approved BR3 reference missing")
    require(approved["excluded_from_remaining_eight_review"] is True, "BR3 exclusion state drift")
    approved_file = (
        THEME_DIR
        / "assets/scroll-world/generated-candidates/founder-commerce-scenes-v1"
        / approved["asset"]
    )
    require(sha256(approved_file) == approved["sha256"], "approved BR3 asset hash drift")

    print(
        "PASS founder review batch: "
        f"{len(scenes)} pending scenes, {product_count} SKU roles, {layer_count} receipted layers, "
        "SOT/opening-media/hash/state/sheet gates intact"
    )


if __name__ == "__main__":
    main()
