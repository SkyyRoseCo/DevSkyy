"""Generate a Seedance 2.5 text-to-video clip through the official Higgsfield SDK.

Credentials: HF_KEY ("key-id:key-secret") is loaded at runtime from the .env.local
file next to this script (gitignored by the `.env.*` rule). The value is only
checked for shape; it is never printed or logged.

Usage:
    .venv/bin/python main.py

Every run submits one billable generation, so nothing is submitted without an
explicit yes: the manifest is always printed, SKYYROSE_AUTO_CONFIRM=1 is the only
non-interactive opt-in, and a run with no TTY aborts. On success the video URL is
the only thing written to stdout; the manifest, progress and errors go to stderr,
and every outcome other than a completed request with a video URL exits non-zero.
"""

from __future__ import annotations

import json
import os
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import higgsfield_client
import httpx
from dotenv import load_dotenv

MODEL = "bytedance/seedance-2.5/text-to-video"
ARGUMENTS: dict[str, Any] = {
    "prompt": "A cinematic scene at sunset",
    "duration": 5,
    "resolution": "720p",
    "aspect_ratio": "16:9",
}
ENV_FILE = Path(__file__).resolve().parent / ".env.local"
MAX_WAIT_SECONDS = 15 * 60
EXIT_NOT_CONFIRMED = 5

# subscribe() returns the final status payload for every terminal state instead of
# raising, so each non-"completed" state (SDK StatusEnum) must be rejected here.
FAILURE_REASONS = {
    "failed": "failed",
    "nsfw": "was rejected by content moderation (nsfw)",
    "canceled": "was canceled",
}


class GenerationError(RuntimeError):
    """The request finished without producing a usable video URL."""


def log(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


def credentials_configured() -> bool:
    """True when HF_KEY is set in key-id:key-secret form. Never exposes the value."""
    key_id, sep, secret = os.environ.get("HF_KEY", "").partition(":")
    return bool(sep and key_id.strip() and secret.strip())


def confirm_billable_run(
    prompt_fn: Callable[[str], str],
    is_tty: Callable[[], bool],
    *,
    auto_confirmed: bool,
) -> bool:
    """STOP-AND-SHOW gate, fail-closed. Same contract as pipeline3d/cli._confirm.

    The manifest prints first in every case. `auto_confirmed` is the only
    non-interactive opt-in and the caller reads it from the real environment before
    .env.local is loaded, so an env-file line cannot confirm future runs; with no
    TTY the run aborts; at a TTY only an explicit y/yes proceeds, and a closed stdin
    is not confirmation. The price is not stated because this script has no
    verified figure for it.
    """
    arguments = "\n".join(f"  {key:<13}: {value}" for key, value in ARGUMENTS.items())
    log(
        "\nSTOP — Confirm before proceeding:\n\n"
        "  Action       : Higgsfield text-to-video (billable, one generation)\n"
        f"  Model        : {MODEL}\n{arguments}\n"
        "  Cost         : charged to the Higgsfield account behind HF_KEY\n"
    )
    if auto_confirmed:
        log("Auto-confirmed via SKYYROSE_AUTO_CONFIRM=1.")
        return True
    if not is_tty():
        log("No TTY — aborting the billable run. Set SKYYROSE_AUTO_CONFIRM=1 to allow it.")
        return False
    try:
        return prompt_fn("Proceed? [y/N] ").strip().lower() in ("y", "yes")
    except EOFError:
        return False


def extract_video_url(result: dict[str, Any]) -> str:
    """Return the video URL of a completed request, or raise GenerationError."""
    status = result.get("status")
    if status != "completed":
        reason = FAILURE_REASONS.get(status, f"ended with unexpected status {status!r}")
        raise GenerationError(f"Generation {reason}.")

    # Verified against the live API on 2026-09-21 (request
    # aa81a322-483a-44aa-81a4-1043c3d44935): a completed seedance-2.5 response
    # carries {"video": {"url": "https://...mp4"}}. The list branch stays because
    # the docs only promise "returned in the video field".
    video = result.get("video")
    if isinstance(video, list) and video:
        video = video[0]
    url = video.get("url") if isinstance(video, dict) else None
    parsed = urlparse(url) if isinstance(url, str) else None
    if parsed is None or parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise GenerationError(
            f"Request completed but returned no video URL (top-level keys: {sorted(result)})."
        )
    return url


class ProgressWatcher:
    """subscribe() callbacks: log status changes, keep the last status, bound the wait."""

    def __init__(self, max_wait_seconds: float) -> None:
        self.request_id: str | None = None
        self.last_status: higgsfield_client.Status | None = None
        self._deadline = time.monotonic() + max_wait_seconds

    def on_enqueue(self, request_id: str) -> None:
        self.request_id = request_id
        log(f"Enqueued request {request_id}")

    def on_queue_update(self, status: higgsfield_client.Status) -> None:
        if type(status) is not type(self.last_status):
            log(f"Status: {type(status).__name__}")
        self.last_status = status
        done = isinstance(status, higgsfield_client.DONE_STATUSES)
        if not done and time.monotonic() > self._deadline:
            raise TimeoutError(f"Request did not finish within {MAX_WAIT_SECONDS} seconds.")


def main(
    prompt_fn: Callable[[str], str] = input,
    is_tty: Callable[[], bool] | None = None,
) -> int:
    # Read the opt-in from the real environment BEFORE .env.local is loaded, so that
    # a line in the env file cannot auto-confirm this and every later billable run.
    auto_confirmed = os.environ.get("SKYYROSE_AUTO_CONFIRM") == "1"
    load_dotenv(ENV_FILE, override=False)
    if not credentials_configured():
        log(f"HF_KEY is missing or not in key-id:key-secret form. Add it to {ENV_FILE}.")
        return 2
    # Resolved at call time: sys.stdin can be replaced after this module is imported.
    if not confirm_billable_run(
        prompt_fn, is_tty or sys.stdin.isatty, auto_confirmed=auto_confirmed
    ):
        return EXIT_NOT_CONFIRMED

    watcher = ProgressWatcher(MAX_WAIT_SECONDS)
    try:
        result = higgsfield_client.subscribe(
            MODEL,
            arguments=ARGUMENTS,
            on_enqueue=watcher.on_enqueue,
            on_queue_update=watcher.on_queue_update,
        )
    except (TimeoutError, KeyboardInterrupt) as exc:
        log(f"Stopped waiting ({type(exc).__name__}): {exc}")
        log(
            f"The request may still finish; check higgsfield_client.status({watcher.request_id!r})."
        )
        return 4 if isinstance(exc, TimeoutError) else 130
    except (
        higgsfield_client.HiggsfieldClientError,
        higgsfield_client.CredentialsMissedError,
        httpx.HTTPError,
        ValueError,
    ) as exc:
        log(f"Higgsfield request failed ({type(exc).__name__}): {exc}")
        return 3

    try:
        url = extract_video_url(result)
        if not isinstance(watcher.last_status, higgsfield_client.Completed):
            raise GenerationError(f"Last polled status was {watcher.last_status!r}.")
    except GenerationError as exc:
        log(f"{exc} Request id: {watcher.request_id}")
        log(json.dumps(result, indent=2, sort_keys=True))
        return 1

    log(f"Completed request {watcher.request_id}")
    print(url)
    return 0


if __name__ == "__main__":
    sys.exit(main())
