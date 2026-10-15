#!/usr/bin/env python3
"""Shared, validated readers for the per-collection SOT pipeline.

Single place that loads the masters (visual-manifest.json and logo-registry.json,
whose ``collections`` section holds each collection's identity) and resolves
asset paths. Both build-collection-sot.py and
verify-collection-sot.py import from here so resolution + validation never drift.
"""

import json
import sys
from pathlib import Path
from typing import Any

DATA = Path(__file__).resolve().parent
sys.path.insert(0, str(DATA.parents[2]))
from skyyrose.core.paths import WP_ASSETS_DIR  # noqa: E402

ASSETS = WP_ASSETS_DIR
COLLECTIONS_DIR = DATA / "collections"
SCHEMA = COLLECTIONS_DIR / "identity.schema.json"
MANIFEST = DATA / "visual-manifest.json"
LOGO_REG = DATA / "logo-registry.json"

# webp first = preferred; resolve_asset honors THIS order, not alphabetical glob order.
IMG_EXTS = (".webp", ".avif", ".png", ".jpg", ".jpeg", ".svg", ".mp4", ".webm")


class IdentityError(Exception):
    """A collection identity failed schema validation or could not be read."""


def slug_to_key(slug: str) -> str:
    return slug.replace("-", "_")


def _load_json(path: Path) -> Any:
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError as e:
        raise IdentityError(f"required master missing: {path}") from e
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise IdentityError(f"malformed JSON in {path}: {e}") from e
    except OSError as e:
        raise IdentityError(f"cannot read {path}: {e}") from e


def load_manifest():
    return _load_json(MANIFEST)


def load_logo_registry():
    return _load_json(LOGO_REG)


def load_identity() -> dict[str, Any]:
    """Return {slug: identity dict} from the registry's ``collections``, schema-validated.

    Collection identity (story, palette, fonts, lockup, hero imagery) lives in the
    product registry beside the products it frames; identity.schema.json still
    validates every entry in full.
    """
    import jsonschema

    schema = _load_json(SCHEMA)
    collections = load_logo_registry().get("collections")
    if not isinstance(collections, dict) or not collections:
        raise IdentityError(f"no collections section in {LOGO_REG}")
    out = {}
    for slug in sorted(collections):
        where = f"{LOGO_REG} collections.{slug}"
        ident = collections[slug]
        try:
            jsonschema.validate(ident, schema)
        except jsonschema.ValidationError as e:
            raise IdentityError(f"{where}: {e.message}") from e
        if ident["slug"] != slug:
            raise IdentityError(f"{where}: slug '{ident['slug']}' != key '{slug}'")
        if ident["key"] != slug_to_key(slug):
            raise IdentityError(f"{where}: key must be slug_to_key('{slug}')")
        out[slug] = ident
    return out


def resolve_asset(rel: str) -> str | None:
    """assets-relative path (possibly extension-less) -> real file rel-path, else None.

    Resolution order for an extension-less base:
      1. exact-stem siblings (``base.ext``) — preferred,
      2. then prefix siblings (``base*`` — e.g. responsive ``-480w.webp`` variants),
    and within each group the extension ranking in IMG_EXTS (webp before avif),
    NOT the alphabetically-first glob hit. Exact-stem-first prevents ``front`` from
    resolving to ``front-model.webp`` when ``front.webp`` exists.
    """
    if not rel:
        return None
    rel = rel.replace("assets/", "", 1) if rel.startswith("assets/") else rel
    p = ASSETS / rel
    # Containment: a traversal path ("../") must never escape the assets tree.
    try:
        if not p.resolve().is_relative_to(ASSETS.resolve()):
            return None
    except (OSError, ValueError):
        return None
    if p.is_file():
        return rel
    parent = p.parent
    if not parent.is_dir():
        return None

    def ranked(files) -> list[Path]:
        usable = [f for f in files if f.is_file() and f.suffix.lower() in IMG_EXTS]
        usable.sort(key=lambda f: (IMG_EXTS.index(f.suffix.lower()), f.name))
        return usable

    for group in (ranked(parent.glob(p.name + ".*")), ranked(parent.glob(p.name + "*"))):
        if group:
            return str(group[0].relative_to(ASSETS))
    return None
