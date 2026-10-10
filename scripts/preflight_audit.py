#!/usr/bin/env python3
"""Preflight audit — classify every canonical SKU before any paid API call.

Classifies every SKU in the product registry (read through
``skyyrose.core.product.get_product`` — the count is read from it, never
hardcoded) into one of:
  READY                — bundle dir exists AND techflat-front.* on disk
  SKIPPED              — render_is_accessory == "1"
  PENDING_USER_ASSETS  — garment missing bundle dir or techflat-front file

Writes `renders/ghost-mannequin/SKIPPED.json` (accessories only, machine-readable).

Exit codes:
  0 — every registry SKU classified (READY + SKIPPED + PENDING == registry
      SKUs), even when PENDING > 0
  1 — unexpected error (registry unreadable or empty)

PENDING_USER_ASSETS is treated as an INFORMATIONAL WARNING, not a hard failure.
The user must provide the source assets before Phase 15 runs — the script's
job is to surface this clearly, not to abort the pipeline setup.

INFRA-05 / INFRA-06 / INFRA-07.
"""

from __future__ import annotations

import json
import shutil
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

from skyyrose.core.catalog_loader import bool_col
from skyyrose.core.product import all_skus, get_product
from skyyrose.core.product_registry import PRODUCT_REGISTRY

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BUNDLES_DIR = PROJECT_ROOT / "data" / "product-bundles"
DEFAULT_SKIPPED_OUT = PROJECT_ROOT / "renders" / "ghost-mannequin" / "SKIPPED.json"

_TECHFLAT_EXTENSIONS = ("jpeg", "jpg", "webp", "png")
_TERMINAL_WIDTH = shutil.get_terminal_size((100, 40)).columns
_SEP = "─" * min(_TERMINAL_WIDTH, 100)


class Status(StrEnum):
    READY = "READY"
    SKIPPED = "SKIPPED"
    PENDING_USER_ASSETS = "PENDING_USER_ASSETS"


@dataclass
class AuditEntry:
    sku: str
    name: str
    collection: str
    status: Status
    bundle_path: Path | None = None
    techflat_path: Path | None = None
    reason: str = ""


def _find_bundle_for_sku(sku: str, bundles_dir: Path = BUNDLES_DIR) -> Path | None:
    """Scan manifest.json files for a matching SKU (INFRA-02 pattern)."""
    if not bundles_dir.is_dir():
        return None
    for d in bundles_dir.iterdir():
        if not d.is_dir():
            continue
        manifest = d / "manifest.json"
        if not manifest.exists():
            continue
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if data.get("sku") == sku:
            return d
    return None


def _find_techflat_front(bundle: Path) -> Path | None:
    """Return path to techflat-front.* in the bundle, or None."""
    for ext in _TECHFLAT_EXTENSIONS:
        candidate = bundle / f"techflat-front.{ext}"
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def classify_sku(row: dict[str, str], bundles_dir: Path = BUNDLES_DIR) -> AuditEntry:
    """Classify one catalog row into a READY / SKIPPED / PENDING_USER_ASSETS entry.

    This is a pure function over a catalog-shaped dict (a product's
    ``get_product(sku)["catalog"]`` section) — it does not read the registry
    itself. Tests call this directly to assert on Status enum values rather than
    string-matching stdout output.
    """
    sku = row["sku"]
    name = row.get("name", "")
    collection = row.get("collection", "")

    if bool_col(row, "render_is_accessory"):
        return AuditEntry(
            sku=sku,
            name=name,
            collection=collection,
            status=Status.SKIPPED,
            reason="accessory — deferred to v1.3 flat-lay pipeline",
        )

    bundle = _find_bundle_for_sku(sku, bundles_dir=bundles_dir)
    if bundle is None:
        return AuditEntry(
            sku=sku,
            name=name,
            collection=collection,
            status=Status.PENDING_USER_ASSETS,
            reason="no bundle directory (user must provide source assets)",
        )

    techflat = _find_techflat_front(bundle)
    if techflat is None:
        return AuditEntry(
            sku=sku,
            name=name,
            collection=collection,
            status=Status.PENDING_USER_ASSETS,
            bundle_path=bundle,
            reason="bundle exists but techflat-front.* is missing",
        )

    return AuditEntry(
        sku=sku,
        name=name,
        collection=collection,
        status=Status.READY,
        bundle_path=bundle,
        techflat_path=techflat,
    )


def _print_header() -> None:
    print(_SEP)
    print("PREFLIGHT AUDIT — v1.2 Imagery Pipeline")
    print(_SEP)
    print(f"Registry: {PRODUCT_REGISTRY}")
    print(f"Bundles: {BUNDLES_DIR}")
    print(_SEP)


def _print_entries(entries: list[AuditEntry]) -> None:
    for i, entry in enumerate(entries, start=1):
        print(f"  [{i:02d}]  {entry.sku:<12}  {entry.status.value}")
        print(f"        {entry.name}  [{entry.collection}]")
        if entry.status == Status.PENDING_USER_ASSETS:
            print(f"        → {entry.reason}")
        elif entry.status == Status.READY and entry.techflat_path:
            print(f"        → {entry.techflat_path.name}")
    print(_SEP)


def _print_summary(entries: list[AuditEntry], catalog_total: int) -> None:
    ready = [e for e in entries if e.status == Status.READY]
    skipped = [e for e in entries if e.status == Status.SKIPPED]
    pending = [e for e in entries if e.status == Status.PENDING_USER_ASSETS]

    print("SUMMARY")
    print(_SEP)
    print(f"  READY:               {len(ready):3d}")
    print(f"  SKIPPED:             {len(skipped):3d}  (out-of-scope accessories)")
    print(f"  PENDING_USER_ASSETS: {len(pending):3d}  (user must provide source assets)")
    print(f"  {'─' * 40}")
    print(f"  TOTAL:               {len(entries):3d} / {catalog_total}")
    print(_SEP)

    if pending:
        print()
        print("PENDING_USER_ASSETS — user action required before Phase 15:")
        for entry in pending:
            print(f"  • {entry.sku:<12} {entry.name}")
            print(f"    reason: {entry.reason}")
        print()

    if skipped:
        print("SKIPPED (accessories → v1.3):")
        for entry in skipped:
            print(f"  • {entry.sku:<12} {entry.name}")
        print()


def _write_skipped_json(
    entries: list[AuditEntry],
    skipped_out: Path,
) -> None:
    """Write SKIPPED.json (accessories only — not PENDING)."""
    accessories = [e for e in entries if e.status == Status.SKIPPED]
    in_scope_garments = sum(1 for e in entries if e.status != Status.SKIPPED)

    payload = {
        "reason": "out-of-scope accessories — deferred to v1.3 flat-lay pipeline",
        "skipped": [
            {"sku": e.sku, "name": e.name, "collection": e.collection} for e in accessories
        ],
        "generated_at": datetime.now(UTC).isoformat(),
        "total_in_scope_garments": in_scope_garments,
        "total_skipped_accessories": len(accessories),
    }

    skipped_out.parent.mkdir(parents=True, exist_ok=True)
    skipped_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {skipped_out}")


def main(
    *,
    bundles_dir: Path = BUNDLES_DIR,
    skipped_out: Path | None = None,
) -> int:
    """Run the preflight audit. Returns 0 on success, 1 on unexpected error."""
    try:
        rows = [get_product(sku)["catalog"] for sku in all_skus()]
    except OSError as exc:
        print(f"ERROR: cannot read the product registry: {exc}", file=sys.stderr)
        return 1

    if not rows:
        print("ERROR: the product registry has zero products", file=sys.stderr)
        return 1

    _print_header()

    entries = [classify_sku(row, bundles_dir=bundles_dir) for row in rows]
    _print_entries(entries)
    _print_summary(entries, catalog_total=len(rows))

    out_path = skipped_out if skipped_out is not None else DEFAULT_SKIPPED_OUT
    _write_skipped_json(entries, out_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
