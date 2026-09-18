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


def test_symlinked_registry_stays_a_symlink_and_writes_through(registry, tmp_path):
    """The repo-root SOT link must survive writes; projections land beside the real file."""
    link_dir = tmp_path / "root"
    link_dir.mkdir()
    link = link_dir / "logo-registry.json"
    link.symlink_to(registry)

    update_catalog_fields("br-test", {"name": "Renamed"}, link)

    assert link.is_symlink()
    assert json.loads(registry.read_text())["products"]["br-test"]["catalog"]["name"] == "Renamed"
    assert (registry.parent / "skyyrose-catalog.csv").is_file()
    assert not (link_dir / "skyyrose-catalog.csv").exists()
    assert not (link_dir / "dossiers").exists()
    assert export_compatibility(link, check=True) == []
    assert link.is_symlink()


def test_check_reports_orphan_dossiers_without_deleting_them(registry):
    """A dossier no product projects to is drift: product facts authored outside the SOT."""
    from skyyrose.core.product_registry import orphan_dossiers

    export_compatibility(registry)
    dossiers = registry.parent / "dossiers"
    (dossiers / "_template.md").write_text("template\n")
    rogue = dossiers / "hand-authored.md"
    rogue.write_text("---\nsku: zz-999\n---\nAuthored outside the registry\n")

    assert export_compatibility(registry, check=True) == [str(rogue)]
    assert orphan_dossiers(registry) == [rogue]
    # A real sync must surface it too and must never remove founder-authored data.
    assert str(rogue) in export_compatibility(registry)
    assert rogue.is_file()


def test_retained_dossier_is_exempt_but_any_other_orphan_still_fails(registry):
    """The founder's keep-as-is exemption covers its exact filename and nothing else."""
    from skyyrose.core.product_registry import RETAINED_DOSSIERS, orphan_dossiers

    export_compatibility(registry)
    dossiers = registry.parent / "dossiers"
    for name in RETAINED_DOSSIERS:
        (dossiers / name).write_text("---\nsku: zz-001\n---\nKept by founder decision\n")
    rogue = dossiers / "hand-authored.md"
    rogue.write_text("---\nsku: zz-999\n---\nAuthored outside the registry\n")

    assert orphan_dossiers(registry) == [rogue]
    assert export_compatibility(registry, check=True) == [str(rogue)]


def test_every_retained_dossier_is_real_and_still_unowned():
    """An exemption whose file is gone, or that now shadows a product's dossier, must go."""
    from skyyrose.core.product_registry import (
        PRODUCT_REGISTRY,
        RETAINED_DOSSIERS,
        load_registry,
    )

    dossiers = PRODUCT_REGISTRY.resolve().parent / "dossiers"
    owned = {f"{p['dossier']['slug']}.md" for p in load_registry()["products"].values()}
    for name, reason in RETAINED_DOSSIERS.items():
        assert (dossiers / name).is_file(), f"{name} is exempt but no longer exists"
        assert name not in owned, f"{name} is a registry product's dossier, not an exception"
        assert len(reason) > 40, f"{name} needs a real reason"


def test_sync_check_cli_fails_on_orphan_dossier(registry, monkeypatch, capsys):
    """`sync_product_registry.py --check` exits non-zero and names the orphan."""
    import importlib

    from skyyrose.core import product_registry

    cli = importlib.import_module("scripts.sync_product_registry")
    export_compatibility(registry)
    rogue = registry.parent / "dossiers" / "hand-authored.md"
    rogue.write_text("Authored outside the registry\n")
    monkeypatch.setattr(product_registry, "PRODUCT_REGISTRY", registry)
    monkeypatch.setattr("sys.argv", ["sync_product_registry.py", "--check"])

    assert cli.main() == 1
    assert f"ORPHAN {rogue}" in capsys.readouterr().out
    assert rogue.is_file()
