# SkyyRose.co Visual Audit — 2026-05-23

Live capture across 16 routes (108+ screenshots) via `openwolf designqc`. Read-only audit. Findings ranked P0 → P3.

---

## P0 — CRITICAL (revenue / buy-path broken)

### P0-1. Cart + Checkout render as RAW CSS TEXT
- **Pages:** `/cart/`, `/checkout/`
- **What's happening:** The cart and checkout pages are serving unminified CSS as VISIBLE text content. Comments like `V3.2 OPTIMIZED SHELL`, `THEME KILL`, full CSS variable declarations are rendering on screen as page body.
- **Customer impact:** Cannot complete purchase. Buy path is functionally broken.
- **Root cause hypothesis:** A `<style>` block is missing its closing tag, OR a PHP template is echoing CSS file contents into the DOM instead of enqueueing them, OR the WooCommerce overrides in `woocommerce/cart.php` + `woocommerce/checkout.php` have a markup error.
- **Severity:** **REVENUE-BLOCKING.** Fix before anything else.

### P0-2. Interior header duplicated + tagline drift on EVERY non-homepage URL
- **Pages:** All except `/`
- **What's happening:** Every interior page renders two stacked nav bars:
  - Row 1: SEARCH / ACCOUNT / BAG with `SKYY ROSE` wordmark (wrapped on 2 lines)
  - Row 2: `SKYYROSE | LUXURY STREETWEAR BORN FROM STRUGGLE` + duplicate nav (`SIGNATURE COLLECTION | SKYYROSE`, `LOVE HURTS COLLECTION | SKYYROSE`, `BLACK ROSE COLLECTION | SKYYROSE`, `CONTACT | SKYYROSE`)
- **Tagline issue:** "LUXURY STREETWEAR BORN FROM STRUGGLE" is tagline drift — not in brand canon. Locked tagline is ""
- **Wordmark issue:** "SKYY ROSE" wraps to 2 lines in the second header, indicating the container is too narrow.
- **Customer impact:** Every interior page first-fold is a broken-looking double header. Brand looks unprofessional and the second nav redundantly repeats menu options.
- **Root cause hypothesis:** Either a builder (Elementor / Divi / Beaver) plugin is injecting a second header globally while the theme header is also active, OR `header.php` is being included twice, OR a global Elementor header template is fighting `header.php`.
- **Severity:** **BRAND-WIDE.** Every page that isn't `/` looks broken.

### P0-3. 3 of 4 collection pages render essentially empty after hero
- **Pages:** `/collection-signature/`, `/collection-black-rose/`, `/collection-love-hurts/`
- **What's happening:** First two sections (header + hero) render. Sections 3-7 are nearly pure-black (5.9KB each ≈ blank JPEG).
- **Exception:** `/collection-kids-capsule/` has full-page content (intentional "COMING SOON" minimalist layout).
- **Black Rose specifically:** Hero image is so dark/blurred it reads as a smudged black void with illegible text overlay.
- **Customer impact:** Collection pages — the main browse surface — are visually empty / non-functional below the fold.
- **Root cause hypothesis:** IntersectionObserver scroll reveals (`.col-reveal` class) stuck at `opacity:0` because the safety-net fallback isn't firing for headless Playwright captures. **OR** content genuinely isn't rendering (product grid query failing, builder not loading).
- **Severity:** Customers see this on every collection visit. Equivalent to the page being blank.

---

## P1 — HIGH (visible damage to brand quality)

### P1-1. Shop page shows placeholder images + "Uncategorized" category
- **Page:** `/shop/`
- **What's happening:** Two category cards: "Shop (32)" + "Uncategorized (3)". Both display the default WordPress placeholder image (mountain-sun-frame icon). The (32)/(3) counts are styled with a gold/yellow background box that looks broken.
- **Customer impact:** The shop entry page looks like an unconfigured WP install. "Uncategorized" is a hygiene failure — categories should be brand-aligned (Black Rose, Love Hurts, Signature, Kids Capsule).
- **Fix:** Real category images + reassign "Uncategorized" products + restyle the count badge.

### P1-2. Homepage tagline drift: "Three collections, one vision"
- **Page:** `/` (homepage)
- **What's happening:** Hero subtitle reads *" Three collections, one vision — built by a father, named after a daughter."*
- **Issue:** Locked canon says "**Four** collections, **one bloodline**" — Kids Capsule is the 4th, and "vision" should be "bloodline."
- **Source:** `front-page.php:252` already has the canon-correct version, so the live render is either stale, cached, or another source overriding it.
- **Severity:** Above-fold homepage copy. Three small word changes.

### P1-3. Front-page hero rose composition feels off-center / off-balance
- **Page:** `/`
- **What's working:** SKYYROSE wordmark dominates. Cathedral imagery is rich. "Oakland · Est. 2020 · Gender Neutral" eyebrow is clean.
- **What's off:** The dark rose centered below the wordmark sits awkwardly in dead space. It competes with the tagline below it. Either the rose should be removed (let the wordmark + tagline carry the hero) OR the rose should be smaller and positioned as a divider element.
- **Severity:** Polish-level, not broken. But homepage hero is the brand's first impression.

---

## P2 — MEDIUM (specific page-level issues)

### P2-1. Signature immersive title says "The Golden Gate Runway"
- **Page:** `/experience-signature/`
- **What's happening:** 3D scene labeled "The Golden Gate Runway" — direct reference to Frisco's bridge, not Oakland's Bay Bridge.
- **Status:** Open question from yesterday's TF-10. Bay Bridge = Oakland is locked; Golden Gate's status is still pending Corey's call.
- **Severity:** Voice canon ambiguity. Visually the 3D scene works but the title positions Signature in Frisco geography.

### P2-2. Signature immersive 3D scene reads as 4 colored dots
- **Page:** `/experience-signature/`
- **What's happening:** The 3D scene shows 4-5 pink/rose dots floating in a loose oval against dark background. Compared to the brand register, it looks more like a placeholder than a finished immersive experience.
- **Fix scope:** Three.js scene geometry, lighting, particle density, or a different conceptual scene altogether.

### P2-3. Wordmark "SKYY ROSE" wraps on 2 lines in interior nav
- **Pages:** All except `/`
- **What's happening:** The brand wordmark in the broken interior header is forced onto 2 lines because the container width is too narrow. Looks unprofessional.
- **Fix:** White-space:nowrap + larger min-width on the wordmark container OR remove the duplicate header (P0-2 fix solves this).

### P2-4. Kids Capsule "COMING SOON" lacks visual richness
- **Page:** `/collection-kids-capsule/`
- **What's working:** Purple gradient + "Luxury runs in the family." tagline + "COMING SOON" pill. Intentional minimalism.
- **What's missing:** No imagery, no visual hook beyond the gradient. Compared to other "coming soon" luxury teases (Hermès, Jacquemus drop pages), this needs a hero image or a single styled product silhouette.
- **Severity:** Polish-level. Works as a holding page but doesn't sell the brand.

---

## P3 — LOW (small polish + minor hygiene)

### P3-1. About page works — minor breadcrumb hygiene
- **Page:** `/about/`
- **What's working:** "THE STORY" big serif headline + child wearing rose-embroidered hoodie + "" tagline = strong page.
- **Minor:** Breadcrumb "ABOUT / SR-001" is cryptic — SR-001 is an internal slug, shouldn't be customer-facing breadcrumb text.

### P3-2. 404 page rendered content
- **Page:** `/not-a-real-page/`
- File sizes show full content rendered (not a minimal 404). Need to read screenshot to confirm. Skipped in this pass.

### P3-3. Search page
- **Page:** `/?s=rose`
- Only captured first-fold (single image). Need follow-up capture for full page review.

---

## Surface coverage

| Page | Captured? | Verdict |
|------|-----------|---------|
| `/` (homepage) | ✅ | Polished but minor canon drift (P1-2) + rose placement (P1-3) |
| `/about/` | ✅ | Strong (P3 only) |
| `/collection-signature/` | ✅ | Empty below fold (P0-3) |
| `/collection-black-rose/` | ✅ | Empty + black-void hero (P0-3) |
| `/collection-love-hurts/` | ✅ | Empty below fold (P0-3) |
| `/collection-kids-capsule/` | ✅ | Intentional minimal (P2-4) |
| `/experience-signature/` | ✅ | 3D works, Golden Gate title pending (P2-1) |
| `/experience-black-rose/` | ✅ | Not deep-read this pass |
| `/experience-love-hurts/` | ✅ | Not deep-read (top=103.9K, biggest experience) |
| `/experience-kids-capsule/` | ✅ | Not deep-read this pass |
| `/pre-order/` | ✅ | Not deep-read (small file sizes — probably minimal) |
| `/shop/` | ✅ | Placeholder hell + Uncategorized (P1-1) |
| `/cart/` | ✅ | **RAW CSS RENDERING (P0-1)** |
| `/checkout/` | ✅ | **RAW CSS RENDERING (P0-1)** |
| `/?s=rose` (search) | ⚠️ partial | Only top captured |
| `/not-a-real-page/` (404) | ✅ | Not deep-read this pass |

Landing pages (`/landing-signature/`, `/landing-black-rose/`, `/landing-love-hurts/`) were NOT captured — URLs uncertain. Need confirmation of live landing URLs to add to next sweep.

---

## Recommended fix priority

| # | Issue | Severity | Likely fix scope |
|---|-------|----------|------------------|
| 1 | **P0-1** Cart/checkout raw CSS | REVENUE-BLOCKING | Likely 1-3 file template fix (WC overrides) |
| 2 | **P0-2** Duplicate interior header + "BORN FROM STRUGGLE" tagline drift | BRAND-WIDE | Locate second header source (builder or duplicate include), remove |
| 3 | **P0-3** 3 collection pages empty below hero | HIGH-VOLUME | Investigate `.col-reveal` IO + content rendering |
| 4 | **P1-1** Shop placeholders + Uncategorized | HIGH | Category cleanup + image assignment |
| 5 | **P1-2** Homepage "three / vision" → "four / bloodline" | HIGH | One template edit OR cache flush |
| 6 | **P1-3** Homepage hero rose placement | MEDIUM | CSS positioning tweak |
| 7 | **P2-1** Golden Gate Runway naming | MEDIUM | Awaits Corey's call |
| 8 | **P2-2** Signature 3D scene thin | MEDIUM | Three.js scene work |
| 9 | **P2-3** Wordmark wraps | LOW | Resolved by P0-2 fix |
| 10 | **P2-4** Kids Capsule visual richness | LOW | Add hero image |
| 11 | **P3-*** misc | LOW | Bundle into polish pass |

---

## Root Cause Investigation (added 2026-05-23 09:50)

Per Corey's request — investigate before fixing to check for common root cause.

**Result: All 3 P0s have DIFFERENT root causes. 2 of 3 are WordPress admin / database fixes, NOT theme code.**

### P0-1 — Cart/checkout raw CSS

**Root cause:** WordPress page content (Gutenberg page body) has a giant CSS dump pasted into it as **plain text**, not wrapped in a `<style>` tag. Same dump is also in the page's SEO meta description field (catastrophic for search engines — Google sees "V3.2 OPTIMIZED SHELL THEME KILL" as the page description).

**Evidence (live curl `https://skyyrose.co/cart/`):**

```html
<div class="entry-content wp-block-post-content...">
/* ═══ V3.2 OPTIMIZED SHELL ═══ */
/* — THEME KILL — */
#masthead,#site-navigation,.site-header{display:none!important}
:root{ –obsidian:#0A0A0A; –bone:#E8E4DF; ... }
```

**Bonus damage:** The CSS uses **en-dashes** (`–void`, `–obsidian`) instead of **double-hyphens** (`--void`, `--obsidian`) for CSS custom properties. Classic Microsoft Word / smart-quote autocorrect mangling. Even if this CSS were inside a `<style>` tag, the variables would be syntactically invalid.

**Fix surface:** WordPress admin — `Pages → Cart → delete CSS block from page body`. Same for `Pages → Checkout`. Also clear the Yoast/RankMath SEO meta description on both pages.

**Theme code involvement:** ZERO. Grepped entire theme for "OPTIMIZED SHELL", "THEME KILL", "V3.2" — no matches.

### P0-2 — "Duplicate header" + "BORN FROM STRUGGLE" tagline

**Root cause:** Not duplicate header. WordPress primary navigation menu items have **bloated marketing labels**:

```html
<li><a href="/">SkyyRoseLuxury Streetwear Born From Struggle</a></li>
<li><a href="/collection-signature/">SIGNATURE COLLECTION | SKYYROSE</a></li>
<li><a href="/collection-love-hurts/">LOVE HURTS COLLECTION | SKYYROSE</a></li>
<li><a href="/collection-black-rose/">BLACK ROSE COLLECTION | SKYYROSE</a></li>
<li><a href="/contact/">CONTACT | SKYYROSE</a></li>
```

These long labels wrap onto multiple lines in the nav container, making it LOOK like two stacked rows. It's one nav with ugly long labels.

**Evidence:** `header.php` is clean (verified by reading the file) — single nav with `wp_nav_menu(theme_location => 'primary')`. The labels above came from the LIVE HTML curled from `/collection-black-rose/`.

**Fix surface:** WordPress admin — `Appearance → Menus → Primary Menu`. Rename each menu item label:
- `SkyyRoseLuxury Streetwear Born From Struggle` → `Home` (or remove — the centered SKYY ROSE wordmark already handles home)
- `SIGNATURE COLLECTION | SKYYROSE` → `Signature`
- `LOVE HURTS COLLECTION | SKYYROSE` → `Love Hurts`
- `BLACK ROSE COLLECTION | SKYYROSE` → `Black Rose`
- `CONTACT | SKYYROSE` → `Contact`

**Theme code involvement:** ZERO. Theme renders whatever labels admin sets.

**Note:** The "BORN FROM STRUGGLE" tagline drift flagged in yesterday's canon audit (LV-10) is the same issue — the marketing phrase is hardcoded as a menu item label in WP admin.

### P0-3 — Collection pages empty below hero

**Root cause:** **NOT empty.** Curling `/collection-black-rose/` returns 177KB of HTML with 7 col-story sections, 6 col-founder sections, 6 col-newsletter sections, 6 col-crossnav sections, etc. The content is there.

**The blank sections in screenshots are a CAPTURE ARTIFACT** — Playwright's headless browser triggers `.col-reveal` IntersectionObserver scroll-reveals, but the safety-net `srRevealSafety` keyframes animation (intended to force `.is-visible` at 2.5s if IO misses) fires AFTER the screenshot is captured. The content stays at `opacity:0`.

**However:** Real-user impact still exists for:
- Users with `prefers-reduced-motion: reduce` (the keyframe path is bypassed)
- In-app browsers (Instagram, TikTok, Facebook) with limited JS execution timing
- Slow connections where 2.5s elapses before content is visible

This is the **S650 paused bug** from May 21 — reveal stutter near 2.5s IO safety mark.

**Fix surface:** Theme code — `assets/css/system/animations-premium.css`. Reduce safety-net delay from 2.5s to 0.8s OR gate on viewport entry instead of pure-time. OR add a JS fallback that force-toggles `.is-visible` on `DOMContentLoaded`.

**Theme code involvement:** YES. This is the only P0 that needs a code edit.

---

## Common factor check

| | P0-1 Cart CSS | P0-2 Long menu labels | P0-3 Reveals stuck |
|---|---|---|---|
| In theme code? | ❌ | ❌ | ✅ |
| In WP database? | ✅ | ✅ | ❌ |
| Fixable via WP admin? | ✅ (10 min) | ✅ (5 min) | ❌ |
| Needs deploy? | ❌ | ❌ | ✅ |
| User-visible severity | CATASTROPHIC | HIGH (every page) | MEDIUM (subset of users) |

**Conclusion:** No single root cause. Three independent issues that happen to all be P0. **2 of 3 are 15 minutes of WP admin work, ZERO code, ZERO deploy.** Massive leverage if you do those first.

---

## Audit method

Captured 16 routes via `openwolf designqc --url https://skyyrose.co` looping per-route. Total 108+ screenshots archived to `.wolf/designqc-archive/`. Sample of 8 critical first-folds read inline this pass. Remaining 100+ available for deep-dive on specific findings. Mobile captures partially missing — designqc did NOT capture mobile viewport for most routes despite the help text suggesting both. Next pass should explicitly handle mobile.
