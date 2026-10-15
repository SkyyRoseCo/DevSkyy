# V7 Product Card Merge — Worklist

**Goal:** Merge V3 (lookbook-lens) grid *display* + V6 *product card* (collection palette + chrome)
+ collection-logo backdrop behind the product + auto-advance carousel (front→back→detail,
hover pauses on current frame). Embed into shop + collection grids on skyyrose.co. Layer in
genuinely-premium 21st.dev features (not generic).

## Decisions locked
- Display = V3 grid (3-col `auto-fill minmax(340px)`, cards `aspect-ratio:3/4`). NOT index table.
- Card = V6 `[data-collection]` palette engine + card chrome (buttons/typography).
- Image mechanic = carousel auto-advance, hover-pause. **ONE mechanic on the card image** (no lens/zoom bolted on).
- Card-motion accent = at most ONE (tilt OR parallax — they fight). Founder picks.
- Logo backdrop = collection logo behind product. **Asset inbound from founder.**
- 21st premium = founder-selected from verified shortlist; ported to PHP later (React≠PHP, port recipe proven on cine-hero).

## Plan
- [x] Recon workflow: extract V3 grid+card spec ∥ V6 palette+chrome+bundle+carousel JS ∥ verify 7 curated 21st components (real source). DONE — 6 keep, marquee CUT (Remotion).
- [x] Build standalone `prototypes/product-card-variants/v7-lookbook-card/index.html` (additive layer on v6 base: V3 grid + V6 palette + carousel hover-pause + logo-backdrop placeholder + ported magnetic CTA).
- [x] Self-verify: Chrome DevTools — 6 cards, palette per collection, carousel autoplay+hover-pause+IO-gate+scroll-resume, console clean, desktop 3-col + mobile 1-col. IO threshold bug (0.2→0) fixed.
- [x] Present prototype + screenshots + verified 21st shortlist (preview links) to founder.

### Eyes-on finding
- Logo backdrop barely visible: SOT shots are NOT cutouts; own bg occludes logo under object-fit:contain. "Logo behind product" needs cutouts (BackgroundRemovalService, S2041) OR framed composition. Pending founder composition pick.
- [ ] GATED on founder: real collection logos + 21st pick + card-accent pick + embed-target confirm.
- [ ] Wire chosen 21st features + real logos → final prototype → eyes-on.
- [ ] Port to WP theme (template-part + enqueue slug-gate + wp_localize + WC Store REST), rebuild `.min`.
- [ ] STOP-AND-SHOW deploy to skyyrose.co; Playwright verify live mobile+desktop.

## Status 2026-06-28
- v7 prototype = REAL verified hub images only (27 SKUs); hallucinated source ripped out. Locked rule [[feedback_real_products_only]].
- Render cleanup: 3 review sheets live over `http://127.0.0.1:8765/` (render-review.html=1719 imgs all engines · glb-models.html=33 textured 3D · verified-contactsheet.html). Founder triaging; downloads skyyrose-delete.json / skyyrose-3d-delete.json → I delete his ✗'s. NOTHING deleted yet.
- 3D GLB improve: solidify = DEAD END (bug-133, slab≠garment + scale blowup). Plan = per-SKU triage: ~6 real-3D (flatness>0.35: sg-007/sg-001/lh-003/br-007/sg-009/lh-004) get cleanup+re-skin; 11 flat planes → serve 2D hub photo; ~8 middle = founder eye. Decoders vendored renders/3d/_viewer/ (bug-132).
- **DECISION (founder): BOTH IN PARALLEL** — wire V7 cards→WP now; founder triages GLB sheet; I cleanup+re-skin 3D survivors when ✗-list lands.

## WP port plan (in progress)
- [ ] Recon theme integration (grid render · SKU→image resolver · enqueue slug-gate · product data) — workflow wwl771n7h.
- [ ] Build template-part `product-card-v7` + CSS + carousel JS; resolve images via hub verdict:verified (server-side gate).
- [ ] Slug-gate enqueue (shop + collection); rebuild .min.
- [ ] Verify locally (wp-playground / standalone) — no production.
- [x] DEPLOYED v1.6.6 → skyyrose.co (2026-06-28); live-verified 8 v7cards desktop+mobile, 0 broken, verified imgs, 4 palettes, holo=0.

## Gates
- No production touch / no paid API in prototype phase (all autonomous-OK).
- Deploy = STOP-AND-SHOW.
- Product images = eyes-on fidelity gate before any render/publish (CLAUDE.md mandatory).
