#!/usr/bin/env python3
"""Generate the V2 presentation registry from the canonical product SOT.

This is a build-time adapter. WooCommerce remains responsible for product IDs,
prices, stock, variations, and visibility; SOT media remains responsible for
approved product visuals. Merchandising-series membership, region, and order
come only from the canonical product SOT.
"""

from __future__ import annotations

import fcntl
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools/v2-source-certification"))

from inputs import garment_types, load_product_sot  # noqa: E402

from skyyrose.core.card_annotations import validate_annotation  # noqa: E402
from skyyrose.core.media_usage import validated_usage_roles  # noqa: E402
from skyyrose.core.product import all_skus, get_product  # noqa: E402

OUTPUT = Path(__file__).resolve().parents[1] / "data/product-presentation-registry.json"
ALLOWED_COLLECTIONS = {"black-rose", "kids-capsule", "love-hurts", "signature"}
ALLOWED_SERIES = {"jersey-series"}

# Provisional layout-review selection; all identity, role and image facts come
# from get_product. This tuple is not product or founder-approval authority.
EDITORIAL_REVIEW_SKUS = ("sg-009", "br-001", "lh-004")


def editorial_front(sku: str, product: dict | None = None) -> dict[str, object]:
    """Project the exact current front without a stale card-scene fallback."""
    product = product or get_product(sku)
    front = product["images"]["card_front"]
    if not front:
        raise ValueError(f"Missing canonical editorial front for {sku}")
    reference = Path("wordpress-theme/skyyrose-flagship-2") / front["path"]
    source = (ROOT / reference).resolve()
    if not source.is_relative_to(ROOT) or not source.is_file():
        raise ValueError(f"Invalid canonical editorial front for {sku}")
    pixels = source.read_bytes()
    with Image.open(io.BytesIO(pixels)) as image:
        width, height = image.size
    digest = hashlib.sha256(pixels).hexdigest()
    if (
        digest != front.get("sha256")
        or digest != front.get("source_sha256")
        or (width, height) != (front.get("width"), front.get("height"))
    ):
        raise ValueError(f"Current editorial master differs from its approved binding: {sku}")
    return {
        "src": front["path"],
        "width": width,
        "height": height,
        "sha256": digest,
        "source_path": source.relative_to(ROOT).as_posix(),
        "source_sha256": digest,
        "role": "card_front",
        "alt": f"{product['name']} — front on model",
        "evidence": front["current_fidelity_status"],
    }


@contextmanager
def registry_read_lock():
    path = ROOT / "wordpress-theme/skyyrose-flagship/data/logo-registry.json"
    with path.with_suffix(".json.lock").open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_SH)
        yield path


def build_registry() -> dict[str, object]:
    with registry_read_lock() as registry_path:
        before = registry_path.read_bytes()
        artifact = build_locked_registry(before)
        if registry_path.read_bytes() != before:
            raise ValueError("Product registry changed during presentation build")
        return artifact


def build_locked_registry(registry_bytes: bytes) -> dict[str, object]:
    # Presentation consumes current founder records. Historical media snapshots
    # remain release evidence, never a competing source of commerce or colors.
    current_products = {sku: get_product(sku) for sku in all_skus()}
    registry_digest = hashlib.sha256(registry_bytes).hexdigest()
    # The approved card-media contract (inc/presentation-registry.php) is bound
    # to the pinned media receipt, so product_sot_* keep that identity. The
    # receipt never supplies commerce or garment facts; garment_types() fails
    # closed when current registry facts drift from it without a recorded
    # founder correction.
    receipt, receipt_text = load_product_sot()
    garment_types(receipt)
    authority = json.loads(registry_bytes)
    for sku, current in current_products.items():
        if (
            current["provenance"]["sources"]["registry"]["sha256"] != registry_digest[:16]
            or current["catalog"] != authority["products"][sku]["catalog"]
        ):
            raise ValueError(f"Incoherent current product snapshot: {sku}")
    accepted_glbs: list[dict[str, object]] = []
    products: dict[str, dict[str, object]] = {}
    series_members: dict[str, list[tuple[int, str]]] = {
        series_slug: [] for series_slug in ALLOWED_SERIES
    }
    series_orders: dict[str, set[int]] = {series_slug: set() for series_slug in ALLOWED_SERIES}
    for sku, current_record in current_products.items():
        current = current_record["catalog"]
        # Current registry bytes identify this projection, not an asset approval.
        # Real assets stay held until an approval contract binds the approved
        # founder facts without a circular whole-registry self-hash. Never stamp
        # an old binding with a new digest and imply that it was reapproved.
        binding = current_record["asset_library"].get("accepted_glb_runtime")
        if binding is not None:
            raise ValueError(
                f"Accepted GLB binding for {sku} requires a reviewed product-source approval contract"
            )
        collection = current["collection"]
        if not sku or sku in products:
            raise ValueError(f"Product SOT contains an empty or duplicate SKU: {sku!r}")
        if collection not in ALLOWED_COLLECTIONS:
            raise ValueError(f"Unknown collection for {sku}: {collection!r}")
        merchandising = current_record["merchandising"]
        if not isinstance(merchandising, dict):
            raise ValueError(f"Canonical registry merchandising record is invalid for {sku}")
        series_slug = str(merchandising.get("series_slug", ""))
        series_region = str(merchandising.get("series_region", ""))
        series_order = merchandising.get("series_order", 0)
        if not isinstance(series_order, int) or isinstance(series_order, bool):
            raise ValueError(f"Series order is invalid for {sku}: {series_order!r}")
        if series_slug and series_slug not in ALLOWED_SERIES:
            raise ValueError(f"Unknown merchandising series for {sku}: {series_slug!r}")
        if series_slug:
            if not series_region or series_order <= 0:
                raise ValueError(f"Series metadata is incomplete for {sku}")
            if series_order in series_orders[series_slug]:
                raise ValueError(f"Duplicate {series_slug} series order: {series_order}")
            series_orders[series_slug].add(series_order)
            series_members[series_slug].append((series_order, sku))
        elif series_region or series_order:
            raise ValueError(f"Non-series product has series metadata: {sku}")

        presentation = series_slug or collection
        record: dict[str, object] = {
            "collection": collection,
            "garment_type": current["garment_type_lock"].strip().lower(),
            "presentation": presentation,
            "route": (
                "/pre-order/"
                if current["is_preorder"].strip() == "1"
                else f"/collections/{collection}/"
            ),
            "is_preorder": current["is_preorder"].strip() == "1",
            "product_sot_hash": receipt["products"][sku]["product_hash"],
            "media_proof_level": receipt["products"][sku]["verification"]["proof_level"],
        }
        annotation = current_record.get("presentation", {}).get("garment_highlight")
        if annotation is not None:
            front = current_record["images"]["card_front"]
            source = annotation.get("source", {})
            if (
                front
                and source.get("path") == front.get("path")
                and source.get("sha256") == front.get("sha256")
            ):
                record["garment_highlight"] = validate_annotation(sku, annotation)
            else:
                # Preserve the old source-bound annotation in authority/history,
                # but never place its geometry over different product pixels.
                record["garment_highlight_state"] = "SOURCE_CHANGED_REVIEW_REQUIRED"
        if series_slug:
            record["series_region"] = series_region
            record["series_order"] = series_order
        products[sku] = record

    supplements = {
        f"{series_slug.replace('-', '_')}_skus": [sku for _order, sku in sorted(members)]
        for series_slug, members in sorted(series_members.items())
    }
    canonical_collections = authority["collections"]
    collections = {
        slug: {"story": {"seed": value.get("story", {}).get("seed")}}
        for slug, value in sorted(canonical_collections.items())
    }
    for sku in EDITORIAL_REVIEW_SKUS:
        current = current_products[sku]
        products[sku]["editorial_front"] = editorial_front(sku, current)
        collections[current["collection"]]["editorial"] = {"lead_sku": sku}
    for slug, collection in canonical_collections.items():
        scene = collection.get("imagery", {}).get("editorial_scene")
        if scene:
            collections[slug].setdefault("editorial", {})["scene"] = scene
        for role in ("collection_hero", "collection_story", "merchandise_scene"):
            binding = collection.get("imagery", {}).get(role)
            if binding:
                collections[slug].setdefault("imagery", {})[role] = binding
    theme = OUTPUT.parent.parent
    inventory = json.loads((theme / "data/v2-media-eligibility.json").read_text())
    adoptions = authority.get("media_usage_adoptions", {})
    for relative in adoptions:
        record = inventory.get("assets", {}).get(relative, {})
        if not validated_usage_roles(relative, record, adoptions, theme):
            raise ValueError("Invalid current canonical media usage grant: " + relative)
    return {
        "glb_runtime": {
            "schema": "skyyrose.accepted-glb-runtime.v1",
            "registry_sha256": registry_digest,
            "publication_authorized": bool(accepted_glbs)
            and all(entry.get("publication_authorized") is True for entry in accepted_glbs),
            "entries": accepted_glbs,
        },
        "schema_version": "2.0.0",
        "kind": "skyyrose-v2-product-presentation-registry",
        "generated_from": "wordpress-theme/skyyrose-flagship/data/logo-registry.json",
        "product_registry_sha256": registry_digest,
        "product_sot_scope": "historical_media_binding_only",
        "product_sot_sha256": hashlib.sha256(receipt_text.encode()).hexdigest(),
        "supplements": supplements,
        "collections": collections,
        "media_usage_adoptions": adoptions,
        "products": dict(sorted(products.items())),
    }


def main_locked() -> int:
    artifact = build_registry()
    rendered = json.dumps(artifact, indent=2, sort_keys=True) + "\n"
    inventory_path = OUTPUT.parent / "v2-media-eligibility.json"
    inventory = json.loads(inventory_path.read_text())
    usages_current = inventory.get("usage_adoptions", {}) == artifact["media_usage_adoptions"]
    if "--check" in sys.argv:
        if (
            not OUTPUT.is_file()
            or OUTPUT.read_text(encoding="utf-8") != rendered
            or not usages_current
        ):
            print(
                "Product presentation registry is stale. Run this script without --check.",
                file=sys.stderr,
            )
            return 1
        for sku in EDITORIAL_REVIEW_SKUS:
            front = artifact["products"][sku]["editorial_front"]
            target = OUTPUT.parent.parent / front["src"]
            if (
                not target.is_file()
                or hashlib.sha256(target.read_bytes()).hexdigest() != front["sha256"]
            ):
                print(f"Packaged editorial front is stale for {sku}", file=sys.stderr)
                return 1
        print(f"Product presentation registry is current ({len(artifact['products'])} SKUs).")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    previous_output = OUTPUT.read_bytes() if OUTPUT.exists() else None
    previous_inventory = inventory_path.read_bytes()
    if not usages_current:
        inventory["usage_adoptions"] = artifact["media_usage_adoptions"]
    encoded_inventory = (json.dumps(inventory, indent=2, sort_keys=True) + "\n").encode()
    for sku in EDITORIAL_REVIEW_SKUS:
        front = artifact["products"][sku]["editorial_front"]
        target = OUTPUT.parent.parent / front["src"]
        target.parent.mkdir(parents=True, exist_ok=True)
        if (ROOT / front["source_path"]).resolve() != target.resolve():
            shutil.copyfile(ROOT / front["source_path"], target)
    try:
        replace_bytes(OUTPUT, rendered.encode())
        if not usages_current:
            replace_bytes(inventory_path, encoded_inventory)
    except BaseException:
        if previous_output is None:
            OUTPUT.unlink(missing_ok=True)
        else:
            replace_bytes(OUTPUT, previous_output)
        if inventory_path.read_bytes() != previous_inventory:
            replace_bytes(inventory_path, previous_inventory)
        raise
    print(f"Wrote {OUTPUT} ({len(artifact['products'])} SKUs).")
    return 0


def replace_bytes(path: Path, data: bytes) -> None:
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o644)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main() -> int:
    # Same lock order as rendition builders: canonical registry, then inventory.
    # Re-read and publish the latest inventory under its exclusive writer lock.
    with registry_read_lock():
        inventory = OUTPUT.parent / "v2-media-eligibility.json"
        with inventory.with_suffix(".json.lock").open("a") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            return main_locked()


if __name__ == "__main__":
    raise SystemExit(main())
