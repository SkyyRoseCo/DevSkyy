"""Start the loopback-only GOD MODE host using existing backend JWT secrets."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import dotenv_values


def main() -> None:
    """Configure explicit local durable state without copying credentials."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8011)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("Choose an unprivileged local port")
    if os.environ.get("ENVIRONMENT", "development").lower() in {"production", "staging"}:
        parser.error("This launcher is for one local workstation, not a deployed profile")
    root = Path(__file__).resolve().parents[1]
    # Read only these named credentials. Never print dotenv keys/values or inherit
    # arbitrary provider keys from a credentials notebook into this process.
    for name in (".env", ".env.local"):
        path = root / name
        if path.is_file():
            source = dotenv_values(path)
            for key in ("JWT_SECRET_KEY", "JWT_REFRESH_SECRET_KEY", "ANTHROPIC_API_KEY"):
                if key not in os.environ and source.get(key):
                    os.environ[key] = str(source[key])
    if not all(os.environ.get(key) for key in ("JWT_SECRET_KEY", "JWT_REFRESH_SECRET_KEY")):
        parser.error(
            "Configure the existing backend JWT_SECRET_KEY and JWT_REFRESH_SECRET_KEY; no temporary login key is created"
        )
    os.environ.setdefault("GOD_MODE_CLAUDE_MODEL", "claude-opus-5-5")
    os.environ.setdefault("GOD_MODE_CODEX_MODEL", "gpt-6.1-sol")
    state = Path.home() / "Library/Application Support/DevSkyy/god-mode/runtime.sqlite"
    os.environ.setdefault("GOD_MODE_DB_PATH", str(state))
    os.environ["GOD_MODE_RUNTIME_PROFILE"] = "workstation"
    os.chdir(root)
    import uvicorn

    uvicorn.run(
        "skyyrose.godmode_runtime.api:create_app", factory=True, host="127.0.0.1", port=args.port
    )


if __name__ == "__main__":
    main()
