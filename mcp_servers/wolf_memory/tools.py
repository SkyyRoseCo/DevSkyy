"""wolf-memory MCP tools: bug_next_id, bug_log, bug_bump, bug_search, cerebrum_append."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from mcp_servers._shared import ResponseFormat, format_response
from mcp_servers.wolf_memory.server import BUGLOG_PATH, CEREBRUM_PATH, LOCK_DB_PATH, logger, mcp
from mcp_servers.wolf_memory.store import WolfMemoryStore, validate_cerebrum_entry

_store = WolfMemoryStore(
    buglog_path=BUGLOG_PATH, lock_db_path=LOCK_DB_PATH, cerebrum_path=CEREBRUM_PATH
)


class BaseInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)


class BugNextIdInput(BaseInput):
    pass


class BugLogInput(BaseInput):
    error_message: str = Field(..., min_length=1, max_length=4000)
    file: str = Field(..., min_length=1, max_length=500)
    root_cause: str = Field(..., min_length=1, max_length=2000)
    fix: str = Field(..., min_length=1, max_length=2000)
    tags: list[str] = Field(default_factory=list)
    related_bugs: list[str] = Field(default_factory=list)


class BugBumpInput(BaseInput):
    id: str = Field(..., pattern=r"^bug-\d+$")


class BugSearchInput(BaseInput):
    query: str = Field(default="", max_length=500)
    tags: list[str] = Field(default_factory=list)
    min_occurrences: int | None = Field(default=None, ge=1)


CerebrumSection = Literal["User Preferences", "Key Learnings", "Do-Not-Repeat", "Decision Log"]


class CerebrumAppendInput(BaseInput):
    section: CerebrumSection
    entry: str = Field(..., min_length=1, max_length=2000)

    @field_validator("entry")
    @classmethod
    def _single_line_no_heading(cls, value: str) -> str:
        # Same rule the store enforces; here it fails at the tool boundary
        # with a validation error instead of a mid-call ValueError.
        return validate_cerebrum_entry(value)


@mcp.tool(
    name="bug_next_id",
    annotations={
        "title": "Allocate the next bug-NNN id (atomic across processes)",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def bug_next_id(params: BugNextIdInput) -> str:
    """Replaces `python scripts/wolf_bug_id.py`'s scan-and-guess with a real atomic
    increment — the documented cause of past cross-session ID collisions.
    Does not write a buglog.json entry; use bug_log for that.
    """
    new_id = _store.next_bug_id()
    logger.info("bug_next_id allocated=%s", new_id)
    return format_response({"id": new_id}, params.response_format, "Next bug id")


@mcp.tool(
    name="bug_log",
    annotations={
        "title": "Log a bug to .wolf/buglog.json (atomic; bumps near-duplicates instead of duplicating)",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def bug_log(params: BugLogInput) -> str:
    """Appends a new entry, or bumps occurrences on a near-duplicate (same file,
    highly similar error_message) per OPENWOLF.md's "bump, don't duplicate" rule.
    """
    entry = _store.bug_log(
        error_message=params.error_message,
        file=params.file,
        root_cause=params.root_cause,
        fix=params.fix,
        tags=params.tags,
        related_bugs=params.related_bugs,
    )
    logger.info("bug_log id=%s file=%s", entry["id"], params.file)
    return format_response(entry, params.response_format, "Bug logged")


@mcp.tool(
    name="bug_bump",
    annotations={
        "title": "Bump occurrences + last_seen on an existing bug entry",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def bug_bump(params: BugBumpInput) -> str:
    """Returns `_recurring_sync_needed: true` once occurrences crosses the
    threshold (>=2) — surfaces the fact instead of relying on the caller to
    remember to run scripts/wolf_recurring_sync.py. The existing Stop hook
    stays the actual sync trigger; this tool only makes the crossing visible.
    """
    try:
        entry = _store.bug_bump(params.id)
    except KeyError as exc:
        return format_response({"error": str(exc)}, params.response_format, "Bug bump failed")
    logger.info("bug_bump id=%s occurrences=%s", entry["id"], entry["occurrences"])
    return format_response(entry, params.response_format, "Bug bumped")


@mcp.tool(
    name="bug_search",
    annotations={
        "title": "Search .wolf/buglog.json by text/tags/occurrence threshold",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def bug_search(params: BugSearchInput) -> str:
    """The "read buglog before fixing" step as one scoped call instead of a
    full 337KB-file read.
    """
    results = _store.bug_search(
        params.query, tags=params.tags or None, min_occurrences=params.min_occurrences
    )
    return format_response(
        {"count": len(results), "results": results},
        params.response_format,
        "Bug search results",
    )


@mcp.tool(
    name="cerebrum_append",
    annotations={
        "title": "Append a bullet under a cerebrum.md section (enum-validated)",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def cerebrum_append(params: CerebrumAppendInput) -> str:
    """Section must be one of: User Preferences, Key Learnings, Do-Not-Repeat,
    Decision Log. The fixed set makes misfiling structurally impossible
    instead of relying on picking the right heading by hand.
    """
    try:
        _store.cerebrum_append(params.section, params.entry)
    except ValueError as exc:
        return format_response(
            {"error": str(exc)}, params.response_format, "Cerebrum append failed"
        )
    logger.info("cerebrum_append section=%s", params.section)
    return format_response(
        {"ok": True, "section": params.section},
        params.response_format,
        "Cerebrum updated",
    )
