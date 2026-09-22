"""Brand — Single source of truth loader for SkyyRose brand identity.

Reads `assets/brand/brand.yaml` and exposes a typed API:

    from skyyrose.elite_studio.brand import BrandConfig

    brand = BrandConfig.load()
    print(brand.tagline_active)        # ""
    print(brand.retired_taglines)      # ("Where Love Meets Luxury",)
    print(brand.collection("black-rose").palette["primary"])  # "#0A0A0A"

Used by:
  - WordPress PHP (via generated inc/brand.generated.php — future sync script)
  - Frontend dashboard (via generated src/config/brand.generated.ts — future)
  - Python page builders (replace hardcoded "Where Love Meets Luxury" literals)
  - Enforcement test (skyyrose/elite_studio/tests/test_brand_enforcement.py)

brand.yaml is the ONLY editable source. Changes propagate via sync scripts.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "PyYAML is required to load brand.yaml. Install with `pip install pyyaml`."
    ) from _e

from .validation import validate_hex_color

_ENV_BRAND_PATH = "SKYYROSE_BRAND_PATH"


def default_brand_path() -> Path:
    """Return the canonical brand.yaml path (env-overridable)."""
    override = os.getenv(_ENV_BRAND_PATH)
    if override:
        return Path(override)
    repo_root = Path(__file__).resolve().parents[2]
    return repo_root / "assets" / "brand" / "brand.yaml"


@dataclass(frozen=True)
class CollectionBrand:
    slug: str
    display_name: str
    tagline: str
    description: str
    theme: str
    mood: str
    inspiration: str
    hero_scene: str
    target_audience: str
    palette: dict[str, str]


@dataclass(frozen=True)
class BrandConfig:
    version: int
    generated_at: str
    tagline_active: str
    retired_taglines: tuple[str, ...]
    identity: dict[str, Any]
    colors: dict[str, dict[str, str]]
    collections: dict[str, CollectionBrand]
    typography: dict[str, Any]
    logos: dict[str, Any]
    social: dict[str, str]
    urls: dict[str, str]
    migration: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path | str | None = None) -> BrandConfig:
        p = Path(path) if path else default_brand_path()
        if not p.is_file():
            raise FileNotFoundError(f"Brand config not found at {p}")
        data = yaml.safe_load(p.read_text()) or {}
        if not isinstance(data, dict):
            raise ValueError(f"brand.yaml must parse to a dict, got {type(data).__name__}")
        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: dict) -> BrandConfig:
        tagline_block = data.get("tagline") or {}
        active = str(tagline_block.get("active") or "")
        # An empty active tagline intentionally means the brand has no slogan.

        retired_raw = tagline_block.get("retired") or []
        retired: list[str] = []
        for entry in retired_raw:
            if isinstance(entry, dict) and "phrase" in entry:
                retired.append(str(entry["phrase"]))
            elif isinstance(entry, str):
                retired.append(entry)

        # Validate hex colors in palettes (fail loud on malformed brand data)
        colors = dict(data.get("colors") or {})
        for group_name, group in colors.items():
            if not isinstance(group, dict):
                continue
            for key, val in group.items():
                validate_hex_color(val, f"colors.{group_name}.{key}")

        # Build collection brands
        collections: dict[str, CollectionBrand] = {}
        for slug, meta in (data.get("collections") or {}).items():
            meta = meta or {}
            palette = dict(meta.get("palette") or {})
            for pkey, pval in palette.items():
                validate_hex_color(pval, f"collections.{slug}.palette.{pkey}")
            collections[slug] = CollectionBrand(
                slug=slug,
                display_name=str(meta.get("display_name") or ""),
                tagline=str(meta.get("tagline") or ""),
                description=str(meta.get("description") or ""),
                theme=str(meta.get("theme") or ""),
                mood=str(meta.get("mood") or ""),
                inspiration=str(meta.get("inspiration") or ""),
                hero_scene=str(meta.get("hero_scene") or ""),
                target_audience=str(meta.get("target_audience") or ""),
                palette=palette,
            )

        return cls(
            version=int(data.get("version") or 0),
            generated_at=str(data.get("generated_at") or ""),
            tagline_active=active,
            retired_taglines=tuple(retired),
            identity=dict(data.get("identity") or {}),
            colors=colors,
            collections=collections,
            typography=dict(data.get("typography") or {}),
            logos=dict(data.get("logos") or {}),
            social=dict(data.get("social") or {}),
            urls=dict(data.get("urls") or {}),
            migration=dict(data.get("migration") or {}),
        )

    def collection(self, slug: str) -> CollectionBrand:
        """Return the CollectionBrand for a slug; raises KeyError if unknown."""
        c = self.collections.get(slug)
        if c is None:
            raise KeyError(f"Collection {slug!r} not found in brand.yaml")
        return c
