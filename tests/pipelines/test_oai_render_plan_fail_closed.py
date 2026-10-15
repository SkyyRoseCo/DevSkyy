"""A missing registry must abort planning, never mark every SKU "skipped".

Catching FileNotFoundError in plan_sku/plan_pair turned a renamed or absent
logo-registry.json into a batch that exits green with every SKU skipped and
$0 spent (bug-230 class). Only a missing dossier is a per-SKU condition.
No API calls are made here: planning fails before any client is built.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.oai_render import pipeline as pipeline_mod
from scripts.oai_render.references import Pair
from skyyrose.core import product_registry
from skyyrose.core.dossier_loader import DossierMissingError

_PAIR = Pair("br-rose-set", "black-rose", ("br-001", "br-002"), "Crewneck + Joggers")
_CATALOG = {
    "br-001": {"name": "Crewneck", "collection": "black-rose"},
    "br-002": {"name": "Joggers", "collection": "black-rose"},
}


def test_plan_sku_raises_when_registry_is_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(product_registry, "PRODUCT_REGISTRY", tmp_path / "renamed-registry.json")
    with pytest.raises(FileNotFoundError):
        pipeline_mod.plan_sku("br-001", _CATALOG, {})


def test_plan_pair_raises_when_registry_is_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(product_registry, "PRODUCT_REGISTRY", tmp_path / "renamed-registry.json")
    with pytest.raises(FileNotFoundError):
        pipeline_mod.plan_pair(_PAIR, _CATALOG, {})


def test_plan_pair_still_skips_when_only_a_dossier_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Guard for the narrowing: a per-SKU dossier gap stays a skip, not a batch abort."""
    monkeypatch.setattr(pipeline_mod, "load_registry", lambda: {"render_components": {}})
    monkeypatch.setattr(pipeline_mod.references, "build_references", lambda *a, **k: [])
    monkeypatch.setattr(pipeline_mod.references, "requires_patch", lambda sku: False)

    def missing_dossier(_path: Path | None) -> str:
        raise DossierMissingError("No dossier 'br-001' content in the product registry.")

    monkeypatch.setattr(pipeline_mod, "read_dossier", missing_dossier)

    plan = pipeline_mod.plan_pair(_PAIR, _CATALOG, {})

    assert plan.renderable is False
    assert "No dossier" in (plan.error or "")
