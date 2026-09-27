"""Canonical catalog loader — shared by nano_banana and elite_studio.

Single import surface for:
    CATALOG_CSV        — Path to wordpress-theme/.../data/skyyrose-catalog.csv
    read_catalog_rows  — Registry-derived commerce rows (list[dict[str, str]])
    bool_col           — "1" / "0" → bool coercion
    int_col            — str → int | None, None if blank or <1
    status_from_row    — Derive pre-order / draft / live / retired from CSV flags
    PRODUCT_STATUS     — Valid status enum strings

Both nano_banana/catalog.py and skyyrose/elite_studio/catalog.py build
their higher-level types on top of this module. The PHP loader uses the
same canonical product registry but cannot share this code — keep the schema and
status-derivation rules documented in both places when they change.
"""

from __future__ import annotations

import csv
from pathlib import Path

from skyyrose.core.product_registry import catalog_rows

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CATALOG_CSV = (
    PROJECT_ROOT / "wordpress-theme" / "skyyrose-flagship" / "data" / "skyyrose-catalog.csv"
)

PRODUCT_STATUS = {"draft", "pre-order", "live", "retired"}


def read_catalog_rows(path: Path | None = None) -> list[dict[str, str]]:
    """Read registry commerce rows; explicit external CSVs are import fixtures.

    Both the root CSV symlink and the canonical compatibility CSV resolve to
    the registry. Fresh reads make founder edits visible without process restart.
    """
    if path is None or Path(path).resolve() == CATALOG_CSV.resolve():
        return catalog_rows()
    csv_path = path or CATALOG_CSV
    with csv_path.open(newline="", encoding="utf-8") as f:
        rows = []
        for row in csv.DictReader(f):
            sku = (row.get("sku") or "").strip()
            if not sku:
                continue
            rows.append(row)
        return rows


# Compatibility for callers that used to explicitly invalidate the CSV cache.
read_catalog_rows.cache_clear = lambda: None


def bool_col(row: dict, key: str) -> bool:
    """Read a CSV flag column ('1' → True, anything else → False)."""
    return (row.get(key) or "").strip() == "1"


def int_col(row: dict, key: str) -> int | None:
    """Read a positive-int column, returning None for blank or non-positive."""
    raw = (row.get(key) or "").strip()
    if not raw:
        return None
    try:
        value = int(raw)
    except ValueError:
        return None
    return value if value >= 1 else None


def get_product_with_dossier(sku: str) -> dict:
    """Return the registry commerce row for `sku` merged with its parsed dossier.

    Hard-fails (raises ``DossierMissingError``) if the SKU has no dossier.
    The thin CSV `branding_spec` column is NOT a fallback.

    Re-exports the canonical implementation from
    ``skyyrose.core.dossier_loader.get_product_with_dossier`` so consumers
    can import either module without divergence.
    """
    from skyyrose.core.dossier_loader import get_product_with_dossier as _get_product_with_dossier

    return _get_product_with_dossier(sku)


def status_from_row(row: dict) -> str:
    """Map the CSV badge/is_preorder/published triple to the legacy status enum.

    Rule order (first match wins):
      1. badge == 'retired' → 'retired'
      2. is_preorder == '1' → 'pre-order'
      3. badge == 'draft'   → 'draft'
      4. published == '1'   → 'live'
      5. fallback           → 'draft'
    """
    badge = (row.get("badge") or "").strip().lower()
    if badge == "retired":
        return "retired"
    if bool_col(row, "is_preorder"):
        return "pre-order"
    if badge == "draft":
        return "draft"
    if bool_col(row, "published"):
        return "live"
    return "draft"
