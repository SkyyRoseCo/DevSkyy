"""Keep tool-module imports off the real registries.

mcp_servers/worktree_fleet/tools.py and wolf_memory/tools.py build their store
at import time from the paths in their server module, which default to this
checkout's own .wolf/ files. Importing them in a test would open — and CREATE
TABLE on — the live fleet.db that other sessions are using. Both servers honour
an env override, so point them at a throwaway directory before any test module
is imported (module level, so it runs during collection).

Assigned, never setdefault: a sandbox that defers to a variable the operator
already exported is not a sandbox — it would run these tests against whatever
registry that variable names. monkeypatch cannot be used here because the paths
are read at import, before any fixture exists.
"""

from __future__ import annotations

import atexit
import os
import shutil
import tempfile
from pathlib import Path

_SANDBOX = Path(tempfile.mkdtemp(prefix="mcp-servers-tests-"))
atexit.register(shutil.rmtree, _SANDBOX, ignore_errors=True)
os.environ["FLEET_DB_PATH"] = str(_SANDBOX / "fleet.db")
os.environ["WOLF_LOCK_DB_PATH"] = str(_SANDBOX / "wolf.lock.db")
os.environ["WOLF_BUGLOG_PATH"] = str(_SANDBOX / "buglog.json")
os.environ["WOLF_CEREBRUM_PATH"] = str(_SANDBOX / "cerebrum.md")
