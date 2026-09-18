#!/usr/bin/env python3
"""Export compatibility catalog/dossiers, or fail when they differ from the SOT."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skyyrose.core.product_registry import export_compatibility, orphan_dossiers  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Read-only freshness check")
    args = parser.parse_args()
    drift = export_compatibility(check=args.check)
    # Orphans are never rewritten or removed by a sync: bind them in the
    # registry or retire them deliberately, so they fail both modes.
    orphans = {str(path) for path in orphan_dossiers()}
    for path in drift:
        if path in orphans:
            print(f"ORPHAN {path}  (dossier not owned by any registry product)")
        else:
            print(("STALE " if args.check else "UPDATED ") + path)
    if not drift:
        print("PASS: CSV and all product dossiers match the registry")
    return int(bool(orphans) or (args.check and bool(drift)))


if __name__ == "__main__":
    raise SystemExit(main())
