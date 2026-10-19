"""Production-parity GLB QC renderer: parity gate, fail-closed setup, pixel diff.

The parity test is the load-bearing one. ``VIEWER_PARITY`` is a hand-mirror of
``product-3d-viewer.js`` (an IIFE that cannot export), so nothing but this test stops
the production viewer from being retuned while the QC tool keeps rendering — and
silently measuring — a viewer that no longer exists.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from skyyrose.core.paths import REPO_ROOT
from skyyrose.elite_studio.pipeline3d.webgl_qc import (
    _HARNESS_TEMPLATE,
    ANGLES,
    PDP_INITIAL_HEIGHT_FRACTION,
    THREE_LIB_DIR_NAME,
    VIEWER_PARITY,
    PixelDiff,
    RenderedImage,
    RenderFailedError,
    RenderReport,
    RenderTarget,
    ThreeLibNotFoundError,
    WebGlQcError,
    _assert_not_blank,
    _render_one,
    _serve,
    build_serve_root,
    diff_images,
    diff_report,
    prepare_out_dir,
    render,
    resolve_three_lib,
)
from tests.elite_studio.pipeline3d.glb_fixture import build_triangle_glb, pack_glb

PRODUCTION_VIEWER = REPO_ROOT / "wordpress-theme/skyyrose-flagship/assets/js/product-3d-viewer.js"

# Each entry: parity key -> pattern whose first group is the production value.
_PARITY_PATTERNS = {
    "fov": r"new THREE\.PerspectiveCamera\(\s*(\d+)",
    "outputColorSpace": r"renderer\.outputColorSpace\s*=\s*THREE\.(\w+)",
    "toneMapping": r"renderer\.toneMapping\s*=\s*THREE\.(\w+)",
    "toneMappingExposure": r"renderer\.toneMappingExposure\s*=\s*([\d.]+)",
    "environmentSigma": r"pmrem\.fromScene\(\s*room\s*,\s*([\d.]+)\s*\)",
    # Anchored on the whole two-axis formula, so a switch to height-only fitting fails
    # this gate even if the margin itself is unchanged.
    "fitMargin": (
        r"Math\.max\(\s*framing\.height\s*/\s*half\s*,\s*"
        r"framing\.width\s*/\s*half\s*/\s*camera\.aspect\s*\)\s*\*\s*([\d.]+)"
    ),
}


def _viewer_code() -> str:
    """The production viewer with comments removed.

    A stale ``// was: renderer.toneMapping = THREE.Neutral…`` left above the real line
    would otherwise satisfy the gate while production had drifted.
    """
    source = PRODUCTION_VIEWER.read_text(encoding="utf-8")
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    return re.sub(r"(?m)^\s*//.*$", "", source)


def _fake_three_lib(root: Path) -> Path:
    """A structurally complete stand-in for the theme's vendored tree."""
    lib = root / THREE_LIB_DIR_NAME
    (lib / "basis").mkdir(parents=True)
    for name in (
        "three.module.min.js",
        "GLTFLoader.js",
        "KTX2Loader.js",
        "RoomEnvironment.js",
        "meshopt_decoder.module.js",
    ):
        (lib / name).write_text("// stub\n", encoding="utf-8")
    (lib / "basis/basis_transcoder.js").write_text("// stub\n", encoding="utf-8")
    return lib


def _png(path: Path, color: tuple[int, int, int], size: int = 8) -> Path:
    from PIL import Image

    Image.new("RGB", (size, size), color).save(path)
    return path


def _report(tmp_path: Path, labels: tuple[str, ...], angle: str = "front") -> RenderReport:
    images = []
    for i, label in enumerate(labels):
        png = _png(tmp_path / f"{label}-{angle}.png", (10 + i * 40, 10, 10))
        images.append(
            RenderedImage(
                label=label,
                angle=angle,
                path=png,
                camera={},
                bbox={},
                materials=[],
                geometry_attributes=[],
                webgl="webgl2",
            )
        )
    return RenderReport(images=tuple(images))


class TestProductionParity:
    def test_production_viewer_exists(self) -> None:
        # Fails closed: if the viewer moves, the parity gate must break loudly rather
        # than quietly stop checking anything.
        assert PRODUCTION_VIEWER.is_file(), f"production viewer not at {PRODUCTION_VIEWER}"

    @pytest.mark.parametrize("key", sorted(_PARITY_PATTERNS))
    def test_parity_matches_production_viewer(self, key: str) -> None:
        matches = re.findall(_PARITY_PATTERNS[key], _viewer_code())
        assert len(matches) <= 1, (
            f"{key} appears {len(matches)} times in {PRODUCTION_VIEWER.name}; the gate cannot "
            "tell which one ships. Tighten the pattern."
        )
        match = matches[0] if matches else None
        assert match, (
            f"could not find {key} in {PRODUCTION_VIEWER.name} using "
            f"{_PARITY_PATTERNS[key]!r}. The viewer changed shape — re-read it and update "
            "both the pattern and VIEWER_PARITY; do not delete this check."
        )
        expected = VIEWER_PARITY[key]
        actual = match if isinstance(expected, str) else float(match)
        expected = expected if isinstance(expected, str) else float(expected)
        assert actual == expected, (
            f"QC renderer parity drift: production viewer has {key}={actual!r}, "
            f"VIEWER_PARITY says {expected!r}. Every render this tool has produced since "
            "the viewer changed was measured against a viewer that no longer ships."
        )

    def test_every_parity_key_is_either_checked_or_harness_only(self) -> None:
        harness_only = {"clearColor", "framesBeforeCapture", "size", "threeLibDirName"}
        assert set(VIEWER_PARITY) == set(_PARITY_PATTERNS) | harness_only

    def test_pdp_initial_angle_matches_the_viewers_opening_shot(self) -> None:
        # applyFit(initial) — what a shopper sees the instant the dialog opens. It is
        # deliberately off the fit sphere, so "front" does not stand in for it.
        source = _viewer_code()
        match = re.search(
            r"camera\.position\.set\(\s*0,\s*framing\.height\s*\*\s*([\d.]+),\s*distance\s*\)",
            source,
        )
        assert match, "could not find applyFit(initial)'s camera placement in the viewer"
        assert float(match.group(1)) == PDP_INITIAL_HEIGHT_FRACTION
        assert ANGLES["pdp-initial"] == {"heightFraction": PDP_INITIAL_HEIGHT_FRACTION}


class TestHarnessTemplate:
    def test_template_ships_with_the_package(self) -> None:
        assert _HARNESS_TEMPLATE.is_file()

    def test_template_renders_nothing_without_injection(self) -> None:
        # The un-injected template must not silently fall back to defaults.
        text = _HARNESS_TEMPLATE.read_text(encoding="utf-8")
        assert "/*__PARITY__*/ null" in text
        assert "/*__ANGLES__*/ null" in text
        assert "refusing to render" in text

    def test_build_serve_root_injects_parity_and_angles(self, tmp_path: Path) -> None:
        lib = _fake_three_lib(tmp_path / "lib")
        glb = tmp_path / "src.glb"
        glb.write_bytes(b"glTF-stub")
        serve = build_serve_root(
            [RenderTarget("base", glb)], tmp_path / "serve", three_lib=lib, size=512
        )

        html = (serve / "harness.html").read_text(encoding="utf-8")
        assert "/*__PARITY__*/" not in html
        assert json.dumps(VIEWER_PARITY["toneMapping"]) in html
        assert '"size": 512' in html
        assert json.dumps({k: dict(v) for k, v in ANGLES.items()}) in html
        assert (serve / THREE_LIB_DIR_NAME).is_symlink()
        assert (serve / "base.glb").resolve() == glb.resolve()

    def test_reused_serve_root_repoints_the_three_link(self, tmp_path: Path) -> None:
        glb = tmp_path / "src.glb"
        glb.write_bytes(b"glTF-stub")
        first, second = _fake_three_lib(tmp_path / "one"), _fake_three_lib(tmp_path / "two")
        serve = tmp_path / "serve"
        build_serve_root([RenderTarget("base", glb)], serve, three_lib=first)
        build_serve_root([RenderTarget("base", glb)], serve, three_lib=second)
        assert (serve / THREE_LIB_DIR_NAME).resolve() == second.resolve()

    def test_build_serve_root_fails_closed_on_missing_glb(self, tmp_path: Path) -> None:
        lib = _fake_three_lib(tmp_path / "lib")
        with pytest.raises(WebGlQcError, match="GLB not found"):
            build_serve_root(
                [RenderTarget("base", tmp_path / "nope.glb")],
                tmp_path / "serve",
                three_lib=lib,
            )

    def test_build_serve_root_fails_closed_when_sentinels_are_gone(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        stripped = tmp_path / "stripped.html"
        stripped.write_text("<html>no sentinels here</html>", encoding="utf-8")
        monkeypatch.setattr("skyyrose.elite_studio.pipeline3d.webgl_qc._HARNESS_TEMPLATE", stripped)
        lib = _fake_three_lib(tmp_path / "lib")
        glb = tmp_path / "src.glb"
        glb.write_bytes(b"glTF-stub")
        with pytest.raises(WebGlQcError, match="injection sentinels"):
            build_serve_root([RenderTarget("base", glb)], tmp_path / "serve", three_lib=lib)


class TestThreeLibResolution:
    def test_missing_directory_raises(self, tmp_path: Path) -> None:
        with pytest.raises(ThreeLibNotFoundError, match="not found"):
            resolve_three_lib(tmp_path / "absent")

    def test_incomplete_tree_names_what_is_missing(self, tmp_path: Path) -> None:
        lib = _fake_three_lib(tmp_path / "lib")
        (lib / "KTX2Loader.js").unlink()
        with pytest.raises(ThreeLibNotFoundError, match="KTX2Loader.js"):
            resolve_three_lib(lib)

    def test_theme_tree_resolves(self) -> None:
        # The default is the theme's sha256-pinned tree; the tool must never copy it.
        assert resolve_three_lib().name == THREE_LIB_DIR_NAME


class TestRenderTarget:
    @pytest.mark.parametrize(
        "label",
        ["", "has/slash", " padded ", "a&x", "a#x", "a%2Fx", "a?x", "a b", "..", "-lead", "x" * 65],
    )
    def test_rejects_labels_that_would_break_paths_or_urls(self, label: str) -> None:
        with pytest.raises(WebGlQcError, match="invalid render label"):
            RenderTarget(label, Path("x.glb"))


class TestPixelDiff:
    def test_identical_images_compare_to_zero(self, tmp_path: Path) -> None:
        a = _png(tmp_path / "a.png", (120, 40, 40))
        max_abs, pct = diff_images(a, a, tmp_path / "d.png")
        assert (max_abs, pct) == (0, 0.0)

    def test_difference_is_measured_and_a_map_is_written(self, tmp_path: Path) -> None:
        a = _png(tmp_path / "a.png", (120, 40, 40))
        b = _png(tmp_path / "b.png", (140, 40, 40))
        diff_map = tmp_path / "d.png"
        max_abs, pct = diff_images(a, b, diff_map)
        assert max_abs == 20
        assert pct == 100.0
        assert diff_map.is_file()

    def test_shape_mismatch_raises_rather_than_comparing_crops(self, tmp_path: Path) -> None:
        a = _png(tmp_path / "a.png", (10, 10, 10), size=8)
        b = _png(tmp_path / "b.png", (10, 10, 10), size=16)
        with pytest.raises(WebGlQcError, match="different shapes"):
            diff_images(a, b, tmp_path / "d.png")

    def test_void_is_distinct_from_no_visible_difference(self, tmp_path: Path) -> None:
        void = PixelDiff("a", "b", "front", 0, 0.0, tmp_path / "d.png")
        faint = PixelDiff("a", "b", "front", 2, 0.01, tmp_path / "d.png")
        assert void.is_void and void.as_dict()["void"] is True
        assert not faint.is_void


class TestDiffReport:
    def test_diffs_every_requested_pair(self, tmp_path: Path) -> None:
        report = _report(tmp_path, ("base", "candidate"))
        diffs = diff_report(report, [("base", "candidate")], tmp_path)
        assert len(diffs) == 1
        assert diffs[0].max_abs_delta == 40
        assert diffs[0].diff_map.is_file()

    def test_flags_void_when_a_variant_rendered_nothing(self, tmp_path: Path) -> None:
        report = _report(tmp_path, ("base", "candidate"))
        # Same pixels: the change under test produced no render difference at all.
        _png(tmp_path / "candidate-front.png", (10, 10, 10))
        diffs = diff_report(report, [("base", "candidate")], tmp_path)
        assert diffs[0].is_void

    def test_self_check_rejects_a_measurement_that_cannot_see_a_change(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # A diff that answers 0 for everything would surface as VOID on every pair.
        import numpy as np

        report = _report(tmp_path, ("base", "candidate"))
        monkeypatch.setattr(
            "skyyrose.elite_studio.pipeline3d.webgl_qc._measure",
            lambda a, b: (0, 0.0, np.zeros_like(a)),
        )
        with pytest.raises(WebGlQcError, match="cannot discriminate"):
            diff_report(report, [("base", "candidate")], tmp_path)

    def test_self_check_rejects_an_image_unequal_to_itself(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import numpy as np

        report = _report(tmp_path, ("base", "candidate"))
        monkeypatch.setattr(
            "skyyrose.elite_studio.pipeline3d.webgl_qc._measure",
            lambda a, b: (1, 0.0, np.zeros_like(a)),
        )
        with pytest.raises(WebGlQcError, match="does not compare equal to itself"):
            diff_report(report, [("base", "candidate")], tmp_path)

    def test_self_check_leaves_no_file_behind(self, tmp_path: Path) -> None:
        report = _report(tmp_path, ("base", "candidate"))
        before = {p.name for p in tmp_path.iterdir()}
        diff_report(report, [("base", "candidate")], tmp_path)
        assert {p.name for p in tmp_path.iterdir()} - before == {"base--candidate-front-diff.png"}

    def test_unknown_label_is_a_qc_error_not_a_keyerror(self, tmp_path: Path) -> None:
        report = _report(tmp_path, ("base", "candidate"))
        with pytest.raises(WebGlQcError, match="unknown label"):
            diff_report(report, [("base", "candidat")], tmp_path)

    def test_refuses_to_diff_a_label_against_itself(self, tmp_path: Path) -> None:
        report = _report(tmp_path, ("base", "candidate"))
        with pytest.raises(WebGlQcError, match="against itself"):
            diff_report(report, [("base", "base")], tmp_path)

    def test_requires_at_least_one_pair(self, tmp_path: Path) -> None:
        report = _report(tmp_path, ("base", "candidate"))
        with pytest.raises(WebGlQcError, match="no diff pairs"):
            diff_report(report, [], tmp_path)

    def test_missing_angle_is_an_error_not_a_silent_skip(self, tmp_path: Path) -> None:
        report = _report(tmp_path, ("base", "candidate"))
        with pytest.raises(WebGlQcError, match="cannot diff at 'raking'"):
            diff_report(report, [("base", "candidate")], tmp_path, angles=["raking"])


class TestLoopbackServer:
    def test_binds_loopback_and_cannot_reach_outside_the_serve_root(self, tmp_path: Path) -> None:
        import socket

        serve = tmp_path / "serve"
        serve.mkdir()
        (serve / "harness.html").write_text("harness", encoding="utf-8")
        (tmp_path / "secret.env").write_text("TOKEN=do-not-serve", encoding="utf-8")

        server, port = _serve(serve)
        try:
            assert server.server_address[0] == "127.0.0.1"

            def get(path: str) -> bytes:
                # Raw socket: an HTTP client would normalise "/../" away before sending.
                with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
                    sock.sendall(f"GET {path} HTTP/1.0\r\n\r\n".encode())
                    chunks = []
                    while chunk := sock.recv(4096):
                        chunks.append(chunk)
                return b"".join(chunks)

            assert b"200 OK" in get("/harness.html")
            attacks = (
                "/../secret.env",
                "/%2e%2e/secret.env",
                "//" + str(tmp_path / "secret.env"),
            )
            for attack in attacks:
                response = get(attack)
                assert b"do-not-serve" not in response, attack
                assert b"200 OK" not in response.split(b"\r\n", 1)[0], attack
        finally:
            server.shutdown()
            server.server_close()


class TestRenderPreconditions:
    """Every one of these must fail BEFORE a browser is launched."""

    @pytest.fixture(autouse=True)
    def _no_browser(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def boom(*_a: object, **_kw: object) -> None:
            raise AssertionError("a browser was launched for an input that should fail first")

        monkeypatch.setattr("playwright.sync_api.sync_playwright", boom)

    @pytest.fixture
    def glb(self, tmp_path: Path) -> Path:
        path = tmp_path / "tri.glb"
        path.write_bytes(build_triangle_glb())
        return path

    def test_no_targets(self, tmp_path: Path) -> None:
        with pytest.raises(WebGlQcError, match="no render targets"):
            render([], tmp_path / "out")

    def test_empty_angles_is_not_a_successful_empty_report(self, tmp_path: Path, glb: Path) -> None:
        with pytest.raises(WebGlQcError, match="no angles"):
            render([RenderTarget("a", glb)], tmp_path / "out", angles=[])

    def test_unknown_angle(self, tmp_path: Path, glb: Path) -> None:
        with pytest.raises(WebGlQcError, match="unknown angle"):
            render([RenderTarget("a", glb)], tmp_path / "out", angles=["nope"])

    def test_duplicate_labels(self, tmp_path: Path, glb: Path) -> None:
        with pytest.raises(WebGlQcError, match="duplicate render labels"):
            render([RenderTarget("a", glb), RenderTarget("a", glb)], tmp_path / "out")

    def test_missing_glb(self, tmp_path: Path) -> None:
        with pytest.raises(WebGlQcError, match="GLB not found"):
            render([RenderTarget("a", tmp_path / "absent.glb")], tmp_path / "out")

    def test_truncated_glb_is_rejected_by_the_container_parser(
        self, tmp_path: Path, glb: Path
    ) -> None:
        bad = tmp_path / "bad.glb"
        bad.write_bytes(glb.read_bytes()[:-8])
        with pytest.raises(WebGlQcError, match="not a valid GLB"):
            render([RenderTarget("a", bad)], tmp_path / "out")

    def test_stale_pngs_in_out_dir_are_refused(self, tmp_path: Path, glb: Path) -> None:
        out = tmp_path / "out"
        out.mkdir()
        _png(out / "a-front.png", (1, 2, 3))
        with pytest.raises(WebGlQcError, match="already holds 1 PNG"):
            render([RenderTarget("a", glb)], out)


class TestPrepareOutDir:
    def test_overwrite_removes_only_pngs(self, tmp_path: Path) -> None:
        _png(tmp_path / "old.png", (1, 2, 3))
        (tmp_path / "notes.txt").write_text("keep me", encoding="utf-8")
        prepare_out_dir(tmp_path, overwrite=True)
        assert sorted(p.name for p in tmp_path.iterdir()) == ["notes.txt"]


def _frame_bytes(tmp_path: Path, *, two_tone: bool) -> bytes:
    from PIL import Image

    img = Image.new("RGB", (8, 8), (128, 128, 128))
    if two_tone:
        img.putpixel((3, 3), (10, 10, 10))
    path = tmp_path / "frame.png"
    img.save(path)
    return path.read_bytes()


class TestBlankFrameGuard:
    def test_uniform_frame_is_a_failed_render(self, tmp_path: Path) -> None:
        with pytest.raises(RenderFailedError, match="blank frame"):
            _assert_not_blank(_frame_bytes(tmp_path, two_tone=False), "a @ front")

    def test_a_frame_with_any_content_passes(self, tmp_path: Path) -> None:
        _assert_not_blank(_frame_bytes(tmp_path, two_tone=True), "a @ front")


class _FakePage:
    def __init__(self, captured: dict, console: list[tuple[str, str]]) -> None:
        self._captured = captured
        self._console = console
        self._handlers: dict = {}

    def on(self, event: str, handler: object) -> None:
        self._handlers[event] = handler

    def goto(self, *_a: object, **_kw: object) -> None:
        for kind, text in self._console:
            self._handlers["console"](type("Msg", (), {"type": kind, "text": text})())

    def wait_for_function(self, *_a: object, **_kw: object) -> None:
        if self._captured.get("timeout"):
            raise TimeoutError("Timeout 1ms exceeded")

    def evaluate(self, *_a: object) -> dict:
        return self._captured

    def close(self) -> None:
        pass


class TestRenderOne:
    """The per-frame fail-closed rules, without a browser."""

    def _run(self, tmp_path: Path, captured: dict, console: list | None = None) -> tuple:
        page = _FakePage(captured, console or [])
        context = type("Ctx", (), {"new_page": lambda self: page})()
        return _render_one(context, 1, RenderTarget("a", tmp_path / "a.glb"), "front", 64, 1)

    def _good(self, tmp_path: Path) -> dict:
        import base64

        png = _frame_bytes(tmp_path, two_tone=True)
        return {
            "result": {"ok": True, "glb": "a.glb"},
            "dataUrl": "data:image/png;base64," + base64.b64encode(png).decode(),
            "errors": [],
        }

    def test_clean_frame_is_returned_with_its_warnings(self, tmp_path: Path) -> None:
        result, png, messages = self._run(
            tmp_path, self._good(tmp_path), [("warning", "GPU stall")]
        )
        assert result["ok"] and png.startswith(b"\x89PNG")
        assert [m["type"] for m in messages] == ["warning"]

    def test_ok_false_raises(self, tmp_path: Path) -> None:
        bad = {
            "result": {"ok": False, "error": "no renderable geometry"},
            "dataUrl": None,
            "errors": [],
        }
        with pytest.raises(RenderFailedError, match="no renderable geometry"):
            self._run(tmp_path, bad)

    def test_console_error_fails_the_render_even_when_ok_is_true(self, tmp_path: Path) -> None:
        # three reports shader link failures via console.error and keeps going.
        with pytest.raises(RenderFailedError, match="VALIDATE_STATUS"):
            self._run(
                tmp_path,
                self._good(tmp_path),
                [("error", "THREE.WebGLProgram: Shader Error VALIDATE_STATUS false")],
            )

    def test_window_error_fails_the_render(self, tmp_path: Path) -> None:
        with pytest.raises(RenderFailedError, match="boom"):
            self._run(tmp_path, {**self._good(tmp_path), "errors": ["boom"]})

    def test_blank_frame_fails_the_render(self, tmp_path: Path) -> None:
        import base64

        blank = base64.b64encode(_frame_bytes(tmp_path, two_tone=False)).decode()
        captured = {**self._good(tmp_path), "dataUrl": "data:image/png;base64," + blank}
        with pytest.raises(RenderFailedError, match="blank frame"):
            self._run(tmp_path, captured)

    def test_timeout_names_the_target(self, tmp_path: Path) -> None:
        with pytest.raises(RenderFailedError, match="a @ front: browser did not produce"):
            self._run(tmp_path, {"timeout": True})


@pytest.mark.integration
@pytest.mark.timeout(180)
class TestRealBrowser:
    """Executes the harness JS. Deselected by the default addopts; when selected, a
    missing Chromium is a FAILURE, never a skip (bug-230)."""

    def test_same_glb_renders_byte_identical_and_empty_scene_fails(self, tmp_path: Path) -> None:
        glb = tmp_path / "tri.glb"
        glb.write_bytes(build_triangle_glb())
        report = render(
            [RenderTarget("a", glb), RenderTarget("b", glb)],
            tmp_path / "out",
            angles=["front"],
            size=64,
        )
        a, b = report.image("a", "front").path, report.image("b", "front").path
        assert a.read_bytes() == b.read_bytes(), "two renders of one GLB must be byte-identical"
        assert report.image("a", "front").camera["fov"] == VIEWER_PARITY["fov"]

        empty = tmp_path / "empty.glb"
        empty.write_bytes(
            pack_glb({"asset": {"version": "2.0"}, "scene": 0, "scenes": [{"nodes": []}]}, None)
        )
        with pytest.raises(RenderFailedError, match="no renderable geometry"):
            render([RenderTarget("e", empty)], tmp_path / "out2", angles=["front"], size=64)


class TestAttackRegressions:
    """Each of these was OBSERVED by a live adversarial run against the first version."""

    @pytest.mark.parametrize("size", [0, 15, 4097, 99999, True, 64.0])
    def test_out_of_range_size_fails_before_a_browser_launches(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, size: object
    ) -> None:
        # size=99999 crashed chrome-headless-shell and the process then hung for 7+ minutes.
        def boom(*_a: object, **_kw: object) -> None:
            raise AssertionError("browser launched for an out-of-range size")

        monkeypatch.setattr("playwright.sync_api.sync_playwright", boom)
        glb = tmp_path / "tri.glb"
        glb.write_bytes(build_triangle_glb())
        with pytest.raises(WebGlQcError, match="size must be an integer"):
            render([RenderTarget("a", glb)], tmp_path / "out", size=size)  # type: ignore[arg-type]

    def test_a_frame_that_loaded_a_different_glb_is_rejected(self, tmp_path: Path) -> None:
        # 'a%41' percent-decoded to 'aA' in the URL, so one label silently rendered
        # another's GLB and the tool reported a confident, wrong VOID.
        captured = {**TestRenderOne()._good(tmp_path)}
        captured["result"] = {"ok": True, "glb": "other.glb"}
        with pytest.raises(RenderFailedError, match="not the requested 'a.glb'"):
            TestRenderOne()._run(tmp_path, captured)

    def test_webgl_context_pointer_is_normalised_out_of_warnings(self, tmp_path: Path) -> None:
        runner = TestRenderOne()
        _, _, messages = runner._run(
            tmp_path,
            runner._good(tmp_path),
            [("warning", "[.WebGL-0x10c0043a800]GL Driver Message: GPU stall")],
        )
        assert messages[0]["text"] == "[.WebGL]GL Driver Message: GPU stall"

    def test_server_refuses_directory_listings(self, tmp_path: Path) -> None:
        import urllib.error
        import urllib.request

        (tmp_path / "harness.html").write_text("x", encoding="utf-8")
        (tmp_path / "sub").mkdir()
        server, port = _serve(tmp_path)
        try:
            for path in ("/", "/sub/"):
                with pytest.raises(urllib.error.HTTPError) as exc:
                    urllib.request.urlopen(
                        f"http://127.0.0.1:{port}{path}", timeout=5
                    )  # noqa: S310
                assert exc.value.code == 404
            with urllib.request.urlopen(  # noqa: S310
                f"http://127.0.0.1:{port}/harness.html", timeout=5
            ) as ok:
                assert ok.status == 200
        finally:
            server.shutdown()
            server.server_close()
