# Focused production final pass — October 1, 2026

The current human directive authorizes authenticated corrections and a gated
production delivery. The enabled candidate scope is the V2 WordPress storefront,
native WooCommerce commerce, and existing approved media. Product GLBs and the
mascot remain dormant. Governor, frontend/API deployments and provider generation
are outside this cutover. No staging database synchronization, real payments,
new orders, demo importer, or deletion of older backups is part of this pass.

Root integration owns source/CI, remote mutations and this packet. The coordinator
owns `tasks/production-readiness-redteam-20261001`; independent Astra and the local
architect review changes and actual evidence. Coordinator-owned `AGENTS.md` is
excluded from integration commits.

## Current evidence

- Current CI correction commit: `c921172bd3405654ba7a664eaf10142f50400dfe` on draft PR #1000.
  Frozen-source checkout history, one stale analytics fixture helper, formatting,
  import order, and obsolete positive retired-tagline test expectations were
  corrected. Released storefront bytes and certification pins did not change.
  Local V2 integrity: 27 passed. Offline analytics and browser suites passed.
  The bounded frozen-source fetch now passes actual remote V2 verification;
  CodeQL also passed for both languages. All 21 non-skipped checks now pass;
  six deployment, Docker and advisory jobs remain explicitly skipped.
  Full Python: 8,101 passed, 35 skipped. See `evidence/ci-current.json` and
  `evidence/ci-head-receipt.json`. This supersedes
  `b4fe5059`, retaining its corrections and fixing three stale Python fixtures.
- Exact ZIP remains SHA-256
  `47c485f0001434b7dd52f572812df02e3e103631902a16e86f92ffea407b5a16`,
  176,928,301 bytes, 599 release files.
- Authenticated SSH target inventories identify production `https://skyyrose.co`
  with V1 active and existing staging
  `https://staging-7e48-skyyrose.wpcomstaging.com` with V2 active. Both report
  WordPress 7.1.2, WooCommerce 11.1.2 and PHP 8.4.26. Product configuration only
  was inspected; no customer or order records were read.
- Existing staging V2 backup: 624 files; archive SHA-256
  `fcaa5025e3f15cc08dbcec27253355c9edbfdfd7ef22384234e7aca6ac674c26`.
  Safe archive members and all local restored file hashes passed. Remote restore
  was not executed. See `evidence/staging-backup-receipt.json`.
- The reviewed ZIP was installed on the existing staging site. Authenticated
  installed-file verification matched all 599 manifest hashes, with no missing,
  extra, changed or symlinked files. See `evidence/staging-install-receipt.json`
  and `evidence/staging-installed-hashes.json`.
- Production has 33 published simple products, no enabled per-product stock
  management or recorded remaining balances, and no native size variations.
  Staging contains 220 product/variation records. Staging cannot establish
  production catalog parity. Registry edition sizes are not remaining balances.
  The narrowed release preserves these 33 simple products, current IDs/prices,
  full-payment checkout, unmanaged quantities and the existing null shipping-date
  promise. Variation conversion, allocation, balances, price/type/date changes
  and inventory-policy expansion are excluded. The unanswered business questions
  govern those excluded expansions; they do not block this scoped storefront cutover.
- Both targets report the analytics API URL absent. This does not qualify live
  analytics delivery. Shopping must remain usable with delivery unavailable.
- Anonymous desktop/mobile staging journeys preserved native size, price and
  quantity through add-to-cart, remove/Undo and checkout rendering. No order,
  payment or account submission occurred. Accepted-consent analytics returned
  HTTP 503 gracefully; no delivery acknowledgement exists. The local synthetic
  V1-to-V2 cart transition preserved the unknown historical promise.
  See `evidence/staging-browser/README.md` for exact scope and evidence.
- The header-count finding is closed for observed desktop/mobile journeys:
  native WooCommerce automatically refreshed the header and mini-cart to
  3 units/$230 within approximately 0.4-0.9 seconds after Undo. Native condition
  waits, events, responses and accessible labels are retained in the separate
  `badge-investigation` and `mobile-badge-recovery` evidence folders. No runtime
  patch was needed. Platform `tk_*` and WooCommerce `sbjs_*` consent behavior
  remains under investigation.
  SkyyRose's own SEE identifier suppression does not establish sitewide consent.
  Staging attribution and the two optional Jetpack analytics modules are now
  disabled through their supported APIs. Fresh configuration readback confirms
  those settings and exactly two modules removed. The original helper refused
  its final receipt because a sparse PHP array became a JSON object; the values
  comparison was corrected and read-only reconciliation completed, with no
  repeated writes. Five offline failure/schema tests pass.

  Ordinary URLs initially served stale HTML with the old tracking scripts;
  a cache-busted MISS response omitted them. Both supported domain purge
  requests failed with the hosting error, and cache-status querying also failed.
  Log filenames do not imply success. The independently authenticated hosting
  UI subsequently confirmed a staging global edge-cache clear. The separate
  post-clear normal-route matrix passes: five no-choice routes, eight Decline
  observations including a current returning visitor, and seven Accept-to-revoke
  observations. The accepted session stopped, identifiers cleared and subsequent
  SEE requests stopped; native three-unit/$230 shopping remained usable.
  Optional platform tracking handles, requests and cookie families were absent
  in that bounded matrix, including the tested accepted pages. Independent Astra
  reviewed the exact receipts and harness. See
  `evidence/consent-runtime-recovery/README.md` and the hosting-clear receipt.
  Historical browser cookies can remain after their
  producer is disabled. These platform statistics stay disabled for accepted
  visitors too; no Accept-to-enable bridge is claimed.
  The original pre-configuration cookie-bearing browser context was not retained;
  that historical visitor and other geographic cache locations remain unverified.
  Earlier stale-page failures and the accepted-navigation waiter failure remain
  preserved independently. A delivery overlay redacts dynamic native cart keys
  missed by the original sanitizer; original HTML and manifests remain unchanged.

  The actual production V1 backup is a separate 79-file implementation declaring
  version 2.3.1, with no matching consent/settings/SEE controls in its archived
  PHP/JavaScript. It cannot inherit the current repository V1 or staging V2 test
  assumptions. Production's three optional tracking controls have a separate
  pinned helper, 27 offline tests and independent Python/architect review. The
  three production changes were applied once and independently read back: order
  attribution disabled, Stats disabled and WooCommerce Analytics disabled; the
  other 41 module states remain unchanged. Search remains active. Separate hosting
  UI receipts confirm object-cache and global edge-cache clearing. Actual V1
  browser observations still found Search's tracking producer and absent consent
  controls. V2 replacement and its production acceptance supersede the legacy
  consent, quantity-control and navigation defects; no separate V1 repair is required.

## Scoped cutover dependencies

The current scoped authority is recorded in the coordinator-owned
`../production-readiness-redteam-20261001/SCOPED-CLEARANCE.md`. The remaining
predeployment dependencies are a separately hashed Search privacy MU extension
and ten routing pages. The immutable theme ZIP is unchanged.

Authenticated installed Jetpack source shows Instant Search unconditionally
enqueues `jp-tracks`, separately from the Search application's `wp-i18n`
dependency. The upstream disable-tracking filter suppresses analytics pushes but
does not suppress the script itself. The reviewed extension applies that filter,
dequeues only `jp-tracks` and gates its final script tag, preserving Search.
Source/offline review passed; atomic publication, actual WordPress dependency
tests and normal-visitor Search acceptance remain separate required evidence.

Four collection pages use the existing Collections parent 9327. A new Worlds
parent has a separately reviewed four-link directory and four scene children;
size-guide uses the frozen source's guidance content. Existing merchant pages,
cart 9451, checkout 9452, their classic shortcodes, templates and WooCommerce
options remain unchanged. Draft preparation, source pins, collision checks,
durable operation records and owned-row rollback precede publication under V2.
Native fallback is source-supported; effective plugin-enabled rendering must pass
on the actual installed production candidate. Final combined clearance is pending.

## Canonical metadata correction

`get_product(sku).catalog`, backed by the one canonical logo registry, supplies
the `_is_preorder` and `_preorder_edition_size` projection plans. The plans
correct 45 fields across 25 published SKUs on each target. They do not change
product types, prices, quantities, dates, artwork or orders. Legacy `250` flags
and `Draft` edition values conflict with the registry.

The first sequential helper failed independent recovery/concurrency review and
was not executed. Its replacement uses one native mysqli/InnoDB SERIALIZABLE
transaction with identity, old-value, type and target guards, durable attempts,
read-only unknown-outcome reconciliation and separate WooCommerce cache clearing.
The actual staging rollback probe updated 33 existing fields and inserted 12,
then rolled back all 45 without committing. The subsequent staging application
committed all 45, cleared caches and passed fresh WooCommerce readback.
An independent fresh inventory compared all captured configuration across 220
products/variations with the original snapshot: exactly the planned 45 metadata
changes, zero nonplanned differences. See the probe/apply attempt files and
`evidence/staging-metadata-independent-readback.json`.

The historical staging executions retain wrapper SHA `29665acc...` and PHP
payload SHA `06116634...`. The reusable wrapper now enforces reviewed digest
pins, the actual imported registry reader origin and sanitized diagnostics;
21 offline tests and independent architect/Python reviews pass. Its externally
supplied execution-manifest digest is
`b2ebf1317b38ba43c05ae7d400cec10910fb71d61932cc475c1ecba48a1547a3`.

The production correction then committed all 45 known metadata fields through
that reviewed launcher. Cache clearing and fresh WooCommerce reads passed.
The independent full 35-record comparison found exactly the planned substitutions
and zero other captured-field changes; Astra independently verified raw and
WooCommerce values and identities over authenticated SSH. Production remains
on active V1. See `evidence/production-metadata-attempt.json` and
`evidence/production-metadata-independent-readback.json`.
A metadata correction does not establish inventory reservation or shipment
promises, and the rollback probe does not prove an actual transport failure or
concurrent-writer scenario.

## Deployment skill adoption and task-specific examples

This packet is the maintained task overlay for
[`engineering:deploy-checklist`](/Users/theceo/.codex/plugins/cache/claude-cowork/engineering/1.2.0/skills/deploy-checklist/SKILL.md).
The disposable plugin cache was not edited. Coverage is **PARTIAL**: target
inspection and local restoration are verified; production activation and remote
restore have not occurred. Authentication is not applicable to offline tests.

**Correct example — VERIFIED_LIVE inspection + REPRODUCED_LOCAL restoration:**
under the current authenticated-fix directive, use existing SSH with BatchMode,
first verify `wp option get home`, stream a backup of the existing staging theme,
then inspect safe tar members and compare every extracted file hash. The
identified backup receipt records the target, scope, archive digest and 624-file
restoration result. This proves the retained local backup, not a remote restore.

**Incorrect example — ILLUSTRATIVE_UNEXECUTED:** sync staging's database over
production to obtain its variations and activate V2 immediately after upload.
Correction: preserve the production database, qualify catalog differences and
native commerce separately, verify the exact installed files, and perform a
separate gated activation with both theme backups and configuration recorded.
WordPress.com documents the risk of replacing orders/customers during staging
database synchronization, and WP-CLI documents that `--force` overwrites an
existing theme while `--activate` immediately changes the active theme.

Primary references:
[WP-CLI theme installation](https://developer.wordpress.org/cli/commands/theme/install/),
[WordPress.com staging](https://wordpress.com/support/how-to-create-a-staging-site/),
[WooCommerce order troubleshooting](https://woocommerce.com/document/managing-orders/troubleshooting-orders/).
These source checks establish documented behavior, not authenticated execution.
