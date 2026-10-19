"""Tests for integrations/openai_agents_api.py — all HTTP mocked, no live calls.

Covers:
    - Manifest formatting (STOP-AND-SHOW block)
    - Dry-run-by-default: create_session refuses to POST without confirm=True
    - Beta header + bearer auth on every request; repr redacts the key
    - Zero-cost access / model probes (200 ok, 4xx denied, transport error)
    - SSE parsing and terminal-state classification (idle is NOT success)
    - Subagent id + delegation item collection, disconnect handling
    - get_turn attribution, delete_session, retrieval-before-retry
"""

from __future__ import annotations

import json
from collections.abc import Iterator

import httpx
import pytest

from integrations.openai_agents_api import (
    AGENTS_BETA_HEADER,
    AGENTS_BETA_VALUE,
    AGENTS_SESSIONS_URL,
    AgentsApiClient,
    AgentsApiError,
    AgentSpec,
    MultiAgentConfig,
    PaidCallNotConfirmed,
    SessionRequest,
    StreamEvent,
    TerminalState,
    classify_event,
    consume_turn,
    format_session_manifest,
    get_api_key,
    parse_sse,
)


class Recorder:
    """httpx mock transport that records requests and replays canned responses."""

    def __init__(self, responses: list[httpx.Response]) -> None:
        self.responses = list(responses)
        self.requests: list[httpx.Request] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return self.responses.pop(0)

    def transport(self) -> httpx.MockTransport:
        return httpx.MockTransport(self.handler)


def _client(recorder: Recorder) -> AgentsApiClient:
    return AgentsApiClient(api_key="sk-test-secret", transport=recorder.transport())


def _request(model: str = "gpt-6-astra") -> SessionRequest:
    return SessionRequest(
        agent=AgentSpec(
            model=model,
            instructions="coordinate",
            multi_agent=MultiAgentConfig(enabled=True, max_concurrent_subagents=3),
        ),
        input='{"report": true}',
    )


def _sse(*events: tuple[str, dict]) -> bytes:
    chunks = [f"event: {name}\ndata: {json.dumps(data)}\n\n" for name, data in events]
    return "".join(chunks).encode("utf-8")


# ---------------------------------------------------------------------------
# Manifest + payload
# ---------------------------------------------------------------------------


def test_manifest_lists_model_environment_subagents_and_prompt() -> None:
    text = format_session_manifest(_request(), task_label="bug-322 audit")
    assert text.startswith("STOP — Confirm before proceeding")
    assert "Model       : gpt-6-astra" in text
    assert "Task        : bug-322 audit" in text
    assert "Environment : none" in text
    assert "max_concurrent_subagents=3" in text
    assert f"POST {AGENTS_SESSIONS_URL}" in text
    assert text.rstrip().endswith("Proceed? [y/N]")


def test_manifest_shows_default_subagent_cap_when_unset() -> None:
    req = SessionRequest(agent=AgentSpec(model="m", instructions="i"), input="x")
    assert "max_concurrent_subagents=default (6)" in format_session_manifest(req)


def test_payload_shape_matches_vendor_contract() -> None:
    payload = _request().to_payload()
    assert payload == {
        "agent": {
            "model": "gpt-6-astra",
            "instructions": "coordinate",
            "multi_agent": {"enabled": True, "max_concurrent_subagents": 3},
        },
        "environment": {"type": "none"},
        "input": '{"report": true}',
        "stream": True,
    }


# ---------------------------------------------------------------------------
# Credentials + headers
# ---------------------------------------------------------------------------


def test_get_api_key_missing_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(AgentsApiError, match="OPENAI_API_KEY not set"):
        get_api_key()


def test_client_loads_key_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-from-env")
    rec = Recorder([httpx.Response(200, json={"data": []})])
    with AgentsApiClient(transport=rec.transport()) as client:
        assert client.check_access() is True
    assert rec.requests[0].headers["Authorization"] == "Bearer sk-from-env"


def test_repr_redacts_key() -> None:
    rec = Recorder([])
    client = _client(rec)
    assert "sk-test-secret" not in repr(client)
    client.close()


def test_every_request_carries_beta_header_and_bearer() -> None:
    rec = Recorder([httpx.Response(200, json={"data": []})])
    with _client(rec) as client:
        client.check_access()
    request = rec.requests[0]
    assert request.method == "GET"
    assert str(request.url) == AGENTS_SESSIONS_URL
    assert request.headers[AGENTS_BETA_HEADER] == AGENTS_BETA_VALUE
    assert request.headers["Authorization"] == "Bearer sk-test-secret"


# ---------------------------------------------------------------------------
# Zero-cost probes
# ---------------------------------------------------------------------------


def test_probe_access_denied_on_401() -> None:
    rec = Recorder([httpx.Response(401, json={"error": {"message": "bad key"}})])
    with _client(rec) as client:
        probe = client.probe_access()
    assert probe.ok is False
    assert probe.status_code == 401
    assert "bad key" in probe.detail


def test_probe_access_fails_closed_on_transport_error() -> None:
    def boom(_: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("dns down")

    with AgentsApiClient(api_key="k", transport=httpx.MockTransport(boom)) as client:
        probe = client.probe_access()
    assert probe.ok is False
    assert probe.status_code is None
    assert "ConnectError" in probe.detail


def test_probe_model_404_is_not_ok() -> None:
    rec = Recorder([httpx.Response(404, json={"error": {"message": "That model does not exist"}})])
    with _client(rec) as client:
        probe = client.probe_model("gpt-6-astra")
    assert probe.ok is False
    assert str(rec.requests[0].url).endswith("/v1/models/gpt-6-astra")
    assert "does not exist" in probe.detail


# ---------------------------------------------------------------------------
# Dry-run by default
# ---------------------------------------------------------------------------


def test_create_session_without_confirm_prints_manifest_and_never_posts() -> None:
    rec = Recorder([])
    shown: list[str] = []
    with _client(rec) as client:
        with pytest.raises(PaidCallNotConfirmed):
            client.create_session(_request(), echo=shown.append)
    assert rec.requests == []
    assert len(shown) == 1 and "Proceed? [y/N]" in shown[0]


def test_dry_run_returns_manifest_without_network() -> None:
    rec = Recorder([])
    with _client(rec) as client:
        text = client.dry_run(_request(), task_label="t")
    assert "Task        : t" in text
    assert rec.requests == []


def test_create_session_with_confirm_posts_and_streams_completed_turn() -> None:
    body = _sse(
        ("agent.session.created", {"session": {"id": "sess_1"}}),
        ("agent.session.subagent.created", {"subagent_id": "sub_a"}),
        (
            "agent.session.turn.item.done",
            {"item": {"type": "create_subagent_call", "agent_id": "coord"}},
        ),
        ("agent.session.turn.completed", {"output_text": "all three collections audited"}),
    )
    rec = Recorder(
        [httpx.Response(200, content=body, headers={"content-type": "text/event-stream"})]
    )
    with _client(rec) as client:
        outcome = client.create_session(_request(), confirm=True, echo=lambda _: None)
    post = rec.requests[0]
    assert post.method == "POST"
    assert json.loads(post.content)["environment"] == {"type": "none"}
    assert post.headers[AGENTS_BETA_HEADER] == AGENTS_BETA_VALUE
    assert outcome.succeeded
    assert outcome.session_id == "sess_1"
    assert outcome.subagent_ids == ("sub_a",)
    assert [d.item_type for d in outcome.delegations] == ["create_subagent_call"]
    assert outcome.delegations[0].agent_id == "coord"
    assert outcome.output_text == "all three collections audited"


def test_create_session_http_error_raises_clear_message() -> None:
    rec = Recorder([httpx.Response(404, json={"error": {"message": "That model does not exist"}})])
    with _client(rec) as client:
        with pytest.raises(AgentsApiError, match="create session failed: HTTP 404"):
            client.create_session(_request(), confirm=True, echo=lambda _: None)


# ---------------------------------------------------------------------------
# SSE + terminal classification
# ---------------------------------------------------------------------------


def test_parse_sse_handles_multiline_data_comments_and_missing_event_name() -> None:
    lines = [
        ": keepalive",
        "event: agent.session.idle",
        'data: {"a":',
        "data: 1}",
        "",
        'data: {"type": "agent.session.turn.completed", "output_text": "ok"}',
        "",
    ]
    events = list(parse_sse(lines))
    assert events[0] == StreamEvent("agent.session.idle", {"a": 1})
    assert events[1].type == "agent.session.turn.completed"
    assert events[1].data["output_text"] == "ok"


@pytest.mark.parametrize(
    ("event_type", "expected"),
    [
        ("agent.session.turn.completed", TerminalState.COMPLETED),
        ("agent.session.turn.failed", TerminalState.FAILED),
        ("agent.session.turn.cancelled", TerminalState.CANCELLED),
        ("agent.session.failed", TerminalState.SESSION_FAILED),
        ("agent.session.idle", TerminalState.IDLE_AMBIGUOUS),
        ("agent.session.turn.item.added", None),
    ],
)
def test_classify_event(event_type: str, expected: TerminalState | None) -> None:
    assert classify_event(event_type) is expected


def test_idle_alone_is_not_success() -> None:
    outcome = consume_turn([StreamEvent("agent.session.idle", {"session_id": "s"})])
    assert outcome.state is TerminalState.IDLE_AMBIGUOUS
    assert outcome.succeeded is False


def test_idle_before_completed_does_not_mask_completion() -> None:
    outcome = consume_turn(
        [
            StreamEvent("agent.session.idle", {}),
            StreamEvent("agent.session.turn.completed", {"output_text": "done"}),
        ]
    )
    assert outcome.state is TerminalState.COMPLETED
    assert outcome.output_text == "done"


def test_failed_turn_captures_error_payload() -> None:
    outcome = consume_turn(
        [StreamEvent("agent.session.turn.failed", {"error": {"code": "rate_limited"}})]
    )
    assert outcome.state is TerminalState.FAILED
    assert outcome.succeeded is False
    assert "rate_limited" in (outcome.error or "")


def test_cancelled_and_session_failed_are_terminal_non_success() -> None:
    assert consume_turn([StreamEvent("agent.session.turn.cancelled", {})]).state is (
        TerminalState.CANCELLED
    )
    assert consume_turn([StreamEvent("agent.session.failed", {})]).state is (
        TerminalState.SESSION_FAILED
    )


def test_stream_ending_without_terminal_event_is_no_terminal_event() -> None:
    outcome = consume_turn([StreamEvent("agent.session.turn.item.added", {"item": {}})])
    assert outcome.state is TerminalState.NO_TERMINAL_EVENT
    assert outcome.succeeded is False


def test_empty_stream_is_disconnected() -> None:
    outcome = consume_turn([])
    assert outcome.state is TerminalState.DISCONNECTED


def test_transport_error_mid_stream_is_disconnected_and_keeps_session_id() -> None:
    def gen() -> Iterator[StreamEvent]:
        yield StreamEvent("agent.session.created", {"session_id": "sess_9"})
        raise httpx.RemoteProtocolError("peer closed connection")

    outcome = consume_turn(gen())
    assert outcome.state is TerminalState.DISCONNECTED
    assert outcome.session_id == "sess_9"
    assert "RemoteProtocolError" in (outcome.error or "")


# ---------------------------------------------------------------------------
# Session retrieval / attribution / cleanup
# ---------------------------------------------------------------------------


def test_recover_after_disconnect_retrieves_session_before_any_retry() -> None:
    def gen() -> Iterator[StreamEvent]:
        yield StreamEvent("agent.session.created", {"session_id": "sess_9"})
        raise httpx.ReadError("boom")

    outcome = consume_turn(gen())
    rec = Recorder([httpx.Response(200, json={"id": "sess_9", "status": "idle"})])
    with _client(rec) as client:
        saved = client.recover_after_disconnect(outcome)
    assert saved == {"id": "sess_9", "status": "idle"}
    assert rec.requests[0].method == "GET"
    assert str(rec.requests[0].url) == f"{AGENTS_SESSIONS_URL}/sess_9"


def test_recover_after_disconnect_is_noop_for_completed_turn() -> None:
    outcome = consume_turn([StreamEvent("agent.session.turn.completed", {"session_id": "s"})])
    rec = Recorder([])
    with _client(rec) as client:
        assert client.recover_after_disconnect(outcome) is None
    assert rec.requests == []


def test_get_turn_reports_subagent_attribution() -> None:
    rec = Recorder(
        [
            httpx.Response(200, json={"id": "turn_1", "subagent_id": None}),
            httpx.Response(200, json={"id": "turn_2", "subagent_id": "sub_a"}),
        ]
    )
    with _client(rec) as client:
        coordinator = client.get_turn("sess_1", "turn_1")
        delegated = client.get_turn("sess_1", "turn_2")
    assert coordinator.is_coordinator and coordinator.subagent_id is None
    assert delegated.subagent_id == "sub_a" and not delegated.is_coordinator
    assert str(rec.requests[1].url) == f"{AGENTS_SESSIONS_URL}/sess_1/turns/turn_2"


def test_delete_session_issues_delete() -> None:
    rec = Recorder([httpx.Response(200, json={"deleted": True})])
    with _client(rec) as client:
        assert client.delete_session("sess_1") is True
    assert rec.requests[0].method == "DELETE"
    assert str(rec.requests[0].url) == f"{AGENTS_SESSIONS_URL}/sess_1"
