# Current production status and release boundaries

**Last updated:** 2026-10-01. **Evidence snapshot:** 2026-10-01 16:48:48 UTC,
recorded from actual operation receipts and the latest coordinator update.
**Operational source:** `a662e707d698a687d7d1d2efed3975b9aa7325b9`.

This is a dated operator snapshot of the integrated release. It supplements the
retained task records; it does not change their historical states or authorize
execution. Refresh the snapshot from the release coordinator's actual receipts
before using it for a new operation. The documentation commit is separate from
the frozen operational source and does not rebuild the approved package.

## What is established

| Gate or surface                 | Observed result                                                                                                                                                       | Evidence limit                                                                                                                                                                                |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Five workstreams                | Scoped source adopted and integrated                                                                                                                                  | The adoption manifest includes open inventory, asset/device, policy, and Governor runtime holds                                                                                               |
| Functional source               | Frozen at `299f694702ac2dcc61a0f30aa34e4b3ef12f9118`                                                                                                                  | Local tests are bounded integration evidence                                                                                                                                                  |
| Clean V2 package                | Source `5950592d922706dd67fc0320e8c5f3dc005a47b7`; repeat bytes and installed-file checks passed                                                                      | Packaging does not establish live production behavior                                                                                                                                         |
| Existing staging                | V2 2.5.0 installed; all 599 reviewed file hashes matched                                                                                                              | Staging has 220 product/variation records; it cannot establish parity with production's 33 simple products                                                                                    |
| Production                      | `https://skyyrose.co`, active V1 `skyyrose-flagship`; exact inactive V2 installation and V1 preservation independently verified                                       | All 599 installed V2 hashes matched. Ten owned pages remain drafts; Search MU installed and actual hosting caches cleared. No V2 activation or `DEPLOYED`                                     |
| Procedure and acceptance inputs | Initial source/freeze review and 30 offline tests passed; query-correction source/procedure/39-file freeze reviewed with 34 focused tests and Ruff/Black/mypy passing | These are offline/localhost and source-review receipts. Observer/finalization correction, review/refreeze, and tests remain pending                                                           |
| Exact operational-head CI       | `CI_PASS`: 21 mandatory successful checks, 6 intentional skips, no pending/failure/cancellation                                                                       | Single targeted Playwright retry: 62 passed (31 Chromium, 31 mobile), 0 failed/skipped/flaky; source CI is separate from production acceptance                                                |
| Execution clearance             | Initial combined clearance and precondition hold release retained; query-corrected V1 checkpoint-only resume issued after independent review                          | Immediate guards still apply. The corrected run has unresolved instrumentation health; all next production writes remain held                                                                 |
| V1 Search checkpoint            | Corrected desktop/mobile functional journeys completed and printed PASS; process exited 0                                                                             | Three `TargetClosedError` occurrences in full stderr leave capture completeness UNKNOWN. Printed PASS is not accepted V1 checkpoint PASS; observer correction and full reviewed rerun pending |
| Production V2 acceptance        | Not executed                                                                                                                                                          | No V2 activation, `DEPLOYED`, or `PRODUCTION_ACCEPTED`; complete accepted V1 Search/privacy capture, activation, and six-profile V2 acceptance remain required                                |

The cancelled Playwright job is `110435542010` in CI run `36880002499` on exact
`a662e707…`. Its preserved complete log records about 16 minutes in checkout, 3
minutes in Python dependencies, 28 seconds in frontend npm installation, and 10
minutes 38 seconds in browser OS dependencies with slow APT mirror retries. No
Playwright tests started in that attempt.

Astra recorded `ONE_BOUNDED_TARGETED_RETRY_REVIEW_PASS` after the complete log
review. Integration dispatched exactly one targeted retry on the same frozen
head and workflow run. Successor job `110451737866`, run attempt 2, started at
15:45:10 UTC and completed successfully at 15:59:04 UTC. The actual Playwright
test step ran from 15:56:46 to 15:58:50 UTC: **62 passed** (31 Chromium and 31
mobile), with **0 failed, skipped, or flaky tests**.

The final authenticated Code Review receipt records **21 mandatory SUCCESS / 6
intentional SKIP**, with no pending, failed, cancelled, or unexpected skipped
checks. The original 20 SUCCESS / 6 intentional SKIP / 1 CANCELLED attempt and
its full log remain preserved. GitHub inherited the earlier successful same-head
upstream results for attempt 2; this does not claim every upstream suite ran
again. No workflow, source, dependencies, browser selection, timeout, or test
changes were made, and no fetch-depth contingency was needed.

GitHub's actual tested checkout was merge commit
`30fdd5940fb7ce4951b8c95c63f2784dc930a3a6`, with parents `7892b797…` and
`a662e707…`. Authenticated tree readback establishes that its tree
`40cad1a67e8efa99ddc0843dbf6ceffb53f55e49` equals the frozen operational `a662`
tree. PR #1000 remains open, draft, and unmerged at the same head.

Astra issued `FINAL_COMBINED_CLEARANCE_PASS`, with architect PASS, after review
of the final CI receipt, combined 12 evidence bindings, adoption record, and
actual target identity. The coordinator's durable
`CLEAR_TO_EXECUTE_SCOPED_CUTOVER` receipt closes both the CI and
acceptance/procedure conditions and sends the sole writer the reviewed execution
signal within the existing human scope.

The receipt supplies **conditional scoped execution clearance**, not proof of
installation or live V2 acceptance. Immediate authenticated target, source,
artifact, option/page preimage, native configuration, and ownership guards
remain required before each mutation.

The inactive installation command returned exit 0 under the reviewed clearance.
Subsequent readback and independent review established all **599 exact installed
V2 files** and preservation of active V1, its file/option baseline, and native
products/prices. The coordinator released the initial
precondition-classification hold at **16:27:08 UTC**. The original intent,
attempt, and initially held readback remain immutable; the later hold-release
receipt supplies the reviewed outcome.

The sole writer prepared **ten owned draft pages, IDs 10427–10436**. Read-only
MU ownership and draft-page readbacks passed. The first MU command's ambiguous
CLI warning is retained without a retry; its precise cause remains **UNKNOWN**.
Fresh bootstrap checks were clean, and the later ownership/readback evidence
establishes the installed reviewed extension without rewriting that attempt.

At **16:33:58 UTC**, the authenticated hosting account `skyyroseco`, Production
`skyyrose.co`, separately confirmed **"Object cache cleared."** and **"Global
edge cache cleared."** Post-cache readback and the **16:34:25 UTC**
`MU_INSTALLED_CACHE_CLEARED` signal bind the installed MU, draft ownership,
cache clear, and still-active V1. These receipts establish installation and
cache clearing, not public runtime acceptance.

The frozen **`checkpoint-v1-live-20261001t1634`** failed in both desktop and
mobile profiles between **16:34:41 and 16:35:41 UTC**, each timing out after
**25 seconds** while awaiting a Search response. Its initial normal-home
observations found no tracking handles or owned visitor/session identifiers;
that narrow observation does not establish the complete privacy or Search gate.
The failed results, per-profile receipts, and evidence manifest are preserved.

The **16:37:50 UTC** read-only diagnostic verified a **test-query/matcher
encoding mismatch**: both `+` and `%20` query forms returned Search API HTTP
200, 27 total results and 10 result rows, with no JavaScript errors. The
observed response query encoding did not satisfy the original predicate; `%20`
navigation displayed the intended `Black Rose` input. The original failed run
remains preserved. Its timeout does not establish a production Search outage.

The bounded query correction passed **34 focused offline tests** and
Ruff/Black/mypy checks, with independent Python and Astra
source/procedure/freeze review. The coordinator issued
`RESUME_V1_SEARCH_CHECKPOINT_ONLY` at **16:46:38 UTC**, bound to the successor
**39-file freeze** and corrected procedure. That signal allowed only the actual
V1 desktop/mobile checkpoint; it did not clear V2 activation or publication. The
original 26-file freeze and first failed 14-file run remain unchanged.

The corrected **`checkpoint-v1-query-corrected-20261001t1647`** completed both
profiles from **16:47:11 to 16:47:23 UTC** and printed PASS with process exit 0.
Each intended-query Search journey returned HTTP 200, 27 total results and 10
rows, opened the returned native product and checked its native form, and
completed a no-results Search journey with HTTP 200 and zero results. Four
privacy observations per profile completed. These establish completed functional
journeys and recorded observations, not accepted privacy capture completeness.

The full attempt stderr contains **three `TargetClosedError` occurrences**; that
count does not prove three distinct lost requests. The request callback reads
`all_headers` before appending its record, and profile PASS/receipt
serialization occurs before context closure. Missing callback request
identities/timing leave capture completeness **UNKNOWN**. Empty frontend
JavaScript error arrays do not establish the observer's health or prove harmless
teardown. The **16:48:48 UTC** immutable instrumentation-hold receipt preserves
the process result and verifies the run's **22 evidence members** without
accepting V1 checkpoint PASS.

A bounded local observer/finalization correction has an independently reviewed
plan; its corrected source/procedure, independent review/refreeze, tests, and
full two-profile rerun remain pending. The timeout, privacy, product-click,
empty-result, and native-form gates must remain intact. This is an observation
completeness hold; it supplies no basis for claiming a production regression or
requiring MU rollback. No application, MU, theme package, or operational-head
change is part of the correction.

At this snapshot, **all next production writes are held**. V1 remains active;
the ten owned pages remain drafts. No V2 activation, `DEPLOYED`, or
`PRODUCTION_ACCEPTED` is established. Source CI and conditional execution
clearance remain separate valid receipts, but neither overrides unresolved
runtime observation completeness. Any changed or unknown precondition also stops
the next mutation for read-only reconciliation under the reviewed stop/recovery
rules. Never blindly retry an uncertain mutation or substitute diagnostic
results for required acceptance evidence.

The authenticated target snapshots report WordPress **7.1.2**, WooCommerce
**11.1.2**, and PHP **8.4.26** on production and existing staging. These are
captured versions, not a promise that hosting versions remain unchanged. Recheck
them with the site identity immediately before execution.

## Exact candidate identities

| Binding                                         | SHA-256 or revision                                                |
| ----------------------------------------------- | ------------------------------------------------------------------ |
| Operational source                              | `a662e707d698a687d7d1d2efed3975b9aa7325b9`                         |
| Functional source                               | `299f694702ac2dcc61a0f30aa34e4b3ef12f9118`                         |
| Clean package source                            | `5950592d922706dd67fc0320e8c5f3dc005a47b7`                         |
| V2 ZIP: 599 members, 176,928,301 bytes          | `47c485f0001434b7dd52f572812df02e3e103631902a16e86f92ffea407b5a16` |
| Separate Search privacy MU extension            | `afc2f6d8a4ae6280de28b6c1306564cc86053acc713c52e5ab0b5717b3ef58f2` |
| Ten-page plan                                   | `dc7ca358d530cc44aeea75771236573e48088cd7f99b545941b3b05cbbd7b44e` |
| Cutover candidate manifest                      | `7b52fb62b0c49e52785e2fc1be6cc2a3dd0d020407e128ead3dd8341ade7c1b3` |
| Initial acceptance freeze: 26 files             | `22b30db9d34eda875acbcc64a26a172bdd2d7e051cadcb4ce41a5c66e8d0b0d1` |
| Initial acceptance procedure                    | `8944f3fe7f461117ec57bec7fc852835c2110bcd534481afc797d33e56ca887e` |
| Initial V2 acceptance harness                   | `0573e738c95a18528bce4e3dd6631c5a5f2c78e9b9fcd2ee083e21ef6807497d` |
| Combined release evidence manifest: 12 bindings | `ef053fa175b69913469c33a259c91afb61eff811e004eff4e09457145e20e2a2` |
| Procedure/source review receipt                 | `cd7d6b16d322dd2ab7ecec19be9f2ff3fff72663aa5a4876be56b5a67647e2ff` |
| Final exact-head CI receipt                     | `23c467bf8dbde980ab3c22f95f84d324cbdf72acac3368bed37c031289d5eeb4` |
| Scoped pre-execution clearance receipt          | `4f90c881ea90674736aa8828e50a34f27f1c604903f9ac6b32d19803149ba286` |
| Inactive V2 installation intent                 | `db924ba569058bb1a2f961756229e919c521270d2c701f9a8ee03f0cdf94c9a6` |
| Inactive V2 command-attempt receipt             | `317bcbe7625e1a6c9a32dcf790167585f3a1802d82da5ca269b686ea3abc5f9a` |
| Inactive V2 installed-file readback             | `e7aa2feeee905f9ddcc861715d436a38c5a2b09ad9346ea8a268ff16e731d68d` |
| Initial precondition hold-release receipt       | `ae25567c5c50f1b1e6c1c1565a1083298fc273fa44c675305ea353d076ab3f2c` |
| MU installed ownership readback                 | `0cf5882765f84601b26654bdbfad25e4d6d682e6e3680378be8f390953eaa449` |
| Ten-draft readback and warning trace            | `39ef314f8a1aa0487dff7107826e297ca24597a0f79d60be681a94cb446afba0` |
| Authenticated hosting cache-clear receipt       | `b2f1ca21cd5dd89f3eaaa4f6d0c769a1c5e98241e4bbff429047974bb6480330` |
| Post-cache MU readback                          | `92b5f00ef60b281ef26a99dc3340b8a271182181fac84a43ce7e6c2011137bcb` |
| Installed MU/cache-cleared checkpoint signal    | `8ef3f92ae55f1890459fdf041741dda5a9b48db3ffcab9d61895a126fa7c2b76` |
| Failed desktop/mobile V1 checkpoint results     | `3fe1b7e41d47af56a36d2806ffb77910cd1bd19f2b90e5f5db12ffd0cfc7d632` |
| Failed V1 checkpoint evidence manifest          | `2268ca39ac746befa045d321f5442e3581a5f081c35a94f405d910c4a9cac1c2` |
| Read-only Search encoding diagnostic            | `5759ca5b0c911f4a457c7d3c4e43094481bfdc638f655667702d6f86ac1a8534` |
| Query-correction reviewed freeze: 39 files      | `1e721925eee5b09703e79d6044c58a3b68ad178514c4ba15891073a27d9fcaeb` |
| Query-correction reviewed procedure             | `ccac68f3acf2929d799add6e9fc9b32103fd0a5440cc680db13bd6fe8cb9a7b1` |
| Query-corrected V1 checkpoint-only resume       | `0c3c674257fa393f52f2c89a8658ae8c295aa8bcd8660ec03b729c3cfbd96e5c` |
| Query-corrected checkpoint full command attempt | `508b4b2c67acb7c651ea488cc21d3fee789a75df7941d296a57c7c383f32fe65` |
| Query-corrected printed profile results         | `a179db54b46d9c08ec2578227e4285f63b1287808916031aecc4f648dc0a0f13` |
| Query-corrected run evidence manifest: 22 files | `62559d1f25143f9342d497042493bc0ddca2a3b2a7d2d889505bd77e1c91f59f` |
| Query-corrected instrumentation-hold receipt    | `676635d31ad6980784a13f0a92564160c80bdbeb442b4a8626b4c31b69f3adab` |

The Search extension is a separate artifact; it does not change the V2 ZIP.
Recomputing hashes of changed files cannot approve a successor. Match the
literal reviewed bindings and invalidate clearance when the operational source
or any required source/artifact/receipt bytes change.

## Scoped storefront release

The current cutover preserves the **33 published simple products**, their native
WooCommerce IDs and prices, full-payment checkout, unmanaged quantities, and
existing null shipping-date promises. Registry edition sizes do not establish
remaining inventory balances. No conversion to variations, size allocation,
stock cap, reservation lifecycle, or fulfillment-date promise is part of this
release.

The allowed candidate consists of the reviewed V2 theme and existing approved
media, the separately reviewed Search privacy MU extension, and ten owned new
pages. Existing merchant pages, WooCommerce cart/checkout/shop/account IDs,
shortcodes, options, customer records, orders, and payment behavior are
preserved. No product type, size, inventory, price, order, payment, or customer
mutation is included. API, dashboard, Fly, Governor, paid providers/generation,
unaccepted GLBs, mascot activation, database synchronization/import, demo
import, deletion, and backup pruning are outside the cutover.

The single editable product authority remains
[logo-registry.json](../logo-registry.json), resolving to the original theme's
[unified product registry](../wordpress-theme/skyyrose-flagship/data/logo-registry.json).
Use [get_product](../skyyrose/core/product.py) for complete reads. Corey's
latest maker specifications remain `FOUNDER_CONFIRMED`; missing facts remain
gaps. Native production configuration snapshots bind the acceptance tests to
existing store records and do not become an alternative product source.

## Execution and acceptance order

The reviewed [runbook](RUNBOOK.md) preserves this order. Source clearance,
inactive installation, draft preparation, and MU/cache readback are recorded at
this snapshot. The V1 Search/privacy checkpoint must pass with complete
observation capture before activation; later runtime states still require actual
evidence:

1. `CI_PASS` and `CLEAR_TO_EXECUTE_SCOPED_CUTOVER` are recorded for exact
   `a662e707…`. The sole writer must refresh immediate target/preimage/ownership
   guards before each mutation; clearance does not override a failed or unknown
   guard.
2. Install exact V2 while inactive and prepare only the ten owned drafts.
   Install the Search privacy MU extension and record actual object/global edge
   cache clearing. With V1 still active, require actual desktop and mobile
   Search checkpoint evidence before activation.
3. Guard all ten captured activation-option preimages; use native WordPress core
   theme switching and next-bootstrap handling/readback. Publish only the ten
   owned drafts, clear caches, and verify the exact 599 files, page mappings,
   unchanged native configuration, and prices. Record actual `DEPLOYED`
   evidence.
4. Require all six desktop/mobile × no-choice/Decline/Accept-then-revoke browser
   profiles, native cart/remove/Undo, Search/PDP, and checkout rendering.
   Checkout is render-only; do not create an order or initiate payment.
5. The coordinator and independent Astra reviewer inspect the actual required
   evidence and hashes before `PRODUCTION_ACCEPTED`. `DEPLOYED` alone is a
   separate state.

Any gating failure or unknown outcome stops the next mutation. Preserve the
journal, reconcile read-only, and use the reviewed ownership/preimage guarded
recovery. Never blindly retry an uncertain result. Recovery also requires actual
readback and public-flow evidence.

## Evidence access and freshness

Portable committed references:

- [Integration adoption manifest](../tasks/integration-release-20261001/adoption-manifest.json):
  adopted source, functional/package identities, bounded local tests, and
  remaining holds.
- [Frozen cutover candidate](../tasks/production-final-pass-20261001/cutover-candidate-manifest.json):
  target, artifacts, page/MU ownership, rollback boundaries, and historical
  state at freeze.
- [Page plan](../tasks/production-final-pass-20261001/evidence/production-v2-page-plan-final.json)
  and
  [page operator](../tasks/production-final-pass-20261001/apply_v2_pages.php):
  ten new routes and guarded prepare/publish/recovery source.
- [MU publisher](../tools/production-runtime/publish-search-privacy.php) and
  [extension](../tools/production-runtime/search-tracking-privacy.php):
  separately hashed Search correction.

New final-clearance and runtime receipts are retained in the coordinator's local
release packet. They are **not assumed to be committed with this
documentation**. On the current operator machine the packet is at
`/Users/theceo/.codex/worktrees/4035/DevSkyy/tasks/production-readiness-redteam-20261001/final-clearance/`,
with execution/readback records in
`/Users/theceo/.codex/worktrees/4035/DevSkyy/tasks/production-final-pass-20261001/evidence/`.
The final-clearance packet contains
`clear-to-execute-scoped-cutover-a662e707d.json`,
`precondition-hold-release-a662e707d.json`, `ci-pass-a662e707d.json`,
`ci-e2e-targeted-retry-dispatch-110435542010.json`,
`ci-e2e-targeted-retry-identity-110451737866.json`,
`acceptance-review-pass-receipt.json`,
`combined-release-evidence-manifest.json`, `acceptance-procedure.md`, and
`frozen-acceptance/acceptance-freeze-manifest.json`. The failed V1 checkpoint is
under
`frozen-acceptance/evidence/production-v2-acceptance/checkpoint-v1-live-20261001t1634/`,
including `results.json`, `evidence-manifest.json`, and desktop/mobile receipts.
The execution evidence folder contains the installation, draft/MU readbacks,
`production-mu-hosting-cache-clear.json`,
`production-mu-installed-cache-cleared-signal.json`, and
`production-search-query-encoding-diagnostic.json`,
`production-v1-query-corrected-checkpoint-attempt.json`, and
`production-v1-query-corrected-checkpoint-instrumentation-hold.json`. The
reviewed query-correction packet is retained under
`final-clearance/frozen-acceptance-query-correction/`, with the corrected run in
`evidence/production-v2-acceptance/checkpoint-v1-query-corrected-20261001t1647/`.
Its freeze/procedure identities and
`final-clearance/resume-v1-search-checkpoint-query-corrected.json` are
separately bound in the table above; their recorded PASS/review states do not
override the later instrumentation hold.

Obtain the current packet from the coordinator and verify its pinned identities
before execution; an unavailable receipt is an explicit gate gap.

The candidate manifest and adoption manifest preserve earlier pending statuses.
Their historical success or hold fields must be read with the later dated
coordinator receipt, without rewriting the originals. This snapshot does not
claim whole-platform E2E completion, accepted GLBs, durable live Governor
qualification, real payment acceptance, or skill-library compliance.
