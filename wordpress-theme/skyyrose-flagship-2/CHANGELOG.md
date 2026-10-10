# Changelog

All notable changes to SkyyRose Flagship 2 are documented here.

## 2.5.1 — Search discovery, consented analytics, express-checkout dedupe — 2026-10-10

- Express checkout: when WooPayments renders express checkout, every callback
  the Stripe express-checkout instance registered on the three WooCommerce hooks
  is removed (walked by object identity, not by guessed priority), so the
  buttons no longer render twice (#1017).
- Analytics: consented analytics is integrated into the theme with its package
  certification reconciled; acknowledged events are projected idempotently.
- Catalog: founder material specifications recorded for 21 products; technical
  drawings are kept out of physical-reference renders.
- Search discovery (details below): sitemap, metadata ownership, no-tagline.

### Search discovery: sitemap, metadata ownership, no-tagline

- Sitemap: robots.txt advertises `/wp-sitemap.xml` only when native sitemaps
  resolve (Jetpack's Sitemaps module disables them and serves `/sitemap.xml`
  itself, so the native line was a 404). The Jetpack sitemap now lists every
  WooCommerce product and skips the same records the native sitemap skips: cart,
  checkout, account, wishlist, and every retired route that 301s to its V2 page
  (`collection-*`, `landing-*`, `collections-world`). The native users (author)
  sitemap is dropped. `scripts/validate-sitemap.py <sitemap-url>` checks a live
  sitemap against Google's requirements.
- Metadata: while the theme renders description/Open Graph/Twitter tags,
  Jetpack's Open Graph tags, SEO-tools meta description, and SEO custom titles
  are switched off (they duplicated every tag and replaced `<title>` with
  per-page SEO-tool titles). A supported SEO plugin still takes over everything.
- No tagline: the WordPress "Tagline" option is never used as a fallback
  description; absent copy omits the tag instead.
- Plain-permalink pagination canonicals keep the parameters that identify the
  archive (`post_type`, `cat`, `tag`, `taxonomy`/`term`, author, date) beside
  `paged` and drop tracking/cache-buster parameters.
- A record marked noindex in Jetpack SEO Tools keeps its `noindex` robots tag
  although Jetpack's own meta output is switched off.
- Jetpack's image sitemap skips images attached to the excluded pages (the
  attachment's parent is tested, not the attachment).
- Canonical: paginated archive canonicals drop request query parameters;
  CollectionPage schema omits `primaryImageOfPage` when no hero resolves.

## 2.5.0 — Whole-site editorial redesign — 2026-09-22

- Every route now follows one composition: a full-bleed cinematic arrival with a
  single focal point, editorial chapters (16:9 scene → copy/commerce band, 3:2
  on phones), then a quiet colophon. Shared primitives (`.sr2-arrival`,
  `.sr2-chapter`, `.sr2-band`, `.sr2-title-*`, `.sr2-lede`,
  `.sr2-editorial-link`) live in `theme.css`; page sheets compose them.
- Shell: header drops to 64px with a smaller mark and Hanken links, floats over
  cinematic arrivals until scroll; Cinzel is reserved for engraved index labels;
  controls and WooCommerce buttons move to Hanken; footer wordmark is type, not
  Cinzel.
- Home: Bay Bridge arrival (founder-approved motion, wordmark low-left, one
  primary action, four-world index strip), on-model film band (SG-005, BR-004,
  LH-004, KIDS-001), four collection chapters with the approved monument scenes
  and unframed garment cards, the worlds rail on an open band, founder portrait
  kept as a portrait, journal films at native 16:9. `editorial-product-edit.php`
  removed. Critical CSS rebuilt from the new hero (13.3 KB of the 16 KB budget).
- Skyy (founder direction 2026-09-22): the header and menu carry no mascot. Skyy
  mounts in a footer-rendered walk-on dock on every non-checkout route and is
  the chat entry; a recall pill appears only after dismissal. Natural-motion rig
  tiers ship (`skyy-natural-desktop.glb` 2.1 MB / `skyy-natural-mobile.glb` 1.2
  MB; clips Idle/Walk/Talk/Joy/Exit/Wave) via `SKYY_3D_CONFIG.mobileModelUrl`.
  The previous `skyy-mascot.glb` remains in the tree pending founder removal.
- Shop, product, collection, immersive, cart/checkout/account and content pages
  recomposed to the same system; product cards accept `'frame' => false` and
  grids ship without portal frames.
- Tests: shell contract asserts the dock instead of the header pin; critical
  rendering pin moves from `.sr2-archive-scene__concierge` to `.sr2-arrival`.

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
- The hero controller binds collection rails once the document is parsed, so the
  inline Home copy (printed before the rail markup) no longer leaves the rail
  controls hidden; `verify-home-policies.mjs` now asserts the rail.
- The rotating header mark pauses while the document is hidden and resumes on
  return, matching the hero film's visibility policy.
- `scripts/deploy-theme.sh` ships only the `data/` files the package boundary
  marks `release: true` for this theme (founder rejection records, QA manifests
  and production contracts stay off the public theme directory) and refuses
  archive roots that are not shell-safe; the boundary now classifies every file
  of the pinned Home baseline.
- Browser tools resolve Playwright from the repository root install instead of
  one workstation path.

## Unreleased local V2 completion candidate — 2026-09-06

- Preserved approved hero, nine-scene, paid-card and character source assets.
- Scoped content and native Woo layout CSS to the routes that need them.
- Completed cart subtotal/extension hooks, touch controls and native error
  semantics.
- Repaired invalid spacing tokens, Account/Checkout/Cart shell spacing and long
  Search/About text reflow.
- Completed localized Skyy loading/failure states and the portrait-to-canvas
  handoff.
- Archived unreachable page drafts and excluded two protected authoring videos
  from distribution.
- Added native cart/notice and spacing regressions plus Chromium/WebKit route
  evidence.
- This candidate is local; mobile performance and production/founder release
  gates remain explicit.

## 2.4.0 — 2026-08-14

- Added an opt-in, idempotent marketplace demo importer under Appearance.
- Added nested collection, editorial, service, policy, and Journal page
  provisioning.
- Added WooCommerce shop, bag, checkout, account, and order-tracking classic
  page provisioning.
- Added safe primary/footer menu creation that preserves populated merchant
  menus.
- Added WordPress starter content, `theme.json`, editor styles, RTL support, and
  a POT catalog.
- Added deterministic product-presentation registry generation and freshness
  verification.
- Added deterministic CSS/JS minification, marketplace verification, and ZIP
  packaging commands.
- Documented the generated-artifact rule required for a reproducible clean
  checkout.

## 2.3.0 — 2026-08-03

- Established the isolated V2 collection-world and WooCommerce prototype
  surface.
