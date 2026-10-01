---
applyTo: 'skyyrose/elite_studio/creative/**/*.py,skyyrose/core/context_resolver.py,skyyrose/core/creative_job.py,api/v1/analytics/**/*.py,alembic/storefront_migrations/**/*.py,alembic-analytics.ini,tests/test_context_resolver.py,tests/test_creative_job.py,tests/test_creative_reporting.py,tests/test_local_composite.py,tests/test_spend_ledger.py,tests/api/analytics/**/*.py'
---

# Creative OS and analytics review guidance

- Treat brand constitution bytes and product records as separate authorities.
  Context resolution must check the declared artifact hashes and owner-ratified
  records; do not promote proposals or stale material into ratified rules.
  Existing product facts come from `get_product(sku)` and the canonical product
  registry; preserve Corey's latest direct corrections.
- Trace asset and approval claims to their bound source, hash, scope, and
  provenance. A local composite can verify bounded pixel preservation; it does
  not prove garment identity, design correctness, or owner approval. Synthetic
  fixture receipts are not real approvals or provider receipts.
- Treat the spend ledger and Governor as authorization boundaries. Check that
  recovery, retries, limits, and unknown provider outcomes fail closed and do
  not silently authorize another paid operation. Reports and receipt readers
  must be read-only, verify signatures/hashes and scope, and distinguish
  synthetic, simulated, historical, and authenticated live evidence.
- Analytics writes must be scoped, validated, idempotent, and atomic. Check
  event identity conflicts, persistence across processes, user/key
  compatibility, and explicit migration targeting. Reporting must exclude
  synthetic events, honor consent scope, and label unavailable or unverified
  purchase, revenue, attribution, spend, and ROAS metrics accurately.
- Useful focused evidence lives in `tests/test_context_resolver.py`,
  `tests/test_creative_job.py`, `tests/test_local_composite.py`,
  `tests/test_spend_ledger.py`, `tests/test_creative_reporting.py`, and
  `tests/api/analytics/`. Inspect the owning fixtures and assertions before
  claiming behavior. Passing synthetic tests does not qualify live providers,
  production ingestion, or deployment.
