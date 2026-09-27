# SkyyRose full reference reproduction contract — 2026-09-21

Status: geometry and implementation specification READY; rendered approval UNVERIFIED. Mode: audit/extend existing tokens. This replaces the earlier interpretation that centered typography alone satisfies the founder. The complete composition must change.

## Authority and inspected evidence

- Founder supplied `/Users/theceo/Downloads/ChatGPT Image Sep 18, 2026 at 03_56_28 PM.png`, visually inspected this session (1024×1536). The reference is the composition authority. Founder additionally requires centered desktop/mobile headings and copy.
- Target read: abe0 `wordpress-theme/skyyrose-flagship-2/front-page.php`, `header.php`, `footer.php`, `inc/global-shell.php`, `template-parts/home/living-archive-worlds.php`, `theme.json`, and collection definitions in `functions.php`.
- Canon read: main `.wolf/memory.md`, `docs/theme-team-charter.md`, `docs/design/fashion-design-system-team.md`, `docs/brand/visual-references.md`; Black Rose `identity.json`; design-system and luxury-design-taste skills; canonical fashion-theme-team router; verified-examples standard. Authentication NOT_APPLICABLE for this local source/image inspection. No live visual claim is made.
- Product authority: main `/Users/theceo/DevSkyy/logo-registry.json` unified products via `skyyrose.core.product.get_product`; Corey’s specifications are FOUNDER_CONFIRMED. The historical abe0 catalog cannot override it. BR-002 and KIDS-002 are excluded from featured selections pending fidelity repair.

## Visual thesis and recognition devices

Reproduce the supplied reference’s contiguous dark photographic editorial composition using SkyyRose’s verified garments, Oakland heritage, existing motion and real commerce. Kith’s photographic editorial grid and Fear of God’s cinematic framing connect this direction to the established canon; the supplied reference governs the new spatial design.

Recognition devices independent of logo/copy: (1) Oakland bridge/civic photographic environments; (2) exact approved garment artwork and sport patches in foreground; (3) restrained black/silver material palette with one house accent; (4) cinematic scene framing coupled to direct garment discovery; (5) an abrupt fullbleed story interruption between compact commerce and journal. Recognition is a hypothesis until independent logo-off testing.

## Composition map — mandatory structural replacement

Measurements below are approximate normalized observations of the reference, not a claim of exact reconstructed pixels. At 1440 width the reference proportions imply a page around2160px tall before necessary utility additions. Do not retain the eight-act Living Archive layout and call it a match.

| Section | Reference location | Required anatomy | Existing source/behavior |
|---|---|---|---|
| Overlay masthead | top of hero | Logo at left, discreet center navigation, search/bag/menu right; transparent over photography; ~5vw gutters | Retain global-shell menu, search, account, mascot recall and bag hooks. Desktop inline navigation must supplement, not replace, the accessible full menu. |
| Cinematic hero | y0–441, ~43vw tall | Fullbleed photographic backdrop, compact centered copy within left42% editorial column, visible subject elsewhere, narrow right collection-link rail; one rectangular light CTA plus quiet text link; bottom motion/index controls | Existing responsive Black Rose hero and `data-recovery-hero`, video, toggle; real collection links. No invented slideshow controls: arrows must operate retained collection rail or real slide state. |
| Collection editorial | y441–699, ~25vw | Image left43%, centered title/copy/underlined action middle43%, category/collection links right14%; entire composition feels one editorial band | Existing approved collection scene resolver/media; bind links to real collections, not invented Outerwear categories. Arch is a compositional reference, not authorization to fabricate a stone tunnel. |
| Product edit | y699–934, ~23vw | Exactly four merchandise cards across desktop, square edges, large image field, quiet name/price and real quick-view affordance; no pill backgrounds or equal promotional icon cards | Existing native `product-edit` / `product-card` data and actions. Use four confirmed available SKUs with approved on-model fronts; exclude disputed SKUs. Prices/stock remain native. |
| Philosophy | y954–1240, ~28vw | Fullbleed photographic interruption, centered story copy within left35–40% column, small right-side utility/values rail, understated story link | Retain founder-approved Oakland/legacy story and existing scene imagery. Founder portrait may be used only with respectful original crop. No invented sustainability claims. |
| Journal + motion | y1264–1406, ~14vw | Left detail image22%, centered editorial copy32%, wide clickable film/experience40%, breathing gaps; distinct scale from product band | Real journal destination and existing playable video/immersive link. A play icon must play media or clearly name an experience destination. |
| Sparse colophon | y1406–1536 | Centered brand, restrained rule and small utility/legal links; generous negative space | Retain all FAQ/shipping/contact/account/legal destinations, footer dialogs, Woo bag shell, `wp_footer`. Collapse visual bulk, never remove service functionality. |

Center alignment applies to headings/copy inside their own editorial columns; it does not turn the asymmetric reference into repeated fullwidth centered blocks. Every section must have a distinct scale/cadence. Preserve all feature destinations, mascot interaction, scene discovery, product quick view, search and bag.

## Token and typography contract

Use existing `theme.json` variables, not a parallel palette or typography system. Background `--wp--preset--color--concrete-black` #0A0A0A; card/surface #111; primary text `text-secondary` #F5F5F0; muted #B3B3B3; borders #323232; one accent maximum. No brown sepia surface wash, new gradients, rounded cards, or arbitrary glass. Square CTA; circular controls only where actual icon actions require them.

Current canonical roles are Archivo display/editorial, Hanken Grotesk body/commerce, Anton utility, monospace index. Cinzel is present in theme.json caption role, but its presence does not authorize changing the whole site to a European-maison serif. The supplied reference uses high-contrast serif. **Role-specific developer constraint explicitly rejects European-maison serif direction; exact serif reproduction is therefore a documented conflict, not silently declared achieved.** Root owns resolution within applicable instruction hierarchy. Never type-render collection-script hero logos. Prohibited: cut fonts, fake script replacements, generic default SaaS stack as display direction.

Use existing fluid scale with hero title visually lighter/smaller than the previous monument wall, short lines, body16px minimum, utility12–14px for functional labels. Mobile does not shrink legal/commerce text to screenshot-scale illegibility. Keep canonical house easing and token durations.

## Asset mapping and fidelity

The existing hero route resolves `images/hero/responsive/black-rose-bay-bridge-monuments-v4-{640,1024,1440}w.webp` and `skyyrose2_collection_hero_motion('black-rose', ...)`. These are known current references, not fresh fidelity approval. Retain their source-approved resolver bindings and inspect rendered crops. Collection media comes from `skyyrose2_collection_commerce_scenes` and `hero-composed-scene`; avoid hardcoding scene file names. Journal/detail should use a verified crop from an approved existing scene or actual post featured image, never an unrelated stock garment. Founder story image currently resolves `images/about/skyy-rose-founder-hero.webp`.

No new paid imagery, no source stretching, no fake arch or fake products. If no approved image can reproduce a photographic element, preserve geometry and declare that exact image match unavailable. Mobile use responsive source/crop that keeps garment art and faces visible. Hero eager/high priority; belowfold lazy with dimensions; no global desaturation obscuring garment truth.

## Responsive and motion transformations

- ≥1200: desktop bands above; four merchandise cards; 5vw outer gutter; copy centered within columns. Hero visual min-height around560px at1440; never crop heads to meet aspect ratio.
- 768–1199: keep split editorial where legible, reduce rail width; product2×2; journal image/copy row then media. Header utilities remain reachable.
- 390: hero art-directed portrait crop with copy in a safe center column below header; collection image→copy→four real links; product2×2 only if usable card width≥160px, otherwise one column; philosophy separates text from busy image if overlay contrast fails; journal stacked; sparse footer with wrapped services.
- 320: one product column, compact nav; no clipped controls or sideways page scroll. 200% zoom must reflow.
- Preserve `data-recovery-hero-video`, `data-recovery-motion-toggle`, `skyyrose2_print_hero_bootstrap`, `skyy-hero-stage`; keep recovery rail prev/count/next/track, scene interaction and hotspot descendants functioning if repositioned.
- Retain quick-view/size-guide/search/mascot dialogs, bag shell and footer hooks. Reduced motion pauses ambient media, removes transforms, keeps poster and all destinations functional. No uniform scroll-reveal added to every block.

## Component states and accessibility

Menu/search/bag/quick-view: default, hover, focus-visible, open, close via Escape, focus return, keyboard loop, narrow-screen scroll. Cards: available, unavailable, variable selection, loading, error, saved; no decorative plus control without an actual action. Media: poster, loading, playing, paused, reduced motion, failed-media fallback. Real semantic buttons/anchors, visible labels, contrast≥4.5:1 body and≥3:1 large text/UI, targets≥44px where practical. Header must remain legible over both light and dark photographs. Native forms remain readable; do not center input values or tables just to satisfy display alignment.

## Verification matrix and independent gate

| Route/surface | Viewports | States required |
|---|---|---|
| Home fullpage |390,768,1440 +320 reflow| default; logo-off; media paused/reduced; each menu/search/bag open; all section destinations |
| Shop/collection |390,768,1440| filters, empty/no-results, cards, scene controls and native commerce |
| PDP representative + excluded featured checks |390,1440| variation/reset, gallery, quick view, add-to-bag, error/unavailable |
| Cart/checkout/account |390,1440| empty/filled, quantity/shipping, validation/login; payment execution deferred by founder |
| About/journal/contact/FAQ/shipping/search/404 |390,768,1440| layout alignment, content, links, empty/error/focus |

Run source scans for font/color/token/motion drift, rebuild committed outputs, test native controls and keyboard, compare fresh fullpage captures to reference section proportions. Independent `design-qc` reviewer must score recognition20/composition20/type15/garment15/token10/states10/motion10. ≥85/100, every category≥70%, zero hard fails, zero unverified claims. Architect/builder cannot approve own pixels.

Current score: UNVERIFIED. Hard-fail scan: not run on new candidate. Logo-off: UNVERIFIED. Token drift: known potential serif conflict above, fresh candidate pending. Captures: supplied reference inspected; no new rendered candidate. Accessibility verdict: UNVERIFIED. Docs consulted: local sources only; no framework/API claims. Independent approver: pending. Builder handoff: BLOCKED for final approval; geometry specification ready for implementation planning. Exact blockers: font conflict resolution, focused specialist artifact coverage, fresh candidate render/state evidence, independent QA approval.

## Evidence-backed examples and limits

SOURCE_VERIFIED correct example: existing front-page.php retains the responsive picture plus `data-recovery-hero-video` and toggle, and footer.php includes native dialogs/bag shell. Recompose those actual components rather than replacing their functionality with a screenshot. Evidence is local source inspection2026-09-21; it does not establish new rendered success.

ILLUSTRATIVE_UNEXECUTED incorrect example: only center the old eight-act Living Archive heading and say the supplied design has been reproduced. Correction: replace section anatomy/order/density with the measured composition table, then compare fresh fullpage captures. The founder’s explicit correction and inspected reference identify why superficial alignment fails.

Required specialist lanes awaiting dispatch/coverage by lead: brand evidence, token foundations, typography/layout, component/commerce, motion/responsive, accessibility/content, DesignOps/governance. Keep independent visual QA separate. This document does not impersonate those reviews. Integrate approved content into canonical `docs/design/skyyrose-reference-home-design-system.md` before final builder approval; this task owns only the present file.
