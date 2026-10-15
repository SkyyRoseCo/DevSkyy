#!/usr/bin/env python3
"""Compose a protected RGBA product/model layer into a candidate scene.

This is intentionally not an image generator. It places real-alpha input layers
last, derives only floor interaction from their alpha, records every input hash,
and makes the resulting file founder-review-only. It is the sanctioned route
for scene candidates when a full-frame model would redraw a garment.
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


def open_rgba(path: Path) -> Image.Image:
    with Image.open(path) as source:
        return ImageOps.exif_transpose(source).convert("RGBA")


def meaningful_alpha(image: Image.Image) -> bool:
    alpha = image.getchannel("A")
    return alpha.getextrema() == (0, 255) and alpha.getbbox() is not None


def scale_to_height(image: Image.Image, height: int) -> Image.Image:
    if height <= 0:
        raise ValueError("layer height must be positive")
    width = round(image.width * height / image.height)
    return image.resize((width, height), Image.Resampling.LANCZOS)


def parse_overlay(value: str) -> tuple[Path, int, int, int]:
    path, x, y, width = value.rsplit(":", 3)
    return Path(path), int(x), int(y), int(width)


def place(base: Image.Image, layer: Image.Image, x: int, y: int) -> Image.Image:
    result = base.copy()
    result.alpha_composite(layer, (x, y))
    return result


def interaction(
    canvas_size: tuple[int, int], layer: Image.Image, x: int, y: int, floor_y: int
) -> tuple[Image.Image, Image.Image]:
    """Create a contact shadow and short floor reflection without drawing on a layer."""
    alpha = Image.new("L", canvas_size, 0)
    alpha.paste(layer.getchannel("A"), (x, y))
    shadow_alpha = alpha.filter(ImageFilter.GaussianBlur(18))
    shadow_alpha = ImageChops.offset(shadow_alpha, 0, 12).point(lambda pixel: round(pixel * 0.48))
    band = Image.new("L", canvas_size, 0)
    band_top = max(0, floor_y - 30)
    band_bottom = min(canvas_size[1], floor_y + 35)
    if band_bottom > band_top:
        band.paste(255, (0, band_top, canvas_size[0], band_bottom))
    shadow_alpha = ImageChops.multiply(shadow_alpha, band)
    shadow = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    shadow.putalpha(shadow_alpha)

    reflection = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    bbox = alpha.getbbox()
    if bbox and floor_y < canvas_size[1]:
        placed = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
        placed.alpha_composite(layer, (x, y))
        crop = placed.crop(bbox).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        height = min(76, canvas_size[1] - floor_y)
        if height > 0:
            crop = crop.resize((crop.width, height), Image.Resampling.LANCZOS)
            pixels = np.asarray(crop, dtype=np.uint8).copy()
            pixels[..., :3] = np.round(pixels[..., :3] * np.array([0.32, 0.22, 0.26])).clip(0, 255)
            fade = np.linspace(0.16, 0.0, height, dtype=np.float32)[:, None]
            pixels[..., 3] = np.round(pixels[..., 3] * fade).clip(0, 255)
            reflected = Image.fromarray(pixels, "RGBA").filter(ImageFilter.GaussianBlur(2))
            reflection.alpha_composite(reflected, (bbox[0], floor_y))
    return shadow, reflection


def verify_exact_opaque(composite: Image.Image, layer: Image.Image, x: int, y: int) -> bool:
    canvas = np.asarray(composite.convert("RGB"), dtype=np.uint8)
    source = np.asarray(layer.convert("RGB"), dtype=np.uint8)
    alpha = np.asarray(layer.getchannel("A"), dtype=np.uint8)
    region = canvas[y : y + layer.height, x : x + layer.width]
    return bool(np.array_equal(region[alpha == 255], source[alpha == 255]))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene-id", required=True)
    parser.add_argument("--plate", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--x", type=int, required=True)
    parser.add_argument("--y", type=int, required=True)
    parser.add_argument("--height", type=int, required=True)
    parser.add_argument("--floor-y", type=int, required=True)
    parser.add_argument("--overlay", action="append", default=[], metavar="PATH:X:Y:WIDTH")
    args = parser.parse_args()

    if not args.plate.is_file() or not args.model.is_file():
        raise SystemExit("plate and protected model must both exist")
    plate = open_rgba(args.plate)
    model_original = open_rgba(args.model)
    if not meaningful_alpha(model_original):
        raise SystemExit("protected model must have real alpha containing both 0 and 255")
    model = scale_to_height(model_original, args.height)
    if (
        args.x < 0
        or args.y < 0
        or args.x + model.width > plate.width
        or args.y + model.height > plate.height
    ):
        raise SystemExit("model placement exceeds plate bounds")

    overlays: list[dict[str, object]] = []
    base = plate.copy()
    for overlay_value in args.overlay:
        overlay_path, x, y, width = parse_overlay(overlay_value)
        if not overlay_path.is_file():
            raise SystemExit(f"overlay does not exist: {overlay_path}")
        overlay = open_rgba(overlay_path)
        if not meaningful_alpha(overlay):
            raise SystemExit(f"overlay lacks real alpha: {overlay_path}")
        height = round(overlay.height * width / overlay.width)
        overlay = overlay.resize((width, height), Image.Resampling.LANCZOS)
        if x < 0 or y < 0 or x + overlay.width > plate.width or y + overlay.height > plate.height:
            raise SystemExit(f"overlay placement exceeds plate bounds: {overlay_path}")
        base = place(base, overlay, x, y)
        overlays.append(
            {
                "path": str(overlay_path),
                "sha256": sha256(overlay_path),
                "placement": [x, y, overlay.width, overlay.height],
            }
        )

    shadow, reflection = interaction(plate.size, model, args.x, args.y, args.floor_y)
    result = Image.alpha_composite(base, reflection)
    result = Image.alpha_composite(result, shadow)
    result = place(result, model, args.x, args.y)
    exact_opaque = verify_exact_opaque(result, model, args.x, args.y)
    if not exact_opaque:
        raise SystemExit("protected model opaque pixels changed during compositing")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.convert("RGB").save(args.output, format="PNG", optimize=True)
    receipt = {
        "schema": "skyyrose.protected-scene-composite.v1",
        "scene_id": args.scene_id,
        "candidate_only": True,
        "founder_approval_required": True,
        "v2_wired": False,
        "deployment_authorized": False,
        "plate": {
            "path": str(args.plate),
            "sha256": sha256(args.plate),
            "dimensions": list(plate.size),
        },
        "protected_model": {
            "path": str(args.model),
            "sha256": sha256(args.model),
            "placement": [args.x, args.y, model.width, model.height],
            "fully_opaque_rgb_exact": exact_opaque,
        },
        "overlays": overlays,
        "floor_interaction": {
            "floor_y": args.floor_y,
            "shadow": "alpha_derived",
            "reflection": "alpha_derived",
        },
        "output": {"path": str(args.output), "sha256": sha256(args.output)},
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
