#!/usr/bin/env python3
"""Read-only permission gate for package-boundary-approved V2 public assets.

No chmod, image decoding, network access, or private/nonrelease asset inspection.
"""

from __future__ import annotations

import argparse
import json
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_SUFFIXES = frozenset(
    {
        ".css",
        ".js",
        ".mjs",
        ".json",
        ".webp",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".svg",
        ".ico",
        ".mp4",
        ".webm",
        ".woff",
        ".woff2",
        ".ttf",
        ".otf",
        ".eot",
        ".glb",
        ".wasm",
        ".txt",
        ".md",
    }
)
PUBLIC_FILENAMES = frozenset({"LICENSE", "SHA256SUMS"})


def check_permissions(theme: Path, boundary: Path) -> int:
    """Fail closed on unsafe declared public paths or inaccessible publication."""
    files = json.loads(boundary.read_text(encoding="utf-8"))["files"]
    if not isinstance(files, dict):
        raise ValueError("Package boundary files must be an object")
    published = []
    for relative, record in files.items():
        if not isinstance(record, dict):
            raise ValueError("Invalid package boundary record")
        if record.get("release") is not True or not relative.startswith("assets/"):
            continue
        parts = Path(relative).parts
        if ".." in parts or any(part.startswith(".") for part in parts) or "\\" in relative:
            raise ValueError(f"Unsafe public asset path: {relative}")
        if (
            Path(relative).suffix.lower() not in PUBLIC_SUFFIXES
            and Path(relative).name not in PUBLIC_FILENAMES
        ):
            raise ValueError(f"Unsupported public asset type: {relative}")
        published.append(relative)
    if not published:
        raise ValueError("Package boundary declares no releasable public assets")
    if theme.is_symlink() or not theme.is_dir():
        raise ValueError("Theme must be an existing nonsymlink directory")
    if stat.S_IMODE(theme.stat().st_mode) != 0o755:
        raise ValueError("Public theme directory requires 0755")
    checked_directories = {}
    failures = []
    for relative in sorted(published):
        target = theme / relative
        parent = theme
        unsafe_parent = False
        for part in Path(relative).parts[:-1]:
            parent = parent / part
            if parent in checked_directories:
                if not checked_directories[parent]:
                    unsafe_parent = True
                    break
                continue
            if parent.is_symlink() or not parent.is_dir():
                checked_directories[parent] = False
                failures.append(f"Unsafe/missing public directory: {parent.relative_to(theme)}")
                unsafe_parent = True
                break
            checked_directories[parent] = True
            if stat.S_IMODE(parent.stat().st_mode) != 0o755:
                failures.append(f"Public directory requires 0755: {parent.relative_to(theme)}")
        if unsafe_parent:
            continue
        if target.is_symlink() or not target.is_file():
            failures.append(f"Unsafe/missing public file: {relative}")
        elif stat.S_IMODE(target.stat().st_mode) != 0o644:
            failures.append(f"Public file requires 0644: {relative}")
    if failures:
        raise ValueError(
            f"{len(failures)} public permission/path failure(s):\n" + "\n".join(failures[:12])
        )
    return len(published)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--theme-dir", type=Path, default=ROOT / "wordpress-theme/skyyrose-flagship-2"
    )
    parser.add_argument(
        "--boundary",
        type=Path,
        default=ROOT / "tools/v2-source-certification/package-boundary.json",
    )
    args = parser.parse_args()
    try:
        count = check_permissions(args.theme_dir, args.boundary)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Public release permission check failed: {error}", file=sys.stderr)
        return 1
    print(
        f"Verified permissions of {count} releasable public assets (0644 files, 0755 directories)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
