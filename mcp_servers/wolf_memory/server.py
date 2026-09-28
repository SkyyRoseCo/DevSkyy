"""FastMCP instance for the wolf-memory server — own process, no backend dependency."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BUGLOG_PATH = Path(os.getenv("WOLF_BUGLOG_PATH", REPO_ROOT / ".wolf" / "buglog.json"))
CEREBRUM_PATH = Path(os.getenv("WOLF_CEREBRUM_PATH", REPO_ROOT / ".wolf" / "cerebrum.md"))
LOCK_DB_PATH = Path(os.getenv("WOLF_LOCK_DB_PATH", REPO_ROOT / ".wolf" / "wolf.lock.db"))

logger = logging.getLogger("wolf_memory")

mcp = FastMCP("wolf-memory")
