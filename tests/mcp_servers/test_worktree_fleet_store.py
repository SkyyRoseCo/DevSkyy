"""Tests for mcp_servers.worktree_fleet.store — the ownership registry.

Git behavior itself is covered by test_worktree_fleet_git_ops.py against real
repos; these tests fake git_ops calls via monkeypatch to isolate registry
logic (claim conflicts, release gating, prune scoping) from git's own state
machine — the registry's correctness doesn't depend on git actually running.
"""

from __future__ import annotations

import sqlite3
import subprocess
from pathlib import Path

import pytest

from mcp_servers.worktree_fleet import git_ops
from mcp_servers.worktree_fleet.store import ClaimConflictError, WorktreeFleetStore


@pytest.fixture
def store(tmp_path: Path) -> WorktreeFleetStore:
    return WorktreeFleetStore(db_path=tmp_path / "fleet.db")


class TestClaim:
    def test_claim_inserts_a_registry_row(
        self, store: WorktreeFleetStore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(git_ops, "add_worktree", lambda **kwargs: None)
        row = store.claim(
            repo_root=Path("/repo"),
            worktree_path=Path("/repo/../wt-a"),
            branch="feat-a",
            owner="claude:sess1",
            purpose="testing",
            base_ref="main",
        )
        assert row["branch"] == "feat-a"
        assert row["owner"] == "claude:sess1"
        assert row["status"] == "active"

    def test_reclaiming_same_branch_same_owner_is_idempotent(
        self, store: WorktreeFleetStore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(git_ops, "add_worktree", lambda **kwargs: None)
        first = store.claim(
            repo_root=Path("/repo"),
            worktree_path=Path("/wt-a"),
            branch="feat-a",
            owner="claude:sess1",
            purpose="p",
            base_ref="main",
        )
        second = store.claim(
            repo_root=Path("/repo"),
            worktree_path=Path("/wt-a"),
            branch="feat-a",
            owner="claude:sess1",
            purpose="p",
            base_ref="main",
        )
        assert first["path"] == second["path"]

    def test_claiming_a_branch_owned_by_someone_else_refuses(
        self, store: WorktreeFleetStore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(git_ops, "add_worktree", lambda **kwargs: None)
        store.claim(
            repo_root=Path("/repo"),
            worktree_path=Path("/wt-a"),
            branch="feat-a",
            owner="claude:sess1",
            purpose="p",
            base_ref="main",
        )
        with pytest.raises(ClaimConflictError):
            store.claim(
                repo_root=Path("/repo"),
                worktree_path=Path("/wt-b"),
                branch="feat-a",
                owner="codex:other",
                purpose="p",
                base_ref="main",
            )


class TestHeartbeatAndList:
    def test_heartbeat_updates_last_seen(
        self, store: WorktreeFleetStore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(git_ops, "add_worktree", lambda **kwargs: None)
        row = store.claim(
            repo_root=Path("/repo"),
            worktree_path=Path("/wt-a"),
            branch="feat-a",
            owner="claude:sess1",
            purpose="p",
            base_ref="main",
        )
        first_seen = row["last_seen_at"]
        store.heartbeat(Path("/wt-a"))
        updated = store.get(Path("/wt-a"))
        assert updated["last_seen_at"] >= first_seen

    def test_list_filters_by_status_and_owner(
        self, store: WorktreeFleetStore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(git_ops, "add_worktree", lambda **kwargs: None)
        store.claim(
            repo_root=Path("/repo"),
            worktree_path=Path("/wt-a"),
            branch="a",
            owner="claude:s1",
            purpose="p",
            base_ref="main",
        )
        store.claim(
            repo_root=Path("/repo"),
            worktree_path=Path("/wt-b"),
            branch="b",
            owner="codex:s2",
            purpose="p",
            base_ref="main",
        )
        assert [r["branch"] for r in store.list(owner="claude:s1")] == ["a"]
        assert {r["branch"] for r in store.list()} == {"a", "b"}


class TestRelease:
    def test_release_refuses_when_dirty(
        self, store: WorktreeFleetStore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(git_ops, "add_worktree", lambda **kwargs: None)
        monkeypatch.setattr(git_ops, "is_dirty", lambda path: True)
        store.claim(
            repo_root=Path("/repo"),
            worktree_path=Path("/wt-a"),
            branch="a",
            owner="claude:s1",
            purpose="p",
            base_ref="main",
        )
        result = store.release(Path("/wt-a"), branch="a", base_ref="main", owner="claude:s1")
        assert result["released"] is False
        assert "dirty" in result["reason"].lower()
        assert store.get(Path("/wt-a"))["status"] == "active"

    def test_release_refuses_when_unpushed(
        self, store: WorktreeFleetStore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from mcp_servers.worktree_fleet.git_ops import PushState, PushStatus

        monkeypatch.setattr(git_ops, "add_worktree", lambda **kwargs: None)
        monkeypatch.setattr(git_ops, "is_dirty", lambda path: False)
        monkeypatch.setattr(
            git_ops,
            "push_status",
            lambda **kwargs: PushStatus(
                PushState.UNPUSHED, ["abc123 x"], "1 commit(s) not on origin/a"
            ),
        )
        store.claim(
            repo_root=Path("/repo"),
            worktree_path=Path("/wt-a"),
            branch="a",
            owner="claude:s1",
            purpose="p",
            base_ref="main",
        )
        result = store.release(Path("/wt-a"), branch="a", base_ref="main", owner="claude:s1")
        assert result["released"] is False
        assert "abc123 x" in result["reason"]

    def test_release_succeeds_when_clean_and_up_to_date(
        self, store: WorktreeFleetStore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from mcp_servers.worktree_fleet.git_ops import PushState, PushStatus

        monkeypatch.setattr(git_ops, "add_worktree", lambda **kwargs: None)
        monkeypatch.setattr(git_ops, "is_dirty", lambda path: False)
        monkeypatch.setattr(
            git_ops, "push_status", lambda **kwargs: PushStatus(PushState.UP_TO_DATE)
        )
        store.claim(
            repo_root=Path("/repo"),
            worktree_path=Path("/wt-a"),
            branch="a",
            owner="claude:s1",
            purpose="p",
            base_ref="main",
        )
        result = store.release(Path("/wt-a"), branch="a", base_ref="main", owner="claude:s1")
        assert result["released"] is True
        assert store.get(Path("/wt-a"))["status"] == "ready_to_merge"

    def test_force_bypasses_the_gate(
        self, store: WorktreeFleetStore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(git_ops, "add_worktree", lambda **kwargs: None)
        monkeypatch.setattr(git_ops, "is_dirty", lambda path: True)
        store.claim(
            repo_root=Path("/repo"),
            worktree_path=Path("/wt-a"),
            branch="a",
            owner="claude:s1",
            purpose="p",
            base_ref="main",
        )
        result = store.release(
            Path("/wt-a"),
            branch="a",
            base_ref="main",
            owner="claude:s1",
            force=True,
            verify_pushed=False,
        )
        assert result["released"] is True


class TestPrune:
    def test_prune_dry_run_reports_but_does_not_remove(
        self, store: WorktreeFleetStore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(git_ops, "add_worktree", lambda **kwargs: None)
        monkeypatch.setattr(git_ops, "is_dirty", lambda path: False)
        monkeypatch.setattr(
            git_ops,
            "remove_worktree",
            lambda **kwargs: (_ for _ in ()).throw(
                AssertionError("should not be called in dry_run")
            ),
        )
        store.claim(
            repo_root=Path("/repo"),
            worktree_path=Path("/wt-a"),
            branch="a",
            owner="claude:s1",
            purpose="p",
            base_ref="main",
        )
        store._mark_ready_to_merge_for_test(Path("/wt-a"))
        result = store.prune(dry_run=True, ttl_hours=0)
        assert any(r["path"] == "/wt-a" for r in result["would_remove"])
        assert store.get(Path("/wt-a")) is not None

    def test_prune_never_removes_active_worktrees(
        self, store: WorktreeFleetStore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(git_ops, "add_worktree", lambda **kwargs: None)
        store.claim(
            repo_root=Path("/repo"),
            worktree_path=Path("/wt-a"),
            branch="a",
            owner="claude:s1",
            purpose="p",
            base_ref="main",
        )
        result = store.prune(dry_run=False, ttl_hours=0)
        assert result["would_remove"] == []
        assert result["removed"] == []
        assert store.get(Path("/wt-a")) is not None


class TestReleaseOwnership:
    """Only the session that claimed a worktree may release it."""

    @pytest.fixture
    def claimed(self, store: WorktreeFleetStore, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(git_ops, "add_worktree", lambda **kwargs: None)
        monkeypatch.setattr(git_ops, "is_dirty", lambda path: False)
        store.claim(
            repo_root=Path("/repo"),
            worktree_path=Path("/wt-a"),
            branch="a",
            owner="claude:s1",
            purpose="p",
            base_ref="main",
        )
        return store

    def test_another_owner_cannot_release(self, claimed: WorktreeFleetStore) -> None:
        result = claimed.release(
            Path("/wt-a"), branch="a", base_ref="main", owner="claude:s2", verify_pushed=False
        )
        assert result["released"] is False
        assert "claude:s1" in result["reason"]
        assert claimed.get(Path("/wt-a"))["status"] == "active"

    def test_force_does_not_bypass_ownership(self, claimed: WorktreeFleetStore) -> None:
        result = claimed.release(
            Path("/wt-a"),
            branch="a",
            base_ref="main",
            owner="claude:s2",
            force=True,
            verify_pushed=False,
        )
        assert result["released"] is False
        assert claimed.get(Path("/wt-a"))["status"] == "active"

    def test_ownership_is_checked_before_git_is_touched(
        self, claimed: WorktreeFleetStore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def explode(path):
            raise AssertionError("git must not run for a non-owner")

        monkeypatch.setattr(git_ops, "is_dirty", explode)
        result = claimed.release(Path("/wt-a"), branch="a", base_ref="main", owner="claude:s2")
        assert result["released"] is False

    def test_owner_is_required(self, claimed: WorktreeFleetStore) -> None:
        with pytest.raises(TypeError):
            claimed.release(Path("/wt-a"), branch="a", base_ref="main")

    def test_the_owner_can_release(self, claimed: WorktreeFleetStore) -> None:
        result = claimed.release(
            Path("/wt-a"), branch="a", base_ref="main", owner="claude:s1", verify_pushed=False
        )
        assert result["released"] is True


class TestReleaseOnUnknownPushState:
    """release() must refuse when push_status could not determine the answer.

    UNKNOWN is returned when the base_ref does not resolve; treating it as
    "nothing to report" is what let a never-pushed worktree be released.
    """

    @pytest.fixture
    def claimed(self, store: WorktreeFleetStore, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(git_ops, "add_worktree", lambda **kwargs: None)
        monkeypatch.setattr(git_ops, "is_dirty", lambda path: False)
        store.claim(
            repo_root=Path("/repo"),
            worktree_path=Path("/wt-a"),
            branch="a",
            owner="claude:s1",
            purpose="p",
            base_ref="main",
        )
        return store

    def test_unknown_push_state_refuses_release(
        self, claimed: WorktreeFleetStore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from mcp_servers.worktree_fleet.git_ops import PushState, PushStatus

        monkeypatch.setattr(
            git_ops,
            "push_status",
            lambda **kwargs: PushStatus(
                PushState.UNKNOWN, reason="base_ref 'mian' does not resolve in this worktree"
            ),
        )
        result = claimed.release(Path("/wt-a"), branch="a", base_ref="mian", owner="claude:s1")
        assert result["released"] is False
        assert "mian" in result["reason"]
        assert claimed.get(Path("/wt-a"))["status"] == "active"


class TestReleaseGateIsAnAllowList:
    """Only states known to be safe release. A state added to PushState later must
    refuse until someone decides otherwise, not pass because nobody listed it.
    """

    def test_an_unrecognised_push_state_refuses(
        self, store: WorktreeFleetStore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(git_ops, "add_worktree", lambda **kwargs: None)
        monkeypatch.setattr(git_ops, "is_dirty", lambda path: False)
        monkeypatch.setattr(
            git_ops,
            "push_status",
            lambda **kwargs: git_ops.PushStatus("state_added_next_year", reason="new state"),
        )
        store.claim(
            repo_root=Path("/repo"),
            worktree_path=Path("/wt-a"),
            branch="a",
            owner="claude:s1",
            purpose="p",
            base_ref="main",
        )
        result = store.release(Path("/wt-a"), branch="a", base_ref="main", owner="claude:s1")
        assert result["released"] is False
        assert "new state" in result["reason"]
        assert store.get(Path("/wt-a"))["status"] == "active"


def _lock_is_held(db_path: Path) -> bool:
    """True if some other connection currently holds the write lock."""
    conn = sqlite3.connect(db_path, timeout=0.2, isolation_level=None)
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("ROLLBACK")
        return False
    except sqlite3.OperationalError:
        return True
    finally:
        conn.close()


class TestHeartbeatUnknownPath:
    """A heartbeat that updated nothing must not report success.

    Before the fix it affected 0 rows and returned normally, so a session
    heartbeating a path it never claimed (or one already pruned) believed it
    was registered.
    """

    def test_heartbeat_on_unregistered_path_raises(self, store: WorktreeFleetStore) -> None:
        with pytest.raises(KeyError, match="never-claimed"):
            store.heartbeat(Path("/never-claimed"))

    def test_heartbeat_on_registered_path_still_updates(
        self, store: WorktreeFleetStore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(git_ops, "add_worktree", lambda **kwargs: None)
        store.claim(
            repo_root=Path("/repo"),
            worktree_path=Path("/wt-a"),
            branch="a",
            owner="claude:s1",
            purpose="p",
            base_ref="main",
        )
        before = store.get(Path("/wt-a"))["last_seen_at"]
        store.heartbeat(Path("/wt-a"))
        assert store.get(Path("/wt-a"))["last_seen_at"] >= before


class TestPruneRemoval:
    """The destructive path itself — previously never executed by a test."""

    @pytest.fixture
    def closed_store(self, store: WorktreeFleetStore, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(git_ops, "add_worktree", lambda **kwargs: None)
        for name in ("a", "b"):
            store.claim(
                repo_root=Path("/repo"),
                worktree_path=Path(f"/wt-{name}"),
                branch=name,
                owner="claude:s1",
                purpose="p",
                base_ref="main",
            )
            store._mark_ready_to_merge_for_test(Path(f"/wt-{name}"))
        return store

    def test_expired_closed_worktree_is_removed_and_its_row_deleted(
        self, closed_store: WorktreeFleetStore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        removed_paths: list[str] = []
        monkeypatch.setattr(
            git_ops,
            "remove_worktree",
            lambda repo_root, worktree_path: removed_paths.append(str(worktree_path)),
        )
        result = closed_store.prune(dry_run=False, ttl_hours=0)
        assert sorted(removed_paths) == ["/wt-a", "/wt-b"]
        assert [c["path"] for c in result["removed"]] == sorted(
            c["path"] for c in result["removed"]
        )
        assert closed_store.get(Path("/wt-a")) is None
        assert closed_store.get(Path("/wt-b")) is None

    def test_one_failing_removal_does_not_abort_the_batch(
        self, closed_store: WorktreeFleetStore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def fake_remove(repo_root: Path, worktree_path: Path) -> None:
            if str(worktree_path) == "/wt-a":
                raise subprocess.CalledProcessError(
                    128, ["git", "worktree", "remove"], "", "fatal: contains modified files"
                )

        monkeypatch.setattr(git_ops, "remove_worktree", fake_remove)
        result = closed_store.prune(dry_run=False, ttl_hours=0)

        assert [c["path"] for c in result["removed"]] == ["/wt-b"]
        assert closed_store.get(Path("/wt-b")) is None
        # The failure is reported with git's own message, and its row survives
        # so the worktree is not silently forgotten.
        assert [f["path"] for f in result["failed"]] == ["/wt-a"]
        assert "modified files" in result["failed"][0]["error"]
        assert closed_store.get(Path("/wt-a"))["status"] == "ready_to_merge"


class TestClaimDoesNotHoldTheLockDuringGit:
    """`git worktree add` is a full checkout, not "a few ms".

    Holding the cross-process write lock for its duration blocks every other
    session's claim/heartbeat/release until it finishes or the 30s timeout
    turns into sqlite3.OperationalError.
    """

    def test_lock_is_free_while_git_runs(
        self, store: WorktreeFleetStore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        observed: list[bool] = []

        def fake_add(**kwargs: object) -> None:
            observed.append(_lock_is_held(store.db_path))

        monkeypatch.setattr(git_ops, "add_worktree", fake_add)
        store.claim(
            repo_root=Path("/repo"),
            worktree_path=Path("/wt-a"),
            branch="a",
            owner="claude:s1",
            purpose="p",
            base_ref="main",
        )
        assert observed == [False], "write lock was held while git ran"

    def test_failed_git_leaves_no_registry_row(
        self, store: WorktreeFleetStore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def boom(**kwargs: object) -> None:
            raise subprocess.CalledProcessError(
                128, ["git", "worktree", "add"], "", "fatal: exists"
            )

        monkeypatch.setattr(git_ops, "add_worktree", boom)
        with pytest.raises(subprocess.CalledProcessError):
            store.claim(
                repo_root=Path("/repo"),
                worktree_path=Path("/wt-a"),
                branch="a",
                owner="claude:s1",
                purpose="p",
                base_ref="main",
            )
        assert store.get(Path("/wt-a")) is None
        # and the branch is claimable again afterwards
        monkeypatch.setattr(git_ops, "add_worktree", lambda **kwargs: None)
        assert (
            store.claim(
                repo_root=Path("/repo"),
                worktree_path=Path("/wt-a"),
                branch="a",
                owner="claude:s1",
                purpose="p",
                base_ref="main",
            )["status"]
            == "active"
        )


class TestWorktreePathContainment:
    """Where a worktree may live, and one directory = one registry row.

    A relative path resolved against the server's CWD created a worktree
    INSIDE the main checkout (it then shows up as untracked in every
    tree-clean and deploy-completeness gate), and the registry keyed on the
    unresolved string, so /tmp/x and /private/tmp/x were two rows for one
    directory.
    """

    @pytest.fixture
    def repo_root(self, tmp_path: Path) -> Path:
        root = tmp_path / "DevSkyy"
        (root / ".claude" / "worktrees").mkdir(parents=True)
        return root

    @pytest.fixture
    def noop_git(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(git_ops, "add_worktree", lambda **kwargs: None)

    def _claim(self, store: WorktreeFleetStore, repo_root: Path, path: Path, branch: str = "a"):
        return store.claim(
            repo_root=repo_root,
            worktree_path=path,
            branch=branch,
            owner="claude:s1",
            purpose="p",
            base_ref="main",
        )

    def test_relative_path_is_refused(
        self, store: WorktreeFleetStore, repo_root: Path, noop_git: None
    ) -> None:
        with pytest.raises(ValueError, match="absolute"):
            self._claim(store, repo_root, Path("nested-wt"))

    def test_path_inside_the_checkout_is_refused(
        self, store: WorktreeFleetStore, repo_root: Path, noop_git: None
    ) -> None:
        with pytest.raises(ValueError, match="inside the checkout"):
            self._claim(store, repo_root, repo_root / "nested-wt")

    def test_sibling_of_repo_root_is_allowed(
        self, store: WorktreeFleetStore, repo_root: Path, noop_git: None
    ) -> None:
        row = self._claim(store, repo_root, repo_root.parent / "DevSkyy-wt-a")
        assert row["path"] == str(repo_root.parent / "DevSkyy-wt-a")

    def test_dot_claude_worktrees_is_allowed(
        self, store: WorktreeFleetStore, repo_root: Path, noop_git: None
    ) -> None:
        """Every live claim in this repo sits here, and it is gitignored."""
        path = repo_root / ".claude" / "worktrees" / "hooks-cutover"
        row = self._claim(store, repo_root, path)
        assert row["path"] == str(path)

    def test_one_directory_is_one_row_through_a_symlink(
        self, store: WorktreeFleetStore, repo_root: Path, tmp_path: Path, noop_git: None
    ) -> None:
        real = repo_root.parent / "DevSkyy-wt-a"
        real.mkdir()
        link_parent = tmp_path / "link"
        link_parent.symlink_to(repo_root.parent, target_is_directory=True)
        self._claim(store, repo_root, link_parent / "DevSkyy-wt-a")
        assert store.get(real) is not None, "symlinked path registered a second row"
