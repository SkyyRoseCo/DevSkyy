#!/usr/bin/env python3
"""Surgically replace two drifted jogger logos with the canonical LH artwork."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageChops, ImageOps

PLACEMENTS = (
    {
        "model": "male",
        "roi": (388, 758, 460, 856),
        "logo_box": (392, 762, 456, 852),
        "garment": "black",
    },
    {
        "model": "female",
        "roi": (750, 800, 818, 892),
        "logo_box": (754, 803, 816, 889),
        "garment": "white",
    },
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("logo", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--diff", type=Path, required=True)
    return parser.parse_args()


def canonical_logo_layer(path: Path) -> Image.Image:
    with Image.open(path) as image:
        rgb = ImageOps.exif_transpose(image).convert("RGB")
    array = np.asarray(rgb, dtype=np.uint8)
    distance_from_white = 255 - array.min(axis=2)
    alpha = np.clip((distance_from_white.astype(np.int16) - 8) * 8, 0, 255).astype(np.uint8)
    layer = Image.fromarray(np.dstack((array, alpha)), "RGBA")
    bbox = layer.getchannel("A").getbbox()
    if bbox is None:
        raise ValueError("canonical logo cutout is empty")
    return layer.crop(bbox)


def remove_drifted_logo(image: Image.Image, placement: dict[str, object]) -> None:
    left, top, right, bottom = placement["roi"]
    region = np.asarray(image.crop((left, top, right, bottom)).convert("RGB"), dtype=np.uint8)
    hsv = cv2.cvtColor(region, cv2.COLOR_RGB2HSV)
    saturation = hsv[:, :, 1]
    value = hsv[:, :, 2]
    if placement["garment"] == "black":
        mask = ((saturation > 45) & (value > 65)).astype(np.uint8) * 255
    else:
        mask = ((saturation > 35) | (value < 105)).astype(np.uint8) * 255
    kernel = np.ones((5, 5), dtype=np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=1)
    cleaned = cv2.inpaint(region, mask, 5, cv2.INPAINT_TELEA)
    image.paste(Image.fromarray(cleaned, "RGB").convert("RGBA"), (left, top))


def main() -> int:
    args = parse_args()
    for path in (args.source, args.logo):
        if not path.is_file():
            raise SystemExit(f"missing input: {path}")

    with Image.open(args.source) as source_image:
        source = ImageOps.exif_transpose(source_image).convert("RGBA")
    output = source.copy()
    logo = canonical_logo_layer(args.logo)

    for placement in PLACEMENTS:
        remove_drifted_logo(output, placement)
        left, top, right, bottom = placement["logo_box"]
        fitted = logo.resize((right - left, bottom - top), Image.Resampling.LANCZOS)
        output.alpha_composite(fitted, (left, top))

    source_array = np.asarray(source, dtype=np.uint8)
    output_array = np.asarray(output, dtype=np.uint8)
    changed = np.any(source_array != output_array, axis=2)
    allowed = np.zeros(changed.shape, dtype=bool)
    for placement in PLACEMENTS:
        left, top, right, bottom = placement["roi"]
        allowed[top:bottom, left:right] = True
    changed_outside = int(np.count_nonzero(changed & ~allowed))
    if changed_outside:
        raise SystemExit(f"patch changed {changed_outside} pixels outside allowed logo ROIs")

    alpha_extrema = output.getchannel("A").getextrema()
    if alpha_extrema != (0, 255):
        raise SystemExit(f"output alpha is invalid: {alpha_extrema}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.save(args.output, format="PNG", optimize=True)

    diff = ImageChops.difference(source, output).convert("RGB")
    emphasized = diff.point(lambda value: min(255, value * 4))
    args.diff.parent.mkdir(parents=True, exist_ok=True)
    emphasized.save(args.diff, format="PNG", optimize=True)

    changed_y, changed_x = np.where(changed)
    changed_bounds = [
        int(changed_x.min()),
        int(changed_y.min()),
        int(changed_x.max() + 1),
        int(changed_y.max() + 1),
    ]
    receipt = {
        "schema": "skyyrose.surgical-logo-patch.v1",
        "source": str(args.source),
        "source_sha256": sha256(args.source),
        "canonical_logo": str(args.logo),
        "canonical_logo_sha256": sha256(args.logo),
        "output": str(args.output),
        "output_sha256": sha256(args.output),
        "diff": str(args.diff),
        "diff_sha256": sha256(args.diff),
        "dimensions": list(output.size),
        "alpha_extrema": list(alpha_extrema),
        "placements": list(PLACEMENTS),
        "changed_bounds": changed_bounds,
        "changed_pixels": int(np.count_nonzero(changed)),
        "changed_pixels_outside_allowed_rois": changed_outside,
        "all_non_logo_pixels_preserved": changed_outside == 0,
        "approval_state": "FOUNDER_REVIEW_REQUIRED",
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(
        "PASS_SURGICAL_LOGO_PATCH "
        f"changed_pixels={receipt['changed_pixels']} outside_rois={changed_outside}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
