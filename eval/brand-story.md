---
name: Brand Story Canon (operational excerpt of WP §2)
specified_by: [wp: §2]
phase: 0
test_command: grep -c "" eval/brand-story.md  # must equal at least 1
pass_threshold: Voice rules + brand-NOT list + tagline + collection thesis present
last_updated: 2026-05-03
last_updated_by: eval-harness (Phase 0)
---

# Skyyrose — Brand Story Canon

This file is the canonical brand story Claude Code reads before any design or copy work. It operationalizes WP plan §2 in an evaluable form. If a design or copy decision contradicts this story, **the design or copy is wrong, not the story.**

The full prose version lives in `docs/SKYYROSE_WORDPRESS_PLAN.md` §2. This file is the binding distillation.

---

No tagline is authorized. Do not restore retired slogans.

> ****

There is exactly one tagline. It is "" It appears as the brand promise everywhere it appears.

> **Retired:** "Where Love Meets Luxury" — never use this anywhere. It's in `MEMORY.md` as a banned phrase.

---

## The one-liner

> Skyyrose is intellectual street poetry from The Town — luxury with a pulse, not a logo.

---

## What Skyyrose IS

- Luxury that grew up on 14th and Broadway in Oakland, not aspirational streetwear
- A thesis the customer buys into, not just a product
- Confident — never loud
- Cinematic — never theatrical
- Editorial — never catalog
- Specific — never generic
- Earned — never gifted

## What Skyyrose IS NOT

- **NOT athleisure.** Comfortable but not gym-ready. The customer is going somewhere.
- **NOT influencer streetwear.** No drop-shipped graphic tees, no celebrity endorsement core.
- **NOT generic luxury** ("minimalism = sophistication"). There's color, texture, grit.
- **NOT sad-aspirational.** The customer wants to be more themselves, not someone else.

---

## The four collections (and what each is *about*)

| Collection | Thesis | Visual language |
|------------|--------|-----------------|
| **Black Rose** | Grief that became armor. Oakland night, gothic gravity. | Archivo headings, Cinzel engraved-caps accent, dark/silver/charcoal palette, BAY BRIDGE / Oakland street references |
| **Love Hurts** | The romanticism of being from a place the world misjudges. Beauty-and-the-Beast from BEAST's perspective. | Crimson accent, gothic cathedral, enchanted-rose-dome immersive |
| **Signature** | What you wear when you've stopped explaining yourself. Bay Area / SF, golden hour. | Gold accent, GOLDEN GATE BRIDGE references, fashion-runway sensibility |
| **Kids Capsule** | (Carry the brand DNA into kidswear.) | Rose-gold accent, playful but not childish |

---

## Voice rules (banned phrases — fail any = fail)

| Banned | Reason | Use instead |
|--------|--------|-------------|
| "the Bay Area" | Oakland-specific brand | "The Town" or "Oakland" |
| "iconic" | Overused, generic | The specific reason it matters |
| "elevated" | Generic luxury cliché | Show, don't say |
| "curated" | Generic | "Selected" / "chosen" or describe the selection |
| "luxe" | Cheapens the brand | The brand IS luxury — don't say "luxe" |
| "drip" | Generic streetwear-speak | The garment by name |
| Exclamation marks in product / marketing copy | Skyyrose doesn't shout | Period or em-dash |
| "you deserve this" / "treat yourself" | Customer doesn't need permission | Just describe the garment |
| Any apology for price | Confidence is the policy | The price as the price |
| Explaining Oakland to outsiders | If they don't get it, they're not the audience | Reference Oakland specifics without footnotes |

---

## The visual language (follows from the brand)

- **Confident, never loud** — restrained palette; impact from material, proportion, stance
- **Cinematic, never theatrical** — motion serves the story
- **Editorial, never catalog** — every product photographed like it's the only thing
- **Specific, never generic** — Oakland references named, never gestured at
- **Earned, never gifted** — luxury moves like dramatic typography or generous whitespace get *paid for* by the design

---

## The "would Corey wear this?" filter (WP §7.3)

The single most important filter on every design decision:

- **"Yes, specifically because [reason]"** → ship
- **"I think so"** → not ready; iterate
- **"No because [reason]"** → revise

Subjective but binding. The founder's taste is the brand's taste.

---

## Brand colors (locked palette)

| Token | Value | Primary use |
|-------|-------|-------------|
| Brand dark | `#0A0A0A` | Background, body text on light surfaces |
| Brand white | (system white via tokens) | Background on dark surfaces |
| Rose gold | `#B76E79` | Global accent, Kids Capsule signature |
| Black Rose silver | `#C0C0C0` | BR collection accent |
| Love Hurts crimson | `#DC143C` | LH collection accent |
| Signature gold | `#D4AF37` | SIG collection accent |

Plus 5 grays + semantic (success/warning/error). No off-system colors anywhere.

---

## Typography (locked)

| Family | Use |
|--------|-----|
| Archivo | Display / hero / headings (all collections) |
| Hanken Grotesk | Body / UI |
| Anton | UI caps / accent |
| Cinzel | Engraved-caps accent |
| Inter | System / fallback |

All font families self-hosted (woff2) and declared in `theme.json` Font Library — **zero Google Fonts CDN.** Collection name-scripts (SkyyRose Black Rose Script, SkyyRose Love Hurts Graffiti, Pinyon Script, Grand Hotel) appear only as lockup images, never as interior text. See `SOT.md` → `typography.json`.

---

## The founder

Corey Foster. Lives in The Town. The brand's taste IS Corey's taste.

---

## The audience

Not pretentious. They want clothes that say something — but only to people who already know. The brand doesn't shout. It doesn't overexplain. It assumes the customer's intelligence and rewards it.

The customer who buys Skyyrose is buying a thesis, not a product.

---

## What this file is for

Every Phase 4+ design surface, every Phase 5.3 narrative product page, every Phase 5.4 drop launch copy, every Phase 6 polish pass — they all read this file first. The 5-pass thinking protocol's pass 1 (brand story coherence, WP §1.1) explicitly references this file.

If you're writing copy or designing a surface and you can't articulate how it serves this story — stop, read this file again, restart.
