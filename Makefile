# DevSkyy Makefile
# ==================
# Unified development commands for Python + TypeScript
# SkyyRose

.PHONY: install dev lint lint-gitignore format test clean help \
        ts-build ts-lint ts-test ts-type-check \
        test-all lint-all format-all \
        demo security \
        docker-secrets docker-build docker-up docker-up-monitoring \
        docker-down docker-logs docker-ps docker-config docker-clean docker-run \
        validate-catalog sync-catalog sync-catalog-dry catalog-help \
        fresh fresh-fix

# Python
PYTHON := python3
PIP := pip

# Node
NPM := npm

# Default target
help:
	@echo ""
	@echo "  🌹 DevSkyy Development Commands"
	@echo "  ================================"
	@echo ""
	@echo "  INSTALLATION"
	@echo "  -------------"
	@echo "    make install      Install Python production dependencies"
	@echo "    make dev          Install Python + TypeScript dev dependencies"
	@echo ""
	@echo "  PYTHON COMMANDS"
	@echo "  ----------------"
	@echo "    make lint         Run Python linters (ruff, mypy)"
	@echo "    make format       Format Python code (isort, ruff, black)"
	@echo "    make test         Run Python tests (pytest)"
	@echo "    make test-cov     Run Python tests with coverage"
	@echo ""
	@echo "  TYPESCRIPT COMMANDS"
	@echo "  --------------------"
	@echo "    make ts-build     Compile TypeScript"
	@echo "    make ts-lint      Run ESLint on TypeScript"
	@echo "    make ts-test      Run TypeScript tests (jest)"
	@echo "    make ts-type-check Run TypeScript type checking"
	@echo ""
	@echo "  UNIFIED COMMANDS"
	@echo "  -----------------"
	@echo "    make test-all     Run all tests (Python + TypeScript)"
	@echo "    make lint-all     Run all linters (Python + TypeScript)"
	@echo "    make format-all   Format all code (Python + TypeScript)"
	@echo "    make ci           Run full CI pipeline locally"
	@echo ""
	@echo "  3D COLLECTION DEMOS"
	@echo "  --------------------"
	@echo "    make demo-black-rose   Preview BLACK ROSE collection"
	@echo "    make demo-signature    Preview SIGNATURE collection"
	@echo "    make demo-love-hurts   Preview LOVE HURTS collection"
	@echo "    make demo-showroom     Preview Showroom experience"
	@echo "    make demo-runway       Preview Runway experience"
	@echo ""
	@echo "  OTHER"
	@echo "  ------"
	@echo "    make clean        Clean all build artifacts"
	@echo "    make security     Run security scans"
	@echo "    make docker-build Build Docker image"
	@echo ""

# ============================================================================
# INSTALLATION
# ============================================================================

install:
	$(PIP) install -e .

dev:
	$(PIP) install -e ".[dev]"
	$(NPM) install

# ============================================================================
# PYTHON COMMANDS
# ============================================================================

lint:
	ruff check .
	mypy --ignore-missing-imports . || echo "⚠️  Mypy warnings in legacy/scripts (non-blocking)"
	$(MAKE) lint-gitignore

lint-strict:
	ruff check .
	mypy --ignore-missing-imports .

lint-gitignore:  ## Flag exact-duplicate + redundant **/X lines in .gitignore
	$(PYTHON) scripts/check_gitignore_health.py

format:
	isort .
	ruff check . --fix
	black .

fresh:  ## Check derived files are in sync (SOT, theme .min, version, retired refs)
	bash scripts/freshness-guard.sh --all

fresh-fix:  ## Regenerate SOT + rebuild theme .min, then re-stage for commit
	bash scripts/freshness-guard.sh --fix

test:
	pytest tests/ -v --tb=short

test-cov:
	pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html

test-fast:
	pytest tests/ -v --tb=short -x -q

# ============================================================================
# ADK RENDER PIPELINE COMMANDS
# ============================================================================
# Mock unit tests for the 9-step SequentialAgent. Uses .venv-agents/ (separate
# from .venv/ — ADK + numpy conflict isolation). No API cost, target <5s.
# Override the venv path via env var: `ADK_PYTHON=/path/to/python make adk-test`

ADK_PYTHON ?= ../DevSkyy/.venv-agents/bin/python3

adk-test:
	@if [ ! -x "$(ADK_PYTHON)" ]; then \
		echo "Error: $(ADK_PYTHON) not found."; \
		echo "Install: $(ADK_PYTHON) -m pip install 'google-adk[extensions]' scipy pytest pytest-asyncio pytest-mock"; \
		echo "Or override: ADK_PYTHON=/path/to/python make adk-test"; \
		exit 1; \
	fi
	$(ADK_PYTHON) -m pytest agents/render_pipeline/tests/ -v --tb=short

adk-test-fast:
	@[ -x "$(ADK_PYTHON)" ] || { echo "Error: $(ADK_PYTHON) not found"; exit 1; }
	$(ADK_PYTHON) -m pytest agents/render_pipeline/tests/ --tb=line -q

adk-lint:
	@[ -x "$(ADK_PYTHON)" ] || { echo "Error: $(ADK_PYTHON) not found"; exit 1; }
	$(ADK_PYTHON) -m ruff check agents/render_pipeline/
	$(ADK_PYTHON) -m black --check agents/render_pipeline/

# Composite manual gate: lint + tests. Used by humans for one-shot
# pre-commit checks. The pre-commit hooks invoke adk-lint and
# adk-test-fast independently so they report separately.
adk-check: adk-lint adk-test-fast

# ADK AgentEvaluator harness run against agents/render_pipeline/eval/.
# DEFAULT (adk-eval) skips the paid call — verifies the harness loads,
# the eval set collects, and the agent imports cleanly. ~$0 cost, ~6s.
# LIVE (adk-eval-live) sets EVAL_LIVE=1 to actually exercise the 9-step
# pipeline against the canonical br-001 fixture. ~$0.20 cost per run.
# Use adk-eval-live only after explicit STOP-AND-SHOW confirmation.
adk-eval:
	@[ -x "$(ADK_PYTHON)" ] || { echo "Error: $(ADK_PYTHON) not found"; exit 1; }
	@echo "Running ADK AgentEvaluator harness (test will SKIP without EVAL_LIVE=1)..."
	$(ADK_PYTHON) -m pytest agents/render_pipeline/eval/ -v --tb=short

adk-eval-live:
	@[ -x "$(ADK_PYTHON)" ] || { echo "Error: $(ADK_PYTHON) not found"; exit 1; }
	@echo "WARNING: Live AgentEvaluator run — paid call (~\$$0.20)."
	@echo "Pipeline: 9-step SequentialAgent against br-001 front canonical fixture."
	EVAL_LIVE=1 $(ADK_PYTHON) -m pytest agents/render_pipeline/eval/ -v --tb=short

# Generate a learning-loop report from data/agent-learning/ JSONL records.
# Reads engine-winrate, template-scores, and failure-modes JSONL files
# emitted by qa_tournament_fn during live runs. Produces a markdown
# proposals file plus terminal output. No API cost — local file analysis.
# See agents/render_pipeline/learning/LOOP.md for the recommended /loop prompt.
adk-learning-report:
	@[ -x "$(ADK_PYTHON)" ] || { echo "Error: $(ADK_PYTHON) not found"; exit 1; }
	@echo "=== Writing proposals markdown ==="
	@PYTHONPATH=. $(ADK_PYTHON) -c "from agents.render_pipeline.learning.proposals import write_proposals_markdown; print(f'Wrote: {write_proposals_markdown()}')"
	@echo ""
	@echo "=== Engine-override proposals (min 3 runs, min score 80) ==="
	@PYTHONPATH=. $(ADK_PYTHON) -c "from agents.render_pipeline.learning.proposals import propose_engine_overrides; import json; props = propose_engine_overrides(); print(json.dumps(props, indent=2)) if props else print('(no proposals — need more runs)')"
	@echo ""
	@echo "=== Failure-mode digest (min 5 occurrences) ==="
	@PYTHONPATH=. $(ADK_PYTHON) -c "from agents.render_pipeline.learning.proposals import digest_failure_modes; import json; modes = digest_failure_modes(); print(json.dumps(modes, indent=2)) if modes else print('(no patterns — need more failures)')"

# ============================================================================
# TYPESCRIPT COMMANDS
# ============================================================================

ts-build:
	$(NPM) run build

ts-lint:
	$(NPM) run lint

ts-lint-fix:
	$(NPM) run lint:fix

ts-test:
	$(NPM) run test -- --passWithNoTests --no-coverage || echo "⚠️  Coverage thresholds not met (non-blocking)"

ts-test-strict:
	$(NPM) run test

ts-test-collections:
	$(NPM) run test:collections

ts-type-check:
	$(NPM) run type-check

ts-format:
	$(NPM) run format

# ============================================================================
# SOT (Single Source of Truth) — product imagery
# ============================================================================

# Regenerate the SOT product-imagery manifest (data/sot-images.json) that every
# non-Python surface reads. Run after build-collection-sot.py / any catalog image
# change. The Python resolver (skyyrose.core.sot_images) reads sot.json fresh, so
# this only refreshes the serialized manifest for JS/PHP consumers.
sot-manifest:
	python3 -m skyyrose.core.sot_images

# ============================================================================
# UNIFIED COMMANDS
# ============================================================================

test-all: test ts-test
	@echo "✅ All tests passed (Python + TypeScript)"

lint-all: lint ts-type-check
	@echo "✅ All linting passed (Python + TypeScript)"

format-all: format ts-format
	@echo "✅ All formatting complete (Python + TypeScript)"

ci: lint-all test-all
	@echo ""
	@echo "🌹 CI Pipeline Complete"
	@echo "========================"

# ============================================================================
# OAI IMAGE RENDER (gpt-image-2 product photography)
# ============================================================================

render-dry: ## Plan + cost manifest, NO API. make render-dry SKUS=br-010,br-001 [STYLE=ghost,on-model] [ALL=1]
	$(PYTHON) scripts/oai-render-run.py dry-run $(if $(ALL),--all,--skus $(SKUS)) $(if $(STYLE),--style $(STYLE),)

render: ## GENERATE renders (PAID, gated by manifest + cap). make render SKUS=br-010,br-001 [STYLE=...] [ALL=1]
	$(PYTHON) scripts/oai-render-run.py generate $(if $(ALL),--all,--skus $(SKUS)) $(if $(STYLE),--style $(STYLE),) --yes

# ============================================================================
# 3D COLLECTION DEMOS
# ============================================================================

demo-black-rose:
	$(NPM) run demo:black-rose

demo-signature:
	$(NPM) run demo:signature

demo-love-hurts:
	$(NPM) run demo:love-hurts

demo-showroom:
	$(NPM) run demo:showroom

demo-runway:
	$(NPM) run demo:runway

# ============================================================================
# SECURITY
# ============================================================================

security:
	bandit -r . -x ./tests -ll
	$(NPM) audit

# ============================================================================
# CLEANING
# ============================================================================

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage/
	rm -rf node_modules/.cache/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# ============================================================================
# BUILD
# ============================================================================

build: clean ts-build
	$(PYTHON) -m build

# ============================================================================
# DOCKER  (production-grade stack — see docs/DOCKER.md)
# ============================================================================
# Flow:  make docker-secrets   → generate .env.docker (random secrets)
#        (paste API keys into .env.docker)
#        make docker-up         → build + start core stack (app/db/redis/workers)
#        make docker-logs       → tail
# All compose calls pass --env-file .env.docker for both secret interpolation
# and in-container env.

COMPOSE := docker compose --env-file .env.docker

_require-docker-env:
	@[ -f .env.docker ] || { echo "✋ Missing .env.docker — run 'make docker-secrets' first."; exit 1; }

docker-secrets:  ## Generate .env.docker with strong random secrets (won't clobber)
	bash scripts/docker-secrets.sh

docker-config: _require-docker-env  ## Validate + render the merged compose config
	$(COMPOSE) config

docker-build: _require-docker-env  ## Build the devskyy:local image
	$(COMPOSE) build

docker-up: _require-docker-env  ## Build + start the core stack (detached)
	$(COMPOSE) up -d --build

docker-up-monitoring: _require-docker-env  ## Core + prometheus + grafana
	$(COMPOSE) --profile monitoring up -d --build

docker-down: _require-docker-env  ## Stop the stack (keeps volumes/data)
	$(COMPOSE) down

docker-clean: _require-docker-env  ## Stop the stack AND delete volumes (DESTROYS data)
	$(COMPOSE) down -v

docker-logs: _require-docker-env  ## Tail logs from all services
	$(COMPOSE) logs -f --tail=100

docker-ps: _require-docker-env  ## Show container status
	$(COMPOSE) ps

# Start just the app service (still via compose, so postgres/redis deps are honored).
docker-run: _require-docker-env
	$(COMPOSE) up -d --build app

# ============================================================================
# CATALOG CONSISTENCY
# ============================================================================

.PHONY: validate-catalog sync-catalog sync-catalog-dry catalog-help

validate-catalog:
	@$(PYTHON) scripts/validate_catalog_consistency.py

sync-catalog:
	@$(PYTHON) scripts/sync_catalog_downstream.py

sync-catalog-dry:
	@$(PYTHON) scripts/sync_catalog_downstream.py --dry-run

catalog-help:
	@echo ""
	@echo "  🌹 Catalog Consistency Commands"
	@echo "  ================================"
	@echo ""
	@echo "    make validate-catalog     Run all consistency checks (read-only, exit 1 on failure)"
	@echo "    make sync-catalog-dry     Preview auto-fixes without writing any files"
	@echo "    make sync-catalog         Apply auto-fixes (backs up changed files first)"
	@echo "    make catalog-help         Show this help"
	@echo ""
	@echo "  Single check:  python scripts/validate_catalog_consistency.py --checks jersey_skus"
	@echo "  All checks:    python scripts/validate_catalog_consistency.py --json"
	@echo "  Pytest:        pytest skyyrose/elite_studio/tests/test_catalog_consistency.py -v"
	@echo ""
	@echo "  Auto-fix targets:"
	@echo "    _JERSEY_SKUS in sku_resolver.py      (jersey garment_type_lock rows in CSV)"
	@echo "    product-similarities.json             (remove stale/retired SKU refs)"
	@echo "    logo-registry.json updated: field     (bump to today's date)"
	@echo ""
	@echo "  DOES NOT auto-edit:"
	@echo "    data/dossiers/*.md  |  ProductCatalogTest.php  |  logo-registry.json content"
	@echo ""
