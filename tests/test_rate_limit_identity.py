"""Per-user and per-API-key limits, and DDoS blacklisting (security/rate_limiting.py).

Requests go through a real FastAPI app over a TestClient. The per-IP rule always
applies; a verified user or an X-API-Key header adds that identity's own window on
top, so one identity is capped across IPs and rotating headers cannot escape the
per-IP limit.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterator

import jwt
import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from starlette.exceptions import HTTPException

from security import rate_limiting
from security.jwt_oauth2_auth import jwt_manager
from security.rate_limiting import (
    DEFAULT_RULE_LIMITS,
    AdvancedRateLimiter,
    SlidingWindowCounter,
)

_ENV_NAMES = [
    f"RATE_LIMIT_{prefix}_{suffix}"
    for prefix, _ in DEFAULT_RULE_LIMITS.values()
    for suffix in ("PER_MINUTE", "PER_HOUR", "BURST")
]


@pytest.fixture(autouse=True)
def _clean_rate_limit_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in _ENV_NAMES:
        monkeypatch.delenv(name, raising=False)


def _app_with(limiter: AdvancedRateLimiter, state_user_id: str | None = None) -> FastAPI:
    app = FastAPI()

    @app.middleware("http")
    async def rate_limit(request: Request, call_next):
        try:
            await limiter.enforce_rate_limit(request)
        except HTTPException as exc:
            return JSONResponse(
                {"detail": exc.detail}, status_code=exc.status_code, headers=exc.headers
            )
        return await call_next(request)

    if state_user_id is not None:
        # Registered last, so it runs first: an upstream auth layer setting user_id.
        @app.middleware("http")
        async def set_user(request: Request, call_next):
            request.state.user_id = state_user_id
            return await call_next(request)

    @app.get("/ping")
    async def ping() -> dict[str, str]:
        return {"ok": "yes"}

    return app


def _clients(app: FastAPI, *ips: str) -> list[TestClient]:
    return [TestClient(app, client=(ip, 50000)) for ip in ips]


def _bearer(user_id: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {jwt_manager.create_access_token(user_id, ['api_user'])}"}


@pytest.fixture
def frozen_clock(monkeypatch: pytest.MonkeyPatch) -> Iterator[list[float]]:
    now = [1_000_000.0]
    monkeypatch.setattr(rate_limiting.time, "time", lambda: now[0])
    yield now


# --- API key ---------------------------------------------------------------


def test_api_key_limit_caps_one_key_across_ips(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RATE_LIMIT_API_KEY_PER_MINUTE", "3")
    first, second = _clients(_app_with(AdvancedRateLimiter()), "10.0.0.1", "10.0.0.2")
    headers = {"X-API-Key": "sk_live_shared"}

    statuses = [first.get("/ping", headers=headers).status_code for _ in range(2)]
    statuses += [second.get("/ping", headers=headers).status_code for _ in range(2)]

    assert statuses == [200, 200, 200, 429]
    blocked = second.get("/ping", headers=headers)
    assert blocked.json() == {"detail": "Rate limit exceeded for API key"}
    assert blocked.headers["X-RateLimit-Limit"] == "3"


def test_rotating_api_keys_cannot_escape_ip_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RATE_LIMIT_IP_PER_MINUTE", "3")
    (client,) = _clients(_app_with(AdvancedRateLimiter()), "10.0.0.1")

    statuses = [
        client.get("/ping", headers={"X-API-Key": f"key-{n}"}).status_code for n in range(4)
    ]

    assert statuses == [200, 200, 200, 429]


def test_distinct_api_keys_have_separate_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RATE_LIMIT_API_KEY_PER_MINUTE", "2")
    (client,) = _clients(_app_with(AdvancedRateLimiter()), "10.0.0.1")

    key_a = [client.get("/ping", headers={"X-API-Key": "a"}).status_code for _ in range(3)]
    key_b = client.get("/ping", headers={"X-API-Key": "b"}).status_code

    assert key_a == [200, 200, 429]
    assert key_b == 200


def test_raw_api_key_is_not_held_in_memory() -> None:
    limiter = AdvancedRateLimiter()
    (client,) = _clients(_app_with(limiter), "10.0.0.1")
    raw_key = "sk_live_do_not_retain"

    assert client.get("/ping", headers={"X-API-Key": raw_key}).status_code == 200

    window_keys = list(limiter.sliding_windows)
    assert not any(raw_key in key for key in window_keys)
    digest = hashlib.sha256(raw_key.encode()).hexdigest()
    assert f"api_key:{digest}:default_api_key" in window_keys


# --- user --------------------------------------------------------------------


def test_verified_user_limit_caps_one_user_across_ips(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RATE_LIMIT_USER_PER_MINUTE", "2")
    first, second = _clients(_app_with(AdvancedRateLimiter()), "10.0.0.1", "10.0.0.2")
    headers = _bearer("user-42")

    statuses = [
        first.get("/ping", headers=headers).status_code,
        second.get("/ping", headers=headers).status_code,
        second.get("/ping", headers=headers).status_code,
    ]

    assert statuses == [200, 200, 429]
    assert second.get("/ping", headers=headers).json() == {"detail": "Rate limit exceeded for user"}
    other_user = first.get("/ping", headers=_bearer("user-43"))
    assert other_user.status_code == 200


def test_forged_token_cannot_spend_a_users_quota(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RATE_LIMIT_USER_PER_MINUTE", "2")
    attacker, victim = _clients(_app_with(AdvancedRateLimiter()), "10.0.0.66", "10.0.0.1")
    # Valid in every respect except the signing key.
    config = jwt_manager.config
    real = jwt.decode(
        jwt_manager.create_access_token("victim", ["api_user"]),
        config.secret_key,
        algorithms=[config.algorithm],
        audience=config.audience,
    )
    forged = jwt.encode(real, "k" * 64, algorithm=config.algorithm)

    attacker_statuses = [
        attacker.get("/ping", headers={"Authorization": f"Bearer {forged}"}).status_code
        for _ in range(5)
    ]
    statuses = [victim.get("/ping", headers=_bearer("victim")).status_code for _ in range(2)]

    assert attacker_statuses == [200] * 5
    assert statuses == [200, 200]


def test_upstream_state_user_id_is_honoured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RATE_LIMIT_USER_PER_MINUTE", "1")
    (client,) = _clients(_app_with(AdvancedRateLimiter(), state_user_id="state-user"), "10.0.0.1")

    statuses = [client.get("/ping").status_code for _ in range(2)]

    assert statuses == [200, 429]


def test_anonymous_request_adds_no_identity_windows() -> None:
    limiter = AdvancedRateLimiter()
    (client,) = _clients(_app_with(limiter), "10.0.0.1")

    assert client.get("/ping").status_code == 200

    assert list(limiter.sliding_windows) == ["ip:10.0.0.1:default_ip"]


# --- DDoS blacklist ----------------------------------------------------------


def test_sustained_flood_gets_ip_blacklisted(monkeypatch: pytest.MonkeyPatch) -> None:
    # 2/min with burst 2: the blacklist fires once attempts in the window exceed 4.
    monkeypatch.setenv("RATE_LIMIT_IP_PER_MINUTE", "2")
    monkeypatch.setenv("RATE_LIMIT_IP_BURST", "2")
    limiter = AdvancedRateLimiter()
    flooder, bystander = _clients(_app_with(limiter), "10.0.0.66", "10.0.0.1")

    statuses = [flooder.get("/ping").status_code for _ in range(6)]

    assert statuses == [200, 200, 429, 429, 403, 403]
    assert limiter.is_ip_blacklisted("10.0.0.66")
    assert bystander.get("/ping").status_code == 200


def test_rejections_stay_below_threshold_without_blacklist(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("RATE_LIMIT_IP_PER_MINUTE", "2")
    monkeypatch.setenv("RATE_LIMIT_IP_BURST", "2")
    limiter = AdvancedRateLimiter()
    (client,) = _clients(_app_with(limiter), "10.0.0.1")

    statuses = [client.get("/ping").status_code for _ in range(4)]

    assert statuses == [200, 200, 429, 429]
    assert not limiter.is_ip_blacklisted("10.0.0.1")


def test_rejected_attempts_are_capped() -> None:
    window = SlidingWindowCounter(window_size=60, max_requests=2, rejection_cap=5)

    results = [window.is_allowed() for _ in range(100)]

    assert results.count(True) == 2
    assert len(window.rejected) == 5
    assert window.attempts() == 7


def test_rejected_attempts_expire_with_the_window(frozen_clock: list[float]) -> None:
    window = SlidingWindowCounter(window_size=60, max_requests=1, rejection_cap=10)

    assert window.is_allowed() is True
    frozen_clock[0] += 1
    assert window.is_allowed() is False
    assert window.attempts() == 2

    frozen_clock[0] += 60.5
    assert window.is_allowed() is True
    assert window.attempts() == 1


# --- production app (main_enterprise) ----------------------------------------


def test_main_app_serves_429_and_403_not_500(monkeypatch: pytest.MonkeyPatch) -> None:
    from main_enterprise import app
    from security.rate_limiting import RateLimitType, default_rule, rate_limiter

    monkeypatch.setenv("RATE_LIMIT_IP_PER_MINUTE", "2")
    monkeypatch.setenv("RATE_LIMIT_IP_BURST", "2")
    monkeypatch.setitem(
        rate_limiter.default_rules, RateLimitType.IP_BASED, default_rule(RateLimitType.IP_BASED)
    )
    client = TestClient(app, client=("10.0.0.77", 50000), raise_server_exceptions=False)

    responses = [client.get("/health") for _ in range(6)]

    assert [r.status_code for r in responses] == [200, 200, 429, 429, 403, 403]
    limited = responses[2]
    assert limited.json()["message"] == "Rate limit exceeded"
    assert limited.headers["X-RateLimit-Limit"] == "2"
    assert int(limited.headers["Retry-After"]) >= 0
