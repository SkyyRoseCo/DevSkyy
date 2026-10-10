# HOMEPAGE REBUILD — Direction Spec (skyyrose.co front page)

All claims `[repo]` unless tagged otherwise. Sources read this session: `front-page.php` (766 ln), `assets/css/homepage-v2.css`, `assets/js/homepage-v2.js`, `assets/js/scroll-world.js`, `inc/collections-world.php`, `inc/enqueue.php` (grepped), `assets/css/design-tokens.css` (grepped), `template-collections-world.php`, the full artifact page + engine.

---

## 1 · What holds the current homepage back from award-grade

**A. Template-grid syndrome — six identical stanzas.** The page runs eyebrow → centered `h2` → paragraph → `stagger-grid` six times in a row: commercial-runway (`front-page.php:320–332`), collections (`:443–447`), style-atelier (`:522–527`), service-promise (`:650–654`), craft (`:681–685`), newsletter (`:700–703`). Same rhythm, same reveal class, same symmetry. That is the template look the founder is asking to leave behind.

**B. Three competing collection choosers, zero products.** Commercial runway (3 collection tiles, `:333–389`), collections grid (4 cards, `:448–516`), style atelier (3 collection recommendations, `:528–567`) all answer the same question — "which collection?" — with three different UIs. Meanwhile no price, no product name-as-link, no PDP route appears anywhere on 766 lines; every CTA lands on a collection index. Decision fatigue up top, commerce depth nowhere.

**C. Fake loader taxes the LCP.** `homepage-v2.js:20–40` runs a `setInterval` fake progress bar over a full-viewport overlay; CSS needed a 2.5 s self-dismiss safety net because it was covering the LCP indefinitely on slow queues (`homepage-v2.css:74–86`). A simulated loader on a store is a conversion tax and an instant award-jury red flag.

**D. The best fashion asset is hidden decoration.** The SOT-verified on-model strip (8 SKUs, `front-page.php:36, 217–262`) renders at 140–220 px, aria-hidden, *behind* the type. The foreground is a static wordmark + two in-page anchor CTAs (`:270–271`). The page's only real garments are wallpaper.

**E. Motion is one note.** Every reveal is the same IO class-toggle at threshold .06 (`homepage-v2.js:69–85`). No scroll-linked choreography, no per-collection accent shifts, a plain CSS marquee (`front-page.php:307–316`). The theme already owns a scroll-scrubbed world engine (`assets/js/scroll-world.js`) — stranded on a side template (`template-collections-world.php:17–18` even warns it must not be the collections page), while the homepage re-implements the four-worlds idea as flat cards.

**F. Token drift inside the theme's own CSS.** `homepage-v2.css:18` declares `--void: #050505` on global `:root` — a third black, diverging from canon `#0A0A0A` *and* leaking outside the homepage scope. `--haze: rgba(255,255,255,.55)` (`:22`) is used as text color (`.ld-tag`, `:102`) — exactly the low-alpha-white "muted" shorthand canon bans (≈4.9:1 unmeasured).

**G. Honesty bug.** Newsletter's no-AJAX fallback shows "Welcome to the movement" success without submitting anything (`homepage-v2.js:221–228`).

What's genuinely good and survives: real press links (`:48–69`), founder story + quote copy, the kc-heir envelope (`:590–646` — the one distinctive section on the page), SOT-resolved imagery discipline, lockup-image collection names (`:474–505`), LCP/preload engineering on the hero pipeline.

---

## 2 · New section architecture (top → bottom)

The artifact **is** the homepage: `front-page.php` becomes World + Editorial in one continuous page. One collection chooser, not three. Editorial and asymmetric — no two adjacent sections share a layout skeleton.

| # | Act | For the shopper | For conversion |
|---|-----|-----------------|----------------|
| **I** | **The Descent** — scroll-world mount (`#skyyrose-collections-world`), 5 scenes: Signature → Black Rose → Love Hurts → Kids Capsule → finale. Stills-first (engine auto-falls-back until Higgsfield clips land, `inc/collections-world.php:13–15`). WP header stays (cart/account are non-negotiable on a store); engine config omits `brand`/`cta` and sets `nav:false` so the engine's topbar chrome never doubles the site header. Route dots + scroll hint kept. | Immersion + orientation: "four worlds, choose your room." Scene 1 copy = H1 = tagline (SEO + LCP still, eager/high — engine native). | **Every scene gets a real CTA** — config-only change: per-section `cta.primary.href` → `/collection-*/` (engine renders CTAs on any section that has the key, `scroll-world.js` ctaBtns). A shopper can exit into commerce at any scene, not just the finale. Finale CTA → `/collections/`. |
| **II** | **The Ticker** — Cinzel caps collection names · Pinyon Script rose-gold interleave (artifact structure, fonts remapped). aria-hidden, CSS loop, edge-masked. | Rhythm break; hands the eye from fixed-stage world to flowing editorial. | Brand mantra repetition at the exact scroll depth where attention resets. |
| **III** | **The Index** — the artifact's four-blade flex accordion replaces runway + col-grid + atelier as the *single* chooser. Blade names use the existing **lockup images** (`hero-overlays/*`, `front-page.php:476–488`) — the artifact type-renders them, which violates lockup canon; we don't. KC keeps the Grand Hotel type fallback (no lockup asset exists — flagged gap). Dynamic piece counts via `skyyrose_get_collection_products()` preserving the `data-collection`/`data-piece-count` audit contract (`front-page.php:509–510`). Desktop: hover/focus expands (attribute-driven state). Mobile ≤900px: stacked 62vh cards, body always visible. | One confident room-choice moment with garment-scale imagery. | Four "Enter <Collection>" CTAs → real collection URLs. Accent glow per collection tells the shopper the house has depth. |
| **IV** | **Drop / Pre-order band** — conditional: `skyyrose_render_drop_block()` gate already exists (`front-page.php:281–283`); the artifact's static pre-order section renders only when a drop is actually live. | Urgency only when true — no fake timers (founder canon). | Reserve CTA at the moment of highest intent, post-choice. |
| **V** | **The Receipts** — artifact stats grid fused with the press strip into one asymmetric proof band: Archivo-monument numerals (dynamic total piece count · 04 worlds · Est. 2020) + the four real press links + Best of Bay Area award. Kills the standalone press strip and the craft icon-grid (craft copy compresses to one line here). | Third-party credibility, scannable in 3 seconds. | Trust at the price-justification moment; external validation adjacent to CTAs. |
| **VI** | **The Origin** — story + quote merged into one asymmetric split: founder portrait, compressed body (3 paragraphs → 2), pull-quote overlapping the image edge. Recognition float card kept. | The differentiator no competitor owns: Corey, Oakland, the daughter's name. | Emotional equity that converts price into meaning; single CTA to the story page. |
| **VII** | **The Letter** — kc-heir envelope, kept as-is (`front-page.php:590–646`). Blade IV is KC's commerce entry; the letter is its emotional one. | The "I've never seen this on a store" moment. | KC route with the highest memorability per pixel on the site. |
| **VIII** | **Close** — service promise compressed to a one-row band (shipping · fit guide · wishlist · concierge), newsletter (fake-success fallback removed — honest error instead), brand outro (monogram lockup image + closing line), then canonical `get_footer()` (mascot mount unaffected). | Practical reassurance + a reason to stay in touch. | Wishlist + email capture for the 97% who don't buy today. |

**Cut:** loader (entirely), commercial runway, collections grid, style atelier (relocation candidate for collection pages — code preserved, not deleted, per surgical-change rule), craft grid, standalone quote section, duplicate scroll-progress bar (engine's `sw-scrollbar` owns it).

---

## 3 · Token mapping onto canon — the block we ship

Rules applied: `--void` resolves to canon `#0A0A0A` (the artifact's `#08080A` and homepage-v2's `#050505` both die — one black on this site). Font vars alias the **generated** `--skyyrose-font-*` chain (`design-tokens.css:150–159, 269–272` — `--ff-brand` etc. already alias it; homepage-v2.css deliberately stopped redeclaring them, `homepage-v2.css:28–32`). Space Mono has no canon mapping → micro-labels move to Hanken Grotesk wide-tracked. Barlow (dashboard-only) is dropped. Low-alpha whites survive **only** as scrims on imagery, never as text — muted text is `--fg3 #B3B3B3` (9.44:1). Crimson stays fills/borders/glows only.

```css
/* homepage-v3 tokens — artifact system resolved to SkyyRose canon.
   Scoped to .homepage-v3 (NOT :root — fixes the homepage-v2.css:18 leak). */
.homepage-v3 {
  /* Blacks — one canon black; artifact #08080A and legacy #050505 collapse into it */
  --void: #0A0A0A;            /* = canon --black; kept as alias for ported artifact CSS */
  --black: #0A0A0A;
  --charcoal: #0E0E12;  --smoke: #141418;  --ash: #1A1A20;
  --card: #111111;      --card-hover: #161616;

  /* Brand accents (canon §6) */
  --rose-gold: #B76E79;  --rose-gold-rgb: 183, 110, 121;
  --gold:      #D4AF37;  --gold-rgb:      212, 175, 55;    /* Signature  */
  --silver:    #C0C0C0;  --silver-rgb:    192, 192, 192;   /* Black Rose */
  --crimson:   #DC143C;  --crimson-rgb:   220, 20, 60;     /* Love Hurts — fills/borders/glows ONLY, never text */

  /* Text — measured, never low-alpha-white shorthand */
  --fg1: #FFFFFF;  --fg2: #E0E0E0;
  --fg3: #B3B3B3;  /* muted = canon --color-text-muted, 9.44:1 on #0A0A0A */
  /* scrims (imagery overlays only — banned as text color): */
  --scrim-04: rgba(255,255,255,.04);  --scrim-10: rgba(255,255,255,.10);

  /* Typography — required mapping applied; aliases the generated SOT chain */
  --fd: var(--skyyrose-font-caps, 'Cinzel', serif);                       /* engraved caps (stays) */
  --fp: var(--skyyrose-font-display, 'Archivo', system-ui, sans-serif);   /* was Playfair Display  */
  --fb: var(--skyyrose-font-body, 'Hanken Grotesk', 'Inter', sans-serif); /* was Cormorant Garamond */
  --fc: var(--skyyrose-font-ui, 'Anton', sans-serif);                     /* was Bebas Neue AND Oswald */
  --fm: var(--skyyrose-font-body, 'Hanken Grotesk', sans-serif);          /* was Space Mono (not canon) — micro-labels: 600, letter-spacing .3em */
  --fi: 'Inter', system-ui, sans-serif;                                   /* stays (fallback tier) */
  --fs: var(--fd);                                                        /* was Instrument Serif → Cinzel */
  --display-stretch: 'wdth' 125, 'wght' 900;  /* Archivo monument treatment (typography.json) */

  /* Collection script voices — bespoke, per canon */
  --fv-signature:  'Pinyon Script', cursive;                    /* was Great Vibes  */
  --fv-black-rose: 'SkyyRose Black Rose Script', cursive;       /* was Alex Brush   */
  --fv-love-hurts: 'SkyyRose Love Hurts Graffiti', cursive;     /* was Bungee Shade */
  --fv-kids:       'Grand Hotel', cursive;

  /* KEEP — artifact's excellent system, verbatim */
  --ease:           cubic-bezier(0.16, 1, 0.3, 1);    /* house ease */
  --ease-cinematic: cubic-bezier(0.22, 1, 0.36, 1);
  --ease-magnetic:  cubic-bezier(0.03, 0.98, 0.52, 0.99);
  --ease-whip:      cubic-bezier(0.75, 0, 0.25, 1);
  --ease-dramatic:  cubic-bezier(0.65, 0, 0.35, 1);
  --dur-fast: 200ms; --dur-base: 300ms; --dur-slow: 600ms;
  --dur-reveal: 800ms; --dur-cinem: 1200ms;

  --depth-1: 0 2px 8px rgba(0,0,0,.4);   --depth-2: 0 8px 24px rgba(0,0,0,.5);
  --depth-3: 0 16px 48px rgba(0,0,0,.6); --depth-4: 0 24px 64px rgba(0,0,0,.7), 0 0 120px rgba(0,0,0,.3);
  --glow-rose:    0 0 20px rgba(var(--rose-gold-rgb), .30);
  --glow-gold:    0 0 20px rgba(var(--gold-rgb), .30);
  --glow-silver:  0 0 20px rgba(var(--silver-rgb), .30);
  --glow-crimson: 0 0 20px rgba(var(--crimson-rgb), .30);

  --space-1: 4px;  --space-2: 8px;  --space-3: 12px; --space-4: 16px;
  --space-6: 24px; --space-8: 32px; --space-12: 48px; --space-16: 64px;
  --space-20: 80px; --space-24: 96px; --space-32: 128px;

  --radius-sharp: 2px;   /* adult collections */
  --radius-kids: 16px;   /* Kids Capsule only */

  --text-3xl: clamp(1.875rem, 2.8vw, 2.25rem);
  --text-4xl: clamp(2.25rem, 3.8vw, 2.875rem);
  --text-5xl: clamp(2.75rem, 5.5vw, 4rem);
  --text-dec-lg: clamp(5rem, 14vw, 12.5rem);

  --z-sticky: 200; --z-overlay: 400; --z-modal: 800;
}
/* Collection zones — one accent per surface (Creative Director rule) */
.homepage-v3 [data-collection="signature"]    { --accent: var(--gold);      --accent-rgb: var(--gold-rgb); }
.homepage-v3 [data-collection="black-rose"]   { --accent: var(--silver);    --accent-rgb: var(--silver-rgb); }
.homepage-v3 [data-collection="love-hurts"]   { --accent: var(--crimson);   --accent-rgb: var(--crimson-rgb); }
.homepage-v3 [data-collection="kids-capsule"] { --accent: var(--rose-gold); --accent-rgb: var(--rose-gold-rgb); }
```

Scroll-world skin overrides (unlayered, beats the engine's `@layer sw` — the artifact's own technique, artifact-page.html:1139–1171): `--sw-bg: var(--black)`, `--sw-ink: #fff`, `--sw-ink-soft: var(--fg3)` (artifact used `#A0A0A0`, 5.9:1 — we use the measured muted token), `--sw-font-display: var(--fd)`, `--sw-font-body: var(--fb)`; `.sw-copy__body` italic register moves from Playfair → Hanken Grotesk italic; `.sw-btn` from Bebas → Anton `.3em` tracking; eyebrows from Space Mono → Hanken 600 `.3em`.

---

## 4 · Motion spec

| Element | Animates | Trigger | Easing / duration | prefers-reduced-motion |
|---|---|---|---|---|
| World scenes (Act I) | Video `currentTime` scrub (rAF lerp ·0.18); stills Ken-Burns scale 1.03→1.17 pre-clip | Scroll position (engine `read()`) | Engine-native; `linger: 0.4` (finale 0.3) mid-scene dwell | Clips **never fetched**; stills cross-dissolve only, scale locked at 1 (engine-native, `scroll-world.js` loadClip guard + transform branch) |
| Scene copy | Opacity + 4vh translateY, scrubbed | Scroll progress per section | smoothstep (engine) | translate → `none`, opacity-only |
| Scene crossfades | Opacity dissolve, 0.12 vh seam | Scroll | smoothstep | Same (it's the PRM story itself) |
| Blades (Act III) | `flex-grow` 900ms; media scale 1.06→1 + de-sat lift 1200ms; halo opacity 900ms; body opacity/translateY(14px) 700ms +120ms delay | `mouseenter`/`focusin` (desktop >900px); blade 0 active at rest | flex-grow + halo + body: `--ease` house; media: `--ease-cinematic` | Transitions collapse to instant via global PRM rule; state machine intact so content is never hidden; mobile always-expanded |
| Editorial reveals `[data-reveal]` | Opacity 0→1, translateY 28px→0, per-element ms stagger | IntersectionObserver threshold 0.12, rootMargin −6%, unobserve on fire | 900ms `--ease` | Set final state immediately, no transition |
| Ticker (Act II) | `translateX(0→−50%)` duplicated track | Autonomous CSS loop | 42s linear infinite | `animation: none` — static single row, edge mask kept |
| Kids letter (Act VII) | Wax-seal split + letter rise (existing kc-heir CSS) | `:hover`/`:focus-visible`; coarse-pointer first-tap opens, second navigates (`homepage-v2.js:318–333`, kept) | Existing kc timings | Seal opens instantly (global PRM), nav unaffected |
| CTAs / buttons | translateY(−2px) + accent glow (`--glow-*`) | hover/focus | 300ms `--ease`; active `scale(.97)` | Lift/press off; color+glow only |
| Progress | Engine `sw-scrollbar` scaleX | Scroll | Engine | Kept (position feedback is a11y-positive) |
| Loader | **Deleted.** LCP = scene-1 still, eager + fetchpriority=high (engine-native) | — | — | — |

---

## 5 · Product image slots — SOT-resolved, every one

**Governing rule (blocking):** every garment `<img>` resolves at render time through `skyyrose_sot_product_image_uri( $sku, 'front' )` / `data/sot-images.json` — never a filename, never an uploads path, never a new render (OAI2 + STOP-AND-SHOW, out of this scope). Final SKU picks are eyes-on pixel-verified against the catalog CSV before deploy (product-image-fidelity gate).

| Slot | Count | Source |
|---|---|---|
| World scene stills (scene-1…5) | 5 | Environment art, `assets/scenes/collections-world/*.webp` — visual-manifest governed, **git-tracked** `[repo]`; Photon srcset via existing helper (`inc/collections-world.php:62–68`). Any garment in a future replacement still ⇒ per-SKU pixel verify. |
| Blade media (Act III) | 4 | One on-model front per collection via SOT. Candidate pool = the already-verified hero-strip list `br-006, sg-009, lh-004, kids-001, br-004, sg-013, lh-002, sg-006` (`front-page.php:36`, eyes-on verified 2026-07-06) — re-verify the final four at build. |
| Collection name lockups | 3 (+1 gap) | Lockup **images** `hero-overlays/{br-brand-script-logotype, lh-logo-combined, sig-brand-skyy-rose-gold}` (`front-page.php:476–488`). KC lockup asset does not exist — Grand Hotel type fallback, flagged for the imagery pipeline. |
| Origin founder portrait | 1 | `homepage-story-founder.webp` (existing brand asset, visual manifest). |
| Brand outro monogram | 1 | `assets/branding/skyyrose-monogram.webp` (already in JSON-LD, `front-page.php:723`). |
| Drop block imagery | 0–n | Whatever `skyyrose_render_drop_block()` emits — its internals must already be SOT-clean; verify at build, don't assume. |

The artifact's blade background UUIDs and its hardcoded counts (32/18/24/14/"88 pieces") are **discarded** — counts come from `skyyrose_get_collection_products()` exactly as `front-page.php:42–44` does today.

---

## 6 · Files, .min rebuild, version bump

**Create**
- `assets/css/homepage-v3.css` — new file (instant rollback to v2 = one enqueue revert), token block above + acts II–VIII + engine skin overrides. Target < 800 lines by pushing act markup into parts.
- `assets/js/homepage-v3.js` — reveals, blades state machine, newsletter (honest fallback), kc tap. No loader, no letter-split, no duplicate progress bar. Target ≤ ~200 lines.
- `template-parts/home/{index-blades,receipts,origin,close}.php` — many-small-files rule; `front-page.php` becomes orchestration.

**Modify**
- `front-page.php` — full act restructure; keep `get_header()/get_footer()`, JSON-LD (`:715–741`), drop-block gate (`:281–283`), kc-heir, press data (feeds Act V); inline-JS path (`:749–764`) → `homepage-v3(.min).js`.
- `inc/enqueue.php` — (a) front-page style mapping → `homepage-v3.css`; (b) enqueue `scroll-world(.min).js` + `scroll-world.css` + localize `SKYY_SCROLL_WORLD_CONFIG` on `is_front_page()` (today gated to the `collections-world` slug only — `:819, :953–975`); (c) **preload pairing contract**: the front-page `wp_head` preload must switch from `homepage-hero-bg` to the scene-1 still with identical URL/widths/sizes as the engine emits (the same contract discipline documented at `front-page.php:171–179`), and the hero-strip br-006 preload (`:233–237`) is retired with the old hero.
- `inc/collections-world.php` — add `$context` arg (`'page'`|`'home'`): home variant omits `brand`/`cta`, sets `nav => false`, adds per-section `cta.primary.href => /collection-*/`. Data stays single-source for both surfaces.
- `assets/js/scroll-world.js` — **target zero engine diffs**; config already supports everything needed. Only if empty-topbar chrome proves visible: one additive `topbar:false` flag (~5 lines).

**Build + versioning (deploy-correctness)**
- `npm run build` from `wordpress-theme/` (parent — no package.json in the theme dir) regenerates `homepage-v3.min.{css,js}`; production serves `.min` (`$use_min`), and `front-page.php` inlines the **min** JS — the file must exist minified or the fallback silently ships unminified source. `npm run verify:theme` min-sync asserts byte-identity.
- Bump the `SKYYROSE_VERSION` triple (`functions.php`, `style.css`, `readme.txt`) — it cache-busts ~52 enqueue calls; without it returning visitors get v2 CSS on v3 markup.
- Deploy-source completeness: the 5 scene stills are git-tracked `[repo]` so `preflight_completeness()` covers them; the untracked `*-v2-avatar.webp` riders are unrelated to this surface. Deploy itself is STOP-AND-SHOW and not part of this spec.

---

## 7 · Canon conflicts in the artifact — resolved or flagged (do not ship silently)

1. **Fonts** — remapped per mandate (§3). Space Mono → Hanken wide-tracked (no canon slot); Barlow dropped.
2. **`--void`** — resolved to canon `#0A0A0A`; also retires homepage-v2.css's rogue `#050505` and its `:root` leak.
3. **"Established 2015"** (artifact stats/outro) vs **"Est. 2020"** (`front-page.php:266`) + JSON-LD `foundingDate: 2020` (`:725`) — ship 2020 unless the founder corrects the site canon.
4. **Type-rendered collection names in blades** — replaced with lockup images per canon; KC lockup asset gap flagged.
5. **"00 Restocks, ever" / "All sales final" / "all numbered"** — policy claims; require founder + legal-pages consistency check before any of them ship.
6. **"Built on grace. Hustled into luxury."** outro line — artifact copy, not confirmed canon; founder sign-off or fall back to the locked tagline. All final copy comes from Seat 7 per charter; nothing here is invented copy shipped as-is.
7. Artifact CTAs are `#top`/`#worlds` placeholders — all become real `/collection-*/` and `/collections/` URLs through the engine's `safeHref()` path (config change only, confirmed in `scroll-world.js`).