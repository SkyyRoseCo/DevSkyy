"""Per-tenant catalog access. SkyyRose impl wraps the locked dossier loader.

The protocol generalizes ground-truth resolution so tenant #2 implements its
own source without touching the platform core. SkyyRose's source resolves the
single editable registry plus separately managed golden evaluation references; DossierMissingError
propagates (no silent fallback).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, runtime_checkable

from skyyrose.core.paths import GOLDEN_DIR
from skyyrose.elite_studio.quality.visual_regression import CANONICAL_ANGLES


@dataclass(frozen=True)
class ProductRecord:
    """A resolved product: registry projection + parsed dossier + complete product record."""

    sku: str
    name: str
    collection: str
    garment_type_lock: str
    dossier: dict  # full dossier.to_dict()
    row: dict = field(default_factory=dict, repr=False)
    product: dict = field(default_factory=dict, repr=False)


@runtime_checkable
class CatalogSource(Protocol):
    """Per-tenant ground-truth resolution."""

    def get(self, sku: str) -> ProductRecord: ...
    def references(self, sku: str) -> dict[str, Path]: ...


class SkyyRoseCatalogSource:
    """Tenant #1 source — reads the unified product registry; golden references are evaluation fixtures."""

    def __init__(self, reference_root: Path | None = None) -> None:
        self._reference_root = Path(reference_root or GOLDEN_DIR)

    def get(self, sku: str) -> ProductRecord:
        from skyyrose.core.product import get_product

        merged = get_product(sku)  # raises KeyError / DossierMissingError
        dossier = merged["dossier"]
        return ProductRecord(
            sku=sku,
            name=dossier.get("name", ""),
            collection=dossier.get("collection", ""),
            garment_type_lock=dossier.get("garment_type_lock", ""),
            dossier=dossier,
            row=merged["catalog_row"],
            product=merged,
        )

    def references(self, sku: str) -> dict[str, Path]:
        """Return {angle: path} for every golden view that exists on disk.

        Honors the legacy reference.jpg=front convention. Missing views are
        omitted (not faked) — the gate marks omitted angles 'inferred'.
        """
        sku_dir = self._reference_root / sku
        out: dict[str, Path] = {}
        for angle in CANONICAL_ANGLES:
            candidate = sku_dir / f"{angle}.jpg"
            if candidate.is_file():
                out[angle] = candidate
            elif angle == "front" and (sku_dir / "reference.jpg").is_file():
                out[angle] = sku_dir / "reference.jpg"
        return out
