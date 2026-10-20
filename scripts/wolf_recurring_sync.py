#!/usr/bin/env python3
"""Sync recurring bugs (occurrences >= 2) from .wolf/buglog.json into CLAUDE.md.

Regenerates the block between the wolf:recurring markers in CLAUDE.md so every
session loads a 1-line digest of issues that have bitten more than once. The
full record stays in .wolf/buglog.json; this is the always-in-context index.

Auto-detected churn entries (tag "auto-detected") are excluded by default —
their messages carry no signal. Pass --include-auto to keep them.

Usage:
    python scripts/wolf_recurring_sync.py [--include-auto] [--min-occurrences N]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BUGLOG = REPO_ROOT / ".wolf" / "buglog.json"
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"
START = "<!-- wolf:recurring:start -->"
END = "<!-- wolf:recurring:end -->"
LINE_WIDTH = 160


def load_bugs() -> list[dict]:
    data = json.loads(BUGLOG.read_text())
    return data if isinstance(data, list) else data["bugs"]


def clip(text: str, limit: int) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def one_liner(bug: dict) -> str:
    day = str(bug.get("last_seen", "?"))[:10]
    problem = clip(bug.get("error_message", ""), LINE_WIDTH // 2)
    fix = clip(bug.get("fix", ""), LINE_WIDTH // 2)
    return f"- **{bug['id']}** (×{bug.get('occurrences', 1)}, {day}): {problem} → fix: {fix}"


def render_block(bugs: list[dict]) -> str:
    # Blank lines keep each marker its own markdown block. Without them the
    # parser merges START into the prettier-ignore-start comment and folds END
    # into the last list item, prettier stops honouring the ignore range, and
    # it and this script rewrite the block back and forth on every run.
    header = (
        f"{START}\n\n"
        "### Recurring issues (synced from `.wolf/buglog.json` — regenerate via "
        "`python scripts/wolf_recurring_sync.py`, do not hand-edit)\n\n"
    )
    body = "\n".join(one_liner(b) for b in bugs) if bugs else "- none on record"
    return f"{header}{body}\n\n{END}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--include-auto", action="store_true")
    parser.add_argument("--min-occurrences", type=int, default=2)
    args = parser.parse_args()

    bugs = [b for b in load_bugs() if b.get("occurrences", 1) >= args.min_occurrences]
    if not args.include_auto:
        bugs = [b for b in bugs if "auto-detected" not in b.get("tags", [])]
    bugs.sort(key=lambda b: (-b.get("occurrences", 1), b["id"]))

    text = CLAUDE_MD.read_text()
    if START not in text or END not in text:
        print(f"ERROR: markers {START} / {END} not found in {CLAUDE_MD}", file=sys.stderr)
        return 1

    block = render_block(bugs)
    # lambda replacement: block is literal text, not a replacement template —
    # backslashes in bug messages (Windows paths, regex snippets) must not be
    # interpreted as \g<...> escapes.
    new_text = re.sub(
        re.escape(START) + r".*?" + re.escape(END),
        lambda _: block,
        text,
        count=1,
        flags=re.DOTALL,
    )
    if new_text == text:
        print(f"CLAUDE.md up to date ({len(bugs)} recurring)")
        return 0
    CLAUDE_MD.write_text(new_text)
    print(f"synced {len(bugs)} recurring issue(s) into CLAUDE.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
