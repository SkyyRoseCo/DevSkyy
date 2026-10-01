"""Registry migration preserves facts and rejection metadata; no visual approval."""

import json
import fcntl
from pathlib import Path

import pytest

from skyyrose.core import product_registry


def fixture(tmp_path: Path) -> tuple[Path, Path, dict]:
    registry = product_registry.load_registry()
    projection = {
        "schema_version": 1,
        "authorization": "LOCAL_SYNTHETIC_TEST",
        "card_treatment_approval": {
            "date": "2026-10-01",
            "request": "Synthetic fixture only",
            "scope": "No visual acceptance",
        },
        "products": {
            sku: {
                "src": "assets/test.webp",
                "width": 100,
                "height": 100,
                "alt": "Synthetic test binding",
                "source_sha256": "0" * 64,
                "scene_status": "FOUNDER_APPROVED_V2_CARD",
                "current_fidelity_note": "Synthetic rejection test",
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
    stale["products"]["br-001"]["current_fidelity_status"] = "EXISTING_SCOPED_APPROVAL_RETAINED"
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


@pytest.mark.parametrize(
    "field,value",
    [
        ("src", "../../outside.webp"),
        ("sha256", 7),
        ("width", 0),
        ("height", True),
        ("alt", ""),
        ("current_fidelity_status", "APPROVED"),
    ],
)
def test_schema_invalid_projection_does_not_write(tmp_path: Path, field: str, value) -> None:
    target, source, _ = fixture(tmp_path)
    unchanged = target.read_bytes()
    invalid = json.loads(source.read_text())
    invalid["products"]["br-001"][field] = value
    source.write_text(json.dumps(invalid))
    with pytest.raises(ValueError, match="Invalid storefront card projection"):
        product_registry.import_storefront_card_projection(source, target)
    assert target.read_bytes() == unchanged
    assert not (tmp_path / "skyyrose-catalog.csv").exists()


def test_registry_commit_failure_restores_projections(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target, source, _ = fixture(tmp_path)
    unchanged = target.read_bytes()
    output = tmp_path / "projection.json"
    output.write_text("old projection")
    monkeypatch.setattr(
        product_registry, "_compatibility_outputs", lambda raw, path: {output: "new projection"}
    )
    atomic_write = product_registry._atomic_write

    def fail_commit(path: Path, content: str) -> None:
        if path == target:
            raise OSError("simulated registry commit failure")
        atomic_write(path, content)

    monkeypatch.setattr(product_registry, "_atomic_write", fail_commit)
    with pytest.raises(OSError, match="simulated"):
        product_registry.import_storefront_card_projection(source, target)
    assert target.read_bytes() == unchanged
    assert output.read_text() == "old projection"


def test_registry_read_occurs_under_writer_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target, source, _ = fixture(tmp_path)
    load = product_registry.load_registry
    calls = []

    def read_locked(path: Path):
        with target.with_suffix(".json.lock").open("a") as probe:
            with pytest.raises(BlockingIOError):
                fcntl.flock(probe.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        calls.append(path)
        return load(path)

    monkeypatch.setattr(product_registry, "load_registry", read_locked)
    product_registry.import_storefront_card_projection(source, target)
    assert calls == [target]


def test_projection_failure_rolls_back_before_registry_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target, source, _ = fixture(tmp_path)
    unchanged = target.read_bytes()
    first, second = tmp_path / "first.json", tmp_path / "second.json"
    first.write_text("original")
    second.write_text("original second")
    monkeypatch.setattr(
        product_registry,
        "_compatibility_outputs",
        lambda raw, path: {first: "new", second: "new second"},
    )
    atomic_write = product_registry._atomic_write

    def fail_second(path: Path, content: str) -> None:
        if path == second:
            raise OSError("simulated projection failure")
        atomic_write(path, content)

    monkeypatch.setattr(product_registry, "_atomic_write", fail_second)
    with pytest.raises(OSError, match="simulated"):
        product_registry.import_storefront_card_projection(source, target)
    assert target.read_bytes() == unchanged
    assert first.read_text() == "original"
    assert second.read_text() == "original second"
