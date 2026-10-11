"""Nano Banana resolves repository paths through skyyrose.core.paths.

Scripts batch 4A: the WordPress products directory, catalog path and repository
root come from the canonical anchors instead of per-module literals.
"""

from __future__ import annotations

import inspect
from pathlib import Path

import nano_banana._validate_layer1 as validate_layer1
import nano_banana._validate_pipeline_multi_sku as validate_multi
from nano_banana import catalog, source_map

from skyyrose.core import paths
from skyyrose.core.catalog_loader import CATALOG_CSV

SCRIPTS = Path(catalog.__file__).resolve().parent
WP_PRODUCTS_LITERAL = "wordpress-theme/skyyrose-flagship/assets/images/products"


def test_catalog_uses_canonical_anchors():
    assert catalog.PROJECT_ROOT == paths.REPO_ROOT
    assert catalog.PRODUCTS_DIR == paths.WP_PRODUCTS_DIR
    assert catalog.CATALOG_CSV == CATALOG_CSV


def test_source_map_uses_canonical_anchors():
    assert source_map.PROJECT_ROOT == paths.REPO_ROOT
    assert source_map.PRODUCTS_DIR == paths.WP_PRODUCTS_DIR


def test_validation_resolver_follows_the_canonical_products_layout(monkeypatch, tmp_path):
    """The multi-SKU resolver takes the products layout from WP_PRODUCTS_DIR under its REPO."""
    moved = tmp_path / "moved" / "products"
    moved.mkdir(parents=True)
    (moved / "br-001.png").write_bytes(b"fixture")
    monkeypatch.setattr(validate_multi, "REPO", tmp_path)
    monkeypatch.setattr(paths, "WP_PRODUCTS_DIR", paths.REPO_ROOT / "moved" / "products")
    resolved = validate_multi._resolve_source_image("br-001", "", "br-001.png")
    assert resolved == moved / "br-001.png"


def test_no_module_spells_out_the_products_dir():
    for module in (catalog, source_map, validate_layer1, validate_multi):
        # Module docstrings may describe the layout; only code must not hardcode it.
        source = inspect.getsource(module).replace(module.__doc__ or "", "")
        for literal in (WP_PRODUCTS_LITERAL, '"wordpress-theme" / "skyyrose-flagship"'):
            assert literal not in source, f"{module.__name__} hardcodes {literal}"
