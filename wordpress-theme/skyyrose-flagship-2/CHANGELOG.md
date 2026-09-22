# Changelog

All notable changes to SkyyRose Flagship 2 are documented here.

## Unreleased — Home critical rendering repair — 2026-09-07

- Home inlines a source-derived structural critical contract
  (`assets/css/critical/home.min.css`, 15.8 KB, budget 16 KB) at `wp_head` so
  the header, hero stage, first-view typography, primary controls, concierge
  stage and rotating-mark container have their geometry before any external
  stylesheet arrives; independent of optimizer-generated critical CSS.
- Home prints the unchanged hero controller inline directly after the hero,
  ignored by script deferral, and drops its footer copy on the front page only;
  collection routes keep the enqueued controller.
- Home preloads the four first-view faces (Archivo, Hanken Grotesk, Anton,
  Cinzel) with hrefs equal to the `@font-face` URLs.
- New gates: `npm run check:critical`, `scripts/test-critical-rendering.php`,
  `tools/v2-runtime/verify-home-derived-output.mjs`,
  `tools/v2-runtime/measure-home-critical.mjs`,
  `tools/v2-runtime/verify-home-policies.mjs`.
- The hero controller binds collection rails once the document is parsed, so
  the inline Home copy (printed before the rail markup) no longer leaves the
  rail controls hidden; `verify-home-policies.mjs` now asserts the rail.
- The rotating header mark pauses while the document is hidden and resumes
  on return, matching the hero film's visibility policy.
- `scripts/deploy-theme.sh` ships only the `data/` files the package boundary
  marks `release: true` for this theme (founder rejection records, QA manifests
  and production contracts stay off the public theme directory) and refuses
  archive roots that are not shell-safe; the boundary now classifies every
  file of the pinned Home baseline.
- Browser tools resolve Playwright from the repository root install instead of
  one workstation path.

## Unreleased local V2 completion candidate — 2026-09-06

- Preserved approved hero, nine-scene, paid-card and character source assets.
- Scoped content and native Woo layout CSS to the routes that need them.
- Completed cart subtotal/extension hooks, touch controls and native error semantics.
- Repaired invalid spacing tokens, Account/Checkout/Cart shell spacing and long Search/About text reflow.
- Completed localized Skyy loading/failure states and the portrait-to-canvas handoff.
- Archived unreachable page drafts and excluded two protected authoring videos from distribution.
- Added native cart/notice and spacing regressions plus Chromium/WebKit route evidence.
- This candidate is local; mobile performance and production/founder release gates remain explicit.

## 2.4.0 — 2026-08-14

- Added an opt-in, idempotent marketplace demo importer under Appearance.
- Added nested collection, editorial, service, policy, and Journal page provisioning.
- Added WooCommerce shop, bag, checkout, account, and order-tracking classic page provisioning.
- Added safe primary/footer menu creation that preserves populated merchant menus.
- Added WordPress starter content, `theme.json`, editor styles, RTL support, and a POT catalog.
- Added deterministic product-presentation registry generation and freshness verification.
- Added deterministic CSS/JS minification, marketplace verification, and ZIP packaging commands.
- Documented the generated-artifact rule required for a reproducible clean checkout.

## 2.3.0 — 2026-08-03

- Established the isolated V2 collection-world and WooCommerce prototype surface.
