---
name: skyyrose-product-copy
description: "Write conversion-optimized product descriptions, collection page copy, and product FAQs for SkyyRose luxury streetwear on WooCommerce. Use when creating or improving product listings, writing collection page descriptions, or generating product FAQ content for skyyrose.co. Delivers ready-to-paste WC REST API field payloads with schema.org-aligned metadata."
allowed-tools: Read Write Edit Glob Grep
---

# SkyyRose Product Copy System

## When to Use This Skill

- Writing new WooCommerce product descriptions for skyyrose.co
- Improving existing product copy that lacks brand voice
- Writing collection page descriptions (Black Rose, Love Hurts, Signature, Kids Capsule)
- Generating product FAQs to reduce pre-purchase hesitation
- Optimizing product SEO (titles, meta descriptions, alt text)
- Creating pre-order product copy with exclusivity (never urgency timers)
- Generating WC REST API-ready JSON payloads for programmatic updates

**DO NOT** use for ad copy (use `skyyrose-paid-media`), email copy (use `skyyrose-email-flows`), or social captions (use `skyyrose-content-engine`).

---

## CRITICAL: Catalog-First Product Resolution

**NEVER use memory, never invent product facts. Every product claim MUST trace to a verified source.**

Resolution order (strict — do not skip steps):

1. **Catalog CSV** — `/Users/theceo/DevSkyy/wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv`
   Columns: `sku, name, price, collection, description, badge, image, front_model_image, back_image, back_model_image, sizes, color, edition_size, published, is_preorder, branding_spec, render_output_slug, render_source_override, render_back_source_override, render_is_tech_flat, render_is_accessory, garment_type_lock, dossier_slug, engine_override`

2. **Per-SKU dossier** — `/Users/theceo/DevSkyy/wordpress-theme/skyyrose-flagship/data/dossiers/{dossier_slug}.md`
   Contains: construction details, gsm/material, narrative canon, founder intent. The dossier is Corey-authored — its words are the source of truth.

3. **User confirmation** — if a fact is absent from CSV + dossier, flag it with `[NEEDS: <fact>]` and proceed. Never fill the gap with invention.

**The lh-005 hallucination ("fanny-pack" → invented specs) was caused by skipping this check. It will not recur.**

Delivery file convention: `{sku}-product-copy.md` saved alongside the dossier, or returned inline as a structured block. The WC REST payload section at the end is always included for copy-paste into WooCommerce admin or API scripts.

---

## Brand Voice Quick Reference

| Element | Rule |
|---------|------|
| Tone | Luxury but grounded, poetic but never pretentious |
| Tagline | "" (period is mandatory) |
| NEVER say | "high-quality", "affordable luxury", "premium", "exclusive" as standalone filler |
| ALWAYS show | Weight (gsm), construction (double-stitched), material specifics from dossier |
| Oakland anchor | "The Town" for Oakland-specific; "Bay Area" is acceptable for regional references |
| Pre-order language | "Limited to X pieces" — NEVER urgency timers, NEVER "Pre-order now" |
| Reading level | 8th grade — short sentences, sensory language, active voice |
| Cross-sell | NONE on PDP. No "Complete the Look", no related products. Garment is the protagonist. |
| Visual refs | The Five: Kith, Oaklandish, Culture Kings, Fear of God, Palm Angels |
| NEVER cite | European luxury houses (Bottega, Rick Owens, Acne, Givenchy, 032c) — wrong DNA |

### Collection Voices — Never Cross-Attribute

| Collection | Voice Register | Accent Color | Canonical Mood |
|-----------|---------------|-------------|----------------|
| **Black Rose** | Defiant, armor, midnight elegance | Silver `#C0C0C0` | "concrete answering back" / "beauty that grows where it shouldn't" |
| **Love Hurts** | Bloodline, passionate, emotionally raw | Crimson `#DC143C` | "Bloodline that raised me" — *Love Hurts ONLY* |
| **Signature** | Confident, golden, West Coast swagger | Gold `#D4AF37` | "stay golden" / "where the fog meets the gold" |
| **Kids Capsule** | Playful, empowering, little royalty | Rose Gold `#B76E79` | "little royalty, big energy" |

Collection names in hero sections = lockup PNG assets (`assets/images/hero-overlays/` or `assets/images/logos/`). Never type-render collection names in hero copy.

---

## WooCommerce REST API Field Map

This table is the canonical bridge between editorial decisions and the WC REST API write payload.
API base: `{site}/wp-json/wc/v3/products/{id}` (POST/PUT). Auth: Basic + consumer key/secret.

| Editorial Field | WC REST Field | Type | Constraint |
|----------------|--------------|------|-----------|
| Product title | `name` | string | 70 chars SEO sweet spot |
| Full description (story + specs) | `description` | HTML string | 300–600 words; wrap in `<p>`, `<ul>`, `<strong>` |
| Above-fold hook | `short_description` | HTML string | 150–200 chars; 1–2 sentences |
| URL slug | `slug` | string | keyword-rich, e.g. `black-rose-hoodie` |
| Price | `regular_price` | string (not number) | e.g. `"40"` — WC requires strings |
| Sale price | `sale_price` | string | `""` when no sale |
| SKU | `sku` | string | From catalog CSV — never invented |
| Collection taxonomy | `categories` | array of `{id: int}` | WC category IDs; resolve via `/wc/v3/products/categories` |
| Product images | `images` | array of `{id, src, alt, name}` | See Image Alt Text section below |
| Variable sizes / colorways | `attributes` | array (see Variable Products section) | |
| SEO title (Yoast) | `meta_data` → key `_yoast_wpseo_title` | `{key, value}` | 60 chars |
| SEO meta desc (Yoast) | `meta_data` → key `_yoast_wpseo_metadesc` | `{key, value}` | 155 chars |
| SEO title (Rank Math) | `meta_data` → key `rank_math_title` | `{key, value}` | 60 chars |
| SEO meta desc (Rank Math) | `meta_data` → key `rank_math_description` | `{key, value}` | 155 chars |
| schema.org material | `meta_data` → key `_schema_material` (or dossier-driven) | `{key, value}` | Plain text, e.g. "French terry 380gsm" |
| schema.org color | `meta_data` → key `_schema_color` | `{key, value}` | From CSV `color` column |
| schema.org size | surfaced via `attributes` `pa_size` | — | Drives JSON-LD `SizeSpecification` |
| FAQ content | `meta_data` → key `_product_faq` (or plugin-specific) | JSON or HTML | 3–5 Q&A pairs |

**STOP-AND-SHOW required** before any WC REST write, media upload, or Klaviyo send. Show exact endpoint, payload, and cost before executing.

### Image Alt Text — First-Class Field

Image alt text is not a footnote. It is a first-class accessibility + SEO field submitted with every image object.

Format: `[Product name] [view] — [one distinguishing detail]`

Examples:
- `"Black Rose Hoodie front view — embroidered rose script on heavyweight black French terry"`
- `"Love Hurts Bomber Jacket back view — large heart-and-rose logo centered on satin body"`
- `"The Fannie front view — heart-and-rose logo at dot of the I in FANNIE"`

Rules:
- Max 125 chars
- Include the product name (matches `name` field)
- Include the view (front / back / detail / flat)
- Include one physical distinguishing detail from the dossier
- Never use the SKU as the alt text

WC REST images array example:
```json
"images": [
  {
    "src": "https://skyyrose.co/wp-content/uploads/br-004-black-rose-hoodie.jpeg",
    "alt": "Black Rose Hoodie front view — embroidered rose script on heavyweight black French terry",
    "name": "Black Rose Hoodie — Front"
  },
  {
    "src": "https://skyyrose.co/wp-content/uploads/black-rose-hoodie-back-model.webp",
    "alt": "Black Rose Hoodie back view — clean black French terry, ribbed hem",
    "name": "Black Rose Hoodie — Back"
  }
]
```

---

## Variable Products — Sizes and Colorways

When a product has multiple sizes or colorways, use WC attributes. Jersey series colorways (br-003 baseball classic variants: Black, Oakland, Giants, White) and Kids Capsule colorblock sets (kids-001 Red/Black, kids-002 Purple/Black) are examples.

### Simple products (single color, multiple sizes)

Most SkyyRose products: set `type: "simple"`, populate `attributes` with size only.

```json
"attributes": [
  {
    "name": "Size",
    "slug": "pa_size",
    "position": 0,
    "visible": true,
    "variation": false,
    "options": ["S", "M", "L", "XL", "2XL", "3XL"]
  }
]
```
Sizes are sourced from the CSV `sizes` column (pipe-delimited: `S|M|L|XL|2XL|3XL`).

### Variable products (multiple colorways)

For products with distinct colorways (e.g., br-003 baseball classic series), set `type: "variable"` on the parent and create child variations.

```json
"attributes": [
  {
    "name": "Size",
    "slug": "pa_size",
    "position": 0,
    "visible": true,
    "variation": true,
    "options": ["S", "M", "L", "XL", "2XL", "3XL"]
  },
  {
    "name": "Colorway",
    "slug": "pa_colorway",
    "position": 1,
    "visible": true,
    "variation": true,
    "options": ["Black", "Oakland", "Giants", "White"]
  }
]
```

Each child variation carries its own `regular_price`, `sku` (e.g., `br-003-black`), `images`, and `attributes` with the specific option values. Edition sizes (e.g., 80 pieces for jersey series) belong on the variation `stock_quantity` when `manage_stock: true`.

Kids Capsule sizes use the child-sizing scale from the CSV (`2T|3T|4T|5|6|7`) — never adult sizing.

---

## Core Workflow

### Phase 1: Gather Product Intelligence

For every product, read in this order:
1. **Catalog CSV** — resolve `sku`, `name`, `price`, `collection`, `sizes`, `color`, `edition_size`, `is_preorder`, `branding_spec`
2. **Dossier** — resolve construction details (gsm, material, stitch spec, placement), narrative canon, founder intent
3. **User input** — any additional context (launch date, special run, Corey's words)

If a required fact is missing from both CSV and dossier, flag it: `[NEEDS: fabric weight]`. Never invent.

### Phase 2: Write the Product Listing

Generate every element in this order:

**1. Product Title**
```
[Collection] [Product Name] — [Key Differentiator]
```
Examples:
- "Black Rose Hoodie — Heavyweight 380gsm French Terry"
- "Love Hurts Varsity Jacket — Full-Grain Leather Sleeves"
- "The Bridge Series 'The Bay Bridge' Shorts — Sublimated Edition"

**2. Short Description (WC `short_description`)**
One to two sentences. Benefit first, then the sensory hook. Delivered as HTML.

Black Rose example:
> Heavyweight French terry that drops like armor. Double-stitched seams, ribbed cuffs, embroidered Black Rose script across the chest.

Love Hurts example:
> Full-grain leather sleeves meet wool-blend body in a varsity silhouette that doesn't ask permission. Chenille "Love Hurts" patch. Hand-finished details throughout.

Signature example:
> Golden hour trapped in cotton. Mint and lavender colorblock hoodie with brushed fleece interior and rose gold hardware.

**3. Long Description (WC `description`)**

```
[Opening hook — 1-2 sentences that set the scene]

[The story — why this piece exists, what it represents]

[Construction details — material, weight, stitching, hardware — sourced from dossier]

[Fit and sizing — how it wears, what to expect]

[Pre-order / exclusivity callout if applicable — no urgency timers]

[CTA — specific, not generic]
```

**4. SEO Elements**
- SEO Title: `[Primary Keyword] — [Brand] | [Collection]` (60 chars)
- Meta Description: 155 chars, benefit + keyword + subtle CTA
- Image alt text per image: see Image Alt Text section above
- URL slug: `/product/[keyword-slug]/`
- SEO fields delivered as `meta_data` array entries (Yoast or Rank Math keys)

**5. Product FAQ (3–5 questions)**
Standard questions to address:
- What's the fabric/material?
- How does it fit? (true to size, oversized, etc.)
- When will pre-orders ship?
- Is this a limited release?
- How do I care for this piece?

### Phase 3: Polish

Run this checklist before delivering:

| Check | Verify |
|-------|--------|
| CSV + dossier sourced | Every fact traces to catalog CSV or dossier — no memory, no invention |
| Collection voice match | Copy sounds like Black Rose / Love Hurts / Signature / Kids — voices not crossed |
| Benefits lead features | Every bullet starts with what you FEEL, not what it IS |
| No unproven superlatives | Zero "best", "#1", "world-class" without proof |
| Sensory language present | Weight, texture, drape, feel are mentioned |
| Pre-order handled correctly | Limited quantity communicated; no urgency timers |
| SEO complete | Title (60c), meta (155c), alt (125c), slug all present |
| Character limits met | All fields within WC limits |
| No banned phrases | No "high-quality", "affordable luxury", "premium" as filler |
| CTA is specific | "Claim yours" beats "Add to cart" |
| Oakland/Bay reference | Natural cultural reference where authentic to the piece |
| No cross-sell on PDP | Zero "Complete the Look", zero related products |
| Image alt text | Every image object has a populated `alt` — not empty, not the SKU |

### Phase 4: Deliver

Output structure for every product:

1. **Editorial preview** — formatted copy for human review
2. **WC REST API payload** — copy-paste JSON block with all fields populated
3. **Delivery path** — `{sku}-product-copy.md` saved to the project dossiers dir if writing to file

---

## WC REST API Payload Template

```json
{
  "name": "Black Rose Hoodie — Heavyweight French Terry",
  "slug": "black-rose-hoodie",
  "type": "simple",
  "status": "publish",
  "sku": "br-004",
  "regular_price": "40",
  "sale_price": "",
  "short_description": "<p>Heavyweight French terry that drops like armor. Double-stitched seams, ribbed cuffs, embroidered Black Rose script across the chest. Built in The Town. Limited pre-order.</p>",
  "description": "<p>Some hoodies you wear. This one wears a reputation.</p>\n<p>The Black Rose Hoodie is 380gsm French terry — dense enough to cut wind, soft enough to live in...</p>",
  "categories": [{"id": 0}],
  "images": [
    {
      "src": "https://skyyrose.co/wp-content/uploads/br-004-black-rose-hoodie.jpeg",
      "alt": "Black Rose Hoodie front view — embroidered rose script on heavyweight black French terry",
      "name": "Black Rose Hoodie — Front"
    }
  ],
  "attributes": [
    {
      "name": "Size",
      "slug": "pa_size",
      "position": 0,
      "visible": true,
      "variation": false,
      "options": ["S", "M", "L", "XL", "2XL", "3XL"]
    }
  ],
  "meta_data": [
    {"key": "_yoast_wpseo_title", "value": "Black Rose Hoodie — SkyyRose Heavyweight Streetwear"},
    {"key": "_yoast_wpseo_metadesc", "value": "380gsm French terry hoodie with embroidered Black Rose script. Double-stitched, built in Oakland. Limited pre-order from SkyyRose."},
    {"key": "rank_math_title", "value": "Black Rose Hoodie — SkyyRose Heavyweight Streetwear"},
    {"key": "rank_math_description", "value": "380gsm French terry hoodie with embroidered Black Rose script. Double-stitched, built in Oakland. Limited pre-order from SkyyRose."},
    {"key": "_schema_material", "value": "French terry 380gsm"},
    {"key": "_schema_color", "value": "Black"}
  ]
}
```

---

## Example: Black Rose Hoodie (br-004, $40, PRE-ORDER)

*Source: catalog CSV row br-004 + dossier black-rose-hoodie.md. All facts verified.*

### Product Title (44/70 chars)
```
Black Rose Hoodie — Heavyweight French Terry
```

### Short Description
```html
<p>Heavyweight French terry that drops like armor. Double-stitched seams, ribbed cuffs, embroidered Black Rose script across the chest. Built in The Town. Limited pre-order.</p>
```

### Long Description
```html
<p>Some hoodies you wear. This one wears a reputation.</p>

<p>The Black Rose Hoodie is 380gsm French terry — dense enough to cut wind, soft enough to live in. The kind of weight that reminds you it's there every time you move. Every seam is double-stitched. The ribbed cuffs hold their shape season after season. The Black Rose script across the chest is embroidered, not printed — because print fades. Embroidery doesn't.</p>

<p>This is the Black Rose Collection: dark, deliberate, Oakland to the core. Named for the beauty that grows where it shouldn't. Where others see concrete, we see potential.</p>

<p><strong>CONSTRUCTION</strong></p>
<ul>
<li>380gsm French terry (heavyweight — this is not a fast-fashion fleece)</li>
<li>Double-stitched seams throughout</li>
<li>Embroidered Black Rose script — front chest</li>
<li>Ribbed cuffs and hem</li>
<li>Brushed interior</li>
<li>Kangaroo pocket with reinforced edges</li>
</ul>

<p><strong>FIT</strong><br>Relaxed fit, true to size. If you want oversized, size up one.</p>

<p><strong>PRE-ORDER</strong><br>Limited release. Once they're gone, they're gone. Ships within 4–6 weeks of order close.</p>

```

### SEO
```
SEO Title:    "Black Rose Hoodie — SkyyRose Heavyweight Streetwear"  (52/60 chars)
Meta Desc:    "380gsm French terry hoodie with embroidered Black Rose script. Double-stitched, built in Oakland. Limited pre-order from SkyyRose."  (131/155 chars)
URL slug:     black-rose-hoodie
```

### Image Alt Text
```
Front:  "Black Rose Hoodie front view — embroidered rose script on heavyweight black French terry"  (88/125)
Back:   "Black Rose Hoodie back view — clean black French terry construction, ribbed hem"  (79/125)
```

### Product FAQ
```
Q: What's the fabric weight?
A: 380gsm French terry — significantly heavier than standard hoodies (typically 250–280gsm). You'll feel the difference immediately.

Q: How does it fit?
A: Relaxed fit, true to size. For an oversized silhouette, go up one size.

Q: When does my pre-order ship?
A: Pre-orders ship within 4–6 weeks of the order window closing. You'll receive tracking via email.

Q: Is this a limited release?
A: Yes. Once pre-order quantities are reached, this run is closed. We don't do restocks on every drop.

Q: How do I care for this hoodie?
A: Machine wash cold, inside out. Tumble dry low or hang dry. The embroidery is built to last — no special treatment needed.
```

---

## Example: The Bridge Series 'The Bay Bridge' Shorts (sg-001, $195, PRE-ORDER)

*Source: catalog CSV row sg-001. Dossier: the-bridge-series-the-bay-bridge-shorts.md if available.*

### Product Title (56/70 chars)
```
The Bridge Series 'The Bay Bridge' Shorts — Limited Edition
```

### Short Description
```html
<p>The bridge between streetwear and statement piece. Full-length sublimated Bay Bridge imagery, embroidered rose, gold hardware. 250 pieces. That's it.</p>
```

### Long Description
```html
<p>The Bay Bridge isn't just infrastructure. It's identity. Two cities connected by steel and intention — and these shorts carry that same energy.</p>

<p>The Bridge Series 'The Bay Bridge' Shorts cover every inch in sublimated Bay Bridge imagery, shot at golden hour. The embroidered rose lands bottom-left — deliberate, not decorative. The entire piece is built around one visual argument: West Coast luxury has an address.</p>

<p>This is Signature Collection. Gold hardware. Confident construction. The exact cut that sits clean whether you're walking Lakeshore or sitting courtside.</p>

<p><strong>CONSTRUCTION</strong></p>
<ul>
<li>Full-length sublimated Bay Bridge imagery — front and back</li>
<li>Embroidered rose — bottom-left thigh</li>
<li>Elastic waistband with external drawstring</li>
<li>Reinforced pockets</li>
</ul>

<p><strong>FIT</strong><br>True to size. Athletic cut, hits at mid-thigh.</p>

<p><strong>PRE-ORDER</strong><br>Limited to 250 pieces. Ships within 4–6 weeks of order close.</p>

<p></p>
```

---

## Collection Page Copy

### Template Structure

```
## H1: [Collection Name] Collection — [Positioning Line]

### Above-Fold Intro (2–3 sentences)
[What the collection is + who it's for + emotional hook, using collection voice only]

### Below-Grid SEO Description (200–300 words)
[Story → what's included → how to choose → internal links]

### Meta Title / Description
[SEO-optimized with collection keywords]
```

**Collection hero name = lockup PNG asset. Do not type-render the collection name.**

### Black Rose Collection Page Example

**H1:** "Black Rose Collection — Dark Elegance from The Town"

**Intro:** "The Black Rose Collection is midnight given form. Built for those who find beauty in darkness and wear their Oakland roots like armor. Limited edition streetwear that doesn't whisper — it announces."

**Below-Grid Description:**
"Every piece in the Black Rose Collection carries the same DNA: heavyweight construction, dark palettes, and details that reveal themselves over time. From the signature Black Rose Hoodie to the limited-edition jersey series celebrating Bay Area sports culture, Black Rose is where luxury streetwear meets Oakland identity.

The jersey series — limited to 80 pieces each — draws from the Bay's sports legacy: SF-inspired (football), Last Oakland (football), The Bay (basketball), The Rose (hockey), and Last Oakland Baseball. Each features the exclusive 'BLACK IS BEAUTIFUL' design with alternating rose-filled numbers and collection-specific patches.

Whether you're starting with the Black Rose Crewneck or going all-in on the Sherpa Jacket, every piece is built to layer, built to last, and built to be seen.

Browse the full Black Rose lineup below."

**Meta Title:** "Black Rose Collection — Limited Edition Oakland Streetwear | SkyyRose" (67 chars)
**Meta Desc:** "Dark elegance from The Town. Heavyweight hoodies, limited jerseys, and statement streetwear. Limited runs. Pre-order from SkyyRose." (132/155 chars)

---

## Anti-Patterns

- **DO NOT** write generic product copy — "This comfortable hoodie is made with quality materials" could be any brand
- **DO NOT** lead with features — "100% cotton" means nothing without "Softer than anything in your closet"
- **DO NOT** use "affordable luxury" — SkyyRose IS luxury. Period.
- **DO NOT** skip the cultural reference — every collection is rooted in a place and a story
- **DO NOT** write walls of text — use line breaks, bullets, sections for scannable listings
- **DO NOT** use generic CTAs — "Claim yours" beats "Add to cart"
- **DO NOT** fabricate specs — if you don't know the gsm or material, flag it with `[NEEDS: fabric weight]`
- **DO NOT** skip pre-order status — every pre-order product must communicate limited availability
- **DO NOT** add urgency timers or countdown language — founder rule, not a stylistic preference
- **DO NOT** reference related products or cross-sells on PDP — garment is the protagonist
- **DO NOT** cross-attribute collection voices — "bloodline" is Love Hurts ONLY; "armor/concrete" is Black Rose ONLY
- **DO NOT** leave image `alt` fields empty — every image object in the API payload must have alt populated
- **DO NOT** use the SKU as the product title or alt text — products are named from the catalog
- **DO NOT** cite European luxury houses as visual references — use The Five only

---

## Recovery

- **User gives minimal product info:** Read the catalog CSV first. Resolve name, collection, price, sizes from CSV. Read dossier for construction. Only ask if CSV + dossier are both silent on a required fact.
- **Unknown fabric/material specs:** Write around the gap with sensory language and flag `[NEEDS: material specs]`. Never invent a gsm number.
- **Product doesn't fit a collection voice:** Default to Signature voice (most versatile) and note for user review.
- **Existing copy needs improvement:** Read current copy, identify top 3 weaknesses, rewrite with before/after comparison.
- **Variable product with colorways:** Use the `attributes` + `type: "variable"` pattern above. Source colorway names from CSV `color` column.
- **Kids Capsule sizing:** Use `2T|3T|4T|5|6|7` from CSV — never substitute adult sizing.
- **SEO plugin unknown:** Deliver both Yoast (`_yoast_wpseo_*`) and Rank Math (`rank_math_*`) keys in `meta_data` — only one set will be active; the other is ignored by WC.
