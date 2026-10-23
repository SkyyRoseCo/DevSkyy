"""Authenticated God Mode execution on the dashboard's provider runtime."""

import asyncio
import os
import socket

from fastapi import APIRouter, Depends, Header, HTTPException

from orchestration.provider_execution import (
    RegistryTools,
    RouterAdapter,
    RunError,
    RunStore,
    execute_run,
    validate_request,
)
from security.jwt_oauth2_auth import TokenPayload, get_current_user

router = APIRouter(prefix="/god-mode", tags=["God Mode"])
_tasks: set[asyncio.Task] = set()


def owner(user: TokenPayload = Depends(get_current_user)) -> str:
    if "admin" not in user.roles:
        raise HTTPException(403, "Administrator role required for provider execution")
    return user.sub


def execution_instance() -> None:
    designated = os.getenv("GODMODE_EXECUTION_INSTANCE")
    current = os.getenv("FLY_MACHINE_ID") or socket.gethostname()
    if not designated or designated != current:
        raise HTTPException(
            503, "Route execution requests to the designated persistent instance"
        )


def store() -> RunStore:
    execution_instance()
    path = os.getenv("GODMODE_RUN_DB")
    if not path:
        raise HTTPException(503, "Configure GODMODE_RUN_DB on a persistent volume")
    return RunStore(path)


@router.get("/providers")
async def providers(user_id: str = Depends(owner)):
    adapter = RouterAdapter()
    try:
        toolset = RegistryTools(user_id)
        tool_names = []
        for name in sorted(toolset.allowed):
            try:
                toolset.specs([name])
                tool_names.append(name)
            except RunError:
                continue
        return {
            "providers": adapter.providers(),
            "tools": tool_names,
            "paid_execution_enabled": os.getenv("GODMODE_EXECUTION_ENABLED") == "1",
        }
    finally:
        await adapter.close()


@router.post("/runs", status_code=202)
async def submit(
    request: dict, idempotency_key: str = Header(...), user_id: str = Depends(owner)
):
    execution_instance()
    adapter = None
    transferred = False
    try:
        validate_request(request)
        runs = store()
        previous = runs.lookup(user_id, idempotency_key, request)
        if previous is not None:
            return previous
        if os.getenv("GODMODE_EXECUTION_ENABLED") != "1":
            raise HTTPException(503, "Provider execution is disabled on this server")
        adapter = RouterAdapter()
        available = {
            p["id"]: p for p in adapter.providers() if p["enabled"] and p["configured"]
        }
        selected = available.get(request["provider"])
        if not selected:
            raise RunError("Provider is not configured and enabled")
        models = set(selected["models"])
        if request["provider"] == "litellm":
            models &= set(
                filter(None, os.getenv("GODMODE_LITELLM_MODELS", "").split(","))
            )
        if request["model"] not in models:
            raise RunError("Model is not enabled in this provider configuration")
        toolset = RegistryTools(user_id)
        toolset.specs(request["tools"])
        record, created = runs.reserve(user_id, idempotency_key, request)
        if created:
            task = asyncio.create_task(
                execute_run(runs, user_id, record["id"], request, adapter, toolset)
            )
            _tasks.add(task)
            task.add_done_callback(_tasks.discard)
            transferred = True
        return record
    except RunError as exc:
        raise HTTPException(409, str(exc)) from None
    finally:
        if adapter is not None and not transferred:
            await adapter.close()


@router.get("/runs/{run_id}")
async def status(run_id: str, user_id: str = Depends(owner)):
    try:
        return store().get(user_id, run_id)
    except KeyError:
        raise HTTPException(404, "Run not found") from None


@router.post("/runs/{run_id}/cancel")
async def cancel(run_id: str, user_id: str = Depends(owner)):
    try:
        return store().update(user_id, run_id, state="cancel_requested")
    except KeyError:
        raise HTTPException(404, "Run not found") from None
