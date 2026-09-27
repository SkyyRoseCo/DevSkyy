"""worktree-fleet MCP tools: claim, heartbeat, list, release, prune."""

from __future__ import annotations

import subprocess
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from mcp_servers._shared import ResponseFormat, format_response
from mcp_servers.worktree_fleet.server import DB_PATH, REPO_ROOT, logger, mcp
from mcp_servers.worktree_fleet.store import ClaimConflictError, WorktreeFleetStore

_store = WorktreeFleetStore(db_path=DB_PATH)


class BaseInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class ClaimInput(BaseInput):
    branch: str = Field(..., min_length=1, max_length=200)
    purpose: str = Field(..., min_length=1, max_length=500)
    owner: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Caller-supplied session/agent id, e.g. 'claude:37b5c934'.",
    )
    base_ref: str = Field(default="main", max_length=200)
    worktree_path: str | None = Field(
        default=None, description="Defaults to a sibling of the repo root named after the branch."
    )


class HeartbeatInput(BaseInput):
    path: str = Field(..., min_length=1)


class ListInput(BaseInput):
    status: str | None = Field(default=None)
    owner: str | None = Field(default=None)


class ReleaseInput(BaseInput):
    path: str = Field(..., min_length=1)
    branch: str = Field(..., min_length=1, max_length=200)
    owner: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Must match the owner that claimed this worktree; force does not waive it.",
    )
    base_ref: str = Field(default="main", max_length=200)
    verify_pushed: bool = Field(default=True)
    force: bool = Field(
        default=False,
        description="Bypasses the dirty/unpushed gate. Data-loss risk — the calling agent must "
        "already have explicit human confirmation before setting this; the tool cannot pause "
        "mid-call to ask.",
    )


class PruneInput(BaseInput):
    dry_run: bool = Field(default=True)
    ttl_hours: int = Field(default=24, ge=0)


def _default_worktree_path(branch: str) -> str:
    safe = branch.replace("/", "-")
    return str(REPO_ROOT.parent / f"{REPO_ROOT.name}-wt-{safe}")


@mcp.tool(
    name="worktree_claim",
    annotations={
        "title": "Claim a git worktree for a branch (atomic across processes)",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def worktree_claim(params: ClaimInput) -> str:
    """Refuses if the branch is already claimed by a different owner — the
    actual race fix: two sessions requesting the same branch at once, only
    one wins. Re-claiming your own already-claimed branch is idempotent.
    """
    worktree_path = Path(params.worktree_path or _default_worktree_path(params.branch))
    try:
        row = _store.claim(
            repo_root=REPO_ROOT,
            worktree_path=worktree_path,
            branch=params.branch,
            owner=params.owner,
            purpose=params.purpose,
            base_ref=params.base_ref,
        )
    except (ClaimConflictError, ValueError) as exc:
        return format_response({"error": str(exc)}, params.response_format, "Claim refused")
    except subprocess.CalledProcessError as exc:
        # git itself refused (path exists, branch checked out elsewhere...).
        # Its stderr is the only thing that says why, and FastMCP's generic
        # wrapper drops it.
        return format_response(
            {"error": (exc.stderr or "").strip() or f"git exited {exc.returncode}"},
            params.response_format,
            "Claim failed",
        )
    logger.info(
        "worktree_claim path=%s branch=%s owner=%s", row["path"], row["branch"], row["owner"]
    )
    return format_response(row, params.response_format, "Worktree claimed")


@mcp.tool(
    name="worktree_heartbeat",
    annotations={
        "title": "Mark a claimed worktree as still actively worked",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def worktree_heartbeat(params: HeartbeatInput) -> str:
    try:
        _store.heartbeat(Path(params.path))
    except KeyError as exc:
        # Updating no row is not a heartbeat: say so instead of reporting ok.
        return format_response(
            {"error": str(exc).strip("'\"")}, params.response_format, "Heartbeat failed"
        )
    return format_response(
        {"ok": True, "path": params.path}, params.response_format, "Heartbeat recorded"
    )


@mcp.tool(
    name="worktree_list",
    annotations={
        "title": "List registered worktrees, optionally filtered",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def worktree_list(params: ListInput) -> str:
    rows = _store.list(status=params.status, owner=params.owner)
    return format_response(
        {"count": len(rows), "worktrees": rows}, params.response_format, "Registered worktrees"
    )


@mcp.tool(
    name="worktree_release",
    annotations={
        "title": "Release a worktree — fail-closed unless clean and pushed",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def worktree_release(params: ReleaseInput) -> str:
    """Refuses by default unless the worktree is both clean (`git status
    --porcelain` empty) and pushed (no commits missing from a remote). On
    refusal, the response names exactly what's dirty or unpushed.
    """
    try:
        result = _store.release(
            worktree_path=Path(params.path),
            branch=params.branch,
            base_ref=params.base_ref,
            owner=params.owner,
            verify_pushed=params.verify_pushed,
            force=params.force,
        )
    except (KeyError, ValueError) as exc:
        return format_response({"error": str(exc)}, params.response_format, "Release failed")
    title = "Worktree released" if result["released"] else "Release refused"
    return format_response(result, params.response_format, title)


@mcp.tool(
    name="worktree_prune",
    annotations={
        "title": "Remove closed worktrees past their TTL (dry-run by default)",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def worktree_prune(params: PruneInput) -> str:
    """Only ever removes rows already marked ready_to_merge/merged by a prior
    worktree_release. Anything that looks abandoned (active status, no
    heartbeat past the TTL) is reported under abandoned_candidates and never
    touched — a human or agent decides what to do with those.
    """
    result = _store.prune(dry_run=params.dry_run, ttl_hours=params.ttl_hours)
    logger.info(
        "worktree_prune dry_run=%s would_remove=%d removed=%d failed=%d abandoned=%d",
        params.dry_run,
        len(result["would_remove"]),
        len(result["removed"]),
        len(result["failed"]),
        len(result["abandoned_candidates"]),
    )
    return format_response(result, params.response_format, "Prune result")
