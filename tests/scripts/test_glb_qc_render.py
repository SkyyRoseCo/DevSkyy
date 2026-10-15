"""CLI contract for scripts/glb_qc_render.py — above all, the exit codes.

Exit 3 (VOID) is the contract callers branch on: two byte-identical renders mean the
change under test produced no pixels. If that ever collapses into exit 0, a null render
reads as a passing look-verdict.
"""

from __future__ import annotations

import json
from pathlib import Path

import glb_qc_render as cli
import pytest
from PIL import Image

from skyyrose.elite_studio.pipeline3d.webgl_qc import RenderedImage, RenderReport, WebGlQcError


def _fake_render(colors: dict[str, tuple[int, int, int]]):
    """A stand-in for ``render`` that writes one solid PNG per label."""

    def render(targets, out_dir, *, angles, **_kw):
        out_dir.mkdir(parents=True, exist_ok=True)
        images = []
        for target in targets:
            for angle in angles:
                path = out_dir / f"{target.label}-{angle}.png"
                Image.new("RGB", (8, 8), colors[target.label]).save(path)
                images.append(
                    RenderedImage(
                        label=target.label,
                        angle=angle,
                        path=path,
                        camera={},
                        bbox={},
                        materials=[{"anisotropy": 0}],
                        geometry_attributes=[],
                        webgl="webgl2",
                    )
                )
        return RenderReport(images=tuple(images))

    return render


def _argv(tmp_path: Path, *extra: str) -> list[str]:
    return [
        "--glb",
        f"a={tmp_path / 'a.glb'}",
        "--glb",
        f"b={tmp_path / 'b.glb'}",
        "--angle",
        "front",
        "--out-dir",
        str(tmp_path / "out"),
        *extra,
    ]


def test_exit_codes_are_distinct() -> None:
    assert len({cli.EXIT_OK, cli.EXIT_FAILED, cli.EXIT_VOID}) == 3
    assert (cli.EXIT_OK, cli.EXIT_FAILED) == (0, 1)
    # argparse owns exit 2 (usage error); VOID sharing it would let a mistyped flag read
    # as "the change rendered nothing".
    assert cli.EXIT_VOID not in (0, 1, 2)


def test_differing_renders_exit_ok(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "render", _fake_render({"a": (10, 10, 10), "b": (90, 10, 10)}))
    assert cli.main(_argv(tmp_path, "--diff", "a:b")) == cli.EXIT_OK


def test_identical_renders_exit_void_and_the_report_says_so(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli, "render", _fake_render({"a": (10, 10, 10), "b": (10, 10, 10)}))
    report = tmp_path / "report.json"

    assert cli.main(_argv(tmp_path, "--diff", "a:b", "--report", str(report))) == cli.EXIT_VOID

    assert "not a verdict on how it looks" in capsys.readouterr().err
    diffs = json.loads(report.read_text(encoding="utf-8"))["diffs"]
    assert diffs[0]["void"] is True and diffs[0]["max_abs_delta"] == 0


def test_render_failure_exits_failed_with_a_tagged_message(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def boom(*_a: object, **_kw: object) -> None:
        raise WebGlQcError("a @ front: rendered a blank frame")

    monkeypatch.setattr(cli, "render", boom)
    assert cli.main(_argv(tmp_path)) == cli.EXIT_FAILED
    assert "glb-qc: a @ front: rendered a blank frame" in capsys.readouterr().err


def test_diff_typo_fails_before_anything_is_rendered(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def must_not_run(*_a: object, **_kw: object) -> None:
        raise AssertionError("rendered despite an unknown --diff label")

    monkeypatch.setattr(cli, "render", must_not_run)
    assert cli.main(_argv(tmp_path, "--diff", "a:bb")) == cli.EXIT_FAILED
    assert "unknown label(s) ['bb']" in capsys.readouterr().err


def test_overwrite_flag_reaches_render(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, object] = {}
    inner = _fake_render({"a": (1, 1, 1), "b": (2, 2, 2)})

    def spy(targets, out_dir, **kw):
        seen.update(kw)
        return inner(targets, out_dir, **kw)

    monkeypatch.setattr(cli, "render", spy)
    cli.main(_argv(tmp_path))
    assert seen["overwrite"] is False
    cli.main(_argv(tmp_path, "--overwrite"))
    assert seen["overwrite"] is True


@pytest.mark.parametrize(
    "argv",
    [
        ["--glb", "a/b=x.glb", "--out-dir", "o"],
        ["--glb", "a=x.glb", "--out-dir", "o", "--size", "99999"],
        ["--glb", "a=x.glb", "--out-dir", "o", "--size", "0"],
        ["--glb", "a=x.glb", "--out-dir", "o", "--angle", "sideways"],
    ],
    ids=["bad-label", "size-too-big", "size-zero", "unknown-angle"],
)
def test_bad_arguments_are_usage_errors_not_tracebacks_and_never_void(
    argv: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    # --size 99999 used to crash the headless shell and hang the process forever.
    with pytest.raises(SystemExit) as exc:
        cli.main(argv)
    assert exc.value.code == 2
    assert exc.value.code != cli.EXIT_VOID
    assert "Traceback" not in capsys.readouterr().err
