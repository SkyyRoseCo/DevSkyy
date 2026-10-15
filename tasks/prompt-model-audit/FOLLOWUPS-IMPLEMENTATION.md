# Product-truth follow-ups 1–4

All four scoped follow-ups are implemented on `codex/product-truth-readiness`,
starting at `6eb755e54f63b42406ac3a9680af2cc5603583c2` in the existing 58cc
worktree. The user subsequently authorized completing the follow-ups, tracking
and committing their changes, and merging if green. This report records the
implementation and local evidence; GitHub PR state is the merge authority.

## Central reporting and readiness

See [READINESS-IMPLEMENTATION.md](READINESS-IMPLEMENTATION.md) for follow-up 1.
Legacy gap names/order remain, with additive garment/view gaps and categories.
Render, SEO and alt-text requirements are explicit and independent of creative
intent. Optional editorial omissions do not indiscriminately block rendering.

## Exact vision references

`core.product.render_reference` consumes a complete product snapshot and
resolves only its explicit front/back binding. It rejects absent bindings,
invalid views, paths escaping the repository, missing files and empty files. The
returned record names the SKU, view, registry binding, path, byte digest and
provenance. No filename guessing or front-for-back fallback remains in the
legacy vision resolver. The compatibility `_reference_path(sku)` call explicitly
defaults to front; graph callers supply a view.

Vision analysis and reference preflight validate before any ADK or judge
dispatch. A supplied reference must match the bound path. Successful results
carry reference evidence. The preflight/3D graph nodes also resolve through this
contract and reject mismatched state overrides. Existing public result fields
remain intact.

## Complete-product consumers

- The complete entry point now exposes exact dossier `full_text` and a
  `catalog_row` compatibility projection alongside its existing structured data.
- Canonical OAI dossier reads resolve through `get_product`. Founder-authored
  registry prose bypasses composition-line deletion and truncation. Explicit
  external fixture paths retain the prior sanitizer contract. Corrections remain
  verbatim, with FOUNDER_CONFIRMED/FOUNDER_VERBATIM separate from AGENT_ADDED;
  unknown SKU or absent dossier fails closed.
- Lookbook facts resolve through `get_product`. Its existing four-value resolver
  contract remains; the prompt receives dossier, corrections, bindings and
  provenance. Reference infrastructure remains registry-backed.
- ThreeDAgent reads the complete record and validates its supplied techflat
  against the front binding before dispatch. Corrections/provenance reach the
  synthesis dossier, corrections reach the serialized base-stage prompt, and
  results carry reference evidence. The existing temporary undecorated-base
  stage and later decoration stage retain their roles.
- SkyyRoseCatalogSource preserves its legacy row/dossier fields and adds the
  full product record. Separately managed golden evaluation fixtures retain
  their existing lookup contract; they are not promoted to product authority.

## Authority terminology and CI

Catalog/config/utils documentation now distinguishes editable registry authority
from CSV compatibility projections and path-parity checks. Existing projection
content checks remain. Catalog CI includes readiness tests and explicitly
installs PyYAML for prompt-library imports; stale projections still fail the
existing `sync_product_registry.py --check` step. New test paths trigger catalog
CI.

Root `logo-registry.json` resolves to the single editable registry in this
checkout, schema v2 with 33 products and 43 correction records. No product data,
projection, asset, or founder fact was changed. Corey is founder/maker
authority; exact words, dimensions, ranges, artwork, placements and provenance
are preserved. No independent proof of his product facts was requested.

The required
[imagery prompting standard](/Users/theceo/.codex/creative-standards/imagery-prompting.md)
was read before prompt review. Natural integration and protected garment detail
remain required; these changes do not approve new scenes or resume generation.
Unsupported controls remain not applicable without a selected provider.

## Verification and limits

Run `bash tasks/prompt-model-audit/verify.sh`. The expanded script exercises the
new readiness and consumer contracts plus existing provider, prompt, visual-QA,
3D, platform and graph tests. See
[followups-verification.txt](followups-verification.txt) for the final
successful local run. Additional registry/plan-failure/catalog checks passed (80
tests), including stale-export failures. Changed Python Ruff, Black and isort
checks and the diff whitespace check passed.

The acceptance fixtures independently omit fit, front reference, SEO copy and
alt text. Consumer tests demonstrate no view substitution/filename guessing, no
dispatch on absent binding, founder-prose preservation, current reference
propagation into mocked request arguments, unknown-SKU/missing-dossier failure,
and unchanged source records. 3D tests inspect the delivered synthesis dossier
and serialized base prompt. All tests use fixtures/mocks; authentication is not
applicable. No live provider, generation, deployment or credential setup
occurred.

The configured `.husky/_` launcher is absent. Checks were run explicitly; no
hook execution is claimed. Whole-repository tests and whole-project mypy were
not run. Data readiness and byte hashes do not prove visual fidelity or
approval. Existing visual QA and authorization gates remain necessary. Full
per-image alt-text coverage, size-chart completeness, broader consumer migration
and provider redesign are outside these four follow-ups.

## CI integration repairs

The first PR run caught registered Kids joggers component IDs being treated as
sale SKUs by the stricter correction reader. Pair planning now carries the
registry-declared parent SKU for correction lookup, while retaining component
source images/placements. Unknown unregistered products still fail. The full
logo-registry suite (including both real Kids pairs) is now in the bounded
verification script; the targeted regression run passed 123 tests.

V2 source certification pins `core/product.py`. Its pin was reconciled only
after `build-product-presentation-registry.py --check` confirmed all 33
generated records are unchanged and all four source-input reconciliation tests
passed. No product/media receipt or generated output was changed.

CI uses isort 9.0.2 while the project environment had 7.0.0; the unaffected
model import layout was restored to the CI-compatible upstream form. The
production npm audit also found high-severity `fast-uri` advisories in the
existing lockfile. A lockfile-only targeted update changed its three entries
(3.1.6 to 3.1.8 and two 4.1.3 to 4.2.1), preserving requested dependency ranges.
The production high- severity audit passed afterward; seven moderate findings
remain. The shared node_modules symlink was not modified by this lockfile-only
operation; hosted CI performs a fresh installation of the updated lockfile.
