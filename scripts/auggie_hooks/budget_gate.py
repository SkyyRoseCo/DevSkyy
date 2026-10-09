#!/usr/bin/env python3
"""PreToolUse hook for devskyy MCP tools — enforces session spend caps.

Reads the auggie hook event from stdin. Exits 2 to block if the
session has exceeded the configured cap, 0 to allow.

Cap is read from AUGGIE_SESSION_BUDGET_USD env var (default: $50).
Spend is tracked in .augment/session-spend.json (append-only).
"""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SPEND_LOG = _REPO_ROOT / ".augment" / "session-spend.json"
_DEFAULT_CAP = float(os.environ.get("AUGGIE_SESSION_BUDGET_USD", "50.0"))

# Tools that have a measurable cost — map to estimated cost per call
_COSTLY_TOOLS = {
    "higgsfield_generate": 8.5,
    "fashn_vton": 1.5,
    "gemini_image": 0.10,
    "openai_image": 0.10,
    "tripo_generate": 2.0,
}


def _load_spend() -> float:
    if not _SPEND_LOG.is_file():
        return 0.0
    total = 0.0
    for line in _SPEND_LOG.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
            total += float(entry.get("cost", 0))
        except (json.JSONDecodeError, ValueError):
            continue
    return total


def _log_call(tool_name: str, cost: float, session_id: str) -> None:
    _SPEND_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(UTC).isoformat(),
        "tool": tool_name,
        "cost": cost,
        "session_id": session_id,
    }
    with _SPEND_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return 0

    tool_name: str = event.get("tool_name", "")
    session_id: str = event.get("session_id", "unknown")
    cap = _DEFAULT_CAP

    # Find matching costly tool
    matched_cost = 0.0
    for pattern, cost in _COSTLY_TOOLS.items():
        if pattern in tool_name:
            matched_cost = cost
            break

    if matched_cost == 0.0:
        return 0  # free tool — allow

    current_spend = _load_spend()

    if current_spend + matched_cost > cap:
        print(
            json.dumps(
                {
                    "decision": "block",
                    "reason": (
                        f"Session budget cap ${cap:.2f} would be exceeded. "
                        f"Current spend: ${current_spend:.2f}, "
                        f"call cost: ${matched_cost:.2f}. "
                        "Obtain explicit approval before proceeding."
                    ),
                }
            )
        )
        return 2

    # Allow and log the anticipated spend
    _log_call(tool_name, matched_cost, session_id)
    print(
        json.dumps(
            {
                "decision": "allow",
                "context": (
                    f"Spend tracked: ${matched_cost:.2f} for {tool_name}. "
                    f"Session total: ${current_spend + matched_cost:.2f} / ${cap:.2f}"
                ),
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
