# Hardened creative job workflow

`PromptEnhancer.build_creative_brief(request, plan)` integrates the resolver with one existing creative-brief consumer. Existing `enhance()` callers retain previous behavior. No broad consumer migration, provider generation or publication occurs.

```python
result = enhancer.build_creative_brief(request, plan, mode="resolved")
execution = result["execution_bundle"]
# Full raw evidence is deliberately opt-in:
review = enhancer.build_creative_brief(request, plan, mode="shadow", include_audit=True)
audit = review["audit_bundle"]
```

- `resolved`: compact execution brief and contract identity/status; no legacy injection.
- `shadow`: same execution brief plus explicitly unverified legacy comparison.
- `legacy`: explicit rollback, no job contract or resolver guarantees. Never use it to claim a blocked resolver job passed.

The default brief contains safe resolved product facts, not raw marketing snapshots or every paragraph of constitutional prose. Rule IDs and inclusion reasons link to the hashed Constitution; the audit bundle records reasons for exclusions too. `render_brief(job, debug=True)` returns the full audit view explicitly.

## Plan and leverage

`JobPlan` binds deliverables, experience outcome, authored meaning, production method and sources, feasibility evidence, success/channel/approval requirements, novelty, accessibility and commerce applicability, open issues, saturation evidence and optional derivative coverage. Source-composite and photography plans require every requested canonical view. Film, photoshoot, product-scan and other declared high-cost sources require derivative coverage planning before production readiness; coverage plans name intended applications and different adaptation purposes, not one crop applied everywhere.

Saturation without evidence is UNKNOWN_NOT_REVIEWED; no fabricated recent-work classifications are emitted. Major production needs evidence of recent-work review. A/B/n is required for major initiatives when practical; an exception requires a reason. Similarity is never a brand pass/fail gate. Local discovery exposes relevant Bay Area territory without selecting a mandatory landmark.

`production_path_ready` means required planning inputs/documentation are available, not that the technique has passed final visual review or received execution permission. Conflicting request and plan values are blockers, not last-write-wins. Job identity binds resolved context, plan, blockers and implementation content.

## Lifecycle and verification

M2 can become PLANNING_READY with an explicitly absent campaign brief. M5–M7 campaign authority must resolve. M6 artifact evidence can yield RELEASE_CANDIDATE; M2 evidence cannot silently promote itself. All action-authority fields remain false.

`VerificationRecord` binds gate, contract, artifact hash, applicability, result, reviewer, method, timestamp, observations, criteria and evidence hashes. `assess_artifact()` re-resolves fresh sources, rejects stale/changed contracts and artifacts, and requires every applicable gate. Missing, failed, blocked, contradictory or duplicate records prevent readiness.

Intent adds mandatory evidence criteria: product cards need readability/crop resilience/consistency, details need visual/material/construction truth, editorial needs creative direction/composition/narrative/novelty, films need story/camera/sound/continuity/master/derivative planning, and interactive experiences need discovery/recoverable control/accessibility/fallback/performance/commerce. Plan booleans cannot disable intent-required accessibility or commerce gates. Product Fidelity retains the complete constitutional checklist, including dimensions.

This is evidence-ledger validation, not pixel inspection, reviewer authentication or legal-rights verification. A PASS record must come from a trusted reviewer or future verifier integration. Hashes bind exact bytes; they do not prove the report's conclusions. Release readiness is distinct from publication, deployment and spending authority.

## Reproducible examples

The candidate includes `docs/examples/context-resolver-abstract.json`, exercised in compact and audit modes by the focused tests. `tests/test_creative_job.py` exercises the brief consumer and evidence gates using temporary, hash-bound test artifacts.

For br-001 the clean registry resolves embossed front treatment and desired preorder false. Present embroidery copy is superseded; retired preorder copy is tested with a provenance-pinned historical fixture. Historical dirty-checkout pilot artifacts are not included or used as clean-candidate evidence.

The next implementation boundary remains actual verifier integrations, authenticated approval handling and appropriately scoped channel/live-commerce adapters. The full Creative OS, Ads OS and campaign automation are not part of this hardening.
