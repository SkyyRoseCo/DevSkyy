"""Shared helpers for standalone DevSkyy MCP servers (wolf_memory, worktree_fleet).

Deliberately does not import mcp_tools.security.secure_tool or
mcp_tools.api_client._format_response: both transitively import
mcp_tools.server, which constructs the devskyy FastMCP app as an import side
effect. These servers exist specifically to have zero dependency on that app
or its backend, so the small pieces worth reusing (response formatting, a
darwin fork-safety guard, a cross-process SQLite mutex) are reimplemented
here instead.
"""

from __future__ import annotations

import contextlib
import json
import os
import sqlite3
import sys
import time
import uuid
from collections.abc import Iterator
from enum import StrEnum
from pathlib import Path
from typing import Any

CHARACTER_LIMIT = 25000


class ResponseFormat(StrEnum):
    MARKDOWN = "markdown"
    JSON = "json"


def apply_darwin_fork_safety() -> None:
    """bug-263: set before any subprocess/httpx-touching import.

    On darwin, once Network.framework is armed (any httpx/requests import
    does this), fork()+exec via subprocess.Popen(close_fds=True) SIGSEGVs in
    nw_settings_child_has_forked(). no_proxy="*" keeps _scproxy out of it.
    Both servers here are long-running stdio processes, not pytest runs, so
    conftest.py's layer-1 guard never applies — must be set here, first.
    """
    if sys.platform == "darwin":
        os.environ.setdefault("no_proxy", "*")
        os.environ.setdefault("NO_PROXY", "*")


def format_response(data: dict[str, Any], response_format: ResponseFormat, title: str = "") -> str:
    """Render a tool result as markdown or JSON. Mirrors mcp_tools.api_client._format_response."""
    if response_format == ResponseFormat.JSON:
        return json.dumps(data, indent=2, default=str, ensure_ascii=False)

    output: list[str] = []
    if title:
        output.append(f"# {title}\n")

    if "error" in data:
        output.append(f"❌ **Error:** {data['error']}\n")
        if "details" in data:
            output.append(f"**Details:** {data['details']}\n")
        return "\n".join(output)

    for key, value in data.items():
        label = key.replace("_", " ").title()
        if isinstance(value, dict):
            output.append(f"### {label}")
            for k, v in value.items():
                output.append(f"- **{k.replace('_', ' ').title()}:** {v}")
        elif isinstance(value, list):
            output.append(f"### {label}")
            for item in value[:10]:
                output.append(
                    f"- {json.dumps(item, default=str)}" if isinstance(item, dict) else f"- {item}"
                )
            if len(value) > 10:
                output.append(f"  _(and {len(value) - 10} more)_")
        else:
            output.append(f"**{label}:** {value}")
        output.append("")

    result = "\n".join(output)
    if len(result) > CHARACTER_LIMIT:
        result = (
            result[:CHARACTER_LIMIT]
            + f"\n\n⚠️ **Response Truncated**\nOriginal length: {len(result)} characters. "
            "Use JSON format for complete data."
        )
    return result


def new_correlation_id() -> str:
    return str(uuid.uuid4())[:8]


@contextlib.contextmanager
def locked_transaction(db_path: Path) -> Iterator[sqlite3.Connection]:
    """Cross-PROCESS mutex via SQLite BEGIN IMMEDIATE on a shared file.

    Each MCP client (Claude Code session, Codex, etc.) over stdio transport
    spawns its own server subprocess — there is no shared memory to lock
    with. BEGIN IMMEDIATE takes a RESERVED lock on the whole db file up
    front (not a per-row lock), so it serializes every mutating call across
    every process touching this file, not just calls on the same logical
    resource. That's intentional: these operations are all fast (a few ms),
    and correctness matters far more than concurrency here.

    Commits on clean exit, rolls back (burning nothing) on any exception —
    callers must do their real file write *inside* this block, before any
    counter value they allocated is persisted.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=30, isolation_level=None)
    try:
        _ensure_wal_mode(conn)
        conn.execute("BEGIN IMMEDIATE")
        yield conn
        conn.execute("COMMIT")
    except BaseException:
        if conn.in_transaction:
            conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()


def _ensure_wal_mode(conn: sqlite3.Connection) -> None:
    """Switch to WAL journaling once; a no-op read on every later call.

    Once WAL mode is set it's stored in the db file itself, so checking the
    current mode first (a read, takes no lock) means only the very first
    connection to a fresh file ever attempts the mode-changing PRAGMA. That
    matters because changing journal mode needs exclusive access at a lower
    level than a normal BEGIN IMMEDIATE write lock: several processes racing
    to open a brand-new lock db can transiently hit "database is locked" on
    this specific PRAGMA even with a busy timeout set, so the (rare) first
    attempt gets a short bounded retry instead of failing outright.
    """
    current = conn.execute("PRAGMA journal_mode").fetchone()[0]
    if str(current).lower() == "wal":
        return
    for attempt in range(10):
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            return
        except sqlite3.OperationalError:
            if attempt == 9:
                raise
            time.sleep(0.05 * (attempt + 1))


def atomic_write_text(path: Path, text: str) -> None:
    """Write-then-os.replace so a crash mid-write never corrupts an existing file.

    A concurrent reader either sees the fully-old or fully-new file, never a
    torn write — os.replace is atomic on POSIX (same filesystem).
    """
    tmp_path = path.with_name(f"{path.name}.tmp-{os.getpid()}-{new_correlation_id()}")
    tmp_path.write_text(text, encoding="utf-8")
    os.replace(tmp_path, path)
