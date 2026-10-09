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
    # Prune — only removes rows already in a closed state, past the TTL,
    # plus orphans (folder gone) whose work is provably on a remote
    # ------------------------------------------------------------------

    def prune(self, dry_run: bool = True, ttl_hours: int = 24) -> dict[str, Any]:
        conn = self._connect_ro()
        try:
            rows = [_row_to_dict(r) for r in conn.execute("SELECT * FROM worktrees").fetchall()]
        finally:
            conn.close()
        now = datetime.now(UTC)
        due = [r for r in rows if (age := _age_hours(r, now)) is not None and age >= ttl_hours]

        candidates: list[dict[str, Any]] = []
        # Never removed — just surfaced so a human/agent can decide, per the
        # "stranded commits != stranded work" lesson (three separate manual
        # sweeps in project history) this registry exists to stop repeating.
        abandoned_candidates: list[dict[str, Any]] = []
        orphans: list[dict[str, Any]] = []
        orphaned_unverifiable: list[dict[str, Any]] = []
        registered: dict[str, set[str] | Exception] = {}
        for row in due:
            reason = _orphan_verdict(row, registered)
            if reason is None:
                orphans.append(row)
            elif reason:
                orphaned_unverifiable.append({**row, "reason": reason})
            elif row["status"] in CLOSED_STATUSES:
                candidates.append(row)
            elif row["status"] in ACTIVE_STATUSES:
                abandoned_candidates.append(row)

        result: dict[str, Any] = {
            "would_remove": [],
            "removed": [],
            "failed": [],
            "abandoned_candidates": abandoned_candidates,
            "would_remove_orphaned": [],
            "removed_orphaned": [],
            "orphaned_unverifiable": orphaned_unverifiable,
        }
        if dry_run:
            return {**result, "would_remove": candidates, "would_remove_orphaned": orphans}
        removed, failed = self._remove_closed(candidates)
        return {
            **result,
            "removed": removed,
            "failed": failed,
            "removed_orphaned": self._delete_orphan_rows(orphans),
        }

    def _remove_closed(
        self, candidates: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
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
        return removed, failed

    def _delete_orphan_rows(self, orphans: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Delete only the row that was judged: a session that re-claimed the
        same path between the check and now has a new last_seen_at/status, and
        its row must survive."""
        removed = []
        with locked_transaction(self.db_path) as conn:
            for row in orphans:
                cursor = conn.execute(
                    "DELETE FROM worktrees WHERE path = ? AND status = ? AND last_seen_at = ?",
                    (row["path"], row["status"], row["last_seen_at"]),
                )
                if cursor.rowcount:
                    removed.append(row)
        return removed


def _age_hours(row: dict[str, Any], now: datetime) -> float | None:
    """Closed rows age from closed_at, active rows from their last heartbeat.
    A closed row with no closed_at has no age and is never due."""
    stamp = row["closed_at"] if row["status"] in CLOSED_STATUSES else row["last_seen_at"]
    if not stamp:
        return None
    return (now - datetime.fromisoformat(stamp)).total_seconds() / 3600


def _orphan_verdict(row: dict[str, Any], registered: dict[str, set[str] | Exception]) -> str | None:
    """Classify a due row by whether its worktree folder still exists.

    Returns "" when it is not an orphan (folder present, or git still lists the
    worktree), None when it is an orphan safe to forget, and a non-empty reason
    when it is an orphan that must be kept. Deleting the row loses no commits —
    the branch outlives it — but an active row is the only record that unpushed
    work exists, so it goes only once the branch is shown to be on a remote. A
    closed row already passed release()'s clean-and-pushed gate.
    """
    path = Path(row["path"])
    if path.exists():
        return ""
    repo_root = row["repo_root"]
    if repo_root not in registered:
        try:
            # A "prunable" entry is git saying the folder is gone: still
            # listed, no longer a worktree anyone can work in.
            registered[repo_root] = {
                str(_resolved(Path(w["path"])))
                for w in git_ops.list_worktrees(repo_root=Path(repo_root))
                if "prunable" not in w
            }
        except (subprocess.CalledProcessError, OSError) as exc:
            registered[repo_root] = exc
    listed = registered[repo_root]
    if isinstance(listed, Exception):
        return f"could not list git worktrees in {repo_root}: {_error_text(listed)}"
    if str(_resolved(path)) in listed:
        return ""
    if row["status"] in CLOSED_STATUSES:
        return None
    try:
        off_remotes = git_ops.branch_commits_off_remotes(
            repo_root=Path(repo_root), branch=row["branch"]
        )
    except (subprocess.CalledProcessError, OSError, ValueError) as exc:
        return f"could not check branch {row['branch']!r}: {_error_text(exc)}"
    if off_remotes is None:
        return f"branch {row['branch']!r} exists neither locally nor on any remote"
    if off_remotes:
        return f"{len(off_remotes)} commit(s) on no remote: " + "; ".join(off_remotes)
    return None


def _error_text(exc: Exception) -> str:
    if isinstance(exc, subprocess.CalledProcessError):
        return (exc.stderr or "").strip() or f"git exited {exc.returncode}"
    return str(exc)
