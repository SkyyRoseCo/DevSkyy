"""``sync_product_registry.py`` owns the asset manifest, not only the CSV and dossiers.

The manifest pins the registry by sha256, so every registry edit makes it stale by
construction. The documented post-edit step (``sync_product_registry.py``) and the
``--check`` that CI and the catalog-drift hook run must therefore see it; otherwise the
only detector is a pytest failure after the fact (branch A's tip shipped with a manifest
pinned to a different registry and nothing flagged it).
"""

from __future__ import annotations

import importlib
import json

import pytest

from skyyrose.core import asset_manifest, product_registry


@pytest.fixture
def world(tmp_path, monkeypatch):
    """A tiny registry plus an empty manifest location, isolated from the real tree."""
    cli = importlib.import_module("scripts.sync_product_registry")
    builder = importlib.import_module("scripts.build_asset_manifest")
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps({"logo": {"width": 3, "height": 4}}))
    manifest = tmp_path / "manifest.json"
    monkeypatch.setattr(product_registry, "PRODUCT_REGISTRY", registry)
    monkeypatch.setattr(builder, "PRODUCT_REGISTRY", registry)
    monkeypatch.setattr(builder, "_catalog_rows", dict)
    monkeypatch.setattr(builder.references, "build_dossier_index", dict)
    monkeypatch.setattr(asset_manifest, "MANIFEST_PATH", manifest)
    # The CSV/dossier half is covered by test_unified_product_registry; isolate the manifest half.
    monkeypatch.setattr(cli, "export_compatibility", lambda check=False: [])
    monkeypatch.setattr(cli, "orphan_dossiers", lambda: [])
    return cli, builder, registry, manifest


def _run(cli, monkeypatch, *argv: str) -> int:
    monkeypatch.setattr("sys.argv", ["sync_product_registry.py", *argv])
    return cli.main()


def _amend_registry(registry) -> None:
    raw = json.loads(registry.read_text())
    raw["logo"]["width"] = 3.25  # isolated hypothetical amendment, never founder data
    registry.write_text(json.dumps(raw))


def test_check_reports_a_missing_manifest_as_stale_and_writes_nothing(world, monkeypatch, capsys):
    cli, _, _, manifest = world
    assert _run(cli, monkeypatch, "--check") == 1
    assert f"STALE {manifest}" in capsys.readouterr().out
    assert not manifest.exists(), "--check must stay read-only"


def test_sync_writes_the_manifest_and_then_check_passes(world, monkeypatch, capsys):
    cli, _, _, manifest = world
    assert _run(cli, monkeypatch) == 0
    assert f"UPDATED {manifest}" in capsys.readouterr().out
    assert manifest.is_file()
    assert _run(cli, monkeypatch, "--check") == 0
    assert "STALE" not in capsys.readouterr().out


def test_a_registry_edit_stales_the_manifest_and_sync_repairs_it(world, monkeypatch, capsys):
    cli, _, registry, manifest = world
    _run(cli, monkeypatch)
    capsys.readouterr()
    _amend_registry(registry)

    assert _run(cli, monkeypatch, "--check") == 1
    assert f"STALE {manifest}" in capsys.readouterr().out
    assert _run(cli, monkeypatch) == 0
    assert _run(cli, monkeypatch, "--check") == 0


def test_a_clean_sync_does_not_rewrite_an_unchanged_manifest(world, monkeypatch):
    cli, _, _, manifest = world
    _run(cli, monkeypatch)
    before = manifest.read_bytes()
    assert _run(cli, monkeypatch) == 0
    assert manifest.read_bytes() == before, "generated_at churn would dirty every sync"


def test_an_unreadable_manifest_is_drift_not_a_crash(world, monkeypatch, capsys):
    cli, _, _, manifest = world
    manifest.write_text("{not json")
    assert _run(cli, monkeypatch, "--check") == 1
    assert f"STALE {manifest}" in capsys.readouterr().out
    assert _run(cli, monkeypatch) == 0
    assert _run(cli, monkeypatch, "--check") == 0


def test_a_non_canonical_registry_leaves_the_real_manifest_alone(world, monkeypatch, tmp_path):
    cli, builder, _, manifest = world
    other = tmp_path / "other-registry.json"
    other.write_text("{}")
    monkeypatch.setattr(builder, "PRODUCT_REGISTRY", other)  # the manifest tracks a different file
    assert _run(cli, monkeypatch, "--check") == 0
    assert not manifest.exists()
