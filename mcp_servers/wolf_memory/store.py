"""Atomic .wolf/buglog.json operations.

buglog.json stays the sole data source of truth — git-tracked, human-diffable,
same schema OPENWOLF.md already mandates. .wolf/wolf.lock.db holds no bug
data; it exists only to make ID allocation and the file read-modify-write
atomic across concurrent processes (see mcp_servers._shared.locked_transaction
for why a cross-process lock, not an in-process one, is what's needed here).
"""

from __future__ import annotations

import difflib
import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from mcp_servers._shared import atomic_write_text, locked_transaction

# Matches scripts/wolf_bug_id.py's ID_RE exactly — same id format, same source of truth.
ID_RE = re.compile(r"^bug-(\d+)$")

# Published history the id allocator must not collide with. Kept as constants so
# the ref check and the blob read can never drift onto different branches.
_PUBLISHED_BRANCH = "origin/main"
_PUBLISHED_REF = f"refs/remotes/{_PUBLISHED_BRANCH}"

RECURRING_SYNC_THRESHOLD = 2
DUPLICATE_MATCH_RATIO = 0.85

# Exact headings as they appear in .wolf/cerebrum.md today — kept as a fixed
# set (not free text) so an append can never land under a misspelled or
# freshly-invented heading.
CEREBRUM_SECTIONS = (
    "User Preferences",
    "Key Learnings",
    "Do-Not-Repeat",
    "Decision Log",
)


def validate_cerebrum_entry(entry: str) -> str:
    """Reject an entry that could forge structure in cerebrum.md.

    cerebrum.md is loaded as instructions in every session and sections are
    located by heading, so an entry with an embedded "\\n## X" line would
    become a real heading that captures every later append addressed to X.
    One bullet == one line, and a line may never start with "#". Shared by
    the tool-layer input model and the store: the store must not depend on
    its caller validating.
    """
    # splitlines() rather than a check for LF/CR: it also breaks on VT, FF, FS/GS/RS,
    # NEL and the Unicode line/paragraph separators, which renderers may honour too.
    # The second clause catches a lone trailing break, which splitlines() reports as
    # one line.
    if len(entry.splitlines()) > 1 or entry != "".join(entry.splitlines()):
        raise ValueError(
            "cerebrum entry must be a single line (no newline characters); "
            "an embedded line could be read as a markdown heading"
        )
    if entry.lstrip().startswith("#"):
        raise ValueError(
            "cerebrum entry must not start with '#' (it would be read as a markdown heading)"
        )
    return entry


def _serialize(entries: list[dict[str, Any]]) -> str:
    """buglog.json's native on-disk format. ensure_ascii=False keeps raw UTF-8
    (→, —); the default would \\u-escape every non-ASCII char in the whole file."""
    return json.dumps(entries, indent=2, ensure_ascii=False) + "\n"


class WolfMemoryStore:
    def __init__(
        self, buglog_path: Path, lock_db_path: Path, cerebrum_path: Path | None = None
    ) -> None:
        self.buglog_path = buglog_path
        self.lock_db_path = lock_db_path
        self.cerebrum_path = cerebrum_path
        self._ensure_counter_seeded()

    # ------------------------------------------------------------------
    # Counter lifecycle
    # ------------------------------------------------------------------

    def _ensure_counter_seeded(self) -> None:
        """Seed the counter from the max existing bug-NNN id, once.

        Seeding from 0 would hand out bug-001 again on a buglog.json that
        already has ~300 entries — the exact collision this server exists
        to prevent. Idempotent: a second WolfMemoryStore instance pointed
        at the same lock db sees the counter row already exists and leaves
        it alone, so re-opening the store never re-seeds past allocations.
        """
        with locked_transaction(self.lock_db_path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS counters (name TEXT PRIMARY KEY, value INTEGER NOT NULL)"
            )
            row = conn.execute("SELECT value FROM counters WHERE name = 'bug'").fetchone()
            if row is None:
                seed = self._max_existing_id()
                conn.execute("INSERT INTO counters (name, value) VALUES ('bug', ?)", (seed,))

    def _max_existing_id(self) -> int:
        """The floor for the next id: the highest id this checkout can see.

        Both sources matter. The local file catches ids appended by the
        manual-edit fallback that the counter never issued. `origin/main`
        catches ids already PUBLISHED that this working tree has not received
        yet — a checkout behind main otherwise reissues them (bug-353: a tree
        missing nine entries was handed bug-353 for a new defect while main's
        bug-353 was an SSRF fixture bug, and both then claimed the id).
        """
        return max(self._max_id(self._read_entries()), self._published_max_id())

    def _published_max_id(self) -> int:
        """Highest bug id on `origin/main`, or 0 when nothing is published.

        Reads a local ref — no network. Distinguishes three cases deliberately:
        not a repo / no origin/main ref / the file is absent there all mean
        "nothing published to collide with" and return 0, while a ref that
        exists but whose buglog cannot be parsed RAISES. An unreadable input is
        not an empty one (bug-230): guessing there is exactly how a duplicate
        id gets minted silently.
        """
        root = self._git("rev-parse", "--show-toplevel", cwd=self.buglog_path.parent)
        if root is None:
            return 0
        repo_root = Path(root)
        if self._git("rev-parse", "--verify", "--quiet", _PUBLISHED_REF, cwd=repo_root) is None:
            return 0
        try:
            relative = self.buglog_path.resolve().relative_to(repo_root.resolve())
        except ValueError:
            # A buglog outside the repo has no published counterpart.
            return 0
        blob = self._git("show", f"{_PUBLISHED_BRANCH}:{relative.as_posix()}", cwd=repo_root)
        if blob is None:
            return 0  # not tracked on main yet
        try:
            data = json.loads(blob)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"cannot read the published buglog at {_PUBLISHED_BRANCH}:{relative.as_posix()} "
                f"({error}); refusing to allocate an id that could already be in use there"
            ) from error
        entries = data if isinstance(data, list) else data.get("bugs", [])
        return self._max_id(entries)

    @staticmethod
    def _git(*args: str, cwd: Path) -> str | None:
        """Run git, returning stdout, or None when git says no.

        None means "git answered, and the answer is that this does not exist" —
        never "git could not run". A missing binary or an unreadable repo
        surfaces as the OSError it is.
        """
        result = subprocess.run(
            ["git", *args], cwd=cwd, capture_output=True, text=True, check=False
        )
        if result.returncode != 0:
            return None
        return result.stdout.strip() if len(args) < 2 or args[0] != "show" else result.stdout

    @staticmethod
    def _max_id(entries: list[dict[str, Any]]) -> int:
        numbers = [int(m.group(1)) for e in entries if (m := ID_RE.match(str(e.get("id", ""))))]
        return max(numbers) if numbers else 0

    def next_bug_id(self) -> str:
        with locked_transaction(self.lock_db_path) as conn:
            value = self._increment_counter(conn, floor=self._max_existing_id())
            return f"bug-{value:03d}"

    @staticmethod
    def _increment_counter(conn, floor: int) -> int:
        # floor = highest id already in buglog.json: the manual-edit fallback can
        # append ids the counter never allocated, and those must not be reissued.
        row = conn.execute("SELECT value FROM counters WHERE name = 'bug'").fetchone()
        value = max(row[0] if row else 0, floor) + 1
        conn.execute(
            "INSERT INTO counters (name, value) VALUES ('bug', ?) "
            "ON CONFLICT(name) DO UPDATE SET value = excluded.value",
            (value,),
        )
        return value

    # ------------------------------------------------------------------
    # buglog.json read/write
    # ------------------------------------------------------------------

    def _read_entries(self) -> list[dict[str, Any]]:
        if not self.buglog_path.exists():
            return []
        data = json.loads(self.buglog_path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else data.get("bugs", [])

    def _read_entries_for_write(self) -> list[dict[str, Any]]:
        """Fail closed instead of re-encoding a file whose format has drifted.

        Every write re-serializes the whole file, so unless _serialize reproduces
        the current bytes exactly, one append would churn every line (bug-250:
        467-line diff). A human normalizes the file in its own reviewed change.
        """
        if not self.buglog_path.exists():
            return []
        text = self.buglog_path.read_text(encoding="utf-8")
        data = json.loads(text)
        if not isinstance(data, list):
            raise ValueError(f"{self.buglog_path} must be a JSON list of entries to be written")
        if _serialize(data) != text:
            raise ValueError(
                f"{self.buglog_path} is not in native format (indent=2, raw UTF-8, trailing "
                "newline); a write would re-encode the whole file (bug-250). Normalize it in "
                "a separate reviewed change first."
            )
        return data

    def _find_duplicate(
        self, entries: list[dict[str, Any]], file: str, error_message: str
    ) -> dict[str, Any] | None:
        for entry in entries:
            if entry.get("file") != file:
                continue
            ratio = difflib.SequenceMatcher(
                None, entry.get("error_message", ""), error_message
            ).ratio()
            if ratio >= DUPLICATE_MATCH_RATIO:
                return entry
        return None

    def bug_log(
        self,
        error_message: str,
        file: str,
        root_cause: str,
        fix: str,
        tags: list[str],
        related_bugs: list[str] | None = None,
    ) -> dict[str, Any]:
        """Append a new bug entry, or bump an existing near-duplicate.

        The counter allocation and the file write happen inside the same
        locked_transaction: the counter is only persisted (via the ctx
        manager's COMMIT) after atomic_write_text succeeds, so a failed
        write never burns an id, and two concurrent bug_log calls can't
        interleave their read-modify-write of buglog.json.
        """
        with locked_transaction(self.lock_db_path) as conn:
            entries = self._read_entries_for_write()

            duplicate = self._find_duplicate(entries, file, error_message)
            if duplicate is not None:
                return self._bump_entry_locked(entries, duplicate["id"])

            value = self._increment_counter(conn, floor=self._max_id(entries))
            new_id = f"bug-{value:03d}"
            now = datetime.now(UTC).isoformat()
            entry = {
                "id": new_id,
                "timestamp": now,
                "error_message": error_message,
                "file": file,
                "root_cause": root_cause,
                "fix": fix,
                "tags": tags,
                "related_bugs": related_bugs or [],
                "occurrences": 1,
                "last_seen": now,
            }
            entries.append(entry)
            atomic_write_text(self.buglog_path, _serialize(entries))
            return entry

    def bug_bump(self, bug_id: str) -> dict[str, Any]:
        with locked_transaction(self.lock_db_path):
            entries = self._read_entries_for_write()
            return self._bump_entry_locked(entries, bug_id)

    def _bump_entry_locked(self, entries: list[dict[str, Any]], bug_id: str) -> dict[str, Any]:
        """Caller must already hold locked_transaction. Writes and returns the updated entry."""
        for entry in entries:
            if entry.get("id") == bug_id:
                entry["occurrences"] = entry.get("occurrences", 1) + 1
                entry["last_seen"] = datetime.now(UTC).isoformat()
                atomic_write_text(self.buglog_path, _serialize(entries))
                result = dict(entry)
                result["_recurring_sync_needed"] = entry["occurrences"] >= RECURRING_SYNC_THRESHOLD
                return result
        raise KeyError(f"no bug entry with id {bug_id!r}")

    def bug_search(
        self,
        query: str,
        tags: list[str] | None = None,
        min_occurrences: int | None = None,
    ) -> list[dict[str, Any]]:
        entries = self._read_entries()
        results = entries
        if query:
            q = query.lower()
            results = [
                e
                for e in results
                if q in e.get("error_message", "").lower()
                or q in e.get("fix", "").lower()
                or q in e.get("root_cause", "").lower()
            ]
        if tags:
            wanted = set(tags)
            results = [e for e in results if wanted & set(e.get("tags", []))]
        if min_occurrences is not None:
            results = [e for e in results if e.get("occurrences", 1) >= min_occurrences]
        return results

    # ------------------------------------------------------------------
    # cerebrum.md structured append
    # ------------------------------------------------------------------

    def cerebrum_append(self, section: str, entry: str) -> None:
        """Append `entry` as a new bullet at the end of the given `## {section}` block.

        The enum-like CEREBRUM_SECTIONS set makes misfiling structurally
        impossible — this can't land under a heading that doesn't exist.
        """
        if self.cerebrum_path is None:
            raise ValueError("cerebrum_path was not configured for this store")
        if section not in CEREBRUM_SECTIONS:
            raise ValueError(
                f"unknown cerebrum section {section!r}; must be one of {CEREBRUM_SECTIONS}"
            )
        validate_cerebrum_entry(entry)

        with locked_transaction(self.lock_db_path):
            text = self.cerebrum_path.read_text()
            heading = f"## {section}"
            # Anchored to a whole line: text.find("## X\n") would also match
            # inside a "### X" sub-heading that happens to come first.
            match = re.search(rf"^{re.escape(heading)}$", text, flags=re.MULTILINE)
            if match is None:
                raise ValueError(f"heading {heading!r} not found in {self.cerebrum_path}")

            body_start = match.end() + 1
            next_heading = re.search(r"^## ", text[body_start:], flags=re.MULTILINE)
            body_end = body_start + next_heading.start() if next_heading else len(text)

            body = text[body_start:body_end].rstrip("\n")
            bullet = entry if entry.lstrip().startswith("-") else f"- {entry}"
            new_body = f"{body}\n{bullet}\n\n" if body else f"\n{bullet}\n\n"

            new_text = text[:body_start] + new_body + text[body_end:]
            atomic_write_text(self.cerebrum_path, new_text)
