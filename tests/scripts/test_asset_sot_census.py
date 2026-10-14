"""Tests for scripts/asset_sot_census.py — tmp_path Git repos, no network."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from scripts import asset_sot_census as census

LEDGERS = (
    census.Ledger("registry", "authority", ("data/registry.json",), ("", "theme")),
    census.Ledger(
        "visual", "authority", ("theme/data/visual.json",), ("theme/assets",), "visual-manifest"
    ),
    census.Ledger("indexes", "projection", ("catalog/**/index.json",), ("@dir",)),
    census.Ledger(census.REVIEW_LEDGER, "review", ("review/inventory.json",)),
)


def _write(root: Path, rel: str, data: bytes | str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str):
        path.write_text(data, encoding="utf-8")
    else:
        path.write_bytes(data)


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init", "-q")
    _write(tmp_path, ".gitignore", "ignored/\n")
    _write(
        tmp_path,
        "data/registry.json",
        json.dumps({"p": {"front": "assets/products/a.png", "logo": "/assets/logo.svg?ver=2"}}),
    )
    _write(
        tmp_path,
        "theme/data/visual.json",
        json.dumps({"hero": {"path": "video/hero", "formats": ["mp4", "480w.webp"]}}),
    )
    _write(tmp_path, "catalog/x/index.json", json.dumps({"assets": [{"path": "orig/x.jpg"}]}))
    _write(tmp_path, "review/inventory.json", json.dumps({"files": [{"path": "misc/r.png"}]}))
    for rel, data in {
        "assets/products/a.png": b"A",
        "theme/assets/logo.svg": b"<svg/>",
        "theme/assets/video/hero.mp4": b"MP4",
        "theme/assets/video/hero-480w.webp": b"W",
        "catalog/x/orig/x.jpg": b"X",
        "misc/r.png": b"R",
        "copies/a-copy.png": b"A",
        "tests/fixtures/f.png": b"F",
        "theme/node_modules/pkg/i.png": b"N",
        "notes/brief.pdf": b"PDF",
        "README.md": "not media",
    }.items():
        _write(tmp_path, rel, data)
    _git(tmp_path, "add", "-A")
    return tmp_path


def _run(repo: Path) -> dict:
    return census.run_census(repo, LEDGERS)


def test_every_reference_kind_resolves(repo: Path) -> None:
    report = _run(repo)
    assert report["orphans"] == []
    assert report["owners"]["assets/products/a.png"] == ["registry"]
    assert report["owners"]["theme/assets/logo.svg"] == ["registry"]
    assert report["owners"]["theme/assets/video/hero-480w.webp"] == ["visual"]
    assert report["owners"]["catalog/x/orig/x.jpg"] == ["indexes"]
    assert report["byte_copies"] == {"copies/a-copy.png": "assets/products/a.png"}
    assert report["totals"]["review_only"] == 1


def test_scope_rules_exclude_with_reason(repo: Path) -> None:
    reasons = _run(repo)["excluded_by_reason"]
    assert reasons == {"dependency": 1, "document": 1, "test-fixture": 1}


def test_untracked_orphan_is_reported(repo: Path) -> None:
    _write(repo, "assets/new-render.png", b"NEW")
    report = _run(repo)
    assert report["orphans"] == [{"path": "assets/new-render.png", "bytes": 3, "tracked": False}]


def test_ignored_media_is_reported_not_gated(repo: Path) -> None:
    _write(repo, "ignored/local.webp", b"I")
    report = _run(repo)
    assert report["orphans"] == []
    assert [row["path"] for row in report["ignored_present"]] == ["ignored/local.webp"]


def test_missing_ledger_fails_closed(repo: Path) -> None:
    (repo / "review/inventory.json").unlink()
    with pytest.raises(census.LedgerError, match="no file matches"):
        _run(repo)


def test_unreadable_ledger_fails_closed(repo: Path) -> None:
    _write(repo, "data/registry.json", "{not json")
    with pytest.raises(census.LedgerError, match="unreadable ledger"):
        _run(repo)


def test_not_a_git_repo_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(census.LedgerError, match="git ls-files failed"):
        census.run_census(tmp_path, LEDGERS)


def test_report_is_deterministic(repo: Path) -> None:
    assert json.dumps(_run(repo)) == json.dumps(_run(repo))


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("./a/b.PNG", "a/b.PNG"),
        ("/wp/x.webp?ver=1#frag", "wp/x.webp"),
        ("https://cdn.example/x.png", None),
        ("../outside.png", None),
        ("notes.txt", None),
        ("multi\nline.png", None),
    ],
)
def test_clean_reference(text: str, expected: str | None) -> None:
    assert census.clean_reference(text) == expected


def test_main_exit_codes(repo: Path, capsys: pytest.CaptureFixture) -> None:
    assert census.main(["--check", "--root", str(repo)], LEDGERS) == 0
    assert "PASS" in capsys.readouterr().out

    assert census.main(["--report", "--root", str(repo)], LEDGERS) == 0
    assert json.loads(capsys.readouterr().out)["totals"]["orphans"] == 0

    _write(repo, "assets/stray.glb", b"GLB")
    assert census.main(["--check", "--root", str(repo)], LEDGERS) == 1
    assert "assets/stray.glb" in capsys.readouterr().err

    (repo / "data/registry.json").unlink()
    assert census.main(["--check", "--root", str(repo)], LEDGERS) == 2


def test_missing_tracked_asset_fails_check(repo: Path, capsys: pytest.CaptureFixture) -> None:
    (repo / "misc/r.png").unlink()
    assert census.main(["--check", "--root", str(repo)], LEDGERS) == 1
    assert "absent on disk" in capsys.readouterr().err
