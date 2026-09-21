"""A committed bug id may be added to, but never redefined.

The allocator (mcp_servers/wolf_memory/store.py) now floors the next id on
`origin/main`, so the MCP path cannot mint a duplicate. It is not the only
writer: OPENWOLF.md still sanctions hand-editing buglog.json when the server is
unreachable, and that path is unpoliceable from inside the allocator.

So this is the backstop, and it is deliberately Python-only with no MCP import:
it runs wherever pytest runs, including where the server does not. It answers
one question — does this tree redefine an id that main has already published?
That is the shape of bug-353, where two unrelated defects both claimed bug-353
and a citation in docs/engineering-learnings.md ended up pointing at the wrong
one.

Adding entries and bumping `occurrences`/`last_seen` on an existing entry are
the normal operations and stay allowed. Changing what an id MEANS is not.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
BUGLOG = REPO_ROOT / ".wolf" / "buglog.json"
PUBLISHED = "origin/main"

# Fields a later session legitimately rewrites on an existing entry: a bump, a
# better description of the same defect, or a fix landing after the report.
MUTABLE_FIELDS = frozenset(
    {"occurrences", "last_seen", "fix", "tags", "related_bugs", "root_cause"}
)
# Fields that identify WHICH defect an id refers to. A change here means the id
# was reused for something else.
IDENTITY_FIELDS = ("error_message", "file")


def _entries(payload: str) -> list[dict]:
    data = json.loads(payload)
    return data if isinstance(data, list) else data.get("bugs", [])


def _published_buglog() -> list[dict] | None:
    """Entries on origin/main, or None when there is nothing published here."""
    ref = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"refs/remotes/{PUBLISHED}"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if ref.returncode != 0:
        return None
    relative = BUGLOG.relative_to(REPO_ROOT).as_posix()
    blob = subprocess.run(
        ["git", "show", f"{PUBLISHED}:{relative}"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if blob.returncode != 0:
        return None
    return _entries(blob.stdout)


@pytest.fixture(scope="module")
def local() -> list[dict]:
    if not BUGLOG.exists():
        pytest.skip("no .wolf/buglog.json in this checkout")
    return _entries(BUGLOG.read_text(encoding="utf-8"))


def test_no_duplicate_ids(local: list[dict]) -> None:
    ids = [e.get("id") for e in local]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    assert not duplicates, f"the same id appears more than once: {duplicates}"


def test_no_published_id_is_redefined(local: list[dict]) -> None:
    published = _published_buglog()
    if published is None:
        pytest.skip(f"{PUBLISHED} has no buglog to compare against")

    by_id = {e["id"]: e for e in published if "id" in e}
    redefined = []
    for entry in local:
        was = by_id.get(entry.get("id"))
        if was is None:
            continue  # a new id, which is the point of the file
        for field in IDENTITY_FIELDS:
            if entry.get(field) != was.get(field):
                redefined.append(
                    f"{entry['id']}: {field} changed from {was.get(field)!r} "
                    f"to {entry.get(field)!r}"
                )
    assert not redefined, (
        "these ids already mean something else on "
        f"{PUBLISHED} — allocate a new id rather than reusing one:\n  " + "\n  ".join(redefined)
    )


def test_local_does_not_drop_published_entries(local: list[dict]) -> None:
    """A tree behind main is what produces a collision in the first place.

    The allocator now reads origin/main directly so it no longer depends on the
    working copy being current, but a buglog that has silently lost published
    entries is still a merge that went wrong, and saying so here is cheaper
    than finding out when an id is next issued.
    """
    published = _published_buglog()
    if published is None:
        pytest.skip(f"{PUBLISHED} has no buglog to compare against")

    missing = sorted(
        {e["id"] for e in published if "id" in e} - {e.get("id") for e in local},
        key=lambda i: int(i.split("-")[1]) if i.split("-")[-1].isdigit() else 0,
    )
    assert not missing, (
        f"entries published on {PUBLISHED} are absent from this buglog "
        f"(merge main in rather than committing over them): {missing}"
    )
