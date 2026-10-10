#!/usr/bin/env python3
"""Fail-closed verification for the founder-approved V2 commerce scenes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageOps

THEME_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
SCROLL_ROOT = THEME_ROOT / "assets" / "scroll-world"
BATCH_ROOT = SCROLL_ROOT / "generated-candidates" / "founder-commerce-scenes-v1"
BLUEPRINT_PATH = THEME_ROOT / "data" / "scene-narrative-blueprints.json"
MANIFEST_PATH = BATCH_ROOT / "manifest.json"
PRODUCT_SOT_PATH = REPO_ROOT / "data" / "product-sot.json"

EXPECTED_CASTS = {
    "BR-COMMERCE-1": ["br-001", "br-002"],
    "BR-COMMERCE-2": ["br-005", "br-007"],
    "BR-COMMERCE-3": ["br-008", "br-009", "br-010", "br-011", "br-012"],
    "LH-COMMERCE-1": ["lh-004", "lh-002", "lh-006"],
    "LH-COMMERCE-2": ["lh-003"],
    "LH-COMMERCE-3": ["lh-005"],
    "SIG-COMMERCE-1": ["sg-009", "sg-007"],
    "SIG-COMMERCE-2": ["sg-013", "sg-014", "sg-006"],
    "SIG-COMMERCE-3": ["sg-001", "sg-005", "sg-003", "sg-002", "sg-015"],
}


def sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def scene_map(blueprint: dict) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for collection in blueprint.get("collections", {}).values():
        for scene in collection.get("commerce_scene_chapters", []):
            scene_id = scene.get("scene_id")
            require(scene_id not in result, f"duplicate scene id: {scene_id}")
            result[scene_id] = scene
    return result


def changed_pixel_count(
    first: Image.Image, second: Image.Image
) -> tuple[int, tuple[int, int, int, int] | None]:
    difference = ImageChops.difference(first.convert("RGB"), second.convert("RGB"))
    pixels = difference.get_flattened_data()
    count = sum(1 for pixel in pixels if pixel != (0, 0, 0))
    return count, difference.getbbox()


def validate_surgical_edit(scene: dict, manifest_scene: dict) -> None:
    source = BATCH_ROOT / manifest_scene["source"]
    output = BATCH_ROOT / manifest_scene["asset"]
    require(source.is_file(), f"missing founder source: {source}")
    require(sha256(source) == manifest_scene["source_sha256"], "founder source hash mismatch")

    with Image.open(source) as source_image, Image.open(output) as output_image:
        require(source_image.size == output_image.size, "surgical edit changed canvas dimensions")
        count, bbox = changed_pixel_count(source_image, output_image)

    allowed = scene["allowed_pixel_edit"]
    require(count == allowed["changed_pixel_count"], f"unexpected changed-pixel count: {count}")
    require(count <= allowed["maximum_changed_pixel_count"], "surgical edit exceeded pixel budget")
    require(bbox is not None, "surgical edit produced no change")
    x, y, width, height = allowed["bounding_box"]
    allowed_right = x + width
    allowed_bottom = y + height
    require(
        bbox[0] >= x and bbox[1] >= y and bbox[2] <= allowed_right and bbox[3] <= allowed_bottom,
        f"surgical edit escaped allowed A region: {bbox}",
    )


def validate_model_layer(layer: dict, manifest_layer: dict) -> None:
    asset = SCROLL_ROOT / layer["asset"]
    layer_skus = layer.get("skus") or [layer.get("sku")]
    layer_skus = [str(sku) for sku in layer_skus if sku]
    sku_label = ",".join(layer_skus)
    require(layer_skus, "model layer has no SKU coverage")
    require(asset.is_file(), f"missing protected model layer: {asset}")
    require(sha256(asset) == layer["sha256"], f"model-layer hash mismatch: {sku_label}")
    require(layer["sha256"] == manifest_layer["sha256"], f"manifest/model hash drift: {sku_label}")
    require(
        str(layer.get("approval_state", "")).startswith("APPROVED"),
        f"unapproved model layer: {sku_label}",
    )
    manifest_skus = manifest_layer.get("skus") or [manifest_layer.get("sku")]
    require(layer_skus == manifest_skus, f"manifest/model SKU coverage drift: {sku_label}")

    with Image.open(asset) as image:
        require(image.mode == "RGBA", f"model layer is not RGBA: {sku_label}")
        require(
            image.getchannel("A").getextrema() == (0, 255),
            f"model layer lacks true alpha: {sku_label}",
        )

    if layer.get("approval_method") == "LIMITED_PRO_SURGICAL_LOGO_PATCH":
        require(
            manifest_layer.get("approval_method") == layer["approval_method"],
            f"limited approval method drift: {sku_label}",
        )
        surgical_path = BATCH_ROOT / manifest_layer["surgical_receipt"]
        adversarial_path = BATCH_ROOT / manifest_layer["adversarial_review"]
        approval_path = BATCH_ROOT / manifest_layer["founder_approval_receipt"]
        for proof in (surgical_path, adversarial_path, approval_path):
            require(proof.is_file(), f"limited approval proof missing: {proof}")
        surgical = load_json(surgical_path)
        adversarial = load_json(adversarial_path)
        approval = load_json(approval_path)
        require(
            surgical.get("output_sha256") == layer["sha256"],
            f"surgical receipt/output hash drift: {sku_label}",
        )
        require(
            surgical.get("changed_pixels_outside_allowed_rois") == 0,
            f"surgical edit escaped approved regions: {sku_label}",
        )
        require(
            surgical.get("all_non_logo_pixels_preserved") is True,
            f"surgical edit lacks preservation proof: {sku_label}",
        )
        require(
            adversarial.get("candidate_sha256") == layer["sha256"],
            f"adversarial review/candidate hash drift: {sku_label}",
        )
        require(
            adversarial.get("verdict") in {"clean", "partially-improved"},
            f"limited candidate adversarial verdict is ineligible: {sku_label}",
        )
        require(
            approval.get("candidate_sha256") == layer["sha256"],
            f"founder approval/candidate hash drift: {sku_label}",
        )
        require(
            approval.get("approval_state") == "FOUNDER_APPROVED",
            f"limited candidate lacks founder approval: {sku_label}",
        )
        require(
            approval.get("approved_scope", {}).get("skus") == layer_skus,
            f"founder approval SKU scope drift: {sku_label}",
        )
        require(
            approval.get("deployment_authorized") is False,
            "founder media approval unexpectedly authorizes deployment",
        )
        bindings = approval.get("bindings", {})
        require(
            bindings.get("surgical_patch_receipt_sha256") == sha256(surgical_path),
            f"founder approval/surgical receipt hash drift: {sku_label}",
        )
        require(
            bindings.get("adversarial_review_sha256") == sha256(adversarial_path),
            f"founder approval/adversarial review hash drift: {sku_label}",
        )
        return

    receipt_path = asset.with_suffix(".receipt.json")
    receipt = load_json(receipt_path)
    require(receipt.get("rgb_preserved") is True, f"RGB preservation not proven: {sku_label}")
    require(
        receipt.get("output_sha256") == layer["sha256"],
        f"receipt/output hash drift: {sku_label}",
    )
    source = (THEME_ROOT / receipt["source"]).resolve()
    require(source.is_file(), f"receipt source missing: {sku_label}")
    require(
        sha256(source) == receipt["source_sha256"], f"receipt source hash mismatch: {sku_label}"
    )
    with Image.open(source) as source_image, Image.open(asset) as output_image:
        require(
            ImageChops.difference(
                ImageOps.exif_transpose(source_image).convert("RGB"),
                output_image.convert("RGB"),
            ).getbbox()
            is None,
            f"protected layer repainted source RGB: {sku_label}",
        )


def validate_baked_founder_scene(scene: dict, manifest_scene: dict) -> None:
    """Validate a founder-selected scene whose product pixels are baked into its plate."""

    scene_id = str(scene["scene_id"])
    receipt_relative = scene.get("founder_approval_receipt")
    require(
        isinstance(receipt_relative, str) and receipt_relative,
        f"missing approval receipt: {scene_id}",
    )
    receipt_path = SCROLL_ROOT / receipt_relative
    require(receipt_path.is_file(), f"missing baked-scene approval receipt: {scene_id}")
    receipt = load_json(receipt_path)

    asset = SCROLL_ROOT / scene["plate_asset"]
    receipt_asset = (REPO_ROOT / str(receipt.get("asset", ""))).resolve()
    require(
        receipt.get("schema") == "skyyrose.founder-scene-approval.v1",
        f"wrong baked-scene approval schema: {scene_id}",
    )
    require(receipt.get("scene_id") == scene_id, f"approval scene drift: {scene_id}")
    require(receipt.get("founder_approved") is True, f"founder approval missing: {scene_id}")
    require(receipt_asset == asset.resolve(), f"approval asset drift: {scene_id}")
    require(receipt.get("sha256") == scene["plate_sha256"], f"approval hash drift: {scene_id}")
    require(
        receipt.get("dimensions") == scene["plate_dimensions"],
        f"approval dimensions drift: {scene_id}",
    )
    require(
        receipt.get("deployment_authorized") is False,
        "scene approval unexpectedly authorizes deployment",
    )
    require(
        receipt.get("production_write_authorized") is False,
        "scene approval unexpectedly authorizes production writes",
    )
    require(
        manifest_scene.get("founder_approval_receipt")
        == str(
            Path(scene["founder_approval_receipt"]).relative_to(
                "generated-candidates/founder-commerce-scenes-v1"
            )
        ),
        f"manifest approval-receipt drift: {scene_id}",
    )

    machine_review = receipt.get("machine_review", {})
    manifest_review = manifest_scene.get("machine_review", {})
    require(
        machine_review.get("verdict") in {"PASS", "REJECT"}, f"missing machine verdict: {scene_id}"
    )
    require(
        machine_review.get("score") == manifest_review.get("score"),
        f"machine score drift: {scene_id}",
    )
    require(
        machine_review.get("verdict") == manifest_review.get("verdict"),
        f"machine verdict drift: {scene_id}",
    )
    if machine_review.get("verdict") == "REJECT":
        require(
            receipt.get("founder_override_of_machine_rejection") is True
            and manifest_review.get("founder_override") is True,
            f"machine rejection lacks explicit founder override: {scene_id}",
        )


def main() -> None:
    blueprint = load_json(BLUEPRINT_PATH)
    manifest = load_json(MANIFEST_PATH)
    current_sot_hash = sha256(PRODUCT_SOT_PATH)
    require(
        blueprint.get("product_sot_sha256") == current_sot_hash,
        "blueprint is stale against product SOT",
    )
    require(
        manifest.get("product_sot_sha256") == current_sot_hash,
        "scene manifest is stale against product SOT",
    )

    scenes = scene_map(blueprint)
    require(
        set(scenes) == set(EXPECTED_CASTS),
        "founder commerce scene IDs are incomplete or unexpected",
    )
    manifest_scenes = {scene["scene_id"]: scene for scene in manifest.get("scenes", [])}
    require(set(manifest_scenes) == set(EXPECTED_CASTS), "scene manifest IDs do not match contract")

    manifest_layers: dict[str, dict] = {}
    for manifest_layer in manifest.get("protected_model_layers", []):
        covered_skus = manifest_layer.get("skus") or [manifest_layer.get("sku")]
        for sku in [str(value) for value in covered_skus if value]:
            require(sku not in manifest_layers, f"duplicate protected layer coverage: {sku}")
            manifest_layers[sku] = manifest_layer
    for scene_id, expected_cast in EXPECTED_CASTS.items():
        scene = scenes[scene_id]
        manifest_scene = manifest_scenes[scene_id]
        require(scene.get("product_bindings") == expected_cast, f"exact SKU cast drift: {scene_id}")
        require(
            scene.get("plate_approval_state", "").startswith("FOUNDER_APPROVED"),
            f"plate not approved: {scene_id}",
        )
        require(
            scene.get("plate_sha256") == manifest_scene.get("sha256"),
            f"blueprint/manifest hash drift: {scene_id}",
        )

        asset = SCROLL_ROOT / scene["plate_asset"]
        require(asset.is_file(), f"missing scene asset: {scene_id}")
        require(sha256(asset) == scene["plate_sha256"], f"scene asset hash mismatch: {scene_id}")
        with Image.open(asset) as image:
            require(
                list(image.size) == scene["plate_dimensions"],
                f"scene dimensions mismatch: {scene_id}",
            )

        scene_layer_skus: list[str] = []
        for layer in scene.get("model_layers", []):
            layer_skus = layer.get("skus") or [layer.get("sku")]
            layer_skus = [str(sku) for sku in layer_skus if sku]
            require(layer_skus, f"model layer has no cast coverage: {scene_id}")
            require(
                all(sku in expected_cast for sku in layer_skus),
                f"model layer outside exact cast: {scene_id}",
            )
            require(
                all(sku in manifest_layers for sku in layer_skus),
                f"model layer missing from manifest: {','.join(layer_skus)}",
            )
            manifest_layer = manifest_layers[layer_skus[0]]
            require(
                all(manifest_layers[sku] is manifest_layer for sku in layer_skus),
                f"combined layer manifest identity drift: {scene_id}",
            )
            validate_model_layer(layer, manifest_layer)
            scene_layer_skus.extend(layer_skus)

        if scene.get("generation_state") == "FOUNDER_APPROVED_PRODUCT_SCENE":
            if scene.get("model_layers"):
                require(
                    sorted(scene_layer_skus) == sorted(expected_cast),
                    f"complete scene lacks exact protected cast: {scene_id}",
                )
            else:
                if scene_id != "BR-COMMERCE-3":
                    validate_baked_founder_scene(scene, manifest_scene)
            require(
                str(manifest_scene.get("composite_state", "")).startswith(
                    "FOUNDER_APPROVED_PRODUCT_SCENE"
                ),
                f"complete scene manifest state drift: {scene_id}",
            )

    if "BR-COMMERCE-3" in scenes:
        validate_surgical_edit(scenes["BR-COMMERCE-3"], manifest_scenes["BR-COMMERCE-3"])

    graphic_rule = manifest.get("black_rose_graphic_rule", {})
    require(
        "pedestal shape" in graphic_rule.get("non_blocking", []),
        "Black Rose base relaxation is missing",
    )
    require("star" in graphic_rule.get("required", []), "Black Rose star identity lock is missing")
    require(
        "single rose" in graphic_rule.get("required", []),
        "Black Rose single-rose identity lock is missing",
    )

    template = (THEME_ROOT / "template-collection.php").read_text(encoding="utf-8")
    functions = (THEME_ROOT / "functions.php").read_text(encoding="utf-8")
    require(
        "skyyrose2_collection_commerce_scenes" in template,
        "runtime does not consume scene contract",
    )
    require(
        "skyyrose2_resolve_commerce_scene_products" in template,
        "runtime does not resolve exact SKU casts",
    )
    require(
        "skyyrose2_collection_scene_product( $slug" not in template,
        "query-order scene resolver remains active",
    )
    require(
        'data-composite-state="' in template,
        "runtime does not expose truthful composite completeness",
    )
    require(
        "'complete' === $scene_composite_state" in template,
        "runtime CTA is not gated by composite completeness",
    )
    require(
        "scene-narrative-blueprints.json" in functions, "runtime scene contract source is missing"
    )

    print(
        "PASS founder commerce scene manifest, hashes, alpha, RGB preservation, casts, and runtime binding"
    )


if __name__ == "__main__":
    main()
