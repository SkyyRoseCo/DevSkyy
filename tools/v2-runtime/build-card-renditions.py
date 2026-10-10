"""Generate responsive delivery copies without changing approved source authority."""

import argparse
import fcntl
import hashlib
import io
import json
import os
import sys
import tempfile
from pathlib import Path

from PIL import Image, features

ROOT = Path(__file__).resolve().parents[2]
THEME = ROOT / "wordpress-theme/skyyrose-flagship-2"
MANIFEST = THEME / "data/v2-media-eligibility.json"
OUTPUT = THEME / "assets/derived/card-fronts"
WIDTHS = (160, 320, 480, 768, 1024, 1280, 1536)


def rendition_widths(native_width: int) -> tuple[int, ...]:
    """Thumbnail through retina delivery, including the compressed native width."""
    return tuple(sorted({width for width in WIDTHS if width <= native_width} | {native_width}))


# Reuse release admission: there is only one visual approval inventory.
sys.path.insert(0, str(ROOT / "tools/v2-source-certification"))
import package as admission  # noqa: E402

from skyyrose.core.product import get_product  # noqa: E402


def approved_sources(inventory: dict) -> dict:
    """Select unique canonical SKU masters with real, byte-bound role reviews."""
    if inventory.get("schema") != "skyyrose.v2.media-eligibility.v1":
        raise ValueError("Invalid V2 media eligibility schema")
    admission.THEME = THEME
    products = {}
    for relative, record in inventory.get("assets", {}).items():
        if not isinstance(record, dict) or record.get("kind") != "photograph":
            continue
        if relative.startswith("assets/derived/") or "card_front" not in record.get("roles", []):
            continue
        if record.get("status") not in {"INDEPENDENT_VISUAL_PASS", "FOUNDER_ACCEPTED"}:
            continue
        if not admission.eligible_media(relative, inventory):
            raise ValueError(f"Approved source drift or invalid review: {relative}")
        skus = record.get("skus")
        if not isinstance(skus, list) or len(skus) != 1:
            raise ValueError("Card master must bind exactly one SKU")
        sku = skus[0]
        if sku in products:
            raise ValueError(f"Competing approved masters: {sku}")
        if not sku or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in sku):
            raise ValueError("Invalid SKU")
        product = get_product(sku)
        if record.get("collections") != [product["collection"]]:
            raise ValueError(f"Canonical collection mismatch: {sku}")
        front = product["images"]["card_front"]
        if (
            relative != f"assets/v2-original/products/{sku}.png"
            or not front
            or front.get("path") != relative
            or front.get("sha256") != record["sha256"]
            or front.get("source_sha256") != record["sha256"]
            or front.get("review") != record["review"]
            or front.get("current_fidelity_status") != record["status"]
        ):
            raise ValueError(f"Delivery source differs from current canonical card: {sku}")
        products[sku] = {**record, "src": relative}
    return products


def derivative_records(manifest: dict, encoded: bytes) -> dict:
    """Project delivery bindings without granting or inventing visual approval."""
    digest = hashlib.sha256(encoded).hexdigest()
    records = {}
    for product in manifest["products"].values():
        for rendition in product["renditions"]:
            records[rendition["src"]] = {
                "kind": "photograph",
                "status": "DELIVERY_DERIVATIVE",
                "origin": "V2_ORIGINAL_20261002",
                "sha256": rendition["sha256"],
                "source_path": product["source"],
                "source_sha256": product["source_sha256"],
                "roles": product["roles"],
                "skus": product["skus"],
                "collections": product["collections"],
                "width": rendition["width"],
                "height": rendition["height"],
                "delivery_manifest": {
                    "path": "assets/derived/card-fronts/manifest.json",
                    "sha256": digest,
                },
            }
    return records


def validate_public_directory(directory: Path) -> None:
    """Detect inaccessible existing generated directories without repairing them."""
    root = THEME / "assets/derived"
    directory.relative_to(root)
    current = directory
    while True:
        if current.exists() and (not current.is_dir() or current.stat().st_mode & 0o005 != 0o005):
            raise ValueError(f"Inaccessible public generated directory: {current}")
        if current == root:
            break
        current = current.parent


def create_public_directory(directory: Path) -> None:
    """Make only newly-created generated directories readable and searchable."""
    missing = []
    current = directory
    while not current.exists():
        missing.append(current)
        current = current.parent
    directory.mkdir(parents=True, exist_ok=True)
    for created in missing:
        if created.is_symlink():
            raise ValueError(f"Symlink generated directory: {created}")
        created.chmod(0o755)
    validate_public_directory(directory)


def write_output(destination: Path, payload: bytes) -> None:
    """Replace a generated entry without following a destination symlink."""
    create_public_directory(destination.parent)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fchmod(stream.fileno(), 0o644)
        os.replace(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def generate(check: bool = False) -> dict:
    """Verify source hashes and generate uncropped, proportionate delivery copies."""
    for directory in (OUTPUT, *OUTPUT.parents):
        if directory.is_symlink():
            raise ValueError(f"Symlink output directory: {directory}")
        if directory == THEME:
            break
    OUTPUT.resolve().relative_to(THEME.resolve())
    source = json.loads(MANIFEST.read_text())
    result = {"schema": "skyyrose.card-renditions.v1", "products": {}}
    for sku, record in sorted(approved_sources(source).items()):
        path = (THEME / record["src"]).resolve()
        path.relative_to((THEME / "assets").resolve())
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != record["sha256"]:
            raise ValueError(f"Approved source drift: {sku}")
        if not sku or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in sku):
            raise ValueError("Invalid SKU")
        with Image.open(io.BytesIO(raw)) as original:
            images = []
            for width in rendition_widths(original.width):
                height = round(original.height * width / original.width)
                resized = original.resize((width, height), Image.Resampling.LANCZOS)
                stream = io.BytesIO()
                resized.save(stream, format="WEBP", quality=90, method=6)
                payload = stream.getvalue()
                destination = OUTPUT / f"{sku}-{width}w.webp"
                if destination.is_symlink():
                    raise ValueError(f"Symlink rendition: {destination.name}")
                if check:
                    validate_public_directory(destination.parent)
                    if (
                        not destination.is_file()
                        or destination.read_bytes() != payload
                        or destination.stat().st_mode & 0o777 != 0o644
                    ):
                        raise ValueError(f"Stale rendition: {destination.name}")
                else:
                    write_output(destination, payload)
                images.append(
                    {
                        "src": destination.relative_to(THEME).as_posix(),
                        "width": width,
                        "height": height,
                        "sha256": hashlib.sha256(payload).hexdigest(),
                    }
                )
            result["products"][sku] = {
                "source": record["src"],
                "source_sha256": record["sha256"],
                "renditions": images,
                "roles": record["roles"],
                "skus": record["skus"],
                "collections": record["collections"],
                "source_review": record["review"],
                "encoding": {
                    "format": "WEBP",
                    "quality": 90,
                    "method": 6,
                    "resize": "LANCZOS",
                    "crop": False,
                    "upscale": False,
                    "pillow_version": Image.__version__,
                    "libwebp_version": features.version("webp"),
                    "builder_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                },
            }
    manifest = OUTPUT / "manifest.json"
    if manifest.is_symlink():
        raise ValueError("Symlink rendition manifest")
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if check:
        validate_public_directory(manifest.parent)
        if (
            not manifest.is_file()
            or manifest.read_text() != encoded
            or manifest.stat().st_mode & 0o777 != 0o644
        ):
            raise ValueError("Stale rendition manifest")
    else:
        write_output(manifest, encoded.encode())
    print(
        f"{'Verified' if check else 'Built'} responsive copies of {len(result['products'])} approved card fronts; originals unchanged"
    )
    # Caller coordinates these consumer entries with the inventory owner. Do not
    # rewrite a concurrently changing approval inventory from a delivery build.
    return derivative_records(result, encoded.encode())


def sync_delivery_inventory(records: dict, expected: bytes) -> None:
    """Coordinate derivative entries only; this grants no master approval."""
    target = THEME / "data/v2-media-eligibility.json"
    with target.with_suffix(".json.lock").open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        if target.is_symlink() or target.read_bytes() != expected:
            raise ValueError("Eligibility inventory changed during responsive delivery build")
        manifest_bytes = (OUTPUT / "manifest.json").read_bytes()
        current_manifest = json.loads(manifest_bytes)
        if records != derivative_records(current_manifest, manifest_bytes) or any(
            not path.startswith("assets/derived/card-fronts/") for path in records
        ):
            raise ValueError(
                "Inventory synchronization requires the exact complete derivative manifest"
            )
        inventory = json.loads(expected)
        assets = inventory["assets"]
        for name in list(assets):
            if name.startswith("assets/derived/card-fronts/"):
                del assets[name]
        assets.update(records)
        encoded = (json.dumps(inventory, indent=2, sort_keys=True) + "\n").encode()
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())
            temporary.chmod(0o644)
            os.replace(temporary, target)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--sync-inventory",
        action="store_true",
        help="Synchronize current delivery records without changing master approvals",
    )
    args = parser.parse_args()
    if args.check and args.sync_inventory:
        parser.error("--check cannot modify the inventory")
    if not args.sync_inventory:
        generate(args.check)
        return
    authority = (ROOT / "logo-registry.json").resolve()
    with authority.with_suffix(".json.lock").open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_SH)
        before = (THEME / "data/v2-media-eligibility.json").read_bytes()
        records = generate(False)
        sync_delivery_inventory(records, before)


if __name__ == "__main__":
    main()
