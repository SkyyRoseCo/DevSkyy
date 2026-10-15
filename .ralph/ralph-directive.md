# Ralph Deployment Directive — SkyyRose Full Website Makeover (Elite Web Builder v2)

> **NEVER DELETE THIS FILE.** Ralph reads it at the start of every iteration.
> **NEVER DELETE `.ralph/ralph-tasks.md`** either. Update it after EVERY iteration.

---

## Mission

Execute a **full website makeover** of the SkyyRose Flagship WordPress theme using the Elite Web Builder design package located at `docs/elite-web-builder-package/`. You are replacing existing templates with the new designs while preserving all immersive (3D storytelling) pages untouched.

**Source package structure:**
```
docs/elite-web-builder-package/
├── homepage/index.html          — New homepage (67KB, self-contained)
├── homepage/about.html          — New About page (129KB, cinematic) — NOTE: This is NOT the homepage. It is a standalone About page. The folder name is misleading.
├── landing-pages/lp-black-rose.html  — Conversion landing (2.1MB, 8 sections)
├── landing-pages/lp-love-hurts.html  — Conversion landing (1.6MB, 8 sections)
├── landing-pages/lp-signature.html   — Conversion landing (1.9MB, 8 sections)
├── collection-pages/black-rose.html  — Full collection grid (413KB)
├── collection-pages/love-hurts.html  — Collection grid (347KB)
├── collection-pages/signature.html   — Collection grid (407KB)
├── product-pages/product-black-rose.html — Single product detail (167KB)
├── product-pages/product-love-hurts.html — Single product detail (148KB)
├── product-pages/product-signature.html  — Single product detail (312KB)
├── wordpress-theme/skyyrose-flagship/    — WP theme overlay files
│   ├── functions.php                     — New functions (merge with existing)
│   ├── style.css                         — Updated theme header
│   ├── inc/wc-product-functions.php      — WooCommerce product helpers
│   ├── woocommerce/single-product.php    — Custom single product template
│   ├── assets/css/main.css               — New main CSS
│   ├── assets/css/single-product.css     — Single product CSS
│   └── assets/js/single-product.js       — Single product JS
└── README.md                             — Package manifest + brand constants
```

---

## CRITICAL RULES (Non-Negotiable)

### 1. File Persistence
- **NEVER delete `.ralph/ralph-context.md`** — this is your directive
- **NEVER delete `.ralph/ralph-tasks.md`** — this tracks your progress
- **Update `ralph-tasks.md` after EVERY iteration** with `[x]` for done, `[/]` for in-progress, `[ ]` for pending
- Add notes under each task about what you did

### 2. Context7 Protocol (HARD GATE — Zero Code Without It)
- **DO NOT WRITE A SINGLE LINE OF CODE** until you have queried Context7 for the relevant technology
- This is a HARD GATE — no exceptions, no "I already know this", no skipping
- Every iteration MUST begin with at least one `resolve-library-id` → `query-docs` call
- If you are about to write PHP: query Context7 for WordPress AND/OR WooCommerce docs FIRST
- If you are about to write CSS: query Context7 for the CSS framework or pattern you're using
- If you are about to write JS: query Context7 for any library (jQuery, GSAP, IntersectionObserver, etc.)
- If you are about to modify `functions.php`: query Context7 for WordPress hook best practices
- If you are about to override WooCommerce templates: query Context7 for WooCommerce template hierarchy
- If you are about to write AJAX handlers: query Context7 for WordPress AJAX API (`wp_ajax_*`)
- If you are about to write SEO markup: query Context7 for schema.org structured data
- **Libraries to always check**: WordPress, WooCommerce, PHP, jQuery, GSAP, IntersectionObserver
- **Log EVERY Context7 query** in your iteration notes in `ralph-tasks.md` — include the library ID resolved and the topic queried
- **If you skip Context7 even once, the entire iteration is invalid and must be redone**
- Context7 is not optional. Context7 is not "nice to have." Context7 is the law.

### 3. Serena Integration (MANDATORY)
- Use Serena MCP tools for ALL WordPress file operations (read, write, symbol lookup)
- After each section, use `write_memory` to save key decisions to Serena memory
- Use `get_symbols_overview` before editing any PHP file
- Use `find_symbol` to understand existing code before replacing
- **Update Serena memory after each major section completion**

### 4. DO NOT TOUCH Interactive/Immersive Pages
These files are OFF-LIMITS — do NOT modify them:
- `template-immersive-black-rose.php`
- `template-immersive-love-hurts.php`
- `template-immersive-signature.php`
- `immersive.js`
- `immersive.css`
- Any file in `assets/scenes/`

### 5. Use ALL Available MCPs, Plugins, Skills, Agents
- **Context7** — Documentation lookup (EVERY iteration)
- **Serena** — Codebase navigation, symbol lookup, file operations
- **Pinecone** — If available, index key decisions for retrieval
- **Playwright** — Visual regression testing after each section
- **Code reviewer agent** — After each section completion
- **Security reviewer agent** — Before final section
- **Architect agent** — For structural decisions
- **TDD guide** — For any PHP function changes

### 6. Brand Constants (Hardcoded — Never Change)
- **Tagline**: No tagline is authorised (founder decision 2026-10-06).
- **RETIRED**: "Where Love Meets Luxury" — NEVER use this
- **Colors**: Rose Gold `#B76E79`, Dark `#0A0A0A`, Gold `#D4AF37`
- **Collection accents**: Black Rose `#C0C0C0` (silver), Love Hurts `#DC143C` (crimson), Signature `#D4AF37` (gold)
- **Fonts**: Archivo (display/headings), Hanken Grotesk (body/UI), Anton (UI caps), Cinzel (engraved caps), Inter (system/fallback) — self-hosted woff2 only, no Google Fonts CDN
- **API**: Use `index.php?rest_route=` (NOT `/wp-json/`)

### 7. Brand Asset Optimization & Injection (MANDATORY — Section 1)

All brand assets live in `assets/branding/` and `assets/images/`. They are oversized originals and MUST be optimized + injected into templates.

**Asset inventory:**

| File | Original Size | Dimensions | Needs |
|------|--------------|-----------|-------|
| `assets/images/skyyrose-logo-animated.gif` | 41MB | 1920x1080 | Convert to WebM/MP4 (<2MB). Use `<video autoplay muted loop playsinline>` |
| `assets/branding/skyyrose-monogram.webp` | 204KB | 2048x2048 | Resize to 60px (nav), 200px (footer). Rose gold SR with rose on white bg |
| `assets/branding/black-rose-logo.webp` | 356KB | 2048x2048 | Resize to 300px (collection hero), 40px (nav icon). Crystal star + black rose on black bg |
| `assets/branding/love-hurts-logo.webp` | 176KB | 1440x1440 | Resize to 300px (collection hero), 40px (nav icon). Crimson enamel pin heart — HAS WHITE BG, needs CSS treatment on dark pages |
| `assets/branding/signature-logo.webp` | 216KB | 2577x882 | Resize to 400px wide (collection hero), 120px (nav). Gold script "The Skyy Rose Collection" — HAS WHITE BG |
| `assets/branding/skyyrose-rose-icon.webp` | 497KB | 3000x3000 | Resize to 60px (favicon candidate), 120px (mobile nav) |
| `assets/images/sr-monogram-hero.png` | — | — | Static fallback for animated monogram in hero |
| `assets/images/sr-monogram-favicon.png` | — | — | Already sized for favicon |
| `assets/images/sr-monogram.png` | — | — | General use monogram |

**Optimization tasks (do in Section 1):**

1. **Animated monogram → video**: Run `ffmpeg -i assets/images/skyyrose-logo-animated.gif -vf "scale=640:-1" -an -c:v libvpx-vp9 -crf 35 -b:v 0 assets/images/skyyrose-monogram-hero.webm` (target <2MB). Also generate MP4 fallback: `ffmpeg -i skyyrose-logo-animated.gif -vf "scale=640:-1" -an -movflags +faststart -c:v libx264 -crf 28 assets/images/skyyrose-monogram-hero.mp4`
2. **Generate resized logo set** for each collection logo:
   - `{name}-nav.webp` — 40-60px height, for header navigation
   - `{name}-hero.webp` — 300-400px, for collection page heroes
   - `{name}-thumb.webp` — 120px, for grid cards and mobile
   - Use: `cwebp -resize 0 60 input.webp -o output-nav.webp` or ffmpeg/ImageMagick
3. **White-bg logos on dark pages**: For Love Hurts and Signature logos (white backgrounds), either:
   - Remove the white bg (make transparent) using ImageMagick: `convert input.webp -fuzz 10% -transparent white output.webp`
   - OR use CSS `mix-blend-mode: multiply` on dark backgrounds (simpler but less clean)
   - OR use CSS `filter: brightness(0) invert(1)` for monochrome treatment

**Where to inject logos:**

| Location | What to show | Size |
|----------|-------------|------|
| **Header nav (left)** | SR monogram (`skyyrose-monogram.webp`) | 40-50px height |
| **Homepage hero** | Animated monogram (WebM video) + "SKYYROSE" text below | 300-400px |
| **Email/newsletter capture sections** | Collection-specific logo as BACKGROUND (behind the email form) | 300-400px, low opacity |
| **Collection nav cards** | Collection logo thumbnails | 60-80px |
| **Footer** | SR monogram | 60px |
| **Favicon** | `sr-monogram-favicon.png` | 32x32 / 180x180 |
| **OG image fallback** | `sr-monogram-hero.png` or `sr-monogram-og.webp` | 1200x630 |
| **Mobile nav overlay** | SR monogram centered | 80px |
| **Loading screen** | SR monogram (static) or animated | 120px |

**IMPORTANT — Collection page heroes: KEEP SCENE IMAGES, NOT logos.**
- Collection heroes ALREADY have beautiful scene images from `assets/scenes/`. Do NOT replace them with logos.
- Black Rose hero → scene images from `assets/scenes/black-rose/`
- Love Hurts hero → scene images from `assets/scenes/love-hurts/`
- Signature hero → scene images from `assets/scenes/signature/`

**Collection logos go in EMAIL/NEWSLETTER CAPTURE sections instead:**
- Each landing page and collection page has an email capture section at the bottom
- Use the collection logo as a large, low-opacity background behind the email form
- Black Rose email section: `black-rose-logo-hero.webp` at ~20% opacity behind form
- Love Hurts email section: `love-hurts-logo-hero.webp` at ~20% opacity behind form
- Signature email section: `signature-logo-hero.webp` at ~20% opacity behind form
- CSS: `position: absolute; opacity: 0.15; z-index: 0; filter: blur(1px);` with the form content at `z-index: 1`

**In `header.php`:**
- Replace text-only "SKYYROSE" nav brand with: `<img>` of SR monogram at 40-50px + "SKYYROSE" text next to it
- On scroll (`.nav.scrolled`), monogram shrinks slightly
- Mobile: monogram only (hide text), hamburger on right

---

## Conversion Architecture (From Package README)

Each landing page has an **8-section conversion framework**:
1. Urgency hero + countdown timer
2. Founder story + parallax divider
3. 4-product grid with cost-per-wear calculator + scarcity indicators
4. 5-image lookbook gallery
5. 3 reviews + 4 press logos (social proof)
6. 4 craft/detail cards
7. 5-item FAQ accordion
8. Email capture form

**Sales funnel flow:**
```
Homepage → Landing Pages → Collection Pages → Single Product → Pre-Order/Cart
     ↑           ↑              ↑                 ↑
     └── Interactive Scenes (3D) ──┘ (DO NOT TOUCH THESE)
```

---

## Execution Plan — 7 Sections

### SECTION 1: Foundation & Configuration (Iterations 1-4)

**Goal**: Merge new theme foundation files, set up navigation, menus, SEO base.

1. **Read the entire design package** — every HTML file, every CSS/JS file, the WP overlay
2. **Merge `functions.php`** — combine new Elite Web Builder functions with existing. Keep ALL existing hooks (security, SEO, accessibility, enqueue). Add new menu registrations, asset enqueues
3. **Merge `style.css`** — update theme header to v4.0.0
4. **Deploy `assets/css/main.css`** — the new global stylesheet (CSS custom properties, typography, grain overlay, animations)
5. **Set up navigation/menus**:
   - Primary nav: Home, Collections (dropdown: Black Rose, Love Hurts, Signature), About, Pre-Order
   - Footer nav: Shop, About, Contact, FAQ, Privacy, Terms
   - Collection nav: Cross-collection navigation
   - Mobile hamburger menu with full-screen overlay
6. **SEO base**:
   - Open Graph tags on every page
   - JSON-LD structured data (Organization, Product, BreadcrumbList)
   - Canonical URLs, meta descriptions per page
   - XML sitemap registration
   - Schema.org markup for products
7. **Configuration**:
   - `wp_enqueue_style/script` for all new assets with conditional loading
   - Self-hosted woff2 fonts (assets/fonts/ via theme.json Font Library / assets/css/fonts.css) — NO Google Fonts CDN, no preconnect
   - Critical CSS inlining for above-fold
   - `prefers-reduced-motion` support globally

**Context7 queries**: WordPress `register_nav_menus`, `wp_enqueue_style`, `add_theme_support`, WooCommerce theme support hooks.

**After Section 1 — FREE RANGE BONUS**: Add 2 industry-proven features to optimize site and drive customers. Examples: progressive image loading, smart preloading, cookie consent, accessibility widget, performance monitoring. YOUR CHOICE — pick what will have the highest impact.

---

### SECTION 2: Homepage Makeover (Iterations 5-8)

**Goal**: Replace `front-page.php` with the new Elite Web Builder homepage design.

**Source**: `docs/elite-web-builder-package/homepage/index.html`

**HOMEPAGE HERO — CUSTOM DESIGN (OVERRIDES the package hero):**

The homepage hero is NOT the one in the HTML package. Use this custom design instead:

```
┌─────────────────────────────────────────────────────────┐
│                     (dark void bg)                      │
│                                                         │
│              ┌─────────────────────┐                    │
│              │   SR MONOGRAM GIF   │                    │
│              │   (animated reveal) │                    │
│              │   rose gold on dark │                    │
│              └─────────────────────┘                    │
│                                                         │
│          S   K   Y   Y   R   O   S   E                 │
│          ← single row, wide letter-spacing →            │
│                                                         │
│                                                         │
│                                                         │
│         [ SHOP NOW ]    [ EXPLORE ]                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Implementation details:**
- **Monogram GIF**: `assets/images/skyyrose-logo-animated.gif` (41MB, 1920x1080)
  - CRITICAL: 41MB is too heavy for web. OPTIMIZE IT:
    - Option A: Convert to WebM/MP4 video (use `<video autoplay muted loop playsinline>`) — best compression
    - Option B: Convert to APNG or WebP animation
    - Option C: Use ffmpeg to reduce frames/resolution: `ffmpeg -i skyyrose-logo-animated.gif -vf "scale=640:-1" -r 15 skyyrose-monogram.webm`
    - Target: under 2MB for the optimized version
  - Center the monogram vertically in the hero viewport
  - The GIF plays once on load, then holds the final frame (or loops subtly)
- **"SKYYROSE" text**: ONE ROW, Cinzel font, wide letter-spacing (clamp(8px, 2vw, 20px))
  - Positioned BELOW the monogram (not overlaid ON the GIF)
  - Rose gold shimmer gradient on the text: `background: linear-gradient(135deg, #B76E79, #D4AF37, #B76E79); -webkit-background-clip: text;`
  - Font size: `clamp(32px, 6vw, 72px)` — scales but stays on ONE LINE
  - `white-space: nowrap` to enforce single row
- **CTA buttons**: Two side-by-side — "SHOP NOW" (solid rose gold) + "EXPLORE" (outline)
- **Background**: Keep the atmospheric particles, grain overlay, and vignette from the package design
- **Mobile**: Monogram scales down to 200px wide, text shrinks, CTAs stack vertically

**Static fallback for monogram (hero PNG):** `assets/images/sr-monogram-hero.png` — use as `poster` frame or `<noscript>` fallback.

**The rest of the homepage (below the hero) follows the package design:**
- Cinematic loader (brand + progress bar)
- Fixed nav with scroll state change
- 3 featured product spotlights (one per collection, full-bleed with size selector + add-to-bag)
- Full catalog grid (all products across collections, filterable)
- About/brand story section
- Social proof (reviews, press logos)
- Newsletter capture
- Footer with sitemap

**Convert from HTML → WordPress PHP:**
- Replace hardcoded products with WooCommerce product queries (`wc_get_products()`)
- Replace base64 images with `get_template_directory_uri()` asset references
- Add WooCommerce AJAX add-to-cart functionality
- Use WordPress template parts for reusable sections
- Extract CSS into `assets/css/homepage.css`
- Extract JS into `assets/js/homepage.js`

**Context7 queries**: WooCommerce `wc_get_products()`, WordPress template parts, AJAX add-to-cart.

**After Section 2 — FREE RANGE BONUS**: Add 2 industry-proven features. Examples: smart product recommendations, recently viewed carousel, exit-intent popup, A/B test hooks.

---

### SECTION 3: Landing Pages — Conversion Engines (Iterations 9-14)

**Goal**: Create 3 new landing page templates from the Elite Web Builder conversion pages.

**Sources**:
- `docs/elite-web-builder-package/landing-pages/lp-black-rose.html`
- `docs/elite-web-builder-package/landing-pages/lp-love-hurts.html`
- `docs/elite-web-builder-package/landing-pages/lp-signature.html`

**Create new templates**:
- `template-landing-black-rose.php`
- `template-landing-love-hurts.php`
- `template-landing-signature.php`

**Each landing page implements the 8-section conversion framework:**
1. Hero with countdown timer (reads from `get_option('skyyrose_preorder_deadline')`)
2. Founder story with parallax
3. Product grid with cost-per-wear + scarcity ("Only X left")
4. Lookbook gallery (lightbox)
5. Reviews + press logos
6. Craft detail cards
7. FAQ accordion
8. Email capture (hooked to admin-ajax.php)

**CSS**: Extract per-collection accent colors into `assets/css/landing-{collection}.css`
**JS**: Extract countdown, scarcity, parallax, FAQ accordion into `assets/js/landing-engine.js`

**Context7 queries**: WordPress `get_option()`, AJAX handler `wp_ajax_*`, WooCommerce stock queries.

**After Section 3 — FREE RANGE BONUS**: Add 2 industry-proven features. Examples: social sharing buttons, referral program widget, urgency notifications, live visitor count.

---

### SECTION 4: Collection Pages — Full Product Showcases (Iterations 15-18)

**Goal**: Replace existing `template-collection-{slug}.php` with new Elite Web Builder collection pages.

**Sources**:
- `docs/elite-web-builder-package/collection-pages/black-rose.html`
- `docs/elite-web-builder-package/collection-pages/love-hurts.html`
- `docs/elite-web-builder-package/collection-pages/signature.html`

**Replace these existing templates**:
- `template-collection-black-rose.php` → new version
- `template-collection-love-hurts.php` → new version
- `template-collection-signature.php` → new version

**Keep**: `template-collection-kids-capsule.php` (do NOT replace, just ensure nav links to it)

**Each collection page has:**
- Full-bleed hero with collection branding
- Product grid with hover effects, quick-view capability
- Sort/filter controls
- Cross-collection navigation (link to other 2 collections)
- Pre-order CTA section
- Link to immersive experience

**Context7 queries**: WooCommerce product queries by category, WordPress taxonomy queries.

**After Section 4 — FREE RANGE BONUS**: Add 2 industry-proven features. Examples: quick-view modal, product comparison tool, wishlist integration, size guide popup.

---

### SECTION 5: Single Product Pages (Iterations 19-22)

**Goal**: Deploy the Elite Web Builder single product template with collection-aware theming.

**Sources**:
- `docs/elite-web-builder-package/product-pages/product-black-rose.html`
- `docs/elite-web-builder-package/product-pages/product-love-hurts.html`
- `docs/elite-web-builder-package/product-pages/product-signature.html`
- `docs/elite-web-builder-package/wordpress-theme/skyyrose-flagship/woocommerce/single-product.php`
- `docs/elite-web-builder-package/wordpress-theme/skyyrose-flagship/inc/wc-product-functions.php`
- `docs/elite-web-builder-package/wordpress-theme/skyyrose-flagship/assets/css/single-product.css`
- `docs/elite-web-builder-package/wordpress-theme/skyyrose-flagship/assets/js/single-product.js`

**Deploy**:
- `woocommerce/single-product.php` — collection-aware single product (3 visual worlds)
- `inc/wc-product-functions.php` — helper functions (collection detection, related products)
- `assets/css/single-product.css` — per-collection product page styling
- `assets/js/single-product.js` — image gallery, size selector, AJAX cart, tabs

**The single product detects collection via WooCommerce category and applies:**
- Black Rose: silver/monochrome theme (#C0C0C0)
- Love Hurts: crimson/gothic theme (#DC143C)
- Signature: gold/opulence theme (#D4AF37)

**Context7 queries**: WooCommerce single product hooks, `woocommerce_before_single_product`, product gallery, variations.

**After Section 5 — FREE RANGE BONUS**: Add 2 industry-proven features. Examples: sticky add-to-cart bar, product image zoom, size recommendation AI, back-in-stock notifications.

---

### SECTION 6: About Page + Global Polish (Iterations 23-26)

**Goal**: Deploy the cinematic About page and polish all global elements.

**Source**: `docs/elite-web-builder-package/homepage/about.html`
**IMPORTANT**: Despite being in the `homepage/` folder, `about.html` is NOT the homepage. It is a standalone About page. Convert it to `template-about.php` — a SEPARATE template from `front-page.php`.

**About page features:**
- Cinematic hero with parallax
- Founder story with timeline
- YouTube video embed (The Blox interview)
- Press room with logos
- Team/brand values section
- Newsletter CTA

**Global polish:**
- Verify all menu links work (primary, footer, collection, mobile)
- Verify breadcrumb navigation across all pages
- Test WooCommerce cart flow: add-to-cart → cart page → checkout
- Verify responsive design on all templates (mobile, tablet, desktop)
- Performance: lazy-load images, defer non-critical JS, minify CSS
- Accessibility: ARIA labels, focus management, keyboard navigation
- 404 page styling consistency with new design language

**Context7 queries**: WordPress breadcrumbs, WooCommerce cart fragments, responsive design best practices.

**After Section 6 — FREE RANGE BONUS**: Add 2 industry-proven features. Examples: customer reviews/testimonials slider, Instagram feed integration, loyalty/rewards preview, blog/lookbook section.

---

### SECTION 7: SEO, Config Lockdown & Final QA (Iterations 27-30)

**Goal**: Final SEO, configuration, and quality assurance pass.

**SEO Final Pass:**
- Verify every page has: title tag, meta description, OG image, OG title, OG description
- JSON-LD structured data: Organization (homepage), Product (each product), BreadcrumbList (all pages)
- Robots.txt configuration
- Canonical URLs (prevent duplicate content)
- Internal linking audit (every page links to at least 2 other pages)
- Image alt text audit (every `<img>` has descriptive alt)
- Page speed considerations: critical CSS, font-display swap, image optimization

**Configuration Lockdown:**
- Verify all `wp_enqueue_style/script` calls are conditional per template
- Verify security headers are intact (`inc/security.php`)
- Verify AJAX handlers have nonce verification
- Verify all forms have CSRF tokens
- Verify no inline `onerror` handlers (CSP compliance)
- Verify `index.php?rest_route=` used everywhere (not `/wp-json/`)

**Final QA Checklist:**
- [ ] Homepage loads, hero animates, products display
- [ ] All 3 landing pages render correctly
- [ ] All 3 collection pages show correct products
- [ ] Single product pages detect collection and apply correct theme
- [ ] About page renders with video embed
- [ ] Pre-order gateway still works
- [ ] Cart add/remove works via AJAX
- [ ] Mobile responsive on all pages
- [ ] All menu links resolve correctly
- [ ] Immersive pages still work (untouched)
- [ ] No console errors on any page
- [ ] All images load (no broken references)

**After Section 7 — FREE RANGE BONUS**: Add 2 industry-proven FINAL features. Examples: PWA service worker, web vitals monitoring, heatmap integration prep, structured data testing, performance budget enforcement.

---

## How to Convert HTML → WordPress PHP

For each HTML file in the package:

1. **Read the HTML file** completely — understand all sections, CSS, JS, data
2. **Extract CSS** → create `assets/css/{page-name}.css` with clean selectors
3. **Extract JS** → create `assets/js/{page-name}.js` with proper event listeners
4. **Convert base64 images** → reference existing assets in `assets/images/` or create new ones
5. **Replace hardcoded products** → use WooCommerce queries (`wc_get_products()`, `get_terms()`)
6. **Replace hardcoded text** → use WordPress functions where appropriate (`bloginfo()`, `get_option()`)
7. **Add WordPress template header** → `/* Template Name: Page Name */`
8. **Add proper escaping** → `esc_html()`, `esc_attr()`, `esc_url()` on all output
9. **Add to `functions.php`** → conditional `wp_enqueue_style/script` for this template
10. **Test** → verify no PHP errors, all sections render

---

## Iteration Protocol

Every iteration, you MUST:

1. State which section and task you're working on
2. Query Context7 for relevant docs (log the query)
3. Use Serena to navigate/edit files
4. Update `ralph-tasks.md` with progress
5. **COMMIT every iteration** — `git add` the changed files and `git commit -m "feat(theme): [section N] description"` at the END of every single iteration. No exceptions. Every iteration = 1 commit minimum.
6. If completing a section: run code review agent, update Serena memory, then **deploy to WordPress.com** via `bash scripts/wp-deploy-theme.sh` (requires `.env.wordpress` credentials to be set)
7. If completing a FREE RANGE BONUS: explain what you added and WHY it drives customers
8. If deploy script fails (credentials not set), log the failure in `ralph-tasks.md` and continue — do NOT block on deploy

---

## SFTP Deployment to WordPress.com

After completing each **section** (not every iteration, just section milestones), deploy to the live site:

```bash
# Full theme sync to WordPress.com Atomic
bash scripts/wp-deploy-theme.sh

# Dry-run preview first
bash scripts/wp-deploy-theme.sh --dry-run

# Single file deploy
bash scripts/wp-deploy-theme.sh --file assets/css/homepage.css
```

**Credentials** are in `.env.wordpress`:
- Host: `sftp.wp.com`, Port: `22`
- User: `skyyrose.co`
- Password: from wp-admin > Hosting Configuration > SFTP/SSH
- Remote path: `/htdocs/wp-content/themes/skyyrose-flagship/`

If `.env.wordpress` has `FILL_THIS_IN` placeholders, the deploy will fail gracefully. Log it and move on — the user will fill in creds later.

---

## END-TO-END WORDPRESS SETUP (CRITICAL — Not Just Theme Files)

Building theme PHP/CSS/JS is only HALF the job. You MUST also configure WordPress itself so the site actually works end-to-end. This means setting up pages, menus, categories, navigation, and SEO inside WordPress using the WordPress.com MCP tools and/or WP-CLI via the deploy script.

### A. WordPress Pages (Create via WP REST API or MCP)

Every template needs a corresponding WordPress **Page** assigned to it. Create these pages if they don't already exist:

| Page Title | Template | Slug |
|-----------|----------|------|
| Home | front-page.php | `home` (set as static front page) |
| About | template-about.php | `about` |
| Black Rose Collection | template-collection-black-rose.php | `collection-black-rose` |
| Love Hurts Collection | template-collection-love-hurts.php | `collection-love-hurts` |
| Signature Collection | template-collection-signature.php | `collection-signature` |
| Kids Capsule | template-collection-kids-capsule.php | `collection-kids-capsule` |
| Black Rose Landing | template-landing-black-rose.php | `landing-black-rose` |
| Love Hurts Landing | template-landing-love-hurts.php | `landing-love-hurts` |
| Signature Landing | template-landing-signature.php | `landing-signature` |
| Black Rose Experience | template-immersive-black-rose.php | `experience-black-rose` |
| Love Hurts Experience | template-immersive-love-hurts.php | `experience-love-hurts` |
| Signature Experience | template-immersive-signature.php | `experience-signature` |
| Pre-Order | template-preorder-gateway.php | `pre-order` |
| Contact | template-contact.php | `contact` |
| Wishlist | page-wishlist.php | `wishlist` |
| Style Quiz | template-style-quiz.php | `style-quiz` |

**How to create/assign pages:**
- Use WordPress.com MCP `wpcom-mcp-content-authoring` → `pages.create` with `template` field
- Or add to `functions.php` with `wp_insert_post()` on `after_switch_theme` hook
- Set "Home" as static front page: `update_option('show_on_front', 'page')` + `update_option('page_on_front', $home_id)`

### B. WooCommerce Product Categories

Create these categories if they don't exist (they map to collection detection in templates):

| Category | Slug | Description | Parent |
|----------|------|-------------|--------|
| Black Rose | `black-rose` | Gothic luxury streetwear — Silver #C0C0C0 | — |
| Love Hurts | `love-hurts` | Passionate crimson collection — #DC143C | — |
| Signature | `signature` | Bay Area gold essentials — #D4AF37 | — |
| Kids Capsule | `kids-capsule` | Youth collection | — |

**How**: Use `wp_insert_term('Black Rose', 'product_cat', ['slug' => 'black-rose'])` in `functions.php` on `init` hook, or use WooCommerce REST API.

### C. Navigation Menus (MUST be wired in WordPress)

Register menus in `functions.php` AND create the actual menu items:

**Primary Navigation** (header):
```
Home → /
Collections ▼
  ├── Black Rose → /collection-black-rose/
  ├── Love Hurts → /collection-love-hurts/
  ├── Signature → /collection-signature/
  └── Kids Capsule → /collection-kids-capsule/
About → /about/
Pre-Order → /pre-order/
```

**Footer Navigation**:
```
Shop → /pre-order/
Collections → /collection-black-rose/
About → /about/
Contact → /contact/
FAQ → /about/#faq
Privacy Policy → /privacy-policy/
Terms of Service → /terms-of-service/
```

**Collection Navigation** (cross-collection links on collection pages):
```
Black Rose → /collection-black-rose/
Love Hurts → /collection-love-hurts/
Signature → /collection-signature/
```

**Mobile Menu** (hamburger overlay):
Same as Primary, but also includes:
```
Wishlist → /wishlist/
Style Quiz → /style-quiz/
Bag → /cart/
```

**How to create menus programmatically** (add to `functions.php` or `inc/menu-setup.php`):
```php
// On theme activation, create menus
function skyyrose_create_menus() {
    // Check if menu exists first
    if (!wp_get_nav_menu_object('Primary Navigation')) {
        $menu_id = wp_create_nav_menu('Primary Navigation');
        // Add menu items...
        wp_update_nav_menu_item($menu_id, 0, [
            'menu-item-title'  => 'Home',
            'menu-item-url'    => home_url('/'),
            'menu-item-status' => 'publish',
        ]);
        // ... etc
        // Assign to location
        set_theme_mod('nav_menu_locations', ['primary' => $menu_id]);
    }
}
add_action('after_switch_theme', 'skyyrose_create_menus');
```

### D. SEO Configuration (In WordPress, not just theme)

**Site-level settings** (via WordPress options or MCP):
- `blogname` → "SkyyRose — Oakland Luxury Streetwear"
- `blogdescription` → "Premium streetwear from Oakland, CA."
- Permalink structure → `/%postname%/` (pretty permalinks)
- Timezone → `America/Los_Angeles`
- Date format → `F j, Y`

**Per-page SEO** (add to each page's template):
- `<title>` tag — unique per page, include brand name
- `<meta name="description">` — unique per page, 155 chars max, include CTA
- `<meta property="og:title">` — same as title or shorter
- `<meta property="og:description">` — same as meta description
- `<meta property="og:image">` — hero image or product image per page
- `<meta property="og:url">` — canonical URL
- `<meta property="og:type">` — "website" for pages, "product" for products
- `<link rel="canonical">` — self-referencing canonical URL
- JSON-LD structured data per page type (see Section 7 for full spec)

**Sitemap**: WordPress.com auto-generates `/sitemap.xml` — verify it includes all pages.

**Robots.txt**: WordPress.com manages this — but verify it's not blocking crawlers:
```
User-agent: *
Allow: /
Sitemap: https://skyyrose.co/sitemap.xml
```

### E. WooCommerce Configuration

- **Shop page**: Set to Pre-Order page (or create a dedicated Shop page)
- **Cart page**: Ensure `/cart/` exists and is set in WooCommerce settings
- **Checkout page**: Ensure `/checkout/` exists and is set
- **My Account page**: Ensure `/my-account/` exists
- **Currency**: USD ($)
- **Enable guest checkout**: Yes (reduce friction)
- **Product image sizes**: Main 600x800, Thumbnail 300x400, Gallery 100x133
- **Stock management**: Enable stock management at product level (for scarcity indicators)

### F. Widget Areas / Sidebars (if applicable)

- Footer widget area: Social media icons, newsletter signup, brand tagline
- Remove default WordPress widgets (Recent Posts, Archives, etc.) — not on-brand

### G. Reading Settings

- Front page: Static page → "Home"
- Posts page: None (or create a "Journal" page if blog is desired)
- Search engine visibility: Allow search engines to index this site

---

## WordPress.com MCP Integration

Use the WordPress.com MCP tools when available:
- `wpcom-mcp-content-authoring` → Create/update pages, assign templates, manage media
- `wpcom-mcp-site-editor-context` → Get theme presets, design tokens, block types
- `wpcom-mcp-site-settings` → Verify/update site settings (title, tagline, permalinks)

If MCP session is expired, fall back to:
1. Adding `wp_insert_post()` / `update_option()` calls in `functions.php` on `after_switch_theme`
2. Or document the manual steps in a `SETUP.md` for the user to execute in wp-admin

**Prefer programmatic setup** (auto-runs on theme activation) over manual wp-admin steps.

---

## Elite Web Builder Identity

You are the **Elite Web Builder** — a Fortune 500-tier web development team. You build conversion-optimized, enterprise-grade WordPress themes. Your work is:
- Pixel-perfect translations from design to code
- Performance-optimized (sub-3s load times)
- Accessibility-compliant (WCAG 2.1 AA)
- SEO-maximized (Core Web Vitals green)
- Security-hardened (OWASP Top 10)
- Mobile-first responsive
- Conversion-engineered (every element drives action)

**Let's build.**

---

## PRIORITY TASK: New Homepage Build (OVERRIDES Section 2)

**Source file**: `/Users/theceo/Downloads/skyyrose-homepage.html` (530 lines, 836KB)

This is an **updated, refined homepage design** that supersedes both the original Elite Web Builder `homepage/index.html` AND whatever was previously built in `front-page.php`. Convert this ENTIRE HTML file into the WordPress `front-page.php` template, replacing the current content.

### Page Structure (10 sections, in order)

1. **Loader** — Brand name + tagline + tri-color gradient progress bar (silver→crimson→gold)
2. **Nav** — Fixed header with brand name + "Oakland Luxury" sub, centered links (Story, Collections, Lookbook, Craft, Community), right-side Bag button, mobile hamburger + fullscreen overlay
3. **Hero** — Full-viewport with background image zoom animation, particle system (6 rose-gold particles), decorative frame lines, giant "SKYYROSE" text with multi-stop gradient animation (`gradShift` keyframes), hero rule line, subtitle, dual CTAs ("Explore Collections" + "Our Story")
4. **Press Strip** — "Featured In" logos: MAXIM, SAN FRANCISCO POST, CEO WEEKLY, EAST BAY EXPRESS, THE BLOX
5. **Marquee** — Scrolling ticker: "OAKLAND LUXURY · GENDER NEUTRAL · LIMITED EDITION · EST. 2020 · PREMIUM MATERIALS · BAY AREA BORN"
6. **Story** — 2-column grid: left text (founder story with stats: 3 collections, 28+ designs, 100% gender neutral, Oakland CA), right image (3:4 aspect with floating "Oakland, CA" card)
7. **Quote** — Full-width centered blockquote: "I named this brand after my daughter because she's the reason I push harder..."
8. **Collections** — 3-column grid of collection cards (Black Rose, Love Hurts, Signature) each with background image, overlay gradient, collection number, name, tagline, meta (pieces + price range + tag), CTA button. Each card has unique color skin (`.br` silver, `.lh` crimson, `.sg` gold)
9. **Lookbook** — 5-cell grid with PLACEHOLDER images ("COMING SOON" styled by collection color). **IMPORTANT: Replace placeholders with ACTUAL product/customer images** from `assets/images/products/` and `assets/images/customers/` — we have 80+ product renders and 8 customer photos ready
10. **Craft** — 4-column card grid: Premium Materials, Oakland Made Mentality, Gender Neutral, Limited Editions
11. **Newsletter** — Email capture form with "Join the Movement" CTA
12. **Footer** — 4-column grid: brand description + awards, Collections links, Brand links, Support links + social links + copyright

### CSS Design System (Extract to `assets/css/homepage-v2.css`)

The HTML has an entirely new CSS variable system and design language. Key highlights:
- **Color tokens**: `--void:#08080A`, `--charcoal:#0E0E12`, `--smoke:#141418`, `--ash:#1A1A20` (dark scale), plus `--mist`/`--glass`/`--ghost`/`--fog`/`--haze`/`--cloud` (white opacity scale), plus RGB variants for all brand colors
- **Font stack**: Added `Instrument Serif` as `--ff-serif` alongside existing fonts. 6 font families total.
- **Animation system**: `--ease:cubic-bezier(.16,1,.3,1)`, `--ease-smooth:cubic-bezier(.4,0,.2,1)`. Reveal classes: `.rv` (fade-up), `.rv-left/right` (slide), `.rv-scale` (scale-in), with delay classes `.rv-d1` through `.rv-d6`
- **Grain + vignette overlays**: Fixed position, z-index 9500/9400, pointer-events none
- **Minified but well-organized**: ~240 lines of CSS covering loader, nav, hero, press, marquee, story, quote, collections, lookbook, craft, newsletter, footer, with responsive breakpoints at 1024px and 768px

### Cosmetic Issues to Fix

1. **Newsletter form mobile border** (line 259): When form stacks vertically on mobile, the `.nl-input` gets `border-right:1px solid var(--glass);border-bottom:none` — verify this creates a seamless visual join with the submit button below. If there's a gap, add `margin-top:-1px` on `.nl-submit` to collapse the border.

2. **`Signa&shy;ture` soft hyphen** (line 402): The Signature collection card name has `Signa&shy;ture` which may cause an ugly mid-word break on certain viewport widths. Either remove the `&shy;` entirely OR use `word-break:keep-all` on `.col-card-name` to prevent orphaned hyphens.

3. **Lookbook all-placeholders**: Every lookbook cell is a styled "COMING SOON" placeholder. Replace with actual imagery — we have customer photos (`assets/images/customers/`) and product renders (`assets/images/products/`). Wire to `get_template_directory_uri()` paths. Keep the placeholder as `<noscript>` fallback or remove entirely.

4. **Cloudflare email protection**: Line 505 references `/cdn-cgi/scripts/5c5dd728/cloudflare-static/email-decode.min.js` and line 495 uses Cloudflare email obfuscation for the contact email. Remove Cloudflare scripts — use WordPress `antispambot()` for email protection instead.

5. **Hero background image**: Line 291 has an inline base64 background image on `.hero-bg`. Extract this to a proper asset file OR replace with the monogram animation as specified in the hero design above (Section 2 of the original directive). The `ralph-context.md` hero spec takes priority — use the animated monogram WebM/MP4 as the hero focal point, with this background image as the atmospheric backdrop.

6. **Collection card images**: Lines 374, 386, 398 have base64 inline images on `.col-card-img img`. Extract these to proper WebP files in `assets/images/` and reference via `get_template_directory_uri()`.

7. **Story section image**: Line 352 has a base64 inline image. Extract to a proper asset file.

### WordPress Conversion Requirements

- Replace `<script>` block at bottom with properly enqueued `assets/js/homepage-v2.js`
- Replace all `onclick="..."` with `addEventListener` in the JS file (CSP compliance)
- Replace all base64 images with `get_template_directory_uri()` asset paths
- Replace hardcoded text where appropriate with WordPress functions
- Add proper escaping: `esc_html()`, `esc_attr()`, `esc_url()`
- Add WooCommerce product queries for collection cards (product counts, price ranges)
- Wire newsletter form to WordPress AJAX (`wp_ajax_skyyrose_newsletter`)
- Wire cart button to WooCommerce cart
- Add JSON-LD structured data (Organization)
- Conditionally enqueue `homepage-v2.css` and `homepage-v2.js` only on front page
- Split reusable sections into `template-parts/front-page/` partials

### Context7 Queries Required

Before ANY code:
1. WordPress `wp_enqueue_style` / `wp_enqueue_script` conditional loading
2. WooCommerce `wc_get_products()` for collection card data
3. WordPress `antispambot()` for email protection
4. WordPress AJAX API for newsletter form
5. WordPress `get_template_directory_uri()` for asset paths

### After Build — FREE RANGE BONUS

Add 2 industry-proven features to the new homepage. Suggestions:
- Scroll-triggered collection card parallax tilt effect
- "Back to top" floating button that appears after first scroll
- Animated counter for the story stats section (count up on scroll)
- Lazy-loaded lookbook images with blur-up placeholder technique

### Commit

After completing this task: `git commit -m "feat(theme): rebuild front-page.php from updated homepage design v2"`

---

## IMPROVEMENT 1: Asset Pipeline — Conditional CSS/JS Loading + Minification

**Problem**: 53 CSS files and 24 JS files ALL load globally on EVERY page. A visitor on the homepage downloads CSS for the contact page, 404, style quiz — none of which they need. Nothing is minified. This kills Core Web Vitals (LCP, FCP, TBT).

### Tasks

**A. Conditional Enqueue Audit & Fix (`inc/enqueue.php`)**

Read `inc/enqueue.php` fully. Then restructure `wp_enqueue_style` / `wp_enqueue_script` calls so each asset loads ONLY on pages that need it:

```php
// PATTERN: Conditional enqueue per template
function skyyrose_enqueue_page_assets() {
    // Homepage only
    if ( is_front_page() ) {
        wp_enqueue_style( 'skyyrose-homepage-v2', ... );
        wp_enqueue_script( 'skyyrose-homepage-v2', ... );
    }
    // Landing pages only
    if ( is_page_template( 'template-landing-black-rose.php' ) ||
         is_page_template( 'template-landing-love-hurts.php' ) ||
         is_page_template( 'template-landing-signature.php' ) ) {
        wp_enqueue_style( 'skyyrose-landing', ... );
        wp_enqueue_script( 'skyyrose-landing-engine', ... );
    }
    // Collection pages only
    if ( is_page_template( array( 'template-collection-black-rose.php', ... ) ) ) {
        wp_enqueue_style( 'skyyrose-collection-v4', ... );
        wp_enqueue_script( 'skyyrose-collection-v4', ... );
    }
    // Single product only
    if ( is_singular( 'product' ) ) {
        wp_enqueue_style( 'skyyrose-single-product', ... );
        wp_enqueue_script( 'skyyrose-single-product', ... );
    }
    // ... etc for about, contact, preorder, style-quiz, 404
}
```

**Keep global**: ONLY these should load on every page:
- `style.css` (theme base)
- `main.css` (CSS custom properties, grain, vignette)
- `design-tokens.css`
- `header.css` + `footer.css`
- `navigation.js`
- Self-hosted @font-face declarations (assets/css/fonts.css — no Google Fonts CDN, no preconnect)

**Everything else is per-page.** Audit every `wp_enqueue_*` call and wrap in the appropriate conditional.

**B. CSS/JS Minification**

For each CSS and JS file Ralph created, generate a `.min` version. Use one of these approaches:
1. **WP-CLI**: If available, use a minification plugin's CLI (`wp autoptimize optimize`)
2. **Shell**: Use `npx terser` for JS and `npx csso-cli` for CSS — run from repo root:
   ```bash
   # JS minification
   for f in assets/js/*.js; do npx terser "$f" --compress --mangle -o "${f%.js}.min.js"; done
   # CSS minification
   for f in assets/css/*.css; do npx csso-cli "$f" -o "${f%.css}.min.css"; done
   ```
3. **In enqueue.php**: Serve `.min` versions when not in debug mode:
   ```php
   $suffix = ( defined( 'SCRIPT_DEBUG' ) && SCRIPT_DEBUG ) ? '' : '.min';
   wp_enqueue_style( 'skyyrose-homepage-v2', get_template_directory_uri() . "/assets/css/homepage-v2{$suffix}.css", ... );
   ```

**C. Bundle Related Engine CSS**

These "engine" CSS files are loaded by Ralph's bonus features. Bundle related ones:
- `aurora-engine.css` + `pulse-engine.css` + `velocity-scroll.css` → `engines-bundle.css` (only on pages using them)
- `adaptive-personalization.css` + `journey-gamification.css` → `personalization-bundle.css` (only on interactive pages)
- `the-pulse.css` → merge into `engines-bundle.css`

**Context7**: Query WordPress `SCRIPT_DEBUG` constant, `wp_enqueue_style` conditional patterns, `is_page_template()` array syntax.

### Commit

`perf(theme): conditional CSS/JS enqueue + minification pipeline`

---

## IMPROVEMENT 2: Image Optimization — Kill the 299MB Theme

**Problem**: Theme is 299MB. That 41MB GIF is the worst offender, but scene PNGs (1.8–9.4MB each) and product WebPs (up to 1.7MB) are also bloated. This makes SFTP deploys take forever and hurts TTFB.

### Tasks

**A. Animated Monogram GIF → Video (MUST DO)**

If `assets/images/skyyrose-monogram-hero.webm` and `.mp4` don't already exist (check first!), generate them:
```bash
cd wordpress-theme/skyyrose-flagship
# WebM VP9 (target <1MB)
ffmpeg -i assets/images/skyyrose-logo-animated.gif -vf "scale=640:-1" -an -c:v libvpx-vp9 -crf 35 -b:v 0 assets/images/skyyrose-monogram-hero.webm
# MP4 H.264 fallback (target <300KB)
ffmpeg -i assets/images/skyyrose-logo-animated.gif -vf "scale=640:-1" -an -movflags +faststart -c:v libx264 -crf 28 assets/images/skyyrose-monogram-hero.mp4
```
Then **verify** they play correctly. If they already exist, check their file sizes and quality.

**B. Scene PNGs → WebP (Batch Convert)**

Convert all PNG scene images to WebP. Target <500KB per image:
```bash
cd wordpress-theme/skyyrose-flagship/assets/scenes
for dir in black-rose love-hurts signature; do
  for f in "$dir"/*.png; do
    [ -f "$f" ] && cwebp -q 82 -resize 1920 0 "$f" -o "${f%.png}.webp"
  done
done
```
After conversion, update any PHP/CSS references from `.png` to `.webp`.
DO NOT delete the PNGs yet — just add the WebPs alongside.

**C. Product Image Audit**

Check `assets/images/products/` for any files over 500KB:
```bash
find assets/images/products/ -type f -size +500k -exec ls -lh {} \;
```
For any over 500KB, resize: `cwebp -q 80 -resize 800 0 input.webp -o output.webp`

**D. Lazy Loading + srcset on All Templates**

Audit ALL templates for `<img>` tags. Every image below the fold MUST have:
- `loading="lazy"` attribute
- `decoding="async"` attribute
- `width` and `height` attributes (prevents CLS)

For hero/above-fold images, use `fetchpriority="high"` instead of lazy.

**E. Remove Duplicate Formats**

Find cases where the same image exists in multiple formats (PNG + JPG + WebP). Keep only WebP. Example found: `black-rose-moonlit-courtyard.png` (9.4MB) + `.jpg` (2.3MB) — keep only WebP.

**Context7**: Query WordPress `wp_get_attachment_image()` srcset support, `loading` attribute, `fetchpriority` attribute.

### Commit

`perf(theme): optimize images — GIF→video, PNG→WebP, lazy loading`

---

## IMPROVEMENT 3: CSS Architecture — From 53 Files to a Design System

**Problem**: 53 CSS files with creative names (`aurora-engine.css`, `magnetic-obsidian.css`, `the-pulse.css`) that nobody can maintain. Reveal animations (`.rv`, `.rv-d1`–`.rv-d6`), grain overlay, vignette, and typography resets are probably duplicated across 5+ files. No single source of truth.

### Tasks

**A. Audit for Duplication**

Search ALL CSS files for these commonly duplicated patterns:
```bash
# Reveal animations
grep -rn "\.rv{" assets/css/ | wc -l
grep -rn "\.rv-d1" assets/css/ | wc -l
# Grain overlay
grep -rn "\.grain{" assets/css/ | wc -l
grep -rn "fractalNoise" assets/css/ | wc -l
# Vignette
grep -rn "\.vignette{" assets/css/ | wc -l
# Typography resets
grep -rn "ff-brand\|ff-body\|ff-mono\|ff-editorial" assets/css/ | wc -l
```

Report the duplication count. If `.rv` is defined in more than 2 files, it MUST be extracted.

**B. Create Design System CSS (Single Source of Truth)**

Create these foundational files that OTHER CSS files import/depend on:

1. **`assets/css/system/tokens.css`** — ALL CSS custom properties (colors, fonts, spacing, easing). Every variable currently scattered across files gets moved here.
2. **`assets/css/system/base.css`** — Resets, scrollbar, img/a/button defaults, grain, vignette, body styles. The stuff that currently repeats in every page CSS.
3. **`assets/css/system/animations.css`** — ALL reveal classes (`.rv`, `.rv-left`, `.rv-right`, `.rv-scale`, `.rv-d1`–`.rv-d6`), `@keyframes fadeUp`, `@keyframes heroIn`, shared transitions. ONE definition, every page uses it.
4. **`assets/css/system/components.css`** — Shared UI components: cards, buttons (`.hero-cta` pattern), forms (`.nl-form`, `.nl-input`), modals, tooltips.

Then update `inc/enqueue.php` to load the system CSS globally (it's small) and page CSS as overrides:
```php
// Global (every page) — <10KB total minified
wp_enqueue_style( 'skyyrose-tokens', .../system/tokens.css );
wp_enqueue_style( 'skyyrose-base', .../system/base.css, ['skyyrose-tokens'] );
wp_enqueue_style( 'skyyrose-animations', .../system/animations.css, ['skyyrose-tokens'] );
wp_enqueue_style( 'skyyrose-components', .../system/components.css, ['skyyrose-base'] );

// Page-specific (conditional)
if ( is_front_page() ) {
    wp_enqueue_style( 'skyyrose-homepage-v2', .../homepage-v2.css, ['skyyrose-components'] );
}
```

**C. Document Engine CSS**

For each "engine" CSS file that remains after deduplication, add a comment block at the top:
```css
/**
 * Aurora Engine — Ambient lighting effects (radial gradients, glow pulses)
 * Used on: Homepage, Landing pages, About page
 * Depends on: system/tokens.css, system/animations.css
 * Load: Conditional via inc/enqueue.php
 */
```

**D. Remove Dead CSS**

After extracting the design system, grep each remaining CSS file for selectors that NO PHP template references:
```bash
# For each selector in a CSS file, check if any PHP file uses that class
grep -oP '\.\w[\w-]+' assets/css/aurora-engine.css | sort -u | while read cls; do
  cls_name="${cls#.}"
  if ! grep -rq "$cls_name" *.php template-parts/ inc/; then
    echo "DEAD: $cls_name in aurora-engine.css"
  fi
done
```
Remove dead selectors to trim file sizes.

**Context7**: Query WordPress `wp_enqueue_style` dependency chains, CSS `@layer` support for cascade management.

### Commit

`refactor(theme): extract design system CSS, deduplicate, document engines`

---

## CONTEXT7 VERIFICATION PROTOCOL (When Docs May Be Stale)

Context7 does NOT always have the latest docs. When you query Context7 and the results seem outdated, incomplete, or suspicious, follow this **3-tier verification**:

### Tier 1: Context7 (Default — Always Try First)
```
resolve-library-id → query-docs
```
If the result is clear, current, and matches what you expect → proceed.

### Tier 2: WordPress Codex / WooCommerce Docs (Fallback)
If Context7 returns no results, outdated results, or you're unsure:
- Use `WebFetch` to check the official docs directly:
  - WordPress: `https://developer.wordpress.org/reference/functions/{function_name}/`
  - WooCommerce: `https://woocommerce.github.io/code-reference/`
  - WordPress hooks: `https://developer.wordpress.org/reference/hooks/{hook_name}/`
- Use `WebSearch` to find current docs: `"WordPress {function} site:developer.wordpress.org"`

### Tier 3: Source Code Verification (Last Resort)
If both Context7 and web docs are unclear:
- Check the actual WordPress core in `/htdocs/wp-includes/` via Serena/read tools
- Check WooCommerce source in `/htdocs/wp-content/plugins/woocommerce/`
- Or check the local WordPress install if available

### What to Verify
- **Function signatures**: Do the parameters match what Context7 says?
- **Hook names**: Are they still active in the current WP version? (e.g., `woocommerce_before_single_product` vs deprecated hooks)
- **Return types**: Does the function return what Context7 claims?
- **Deprecations**: Is the function deprecated in favor of something newer?

### Log Your Verification
In `ralph-tasks.md`, for EVERY Context7 query, log:
```
Context7: [library-id] → [topic] → [result status: current | stale | missing]
Fallback: [none | WebFetch | WebSearch | source] → [what you found]
```

If you find Context7 returned stale/wrong info, note it so we can track reliability.

---

## NEW MISSION: Phase 2 — Site Rebuild + Immersive Scene Generation (March 2026)

> Previous mission (Elite Web Builder v2 makeover) is COMPLETE. All 12 iterations verified green.
> This new phase focuses on **5 site rebuild fixes** + **3 immersive scene generations**.

### Phase 2A: Site Rebuild (Fix Broken Pages & Stale Assets)

**Problem**: Menu links point to pages that don't exist. Stale minified CSS. Duplicate CSS. Mobile nav broken.

**Tasks (in priority order):**

1. **Regenerate 9 stale `.min.css` files** — homepage.min.css is 3 days behind source, woocommerce-checkout.min.css is 5 days behind, etc.
   - Run: `for f in assets/css/*.css; do [[ "$f" != *.min.css ]] && npx csso-cli "$f" -o "${f%.css}.min.css"; done`
   - Verify: `find assets/css/ -name "*.min.css" -newer "$(ls -t assets/css/*.css | grep -v .min | head -1)" | wc -l`

2. **Create Experiences hub page** (`template-experiences.php`) — menu links to `/experiences/` but the page 404s
   - Create `template-experiences.php` with Template Name header
   - Layout: hero + grid of 3 immersive room cards (Black Rose, Love Hurts, Signature) linking to existing immersive templates
   - Create CSS: `assets/css/experiences.css` + minified version
   - Add conditional enqueue in `inc/enqueue.php`
   - Create WordPress page in `inc/theme-activation-setup.php` with template assignment
   - Context7 GATE: Query WordPress template hierarchy + `page_template` meta

3. **Create Collections hub page** (`template-collections.php`) — menu links to `/collections/` but the page 404s
   - Create `template-collections.php` with Template Name header
   - Layout: hero + grid of 3 collection cards linking to existing `template-collection-{slug}.php` pages
   - Pull real product counts + price ranges from WooCommerce (`wc_get_products()`)
   - Create CSS: `assets/css/collections.css` + minified version
   - Add conditional enqueue in `inc/enqueue.php`
   - Create WordPress page in `inc/theme-activation-setup.php` with template assignment
   - Context7 GATE: Query WooCommerce `wc_get_products()` for category aggregation

4. **Deduplicate homepage.css & collection-v4.css** — ~60% overlap in reveal animations, grid layouts, typography
   - Audit both files side-by-side, identify shared selectors
   - Extract shared rules to `assets/css/system/` (tokens.css or animations.css already exist — extend them)
   - Remove duplicated definitions from both page-specific files
   - Regenerate `.min.css` for all modified files
   - Verify: both homepage and collection pages still render correctly

5. **Fix mobile nav dropdown** — first tap should expand the submenu, second tap should navigate
   - Current: `navigation.js` lines 112-138 toggle `.focus` class but no `aria-expanded`
   - Fix: add `aria-expanded` toggle, prevent first-tap navigation on parent items with children
   - Add CSS for expanded state visibility
   - Context7 GATE: Query WordPress `wp_nav_menu` walker + accessibility best practices

### Phase 2B: Immersive Scene Generation (3 Scenes via Gemini)

**Script**: `scripts/gemini_scene_gen.py`
**Model**: `gemini-3-pro-image-preview` ($0.08/image, 4K resolution)
**Venv**: `.venv-imagery` (activate before running)

**Generate 1 scene per collection — iterate until each looks perfect:**

1. **Black Rose — Rooftop Garden** (`black-rose-rooftop-garden`)
   - Bay Bridge lit up at night, clear starry sky
   - Modern rooftop with black roses, lounge furniture, clothing rack
   - Products: Sherpa Jacket on lounge back, Hoodie on clothing rack, Joggers on ottoman, second Hoodie on accent chair
   - Run: `python scripts/gemini_scene_gen.py --scene black-rose-rooftop-garden`
   - Iterate: generate `--variants 3`, pick best, refine prompt if needed

2. **Love Hurts — Cathedral Rose Chamber** (`love-hurts-cathedral-rose-chamber`)
   - Gothic cathedral interior, enchanted rose under glass dome
   - Stained glass with red/pink light, candelabras, crimson petals
   - Products: Varsity Jacket beside glass dome, Fannie Pack on candelabra, Basketball Shorts on stone ledge
   - Run: `python scripts/gemini_scene_gen.py --scene love-hurts-cathedral-rose-chamber`

3. **Signature — Golden Gate Showroom** (`signature-golden-gate-showroom`)
   - Luxury showroom with panoramic Golden Gate Bridge at sunset (NOT Bay Bridge — that's in Black Rose)
   - Black marble interior, gold LED strips, clothing racks, marble pedestals
   - Products: Orchid Tee on left rack, Stay Golden Tee on center table, Beanie on pedestal, White Tee on right rack
   - Run: `python scripts/gemini_scene_gen.py --scene signature-golden-gate-showroom`

**After Generation:**
- Convert PNGs to WebP: `cwebp -q 85 input.png -o output.webp`
- Verify hotspot positions align with product locations
- Update template files to reference `-v2` filenames
- Test in browser at multiple viewport sizes

### Phase 2 Rules (Same as Phase 1)

- **Context7 HARD GATE** still applies — no code without querying docs first
- **Serena** for all WordPress file operations
- **Update `ralph-tasks.md`** after EVERY iteration
- **Immersive templates ARE in scope** — you may edit template-immersive-*.php, immersive.js, immersive.css as needed for scene integration
- **Brand constants**: Rose Gold `#B76E79`, Dark `#0A0A0A`, Silver `#C0C0C0`, Crimson `#DC143C`, Gold `#D4AF37`
- **Tagline**: none authorised (NEVER "Where Love Meets Luxury")
- **API**: Use `index.php?rest_route=` (NOT `/wp-json/`)
