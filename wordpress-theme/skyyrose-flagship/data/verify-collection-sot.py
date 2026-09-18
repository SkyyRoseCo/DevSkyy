#!/usr/bin/env python3
"""Verify the generated SOT + tokens against canon and reality. Exit 0 clean, 1 on hard fail.

Per collection asserts: catalog SKU coverage; every declared resolved path is a real file;
every identity font woff2 resolves; the generated design-tokens region matches a fresh
generation (staleness gate); broken catalog product refs are reported (non-fatal).

The staleness gate regenerates design-tokens.css to compare, then restores the original
bytes on mismatch — so verify never leaves a net change in the working tree.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

DATA = Path(__file__).resolve().parent
sys.path.insert(0, str(DATA))
sys.path.insert(0, str(DATA.parents[2]))
import sot_common  # noqa: E402

from skyyrose.core.catalog_loader import read_catalog_rows  # noqa: E402

OUT = DATA / "collections"
# CSS path is overridable via SKYYROSE_TOKENS_CSS so the staleness gate can run
# against a private tmp copy in tests (hermetic isolation). The gen subprocess
# this script spawns inherits the env, so both halves of the gate use the same
# file. Unset -> the real theme file.
_CSS_OVERRIDE = os.environ.get("SKYYROSE_TOKENS_CSS")
CSS = Path(_CSS_OVERRIDE) if _CSS_OVERRIDE else DATA.parent / "assets/css/design-tokens.css"
HERO_MIN_WIDTH = 2560  # MJ masters target; interim files are < 2560 (warn, not fail)


def catalog_skus() -> dict[str, set]:
    by: dict[str, set] = {}
    for row in read_catalog_rows():
        by.setdefault(row["collection"], set()).add(row["sku"])
    return by


def walk_resolved(obj: Any, slug: str, hard: list) -> None:
    if isinstance(obj, dict):
        p, r = obj.get("path"), obj.get("resolved")
        if p and "resolved" in obj and (not r or not (sot_common.ASSETS / r).is_file()):
            hard.append(f"{slug}: declared path does not resolve: {p}")
        for v in obj.values():
            walk_resolved(v, slug, hard)
    elif isinstance(obj, list):
        for v in obj:
            walk_resolved(v, slug, hard)


def _hero_pixel_width(resolved: str) -> int | None:
    """Return the pixel width of a resolved asset path, or None if unreadable."""
    abs_path = sot_common.ASSETS / resolved
    try:
        r = subprocess.run(
            ["identify", "-format", "%w", str(abs_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if r.returncode == 0 and r.stdout.strip().isdigit():
            return int(r.stdout.strip())
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def main() -> int:
    idents = sot_common.load_identity()  # raises IdentityError on bad canon
    cat = catalog_skus()
    hard, warn = [], []

    before = CSS.read_text()
    subprocess.run([sys.executable, str(DATA / "gen-design-tokens.py")], check=True)
    if CSS.read_text() != before:
        CSS.write_text(before)  # verify is net read-only: undo the regen, just report staleness
        hard.append(
            "design-tokens.css collection region is STALE — run gen-design-tokens.py and commit"
        )

    for slug, ident in idents.items():
        fp = OUT / slug / "sot.json"
        if not fp.is_file():
            hard.append(f"{slug}: sot.json missing")
            continue
        sot = json.loads(fp.read_text())
        sot_skus = {p["sku"] for p in sot.get("products", [])}
        expected = cat.get(slug, set())
        if miss := expected - sot_skus:
            hard.append(f"{slug}: catalog SKUs missing from SOT: {sorted(miss)}")
        if extra := sot_skus - expected:
            hard.append(f"{slug}: SOT SKUs not in catalog: {sorted(extra)}")
        for role, font in ident["fonts"].items():
            w = font["woff2"]
            if w and not sot_common.resolve_asset(w):
                hard.append(f"{slug}: font {role} woff2 missing: {w}")
        walk_resolved(sot.get("lockup", {}), slug, hard)
        walk_resolved(sot.get("imagery", {}), slug, hard)
        walk_resolved(sot.get("logos", []), slug, hard)
        # Hero slot check: must exist and resolve to a real file.
        hero = (sot.get("imagery") or {}).get("hero")
        if not hero or not hero.get("path"):
            hard.append(
                f"{slug}: imagery.hero slot missing — add to logo-registry.json collections.{slug}"
            )
        else:
            h_resolved = hero.get("resolved")
            if not h_resolved or not (sot_common.ASSETS / h_resolved).is_file():
                hard.append(
                    f"{slug}: imagery.hero declared path does not resolve: {hero.get('path')}"
                )
            else:
                w = _hero_pixel_width(h_resolved)
                if w is not None and w < HERO_MIN_WIDTH:
                    warn.append(
                        f"{slug}: imagery.hero width {w}px < {HERO_MIN_WIDTH}px"
                        f" ({h_resolved}) — interim master; MJ hero pending"
                    )
                print(
                    f"  hero: {h_resolved}"
                    + (f" ({w}px wide)" if w is not None else "")
                    + (" [interim]" if (hero.get("status") or "").startswith("interim") else "")
                )
        for u in sot.get("unresolved_product_images", []):
            warn.append(f"{slug}: {u['sku']} {u['column']} -> {u['path']} (missing file)")
        print(
            f"{slug}: {len(sot_skus)}/{len(expected)} SKUs, "
            f"{len(sot.get('unresolved_product_images', []))} broken product refs"
        )

    if warn:
        print("\nWARNINGS:")
        for w in warn:
            print("  ⚠ " + w)
    if hard:
        print("\nHARD FAILURES:")
        for h in hard:
            print("  ✗ " + h)
        return 1
    print("\n✓ all per-collection SOT files + tokens verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
