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

from skyyrose.elite_studio.pipeline3d.glb_container import (
    GlbFormatError,
    read_glb,
    require_embedded_resources,
    write_glb,
)

from skyyrose.core.paths import REPO_ROOT
from skyyrose.elite_studio.pipeline3d.webgl_qc import (
    _HARNESS_TEMPLATE,
    ANGLES,
    PDP_INITIAL_HEIGHT_FRACTION,
    THREE_LIB_DIR_NAME,
    VIEWER_PARITY,
    PixelDiff,
    RenderedImage,
    RenderReport,
    RenderTarget,
    ThreeLibNotFoundError,
    WebGlQcError,
    build_serve_root,
    diff_images,
    diff_report,
    resolve_three_lib,
    render,
    _offline_request_allowed,
    _restrict_requests,
)

PRODUCTION_VIEWER = REPO_ROOT / "wordpress-theme/skyyrose-flagship/assets/js/product-3d-viewer.js"


class TestOfflineBoundary:
    @pytest.mark.parametrize("kind", ["buffers", "images"])
    @pytest.mark.parametrize(
        "uri",
        ["https://example.invalid/a", "a.bin", "../a.png", "data:image/png;base64,AA==", "", None],
    )
    def test_uri_resources_rejected_before_browser(self, tmp_path, kind, uri, monkeypatch):
        path = tmp_path / "external.glb"
        path.write_bytes(write_glb({"asset": {"version": "2.0"}, kind: [{"uri": uri}]}, b""))
        monkeypatch.setattr(
            "skyyrose.elite_studio.pipeline3d.webgl_qc.resolve_three_lib",
            lambda *_: pytest.fail("external GLB passed preflight"),
        )
        with pytest.raises(WebGlQcError, match="embedded resources required"):
            render([RenderTarget("external", path)], tmp_path / "output")
        assert not (tmp_path / "output").exists()

    def test_embedded_resources_allowed(self):
        require_embedded_resources(
            {"buffers": [{"byteLength": 4}], "images": [{"bufferView": 0, "mimeType": "image/png"}]}
        )

    @pytest.mark.parametrize("document", [{"buffers": {}}, {"images": [None]}])
    def test_malformed_resource_arrays_rejected(self, document):
        with pytest.raises(GlbFormatError):
            require_embedded_resources(document)

    @pytest.mark.parametrize(
        "url", ["http://127.0.0.1:8123/harness.html", "blob:http://127.0.0.1:8123/id"]
    )
    def test_exact_loopback_origin_allowed(self, url):
        assert _offline_request_allowed(url, 8123)

    @pytest.mark.parametrize(
        "url",
        [
            "https://example.invalid/a",
            "http://127.0.0.1:8124/a",
            "http://localhost:8123/a",
            "http://user@127.0.0.1:8123/a",
            "http://127.0.0.1:bad/a",
            "file:///tmp/a",
            "blob:https://example.invalid/id",
            "data:text/html,hi",
        ],
    )
    def test_other_origins_denied(self, url):
        assert not _offline_request_allowed(url, 8123)

    def test_route_aborts_external_and_continues_local(self):
        from types import SimpleNamespace

        actions = []

        class Context:
            def route(self, pattern, callback):
                assert pattern == "**/*"
                self.callback = callback

        context = Context()
        blocked = []
        _restrict_requests(context, 8123, blocked)
        for url in ["http://127.0.0.1:8123/asset.glb", "https://example.invalid/a"]:
            context.callback(
                SimpleNamespace(
                    request=SimpleNamespace(url=url),
                    continue_=lambda: actions.append("continue"),
                    abort=lambda reason: actions.append(reason),
                )
            )
        assert actions == ["continue", "blockedbyclient"]
        assert blocked == ["https://example.invalid/a"]


# Each entry: parity key -> pattern whose first group is the production value.
_PARITY_PATTERNS = {
    "fov": r"new THREE\.PerspectiveCamera\(\s*(\d+)",
    "toneMapping": r"renderer\.toneMapping\s*=\s*THREE\.(\w+)",
    "toneMappingExposure": r"renderer\.toneMappingExposure\s*=\s*([\d.]+)",
    "environmentSigma": r"pmrem\.fromScene\(\s*room\s*,\s*([\d.]+)\s*\)",
    "fitMargin": r"framing\.width\s*/\s*half\s*/\s*camera\.aspect\)\s*\*\s*([\d.]+)",
}


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
        source = PRODUCTION_VIEWER.read_text(encoding="utf-8")
        match = re.search(_PARITY_PATTERNS[key], source)
        assert match, (
            f"could not find {key} in {PRODUCTION_VIEWER.name} using "
            f"{_PARITY_PATTERNS[key]!r}. The viewer changed shape — re-read it and update "
            "both the pattern and VIEWER_PARITY; do not delete this check."
        )
        found = match.group(1)
        expected = VIEWER_PARITY[key]
        actual = type(expected)(found) if not isinstance(expected, str) else found
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
        source = PRODUCTION_VIEWER.read_text(encoding="utf-8")
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
        glb.write_bytes(write_glb({"asset": {"version": "2.0"}}, b""))
        serve = build_serve_root(
            [RenderTarget("base", glb)], tmp_path / "serve", three_lib=lib, size=512
        )

        html = (serve / "harness.html").read_text(encoding="utf-8")
        assert "/*__PARITY__*/" not in html
        assert json.dumps(VIEWER_PARITY["toneMapping"]) in html
        assert '"size": 512' in html
        assert json.dumps({k: dict(v) for k, v in ANGLES.items()}) in html
        assert (serve / THREE_LIB_DIR_NAME).is_symlink()
        assert not (serve / "base.glb").is_symlink()
        assert (serve / "base.glb").read_bytes() == glb.read_bytes()

    def test_frozen_payload_cannot_be_swapped_after_preflight(self, tmp_path):
        lib = _fake_three_lib(tmp_path / "lib")
        source = tmp_path / "mutable.glb"
        checked = write_glb({"asset": {"version": "2.0"}}, b"")
        source.write_bytes(checked)
        require_embedded_resources(read_glb(checked).document)
        source.write_bytes(write_glb({"images": [{"uri": "relative.png"}]}, b""))
        serve = build_serve_root(
            [RenderTarget("base", source)],
            tmp_path / "serve",
            three_lib=lib,
            glb_payloads={"base": checked},
        )
        assert (serve / "base.glb").read_bytes() == checked
        assert not (serve / "base.glb").is_symlink()
        require_embedded_resources(read_glb((serve / "base.glb").read_bytes()).document)

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
    @pytest.mark.parametrize("label", ["", "has/slash", " padded "])
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

    def test_refuses_when_the_comparison_cannot_be_shown_to_discriminate(
        self, tmp_path: Path
    ) -> None:
        report = _report(tmp_path, ("only",))
        with pytest.raises(WebGlQcError, match="discriminate"):
            diff_report(report, [("only", "only")], tmp_path)

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
        with pytest.raises(KeyError):
            diff_report(report, [("base", "candidate")], tmp_path, angles=["raking"])
