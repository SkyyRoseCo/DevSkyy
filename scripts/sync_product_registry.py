#!/usr/bin/env python3
"""Export compatibility catalog/dossiers and the asset manifest, or fail when they differ from the SOT."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import build_asset_manifest as manifest_builder  # noqa: E402
from skyyrose.core import asset_manifest, product_registry  # noqa: E402
from skyyrose.core.product_registry import export_compatibility, orphan_dossiers  # noqa: E402


def _reconcile_asset_manifest(check: bool) -> list[str]:
    """Regenerate the asset manifest (or, with ``check``, only report it) when it drifted.

    The manifest pins the registry and every dossier by sha256, so any registry edit
    makes it stale by construction. It is a projection of the registry like the CSV and
    dossiers, and therefore belongs to the same sync/--check that CI and the
    catalog-drift hook already run. Must run after ``export_compatibility``: it hashes
    the dossiers that step writes.
    """
    # The manifest tracks the canonical registry only; syncing any other registry (a
    # test fixture, an ad-hoc copy) must never rewrite the real manifest.
    if manifest_builder.PRODUCT_REGISTRY != product_registry.PRODUCT_REGISTRY:
        return []
    fresh = manifest_builder.build()
    try:
        committed = asset_manifest.AssetManifest.load().to_payload()
    except ValueError:
        committed = None  # unreadable counts as drift; regenerating is the documented remedy
    payload = fresh.to_payload()
    if committed is not None:
        # generated_at is a timestamp, not content: it must not make every sync a diff.
        committed.pop("generated_at", None)
        payload.pop("generated_at", None)
        if committed == payload:
            return []
    if not check:
        fresh.save()
    return [str(asset_manifest.MANIFEST_PATH)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Read-only freshness check")
    args = parser.parse_args()
    drift = export_compatibility(check=args.check)
    # Orphans are never rewritten or removed by a sync: bind them in the
    # registry or retire them deliberately, so they fail both modes.
    orphans = {str(path) for path in orphan_dossiers()}
    drift.extend(_reconcile_asset_manifest(args.check))
    for path in drift:
        if path in orphans:
            print(f"ORPHAN {path}  (dossier not owned by any registry product)")
        else:
            print(("STALE " if args.check else "UPDATED ") + path)
    if not drift:
        print("PASS: CSV, all product dossiers and the asset manifest match the registry")
    return int(bool(orphans) or (args.check and bool(drift)))


if __name__ == "__main__":
    raise SystemExit(main())
