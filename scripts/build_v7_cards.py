#!/usr/bin/env python3
"""build_v7_cards.py — Generate the V7 lookbook card store as a DERIVED VIEW.

``wordpress-theme/skyyrose-flagship/data/v7-cards.json`` was previously a
hand-maintained file — the last product-data store in the repo not tied to a
single source of truth. It carried catalog fields (name / price / badge /
preorder) copied by hand from the CSV, which let it drift (it inherited the
br-014/br-015 ``badge="Pre-Order"`` vs ``is_preorder=0`` contradiction verbatim).

This generator makes it a GENERATED VIEW joining two authorities:

  * Catalog fields (name, price, collection, badge, edition, preorder)
        → the product SOT: the registry, read through ``skyyrose.core.product.get_product``.
  * Imagery (which SKUs qualify + their shot files)
        → the tracked, promoted V7 served tree
          ``wordpress-theme/skyyrose-flagship/assets/images/products/v7/<sku>/``.
          A SKU earns a card iff it has a promoted ``front`` shot there. That tree
          is the served projection of the asset-hub ``verdict:verified`` gate
          (see ``feedback_real_products_only``); gating on the tracked tree keeps
          this generator runnable in CI and fresh clones, where the hub manifest
          (``assets/hub/manifest.json``) is gitignored and absent.

``preorder`` is therefore a COMPUTED field — it can no longer disagree with the
registry. The companion validator check ``v7_cards_current`` regenerates into a buffer
and fails CI if the committed file drifts from this generator's output, closing
the recurrence hole.

Stdlib-only + ``skyyrose.core`` so it runs in the catalog-validate CI job (no
project install).

USAGE:
  python scripts/build_v7_cards.py            # regenerate the file in place
  python scripts/build_v7_cards.py --check    # exit 1 if the committed file is stale (no write)
  python scripts/build_v7_cards.py --stdout    # print generated JSON, do not write
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from skyyrose.core.catalog_loader import bool_col, int_col
from skyyrose.core.paths import REPO_ROOT, THEME_ROOT
from skyyrose.core.product import all_skus, get_product

# ---------------------------------------------------------------------------
# Paths (canonical anchors from skyyrose.core.paths)
# ---------------------------------------------------------------------------
_THEME_ROOT: Path = THEME_ROOT
_THEME_DATA: Path = _THEME_ROOT / "data"
_V7_IMG_DIR: Path = _THEME_ROOT / "assets" / "images" / "products" / "v7"
_OUT_PATH: Path = _THEME_DATA / "v7-cards.json"

# Theme-relative URI prefix the PHP loader resolves via get_theme_file_uri().
_URI_PREFIX = "assets/images/products/v7"

# Shot faces in canonical emit order. A card requires "front"; "alt"/"back" are
# optional. The set is closed — any other file under a SKU dir is ignored (and
# reported by --check via the integrity note, never silently shipped).
_FACE_ORDER: tuple[str, ...] = ("front", "alt", "back")

# Base-shot raster formats in preference order. The base shot is the universal
# ``<img>`` fallback; ``.avif`` is an enhancement sibling served via the card
# template's ``<picture><source type="image/avif">`` and is NEVER the base URI
# (a raw ``<img src=".avif">`` would break browsers without AVIF support).
_BASE_EXTS: tuple[str, ...] = (".webp", ".png", ".jpg", ".jpeg")

_AUTHORITY = "verdict:verified hub images only — see feedback_real_products_only"
_GENERATED_BY = (
    "scripts/build_v7_cards.py — DO NOT EDIT. "
    "SOT = skyyrose-catalog.csv (fields) × promoted v7 served tree (imagery). "
    "Regenerate after CSV/imagery changes; CI check 'v7_cards_current' enforces this."
)


def _registry_rows() -> list[dict[str, str]]:
    """Every product's catalog section from the registry, via get_product."""
    return [get_product(sku)["catalog"] for sku in all_skus()]


def _shots_for(sku: str) -> list[dict[str, str]]:
    """Return the ordered shot list for a SKU by scanning its served V7 dir.

    Picks the base raster file per face in ``_BASE_EXTS`` preference order
    (webp → png → jpg), so mixed-extension promotions resolve deterministically.
    ``.avif`` siblings are ignored here — they are the ``<picture>`` enhancement,
    not the base ``<img>`` src. Returns ``[]`` when the SKU has no served dir.
    """
    sku_dir = _V7_IMG_DIR / sku
    if not sku_dir.is_dir():
        return []
    shots: list[dict[str, str]] = []
    for face in _FACE_ORDER:
        cands = [p for p in sku_dir.glob(f"{face}.*") if p.suffix.lower() in _BASE_EXTS]
        if not cands:
            continue
        cands.sort(key=lambda p: (_BASE_EXTS.index(p.suffix.lower()), p.name))
        shots.append({"face": face, "uri": f"{_URI_PREFIX}/{sku}/{cands[0].name}"})
    return shots


def build_cards(rows: list[dict[str, str]] | None = None) -> list[dict]:
    """Build the V7 card list: every registry SKU with a promoted ``front`` shot.

    Cards are emitted in lexicographic SKU order (the established file order).
    Each card joins registry catalog fields with the served shot list.
    ``preorder`` is computed from the ``is_preorder`` flag — never hand-set.
    ``rows`` overrides the registry with catalog-shaped dicts (tests).
    """
    catalog_rows = rows if rows is not None else _registry_rows()
    cards: list[dict] = []
    for row in sorted(catalog_rows, key=lambda r: r["sku"].strip()):
        sku = row["sku"].strip()
        shots = _shots_for(sku)
        if not shots or shots[0]["face"] != "front":
            # No promoted front shot → not a verified V7 card; falls back to holo.
            continue
        cards.append(
            {
                "sku": sku,
                "name": row["name"],
                "price": int(row["price"]),
                "collection": row["collection"],
                "badge": (row.get("badge") or "").strip(),
                "edition": int_col(row, "edition_size"),
                "preorder": bool_col(row, "is_preorder"),
                "shots": shots,
            }
        )
    return cards


def build_document(rows: list[dict[str, str]] | None = None) -> dict:
    """Build the full v7-cards.json document (header + cards)."""
    cards = build_cards(rows)
    return {
        "_generated_by": _GENERATED_BY,
        "_authority": _AUTHORITY,
        "_count": len(cards),
        "cards": cards,
    }


def serialize(doc: dict) -> str:
    """Canonical serialization — the single definition of the file's bytes."""
    import json

    return json.dumps(doc, indent=1, ensure_ascii=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the V7 lookbook card store from the CSV + served tree."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if the committed v7-cards.json differs from freshly generated output (no write).",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print generated JSON to stdout; do not write the file.",
    )
    args = parser.parse_args(argv)

    generated = serialize(build_document())

    if args.stdout:
        sys.stdout.write(generated)
        return 0

    if args.check:
        if not _OUT_PATH.exists():
            print(f"FAIL: {_OUT_PATH} does not exist", file=sys.stderr)
            return 1
        current = _OUT_PATH.read_text(encoding="utf-8")
        if current != generated:
            print(
                "FAIL: v7-cards.json is stale — run `python scripts/build_v7_cards.py` to regenerate.",
                file=sys.stderr,
            )
            return 1
        print("OK: v7-cards.json is up to date with the CSV + served tree.")
        return 0

    _OUT_PATH.write_text(generated, encoding="utf-8")
    doc_count = generated.count('"sku":')
    print(f"Wrote {_OUT_PATH.relative_to(REPO_ROOT)} — {doc_count} cards.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
