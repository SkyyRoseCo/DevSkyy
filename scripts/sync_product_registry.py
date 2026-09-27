#!/usr/bin/env python3
"""Export compatibility catalog/dossiers, or fail when they differ from the SOT."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skyyrose.core.product_registry import export_compatibility  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Read-only freshness check")
    args = parser.parse_args()
    drift = export_compatibility(check=args.check)
    for path in drift:
        print(("STALE " if args.check else "UPDATED ") + path)
    if not drift:
        print("PASS: CSV and all product dossiers match the registry")
    return int(args.check and bool(drift))


if __name__ == "__main__":
    raise SystemExit(main())
