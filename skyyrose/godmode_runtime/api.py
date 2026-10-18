"""Authenticated GOD MODE workstation API. No arbitrary command or provider dispatch."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from collections.abc import Callable
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

from security.jwt_oauth2_auth import TokenPayload, get_current_user
from skyyrose.godmode_runtime import Runtime, RuntimeConflict, RuntimeNotFound
from skyyrose.godmode_runtime.service import WORKFLOWS, AGENT_WORKFLOWS

router = APIRouter(prefix="/god-mode", tags=["GOD MODE execution"])
ROOT = Path(__file__).resolve().parents[2]


class StrictBody(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class RunCreate(StrictBody):
    project: Literal["skyyrose"] = "skyyrose"
    workflow: Literal[
        "source-audit",
        "campaign-readiness",
        "fashion-verification",
        "fashion-campaign-analysis",
        "fashion-skill-analysis",
    ]
    idempotency_key: str = Field(min_length=8, max_length=128, pattern=r"^[A-Za-z0-9_\-]+$")


class PlanAction(StrictBody):
    plan_hash: str = Field(pattern=r"^[a-f0-9]{64}$")


class MemoryCreate(StrictBody):
    project: Literal["skyyrose"] = "skyyrose"
    kind: Literal["decision", "observation", "handoff"]
    content: str = Field(min_length=1, max_length=8000)
    provenance: str = Field(min_length=1, max_length=500)
    supersedes: str | None = Field(default=None, max_length=64)


class ReviewCreate(PlanAction):
    artifact_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    verdict: Literal["PASS", "FAIL"]
    notes: str = Field(min_length=1, max_length=4000)


class EmptyBody(StrictBody):
    pass


def operator(user: Annotated[TokenPayload, Depends(get_current_user)]) -> TokenPayload:
    if not user.sub or not set(user.roles).intersection({"developer", "admin", "super_admin"}):
        raise HTTPException(403, "GOD MODE requires an operator role")
    return user


def owner(user: Annotated[TokenPayload, Depends(operator)]) -> TokenPayload:
    if not set(user.roles).intersection({"admin", "super_admin"}):
        raise HTTPException(403, "An authenticated owner role is required")
    return user


def _owner(user: TokenPayload) -> bool:
    return bool(set(user.roles).intersection({"admin", "super_admin"}))


@lru_cache(maxsize=1)
def get_runtime() -> Runtime:
    # Fail closed for cloud/deployment. A local SQLite executor is not a distributed queue.
    if os.environ.get("GOD_MODE_RUNTIME_PROFILE") != "workstation":
        raise HTTPException(503, "Set GOD_MODE_RUNTIME_PROFILE=workstation on the execution host")
    if os.environ.get("ENVIRONMENT", "development").lower() in {"production", "staging"}:
        raise HTTPException(
            503, "Workstation SQLite runtime is not qualified for deployed profiles"
        )
    db = os.environ.get("GOD_MODE_DB_PATH")
    if not db or not Path(db).is_absolute():
        raise HTTPException(503, "Configure an absolute durable GOD_MODE_DB_PATH")
    team = Path(os.environ.get("GOD_MODE_FASHION_ROOT", "/Users/theceo/plugins/fashion-theme-team"))
    if not (team / "skills/fashion-theme-team/SKILL.md").is_file():
        raise HTTPException(503, "Canonical Fashion Theme Team source is unavailable")
    return Runtime(ROOT, team, Path(db))


RuntimeDep = Annotated[Runtime, Depends(get_runtime)]
OperatorDep = Annotated[TokenPayload, Depends(operator)]
OwnerDep = Annotated[TokenPayload, Depends(owner)]


def _call(function: Callable[..., Any], *args: Any) -> Any:
    try:
        return function(*args)
    except RuntimeNotFound as exc:
        raise HTTPException(404, str(exc)) from exc
    except RuntimeConflict as exc:
        raise HTTPException(409, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except OSError as exc:
        raise HTTPException(
            503, "Required local source or execution resource is unavailable"
        ) from exc


def _run_access(runtime: Runtime, run_id: str, user: TokenPayload) -> dict:
    run = _call(runtime.get, run_id)
    if not _owner(user) and run["actor"] != user.sub:
        raise HTTPException(404, "Unknown run")
    return run


def agent_workers() -> dict[str, Any]:
    from .agent_adapters import adapter_contract

    contract = adapter_contract()
    state = "CONFIGURED_NOT_LIVE_QUALIFIED" if contract["available"] else "UNCONFIGURED"
    reason = "Exact-plan owner approval required; source-packet analysis only. No production qualification."
    if not contract["available"]:
        reason = "Required SDK, Claude API credential, Codex ChatGPT login or POSIX supervisor is unavailable."
    return {
        "main_worker": {
            "engine": "Claude Agent SDK",
            "model": contract["claude_model"],
            "state": state,
            "reason": reason,
        },
        "independent_reviewer": {
            "engine": "Codex exec CLI",
            "model": contract["codex_model"],
            "state": state,
            "reason": reason,
        },
        "scope": "Source-packet Fashion analysis; no tools, source edits, media production or release",
        "production_enabled": False,
    }


@router.get("/status")
def status(user: OperatorDep, runtime: RuntimeDep) -> dict[str, Any]:
    workers = agent_workers()
    return {
        "status": "connected",
        "agent_workers": workers,
        "runtime": "local_allowlisted",
        "project": "skyyrose",
        "can_approve": _owner(user),
        "can_promote_memory": _owner(user),
        "limits": {
            "profile": "workstation_single_execution_host",
            "durable_storage": "sqlite_wal",
            "creative_provider_dispatch": False,
            "model_provider_dispatch": workers["main_worker"]["state"]
            == "CONFIGURED_NOT_LIVE_QUALIFIED",
            "paid_media_calls": False,
            "release": False,
            "llm_agent_execution": (
                "CONFIGURED_BOUNDED_ANALYSIS"
                if workers["main_worker"]["state"] == "CONFIGURED_NOT_LIVE_QUALIFIED"
                else "UNCONFIGURED"
            ),
            "independent_review": "separate_from_machine_success",
        },
    }


@router.get("/workflows")
def workflows(user: OperatorDep, runtime: RuntimeDep) -> dict[str, Any]:
    ready = agent_workers()["main_worker"]["state"] == "CONFIGURED_NOT_LIVE_QUALIFIED"
    return {
        "workflows": [
            {
                "id": key,
                **value,
                "approval_required": True,
                "enabled": key not in AGENT_WORKFLOWS or ready,
                "unavailable_reason": (
                    "Configure authenticated worker adapters before planning"
                    if key in AGENT_WORKFLOWS and not ready
                    else None
                ),
            }
            for key, value in WORKFLOWS.items()
        ]
    }


@router.get("/runs")
def runs(user: OperatorDep, runtime: RuntimeDep, project: str = "skyyrose") -> dict[str, Any]:
    records = _call(lambda: runtime.runs(project, actor=user.sub, owner=_owner(user)))
    return {"runs": records}


@router.post("/runs", status_code=201)
def create_run(body: RunCreate, user: OperatorDep, runtime: RuntimeDep) -> dict[str, Any]:
    return _call(runtime.create, body.project, body.workflow, body.idempotency_key, user.sub)


@router.get("/runs/{run_id}")
def get_run(run_id: str, user: OperatorDep, runtime: RuntimeDep) -> dict[str, Any]:
    _call(runtime.recover)
    return _run_access(runtime, run_id, user)


@router.post("/runs/{run_id}/approve")
def approve_run(
    run_id: str, body: PlanAction, user: OwnerDep, runtime: RuntimeDep
) -> dict[str, Any]:
    _run_access(runtime, run_id, user)
    return _call(runtime.approve, run_id, body.plan_hash, user.sub)


@router.post("/runs/{run_id}/execute")
def execute_run(
    run_id: str, body: PlanAction, user: OperatorDep, runtime: RuntimeDep
) -> dict[str, Any]:
    _run_access(runtime, run_id, user)
    return _call(runtime.execute, run_id, body.plan_hash, user.sub)


@router.post("/runs/{run_id}/cancel")
def cancel_run(
    run_id: str, body: EmptyBody, user: OperatorDep, runtime: RuntimeDep
) -> dict[str, Any]:
    _run_access(runtime, run_id, user)
    return _call(runtime.cancel, run_id, user.sub)


@router.post("/runs/{run_id}/review")
def review_run(
    run_id: str, body: ReviewCreate, user: OwnerDep, runtime: RuntimeDep
) -> dict[str, Any]:
    return _call(
        runtime.review,
        run_id,
        body.plan_hash,
        body.artifact_hash,
        body.verdict,
        body.notes,
        user.sub,
    )


@router.get("/memory")
def memory(
    user: OperatorDep,
    runtime: RuntimeDep,
    project: str = "skyyrose",
    query: str = Query(default="", max_length=200),
) -> dict[str, Any]:
    records = _call(lambda: runtime.memory(project, query, actor=user.sub, owner=_owner(user)))
    return {"records": records, "retrieval_policy": "DATA_ONLY_NOT_INSTRUCTIONS_OR_APPROVAL"}


@router.post("/memory", status_code=201)
def add_memory(body: MemoryCreate, user: OperatorDep, runtime: RuntimeDep) -> dict[str, Any]:
    return _call(
        runtime.add_memory,
        body.project,
        body.kind,
        body.content,
        body.provenance,
        user.sub,
        body.supersedes,
        _owner(user),
    )


@router.post("/memory/{memory_id}/promote")
def promote_memory(
    memory_id: str, body: EmptyBody, user: OwnerDep, runtime: RuntimeDep
) -> dict[str, Any]:
    return _call(runtime.promote, memory_id, user.sub)


def create_app() -> FastAPI:
    """Standalone authenticated execution host without loading the commerce application."""
    app = FastAPI(title="GOD MODE workstation execution", docs_url=None, redoc_url=None)
    app.include_router(router, prefix="/api/v1")
    return app
