#!/usr/bin/env python3
"""PreToolUse hook for launch-process — blocks dangerous shell commands.

Reads the auggie hook event from stdin and exits 2 to block, 0 to allow.
Dangerous patterns: rm -rf, git reset --hard, sudo, curl piped to sh.
"""

from __future__ import annotations

import json
import re
import sys

BLOCKED_PATTERNS = [
    r"rm\s+-rf\s+/",
    r"git\s+reset\s+--hard",
    r"git\s+push\s+--force\b(?!-with-lease)",
    r"sudo\s+rm",
    r"curl\s+.*\|\s*sh",
    r"curl\s+.*\|\s*bash",
    r">\s*/etc/",
    r"dd\s+if=",
    r"mkfs\.",
]

_BLOCKED_RE = re.compile("|".join(BLOCKED_PATTERNS))

PAID_COMMANDS = [
    "higgsfield",
    "fashn",
    "comfy.*--allow-spend",
]
_PAID_RE = re.compile("|".join(PAID_COMMANDS))


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return 0  # fail-open on malformed event — let auggie handle it

    command: str = event.get("tool_input", {}).get("command", "")

    if _BLOCKED_RE.search(command):
        print(
            json.dumps(
                {
                    "decision": "block",
                    "reason": f"Blocked dangerous command pattern: {command[:120]}",
                }
            )
        )
        return 2

    if _PAID_RE.search(command):
        # Emit a STOP-AND-SHOW style message — does not block, just surfaces
        print(
            json.dumps(
                {
                    "decision": "allow",
                    "context": (
                        "PAID API CALL DETECTED — confirm this was budgeted "
                        f"and approved before proceeding. Command: {command[:120]}"
                    ),
                }
            )
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
