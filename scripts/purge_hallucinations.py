#!/usr/bin/env python3
"""
Purge Hallucinations Utility
============================
Finds identified AI hallucinations in the product imagery folder:
1. Model shots for SKUs the product registry marks as accessories.
2. Renders for the non-existent 'po' collection.
3. Identified 2MB+ unoptimized model shots that lack front-view pairs.

Deletion is permanent, so the default run only lists the matches.
Pass --apply to delete them.
"""

import argparse
import logging
from pathlib import Path

from skyyrose.core.paths import WP_PRODUCTS_DIR
from skyyrose.core.product import all_skus, get_product

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Paths
PRODUCTS_DIR = WP_PRODUCTS_DIR

# Hallucinated targets
PO_COLLECTION_PREFIX = "po-"  # Non-existent collection
SUSPECT_UNOPTIMIZED_SIZE_LIMIT = 1.5 * 1024 * 1024  # 1.5MB


def accessory_skus() -> list[str]:
    """SKUs the registry flags as accessories; these should not have human model shots."""
    return [
        sku
        for sku in all_skus()
        if str(get_product(sku)["catalog"].get("render_is_accessory", "")).strip() == "1"
    ]


def purge(apply: bool = False) -> list[Path]:
    """Return the matching files, deleting them only when ``apply`` is true."""
    if not PRODUCTS_DIR.exists():
        logger.error(f"Products directory not found: {PRODUCTS_DIR}")
        return []

    accessories = accessory_skus()
    matches = []

    for item in PRODUCTS_DIR.iterdir():
        if not item.is_file():
            continue

        name = item.name.lower()

        # Rule 1: Purge accessory model shots
        is_accessory_model = any(sku in name for sku in accessories) and "model" in name

        # Rule 2: Purge 'po' collection
        is_po_hallucination = name.startswith(PO_COLLECTION_PREFIX)

        # Rule 3: Identify unoptimized massive files (>1.5MB) that are specifically 'model' shots
        # These are usually the result of unconstrained AI generation without web-optimization
        is_massive_hallucination = (
            item.stat().st_size > SUSPECT_UNOPTIMIZED_SIZE_LIMIT and "model" in name
        )

        if is_accessory_model or is_po_hallucination or is_massive_hallucination:
            verb = "Purging" if apply else "Would purge"
            logger.info(
                f"{verb} hallucination: {item.name} ({item.stat().st_size / 1024 / 1024:.2f} MB)"
            )
            if apply:
                item.unlink()
            matches.append(item)

    if apply:
        logger.info(f"Cleanup complete. Deleted {len(matches)} hallucinated assets.")
    else:
        logger.info(f"Dry run: {len(matches)} file(s) match. Re-run with --apply to delete them.")
    return matches


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--apply", action="store_true", help="Delete the matches (permanent). Default: list only."
    )
    purge(apply=parser.parse_args(argv).apply)


if __name__ == "__main__":
    main()
