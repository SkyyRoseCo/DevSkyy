"""The id allocator must not reissue an id that is already published on main.

bug-353 (2026-09-21): the counter's floor is the max id in the LOCAL
buglog.json. A checkout that is behind `origin/main` therefore hands out ids
main has already used — `main` had a bug-353 about an SSRF test fixture, and a
session whose working tree was missing nine entries was issued `bug-353` for a
completely different defect. Both then claimed the same id, and a citation
written into docs/engineering-learnings.md pointed at the wrong bug.

The SQLite counter de-races sessions sharing one checkout, which is what it was
built for. It cannot de-race a checkout against published history, because it
never looks there. This raises the floor to include what main has published.

bug-231 discipline: every test gets its own tmp_path buglog + lock db.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from mcp_servers.wolf_memory.store import WolfMemoryStore


def _entry(number: int, message: str = "x") -> dict:
    return {
        "id": f"bug-{number:03d}",
        "timestamp": "2026-09-21",
        "error_message": message,
        "file": "a.py",
        "root_cause": "x",
        "fix": "y",
        "tags": [],
        "related_bugs": [],
        "occurrences": 1,
        "last_seen": "2026-09-21",
    }


def _git(*args: str, cwd: Path) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout.strip()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A real repository with an `origin/main` remote-tracking ref.

    Built with a clone rather than a hand-written ref so that
    `git show origin/main:<path>` resolves exactly as it does in the real
    checkout — the mechanism under test is that resolution, not a mock of it.
    """
    upstream = tmp_path / "upstream"
    upstream.mkdir()
    _git("init", "-b", "main", cwd=upstream)
    _git("config", "user.email", "t@example.invalid", cwd=upstream)
    _git("config", "user.name", "T", cwd=upstream)
    wolf = upstream / ".wolf"
    wolf.mkdir()
    # Published history: ids up to 353.
    (wolf / "buglog.json").write_text(
        json.dumps([_entry(352), _entry(353, "the SSRF fixture bug")], indent=2) + "\n"
    )
    _git("add", "-A", cwd=upstream)
    _git("commit", "-m", "published", cwd=upstream)

    clone = tmp_path / "clone"
    _git("clone", str(upstream), str(clone), cwd=tmp_path)
    return clone


class TestPublishedIdsRaiseTheFloor:
    def test_stale_checkout_does_not_reissue_a_published_id(self, repo: Path) -> None:
        """The exact bug-353 shape: local max 352, published max 353."""
        buglog = repo / ".wolf" / "buglog.json"
        # A working tree that is behind: it never received bug-353.
        buglog.write_text(json.dumps([_entry(352)], indent=2) + "\n")

        store = WolfMemoryStore(buglog_path=buglog, lock_db_path=repo / ".wolf" / "wolf.lock.db")
        assert store.next_bug_id() == "bug-354", (
            "allocated an id that origin/main has already published — "
            "two different defects would claim it"
        )

    def test_local_ahead_of_main_still_wins(self, repo: Path) -> None:
        """The published floor RAISES the floor; it must never lower it."""
        buglog = repo / ".wolf" / "buglog.json"
        buglog.write_text(json.dumps([_entry(352), _entry(400)], indent=2) + "\n")

        store = WolfMemoryStore(buglog_path=buglog, lock_db_path=repo / ".wolf" / "wolf.lock.db")
        assert store.next_bug_id() == "bug-401"

    def test_unreadable_published_buglog_refuses_to_allocate(self, repo: Path) -> None:
        """A gate that cannot read its input must block, not guess (bug-230).

        origin/main exists but its buglog is not parseable, so the highest
        published id is unknown. Allocating anyway is how a collision is
        minted silently.
        """
        buglog = repo / ".wolf" / "buglog.json"
        buglog.write_text(json.dumps([_entry(352)], indent=2) + "\n")
        upstream = Path(_git("config", "remote.origin.url", cwd=repo))
        (upstream / ".wolf" / "buglog.json").write_text("{ this is not json")
        _git("-C", str(upstream), "add", "-A", cwd=repo)
        _git("-C", str(upstream), "commit", "-m", "corrupt", cwd=repo)
        _git("fetch", "origin", cwd=repo)

        with pytest.raises(ValueError, match="origin/main"):
            WolfMemoryStore(
                buglog_path=buglog, lock_db_path=repo / ".wolf" / "wolf.lock.db"
            ).next_bug_id()

    def test_no_origin_main_ref_allocates_from_local(self, tmp_path: Path) -> None:
        """A fresh clone or a non-git fixture must keep working.

        The published floor is an additional source, not a requirement: with no
        origin/main there is nothing published to collide with.
        """
        buglog = tmp_path / "buglog.json"
        buglog.write_text(json.dumps([_entry(352)], indent=2) + "\n")
        store = WolfMemoryStore(buglog_path=buglog, lock_db_path=tmp_path / "wolf.lock.db")
        assert store.next_bug_id() == "bug-353"
