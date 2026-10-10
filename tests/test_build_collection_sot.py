"""Hermetic unit tests for ``data/build-collection-sot.py``.

``tests/test_collection_sot_guard.py`` covers the generator against the real masters
(document shape, ``serialize`` byte format, committed-file freshness, the validator
guard). This file covers the pure helpers underneath it against a synthetic asset tree
and synthetic masters, so every branch is exercised without depending on real product
data:

  * ``expand_formats`` / ``walk_manifest_entries`` / ``registered_files`` — what counts
    as "registered" for the orphan set-difference.
  * ``build_orphans`` — tree minus registered minus ``known_orphans``.
  * ``imagery_block`` / ``logos_for`` / ``build_collection`` — the per-collection view.
  * ``main --out-dir`` — writes only into the requested directory.

Synthetic masters enter through the ``masters=`` seam, never through the product
loader's internals, so these tests are independent of how products are sourced.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_SCRIPT = _REPO_ROOT / "wordpress-theme" / "skyyrose-flagship" / "data" / "build-collection-sot.py"
_TRACKED_COLLECTIONS = _SCRIPT.parent / "collections"


def _load(mod_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(mod_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)
    return module


# Distinct module name so this never re-executes over the guard test's module entry.
gen = _load("build_collection_sot_unit", _SCRIPT)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _touch(root: Path, rel: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"x")


@pytest.fixture
def assets(tmp_path, monkeypatch) -> Path:
    """A synthetic asset tree bound to BOTH asset roots.

    The generator copies ``ASSETS = sot_common.ASSETS`` at import: ``scan_tree`` and
    ``expand_formats`` read the generator's copy, ``resolve_asset`` reads sot_common's.
    Patching only one would let resolution silently consult the real tree.
    """
    root = tmp_path / "assets"
    root.mkdir()
    monkeypatch.setattr(gen, "ASSETS", root)
    monkeypatch.setattr(gen.sot_common, "ASSETS", root)
    monkeypatch.setattr(gen, "TREE_SCAN_DIRS", ["images", "images/logos"])
    return root


def _ident(slug: str, *, hero: dict | None = None, known_orphans: list[str] | None = None):
    ident = {
        "slug": slug,
        "key": slug.replace("-", "_"),
        "name": slug.title(),
        "story": {"seed": "seed", "doc_ref": "docs/x.md"},
        "palette": {"primary": "#000000"},
        "fonts": {"script": "Test Script"},
        "lockup": {"ref": f"images/lockups/{slug}-lockup"},
    }
    if hero is not None:
        ident["imagery"] = {"hero": hero}
    if known_orphans is not None:
        ident["known_orphans"] = known_orphans
    return ident


def _product(sku: str, images: dict[str, tuple[str, str | None]]) -> dict:
    return {
        "sku": sku,
        "name": f"Product {sku}",
        "images": {col: {"path": p, "resolved": r} for col, (p, r) in images.items()},
    }


# ---------------------------------------------------------------------------
# expand_formats / walk_manifest_entries / manifest_entry
# ---------------------------------------------------------------------------


class TestExpandFormats:
    def test_extension_dot_and_width_token_dash(self, assets):
        _touch(assets, "images/hero.webp")
        _touch(assets, "images/hero.avif")
        _touch(assets, "images/hero-480w.webp")
        entry = {"path": "images/hero", "formats": ["webp", "avif", "480w.webp"]}
        assert gen.expand_formats(entry) == {
            "images/hero.webp",
            "images/hero.avif",
            "images/hero-480w.webp",
        }

    def test_declared_format_missing_on_disk_is_dropped(self, assets):
        _touch(assets, "images/hero.webp")
        entry = {"path": "images/hero", "formats": ["webp", "png"]}
        assert gen.expand_formats(entry) == {"images/hero.webp"}

    def test_base_path_resolves_without_formats(self, assets):
        _touch(assets, "images/scene.png")
        assert gen.expand_formats({"path": "images/scene"}) == {"images/scene.png"}

    def test_empty_path_registers_nothing(self, assets):
        _touch(assets, "images/.webp")
        assert gen.expand_formats({"path": "", "formats": ["webp"]}) == set()


class TestWalkManifestEntries:
    def test_yields_entries_at_any_depth_including_inside_entries(self):
        manifest = {
            "black_rose": {
                "lockup_display": {"path": "a", "variant": {"path": "a-nested"}},
                "atmospherics": [{"path": "b"}, {"kind": "no-path"}, [{"path": "c"}]],
            },
            "notes": "not an entry",
        }
        paths = sorted(e["path"] for e in gen.walk_manifest_entries(manifest))
        assert paths == ["a", "a-nested", "b", "c"]

    def test_scalars_yield_nothing(self):
        assert list(gen.walk_manifest_entries("x")) == []
        assert list(gen.walk_manifest_entries(None)) == []


class TestManifestEntry:
    def test_non_dict_is_none(self, assets):
        assert gen.manifest_entry(None) is None
        assert gen.manifest_entry("images/x") is None

    def test_dict_carries_resolution_and_metadata(self, assets):
        _touch(assets, "images/x.webp")
        out = gen.manifest_entry({"path": "images/x", "kind": "k", "status": "s"})
        assert out == {
            "path": "images/x",
            "resolved": "images/x.webp",
            "kind": "k",
            "status": "s",
            "notes": None,
        }

    def test_missing_file_resolves_none(self, assets):
        assert gen.manifest_entry({"path": "images/absent"})["resolved"] is None


# ---------------------------------------------------------------------------
# registered_files / build_orphans
# ---------------------------------------------------------------------------


class TestRegisteredFiles:
    def test_union_of_manifest_logos_and_resolved_product_images(self, assets):
        _touch(assets, "images/hero.webp")
        _touch(assets, "images/hero.avif")
        _touch(assets, "images/logos/mark.png")
        _touch(assets, "images/root-logo.svg")
        manifest = {"c": {"hero_backdrops": [{"path": "images/hero", "formats": ["avif"]}]}}
        logo_reg = {"logos": {"m": {"file": "mark.png"}, "r": {"file": "images/root-logo.svg"}}}
        products = {
            "c": [
                _product(
                    "t-001",
                    {
                        "image": ("images/p.webp", "images/p.webp"),
                        "back_image": ("images/gone.webp", None),
                    },
                )
            ]
        }
        assert gen.registered_files(manifest, logo_reg, products) == {
            "images/hero.webp",
            "images/hero.avif",
            "images/logos/mark.png",
            "images/root-logo.svg",
            "images/p.webp",
        }


class TestBuildOrphans:
    def _masters(self, *, known: list[str]):
        idents = {"black-rose": _ident("black-rose", known_orphans=known)}
        manifest = {"black_rose": {"patches": [{"path": "images/patch", "formats": ["webp"]}]}}
        logo_reg = {"logos": {"m": {"file": "mark.png"}}}
        products = {
            "black-rose": [_product("t-001", {"image": ("images/p.webp", "images/p.webp")})]
        }
        return idents, manifest, logo_reg, products

    def test_tree_minus_registered_minus_known(self, assets):
        for rel in (
            "images/patch.webp",  # manifest format sibling
            "images/logos/mark.png",  # logo
            "images/p.webp",  # product image
            "images/known.webp",  # known orphan
            "images/z-stray.webp",
            "images/a-stray.png",
            "images/readme.txt",  # not an image extension
            "images/deep/nested.webp",  # scan does not recurse
            "elsewhere/unscanned.webp",  # dir not in TREE_SCAN_DIRS
        ):
            _touch(assets, rel)
        doc = gen.build_orphans(masters=self._masters(known=["images/known.webp"]))
        assert doc["orphans"] == ["images/a-stray.png", "images/z-stray.webp"]
        assert doc["count"] == 2

    def test_known_orphans_are_the_only_suppression(self, assets):
        _touch(assets, "images/known.webp")
        doc = gen.build_orphans(masters=self._masters(known=[]))
        assert doc["orphans"] == ["images/known.webp"]
        assert doc["count"] == 1

    def test_missing_scan_dir_is_skipped(self, assets, monkeypatch):
        monkeypatch.setattr(gen, "TREE_SCAN_DIRS", ["does/not/exist"])
        doc = gen.build_orphans(masters=self._masters(known=[]))
        assert doc == {**doc, "count": 0, "orphans": []}


# ---------------------------------------------------------------------------
# imagery_block / logos_for / build_collection
# ---------------------------------------------------------------------------


class TestImageryBlock:
    def test_collection_portrait_moves_out_of_atmospherics(self, assets):
        mc = {
            "atmospherics": [
                {"path": "images/fog", "kind": "atmosphere"},
                {"path": "images/portrait", "kind": "collection-portrait"},
            ],
            "hero_backdrops": [{"path": "images/bg1"}, {"path": "images/bg2"}],
        }
        block = gen.imagery_block(mc)
        assert block["scene_portrait"]["path"] == "images/portrait"
        assert [e["path"] for e in block["atmospherics"]] == ["images/fog"]
        assert block["hero_backdrop"]["path"] == "images/bg1"

    def test_absent_and_malformed_keys_degrade(self, assets):
        block = gen.imagery_block({"lockup_display": "not-a-dict", "patches": "not-a-list"})
        assert block["lockup_display"] is None
        assert block["scene_portrait"] is None
        assert block["hero_backdrop"] is None
        for key in ("atmospherics", "patches", "lettering_alt", "lockup_parts", "lookbook"):
            assert block[key] == [], key

    def test_lockup_primary_maps_to_source_art(self, assets):
        block = gen.imagery_block({"lockup_primary": {"path": "images/src"}})
        assert block["lockup_source_art"]["path"] == "images/src"


class TestLogosFor:
    def test_matches_by_key_or_slug_only(self, assets):
        _touch(assets, "images/logos/br.png")
        logo_reg = {
            "logos": {
                "by-key": {"file": "br.png", "collection": "black_rose"},
                "by-slug": {"file": "x.png", "collection": "black-rose"},
                "other": {"file": "lh.png", "collection": "love_hurts"},
                "none": {"file": "n.png"},
            }
        }
        out = gen.logos_for("black-rose", "black_rose", logo_reg)
        assert [lg["id"] for lg in out] == ["by-key", "by-slug"]
        assert out[0]["resolved"] == "images/logos/br.png"
        assert out[1]["resolved"] is None

    def test_notes_truncated_to_160(self, assets):
        logo_reg = {
            "logos": {"l": {"file": "l.png", "collection": "signature", "description": "d" * 400}}
        }
        assert len(gen.logos_for("signature", "signature", logo_reg)[0]["notes"]) == 160

    def test_bare_file_path_fallback(self, assets):
        _touch(assets, "branding/mark.svg")
        logo_reg = {"logos": {"l": {"file": "branding/mark.svg", "collection": "signature"}}}
        assert (
            gen.logos_for("signature", "signature", logo_reg)[0]["resolved"] == "branding/mark.svg"
        )


class TestBuildCollection:
    def _build(self, ident, products=(), manifest=None):
        return gen.build_collection(
            ident["slug"], ident, manifest or {}, {"logos": {}}, list(products), "2026-10-10"
        )

    def test_lockup_keys_leave_imagery(self, assets):
        _touch(assets, "images/lockups/signature-lockup.webp")
        manifest = {"signature": {"lockup_display": {"path": "images/d"}, "lookbook": []}}
        doc = self._build(_ident("signature"), manifest=manifest)
        assert doc["lockup"]["canonical"] == "images/lockups/signature-lockup.webp"
        assert doc["lockup"]["display_webp"]["path"] == "images/d"
        for key in ("lockup_display", "lockup_svg_master", "lockup_source_art", "lockup_alt"):
            assert key not in doc["imagery"], key

    def test_hero_from_identity_or_none(self, assets):
        _touch(assets, "images/hero.webp")
        with_hero = self._build(_ident("signature", hero={"path": "images/hero", "kind": "hub"}))
        assert with_hero["imagery"]["hero"]["resolved"] == "images/hero.webp"
        assert with_hero["imagery"]["hero"]["kind"] == "hub"
        assert self._build(_ident("signature"))["imagery"]["hero"] is None

    def test_unresolved_product_images_lists_only_unresolved(self, assets):
        products = [
            _product("t-001", {"image": ("images/a.webp", "images/a.webp")}),
            _product(
                "t-002",
                {"image": ("images/b.webp", "images/b.webp"), "back_image": ("images/gone", None)},
            ),
        ]
        doc = self._build(_ident("signature"), products=products)
        assert doc["unresolved_product_images"] == [
            {"sku": "t-002", "column": "back_image", "path": "images/gone"}
        ]
        assert doc["products"] == products

    def test_identity_fields_and_updated_pass_through(self, assets):
        ident = _ident("kids-capsule")
        doc = self._build(ident)
        assert doc["collection"] == "kids-capsule"
        assert doc["updated"] == "2026-10-10"
        for key in ("name", "story", "palette", "fonts"):
            assert doc[key] == ident[key], key
        assert doc["_generated_by"].startswith("data/build-collection-sot.py")


# ---------------------------------------------------------------------------
# build_documents seam + main --out-dir
# ---------------------------------------------------------------------------


def _synthetic_masters():
    idents = {slug: _ident(slug) for slug in ("black-rose", "signature")}
    products = {"signature": [_product("t-001", {"image": ("images/p.webp", None)})]}
    return idents, {}, {"logos": {}}, products


def test_build_documents_uses_masters_seam(assets):
    docs = gen.build_documents("U", masters=_synthetic_masters())
    assert set(docs) == {"black-rose", "signature"}
    assert docs["black-rose"]["products"] == []
    assert [p["sku"] for p in docs["signature"]["products"]] == ["t-001"]
    assert all(d["updated"] == "U" for d in docs.values())


def test_main_writes_only_into_out_dir(assets, tmp_path, monkeypatch):
    out = tmp_path / "out"
    masters = _synthetic_masters()
    monkeypatch.setattr(gen, "_load_masters", lambda: masters)
    monkeypatch.setattr(
        sys, "argv", ["build-collection-sot.py", "--updated", "D", "--out-dir", str(out)]
    )
    tracked_before = {
        p: p.stat().st_mtime_ns for p in _TRACKED_COLLECTIONS.glob("**/*.json") if p.is_file()
    }

    assert gen.main() == 0

    written = sorted(str(p.relative_to(out)) for p in out.rglob("*.json"))
    assert written == ["_orphans.json", "black-rose/sot.json", "signature/sot.json"]
    for slug, doc in gen.build_documents("D", masters=masters).items():
        assert (out / slug / "sot.json").read_text() == gen.serialize(doc)
    orphans = json.loads((out / "_orphans.json").read_text())
    assert orphans["count"] == len(orphans["orphans"]) == 0
    tracked_after = {
        p: p.stat().st_mtime_ns for p in _TRACKED_COLLECTIONS.glob("**/*.json") if p.is_file()
    }
    assert tracked_after == tracked_before
