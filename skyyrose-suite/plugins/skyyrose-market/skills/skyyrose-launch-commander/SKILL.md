---
name: skyyrose-launch-commander
description: "End-to-end product drop orchestration for SkyyRose. Coordinates the full launch timeline from T-30 to T+7 across product setup, email sequences, ad campaigns, social content, and influencer seeding — with mandatory STOP-AND-SHOW gates before any paid spend, Klaviyo sends, WooCommerce writes, or media uploads. Use when planning any product drop, collection launch, restock, or seasonal event."
allowed-tools: Read Write Edit Glob Bash Grep
---

# SkyyRose Launch Commander

## Brand Canon (non-negotiable)

No tagline is authorized. Do not restore retired slogans.
> - Collections: Black Rose (armor/concrete · silver `#C0C0C0`), Love Hurts (bloodline/crimson `#DC143C`), Signature (stay golden · gold `#D4AF37`), Kids Capsule (little royalty · rose gold `#B76E79`)
> - **Never cross-attribute** collection voices — "bloodline that raised me" = Love Hurts ONLY, "armor / you already stood up" = Black Rose ONLY
> - Products by **NAME**, not SKU, resolved from the catalog CSV + per-SKU dossier — never invented
> - Visual refs = The Five: Kith, Oaklandish, Culture Kings, Fear of God, Palm Angels — NEVER European luxury-house lineage
> - Collection names in hero positions = lockup PNG assets (`assets/images/hero-overlays/` for BR/LH/SIG; `assets/images/logos/` for Kids) — never live type
> - NO cross-sell · NO related-products on PDP · NO urgency timers — scarcity stated as fact, never fake countdown pressure
> - Oakland, CA anchor ("The Town") — "Bay Area" acceptable, Oakland-first preferred
>
> Full canon: `../skyyrose-content-engine/brand-guardrails.md`

---

## When to Use This Skill

- Planning a new product drop (single product or collection)
- Orchestrating a seasonal launch (Black Friday, summer drop, holiday)
- Coordinating restock announcements
- Running a flash drop / surprise release
- Generating all launch assets (emails, ads, social, product pages) in one workflow

This is the MASTER SKILL that orchestrates: `skyyrose-product-copy`, `skyyrose-email-flows`, `skyyrose-paid-media`, `skyyrose-content-engine`, `skyyrose-photography-brief`, `skyyrose-seo-commerce`, and `skyyrose-influencer-growth`.

---

## STOP-AND-SHOW Protocol (Non-Negotiable)

**Before any of the actions below, the commander MUST:**
1. Print a `propose-roster-and-wait` manifest (see format below)
2. Wait for explicit founder `y` / `yes`
3. Only then execute

**Gated actions:**
- Any paid ad spend (Meta, Google, TikTok)
- Any Klaviyo send or sequence activation
- Any WooCommerce product write (create, update, status change)
- Any media upload (WordPress Media Library, WC product images)
- Any T-phase step that triggers Elite Studio paid renders

**Manifest format:**

```
STOP — Confirm before proceeding:

Phase     : T-[N] — [Phase Name]
Actions   : [bullet list of exact actions]
  • Klaviyo: [sequence name] → [segment] ([N] recipients est.)
  • Meta Ads: [campaign name] → Submit for review (~$X/day budget)
  • WooCommerce: Create product "[Product Name]", status=pre-order
  • Media: Upload [N] images to WP Media Library
  • Elite Studio: Generate [N] renders for [SKU list] (~$X est.)
Files     : [file paths or "n/a"]
Cost est. : ~$[X] total

Proceed? [y/N]
```

---

## Drop Types & Timelines

| Drop Type | Timeline | Emails | Social Posts | Ads |
|-----------|----------|--------|-------------|-----|
| Full Collection Launch | T-30 to T+7 | 11 emails | 15-20 posts | 3 campaigns |
| Single Product Drop | T-14 to T+5 | 7 emails | 8-10 posts | 2 campaigns |
| Flash Drop (surprise) | T-48h to T+2 | 4 emails | 5 posts | 1 campaign |
| Restock | T-7 to T+3 | 5 emails | 5 posts | 1 campaign |

---

## Full Collection Launch Timeline (T-30 to T+7)

### T-30: STRATEGY

- [ ] Define the drop: products, quantities, pricing, collection
- [ ] Set launch date and pre-order window duration
- [ ] Identify hero product (leads all creative) — reference by NAME, not SKU
- [ ] Set revenue target and ad budget
- [ ] Brief: Who is this drop for? What story does it tell?
- [ ] Confirm collection voice (see Brand Canon above — do not cross-attribute)

**Deliverable:** Launch Brief document

---

### T-21: CONTENT PRODUCTION

> **STOP-AND-SHOW required** before dispatching Elite Studio renders (paid compute).

**Before executing this phase, propose manifest:**
```
STOP — Confirm before proceeding:

Phase     : T-21 — Content Production
Actions   :
  • Elite Studio: Generate renders for [product names] (front, back, branding per SKU)
  • skyyrose-photography-brief: Create shot lists and lifestyle briefs
Cost est. : ~$[X] (N renders × rate)

Proceed? [y/N]
```

- [ ] Product renders generated (invoke Elite Studio / `skyyrose-photography-brief` → front, back, branding per SKU)
- [ ] Lifestyle photography briefs created (use `skyyrose-photography-brief`)
- [ ] Video scripts written: 3 TikToks, 2 Reels, 1 brand story (use `skyyrose-content-engine`)
- [ ] Email copy written for all 7 launch emails (use `skyyrose-email-flows`)
- [ ] Product descriptions written for all SKUs (use `skyyrose-product-copy`)
- [ ] Ad copy and creative briefs prepared (use `skyyrose-paid-media`)

**Deliverable:** Complete content library for the drop

---

### T-14: WAITLIST & HYPE

> **STOP-AND-SHOW required** before activating Klaviyo teaser send.

**Before sending, propose manifest:**
```
STOP — Confirm before proceeding:

Phase     : T-14 — Waitlist & Hype
Actions   :
  • Klaviyo: "Something's Coming" teaser → Full list (~N recipients)
  • Influencer seeding: Ship product to [N] creators (use `skyyrose-influencer-growth` brief)

Proceed? [y/N]
```

- [ ] Waitlist / early-access signup page live on skyyrose.co
- [ ] Teaser posts begin on Instagram + TikTok (atmospheric, collection-appropriate imagery — NO countdown clocks)
- [ ] Influencer seeding: ship product to 5-10 micro-creators (brief via `skyyrose-influencer-growth`)
- [ ] Email teaser #1 sent to existing list ("something's coming" — tone matches collection voice)
- [ ] Stories on Instagram begin — no reveal yet

**Scarcity note:** If communicating limited quantities, state the number as fact ("250 made") — never a ticking countdown.

**Deliverable:** Active hype machine running

---

### T-7: FINAL PREP

> **STOP-AND-SHOW required** before any WooCommerce product write, media upload, or Klaviyo scheduling.

**Before executing, propose manifest:**
```
STOP — Confirm before proceeding:

Phase     : T-7 — Final Prep
Actions   :
  • WooCommerce: Create/update product "[Product Name]" — status=pre-order, price=$X
  • WooCommerce pre-order meta: _is_preorder=1, _preorder_edition_size=N, _preorder_ship_date=YYYY-MM-DD
  • Media: Upload N product images (renders + lifestyle)
  • Klaviyo: Schedule 7-email sequence (dates: [list])
  • Meta Ads: Build campaigns [names] in Ads Manager — NOT launched

Proceed? [y/N]
```

#### WooCommerce Configuration

**Standard product setup:**
- Pre-order status enabled (see WooCommerce Pre-order section below)
- Product images uploaded (renders + lifestyle)
- Product copy pasted (short desc, long desc, FAQ — from `skyyrose-product-copy`)
- SEO meta filled (title, description, slug — from `skyyrose-seo-commerce`)
- Collection/category assignments
- Price and inventory quantity set

#### WooCommerce Pre-Order (Theme-Native — `inc/woocommerce-preorder.php`)

SkyyRose uses a **theme-native** pre-order system — NOT a third-party plugin. It is built into the flagship theme at `inc/woocommerce-preorder.php`.

**Required post meta fields** (set via the `skyyrose_preorder_settings` meta box in WP admin, or programmatically on `save_post_product`):

| Meta Key | Type | Description |
|----------|------|-------------|
| `_is_preorder` | `"1"` / `"0"` | Enable pre-order mode |
| `_preorder_edition_size` | `absint` | Total units produced (edition limit) |
| `_preorder_available` | `absint` | Units available for pre-order |
| `_preorder_ship_date` | `YYYY-MM-DD` | Estimated ship date shown to customers |
| `_preorder_price` | `float` | Pre-order price (may differ from retail) |

**Theme helper:** `skyyrose_is_preorder($product_id)` — returns `bool`. Use to conditionally show pre-order badge or alter checkout flow.

**Template:** `template-preorder-gateway.php` — collection-selector pre-order experience.

**Nonce:** `skyyrose_preorder_nonce` — required on all programmatic saves.

**Verification:** After setting meta, confirm `skyyrose_is_preorder($product_id) === true` before launch.

#### Other T-7 Items

- [ ] Klaviyo email sequences scheduled (all emails with correct dates/times — no manual sends during launch)
- [ ] Ad campaigns built in Meta Ads Manager (NOT launched yet)
- [ ] TikTok ad campaigns built (NOT launched yet)
- [ ] Press release distributed (if newsworthy drop)
- [ ] Social media posts scheduled for launch day
- [ ] Test: complete a full test purchase on staging or with test card
- [ ] Verify: `skyyrose_is_preorder($product_id)` returns `true` for all pre-order SKUs

**Deliverable:** Everything built, tested, and waiting for go-live

---

### T-2: AD CREATIVE SUBMISSION ⚠️ SAFETY-CRITICAL

> **STOP-AND-SHOW required** before submitting ad creatives to Meta/Google.

**This step is non-negotiable.** Meta and Google ad review takes **24-48 hours**. Submitting at T-1 risks campaigns not being approved by launch.

```
STOP — Confirm before proceeding:

Phase     : T-2 — Ad Creative Submission
Actions   :
  • Meta Ads: Submit all campaigns for review (24-48h SLA)
    - Campaign: [name], Budget: $X/day, Creative: [description]
  • Google Ads: Submit [N] campaigns for review
  • TikTok Ads: Submit [N] campaigns for review

Proceed? [y/N]
```

- [ ] All Meta ad creatives submitted for review (do NOT wait until T-1)
- [ ] Google Ads campaigns submitted for review
- [ ] TikTok campaigns submitted for review
- [ ] Record submission timestamps — if not approved by T-1, escalate to Meta support
- [ ] Prepare backup static image creatives (in case primary video/carousel disapproved)

**If ads not approved by T-1:** Use the contingency path in the Branching & Contingency section below.

---

### T-1: PRE-LAUNCH CHECK

- [ ] ALL product pages live and functional
- [ ] `skyyrose_is_preorder($product_id)` confirmed `true` on all pre-order products
- [ ] Pre-order meta fields verified: `_preorder_ship_date`, `_preorder_edition_size`, `_preorder_available`
- [ ] Payment processing tested end-to-end
- [ ] Email sequences verified in Klaviyo (preview, test send — do NOT send live)
- [ ] Ad campaigns confirmed in "In Review" or "Approved" status (not just built)
- [ ] Social posts queued for publish
- [ ] Team briefed on launch day roles

**If ad campaigns still "In Review" at T-1:** See Contingency — Ad Account / Review Delay below.

---

### T-0: LAUNCH DAY

> **STOP-AND-SHOW required** before activating ad campaigns and sending launch emails.

**10:00am PST — Subscriber Early Access**

```
STOP — Confirm before proceeding:

Phase     : T-0 10:00am — Subscriber Early Access
Actions   :
  • Klaviyo: "Early Access Is Live" → Subscribers segment (~N recipients)
  • Instagram: Post "Early Access" Story

Proceed? [y/N]
```

- [ ] Send "early access is live" email (subscribers only)
- [ ] Post "early access" Story on Instagram
- [ ] Monitor: site speed, checkout function, inventory count

**12:00pm PST — Public Launch**

```
STOP — Confirm before proceeding:

Phase     : T-0 12:00pm — Public Launch
Actions   :
  • Klaviyo: "Now Live" → Full list (~N recipients)
  • Meta Ads: Activate campaigns [names] (~$X/day)
  • TikTok Ads: Activate campaigns [names] (~$X/day)
  • Google Ads: Activate campaigns [names] (~$X/day)
  • Publish launch posts: Instagram, TikTok, X

Proceed? [y/N]
```

- [ ] Send "now live" email to full list
- [ ] Publish launch posts on Instagram, TikTok, X
- [ ] Activate ad campaigns (Meta + TikTok + Google)
- [ ] Monitor first 4 hours: orders, page views, ad spend, any errors

**Throughout Launch Day:**
- [ ] Respond to DMs and comments in real-time
- [ ] Share Stories of early orders / excitement
- [ ] Screenshot and save any organic UGC from customers

---

### T+1 to T+3: MOMENTUM

> **STOP-AND-SHOW required** before "selling fast" email send.

- [ ] Send "selling fast" email (with real % sold if >50% — never fabricated urgency)
- [ ] Post customer reactions / UGC on Stories
- [ ] Adjust ad budgets: increase on winners, kill underperformers (STOP-AND-SHOW if budget change >$50)
- [ ] Share behind-the-scenes content (packing orders, production footage)

**Scarcity framing:** "X of 250 units remain" = correct. Fake countdown timer = never.

---

### T+5 to T+7: CLOSE & TRANSITION

> **STOP-AND-SHOW required** before "last chance" send and ad campaign changes.

- [ ] Send "last chance" email (only if inventory genuinely limited — state real number)
- [ ] Final push social posts
- [ ] When sold out: send "sold out + waitlist" email
- [ ] Transition ad campaigns to retargeting only (STOP-AND-SHOW — budget change)
- [ ] Begin post-launch analysis

---

### T+7: POST-LAUNCH REPORT

Generate using this template. All benchmark targets are **directional heuristics — test and adjust per your platform analytics**.

```
# [Drop Name] Launch Report

## Revenue
- Total revenue: $[X]
- Target: $[Y]
- Achievement: [X/Y]%
- Units sold: [N] of [Total available]
- Average order value: $[AOV]

## Email Performance
| Email | Open Rate | Click Rate | Revenue | Benchmark (directional) |
|-------|-----------|-----------|---------|------------------------|
| Teaser | X% | X% | $0 | Open: 25-35%¹ |
| Announcement | X% | X% | $X | Open: 25-35%¹ |
| Early Access | X% | X% | $X | Open: 35-45%¹ |
| Public Launch | X% | X% | $X | CTR: 2-4% |
| Selling Fast | X% | X% | $X | CTR: 2-4% |
| Last Chance | X% | X% | $X | Open: 30-40%¹ |
| Sold Out | X% | X% | $0 | — |

¹ Apple Mail Privacy Protection (MPP) inflates open rates — track click-through as the more reliable signal.

## Ad Performance
| Platform | Spend | Revenue | ROAS | CPA | Top Creative |
|----------|-------|---------|------|-----|-------------|
| Meta | $X | $X | Xx | $X | [Name] |
| TikTok | $X | $X | Xx | $X | [Name] |
| Google | $X | $X | Xx | $X | [Name] |

Directional benchmarks: fashion e-commerce ROAS 2-4x cold traffic; CPA $20-$60 depending on AOV.
Adjust expectations for brand-awareness campaigns (lower ROAS, higher long-term LTV).

## Social Performance
- Total impressions: [X]
- Total engagement: [X]
- New followers gained: [X]
- Top performing post: [link]
- UGC collected: [N] pieces

Directional benchmarks: Instagram engagement rate 1-3% for fashion; TikTok 3-8% for organic drops.

## Lessons Learned
1. [What worked]
2. [What didn't work]
3. [What to change for next drop]

## Pre-Order Performance (if applicable)
- Pre-order window: [start] → [end]
- Pre-orders placed: [N]
- Pre-order revenue: $[X]
- Ship date communicated: [YYYY-MM-DD]
- Actual ship date: [YYYY-MM-DD]
```

---

## Branching & Contingency Logic

### If product page not ready at T-7

**Trigger:** WooCommerce product not configured / images not uploaded / copy not in CMS by T-7.

**Path:**
1. Identify the blocker (renders missing? copy not written? WC meta not set?)
2. Escalate to the relevant skill immediately:
   - Missing renders → `skyyrose-photography-brief` + Elite Studio re-run (STOP-AND-SHOW)
   - Missing copy → `skyyrose-product-copy` emergency sprint
   - Missing SEO meta → `skyyrose-seo-commerce` fill
3. If page won't be ready by T-3: consider compressing to Single Product Drop timeline (T-14 structure, not T-30)
4. Do NOT launch on an incomplete product page — a broken or empty PDP on launch day loses sales and damages brand trust

### If ad account restricted or ad not approved by T-1

**Trigger:** Meta/Google ad account flagged, campaigns still "In Review" at T-1, or creatives disapproved.

**Path:**
1. Do NOT delay launch — owned channels (email + organic social) are primary drivers
2. Submit appeal immediately to Meta Business Support (document the campaign objective, creative, and policy compliance)
3. Activate backup static-image creatives (prepared at T-2) as fallback if available
4. Launch on T-0 via email + organic social only
5. Ads go live as soon as approved — they do not need to launch simultaneously with email
6. Do NOT run disapproved ads on alternate accounts — policy violation risk

**Learning:** Meta review SLA is 24-48h. Submitting at T-2 (not T-1) gives a recovery window. If account has prior flags, budget T-3 submission.

### If Klaviyo sequence fails to send

**Trigger:** Email not delivered, sequence not triggered, audience sync error.

**Path:**
1. Check Klaviyo activity feed for send errors (bounce, unsubscribe spike, API error)
2. Verify list/segment sync — WooCommerce Klaviyo integration can lag
3. For critical launch sends (Early Access, Public Launch): manual broadcast send from Klaviyo UI as fallback
4. Do NOT send duplicate emails to the same segment — check send logs before any manual resend

### If checkout is broken on launch day

**Trigger:** Orders not completing, payment gateway errors, cart not functioning.

**Path:**
1. Immediately pause all live ad spend (STOP-AND-SHOW — budget change)
2. Post "technical maintenance" Story on Instagram — do not go silent
3. Email the subscriber list: "We'll be back in [X] minutes — your interest is noted"
4. Escalate to WordPress hosting / WooCommerce support
5. Extend pre-order window to compensate — communicate via email + social once resolved
6. Never extend a fake countdown clock — extend the actual window and state the new date

### If sales are slower than expected after T+1

**Trigger:** <10% inventory sold after 24h, ROAS <1x, minimal organic engagement.

**Path:**
1. Pivot messaging from "new" to social proof — feature authentic customer reactions if available
2. Reframe ads around the story of the piece, not urgency ("250 made" if that's true — never fake countdown)
3. Audit ad targeting — are you hitting the right audience?
4. Audit product page — is the photography telling the story? Is copy grounded in collection voice?
5. Brief `skyyrose-influencer-growth` for accelerated organic seeding
6. Do NOT discount on or immediately after launch day — the product has full value at launch

### If influencers don't post as expected

**Trigger:** Seeded creators haven't posted by T-1.

**Path:**
1. Follow up via DM — confirm they received the product and brief
2. Do NOT rely on influencer timing for launch day — treat organic influencer content as upside, not baseline
3. Owned channels (email + skyyrose.co social) are the primary launch drivers
4. Re-brief via `skyyrose-influencer-growth` if relationship is ongoing

---

## Single Product Drop (Compressed — T-14)

Same structure, compressed timeline:
- T-14: Strategy + begin content production (STOP-AND-SHOW on renders)
- T-10: Content complete
- T-7: Hype begins (teasers, influencer seeding) + WooCommerce configured (STOP-AND-SHOW)
- T-3: Emails scheduled, ads built
- **T-2: Ad creatives submitted for review (24-48h SLA — non-negotiable)**
- T-1: Pre-launch check — confirm `skyyrose_is_preorder()` + ad review status
- T-0: Launch (same day-of structure as full launch)
- T+5: Close + report

Email sequence: 5 emails (teaser, announcement, early access, selling fast, last chance)

---

## Flash Drop (T-48 hours)

For surprise releases or limited restocks:

**T-48h:** Decide product, quantity, set up WooCommerce (STOP-AND-SHOW — WC write), write 4 emails
**T-24h:** Teaser on social ("tomorrow. that's all we'll say.") — no countdown timer, no fake urgency
**T-0:** Drop live. Email + social + DM to VIP customers simultaneously. (STOP-AND-SHOW — Klaviyo send)
**T+24h:** "Selling fast" update — state real inventory number
**T+48h:** Sold out or close

No paid ads for flash drops — organic demand only. Scarcity stated as fact, never as pressure.

---

## Restock Drop (T-7)

For bringing back sold-out products:

**T-7:** Notify waitlist ("it's coming back") — STOP-AND-SHOW before Klaviyo send
**T-3:** Email + social announcement with exact quantity (state as fact: "200 units available")
**T-0:** Waitlist gets 2-hour early access, then public — STOP-AND-SHOW on both sends
**T+3:** Close or continue

---

## Cross-Skill Orchestration

When running a launch, invoke skills in this order:

1. `skyyrose-product-copy` → Generate product descriptions for all products (NAME, not SKU)
2. `skyyrose-photography-brief` → Create shot lists and render briefs (triggers STOP-AND-SHOW on Elite Studio renders)
3. `skyyrose-email-flows` → Build complete email sequence
4. `skyyrose-paid-media` → Create ad campaigns and creative briefs
5. `skyyrose-content-engine` → Generate social content calendar
6. `skyyrose-seo-commerce` → Optimize product pages for search
7. `skyyrose-influencer-growth` → Brief influencer partnerships

**Wiring note:** At runtime, the commander routes through `agents/core/orchestrator.py → route(task)`. Photography briefs dispatch to `SkyyRoseImageryAgent.generate_image(purpose=ImageryPurpose.CAMPAIGN)` via Elite Studio (`skyyrose/elite_studio/`). All paid render calls are STOP-AND-SHOW.

---

## Implementation

```python
from agents.social_media_agent import SocialMediaAgent
from skyyrose.elite_studio.ventures.social import smoke

# Check pre-order status on a product before launch
from agents.wordpress_asset_agent import WordPressAssetAgent

agent = SocialMediaAgent()
# Generate launch caption for the collection's hero product
post = agent.generate_post(hero_product_name, "instagram", "product_launch")
print(post.caption)
print(post.hashtags)
```

```bash
# Run the full launch-commander workflow via Elite Studio CLI:
python -m skyyrose.elite_studio.ventures.social smoke --drop-type full_collection

# Verify pre-order meta is set correctly (query WC REST API):
# GET /wp-json/wc/v3/products/{id}/meta_data
# Confirm _is_preorder = "1", _preorder_ship_date set, _preorder_edition_size > 0
```

**Klaviyo campaign payload example (T-14 teaser send):**

```json
{
  "data": {
    "type": "campaign",
    "attributes": {
      "name": "[Drop Name] — Teaser",
      "audiences": {
        "included": [{ "id": "LIST_ID", "type": "list" }],
        "excluded": []
      },
      "send_strategy": {
        "method": "immediate"
      },
      "campaign-messages": {
        "data": [{
          "type": "campaign-message",
          "attributes": {
            "label": "Teaser",
            "channel": "email",
            "content": {
              "subject": "something's coming.",
              "preview_text": ""
            }
          }
        }]
      }
    }
  }
}
```

---

## Anti-Patterns

- **DO NOT** launch without testing checkout — a broken cart on launch day is catastrophic
- **DO NOT** launch without pre-scheduled emails — manual sending leads to missed timing
- **DO NOT** discount on launch day — the product is new, it has full value
- **DO NOT** launch on Monday or Friday — Tuesday-Thursday get best email engagement
- **DO NOT** skip the post-launch report — every drop teaches something for the next one
- **DO NOT** launch multiple products without a hero — one product leads, others follow
- **DO NOT** forget to exclude purchasers from "selling fast" emails — insulting to buyers
- **DO NOT** submit ads at T-1 — Meta review is 24-48h, submit at T-2 minimum
- **DO NOT** launch on a product page with missing or wrong pre-order meta — `skyyrose_is_preorder()` must return `true` before T-0
- **DO NOT** use urgency timers, fake countdown clocks, or "only N hours left" copy — scarcity is stated as fact, never manufactured pressure
- **DO NOT** put one collection's voice on another — "bloodline that raised me" is Love Hurts only; "concrete answering back" is Black Rose only
- **DO NOT** proceed past any STOP-AND-SHOW gate without explicit founder `y` — paid spend, Klaviyo sends, WC writes, and media uploads all require confirmation

## Recovery

- **Low pre-launch interest:** Increase hype content. Add an exclusive early-access incentive (limited to N units). Extend teaser period. Do not add urgency timers.
- **Site crashes on launch:** Pause all ad spend immediately (STOP-AND-SHOW). Post maintenance Story. Email list with honest update and revised window. Never extend a fake countdown — extend the actual window and state the new end date.
- **Ads not approved in time:** Submit at T-2, not T-1. Always prepare backup static image creatives. If disapproved at T-1, launch via owned channels (email + social). File appeal; ads can activate post-launch.
- **Influencers don't post:** Do not rely on influencer timing for launch day. Owned channels are primary. Re-brief via `skyyrose-influencer-growth` for organic seeding follow-up.
- **Slow sales after launch:** Pivot messaging from "new" to social proof. Feature authentic customer reactions. State real remaining inventory as fact ("X of 250 remain") — never a fake countdown. Audit targeting and PDP photography before assuming the product is wrong.
- **Pre-order meta not set correctly:** Run `skyyrose_is_preorder($product_id)` diagnostic. Re-set via WP admin `skyyrose_preorder_settings` meta box or programmatically on `save_post_product` with nonce `skyyrose_preorder_nonce`. Verify `_is_preorder = "1"`, `_preorder_ship_date` set, `_preorder_edition_size > 0`.
