"""The `.wolf/memory.md merge=union` gitattribute must actually prevent conflicts.

Several sessions append rows to that log at the same place, so without a union
merge every concurrent PR conflicts there. These tests build a throwaway repo in
tmp_path and merge two divergent appends: with the repo's real .gitattributes the
merge succeeds and keeps both rows, and the control case (no .gitattributes)
proves the scenario genuinely conflicts otherwise.
"""

import subprocess
from pathlib import Path

import pytest

GITATTRIBUTES = Path(__file__).resolve().parents[1] / ".gitattributes"
HEADER = "| Time | Action | File(s) | Outcome | ~Tokens |\n| ---- | ------ | ------- | ------- | ------- |\n"
ROW_A = "| 01:00 | session A did a thing | a.py | ok | ~1k |\n"
ROW_B = "| 02:00 | session B did another thing | b.py | ok | ~2k |\n"


def git(repo, *args, check=True):
    return subprocess.run(
        [
            "git",
            "-c",
            "user.email=test@example.invalid",
            "-c",
            "user.name=Test",
            "-c",
            "commit.gpgsign=false",
            "-c",
            "core.hooksPath=/dev/null",
            *args,
        ],
        cwd=repo,
        capture_output=True,
        text=True,
        check=check,
        timeout=60,
    )


def build_repo(tmp_path, with_attributes):
    """A repo whose main and side branch each append a different row to the log."""
    repo = tmp_path / "repo"
    (repo / ".wolf").mkdir(parents=True)
    git(repo.parent, "init", "-q", "-b", "main", str(repo))
    if with_attributes:
        (repo / ".gitattributes").write_text(GITATTRIBUTES.read_text())
    (repo / ".wolf" / "memory.md").write_text(HEADER)
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "base")

    git(repo, "checkout", "-q", "-b", "side")
    (repo / ".wolf" / "memory.md").write_text(HEADER + ROW_A)
    git(repo, "commit", "-qam", "session A row")

    git(repo, "checkout", "-q", "main")
    (repo / ".wolf" / "memory.md").write_text(HEADER + ROW_B)
    git(repo, "commit", "-qam", "session B row")
    return repo


def test_union_attribute_merges_concurrent_rows(tmp_path):
    repo = build_repo(tmp_path, with_attributes=True)

    merge = git(repo, "merge", "--no-edit", "side", check=False)

    assert merge.returncode == 0, merge.stdout + merge.stderr
    merged = (repo / ".wolf" / "memory.md").read_text()
    assert ROW_A in merged
    assert ROW_B in merged
    assert "<<<<<<<" not in merged


def test_control_without_attribute_conflicts(tmp_path):
    """Proves the scenario is a real conflict, so the test above tests something."""
    repo = build_repo(tmp_path, with_attributes=False)

    merge = git(repo, "merge", "--no-edit", "side", check=False)

    assert merge.returncode != 0
    assert "<<<<<<<" in (repo / ".wolf" / "memory.md").read_text()


def test_rule_is_declared_for_memory_md_only():
    """buglog.json is JSON and cerebrum.md is edited in place; both must still conflict."""
    lines = [
        line.split("#", 1)[0].strip()
        for line in GITATTRIBUTES.read_text().splitlines()
        if line.split("#", 1)[0].strip()
    ]
    union = [line for line in lines if "merge=union" in line]
    assert union == [".wolf/memory.md merge=union"]


@pytest.mark.parametrize("path", [".wolf/buglog.json", ".wolf/cerebrum.md", ".wolf/anatomy.md"])
def test_other_wolf_files_keep_normal_merge(path):
    check = subprocess.run(
        ["git", "check-attr", "merge", "--", path],
        cwd=GITATTRIBUTES.parent,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert check.returncode == 0, check.stderr
    assert "unspecified" in check.stdout, check.stdout
