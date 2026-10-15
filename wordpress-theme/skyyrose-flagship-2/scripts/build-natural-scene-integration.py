#!/usr/bin/env python3
"""Build a natural scene composite while protecting approved product pixels.

The generator is allowed to suggest atmosphere and environmental interaction,
but never owns the final model or garment pixels. The exact approved RGBA model
layer is resized once, placed over alpha-derived floor interaction, and written
last. Fully opaque source pixels therefore remain exact in the production scene.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageFilter, ImageOps


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plate", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--prompt", type=Path, required=True)
    parser.add_argument("--layout-output", type=Path, required=True)
    parser.add_argument("--production-output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--guide", type=Path)
    return parser.parse_args()


def contain_to_canvas(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Crop an arbitrary guide to the production aspect ratio, then resize."""
    target_ratio = size[0] / size[1]
    source_ratio = image.width / image.height
    if source_ratio > target_ratio:
        crop_width = round(image.height * target_ratio)
        left = (image.width - crop_width) // 2
        image = image.crop((left, 0, left + crop_width, image.height))
    elif source_ratio < target_ratio:
        crop_height = round(image.width / target_ratio)
        top = (image.height - crop_height) // 2
        image = image.crop((0, top, image.width, top + crop_height))
    return image.resize(size, Image.Resampling.LANCZOS)


def scale_model(model: Image.Image, height: int) -> Image.Image:
    width = round(model.width * height / model.height)
    return model.resize((width, height), Image.Resampling.LANCZOS)


def paste_rgba(base: Image.Image, layer: Image.Image, xy: tuple[int, int]) -> Image.Image:
    result = base.copy()
    result.alpha_composite(layer, dest=xy)
    return result


def alpha_foot_interaction(
    canvas_size: tuple[int, int],
    model: Image.Image,
    xy: tuple[int, int],
    floor_y: int,
) -> tuple[Image.Image, Image.Image, Image.Image]:
    """Return contact shadow, subtle reflection, and ambient edge light."""
    placed_alpha = Image.new("L", canvas_size, 0)
    placed_alpha.paste(model.getchannel("A"), xy)

    # Contact shadow is derived only from the bottom of the approved alpha.
    lower_band = Image.new("L", canvas_size, 0)
    band_top = max(0, floor_y - 70)
    lower_band.paste(placed_alpha.crop((0, band_top, canvas_size[0], floor_y + 8)), (0, band_top))
    contact_alpha = lower_band.filter(ImageFilter.GaussianBlur(15))
    contact_alpha = ImageChops.offset(contact_alpha, 0, 8)
    band_mask = Image.new("L", canvas_size, 0)
    gradient_height = 44
    gradient = Image.new("L", (canvas_size[0], gradient_height))
    gradient.putdata(
        [
            max(0, 255 - round(abs(y - 16) * 255 / 28))
            for y in range(gradient_height)
            for _ in range(canvas_size[0])
        ]
    )
    band_mask.paste(gradient, (0, floor_y - 18))
    contact_alpha = ImageChops.multiply(contact_alpha, band_mask).point(
        lambda value: round(value * 0.72)
    )
    contact = Image.new("RGBA", canvas_size, (2, 0, 1, 0))
    contact.putalpha(contact_alpha)

    # A vertically compressed, rapidly fading reflection sells the polished floor.
    bbox = placed_alpha.getbbox()
    reflection = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    if bbox:
        placed_model = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
        placed_model.alpha_composite(model, dest=xy)
        crop = placed_model.crop(bbox).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        reflected_height = min(canvas_size[1] - floor_y, 82)
        if reflected_height > 0:
            crop = crop.resize((crop.width, reflected_height), Image.Resampling.LANCZOS)
            crop_array = np.asarray(crop, dtype=np.uint8).copy()
            crop_array[..., :3] = np.round(crop_array[..., :3] * np.array([0.30, 0.16, 0.17])).clip(
                0, 255
            )
            fade = np.linspace(0.18, 0.0, reflected_height, dtype=np.float32)[:, None]
            crop_array[..., 3] = np.round(crop_array[..., 3].astype(np.float32) * fade).clip(0, 255)
            reflected = Image.fromarray(crop_array, "RGBA").filter(ImageFilter.GaussianBlur(2.2))
            reflection.alpha_composite(reflected, dest=(bbox[0], floor_y))

    # Warm light around, never on top of, the protected product pixels.
    expanded = placed_alpha.filter(ImageFilter.MaxFilter(17)).filter(ImageFilter.GaussianBlur(8))
    edge_only = ImageChops.subtract(expanded, placed_alpha).point(lambda value: round(value * 0.20))
    rim = Image.new("RGBA", canvas_size, (155, 46, 28, 0))
    rim.putalpha(edge_only)
    return contact, reflection, rim


def main() -> int:
    args = parse_args()
    for required in (args.plate, args.model, args.prompt):
        if not required.is_file():
            raise SystemExit(f"required input does not exist: {required}")

    prompt = json.loads(args.prompt.read_text(encoding="utf-8"))
    layout = prompt["layout_contract"]
    canvas_size = tuple(layout["canvas"])
    group = layout["protected_group"]
    model_xy = (int(group["x_px"]), int(group["y_px"]))
    model_height = int(group["height_px"])
    floor_y = int(group["floor_contact_y_px"])

    expected_hashes = {item["role"]: item["sha256"] for item in prompt["inputs"]}
    plate_hash = sha256(args.plate)
    model_hash = sha256(args.model)
    if plate_hash != expected_hashes["founder_approved_love_hurts_cathedral_plate"]:
        raise SystemExit("plate hash does not match the prompt contract")
    if model_hash != expected_hashes["founder_approved_protected_two_model_product_layer"]:
        raise SystemExit("model hash does not match the prompt contract")

    with Image.open(args.plate) as plate_source:
        plate = ImageOps.exif_transpose(plate_source).convert("RGBA")
    if plate.size != canvas_size:
        raise SystemExit(f"plate dimensions changed: {plate.size} != {canvas_size}")
    with Image.open(args.model) as model_source:
        model = ImageOps.exif_transpose(model_source).convert("RGBA")
    alpha_extrema = model.getchannel("A").getextrema()
    if alpha_extrema != (0, 255):
        raise SystemExit(f"model layer lacks meaningful alpha: {alpha_extrema}")

    scaled_model = scale_model(model, model_height)
    contact, reflection, rim = alpha_foot_interaction(canvas_size, scaled_model, model_xy, floor_y)

    # Layout target shown to Image 2. It already includes physically meaningful
    # interaction, so the model is asked to refine a bounded visual problem.
    layout_image = plate.copy()
    layout_image = Image.alpha_composite(layout_image, rim)
    layout_image = Image.alpha_composite(layout_image, reflection)
    layout_image = Image.alpha_composite(layout_image, contact)
    layout_image = paste_rgba(layout_image, scaled_model, model_xy)
    args.layout_output.parent.mkdir(parents=True, exist_ok=True)
    layout_image.convert("RGB").save(args.layout_output, format="PNG", optimize=True)

    production_base = plate.copy()
    guide_hash = None
    if args.guide:
        if not args.guide.is_file():
            raise SystemExit(f"guide does not exist: {args.guide}")
        guide_hash = sha256(args.guide)
        with Image.open(args.guide) as guide_source:
            guide = contain_to_canvas(
                ImageOps.exif_transpose(guide_source).convert("RGBA"), canvas_size
            )

        # Generated environment treatment may survive only outside a generous
        # protected silhouette. The original approved plate is restored around
        # the models to remove stray generated hair, limbs, or garment pixels.
        placed_alpha = Image.new("L", canvas_size, 0)
        placed_alpha.paste(scaled_model.getchannel("A"), model_xy)
        protected_zone = placed_alpha.filter(ImageFilter.MaxFilter(31)).filter(
            ImageFilter.GaussianBlur(2)
        )
        production_base = Image.composite(plate, guide, protected_zone)

    production = Image.alpha_composite(production_base, rim)
    production = Image.alpha_composite(production, reflection)
    production = Image.alpha_composite(production, contact)
    production = paste_rgba(production, scaled_model, model_xy)

    # Verify every fully opaque model pixel is exact after final compositing.
    output_rgb = np.asarray(production.convert("RGB"), dtype=np.uint8)
    model_rgb = np.asarray(scaled_model.convert("RGB"), dtype=np.uint8)
    model_alpha = np.asarray(scaled_model.getchannel("A"), dtype=np.uint8)
    x, y = model_xy
    region = output_rgb[y : y + scaled_model.height, x : x + scaled_model.width]
    opaque_mask = model_alpha == 255
    exact_opaque_pixels = bool(np.array_equal(region[opaque_mask], model_rgb[opaque_mask]))
    if not exact_opaque_pixels:
        raise SystemExit("final composite changed fully opaque protected model pixels")

    args.production_output.parent.mkdir(parents=True, exist_ok=True)
    production.convert("RGB").save(args.production_output, format="PNG", optimize=True)

    scaled_alpha_bbox = scaled_model.getchannel("A").getbbox()
    placed_bbox = None
    if scaled_alpha_bbox:
        placed_bbox = [
            scaled_alpha_bbox[0] + x,
            scaled_alpha_bbox[1] + y,
            scaled_alpha_bbox[2] + x,
            scaled_alpha_bbox[3] + y,
        ]
    expected_bbox = list(group["expected_opaque_bounds_px"])
    if placed_bbox is None:
        raise SystemExit(f"placed model bounds drifted: {placed_bbox} vs {expected_bbox}")
    bbox_delta = [
        abs(actual - expected) for actual, expected in zip(placed_bbox, expected_bbox, strict=True)
    ]
    if any(delta > 6 for delta in bbox_delta):
        raise SystemExit(f"placed model bounds drifted: {placed_bbox} vs {expected_bbox}")

    receipt = {
        "schema": "skyyrose.natural-scene-integration-receipt.v1",
        "scene_id": prompt["scene_id"],
        "prompt": str(args.prompt),
        "prompt_sha256": sha256(args.prompt),
        "plate": str(args.plate),
        "plate_sha256": plate_hash,
        "protected_model_layer": str(args.model),
        "protected_model_layer_sha256": model_hash,
        "guide": str(args.guide) if args.guide else None,
        "guide_sha256": guide_hash,
        "layout_output": str(args.layout_output),
        "layout_output_sha256": sha256(args.layout_output),
        "production_output": str(args.production_output),
        "production_output_sha256": sha256(args.production_output),
        "dimensions": list(canvas_size),
        "model_placement": {
            "origin": list(model_xy),
            "scaled_dimensions": list(scaled_model.size),
            "opaque_bounds": placed_bbox,
            "floor_contact_y": floor_y,
        },
        "product_pixel_policy": {
            "generator_output_is_guide_only": True,
            "generated_pixels_removed_within_dilated_model_silhouette": bool(args.guide),
            "protected_layer_composited_last": True,
            "fully_opaque_model_rgb_exact": exact_opaque_pixels,
            "contact_shadow_derived_from_alpha": True,
            "reflection_derived_from_protected_layer": True,
        },
        "approval_state": "FOUNDER_REVIEW_REQUIRED",
        "v2_wired": False,
        "deployment_authorized": False,
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
