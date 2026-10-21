# Verified package deployed to SkyyRose

Status: DEPLOYED_WITH_BOUNDED_VERIFICATION.

On October 20, 2026 at 19:10:58 PDT (October 21 02:10:58 UTC), Integration replaced the active theme through the established authenticated WordPress.com SSH route. This directly fulfills the user's current deployment instruction; no competing implementation owner was created.

## Exact release

- Site: https://skyyrose.co; authenticated WordPress.com site ID 238510894; stylesheet `skyyrose-flagship-2`.
- Version 2.5.6; source 83d0edb531f505bf0762a6b41ed2ebef0d3f1955; theme tree cae9475ff0551256848fb6e4d8834366b73f4858.
- ZIP SHA256 `e3328e6db2fcdb6d590837c526eddb9c632bf8a769c180d6bdbc4f0cdbd9c739`: 732 members, 285,780,970 bytes.
- One changed release member versus prior c314: `inc/simple-product-sizes.php`. All 731 other members, including images/styles/scripts/templates, are identical. The later d43b4c17a test-only commit does not change the package tree.
- Exact installed compatibility fix: only the two source-pinned Stripe Tax callbacks that pass product lines through are admitted. Unknown callbacks, arguments or source drift remain refused. Native HPOS/CPT upgrade checks passed.

## Filesystem repair and retained rollback

The first replacement safely stopped with EXDEV when moving the old theme into `/tmp`; the virtual filesystem reported equal device IDs, but an actual disposable rename exposed the cross-device boundary. Reconciliation proved the active old 808 and staged new 732 were unchanged. No blind retry, mirrored deletion or partial-copy fallback was used.

A fresh attempt used a checked same-filesystem rename. Actual disposable forward and reverse renames passed. A public control returned its exact marker; all 15 direct/encoded hidden-folder canary requests returned uncached nginx 403. The exact qualified parent was set 0700 before retaining the old theme. After activation, direct and encoded requests for actual retained source also returned 403.

Both the failed original journal and the successful fresh journal are retained. Remote retained source: `/srv/htdocs/wp-content/themes/.sr-private-route-probe-20261021T004120Z-e3328e6d/skyyrose-flagship-2`. All 808 old members and both dist artifacts remain intact and rehashed. The earlier permanent private local capture also remains intact. The uploaded verified ZIP remains available on the server. No cleanup was expanded.

Rollback is preserved, not invoked. Do not automatically restore the older theme after activation: first reconcile current generation orders and any late unmarked orders, and retain the current commerce safeguards. Never remove or rebaseline the two immutable history/boundary options as a rollback shortcut.

## Validation actually performed

- Fresh actual installed PHP 8.4.26/MariaDB 11.8.9 HPOS profile admitted the exact initializer and native order fingerprint before replacement. CPT coverage is synthetic native local, not an installed CPT claim.
- New exact package passed 36 HPOS + 36 CPT native local steps, including 14 nested upgrade checks per mode and normal wp-admin upload/install/activate/replace. Prior failures remain retained.
- First public cache-busted homepage returned 200 without PHP error text. A standalone read-only SQL snapshot before the first post-deployment WP-CLI call observed both valid initializer options, exact 213-byte baseline SHA e20d90615a3b4d15b447b406ec6d6d3ff015f0024790e9c5d5e079b1b0405484, 1 legacy fingerprint, 1 shop order and 0 marked orders. CLI bootstrap is not labeled inherently read-only.
- Initial normal Kids URL served a stale page. The established `wp cache flush` succeeded; the subsequent normal URL served the new Kids arrival as a cache HIT. No blanket transient deletion or rewrite flush was used.
- 12 unique public browser cases passed: homepage, Shop, Kids collection, kids-001, br-004 and sg-013, each at 390/1440px. Exact released CSS bodies were identified inside host-combined stylesheets. Sampled visible images loaded, pages had no horizontal overflow, and required size lists matched actual installed catalog reads and accepted DOM selection. No consent interaction or form submission occurred; size interaction does not claim post-consent visible usability or a purchase funnel.
- Public browser access permitted GET/HEAD only and one bounded theme-image CDN route. Six expected failed tracking fetches are retained and attributed by exact WooPayments frontend-tracks.js source SHA, exact stack and blocked+failed admin-ajax POST timing. There were zero unattributed JavaScript errors and zero same-origin HTTP errors. Background tracking, payment and unrestricted plugin behavior remain unqualified.
- All browser connections/process groups were retired. Three earlier browser attempts remain retained: strict stylesheet-path assumptions, intentionally blocked CDN media, and the diagnostic blocked tracking failure were not erased or recast as passes.
- Later native readback validated the same 1 legacy order, 0 unknown unmarked and 0 invalid marked orders. The original immutable fingerprint matched before and after deployment. No order, stock or payment mutation was invoked; no customer identifiers, order maps or raw keys were exported. This is fingerprint and bounded operation evidence, not a whole-database byte-equivalence claim.
- Anonymous empty cart returned 200; empty checkout redirected to the cart and returned 200 without PHP errors. No cart add, checkout submission or payment occurred.
- Final fresh census again matched 732 active members and 808 retained old members plus the 2 preserved dist artifacts. Recorded snapshots show no new generation orders; no universal writer-drain claim is made.

## Limits and retained holds

No live order, cart add, payment, product conversion, support outreach, provider archive acquisition, paid generation or fresh privacy-collector run occurred. Component, synthetic native, actual installed HPOS and sampled live-page qualification remain distinct. Historical synthetic 1290/1292 ownership remains NOT_ESTABLISHED; it is not presented as a live order defect. No new creative/use grants or broader installed-stack acceptance are inferred from deployment.

The new live preview is in `.artifacts/release-gates-20261020/production-resumption-20261020/preview/index.html`; the earlier local preview remains preserved. All private operational evidence is under that production-resumption directory. See `reference-pins.json` for exact retained inputs and results.
