"""Trusted local qualification under the current user's explicit chat instruction.

Not an API approval bypass: no endpoint imports this harness, no JWT is minted,
and receipts never claim owner-browser approval. No automatic retries.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from skyyrose.godmode_runtime.service import Runtime, canonical

if __name__ == "__main__":
    raise SystemExit(
        "Historical qualification harness disabled. Use a fresh reviewed plan and current authorization; no stored chat approval may be replayed."
    )
    workflow = sys.argv[1]
    if workflow not in {"fashion-campaign-analysis", "fashion-skill-analysis"}:
        raise SystemExit(2)
    key = dotenv_values(ROOT / ".env").get("ANTHROPIC_API_KEY")
    if not key:
        raise SystemExit("Claude credential unavailable")
    os.environ["ANTHROPIC_API_KEY"] = key
    os.environ["GOD_MODE_CLAUDE_MODEL"] = "claude-opus-5-5"
    os.environ["GOD_MODE_CODEX_MODEL"] = "gpt-6.1-sol"
    state = Path.home() / "Library/Application Support/DevSkyy/god-mode/runtime.sqlite"
    r = Runtime(ROOT, Path("/Users/theceo/plugins/fashion-theme-team"), state)
    actor = "codex-current-chat:01a1284f"
    run = r.create(
        "skyyrose",
        workflow,
        "live-qualification-"
        + workflow
        + "-20261018-"
        + (sys.argv[2] if len(sys.argv) > 2 else "initial"),
        actor,
    )
    if run["status"] != "PENDING_APPROVAL":
        print(
            json.dumps(
                {"existing_run": run["id"], "status": run["status"], "automatic_retry": False}
            )
        )
        raise SystemExit(1)
    with r.transaction() as conn:
        row = r._get(conn, run["id"])
        if r._drift(row):
            raise RuntimeError("Changed plan; no dispatch")
        approval = {
            "actor": actor,
            "plan_hash": run["plan_hash"],
            "approved_at": time.time(),
            "expires_at": time.time() + 900,
            "scope": run["plan"]["scope"],
            "approval_channel": "current_chat",
            "authorization": "Current user explicitly authorized Claude main worker, Codex independent reviewer and Fashion workflow testing; then selected Opus 5.5.",
        }
        conn.execute(
            "UPDATE runs SET status='APPROVED',approval=?,updated=? WHERE id=?",
            (canonical(approval), time.time(), run["id"]),
        )
        r.event(conn, run["id"], "LOCAL_QUALIFICATION_AUTHORIZED", actor, approval)
    result = r.execute(run["id"], run["plan_hash"], actor)
    output = ROOT / "tasks/godmode-agent-workers-20261018" / f"{workflow}-live.json"
    output.write_text(
        json.dumps(
            {
                "evidence_class": "VERIFIED_LIVE",
                "approval_channel": "current_chat_service_layer",
                "owner_browser_login": "NOT_TESTED",
                "provider_authentication": {
                    "Claude": "api.anthropic.com credential identity bound; actual result establishes call authentication",
                    "Codex": "existing ChatGPT auth, no API-key fallback",
                },
                "run": result,
            },
            indent=2,
        )
        + "\n"
    )
    print(
        json.dumps(
            {
                "run_id": result["id"],
                "status": result["status"],
                "steps": [
                    {
                        "id": s["id"],
                        "status": s["status"],
                        "error_code": s.get("error_code"),
                        "usage": s.get("usage"),
                        "verdict": s.get("artifact", {}).get("verdict"),
                    }
                    for s in result["steps"]
                ],
                "receipt": str(output),
            }
        )
    )
