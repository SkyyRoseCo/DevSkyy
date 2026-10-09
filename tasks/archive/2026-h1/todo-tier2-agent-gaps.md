# Tier-2 Agent Gaps — Net-New Build (ticket #17660)

Verified state: `project_agent_gaps_verified_2026_06_20`. ROI order, founder-directed.
Architecture: deterministic AI-free core (`services/`), advisory/read-only, fail-closed,
never-raises, founder-tunable thresholds. Mirrors `monitoring/fleet_observer.py`. Any LLM/
embedding sits behind a narrow injected port; the no-LLM path ships by default. NO live
WC/Klaviyo writes (advisory payloads only).

## Gap 4 — Fraud / Chargeback risk (ABSENT → BUILT ✅)
- [x] `services/risk/fraud.py` — `FraudScorer` (11 weighted signals → score/level/action)
- [x] `tests/services/test_fraud_risk.py` — 53 tests
- [x] MCP `devskyy_fraud_assess`
- [x] Adversarial review (16 confirmed → all 15 actionable fixed; 1 accepted) — bug-150

## Gap 5 — Customer Lifecycle / Retention (fragmented → UNIFIED ✅)
- [x] `services/lifecycle/retention.py` — RFM + lifecycle-stage + churn-risk scorer
- [x] `tests/services/test_retention.py` — 34 tests
- [x] MCP `devskyy_retention_assess`; wired `analytics_agent.segment_customers` RFM fallback
- [x] Review fixed: LOYAL reachable through inter-drop window; churn=0 when no purchases; datetime parse

## Gap 3 — Drop / Demand Forecasting (stub → REAL ✅)
- [x] `services/forecasting/demand.py` — velocity/trend/sellout forecaster
- [x] `tests/services/test_demand_forecast.py` — 31 tests
- [x] Wired `analytics_agent.forecast_sales` → deterministic fallback (no more "not available")
- [x] MCP `devskyy_demand_forecast`; `tests/agents/test_analytics_forecast_wiring.py` — 8 tests
- [x] Review fixed: pre-order suppresses CRITICAL; today excluded from velocity; 30d projection fixed

## Gap 6 — Personalization / Recommendation (ABSENT → BUILT ✅)
- [x] `services/personalization/recommender.py` — per-user reranker (content + co-purchase
      + popularity cold-start; optional `SimilarityBackend` port for Pinecone)
- [x] `tests/services/test_recommender.py` — 28 tests
- [x] MCP `devskyy_recommend`
- [x] Review fixed: popularity log-scaled (no swamp); price=0 not dropped; similarity_k fanout

## Status — COMPLETE
148 new tests green · 228 core-agents regression green · ruff/black/mypy clean on all new code ·
4 new MCP tools registered (56 total, count now dynamic) · NOT committed (matches Tier-1).
Two adversarial reviews run: fraud (16 findings → bug-150), Tier-2 trio (43 findings → bug-151).
Founder decides commit. Deferred-by-design (founder-tunable, accepted): churn/stage as
complementary signals; co-purchase raw count; `.name` enum serialization; ML/Pinecone upgrades
behind the injected ports.
