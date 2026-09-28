"""Tests for mcp_servers.wolf_memory.store — RED first.

bug-231 discipline: every test gets its own tmp_path buglog.json + lock db,
never the real 337KB .wolf/buglog.json.
"""

from __future__ import annotations

import json
import multiprocessing
import sys
from pathlib import Path

import pytest

from mcp_servers.wolf_memory.store import WolfMemoryStore

FIXTURE_ENTRIES = [
    {
        "id": "bug-001",
        "timestamp": "2026-04-07T23:54:02.717Z",
        "error_message": "Significant refactor of ",
        "file": "a.css",
        "root_cause": "x",
        "fix": "y",
        "tags": ["auto-detected"],
        "related_bugs": [],
        "occurrences": 2,
        "last_seen": "2026-04-07T23:54:18.004Z",
    },
    {
        "id": "bug-096",
        "timestamp": "2026-05-08",
        "error_message": "Tripo hallucinated brand canon",
        "file": "scripts/tripo_dispatch.py",
        "root_cause": "no classifier",
        "fix": "added classify_skus()",
        "tags": ["tripo"],
        "related_bugs": [],
        "occurrences": 30,
        "last_seen": "2026-05-08",
    },
]


@pytest.fixture
def store(tmp_path: Path) -> WolfMemoryStore:
    buglog = tmp_path / "buglog.json"
    buglog.write_text(json.dumps(FIXTURE_ENTRIES, indent=2) + "\n")
    return WolfMemoryStore(buglog_path=buglog, lock_db_path=tmp_path / "wolf.lock.db")


@pytest.fixture
def empty_store(tmp_path: Path) -> WolfMemoryStore:
    buglog = tmp_path / "buglog.json"
    buglog.write_text("[]\n")
    return WolfMemoryStore(buglog_path=buglog, lock_db_path=tmp_path / "wolf.lock.db")


class TestCounterSeeding:
    def test_seeds_from_max_existing_id_not_from_zero(self, store: WolfMemoryStore) -> None:
        """The fixture already has bug-096. A fresh counter must not hand out bug-001 again."""
        new_id = store.next_bug_id()
        assert new_id == "bug-097"

    def test_seeds_from_zero_when_buglog_is_empty(self, empty_store: WolfMemoryStore) -> None:
        assert empty_store.next_bug_id() == "bug-001"

    def test_ignores_malformed_ids_when_seeding(self, tmp_path: Path) -> None:
        buglog = tmp_path / "buglog.json"
        buglog.write_text(json.dumps([{"id": "not-a-bug-id"}, {"id": "bug-005"}]))
        s = WolfMemoryStore(buglog_path=buglog, lock_db_path=tmp_path / "wolf.lock.db")
        assert s.next_bug_id() == "bug-006"

    def test_reopening_store_does_not_reseed_past_allocations(self, tmp_path: Path) -> None:
        """Seeding must happen once, from disk state at first run, not on every open."""
        buglog = tmp_path / "buglog.json"
        buglog.write_text(json.dumps(FIXTURE_ENTRIES))
        lock_db = tmp_path / "wolf.lock.db"

        first = WolfMemoryStore(buglog_path=buglog, lock_db_path=lock_db)
        assert first.next_bug_id() == "bug-097"

        second = WolfMemoryStore(buglog_path=buglog, lock_db_path=lock_db)
        assert second.next_bug_id() == "bug-098"

    def test_never_reissues_an_id_appended_outside_the_store(self, store: WolfMemoryStore) -> None:
        """OPENWOLF.md keeps a manual-edit fallback, so buglog.json can gain ids
        the counter never allocated. Allocation must reconcile against the file."""
        entries = json.loads(store.buglog_path.read_text())
        entries.append({**FIXTURE_ENTRIES[0], "id": "bug-500", "file": "manual.py"})
        store.buglog_path.write_text(json.dumps(entries, indent=2) + "\n")

        assert store.next_bug_id() == "bug-501"
        entry = store.bug_log(
            error_message="after manual append", file="z.py", root_cause="rc", fix="fx", tags=[]
        )
        assert entry["id"] == "bug-502"


class TestBugLog:
    def test_appends_new_entry_atomically(self, store: WolfMemoryStore) -> None:
        entry = store.bug_log(
            error_message="new failure",
            file="foo.py",
            root_cause="rc",
            fix="fx",
            tags=["test"],
        )
        assert entry["id"] == "bug-097"
        on_disk = json.loads(store.buglog_path.read_text())
        assert len(on_disk) == 3
        assert on_disk[-1]["id"] == "bug-097"

    def test_duplicate_bumps_instead_of_creating_new_id(self, store: WolfMemoryStore) -> None:
        """OPENWOLF.md rule: bump occurrences + last_seen instead of duplicating."""
        entry = store.bug_log(
            error_message="Tripo hallucinated brand canon",
            file="scripts/tripo_dispatch.py",
            root_cause="dup",
            fix="dup",
            tags=["tripo"],
        )
        assert entry["id"] == "bug-096"
        assert entry["occurrences"] == 31
        on_disk = json.loads(store.buglog_path.read_text())
        assert len(on_disk) == 2  # no new entry appended

    def test_preserves_raw_unicode_in_existing_entries_on_write(self, tmp_path: Path) -> None:
        """json.dumps defaults to ensure_ascii=True — that would re-escape every
        non-ASCII char in the WHOLE file (→, —, etc. are common in real
        buglog.json entries) into \\uXXXX on every single append, a massive
        unrelated diff each time. json.loads round-trips escapes fine either
        way, so this must check the raw on-disk bytes, not a re-parsed dict.
        """
        buglog = tmp_path / "buglog.json"
        buglog.write_text(
            json.dumps(
                [
                    {
                        "id": "bug-001",
                        "timestamp": "2026-01-01",
                        "error_message": "x",
                        "file": "a.py",
                        "root_cause": "rc",
                        "fix": "Rewrote 5→12 lines — cleaner",
                        "tags": [],
                        "related_bugs": [],
                        "occurrences": 1,
                        "last_seen": "2026-01-01",
                    }
                ],
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        s = WolfMemoryStore(buglog_path=buglog, lock_db_path=tmp_path / "wolf.lock.db")
        s.bug_log(error_message="new", file="b.py", root_cause="rc", fix="fx", tags=[])

        raw = buglog.read_text(encoding="utf-8")
        assert "5→12 lines — cleaner" in raw
        assert "\\u2192" not in raw
        assert "\\u2014" not in raw

    def test_refuses_write_that_would_reencode_a_drifted_file(self, tmp_path: Path) -> None:
        """bug-250: a whole-file re-serialize of a file in a different native
        format churns every line. Fail closed: no write, no burned id."""
        buglog = tmp_path / "buglog.json"
        drifted = json.dumps([{**FIXTURE_ENTRIES[1], "fix": "5→12"}], indent=2) + "\n"
        assert "\\u2192" in drifted
        buglog.write_text(drifted, encoding="utf-8")
        s = WolfMemoryStore(buglog_path=buglog, lock_db_path=tmp_path / "wolf.lock.db")

        with pytest.raises(ValueError, match="native format"):
            s.bug_log(error_message="new", file="b.py", root_cause="rc", fix="fx", tags=[])
        with pytest.raises(ValueError, match="native format"):
            s.bug_bump("bug-096")

        assert buglog.read_text(encoding="utf-8") == drifted
        assert s.next_bug_id() == "bug-097"

    def test_refuses_write_to_a_non_list_buglog(self, tmp_path: Path) -> None:
        """Writes serialize the entry list, so a {"bugs": [...]} wrapper would be
        silently dropped — refuse instead of changing the file's shape."""
        buglog = tmp_path / "buglog.json"
        wrapped = json.dumps({"bugs": FIXTURE_ENTRIES}, indent=2) + "\n"
        buglog.write_text(wrapped)
        s = WolfMemoryStore(buglog_path=buglog, lock_db_path=tmp_path / "wolf.lock.db")

        with pytest.raises(ValueError, match="JSON list"):
            s.bug_log(error_message="new", file="b.py", root_cause="rc", fix="fx", tags=[])
        assert buglog.read_text() == wrapped

    def test_no_temp_files_left_behind_after_write(self, store: WolfMemoryStore) -> None:
        store.bug_log(error_message="x", file="y", root_cause="z", fix="w", tags=[])
        leftovers = list(store.buglog_path.parent.glob("*.tmp-*"))
        assert leftovers == []

    def test_failed_write_does_not_burn_an_id(
        self, store: WolfMemoryStore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import mcp_servers.wolf_memory.store as store_module

        def boom(*args, **kwargs):
            raise OSError("disk full")

        # Patch the name where store.py bound it via `from ... import atomic_write_text` —
        # patching the defining module doesn't affect the already-copied reference.
        monkeypatch.setattr(store_module, "atomic_write_text", boom)
        with pytest.raises(OSError):
            store.bug_log(error_message="x", file="y", root_cause="z", fix="w", tags=[])
        # counter must not have advanced past the pre-failure state
        assert store.next_bug_id() == "bug-097"


class TestBugBump:
    def test_bump_increments_occurrences_and_updates_last_seen(
        self, store: WolfMemoryStore
    ) -> None:
        updated = store.bug_bump("bug-001")
        assert updated["occurrences"] == 3
        assert updated["last_seen"] != "2026-04-07T23:54:18.004Z"

    def test_bump_unknown_id_raises(self, store: WolfMemoryStore) -> None:
        with pytest.raises(KeyError):
            store.bug_bump("bug-999")

    def test_bump_flags_recurring_sync_needed_at_threshold(self, store: WolfMemoryStore) -> None:
        # bug-001 goes 2 -> 3, already past the >=2 sync threshold both before and after
        updated = store.bug_bump("bug-001")
        assert updated["_recurring_sync_needed"] is True


class TestBugSearch:
    def test_search_matches_error_message_substring(self, store: WolfMemoryStore) -> None:
        results = store.bug_search("hallucinated")
        assert [r["id"] for r in results] == ["bug-096"]

    def test_search_filters_by_tag(self, store: WolfMemoryStore) -> None:
        results = store.bug_search("", tags=["tripo"])
        assert [r["id"] for r in results] == ["bug-096"]

    def test_search_filters_by_min_occurrences(self, store: WolfMemoryStore) -> None:
        results = store.bug_search("", min_occurrences=10)
        assert [r["id"] for r in results] == ["bug-096"]


def _cross_process_worker(buglog_path: str, lock_db_path: str, n: int, result_path: str) -> None:
    """Runs in a real child process — pytest threads share the GIL and wouldn't
    exercise the cross-process file lock, which is the entire point of this test.
    """
    store = WolfMemoryStore(buglog_path=Path(buglog_path), lock_db_path=Path(lock_db_path))
    ids = [store.next_bug_id() for _ in range(n)]
    Path(result_path).write_text(json.dumps(ids))


def _cross_process_bug_log_worker(buglog_path: str, lock_db_path: str, n: int) -> None:
    """Module-level (not a test-method closure) so it's picklable under spawn."""
    import os

    store = WolfMemoryStore(buglog_path=Path(buglog_path), lock_db_path=Path(lock_db_path))
    pid = os.getpid()
    for i in range(n):
        # Distinct `file` per call so the duplicate-detector (correctly) never
        # collapses these — this test isolates the lost-update race, not
        # duplicate detection (that's TestBugLog::test_duplicate_bumps_instead...).
        store.bug_log(
            error_message=f"unique failure {pid}-{i}",
            file=f"file-{pid}-{i}.py",
            root_cause="rc",
            fix="fx",
            tags=[],
        )


class TestCrossProcessConcurrency:
    def test_concurrent_processes_never_allocate_the_same_id(self, tmp_path: Path) -> None:
        buglog = tmp_path / "buglog.json"
        buglog.write_text(json.dumps(FIXTURE_ENTRIES))
        lock_db = tmp_path / "wolf.lock.db"
        n_per_proc = 15
        n_procs = 4

        ctx = multiprocessing.get_context("spawn" if sys.platform == "darwin" else "fork")
        procs = []
        result_paths = []
        for i in range(n_procs):
            result_path = tmp_path / f"result-{i}.json"
            result_paths.append(result_path)
            p = ctx.Process(
                target=_cross_process_worker,
                args=(str(buglog), str(lock_db), n_per_proc, str(result_path)),
            )
            procs.append(p)

        for p in procs:
            p.start()
        for p in procs:
            p.join(timeout=30)
            assert p.exitcode == 0

        all_ids: list[str] = []
        for result_path in result_paths:
            all_ids.extend(json.loads(result_path.read_text()))

        assert len(all_ids) == n_per_proc * n_procs
        assert len(set(all_ids)) == len(all_ids), "duplicate id allocated across processes"

    def test_concurrent_bug_log_appends_never_lose_an_entry(self, tmp_path: Path) -> None:
        """The lost-update race: two processes each read-modify-write buglog.json.
        Without the shared lock covering the file write (not just the counter),
        the second writer's file write clobbers the first writer's append.
        """
        buglog = tmp_path / "buglog.json"
        buglog.write_text("[]\n")
        lock_db = tmp_path / "wolf.lock.db"
        n_per_proc = 10
        n_procs = 4

        ctx = multiprocessing.get_context("spawn" if sys.platform == "darwin" else "fork")
        procs = [
            ctx.Process(
                target=_cross_process_bug_log_worker, args=(str(buglog), str(lock_db), n_per_proc)
            )
            for _ in range(n_procs)
        ]
        for p in procs:
            p.start()
        for p in procs:
            p.join(timeout=30)
            assert p.exitcode == 0

        on_disk = json.loads(buglog.read_text())
        assert len(on_disk) == n_per_proc * n_procs
        ids = [e["id"] for e in on_disk]
        assert len(set(ids)) == len(ids), "duplicate id in final buglog.json"
