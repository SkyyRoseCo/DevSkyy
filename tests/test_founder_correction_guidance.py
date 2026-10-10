"""Offline checks that render guidance preserves the maker's recorded corrections."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.generate_stage3_prompts import (
    build_output,
    extract_branding_entries,
    extract_frontmatter,
)
from scripts.scaffold_sku_asset_folders import LOGO_REGISTRY_JSON, _build_placement_md
from skyyrose.core.catalog_loader import get_product_with_dossier

ROOT = Path(__file__).resolve().parents[1]
DOSSIERS = ROOT / "wordpress-theme/skyyrose-flagship/data/dossiers"
JERSEY = "black-is-beautiful-jersey-series-2-last-oakland-football"
BOMBER = "love-hurts-bomber-jacket"


def test_jersey_decoration_obeys_front_and_back_digit_assignment():
    dossier = (DOSSIERS / f"{JERSEY}.md").read_text()
    entries = {entry["region"]: entry for entry in extract_branding_entries(dossier)}
    front = entries["front-chest"]["description"]
    back = entries["back-center"]["description"]
    assert "3 only" in front
    assert "2 remains plain white" in front
    assert "2 only" in back
    assert "3 plain white" in back
    assert "~10in tall" in dossier
    assert "~12in tall" in dossier
    assert "FOUNDER_CONFIRMED" in dossier


def test_jersey_preview_matches_corrected_canonical_dossier():
    dossier = (DOSSIERS / f"{JERSEY}.md").read_text()
    metadata = extract_frontmatter(dossier)
    expected = build_output(
        JERSEY, metadata["name"], metadata["sku"], extract_branding_entries(dossier)
    )
    preview = ROOT / "renders/prompts-preview" / JERSEY / "stage3-decoration.txt"
    assert preview.read_text() == expected


def test_bomber_placement_matches_canonical_satin_specification():
    product = get_product_with_dossier("lh-004")
    registry = json.loads(LOGO_REGISTRY_JSON.read_text())
    expected = _build_placement_md("lh-004", product, registry)
    placement = ROOT / "skyyrose/elite_studio/assets/golden/lh-004/placement.md"
    assert placement.read_text() == expected
    # Markdown line wrapping changes whitespace, not the maker's specification.
    expected = " ".join(expected.split())
    assert "FOUNDER_CONFIRMED" in expected
    assert "Satin appearance is required" in expected
    assert "Fiber composition is unspecified" in expected
    assert "NOT satin" not in expected
    assert "cotton-blend" not in expected


def test_bomber_base_prompt_preserves_satin_and_construction():
    preview = ROOT / "renders/prompts-preview" / BOMBER / "stage1-base.txt"
    text = preview.read_text()
    assert "satin" in text.lower()
    assert "NOT satin" not in text
    assert "cotton-blend" not in text
    for detail in ("white body", "black", "raglan", "hood", "button"):
        assert detail in text.lower()
