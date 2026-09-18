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
looks. Callers must branch on it (``scripts/glb_qc_render.py`` exits 3).
"""

from __future__ import annotations

import base64
import http.server
import json
import re
import shutil
import socketserver
import tempfile
import threading
from collections.abc import Iterable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

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
    "outputColorSpace": "SRGBColorSpace",
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
#: An oversized viewport crashes chrome-headless-shell, and Playwright then waits on the
#: dead browser forever — a hang, not an error. Bound it before anything launches.
MIN_SIZE, MAX_SIZE = 16, 4096
#: Browser launch must finish inside this, or the run is abandoned.
_BROWSER_STARTUP_TIMEOUT_MS = 60_000
_WEBGL_POINTER_RE = re.compile(r"\[\.WebGL-0x[0-9a-f]+\]")
_LABEL_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")


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
        # The label lands in a filename AND a URL query, so it is held to characters
        # that mean nothing in either: no separators, no URL metacharacters.
        if not _LABEL_RE.fullmatch(self.label):
            raise WebGlQcError(
                f"invalid render label: {self.label!r} (allowed: letters, digits, '.', '_', '-')"
            )


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
        """JSON-serialisable form, as written to ``--report``."""
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
    """Everything one successful ``render`` call produced.

    There is no error field on purpose: a console error, page error, blank frame or
    ``ok: false`` raises ``RenderFailedError`` instead of being recorded, so a report
    in hand means every frame in it rendered cleanly.
    """

    images: Sequence[RenderedImage]
    console_messages: Sequence[Mapping[str, Any]] = field(default_factory=tuple)

    @property
    def console_warnings(self) -> tuple[Mapping[str, Any], ...]:
        """Software rendering always emits a few ("GPU stall due to ReadPixels")."""
        return tuple(m for m in self.console_messages if m.get("type") == "warning")

    def image(self, label: str, angle: str) -> RenderedImage:
        """The frame for ``(label, angle)``; ``KeyError`` when it was not rendered."""
        for img in self.images:
            if img.label == label and img.angle == angle:
                return img
        raise KeyError(f"no render for {label!r} at angle {angle!r}")

    def as_dict(self) -> dict[str, Any]:
        """JSON-serialisable form, as written to ``--report``."""
        return {
            "parity": dict(VIEWER_PARITY),
            "images": [i.as_dict() for i in self.images],
            "console_warnings": [dict(e) for e in self.console_warnings],
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
        """JSON-serialisable form, as written to ``--report``."""
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
    if link.is_symlink() or link.exists():
        link.unlink()
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
            # Containment rests on what is linked into the serve root; refusing listings
            # means a future over-broad link is not also browsable.
            "list_directory": lambda self, path: self.send_error(404, "no listing"),
        },
    )
    server = _LoopbackServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, server.server_address[1]


def _capture(page: Any, url: str, timeout_ms: int) -> dict[str, Any]:
    page.goto(url, wait_until="load")
    # Loose inequality on purpose: `undefined !== null` is TRUE, so the strict form could
    # return before the harness had assigned anything and evaluate() then read a null.
    page.wait_for_function("window.__result != null", timeout=timeout_ms)
    return page.evaluate(
        "() => { const r = window.__result || { ok: false, error: 'harness produced no result' };"
        " return { result: { ...r, dataUrl: undefined }, dataUrl: r.dataUrl || null,"
        " errors: window.__errors || [] }; }"
    )


def prepare_out_dir(out_dir: Path, *, overwrite: bool) -> None:
    """Refuse to mix this run's images with a previous run's.

    A folder holding last run's PNGs next to this run's is how someone ends up judging
    a material change from pixels rendered before the change. Without ``overwrite`` an
    ``out_dir`` that already holds PNGs is an error; with it, exactly those PNGs are
    removed first — nothing else in the directory is touched.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    stale = sorted(out_dir.glob("*.png"))
    if not stale:
        return
    if not overwrite:
        raise WebGlQcError(
            f"{out_dir} already holds {len(stale)} PNG(s) from an earlier run; pass "
            "overwrite (CLI: --overwrite) to replace them, or use a fresh directory"
        )
    for png in stale:
        png.unlink()


def _assert_not_blank(png_bytes: bytes, where: str) -> None:
    """A frame of one uniform colour means the mesh drew nothing.

    The harness only rejects an EMPTY bounding box. Geometry that is present but
    invisible — a material that broke to fully transparent, a shader that failed to
    link — still reports ok, and would otherwise be written out as a successful render.
    """
    try:
        import io

        from PIL import Image
    except ImportError as exc:  # pragma: no cover - environment failure
        raise WebGlQcError("Pillow is required to validate rendered frames") from exc
    with Image.open(io.BytesIO(png_bytes)) as img:
        lo_hi = img.convert("RGB").getextrema()
    if all(lo == hi for lo, hi in lo_hi):
        raise RenderFailedError(
            f"{where}: rendered a blank frame (every pixel is {tuple(lo for lo, _ in lo_hi)}) — "
            "the geometry loaded but nothing was drawn"
        )


def _validate_capture(
    captured: dict[str, Any],
    messages: Sequence[Mapping[str, Any]],
    page_errors: Sequence[str],
    requested: str,
    where: str,
) -> tuple[dict[str, Any], bytes]:
    """Every reason a frame that came back is still not a usable render."""
    result = captured["result"]
    if not result.get("ok") or not captured["dataUrl"]:
        raise RenderFailedError(f"{where}: {result.get('error')}")
    # The label allow-list already makes this unreachable; it stays because the failure
    # it guards is a confidently WRONG verdict (one label rendering another's GLB), and
    # that is worth one comparison per frame.
    if result.get("glb") != requested:
        raise RenderFailedError(
            f"{where}: harness loaded {result.get('glb')!r}, not the requested {requested!r}"
        )
    errors = [m["text"] for m in messages if m["type"] == "error"]
    errors += page_errors + [str(e) for e in captured["errors"]]
    if errors:
        raise RenderFailedError(f"{where}: page reported error(s): {errors}")
    png_bytes = base64.b64decode(captured["dataUrl"][len(_PNG_PREFIX) :])
    _assert_not_blank(png_bytes, where)
    return result, png_bytes


def _render_one(
    context: Any, port: int, target: RenderTarget, angle: str, size: int, timeout_ms: int
) -> tuple[dict[str, Any], bytes, list[dict[str, Any]]]:
    """Render one ``(target, angle)``; raise on ANY error signal from the page.

    three.js reports shader compile/link failures through console.error without
    throwing and simply skips the mesh, so a console error is a failed render here,
    not a footnote. Warnings are returned for the report.
    """
    where = f"{target.label} @ {angle}"
    messages: list[dict[str, Any]] = []
    page_errors: list[str] = []
    page = context.new_page()
    page.on(
        "console",
        lambda msg: (
            messages.append(
                {
                    "label": target.label,
                    "angle": angle,
                    "type": msg.type,
                    # The context pointer differs per process; without this two reports
                    # of byte-identical renders never diff clean.
                    "text": _WEBGL_POINTER_RE.sub("[.WebGL]", msg.text),
                }
            )
            if msg.type in ("error", "warning")
            else None
        ),
    )
    page.on("pageerror", lambda err: page_errors.append(str(err)))
    page.on("crash", lambda *_: page_errors.append("the browser page crashed"))
    requested = f"{target.label}.glb"
    url = f"http://127.0.0.1:{port}/harness.html?" + urlencode(
        {"glb": requested, "angle": angle, "size": size}
    )
    try:
        captured = _capture(page, url, timeout_ms)
    except Exception as exc:  # playwright TimeoutError / Error: name the target, fail closed
        raise RenderFailedError(f"{where}: browser did not produce a result: {exc}") from exc
    finally:
        page.close()

    result, png_bytes = _validate_capture(captured, messages, page_errors, requested, where)
    return result, png_bytes, messages


def _check_inputs(
    targets: Sequence[RenderTarget], angles: Sequence[str], size: int
) -> tuple[str, ...]:
    if isinstance(size, bool) or not isinstance(size, int) or not MIN_SIZE <= size <= MAX_SIZE:
        raise WebGlQcError(f"size must be an integer in [{MIN_SIZE}, {MAX_SIZE}], got {size!r}")
    if not targets:
        raise WebGlQcError("no render targets given")
    unique = tuple(dict.fromkeys(angles))
    if not unique:
        raise WebGlQcError("no angles given")
    unknown = [a for a in unique if a not in ANGLES]
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
    return unique


@contextmanager
def _loopback(serve_root: Path) -> Iterator[int]:
    """Serve ``serve_root`` on an ephemeral loopback port for the life of the block."""
    server, port = _serve(serve_root)
    try:
        yield port
    finally:
        server.shutdown()
        server.server_close()


@contextmanager
def _chromium(pw: Any) -> Iterator[Any]:
    """A headless Chromium that is always closed, and whose launch cannot hang."""
    try:
        browser = pw.chromium.launch(
            headless=True, args=list(_CHROMIUM_ARGS), timeout=_BROWSER_STARTUP_TIMEOUT_MS
        )
    except Exception as exc:
        raise WebGlQcError(
            f"could not launch Chromium (playwright install chromium?): {exc}"
        ) from exc
    try:
        yield browser
    finally:
        browser.close()


_Frame = tuple[RenderTarget, str, dict[str, Any], bytes]


def _render_frames(
    targets: Sequence[RenderTarget],
    angles: Sequence[str],
    serve_root: Path,
    size: int,
    timeout_ms: int,
) -> tuple[list[_Frame], list[dict[str, Any]]]:
    """Drive the browser over every ``(target, angle)``; nothing is written to disk."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - environment failure
        raise WebGlQcError(
            "playwright is not installed; the QC render cannot run (pip install playwright "
            "&& playwright install chromium)"
        ) from exc

    frames: list[_Frame] = []
    console_messages: list[dict[str, Any]] = []
    with _loopback(serve_root) as port, sync_playwright() as pw, _chromium(pw) as browser:
        context = browser.new_context(
            viewport={"width": size, "height": size}, device_scale_factor=1
        )
        context.set_default_timeout(timeout_ms)
        for target, angle in ((t, a) for t in targets for a in angles):
            result, png_bytes, messages = _render_one(
                context, port, target, angle, size, timeout_ms
            )
            frames.append((target, angle, result, png_bytes))
            console_messages.extend(messages)
    return frames, console_messages


def render(
    targets: Sequence[RenderTarget],
    out_dir: Path,
    *,
    angles: Sequence[str] = tuple(ANGLES),
    size: int = 1024,
    three_lib: Path | None = None,
    timeout_ms: int = 120_000,
    overwrite: bool = False,
) -> RenderReport:
    """Render every ``(target, angle)`` deterministically and write one PNG each.

    Raises rather than returning a partial report: a QC tool that quietly drops a
    failed render invites a verdict drawn from the frames that happened to work. PNGs
    are written only after EVERY render succeeded, for the same reason.
    """
    angles = _check_inputs(targets, angles, size)
    lib = resolve_three_lib(three_lib)
    prepare_out_dir(out_dir, overwrite=overwrite)

    # The serve root is scaffolding, not output: a temp dir keeps symlink clutter out
    # of the directory the founder opens to look at renders.
    serve_root = Path(tempfile.mkdtemp(prefix="glb-qc-serve-"))
    try:
        build_serve_root(targets, serve_root, three_lib=lib, size=size)
        frames, console_messages = _render_frames(targets, angles, serve_root, size, timeout_ms)
    finally:
        shutil.rmtree(serve_root, ignore_errors=True)

    images: list[RenderedImage] = []
    for target, angle, result, png_bytes in frames:
        png = out_dir / f"{target.label}-{angle}.png"
        png.write_bytes(png_bytes)
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
    return RenderReport(images=tuple(images), console_messages=tuple(console_messages))


def _load_rgb(path: Path) -> Any:
    try:
        import numpy as np
        from PIL import Image
    except ImportError as exc:  # pragma: no cover - environment failure
        raise WebGlQcError("numpy and Pillow are required for pixel diffing") from exc
    with Image.open(path) as img:
        return np.asarray(img.convert("RGB"), dtype=np.int16)


def _measure(a: Any, b: Any) -> tuple[int, float, Any]:
    import numpy as np

    if a.shape != b.shape:
        raise WebGlQcError(f"cannot diff different shapes: {a.shape} vs {b.shape}")
    delta = np.abs(a - b)
    return int(delta.max()), float((delta > 1).any(axis=2).mean() * 100.0), delta


def diff_images(baseline: Path, target: Path, diff_map: Path) -> tuple[int, float]:
    """Max absolute per-channel delta and the share of pixels differing by >1/255."""
    import numpy as np
    from PIL import Image

    max_abs, pct, delta = _measure(_load_rgb(baseline), _load_rgb(target))
    diff_map.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.clip(delta * _DIFF_AMPLIFY, 0, 255).astype(np.uint8), "RGB").save(diff_map)
    return max_abs, pct


def _self_check(probe: Path) -> None:
    """Prove the measurement can return both answers before trusting either.

    An image against itself must be 0, and against a copy with ONE channel of ONE pixel
    moved by 2 it must not be. A measurement that says 0 for everything would otherwise
    surface as VOID on every pair — blaming the GLB pipeline for a broken diff.
    """
    a = _load_rgb(probe)
    same, _, _ = _measure(a, a)
    if same != 0:
        raise WebGlQcError("diff self-check failed: an image does not compare equal to itself")
    nudged = a.copy()
    nudged[0, 0, 0] = nudged[0, 0, 0] + 2 if nudged[0, 0, 0] < 128 else nudged[0, 0, 0] - 2
    moved, _, _ = _measure(a, nudged)
    if moved != 2:
        raise WebGlQcError(
            f"diff self-check failed: a known 2-level change measured as {moved} — "
            "the comparison cannot discriminate"
        )


def diff_report(
    report: RenderReport,
    pairs: Iterable[tuple[str, str]],
    out_dir: Path,
    *,
    angles: Sequence[str] | None = None,
) -> list[PixelDiff]:
    """Diff each ``(baseline_label, target_label)`` pair at every rendered angle.

    Runs ``_self_check`` first, and turns every unknown label or missing angle into a
    ``WebGlQcError`` — never a silent skip and never a bare ``KeyError``.
    """
    pair_list = list(pairs)
    if not pair_list:
        raise WebGlQcError("no diff pairs given")
    if not report.images:
        raise WebGlQcError("cannot diff an empty render report")
    wanted = tuple(angles) if angles else tuple(dict.fromkeys(i.angle for i in report.images))
    known = {i.label for i in report.images}
    for baseline_label, target_label in pair_list:
        if baseline_label == target_label:
            raise WebGlQcError(f"cannot diff {baseline_label!r} against itself")
        missing = [name for name in (baseline_label, target_label) if name not in known]
        if missing:
            raise WebGlQcError(f"diff names unknown label(s) {missing}; rendered: {sorted(known)}")

    _self_check(report.images[0].path)

    diffs: list[PixelDiff] = []
    for baseline_label, target_label in pair_list:
        for angle in wanted:
            try:
                base_img = report.image(baseline_label, angle)
                target_img = report.image(target_label, angle)
            except KeyError as exc:
                raise WebGlQcError(f"cannot diff at {angle!r}: {exc.args[0]}") from exc
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
