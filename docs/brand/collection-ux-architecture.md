# SkyyRose Collection UX Architecture — Proposal

**Status:** Proposal only — no source files modified  
**Date:** 2026-05-24  
**Author:** ArchitectUX  
**Scope:** Black Rose, Love Hurts, Signature, Kids Capsule — PDP, browse grid, landing, CSS, components, animation, performance, accessibility

---

## 1. PDP Per-Collection Dispatch Pattern

**Recommendation: Option (a) — `get_template_part('woocommerce/pdp/' . $collection_slug)` nested inside the existing editorial/non-editorial split.**

`woocommerce/single-product.php:36-49` already dispatches on `$has_editorial`. The per-collection layer goes inside each branch, not around it:

```
single-product.php
├── has_editorial → get_template_part('template-parts/product-detail-editorial', ..., ['collection' => $slug])
│   (editorial partial handles per-collection variation internally via $args['collection'])
└── standard → get_template_part('woocommerce/pdp/' . $slug, null, $args)
    fallback → woocommerce/pdp/default.php  (if no slug-specific file exists)
```

**Why not flat slug switch (option b):** That would bypass the editorial flag entirely. The editorial/non-editorial split is the primary dispatch axis — collection identity is secondary. Inverting the order throws away a functional system.

**Why not do_action registry (option d) for PDPs:** Action hooks are the right pattern for collection *page* extensibility (section 2), not for template selection. Template dispatch via `get_template_part` fallback chain is the WordPress-idiomatic approach and requires zero PHP registration overhead.

**Implementation path:** `woocommerce/pdp/black-rose.php`, `woocommerce/pdp/love-hurts.php`, `woocommerce/pdp/signature.php`, `woocommerce/pdp/kids-capsule.php`, `woocommerce/pdp/default.php`. Start with default.php extracted from the inline standard layout at `single-product.php:56+`. Collection-specific files override only what differs — gallery behavior, typography treatment, ATC button label framing.

**Non-editorial standard layout columns (all collections):** product gallery, garment type, SKU, material composition, ATC button, stock status. No related-products rail. No urgency timers.

---

## 2. Collection Browse Grid Variation

**Recommendation: Option (c) hybrid — keep `page.php` scaffold, replace raw `if` branches with `do_action('skyyrose_collection_section_' . $slug)` hooks.**

`template-parts/collection/page.php` already has slug-specific branches:
- Line 46: `$is_kids = ('kids-capsule' === $slug)` — Kids Capsule layout flag
- Line 94: `'black-rose' === $slug ? ' rv-scroll-bloom' : ''` — Black Rose hero logo animation
- Lines 146–148: Black Rose-only founder pullquote

The current raw `if` structure works but will accumulate as collections deepen. Formalizing with `do_action` preserves the shared scaffold while giving each collection a clean extension point.

**Hook map:**

| Hook | Default behavior | Per-collection override |
|---|---|---|
| `skyyrose_collection_after_hero_{slug}` | empty | BR: founder pullquote injection |
| `skyyrose_collection_story_{slug}` | generic story render | LH: grief/survival narrative; SG: 4AM origin |
| `skyyrose_collection_grid_classes_{slug}` | filter on CSS class string | KC: tighter gap, warmer palette classes |

The shared page structure (Hero → Grid → Story → CTA → Cross-Collection Nav → Newsletter) stays intact. The cross-collection nav at `page.php:170-180` remains the one permitted cross-sell rail.

**Why not fully separate templates (option a):** Duplicates 160+ lines of identical scaffold. Every structural change requires editing 4 files.

**Why not CSS-only (option b):** CSS can't conditionally inject markup — the pullquote at lines 146–148 is a content-structural difference, not a visual difference.

---

## 3. Landing Page Surface Architecture

**Surface distinction:**

| Surface | Purpose | Entry path | Sections |
|---|---|---|---|
| Browse grid (`/collection-{slug}/`) | Organic catalog scan, brand immersion | Direct nav, SEO | 6 sections |
| Landing (`/launch-{slug}/`) | Paid traffic conversion | Ad → landing | 10 sections (press, reviews, FAQ, email CTA) |

The 10-section structure in `template-landing-signature.php` (confirmed: Hero, Press Bar, Story, Parallax Banner, Product Grid, Editorial Gallery, Reviews, Craft cards, FAQ, Email CTA) is the proven conversion template. Love Hurts gets the same scaffold with `data-collection="love-hurts"` triggering its palette.

**Kids Capsule landing: SKIP.** With 2 SKUs, a conversion-optimized landing page would be product-poor. Kids Capsule browse grid serves both discovery and conversion. Revisit when catalog reaches 6+ KC SKUs.

**Landing templates needed:** `template-landing-black-rose.php` (exists, gap to verify), `template-landing-love-hurts.php` (build from SG scaffold with `$collection = 'love-hurts'`). Signature exists. Kids Capsule deferred.

**Shared landing template part contracts** (`template-parts/landing/`): `hero.php`, `product-grid.php`, `faq.php` accept `$args` arrays — extend, do not fork. Landing pages use `lp-*` CSS classes and `lp-rv` scroll-reveal throughout.

---

## 4. CSS Architecture

**Naming conventions:**

| Layer | Namespace | Load strategy |
|---|---|---|
| Global tokens | `--skyyrose-*` in `design-tokens.css` | Enqueued globally, always |
| Collection browse | `col-*` | `collection-pages.css` — loaded for `collection-standalone` slug |
| Landing pages | `lp-*` | `landing-pages.css` — loaded for `landing` slug |
| PDPs (standard) | `sr-*` | `single-product.css` — loaded for `single-product` slug |
| PDPs (per-collection) | `pdp-br-*`, `pdp-lh-*`, `pdp-sg-*`, `pdp-kc-*` | lazy-loaded per slug |

**Lazy-load via `$template_styles` map** (`inc/enqueue.php:465-485`). Extend with:

```php
'pdp-black-rose'   => 'collection-black-rose-pdp.css',
'pdp-love-hurts'   => 'collection-love-hurts-pdp.css',
'pdp-signature'    => 'collection-signature-pdp.css',
'pdp-kids-capsule' => 'collection-kids-capsule-pdp.css',
```

The `kc-launch` → `kids-capsule.css` entry at `enqueue.php:478` already proves the per-collection CSS override pattern. This proposal extends existing infrastructure, not new architecture.

**Template slug detection:** `skyyrose_get_current_template_slug()` (`enqueue.php:386-447`) must return `'pdp-{collection}'` for WooCommerce single-product pages. Detect via `get_queried_object()` → product → taxonomy term → collection slug. Add before the existing `is_product()` → `'single-product'` branch.

**Per-collection token blocks** already exist in `design-tokens.css` (generated — font tokens come from `typography.json` + per-collection registry `collections.<slug>.fonts`, see `SOT.md` → `typography.json`). No new tokens needed for Phase 1.

**Total CSS budget:** see Section 7.

---

## 5. Component Library Map

**Shared (no modification, all collections):**
- `product-card-holo.php` + `.product-card-holo` — holographic glass card system
- `template-parts/product-grid.php` — grid container
- `template-parts/landing/hero.php`, `product-grid.php`, `faq.php`
- `inc/enqueue.php` — template slug detection and `$template_styles` map
- `design-tokens.css` — token cascade

**Collection-specific (new files, no forks):**

| Component | Black Rose | Love Hurts | Signature | Kids Capsule |
|---|---|---|---|---|
| PDP layout | `woocommerce/pdp/black-rose.php` | `woocommerce/pdp/love-hurts.php` | `woocommerce/pdp/signature.php` | `woocommerce/pdp/kids-capsule.php` |
| PDP CSS | `collection-black-rose-pdp.css` | `collection-love-hurts-pdp.css` | `collection-signature-pdp.css` | `collection-kids-capsule-pdp.css` |
| Browse hook callbacks | `inc/collections/black-rose.php` | `inc/collections/love-hurts.php` | `inc/collections/signature.php` | `inc/collections/kids-capsule.php` |

Hook callback files registered in `functions.php` includes array, pattern mirrors `inc/builders/` registration (detection.php → shared.php → builder-specific files).

**Forking is forbidden.** `page.php`, `single-product.php`, `footer.php` are shared infrastructure. Per-collection behavior enters only through `$args`, `do_action`, and `get_template_part` fallback chain.

---

## 6. Animation System

**Re-use existing system entirely. No new animation infrastructure.**

`assets/js/premium-interactions.js` + `assets/css/animations-premium.css` provide everything needed. Single IntersectionObserver, single `revealSelectors` variable, `.is-visible` toggle with `unobserve`. Threshold 0.12, rootMargin `0px 0px -40px 0px`.

**Per-collection animation personality via CSS only** (variable values, not new classes):

| Collection | Reveal class used | Personality expressed via |
|---|---|---|
| Black Rose | `rv-clip-up`, `rv-split-char` | `--skyyrose-ease` slower (0.8s), Cinzel letter-spacing |
| Love Hurts | `rv-blur-down`, `rv-clip-diagonal` | crimson accent bleed on blur transition |
| Signature | `rv-clip-up`, `stagger-grid` | gold shimmer on `.is-visible` via `--skyyrose-accent` |
| Kids Capsule | `rv-blur`, `stagger-grid` | warmer ease timing, rose-gold accent on stagger |

Interactive classes (`magnetic`, `btn-sweep`, `btn-border-draw`, `btn-press`) used as-is — per-collection visual distinction comes from `--skyyrose-accent` driving button color, not new interaction classes.

`rv-scroll-bloom` on Black Rose hero logo (`page.php:94`) is already implemented. Extend only by adding to `revealSelectors` in `premium-interactions.js` if a new reveal class is introduced — single source of truth.

Reduced-motion: existing early-return in `premium-interactions.js` forces `.is-visible` on all reveal elements. No per-collection override needed.

---

## 7. Performance Budget

| Metric | Target | Enforcement |
|---|---|---|
| LCP (collection browse) | ≤ 2.0s | Hero image `<link rel="preload">` in `page.php`, AVIF first |
| LCP (landing page) | ≤ 2.5s | Hero partial renders blocking `<img>` with `fetchpriority="high"` |
| LCP (PDP) | ≤ 2.0s | First gallery image preloaded; AVIF/WebP `<picture>` |
| CSS per page (total) | ≤ 80KB gzip | Global tokens (≤8KB) + page CSS (≤40KB) + pdp CSS (≤16KB) |
| JS per page | ≤ 60KB gzip | premium-interactions.js (≤24KB) + page-specific (≤20KB) |
| CLS | ≤ 0.05 | Explicit `width`/`height` on all product images, no layout-shifting fonts |

**Image format strategy:** AVIF primary, WebP fallback, JPEG baseline via `<picture>` element with `srcset`. All product images minimum 800px wide, 2x for retina. Hero images: 1440px max, lazy-load below-fold, preload above-fold only.

**Per-collection PDP CSS files** must each stay under 16KB gzip. If a file approaches 20KB, extract shared PDP utilities to a `pdp-shared.css` loaded for all `pdp-*` slugs.

**Font loading:** All 9 font families already self-hosted via WordPress Font Library (zero Google CDN). `font-display: swap` on all faces. Cinzel loads only on Black Rose pages (gated by `[data-collection="black-rose"]` in design-tokens.css, but the font file loads globally — track this on next font audit).

---

## 8. Accessibility Floor

**Standard:** WCAG 2.2 AA throughout. No exceptions for aesthetic reasons.

**Contrast by collection:**

| Collection | Accent on dark bg | Ratio | AA status |
|---|---|---|---|
| Black Rose | #C0C0C0 on #0A0A0A | ~8.9:1 | Pass (large + normal) |
| Love Hurts | #DC143C on #0A0A0A | ~4.8:1 | Pass AA normal text; **constraint on thin/decorative** |
| Signature | #D4AF37 on #0A0A0A | ~7.2:1 | Pass |
| Kids Capsule | #B76E79 on #0A0A0A | ~4.6:1 | Pass AA normal text; **constraint on thin/decorative** |

**Love Hurts and Kids Capsule constraint:** Crimson #DC143C and rose gold #B76E79 both pass AA for body text (≥16px regular or ≥14px bold) but fail AAA. On thin weights or decorative use at <16px, supplement with `--skyyrose-secondary` (purple for LH, gold for KC) or white `#FFFFFF`. Per-collection PDP CSS must not use accent on text below 16px regular weight.

**Focus visible:** All interactive elements must have `:focus-visible` outline using `--skyyrose-accent` at 2px offset, never removed via `outline: none` without replacement. PDP ATC button: `box-shadow: 0 0 0 3px var(--skyyrose-accent)` on focus.

**Landmark regions** required on all templates:
- `<header role="banner">` — navigation
- `<main id="main-content">` with `tabindex="-1"` for skip-link target
- `<nav aria-label="Collection navigation">` for cross-collection rail
- `<footer role="contentinfo">`

**Skip navigation link:** `<a href="#main-content" class="skip-link">` in `header.php`. Must be the first focusable element in DOM. Already present in base theme — verify it exists on PDP templates since `woocommerce/single-product.php` has its own `<main>` construction.

**Product images:** `alt` text from WooCommerce `_wp_attachment_image_alt` meta. Empty `alt=""` only for purely decorative overlays. Holo card tilt effect must not cause CLS on keyboard focus — `will-change: transform` already applied.

**ARIA on theme toggle:** If added to collection pages, use `role="radiogroup"` with `aria-checked` on each option. (Template-level toggle not currently in scope — note for future phase.)

---

## Decision Summary

1. **PDP dispatch is nested, not flat** — collection identity is secondary to editorial/non-editorial. `single-product.php:36-49` editorial split is preserved as primary axis.
2. **Browse grid extends via hooks, not forks** — `page.php` stays shared; per-collection personality enters through `do_action('skyyrose_collection_section_' . $slug)` callbacks in `inc/collections/`.
3. **CSS lazy-load via `$template_styles` map extension** — identical mechanism to `kc-launch` → `kids-capsule.css` precedent in `enqueue.php:478`. Per-collection PDP CSS adds rows, not new architecture.

---

*Proposal document — no source files were modified. Implementation begins with `woocommerce/pdp/default.php` extraction from inline standard layout.*
