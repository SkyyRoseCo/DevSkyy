---
name: skyyrose-brand-dna
description: Brand identity guide for SkyyRose luxury streetwear. Use when creating content, designs, marketing materials, product descriptions, or any creative work for SkyyRose. Triggers on references to SkyyRose, the collections (Black Rose, Love Hurts, Signature, Kids Capsule), Oakland streetwear, luxury fashion content, or requests for brand-aligned outputs. Essential for maintaining brand consistency across all touchpoints.
---

<!-- last updated 2026-06-05 -->

# SkyyRose Brand DNA

> **Canon foundation.** Every other SkyyRose skill inherits from this document.
> Operational guardrails (visual references, lockup-image rule, SKU-vs-name rule,
> confirmed anti-patterns) live in the companion file **`brand-guardrails.md`** in
> this same directory. Read both when authoring or auditing any SkyyRose output.
> If a rule in another skill conflicts with this file or `brand-guardrails.md`,
> the conflict traces here — fix the downstream skill.

The Skyy Rose Collection is a luxury streetwear brand based in Oakland/San Leandro, California. Website: https://skyyrose.co

---

## The Founder's Story

**Corey Foster** — CEO/Owner, single father, entrepreneur

The Skyy Rose Collection was born out of a deeply personal experience — Corey's resolve to provide a better life for his daughter, **Skyy Rose**, after whom the brand is named. As a single father raising a child in one of Oakland's crime-ridden neighborhoods, Corey was determined not to become another statistic.

> "If you asked me four years ago, I never would have thought I'd be here. I had no drive, lost it all, a baby on the way, and was broke. But we knew we had to get it by any means necessary."

**The Journey:**
- Dealt with doubts, losing loved ones, feeling like he had nothing left to give
- Navigated multiple failed website attempts
- Overcame deceitful manufacturers who promised much but delivered little
- Balanced single parenthood with entrepreneurship on minimal to no support
- Maintained integrity, steering clear from paths that lead many astray in his community

**Philosophy:** *"Believe in your vision even when others can't see it."*

**Recognition:**
- Maxim's "14 Game-Changing Entrepreneurs To Watch In 2023"
- Featured entrepreneur on The Blox
- Best of Best Review: Best Bay Area Clothing Line Award 2024
- Featured in San Francisco Post, CEO Weekly

---

## Brand Essence

**Positioning:** Where Bay Area authenticity meets high-fashion aesthetics

**What Makes SkyyRose Different:**
- **Pioneer in gender-neutral fashion** — One of the first Bay Area brands to embrace clothing designed for anyone, regardless of gender or age
- **Born from struggle** — Not a marketing story, but a real journey from rock bottom
- **Family at the core** — Named after a daughter, built to provide for family
- **Oakland authenticity** — Reflects the unique cultural landscape of The Town
- **Black-owned** — Represents hope and possibility for the community

**Brand Aesthetic:**
- Blend of modern elegance and urban flair
- From sleek, minimalist designs to bold, statement-making pieces
- Meticulous attention to detail
- Quality and durability, not fast fashion
- Versatile, stylish, accessible to all

---

## The Collections

Each collection is its **own emotional register**. Never cross-attribute voices, quotes, or visual language across collections. For the full canonical line library per collection, read `docs/brand/collection-stories.md`.

### Black Rose Collection
**Slug:** `black-rose`
**Identity:** Gothic luxury, armor, defiant elegance

- Register: "You already stood up." "Concrete answering back." Twilight, noir, defiance.
- Colors: Deep blacks, midnight tones, Silver `#C0C0C0` accent
- Pieces: Statement items, collector editions
- Mood: Elevated darkness, refined edge
- Display font: Archivo — for interior surfaces only (see lockup rule below); Cinzel available as optional engraved-caps accent; collection NAME identity = SkyyRose Black Rose Script lockup image, never live type
- Hero lockup asset: `assets/images/hero-overlays/br-brand-script.png` (embossed script logotype)
- Patches: NFL, NBA, MLB, Hockey (sport-specific per jersey)
- **Reserved voice:** "armor / you already stood up / concrete answering back" = Black Rose ONLY

### Love Hurts Collection
**Slug:** `love-hurts`
**Identity:** Street passion, bloodline, raw romance

- **"Hurts" is the founder's family name** — this collection is deeply personal
- Register: Raw emotion, vulnerability as strength, crimson heat, "the bloodline that raised me"
- Colors: Crimson `#DC143C`, deep blacks, emotional contrasts
- Pieces: Expressive graphics, meaningful typography
- Mood: Authentic pain transformed into beauty
- Display font: Archivo — for interior surfaces only; collection NAME identity = SkyyRose Love Hurts Graffiti lockup image, never live type
- Hero lockup asset: `assets/images/hero-overlays/lh-logo-combined.png` (red graffiti drip "Love" + "Hurts")
- **Reserved voice:** "bloodline that raised me" = Love Hurts ONLY

### Signature Collection
**Slug:** `signature`
**Identity:** West Coast luxury, the standard, everyday elevation

- Register: "Stay golden." Understated confidence, worldwide respect, elevated basics.
- Colors: Gold `#D4AF37` accent, neutral palette, timeless tones
- Pieces: Wardrobe staples, quality basics (tees, hoodies, joggers)
- Mood: Understated confidence, daily elevation
- Display font: Archivo — for interior surfaces only; collection NAME identity = Pinyon Script lockup image, never live type
- Hero lockup asset: `assets/images/hero-overlays/sig-brand-skyy-rose-gold.png` (gold calligraphy with rose)

### Kids Capsule Collection
**Slug:** `kids-capsule`
**Identity:** Little royalty, heritage passed down

- Launched March 2023 to celebrate Skyy Rose's birthday — extending the brand to the next generation
- Register: Playful but premium. Heritage, not hype.
- Accent: Rose Gold `#B76E79`
- Mood: Joyful luxury, parent-child bonds
- Hero lockup asset: `assets/images/logos/` (Kids Capsule lockup)
- **Launch-mode default:** Shows 0 grid cards by design (`skyyrose_kc_mode` customizer toggle = `'launch'`). Founder flips to `'live'` to open the shop. This is NOT a bug.

---

## Hero Titles — Lockup Images, Never Type-Rendered

> **Cross-reference:** `brand-guardrails.md § 4` has the full lockup rule with asset paths.

A collection's **name** in any hero / cover / title position is a brand-script **lockup image**, not live typeset text. Fonts (Archivo, Hanken Grotesk, Anton, Cinzel) apply only to interior surfaces — body copy, captions, slide subtext, UI labels — **never** to the collection name itself. The lockup IS the name.

| Collection | Lockup asset location |
|------------|----------------------|
| Black Rose | `assets/images/hero-overlays/br-brand-script.png` |
| Love Hurts | `assets/images/hero-overlays/lh-logo-combined.png` |
| Signature | `assets/images/hero-overlays/sig-brand-skyy-rose-gold.png` |
| Kids Capsule | `assets/images/logos/` (Kids Capsule lockup) |

---

## Visual Identity

**Color Palette:**

| Token | Hex | Usage |
|-------|-----|-------|
| Dark (background) | `#0A0A0A` | Global page background |
| Pure white | `#FFFFFF` | Text on dark, structural contrast |
| Rose Gold (global accent) | `#B76E79` | Global accent, Kids Capsule collection accent |
| Gold (Signature) | `#D4AF37` | Signature Collection accent |
| Crimson (Love Hurts) | `#DC143C` | Love Hurts Collection accent |
| Silver (Black Rose) | `#C0C0C0` | Black Rose Collection accent |
| Blood red | `#8B0000` | Supporting dark red for graphic elements |
| Charcoal | `#1C1C1C` | Secondary surface, card backgrounds |
| Smoke | `#2D2D2D` | Tertiary surface, elevated panel backgrounds |

**Typography System:**

| Role | Font | Notes |
|------|------|-------|
| Display / hero / headings (interior, ALL collections) | Archivo | Display sans, expanded width — NEVER for collection name lockup |
| Editorial body | Hanken Grotesk | Long-form copy, product narrative |
| UI / system | Inter | System fallback — interface, navigation, system text |
| Prices / technical data | Space Mono | Numbers, SKU-adjacent UI |
| Buttons / labels | Anton | CTA text, tag labels, caps, drop accent |
| Engraved-caps accent (optional) | Cinzel | Generic engraved-caps accent — NEVER for collection name lockup |
| Collection NAME (hero / cover / title) | Lockup image only — SkyyRose Black Rose Script (BR), SkyyRose Love Hurts Graffiti (LH), Pinyon Script (SIG), Grand Hotel (KC) | Never live type |

All 9 font families are declared in `theme.json` via WordPress Font Library. Zero external CDN (Google Fonts removed).

**Photography Direction:**

> **Cross-reference:** `brand-guardrails.md § 2` — The Five visual references govern all visual direction. Pull from Kith, Oaklandish, Culture Kings, Fear of God, Palm Angels. NEVER European luxury-house lineage.

- Lighting: Dramatic, directional, cinematic
- Settings: Urban Oakland, industrial spaces, elevated environments
- Models: Confident, diverse, authentic, inclusive of all genders
- Styling: Intentional, layered, statement-making

---

## Voice & Tone

**Brand Voice Characteristics:**
- Confident without arrogance
- Rooted in fatherhood and family
- Oakland-authentic, globally aware
- Emotionally intelligent
- Never corporate or generic

**Writing Guidelines:**
- Lead with emotion, follow with features
- Reference the origin story when appropriate
- Short, impactful sentences
- Emphasize quality, craftsmanship, sustainability
- Say "The Town" when Oakland-specific; "Bay Area" is acceptable but Oakland-first is preferred
- Avoid: "premium," "exclusive" as standalone descriptors — show, don't tell
- Reference products by **NAME, not SKU** in any customer-facing copy. "BLACK Rose Crewneck" not "br-001". SKUs are internal identifiers; SKU-first phrasing has caused product conflations.

**Example Product Description:**
```
BLACK ROSE HEAVYWEIGHT TEE
Built for those who move through darkness like it's home.
Double-stitched seams. 280gsm cotton. Oakland-made mentality.
This isn't fast fashion. This is armor.
```

---

## Canonical Tagline

> **`Luxury Grows from Concrete.`**

The period is part of the tagline. This is the **only** tagline. Never paraphrase:
- "luxury from the streets" = WRONG
- "grown from concrete" = WRONG
- "Luxury grows from the concrete" (no period, no capital C) = WRONG

---

## Key Brand Messages

- "Luxury Grows from Concrete." (only tagline — verbatim with period)
- "Where fashion meets emotion"
- "Redefine luxury fashion"
- "Sustainably crafted, limited edition designs"
- Named after a daughter, built by a father
- From losing everything to building an award-winning brand

---

## Target Customer

- Age: All ages (including children's line)
- Gender: All — pioneer in gender-neutral Bay Area streetwear
- Values quality over quantity, fashion as expression
- Appreciates founder story and authenticity
- Supports Black-owned, independent businesses
- Parents who want matching fits with their kids

---

## Founder Canon — What We NEVER Do

> **Cross-reference:** Full list in `brand-guardrails.md § 5`. The rules below are non-negotiable.

- **No urgency timers / countdown-pressure manipulation.** Scarcity stated as fact ("limited to pre-order", "250 made"), never a ticking clock.
- **No related-products / "complete the look" cross-sell on PDPs.** The garment is the protagonist. One piece, one story. (`woocommerce.php:541` hook commented out; do not reactivate without founder sign-off.)
- **No hype-merchant tone.** Corey's register: earned, specific, Oakland-direct. No "🔥🔥 DON'T MISS OUT 🔥🔥".
- **No European luxury-house aesthetic framing.** Wrong brand DNA (see The Five in `brand-guardrails.md § 2`).
- **No invented products or colorways.** Every product fact resolves through the canonical catalog CSV + per-SKU dossier (see section below). Never memory, never imagination.

---

## Canonical Product Source

> **Cross-reference:** `brand-guardrails.md § 6` has the full canonical source protocol.

Product facts — name, collection, price, description, colorway — resolve through:

1. **Catalog CSV:** `wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv` (33 SKUs)
2. **Per-SKU dossiers:** `skyyrose/elite_studio/assets/` per-product directories
3. **Live agent (for social copy):** `SocialMediaAgent` → the product registry via `skyyrose.core.product.get_product(sku)`

**Never invent a product, colorway, or detail.** If catalog data is absent, surface the gap — do not fill it with inference. (This rule traces to the lh-005 fanny-pack hallucination incident, 2026-05-27.)

Dossiers are Corey-authored from the actual product; do not draft dossier content via ML without founder review.

---

## STOP-AND-SHOW Confirmation Gates

The following actions require an explicit confirmation manifest + `y` from the user before execution:

| Action | Gate |
|--------|------|
| Any paid API call (FASHN, Gemini image-gen, FLUX, Replicate) | STOP AND SHOW cost + files |
| Klaviyo send (any list, any email) | STOP AND SHOW audience + template |
| WooCommerce REST write (create/update/delete product, order, media) | STOP AND SHOW exact payload |
| WordPress Media Library upload | STOP AND SHOW file + destination |
| Deploy to skyyrose.co (`deploy-theme.sh` / SFTP) | STOP AND SHOW manifest |

"Autonomous" means Claude handles implementation after confirmation. It does NOT mean Claude decides what to spend or deploy without checking first.

---

## Cross-References

| Topic | Where to find it |
|-------|-----------------|
| Visual references (The Five) + full lockup rule | `brand-guardrails.md § 2, § 4` |
| Collection voice lines (per-collection full library) | `docs/brand/collection-stories.md` |
| Per-SKU product facts | `wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv` + per-SKU dossiers |
| Canonical visual references doc | `docs/brand/visual-references.md` |
| STOP-AND-SHOW full protocol | `CLAUDE.md` (project root) under "STOP AND SHOW" |
| Font declarations | `wordpress-theme/skyyrose-flagship/theme.json` |
| Design tokens (all CSS vars) | `wordpress-theme/skyyrose-flagship/assets/css/design-tokens.css` |
| skyyrose-content-engine social guardrails | `skyyrose-content-engine/brand-guardrails.md` (original source of The Five + lockup rule) |
