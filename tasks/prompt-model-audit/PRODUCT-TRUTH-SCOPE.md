# Independent product-truth scope

Reviewed 2026-09-28 by the delegated `product_truth_scope` agent against
`/Users/theceo/.codex/worktrees/58cc/DevSkyy`, now committed as `d1f804028`.
Read-only source/data inspection found no product-fact blocker in the current
prompt/model changes. This is not certification of every consumer or a live run.

The agent read AGENTS.md, SOT.md and the required
[imagery prompting standard](/Users/theceo/.codex/creative-standards/imagery-prompting.md).
Authentication and provider controls were not applicable to this offline scope.
No product facts, bindings or assets were changed.

## Authority and checkout freshness

Root `logo-registry.json` resolves to
`wordpress-theme/skyyrose-flagship/data/logo-registry.json`, the single editable
product authority. CSVs/dossiers are projections. Use `get_product` for complete
records. Corey is the founder/maker; preserve exact wording, dimensions, ranges,
artwork and placements. Direct new confirmations are `FOUNDER_CONFIRMED`;
preserve existing `FOUNDER_VERBATIM` and `AGENT_ADDED` provenance rather than
relabeling it. Checking our output does not require independent proof of the
maker's facts.

| Observed checkout            | Schema | Products | Unified correction records             | Registry SHA-256 prefix |
| ---------------------------- | ------ | -------- | -------------------------------------- | ----------------------- |
| Reviewed worktree            | 2      | 33       | 43: 34 FOUNDER_VERBATIM, 9 AGENT_ADDED | 4bd403a92525048d        |
| Main `/Users/theceo/DevSkyy` | 1      | 33       | 0                                      | c27f1a3809208542        |

Do not replace the reviewed registry with the older main-checkout copy. This
comparison establishes current local schema/correction coverage, not exhaustive
freshness against founder statements outside this task. Projection validation
passed: `CSV and all product dossiers match the registry`.

## Current implementation evidence

- `skyyrose/core/product.py:240,256,271`: unified record includes corrections,
  logos, authority, sources and provenance.
- `skyyrose/elite_studio/prompts/chain.py:161,183,210`: grounded constraints,
  missing requirements and founder/agent provenance separation.
- `skyyrose/elite_studio/prompts/enhancer.py:137`: grounded briefs bypass
  semantic cache.
- `skyyrose/elite_studio/agents/quality_agent.py:74,124,183`: exact SKU/view
  binding, path/binary validation, paired images, hashes and registry
  provenance.

## Follow-up scope

### 1. Central gaps and task-specific readiness

`skyyrose/core/product.py:290` combines image, content and merchandising gaps
but omits missing garment specifications and render-source views. The new brief
compensates locally in `prompts/chain.py:183–194`.

Observed: 25 records lack fit specifications; 16 front/back bindings are absent
across 15 SKUs. Every nonempty front/back binding resolves to a file. All 33
products also lack six editorial/enrichment fields, so aggregate `incomplete`
status includes non-rendering gaps. Do not turn it into an indiscriminate gate.

Scope: additive central gap categories or a readiness helper, then task-specific
brief readiness. Preserve nulls; never infer missing product facts.

Acceptance: independently remove fit, front reference, SEO copy and alt text in
fixtures. All absences appear centrally; only relevant requirements block the
selected operation. Unknown SKU/missing required view remain fail-closed.

### 2. Replace legacy vision filename guessing

`skyyrose/elite_studio/agents/vision_agent.py:39–66` checks catalog sources,
then guesses SKU filenames and eventually returns a presumed JPG path. This is
pre-existing behavior outside the committed changes.

Scope: explicit SKU/view registry binding through `get_product`, with direct
caller/test migration. Acceptance: similarly named unrelated files cannot be
selected; back cannot use front; absent bindings stop before dispatch;
provenance identifies the exact binding.

### 3. Migrate complete-product consumers selectively

Candidate consumers: `scripts/oai_render/lookbook.py:48,136`,
`scripts/oai_render/prompt.py:15–17`,
`skyyrose/elite_studio/agents/three_d_agent.py:99–105`, and
`skyyrose/elite_studio/platform/catalog_source.py:46–48`.

Narrow readers are not automatically competing sources:
`skyyrose/core/catalog_loader.py:73–85` delegates to the registry-backed dossier
layer. Inspect completeness/corrections/provenance before changing each
consumer. `prompt.py:62–68` drops composition-matching lines; regression tests
must prove protected founder wording survives.

Scope: one consumer at a time, preserving public contracts and founder text.
Acceptance: fixture corrections and changed references reach serialized
requests; unknown SKU/missing dossier fail; no stale file/CSV fallback; no
provider calls.

### 4. Update remaining authority terminology and validation

`skyyrose/elite_studio/config.py:253–263`, `catalog.py:1` and `utils.py:123`
retain older CSV terminology. Describe projections accurately and distinguish
path parity from registry authority. Keep useful compatibility checks. Existing
CI runs drift checks at `.github/workflows/catalog-validate.yml:128` and product
entry tests at line 147.

Acceptance: consistent single-registry documentation, stale projections fail CI,
and registry corrections reach consumers without a parallel product record. The
new Elite Studio README and implementation report document current contracts;
this follow-up includes the remaining legacy comments/checks.

## Binding gaps, not claims of missing artwork

Back bindings are absent for `br-004`, `br-005`, `lh-002`, `lh-005`, `lh-006`,
`sg-001`, `sg-002`, `sg-003`, `sg-005`, `sg-006`, `sg-007`, `sg-009`, `sg-011`,
`sg-012`. Both front and back are absent for `sg-015`.

Repair only from approved sources and current founder statements. Follow the
applicable dossier/registry write contract and regenerate projections. Do not
invent measurements, demand reconfirmation of supplied facts, or author a new
parallel product-truth manifest. These follow-ups are scoped, not implemented.
