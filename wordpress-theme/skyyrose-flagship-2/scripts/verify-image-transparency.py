#!/usr/bin/env python3
"""Fail when a required compositing asset has no transparent pixels."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, UnidentifiedImageError


def has_transparency(path: Path) -> bool:
    with Image.open(path) as image:
        image.seek(0)
        rgba = image.convert("RGBA")
        alpha_minimum, _ = rgba.getchannel("A").getextrema()
        return alpha_minimum < 255


def main(paths: list[str]) -> int:
    for raw_path in paths:
        path = Path(raw_path)
        try:
            if not has_transparency(path):
                print(f"Brand asset has no transparent pixels: {path}", file=sys.stderr)
                return 1
        except (OSError, UnidentifiedImageError) as error:
            print(f"Unable to inspect brand asset {path}: {error}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
