---
name: skyyrose-social-social-media-audit
description: "Runs a structured social media audit of SkyyRose's active platform presence — scoring profile optimization, content quality, consistency, engagement, and growth signals — then delivers a prioritized 30-day action plan."
allowed-tools: Read Write Edit Glob
---

# SkyyRose Social — Social Media Audit

## When to Use This Skill

- Evaluating SkyyRose's current Instagram, TikTok, Pinterest, or X presence before a strategy refresh
- Diagnosing why content effort isn't translating to skyyrose.co traffic or sales
- Getting a structured scorecard with ratings before a collection campaign
- Identifying profile optimization gaps before a major drop
- Preparing a quarterly social media report for the brand

**DO NOT** use this skill for:
- Creating new social content (use `skyyrose-social-social-media-calendar`, `skyyrose-social-instagram-carousel`)
- Running competitor analysis without auditing SkyyRose's own accounts first
- Analyzing paid ad performance — this audit covers organic presence only
- Accessing live platform analytics via API — this audit is based on user-reported data and publicly observable profile state

---

## Brand Canon (non-negotiable)

- **No tagline:** None is authorised (founder decision 2026-10-06). Any tagline appearing in a bio, pinned post, or highlight = flagged finding.
- **Collection voice discipline:** Audit whether collection-specific content uses the correct register. Black Rose = armor. Love Hurts = bloodline. Signature = the standard. Mixed attribution = flagged finding.
- **The Five visual references:** Audit whether visual direction aligns with Kith · Oaklandish · Culture Kings · Fear of God · Palm Angels. European luxury-house aesthetic in active content = flagged finding.
- **Product naming:** Are products named by name ("BLACK Rose Crewneck") or by SKU ("br-001") in public posts? SKU-first = customer-facing bug.
- **No urgency manipulation:** Any countdown timers, "🔥 DON'T MISS OUT" copy, or artificial scarcity in active posts = flagged finding.

Full canon: ../skyyrose-content-engine/brand-guardrails.md

---

## SkyyRose Platform Benchmarks

| Platform | Healthy Frequency | Good Engagement Rate | Primary Format | Audience |
|----------|------------------|---------------------|----------------|---------|
| Instagram | 4-5 feed + 3 Reels/week + daily Stories | 2-4% on feed, 3-5% on Reels | Reels, Carousels, Stories | Luxury streetwear 18-35, Black consumers |
| TikTok | 1-2x/day | 3-6% on videos | Short-form 15-30s | Streetwear discovery, 16-30 |
| Pinterest | 5-10 pins/day | 0.2-0.5% click-through | Product pins, lifestyle | Purchase-intent fashion search |
| X / Twitter | 1-2x/day | 0.5-1.5% per tweet | Text + image, threads | Founder voice, drop announcements |

---

## Step 1: Understand

Confirm these inputs before auditing:

1. **Active platforms** — which platforms have posted in the last 30 days?
2. **Current goal** — brand awareness, direct sales to skyyrose.co, community building, or active collection launch?
3. **Posting frequency** — how often per platform in the past 30 days?
4. **Self-assessment** — what does the founder or team think is working? What feels stuck?
5. **Recent drops** — any collection launches or pre-orders in the past 60 days that content should have supported?

```
Platform Checklist — confirm which are active:

| Platform  | Active? | Handle / URL |
|-----------|---------|-------------|
| Instagram |         | @skyyroseco  |
| TikTok    |         |              |
| Pinterest |         |              |
| X/Twitter |         |              |
| YouTube   |         |              |
```

**GATE: Do not proceed to Step 2 without at least one confirmed active platform and a stated or inferred goal.**

---

## Step 2: Audit

Score each active platform across 6 dimensions. Score: **Strong** / **Needs Work** / **Missing**.

### Dimension 1: Profile Optimization

| Element | What to Evaluate | Strong | Needs Work | Missing |
|---------|-----------------|--------|------------|---------|
| **Bio** | States brand identity + Oakland anchor. No tagline (none authorised). | Specific, benefit-driven, no tagline | Bio exists but vague or generic ("Luxury fashion brand") | Empty or no brand language |
| **Profile photo** | Brand logo or Corey — consistent across platforms | High-quality, consistent everywhere | Low-res or inconsistent between platforms | Default avatar |
| **Link** | Drives to skyyrose.co — product page or homepage with clear navigation | Link-in-bio tool with collection links or direct skyyrose.co URL | Link exists but lands on wrong page (admin, 404, old URL) | No link or broken |
| **Pinned / Highlights** | Best content or collection intro pinned. Highlight covers: per collection + Behind Studio + Orders | Curated, up to date, covers visible | Exists but disorganized or stale | None |
| **Handle consistency** | @skyyroseco or recognizable variation across all platforms | Identical or immediately recognizable everywhere | Variations that require searching | Completely different names |

### Dimension 2: Brand Canon Compliance

| Element | What to Evaluate | Strong | Needs Work | Missing |
|---------|-----------------|--------|------------|---------|
| **Collection voice accuracy** | Black Rose, Love Hurts, Signature content each use correct register | No cross-attribution; each post uses its collection's voice | Occasional voice bleed between collections | Voices mixed or absent |
| **Visual reference alignment** | Photography and aesthetic aligns with The Five, not European luxury | Matches Kith/Culture Kings/Fear of God energy | Mixed signals — some European luxury-house styling | Clearly off-brand (minimalist white-space European aesthetic) |
| **Product naming** | Customer-facing posts use product name, not SKU | "BLACK Rose Crewneck" consistently | Mix of names and SKUs | SKU-first throughout ("br-001 is dropping") |
| **No urgency manipulation** | No countdown timers, "🔥 DON'T MISS OUT," or artificial scarcity pressure | Scarcity stated as fact only | Some hype language in older posts | Active posts with urgency clock or fire-emoji manipulation |

### Dimension 3: Content Quality

| Element | What to Evaluate | Strong | Needs Work | Missing |
|---------|-----------------|--------|------------|---------|
| **Visual consistency** | Cohesive dark/moody palette per collection. Dark background `#0A0A0A`. Collection accents visible. | Immediately recognizable brand look | Somewhat consistent but no clear palette discipline | Random visuals, no cohesion |
| **Caption quality** | Hook in first line. Brand voice present. CTA at end. 150-300 words on IG Feed. | Strong hooks, brand-specific language, clear CTA | Captions exist but generic or no brand voice | Single emojis, no copy, or copy-paste generic text |
| **5-Pillar representation** | Brand Story, Product Showcase, Culture & Community, Lifestyle, Exclusivity all present | All 5 pillars visible in past 30 days | 2-3 pillars only | All promotional or all random |
| **Video hook quality** | First 1.5 seconds of Reels/TikToks stops scroll | Compelling visual or text hook within 1.5s | Hook is present but weak | No hook — product just appears from frame 1 |

### Dimension 4: Posting Consistency

| Element | What to Evaluate | Strong | Needs Work | Missing |
|---------|-----------------|--------|------------|---------|
| **Frequency** | Meets SkyyRose platform benchmark above | At or above benchmark | Regular but below benchmark | Sporadic — weeks of silence |
| **Gap discipline** | No gaps longer than 3 days on feed, 1 day on Stories | No extended gaps | Occasional 1-2 week gaps | Regular 3+ week disappearances |
| **Cadence signal** | Evidence of a posting plan vs. spontaneous | Consistent posting times, themed days | Some regularity but no clear system | Clearly reactive, no plan |

### Dimension 5: Engagement Health

| Element | What to Evaluate | Strong | Needs Work | Missing |
|---------|-----------------|--------|------------|---------|
| **Comment responses** | Replies to comments on own posts within 24h | Responds to most comments | Responds to some, ignores others | Never responds |
| **DM responsiveness** | Handles purchase inquiries and community DMs | Reports responding promptly | Slow or inconsistent | Ignores DMs |
| **Outbound engagement** | Engages with Oakland culture accounts, streetwear community, customers | Active commenter on relevant accounts | Occasional outbound | Posts and disappears |
| **CTAs present** | Every post includes a clear next step for the audience | Specific, relevant CTAs throughout | Generic "link in bio" on everything | No CTAs — audience never directed |

### Dimension 6: Growth Signals

| Element | What to Evaluate | Strong | Needs Work | Missing |
|---------|-----------------|--------|------------|---------|
| **Follower trend** | Direction of audience growth | Steady growth over past 30-90 days | Flat or very slow | Declining |
| **Top-performing content** | Awareness of which formats drive reach and saves | Can identify and replicates top formats | Some high-performers but pattern not exploited | No awareness of what works |
| **Hashtag discipline** | Collection-aware hashtag sets in first comment. Branded + niche + collection tags. | Correct sets, rotated, first comment | Hashtags used but in caption / generic / not rotated | No hashtags |
| **Cross-promotion** | skyyrose.co linked consistently. Platforms reference each other. | Tight cross-platform funnel | Occasional links | Each platform isolated |

---

## Step 3: Present

Deliver in this order — present everything before saving.

### 3A: Audit Scorecard

```
## SkyyRose Social Media Audit Scorecard — [Date]

| Dimension              | Instagram | TikTok | Pinterest | X/Twitter |
|------------------------|-----------|--------|-----------|-----------|
| Profile Optimization   |           |        |           |           |
| Brand Canon Compliance |           |        |           |           |
| Content Quality        |           |        |           |           |
| Posting Consistency    |           |        |           |           |
| Engagement Health      |           |        |           |           |
| Growth Signals         |           |        |           |           |

Overall: X Strong / Y Needs Work / Z Missing
```

### 3B: Top 3 Wins

Specific, SkyyRose-flavored findings. What's working and why:

```
## What Is Working

1. [Specific finding tied to SkyyRose brand performance, not generic praise]
2. [...]
3. [...]
```

### 3C: Top 3 Gaps

Tied to the stated goal (brand awareness / sales / community). Brand canon violations surface here:

```
## Biggest Opportunities

1. [Specific gap + specific fix, e.g., "Instagram bio uses generic 'luxury streetwear brand'
   copy — every profile visit misses the Oakland anchor. Fix: rewrite bio around the
   Oakland-direct brand description. No tagline is authorised."]
2. [...]
3. [...]
```

### 3D: Quick Wins (Fix Today)

3-5 zero-content-creation fixes:

```
## Quick Wins (Fix Today)

1. Rewrite Instagram bio around the Oakland-direct brand description (no tagline — none is authorised)
2. Add link-in-bio tool (Linktree or Stan Store) with links to each collection page on skyyrose.co
3. Pin top-performing product post to top of Instagram grid
4. Match profile photo across Instagram, TikTok, and X
5. Create IG Highlight covers: Black Rose / Love Hurts / Signature / Kids / Behind the Studio / Orders
```

### 3E: Review Gate

```
Does this audit reflect what you're seeing on your end? I can:
- Adjust any scores if something was mis-assessed
- Dig deeper into a specific platform or dimension
- Add a platform not yet covered

Once confirmed, I'll save the full audit report and build your 30-day action plan.
```

**GATE: Do not proceed to Step 4 until the user confirms the audit findings.**

---

## Step 4: Act

### 4A: Save the Audit Report

Save to `social-media-audit/skyyrose-audit-[YYYY-MM-DD].md`.

Include: scorecard, wins, gaps, quick wins, and the 30-day action plan.

### 4B: 30-Day Action Plan

Tailored to audit findings. Template:

```
## SkyyRose 30-Day Social Media Action Plan

### Week 1: Profile Foundation
- [ ] Rewrite bios on all active platforms — Oakland anchor, skyyrose.co link, no tagline
- [ ] Set up link-in-bio with per-collection deep links to skyyrose.co product pages
- [ ] Create or refresh IG Highlight covers (one per collection + Behind Studio + Orders)
- [ ] Pin top-performing product post to Instagram grid top
- [ ] Audit recent posts for brand canon violations — correct product naming, collection voice

### Week 2: Content System
- [ ] Run /skyyrose-social-social-media-calendar to build the next 2 weeks
- [ ] Establish weekly pillar schedule (Brand Story Mon, Product Tue/Fri, Culture Wed, Lifestyle Thu)
- [ ] Batch-create next week's text posts and identify assets needed
- [ ] Schedule all posts via native scheduler or Buffer

### Week 3: Engagement Engine
- [ ] Start daily engagement: 10 min before posting, comment authentically on 5 Oakland/streetwear accounts
- [ ] Respond to every comment within 24 hours
- [ ] Add specific CTAs to every post — not just "link in bio" but a direct action tied to post content
- [ ] DM every account that tags SkyyRose — request UGC permission if the photo is strong

### Week 4: Growth and Measurement
- [ ] Review which posts in weeks 2-3 got the most saves, shares, and profile visits
- [ ] Double down on top format — if carousels drove saves, plan 2 more for next month
- [ ] Implement correct hashtag sets (see /skyyrose-social-hashtag-strategy)
- [ ] Screenshot follower counts and engagement rates — baseline for next audit
```

### 4C: Next-Step Suggestions

```
## Recommended Next Steps

- Run /skyyrose-social-social-media-calendar — build the next 2 weeks using the 5-pillar framework
- Run /skyyrose-social-hashtag-strategy — get collection-aware hashtag sets to fix Growth Signals
- Run /skyyrose-social-social-media-strategy — if the audit reveals platform-mix problems, rebuild the strategy
```

---

## Implementation

```python
from agents.social_media_agent import SocialMediaAgent

agent = SocialMediaAgent()

# Pull analytics snapshot to inform audit scoring
analytics = agent.get_analytics()
print(analytics)

# Check platform config for benchmark comparison
ig_config = agent.get_platform_config("instagram")
tt_config = agent.get_platform_config("tiktok")

# Generate a benchmark post to compare against current live content quality
benchmark = agent.generate_post("br-001", "instagram", "product_launch")
print("Benchmark caption:")
print(benchmark.caption)
print("Benchmark hashtags:")
print(benchmark.hashtags)
```

```bash
# Run social venture smoke test to confirm pipeline is functioning before audit-driven rebuild:
python -m skyyrose.elite_studio.ventures.social smoke --sku br-001
```

```json
// Audit report schema — save to social-media-audit/skyyrose-audit-[YYYY-MM-DD].json
{
  "audit_date": "2026-05-27",
  "auditor": "SkyyRose Social Agent",
  "goal": "direct_sales",
  "platforms_audited": ["instagram", "tiktok"],
  "scorecard": {
    "instagram": {
      "profile_optimization": "needs_work",
      "brand_canon_compliance": "needs_work",
      "content_quality": "strong",
      "posting_consistency": "strong",
      "engagement_health": "needs_work",
      "growth_signals": "missing"
    }
  },
  "top_wins": [],
  "top_gaps": [],
  "quick_wins": [],
  "action_plan_weeks": 4
}
```

---

## Example: SkyyRose Instagram + TikTok Audit

**Scenario:** 6 months after launch, Instagram has 3,200 followers. TikTok has 890 followers. skyyrose.co traffic from social is flat. Posting ~3x/week on IG, inconsistently on TikTok.

**Step 1 findings:**
- Goal: Direct sales to skyyrose.co
- Instagram active, TikTok active but inconsistent
- Recent drop: BLACK Rose Crewneck pre-order 3 months ago — no sustained content follow-through post-drop

**Step 2 scoring (selected dimensions):**

| Dimension | Instagram | TikTok |
|-----------|-----------|--------|
| Profile Optimization | Needs Work | Missing |
| Brand Canon Compliance | Needs Work | Missing |
| Content Quality | Strong | Needs Work |
| Posting Consistency | Needs Work | Missing |
| Engagement Health | Needs Work | Missing |
| Growth Signals | Needs Work | Missing |

**Top 3 Wins:**
1. Instagram product photography is strong — consistent dark palette, editorial quality, BLACK Rose collection posts feel cohesive
2. Caption quality on feed posts has improved — hooks are present in first line, brand voice is closer to Corey's earned register
3. The BLACK Rose Crewneck pre-order posts drove a clear traffic spike — product drops work when content is concentrated

**Top 3 Gaps:**
1. TikTok profile has no bio, no link, and no consistent posting — the platform's discovery potential is entirely unrealized. For a visual streetwear brand, TikTok is the primary acquisition channel. Fix: complete the TikTok profile, run /skyyrose-social-tiktok-script, and commit to 1 video/day for 30 days.
2. No Instagram CTAs in last 15 posts say "shop at skyyrose.co" — captions end with vibes but no conversion path. Since the goal is direct sales, every product post needs a direct link. Fix: add "Shop the [Product Name] at skyyrose.co — link in bio" to every product caption.
3. Brand canon compliance: two recent Instagram posts use urgency copy ("Last chance — don't miss out!") that violates the founder's stated anti-manipulation canon. Fix: edit or archive those posts; rewrite the approach as stated fact ("Pre-order window closes [date]").

**Quick Wins:**
1. Complete TikTok bio: "Oakland streetwear | skyyrose.co"
2. Add TikTok link to skyyrose.co
3. Edit last 2 IG posts to replace urgency copy with stated-fact scarcity
4. Pin the BLACK Rose Crewneck reveal post to Instagram grid top
5. Create IG Highlights: Black Rose / Love Hurts / Signature / Behind the Studio

---

## Anti-Patterns

- **Starting the audit without confirming the goal** — a profile optimized for brand awareness looks different from one optimized for direct sales. Scores and recommendations shift based on goal.
- **Skipping Brand Canon Compliance dimension** — this is unique to SkyyRose. Generic social audits ignore brand voice discipline. Canon violations in public content damage brand equity.
- **Scoring platforms that haven't posted in 90+ days** — a dormant account isn't "Missing" on all dimensions; it should be flagged as "Inactive — audit not applicable" and noted as a strategic decision point.
- **Recommending daily posting on every platform** — SkyyRose at early stage should dominate 2 platforms before spreading. Inconsistent daily posting on 4 platforms is worse than consistent 4x/week on 1.
- **Presenting scores without specific SkyyRose-flavored findings** — "Content Quality: Needs Work" without citing which specific post and what specifically needs fixing is useless.
- **Saving the report before user review** — always present first, save second. The user may correct a score.
- **Treating hashtag gaps as Minor** — for a growing SkyyRose account (sub-10K), hashtag discoverability is a primary growth lever. Always surface hashtag gaps in Top 3 Gaps if present.

---

## Recovery

- **User has only one active platform:** Audit that platform fully. Recommend one additional platform based on goal — if sales goal and visual product, recommend Pinterest as the highest-ROI secondary. Include the second-platform setup as Week 4 of the action plan.
- **User can't describe posting frequency:** Ask "When was your last post? This week, last week, or longer ago?" — score Posting Consistency as Needs Work for platforms with vague cadence and note it in the audit.
- **Every dimension scores Missing:** Prioritize by goal. If the goal is sales: fix Profile Optimization and add CTAs first. Don't try to address all gaps simultaneously — pick 3 actions per week.
- **User disagrees with a score:** Ask what they see differently. If they provide evidence, adjust. If disagreement is feeling vs. evidence, keep the score and soften language: "This reflects opportunity, not failure — these are the highest-leverage moves."
- **Canon violation is ongoing and widespread:** Flag it prominently in Top 3 Gaps. Don't soften it. Canon violations in public content cost more long-term than any short-term engagement they generate.
