---
name: skyyrose-paid-media
description: Paid media playbook for SkyyRose luxury streetwear — Meta, Google, TikTok campaigns. Covers campaign architecture (verified API field names), pixel + CAPI server-side events, Merchant Center feed with preorder fields, UTM attribution, audience strategy, creative copy, and brand-canon enforcement. Use when building, auditing, or optimizing paid campaigns.
---

# SkyyRose Paid Media Playbook

> **Tagline:** No tagline is authorised (founder decision 2026-10-06).
> **Collections:** Black Rose (armor, concrete, silver #C0C0C0) · Love Hurts (bloodline, crimson #DC143C) · Signature (stay golden, gold #D4AF37) · Kids Capsule (little royalty, rose gold #B76E79)
> **Visual DNA:** Kith · Oaklandish · Culture Kings · Fear of God · Palm Angels — ONLY these five. Never European luxury house aesthetics.
> **STOP-AND-SHOW required** before any paid spend, Klaviyo send, WooCommerce write, or media upload.

---

## Table of Contents

1. [Brand Canon Guardrails](#brand-canon-guardrails)
2. [Catalog Facts](#catalog-facts)
3. [Target Audiences](#target-audiences)
4. [Meta Campaign Architecture](#meta-campaign-architecture)
5. [Meta Pixel + Conversions API (CAPI)](#meta-pixel--conversions-api-capi)
6. [TikTok Playbook](#tiktok-playbook)
7. [Google Ads Architecture](#google-ads-architecture)
8. [Google Merchant Center Feed](#google-merchant-center-feed)
9. [UTM Attribution Scheme](#utm-attribution-scheme)
10. [Retargeting Framework](#retargeting-framework)
11. [Budget Framework](#budget-framework)
12. [Creative Brief Template](#creative-brief-template)
13. [Copy Templates by Collection](#copy-templates-by-collection)
14. [Anti-Patterns](#anti-patterns)
15. [Recovery Guide](#recovery-guide)

---

## Brand Canon Guardrails

These rules apply to every ad, brief, copy template, and audience segment:

| Rule | Detail |
|------|--------|
| Tagline | No tagline is authorised (founder decision 2026-10-06). Never add one to ad copy. |
| Collection voices | NEVER cross-attribute. Black Rose ≠ Love Hurts ≠ Signature ≠ Kids Capsule |
| Products | Reference by NAME (e.g., "BLACK Rose Hoodie"). Never SKU. Resolve from catalog CSV + dossier. |
| Fabric specs | Resolve from per-SKU dossier only. Never infer or invent. |
| Social proof | Use bracket templates: `[Customer name, City]` · `[X]+ members of the community` — never fabricate quotes or numbers |
| Scarcity | Real edition sizes from catalog (jersey series: ~80 pieces). No artificial urgency timers. |
| Visual refs | The Five: Kith, Oaklandish, Culture Kings, Fear of God, Palm Angels. Zero European luxury house references. |
| Hero names | Collection names use lockup PNG assets from `assets/images/hero-overlays/`. Never type-rendered in hero ads. |
| Cross-sell | No related products in ad copy or landing experience. Garment is the protagonist. |
| Oakland anchor | Ground all brand copy in Oakland. "Bay Area" acceptable; European luxury house framing never. |
| Pre-order SKUs | Treat `availability: preorder` + `availability_date` as the primary state, not an edge case (~10/33 SKUs) |

---

## Catalog Facts

| Metric | Value | Source |
|--------|-------|--------|
| Total SKUs | 33 | `skyyrose-catalog.csv` |
| Pre-order SKUs | ~10 | badge="Pre-Order" in catalog |
| List price range | $25–$265 | catalog CSV |
| Mean list price | ~$79.70 | catalog CSV (calculated) |
| Planning AOV | $65–$80 | Catalog mean; validate against live order data once available |
| Collections | 4 | Black Rose, Love Hurts, Signature, Kids Capsule |

> **AOV note:** $65–$80 is a planning figure based on catalog list prices. True AOV depends on units-per-order and sales mix. Validate against WooCommerce order data before committing to ROAS targets.

---

## Target Audiences

### Primary Segments

**Segment A — Streetwear Loyalists (25–34)**
- Platform signal: Follow Supreme, Off-White, Fear of God, Kith, Yeezy
- Oakland / Bay Area geo concentration
- Lookalike seed: customer email list (once ≥500 purchasers)
- Bid: LOWEST_COST_WITHOUT_CAP until ROAS baseline established

**Segment B — Conscious Luxury (28–42)**
- Interests: Black-owned businesses, conscious consumerism, premium streetwear
- Income targeting: top 25% (Meta: household income percentile targeting)
- Cross-platform: Pinterest + Instagram primary
- Bid: COST_CAP at ~2× AOV planning figure

**Segment C — Gift Buyers (30–55, seasonal)**
- Interests: luxury gifts, fashion gifting, premium menswear/womenswear
- Event: Birthday, Anniversary audience overlays
- Activate Q4 (Oct 1) and Mother's Day (Apr 1)
- Bid: LOWEST_COST_WITH_BID_CAP during peak; switch to LOWEST_COST_WITHOUT_CAP after learning

**Segment D — Kids Capsule Parents (28–45)**
- Interests: premium kids clothing, Black-owned kids brands, streetwear for kids
- Geo: Oakland/Bay Area primary, LA/NYC secondary
- Lookalike from Kids Capsule page visitors
- Bid: LOWEST_COST_WITHOUT_CAP

---

## Meta Campaign Architecture

### Verified API Hierarchy

```
Campaign
  └── Ad Set
        └── Ad
```

#### Campaign Object (verified field names)

```json
{
  "name": "SR_[Collection]_[Objective]_[Date]",
  "objective": "OUTCOME_SALES",          // or OUTCOME_AWARENESS, OUTCOME_LEADS
  "status": "PAUSED",                     // launch paused, activate manually
  "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
  "daily_budget": 5000,                   // in CENTS — $50.00 = 5000
  "special_ad_categories": []
}
```

> **Budget is in CENTS.** `daily_budget: 5000` = $50.00. `lifetime_budget: 100000` = $1,000.00. This is a common source of overspend bugs.

#### Bid Strategy Enums (exact API values)

| Enum | Use Case |
|------|----------|
| `LOWEST_COST_WITHOUT_CAP` | Learning phase; maximize delivery |
| `LOWEST_COST_WITH_BID_CAP` | Control per-action cost; set `bid_amount` in cents |
| `LOWEST_COST_WITH_MIN_ROAS` | Revenue optimization; requires `bid_constraints` |
| `COST_CAP` | Predictable CPA; set `bid_amount` as target CPA in cents |
| `TARGET_COST` | Stable CPA; deprecated in some account types — prefer COST_CAP |

For `LOWEST_COST_WITH_MIN_ROAS`:
```json
{
  "bid_strategy": "LOWEST_COST_WITH_MIN_ROAS",
  "bid_constraints": {
    "roas_average_floor": 20000
  }
}
```
> `roas_average_floor` = target ROAS × 10000. A 2.0× ROAS floor = `20000`. A 3.5× floor = `35000`.

#### Ad Set Object (verified field names)

```json
{
  "name": "SR_[Collection]_[Segment]_[Date]",
  "campaign_id": "<campaign_id>",
  "optimization_goal": "OFFSITE_CONVERSIONS",
  "billing_event": "IMPRESSIONS",
  "daily_budget": 2000,                   // cents
  "targeting": {
    "age_min": 25,
    "age_max": 40,
    "genders": [1, 2],                    // 1=male, 2=female; omit for all
    "geo_locations": {
      "cities": [
        {"key": "2421836", "radius": 25, "distance_unit": "mile"}  // Oakland
      ]
    },
    "flexible_spec": [
      {
        "interests": [
          {"id": "<id>", "name": "Fear of God"},
          {"id": "<id>", "name": "Kith"}
        ]
      }
    ]
  },
  "targeting_automation": {
    "advantage_audience": 0               // 0=off, 1=Advantage+ audience ON
  },
  "promoted_object": {
    "pixel_id": "<pixel_id>",
    "custom_event_type": "PURCHASE"
  }
}
```

> **Advantage+ audience** (`targeting_automation.advantage_audience: 1`): Meta expands targeting beyond your defined spec. Useful after 50+ purchase events/week. Start with `0` during learning phase; test `1` in a separate ad set.

#### Campaign Naming Convention

```
SR_[COL]_[OBJ]_[AUDIENCE]_[YYYYMMDD]

Examples:
SR_BR_SALES_STREETWEAR25-34_20260601
SR_SIG_AWARENESS_LOOKALIKE1PCT_20260601
SR_KC_SALES_PARENTS28-45_20260601
```

### Advantage+ Shopping Campaigns

For catalog-based retargeting and broad prospecting once pixel has 500+ purchase events:

```json
{
  "objective": "OUTCOME_SALES",
  "campaign_type": "SHOPPING",            // triggers Advantage+ Shopping
  "targeting": {
    "geo_locations": { "countries": ["US"] }
  }
}
```

Requires: WooCommerce catalog feed synced to Meta Commerce Manager. Use `availability: in stock` or `availability: preorder` — Meta rejects items without this field.

### Ad Set Budget Split (starting point)

| Ad Set | Allocation | Audience |
|--------|-----------|---------|
| Prospecting — cold interest | 40% | Segment A + B interest targeting |
| Lookalike — 1–3% | 40% | LAL from purchaser/pixel events |
| Retargeting — warm | 20% | 30–90 day site visitors, add-to-cart |

> **These percentages are starting points.** Validate with live ROAS data. Winning segments deserve budget shift; losing segments should be cut or restructured after 7–14 days of data.

---

## Meta Pixel + Conversions API (CAPI)

Post-iOS 14, browser-only pixel data is unreliable. Server-side Conversions API is required for accurate attribution and smart bidding eligibility.

### Setup (WooCommerce)

**Plugin:** Facebook for WooCommerce (Meta's official plugin) — installs both browser pixel + server-side CAPI in one integration.

Installation path:
1. WP Admin → Plugins → Add New → search "Facebook for WooCommerce"
2. Connect to Meta Business Manager and ad account
3. Enable "Conversions API" in the plugin settings (server-side toggle)
4. Verify event deduplication: both browser and server events fire; Meta deduplicates via `event_id`

### Critical Events to Fire (Server-Side Priority)

| Event | Trigger | Priority |
|-------|---------|----------|
| `Purchase` | WooCommerce order status → `processing` | P0 |
| `InitiateCheckout` | WC checkout page load | P1 |
| `AddToCart` | WC add-to-cart action | P1 |
| `ViewContent` | WC single product page | P2 |
| `PageView` | All pages | P2 |

### Server-Side Event Payload (CAPI)

```json
{
  "data": [{
    "event_name": "Purchase",
    "event_time": 1700000000,
    "event_id": "order_12345",            // must match browser event_id for dedup
    "event_source_url": "https://skyyrose.co/checkout/order-received/12345/",
    "action_source": "website",
    "user_data": {
      "em": ["<sha256_hashed_email>"],    // hash before sending — never plaintext
      "ph": ["<sha256_hashed_phone>"],
      "client_ip_address": "<ip>",
      "client_user_agent": "<ua>",
      "fbp": "<_fbp_cookie_value>",
      "fbc": "<_fbc_cookie_value>"
    },
    "custom_data": {
      "currency": "USD",
      "value": 89.00,
      "order_id": "12345",
      "content_ids": ["br-004"],          // SKU array — internal only, not in ad copy
      "content_type": "product",
      "contents": [{
        "id": "br-004",
        "quantity": 1,
        "item_price": 89.00
      }]
    }
  }],
  "access_token": "<pixel_access_token>",
  "partner_agent": "woocommerce"
}
```

> User PII (email, phone) **must be SHA-256 hashed** before sending to CAPI. The Facebook for WooCommerce plugin handles this automatically. If building a custom integration, hash server-side — never send plaintext.

### Verify CAPI Health

- Meta Events Manager → Events → filter by "Server" source → confirm Purchase events arriving
- Check deduplication rate (Events Manager shows this) — should be >80% deduplicated if both browser + server are firing correctly
- Test with Meta Pixel Helper (Chrome extension) for browser events; use Events Manager "Test Events" for server-side

---

## TikTok Playbook

### Account Structure

- Business Center → Advertiser Account → Campaign → Ad Group → Ad
- Objective: `PRODUCT_SALES` (catalog required) or `WEB_CONVERSIONS`
- Pixel: TikTok Pixel + Events API (same dual-signal logic as Meta CAPI)

### 20 Hook Frameworks

**Curiosity Hooks**
1. "You've never seen a hoodie built like this."
2. "What does luxury from Oakland actually look like?"
3. "The rose that survived the concrete."
4. "This isn't streetwear. This is armor."
5. "They said it couldn't come from here."

**Pattern Interrupt Hooks**
6. [Dead silence] Show the product. Let it speak.
7. Open mid-sentence: "...and that's why we don't do fast fashion."
8. B-roll of Oakland streets → cut to product close-up.
9. Hands unboxing. Zero words. Just the reveal.
10. "I'm not selling you a hoodie." [pause] "I'm selling you a standard."

**Social Proof Hooks** (use real customer testimonials when available)
11. "[Customer name, City]: 'I've bought from brands 10× our price. This is different.'"
12. Community milestone: "[X]+ members of the SkyyRose family. Growing."
13. Founder on camera: "We built this for people who refuse to shrink."
14. Before/after: Wearing it vs. not. Let the garment do the work.
15. "The most asked question in our DMs: when is the [Collection] dropping?"

**Direct Hooks**
16. "New drop. [Collection name] by SkyyRose."
17. "[Edition size] pieces. [Availability status]. Link in bio."
18. "[Collection Voice Line]. New [Collection] is live."
19. "Limited edition. Heavyweight. Embroidered. Ours."
20. Price point reveal: "[$X]. Built different."

### 3 Script Templates

**Template 1: The Origin Story (15–30s)**
```
HOOK (0–3s): [Oakland cityscape or concrete texture b-roll]
BRIDGE (3–10s): "We didn't grow up near luxury. We grew up near concrete.
                  SkyyRose is what happens when you refuse to let that be a ceiling."
PRODUCT (10–22s): Close-ups of garment details — embroidery, construction, fit
CTA (22–30s): "[Product name]. [Collection]. skyyrose.co"
```

**Template 2: The Product Feature (7–15s)**
```
HOOK (0–2s): Show the most striking visual detail (embroidery, colorway)
FEATURE (2–10s): Quick cuts — front, back, detail, worn on body
VOICE (10–13s): "[Collection voice line]"
CTA (13–15s): "skyyrose.co" on screen
```

**Template 3: The Community Signal (20–45s)**
```
HOOK (0–3s): "[X]+ people already wearing [Collection]."
SOCIAL (3–15s): [Customer content — with permission] or founder walkthrough
SCARCITY (15–30s): "[Edition size] pieces in this run." (only if catalog-verified)
BRAND (30–40s): Logo lock-up.
CTA (40–45s): "[Product name] — available now at skyyrose.co"
```

### Spark Ads

Promote organic posts as paid ads — preserves authentic engagement signals:
- Use posts with >3% organic engagement rate
- Minimum 24h organic performance before promoting
- Link to product page with UTM params (see [UTM Attribution Scheme](#utm-attribution-scheme))
- Budget: start at $20–30/day per Spark; scale winners

### TikTok Creative Principles

- First 1–2 seconds must earn the watch — no slow builds
- Native feel > polished production. SkyyRose aesthetic is intentional, not accidental
- Sound on: use original audio or royalty-free tracks that match brand register
- Caption text reinforces the hook, never redundant
- CTA in caption: "Link in bio" or "Shop skyyrose.co"

---

## Google Ads Architecture

### Verified API Field Names

#### Performance Max Campaign

```python
campaign = {
    "name": "SR_[Collection]_PMAX_[Date]",
    "advertising_channel_type": "PERFORMANCE_MAX",  # exact enum
    "status": "PAUSED",
    "bidding_strategy_type": "MAXIMIZE_CONVERSION_VALUE",
    "target_roas": 2.0,                              # 200% = 2.0 (not 200)
    "campaign_budget": {
        "amount_micros": 5000000,                    # in micros — $5.00 = 5000000
        "delivery_method": "STANDARD"
    },
    # Retail/shopping campaigns require merchant_id:
    "shopping_setting": {
        "merchant_id": "<google_merchant_center_id>",
        "sales_country": "US"
    }
}
```

> **PMax replaces Smart Shopping.** If you see Smart Shopping campaigns in the account, migrate to PMax. Smart Shopping was sunset by Google.

> **Budget is in micros.** 1,000,000 micros = $1.00. `amount_micros: 5000000` = $5.00/day.

#### Standard Shopping Campaign

```python
campaign = {
    "advertising_channel_type": "SHOPPING",         # not PERFORMANCE_MAX
    "shopping_setting": {
        "merchant_id": "<merchant_id>",
        "campaign_priority": 0                       # 0=low, 1=medium, 2=high
    }
}

ad_group = {
    "type": "SHOPPING_PRODUCT_ADS",                 # exact enum — not "SHOPPING"
    "cpc_bid_micros": 500000                        # $0.50 max CPC = 500000 micros
}
```

#### Search Campaign (Brand + Non-Brand)

```python
# Segment conversions by conversion_action for accurate ROAS per product line
segments = {
    "conversion_action": "customers/<id>/conversionActions/<action_id>"
}
```

### Campaign Structure

| Campaign | Type | Objective |
|----------|------|-----------|
| SR_Brand_Search | SEARCH | Protect brand terms |
| SR_NonBrand_Search | SEARCH | Capture streetwear intent |
| SR_[Collection]_PMAX | PERFORMANCE_MAX | Broad conversion |
| SR_Retargeting_Display | DISPLAY | Re-engage site visitors |

### Keyword Strategy

**Brand terms (exact + phrase):** "SkyyRose", "Skyy Rose hoodie", "SkyyRose collection"
**Non-brand (broad match + smart bidding):** "luxury streetwear Oakland", "Black-owned luxury fashion", "premium streetwear hoodie", "limited edition streetwear"
**Negative keywords (always):** "cheap", "discount", "knockoff", "replica", "wholesale", "aliexpress"

### GA4 Requirement for Smart Bidding

Google's smart bidding (Target ROAS, Maximize Conversion Value) requires a linked GA4 property with:
- Enhanced measurement enabled
- Purchase event flowing with `value` and `currency` parameters
- Link: Google Ads account → Tools → Linked accounts → Google Analytics 4

Without GA4 data, smart bidding operates blind on the first 2–4 weeks. Consider manual CPC for this period.

---

## Google Merchant Center Feed

SkyyRose has ~10/33 SKUs in pre-order status. Merchant Center rejects items that:
- Have `availability: preorder` without `availability_date`
- Have `availability_date` in the past
- Are missing required attributes for apparel (size, color, gender, age_group)

### Required Attributes (Apparel)

```xml
<item>
  <g:id>br-004</g:id>
  <g:title>BLACK Rose Hoodie – SkyyRose</g:title>
  <g:description>Heavyweight cotton fleece pullover hoodie. Embroidered Black Rose logo at chest. Tonal black throughout. SkyyRose Black Rose Collection.</g:description>
  <g:link>https://skyyrose.co/product/black-rose-hoodie/</g:link>
  <g:image_link>https://skyyrose.co/wp-content/uploads/br-004-front.jpg</g:image_link>
  <g:price>89.00 USD</g:price>
  <g:availability>in stock</g:availability>    <!-- or: preorder -->
  <!-- Required for preorder: -->
  <!-- <g:availability>preorder</g:availability> -->
  <!-- <g:availability_date>2026-09-01T00:00:00-07:00</g:availability_date> -->
  <g:condition>new</g:condition>
  <g:brand>SkyyRose</g:brand>
  <g:google_product_category>1604</g:google_product_category>  <!-- Apparel & Accessories > Clothing > Outerwear -->
  <g:product_type>Apparel > Hoodies > Black Rose Collection</g:product_type>
  <g:size>S</g:size>          <!-- one item per variant -->
  <g:color>Black</g:color>
  <g:gender>unisex</g:gender>
  <g:age_group>adult</g:age_group>
  <g:item_group_id>br-004</g:item_group_id>  <!-- groups all size variants -->
  <g:identifier_exists>no</g:identifier_exists>  <!-- no UPC/EAN — required field -->
</item>
```

### Pre-Order Handling

```xml
<!-- For all SKUs with badge="Pre-Order" in catalog: -->
<g:availability>preorder</g:availability>
<g:availability_date>2026-10-01T00:00:00-07:00</g:availability_date>
```

> `availability_date` is **required** when `availability: preorder`. Without it, Merchant Center rejects the item and it will not serve in Shopping ads or PMax.
> Format: ISO 8601 with timezone offset. Use Pacific time (`-07:00` PDT / `-08:00` PST).
> Source the `availability_date` from WooCommerce product meta (set in WC Pre-Orders plugin) — do not hardcode.

### Feed Sync Options

**Option 1: Google Listings & Ads plugin (recommended)**
- WP Admin → Plugins → Google Listings & Ads
- Syncs WooCommerce catalog → Merchant Center automatically
- Handles pre-order `availability` and `availability_date` from WC Pre-Orders meta
- Supports `item_group_id` for size/color variants

**Option 2: Manual feed upload**
- Generate XML/CSV via WooCommerce product export
- Upload to Merchant Center → Feeds → Add feed
- Schedule daily refresh or trigger on product update via webhook

**Option 3: Content API for Shopping (advanced)**
- Direct API integration for programmatic product management
- Useful when WooCommerce catalog updates need real-time sync
- Requires server-side OAuth, not plugin-based

### Common Feed Rejection Fixes

| Error | Fix |
|-------|-----|
| "Missing required attribute: availability_date" | Add `availability_date` for all `preorder` items |
| "Invalid value for attribute: availability" | Only valid values: `in stock`, `out of stock`, `preorder`, `backorder` |
| "Item not found in your website" | Verify product URL is indexed and publicly accessible |
| "Missing required attribute: size" | Add size variants as separate items with `item_group_id` |
| "Mismatched price" | Ensure feed price matches page price — Merchant Center crawls the URL |

---

## UTM Attribution Scheme

Consistent UTM parameters enable cross-channel attribution in GA4 and WooCommerce order data.

### Template

```
https://skyyrose.co/product/<slug>/?utm_source=<source>&utm_medium=<medium>&utm_campaign=<campaign>&utm_content=<content>&utm_term=<term>
```

### Source/Medium Matrix

| Channel | `utm_source` | `utm_medium` |
|---------|-------------|-------------|
| Meta (Facebook/Instagram) | `facebook` / `instagram` | `cpc` |
| TikTok | `tiktok` | `cpc` |
| Google Search | `google` | `cpc` |
| Google Shopping / PMax | `google` | `shopping` |
| Google Display | `google` | `display` |
| Klaviyo email | `klaviyo` | `email` |
| Organic social | `instagram` / `tiktok` | `social` |
| Influencer | `influencer` | `referral` |

### Campaign Naming Convention

```
utm_campaign = [collection]-[type]-[date]

Examples:
black-rose-prospecting-20260601
signature-retargeting-20260601
kids-capsule-seasonal-q4-2026
```

### Content (Ad Variant Tracking)

```
utm_content = [format]-[hook_variant]

Examples:
video-origin-story
static-product-detail
carousel-collection
spark-ads-organic-1
```

### Term (Optional — Paid Search)

```
utm_term = [keyword_match]:[keyword]

Examples:
exact:luxury+streetwear+hoodie
broad:black+owned+fashion
```

### Full Example

```
https://skyyrose.co/product/black-rose-hoodie/?utm_source=instagram&utm_medium=cpc&utm_campaign=black-rose-prospecting-20260601&utm_content=video-origin-story&utm_term=
```

### GA4 Configuration

Required for UTM data to surface in GA4 reports:
- GA4 → Admin → Data Streams → Web stream → Enhanced measurement: ON
- Verify `page_location` parameter captures full URL including UTM params
- Create GA4 explorations filtered by `utm_campaign` to see per-campaign revenue

---

## Retargeting Framework

### Audience Segments by Funnel Stage

| Stage | Audience Definition | Lookback | Bid Strategy |
|-------|-------------------|----------|-------------|
| Hot | Initiated checkout, no purchase | 7 days | COST_CAP at 1.5× CPA target |
| Warm | Add to cart, no checkout | 14 days | LOWEST_COST_WITH_BID_CAP |
| Engaged | Product page views, 60%+ scroll | 30 days | LOWEST_COST_WITHOUT_CAP |
| Cold Warm | Homepage/collection page visitors | 90 days | LOWEST_COST_WITHOUT_CAP |
| Purchaser LTV | Past purchasers | 180 days | Exclude from prospecting; use for upsell/new collection launch |

### Retargeting Creative Principles

- Hot (checkout abandon): product image + direct CTA. No brand story needed — they know you.
- Warm (cart abandon): emphasize what makes this different. Real scarcity if applicable.
- Engaged: brand storytelling. "You've been thinking about it." No pressure, no timers.
- Cold Warm: collection-level awareness. "The [Collection] collection is still here."

### Exclusion Rules

Always exclude:
- 7-day purchasers from all ad sets (prevent overlap with post-purchase email)
- Custom audience: purchasers (all-time) from prospecting campaigns

---

## Budget Framework

### Platform Split (starting point — validate with ROAS data)

| Platform | Allocation | Rationale |
|----------|-----------|-----------|
| Meta (FB/IG) | 50% | Highest purchase intent audience targeting precision |
| TikTok | 30% | Brand awareness, community building, younger demographic |
| Google | 20% | Capture high-intent search; protect brand terms |

> This 50/30/20 split is a starting point, not a formula. Shift budget toward platforms delivering ROAS above break-even (typically >2× AOV planning figure). Pull from underperforming platforms after 14+ days of data.

### Break-Even ROAS

```
Break-Even ROAS = 1 / Gross Margin %

Example (illustrative — use your actual COGS):
If GM = 60%: Break-Even ROAS = 1 / 0.60 = 1.67×
If GM = 50%: Break-Even ROAS = 1 / 0.50 = 2.00×
```

### Daily Budget Starting Points

| Phase | Daily Budget | Goal |
|-------|-------------|------|
| Learning (week 1–2) | $50–100 | Gather pixel data, test hooks |
| Scaling (week 3–8) | $100–300 | Scale winning ad sets |
| Steady state | Depends on ROAS | Maintain profitable campaigns |

> These ranges assume a small catalog launch. Scale with ROAS confirmation, not projections.

### ROAS Calculation

```
ROAS = Revenue from Ads / Ad Spend

Example:
$2,500 revenue attributed to Meta | $800 spend = 3.1× ROAS
```

At planning AOV $65–$80: target 2–3× ROAS minimum to cover COGS and fulfillment. Validate GM% before setting ROAS floors in Meta/Google bid strategies.

---

## Creative Brief Template

**Campaign:** [Collection name] — [Campaign type: prospecting/retargeting/awareness]
**Platform:** [Meta / TikTok / Google / all]
**Format:** [Video 9:16 / Static 1:1 / Carousel / Story]
**Product:** [Product name — from catalog, never SKU]
**Collection:** [Black Rose / Love Hurts / Signature / Kids Capsule]

**Hook (first 2s):**
[Describe the opening visual or spoken line]

**Body copy:**
[3–5 lines max. Collection voice only. No cross-attribution.]

**Headline (if static):**
[Headline only — no tagline.]

**CTA:**
[Shop now / Preorder [Product name] / Link in bio]

**Landing page:**
[Full URL with UTM params — see UTM scheme above]

**Scarcity (if applicable):**
[Edition size from catalog — e.g., "80 pieces" for jersey series. Never invented.]

**Visual direction:**
[Reference The Five: Kith / Oaklandish / Culture Kings / Fear of God / Palm Angels]

**What NOT to do:**
- No urgency timers or countdown clocks
- No cross-collection voice attribution
- No fabric spec claims without dossier verification
- No invented social proof numbers
- No European luxury house visual references

---

## Copy Templates by Collection

### Black Rose

**Voice register:** Armor. Concrete answering back. You already stood up.

```
Headline: Built from the concrete. Worn like armor.
Body: BLACK Rose isn't streetwear. It's the proof you made it through.
      Heavyweight construction. Embroidered. Made to last.
CTA: Shop BLACK Rose →
```

```
Hook: "They said luxury wasn't built here."
Body: They were wrong.
      The BLACK Rose Hoodie. Heavyweight cotton fleece. Embroidered chest.
      [Edition context if applicable]
      skyyrose.co
```

### Love Hurts

**Voice register:** The bloodline that raised you. Every scar earned.

```
Headline: Worn by those who carry the weight.
Body: Love Hurts Collection.
      For everyone who kept going anyway.
CTA: Shop Love Hurts →
```

### Signature

**Voice register:** Stay golden. Quiet confidence. You already know.

```
Headline: Gold doesn't ask for permission.
Body: Signature Collection by SkyyRose.
      Stay golden.
CTA: Shop Signature →
```

### Kids Capsule

**Voice register:** Little royalty. They inherit what we build.

```
Headline: Raise them like royalty.
Body: Kids Capsule by SkyyRose.
      Premium construction, built for the next generation.
CTA: Shop Kids Capsule →
```

---

## Anti-Patterns

These will kill performance or violate brand canon. Do not do these.

| Anti-Pattern | Why It Fails |
|-------------|-------------|
| Budget in dollars (Meta API) | API expects cents. Wrong unit = 100× overspend or underspend. |
| Mixing collection voices in one ad | Dilutes brand identity; confuses audience signal |
| Urgency timers ("only X hours left!") | Not a SkyyRose brand mechanic. Real scarcity only. |
| SKU in ad copy | Meaningless to consumers; use product name |
| Fabricated testimonials | Brand integrity risk; use bracket templates until real reviews exist |
| Launching broad without pixel warmup | Smart bidding fails without conversion data. Warm pixel first. |
| Performance Max without Merchant Center feed | PMax requires product feed for Shopping placements |
| `preorder` without `availability_date` | Merchant Center rejects. Item won't serve. |
| Smart Shopping campaigns | Sunset by Google. Use Performance Max. |
| `SHOPPING_PRODUCT_ADS` omitted from Shopping ad group | Required enum; ad group creation fails without it |
| Cross-collection visual in one ad | Black Rose silver ≠ Love Hurts crimson ≠ Signature gold — never mix |
| European luxury house references | Wrong brand DNA. The Five only: Kith, Oaklandish, Culture Kings, Fear of God, Palm Angels |
| Hero collection names as type | Collection names = lockup PNG assets. Never rendered as live type in hero positions. |
| Paid spend without STOP-AND-SHOW | Requires explicit confirmation before any spend is committed |

---

## Recovery Guide

### Campaign Not Spending

1. Check campaign/ad set status (paused?)
2. Check budget — is it set in cents (Meta) or micros (Google)?
3. Check bid strategy — COST_CAP/BID_CAP too restrictive?
4. Check audience size (too narrow → delivery fails)
5. Check pixel events — are purchase events flowing?
6. Check ad creative — rejected for policy violation?

### Low ROAS (below break-even)

1. Verify attribution window (Meta: 7-day click + 1-day view is default)
2. Check landing page — UTM tracking intact? Page loads < 3s?
3. Narrow audience — broad audiences need more pixel data before scaling
4. Audit creative — is the hook earning the watch?
5. Check product page — is pre-order messaging clear? Is price visible?
6. Reduce budget to minimum, wait for 50+ purchase events before re-scaling

### CAPI Not Firing (Meta)

1. Events Manager → Events → filter "Server" — any events?
2. Facebook for WooCommerce plugin: Settings → Conversions API → toggle ON
3. Check WooCommerce order flow — purchase event fires on `processing` status
4. Test with Events Manager "Test Events" tool
5. Verify pixel ID matches between plugin config and Events Manager

### Google Shopping Disapprovals

1. Open Merchant Center → Products → Diagnostics
2. Common fixes:
   - `availability_date` missing → add to all preorder SKUs
   - Price mismatch → sync WC price to feed
   - Missing required attributes → check apparel requirements (size, color, gender, age_group)
   - Item not found → verify product URL is live and indexed

### TikTok Spark Ads Underperforming

1. Check organic post engagement rate (need >3% before promoting)
2. Test multiple hooks in parallel — TikTok algorithm rewards fresh creative
3. Verify pixel tracking → TikTok Events Manager → Test Events
4. Audience too narrow? TikTok performs better with broader targeting than Meta at comparable budgets
