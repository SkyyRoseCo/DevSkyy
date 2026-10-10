#!/usr/bin/env python3
"""Add a new source product photo to the canonical photography directory.

Validates the upload (resolution, format, single subject), optionally runs
BRIA RMBG 2.0 to verify a clean matte is achievable, writes the file to the
canonical path, and refreshes the manifest.

Usage:
  python scripts/source_product_photos.py --sku br-001 --angle front \\
      --image /path/to/upload.jpg

Exit:
  0 success
  1 validation failure or write error
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from skyyrose.core.catalog_loader import read_catalog_rows  # noqa: E402

CANONICAL_DIR = ROOT / "assets" / "products" / "source-photos"

_MIN_DIM = 2048
_VALID_ANGLES = {
    "front",
    "back",
    # Always wearer-relative: "wearer-left" is the customer's left side when worn.
    "wearer-left",
    "wearer-right",
    "three-quarter",
    "detail-graphic",
    "detail-hood",
    "detail-pocket",
    "detail-patch",
    "detail-stitching",
    "combined-front",
    "top-only",
    "bottom-only",
    "in-context",
    "techflat",
}


def _validate_image(path: Path) -> str | None:
    if not path.is_file():
        return f"file not found: {path}"
    if path.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
        return f"unsupported format: {path.suffix} (require jpg/png/webp)"
    try:
        from PIL import Image
    except ImportError:
        return "Pillow not installed; cannot validate dimensions"
    try:
        with Image.open(path) as img:
            short = min(img.size)
            if short < _MIN_DIM:
                return (
                    f"image too small ({img.size[0]}x{img.size[1]}); "
                    f"shortest side must be ≥{_MIN_DIM}px"
                )
    except Exception as exc:
        return f"could not read image: {exc}"
    return None


def _try_bria_matte(path: Path) -> str | None:
    """Optional sanity check — run BRIA matte and verify the alpha is non-trivial.

    Returns None on success or skip; an error string on a clearly-broken matte
    (which usually means the photo isn't isolating the subject cleanly enough
    for the compositor's Stage 1).
    """
    try:
        from PIL import Image
        from rembg import remove  # type: ignore[import-not-found]
    except ImportError:
        return None  # Skip — environment lacks rembg
    try:
        with open(path, "rb") as f:
            result = remove(f.read())
        if isinstance(result, bytes):
            from io import BytesIO

            img = Image.open(BytesIO(result)).convert("RGBA")
        else:
            img = result.convert("RGBA")
        alpha = img.split()[-1]
        non_zero = sum(1 for px in alpha.get_flattened_data() if px > 8)
        ratio = non_zero / (img.size[0] * img.size[1])
        if ratio < 0.05:
            return (
                f"matte produced near-empty alpha ({ratio:.2%} non-zero) — "
                "likely the photo background isn't separable. Recapture against "
                "white seamless or a transparent backdrop."
            )
        if ratio > 0.95:
            return (
                f"matte produced near-full alpha ({ratio:.2%} non-zero) — "
                "subject fills the frame. Reshoot with the subject occupying "
                "60-80% of the frame so the compositor has room to place it."
            )
        return None
    except Exception as exc:
        return f"BRIA matte check errored (non-blocking): {exc}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Add a source product photo")
    parser.add_argument("--sku", required=True)
    parser.add_argument(
        "--angle",
        required=True,
        choices=sorted(_VALID_ANGLES),
        help=(
            "view of the garment; directional sides are always wearer-relative "
            "(wearer-left/wearer-right)"
        ),
    )
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--no-matte-check", action="store_true", help="Skip BRIA matte sanity")
    parser.add_argument("--force", action="store_true", help="Skip overwrite confirmation")
    args = parser.parse_args()

    valid_skus = {row["sku"] for row in read_catalog_rows() if row.get("sku")}
    if args.sku not in valid_skus:
        print(f"✗ {args.sku} is not in the canonical catalog", file=sys.stderr)
        return 1

    err = _validate_image(args.image)
    if err:
        print(f"✗ {err}", file=sys.stderr)
        return 1

    # Try the matte check non-blockingly — print a warning, ask to proceed.
    if not args.no_matte_check:
        matte_err = _try_bria_matte(args.image)
        if matte_err:
            print(f"!  matte check: {matte_err}")
            if not args.force:
                ans = input("  proceed anyway? [y/N] ").strip().lower()
                if ans not in ("y", "yes"):
                    return 1

    dest_dir = CANONICAL_DIR
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{args.sku}-{args.angle}{args.image.suffix.lower()}"
    if dest.exists() and not args.force:
        if not _confirm(f"  overwrite existing {dest.name}?"):
            print("aborted")
            return 1
    shutil.copy2(args.image, dest)
    print(f"✓ wrote {dest.relative_to(ROOT)}")

    # Refresh manifest
    print("Refreshing manifest...")
    import subprocess

    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "audit_source_photos.py")],
        check=False,
    )
    return 0


def _confirm(prompt: str) -> bool:
    return input(f"{prompt} [y/N] ").strip().lower() in ("y", "yes")


if __name__ == "__main__":
    raise SystemExit(main())
