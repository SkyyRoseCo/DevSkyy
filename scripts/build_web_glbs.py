#!/usr/bin/env python3
"""Build CDN-ready garment GLBs: fabric sheen patch → gltfpack (meshopt + KTX2) → web gate.

For every product in the registry (``logo-registry.json`` → ``products[sku]``, the single
product SOT) this script:

1. reads ``<src-dir>/<sku>.glb`` (missing sources are recorded, never silently skipped);
2. classifies the exterior fabric from the founder's ``garment.materials.specification``
   (unclassifiable prose fails closed) and patches ``KHR_materials_sheen`` losslessly —
   anisotropy only for SKUs passed via ``--anisotropy-sku``;
3. compresses with ``gltfpack -cc -tc`` (binary from ``GLTFPACK_BIN`` or PATH);
4. gates the result (≤3 MB, meshopt + basisu, sheen on every material, KTX2-only images)
   and publishes it to ``<out-dir>/<sku>.glb`` ONLY if the gate passes.

``--prepacked-dir`` (opt-in) covers SKUs whose uncompressed source is gone but an
already-packed copy exists: the sheen patch is applied to that file's JSON chunk only
(meshopt/KTX2 payload carried over byte-for-byte, no re-encode) and the same gate decides.
A source GLB always takes precedence over a prepacked copy.

Local files only: zero network, zero paid calls, zero WordPress/WooCommerce writes. It never
writes into ``renders/3d/web`` (the legacy hand-built set) or over the source directory.

Usage:
    GLTFPACK_BIN=/path/to/gltfpack python scripts/build_web_glbs.py
    python scripts/build_web_glbs.py --sku br-006 --sku sg-011
    python scripts/build_web_glbs.py --sku br-006 --anisotropy-sku br-006=0.4
    python scripts/build_web_glbs.py --sku br-001 --prepacked-dir renders/3d/web

One SKU can never take the batch down: any unexpected exception is recorded against that SKU
and the run continues, so the report always describes what was published.

Exit codes: 0 all SKUs published · 1 any SKU missing/unclassified/failed · 2 usage refused.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from skyyrose.core.product_registry import load_registry  # noqa: E402
from skyyrose.elite_studio.pipeline3d.glb_container import GlbFormatError  # noqa: E402
from skyyrose.elite_studio.pipeline3d.glb_materials import (  # noqa: E402
    SHEEN_PRESETS,
    AnisotropyParams,
    MaterialPatchError,
    SheenPreset,
    UnclassifiedFabricError,
    apply_fabric_extensions,
    classify_product,
)
from skyyrose.elite_studio.pipeline3d.glb_optimize import (  # noqa: E402
    WEB_BUDGET_BYTES,
    WEB_PACK_FLAGS,
    GltfpackError,
    GltfpackNotFoundError,
    gltfpack_version,
    pack_for_web,
    resolve_gltfpack,
    web_gate,
)
from skyyrose.elite_studio.pipeline3d.preflight import _SKU_RE  # noqa: E402

DEFAULT_SRC_DIR = PROJECT_ROOT / "renders" / "3d"
DEFAULT_OUT_DIR = DEFAULT_SRC_DIR / "web-v2"
LEGACY_WEB_DIR = DEFAULT_SRC_DIR / "web"


class UsageError(ValueError):
    """Arguments that must stop the run before any file is written."""


@dataclass(frozen=True)
class BuildContext:
    """Everything a single SKU build needs, resolved once before the loop."""

    src_dir: Path
    out_dir: Path
    work_dir: Path
    binary: Path
    prepacked_dir: Path | None
    prior_kinds: Mapping[str, str]
    force: bool


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--src-dir", type=Path, default=DEFAULT_SRC_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--sku", action="append", default=[], help="repeatable; default all")
    parser.add_argument(
        "--anisotropy-sku",
        action="append",
        default=[],
        metavar="SKU=STRENGTH",
        help="opt-in KHR_materials_anisotropy strength in [0,1] for one SKU (repeatable)",
    )
    parser.add_argument(
        "--prepacked-dir",
        type=Path,
        default=None,
        help="read-only fallback of already-packed GLBs for SKUs with no source (JSON patch only)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="allow a prepacked patch to replace an output a previous run built from source",
    )
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--registry", type=Path, default=None, help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def select_skus(requested: list[str], products: dict[str, Any]) -> list[str]:
    unknown = sorted(set(requested) - set(products))
    if unknown:
        raise UsageError(f"SKUs not in the product registry: {', '.join(unknown)}")
    chosen = requested or list(products)
    invalid = [sku for sku in chosen if not _SKU_RE.match(sku)]
    if invalid:
        raise UsageError(f"invalid SKU format: {', '.join(invalid)}")
    return list(dict.fromkeys(chosen))


def parse_anisotropy(values: list[str], products: dict[str, Any]) -> dict[str, AnisotropyParams]:
    parsed: dict[str, AnisotropyParams] = {}
    for value in values:
        sku, separator, strength = value.partition("=")
        if not separator or sku not in products:
            raise UsageError(f"--anisotropy-sku expects a registry SKU=STRENGTH, got {value!r}")
        try:
            parsed[sku] = AnisotropyParams(strength=float(strength))
        except ValueError as exc:
            raise UsageError(f"--anisotropy-sku {value!r}: {exc}") from exc
    return parsed


def validate_dirs(src_dir: Path, out_dir: Path, prepacked_dir: Path | None = None) -> None:
    src, out, legacy = src_dir.resolve(), out_dir.resolve(), LEGACY_WEB_DIR.resolve()
    if out == legacy or out.is_relative_to(legacy):
        raise UsageError(f"refusing to write into the legacy web set {legacy}")
    if out == src:
        raise UsageError(f"refusing to write over the source directory {src}")
    if prepacked_dir is not None and prepacked_dir.resolve() == out:
        raise UsageError(f"refusing to write over the prepacked directory {out}")


def _preset_record(preset: SheenPreset | None, aniso: AnisotropyParams | None) -> dict | None:
    if preset is None:
        return None
    return {
        "sheen_color": preset.color,
        "sheen_roughness": preset.roughness,
        "anisotropy": aniso.strength if aniso else None,
    }


def _failed(entry: dict[str, Any], status: str, message: str) -> dict[str, Any]:
    return {**entry, "status": status, "gate_pass": False, "violations": [message]}


def _stage_patched(
    src: Path, work_dir: Path, preset: SheenPreset | None, aniso: AnisotropyParams | None
) -> Path:
    if preset is None and aniso is not None:
        raise MaterialPatchError("anisotropy requested for a fabric class without sheen")
    data = src.read_bytes()
    patched = data if preset is None else apply_fabric_extensions(data, preset, anisotropy=aniso)
    staged = work_dir / src.name
    staged.write_bytes(patched)
    return staged


def _resolve_source(sku: str, src_dir: Path, prepacked_dir: Path | None) -> tuple[Path, str]:
    source = src_dir / f"{sku}.glb"
    if source.is_file() or prepacked_dir is None:
        return source, "source"
    prepacked = prepacked_dir / f"{sku}.glb"
    return (prepacked, "prepacked") if prepacked.is_file() else (source, "source")


def build_one(
    sku: str,
    product: dict[str, Any],
    context: BuildContext,
    aniso: AnisotropyParams | None,
) -> dict[str, Any]:
    """Build one SKU. Any unexpected failure is recorded, never raised into the batch."""
    base: dict[str, Any] = {"sku": sku, "name": product.get("catalog", {}).get("name")}
    try:
        return _build_one(sku, product, context, aniso)
    except Exception as exc:  # noqa: BLE001 — one bad SKU must not abort the remaining ones
        return _failed({**base, "source_kind": None}, "error", f"{type(exc).__name__}: {exc}")


def _build_one(
    sku: str,
    product: dict[str, Any],
    context: BuildContext,
    aniso: AnisotropyParams | None,
) -> dict[str, Any]:
    src, source_kind = _resolve_source(sku, context.src_dir, context.prepacked_dir)
    entry: dict[str, Any] = {
        "sku": sku,
        "name": product.get("catalog", {}).get("name"),
        "status": "ok",
        "source_kind": source_kind,
        "fabric_class": None,
        "matched_keyword": None,
        "preset": None,
        "src_bytes": None,
        "out_bytes": None,
        "gate_pass": False,
        "violations": [],
    }
    if not src.is_file():
        return _failed(entry, "missing_source", f"source not found: {src}")
    if source_kind == "prepacked" and not context.force:
        if context.prior_kinds.get(sku) == "source":
            return _failed(
                entry,
                "refused_downgrade",
                "a previous run built this SKU from its uncompressed source; refusing to replace "
                "it with a JSON-patched prepacked copy (pass --force to override)",
            )
    try:
        match = classify_product(product)
    except UnclassifiedFabricError as exc:
        return _failed(entry, "unclassified", str(exc))
    preset = SHEEN_PRESETS[match.fabric_class]
    entry = {
        **entry,
        "fabric_class": match.fabric_class.value,
        "matched_keyword": match.keyword,
        "preset": _preset_record(preset, aniso),
        "src_bytes": src.stat().st_size,
    }
    dirs = (context.out_dir, context.work_dir)
    if source_kind == "prepacked":
        return _patch_and_publish(entry, src, dirs, (preset, aniso))
    return _pack_and_publish(entry, src, dirs, context.binary, (preset, aniso))


def _gate_and_publish(
    entry: dict[str, Any], candidate: Path, out_dir: Path, preset: SheenPreset | None
) -> dict[str, Any]:
    gate = web_gate(candidate, require_sheen=preset is not None)
    if not gate.passed:
        return {
            **entry,
            "status": "gate_failed",
            "out_bytes": gate.size_bytes,
            "violations": list(gate.violations),
        }
    published = out_dir / f"{entry['sku']}.glb"
    os.replace(candidate, published)
    return {**entry, "out_bytes": published.stat().st_size, "gate_pass": True}


def _patch_and_publish(
    entry: dict[str, Any],
    src: Path,
    dirs: tuple[Path, Path],
    materials: tuple[SheenPreset | None, AnisotropyParams | None],
) -> dict[str, Any]:
    out_dir, work_dir = dirs
    preset, aniso = materials
    try:
        staged = _stage_patched(src, work_dir, preset, aniso)
    except (GlbFormatError, MaterialPatchError) as exc:
        return _failed(entry, "patch_failed", str(exc))
    return _gate_and_publish(entry, staged, out_dir, preset)


def _pack_and_publish(
    entry: dict[str, Any],
    src: Path,
    dirs: tuple[Path, Path],
    binary: Path,
    materials: tuple[SheenPreset | None, AnisotropyParams | None],
) -> dict[str, Any]:
    out_dir, work_dir = dirs
    preset, aniso = materials
    try:
        staged = _stage_patched(src, work_dir, preset, aniso)
    except (GlbFormatError, MaterialPatchError) as exc:
        return _failed(entry, "patch_failed", str(exc))
    packed = work_dir / "packed" / src.name
    try:
        pack_for_web(staged, packed, binary=binary)
    except (GltfpackError, subprocess.TimeoutExpired) as exc:
        return _failed(entry, "pack_failed", str(exc))
    return _gate_and_publish(entry, packed, out_dir, preset)


def summarise(entries: list[dict[str, Any]]) -> dict[str, Any]:
    published = [e["out_bytes"] for e in entries if e["status"] == "ok"]
    return {
        "total": len(entries),
        "by_status": dict(Counter(e["status"] for e in entries)),
        "published_bytes": sum(published),
        "published_avg_bytes": round(sum(published) / len(published)) if published else 0,
    }


def prior_source_kinds(path: Path) -> dict[str, str]:
    """Read the previous run's report so a prepacked patch cannot silently downgrade it."""
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    entries = report.get("entries") if isinstance(report, dict) else None
    if not isinstance(entries, list):
        return {}
    return {
        entry["sku"]: entry["source_kind"]
        for entry in entries
        if isinstance(entry, dict)
        and isinstance(entry.get("sku"), str)
        and isinstance(entry.get("source_kind"), str)
        and entry.get("status") == "ok"
    }


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    staging = path.with_suffix(path.suffix + ".tmp")
    staging.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    os.replace(staging, path)


def print_table(entries: list[dict[str, Any]]) -> None:
    print(f"{'sku':<10}{'class':<14}{'keyword':<14}{'src MB':>8}{'out MB':>8}  status")
    for e in entries:
        src_mb = f"{e['src_bytes'] / 1e6:.2f}" if e["src_bytes"] else "-"
        out_mb = f"{e['out_bytes'] / 1e6:.2f}" if e["out_bytes"] else "-"
        klass, keyword = e["fabric_class"] or "-", e["matched_keyword"] or "-"
        print(f"{e['sku']:<10}{klass:<14}{keyword:<14}{src_mb:>8}{out_mb:>8}  {e['status']}")


def _prepare(args: argparse.Namespace) -> tuple[dict, list[str], dict, Path]:
    products = load_registry(args.registry)["products"]
    skus = select_skus(args.sku, products)
    anisotropy = parse_anisotropy(args.anisotropy_sku, products)
    validate_dirs(args.src_dir, args.out_dir, args.prepacked_dir)
    try:
        binary = resolve_gltfpack()
    except GltfpackNotFoundError as exc:
        raise UsageError(str(exc)) from exc
    return products, skus, anisotropy, binary


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        products, skus, anisotropy, binary = _prepare(args)
    except (UsageError, ValueError, OSError) as exc:
        print(f"build_web_glbs: {exc}", file=sys.stderr)
        return 2
    args.out_dir.mkdir(parents=True, exist_ok=True)
    report_path = args.report or args.out_dir / "build_report.json"
    # Probed before the loop: a failure here must not land after files are published.
    try:
        version = gltfpack_version(binary)
    except (GltfpackError, subprocess.SubprocessError, OSError) as exc:
        print(f"build_web_glbs: {binary} is not runnable: {exc}", file=sys.stderr)
        return 2
    prior_kinds = prior_source_kinds(report_path)
    with tempfile.TemporaryDirectory(dir=args.out_dir, prefix=".build-") as scratch:
        context = BuildContext(
            src_dir=args.src_dir,
            out_dir=args.out_dir,
            work_dir=Path(scratch),
            binary=binary,
            prepacked_dir=args.prepacked_dir,
            prior_kinds=prior_kinds,
            force=args.force,
        )
        entries = [build_one(sku, products[sku], context, anisotropy.get(sku)) for sku in skus]
    report = {
        "generated": datetime.now(UTC).isoformat(timespec="seconds"),
        "tool": {"gltfpack": str(binary), "version": version, "flags": list(WEB_PACK_FLAGS)},
        "src_dir": str(args.src_dir),
        "prepacked_dir": str(args.prepacked_dir) if args.prepacked_dir else None,
        "out_dir": str(args.out_dir),
        "budget_bytes": WEB_BUDGET_BYTES,
        "entries": entries,
        "summary": summarise(entries),
    }
    write_report(report_path, report)
    print_table(entries)
    print(json.dumps(report["summary"]))
    return 0 if all(e["status"] == "ok" for e in entries) else 1


if __name__ == "__main__":
    raise SystemExit(main())
