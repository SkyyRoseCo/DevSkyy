"""Every committed SOT projection equals fresh generator output.

The product registry feeds a chain of generated files: collection ``sot.json``,
``data/sot-images.json``, ``lookbook-sot.json`` and ``docs/campaigns/sot-lookbook.html``.
A registry commit that skips regeneration leaves them stale. The pre-commit
freshness guard can be bypassed, so this test is the gate that always runs in CI.

The byte authority is ``scripts/validate_catalog_consistency.py``; this test
calls its checks rather than re-implementing the comparison. Fix a failure with
``bash scripts/freshness-guard.sh --fix``.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from tests.sparse_guard import requires_tree

_REPO_ROOT = Path(__file__).resolve().parents[1]
_VALIDATOR = _REPO_ROOT / "scripts" / "validate_catalog_consistency.py"


def _load_validator():
    spec = importlib.util.spec_from_file_location("validate_catalog_consistency", _VALIDATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


validator = _load_validator()


@pytest.mark.parametrize(
    "check",
    [
        pytest.param("collection_sot_current", marks=requires_tree("assets/hub")),
        "sot_images_current",
        "lookbook_sot_current",
        "lookbook_html_current",
    ],
)
def test_committed_projection_is_fresh(check: str) -> None:
    result = validator.ALL_CHECKS[check]()
    assert result.passed, f"{check}: {result.message}"
    # A skipped check reports passed=True without comparing anything.
    assert "skip" not in result.message.lower(), f"{check} did not run: {result.message}"
