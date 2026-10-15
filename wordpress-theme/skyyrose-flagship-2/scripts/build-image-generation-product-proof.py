#!/usr/bin/env python3
"""Build a hash-bound product-proof board before any image-model prompt is authored."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[3]
THEME_DIR = Path(__file__).resolve().parent.parent
PRODUCT_SOT = ROOT / "data/product-sot.json"
OUTPUT_DIR = (
    THEME_DIR / "assets/scroll-world/generated-candidates/founder-commerce-scenes-v1/preflight-v1"
)
BOARD = OUTPUT_DIR / "product-proof-board-v1.png"
MANIFEST = OUTPUT_DIR / "product-proof-manifest-v1.json"

PROOF_ITEMS = (
    (
        "BR-005 / physical hoodie",
        ("br-005",),
        "assets/products/source-photos/black-rose/br-005-signature-edition-hoodie.jpeg",
    ),
    (
        "BR-007 / founder front + left side",
        ("br-007",),
        "assets/products/source-photos/black-rose/br-007-shorts-front.jpeg",
    ),
    (
        "BR-007 / founder back",
        ("br-007",),
        "assets/products/source-photos/black-rose/br-007-shorts-back-detail.jpeg",
    ),
    (
        "LH-004 / physical satin bomber",
        ("lh-004",),
        "assets/products/source-photos/love-hurts/lh-004-bomber-front.jpg",
    ),
    (
        "LH-002 / physical black jogger",
        ("lh-002",),
        "assets/products/source-photos/love-hurts/lh-004-joggers-black.jpeg",
    ),
    (
        "LH-006 / physical white jogger",
        ("lh-006",),
        "assets/products/source-photos/love-hurts/lh-002-joggers-white.jpeg",
    ),
    (
        "LH-002 + LH-006 / exact thigh logo",
        ("lh-002", "lh-006"),
        "wordpress-theme/skyyrose-flagship/assets/images/logos/heart-rose-composite.jpeg",
    ),
    (
        "SG-001 / physical Bay Bridge shorts",
        ("sg-001",),
        "assets/products/source-photos/signature/sg-001-bay-bridge-shorts-front-authentic.png",
    ),
    (
        "SG-005 / physical Bay Bridge shirt",
        ("sg-005",),
        "assets/products/source-photos/signature/sg-005-bay-bridge-shirt-front-authentic.jpg",
    ),
)


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


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in (
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    ):
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def main() -> int:
    product_sot = load_json(PRODUCT_SOT)
    products = product_sot["products"]
    product_sot_hash = sha256(PRODUCT_SOT)
    records: list[dict[str, Any]] = []

    for label, skus, relative in PROOF_ITEMS:
        source = ROOT / relative
        require(source.is_file(), f"proof source missing: {relative}")
        source_hash = sha256(source)
        for sku in skus:
            require(sku in products, f"proof SKU missing from product SOT: {sku}")
            reference_hashes = {item["sha256"] for item in products[sku]["references"]}
            require(
                source_hash in reference_hashes,
                f"{sku} proof source is not hash-bound in its canonical reference stack: {relative}",
            )
        records.append(
            {
                "label": label,
                "skus": list(skus),
                "source": relative,
                "sha256": source_hash,
                "product_hashes": {sku: products[sku]["product_hash"] for sku in skus},
            }
        )

    tile_width, tile_height = 600, 540
    label_height = 58
    board = Image.new("RGB", (tile_width * 3, tile_height * 3 + 72), "#080808")
    draw = ImageDraw.Draw(board)
    draw.rectangle((0, 0, board.width, 72), fill="#721226")
    draw.text(
        (24, 21),
        "PRE-GENERATION PRODUCT PROOF — FOUNDER PHOTOS / TECHNICAL LOGO TRUTH",
        fill="white",
        font=font(26),
    )
    for index, record in enumerate(records):
        left = (index % 3) * tile_width
        top = 72 + (index // 3) * tile_height
        draw.rectangle((left, top, left + tile_width, top + tile_height), fill="#111111")
        draw.text((left + 16, top + 16), record["label"], fill="white", font=font(21))
        with Image.open(ROOT / record["source"]) as source_image:
            proof = ImageOps.exif_transpose(source_image).convert("RGB")
            proof.thumbnail(
                (tile_width - 32, tile_height - label_height - 26), Image.Resampling.LANCZOS
            )
            x = left + (tile_width - proof.width) // 2
            y = top + label_height + (tile_height - label_height - proof.height) // 2
            board.paste(proof, (x, y))
        draw.rectangle(
            (left, top, left + tile_width - 1, top + tile_height - 1), outline="#3b3b3b", width=2
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    board.save(BOARD, optimize=True)
    manifest = {
        "schema": "skyyrose.image-generation-product-proof.v1",
        "stage": "BEFORE_PROMPT_AUTHORING",
        "approval_state": "INPUT_EVIDENCE_ONLY_NOT_GENERATED",
        "product_sot": {
            "file": str(PRODUCT_SOT.relative_to(ROOT)),
            "sha256": product_sot_hash,
        },
        "items": records,
        "board": {
            "file": str(BOARD.relative_to(THEME_DIR)),
            "sha256": sha256(BOARD),
            "dimensions": list(board.size),
        },
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(
        f"PASS pre-prompt product proof: {len(records)} evidence panels, "
        f"{len({sku for record in records for sku in record['skus']})} SKUs, hash-bound to product SOT"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
