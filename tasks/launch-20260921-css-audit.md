# CSS Audit Report

Scope: the V2 styles enqueued by `functions.php` for the home, shop, product,
cart, checkout, account, service/FAQ, shell, controls, visual-recovery,
collection, scene, mascot, and commerce surfaces. Audit source: the staging
matching `abe0` worktree. This is distinct from the shared checkout, whose
homepage source does not match the currently deployed Living Archive DOM.

## Overall Score: 7.5 / 10

| Dimension | Score | Summary |
|---|---:|---|
| Architecture | 8/10 | Route-scoped styles, semantic tokens, and a generated archive bundle give each surface a clear owner; the global archive projection still makes cascade order consequential. |
| Specificity | 7/10 | BEM-like scope is generally disciplined; 35 integration-scoped `!important` declarations support Woo/dialog, visibility, and motion states, while two focus overrides need careful local reinforcement. |
| Redundancy | 7/10 | Tokens and route sheets reduce repetition, but legacy/theme/global overlays repeat responsive product-card and header decisions. |
| Accessibility | 8/10 | Global focus, forced-colors, reduced-motion, native controls, and target tokens are strong; two service links measured 41px at 390px and the contact fields suppress the general focus ring. |
| Performance | 8/10 | Page assets are route-scoped and primary motion is transform/opacity; scene effects have containment and reduced-motion fallbacks. Existing `backdrop-filter` remains limited to dialogs/hero controls. |
| Modernity | 7/10 | Logical properties, `clamp`, `color-mix`, container queries, and `:is()` are used. CSS layers/private-token convention are absent, and legacy float neutralization remains necessary for WooCommerce. |

## Findings

### Critical

- **Resolved: phone shop cards made garment proof too small** — the earlier live 390px two-column presentation produced 156px cards and 103 × 167px product pixels. `assets/css/shop-page.css` now makes the archive one garment-led column at ≤479px while preserving the 2/3/4-column breakpoints above it. A transient unavailable-media decoration observed during visual capture remains unconfirmed as a product-media issue; the separate all-33 on-model audit remains authoritative for that question.

  ```css
  @media (max-width: 29.99rem) {
    body.woocommerce .sr2-shop-archive ul.products {
      grid-template-columns: minmax(0, 1fr);
    }
  }
  ```

- **Resolved: contact-field keyboard focus was locally weakened** — `assets/css/content-page.css:86-88` retains the field’s editorial underline while restoring the house `:focus-visible` outline and two-tone focus treatment.

  ```css
  .sr2-contact-form input, .sr2-contact-form select, .sr2-contact-form textarea {
    outline: 0;
  }
  ```

### Warnings

- **Resolved: service-link targets were short on mobile** — `assets/css/theme.css:403-405` applies the existing 44px target token without changing route structure or copy. The wrapping service and account link groups are also centered beneath their centered page heads.

- **Resolved: arrival hierarchy and cross-page axes** — the baseline 1440px staging page placed the 115.2px title on the left rail while centering the 19.2px intro and CTA group. The founder’s final direction is a centered desktop aesthetic. `assets/css/home-page.css:7-12` now centers the hero copy, refined 7ch display, 34ch intro, and actions on every viewport; it preserves the scenic media, mascot, controls, and animation hooks. The shared route rules already center page and section heads; this final pass additionally centers the Shop collection rail (`shop-page.css:10`), service/account link groups (`theme.css:403`), and PDP collection eyebrow/title (`product-page.css:33,146-147`). Purchase information, field labels, tables, prices, and product options intentionally remain left-aligned for scanning.

- **Legacy motion toggle uses `outline: none`** — `assets/css/legacy-world-components.css:60` — focus currently changes border/background alongside hover, so it has a visible state, but the stronger global focus ring is suppressed. Retain for this launch because this sheet is a motion-dependent collection surface and the risk is lower than changing its interaction stack today.

- **No stylesheet-native cascade layers** — all loaded route sheets — asset ownership is clear but order is still part of the contract. Do not introduce `@layer` during launch; it would re-order a high-risk established cascade.

### Notes

- **Motion preservation passes static audit** — `assets/css/design-tokens.css:228-238`, `visual-recovery.css:292-313`, `mascot.css:362-417`, `collection-scene-motion.css:95-98`, and `premium-commerce.css:29` each implement a reduced-motion route. The existing scene/video/mascot behavior must be rechecked after the build, not removed.

- **Contrast is strong in the arrival** — live hero `#f8f5ef` on `#040405` calculates 18.83:1; supporting `#d7d4ce` calculates 13.86:1. The audit introduces no palette changes.

- **Reflow baseline** — at an explicit 390 × 844 viewport, live staging had no horizontal overflow on the homepage, open/closed mobile menu, shop, and FAQ. A 320px post-build browser check remains required. The staged source also requires cache-busted verification because Jetpack combines CSS assets on staging.

- **Final CSS build evidence** — the current source set passes asset parity (21 CSS and 14 JS), critical CSS verification at 16,306 / 16,384 bytes, archive-bundle verification, and `git diff --check`. Final source hashes are `home-page.css` `97a9695f5821df79d08578b71bca0207b32a59577eccac4e3105209745046278`, `shop-page.css` `9f0f2410fa880e851eef43402ba4ce37e4e038281d3508160e7def1d3e14772d`, `theme.css` `a415c69562f70b2ca892b892ae829b4b19ee4a52858b59aea8c6d607fd3d7b5e`, and `product-page.css` `d3e5d3167eb66f8ae543c1951fa815d85ee30a5f9a23d131df3fb2cbf463c784`.

- **Product imagery is not a CSS substitute** — a temporary capture appeared to show unavailable-media decoration, but that state is unconfirmed and was not treated as evidence of missing product media. The image/on-model owner is separately auditing all 33 products; this report deliberately does not create fallback imagery.

## Anti-Patterns Detected

| Pattern | Count | Locations |
|---|---:|---|
| `@import` | 0 | None in loaded V2 source stylesheets. |
| Layout floats | 11 neutralizations + 2 compatibility uses | `product-page.css:16,26,32,49-50,131`; `theme.css:158,387,394-401`; `global-shell.css:68,219`. Most reset WooCommerce defaults; the mini-cart image float remains a contained compatibility rule. |
| `!important` | 35 declarations in 7 files | `about-archive.css:75,91`; `product-page.css:15,85`; `mascot.css:307,330,352,362,378,403,412,417`; `immersive.css:666,669,689-692,696`; `visual-recovery.css:230`; `global-shell.css:69`; `theme.css:13,253,267,571,575`. These are screen-reader, hidden-state, Woo/dialog, responsive placement, pause, and reduced-motion overrides; none were introduced by this audit. |
| `outline: 0` | 3 | `design-tokens.css:224` has a box-shadow replacement; `theme.css:286` has one; `content-page.css:86` needs the local focus repair above. |
| Broad backdrop blur | 4 route-local uses | `theme.css:19,301,316,331`; dialog and scrolled-header only, not card-grid glassmorphism. |
| Generic AI aesthetic patterns | 0 | No gradient-text, custom cursor, grain overlay, or generic purple SaaS treatment detected. |

## Prioritized Fix Plan

| Priority | Fix | Impact | Effort | Dimensions Affected |
|---:|---|---|---|---|
| 1 | Completed: use a one-column garment-led Shop card at ≤479px while preserving 2/3/4 columns and all card actions. | High | Low | Accessibility, responsive quality, product hierarchy |
| 2 | Completed: add the house focus-ring tokens to contact field `:focus-visible`. | High | Low | Accessibility |
| 3 | Completed: set service/account route links to `min-height: var(--sr2-target-size)` and center their wrapping groups. | Medium | Low | Accessibility, responsive quality |
| 4 | Completed: center the refined desktop hero and shared page-heading axes while preserving readable commerce/form detail alignment. | Medium | Low | Typography, visual hierarchy |
| 5 | Build only after the three source fixes, then test staging cache-busted CSS at 320, 390, and 1440; exercise menu, scene pause, mascot, product purchase path, cart, and checkout failure/recovery. | High | Medium | Release evidence |
| 6 | Complete the separate all-33 on-model/media audit and resolve only confirmed gaps through the approved workflow. | High | Medium | Product truth, visual quality |
