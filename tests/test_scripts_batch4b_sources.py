"""Batch-4B scripts read product facts through get_product and paths through skyyrose.core.paths.

Covers batch_flux_collections, build_asset_manifest, generate_product_embeddings,
generate_stage3_prompts, flux_lora/upload and tripo_dispatch. Every test is offline:
no API client is built and the CLIP embedder is faked.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from skyyrose.core import paths

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = [
    "scripts/batch_flux_collections.py",
    "scripts/build_asset_manifest.py",
    "scripts/build_brand_centroid.py",
    "scripts/generate_product_embeddings.py",
    "scripts/generate_stage3_prompts.py",
    "scripts/flux_lora/upload.py",
    "scripts/tripo_dispatch.py",
]

FAKE_REGISTRY = {"products": {"zz-002": {}, "zz-001": {}}}  # insertion order is catalog order
FAKE_CATALOG = {
    "zz-002": {
        "sku": "zz-002",
        "name": "Registry Only Two",
        "collection": "signature",
        "published": "1",
        "dossier_slug": "zz-two",
        "garment_type_lock": "tee",
    },
    "zz-001": {
        "sku": "zz-001",
        "name": "Registry Only One",
        "collection": "love-hurts",
        "published": "1",
        "dossier_slug": "zz-one",
        "garment_type_lock": "hoodie",
    },
}


def _fake_get_product(sku):
    return {
        "sku": sku,
        "catalog": dict(FAKE_CATALOG[sku]),
        "images": {"front": {"path": f"assets/images/products/{sku}-front.webp"}},
    }


def _use_fake_registry(monkeypatch, module, *, attr_level=True):
    if attr_level:
        monkeypatch.setattr(module, "load_registry", lambda: FAKE_REGISTRY)
        monkeypatch.setattr(module, "get_product", _fake_get_product)
    else:  # the script imports inside a function
        import skyyrose.core.product as product

        monkeypatch.setattr(product, "load_registry", lambda: FAKE_REGISTRY)
        monkeypatch.setattr(product, "get_product", _fake_get_product)


@pytest.mark.parametrize("script", SCRIPTS)
def test_no_hardcoded_home_paths(script):
    assert "/Users/" not in (ROOT / script).read_text(encoding="utf-8")


def test_scripts_no_longer_read_the_catalog_csv():
    for script in SCRIPTS:
        text = (ROOT / script).read_text(encoding="utf-8")
        assert "read_catalog_rows" not in text, script
        assert "csv.DictReader" not in text, script


# ── batch_flux_collections ────────────────────────────────────────────


def test_batch_flux_manifest_follows_registry(monkeypatch):
    from scripts import batch_flux_collections as flux

    _use_fake_registry(monkeypatch, flux)
    monkeypatch.setattr(flux, "resolve_image", lambda sku, role: f"{role}/{sku}.webp")
    items = flux._load_manifest({"love-hurts", "signature"}, set())
    assert [i["sku"] for i in items] == ["zz-002", "zz-001"]
    assert items[0]["name"] == "Registry Only Two"
    assert items[1]["front_path"] == paths.THEME_ROOT / "packshot/zz-001.webp"
    assert [i["sku"] for i in flux._load_manifest({"signature"}, set())] == ["zz-002"]


def test_batch_flux_assets_root_is_the_theme():
    from scripts import batch_flux_collections as flux

    assert flux.ASSETS_ROOT == paths.THEME_ROOT


# ── build_asset_manifest ──────────────────────────────────────────────


def test_asset_manifest_catalog_rows_follow_registry(monkeypatch):
    from scripts import build_asset_manifest as manifest

    _use_fake_registry(monkeypatch, manifest)
    rows = manifest._catalog_rows()
    assert list(rows) == ["zz-002", "zz-001"]
    assert rows["zz-001"] == {
        "name": "Registry Only One",
        "collection": "love-hurts",
        "garment_type": "hoodie",
    }


# ── generate_product_embeddings ───────────────────────────────────────


class _Vec(list):
    def tolist(self):
        return list(self)


def test_embeddings_follow_registry_names_and_images(monkeypatch, tmp_path):
    from scripts import generate_product_embeddings as embeddings

    _use_fake_registry(monkeypatch, embeddings)
    theme = tmp_path / "theme"
    for sku in FAKE_CATALOG:
        image = theme / f"assets/images/products/{sku}-front.webp"
        image.parent.mkdir(parents=True, exist_ok=True)
        image.write_bytes(b"x")
    embedded: list[Path] = []

    def fake_embed(path: Path) -> _Vec:
        embedded.append(path)
        return _Vec([1.0])

    monkeypatch.setattr(embeddings, "THEME_ROOT", theme)
    monkeypatch.setattr(embeddings.clip_embedder, "embed_image", fake_embed)
    monkeypatch.setattr(embeddings, "OUTPUT_PATH", tmp_path / "out.json")
    monkeypatch.setattr(embeddings, "ROOT", tmp_path)
    assert embeddings.main() == 0
    products = json.loads((tmp_path / "out.json").read_text())["products"]
    assert list(products) == ["zz-002", "zz-001"]
    assert products["zz-002"]["name"] == "Registry Only Two"
    assert embedded[0] == theme / "assets/images/products/zz-002-front.webp"


def test_embeddings_output_path_is_anchored():
    from scripts import generate_product_embeddings as embeddings

    assert embeddings.OUTPUT_PATH == paths.THEME_ROOT / "data" / "product-embeddings.json"


# ── generate_stage3_prompts / flux_lora upload ─────────────────────────


def test_stage3_reads_the_canonical_dossier_dir():
    from scripts import generate_stage3_prompts as stage3

    assert stage3.DOSSIER_DIR == paths.DOSSIERS_DIR


def test_flux_lora_env_file_is_the_repo_root():
    from scripts.flux_lora import upload

    assert Path(upload._ENV_HF) == paths.REPO_ROOT / ".env.hf"


# ── tripo_dispatch ────────────────────────────────────────────────────


def test_tripo_catalog_follows_registry(monkeypatch):
    from scripts import tripo_dispatch as tripo

    _use_fake_registry(monkeypatch, tripo, attr_level=False)
    rows = tripo.load_catalog()
    assert [r["sku"] for r in rows] == ["zz-002", "zz-001"]
    assert rows[1]["name"] == "Registry Only One"


def test_tripo_paths_are_anchored():
    from scripts import tripo_dispatch as tripo

    assert tripo.THEME_ROOT == paths.THEME_ROOT
    assert tripo.DOSSIER_DIR == paths.DOSSIERS_DIR
    assert tripo.resolve_source_image({"render_source_override": "x.webp"}) == (
        paths.WP_PRODUCTS_DIR / "x.webp"
    )


# The bug-096 hallucination gate: which real SKUs Tripo multiview may receive.
# A change here must be a deliberate catalog decision, never a refactor side effect.
TRIPO_NOT_TECH_FLAT = {"sg-011", "sg-012"}


def test_tripo_gate_blocks_exactly_the_pinned_skus():
    from scripts import tripo_dispatch as tripo
    from skyyrose.core.product import all_skus

    approved, blocked = tripo.classify_skus(tripo.load_catalog())
    reasons = {row["sku"]: why.split(" —")[0] for row, why in blocked}
    assert approved == []
    assert set(reasons) == set(all_skus())
    assert {s for s, r in reasons.items() if r == "NOT A TECH-FLAT"} == TRIPO_NOT_TECH_FLAT
    assert {s for s, r in reasons.items() if r == "BRANDED"} == set(all_skus()) - (
        TRIPO_NOT_TECH_FLAT
    )
