"""Load the canonical product catalog CSV (SOT — see repo-root SOT.md).

Used to look up canonical facts WooCommerce doesn't reliably carry itself,
e.g. `is_preorder`, which drives the availability mapping in mapping.py.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from skyyrose.core.catalog_loader import CATALOG_CSV, read_catalog_rows

DEFAULT_CATALOG_PATH = CATALOG_CSV


def load_catalog(path: Path = DEFAULT_CATALOG_PATH) -> dict[str, dict[str, Any]]:
    """Return {sku: row_dict} for every row in the catalog CSV."""
    if path.resolve() != DEFAULT_CATALOG_PATH.resolve() and not path.exists():
        raise FileNotFoundError(f"Canonical catalog CSV not found at {path} (see SOT.md)")
    return {
        sku: dict(row) for row in read_catalog_rows(path) if (sku := row.get("sku", "").strip())
    }
