"""Single editable product authority; CSV and dossier files are projections."""

from __future__ import annotations

import copy
import csv
import fcntl
import hashlib
import io
import json
import os
import re
import stat
import subprocess
import sys
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
V2_CARD_FRONT_PROJECTION = (
    Path(__file__).resolve().parents[2]
    / "wordpress-theme/skyyrose-flagship-2/data/approved-card-fronts.json"
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


def import_storefront_card_projection(projection: Path, path: Path | None = None) -> None:
    """Move existing card bindings into the registry without changing product facts.

    This is a source migration, not a visual approval. All existing rejection and
    scoped approval metadata is retained verbatim. An existing canonical binding
    cannot be overwritten by an older projection.
    """
    from jsonschema import Draft202012Validator, ValidationError

    schema = json.loads(_CANONICAL_REGISTRY.with_name("logo-registry.schema.json").read_text())
    binding_validator = Draft202012Validator(schema["$defs"]["cardFrontBinding"])
    metadata_validator = Draft202012Validator(schema["properties"]["storefront_card_manifest"])
    target = _registry_target(path)
    with target.with_suffix(".json.lock").open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        raw = load_registry(target)
        cards = json.loads(projection.read_text(encoding="utf-8"))
        if not isinstance(cards, dict):
            raise ValueError("Invalid storefront card projection metadata")
        records = cards.get("products")
        if not isinstance(records, dict) or set(records) != set(raw["products"]):
            raise ValueError("Storefront card projection must cover the exact registry SKU set")
        metadata = {key: value for key, value in cards.items() if key != "products"}
        try:
            metadata_validator.validate(metadata)
            for record in records.values():
                binding_validator.validate(record)
        except ValidationError as error:
            raise ValueError("Invalid storefront card projection: " + error.message) from error
        for sku, record in records.items():
            existing = raw["products"][sku].get("images", {}).get("card_front")
            if existing is not None and existing != record:
                raise ValueError(f"Canonical card binding conflicts with projection: {sku}")
        if raw.get("storefront_card_manifest", metadata) != metadata:
            raise ValueError("Canonical card metadata conflicts with projection")
        for sku, record in records.items():
            raw["products"][sku].setdefault("images", {})["card_front"] = record
        raw["storefront_card_manifest"] = metadata
        outputs = _compatibility_outputs(raw, target)
        previous = {p: p.read_text() if p.exists() else None for p in outputs}
        touched = []
        try:
            for destination, content in outputs.items():
                if previous[destination] != content:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    _atomic_write(destination, content)
                    touched.append(destination)
            # Commit authority last, under the same lock as catalog writers.
            _atomic_write(target, json.dumps(raw, ensure_ascii=False, indent=2) + "\n")
        except BaseException:
            for destination in reversed(touched):
                if previous[destination] is None:
                    destination.unlink(missing_ok=True)
                else:
                    _atomic_write(destination, previous[destination])
            raise


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
    for field in ("fit", "materials", "features", "care_instructions"):
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
            "care_instructions",
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


def _bound_review_file(root: Path, binding: Any) -> Path:
    """Resolve an exact, normalized evidence binding without following aliases."""
    if not isinstance(binding, dict) or set(binding) != {"path", "sha256"}:
        raise ValueError("Review dependency requires exact path/hash fields")
    relative, digest = binding["path"], binding["sha256"]
    if (
        not isinstance(relative, str)
        or "\\" in relative
        or Path(relative).is_absolute()
        or Path(relative).as_posix() != relative
        or any(part in {"", ".", ".."} for part in relative.split("/"))
        or not isinstance(digest, str)
        or not re.fullmatch(r"[a-f0-9]{64}", digest)
    ):
        raise ValueError("Invalid normalized review dependency")
    if root.is_symlink():
        raise ValueError("Symlink evidence roots are not permitted")
    ancestor = root
    for part in Path(relative).parts:
        ancestor /= part
        if ancestor.is_symlink():
            raise ValueError("Symlink review dependencies are not permitted")
    candidate = root / relative
    if not candidate.is_file() or not candidate.resolve().is_relative_to(root.resolve()):
        raise ValueError("Review dependency is missing or outside evidence root")
    if hashlib.sha256(candidate.read_bytes()).hexdigest() != digest:
        raise ValueError("Review dependency hash changed")
    return candidate


def _snapshot_dependency(dependencies: dict, path: Path, expected: str | None = None) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ValueError("Source association dependency is missing or aliased")
    raw = path.read_bytes()
    identity = (hashlib.sha256(raw).hexdigest(), path.resolve())
    if expected is not None and identity[0] != expected:
        raise ValueError("Source association dependency drift")
    if path in dependencies and dependencies[path] != identity:
        raise ValueError("Source association dependency drift during validation")
    dependencies[path] = identity
    return raw


def _revalidate_dependencies(dependencies: dict) -> None:
    for path, (digest, resolved) in dependencies.items():
        if (
            path.is_symlink()
            or not path.is_file()
            or path.resolve() != resolved
            or hashlib.sha256(path.read_bytes()).hexdigest() != digest
        ):
            raise ValueError("Source association dependency drift: " + str(path))


def _check_nested_review_bindings(root: Path, value: Any, dependencies: dict) -> None:
    if isinstance(value, dict):
        if "path" in value and "sha256" in value:
            path = _bound_review_file(root, {key: value[key] for key in ("path", "sha256")})
            _snapshot_dependency(dependencies, path, value["sha256"])
        for nested in value.values():
            _check_nested_review_bindings(root, nested, dependencies)
    elif isinstance(value, list):
        for nested in value:
            _check_nested_review_bindings(root, nested, dependencies)


def _reviewed_card_records(
    assignments: dict[str, str],
    *,
    theme: Path,
    evidence_root: Path,
    dependencies: dict | None = None,
) -> dict[str, dict[str, Any]]:
    """Reuse the actual package eligibility gate in one isolated batch process."""
    from PIL import Image

    from skyyrose.core.card_annotations import _asset_path
    from skyyrose.core.native_review import REVIEW_CHECKS, NativeVisualReceipt

    root = Path(__file__).resolve().parents[2]
    assignments = copy.deepcopy(assignments)
    dependencies = dependencies if dependencies is not None else {}
    for relative in (
        "skyyrose/core/product_registry.py",
        "skyyrose/core/card_annotations.py",
        "skyyrose/core/product.py",
        "skyyrose/core/context_resolver.py",
        "skyyrose/core/creative_job.py",
        "skyyrose/core/native_review.py",
        "tools/v2-source-certification/inputs.py",
    ):
        _snapshot_dependency(dependencies, root / relative)
    module = root / "tools/v2-source-certification/package.py"
    module_digest = hashlib.sha256(_snapshot_dependency(dependencies, module)).hexdigest()
    inventory_path = theme / "data/v2-media-eligibility.json"
    if theme.is_symlink() or inventory_path.is_symlink() or inventory_path.parent.is_symlink():
        raise ValueError("Symlink V2 inventory/theme is not permitted")
    inventory_bytes = _snapshot_dependency(dependencies, inventory_path)
    inventory_digest = hashlib.sha256(inventory_bytes).hexdigest()
    inventory = json.loads(inventory_bytes)
    if inventory.get("schema") != "skyyrose.v2.media-eligibility.v1":
        raise ValueError("Invalid V2 eligibility inventory schema")
    for sku, relative in assignments.items():
        if not isinstance(relative, str) or not re.fullmatch(
            rf"assets/v2-original/products/{re.escape(sku)}\.(?:png|webp|jpe?g)", relative
        ):
            raise ValueError("Card front must be its exact SKU's V2 original master")
        _asset_path(theme, relative)
    payload = {
        "module": str(module),
        "module_sha256": module_digest,
        "theme": str(theme.resolve()),
        "inventory_sha256": inventory_digest,
        "paths": list(assignments.values()),
    }
    # Data-only stdin, no shell, no process-global module or THEME mutation.
    script = """
import hashlib, json, sys
from pathlib import Path
p = json.load(sys.stdin)
module = Path(p['module'])
assert hashlib.sha256(module.read_bytes()).hexdigest() == p['module_sha256']
sys.path.insert(0, str(module.parent))
import package
package.THEME = Path(p['theme'])
raw = (package.THEME / 'data/v2-media-eligibility.json').read_bytes()
assert hashlib.sha256(raw).hexdigest() == p['inventory_sha256']
inventory = json.loads(raw)
print(json.dumps({relative: package.eligible_media(relative, inventory) for relative in p['paths']}))
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        cwd=root,
        timeout=60,
        env={"PATH": "/usr/bin:/bin", "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if result.returncode != 0:
        raise ValueError("Current package eligibility subprocess failed closed")
    verified = json.loads(result.stdout)
    if set(verified) != set(assignments.values()) or any(v is not True for v in verified.values()):
        raise ValueError("Current independent V2 master eligibility rejected")
    if (
        hashlib.sha256(inventory_path.read_bytes()).hexdigest() != inventory_digest
        or hashlib.sha256(module.read_bytes()).hexdigest() != module_digest
    ):
        raise ValueError("V2 eligibility inputs changed during batch verification")
    records = {}
    for sku, relative in assignments.items():
        record = inventory["assets"][relative]
        if (
            record.get("status") not in {"INDEPENDENT_VISUAL_PASS", "FOUNDER_ACCEPTED"}
            or record.get("kind") != "photograph"
            or record.get("skus") != [sku]
            or "card_front" not in record.get("roles", [])
            or not isinstance(record.get("collections"), list)
            or len(record["collections"]) != 1
        ):
            raise ValueError("V2 master is not a unique independently reviewed product front")
        asset = _asset_path(theme, relative)
        asset_bytes = _snapshot_dependency(dependencies, asset, record["sha256"])
        with Image.open(io.BytesIO(asset_bytes)) as image:
            formats = {".png": "PNG", ".webp": "WEBP", ".jpg": "JPEG", ".jpeg": "JPEG"}
            if (
                min(image.size) < 1024
                or max(image.size) > 4096
                or image.format != formats[asset.suffix]
            ):
                raise ValueError("V2 card master requires full-resolution native pixels")
        review = record["review"]
        receipt = _bound_review_file(theme, {k: review[k] for k in ("path", "sha256")})
        evidence = json.loads(_snapshot_dependency(dependencies, receipt, review["sha256"]))
        if record["status"] == "FOUNDER_ACCEPTED":
            if record["roles"] != ["card_front"]:
                raise ValueError("Founder card acceptance cannot broaden to another role")
            source = _bound_review_file(theme, evidence["decision_source"])
            _snapshot_dependency(dependencies, source, evidence["decision_source"]["sha256"])
            records[sku] = copy.deepcopy(record)
            continue
        if not isinstance(evidence.get("native_review"), dict):
            raise ValueError("Actual typed native independent review is required")
        native_path = _bound_review_file(evidence_root, evidence["native_review"])
        native = NativeVisualReceipt.model_validate_json(
            _snapshot_dependency(dependencies, native_path, evidence["native_review"]["sha256"])
        )
        reviewer = native.reviewer.strip().casefold()
        if (
            native.status != "PASS"
            or native.method != "ACTUAL_PIXEL_INSPECTION"
            or set(native.checks) != REVIEW_CHECKS
            or any(v != "PASS" for v in native.checks.values())
            or not reviewer
            or reviewer != review["reviewer"].strip().casefold()
            or reviewer == record["producer"].strip().casefold()
            or native.operation_id != record["production_id"]
            or native.candidate != native.full_size_pixels
            or native.candidate.sha256 != record["sha256"]
        ):
            raise ValueError("Native independent review differs from exact actual V2 master")
        native_data = native.model_dump(mode="json")
        _check_nested_review_bindings(evidence_root, native_data, dependencies)
        contexts = evidence.get("contexts")
        required_contexts = {"card_desktop", "card_mobile"}
        if "pdp_on_model_front" in record["roles"]:
            required_contexts |= {"pdp_desktop", "pdp_mobile"}
        supported_contexts = required_contexts | {"card_tablet"}
        if "pdp_on_model_front" in record["roles"]:
            supported_contexts |= {"pdp_tablet"}
        if (
            not isinstance(contexts, dict)
            or not required_contexts <= set(contexts)
            or not set(contexts) <= supported_contexts
        ):
            raise ValueError("Exact applicable card/PDP role contexts are required")
        if (
            contexts["card_desktop"] != native_data["desktop_card"]
            or contexts["card_mobile"] != native_data["mobile_card"]
        ):
            raise ValueError("Role context differs from native reviewed card context")
        for binding in contexts.values():
            context_path = _bound_review_file(evidence_root, binding)
            _snapshot_dependency(dependencies, context_path, binding["sha256"])
        records[sku] = copy.deepcopy(record)
    _revalidate_dependencies(dependencies)
    return records


def update_reviewed_card_fronts(
    assignments: dict[str, str],
    *,
    path: Path | None = None,
    theme_root: Path | None = None,
    evidence_root: Path | None = None,
) -> list[str]:
    """Atomically bind eligible V2 masters with their actual review class.

    Only images.card_front changes. Original image/source facts remain intact;
    compatibility projections commit before authority and roll back on failure.
    """
    if (
        not isinstance(assignments, dict)
        or not assignments
        or any(not isinstance(sku, str) for sku in assignments)
    ):
        raise ValueError("Reviewed card fronts require a nonempty SKU/path batch")
    assignments = copy.deepcopy(assignments)
    from jsonschema import Draft202012Validator, ValidationError

    root = Path(__file__).resolve().parents[2]
    theme = theme_root or root / "wordpress-theme/skyyrose-flagship-2"
    evidence = evidence_root or root
    target = _registry_target(path)
    if target == _CANONICAL_REGISTRY and (
        theme.resolve() != (root / "wordpress-theme/skyyrose-flagship-2").resolve()
        or evidence.resolve() != root.resolve()
    ):
        raise ValueError("Canonical product authority requires its own V2 theme/evidence roots")
    with target.with_suffix(".json.lock").open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        dependencies = {}
        previous_authority = _snapshot_dependency(dependencies, target).decode("utf-8")
        schema = json.loads(
            _snapshot_dependency(
                dependencies, _CANONICAL_REGISTRY.with_name("logo-registry.schema.json")
            )
        )
        validator = Draft202012Validator(schema["$defs"]["cardFrontBinding"])
        raw = load_registry(target)
        _revalidate_dependencies(dependencies)
        for sku in assignments:
            if sku not in raw["products"]:
                raise KeyError(f"SKU {sku!r} is not in the product registry")
        records = _reviewed_card_records(
            assignments, theme=theme, evidence_root=evidence, dependencies=dependencies
        )
        changed = []
        for sku, record in records.items():
            product = raw["products"][sku]
            if record["collections"] != [product["catalog"]["collection"]]:
                raise ValueError("Reviewed V2 collection differs from current product authority")
            name = product["catalog"].get("name")
            if not isinstance(name, str) or not name.strip():
                raise ValueError("Missing canonical product name for card alt text")
            from PIL import Image

            asset_bytes = _snapshot_dependency(
                dependencies, theme / assignments[sku], record["sha256"]
            )
            with Image.open(io.BytesIO(asset_bytes)) as image:
                width, height = image.size
            founder = record["status"] == "FOUNDER_ACCEPTED"
            binding = {
                "src": assignments[sku],
                "width": width,
                "height": height,
                "alt": name,
                "source_sha256": record["sha256"],
                "sha256": record["sha256"],
                "candidate_id": record["production_id"],
                "scene_status": (
                    "FOUNDER_APPROVED_V2_CARD" if founder else "INDEPENDENT_REVIEWED_V2_CARD"
                ),
                "current_fidelity_status": (
                    "FOUNDER_ACCEPTED" if founder else "INDEPENDENT_VISUAL_PASS"
                ),
                "review": record["review"],
            }
            try:
                validator.validate(binding)
            except ValidationError as error:
                raise ValueError(
                    "Invalid independently reviewed card binding: " + error.message
                ) from error
            if product.get("images", {}).get("card_front") != binding:
                product.setdefault("images", {})["card_front"] = binding
                changed.append(sku)
        if not changed:
            _revalidate_dependencies(dependencies)
            return []
        outputs = _compatibility_outputs(raw, target)
        previous = {p: p.read_text() if p.exists() else None for p in outputs}
        previous[target] = previous_authority
        touched = []
        try:
            for destination, content in outputs.items():
                _revalidate_dependencies(dependencies)
                if previous[destination] != content:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    touched.append(destination)
                    _atomic_write(destination, content)
            _revalidate_dependencies(dependencies)
            content = json.dumps(raw, ensure_ascii=False, indent=2) + "\n"
            touched.append(target)
            _atomic_write(target, content)
            _revalidate_dependencies(
                {p: identity for p, identity in dependencies.items() if p != target}
            )
            if target.read_text() != content:
                raise ValueError("Source association authority changed during final commit")
        except BaseException:
            for destination in reversed(touched):
                if destination.exists() and destination.read_text() == previous[destination]:
                    continue
                if previous[destination] is None:
                    destination.unlink(missing_ok=True)
                else:
                    _atomic_write(destination, previous[destination])
            raise
    return changed


def update_media_usage_adoptions(
    adoptions: dict[str, dict[str, str]],
    placements: dict[str, dict[str, str]],
    *,
    path: Path | None = None,
    theme_root: Path | None = None,
) -> list[str]:
    """Bind unchanged accepted bytes to exact additional uses and collections.

    Original acceptance receipts and product facts remain untouched. Each grant
    is checked against the real package gate, current SKU and current listing.
    Compatibility outputs and authority commit atomically, as for card updates.
    """
    from jsonschema import Draft202012Validator
    from PIL import Image

    from skyyrose.core.media_usage import validated_usage_roles

    root = Path(__file__).resolve().parents[2]
    theme = theme_root or root / "wordpress-theme/skyyrose-flagship-2"
    target = _registry_target(path)
    if not isinstance(adoptions, dict) or not adoptions or not isinstance(placements, dict):
        raise ValueError("Exact nonempty media adoption and placement maps are required")
    if (
        target == _CANONICAL_REGISTRY
        and theme.resolve() != (root / "wordpress-theme/skyyrose-flagship-2").resolve()
    ):
        raise ValueError("Canonical media grants require this checkout's V2 theme")
    adoptions, placements = copy.deepcopy(adoptions), copy.deepcopy(placements)
    with target.with_suffix(".json.lock").open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        dependencies: dict = {}
        previous_authority = _snapshot_dependency(dependencies, target).decode("utf-8")
        raw = json.loads(previous_authority)
        inventory_path = theme / "data/v2-media-eligibility.json"
        inventory = json.loads(_snapshot_dependency(dependencies, inventory_path))
        if inventory.get("schema") != "skyyrose.v2.media-eligibility.v1":
            raise ValueError("Invalid media inventory")
        module = root / "tools/v2-source-certification/package.py"
        _snapshot_dependency(dependencies, module)
        _snapshot_dependency(dependencies, root / "skyyrose/core/media_usage.py")
        payload = {"theme": str(theme.resolve()), "paths": sorted(adoptions)}
        process = subprocess.run(
            [
                sys.executable,
                "-c",
                """
import json, sys
from pathlib import Path
sys.path.insert(0, 'tools/v2-source-certification')
import package
p = json.load(sys.stdin)
package.THEME = Path(p['theme'])
i = json.loads((package.THEME / 'data/v2-media-eligibility.json').read_text())
print(json.dumps({s: package.eligible_media(s, i) for s in p['paths']}))
""",
            ],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            cwd=root,
            timeout=60,
        )
        if process.returncode or json.loads(process.stdout) != dict.fromkeys(adoptions, True):
            raise ValueError("An original source acceptance failed the actual package gate")
        sources = {}
        for relative, binding in adoptions.items():
            record = inventory["assets"][relative]
            if (
                not relative.startswith("assets/v2-original/")
                or record.get("kind") != "photograph"
                or len(record.get("skus", [])) != 1
                or len(record.get("collections", [])) != 1
            ):
                raise ValueError("Media adoption requires one exact V2 original SKU/collection")
            original_binding = {key: record["review"][key] for key in ("path", "sha256")}
            original_path = _bound_review_file(theme, original_binding)
            original = json.loads(
                _snapshot_dependency(dependencies, original_path, original_binding["sha256"])
            )
            if record["status"] == "FOUNDER_ACCEPTED":
                owner = _bound_review_file(theme, original["decision_source"])
                _snapshot_dependency(dependencies, owner, original["decision_source"]["sha256"])
            grant_path = _bound_review_file(theme, binding)
            grant = json.loads(_snapshot_dependency(dependencies, grant_path, binding["sha256"]))
            _check_nested_review_bindings(theme, grant, dependencies)
            roles = validated_usage_roles(relative, record, adoptions, theme)
            if not roles:
                raise ValueError("Missing or invalid source-bound founder reuse grant")
            sku, collection = record["skus"][0], record["collections"][0]
            product = raw["products"].get(sku)
            if not product or product["catalog"]["collection"] != collection:
                raise ValueError("Usage collection differs from current product authority")
            if "pdp_on_model_front" in roles:
                front = product.get("images", {}).get("card_front", {})
                if front.get("src") != relative or front.get("sha256") != record["sha256"]:
                    raise ValueError("PDP reuse must be the current canonical product front")
            if "merchandise_scene" in roles and (
                product["catalog"].get("is_preorder") != "1"
                or product["catalog"].get("published") != "1"
            ):
                raise ValueError("Preorder merchandise scene requires a current preorder subject")
            source = theme / relative
            with Image.open(
                io.BytesIO(_snapshot_dependency(dependencies, source, record["sha256"]))
            ) as pixels:
                width, height = pixels.size
            sources[relative] = (record, roles, width, height, product["catalog"]["name"])
        changed = []
        if raw.get("media_usage_adoptions") != adoptions:
            raw["media_usage_adoptions"] = adoptions
            changed.append("media_usage_adoptions")
        for collection, slots in placements.items():
            if collection not in raw["collections"] or not isinstance(slots, dict):
                raise ValueError("Unknown collection placement")
            for role, relative in slots.items():
                if (
                    role not in {"collection_hero", "collection_story", "merchandise_scene"}
                    or relative not in sources
                ):
                    raise ValueError("Unsupported or ungranted collection placement")
                record, roles, width, height, name = sources[relative]
                if role not in roles or record["collections"] != [collection]:
                    raise ValueError("Role/collection differs from its exact source grant")
                bound = {
                    "src": relative,
                    "sha256": record["sha256"],
                    "width": width,
                    "height": height,
                    "sku": record["skus"][0],
                    "role": role,
                    "alt": name,
                    "usage_adoption": adoptions[relative],
                }
                imagery = raw["collections"][collection].setdefault("imagery", {})
                if imagery.get(role) != bound:
                    imagery[role] = bound
                    changed.append(collection + "." + role)
                # ``imagery.hero`` is the v1 collection-hub slot; it resolves
                # against the v1 asset tree, so a V2 theme path never goes there.
        if not changed:
            _revalidate_dependencies(dependencies)
            return []
        schema = json.loads(
            _snapshot_dependency(
                dependencies, _CANONICAL_REGISTRY.with_name("logo-registry.schema.json")
            )
        )
        Draft202012Validator(schema).validate(raw)
        outputs = _compatibility_outputs(raw, target)
        previous = {
            destination: destination.read_text() if destination.exists() else None
            for destination in outputs
        }
        previous[target] = previous_authority
        touched = []
        try:
            for destination, content in outputs.items():
                _revalidate_dependencies(dependencies)
                if previous[destination] != content:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    touched.append(destination)
                    _atomic_write(destination, content)
            _revalidate_dependencies(dependencies)
            content = json.dumps(raw, ensure_ascii=False, indent=2) + "\n"
            touched.append(target)
            _atomic_write(target, content)
            _revalidate_dependencies(
                {p: identity for p, identity in dependencies.items() if p != target}
            )
            if target.read_text() != content:
                raise ValueError("Media authority changed during commit")
        except BaseException:
            for destination in reversed(touched):
                if previous[destination] is None:
                    destination.unlink(missing_ok=True)
                else:
                    _atomic_write(destination, previous[destination])
            raise
    return changed


def update_garment_highlights(
    assignments: dict[str, dict[str, Any]],
    *,
    evidence_path: Path,
    path: Path | None = None,
    theme_root: Path | None = None,
) -> list[str]:
    """Commit an independently reviewed technical geometry batch atomically.

    Only presentation.garment_highlight is changed. All sources and review
    bindings are validated before any write, preserving unrelated product facts.
    """
    from skyyrose.core.card_annotations import validate_annotation

    if not isinstance(assignments, dict) or not assignments:
        raise ValueError("Garment annotations require a nonempty SKU batch")
    target = _registry_target(path)
    with target.with_suffix(".json.lock").open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        raw = load_registry(target)
        validated = {}
        for sku, annotation in assignments.items():
            if sku not in raw["products"]:
                raise KeyError(f"SKU {sku!r} is not in the product registry")
            validated[sku] = validate_annotation(
                sku, annotation, evidence_path=evidence_path, theme_root=theme_root
            )
        changed = []
        for sku, annotation in validated.items():
            product = raw["products"][sku]
            presentation = product.get("presentation", {})
            if not isinstance(presentation, dict):
                raise ValueError(f"Invalid technical presentation section for {sku}")
            if presentation.get("garment_highlight") != annotation:
                product.setdefault("presentation", {})["garment_highlight"] = annotation
                changed.append(sku)
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


def record_founder_render_correction(
    sku: str,
    *,
    verbatim: str,
    implementation: str,
    captured: str,
    supersedes: str | None = None,
    path: Path | None = None,
) -> bool:
    """Record a founder's visual correction and its separate render directive.

    The founder's words are preserved exactly in both the dossier and the
    structured correction list. The derived implementation is explicitly
    marked agent-authored; it cannot be mistaken for a new founder product
    specification. Dossier/CSV projections are written under the registry
    lock before the authoritative registry commit and rolled back if that
    commit fails. Returns ``False`` when the complete correction is already
    present. An exact stale AGENT_ADDED derivation may be superseded only when
    its complete old text is supplied and the founder statement is already
    recorded exactly once in both the registry and dossier.
    """
    from datetime import date

    if not isinstance(verbatim, str) or not verbatim.strip() or "\n" in verbatim:
        raise ValueError("Founder correction must be one non-empty verbatim line")
    if verbatim != verbatim.strip():
        raise ValueError("Founder correction whitespace must be preserved explicitly")
    if not isinstance(implementation, str) or not implementation.strip():
        raise ValueError("Render implementation must be a non-empty string")
    if implementation != implementation.strip():
        raise ValueError("Render implementation must not have surrounding whitespace")
    if supersedes is not None and (
        not isinstance(supersedes, str)
        or not supersedes.strip()
        or supersedes != supersedes.strip()
    ):
        raise ValueError("supersedes must be an exact non-empty prior implementation")
    try:
        date.fromisoformat(captured)
    except (TypeError, ValueError) as error:
        raise ValueError("captured must be an ISO date") from error

    founder_record = {
        "text": verbatim,
        "authority": "FOUNDER_VERBATIM",
        "captured": captured,
    }
    implementation_record = {
        "text": implementation,
        "authority": "AGENT_ADDED",
        "captured": captured,
    }
    target = _registry_target(path)
    with target.with_suffix(".json.lock").open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        raw = load_registry(target)
        if sku not in raw["products"]:
            raise KeyError(f"SKU {sku!r} is not in the product registry")
        product = raw["products"][sku]
        dossier = product.get("dossier")
        if not isinstance(dossier, dict) or not isinstance(dossier.get("content"), str):
            raise ValueError(f"SKU {sku!r} has no editable registry dossier")
        content = dossier["content"]
        branding_anchor = "\n## Branding"
        if content.count(branding_anchor) != 1:
            raise ValueError(f"SKU {sku!r} dossier must contain one ## Branding anchor")
        section = "## Founder-confirmed correction"
        if content.count(section) != 1:
            raise ValueError(f"SKU {sku!r} dossier must contain one founder correction section")

        corrections = product.get("corrections")
        if corrections is None:
            corrections = []
        if not isinstance(corrections, list):
            raise ValueError(f"SKU {sku!r} corrections must be a list")
        founder_matches = [record for record in corrections if record == founder_record]
        implementation_matches = [
            record for record in corrections if record == implementation_record
        ]
        founder_in_text = verbatim in content
        implementation_in_text = implementation in content
        complete = (
            len(founder_matches) == 1
            and len(implementation_matches) == 1
            and founder_in_text
            and implementation_in_text
        )
        if complete:
            return False

        if supersedes is not None:
            stale_records = [
                (index, record)
                for index, record in enumerate(corrections)
                if isinstance(record, dict)
                and record.get("authority") == "AGENT_ADDED"
                and record.get("text") == supersedes
            ]
            if (
                len(founder_matches) != 1
                or not founder_in_text
                or content.count(f"**FOUNDER_CONFIRMED:** {verbatim} ") != 1
                or implementation_matches
                or implementation_in_text
                or len(stale_records) != 1
                or content.count(supersedes) != 1
            ):
                raise ValueError(
                    "Stale render correction does not exactly match the recorded founder and agent evidence"
                )
            stale_index, _ = stale_records[0]
            old_line = (
                "**Render implementation (agent-derived from the founder's visual correction):** "
                f"{supersedes}"
            )
            new_line = (
                "**Render implementation (agent-derived from the founder's visual correction):** "
                f"{implementation}"
            )
            if content.count(old_line) != 1:
                raise ValueError("Stale render implementation is not in its expected dossier field")

            dossier["content"] = content.replace(old_line, new_line, 1)
            updated_corrections = list(corrections)
            updated_corrections[stale_index] = implementation_record
            updated_product = _with_section_before(
                product,
                "authority",
                "corrections",
                updated_corrections,
            )
            updated_product["dossier"] = dossier
            raw["products"][sku] = updated_product

            outputs = _compatibility_outputs(raw, target)
            previous = {
                destination: destination.read_text() if destination.exists() else None
                for destination in outputs
            }
            touched: list[Path] = []
            try:
                for destination, output in outputs.items():
                    if previous[destination] != output:
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        _atomic_write(destination, output)
                        touched.append(destination)
                _atomic_write(target, json.dumps(raw, ensure_ascii=False, indent=2) + "\n")
            except BaseException:
                for destination in reversed(touched):
                    if previous[destination] is None:
                        destination.unlink(missing_ok=True)
                    else:
                        _atomic_write(destination, previous[destination])
                raise
            return True
        partial = bool(
            founder_matches or implementation_matches or founder_in_text or implementation_in_text
        )
        if partial:
            raise ValueError("Founder correction is only partially recorded; refusing to overwrite")

        note = (
            f"\n\n**FOUNDER_CONFIRMED:** {verbatim} "
            f'(Corey, {captured} America/Los_Angeles, verbatim: "{verbatim}")\n\n'
            "**Render implementation (agent-derived from the founder's visual correction):** "
            f"{implementation}\n"
        )
        dossier["content"] = content.replace(branding_anchor, note + branding_anchor, 1)
        raw["products"][sku] = _with_section_before(
            product,
            "authority",
            "corrections",
            [*corrections, founder_record, implementation_record],
        )

        outputs = _compatibility_outputs(raw, target)
        previous = {
            destination: destination.read_text() if destination.exists() else None
            for destination in outputs
        }
        touched: list[Path] = []
        try:
            for destination, output in outputs.items():
                if previous[destination] != output:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    _atomic_write(destination, output)
                    touched.append(destination)
            _atomic_write(target, json.dumps(raw, ensure_ascii=False, indent=2) + "\n")
        except BaseException:
            for destination in reversed(touched):
                if previous[destination] is None:
                    destination.unlink(missing_ok=True)
                else:
                    _atomic_write(destination, previous[destination])
            raise
    return True


def record_founder_garment_spec_correction(
    sku: str,
    *,
    verbatim: str,
    implementation: str,
    captured: str,
    old_feature_fragment: str,
    new_feature_fragment: str,
    new_specification: str,
    dossier_replacements: dict[str, str],
    source_evidence: list[dict[str, str]],
    supersedes: str | None = None,
    path: Path | None = None,
) -> bool:
    """Record a founder correction and atomically update its derived garment prose.

    The dossier remains the authored source for ``garment.features``. Exact
    founder wording is recorded before the Branding section, while the changed
    machine-derived feature field stays labelled ``derived_from_dossier``.
    Source references must match this SKU's current registry bindings and their
    bytes must match the supplied hashes. Compatibility projections are
    written under the registry lock and rolled back if the registry commit
    fails. Returns ``False`` for a complete idempotent repeat; partial state is
    rejected instead of silently repaired.
    """
    from datetime import date

    if not isinstance(verbatim, str) or not verbatim.strip() or "\n" in verbatim:
        raise ValueError("Founder correction must be one non-empty verbatim line")
    if verbatim != verbatim.strip():
        raise ValueError("Founder correction whitespace must be preserved explicitly")
    if not isinstance(implementation, str) or not implementation.strip():
        raise ValueError("Derived garment implementation must be non-empty")
    if implementation != implementation.strip():
        raise ValueError("Derived garment implementation must not have surrounding whitespace")
    if not isinstance(new_specification, str) or not new_specification.strip():
        raise ValueError("New garment specification must be non-empty")
    if (
        not isinstance(old_feature_fragment, str)
        or not old_feature_fragment
        or not isinstance(new_feature_fragment, str)
        or not new_feature_fragment
        or old_feature_fragment == new_feature_fragment
    ):
        raise ValueError("Feature correction requires distinct exact non-empty fragments")
    if not isinstance(dossier_replacements, dict) or not dossier_replacements:
        raise ValueError("At least one exact dossier replacement is required")
    if any(
        not isinstance(old, str) or not old or not isinstance(new, str) or not new or old == new
        for old, new in dossier_replacements.items()
    ):
        raise ValueError("Dossier replacements must map distinct non-empty exact text")
    if not isinstance(source_evidence, list) or not source_evidence:
        raise ValueError("Hash-bound source evidence is required")
    if supersedes is not None and (
        not isinstance(supersedes, str)
        or not supersedes.strip()
        or supersedes != supersedes.strip()
    ):
        raise ValueError("supersedes must be the exact prior agent-derived implementation")
    try:
        date.fromisoformat(captured)
    except (TypeError, ValueError) as error:
        raise ValueError("captured must be an ISO date") from error

    founder_record = {
        "text": verbatim,
        "authority": "FOUNDER_VERBATIM",
        "captured": captured,
    }
    implementation_record = {
        "text": implementation,
        "authority": "AGENT_ADDED",
        "captured": captured,
    }
    target = _registry_target(path)
    evidence_root = (
        target.parents[3]
        if target.parent.name == "data" and target.parent.parent.name == "skyyrose-flagship"
        else target.parent
    )
    with target.with_suffix(".json.lock").open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        raw = load_registry(target)
        if sku not in raw["products"]:
            raise KeyError(f"SKU {sku!r} is not in the product registry")
        product = raw["products"][sku]
        feature = product.get("garment", {}).get("features")
        if (
            not isinstance(feature, dict)
            or feature.get("source") != "derived_from_dossier"
            or not isinstance(feature.get("specification"), str)
        ):
            raise ValueError(f"SKU {sku!r} garment features are not a dossier-derived field")
        old_specification = feature["specification"]
        already_updated = old_specification == new_specification
        if not already_updated and (
            old_specification.count(old_feature_fragment) != 1
            or new_specification
            != old_specification.replace(old_feature_fragment, new_feature_fragment, 1)
        ):
            raise ValueError(
                "New specification must apply one exact replacement present in the current feature field"
            )
        dossier = product.get("dossier")
        if not isinstance(dossier, dict) or not isinstance(dossier.get("content"), str):
            raise ValueError(f"SKU {sku!r} has no editable registry dossier")
        content = dossier["content"]
        branding_anchor = "\n## Branding"
        if content.count(branding_anchor) != 1:
            raise ValueError(f"SKU {sku!r} dossier must contain one ## Branding anchor")
        if content.count("## Founder-confirmed correction") != 1:
            raise ValueError(f"SKU {sku!r} dossier must contain one founder correction section")
        if content.count(old_specification) != 1:
            raise ValueError("Current derived feature specification is not unique in its dossier")
        render_sources = product.get("render_sources", {})
        expected_source_paths = {
            render_sources.get(key)
            for key in ("techflat_front", "techflat_back", "techflat_sheet", "reference")
            if render_sources.get(key)
        }
        if (
            not {render_sources.get("techflat_front"), render_sources.get("reference")}
            <= expected_source_paths
        ):
            raise ValueError("SKU must bind a techflat front and a real-product reference")
        seen_paths: set[str] = set()
        for binding in source_evidence:
            if not isinstance(binding, dict) or set(binding) != {"path", "sha256"}:
                raise ValueError("Each source binding requires exact path and sha256 fields")
            if not isinstance(binding["path"], str) or not isinstance(binding["sha256"], str):
                raise ValueError("Source evidence path and hash must be strings")
            _bound_review_file(evidence_root, binding)
            seen_paths.add(binding["path"])
            if binding["path"] not in implementation or binding["sha256"] not in implementation:
                raise ValueError("Derived implementation must cite each source path and hash")
        if seen_paths != expected_source_paths or len(source_evidence) != len(seen_paths):
            raise ValueError(
                "Source evidence must bind the current techflat and real-product photo"
            )

        corrections = product.get("corrections") or []
        if not isinstance(corrections, list):
            raise ValueError(f"SKU {sku!r} corrections must be a list")
        founder_matches = [record for record in corrections if record == founder_record]
        implementation_matches = [
            record for record in corrections if record == implementation_record
        ]
        founder_in_text = f"**FOUNDER_CONFIRMED:** {verbatim} " in content
        implementation_in_text = implementation in content
        replacements_applied = all(
            old not in content and content.count(new) == 1
            for old, new in dossier_replacements.items()
        )
        complete = (
            already_updated
            and len(founder_matches) == 1
            and len(implementation_matches) == 1
            and founder_in_text
            and implementation_in_text
            and replacements_applied
        )
        if complete:
            return False
        if supersedes is not None:
            stale_records = [
                (index, record)
                for index, record in enumerate(corrections)
                if isinstance(record, dict)
                and record.get("authority") == "AGENT_ADDED"
                and record.get("text") == supersedes
            ]
            if (
                len(founder_matches) != 1
                or not founder_in_text
                or content.count(f"**FOUNDER_CONFIRMED:** {verbatim} ") != 1
                or implementation_matches
                or implementation_in_text
                or len(stale_records) != 1
                or content.count(supersedes) != 1
            ):
                raise ValueError(
                    "Stale garment implementation does not exactly match the recorded founder and agent evidence"
                )
            stale_index, _ = stale_records[0]
            old_implementation_line = (
                "**Garment implementation (agent-derived from founder-directed product sources):** "
                f"{supersedes}"
            )
            new_implementation_line = (
                "**Garment implementation (agent-derived from founder-directed product sources):** "
                f"{implementation}"
            )
            if content.count(old_implementation_line) != 1:
                raise ValueError(
                    "Stale garment implementation is not in its expected dossier field"
                )
            if content.count(old_specification) != 1:
                raise ValueError(
                    "Current derived feature specification is not unique in its dossier"
                )
            updated_content = content.replace(old_specification, new_specification, 1)
            for old, new in dossier_replacements.items():
                if updated_content.count(old) != 1:
                    raise ValueError("Dossier replacement source must appear exactly once")
                updated_content = updated_content.replace(old, new, 1)
            dossier["content"] = updated_content.replace(
                old_implementation_line, new_implementation_line, 1
            )
            product.setdefault("garment", {}).setdefault("features", {})[
                "specification"
            ] = new_specification
            updated_corrections = list(corrections)
            updated_corrections[stale_index] = implementation_record
            updated_product = _with_section_before(
                product,
                "authority",
                "corrections",
                updated_corrections,
            )
            updated_product["dossier"] = dossier
            raw["products"][sku] = updated_product

            outputs = _compatibility_outputs(raw, target)
            previous = {
                destination: destination.read_text() if destination.exists() else None
                for destination in outputs
            }
            touched: list[Path] = []
            try:
                for destination, output in outputs.items():
                    if previous[destination] != output:
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        _atomic_write(destination, output)
                        touched.append(destination)
                _atomic_write(target, json.dumps(raw, ensure_ascii=False, indent=2) + "\n")
            except BaseException:
                for destination in reversed(touched):
                    if previous[destination] is None:
                        destination.unlink(missing_ok=True)
                    else:
                        _atomic_write(destination, previous[destination])
                raise
            return True
        partial = bool(
            founder_matches
            or implementation_matches
            or founder_in_text
            or implementation_in_text
            or already_updated
            or any(new in content for new in dossier_replacements.values())
        )
        if partial:
            raise ValueError("Founder garment correction is only partially recorded")
        if content.count(new_specification) != 0:
            raise ValueError("New feature specification already appears in the dossier")

        updated_content = content.replace(old_specification, new_specification, 1)
        for old, new in dossier_replacements.items():
            if updated_content.count(old) != 1:
                raise ValueError("Dossier replacement source must appear exactly once")
            updated_content = updated_content.replace(old, new, 1)
        note = (
            f"\n\n**FOUNDER_CONFIRMED:** {verbatim} "
            f'(Corey, {captured} America/Los_Angeles, verbatim: "{verbatim}")\n\n'
            "**Garment implementation (agent-derived from founder-directed product sources):** "
            f"{implementation}\n"
        )
        dossier["content"] = updated_content.replace(branding_anchor, note + branding_anchor, 1)
        product.setdefault("garment", {}).setdefault("features", {})[
            "specification"
        ] = new_specification
        product["corrections"] = [*corrections, founder_record, implementation_record]

        outputs = _compatibility_outputs(raw, target)
        previous = {
            destination: destination.read_text() if destination.exists() else None
            for destination in outputs
        }
        touched: list[Path] = []
        try:
            for destination, output in outputs.items():
                if previous[destination] != output:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    _atomic_write(destination, output)
                    touched.append(destination)
            _atomic_write(target, json.dumps(raw, ensure_ascii=False, indent=2) + "\n")
        except BaseException:
            for destination in reversed(touched):
                if previous[destination] is None:
                    destination.unlink(missing_ok=True)
                else:
                    _atomic_write(destination, previous[destination])
            raise
    return True


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
        card_manifest = raw.get("storefront_card_manifest")
        if card_manifest is not None:
            if not isinstance(card_manifest, dict):
                raise ValueError("Storefront card metadata must be an object")
            card_fronts = {}
            for sku, product in raw["products"].items():
                front = product.get("images", {}).get("card_front")
                if not isinstance(front, dict):
                    raise ValueError(f"Missing registry-owned card front for {sku}")
                card_fronts[sku] = front
            projection = {
                "schema_version": card_manifest["schema_version"],
                "authorization": card_manifest["authorization"],
                "products": card_fronts,
            }
            if "card_treatment_approval" in card_manifest:
                projection["card_treatment_approval"] = card_manifest["card_treatment_approval"]
            outputs[V2_CARD_FRONT_PROJECTION] = (
                json.dumps(projection, ensure_ascii=False, indent=2) + "\n"
            )
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
