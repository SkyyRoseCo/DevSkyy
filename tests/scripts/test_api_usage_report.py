"""scripts/api_usage_report.py: per-key usage/cost report from provider admin APIs.

The providers are replaced at the HTTP boundary with httpx.MockTransport, which
also asserts the exact requests the script sends (auth headers, query encoding,
pagination). A live run needs real admin keys and is out of scope here.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal
from urllib.parse import parse_qs, urlsplit

import api_usage_report as report
import httpx
import pytest

DAY = "2026-10-17"
DAY_START = datetime(2026, 10, 17, tzinfo=UTC)
DAY_EPOCH = int(DAY_START.timestamp())
ANTHROPIC_KEY = "sk-ant-admin01-test-only"
OPENAI_KEY = "sk-admin-test-only"


@pytest.fixture(autouse=True)
def _isolated_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(report, "ENV_FILES", ())
    monkeypatch.delenv("ANTHROPIC_ADMIN_KEY", raising=False)
    monkeypatch.delenv("OPENAI_ADMIN_KEY", raising=False)


def _anthropic_usage(
    key_id: str | None, model: str, uncached: int, output: int, web: int = 0
) -> dict:
    return {
        "api_key_id": key_id,
        "model": model,
        "uncached_input_tokens": uncached,
        "cache_creation": {"ephemeral_5m_input_tokens": 0, "ephemeral_1h_input_tokens": 0},
        "cache_read_input_tokens": 0,
        "output_tokens": output,
        "server_tool_use": {"web_search_requests": web},
    }


def _anthropic_cost(
    cents: str, token_type: str | None, model: str | None = "claude-x", kind: str = "tokens"
) -> dict:
    return {
        "amount": cents,
        "currency": "USD",
        "cost_type": kind,
        "model": model,
        "token_type": token_type,
        "description": f"{model} {token_type or kind}",
    }


def test_anthropic_cost_is_allocated_by_token_share() -> None:
    usage = [
        _anthropic_usage("apikey_a", "claude-x", uncached=750, output=100, web=3),
        _anthropic_usage("apikey_b", "claude-x", uncached=250, output=300),
    ]
    costs = [
        _anthropic_cost("400", "uncached_input_tokens"),  # $4.00 over 1000 input tokens
        _anthropic_cost("800", "output_tokens"),  # $8.00 over 400 output tokens
        _anthropic_cost("150", None, model=None, kind="web_search"),  # $1.50, not per token
    ]

    result = report.build_anthropic_report(usage, costs, {"apikey_a": "Render key"})

    by_id = {row["key_id"]: row for row in result["keys"]}
    assert result["total_cost_usd"] == "13.5000"
    assert by_id["apikey_a"]["est_cost_usd"] == "5.0000"  # 0.75*4 + 0.25*8
    assert by_id["apikey_b"]["est_cost_usd"] == "7.0000"  # 0.25*4 + 0.75*8
    assert result["unallocated_cost_usd"] == "1.5000"
    assert by_id["apikey_a"]["name"] == "Render key"
    assert by_id["apikey_b"]["name"] == "apikey_b"
    assert by_id["apikey_a"]["models"][0]["web_search_requests"] == 3
    assert [row["key_id"] for row in result["keys"]] == ["apikey_b", "apikey_a"]


def test_anthropic_cost_with_no_matching_usage_stays_unallocated() -> None:
    usage = [_anthropic_usage(None, "claude-x", uncached=10, output=0)]
    costs = [
        _anthropic_cost("100", "uncached_input_tokens"),
        _anthropic_cost("50", "output_tokens", model="claude-y"),
    ]

    result = report.build_anthropic_report(usage, costs, {})

    assert result["keys"][0]["name"] == report.NO_KEY
    assert result["keys"][0]["est_cost_usd"] == "1.0000"
    assert result["unallocated_cost_usd"] == "0.5000"


def test_openai_report_merges_costs_completions_and_images() -> None:
    costs = [
        {
            "api_key_id": "key_1",
            "line_item": "gpt-image-2, images",
            "amount": {"value": 2.4, "currency": "usd"},
        },
        {
            "api_key_id": "key_1",
            "line_item": "gpt-5, input",
            "amount": {"value": 0.1, "currency": "usd"},
        },
        {
            "api_key_id": None,
            "line_item": "gpt-5, input",
            "amount": {"value": 0.05, "currency": "usd"},
        },
    ]
    completions = [
        {
            "api_key_id": "key_1",
            "model": "gpt-5",
            "num_model_requests": 4,
            "input_tokens": 900,
            "input_cached_tokens": 100,
            "output_tokens": 50,
        },
    ]
    images = [{"api_key_id": "key_1", "model": "gpt-image-2", "num_model_requests": 6, "images": 6}]

    result = report.build_openai_report(costs, completions, images, {"key_1": "imagery"})

    first, second = result["keys"]
    assert result["total_cost_usd"] == "2.5500"
    assert (first["name"], first["cost_usd"]) == ("imagery", "2.5000")
    assert (second["name"], second["cost_usd"]) == (report.NO_KEY, "0.0500")
    models = {m["model"]: m for m in first["models"]}
    assert models["gpt-5"]["requests"] == 4 and models["gpt-5"]["cached_input_tokens"] == 100
    assert models["gpt-image-2"]["images"] == 6
    assert Decimal(first["line_items"][0]["cost_usd"]) == Decimal("2.4")


class FakeProviders:
    """Serves both admin APIs and records every request it receives."""

    def __init__(self, anthropic_bucket_start: str = f"{DAY}T00:00:00Z") -> None:
        self.requests: list[httpx.Request] = []
        self.anthropic_bucket_start = anthropic_bucket_start

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        path, query = request.url.path, parse_qs(urlsplit(str(request.url)).query)
        if request.url.host == "api.anthropic.com":
            return self._anthropic(path, query)
        return self._openai(path, query)

    def _bucket(self, results: list[dict]) -> dict:
        return {
            "data": [
                {"starting_at": self.anthropic_bucket_start, "ending_at": "x", "results": results}
            ],
            "has_more": True,
            "next_page": "page_next",
        }

    def _anthropic(self, path: str, query: dict) -> httpx.Response:
        if path.endswith("/usage_report/messages"):
            return httpx.Response(
                200, json=self._bucket([_anthropic_usage("apikey_a", "claude-x", 100, 10)])
            )
        if path.endswith("/cost_report"):
            return httpx.Response(
                200, json=self._bucket([_anthropic_cost("250", "uncached_input_tokens")])
            )
        if path.endswith("/api_keys"):
            if "after_id" not in query:
                return httpx.Response(
                    200,
                    json={
                        "data": [{"id": "apikey_z", "name": "old"}],
                        "has_more": True,
                        "last_id": "apikey_z",
                    },
                )
            return httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": "apikey_a",
                            "name": "elite-studio",
                            "partial_key_hint": "sk-ant-api03-R2D...igAA",
                        }
                    ],
                    "has_more": False,
                    "last_id": "apikey_a",
                },
            )
        return httpx.Response(404, json={"error": {"message": f"unexpected {path}"}})

    @staticmethod
    def _openai_bucket(results: list[dict]) -> dict:
        return {
            "data": [{"start_time": DAY_EPOCH, "end_time": DAY_EPOCH + 86400, "results": results}],
            "has_more": False,
            "next_page": None,
        }

    def _openai(self, path: str, query: dict) -> httpx.Response:
        bucket = self._openai_bucket
        if path.endswith("/costs"):
            return httpx.Response(
                200,
                json=bucket(
                    [
                        {
                            "api_key_id": "key_1",
                            "line_item": "gpt-image-2, images",
                            "amount": {"value": 1.2, "currency": "usd"},
                        }
                    ]
                ),
            )
        if path.endswith("/usage/completions"):
            return httpx.Response(200, json=bucket([]))
        if path.endswith("/usage/images"):
            return httpx.Response(
                200,
                json=bucket(
                    [
                        {
                            "api_key_id": "key_1",
                            "model": "gpt-image-2",
                            "num_model_requests": 3,
                            "images": 3,
                        }
                    ]
                ),
            )
        if path.endswith("/projects"):
            return httpx.Response(
                200, json={"data": [{"id": "proj_1", "name": "DevSkyy"}], "has_more": False}
            )
        if path.endswith("/projects/proj_1/api_keys"):
            return httpx.Response(
                200,
                json={
                    "data": [{"id": "key_1", "name": "renders", "redacted_value": "sk-...abc"}],
                    "has_more": False,
                },
            )
        return httpx.Response(404, json={"error": {"message": f"unexpected {path}"}})


def test_main_queries_both_providers_with_correct_requests(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("ANTHROPIC_ADMIN_KEY", ANTHROPIC_KEY)
    monkeypatch.setenv("OPENAI_ADMIN_KEY", OPENAI_KEY)
    fake = FakeProviders()

    code = report.main(["--date", DAY, "--json"], transport=httpx.MockTransport(fake))

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    anthropic, openai = payload["reports"]
    assert anthropic["keys"][0]["name"] == "elite-studio [sk-ant-api03-R2D...igAA]"
    assert anthropic["total_cost_usd"] == "2.5000"
    assert openai["keys"][0]["name"] == "renders [sk-...abc] (DevSkyy)"
    assert openai["keys"][0]["models"][0]["images"] == 3

    usage_req = next(r for r in fake.requests if r.url.path.endswith("/usage_report/messages"))
    assert usage_req.headers["x-api-key"] == ANTHROPIC_KEY
    assert usage_req.headers["anthropic-version"] == "2023-06-01"
    query = parse_qs(urlsplit(str(usage_req.url)).query)
    assert query["group_by[]"] == ["api_key_id", "model"]
    assert query["starting_at"] == [f"{DAY}T00:00:00Z"]
    assert query["bucket_width"] == ["1d"] and query["limit"] == ["1"]

    costs_req = next(r for r in fake.requests if r.url.path.endswith("/organization/costs"))
    assert costs_req.headers["authorization"] == f"Bearer {OPENAI_KEY}"
    costs_query = parse_qs(urlsplit(str(costs_req.url)).query)
    assert costs_query["group_by"] == ["api_key_id", "line_item"]
    assert costs_query["start_time"] == [str(DAY_EPOCH)]
    assert (
        sum(
            r.url.path.endswith("/api_keys") and r.url.host == "api.anthropic.com"
            for r in fake.requests
        )
        == 2
    )


def test_text_output_lists_keys(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("OPENAI_ADMIN_KEY", OPENAI_KEY)

    code = report.main(
        ["--date", DAY, "--provider", "openai"], transport=httpx.MockTransport(FakeProviders())
    )

    out = capsys.readouterr().out
    assert code == 0
    assert "== OPENAI  total $1.2000" in out
    assert "-- renders [sk-...abc] (DevSkyy)  $1.2000" in out
    assert "gpt-image-2: requests=3, images=3" in out


def test_missing_keys_exit_2(capsys: pytest.CaptureFixture[str]) -> None:
    code = report.main(["--date", DAY], transport=httpx.MockTransport(FakeProviders()))

    err = capsys.readouterr().err
    assert code == 2
    assert "SKIP  anthropic: ANTHROPIC_ADMIN_KEY not set" in err
    assert "SKIP  openai: OPENAI_ADMIN_KEY not set" in err


def test_one_missing_key_skips_only_that_provider(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("ANTHROPIC_ADMIN_KEY", ANTHROPIC_KEY)

    code = report.main(["--date", DAY], transport=httpx.MockTransport(FakeProviders()))

    captured = capsys.readouterr()
    assert code == 0
    assert "== ANTHROPIC" in captured.out and "== OPENAI" not in captured.out
    assert "SKIP  openai" in captured.err


def test_inference_key_is_rejected_before_any_request(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("ANTHROPIC_ADMIN_KEY", "sk-ant-api03-not-an-admin-key")
    fake = FakeProviders()

    code = report.main(
        ["--date", DAY, "--provider", "anthropic"], transport=httpx.MockTransport(fake)
    )

    err = capsys.readouterr().err
    assert code == 1
    assert "not an admin key" in err and "sk-ant-api03-not" not in err
    assert fake.requests == []


def test_http_error_fails_without_leaking_key(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("OPENAI_ADMIN_KEY", OPENAI_KEY)
    denied = httpx.MockTransport(
        lambda request: httpx.Response(401, json={"error": {"message": "Invalid admin key"}})
    )

    code = report.main(["--date", DAY, "--provider", "openai"], transport=denied)

    captured = capsys.readouterr()
    assert code == 1
    assert "HTTP 401: Invalid admin key" in captured.err
    assert OPENAI_KEY not in captured.err + captured.out


def test_wrong_bucket_fails_closed(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("ANTHROPIC_ADMIN_KEY", ANTHROPIC_KEY)
    fake = FakeProviders(anthropic_bucket_start="2026-10-16T00:00:00Z")

    code = report.main(
        ["--date", DAY, "--provider", "anthropic"], transport=httpx.MockTransport(fake)
    )

    assert code == 1
    assert "expected 2026-10-17T00:00:00+00:00" in capsys.readouterr().err


def test_empty_day_reports_no_usage(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("ANTHROPIC_ADMIN_KEY", ANTHROPIC_KEY)

    def empty(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/api_keys"):
            return httpx.Response(200, json={"data": [], "has_more": False})
        return httpx.Response(200, json={"data": [], "has_more": False, "next_page": None})

    code = report.main(
        ["--date", DAY, "--provider", "anthropic"], transport=httpx.MockTransport(empty)
    )

    assert code == 0
    assert "no usage recorded for this day" in capsys.readouterr().out
