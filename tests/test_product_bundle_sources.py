"""Product-bundle "real photo" files must be byte copies of the registry reference.

The legacy render paths (agents/render_pipeline, scripts/nano_banana) hand a bundle's
``source-photo`` / ``photo-front`` to the model as "REFERENCE — REAL PRODUCT PHOTO".
A bundle that drifts from ``get_product(sku)["render_sources"]["reference"]`` forks the
product SOT: the kids bundles carried plain-tee photos for the colorblock sets.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from skyyrose.core.paths import REPO_ROOT
from skyyrose.core.product import get_product

BUNDLES = REPO_ROOT / "data" / "product-bundles"
PHOTO_TAGS = ("source-photo", "photo-front")

# Bundles whose photo already differed from the registry reference when this guard
# landed. Each needs an eyes-on review against the reference before it is repointed.
# The list may only shrink: a fixed entry fails test_divergent_list_is_current.
KNOWN_DIVERGENT = frozenset(
    {"br-001", "br-002", "br-005", "br-006", "br-011", "lh-004", "lh-005", "sg-002"}
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _bundle_photos() -> list[tuple[str, Path]]:
    photos = []
    for manifest in sorted(BUNDLES.glob("*/manifest.json")):
        data = json.loads(manifest.read_text(encoding="utf-8"))
        for tag in PHOTO_TAGS:
            name = data.get("files", {}).get(tag)
            if name:
                photos.append((data["sku"], manifest.parent / name))
    return photos


def _matches_reference(sku: str, photo: Path) -> bool:
    reference = get_product(sku)["render_sources"]["reference"]
    assert reference, f"{sku}: registry has no render_sources.reference"
    return _sha(photo) == _sha(REPO_ROOT / reference)


PHOTOS = _bundle_photos()


def test_bundles_with_photos_exist() -> None:
    skus = {sku for sku, _ in PHOTOS}
    assert {"kids-001", "kids-002"} <= skus


@pytest.mark.parametrize(("sku", "photo"), PHOTOS, ids=[p.parent.name for _, p in PHOTOS])
def test_bundle_photo_is_the_registry_reference(sku: str, photo: Path) -> None:
    assert photo.is_file(), f"{photo} is listed in its manifest but missing"
    if sku in KNOWN_DIVERGENT:
        pytest.skip(f"{sku}: pending review against the registry reference")
    assert _matches_reference(
        sku, photo
    ), f"{photo.relative_to(REPO_ROOT)} is not a byte copy of {sku}'s registry reference"


def test_divergent_list_is_current() -> None:
    fixed = sorted(
        sku for sku, photo in PHOTOS if sku in KNOWN_DIVERGENT and _matches_reference(sku, photo)
    )
    assert not fixed, f"now match the registry; drop from KNOWN_DIVERGENT: {fixed}"
    unknown = sorted(KNOWN_DIVERGENT - {sku for sku, _ in PHOTOS})
    assert not unknown, f"no bundle photo for: {unknown}"
