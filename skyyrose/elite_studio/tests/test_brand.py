"""Tests for skyyrose.elite_studio.brand (BrandConfig SoT loader)."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from skyyrose.elite_studio.brand import BrandConfig, CollectionBrand

pytest.importorskip("yaml")


FIXTURE_YAML = """
version: 1
generated_at: "2026-04-17T00:00:00Z"
tagline:
  active: ""
  retired:
    - phrase: "Where Love Meets Luxury"
      retired_at: "2026-03"
      reason: "Replaced for brand repositioning."
identity:
  name: "SkyyRose"
  founder: "Corey Foster"
colors:
  primary:
    dark: "#0A0A0A"
    rose_gold: "#B76E79"
collections:
  black-rose:
    display_name: "BLACK ROSE"
    tagline: ""
    theme: "gothic"
    mood: "dark"
    inspiration: "Oakland"
    hero_scene: "Bay Bridge"
    target_audience: "Oakland streetwear"
    palette:
      primary: "#0A0A0A"
      accent: "#B76E79"
typography:
  families: {}
logos: {}
social:
  instagram: "@skyyroseco"
urls:
  flagship: "https://skyyrose.co"
  dashboard: "https://devskyy.app"
"""


@pytest.fixture
def brand(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> BrandConfig:
    p = tmp_path / "brand.yaml"
    p.write_text(textwrap.dedent(FIXTURE_YAML).lstrip("\n"))
    monkeypatch.setenv("SKYYROSE_BRAND_PATH", str(p))
    return BrandConfig.load()


def test_loads_active_tagline(brand: BrandConfig) -> None:
    assert brand.tagline_active == ""


def test_loads_retired_taglines_as_phrase_list(brand: BrandConfig) -> None:
    assert brand.retired_taglines == ("Where Love Meets Luxury",)


def test_missing_active_tagline_is_optional(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    bad = FIXTURE_YAML.replace('  active: ""', '')
    p = tmp_path / "brand.yaml"
    p.write_text(textwrap.dedent(bad).lstrip("\n"))
    monkeypatch.setenv("SKYYROSE_BRAND_PATH", str(p))
    assert BrandConfig.load().tagline_active == ""


def test_invalid_hex_color_in_palette_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bad = FIXTURE_YAML.replace('dark: "#0A0A0A"', 'dark: "not-a-hex"')
    p = tmp_path / "brand.yaml"
    p.write_text(textwrap.dedent(bad).lstrip("\n"))
    monkeypatch.setenv("SKYYROSE_BRAND_PATH", str(p))
    with pytest.raises(ValueError, match="hex color"):
        BrandConfig.load()


def test_collection_lookup_returns_typed_object(brand: BrandConfig) -> None:
    c = brand.collection("black-rose")
    assert isinstance(c, CollectionBrand)
    assert c.display_name == "BLACK ROSE"
    assert c.palette["primary"] == "#0A0A0A"


def test_collection_lookup_unknown_raises_keyerror(brand: BrandConfig) -> None:
    with pytest.raises(KeyError, match="not found"):
        brand.collection("ghost-collection")


def test_missing_file_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SKYYROSE_BRAND_PATH", str(tmp_path / "nope.yaml"))
    with pytest.raises(FileNotFoundError):
        BrandConfig.load()


# ─── Live brand.yaml sanity check ───────────────────────────────────────


def test_live_brand_yaml_loads_clean() -> None:
    """Sanity: the committed assets/brand/brand.yaml must load without errors."""
    repo_root = Path(__file__).resolve().parents[3]
    live = repo_root / "assets" / "brand" / "brand.yaml"
    if not live.is_file():
        pytest.skip("Live brand.yaml not present in test environment")
    brand = BrandConfig.load(path=live)
    assert brand.tagline_active == ""
    assert "Where Love Meets Luxury" in brand.retired_taglines
    assert "black-rose" in brand.collections
