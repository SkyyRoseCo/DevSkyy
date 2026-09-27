---
name: skyyrose-influencer-growth
description: >
  Full creator-program lifecycle for SkyyRose — from discovery profiling and personalized
  outreach (DM <150 words + email with subject) through a 3-touch follow-up sequence
  (day 0 / day 5 / day 15, hard stop), compensation tiers (nano gifting+affiliate through
  macro flat+usage), collab agreement outline, campaign brief, content approval workflow
  (max 2 rounds / 48 h turnaround), performance tracking (unique code + UTM), post-campaign
  analytics (day-7 screenshot), and anti-pattern recovery. Trigger phrases: influencer
  program, creator partnership, outreach, collab brief, ambassador, gifting, creator tier,
  FTC, influencer campaign, creator program, partnership pitch, DM pitch, micro-influencer,
  nano-influencer, mid-tier, macro, affiliate code, collab agreement, campaign brief,
  go-live, approval workflow, post-campaign analytics, Oakland creator, Bay Area creator,
  streetwear partnership.
allowed-tools: Read Write Edit Glob
---

# SkyyRose — Influencer Growth (Full Creator-Program Lifecycle)

## When to Use This Skill

- Building or running the SkyyRose creator program end-to-end (discovery → brief → payment → analytics)
- Writing a personalized DM or email pitch for a specific creator
- Structuring compensation for any tier (nano through macro)
- Drafting follow-up sequences, collab agreement outlines, or full campaign briefs
- Setting up tracking (unique codes, UTM links) and post-campaign analytics
- Refreshing or recovering a stalled or mishandled creator relationship

**Supersedes** both `skyyrose-social-influencer-outreach` and `skyyrose-social-influencer-campaign-brief`. Those skills remain for focused one-step tasks; this skill covers the full lifecycle in a single session.

---

## Section 1 — Brand Canon Gate

All influencer work must pass these guardrails before any copy is produced. These are non-negotiable.

### Tagline
`` — verbatim, with period. Never paraphrased as "luxury streetwear from Oakland" or any other form.

### Collection Voice Isolation
Each collection has its own emotional register. **Never cross-attribute.**

| Collection | Accent | Register | Locked Phrase |
|------------|--------|----------|---------------|
| Black Rose | Silver `#C0C0C0` | Armor, defiant elegance, concrete answering back | "You already stood up." |
| Love Hurts | Crimson `#DC143C` | Bloodline, raw romance, the ones who loved hardest | "Bloodline that raised me." |
| Signature | Gold `#D4AF37` | West Coast luxury, earned standard, worldwide but Oakland-rooted | "Stay golden." |
| Kids Capsule | Rose Gold `#B76E79` | Little royalty, tender pride, generational | "Little royalty." |

If a creator brief is for Black Rose, "bloodline" language is forbidden. If it is for Love Hurts, "armor" language is forbidden. Each collection is its own world.

### Product Naming
Always use the product's **full name** as it appears in the canonical catalog. Never use a SKU (br-001, lh-002, etc.) in creator-facing copy. SKU-first referencing causes product conflations and looks unprofessional outside the internal team.

> **Canonical source:** `wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv` + per-SKU dossier files. Resolve product name, price, and collection from that source — never from memory, never invented.

### Hero Lockup Rule
The collection name in any hero position (video title card, Story text, Reel opening frame) **must be the official lockup PNG asset** supplied from the brand asset pack — never type-rendered using live fonts. Collections have lockup images in `assets/images/hero-overlays/` (Black Rose, Love Hurts, Signature) and `assets/images/logos/` (Kids Capsule). The creator does not compose the collection name in their editing app.

### Visual Reference Set — The Five
Kith, Oaklandish, Culture Kings, Fear of God, Palm Angels. **Never European luxury house lineage** (Bottega, Numéro, Hedi Slimane, Rick Owens, 032c, Acne, Givenchy by Tisci). Wrong brand DNA.

### Hard Rules (no exceptions)
- No urgency-timer manipulation. Limited availability is stated as **fact** ("limited to pre-order," "250 made"), never a fake ticking clock.
- No cross-sell or related-products inside influencer deliverables. The garment is the protagonist.
- No more than 3 follow-up touches. Hard stop. Revisit in 90 days.
- FTC #ad or #sponsored disclosure is mandatory on every paid piece. #sp or #collab alone does not satisfy FTC guidance.
- Maximum 2 approval rounds per deliverable. If messaging is wrong after round 2, the brief was under-specified.
- Oakland anchor preferred when the creator has Bay Area geography; national reach is acceptable.

---

## Section 2 — Inputs & Gates

### Required Inputs — Confirm All Before Any Copy

| Input | Confirm With | Default |
|-------|-------------|---------|
| **Collection** | "Which collection? (Black Rose / Love Hurts / Signature / Kids Capsule)" | No default — must be confirmed |
| **Product name** | "Which product by name?" — resolve from catalog CSV | No default — read from catalog |
| **Creator handle** | "Platform + handle (e.g., @handle on Instagram)" | No default |
| **Creator tier** | "Nano 1K-10K / micro 10K-100K / mid 100K-500K / macro 500K+?" | Micro (10K-100K) |
| **Outreach channel** | "DM (IG / TikTok) or email?" | Instagram DM |
| **Campaign goal** | "Awareness / pre-order sales / drop sellout / UGC library?" | Pre-order sales |
| **Compensation model** | "Gifting only / flat fee / product + affiliate?" | Product + affiliate |
| **Go-live window** | "Drop date or campaign window?" | Within 3 weeks of product delivery |
| **Budget per creator** | "Approved spend ceiling?" | Tier-based ranges in Section 4 |

**GATE: Do not generate any pitch copy, brief, or agreement text until collection, product name (from catalog), and creator handle are confirmed. Do not invent product details.**

---

## Section 3 — Creator Targeting Profile

Build this profile before writing a single word of pitch copy. The outreach quality depends entirely on the depth of this research.

```
Creator: [Handle]
Platform: [Instagram / TikTok / YouTube / Multi]
Follower count: [Number]
Engagement rate: [X.X%]
  → Floor: 3.0% for nano/micro
  → Mid/macro: verify via HypeAuditor, Social Blade, or platform media kit
Content niche: [Streetwear / Bay Area lifestyle / Black culture / sneakers / skate / music / etc.]
Geography: [Oakland / SF Bay Area / LA / National / International]
Oakland/Bay Area anchor: [Yes / No / Partial — e.g., based in LA, shoots Bay Area content]
Specific content reference: [REQUIRED — real post, reel, or video title/date that resonates]
  → Must be a GENUINE, SPECIFIC piece of content the creator actually made
  → Not "your content in general" — that reads as mass-blast spam
Why their audience fits SkyyRose: [Specific reason tied to their niche + the collection's register]
Audience demographic match: [Bay Area 18-35 / Black streetwear consumers / style-forward / etc.]
Prior brand deals: [List if visible — check for competitor exclusivity conflicts]
Red flags: [Purchased followers / engagement pod signs / cultural mismatch / exclusivity conflict]
```

### Targeting Criteria Summary

| Signal | Minimum Bar | Preferred |
|--------|-------------|-----------|
| Engagement rate (nano/micro) | 3.0% | 4.5%+ |
| Engagement rate (mid/macro) | 1.5% | 2.5%+ |
| Niche alignment | Streetwear, Black culture, Bay Area lifestyle | Oakland-rooted, luxury-meets-concrete lane |
| Geographic anchor | National reach acceptable | Oakland / Bay Area preferred |
| Authentic voice | Genuine, specific, unhurried | Founder-peer energy — not hype-merchant |
| Content ref available | Mandatory | Specific reel/post from last 90 days |

**Oakland-first:** When two creators are otherwise equivalent, prioritize the one rooted in Oakland. SkyyRose's origin story is specific — creators who understand that geography sell the brand without being coached.

**Nano is not lesser.** An Oakland-rooted nano creator with 4K engaged local followers can outperform a 150K lifestyle macro at 0.6% engagement for a collection drop. Lead with culture fit, not follower count.

---

## Section 4 — Compensation Structure

Select the model matching the creator's tier and campaign goal. These are SkyyRose standard ranges — adjust against your CPA ceiling (see Section 9) before committing.

| Creator Tier | Follower Range | Recommended Model | Typical SkyyRose Range |
|-------------|---------------|------------------|----------------------|
| **Nano** | 1K – 10K | Product gifting + 15-20% affiliate commission | Product value $50-120 + commission |
| **Micro** | 10K – 100K | Product + flat fee + 15% affiliate commission | $200-$800 flat + product + 15% commission |
| **Mid** | 100K – 500K | Flat fee + product (no commission required) | $800-$3,500 per primary deliverable + product |
| **Macro** | 500K+ | Flat fee + product + usage rights negotiation | $3,500-$15,000+ per deliverable + negotiated usage |

### Affiliate Code System
- **Naming convention:** `[CREATORNAME][DISCOUNT]` — e.g., `MARCUS15`, `BAYAREA15`, `TOWN15`
- **Discount:** 15% off for the creator's audience (this is genuine value, not just a tracking mechanism)
- **Tracking platform:** Rewardful or the WooCommerce affiliate plugin (resolve current config from `inc/woocommerce.php`)
- **Commission:** 15% on tracked sales; confirm rate in the collab outline before going live

### Payment Terms
- Nano/micro: Product ships on agreement confirmation; flat fee (if any) Net 30 on final content delivery
- Mid: 50% upfront on signed brief; 50% on final content delivery + analytics screenshot
- Macro: 50% upfront on signed agreement; 50% on go-live + analytics screenshot; usage rights documented in written contract

### Usage Rights — Paid Amplification Gate
> **STOP-AND-SHOW required before authorizing paid amplification** (Spark Ads / Meta whitelisting / TikTok Spark) — these involve spend. Show creator handle, platform, estimated CPM/budget, and get explicit `y` before enabling.

---

## Section 5 — Initial Outreach Pitch

### DM Version (under 150 words)

The structure is fixed. Every element has a purpose. Do not reorder.

```
Hey [First Name],

[Specific post or video reference — one genuine sentence on why it resonated and why
it connects to SkyyRose's lane. Reference Oakland, Bay Area street culture, or craft
if applicable. Never "love your content!" — name the actual piece.]

I'm Corey, founder of SkyyRose — luxury Oakland streetwear. ""
[One-sentence product description: what it is, what it's made of, who it's for.]

I think your audience would connect with [Product Name from catalog] — [one specific reason
tied to their content and the collection's emotional register — not generic "it's dope"].

Here's what I had in mind:
- [Product Name] shipped to you — yours to keep
- [Compensation: flat fee, or X% affiliate commission on your unique code]
- Full creative control — no script, your voice

No pressure at all. If this sounds interesting, DM back and we can talk details.

Corey Foster
skyyrose.co
```

### Email Version

Adds subject line and expands lightly. Keep it under 200 words.

```
Subject: [Something specific — never "collab opportunity" or "partnership inquiry"]
         Examples: "[Product Name] + your [specific content series]"
                   "Re: your [reel/post title] — SkyyRose x [Handle]"

[Same structure as DM — specific reference → founder intro + tagline →
one-product rationale → what's in it → low-pressure close]

Signature:
Corey Foster
Founder, SkyyRose
skyyrose.co | @skyyroseco
```

### Pitch Voice Rules
- Reference ONE specific piece of content — not "your feed" or "your aesthetic"
- Oakland / Bay Area anchor when the creator has that geography
- One product, one collection — do not list the catalog
- Founder voice: direct, Oakland-earned, unhurried. No "I've been a HUGE fan forever!!" energy
- Pitch answers "what's in it for them" before asking for anything
- Deliverables language is casual at this stage — "a Reel, a Story mention, or whatever fits your content"

---

## Section 6 — Follow-Up Sequence

Three touches. Hard stop. No exceptions.

### Touch 1 — Day 0: Initial Pitch
Send via agreed channel (DM or email). Log send date in tracker.

### Touch 2 — Day 5: Soft Bump

```
Hey [Name] — just following up in case this got buried. Know the inbox is wild.

Quick recap: I'd love to send you the [Product Name] and explore a collab. Totally
flexible on format — a Reel, a Story mention, or just an honest post if you like the
piece. Your call on how it fits your content.

Either way, keep building. — Corey
```

### Touch 3 — Day 15: Final Touch

```
Last message from me on this — I respect your time. If the timing doesn't work,
no worries at all.

If you're ever open to a SkyyRose collab down the line, hit me at skyyroseco@gmail.com
anytime.

— Corey
```

### HARD STOP after Touch 3
- Mark status as `not_now` in the tracker
- Set a 90-day revisit flag
- Do not send a 4th message under any circumstances — it damages the brand's standing in that creator's community
- At 90-day revisit: if the creator has posted content clearly in SkyyRose's lane since the original outreach, that's your natural re-entry point. Be genuine about the specific thing they made. Do not reference the prior sequence unless they do.

---

## Section 7 — Collab Agreement Outline

For nano/micro, DM confirmation or email reply is sufficient. For mid/macro, use a signed document. This outline covers all tiers — adapt formality to tier.

```
## SkyyRose x [Creator Handle] — Collab Outline

Date: [ISO date]
Collection: [Collection name]
Product: [Product name — from catalog, never SKU]

**Deliverables**
[Quantity, type, platform — e.g., "1 Instagram Reel (20-30s) + 3 Stories (9:16, 3-5 frames)"]

**Go-Live Window**
[Start date] — [End date]
Content must not go live before written brand approval.

**Content Approval**
- Creator submits draft (raw cut + proposed caption) by [date]
- SkyyRose provides feedback within 48 hours
- Maximum 2 rounds of revisions
- Revisions limited to: brand canon accuracy, FTC disclosure, messaging guardrails
- Brand will NOT request changes to creator style, editing cadence, or authentic voice
- Final approval is written confirmation via [email / DM]

**Compensation**
- Product: [Product name] — shipped, creator keeps. Value: $[amount]
- Flat fee: $[amount] (if applicable) | Payment: [50% upfront / 50% on delivery] or [Net 30 on delivery]
- Affiliate commission: [X%] on tracked sales via unique code [CREATOR_CODE]

**FTC Disclosure (mandatory)**
Creator includes #ad or #sponsored in all paid content — in the caption and, for video,
as a verbal disclosure at the start AND as on-screen text. #sp or #collab alone does not
satisfy FTC guidance (see Section 12 — Regulatory References). This is non-negotiable.

**Usage Rights**
- Organic repost by SkyyRose: Yes, for [X months] from go-live, with creator credit
- Paid amplification (Spark Ads / Meta whitelisting): [Yes / No] — additional fee applies if yes
- Website or email use: [Yes / No]
- Third-party licensing: Requires separate written agreement

**Exclusivity**
No competing streetwear brand content for [X days] after go-live.
[Nano/micro: 7-14 days | Mid: 14-30 days | Macro: 30-60 days, negotiated]

**Affiliate Code**
Unique code: [CREATOR_CODE] — [X%] off for their audience, tracked for commission.
Creator may not share the code outside their own channels without written permission.

**California Provisions (CA creators only)**
- Model release: Creator grants SkyyRose rights to use their likeness in reposted content
  per California Civil Code § 3344.
- Written contract required for CA creators compensated more than $250 (AB 2496 — effective
  January 1, 2024). This outline serves as that written agreement when signed by both parties.
```

---

## Section 8 — Campaign Brief

This is the full operational document sent after the creator confirms. Replaces the collab outline for mid/macro; supplements it for nano/micro.

---

### Brief Header

```
## SkyyRose x [Creator Handle] — Campaign Brief

Collection: [Black Rose / Love Hurts / Signature / Kids Capsule]
Product(s): [Product names — from catalog]
Campaign dates: [Start date] — [End date]
Content go-live window: [Date range]
Brief submitted: [Date]
```

---

### Campaign Objective

1-2 sentences. Tied to the collection's emotional register — not generic "brand awareness."

```
Example (Black Rose drop):
"Drive pre-order conversions for the Black Rose Sherpa Jacket by placing the garment
in real Oakland street context — armor on. The goal is 50 pre-orders attributed to
your unique link in the first 72 hours of go-live."

Example (Signature launch):
"Build earned reach for the Signature Crewneck among Bay Area style-forward consumers
who buy in the luxury-meets-concrete lane. Primary metric: 300 unique UTM link clicks
in the first week."
```

---

### Target Audience

SkyyRose's audience for this brief:
- Black men and women 18-35 in the Bay Area and beyond who buy elevated streetwear
- Style-forward consumers who respond to craft and story, not hype
- Fans of Kith, Fear of God, Oaklandish, Culture Kings, Palm Angels — the luxury-meets-concrete lane

---

### Deliverables Table

| # | Type | Platform | Duration / Specs | Draft Due | Go-Live |
|---|------|----------|-----------------|-----------|---------|
| 1 | [Reel / TikTok / YouTube Short] | [Platform] | [Duration], 9:16 | [Date] | [Date] |
| 2 | [Story Set] | [Platform] | 3-5 frames, 9:16 | [Date] | [Date] |

**Content Specifications:**
- Aspect ratio: 9:16 (vertical) for all short-form
- Reel/TikTok duration: 15-30s; YouTube Shorts: 60s max
- Product must be visible and worn or held in at least one frame
- Caption must include: @skyyroseco, #SkyyRose, , FTC disclosure (#ad or #sponsored), unique tracking code
- **Hero lockup rule:** Do NOT type the collection name as live text — use the lockup PNG from the brand asset pack supplied below

---

### Collection Voice Block

**[Collection name] — Register and Tone**

```
Black Rose:
Register: Gothic luxury. Armor. Defiant elegance. "You already stood up."
The product is protection — not fashion. Shoot at dusk or dark. Silver accents catch light.
Texture is the story — waxed cotton, matte hardware, weight you feel.

Love Hurts:
Register: Street passion. The bloodline that raised me. Raw romance, crimson heat.
The product is an emotional statement — wear it like it means something.
Shoot in daylight or golden hour. Crimson pops against concrete.

Signature:
Register: West Coast luxury. The standard. "Stay golden." Worldwide but Oakland-rooted.
The product is aspirational and earned — not for everyone, but for the ones who get it.
Clean composition. Gold details in natural light. Unhurried, confident.

Kids Capsule:
Register: Little royalty. Tender pride. Generational.
Shoot with real kids — candid, joyful, grounded. Rose gold softness, not hard street energy.
The parent and child together is the story.
```

**Talking Points (pick 1-2, do not script — these are reference points, not lines to read):**
1. [Specific product detail — fabric, construction, silhouette, material sourcing]
2. [Oakland / Bay Area anchor, if appropriate to the collection and creator's geography]
3. [Pre-order or availability fact — stated plainly, no urgency-timer language]

**DO NOT Say or Show:**
- Any other brand names or competitor products
- Urgency-timer language ("only X hours left!", "selling out fast!") — state availability as fact: "limited to pre-order," "250 made"
- Cross-sells to other collections — this creator promotes ONE product, ONE story
- The collection name as live type — use the brand lockup image
- "collab" or "brand deal" as the framing — this is a partnership built on genuine fit

---

### Content Approval Workflow

```
Step 1 — Draft Submission
  Creator submits: raw cut + proposed caption
  Submit via: [Email / shared folder / IG DM thread]
  Draft due: [Date]

Step 2 — Brand Review (48 hours)
  SkyyRose reviews for: brand canon accuracy, FTC disclosure presence, messaging guardrails
  SkyyRose does NOT request changes to: creator style, editing cadence, authentic voice
  Feedback delivered by: [Date = Draft Due + 2 business days]

Step 3 — Revision (if needed, max 1 more round)
  Creator revises + resubmits within [X days]
  SkyyRose final review within 24 hours
  Maximum 2 rounds total — if messaging is fundamentally wrong at round 2,
  the brief was under-specified; revisit the collection voice block.

Step 4 — Final Approval
  Written confirmation (email or DM) before go-live
  No posting before written approval — this is a firm requirement

Step 5 — Go-Live
  Creator posts within approved window
  Creator sends SkyyRose a screenshot of the live post
```

---

### Compensation and Usage Rights

```
Compensation:
  Fee: [Amount, "product gifting only", or "product + X% affiliate commission"]
  Payment terms: [50% upfront on brief signature / 50% on delivery; or Net 30]
  Affiliate commission: [X%] on sales tracked via unique code [CREATOR_CODE]
  Product: [Item name — creator keeps]

Usage Rights:
  Organic repost by SkyyRose: Yes, for [X months] from go-live — with creator credit
  Paid amplification (Spark Ads / Meta whitelisting): [Yes / No] — additional fee if yes
  Website / email use: [Yes / No]
  Exclusivity: No competing streetwear brands for [X days] after go-live
```

---

### Platform Partnership Ad Labeling

For paid partnerships, platform-native disclosure labels are required **in addition to** #ad/#sponsored in the caption:

- **Instagram:** Use the "Paid Partnership" label (creator adds SkyyRose as brand partner in Creator Tools → Branded Content → Add Brand Partners before submitting draft). This enables partnership insights for SkyyRose and satisfies Meta's policy.
- **TikTok:** Creator marks as "Branded content" in the TikTok app (Settings → Creator tools → Branded content toggle). TikTok Creator Marketplace deals auto-generate the disclosure.
- **YouTube:** Creator enables the "Paid promotion" flag in YouTube Studio for the video. YouTube BrandConnect partnerships include this automatically.

These platform labels **supplement** #ad/#sponsored — they do not replace the caption disclosure.

---

### Brand Asset Pack (supplied by SkyyRose)

- Collection lockup PNG (hero overlay, transparent background) — for the title card rule
- Brand logo PNG (white on transparent)
- Hashtag reference card (#SkyyRose, , collection-specific hashtags)
- Product photography — hi-res, for reference or B-roll backdrop
- Font reference card (Archivo for headings — all collections, Hanken Grotesk for body, Anton for UI labels, Cinzel as optional engraved-caps accent) — for captions/graphics if creator designs overlays

---

## Section 9 — Tracking & KPIs

### UTM Link Template

```
https://skyyrose.co/[product-slug]?utm_source=[creator-handle-no-@]&utm_medium=influencer&utm_campaign=[collection-slug]

Example:
https://skyyrose.co/black-rose-sherpa-jacket?utm_source=marcus_town&utm_medium=influencer&utm_campaign=black-rose
```

Use a URL shortener (e.g., bit.ly branded link) for caption use — UTM strings are unwieldy in captions and Stories.

### Unique Affiliate Code
Format: `[CREATORNAME][DISCOUNT]` — e.g., `MARCUS15`, `TOWN15`, `BAYAREA15`
Track via: Rewardful or WooCommerce affiliate plugin
Creator's audience discount: 15% off (real value, not just tracking)

### KPI Table

| Metric | Target | Source |
|--------|--------|--------|
| Reach | {operator-supplied} impressions | Platform analytics |
| Engagement rate | >{operator-supplied}% | Likes + comments ÷ reach |
| Link clicks | {operator-supplied} unique clicks | UTM / Google Analytics |
| Conversions (pre-orders / sales) | {operator-supplied} | WooCommerce + affiliate platform |
| Cost per acquisition (CPA) ceiling | <${operator-supplied} | Total cost ÷ conversions |
| Affiliate revenue generated | ${operator-supplied} | Affiliate platform |

**Set these targets before the campaign launches.** "Good engagement" is not a KPI.

### Post-Campaign Analytics
- Creator sends analytics screenshot at **day 7** after go-live
- SkyyRose pulls UTM / WooCommerce conversion data at day 7
- Reconcile: reach, engagement, clicks, conversions, CPA
- If no analytics received by day 7: one follow-up. If still no response by day 10: collect what you can from public post metrics. Document reliability in the tracker for future decisions.
- CPA above ceiling: flag immediately; do not repeat this compensation model with this creator tier without adjusting targets or structure

---

## Section 10 — Product Shipment & Asset Pack

### Shipment

```
Product(s): [Product name — from catalog, never SKU]
Ship date: [Content deadline minus 10 business days — allow time to receive, try on, plan content]
Packaging: Standard SkyyRose branded box — creator may film unboxing if authentic to their content
Product value: $[amount] (creator keeps regardless of outcome)
Shipping address: Collected via [secure form link / encrypted DM]
```

**Timing note:** Nano/micro creators often have day-job schedules. Ship earlier than you think necessary — a delayed product is the most common reason campaigns miss go-live windows.

### Asset Pack Delivery

Deliver via a shared folder link (Google Drive, Dropbox, or similar) — not email attachments.

Contents:
1. Collection lockup PNG (hero overlay, transparent background, at least 2000px wide)
2. Brand logo PNG (white on transparent + dark on transparent variants)
3. Hashtag reference card (PNG, shareable for Stories) — includes required tags, FTC reminder
4. Product photography — hi-res JPEGs for reference or B-roll backdrop use
5. Font reference card — for caption/overlay graphics if creator designs their own
6. Brief summary card (1-page PDF) — the key rules at a glance: lockup rule, FTC, do-not-say list, go-live window, approval contact

---

## Section 11 — Outreach Tracker JSON Schema

Use this schema to track every creator in the pipeline. One JSON object per creator. Store in a JSON array in the project tracker file.

```json
{
  "creator_handle": "@handle",
  "platform": "instagram",
  "tier": "micro",
  "follower_count": 28400,
  "engagement_rate": 4.6,
  "collection": "black-rose",
  "product_name": "Black Rose Sherpa Jacket",
  "reference_post": "Exact post title or description — e.g., 'Your Oakland winter fits reel from Nov 2025'",
  "pitch_sent_date": "2026-06-01",
  "outreach_channel": "instagram_dm",
  "follow_up_1_date": "2026-06-06",
  "follow_up_2_date": "2026-06-16",
  "follow_up_3_sent": false,
  "status": "awaiting_response",
  "compensation_model": "product + 15% affiliate",
  "flat_fee": 0,
  "product_value": 85,
  "unique_code": "CREATOR15",
  "tracking_url": "https://skyyrose.co/black-rose-sherpa-jacket?utm_source=handle&utm_medium=influencer&utm_campaign=black-rose",
  "brief_sent_date": null,
  "go_live_window_start": null,
  "go_live_window_end": null,
  "deliverables": ["1x Reel", "3x Stories"],
  "approval_status": "pending_draft",
  "draft_due": null,
  "approved_date": null,
  "live_screenshot_received": false,
  "analytics_due": null,
  "analytics_received": false,
  "kpi_reach_target": null,
  "kpi_clicks_target": null,
  "kpi_conversions_target": 30,
  "kpi_cpa_ceiling": 25,
  "actual_reach": null,
  "actual_engagement_rate": null,
  "actual_clicks": null,
  "actual_conversions": null,
  "actual_cpa": null,
  "revisit_date": null,
  "notes": "Tone: direct, Oakland-peer energy. Not a fan pitch — founder-to-creator peer conversation.",
  "ca_creator": false,
  "ca_ab2496_contract_required": false,
  "ca_model_release_obtained": false
}
```

**Status values:** `identified` → `pitch_sent` → `follow_up_1` → `follow_up_2` → `not_now` → `interested` → `brief_sent` → `agreement_signed` → `product_shipped` → `draft_received` → `approved` → `live` → `analytics_received` → `complete` → `declined`

---

## Section 12 — Anti-Patterns & Recovery

### Anti-Patterns

**Outreach**
- **Mass-blast identical pitches.** The opener MUST reference something the creator actually made. Generic "love your content!" reads as spam and gets ignored.
- **Leading with the ask.** Never open with deliverables, fees, or requirements. The creator needs to see their value to SkyyRose first.
- **Listing multiple products or collections.** One product, one pitch. Listing the catalog signals vendor, not collaborator.
- **Referencing SKUs.** "We'd love to send you br-001" is meaningless outside the internal team.
- **Urgency-timer language in pitches.** "You'd be perfect for our launch happening THIS WEEK ONLY" signals desperation. State facts: "We're running a pre-order window through June 21."
- **Over-following up.** 3 touches total. After that you damage the brand's reputation in that creator's community.
- **Treating nano creators as lesser.** Oakland-rooted nano creators with 3K engaged local followers can outperform a 200K lifestyle macro at 0.6% engagement.

**Briefs and Agreements**
- **Scripting the creator's dialogue word-for-word.** Kills authenticity. Provide talking points, not a teleprompter.
- **Cross-attributing collection voices.** Black Rose brief must not contain "bloodline" language. Love Hurts brief must not contain "armor" language. Each collection is its own emotional register.
- **Allowing the creator to render the collection name as live type.** Lockup PNG is mandatory. Brief must supply the asset and explain the rule explicitly.
- **More than 2 revision rounds.** Over-revision erodes the creator relationship. If messaging is fundamentally wrong after round 2, the brief was under-specified — own that and rebuild the voice block before the next creator.
- **Vague KPIs.** "Good engagement" is not a KPI. Specify reach, engagement rate floor, click target, conversion target, and CPA ceiling before the campaign launches.
- **Omitting FTC disclosure from the deliverables spec.** Every paid partnership requires #ad or #sponsored — and for video, verbal + on-screen disclosure at the start. Non-negotiable.

**Tracking**
- **Shipping the product too late.** Nano/micro creators need lead time. Ship 10+ business days before the content deadline.
- **No post-campaign analytics follow-up.** The data belongs to SkyyRose as much as to the creator. Follow up at day 7, once more at day 10 if needed.

### Recovery Scenarios

| Scenario | Recovery Action |
|----------|----------------|
| Creator wants to show multiple products | Redirect — one product per campaign. If they want to style outfits, the featured product is the hero; other pieces stay unbranded. Do not bundle. |
| Creator counters with a higher rate | Run the math against your CPA ceiling before negotiating. If 15 conversions at $75 avg = $1,125 revenue, $600 flat + $0 commission may still be favorable. |
| Draft uses wrong collection voice or cross-attributes | Flag in round 1 with specific language — quote the guardrail and provide the correct register description. Do not just say "sounds off." |
| Creator posts before final approval | DM immediately. Document the violation. Add an explicit "no posting before written approval" clause with a hold-back payment mechanic in all future briefs with this creator. |
| No analytics sent after go-live | Follow up at day 7, once more at day 10. If still no response, collect public post metrics. Factor reliability into future partnership decisions. |
| No engagement data available for new creator | Request a media kit or Instagram Insights screenshot. If they cannot produce it, treat as nano-tier gifting offer only. |
| Creator's audience outside SkyyRose's market | Geographic mismatch (e.g., East Coast creator for a Bay Area drop) is manageable — SkyyRose ships nationally. Cultural mismatch (European luxury aesthetic, no streetwear alignment) is a disqualifier. Do not force a partnership because their numbers look good. |
| Creator refuses FTC disclosure | Non-starter. The partnership cannot proceed without #ad or #sponsored. Explain that this is a legal requirement, not a brand preference. If they still refuse, terminate the engagement. |
| No response after 3 touches | Mark `not_now`. 90-day revisit flag. Do not send a 4th message. |

---

## Regulatory References

**FTC Endorsement Guides (2023 Update)**
The Federal Trade Commission's *Guides Concerning the Use of Endorsements and Testimonials in Advertising* (16 C.F.R. Part 255), updated in 2023, require:
- Disclosure must be **clear and conspicuous** — not buried in hashtags, not below the fold, not in a list of 30 other hashtags.
- **#ad or #sponsored** are FTC-recognized disclosures. **#sp, #collab, or #partner alone do not satisfy the standard** — they are ambiguous to a general audience.
- **Video disclosure:** Must appear at the **start** of the video (not just the end), both as on-screen text and as a verbal disclosure.
- **Affiliate commission = material connection** — receiving a commission for driving sales is a material connection that requires disclosure, even if no flat fee is paid.
- Source: [ftc.gov — Endorsements, Influencers, and Reviews](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking)
- **Label:** Regulatory guidance — NOT sourced from Context7. Verify current FTC guidance at ftc.gov before advising on enforcement specifics.

**California — Model Release (Civil Code § 3344)**
California Civil Code § 3344 requires written consent to use a person's name, voice, photograph, or likeness for commercial purposes. For any SkyyRose content reposted from a creator's channel on paid or owned media, a model release (or equivalent clause in the collab agreement) is required for California-based creators. The collab agreement outline in Section 7 includes this clause.

**California — AB 2496 (effective January 1, 2024)**
California AB 2496 (now codified) requires a **written contract** for freelance creative work (including social media content creation) where the total compensation is **$250 or more** per engagement or over a 120-day period. For any California-based creator compensated at or above this threshold, the collab outline in Section 7 constitutes that written agreement when signed by both parties. For macro deals, use a full contract reviewed by legal.

---

## Implementation Reference

```python
from agents.social_media_agent import SocialMediaAgent

agent = SocialMediaAgent()

# Load collection voice to inform pitch talking points and brief messaging block
ctx = agent.get_collection_context("black-rose")
print(ctx["mood"])        # register the creator must stay inside
print(ctx["hashtags"])    # collection hashtag set for brief required-tags + FTC section

# A product blurb in the right voice for the pitch hook or brief messaging block
post = agent.generate_post("br-001", "instagram", "product_launch")
print(post.caption)       # mine for one specific detail to personalize outreach
# NOTE: br-001 is an internal SKU — use the product's catalog name in any creator-facing copy
```

```bash
# Inspect the social venture surface behind the campaign:
python -m skyyrose.elite_studio.ventures.social agents

# Check tracker status:
python -m skyyrose.elite_studio.ventures.social status
```

---

## Full-Lifecycle Example: Black Rose Drop x Oakland Creator

**Scenario:** Oakland-based micro-influencer, 22K Instagram followers, streetwear and sneaker niche, 4.8% engagement rate.

**Creator Profile:**
- Handle: @townstyle_oak | Platform: Instagram | Tier: Micro
- Follower count: 22,000 | Engagement rate: 4.8%
- Niche: Oakland streetwear, Bay Area street photography
- Geographic anchor: Oakland (born and raised)
- Content reference: "December Oakland Fits — waxed canvas week" Reel, posted 2025-12-12
- Audience fit: Black men 18-35, Bay Area style-forward, Kith/FOG lane

**Initial DM:**

```
Hey Jasmine,

Your "December Oakland Fits — waxed canvas week" reel was exactly the kind of texture
story SkyyRose lives in — the way you showed how the canvas aged on the walk from the
Lake to Fruitvale, that's the lane we're building in.

I'm Corey, founder of SkyyRose — luxury Oakland streetwear. ""
We just launched the Black Rose Sherpa Jacket: waxed cotton outer, sherpa lining, matte
black hardware, built for Oakland winter.

I think your audience would feel that jacket the same way you felt that canvas — it's
armor, not fashion.

Here's what I had in mind:
- Black Rose Sherpa Jacket shipped to you — yours to keep
- 15% affiliate commission on tracked sales through your unique code
- Full creative control — no script, just the jacket and your Oakland lens

No pressure. If this sounds interesting, DM back.

Corey Foster
skyyrose.co
```

**Compensation:** Black Rose Sherpa Jacket (product) + 15% affiliate commission via `JASMINE15`

**Brief (key points):**
- Deliverables: 1 Instagram Reel (20-30s, 9:16) + 4 Stories (product close-up / wearing / tracking link sticker / CTA)
- Collection voice: Black Rose — armor, twilight setting, defiant energy. "You already stood up." Shoot dark; sherpa texture catches ambient light.
- Key talking point: Waxed cotton outer, sherpa lining, matte black hardware — Oakland winter gear.
- Do NOT say: "Only X left!" / Do not cross-sell Signature or Love Hurts pieces
- Lockup rule: Collection name must use the Black Rose hero overlay PNG — not live type
- Draft due: June 8 | Brand review by June 10 | Go-live: June 14
- KPIs: 40 pre-order conversions in 72h of go-live, CPA ceiling $22, UTM clicks target 200

**Tracker entry:** Status `brief_sent`, `ca_creator: true`, `ca_ab2496_contract_required: true` (compensation > $250)
