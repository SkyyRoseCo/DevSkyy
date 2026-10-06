---
name: skyyrose-social-media-kit
description: "Produces the complete SkyyRose brand media kit document — cover, brand story, founder bio, per-collection one-sheets, product highlights, press contact, and brand asset list — for journalist and partner outreach, with all metric fields marked operator-supplied."
allowed-tools: Read Write Edit Glob
---

# SkyyRose Social — Media Kit

## When to Use This Skill

- Responding to a journalist, editor, or podcast host who asks "can you send your media kit?"
- Preparing a media kit to attach to a PR pitch follow-up (after the journalist responds to the initial pitch)
- Building a partner-facing brand document for co-marketing conversations
- Refreshing the media kit for a new collection launch or milestone
- Creating collection-specific one-sheets for targeted fashion press

**DO NOT** use this as the first touchpoint with press — send the personalized pitch email first (`skyyrose-social-pr-pitch`), then the media kit on request. A media kit cold-sent as the opening move is amateur-hour PR. **DO NOT** use this as an influencer media kit — this skill builds the brand's outbound kit, not a creator's monetization kit.

---

## Brand Canon (non-negotiable)

- **Tagline:** No tagline is authorised (founder decision 2026-10-06). No version of this kit carries one.
- **No fabricated stats, press placements, or awards.** All metric fields that require live data are marked `{operator-supplied}`. Do not fill them with invented numbers. The brand story is real — it doesn't need manufactured validation.
- **Founder:** Corey Foster. Oakland / Bay Area. Voice is earned, direct, unhurried — not a hype-merchant bio. The bio should read like a person, not a press release.
- **Products by NAME, not SKU** in all public-facing copy. "Black Rose Crewneck" in the one-sheet, not "br-001."
- **Collection voices are isolated.** Do not mix Black Rose copy into the Signature one-sheet. Each collection has its own register.
- **Hero titles = lockup IMAGES, not live type.** In the digital PDF, collection names in header positions use the official lockup image — not Cinzel or Archivo rendered as text.

Full canon: `../skyyrose-content-engine/brand-guardrails.md`

---

## Phase 1: Confirm Scope

### Required Inputs

| Input | What to Confirm | Default |
|-------|----------------|---------|
| **Kit scope** | "Full brand kit, or collection-specific one-sheet?" | Full brand kit |
| **Target audience** | "Fashion press, streetwear media, co-marketing partner, or investor?" | Fashion press |
| **Format** | "PDF structure (for print/email) or Markdown (for digital/web)?" | PDF structure |
| **Metrics available** | "What operator-supplied figures can be included? (orders, social followers, founding year, etc.)" | Only what operator confirms |

**GATE: Confirm scope and available real metrics before producing the kit.**

---

## Phase 2: Build the Kit

### Artifact Specification

The SkyyRose brand media kit is a 5-7 page document with the following structure. Every section is specified below. Fields marked `{operator-supplied}` must be filled in by the operator with verified data before sending — do not invent values.

---

#### Cover Page (Page 1)

```
[SkyyRose logo — centered, white on dark background]
[Collection lockup image for the primary collection being featured, if collection-specific kit]

THE SKYY ROSE COLLECTION

Oakland, California

[Year founded: {operator-supplied}]
skyyrose.co

[Press contact:]
skyyroseco@gmail.com
[Phone: {operator-supplied, optional}]
```

**Design notes:**
- Background: Dark `#0A0A0A`
- Logo and text: white
- Collection lockup (if featured): use official PNG from `assets/images/hero-overlays/` (BR/LH/SIG) or `assets/images/logos/` (Kids)
- Font for body text only: Hanken Grotesk or Archivo — NOT Cinzel or any font rendered as the collection name itself

---

#### Brand Story (Page 2)

```
## About SkyyRose

SkyyRose — The Skyy Rose Collection — is an Oakland-born luxury streetwear brand
founded by Corey Foster. Built in The Town, worn beyond it.

The founding truth: that craft, quality, and elevation can come from anywhere —
especially from places the fashion industry has historically overlooked.

SkyyRose launched in [Year: {operator-supplied}] with a single vision: to make luxury
streetwear that is rooted in Black culture, West Coast identity, and honest construction —
without a European house pedigree, without manufactured scarcity, and without urgency tricks.

Four collections. One city. No apology.

---

### Brand at a Glance

| | |
|---|---|
| **Founded** | {operator-supplied} |
| **Headquarters** | Oakland, California |
| **Collections** | Black Rose · Love Hurts · Signature · Kids Capsule |
| **Price range** | {operator-supplied} |
| **Distribution** | Direct-to-consumer — skyyrose.co |
| **Instagram** | @skyyroseco |
| **Orders fulfilled** | {operator-supplied} |
| **Social reach** | {operator-supplied} |
```

---

#### Founder Bio (Page 3)

```
## Corey Foster — Founder & Creative Director

[Founder photo — editorial, not a headshot. Oakland setting preferred.]

Corey Foster is the founder and creative director of SkyyRose — The Skyy Rose Collection.

[Bio text: operator-authored from actual founder voice. Do NOT generate a generic founder bio.
Source from: knowledge-base/seed/from-interview.md — the verbatim founder interview.
The bio should reflect Corey's specific Oakland story and the brand name origin (named for
his daughter Skyy Rose).
Voice: direct, specific, earned. Never hype-merchant. Never "visionary entrepreneur who...]

[Suggested structure — operator fills in:]
- Oakland anchor / where the brand comes from geographically and personally
- What problem the brand is solving (luxury streetwear gap in the Bay Area)
- The brand name origin
- Where the brand is going

**Quote (direct from founder, operator-supplied):**
"{operator-supplied — verbatim Corey quote for press use}"

---

### Press Contact

Corey Foster
Founder, SkyyRose
skyyroseco@gmail.com
skyyrose.co
Instagram: @skyyroseco
```

**Rules for the bio:**
- The founder bio in this kit must be sourced from the actual interview, not AI-drafted from scratch
- Read `knowledge-base/seed/from-interview.md` to pull the correct voice and facts
- Do not invent backstory, press milestones, or awards

---

#### Collection One-Sheets (Pages 4-7, one per collection)

Each collection gets its own page. Use only the register for that collection — never cross-attribute.

---

**Black Rose — One-Sheet**

```
[Black Rose lockup image — from assets/images/hero-overlays/br-lockup.png]

## Black Rose Collection

Accent: Silver #C0C0C0
Register: Gothic luxury. Armor. Defiant elegance.
"You already stood up." "Concrete answering back."

Aesthetic: Twilight and dark. Silver catches light on dark fabric.
Visual references: Fear of God (tonal restraint), Palm Angels (graphic confidence), Oaklandish (town authenticity)

### Featured Products

| Product Name | Description | Price |
|-------------|-------------|-------|
| [Name from catalog] | [1-sentence description in Black Rose register] | ${operator-supplied} |
| [Name from catalog] | [1-sentence description] | ${operator-supplied} |

[Product photography — editorial. Not lifestyle mockups without a person. Garment is the protagonist.]

### The Collection in One Line
"Armor for the ones who are still standing."
```

---

**Love Hurts — One-Sheet**

```
[Love Hurts lockup image — from assets/images/hero-overlays/lh-lockup.png]

## Love Hurts Collection

Accent: Crimson #DC143C
Register: Street passion. The bloodline that raised me. Raw romance, crimson heat.

Aesthetic: Red and dark. Emotional, embodied. Not fashion-forward — lived-in.
Visual references: Culture Kings (bold energy), Oaklandish (community rootedness), Fear of God (quiet premium quality)

### Featured Products

| Product Name | Description | Price |
|-------------|-------------|-------|
| [Name from catalog] | [1-sentence description in Love Hurts register] | ${operator-supplied} |
| [Name from catalog] | [1-sentence description] | ${operator-supplied} |

### The Collection in One Line
"For the ones who loved hard and are still here."
```

---

**Signature — One-Sheet**

```
[Signature lockup image — from assets/images/hero-overlays/sg-lockup.png]

## Signature Collection

Accent: Gold #D4AF37
Register: West Coast luxury. The standard. "Stay golden." Worldwide respect, Oakland roots.

Aesthetic: Warm and golden. Elevated. Something you earn your way to wearing.
Visual references: Kith (editorial product storytelling), Fear of God (premium basics), Palm Angels (runway-meets-street)

### Featured Products

| Product Name | Description | Price |
|-------------|-------------|-------|
| [Name from catalog] | [1-sentence description in Signature register] | ${operator-supplied} |
| [Name from catalog] | [1-sentence description] | ${operator-supplied} |

### The Collection in One Line
"The standard. Set in Oakland. Worn everywhere."
```

---

**Kids Capsule — One-Sheet**

```
[Kids Capsule logo — from assets/images/logos/kids-capsule.png]

## Kids Capsule

Accent: Rose Gold #B76E79
Register: Little royalty. Heritage passed down. Playful but premium.

Aesthetic: Soft and warm. The next generation wearing the brand their parents built.
Visual references: Kith (editorial retail polish), Oaklandish (community and heritage)

### Featured Products

| Product Name | Description | Price |
|-------------|-------------|-------|
| [Name from catalog] | [1-sentence description] | ${operator-supplied} |

### The Collection in One Line
"For the ones being raised on it."
```

---

#### Press Highlights (Page — include if any real coverage exists)

```
## In the Press

[ONLY include real, verified coverage. If none exists yet, omit this section entirely —
do not fabricate press placements.]

| Publication | Headline / Feature | Date |
|------------|-------------------|------|
| {operator-supplied} | {operator-supplied} | {operator-supplied} |

"[Quote from press coverage — verbatim, attributed, operator-supplied]"
```

**If no press coverage exists:** omit this section. Replace with:
```
## Community

[Operator-supplied: real customer quotes, tagged posts, UGC with permission,
or a brief statement about the community the brand is building.
Do not fabricate testimonials.]
```

---

#### Brand Asset Specifications (Final Page)

```
## Brand Assets Available for Press Use

All assets provided on request. Contact: skyyroseco@gmail.com

### Logos
| Asset | Format | Dimensions | Background |
|-------|--------|-----------|------------|
| SkyyRose wordmark | PNG | 2400px wide | Transparent |
| SkyyRose wordmark | SVG | Vector | Transparent |
| SkyyRose wordmark (white) | PNG | 2400px wide | Transparent — for dark backgrounds |
| Black Rose lockup | PNG | 3000 × 1200px | Transparent |
| Love Hurts lockup | PNG | 3000 × 1200px | Transparent |
| Signature lockup | PNG | 3000 × 1200px | Transparent |
| Kids Capsule logo | PNG | 2000 × 2000px | Transparent |

### Product Photography
| Asset | Format | Resolution | Usage |
|-------|--------|-----------|-------|
| Per-product editorial stills | JPG | 3000px min (longest side) | Press, editorial, web |
| Lifestyle / on-body shots | JPG | 3000px min | Editorial and social |
| Detail / texture close-ups | JPG | 3000px min | Product features, editorial |

### Usage Guidelines
- Logos may not be recolored, distorted, or used over busy backgrounds without approval
- Collection lockup images must be used as-is — never re-typed as live text
- Credit line for editorial use: "Photo courtesy of SkyyRose / The Skyy Rose Collection"
- For questions: skyyroseco@gmail.com
```

---

## Implementation

```python
from agents.social_media_agent import SocialMediaAgent

agent = SocialMediaAgent()

# Pull each collection's voice + hashtags to seed the one-sheets
black_rose = agent.get_collection_context("black-rose")
print(black_rose["full_name"])     # collection display name for the one-sheet header
print(black_rose["caption_hooks"]) # on-register lines to draw the one-sheet copy from
print(black_rose["hashtags"])      # collection hashtag set for the press asset list

# Pull a catalog-correct product blurb in the collection register
post = agent.generate_post("br-001", "instagram", "product_launch")
print(post.caption)                # one-sheet product description, brand voice
```

```bash
# Inspect the social venture surface that feeds the kit (agents + status):
python -m skyyrose.elite_studio.ventures.social agents
```

### Media Kit Version Tracker Schema

```json
{
  "kit_version": "1.2",
  "scope": "full_brand",
  "last_updated": "2026-06-01",
  "target_audience": "fashion_press",
  "format": "PDF",
  "collections_included": ["black-rose", "love-hurts", "signature", "kids-capsule"],
  "operator_supplied_fields_complete": false,
  "missing_fields": ["founding_year", "order_count", "press_quotes"],
  "asset_pack_location": "assets/press/media-kit-assets/",
  "send_to": "on_request_only"
}
```

---

## Example: Black Rose Collection Press Kit for Hypebeast Outreach

**Scenario:** A Hypebeast writer responded to the PR pitch and requested the media kit. The kit is Black Rose-scoped (collection-specific), 4 pages: cover, brand story + founder bio condensed, Black Rose one-sheet with Black Rose Crewneck as the featured product, and brand asset spec.

**Cover:** Dark background, Black Rose lockup image, `Oakland, California`, `skyyrose.co`.

**Brand story (condensed for collection kit):** 2 paragraphs — the founding truth, the Oakland anchor, and the Black Rose register in one line: "Armor for the ones who are still standing."

**Founder bio:** Pulled directly from `knowledge-base/seed/from-interview.md`. Corey's Oakland story, the Skyy Rose name origin, the founding vision. One verbatim quote operator-supplied.

**Black Rose one-sheet:** Black Rose lockup image (PNG from `assets/images/hero-overlays/`), Silver accent, "Gothic luxury. Armor. Defiant elegance." register, Black Rose Crewneck featured with catalog-sourced description and price.

**Asset spec:** Logo formats available, usage guidelines, credit line.

**What is NOT in this kit:** Fabricated press placements, invented follower counts, made-up "as seen in" logos. The brand stands on its story — that is sufficient for press outreach.

---

## Anti-Patterns

- **Sending the media kit as the first press touchpoint** — the pitch comes first. The kit is a follow-up document. Cold-sending a PDF signals that you don't know how PR works.
- **Fabricating press placements** — "As seen in Vogue" when you haven't been. Journalists verify. One fake placement destroys all credibility.
- **Filling in metric fields with estimates or aspirational numbers** — use `{operator-supplied}` and actually fill them in with verified data, or omit the row. Never write "~10K orders" if you don't know.
- **Cross-attributing collection voices on the one-sheets** — the Black Rose page must not use Love Hurts language. Each page is its own emotional register.
- **Rendering collection names as live type in the PDF design** — the lockup images exist for this reason. Placing "Black Rose" in Cinzel as a heading is a brand violation.
- **A generic founder bio generated from nothing** — the bio must be sourced from the actual interview. Read `knowledge-base/seed/from-interview.md`. Do not draft a bio from training data.
- **Making the kit longer than 7 pages** — press is busy. Everything needed is in 5-7 pages maximum. A 15-page brand bible is not a media kit.
- **Referencing products by SKU** — "br-001 Crewneck" in a press kit is unprofessional. Always use the full product name.
- **Listing European luxury houses as visual references** — this kit explicitly names Kith, Oaklandish, Culture Kings, Fear of God, and Palm Angels as the reference lane. Not Bottega, not Numéro, not Rick Owens.

---

## Recovery

- **Journalist asks for the kit but no real stats are ready yet:** Send the kit with `{operator-supplied}` fields removed rather than invented. A story-first kit without metrics is honest and still useful. Add the community section with real customer quotes if available.
- **Founding year or other basic facts are uncertain:** Ask the operator. Do not guess. Basic brand facts (founding year, price range) must be accurate.
- **Journalist wants a collection-specific one-pager instead of the full kit:** Build the collection one-sheet (one page) from the artifact spec above — cover + one-sheet + asset spec. Trim to 2-3 pages.
- **Kit needs to be updated for a new drop:** Refresh the collection one-sheets with the new product names and descriptions pulled from the catalog. Bump the version number in the tracker schema. Do not update metrics fields unless operator confirms new verified numbers.
- **No press coverage exists to include:** Omit the Press Highlights section entirely. Replace with Community if real customer quotes are available. Do not create a placeholder section — an empty press section is worse than no press section.
