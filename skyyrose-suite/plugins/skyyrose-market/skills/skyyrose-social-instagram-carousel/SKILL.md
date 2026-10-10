---
name: skyyrose-social-instagram-carousel
description: "Produces slide-by-slide Instagram carousel scripts, design notes, and brand-voice captions for SkyyRose product launches, collection stories, and styling content."
allowed-tools: Read Write Edit Glob
---

# SkyyRose Social — Instagram Carousel

## When to Use This Skill

- Writing a 5-7 slide product launch carousel for a new SkyyRose drop
- Telling a collection origin story across sequential slides (Black Rose, Love Hurts, Signature, Kids Capsule)
- Creating a "3 ways to style" or "fabric story" carousel for a single garment
- Producing a founder / brand-story carousel (Bay Area roots, why SkyyRose exists)
- Generating a save-worthy styling guide tied to an upcoming drop

**DO NOT** use this for single static Instagram posts, Reels scripts, Stories stickers, or Instagram ad creative. This is for swipeable carousel posts only. Use `skyyrose-social-tiktok-script` for video.

---

## Brand Canon (non-negotiable)

- **Tagline:** none authorised (founder decision 2026-10-06). Never add one.
- **Collection voice is strict:** "Bloodline that raised me" = Love Hurts ONLY. "Armor / you already stood up / concrete answering back" = Black Rose ONLY. Signature = "stay golden / the standard". Kids Capsule = little royalty, heritage passed down.
- **Name, not SKU:** Write "BLACK Rose Crewneck", not "br-001". SKU-first copy has caused product conflations — it is forbidden in any customer-facing slide.
- **No hype-merchant tone:** No countdown timers, no "DON'T MISS OUT", no fake urgency. Scarcity = "limited to pre-order" stated once as fact.
- **Garment is the protagonist:** No "complete the look" bundling. One piece, one story per carousel.
- **The Five references only:** Kith, Oaklandish, Culture Kings, Fear of God, Palm Angels. Never European luxury house framing.

Full canon: `../skyyrose-content-engine/brand-guardrails.md`

---

## Phase 1: Brief

### Required Inputs

| Input | What to Ask | Default |
|-------|-------------|---------|
| **Product / topic** | "Which product or collection is this carousel for?" | No default — must be provided. Use the NAME, not SKU. |
| **Carousel type** | "Product launch, styling guide, collection story, founder story, or fabric/construction deep-dive?" | Product launch |
| **Slide count** | "How many slides? (5-7 is optimal for IG algorithm)" | 6 slides |
| **Collection** | "Black Rose, Love Hurts, Signature, or Kids Capsule?" | Derive from product if possible |
| **CTA** | "Save, share, comment DROP, or link in bio?" | "Link in bio" + "Comment DROP for early access" |
| **Drop status** | "Live, pre-order, or coming soon?" | Pre-order |

**GATE: Confirm product name, collection, and CTA before proceeding. Never begin writing slides against an ambiguous product reference.**

---

## Phase 2: Outline

### Carousel Architecture

Every SkyyRose carousel follows this spine:

1. **Cover slide** — hook that stops the scroll mid-feed; collection energy is unmistakable in the first frame
2. **Context slide** — why this piece exists; the emotional register of the collection
3. **Body slides (2-4)** — product detail, construction story, styling angle, or collection lore
4. **CTA slide** — single action + @SkyyRose handle

### Outline Format

```
Cover:    [Hook — the line that makes them swipe]
Slide 2:  [Why this piece / collection context]
Slide 3:  [Construction or material detail]
Slide 4:  [Styling angle or collection lore]
Slide 5:  [Community / culture tie or founder voice]
CTA:      [Single action — save / pre-order / comment]
```

**GATE: Approve outline before writing slide copy. If the collection voice is Black Rose, confirm no Love Hurts language is in the brief.**

---

## Phase 3: Write

### Slide-by-Slide Content

For each slide deliver:
1. **Headline text** (appears large on slide image — max 8 words)
2. **Supporting text** (body copy below headline — max 30 words)
3. **Design note** (specific enough for a designer to execute: color palette from token, layout direction, lockup usage)

### Slide Rules

**Cover Slide**
- Headline: 4-8 words. Must create tension, curiosity, or an identity statement.
- Do NOT render the collection name as live type in hero position — use the lockup image (`assets/images/hero-overlays/`). Live type goes in supporting subtext only.
- Background palette: Dark `#0A0A0A` base + collection accent (Silver `#C0C0C0` for Black Rose, Crimson `#DC143C` for Love Hurts, Gold `#D4AF37` for Signature, Rose Gold `#B76E79` for Kids).
- Proven SkyyRose cover formats:
  - Identity gap: "You know what you stood up from."
  - Fabric-first: "Sherpa that keeps. Logo that means something."
  - Drop reveal: "The [Product Name] is here."

**Body Slides**
- One point per slide — never two.
- Headline: 3-7 words (the point, not a sentence)
- Supporting text: 1-2 short sentences. Total under 40 words per slide.
- Alternate layout (left-heavy / right-heavy / centered) to signal new slide at a glance.
- Design note must specify font choice: Hanken Grotesk body, Anton for UI labels.

**CTA Slide**
- Single action. If pre-order: "Pre-order open. Link in bio." If live: "Shop now. skyyrose.co"
- Include @SkyyRose handle.
- Design: clean, near-black background, Rose Gold accent line, no competing visual elements.

### Caption Writing

Caption complements — does not repeat — slide content.

```
## Caption Structure

[Hook line — earns the "...more" tap; must land without seeing the slides]

[2-3 sentences: the emotional or construction story the slides gesture at but don't spell out]

[1 sentence: drop status / availability — factual, no pressure language]

[CTA: "Link in bio." or "Comment DROP and we'll send you the direct link."]
```

**Caption length:** 150-300 words. Hashtags go in the FIRST COMMENT, not the caption.

**Hashtag block for first comment (15-20 tags):**
- Branded always: `#SkyyRose` `#TheSkyRoseCollection`
- Collection-specific (pick set): `#BlackRoseCollection` OR `#LoveHurtsCollection` OR `#SignatureCollection` OR `#SkyyRoseKids`
- Niche (rotate 10-12): `#LuxuryStreetwear` `#BlackOwnedFashion` `#OaklandFashion` `#BayAreaStyle` `#StreetLuxury` `#BlackDesigner` `#UrbanLuxury` `#TheTown` `#MadeInOakland` `#IndependentFashion`

### Formatting Rules

| Element | Rule |
|---------|------|
| **Slide dimensions** | 1080×1350px (4:5 — maximum feed real estate) |
| **Headlines** | 40-60pt Archivo or Anton (Cinzel as optional engraved-caps accent) |
| **Body text** | 24-30pt Hanken Grotesk |
| **Words per slide** | Under 40 |
| **Collection name in hero** | Lockup image ONLY — never live type |
| **Hashtags** | First comment, not caption |

---

## Phase 4: Polish

### Carousel Quality Checklist

```
- [ ] Cover slide stops a scrolling thumb — passes "would YOU swipe?" test
- [ ] Every slide under 40 words
- [ ] One clear point per slide
- [ ] Collection name in hero position uses lockup image, not live type
- [ ] Collection voice is correct — no cross-attribution
- [ ] Design notes specify colors by token value, not generic descriptions
- [ ] CTA slide has single action + handle
- [ ] Caption hook earns the "more" tap without needing to see any slides
- [ ] Caption does not repeat slide copy verbatim
- [ ] 15-20 hashtags in first comment, not caption
- [ ] No urgency timers, no "don't miss out" language
- [ ] Product referenced by NAME, not SKU
```

### Posting Notes

- Best times: 11 AM–1 PM or 7–9 PM PST
- Share to Stories with "New Post" sticker within 1 hour of publishing
- Engage with every comment in first 30 minutes — carousel saves signal content quality to the algorithm
- Pin a reply to your own post with the direct product link if link-in-bio is too buried

---

## Implementation

```python
from agents.social_media_agent import SocialMediaAgent

agent = SocialMediaAgent()

# Generate a product launch carousel for the BLACK Rose Crewneck
post = agent.generate_post("br-001", "instagram", "product_launch")

print(post.caption)        # Brand-voice caption, hook-first
print(post.hashtags)       # Collection-aware hashtag set (put in first comment)
# The agent returns the caption + hashtags as your brand-voice SEED.
# The slide-by-slide structure (headline / supporting / design note) is what
# THIS skill produces from that seed via Phases 2-3 below.
```

```bash
# Smoke-test the full social venture pipeline for a given SKU:
python -m skyyrose.elite_studio.ventures.social smoke --sku br-001
```

**Scheduler row example** (n8n / posting calendar):

```json
{
  "sku": "br-001",
  "product_name": "BLACK Rose Crewneck",
  "collection": "black-rose",
  "format": "instagram-carousel",
  "slide_count": 6,
  "drop_status": "pre-order",
  "cta": "comment_drop",
  "scheduled_utc": "2026-06-03T19:00:00Z",
  "hashtag_placement": "first_comment",
  "notes": "Publish to feed; share to Stories within 60 min"
}
```

---

## Example: BLACK Rose Crewneck Drop Carousel (6 slides)

**Product:** BLACK Rose Crewneck | Collection: Black Rose | Status: Pre-order

```
COVER SLIDE
Headline:    "Armor doesn't ask permission."
Supporting:  BLACK Rose Crewneck. Pre-order open.
Design note: Dark #0A0A0A background. BLACK Rose lockup image (assets/images/hero-overlays/black-rose-lockup.png) centered upper third. Silver #C0C0C0 thin rule below lockup. Headline in Anton 56pt bottom-left. No other elements.

SLIDE 2
Headline:    "Built for the town that built you."
Supporting:  Oakland doesn't do soft. Neither does this crewneck. French terry construction. Weight that means something when you put it on.
Design note: Full bleed product flat-lay on dark concrete background. Headline top-left, Anton 44pt silver. Body Hanken Grotesk 26pt white.

SLIDE 3
Headline:    "The details you earn."
Supporting:  Embroidered Black Rose chest script. Reinforced ribbed cuffs and hem. Preshrunk so the drop doesn't leave you.
Design note: Two-panel layout: left panel = close-up embroidery detail; right panel = ribbed cuff detail. Minimal white labels (Anton 18pt) pointing to each detail.

SLIDE 4
Headline:    "Concrete answering back."
Supporting:  Black Rose is the collection for those who already stood up. This piece doesn't try to prove anything. It simply is.
Design note: Lifestyle editorial — model in full Black Rose look, outdoor Oakland location, overcast light. Headline bottom-center, Archivo 44pt, silver.

SLIDE 5
Headline:    "250 made. That's the run."
Supporting:  No restock. No restocking announcement. When it's gone, it's gone — stated once.
Design note: Near-black background. Single centered text block. Hanken Grotesk 30pt white. Silver horizontal rule above and below the block. No product imagery.

CTA SLIDE
Headline:    "Pre-order now."
Supporting:  skyyrose.co | @SkyyRose
Design note: Dark #0A0A0A. Rose Gold #B76E79 accent left border. Headline Anton 52pt white centered. Handle Hanken Grotesk 22pt silver below.
```

**Caption:**

```
You already know what this is.

The BLACK Rose Crewneck is French terry weight, Oakland-grade construction,
and a chest embroidery that took four rounds to get right.
We didn't cut corners because we were building for The Town —
and The Town can tell.

250 made. Pre-order is open. When it's gone, it's gone.

Link in bio.
```

**First comment hashtags:**
`#SkyyRose #BlackRoseCollection #BlackOwnedFashion #OaklandFashion #TheTown #LuxuryStreetwear #UrbanLuxury #BlackDesigner #StreetLuxury #BayAreaStyle #IndependentFashion #TheSkyRoseCollection #BlackRoseBySkyyRose #MadeInOakland`

---

## Anti-Patterns

- **Rendering the collection name as live type in the cover hero** — "Black Rose" set in Cinzel on the cover IS the lockup's job. Use the lockup image asset.
- **Cross-attributing collection language** — writing "the bloodline that raised me" under a Black Rose product is a brand violation. Each collection has its own emotional register; check the guardrails before writing body copy.
- **Putting hashtags in the caption** — they belong in the first comment. Hashtags in captions read as generic and crowd the voice.
- **Repeating slide copy verbatim in the caption** — the caption should tell a story the slides only gesture at. They are two separate surfaces.
- **Fake urgency language** — "Only 3 left! Order NOW before it's too late!" is not SkyyRose's register. State scarcity as fact, once.
- **Multiple CTAs on the CTA slide** — "Save, share, comment, AND click the link" is zero CTAs. Pick one.
- **Referencing SKU codes in copy** — "br-001 drop is here" is internal language. Always the product name.
- **Generic Canva gradient backgrounds** — SkyyRose color palette is specific: Dark `#0A0A0A` base, collection accent token. No stock gradients.
- **Skipping the design note** — "Make it look nice" is not a design note. Every slide needs color tokens, font specs, and layout direction so a designer can execute without questions.
- **Covering two products in one carousel** — garment is the protagonist. One piece, one story.

---

## Recovery

- **Cover slide isn't stopping the scroll:** Test the identity-statement format ("You know what you stood up from.") — it performs above average for SkyyRose because the audience self-selects.
- **Collection voice feels off:** Read `docs/brand/collection-stories.md` for the exact emotional register. If you're not sure which register a phrase belongs to, it doesn't belong in this draft.
- **Too many points for 6 slides:** Cut to the 4 most iconic product details. Save the rest for a Part 2 carousel or a Reels close-up.
- **No design assets yet:** Flag the slide as "asset pending" and write the copy against the design note. The script and caption can ship to the client while photography is in production.
- **Caption feels flat:** Add one specific construction detail (material weight, stitch count, who embroidered it) — specificity is what earns saves.
- **Hashtag set needs updating:** Check the canonical set in `skyyrose-content-engine` and rotate niche tags based on recent performance data from the analytics dashboard.
