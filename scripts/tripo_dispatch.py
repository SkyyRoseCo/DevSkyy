"""
Tripo multiview dispatch — STOP-AND-SHOW gated SKU imagery generation.

Probes balance, shows a manifest (SKUs, source images, cost), and waits for
explicit "y" before dispatching any paid Tripo generate_multiview_image API
calls via the Elite Studio creative hub.

Outputs land in renders/output/tripo/<sku>/ — NOT the WordPress theme.
A second manual SFTP copy step (with its own confirmation) moves approved
images into wordpress-theme/skyyrose-flagship/assets/images/products/.

Usage:
    # Priority SKUs only (those missing both front_model_image + back_model_image)
    python scripts/tripo_dispatch.py

    # All 33 published SKUs
    python scripts/tripo_dispatch.py --all

    # Single SKU (useful for testing; defaults to dry-run)
    python scripts/tripo_dispatch.py --sku br-001
    python scripts/tripo_dispatch.py --sku br-001 --execute
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# skyyrose is not pip-installed. Only mutate sys.path when the import actually
# fails (CLI run from an arbitrary cwd) so merely importing this module (tests)
# leaves interpreter-wide import resolution untouched.
try:
    from skyyrose.core.sot_images import resolve_image  # noqa: E402
except ImportError:  # pragma: no cover — CLI invocation outside the repo root
    sys.path.insert(0, str(REPO_ROOT))
    from skyyrose.core.sot_images import resolve_image  # noqa: E402

CATALOG_CSV = REPO_ROOT / "wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv"
THEME_ROOT = REPO_ROOT / "wordpress-theme/skyyrose-flagship"
DOSSIER_DIR = THEME_ROOT / "data/dossiers"
OUTPUT_DIR = REPO_ROOT / "renders/output/tripo"
CREDITS_PER_SKU = 10  # flux.1_kontext_pro + generate_multiview_image template

# Tripo's `generate_multiview_image` template feeds a single source image into
# FLUX.1 Kontext, which then synthesises 4 viewing angles. It accepts NO prompt,
# NO reference overlays, NO dossier branding spec, NO palette token. With no
# canon to anchor against, FLUX freelances on any non-trivial branded surface:
# - Branded SKUs render with invented logos (the "rose-on-cloud" motif seen on
#   br-001 / br-011 / sg-007 in the May 8 batch)
# - Model-on shots get re-built as different garment types (br-011 hockey jersey
#   → cyan hoodie)
# - Garbled label patches with hallucinated text appear on cuffs
#
# Therefore Tripo multiview is for UNBRANDED CLEAN TECH-FLATS ONLY. Branded
# SKUs with a populated dossier `logo_reference` MUST route through the ADK
# render_pipeline (see agents/render_pipeline/) which applies logo overlays,
# 3-judge QA tournament, and refine loop. The guard below blocks branded SKUs
# at the dispatch boundary so this regression cannot recur silently.


def load_catalog() -> list[dict[str, str]]:
    from skyyrose.core.catalog_loader import read_catalog_rows

    return read_catalog_rows(CATALOG_CSV)


def resolve_source_image(row: dict[str, str]) -> Path:
    override = row.get("render_source_override", "").strip()
    if override and "/" not in override:
        return THEME_ROOT / "assets/images/products" / override
    if override:
        return THEME_ROOT / override
    sku = row.get("sku", "")
    rel = resolve_image(sku, "packshot")
    if rel is None:
        raise SystemExit(
            f"SKU {sku!r} has no SOT packshot image — regenerate sot.json "
            "(data/build-collection-sot.py) or set render_source_override in the catalog CSV."
        )
    return THEME_ROOT / rel


def _image_exists(row: dict[str, str], field: str) -> bool:
    val = row.get(field, "").strip()
    if not val:
        return False
    candidate = THEME_ROOT / val
    return candidate.exists()


# --------------------------------------------------------------------------- #
# Hallucination prevention guards (RCA bug #BUG-tripo-hallu-001, 2026-05-11)
# --------------------------------------------------------------------------- #


def _load_dossier_logo_reference(row: dict[str, str]) -> str:
    """Return the dossier's `logo_reference` frontmatter value (empty string
    when the dossier file is missing or the field is absent/blank).

    Done with a small regex parse instead of pulling in PyYAML — the field
    is single-line `key: value` and the rest of the dossier body never
    intrudes.
    """
    slug = row.get("dossier_slug", "").strip()
    if not slug:
        return ""
    dossier_path = DOSSIER_DIR / f"{slug}.md"
    if not dossier_path.exists():
        return ""
    try:
        text = dossier_path.read_text(encoding="utf-8")
    except OSError:
        return ""
    # Frontmatter lives between the first two `---` fences.
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 4)
    if end < 0:
        return ""
    frontmatter = text[3:end]
    for line in frontmatter.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        if key.strip() == "logo_reference":
            return value.strip().strip("\"'")
    return ""


def _has_tech_flat_source(row: dict[str, str]) -> bool:
    """Tripo multiview expects an UNBRANDED CLEAN TECH-FLAT as input. The
    catalog `image` column is the canonical tech-flat field; `front_model_image`
    is a model-on shot that breaks the template (FLUX rebuilds the garment
    from scratch — see br-011 → cyan hoodie regression).
    """
    image_field = row.get("image", "").strip()
    if not image_field:
        return False
    candidate = THEME_ROOT / image_field
    return candidate.exists()


def _is_catalog_tech_flat(row: dict[str, str]) -> bool:
    """The catalog `render_is_tech_flat` column is the explicit operator
    declaration that the SKU's `image` field points to a clean unbranded
    tech-flat — the only kind of source Tripo's multiview template can
    preserve without hallucinating.

    Value "1" → catalog-flagged tech-flat. Anything else (including "0" or
    empty) is treated as NOT a tech-flat. File-existence is a weaker check
    (`_has_tech_flat_source`) because a file can exist and still be a
    model-on shot or a product render — see br-011: PNG present, but the
    catalog explicitly marks `render_is_tech_flat=0`.
    """
    return row.get("render_is_tech_flat", "").strip() == "1"


def classify_skus(
    rows: list[dict[str, str]], allow_branded: bool = False
) -> tuple[list[dict[str, str]], list[tuple[dict[str, str], str]]]:
    """Split target SKUs into (approved_for_tripo, blocked_with_reason).

    Block conditions (in order — first match wins for the reason string):
      1. Dossier `logo_reference` is populated → BRANDED, route to ADK
         (unless ``allow_branded`` is True — escape hatch with WARNING).
      2. Catalog `render_is_tech_flat` is not "1" → NOT A TECH-FLAT.
         The catalog is the authority on whether the source is a clean
         unbranded tech-flat; file existence alone is insufficient
         (br-011 had a PNG file but it was a branded product render,
         not a tech-flat — flag was "0").
      3. Catalog `image` column empty or file missing → NO TECH-FLAT FILE.

    A SKU that passes all checks is approved for Tripo multiview.
    """
    approved: list[dict[str, str]] = []
    blocked: list[tuple[dict[str, str], str]] = []
    for row in rows:
        logo_ref = _load_dossier_logo_reference(row)
        if logo_ref and not allow_branded:
            blocked.append(
                (
                    row,
                    f"BRANDED — dossier logo_reference={logo_ref!r}. "
                    "Route to ADK render_pipeline; Tripo multiview hallucinates branding.",
                )
            )
            continue
        if not _is_catalog_tech_flat(row):
            blocked.append(
                (
                    row,
                    "NOT A TECH-FLAT — catalog `render_is_tech_flat` is not '1'. "
                    "Tripo multiview needs a clean unbranded tech-flat per catalog flag.",
                )
            )
            continue
        if not _has_tech_flat_source(row):
            blocked.append(
                (
                    row,
                    "NO TECH-FLAT FILE — catalog `image` column empty or file missing. "
                    "Tripo multiview needs a clean tech-flat, not a model-on shot.",
                )
            )
            continue
        approved.append(row)
    return approved, blocked


def select_skus(
    rows: list[dict[str, str]],
    all_published: bool,
    single_sku: str | None,
) -> list[dict[str, str]]:
    published = [r for r in rows if r.get("published", "0").strip() == "1"]

    if single_sku:
        matched = [r for r in published if r["sku"] == single_sku]
        if not matched:
            sys.exit(f"SKU {single_sku!r} not found or not published in catalog.")
        return matched

    if all_published:
        return published

    # Default: priority set — SKUs that have a resolvable source image but
    # are missing at least one model image (most need Tripo the most).
    priority = []
    for r in published:
        has_source = resolve_source_image(r).exists()
        missing_front = not _image_exists(r, "front_model_image")
        missing_back = not _image_exists(r, "back_model_image")
        if has_source and (missing_front or missing_back):
            priority.append(r)
    return priority


async def _probe_balance() -> int:
    try:
        from tripo3d import TripoClient

        async with TripoClient() as client:
            result = await client.get_balance()
            if hasattr(result, "balance"):
                return int(result.balance)
            return int(result)
    except Exception as exc:
        print(f"  WARNING: balance probe failed ({exc}) — proceeding without balance check.")
        return -1


def show_manifest(
    target_rows: list[dict[str, str]],
    blocked: list[tuple[dict[str, str], str]],
    balance: int,
    dry_run: bool,
    allow_branded: bool = False,
) -> None:
    total_credits = len(target_rows) * CREDITS_PER_SKU
    print()
    print("=" * 70)
    print("STOP — Confirm before proceeding:")
    print("=" * 70)
    print("  Action       : Tripo generate_multiview_image (4 views per SKU)")
    print("  Template     : generate_multiview_image")
    print("  Model        : flux.1_kontext_pro")
    print("  Region       : .ai (https://api.tripo3d.ai/v2/openapi)")
    print(f"  Output       : {OUTPUT_DIR}/<sku>/")
    print()
    if blocked:
        print(f"  BLOCKED ({len(blocked)}) — will NOT be dispatched:")
        for row, reason in blocked:
            print(f"    {row['sku']:<22} {row['name']:<40}")
            print(f"      ↳ {reason}")
        print()
    if allow_branded:
        print("  WARNING: --force-branded is set. Branded SKUs are NOT blocked.")
        print("           These SKUs will hallucinate logos (see RCA #BUG-tripo-hallu-001).")
        print()
    print(f"  APPROVED ({len(target_rows)}):")
    for row in target_rows:
        src = resolve_source_image(row)
        size_note = f"{src.stat().st_size / 1024:.0f} KB" if src.exists() else "MISSING"
        print(f"    {row['sku']:<22} {row['name']:<40} source={size_note}")
    print()
    print(f"  Credits      : {len(target_rows)} SKUs × {CREDITS_PER_SKU} cr = {total_credits} cr")
    if balance >= 0:
        remaining = balance - total_credits
        status = "OK" if remaining >= 0 else "INSUFFICIENT"
        print(f"  Balance      : {balance} cr  →  after dispatch: {remaining} cr  [{status}]")
        if remaining < 0:
            print("  WARNING: insufficient balance — top up before dispatching.")
    print("  NOTE: Outputs land in renders/output/tripo/ — NOT the theme.")
    print("        A separate SFTP step (with its own confirmation) is required")
    print("        to publish approved images to skyyrose.co.")
    print("=" * 70)
    if dry_run:
        print("DRY RUN — no API calls dispatched. Pass --execute to proceed.")
    print()


def dispatch_sku(row: dict[str, str]) -> dict:
    """Invoke the creative hub for a single SKU synchronously.

    Only ``image_path`` is honored downstream. The previous version of this
    function passed ``model_version="flux.1_kontext_pro"`` as a second param,
    but ``tripo_generate_node`` in ``skyyrose/elite_studio/creative/nodes.py``
    reads only ``params["image_path"]`` (verified via grep) and the wrapped
    ``client.generate_multiview_image(image=...)`` call accepts no
    ``model_version`` argument (Tripo API docs: only ``type`` + ``file``).
    The model_version param was dead weight that suggested we had a knob
    we didn't.
    """
    import sys

    sys.path.insert(0, str(REPO_ROOT))

    from skyyrose.elite_studio.creative.runner import run_creative

    src = resolve_source_image(row)
    return run_creative(
        intent="tripo-generate",
        params={
            "image_path": str(src),
        },
        sku=row["sku"],
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Tripo multiview dispatch for SkyyRose SKUs.")
    ap.add_argument("--sku", default=None, help="Single SKU to process.")
    ap.add_argument(
        "--all",
        dest="all_published",
        action="store_true",
        help="Process all published SKUs (default: priority set only).",
    )
    ap.add_argument(
        "--execute",
        action="store_true",
        help="Actually dispatch paid API calls (default is dry-run).",
    )
    ap.add_argument(
        "--force-branded",
        action="store_true",
        help=(
            "Escape hatch: dispatch even branded SKUs (those with a populated "
            "dossier `logo_reference`). DANGEROUS — Tripo multiview will "
            "hallucinate the brand canon. See RCA #BUG-tripo-hallu-001."
        ),
    )
    args = ap.parse_args()

    if not os.environ.get("TRIPO_API_KEY"):
        print("ERROR: TRIPO_API_KEY env var not set.", file=sys.stderr)
        return 2

    rows = load_catalog()
    candidate_rows = select_skus(rows, all_published=args.all_published, single_sku=args.sku)

    if not candidate_rows:
        print("No SKUs match the selection criteria. Nothing to dispatch.")
        return 0

    # Hallucination prevention: block branded SKUs + no-techflat SKUs at the
    # dispatch boundary. See module docstring + RCA #BUG-tripo-hallu-001.
    target_rows, blocked = classify_skus(candidate_rows, allow_branded=args.force_branded)

    if not target_rows:
        print("All candidate SKUs were blocked by the hallucination-prevention guard.")
        print("Common causes:")
        print("  - Dossier `logo_reference` populated → SKU is branded; route to ADK render")
        print("  - Catalog `image` column empty → no tech-flat source for multiview")
        print()
        print(f"Blocked ({len(blocked)}):")
        for row, reason in blocked:
            print(f"  {row['sku']:<22} {reason}")
        return 3

    print("Probing Tripo balance...")
    balance = asyncio.run(_probe_balance())

    show_manifest(
        target_rows,
        blocked,
        balance,
        dry_run=not args.execute,
        allow_branded=args.force_branded,
    )

    if not args.execute:
        return 0

    # Confirm before any paid dispatch
    answer = input("Proceed? [y/N] ").strip().lower()
    if answer != "y":
        print("Aborted.")
        return 0

    print()
    results: list[tuple[str, bool, str]] = []
    for i, row in enumerate(target_rows, 1):
        sku = row["sku"]
        src = resolve_source_image(row)
        if not src.exists():
            print(f"[{i}/{len(target_rows)}] SKIP {sku} — source image not found: {src}")
            results.append((sku, False, f"source missing: {src}"))
            continue

        print(f"[{i}/{len(target_rows)}] Dispatching {sku}...")
        state = dispatch_sku(row)
        tripo = state.get("tripo_result") or {}
        success = tripo.get("success", False)
        views = tripo.get("views", [])
        error = tripo.get("error", state.get("error", "unknown"))

        if success:
            print(f"  OK — {len(views)} view(s) in {tripo.get('output_path', OUTPUT_DIR / sku)}")
        else:
            print(f"  FAILED — {error}")
        results.append((sku, success, error if not success else ""))

    print()
    print("=" * 70)
    ok = [r for r in results if r[1]]
    fail = [r for r in results if not r[1]]
    print(f"DONE: {len(ok)} succeeded, {len(fail)} failed.")
    if fail:
        print("Failed SKUs:")
        for sku, _, err in fail:
            print(f"  {sku}: {err}")
    print()
    print("Next step: review renders/output/tripo/ and then run the SFTP copy")
    print("step (with confirmation) to publish approved images to the theme.")
    return 0 if not fail else 1


if __name__ == "__main__":
    raise SystemExit(main())
