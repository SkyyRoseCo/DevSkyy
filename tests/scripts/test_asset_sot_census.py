"""Tests for scripts/asset_sot_census.py — tmp_path Git repos, no network."""

from __future__ import annotations

import fnmatch
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
        "misc/r.png": b"R",
        "copies/a-copy.png": b"A",
        "tests/fixtures/f.png": b"F",
        "theme/node_modules/pkg/i.png": b"N",
        "notes/brief.pdf": b"PDF",
        "README.md": "not media",
    }.items():
        _write(tmp_path, rel, data)
    # Like assets/products/catalog/**/originals: a link to an authority-owned source.
    (tmp_path / "catalog/x/orig").mkdir(parents=True)
    (tmp_path / "catalog/x/orig/x.jpg").symlink_to("../../../assets/products/a.png")
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
    assert report["byte_copies"] == {
        "catalog/x/orig/x.jpg": "assets/products/a.png",
        "copies/a-copy.png": "assets/products/a.png",
    }
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


def test_projection_reference_alone_does_not_own(repo: Path) -> None:
    """A stale generated view must not keep an asset the authority dropped."""
    _write(repo, "catalog/x/index.json", json.dumps({"assets": [{"path": "orig/stale.jpg"}]}))
    _write(repo, "catalog/x/orig/stale.jpg", b"STALE")
    _git(repo, "add", "-A")
    report = _run(repo)
    assert [row["path"] for row in report["orphans"]] == ["catalog/x/orig/stale.jpg"]
    indexes = next(row for row in report["ledgers"] if row["name"] == "indexes")
    assert indexes["owned_in_scope"] == 1  # still reported for consistency
    assert "indexes" not in report["owned_by_ledger"]


def test_theme_ledger_resolves_paths_relative_to_its_own_folder(repo: Path) -> None:
    (theme_v2,) = [ledger for ledger in census.DEFAULT_LEDGERS if ledger.role == "theme-v2"]
    ledgers = (*LEDGERS, census.Ledger("v2", "theme-v2", ("v2/**/manifest.json",), theme_v2.bases))
    _write(repo, "v2/assets/sot/manifest.json", json.dumps({"file": "br-002/ghost-front.png"}))
    _write(repo, "v2/assets/sot/br-002/ghost-front.png", b"GHOST")
    _git(repo, "add", "-A")
    report = census.run_census(repo, ledgers)
    assert report["owners"]["v2/assets/sot/br-002/ghost-front.png"] == ["v2"]


def test_theme_ledger_prefers_the_manifest_folder_over_broader_bases(repo: Path) -> None:
    """A name that also exists at the theme root must credit the file beside the manifest."""
    (theme_v2,) = [ledger for ledger in census.DEFAULT_LEDGERS if ledger.role == "theme-v2"]
    bases = tuple("v2" if base == census.V2 else base for base in theme_v2.bases)
    ledgers = (*LEDGERS, census.Ledger("v2", "theme-v2", ("v2/**/manifest.json",), bases))
    _write(repo, "v2/assets/sot/manifest.json", json.dumps({"file": "dupe.png"}))
    _write(repo, "v2/assets/sot/dupe.png", b"LOCAL")
    _write(repo, "v2/dupe.png", b"ROOT")
    _git(repo, "add", "-A")
    report = census.run_census(repo, ledgers)
    assert report["owners"].get("v2/assets/sot/dupe.png") == ["v2"]


def _checkout_without_symlinks(repo: Path, rel: str) -> None:
    """Re-check ``rel`` out as a native Windows clone does: a text file holding the target."""
    (repo / rel).unlink()
    _git(repo, "-c", "core.symlinks=false", "checkout", "--", rel)
    assert not (repo / rel).is_symlink()


def test_placeholder_link_is_owned_through_its_target(repo: Path) -> None:
    _checkout_without_symlinks(repo, "catalog/x/orig/x.jpg")
    report = _run(repo)
    assert report["orphans"] == []
    assert report["byte_copies"]["catalog/x/orig/x.jpg"] == "assets/products/a.png"


@pytest.mark.parametrize("placeholder", [False, True])
def test_link_to_an_unowned_file_is_an_orphan(repo: Path, placeholder: bool) -> None:
    _write(repo, "loose/b.png", b"B")
    (repo / "catalog/x/orig/b.jpg").symlink_to("../../../loose/b.png")
    _git(repo, "add", "-A")
    if placeholder:
        _checkout_without_symlinks(repo, "catalog/x/orig/b.jpg")
    orphans = [row["path"] for row in _run(repo)["orphans"]]
    assert orphans == ["catalog/x/orig/b.jpg", "loose/b.png"]


@pytest.mark.parametrize("placeholder", [False, True])
def test_link_to_a_missing_file_is_missing_on_every_platform(repo: Path, placeholder: bool) -> None:
    _write(repo, "loose/gone.png", b"G")
    (repo / "catalog/x/orig/gone.jpg").symlink_to("../../../loose/gone.png")
    _git(repo, "add", "-A")
    _git(repo, "rm", "-q", "--cached", "loose/gone.png")
    (repo / "loose/gone.png").unlink()
    if placeholder:
        _checkout_without_symlinks(repo, "catalog/x/orig/gone.jpg")
    report = _run(repo)
    assert report["tracked_missing_on_disk"] == ["catalog/x/orig/gone.jpg"]
    assert report["orphans"] == []


def test_chained_placeholder_links_resolve_to_the_final_file(repo: Path) -> None:
    (repo / "catalog/x/orig/hop.jpg").symlink_to("x.jpg")
    _git(repo, "add", "-A")
    for rel in ("catalog/x/orig/x.jpg", "catalog/x/orig/hop.jpg"):
        _checkout_without_symlinks(repo, rel)
    report = _run(repo)
    assert report["orphans"] == []
    assert report["byte_copies"]["catalog/x/orig/hop.jpg"] == "assets/products/a.png"


def test_link_leaving_the_repo_is_not_followed(repo: Path) -> None:
    (repo / "catalog/x/orig/out.jpg").symlink_to("../../../../outside.png")
    _git(repo, "add", "-A")
    _checkout_without_symlinks(repo, "catalog/x/orig/out.jpg")
    assert census.tracked_symlinks(repo) == {
        "catalog/x/orig/x.jpg": "assets/products/a.png",
    }
    assert [row["path"] for row in _run(repo)["orphans"]] == ["catalog/x/orig/out.jpg"]


WORKFLOW = census.REPO_ROOT / ".github/workflows/catalog-validate.yml"


@pytest.mark.parametrize("event", ["pull_request", "push"])
def test_workflow_triggers_on_every_scanned_extension(event: str) -> None:
    """A PR adding only an orphan of any scanned type, in any case, must run the census."""
    yaml = pytest.importorskip("yaml")
    workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    triggers = workflow.get("on") or workflow[True]  # PyYAML reads a bare `on` key as True
    patterns = triggers[event]["paths"]
    missing = [
        name
        for ext in sorted(census.MEDIA_EXTENSIONS)
        for name in (f"assets/x/new.{ext}", f"assets/x/new.{ext.upper()}")
        if not any(fnmatch.fnmatchcase(name, pattern) for pattern in patterns)
    ]
    assert missing == []
