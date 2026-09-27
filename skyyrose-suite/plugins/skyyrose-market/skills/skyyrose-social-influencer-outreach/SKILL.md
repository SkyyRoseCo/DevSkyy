---
name: skyyrose-social-influencer-outreach
description: "Produces personalized SkyyRose influencer pitch DMs and emails, a 3-touch follow-up sequence, compensation structure, and a lightweight collab agreement outline for Bay Area and streetwear-adjacent creators."
allowed-tools: Read Write Edit Glob
---

# SkyyRose Social — Influencer Outreach

## When to Use This Skill

- Reaching out cold to a Bay Area, Black culture, or streetwear creator for the first time
- Writing a personalized DM or email pitch to propose a SkyyRose collection partnership
- Building a follow-up sequence after an initial pitch
- Structuring compensation (product gifting, flat fee, affiliate) for a specific creator tier
- Drafting a lightweight collab agreement outline before the full brief is sent

**DO NOT** use this for the detailed campaign brief (use `skyyrose-social-influencer-campaign-brief` after the creator says yes) or for vetting/finding creators. This skill produces outreach materials for creators already identified.

---

## Brand Canon (non-negotiable)

No tagline is authorized. Do not restore retired slogans.
- **Lead with the creator's value** — the pitch must answer "what's in it for them" before asking for anything. SkyyRose is the subject of the pitch, but the creator is the audience for it.
- **Products by NAME, not SKU** — "Black Rose Crewneck", not "br-001". Always identify the product you're proposing by its full name.
- **No mass-blast identical pitches** — every outreach references something specific the creator actually made.
- **Founder voice register** — Corey's pitch style is direct, Oakland-earned, unhurried. No "I've been a HUGE fan forever!!" energy. Genuine, specific, confident.
- **Maximum 3 follow-up touches** — do not spam.

Full canon: `../skyyrose-content-engine/brand-guardrails.md`

---

## Phase 1: Define Campaign Parameters

### Required Inputs

| Input | What to Confirm | Default |
|-------|----------------|---------|
| **Collection** | "Which collection? (Black Rose / Love Hurts / Signature / Kids Capsule)" | No default |
| **Product name** | "Which specific product by name?" | No default — read from catalog |
| **Creator handle** | "Who is this pitch for? Platform + handle." | No default |
| **Creator tier** | "Nano 1K-10K, micro 10K-100K, mid 100K-500K, macro 500K+?" | Micro (10K-100K) |
| **Outreach platform** | "DM on Instagram/TikTok, or email?" | Instagram DM |
| **Budget or model** | "Product gifting only, flat fee, or product + affiliate?" | Product + affiliate |

**GATE: Confirm collection, product name, and creator handle before generating any pitch copy.**

> Product facts resolve from `wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv`.
> Never invent a product name, colorway, or price.

---

## Phase 2: Build Creator Targeting Profile

Before writing the pitch, answer these for the specific creator:

```
Creator: [Handle]
Platform: [Instagram / TikTok / YouTube]
Follower count: [Number]
Engagement rate: [X%] (target 3%+ for nano/micro)
Content niche: [Streetwear / Bay Area lifestyle / Black culture / sneakers / etc.]
Geography: [Oakland / SF Bay Area / LA / National]
Specific content piece to reference: [Real post, video, or series title — must be genuine]
Why their audience fits SkyyRose: [Specific reason tied to their niche and our collection]
```

**Engagement rate minimum:** 3% for nano/micro. For mid/macro, check third-party tools (HypeAuditor, Social Blade) if platform data is unavailable.

---

## Phase 3: Create Outreach Sequence

### Initial Pitch — DM or Email

```
[DM version — under 150 words]

Subject (email only): [Something specific, not "collab opportunity"]

Hey [Name],

[Specific post or video title] — [one genuine sentence on why it resonated and why it's relevant to SkyyRose's lane. Reference Oakland, Bay Area street culture, or craft if applicable.]

I'm Corey, founder of SkyyRose — luxury Oakland streetwear. "" We make [one-sentence product description] for [the audience you're describing: Bay Area style-forward people, Black streetwear consumers, etc.].

I think your audience would connect with [Product Name] — [one specific reason tied to their content and the collection's register, not generic "it's dope"].

Here's what I had in mind:
- [Product delivered to you — keep it]
- [Compensation: flat fee, or X% affiliate commission on your unique code]
- Full creative control — no script, your voice

No pressure at all. If this sounds interesting, DM back or reply here and we can talk details.

Corey Foster
skyyrose.co
```

**Key rules for the opener:**
- Reference ONE specific piece of content — not "your content in general"
- Oakland or Bay Area anchor is preferred when the creator has that geography
- Pitch one product, one collection — do not list the whole catalog

---

### Follow-Up 1 — 5 days after initial pitch

```
[DM / Reply thread]

Hey [Name] — just following up in case this got buried. Know the inbox is wild.

Quick recap: I'd love to send you the [Product Name] and explore a collab. Totally flexible on format — a Reel, a Story mention, or just an honest post if you like the piece. Your call on how it fits your content.

Either way, keep building. — Corey
```

---

### Follow-Up 2 — 10 days after Follow-Up 1 (final touch)

```
[DM / Reply thread]

Last message from me on this — I respect your time. If the timing doesn't work, no worries at all.

If you're ever open to a SkyyRose collab down the line, hit me at skyyroseco@gmail.com anytime.

— Corey
```

**STOP after 3 touches.** No exceptions. Mark as "not now" and revisit in 90 days.

---

## Phase 4: Structure Compensation

Select one model based on creator tier and campaign goal:

| Creator Tier | Recommended Model | SkyyRose Typical Range |
|-------------|------------------|----------------------|
| Nano (1K-10K) | Product gifting + 15-20% affiliate commission | Product value $50-120 + commission |
| Micro (10K-100K) | Product + flat fee + affiliate | $200-$800 + product + 15% commission |
| Mid (100K-500K) | Flat fee + product | $800-$3,500 per deliverable |
| Macro (500K+) | Flat fee + usage rights negotiation | $3,500-$15,000+ per deliverable |

**Affiliate commission:** Use a unique discount code (e.g., CREATOR15 = 15% off). Tracked via Rewardful or the WooCommerce affiliate plugin. Creator's audience gets a real discount — this is value, not just tracking.

---

## Phase 5: Collab Agreement Outline

Before the full brief is sent, confirm these terms in writing (DM confirmation or email is sufficient for nano/micro; a signed doc for mid/macro):

```
## SkyyRose x [Creator] — Collab Outline

**Product:** [Name] (shipped, creator keeps)
**Deliverables:** [Quantity, type, platform — e.g., "1 Instagram Reel + 3 Stories"]
**Go-live window:** [Date range]
**Content approval:** 1 round of brand feedback, max 48-hour turnaround
**Compensation:** [Product value] + [flat fee if any] + [X% affiliate commission]
**Payment:** [50% upfront / 50% on delivery, or Net 30]
**FTC disclosure:** Creator includes #ad or #sponsored in all paid content — mandatory
**Usage rights:** SkyyRose may organically repost with creator credit for [X months]
**Exclusivity:** No competing streetwear brand content for [X days] after go-live
**Affiliate code:** [CREATOR_CODE] — 15% off for their audience, tracked for commission
```

---

## Implementation

```python
from agents.social_media_agent import SocialMediaAgent

agent = SocialMediaAgent()

# Load Signature collection voice to inform pitch talking points
ctx = agent.get_collection_context("signature")
print(ctx["mood"])        # register to strike in the DM/email (never generic flattery)
print(ctx["hashtags"])    # hashtag set for the agreement's FTC disclosure section

# A product blurb in the right voice for the pitch's hook
post = agent.generate_post("sg-001", "instagram", "product_launch")
print(post.caption)       # mine for one specific detail to personalize the outreach
```

```bash
# Inspect the social venture surface behind the outreach:
python -m skyyrose.elite_studio.ventures.social status
```

### Outreach Tracker Schema

```json
{
  "creator_handle": "@bayareastreetwear",
  "platform": "instagram",
  "tier": "micro",
  "follower_count": 28400,
  "engagement_rate": 4.6,
  "collection": "signature",
  "product_name": "Signature Crewneck",
  "reference_post": "Your 'Oakland to LA' fit transition reel from April",
  "pitch_sent_date": "2026-06-01",
  "follow_up_1_date": "2026-06-06",
  "follow_up_2_date": "2026-06-16",
  "status": "awaiting_response",
  "compensation_model": "product + 15% affiliate",
  "unique_code": "BAYAREA15",
  "notes": "Tone: direct, Oakland-peer energy. Not a fan pitch — a founder-to-creator peer conversation."
}
```

---

## Example: Signature Line x Bay Area Streetwear Creator

**Scenario:** Micro-influencer in Oakland, 28K Instagram followers, 4.6% engagement rate. Posts West Coast fits and Bay Area street photography. Target product: Signature Crewneck.

**Initial DM:**

```
Hey Marcus,

Your "Oakland to LA" fit transition reel was clean — the way you documented
the difference in textures between the two cities is exactly the kind of visual
storytelling that fits where SkyyRose lives.

I'm Corey, founder of SkyyRose — luxury Oakland streetwear. "" We just dropped the Signature Crewneck: heavyweight fleece, tonal
embroidery, built for the Bay and wearable anywhere. West Coast luxury, no
European house required.

Here's what I had in mind:
- Signature Crewneck shipped to you — yours to keep
- 15% affiliate commission on tracked sales through your unique code
- Your format, your edit — no script from me

If it sounds interesting, DM back or hit me at skyyroseco@gmail.com.

Corey Foster
skyyrose.co
```

**Compensation:** Signature Crewneck (product) + 15% commission on affiliate sales via code MARCUS15

**Agreement outline:** 1 Instagram Reel + 2 Stories, go-live within 3 weeks of product delivery, 1 round of brand approval, organic repost rights for 6 months.

---

## Anti-Patterns

- **Mass-blast identical pitches** — the opener MUST reference something the creator actually made. Generic "love your content!" openers read as spam and get ignored.
- **Leading with the ask** — never open with deliverables, fees, or requirements. The creator needs to see their value to SkyyRose first.
- **Listing multiple products or collections** — one product, one pitch. If you list the whole catalog you look like a vendor, not a collaborator.
- **Referencing SKUs** — "we'd love to send you br-001" is unprofessional and meaningless outside the internal team. Always use the product's full name.
- **Urgency-timer language in pitches** — "you'd be perfect for our launch happening THIS WEEK ONLY" signals desperation, not partnership. State facts: "we're running a pre-order window through June 21."
- **Over-following up** — 3 touches total, maximum. After that you're damaging the relationship and the brand's reputation with that creator's community.
- **Scripting the creator** — the agreement outline says "full creative control." Mean it. Over-specifying in the pitch (before the brief stage) kills interest.
- **Treating nano creators as lesser** — Oakland-rooted nano creators with 3K engaged local followers can drive more real conversions than a 200K lifestyle macro with 0.8% engagement. Lead with culture fit, not follower count.

---

## Recovery

- **No response after 3 touches:** Mark as "not now." Add a 90-day revisit flag. Do not send a 4th message. If you see them post content that's clearly in SkyyRose's lane later, that's your next opening — be genuine about it.
- **Creator counters with a higher rate:** Evaluate against your CPA target. If a micro-influencer counters $600 for a product costing $85, run the math: if 15 conversions at $75 average = $1,125 revenue, $600 flat + $0 commission may still be favorable. Do not just say no without the math.
- **No engagement data available:** Request a media kit or screenshot of Instagram Insights. If they can't produce it, treat as a nano-tier gifting offer only.
- **Creator wants to post immediately without approval:** Clarify the approval requirement before committing to the partnership. It's non-negotiable for brand-safety reasons. If they won't agree, they are not the right partner for this campaign.
- **Creator's audience is outside SkyyRose's market:** Geographic mismatch (e.g., an East Coast creator for a Bay Area drop) is manageable — SkyyRose ships nationally. Cultural mismatch (e.g., European luxury aesthetic, no streetwear alignment) is a disqualifier. Do not force a partnership because their numbers look good.
