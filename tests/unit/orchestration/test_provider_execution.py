"""Offline state/dispatch regressions; no paid provider requests."""

import asyncio
import importlib.util
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "provider_execution_under_test", ROOT / "orchestration/provider_execution.py"
)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def request(**updates):
    value = dict(
        mission={k: "Concrete " + k for k in m.FIELDS},
        provider="example",
        model="configured-model",
        max_calls=3,
        max_output_tokens=128,
        timeout_seconds=10,
        tools=[],
        authorize_paid=True,
        max_cost_usd=1,
    )
    value.update(updates)
    return value


@pytest.fixture(autouse=True)
def tariff(monkeypatch):
    monkeypatch.setenv(
        "GODMODE_MODEL_PRICES",
        json.dumps(
            {
                "example/configured-model": {
                    "input_per_million": 1,
                    "output_per_million": 2,
                }
            }
        ),
    )


@pytest.fixture
def store(tmp_path):
    return m.RunStore(tmp_path / "runs.sqlite3")


class Adapter:
    def __init__(self, outputs):
        self.outputs = iter(outputs)
        self.calls = []
        self.closed = False

    async def complete(self, provider, model, messages, max_tokens):
        self.calls.append((provider, model, list(messages), max_tokens))
        result = next(self.outputs)
        if isinstance(result, Exception):
            raise result
        return dict(
            content=json.dumps(result), model=model, input_tokens=20, output_tokens=30
        )

    async def close(self):
        self.closed = True


class Tools:
    def __init__(self):
        self.calls = []

    def specs(self, names):
        return [{"name": n} for n in names]

    async def execute(self, name, arguments):
        self.calls.append((name, arguments))
        return {"evidence": "actual tool response"}


def run(store, req, adapter, tools=None):
    record, _ = store.reserve("owner", "unique-key", req)
    asyncio.run(
        m.execute_run(store, "owner", record["id"], req, adapter, tools or Tools())
    )
    return store.get("owner", record["id"])


def test_final_has_receipt_but_no_acceptance(store):
    adapter = Adapter([{"action": "final", "output": "Completed draft"}])
    result = run(store, request(), adapter)
    assert result["state"] == "completed"
    assert result["verification"] == "NOT_RUN"
    assert result["release"] == "NOT_DEPLOYED"
    assert len(result["output_sha256"]) == 64
    assert adapter.closed and len(adapter.calls) == 1


def test_tools_reach_provider_with_context(store):
    adapter = Adapter(
        [
            {"action": "tool", "name": "lookup", "arguments": {"sku": "x"}},
            {"action": "final", "output": "Grounded deliverable"},
        ]
    )
    tools = Tools()
    result = run(store, request(tools=["lookup"]), adapter, tools)
    assert result["state"] == "completed"
    assert tools.calls == [("lookup", {"sku": "x"})]
    assert "actual tool response" in adapter.calls[1][2][-1]["content"]


def test_non_allowlisted_tool_never_executes(store):
    tools = Tools()
    result = run(
        store,
        request(),
        Adapter([{"action": "tool", "name": "shell", "arguments": {}}]),
        tools,
    )
    assert result["state"] == "failed" and tools.calls == []


def test_call_budget(store):
    adapter = Adapter([{"action": "tool", "name": "lookup", "arguments": {}}] * 4)
    result = run(store, request(max_calls=2, tools=["lookup"]), adapter)
    assert result["state"] == "failed" and len(adapter.calls) == 2


def test_atomic_duplicate_reservation(store):
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(
            pool.map(
                lambda _: store.reserve("owner", "unique-key", request()), range(8)
            )
        )
    assert sum(created for _, created in results) == 1
    assert len({record["id"] for record, _ in results}) == 1


def test_conflicting_key(store):
    store.reserve("owner", "unique-key", request())
    with pytest.raises(m.RunError, match="different inputs"):
        store.reserve("owner", "unique-key", request(max_calls=2))


def test_owner_isolation(store):
    record, _ = store.reserve("owner", "unique-key", request())
    with pytest.raises(KeyError):
        store.get("other", record["id"])
    with pytest.raises(KeyError):
        store.update("other", record["id"], state="cancel_requested")


def test_expired_run_is_unknown_never_resubmitted(store):
    record, _ = store.reserve("owner", "unique-key", request())
    with store.db() as db:
        db.execute("UPDATE provider_runs SET deadline=?", (time.time() - 1,))
    result, created = store.reserve("owner", "unique-key", request())
    assert result["state"] == "unknown" and not created


def test_cancel_before_start(store):
    req = request()
    record, _ = store.reserve("owner", "unique-key", req)
    store.update("owner", record["id"], state="cancel_requested")
    adapter = Adapter([])
    asyncio.run(m.execute_run(store, "owner", record["id"], req, adapter, Tools()))
    assert not adapter.calls


def test_cancel_wins_completion_race(store):
    record, _ = store.reserve("owner", "unique-key", request())
    store.update("owner", record["id"], state="running")
    store.update("owner", record["id"], state="cancel_requested")
    result = store.update(
        "owner", record["id"], state="completed", output="late result"
    )
    assert result["state"] == "cancelled" and result["output"] is None


def test_provider_failure_not_retried_or_leaked(store):
    adapter = Adapter([RuntimeError("SECRET provider diagnostic")])
    result = run(store, request(), adapter)
    assert len(adapter.calls) == 1 and "SECRET" not in json.dumps(result)


@pytest.mark.parametrize(
    "updates",
    [
        dict(authorize_paid=False),
        dict(max_calls=True),
        dict(max_calls=9),
        dict(tools=["x", "x"]),
        dict(model=""),
        dict(timeout_seconds=0),
    ],
)
def test_invalid_requests(updates):
    with pytest.raises(m.RunError):
        m.validate_request(request(**updates))


def test_valid_request():
    assert m.validate_request(request())["provider"] == "example"


def test_budget_refuses_before_paid_call(store):
    adapter = Adapter([])
    result = run(store, request(max_cost_usd=0.000001), adapter)
    assert result["state"] == "failed" and not adapter.calls


def test_claim_does_not_overwrite_cancellation(store):
    record, _ = store.reserve("owner", "unique-key", request())
    store.update("owner", record["id"], state="cancel_requested")
    assert (
        store.update("owner", record["id"], state="running", expected="queued") is None
    )
    assert store.get("owner", record["id"])["state"] == "cancel_requested"


def test_terminal_state_survives_late_updates(store):
    record, _ = store.reserve("owner", "unique-key", request())
    store.update("owner", record["id"], state="completed", output="done")
    with store.db() as db:
        db.execute("UPDATE provider_runs SET deadline=?", (time.time() - 1,))
    assert store.get("owner", record["id"])["state"] == "completed"
    assert (
        store.update("owner", record["id"], state="cancel_requested")["state"]
        == "completed"
    )


def test_missing_pricing_refuses_call(store, monkeypatch):
    monkeypatch.delenv("GODMODE_MODEL_PRICES")
    adapter = Adapter([])
    result = run(store, request(), adapter)
    assert result["state"] == "failed" and not adapter.calls


def test_http_owner_gate_and_end_to_end(tmp_path, monkeypatch):
    """Exercise actual ASGI routes with a synthetic auth dependency and provider."""
    import types
    from dataclasses import dataclass

    from fastapi import FastAPI, HTTPException
    from fastapi.testclient import TestClient

    @dataclass
    class User:
        sub: str
        roles: list[str]

    def auth():
        raise HTTPException(401, "Not authenticated")

    security = types.ModuleType("security.jwt_oauth2_auth")
    security.TokenPayload = User
    security.get_current_user = auth
    monkeypatch.setitem(sys.modules, "security.jwt_oauth2_auth", security)
    monkeypatch.setitem(sys.modules, "orchestration.provider_execution", m)
    api_spec = importlib.util.spec_from_file_location(
        "execution_api_under_test", ROOT / "api/v1/provider_execution.py"
    )
    api = importlib.util.module_from_spec(api_spec)
    api_spec.loader.exec_module(api)

    class ReadyAdapter(Adapter):
        def __init__(self):
            super().__init__(
                [{"action": "final", "output": "Verified transport result"}]
            )

        def providers(self):
            return [
                {
                    "id": "example",
                    "default_model": "configured-model",
                    "models": ["configured-model"],
                    "enabled": True,
                    "configured": True,
                }
            ]

    class ReadyTools(Tools):
        def __init__(self, owner):
            super().__init__()
            self.allowed = set()

    monkeypatch.setattr(api, "RouterAdapter", ReadyAdapter)
    monkeypatch.setattr(api, "RegistryTools", ReadyTools)
    monkeypatch.setenv("GODMODE_RUN_DB", str(tmp_path / "api.sqlite3"))
    monkeypatch.setenv("GODMODE_EXECUTION_ENABLED", "1")
    monkeypatch.setenv("GODMODE_EXECUTION_INSTANCE", __import__("socket").gethostname())
    monkeypatch.delenv("FLY_MACHINE_ID", raising=False)
    app = FastAPI()
    app.include_router(api.router, prefix="/api/v1/orchestration")
    base = "/api/v1/orchestration/god-mode"
    with TestClient(app) as client:
        assert client.get(base + "/providers").status_code == 401
        app.dependency_overrides[auth] = lambda: User("owner", ["user"])
        assert client.get(base + "/providers").status_code == 403
        app.dependency_overrides[auth] = lambda: User("owner", ["admin"])
        assert client.get(base + "/providers").status_code == 200
        submitted = client.post(
            base + "/runs", json=request(), headers={"Idempotency-Key": "http-key"}
        )
        assert submitted.status_code == 202
        run_id = submitted.json()["id"]
        for _ in range(50):
            result = client.get(base + "/runs/" + run_id).json()
            if result["state"] not in m.ACTIVE:
                break
        assert result["state"] == "completed"
        assert (
            client.post(
                base + "/runs", json=request(), headers={"Idempotency-Key": "http-key"}
            ).json()["id"]
            == run_id
        )
        # Recovery must survive disabled execution and removed provider/tool policy.
        monkeypatch.setenv("GODMODE_EXECUTION_ENABLED", "0")
        def forbidden_adapter():
            raise AssertionError("Replay must not construct a provider")
        monkeypatch.setattr(api, "RouterAdapter", forbidden_adapter)
        replay = client.post(
            base + "/runs", json=request(), headers={"Idempotency-Key": "http-key"}
        )
        assert replay.status_code == 202 and replay.json()["id"] == run_id
        conflict = client.post(
            base + "/runs", json=request(max_calls=2), headers={"Idempotency-Key": "http-key"}
        )
        assert conflict.status_code == 409
        fresh = client.post(
            base + "/runs", json=request(), headers={"Idempotency-Key": "fresh-key"}
        )
        assert fresh.status_code == 503
        app.dependency_overrides[auth] = lambda: User("other", ["admin"])
        assert client.get(base + "/runs/" + run_id).status_code == 404
