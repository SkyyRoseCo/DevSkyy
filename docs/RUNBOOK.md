# DevSkyy production runbook

**Last updated:** 2026-10-01. **Operational source:**
`a662e707d698a687d7d1d2efed3975b9aa7325b9`.

Use [PRODUCTION_STATUS.md](PRODUCTION_STATUS.md) for the dated live-target/CI
snapshot, current holds, and literal artifact/receipt identities. This procedure
moves the captured V1 baseline to the reviewed V2 candidate within a scoped
WordPress storefront cutover. Staging qualification remains separate from
production acceptance. API, dashboard, Fly, Governor, paid providers, GLBs, and
mascot deployment are outside this runbook's release scope.

## Before application

Execution requires current explicit scope authorization, final exact-head
mandatory CI, and independent review of the frozen procedure and combined
artifact/evidence bindings. The release coordinator issues
`CLEAR_TO_EXECUTE_SCOPED_CUTOVER` after those conditions pass. A local check,
source review, uploaded archive, staging result, or public HTTP 200 does not
supply that signal.

Read the frozen final `acceptance-procedure.md` from the coordinator packet
identified in
[production status](PRODUCTION_STATUS.md#evidence-access-and-freshness). Its
final sequence supplements the older candidate manifest: qualify the Search
privacy extension and real cache clear while **V1 remains active before V2
activation**. The committed
[cutover manifest](../tasks/production-final-pass-20261001/cutover-candidate-manifest.json)
retains its historical sequence/status for audit purposes.

Verify immediately before application:

- Exact operational source, ZIP, Search extension, page plan, frozen acceptance
  source/tests, browser runtime, and reviewed evidence hashes.
- Authenticated target `https://skyyrose.co`, current V1 stylesheet, captured
  WordPress/WooCommerce/PHP versions, existing native product configuration and
  price/tax/currency baseline.
- All ten activation-option preimages, existing merchant page/shortcode/option
  snapshots, active/inactive theme file maps, retained archives, operation IDs,
  exclusive operation journals, and MU/page ownership guards.
- Literal reviewed receipt dependencies. Do not approve changed bytes by merely
  computing replacement hashes.

Changed preimages, pending CI, unexpected skips, missing receipts, or ambiguous
ownership stop application for read-only assessment. Preserve unrelated work and
concurrent merchant changes. Use the frozen operational source, not a rebuilt
package from an unrelated dirty checkout.

## Ordered storefront cutover

1. **Install inactive V2 and prepare owned drafts.** Install the exact ZIP over
   the inactive `skyyrose-flagship-2` directory. Independently verify all 599
   installed members. Keep active V1 unchanged. Prepare only the ten reviewed
   new pages using the
   [guarded page operator](../tasks/production-final-pass-20261001/apply_v2_pages.php),
   exact source/preimage checks, and a durable returned-ID journal. Preserve all
   existing merchant pages and native WooCommerce IDs/options.
2. **Install Search privacy correction.** Use the reviewed
   [MU publisher](../tools/production-runtime/publish-search-privacy.php) with
   durable external intent, exclusive/cooperating-writer control, and
   inode-bound ownership. Independently read back target, installed bytes/hash,
   ownership, and still-active V1. Unknown transport outcomes permit read-only
   reconciliation first; do not blindly retry or remove a same-byte foreign
   file.
3. **Clear caches and pass V1 Search.** Record separate actual object/global
   edge-cache confirmations through supported authenticated hosting controls.
   Produce `MU_INSTALLED_CACHE_CLEARED` from those operations. Run the frozen
   Search checkpoint in fresh desktop and mobile browser contexts. Require
   normal home/PDP routes, no optional platform tracking before consent, actual
   positive Search results and the recorded native product click, and a settled
   successful no-results state. Both profiles and independent evidence review
   must pass before `V1_SEARCH_CHECKPOINT_PASS` and activation.
4. **Activate through WordPress core.** Recheck all ten captured
   activation-option preimages and the Search checkpoint. Use native core
   `switch_theme`, complete next-bootstrap theme-switch handling, and read back
   the resulting activation state. Restore/preserve the reviewed
   absent-versus-present option semantics. An issued switch command alone does
   not establish completed activation.
5. **Publish, clear, and read back V2.** Publish only the ten owned drafts with
   source/ownership/preimage guards. Read back each ID, path, parent, status,
   template, and content; reject collisions or unexpected rows. Clear
   object/global edge caches. Independently verify active theme/home/version,
   all 599 file hashes, MU bytes/ownership, page mappings, preserved
   merchant/WooCommerce configuration, and unchanged native prices. Record an
   actual `DEPLOYED` receipt with the verified IDs and dependencies.
6. **Run production acceptance and independent review.** Use the frozen V2
   harness only after the coordinator's actual `DEPLOYED` signal and receipt.
   Require all six profiles and the behavior/evidence checks below. The
   coordinator and independent Astra reviewer inspect outputs and evidence
   hashes before `PRODUCTION_ACCEPTED`.

General deployment wrappers are not substitutes for this cutover procedure.
[scripts/deploy-theme.sh](../scripts/deploy-theme.sh) is an engine invoked by
[scripts/deploy-staging.sh](../scripts/deploy-staging.sh) or
[scripts/deploy-production.sh](../scripts/deploy-production.sh); it refuses
unsupported direct invocation. Existing wrapper flags, successful staging
transfers, or a version change do not authorize product/page/MU operations or
production acceptance. Use the reviewed release packet for the active operation.

## Production acceptance contract

The six profiles are desktop/mobile, each with a fresh anonymous context for no
choice, Decline, and actual Accept → Cookie settings → Decline. Use normal
navigation and observe actual native traffic without blocking, rewriting,
synthetic interception, or cache-busting to manufacture success.

| Area                | Required actual behavior                                                                                                                                                                                                       |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Routes/navigation   | All 12 planned route mappings; non-404 content; four Worlds links; collection native product links; actual header navigation; rendered size guide                                                                              |
| Native product/cart | Existing simple-product forms/IDs and current native prices; two Kids 001 at $65 plus one BR 003 at $100 gives subtotal $230/count 3; remove Kids gives $100/count 1; native Undo restores $230/count 3 after fragments settle |
| Cart retention      | Accessible header count and mini-cart subtotal agree; cart persists through consent changes and reloads                                                                                                                        |
| Search              | Actual positive results/native product click and settled empty results; V2 header dialog is exercised                                                                                                                          |
| PDP/checkout        | Standard and existing preorder PDPs render; native checkout form renders without customer input, submission, order creation, or payment initiation                                                                             |
| Platform privacy    | Zero optional platform tracking requests/handles/cookies in every required phase                                                                                                                                               |
| Owned analytics     | No own identifier/cookie transmission/POST before choice or after decline/revocation; accepted delivery reports actual status; same-document revoke, flush interval, reload, and returning navigation are covered              |
| Runtime/evidence    | No unexpected JavaScript exception, native-flow failure, identity drift, missing profile, crash, or ambiguous observer/receipt evidence                                                                                        |

The cart amounts above are captured native production acceptance baselines, not
new authored product facts or price changes. Accepted analytics HTTP 503 proves
unavailable delivery/graceful degradation only; it does not prove durable
ingestion. Classify requests by actual initiation eligibility, retaining that
classification if their response arrives after revocation. Missing/ambiguous
observer evidence remains FAIL/UNKNOWN. Local fixtures do not establish these
production behaviors.

Save sanitized document/traffic observations, cookie names and identifier
presence, actual statuses, start/end, operation IDs, command outcomes,
dependencies, executed-source hashes, and each profile result. Do not export
cookie values, raw headers, request bodies, nonces, dynamic cart/remove/Undo
keys, or customer information. Preserve failed attempts in separate exclusive
output directories.

## Stop, reconcile, and recover

Stop the next mutation at the first gating failure or unknown outcome. Preserve
the attempt journal and artifacts. Reconcile target identity and owned state
read-only before choosing the reviewed recovery mode; do not make a new
operation to evade an uncertain previous attempt.

Recovery may restore only this operation's unchanged new pages and inode-proven
MU file. Preserve foreign files/pages, same-byte competing writers, and merchant
changes. Restore active V1 through native core and the exact captured
activation, sidebar, menu, and theme-mod option preimages. Restore replaced
inactive V2 files from the retained archive only when the reviewed plan requires
it. Do not perform database synchronization, backup pruning, or rollback
unrelated confirmed metadata/tracking changes.

After recovery, clear object/global edge caches, read back theme/configuration/
page/MU state, and verify normal home, representative PDP, native cart/checkout
rendering, and Search on desktop/mobile. Record recovered and unresolved
conditions. Issuing a restore command is not a `ROLLED_BACK` receipt. Failed
cleanup, ownership drift, or transport uncertainty stops automatic retry.

## Independent local workspace checks

These commands are for local validation in the indicated workspace. They do not
deploy a service or clear a production gate by themselves.

```bash
# Repository root: Python and shared TypeScript
uv run --locked --extra dev python -m pytest tests/ -v
npm run lint
npm run type-check
npm test
npm run build
```

```bash
# Dashboard workspace
cd frontend
npm run lint
npm run type-check
npm test
npm run build
npm run test:e2e
```

```bash
# V2 theme workspace: rebuild after source changes, then inspect generated diffs
cd wordpress-theme/skyyrose-flagship-2
npm run build
npm run check:assets
npm run lint:php
npm run verify
npm run package:theme
```

Root `make ci` is a legacy composite with non-blocking checks and does not cover
the independent dashboard/theme suites. See [README.md](../README.md#validation)
and the release's exact mandatory CI receipt. Source/certification changes
require new review; this release consumes its frozen package.

For local containers, follow [DOCKER.md](DOCKER.md): `make docker-secrets`,
`make docker-config`, then `make docker-up`. These use `.env.docker` and the
configured API/database/Redis/workers stack. They are local operations, separate
from production hosting.

## API health and other deployment surfaces

Source routes in [main_enterprise.py](../main_enterprise.py) are `/health`,
`/ready`, and `/live`. `/health` includes database health information but its
outer status is always `healthy`; `/ready` currently returns constant
`{"ready": true}`. Neither HTTP 200 nor this readiness response proves that all
integrations, Redis, providers, or downstream services are available. The full
backend does not mount a root Prometheus-format `/metrics` endpoint.

Source configurations distinguish the slim MCP service in
[fly.toml](../fly.toml) (`mcp_service:app`) from the full backend in
[fly.backend.toml](../fly.backend.toml) (`main_enterprise:app`). The dashboard's
[Vercel configuration](../frontend/vercel.json) describes a build target, not
current host/domain/automatic-deployment proof. These configurations are not
live deployment receipts and their services are outside this storefront cutover.
