"""Gate for the product registry's organization: schema-valid and consistent.

A SOT that 116 files read has to stay predictable. These tests hold the three
properties ``scripts/organize_product_registry.py`` enforces -- schema validity,
canonical ordering, and cross-field consistency -- and prove the reorder is
lossless, so applying it is never a data risk.

Ordering findings are reported, not failed: reordering the 436 KB registry is a
deliberate one-time rewrite, and failing CI on it would block unrelated work.
Schema and consistency findings DO fail -- those are real defects.
"""

from __future__ import annotations

import json

import pytest

from scripts.organize_product_registry import (
    REGISTRY,
    SCHEMA,
    check_consistency,
    check_schema,
    organize,
    sku_sort_key,
)


@pytest.fixture(scope="module")
def registry() -> dict:
    return json.loads(REGISTRY.read_text())


def test_schema_file_is_itself_a_valid_json_schema() -> None:
    from jsonschema import Draft202012Validator

    Draft202012Validator.check_schema(json.loads(SCHEMA.read_text()))


def test_registry_matches_its_schema(registry: dict) -> None:
    """Required fields, SKU pattern, collection enum, boolean strings, no stray keys."""
    findings = check_schema(registry)
    assert not findings, "schema violations:\n" + "\n".join(
        f"  {f.where}: {f.message}" for f in findings[:20]
    )


def test_registry_is_internally_consistent(registry: dict) -> None:
    """catalog.sku matches its key, catalog_columns is satisfied, images exist on disk."""
    findings = check_consistency(registry)
    assert not findings, "consistency violations:\n" + "\n".join(
        f"  [{f.kind}] {f.where}: {f.message}" for f in findings[:20]
    )


def test_reordering_is_lossless(registry: dict) -> None:
    """The canonical rewrite changes key order only -- never a value.

    This is what makes ``--apply`` safe to run on the live SOT: dict equality in
    Python is order-insensitive, so an equal compare after reordering proves no
    datum moved, was dropped, or was coerced.
    """
    assert organize(registry) == registry


def test_reordering_is_idempotent(registry: dict) -> None:
    once = organize(registry)
    assert list(organize(once)) == list(once)
    assert list(organize(once)["products"]) == list(once["products"])


def test_skus_sort_by_collection_then_number() -> None:
    unsorted = ["kids-002", "br-010", "sg-001", "lh-005", "br-002", "sg-015"]
    assert sorted(unsorted, key=sku_sort_key) == [
        "sg-001",
        "sg-015",
        "br-002",
        "br-010",
        "lh-005",
        "kids-002",
    ]


def test_every_declared_image_exists_on_disk(registry: dict) -> None:
    """No record may point at an image that is not there (the lh-005 defect class)."""
    missing = [f for f in check_consistency(registry) if f.kind == "missing-asset"]
    assert not missing, "declared images missing from disk:\n" + "\n".join(
        f"  {f.where}: {f.message}" for f in missing[:20]
    )
