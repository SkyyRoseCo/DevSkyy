# More access for the fashion e-commerce motion/3D workflow: Research Report
*Generated: 2026-10-14 | Sources: 40+ pages (6 Exa searches, 20 GitHub API checks, 11 HTTP checks) | Confidence: Medium*

## Executive Summary
Free, viewable-source material for **fashion product-detail, size-selector, cart-drawer and add-to-cart motion** exists, but it is thin and mostly small personal repos, so licence and quality are the real filters. Licences were re-checked against the GitHub API rather than trusting READMEs, which caught at least one mismatch. The strongest free replacement for the paid 60fps MCP is an open-source Awwwards MCP that records live-site motion ([Awwwards-mcp](https://github.com/INSANE0777/Awwwards-mcp)). The best free pattern gallery for fashion e-commerce is [GoodCart](https://www.goodcart.design/), but it is screenshots only, with no motion and no code. Streetwear-specific references with real cart and size-selector behaviour are agency concepts (no source), not repos.

## 1. Fashion / e-commerce PDP, size selector, cart motion
- GoodCart is a gallery of 1160+ full-page screenshots from 396 live ecommerce sites, filterable by industry (incl. Fashion & Apparel), page type and UX pattern such as sticky add to cart, quick add and variant swatches, on desktop and mobile ([GoodCart](https://www.goodcart.design/)).
- A streetwear drop-store concept documents a size selector "with real states for hover, selected and sold out", a side cart drawer, hover image swap and a reduced-motion fallback ([Studio Ubique GRYM](https://www.studioubique.com/work/streetwear-ecommerce-website-design/)). Design reference only; it is a staging concept.
- A streetwear label site uses the View Transitions API so the tapped card image "flies" into the product page, sold-out sizes are struck through, and a scroll-scrubbed orbit video drives the camera; it also falls back when View Transitions are unsupported and under reduced motion ([Webforging StreetWearzzz](https://webforging.de/referenzen/streetwearzzz)). Imagery is AI-generated per the page. Live at streetwearzzz.de (HTTP 200).
- Open code with the exact interactions: fly-to-cart along a parabolic arc (GSAP), size pills using Framer Motion `layoutId`, sticky add-to-cart bar, quick-view modal ([ecommerce-product-showcase](https://github.com/KaranChandekar/ecommerce-product-showcase)). README says MIT but the GitHub licence field is empty.
- Add-to-cart flight with 9 configurable presets (straight, parabola, spiral, elastic paths) and MIT licence ([add-item-to-cart-animation](https://github.com/EricTsai83/add-item-to-cart-animation)).
- A sneakers storefront with cart drawer, wishlist and 3-step checkout, but no licence ([shopnest](https://github.com/sarfrazsaeed/shopnest)).
- A dark apparel/streetwear Next.js template with gallery zoom, stock-state variants and a free-shipping-progress cart drawer ([Nocturne Harbor](https://nocturneui.com/templates/harbor)). Price and licence were not stated on the page read.

## 2. Open scroll-driven and 3D source
- Canonical R3F shoe configurator, MIT, 132 stars, pushed 2026-10-13 ([pmndrs/examples](https://github.com/pmndrs/examples/tree/main/demos/shoe-configurator/src)).
- A Claude Code skill with four three r170 + GSAP + Lenis templates, locked versions and a documented anti-pattern list; MIT ([awwwards-3d](https://github.com/tsogjavklann/awwwards-3d)). It is a skill that runs with agent permissions: review before use.
- A vanilla Three.js + GSAP + Lenis scroll experience written up as study material ([CherryTree](https://github.laiyagushi.com/boydcroberts/CherryTree)); not commerce.
- Sixty GSAP recipes where reduced motion, no-JS fallback and cleanup are part of the contract, with a WordPress adapter ([synced-motion](https://github.com/SyncedCo/synced-motion)).
- Small garment configurators exist ([fabric-3d-designer](https://github.com/rajpal-se/fabric-3d-designer), [3D-Clothing-Configurator](https://github.com/afilahkle/3D-Clothing-Configurator)) but both have **no licence**.

## 3. Free alternatives to paid galleries and MCPs
- An MIT MCP server for Awwwards with `get_motion_dna` (animation libraries, ScrollTrigger stats, easing vocabulary) and `record_site_motion`; "No API key" ([Awwwards-mcp](https://github.com/INSANE0777/Awwwards-mcp)). 106 stars, pushed 2026-10-12. Needs Playwright.
- 288 animated components, MIT-0, React+Tailwind and plain HTML/CSS/JS with no dependencies ([movin.design](https://movin.design/components/)).
- A Next.js library claiming 500+ motion variants, 20 of them e-commerce (Add to Cart, Price Flip, Wishlist Toggle), MIT ([motionary](https://github.com/aimkick/motionary)). The 500+ figure was not verified; 1 star.
- Free copy-paste e-commerce components in React and HTML, including a shoe-size gauge ([We.Inc](https://we.inc/components/ecommerce)). Licence terms not read; the set leans whimsical (pizza, lipstick).

## 4. Galleries with APIs, repos or MCP servers
- A local MCP registry of 30 patterns, 20 components and 15 motion configs (Framer Motion, GSAP, CSS), MIT, Fuse.js search ([ui-elite-patterns](https://github.com/maahigoel/ui-elite-patterns)).
- An MCP that extracts design tokens and motion rules from any live site into a local SQLite library; uses Claude vision and Voyage embeddings, so it carries API cost ([design-dna-mcp](https://github.com/olartgabo/design-dna-mcp)).
- Declarative, config-driven interactions on native browser APIs with SSR CSS generation, from Wix ([wix/interact](https://github.com/wix/interact/)); MIT.

## 5. Web motion breakdowns and code (not SwiftUI)
- Motion's own site states the library is "Completely free to use, MIT licensed and open source" and that its MCP exposes "490+ example sources" ([motion.dev](https://motion.dev/)). Which of those sources need Motion+ was not determinable from the page.
- Attribute-driven animation, under 7 kB gzipped, reduced-motion built in ([Vivace](https://usevivace.dev/)); web components with spring physics ([Motion Components](https://www.motion-components.dev/)); scroll reveal at 8 KB, 147 stars, MIT ([usal](https://github.com/usaljs/usal)).
- Paid: a visual animation builder and WordPress plugin at EUR 149/year, with a free zero-dependency npm SDK ([Motion.page](https://motion.page/)).

## Ranked shortlist (top 15)
| # | Item | Access | Rendering | Fit |
|---|------|--------|-----------|-----|
| 1 | GoodCart | Free to browse (full filter access not verified) | Server-rendered screenshots | Fashion & Apparel slice, PDP/quick-add patterns; no motion or code |
| 2 | ecommerce-product-showcase | Source open, licence field NONE | Next.js app | Fly-to-cart, size pills, sticky bar, quick view |
| 3 | add-item-to-cart-animation | MIT | Next.js | Add-to-bag flight presets |
| 4 | Awwwards-mcp | MIT, free | Needs Playwright | Free stand-in for 60fps MCP motion breakdowns |
| 5 | Studio Ubique GRYM | Free to view | Server-rendered | Streetwear PDP, size states, cart drawer |
| 6 | Webforging StreetWearzzz | Free to view | Server-rendered | View Transitions card to PDP, scroll orbit |
| 7 | pmndrs/examples shoe-configurator | MIT | Vite app | Canonical R3F product viewer |
| 8 | movin.design | MIT-0, free | Browser | Plain HTML/CSS/JS components, theme-compatible |
| 9 | synced-motion | MIT | Library | Reduced-motion contract, WordPress adapter |
| 10 | awwwards-3d | MIT | Skill + templates | Vanilla three+GSAP+Lenis templates |
| 11 | shopnest | No licence | Vite SPA | Cart drawer, wishlist, checkout (view only) |
| 12 | Nocturne Harbor | Price unstated | Next.js template | Dark apparel storefront structure |
| 13 | ui-elite-patterns | MIT | Local MCP | Motion configs for Framer/GSAP |
| 14 | usal | MIT | Library | 8 KB scroll reveals, vanilla |
| 15 | motionary | MIT | Next.js | 20 e-commerce motion variants (claims unverified) |

## Rejected
- **gsap-in-ecommerce:** an idea list of 20 projects, no code visible, no licence field.
- **fabric-3d-designer, 3D-Clothing-Configurator, lookbook:** no licence; lookbook also expects your own Mobbin screenshot exports.
- **design-inspiration-mcp-server, dia-mcp, kromamcp:** depend on third-party search or crawl API keys (Serper, Firecrawl/TinyFish, Google Images scraping), so not truly free access.
- **notsointresting/design-inspiration-mcp:** 28 tools that scrape gallery sites; platform terms unverified, 6 stars.
- **build56 viewer:** procedural headphones/watch/keyboard, not apparel.
- **Motion.page builder:** paid.
- **WICG scroll use-cases list:** links date from the 2016 era; not checked, low value.

## Key Takeaways
- Fashion-specific, free, openly licensed motion code is scarce; the realistic path is Motion plus the two MIT add-to-cart repos as references, not a fashion library to install.
- Check licences on the GitHub API, not the README: ecommerce-product-showcase claims MIT but reports none.
- Awwwards-mcp is the credible free substitute for the $29/month 60fps MCP, but it scrapes Awwwards and its terms were not reviewed.
- Anything labelled "500+" or "Awwwards-style" is marketing until a sample is opened.

## Sources
1. [GoodCart](https://www.goodcart.design/) — 1160+ ecommerce screenshots, 13 industries
2. [Studio Ubique GRYM](https://www.studioubique.com/work/streetwear-ecommerce-website-design/) — streetwear storefront concept
3. [Webforging StreetWearzzz](https://webforging.de/referenzen/streetwearzzz) — View Transitions streetwear shop
4. [Nocturne Harbor](https://nocturneui.com/templates/harbor) — dark apparel Next.js template
5. [ecommerce-product-showcase](https://github.com/KaranChandekar/ecommerce-product-showcase) — fly-to-cart, size pills
6. [add-item-to-cart-animation](https://github.com/EricTsai83/add-item-to-cart-animation) — 9 add-to-cart presets, MIT
7. [shopnest](https://github.com/sarfrazsaeed/shopnest) — sneakers store, unlicensed
8. [Awwwards-mcp](https://github.com/INSANE0777/Awwwards-mcp) — free MIT motion-DNA MCP
9. [ui-elite-patterns](https://github.com/maahigoel/ui-elite-patterns) — MIT pattern MCP
10. [design-dna-mcp](https://github.com/olartgabo/design-dna-mcp) — site-to-component library MCP
11. [pmndrs/examples shoe-configurator](https://github.com/pmndrs/examples/tree/main/demos/shoe-configurator/src) — R3F reference
12. [awwwards-3d](https://github.com/tsogjavklann/awwwards-3d) — three+GSAP+Lenis skill and templates
13. [synced-motion](https://github.com/SyncedCo/synced-motion) — accessible GSAP recipes
14. [movin.design](https://movin.design/components/) — 288 MIT-0 components
15. [motionary](https://github.com/aimkick/motionary) — motion variant library
16. [We.Inc ecommerce](https://we.inc/components/ecommerce) — free e-commerce components
17. [motion.dev](https://motion.dev/) — Motion licence and MCP statement
18. [usal](https://github.com/usaljs/usal) — scroll animation, 8 KB
19. [Motion.page](https://motion.page/) — paid builder, free SDK
20. [wix/interact](https://github.com/wix/interact/) — declarative interactions

## Methodology
Six semantic searches via Exa (one per gap), then GitHub API checks (licence, stars, last push, archived) on 20 repos and HTTP status checks on 11 sites on 2026-10-14. Search results returned page content, which was read from the tool output. The Webforging page is in German; the description above is my translation. **Not done:** no Chrome render, no opening of individual example pages, no licence-text review beyond the SPDX field, no Motion+ gating check on motion.dev. Single-source claims are marked in-line (Motionary 500+, GoodCart filter access, Nocturne price).
