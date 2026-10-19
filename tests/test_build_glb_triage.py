"""Tests for scripts/build_glb_triage.py — pure generator, no network, no real renders."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "build_glb_triage",
    Path(__file__).resolve().parent.parent / "scripts" / "build_glb_triage.py",
)
build_glb_triage = importlib.util.module_from_spec(_SPEC)
sys.modules["build_glb_triage"] = build_glb_triage
_SPEC.loader.exec_module(build_glb_triage)


def _touch(path: Path, data: bytes = b"x") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


@pytest.fixture
def fake_repo(tmp_path, monkeypatch):
    """Repo tree: three GLBs; founder photos for two SKUs; a site render for one; registry of three."""
    web = tmp_path / "renders" / "3d" / "web-v2"
    web.mkdir(parents=True)
    (web / "br-006.glb").write_bytes(b"glTF-fake-bomber")
    (web / "br-010.glb").write_bytes(b"glTF-fake-basketball")
    (web / "lh-006.glb").write_bytes(b"glTF-fake-joggers")

    photos = tmp_path / build_glb_triage.SOURCE_PHOTOS_REL
    # br-006: back + techflat + front -> front must win.
    _touch(photos / "black-rose" / "br-006-sherpa-jacket-back.jpeg")
    _touch(photos / "black-rose" / "br-006-techflat-sherpa.jpeg")
    _touch(photos / "black-rose" / "br-006-sherpa-jacket-front.jpeg")
    # br-010: techflat only.
    _touch(photos / "black-rose" / "br-010-techflat-basketball.jpeg")
    # lh-006: nothing. A neighbouring lh-002 file must NOT be picked up by prefix.
    _touch(photos / "love-hurts" / "lh-002-joggers-white.jpeg")
    # Non-photo noise under a matching prefix is ignored.
    _touch(photos / "black-rose" / "br-010-notes.txt")

    site_rel = "assets/images/products/br-006-onmodel.webp"
    _touch(tmp_path / build_glb_triage.THEME_REL / site_rel, b"RIFFfakewebp")

    registry = {
        "products": {
            "br-006": {"catalog": {"sku": "br-006", "name": "The Bomber Sherpa"}},
            "br-010": {"catalog": {"sku": "br-010", "name": "The Bay Basketball Jersey"}},
            "lh-006": {"catalog": {"sku": "lh-006", "name": "Love Hurts Joggers White"}},
        }
    }
    monkeypatch.setattr(build_glb_triage, "load_registry", lambda: registry)
    monkeypatch.setattr(
        build_glb_triage.sot_images,
        "resolve_image",
        lambda sku, role="front": site_rel if sku == "br-006" else None,
    )
    return tmp_path


def test_reference_precedence_front_over_techflat_over_variant(tmp_path):
    photos = tmp_path / "src"
    _touch(photos / "a" / "sg-001-shorts-back.jpeg")
    assert build_glb_triage.resolve_reference("sg-001", photos)[1] == "back"
    _touch(photos / "a" / "sg-001-shorts-wearer-left.jpeg")
    assert build_glb_triage.resolve_reference("sg-001", photos)[1] == "variant"
    _touch(photos / "a" / "sg-001-techflat-shorts.jpeg")
    path, rule = build_glb_triage.resolve_reference("sg-001", photos)
    assert (rule, path.name) == ("techflat", "sg-001-techflat-shorts.jpeg")
    _touch(photos / "b" / "sg-001-shorts-front.jpeg")
    path, rule = build_glb_triage.resolve_reference("sg-001", photos)
    assert (rule, path.name) == ("front", "sg-001-shorts-front.jpeg")
    # A techflat whose name says "front" is still a techflat, never rule "front".
    _touch(photos / "c" / "sg-002-techflat-allover-front.jpg")
    assert build_glb_triage.resolve_reference("sg-002", photos)[1] == "techflat"
    # Prefix is exact: sg-0011 must not match sg-001, and a missing dir is "none".
    _touch(photos / "d" / "sg-0011-front.jpeg")
    assert build_glb_triage.resolve_reference("sg-0011", photos)[1] == "front"
    assert build_glb_triage.resolve_reference("zz-999", photos) == (None, "none")
    assert build_glb_triage.resolve_reference("sg-001", tmp_path / "missing") == (None, "none")


def test_collect_entries_binds_real_reference_site_image_and_sha(fake_repo):
    entries = build_glb_triage.collect_entries(fake_repo / "renders/3d/web-v2", fake_repo)
    by_sku = {e["sku"]: e for e in entries}
    assert list(by_sku) == ["br-006", "br-010", "lh-006"]

    bomber = by_sku["br-006"]
    assert bomber["name"] == "The Bomber Sherpa"
    assert bomber["reference_rule"] == "front"
    assert (
        bomber["reference_file"]
        == "assets/products/source-photos/black-rose/br-006-sherpa-jacket-front.jpeg"
    )
    assert (
        bomber["site_image"]
        == f"/{build_glb_triage.THEME_REL}/assets/images/products/br-006-onmodel.webp"
    )
    assert bomber["glb_sha256"] == hashlib.sha256(b"glTF-fake-bomber").hexdigest()

    basketball = by_sku["br-010"]
    assert basketball["reference_rule"] == "techflat"
    assert basketball["reference_file"].endswith("br-010-techflat-basketball.jpeg")
    assert basketball["site_image"] is None

    joggers = by_sku["lh-006"]
    assert joggers["reference_file"] is None
    assert joggers["reference_rule"] == "none"
    assert "lh-002-joggers-white.jpeg" in joggers["open_question"]


def test_missing_reference_blocks_controls_and_never_substitutes(fake_repo):
    entries = build_glb_triage.collect_entries(fake_repo / "renders/3d/web-v2", fake_repo)
    page = build_glb_triage.render_page(entries, "2026-09-17T00:00:00+00:00")

    lh = page.split('id="sku-lh-006"')[1].split("</section>")[0]
    assert build_glb_triage.NO_REFERENCE_NOTICE in lh
    assert 'name="verdict-lh-006"' not in lh
    assert "<textarea" not in lh
    assert "triage-blocked" in lh
    assert "lh-002-joggers-white.jpeg" in lh  # named in the open question only...
    assert (
        '<img src="/assets/products/source-photos/love-hurts/lh-002-joggers-white.jpeg"' not in page
    )  # ...never shown

    # SKUs with a reference keep their controls and say what they are judged against.
    br = page.split('id="sku-br-006"')[1].split("</section>")[0]
    assert 'name="verdict-br-006"' in br
    assert "br-006-sherpa-jacket-front.jpeg" in br
    assert "rule: <code>front</code>" in br
    assert 'href="/assets/products/source-photos/black-rose/br-006-sherpa-jacket-front.jpeg"' in br
    assert "Current site image — generated, not the reference" in br
    assert "1 blocked (no real reference)" in page


def test_render_page_serves_from_repo_root_and_embeds_reference_in_data(fake_repo):
    entries = build_glb_triage.collect_entries(fake_repo / "renders/3d/web-v2", fake_repo)
    page = build_glb_triage.render_page(entries, "2026-09-17T00:00:00+00:00")

    assert 'data-model="/renders/3d/web-v2/br-006.glb"' in page
    assert f'src="{build_glb_triage.VIEWER_JS}"' in page
    assert build_glb_triage.LIB_BASE in page
    assert (
        page.count('class="button view-3d-model"') == 3
    )  # viewer offered on every model, blocked or not
    assert 'data-product-name="The Bomber Sherpa"' in page
    assert page.count('<section class="triage-sku') == 3
    assert 'id="export-verdicts"' in page

    data = json.loads(
        page.split('<script id="triage-data" type="application/json">')[1].split("</script>")[0]
    )
    by_sku = {d["sku"]: d for d in data}
    assert set(by_sku) == {"br-006", "br-010", "lh-006"}
    assert all(
        {"sku", "name", "glb_path", "glb_sha256", "reference_file", "reference_rule"} <= set(d)
        for d in data
    )
    assert by_sku["br-006"]["reference_rule"] == "front"
    assert by_sku["lh-006"]["reference_file"] is None


def test_coverage_table_and_build_fail_closed(fake_repo, tmp_path):
    out = tmp_path / "out" / "glb-triage.html"
    entries = build_glb_triage.build(fake_repo / "renders/3d/web-v2", out, fake_repo)
    assert out.is_file()
    table = build_glb_triage.coverage_table(entries)
    assert "front=1" in table and "techflat=1" in table and "none=1" in table

    with pytest.raises(FileNotFoundError):
        build_glb_triage.collect_entries(fake_repo / "renders/3d/nope", fake_repo)
    empty = fake_repo / "renders/3d/empty"
    empty.mkdir()
    with pytest.raises(FileNotFoundError):
        build_glb_triage.collect_entries(empty, fake_repo)


def test_product_names_with_ampersand_and_apostrophe_render_once_escaped(tmp_path, monkeypatch):
    """Double-escaping printed literal &#x27; in 7 of 33 real product names."""
    section = build_glb_triage._section(
        {
            "sku": "sg-001",
            "name": "The Bridge Series 'Stay Golden' Shirt & Shorts",
            "glb_path": "renders/3d/web-v2/sg-001.glb",
            "glb_bytes": 1_770_000,
            "glb_sha256": "a" * 64,
            "reference_file": "assets/products/source-photos/signature/sg-001-front.jpeg",
            "reference_rule": "front",
            "site_image": None,
            "qc_blocked": False,
        }
    )
    assert "&amp;#x27;" not in section and "&amp;amp;" not in section
    assert "<h2>The Bridge Series &#x27;Stay Golden&#x27; Shirt &amp; Shorts</h2>" in section
