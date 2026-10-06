---
name: skyyrose-social-social-listening-plan
description: "Designs and runs the SkyyRose social listening framework — keyword and hashtag monitoring across Instagram, TikTok, X, and Reddit — to track brand mentions, competitor activity, Oakland streetwear sentiment, and purchase signals, with a response workflow and monthly intelligence report."
allowed-tools: Read Write Edit Glob
---

# SkyyRose Social — Social Listening Plan

## When to Use This Skill

- Setting up systematic brand mention monitoring across Instagram, TikTok, X, Pinterest, and Reddit
- Building the keyword and hashtag tracking list for SkyyRose, The Skyy Rose Collection, and all four collections
- Designing the response workflow for what to do with what we find (positive mentions, complaints, purchase signals, competitor moves)
- Configuring Apify actors or free-tier tools (Google Alerts, native platform search) for listening automation
- Building the monthly social intelligence report template
- Auditing an existing listening setup for gaps

**DO NOT** use this for posting strategy or content creation (use `skyyrose-content-engine`), for crisis response once a crisis is active (use `skyyrose-social-crisis-comms`), or for community moderation within The Concrete Garden (use `skyyrose-social-community-moderation`). This is a monitoring and intelligence-gathering skill.

---

## Brand Canon (non-negotiable)

- **Monitor the brand, not just the handle.** Most SkyyRose mentions will be untagged — people write "SkyyRose" or "Skyy Rose" or "The Town's luxury brand" without the @. Untagged monitoring is as important as @mention tracking.
- **Oakland context is signal.** Mentions that pair Oakland/Bay Area with luxury streetwear, even without naming SkyyRose, are warm audience signals. The Town is the brand's home territory.
- **The Five visual references** define the competitive space we monitor. Kith, Oaklandish, Culture Kings, Fear of God, and Palm Angels represent our competitive adjacency — their audience conversations are intelligence. European luxury house (Bottega, Rick Owens, 032c) conversations are not our audience.
- **No hype-merchant response.** When we respond to a mention, it must be in Corey's voice: direct, specific, genuinely grateful or genuinely helpful. Not "🔥 Thanks for the love!! 🙌🙌."
- Full canon: `../skyyrose-content-engine/brand-guardrails.md`

---

## Phase 1: Brief

### Required Inputs

| Input | What to Ask | Default |
|-------|------------|---------|
| **Current monitoring setup** | Are you using any tools already? Google Alerts? Manually checking? | Manual, ad hoc |
| **Priority platforms** | Which platforms generate the most SkyyRose conversation? | Instagram, TikTok, X |
| **Competitor list** | Which 3-5 brands are we benchmarking against? | Kith, Oaklandish, Culture Kings + 2 others |
| **Listening goals** | Brand sentiment, competitor intelligence, purchase signals, UGC sourcing, all? | Brand mentions + purchase signals + UGC |
| **Budget** | Free tools only, or budget for paid monitoring tools? | Free tools priority; Apify for targeted scrapes |
| **Response owner** | Who acts on what we find — Corey, a social manager? | Corey + social lead |

**GATE: Confirm brief before building the plan.**

---

## Phase 2: Outline

```
1. Listening Categories — what we monitor and why
2. Keyword & Hashtag Master List — SkyyRose, competitor, and industry queries
3. Tool Configuration — free tools, Apify actors, alert setup
4. Monitoring Schedule — cadence, time commitments, who owns what
5. Response Workflow — what to do with each type of finding
6. Monthly Intelligence Report — template and distribution
```

**GATE: Approve outline before full plan.**

---

## Phase 3: Build the System

### 1. Listening Categories

```
## What We Monitor

| Category              | What to Listen For                                         | Why It Matters                               |
|-----------------------|------------------------------------------------------------|----------------------------------------------|
| Brand mentions        | "SkyyRose", "Skyy Rose", "@skyyroseco", "The Skyy Rose Collection" | Reputation, UGC sourcing, sentiment tracking |
| Collection mentions   | "Black Rose collection", "Love Hurts collection", "Signature collection", "Kids Capsule" | Per-collection sentiment + UGC |
| Corey Foster mentions | "Corey Foster", "SkyyRose founder"                         | Founder brand health, interview/press opportunities |
| Competitor mentions   | Kith, Oaklandish, Culture Kings, Fear of God, Palm Angels  | Competitive intelligence, audience overlap   |
| Oakland streetwear    | "Oakland fashion", "Bay Area streetwear", "Oakland luxury", "The Town style" | Warm audience discovery |
| Purchase signals      | "looking for luxury streetwear", "recommend streetwear brand Oakland", "Black-owned fashion brands" | Direct acquisition opportunities |
| Sentiment shifts      | Spike in negative mentions, unusual complaint patterns     | Early warning system for brand issues        |
| UGC and fit pics      | Customers tagging @skyyroseco or posting without tagging   | Social proof sourcing, reshare opportunities |
```

### 2. Keyword & Hashtag Master List

```
## Monitoring Queries

### Tier 1 — Brand Core (check daily)
Exact matches:
  - "SkyyRose"
  - "Skyy Rose Collection"
  - "The Skyy Rose Collection"
  - "@skyyroseco"

Common variations and misspellings:
  - "SkyRose" / "Sky Rose"
  - "Skyyrose co"
  - "skyyrose.co"

### Tier 2 — Collections (check 3x/week)
  - "Black Rose collection" OR "Black Rose by SkyyRose"
  - "Love Hurts collection" OR "Love Hurts SkyyRose"
  - "Signature collection SkyyRose"
  - "Kids Capsule SkyyRose"
  - "#BlackRoseCollection" "#LoveHurtsCollection" "#SignatureCollection"

### Tier 3 — Competitors (check 2x/week)
  - "Kith" + "drop" OR "launch"
  - "Oaklandish" + "new"
  - "Culture Kings" + "streetwear"
  - "Fear of God" + "essentials" OR "essentials drop"
  - "Palm Angels" + "collection"

### Tier 4 — Oakland & audience discovery (check weekly)
  - "Oakland streetwear" "Oakland fashion" "Bay Area streetwear"
  - "Oakland luxury brand" "Black-owned Oakland fashion"
  - "luxury streetwear Oakland" "The Town style"
  - "Black-owned fashion brand" + "streetwear"

### Tier 5 — Purchase signals (check daily)
  - "looking for luxury streetwear"
  - "recommend a Black-owned streetwear brand"
  - "best Oakland fashion brand"
  - "alternative to Kith" "like Kith but Black-owned"
  - "streetwear brand Bay Area"
  - "streetwear gift idea" + "luxury"

### Branded hashtags to monitor (Instagram & TikTok)
  #SkyyRose #TheSkyRoseCollection
  #BlackRoseCollection #LoveHurtsCollection #SignatureCollection #SkyyRoseKids
  #OaklandFashion #BayAreaStyle #LuxuryStreetwear #BlackOwnedFashion
```

### 3. Tool Configuration

#### Tool Stack

##### Free (Always-On Baseline)

| Tool                    | Use                                          | Setup                                              |
|-------------------------|----------------------------------------------|----------------------------------------------------|
| Google Alerts           | Blog and news mentions for Tier 1 brand terms| alert per query; daily digest email                |
| Instagram native search | Hashtag and keyword monitoring               | Manual 10-min daily check on Tier 1 hashtags       |
| TikTok native search    | Keyword and hashtag trending                 | Manual 10-min daily check; note trending sounds     |
| X/Twitter Advanced Search | Real-time keyword monitoring               | Saved searches for Tier 1 + Tier 5 purchase signals|
| Reddit search           | Subreddit monitoring (r/streetwear, r/malefashionadvice, r/femalefashionadvice, r/AskSF, r/Oakland) | Weekly keyword scan |

##### Google Alerts Setup (Tier 1: Separate Alert per Query)

  Query 1: "SkyyRose" -site:skyyrose.co
  Query 2: "Skyy Rose Collection" -site:skyyrose.co
  Delivery: Daily digest, to social@skyyrose.co
  Sources: Everything (web + news + blogs)

##### Apify (Targeted Scrape Runs, Not Always-On)

Use Apify actors for periodic deep-scrapes when manual monitoring finds a spike or
when running monthly competitive intelligence. Require Corey confirmation before
dispatching any paid Apify run.

Actor recommendations:
  - apify/instagram-scraper — for hashtag and profile mention scrapes
  - apify/tiktok-scraper — for keyword and hashtag TikTok pulls
  - apify/twitter-scraper-lite — for X/Twitter keyword volume pulls
  - apify/reddit-search-scraper — for subreddit keyword monitoring
  - [Xquik X Tweet Scraper](https://apify.com/xquik/x-tweet-scraper)
    (`xquik/x-tweet-scraper`) for bounded X searches, post lookups, and public
    profile timelines
  - [Xquik X Follower Scraper](https://apify.com/xquik/x-follower-scraper)
    (`xquik/x-follower-scraper`) for bounded public follower, following, list,
    community, and audience-overlap research

Keep the existing actors available. Choose the actor matching the job's
documented contract.

Before each paid Actor dispatch:

1. Open the linked Actor Store page. Verify its current charging model.
2. Set the Actor's supported item cap. Use `maxItemsPerTarget` only when its
   live schema supports that field.
3. Set Apify's `maxTotalChargeUsd` run option outside the Actor input.
4. Record the exact Actor, canonical input hash, item cap, charge cap, live
   price, estimated cost, and approver in the STOP AND SHOW manifest.
   Wait for explicit confirmation bound to that manifest.
5. Keep the Apify token in secret storage. Never place it in a URL or report.
6. Collect only public data allowed by platform rules.
   Never bypass protected accounts. Never infer sensitive traits from the data.

Treat follower relationships and audience overlap as research signals.
They do not prove identity, intent, endorsement, or affiliation.

Xquik is an independent third-party service. Not affiliated with X Corp. "Twitter" and "X" are trademarks of X Corp.

Dispatch trigger: monthly intelligence report cycle OR when a listening spike
is detected in daily manual monitoring.

### 4. Monitoring Schedule

```
## Listening Cadence

| Activity                          | Frequency   | Time Required | Owner              |
|-----------------------------------|-------------|---------------|--------------------|
| Tier 1 brand mentions (Instagram) | Daily       | 10 minutes    | Social lead        |
| Tier 1 brand mentions (TikTok/X)  | Daily       | 10 minutes    | Social lead        |
| Google Alerts digest review       | Daily       | 5 minutes     | Social lead        |
| Tier 5 purchase signals (X, Reddit)| Daily      | 10 minutes    | Social lead        |
| Tier 2 collection hashtags        | 3x/week     | 15 minutes    | Social lead        |
| Tier 3 competitor monitoring      | 2x/week     | 15 minutes    | Social lead        |
| Tier 4 Oakland/audience discovery | Weekly      | 20 minutes    | Social lead        |
| Reddit subreddit scan             | Weekly      | 20 minutes    | Social lead        |
| Full Apify scrape (competitive)   | Monthly     | Run + review  | Social lead + Corey|
| Monthly intelligence report       | Monthly     | 1 hour        | Social lead        |
```

### 5. Response Workflow

```
## What to Do With What We Find

| Finding                              | Action                                              | Timeline          | Owner        |
|--------------------------------------|-----------------------------------------------------|-------------------|--------------|
| Positive brand mention (tagged)      | Like + genuine reply in Corey's voice; reshare to Stories with credit | Same day | Social lead |
| Positive brand mention (untagged)    | Reply to introduce the brand; ask permission to reshare | Same day | Social lead |
| Negative brand mention (tagged)      | Assess: valid complaint or troll? Valid → DM first, then public reply | Within 2 hours | Corey |
| Customer complaint gaining traction  | Escalate to Corey immediately; treat as L2 crisis   | Within 1 hour    | Corey        |
| Fit pic or customer photo (untagged) | DM for permission to reshare; log in UGC tracker   | Same day         | Social lead  |
| Purchase signal ("looking for...")   | Reply with a helpful, non-salesy recommendation (not "BUY NOW") | Same day | Social lead |
| Competitor weakness mentioned        | Log for positioning strategy; never trash-talk publicly | Log immediately | Corey |
| Competitor drop announcement         | Note timing for content calendar awareness          | Log immediately  | Social lead  |
| Industry trend gaining traction      | Add to content backlog with original source post    | Within the week  | Social lead  |
| Oakland/Bay Area streetwear conversation | Engage authentically; introduce SkyyRose only if it fits naturally | Same day | Social lead |

Response tone rule: Every response sounds like Corey — direct, specific, genuine.
Not "🔥 Thanks for the love!!" — not "We appreciate your feedback and will look into this."
Example positive reply: "Glad it landed right. That's the Black Rose — built exactly for that energy."
Example purchase signal reply: "If you're looking for luxury streetwear rooted in Oakland — we're it. skyyrose.co."
```

---

## Phase 4: Monthly Intelligence Report

```
## Monthly Social Listening Report — [Month YYYY]

**Brand mention volume:** [N] total ([+/-]% vs prior month)
**Sentiment breakdown:** [X]% positive / [Y]% neutral / [Z]% negative
**Platform breakdown:**
  Instagram: [N] mentions | TikTok: [N] | X/Twitter: [N] | Reddit: [N] | Other: [N]

**Top positive mention:**
  Platform: [Platform]
  Quote: "[verbatim text]"
  Engagement: [likes/shares/comments]
  Reshared: [yes/no]

**Top negative mention / complaint:**
  Platform: [Platform]
  Issue: [brief description]
  Response taken: [what we did]
  Resolved: [yes/no/in-progress]

**Collection mentions breakdown:**
  Black Rose: [N] | Love Hurts: [N] | Signature: [N] | Kids Capsule: [N]

**Competitor highlights:**
  Kith: [key activity or sentiment shift]
  Oaklandish: [key activity]
  Culture Kings: [key activity]
  Fear of God: [key activity]
  Palm Angels: [key activity]

**Purchase signals identified:** [N] (converted to reply: [N])

**UGC discovered:** [N] (permission secured for reshare: [N])

**Audience discovery — Oakland/Bay Area conversations:**
  [Key themes, subreddits, hashtags gaining traction]


**Content ideas from listening:**
  1. [Idea — source post URL]
  2. [Idea — source post URL]

**Action items for next month:**
  - [Specific action + owner]
  - [Specific action + owner]

**Apify scrape summary (if run):**
  Actor: [actor name]
  Actor Store URL: [exact linked Store URL]
  Run ID: [Apify run ID]
  Dataset ID: [Apify dataset ID]
  Max items: [configured item cap]
  Max total charge: [$ cap]
  Query: [keyword/hashtag]
  Volume: [N results]
  Key insight: [one-line takeaway]
```

---

## Implementation

```python
from agents.social_media_agent import SocialMediaAgent

agent = SocialMediaAgent()

# Pull brand mention analytics from the agent's listening integrations
mentions = agent.get_analytics(
    metric="brand_mentions",
    platform="all",
    date_range="last_30_days",
    keywords=["SkyyRose", "Skyy Rose Collection"]
)
print(mentions.summary)
print(mentions.sentiment_breakdown)

# Pull purchase signal conversations for manual response queue
signals = agent.get_analytics(
    metric="purchase_signals",
    platform="twitter,instagram,reddit",
    keywords=["looking for luxury streetwear", "Black-owned streetwear Oakland"]
)
for signal in signals.results:
    print(f"{signal.platform} | {signal.author} | {signal.text[:120]}")
```

```bash
# Smoke-test the social listening analytics endpoint
python -m skyyrose.elite_studio.ventures.social smoke \
  --sku none \
  --post-type listening_report \
  --platform all
```

Apify Instagram hashtag scraper configuration for the monthly Tier 2 collection
sweep:

```json
{
  "actor": "apify/instagram-scraper",
  "input": {
    "hashtags": [
      "BlackRoseCollection",
      "LoveHurtsCollection",
      "SignatureCollection",
      "SkyyRose",
      "OaklandFashion",
      "BayAreaStyle"
    ],
    "resultsLimit": 200,
    "scrapeType": "hashtag",
    "addParentData": false
  },
  "run_options": {
    "maxTotalChargeUsd": 5
  },
  "frequency": "monthly",
  "trigger": "manual_or_spike",
  "output_destination": "google_sheets_social_listening_log",
  "requires_approval": true,
  "approval_manifest": {
    "actor": "apify/instagram-scraper",
    "input_sha256": "<sha256-of-canonical-input>",
    "item_cap": 200,
    "max_total_charge_usd": 5,
    "pricing_checked_at": "<ISO-8601 timestamp>",
    "approver": "corey_foster"
  }
}
```

Xquik X Tweet Scraper Actor input for a bounded Tier 1 and Tier 5 sweep:

```json
{
  "mode": "search",
  "searchTerms": [
    "\"SkyyRose\"",
    "\"Skyy Rose Collection\"",
    "\"looking for luxury streetwear\"",
    "\"Black-owned streetwear\" Oakland"
  ],
  "maxItems": 200,
  "outputVariant": "rich",
  "fieldStyle": "camelCase",
  "outputPreset": "nested",
  "includeSearchTerms": true
}
```

Use this X Follower Scraper input for a bounded audience-overlap sample.
Verify the public X handle before replacing `verified_competitor_handle`:

```json
{
  "twitterHandles": [
    "skyyroseco",
    "verified_competitor_handle"
  ],
  "relation": "followers",
  "maxItems": 200,
  "maxItemsPerTarget": 100,
  "outputMode": "compact",
  "includeTargetMetadata": true,
  "overlapMode": true
}
```

The 2 Xquik Actor inputs omit the run-level charge cap. Configure
`maxTotalChargeUsd` in Apify before dispatch and record it in the approval
manifest.

Google Alerts configuration, replicated per query:

```json
[
  {
    "query": "\"SkyyRose\" -site:skyyrose.co",
    "frequency": "daily_digest",
    "sources": "all",
    "language": "en",
    "region": "any",
    "delivery": "email",
    "email": "social@skyyrose.co"
  },
  {
    "query": "\"Skyy Rose Collection\" -site:skyyrose.co",
    "frequency": "daily_digest",
    "delivery": "email",
    "email": "social@skyyrose.co"
  }
]
```

---

## Example: Listening During the Love Hurts Collection Pre-Order Window

**Scenario:** Love Hurts pre-order opens. Social listening detects:
1. A TikTok video (untagged): creator holds up the Love Hurts Jogger and says "this might be the best piece I've bought this year — SkyyRose is different"
2. X post: "anyone else waiting on their Love Hurts order? It's been 10 days and nothing shipped yet from skyyrose.co"
3. Reddit r/streetwear thread: "Best Black-owned streetwear brands right now?" — no SkyyRose mention

**Findings → Actions:**

TikTok (positive, untagged):
- DM the creator: "That Love Hurts piece was made for exactly that energy. Can we reshare this on our channels?" — Love Hurts register: raw passion, the bloodline. Not "Thanks for the love!! 🔥"
- Reshare to @skyyroseco with creator credit if permission granted.

X (complaint, tagged — treat as potential L2):
- Assess: shipping delay of 10 days on a pre-order? Confirm with Corey whether this is within expected window.
- If within window: reply publicly, direct to email for order status. Tone: direct, empathetic, no defensiveness.
- If actually delayed: escalate to Corey immediately. Treat as L2 crisis per `skyyrose-social-crisis-comms`.

Reddit (purchase signal — opportunity):
- Reply in r/streetwear thread with a genuine, non-salesy introduction: "SkyyRose out of Oakland — Black-owned, luxury streetwear rooted in The Town. Love Hurts collection is their signature for exactly this vibe: skyyrose.co/love-hurts"
- Do not over-pitch. One reply, specific, relevant.

**Love Hurts voice check:** Raw passion, the bloodline that raised us. Never cross into Black Rose (armor) or Signature (stay golden) language in these replies.

---

## Anti-Patterns

- **Monitoring only the handle (@skyyroseco)** — the majority of genuine brand conversation is untagged. Monitoring only @mentions misses 60-80% of real conversations.
- **Responding to every mention** — not every mention needs a response. Positive mentions get appreciation; purchase signals get a helpful reply; trolls get nothing. A social lead who replies to 100% of mentions burns time and dilutes the brand voice.
- **Trash-talking competitors** — when a competitor weakness surfaces in listening data, it goes into the positioning log, never into a public reply. "Why do people say Kith has gotten worse?" → log it, never quote-tweet it.
- **Hype-tone in responses** — "Thanks for the love!! 🔥🔥 We're so glad you love our product!!" is not SkyyRose. Every response should sound like Corey wrote it from the shop floor, not from a social media management app.
- **Monitoring without a response system** — listening that never generates action is wasted intelligence. Every signal type in the response workflow table must have an assigned owner and a response time.
- **Frequency mismatch** — checking brand mentions weekly instead of daily means a customer complaint spends 5 days unanswered. Tier 1 is daily, non-negotiable.
- **Apify running without approval** — Apify actors cost money. Per the STOP AND SHOW protocol, any Apify actor dispatch requires explicit Corey confirmation before execution.
- **Unbounded or private-data scraping:** Every Actor run needs item and charge caps. Collect public data only. Never infer sensitive traits from account relationships.
- **Ignoring misspellings** — "SkyRose" and "Sky Rose" generate real brand mentions that won't surface if the monitoring queries only use exact "SkyyRose" spelling.
- **Treating Oakland/Bay Area conversation as noise** — "Oakland luxury brand" and "Bay Area streetwear" conversation is warm audience discovery, not irrelevant background noise. These are the people who find SkyyRose next.

---

## Recovery

- **No brand mentions found:** The brand may still be in early awareness phase. Shift focus to Tier 4 (Oakland/audience discovery) and Tier 5 (purchase signals). When people start finding the brand through community channels, Tier 1 volume follows.
- **Overwhelmed by mention volume after a viral moment:** Prioritize the response workflow triage table. Handle negative and purchase-signal mentions first; acknowledge positives in batches. Do not let the backlog grow past 24 hours without action.
- **Negative sentiment trending:** Identify the root cause from the listening data before drafting any response. Log the trend in the monthly report. If it constitutes a crisis (sustained negative spike), escalate to `skyyrose-social-crisis-comms`.
- **No budget for paid tools:** Google Alerts + platform native search + weekly Reddit manual scan covers the essential monitoring at zero cost. Apify is reserved for monthly deep-scrapes when specific intelligence is needed.
- **Listening data not translating into content ideas:** Review the monthly report's "Content ideas from listening" section with Corey. Real audience language from listening (what people call the brand, how they describe the pieces) is the raw material for captions, TikTok hooks, and product descriptions.
- **Response owner is a bottleneck:** If Corey is the only response owner and volume exceeds his capacity, create templated reply frameworks for the top 5 response types (positive tagged mention, positive untagged, purchase signal, Oakland discovery, shipping complaint). The social lead can execute against templates; Corey reviews exceptions.
