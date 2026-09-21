"""Atomic worktree ownership registry.

`git worktree list` alone doesn't say who owns a worktree, why it exists, or
whether its work already reached a branch elsewhere — that's exactly the
manifest every past stranded-worktree sweep had to reconstruct by hand. This
registry answers those questions and gates removal on git's own truth
(dirty/pushed state), never on trust.
"""

from __future__ import annotations

import sqlite3
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from mcp_servers._shared import locked_transaction
from mcp_servers.worktree_fleet import git_ops
from mcp_servers.worktree_fleet.git_ops import PushState

ACTIVE_STATUSES = ("active",)
CLOSED_STATUSES = ("ready_to_merge", "merged")


class ClaimConflictError(Exception):
    """A branch or path is already claimed by a different owner."""


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def _resolved(worktree_path: Path) -> Path:
    """One directory must be one registry row.

    The registry keys on the path string, so an unresolved path let
    /tmp/x and /private/tmp/x (or any symlinked parent) register twice for one
    directory — and a later lookup by the other spelling found nothing.
    """
    return Path(worktree_path).expanduser().resolve()


def _validated_worktree_path(repo_root: Path, worktree_path: Path) -> Path:
    """Resolve a claim's path and confirm it is somewhere a worktree may live.

    A relative path resolved against the server process's CWD, which put a
    worktree INSIDE the checkout, where it shows up as untracked in every
    tree-clean and deploy-source-completeness gate. Two locations are allowed:
    a sibling of the repo root (the tool's own default) and the gitignored
    <repo>/.claude/worktrees/ directory, where this repo's live claims sit.
    """
    if not Path(worktree_path).is_absolute():
        raise ValueError(
            f"worktree_path must be an absolute path, got {str(worktree_path)!r} — "
            "a relative path would resolve against the server's working directory"
        )
    resolved = _resolved(worktree_path)
    repo_root = _resolved(repo_root)
    worktrees_dir = repo_root / ".claude" / "worktrees"
    if resolved.is_relative_to(worktrees_dir) and resolved != worktrees_dir:
        return resolved
    if resolved.parent == repo_root.parent and resolved != repo_root:
        return resolved
    if resolved.is_relative_to(repo_root):
        raise ValueError(
            f"worktree_path {str(resolved)!r} is inside the checkout ({repo_root}); only "
            f"{worktrees_dir} is allowed there — anywhere else pollutes the working tree"
        )
    raise ValueError(
        f"worktree_path {str(resolved)!r} must be a sibling of the repo root "
        f"({repo_root.parent}) or live under {worktrees_dir}"
    )


class WorktreeFleetStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        with locked_transaction(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS worktrees (
                    path TEXT PRIMARY KEY,
                    branch TEXT NOT NULL,
                    repo_root TEXT NOT NULL,
                    owner TEXT NOT NULL,
                    purpose TEXT,
                    status TEXT NOT NULL DEFAULT 'active'
                        CHECK (status IN ('active','ready_to_merge','merged','abandoned')),
                    created_at TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL,
                    closed_at TEXT
                )
                """)

    def _connect_ro(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ------------------------------------------------------------------
    # Claim / heartbeat / list
    # ------------------------------------------------------------------

    def claim(
        self,
        repo_root: Path,
        worktree_path: Path,
        branch: str,
        owner: str,
        purpose: str,
        base_ref: str,
    ) -> dict[str, Any]:
        worktree_path = _validated_worktree_path(repo_root, worktree_path)
        path_str = str(worktree_path)
        with locked_transaction(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            existing_by_path = conn.execute(
                "SELECT * FROM worktrees WHERE path = ?", (path_str,)
            ).fetchone()
            if existing_by_path is not None:
                if existing_by_path["branch"] == branch and existing_by_path["owner"] == owner:
                    conn.execute(
                        "UPDATE worktrees SET last_seen_at = ? WHERE path = ?", (_now(), path_str)
                    )
                    return _row_to_dict(
                        conn.execute(
                            "SELECT * FROM worktrees WHERE path = ?", (path_str,)
                        ).fetchone()
                    )
                raise ClaimConflictError(
                    f"{path_str} is already registered for branch {existing_by_path['branch']!r} "
                    f"owned by {existing_by_path['owner']!r}"
                )

            existing_by_branch = conn.execute(
                "SELECT * FROM worktrees WHERE branch = ? AND status NOT IN ('merged')", (branch,)
            ).fetchone()
            if existing_by_branch is not None:
                raise ClaimConflictError(
                    f"branch {branch!r} is already claimed at {existing_by_branch['path']!r} "
                    f"owned by {existing_by_branch['owner']!r}"
                )

            now = _now()
            conn.execute(
                """
                INSERT INTO worktrees (path, branch, repo_root, owner, purpose, status, created_at, last_seen_at)
                VALUES (?, ?, ?, ?, ?, 'active', ?, ?)
                """,
                (path_str, branch, str(repo_root), owner, purpose, now, now),
            )

        # git runs OUTSIDE the lock: `git worktree add` is a full checkout, not
        # the "few ms" locked_transaction is sized for, and holding the
        # cross-process write lock for it blocks every other session's
        # claim/heartbeat/release until it finishes or times out. The row
        # inserted above already reserves the claim, so a concurrent session
        # still loses the race; if git fails we delete it and re-raise, leaving
        # the branch claimable again.
        try:
            git_ops.add_worktree(
                repo_root=repo_root, worktree_path=worktree_path, branch=branch, base_ref=base_ref
            )
        except BaseException:
            with locked_transaction(self.db_path) as conn:
                conn.execute("DELETE FROM worktrees WHERE path = ?", (path_str,))
            raise

        row = self.get(worktree_path)
        if row is None:
            raise ClaimConflictError(
                f"the claim row for {path_str} disappeared while git ran — another process "
                "removed it; the worktree may exist on disk without a registry entry"
            )
        return row

    def heartbeat(self, worktree_path: Path) -> None:
        path_str = str(_resolved(worktree_path))
        with locked_transaction(self.db_path) as conn:
            cursor = conn.execute(
                "UPDATE worktrees SET last_seen_at = ? WHERE path = ?", (_now(), path_str)
            )
            if cursor.rowcount == 0:
                # Updating nothing is not success: the caller believes it holds
                # a claim it never made, or one prune() already removed.
                raise KeyError(f"no worktree registered at {path_str}")

    def get(self, worktree_path: Path) -> dict[str, Any] | None:
        conn = self._connect_ro()
        try:
            row = conn.execute(
                "SELECT * FROM worktrees WHERE path = ?", (str(_resolved(worktree_path)),)
            ).fetchone()
            return _row_to_dict(row) if row else None
        finally:
            conn.close()

    def list(self, status: str | None = None, owner: str | None = None) -> list[dict[str, Any]]:
        conn = self._connect_ro()
        try:
            query = "SELECT * FROM worktrees WHERE 1=1"
            params: list[str] = []
            if status:
                query += " AND status = ?"
                params.append(status)
            if owner:
                query += " AND owner = ?"
                params.append(owner)
            rows = conn.execute(query, params).fetchall()
            return [_row_to_dict(r) for r in rows]
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Release — fail-closed by default
    # ------------------------------------------------------------------

    def release(
        self,
        worktree_path: Path,
        branch: str,
        base_ref: str,
        owner: str,
        verify_pushed: bool = True,
        force: bool = False,
    ) -> dict[str, Any]:
        row = self.get(worktree_path)
        if row is None:
            raise KeyError(f"no worktree registered at {worktree_path}")

        # Checked first and never bypassed by force: force waives the dirty/unpushed
        # gate for your own worktree, not the ownership of someone else's. A dead
        # session's claim is reclaimed by prune() once it passes the TTL.
        if row["owner"] != owner:
            return {
                "released": False,
                "reason": f"worktree is owned by {row['owner']!r}, not {owner!r}",
            }

        if not force:
            if git_ops.is_dirty(worktree_path):
                return {"released": False, "reason": "worktree has uncommitted changes (dirty)"}

            if verify_pushed:
                status = git_ops.push_status(
                    worktree_path=worktree_path, branch=branch, base_ref=base_ref
                )
                # Allow-list: only states known to be safe release. UNKNOWN (the
                # check could not run, e.g. base_ref does not resolve) refuses, and so
                # does any state added later until it is listed here on purpose.
                if status.state not in (PushState.UP_TO_DATE, PushState.NO_NEW_COMMITS):
                    detail = "; ".join(status.unpushed_commits)
                    reason = f"{status.reason}: {detail}" if detail else status.reason
                    return {"released": False, "reason": reason}

        self._set_status(worktree_path, "ready_to_merge", closed_at=_now())
        return {"released": True, "status": "ready_to_merge"}

    def _set_status(self, worktree_path: Path, status: str, closed_at: str | None = None) -> None:
        with locked_transaction(self.db_path) as conn:
            conn.execute(
                "UPDATE worktrees SET status = ?, closed_at = COALESCE(?, closed_at) WHERE path = ?",
                (status, closed_at, str(_resolved(worktree_path))),
            )

    def _mark_ready_to_merge_for_test(self, worktree_path: Path) -> None:
        """Test-only shortcut to reach a closed state without re-mocking the
        full release() gate in every prune test.
        """
        self._set_status(worktree_path, "ready_to_merge", closed_at=_now())

    # ------------------------------------------------------------------
    # Prune — only removes rows already in a closed state, past the TTL
    # ------------------------------------------------------------------

    def prune(self, dry_run: bool = True, ttl_hours: int = 24) -> dict[str, Any]:
        now = datetime.now(UTC)
        placeholders = ", ".join("?" for _ in CLOSED_STATUSES)
        conn = self._connect_ro()
        try:
            closed_rows = conn.execute(
                f"SELECT * FROM worktrees WHERE status IN ({placeholders})", CLOSED_STATUSES
            ).fetchall()
            active_rows = conn.execute(
                f"SELECT * FROM worktrees WHERE status IN ({', '.join('?' for _ in ACTIVE_STATUSES)})",
                ACTIVE_STATUSES,
            ).fetchall()
        finally:
            conn.close()

        candidates = []
        for row in closed_rows:
            closed_at = row["closed_at"]
            if not closed_at:
                continue
            age_hours = (now - datetime.fromisoformat(closed_at)).total_seconds() / 3600
            if age_hours >= ttl_hours:
                candidates.append(_row_to_dict(row))

        # Never removed — just surfaced so a human/agent can decide, per the
        # "stranded commits != stranded work" lesson (three separate manual
        # sweeps in project history) this registry exists to stop repeating.
        abandoned_candidates = []
        for row in active_rows:
            age_hours = (now - datetime.fromisoformat(row["last_seen_at"])).total_seconds() / 3600
            if age_hours >= ttl_hours:
                abandoned_candidates.append(_row_to_dict(row))

        if dry_run:
            return {
                "would_remove": candidates,
                "removed": [],
                "failed": [],
                "abandoned_candidates": abandoned_candidates,
            }

        removed = []
        failed = []
        for candidate in candidates:
            path = Path(candidate["path"])
            try:
                git_ops.remove_worktree(repo_root=Path(candidate["repo_root"]), worktree_path=path)
            except subprocess.CalledProcessError as exc:
                # One candidate git refuses (e.g. dirtied after release) must not
                # abandon the rest of the batch, and git's own message is the
                # only thing that says why. Its row stays, so the worktree is
                # reported rather than silently forgotten.
                failed.append(
                    {
                        "path": candidate["path"],
                        "error": (exc.stderr or "").strip() or f"git exited {exc.returncode}",
                    }
                )
                continue
            with locked_transaction(self.db_path) as conn:
                conn.execute("DELETE FROM worktrees WHERE path = ?", (candidate["path"],))
            removed.append(candidate)

        return {
            "would_remove": [],
            "removed": removed,
            "failed": failed,
            "abandoned_candidates": abandoned_candidates,
        }
