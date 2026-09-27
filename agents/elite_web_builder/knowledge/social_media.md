# Social Media Agent — Knowledge Reference

**Catalog source of truth:** `wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv`. Every post references a real SKU. Never invent product names or prices.

The Social Media sub-agent generates platform-specific captions, hashtags, campaigns, and content calendars. It pairs with the Imagery Agent (who supplies visuals) and the SEO Content Agent (who supplies long-form copy). Production output is consumed by `frontend/app/api/social-media/generate/route.ts` or scheduled via Klaviyo / Meta Business Suite.

---

## Brand voice (non-negotiable)

- **Only tagline:** ``
- **Retired (NEVER use):** `Where Love Meets Luxury`, `#WhereLoveMeetsLuxury`
- **Brand name:** SkyyRose (one word). "Skyy Rose" only when referring to the founder's daughter by name.
- **Founder:** Corey Foster (Oakland). Brand named after his daughter, Skyy Rose.
- **Voice:** confident, emotionally resonant, culturally aware. Oakland street meets high fashion. Storytelling over selling. No AI-giveaway phrases ("In today's fast-paced world…"). No generic CTAs ("Check it out!", "Don't miss out!"). No em-dashes.

---

## Collection voices (strict)

| Collection | Accent | Voice | Setting |
|------------|--------|-------|---------|
| Black Rose | `#C0C0C0` silver | Gothic, cathedral-inspired, monochrome luxury | Industrial Oakland at night |
| Love Hurts | `#DC143C` crimson | Dramatic, vulnerability-as-strength, baroque | Weathered brick, candlelit |
| Signature | `#B76E79` rose gold + `#D4AF37` gold | Bay Area elevated, golden-hour, approachable luxury | Bay Bridge backdrop |
| Kids Capsule | `#FFB6C1` pink + `#E6E6FA` lavender | Joyful confidence, legacy, scaled-down not dumbed-down | Clean Oakland street |

---

## Platform guardrails

| Platform | Char limit | Hashtags | Voice |
|----------|-----------|----------|-------|
| Instagram | ≤ 2200 | 5–8 on their own line | Aesthetic, aspirational, line breaks for readability, end with CTA |
| TikTok | ≤ 300 | 3–5 inline | Gen-Z, trend-aware, hook-driven, conversational |
| X / Twitter | ≤ 280 | 2–3 | Sharp, quotable, retweetable |
| Facebook | ≤ 500 | 3–4 | Warm, community-focused, conversation starter (question or prompt) |

---

## Content types

1. **product_launch** — single SKU drop announcement, all 4 platforms. Pair with Imagery Agent's product shot.
2. **collection_drop** — multi-day campaign for a full collection (3 products × 4 platforms × 7 days = 84-post calendar).
3. **lifestyle** — storytelling post that weaves product into brand narrative.
4. **ugc_seed** — customer-facing prompt / template kit to encourage user-generated content.
5. **ad_creative** — paid headlines + primary text + CTAs with A/B hypotheses (Meta, TikTok, Pinterest).
6. **editorial** — long-form brand narrative (founder's journey, "why Oakland", "why Signature matters").

---

## Output format (JSON, strict schema)

```json
{
  "sku": "br-005",
  "collection": "black-rose",
  "platform": "instagram",
  "content_type": "product_launch",
  "caption": "…",
  "hashtags": ["#SkyyRose", "", "..."],
  "imagery_brief": {
    "style": "flat-lay | on-model | lifestyle | editorial",
    "mood_notes": "…",
    "required_elements": ["garment front", "rose embroidery detail"]
  },
  "scheduled_at": "2026-04-22T18:00:00-07:00 | null",
  "paired_post_ids": ["..."]
}
```

The `imagery_brief` block is the hand-off to the Imagery Agent — every post describes the visual it needs.

---

## Hashtag strategy

Every post gets a baseline bundle:
```
#SkyyRose  #LuxuryStreetwear #{collection_no_dashes}
```
Platform-specific additions:
- IG: `#NewDrop #FashionForward #OOTD #StreetLuxury` (pick 1–4)
- TikTok: `#NewDrop #FashionTok` (pick 1–2)
- X: just baseline (max 3)
- FB: baseline + `#Fashion`

Do NOT use trending hashtags that contradict brand voice (e.g., `#SaleAlert`, `#MondayMotivation`).

---

## Campaign orchestration

For a collection drop, produce a **7-day content calendar**:

| Day | IG | TikTok | X | FB |
|-----|-----|--------|---|-----|
| -3  | Teaser: founder voiceover | Teaser: 1-frame flash | Thread: "What's coming" | Community question |
| -2  | Detail close-up | Reveal 50% | Countdown | Recap day-1 engagement |
| -1  | Full reveal lookbook | Full reveal + audio trend | "Drop tomorrow 6pm PT" | Launch party invite |
| 0   | Hero shot + pre-order CTA | POV unboxing | Drop live + link | Shop now |
| +1  | UGC repost | Duet prompt | Thank-yous | Styling guide |
| +2  | Styling tips carousel | Styling hack | Styling poll | FAQ thread |
| +3  | Customer spotlight | "Why it sold out" | Restock signal | Next drop tease |

---

## Integration points

- **Copy generation:** `frontend/app/api/social-media/generate/route.ts` — Claude Sonnet 4.6 via Vercel AI SDK.
- **Scheduling:** Klaviyo (email) + Meta Business Suite (IG/FB) + TikTok Ads Manager.
- **Analytics:** `frontend/app/admin/social-media/page.tsx` dashboard pulls from `/api/social-media/analytics`.
- **Asset storage:** Posts reference images produced by the Imagery Agent under `wordpress-theme/.../assets/images/products/` and `assets/images/social/`.
