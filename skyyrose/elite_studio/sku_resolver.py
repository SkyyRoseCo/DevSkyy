"""
sku_resolver.py — SKU sanitization, catalog resolution, and Tripo region verification.

This module is the security gate for every downstream Phase 15 call.
All path construction that touches renders/{sku}-* MUST pass through sanitize_sku() first.

Design: standalone module with zero imports from other elite_studio modules.
Tripo client is lazy-imported inside verify_tripo_region() to avoid hard dep at module load.
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

# Derive paths relative to this file's location — do NOT hardcode absolute paths.
# skyyrose/elite_studio/sku_resolver.py  →  parents[0] = elite_studio/
#                                            parents[1] = skyyrose/
#                                            parents[2] = repo root
_REPO_ROOT: Path = Path(__file__).resolve().parents[2]

CATALOG_CSV_PATH: Path = (
    _REPO_ROOT / "wordpress-theme" / "skyyrose-flagship" / "data" / "skyyrose-catalog.csv"
)

BUNDLE_DIR: Path = _REPO_ROOT / "data" / "product-bundles"

_ACCESSORY_GARMENT_TYPE: str = "accessory"

# Jersey SKUs per D-10 (8 SKUs — br-003 + br-008..br-012 + br-014..br-015).
# br-013 retired 2026-05-25: confirmed duplicate of br-003 (Baseball Classic Black).
_JERSEY_SKUS: frozenset[str] = frozenset(
    {
        "br-003",
        "br-008",
        "br-009",
        "br-010",
        "br-011",
        "br-012",
        "br-014",
        "br-015",
    }
)

# Allow ONLY alphanumeric, hyphens, underscores — max 64 chars.
# This allowlist blocks all shell metacharacters (space, ;, |, $, `, etc.),
# path-separator characters, and unicode tricks.
_SKU_SAFE_RE: re.Pattern[str] = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ResolvedSKU:
    """Resolved product information for a valid, in-scope garment SKU."""

    sku: str
    """Sanitized SKU string."""

    name: str
    """Product name from the catalog CSV."""

    garment_type: str
    """garment_type_lock value from CSV col 21 (0-indexed)."""

    bundle_dir: Path
    """Absolute path to data/product-bundles/<dirname>/"""

    manifest_path: Path
    """Absolute path to the manifest.json within bundle_dir."""

    branding_spec: str
    """Branding spec free-text from CSV col 15 (0-indexed)."""

    is_jersey: bool
    """True if this SKU belongs to the jersey cascade tier (D-10)."""


# ---------------------------------------------------------------------------
# sanitize_sku
# ---------------------------------------------------------------------------


def sanitize_sku(raw: str) -> str:
    """Sanitize a raw --sku CLI argument against path-traversal and injection.

    Enforces:
    - Non-empty after stripping whitespace
    - No ".." sequences (path-traversal prevention)
    - No leading "/" or "\\" (absolute-path prevention)
    - Allowlist: only [a-zA-Z0-9_-], max 64 chars

    Args:
        raw: The unsanitized SKU string from CLI or caller.

    Returns:
        The stripped, validated SKU string.

    Raises:
        ValueError: If the SKU fails any safety check.
    """
    sku = raw.strip()

    if not sku:
        raise ValueError("SKU must not be empty")

    if ".." in sku:
        raise ValueError("SKU contains path-traversal sequence")

    if sku.startswith("/") or sku.startswith("\\"):
        raise ValueError("SKU must not be an absolute path")

    if not _SKU_SAFE_RE.match(sku):
        raise ValueError(f"SKU contains illegal characters: {raw!r}")

    return sku


# ---------------------------------------------------------------------------
# resolve_sku
# ---------------------------------------------------------------------------


def resolve_sku(
    raw_sku: str,
    catalog_path: Path | None = None,
    bundle_root: Path | None = None,
) -> ResolvedSKU | None:
    """Resolve a raw SKU against the product catalog.

    Sanitizes the input, finds the matching catalog row, and constructs the
    bundle directory and manifest path.  Accessories return None (silent skip
    per D-12/GM-06).  Unknown SKUs raise ValueError.

    Args:
        raw_sku: Unsanitized SKU string.
        catalog_path: Override catalog CSV path (defaults to CATALOG_CSV_PATH).
        bundle_root: Override product-bundles root (defaults to BUNDLE_DIR).

    Returns:
        ResolvedSKU dataclass for in-scope garments, or None for accessories.

    Raises:
        ValueError: If raw_sku fails sanitization or is not in the catalog.
    """
    sanitized_sku = sanitize_sku(raw_sku)

    effective_catalog = catalog_path or CATALOG_CSV_PATH
    effective_bundle_root = bundle_root or BUNDLE_DIR

    from skyyrose.core.catalog_loader import read_catalog_rows

    matching_row = next(
        (
            row
            for row in read_catalog_rows(effective_catalog)
            if row.get("sku", "").strip() == sanitized_sku
        ),
        None,
    )

    if matching_row is None:
        raise ValueError(f"SKU {sanitized_sku!r} not found in catalog")

    # Accessory gate — D-12 / GM-06: return None without raising so callers can
    # log the skip to failures.json without aborting the run.
    garment_type = matching_row.get("garment_type_lock", "").strip()
    render_is_accessory = matching_row.get("render_is_accessory", "0").strip()

    if garment_type == _ACCESSORY_GARMENT_TYPE or render_is_accessory == "1":
        logger.info(
            "SKU %s is accessory — skipping (per D-12/GM-06). "
            "garment_type_lock=%r render_is_accessory=%r",
            sanitized_sku,
            garment_type,
            render_is_accessory,
        )
        return None

    # Construct bundle path from dossier_slug (col 22, 0-indexed).
    # Fall back to sanitized_sku when dossier_slug is absent or empty.
    dossier_slug = matching_row.get("dossier_slug", "").strip()
    dir_name = dossier_slug if dossier_slug else sanitized_sku
    bundle_dir = effective_bundle_root / dir_name
    manifest_path = bundle_dir / "manifest.json"

    branding_spec = matching_row.get("branding_spec", "").strip()

    return ResolvedSKU(
        sku=sanitized_sku,
        name=matching_row.get("name", "").strip(),
        garment_type=garment_type,
        bundle_dir=bundle_dir,
        manifest_path=manifest_path,
        branding_spec=branding_spec,
        is_jersey=(sanitized_sku in _JERSEY_SKUS),
    )


# ---------------------------------------------------------------------------
# verify_tripo_region
# ---------------------------------------------------------------------------


def verify_tripo_region(tripo_api_key: str | None = None) -> bool:
    """Verify the Tripo .ai region key is active by calling the free get_balance endpoint.

    This is a mandatory pre-flight check before any paid Tripo dispatch (D-08).
    The lazy import of TripoClient prevents EnvironmentError at module import time —
    the client is only instantiated when this function is explicitly called.

    The TRIPO3D_API_KEY is read from the environment; it is NEVER logged.

    Args:
        tripo_api_key: Optional explicit key override (for testing).
                       If None, reads TRIPO3D_API_KEY from os.environ.

    Returns:
        True if the .ai region key is active and get_balance() returned data.
        False if the balance probe fails (wrong region, bad key, network error).

    Raises:
        EnvironmentError: If no API key is available.
    """
    # Lazy import — prevents TripoClient (and its httpx dep) from being required
    # at module import time, and prevents accidental key loading by importers.
    from ai_3d.providers.tripo import TripoClient  # noqa: PLC0415

    key = tripo_api_key or os.environ.get("TRIPO3D_API_KEY")

    if not key:
        raise OSError(
            "TRIPO3D_API_KEY not set — cannot verify Tripo region. "
            "Set the key in .env.hf or environment before dispatching."
        )

    async def _probe() -> bool:
        client = TripoClient(api_key=key)
        try:
            balance = await client.get_balance()
            # get_balance() returns {} on any internal error (it swallows exceptions).
            # Treat a non-empty dict as a successful probe.
            if balance:
                logger.info(
                    "Tripo .ai region active; credits available (balance keys: %s)",
                    list(balance.keys()),
                )
                return True
            logger.warning(
                "Tripo region check returned empty balance dict — "
                "possible wrong region, bad key, or API error."
            )
            return False
        except Exception as exc:
            logger.warning("Tripo region check failed: %s", exc)
            return False
        finally:
            await client.close()

    try:
        return asyncio.run(_probe())
    except Exception as exc:
        logger.warning("Tripo region probe raised unexpected error: %s", exc)
        return False
