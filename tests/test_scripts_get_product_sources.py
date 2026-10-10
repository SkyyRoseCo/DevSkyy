"""Generator scripts read product facts through ``get_product``, not the CSV.

Covers the second scripts refactor batch: ``build_v7_cards.py`` and
``preflight_audit.py`` source their catalog fields from the registry via
``skyyrose.core.product.get_product`` (``build-site-guide.py`` is covered in
``tests/test_build_site_guide.py``). Each test swaps in a fake registry and
observes the change in the script's output, so a regression to a CSV reader fails.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import scripts.preflight_audit as audit_mod  # noqa: E402
from skyyrose.core.product import all_skus, get_product  # noqa: E402


def _load_v7_generator():
    spec = importlib.util.spec_from_file_location(
        "build_v7_cards_sources", _REPO_ROOT / "scripts" / "build_v7_cards.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gen = _load_v7_generator()


def _catalog(sku: str, **over: str) -> dict[str, str]:
    row = {
        "sku": sku,
        "name": "Registry Name",
        "price": "77",
        "collection": "black-rose",
        "badge": "",
        "edition_size": "12",
        "is_preorder": "1",
        "render_is_accessory": "0",
    }
    row.update(over)
    return row


def _fake_registry(monkeypatch, module, catalogs: dict[str, dict[str, str]]) -> None:
    monkeypatch.setattr(module, "all_skus", lambda: sorted(catalogs))
    monkeypatch.setattr(module, "get_product", lambda sku: {"sku": sku, "catalog": catalogs[sku]})


def test_v7_cards_take_catalog_fields_from_the_registry(monkeypatch) -> None:
    _fake_registry(monkeypatch, gen, {"br-001": _catalog("br-001")})
    (card,) = gen.build_cards()
    assert (card["name"], card["price"], card["edition"], card["preorder"]) == (
        "Registry Name",
        77,
        12,
        True,
    )


def test_v7_cards_registry_rows_match_get_product() -> None:
    assert gen._registry_rows() == [get_product(sku)["catalog"] for sku in all_skus()]


def test_v7_cards_committed_file_is_current_from_the_registry() -> None:
    assert gen.main(["--check"]) == 0


def test_preflight_classifies_registry_products(monkeypatch, tmp_path) -> None:
    _fake_registry(
        monkeypatch,
        audit_mod,
        {
            "zz-001": _catalog("zz-001", name="Registry Bag", render_is_accessory="1"),
            "zz-002": _catalog("zz-002"),
        },
    )
    out = tmp_path / "SKIPPED.json"
    assert audit_mod.main(bundles_dir=tmp_path / "no-bundles", skipped_out=out) == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["skipped"] == [
        {"sku": "zz-001", "name": "Registry Bag", "collection": "black-rose"}
    ]
    assert data["total_in_scope_garments"] == 1


def test_preflight_fails_closed_on_an_empty_registry(monkeypatch, tmp_path, capsys) -> None:
    _fake_registry(monkeypatch, audit_mod, {})
    assert audit_mod.main(skipped_out=tmp_path / "SKIPPED.json") == 1
    assert "zero products" in capsys.readouterr().err
    assert not (tmp_path / "SKIPPED.json").exists()
