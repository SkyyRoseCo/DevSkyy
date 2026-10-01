"""Offline projection regressions: current identity cannot reapprove an old asset."""

import copy
import importlib.util
from pathlib import Path

import pytest

from skyyrose.core.product import get_product

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def builder(monkeypatch):
    path = (
        ROOT / "wordpress-theme/skyyrose-flagship-2/scripts/build-product-presentation-registry.py"
    )
    spec = importlib.util.spec_from_file_location("integration_glb_projection", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Synthetic media projection isolates acceptance from unrelated source pins.
    manifest = {
        "products": {
            "br-001": {
                "product_hash": "synthetic-media-only",
                "verification": {"proof_level": "SYNTHETIC_TEST"},
            }
        }
    }
    monkeypatch.setattr(module, "load_product_sot", lambda: (manifest, "synthetic-test"))
    monkeypatch.setattr(module, "garment_types", lambda _: {"br-001": "synthetic-test"})
    return module


def test_current_projection_keeps_unapproved_assets_dormant(builder):
    result = builder.build_registry()
    assert result["glb_runtime"]["entries"] == []
    assert result["glb_runtime"]["publication_authorized"] is False
    assert len(result["product_registry_sha256"]) == 64


@pytest.mark.parametrize(
    "binding",
    [
        {},
        {
            "sku": "br-001",
            "publication_authorized": True,
            "registry_sha256": "0" * 64,
            "creative_approval": "FOUNDER_APPROVED",
        },
    ],
)
def test_existing_binding_cannot_be_reapproved_by_current_registry_hash(
    builder, monkeypatch, binding
):
    # Illustrative stale acceptance payload, never a real founder approval.
    record = copy.deepcopy(get_product("br-001"))
    record["asset_library"]["accepted_glb_runtime"] = binding
    monkeypatch.setattr(builder, "get_product", lambda _: record)
    with pytest.raises(ValueError, match="reviewed product-source approval contract"):
        builder.build_registry()
