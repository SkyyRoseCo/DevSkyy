"""Offline evidence that Bridge bundles preserve exact garment-source roles."""

from pathlib import Path

import pytest

from scripts import scaffold_sku_asset_folders as scaffold
from skyyrose.core.dossier_loader import get_product_with_dossier
from skyyrose.elite_studio.logo_registry import LogoRegistry


@pytest.mark.parametrize("sku", ["sg-001", "sg-002", "sg-003", "sg-005"])
def test_bridge_bundle_uses_bound_garment_not_generic_logo(monkeypatch, tmp_path, sku):
    registry = LogoRegistry.load()
    monkeypatch.setattr(scaffold, "GOLDEN_DIR", tmp_path / "golden")
    source = registry.primary_reference_for(sku)
    result = scaffold.scaffold_sku(sku, get_product_with_dossier(sku), registry._raw)
    bundle = tmp_path / "golden" / sku
    links = list((bundle / "garment-source").iterdir())
    assert len(links) == 1
    assert links[0].resolve() == source.resolve()
    assert not list((bundle / "logos").iterdir())
    assert not list((bundle / "techflat").iterdir())
    assert scaffold._find_logo_file("black-roses-cloud-cluster", registry._raw, sku) is None
    brief = (bundle / "placement.md").read_text()
    assert "Role: complete physical garment, front view" in brief
    assert "No standalone logo is supplied" in brief
    assert source.relative_to(scaffold._REPO_ROOT).as_posix() in brief
    assert "garment-source/back" in result.missing
    again = scaffold.scaffold_sku(sku, get_product_with_dossier(sku), registry._raw)
    assert again.created_symlinks == again.pruned_symlinks == 0
    assert not again.wrote_placement


def test_bridge_scaffold_replaces_only_generated_stale_links(monkeypatch, tmp_path):
    sku = "sg-002"
    registry = LogoRegistry.load()
    monkeypatch.setattr(scaffold, "GOLDEN_DIR", tmp_path / "golden")
    bundle = tmp_path / "golden" / sku
    for sub in ("techflat", "logos", "garment-source"):
        (bundle / sub).mkdir(parents=True)
    wrong = tmp_path / "unregistered-generic.jpg"
    wrong.write_bytes(b"illustrative wrong-source fixture")
    stale = [
        bundle / "techflat" / "front.jpg",
        bundle / "techflat" / "back.jpg",
        bundle / "logos" / "black-roses-cloud-cluster.jpeg",
        bundle / "garment-source" / "front.webp",
    ]
    for link in stale:
        link.symlink_to(wrong)
    result = scaffold.scaffold_sku(sku, get_product_with_dossier(sku), registry._raw)
    assert result.pruned_symlinks == len(stale)
    assert all(not path.exists() and not path.is_symlink() for path in stale)
    source = registry.primary_reference_for(sku)
    assert (bundle / "garment-source" / f"front{source.suffix}").resolve() == source
    assert wrong.read_bytes() == b"illustrative wrong-source fixture"


def test_bridge_scaffold_preserves_and_reports_real_user_files(monkeypatch, tmp_path):
    sku = "sg-002"
    registry = LogoRegistry.load()
    monkeypatch.setattr(scaffold, "GOLDEN_DIR", tmp_path / "golden")
    bundle = tmp_path / "golden" / sku
    relative_files = [
        "techflat/front.jpg",
        "logos/black-roses-cloud-cluster.jpeg",
        "garment-source/front.jpg",
        "placement.md",
    ]
    for name in relative_files:
        path = bundle / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"user-authored original")
    result = scaffold.scaffold_sku(sku, get_product_with_dossier(sku), registry._raw)
    for name in relative_files:
        assert (bundle / name).read_bytes() == b"user-authored original"
        assert f"preserved user file: {Path(name)}" in result.missing


def test_bridge_scaffold_dry_run_leaves_files_unchanged(monkeypatch, tmp_path):
    registry = LogoRegistry.load()
    target = tmp_path / "golden"
    monkeypatch.setattr(scaffold, "GOLDEN_DIR", target)
    scaffold.scaffold_sku("sg-001", get_product_with_dossier("sg-001"), registry._raw, dry_run=True)
    assert not target.exists()
