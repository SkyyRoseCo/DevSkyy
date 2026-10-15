# SkyyRose Suite — Wiring Map

How the `skyyrose-suite` plugins connect to the **Elite Team** (Python runtime SuperAgents), the **Elite Studio** imagery pipelines, and the **dev-team** workflow. The seven personas below now live across `skyyrose-market` (6) and `skyyrose-design` (photography-director). Every claim cites the source verified during the 2026-06-05 discovery pass.

---

## 1. Two planes, one team

The plugin operates on the **authoring plane** (Claude Code skills + subagent personas). The SkyyRose platform runs on the **runtime plane** (Python `EnhancedSuperAgent` classes in `agents/`). They are not competitors — the authoring plane is where a human + Claude draft, brief, and QA; the runtime plane is where the platform executes at scale (WordPress publish, image generation, WooCommerce writes).

```
 AUTHORING PLANE (this plugin)                RUNTIME PLANE (agents/*.py)
 ┌─────────────────────────────┐             ┌────────────────────────────────┐
 │ /skyyrose  (command)        │             │ EnhancedSuperAgent base        │
 │   ├─ content-engine  ◄──────┼──maps to────┤ SkyyRoseContentAgent           │
 │   ├─ email-strategist ◄─────┼──maps to────┤ MarketingAgent (email cap)     │
 │   ├─ paid-media-buyer ◄─────┼──maps to────┤ agents/core/marketing/ (slot)  │
 │   ├─ seo-commerce    ◄──────┼──maps to────┤ ContentType.SEO_META           │
 │   ├─ influencer-lead ◄──────┼──maps to────┤ MarketingAgent (influencer cap)│
 │   ├─ photography-dir ◄──────┼──maps to────┤ SkyyRoseImageryAgent (CAMPAIGN)│
 │   └─ launch-commander◄──────┼──maps to────┤ core/orchestrator route+fanout │
 └─────────────────────────────┘             └────────────────────────────────┘
            │                                              │
            └──────────── shared source of truth ─────────┘
              catalog CSV + per-SKU dossiers + brand-dna
```

---

## 2. Persona → runtime seam map

Source: `agents/base_super_agent/agent.py`, `agents/skyyrose_content_agent.py`, `agents/marketing_agent.py`, `agents/core/orchestrator.py`, `agents/skyyrose_imagery_agent.py`.

| Plugin agent | Runtime entry point | Seam |
|---|---|---|
| `skyyrose-content-engine` | `SkyyRoseContentAgent.generate_content(ContentRequest(content_type=PRODUCT_DESCRIPTION/COLLECTION_PAGE, sku, collection))` | Persona injected via `AgentConfig.system_prompt`; `context=` kwarg on `execute_auto` bypasses auto-RAG to inject brand-dna |
| `skyyrose-email-strategist` | `MarketingAgent` (`sub_capabilities` includes `email_campaigns`; `TECHNIQUE_MAP["email"]=CHAIN_OF_THOUGHT`) or `agents/claude_sdk/email_automation.py` | `execute_auto(task_type=TaskCategory.MARKETING)` |
| `skyyrose-paid-media-buyer` | New `CoreAgent` in `agents/core/marketing/` registered via `orchestrator.register_core_agent()` | `CoreAgentType.MARKETING` keyword route (`agents/core/orchestrator.py:35`) |
| `skyyrose-seo-commerce` | `SkyyRoseContentAgent.generate_content(content_type=ContentType.SEO_META)` | same as content; SEO meta writes to WC via `meta_data` |
| `skyyrose-influencer-lead` | `MarketingAgent` (`influencer_outreach` cap; `TECHNIQUE_MAP["influencer"]=REACT`) | `sub_capabilities` routing |
| `skyyrose-photography-director` | `SkyyRoseImageryAgent.generate_image(purpose=ImageryPurpose.CAMPAIGN, collection)` | imagery purpose enum |
| `skyyrose-launch-commander` | `agents/core/orchestrator.py` `route(task)` → fan-out across the six | orchestrator dispatch |

**Base-class contract** (any new runtime persona): set `agent_type: SuperAgentType` + `sub_capabilities: list[str]` at class scope, implement `async execute(self, prompt, **kwargs)`, import `AgentConfig`/`AgentResult`/`AgentStatus` from `adk.base`. Call `await agent.initialize()` before use. Prefer `execute_auto(...)`.

---

## 3. Pipeline relationships

- **Elite Studio** (`skyyrose/elite_studio/`) is the imagery hub — LangGraph graph (`graph/builder.py`), FLUX synthesis (`synthesis/flux_pipeline.py`), 6-stage compositor. The **photography-director** persona authors the *brief*; Elite Studio *executes* the render. Entry: `coordinator.produce(sku, view)` / `platform/service.generate_3d(tenant_id, sku, ...)`. The lockup is composited at the Elite Studio stage — never burned into camera (see `skyyrose-photography-brief`).
- **3D round table** (`orchestration/threed_round_table.py`) is the 3D stage inside Elite Studio — not a marketing touchpoint, but launch-commander references it when a drop needs 3D PDP assets.
- **ADK render_pipeline** (`agents/render_pipeline/`) — 9-step product render, callable engine inside Elite Studio. Marketing copy and imagery run on separate dispatch paths today (`orchestration/asset_pipeline.py` does NOT call the content/marketing agents) — launch-commander is the coordination layer that sequences them.
- **Data spine**: every persona resolves product facts through `wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv` + `knowledge-base/products/<sku>/` dossier → content agent → WooCommerce REST `meta_data` (SEO) / `description` / `short_description`.

---

## 4. Dev-team workflow lane

Source: `plugins/skyyrose/workflows/skyyrose-dev-team.js` (embedded in the orchestrator plugin, CHARTER co-located; the original dev-time copy remains at `.claude/workflows/`). The marketing lane is added via the **`batch` enum** (least-invasive option A):

```js
// PLAN_SCHEMA, ~js:37 — extend the enum
batch: { type: 'string', enum: ['frontend', 'backend', 'marketing'] }

// agentFor(), ~js:121 — map the new batch to the dispatcher command
function agentFor(batch) {
  if (batch === 'frontend')  return 'Frontend Developer'
  if (batch === 'marketing') return 'skyyrose-launch-commander'  // plugin agent
  return 'Backend Architect'
}
```

The architect (Phase 1) can then assign marketing workstreams (copy, email, SEO, photography briefs) with `batch: 'marketing'`; the existing `pipeline()` fan-out (js:162-195) runs them alongside FE/BE workstreams, and the Phase-3 review loop reviews them. The workflow now ships **embedded** in the `skyyrose` orchestrator plugin (`plugins/skyyrose/workflows/`), so it travels with the suite; the copy under the gitignored `.claude/workflows/` remains the dev-time original.

---

## 5. Canon enforcement (cross-cutting)

Every skill and agent inherits these from `skyyrose-brand-dna` + its `brand-guardrails.md`:

- Tagline: No tagline is authorised (founder decision 2026-10-06).
- Collection voice isolation — Black Rose / Love Hurts / Signature / Kids Capsule never cross-attributed.
- Products by **name**, never SKU, resolved from the catalog CSV.
- Visual references = **The Five** (Kith, Oaklandish, Culture Kings, Fear of God, Palm Angels) — never European luxury-house lineage.
- Collection names in hero positions = **lockup PNG assets**, never type-rendered.
- **No cross-sell / no related-products on PDP. No urgency timers.** Garment is the protagonist.
- **STOP-AND-SHOW** on every paid-media spend, Klaviyo send, WooCommerce write, and media upload.
