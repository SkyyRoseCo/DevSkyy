"""Tests for scripts/check_retired_brand_copy.py (the retired-tagline CI guard)."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_retired_brand_copy.py"
spec = importlib.util.spec_from_file_location("check_retired_brand_copy", SCRIPT)
guard = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = guard
spec.loader.exec_module(guard)

# Assembled in reverse at runtime so this file does not itself contain the retired wording.
PHRASE = " ".join(reversed(["Concrete", "from", "Grows", "Luxury"]))


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(tmp_path / "no-gitconfig"))
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    return root


def write(root: Path, name: str, content: str | bytes) -> None:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


def run(root: Path, allowlist=()) -> list[str]:
    return guard.find_violations(root, guard.tracked_paths(root), allowlist)


def test_clean_tree_passes(repo: Path) -> None:
    write(repo, "page.html", "<h1>Not basics. Blueprints.</h1>")
    assert run(repo) == []


def test_new_file_with_phrase_fails(repo: Path) -> None:
    write(repo, "theme/new.php", f"<p>{PHRASE}.</p>")
    assert run(repo) == ["Retired brand copy must be removed: theme/new.php"]


W = PHRASE.split()
VARIANTS = [
    "#" + "".join(W),
    "<br>".join([W[0], " ".join(W[1:3]), W[3]]),
    PHRASE.upper(),
    PHRASE.lower(),
    "&nbsp;".join(W),
    f'<img alt="{PHRASE}">',
    f"<img alt='{PHRASE}'>",
    f'<meta property="og:description" content="{PHRASE}.">',
    f'<a href="/x" title="{PHRASE}">x</a>',
    f'<button aria-label="{PHRASE.lower()}">',
    "<?php echo wp_kses( __( '"
    + "<br>".join([W[0], " ".join(W[1:3]), W[3]])
    + "', 'x' ), array() );",
]


@pytest.mark.parametrize("text", VARIANTS)
def test_variants_fail(repo: Path, text: str) -> None:
    write(repo, "v.txt", text)
    assert len(run(repo)) == 1


def test_phrase_in_file_name_fails(repo: Path) -> None:
    write(repo, "docs/blog-" + PHRASE.lower().replace(" ", "-") + ".md", "clean body")
    assert len(run(repo)) == 1


def test_allowlisted_file_passes(repo: Path) -> None:
    write(repo, "kept/quote.md", f"{PHRASE} (founder quote)")
    allow = (guard.AllowEntry("kept/quote.md", "kept on purpose", 1),)
    assert run(repo, allow) == []


def test_allowlisted_file_with_extra_occurrence_fails(repo: Path) -> None:
    write(repo, "kept/quote.md", f"{PHRASE}\n\nand again: {PHRASE}")
    allow = (guard.AllowEntry("kept/quote.md", "kept on purpose", 1),)
    problems = run(repo, allow)
    assert len(problems) == 1 and "increased" in problems[0]


def test_unpinned_glob_allows_records_but_not_other_paths(repo: Path) -> None:
    write(repo, "archive/old/page.html", PHRASE)
    write(repo, "src/page.html", PHRASE)
    allow = (guard.AllowEntry("archive/*", "archived site"),)
    assert run(repo, allow) == ["Retired brand copy must be removed: src/page.html"]


def test_undecodable_non_binary_file_fails(repo: Path) -> None:
    write(repo, "notes.txt", b"\xff\xfe\x00bad bytes")
    problems = run(repo)
    assert len(problems) == 1 and "Cannot decode" in problems[0]


def test_binary_extension_is_skipped(repo: Path) -> None:
    write(repo, "img/hero.webp", b"\xff\xfe\x00binary")
    write(repo, "lib/decoder.wasm", b"\x00asm\xff")
    assert run(repo) == []


def test_main_exit_codes(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write(repo, "ok.txt", "fine")
    assert guard.main(["--root", str(repo)]) == 0
    write(repo, "bad.txt", PHRASE)
    assert guard.main(["--root", str(repo)]) == 1
    assert "bad.txt" in capsys.readouterr().out


def test_not_a_git_repo_is_a_clear_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    plain = tmp_path / "plain"
    plain.mkdir()
    assert guard.main(["--root", str(plain)]) == 2
    err = capsys.readouterr().err.strip().splitlines()
    assert len(err) == 1 and err[0].startswith("Retired-copy check could not run")


def test_script_does_not_contain_the_phrase() -> None:
    assert not guard.contains_retired_copy(SCRIPT.read_text(encoding="utf-8"))


def test_pinned_file_gaining_attribute_occurrence_fails(repo: Path) -> None:
    write(repo, "kept/page.html", f'<p>{PHRASE}</p>\n<img alt="{PHRASE}">')
    allow = (guard.AllowEntry("kept/page.html", "kept", 1),)
    problems = run(repo, allow)
    assert len(problems) == 1 and "increased" in problems[0]


def test_new_file_outside_every_allowlisted_path_fails(repo: Path) -> None:
    write(repo, "tests/fixtures/new/nested.html", PHRASE)
    write(repo, "kept/page.html", PHRASE)
    allow = (guard.AllowEntry("kept/page.html", "kept", 1),)
    assert run(repo, allow) == [
        "Retired brand copy must be removed: tests/fixtures/new/nested.html"
    ]


def test_real_allowlist_has_no_unpinned_fixture_glob() -> None:
    assert not [
        e for e in guard.ALLOWLIST if e.pattern.startswith("tests/fixtures") and e.max_count is None
    ]


def test_stale_entries_are_reported_not_failed(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    write(repo, "clean.txt", "fine")
    allow = (
        guard.AllowEntry("gone.md", "removed", 1),
        guard.AllowEntry("clean.txt", "now clean", 1),
    )
    stale = guard.find_stale(repo, guard.tracked_paths(repo), allow)
    assert len(stale) == 2 and all("Stale" in m for m in stale)
    assert run(repo, allow) == []
