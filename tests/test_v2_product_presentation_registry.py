"""Regression coverage for the generated V2 product-presentation adapter."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv"
REGISTRY = ROOT / "wordpress-theme/skyyrose-flagship-2/data/product-presentation-registry.json"


def _catalog() -> dict[str, dict[str, str]]:
    with CATALOG.open(newline="", encoding="utf-8") as source:
        return {row["sku"].lower(): row for row in csv.DictReader(source)}


def _registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_registry_covers_the_exact_canonical_catalog_skus() -> None:
    assert set(_registry()["products"]) == set(_catalog())


def test_registry_preorder_state_is_derived_from_the_catalog() -> None:
    catalog = _catalog()
    for sku, presentation in _registry()["products"].items():
        assert presentation["is_preorder"] is (
            catalog[sku]["is_preorder"].strip().lower() in {"1", "true", "yes"}
        )


def test_jersey_membership_and_routes_have_one_registry_authority() -> None:
    registry = _registry()
    jerseys = registry["supplements"]["jersey_series_skus"]
    assert jerseys == [
        "br-003",
        "br-008",
        "br-009",
        "br-010",
        "br-011",
        "br-012",
        "br-014",
        "br-015",
    ]
    for sku in jerseys:
        record = registry["products"][sku]
        assert record["collection"] == "black-rose"
        assert record["presentation"] == "jersey-series"
        # Founder correction: Jersey Series is a Black Rose release chapter.
        # See docs/design/v2-remodel/reports/handoff-reconciliation-2026-08-15.md.
        assert record["route"] == "/collections/black-rose/#jersey-series"
        assert "jersey_chapter" in record
        assert "film_start" in record
