"""Route-level authentication coverage for the production backend (main_enterprise).

Three guarantees:

1. Coverage gate: every mounted HTTP route has an authentication dependency,
   except an explicit allowlist of intentionally public routes. A new route that
   ships without auth fails this test instead of shipping open (121 routes were
   open until 2026-10-10, including paid generation and webhook administration).
2. Behaviour: routes that were open now reject anonymous callers with 401/403.
   POSTs send ``{}`` so, on a tree without the gate, they stop at body validation
   (422) and never reach a paid handler.
3. ``security.require_roles`` is a decorator. Wrapping it in ``Depends()`` made
   FastAPI read its ``func`` parameter as a query param, so ``?func=x`` skipped
   authentication. The analytics routers must use a real dependency.
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

_UNAUTH = (401, 403)

# Intentionally public: liveness/readiness probes, login bootstrap, and a static
# policy document. /auth/register can only create api_user accounts.
PUBLIC_ROUTES = {
    ("GET", "/"),
    ("GET", "/health"),
    ("GET", "/live"),
    ("GET", "/ready"),
    ("GET", "/api/v2/health"),
    ("GET", "/api/v1/sync/health"),
    ("GET", "/api/v1/wordpress/health"),
    ("GET", "/api/v1/gdpr/retention-policy"),
    ("POST", "/api/v1/auth/refresh"),
    ("POST", "/api/v1/auth/register"),
}

_AUTH_MARKERS = (
    "current_user",
    "rolechecker",
    "service_or_user",
    "require",
    "auth",
    "token",
    "verify",
    "api_key",
    "admin",
    "signature",
    "permission",
)


def _flatten(routes):
    for route in routes:
        if hasattr(route, "effective_candidates"):
            yield from _flatten(list(route.effective_candidates()))
        else:
            yield route


def _dependency_names(dependant, acc: set[str]) -> set[str]:
    for dep in dependant.dependencies:
        acc.add(getattr(dep.call, "__name__", type(dep.call).__name__).lower())
        _dependency_names(dep, acc)
    return acc


def _http_routes(app: FastAPI):
    for route in _flatten(app.routes):
        is_route = isinstance(route, APIRoute) or type(route).__name__ == "_EffectiveRouteContext"
        if not is_route or getattr(route, "dependant", None) is None:
            continue
        for method in sorted((route.methods or set()) - {"HEAD", "OPTIONS"}):
            yield method, route.path, _dependency_names(route.dependant, set())


@pytest.fixture(scope="module")
def app() -> FastAPI:
    from main_enterprise import app as production_app

    return production_app


@pytest.fixture(scope="module")
def client(app) -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


class TestEveryRouteRequiresAuth:
    def test_route_inventory_is_not_empty(self, app):
        # Guards the gate itself: if route discovery breaks, coverage must not
        # pass vacuously.
        assert len(list(_http_routes(app))) > 200

    def test_no_unauthenticated_route_outside_allowlist(self, app):
        open_routes = sorted(
            (method, path)
            for method, path, names in _http_routes(app)
            if (method, path) not in PUBLIC_ROUTES
            and not any(marker in name for name in names for marker in _AUTH_MARKERS)
        )
        assert open_routes == [], f"routes without an auth dependency: {open_routes}"


class TestFormerlyOpenRoutesRejectAnonymous:
    @pytest.mark.parametrize(
        "path",
        [
            "/api/v1/agents",
            "/api/v1/3d/jobs",
            "/api/v1/virtual-tryon/jobs",
            "/api/v1/visual/jobs",
            "/api/v1/webhooks/endpoints",
            "/api/v1/round-table",
            "/api/v1/brand",
            "/api/v1/ar/capabilities",
            "/api/v1/tools",
            "/graphql",
        ],
    )
    def test_get_requires_auth(self, client, path):
        assert client.get(path).status_code in _UNAUTH

    @pytest.mark.parametrize(
        "path",
        [
            "/api/v1/agents/commerce/execute",
            "/api/v1/virtual-tryon/generate",
            "/api/v1/visual/enhance",
            "/api/v1/3d/generate/text",
            "/api/v1/round-table/compete",
            "/api/v1/webhooks/endpoints",
        ],
    )
    def test_paid_or_mutating_post_requires_auth(self, client, path):
        assert client.post(path, json={}).status_code in _UNAUTH

    def test_wordpress_status_requires_auth(self, client):
        assert client.get("/api/v1/wordpress/status").status_code in _UNAUTH


class TestAnalyticsRolesNotBypassable:
    @pytest.mark.parametrize(
        ("module", "path"),
        [
            ("api.v1.analytics.alerts", "/analytics/alerts/history"),
            ("api.v1.analytics.alert_configs", "/analytics/alert-configs"),
            ("api.v1.analytics.ml_pipelines", "/analytics/ml/overview"),
        ],
    )
    def test_func_query_param_does_not_skip_auth(self, module, path):
        import importlib

        router = importlib.import_module(module).router
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app, raise_server_exceptions=False)
        assert client.get(path, params={"func": "x"}).status_code in _UNAUTH
