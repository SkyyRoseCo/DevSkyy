"""worktree-fleet MCP server — stdio entrypoint.

Standalone: no dependency on the devskyy FastAPI backend or on mcp_tools/.
Atomic git-worktree ownership registry across concurrent sessions (Claude
Code, Codex, or a human) on this machine — see
docs/architecture/mcp-worktree-fleet-and-wolf-memory.html.

Usage:
    python3 worktree_fleet_mcp.py
"""

import sys

from mcp_servers._shared import apply_darwin_fork_safety

apply_darwin_fork_safety()  # bug-263 — must run before any subprocess/httpx-touching import

from mcp_servers.worktree_fleet.tools import (  # noqa: E402 — import order is the fork-safety guard above
    mcp,
)

if __name__ == "__main__":
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
    print("worktree-fleet MCP server starting on stdio...", file=sys.stderr)
    mcp.run()
