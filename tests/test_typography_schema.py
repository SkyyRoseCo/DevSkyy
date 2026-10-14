"""typography.json must satisfy its own schema; the schema must still reject drift."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

BRAND = Path(__file__).resolve().parents[1] / "wordpress-theme/skyyrose-flagship/data/brand"
TYPOGRAPHY = BRAND / "typography.json"
SCHEMA = BRAND / "typography.schema.json"


@pytest.fixture(scope="module")
def validator() -> Draft202012Validator:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


@pytest.fixture
def typography() -> dict:
    return json.loads(TYPOGRAPHY.read_text(encoding="utf-8"))


def messages(validator: Draft202012Validator, value: object) -> list[str]:
    return [f"{list(e.absolute_path)}: {e.message}" for e in validator.iter_errors(value)]


def test_current_typography_has_no_schema_violations(validator, typography) -> None:
    assert messages(validator, typography) == []


def test_font_role_note_must_be_text(validator, typography) -> None:
    broken = deepcopy(typography)
    broken["universal"]["display"]["note"] = 125
    assert messages(validator, broken)


@pytest.mark.parametrize("role", ["display", "body", "mono", "ui"])
def test_font_role_rejects_unknown_keys(validator, typography, role) -> None:
    broken = deepcopy(typography)
    broken["universal"][role]["weight"] = 900
    assert messages(validator, broken)


@pytest.mark.parametrize("key", ["family", "stack", "woff2"])
def test_font_role_requires_core_keys(validator, typography, key) -> None:
    broken = deepcopy(typography)
    del broken["universal"]["display"][key]
    assert messages(validator, broken)
