"""Tests for the all-SKU multi-view media production contract."""

from __future__ import annotations

import pytest

from skyyrose.core import sku_media_contract


@pytest.fixture(autouse=True)
def theme_root(tmp_path, monkeypatch):
    """Isolated theme tree; tests create the asset files a view should find."""
    monkeypatch.setattr(sku_media_contract, "_THEME_ROOT", tmp_path)
    return tmp_path


def _materialize(root, product: dict) -> None:
    for entry in product["images"].values():
        asset = root / entry["path"]
        asset.parent.mkdir(parents=True, exist_ok=True)
        asset.write_bytes(b"x")


def test_required_contract_has_all_founder_required_views() -> None:
    assert [requirement.key for requirement in sku_media_contract.REQUIRED_MEDIA] == [
        "on_model_front",
        "on_model_back",
        "mannequin_front",
        "mannequin_back",
        "render_3d",
    ]


def test_record_requires_explicit_mannequin_and_3d_fields(monkeypatch, theme_root) -> None:
    product = {
        "sku": "br-999",
        "name": "Test Piece",
        "collection": "black-rose",
        "images": {
            "image": {
                "path": "assets/images/products/test-front.png",
                "resolved": "images/products/test-front.png",
            },
            "back_image": {
                "path": "assets/images/products/test-back.png",
                "resolved": "images/products/test-back.png",
            },
            "front_model_image": {
                "path": "assets/images/products/test-onmodel-front.webp",
                "resolved": "images/products/test-onmodel-front.webp",
            },
            "back_model_image": {
                "path": "assets/images/products/test-onmodel-back.webp",
                "resolved": "images/products/test-onmodel-back.webp",
            },
            "mannequin_front_image": {
                "path": "assets/images/products/test-mannequin-front.webp",
                "resolved": "images/products/test-mannequin-front.webp",
            },
            "mannequin_back_image": {
                "path": "assets/images/products/test-mannequin-back.webp",
                "resolved": "images/products/test-mannequin-back.webp",
            },
            "render_3d_image": {
                "path": "assets/images/products/test-render-3d.webp",
                "resolved": "images/products/test-render-3d.webp",
            },
        },
    }
    _materialize(theme_root, product)
    monkeypatch.setattr(sku_media_contract.sot_images, "_index", lambda: {"br-999": product})
    record = sku_media_contract.sku_media_record("br-999")
    assert record is not None
    assert record["complete"] is True
    assert record["views"]["mannequin_front"]["path"].endswith("test-mannequin-front.webp")
    assert record["views"]["render_3d"]["path"].endswith("test-render-3d.webp")
    assert (
        record["views"]["render_3d"]["review_target"] == "renders/sku-media/br-999/render_3d.webp"
    )


def test_missing_views_are_reported_without_packshot_substitution(monkeypatch, theme_root) -> None:
    product = {
        "sku": "lh-999",
        "name": "Test Piece",
        "collection": "love-hurts",
        "images": {
            "image": {
                "path": "assets/images/products/test-front.png",
                "resolved": "images/products/test-front.png",
            },
            "front_model_image": {
                "path": "assets/images/products/test-onmodel-front.webp",
                "resolved": "images/products/test-onmodel-front.webp",
            },
        },
    }
    _materialize(theme_root, product)
    monkeypatch.setattr(sku_media_contract.sot_images, "_index", lambda: {"lh-999": product})
    monkeypatch.setattr(sku_media_contract.sot_images, "all_skus", lambda: ["lh-999"])
    matrix = sku_media_contract.build_media_matrix()
    assert matrix["summary"]["complete_sku_count"] == 0
    assert sku_media_contract.missing_views(matrix) == [
        "lh-999:on_model_back",
        "lh-999:mannequin_front",
        "lh-999:mannequin_back",
        "lh-999:render_3d",
    ]


def test_production_jobs_are_sku_bound_and_promotion_gated(monkeypatch, theme_root) -> None:
    product = {
        "sku": "sig-999",
        "name": "Test Signature Piece",
        "collection": "signature",
        "images": {
            "image": {
                "path": "assets/images/products/test-front.png",
                "resolved": "images/products/test-front.png",
            },
            "back_image": {
                "path": "assets/images/products/test-back.png",
                "resolved": "images/products/test-back.png",
            },
        },
    }
    _materialize(theme_root, product)
    monkeypatch.setattr(sku_media_contract.sot_images, "_index", lambda: {"sig-999": product})
    monkeypatch.setattr(sku_media_contract.sot_images, "all_skus", lambda: ["sig-999"])

    plan = sku_media_contract.build_production_jobs()
    assert plan["summary"] == {"sku_count": 1, "job_count": 5, "missing_only": True}
    front = plan["jobs"][0]
    assert front["id"] == "sig-999:on_model_front"
    assert front["reference_inputs"] == [
        "assets/images/products/test-front.png",
        "assets/images/products/test-back.png",
    ]
    assert front["generation"]["provider"] == "UNASSIGNED"
    assert front["promotion"]["state"] == "blocked_pending_review"
    assert "founder-approved" in front["promotion"]["rule"]
    assert "sku_identity_match" in front["review"]["required_dimensions"]


def test_production_jobs_flag_missing_sku_reference_inputs(monkeypatch, theme_root) -> None:
    product = {"sku": "lh-000", "name": "No References", "collection": "love-hurts", "images": {}}
    _materialize(theme_root, product)
    monkeypatch.setattr(sku_media_contract.sot_images, "_index", lambda: {"lh-000": product})
    monkeypatch.setattr(sku_media_contract.sot_images, "all_skus", lambda: ["lh-000"])

    plan = sku_media_contract.build_production_jobs()
    assert {job["status"] for job in plan["jobs"]} == {"needs_reference"}


def test_path_only_binding_is_ready_when_the_asset_exists(monkeypatch, theme_root) -> None:
    """A registry binding with no stored ``resolved`` must not read as missing."""
    product = {
        "sku": "br-998",
        "images": {"front_model_image": {"path": "assets/images/products/approved-front.webp"}},
    }
    _materialize(theme_root, product)
    monkeypatch.setattr(sku_media_contract.sot_images, "_index", lambda: {"br-998": product})
    record = sku_media_contract.sku_media_record("br-998")
    assert record is not None
    assert record["views"]["on_model_front"]["ready"] is True


def test_stale_resolved_without_the_asset_is_not_ready(monkeypatch) -> None:
    """A stored ``resolved`` is never trusted over the file actually being there."""
    product = {
        "sku": "br-997",
        "images": {
            "front_model_image": {
                "path": "assets/images/products/deleted-front.webp",
                "resolved": "images/products/deleted-front.webp",
            }
        },
    }
    monkeypatch.setattr(sku_media_contract.sot_images, "_index", lambda: {"br-997": product})
    record = sku_media_contract.sku_media_record("br-997")
    assert record is not None
    assert record["views"]["on_model_front"]["ready"] is False
