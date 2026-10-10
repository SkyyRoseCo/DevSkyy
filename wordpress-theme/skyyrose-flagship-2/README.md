# SkyyRose Flagship 2

SkyyRose Flagship 2 is a WooCommerce-first, Oakland-rooted luxury streetwear
theme. The presentation layer combines collection-specific editorial worlds,
accessible commerce controls, and progressive cinematic enhancements while
WooCommerce remains the sole authority for products, variations, price,
inventory, cart, checkout, customer, order, and payment state.

## Install

1. Upload the `skyyrose-flagship-2` folder or packaged ZIP in **Appearance → Themes**.
2. Install and activate WooCommerce before importing the store structure.
3. Activate SkyyRose Flagship 2.
4. Open **Appearance → SkyyRose V2 Setup**.
5. Select **Import SkyyRose V2 demo structure** once.
6. Import or synchronize the authorized product catalog through your separate
   WooCommerce catalog workflow. The theme importer deliberately creates no
   products and invents no inventory.
7. Assign payment, tax, shipping, email, privacy, and policy settings for the
   merchant and jurisdiction before accepting orders.

The importer is idempotent. It reuses exact existing page paths, never deletes
content, never overwrites merchant-authored pages, and never replaces a menu
that already contains items. If WooCommerce is inactive, commerce pages are
skipped with a warning and can be provisioned by running the importer again.

## Imported route structure

- `/` — House homepage
- `/collections/` — collection index
- `/collections/signature/`
- `/collections/black-rose/`
- `/collections/love-hurts/`
- `/collections/kids-capsule/`
- `/worlds/signature/`, `/worlds/black-rose/`, `/worlds/love-hurts/`, `/worlds/kids-capsule/`
- `/pre-order/`, `/about/`, `/contact/`, `/journal/`, `/wishlist/`
- `/faq/`, `/shipping-returns/`, `/size-guide/`
- `/privacy-policy/`, `/terms-of-service/`, `/accessibility/`
- WooCommerce shop, bag, checkout, account, and order-tracking pages

## Product and asset authority

- Product facts and product media resolve from WooCommerce and the authorized
  SkyyRose SOT pipeline. The theme never manufactures a product fallback.
- `data/product-presentation-registry.json` is a generated, non-commercial
  adapter. It classifies Jersey Series SKUs as the dedicated Black Rose
  release presentation (`/collections/black-rose/#jersey-series`) while keeping
  their Town Line art direction separate from core Black Rose cards. It contains
  no prices, stock, WooCommerce IDs, or product media.
- Theme-local editorial assets require candidate-bound provenance. A file path
  alone is not proof of product identity or usage rights.

## Build contract

Production uses generated `.min.css` and `.min.js` siblings. Edit source files,
then rebuild and verify byte parity:

```bash
npm ci
npm run build
npm run verify
npm run package:theme
```

`npm run package:theme` performs the build and verification again before it
creates the distributable ZIP. `npm-shrinkwrap.json` pins the build-tool graph
for clean-checkout reproducibility; the package itself ships the generated
assets and does not require Node.js at runtime.

`npm run verify` checks PHP syntax, JSON, presentation-registry freshness,
minified-asset parity, required marketplace artifacts, placeholder markers,
and retired fonts. Generated minified artifacts must be force-tracked by the
release integrator because the repository’s global ignore policy excludes
`*.min.css` and `*.min.js`; a clean checkout is not release-ready without them.

## Home critical rendering and release parity

The front page inlines a theme-owned structural contract
(`assets/css/critical/home.min.css`, built by `npm run build:critical` from the
enqueued source sheets under `assets/css/critical/home.contract.json`) and prints
the unchanged hero controller inline directly after the hero markup with
`data-jetpack-boost="ignore"`. The contract is independent of any
optimizer-generated critical CSS: Jetpack Boost's block is derived from a
script-less render, is stored per URL, and is only invalidated by a theme
switch, so a same-theme file deployment never refreshes it. The theme's block
is derived from source bytes at build time and ships with the theme.

A release is complete only when every layer below is verified, in order:

1. **Source artifact** — `npm run build && npm run verify` on the frozen
   candidate (`check:critical` fails on a stale or over-budget contract).
2. **Filesystem parity** — the deployed theme tree hashes equal the candidate
   (deploy script post-swap verification).
3. **Generated critical CSS parity** — the delivered Home `<head>` carries the
   candidate's `#skyyrose2-critical-home` byte for byte, the four first-view
   font preloads, and the inline hero bootstrap before the classic body chain:
   `node tools/v2-runtime/verify-home-derived-output.mjs --base=https://host`.
   If an optimizer block is also present, regenerate it from the optimizer's
   admin after the deployment; the theme contract does not depend on it.
4. **Managed bundle parity** — served theme CSS/JS files match the local build
   (same script, sha256 per file; optimizer concatenation is derived from them).
5. **Browser parity** — `node tools/v2-runtime/measure-home-critical.mjs` at
   320/390/414/768/1440 (CLS ≤ 0.1, first-paint and settled screenshots, hero
   startup timings) and `node tools/v2-runtime/verify-home-policies.mjs`
   (no-JS, reduced motion, Save-Data, visibility, pause/play, commerce journey).
   Both browser tools resolve Playwright from the repository root install
   (`npm install` at the repository root), falling back to `DEVSKYY_ROOT` or the
   primary `~/DevSkyy` checkout; without any install they print
   `UNVERIFIED: playwright not installed` and exit 3.

## Customization

`theme.json` exposes the canonical SkyyRose palette, spacing, and type roles in
the editor. Archivo is the text display face, Hanken Grotesk is body, Anton is
utility, and Cinzel is restricted to ceremonial metadata. Collection names in
cinematic heroes remain approved lockup images rather than type-rendered
wordmarks.

The editor loads `editor-style.css`. WordPress loads `rtl.css` for right-to-left
locales. All front-end motion must preserve native scrolling, keyboard access,
reduced-motion equivalence, and a static failure path.

## Marketplace handoff gates

Before distribution, verify the same frozen candidate at 390, 768, and 1440
pixels; run keyboard and assistive-technology journeys; validate WooCommerce
simple and variable products, cart mutations, checkout failures/recovery,
account ownership, and empty/error states; run Lighthouse; confirm every
product image against its SKU pixels; and review starter policy copy with the
merchant’s legal adviser.

No deployment, catalog write, media upload, or payment configuration is part of
the theme package.

## V2 completion candidate: ownership and delivery

The shared shell and control styles remain global. About, Contact and reservation
compositions live in `assets/css/content-page.css`, loaded on the same conservative
content/legacy route boundary as `legacy-world-components.css`. Home, the four
editorial collections, Shop/taxonomy and PDP do not load this content stylesheet.
When moving a component, preserve responsive rules and split mixed selector lists
so a later route stylesheet cannot accidentally override its own mobile rules.

Home and the four enabled editorial collection pages render theme-owned product
cards, Quick View and bag markup. They omit WooCommerce's general/layout/smallscreen
styles while keeping its scripts, native fragments and product authority. All
transactional pages, Shop, taxonomy, PDP, ordinary content and legacy immersive
routes retain native Woo styles. An extension adding native Woo layout to an
editorial page can retain the styles with:

```php
add_filter( 'skyyrose2_editorial_native_woo_styles', '__return_true' );
```

Cart item prices, subtotals, quantity controls, remove links, backorder notices and
item-name/coupon hooks follow the native extension contracts. The native error
notice override retains `.woocommerce-error` on an alert container and places a
semantic list inside it. Keep the native escaping and data attributes when updating
that override against WooCommerce's template version; do not replace the alert with
a generic list live region. Cart and Checkout route shells reserve space for notices
before their forms, including the fixed-header clearance after native error focus.

Ask Skyy uses one model and canvas. The approved portrait stays still during the
canvas opacity handoff; loading, failure, reduced-motion and Save-Data messages are
server-translated. A failed guide script preserves the native Contact destination.
The current model and physical gait are preserved; deeper Blender production and
the final Town Line Pre-Order composition remain separately specified work.

Two large BR-006 source/authoring videos remain in the repository but are excluded
from the installable ZIP by `tools/v2-source-certification/package-boundary.json`.
The founder footage remains an SOT reference. Never delete it to reduce package
size. Exact unreachable page drafts are archived outside the theme runtime under
`docs/v2-authoring/archive-20260906/`; live page partials and their assets remain.

The completion evidence lives in `tasks/v2-completion-20260906/`. Local verification
and a reproducible ZIP do not establish production gateway/account/plugin behavior,
field Core Web Vitals, founder artistic acceptance or deployment permission.
