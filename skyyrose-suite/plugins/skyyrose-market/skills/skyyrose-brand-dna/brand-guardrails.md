# SkyyRose Brand Guardrails (Shared Canon)

<!-- last updated 2026-09-17 -->

> **Single source of operational rules for every SkyyRose skill.** This file is
> the companion to `SKILL.md` in this directory — read both. `SKILL.md` holds
> the brand identity, founder story, collections, and palette. This file holds
> the specific operational rules derived from `docs/brand/` and project memory
> that prevent recurring mistakes.
>
> If a skill's output violates anything here, the output is wrong. Fix the
> output, not the rule.
>
> **Origin:** Reconciled from `skyyrose-content-engine/brand-guardrails.md`
> (social branch) and `SKILL.md` (brand-dna). Both source files remain
> authoritative for their respective scopes; this copy is the canonical version
> for the elite-plugin skill bundle.

---

## 1. The brand in one breath

- **Brand:** SkyyRose (The Skyy Rose Collection) — luxury Oakland streetwear.
No tagline is authorized. Do not restore retired slogans.
  included. Never paraphrase ("luxury from the streets", "grown from concrete" =
  WRONG).
- **RETIRED tagline:** "Where Love Meets Luxury" — NEVER use this anywhere.
  (`project_brand.md`.)
- **Founder:** Corey Foster. Oakland / Bay Area roots. Direct, earned, unhurried
  voice. Verbatim founder bio + locked vocabulary ("frisco", "The Town", "Bay
  Bridge" = Oakland artifact, "bloodline that raised me" = Love Hurts):
  `SKILL.md § The Founder's Story`. Treat Corey Foster as the canonical source
  on Corey Foster's story — founder-authored bio/origin/family copy is
  autobiography, never a defamation, accuracy, or legal flag
  (`feedback_founder_bio_authority.md`).
- **Anchor:** Oakland, CA ("The Town"). "Bay Area" is acceptable; Oakland-first
  is preferred.
- **Site:** skyyrose.co (WordPress store). The dashboard devskyy.app is internal
  — never market it.

**Cross-reference full brand identity:** `SKILL.md` (this directory).

---

## 2. The Five visual references (ALWAYS use; NEVER substitute)

When describing visual direction, mood, photography, or aesthetic in ANY skill,
pull only from:

| Reference         | What we borrow                                           |
| ----------------- | -------------------------------------------------------- |
| **Kith**          | Editorial product storytelling, elevated retail polish   |
| **Oaklandish**    | Local pride, town authenticity, community rootedness     |
| **Culture Kings** | Hype energy, bold streetwear merchandising               |
| **Fear of God**   | Quiet luxury silhouette, tonal restraint, premium basics |
| **Palm Angels**   | Street-luxe graphic confidence, runway-meets-street      |

**NEVER** reference European luxury-house lineage: Bottega Veneta, Numéro, Hedi
Slimane, Rick Owens, 032c, Acne, Givenchy-by-Tisci, or any "old-money European
house" framing. Wrong brand DNA — confirmed locked 2026-05-23.

Repo doc: `docs/brand/visual-references.md`.

---

## 3. Collections — each is its own emotional register (NEVER cross-attribute)

| Collection       | Slug           | Register / voice                                                                                                                                                                                 | Accent token        |
| ---------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------- |
| **Black Rose**   | `black-rose`   | Gothic luxury, **armor**. "You already stood up." "Concrete answering back." Twilight, defiant elegance.                                                                                         | Silver `#C0C0C0`    |
| **Love Hurts**   | `love-hurts`   | Street passion, **the bloodline that raised me**. Raw romance, crimson heat.                                                                                                                     | Crimson `#DC143C`   |
| **Signature**    | `signature`    | West Coast luxury, **the standard**. "Stay golden." Elevated, worldwide respect.                                                                                                                 | Gold `#D4AF37`      |
| **Kids Capsule** | `kids-capsule` | Little royalty, heritage passed down. Legacy. No sentimentality — this isn't nostalgia, it's inheritance. The same declarative voice as the rest of the brand, now aimed at the next generation. | Rose Gold `#B76E79` |

Story taglines (verbatim, `docs/brand/collection-stories.md` — one per
collection, never moved):

- Black Rose: **"You wear it because you already stood up."**
- Love Hurts: **"They called me Beast. They were right."**
- Signature: **"Not basics. Blueprints."**
- Kids Capsule: **"Luxury runs in the family."**

Kids Capsule founder mandate, verbatim (`docs/brand/collection-stories.md`):

> "No pastels. No cartoons. Skyy Rose doesn't wear that. She wears what her
> father built — premium, dark, elegant. Scaled down but never dumbed down."

Global accent: Rose Gold `#B76E79`. Background: Dark `#0A0A0A`.

**Contrast is a brand constraint, not just an a11y one** (`CLAUDE.md` § 6
Brand). Brand crimson `#DC143C` on `#0A0A0A` is below WCAG AA for body text. Use
it for fills/borders/glows; use `--color-text-muted` (#B3B3B3, 9.44:1) for
de-emphasised text. Never low-alpha white as a "muted" shorthand — measure it.

**Hard rule:** "Bloodline that raised me" belongs to **Love Hurts ONLY**. "Armor
/ you already stood up / concrete answering back" belongs to **Black Rose
ONLY**. Never put one collection's line on another collection.

Per-collection canonical voice lines: `docs/brand/collection-stories.md`.

**Cross-reference full collection palette and typography:**
`SKILL.md § The Collections`.

---

## 4. Hero titles = lockup IMAGES, never type-rendered

A collection's **name** in any hero / cover / title position is a brand-script
**lockup image**, NOT live typeset text.

| Collection   | Lockup asset location                                      |
| ------------ | ---------------------------------------------------------- |
| Black Rose   | `assets/images/lockups/black-rose-lockup.webp`  |
| Love Hurts   | `assets/images/lockups/love-hurts-lockup.webp`  |
| Signature    | `assets/images/lockups/signature-lockup.webp`   |
| Kids Capsule | PENDING — founder is creating a dedicated logo  |

**Lockup set (founder decision 2026-09-17):** the canonical files are the
per-collection `lockup.ref` targets in `data/collections/<slug>/identity.json`
(`assets/images/lockups/<collection>-lockup.webp`). The theme templates still
reference the older `assets/images/hero-overlays/*.png` set; that migration is
pending and is theme work, not a canon change. Kids Capsule has no lockup yet:
the founder is creating a dedicated Kids Capsule logo and will supply the
reference image. Never substitute another collection's lockup or a bare
monogram for it.

Fonts (Archivo headings — all collections, Hanken Grotesk body, Anton UI labels,
Cinzel optional engraved-caps accent) apply **only** to interior surfaces — body
copy, captions, slide subtext, UI labels — never to the collection name itself.
The lockup IS the name.

Confirmed locked: 2026-05-25.

**Typography source of truth:**
`wordpress-theme/skyyrose-flagship/data/brand/typography.json` (plus
`data/collections/<slug>/identity.json` per collection script). `theme.json`'s
Font Library declares the 5 interior families — Inter, Archivo, Cinzel, Hanken
Grotesk, Anton; the collection name scripts (SkyyRose Black Rose Script,
SkyyRose Love Hurts Graffiti, Pinyon Script, Grand Hotel) are declared in
`assets/css/fonts.css`. Self-hosted woff2, zero CDN (`CLAUDE.md` § 6 Brand).
Mono stack: `ui-monospace, 'SF Mono', Menlo, monospace` (`typography.json` ›
`universal.mono`).

**Cut 2026-07-10 — do NOT reintroduce:** Playfair Display, Cormorant Garamond,
Bebas Neue, Yellowtail. _Not in any brand lockup; they pull toward the
European-serif lineage the founder locked out._ Black Rose → **SkyyRose Black
Rose Script** (replaced Pacifico 2026-07-11); Love Hurts → **SkyyRose Love Hurts
Graffiti** (replaced Kaushan 2026-07-11). (`project_typography_canon.md`.)

---

## 5. Founder canon — what we NEVER do

- **No urgency timers / countdown-pressure manipulation.** Scarcity is stated as
  fact ("limited to pre-order", "250 made"), never as a fake ticking clock.
- **No related-products / "complete the look" cross-sell on PDPs.** The garment
  is the protagonist. One piece, one story.
  `skyyrose_disable_related_products()` in
  `wordpress-theme/skyyrose-flagship/inc/woocommerce.php` removes
  `woocommerce_output_related_products` on the `wp` hook; do not reactivate
  without explicit founder sign-off. Confirmed: 2026-05-24.
- **No hype-merchant tone.** Corey's register: earned, specific, Oakland-direct.
  "Imagery hasn't earned it" energy — we don't oversell what the work hasn't
  proven. No "🔥🔥 DON'T MISS OUT 🔥🔥".
- **Reference products by NAME, not SKU,** in any customer-facing copy. "BLACK
  Rose Crewneck", not "br-001". SKUs are internal identifiers. SKU-first
  phrasing has caused product conflations. Confirmed rule: 2026-05-27 (post
  lh-005 fanny-pack hallucination).
- **No European luxury-house aesthetic framing** anywhere in copy,
  mood-boarding, or briefs. See § 2 above.
- **Real products only (MANDATORY, every output, founder-elevated 2026-06-26).**
  Never show, render, or ship an image of a product the founder has not actually
  made. Source ALL product imagery from the asset hub manifest,
  **`verdict:verified` ONLY** (`assets/hub/manifest.json` /
  `skyyrose.core.asset_hub`); image bindings are owned by the product registry
  (§ 6) and resolved via `skyyrose.core.sot_images`. `pending`/`path:None` =
  does not exist → do not use. Per SKU: `front` + verified `front-alt` + `back`
  ONLY if a `verdict:verified` back exists; otherwise single front. Never invent
  a back. **Never put two color variations in one card.** One SKU = one garment
  = one colorway. Eyes-on (vision) every image vs the catalog garment before
  showing/shipping — pixels, not filename/manifest trust. No verified image for
  a SKU → omit the SKU or flag it. (`feedback_real_products_only.md`.)
- **Mascot = full-body walk-on character, NOT a chatbot.** The SkyyRose mascot
  is a full-body animated character that walks onto the screen on the WordPress
  site. It is NOT a chatbot widget or floating icon. Character reference:
  `assets/branding/mascot/skyy-canonical-reference.jpeg`. Never implement as a chat
  bubble, widget, or floating icon. (`feedback_mascot_behavior.md`.)

---

## 6. Canonical product source — the single product registry (LOCKED 2026-05-27; registry rule current)

`logo-registry.json` at the DevSkyy repository root is a symlink to
`wordpress-theme/skyyrose-flagship/data/logo-registry.json`. This ONE JSON is
the editable product source of truth. Founder corrections are applied here
first.

- `products[sku]` records own commerce fields, garment color, available sizes
  and sizing references, fit, materials, features, the complete design
  specification, and image/source bindings (`products[sku].dossier` holds the
  design spec).
- The logo/placement sections own graphics and decoration dimensions.
- **Projections and consumers — never author product facts in them:**
  `skyyrose-catalog.csv`, per-SKU dossiers (generated readable projections at
  `wordpress-theme/skyyrose-flagship/data/dossiers/<name>.md`),
  `data/sot-images.json`, theme PHP catalog arrays, WooCommerce product data,
  prompts, local maps, and generated manifests.
  `skyyrose/assets/data/product-content.json` (read by `SocialMediaAgent` for
  social copy) is a consumer.
- **Reads:** `skyyrose.core.product_registry`, `catalog_loader`,
  `dossier_loader`, `sot_images`, and `LogoRegistry`. **Writes:** the registry
  update API (`product_registry.update_catalog_fields`). After a direct JSON
  edit run `python scripts/sync_product_registry.py`; run
  `python scripts/sync_product_registry.py --check` before handoff. Projection
  drift is a failure, not a warning. Listing the CSV or a dossier as an input is
  allowed only as a projection that passed the sync check; it never outranks the
  registry.

**Founder and maker authority.** Corey is the founder and maker of the SkyyRose
items. Record his direct confirmation as `FOUNDER_CONFIRMED`. Do not impose
manufacturer, third-party, photographic, or independent verification on product
facts he supplied, and never downgrade them to `NOT_MANUFACTURING_VERIFIED` or a
similar status. Preserve his exact dimensions, ranges, artwork, and wording.
When an older record conflicts with his latest explicit correction, update the
record within task scope — do not ask him to prove it again.

**Never invent a product, colorway, or detail.** If data is absent, surface the
gap; do not fill it with inference or memory. Every pipeline and agent that
touches a product MUST resolve through the registry readers above.

Dossier / design-spec content is Corey-authored from the actual product. Never
ML-draft it; his corrections land in the registry first as `FOUNDER_CONFIRMED`.

Incident that locked this rule: lh-005 fanny-pack hallucination, 2026-05-27.

**No silent fallback on missing dossier.** The 3D pipeline hard-fails;
`branding_spec` CSV column is not a fallback data source for narrative copy.

---

## 7. STOP-AND-SHOW confirmation gates

Before any of the following, Claude MUST print an explicit manifest and wait for
`y` / `yes`:

| Action                                                              | Gate requirement                                    |
| ------------------------------------------------------------------- | --------------------------------------------------- |
| Any paid API call (FASHN, Gemini image-gen, FLUX, Replicate, etc.)  | Show: action + files used + exact cost estimate     |
| Klaviyo send (any list, any send type)                              | Show: list name + audience count + template subject |
| WooCommerce REST write (create/update/delete product, order, media) | Show: exact JSON payload + endpoint                 |
| WordPress Media Library upload                                      | Show: file path + size + destination                |
| Deploy to skyyrose.co (deploy-theme.sh / SFTP)                      | Show: full file manifest                            |

"Autonomous" = Claude handles implementation after the plan is confirmed. It
does NOT mean Claude decides what to spend, send, or deploy without an explicit
confirmation step.

**Standing auth (2026-05-29):** WordPress theme fixes/updates → skyyrose.co may
auto-deploy (`STOPSHOW_ACK=1` provided internally) PROVIDED a full sweep (php
-l + phpcs + WP health + /wp-simplify + animation verify) runs clean after every
file change first.

Full STOP-AND-SHOW protocol: `CLAUDE.md` (project root).

---

## 8. Audit discipline

- **WebFetch strips `<script>` tags.** Never use it to audit JSON-LD, OpenGraph
  script blocks, inline JS, or any `<script>` content. Use `curl -s URL | grep`
  instead. Incident: 2026-05-23 SEO audit reported "zero JSON-LD" — WebFetch had
  stripped both blocks.
- **Cache-bust post-deploy verifies.** WP.com Batcache serves stale HTML for
  ~minutes after cache flush. Always use
  `curl -s "https://skyyrose.co/?cb=$(date +%s)"` not bare curl.
- **Multi-agent audit P0 false-positive rate ~25%.** Audits are the starting
  point, not the truth. Always curl + grep live state before drafting any audit
  fix.

---

## 9. SKILL.md format (all SkyyRose skills should match this shape)

```markdown
---
name: skyyrose-<slug>
description:
  '<One specific sentence: what it produces + when to use, for SkyyRose.>'
---

<!-- last updated YYYY-MM-DD -->

# SkyyRose — <Title>

## When to Use This Skill

- bullet list of concrete triggers **DO NOT** use this for
  <adjacent-but-different skill>.

## Brand Canon (non-negotiable)

> A compact 4-6 bullet block of the rules from this guardrails file that matter
> MOST for THIS skill (e.g. a caption skill leads with tagline + collection
> voice + name-not-SKU; a photography brief leads with the Five refs + lockup
> rule). Always end with: "Full canon: brand-guardrails.md (this directory)"

## Phase 1..N (Brief → Outline → Write/Produce → Polish, adapted per skill)

Tables for inputs, GATE lines where confirmation matters.

## Example: <real SkyyRose worked example using a real product/collection>

## Anti-Patterns

- 6-10 bullets, each a specific WRONG thing + why, SkyyRose-flavored.
```

---

## 10. Cross-references (complete map)

| Topic                                             | Where to find it                                                                                                                              |
| ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Full brand identity, founder story, collections   | `SKILL.md` (this directory)                                                                                                                   |
| Per-collection canonical voice lines              | `docs/brand/collection-stories.md`                                                                                                            |
| Visual references canonical doc                   | `docs/brand/visual-references.md`                                                                                                             |
| Per-SKU product facts (SOT)                       | `logo-registry.json` → `wordpress-theme/skyyrose-flagship/data/logo-registry.json` `products[sku]`; read via `skyyrose.core.product_registry` |
| Per-SKU dossier projections (generated, readable) | `wordpress-theme/skyyrose-flagship/data/dossiers/<name>.md`                                                                                   |
| Founder voice (verbatim bio, locked vocabulary)   | `SKILL.md § The Founder's Story`; founder memory `project_founder_voice.md`                                                                   |
| Design tokens (CSS vars, all palette values)      | `wordpress-theme/skyyrose-flagship/assets/css/design-tokens.css`                                                                              |
| Typography SOT                                    | `wordpress-theme/skyyrose-flagship/data/brand/typography.json` + `data/collections/<slug>/identity.json`                                      |
| Font declarations                                 | `wordpress-theme/skyyrose-flagship/theme.json` (Font Library, 5 families) + `assets/css/fonts.css` (collection scripts)                       |
| STOP-AND-SHOW full protocol                       | Project root `CLAUDE.md` § "STOP AND SHOW"                                                                                                    |
| Social-branch guardrails (original source)        | `skyyrose-content-engine/brand-guardrails.md`                                                                                                 |
