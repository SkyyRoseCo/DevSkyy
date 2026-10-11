"""Tests for ``load_products_by_collection`` in ``data/build-collection-sot.py``.

The loader reads every product through ``skyyrose.core.product.get_product`` and
re-keys its role-resolved images back to the registry field that bound each one, in
the historical ``sot.json`` key order the freshness guard byte-compares. Synthetic
``get_product`` records exercise every branch; one test runs against the real
registry to prove no SKU is dropped or duplicated.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_SCRIPT = _REPO_ROOT / "wordpress-theme" / "skyyrose-flagship" / "data" / "build-collection-sot.py"


def _load(mod_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(mod_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)
    return module


# Distinct module name so this never re-executes over another test's module entry.
gen = _load("build_collection_sot_loader", _SCRIPT)


def _image(path: str, key: str) -> dict:
    return {"path": path, "source_key": key, "role_asset": True}


def _record(sku: str, collection: str | None, images: dict, **catalog) -> dict:
    return {
        "sku": sku,
        "name": f"Product {sku}",
        "collection": collection,
        "catalog": {"price": "10.00", **catalog},
        "images": images,
    }


def _install(monkeypatch, records: list[dict]) -> None:
    by_sku = {r["sku"]: r for r in records}
    monkeypatch.setattr(gen, "all_skus", lambda: sorted(by_sku))
    monkeypatch.setattr(gen, "get_product", lambda sku: by_sku[sku])
    monkeypatch.setattr(gen.sot_common, "resolve_asset", lambda rel: f"resolved/{rel}")


def test_images_keyed_by_source_key_in_historical_order(monkeypatch):
    _install(
        monkeypatch,
        [
            _record(
                "t-001",
                "signature",
                {
                    "front": _image("f.webp", "front_model_image"),
                    "back": _image("bm.webp", "back_model_image"),
                    "packshot": _image("p.webp", "image"),
                    "back_packshot": _image("b.webp", "back_image"),
                },
            )
        ],
    )
    (product,) = gen.load_products_by_collection()["signature"]
    assert list(product["images"]) == [
        "image",
        "front_model_image",
        "back_image",
        "back_model_image",
    ]
    assert product["images"]["back_image"] == {"path": "b.webp", "resolved": "resolved/b.webp"}


def test_fallback_roles_share_one_binding_and_absent_roles_are_omitted(monkeypatch):
    # front fell back to the packshot ("image"); no back assets at all.
    packshot = _image("p.webp", "image")
    _install(
        monkeypatch,
        [
            _record(
                "t-001",
                "signature",
                {
                    "front": {**packshot, "role_asset": False},
                    "back": None,
                    "packshot": packshot,
                    "back_packshot": None,
                },
            )
        ],
    )
    (product,) = gen.load_products_by_collection()["signature"]
    assert product["images"] == {"image": {"path": "p.webp", "resolved": "resolved/p.webp"}}


def test_grouped_by_registry_collection_and_none_maps_to_empty(monkeypatch):
    _install(
        monkeypatch,
        [
            _record("t-002", "black-rose", {}),
            _record("t-001", "black-rose", {}),
            _record("t-003", "love-hurts", {}),
            _record("t-004", None, {}),
        ],
    )
    by_col = gen.load_products_by_collection()
    assert set(by_col) == {"black-rose", "love-hurts", ""}
    assert [p["sku"] for p in by_col["black-rose"]] == ["t-001", "t-002"]
    assert [p["sku"] for p in by_col[""]] == ["t-004"]


def test_catalog_fields_flags_and_dossier(monkeypatch, tmp_path):
    (tmp_path / "dossiers").mkdir()
    (tmp_path / "dossiers" / "present.md").write_text("x")
    monkeypatch.setattr(gen, "DATA", tmp_path)
    _install(
        monkeypatch,
        [
            _record(
                "t-001", "signature", {}, is_preorder="1", published="0", dossier_slug="present"
            ),
            _record("t-002", "signature", {}, is_preorder="", dossier_slug=" missing "),
            _record("t-003", "signature", {}),
        ],
    )
    a, b, c = gen.load_products_by_collection()["signature"]
    assert (a["name"], a["price"], a["is_preorder"], a["published"]) == (
        "Product t-001",
        "10.00",
        True,
        False,
    )
    assert (a["dossier"], a["dossier_exists"]) == ("data/dossiers/present.md", True)
    assert (b["is_preorder"], b["dossier"], b["dossier_exists"]) == (
        False,
        "data/dossiers/missing.md",
        False,
    )
    assert (c["dossier"], c["dossier_exists"]) == (None, False)


def test_real_registry_every_sku_exactly_once():
    by_col = gen.load_products_by_collection()
    emitted = [p["sku"] for products in by_col.values() for p in products]
    assert sorted(emitted) == gen.all_skus()
    for products in by_col.values():
        for p in products:
            assert list(p["images"]) == [k for k in gen.IMAGE_KEY_ORDER if k in p["images"]]
