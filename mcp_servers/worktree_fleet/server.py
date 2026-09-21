"""FastMCP instance for the worktree-fleet server — own process, no backend dependency."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = Path(os.getenv("FLEET_DB_PATH", REPO_ROOT / ".wolf" / "fleet.db"))

logger = logging.getLogger("worktree_fleet")

mcp = FastMCP("worktree-fleet")
