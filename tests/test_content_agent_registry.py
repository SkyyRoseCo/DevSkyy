"""The ADK content agent's tools read and write the product registry only.

The retired side store (``skyyrose/assets/data/product-content.json``) carried
names and copy for garments the registry does not describe -- lh-006 was "The
Fannie" fanny-pack copy on the white joggers. These tests pin the tools to the
registry: names come from ``get_product``, writes land in
``products[sku].content`` stamped ``AGENT_GENERATED``, and ``get_product`` then
serves that copy with its authority named.

The module imports ``google.adk`` at import time. The ADK is not installed in
the main test environment, so when the real package is absent the fixture
stubs the four ADK names the module binds; the tool functions under test never
touch them. ``dotenv.load_dotenv`` is disabled so importing the module cannot
pull API keys into the test process.
"""

from __future__ import annotations

import importlib
import shutil
import sys
import types
from pathlib import Path

import pytest

from skyyrose.core import product_registry
from skyyrose.core.product import get_product

MODULE = "skyyrose.skyyrose_content_agent"


def _stub_adk(mp: pytest.MonkeyPatch) -> None:
    """Register placeholder ``google.adk`` modules when the real ADK is absent."""
    try:
        importlib.import_module("google.adk")
        return
    except ImportError:
        pass
    placeholders = {
        "google.adk": ("Runner",),
        "google.adk.agents": ("LlmAgent",),
        "google.adk.sessions": ("InMemorySessionService",),
        "google.adk.tools": ("FunctionTool",),
    }
    for name, attrs in placeholders.items():
        module = types.ModuleType(name)
        for attr in attrs:
            setattr(module, attr, type(attr, (), {}))
        mp.setitem(sys.modules, name, module)


@pytest.fixture(scope="module")
def agent():
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("dotenv.load_dotenv", lambda *args, **kwargs: False)
        _stub_adk(mp)
        sys.modules.pop(MODULE, None)
        yield importlib.import_module(MODULE)
    sys.modules.pop(MODULE, None)


@pytest.fixture
def tmp_registry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A private copy of the real registry; the real file is never written."""
    copy = tmp_path / "logo-registry.json"
    shutil.copy(product_registry.PRODUCT_REGISTRY.resolve(), copy)
    monkeypatch.setattr(product_registry, "PRODUCT_REGISTRY", copy)
    return copy


def test_module_has_no_side_store(agent) -> None:
    assert not hasattr(agent, "PRODUCT_JSON_PATH")
    assert "product-content.json" not in agent.SYSTEM_INSTRUCTION
    assert "product registry" in agent.SYSTEM_INSTRUCTION
    assert "AGENT_GENERATED" in agent.SYSTEM_INSTRUCTION


def test_get_product_serves_registry_name_not_side_store_copy(agent) -> None:
    result = agent.get_product("LH-006 ")
    assert result["status"] == "ok"
    product = result["product"]
    assert product["name"] == "Love Hurts Joggers (White)"
    assert product["collection"] == "love-hurts"
    assert "Fannie" not in str(product)
    assert product["color"] == "White"
    assert product["sizes"] == ["S", "M", "L", "XL", "2XL", "3XL"]
    assert product["garment"]["fit"] and product["garment"]["materials"]
    assert set(product["content"]) == agent.WRITABLE_FIELDS
    assert isinstance(product["gaps"], list)


def test_get_product_unknown_sku_is_an_error(agent) -> None:
    result = agent.get_product("lh-999")
    assert result["status"] == "error"
    assert "lh-999" in result["error"]


def test_catalog_and_collections_come_from_the_registry(agent) -> None:
    catalog = agent.get_product_catalog()
    assert catalog["status"] == "ok"
    assert catalog["count"] >= 33
    assert catalog["catalog"]["br-001"]["name"] == "BLACK Rose Crewneck"

    kids = agent.get_collection_products("Kids Capsule")
    assert kids["status"] == "ok"
    assert kids["collection"] == "kids-capsule"
    assert kids["collection_name"] == "Kids Capsule"
    assert set(kids["products"]) == {"kids-001", "kids-002"}

    bad = agent.get_collection_products("denim")
    assert bad["status"] == "error"
    assert "kids-capsule" in bad["error"]


def test_update_writes_registry_with_agent_authority(agent, tmp_registry: Path) -> None:
    before = get_product("lh-006")
    assert before["content"]["instagram"] is None

    copy = "White joggers, black side-panel, the heart-rose on the thigh. Oakland-built. #SkyyRose"
    result = agent.update_product_field("lh-006", "instagram", copy)
    assert result["status"] == "ok", result
    assert result["authority"] == "AGENT_GENERATED"
    assert result["old_length"] == 0
    assert result["new_length"] == len(copy)

    after = get_product("lh-006")
    assert after["content"]["instagram"] == {
        "value": copy,
        "source": "registry.content",
        "enriched": True,
        "authority": "AGENT_GENERATED",
    }
    assert "content.instagram" not in after["gaps"]

    raw = product_registry.load_registry(tmp_registry)["products"]["lh-006"]["content"]["instagram"]
    assert raw["source"] == "skyyrose_content_agent"
    assert raw["updated"]

    via_tool = agent.get_product("lh-006")["product"]["content"]["instagram"]
    assert via_tool["authority"] == "AGENT_GENERATED"


def test_update_rejects_read_only_and_unknown_fields_and_skus(agent, tmp_registry: Path) -> None:
    original = tmp_registry.read_bytes()

    read_only = agent.update_product_field("lh-006", "name", "The Fannie")
    assert read_only["status"] == "error"
    assert "read-only" in read_only["error"]

    unknown_field = agent.update_product_field("lh-006", "price", "1")
    assert unknown_field["status"] == "error"
    assert "Unknown field" in unknown_field["error"]

    unknown_sku = agent.update_product_field("lh-999", "tiktok", "copy")
    assert unknown_sku["status"] == "error"
    assert "lh-999" in unknown_sku["error"]

    assert tmp_registry.read_bytes() == original


def test_refresh_audit_counts_only_registry_content(agent, tmp_registry: Path) -> None:
    audit = agent.list_products_needing_refresh("tiktok")
    assert audit["status"] == "ok"
    assert audit["needs_refresh_count"] + audit["ok_count"] >= 33
    flagged = {entry["sku"]: entry for entry in audit["needs_refresh"]}
    assert flagged["lh-006"]["issue"] == "missing"
    assert flagged["lh-006"]["name"] == "Love Hurts Joggers (White)"

    agent.update_product_field("lh-006", "tiktok", "Heart-rose on the thigh. #SkyyRose #LoveHurts")
    after = agent.list_products_needing_refresh("tiktok")
    ok = {entry["sku"]: entry for entry in after["ok"]}
    assert ok["lh-006"]["authority"] == "AGENT_GENERATED"
    assert ok["lh-006"]["char_count"] >= agent.FIELD_MIN_CHARS["tiktok"]

    # A description served from the catalog base line is the founder's spec,
    # not finished copy: it must be reported as missing, not "ok".
    description = agent.list_products_needing_refresh("description")
    assert {e["sku"] for e in description["needs_refresh"] if e["issue"] == "missing"} >= {"lh-006"}

    assert agent.list_products_needing_refresh("name")["status"] == "error"
