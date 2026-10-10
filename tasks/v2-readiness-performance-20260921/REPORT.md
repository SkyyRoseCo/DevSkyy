# V2 performance and target readiness investigation

Verified 2026-09-22 UTC against production `https://skyyrose.co` (site 238510894) and staging `https://staging-7e48-skyyrose.wpcomstaging.com` (site 256563697). Source base: `15d6f012a7302b8386d5502fe3391131501fd3cb`, isolated branch `codex/v2-readiness-performance-20260921`.

## Performance finding and repair

Three sequential anonymous Lighthouse 13.5.0 mobile/simulated runs of the currently deployed staging homepage measured:

| Run | LCP | TBT | CLS | Performance score |
| --- | ---: | ---: | ---: | ---: |
| 1 | 3.470 s | 0 ms | 0.000157 | 91 |
| 2 | 4.284 s | 15.5 ms | 0 | 83 |
| 3 | 3.402 s | 0 ms | 0.000157 | 91 |

Median LCP: **3.470 s**. This is a fresh pre-deployment baseline, not a measured effect of this patch. Raw report paths, hashes, exact timestamps and throttling profiles are in `performance-baseline.json`. Earlier 5.2 s / 540 ms results illustrate variability; they are not a controlled before/after comparison.

The measured LCP element is the first SG-005 on-model film image. Its served markup lacks the image-priority change already merged in PR #964. Authenticated WP-CLI confirmed staging uses `skyyrose-flagship-2` 2.4.4 and environment `staging`; production still uses V1 `skyyrose-flagship`.

New root cause: first-view font preloads and the inline critical CSS still selected Cinzel after the homepage display family changed to Archivo. Fixed the preload to the existing `assets/derived/fonts/archivo-normal-width.woff2`, updated the critical extraction contract, and rebuilt `home.min.css`. The two preloaded faces are now Archivo and Hanken Grotesk. The regression requires the current headline face, rejects the obsolete Cinzel priority, and checks exact preload/CSS URL parity. No imagery, product facts, layout rules, animation rules or font binaries changed. Integrity hashes were reconciled for these reviewed changes only.

Critical CSS is 16,147 bytes against its existing 16,384-byte budget. Independent review confirmed CSS excluding font-face declarations is identical. Full `npm run build`, `npm run verify` (including 114 JavaScript tests), and `npm run package:theme` passed using the declared Python 3.12.12/Pillow 12.3.0/Node 22.23.2/npm 10.9.8 toolchain. `sync_product_registry.py --check` passed. The package contains 566 runtime entries; SHA-256 `37f0d6f7d7b11b55f359c59c2932c761630d64c171169f8d40fd0a00e342a9cb`. No deployment has occurred in this investigation.

The remaining performance gate requires serving the exact candidate, confirming asset hashes and image priority in the browser, then repeating the same three-run profile plus desktop/mobile interaction checks. LCP must not be represented as passing yet. TBT is a lab diagnostic, not field INP. [Core Web Vitals thresholds](https://web.dev/articles/defining-core-web-vitals-thresholds) apply at the 75th percentile of real user observations; a lab pass alone cannot certify field CWV.

## Target evidence

`target-status.json` contains authenticated read-only WordPress.com MCP receipts. WP-CLI checks below used existing environment-specific SSH credentials without printing credentials or customer data.

| Gate | Verified observation | Remaining boundary |
| --- | --- | --- |
| Production backups | Active, managed credentials, 447 backups; latest reported backup 2026-09-21 09:13:08, attempt finished without failure; storage not stopped | Restore preflight returned null. No restoration executed. Provider timestamps retained as returned. |
| Staging backups | Active, managed credentials, 50 backups; latest reported backup 2026-09-21 09:52:48, attempt finished without failure; storage not stopped | No restoration executed. |
| Theme rollback | Staging has `skyyrose-flagship-2.old.1788790527-87183` and `.old.20260817000113`; each has readable style.css/functions.php | Directory presence is not a rehearsed rollback or a complete site backup. Snapshot current state immediately before approved deployment. |
| Monitoring | Both sites: monitor active, status up | Actual downtime alert delivery and recipient binding unverified. The account notification-settings call returned unrelated site IDs, so it cannot certify either target's recipients. No alert sent or outage induced. |
| Production indexing readiness | blog_public=1, public/launched; homepage HTTP 200, no noindex response header/meta, self canonical; robots permits public routes; sitemap lists 70 URLs, all under skyyrose.co | This verifies current V1 crawl configuration, not Google index inclusion or a future deployed V2 response. |
| Staging indexing isolation | `X-Robots-Tag: noindex, nofollow, noarchive`, HTML noindex/nofollow | Preserve this staging boundary. |
| Commerce | All staging gateways disabled; Stripe testmode=yes, test_publishable_key/test_secret_key/test_webhook_secret settings empty | These option checks do not establish an authenticated test processor or rule out every OAuth storage mechanism. Establish the staging sandbox account, gateway and webhook before a payment test. |
| Production commerce | Enabled Stripe/Link/Klarna report testmode=no; WooPayments enabled | No live charge placed. Enabled settings do not prove payment/order/webhook/email success. |

## Concrete next execution

1. Deploy the verified V2 package to staging only after explicit deployment approval. Capture the active theme manifest and retain the pre-swap directory; verify candidate asset hashes, noindex and the home → product → cart → checkout route. Re-run the three-sample mobile measurement with the same profile. Rehearse theme rollback and candidate re-application within that approved staging window, retaining both manifests and HTTP/browser results.
2. Rehearse full-site restoration on an isolated copy with a specifically selected provider backup and a current-state preservation plan. Capture backup identifier, restored files/database integrity, isolated URL binding, disabled outbound mail/payment jobs, completion time and restored public flows. A theme-directory rollback does not close this gate. The [provider restore instructions](https://wordpress.com/support/restore/) state that restoration overwrites subsequent content; no production or staging database was rolled back during this audit.
3. Confirm the site-specific alert recipient and use a provider-supported delivery test to that approved destination. Record provider acceptance separately from inbox/push receipt. [WordPress.com's monitoring documentation](https://wordpress.com/support/downtime-monitoring/) describes account email, notification-bar and optional push delivery; `active=true` alone is not a receipt. Do not manufacture an outage to prove delivery.
4. Connect staging to the intended Stripe sandbox through the normal secure setup, verify test mode and matching webhook, and isolate test mail recipients. Exercise successful and declined test payments, order totals/shipping/tax, duplicate submission/webhook idempotency, stock updates, confirmation and refund paths. Record test IDs without secrets/customer data. Present the rendered checkout/order result for founder acceptance. Never use production live-mode credentials or a real payment to fill a staging evidence gap.

## Approval boundary

Repository AGENTS.md requires explicit approval for WordPress deployment. The WordPress.com tools separately require describing and confirming target writes. Local fixes, public requests and authenticated read-only checks are complete; target mutation is not silently inferred from a source-check pass. An automatic hook also rejected a read-only deployment-script search as a production deploy. That command was not retried with an acknowledgement bypass.
