# DevSkyy API v1 Endpoints Structure

## Overview

All API endpoints are located under `/api/v1/` and use **validated Pydantic models** for request/response structuring.

## Endpoint Routers

| Router | File | Prefix | Purpose |
|--------|------|--------|---------|
| `dashboard_router` | `api/dashboard.py` | `/api/v1` | Agent management (list, start, stop, execute) |
| `tasks_router` | `api/tasks.py` | `/api/v1` | Task submission and tracking |
| `round_table_router` | `api/round_table.py` | `/api/v1` | LLM Round Table competitions |
| `brand_router` | `api/brand.py` | `/api/v1` | SkyyRose brand configuration |
| `tools_router` | `api/tools.py` | `/api/v1` | Tool listing and testing |

## Validated Request/Response Models

### All tool calls MUST use validated structuring:

```python
from pydantic import BaseModel, Field

class ToolRequest(BaseModel):
    tool_name: str = Field(..., min_length=1)
    parameters: dict[str, Any] = Field(default_factory=dict)

class ToolResponse(BaseModel):
    result: Any = None
    error: str | None = None
    duration_ms: float = 0.0
```

### Agent Execution Pattern:

```python
class ExecuteRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=10000)
    max_tokens: int = Field(default=4096, ge=1, le=128000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)

class ExecuteResponse(BaseModel):
    task_id: str
    status: Literal["queued", "running", "completed", "failed"]
    result: str | None = None
```

## AgentRegistry Pattern

All agents are managed via `AgentRegistry` in `api/dashboard.py`:

```python
from api.dashboard import agent_registry

# Get or create agent instance (lazy loading)
agent = agent_registry.get_agent("commerce")

# Execute via agent
result = await agent.execute(prompt)
```

## Frontend API Client

Frontend uses `frontend/lib/api.ts` which calls `/api/v1/*` endpoints:

- `api.agents.list()` → `GET /api/v1/agents`
- `api.tasks.submit(req)` → `POST /api/v1/tasks`
- `api.roundTable.runCompetition(prompt)` → `POST /api/v1/round-table/compete`
- `api.brand.get()` → `GET /api/v1/brand`
- `api.tools.list()` → `GET /api/v1/tools`

## Key Principles

1. **No mock data** - All endpoints use real agent instances
2. **Validated I/O** - Pydantic models for all requests and responses
3. **Consistent prefixes** - All versioned endpoints use `/api/v1/`
4. **Type safety** - Full typing in both Python and TypeScript
5. **Error handling** - HTTPException with proper status codes

## Files Modified

- `main_enterprise.py` - Mounts all routers
- `api/index.py` - Vercel serverless deployment
- `api/dashboard.py` - AgentRegistry + agent endpoints
- `api/tasks.py` - Task management
- `api/round_table.py` - LLM competition
- `api/brand.py` - Brand configuration
- `api/tools.py` - Tool aggregation
- `frontend/lib/api.ts` - Frontend API client
