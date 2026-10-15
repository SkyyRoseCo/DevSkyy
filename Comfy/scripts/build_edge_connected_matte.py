#!/usr/bin/env python3
"""Build an auditable alpha matte from an edge-connected near-white backdrop.

This tool is intentionally deterministic. It does not redraw, retouch, or infer
product pixels. Only near-white pixels connected to the image boundary are made
transparent; near-white regions enclosed by the product remain opaque.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from collections import deque
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def sha256_file(path: Path) -> str:
    """Return the lowercase SHA-256 digest for *path*."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def edge_connected_background(
    rgb: np.ndarray,
    *,
    minimum_channel: int = 238,
    maximum_chroma: int = 22,
) -> np.ndarray:
    """Return an 8-connected mask of qualifying background pixels.

    A pixel qualifies only when all channels are bright and its channel spread is
    low. Connectivity to an outer edge prevents internal white garment regions
    from being erased.
    """
    minimum = rgb.min(axis=2)
    chroma = rgb.max(axis=2) - minimum
    candidate = (minimum >= minimum_channel) & (chroma <= maximum_chroma)
    height, width = candidate.shape
    background = np.zeros((height, width), dtype=bool)
    queue: deque[tuple[int, int]] = deque()

    def seed(y: int, x: int) -> None:
        if candidate[y, x] and not background[y, x]:
            background[y, x] = True
            queue.append((y, x))

    for x in range(width):
        seed(0, x)
        seed(height - 1, x)
    for y in range(height):
        seed(y, 0)
        seed(y, width - 1)

    while queue:
        y, x = queue.popleft()
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if not (dx or dy):
                    continue
                ny, nx = y + dy, x + dx
                if (
                    0 <= ny < height
                    and 0 <= nx < width
                    and candidate[ny, nx]
                    and not background[ny, nx]
                ):
                    background[ny, nx] = True
                    queue.append((ny, nx))

    return background


def build_matte(
    source: Path,
    output: Path,
    proof: Path,
    receipt: Path,
    *,
    minimum_channel: int,
    maximum_chroma: int,
    role: str,
) -> dict[str, object]:
    """Create a protected RGBA asset, visual proof sheet, and JSON receipt."""
    destinations = (output, proof, receipt)
    existing = [path for path in destinations if path.exists()]
    if existing:
        raise FileExistsError(f"protected matte destination already exists: {existing[0]}")
    with Image.open(source) as opened:
        rgb_image = opened.convert("RGB")
    rgb = np.asarray(rgb_image, dtype=np.uint8)
    background = edge_connected_background(
        rgb,
        minimum_channel=minimum_channel,
        maximum_chroma=maximum_chroma,
    )
    alpha = np.where(background, 0, 255).astype(np.uint8)
    rgba = np.dstack((rgb, alpha))

    output_buffer = io.BytesIO()
    Image.fromarray(rgba, mode="RGBA").save(output_buffer, format="PNG", optimize=True)
    output_bytes = output_buffer.getvalue()

    checker = Image.new("RGB", rgb_image.size, "#d2d2d2")
    draw = ImageDraw.Draw(checker)
    tile = max(12, min(rgb_image.size) // 32)
    for y in range(0, checker.height, tile):
        for x in range(0, checker.width, tile):
            if ((x // tile) + (y // tile)) % 2:
                draw.rectangle((x, y, x + tile - 1, y + tile - 1), fill="#8d8d8d")
    protected = Image.fromarray(rgba, mode="RGBA")
    on_checker = Image.alpha_composite(checker.convert("RGBA"), protected).convert("RGB")
    on_black = Image.alpha_composite(Image.new("RGBA", rgb_image.size, "black"), protected).convert(
        "RGB"
    )
    on_white = Image.alpha_composite(Image.new("RGBA", rgb_image.size, "white"), protected).convert(
        "RGB"
    )
    proof_sheet = Image.new("RGB", (rgb_image.width * 3, rgb_image.height), "white")
    proof_sheet.paste(on_checker, (0, 0))
    proof_sheet.paste(on_black, (rgb_image.width, 0))
    proof_sheet.paste(on_white, (rgb_image.width * 2, 0))
    proof_buffer = io.BytesIO()
    proof_sheet.save(proof_buffer, format="PNG", optimize=True)
    proof_bytes = proof_buffer.getvalue()

    pixel_count = int(alpha.size)
    transparent_count = int(np.count_nonzero(alpha == 0))
    report: dict[str, object] = {
        "schema_version": "1.0",
        "operation": "EDGE_CONNECTED_NEAR_WHITE_ALPHA_EXTRACTION",
        "disposition": "PRODUCT_ONLY_MATTE_CANDIDATE",
        "role": role,
        "created_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "source": {
            "path": str(source.resolve()),
            "sha256": sha256_file(source),
            "width": rgb_image.width,
            "height": rgb_image.height,
        },
        "output": {
            "path": str(output.resolve()),
            "sha256": hashlib.sha256(output_bytes).hexdigest(),
            "mode": "RGBA",
            "rgb_policy": "SOURCE_RGB_PRESERVED_BYTE_FOR_BYTE_PER_PIXEL",
        },
        "proof": {
            "path": str(proof.resolve()),
            "sha256": hashlib.sha256(proof_bytes).hexdigest(),
            "views": ["checkerboard", "black", "white"],
        },
        "algorithm": {
            "connectivity": 8,
            "minimum_channel": minimum_channel,
            "maximum_chroma": maximum_chroma,
            "transparent_pixel_count": transparent_count,
            "transparent_fraction": round(transparent_count / pixel_count, 8),
            "opaque_pixel_count": pixel_count - transparent_count,
        },
        "guardrails": {
            "generative_operation": False,
            "on_model_authority": False,
            "promotion_authority": False,
            "allowed_use": "source inspection, protected product layout, and mask planning",
        },
    }
    receipt_bytes = (json.dumps(report, indent=2) + "\n").encode("utf-8")
    created: list[Path] = []
    try:
        for path, content in (
            (output, output_bytes),
            (proof, proof_bytes),
            (receipt, receipt_bytes),
        ):
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as handle:
                handle.write(content)
            created.append(path)
    except OSError:
        for path in reversed(created):
            path.unlink(missing_ok=True)
        raise
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--proof", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--role", required=True)
    parser.add_argument("--minimum-channel", type=int, default=238)
    parser.add_argument("--maximum-chroma", type=int, default=22)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.source.is_file():
        raise SystemExit(f"source does not exist: {args.source}")
    if not 0 <= args.minimum_channel <= 255:
        raise SystemExit("--minimum-channel must be between 0 and 255")
    if not 0 <= args.maximum_chroma <= 255:
        raise SystemExit("--maximum-chroma must be between 0 and 255")
    report = build_matte(
        args.source,
        args.output,
        args.proof,
        args.receipt,
        minimum_channel=args.minimum_channel,
        maximum_chroma=args.maximum_chroma,
        role=args.role,
    )
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
