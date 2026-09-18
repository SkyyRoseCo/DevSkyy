import json
from pathlib import Path

import pytest

DATA = Path(__file__).resolve().parents[2] / "wordpress-theme/skyyrose-flagship/data"
SCHEMA = DATA / "collections/identity.schema.json"


def test_schema_is_valid_jsonschema():
    import jsonschema

    schema = json.loads(SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)  # raises if schema itself is malformed
    assert schema["required"]  # has required keys


SLUGS = ["black-rose", "love-hurts", "signature", "kids-capsule"]
EXPECTED_PALETTE = {
    "black-rose": {"black", "white", "silver", "accent", "accent_dark", "secondary", "bg", "text"},
    "love-hurts": {
        "red",
        "red_dark",
        "white",
        "black",
        "accent",
        "accent_dark",
        "secondary",
        "bg",
        "text",
    },
    "signature": {"gold", "rose_gold", "accent", "accent_dark", "secondary", "bg", "text"},
    "kids-capsule": {"gold", "rose_gold", "accent", "accent_dark", "secondary", "bg", "text"},
}
# Canon pins — founder typography overhaul 2026-07-10; bespoke faces landed
# 2026-07-11 (13c61beda): BR Pacifico -> SkyyRose Black Rose Script,
# LH Kaushan Script (interim) -> SkyyRose Love Hurts Graffiti.
SCRIPT_FONT = {
    "black-rose": "SkyyRose Black Rose Script",
    "love-hurts": "SkyyRose Love Hurts Graffiti",
    "signature": "Pinyon Script",
    "kids-capsule": "Grand Hotel",
}


@pytest.mark.parametrize("slug", SLUGS)
def test_identity_validates_and_matches_canon(slug):
    import jsonschema

    schema = json.loads(SCHEMA.read_text())
    registry = json.loads((DATA / "logo-registry.json").read_text())
    ident = registry["collections"][slug]
    jsonschema.validate(ident, schema)
    assert ident["slug"] == slug
    assert ident["key"] == slug.replace("-", "_")
    assert EXPECTED_PALETTE[slug].issubset(set(ident["palette"]))
    assert ident["fonts"]["script"]["family"] == SCRIPT_FONT[slug]
    assert ident["fonts"]["caps"]["family"] == "Cinzel"
    assert ident["fonts"]["body"]["family"] == "Hanken Grotesk"


import sys

sys.path.insert(0, str(DATA))
import sot_common  # noqa: E402


def test_slug_to_key():
    assert sot_common.slug_to_key("black-rose") == "black_rose"
    assert sot_common.slug_to_key("signature") == "signature"


def test_load_identity_all_four():
    idents = sot_common.load_identity()
    assert set(idents) == set(SLUGS)
    assert idents["signature"]["fonts"]["script"]["family"] == "Pinyon Script"


def test_load_identity_rejects_malformed(tmp_path, monkeypatch):
    registry = tmp_path / "logo-registry.json"
    registry.write_text('{"collections": {"black-rose": {"slug": "black-rose"}}}')
    monkeypatch.setattr(sot_common, "LOGO_REG", registry)
    with pytest.raises(sot_common.IdentityError, match="collections.black-rose"):
        sot_common.load_identity()


def test_load_identity_rejects_a_slug_that_disagrees_with_its_key(tmp_path, monkeypatch):
    ident = json.loads((DATA / "logo-registry.json").read_text())["collections"]["signature"]
    registry = tmp_path / "logo-registry.json"
    registry.write_text(json.dumps({"collections": {"black-rose": ident}}))
    monkeypatch.setattr(sot_common, "LOGO_REG", registry)
    with pytest.raises(sot_common.IdentityError, match="!= key 'black-rose'"):
        sot_common.load_identity()


def test_load_identity_fails_closed_without_a_collections_section(tmp_path, monkeypatch):
    registry = tmp_path / "logo-registry.json"
    registry.write_text('{"products": {}}')
    monkeypatch.setattr(sot_common, "LOGO_REG", registry)
    with pytest.raises(sot_common.IdentityError, match="no collections section"):
        sot_common.load_identity()


def test_resolve_asset_prefers_webp_over_avif(tmp_path, monkeypatch):
    monkeypatch.setattr(sot_common, "ASSETS", tmp_path)
    (tmp_path / "x.avif").write_bytes(b"a")
    (tmp_path / "x.webp").write_bytes(b"w")
    assert sot_common.resolve_asset("x").endswith("x.webp")  # IMG_EXTS preference, not alphabetical


def test_resolve_asset_exact_stem_beats_prefix_sibling(tmp_path, monkeypatch):
    monkeypatch.setattr(sot_common, "ASSETS", tmp_path)
    (tmp_path / "front.webp").write_bytes(b"w")
    (tmp_path / "front-model.webp").write_bytes(b"m")
    # exact stem 'front.webp' must win over the prefix sibling 'front-model.webp'
    assert sot_common.resolve_asset("front").endswith("front.webp")


def test_resolve_asset_prefix_fallback_for_responsive(tmp_path, monkeypatch):
    monkeypatch.setattr(sot_common, "ASSETS", tmp_path)
    (tmp_path / "luxury-480w.webp").write_bytes(b"w")  # responsive sibling, no exact base.ext
    assert sot_common.resolve_asset("luxury").endswith("luxury-480w.webp")


def test_load_json_unreadable_path_raises_identity_error(tmp_path):
    # a directory (not a file) triggers OSError, which must surface as IdentityError
    with pytest.raises(sot_common.IdentityError):
        sot_common._load_json(tmp_path)
