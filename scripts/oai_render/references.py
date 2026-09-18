"""Reference resolution — maps each SKU to its garment / logo / patch images.

Ported from the retired nano_banana ``source_map.py`` + ``logo_refs.py`` so the
OAI pipeline is fully self-contained (nano_banana can be deleted). The maps are
engine-agnostic data: SKU → real garment photos, collection/SKU logos, and the
sport-patch PNGs.

Hard-fail policy (no silent fallback, per project rule): if a SKU has no usable
garment reference, or a jersey SKU's required sport patch is missing, building
its reference set raises ``MissingReferenceError`` — the SKU is reported and
skipped, never rendered as an incomplete image.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from skyyrose.core.catalog_loader import PROJECT_ROOT, read_catalog_rows
from skyyrose.core.dossier_loader import DOSSIERS_DIR
from skyyrose.core.product_registry import load_registry
from skyyrose.elite_studio.logo_registry import LogoRegistry

from . import config

log = logging.getLogger(__name__)


class MissingReferenceError(RuntimeError):
    """Raised when a SKU lacks a required reference image (garment or patch)."""


@dataclass(frozen=True)
class ReferenceImage:
    """A single labeled reference fed to the image edit call."""

    label: str
    path: Path
    kind: str  # "garment" | "garment-back" | "logo" | "patch"


# ── Catalog ─────────────────────────────────────────────────────────────────
def load_catalog() -> dict[str, dict]:
    """Project the unified product registry, keyed by SKU."""
    catalog: dict[str, dict] = {}
    for row in read_catalog_rows(config.CATALOG_CSV):
        sku = row["sku"].strip()
        if not sku:
            continue
        catalog[sku] = {
            "name": (row.get("name") or "").strip(),
            "collection": (row.get("collection") or "").strip(),
            "is_preorder": (row.get("is_preorder") or "").strip() == "1",
            "output_slug": (row.get("render_output_slug") or "").strip() or sku,
        }
    return catalog


# ── Registry-owned garment source bindings ──────────────────────────────────
def get_source_map() -> dict[str, dict[str, Path | None]]:
    """Read current registry bindings, including explicit non-catalog components."""
    registry = load_registry()
    sources = {
        sku: product["render_sources"]
        for sku, product in registry["products"].items()
        if "render_sources" in product
    }
    sources.update(registry.get("render_source_aliases", {}))
    return {
        sku: {view: PROJECT_ROOT / path if path else None for view, path in refs.items()}
        for sku, refs in sources.items()
    }


# ── Logo + sport-patch references ───────────────────────────────────────────
def requires_patch(sku: str) -> bool:
    """Read the registered sport-patch requirement, independent of asset filenames."""
    return LogoRegistry.load().patch_sport_for(sku) is not None


def has_back_source(sku: str) -> bool:
    """True if the SKU has a dedicated back garment source → it earns a ghost-back render."""
    back = get_source_map().get(sku, {}).get("back")
    return back is not None and back.exists()


# ── Paired-look registry (founder-confirmed 2026-06-08) ─────────────────────
# Coordinating SKUs shown together on ONE model (paired look) but SOLD
# SEPARATELY. The on-model shot for a paired SKU is the PAIR; ghost-mannequin
# shots stay per-SKU (product cards). A SKU may belong to more than one pair
# (e.g. lh-004 bomber pairs with both jogger colorways).
@dataclass(frozen=True)
class Pair:
    """A two-garment coordinated on-model look (the pieces are sold separately)."""

    pair_id: str
    collection: str
    skus: tuple[str, str]
    label: str


PAIRS: tuple[Pair, ...] = (
    Pair("br-rose-set", "black-rose", ("br-001", "br-002"), "BLACK Rose Crewneck + Joggers"),
    Pair(
        "sg-baybridge-set",
        "signature",
        ("sg-001", "sg-005"),
        "Bridge Series 'The Bay Bridge' Shorts + Shirt",
    ),
    Pair(
        "sg-staygolden-set",
        "signature",
        ("sg-002", "sg-003"),
        "Bridge Series 'Stay Golden' Shirt + Shorts",
    ),
    Pair(
        "sg-mintlav-set",
        "signature",
        ("sg-013", "sg-014"),
        "Mint & Lavender Crewneck + Sweatpants",
    ),
    Pair(
        "lh-bomber-black", "love-hurts", ("lh-004", "lh-002"), "Love Hurts Bomber + Joggers (Black)"
    ),
    Pair(
        "lh-bomber-white", "love-hurts", ("lh-004", "lh-006"), "Love Hurts Bomber + Joggers (White)"
    ),
    Pair(
        "kids-red-set",
        "kids-capsule",
        ("kids-001", "kids-001-joggers"),
        "Kids Colorblock Red — Hoodie + Joggers",
    ),
    Pair(
        "kids-purple-set",
        "kids-capsule",
        ("kids-002", "kids-002-joggers"),
        "Kids Colorblock Purple — Hoodie + Joggers",
    ),
)


def get_pairs_for_sku(sku: str) -> list[Pair]:
    """Return every pair that includes this SKU (a SKU can belong to more than one)."""
    return [p for p in PAIRS if sku in p.skus]


def get_logo_reference(sku: str, collection: str) -> Path | None:
    """Use registered SKU artwork only; collection membership never supplies a logo."""
    registry = LogoRegistry.load()
    registry.decoration_sizing_for(sku, required=requires_patch(sku))
    path = registry.primary_reference_for(sku)
    if path is None:
        return None
    if not path.is_file():
        raise MissingReferenceError(f"Registered logo reference missing for {sku}: {path}")
    return path


def find_flatlay_photo(sku: str) -> Path | None:
    """Resolve the explicit supplemental source; never discover authority by filename."""
    return get_source_map().get(sku, {}).get("reference")


def build_dossier_index() -> dict[str, Path]:
    """Map SKU → dossier markdown path by parsing each dossier's frontmatter ``sku:``."""
    if config.DOSSIER_DIR.resolve() == DOSSIERS_DIR.resolve():
        registry = load_registry()
        index = {
            sku: DOSSIERS_DIR / f"{product['dossier']['slug']}.md"
            for sku, product in registry["products"].items()
            if product.get("dossier", {}).get("slug")
        }
        for component, binding in registry.get("render_components", {}).items():
            index[component] = index[binding["parent_sku"]]
        return index
    index: dict[str, Path] = {}
    if not config.DOSSIER_DIR.exists():
        return index
    for md in sorted(config.DOSSIER_DIR.glob("*.md")):
        if md.name.startswith("_"):
            continue  # skip _template.md
        try:
            text = md.read_text(encoding="utf-8")
        except OSError:
            continue
        # Frontmatter is the first --- ... --- block.
        if not text.startswith("---"):
            continue
        end = text.find("---", 3)
        if end == -1:
            continue
        for line in text[3:end].splitlines():
            if line.strip().lower().startswith("sku:"):
                sku = line.split(":", 1)[1].strip()
                if sku and sku.upper() != "REPLACE-WITH-SKU":
                    index[sku] = md
                break
    return index


def build_references(
    sku: str, collection: str, *, include_back: bool = True, view: str = "front"
) -> list[ReferenceImage]:
    """Resolve the ordered, labeled reference set for a SKU.

    Order (first image is the primary canvas — masks apply to it, and per the
    OpenAI cookbook the first image gets the finest detail preservation):
      1. Explicitly registered supplemental product source — if available
      2. Garment front source (techflat / split)
      3. Garment back source — if available AND ``include_back`` (front-only on-model
         renders pass ``include_back=False`` to avoid back-view / multi-panel collage)
      4. Logo / sport-patch close-up — if applicable

    For ``view="back"`` the back techflat is promoted to FIRST position so the
    view-primary reference leads — best-available mitigation for mirrored-front
    hallucination on rear renders (no verified deterministic fix exists).

    Raises MissingReferenceError when no usable garment reference exists, or
    when a jersey SKU's required sport patch is missing (no silent fallback).
    """
    smap = get_source_map().get(sku, {})
    front = smap.get("front")
    back = smap.get("back")
    flatlay = find_flatlay_photo(sku)
    registry = LogoRegistry.load()
    logo = get_logo_reference(sku, collection)
    reference_kind = registry.reference_kind_for(sku)
    bound_garment = logo if reference_kind == "garment" else None
    if bound_garment and view == "back" and (back is None or not back.is_file()):
        raise MissingReferenceError(
            f"{sku}: garment artwork is bound to the front only; no registered back source"
        )
    physical_front_label = (
        "REFERENCE IMAGE {n} — REGISTERED GARMENT SOURCE (FRONT VIEW): the complete "
        "physical garment with its exact printed artwork and embroidery. Preserve "
        "the full composition and original graphic placement; this is not a standalone "
        "logo close-up or a techflat. Do not extract, recolor, or replace the artwork."
    )

    refs: list[ReferenceImage] = []

    if flatlay and flatlay.exists():
        refs.append(
            ReferenceImage(
                label=(
                    physical_front_label
                    if flatlay == bound_garment
                    else (
                        "REFERENCE IMAGE {n} — REGISTERED PRODUCT SOURCE: use this explicitly "
                        "bound image for the garment's appearance. This source may be a "
                        "photo, techflat, or prior render; founder specifications in the "
                        "registry remain authoritative."
                    )
                ),
                path=flatlay,
                kind="garment",
            )
        )

    if front and front.exists():
        refs.append(
            ReferenceImage(
                label=(
                    physical_front_label
                    if front == bound_garment
                    else (
                        "REFERENCE IMAGE {n} — GARMENT TECH FLAT (FRONT VIEW): front-facing design "
                        "illustration showing front panel layout, graphic placement, silhouette, "
                        "and construction."
                    )
                ),
                path=front,
                kind="garment",
            )
        )

    # Must have at least one garment reference — otherwise hard-fail.
    if not refs:
        raise MissingReferenceError(
            f"{sku}: no usable garment reference (front={front}, flatlay=None)."
        )

    if include_back and back and back.exists():
        refs.append(
            ReferenceImage(
                label=(
                    "REFERENCE IMAGE {n} — GARMENT TECH FLAT (BACK VIEW): rear-facing design "
                    "illustration showing back panel layout and graphics."
                ),
                path=back,
                kind="garment-back",
            )
        )

    patch_required = requires_patch(sku)
    if logo and logo.exists():
        # primary_reference_for resolves the actual registered sport-patch
        # record before considering non-sport supplemental logo bindings.
        is_patch = patch_required
        refs.append(
            ReferenceImage(
                label=(
                    physical_front_label
                    if reference_kind == "garment"
                    else (
                        "REFERENCE IMAGE {n} — "
                        + ("SPORT PATCH" if is_patch else "LOGO/BRANDING")
                        + " CLOSE-UP: the EXACT graphic on the garment. Reproduce it at the EXACT "
                        "position and size shown in the tech flat. Do NOT resize, reposition, "
                        "duplicate, omit, or alter it."
                    )
                ),
                path=logo,
                kind=reference_kind,
            )
        )
    elif patch_required:
        # Jersey whose sport patch is missing → must not render patchless.
        raise MissingReferenceError(
            f"{sku}: required sport patch reference is missing; refusing to render a "
            "patchless jersey (100%-replicated rule)."
        )

    if view == "back":
        # View-primary ordering: the registered back source leads for back renders.
        refs.sort(key=lambda r: 0 if r.kind == "garment-back" else 1)

    # A garment may be bound as front, supplemental source, and artwork. Attach its
    # unchanged bytes once, retaining its accurate garment role and source label.
    unique: list[ReferenceImage] = []
    seen_paths: set[Path] = set()
    for ref in refs:
        resolved_path = ref.path.resolve()
        if resolved_path not in seen_paths:
            seen_paths.add(resolved_path)
            unique.append(ref)
    capped = unique[: config.MAX_REFERENCE_IMAGES]
    # Re-number the {n} placeholders in display order.
    return [
        ReferenceImage(label=r.label.format(n=i + 1), path=r.path, kind=r.kind)
        for i, r in enumerate(capped)
    ]
