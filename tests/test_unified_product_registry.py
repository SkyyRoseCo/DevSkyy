"""The authoritative record survives export edits and updates atomically."""

import json

import pytest

from skyyrose.core.product_registry import (
    catalog_rows,
    export_compatibility,
    load_registry,
    update_catalog_fields,
)


@pytest.fixture
def registry(tmp_path):
    path = tmp_path / "logo-registry.json"
    path.write_text(
        json.dumps(
            {
                "catalog_columns": ["sku", "name", "front_model_image", "dossier_slug"],
                "products": {
                    "br-test": {
                        "catalog": {
                            "sku": "br-test",
                            "name": "Original",
                            "front_model_image": "",
                            "dossier_slug": "test",
                        },
                        "dossier": {"slug": "test", "content": "Maker specification\n"},
                        "images": {},
                    }
                },
            }
        )
    )
    return path


def test_exports_cannot_override_authority(registry):
    export_compatibility(registry)
    csv_path = registry.parent / "skyyrose-catalog.csv"
    csv_path.write_text(csv_path.read_text().replace("Original", "Stale edit"))
    assert catalog_rows(registry)[0]["name"] == "Original"
    assert str(csv_path) in export_compatibility(registry, check=True)
    export_compatibility(registry)
    assert export_compatibility(registry, check=True) == []


def test_product_update_changes_image_binding_and_preserves_other_fields(registry):
    update_catalog_fields("br-test", {"front_model_image": "assets/images/new.webp"}, registry)
    product = load_registry(registry)["products"]["br-test"]
    assert product["images"]["front_model_image"]["path"] == "assets/images/new.webp"
    assert product["catalog"]["name"] == "Original"
    assert product["dossier"]["content"] == "Maker specification\n"
    assert export_compatibility(registry, check=True) == []


def test_registry_commit_failure_restores_compatibility_exports(registry, monkeypatch):
    from skyyrose.core import product_registry

    export_compatibility(registry)
    original = registry.read_bytes()
    csv_path = registry.parent / "skyyrose-catalog.csv"
    original_csv = csv_path.read_bytes()
    real_write = product_registry._atomic_write

    def fail_commit(path, content):
        if path == registry:
            raise OSError("Simulated registry commit failure")
        real_write(path, content)

    monkeypatch.setattr(product_registry, "_atomic_write", fail_commit)
    with pytest.raises(OSError, match="commit failure"):
        update_catalog_fields("br-test", {"name": "Changed"}, registry)
    assert registry.read_bytes() == original
    assert csv_path.read_bytes() == original_csv


def test_effective_image_binding_is_the_export_authority(registry):
    raw = json.loads(registry.read_text())
    product = raw["products"]["br-test"]
    product["catalog"]["front_model_image"] = "assets/images/stale.webp"
    product["images"]["front_model_image"] = {"path": "assets/images/current.webp"}
    registry.write_text(json.dumps(raw))
    assert catalog_rows(registry)[0]["front_model_image"] == "assets/images/current.webp"
    export_compatibility(registry)
    assert "stale.webp" not in (registry.parent / "skyyrose-catalog.csv").read_text()


@pytest.mark.parametrize(
    "changes", [{"sku": "different"}, {"front_model_image": "../escape"}, {"name": 3}]
)
def test_bad_updates_leave_registry_bytes_intact(registry, changes):
    original = registry.read_bytes()
    with pytest.raises(ValueError):
        update_catalog_fields("br-test", changes, registry)
    assert registry.read_bytes() == original


def test_missing_registry_has_no_csv_fallback(tmp_path):
    (tmp_path / "skyyrose-catalog.csv").write_text("sku,name\nbr-test,Old\n")
    with pytest.raises(FileNotFoundError):
        catalog_rows(tmp_path / "logo-registry.json")


def test_returned_catalog_rows_do_not_mutate_authority(registry):
    catalog_rows(registry)[0]["name"] = "Changed"
    assert catalog_rows(registry)[0]["name"] == "Original"


@pytest.mark.parametrize("mode", [0o644, 0o640])
def test_atomic_update_preserves_existing_read_permissions(registry, mode):
    import stat

    export_compatibility(registry)
    csv_path = registry.parent / "skyyrose-catalog.csv"
    registry.chmod(mode)
    csv_path.chmod(mode)
    update_catalog_fields("br-test", {"name": "Updated"}, registry)
    assert stat.S_IMODE(registry.stat().st_mode) == mode
    assert stat.S_IMODE(csv_path.stat().st_mode) == mode


def test_new_exports_are_readable_by_consumer_processes(registry):
    import stat

    export_compatibility(registry)
    assert stat.S_IMODE((registry.parent / "skyyrose-catalog.csv").stat().st_mode) == 0o644


def test_csv_preserves_structured_garment_facts_without_competing_values(registry):
    import csv

    raw = json.loads(registry.read_text())
    raw["catalog_columns"].extend(
        ["color", "sizes", "fit", "materials", "features", "sizing_references"]
    )
    product = raw["products"]["br-test"]
    product["catalog"].update(color="Old", sizes="XS")
    product["garment"] = {
        "color": "Black",
        "available_sizes": ["S", "M"],
        "fit": {"specification": "Relaxed fit"},
        "materials": {"specification": "Cotton"},
        "features": {"specification": "Button front"},
        "sizing_references": {
            "garment_size_chart": None,
            "decoration_sizing_pointer": "#/sku_logos/br-test/decoration_sizing",
        },
    }
    registry.write_text(json.dumps(raw))
    export_compatibility(registry)
    with (registry.parent / "skyyrose-catalog.csv").open(newline="") as handle:
        row = next(csv.DictReader(handle))
    assert row == catalog_rows(registry)[0]
    assert (row["color"], row["sizes"], row["fit"], row["materials"], row["features"]) == (
        "Black",
        "S|M",
        "Relaxed fit",
        "Cotton",
        "Button front",
    )
    assert json.loads(row["sizing_references"]) == product["garment"]["sizing_references"]
    with pytest.raises(ValueError):
        update_catalog_fields("br-test", {"materials": "Competing value"}, registry)
