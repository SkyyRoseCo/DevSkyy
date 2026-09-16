"""Raw-HTTP client for the OpenAI Agents API (beta, multi-agent sessions).

The pinned ``openai`` SDK in this repo (``openai>=1.6,<3``, see pyproject and
bug-254) has no Agents API surface, so this module talks to the REST endpoints
directly with ``httpx``. Every request carries the ``OpenAI-Beta: agents=v1``
header the beta requires.

Spend discipline: ``create_session`` is the only paid call in this module and
is dry-run by default -- it prints a STOP-AND-SHOW manifest and refuses to POST
unless ``confirm=True`` is passed explicitly. ``check_access`` (a bare
``GET /v1/agents/sessions``) is the one zero-cost live probe.
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

import httpx

PROJECT_ROOT = Path(__file__).resolve().parents[1]
try:  # pragma: no cover - optional dependency guard
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / ".env", override=False)
except ImportError:  # pragma: no cover - environment already populated by caller
    pass

API_KEY_ENV = "OPENAI_API_KEY"
OPENAI_API_BASE = "https://api.openai.com/v1"
AGENTS_SESSIONS_URL = f"{OPENAI_API_BASE}/agents/sessions"
MODELS_URL = f"{OPENAI_API_BASE}/models"
AGENTS_BETA_HEADER = "OpenAI-Beta"
AGENTS_BETA_VALUE = "agents=v1"
DEFAULT_MAX_CONCURRENT_SUBAGENTS = 6
REQUEST_TIMEOUT_S = 60.0
STREAM_READ_TIMEOUT_S = 300.0

EVENT_TURN_COMPLETED = "agent.session.turn.completed"
EVENT_TURN_FAILED = "agent.session.turn.failed"
EVENT_TURN_CANCELLED = "agent.session.turn.cancelled"
EVENT_SESSION_FAILED = "agent.session.failed"
EVENT_SESSION_IDLE = "agent.session.idle"
EVENT_SUBAGENT_CREATED = "agent.session.subagent.created"
EVENT_ITEM_ADDED = "agent.session.turn.item.added"
EVENT_ITEM_DONE = "agent.session.turn.item.done"
DELEGATION_ITEM_TYPES = frozenset(
    {
        "create_subagent_call",
        "send_subagent_input_call",
        "wait_for_subagents_call",
        "interrupt_subagent_call",
    }
)


class AgentsApiError(RuntimeError):
    """Base error for Agents API failures."""


class PaidCallNotConfirmed(AgentsApiError):
    """Raised when a paid session create is attempted without ``confirm=True``."""


class TerminalState(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SESSION_FAILED = "session_failed"
    IDLE_AMBIGUOUS = "idle_ambiguous"
    DISCONNECTED = "disconnected"
    NO_TERMINAL_EVENT = "no_terminal_event"


_TERMINAL_EVENTS: dict[str, TerminalState] = {
    EVENT_TURN_COMPLETED: TerminalState.COMPLETED,
    EVENT_TURN_FAILED: TerminalState.FAILED,
    EVENT_TURN_CANCELLED: TerminalState.CANCELLED,
    EVENT_SESSION_FAILED: TerminalState.SESSION_FAILED,
}


def get_api_key() -> str:
    """Return ``OPENAI_API_KEY`` from the environment or raise a clear error."""
    key = os.environ.get(API_KEY_ENV, "").strip()
    if not key:
        raise AgentsApiError(
            f"{API_KEY_ENV} not set. Add it to the project root .env or export it "
            "for this process and retry."
        )
    return key


@dataclass(frozen=True)
class MultiAgentConfig:
    enabled: bool = True
    max_concurrent_subagents: int | None = None

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"enabled": self.enabled}
        if self.max_concurrent_subagents is not None:
            payload["max_concurrent_subagents"] = self.max_concurrent_subagents
        return payload


@dataclass(frozen=True)
class AgentSpec:
    model: str
    instructions: str
    multi_agent: MultiAgentConfig = field(default_factory=MultiAgentConfig)

    def to_payload(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "instructions": self.instructions,
            "multi_agent": self.multi_agent.to_payload(),
        }


@dataclass(frozen=True)
class SessionRequest:
    """A ``POST /v1/agents/sessions`` body.

    ``environment_type="none"`` means the agents only reason over ``input``;
    the first turn must then be supplied in the create call.
    """

    agent: AgentSpec
    input: str
    environment_type: str = "none"
    stream: bool = True

    def to_payload(self) -> dict[str, Any]:
        return {
            "agent": self.agent.to_payload(),
            "environment": {"type": self.environment_type},
            "input": self.input,
            "stream": self.stream,
        }


def format_session_manifest(request: SessionRequest, task_label: str = "") -> str:
    """Render the STOP-AND-SHOW manifest shown before any paid session create."""
    ma = request.agent.multi_agent
    cap = ma.max_concurrent_subagents if ma.max_concurrent_subagents else "default (6)"
    input_bytes = len(request.input.encode("utf-8"))
    lines = [
        "STOP — Confirm before proceeding (paid OpenAI Agents API session):",
        "",
        f"  Action      : POST {AGENTS_SESSIONS_URL}",
        f"  Model       : {request.agent.model}",
        f"  Task        : {task_label or '(unlabelled)'}",
        f"  Environment : {request.environment_type}",
        f"  Multi-agent : enabled={str(ma.enabled).lower()}, max_concurrent_subagents={cap}",
        f"  Instructions: {len(request.agent.instructions)} chars",
        f"  Input       : {input_bytes} bytes ({len(request.input)} chars)",
        f"  Stream      : {str(request.stream).lower()}",
        "  Cost        : metered by OpenAI per token for the coordinator AND every "
        "subagent it spawns;",
        "                not estimable before the run — treat as real spend.",
        "",
        "Proceed? [y/N]",
    ]
    return "\n".join(lines)


@dataclass(frozen=True)
class StreamEvent:
    type: str
    data: dict[str, Any]


@dataclass(frozen=True)
class DelegationItem:
    item_type: str
    agent_id: str | None
    event_type: str


@dataclass(frozen=True)
class TurnOutcome:
    state: TerminalState
    session_id: str | None
    events: tuple[StreamEvent, ...]
    subagent_ids: tuple[str, ...]
    delegations: tuple[DelegationItem, ...]
    output_text: str
    error: str | None = None

    @property
    def succeeded(self) -> bool:
        """Turn reached ``turn.completed``. Callers must still read ``output_text``."""
        return self.state is TerminalState.COMPLETED


@dataclass(frozen=True)
class TurnRecord:
    turn_id: str
    subagent_id: str | None
    raw: dict[str, Any]

    @property
    def is_coordinator(self) -> bool:
        return self.subagent_id is None


@dataclass(frozen=True)
class AccessProbe:
    ok: bool
    status_code: int | None
    detail: str


def parse_sse(lines: Iterable[str]) -> Iterator[StreamEvent]:
    """Yield events from server-sent-event lines (``event:`` / ``data:`` blocks)."""
    event_type = ""
    data_lines: list[str] = []
    for raw in lines:
        line = raw.rstrip("\r\n")
        if not line:
            if data_lines:
                yield _finish_event(event_type, data_lines)
            event_type, data_lines = "", []
            continue
        if line.startswith(":"):
            continue
        key, _, value = line.partition(":")
        value = value[1:] if value.startswith(" ") else value
        if key == "event":
            event_type = value
        elif key == "data":
            data_lines.append(value)
    if data_lines:
        yield _finish_event(event_type, data_lines)


def _finish_event(event_type: str, data_lines: list[str]) -> StreamEvent:
    payload = "\n".join(data_lines)
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        data = {"raw": payload}
    if not isinstance(data, dict):
        data = {"value": data}
    resolved = event_type or str(data.get("type", ""))
    return StreamEvent(type=resolved, data=data)


def classify_event(event_type: str) -> TerminalState | None:
    """Map a stream event type to a terminal state; ``None`` for non-terminal events."""
    if event_type in _TERMINAL_EVENTS:
        return _TERMINAL_EVENTS[event_type]
    if event_type == EVENT_SESSION_IDLE:
        return TerminalState.IDLE_AMBIGUOUS
    return None


def _extract_session_id(data: dict[str, Any]) -> str | None:
    direct = data.get("session_id")
    if isinstance(direct, str) and direct:
        return direct
    session = data.get("session")
    if isinstance(session, dict) and isinstance(session.get("id"), str):
        return session["id"]
    return None


def _extract_subagent_id(data: dict[str, Any]) -> str | None:
    for key in ("subagent_id", "agent_id", "id"):
        value = data.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _extract_text(data: dict[str, Any]) -> str:
    for key in ("output_text", "text"):
        value = data.get(key)
        if isinstance(value, str):
            return value
    return ""


def _delegation_from_item_event(event: StreamEvent) -> DelegationItem | None:
    item = event.data.get("item")
    if not isinstance(item, dict):
        return None
    item_type = item.get("type")
    if item_type not in DELEGATION_ITEM_TYPES:
        return None
    agent_id = item.get("agent_id")
    return DelegationItem(
        item_type=str(item_type),
        agent_id=agent_id if isinstance(agent_id, str) else None,
        event_type=event.type,
    )


def consume_turn(events: Iterable[StreamEvent]) -> TurnOutcome:
    """Fold a stream into a ``TurnOutcome``.

    ``agent.session.idle`` alone never counts as success. A stream that ends
    (or raises an httpx transport error) before any terminal event is
    classified ``DISCONNECTED`` so the caller retrieves the session before
    retrying instead of blindly resubmitting.
    """
    seen: list[StreamEvent] = []
    subagents: list[str] = []
    delegations: list[DelegationItem] = []
    session_id: str | None = None
    state = TerminalState.NO_TERMINAL_EVENT
    output_text = ""
    error: str | None = None
    try:
        for event in events:
            seen.append(event)
            session_id = session_id or _extract_session_id(event.data)
            if event.type == EVENT_SUBAGENT_CREATED:
                sub_id = _extract_subagent_id(event.data)
                if sub_id:
                    subagents.append(sub_id)
            elif event.type in (EVENT_ITEM_ADDED, EVENT_ITEM_DONE):
                delegation = _delegation_from_item_event(event)
                if delegation:
                    delegations.append(delegation)
            terminal = classify_event(event.type)
            if terminal is TerminalState.IDLE_AMBIGUOUS:
                if state is TerminalState.NO_TERMINAL_EVENT:
                    state = terminal
                continue
            if terminal is not None:
                state = terminal
                output_text = _extract_text(event.data) or output_text
                if terminal is not TerminalState.COMPLETED:
                    error = json.dumps(event.data.get("error", event.data), sort_keys=True)
                break
    except httpx.HTTPError as exc:
        state = TerminalState.DISCONNECTED
        error = f"{type(exc).__name__}: {exc}"
    if state is TerminalState.NO_TERMINAL_EVENT and not seen:
        state = TerminalState.DISCONNECTED
        error = error or "stream closed before any event"
    return TurnOutcome(
        state=state,
        session_id=session_id,
        events=tuple(seen),
        subagent_ids=tuple(subagents),
        delegations=tuple(delegations),
        output_text=output_text,
        error=error,
    )


class AgentsApiClient:
    """Minimal synchronous client for ``/v1/agents/sessions``."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        transport: httpx.BaseTransport | None = None,
        timeout: float = REQUEST_TIMEOUT_S,
    ) -> None:
        self._api_key = api_key or get_api_key()
        self._http = httpx.Client(
            transport=transport,
            timeout=httpx.Timeout(timeout, read=STREAM_READ_TIMEOUT_S),
            headers=self._headers(),
        )

    def __repr__(self) -> str:
        return "AgentsApiClient(api_key=<redacted>)"

    def __enter__(self) -> AgentsApiClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        self._http.close()

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            AGENTS_BETA_HEADER: AGENTS_BETA_VALUE,
            "Content-Type": "application/json",
        }

    def probe_access(self) -> AccessProbe:
        """Zero-cost ``GET /v1/agents/sessions``; ok only on HTTP 200."""
        return self._probe(AGENTS_SESSIONS_URL)

    def check_access(self) -> bool:
        return self.probe_access().ok

    def probe_model(self, model: str) -> AccessProbe:
        """Zero-cost ``GET /v1/models/{model}``; 404 means the key cannot use it."""
        return self._probe(f"{MODELS_URL}/{model}")

    def _probe(self, url: str) -> AccessProbe:
        try:
            response = self._http.get(url)
        except httpx.HTTPError as exc:
            return AccessProbe(False, None, f"{type(exc).__name__}: {exc}")
        detail = _error_excerpt(response) if response.status_code != 200 else "ok"
        return AccessProbe(response.status_code == 200, response.status_code, detail)

    def dry_run(self, request: SessionRequest, task_label: str = "") -> str:
        """Return the manifest without touching the network."""
        return format_session_manifest(request, task_label)

    def create_session(
        self,
        request: SessionRequest,
        *,
        confirm: bool = False,
        task_label: str = "",
        echo: Callable[[str], None] = print,
    ) -> TurnOutcome:
        """Create a session and consume its first streamed turn. PAID.

        Always prints the manifest first; refuses to POST unless ``confirm``.
        """
        echo(format_session_manifest(request, task_label))
        if not confirm:
            raise PaidCallNotConfirmed(
                "Session create is a paid call and was not confirmed. "
                "Re-run with confirm=True after the manifest is approved."
            )
        payload = request.to_payload()
        if not request.stream:
            response = self._http.post(AGENTS_SESSIONS_URL, json=payload)
            _raise_for_status(response, "create session")
            return consume_turn(_events_from_json_body(response.json()))
        with self._http.stream("POST", AGENTS_SESSIONS_URL, json=payload) as response:
            _raise_for_status(response, "create session")
            return consume_turn(parse_sse(response.iter_lines()))

    def get_session(self, session_id: str) -> dict[str, Any]:
        """Retrieve a session — call this before retrying a disconnected stream."""
        response = self._http.get(f"{AGENTS_SESSIONS_URL}/{session_id}")
        _raise_for_status(response, "get session")
        return response.json()

    def recover_after_disconnect(self, outcome: TurnOutcome) -> dict[str, Any] | None:
        """Retrieval-before-retry: fetch the saved session state, never resubmit blindly."""
        if outcome.state is not TerminalState.DISCONNECTED or not outcome.session_id:
            return None
        return self.get_session(outcome.session_id)

    def get_turn(self, session_id: str, turn_id: str) -> TurnRecord:
        """Fetch a turn; ``subagent_id`` is ``None`` for the coordinator's own turns."""
        response = self._http.get(f"{AGENTS_SESSIONS_URL}/{session_id}/turns/{turn_id}")
        _raise_for_status(response, "get turn")
        raw = response.json()
        subagent_id = raw.get("subagent_id")
        return TurnRecord(
            turn_id=str(raw.get("id", turn_id)),
            subagent_id=subagent_id if isinstance(subagent_id, str) else None,
            raw=raw,
        )

    def delete_session(self, session_id: str) -> bool:
        response = self._http.delete(f"{AGENTS_SESSIONS_URL}/{session_id}")
        _raise_for_status(response, "delete session")
        return True


def _events_from_json_body(body: Any) -> Iterator[StreamEvent]:
    if isinstance(body, dict):
        events = body.get("events")
        if isinstance(events, list):
            for item in events:
                if isinstance(item, dict):
                    yield StreamEvent(type=str(item.get("type", "")), data=item)
            return
        yield StreamEvent(type=str(body.get("type", "")), data=body)


def _error_excerpt(response: httpx.Response, limit: int = 300) -> str:
    try:
        body = response.read().decode("utf-8", errors="replace")
    except httpx.HTTPError:
        body = ""
    return body[:limit] or f"HTTP {response.status_code}"


def _raise_for_status(response: httpx.Response, action: str) -> None:
    if response.status_code < 400:
        return
    raise AgentsApiError(
        f"{action} failed: HTTP {response.status_code} — {_error_excerpt(response)}"
    )
