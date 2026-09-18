# SkyyRose Social Branch — Brand Guardrails (Shared Canon)

> **Single source of consistency for every `skyyrose-social-*` skill.**
> Every skill in the social branch references this file. If a skill's output
> violates anything here, the output is wrong — fix the output, not the rule.
> These rules are derived from project memory and `docs/brand/`. They are
> non-negotiable and apply to captions, scripts, briefs, plans, and policy alike.

---

## 1. The brand in one breath

- **Brand:** SkyyRose (The Skyy Rose Collection) — luxury Oakland streetwear.
- **Tagline (verbatim, the ONLY tagline):** `Luxury Grows from Concrete.`
  Period included. Never paraphrase ("luxury from the streets", "grown from concrete" = WRONG).
- **Founder:** Corey Foster. Oakland / Bay Area roots. Direct, earned, unhurried voice.
- **Anchor:** Oakland, CA ("The Town"). "Bay Area" is acceptable; Oakland-first is preferred.
- **Site:** skyyrose.co (WordPress store). The dashboard devskyy.app is internal — never market it.

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
Rick Owens, 032c, Acne, Givenchy-by-Tisci, or "old-money European house" framing. Wrong brand DNA.
Repo doc: `docs/brand/visual-references.md`.

## 3. Collections — each is its own emotional register (NEVER cross-attribute)

| Collection | Slug | Register / voice | Accent token |
|------------|------|------------------|--------------|
| **Black Rose** | `black-rose` | Gothic luxury, **armor**. "You already stood up." "Concrete answering back." Twilight, defiant elegance. | Silver `#C0C0C0` |
| **Love Hurts** | `love-hurts` | Street passion, **the bloodline that raised me**. Raw romance, crimson heat. | Crimson `#DC143C` |
| **Signature** | `signature` | West Coast luxury, **the standard**. "Stay golden." Elevated, worldwide respect. | Gold `#D4AF37` |
| **Kids Capsule** | `kids-capsule` | Little royalty, heritage passed down. Playful but premium. | Rose Gold `#B76E79` |

Global accent: Rose Gold `#B76E79`. Background: Dark `#0A0A0A`.

**Hard rule:** "Bloodline that raised me" belongs to **Love Hurts ONLY**. "Armor / you already
stood up / concrete answering back" belongs to **Black Rose ONLY**. Never put one collection's
line on another. Pull per-collection lines from `docs/brand/collection-stories.md`.

## 4. Hero titles = lockup IMAGES, never type-rendered

A collection's **name** in any hero / cover / title position is a brand-script **lockup image**
(`assets/images/hero-overlays/` for BR/LH/SIG, `assets/images/logos/` for Kids), NOT live type.
Fonts (Archivo headings — all collections, Hanken Grotesk body, Anton UI labels,
Cinzel optional engraved-caps accent) apply ONLY to interior surfaces — body copy, captions, slide subtext — never to
the collection name itself. The lockup IS the name.

## 5. Founder canon — what we NEVER do

- **No urgency timers / countdown-pressure manipulation.** Scarcity is stated as fact
  ("limited to pre-order", "250 made"), never as a fake ticking clock.
- **No related-products / "complete the look" cross-sell.** The garment is the protagonist.
  One piece, one story. Do not bundle or up-sell inside product storytelling.
- **No hype-merchant tone.** Corey's register: earned, specific, Oakland-direct. "Imagery hasn't
  earned it" energy — we don't oversell what the work hasn't proven. No "🔥🔥 DON'T MISS OUT 🔥🔥".
- **Reference products by NAME, not SKU,** in any customer-facing copy. "BLACK Rose Crewneck",
  not "br-001". (SKUs are internal; SKU-first phrasing has caused product conflations before.)

## 6. Canonical product source

Product facts (name, collection, price, description) resolve through the canonical catalog
(`wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv`) + the live agent
`SocialMediaAgent`, which reads the product registry through `get_product(sku)`. **Never invent a
product, colorway, or detail.** If a skill needs product data, call the agent or read the catalog —
do not hallucinate. (This rule traces to the lh-005 fanny-pack hallucination incident.)

**Resolution order:**
1. `wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv` (33 SKUs, authoritative)
2. Per-SKU dossier (linked via `dossier_slug` column)
3. `SocialMediaAgent.get_collection_context(collection)` for collection-level facts

Memory, session context, and social copy are NOT valid product sources. Never fall back to them.

---

## 7. SKILL.md format (every social skill MUST match)

```markdown
---
name: skyyrose-social-<slug>
description: "<One specific sentence: what it produces + when to use, for SkyyRose.>"
allowed-tools: Read Write Edit Glob
---

# SkyyRose Social — <Title>

## When to Use This Skill
- bullet list of concrete triggers
**DO NOT** use this for <adjacent-but-different skill>.

## Brand Canon (non-negotiable)
> A compact 4-6 bullet block of the rules from this guardrails file that matter
> MOST for THIS skill (e.g. a caption skill leads with tagline + collection voice +
> name-not-SKU; a photography brief leads with the Five refs + lockup rule).
> Always end with: "Full canon: ../skyyrose-content-engine/brand-guardrails.md"

## Phase 1..N  (Brief → Outline → Write/Produce → Polish, adapted per skill)
Tables for inputs, GATE lines where confirmation matters.

## Implementation        <-- see section 8 (LOCKED)

## Example: <real SkyyRose worked example using a real product/collection>

## Anti-Patterns
- 6-10 bullets, each a specific WRONG thing + why, SkyyRose-flavored.

## Recovery
- 4-6 bullets: when X goes wrong, do Y.
```

## 8. The `## Implementation` block (LOCKED — identical shape across all skills)

Every skill carries a `## Implementation` section with BOTH of:

**(a) A runnable snippet** — either Python against the live agent, or the venture CLI:

```python
from agents.social_media_agent import SocialMediaAgent

agent = SocialMediaAgent()
post = agent.generate_post("br-001", "instagram", "product_launch")
print(post.caption)        # real brand-voice caption
print(post.hashtags)       # collection-aware hashtag set
```
```bash
# Generate a multi-platform set through the Elite Studio social venture:
python -m skyyrose.elite_studio.ventures.social smoke --sku br-001
```

**(b) One config/payload example** relevant to the skill — a scheduler/cron entry, a platform
API payload, an n8n/automation node, a posting-calendar row, or a tracking-sheet schema.

**Exception — deliverable-spec skills** (`media-kit`, `pr-pitch`, `brand-photography-brief`,
`product-photography-brief`, `social-media-policy`, `platform-community-guidelines`,
`social-media-graphics`): replace `## Implementation` with **`## Artifact specification`** —
the literal output document structure (sections, fields, file format, dimensions) the skill emits.

> Rationale: the source bundle skills have zero code. Locking this shape is what makes 27
> independently-authored skills read as ONE product (the "cloned SaaS feel").

## 9. Worked-example rule

Every skill's `## Example` uses a REAL SkyyRose product or collection — preferably:
`BLACK Rose Crewneck` (br-001, Black Rose), a Love Hurts piece, or a Signature piece — with the
correct collection voice from section 3. Never a generic "Acme brand" placeholder.

Product names and facts MUST be resolved from the canonical catalog CSV before use in any example.

---

## 10. Content-engine migration map (for the strategy/calendar/format skills)

`skyyrose-content-engine` is being refactored into a one-page **index hub**. Its production
knowledge migrates into sub-skills. When authoring these skills, SEED them with the named section
from the current content-engine, THEN layer the bundle-source structure on top:

| content-engine section | → seed into sub-skill |
|---|---|
| 5 Content Pillars + ratios + best platforms | `social-media-strategy` |
| Weekly Rhythm (Mon–Sun) + Monthly Specials | `social-media-calendar` |
| Instagram Playbook (carousel bits) + Caption Formulas + br-001 example | `instagram-carousel` |
| TikTok Playbook + Video Script Templates (15s/30s/60s) | `tiktok-script` + `short-form-video-plan` |
| X/Twitter Playbook | `twitter-thread` + `thread-hook-writer` |
| Pinterest Playbook | `pinterest-strategy` |
| Hashtag Strategy (branded + collection + niche sets) | `hashtag-strategy` |
| Cross-Platform Repurposing flow | `social-media-strategy` |
| Anti-Patterns | distribute to the topical skill |

The hub then links out to all sub-skills — it does not re-derive their content.

> **Pillar ratios and posting times in sub-skills are heuristics.** Label them explicitly as
> "starting-point heuristics — test and adjust per platform analytics" wherever they appear.
> Do not present them as sourced facts or benchmarks.
