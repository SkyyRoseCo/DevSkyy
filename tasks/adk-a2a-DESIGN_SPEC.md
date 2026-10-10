# DESIGN_SPEC.md — `devskyy-a2a` (DevSkyy A2A Coordinator)

## Overview

The DevSkyy codebase has a sophisticated Python agent stack (Claude SDK domain agents,
LangGraph creative pipeline, CrewAI orchestration, a 3D round-table tournament, and a
6-stage imagery compositor) running behind FastAPI at `main_enterprise.py`. Today the
Vercel dashboard at `devskyy.app` does **not** call into this stack; its Next.js API
routes (`frontend/app/api/imagery/route.ts`, `frontend/app/api/pipeline/tripo/route.ts`,
etc.) talk to Gemini, Tripo, Meshy, and FASHN directly. Each route reimplements
fragments of cost gating, retry logic, and the STOP-AND-SHOW human-in-the-loop
confirmation that the Python side already owns. There is no single control plane.

`devskyy-a2a` is a Google ADK A2A-compliant agent that exposes the existing Python
agent graph as a single network-addressable service. External callers (the Vercel
dashboard, MCP tools, Ralph, future integrations) send a normalized A2A request to
one endpoint; the coordinator routes to the right internal agent (`SDKGarment3DAgent`,
`CompositorAgent`, `CommerceAgent`, `BrandGuardianAgent`, etc.) using the homegrown
`adk/google_adk.py` adapter for model resolution, applies cost gating before any
paid-API stage, persists session state through ADK's session manager, and returns
a structured response.

The coordinator does **not** re-implement the agents themselves. Its job is
routing, gating, session continuity, and observability. Implementations stay in
`agents/` and `skyyrose/elite_studio/`; this layer is glue + protocol + policy.

---

## Example Use Cases

### 1. Vercel dashboard requests a 3D model for a SKU
**Caller:** `frontend/app/api/pipeline/tripo/route.ts` (current direct-Tripo call → migrated to A2A)
**Input:**
```json
{
  "skill": "generate_3d_model",
  "params": { "sku": "br-001", "quality": "production" }
}
```
**Behavior:** A2A coordinator routes to `orchestration/threed_round_table.py`, which runs
Tripo + Meshy + HuggingFace in parallel, scores them, returns the winner. Confirms the
paid-API budget against the request's `max_cost_usd` field before dispatching.
**Output:** `{ "asset_url": "...", "provider": "tripo", "cost_usd": 0.40, "session_id": "..." }`

### 2. MCP tool requests a dossier-grounded product description
**Caller:** A Claude Code session via the future `mcp__devskyy__describe_product` tool
**Input:**
```json
{
  "skill": "product_description",
  "params": { "sku": "lh-002", "audience": "luxury", "max_words": 60 }
}
```
**Behavior:** Routes to `agents/claude_sdk/domain_agents/commerce.py:CommerceAgent`,
which calls `skyyrose.core.dossier_loader.get_product_with_dossier(sku)` and grounds
the description in the per-product dossier. Returns deterministic-with-temperature copy.
**Output:** `{ "description": "...", "dossier_slug": "love-meets-luxury-tote", "tokens_used": 412 }`

### 3. CI workflow requests imagery QA on a render
**Caller:** GitHub Actions post-render step (post-imagery-pipeline)
**Input:**
```json
{
  "skill": "qa_render",
  "params": { "image_path": "renders/output/br-001-front.webp", "sku": "br-001" }
}
```
**Behavior:** Routes to `skyyrose/elite_studio/agents/quality_agent.py:QualityAgent`,
which dual-scores against `assets/golden/br-001/reference.jpg` (SSIM via
`skyyrose/elite_studio/quality/visual_regression.py`) plus a Claude+Gemini judge pass
from `llm/creative_judge.py:CreativeJudge`. Returns pass/fail + structured verdict.
**Output:** `{ "verdict": "pass", "ssim": 0.94, "judge_scores": {...}, "session_id": "..." }`

### 4. Ralph Wiggum loop iteration requests brand consistency check
**Caller:** Ralph (`@th0rgal/ralph-wiggum`) during a multi-iteration generative task
**Input:**
```json
{
  "skill": "brand_check",
  "params": { "asset_url": "...", "collection": "black-rose" }
}
```
**Behavior:** Routes to `agents/claude_sdk/domain_agents/brand_guardian.py:BrandGuardianAgent`,
which validates color palette (`#0a0a0a`, `#C0C0C0`), tagline ("" — never "Where Love Meets Luxury"), and collection-specific iconography.
**Output:** `{ "compliant": false, "violations": ["forbidden tagline detected"], "fix_suggestions": [...] }`

### 5. External partner agent (future) requests product availability
**Caller:** A partner ADK agent over A2A wire format (uses `.well-known/agent.json` to discover us)
**Input:**
```json
{
  "skill": "list_products",
  "params": { "collection": "signature", "in_stock_only": true }
}
```
**Behavior:** Routes to a thin wrapper around
`wordpress-theme/skyyrose-flagship/inc/product-catalog.php`-equivalent Python loader
(`skyyrose/core/catalog_loader.py:read_catalog_rows`). Read-only, no auth required.
**Output:** `{ "products": [...], "count": 15, "collection": "signature" }`

---

## Tools Required

| Tool | Source | Purpose | Auth |
|------|--------|---------|------|
| `route_to_3d_pipeline` | `orchestration/threed_round_table.py` | Run Tripo+Meshy+HF tournament | Tripo API key, Meshy API key, HF token in `.env` |
| `route_to_imagery_pipeline` | `skyyrose/elite_studio/agents/compositor_agent.py` | 6-stage compositor (BRIA→IC-Light→FLUX Fill→GPSDiff→Gemini QA) | Gemini API key, FLUX provider creds |
| `route_to_commerce_agent` | `agents/claude_sdk/domain_agents/commerce.py` | Dossier-grounded product copy + recommendations | `ANTHROPIC_API_KEY` |
| `route_to_brand_guardian` | `agents/claude_sdk/domain_agents/brand_guardian.py` | Brand rule enforcement (tagline, palette, collection iconography) | `ANTHROPIC_API_KEY` |
| `route_to_quality_agent` | `skyyrose/elite_studio/agents/quality_agent.py` | Dual-model judge + SSIM regression | `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY` |
| `route_to_catalog_retriever` | `orchestration/catalog_retriever.py` | Semantic search over 33-SKU catalog + dossiers | Local SentenceTransformers (no auth) |
| `get_session_state` | ADK `InMemorySessionService` (prototype) → Cloud SQL/`agent_engine` later | Multi-turn session continuity | GCP IAM when promoted from prototype |
| `cost_gate` | New thin module under `agents/adk_a2a/policy/cost_gate.py` | Reject requests that would exceed `max_cost_usd` cap | None (in-process) |

The agent does **not** implement any of the underlying logic — it dispatches to
existing classes and returns their output through ADK's `Runner`.

---

## Constraints & Safety Rules

### Hard-blocks (request rejected before any work runs)
1. **No paid-API call without explicit `max_cost_usd` in the request.** The cost gate
   computes an estimate from the skill (e.g., FASHN tryon = $1.20 fixed, Gemini gen ≈
   $0.039/image) and rejects if estimate > cap.
2. **No write to skyyrose.co.** This agent is read-only against the WordPress storefront.
   Mutations stay in the FastAPI WooCommerce REST endpoints behind STOP-AND-SHOW.
3. **No execution of arbitrary shell or Python code.** The skill registry is closed —
   only enumerated skills (`generate_3d_model`, `qa_render`, etc.) can run. Unknown
   skill name → 400.
4. **No writes to `wordpress-theme/skyyrose-flagship/data/`.** Catalog and dossiers are
   immutable from this agent's perspective. They're authored by Corey, not by agents.
5. **Never resurrect retired SKUs.** Reject any request naming `lh-001`, `sg-004`,
   `sg-008`, `sg-010`, or any `sg-d0[1-4]`/`br-d0[1-4]` (per CLAUDE.md, retired list).
6. **Never use the retired tagline "Where Love Meets Luxury".** The brand_guardian
   skill must flag it; the commerce skill must never emit it.

### Behavioral rules
- All paid-API calls log to a structured audit log: `{timestamp, caller, skill, params, cost_estimate, cost_actual, outcome}`.
- Sessions persist tool-call history so multi-turn flows (e.g., "QA this render → fix
  these issues → QA again") share context.
- The agent uses the existing `adk/google_adk.py` model adapter — Claude via LiteLlm
  for non-Google models, Gemini natively. Do not re-implement model routing.
- Failure mode: any internal agent exception is caught, structured, returned as
  `{ "error": {...}, "skill": "...", "session_id": "..." }` — never crash the A2A
  server or leak Python tracebacks across the wire.

---

## Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Vercel dashboard imagery routes migrated to A2A | 100% (4 routes today: imagery, pipeline/tripo, fashn, generate) | Audit `frontend/app/api/` for direct provider calls; should be zero post-migration |
| P50 latency for `qa_render` skill | ≤ 3.0 s end-to-end | Captured in audit log; reported via `/health` |
| Cost-gate rejection precision | 100% (no paid call ever runs after rejection) | Integration test: mock provider client, assert no HTTP call when over budget |
| Session continuity | Multi-turn requests share state correctly | Test: 3-turn QA-and-fix flow returns coherent results without re-loading dossiers |
| Brand rule enforcement | 100% (zero "Where Love Meets Luxury" emitted) | Regression test against 50 historical product descriptions |
| Coverage of skill registry | ≥ 90% of skill paths exercised by tests | `pytest --cov=agents/adk_a2a/` |
| A2A discovery | `.well-known/agent.json` returns valid AgentCard | Smoke test via `curl localhost:8080/.well-known/agent.json` |

---

## Edge Cases

1. **Paid-API budget cap is exactly the estimate.** Cost gate uses `<=` (allow), not `<`
   (deny). Test with `max_cost_usd=0.040` against a Gemini gen estimate of `$0.039`.

2. **Caller passes a SKU not in the catalog.** Reject with `404 sku_not_found` + the
   nearest 3 SKUs by SentenceTransformers similarity (so the caller can disambiguate).
   Do **not** silently fall back to a default SKU.

3. **Underlying agent times out (e.g., Tripo 3D takes >120s).** A2A returns `503 upstream_timeout`
   with `session_id` so the caller can retry idempotently. The 3D round table already
   has a circuit breaker — surface it; don't double-retry at the A2A layer.

4. **Multiple concurrent requests for the same SKU's render.** Use the existing Redis
   cache at `orchestration/asset_pipeline.py:ProductAssetPipeline` (already
   request-coalesced). A2A layer adds nothing — just makes sure the cache key
   includes the requested skill, not just the SKU.

5. **Caller sends a malformed A2A request (missing `skill` field).** Return
   `400 missing_skill` with the list of valid skill names. Never crash the agent loop.

6. **Dossier file is missing for a referenced SKU.** Per `feedback_no_silent_fallback.md`,
   hard-fail with `500 missing_dossier` rather than substitute `branding_spec`. The
   error message must include the expected dossier path so authors can fix it.

7. **GCP credentials expire mid-session (when deployed).** ADK's session manager
   transparently refreshes via the service account. Test by injecting an expired token;
   assert the request completes after one transparent refresh.

---

## Pre-conditions before scaffolding

| Check | Status | Action |
|-------|--------|--------|
| `uvx` installed | ✅ `uvx 0.11.3` | None |
| Target dir `agents/adk_a2a/` absent | ✅ does not exist | None |
| `.venv-agents/` exists | ✅ exists but empty | `python -m venv .venv-agents && .venv-agents/bin/pip install -r skyyrose/requirements-agents.txt` (post-scaffold) |
| `adk/google_adk.py` adapter | ✅ exists | Import from new agent |
| GCP project + Cloud Run API | ⚠️ unknown | Required only when promoting from prototype to deployment; **not** required for scaffolding |
| `.env` has `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `TRIPO_API_KEY`, `MESHY_API_KEY`, `HF_TOKEN` | ⚠️ partial (verified in CLAUDE.md but not audited) | Verify before first run |

---

## Scaffold command (proposed — awaiting `y` to execute)

```bash
uvx agent-starter-pack create devskyy-a2a \
  --agent adk_a2a \
  --deployment-target none \
  --prototype \
  --agent-directory agents \
  --agent-guidance-filename CLAUDE.md \
  -y
```

**Why these flags:**
- `--agent adk_a2a` — A2A scaffolding cannot be hand-rolled (`AgentCard` schema + `to_a2a()` signature change across versions).
- `--deployment-target none` + `--prototype` — skip Terraform/CI/CD/Dockerfile for now. Add Cloud Run later via `enhance` after agent code is verified working in `.venv-agents/`.
- `--agent-directory agents` — match this codebase's convention; the project structure already has `agents/` as the agent root.
- `--agent-guidance-filename CLAUDE.md` — DevSkyy uses CLAUDE.md, not the ASP default `GEMINI.md`.
- `-y` — auto-approve ASP's own internal prompts (the user-facing approval gate is *this* spec, not ASP's confirmations).

**Project name:** `devskyy-a2a` (12 chars; well under the 26-char ceiling; matches the `devskyy.app` brand).

**Resulting directory:** `/Users/theceo/DevSkyy/agents/devskyy-a2a/` (the CLI will create it; the skill explicitly forbids pre-`mkdir`).

---

## Post-scaffold next steps (do **not** run until scaffolding succeeds)

1. `python -m venv .venv-agents && .venv-agents/bin/pip install -r skyyrose/requirements-agents.txt`
2. Move scaffolded code into `agents/devskyy-a2a/` if ASP uses a different layout.
3. Wire the homegrown `adk/google_adk.py` adapter as the model resolver inside the new agent (do not re-implement model routing).
4. Implement the 7 enumerated skills as thin dispatchers — each one ≤ 30 lines, just
   imports the existing class, validates input, calls, returns.
5. Add `.well-known/agent.json` AgentCard at the FastAPI mount path so external A2A
   agents can discover this one.
6. Add integration tests in `tests/integration/test_devskyy_a2a.py` that exercise each
   skill against mocked providers (no live paid-API calls in CI).
7. Once stable, run `uvx agent-starter-pack enhance . --deployment-target cloud_run --cicd-runner github_actions` to add deployment infra.

---

## Why ADK A2A specifically (not LangGraph, not CrewAI, not raw FastAPI)

- **LangGraph** — already in use for the imagery creative pipeline. Excellent for *internal*
  multi-step state machines. Has no built-in network protocol for external callers.
  Wrapping it in custom HTTP would re-invent A2A.
- **CrewAI** — already used inside `orchestration/`. Good for role-based crew composition.
  No A2A protocol; no managed deployment story.
- **Raw FastAPI** — already in use at `main_enterprise.py`. Could absolutely host a
  `/agents/execute` endpoint. But there's no standard wire format → every external
  caller invents its own request shape → exactly the fragmentation the Vercel API
  routes already exhibit.
- **ADK A2A** — gives a *standard* protocol (`AgentCard`, skill discovery via
  `.well-known/agent.json`, normalized request/response envelope) plus a managed
  deployment path (Vertex Agent Engine or Cloud Run with first-class GCP integration).
  Future external integrations get a known wire format for free.

The decision is not "ADK is best at routing" — FastAPI routes equally well. The
decision is "A2A is the only standardized protocol, and ADK is the only Python SDK
that scaffolds it correctly."
