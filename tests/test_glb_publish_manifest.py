"""Candidate identity and fail-closed local GLB contract; no browser/network."""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

import pytest

from skyyrose.elite_studio.pipeline3d.glb_container import GlbFormatError, write_glb

_SPEC = importlib.util.spec_from_file_location(
    "glb_publish_manifest",
    Path(__file__).resolve().parent.parent / "scripts/glb_publish_manifest.py",
)
glb_publish_manifest = importlib.util.module_from_spec(_SPEC)
sys.modules["glb_publish_manifest"] = glb_publish_manifest
_SPEC.loader.exec_module(glb_publish_manifest)


def row(tmp_path, sku="sg-001", **kwargs):
    path = tmp_path / f"{sku}.glb"
    path.write_bytes(write_glb({"asset": {"version": "2.0"}}, b""))
    return {"sku": sku, "glb": str(path), "verdict": "pass", **kwargs}


def test_candidate_binds_current_bytes_and_registry(tmp_path):
    source = row(tmp_path, color_delta_e=7.3, master="m.webp")
    manifest = glb_publish_manifest.build_publish_manifest([source])
    entry = manifest["entries"][0]
    assert entry["glb_bytes"] == Path(source["glb"]).stat().st_size
    assert entry["glb_sha256"] == hashlib.sha256(Path(source["glb"]).read_bytes()).hexdigest()
    assert len(entry["registry_sha256"]) == 64
    assert entry["qc_binding"] == "BLOCKED"
    assert entry["product_fidelity"] == "NOT RUN"
    assert entry["creative_approval"] == "BLOCKED"
    assert entry["publication_authorized"] is False
    assert manifest["publication_authorized"] is False
    assert manifest["schema"] == "skyyrose.glb-candidates.v2"
    assert entry["color_delta_e"] == 7.3
    assert entry["master"] == "m.webp"
    assert "ship-cleared" not in manifest["note"].lower()


def test_bound_triage_does_not_grant_approval(tmp_path):
    source = row(tmp_path)
    source["glb_sha256"] = hashlib.sha256(Path(source["glb"]).read_bytes()).hexdigest()
    entry = glb_publish_manifest.build_publish_manifest([source])["entries"][0]
    assert entry["qc_binding"] == "PASS"
    assert entry["creative_approval"] == "BLOCKED"
    assert not entry["publication_authorized"]


def test_missing_asset_is_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        glb_publish_manifest.build_publish_manifest(
            [{"sku": "sg-002", "glb": str(tmp_path / "missing.glb"), "verdict": "pass"}]
        )


def test_invalid_container_is_error(tmp_path):
    source = row(tmp_path)
    Path(source["glb"]).write_bytes(b"glTF" * 100)
    with pytest.raises(GlbFormatError):
        glb_publish_manifest.build_publish_manifest([source])


def test_external_asset_is_error(tmp_path):
    source = row(tmp_path)
    Path(source["glb"]).write_bytes(
        write_glb({"images": [{"uri": "https://example.invalid/texture"}]}, b"")
    )
    with pytest.raises(GlbFormatError, match="embedded resources required"):
        glb_publish_manifest.build_publish_manifest([source])


def test_stale_hash_is_error(tmp_path):
    with pytest.raises(ValueError, match="Stale QC"):
        glb_publish_manifest.build_publish_manifest([row(tmp_path, glb_sha256="0" * 64)])


def test_duplicate_and_unknown_skus_are_errors(tmp_path):
    source = row(tmp_path)
    with pytest.raises(ValueError, match="Duplicate"):
        glb_publish_manifest.build_publish_manifest([source, source])
    with pytest.raises(KeyError):
        glb_publish_manifest.build_publish_manifest([row(tmp_path, sku="unknown-product")])


def test_failed_triage_rows_do_not_touch_files_or_registry():
    manifest = glb_publish_manifest.build_publish_manifest(
        [{"sku": "unknown-product", "glb": "missing", "verdict": "fail"}]
    )
    assert manifest["entries"] == []
    assert manifest["summary"]["count"] == 0


def test_changed_product_source_identity_is_rejected(tmp_path, monkeypatch):
    original = glb_publish_manifest.get_product

    def changed(sku):
        product = original(sku)
        product["provenance"]["sources"]["registry"]["sha256"] = "0" * 16
        return product

    monkeypatch.setattr(glb_publish_manifest, "get_product", changed)
    with pytest.raises(ValueError, match="Registry changed"):
        glb_publish_manifest.build_publish_manifest([row(tmp_path)])
