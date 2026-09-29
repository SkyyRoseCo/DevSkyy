#!/usr/bin/env python3
"""Build the collection/SKU library from registry bindings, never filename guesses.

Originals stay untouched. PNG exports use the founder-selected 2400 px canvas.
Run --check to validate source hashes, link targets, export dimensions and indexes.
The optional review inventory creates local links outside the verified library;
external-checkout links are ignored by Git and are not product inputs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

from PIL import Image, ImageOps
from PIL.PngImagePlugin import PngInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from skyyrose.core.product import all_skus, get_product  # noqa: E402
from skyyrose.core.product_registry import load_registry  # noqa: E402


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inside(root: Path, relative: str) -> Path:
    path = root / relative
    if Path(relative).is_absolute() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Path escapes repository: {relative}")
    return path


def write_text(path: Path, text: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != text:
            raise ValueError(f"Stale generated file: {path}")
    elif not path.is_file() or path.read_text() != text:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def link_source(source: Path, link: Path, check: bool) -> None:
    if source == link:
        return
    if link.is_symlink() and link.is_file() and digest(link) == digest(source):
        return
    if check or link.exists() or link.is_symlink():
        raise ValueError(f"Missing or conflicting generated link: {link}")
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(os.path.relpath(source, link.parent))


def export_image(source: Path, target: Path, policy: dict, check: bool) -> dict:
    with Image.open(source) as original:
        frame = ImageOps.exif_transpose(original)
        width, height = frame.size
        canvas_size = (policy["width"], policy["height"])
        limit = min(canvas_size) - 2 * policy["padding"]
        scale = min(limit / width, limit / height)
        fitted = (max(1, round(width * scale)), max(1, round(height * scale)))
        signature = hashlib.sha256(
            (digest(source) + json.dumps(policy, sort_keys=True)).encode()
        ).hexdigest()
        current = False
        if target.is_file():
            with Image.open(target) as existing:
                current = existing.info.get("catalog_export_signature") == signature
        if check:
            with Image.open(target) as output:
                if output.size != canvas_size or output.format != "PNG" or not current:
                    raise ValueError(f"Incorrect export dimensions/format: {target}")
        elif not current:
            canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
            resized = frame.convert("RGBA").resize(fitted, Image.Resampling.LANCZOS)
            canvas.paste(
                resized, ((canvas_size[0] - fitted[0]) // 2, (canvas_size[1] - fitted[1]) // 2)
            )
            target.parent.mkdir(parents=True, exist_ok=True)
            metadata = PngInfo()
            metadata.add_text("catalog_export_signature", signature)
            options = {"compress_level": 6, "pnginfo": metadata}
            if original.info.get("icc_profile"):
                options["icc_profile"] = original.info["icc_profile"]
            canvas.save(target, "PNG", **options)
    return {
        "width": width,
        "height": height,
        "scaled_width": fitted[0],
        "scaled_height": fitted[1],
        "upscaled": scale > 1,
        "export_sha256": digest(target),
    }


def product_sources(product: dict) -> list[dict]:
    sources = [dict(s) for s in product["asset_library"]["sources"]]
    for role, path in product["render_sources"].items():
        if path:
            sources.append(
                {
                    "path": path,
                    "kind": "techflat" if role.startswith("techflat") else "reference",
                    "view": role,
                    "verification": "EXISTING_REGISTRY_BINDING",
                }
            )
    for role, binding in product["images"].items():
        if binding:
            sources.append(
                {
                    "path": "wordpress-theme/skyyrose-flagship/" + binding["path"],
                    "kind": "storefront",
                    "view": role,
                    "verification": "EXISTING_REGISTRY_BINDING",
                }
            )
    return sources


def build_product(product: dict, policy: dict, check: bool) -> dict:
    sku = product["sku"]
    directory = inside(ROOT, product["asset_library"]["directory"])
    expected_directory = ROOT / "assets/products/catalog" / product["collection"] / sku
    if directory != expected_directory:
        raise ValueError(f"Incorrect product directory: {sku}")
    entries = []
    for binding in product_sources(product):
        source = inside(ROOT, binding["path"])
        sha = digest(source)
        if binding.get("sha256", sha) != sha:
            raise ValueError(f"Reviewed source changed: {sku}: {binding['path']}")
        # Every distinct image has one export per product; roles share the export.
        native = directory / "originals" / f"{sku}-{sha[:16]}{source.suffix.lower()}"
        if source.parent == directory / "originals":
            native = source
        link_source(source, native, check)
        output = directory / "standardized" / f"{sku}-{sha[:16]}-2400.png"
        info = export_image(source, output, policy, check)
        entries.append(
            {
                **binding,
                "sha256": sha,
                "original": native.relative_to(ROOT).as_posix(),
                "export": output.relative_to(ROOT).as_posix(),
                **info,
            }
        )
    expected_exports = {ROOT / entry["export"] for entry in entries}
    expected_originals = {ROOT / entry["original"] for entry in entries}
    for obsolete in (directory / "standardized").glob("*.png"):
        if obsolete not in expected_exports:
            with Image.open(obsolete) as image:
                generated = "catalog_export_signature" in image.info
            if not generated:
                raise ValueError(f"Unmanaged file in generated exports: {obsolete}")
            if check:
                raise ValueError(f"Stale generated export: {obsolete}")
            obsolete.unlink()
    for obsolete in (directory / "originals").iterdir():
        if obsolete.is_symlink() and obsolete not in expected_originals:
            if check:
                raise ValueError(f"Stale generated source link: {obsolete}")
            obsolete.unlink()
    unique = {entry["export"] for entry in entries}
    has_photos = any(
        s["kind"] in {"flatlay", "packshot"} for s in product["asset_library"]["sources"]
    )
    manifest = {
        "sku": sku,
        "collection": product["collection"],
        "authority": "logo-registry.json::products." + sku,
        "policy": policy,
        "source_photo_gap": not has_photos,
        "assets": entries,
    }
    write_text(
        directory / "index.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", check
    )
    readme = (
        f"# {sku}: {product['name']}\n\n"
        "Generated projection of `logo-registry.json`. Read product facts via "
        f"`python -m skyyrose.core.product {sku}`.\n\n"
        "- `originals/`: native-resolution source files or links; never overwrite.\n"
        "- `standardized/`: 2400 × 2400 lossless PNG exports. No recoloring or AI enhancement.\n"
        "- `index.json`: source/view/export mapping and quality limitations, generated from the registry.\n\n"
        + (
            "**Gap:** no individually reviewed source photo is bound yet.\n"
            if not has_photos
            else ""
        )
        + "\nExisting storefront bindings are not new founder approvals. Upscaling adds pixels, not recovered detail.\n"
    )
    write_text(directory / "README.md", readme, check)
    return {
        "sku": sku,
        "directory": directory.relative_to(ROOT).as_posix(),
        "unique_exports": len(unique),
        "reviewed_sources": len(product["asset_library"]["sources"]),
        "source_photo_gap": not has_photos,
    }


def build_review(inventory: Path, external_root: Path | None, reviewed_hashes: set[str]) -> dict:
    rows = json.loads(inventory.read_text())["files"]
    review = ROOT / "assets/products/outside-verified-products"
    review.mkdir(parents=True, exist_ok=True)
    counts = {}
    missing = []
    expected_links = set()
    for row in rows:
        # Existing bindings and reviewed source identities are already catalogued.
        if row.get("bindings") or row["sha256"] in reviewed_hashes:
            continue
        location = row["location"]
        base = ROOT if location == "worktree" else external_root
        category = row.get(
            "review_category",
            "unverified-candidates" if row.get("candidate_skus") else "unassigned",
        )
        counts[category] = counts.get(category, 0) + 1
        if base is None:
            missing.append({"location": location, "path": row["path"]})
            continue
        source = inside(base, row["path"])
        if not source.is_file() or digest(source) != row["sha256"]:
            missing.append({"location": location, "path": row["path"]})
            continue
        link = review / "files" / category / location / row["path"]
        expected_links.add(link)
        link_source(source, link, False)
    for obsolete in (review / "files").rglob("*"):
        if obsolete.is_symlink() and obsolete not in expected_links:
            obsolete.unlink()
    write_text(review / ".gitignore", "files/\n", False)
    write_text(
        review / "README.md",
        "# Outside the 33 verified products\n\n"
        "This is a review area, not a product source. It includes other designs, "
        "multi-product images, non-product assets and unresolved candidates. "
        "An uncertain match is not a claim that the pictured item is absent from the catalog.\n\n"
        "`files/` contains generated local links and is intentionally ignored by Git. "
        "Main-checkout sources remain in their original location; these links are not portable product inputs. "
        "The tracked inventory is `tasks/catalog-reconciliation/image-library/inventory.json`.\n\n"
        "Rebuild with `python scripts/build_product_asset_library.py --review-inventory "
        "tasks/catalog-reconciliation/image-library/inventory.json --external-root /path/to/main-checkout`.\n",
        False,
    )
    report = {"counts": counts, "missing_sources": missing}
    write_text(review / "index.json", json.dumps(report, indent=2) + "\n", False)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--review-inventory", type=Path)
    parser.add_argument("--external-root", type=Path)
    args = parser.parse_args()
    registry = load_registry()
    policy = registry["authority_contract"]["product_image_export"]
    summaries = []
    reviewed_hashes = set()
    for sku in all_skus():
        product = get_product(sku)
        summaries.append(build_product(product, policy, args.check))
        reviewed_hashes.update(s["sha256"] for s in product["asset_library"]["sources"])
    overview = {
        "authority": "logo-registry.json",
        "product_count": len(summaries),
        "products": summaries,
    }
    write_text(
        ROOT / "assets/products/catalog/index.json",
        json.dumps(overview, indent=2) + "\n",
        args.check,
    )
    if args.review_inventory:
        if args.check:
            parser.error("--review-inventory cannot be used with --check")
        review = build_review(args.review_inventory, args.external_root, reviewed_hashes)
        print("Review area:", review["counts"], "missing:", len(review["missing_sources"]))
    print(f"PASS: {len(summaries)} products; {sum(s['unique_exports'] for s in summaries)} exports")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
