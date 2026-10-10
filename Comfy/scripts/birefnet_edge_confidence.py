#!/usr/bin/env python3
"""Create hash-bound BiRefNet alpha and edge-confidence evidence.

The metrics in this receipt describe a mask; they do not approve product
fidelity, edge quality, or a final composite. Independent visual review stays
mandatory, and this module never modifies protected RGB pixels.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
from pathlib import Path
from typing import Any

from PIL import Image, UnidentifiedImageError

RECEIPT_SCHEMA = "skyyrose.birefnet-edge-confidence/1"
BIREFNET_MODEL_SHA256 = "9ab37426bf4de0567af6b5d21b16151357149139362e6e8992021b8ce356a154"
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class EdgeConfidenceError(ValueError):
    """Raised when mask evidence cannot be bound safely."""


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _require_sha256(value: str, *, field: str) -> str:
    normalized = value.strip().lower()
    if SHA256_PATTERN.fullmatch(normalized) is None:
        raise EdgeConfidenceError(f"{field} must be a lowercase SHA-256 digest")
    return normalized


def analyze_birefnet_mask(
    mask_bytes: bytes,
    *,
    source_sha256: str,
    model_sha256: str = BIREFNET_MODEL_SHA256,
) -> dict[str, Any]:
    """Return descriptive alpha metrics bound to source, model, and mask hashes."""
    source_hash = _require_sha256(source_sha256, field="source_sha256")
    model_hash = _require_sha256(model_sha256, field="model_sha256")
    if not mask_bytes:
        raise EdgeConfidenceError("mask is empty")
    try:
        with Image.open(io.BytesIO(mask_bytes)) as opened:
            if "A" in opened.getbands():
                mask = opened.getchannel("A")
                mode_analyzed = "A"
            else:
                mask = opened.convert("L")
                mode_analyzed = "L"
            mask.load()
    except (OSError, UnidentifiedImageError) as exc:
        raise EdgeConfidenceError(f"mask is not a readable image: {exc}") from exc

    width, height = mask.size
    if width <= 0 or height <= 0:
        raise EdgeConfidenceError("mask dimensions must be positive")
    pixels = list(mask.get_flattened_data())
    total = len(pixels)
    transparent = sum(alpha == 0 for alpha in pixels)
    opaque = sum(alpha == 255 for alpha in pixels)
    transition_values = [alpha for alpha in pixels if 0 < alpha < 255]
    ambiguous = sum(64 <= alpha <= 191 for alpha in transition_values)
    foreground = sum(alpha > 0 for alpha in pixels)
    all_pixel_binary_confidence = sum(abs(alpha - 127.5) / 127.5 for alpha in pixels) / total
    transition_binary_confidence = (
        sum(abs(alpha - 127.5) / 127.5 for alpha in transition_values) / len(transition_values)
        if transition_values
        else 1.0
    )
    degenerate = transparent == total or opaque == total

    return {
        "schema": RECEIPT_SCHEMA,
        "status": "BLOCKED_DEGENERATE_MASK" if degenerate else "EVIDENCE_RECORDED_REVIEW_REQUIRED",
        "extraction_role": "ALPHA_AND_EDGE_CONFIDENCE_ONLY",
        "source_sha256": source_hash,
        "model": {
            "name": "BiRefNet",
            "sha256": model_hash,
        },
        "mask": {
            "sha256": _sha256_bytes(mask_bytes),
            "width": width,
            "height": height,
            "mode_analyzed": mode_analyzed,
        },
        "metrics": {
            "foreground_ratio": round(foreground / total, 8),
            "transparent_ratio": round(transparent / total, 8),
            "opaque_ratio": round(opaque / total, 8),
            "transition_ratio": round(len(transition_values) / total, 8),
            "ambiguous_transition_ratio": round(ambiguous / total, 8),
            "all_pixel_binary_confidence": round(all_pixel_binary_confidence, 8),
            "transition_binary_confidence": round(transition_binary_confidence, 8),
        },
        "protected_rgb_modified": False,
        "generative_use_allowed": False,
        "quality_decision": "UNDETERMINED",
        "independent_visual_review_required": True,
        "notes": [
            "Metrics describe alpha certainty only and are not product-fidelity approval.",
            "Protected customer, identity, garment, artwork, zipper, pocket, and sculpture RGB must remain byte-identical.",
        ],
    }


def write_receipt_exclusive(path: Path, receipt: dict[str, Any]) -> None:
    """Create a new receipt without replacing prior evidence."""
    destination = path.expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with destination.open("x", encoding="utf-8") as handle:
            json.dump(receipt, handle, indent=2)
            handle.write("\n")
    except FileExistsError as exc:
        raise EdgeConfidenceError(f"receipt already exists: {destination}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mask", type=Path, required=True)
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--model-sha256", default=BIREFNET_MODEL_SHA256)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    try:
        receipt = analyze_birefnet_mask(
            args.mask.expanduser().read_bytes(),
            source_sha256=args.source_sha256,
            model_sha256=args.model_sha256,
        )
        if args.receipt is not None:
            write_receipt_exclusive(args.receipt, receipt)
    except (OSError, EdgeConfidenceError) as exc:
        print(json.dumps({"schema": RECEIPT_SCHEMA, "status": "BLOCKED", "error": str(exc)}))
        return 2
    print(json.dumps(receipt, indent=2))
    return 0 if receipt["status"] == "EVIDENCE_RECORDED_REVIEW_REQUIRED" else 2


if __name__ == "__main__":
    sys.exit(main())
