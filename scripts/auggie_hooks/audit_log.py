#!/usr/bin/env python3
"""PostToolUse hook — appends an audit trail entry to .augment/audit.jsonl.

Runs after every tool call. Never blocks (always exits 0).
Log format is append-only JSONL: one JSON object per line.
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_AUDIT_LOG = _REPO_ROOT / ".augment" / "audit.jsonl"

# Fields to redact from tool inputs (contain credentials or PII)
_REDACT_KEYS = {
    "api_key",
    "apikey",
    "token",
    "password",
    "secret",
    "authorization",
    "auth",
    "cookie",
    "session",
}


def _redact(obj: object) -> object:
    if isinstance(obj, dict):
        return {
            k: "<redacted>" if k.lower() in _REDACT_KEYS else _redact(v) for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [_redact(i) for i in obj]
    return obj


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return 0  # never block on parse failure

    entry = {
        "ts": datetime.now(UTC).isoformat(),
        "tool": event.get("tool_name", "unknown"),
        "session_id": event.get("session_id", "unknown"),
        "exit_code": event.get("tool_result", {}).get("exit_code"),
        "input_summary": _redact(event.get("tool_input", {})),
    }

    # Truncate large outputs
    result_content = str(event.get("tool_result", {}).get("content", ""))
    entry["result_chars"] = len(result_content)
    if len(result_content) > 500:
        entry["result_preview"] = result_content[:500] + "…"

    try:
        _AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with _AUDIT_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass  # never fail the hook due to I/O

    return 0


if __name__ == "__main__":
    sys.exit(main())
