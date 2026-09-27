"""Offline storefront parity against the same registry used by Python consumers."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from skyyrose.core.product_registry import catalog_rows


@pytest.mark.skipif(shutil.which("php") is None, reason="PHP runtime unavailable")
def test_storefront_garment_and_image_fields_match_registry():
    root = Path(__file__).resolve().parents[1]
    script = r"""
    define('ABSPATH', '/offline/');
    set_error_handler(function($level, $message) { throw new Exception($message); });
    function get_theme_file_path($path) {
        return getcwd() . '/wordpress-theme/skyyrose-flagship/' . $path;
    }
    function wp_json_encode($value) { return json_encode($value); }
    require get_theme_file_path('inc/product-catalog.php');
    echo json_encode(skyyrose_get_product_catalog());
    """
    result = subprocess.run(
        ["php", "-r", script], cwd=root, capture_output=True, text=True, check=True
    )
    assert not result.stderr
    actual = json.loads(result.stdout)
    expected = {row["sku"]: row for row in catalog_rows()}
    assert actual.keys() == expected.keys()
    fields = (
        "color",
        "sizes",
        "fit",
        "materials",
        "features",
        "image",
        "front_model_image",
        "back_image",
        "back_model_image",
    )
    for sku, row in expected.items():
        for field in fields:
            assert actual[sku][field] == row[field], (sku, field)
        assert json.loads(actual[sku]["sizing_references"]) == json.loads(row["sizing_references"])
