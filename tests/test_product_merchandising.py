"""Canonical merchandising is route configuration, separate from founder facts."""

import copy
import json

import pytest

from skyyrose.core import product as reader
from skyyrose.core import product_registry as registry


@pytest.fixture
def registry_copy(tmp_path):
    target = tmp_path / "logo-registry.json"
    target.write_text(registry.PRODUCT_REGISTRY.read_text())
    return target


def test_canonical_assignments_exposed():
    raw = registry.load_registry()
    for sku, record in raw["products"].items():
        assert reader.get_product(sku)["merchandising"] == record["merchandising"]
    assert reader.get_product("br-015")["merchandising"] == {
        "series_slug": "jersey-series",
        "series_region": "oakland",
        "series_order": 20,
    }


def test_mutation_reads_canonical_and_preserves_other_facts(registry_copy, monkeypatch):
    before = registry.load_registry(registry_copy)
    value = {"series_slug": "jersey-series", "series_region": "san-jose", "series_order": 90}
    registry.update_product_merchandising({"br-003": value}, source="test", path=registry_copy)
    monkeypatch.setattr(registry, "PRODUCT_REGISTRY", registry_copy)
    assert reader.get_product("br-003")["merchandising"] == value
    after = registry.load_registry(registry_copy)
    expected = copy.deepcopy(before)
    expected["products"]["br-003"]["merchandising"] = value
    expected["products"]["br-003"]["merchandising_provenance"] = {
        "source": "test",
        "kind": "ROUTE_CONFIGURATION",
    }
    assert after == expected


def test_missing_only_does_not_overwrite(registry_copy):
    before = registry_copy.read_bytes()
    value = {"series_slug": "", "series_region": "", "series_order": 0}
    assert (
        registry.update_product_merchandising(
            {"br-003": value}, source="migration", only_missing=True, path=registry_copy
        )
        == []
    )
    assert registry_copy.read_bytes() == before


@pytest.mark.parametrize(
    "bad",
    [
        {"series_slug": "invented", "series_region": "oakland", "series_order": 10},
        {"series_slug": "jersey-series", "series_region": "invented", "series_order": 10},
        {"series_slug": "jersey-series", "series_region": "oakland", "series_order": True},
        {"series_slug": "jersey-series", "series_region": "oakland", "series_order": 0},
        {"series_slug": "", "series_region": "oakland", "series_order": 0},
        {"series_slug": ""},
    ],
)
def test_invalid_batch_is_atomic(registry_copy, bad):
    before = registry_copy.read_bytes()
    with pytest.raises(ValueError):
        registry.update_product_merchandising(
            {
                "br-003": {"series_slug": "", "series_region": "", "series_order": 0},
                "br-008": bad,
            },
            source="test",
            path=registry_copy,
        )
    assert registry_copy.read_bytes() == before


def test_unknown_sku_refused(registry_copy):
    with pytest.raises(KeyError):
        registry.update_product_merchandising(
            {
                "unknown": {"series_slug": "", "series_region": "", "series_order": 0},
            },
            source="test",
            path=registry_copy,
        )


def test_reader_refuses_invalid_canonical_assignment(registry_copy, monkeypatch):
    raw = registry.load_registry(registry_copy)
    raw["products"]["br-003"]["merchandising"]["series_slug"] = "invented"
    registry_copy.write_text(json.dumps(raw))
    monkeypatch.setattr(registry, "PRODUCT_REGISTRY", registry_copy)
    with pytest.raises(ValueError, match="Unknown merchandising"):
        reader.get_product("br-003")


def test_duplicate_series_order_rejected_without_writing(registry_copy):
    before = registry_copy.read_bytes()
    products = registry.load_registry(registry_copy)["products"]
    # A different region still shares the series-wide ordering namespace.
    value = dict(products["br-008"]["merchandising"], series_order=10)
    with pytest.raises(ValueError, match="Duplicate merchandising series/order"):
        registry.update_product_merchandising({"br-008": value}, source="test", path=registry_copy)
    assert registry_copy.read_bytes() == before


def test_batch_can_swap_series_positions(registry_copy):
    products = registry.load_registry(registry_copy)["products"]
    assignments = {
        "br-003": dict(products["br-003"]["merchandising"], series_order=50),
        "br-008": dict(products["br-008"]["merchandising"], series_order=10),
    }
    assert registry.update_product_merchandising(
        assignments, source="test", path=registry_copy
    ) == ["br-003", "br-008"]
    after = registry.load_registry(registry_copy)["products"]
    for sku, expected in assignments.items():
        assert after[sku]["merchandising"] == expected
