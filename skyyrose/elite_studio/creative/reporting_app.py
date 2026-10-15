"""Isolated, protected read-only Governor report application.

Construct explicitly with server-side configuration. Importing this application
does not load the enterprise API, instantiate a ledger, or acquire a transport.
"""

from __future__ import annotations

import hashlib
import hmac
import sqlite3
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request

from .governor_reporting import ReadOnlyLedger, identifier
from .spend_ledger import LedgerError


@dataclass(frozen=True)
class ReportConfig:
    database: Path
    authority_public_key: bytes = field(repr=False)
    integrity_key: bytes = field(repr=False)
    minimum_checkpoint: dict
    authentication_key: bytes = field(repr=False)
    site_id: str
    allowed_scopes: frozenset[tuple[str, str]]
    max_age_seconds: int = 60

    def __post_init__(self) -> None:
        identifier(self.site_id)
        if len(self.authentication_key) < 32 or len(self.integrity_key) < 32:
            raise ValueError("Strong reporting credentials required")
        if not self.allowed_scopes or not 1 <= self.max_age_seconds <= 300:
            raise ValueError("Bounded read-only job/grant scopes required")
        for job_id, grant_id in self.allowed_scopes:
            identifier(job_id)
            identifier(grant_id)


def report_signature(key: bytes, *, timestamp: str, path: str, site_id: str) -> str:
    """Client signature binds read-only method, exact route, site and timestamp."""
    payload = "\n".join(("GET", path, site_id, timestamp)).encode()
    return hmac.new(key, payload, hashlib.sha256).hexdigest()


def create_reporting_app(
    config: ReportConfig | None = None,
    *,
    clock: Callable[[], float] = time.time,
) -> FastAPI:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    @app.middleware("http")
    async def private_response(request: Request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        return response

    @app.get("/v1/governor/report/{job_id}/{grant_id}")
    def governor_report(request: Request, job_id: str, grant_id: str) -> dict:
        if config is None:
            raise HTTPException(503, "Reporting configuration unavailable")
        if request.query_params:
            raise HTTPException(400, "Report query controls are unsupported")
        timestamp = request.headers.get("X-Report-Timestamp", "")
        signature = request.headers.get("X-Report-Signature", "")
        site = request.headers.get("X-Report-Site", "")
        if (
            not timestamp.isascii()
            or not timestamp.isdigit()
            or len(timestamp) > 12
            or abs(clock() - int(timestamp)) > config.max_age_seconds
            or site != config.site_id
            or not signature.isascii()
            or len(signature) != 64
            or not hmac.compare_digest(
                signature,
                report_signature(
                    config.authentication_key,
                    timestamp=timestamp,
                    path=request.url.path,
                    site_id=config.site_id,
                ),
            )
        ):
            raise HTTPException(401, "Read-only report authentication required")
        try:
            identifier(job_id)
            identifier(grant_id)
        except LedgerError:
            raise HTTPException(404, "Report scope unavailable") from None
        if (job_id, grant_id) not in config.allowed_scopes:
            raise HTTPException(403, "Report scope denied")
        try:
            reader = ReadOnlyLedger(
                config.database,
                config.authority_public_key,
                config.integrity_key,
                minimum_checkpoint=config.minimum_checkpoint,
            )
            return reader.report(job_id=job_id, grant_id=grant_id)
        except (OSError, ValueError, KeyError, TypeError, sqlite3.Error) as exc:
            raise HTTPException(503, "Verified report evidence unavailable") from exc

    return app
