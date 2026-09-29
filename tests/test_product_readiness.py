"""Offline omission fixtures exercise the real central projection and brief chain."""

import copy
import json

import pytest

from skyyrose.core import product as core
from skyyrose.elite_studio.prompts.enhancer import PromptEnhancer


@pytest.fixture
def registry(monkeypatch):
    registry = copy.deepcopy(core.load_registry())
    item = registry["products"]["br-001"]
    item["content"] = {
        field: {"value": "Synthetic editorial fixture", "authority": "TEST_FIXTURE"}
        for field in core.CONTENT_FIELDS
    }
    item["content"]["alt_text"] = {"front": "Synthetic accessible description"}
    monkeypatch.setattr(core, "load_registry", lambda: registry)
    return item


@pytest.mark.parametrize(
    "omission,gap,blocked",
    [
        ("fit", "garment.fit", "render"),
        ("front", "render_sources.front", "render"),
        ("seo", "content.seo_meta", "seo"),
        ("alt", "content.alt_text", "alt-text"),
    ],
)
def test_independent_omissions(registry, omission, gap, blocked):
    if omission == "fit":
        registry["garment"]["fit"]["specification"] = None
    elif omission == "front":
        registry["render_sources"]["front"] = None
    elif omission == "seo":
        registry["content"]["seo_meta"] = None
    else:
        registry["content"]["alt_text"] = {}
    before = copy.deepcopy(registry)
    record = core.get_product("br-001")
    assert gap in record["gaps"]
    assert gap in record["gap_categories"][gap.split(".")[0]]
    assert gap in core.gap_report()["br-001"]
    for operation in ("render", "seo", "alt-text"):
        result = core.product_readiness(record, operation, required_views=("front",))
        assert result["ready"] == (operation != blocked)
        assert (gap in result["blocking_gaps"]) == (operation == blocked)
        brief = PromptEnhancer().enhance(
            "Photograph br-001", operation=operation, required_views=("front",)
        )
        assert (brief.brief_status == "incomplete") == (operation == blocked)
        assert f"br-001.{gap}" in brief.gaps
        payload = json.loads(brief.enhanced)
        assert payload["product_constraints"]["br-001"]["garment"] == record["garment"]
        assert payload["product_constraints"]["br-001"]["corrections"] == record["corrections"]
    assert registry == before


def test_optional_back_and_editorial_do_not_block_front(registry):
    registry["render_sources"]["back"] = None
    registry["content"] = {}
    record = core.get_product("br-001")
    front = core.product_readiness(record, required_views=("front",))
    assert front["ready"]
    assert "render_sources.back" in front["optional_gaps"]
    assert not core.product_readiness(record, required_views=("back",))["ready"]
    assert not core.product_readiness(record)["ready"]


@pytest.mark.parametrize("field", ["color", "fit", "materials", "features"])
def test_whitespace_specification_is_missing(registry, field):
    registry["garment"][field] = "  " if field == "color" else {"specification": "  "}
    result = core.product_readiness(core.get_product("br-001"), required_views=("front",))
    assert f"garment.{field}" in result["blocking_gaps"]


def test_invalid_contracts_fail_closed(registry):
    record = core.get_product("br-001")
    with pytest.raises(KeyError):
        core.get_product("br-999")
    with pytest.raises(ValueError):
        core.product_readiness(record, "invented")
    with pytest.raises(ValueError):
        core.product_readiness(record, required_views=("side",))


def test_blank_alt_values_are_discoverable(registry):
    registry["content"]["alt_text"] = {"front": " "}
    assert "content.alt_text" in core.get_product("br-001")["gaps"]
