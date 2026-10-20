"""Tests for scripts/wolf_recurring_sync.py -- the recurring-bug digest in CLAUDE.md.

The Stop hook runs the sync at every turn end. If its output differs from the
committed (prettier-formatted) CLAUDE.md by even one byte, every session ends
with ``M CLAUDE.md`` and the git-check hook demands a commit. These tests pin
the script and the committed file to the same bytes.
"""

from __future__ import annotations

import re

from scripts.wolf_recurring_sync import (
    BUGLOG,
    CLAUDE_MD,
    END,
    START,
    load_bugs,
    render_block,
    select_bugs,
    sync_text,
)

HEADING = "### Recurring issues"


def _bug(bug_id: str, occurrences: int, tags: list[str] | None = None) -> dict:
    return {
        "id": bug_id,
        "occurrences": occurrences,
        "last_seen": "2026-10-20T00:00:00Z",
        "error_message": f"{bug_id} problem",
        "fix": f"{bug_id} fix",
        "tags": tags or [],
    }


def test_sync_is_noop_on_committed_claude_md():
    assert CLAUDE_MD.exists() and BUGLOG.exists()
    text = CLAUDE_MD.read_text()
    assert START in text and END in text
    synced = sync_text(text, select_bugs(load_bugs()))
    assert synced == text, (
        "scripts/wolf_recurring_sync.py would rewrite the committed CLAUDE.md -- "
        "either run the sync and commit, or align render_block() with the committed format"
    )


def test_recurring_block_is_inside_prettier_ignore():
    # prettier (proseWrap: always, printWidth 80 for *.md) would re-wrap the
    # one-line entries and the two tools would fight over the block again.
    text = CLAUDE_MD.read_text()
    assert re.search(
        r"<!-- prettier-ignore-start -->\n"
        + re.escape(START)
        + r".*?"
        + re.escape(END)
        + r"\n<!-- prettier-ignore-end -->",
        text,
        flags=re.DOTALL,
    ), "the wolf:recurring block must stay wrapped in <!-- prettier-ignore-start/end -->"


def test_render_block_blank_line_after_start_none_before_end():
    block = render_block([_bug("bug-001", 3)])
    assert block.startswith(f"{START}\n\n{HEADING}")
    assert block.endswith(
        f"- **bug-001** (×3, 2026-10-20): bug-001 problem → fix: bug-001 fix\n{END}"
    )


def test_render_block_empty():
    assert render_block([]).endswith(f"\n- none on record\n{END}")
    assert render_block([]).startswith(f"{START}\n\n{HEADING}")


def test_sync_text_is_idempotent_and_preserves_surroundings():
    text = f"intro\n\n<!-- prettier-ignore-start -->\n{START}\nstale\n{END}\n<!-- prettier-ignore-end -->\n"
    bugs = [_bug("bug-001", 2)]
    once = sync_text(text, bugs)
    assert once.startswith("intro\n\n<!-- prettier-ignore-start -->\n")
    assert once.endswith(f"{END}\n<!-- prettier-ignore-end -->\n")
    assert sync_text(once, bugs) == once


def test_sync_text_keeps_backslashes_literal():
    bug = {**_bug("bug-002", 2), "error_message": r"C:\new\g<1> path"}
    assert r"C:\new\g<1> path" in sync_text(f"{START}\n{END}", [bug])


def test_select_bugs_filters_and_orders():
    bugs = [
        _bug("bug-003", 1),
        _bug("bug-002", 5),
        _bug("bug-001", 5),
        _bug("bug-004", 9, tags=["auto-detected"]),
    ]
    assert [b["id"] for b in select_bugs(bugs)] == ["bug-001", "bug-002"]
    assert [b["id"] for b in select_bugs(bugs, include_auto=True)] == [
        "bug-004",
        "bug-001",
        "bug-002",
    ]
    assert [b["id"] for b in select_bugs(bugs, min_occurrences=1)] == [
        "bug-001",
        "bug-002",
        "bug-003",
    ]
