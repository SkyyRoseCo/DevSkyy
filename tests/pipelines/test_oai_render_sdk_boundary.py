"""OAIImageClient against the real openai SDK, with only the HTTP transport faked.

The other oai_render tests fake the client wrapper, so an SDK upgrade that
changed request encoding, ``with_raw_response`` headers or ``parse()`` would
pass them unnoticed. These tests build the real ``openai.OpenAI`` client and
swap in a mock transport, so every byte the SDK sends and parses is exercised
and no request leaves the process.
"""

from __future__ import annotations

import base64
import importlib
from pathlib import Path

import openai
import pytest

from scripts.oai_render import config
from scripts.oai_render.client import OAIImageClient

PNG_BYTES = b"\x89PNG\r\n\x1a\nfake-image-payload"

# openai 3.x moved its transport to httpx2; earlier majors use httpx.
_HTTP = importlib.import_module("httpx2" if int(openai.__version__.split(".")[0]) >= 3 else "httpx")


def _install_transport(monkeypatch, handler) -> list:
    """Make OAIImageClient build a real OpenAI client over a mock transport."""
    requests: list = []

    def recording_handler(request):
        requests.append(request)
        return handler(request)

    real_openai = openai.OpenAI

    def offline_openai(**kwargs):
        client = _HTTP.Client(transport=_HTTP.MockTransport(recording_handler))
        return real_openai(**kwargs, http_client=client)

    monkeypatch.setattr(openai, "OpenAI", offline_openai)
    monkeypatch.setenv(config.API_KEY_ENV, "sk-offline-test-not-a-key")
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    return requests


def _image_response(request, *, request_id: str | None = "req_offline_123"):
    headers = {"x-request-id": request_id} if request_id else {}
    body = {"created": 0, "data": [{"b64_json": base64.b64encode(PNG_BYTES).decode()}]}
    return _HTTP.Response(200, request=request, headers=headers, json=body)


@pytest.fixture
def reference(tmp_path: Path) -> Path:
    path = tmp_path / "front.png"
    path.write_bytes(PNG_BYTES)
    return path


def test_edit_round_trips_through_the_real_sdk(monkeypatch, reference):
    requests = _install_transport(monkeypatch, _image_response)

    result = OAIImageClient().edit_with_metadata(prompt="studio render", image_paths=[reference])

    assert result.data == PNG_BYTES
    assert result.request_id == "req_offline_123"
    assert result.sdk_version == openai.__version__
    (request,) = requests
    assert request.method == "POST"
    assert request.url.path == "/v1/images/edits"
    assert request.headers["authorization"] == "Bearer sk-offline-test-not-a-key"
    body = request.read()
    assert request.headers["content-type"].startswith("multipart/form-data")
    assert config.MODEL.encode() in body
    assert b"studio render" in body
    assert PNG_BYTES in body


def test_edit_refuses_a_response_without_request_id(monkeypatch, reference):
    _install_transport(monkeypatch, lambda request: _image_response(request, request_id=None))

    with pytest.raises(RuntimeError, match="x-request-id"):
        OAIImageClient().edit_with_metadata(prompt="studio render", image_paths=[reference])


def test_generate_round_trips_through_the_real_sdk(monkeypatch):
    requests = _install_transport(monkeypatch, _image_response)

    assert OAIImageClient().generate(prompt="scene backdrop") == PNG_BYTES
    (request,) = requests
    assert request.url.path == "/v1/images/generations"
    assert b"scene backdrop" in request.read()


def test_rate_limit_surfaces_as_the_sdk_error_class(monkeypatch, reference):
    """A 429 must map to openai.RateLimitError, the class the retry loop keys on."""
    _install_transport(
        monkeypatch,
        lambda request: _HTTP.Response(
            429, request=request, json={"error": {"message": "slow down", "type": "rate_limit"}}
        ),
    )

    with pytest.raises(openai.RateLimitError):
        OAIImageClient().edit_with_metadata(prompt="studio render", image_paths=[reference])
