"""wolf-memory MCP server — stdio entrypoint.

Standalone: no dependency on the devskyy FastAPI backend or on
mcp_tools/. Atomic .wolf/buglog.json writes and bug-NNN allocation across
concurrent sessions (Claude Code, Codex, or a human), for the reasons
documented in docs/architecture/mcp-worktree-fleet-and-wolf-memory.html.

Usage:
    python3 wolf_memory_mcp.py
"""

import sys

from mcp_servers._shared import apply_darwin_fork_safety

apply_darwin_fork_safety()  # bug-263 — must run before any subprocess/httpx-touching import

from mcp_servers.wolf_memory.tools import (  # noqa: E402 — import order is the fork-safety guard above
    mcp,
)

if __name__ == "__main__":
    # stdio transport uses STDOUT as the JSON-RPC channel — every human-readable
    # line must go to stderr, matching devskyy_mcp.py's convention.
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
    print("wolf-memory MCP server starting on stdio...", file=sys.stderr)
    mcp.run()
