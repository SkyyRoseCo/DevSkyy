# SkyyRose V2 release candidate — 22 September 2026

**Decision: hold production release.** The staged theme is built, repaired, packaged and verified within the coverage below. It is ready for candidate review. Taking orders is not verified: staging has no enabled payment gateway, international destinations have no shipping method, and the intended tax configuration remains unresolved. No production deployment, payment, order submission, media generation, or customer communication was performed.

## Candidate identity and scope

- Review site: https://staging-7e48-skyyrose.wpcomstaging.com
- Source: `/Users/theceo/.codex/worktrees/v2-production-readiness/DevSkyy`, branch `codex/v2-production-readiness-20260922`, based on `2c7644772` with an explicitly recorded working snapshot.
- Selected existing V2 staging implementation from `abe0`; preserved its 58 changed/untracked theme and certification paths. The separate unfinished 2.5.0 redesign was not substituted.
- Theme: **skyyrose-flagship-2 2.4.4**. Staging: WordPress 7.1.2, WooCommerce 11.1.2, PHP 8.4.25.
- Archive: `../../wordpress-theme/skyyrose-flagship-2/dist/skyyrose-flagship-2.zip`.
- SHA-256: **ea9f7bfa15c4775ae4a9c743b6f4d88bde2a9c4a4deb85f741dbaf95d69a7998**.
- **563/563 package files match staging bytes.** Repeating packaging produced the identical checksum. `dist/release-manifest.json` pins each member and explicitly records `deployment_authorized: false` and the dirty source state.
- `evidence/inherited-paths.json`, `authority-import.json`, `candidate-source-manifest.json`, and `candidate-tracked.patch` describe the source snapshot. The branch name alone does not capture its uncommitted files. `candidate-source-overlay.zip` preserves all 89 changed source files, with a separate checksum.

The live storefront is the PHP/WooCommerce theme, not the separate Next.js dashboard. The complete theme release suite was run; this is not a claim that every unrelated FastAPI, dashboard, provider, or monorepo integration test passed.

## Gap matrix

| Area | Intended experience / validated state | Action and evidence | Release status |
| --- | --- | --- | --- |
| Frontend identity | Existing cinematic house homepage, moving product film, collection storytelling, editorial cards, journal/service pages, navigation, search, bag and quick view | Preserved current staging presentation. Desktop/mobile menu, search, Escape dismissal, bag and SG-005 quick view passed. `commerce-fresh.json` | Pass in tested Chromium flows |
| Product authority | One current founder-authoritative registry; 33 coherent product records | Reconciled the staging source checkout's obsolete registry with exact current `origin/main` authority at `6994d978579500e94e1571a223cc4aab70c60609`. Imported canonical readers, generated compatibility projections. All 33 products readable through `get_product`; registry sync check passes | Pass source consistency; no new founder facts invented |
| WooCommerce integration | Native variations, gallery metadata, cart/checkout hooks and accurate purchase states | Complete theme contract suite passes; live BR-003 size M adds to cart and reaches checkout at $100 + $17 standard shipping = $117. Core gallery override version 11.1.0 matches installed WooCommerce's file; notices version 8.6.0 matches | Pass to checkout, not transaction completion |
| Payments | Test purchase success/failure, order status, stock, refund and webhook reconciliation before live activation | All gateways disabled; Stripe mode is test. Checkout explicitly reports no available payment methods. Sandbox blocks email/webhook delivery | **Blocking: connect intended Stripe test account through WooCommerce, then validate transaction lifecycle in controlled scope** |
| Shipping | Supported destinations have intentional, verified rates | Read live U.S. zone: Standard $17, Express $22, free standard minimum $200. Catchall has no methods. Standard rate observed at checkout | **Decision required: confirm U.S.-only launch or provide international service/rate scope. Threshold and address matrix remain unverified** |
| Taxes | Deliberate configuration matching business requirements | Taxes enabled; stored rate count zero. This observation alone does not establish the appropriate tax treatment or external automated-tax behavior | **Decision/configuration review required before orders** |
| 3D / immersive | Black Rose, Love Hurts and Signature atmospheres load independently; shop links survive fallback | Fixed missing shared Three engine dependency in the world template. Regression failed before fix and passes after. **18/18 final browser profiles pass:** three worlds × desktop/mobile × normal/reduced/no-JS; normal reaches `three-ready`, reduced motion avoids Three imports, static links remain. No GLB downloads introduced | Pass tested scope; these are atmospheric scenes with commerce links, not a newly built fully navigable 3D store |
| Responsive / motion | Clear mobile/tablet/desktop layout, controllable film, static reduced-motion/no-JS paths | **9/9 final homepage profiles pass** at 390/768/1440 widths. Normal desktop retains animation; reduced motion disables it. No horizontal overflow or page errors. No-JS renders usable static content, with expanded navigation increasing page height | Pass tested emulation; physical iOS/Safari and Android review still open |
| Accessibility | Keyboard/dialog behavior, visible focus, adequate targets, semantic content, reduced motion | 80 public URLs × two widths = **160 initial states**: no navigation errors/overflow, one BR-004 mobile state had target-size violations. Three fresh same-route retests pass; intermittent result retained, cause not proven. Final homepage axe checks pass in all six JS-enabled profiles. Lighthouse accessibility 100 | Automated pass with recorded intermittent observation; **manual screen-reader review remains open** |
| Performance | Fast first view without sacrificing existing motion/media | Added high fetch priority to only the first original film image. Mobile lab score **79 → 96**, LCP **4.7s → 2.8s**, CLS **0 → 0**, TBT **30ms → 0ms**. Expanded critical CSS experiment exceeded the existing 16KB budget and was not retained | Improved; LCP still above 2.5s target. No field/Core Web Vitals claim; lab runs are variable |
| Source/build/deployment | Reproducible package and staging/source parity, controlled rollback | Added omitted launch-readiness and final-CSS guards plus new immersive regression to normal verification. Reconciled two stale unminified staging sources and POT line references; served minified assets already matched. Final package parity 563/563, deterministic repeat | Pass candidate integrity; production backup, environment preflight and explicit release approval still required |
| SEO | Staging protected from search indexing; production separately indexable | Lighthouse SEO 66 on noindex staging is expected and is not a production SEO approval. Theme SEO/indexing tests pass | Production canonical/indexing settings must be checked during approved release |

## Changes completed in this pass

1. `template-parts/immersive/world.php` explicitly enqueues the existing shared engine after the mascot loader and before immersive code, with content-based asset versions. The engine no longer depends on prior mascot interaction. Existing reduced-motion/static behavior remains intact.
2. `tools/v2-runtime/test-immersive-dependencies.php` executes the real template's enqueue phase and verifies dependency order, footer placement, asset identity and configuration. It reproduced the defect before repair.
3. `package.json` now runs that regression and the previously omitted launch-readiness/final-CSS guards during ordinary verification.
4. `template-parts/home/editorial-hero.php` gives the first original product-film image `fetchpriority="high"`; other film images remain `auto`. Product sources and animation behavior remain unchanged.
5. Current canonical registry/readers were reconciled into this release checkout and projections regenerated. `LogoRegistry` was also brought forward to satisfy the current single-entry-point reader. Historical presentation pin hashes remain historical provenance; they do not replace the current editable registry.
6. Staging source files now agree with the build inputs and generated runtime package. Changes were restricted to the verified staging host with expected-old/new hash checks and rollback copies.

## Verification actually run

- Complete `npm run package:theme`, including build and full `npm run verify`: exit 0. See `evidence/package-final.log`.
- JavaScript tests: **114 passed, 0 failed**. PHP syntax, marketplace, native commerce, media, source integrity, routing, critical CSS, token, SEO, frame, font and image-delivery guards all ran through that suite.
- Source-certification unit suite: **13 tests passed**. Pinned native fixture: WordPress 7.1 / WooCommerce 11.1.0. Live installed WooCommerce is 11.1.2; relevant override versions were checked independently on staging.
- Registry projection check: pass; all 33 single-entry-point reads succeed.
- Repeat packager: exact same SHA-256. `git diff --check`: pass.
- Public crawl: 160 states, with initial intermittent finding and targeted retests retained, rather than rewriting the baseline as clean.
- Commerce interactions: two widths passed. Actual checkout observed; **no order submitted**.
- Immersive final matrix: 18/18 passed. Homepage final matrix: 9/9 passed, including six axe runs.
- Lighthouse mobile final: performance 96, accessibility 100, best practices 100, SEO 66. See baseline and final JSON reports.
- Scrolled homepage image checks: 13 visible images at 390px and 16 at 1440px all loaded. Collapsed world content and inactive overlays are excluded using computed visibility; they are not mistaken for broken visible images. See `home-images-final.json` and `home-scrolled-*.png`.
- The synthetic cart item was removed after testing; the browser confirmed an empty cart.
- Canonical URLs temporarily served old cached HTML after updates. Final normal-URL browser retests received the expected assets and priority attribute. Neither cache flush nor HTTP 200 alone was treated as success.

## Platform decisions and authoritative references

- WordPress script dependencies determine load order. The fix uses the enqueue dependency graph instead of relying on an unrelated interaction to register an engine: [wp_enqueue_script reference](https://developer.wordpress.org/reference/functions/wp_enqueue_script/).
- WooCommerce classic themes should declare support, preserve hooks and track override compatibility. The existing support declaration and native contracts were inspected; versioned gallery and notice overrides were compared against installed core: [Classic theme handbook](https://developer.woocommerce.com/docs/theming/theme-development/classic-theme-developer-handbook), [outdated template guidance](https://developer.woocommerce.com/docs/theming/theme-development/fixing-outdated-woocommerce-templates).
- LCP images should be discoverable early and selectively prioritized. The first film image was the observed LCP element, so the change targets it rather than every product: [Fetch Priority](https://web.dev/articles/fetch-priority), [Optimize LCP](https://web.dev/articles/optimize-lcp).
- Staging identity and separate access were verified before mutation: [WordPress.com staging](https://wordpress.com/support/how-to-create-a-staging-site/).
- Payment validation belongs in a controlled test environment; test orders may trigger operational side effects. Existing staging delivery protections were preserved: [WooCommerce testing orders](https://woocommerce.com/document/managing-orders/testing-orders/).

## Approval and completion gates

The user approved this candidate for final checkout and manual acceptance testing in the conversation following delivery of this report. This records that approval within its stated scope; it is not production deployment approval. Before a production release request, resolve payment test access, supported shipping destinations and tax configuration; complete controlled success/failure/refund/order-state testing and manual assistive-technology/device review. Decide whether the 2.8s mobile lab LCP is acceptable for release or needs another measured optimization pass.

After those gates close, refresh this exact artifact's hashes, create/verify a production backup and rollback plan, inspect production plugin/settings compatibility and obtain explicit deployment approval. Do not push staging orders, users or database wholesale to production. Production approval has not been requested or inferred from the work completed here.

Staging rollback copies for this pass are under `/tmp/skyyrose-readiness-20260922/` on the verified staging SSH host: `world.rollback.php`, `hero.rollback.php`, and `parity-{0,1,2}.rollback`. The evidence logs identify the corresponding targets and hashes. These temporary copies are not a substitute for a durable production backup.


## Approved acceptance follow-up

The user replied “approve” to the recommendation to approve this candidate for final checkout and manual acceptance testing while holding production. That approval has been applied within that scope. The release archive remains unchanged at SHA-256 `ea9f7bfa15c4775ae4a9c743b6f4d88bde2a9c4a4deb85f741dbaf95d69a7998`.

Fresh automated acceptance testing passed in **Chromium at 390px and WebKit at 1440px**. Each run selected BR-003 size M, added it to the cart, verified $100 below the free-shipping threshold, changed quantity to reach exactly $200, observed free standard shipping, exercised the U.S. checkout, then changed the shipping destination to Canada and verified the no-shipping-options message. Menu dismissal using Escape also passed. Both runs had zero page errors and no horizontal checkout overflow. Both synthetic carts were explicitly cleared. No order was submitted. See `evidence/acceptance.json`, `acceptance.log`, and the two checkout screenshots.

Initial harness attempts were corrected to wait for variation availability, avoid requiring network idleness on a media-rich page, use the actual named remove control, and explicitly use the billing address for shipping before varying the address. The initial address attempt had altered billing while a separate shipping address remained selected; it was not evidence of incorrect shipping-zone behavior. Initial evidence is retained. The final harness is `checks/acceptance.cjs`.

The current stored settings independently confirm Stripe disabled, test mode on, all three standard test credential fields absent, all countries accepted, and the stored automated-tax setting off. No credential values were read into the report or printed. These are configuration observations, not proof of an authenticated Stripe connection. See `acceptance-config.json`.

The exact-$200 threshold behavior and the unmatched-destination response agree with WooCommerce's documented [free-shipping rules](https://woocommerce.com/document/free-shipping/) and [shipping-zone selection](https://woocommerce.com/document/setting-up-shipping-zones/).

**Updated remaining gates:** connect the intended Stripe test account in WooCommerce; confirm U.S.-only versus international launch and implement the corresponding country/rate settings; confirm the intended tax configuration; then test payment success/failure, order state, stock, refunds and relevant delivery/webhook behavior in controlled scope. Manual screen-reader and physical-device acceptance remain open. WebKit automation is additional browser-engine coverage, not a claim of testing a physical iPhone or the installed Safari application. Production remains unchanged.


## Founder launch-scope decision

The user explicitly selected **international launch**. The U.S.-only/international decision is closed. International destination coverage, rate calculation, delivery services, and any free-shipping scope still need an approved configuration. Existing U.S. rates must not be extrapolated to international destinations without that decision. This scope selection does not authorize production deployment or establish payment/tax readiness.


The staging shipping policy was read in the browser after the international decision. It already describes 40+ countries, dynamically calculated rates based on destination and package weight/dimensions, an estimated 10–14 business days after dispatch, and recipient-paid import duties/taxes. Free shipping at $200 appears in the domestic section. The policy does not name the 40+ countries or rate provider. The implementation gap is connecting an intended live-rate provider and defining the supported destinations; an invented international flat rate would not follow this policy. Policy wording is recorded as existing content, not proof of carrier configuration or legal/tax validation.


## International live-rate connection audit — 23 September

The user requested adding the international rate connection. Fresh authenticated staging inspection found only `flat_rate`, `free_shipping`, and `local_pickup` registered. Checked conventional Shippo, EasyPost, Easyship, ShipStation, UPS, USPS, FedEx and DHL settings were absent; this is scoped evidence, not proof that the business owns no external account. The installed WooCommerce Shipping/Services plugins do not supply new live checkout rates, per [WooCommerce Shipping documentation](https://woocommerce.com/document/woocommerce-shipping/).

All 33 published physical parent products currently have no positive shipping weight or complete dimensions in WooCommerce. The canonical product entry-point records expose no structured weight, parcel, packaging or shipping-package fields in the audit. Product artwork/garment dimensions must not be repurposed as packed shipping dimensions. Real-rate configuration needs the intended carrier/rating account plus approved item weights and packing data (or a fulfillment provider that owns those inputs). No account was connected, no subscription purchased, no invented flat rate or measurement saved, and production remains untouched. See `international-connection-audit.json` and `international-registry-measurement-fields.json`.


## Product-record preparation delegated

At the user's explicit request, the product-catalog agent was dispatched to prepare international shipping records for the existing 33 SKUs in the isolated release checkout. Its scope is canonical-registry records, single-entry-point exposure/gaps if needed, focused tests and a generated completion sheet. Missing weights and packed dimensions must remain null and discoverable; existing garment/artwork dimensions cannot substitute for parcel measurements. No duplicate WooCommerce products, carrier connection, live catalog mutation or production deployment is authorized by this delegation. Delivery and validation remain pending until the agent returns.


## Product shipping records delivered and reviewed

The delegated product-record task is complete in the isolated release checkout. All33 existing canonical product records now include a shipping section: item weight (g), packed parcel weight (g), packed length/width/height (cm), and packaging reference. All six unknowns remain null for each SKU: **198 named gaps**, exposed through `get_product`. Item weight excludes packaging; the parcel record describes one sellable unit, not a multi-item packing algorithm. No measurements or founder facts were invented.

Parent and independent Python review both confirmed all pre-existing product facts match the preserved baseline exactly. Five focused tests passed, as did Ruff, scoped mypy, Black, registry projection consistency, and diff checks. Tests cover unknown and populated fixtures, idempotence, preservation and rejected malformed/zero/negative measurements or unsupported units. Final reviewer verdict: no remaining actionable findings.

See `product-shipping-records/REPORT.md`, `completion-sheet.csv`, and `shipping-records.json`. Those exports are generated consumers; registry updates remain authoritative. The source overlay/manifest were refreshed to89 changed source files. The approved theme ZIP remains unchanged. This task did not alter live WooCommerce products, connect a carrier account, deploy or buy anything. Actual measurements and the intended live-rate integration still block international checkout rates.
