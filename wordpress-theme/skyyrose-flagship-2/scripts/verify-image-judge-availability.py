#!/usr/bin/env python3
"""Probe the mandatory GPT vision reviewer without exposing credentials."""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
THEME_DIR = Path(__file__).resolve().parent.parent
OUTPUT = (
    THEME_DIR
    / "assets/scroll-world/generated-candidates/founder-commerce-scenes-v1/preflight-v1/judge-availability-receipt-v1.json"
)
ENV_FILES = (
    ".env.judge-gpt-vision",
    ".env.hf",
    ".env",
    ".env.secrets",
    ".env.production",
)


def load_local_environment() -> None:
    for name in ENV_FILES:
        path = ROOT / name
        if not path.is_file():
            continue
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def credential_candidates(names: tuple[str, ...]) -> list[str]:
    """Return every configured unique credential without exposing its name or value."""

    credentials: list[str] = []
    for name in names:
        value = os.getenv(name, "").strip()
        if value and value not in credentials:
            credentials.append(value)
    return credentials


def safe_failure_reason(error: BaseException) -> str:
    """Classify provider failures without persisting response bodies or secrets."""
    message = str(error).lower()
    if any(
        marker in message
        for marker in (
            "insufficient_quota",
            "credit balance",
            "no credits remaining",
            "quota exceeded",
            "resource_exhausted",
        )
    ):
        return "inference_quota_or_credit_exhausted"
    if "rate limit" in message or type(error).__name__ == "RateLimitError":
        return "inference_rate_limited"
    return f"model_probe_failed:{type(error).__name__}"


def probe_credentials(
    label: str,
    credentials: list[str],
    callback: Callable[[str], Any],
) -> dict[str, Any]:
    """Try every configured key until one proves the required model is live."""

    if not credentials:
        return {
            "model": label,
            "available": False,
            "reason": "credential_not_configured",
            "configured_credentials_tried": 0,
        }
    failures: list[str] = []
    for credential in credentials:
        try:
            callback(credential)
        except (KeyboardInterrupt, GeneratorExit):
            raise
        except (Exception, SystemExit) as error:  # Some SDKs raise SystemExit while configuring.
            failures.append(safe_failure_reason(error))
            continue
        return {
            "model": label,
            "available": True,
            "reason": "live_model_probe_passed",
            "configured_credentials_tried": len(failures) + 1,
        }
    return {
        "model": label,
        "available": False,
        "reason": failures[-1],
        "configured_credentials_tried": len(failures),
    }


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as stream:
        temporary = Path(stream.name)
        json.dump(payload, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def probe_openai(key: str) -> None:
    from openai import OpenAI

    client = OpenAI(api_key=key, timeout=30)
    client.models.retrieve("gpt-5.5-pro")
    client.responses.create(
        model="gpt-5.5-pro",
        input="Return only OK.",
        reasoning={"effort": "high"},
        max_output_tokens=16384,
    )


def main() -> int:
    load_local_environment()
    results = [
        probe_credentials(
            "gpt-5.5-pro",
            credential_candidates(
                ("OPENAI_API_KEY", "OPENAI_AGENT107_KEY", "OPENAI_FEB19", "OPENAI_MCP_KEY")
            ),
            probe_openai,
        ),
    ]
    all_available = all(result["available"] for result in results)
    receipt = {
        "schema": "skyyrose.image-judge-availability.v1",
        "status": (
            "PASS_ALL_JUDGES_AVAILABLE" if all_available else "BLOCKED_REQUIRED_JUDGE_UNAVAILABLE"
        ),
        "checked_at": datetime.now(UTC).isoformat(),
        "all_judges_available": all_available,
        "judges": results,
        "secrets_in_receipt": False,
    }
    write_json_atomic(OUTPUT, receipt)
    print(receipt["status"])
    for result in results:
        print(f"{result['model']}: {'available' if result['available'] else result['reason']}")
    return 0 if all_available else 1


if __name__ == "__main__":
    raise SystemExit(main())
