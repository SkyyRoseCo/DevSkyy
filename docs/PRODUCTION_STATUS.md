# Current production status and release boundaries

**Last updated:** 2026-10-01. **Evidence snapshot:** 2026-10-01 16:11 UTC,
recorded from the latest coordinator update. **Operational source:**
`a662e707d698a687d7d1d2efed3975b9aa7325b9`.

This is a dated operator snapshot of the integrated release. It supplements the
retained task records; it does not change their historical states or authorize
execution. Refresh the snapshot from the release coordinator's actual receipts
before using it for a new operation. The documentation commit is separate from
the frozen operational source and does not rebuild the approved package.

## What is established

| Gate or surface                 | Observed result                                                                                           | Evidence limit                                                                                                                                     |
| ------------------------------- | --------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Five workstreams                | Scoped source adopted and integrated                                                                      | The adoption manifest includes open inventory, asset/device, policy, and Governor runtime holds                                                    |
| Functional source               | Frozen at `299f694702ac2dcc61a0f30aa34e4b3ef12f9118`                                                      | Local tests are bounded integration evidence                                                                                                       |
| Clean V2 package                | Source `5950592d922706dd67fc0320e8c5f3dc005a47b7`; repeat bytes and installed-file checks passed          | Packaging does not establish live production behavior                                                                                              |
| Existing staging                | V2 2.5.0 installed; all 599 reviewed file hashes matched                                                  | Staging has 220 product/variation records; it cannot establish parity with production's 33 simple products                                         |
| Production                      | `https://skyyrose.co`, active V1 `skyyrose-flagship`                                                      | Inactive V2 install command has run; actual installed-file/V1-preservation readback pending. No V2 activation or `DEPLOYED` receipt                |
| Procedure and acceptance inputs | Independent source/freeze review passed; 30 offline tests and Ruff/Black/mypy passed independently        | Offline/localhost checks have no authenticated production acceptance scope                                                                         |
| Exact operational-head CI       | `CI_PASS`: 21 mandatory successful checks, 6 intentional skips, no pending/failure/cancellation           | Single targeted Playwright retry: 62 passed (31 Chromium, 31 mobile), 0 failed/skipped/flaky; source CI is separate from production acceptance     |
| Execution clearance             | `FINAL_COMBINED_CLEARANCE_PASS`, architect PASS, and coordinator `CLEAR_TO_EXECUTE_SCOPED_CUTOVER` issued | Conditional immediate guards remain required. Inactive installation begun; all subsequent mutations held for read-only outcome/precondition review |
| Production V2 acceptance        | Not executed                                                                                              | No `DEPLOYED` or `PRODUCTION_ACCEPTED`; actual installation/readback, V1 Search checkpoint, activation, and six-profile acceptance remain required |

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

At **16:10:54 UTC**, integration reported that the first inactive V2 ZIP
installation had been dispatched under that clearance before the coordinator's
hold message arrived. The command returned **exit 0**. At the **16:11 UTC
snapshot**, actual verification of all 599 installed file hashes and
preservation of active V1 remains pending. Command completion does not establish
an accepted installation. Outcome verification and read-only precondition
classification are under review; **all subsequent mutations are held**. No page,
MU, or activation writes have been reported. V1 remains active, and neither
`DEPLOYED` nor `PRODUCTION_ACCEPTED` is established.

The original `production-inactive-v2-install-intent.json` and
`production-inactive-v2-install-attempt.json` are retained in the production
final pass evidence folder without rewriting earlier records. Any changed or
unknown precondition stops the next mutation for read-only reconciliation under
the reviewed stop/recovery rules. Source CI, conditional clearance, command
outcome, verified installation, deployment, and actual production browser
acceptance remain separate evidence states.

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
| Final acceptance freeze: 26 files               | `22b30db9d34eda875acbcc64a26a172bdd2d7e051cadcb4ce41a5c66e8d0b0d1` |
| Final acceptance procedure                      | `8944f3fe7f461117ec57bec7fc852835c2110bcd534481afc797d33e56ca887e` |
| Final V2 acceptance harness                     | `0573e738c95a18528bce4e3dd6631c5a5f2c78e9b9fcd2ee083e21ef6807497d` |
| Combined release evidence manifest: 12 bindings | `ef053fa175b69913469c33a259c91afb61eff811e004eff4e09457145e20e2a2` |
| Procedure/source review receipt                 | `cd7d6b16d322dd2ab7ecec19be9f2ff3fff72663aa5a4876be56b5a67647e2ff` |
| Final exact-head CI receipt                     | `23c467bf8dbde980ab3c22f95f84d324cbdf72acac3368bed37c031289d5eeb4` |
| Scoped pre-execution clearance receipt          | `4f90c881ea90674736aa8828e50a34f27f1c604903f9ac6b32d19803149ba286` |
| Inactive V2 installation intent                 | `db924ba569058bb1a2f961756229e919c521270d2c701f9a8ee03f0cdf94c9a6` |
| Inactive V2 command-attempt receipt             | `317bcbe7625e1a6c9a32dcf790167585f3a1802d82da5ca269b686ea3abc5f9a` |

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

The reviewed [runbook](RUNBOOK.md) preserves this order. The first clearance
state is complete at this snapshot; runtime states still require actual
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
`/Users/theceo/.codex/worktrees/4035/DevSkyy/tasks/production-final-pass-20261001/`.
The final-clearance packet contains
`clear-to-execute-scoped-cutover-a662e707d.json`, `ci-pass-a662e707d.json`,
`ci-e2e-targeted-retry-dispatch-110435542010.json`,
`ci-e2e-targeted-retry-identity-110451737866.json`,
`acceptance-review-pass-receipt.json`,
`combined-release-evidence-manifest.json`, `acceptance-procedure.md`, and
`frozen-acceptance/acceptance-freeze-manifest.json`. Obtain the current packet
from the coordinator and verify its pinned identities before execution; an
unavailable receipt is an explicit gate gap.

The candidate manifest and adoption manifest preserve earlier pending statuses.
Their historical success or hold fields must be read with the later dated
coordinator receipt, without rewriting the originals. This snapshot does not
claim whole-platform E2E completion, accepted GLBs, durable live Governor
qualification, real payment acceptance, or skill-library compliance.
