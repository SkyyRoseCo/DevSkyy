---
name: skyyrose-email-flows
description: "Complete Klaviyo email marketing system for SkyyRose luxury streetwear. Welcome sequences, pre-order drop launches, abandoned cart recovery, post-purchase flows, and seasonal campaigns. Use when creating any email content, flows, or sequences for skyyrose.co."
allowed-tools: Read Write Edit Glob
---

# SkyyRose Email Marketing System

## When to Use This Skill

- Creating welcome email sequences for new subscribers
- Building pre-order drop launch email sequences
- Writing abandoned cart recovery emails
- Designing post-purchase flows (confirmation → shipping → styling → review)
- Planning seasonal campaigns (Black Friday, holiday, summer drop)
- Writing any email content for the SkyyRose brand
- Setting up Klaviyo flows, segments, filters, or automation logic
- Configuring Klaviyo A/B tests, deliverability segments, or list-health sunset rules

**Platform:** Klaviyo (integrated with WooCommerce at skyyrose.co)

---

## Klaviyo Architecture — Verified Facts

**A Klaviyo Flow is an event-triggered sequence of actions.** It is NOT a scheduled campaign. The three trigger types are:

| Trigger Type | When it fires | SkyyRose use |
|---|---|---|
| **Metric (event)** | A tracked event fires for a profile (e.g., "Started Checkout") | Abandoned cart, post-purchase, browse abandonment |
| **List** | A profile is added to a specific Klaviyo list | Welcome sequence |
| **Segment** | A profile enters (or exits) a segment's membership condition | Re-engagement, VIP, collection-affinity |

**Flow actions available:**
- `send-email` — delivers a single email template
- `send-sms` — delivers SMS (requires SMS consent flag on profile)
- `time-delay` — waits N minutes/hours/days; supports timezone-aware "smart send time", weekday-only constraints (e.g., skip Saturday/Sunday), and specific time-of-day windows
- `conditional-split` — branches the flow on: profile properties, custom properties, marketing consent status, predictive analytics (predicted CLV tier, churn risk score), geographic/regional data, or random-sample percentage (A/B variant assignment)
- `trigger-split` — branches on properties of the triggering event payload (e.g., line-item collection, order total threshold)
- `update-profile` — sets or removes tags, custom properties, or list memberships mid-flow

**WooCommerce metric names in Klaviyo** (exact strings — used in trigger configuration):
- `Started Checkout` — fires when a customer reaches the checkout page and enters their email; payload includes full line-item details (product name, variant, SKU, price, image URL, quantity, URL)
- `Added to Cart` — fires earlier, at add-to-cart action; no full checkout payload
- `Viewed Product` — fires on product page view; use for browse abandonment
- `Placed Order` — fires on WooCommerce order completion; use for post-purchase flow

---

## Brand Voice for Email

| Element | Rule |
|---------|------|
| Tone | Like a text from a friend who happens to have incredible taste |
| Subject lines | Short, intriguing, never clickbait. Lowercase preferred. |
| Preview text | Complements the subject, never repeats it |
| CTAs | One per email. Specific: "See the drop" not "Shop now" |
| Imagery | Product renders + lifestyle. Dark backgrounds for BR, warm for SIG |
| Sign-off | "— The SkyyRose Team" or "— Corey" for founder emails |
| NEVER | Discount more than 15% (luxury brands don't race to the bottom) |
| NEVER | Use "Dear customer" or generic greetings. First name or nothing. |
| NEVER | Cross-sell or suggest related products — garment is the protagonist |
| NEVER | Urgency timers or countdown clocks — urgency is in the copy, not a widget |
| NEVER | European luxury house aesthetics — SkyyRose visual DNA = The Five (Kith, Oaklandish, Culture Kings, Fear of God, Palm Angels) |

**Tagline:** No tagline is authorised (founder decision 2026-10-06).

**Collection voice assignments — never mix:**
- **Black Rose:** armor, concrete, darkness as beauty, silver `#C0C0C0`. Voice: "you already stood up", "concrete answering back"
- **Love Hurts:** raw emotion, family, bloodline, crimson `#DC143C`. Voice: "Bloodline that raised me" (Love Hurts ONLY — never use in BR, SIG, or KC copy)
- **Signature:** Bay Area golden hour, gold `#D4AF37`. Voice: "stay golden", warmth, legacy
- **Kids Capsule:** little royalty, rose gold `#B76E79`. Voice: joy, inheritance, next generation

---

## Flow 1: Welcome Sequence (5 emails)

**Trigger type:** List — profile added to the SkyyRose subscriber list
**Goal:** Brand introduction → emotional connection → first pre-order

**Conditional-split example for this flow:** After Email 2, split on `collection_affinity` custom property:
- Branch A (`collection_affinity = "black-rose"`) → send BR-specific styling imagery in Email 3 hero
- Branch B (all others) → send generic brand story Email 3

### Email 1: Welcome (Immediate)
```
Subject: welcome to the concrete
Preview: luxury starts here

---

{{ first_name|default:"" }},

You just joined something different.

SkyyRose isn't another streetwear brand. It's luxury — built by a single father in Oakland who turned rock bottom into runway.

Every piece is limited. Every drop is intentional. And you're now first in line.

Here's 10% off your first order as a thank you:
USE CODE: {{ welcome_discount_code }}

[BROWSE THE COLLECTIONS →]

— Corey
Founder, The Skyy Rose Collection
```

**Klaviyo notes:** Tag subscriber as `welcome-flow-active`. Exclude from promotional sends for 7 days. The `{{ welcome_discount_code }}` variable is set per-campaign in Klaviyo's coupon code generator — never hardcode a code string.

### Email 2: The Collections (Day 2)
```
Subject: find your collection
Preview: three stories, one brand

---

Every SkyyRose collection tells a different story. Which one is yours?

🖤 BLACK ROSE
Dark elegance. Oakland roots. Limited edition pieces for those who find beauty in darkness.
[Explore Black Rose →]

❤️ LOVE HURTS
Raw emotion turned wearable. Named after the founder's family — this collection is personal.
[Explore Love Hurts →]

✨ SIGNATURE
Bay Area golden hour, bottled in cotton. Everyday luxury that speaks for itself.
[Explore Signature →]

Every collection drops in limited runs. When they're gone, they're gone.
```

### Email 3: The Founder Story (Day 4)
```
Subject: the real story behind skyyrose
Preview: from losing everything to building this

---

{{ first_name|default:"" }},

Four years ago, I had nothing. A baby on the way, no drive, no direction.

My daughter Skyy Rose changed everything. I named this brand after her because she's the reason it exists. Every late night, every failed manufacturer, every website rebuild — I kept going because she was watching.

SkyyRose isn't a brand story written by a marketing team. It's a father's promise to his daughter that where you come from doesn't define where you end up.

— Corey

[Read the full story →]
```

### Email 4: Social Proof (Day 7)
```
Subject: what people are saying
Preview: from our community

---

We don't do influencer campaigns (yet). What we do have is a community that gets it.

[UGC image grid — 3 customer photos]

"The weight of this hoodie is insane. This isn't mall brand quality." — Marcus, Oakland

"My daughter and I got matching Kids sets. She won't take hers off." — Keisha, San Leandro

"The jersey series is collector-level. 80 pieces and you can feel why." — J, San Francisco

Join the conversation: tag us @theskyyrosecollection

[SHOP THE MOST-LOVED PIECES →]
```

### Email 5: Pre-Order Exclusivity (Day 10)
```
Subject: your early access is waiting
Preview: limited pieces, limited time

---

{{ first_name|default:"" }},

Most of what we make sells through pre-order before it ever hits the shelves.

That's intentional. We don't overproduce. We don't do restocks on every drop. When a run is done, it's done.

As a subscriber, you get first access to every drop — before social media, before the public.

Your next chance is coming soon.

Stay ready.

[VIEW CURRENT PRE-ORDERS →]
```

**Klaviyo notes:** Remove `welcome-flow-active` tag after Email 5 via `update-profile` flow action. Add to main promotional segment.

---

## Flow 2: Pre-Order Drop Launch (7 emails)

**Trigger type:** Segment or manual campaign send to full list (or a collection-affinity segment) on launch calendar. This flow operates as a scheduled campaign sequence — it is NOT triggered by a metric event. Build as a Klaviyo Campaign series or a segment-entry flow tied to a `drop-announced` tag applied manually at launch.

**Goal:** Build hype → announce → convert → close

**Conditional-split example:** In Email 3 (Early Access), split on `repeat_customer` property:
- Branch A (repeat customer) → add personal thank-you line: "You've been here before. You already know."
- Branch B (first-time) → standard early-access copy

### Email 1: Teaser (T-7 days)
```
Subject: something's coming
Preview: {{ collection_name }} drop. soon.

---

[Dark/moody product silhouette image]

{{ collection_name }}.
New drop.
{{ drop_date }}.

Details soon. But if you've been waiting — this is it.

Be first: turn on notifications or just watch your inbox.
```

### Email 2: Announcement (T-3 days)
```
Subject: the {{ product_name }} drops {{ drop_date }}
Preview: limited to {{ quantity }} pieces

---

[Hero product image — front view]

{{ product_name }}
{{ collection_name }} Collection
${{ price }}

{{ short_description }}

Limited to {{ quantity }} pieces.
Pre-order opens {{ drop_date }} at {{ time }} PST.

Subscribers get early access — 2 hours before the public.

[SET A REMINDER →]
```

### Email 3: Early Access — Subscribers Only (Drop Day, 10am)
```
Subject: early access is live — you're first
Preview: 2 hours before everyone else

---

{{ first_name|default:"" }},

This is your window. The {{ product_name }} is live for subscribers only.

Public access opens at noon PST. You're already in.

[CLAIM YOURS →]

${{ price }} · Limited to {{ quantity }} pieces · Ships in 4-6 weeks
```

### Email 4: Public Launch (Drop Day, 12pm)
```
Subject: now live: {{ product_name }}
Preview: the drop is here

---

[Lifestyle product image]

The {{ product_name }} is officially live.

{{ two_sentence_description }}

${{ price }} · Pre-order until sold out.

[SHOP THE DROP →]
```

### Email 5: Social Proof / Momentum (T+2 days)
```
Subject: selling faster than expected
Preview: {{ percent_sold }}% claimed

---

The {{ product_name }} is {{ percent_sold }}% sold.

No restock planned for this run.

If you've been thinking about it — now's the time.

[SECURE YOURS →]
```

**Klaviyo notes:** Apply flow filter: exclude `purchased-this-drop` segment (see Key Segments below). This prevents sending a "selling fast" urgency email to someone who already converted. Define the segment as: profiles where the event `Placed Order` occurred AND order items contain `{{ product_id }}` for this drop — applied as a flow-level filter, not just a conditional split.

### Email 6: Last Chance (T+5 days or when 80%+ sold)
```
Subject: last call: {{ product_name }}
Preview: almost gone

---

{{ remaining_quantity }} left.

We're not saying this to pressure you. We're saying it because it's true.

When this pre-order closes, this exact piece won't come back the same way.

[FINAL CHANCE →]
```

### Email 7: Sold Out / Waitlist (When sold out)
```
Subject: sold out: {{ product_name }}
Preview: but you can still get on the list

---

The {{ product_name }} just sold out.

{{ quantity }} pieces. All claimed.

If you missed it — join the waitlist. We'll notify you first if we ever bring it back or release something similar.

[JOIN THE WAITLIST →]

Up next: [tease next drop if known]
```

---

## Flow 3: Abandoned Cart Recovery (3 emails)

**Trigger type:** Metric — `Started Checkout` (primary, highest intent) OR `Added to Cart` (secondary, earlier in funnel)

**Choosing your trigger:**
- **`Started Checkout`** (recommended): fires when the customer reaches checkout and enters their email. The event payload includes full line-item details — product name, variant, price, image URL, quantity, and product page URL — enabling complete personalization of all three emails. This is the highest-intent signal.
- **`Added to Cart`** (broader reach): fires earlier, at the moment of add-to-cart. Captures more profiles but payload has fewer line-item details. Use if `Started Checkout` volume is too low to be actionable.

Configure in Klaviyo: Flows → Create Flow → "Build your own" → Metric trigger → select `Started Checkout`. Set flow filter: `Has not placed order since starting this flow` (prevents emailing after successful purchase).

**Conditional-split example (Email 2):** Split on `predicted_clv` (Klaviyo predictive property):
- Branch A (high predicted CLV) → emphasize quality craftsmanship + exclusivity
- Branch B (low/unknown) → emphasize community testimonials + social proof

**Goal:** Recover the sale without devaluing the brand

### Email 1: Gentle Reminder (1 hour after abandon)
```
Subject: still thinking about it?
Preview: your {{ item.ProductName }} is waiting

---

[Product image from cart — {{ item.ImageURL }}]

The {{ item.ProductName }} is still in your cart.

We get it — some decisions need a minute. But this is a limited run, and we can't hold inventory.

[COMPLETE YOUR ORDER →]

${{ item.Price }} · {{ item.Categories.0 }} Collection
```

### Email 2: Social Proof Push (24 hours)
```
Subject: here's why they pulled the trigger
Preview: from people who didn't wait

---

{{ first_name|default:"" }},

Still on the fence? Here's what people say after they get their SkyyRose:

"The quality is on another level. You can feel the difference." — Customer review

"I hesitated on the last drop and it sold out. Not making that mistake again."

Your {{ item.ProductName }} is still available. For now.

[FINISH CHECKOUT →]
```

### Email 3: Scarcity + Offer (48 hours)
```
Subject: last nudge: free shipping on your cart
Preview: we covered shipping. you just have to say yes.

---

{{ first_name|default:"" }},

We don't do this often. But your cart has been sitting there for 2 days, and we'd rather see the {{ item.ProductName }} on you than back in inventory.

Free shipping on your order. No code needed — it's already applied.

[COMPLETE YOUR ORDER →]

This offer expires in 24 hours.
```

**Klaviyo notes:** Apply free shipping automatically via Klaviyo coupon code (generated dynamically per-profile). Do NOT offer percentage discounts — luxury brands protect their pricing. The `item.*` variables (ProductName, ImageURL, Price, Categories) are available from the `Started Checkout` event payload via Klaviyo's event variable syntax.

---

## Flow 4: Post-Purchase (4 emails)

**Trigger type:** Metric — `Placed Order` (fires on WooCommerce order completion, routed to Klaviyo via WooCommerce–Klaviyo integration webhook)

**Conditional-split example (after Email 1):** Split on `order.extra.collection` or product tag from the order payload:
- Branch A (Black Rose order) → Email 3 hero uses dark/silver imagery, armor-register care copy
- Branch B (Love Hurts order) → Email 3 hero uses deep-red/crimson imagery, bloodline-register care copy
- Branch C (Signature order) → Email 3 hero uses warm gold imagery, "stay golden" register
- Branch D (Kids Capsule order) → Email 3 hero uses rose-gold imagery, joyful little-royalty register

### Email 1: Order Confirmation (Immediate)
```
Subject: order confirmed — you're in
Preview: {{ event.ProductName }} is yours

---

{{ first_name|default:"" }},

It's official. The {{ event.ProductName }} is yours.

ORDER #{{ event.OrderId }}
{{ event.ProductName }} — {{ event.Variant }} — ${{ event.ItemPrice }}

[VIEW ORDER STATUS →]

PRE-ORDER NOTE: Your piece is being produced as part of a limited run. Expected ship date: {{ ship_date_estimate }}. We'll send tracking the moment it leaves.

Thank you for believing in what we're building.
— The SkyyRose Team
```

### Email 2: Shipping Notification (When shipped)
```
Subject: your skyyrose is on the way
Preview: tracking inside

---

It's moving.

{{ event.ProductName }} — {{ event.Variant }}
Tracking: {{ tracking_number }}
Carrier: {{ carrier }}
Estimated delivery: {{ delivery_estimate }}

[TRACK YOUR ORDER →]

CARE TIP: When it arrives, wash cold, inside out, tumble dry low. Your embroidery/print will thank you.
```

### Email 3: Garment Care + Styling (5 days after delivery)
```
Subject: 3 ways to wear your {{ event.ProductName }}
Preview: styled by the community

---

Your {{ event.ProductName }} has arrived. Here's how the community is wearing theirs:

1. LAYERED — Under a bomber or over a fitted tee. The weight holds structure.
2. MONOCHROME — All black everything. Let the details do the talking.
3. CONTRAST — Pair dark pieces with light denim or bright kicks.

[Share your fit: tag @theskyyrosecollection]

CARE GUIDE:
— Machine wash cold, inside out
— Tumble dry low or hang dry — heat breaks down print bonds
— No fabric softener on embroidered pieces — it loosens thread
— Store folded, not hung — heavy fleece stretches on a hanger
```

**Note:** No "WHAT'S NEXT?" block, no browse links, no complementary-product suggestions. The garment is the protagonist. Founder canon: no cross-sell, no related products, no recommendation widgets. If the customer wants more, they'll come back on their own terms.

### Email 4: Review Request (14 days after delivery)
```
Subject: how's the fit?
Preview: your opinion shapes the next drop

---

{{ first_name|default:"" }},

You've had the {{ event.ProductName }} for a couple weeks now. We want to hear it — the good, the real, all of it.

Your review helps the next person decide. And it helps us make the next drop even better.

[LEAVE A REVIEW →]

Bonus: Share a photo wearing your SkyyRose and we might feature you on the site and our socials.
```

**Klaviyo notes:** Tag reviewer as `review-submitted` via update-profile action on click. Add photo reviewers to `ugc-candidates` segment.

---

## Flow 5: Seasonal Campaign Template

**Trigger type:** Segment or manual campaign series — NOT metric-triggered. Activate by adding profiles to a `seasonal-campaign-active` segment or by launching as a scheduled Campaign series in Klaviyo.

Adapt this structure for Black Friday, holiday drops, summer collections, etc.

**Conditional-split example (T-0 Launch email):** Split on `days_since_last_purchase` (profile property):
- Branch A (purchased in last 60 days) → "You already know what we're about. Here's what's new."
- Branch B (lapsed 60–180 days) → re-engagement hook: "It's been a minute. Come see what dropped."
- Branch C (never purchased) → lead with brand story hook before product reveal

### Campaign Timeline
```
T-14: Teaser email ("something big is coming {{ date }}")
T-7:  Reveal email ("here's what's dropping")
T-3:  Reminder email ("3 days until [event]")
T-0:  Launch email (early access for subscribers)
T-0+4h: Public launch email
T+1:  Momentum email ("selling fast")
T+3:  Last chance email
T+5:  Closed/thank you email
```

### Black Friday Specific Rules
- Max 15% off — never more. SkyyRose is luxury.
- Position as "our only sale of the year" not "everything must go"
- Create a curated "Black Friday Edit" — 5-7 hero products
- Subject lines: lowercase, minimal, mysterious: "the only sale"

---

## Native A/B Testing in Klaviyo

Klaviyo supports native A/B tests inside flows and campaigns. Use these deliberately — not every email needs a test.

### What to test

| Test type | Implementation | When to use |
|---|---|---|
| Subject line | Klaviyo flow A/B on Email action | Low open rate (<20%) on a flow email |
| Send time | Smart Send Time vs fixed time | Testing timezone optimization |
| Content variant | Two Email blocks inside a conditional-split (random 50/50) | Testing CTA copy, hero image, social proof placement |
| Discount amount | Variant A: free shipping / Variant B: 10% off | Cart recovery Email 3 optimization |

### How to set up a content A/B test
1. In a flow, replace a single `send-email` action with a `conditional-split` set to **random 50%**.
2. Branch A → Email Template A. Branch B → Email Template B.
3. Let run for minimum 1,000 recipients (or 2 weeks for low-volume flows) before evaluating.
4. Klaviyo's built-in A/B reporting shows open rate, click rate, revenue per recipient — use revenue as the primary metric for cart recovery; use click rate for informational flows.
5. Once a winner is clear (statistical significance shown in the dashboard), collapse the split and set the winning template as the single email action.

### Subject line A/B (campaign)
In Klaviyo Campaign builder → "Add variation" → enter two subject lines → Klaviyo auto-splits send and promotes the winner after a defined engagement window (configurable: 4h / 8h / 24h after initial send). Use for every broadcast campaign where open rate is the primary concern.

### Rules for SkyyRose A/B tests
- Test ONE variable at a time — never subject + content simultaneously
- Never A/B test on a list smaller than 500 (no statistical signal)
- Document every test result in `.wolf/memory.md` for cross-session reference
- STOP-AND-SHOW before launching any A/B test that routes real Klaviyo sends — confirm variant copy and split ratio before activating

---

## Deliverability and List Health

### Sunset flow (unengaged profiles)
Unengaged profiles hurt sender reputation. Build a Klaviyo sunset flow triggered by **segment entry**:

**Segment definition — `lapsed-unengaged`:**
- Has not opened email in 90 days
- Has not clicked email in 90 days
- Has not placed order in 180 days
- Is NOT in `welcome-flow-active`
- Is NOT in `pre-order-customers`

**Sunset flow sequence:**
1. Email 1: "We miss you" re-engagement (softest touch)
2. Time delay: 7 days
3. Conditional-split: Has opened Email 1?
   - YES → exit flow, remove from `lapsed-unengaged`, keep subscribed
   - NO → continue to Email 2
4. Email 2: Final re-engagement ("Should we break up?") — clear opt-out CTA
5. Time delay: 7 days
6. Conditional-split: Has opened or clicked Email 2?
   - YES → exit, keep subscribed
   - NO → Suppress profile (Klaviyo → suppress = stops all sends, preserves data)

**Why:** Email providers (Gmail, Outlook) use engagement signals. Sending to large pools of unengaged profiles increases spam classification probability for ALL your sends, including to engaged subscribers.

### Engagement-based sending (advanced)
For large lists (5,000+), create a **send-to-engaged-only** segment for campaign broadcasts:
- Active on-site in last 90 days (requires Klaviyo JS tracking)
- OR clicked any email in last 30 days
- OR placed order in last 180 days

Send broadcast campaigns to this segment first. If engagement is strong after 24h, expand send to full list. This "warm-up" pattern protects deliverability on high-volume sends.

### List growth hygiene
- Never import cold purchased lists — instant spam-trap risk, violates Klaviyo TOS
- Double opt-in recommended for organic list-building (lower volume, higher engagement = better deliverability math)
- Review bounce rates after every campaign: hard bounces >2% signals list health problem

---

## Subject Line Formulas for SkyyRose

| Type | Formula | Example |
|------|---------|---------|
| Drop tease | something's coming | "something's coming" |
| Drop launch | now live: [product] | "now live: the varsity jacket" |
| Urgency | [number] left | "12 left" |
| Founder personal | lowercase casual | "the real story behind skyyrose" |
| Social proof | what people are saying | "what people are saying" |
| Cart recovery | question | "still thinking about it?" |
| Post-purchase | confirmation + excitement | "order confirmed — you're in" |

**Rules:** Lowercase preferred. Under 40 characters. No emojis in subject (save for preview text). Never misleading.

---

## Klaviyo Configuration Notes

### Key Segments
- `all-subscribers` — Full list
- `welcome-flow-active` — Currently in welcome sequence (exclude from promos)
- `pre-order-customers` — Have placed a pre-order (nurture differently)
- `repeat-customers` — 2+ orders (VIP treatment)
- `ugc-candidates` — Submitted photo reviews
- `lapsed-30d` — No open/click in 30 days (re-engagement target)
- `lapsed-unengaged` — No open/click/purchase in 90d+ (sunset flow trigger — see Deliverability section)
- `purchased-this-drop` — Placed an order containing the current drop's product ID; used as flow-level filter on Flow 2 Email 5 to suppress "selling fast" sends to buyers. Rebuild this segment per drop by filtering `Placed Order` events where the order contains the specific `{{ product_id }}` for the current launch.
- Collection-specific: `interested-black-rose`, `interested-love-hurts`, `interested-signature`, `interested-kids-capsule`

### Key Tags
- `source:website`, `source:instagram`, `source:tiktok` (track acquisition)
- `purchased:{sku}` (product-level targeting — internal identifier, not customer-facing)
- `collection:{name}` (collection affinity)
- `welcome-flow-active` (managed by Flow 1 update-profile actions)
- `review-submitted` (set on review CTA click in Flow 4 Email 4)

### Flow Priority (if subscriber qualifies for multiple flows)
1. Abandoned Cart (highest priority — revenue recovery)
2. Post-Purchase (time-sensitive)
3. Welcome Sequence
4. Drop Launch
5. Seasonal Campaign (lowest priority)

---

## Anti-Patterns

- **DO NOT** discount more than 15% — luxury brands don't race to the bottom
- **DO NOT** send generic WooCommerce transactional emails — brand every touchpoint
- **DO NOT** email more than 3x per week outside of launch windows
- **DO NOT** use "Dear Customer" — first name or skip the greeting
- **DO NOT** send the same email to all segments — personalize by collection affinity
- **DO NOT** write novels — emails should be scannable in under 30 seconds
- **DO NOT** use stock photography — only SkyyRose product renders and lifestyle shots
- **DO NOT** guilt-trip non-buyers — "we noticed you didn't buy" is passive-aggressive
- **DO NOT** cross-sell or suggest complementary products in any flow — garment is the protagonist
- **DO NOT** add urgency countdown timers — urgency lives in copy, not widgets
- **DO NOT** cross-attribute collection voices — "Bloodline that raised me" is Love Hurts ONLY
- **DO NOT** reference products by SKU in customer-facing copy — use product names from the catalog
- **DO NOT** hardcode discount codes — use `{{ welcome_discount_code }}` or Klaviyo's dynamic coupon generator
- **DO NOT** send to cold purchased lists — Klaviyo TOS violation, deliverability damage

## STOP-AND-SHOW Gate

Before any of the following, stop and show exact details, cost, and target — then wait for explicit `y`:
- Activating any Klaviyo flow or campaign (real sends to real subscribers)
- Creating or modifying WooCommerce webhooks
- Uploading media to Klaviyo or WordPress
- Running any paid API call (image generation, FASHN, Gemini, FLUX)

## Recovery

- **Low open rates (<20%):** Test subject lines. SkyyRose formula: lowercase, short, intriguing.
- **Low click rates (<2%):** CTA is buried or unclear. One button, above the fold.
- **High unsubscribe on welcome flow:** Email 1 is too salesy. Lead with story, not offers.
- **Cart recovery not converting:** Try earlier timing (30 min instead of 1 hour) or add product social proof.
- **Small list (<500):** Focus on welcome flow quality and organic list growth. Don't buy lists.
- **Deliverability degrading:** Run sunset flow immediately. Suppress all `lapsed-unengaged` profiles before next broadcast.
