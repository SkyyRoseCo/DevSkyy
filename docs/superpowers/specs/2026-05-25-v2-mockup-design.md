> SUPERSEDED 2026-07-10/11 — fonts now per SOT.md → typography.json (Archivo / Hanken Grotesk / Anton / Cinzel + bespoke collection name-scripts; zero-CDN self-hosted woff2). Font/CDN references below are historical.

# SkyyRose v2 Mockup — Visual Direction Lock

**Date:** 2026-05-25
**Status:** Approved through Q3-synthesis
**Mode:** Standalone design ref (no WP integration, no deploy)
**Owner:** Claude (DevSkyy engineering agent)
**Deliverable file:** `docs/brand/design-mockups/v2.html`

## Mission

Lock the visual direction for SkyyRose's next-generation homepage + Black Rose collection page before any production translation. Produce one self-contained HTML file that demonstrates the **magazine-as-site** thesis with real brand assets, the locked collection fonts, and scroll-driven motion. Sign-off here becomes the contract for the production phase that follows.

## Reference Set (Locked)

Pull every visual move from these five brands. Do not reach for the European-luxury-house lineage (Bottega / Numéro / Hedi Slimane / Rick Owens / 032c / Givenchy by Tisci) — that set is locked out at `docs/brand/visual-references.md` and `feedback_brand_visual_references.md` in memory.

| Reference | What we pull |
|-----------|--------------|
| **Kith** | Monogram-led editorial photography, magazine masthead, retail-store-integrated lookbook |
| **Oaklandish** | "For The Town" civic-pride messaging, local landmark photography |
| **Culture Kings** | Drop-density on the spread frame, sneaker/sport patch hero treatment |
| **Fear of God** | Cinematic sepia photography palette, oversized type on hero, sport DNA |
| **Palm Angels** | Sport heritage motifs, embroidery macros, vintage athletic colorism |

## The Thesis

**The site is a magazine. Scroll = page turn.**

Each scroll-snap landing is a magazine page that serves a distinct role. Four roles in vertical sequence. Production-side this means each "frame" becomes its own section with scroll-driven entrance choreography, but in v2.html they read as one continuous editorial composition.

## Composition — Homepage (Surface 1 of 2)

### Frame 01 — Cover

| Element | Spec |
|---------|------|
| Masthead | "SKYY ROSE" in Cinzel 700 / 84px desktop, 48px mobile, letter-spacing 0.05em. Thin 1px rule underneath. |
| Meta block (right) | Space Mono 9px / 0.3em letter-spacing. Three lines: "VOL. IV", "S/S 2026", "THE TOWN · DROP 01". |
| Cover photo | `assets/branding/hero/forbidden-midnight-{480,768,1280,1680}w.webp` — `<picture>` with `srcset` for responsive. Fullbleed behind masthead. Dark overlay gradient top + bottom. |
| Monogram graffiti | Playfair italic 700 / 96px / `#B76E79` / rotated -7deg / overlaid on photo, positioned right-third. |
No brand slogan is authorized; retain the brand-name heading.
| By-line | Inter 10px / 0.3em letter-spacing / "By Corey Foster · Oakland · 2026" |
| Barcode | SVG inline. Below it: Space Mono 9px "03 · 26 · DROP 01". |

### Frame 02 — Hero (Town Cinema)

| Element | Spec |
|---------|------|
| Background | `assets/branding/hero/luxury-nighttime-*.webp` — Oakland industrial scene, fullbleed. Same `<picture>` responsive pattern. |
| Kicker | Space Mono 9px / 0.4em / "For The Town" / top-left. |
| **Hero title (collection lockup)** | The featured collection's **brand-script lockup image** — NOT type-rendered text. Use the canonical hero-overlay PNG/WebP/AVIF asset (see Collection Lockup Assets below). The lockup carries the collection's true identity at hero size. Place as `<picture>` with `srcset` for AVIF→WebP→PNG fallback. Drop-shadow + slight scale-on-load animation. Sized at ~50% of hero width on desktop, ~75% on mobile. |
| Subtitle | Space Mono 10px / 0.4em / drop date + edition (e.g. "SPRING DROP · 2026 · DROP 01") — stacked under the lockup image. |
| Bottom bar | Two-column Space Mono: left "Photographed in East Oakland", right "14 looks · 4 collections · One town" — separated by 1px top border. |
| Scroll behavior | Parallax: background scrolls at 0.6x, lockup image scrolls at 1x with slight scale 1 → 1.03 on scroll-into-view. |

### Collection Lockup Assets (canonical — DO NOT type-render these names)

The featured collection's identity at hero size is **always its brand-script lockup image**, never a font-rendered approximation. Each collection has a canonical hero-overlay asset locked into the repo. Use them.

| Collection | Hero overlay asset | Location |
|-----------|--------------------|----------|
| Black Rose | `br-brand-script.{avif,webp,png}` (dimensional script "The Black Rose Collection" w/ rose) — **shown by founder 2026-05-25 as the locked BR identity** | `assets/images/hero-overlays/` |
| Love Hurts | `lh-logo-combined.{avif,webp,png}` (graffiti drip "Love Hurts" lockup) | `assets/images/hero-overlays/` |
| Signature | `sig-brand-skyy-rose-gold.{avif,webp,png}` (gold "Skyy Rose" calligraphy + rose) | `assets/images/hero-overlays/` |
| Kids Capsule | `skyy-rose-collection-circular-patch.{avif,webp,png}` ("SKYY ROSE COLLECTION" circular patch) | `assets/images/logos/` |
| Brand-primary (homepage default) | `sr-monogram-rose-gold.jpeg` overlaid + `br-brand-script.webp` as feature-drop lockup if Black Rose is the featured drop | `assets/branding/` + `assets/images/hero-overlays/` |

Editorial chrome around the lockup (kickers, subtitles, masthead nameplate, attribution) keeps consistent typography across all collection pages — that's what anchors the magazine identity. Custom fonts (Cinzel, Italiana, Yellowtail, Pinyon Script, UnifrakturMaguntia) apply to:
- F01 masthead nameplate (Cinzel 700 — "SKYY ROSE" always)
- F03 voice quote (Playfair italic — founder voice register, brand-wide)
- F04 section title only (Bebas Neue — editorial)
- Body content, captions, by-lines (Inter / Space Mono)

**Custom fonts are NEVER used to spell out a collection name when a lockup asset exists.** The lockup IS the collection name in its canonical form.

### Frame 03 — Voice

| Element | Spec |
|---------|------|
| Background | Pure `#0a0a0a` with two radial gradients (rose-gold from bottom, gold from top) at low opacity. No photo. |
| Quote | Playfair Display italic 56px (desktop) / 36px (mobile), three lines: "Named after" / "a daughter." (rose-gold) / "Built by a father." |
| Attribution | Space Mono 10px / 0.5em letter-spacing / "Corey Foster · The Town" / centered under 1px top border. |
| Motion | Three-line stagger reveal on scroll-into-view, 0.15s delay between lines. Quote stays fixed for ~80vh of scroll before releasing. |

### Frame 04 — Spread

| Element | Spec |
|---------|------|
| Section title | Bebas Neue 22px / "THE COLLECTIONS" / gold. |
| Sub | Space Mono 9px / "PG 04—05 · BLACK ROSE · LOVE HURTS · SIGNATURE · KIDS" |
| Layout | 4-tile grid (1.4fr / 1fr / 1fr / 1fr). One large feature tile + three supporting. |
| Tile content | Each tile = collection thumbnail using `assets/branding/{black-rose,love-hurts,signature}-logo-hero.webp` + brand colors. |
| Motion | Tiles enter with staggered scroll-driven reveal. Hover = subtle scale 1.02 + rose-gold border glow. |

## Composition — Black Rose Page (Surface 2 of 2)

Same magazine engine, BR-specific dressing. Continuation of the homepage thesis — no register departure. This is what "one engine, four worlds" means in the new lineage.

| Element | Black Rose treatment |
|---------|----------------------|
| Cover masthead | "BLACK ROSE" Cinzel 84px replaces "SKYY ROSE" at the top. Subtitle: "A SKYY ROSE COLLECTION". |
| Cover photo | `assets/branding/black-rose-logo-hero.webp` or `black-rose-monogram-sr.jpg` if hero-fit. |
| Cover line | "Built for those who move through darkness like it's home." (from brand-DNA skill product copy spec). |
| Hero title (collection lockup) | `assets/images/hero-overlays/br-brand-script.{avif,webp,png}` — the canonical "The Black Rose Collection" dimensional script asset. Sized at ~60% of hero width (larger than homepage hero — this is BR's home turf). Drop-shadow + 1.0 → 1.04 scale on scroll-into-view. NOT type-rendered. |
| Hero subtitle | "Vol. IV · Spring 2026 · The Town" — Space Mono 10px / 0.4em letter-spacing. |
| Hero | Sepia palette darkened. Sport patch macro inset (NFL/NBA/MLB/Hockey patches as small product-detail squares from `assets/images/hero-overlays/br-patch-*.webp`). |
| Voice frame | **"You wear it / because you / already stood up."** — Black Rose story tagline, verbatim founder-locked from `docs/brand/collection-stories.md` (line: Story Tagline). 3-line stack matches the homepage voice-frame pattern. Playfair italic. Middle line in rose-gold. Attribution: "Black Rose · The Town · 2026". |
| Spread | 6-8 Black Rose SKUs only. Loaded from `data/skyyrose-catalog.csv` filtered by collection=black-rose. Pulled via static reference in this mockup (not a CSV runtime read). |
| Palette tweak | Silver `#C0C0C0` replaces gold accent in this view. Rose-gold and crimson stay. |

## Typography System

All loaded via Google Fonts `@import` in v2.html (no theme integration). When this spec translates to production, fonts come from `assets/fonts/` self-hosted woff2.

| Role | Font | Where |
|------|------|-------|
| Magazine masthead | Cinzel 700 | F01 nameplate ("SKYY ROSE" only) |
| **Hero title** | **NONE — collection lockup IMAGE used** | F02 hero (see Collection Lockup Assets) |
| Section title | Bebas Neue | F04 section title only |
| Voice quote | Playfair Display italic 400 + 700 | F03 quote (brand-wide editorial voice, not collection-driven) |
| Cover line | Bebas Neue + Playfair italic accent | F01 |
| Meta / kickers / attribution | Space Mono 400 | F01 meta block, F02 kicker, F03 attribution, F04 sub |
| Body / nav | Inter 300/400/600 | by-lines, nav, captions |
| Brand-mark accent | Playfair Display italic 700 | "SR" graffiti on F01 (when used as inline-rendered accent) |

**Collection-specific fonts in reserve** — Italiana, Yellowtail, Pinyon Script, UnifrakturMaguntia, Cinzel beyond masthead — used only on COLLECTION INTERIOR surfaces (PDP, future collection landing) when the lockup image isn't appropriate (e.g., body callouts, secondary headings). The brand-script lockup carries the collection identity at hero. Type-rendered display fonts back up the lockup in the interior, not in place of it.

Collection-specific accents (held in reserve for collection pages):
- Italiana — Signature display
- Yellowtail — Love Hurts script accent
- Pinyon Script — Signature script accent
- UnifrakturMaguntia — Black Rose gothic accent (sparingly, only for special drops)

## Motion Budget

Standalone mockup, so motion runs in-browser with vanilla JS + CSS. No Three.js for v2 — that decision was overturned by the brand-DNA reset.

| Effect | Implementation |
|--------|----------------|
| Frame entrance reveal | IntersectionObserver toggling `.is-visible` class with CSS transition |
| Parallax (F02 background) | `requestAnimationFrame` + `getBoundingClientRect()` → `translateY(scrollY * 0.6px)` |
| Voice quote stagger | CSS `transition-delay` on `.is-visible` per-child |
| Spread tile stagger | Same pattern as voice, with per-tile delay |
| Hover micro-interactions | CSS-only `transform` + `box-shadow` transitions |
| Reduced-motion fallback | `@media (prefers-reduced-motion: reduce)` forces all `.is-visible` states immediately, suppresses parallax |

No WebGL. No canvas. The "visualize the impossible" requirement is met by **typography + scroll choreography + photographic composition**, not by 3D scenes.

## Assets Used (verified 2026-05-25)

### Photography (background imagery — F01 + F02)

Located in `wordpress-theme/skyyrose-flagship/assets/branding/hero/`:

| Asset | Used in |
|-------|---------|
| `forbidden-midnight-{480,768,1280,1680}w.webp` | F01 cover photo (homepage) |
| `luxury-nighttime-{480,768,1280,1680}w.webp` | F02 hero photo (homepage) |
| `beauty-and-beast-{480,768,1280,1680}w.webp` | F02 hero photo alternate (Black Rose page) |

### Collection lockup overlays (hero title images — F02)

Located in `wordpress-theme/skyyrose-flagship/assets/images/hero-overlays/`:

| Asset | Used in | Notes |
|-------|---------|-------|
| `br-brand-script.{avif,webp,png}` | F02 Black Rose hero title | 89K / 182K / 693K. **Founder-confirmed 2026-05-25 as locked BR identity** |
| `lh-logo-combined.{avif,webp,png}` | F02 Love Hurts hero (future page) | 93K / 139K / 548K |
| `sig-brand-skyy-rose-gold.{avif,webp,png}` | F02 Signature hero (future page) | 93K / 132K / 389K |
| `br-patch-{nfl-football,nba-basketball,mlb-baseball,hockey}.{avif,webp,png}` | F02 BR page sport patch macro insets | Used as small detail squares |

Kids Capsule lockup (`skyy-rose-collection-circular-patch.{avif,webp,jpeg}`) lives in `wordpress-theme/skyyrose-flagship/assets/images/logos/` — used on F02 hero only when Kids page is built (future phase).

### Nav-bound + monogram (chrome)

| Asset | Used in |
|-------|---------|
| `assets/branding/skyyrose-monogram-nav.webp` (742B) | Mockup nav-bar monogram |
| `assets/branding/sr-monogram-rose-gold.jpeg` (or .webp variant) | F01 SR graffiti reference — but in mockup rendered as text overlay per F01 spec (Playfair italic 700) since the rotation/positioning differs from the source asset's framing |

### Collection identity assets (F04 spread tiles)

Located in `wordpress-theme/skyyrose-flagship/assets/branding/`:

| Asset | Used in |
|-------|---------|
| `black-rose-logo-hero.webp` (50K) | F04 spread tile — Black Rose |
| `love-hurts-logo-hero.webp` (205K) | F04 spread tile — Love Hurts |
| `signature-logo-hero.webp` (39K) | F04 spread tile — Signature |
| Kids Capsule placeholder | F04 spread tile — Kids (use `skyy-rose-collection-circular-patch.webp`) |

Assets get inlined via relative path from `docs/brand/design-mockups/v2.html` → `../../../wordpress-theme/skyyrose-flagship/assets/...`. Browser resolves at file:// or local-server URLs.

## File Structure

```
docs/brand/design-mockups/
├── v2.html                  ← the deliverable
├── v2-assets/               ← only if any inline imagery is custom-made for the mockup
└── README.md                ← short pointer to this spec
```

v2.html is one file. CSS embedded in `<style>` (no external stylesheet). JS embedded in `<script>` (no module imports). Fonts via Google Fonts `@import`.

## Acceptance Criteria

1. v2.html renders all 4 frames for both surfaces (homepage + Black Rose) in a single scrollable document.
2. Real brand assets load from `../../../wordpress-theme/skyyrose-flagship/assets/branding/`.
3. All 9+ fonts in the system render correctly (visual check).
4. IntersectionObserver-driven reveals run smoothly at 60fps on M-series laptops.
5. `prefers-reduced-motion: reduce` correctly suppresses all motion + forces all reveals to visible.
6. Mobile breakpoint (≤768px) holds composition (headlines downsize per spec, tile grid collapses).
7. No external CDN dependencies beyond Google Fonts. No npm. No build step.
8. Lighthouse accessibility score ≥95 (alt text, semantic landmarks, contrast — checked locally).

## Out of Scope (do not do in this artifact)

- WordPress theme integration
- WooCommerce product card rendering
- Real cart/checkout flow
- Production CSS architecture (`design-tokens.css`, `landing-pages.css`, etc.)
- Three.js or WebGL of any kind
- Collection pages beyond Black Rose (Love Hurts / Signature / Kids saved for future)
- Per-collection PDP variants

### Canon reservations for future collection pages

When Love Hurts gets its own v2-style page (future phase, separate spec):

- Voice frame line: **"Hurts is the bloodline that raised me."** — founder-locked 2026-05-23. "Hurts" is Corey Foster's family name. This line belongs ONLY to Love Hurts. Do not place it on Black Rose, Signature, or Kids.
- Palette: Crimson `#DC143C` accent on deep black background.
- Display font: Yellowtail script accent + Playfair italic primary.
- Source: `docs/brand/collection-stories.md` → Love Hurts section.

Reservation noted to prevent the same misattribution loop on the next pass.

## Implementation Mode

Single Write call producing one HTML file (estimated 800-1500 lines depending on CSS depth). After v2.html ships:

1. User opens `docs/brand/design-mockups/v2.html` in browser.
2. Validate visually against this spec.
3. If approved → translate to production templates as a separate phase (becomes its own spec + plan + execute cycle).
4. If refine needed → I iterate v2.html in place until approved.

## Risk

| Risk | Mitigation |
|------|------------|
| Real brand assets at relative path fail to resolve | Test load once in browser before declaring v2.html complete. |
| Google Fonts CDN fails offline | All 9 fonts are also available self-hosted at `assets/fonts/` — fallback path documented as a comment in v2.html. |
| Mockup oversells what production can ship | Spec explicitly notes "no Three.js" + "vanilla JS only" so production translation is realistic. |
| 60fps degraded on older mobile | Parallax disabled at ≤480px; reduced-motion respected. |

## Cross-references

- `docs/brand/visual-references.md` — locked reference set
- `~/.claude/projects/-Users-theceo-DevSkyy/memory/feedback_brand_visual_references.md` — agent-side enforcement of the lineage
- `~/.claude/skills/skyyrose-brand-dna/SKILL.md` — brand DNA skill
- `wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv` — Black Rose SKU list for F04 spread
- `wordpress-theme/skyyrose-flagship/assets/branding/` — hero photography + collection logos source
