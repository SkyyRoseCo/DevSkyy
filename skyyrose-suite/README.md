# SkyyRose Suite

A private Claude Code **marketplace** of five plugins — an orchestrator plus four themed teams (marketing, design, core-engineering, QA) — each grounded in verified vendor docs and wired to the SkyyRose Elite Studio runtime and dev-team pipeline.

> No tagline is authorised (founder decision 2026-10-06).

## The five plugins

| Plugin | What it does | Skills | Agents |
|--------|--------------|-------:|-------:|
| **`skyyrose`** | Orchestrator + front door. `/skyyrose <task>` classifies and routes; runs the embedded dev-team workflow for multi-step work. | — | 1 |
| **`skyyrose-market`** | Brand DNA, product copy, WooCommerce SEO, Klaviyo email flows, paid media, influencer growth, photography briefs, launch orchestration, 30+ social skills. | 50 | 6 |
| **`skyyrose-design`** | Imagery (gpt-image-2 prompt composition + brand-native element library), frontend, Three.js/immersive 3D, WP/WooCommerce theming, accessibility, layout. | 37 | 5 |
| **`skyyrose-core`** | FastAPI/Python backend, Postgres/Redis, Alembic migrations, Docker, API design, behavior/token discipline, planning, memory & self-healing. | 23 | 8 |
| **`skyyrose-qa`** | TDD, drive-to-green, verification loops, audits, evals, regression testing, code review. | 16 | 5 |

Routing and handoffs between plugins are documented in [`CROSS-PLUGIN.md`](./CROSS-PLUGIN.md).

## Install (local marketplace)

```bash
/plugin marketplace add /Users/theceo/DevSkyy/skyyrose-suite
/plugin install skyyrose@skyyrose-suite
/plugin install skyyrose-market@skyyrose-suite
/plugin install skyyrose-design@skyyrose-suite
/plugin install skyyrose-core@skyyrose-suite
/plugin install skyyrose-qa@skyyrose-suite
```

Skills load under each plugin's namespace (`skyyrose-market:*`, `skyyrose-design:*`, …) and agents register as `subagent_type`s. Start any task with `/skyyrose <task>`.

## Wiring

- [`CROSS-PLUGIN.md`](./CROSS-PLUGIN.md) — handoff graph (market → design → qa → core → qa), namespace table, when-to-call-which.
- [`WIRING.md`](./WIRING.md) — how the marketing/design agent personas map to the Python runtime SuperAgents (`SkyyRoseContentAgent`, `MarketingAgent`, `SkyyRoseImageryAgent`, `agents/core/orchestrator.py`), the Elite Studio imagery pipelines, and the dev-team workflow lane.

## Guardrails

Every agent carries the always-on operating discipline (`skyyrose-core:token-aware-behavior` + `skyyrose-core:efficient-production`). Paid-media spend, Klaviyo sends, WooCommerce writes, media uploads, and paid renders (gpt-image-2) are all **STOP-AND-SHOW** — agents propose and wait for explicit founder approval before any money or production action. Product facts resolve through the catalog CSV + per-SKU dossiers only; brand canon (collections, palettes, The Five) is locked.
