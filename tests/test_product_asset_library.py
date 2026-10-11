"""Offline regression evidence for registry-based, non-destructive image exports."""

import pytest
from PIL import Image

from scripts import build_product_asset_library as library
from scripts import scaffold_sku_asset_folders as scaffold
from skyyrose.core.product import all_skus, get_product
from skyyrose.core.product_registry import load_registry


def test_export_preserves_original_and_aspect_ratio(tmp_path):
    source = tmp_path / "source.png"
    Image.new("RGB", (300, 150), (110, 40, 90)).save(source)
    original = source.read_bytes()
    target = tmp_path / "export.png"
    policy = {"width": 2400, "height": 2400, "padding": 120}
    info = library.export_image(source, target, policy, False)
    assert source.read_bytes() == original
    assert (info["scaled_width"], info["scaled_height"]) == (2160, 1080)
    with Image.open(target) as image:
        assert image.size == (2400, 2400)
        assert image.getpixel((1200, 1200)) == (110, 40, 90, 255)
        assert image.getpixel((0, 0))[3] == 0
    assert library.export_image(source, target, policy, True) == info
    # A changed padding policy must not silently reuse a stale derivative.
    with pytest.raises(ValueError, match="Incorrect export"):
        library.export_image(source, target, {**policy, "padding": 200}, True)


def test_library_refuses_path_escape_and_source_replacement(tmp_path):
    with pytest.raises(ValueError, match="escapes"):
        library.inside(tmp_path, "../outside.png")
    source = tmp_path / "source.png"
    source.write_bytes(b"original")
    occupied = tmp_path / "occupied.png"
    occupied.write_bytes(b"unrelated")
    with pytest.raises(ValueError, match="conflicting"):
        library.link_source(source, occupied, False)
    assert occupied.read_bytes() == b"unrelated"


def test_all_33_products_have_registry_library_entries():
    skus = all_skus()
    assert len(skus) == 33
    for sku in skus:
        product = get_product(sku)
        assert product["asset_library"]["directory"] == (
            f"assets/products/catalog/{product['collection']}/{sku}"
        )
        for source in product["asset_library"]["sources"]:
            assert library.digest(library.ROOT / source["path"]) == source["sha256"]


def test_technical_sources_do_not_guess_from_filenames(monkeypatch, tmp_path):
    # Deliberately misleading files must never fill absent registry views.
    (tmp_path / "sg-007-techflat-back.jpeg").write_bytes(b"front mislabeled as rear")
    monkeypatch.setattr(scaffold, "PRODUCT_REFERENCES_DIR", tmp_path)
    assert scaffold._find_real_back_source("sg-007") is None
    product = get_product("sg-002")
    assert scaffold._find_real_back_source("sg-002") == (
        scaffold._REPO_ROOT / product["render_sources"]["techflat_back"]
    )


def test_export_policy_matches_founder_choice():
    policy = load_registry()["authority_contract"]["product_image_export"]
    assert (policy["width"], policy["height"], policy["padding"]) == (2400, 2400, 120)
    assert policy["format"] == "PNG"


def test_founder_fit_and_care_reach_csv_without_inventing_materials():
    from skyyrose.core.product_registry import catalog_rows

    rows = {row["sku"]: row for row in catalog_rows()}
    assert len(rows) == 33
    # Jerseys combine two founder statements (2026-09-29 + 2026-09-21); each
    # clause must still trace to its own FOUNDER_CONFIRMED dossier paragraph.
    jerseys = {"br-003", "br-008", "br-009", "br-010", "br-011", "br-012", "br-014", "br-015"}
    for sku, row in rows.items():
        product = get_product(sku)
        dossier = product["dossier"]["full_text"]
        assert "gender neutral relaxed fit" in dossier
        if sku in jerseys:
            assert (
                row["fit"] == "Gender neutral relaxed fit; true to size, relaxed through the body."
            )
            assert "True to size, relaxed through the body." in dossier
            assert 'verbatim: "all jerseys true to size, relaxed through the body"' in dossier
        else:
            assert row["fit"] == "gender neutral relaxed fit"
        if sku == "lh-005":
            assert row["care_instructions"] == ""
        else:
            assert "Tumble dry on low heat." in row["care_instructions"]
            assert row["care_instructions"] in product["dossier"]["full_text"]
        # This review must not convert material hypotheses to founder facts.
        assert product["garment"]["materials"]["source"] == "derived_from_dossier"


def test_signature_sherpa_does_not_use_black_rose_bomber_source():
    product = get_product("sg-009")
    assert (
        product["render_sources"]["front"] == "assets/products/references/sg-009-sherpa-front.jpeg"
    )
    paths = {source["path"] for source in library.product_sources(product)}
    assert (
        "wordpress-theme/skyyrose-flagship/assets/images/products/sherpa-jacket-front.jpg"
        not in paths
    )
