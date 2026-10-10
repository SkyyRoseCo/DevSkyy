# Product-truth follow-up 1 — central gaps and brief readiness

Implemented locally in `/Users/theceo/.codex/worktrees/58cc/DevSkyy` on
`codex/product-truth-readiness`, created from the clean exact parent
`6eb755e54f63b42406ac3a9680af2cc5603583c2`. This report records the initial
local delivery. The user subsequently authorized completing, committing and
merging all follow-ups if green; see
[FOLLOWUPS-IMPLEMENTATION.md](FOLLOWUPS-IMPLEMENTATION.md).

## Behavior

`get_product` retains existing flat gap names and their order, appending missing
`garment.color`, `garment.fit`, `garment.materials`, `garment.features` and
`render_sources.front/back` bindings. Whitespace-only specifications and empty
alt-text values count as missing. Additive `gap_categories` groups omissions by
section; `gap_report` and the CLI inherit the expanded report.

`product_readiness(record, operation, required_views=...)` consumes the complete
`get_product` snapshot. It reports required fields/views, all gaps, blocking
gaps, optional gaps and readiness. Explicit contracts:

- `render` (default): color, fit, materials, features; at least one explicit
  front/back view, with every requested render-source binding present.
- `seo`: existing `content.seo_meta`.
- `alt-text`: at least one nonblank existing alt-text value. This does not claim
  complete alt-text coverage for every image.

SEO/alt-text readiness measures existing deliverable completeness, not ability
to start drafting. Unknown operations/views raise. Unknown SKUs still raise
through `get_product`; an absent required view produces incomplete readiness.
Storefront fallbacks and supplemental references cannot supply missing views.

PromptChain and PromptEnhancer accept explicit `operation` independently of
creative intent. `gaps` remains comprehensive; `blocking_gaps` and
`optional_gaps` are additive. A brief is `grounded` when the selected operation
has no blockers, even if optional enrichment remains absent. Missing SKU always
blocks. Product briefs still bypass semantic caching; serialized briefs include
per-SKU readiness.

## Authority and preservation

Read and applied the required
[imagery prompting standard](/Users/theceo/.codex/creative-standards/imagery-prompting.md).
Briefs retain its citation, natural integration/fidelity rules and unsupported
provider-control declarations. The generation hold remains in effect.

The root registry symlink resolves to
`wordpress-theme/skyyrose-flagship/data/logo-registry.json` in this checkout.
Verified schema v2, 33 products, 43 correction records and SHA-256 prefix
`4bd403a92525048d`, matching the parent scope report. No registry, projection or
asset writes were made. Corey remains founder/maker authority; exact supplied
wording, dimensions, ranges, artwork, placements, nulls and correction
provenance are preserved. Tests check our execution, not independent proof of
maker facts.

## Reproduced verification

[readiness-verification.txt](readiness-verification.txt) records a successful
`bash tasks/prompt-model-audit/verify.sh` run:

- 300 Python product/prompt/provider/QA contract tests.
- 34 web-builder provider/runtime tests.
- 27 TypeScript service/SDK compatibility tests.
- Root TypeScript type-check, changed TypeScript ESLint/Prettier.
- Registry sync `--check`: CSV and every product dossier match the registry.
- `git diff --check`.

Additionally, 59 focused product/readiness/prompt tests passed, and Ruff, Black
and isort passed on the three changed Python modules and new test module. The
verification script now includes readiness and product-entry tests.

`tests/test_product_readiness.py` independently omits fit, front reference, SEO
copy and alt text. Each is centrally discoverable and blocks only its operation.
Tests also cover optional back bindings, absent required views, unsupported
contracts, whitespace-only specifications, unknown SKU, null preservation and
exact garment/correction propagation through serialized briefs. Authentication
is not applicable: fixtures and mocked transports only. The existing guard
prevents real requests/httpx HTTP and allows explicit mocks.

`.husky/_` is configured but absent. No hook execution is claimed. The checks
above were run explicitly; whole-repository tests and whole-project mypy were
not run.

## Remaining scope and limits

Readiness validates data presence and explicit bindings; it does not establish
binary existence/readability, authenticity, judge accuracy or approval. Existing
asset and visual QA gates remain responsible for those checks. No missing
product fact was filled in. These rules cover the four explicitly named garment
fields; size-chart coverage and per-image alt-text completeness are not new
gates.

At this initial delivery, follow-ups 2–4 were unimplemented: legacy vision
filename guessing, selective complete-product consumer migrations, and remaining
authority terminology and validation cleanup. No paid API, generation, live
evaluation, deployment, publishing, purchases, credentials or main-branch merge
occurred.
