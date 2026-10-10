"""
Tasks API Endpoints
===================

Backend API for task management and execution.
Provides endpoints for submitting, tracking, and retrieving agent tasks.

Endpoints:
- GET /tasks - List tasks with optional filtering
- GET /tasks/{task_id} - Get specific task
- POST /tasks - Submit a new task
- POST /tasks/{task_id}/cancel - Cancel a running task
"""

import asyncio
import logging
import time
import uuid
from collections import deque
from datetime import UTC, datetime
from typing import Any, Literal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from security.jwt_oauth2_auth import TokenPayload, UserRole, get_current_user, require_roles

from .dashboard import agent_registry
from .websocket_integration import WebSocketIntegration

logger = logging.getLogger(__name__)

# =============================================================================
# Models
# =============================================================================

SuperAgentTypeLiteral = Literal[
    "commerce", "creative", "marketing", "support", "operations", "analytics"
]


class TaskMetrics(BaseModel):
    startTime: str | None = None
    endTime: str | None = None
    durationMs: float | None = None
    tokensUsed: int | None = None
    costUsd: float | None = None
    provider: str | None = None
    promptTechnique: str | None = None


class TaskRequest(BaseModel):
    agent_type: SuperAgentTypeLiteral = Field(..., alias="agentType")
    prompt: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    use_round_table: bool = Field(default=False, alias="useRoundTable")

    class Config:
        populate_by_name = True


class TaskResponse(BaseModel):
    taskId: str
    agentType: SuperAgentTypeLiteral
    prompt: str
    status: Literal["pending", "running", "completed", "failed"]
    result: Any = None
    error: str | None = None
    createdAt: str
    metrics: TaskMetrics = Field(default_factory=TaskMetrics)


# =============================================================================
# Task Store (In-Memory)
# =============================================================================


class TaskStore:
    """
    In-memory task store with history.
    For production, replace with Redis or database.
    """

    def __init__(self, max_history: int = 1000):
        self._tasks: dict[str, TaskResponse] = {}
        self._history: deque[str] = deque(maxlen=max_history)
        self._lock = asyncio.Lock()

    async def create(self, agent_type: SuperAgentTypeLiteral, prompt: str) -> TaskResponse:
        """Create a new task."""
        task_id = f"task-{uuid.uuid4().hex[:12]}"
        now = datetime.now(UTC).isoformat()

        task = TaskResponse(
            taskId=task_id,
            agentType=agent_type,
            prompt=prompt,
            status="pending",
            createdAt=now,
            metrics=TaskMetrics(startTime=now),
        )

        async with self._lock:
            self._tasks[task_id] = task
            self._history.append(task_id)

        return task

    async def get(self, task_id: str) -> TaskResponse | None:
        """Get a task by ID."""
        return self._tasks.get(task_id)

    async def update(self, task_id: str, **updates) -> TaskResponse | None:
        """Update a task."""
        async with self._lock:
            if task_id not in self._tasks:
                return None
            task = self._tasks[task_id]
            for key, value in updates.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            return task

    async def list_tasks(
        self,
        agent_type: str | None = None,
        status: str | None = None,
        limit: int = 20,
    ) -> list[TaskResponse]:
        """List tasks with optional filtering."""
        tasks = list(self._tasks.values())

        if agent_type:
            tasks = [t for t in tasks if t.agentType == agent_type]
        if status:
            tasks = [t for t in tasks if t.status == status]

        # Sort by creation time (newest first)
        tasks.sort(key=lambda t: t.createdAt, reverse=True)

        return tasks[:limit]


# Global task store
task_store = TaskStore()


# =============================================================================
# Background Task Execution
# =============================================================================


async def execute_task_background(
    task_id: str, agent_type: str, prompt: str, use_round_table: bool = False
):
    """Execute a task in the background."""
    start_time = time.time()

    # Generate agent ID
    agent_id = f"{agent_type}-001"

    try:
        # Update status to running
        await task_store.update(task_id, status="running")

        # Broadcast agent execution start
        await WebSocketIntegration.broadcast_agent_execution_start(
            agent_id=agent_id,
            agent_type=agent_type,
            task_id=task_id,
            prompt=prompt,
        )

        # Initialize agent if needed
        if not agent_registry._initialized.get(agent_type):
            await agent_registry.initialize_agent(agent_type)

        agent = agent_registry.get_agent(agent_type)
        agent_registry.set_status(agent_type, "running")

        # Execute the task
        if use_round_table and hasattr(agent, "execute_with_round_table"):
            result = await agent.execute_with_round_table(prompt)
        elif hasattr(agent, "execute_smart"):
            result = await agent.execute_smart(prompt)
        elif hasattr(agent, "execute"):
            result = await agent.execute(prompt)
        else:
            result = {"response": "Agent executed successfully", "prompt": prompt}

        duration_ms = (time.time() - start_time) * 1000

        # Extract metrics from result if available
        technique = None
        provider = None
        tokens = None

        if isinstance(result, dict):
            technique = result.get("technique_used") or result.get("technique")
            provider = result.get("provider")
            tokens = result.get("tokens_used")

        # Update task with result
        metrics = TaskMetrics(
            startTime=datetime.now(UTC).isoformat(),
            endTime=datetime.now(UTC).isoformat(),
            durationMs=duration_ms,
            tokensUsed=tokens or int(len(prompt.split()) * 1.5),  # Estimate if not provided
            costUsd=duration_ms / 1000 * 0.001,  # Rough estimate
            provider=provider or "anthropic",
            promptTechnique=technique,
        )

        await task_store.update(
            task_id,
            status="completed",
            result=result,
            metrics=metrics,
        )

        # Broadcast agent execution complete
        await WebSocketIntegration.broadcast_agent_execution_complete(
            agent_id=agent_id,
            agent_type=agent_type,
            task_id=task_id,
            result=result,
            duration_ms=duration_ms,
            technique_used=technique,
        )

        # Update agent stats
        agent_registry.update_stats(agent_type, success=True, latency_ms=duration_ms)
        agent_registry.set_status(agent_type, "idle")

        logger.info(f"Task {task_id} completed in {duration_ms:.2f}ms")

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000

        await task_store.update(
            task_id,
            status="failed",
            error=str(e),
            metrics=TaskMetrics(
                startTime=datetime.now(UTC).isoformat(),
                endTime=datetime.now(UTC).isoformat(),
                durationMs=duration_ms,
            ),
        )

        # Broadcast agent execution error
        await WebSocketIntegration.broadcast_agent_execution_error(
            agent_id=agent_id,
            agent_type=agent_type,
            task_id=task_id,
            error=str(e),
        )

        agent_registry.update_stats(agent_type, success=False, latency_ms=duration_ms)
        agent_registry.set_status(agent_type, "error")

        logger.error(f"Task {task_id} failed: {e}")


# =============================================================================
# Router
# =============================================================================

tasks_router = APIRouter(tags=["Tasks"])


@tasks_router.get("/tasks", response_model=list[TaskResponse])
async def list_tasks(
    agent_type: str | None = Query(None, alias="agent_type"),
    status: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    user: TokenPayload = Depends(get_current_user),
):
    """List tasks with optional filtering."""
    return await task_store.list_tasks(agent_type=agent_type, status=status, limit=limit)


@tasks_router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, user: TokenPayload = Depends(get_current_user)):
    """Get a specific task by ID."""
    task = await task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")
    return task


@tasks_router.post("/tasks", response_model=TaskResponse)
@require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)
async def submit_task(
    request: TaskRequest,
    background_tasks: BackgroundTasks,
    user: TokenPayload = Depends(get_current_user),
):
    """Submit a new task for execution (admin-only: runs paid agent/LLM work)."""
    # Create the task
    task = await task_store.create(request.agent_type, request.prompt)

    # Schedule background execution
    background_tasks.add_task(
        execute_task_background,
        task.taskId,
        request.agent_type,
        request.prompt,
        request.use_round_table,
    )

    return task


@tasks_router.post("/tasks/{task_id}/cancel")
@require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)
async def cancel_task(task_id: str, user: TokenPayload = Depends(get_current_user)):
    """Cancel a running task."""
    task = await task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")

    if task.status not in ("pending", "running"):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel task in status: {task.status}",
        )

    await task_store.update(task_id, status="failed", error="Cancelled by user")

    return {"success": True, "message": f"Task {task_id} cancelled"}


# =============================================================================
# Export
# =============================================================================

__all__ = ["tasks_router", "task_store", "TaskRequest", "TaskResponse"]
