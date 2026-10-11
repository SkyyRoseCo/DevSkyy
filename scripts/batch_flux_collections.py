"""Batch FLUX synthesis pipeline — Love Hurts + Signature collections.

Iterates all active products in the specified collections and renders each
front (and back where back_image exists) view through the full pipeline:
  Stage 1  FLUX Kontext Pro  → base garment
  Stage 2  Gemini Flash      → decoration mask
  Stage 3  FLUX Fill Pro     → inpaint decoration
  Stage 5  Vision Audit      → fidelity gate + H4 retry

Usage:
    python scripts/batch_flux_collections.py
    python scripts/batch_flux_collections.py --collections love-hurts
    python scripts/batch_flux_collections.py --sku lh-002 sg-006
    python scripts/batch_flux_collections.py --dry-run

Outputs:
    renders/output/{name-slug}/{sku}-{view}/   accepted renders
    renders/quarantine/{sku}/{ts}/             rejected after 3 attempts
    renders/batch-report-{ts}.json            machine-readable summary
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

# skyyrose is not in the editable-install MAPPING — add project root so scripts/
# subdirectory invocations can resolve it without PYTHONPATH.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

for _f in [".env", ".env.hf", ".env.secrets"]:
    if Path(_f).exists():
        load_dotenv(_f, override=False)

from skyyrose.core.dossier_loader import DOSSIERS_DIR, get_product_with_dossier
from skyyrose.core.paths import THEME_ROOT
from skyyrose.core.product import get_product, load_registry
from skyyrose.core.sot_images import resolve_image
from skyyrose.elite_studio.synthesis.flux_pipeline import render
from skyyrose.elite_studio.synthesis.state.telemetry import CostTracker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("batch")

ASSETS_ROOT = THEME_ROOT
BATCH_COLLECTIONS = {"love-hurts", "signature"}


def _load_manifest(collections: set[str], skus: set[str]) -> list[dict]:
    """Return list of {sku, name, collection, front_path, back_path, dossier_slug}."""
    manifest = []
    # Registry order is the catalog order; every fact comes from get_product.
    for sku in load_registry()["products"]:
        row = get_product(sku)["catalog"]
        if row.get("published", "true").lower() == "false":
            continue
        if row["collection"] not in collections:
            continue
        if skus and sku not in skus:
            continue
        front_rel = resolve_image(sku, "packshot")
        if front_rel is None:
            logger.warning("skipping %s — SOT has no packshot image", sku)
            continue
        front_path = ASSETS_ROOT / front_rel
        back_rel = resolve_image(sku, "back_packshot")
        back_path = (ASSETS_ROOT / back_rel) if back_rel else None
        manifest.append(
            {
                "sku": sku,
                "name": row["name"],
                "collection": row["collection"],
                "dossier_slug": row.get("dossier_slug", ""),
                "front_path": front_path,
                "back_path": back_path,
            }
        )
    return manifest


def _print_plan(items: list[dict]) -> None:
    total_views = sum(2 if it["back_path"] else 1 for it in items)
    print(f"\n{'SKU':<10}{'Name':<40}{'Views'}")
    print("─" * 65)
    for it in items:
        views = "front+back" if it["back_path"] else "front"
        print(f"{it['sku']:<10}{it['name']:<40}{views}")
    print("─" * 65)
    print(f"{'Total:':<50}{len(items)} products  {total_views} views\n")


async def _run_view(
    *,
    sku: str,
    view: str,
    dossier: dict,
    techflat: Path,
    tracker: CostTracker,
    dry_run: bool,
) -> dict:
    """Render one view and return a result dict for the summary report."""
    if dry_run:
        return {"sku": sku, "view": view, "ok": None, "dry_run": True}

    result = await render(
        sku=sku,
        view=view,
        dossier=dossier,
        techflat_path=techflat,
        cost_tracker=tracker,
    )
    return {
        "sku": sku,
        "view": view,
        "ok": result.ok,
        "attempts": result.attempts,
        "duration_ms": result.duration_ms,
        "output_path": str(result.output_path) if result.output_path else None,
        "quarantine_path": str(result.quarantine_path) if result.quarantine_path else None,
        "violations": (
            [
                {"element": v.element, "region": v.region, "severity": v.severity}
                for v in result.audit_result.violations
            ]
            if result.audit_result
            else []
        ),
        "error": result.error,
    }


async def main(args: argparse.Namespace) -> int:
    collections = set(args.collections) if args.collections else BATCH_COLLECTIONS
    skus = set(args.sku) if args.sku else set()

    items = _load_manifest(collections, skus)
    if not items:
        print("No matching products found — check --collections / --sku filters.")
        return 1

    _print_plan(items)

    if args.dry_run:
        print("DRY RUN — no API calls made.")
        return 0

    tracker = CostTracker()
    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
    results: list[dict] = []
    batch_start = time.perf_counter()

    total_views = sum(2 if it["back_path"] else 1 for it in items)
    done = 0

    for item in items:
        sku = item["sku"]
        product = get_product_with_dossier(sku)
        dossier = product["dossier"]
        slug = dossier.get("slug", "")
        dossier["_dossier_path"] = str(DOSSIERS_DIR / f"{slug}.md") if slug else ""

        views: list[tuple[str, Path]] = [("front", item["front_path"])]
        if item["back_path"] and item["back_path"].is_file():
            views.append(("back", item["back_path"]))

        for view, techflat in views:
            done += 1
            print(
                f"\n[{done}/{total_views}] {sku} — {item['name']} ({view})  "
                f"techflat={techflat.name}"
            )
            row = await _run_view(
                sku=sku,
                view=view,
                dossier=dossier,
                techflat=techflat,
                tracker=tracker,
                dry_run=False,
            )
            results.append(row)
            status = "PASS" if row["ok"] else "FAIL"
            print(
                f"  → {status}  attempts={row.get('attempts', '?')}  "
                f"duration={row.get('duration_ms', 0) // 1000}s  "
                f"cost_so_far=${tracker.total_usd:.3f}"
            )
            if row.get("violations"):
                for v in row["violations"]:
                    print(f"     [{v['severity']}] {v['element']} @ {v['region']}")

    total_ms = int((time.perf_counter() - batch_start) * 1000)
    passed = sum(1 for r in results if r.get("ok"))
    failed = len(results) - passed

    print("\n" + "━" * 65)
    print(
        f"BATCH COMPLETE  {passed}/{len(results)} passed  "
        f"cost=${tracker.total_usd:.3f}  time={total_ms // 1000}s"
    )
    if failed:
        print(f"\nFailed ({failed}):")
        for r in results:
            if not r.get("ok"):
                print(f"  {r['sku']} {r['view']}  quarantine={r.get('quarantine_path', '?')}")
    print("━" * 65)

    report_path = Path(f"renders/batch-report-{ts}.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(
            {
                "timestamp": ts,
                "collections": sorted(collections),
                "total_views": len(results),
                "passed": passed,
                "failed": failed,
                "total_cost_usd": tracker.total_usd,
                "total_duration_ms": total_ms,
                "results": results,
            },
            indent=2,
            default=str,
        )
    )
    print(f"\nReport: {report_path}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch FLUX render — Love Hurts + Signature")
    parser.add_argument(
        "--collections",
        nargs="+",
        default=None,
        help="Collections to render (default: love-hurts signature)",
    )
    parser.add_argument(
        "--sku", nargs="+", default=None, help="Render specific SKUs only (space-separated)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print plan without making API calls"
    )
    args = parser.parse_args()
    sys.exit(asyncio.run(main(args)))
