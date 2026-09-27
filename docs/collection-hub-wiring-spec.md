# Collection Hub Wiring Spec

All claims below verified this session — engine read from the artifact bundle, theme wiring from the repo, URLs probed live.

# SCROLL-WORLD → COLLECTION HUB — Wiring Spec

**Two corrections to the brief before anything else (both load-bearing):**

1. **Collection URLs.** `/collection-black-rose/` etc. are LEGACY. Canonical is `/collections/{slug}/` — locked in structural remediation WS2, enforced by rewrite + 301 + `page_link` filter (`inc/redirects.php:56-152`) `[repo]`. `https://skyyrose.co/collections/black-rose/` serves 200/178KB `[live]`. All CTA hrefs in this spec use `/collections/{slug}/`.
2. **"6 worlds" is actually 5 + 1.** The artifact defines **5 scroll worlds** (`worldConfig()` in artifact-page.html:1411-1460 — signature, black-rose, love-hurts, kids-capsule, finale) `[repo]`; asset2.js is the engine only. The "6th world" is the **post-flight editorial hub** (marquee → Four Worlds blade accordion → stats band → pre-order → house closing → footer) that the artifact renders after the track ends. That structure is the answer to "the other 2": world 5 = **finale/conversion scene**, surface 6 = **the crawlable editorial index**. No new scene still is needed — the 5 tracked stills in `assets/scenes/collections-world/` (`git ls-files` confirms) `[repo]` cover it, and inventing a 6th render is banned.

---

## 1. What the hub replaces: the world BECOMES /collections/ (no redirect of /collections/)

**Decision: serve the world AT `/collections/`.** Do not redirect `/collections/` anywhere.

- `/collections/` is the indexed, linked, canonical index (200/96KB live `[live]`); every legacy route (`/collection-*`, `/experience-*`, `/experiences/`, Shopify `/products/*` fallback) already funnels into it (`redirects.php:125-184`) `[repo]`. Redirecting it to a new URL would launder all that equity through a 301 for zero gain.
- The current `/collections-world/` page (200/56KB live `[live]`) gets a **301 → `/collections/`** added to the `skyyrose_collection_redirects()` map. `template-collections-world.php` stays in the theme (commercial-theme feature; deletion needs its own census) but the dedicated page retires.
- **Mechanism:** `/collections/` is already force-routed to `page-collections.php` by `skyyrose_collections_index_template()` (`redirects.php:256-265`) `[repo]` — that stays. `page-collections.php` evolves into the merged hub: **world mount on top, server-rendered editorial index below** — exactly the artifact's own structure (`div#skyyrose-collections-world` followed by `[data-editorial]`).
- **SEO consequence handled:** the bare-canvas world alone would be an SEO regression (empty JS mount, zero crawlable links). Merged, the initial HTML keeps H1 + 4 collection `<a href="/collections/{slug}/">` cards + pre-order link (today's `ci-grid`). Crawlers and no-JS users see a complete index; the world is pure enhancement above it. Title/canonical/H1 of `/collections/` unchanged.
- The `IMPORTANT` warning in `template-collections-world.php:16-18` ("do NOT assign this template to the collections page") is obsoleted by this design and must be updated — the conflict it warns about (the `template_include` force) is now the delivery mechanism.

## 2. Config shape — the PHP that builds SKYY_SCROLL_WORLD_CONFIG

Engine facts that make this a config change `[repo asset2.js]`: CTAs render for **any** section that has `cta` (asset2.js:171 — the "last section only" note is convention, not code); `safeHref()` sanitizes; `cta.primary`/`cta.secondary` each take `{label, href}`; localization must stay `wp_add_inline_script` + `wp_json_encode` (never `wp_localize_script` — it stringifies `diveScroll` and freezes the engine, already documented at `enqueue.php:967-979`) `[repo]`.

Rewrite `skyyrose_get_collections_world_config()` (`inc/collections-world.php`) to:

```php
$col      = skyyrose_get_collections_config();          // SOT for slug/label/accent
$page_url = static fn( $slug ) => esc_url( home_url( '/collections/' . $slug . '/' ) );
// Piece counts: catalog CSV via skyyrose_get_collection_products() — NEVER the
// artifact's fictional 32/18/24/14.
$count    = static fn( $slug ) => count( skyyrose_get_collection_products( $slug ) );

$config = array(
    // NO 'brand', NO top-level 'cta': the theme header (sticky, transparent
    // .is-world-hub variant) owns brand + cart on /collections/. Engine topbar
    // then renders only the section nav — no double chrome.
    'hint'       => __( 'scroll to enter', 'skyyrose' ),
    'nav'        => true,
    'atmosphere' => false,
    'diveScroll' => 1.4,
    'crossfade'  => 0.12,
    'headingLevel' => 2,   // new engine option: server H1 lives in the editorial index
    'sections'   => array(
        array_merge( $assets( 'scene-1-signature' ), array(
            'id' => 'signature', 'label' => $col['signature']['label'],
            'accent' => SKYYROSE_COLOR_GOLD, 'scroll' => 1.6, 'linger' => 0.4,
            'eyebrow' => __( 'The Signature', 'skyyrose' ),
            'title'   => __( '', 'skyyrose' ),
            'body'    => __( 'Oakland-born luxury, cut in gold and earned on the block.', 'skyyrose' ),
            'tags'    => array( __( 'Signature', 'skyyrose' ), __( 'Gold', 'skyyrose' ),
                               sprintf( __( '%d Pieces', 'skyyrose' ), $count( 'signature' ) ) ),
            'cta'     => array( 'primary' => array(
                'label' => __( 'Enter Signature', 'skyyrose' ),
                'href'  => $page_url( 'signature' ) ) ),
        ) ),
        // black-rose  — accent SKYYROSE_COLOR_SILVER,  cta.primary → $page_url('black-rose'),
        //               copy: 'Worn As Armor' (armor canon)
        // love-hurts  — accent SKYYROSE_COLOR_CRIMSON, cta.primary → $page_url('love-hurts'),
        //               copy: 'The Bloodline That Raised Me' (bloodline canon)
        // kids-capsule— accent SKYYROSE_COLOR_ROSE_GOLD, cta.primary → $page_url('kids-capsule')
        //   (same shape as signature; existing copy in inc/collections-world.php is
        //    already canon-correct — keep it, add cta + real count tag)
        array_merge( $assets( 'scene-5-finale' ), array(
            'id' => 'finale', 'label' => __( 'The Collection', 'skyyrose' ),
            'accent' => SKYYROSE_COLOR_ROSE_GOLD, 'linger' => 0.3,
            'eyebrow' => __( 'The Skyy Rose Collection', 'skyyrose' ),
            'title'   => __( 'Enter The Collections', 'skyyrose' ),
            'body'    => __( 'Four cinematic worlds, one house built from Oakland concrete.', 'skyyrose' ),
            'cta'     => array(
                'primary'   => array( 'label' => __( 'Browse the Index', 'skyyrose' ),
                                      'href'  => '#collections-index' ),   // editorial handoff below
                'secondary' => array( 'label' => __( 'Pre-Order', 'skyyrose' ),
                                      'href'  => esc_url( home_url( '/pre-order/' ) ) ),
            ),
        ) ),
    ),
);
```

Keep the existing `$assets()` helper (still + clip + clipMobile + Photon `stillSet`) untouched — it is already correct. **Imagery:** scene stills stay the 5 tracked webp (non-product imagery → visual-manifest lane); any product imagery in the editorial blades resolves ONLY via `skyyrose_sot_product_image_uri()` (`inc/collection-sot-reader.php:303`) `[repo]` — the current lockup-image approach in `page-collections.php` needs no product images at all, which is the safest default.

**Editorial hub sections (surface 6), all server-rendered PHP:** marquee (names + tagline, CSS animation), Four Worlds blade accordion (4 `<a href="/collections/{slug}/">` blades, accent per canon, `--radius-kids: 16px` on the KC blade only — the artifact does this and it matches canon), stats band (**derive counts from the catalog; the artifact's "88 pieces" is fiction — catalog holds 33 SKUs; "Established 2015" needs founder confirmation before shipping** `[inferred]`), pre-order CTA → `/pre-order/`, house closing + footer.

**Typography remap (founder-directed) applied in `scroll-world.css` + the new hub CSS:** Playfair Display → Archivo (`'wdth' 125`) · Cormorant Garamond → Hanken Grotesk · Bebas Neue → Anton · Oswald → Anton · Instrument Serif → Cinzel · Great Vibes → Pinyon Script · Alex Brush → SkyyRose Black Rose Script · Bungee Shade → SkyyRose Love Hurts Graffiti · Kids Capsule voice → Grand Hotel · Cinzel/Inter stay. **Space Mono (artifact micro-labels) is not in canon and not self-hosted — do not add it; micro-labels become Hanken Grotesk, small size, wide tracking.** Barlow is dashboard-only — drop. The artifact's two `fonts.gstatic.com` @font-faces violate zero-CDN and die with the remap. **`--void #08080A` resolves to canon `--black #0A0A0A`** (page bg, all `rgba(8,8,10,*)` overlays → `rgba(10,10,10,*)`); the layered darks above it (`--charcoal #0E0E12` etc.) keep. Keep the whole artifact token system: easings, durations, `--depth-1..4`, `--glow-*`, `--space-*`, `--radius-*` (sharp 2px adult / 16px kids), z-scale, clamp() type scale. Contrast rule holds: crimson never as body text; muted text is `#B3B3B3`, never low-alpha white.

## 3. Progressive enhancement — the hub is never the only route

- **No JS:** the mount `<div>` is empty and zero-height; the visitor lands directly on the server-rendered editorial index — full H1, 4 collection cards, pre-order. Nothing to "fall back" to; the fallback IS the page. (This is why merging beats the bare canvas.)
- **`prefers-reduced-motion`:** engine already never fetches clips and cross-dissolves stills (`loadClip` early-return, asset2.js:224) `[repo]`; additionally kill the marquee animation, blade flex-grow transition, and reveal translations via one `@media (prefers-reduced-motion: reduce)` block in the hub CSS.
- **Low power / Save-Data:** add a bootstrap gate in the theme's `scroll-world.js`: if `navigator.connection?.saveData` (or `downlink < 1.5`), strip `clip`/`clipMobile`/`connectors` from the config before `mountScrollWorld()` — stills-only flight, identical navigation. Fails closed to stills.
- **Keyboard / SR:** engine already gates CTA tab order to visible sections (WCAG 2.4.7) and sets `aria-current` on dots `[repo]`. Add a skip link "Skip to the collections index" → `#collections-index`. `headingLevel:2` keeps a single H1 (in the editorial).
- **Mobile:** engine is phone-aware (mobile clip tier, seek coalescing, iOS priming, URL-bar resize guard) — ship `clipMobile` encodes when clips land; until then stills-only is the shipped state (clips 404 → `s.failed` latch → poster stays, by design).

## 4. Shopper path: world → collection page → PDP → cart

| Transition | Where | State carried |
|---|---|---|
| World scene → collection page | `cta.primary` "Enter {Collection}" in-scene; blade `<a>` in editorial; nav pills jump within world | Plain `<a href="/collections/{slug}/">` — full navigation. Cross-document View Transition opt-in can reuse the existing collection View-Transitions choreography (`skyyrose_enqueue_collection_styles`, `enqueue.php:843`) — Chromium-only, progressive. |
| Return to hub | Browser back (bfcache) + collection pages' existing nav | New: engine stores `activeIndex` in `sessionStorage` on scene change; on mount, if present, `jumpTo(i)` restores the visitor to the world they left. No URL params, no server state. |
| Collection page → PDP → cart | Unchanged existing surfaces (full theme chrome, Woo templates) | Woo session cookie carries cart — nothing new. The hub keeps the theme header, so the cart icon/count is visible from the first scene; a shopper is never inside chrome-less limbo. |

## 5. Performance budget — primary funnel entry

- **Targets:** LCP ≤ 2.5s mobile p75 (LCP element = scene-1 still); INP ≤ 200ms; CLS < 0.05 (fixed stage + fixed-height editorial sections).
- **LCP path:** reuse the existing scene-1 preload pattern (`enqueue.php:819-840` — Photon `imagesrcset`, must byte-match the engine's `srcset` or it double-fetches) `[repo]`, moved to fire on the collections slug. Preload only Cinzel + Hanken Grotesk woff2 (first-viewport copy); all fonts `font-display: swap`, self-hosted (confirmed present: `assets/fonts/` has all 9 canon families) `[repo]`.
- **Weight ceilings:** critical path (HTML + CSS + scroll-world.min.js + scene-1 still at viewport width) ≤ 350KB. Stills total 816KB full-res `[repo: 194+207+253+134+29KB]` but only scene-1 loads eagerly; the rest are proximity-gated (±2.4vh) by the engine. Clips (when generated): ≤ 3MB desktop / ≤ 1.2MB mobile-720p per dive, ≤ 2MB per connector, whole flight ≤ 20MB — all lazy (±1.6vh gate, Blob fetch), zero bytes at t=0.
- **Deferred:** scroll-world.js `defer`+footer (already); hub JS (blades/reveals) `defer`; **mascot GLB does not load on the hub** (extend the checkout-style exclusion — three.js + draco decode competing with clip scrubbing on phones blows INP; flag to founder as a call, default off); no three.js, no GSAP anywhere on this page.
- **Cache-bust:** any of this shipping requires the `SKYYROSE_VERSION` triple bump (functions.php, style.css, readme.txt) — deploy-correctness, ~52 enqueue calls key on it `[repo]`.

## 6. Files to create/modify + verification

| # | File | Change | Verify |
|---|---|---|---|
| 1 | `inc/collections-world.php` | Config rewrite per §2 (per-section CTAs, counts from catalog, headingLevel, drop brand/cta top-level) | `php -l`; unit: assert every `cta.primary.href` matches `#^/collections/(black-rose\|love-hurts\|signature\|kids-capsule)/$#` or `/pre-order/`/anchor; `npm run lint:php` |
| 2 | `page-collections.php` | Add world mount div + `.is-world-hub` body class; extract editorial into template-part; `id="collections-index"` anchor | curl cache-busted `/collections/`: 200, ≥50KB, contains 4 `/collections/{slug}/` hrefs **in raw HTML** (never WebFetch); no PHP-error markers |
| 3 | `template-parts/collections-index-editorial.php` (new) | Hero/ci-grid/marquee/blades/stats/preorder, fonts remapped, counts derived | Same curl + Playwright eyes-on |
| 4 | `assets/js/scroll-world.js` | Port artifact engine improvements (scroll polling, NaN-fade floor, seek coalescing, srcset-before-src, CTA tab-gating — artifact asset2.js is ahead of the theme copy; diff first), add `headingLevel`, Save-Data gate, sessionStorage resume | Engine mounts on DevTools mobile+desktop; reduced-motion emulation shows stills-only; console clean |
| 5 | `assets/css/scroll-world.css` | Merge artifact dark-luxury sw-skin, font remap, `#0A0A0A` resolution, token system | Rendered check both breakpoints; contrast spot-check muted text = #B3B3B3 |
| 6 | `assets/css/collections-index.css` (or new `collections-hub.css`) | Marquee/blades/stats + reduced-motion guards + `--radius-kids` on KC blade | Same |
| 7 | `inc/enqueue.php` | Extend the 5 `'collections-world'` slug conditions (lines 143, 145, 322, 656, 819, 953) to the collections-index slug; **the two-edit rule** (`$template_map` ~:597, `$template_styles` ~:656) or CSS silently misloads; move scene-1 LCP preload | `verify:theme` per-aspect gate; view-source shows preload `imagesrcset` byte-identical to engine srcset |
| 8 | `inc/redirects.php` | Add `'/collections-world/' => '/collections/'` to `skyyrose_collection_redirects()`; rewrite flush is automatic via `skyyrose_flush_rewrites_once()` on version bump | `curl -sI https://skyyrose.co/collections-world/` → 301 → `/collections/` post-deploy |
| 9 | `template-collections-world.php` | Update the obsolete header warning; template stays | `php -l` |
| 10 | Version triple + `npm run build` (from `wordpress-theme/`, NOT the theme dir) | Bump; rebuild `.min` | `verify:theme` min-sync (byte-identity with fresh build); post-deploy: cache-busted curl + Playwright mobile+desktop with `img.decode()` before screenshot |

Deploy itself is STOP-AND-SHOW (production), and clip generation (Higgsfield) is a separate paid-gated workstream — this hub ships stills-only and upgrades in place when clips land.

Open founder calls flagged: (a) mascot on/off on the hub (spec default: off); (b) "Established 2015" and any stats-band numbers need founder confirmation; (c) whether the finale primary CTA should later point at a live drop instead of `#collections-index`.