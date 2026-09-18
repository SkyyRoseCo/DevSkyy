# SkyyRose Brand Guardrails (Shared Canon)

<!-- last updated 2026-06-05 -->

> **Single source of operational rules for every SkyyRose skill.**
> This file is the companion to `SKILL.md` in this directory — read both.
> `SKILL.md` holds the brand identity, founder story, collections, and palette.
> This file holds the specific operational rules derived from `docs/brand/` and
> project memory that prevent recurring mistakes.
>
> If a skill's output violates anything here, the output is wrong.
> Fix the output, not the rule.
>
> **Origin:** Reconciled from `skyyrose-content-engine/brand-guardrails.md` (social branch)
> and `SKILL.md` (brand-dna). Both source files remain authoritative for their
> respective scopes; this copy is the canonical version for the elite-plugin skill bundle.

---

## 1. The brand in one breath

- **Brand:** SkyyRose (The Skyy Rose Collection) — luxury Oakland streetwear.
- **Tagline (verbatim, the ONLY tagline):** `Luxury Grows from Concrete.`
  Period included. Never paraphrase ("luxury from the streets", "grown from concrete" = WRONG).
- **Founder:** Corey Foster. Oakland / Bay Area roots. Direct, earned, unhurried voice.
- **Anchor:** Oakland, CA ("The Town"). "Bay Area" is acceptable; Oakland-first is preferred.
- **Site:** skyyrose.co (WordPress store). The dashboard devskyy.app is internal — never market it.

**Cross-reference full brand identity:** `SKILL.md` (this directory).

---

## 2. The Five visual references (ALWAYS use; NEVER substitute)

When describing visual direction, mood, photography, or aesthetic in ANY skill, pull only from:

| Reference | What we borrow |
|-----------|----------------|
| **Kith** | Editorial product storytelling, elevated retail polish |
| **Oaklandish** | Local pride, town authenticity, community rootedness |
| **Culture Kings** | Hype energy, bold streetwear merchandising |
| **Fear of God** | Quiet luxury silhouette, tonal restraint, premium basics |
| **Palm Angels** | Street-luxe graphic confidence, runway-meets-street |

**NEVER** reference European luxury-house lineage: Bottega Veneta, Numéro, Hedi Slimane,
Rick Owens, 032c, Acne, Givenchy-by-Tisci, or any "old-money European house" framing.
Wrong brand DNA — confirmed locked 2026-05-23.

Repo doc: `docs/brand/visual-references.md`.

---

## 3. Collections — each is its own emotional register (NEVER cross-attribute)

| Collection | Slug | Register / voice | Accent token |
|------------|------|------------------|--------------|
| **Black Rose** | `black-rose` | Gothic luxury, **armor**. "You already stood up." "Concrete answering back." Twilight, defiant elegance. | Silver `#C0C0C0` |
| **Love Hurts** | `love-hurts` | Street passion, **the bloodline that raised me**. Raw romance, crimson heat. | Crimson `#DC143C` |
| **Signature** | `signature` | West Coast luxury, **the standard**. "Stay golden." Elevated, worldwide respect. | Gold `#D4AF37` |
| **Kids Capsule** | `kids-capsule` | Little royalty, heritage passed down. Playful but premium. | Rose Gold `#B76E79` |

Global accent: Rose Gold `#B76E79`. Background: Dark `#0A0A0A`.

**Hard rule:** "Bloodline that raised me" belongs to **Love Hurts ONLY**.
"Armor / you already stood up / concrete answering back" belongs to **Black Rose ONLY**.
Never put one collection's line on another collection.

Per-collection canonical voice lines: `docs/brand/collection-stories.md`.

**Cross-reference full collection palette and typography:** `SKILL.md § The Collections`.

---

## 4. Hero titles = lockup IMAGES, never type-rendered

A collection's **name** in any hero / cover / title position is a brand-script **lockup image**,
NOT live typeset text.

| Collection | Lockup asset location |
|------------|----------------------|
| Black Rose | `assets/images/hero-overlays/br-brand-script.png` |
| Love Hurts | `assets/images/hero-overlays/lh-logo-combined.png` |
| Signature | `assets/images/hero-overlays/sig-brand-skyy-rose-gold.png` |
| Kids Capsule | `assets/images/logos/` (Kids Capsule lockup) |

Fonts (Archivo headings — all collections, Hanken Grotesk body, Anton UI labels,
Cinzel optional engraved-caps accent) apply **only** to interior surfaces — body copy, captions, slide subtext,
UI labels — never to the collection name itself. The lockup IS the name.

Confirmed locked: 2026-05-25.

---

## 5. Founder canon — what we NEVER do

- **No urgency timers / countdown-pressure manipulation.** Scarcity is stated as fact
  ("limited to pre-order", "250 made"), never as a fake ticking clock.
- **No related-products / "complete the look" cross-sell on PDPs.** The garment is the protagonist.
  One piece, one story. `woocommerce.php:541` hook is commented out; do not reactivate
  without explicit founder sign-off. Confirmed: 2026-05-24.
- **No hype-merchant tone.** Corey's register: earned, specific, Oakland-direct. "Imagery hasn't
  earned it" energy — we don't oversell what the work hasn't proven. No "🔥🔥 DON'T MISS OUT 🔥🔥".
- **Reference products by NAME, not SKU,** in any customer-facing copy. "BLACK Rose Crewneck",
  not "br-001". SKUs are internal identifiers. SKU-first phrasing has caused product conflations.
  Confirmed rule: 2026-05-27 (post lh-005 fanny-pack hallucination).
- **No European luxury-house aesthetic framing** anywhere in copy, mood-boarding, or briefs.
  See § 2 above.

---

## 6. Canonical product source (LOCKED 2026-05-27)

Product facts — name, collection, price, description, colorway — resolve through:

1. **Catalog CSV:** `wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv` (33 SKUs)
2. **Per-SKU dossiers:** `skyyrose/elite_studio/assets/` per-product directories
3. **Live agent (for social copy):** `SocialMediaAgent` → the product registry via `skyyrose.core.product.get_product(sku)`

**Never invent a product, colorway, or detail.** If data is absent, surface the gap; do not fill
it with inference or memory. Every pipeline and agent that touches a product MUST resolve through
the catalog CSV + per-SKU dossier. Every other product-reference store is deletable garbage.

Dossiers are Corey-authored from the actual product. Do not ML-draft dossier content without
founder review.

Incident that locked this rule: lh-005 fanny-pack hallucination, 2026-05-27.

**No silent fallback on missing dossier.** The 3D pipeline hard-fails; `branding_spec` CSV
column is not a fallback data source for narrative copy.

---

## 7. STOP-AND-SHOW confirmation gates

Before any of the following, Claude MUST print an explicit manifest and wait for `y` / `yes`:

| Action | Gate requirement |
|--------|-----------------|
| Any paid API call (FASHN, Gemini image-gen, FLUX, Replicate, etc.) | Show: action + files used + exact cost estimate |
| Klaviyo send (any list, any send type) | Show: list name + audience count + template subject |
| WooCommerce REST write (create/update/delete product, order, media) | Show: exact JSON payload + endpoint |
| WordPress Media Library upload | Show: file path + size + destination |
| Deploy to skyyrose.co (deploy-theme.sh / SFTP) | Show: full file manifest |

"Autonomous" = Claude handles implementation after the plan is confirmed. It does NOT mean
Claude decides what to spend, send, or deploy without an explicit confirmation step.

**Standing auth (2026-05-29):** WordPress theme fixes/updates → skyyrose.co may auto-deploy
(`STOPSHOW_ACK=1` provided internally) PROVIDED a full sweep (php -l + phpcs + WP health +
/wp-simplify + animation verify) runs clean after every file change first.

Full STOP-AND-SHOW protocol: `CLAUDE.md` (project root).

---

## 8. Audit discipline

- **WebFetch strips `<script>` tags.** Never use it to audit JSON-LD, OpenGraph script blocks,
  inline JS, or any `<script>` content. Use `curl -s URL | grep` instead.
  Incident: 2026-05-23 SEO audit reported "zero JSON-LD" — WebFetch had stripped both blocks.
- **Cache-bust post-deploy verifies.** WP.com Batcache serves stale HTML for ~minutes after
  cache flush. Always use `curl -s "https://skyyrose.co/?cb=$(date +%s)"` not bare curl.
- **Multi-agent audit P0 false-positive rate ~25%.** Audits are the starting point, not the truth.
  Always curl + grep live state before drafting any audit fix.

---

## 9. SKILL.md format (all SkyyRose skills should match this shape)

```markdown
---
name: skyyrose-<slug>
description: "<One specific sentence: what it produces + when to use, for SkyyRose.>"
---

<!-- last updated YYYY-MM-DD -->

# SkyyRose — <Title>

## When to Use This Skill
- bullet list of concrete triggers
**DO NOT** use this for <adjacent-but-different skill>.

## Brand Canon (non-negotiable)
> A compact 4-6 bullet block of the rules from this guardrails file that matter
> MOST for THIS skill (e.g. a caption skill leads with tagline + collection voice +
> name-not-SKU; a photography brief leads with the Five refs + lockup rule).
> Always end with: "Full canon: brand-guardrails.md (this directory)"

## Phase 1..N  (Brief → Outline → Write/Produce → Polish, adapted per skill)
Tables for inputs, GATE lines where confirmation matters.

## Example: <real SkyyRose worked example using a real product/collection>

## Anti-Patterns
- 6-10 bullets, each a specific WRONG thing + why, SkyyRose-flavored.
```

---

## 10. Cross-references (complete map)

| Topic | Where to find it |
|-------|-----------------|
| Full brand identity, founder story, collections | `SKILL.md` (this directory) |
| Per-collection canonical voice lines | `docs/brand/collection-stories.md` |
| Visual references canonical doc | `docs/brand/visual-references.md` |
| Per-SKU product catalog | `wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv` |
| Per-SKU dossiers | `skyyrose/elite_studio/assets/<sku>/` |
| Design tokens (CSS vars, all palette values) | `wordpress-theme/skyyrose-flagship/assets/css/design-tokens.css` |
| Font declarations | `wordpress-theme/skyyrose-flagship/theme.json` |
| STOP-AND-SHOW full protocol | Project root `CLAUDE.md` § "STOP AND SHOW" |
| Social-branch guardrails (original source) | `skyyrose-content-engine/brand-guardrails.md` |
