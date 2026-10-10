# SkyyRose Full-Site Visual + Canon Audit — 2026-05-29

**Source:** `skyyrose-visual-sweep-audit` workflow (runId `wf_8fe74ba9-724`, taskId `wrwj2tlu5`)
**Method:** 12 parallel code-grounded auditors (read real source, cite `file:line`) + triage synthesizer. Read-only — mutated nothing.
**Scope:** 18 branded surfaces. **Excluded:** 4 immersive rooms + preorder-gateway (owned by uncommitted Phase 1 scene-intro work).
**Totals:** 116 findings — **7 critical, 30 high, 48 medium, 31 low**.

> **Verification status:** All 7 criticals + the `agency-tier-visuals.css` poison finding were re-verified against live source on 2026-05-29 — **7/7 true, zero false positives.** Auditors were code-grounded, not WebFetch (the 2026-05-23 false-positive failure mode does not apply). Items requiring founder DATA (edition sizes, fabric gsm, FAQ material claims) or NEW design assets (Kids lockup) are flagged and NOT auto-fixable.

---

## Scorecard (luxury-brand bar, not "it works")

| Surface | Grade | Crit | High | One-line verdict |
|---|---|---|---|---|
| Homepage (`front-page.php`) | **F** | 3 | 3 | Three canon violations on the first screen + `.rv` hides press/story/newsletter |
| Cross-cutting Design System | **F** | 0 | 4 | `agency-tier-visuals.css` globally poisons every page (white CTAs, hidden sections, motion conflict, CDN grain) |
| Landing Pages (×4) | **D** | 1 | 4 | "200 Pieces" contradicts catalog; press/review bars unstyled on 3/4; invented BR story + mixed-collection quote; FAQ aria dead |
| About | **D** | 1 | 4 | Invented pull-quote; live TODO; `about.css` bypasses tokens (49 hex); meta contrast fails AA; dead parallax selector |
| Global Chrome | **D** | 0 | 4 | Footer monogram = wrong asset (720px SKU master); search overlay no dialog role; no mobile-menu Esc; mascot alt embeds LH identity |
| Collection Pages (×4) | **D** | 1 | 1 | Kids type-rendered title (no lockup); per-collection accent defeated by hardcoded rose-gold; missing SR h1 on 3/4; newsletter AJAX dead |
| Shop Archive (holo cards) | **D** | 0 | 2 | Quick-add drawer hover-gated → invisible on touch (kills mobile conversion); wishlist broken (attr mismatch); size pills not keyboard-accessible |
| Search + 404 | **C** | 0 | 3 | 404 voice = mall-brand runway; mascot = chatbot boilerplate; inline hex bypasses token cascade |
| WooCommerce PDP | **C** | 0 | 2 | 6 dead JS blocks ship every PDP; gallery zoom wired to absent `#srZoom`; accent not on 3 states |
| Coming Soon + Contact | **C** | 0 | 2 | Contact CTA blood-red `#8B0000` (off-palette, gothic); FAQ Shopify boilerplate; glassmorphism conflicts with veil direction |
| Cart + Checkout | **C** | 1 | 0 | "Complete the Look" cross-sell live in cart (founder killed it); links clean; security solid |
| FAQ + Shipping | **C** | 0 | 1 | Cleanest surface; `info-pages.css` consumes ghost tokens that exist nowhere |

---

## Canon violations (non-negotiable — verified true)

1. **Homepage** `front-page.php:358` — collection names type-rendered (`<h3 class="col-card-name">`), must be lockup `<picture>` images. *(verified)*
2. **Homepage** `collections-config.php:53` — invented Black Rose tagline "For those who found power in the dark." Replace with verbatim `collection-stories.md:67`. *(verified — and ALL 4 poetic_taglines `:53,77,101,125` are suspect, canon-check each)*
3. **Homepage** `front-page.php:343` — "Three Worlds. One Vision." → four collections exist → "Four Collections. One Vision." *(verified)*
4. **Collection pages** `collection-content.php` — Kids Capsule type-rendered title; no Kids lockup asset exists. Interim: SR monogram; needs custom lockup (asset creation). *(verified — BR/LH/SIG have `hero_logo`, Kids does not)*
5. **Landing BR** `template-landing-black-rose.php:31,102,256` — "200 Pieces" invented; catalog = 250 (br-004/005/006) / 80 (br-010). **Needs founder messaging decision** (mixed sizes). *(verified)*
6. **About** `template-about.php:60` — invented pull-quote paraphrase + live TODO `:58`. Replace with verbatim Signature origin quote from `collection-stories.md`. *(verified)*
7. **Cart** `cart.php:404-414` — "Complete the Look" cross-sell live; founder killed it by name. Remove block; keep `skyyrose_get_cart_wears_with()` in `inc/woocommerce.php` for one-line revival. *(verified)*

Additional canon/voice (high): mascot alt embeds Love Hurts identity (`skyy-mascot.php`, global); 404 mall-brand voice; Love Hurts FAQ "actual family name" imprecise vs `corey-questions.md:66-70`; BR landing story title + blockquote mix Signature register.

---

## Recommended fix batches

**Batch 1 — criticals + S-effort (no design assets, mostly no founder data):**
- Canon copy: "Four Collections"; BR tagline → canon verbatim; About pull-quote + delete TODO; cart "Complete the Look" removal; BR landing story title + blockquote → BR register; LH FAQ family-name fix; mascot alt → generic.
- `agency-tier-visuals.css` poison: add bare `.rv` to `revealSelectors`; remove section `!important` padding; remove reveal-class redefs; remove CDN grain.
- Mobile commerce: `@media (hover:none)` reveal holo drawer; fix `data-wishlist-id`/`data-product-id` mismatch.
- A11y quick wins: landing FAQ `aria-expanded` toggle; search overlay `role="dialog"`+`aria-modal`; mobile-menu Esc handler; marquee reduced-motion selector (`.mq-track`→`.marquee-track`); collection-pages accent `var(--color-rose-gold)`→`var(--skyyrose-accent)`; missing SR `<h1>` on 3 collection pages.

**Batch 2 — M/L (some need design assets):**
- Homepage collection-card lockup images (assets exist in `hero-overlays/`); full `agency-tier-visuals.css` scoping; `about.css` token migration (49 hex) + rebuild `.min`; `info-pages.css` ghost-token fix; dead-JS pruning (`single-product.js` 6 blocks, `homepage-v7` + v7 IIFE); holo-card token migration.

**Needs founder input / assets (NOT auto-fixable):**
- C5 "200 Pieces" real number / messaging (catalog mixed 250/80).
- Kids Capsule custom hero lockup (design asset).
- Contact FAQ material/sizing/shipping claims (unverified vs catalog).
- BR landing fabric gsm (380 vs 280 contradiction, not catalog-grounded).

**Deferred from fix scope (separability):** version bump (`functions.php`/`style.css`) happens at deploy time, combined with uncommitted Phase 1 — keeps the visual-sweep fixes on files disjoint from the Phase 1 set.

---

*Full raw triage (all 116 ranked): workflow result `wf_8fe74ba9-724`.*

---

## Fix pass results (2026-05-29, run `wf_72e86188-d5f` + inline)

**Shape:** verify→harden→build→re-verify→report (NOT dev-team loop — per `feedback_workflow_verify_harden_pattern`). 23 agents, ran clean ~39min. Then 3 inline residual fixes.

- **72 fixes applied** across 10 clusters + 3 inline. **63 theme source files changed** (526 ins / 775 del) + all `.min` regenerated via `scripts/build-css.js` + `build-js.js`.
- **7 skipped** as non-reproducible (hypothesis-verify) — incl. the audit's own **rank-52 false positive** (search-CTA dark text already passes AA at 5.26:1; "fixing" to white would have failed it at 3.76:1).
- **4 deferred** (founder data): 200-Pieces edition count, fabric gsm, Kids lockup asset, Contact FAQ claims.

**Residual must-fixes — RESOLVED inline (all PHP, lint-clean):**
1. `404.php:208` mascot alt "wandered off" → `'Skyy, SkyyRose brand mascot.'`
2. `inc/collections-config.php:77` LH tagline → title case `'Wear Your Heart. Own Your Scars.'` (canon `collection-stories.md:130`)
3. `inc/builders/elementor-compat.php` `[skyyrose_press_bar]` shortcode rewritten from orphaned `lp-press__label`/`lp-press__list` DOM to styled `lp-press__row`/`lp-press__name` (lesson #2 orphan — 3rd press-bar emitter not in the cluster file set).

**Open — founder decisions (not code bugs):**
- `agency-tier-visuals.css` `.btn-primary` retains layout `!important` (pill shape: `border-radius:9999px`, `display:inline-flex`, custom padding) on `.hero-cta,.col-card-cta,.btn-primary,.holo__buy`. Bg/color override already removed. The pill may be **intended brand design** — left for eyeball; WC button sizing is the risk.
- LH landing story title `template-landing-love-hurts.php:65` "…the Bloodline That Raised Me." vs `collection-stories.md:99` "…a Family Name." — which is canon?
- `footer.php` copyright "The Skyy Rose Collection LLC" — registered entity name? (skipped, legal).
- `design-tokens.css` gained `--color-gold-rgb` + `--skyyrose-surface-warm` (Tokens phase — **intended, load-bearing for about.css**, NOT a forbidden violation despite 6 re-verifiers flagging it; my re-verify prompt didn't exempt the Tokens-phase file).

**State (final):** DEPLOYED LIVE to skyyrose.co at **v1.5.25** on 2026-05-29. Commits `cfc905726` (Phase-1 min) + `de495b11c` (sweep) + `cd8e277de` (Phase 2). Gate green (php -l + phpcs + WP health + wp-simplify + animation harness revealWorks=yes). Cache-busted verify confirmed: "Four Collections" live, "Three Worlds" gone, Lenis+immersive-core+data-warp live on /pre-order/. Founder ran the deploy via `!` (classifier blocks agent-side deploy until an `autoMode.allow` rule is added — see [[feedback_wp_autodeploy_after_sweep]]).
