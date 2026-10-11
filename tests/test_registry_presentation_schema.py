"""Structural gate for technical garment regions; pixel/review validation is separate."""

from __future__ import annotations

import json
from copy import deepcopy

import pytest
from jsonschema import Draft202012Validator

from scripts.organize_product_registry import REGISTRY, SCHEMA, check_schema
from skyyrose.core.product import get_product


@pytest.fixture
def presentation() -> dict:
    return get_product("br-002")["presentation"]


def errors(value: object) -> list:
    schema = json.loads(SCHEMA.read_text())
    focused = {"$ref": "#/$defs/presentation", "$defs": schema["$defs"]}
    return list(Draft202012Validator(focused).iter_errors(value))


def test_current_registry_has_no_schema_violations() -> None:
    assert check_schema(json.loads(REGISTRY.read_text())) == []


def test_existing_presentation_contract_is_accepted(presentation: dict) -> None:
    assert errors(presentation) == []
    assert errors({}) == []  # No annotation is a legitimate pending state.


@pytest.mark.parametrize(
    "path,value",
    [
        (("unexpected",), "arbitrary metadata"),
        (("garment_highlight", "unexpected"), "unbound fact"),
        (("garment_highlight", "sku"), "unknown"),
        (("garment_highlight", "status"), "PASS"),
        (("garment_highlight", "source", "width"), 768),
        (("garment_highlight", "source", "height"), True),
        (("garment_highlight", "source", "sha256"), "not-a-hash"),
        (("garment_highlight", "source", "path"), "assets/../private/card.webp"),
        (("garment_highlight", "source", "path"), "/assets/card.webp"),
        (("garment_highlight", "source", "unexpected"), "value"),
        (("garment_highlight", "polygons"), []),
        (("garment_highlight", "polygons", 0, "outer"), [[0, 0], [1, 1]]),
        (("garment_highlight", "polygons", 0, "outer", 0), [True, 0]),
        (("garment_highlight", "polygons", 0, "outer", 0), [1025, 0]),
        (("garment_highlight", "polygons", 0, "outer", 0), [0, 1537]),
        (("garment_highlight", "polygons", 0, "outer", 0), [0, 0, 1]),
        (("garment_highlight", "polygons", 0, "holes"), [None]),
        (("garment_highlight", "polygons", 0, "unexpected"), "value"),
        (("garment_highlight", "review", "geometry_sha256"), "g" * 64),
        (("garment_highlight", "review", "evidence_sha256"), ""),
        (("garment_highlight", "review", "evidence_path"), " "),
        (("garment_highlight", "review", "unexpected"), "value"),
    ],
)
def test_rejects_malformed_or_unrecognized_fields(presentation: dict, path: tuple, value: object):
    candidate = deepcopy(presentation)
    parent = candidate
    for key in path[:-1]:
        parent = parent[key]
    parent[path[-1]] = value
    assert errors(candidate), f"Accepted invalid field {path}"


@pytest.mark.parametrize(
    "section,required",
    [
        ((), "source"),
        (("source",), "sha256"),
        (("source",), "path"),
        (("review",), "evidence_sha256"),
        (("review",), "evidence_path"),
    ],
)
def test_requires_complete_source_review_binding(presentation: dict, section: tuple, required: str):
    parent = presentation["garment_highlight"]
    for key in section:
        parent = parent[key]
    del parent[required]
    assert errors(presentation)


@pytest.mark.parametrize("budget", ["polygons", "holes", "vertices"])
def test_rejects_geometry_over_runtime_per_ring_limits(presentation: dict, budget: str) -> None:
    polygons = presentation["garment_highlight"]["polygons"]
    if budget == "polygons":
        polygons *= 17
    elif budget == "holes":
        polygons[0]["holes"] = [[[0, 0], [1, 0], [1, 1]]] * 17
    else:
        polygons[0]["outer"] = [[x, 0] for x in range(257)]
    assert errors(presentation)
