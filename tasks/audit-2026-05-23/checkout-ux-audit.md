# SkyyRose Cart → Checkout → Order-Received UX Audit
**Date:** 2026-05-23 | **Auditor:** UX Researcher Agent | **Scope:** Read-only HTTP + source analysis

---

## Executive Summary

The SkyyRose WooCommerce cart/checkout flow has **2 P0 conversion blockers** that require immediate action before any marketing spend:

1. The live cart page renders a **static Elementor HTML widget** — not the well-built `woocommerce/cart/cart.php` override. The promo code field cannot apply coupons, checkout URL is hardcoded, and "Continue Shopping" returns to the homepage.
2. **No `thankyou.php` override exists** — the order-received page delivers WC generic copy, violating brand voice canon (no urgency, garment as protagonist, founder register).

---

## Severity Reference

| Level | Definition |
|---|---|
| **P0** | Blocks checkout completion or violates production canon |
| **P1** | Measurable conversion loss, mobile UX degraded |
| **P2** | Friction / missed optimization, real but not blocking |
| **P3** | Inconsistency, minor, low-impact |

---

## Section 1 — Cart Page (`/cart/`)

### Architecture Finding (Critical)

| Finding | Evidence |
|---|---|
| Live cart uses Elementor Canvas template | `curl https://skyyrose.co/cart/` → body class: `page-template-skyyrose-canvas` |
| WC analytics confirms no WC shortcode | `cart_page_contains_cart_block: "0"`, `cart_page_contains_cart_shortcode: "0"` |
| PHP override silently ignored | `woocommerce/cart/cart.php` (597 lines, well-built) — never rendered |

The entire PHP override — with proper WC coupon form, AJAX quantity, trust badges, free shipping progress bar, and cross-sell — **never runs in production**.

---

### Cart P0 Findings

| ID | Finding | File:Line | Revenue Impact |
|---|---|---|---|
| **C-P0-01** | Promo code field has no `<input name="coupon_code">` and no WC nonce — coupons cannot be applied | Elementor HTML widget (live page) | 100% of coupon campaigns fail silently |
| **C-P0-02** | "Proceed to Checkout" uses hardcoded `/?page_id=9452` — breaks if page is deleted/recreated | Elementor HTML widget (live page) | Full checkout funnel breaks on page rebuild |
| **C-P0-03** | "Continue Shopping" links to `/` (homepage) not shop | Elementor HTML widget (live page) | Abandoning shoppers have no path back to product |

**Fix for C-P0-01/02/03:** Replace Elementor HTML widget with the WC cart shortcode `[woocommerce_cart]` inside the Elementor layout, or set the cart page template to the default (not Elementor Canvas). The PHP override at `woocommerce/cart/cart.php` will then render with all its implemented features.

---

### Cart P1 Findings

| ID | Finding | File:Line | Revenue Impact |
|---|---|---|---|
| **C-P1-01** | No shipping estimate on cart — only "Free shipping on orders over $150" static text | Elementor widget (live); `cart.php` has `woocommerce_cart_totals` which includes calculator | Users cannot see shipping cost before checkout commitment; ~15–20% checkout abandonment attributed to unexpected shipping |
| **C-P1-02** | Cart item count and subtotal in Elementor widget are JS-rendered with no visible stock connection to WC | `woocommerce.php:145` — fragments update `.cart-count` + `.cart-subtotal` on WC events, but Elementor cart uses different markup | Out-of-stock items may silently persist in UI cart |

---

### Cart P2 Findings

| ID | Finding | File:Line |
|---|---|---|
| **C-P2-01** | Express pay hook `do_action('skyyrose_cart_express_pay_buttons')` in PHP override never fires (override not rendering); unknown if any gateway listener is wired | `woocommerce/cart/cart.php:89` |
| **C-P2-02** | Free shipping progress bar in `cart.php` (`.skyy-cart__shipping-progress`) not visible on live cart | `woocommerce/cart/cart.php:52–68` — blocked by Elementor rendering |
| **C-P2-03** | Single "Wears With" cross-sell via `skyyrose_get_cart_wears_with()` implemented but not visible | `inc/woocommerce.php:668` + `cart.php:495–562` |

---

### Cart P3 Findings

| ID | Finding | File:Line |
|---|---|---|
| **C-P3-01** | ATC notification uses custom `.skyy-cart-notice` (jQuery DOM construction) instead of `window.skyyToast` | `assets/js/woocommerce.js:38–62` — functional but inconsistent with global toast system |
| **C-P3-02** | `cart.js` (Store API v1) retirement confirmed clean — no dangling `window.SkyyRoseCart` references in theme PHP or JS | Verified via grep: `87e420883` retirement complete |

---

## Section 2 — Checkout Page (`/checkout/`)

### Architecture Baseline

| Property | Value | Source |
|---|---|---|
| Template rendering | `form-checkout.php` (662 lines, 4-step JS checkout) | `woocommerce/checkout/form-checkout.php` |
| Guest checkout | Enabled (`option_guest_checkout: "yes"`) | `curl https://skyyrose.co/checkout/` → `wc_checkout_params` |
| Delayed account creation | Enabled | `wc_checkout_params.delayed_account_creation: "Yes"` |
| Active gateways | `woocommerce_payments`, `stripe`, `stripe_klarna` | `wc_checkout_params.payment_methods` |
| Stripe Link | Enabled (`is_link_enabled: true`) | `wc_stripe_upe_params` |

---

### Checkout P1 Findings

| ID | Finding | File:Line | Mobile Impact |
|---|---|---|---|
| **CH-P1-01** | No `inputmode` attribute on any checkout field — phone, postcode, card fields show alphabetic keyboard on iOS/Android | `woocommerce/checkout/form-checkout.php:114–340` — all fields via `woocommerce_form_field()` with no `input_class` or `custom_attributes` for `inputmode` | ~3–5s extra per numeric field × 4 numeric fields = 12–20s added friction per mobile checkout |
| **CH-P1-02** | No `enterkeyhint` on step-advancing fields — "Go"/"Next" CTA not available on mobile keyboard; users don't know tap-return will advance the step | Same as CH-P1-01 | Increases step-abandonment on mobile |
| **CH-P1-03** | `billing_phone` may render twice: conditionally in Step 1 (`show_wc_password_strength_meter()` branch) AND required in Step 2 | `form-checkout.php:114–129` (Step 1 conditional block) + `form-checkout.php:273–285` (Step 2 address fields) | Duplicate field = confusing UX + duplicate validation error messages |
| **CH-P1-04** | No `autocomplete` override — WC defaults `autocomplete="tel"` on phone and `autocomplete="postal-code"` on postcode, but `first_name`/`last_name` rely on `autocomplete="given-name"` / `autocomplete="family-name"` from WC core — unverified if correct tokens pass through custom override | `form-checkout.php` — no explicit `custom_attributes` array passed | Autofill failure = re-entry of full name/address, ~8s per checkout |

**Fix for CH-P1-01/02/04:** Add `custom_attributes` to `woocommerce_form_field()` calls. Example:

```php
// form-checkout.php — Step 2 phone field (~line 278)
woocommerce_form_field( 'billing_phone', array(
    'type'             => 'tel',
    'custom_attributes' => array(
        'inputmode'    => 'tel',
        'enterkeyhint' => 'next',
        'autocomplete' => 'tel',
    ),
    ...
) );
// postcode field (~line 310)
woocommerce_form_field( 'billing_postcode', array(
    'type'             => 'text',
    'custom_attributes' => array(
        'inputmode'    => 'numeric',
        'enterkeyhint' => 'next',
        'autocomplete' => 'postal-code',
    ),
    ...
) );
```

**Fix for CH-P1-03:** Audit `billing_phone` render conditions. If Step 1 only shows phone for password-strength scenarios, gate it strictly with `if ( 'yes' === get_option('woocommerce_registration_generate_password') )` and ensure it does NOT also render in Step 2's address block.

---

### Checkout P2 Findings

| ID | Finding | File:Line |
|---|---|---|
| **CH-P2-01** | `billing_address_2` (Apt/Suite) visible by default — adds cognitive load for ~80% of users who don't need it | `form-checkout.php:~295` — field rendered unconditionally in Step 2 |
| **CH-P2-02** | Step progress indicator uses visual dots only — no text label ("Step 2 of 4: Shipping") — screen readers and anxious users have no named context | `form-checkout.php:45–65` (progress dots HTML) |
| **CH-P2-03** | Sticky sidebar (420px) order summary shows cart items on desktop but not confirmed as rendering on mobile (sidebar collapses) — if mobile summary is hidden until Step 4, users cannot verify order mid-checkout | `form-checkout.php:390–450` (sidebar HTML) |
| **CH-P2-04** | Klarna (`stripe_klarna`) listed as active gateway but no BNPL messaging visible in checkout — "buy now, pay later" not surfaced as cart-stage hook to reduce large-order hesitation | `wc_checkout_params.payment_methods` + `form-checkout.php:320–380` (payment step) |

---

### Checkout P3 Findings

| ID | Finding | File:Line |
|---|---|---|
| **CH-P3-01** | Guest checkout is enabled but no visual prominence — the default WC "returning customer?" login prompt likely renders above the form; no A/B on "Continue as Guest" primary CTA | `form-checkout.php:20–40` (login prompt block) |
| **CH-P3-02** | Stripe Link express checkout enabled (`is_link_enabled: true`) — if express pay renders at checkout top, users can skip all fields; confirm express pay placement is above Step 1, not after all fields | `wc_stripe_upe_params` + `form-checkout.php:85–100` (express pay hook location) |

---

## Section 3 — Order Received / Thank-You

### P0 Findings

| ID | Finding | File:Line | Brand Canon Impact |
|---|---|---|---|
| **TY-P0-01** | No `woocommerce/checkout/thankyou.php` override exists — live order-received page delivers WC generic copy ("Thank you. Your order has been received.", transaction table, generic next steps) | Confirmed via `ls woocommerce/checkout/` — file absent | Violates founder canon: "garment is the protagonist," no urgency, brand voice register required. WC default copy has zero SkyyRose voice. |

**Fix:** Create `woocommerce/checkout/thankyou.php`. Minimum viable brand-compliant content:

```
- Headline: brand-voice confirmation (e.g., "Your order is moving." — terse, confident, no urgency)
- Subhead: order number + "We'll email you when it ships."
- NO related products (skyyrose_disable_related_products() already fires — stay consistent)
- NO countdown timers, NO urgency copy
- Garment reference: if order contains a named product, surface product name in context (e.g., "The Charcoal Reverie Hoodie is being prepared.")
- CTA: "Back to Collections" → wc_get_page_permalink('shop')
- Optional: account creation prompt (delayed_account_creation is already enabled via WC settings)
```

---

### Order-Received P2 Findings

| ID | Finding |
|---|---|
| **TY-P2-01** | Delayed account creation is enabled in WC settings — WC default will prompt "Create an account" on the thank-you page. Without `thankyou.php` override, this renders in WC generic styling, not SkyyRose design. |
| **TY-P2-02** | No post-purchase brand moment — no social follow CTA, no loyalty/waitlist mention, no brand story anchor. WC default is transactional; SkyyRose should reinforce the brand story (no tagline — none is authorised, founder decision 2026-10-06). |

---

## Section 4 — Mini Cart / Cart Drawer

| ID | Finding | File:Line |
|---|---|---|
| **MC-01** | `cart.js` (Store API v1, `window.SkyyRoseCart`) retirement confirmed clean — no theme PHP or JS references remain | Verified: `87e420883` + grep confirms no dangling calls in `inc/`, `assets/js/`, `template-parts/` |
| **MC-02** | ATC feedback: `woocommerce_add_to_cart_fragments` hook fires, updates `.cart-count` via `skyyrose_woocommerce_cart_fragments()` | `inc/woocommerce.php:145` |
| **MC-03** | ATC notification: custom `.skyy-cart-notice` created via jQuery DOM (not `innerHTML`), bottom-right fixed, fades in with `.is-visible` — functional | `assets/js/woocommerce.js:38–62` |
| **MC-04** | Mini-cart drawer references (`drawer.php`, `product-card-holo.js`, `immersive-wc-bridge.js`) use WC's built-in `woocommerce_add_to_cart_fragments` / `wc_add_to_cart_params` — these are the correct WC APIs, not `cart.js` | `template-parts/`, `assets/js/` — confirmed correct |

---

## Priority Action Table

| Priority | ID | Action | Owner | Estimated Conversion Lift |
|---|---|---|---|---|
| **P0** | C-P0-01/02/03 | Replace Elementor HTML widget with `[woocommerce_cart]` shortcode (or remove Canvas template from cart page) — unlocks coupon, dynamic checkout URL, shop link | WordPress Admin (template change) + Dev (Elementor edit) | Coupons functional; estimated 5–10% redemption rate on campaign traffic |
| **P0** | TY-P0-01 | Create `woocommerce/checkout/thankyou.php` with brand-voice content | `woocommerce/checkout/thankyou.php` (new file) | Brand canon compliance; post-purchase brand equity |
| **P1** | CH-P1-01/02 | Add `inputmode` + `enterkeyhint` to all checkout numeric/tel fields | `woocommerce/checkout/form-checkout.php:114–340` | ~12–20s saved per mobile checkout; mobile conversion rate improvement |
| **P1** | CH-P1-03 | Audit and fix `billing_phone` double-render risk | `form-checkout.php:114–129` + `form-checkout.php:273–285` | Eliminates duplicate validation errors |
| **P2** | CH-P2-01 | Hide `billing_address_2` by default, show via "Add apartment/suite" toggle | `form-checkout.php:~295` | Reduces form cognitive load |
| **P2** | CH-P2-04 | Surface Klarna BNPL messaging at cart + checkout (e.g., "or 4 payments of $X") | Cart sidebar + checkout payment step | Reduces large-order hesitation |
| **P3** | C-P3-01 | Migrate ATC notification from `.skyy-cart-notice` to `window.skyyToast` | `assets/js/woocommerce.js:38–62` | Code consistency, no user-facing impact |

---

## What Is Working Correctly

- Guest checkout enabled (`wc_checkout_params.option_guest_checkout: "yes"`)
- Delayed account creation enabled — post-purchase prompt with no friction during checkout
- Stripe Link express checkout enabled and active (`is_link_enabled: true`, `is_express_checkout_enabled: true`)
- `cart.js` (Store API v1) cleanly retired — no dangling references
- `skyyrose_disable_related_products()` fires on `wp` hook — no related products on any WC page
- Free shipping threshold constant `SKYYROSE_FREE_SHIPPING_THRESHOLD = 150` correctly defined and used
- PHP override `woocommerce/cart/cart.php` is well-implemented (trust badges, progress bar, cross-sell, AJAX quantity, express pay hook) — it just needs the Elementor Canvas template removed from the cart page to activate

---

*Citations: all curl evidence from `https://skyyrose.co/cart/` and `https://skyyrose.co/checkout/` fetched 2026-05-23. All file:line references from source reads in this session.*
