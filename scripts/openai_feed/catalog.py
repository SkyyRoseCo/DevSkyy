"""Load the canonical product catalog CSV (SOT — see repo-root SOT.md).

Used to look up canonical facts WooCommerce doesn't reliably carry itself,
e.g. `is_preorder`, which drives the availability mapping in mapping.py.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from skyyrose.core.catalog_loader import read_catalog_rows

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG_PATH = (
    REPO_ROOT / "wordpress-theme" / "skyyrose-flagship" / "data" / "skyyrose-catalog.csv"
)


def load_catalog(path: Path = DEFAULT_CATALOG_PATH) -> dict[str, dict[str, Any]]:
    """Return {sku: row_dict} for every row in the catalog CSV."""
    if path.resolve() != DEFAULT_CATALOG_PATH.resolve() and not path.exists():
        raise FileNotFoundError(f"Canonical catalog CSV not found at {path} (see SOT.md)")
    return {
        sku: dict(row) for row in read_catalog_rows(path) if (sku := row.get("sku", "").strip())
    }
