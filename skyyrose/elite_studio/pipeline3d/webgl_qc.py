"""Deterministic GLB QC renders in the SAME engine the storefront ships.

``scripts/glb_fidelity.py`` already screenshots GLBs, but it renders with
``<model-viewer>`` and scores a render against a hub master. This module answers a
different question — *what does the PDP viewer actually show, and did a change to the
GLB alter it* — so it renders through the theme's own vendored three.js r170 with the
production viewer's constants (``VIEWER_PARITY``). Rendering a material change in a
different engine than the one that will ship it proves nothing about the storefront.

Two renders must differ ONLY because their GLBs differ. Everything in ``VIEWER_PARITY``
and in the harness exists to hold that invariant; ``tests/elite_studio/pipeline3d/
test_webgl_qc.py::test_parity_matches_production_viewer`` fails when the production
viewer drifts from these values, because a QC tool measuring against a viewer that no
longer exists is worse than no QC tool.

Fails closed throughout: a missing three tree, a missing GLB, an un-injected harness,
an absent Playwright or browser binary, and a render that reports ``ok: false`` are all
errors, never a skip. The one result that is neither pass nor fail is VOID — see
``PixelDiff.is_void``: two renders identical to the byte mean the change under test
produced NO pixels, which is a statement about the pipeline, not a verdict on how it
looks. Callers must branch on it (``scripts/glb_qc_render.py`` exits 2).
"""

from __future__ import annotations

import base64
import http.server
import json
import shutil
import socketserver
import tempfile
import threading
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from skyyrose.core.paths import REPO_ROOT

from .glb_container import GlbFormatError, read_glb

_TEMPLATES = Path(__file__).resolve().parent / "templates"
_HARNESS_TEMPLATE = _TEMPLATES / "webgl_qc_harness.html"
_PARITY_SENTINEL = "/*__PARITY__*/ null"
_ANGLES_SENTINEL = "/*__ANGLES__*/ null"

#: The theme owns this tree and pins it by sha256 in VENDOR.md. Resolve it, never copy
#: it — a second copy is an unpinned fork of a pinned vendor tree.
THREE_LIB_DIR_NAME = "three-0.170.0"
DEFAULT_THREE_LIB = (
    REPO_ROOT / "wordpress-theme/skyyrose-flagship/assets/js/lib" / THREE_LIB_DIR_NAME
)
_REQUIRED_LIB_FILES = (
    "three.module.min.js",
    "GLTFLoader.js",
    "KTX2Loader.js",
    "RoomEnvironment.js",
    "meshopt_decoder.module.js",
    "basis/basis_transcoder.js",
)

#: Mirrors wordpress-theme/skyyrose-flagship/assets/js/product-3d-viewer.js. That file is
#: an IIFE and cannot export these, so the test greps both sources and fails on drift.
VIEWER_PARITY: Mapping[str, Any] = {
    "fov": 35,
    "toneMapping": "NeutralToneMapping",
    "toneMappingExposure": 1,
    "environmentSigma": 0.04,
    "fitMargin": 1.35,
    # Harness-only determinism knobs; no production counterpart.
    "clearColor": 0x808080,
    "framesBeforeCapture": 12,
    "size": 1024,
    "threeLibDirName": THREE_LIB_DIR_NAME,
}

#: Spherical camera placements around the bbox-centred model. "raking" is the one that
#: shows directional highlights: a low glancing angle across the panels.
ANGLES: Mapping[str, Mapping[str, float]] = {
    # What a shopper sees the instant the dialog opens. Production's applyFit(initial)
    # is position(0, framing.height * 0.1, distance) — slightly above centre and NOT on
    # the fit sphere — so it gets its own entry rather than being approximated by
    # "front". PDP_INITIAL_HEIGHT_FRACTION is parity-gated by the test suite.
    "pdp-initial": {"heightFraction": 0.1},
    "front": {"azimuthDeg": 0, "elevationDeg": 0},
    "three-quarter": {"azimuthDeg": 35, "elevationDeg": 12},
    "raking": {"azimuthDeg": 70, "elevationDeg": -18},
}
PDP_INITIAL_HEIGHT_FRACTION = ANGLES["pdp-initial"]["heightFraction"]

_CHROMIUM_ARGS = (
    "--use-gl=angle",
    "--use-angle=swiftshader",
    "--enable-unsafe-swiftshader",
    "--ignore-gpu-blocklist",
)
_DIFF_AMPLIFY = 16
_PNG_PREFIX = "data:image/png;base64,"


class WebGlQcError(RuntimeError):
    """A QC render or diff could not be performed."""


class ThreeLibNotFoundError(WebGlQcError):
    """The theme's vendored three.js tree is missing or incomplete."""


class RenderFailedError(WebGlQcError):
    """The harness reported a failure for a specific target."""


@dataclass(frozen=True)
class RenderTarget:
    """One GLB to render. ``label`` names it in outputs and diffs."""

    label: str
    glb: Path

    def __post_init__(self) -> None:
        if not self.label or "/" in self.label or self.label != self.label.strip():
            raise WebGlQcError(f"invalid render label: {self.label!r}")


@dataclass(frozen=True)
class RenderedImage:
    """One captured frame plus the facts the loader (not the file) reported."""

    label: str
    angle: str
    path: Path
    camera: Mapping[str, Any]
    bbox: Mapping[str, Any]
    materials: Sequence[Mapping[str, Any]]
    geometry_attributes: Sequence[str]
    webgl: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "angle": self.angle,
            "path": str(self.path),
            "camera": dict(self.camera),
            "bbox": dict(self.bbox),
            "materials": [dict(m) for m in self.materials],
            "geometry_attributes": list(self.geometry_attributes),
            "webgl": self.webgl,
        }


@dataclass(frozen=True)
class RenderReport:
    """Everything one ``render`` call produced."""

    images: Sequence[RenderedImage]
    console_messages: Sequence[Mapping[str, Any]] = field(default_factory=tuple)
    page_errors: Sequence[Mapping[str, Any]] = field(default_factory=tuple)

    @property
    def console_errors(self) -> tuple[Mapping[str, Any], ...]:
        """Console output that is actually an error.

        Kept separate from warnings on purpose: software rendering always emits a
        few ("GPU stall due to ReadPixels", "KHR_parallel_shader_compile extension
        not supported"), and a count that mixes them in is a number nobody reads.
        """
        return tuple(m for m in self.console_messages if m.get("type") == "error")

    @property
    def console_warnings(self) -> tuple[Mapping[str, Any], ...]:
        return tuple(m for m in self.console_messages if m.get("type") == "warning")

    def image(self, label: str, angle: str) -> RenderedImage:
        for img in self.images:
            if img.label == label and img.angle == angle:
                return img
        raise KeyError(f"no render for {label!r} at angle {angle!r}")

    def as_dict(self) -> dict[str, Any]:
        return {
            "parity": dict(VIEWER_PARITY),
            "images": [i.as_dict() for i in self.images],
            "console_errors": [dict(e) for e in self.console_errors],
            "console_warnings": [dict(e) for e in self.console_warnings],
            "page_errors": [dict(e) for e in self.page_errors],
        }


@dataclass(frozen=True)
class PixelDiff:
    """One baseline-vs-target comparison at a single angle."""

    baseline_label: str
    target_label: str
    angle: str
    max_abs_delta: int
    changed_pixel_pct: float
    diff_map: Path

    @property
    def is_void(self) -> bool:
        """True when the target is byte-identical to its baseline.

        NOT the same as "no visible difference": it means the change under test
        produced no pixels at all, so any aesthetic verdict drawn from these two
        images would be a verdict on a null result.
        """
        return self.max_abs_delta == 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "baseline_label": self.baseline_label,
            "target_label": self.target_label,
            "angle": self.angle,
            "max_abs_delta": self.max_abs_delta,
            "changed_pixel_pct": round(self.changed_pixel_pct, 4),
            "diff_map": str(self.diff_map),
            "void": self.is_void,
        }


def resolve_three_lib(lib_dir: Path | None = None) -> Path:
    """Locate the vendored three tree, failing closed on anything incomplete."""
    candidate = (lib_dir or DEFAULT_THREE_LIB).resolve()
    if not candidate.is_dir():
        raise ThreeLibNotFoundError(f"vendored three tree not found: {candidate}")
    missing = [name for name in _REQUIRED_LIB_FILES if not (candidate / name).is_file()]
    if missing:
        raise ThreeLibNotFoundError(f"vendored three tree {candidate} is missing: {missing}")
    return candidate


def build_serve_root(
    targets: Sequence[RenderTarget],
    serve_root: Path,
    *,
    three_lib: Path,
    angles: Mapping[str, Mapping[str, float]] = ANGLES,
    size: int | None = None,
) -> Path:
    """Materialise the directory the browser is allowed to see.

    Only the harness, a link to the vendored three tree, and a link per GLB. The
    repo root is never served: it holds .env.wordpress and .env.secrets.
    """
    serve_root.mkdir(parents=True, exist_ok=True)
    template = _HARNESS_TEMPLATE.read_text(encoding="utf-8")
    if _PARITY_SENTINEL not in template or _ANGLES_SENTINEL not in template:
        raise WebGlQcError(
            f"{_HARNESS_TEMPLATE} no longer contains the injection sentinels; "
            "refusing to serve a harness that would render with no parity constants"
        )
    parity = dict(VIEWER_PARITY)
    if size is not None:
        parity["size"] = size
    html = template.replace(_PARITY_SENTINEL, json.dumps(parity)).replace(
        _ANGLES_SENTINEL, json.dumps({k: dict(v) for k, v in angles.items()})
    )
    (serve_root / "harness.html").write_text(html, encoding="utf-8")

    link = serve_root / THREE_LIB_DIR_NAME
    if not link.exists():
        link.symlink_to(three_lib, target_is_directory=True)

    for target in targets:
        glb = target.glb.resolve()
        if not glb.is_file():
            raise WebGlQcError(f"GLB not found for {target.label!r}: {glb}")
        dest = serve_root / f"{target.label}.glb"
        if dest.exists() or dest.is_symlink():
            dest.unlink()
        dest.symlink_to(glb)
    return serve_root


class _LoopbackServer(socketserver.TCPServer):
    allow_reuse_address = True


def _serve(root: Path) -> tuple[_LoopbackServer, int]:
    handler = type(
        "_Handler",
        (http.server.SimpleHTTPRequestHandler,),
        {
            "__init__": lambda self, *a, **kw: http.server.SimpleHTTPRequestHandler.__init__(
                self, *a, directory=str(root), **kw
            ),
            "log_message": lambda self, *a: None,
        },
    )
    server = _LoopbackServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, server.server_address[1]


def _capture(page: Any, url: str, timeout_ms: int) -> dict[str, Any]:
    page.goto(url, wait_until="load")
    page.wait_for_function("window.__result !== null", timeout=timeout_ms)
    return page.evaluate(
        "() => ({ result: { ...window.__result, dataUrl: undefined },"
        " dataUrl: window.__result.dataUrl || null, errors: window.__errors })"
    )


def render(
    targets: Sequence[RenderTarget],
    out_dir: Path,
    *,
    angles: Sequence[str] = tuple(ANGLES),
    size: int = 1024,
    three_lib: Path | None = None,
    timeout_ms: int = 120_000,
) -> RenderReport:
    """Render every ``(target, angle)`` deterministically and write one PNG each.

    Raises rather than returning a partial report: a QC tool that quietly drops a
    failed render invites a verdict drawn from the frames that happened to work.
    """
    if not targets:
        raise WebGlQcError("no render targets given")
    unknown = [a for a in angles if a not in ANGLES]
    if unknown:
        raise WebGlQcError(f"unknown angle(s): {unknown}; known: {sorted(ANGLES)}")
    labels = [t.label for t in targets]
    if len(set(labels)) != len(labels):
        raise WebGlQcError(f"duplicate render labels: {labels}")

    # Parse every container before spending a browser launch on it: a truncated or
    # non-glTF file should say so in milliseconds, not as a loader error 30s later.
    for target in targets:
        if not target.glb.is_file():
            raise WebGlQcError(f"GLB not found for {target.label!r}: {target.glb}")
        try:
            read_glb(target.glb.read_bytes())
        except GlbFormatError as exc:
            raise WebGlQcError(f"{target.label!r} is not a valid GLB: {exc}") from exc

    lib = resolve_three_lib(three_lib)
    out_dir.mkdir(parents=True, exist_ok=True)
    # The serve root is scaffolding, not output: a temp dir keeps symlink clutter out
    # of the directory the founder opens to look at renders.
    serve_root = Path(tempfile.mkdtemp(prefix="glb-qc-serve-"))
    build_serve_root(targets, serve_root, three_lib=lib, size=size)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - environment failure
        raise WebGlQcError(
            "playwright is not installed; the QC render cannot run (pip install playwright "
            "&& playwright install chromium)"
        ) from exc

    images: list[RenderedImage] = []
    console_messages: list[dict[str, Any]] = []
    page_errors: list[dict[str, Any]] = []
    server, port = _serve(serve_root)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=list(_CHROMIUM_ARGS))
            context = browser.new_context(
                viewport={"width": size, "height": size}, device_scale_factor=1
            )
            try:
                for target in targets:
                    for angle in angles:
                        page = context.new_page()
                        page.on(
                            "console",
                            lambda msg, t=target, a=angle: (
                                console_messages.append(
                                    {
                                        "label": t.label,
                                        "angle": a,
                                        "type": msg.type,
                                        "text": msg.text,
                                    }
                                )
                                if msg.type in ("error", "warning")
                                else None
                            ),
                        )
                        page.on(
                            "pageerror",
                            lambda err, t=target, a=angle: page_errors.append(
                                {"label": t.label, "angle": a, "error": str(err)}
                            ),
                        )
                        url = (
                            f"http://127.0.0.1:{port}/harness.html"
                            f"?glb={target.label}.glb&angle={angle}&size={size}"
                        )
                        captured = _capture(page, url, timeout_ms)
                        page.close()

                        result = captured["result"]
                        for err in captured["errors"]:
                            page_errors.append(
                                {"label": target.label, "angle": angle, "error": str(err)}
                            )
                        if not result.get("ok") or not captured["dataUrl"]:
                            raise RenderFailedError(
                                f"{target.label} @ {angle}: {result.get('error')}"
                            )
                        png = out_dir / f"{target.label}-{angle}.png"
                        png.write_bytes(base64.b64decode(captured["dataUrl"][len(_PNG_PREFIX) :]))
                        images.append(
                            RenderedImage(
                                label=target.label,
                                angle=angle,
                                path=png,
                                camera=result["camera"],
                                bbox=result["bbox"],
                                materials=result["materials"],
                                geometry_attributes=result["geometryAttributes"],
                                webgl=result["webgl"],
                            )
                        )
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        shutil.rmtree(serve_root, ignore_errors=True)

    return RenderReport(
        images=tuple(images),
        console_messages=tuple(console_messages),
        page_errors=tuple(page_errors),
    )


def _load_rgb(path: Path) -> Any:
    try:
        import numpy as np
        from PIL import Image
    except ImportError as exc:  # pragma: no cover - environment failure
        raise WebGlQcError("numpy and Pillow are required for pixel diffing") from exc
    with Image.open(path) as img:
        return np.asarray(img.convert("RGB"), dtype=np.int16)


def diff_images(baseline: Path, target: Path, diff_map: Path) -> tuple[int, float]:
    """Max absolute per-channel delta and the share of pixels differing by >1/255."""
    import numpy as np
    from PIL import Image

    a, b = _load_rgb(baseline), _load_rgb(target)
    if a.shape != b.shape:
        raise WebGlQcError(f"cannot diff different shapes: {a.shape} vs {b.shape}")
    delta = np.abs(a - b)
    diff_map.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.clip(delta * _DIFF_AMPLIFY, 0, 255).astype(np.uint8), "RGB").save(diff_map)
    return int(delta.max()), float((delta > 1).any(axis=2).mean() * 100.0)


def diff_report(
    report: RenderReport,
    pairs: Iterable[tuple[str, str]],
    out_dir: Path,
    *,
    angles: Sequence[str] | None = None,
) -> list[PixelDiff]:
    """Diff each ``(baseline_label, target_label)`` pair at every rendered angle.

    Before comparing anything, proves the diff itself can distinguish images: a render
    against ITSELF must be 0 and two different labels must not be. If that self-check
    cannot run (fewer than two distinct labels) it raises — an unexercised sanity check
    is not a passed one.
    """
    wanted = tuple(angles) if angles else tuple(dict.fromkeys(i.angle for i in report.images))
    pair_list = list(pairs)
    if not pair_list:
        raise WebGlQcError("no diff pairs given")

    probe = report.images[0]
    identical, _ = diff_images(probe.path, probe.path, out_dir / "_selfcheck.png")
    if identical != 0:
        raise WebGlQcError("diff self-check failed: an image does not compare equal to itself")
    labels = {i.label for i in report.images}
    if len(labels) < 2:
        raise WebGlQcError(
            "diff requires at least two labels so the comparison can be shown to discriminate"
        )
    (out_dir / "_selfcheck.png").unlink(missing_ok=True)

    diffs: list[PixelDiff] = []
    for baseline_label, target_label in pair_list:
        if baseline_label == target_label:
            raise WebGlQcError(f"cannot diff {baseline_label!r} against itself")
        for angle in wanted:
            base_img = report.image(baseline_label, angle)
            target_img = report.image(target_label, angle)
            diff_map = out_dir / f"{baseline_label}--{target_label}-{angle}-diff.png"
            max_abs, pct = diff_images(base_img.path, target_img.path, diff_map)
            diffs.append(
                PixelDiff(
                    baseline_label=baseline_label,
                    target_label=target_label,
                    angle=angle,
                    max_abs_delta=max_abs,
                    changed_pixel_pct=pct,
                    diff_map=diff_map,
                )
            )
    return diffs
