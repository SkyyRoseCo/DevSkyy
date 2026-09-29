"""
Direct REST client for Gemini API — bypasses the Python SDK.

Enhanced with OpenTelemetry for "Back Data" observability.

Security posture:
    - API key passed via x-goog-api-key HEADER (never in URL querystring).
      Prior bug (CRIT): key-in-URL leaked via httpx HTTPError strings,
      OpenTelemetry span attributes, and server access logs.
    - Key list frozen at import time. Prior bug (HIGH #7984):
      sorted(set(_load_keys())) re-derived ordering on every call,
      silently breaking the round-robin when env vars changed.
    - Fail-fast on 400/401/403 — retrying auth errors burns quota and
      delays the real failure.
    - All exception strings are scrubbed for key-shaped tokens before
      they enter logs or return values (defense in depth).
"""

from __future__ import annotations

import base64
import logging
import os
import re
import threading
import time
from typing import Any

import requests

from core.telemetry.tracer import get_tracer

from .config import GEMINI_TIMEOUT

logger = logging.getLogger(__name__)

_API_BASE = "https://generativelanguage.googleapis.com/v1beta"


def _load_keys() -> list[str]:
    """Discover configured Gemini API keys from env, preserving discovery order.

    Reads primary names first, then numbered fallbacks. Deduplicates while
    preserving the order each key was first seen so round-robin rotation is
    deterministic across process restarts (given identical env).
    """
    keys: list[str] = []
    seen: set[str] = set()

    def _add(val: str | None) -> None:
        if val and val not in seen:
            seen.add(val)
            keys.append(val)

    for primary in ("GEMINI_API_KEY", "GOOGLE_AI_API_KEY", "GOOGLE_API_KEY"):
        _add(os.getenv(primary))

    for i in range(1, 11):
        for fmt in ("GEMINI_API_KEY_{}", "GOOGLE_AI_API_KEY_{}", "GOOGLE_API_KEY_{}"):
            _add(os.getenv(fmt.format(i)))

    return keys


def _get_keys() -> list[str]:
    """Read keys from env on each call. Backward-compat alias used by tests
    and diagnostic tooling. The hot path uses the frozen module-level
    ``_KEYS`` list (see ``_get_active_key``) — that's the only path that
    rotation order depends on. This re-reads env each invocation so
    monkeypatch.setenv-style tests can verify env discovery.
    """
    return _load_keys()


# Frozen once at import. Mutating env after import does NOT affect rotation —
# fix the env, then restart the process. This is the only way to make rotation
# index meaningful across calls.
_KEYS: list[str] = _load_keys()
_KEY_INDEX = 0
_KEY_LOCK = threading.Lock()

tracer = get_tracer(__name__)

# Status codes worth retrying — transient or rate-limited.
_RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})

# Status codes that must NOT be retried — auth failures, malformed requests.
_NON_RETRYABLE_STATUS = frozenset({400, 401, 403, 404})

# Match anything shaped like a Google API key. Used to scrub keys that may
# have leaked into exception strings from older clients, downstream libraries,
# or third-party error reporters.
_KEY_SCRUB_RE = re.compile(r"AIza[0-9A-Za-z_\-]{30,}")


def _scrub(text: str) -> str:
    """Strip Gemini-shaped API key tokens from a string before logging."""
    return _KEY_SCRUB_RE.sub("AIza<scrubbed>", text)


def _get_active_key() -> str:
    """Round-robin next key from the frozen list."""
    global _KEY_INDEX
    if not _KEYS:
        return ""
    with _KEY_LOCK:
        key = _KEYS[_KEY_INDEX % len(_KEYS)]
        _KEY_INDEX += 1
    return key


def _endpoint(model: str, method: str = "generateContent") -> str:
    """Build endpoint URL. Auth via x-goog-api-key header, never querystring."""
    return f"{_API_BASE}/models/{model}:{method}"


def _post_with_retry(
    model: str, method: str, payload: dict, *, attempt_limit: int | None = None
) -> dict[str, Any]:
    """Post to Gemini with key rotation on 429/5xx and OpenTelemetry tracing.

    Auth: x-goog-api-key header. Fail-fast on 400/401/403/404; otherwise rotate
    to the next key with exponential backoff. Caps total attempts at len(_KEYS).
    All errors returned to the caller are scrubbed of key-shaped tokens.
    """
    with tracer.start_as_current_span(f"gemini_api_{method}") as span:
        span.set_attribute("model", model)
        span.set_attribute("method", method)

        if not _KEYS:
            return {"success": False, "error": "No Gemini API keys configured"}

        url = _endpoint(model, method)
        max_attempts = len(_KEYS) if attempt_limit is None else min(len(_KEYS), attempt_limit)
        if max_attempts < 1:
            raise ValueError("attempt_limit must be positive")

        for attempt in range(max_attempts):
            key = _get_active_key()
            try:
                start_time = time.monotonic()
                resp = requests.post(
                    url,
                    json=payload,
                    timeout=GEMINI_TIMEOUT,
                    headers={
                        "x-goog-api-key": key,
                        "Content-Type": "application/json",
                    },
                )
                duration = time.monotonic() - start_time

                span.add_event(
                    f"api_attempt_{attempt}",
                    attributes={
                        "status_code": resp.status_code,
                        "duration_s": duration,
                    },
                )

                if resp.status_code in _NON_RETRYABLE_STATUS:
                    span.set_attribute("error.kind", "non_retryable")
                    body = _scrub((resp.text or "")[:200])
                    return {
                        "success": False,
                        "error": f"HTTP {resp.status_code} (non-retryable): {body}",
                    }

                if resp.status_code in _RETRYABLE_STATUS and attempt < max_attempts - 1:
                    backoff = min(1.0 * (2**attempt), 8.0)
                    time.sleep(backoff)
                    continue

                resp.raise_for_status()
                data = resp.json()

                usage = data.get("usageMetadata", {})
                if usage:
                    span.set_attribute("prompt_tokens", usage.get("promptTokenCount", 0))
                    span.set_attribute("candidates_tokens", usage.get("candidatesTokenCount", 0))

                return {"success": True, "data": data}
            except Exception as exc:
                msg = _scrub(str(exc))
                span.record_exception(exc)
                if attempt < max_attempts - 1:
                    time.sleep(min(1.0 * (2**attempt), 8.0))
                    continue
                return {"success": False, "error": msg}

        return {"success": False, "error": "All API keys exhausted or rate limited"}


def generate_text(model: str, prompt: str) -> dict[str, Any]:
    """Generate text content."""
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    result = _post_with_retry(model, "generateContent", payload)

    if not result["success"]:
        return result

    try:
        text = result["data"]["candidates"][0]["content"]["parts"][0]["text"]
        return {"success": True, "text": text}
    except Exception as exc:
        return {"success": False, "error": _scrub(str(exc))}


def analyze_vision(
    model: str,
    prompt: str,
    image_b64: str,
    mime_type: str = "image/jpeg",
    *,
    reference_images: list[dict[str, str]] | None = None,
    response_schema: dict | None = None,
    max_output_tokens: int = 2400,
) -> dict[str, Any]:
    """Analyze a candidate, optionally preceded by labeled authoritative references.

    Structured QA uses one transport attempt; no account-key rotation retries.
    Other vision callers retain their existing retry policy and input signature.
    """
    parts: list[dict[str, Any]] = [{"text": prompt}]
    for index, reference in enumerate(reference_images or []):
        parts.extend(
            [{"text": f"A{index + 1}: authoritative reference"}, {"inline_data": reference}]
        )
    if reference_images:
        parts.append({"text": "B: candidate"})
    parts.append({"inline_data": {"mime_type": mime_type, "data": image_b64}})
    payload = {"contents": [{"parts": parts}]}
    if response_schema is not None:
        payload["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseJsonSchema": response_schema,
            "maxOutputTokens": max_output_tokens,
        }
        result = _post_with_retry(model, "generateContent", payload, attempt_limit=1)
    else:
        result = _post_with_retry(model, "generateContent", payload)
    if not result["success"]:
        return result
    try:
        candidate = result["data"]["candidates"][0]
        if response_schema is not None and candidate.get("finishReason") != "STOP":
            return {"success": False, "error": "Incomplete or blocked structured vision response"}
        text = "".join(
            p.get("text", "") for p in candidate["content"]["parts"] if not p.get("thought")
        )
        if not text:
            return {"success": False, "error": "Empty vision response"}
        return {"success": True, "text": text}
    except Exception as exc:
        return {"success": False, "error": _scrub(str(exc))}


def generate_image(
    model: str,
    prompt: str,
    reference_images_b64: list[str] | str,
    aspect_ratio: str = "3:4",
    mime_type: str = "image/jpeg",
) -> dict[str, Any]:
    """Generate image using Gemini image model with one or more reference images."""
    parts: list[dict[str, Any]] = [{"text": prompt}]

    if isinstance(reference_images_b64, str):
        # Backward compatibility for single string
        if reference_images_b64:
            parts.append(
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": reference_images_b64,
                    }
                }
            )
    else:
        for b64 in reference_images_b64:
            if b64:
                parts.append(
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": b64,
                        }
                    }
                )

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": aspect_ratio},
        },
    }

    result = _post_with_retry(model, "generateContent", payload)

    if not result["success"]:
        return result

    try:
        data = result["data"]
        for part in data.get("candidates", [{}])[0].get("content", {}).get("parts", []):
            if "inlineData" in part:
                image_b64_str = part["inlineData"]["data"]
                return {
                    "success": True,
                    "image_data": base64.b64decode(image_b64_str),
                    "mime_type": part["inlineData"].get("mimeType", "image/jpeg"),
                }

        return {"success": False, "error": "No image in response"}
    except Exception as exc:
        return {"success": False, "error": _scrub(str(exc))}
