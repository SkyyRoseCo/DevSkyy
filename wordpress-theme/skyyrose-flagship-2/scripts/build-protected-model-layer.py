#!/usr/bin/env python3
"""Build a hash-bound transparent model layer without repainting source RGB.

The installed rembg entry point currently imports NumPy aliases removed in
NumPy 2.x. This wrapper supplies the compatibility aliases before importing
rembg, uses the local IS-Net model, and then discards every RGB value produced
by the segmentation library. Only its alpha mask is retained; the output RGB
channels are copied byte-for-byte from the approved source image.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

NUMPY_COMPAT_ALIASES = {
    "alltrue": "all",
    "cumproduct": "cumprod",
    "in1d": "isin",
    "product": "prod",
    "round_": "round",
    "sometrue": "any",
    "trapz": "trapezoid",
}


def sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def install_numpy_compatibility_aliases() -> None:
    for old_name, current_name in NUMPY_COMPAT_ALIASES.items():
        if not hasattr(np, old_name) and hasattr(np, current_name):
            setattr(np, old_name, getattr(np, current_name))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a protected RGBA model layer from an approved RGB source."
    )
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--model", default="isnet-general-use")
    parser.add_argument(
        "--alpha-source",
        type=Path,
        help="Reuse the alpha channel from an existing same-size RGBA cutout.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.source.is_file():
        raise SystemExit(f"source image does not exist: {args.source}")
    if args.output.suffix.lower() != ".png":
        raise SystemExit("protected model layers must be written as PNG")

    with Image.open(args.source) as source_image:
        source_rgb = ImageOps.exif_transpose(source_image).convert("RGB")
        source_size = source_rgb.size

    if args.alpha_source:
        if not args.alpha_source.is_file():
            raise SystemExit(f"alpha source does not exist: {args.alpha_source}")
        with Image.open(args.alpha_source) as alpha_source_image:
            segmented = ImageOps.exif_transpose(alpha_source_image).convert("RGBA")
    else:
        install_numpy_compatibility_aliases()
        try:
            from rembg import new_session, remove
        except Exception as error:  # pragma: no cover - exercised by runtime preflight.
            raise SystemExit(f"background-removal runtime preflight failed: {error}") from error
        session = new_session(args.model)
        segmented = remove(
            source_rgb,
            session=session,
            alpha_matting=False,
            post_process_mask=True,
        ).convert("RGBA")
    if segmented.size != source_size:
        raise SystemExit(f"segmentation changed dimensions: {segmented.size} != {source_size}")

    alpha = segmented.getchannel("A")
    alpha_min, alpha_max = alpha.getextrema()
    if alpha_min != 0 or alpha_max != 255:
        raise SystemExit(
            f"segmentation did not produce meaningful transparency: {(alpha_min, alpha_max)}"
        )

    alpha_array = np.asarray(alpha, dtype=np.uint8)
    opaque_fraction = float(np.count_nonzero(alpha_array >= 128) / alpha_array.size)
    if not 0.05 <= opaque_fraction <= 0.90:
        raise SystemExit(f"foreground coverage outside hardened bounds: {opaque_fraction:.6f}")

    red, green, blue = source_rgb.split()
    protected = Image.merge("RGBA", (red, green, blue, alpha))
    protected_rgb = np.asarray(protected.convert("RGB"), dtype=np.uint8)
    source_array = np.asarray(source_rgb, dtype=np.uint8)
    if not np.array_equal(protected_rgb, source_array):
        raise SystemExit("protected layer changed source RGB pixels")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    protected.save(args.output, format="PNG", optimize=True)

    receipt = {
        "schema": "skyyrose.protected-model-layer.v1",
        "source": str(args.source),
        "source_sha256": sha256(args.source),
        "output": str(args.output),
        "output_sha256": sha256(args.output),
        "dimensions": list(source_size),
        "alpha_extrema": [alpha_min, alpha_max],
        "opaque_fraction": round(opaque_fraction, 6),
        "model": "existing-alpha-mask" if args.alpha_source else args.model,
        "alpha_source": str(args.alpha_source) if args.alpha_source else None,
        "alpha_source_sha256": sha256(args.alpha_source) if args.alpha_source else None,
        "rgb_preserved": True,
    }
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    json.dump(receipt, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
