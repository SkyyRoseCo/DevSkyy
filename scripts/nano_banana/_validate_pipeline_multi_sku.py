"""Multi-SKU production-pipeline validator — manual, paid-call validator.

NOT FOR CI. Run manually to surface per-SKU regressions in the
production pipeline that single-SKU `_validate_layer1.py` cannot
detect. Each picked SKU exercises the full 5-step flow (describe →
route → generate → QA → refine) via `ProductionPipeline.run_batch`.

Cost: ~$5–$15 across 4 SKUs × 1 view each (configurable via MAX_USD
env var, default $10). Leading-underscore filename signals "internal
validator, not a library script."

Why this exists: `_validate_layer1.py` validates only br-001 against
the canonical dossier. After the VisionContext refactor (Phase 3 of
the closeout, PR #487), we needed cross-SKU evidence that the typed
dataclass + Tier 2 dossier path holds across collections (Black Rose,
Love Hurts, Signature, Kids Capsule). One bad SKU integration could
silently corrupt a downstream batch run; this script surfaces that.

Flow:
1. Load per-judge env files + FAL_KEY (mirrors `_validate_layer1.py`).
2. Resolve catalog rows for each picked SKU (name, collection, source).
3. Preflight: `build_dna_from_sku(sku)` for each — abort if any
   raises (KeyError or DossierMissingError) before any paid call.
4. STOP-AND-SHOW gate: print actions/SKUs/cost; require explicit
   `y\\n` on stdin.
5. `pipe = ProductionPipeline.from_env()` → `pipe.run_batch(products)`.
6. Per-SKU summary table + JSON dump to `tasks/multi-sku-validation-{ts}.json`.
7. Hard cost cap: if running total exceeds MAX_USD, break the loop
   and write partial results before exit.

Usage:
    python scripts/nano_banana/_validate_pipeline_multi_sku.py
    python scripts/nano_banana/_validate_pipeline_multi_sku.py --skus br-001,lh-004
    MAX_USD=2 python scripts/nano_banana/_validate_pipeline_multi_sku.py
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

DEFAULT_SKUS = ["br-001", "lh-004", "sg-007", "kids-001"]
DEFAULT_MAX_USD = 10.0


def _load(p: Path) -> None:
    """Source a .env-style file into os.environ. Pattern from _validate_layer1.py:41."""
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _load_env_files() -> list[str]:
    """Return list of missing required keys after env-file loading."""
    for envf in (
        ".env.judge-gpt-vision",
        ".env.judge-gemini-vision",
        ".env.judge-opus-thinking",
        ".env.hf",  # FAL_KEY lives here
        ".env.secrets",  # used by ProductionPipeline.from_env()
    ):
        _load(REPO / envf)

    needed = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "FAL_KEY"]
    return [k for k in needed if not os.environ.get(k)]


def _resolve_source_image(sku: str, name: str, src_override: str) -> Path | None:
    """Find the source photo for a SKU. Returns first existing candidate, else None.

    Resolution order (each product has at least one of these by convention):
      1. Catalog's `source_override` value resolved against products/ dir.
      2. Bundle dir `source-photo.{jpg,jpeg,png,webp}` (real product photo).
      3. Bundle dir `photo-front.{jpg,jpeg,png,webp}` (front product photo).
      4. Glob `{sku}.{ext}` or `{sku}-*.{ext}` in products/ dir, preferring
         "main" variants over -back/-composite/-detail/-real-back-three-quarter.
    """
    from skyyrose.core.paths import REPO_ROOT, WP_PRODUCTS_DIR

    # Canonical layout, rooted at this module's REPO (tests point REPO at a fixture tree).
    img_dir = REPO / WP_PRODUCTS_DIR.relative_to(REPO_ROOT)
    bundle_dir = REPO / "data/product-bundles" / name if name else None

    candidates: list[Path] = []

    if src_override:
        candidates.append(img_dir / src_override)

    if bundle_dir:
        for tag in ("source-photo", "photo-front"):
            for ext in ("jpg", "jpeg", "png", "webp"):
                candidates.append(bundle_dir / f"{tag}.{ext}")

    # Products-dir glob, ordered to prefer "primary" images
    skip_substrings = ("-back", "-composite", "-detail", "-real-")
    for ext in ("jpg", "jpeg", "png", "webp"):
        # Exact-stem match wins over prefix-glob
        candidates.append(img_dir / f"{sku}.{ext}")
    for ext in ("jpg", "jpeg", "png", "webp"):
        for match in sorted(img_dir.glob(f"{sku}-*.{ext}")):
            n = match.name.lower()
            if any(s in n for s in skip_substrings):
                continue
            candidates.append(match)

    return next((c for c in candidates if c.exists()), None)


def _resolve_products(skus: list[str]) -> tuple[list[dict], list[str]]:
    """Resolve catalog rows + verify source images. Returns (products, errors).

    products: list of dicts with shape {sku, name, collection, source_image}
    errors: list of SKUs that couldn't be resolved (missing catalog row OR no source).
    """
    from nano_banana.catalog import load_catalog

    catalog = load_catalog()
    products: list[dict] = []
    errors: list[str] = []

    for sku in skus:
        row = catalog.get(sku)
        if not row:
            errors.append(f"{sku}: not in catalog CSV")
            continue
        name = row.get("name", "")
        # nano_banana.catalog.load_catalog() renames CSV `render_source_override`
        # → `source_override` and does not expose `image`. Use the loader key.
        src_override = row.get("source_override", "")
        src_path = _resolve_source_image(sku, name, src_override)
        if not src_path:
            errors.append(
                f"{sku}: no source photo found (override='{src_override}', name='{name}')"
            )
            continue
        products.append(
            {
                "sku": sku,
                "name": name or sku,
                "collection": row.get("collection", ""),
                "source_image": str(src_path),
            }
        )
    return products, errors


def _preflight_dossiers(skus: list[str]) -> list[str]:
    """Verify each SKU has a loadable dossier. Returns list of failing SKUs."""
    from nano_banana.spec_builder import build_dna_from_sku

    failures: list[str] = []
    for sku in skus:
        try:
            build_dna_from_sku(sku)
        except Exception as exc:
            failures.append(f"{sku}: {type(exc).__name__}: {exc}")
    return failures


def _stop_and_show(products: list[dict], max_usd: float) -> bool:
    """Print action summary; require explicit `y` on stdin to proceed.

    Returns True if user confirmed, False otherwise. Auto-confirmed (skip
    interactive prompt) only if STOP_CONFIRM=y is set in the environment —
    used by tests.
    """
    print("\n" + "=" * 70)
    print("STOP — Confirm before proceeding (paid API call):")
    print("=" * 70)
    print("  Action  : multi-SKU production pipeline validator")
    print(f"  SKUs    : {len(products)} ({', '.join(p['sku'] for p in products)})")
    print(f"  Cost    : ~$5–$15 estimated (capped at ${max_usd:.2f} via MAX_USD)")
    print("  Output  : tasks/multi-sku-validation-{ts}.json")
    print("  Sources :")
    for p in products:
        size_kb = Path(p["source_image"]).stat().st_size / 1024
        print(f"    {p['sku']:<10} {Path(p['source_image']).name} ({size_kb:.0f} KB)")
    print("=" * 70)

    if os.environ.get("STOP_CONFIRM", "").lower() == "y":
        print("[STOP_CONFIRM=y in environment — auto-confirmed]")
        return True

    try:
        answer = input("Proceed? [y/N]: ").strip().lower()
    except EOFError:
        return False
    return answer in ("y", "yes")


def _summary_table(results: list) -> str:
    """Build a fixed-width summary table from PipelineResult list."""
    lines = []
    lines.append(
        f"{'SKU':<10} {'collection':<14} {'engine':<14} {'qa_score':>9} "
        f"{'pass':<5} {'refined':<8} {'cost_usd':>9} {'attempts':>9}"
    )
    lines.append("-" * 85)
    for r in results:
        lines.append(
            f"{r.sku:<10} {'':<14} {r.engine_used or '(none)':<14} "
            f"{r.qa_score:>9.1f} {str(r.qa_passed):<5} {str(r.refinement_applied):<8} "
            f"${r.cost_usd:>8.3f} {r.attempts:>9d}"
        )
    return "\n".join(lines)


def _run_with_cost_cap(pipe, products: list[dict], max_usd: float) -> tuple[list, bool]:
    """Run pipeline per-product with a hard cost cap. Returns (results, exceeded)."""
    from nano_banana.pipeline import PipelineResult

    results = []
    total_cost = 0.0
    exceeded = False

    for i, product in enumerate(products):
        sku = product.get("sku", "unknown")
        source = product.get("source_image", "")
        log.info("\n[%d/%d] %s — running...", i + 1, len(products), sku)

        if total_cost >= max_usd:
            log.warning(
                "MAX_USD reached ($%.2f >= $%.2f) — skipping %s and remaining SKUs.",
                total_cost,
                max_usd,
                sku,
            )
            exceeded = True
            results.append(
                PipelineResult(
                    sku=sku, view="front", issues=[f"Skipped: MAX_USD={max_usd:.2f} reached"]
                )
            )
            continue

        try:
            result = pipe.run_single(product, Path(source), view="front")
        except Exception as exc:
            log.error("%s: pipeline raised %s: %s", sku, type(exc).__name__, exc)
            result = PipelineResult(sku=sku, view="front", issues=[f"{type(exc).__name__}: {exc}"])

        results.append(result)
        total_cost += result.cost_usd
        log.info(
            "[%d/%d] %s done — qa=%.1f cost=$%.3f",
            i + 1,
            len(products),
            sku,
            result.qa_score,
            result.cost_usd,
        )

    return results, exceeded


log = logging.getLogger("validate_pipeline_multi_sku")


def main() -> int:
    """Driver entry point. Returns exit code."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--skus",
        type=str,
        default=",".join(DEFAULT_SKUS),
        help=(
            f"Comma-separated SKU list, OR 'all' for every SKU in the catalog "
            f"(default: {','.join(DEFAULT_SKUS)} — one per collection sample)"
        ),
    )
    parser.add_argument(
        "--collection",
        type=str,
        default="",
        help=(
            "Filter to one collection (black-rose, love-hurts, signature, kids-capsule). "
            "Combine with --skus all to run every SKU in that collection."
        ),
    )
    args = parser.parse_args()

    if args.skus.strip().lower() == "all":
        from nano_banana.catalog import load_catalog

        catalog = load_catalog()
        skus = sorted(
            sku
            for sku, row in catalog.items()
            if not args.collection or row.get("collection", "") == args.collection
        )
        log.info(
            "Loaded %d SKUs from catalog%s",
            len(skus),
            f" (collection={args.collection})" if args.collection else "",
        )
    else:
        skus = [s.strip() for s in args.skus.split(",") if s.strip()]

    max_usd = float(os.environ.get("MAX_USD", DEFAULT_MAX_USD))

    # --- 1. Env loading ---
    missing = _load_env_files()
    if missing:
        print(f"ERROR: missing env keys: {missing}", file=sys.stderr)
        print("Required env files (relative to repo root):", file=sys.stderr)
        print("  .env.judge-gpt-vision .env.judge-gemini-vision", file=sys.stderr)
        print("  .env.judge-opus-thinking .env.hf .env.secrets", file=sys.stderr)
        return 1
    log.info("All required env keys loaded.")

    # --- 2. Catalog resolution + image verification ---
    products, resolution_errors = _resolve_products(skus)
    if resolution_errors:
        print("\nERROR: SKU resolution failures:", file=sys.stderr)
        for err in resolution_errors:
            print(f"  - {err}", file=sys.stderr)
        return 2
    log.info("Resolved %d products from catalog.", len(products))

    # --- 3. Dossier preflight (no paid calls yet) ---
    dossier_failures = _preflight_dossiers(skus)
    if dossier_failures:
        print(
            "\nERROR: Dossier preflight failures (must hard-fail per Tier 2 rules):",
            file=sys.stderr,
        )
        for err in dossier_failures:
            print(f"  - {err}", file=sys.stderr)
        return 3
    log.info("All %d SKUs passed dossier preflight.", len(skus))

    # --- 4. STOP-AND-SHOW gate ---
    if not _stop_and_show(products, max_usd):
        print("\nAborted by user.", file=sys.stderr)
        return 4

    # --- 5. Build pipeline + run with cost cap ---
    from nano_banana.pipeline import ProductionPipeline

    log.info("Building pipeline from environment...")
    pipe = ProductionPipeline.from_env()

    t0 = time.monotonic()
    results, cap_exceeded = _run_with_cost_cap(pipe, products, max_usd)
    elapsed = time.monotonic() - t0

    # --- 6. Summary ---
    print("\n" + "=" * 70)
    print(f"RESULTS — {len(results)} SKUs in {elapsed:.0f}s")
    print("=" * 70)
    print(_summary_table(results))

    passed = sum(1 for r in results if r.qa_passed)
    refined = sum(1 for r in results if r.refinement_applied)
    total_cost = sum(r.cost_usd for r in results)
    print()
    print(f"  Passed QA       : {passed}/{len(results)}")
    print(f"  Refined         : {refined}/{len(results)}")
    print(f"  Total cost      : ${total_cost:.3f}")
    print(f"  Cost cap exceeded: {cap_exceeded}")

    # --- 7. Persist JSON ---
    out_path = REPO / "tasks" / f"multi-sku-validation-{int(time.time())}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(
            {
                "skus_requested": skus,
                "elapsed_seconds": elapsed,
                "max_usd": max_usd,
                "cap_exceeded": cap_exceeded,
                "summary": {
                    "passed": passed,
                    "refined": refined,
                    "total_cost": total_cost,
                },
                "results": [r.to_dict() for r in results],
            },
            indent=2,
        )
    )
    print(f"\n  Full results: {out_path.relative_to(REPO)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
