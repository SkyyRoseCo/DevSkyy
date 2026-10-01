"""Registry migration preserves facts and rejection metadata; no visual approval."""

import json
from pathlib import Path

import pytest

from skyyrose.core import product_registry


def fixture(tmp_path: Path) -> tuple[Path, Path, dict]:
    registry = product_registry.load_registry()
    projection = {
        "schema_version": 1,
        "authorization": "LOCAL_SYNTHETIC_TEST",
        "products": {
            sku: {
                "src": "assets/test.webp",
                "sha256": "0" * 64,
                "current_fidelity_status": "BLOCKED_PRODUCT_MISMATCH",
            }
            for sku in registry["products"]
        },
    }
    for product in registry["products"].values():
        product["images"].pop("card_front", None)
    registry.pop("storefront_card_manifest", None)
    target = tmp_path / "logo-registry.json"
    source = tmp_path / "cards.json"
    target.write_text(json.dumps(registry))
    source.write_text(json.dumps(projection))
    return target, source, registry


def test_migration_preserves_all_product_facts_and_rejections(tmp_path: Path) -> None:
    target, source, before = fixture(tmp_path)
    product_registry.import_storefront_card_projection(source, target)
    after = product_registry.load_registry(target)
    for sku, product in after["products"].items():
        binding = product["images"].pop("card_front")
        assert binding["current_fidelity_status"] == "BLOCKED_PRODUCT_MISMATCH"
        assert product == before["products"][sku]
    product_registry.import_storefront_card_projection(source, target)
    assert product_registry.export_compatibility(target, check=True) == []


def test_existing_canonical_binding_cannot_be_overwritten(tmp_path: Path) -> None:
    target, source, _ = fixture(tmp_path)
    product_registry.import_storefront_card_projection(source, target)
    unchanged = target.read_bytes()
    stale = json.loads(source.read_text())
    stale["products"]["br-001"]["current_fidelity_status"] = "APPROVED"
    source.write_text(json.dumps(stale))
    with pytest.raises(ValueError, match="conflicts"):
        product_registry.import_storefront_card_projection(source, target)
    assert target.read_bytes() == unchanged


def test_incomplete_projection_does_not_write(tmp_path: Path) -> None:
    target, source, _ = fixture(tmp_path)
    unchanged = target.read_bytes()
    stale = json.loads(source.read_text())
    stale["products"].pop("br-001")
    source.write_text(json.dumps(stale))
    with pytest.raises(ValueError, match="exact registry SKU"):
        product_registry.import_storefront_card_projection(source, target)
    assert target.read_bytes() == unchanged
