"""LIVE Gemini scripts against the real google-genai SDK, with only HTTP faked.

The nano_banana tests mock ``_judge_call_gemini`` and nothing exercises
``gemini_scene_gen`` or the lookbook request shape, so a google-genai upgrade
that changed request encoding or response parsing would pass unseen. These
tests build a real ``genai.Client`` over an ``httpx.MockTransport`` (passed
through ``HttpOptions.client_args``) so the SDK serializes and parses every
byte, and no request leaves the process.
"""

from __future__ import annotations

import base64
import io
import json
from pathlib import Path

import httpx
import pytest
from google import genai
from google.genai import types
from PIL import Image

from scripts import gemini_scene_gen
from scripts.nano_banana import tournament


def _png_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (4, 4), (183, 110, 121)).save(buffer, format="PNG")
    return buffer.getvalue()


PNG = _png_bytes()


def _client(handler) -> tuple[genai.Client, list[httpx.Request]]:
    requests: list[httpx.Request] = []

    def recording_handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return handler(request)

    options = types.HttpOptions(client_args={"transport": httpx.MockTransport(recording_handler)})
    return genai.Client(api_key="offline-test-not-a-key", http_options=options), requests


def _reply(*parts: dict):
    body = {"candidates": [{"content": {"role": "model", "parts": list(parts)}}]}
    return lambda request: httpx.Response(200, request=request, json=body)


def _inline_png() -> dict:
    return {"inlineData": {"mimeType": "image/png", "data": base64.b64encode(PNG).decode()}}


def _body(request: httpx.Request) -> dict:
    return json.loads(request.read())


@pytest.fixture(autouse=True)
def _no_provider_keys(monkeypatch):
    for name in ("GOOGLE_API_KEY", "GEMINI_API_KEY", "GOOGLE_GENAI_USE_VERTEXAI"):
        monkeypatch.delenv(name, raising=False)


def test_scene_gen_requests_an_image_and_decodes_it():
    client, requests = _client(_reply(_inline_png()))

    data = gemini_scene_gen.generate_scene(client, "rose-gold atelier at dusk")

    assert data is not None, "generate_scene swallowed an SDK error and returned None"
    assert Image.open(io.BytesIO(data)).size == (4, 4)
    (request,) = requests
    assert request.url.path.endswith(f"/models/{gemini_scene_gen.MODEL_ID}:generateContent")
    assert request.headers["x-goog-api-key"] == "offline-test-not-a-key"
    body = _body(request)
    assert body["contents"][0]["parts"][0]["text"] == "rose-gold atelier at dusk"
    assert body["generationConfig"]["responseModalities"] == ["IMAGE"]
    assert body["generationConfig"]["imageConfig"]["aspectRatio"] == "16:9"


def test_scene_gen_reports_a_text_only_reply_as_no_image():
    client, _ = _client(_reply({"text": "cannot draw that"}))

    assert gemini_scene_gen.generate_scene(client, "scene") is None


def test_tournament_gemini_judge_sends_thinking_and_schema(tmp_path: Path):
    source = tmp_path / "source.png"
    candidate = tmp_path / "candidate.png"
    source.write_bytes(PNG)
    candidate.write_bytes(PNG)
    verdict = json.dumps({"overall": 88})
    client, requests = _client(_reply({"text": verdict}))

    text = tournament._judge_call_gemini(
        client, source, candidate, "", "image/png", "", "image/png", "spec text"
    )

    assert json.loads(text) == {"overall": 88}
    (request,) = requests
    assert request.url.path.endswith(f"/models/{tournament.GEMINI_JUDGE_MODEL}:generateContent")
    body = _body(request)
    config = body["generationConfig"]
    # The SDK emits this nested key in snake_case (1.59 and 2.29 alike); proto
    # JSON accepts either spelling, so pin the value, not the casing.
    thinking = config["thinkingConfig"]
    assert thinking.get("thinkingBudget", thinking.get("thinking_budget")) == -1
    assert config["responseMimeType"] == "application/json"
    assert config["maxOutputTokens"] == 16384
    assert "responseSchema" in config or "responseJsonSchema" in config
    inline = [p["inlineData"] for p in body["contents"][0]["parts"] if "inlineData" in p]
    assert [part["data"] for part in inline] == [base64.b64encode(PNG).decode()] * 2


def test_lookbook_request_shape_round_trips():
    """The exact objects scripts/gemini_lookbook.py builds and reads."""
    client, requests = _client(_reply({"text": "styled"}, _inline_png()))
    parts = [
        types.Part.from_bytes(data=PNG, mime_type="image/jpeg"),
        types.Part.from_text(text="place the garments"),
    ]

    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=types.Content(parts=parts, role="user"),
        config=types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"], temperature=0.8),
    )

    images = [
        part.inline_data.data
        for part in response.candidates[0].content.parts
        if part.inline_data and part.inline_data.mime_type.startswith("image/")
    ]
    assert images == [PNG]
    body = _body(requests[0])
    assert body["contents"][0]["role"] == "user"
    assert body["contents"][0]["parts"][1]["text"] == "place the garments"
    assert body["generationConfig"] == {"responseModalities": ["IMAGE", "TEXT"], "temperature": 0.8}
