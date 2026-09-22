# V2 prelaunch audit and remediation — 2026-09-21

Status: source remediation validated locally; hosted PR validation pending. **Go-live remains blocked** by untested payment completion and operational release checks below. A merge is not a deployment or acceptance of those gaps.

## Identity and evidence

- Repository: SkyyRoseCo/DevSkyy; isolated branch `codex/v2-prelaunch-audit-20260921`, based on main `7c2b97cb50266d10c88b5f84606bc78b1a01e0b6`; PR [#964](https://github.com/SkyyRoseCo/DevSkyy/pull/964).
- Audited staging: https://staging-7e48-skyyrose.wpcomstaging.com (WordPress.com site 256563697). An authenticated connector read confirmed active stylesheet `skyyrose-flagship-2`. Subsequent browser/API tests were anonymous. No credentials or customer data are included.
- The original working checkout did not match staging. Eight sampled served CSS/JS hashes match the V2 source in worktree `abe0`, HEAD `2c7644772be1d19c9218ebfb2b980350033b83f7`, including its uncommitted source. The source manifest records exact imported bytes; this is sampled parity, not proof of every deployed file.
- Imported scope: V2 theme, its runtime/certification tools, and two hash-bound existing scene receipts. Current main's registry was retained. No deployment, purchase, email send, webhook dispatch, or provider generation occurred.
- Evidence types: source inspection; reproduced offline tests; anonymous staging browser/API observations; authenticated site/theme identity read. Historical scene approval records preserve provenance and do not grant a new release authorization.

## Findings and fixes

| Finding | Severity | Remediation / evidence |
| --- | --- | --- |
| Original checkout was not the staged V2 source | High | Recover exact candidate in an isolated main-based worktree; source manifest and sampled asset parity retained. |
| PostCSS 8.5.6 build dependency vulnerabilities | High | Pin 8.5.28 in package/shrinkwrap/toolchain declaration; full npm audit reports 0 vulnerabilities. |
| User-Agent rotation bypassed contact throttle | Medium | Bucket uses HMAC of server REMOTE_ADDR; untrusted headers cannot reset it. Regression checks distinct addresses, no raw IP exposure, UA/forwarded invariance. |
| FAQ template and schema suppressed merchant content | Medium | Native authored page content and schema parse the same current post; regression verifies merchant FAQ survives. |
| Demo repair could overwrite existing merchant template | Medium | Require theme ownership and recognized default/theme template; preserve custom templates and repeat-import idempotency. |
| Historical product snapshot still controlled current routing | Medium | Read current product facts and merchandising through get_product; migrate exact existing routing assignments into canonical registry with ROUTE_CONFIGURATION provenance. Historical snapshot remains media receipt identity. |
| Registry updater could persist duplicate series positions | High | Validate whole final batch before atomic save; tests reject collision without changing bytes and allow position swaps. |
| Registry schema omitted newly canonical merchandising | Medium | Hosted Catalog Consistency Validation caught missing schema fields. Add strict assigned/unassigned route and provenance definitions, require paired records, retain unknown-key rejection; 34 focused registry/presentation tests and Python static checks pass locally. |
| Homepage display typography used ceremonial face broadly | Design | Use brand Archivo display role; verify 390/768/1440px preview, no overflow or automated axe violations. Original visual product assets preserved. |
| Measured homepage LCP image lacked priority | Performance | Prioritize original first film image; keep duplicated loop images lazy. No claim of post-deployment performance improvement yet. |
| Retired related/upsell/cross-sell modules could surface | Design / commerce | Remove their native WooCommerce hooks while preserving cart/checkout hooks. |
| WebKit collection mobile overflow | Medium | Position the scroll rail as the containing block. Browser verification retains all three cards and horizontal rail scrolling without page overflow at 390/1440 in WebKit and Chromium. |

## Coverage and results

| Area | Executed checks | Result / limitation |
| --- | --- | --- |
| Marketplace/package | PHP syntax, required templates/docs/license/screenshot, version consistency, translation extraction including plural record, retired-font and placeholder scans, explicit package allowlist and ZIP byte verification | V2 verify PASS; 566 runtime archive entries at initial packaging. Marketplace acceptance and third-party asset rights are not independently certified. |
| Source/build | Pinned Node 22.23.2/npm 10.9.8/Python 3.12.12/Pillow 12.3.0; regenerate CSS/JS, registry, fonts, responsive assets and POT; negative integrity tests | Complete build and verify passed. Final full build/verify/package PASS; 17 certification tests and 114 JavaScript tests PASS. Hosted repeat-build comparison pending. |
| Fashion/visual | Brand typography and collection identity reviewed against `.impeccable.md`, canonical typography JSON and approved design references; homepage/collection/PDP desktop/mobile screenshots | Product-led imagery, collection distinction, navigation and mobile composition inspected. Candidate CSS preview is explicitly separate from deployed PHP. Founder acceptance is not inferred. |
| Navigation/links | 24 desktop route checks and 7 mobile checks; 66 same-origin navigational links | Valid routes 200, intentional missing route 404; account endpoints returned crawler 429 while browser account route passed. No actual dead route established by those rate limits. |
| JavaScript/resources | Chromium page errors and resource failures on sampled routes | No page errors or unexpected >=400 resources in baseline route sweep. Hidden dialog image placeholders with empty src were excluded from broken-image findings. |
| Accessibility | Axe WCAG A/AA tags on home and six representative commerce/content routes; mobile menu open/Escape close; reduced-motion rendering | No automated violations observed. Does not establish complete WCAG conformance, screen-reader usability or all keyboard states. |
| Browser support | Chromium desktop/mobile plus WebKit mobile smoke | WebKit identified overflow; later settled Chromium reproduced it too. Local candidate CSS resolves both while preserving rail scrolling. Real iOS device and full Firefox/assistive-tech coverage remain unverified. |
| Commerce | Public Store API 33 products; select BR-004 size M, add variation 10507, wait for success, cart and checkout | Native add success, 1 item/$40; displayed standard shipping $17 and total $57 in test session. No order submitted. Shipping/tax correctness for every destination not certified. |
| Checkout/payment | Checkout form loads; explicit staging safety notice inspected | Payment disabled until Stripe test credentials connected; no available method. Payment, decline, duplicate webhook, refund and receipt email paths NOT VERIFIED. |
| API/security | Store API read, nonce/sanitization/capability source inspection, contact throttle regression, dependency audit, response headers | HSTS/nosniff/frame/CSP present on staging. No authenticated authorization penetration test or full backend API/load test performed. |
| SEO | Titles/canonical/404/FAQ schema; robots headers | Staging noindex/nofollow/noarchive intentionally retained. Production indexability, sitemap and search-console acceptance require environment release checks. |
| Performance | Lighthouse mobile staging home | Performance 61, accessibility 100, best practices 100, SEO 66; LCP 5.2s, TBT 540ms, CLS 0, FCP 1.7s. Lab baseline, not field p75. Staging noindex affects SEO; plugin/host bundled scripts consume significant main-thread time. |
| Product/media authority | Current canonical registry, projection sync check, all 33 front hashes/dimensions, nine scene casts and media bindings | Existing founder facts unchanged; no replacement creative generation. Historical stale/rejected media labels are preserved media evidence, not judgments on maker specifications. |
| Operations/resilience | Release manifest, explicit artifact allowlist, independent reviews, CI gates, deployment boundary | Backup restore, rollback on target host, alert delivery, credentials/webhooks, privacy retention and real transactional mail remain NOT VERIFIED. No legal certification claimed. |

## Launch gates still requiring target-environment evidence

1. Configure the intended staging test gateway and complete success/decline, retry/idempotency, order inventory, refund, tax/shipping and transactional receipt tests. Preserve staging mail/webhook isolation until authorized test destinations are ready.
2. Deploy the reviewed artifact only with explicit release approval, verify served-file identity, repeat affected browser/accessibility flows and measure mobile performance. LCP target is <=2.5s at field p75; current 5.2s lab baseline does not satisfy that standard.
3. Verify production indexability/canonicals/sitemap, cache exclusions for cart/checkout/account, gateway environment, secrets scope, backup restoration, rollback and monitoring/alert delivery. Obtain final visual/commerce acceptance.

These are coverage gaps or environment blockers, not passing checks. The code can be reviewed and merged while the launch remains blocked.

## Broader repository dependency risk

An authenticated GitHub Dependabot inventory on 2026-09-21 returned 284 open
repository alerts: 13 critical, 104 high, 137 medium and 30 low. The affected
manifests were root `uv.lock` (112), `agents/devskyy-a2a/uv.lock` (81),
`frontend/package-lock.json` (70),
`design-system/skyyrose-storefront/package-lock.json` (15),
`devskyy-sdk-app/uv.lock` (4) and root `package-lock.json` (2). No affected
manifest in that inventory belongs to the V2 theme. Critical findings include
anyio, litellm, GitPython, nltk, next and next-auth. These are repository-wide
risks requiring separate dependency and deployed-reachability triage; the V2
theme's zero-vulnerability npm audit does not establish repository-wide safety.

A bounded V2 runtime source scan found same-origin HTML requests for quick-view
and search, plus model asset fetching; it did not establish direct FastAPI
coupling or custom PHP REST/AJAX/outbound HTTP handlers. That source observation
does not establish the absence of exploitable deployed services or plugins.

## Reproduction

Use the declared toolchain and requirements in `tools/v2-source-certification/README.md`; prepare the hash-pinned WP/Woo native fixture with `prepare-native-fixture.py`, set `V2_WP_FIXTURE`, then run theme build/verify/package. CI repeats packaging and compares archive bytes. Focused tests cover `tests/test_product_merchandising.py`, `tests/test_v2_product_presentation_registry.py`, and certification tests. Native template fixture tests exercise real pinned template/hook files with mocked data; they are not a full hosted WordPress install.

## Verified reference sources

Checked 2026-09-21. These establish review criteria, not proof that this site passes them:

- [WordPress theme release handbook](https://developer.wordpress.org/themes/releasing-your-theme/): release preparation and review expectations.
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/): accessibility criteria; automated scans cover only part of conformance.
- [Core Web Vitals thresholds](https://web.dev/articles/defining-core-web-vitals-thresholds): LCP, INP and CLS targets and p75 field interpretation.
- [WooCommerce cart and checkout theming](https://developer.woocommerce.com/docs/theming/block-theme-development/cart-and-checkout): native commerce integration context; this theme's actual classic templates were separately tested.
- Local source authorities: `.impeccable.md`, `wordpress-theme/skyyrose-flagship/data/brand/typography.json`, `docs/brand/visual-references.md`, canonical `logo-registry.json`.

## Independent review

PHP/source reviewer confirmed original defect fixes; Python reviewer approved canonical migration after collision fix, with focused tests and static checks. JavaScript reviewer approved the reviewed commerce, navigation, motion and build scope; 114 behavioral tests passed. Reviews are bounded source assessments; they do not certify deployment or live payment execution.

Local final package: 566 runtime entries, SHA-256 `db2f56e5f778e37074036fcfab633efca8f7fd664a5407f298c0d89aa37b2f7b`. The saved manifest explicitly reports a dirty precommit source tree; it is local test evidence, not a clean release receipt.
