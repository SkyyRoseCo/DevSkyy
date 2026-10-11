"""Technical garment regions bound to independently reviewed, exact card pixels.

These annotations describe image geometry, never garment or founder product facts.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]
THEME_ROOT = REPO_ROOT / "wordpress-theme/skyyrose-flagship-2"
MAX_VERTICES = 2048
MAX_RING_VERTICES = 256
MAX_POLYGONS = 16
MAX_HOLES = 16
MAX_RINGS = 64


def geometry_paths(polygons: Any) -> list[str]:
    """Serialize rings identically to the runtime SVG consumer."""
    return [
        " ".join(
            "M" + " L".join(f"{x} {y}" for x, y in ring) + " Z"
            for ring in [polygon["outer"], *polygon["holes"]]
        )
        for polygon in polygons
    ]


def geometry_digest(polygons: Any) -> str:
    return hashlib.sha256("\n".join(geometry_paths(polygons)).encode()).hexdigest()


def _cross(a: list[int], b: list[int], c: list[int]) -> int:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _on(a: list[int], b: list[int], p: list[int]) -> bool:
    return _cross(a, b, p) == 0 and all(min(a[i], b[i]) <= p[i] <= max(a[i], b[i]) for i in (0, 1))


def _intersect(a: list[int], b: list[int], c: list[int], d: list[int]) -> bool:
    crosses = (_cross(a, b, c), _cross(a, b, d), _cross(c, d, a), _cross(c, d, b))
    return (crosses[0] * crosses[1] < 0 and crosses[2] * crosses[3] < 0) or any(
        (_on(a, b, c), _on(a, b, d), _on(c, d, a), _on(c, d, b))
    )


def _edges(ring: list[list[int]]) -> list[tuple[list[int], list[int]]]:
    return list(zip(ring, ring[1:] + ring[:1], strict=True))


def _inside(point: list[int], ring: list[list[int]]) -> bool:
    if any(_on(a, b, point) for a, b in _edges(ring)):
        return False
    x, y = point
    inside = False
    for a, b in _edges(ring):
        if (a[1] > y) != (b[1] > y) and x < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]:
            inside = not inside
    return inside


def _ring(ring: Any, width: int, height: int) -> None:
    if not isinstance(ring, list) or not 3 <= len(ring) <= MAX_RING_VERTICES:
        raise ValueError("Garment ring must contain 3..256 vertices")
    for point in ring:
        if not isinstance(point, list) or len(point) != 2 or any(type(v) is not int for v in point):
            raise ValueError("Garment coordinates must be integer pairs")
        if not 0 <= point[0] <= width or not 0 <= point[1] <= height:
            raise ValueError("Garment coordinate exceeds native image bounds")
    if len({tuple(p) for p in ring}) != len(ring):
        raise ValueError("Garment ring contains repeated vertices")
    edges = _edges(ring)
    for index, b in enumerate(ring):
        a, c = ring[index - 1], ring[(index + 1) % len(ring)]
        if _cross(a, b, c) == 0 and sum((b[i] - a[i]) * (c[i] - b[i]) for i in (0, 1)) <= 0:
            raise ValueError("Garment ring reverses along an adjacent edge")
    if not sum(a[0] * b[1] - b[0] * a[1] for a, b in edges):
        raise ValueError("Garment ring has zero area")
    for i, (a, b) in enumerate(edges):
        for j, (c, d) in enumerate(edges):
            if j <= i or j == i + 1 or (i == 0 and j == len(edges) - 1):
                continue
            if _intersect(a, b, c, d):
                raise ValueError("Garment ring self-intersects")


def _asset_path(theme: Path, relative: Any) -> Path:
    if not isinstance(relative, str):
        raise ValueError("Missing card source path")
    path = Path(relative)
    if (
        not re.fullmatch(r"assets/[a-zA-Z0-9_./-]+\.(?:webp|png|jpe?g)", relative)
        or ".." in relative
        or path.is_absolute()
        or not path.parts
        or path.parts[0] != "assets"
        or path.as_posix() != relative
        or path.suffix not in {".webp", ".png", ".jpg", ".jpeg"}
    ):
        raise ValueError("Card source must be a normalized theme-relative PNG/JPEG/WebP asset")
    candidate = theme / path
    ancestor = theme
    if ancestor.is_symlink():
        raise ValueError("Symlink card sources are not permitted")
    for part in path.parts:
        ancestor = ancestor / part
        if ancestor.is_symlink():
            raise ValueError("Symlink card sources are not permitted")
    if not candidate.resolve().is_relative_to(theme.resolve()) or not candidate.is_file():
        raise ValueError("Card source is missing or outside theme")
    return candidate


def validate_annotation(
    sku: str, annotation: Any, *, evidence_path: Path | None = None, theme_root: Path | None = None
) -> dict[str, Any]:
    """Return a detached validated record; reject changed pixels or review claims."""
    theme = theme_root or THEME_ROOT
    if (
        not isinstance(annotation, dict)
        or annotation.get("sku") != sku
        or annotation.get("status") != "INDEPENDENT_VISUAL_PASS"
    ):
        raise ValueError("Garment annotation requires matching SKU and independent visual PASS")
    if set(annotation) != {"sku", "status", "source", "polygons", "review"}:
        raise ValueError("Garment annotation contains unsupported technical fields")
    source = annotation.get("source")
    if (
        not isinstance(source, dict)
        or type(source.get("width")) is not int
        or type(source.get("height")) is not int
        or (source["width"], source["height"]) != (1024, 1536)
    ):
        raise ValueError("Garment annotation requires native 1024x1536 pixels")
    approved = json.loads((theme / "data/approved-card-fronts.json").read_text())["products"].get(
        sku
    )
    if not isinstance(approved, dict) or (
        approved.get("scene_status"),
        approved.get("current_fidelity_status"),
    ) not in {
        ("FOUNDER_APPROVED_V2_CARD", "EXISTING_SCOPED_APPROVAL_RETAINED"),
        ("INDEPENDENT_REVIEWED_V2_CARD", "INDEPENDENT_VISUAL_PASS"),
    }:
        raise ValueError("Current card source is not approved for this SKU")
    if approved["scene_status"] == "INDEPENDENT_REVIEWED_V2_CARD":
        from skyyrose.core.product_registry import _reviewed_card_records

        record = _reviewed_card_records(
            {sku: approved.get("src")}, theme=theme, evidence_root=REPO_ROOT
        )[sku]
        if (
            approved.get("review") != record["review"]
            or approved.get("sha256") != record["sha256"]
            or approved.get("source_sha256") != record["sha256"]
            or approved.get("candidate_id") != record["production_id"]
        ):
            raise ValueError("Independent card binding differs from exact reviewed master")
    expected = {
        "path": approved.get("src"),
        "sha256": approved.get("sha256"),
        "width": approved.get("width"),
        "height": approved.get("height"),
    }
    if source != expected:
        raise ValueError("Garment source differs from current approved front")
    asset = _asset_path(theme, source["path"])
    if hashlib.sha256(asset.read_bytes()).hexdigest() != source["sha256"]:
        raise ValueError("Garment source bytes changed")
    with Image.open(asset) as image:
        if image.size != (source["width"], source["height"]):
            raise ValueError("Garment source dimensions changed")
    polygons = annotation.get("polygons")
    if not isinstance(polygons, list) or not 1 <= len(polygons) <= MAX_POLYGONS:
        raise ValueError("Garment annotation requires 1..16 polygons")
    vertices = 0
    ring_count = 0
    # Bound the whole input before quadratic ring/intersection validation.
    for polygon in polygons:
        if (
            not isinstance(polygon, dict)
            or set(polygon) != {"outer", "holes"}
            or not isinstance(polygon["holes"], list)
            or len(polygon["holes"]) > MAX_HOLES
        ):
            raise ValueError("Garment polygon requires outer and at most 16 holes")
        rings = [polygon["outer"], *polygon["holes"]]
        ring_count += len(rings)
        for ring in rings:
            if not isinstance(ring, list) or not 3 <= len(ring) <= MAX_RING_VERTICES:
                raise ValueError("Garment ring must contain 3..256 vertices")
            vertices += len(ring)
        if ring_count > MAX_RINGS or vertices > MAX_VERTICES:
            raise ValueError("Garment annotation exceeds ring/vertex budget")
    # Each polygon is a union region. Independent outer rings may overlap,
    # touch or nest; only their own holes subtract from that region.
    for polygon in polygons:
        for ring in [polygon["outer"], *polygon["holes"]]:
            _ring(ring, source["width"], source["height"])
        for i, hole in enumerate(polygon["holes"]):
            if not all(_inside(p, polygon["outer"]) for p in hole):
                raise ValueError("Garment hole must lie strictly inside outer ring")
            for other in [polygon["outer"], *polygon["holes"][:i]]:
                if any(
                    _intersect(a, b, c, d) for a, b in _edges(hole) for c, d in _edges(other)
                ) or (
                    other != polygon["outer"]
                    and (_inside(hole[0], other) or _inside(other[0], hole))
                ):
                    raise ValueError("Garment hole intersects another ring")
    review = annotation.get("review")
    digest = geometry_digest(polygons)
    if not isinstance(review, dict) or review.get("geometry_sha256") != digest:
        raise ValueError("Garment geometry hash does not match review")
    if set(review) - {"geometry_sha256", "evidence_sha256", "evidence_path"}:
        raise ValueError("Garment annotation review contains unsupported fields")
    receipt_path = evidence_path or REPO_ROOT / str(review.get("evidence_path", ""))
    if not receipt_path.is_file() or receipt_path.is_symlink():
        raise ValueError("Independent garment review receipt is missing")
    receipt_bytes = receipt_path.read_bytes()
    receipt = json.loads(receipt_bytes)
    if (
        review.get("evidence_sha256") != hashlib.sha256(receipt_bytes).hexdigest()
        or receipt.get("schema_version") != 1
    ):
        raise ValueError("Independent garment review receipt digest/schema mismatch")
    matching = [r for r in receipt.get("reviews", []) if r.get("sku") == sku]
    if len(matching) != 1:
        raise ValueError("Independent review requires exactly one record for this SKU")
    row = matching[0]
    if (
        row.get("status") != "PASS"
        or row.get("source") != source
        or row.get("geometry_sha256") != digest
    ):
        raise ValueError("Independent review is not bound to this garment geometry/source")
    if (
        not all(isinstance(row.get(k), str) and row[k].strip() for k in ("annotator", "reviewer"))
        or row["annotator"].strip() == row["reviewer"].strip()
    ):
        raise ValueError("Independent review requires distinct annotator and reviewer")
    result = copy.deepcopy(annotation)
    if evidence_path is not None:
        result["review"]["evidence_path"] = (
            str(receipt_path.resolve().relative_to(REPO_ROOT))
            if receipt_path.resolve().is_relative_to(REPO_ROOT)
            else str(receipt_path.resolve())
        )
    return result
