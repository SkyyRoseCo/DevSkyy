"""Canonical SOT product-imagery resolver — the single authority for
"what image represents this SKU".

Every surface that shows a product image — pipelines, MCP tools, subagents, the
WordPress theme, and the dashboard (via the generated ``data/sot-images.json``
manifest) — resolves product imagery through here, never through ad-hoc paths.
Hardcoding ``assets/images/products/<sku>...`` anywhere else is a drift bug
(``tests/test_sot_no_adhoc_imagery.py`` guards against it).

Source of truth = product image records in ``logo-registry.json``. Collection
SOT views and ``data/sot-images.json`` are generated mirrors, not editable inputs.

The front-first fallback chain mirrors the WordPress theme's
``template-parts/product-card-holo.php`` rule exactly: the on-model render
(``front_model_image``) is shown first; the flat studio packshot (``image``) is
the last resort, never the default. This is the rule the dead prototype bundler
violated (it bound cards to the flat ``image``), producing the flatlay/wrong-item
previews this module exists to prevent.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

# Anchor on the canonical path registry (skyyrose.core.paths) — never recompute
# repo/theme roots locally (paths.py is the single place that answers "where").
from skyyrose.core.paths import REPO_ROOT, THEME_ROOT
from skyyrose.core.product_registry import load_registry

COLLECTIONS_DIR: Path = THEME_ROOT / "data" / "collections"
_CANONICAL_COLLECTIONS_DIR = COLLECTIONS_DIR

Role = Literal["front", "back", "packshot", "back_packshot"]

# role -> ordered SOT image keys. On-model render first, flat packshot last —
# the same precedence product-card-holo.php applies. Order matters.
_ROLE_KEYS: dict[str, tuple[str, ...]] = {
    "front": ("front_model_image", "image"),
    "back": ("back_model_image", "back_image"),
    "packshot": ("image",),
    "back_packshot": ("back_image",),
}


def _index() -> dict[str, dict]:
    """Read current registry products, or an explicitly redirected fixture tree."""
    if COLLECTIONS_DIR.resolve() == _CANONICAL_COLLECTIONS_DIR.resolve():
        return {
            sku: {**product["catalog"], "sku": sku, "images": product.get("images", {})}
            for sku, product in load_registry()["products"].items()
        }

    # Noncanonical directories are deliberate fixture inputs. Never consult
    # generated collection files to repair a missing canonical registry record.
    idx: dict[str, dict] = {}
    # Enumerate collections from the filesystem so a newly-added collection is
    # picked up automatically — never a hardcoded slug list that silently omits it.
    for sot_path in sorted(COLLECTIONS_DIR.glob("*/sot.json")):
        slug = sot_path.parent.name
        sot = json.loads(sot_path.read_text())
        for prod in sot.get("products", []):
            sku = prod.get("sku")
            if sku:
                idx[sku] = {**prod, "collection": slug}
    return idx


def refresh() -> None:
    """Compatibility hook: reads already reload the current registry each time."""


def all_skus() -> list[str]:
    """Every SKU present in the SOT, sorted."""
    return sorted(_index())


def _validated_path(raw: str, sku: str) -> str:
    """Enforce the theme-relative contract — reject absolute paths / ``..`` escapes.

    The SOT is repo-tracked and generated, so this is defense-in-depth (matching
    ``paths.golden_path`` / ``paths.wp_product_path``): a consumer that ``open()``s
    or serves the returned path must never receive one that climbs out of the tree.
    """
    if raw.startswith("/") or ".." in Path(raw).parts:
        raise ValueError(f"sot.json image path escapes the assets tree for {sku!r}: {raw!r}")
    return raw


def _first_path(images: dict, keys: tuple[str, ...], sku: str) -> str | None:
    """First present, validated ``path`` among ``keys`` — the front-first fallback.

    Single authority for the fallback loop (used by both :func:`resolve_image` and
    :func:`build_manifest`).
    """
    for key in keys:
        entry = images.get(key)
        if isinstance(entry, dict) and entry.get("path"):
            return _validated_path(entry["path"], sku)
    return None


def resolve_image(sku: str, role: Role = "front") -> str | None:
    """Return the theme-relative path (``assets/images/products/...``) for a SKU's
    image in ``role``, applying the front-first fallback chain.

    Returns ``None`` when the SKU is unknown or the SOT carries no image for the
    role — callers fall back to their own placeholder. Never invents a path.

    Args:
        sku: Canonical SKU (e.g. ``"br-004"``).
        role: ``"front"`` (on-model, default) | ``"back"`` | ``"packshot"`` (flat).
    """
    if not sku:
        return None
    prod = _index().get(sku)
    if not prod:
        return None
    return _first_path(prod.get("images", {}), _ROLE_KEYS.get(role, ()), sku)


def has_render(sku: str) -> bool:
    """True when the SOT has an actual on-model FRONT render (``front_model_image``).

    Distinct from ``resolve_image(sku, "front") is not None`` — that falls back to the
    flat ``image`` packshot so a card always shows *something*. ``has_render`` answers
    the narrower "is there a real render", so it must NOT honor the packshot fallback.
    """
    prod = _index().get(sku)
    if not prod:
        return False
    entry = prod.get("images", {}).get("front_model_image")
    return isinstance(entry, dict) and bool(entry.get("path"))


def build_manifest() -> dict[str, dict[str, str]]:
    """Flat ``{sku: {front, back?, packshot?}}`` map of theme-relative paths.

    The serialized form (``data/sot-images.json``) is the SOT imagery contract for
    non-Python surfaces (the Next.js dashboard, any JS/PHP consumer). Generated —
    regenerate via :func:`write_manifest`; never hand-edit.
    """
    # Single pass over the current index, reusing the same _ROLE_KEYS fallback
    # chain resolve_image() applies (one authority for the front-first rule).
    manifest: dict[str, dict[str, str]] = {}
    for sku, prod in sorted(_index().items()):
        images = prod.get("images", {})
        entry: dict[str, str] = {}
        for role, keys in _ROLE_KEYS.items():
            path = _first_path(images, keys, sku)
            if path:
                entry[role] = path
        if entry:
            manifest[sku] = entry
    return manifest


# Default emit location: repo-root data/sot-images.json (a generated artifact
# both systems can read without cross-wiring the WP theme tree).
MANIFEST_PATH: Path = REPO_ROOT / "data" / "sot-images.json"


def serialize_manifest(manifest: dict | None = None) -> str:
    """Canonical serialized bytes of the SOT imagery manifest.

    The SINGLE byte-authority for ``data/sot-images.json``: both
    :func:`write_manifest` and the catalog validator's ``sot_images_current`` drift
    guard call this, so the committed file and the CI check can never disagree on
    formatting (the way two independent serializers would). Pass a pre-built
    ``manifest`` to avoid rebuilding it.
    """
    payload = {
        "_generated_by": "skyyrose.core.sot_images.write_manifest — DO NOT EDIT. "
        "Regenerate after build-collection-sot.py.",
        "_authority": "SOT product-imagery contract. Front-first fallback "
        "(on-model render before flat packshot).",
        "images": build_manifest() if manifest is None else manifest,
    }
    return json.dumps(payload, indent=2) + "\n"


def write_manifest(out_path: Path | None = None, manifest: dict | None = None) -> Path:
    """Write the manifest to ``out_path`` (default :data:`MANIFEST_PATH`).

    Pass an already-built ``manifest`` to avoid rebuilding it (e.g. when the caller
    also needs the count); otherwise it is built here.
    """
    out = out_path or MANIFEST_PATH
    # Never let a caller-supplied out_path write outside the repo.
    if out_path is not None and not str(out.resolve()).startswith(str(REPO_ROOT)):
        raise ValueError(f"write_manifest: out_path must be within the repo: {out_path}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(serialize_manifest(manifest))
    return out


if __name__ == "__main__":
    images = build_manifest()
    p = write_manifest(manifest=images)
    print(f"wrote {p} ({len(images)} skus)")
