# Current production status and release boundaries

**Last updated:** 2026-10-01. **Evidence snapshot:** 2026-10-01 15:46 UTC,
recorded from the latest coordinator update. **Operational source:**
`a662e707d698a687d7d1d2efed3975b9aa7325b9`.

This is a dated operator snapshot of the integrated release. It supplements the
retained task records; it does not change their historical states or authorize
execution. Refresh the snapshot from the release coordinator's actual receipts
before using it for a new operation. The documentation commit is separate from
the frozen operational source and does not rebuild the approved package.

## What is established

| Gate or surface                 | Observed result                                                                                    | Evidence limit                                                                                                                                                          |
| ------------------------------- | -------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Five workstreams                | Scoped source adopted and integrated                                                               | The adoption manifest includes open inventory, asset/device, policy, and Governor runtime holds                                                                         |
| Functional source               | Frozen at `299f694702ac2dcc61a0f30aa34e4b3ef12f9118`                                               | Local tests are bounded integration evidence                                                                                                                            |
| Clean V2 package                | Source `5950592d922706dd67fc0320e8c5f3dc005a47b7`; repeat bytes and installed-file checks passed   | Packaging does not establish live production behavior                                                                                                                   |
| Existing staging                | V2 2.5.0 installed; all 599 reviewed file hashes matched                                           | Staging has 220 product/variation records; it cannot establish parity with production's 33 simple products                                                              |
| Production                      | `https://skyyrose.co`, active V1 `skyyrose-flagship`                                               | V2 cutover has not been dispatched                                                                                                                                      |
| Procedure and acceptance inputs | Independent source/freeze review passed; 30 offline tests and Ruff/Black/mypy passed independently | Offline/localhost checks have no authenticated production acceptance scope                                                                                              |
| Exact operational-head CI       | Current retry snapshot: 20 successful checks, 5 intentional skips, 1 in-progress Playwright job    | Prior completed attempt: 20 successful checks, 6 intentional skips, 1 cancelled Playwright job; original log preserved. Retry tests pending; no final `CI_PASS` receipt |
| Execution clearance             | Not issued                                                                                         | Requires the exact-head mandatory CI result and independent combined review                                                                                             |
| Production V2 acceptance        | Not executed                                                                                       | Requires actual installation, V1 Search checkpoint, V2 deployment/readback, six browser profiles, and independent actual-evidence review                                |

The cancelled Playwright job is `110435542010` in CI run `36880002499` on exact
`a662e707…`. Its preserved complete log records about 16 minutes in checkout, 3
minutes in Python dependencies, 28 seconds in frontend npm installation, and 10
minutes 38 seconds in browser OS dependencies with slow APT mirror retries. No
Playwright tests started in that attempt.

Astra recorded `ONE_BOUNDED_TARGETED_RETRY_REVIEW_PASS` after the complete log
review. Integration dispatched exactly one targeted retry on the same frozen
head and workflow run. The 15:46:10 UTC authenticated identity receipt confirms
successor job `110451737866`, run attempt 2, started at 15:45:10 UTC and in
progress at checkout; its Playwright test step remains pending. The latest
coordinator CI snapshot reports 20 SUCCESS / 5 SKIP / 1 IN_PROGRESS; the
deployment-production skip is not materialized in that snapshot. The previous
completed result remains 20 SUCCESS / 6 intentional SKIP / 1 CANCELLED. Dispatch
is not a test result or execution clearance. No source/workflow change or
storefront application was dispatched. PR #1000 remains draft.

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

## Required next states

The reviewed [runbook](RUNBOOK.md) preserves this order:

1. Record successful mandatory CI on exact `a662e707…`, intentional skips, and
   independent combined evidence review. The coordinator then records
   `CLEAR_TO_EXECUTE_SCOPED_CUTOVER`.
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
