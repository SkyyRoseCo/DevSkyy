"""Single editable product authority; CSV and dossier files are projections."""

from __future__ import annotations

import copy
import csv
import fcntl
import json
import os
import stat
import tempfile
from pathlib import Path
from typing import Any

PRODUCT_REGISTRY = (
    Path(__file__).resolve().parents[2]
    / "wordpress-theme/skyyrose-flagship/data/logo-registry.json"
)


def load_registry(path: Path | None = None) -> dict[str, Any]:
    """Read current authoritative bytes, never fall back to a stale export."""
    target = path or PRODUCT_REGISTRY
    raw = json.loads(target.read_text(encoding="utf-8"))
    products = raw.get("products")
    if not isinstance(products, dict) or not products:
        raise ValueError(f"Unified products missing from {target}")
    for sku, product in products.items():
        if product.get("catalog", {}).get("sku") != sku:
            raise ValueError(f"Registry product/catalog SKU mismatch: {sku}")
    return raw


def catalog_rows(path: Path | None = None) -> list[dict[str, str]]:
    raw = load_registry(path)
    return [_catalog_projection(p, raw["catalog_columns"]) for p in raw["products"].values()]


def _catalog_projection(product: dict[str, Any], columns: list[str]) -> dict[str, str]:
    row = copy.deepcopy(product["catalog"])
    garment = product.get("garment", {})
    for key in row:
        if key.lower() == "color" and "color" in garment:
            row[key] = garment["color"]
        if key.lower() == "sizes" and "available_sizes" in garment:
            row[key] = "|".join(garment["available_sizes"])
        if key in {"image", "front_model_image", "back_image", "back_model_image"}:
            row[key] = product.get("images", {}).get(key, {}).get("path", "")
    for field in ("fit", "materials", "features"):
        if field in columns:
            row[field] = garment.get(field, {}).get("specification") or ""
    if "sizing_references" in columns:
        row["sizing_references"] = json.dumps(
            garment.get("sizing_references", {}), ensure_ascii=False, sort_keys=True
        )
    return row


def _atomic_write(path: Path, content: str) -> None:
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            os.fchmod(handle.fileno(), mode)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def update_catalog_fields(sku: str, changes: dict[str, str], path: Path | None = None) -> None:
    """Atomically update one product, preserving unrelated concurrent fields.

    Image-column changes update the corresponding effective image binding in
    the same transaction. Compatibility projections are written before the
    registry commit, under the same lock, and restored if the commit fails.
    """
    target = path or PRODUCT_REGISTRY
    with target.with_suffix(".json.lock").open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        raw = load_registry(target)
        product = raw["products"][sku]
        allowed = set(raw["catalog_columns"]) - {
            "sku",
            "dossier_slug",
            "fit",
            "materials",
            "features",
            "sizing_references",
        }
        if not set(changes) <= allowed:
            raise ValueError("Unknown or identity-changing catalog fields")
        if any(not isinstance(value, str) for value in changes.values()):
            raise ValueError("Catalog field values must remain strings")
        for key, value in changes.items():
            product["catalog"][key] = value
            if key.lower() == "color":
                product.setdefault("garment", {})["color"] = value
            if key.lower() == "sizes":
                product.setdefault("garment", {})["available_sizes"] = value.split("|")
            if key in {"image", "front_model_image", "back_image", "back_model_image"}:
                if value.startswith("/") or ".." in Path(value).parts:
                    raise ValueError("Product image must be a safe theme-relative path")
                if value:
                    product.setdefault("images", {})[key] = {"path": value}
                else:
                    product.setdefault("images", {}).pop(key, None)
        outputs = _compatibility_outputs(raw, target)
        previous = {p: p.read_text() if p.exists() else None for p in outputs}
        touched = []
        try:
            for destination, content in outputs.items():
                if previous[destination] != content:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    _atomic_write(destination, content)
                    touched.append(destination)
            # Commit last. A failure leaves the old authoritative record valid.
            _atomic_write(target, json.dumps(raw, ensure_ascii=False, indent=2) + "\n")
        except BaseException:
            for destination in reversed(touched):
                if previous[destination] is None:
                    destination.unlink(missing_ok=True)
                else:
                    _atomic_write(destination, previous[destination])
            raise


def _compatibility_outputs(raw: dict[str, Any], target: Path) -> dict[Path, str]:
    import io

    from skyyrose.core.dossier_loader import project_registry_dossier

    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=raw["catalog_columns"], lineterminator="\n")
    writer.writeheader()
    writer.writerows(
        _catalog_projection(p, raw["catalog_columns"]) for p in raw["products"].values()
    )
    outputs = {target.parent / "skyyrose-catalog.csv": stream.getvalue()}
    for product in raw["products"].values():
        dossier = product["dossier"]
        slug = dossier["slug"]
        if Path(slug).name != slug or slug in {".", ".."}:
            raise ValueError(f"Unsafe dossier slug: {slug!r}")
        outputs[target.parent / "dossiers" / f"{slug}.md"] = project_registry_dossier(product).raw
    return outputs


def export_compatibility(path: Path | None = None, *, check: bool = False) -> list[str]:
    """Serialize export reads/writes with product updates to prevent stale exports."""
    target = path or PRODUCT_REGISTRY
    with target.with_suffix(".json.lock").open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_SH if check else fcntl.LOCK_EX)
        outputs = _compatibility_outputs(load_registry(target), target)
        drift = []
        for destination, content in outputs.items():
            existing = destination.read_text() if destination.exists() else None
            if existing != content:
                drift.append(str(destination))
                if not check:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    _atomic_write(destination, content)
        return drift
