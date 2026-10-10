"""Catalog-derived production contract for complete SkyyRose SKU media.

The product registry remains the only product source of truth.  This module
does not create a second product/media registry: it reads the registry's image
bindings through :mod:`skyyrose.core.sot_images` and reports the required views
for each SKU.  Candidate outputs are review-only until a founder-approved asset
is promoted into the registry.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from skyyrose.core import paths, sot_images

# Registry image paths are theme-relative (``assets/images/...``).
_THEME_ROOT: Final = paths.THEME_ROOT


@dataclass(frozen=True)
class MediaRequirement:
    """One required, SKU-bound storefront media view."""

    key: str
    catalog_field: str
    label: str
    generation_brief: str


REQUIRED_MEDIA: Final[tuple[MediaRequirement, ...]] = (
    MediaRequirement(
        "on_model_front",
        "front_model_image",
        "On-model front",
        "Full-body editorial model shot. Preserve the exact SKU garment and show the front clearly.",
    ),
    MediaRequirement(
        "on_model_back",
        "back_model_image",
        "On-model back",
        "Full-body editorial model shot. Preserve the exact SKU garment and show the back clearly.",
    ),
    MediaRequirement(
        "mannequin_front",
        "mannequin_front_image",
        "Mannequin front",
        "Neutral full-body mannequin or ghost-mannequin view. Show the front construction only.",
    ),
    MediaRequirement(
        "mannequin_back",
        "mannequin_back_image",
        "Mannequin back",
        "Neutral full-body mannequin or ghost-mannequin view. Show the back construction only.",
    ),
    MediaRequirement(
        "render_3d",
        "render_3d_image",
        "3D render",
        "Faithful three-quarter 3D product render with material, silhouette, and branding verified against the SKU canon.",
    ),
)


# These are deliberately separated from the catalog fields.  They describe how
# to *request* a candidate image, while the CSV remains the sole authority for
# promoting a reviewed image into a storefront-servable media slot.
MEDIA_PRODUCTION_PROFILES: Final[dict[str, dict[str, str | tuple[str, ...]]]] = {
    "on_model_front": {
        "capture_type": "on-model editorial",
        "camera": "full-body, front-facing, 4:5 vertical ecommerce crop",
        "subject": "gender-neutral adult model; garment remains the focal point",
        "background": "quiet studio or collection-approved scene with clear silhouette separation",
        "requirements": (
            "Show the complete front of the exact SKU.",
            "Preserve logos, artwork placement, trims, color blocking, material, and fit.",
            "Do not add, remove, recolor, crop, or invent garment details.",
        ),
    },
    "on_model_back": {
        "capture_type": "on-model editorial",
        "camera": "full-body, back-facing, 4:5 vertical ecommerce crop",
        "subject": "gender-neutral adult model; garment remains the focal point",
        "background": "quiet studio or collection-approved scene with clear silhouette separation",
        "requirements": (
            "Show the complete back of the exact SKU.",
            "Preserve logos, artwork placement, trims, color blocking, material, and fit.",
            "Do not add, remove, recolor, crop, or invent garment details.",
        ),
    },
    "mannequin_front": {
        "capture_type": "ghost mannequin",
        "camera": "front-facing, centered, 4:5 vertical product crop",
        "subject": "neutral ghost mannequin; no person or styling props",
        "background": "clean neutral background",
        "requirements": (
            "Show only the front construction of the exact SKU.",
            "Keep edge shape, drape, pockets, fasteners, and proportions faithful.",
            "Do not add, remove, recolor, crop, or invent garment details.",
        ),
    },
    "mannequin_back": {
        "capture_type": "ghost mannequin",
        "camera": "back-facing, centered, 4:5 vertical product crop",
        "subject": "neutral ghost mannequin; no person or styling props",
        "background": "clean neutral background",
        "requirements": (
            "Show only the back construction of the exact SKU.",
            "Keep edge shape, drape, pockets, fasteners, and proportions faithful.",
            "Do not add, remove, recolor, crop, or invent garment details.",
        ),
    },
    "render_3d": {
        "capture_type": "3D product render",
        "camera": "three-quarter product view, 4:5 vertical product crop",
        "subject": "the exact SKU only; no model or mannequin",
        "background": "clean neutral background with a restrained contact shadow",
        "requirements": (
            "Match the exact SKU silhouette, material response, artwork, branding, and construction.",
            "Keep the garment readable at a product-card scale.",
            "Do not add, remove, recolor, crop, or invent garment details.",
        ),
    },
}

REVIEW_DIMENSIONS: Final[tuple[str, ...]] = (
    "sku_identity_match",
    "front_or_back_view_accuracy",
    "logo_and_artwork_fidelity",
    "color_and_material_fidelity",
    "silhouette_and_construction_fidelity",
    "crop_and_storefront_readiness",
)


def _image_path(product: dict, field: str) -> str | None:
    entry = product.get("images", {}).get(field)
    if not isinstance(entry, dict):
        return None
    path = entry.get("path")
    if not isinstance(path, str) or not path:
        return None
    path = sot_images._validated_path(path, product.get("sku", "unknown"))
    # A view is ready only when its bound asset exists. Presence is read from the
    # file itself, never from a stored ``resolved`` copy that can go missing or stale.
    return path if (_THEME_ROOT / path).is_file() else None


def sku_media_record(sku: str) -> dict | None:
    """Return one generated media matrix record, or ``None`` for an unknown SKU."""
    product = sot_images._index().get(sku)
    if not product:
        return None

    views: dict[str, dict[str, str | bool | None]] = {}
    for requirement in REQUIRED_MEDIA:
        path = _image_path(product, requirement.catalog_field)
        views[requirement.key] = {
            "label": requirement.label,
            "catalog_field": requirement.catalog_field,
            "path": path,
            "ready": bool(path),
            "generation_brief": requirement.generation_brief,
            "review_target": f"renders/sku-media/{sku}/{requirement.key}.webp",
            "promotion_target": requirement.catalog_field,
        }

    return {
        "sku": sku,
        "name": product.get("name", ""),
        "collection": product.get("collection", ""),
        "reference_inputs": {
            "front_packshot": _image_path(product, "image"),
            "back_packshot": _image_path(product, "back_image"),
        },
        "views": views,
        "complete": all(view["ready"] for view in views.values()),
    }


def build_media_matrix() -> dict:
    """Build the generated all-SKU production matrix from the collection SOT."""
    records = [sku_media_record(sku) for sku in sot_images.all_skus()]
    sku_records = [record for record in records if record is not None]
    complete = sum(1 for record in sku_records if record["complete"])
    return {
        "_authority": "Generated from the catalog via collection SOT; do not hand-edit.",
        "_promotion_rule": "A media file is storefront-eligible only after verified review and catalog/SOT regeneration.",
        "required_views": [requirement.key for requirement in REQUIRED_MEDIA],
        "summary": {
            "sku_count": len(sku_records),
            "complete_sku_count": complete,
            "incomplete_sku_count": len(sku_records) - complete,
        },
        "skus": sku_records,
    }


def _reference_inputs(record: dict) -> list[str]:
    """Return unique SOT asset inputs in a stable production-review order."""
    references = record["reference_inputs"]
    return [
        path
        for path in (references.get("front_packshot"), references.get("back_packshot"))
        if isinstance(path, str) and path
    ]


def build_production_jobs(matrix: dict | None = None, *, only_missing: bool = True) -> dict:
    """Build deterministic, approval-gated jobs for every SKU media view.

    This is an input package for a future provider adapter, not a provider call.
    It cannot generate, upload, or promote an asset.  Every job keeps its SKU
    proof inputs, candidate location, QA rubric, and catalog promotion field
    together so a generated image cannot be mistaken for SOT media.
    """
    matrix = matrix or build_media_matrix()
    jobs: list[dict] = []
    for record in matrix["skus"]:
        references = _reference_inputs(record)
        for view_key, view in record["views"].items():
            if only_missing and view["ready"]:
                continue
            profile = MEDIA_PRODUCTION_PROFILES[view_key]
            sku = record["sku"]
            jobs.append(
                {
                    "id": f"{sku}:{view_key}",
                    "sku": sku,
                    "name": record["name"],
                    "collection": record["collection"],
                    "view": view_key,
                    "status": (
                        "needs_reference" if not references else "ready_for_reviewed_generation"
                    ),
                    "reference_inputs": references,
                    "generation": {
                        "provider": "UNASSIGNED",
                        "capture_type": profile["capture_type"],
                        "camera": profile["camera"],
                        "subject": profile["subject"],
                        "background": profile["background"],
                        "requirements": list(profile["requirements"]),
                        "generation_brief": view["generation_brief"],
                    },
                    "candidate_target": f"renders/sku-media/{sku}/{view_key}.webp",
                    "review": {
                        "state": "not_submitted",
                        "required_dimensions": list(REVIEW_DIMENSIONS),
                        "rejection_rule": "Reject if the candidate changes SKU-specific artwork, branding, color, silhouette, construction, or requested view.",
                    },
                    "promotion": {
                        "state": "blocked_pending_review",
                        "catalog_field": view["catalog_field"],
                        "target_path": view["promotion_target"],
                        "rule": "Only a founder-approved, asset-resolved candidate may be written to the catalog and regenerated into collection SOT.",
                    },
                }
            )

    return {
        "_authority": "Generated from the catalog-backed SKU media contract; do not hand-edit.",
        "_execution_boundary": "Jobs are dry-run specifications. Provider calls, uploads, and catalog promotion require separate approval.",
        "summary": {
            "sku_count": matrix["summary"]["sku_count"],
            "job_count": len(jobs),
            "missing_only": only_missing,
        },
        "jobs": jobs,
    }


def missing_views(matrix: dict | None = None) -> list[str]:
    """Return stable ``sku:view`` identifiers for any missing required view."""
    matrix = matrix or build_media_matrix()
    missing: list[str] = []
    for record in matrix["skus"]:
        for view, data in record["views"].items():
            if not data["ready"]:
                missing.append(f"{record['sku']}:{view}")
    return missing
