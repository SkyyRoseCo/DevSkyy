"""
Tripo publish — STOP-AND-SHOW gated copy + catalog update.

Discovers completed Tripo outputs in renders/output/tripo/<sku>/,
shows exactly what will change, waits for explicit "y", then:
  1. Converts PNG→webp (Pillow) and copies to theme assets/images/products/
  2. Updates front_model_image / back_model_image in skyyrose-catalog.csv

Destination naming convention:
  {render_output_slug}-front-model.webp
  {render_output_slug}-back-model.webp

View assignment (4-view output sorted by filename):
  index 0 → front,  index 2 → back
  (2-file fallback: index 0 → front, index 1 → back)
  (1-file fallback: index 0 → front only)

Usage:
    python scripts/tripo_publish.py              # all completed SKUs (dry-run)
    python scripts/tripo_publish.py --sku br-001 # single SKU
    python scripts/tripo_publish.py --execute    # actually copy + update catalog
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
TRIPO_OUTPUT = REPO_ROOT / "renders/output/tripo"
CATALOG_CSV = REPO_ROOT / "wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv"
ASSETS_DIR = REPO_ROOT / "wordpress-theme/skyyrose-flagship/assets/images/products"

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".tiff", ".bmp"}


def load_catalog() -> list[dict[str, str]]:
    from skyyrose.core.catalog_loader import read_catalog_rows

    return read_catalog_rows(CATALOG_CSV)


def catalog_by_sku(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {r["sku"]: r for r in rows}


def discover_outputs(single_sku: str | None) -> dict[str, list[Path]]:
    """Return {sku: sorted_image_files} for all completed Tripo outputs."""
    if not TRIPO_OUTPUT.exists():
        return {}

    result: dict[str, list[Path]] = {}
    for sku_dir in sorted(TRIPO_OUTPUT.iterdir()):
        if not sku_dir.is_dir():
            continue
        sku = sku_dir.name
        if single_sku and sku != single_sku:
            continue
        images = sorted(
            [f for f in sku_dir.iterdir() if f.suffix.lower() in IMAGE_EXTS],
            key=lambda p: p.name,
        )
        if images:
            result[sku] = images
    return result


def assign_views(images: list[Path]) -> dict[str, Path | None]:
    """Map front/back from filenames, falling back to sorted position."""
    if not images:
        return {"front": None, "back": None}

    # Prefer explicit view labels in filename (e.g. task_front.jpeg, task_back.jpeg)
    by_label: dict[str, Path] = {}
    for img in images:
        stem = img.stem.lower()
        for label in ("front", "back", "left", "right"):
            if stem.endswith(f"_{label}") or stem == label:
                by_label[label] = img
                break

    if by_label:
        return {"front": by_label.get("front"), "back": by_label.get("back")}

    # Positional fallback: sorted list, 4-view index convention
    front = images[0]
    if len(images) >= 4:
        back = images[2]
    elif len(images) >= 2:
        back = images[1]
    else:
        back = None
    return {"front": front, "back": back}


def dest_path(slug: str, view: str) -> Path:
    return ASSETS_DIR / f"{slug}-{view}-model.webp"


def convert_to_webp(src: Path, dst: Path) -> None:
    from PIL import Image

    img = Image.open(src)
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA")
    dst.parent.mkdir(parents=True, exist_ok=True)
    img.save(dst, "webp", quality=92, method=6)


def build_plan(
    outputs: dict[str, list[Path]],
    catalog: dict[str, dict[str, str]],
) -> list[dict]:
    plan = []
    for sku, images in outputs.items():
        row = catalog.get(sku)
        if not row:
            plan.append({"sku": sku, "error": "not in catalog", "ops": []})
            continue

        slug = row.get("render_output_slug", "").strip()
        if not slug:
            plan.append({"sku": sku, "error": "missing render_output_slug", "ops": []})
            continue

        views = assign_views(images)
        ops = []
        for view_name, src in views.items():
            if src is None:
                continue
            dst = dest_path(slug, view_name)
            catalog_field = "front_model_image" if view_name == "front" else "back_model_image"
            catalog_rel = f"assets/images/products/{dst.name}"
            ops.append(
                {
                    "view": view_name,
                    "src": src,
                    "dst": dst,
                    "catalog_field": catalog_field,
                    "catalog_value": catalog_rel,
                    "existing_catalog": row.get(catalog_field, "").strip(),
                }
            )
        plan.append({"sku": sku, "slug": slug, "error": None, "ops": ops})
    return plan


def show_manifest(plan: list[dict], dry_run: bool) -> None:
    print()
    print("=" * 70)
    print("STOP — Confirm before proceeding:")
    print("=" * 70)
    print("  Action  : Copy Tripo outputs → theme assets + update catalog CSV")
    print(f"  Source  : {TRIPO_OUTPUT}/")
    print(f"  Dest    : {ASSETS_DIR}/")
    print(f"  Catalog : {CATALOG_CSV}")
    print()

    for entry in plan:
        sku = entry["sku"]
        if entry.get("error"):
            print(f"  [{sku}] SKIP — {entry['error']}")
            continue
        print(f"  [{sku}]  slug={entry['slug']}")
        for op in entry["ops"]:
            src_size = f"{op['src'].stat().st_size / 1024:.0f} KB" if op["src"].exists() else "?"
            existing = op["existing_catalog"]
            change = (
                f"{existing!r} → {op['catalog_value']!r}"
                if existing
                else f"(empty) → {op['catalog_value']!r}"
            )
            print(f"    {op['view']:<6}  src={op['src'].name} ({src_size})  dst={op['dst'].name}")
            print(f"           catalog [{op['catalog_field']}]: {change}")
        print()

    ops_total = sum(len(e.get("ops", [])) for e in plan)
    skus_ok = sum(1 for e in plan if not e.get("error") and e.get("ops"))
    print(f"  Total   : {skus_ok} SKUs / {ops_total} image copies / 1 CSV rewrite")
    print("=" * 70)
    if dry_run:
        print("DRY RUN — no files written. Pass --execute to proceed.")
    print()


def execute_plan(plan: list[dict], rows: list[dict[str, str]]) -> int:
    catalog_map = catalog_by_sku(rows)
    errors: list[str] = []
    successful_changes: dict[str, dict[str, str]] = {}

    for entry in plan:
        if entry.get("error") or not entry.get("ops"):
            continue
        sku = entry["sku"]
        for op in entry["ops"]:
            src: Path = op["src"]
            dst: Path = op["dst"]
            try:
                print(f"  Converting {src.name} → {dst.name}...")
                convert_to_webp(src, dst)
                catalog_map[sku][op["catalog_field"]] = op["catalog_value"]
                successful_changes.setdefault(sku, {})[op["catalog_field"]] = op["catalog_value"]
                print(f"    OK  ({dst.stat().st_size / 1024:.0f} KB)")
            except Exception as exc:
                msg = f"{sku}/{op['view']}: {exc}"
                print(f"    FAILED — {msg}")
                errors.append(msg)

    if not successful_changes:
        return len(errors)

    # Commit changed image bindings to the registry; CSV is only an export.
    from skyyrose.core.product_registry import update_catalog_fields

    try:
        for sku, changes in successful_changes.items():
            update_catalog_fields(sku, changes)
        print("  Product registry and catalog export updated.")
    except Exception as exc:
        errors.append(f"registry update failed: {exc}")
        print(f"  FAILED to update registry — {exc}")

    return len(errors)


def main() -> int:
    ap = argparse.ArgumentParser(description="Publish Tripo outputs to theme + update catalog.")
    ap.add_argument("--sku", default=None, help="Single SKU to publish.")
    ap.add_argument(
        "--execute", action="store_true", help="Actually copy files and update catalog."
    )
    args = ap.parse_args()

    outputs = discover_outputs(args.sku)
    if not outputs:
        target = f"SKU {args.sku!r}" if args.sku else "any SKU"
        print(f"No Tripo output found for {target} in {TRIPO_OUTPUT}")
        print("Run 'python scripts/tripo_dispatch.py --execute' first.")
        return 0

    rows = load_catalog()
    catalog = catalog_by_sku(rows)
    plan = build_plan(outputs, catalog)

    show_manifest(plan, dry_run=not args.execute)

    if not args.execute:
        return 0

    answer = input("Proceed? [y/N] ").strip().lower()
    if answer != "y":
        print("Aborted.")
        return 0

    print()
    error_count = execute_plan(plan, rows)

    print()
    print("=" * 70)
    if error_count:
        print(f"DONE with {error_count} error(s) — review output above.")
    else:
        print("DONE — all images copied and catalog updated.")
        print()
        print("Next step: deploy the theme to publish images to skyyrose.co:")
        print("  cd wordpress-theme && npm run deploy")
    print("=" * 70)
    return 0 if not error_count else 1


if __name__ == "__main__":
    raise SystemExit(main())
