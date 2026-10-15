# Phase A — Zero-Deploy Admin Walkthrough
**Date:** 2026-05-23
**Owner:** Founder (Corey) or anyone with `manage_options` cap on wp-admin
**Total time:** 5 minutes
**Deploy required:** None
**Risk:** Reversible from wp-admin in 30 seconds

---

## Step 1 — Fix WP Site Title (30 seconds)

**Current state (curl-confirmed):** WordPress Site Title = `"The Skyy Rose Collection"`
Evidence: `<meta property="og:site_name" content="The Skyy Rose Collection">` on every page

**Why it matters:**
- Every `<title>` tag site-wide includes the wrong brand name
- Collection page titles overflow Google's 60-char limit because of the extra string length ("Shop Signature — Everyday Luxury Essentials | The Skyy Rose Collection" = ~71 chars; with "SkyyRose" → 54 chars)
- Social shares (Facebook, LinkedIn, Twitter) show wrong brand name in card site_name field

**Steps:**
1. Open `https://skyyrose.co/wp-admin/`
2. Sidebar → **Settings** → **General**
3. Field: **Site Title**
4. Replace `The Skyy Rose Collection` → `SkyyRose`
5. **Tagline** field — leave it empty. No tagline is authorised (founder decision 2026-10-06).
6. Scroll to bottom → **Save Changes**

**Verify (run from terminal):**
```bash
curl -s https://skyyrose.co/ | grep og:site_name
# Expect: <meta property="og:site_name" content="SkyyRose" ...
```

---

## Step 2 — Fix Cart Page Template (3 minutes)

**Current state (audit-confirmed):** Cart page rendered via Elementor HTML widget with hardcoded markup. WC overrides exist but don't render. Result: coupon input has no backend (100% broken), "Continue Shopping" button → homepage, checkout URL hardcoded `/?page_id=9452`.

**Why it matters:**
- Coupons silently fail — every coupon-using customer is blocked at cart
- "Continue Shopping" lands customers on homepage instead of last-viewed product or shop
- Theme has fully-built `woocommerce/cart/cart.php` override sitting unused

**Diagnostic first — confirm the page state:**
1. Open `https://skyyrose.co/wp-admin/`
2. Sidebar → **Pages** → find the page slugged `cart` (typically `Cart` or `Shopping Cart`)
3. Hover the page row → click **Edit**
4. Look at right-sidebar **Page Attributes** → **Template** field. If it says `Elementor Canvas` or `Elementor Full Width` → that's the bug.
5. Look at page content. If you see an HTML widget with raw `<form>` markup OR an Elementor section instead of the single shortcode `[woocommerce_cart]` → that's the bug.

**Fix — Option A (recommended): Disable Elementor on the Cart page**
1. Page Attributes → Template → change to **Default Template**
2. In page content editor, delete all content
3. Add ONLY this single block (Shortcode block): `[woocommerce_cart]`
4. **Update** the page

**Fix — Option B (if you want to keep Elementor everywhere):** Replace the HTML widget inside Elementor with a Shortcode widget containing `[woocommerce_cart]`. Less clean but preserves the Elementor Canvas template if you depend on it.

**Verify (terminal):**
```bash
curl -s https://skyyrose.co/cart/ | grep -c 'woocommerce-cart-form'
# Expect: 1 or more (the real WC cart form renders this class)

curl -s https://skyyrose.co/cart/ | grep -c 'page_id=9452'
# Expect: 0 (the hardcoded checkout URL is gone)
```

---

## Step 3 — Verify Everything (1 minute)

Run all four curls back-to-back. All must return the expected value:

```bash
# Site Title fix
curl -s https://skyyrose.co/ | grep og:site_name
# Expect content="SkyyRose"

# Cart fix
curl -s https://skyyrose.co/cart/ | grep -c 'woocommerce-cart-form'
# Expect ≥ 1

# Cart hardcoded URL gone
curl -s https://skyyrose.co/cart/ | grep -c 'page_id=9452'
# Expect 0

# JSON-LD still firing (regression check)
curl -s https://skyyrose.co/ | grep -c 'application/ld+json'
# Expect 2
```

If all 4 checks pass: Phase A done. Three P0s resolved with zero deploy.

---

## What Phase A does NOT cover

These need code changes + deploy in Phase B:
- focus-visible outline restoration (A11Y-01)
- "Complete the Look" cross-sell removal (PDP-01)
- Size chip → form binding (PDP-02)
- Brand-voice thank-you page (TY-01)
- WC session cookie cache filter (PERF-01)
- AVIF preload wiring (PERF-02)
- Possibly LCP hero img (PERF-03 — under re-verification)

---

## Rollback (if anything breaks)

**Site Title rollback:** wp-admin → Settings → General → restore the old value → Save.
**Cart page rollback:** wp-admin → Pages → Cart → Revisions (right sidebar) → restore the prior revision. WordPress keeps all page edits as revisions.

Both rollbacks take under 1 minute from the same wp-admin screen.
