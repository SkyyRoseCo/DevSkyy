"""Asset-manifest integrity gate.

Guards the content-hashed SKU→asset manifest (``assets/products/manifest.json``)
against the two drift classes it exists to prevent:

1. **Stale manifest** — a source file was renamed/replaced but the manifest was
   not regenerated. ``--check`` (regenerate-and-diff) catches it.
2. **Broken tree** — the committed manifest names a file that is now missing or
   whose content changed. ``verify()`` catches it.

These are the bug-119 (mislabeled-reference) and "rename breaks mid-paid-run"
preventions, asserted in CI.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from skyyrose.core.asset_manifest import AssetManifest
from tests.sparse_guard import requires_tree

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "assets" / "products" / "manifest.json"

requires_asset_tree = requires_tree("assets/products")


def _load_builder():
    """Import scripts/build_asset_manifest.py as a module (hyphen-free path)."""
    spec = importlib.util.spec_from_file_location(
        "build_asset_manifest", REPO_ROOT / "scripts" / "build_asset_manifest.py"
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@requires_asset_tree
def test_manifest_exists_and_loads():
    assert (
        MANIFEST.exists()
    ), "assets/products/manifest.json missing — run scripts/build_asset_manifest.py"
    m = AssetManifest.load()
    assert m.skus, "manifest registered zero SKUs"


@requires_asset_tree
def test_committed_manifest_matches_regenerated_tree():
    """The committed manifest must equal a fresh regeneration (no silent drift)."""
    builder = _load_builder()
    fresh = builder.build()
    committed = AssetManifest.load()
    committed_payload = committed.to_payload()
    fresh_payload = fresh.to_payload()
    committed_payload.pop("generated_at", None)
    fresh_payload.pop("generated_at", None)
    assert committed_payload == fresh_payload, (
        "asset manifest is stale — a source file changed without regeneration. "
        "Run `python scripts/build_asset_manifest.py` and commit."
    )


@requires_asset_tree
def test_every_pinned_asset_exists_and_hash_matches():
    """Pinned files stay valid; deliberately blocked SKUs remain blocked."""
    manifest = AssetManifest.load()
    findings = manifest.verify()
    assert {d.sku for d in findings if d.kind == "resolution_error"} == {
        sku for sku, entry in manifest.skus.items() if entry.resolution_error
    }
    drift = [d for d in findings if d.kind != "resolution_error"]
    assert not drift, "asset drift: " + "; ".join(
        f"{d.sku}/{d.role}:{d.kind}:{d.path}" for d in drift
    )


@requires_asset_tree
def test_catalog_sha_is_pinned():
    m = AssetManifest.load()
    assert m.catalog_sha and m.catalog_sha.startswith("sha256:")


def test_br007_directional_authorities_are_hash_bound():
    assets = AssetManifest.load().skus["br-007"]
    wearer_left = assets.by_role("garment-wearer-left")
    wearer_right = assets.by_role("garment-wearer-right")

    assert wearer_left is not None
    assert wearer_left.path.endswith("br-007-shorts-wearer-left.jpeg")
    assert wearer_left.sha256 == (
        "sha256:34ad777e56b38bea0d86c87e9815c537b109ab7fcf39614711093fb55f2309d2"
    )
    assert wearer_right is not None
    assert wearer_right.path.endswith("br-007-shorts-wearer-right.jpeg")
    assert wearer_right.sha256 == (
        "sha256:850d29f480bcb8e282a21ffca427bd368a03d05ff5f61fad8a8ff58f497ec8f8"
    )


def test_br007_founder_four_angle_authority_is_hash_bound():
    assets = AssetManifest.load().skus["br-007"]
    founder_board = assets.by_role("garment-founder-four-angle")

    assert founder_board is not None
    assert founder_board.path.endswith("br-007-founder-four-angle-physical-authority.jpg")
    assert founder_board.sha256 == (
        "sha256:7142815d09c35eff5de2b9c918340a6298f64dc84b66f9c142f37a1cf9c6b130"
    )


def test_verify_detects_a_missing_file(tmp_path):
    """A manifest that names an absent file must surface as drift."""
    from skyyrose.core.asset_manifest import AssetRecord, SkuAssets

    m = AssetManifest()
    m.skus["x-001"] = SkuAssets(
        sku="x-001",
        name="X",
        collection="test",
        garment_type="tee",
        assets=[
            AssetRecord(
                role="front",
                path="assets/products/_does_not_exist.png",
                sha256="sha256:dead",
            )
        ],
    )
    drift = m.verify(base=tmp_path)
    assert len(drift) == 1 and drift[0].kind == "missing"


def test_keeper_with_missing_asset_is_ignored(monkeypatch):
    """A keeper whose surviving asset is gone must NOT block the re-render."""
    from scripts.oai_render import pipeline

    monkeypatch.setattr(
        pipeline,
        "_registry_keepers",
        lambda: [
            {
                "sku": "sg-009",
                "style": "on-model",
                "view": "front",
                "asset": "assets/products/_gone.webp",
            }
        ],
    )
    skips = pipeline._keeper_skips()
    assert ("sg-009", "on-model", "front") not in skips  # asset missing → not skipped


def test_gate_fails_closed_when_manifest_missing(tmp_path, monkeypatch):
    """A missing manifest must BLOCK a paid run, not pass with zero protection."""
    from scripts.oai_render import pipeline
    from skyyrose.core import asset_manifest

    monkeypatch.setattr(asset_manifest, "MANIFEST_PATH", tmp_path / "no_manifest.json")
    findings = pipeline.verify_plan_assets([])  # plans irrelevant — file is absent
    assert len(findings) == 1 and findings[0].kind == "manifest_missing"


def test_corrupt_manifest_raises_actionable_error(tmp_path):
    bad = tmp_path / "manifest.json"
    bad.write_text("{ not valid json", encoding="utf-8")
    with pytest.raises(ValueError, match="corrupt"):
        AssetManifest.load(bad)


def test_registry_contract_failure_serializes_and_blocks_verification(tmp_path, monkeypatch):
    from skyyrose.elite_studio.logo_registry import RegistryContractError

    builder = _load_builder()
    registry = tmp_path / "registry.json"
    registry.write_text('{"authority":"fixture"}')
    monkeypatch.setattr(builder, "PRODUCT_REGISTRY", registry)
    monkeypatch.setattr(
        builder,
        "_catalog_rows",
        lambda: {"sg-002": {"name": "Bridge", "collection": "signature", "garment_type": "shirt"}},
    )
    monkeypatch.setattr(builder.references, "build_dossier_index", dict)
    monkeypatch.setattr(builder, "_supplemental_source_records", lambda sku: [])

    def blocked(*args):
        raise RegistryContractError("sg-002: exact Bridge artwork binding is UNBOUND")

    monkeypatch.setattr(builder.references, "build_references", blocked)
    first, second = builder.build(), builder.build()
    assert first.to_payload() == second.to_payload()
    assert first.skus["sg-002"].assets == []
    path = first.save(tmp_path / "manifest.json")
    restored = AssetManifest.load(path)
    findings = restored.verify(["sg-002"])
    assert len(findings) == 1
    assert findings[0].kind == "resolution_error"
    assert "RegistryContractError" in findings[0].detail
    assert "UNBOUND" in findings[0].detail
    assert restored.to_payload() == first.to_payload()


def test_registry_hash_changes_invalidate_manifest_and_check(tmp_path, monkeypatch):
    import json

    from skyyrose.core.hashing import sha256_of_file

    builder = _load_builder()
    registry = tmp_path / "registry.json"
    registry.write_text('{"logo":{"width":3,"height":4}}')
    monkeypatch.setattr(builder, "PRODUCT_REGISTRY", registry)
    monkeypatch.setattr(builder, "_catalog_rows", dict)
    monkeypatch.setattr(builder.references, "build_dossier_index", dict)
    original = builder.build()
    assert original.registry_sha == sha256_of_file(registry)
    assert original.verify() == []
    original_path = original.save(tmp_path / "manifest.json")
    restored = AssetManifest.load(original_path)
    monkeypatch.setattr(builder.AssetManifest, "load", lambda: restored)
    assert builder.main(["build_asset_manifest.py", "--check"]) == 0
    raw = json.loads(registry.read_text())
    raw["logo"]["width"] = 3.25  # isolated hypothetical amendment, never founder data
    registry.write_text(json.dumps(raw))
    assert builder.build().registry_sha != original.registry_sha
    findings = restored.verify()
    assert len(findings) == 1 and findings[0].role == "registry"
    assert findings[0].kind == "hash_mismatch"
    assert builder.main(["build_asset_manifest.py", "--check"]) == 1


def test_legacy_manifest_payload_remains_readable(tmp_path):
    import json

    payload = {
        "version": 1,
        "generated_at": "",
        "catalog_sha": None,
        "skus": {
            "x-001": {
                "sku": "x-001",
                "name": "X",
                "collection": "test",
                "garment_type": "tee",
                "assets": [],
            }
        },
    }
    path = tmp_path / "legacy.json"
    path.write_text(json.dumps(payload))
    assert AssetManifest.load(path).to_payload() == payload


def test_version_two_requires_registry_hash():
    findings = AssetManifest(version=2).verify()
    assert len(findings) == 1 and findings[0].kind == "registry_unpinned"
