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

# Vercel builds the dashboard from frontend/, so its serverless functions cannot
# read the monorepo parent; they read this byte-for-byte copy of the catalog
# projection instead. It is generated here like every other projection, so a
# registry edit refreshes it and ``--check`` fails the moment it drifts.
FRONTEND_CATALOG_REPLICA = (
    Path(__file__).resolve().parents[2] / "frontend/data/skyyrose-catalog.csv"
)
# The real registry file, fixed at import. The replica belongs to it alone: a
# caller (or test) that points PRODUCT_REGISTRY at a copy must never rewrite the
# tracked dashboard replica from that copy.
_CANONICAL_REGISTRY = PRODUCT_REGISTRY.resolve()

# Dossier files the founder chose to keep that no product projects to. Each is
# exempt from the orphan check by exact filename only, with the reason; any
# other unowned dossier still fails it. tests/test_unified_product_registry.py
# fails if an entry's file disappears or its name becomes a registry slug.
RETAINED_DOSSIERS: dict[str, str] = {
    "black-rose-bomber-sherpa.md": (
        "Earlier dossier for br-006 The Bomber Sherpa, whose registry dossier is "
        "black-rose-sherpa-jacket. Kept as-is by founder decision, 2026-09-18."
    ),
}


def _registry_target(path: Path | None) -> Path:
    """The real file behind the registry path.

    The repo-root ``logo-registry.json`` is a symlink to the theme copy. Writing
    through the unresolved link would replace it with a regular file and drop the
    projections next to it — forking the SOT.
    """
    return (path or PRODUCT_REGISTRY).resolve()


def load_registry(path: Path | None = None) -> dict[str, Any]:
    """Read current authoritative bytes, never fall back to a stale export."""
    target = _registry_target(path)
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


def update_catalog_fields(sku: str, changes: dict[str, str], path: Path | None = None) -> list[str]:
    """Atomically update one product, preserving unrelated concurrent fields.

    Returns the catalog keys whose value actually changed, read under the lock.

    Image-column changes update the corresponding effective image binding in
    the same transaction. Compatibility projections are written before the
    registry commit, under the same lock, and restored if the commit fails.
    """
    target = _registry_target(path)
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
        changed = sorted(k for k, v in changes.items() if product["catalog"].get(k) != v)
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
    return changed


MERCHANDISING_SERIES = {"jersey-series": frozenset({"oakland", "san-francisco", "san-jose"})}


def validate_merchandising(value: Any) -> None:
    """Reject unknown route assignments and malformed ordering, including booleans."""
    if not isinstance(value, dict) or set(value) != {
        "series_slug",
        "series_region",
        "series_order",
    }:
        raise ValueError("Merchandising requires series_slug, series_region, series_order")
    slug, region, order = (value[key] for key in ("series_slug", "series_region", "series_order"))
    if not isinstance(slug, str) or not isinstance(region, str) or type(order) is not int:
        raise ValueError("Merchandising slug/region must be strings and order an integer")
    if not slug:
        if region or order != 0:
            raise ValueError("Unassigned merchandising must have empty region and zero order")
    elif slug not in MERCHANDISING_SERIES or region not in MERCHANDISING_SERIES[slug]:
        raise ValueError(f"Unknown merchandising series or region: {slug!r}/{region!r}")
    elif order <= 0:
        raise ValueError("Assigned merchandising order must be positive")


def update_product_merchandising(
    assignments: dict[str, dict[str, Any]],
    *,
    source: str,
    only_missing: bool = False,
    path: Path | None = None,
) -> list[str]:
    """Atomically write route configuration without altering founder product facts.

    Validate the entire batch before committing. ``only_missing`` supports a
    one-time migration without overwriting a current canonical assignment.
    Merchandising is not included in CSV or dossier compatibility projections.
    """
    if not isinstance(source, str) or not source.strip():
        raise ValueError("Merchandising source must identify its provenance")
    target = _registry_target(path)
    with target.with_suffix(".json.lock").open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        raw = load_registry(target)
        changed = []
        for sku, value in assignments.items():
            if sku not in raw["products"]:
                raise KeyError(f"SKU {sku!r} is not in the product registry")
            validate_merchandising(value)
            product = raw["products"][sku]
            if only_missing and "merchandising" in product:
                continue
            if product.get("merchandising") == value:
                continue
            product["merchandising"] = copy.deepcopy(value)
            product["merchandising_provenance"] = {
                "source": source,
                "kind": "ROUTE_CONFIGURATION",
            }
            changed.append(sku)
        # Check the final set, not intermediate edits: a batch may legitimately
        # swap positions, but must not commit a collision with an unchanged SKU.
        positions: dict[tuple[str, int], str] = {}
        for sku, product in raw["products"].items():
            value = product.get("merchandising")
            if value is None:
                continue
            validate_merchandising(value)
            if not value["series_slug"]:
                continue
            position = (value["series_slug"], value["series_order"])
            if position in positions:
                raise ValueError(
                    f"Duplicate merchandising series/order {position!r}: "
                    f"{positions[position]} and {sku}"
                )
            positions[position] = sku
        if changed:
            _atomic_write(target, json.dumps(raw, ensure_ascii=False, indent=2) + "\n")
    return changed


CONTENT_FIELDS = ("description", "short_description", "seo_meta", "instagram", "tiktok")
CONTENT_AUTHORITIES = frozenset({"FOUNDER_AUTHORED", "AGENT_GENERATED"})


def _copy_record(value: str, authority: str, source: str, updated: str) -> dict[str, str]:
    """One piece of copy plus who wrote it. Rejects anything unlabelled or blank."""
    if authority not in CONTENT_AUTHORITIES:
        raise ValueError(f"Unknown content authority {authority!r}")
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Content must be a non-empty string")
    return {"value": value, "authority": authority, "source": source, "updated": updated}


def _write_content(sku: str, path: Path | None, apply: Any) -> str | None:
    """Apply ``apply(product, content)`` to ``products[sku].content`` under the lock.

    Content is not part of any compatibility projection, so only the registry is
    rewritten, under the same lock as catalog edits. Returns the replaced value.
    """
    target = _registry_target(path)
    with target.with_suffix(".json.lock").open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        raw = load_registry(target)
        if sku not in raw["products"]:
            raise KeyError(f"SKU {sku!r} is not in the product registry")
        product = raw["products"][sku]
        content = copy.deepcopy(product.get("content", {}))
        previous = apply(product, content)
        raw["products"][sku] = _with_section_before(product, "authority", "content", content)
        _atomic_write(target, json.dumps(raw, ensure_ascii=False, indent=2) + "\n")
    return previous["value"] if isinstance(previous, dict) else None


def update_product_content(
    sku: str,
    field: str,
    value: str,
    *,
    authority: str,
    source: str,
    updated: str,
    path: Path | None = None,
) -> str | None:
    """Write one copy field into ``products[sku].content`` and return the old value.

    Copy lives in the registry like every other product fact. Each field records
    who wrote it, so agent copy can never be mistaken for the founder's words.
    """
    if field not in CONTENT_FIELDS:
        raise ValueError(f"Unknown content field {field!r}; expected one of {CONTENT_FIELDS}")
    record = _copy_record(value, authority, source, updated)

    def apply(_product: dict[str, Any], content: dict[str, Any]) -> Any:
        previous = content.get(field)
        content[field] = record
        return previous

    return _write_content(sku, path, apply)


def update_product_alt_text(
    sku: str,
    image_stem: str,
    value: str,
    *,
    authority: str,
    source: str,
    updated: str,
    path: Path | None = None,
) -> str | None:
    """Write alt text for one of the product's registry-bound images.

    ``image_stem`` is the file stem of an ``images[*].path`` bound to this SKU.
    Alt text for an image the registry does not bind is refused: it would
    describe a picture no product page can show.
    """
    record = _copy_record(value, authority, source, updated)

    def apply(product: dict[str, Any], content: dict[str, Any]) -> Any:
        bound = {
            Path(binding["path"]).stem
            for binding in product.get("images", {}).values()
            if isinstance(binding, dict) and binding.get("path")
        }
        if image_stem not in bound:
            raise ValueError(
                f"{image_stem!r} is not an image bound to {sku}; bound: {sorted(bound)}"
            )
        alt_text = content.setdefault("alt_text", {})
        previous = alt_text.get(image_stem)
        alt_text[image_stem] = record
        return previous

    return _write_content(sku, path, apply)


def _with_section_before(
    product: dict[str, Any], anchor: str, key: str, value: Any
) -> dict[str, Any]:
    """``product`` with ``key`` set, placed before ``anchor`` when it is new."""
    if key in product:
        return {**product, key: value}
    out: dict[str, Any] = {}
    for existing, section in product.items():
        if existing == anchor:
            out[key] = value
        out[existing] = section
    out.setdefault(key, value)
    return out


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
    if target == _CANONICAL_REGISTRY:
        outputs[FRONTEND_CATALOG_REPLICA] = stream.getvalue()
    for product in raw["products"].values():
        dossier = product["dossier"]
        slug = dossier["slug"]
        if Path(slug).name != slug or slug in {".", ".."}:
            raise ValueError(f"Unsafe dossier slug: {slug!r}")
        outputs[target.parent / "dossiers" / f"{slug}.md"] = project_registry_dossier(product).raw
    return outputs


def _orphan_dossiers(raw: dict[str, Any], target: Path) -> list[Path]:
    """Dossier files no product projects to: product facts authored outside the registry.

    Only the projections the registry expects are otherwise compared, so a
    hand-authored or unbound dossier would never be examined. It is reported as
    drift and never deleted — it may be founder data awaiting a registry binding.
    Files named in ``RETAINED_DOSSIERS`` are kept by founder decision.
    """
    expected = {f"{product['dossier']['slug']}.md" for product in raw["products"].values()}
    exempt = expected | set(RETAINED_DOSSIERS) | {"_template.md"}
    dossiers_dir = target.parent / "dossiers"
    return sorted(
        candidate for candidate in dossiers_dir.glob("*.md") if candidate.name not in exempt
    )


def orphan_dossiers(path: Path | None = None) -> list[Path]:
    """Dossier files present on disk that no registry product owns."""
    target = _registry_target(path)
    return _orphan_dossiers(load_registry(target), target)


def export_compatibility(path: Path | None = None, *, check: bool = False) -> list[str]:
    """Serialize export reads/writes with product updates to prevent stale exports.

    Returns every drifted path: stale or missing projections (rewritten unless
    ``check``) and orphan dossiers (reported, never touched).
    """
    target = _registry_target(path)
    with target.with_suffix(".json.lock").open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_SH if check else fcntl.LOCK_EX)
        raw = load_registry(target)
        outputs = _compatibility_outputs(raw, target)
        drift = []
        for destination, content in outputs.items():
            existing = destination.read_text() if destination.exists() else None
            if existing != content:
                drift.append(str(destination))
                if not check:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    _atomic_write(destination, content)
        drift.extend(str(orphan) for orphan in _orphan_dossiers(raw, target))
        return drift


def _main(argv: list[str] | None = None) -> int:
    """``update <sku> [--registry PATH]``: apply a JSON ``{field: value}`` patch from stdin.

    The one write entry point for non-Python callers (the dashboard's admin
    catalog editor). It calls ``update_catalog_fields`` so the registry changes
    and the CSV/dossier projections regenerate in the same transaction. Prints
    one JSON object on stdout; a rejected patch, unknown SKU, malformed input or
    unreadable registry exits 1 with ``{"ok": false, "error": ...}``.
    """
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        prog="python -m skyyrose.core.product_registry",
        description="Write product catalog fields through the single registry.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    update = commands.add_parser("update", help="patch one SKU from a JSON object on stdin")
    update.add_argument("sku")
    update.add_argument("--registry", type=Path, default=None, help="registry JSON path")
    args = parser.parse_args(argv)

    try:
        changes = json.load(sys.stdin)
        if not isinstance(changes, dict) or not changes:
            raise ValueError("Patch must be a non-empty JSON object of {field: value}")
        target = _registry_target(args.registry)
        changed = update_catalog_fields(args.sku, changes, target)
    except KeyError as exc:
        print(json.dumps({"ok": False, "error": f"SKU not found: {exc.args[0]}"}))
        return 1
    except (ValueError, OSError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 1
    print(json.dumps({"ok": True, "sku": args.sku, "changed": changed, "registry": str(target)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
