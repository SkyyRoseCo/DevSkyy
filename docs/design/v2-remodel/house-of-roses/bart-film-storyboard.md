# Superseded: transit-specific Jersey Series film contract

**Phase:** `v2-house-of-roses-commerce-wave`
**Status:** `SUPERSEDED / ARCHIVAL ONLY`
**Replacement:** [`skyyrose-tour-film-storyboard.md`](skyyrose-tour-film-storyboard.md)

This transit-specific concept is not the active direction. The active Jersey
Series language is the fictional, house-owned **SkyyRose Town Line**;
it does not recreate, reference, or imply an affiliation with a transit
operator. This retained document is historical context only and cannot be used
as creative, runtime, asset, or release authority.

## Purpose and non-negotiable boundaries

The header motion is a moving house index: it lets every route retain the four collection worlds without turning navigation into a decorative logo loop. The Jersey Series film is a reveal for the jerseys only: a ride from Oakland through San Francisco to San Jose, with “The Bay” as the connective chapter. It must never be folded into Black Rose product cards or used as generic Black Rose imagery.

- Native document scroll remains untouched. No wheel, touch, PageUp/PageDown, Home/End, scrollbar, or keyboard event is cancelled.
- The collection scene reel pauses for hover, focus, an explicit pause control, offscreen state, hidden tabs, user cancellation, reduced motion, Save-Data, and non-expanded layouts.
- Film audio never autoplays. The film may attempt one muted in-view play on eligible medium/expanded clients only; replay and sound require explicit controls.
- Product names, links, price, availability, selection, add-to-cart, and service truth remain WooCommerce-authoritative and outside the film controller.
- The poster, title, copy, chapter list, SKU links, and CTA are server-rendered. Video is optional progressive enhancement.
- No uniform page reveals, scroll-jacking, WebGL dependency, garment-competing particles, artificial film grain loop, cursor trail, or autoplay soundtrack.

## Current source truth

### Selected visual reference

`/Users/theceo/.codex/generated_images/019fd8c6-5ed8-7ac1-b6e3-2afa3c5adcbb/exec-ab34f21f-ce1f-40b6-8890-d4c9e101d22f.png` is founder-selected **composition reference only**. It is not a production theme asset and is not silently promoted to the SOT.

### Candidate-local collection sources

These bytes exist in the candidate. Their manifest use boundary still governs where they may ship.

| Collection chapter | Candidate source | Role in the header reel | Current boundary |
|---|---|---|---|
| Signature typography | `assets/sot/images/lockups/signature-lockup.webp` | Semantic label/art layer over the scene | Candidate-local lockup; do not reinterpret the mark |
| Signature graphic/statue | `assets/sot/images/hero/signature-golden-gate-monuments-v2.webp` | Golden Gate + Signature/SR monument scene | `FOUNDER_DIRECTED`; manifest currently names collection-hero use |
| Black Rose typography | `assets/sot/images/lockups/black-rose-lockup.webp` | Typography chapter | Candidate-local lockup |
| Black Rose graphic/statue | `assets/sot/images/hero/black-rose-typography-star-salon-v3.png` | Typography monument and star/rose monument in one scene | `FOUNDER_DIRECTED`; collection-hero use |
| Love Hurts typography | `assets/sot/images/lockups/love-hurts-lockup.webp` | Typography chapter | Candidate-local lockup |
| Love Hurts graphic/statue | `assets/sot/images/hero/love-hurts-rose-aisle-monuments-v3.webp` | Graffiti wordmark monument and star-heart monument scene | `FOUNDER_DIRECTED`; collection-hero use |
| Kids Capsule typography | Server-rendered “Kids Capsule” text in the approved collection type role | Type remains accessible and sharp; no fabricated lockup | No standalone Kids typography-lockup byte exists in candidate SOT |
| Kids Capsule graphic/statue | `assets/sot/images/hero/kids-capsule-heir-throne-v3.webp` | Full-color mascot/heir throne monument; side outfit displays removed | `FOUNDER_DIRECTED`; collection hero and Royal Procession use |

The combined scenes can produce a four-scene first integration. An eight-scene type/graphic alternation must not use `.fashion-theme/review-assets/*` until each intended derivative and its expanded header use are founder-approved and recorded in the shot manifest.

### Superseding Town Line visual

The founder-approved Town Line arrival frame is the runtime poster for the
Jersey Series entry chapter:

- Review source: `.fashion-theme/review-assets/jersey-series-town-line-train-v1.png`
- Served derivative: `assets/sot/images/hero/jersey-series-town-line-train-v1.webp`
- Vehicle identity: fictional SkyyRose electric metro with a `THE TOWN LINE`
  destination board, house star/rose emblem, and SkyyRose wordmark.

It deliberately contains no BART word mark, livery, route map, station mark,
or service claim. The older `jersey-series-bart-*` experiment was rejected by Corey on
2026-10-09. Its MP4, WebM, poster and build script were removed from the
active theme. Historical Git revisions are provenance only; do not reuse,
regenerate or adopt that film for new work.

### Jersey product truth

The canonical catalog and generated `data/sot-images.json` bind the following chapters, but the referenced product media bytes are **absent from this isolated worktree**. They are instructions to the canonical media pipeline, not usable film files yet.

| Place/chapter | SKU truth | Intended product proof | Candidate state |
|---|---|---|---|
| The Foundation | `br-003`, `br-015` | Baseball Classic black/white | SOT paths recorded; local bytes missing |
| Oakland | `br-009`, `br-012` | Last Oakland football/baseball | SOT paths recorded; local bytes missing |
| San Francisco | `br-008`, `br-014` | SF Inspired football/Giants baseball | SOT paths recorded; local bytes missing |
| The Bay | `br-010` | The Bay basketball | SOT paths recorded; local bytes missing |
| San Jose | `br-011` | The Rose hockey, catalog-described as San Jose inspired | SOT paths recorded; local bytes missing |

No Jersey Series product image may be substituted with `BR-004`, a generic Black Rose hoodie, or an invented jersey. The film remains `MEDIA BLOCKED` until the canonical bytes are materialized, eyes-on checked against the garments, and rights are recorded.

### Rejected previsualization — removed

Corey instructed on 2026-10-09: “do not use that old film get rid of irt”.
The old 16-second Jersey slideshow, both video formats, its poster and its
rebuild script were removed from the active theme. It must not be used as
campaign footage, a fallback, or the basis of the new Jersey film. This is
an explicit rejection, not a pending review candidate. Removal here is local;
it does not establish deletion of historical deployments or other checkouts.

## Header collection-scene reel

### Motion tokens

The integration CSS must alias these to the existing V2 motion system rather than introduce a second timing scale:

| Token | Value | Use |
|---|---:|---|
| `--house-motion-instant` | `0ms` | Reduced motion, media failure, and direct truth/state changes |
| `--house-motion-feedback` | `120ms` | Pressed/selected control acknowledgement only |
| `--house-motion-ui` | `180ms` | Count/control state and manual scene selection |
| `--house-motion-scene` | `420ms` | One header scene opacity/transform handoff |
| `--house-ease-enter` | `cubic-bezier(.22,.61,.36,1)` | Incoming scene |
| `--house-ease-exit` | `cubic-bezier(.4,0,.2,1)` | Outgoing scene |
| `--house-scene-hold` | `6500ms` | Expanded eligible auto-cycle; configurable only from 5–15 seconds |
| `--house-distance-scene` | `min(2vw,24px)` | Optional scenic depth, never applied to text, navigation, or garment proof |

No transition may delay a link or commerce action. The scene handoff is a single crossfade/short transform; the product and header controls remain stable.

### Sequence

The server should render the chapters in this order, repeating neither the brand mark nor a garment:

1. Signature / typography threshold.
2. Signature / SR monument at Golden Gate.
3. Black Rose / typography monument.
4. Black Rose / star-and-rose monument.
5. Love Hurts / one-line graffiti typography monument.
6. Love Hurts / star-heart graphic monument.
7. Kids Capsule / “Kids Capsule” accessible type over the heir-room threshold.
8. Kids Capsule / mascot on throne.

If only the four combined founder-directed scenes are bound, render four chapters and do not duplicate them to simulate eight.

### State machine

| State | Trigger | Visual behavior | Cancellation / equivalence |
|---|---|---|---|
| `static` | `<1024px`, reduced motion, or Save-Data | All chapters remain a native horizontal rail; no timer or inert slides | Prev/next and touch scroll remain available; all links stay in DOM order |
| `running` | Expanded, eligible, in view, unpaused | One active scene; advance every 6.5s; one scene crossfade up to 420ms | Pause control always visible; timer only, no continuous RAF |
| `paused-user` | Pause control or Escape within reel | Active scene holds | Resume requires explicit pause-control activation |
| `paused-focus` | Keyboard focus enters the reel | Active scene holds so focused content cannot leave | Resume only after focus exits, unless user pause remains |
| `paused-hover` | Fine pointer enters the reel | Active scene holds | Resume after pointer leaves, unless another pause cause remains |
| `paused-hidden` | `document.hidden` | Timer cleared | Re-evaluate on visibility return |
| `paused-offscreen` | Reel exits observer threshold | Timer cleared | Re-evaluate on intersection return |

CSS may animate only `opacity` and `transform`. Reserve the scene geometry in server markup so active-scene changes add **0.00 CLS**. Inactive carousel chapters are removed from focus and the accessibility tree only in enhanced desktop carousel mode; native and no-JS rails expose every chapter.

### Integration hooks

`assets/js/house-of-roses-motion.js` is intentionally not enqueued in this lane. The template and integration owner should enqueue it as a deferred footer script only after the matching markup and CSS exist.

Required attributes:

- Root: `[data-house-header-reel]`, optional `data-house-header-interval="6500"` and `data-house-header-start="0"`.
- Track: `[data-house-header-track]`.
- Chapters: `[data-house-header-slide]`, with `data-house-header-label="Signature typography monument"` (or the equivalent).
- Controls: `[data-house-header-prev]`, `[data-house-header-next]`, `[data-house-header-toggle]`, `[data-house-header-count]`.
- Screen-reader announcement node: `[data-house-header-status]` with an existing screen-reader-only class and `aria-live="polite"`.
- CSS state hooks: `data-house-header-mode`, `data-house-header-state`, `data-house-header-index`, `.is-active`, and `data-house-header-active`.
- Event: `house:headerchange`, whose detail is `{ index, label, source }`.

The controller never writes image URLs. PHP must resolve every source through the SOT helper and emit accurate dimensions, `srcset`, `sizes`, loading priority, and alt treatment.

## Jersey Series short film — “Ride the Bay”

### Format

- Master duration: **31 seconds**, 24 fps, 16:9, with protected 9:16 and 1:1 crops planned at shot time.
- Web delivery: AV1/VP9 or H.264 fallback only after the source master is approved; one poster remains the LCP candidate.
- Edit grammar: real train movement, hard architectural cuts, and garment close-ups. No generic luxury dissolve package and no fake handheld shake.
- Product fidelity: the garment is never regenerated from memory. Approved on-model/packshot media or a production shoot using the physical SKU is required.
- Copy: compact station-board typography; one text event per city. No fictional prices, dates, stock, or arrival claims.

### Shot and timing board

| Time | Picture / camera | Jersey chapter | On-screen text | Audio | Source status |
|---|---|---|---|---|---|
| `00:00–00:02.5` | Black frame opens on train headlights entering an Oakland platform; low angle, platform edge leads toward camera | Series entrance | `THE LINE REMEMBERS.` | Original rail-bed pulse; no agency chime | **MISSING KEYFRAME/FOOTAGE.** Requires original shoot or approved generation; no local BART footage exists |
| `00:02.5–00:05.5` | Doors open; model exits in `br-009`; full garment held long enough to read number and silhouette | Last Oakland football | `OAKLAND / THE ROOT` | Door release and one footfall; cleared/original only | **BLOCKED.** SOT record exists; candidate garment byte and transit footage absent |
| `00:05.5–00:08.5` | Platform-side cut to `br-012`; front then upper-back embroidery detail | Last Oakland baseball | `BUILT HERE.` | Track rhythm becomes beat | **BLOCKED.** SOT record exists; local byte absent |
| `00:08.5–00:11.0` | Dark tunnel/window transition; Bay lights appear as a reflection, never a fake window panorama | Transit bridge | `NEXT STOP / THE BAY` | Sub-bass travel swell | **MISSING KEYFRAME.** `black-rose-bay-bridge-monuments-v4.webp` is a verified local collection hero, but film use requires expanded-use approval and it is not transit footage |
| `00:11.0–00:14.5` | San Francisco station architecture; model rotates once in `br-008`, cut on number reversal | SF Inspired football | `SAN FRANCISCO / THE FOG` | Original metallic hit | **BLOCKED.** SOT record exists; local byte absent; station/location rights unresolved |
| `00:14.5–00:17.0` | `br-014` Giants colorway front-to-back match cut against city light | Giants baseball | `THE CITY WE TOUCH.` | Beat continues, no licensed sports audio | **BLOCKED.** SOT record exists; local byte absent |
| `00:17.0–00:19.5` | Train-car interior; series foundation in `br-003`/`br-015` across opposite seats, full logos unobscured | Baseball Classic | `00 / THE FOUNDATION` | Car ambience; no copied BART announcement | **MISSING SHOOT + PRODUCT BYTES.** Never composite inaccurate garments |
| `00:19.5–00:23.0` | Southbound arrival; `br-011` steps into teal-black station light; hood and rose crest receive a clean detail cut | The Rose hockey | `SAN JOSE / THE NIGHT` | Rail squeal resolves into score | **BLOCKED.** SOT record exists; local byte absent; location treatment unapproved |
| `00:23.0–00:26.5` | `br-010` in a centered train doorway; hold on “THE BAY,” then one natural step toward lens | The Bay basketball | `THE BAY / ONE HOUSE` | Score opens, ambience drops | **BLOCKED.** SOT record exists; local byte absent |
| `00:26.5–00:29.0` | Rapid but readable four-city recap: Oakland → San Francisco → San Jose → Bay, one garment frame each | Series recap | `EVERY CITY. EVERY NUMBER. A CHAPTER.` | Four original station-board clicks | **BLOCKED** until every included garment frame passes fidelity and rights gates |
| `00:29.0–00:31.0` | Doors close to black; rose crest/series title only, then canonical collection CTA outside the video | End card | `JERSEY SERIES / RIDE THE BAY` | Train departs; score ends cleanly | Graphic end card can be locally authored after logo-use confirmation; CTA copy is server HTML, not baked purchase state |

### Audio and text contract

- The page loads the poster silently. Autoplay, when eligible, is muted and occurs at most once.
- The audio master requires original or licensed music and cleared field recordings. Do not sample BART announcements, chimes, broadcast calls, or sports audio.
- An explicit “Turn sound on” control is the only unmute path. Leaving the viewport or hiding the page pauses playback; audible playback never restarts itself.
- If dialogue or station voice is added later, ship a WebVTT caption file. Even without speech, provide a concise transcript that includes meaningful sounds such as `[Train doors close]`.
- Do not show official BART marks, maps, train livery, or station identity in a way that implies partnership until trademark, location, and filming permissions are documented. Creative can still preserve the rider’s-eye Bay transit idea with cleared production.

### Film integration hooks

Required server markup:

- Root: `[data-house-film]`, optionally `data-house-film-autoplay="once"`.
- Video: `[data-house-film-video]`, `poster`, explicit `width`/`height`, `muted`, `playsinline`, `preload="none"`; source URL lives in `<source data-src="…">`, never `src` at initial render.
- Controls: `[data-house-film-toggle]`, `[data-house-film-sound]`, and `[data-house-film-status]`.
- Chapter list: `[data-house-film-chapter][data-start="seconds"]`. Each chapter remains a normal link to the relevant collection/PDP; the controller only reflects `aria-current` while video plays.
- Static equivalence: a visible poster, title, synopsis, complete chapter/SKU list, and ordinary Jersey Series CTA outside the `<video>`.
- CSS state hooks: `data-house-film-mode="poster|video"`, `data-house-film-state`, `data-house-film-active`, and `--house-film-progress`.
- Event: `house:filmstatechange`, whose detail is `{ state }`.

The controller does not loop the film and does not create a WebGL or canvas fallback. Unsupported video, missing media, JavaScript failure, reduced motion, Save-Data, and compact layouts all resolve to the same poster + chapter list + commerce links.

## Responsive behavior matrix

| Capability | Header | Jersey film | Focus, keyboard, and touch |
|---|---|---|---|
| `390×844` | Native horizontal scene rail; all chapters available; no timer; no inert content | Poster + title + chapter/SKU list; **0 automatic video bytes** | ≥44×44 controls, native pan-x/pan-y, no hover dependency, no fixed-height trap |
| `768×1024` | Native rail with prev/next; no autonomous cycle | Poster first; one muted in-view play may be enabled only after approved ≤450 KiB derivative exists | DOM order is media → story → chapters → CTA; controls never cover copy |
| `1440×900` | One active scene, 6.5s cycle, visible pause, prev/next, focus/hover/offscreen cancellation | Poster first; optional single muted in-view play; explicit replay/sound | Escape pauses focused header reel; native buttons handle Enter/Space; no arrow-key or scroll interception |
| Reduced motion | Native/static rail | Poster + all chapters; no video request | All information and routes equal to enhanced path |
| Save-Data | Native/static rail | Poster + all chapters; no video request | No hidden download caused by JS |
| No JS | All server-rendered scenes in DOM/native rail | Poster, synopsis, chapters, and links | Complete browse and commerce path |
| No WebGL | Identical; feature does not use WebGL | Identical; feature does not use WebGL | No loader and no missing information |

## Performance budgets

| Resource / metric | Gate |
|---|---:|
| Incremental critical CSS | ≤14 KiB gzip; scene styles cannot block initial header text/navigation paint |
| `house-of-roses-motion.js` | ≤18 KiB gzip incremental; no dependency; no long task >50ms |
| Header imagery | First visible scene ≤180 KiB at 390, ≤320 KiB at 768, ≤450 KiB at 1440; later scenes responsive/lazy where browser behavior remains stable |
| Header motion | Timeout-based stepping; **0 continuous RAF**. A RAF is used only to coalesce native rail scroll state |
| Film poster | ≤180 KiB at 390, ≤320 KiB at 768, ≤450 KiB at 1440; explicit intrinsic size; only one LCP candidate |
| Film video | 0 automatic bytes at 390, reduced motion, or Save-Data; ≤450 KiB medium and ≤900 KiB expanded for the web derivative |
| Audio | Multiplexed only inside the approved film; never a separate autoplay request |
| CLS | ≤0.05 route, with **0.00 attributable** to header scene or video/poster swapping |
| LCP | ≤2.5s p75 target / ≤3.0s stated lab profile; video not in critical path |
| INP | ≤200ms p75 target; ≤100ms lab processing for header and film controls |
| Motion | ≤1 active RAF/page overall; this controller contributes no continuous RAF; all timers stop when hidden/offscreen/preference-disabled |
| Touch/overflow | `scrollWidth <= innerWidth` at 390/768/1440; ≥44×44 CSS-pixel targets; no prevented vertical gesture |

Fonts remain within the global initial-route budget of three WOFF2 faces / 180 KiB. Do not load every collection display face for the global header; render scene typography into already-approved imagery or use the existing route-neutral display/body faces. Do not ship the 1.9 MiB Black Rose PNG directly as an initial header source; create SOT-bound responsive WebP/AVIF derivatives after expanded-use approval.

## Measurable acceptance checks

1. **Syntax:** `node --check assets/js/house-of-roses-motion.js` returns zero.
2. **No interception:** repository search shows no `preventDefault`, wheel handler, touchmove handler, smooth-scroll runtime, or document scroll mutation in this controller.
3. **Overflow:** at 390, 768, and 1440, `document.documentElement.scrollWidth <= innerWidth` on every route carrying the global header and on the Jersey film surface.
4. **CLS:** header swap and poster/video activation contribute `0.00` layout-shift score; route total stays ≤0.05.
5. **LCP/network:** film request waterfall is empty on compact, reduced motion, and Save-Data; poster is the reported LCP candidate where the film is first viewport.
6. **INP:** prev, next, pause, play, replay, mute, and chapter-link activations paint within the stated budget without waiting for media decode.
7. **Cancellation:** timer/video stop on offscreen, hidden tab, `pagehide`, reduced-motion change, Save-Data change, and user pause. An audible film never self-resumes.
8. **Keyboard:** native tab order reaches scene controls and every chapter link; Escape pauses the focused auto-cycling header and moves focus to its pause control. No focus is moved during automatic changes.
9. **Touch:** horizontal header panning does not block vertical page movement; no first-tap hover state; controls measure ≥44×44.
10. **Fallbacks:** disable JS, block video, 404 the video, force reduced motion, force Save-Data, and remove WebGL. Poster, story, all chapters, Jersey collection/PDP links, and CTA remain usable with no permanent loader.
11. **Garment fidelity:** every included frame is checked side-by-side against the canonical front/back/product-detail references. Any logo, number, color, material, trim, or silhouette mismatch fails the shot.
12. **Independent review:** founder approval of the film frames and a separate visual-QA verdict are required; the builder cannot self-approve.

## Open blockers and paid-provider boundary

- No BART/transit footage or approved transit keyframes exist locally.
- Jersey SOT paths exist, but the product bytes required for `br-003`, `br-008`, `br-009`, `br-010`, `br-011`, `br-012`, `br-014`, and `br-015` are absent from this worktree.
- No film poster, edited master, web derivatives, vertical crop, captions/transcript file, or cleared audio master exists.
- BART trademark/livery/map/announcement, station filming, model, music, and location releases are unresolved.
- The founder-directed collection heroes are currently recorded for collection-hero use. Reusing them in a global header or film requires the intended expanded use to be confirmed in the SOT/shot manifest.
- Any provider generation, video model, compositor, voice, music, stock license, or cloud render is a paid/external action and requires separate founder approval before execution. This lane made no provider call.

Until those blockers close, integrate the controller and static, SOT-bound markup only; keep the Jersey film surface in poster/storyboard mode and do not imply that a finished film exists.
