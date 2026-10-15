#!/usr/bin/env bash
# Offline/mocked verification only. Never creates credentials or dispatches models.
set -euo pipefail
repo_root="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$repo_root"
export PYTHONPATH="$repo_root/tasks/prompt-model-audit:$repo_root"
.venv/bin/python -m pytest -p offline_guard -o addopts='' -q --disable-warnings \
  tests/test_product_readiness.py tests/test_product_entry_point.py \
  skyyrose/elite_studio/tests/test_logo_registry.py \
  tests/test_product_consumer_contracts.py tests/pipelines/test_oai_render_hardening.py \
  tests/elite_studio/platform/test_catalog_source.py \
  skyyrose/elite_studio/tests/test_dual_vision_gate.py \
  skyyrose/elite_studio/tests/test_three_d_agent.py \
  skyyrose/elite_studio/tests/test_ghost_mannequin_preflight.py \
  tests/test_prompt_model_contracts.py tests/test_openai_settings_contract.py \
  tests/test_prompt_intelligence.py tests/test_llm.py tests/test_creative_job.py \
  tests/test_context_resolver.py skyyrose/elite_studio/tests/test_ghost_mannequin_qa.py \
  skyyrose/elite_studio/tests/test_coordinator.py tests/test_graph_nodes_quality.py \
  skyyrose/elite_studio/tests/test_graph_nodes_quality.py \
  skyyrose/elite_studio/tests/test_graph_nodes.py skyyrose/elite_studio/tests/test_graph_edges.py \
  skyyrose/elite_studio/tests/test_gemini_rest.py
(
  cd agents/elite_web_builder
  "$repo_root/.venv/bin/python" -m pytest -p offline_guard --confcutdir=. \
    --import-mode=importlib -o addopts='' -q --disable-warnings \
    tests/test_provider_adapters.py tests/test_agent_runtime.py
)
npm test -- src/services/__tests__/OpenAIService.test.ts src/services/__tests__/openai-sdk-compatibility.test.ts
npm run type-check
node_modules/.bin/eslint src/services/OpenAIService.ts src/services/__tests__/OpenAIService.test.ts
node_modules/.bin/prettier --check src/services/OpenAIService.ts src/services/__tests__/OpenAIService.test.ts
.venv/bin/python scripts/sync_product_registry.py --check
git diff --check
