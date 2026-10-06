# DevSkyy

**AI-driven luxury fashion e-commerce platform for the SkyyRose brand.**

[![CI](https://github.com/SkyyRoseCo/DevSkyy/actions/workflows/ci.yml/badge.svg)](https://github.com/SkyyRoseCo/DevSkyy/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![TypeScript 5.0+](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> [skyyrose.co](https://skyyrose.co)

---

## Production

| Surface             | URL                                                  | Stack                                             |
| ------------------- | ---------------------------------------------------- | ------------------------------------------------- |
| **Customer site**   | [skyyrose.co](https://skyyrose.co)                   | WordPress · WooCommerce · SkyyRose Flagship theme |
| **Agent dashboard** | [devskyy.app](https://devskyy.app)                   | Next.js 16 · React 19 · Vercel                    |
| **API**             | [api.devskyy.app](https://api.devskyy.app)           | FastAPI · Python 3.11+ · Docker                   |
| **API Docs**        | [api.devskyy.app/docs](https://api.devskyy.app/docs) | OpenAPI                                           |

---

## Quick Start

```bash
# Install
make install                         # Python API + dev tooling
cd frontend && npm install           # Next.js dashboard

# Run locally (pick one approach)
# A) Native (two terminals):
uvicorn main_enterprise:app --reload --port 8000    # API
cd frontend && npm run dev                          # Dashboard

# B) Full stack via Docker (API + deps in containers):
docker-compose up -d


# Test
make test-fast                       # Unit tests
make ci                              # Full CI (lint + type + test)
```

See [docs/RUNBOOK.md](docs/RUNBOOK.md) for deployment and
[docs/AGENTS.md](docs/AGENTS.md) for agent orchestration.

---

## Architecture

8-layer platform with one-way dependency flow:

```
api/ · frontend/           ← Presentation (FastAPI + Next.js)
    ↑
agents/ · agent_sdk/       ← AI agents (Claude Agent SDK + 6 SuperAgents)
    ↑
orchestration/ · services/ ← Business logic (RAG, LangGraph, 3D pipelines)
    ↑
llm/ · integrations/       ← LLM providers (6) + third-party APIs
    ↑
database/ · security/      ← Persistence (Postgres + Alembic) + AES-256-GCM
    ↑
core/                      ← Foundation (auth, cache, events, errors, runtime)
```

**Dependency rule:**
`core → security → database/llm → orchestration/services → agents → api`

### Key Capabilities

- **Multi-agent orchestration** — 6 Super Agents (Commerce, Creative, Marketing,
  Support, Operations, Analytics)
- **6 LLM providers** — OpenAI, Anthropic, Google, Mistral, Cohere, Groq with
  tournament routing
- **Three.js 3D experiences** — per-collection immersive scenes (Black Rose,
  Love Hurts, Signature)
- **WordPress/WooCommerce** — REST API sync, Elementor templates, 30+ products
  across 4 collections
- **Enterprise security** — JWT/OAuth2, AES-256-GCM, Argon2id, rate limiting,
  circuit breakers
- **Production observability** — Prometheus, Sentry, correlation IDs, structured
  logging

---

## Repository Structure

| Group           | Directories                                                   | Purpose                                   |
| --------------- | ------------------------------------------------------------- | ----------------------------------------- |
| **API**         | `api/` `core/` `security/` `database/` `alembic/`             | FastAPI app, auth, migrations, foundation |
| **Agents**      | `agents/` `agent_sdk/` `adk/` `prompts/` `llm/`               | AI agents, prompts, LLM routing           |
| **Services**    | `services/` `orchestration/` `pipelines/` `imagery/` `ai_3d/` | Business logic, RAG, 3D generation        |
| **Integration** | `mcp_servers/` `mcp_tools/` `integrations/` `sync/`           | MCP, third-party APIs, WordPress sync     |
| **Frontend**    | `frontend/` `src/` `public/` `__mocks__/`                     | Next.js dashboard, 3D collections         |
| **WordPress**   | `wordpress-theme/skyyrose-flagship/` `wordpress-theme/skyyrose-flagship-2/` `wordpress/` | Production WP themes (V1 + V2) + tools |
| **Content**     | `assets/` `data/` `datasets/` `models/` `hf-spaces/` `renders/` `imagery/`               | Imagery, catalogs, ML models, renders   |
| **Design**      | `design-system/` `ds-bundle/` `eval/` `editorial-staging/`                               | Design tokens, brand eval, staging      |
| **Media**       | `Comfy/` `skyyrose/elite_studio/` `pipelines/`                                            | ComfyUI workflows, elite studio, media  |
| **Platform**    | `aos/` `billing/` `grpc_server/` `sdk/` `devskyy_workflows/` `skyyrose/`                 | AOS runtime, billing, gRPC, SDK         |
| **DevOps**      | `monitoring/` `scripts/` `tests/` `cli/` `tools/` `config/`                              | Observability, tests, CLI tools         |
| **Docs**        | `docs/` `archive/` `examples/` `tasks/` `knowledge-base/`                                | Documentation, lessons, examples        |

Entry points at root: `main_enterprise.py` (API), `devskyy_mcp.py` (MCP server),
`conftest.py` (pytest), `SOT.md` (source of truth registry).

---

## Workspaces

Each workspace is isolated with its own dependencies:

| Workspace        | Runtime           | Install                                      | Dev                                          |
| ---------------- | ----------------- | -------------------------------------------- | -------------------------------------------- |
| **Python API**   | Python 3.11+      | `make install`                               | `make dev`                                   |
| **Dashboard**    | Node.js 22, npm   | `cd frontend && npm install`                 | `npm run dev`                                |
| **WordPress V1** | PHP 8.2, SFTP     | See `.env.wordpress`                         | `bash scripts/deploy-theme.sh`               |
| **WordPress V2** | Node.js 22        | `cd wordpress-theme/skyyrose-flagship-2 && npm install` | `npm run build`                   |
| **Imagery**      | Python (isolated) | `pip install -r requirements-imagery.txt`    | `scripts/oai_render/`                        |
| **ADK Agents**   | Python (isolated) | `.venv-agents/` (`pip install google-adk`)   | Numpy conflicts — use separate venv          |
| **ComfyUI**      | Python (isolated) | See `Comfy/README.md`                        | `comfy` CLI                                  |

---

## Development

```bash
# Format & lint (Python)
make format                          # isort + ruff --fix + black
make lint                            # ruff check + black --check
make ci                              # Full pipeline

# Type check
mypy .                               # 904 files, 0 issues target

# Coverage target: 85%+
pytest tests/ --cov --cov-report=html
```

**Conventions:** files <800 lines · functions <50 lines · immutability ·
Zod/Pydantic validation at boundaries · conventional commits (`feat:` `fix:`
`refactor:` `docs:` `test:` `chore:`).

See [CLAUDE.md](CLAUDE.md) for the full engineering protocol and [docs/](docs/)
for detailed guides.

---

## Deployment

```bash
# WordPress theme V1 (skyyrose.co)
bash scripts/deploy-theme.sh

# WordPress theme V2 (build + deploy)
cd wordpress-theme/skyyrose-flagship-2 && npm run build

# Frontend (Vercel — devskyy.app)
cd frontend && git push origin main  # auto-deploys

# API (Fly.io)
fly deploy --config fly.toml

# API (Docker local)
docker-compose up -d
```

Full procedures in [docs/RUNBOOK.md](docs/RUNBOOK.md).

---

## License

MIT © SkyyRose LLC
