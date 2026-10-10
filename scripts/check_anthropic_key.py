#!/usr/bin/env python3
"""Check that ANTHROPIC_API_KEY is loaded and accepted by the Anthropic API.

Default run is free: it lists models (no tokens consumed).
`--message --yes` additionally sends one 50-token Haiku message (paid, < $0.001).

Usage:
    python scripts/check_anthropic_key.py
    python scripts/check_anthropic_key.py --message --yes
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_FILES = (".env", ".env.local")
HAIKU_MODEL = "claude-haiku-4-5-20251001"


def load_key() -> str:
    """Load the key from the shell or the repo env files; never print it."""
    source = "shell environment" if os.environ.get("ANTHROPIC_API_KEY") else None
    for name in ENV_FILES:
        if source:
            break
        path = REPO_ROOT / name
        if path.is_file():
            load_dotenv(path, override=False)
            if os.environ.get("ANTHROPIC_API_KEY"):
                source = name
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key.startswith("sk-ant-"):
        sys.exit(f"FAIL  no ANTHROPIC_API_KEY found (checked shell, {', '.join(ENV_FILES)})")
    print(f"OK    key loaded from {source}")
    return key


def check_models(client: anthropic.Anthropic) -> None:
    models = [m.id for m in client.models.list(limit=5).data]
    print(f"OK    key accepted - {len(models)} models visible: {', '.join(models)}")


def send_message(client: anthropic.Anthropic) -> None:
    reply = client.messages.create(
        model=HAIKU_MODEL,
        max_tokens=50,
        messages=[{"role": "user", "content": "Reply with exactly: SkyyRose key check passed"}],
    )
    text = reply.content[0].text if reply.content else ""
    usage = reply.usage
    print(
        f"OK    {HAIKU_MODEL} replied: {text!r} ({usage.input_tokens} in / {usage.output_tokens} out tokens)"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--message", action="store_true", help="also send one paid Haiku message")
    parser.add_argument("--yes", action="store_true", help="confirm the paid --message call")
    args = parser.parse_args()
    if args.message and not args.yes:
        sys.exit(
            "STOP  --message is a paid call (< $0.001). Re-run with --message --yes to confirm."
        )

    client = anthropic.Anthropic(api_key=load_key())
    try:
        check_models(client)
        if args.message:
            send_message(client)
    except anthropic.AuthenticationError:
        sys.exit(
            "FAIL  401 - key rejected (revoked, mistyped, or rotated). Create a new key in the Console."
        )
    except anthropic.PermissionDeniedError:
        sys.exit("FAIL  403 - key valid but lacks permission for this request.")
    except anthropic.RateLimitError:
        sys.exit("FAIL  429 - rate limited or out of credit. Check Console billing.")
    except anthropic.APIConnectionError as exc:
        sys.exit(
            f"FAIL  could not reach api.anthropic.com ({type(exc).__name__}). Check network/proxy."
        )
    except anthropic.APIStatusError as exc:
        sys.exit(f"FAIL  API returned {exc.status_code}.")
    print("DONE  key is working")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
