# SkyyRose Interactive Commerce Research Report

> **SKYYROSE LLC · FASHION THEME BRAIN**

*Generated 2026-08-06 · Evidence snapshot for V2 planning · Status: research, not release approval*

## Executive summary

The current frontier is not “more animation.” The strongest experiences connect a distinct world to an action: Lacoste turns membership into design and voting, Gucci turns a collection into a playable mystery, DICH uses a WebGL/scroll narrative to make a fashion world explorable, and Dolce&Gabbana frames product discovery as a sensory ritual. Award galleries classify these patterns with tags such as fullscreen, WebGL, animated, scroll, video/sound, and unusual navigation ([Lacoste CSSDA](https://www.cssdesignawards.com/sites/lacoste-members-experience/46965/), [DICH CSSDA](https://www.cssdesignawards.com/sites/dich-fashion/47473/), [Dolce&Gabbana CSSDA](https://www.cssdesignawards.com/sites/dolce-gabbana-beauty-fresh-skin/48116/), [Finely Crafted Awwwards](https://www.awwwards.com/sites/finely-crafted)).

Commerce leaders are simultaneously increasing decision support: Google introduced AI shopping guidance, query fan-out, own-photo virtual try-on, saved/shareable looks, price tracking, and an agentic checkout concept ([Google Shopping](https://blog.google/products-and-platforms/products/shopping/google-shopping-ai-mode-virtual-try-on-update/)). Shopify’s merchandising analysis describes rich PDPs with AR/3D, spin-and-zoom, video, user-generated photos, how-to content, and interactive size/style guides ([Shopify](https://www.shopify.com/ca/enterprise/blog/ecommerce-merchandising-trends)). DHL reports that 7 in 10 shoppers globally want AI-powered shopping features, with virtual try-on, AI assistants, and voice search among the most requested ([DHL](https://group.dhl.com/en/media-relations/press-releases/2025/dhl-e-commerce-trends-report-2025.html)).

SkyyRose should adopt the useful layer first: high-density product truth, fit confidence, shoppable stories, chapter transitions, controlled 3D/360 media, and member co-creation. WebGL worlds, AI try-on, and agentic buying belong behind explicit pilots with performance, privacy, catalog, and founder gates.

## Sites scraped and what is present

| Site / evidence | Observed interactive feature | SkyyRose adaptation |
|---|---|---|
| **Lacoste Members Experience** — CSSDA WOTD score 9.15; tagged fullscreen/WebGL ([award](https://www.cssdesignawards.com/sites/lacoste-members-experience/46965/)) | Members design a polo from shape, colors, and patterns; submit, vote, earn badges, and connect boutique QR activity ([Lacoste newsroom](https://www.lacoste.com/gb/news/events/new-lacoste-member-experiences.html)). | `loyalty`, `campaign-launch`, and `store-appointment`: limited co-design challenge, vote ledger, badge, and boutique unlock. |
| **DICH™ Fashion** — CSSDA WOTD score 8.39; tagged animated/scroll/WebGL ([award](https://www.cssdesignawards.com/sites/dich-fashion/47473/)) | Live site uses a protocol/file-system fiction, style toggles, numbered chapters, discover links, collection “drops,” narrative copy, and an idea-submission form ([live site](https://dich-fashion.webflow.io/)). | `home`, `collection`, `lookbook`: Oakland archive/protocol chaptering, collection drops, progressive reveal, and an optional idea form. |
| **Dolce&Gabbana Fresh Skin** — CSSDA WOTD score 8.14; tagged animated/liquid/video-sound ([award](https://www.cssdesignawards.com/sites/dolce-gabbana-beauty-fresh-skin/48116/)) | A phygital, sensory product-discovery ritual; live experience is a JavaScript application with a commerce collection fallback ([live tool](https://beautytools.dolcegabbana.com/en-it/fresh-skin/)). | `home`, `collection`, `product`: material/ritual chapter with sound optional, product facts always available, and a static fallback. |
| **Finely Crafted / Shoe Surgeon studio** — Awwwards SOTD; immersive 3D studio tour, unusual navigation, transitions, sound, WebGL, GSAP, Vue ([award](https://www.awwwards.com/sites/finely-crafted), [site](https://www.finely-crafted.com/)). | A navigable craft space makes process the story rather than a flat gallery. | `lookbook`, `about`: Oakland studio/craft tour as an optional desktop layer; linear chapters remain the mobile and reduced-motion path. |
| **Gucci La Famiglia: Mystery Unfolds** — live official game ([Gucci](https://www.gucci.com/int/es/nst/la-famiglia-mystery-unfolds)); coverage describes an AI-powered detective story with characters, rooms, questioning, and clues ([BusinessToday](https://www.businesstoday.com.my/2026/03/17/guccis-quirky-la-famiglia-mystery-unfolds-is-now-a-mystery-game/)). | Playable narrative turns lookbook characters into a mystery with discovery and progression. | `campaign-launch`, `lookbook`: optional “find the rose” chapter game with clues tied only to approved collection facts; never gate purchase behind play. |

## Commerce features present in the market now

1. **AI shopping guide and query fan-out:** customers describe intent, constraints, and context; the system returns visual product paths ([Google](https://blog.google/products-and-platforms/products/shopping/google-shopping-ai-mode-virtual-try-on-update/)).
2. **Own-photo virtual try-on:** customers upload a full-length photo, see generated looks, and can save/share them ([Google](https://blog.google/products-and-platforms/products/shopping/google-shopping-ai-mode-virtual-try-on-update/)).
3. **Price tracking and agentic checkout:** shoppers set size/color/budget preferences, receive price-drop notices, then confirm purchase through an agentic flow ([Google](https://blog.google/products-and-platforms/products/shopping/google-shopping-ai-mode-virtual-try-on-update/)).
4. **Visual search and style matching:** image-led search and “show me something like this” discovery are becoming expected inputs; implementation must disclose ranking and catalog limits ([Shopify](https://www.shopify.com/ca/enterprise/blog/ecommerce-merchandising-trends), [DHL](https://group.dhl.com/en/media-relations/press-releases/2025/dhl-e-commerce-trends-report-2025.html)).
5. **High-density PDPs:** 360 imagery, zoom, 3D/AR, videos, UGC, how-to modules, and interactive size/style guides support in-store-like evaluation ([Shopify](https://www.shopify.com/ca/enterprise/blog/ecommerce-merchandising-trends)).
6. **Fit evidence and filters:** benchmarked apparel UX work covers 14 sites, 7,000+ performance scores, and 6,000+ best-practice examples; it highlights fit subscores and clear size filtering as important areas ([Baymard](https://baymard.com/blog/apparel-and-accessories-ux-benchmark-2025)).
7. **Voice and conversational shopping:** DHL identifies voice-enabled search, AI assistants, and virtual try-on among requested capabilities ([DHL](https://group.dhl.com/en/media-relations/press-releases/2025-dhl-e-commerce-trends-report-2025.html)).
8. **Member co-creation:** design tools, community voting, badges, and physical-location QR unlocks turn loyalty into participation ([Lacoste newsroom](https://www.lacoste.com/gb/news/events/new-lacoste-member-experiences.html)).
9. **Playable editorial:** mystery, clue, and chapter mechanics are being used to extend a collection story beyond passive scrolling ([Gucci](https://www.gucci.com/int/es/nst/la-famiglia-mystery-unfolds)).
10. **Phygital rituals:** product discovery is framed as an interactive sensory sequence, with commerce paths available inside the experience ([Dolce&Gabbana CSSDA](https://www.cssdesignawards.com/sites/dolce-gabbana-beauty-fresh-skin/48116/)).

## SkyyRose rollout scaffold

### Build now — core theme value

- Chapter-based Home, Collection, Lookbook, About, and Journal transitions using CSS/IntersectionObserver.
- Product media sequence with front/back/detail/movement, zoom, video poster, and explicit loading/error states.
- Sticky product/story split on PDP and Lookbook with mobile linear fallback.
- Interactive size/fit guide, fit evidence, model reference, and localized units.
- Shoppable editorial hotspots that become labeled product lists on mobile.
- Stateful CTA feedback: loading, success, unavailable, waitlist, error, keyboard, and reduced motion.
- Search/filter drawer, visual crop consistency, and a “search by image” extension point without pretending the model is live.

### Pilot — founder and catalog gates

- 360-degree product viewer from a 36–72 frame SOT image sequence.
- AI style advisor that returns only catalog-backed products and discloses recommendation logic.
- Own-photo try-on through an approved provider, with consent, deletion, generated-image labeling, and manual review.
- SkyyRose co-creation challenge with badge, voting, moderation, and an explicit no-purchase gate.
- Phygital Oakland QR chapter or appointment unlock.
- One campaign mystery chapter with a skip-to-shop path and no purchase dependency.

### Future — only after proof

- WebGL collection world with a DOM commerce overlay and static/mobile fallback.
- WebAR garment preview where garment assets, privacy, device support, and fit limitations are verified.
- Conversational/voice shopping with accessible text parity.
- Price tracking or agentic checkout only if WooCommerce, payment, consent, fraud, and customer support contracts are ready.

### Reject or quarantine

Liquid-glass chrome, gradient text, generic gradient meshes, cursor trails, custom cursors, fake scarcity countdowns, hover-only product information, autoplay sound, scroll-jacking, unverified 3D garments, and any animation that delays checkout or hides recovery.

## Evidence and implementation gates

Every feature needs a page ID, stable section ID, data source, event schema, fallback, performance budget, accessibility behavior, and candidate-bound evidence. A feature is not “present” because a concept render looks impressive: the Theme Team must prove it with keyboard/mobile/reduced-motion checks, real catalog behavior, and independent visual QA.

## Sources

1. [Lacoste Members Experience — CSS Design Awards](https://www.cssdesignawards.com/sites/lacoste-members-experience/46965/)
2. [Lacoste member experiences newsroom](https://www.lacoste.com/gb/news/events/new-lacoste-member-experiences.html)
3. [DICH Fashion — CSS Design Awards](https://www.cssdesignawards.com/sites/dich-fashion/47473/)
4. [DICH live site](https://dich-fashion.webflow.io/)
5. [Dolce&Gabbana Fresh Skin — CSS Design Awards](https://www.cssdesignawards.com/sites/dolce-gabbana-beauty-fresh-skin/48116/)
6. [Dolce&Gabbana Fresh Skin live tool](https://beautytools.dolcegabbana.com/en-it/fresh-skin/)
7. [Finely Crafted — Awwwards](https://www.awwwards.com/sites/finely-crafted)
8. [Finely Crafted live site](https://www.finely-crafted.com/)
9. [Gucci La Famiglia: Mystery Unfolds](https://www.gucci.com/int/es/nst/la-famiglia-mystery-unfolds)
10. [Google Shopping AI Mode and virtual try-on](https://blog.google/products-and-platforms/products/shopping/google-shopping-ai-mode-virtual-try-on-update/)
11. [Shopify immersive merchandising trends](https://www.shopify.com/ca/enterprise/blog/ecommerce-merchandising-trends)
12. [Baymard apparel UX benchmark](https://baymard.com/blog/apparel-and-accessories-ux-benchmark-2025)
13. [DHL E-Commerce Trends Report 2025](https://group.dhl.com/en/media-relations/press-releases/2025-dhl-e-commerce-trends-report-2025.html)

## Methodology

Searched current award galleries, award detail pages, live brand experiences, official commerce platform updates, and current apparel UX research on 2026-08-06. Scraped the accessible text layer of five interactive/immersive examples and cross-checked feature claims against official brand/platform or award pages. Visual implementation claims remain subject to browser inspection and source-page availability.
