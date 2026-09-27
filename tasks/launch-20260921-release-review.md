# SkyyRose staging red-team release review — 2026-09-21

## Scope and identity

Target: `https://staging-7e48-skyyrose.wpcomstaging.com`, active `skyyrose-flagship-2` 2.4.4. Matching runtime checkout: `/Users/theceo/.codex/worktrees/abe0/DevSkyy`, baseline HEAD `2c7644772`. The main checkout has a different, older homepage implementation and unrelated dirty work; it was not used to overwrite staging.

Current product authority remains `/Users/theceo/DevSkyy/logo-registry.json` (symlink to the original theme's unified registry). Founder product facts remain authoritative. No old catalog projection was promoted. Main registry compatibility check passed. This patch changes presentation and delivery only; it does not change product facts, attachments, prices, payments, or the approved image pixels.

## Changes prepared

- Editorial hierarchy: refined hero type and copy. Founder explicitly requires centered desktop and mobile alignment across pages. Source now centers hero hierarchy, shop navigation, service/account links and the product collection eyebrow; existing centered page/product headings are preserved. The combined followup is deployed on staging; final viewport checks are complete for the routes and widths recorded in `tasks/evidence/final-visual-qa-20260921.md`.
- Shop uses one column below 480px with corresponding responsive image hints; larger layouts preserved.
- Contact keyboard focus and service/account touch targets strengthened.
- FAQ visible text and structured data use the same maintained content, avoiding stale unsupported database claims.
- Five ghost-primary PDPs (BR-002, BR-005, KIDS-002, LH-003, SG-014) use existing exact-SKU approved model fronts. Initial render, variation data, native gallery regeneration and reset are covered. All 33 approved fronts retain source hash checks.
- No JavaScript or motion source changed. The critical stylesheet remains within its original 16,384-byte ceiling.
- Translation source references regenerated; no translation message changed.

## Staging settings already repaired

The founder selected published rates and the $200 threshold. US zone1 now has Standard $17, Express $22, and Free standard at $200 after discounts. Synthetic Woo cart evidence verifies standard/express at $100 and free/standard/express at $200. See before/after JSON in `tasks/evidence/`.

Cookie-policy links now resolve to Automattic, PayPal and TikTok's available destinations. An invalid legacy `template-policy.php` metadata reference was reset to `default` after backup; page identity and content were preserved, with public HTML byte-identical before/after the metadata repair.

## Verification boundaries

83 unique internal clean paths returned HTTP200 without observed PHP fatal output. Four collection filters resolved. This is HTTP routing evidence, supplemented by browser journey checks; it is not a claim that every external provider will remain available. The external DAA opt-out endpoint returned429 and remains externally rate-limited.

Before patch, browser checks exercised desktop/mobile navigation, quick view, variation selection, add to cart, quantity update, invalid coupon, checkout staging notice and empty-cart cleanup. No order or payment was submitted.

Native Woo11.1.1 gallery helper/template files on staging match the pinned11.1.0 fixture bytes. WordPress7.1.1 has core hook-file patch drift versus the7.1 fixture; postpatch staging browser checks remain required.

Runtime hash baseline changes have explicit before/after lineage in `tasks/evidence/runtime-baseline-lineage-20260921.json`. Scene, motion, product and approved image hashes were not relaxed.

## Decisions remaining before accepting production orders

- Payment execution is explicitly deferred to production by the founder. Sandbox remains unchanged. The production gateway and a controlled transaction/refund still need post-cutover verification.
- Tax calculation ownership/setup is not yet confirmed. Tax is enabled, base rates are empty, and no active automatic-tax integration was observed. No tax obligation or rate was invented.
- Published international delivery language exceeds configured coverage: catch-all zone has no methods. Carrier/rate setup or a founder-approved launch-country policy is needed.
- Formal refund policy promises prepaid US labels/free US exchanges, while the service summary describes replacement availability case by case. The operating promise needs reconciliation by the merchant.
- Main registry image roles for BR-002, BR-005 and KIDS-002 were corrected via the registry update API to exact copies of the already-approved model fronts. Existing differing image files were preserved under their original paths. `get_product()` resolves the corrected roles and compatibility sync check passes.

Production has not been deployed. The runtime ZIP captures the reviewed theme candidate, with an exact file manifest. Historical catalog projections in this checkout must not be used to synchronize or overwrite production product facts; the current unified main registry remains authoritative. The ZIP does not authorize deployment or perform a WooCommerce catalog sync.

## Applied patch and local verification

The first 18-file patch was deployed to staging after all remote pre-change hashes matched the source baseline. Every post-change hash matched the candidate. Rollback archive and manifest are under `tasks/evidence/`. `wp cache flush` succeeded; cache-group flushing is unsupported on this host, so no full-page cache purge is claimed. Fresh verification uses unique query parameters.

Full `npm run verify` passed with Node22.23.2, npm10.9.8, Python3.12.12, Pillow12.3.0, fonttools4.59.2 and brotli1.2.0. Pinned fixture dependencies were fetched from the official WordPress/WooCommerce archives and hash-checked. The isolated verification environment does not alter the main project environment.

Postpatch HTTP inspection: all 33 published product pages returned200 and contain their primary image. Five existing approved fallback presentations use a different DOM structure than native galleries; the audit explicitly accounts for those rather than treating an absent `.wp-post-image` selector as a missing photo.

## Image performance followup

Five approved fallback PDP views had only an original 1024px image URL. They now use existing same-source 320/480/768px derivatives plus the original in `srcset`, with contained-gallery responsive sizes. Their original files total 1,132,782 bytes; the 480px derivatives total 348,896 bytes (69.2% smaller), and 768px total 771,682 bytes (31.9% smaller). These are potential file-byte savings across five distinct images, not a measured page-load speed or a claim that every browser selects 480px. No source image pixels or animation assets were regenerated.

PDP size hints are corrected to final CSS heights: mobile `clamp(20rem,52svh,30rem)`, desktop `clamp(28rem,64svh,44rem)`, scaled by each image aspect ratio for `object-fit:contain`.

## Reusable marketplace foundation

`page.php` now composes `template-parts/pages/service.php` for generic, service, FAQ and account shells. Its explicit input contract preserves managed FAQ filtering/sanitization and native WordPress/Woo content. The section test covers FAQ, ordinary pages, non-FAQ service pages and account rendering, including exact content call counts and service-link boundaries. It is wired into `npm run verify`, as is the approved-front integrity/fallback regression.

The page-by-page map is `tasks/launch-20260921-marketplace-template-map.md`. Contact and collections-index extraction remain subsequent work, while existing home, collection worlds, product cards, pre-order, About and lookbook already compose reusable parts. No external marketplace approval or full package certification is claimed.

## Final staged candidate

The 17-file followup is installed, including the new service template, centered alignment and hash-bound responsive images. All pre-install guards and post-install hashes passed. Both canonical and fresh URLs returned 200 for 12 checked routes; canonical BR-002/BR-003 markup exposes the final responsive candidates and 52svh/64svh size hints. Final FAQ exposes exactly the three maintained questions.

The final full verification chain passed, including 114 JavaScript tests and both new PHP regressions. The runtime packager classified every theme file and verified 558 ZIP entries and their SHA-256 values. Candidate: `wordpress-theme/skyyrose-flagship-2/dist/skyyrose-flagship-2.zip`; SHA-256 `e1a35cc901854714f471e1256e6f2aa60a4610788c07f033a65f7cc65f67ce5d`. Its manifest records the dirty source state and does not grant production authorization.

The founder approved removal of the synthetic cart item at action time; BR-002/M/quantity 4 was removed and Bag 0/empty cart were confirmed. No payment or order was created.

## Final visual closeout and isolated packaging followup

Terra completed final browser checks: home at 1440/390/320px, shop and account at 390px, desktop BR-003, FAQ, BR-002 variation/reset, and sequential mobile collections index, Signature world, About, Journal, Contact and Shipping & Returns. No alignment/clipping defect was observed in those paths. Live pause/play motion and collection controls remained available. This is the measured scope, not a claim of every page at every viewport or payment completion.

Sol completed the separately authorized packaging candidate in `/Users/theceo/.codex/worktrees/marketplace-split/DevSkyy`. Its 173-file core and 385-file required-media packages reconstruct the exact 558-file verified runtime bundle. Optional demo content is empty. Deterministic rebuild, integrity/rejection/rollback tests and independent security review passed according to the saved agent report. No split package was deployed. Marketplace acceptance, media redistribution licensing, independently authenticated release hash publication and clean WordPress installation acceptance remain separate gates. See that checkout's `tasks/marketplace-split-20260921.md` for evidence.
