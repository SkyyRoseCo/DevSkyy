"""Scripts use current library APIs and the canonical path anchors.

Covers the first scripts refactor batch: Pillow's deprecated
``Image.getdata`` (removed in Pillow 14) and path literals that duplicated
``skyyrose.core.paths`` / ``skyyrose.core.catalog_loader`` anchors.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import types
import warnings
from pathlib import Path

import pytest
from PIL import Image

from skyyrose.core import paths
from skyyrose.core.catalog_loader import CATALOG_CSV

ROOT = Path(__file__).resolve().parent.parent


def _matte_result(monkeypatch, tmp_path, opaque_fraction: float) -> str | None:
    """Run the matte check against a fake rembg that returns a known alpha."""
    from scripts import source_product_photos

    width, height = 10, 10
    matte = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    for index in range(round(width * height * opaque_fraction)):
        matte.putpixel((index % width, index // width), (255, 255, 255, 255))
    monkeypatch.setitem(sys.modules, "rembg", types.SimpleNamespace(remove=lambda _: matte))
    photo = tmp_path / "photo.png"
    photo.write_bytes(b"fixture")
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        return source_product_photos._try_bria_matte(photo)


def test_matte_check_accepts_isolated_subject_without_deprecations(monkeypatch, tmp_path):
    assert _matte_result(monkeypatch, tmp_path, 0.5) is None


@pytest.mark.parametrize(("fraction", "phrase"), [(0.0, "near-empty"), (1.0, "near-full")])
def test_matte_check_rejects_empty_and_full_alpha(monkeypatch, tmp_path, fraction, phrase):
    assert phrase in _matte_result(monkeypatch, tmp_path, fraction)


def test_openai_feed_reads_the_canonical_catalog_path():
    from scripts.openai_feed.catalog import DEFAULT_CATALOG_PATH

    assert DEFAULT_CATALOG_PATH == CATALOG_CSV


def test_catalog_ml_audit_uses_canonical_theme_paths():
    from scripts import catalog_ml_audit

    assert catalog_ml_audit.PRODUCTS_DIR == paths.WP_PRODUCTS_DIR
    assert catalog_ml_audit.EMBEDDINGS_PATH == paths.THEME_ROOT / "data" / "product-embeddings.json"


def test_product_asset_library_uses_canonical_asset_root():
    from scripts import build_product_asset_library

    assert build_product_asset_library.CATALOG_DIR == paths.PRODUCT_ASSETS / "catalog"
    assert (
        build_product_asset_library.REVIEW_DIR == paths.PRODUCT_ASSETS / "outside-verified-products"
    )


@pytest.mark.skipif(shutil.which("node") is None, reason="node is required for the .mjs check")
def test_live_verifier_finds_frontend_without_a_hardcoded_home():
    """With no spec the verifier stops before any browser or network use."""
    script = ROOT / "scripts" / "verify-live-playwright.mjs"
    assert "/Users/" not in script.read_text(encoding="utf-8")
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"}
    result = subprocess.run(
        ["node", str(script)], capture_output=True, text=True, env=env, timeout=60
    )
    if result.returncode == 3:
        # Playwright is not installed under frontend/: the message names the root it tried.
        assert f"not resolvable from {ROOT / 'frontend'}/" in result.stderr
    else:
        # Playwright resolved from the derived root, so the run reached spec loading.
        assert result.returncode != 0
        assert "No spec" in result.stderr
