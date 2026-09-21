"""Tests for the worktree-fleet TOOL layer — the error mapping, specifically.

The store raises; the tool must turn that into a structured response an agent
can read. An exception escaping here reaches the agent as FastMCP's generic
"Error executing tool ..." wrapper, which drops git's own message.

conftest.py points the server modules at a throwaway directory, so importing
tools never touches this checkout's live .wolf/fleet.db.
"""

from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path

import pytest

from mcp_servers.worktree_fleet import git_ops, tools
from mcp_servers.worktree_fleet.store import WorktreeFleetStore


@pytest.fixture
def tool_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> WorktreeFleetStore:
    store = WorktreeFleetStore(db_path=tmp_path / "fleet.db")
    monkeypatch.setattr(tools, "_store", store)
    return store


def run(coro) -> str:
    return asyncio.run(coro)


class TestHeartbeatToolMapsFailure:
    def test_unregistered_path_reports_an_error_not_ok(
        self, tool_store: WorktreeFleetStore
    ) -> None:
        out = run(tools.worktree_heartbeat(tools.HeartbeatInput(path="/never-claimed")))
        assert "no worktree registered" in out
        assert "ok" not in out.lower().split("error")[0]

    def test_registered_path_still_reports_ok(
        self, tool_store: WorktreeFleetStore, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(git_ops, "add_worktree", lambda **kwargs: None)
        repo_root = tmp_path / "DevSkyy"
        repo_root.mkdir()
        wt = tmp_path / "DevSkyy-wt-a"
        tool_store.claim(
            repo_root=repo_root,
            worktree_path=wt,
            branch="a",
            owner="claude:s1",
            purpose="p",
            base_ref="main",
        )
        out = run(tools.worktree_heartbeat(tools.HeartbeatInput(path=str(wt))))
        assert "Heartbeat recorded" in out


class TestClaimToolMapsGitFailure:
    def test_git_failure_returns_gits_message(
        self, tool_store: WorktreeFleetStore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def boom(**kwargs: object) -> None:
            raise subprocess.CalledProcessError(
                128, ["git", "worktree", "add"], "", "fatal: destination path already exists"
            )

        monkeypatch.setattr(git_ops, "add_worktree", boom)
        monkeypatch.setattr(tools, "REPO_ROOT", Path("/repo"))
        out = run(
            tools.worktree_claim(
                tools.ClaimInput(branch="a", purpose="p", owner="claude:s1", worktree_path="/wt-a")
            )
        )
        assert "destination path already exists" in out


class TestPruneToolReportsFailures:
    def test_failed_removals_appear_in_the_response(
        self, tool_store: WorktreeFleetStore, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(git_ops, "add_worktree", lambda **kwargs: None)
        tool_store.claim(
            repo_root=Path("/repo"),
            worktree_path=Path("/wt-a"),
            branch="a",
            owner="claude:s1",
            purpose="p",
            base_ref="main",
        )
        tool_store._mark_ready_to_merge_for_test(Path("/wt-a"))

        def refuse(repo_root: Path, worktree_path: Path) -> None:
            raise subprocess.CalledProcessError(
                128, ["git", "worktree", "remove"], "", "fatal: contains modified files"
            )

        monkeypatch.setattr(git_ops, "remove_worktree", refuse)
        out = run(tools.worktree_prune(tools.PruneInput(dry_run=False, ttl_hours=0)))
        assert "contains modified files" in out
        assert tool_store.get(Path("/wt-a")) is not None
