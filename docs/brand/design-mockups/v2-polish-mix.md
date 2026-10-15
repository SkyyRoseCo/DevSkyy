# v2 Polish Mix-In Specification
## Live Homepage Polish Layers → Standalone v2.html

**Reference:** `docs/brand/design-mockups/v2.html` (897 lines, 8 frames)
**Live source:** `front-page.php` + `assets/css/homepage-v2.css` + `assets/js/homepage-v2.js`
**Constraint:** v2.html is standalone — no WordPress, no PHP, no Three.js/WebGL, no enqueues
**Brand canon:** The Five only (Kith / Oaklandish / Culture Kings / Fear of God / Palm Angels)

---

## Part 1: Polish Layer Inventory

### Layer 1 — Film Grain Overlay

| Field | Value |
|-------|-------|
| Source | `assets/js/homepage-v2.js` — `renderGrain()` / `scheduleGrain()` (lines 1–80 approx) |
| Live HTML | `<div class="grain" aria-hidden="true">` (front-page.php line 164) |
| Effect | Canvas-rendered noise texture drawn at 60fps over the full viewport — adds editorial texture, prevents the flat-dark-background problem |
| Recommendation | **YES** |
| Rationale | Pure vanilla JS + canvas, zero dependencies, zero asset files. Canvas grain is how editorial sites (032c, Purple Magazine aesthetics that inform The Five) avoid "tech brand dark mode" syndrome. v2 currently reads too clean/digital without it. |
| Difficulty | **CSS + JS** — copy the `renderGrain`/`scheduleGrain` functions from `homepage-v2.js` and add `<canvas class="grain" aria-hidden="true">` before `</body>`. CSS: `position:fixed; inset:0; pointer-events:none; z-index:9998; opacity:0.035;` |

---

### Layer 2 — Vignette

| Field | Value |
|-------|-------|
| Source | `assets/css/homepage-v2.css` lines 48–61 (inferred; `.vignette` CSS block in `:root` section) |
| Live HTML | `<div class="vignette" aria-hidden="true">` (front-page.php line 165) |
| Effect | Radial gradient from transparent center to `rgba(0,0,0,0.55)` at edges — focuses eye toward center of each frame |
| Recommendation | **YES** |
| Rationale | Pure CSS. Trivially portable. Pairs with grain to create the cinematic "developed in a darkroom" atmosphere v2's magazine frames need. Without vignette + grain, dark full-bleed photos look flat-screened not printed. |
| Difficulty | **Simple CSS** — `position:fixed; inset:0; pointer-events:none; background:radial-gradient(ellipse at center, transparent 50%, rgba(0,0,0,.55) 100%); z-index:9997;` |

---

### Layer 3 — Ken Burns Hero Zoom

| Field | Value |
|-------|-------|
| Source | `assets/css/homepage-v2.css` lines 269–295 |
| Live HTML | `<div class="hero-bg parallax-ken-burns">` (front-page.php line 224) |
| Effect | Background image breathes: `scale(1.05)` → `scale(1.1) translateY(-2%)` over 30s, infinite alternate — adds life to still photography |
| Recommendation | **YES** |
| Rationale | Zero JS in CSS-only form. One `@keyframes` block. Every magazine-as-site reference uses this or scroll-parallax zoom on cover imagery. v2's `#home-cover` and `#br-cover` frames are static — this single animation makes them feel editorial. |
| Difficulty | **Simple CSS** — `@keyframes heroZoom { 0% { transform: scale(1.05); } 100% { transform: scale(1.1) translateY(-2%); } }` applied to `.hero-bg { animation: heroZoom 30s ease-in-out infinite alternate; }` |

---

### Layer 4 — Scroll-Progress Bar

| Field | Value |
|-------|-------|
| Source | `assets/css/homepage-v2.css` lines 38–47; JS in `homepage-v2.js` scroll listener |
| Live HTML | `<div class="scroll-progress" aria-hidden="true">` (front-page.php line 166) |
| Effect | 2px fixed bar at top of viewport; width tracks `scrollY / (scrollHeight - innerHeight)` — orients reader in long scroll document |
| Recommendation | **OPTIONAL** |
| Rationale | v2 is 8 long frames — a progress bar aids orientation. However, magazine purists argue the bar is "UI app" language, not editorial. Include if the spec evolves toward a product-feel, skip for pure editorial. |
| Difficulty | **CSS + JS** — CSS: `position:fixed; top:0; height:2px; background:var(--accent); z-index:9999; width:var(--scroll-pct,0%);`. JS: `window.addEventListener('scroll', () => document.documentElement.style.setProperty('--scroll-pct', (scrollY / (document.body.scrollHeight - innerHeight) * 100) + '%'))` |

---

### Layer 5 — Page Loader

| Field | Value |
|-------|-------|
| Source | `assets/css/homepage-v2.css` lines 62–109; `homepage-v2.js` `initLoader()` |
| Live HTML | `<div id="loader">` with `.ld-brand`, `.ld-tag`, `.ld-bar`, `.ld-fill` (front-page.php lines 171–175) |
| Effect | Full-screen cover with brand name + animated fill bar; fades out after ~1.5s on DOMContentLoaded |
| Recommendation | **OPTIONAL** |
| Rationale | Adds ceremony for first impression; signals premium. But v2 is a design mockup / demo reference — a loader may hinder quick evaluation iteration. Include only if v2 evolves into a client-facing demo or landing page. |
| Difficulty | **CSS + JS** — self-contained; no WP dependencies. ~30 lines CSS, ~20 lines JS. |

---

### Layer 6 — Nav Scroll-Blur

| Field | Value |
|-------|-------|
| Source | `assets/css/homepage-v2.css` lines 128–133 |
| Live JS | `homepage-v2.js` `initNavScroll()` — toggles `.scrolled` on `#mainNav` when `scrollY > 80` |
| Effect | Nav gains `backdrop-filter: blur(24px) saturate(1.5); background: rgba(5,5,5,.85)` once user scrolls past 80px |
| Recommendation | **YES** |
| Rationale | v2 has a fixed nav bar. Without scroll-blur it looks flat/transparent against the hero for the entire page length. The blur effect is standard modern dark-site luxury language (Fear of God, Culture Kings nav behavior). Pure CSS + 5-line JS scroll listener. |
| Difficulty | **CSS + JS** — CSS: `.nav.scrolled { background: rgba(5,5,5,.85); backdrop-filter: blur(24px) saturate(1.5); border-bottom: 1px solid rgba(255,255,255,.06); transition: all 0.3s; }`. JS: `window.addEventListener('scroll', () => document.querySelector('.nav')?.classList.toggle('scrolled', scrollY > 80))` |

---

### Layer 7 — Hero Floating Particles

| Field | Value |
|-------|-------|
| Source | `assets/css/homepage-v2.css` lines 306–327 |
| Live HTML | `<div class="hero-particles" aria-hidden="true"><i></i>` × 6 (front-page.php line 245) |
| Effect | 6 absolutely-positioned 2×2px white dots animate from bottom to top over 20s at staggered delays, opacity 0→0.15→0 — micro-ambient depth |
| Recommendation | **YES** |
| Rationale | Zero JS. 6 `<i>` tags + one CSS block. The cost is 15 lines of CSS and 6 empty elements. The return is depth that breaks the "dark rectangle + photo" static quality. Especially effective on `#home-cover` and `#br-cover` dark-field frames. |
| Difficulty | **Simple CSS** — all animation via `@keyframes ptcl` + `nth-child` delays on `.hero-particles i` |

---

### Layer 8 — Hero Frame Border

| Field | Value |
|-------|-------|
| Source | `assets/css/system/animations-premium.css` (`.parallax-ken-burns` context) or `design-tokens.css` — exact hero-frame rules NOT found in `homepage-v2.css` 1481 lines |
| Live HTML | `<div class="hero-frame" aria-hidden="true">` (front-page.php line 246) |
| Effect | Thin rectangular inset border inside the hero viewport — frames the photographic content like a print mat |
| Recommendation | **YES** |
| Rationale | A single CSS rule: `position:absolute; inset:12px; border:1px solid rgba(255,255,255,.08); pointer-events:none;`. The visual effect is subtle but decisive — it transforms a photo from "background image" to "framed artwork." Pure CSS, zero dependencies. |
| Difficulty | **Simple CSS** — note: CSS not in `homepage-v2.css`; must write from scratch. Suggested: `position:absolute; inset:clamp(8px,1.5vw,16px); border:1px solid rgba(255,255,255,.07); pointer-events:none; z-index:2;` |

---

### Layer 9 — Hero Scroll Cue

| Field | Value |
|-------|-------|
| Source | `assets/css/homepage-v2.css` lines 457–487 |
| Live HTML | `<div class="hero-scroll"><span>Scroll</span><div class="hero-scroll-line">` (front-page.php lines 258–261) |
| Effect | Centered at hero bottom: "Scroll" label + 48px vertical line that pulses opacity 0.1→0.5 with scaleY via `@keyframes sPulse` |
| Recommendation | **YES** |
| Rationale | v2's frame format is long-scroll; users need a visual cue to continue. The pulsing line is elegant — editorial not app-UI. Pure CSS animation, no JS. Oaklandish and Kith landing pages use this exact pattern. |
| Difficulty | **Simple CSS** — `@keyframes sPulse { 0%,100% { opacity:.1; transform:scaleY(.6); } 50% { opacity:.5; transform:scaleY(1); } }` |

---

### Layer 10 — Hero Location Marks

| Field | Value |
|-------|-------|
| Source | `assets/css/homepage-v2.css` lines 339–373 |
| Live HTML | `<div class="hero-mark-top">Oakland</div>` + `<div class="hero-mark-bot">Est. 2020</div>` (front-page.php lines 248, 250) |
| Effect | Rotated vertical text flanking the hero — "Oakland" top-right, "Est. 2020" bottom-left — in Rose Gold with gold accent rules |
| Recommendation | **YES** |
| Rationale | Brand-identity anchor. Oakland provenance is a brand pillar. These marks are pure CSS positioned text with `writing-mode: vertical-rl`. v2 has no geographic grounding — these add it. Culture Kings and Kith both use sidebar typographic marks as identity nodes. |
| Difficulty | **Simple CSS** — `position:absolute; writing-mode:vertical-rl; font-size:10px; letter-spacing:.2em; color:var(--rose-gold);` |

---

### Layer 11 — Button Treatments (btn-sweep, btn-border-draw, btn-press)

| Field | Value |
|-------|-------|
| Source | `assets/css/system/animations-premium.css` lines 204–266 |
| Live HTML | `.hero-cta.btn-sweep.btn-press` and `.btn-border-draw.btn-press` (front-page.php lines 254–255) |
| Effect | `btn-sweep`: diagonal bg slide on hover from left. `btn-border-draw`: borders grow from corners on hover. `btn-press`: `scale(0.96)` on `:active`. |
| Recommendation | **YES** |
| Rationale | The CSS for all three is self-contained in `animations-premium.css` and requires only `--skyyrose-accent` CSS variable. v2's CTAs are currently static with a simple border hover. Replacing with `btn-sweep` + `btn-press` costs 30 lines of CSS and transforms the interaction register from "template" to "luxury product." |
| Difficulty | **Simple CSS** — copy lines 204–266 from `animations-premium.css` verbatim; replace `--skyyrose-accent` with whatever accent token v2 uses (e.g., `--accent`) |

---

### Layer 12 — Reveal System (rv-clip-up, rv-blur, stagger-grid)

| Field | Value |
|-------|-------|
| Source | `assets/css/system/animations-premium.css` lines 19–180; `assets/js/premium-interactions.js` (full file, 281 lines) |
| Effect | Clip-path reveals, blur+scale entrance, staggered grid entrance — all driven by IntersectionObserver toggling `.is-visible` |
| Recommendation | **YES — partial port** |
| Rationale | v2 already has a `.reveal`/`.is-visible` system. Port: `rv-clip-up` (29 lines CSS, cleanest reveal for headings), `stagger-grid` (12 lines CSS + stagger indexer JS), and the IntersectionObserver pattern from `premium-interactions.js` lines 138–153. Skip: `rv-split-char/word/line` (requires significant JS split engine), `magnetic` (requires mouse tracking JS). |
| Difficulty | **CSS + JS** — selective extract; total ~80 lines CSS + 30 lines JS. Do NOT port the full `premium-interactions.js` — it references Motion One CDN and page-transition behavior that conflicts with standalone single-page use. |

---

### Layer 13 — Magnetic Hover on Cards

| Field | Value |
|-------|-------|
| Source | `assets/css/system/animations-premium.css` lines 187–198; `assets/js/premium-interactions.js` lines 225–239 |
| Effect | Cards shift ±12px and tilt ±4deg following cursor within element bounds, driven by `--mag-x`/`--mag-y` CSS vars set by JS mousemove |
| Recommendation | **OPTIONAL** |
| Rationale | High delight factor on hover-capable devices. The JS is 15 lines and entirely self-contained. However v2 currently has no card grid equivalent to the live `.col-card.magnetic` layout — would only apply after a structural grid section is added (see Part 2). Port together with stagger-grid if a collection card section is added. |
| Difficulty | **CSS + JS** — simple but JS-dependent for the interaction math |

---

### Layer 14 — Press Strip

| Field | Value |
|-------|-------|
| Source | `assets/css/homepage-v2.css` lines 496–547 |
| Live HTML | `.press` section with logo marks (front-page.php ~line 300) |
| Effect | Horizontal strip of press/brand logo marks with fade-edge masking and subtle border rules |
| Recommendation | **NO** |
| Rationale | v2 scope is homepage cover + Black Rose only (8 frames). Press strip is a social-proof CRO element. Brand is pre-launch; no verified press placements. Adds filler risk. Not part of the magazine-as-site thesis. |
| Difficulty | n/a — not recommended |

---

### Layer 15 — Marquee (scrolling text ticker)

| Field | Value |
|-------|-------|
| Source | `assets/css/homepage-v2.css` lines 552–585 |
| Effect | Infinite horizontal scroll of repeated text (e.g., repeated brand text) — `@keyframes mqScroll` |
| Recommendation | **OPTIONAL** |
| Rationale | Strong editorial signal — Palm Angels, Fear of God archives, 032c all use ticker strips between content sections. In v2's magazine context, a marquee between the `#home-spread` and `#br-cover` frames would mark the "page turn." Pure CSS + static HTML. Risk: feels derivative if not copy-differentiated. |
| Difficulty | **Simple CSS** — `@keyframes mqScroll { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }` with duplicated text node for seamless loop |

---

### Layer 16 — Story + Quote Section

| Field | Value |
|-------|-------|
| Source | `assets/css/homepage-v2.css` lines 590–721 |
| Effect | `.story` = two-column image + editorial text block. `.quote-section` = large centered quote with decorative `"` mark and horizontal rules |
| Recommendation | **NO** |
| Rationale | v2's `#home-voice` frame already covers the editorial voice function. Adding `.story` and `.quote-section` from live would duplicate the intent. v2's voice frame has a tighter magazine-column execution. Keep v2's version; skip the live port. |
| Difficulty | n/a — not recommended |

---

### Layer 17 — Collections Section + KC Heir Envelope

| Field | Value |
|-------|-------|
| Source | `assets/css/homepage-v2.css` lines 725–1068 |
| Live HTML | `.col-grid.stagger-grid` + `.kc-heir` envelope (front-page.php lines 345–425) |
| Effect | `.col-grid` = 4-card collection grid with magnetic hover, stagger reveal, collection name overlays. `.kc-heir` = envelope-style toggle for Kids Capsule collection with fold/unfold animation |
| Recommendation | **NO — for current v2 scope** |
| Rationale | v2 covers Home + Black Rose frames only. The full collection grid and KC heir are out of scope for this spec iteration. The KC heir question (see Part 2) requires a brand decision before implementation. Flag for v2.1. |
| Difficulty | Asset dependency (collection images) + significant JS for kc-heir toggle |

---

### Layer 18 — Lookbook Grid + Editorial Image Filter

| Field | Value |
|-------|-------|
| Source | `assets/css/homepage-v2.css` lines 1073–1153 |
| Effect | Asymmetric bento-style image grid with `filter: contrast(1.04) saturate(0.94) brightness(0.97)` applied to all images |
| Recommendation | **YES — filter only** |
| Rationale | The image filter (`contrast(1.04) saturate(0.94) brightness(0.97)`) is one CSS rule and should be applied globally to ALL photography in v2. This is the "editorial desaturation" pattern from Palm Angels and Fear of God lookbooks — it removes the "stock photo" quality from any image regardless of source. Apply to all `img` tags within frame sections. Skip the bento grid structure itself (out of v2 scope). |
| Difficulty | **Simple CSS** — `.frame img, .spread img, [class*="-photo"] img { filter: contrast(1.04) saturate(0.94) brightness(0.97); }` |

---

### Layer 19 — Craft Cards (Glass Morphism)

| Field | Value |
|-------|-------|
| Source | `assets/css/homepage-v2.css` lines 1158–1210 |
| Effect | `.craft-card` = `backdrop-filter: blur(20px)` glass-morphism cards with brand stat content (380gsm, numbered, etc.) |
| Recommendation | **OPTIONAL** |
| Rationale | Brand differentiation content (the "380gsm" stat card system) is strong CRO. The glass morphism treatment ports cleanly to standalone HTML with no dependencies. However this content duplicates the CRO section (layer 21). If CRO section is ported, skip craft cards. If CRO section is skipped, include craft cards as the brand value anchor. |
| Difficulty | **Simple CSS** — glass card pattern is pure `backdrop-filter` + `rgba` borders |

---

### Layer 20 — Newsletter Section

| Field | Value |
|-------|-------|
| Source | `assets/css/homepage-v2.css` lines 1215–1284 |
| Effect | Full-width email signup with input + submit button |
| Recommendation | **NO** |
| Rationale | Standalone v2.html has no backend. Adding a non-functional form adds visual weight with zero utility. If v2 evolves into a deployed page, wire to Klaviyo first then add. |
| Difficulty | n/a — not recommended without backend |

---

### Layer 21 — Footer CRO (Reviews + Craft + FAQ)

| Field | Value |
|-------|-------|
| Source | `template-parts/footer-cro.php` (127 lines) |
| Sections | Scarcity banner / Customer reviews grid (3 testimonials) / Value props grid (4 craft cards) / FAQ accordion (6 items) |
| Recommendation | **OPTIONAL** |
| Rationale | Footer CRO is high-conversion real estate on the live site. The content (reviews, 380gsm spec, numbered authentication, FAQ) is fully portable as static HTML — no PHP logic, all hardcoded strings. The FAQ accordion JS is minimal. Port the scarcity banner + reviews + craft grid as static HTML; skip the FAQ accordion unless v2 evolves into a demo/landing page. |
| Difficulty | **CSS + JS** — content is straightforward static HTML; requires `footer-cro.css` to be read for the styles (not yet read this session). FAQ accordion = 20 lines JS. |

---

### Layer 22 — Reduced Motion Safety Net

| Field | Value |
|-------|-------|
| Source | `assets/css/homepage-v2.css` lines 1444–1480; `assets/css/system/animations-premium.css` lines 432–455 |
| Effect | `@media (prefers-reduced-motion: reduce)` — disables all animation/transition/clip-path for accessibility |
| Recommendation | **YES** |
| Rationale | Non-negotiable for any public-facing page. Copy the reduced-motion block verbatim for every animation added. The safety-net `srRevealSafety` pattern (`animations-premium.css` lines 393–425) should also be included for any ported reveal classes — it force-shows content after 0.8s if IntersectionObserver fires late. |
| Difficulty | **Simple CSS** — copy the `@media (prefers-reduced-motion: reduce)` block and update selectors to match whatever is ported |

---

## Part 2: Structural Gap Analysis

### Section Count Comparison

| # | Live Homepage Section | v2 Frame | Status |
|---|----------------------|----------|--------|
| 1 | `#loader` — page load cover | none | ABSENT — OPTIONAL |
| 2 | Nav (fixed, scroll-blur) | Nav bar present | PARTIAL — blur missing |
| 3 | Hero (grain + vignette + particles + frame + scroll cue + ken burns) | `#home-cover` + `#home-hero` | PARTIAL — decorative layers missing |
| 4 | Editorial voice + quote | `#home-voice` | COVERED |
| 5 | Press strip | none | ABSENT — NOT RECOMMENDED |
| 6 | Marquee ticker | none | ABSENT — OPTIONAL |
| 7 | Story (image + text) | `#home-spread` (partial equivalent) | PARTIAL — different treatment |
| 8 | Collection grid (`col-grid.stagger-grid`) | none | ABSENT — out of current scope |
| 9 | KC Heir envelope | none | ABSENT — brand decision required (see below) |
| 10 | Lookbook bento grid | `#br-spread` (different treatment) | PARTIAL — filter only recommended |
| 11 | Craft cards (380gsm stats) | none | ABSENT — OPTIONAL |
| 12 | Newsletter | none | ABSENT — NOT RECOMMENDED (no backend) |
| 13 | Footer CRO (reviews + craft + FAQ) | none | ABSENT — OPTIONAL |
| 14 | Footer (links + social + legal) | none | ABSENT — minor |

### KC Heir Question

`footer-cro.php` observation #7315 (2026-05-23) flagged that the testimonial "Jade W., San Francisco" appeared in three templates — this is a data-consistency issue on the live site, not a v2 concern.

The KC Heir envelope (`kc-heir` in the live `front-page.php` lines 376–425) presents Kids Capsule collection as a special reveal. v2 has no equivalent. **Brand decision required before porting:** Does v2 cover Kids Capsule? The current v2 spec (`docs/superpowers/specs/2026-05-25-v2-mockup-design.md`) scopes v2 to Homepage + Black Rose only. Until that scope expands, KC heir is out of v2.

### Missing CRO Sections

The live homepage has three distinct CRO zones absent from v2:

1. **Scarcity signal** — "Limited Edition. Individually Numbered. Never Restocked." banner. One line of HTML + 5 lines CSS. Highest CRO ROI per complexity unit of anything in this spec.
2. **Social proof** — three customer reviews. Static HTML, no backend. Builds purchase confidence.
3. **Brand authority** — 380gsm / numbered / made-to-order / double-stitched stat cards. Converts spec-readers into buyers.

v2 as a design mockup doesn't need CRO. v2 as a deployed landing page needs all three.

---

## Part 3: Prioritized Mix-In List

### Tier 1 — Highest visual impact, lowest complexity. Port first.

| Priority | Layer | Complexity | Why First |
|----------|-------|-----------|-----------|
| T1-A | Ken Burns hero zoom | Simple CSS | One keyframe transforms static photos into alive editorial imagery. 10 lines. |
| T1-B | Film grain overlay | CSS + JS | Canvas grain converts "dark website" to "editorial print." ~40 lines total. Defines the v2 atmosphere ceiling. |
| T1-C | Editorial image filter | Simple CSS | One CSS rule applied globally. Every photo immediately reads as lookbook not e-commerce. |
| T1-D | Vignette | Simple CSS | 3 lines. Pairs with grain. Frames every hero photo. |
| T1-E | Hero floating particles | Simple CSS | Zero JS. 6 elements + 15 lines CSS. Depth for dark-field frames. |

### Tier 2 — High impact, moderate effort. Port after Tier 1 validates.

| Priority | Layer | Complexity | Notes |
|----------|-------|-----------|-------|
| T2-A | Nav scroll-blur | CSS + JS | 10 lines CSS + 5 lines JS. Navigation feels production-grade instantly. |
| T2-B | Hero scroll cue | Simple CSS | Guides scroll behavior for long-frame layout. |
| T2-C | Hero location marks | Simple CSS | Oakland brand anchor. `writing-mode:vertical-rl`. |
| T2-D | Hero frame border | Simple CSS | Must write CSS from scratch (not in homepage-v2.css). 4 lines. |
| T2-E | Button treatments (btn-sweep, btn-border-draw, btn-press) | Simple CSS | Extract 60 lines from `animations-premium.css`. CTAs stop reading like templates. |
| T2-F | Reveal system (rv-clip-up + stagger-grid) | CSS + JS | ~80 CSS + 30 JS. Selective extract only — skip split-text and Motion One dependency. |

### Tier 3 — Contextual additions. Include only if v2 scope expands.

| Priority | Layer | Complexity | Condition |
|----------|-------|-----------|-----------|
| T3-A | Marquee ticker | Simple CSS | Only between major section transitions. Pure CSS. |
| T3-B | Magnetic hover | CSS + JS | Only when collection grid section is added. |
| T3-C | Scarcity banner | Simple CSS | If v2 becomes deployed landing page. |
| T3-D | Customer reviews | Static HTML | If v2 becomes deployed landing page. |
| T3-E | Craft stat cards (glass) | Simple CSS | If v2 becomes deployed landing page and CRO needed. |
| T3-F | Page loader | CSS + JS | If v2 becomes deployed landing page or client demo. |
| T3-G | Scroll-progress bar | CSS + JS | If v2 scope expands to 12+ sections. |
| T3-H | KC heir envelope | CSS + JS + asset | After brand decision to include Kids Capsule in v2. |

---

## Part 4: Portable CSS/HTML Snippets

### Snippet A — Ken Burns (T1-A)

Add class `hero-bg` to the background image wrapper of any hero frame. CSS:

```css
.hero-bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
  transform: scale(1.05);
  animation: heroZoom 30s ease-in-out infinite alternate;
  transform-origin: center;
  will-change: transform;
}
@keyframes heroZoom {
  0%   { transform: scale(1.05); }
  100% { transform: scale(1.1) translateY(-2%); }
}
@media (prefers-reduced-motion: reduce) {
  .hero-bg { animation: none; transform: scale(1.05); }
}
```

Source: `assets/css/homepage-v2.css` lines 269–295 (adapted for standalone).

---

### Snippet B — Film Grain (T1-B)

HTML (before `</body>`):
```html
<canvas class="grain" aria-hidden="true"></canvas>
```

CSS:
```css
.grain {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 9998;
  opacity: 0.035;
}
```

JS (copy from `assets/js/homepage-v2.js` — `renderGrain` + `scheduleGrain` functions, lines 1–80 approx):
```js
(function () {
  var canvas = document.querySelector('.grain');
  if (!canvas) return;
  var ctx = canvas.getContext('2d');
  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  function renderGrain() {
    var w = canvas.width, h = canvas.height;
    var img = ctx.createImageData(w, h);
    for (var i = 0; i < img.data.length; i += 4) {
      var v = (Math.random() * 255) | 0;
      img.data[i] = img.data[i+1] = img.data[i+2] = v;
      img.data[i+3] = Math.random() * 40;
    }
    ctx.putImageData(img, 0, 0);
  }
  function scheduleGrain() { requestAnimationFrame(function () { renderGrain(); scheduleGrain(); }); }
  window.addEventListener('resize', resize);
  resize();
  scheduleGrain();
})();
```

---

### Snippet C — Editorial Image Filter (T1-C)

```css
/* Apply to all editorial/lookbook photography in v2 */
.frame img,
[class*="-photo"] img,
[class*="-cover"] img,
[class*="-spread"] img {
  filter: contrast(1.04) saturate(0.94) brightness(0.97);
}
```

Source: `assets/css/homepage-v2.css` lines 1129–1131 (generalized for v2 selectors).

---

### Snippet D — Vignette (T1-D)

HTML:
```html
<div class="vignette" aria-hidden="true"></div>
```

CSS:
```css
.vignette {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9997;
  background: radial-gradient(ellipse at center, transparent 50%, rgba(0,0,0,0.55) 100%);
}
```

---

### Snippet E — Hero Particles (T1-E)

HTML (inside hero section):
```html
<div class="hero-particles" aria-hidden="true">
  <i></i><i></i><i></i><i></i><i></i><i></i>
</div>
```

CSS:
```css
.hero-particles {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}
.hero-particles i {
  position: absolute;
  width: 2px;
  height: 2px;
  background: #fff;
  border-radius: 50%;
  opacity: 0;
  animation: ptcl 20s linear infinite;
}
.hero-particles i:nth-child(1) { left: 15%; animation-delay: 0s; }
.hero-particles i:nth-child(2) { left: 30%; animation-delay: 3s; }
.hero-particles i:nth-child(3) { left: 50%; animation-delay: 7s; }
.hero-particles i:nth-child(4) { left: 65%; animation-delay: 11s; }
.hero-particles i:nth-child(5) { left: 80%; animation-delay: 15s; }
.hero-particles i:nth-child(6) { left: 45%; animation-delay: 18s; }
@keyframes ptcl {
  0%   { transform: translateY(100vh) scale(0); opacity: 0; }
  10%  { opacity: .15; }
  90%  { opacity: .1; }
  100% { transform: translateY(-10vh) scale(1); opacity: 0; }
}
@media (prefers-reduced-motion: reduce) {
  .hero-particles { display: none; }
}
```

Source: `assets/css/homepage-v2.css` lines 306–327.

---

### Snippet F — Button Treatments (T2-E)

Copy verbatim from `assets/css/system/animations-premium.css` lines 204–266. Replace `--skyyrose-accent` with v2's accent variable name (currently `--accent` or `--gold` depending on collection context).

Key classes:
- `.btn-sweep` — background slide from left on hover
- `.btn-border-draw` — border corners grow on hover
- `.btn-press` — `scale(0.96)` on `:active`

Apply to existing v2 CTA elements: `<a class="cta btn-sweep btn-press" href="#">Shop Black Rose</a>`

---

### Snippet G — Nav Scroll-Blur (T2-A)

CSS addition to existing v2 nav styles:
```css
.nav {
  transition: background 0.3s ease, backdrop-filter 0.3s ease, border-color 0.3s ease;
}
.nav.scrolled {
  background: rgba(5, 5, 5, 0.85);
  backdrop-filter: blur(24px) saturate(1.5);
  -webkit-backdrop-filter: blur(24px) saturate(1.5);
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
```

JS (add to existing inline `<script>`):
```js
window.addEventListener('scroll', function () {
  document.querySelector('.nav')
    ?.classList.toggle('scrolled', window.scrollY > 80);
}, { passive: true });
```

Source: `assets/css/homepage-v2.css` lines 128–133 + `homepage-v2.js` `initNavScroll()`.

---

### Snippet H — Hero Frame Border (T2-D)

HTML (absolute child inside hero section, after background):
```html
<div class="hero-frame" aria-hidden="true"></div>
```

CSS (write from scratch — not in homepage-v2.css):
```css
.hero-frame {
  position: absolute;
  inset: clamp(8px, 1.5vw, 16px);
  border: 1px solid rgba(255, 255, 255, 0.07);
  pointer-events: none;
  z-index: 2;
}
```

---

### Snippet I — Hero Scroll Cue (T2-B)

HTML (inside hero, below CTA zone):
```html
<div class="hero-scroll" aria-hidden="true">
  <span>Scroll</span>
  <div class="hero-scroll-line"></div>
</div>
```

CSS:
```css
.hero-scroll {
  position: absolute;
  bottom: 2.5rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  font-size: 10px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.4);
  user-select: none;
}
.hero-scroll-line {
  width: 1px;
  height: 48px;
  background: linear-gradient(to bottom, rgba(255,255,255,0.6), transparent);
  opacity: 0.2;
  transform-origin: top;
  animation: sPulse 3s cubic-bezier(0.16, 1, 0.3, 1) infinite;
}
@keyframes sPulse {
  0%, 100% { opacity: 0.1; transform: scaleY(0.6); }
  50%       { opacity: 0.5; transform: scaleY(1); }
}
@media (prefers-reduced-motion: reduce) {
  .hero-scroll-line { animation: none; opacity: 0.3; transform: none; }
}
```

Source: `assets/css/homepage-v2.css` lines 457–487.

---

## Notes

- All Tier 1 snippets are additive — no existing v2.html markup needs to change, only new elements added
- The `.grain` canvas must be the last element before `</body>` to ensure it layers above all content
- `backdrop-filter` requires a non-opaque background on the element — the nav must have at least `background: rgba(0,0,0,0)` initially for the transition to read
- The easing token `cubic-bezier(0.16, 1, 0.3, 1)` is shared between live (`--ease-luxury`) and v2 (`--ease-out`) — both are identical curves under different token names
- No Three.js, no WebGL, no WP-specific PHP helpers used in any of the above snippets

---

*Spec authored by ArchitectUX agent — 2026-05-25*
*Source files read: front-page.php, homepage-v2.css, homepage-v2.js, animations-premium.css, premium-interactions.js, footer-cro.php, v2.html, v2-mockup-design.md*
