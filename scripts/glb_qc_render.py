#!/usr/bin/env python3
"""Render GLBs in the production three.js viewer and pixel-diff them against each other.

The QC question this answers is "what does the PDP viewer actually show, and did this
change alter it" — so it renders through the theme's own vendored three r170 with the
production viewer's constants, not through a second engine. See
``skyyrose/elite_studio/pipeline3d/webgl_qc.py`` for why that matters and what holds the
renders deterministic.

Local and free: no network, no paid calls, nothing written outside ``--out-dir``. The
HTTP server it starts is bound to 127.0.0.1 and serves ONLY a scratch directory holding
the harness, a link to the vendored three tree, and a link per GLB.

Exit codes:
    0  every render succeeded, and every requested diff showed a real pixel difference
    1  a render or diff failed — including a console/page error, a blank frame, or an
       --out-dir that already holds PNGs without --overwrite
    2  usage error (argparse)
    3  VOID — at least one diff was byte-identical. That is NOT "no visible difference":
       the change under test produced no pixels, so any look-based verdict drawn from
       those two images would be a verdict on a null result. Callers must branch on it.

Usage:
    python scripts/glb_qc_render.py --glb base=renders/3d/web-v2/br-006.glb \\
        --glb candidate=/tmp/br-006-aniso.glb --diff base:candidate \\
        --out-dir renders/3d/qc/br-006-aniso
    python scripts/glb_qc_render.py --glb br-006=renders/3d/web-v2/br-006.glb \\
        --angle raking --out-dir renders/3d/qc/look
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from skyyrose.elite_studio.pipeline3d.webgl_qc import (
    ANGLES,
    MAX_SIZE,
    MIN_SIZE,
    PixelDiff,
    RenderReport,
    RenderTarget,
    WebGlQcError,
    diff_report,
    render,
)

EXIT_OK = 0
EXIT_FAILED = 1
# Not 2: argparse exits 2 on a usage error, and a caller branching on the code must never
# read "you mistyped a flag" as "the change rendered nothing".
EXIT_VOID = 3


def _parse_glb(value: str) -> RenderTarget:
    label, _, path = value.partition("=")
    if not label or not path:
        raise argparse.ArgumentTypeError(f"--glb expects LABEL=PATH, got {value!r}")
    try:
        return RenderTarget(label=label, glb=Path(path))
    except WebGlQcError as exc:
        # argparse only turns ArgumentTypeError/TypeError/ValueError into a usage error;
        # anything else escapes as a traceback.
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _parse_size(value: str) -> int:
    try:
        size = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"--size expects an integer, got {value!r}") from exc
    if not MIN_SIZE <= size <= MAX_SIZE:
        raise argparse.ArgumentTypeError(f"--size must be in [{MIN_SIZE}, {MAX_SIZE}], got {size}")
    return size


def _parse_pair(value: str) -> tuple[str, str]:
    base, _, target = value.partition(":")
    if not base or not target:
        raise argparse.ArgumentTypeError(f"--diff expects BASELINE:TARGET, got {value!r}")
    return base, target


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument(
        "--glb",
        type=_parse_glb,
        action="append",
        required=True,
        metavar="LABEL=PATH",
        dest="targets",
        help="repeatable; LABEL names the GLB in filenames, diffs and the report",
    )
    parser.add_argument(
        "--angle",
        action="append",
        default=[],
        choices=sorted(ANGLES),
        help=f"repeatable; default all of {sorted(ANGLES)}",
    )
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument(
        "--size",
        type=_parse_size,
        default=1024,
        help=f"square render size in [{MIN_SIZE}, {MAX_SIZE}], default 1024",
    )
    parser.add_argument(
        "--diff",
        type=_parse_pair,
        action="append",
        default=[],
        metavar="BASELINE:TARGET",
        help="repeatable; compare two labels at every rendered angle",
    )
    parser.add_argument(
        "--three-lib",
        type=Path,
        default=None,
        help="override the vendored three tree (default: the theme's, resolved fail-closed)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace PNGs already in --out-dir (default: refuse, so stale and fresh renders never mix)",
    )
    parser.add_argument("--report", type=Path, default=None, help="write the full JSON report")
    return parser


def _print_summary(report: RenderReport, diffs: list[PixelDiff]) -> None:
    for img in report.images:
        anisotropy = {m.get("anisotropy") for m in img.materials}
        print(f"  {img.label:<24} {img.angle:<14} {img.path.name}  anisotropy={anisotropy}")
    for d in diffs:
        flag = "  VOID" if d.is_void else ""
        print(
            f"  {d.baseline_label} -> {d.target_label} @ {d.angle}: "
            f"maxΔ={d.max_abs_delta}/255 changed={d.changed_pixel_pct:.2f}%{flag}"
        )
    if report.console_warnings:
        # Software rendering always emits a few. Console ERRORS never reach here:
        # they fail the render.
        print(f"  console warnings: {len(report.console_warnings)} (software renderer)")


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    angles = tuple(dict.fromkeys(args.angle)) if args.angle else tuple(ANGLES)

    # A typo in --diff should cost nothing, not a full render followed by a traceback.
    labels = {t.label for t in args.targets}
    unknown = sorted({name for pair in args.diff for name in pair if name not in labels})
    if unknown:
        print(
            f"glb-qc: --diff names unknown label(s) {unknown}; given: {sorted(labels)}",
            file=sys.stderr,
        )
        return EXIT_FAILED

    try:
        report = render(
            args.targets,
            args.out_dir,
            angles=angles,
            size=args.size,
            three_lib=args.three_lib,
            overwrite=args.overwrite,
        )
        diffs = diff_report(report, args.diff, args.out_dir, angles=angles) if args.diff else []
    except WebGlQcError as exc:
        print(f"glb-qc: {exc}", file=sys.stderr)
        return EXIT_FAILED

    payload = {**report.as_dict(), "diffs": [d.as_dict() for d in diffs]}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    _print_summary(report, diffs)

    void = [d for d in diffs if d.is_void]
    if void:
        print(
            f"VOID: {len(void)} comparison(s) byte-identical — the change under test rendered "
            "nothing. This is not a verdict on how it looks.",
            file=sys.stderr,
        )
        return EXIT_VOID
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
