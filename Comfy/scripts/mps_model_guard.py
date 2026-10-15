#!/usr/bin/env python3
"""Fail-closed MPS model compatibility guard for Apple Silicon hosts.

Reads safetensors headers and rejects any model containing Float8 (F8_E4M3fn)
weight dtypes, which Apple MPS cannot execute. Also warns when combined model
weights exceed a configurable RAM budget.

Usage:
    python3 Comfy/scripts/mps_model_guard.py --check
    python3 Comfy/scripts/mps_model_guard.py --check --budget-gb 12
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

MODELS_ROOT = Path("/Users/theceo/ComfyUI-Shared/models")
MPS_INCOMPATIBLE_DTYPES = {"F8_E4M3", "F8_E5M2", "float8_e4m3fn", "float8_e5m2"}
DEFAULT_BUDGET_GB = 12.0


def read_safetensors_dtypes(path: Path) -> set[str]:
    try:
        with path.open("rb") as f:
            n = struct.unpack("<Q", f.read(8))[0]
            header = json.loads(f.read(n))
        return {v["dtype"] for v in header.values() if isinstance(v, dict) and "dtype" in v}
    except Exception as exc:
        return {f"ERROR:{exc}"}


def audit_models(models_root: Path, budget_gb: float) -> dict:
    results = []
    total_gb = 0.0
    any_incompatible = False

    for path in sorted(models_root.rglob("*.safetensors")):
        size_gb = path.stat().st_size / 1e9
        dtypes = read_safetensors_dtypes(path)
        incompatible = bool(dtypes & MPS_INCOMPATIBLE_DTYPES)
        if incompatible:
            any_incompatible = True
        total_gb += size_gb
        results.append(
            {
                "path": str(path.relative_to(models_root)),
                "size_gb": round(size_gb, 2),
                "dtypes": sorted(dtypes),
                "mps_compatible": not incompatible,
                "status": "MPS_INCOMPATIBLE" if incompatible else "MPS_SAFE",
            }
        )

    over_budget = total_gb > budget_gb
    return {
        "schema": "skyyrose.mps-model-guard/1",
        "models_root": str(models_root),
        "budget_gb": budget_gb,
        "total_weight_gb": round(total_gb, 2),
        "over_budget": over_budget,
        "any_incompatible": any_incompatible,
        "status": "FAIL" if (any_incompatible or over_budget) else "PASS",
        "models": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.add_argument("--budget-gb", type=float, default=DEFAULT_BUDGET_GB)
    parser.add_argument("--models-root", type=Path, default=MODELS_ROOT)
    args = parser.parse_args()

    report = audit_models(args.models_root, args.budget_gb)
    print(json.dumps(report, indent=2))

    if report["any_incompatible"]:
        bad = [m["path"] for m in report["models"] if not m["mps_compatible"]]
        print(f"\nMPS_INCOMPATIBLE models: {bad}", file=sys.stderr)
        print("Remove or replace Float8 weights before loading on Apple MPS.", file=sys.stderr)

    if report["over_budget"]:
        print(
            f"\nWeight budget exceeded: {report['total_weight_gb']:.1f} GB "
            f"> {args.budget_gb:.1f} GB limit. Severe swap pressure expected.",
            file=sys.stderr,
        )

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
