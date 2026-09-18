---
name: skyyrose-content-engine
description: "Index hub for the SkyyRose social media branch — routes to 27 specialized social skills (content formats, strategy, community, influencer/PR, visual briefs) and the Elite Studio social venture. Use to find the right SkyyRose social skill, or for the at-a-glance brand-voice quick reference."
allowed-tools: Read Write Edit Glob
---

# SkyyRose Content Engine — Social Branch Hub

> The front door to the SkyyRose social media branch of Elite Studio. This is an
> **index** — the depth lives in the specialized `skyyrose-social-*` skills below.
> Start here to find the right skill, confirm brand voice, or reach the venture.

**Non-negotiable canon for the whole branch:** [`brand-guardrails.md`](./brand-guardrails.md)
— read it before producing anything. Every sub-skill references it.

> **Last updated:** 2026-06-05

---

## Wrong entry point? Go here instead

| If your task is… | Use this instead |
|------------------|-----------------|
| Brand DNA, visual identity, tone-of-voice reference, founder story | [`skyyrose-brand-dna`](../skyyrose-brand-dna/SKILL.md) |
| SEO, search/catalog copy, product descriptions for the WooCommerce store | [`skyyrose-seo-commerce`](../skyyrose-seo-commerce/SKILL.md) |
| Email marketing flows, Klaviyo sequences, drip campaigns | [`skyyrose-email-flows`](../skyyrose-email-flows/SKILL.md) |
| Paid media briefs, ad creative, budget/channel strategy | [`skyyrose-paid-media`](../skyyrose-paid-media/SKILL.md) |
| Product copy (PDPs, naming, retail-shelf language) | [`skyyrose-product-copy`](../skyyrose-product-copy/SKILL.md) |

This hub is **social/content**. When the task is brand-definition (not brand-application),
`skyyrose-brand-dna` is the correct entry point.

---

## Brand voice — at a glance

- **Tagline (verbatim):** `Luxury Grows from Concrete.` — period included, never paraphrased.
- **Brand:** SkyyRose — luxury Oakland streetwear. Founder: Corey Foster. Site: skyyrose.co.
- **Voice:** earned, unhurried, Oakland-direct. No hype-merchant tone, no fake urgency, no
  "complete the look" cross-sell. The garment is the protagonist. Reference products by NAME, not SKU.
- **Visual references (the Five, ALWAYS):** Kith · Oaklandish · Culture Kings · Fear of God · Palm Angels.
  NEVER European luxury-house framing (no Bottega Veneta, Rick Owens, 032c, Acne, etc.).

### Collections (each its own register — never cross-attribute)

| Collection | Register | Accent |
|------------|----------|--------|
| **Black Rose** | Gothic luxury, armor. "You already stood up." "Concrete answering back." | Silver `#C0C0C0` |
| **Love Hurts** | Street passion, "the bloodline that raised me." Crimson heat. | Crimson `#DC143C` |
| **Signature** | West Coast luxury, "the standard." "Stay golden." | Gold `#D4AF37` |
| **Kids Capsule** | Little royalty, heritage passed down. | Rose Gold `#B76E79` |

Global accent Rose Gold `#B76E79` · Background Dark `#0A0A0A`. Full canon in `brand-guardrails.md`.

### Content pillars

> **Heuristic — test and adjust per platform analytics.** The ratios below are starting-point
> hypotheses, not sourced benchmarks. After 30+ days of publishing, compare engagement rates by
> pillar against your actual audience data and rebalance accordingly.

Brand Story (15%) · Product Showcase (30%) · Culture & Community (25%) · Lifestyle (20%) · Exclusivity (10%).

Depth in `skyyrose-social-social-media-strategy`.

### Posting times (PST)

> **Heuristic — test and adjust per platform analytics.** These are common industry starting
> points, not SkyyRose-specific measured optima. Use Instagram Insights, TikTok Analytics, and
> X analytics on your own account to validate and refine. See Instagram's "Most Active Times"
> in Professional Dashboard after 7+ days of posts.

Instagram 11am–1pm / 7–9pm · TikTok 9am, 12pm, 6pm, 9pm · X throughout day, Oakland energy.

---

## Canonical product source — mandatory

**All product facts (name, collection, price, colorway, garment type, edition size) MUST resolve
through the canonical sources in order:**

1. **Catalog CSV:** `wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv` — 33 SKUs,
   columns: `sku, name, price, collection, description, sizes, color, edition_size, ...`
2. **Per-SKU dossier:** `get_product(sku)` (the product registry) + per-SKU dossier projections
   (linked via `dossier_slug` column in the CSV).
3. **Live agent:** `SocialMediaAgent.get_collection_context(collection)` for collection-level facts.

**Never invent a product, colorway, detail, or price from memory or social copy context.**
Reference products by NAME (e.g. "BLACK Rose Crewneck"), not SKU (not "br-001") in any
customer-facing output. The lh-005 fanny-pack hallucination incident traces directly to skipping
the catalog. This rule is non-negotiable and overrides any claim in session memory.

---

## The Engine — Elite Studio social venture

The branch is powered by the deep-wired **social venture** in Elite Studio. Its publisher node
runs the live `SocialMediaAgent` (free, template-based brand-voice posts); graphics
(`CreativeAgent`) and strategy (`MarketingAgent`) are wired but cost-gated.

```bash
python -m skyyrose.elite_studio.ventures.social info     # manifest
python -m skyyrose.elite_studio.ventures.social agents   # bound agents + wiring
python -m skyyrose.elite_studio.ventures.social smoke --sku br-001   # real posts, free
```
```python
from agents.social_media_agent import SocialMediaAgent
agent = SocialMediaAgent()
post = agent.generate_post("br-001", "instagram", "product_launch")
print(post.caption, post.hashtags)   # brand-voice seed every social skill builds on
```

Agent surface (all real): `generate_post(sku, platform, content_type)` ·
`generate_campaign(...)` · `get_analytics()` · `get_collection_context(collection)` ·
`get_platform_config(platform)`. Platforms: instagram, tiktok, twitter, facebook.
Content types: product_launch, collection_drop, behind_scenes, lifestyle, engagement.

> **STOP-AND-SHOW required** before any action that posts to live accounts, triggers a Klaviyo
> send, executes a WooCommerce write, or uploads media. Show the exact action, platform, content
> hash, and any cost — then wait for explicit `y`/`yes`.

---

## Skill directory — route to the right specialist

### Content formats (what you post)
| Skill | Use when |
|-------|----------|
| `skyyrose-social-instagram-carousel` | Swipeable IG carousel (launch, styling, collection story) |
| `skyyrose-social-tiktok-script` | Frame-by-frame TikTok/Reels script |
| `skyyrose-social-short-form-video-plan` | Multi-week short-form video calendar + batch sessions |
| `skyyrose-social-twitter-thread` | X thread (brand story, drop, founder POV) |
| `skyyrose-social-thread-hook-writer` | Hook variants + scoring for any thread/post |
| `skyyrose-social-meme-content-brief` | On-brand meme concepts (engagement register) |

### Strategy & planning (what to do)
| Skill | Use when |
|-------|----------|
| `skyyrose-social-social-media-strategy` | Pillars, channel mix, 90-day roadmap, repurposing flow |
| `skyyrose-social-social-media-calendar` | 30-day calendar, weekly rhythm, monthly arcs |
| `skyyrose-social-social-media-audit` | Score current accounts incl. brand-canon compliance |
| `skyyrose-social-hashtag-strategy` | Branded + collection + niche hashtag sets per platform |
| `skyyrose-social-youtube-strategy` | YouTube channel positioning + Shorts pipeline |
| `skyyrose-social-pinterest-strategy` | Boards, Rich Pins, keyword formula |
| `skyyrose-social-reddit-strategy` | Corey-as-person community participation (90/10 rule) |

### Community & policy (how the audience is run)
| Skill | Use when |
|-------|----------|
| `skyyrose-social-community-launch` | Stand up the Discord/community space |
| `skyyrose-social-community-moderation` | Moderation tiers, AutoMod, escalation |
| `skyyrose-social-platform-community-guidelines` | Public-facing community guidelines doc |
| `skyyrose-social-social-media-policy` | Internal social governance + approval workflow |
| `skyyrose-social-social-listening-plan` | Keyword/hashtag monitoring + intel reporting |
| `skyyrose-social-crisis-comms` | Severity-tiered crisis response runbook |

### Influencer & PR (who amplifies)
| Skill | Use when |
|-------|----------|
| `skyyrose-social-influencer-campaign-brief` | Brief doc for a paid creator campaign |
| `skyyrose-social-influencer-outreach` | DM/email outreach sequence + tracker |
| `skyyrose-social-pr-pitch` | Sub-200-word press pitch + follow-up |
| `skyyrose-social-media-kit` | Press/partner media kit document |
| `skyyrose-social-co-marketing-plan` | Brand-to-brand co-marketing partnership |

### Visual briefs (how it looks)
| Skill | Use when |
|-------|----------|
| `skyyrose-social-brand-photography-brief` | Lifestyle/campaign/founder shoot brief |
| `skyyrose-social-product-photography-brief` | Garment-centric e-commerce shoot brief |
| `skyyrose-social-social-media-graphics` | Per-platform graphic specs + canvas sizes |

---

## How the pieces fit

```
brand-guardrails.md  ← canon every skill obeys
skyyrose-brand-dna   ← brand definition (wrong entry point? go here)
        │
skyyrose-catalog.csv + per-SKU dossiers  ← product facts (canonical, never memory)
        │
skyyrose-content-engine (this hub)  → routes to ↓
        │
27 skyyrose-social-* skills  ← author the deliverables
        │
Elite Studio social venture  ← SocialMediaAgent produces the brand-voice seed
        │
skyyrose.co / platforms  ← published
```

**Rule:** every platform gets a native adaptation — never cross-post identical content. Each
skill above carries its own Implementation/Artifact spec, real worked example, anti-patterns,
and recovery steps. When in doubt about voice, return to `brand-guardrails.md`.
When in doubt about brand identity vs. social execution, go to `skyyrose-brand-dna`.
