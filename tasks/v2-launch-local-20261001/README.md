# Stream 1 local V2 launch candidate

The owned implementation is committed and reviewable. Overall launch qualification remains **BLOCKED**. Local checks, public staging reads and an authenticated read-only runtime inventory are separate evidence layers; none grants deployment, product-image approval, payment/order execution or release authority.

## Identity and scope

- Checkout: `/Users/theceo/.codex/worktrees/58b5/DevSkyy`
- Branch: `codex/v2-launch-local-20261001`
- Frozen base: `7892b797d838e67e62c862a6698a5b42b6dccaee`
- Comprehensive tested source: `5b1715df3949b2ff52725cc57a1f6c8064adef4b`
- Final source candidate: `524d6cd91f0ad9f16dcece58c7b7b709fcad6700`
- Registry: `wordpress-theme/skyyrose-flagship/data/logo-registry.json`, also exposed by the root symlink; all complete product reads use `get_product`.
- Canonical registry SHA-256: `db3181f70cc7ec021329365cfa24554f3d3af9feb87e6a014fb1d5b3514a4757`
- Source-certified package: **not produced**. Local theme version stays 2.5.0; inspected staging theme reports 2.5.1.
- Execution role evidence: parent `gpt-6.1-sol/high`, as confirmed by the coordinator; architect review `gpt-6-astra/high`, explicitly spawned for review only. Explore/Plan and worker configuration were inspected, but no worker was dispatched.

The final source differs from the comprehensive tested source only by sorting two standard-library imports in the FAQ builder. Ruff, Black and isort passed on all 17 changed Python files, and the three FAQ regressions passed at the final source SHA. [Follow-up evidence](evidence/final-source-followup.json) records the exact diff and commands. Theme and generated asset bytes are unchanged. The final handoff commit adds evidence and repository session notes after that source candidate; its diff must contain evidence/session notes only. The local check wrapper was available in the worktree during execution and is included here for reproducibility.

## Delivered behavior

1. Reconciled owned V2 slices from launch PR #983 with the newer base. The historical registry, source-certification contracts, preorder template owned by stream 2, and old task evidence were not substituted wholesale. PR #983 and FAQ PR #981 remain open/conflicting; this branch does not merge them. PR #993/#994 are already merged and their founder corrections are retained.
2. Migrated existing card bindings into the canonical registry. The migration validates canonical schema fragments under the existing writer lock, rejects conflicting bindings, writes compatibility projections before committing authority and rolls back written projections on failure. It retains scoped approval and current rejection metadata verbatim.
3. Reconciled homepage, jersey-gallery, PDP/media and asset-enqueue consumers. Product-card fallback and homepage editorial-film lookup respect current mismatch blocks. Source CSS/JS, committed minified outputs, critical CSS and translation output were rebuilt. The source-integrity gate remains enabled.
4. Represented the ratified absence of a global tagline explicitly in canonical brand YAML and its loader. Retired taglines cannot be reactivated silently. External PHP generation now reports/checks output outside the repository without crashing after writing it.
5. Corrected only BR-001/BR-002 catalog descriptions that contradicted their existing founder decoration specifications. These are agent-authored factual descriptions derived from existing specifications, not newly invented product facts or founder-authored wording. All other product facts, exact dimensions, authority and approval/rejection records remain unchanged. Regenerated catalog replicas, asset manifest and V2 presentation registry.
6. Reconciled the maintained, unpublished FAQ candidate from #981. Its 22 answers parse through the theme's native details branch; 57 quotes match refreshed public policy/canonical sources. Retired taglines, unsupported response-time promises, stale quotes and category-as-question errors are rejected. Historical September 26 decisions are labeled discovery context rather than current runtime attestation.
7. Fixed the local preview's explicit CSV escape argument for PHP 8.5 and made its homepage CSS/script inventory match the new enqueue order. The preview displays actual candidate identity, fails closed for unavailable fixture products and does not operate a WooCommerce database.

## Checks and limits

The final [local check ledger](evidence/local-checks.json) records **31 PASS / 2 FAIL across 33 checks**, all against `5b1715df3949b2ff52725cc57a1f6c8064adef4b`. Each entry includes the command, working directory, UTC time, expected behavior, status, tested SHA and log hash. Earlier intermediate runs are superseded by this final run.

- Focused Python product/registry/migration/brand/FAQ suites: 114 tests passed. Node runtime suites: 127 passed, zero skipped. Registry sync and asset-manifest drift checks passed.
- V2 asset, i18n, presentation-registry, token, card-rendition, font, frame, approved-scene and poster checks passed. PHP syntax and commerce/media, routes, cart/checkout truth, safety, SEO, global shell and critical-rendering contracts passed.
- `test-pdp-gallery.php` passed against the seven hash-pinned native WordPress/WooCommerce fixture files. Official source archives are WordPress 7.1 and WooCommerce 11.1.0; the test uses in-memory store adapters. Inspected staging runs 7.1.2/11.1.2. This does not establish live database, session, gateway or current hosted patch-version acceptance.
- **FAIL — broad brand enforcement:** 125 source hits in 83 files. [Findings](evidence/retired-tagline-findings.json) distinguish scanner observations from unestablished runtime use. Frontend, creative/provider, V1 and documentation consumers need ownership/scoped cleanup; this check was not disabled or weakened.
- **FAIL — full V2 build:** the pinned toolchain reaches the source-integrity check and rejects an unreconciled critical-home input hash. [Request for stream 4](evidence/source-certification-request.json) lists all nine changed existing input pins plus new runtime sources. Full verification/package certification remains blocked on that owner; approval states must not change as part of pin reconciliation.

## Staging evidence

[Runtime inventory](evidence/staging-runtime.json) was read through existing SSH BatchMode after `wp option get home` confirmed `https://staging-7e48-skyyrose.wpcomstaging.com`. Scope was theme PHP/CSS/JS/JSON hashes and public runtime versions/settings; no order/customer data or external mutation was involved.

Of 191 inspected theme files, 177 match this local candidate, 148 match the frozen base, 180 match the launch PR head and 11 match none of these refs. Counts overlap. [Per-file mapping](evidence/staging-source-mapping.json) does not infer a single deployed commit and does not cover fonts, images, video, GLB or plugin source parity. The remaining unmatched files need provenance/reconciliation.

All 18 [public route reads](evidence/public-route-inventory.json) returned HTTP 200. HTML routes retained `noindex, nofollow`, and response headers retained `noindex, nofollow, noarchive`, despite `blog_public=1`. This records staging protections; it is not production indexing acceptance.

The BR-001 staging PDP has no published product views, displays imagery-unavailable fallback and still includes the older embroidery description. The local description correction has not been applied to live WooCommerce. BR-001, BR-004 and BR-007 current card bindings remain `BLOCKED_PRODUCT_MISMATCH`.

Local homepage screenshots are [desktop](evidence/local-home-desktop.jpg) and [mobile](evidence/local-home-mobile.jpg), captured at source `8225f8987d13` before the final presentation-registry hash-only rebuild. Visual source files are byte-identical at the final tested candidate. At 390 px, the loaded hero uses `object-fit: cover`, the heading remains visible and document width equals viewport width. The menu moves focus into navigation; Escape restores the closed trigger. These are bounded fixture observations. Screen-reader, contrast, cross-browser, current hosted CWV and founder visual acceptance remain unqualified. The older [Black Rose fixture](evidence/local-black-rose-mobile.jpg) is explicitly a prior screenshot, not the final candidate's runtime proof.

## Acceptance state

| Gate | State | Concrete remaining work / owner |
| --- | --- | --- |
| LOCAL CODE COMPLETE | BLOCKED overall; owned source prepared | Stream 4 exact-source certification and package boundary; scoped broad-brand cleanup; stream 2 checkout compatibility artifact and the single V2 bootstrap include |
| MERGED | NOT RUN | No push, PR creation, merge or CI/workflow edit performed; CI facts are not inferred from branch protection metadata |
| RUNTIME ACCEPTED | BLOCKED | Reconcile deployed provenance, sync corrected product copy within authorized runtime work, complete product imagery/visual acceptance, current WordPress/WooCommerce E2E and transactional/operational qualification |
| RELEASED | NOT RUN | No deployment/publishing/provider-spend/release authority exercised |

The checkout dependency is intentionally explicit: stream 2 owns `inc/woocommerce-compat.php`; stream 1 owns adding its single V2 `functions.php` include after receiving the reviewed artifact/SHA. An absent dependency is not treated as an implemented include. Paid generation, real payment/order mutations and deployment remain outside this run's authorization.

## Reproduction and rollback

Run `python` from this checkout's `.venv`; it is Python 3.13.12 for the focused tests. Full V2 commands require Python 3.12.12/Pillow 12.3.0 and Node 22.23.2/npm 10.9.8. The exact installed local paths and fixture path are declared in [run_local_checks.py](run_local_checks.py). These `/tmp` dependencies are session-local, not committed distributable dependencies.

```sh
.venv/bin/python tasks/v2-launch-local-20261001/run_local_checks.py
```

The wrapper runs all independent local checks even after a failure and returns nonzero while either gate remains failed. It performs no provider, deployment, order/payment, push or merge operation. For the native gallery fixture alone:

```sh
V2_WP_FIXTURE=/tmp/stream1-native-downloads/wordpress php tools/v2-runtime/test-pdp-gallery.php
```

No rollback has been executed. In an authorized integration checkout, review the commit sequence and revert scoped commits newest-first if rollback is required; do not reset or discard unrelated work. The original frozen base remains available. Full deployment rollback and cache invalidation need their own runtime authority.

Repository session notes were added to `.wolf/memory.md` and `.wolf/anatomy.md`; persistent cross-session Codex memory was not changed. The existing buglog serializer refused its legacy format; the unrelated ledger was left untouched rather than normalized as part of this task.
