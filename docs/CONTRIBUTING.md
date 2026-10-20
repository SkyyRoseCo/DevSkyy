# DevSkyy Contributor Guide

**Last Updated**: 2026-08-01
**Source of Truth**: `Makefile`, `pyproject.toml`, `package.json`, `wordpress-theme/package.json`, `frontend/package.json`, `.env.example`, `scripts/remediation/env.example`

Renamed from `CONTRIB.md` to the standard GitHub filename; content otherwise carried forward.

---

## Quick Start

```bash
# 1. Clone & install (root Python API)
git clone https://github.com/The-Skyy-Rose-Collection-LLC/DevSkyy.git
cd DevSkyy
make install                  # Python production deps (pip install -e .)
npm install                   # Root Node deps (use npm, NOT pnpm)

# 2. Environment
cp .env.example .env                      # Fill in API keys
cp .env.wordpress.example .env.wordpress   # WordPress.com / WooCommerce credentials

# 3. Verify
python -c "import fastapi; print('Python OK')"
npm run type-check            # Root TypeScript OK

# 4. Run the API locally (non-Docker)
.venv/bin/python -m uvicorn main_enterprise:app --host 0.0.0.0 --port 8000
```

**Do not run `python main_enterprise.py` directly, and do not add `--reload`.** Its
`if __name__ == "__main__"` block calls `uvicorn.run(..., reload=True)`, and on
macOS the reload watcher's subprocess spawn crashes with `SIGSEGV` /
`nw_settings_child_has_forked` before the app finishes booting (bug-263 — see
`.wolf/buglog.json`). `make dev` only installs dependencies, it does not start
a server. The plain `uvicorn` invocation above (no `--reload`) is the verified
working local command; `docs/RUNBOOK.md` documents the same entry point for
Docker.

This repo has **three independent workspaces** — don't cross-install dependencies between them:

| Workspace | Runtime | Root | Install |
|-----------|---------|------|---------|
| Python API | Python 3.12+ (`requires-python` in `pyproject.toml`: `>=3.12,<3.15`) | `/` | `make install` / `make dev` |
| Dashboard | Node.js 22 | `frontend/` | `cd frontend && npm install` |
| WordPress theme | PHP 8.2, Node 18+ | `wordpress-theme/` | `cd wordpress-theme && npm install` |

## Virtual Environments

| Venv | Purpose | Setup |
|------|---------|-------|
| `.venv` | Main (FastAPI, diffusers, torch) | `python -m venv .venv && pip install -e ".[all]"` |
| `.venv-imagery` | Image processing (rembg, BRIA, genai) | `python -m venv .venv-imagery && pip install -r requirements-imagery.txt` |
| `.venv-lora` | LoRA training | `python -m venv .venv-lora` |
| `.venv-agents` | Google ADK render pipeline (conflicts with numpy in `.venv`) | `python -m venv .venv-agents && .venv-agents/bin/python -m pip install 'google-adk[extensions]' scipy pytest pytest-asyncio pytest-mock` |

<!-- AUTO-GENERATED:command-tables:start -->
## Available Scripts

### Python (via Makefile)

Run `make help` for the short version. Full target list, grouped by area:

| Command | Description |
|---------|-------------|
| `make install` | Install production Python dependencies (`pip install -e .`) |
| `make dev` | Install Python dev deps (`.[dev]`) + `npm install` |
| `make lint` | `ruff check .` + `mypy` (mypy warnings non-blocking) |
| `make lint-strict` | Same, but mypy failures block |
| `make format` | `isort . && ruff check . --fix && black .` |
| `make test` | `pytest tests/ -v --tb=short` |
| `make test-fast` | `pytest tests/ -x -q` (stop on first failure) |
| `make test-cov` | pytest with terminal + HTML coverage report |
| `make fresh` | Check derived files are in sync (SOT, theme `.min`, version, retired refs) — `scripts/freshness-guard.sh --all` |
| `make fresh-fix` | Regenerate SOT + rebuild theme `.min`, re-stage for commit |
| `make ts-build` / `ts-lint` / `ts-lint-fix` / `ts-test` / `ts-test-strict` / `ts-test-collections` / `ts-type-check` / `ts-format` | Root TypeScript equivalents of the npm scripts below, invoked via Make |
| `make test-all` / `lint-all` / `format-all` | Python + TypeScript combined |
| `make ci` | Full local CI (`lint-all` + `test-all`) |
| `make sot-manifest` | Regenerate `data/sot-images.json` (`python3 -m skyyrose.core.sot_images`) — run after any catalog image change |
| `make validate-catalog` | Read-only catalog consistency checks (jersey SKUs, similarities, logo registry); exits 1 on failure |
| `make sync-catalog-dry` / `sync-catalog` | Preview / apply catalog auto-fixes (backs up changed files first) |
| `make catalog-help` | Full catalog-tooling help text |
| `make render-dry SKUS=... [STYLE=...] [ALL=1]` | Cost manifest for OAI `gpt-image-2` renders — **no API call** |
| `make render SKUS=... [STYLE=...] [ALL=1]` | **PAID** — generates renders (gated by manifest + cost cap); STOP-AND-SHOW applies |
| `make adk-test` / `adk-test-fast` / `adk-lint` / `adk-check` | ADK render-pipeline unit tests + lint, run against `.venv-agents/` (override with `ADK_PYTHON=`) |
| `make adk-eval` | ADK AgentEvaluator harness, **skips the paid call** by default (~$0) |
| `make adk-eval-live` | Same harness with `EVAL_LIVE=1` — **paid**, ~$0.20/run, requires STOP-AND-SHOW |
| `make adk-learning-report` | Generate learning-loop proposals markdown from `data/agent-learning/` JSONL records |
| `make demo-black-rose` / `demo-signature` / `demo-love-hurts` / `demo-showroom` / `demo-runway` | Launch a 3D collection demo (wraps the npm `demo:*` scripts) |
| `make security` | `bandit -r . -x ./tests -ll` + `npm audit` |
| `make clean` | Remove build/test/cache artifacts (`build/`, `dist/`, `__pycache__`, etc.) |
| `make build` | `clean` + `ts-build` + `python -m build` |
| `make docker-secrets` | Generate `.env.docker` with strong random secrets (won't clobber existing) |
| `make docker-config` | Validate + render the merged compose config (requires `.env.docker`) |
| `make docker-build` | Build the `devskyy:local` image |
| `make docker-up` | Build + start the core stack (postgres/redis/app/worker/elite-worker), detached |
| `make docker-up-monitoring` | Core stack + prometheus + grafana (`--profile monitoring`) |
| `make docker-down` | Stop the stack (keeps volumes) |
| `make docker-clean` | Stop the stack **and delete volumes** — destroys data |
| `make docker-logs` / `docker-ps` | Tail logs / show container status |
| `make docker-run` | Start just the `app` service (postgres/redis deps still honored) |

See `docs/DOCKER.md` for the full Docker workflow and `make catalog-help` for catalog-tooling details.

### Node.js — root (via npm)

| Command | Description |
|---------|-------------|
| `npm run build` | TypeScript compilation (`tsc --project config/typescript/tsconfig.json`) |
| `npm run build:watch` | TypeScript compilation (watch mode) |
| `npm run dev` | Dev server with nodemon |
| `npm run start` | Production server (`node dist/index.js`) |
| `npm run test` | Vitest unit-test suite |
| `npm run test:watch` | Vitest in watch mode |
| `npm run test:coverage` | Vitest with coverage |
| `npm run test:ci` | Vitest CI run with coverage |
| `npm run lint` / `lint:fix` | ESLint on `src/**/*.{ts,tsx,js,jsx}` |
| `npm run format` / `format:check` | Prettier on `src/` + root `.json`/`.md` |
| `npm run type-check` | TypeScript type checking (no emit) |
| `npm run clean` | Remove `dist/` and `coverage/` |
| `npm run prepare` | Husky setup + build (runs on `npm install`) |
| `npm run precommit` | lint + type-check + test:ci |
| `npm run security:audit` / `security:audit:production` | Full dependency audit / production-only high-severity gate |
| `npm run deps:check` / `deps:update` | `npm outdated` / `npm update` |
| `npm run demo:collections` | List all available 3D demos |
| `npm run demo:black-rose` / `demo:signature` / `demo:love-hurts` / `demo:showroom` / `demo:runway` | Launch a specific 3D collection demo (Vite) |
| `npm run test:collections` | Vitest collection-focused unit tests |

### WordPress theme (`cd wordpress-theme/`)

| Command | Description |
|---------|-------------|
| `npm run build` | `build:css` + `build:js` — rebuilds `.min.css`/`.min.js` (theme serves `.min` in production; **required after any CSS/JS edit**) |
| `npm run rebuild` | `clean` (delete existing `.min.*`) + `build` |
| `npm run lint` | `lint:php` + `lint:css` |
| `npm run lint:php` | `php -l` syntax check on every theme `.php` file |
| `npm run lint:php:strict` | PHPCS against `.phpcs.xml` (needs `composer install` in `skyyrose-flagship/` first) |
| `npm run lint:css` | stylelint |
| `npm run format` / `format:check` | Prettier on theme CSS/JS/JSON |
| `npm run verify` | Quick PHP-lint summary |
| `npm run verify:full` | `lint` + `build`, full pre-deploy pipeline |
| `npm run deploy` | `bash ../scripts/deploy-theme.sh` — **live deploy to skyyrose.co** |
| `npm run deploy:dry` | Same script with `--dry-run` — preview only, no server contact |
| `npm run deploy:full` | Same script with `--with-maintenance` (legacy maintenance-mode path; default deploy is hot-swap) |
| `npm run deploy:verify` | Cache-busted `curl -sIL` against the live site |
| `npm run backfill:nextgen[:dry\|:loop]` | AVIF/WebP backfill via `wp-cli-nextgen-backfill.sh` |
| `npm run designqc[:local]` | Playwright desktop/mobile visual-QA screenshots (live site / local) |
| `npm run audit:deps` / `audit:fix` | `npm audit --omit=dev` / `npm audit fix` |
| `npm run size` | Print `.min.css`/`.min.js` bundle sizes |

### Dashboard (`cd frontend/`)

| Command | Description |
|---------|-------------|
| `npm run dev` | Next.js dev server |
| `npm run build` | Production build |
| `npm run start` | Serve production build |
| `npm run lint` | ESLint |
| `npm run type-check` | `tsc --noEmit` |
| `npm run test:e2e` / `test:e2e:ui` | Playwright E2E tests (headless / UI mode) — spec dir is `tests/e2e/`, **not** `frontend/e2e/` |
| `npm run deploy` / `deploy:prod` | `vercel` / `vercel --prod` |
| `npm run deploy:auto[:prod]` | `tsx scripts/deploy.ts` (scripted deploy) |
| `npm run vercel:link[:auto]` | Link the Vercel project |
| `npm run vercel:env:pull` / `env:push` | Sync `.env.local` with Vercel project env |
| `npm run vercel:logs` / `vercel:inspect` / `vercel:project` | Vercel CLI passthroughs |

No root-level unit-test runner is wired for the dashboard (`npm test` has no script) despite `@testing-library/react` being installed — Playwright E2E is the only automated test path today.
<!-- AUTO-GENERATED:command-tables:end -->

<!-- AUTO-GENERATED:api-surface:start -->
## API Surface (v1)

FastAPI mounts every `api/v1/*.py` router under `/api/v1` (each router declares its own sub-prefix; see `api/CLAUDE.md` for the two-layer routing contract with the non-versioned `api/*.py` routers). Router-level summary — full per-route detail lives in the source files themselves (`grep '@router\.' api/v1/<file>.py`):

| Router module | Mount | Purpose |
|---|---|---|
| `analytics/business.py`, `analytics/dashboard.py` | `/api/v1` | Business metrics (revenue, orders, AOV, funnel) + analytics dashboard |
| `approval.py` | `/api/v1/queue`, `/revisions`, `/stats` | Human-in-the-loop approval queue for AI-generated content |
| `assets.py` | `/api/v1` | Asset ingestion, job status, versioning, retention, datasets |
| `autonomous.py` | `/api/v1` | Autonomous agent run status |
| `brand_assets.py` | `/api/v1/assets`, `/ingest`, `/training-readiness` | Brand asset ingestion + LoRA training-readiness checks |
| `catalog.py` | `/api/v1` (`/search`, `/products/{sku}`, `/answer`) | Product catalog search, similar-products, RAG Q&A over the catalog — `/answer` is **cost-bearing and currently ungated** (see `api/v1/catalog.py:12-15`) |
| `claude_sdk.py` | `/api/v1` | Claude Agent SDK bridges (research, email, excel, dashboard session) |
| `code.py` | `/api/v1` (`/scan`, `/fix`) | Code scanning/fixing agent endpoints |
| `commerce.py` | `/api/v1` | Bulk products + dynamic pricing |
| `competitors.py` | `/api/v1` | Competitor asset tracking + style-distribution analytics |
| `descriptions.py` | `/api/v1/generate` | AI product-description generation (single/quick/batch) |
| `hf_spaces.py` | `/api/v1` | HuggingFace Spaces integration |
| `marketing.py` | `/api/v1` | Marketing campaign endpoints |
| `media.py` | `/api/v1` | 3D generation + media processing |
| `ml.py` | `/api/v1/predict` | ML model predictions |
| `monitoring.py` | `/api/v1/monitoring` | System metrics (`/monitoring/metrics`, JSON) + agent directory (`/agents`) |
| `orchestration.py` | `/api/v1` | Multi-agent workflow orchestration |
| `social_media.py` | `/api/v1` | Social content generation, scheduling, analytics |
| `sync.py` | `/api/v1` | Asset sync pipeline (HF ↔ DevSkyy ↔ WordPress) |
| `training_status.py` | `/api/v1/training` | LoRA training-run progress (reads the same `RUNS_DIR` as `scripts/flux_lora`) |
| `woocommerce_webhooks.py` | `/api/v1/woocommerce/webhooks` (`/order`, `/product`) | Inbound WooCommerce webhook receivers |
| `wordpress.py`, `wordpress_agent.py`, `wordpress_integration.py`, `wordpress_theme.py` | `/api/v1` | WordPress/WooCommerce sync, agent execution, product↔collection sync, theme deploy trigger |

**Auth posture is opt-in, not default** — public catalog reads vs. `Depends(get_current_user)` vs. rate-limited are each router's explicit choice. Any caller-provided URL must validate through `security.ssrf_protection.ssrf_protection.validate_url()` before use (mandatory per `api/CLAUDE.md`; was a P1 finding in PR #649).
<!-- AUTO-GENERATED:api-surface:end -->

<!-- AUTO-GENERATED:env-vars:start -->
## Environment Variables

Copy `.env.example` to `.env` and fill in values (root/API). Copy `.env.wordpress.example` to `.env.wordpress` for WordPress.com/WooCommerce credentials. There is no `.env.hf.example` — HuggingFace-related variable **names** below were derived from `os.getenv`/`os.environ` call sites, not from a template file.

| Variable | Required | Description |
|----------|----------|--------------|
| `JWT_SECRET_KEY` | **Production** | 64+ char secret for JWT signing |
| `ENCRYPTION_MASTER_KEY` | **Production** | Base64-encoded AES-256 key |
| `DATABASE_URL` | Yes | SQLite (dev default: `sqlite+aiosqlite:///./devskyy.db`) or PostgreSQL (prod) |
| `DB_POOL_SIZE` / `DB_MAX_OVERFLOW` / `DB_POOL_TIMEOUT` | Optional | Connection pool tuning (defaults 10/20/30) |
| `CORS_ORIGINS` | Yes | Comma-separated allowed origins |
| `FRONTEND_URL` / `API_URL` | Optional | Canonical URLs for cross-service links |
| `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GOOGLE_AI_API_KEY` | Optional | LLM providers |
| `STRIPE_API_KEY` / `STRIPE_PUBLISHABLE_KEY` / `STRIPE_WEBHOOK_SECRET` | Optional | Stripe payments |
| `HF_TOKEN` | Optional | HuggingFace inference/dataset access — **primary** 3D-asset path |
| `HF_HOME` | Optional | HuggingFace cache dir (default `./cache/huggingface`) |
| `HF_3D_MODEL_PRIMARY` / `HF_3D_MODEL_FALLBACK` | Optional | 3D model selection (Hunyuan3D-2 / TripoSR by default) |
| `TRIPO_API_KEY` / `TRIPO_API_BASE_URL` / `TRIPO_OUTPUT_DIR` | Optional | Tripo3D — fallback 3D generation |
| `FASHN_API_KEY` / `FASHN_API_BASE_URL` / `FASHN_OUTPUT_DIR` | Optional | FASHN virtual try-on |
| `WORDPRESS_URL` / `WORDPRESS_USERNAME` / `WORDPRESS_APP_PASSWORD` | Optional | WordPress REST auth (root `.env`) |
| `WOOCOMMERCE_KEY` / `WOOCOMMERCE_SECRET` | Optional | WooCommerce REST API keys |
| `REDIS_URL` | Optional | Redis caching (default `redis://localhost:6379/0`) |
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_USER` / `SMTP_PASSWORD` | Optional | Outbound email |
| `KLAVIYO_PRIVATE_KEY` / `KLAVIYO_PUBLIC_KEY` / `KLAVIYO_LIST_ID` | Optional | Klaviyo email marketing |
| `PROMETHEUS_ENABLED` | Optional | Toggles the Prometheus scrape target in `prometheus.yml` — note `main_enterprise.py` does not currently expose a `/metrics` route (see `docs/RUNBOOK.md` Health Endpoints) |
| `SENTRY_DSN` | Optional | Error monitoring |
| `RATE_LIMIT_{IP,USER,API_KEY}_{PER_MINUTE,PER_HOUR,BURST}` | Optional | Default API rate limits (`security/rate_limiting.py`; per-IP default 100/min). A set but invalid value fails startup |
| `EMBEDDING_CACHE_SIZE` / `RESPONSE_CACHE_TTL` / `VECTOR_SEARCH_CACHE_TTL` / `RERANKING_CACHE_TTL` / `MAX_PARALLEL_INGESTION` | Optional | Performance/cache tuning |
| `GEMINI_API_KEY` | Optional | Antigravity SDK |

**`.env.wordpress`** (WordPress.com integration — separate from the root WooCommerce keys above):

| Variable | Required | Description |
|----------|----------|--------------|
| `WORDPRESS_SITE_URL` | Yes | e.g. `https://skyyrose.co` |
| `WORDPRESS_API_TOKEN` | Yes | WordPress.com OAuth2 token |
| `WOOCOMMERCE_KEY` / `WOOCOMMERCE_SECRET` | Yes | REST API consumer key/secret |
| `WC_WEBHOOK_SECRET` | Optional | Webhook signature verification |

**Frontend** (`frontend/.env.local`, copy from `frontend/.env.example` if present):

| Variable | Required | Description |
|----------|----------|--------------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend API URL — defaults to `http://localhost:8000` if unset (`lib/api/config.ts`); the Hub/Agents admin screens silently render empty ("No agents reporting") with no error if nothing is listening there |
| `NEXT_PUBLIC_WS_URL` | Yes | WebSocket URL |
| `NEXTAUTH_SECRET` | Yes | NextAuth session secret |
| `NEXT_PUBLIC_WORDPRESS_URL` | Optional | WordPress for WooCommerce integration |

**Admin dashboard ↔ WordPress/WooCommerce** (`frontend/.env.local` — contract defined in `scripts/remediation/env.example`, populated via `python3 scripts/remediation/setup_credentials.py`). Next.js only loads `frontend/.env*`; it does **not** read a repo-root `.env`, so these must be set in `frontend/.env.local` specifically even though the setup script's default `--env-file` is root `.env`:

| Variable | Required | Description |
|----------|----------|--------------|
| `WP_BASE_URL` | Yes | e.g. `https://skyyrose.co` — used by `lib/wp/client.ts`, distinct from `WORDPRESS_URL` (legacy proxy stack) |
| `WP_APP_USER` / `WP_APP_PASSWORD` | Yes | WordPress Application Password (service user) — read by `app/admin/settings/page.tsx` for the live "Connected" status card |
| `WC_CONSUMER_KEY` / `WC_CONSUMER_SECRET` | Yes | WooCommerce REST API keys (Read/Write) — distinct from `WOOCOMMERCE_KEY`/`WOOCOMMERCE_SECRET` (legacy proxy stack) |
| `WP_WEBHOOK_SECRET` | Yes | HMAC secret for inbound WooCommerce webhooks — auto-generated by the setup script |
| `REVALIDATE_SECRET` | Yes | Next.js on-demand revalidation secret — auto-generated by the setup script |

Verify live connectivity (read-only, never prints secret values): `python3 scripts/remediation/wiring_audit.py`.

Generate secrets:
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"         # JWT key
python -c "import secrets,base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"  # AES key
```
<!-- AUTO-GENERATED:env-vars:end -->

## Testing

```bash
# Python
make test                              # Full suite
make test-fast                         # Stop on first failure
pytest tests/unit/test_foo.py -v       # Single file
pytest tests/ -k "test_name" -v        # Single test by name
pytest tests/ -m integration           # By marker
rtk proxy pytest tests/ -v             # Use for the TRUE exit code — bare pytest can
                                        # misreport "no tests collected" as a pass

# TypeScript (root)
npm run test                           # Vitest
npm run test:coverage                  # With coverage

# Both
make test-all                          # Python + TypeScript
```

Target: **85%+ coverage**. Run `make test-cov` to check. No mocks in integration/E2E tests (project-wide rule, see `.claude/rules/testing.md`).

## Code Style

| Tool | Language | Config |
|------|----------|--------|
| Black | Python | Line length: 100, target py313 (`pyproject.toml`) |
| Ruff | Python | Linting + import sorting (isort handled separately, see below) |
| isort | Python | Import organization, `profile = "black"` |
| mypy | Python | Type checking — canonical config is `mypy.ini`, not `pyproject.toml` |
| ESLint | TypeScript | `src/**/*.{ts,tsx,js,jsx}` (root) |
| Prettier | TypeScript | `src/**/*.{ts,tsx,js,jsx}` (root) |
| PHPCS | PHP (theme) | `wordpress-theme/skyyrose-flagship/.phpcs.xml`, WordPress standard, `skyyrose` prefix |

Run before committing: `make format && make lint` (root); `cd wordpress-theme && npm run lint:php:strict` for theme PHP.

## Git Conventions

**Branch naming**: `<type>/<description>` (e.g., `feat/immersive-worlds`, `fix/wp-csp-headers`)

**Commit messages**: `<type>: <description>`

| Type | Use for |
|------|---------|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code restructuring |
| `docs` | Documentation |
| `test` | Tests |
| `chore` | Maintenance |
| `perf` | Performance |
| `style` | Formatting |

## Pull Request Checklist

- [ ] `make ci` passes locally (or `make test-all` + `make lint-all` if `ci` is unavailable)
- [ ] `rtk proxy pytest tests/ -v` shows the true pass/fail (don't trust a bare `pytest` "no tests collected" line)
- [ ] New/changed endpoints in `api/v1/` have an explicit auth posture and, if they take a caller URL, an SSRF guard (`api/CLAUDE.md`)
- [ ] Theme CSS/JS changes: `cd wordpress-theme && npm run build` and re-verify the `.min` output, not just source
- [ ] No hardcoded secrets; new env vars added to `.env.example` (or `.env.wordpress.example`) with a comment
- [ ] `docs/` updated in the same PR if the change touches commands, endpoints, env vars, or deploy steps
- [ ] Commit messages follow `<type>: <description>`

## Project Structure

```
DevSkyy/
├── main_enterprise.py          # FastAPI app (REST + GraphQL + webhooks)
├── devskyy_mcp.py               # MCP server
├── frontend/                    # Next.js 16 + React 19 dashboard
├── wordpress-theme/             # SkyyRose Flagship theme
│   └── skyyrose-flagship/
├── agents/                      # Specialized agents (218+ files)
├── api/v1/                      # Versioned REST routers (35+ modules, see API Surface above)
├── core/                        # Foundation (zero external deps)
├── orchestration/                # RAG, LangGraph workflows
├── services/                    # ML, 3D, Analytics
├── security/                    # JWT, OAuth2, AES-256-GCM
├── data/
│   └── product-catalog.csv      # Legacy path; canonical catalog is
│                                 # wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv
├── scripts/                     # Deploy, sync, generation, verification scripts
├── tests/                       # pytest + jest
└── docs/                        # Documentation
    └── archive/                 # Historical docs
```

## Critical Rules

- Files < 800 lines, functions < 50 lines
- No hardcoded secrets — use env vars
- Validate inputs: Zod (frontend), Pydantic (backend)
- Python line length: 100
- Use `npm` not `pnpm` (Vercel compat on Node 22+)
- WordPress: extend via hooks, never modify core
- Product catalog is single-source: `wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv` — never invent or reference retired SKUs
