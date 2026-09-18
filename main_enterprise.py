"""
DevSkyy Enterprise Platform
============================

Run: uvicorn main_enterprise:app --host 0.0.0.0 --port 8000 --reload
"""

from __future__ import annotations

import logging
import os
import sys
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime

# bug-263: on darwin, subprocess forks SIGSEGV in nw_settings_child_has_forked()
# once Network.framework is armed (any httpx/requests/torch/onnxruntime import
# does this) and close_fds=True (the default) sends Popen through fork()+exec
# instead of posix_spawn. no_proxy="*" keeps _scproxy out of the picture. This
# is a long-running uvicorn server process (not a pytest run), so conftest.py's
# layer-1 guard never applies here — set it before fastapi/structlog pull in
# anything heavy, and before any route handler can reach agents/* subprocess calls.
if sys.platform == "darwin":
    os.environ.setdefault("no_proxy", "*")
    os.environ.setdefault("NO_PROXY", "*")

import structlog
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

load_dotenv()

logger = logging.getLogger(__name__)


def _parse_sentry_sample_rate(raw: str | None, default: float) -> float:
    """Parse a Sentry sample-rate env var into [0.0, 1.0]; falls back to
    ``default`` on missing, empty, non-numeric, or out-of-range input."""
    if raw is None or raw.strip() == "":
        return default
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return default
    if not 0.0 <= value <= 1.0:
        return default
    return value


def _resolve_cors_origin_regex(raw: str | None) -> str:
    """Resolve the CORS allow_origin_regex from CORS_ORIGIN_REGEX env var.

    The default is deliberately narrow because CORSMiddleware runs with
    allow_credentials=True: a bare ``[a-z0-9-]+\\.vercel\\.app`` matched ANY
    Vercel-hosted app (an attacker-registrable shared domain), letting a hostile
    site read credentialed cross-origin responses. Scope to this project's own
    surfaces only — devskyy.app + its subdomains, and this project's Vercel
    preview URLs (``devskyy-<hash>-skyyroseco.vercel.app``). Anchored with ``$``
    so no attacker suffix can extend a match. Override via CORS_ORIGIN_REGEX.
    """
    raw = (raw or "").strip()
    return raw or (
        r"^https://("
        r"([a-z0-9-]+\.)?devskyy\.app"  # devskyy.app + any subdomain
        r"|devskyy-[a-z0-9-]+-skyyroseco\.vercel\.app"  # this project's previews
        r")$"
    )


# =============================================================================
# Lifespan — startup / shutdown
# =============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database, logging, optional services."""
    from core.structured_logging import configure_logging

    log_level = os.getenv("LOG_LEVEL", "INFO")
    configure_logging(log_level=log_level, include_timestamp=True)
    log = structlog.get_logger(__name__)

    environment = os.getenv("ENVIRONMENT", "development")
    log.info("platform_starting", environment=environment)

    # Sentry (optional)
    sentry_dsn = os.getenv("SENTRY_DSN")
    if sentry_dsn:
        import sentry_sdk

        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=os.getenv("SENTRY_ENVIRONMENT", environment),
            traces_sample_rate=_parse_sentry_sample_rate(
                os.getenv("SENTRY_TRACES_SAMPLE_RATE"),
                default=0.1 if environment == "production" else 1.0,
            ),
            profiles_sample_rate=_parse_sentry_sample_rate(
                os.getenv("SENTRY_PROFILES_SAMPLE_RATE"), default=0.0
            ),
            send_default_pii=False,
        )
        log.info("sentry_initialized")

    # Database
    from database.db import db_manager

    await db_manager.initialize()
    app.state.db_manager = db_manager
    log.info("database_initialized")

    # OpenTelemetry (optional)
    try:
        from core.telemetry.tracer import init_telemetry

        init_telemetry(service_name="devskyy-api")
        log.info("opentelemetry_initialized")
    except Exception:
        pass

    # Langfuse LLM observability (optional — requires LANGFUSE_PUBLIC_KEY/SECRET_KEY/HOST)
    app.state.langfuse = None
    if os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"):
        try:
            from langfuse import get_client

            langfuse_client = get_client()
            if langfuse_client.auth_check():
                app.state.langfuse = langfuse_client
                log.info("langfuse_initialized", host=os.getenv("LANGFUSE_HOST", "default"))
            else:
                log.warning("langfuse_auth_check_failed")
        except Exception as exc:  # noqa: BLE001 — observability is non-critical
            log.warning("langfuse_init_failed", error=str(exc))

    # Run the MCP streamable-HTTP session manager for the app lifetime so the
    # mounted /mcp endpoint can serve sessions to the dashboard + WordPress.
    from mcp_tools.http_mount import mcp_session_manager

    async with mcp_session_manager().run():
        log.info("platform_ready", routes=len([r for r in app.routes if hasattr(r, "path")]))
        yield

    # Shutdown
    log.info("platform_shutting_down")
    await db_manager.close()
    try:
        from skyyrose.elite_studio.creative.checkpointer import close_checkpointer

        await close_checkpointer()
    except Exception as exc:  # noqa: BLE001 — non-critical cleanup
        log.warning("creative_checkpointer_close_failed", error=str(exc))
    # Flush any buffered Langfuse traces before exit
    if getattr(app.state, "langfuse", None) is not None:
        try:
            app.state.langfuse.flush()
        except Exception as exc:  # noqa: BLE001 — non-critical cleanup
            log.warning("langfuse_flush_failed", error=str(exc))
    log.info("platform_shutdown_complete")


# =============================================================================
# App
# =============================================================================


def _resolve_schema_url(environment: str, path: str) -> str | None:
    """Gate a docs/schema endpoint by environment.

    Returns None in production to DISABLE the endpoint, else ``path``. Disabling
    docs_url/redoc_url alone still leaves /openapi.json publicly readable —
    disclosing every route and parameter on the internet-facing backend — so the
    OpenAPI schema is gated the same way (None also disables the Swagger/ReDoc
    pages that depend on it).
    """
    return None if environment == "production" else path


_environment = os.getenv("ENVIRONMENT", "development")
_docs_url = _resolve_schema_url(_environment, "/docs")
_redoc_url = _resolve_schema_url(_environment, "/redoc")
_openapi_url = _resolve_schema_url(_environment, "/openapi.json")

app = FastAPI(
    title="DevSkyy Enterprise Platform",
    description="AI-Driven Multi-Agent Orchestration for SkyyRose",
    version="3.2.0",
    docs_url=_docs_url,
    redoc_url=_redoc_url,
    openapi_url=_openapi_url,
    lifespan=lifespan,
)

# Mount the DevSkyy MCP server (streamable HTTP, Bearer-auth) at /mcp so the
# Next.js dashboard and WordPress site can consume the same tools the stdio
# server exposes. build_mcp_app() also constructs mcp.session_manager, which the
# lifespan above runs. See mcp_tools/http_mount.py.
from mcp_tools.http_mount import MCP_MOUNT_PATH, build_mcp_app  # noqa: E402

app.mount(MCP_MOUNT_PATH, build_mcp_app())

# =============================================================================
# Middleware
# =============================================================================

# CORS
cors_origins = os.getenv("CORS_ORIGINS", "").split(",")
cors_origins = [o.strip() for o in cors_origins if o.strip()] or [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://skyyrose.co",
    "https://devskyy.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=_resolve_cors_origin_regex(os.getenv("CORS_ORIGIN_REGEX")),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID", "X-Correlation-ID"],
    expose_headers=["X-Response-Time", "X-Correlation-ID"],
)

# Host-header allowlist (opt-in). Now that the app is internet-facing at
# api.devskyy.app, a Host allowlist is standard hardening — but a wrong list
# fails Fly's /health check and kills the machine, so it is enabled ONLY when
# ALLOWED_HOSTS is explicitly set (comma-separated; e.g.
# "api.devskyy.app,*.devskyy.app,devskyy-backend.fly.dev"). Include the Fly
# health-check host and the .fly.dev domain when enabling. Unset = no change.
_allowed_hosts = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()]
if _allowed_hosts:
    from starlette.middleware.trustedhost import TrustedHostMiddleware

    app.add_middleware(TrustedHostMiddleware, allowed_hosts=_allowed_hosts)


# Correlation ID
@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    request.state.correlation_id = correlation_id
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response


# Response timing
@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    import time

    from api.v1.monitoring import track_request

    start = time.time()
    response = await call_next(request)
    ms = (time.time() - start) * 1000
    response.headers["X-Response-Time"] = f"{ms:.2f}ms"
    track_request(ms, response.status_code < 400)
    return response


# Security headers
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "connect-src 'self' https://*.devskyy.app https://*.vercel.app; "
        "frame-ancestors 'none'"
    )
    return response


# Rate limiting
from security.rate_limiting import rate_limiter  # noqa: E402


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    await rate_limiter.enforce_rate_limit(request)
    return await call_next(request)


# =============================================================================
# Routers
# =============================================================================

# Core dashboard & agent routers
from api.admin_dashboard import admin_dashboard_router
from api.agents import agents_router
from api.brand import brand_router
from api.dashboard import dashboard_router
from api.round_table import round_table_router
from api.tasks import tasks_router
from api.three_d import three_d_router
from api.tools import tools_router
from api.visual import visual_router

app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(round_table_router, prefix="/api/v1")
app.include_router(brand_router, prefix="/api/v1")
app.include_router(tools_router, prefix="/api/v1")
app.include_router(three_d_router, prefix="/api/v1")
app.include_router(visual_router, prefix="/api/v1")
app.include_router(agents_router)
app.include_router(admin_dashboard_router, prefix="/api/v1")

# WordPress & e-commerce
from api.ar_sessions import ar_sessions_router
from api.elementor_3d import elementor_3d_router
from api.gdpr import gdpr_router
from api.virtual_tryon import virtual_tryon_router
from api.webhooks import webhook_router
from api.websocket import ws_router

app.include_router(ar_sessions_router, prefix="/api/v1")
app.include_router(virtual_tryon_router, prefix="/api/v1")
app.include_router(elementor_3d_router, prefix="/api/v1")
app.include_router(gdpr_router)
app.include_router(webhook_router)
app.include_router(ws_router)

# API v1 MCP routers
from api.v1 import (
    autonomous_router,
    catalog_router,
    code_router,
    commerce_router,
    context_dev_router,
    hf_spaces_router,
    lora_router,
    marketing_router,
    media_router,
    ml_router,
    monitoring_router,
    orchestration_router,
    render_jobs_router,
    sync_router,
    training_router,
    wordpress_agent_router,
    wordpress_theme_router,
)

app.include_router(catalog_router, prefix="/api/v1")
app.include_router(code_router, prefix="/api/v1")
app.include_router(commerce_router, prefix="/api/v1")
app.include_router(context_dev_router, prefix="/api/v1")
app.include_router(hf_spaces_router, prefix="/api/v1")
app.include_router(marketing_router, prefix="/api/v1")
app.include_router(media_router, prefix="/api/v1")
app.include_router(ml_router, prefix="/api/v1")
app.include_router(autonomous_router, prefix="/api/v1")
app.include_router(monitoring_router, prefix="/api/v1")
app.include_router(orchestration_router, prefix="/api/v1")
# Blender render jobs (POST /api/v1/render-jobs → headless worker; see pipelines/blender_render).
app.include_router(render_jobs_router, prefix="/api/v1")
app.include_router(sync_router, prefix="/api/v1")
app.include_router(lora_router, prefix="/api/v1")
app.include_router(training_router, prefix="/api/v1")
app.include_router(wordpress_agent_router, prefix="/api/v1")
app.include_router(wordpress_theme_router, prefix="/api/v1")

# Claude Agent SDK
from api.v1.claude_sdk import router as claude_sdk_router

app.include_router(claude_sdk_router, prefix="/api/v1")

# Elite Studio — Layer 5 REST API
from api.v1.elite_studio import router as elite_studio_router

app.include_router(elite_studio_router, prefix="/api/v1")

# RAGAnything — Multimodal Knowledge Graph RAG
from api.v1.rag_anything import router as rag_anything_router  # noqa: E402

app.include_router(rag_anything_router, prefix="/api/v1")

# Enterprise API v2 — creative ops, characters, assets, webhooks, health
from api.v2 import assets_router as v2_assets_router
from api.v2 import characters_router as v2_characters_router
from api.v2 import creative_router as v2_creative_router
from api.v2 import health_router as v2_health_router
from api.v2 import webhooks_router as v2_webhooks_router

app.include_router(v2_creative_router, prefix="/api/v2")
app.include_router(v2_characters_router, prefix="/api/v2")
app.include_router(v2_assets_router, prefix="/api/v2")
app.include_router(v2_webhooks_router, prefix="/api/v2")
app.include_router(v2_health_router, prefix="/api/v2")

# WordPress integration
from api.v1.wordpress_integration import router as wordpress_router

app.include_router(wordpress_router, prefix="/api/v1")

# WooCommerce webhooks (order/product events)
from api.v1.woocommerce_webhooks import router as woocommerce_webhooks_router

app.include_router(woocommerce_webhooks_router, prefix="/api/v1")

# Feature flags
from api.v1.feature_flags import router as feature_flags_router

app.include_router(feature_flags_router)  # router already carries full /api/v1/flags prefix

# WordPress content (sync/status) — no path collision with wordpress_integration routes
from api.v1.wordpress import router as wordpress_content_router

app.include_router(wordpress_content_router, prefix="/api/v1")

# Analytics & pipeline
from api.v1 import (
    approval_router,
    assets_router,
    brand_assets_router,
    business_router,
    competitors_router,
    descriptions_router,
)

app.include_router(business_router, prefix="/api/v1")
app.include_router(assets_router, prefix="/api/v1")
app.include_router(approval_router, prefix="/api/v1")
app.include_router(brand_assets_router, prefix="/api/v1")
app.include_router(competitors_router, prefix="/api/v1")
app.include_router(descriptions_router, prefix="/api/v1")

from api.v1.analytics.dashboard import router as analytics_dashboard_router

app.include_router(analytics_dashboard_router, prefix="/api/v1")

from api.v1.pipeline import router as pipeline_router

app.include_router(pipeline_router, prefix="/api/v1")

# Authentication
from security.jwt_oauth2_auth import auth_router

app.include_router(auth_router)

from billing.middleware import billing_middleware  # noqa: E402

# SaaS Infrastructure — tenant resolution + billing entitlements.
# FastAPI runs http middlewares in LIFO order: the LAST-registered runs FIRST.
# We want tenant → billing → handler, so billing is registered first and
# tenant is registered second so it wraps billing.
from core.middleware.tenant import tenant_middleware  # noqa: E402

app.middleware("http")(billing_middleware)
app.middleware("http")(tenant_middleware)

# Customer Portal
from api.v1.portal import portal_router  # noqa: E402

app.include_router(portal_router, prefix="/api/v1")

# GraphQL
from api.graphql_server import graphql_router

app.include_router(graphql_router, prefix="/graphql", tags=["GraphQL"])


# =============================================================================
# Health & Status
# =============================================================================


@app.get("/", tags=["Root"])
async def root():
    return {
        "platform": "DevSkyy Enterprise",
        "version": "3.2.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/health",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/health", tags=["Health"])
async def health_check():
    db_status = "unknown"
    try:
        db = app.state.db_manager
        health = await db.health_check()
        db_status = health.get("status", "unknown")
    except Exception:
        db_status = "unavailable"

    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "3.2.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "services": {
            "api": "operational",
            "database": db_status,
        },
    }


@app.get("/ready", tags=["Health"])
async def readiness_check():
    return {"ready": True}


@app.get("/live", tags=["Health"])
async def liveness_check():
    return {"alive": True}


# =============================================================================
# Error Handlers
# =============================================================================


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail,
            "path": str(request.url.path),
            "timestamp": datetime.now(UTC).isoformat(),
            "correlation_id": getattr(request.state, "correlation_id", None),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    log = structlog.get_logger(__name__)
    log.error(
        "unhandled_exception",
        exception_type=type(exc).__name__,
        path=str(request.url.path),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "status_code": 500,
            "message": "Internal server error",
            "path": str(request.url.path),
            "timestamp": datetime.now(UTC).isoformat(),
            "correlation_id": getattr(request.state, "correlation_id", None),
        },
    )


# =============================================================================
# Dev Server
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main_enterprise:app",
        host="0.0.0.0",  # nosec B104 — 0.0.0.0 required in containerized/cloud deployment; network isolation at infra layer
        port=8000,
        reload=True,
        log_level="info",
    )
