---
name: skyyrose-photography-brief
description: "Produces a photographer-ready brief for any SkyyRose photography session — product/e-commerce shots (PDP catalog: hero front, angle, back, detail, flat-lay, on-body, lifestyle) AND brand/lifestyle/founder/campaign/BTS sessions. Covers per-collection visual direction, lighting, shot-list tables, platform crop specs (WooCommerce PDP, IG, Stories/Reels, Pinterest, web hero, email), file naming, styling, AVOID list, and Elite Studio handoff. Merges both product-photography and brand-photography briefs into a single unified workflow with session-type routing."
allowed-tools: Read Write Edit Glob
triggers:
  - photography brief
  - shot list
  - product photography
  - brand shoot
  - art direction
  - PDP images
  - founder shoot
  - campaign brief
  - lifestyle shoot
  - BTS photography
---

# SkyyRose Photography Brief

## When to Use This Skill

Use this skill to produce a photographer-ready brief for any SkyyRose session:

- **Product / e-commerce sessions:** WooCommerce PDP catalog images, flat lay, garment detail macros, on-body fit shots — assets that feed the product detail page and Elite Studio pipeline
- **Brand / lifestyle sessions:** Editorial campaigns, collection launches, founder story, community lifestyle, behind-the-scenes — assets that feed IG feed, website heroes, lookbooks, and press
- **Mixed sessions:** Single shoot day covering both product catalog and brand narrative angles

This skill routes automatically to the correct brief structure after intake. No need to select between product and brand separately.

---

## Section 1: Brand Canon Gate

Non-negotiable. These rules apply to every brief produced by this skill, regardless of session type.

### The Five — Exclusive Visual References

Pull from these five brands **only**. Every mood board reference, every lighting direction, every styling comparison must trace back to one of The Five:

| Brand | What It Contributes to SkyyRose Briefs |
|-------|---------------------------------------|
| **Kith** | Editorial product storytelling, elevated retail polish, restrained campaign composition |
| **Oaklandish** | Authentic town pride visible even in product styling, community rootedness, Oakland as identity |
| **Culture Kings** | Bold streetwear merchandising, hype-energy presentation, garment as centerpiece |
| **Fear of God** | Quiet luxury — let the garment speak through restraint, tonal silhouette work |
| **Palm Angels** | Street-luxe graphic confidence, garment as statement, confident motion |

**Never** reference: Bottega Veneta, Hedi Slimane, Rick Owens, 032c, Acne Studios, Givenchy-by-Tisci, Celine, Balenciaga, Vetements, or any European luxury-house lineage. Wrong brand DNA. Including them in a brief sends the shoot in the wrong direction.

### Lockup Rule — Collection Name Is Never Type-Rendered

The collection name must **never** appear as typed text in any photograph — product shot, hero frame, Reel cover, or BTS content. If a hero crop will carry a collection-name title treatment, the photographer leaves **clean negative space** at the top of frame. The lockup asset is composited at the Elite Studio stage:

- Black Rose, Love Hurts, Signature → `assets/images/hero-overlays/`
- Kids Capsule → `assets/images/logos/`

Fonts (Archivo, Hanken Grotesk, Anton, Cinzel, Inter) are for interior copy surfaces only — never for the collection name itself, and never burned into photography.

### Color Tokens (verbatim, enforce in grade direction)

| Token | Hex | Collection |
|-------|-----|-----------|
| Rose Gold | `#B76E79` | Global brand accent / Kids Capsule |
| Dark | `#0A0A0A` | Global background |
| Silver | `#C0C0C0` | Black Rose accent |
| Crimson | `#DC143C` | Love Hurts accent |
| Gold | `#D4AF37` | Signature accent |

### Tagline

No tagline is authorised (founder decision 2026-10-06). Never use or invent one; any tagline in a brief is a violation.

### Products by Name, Not SKU

Briefs reference products by human-readable name: "Black Rose Crewneck" — not "br-001." Photographers don't work from internal SKUs. SKU-first briefing has caused product conflations in past sessions.

### Catalog Source — Mandatory Before Briefing

Product facts (colorways, materials, features, graphic details) resolve from:

1. `wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv` (33 SKUs)
2. Per-SKU dossier files (in the same directory)

Never invent product details from memory. If a selling point isn't confirmed in the CSV or dossier, it doesn't go in the brief.

### Founder Canon

Corey Foster is the founder — not a fashion model. Founder shots read as earned, direct, Oakland-grounded. No boardroom pointer, no crossed-arms power pose, no jet stairs. Real Corey beats posed Corey every time.

### No Cross-Sell / No Urgency Timers / No Related Products on PDP

The garment is the protagonist. One piece, one story per frame.

---

## Section 2: Session Type Routing

After intake (Section 3), route the brief to the correct structure:

| Session Type | Definition | Sections Used |
|-------------|------------|---------------|
| **Product** | Garment-centric catalog photography — flat lay, on-body, detail macros for WooCommerce PDP and social product use | Sections 4 → 6A → 7 → 8 → 9 → 10 → 11 → 12 |
| **Brand** | Storytelling sessions featuring talent, Oakland locations, campaign/lifestyle/founder/BTS narrative | Sections 4 → 6B → 7 → 8 → 9 → 10 → 11 → 12 |
| **Mixed** | Single session covering both product catalog and brand narrative | Sections 4 → 6A + 6B → 7 → 8 → 9 → 10 → 11 → 12 |

**30-shot half-day ceiling:** Flag to the user if the combined shot list exceeds 30 shots for a half-day session. Recommend splitting sessions. Rushed shots are unusable shots.

---

## Section 3: Brief Intake

Gather every field before producing a brief. If the user has already provided these, skip directly to Section 4.

| Input | Question | Notes |
|-------|----------|-------|
| **Session type** | Product, brand, or mixed? | Sets which shot-list branch(es) to build |
| **Collection(s)** | Black Rose / Love Hurts / Signature / Kids Capsule? | Sets entire visual direction block — do not blend |
| **Product names** | Which specific products are featured? | By NAME from catalog CSV — e.g. "Black Rose Crewneck." Never invent. |
| **Variants** | Colorways or sizes that differ visually? | Requires separate hero-front for each variant |
| **Session purpose** | WooCommerce catalog launch, IG campaign, evergreen lifestyle, founder story, BTS, lookbook? | Determines shot priority |
| **Platforms** | WooCommerce PDP, IG Feed, Stories/Reels, Pinterest, web hero, email? | Determines which crop ratios are required |
| **Talent** | Flat lay only / hands or partial model / full model / founder Corey? | Affects shot categories |
| **Location** | Oakland-anchored, studio, or other? | Oakland-first preferred; see per-collection backgrounds |
| **Scope** | Shot count target and session length (half-day / full-day)? | Caps at 30 for half-day; see routing note above |
| **Deadline** | Shoot date and delivery deadline | Affects shot count recommendation |

**GATE:** Do not proceed without collection and session purpose confirmed.

---

## Section 4: Per-Collection Visual Direction

Apply the correct block to every shot in the brief. Do not blend collections within a single frame. If shooting a mixed-collection session, complete all shots for one collection before changing the set.

### Black Rose — Dark Precision

- **Register:** Gothic luxury. Twilight, shadow architecture, defiant elegance. Armor — "you already stood up," "concrete answering back."
- **Palette:** Dark `#0A0A0A` dominant; Silver `#C0C0C0` for hardware and accent details; deep charcoal, slate.
- **Hero/flat-lay background:** Matte black seamless, dark concrete (#0A0A0A), or dark slate surface.
- **Lifestyle/brand background:** Raw concrete wall, industrial iron gate, wet asphalt, rusted corrugated metal, foggy Oakland waterfront, West Oakland warehouse exteriors.
- **Lighting — hero/flat lay:** Dual softbox at 45 degrees each side; add edge light from above or directly behind to separate dark garment from dark ground; white fill card below to preserve shadow detail without creating hot spots.
- **Lighting — detail/macro:** Single directional key at 20–30 degrees from left, raking across texture; no fill — shadow defines the weave, print, or embroidery. Must be raking. Never flat overhead for detail shots.
- **Lighting — lifestyle/brand:** Low-key dramatic. Single key from camera-left or above casting strong defined shadow. Reflector to preserve fabric detail — not to fill the darkness. Chiaroscuro acceptable.
- **Color temperature:** Cool-neutral throughout. No warm grade. No gold shift.
- **Styling:** Matte fabrics, silver hardware and accessories **only** — no gold, no warm props, no shiny or glossy outerwear.
- **References:** Fear of God tonal restraint + Palm Angels street-luxe graphic confidence + Oakland post-industrial grit.
- **AVOID:** White backgrounds, warm or golden color grading, soft-light evenly-lit product aesthetic, floral props, European fashion-week staging (clean white studio, floating fabric, motion blur for art), anything that reads soft or aspirationally luxe in the European register, warm-toned surfaces (wood, linen, cream).

### Love Hurts — Crimson Heat

- **Register:** Street passion, raw romance, crimson heat. "The bloodline that raised me." High tension — not romance-novel soft.
- **Palette:** Crimson `#DC143C` hits against dark grounds; deep reds, near-blacks, dark maroon.
- **Hero/flat-lay background:** Deep red brick (if prop available), dark maroon seamless, or black.
- **Lifestyle/brand background:** Cracked sidewalk, red-brick alley walls, chain-link, neon-lit corridors, dark wood with crimson accent prop.
- **Lighting — hero/flat lay:** Dual softbox; a subtle red-gel fill on one side is acceptable to warm the shadow areas on dark garments.
- **Lighting — detail/macro:** Directional from left, warm color temp; let crimson elements glow slightly. Raking for texture definition.
- **Lighting — lifestyle/brand:** High-contrast. Dramatic shadows and crimson color gels acceptable. Dusk or sunset for outdoor. Warm strobe with slight red cast acceptable.
- **Color temperature:** Warm-dramatic; lifted contrast. Not cool-neutral — that reads Black Rose.
- **Styling:** Bold silhouettes, crimson accessories, red-toned props. Tension in the frame.
- **References:** Culture Kings hype energy + Oaklandish authenticity + Palm Angels street-luxe.
- **AVOID:** Pink or pastel props, Valentine's Day clichés (florals, soft-focus romance, hearts), European editorial detachment, cool or blue-toned lighting (reads Black Rose), anything saccharine or commercially soft.

### Signature — West Coast Gold

- **Register:** West Coast luxury, elevated, worldwide respect. "Stay golden." California identity as luxury.
- **Palette:** Gold `#D4AF37` in light and accessories; warm neutrals — cream, amber, warm white, natural stone.
- **Hero/flat-lay background:** Warm cream, natural stone, warm white seamless, light-toned wood.
- **Lifestyle/brand background:** Sunlit Oakland streets, stadium steps, rooftop with Bay Area horizon, eucalyptus groves, warm wood desk, cream linen, golden-hour outdoor.
- **Lighting — hero/flat lay:** Natural window light or softbox with warm gel; even and bright; slight shadow on right for dimension. Morning or late-afternoon quality.
- **Lighting — detail/macro:** Warm directional — morning window light from left reveals texture without harshness.
- **Lighting — lifestyle/brand:** Natural golden hour outdoor, or warm studio approximation. California outdoor preferred.
- **Color temperature:** Warm-golden. No cool shift — that reads Black Rose.
- **Styling:** Layered premium basics, gold jewelry, warm leather goods as props, clean sneakers, neutral wood and linen surfaces.
- **References:** Kith editorial polish + Oaklandish community rootedness + Fear of God quiet luxury.
- **AVOID:** Cool or blue-toned lighting, industrial or dark backgrounds (reads Black Rose), beach/surf lifestyle (wrong register), tech-bro minimalism, European neutral palette, anything that reads cold or commercial.

### Kids Capsule — Bright Royalty

- **Register:** Little royalty. Heritage passed down, playful-premium. Not childish — aspirational and warm.
- **Palette:** Rose Gold `#B76E79` dominant; soft cream, warm white.
- **Hero/flat-lay background:** White seamless, warm white, or soft cream.
- **Lifestyle/brand background:** Neighborhood park, Oakland mural wall (if color-consistent with the collection), clean studio with warm backdrop.
- **Lighting — hero/flat lay:** Bright and even — dual softbox, white reflectors, no dramatic shadow; kids' pieces need clarity and warmth, not mood.
- **Lighting — detail/macro:** Soft directional, minimal shadow, high brightness.
- **Lighting — lifestyle/brand:** Natural outdoor light — morning or overcast. Never direct harsh midday sun. Warmth over drama.
- **Color temperature:** Bright-neutral with warm bias. No moody grades.
- **Styling:** Kids in full looks. Parents (Corey when relevant) in matching or complementary Signature pieces. Props: minimal — a ball, a book, a simple toy (nothing branded outside SkyyRose). Rose gold and neutral accessories.
- **References:** Oaklandish community warmth + Kith editorial storytelling at kid-scale + Culture Kings energy (scaled down).
- **AVOID:** Dark backgrounds, dramatic or moody lighting, adult editorial aesthetics, overly cute/saccharine styling ("happy family" stock-photo setups), anything that reads Black Rose or Love Hurts.

---

## Section 5: Shot Type Reference Table

Full cross-reference of both branches. Every shot type, its purpose, and primary destination.

| Shot Type | Branch | Purpose | Primary Destination |
|-----------|--------|---------|-------------------|
| Hero front | Product | First impression, PDP main image | WooCommerce PDP main thumbnail, IG square |
| Hero angle | Product | Depth, shape, garment dimension | PDP gallery slot 2 |
| Back view | Product | Full garment — rear construction, brand mark | PDP gallery slot 3 |
| Detail / macro — primary | Product | Key selling point: fabric, print, embroidery, hardware | PDP gallery, social close-up |
| Detail / macro — secondary | Product | Secondary construction detail (collar, tag, zipper) | PDP gallery, social detail |
| Flat lay | Product | Clean editorial, collection grouping | Pinterest 2:3, editorial use |
| On-body / scale | Product | Fit, drape, proportion — hands or partial model | PDP gallery, IG 4:5, social ads |
| Lifestyle in-use | Product/Brand | Garment worn in real context | IG Feed, social ads, PDP |
| Packaging / unboxing | Product | Brand experience, delivery moment | IG Stories, email |
| Variant comparison | Product | Two colorways side by side | PDP, IG carousel |
| Collection group | Product/Brand | Multiple pieces from same collection | Collection page header, IG |
| Hero lockup-ready | Brand | Primary campaign image — negative space above for lockup overlay | Website hero, IG Feed, Pinterest |
| Lifestyle — motion | Brand | Subject walking/in motion in Oakland location | IG Reel cover, TikTok |
| Lifestyle — candid | Brand | Unguarded moment in location | IG Feed, brand story pillar |
| Lifestyle — environmental wide | Brand | Subject small in large Oakland location | Website editorial, press |
| Lifestyle — community | Brand | Two or more subjects — brotherhood/sisterhood | Culture pillar content |
| Lifestyle — trailing back | Brand | Subject from behind, garment back detail prominent | IG Feed, Pinterest |
| Founder — direct | Brand | Corey direct eye contact, minimal background | Press kit, About page |
| Founder — environmental | Brand | Corey in Oakland setting — purposeful, in his city | Brand Story pillar |
| Founder — hands-on | Brand | Corey handling product, adjusting tag, reviewing production | BTS pillar |
| Founder — candid | Brand | Natural laugh or off-guard moment | Community pillar |
| Founder — legacy | Brand | Corey with Skyy Rose (daughter) — if appropriate | Brand Story / About |
| BTS — behind camera | Brand | DP or photographer working | Stories, TikTok |
| BTS — wardrobe rack | Brand | SkyyRose pieces backstage | Stories |
| BTS — styling table | Brand | Tags, accessories, brand packaging overhead | Stories, Pinterest |

---

## Section 6A: Product Shot List Template

Use for catalog sweeps (WooCommerce PDP launches) and single-product deep-dives.

### Standard 7-Shot Catalog Template

All seven are required for every product added to the WooCommerce catalog. This is the minimum viable set for PDP launch.

| Priority | Shot | Description | Framing | Lighting | Background |
|----------|------|-------------|---------|----------|------------|
| 1 | Hero front | Garment centered, straight-on, main face and graphic visible | Product fills 75% of frame, centered, camera slightly above horizontal | Per-collection — see Section 4 | Per-collection |
| 2 | Hero angle | 3/4 view from left showing depth, shape, shoulder, and sleeve seam | 30-degree angle, medium | Dual softbox, slight shadow right for depth | Per-collection |
| 3 | Back view | Full reverse — rear construction, back hem, any exterior brand mark | Straight-on, match hero front framing exactly | Match hero front lighting | Same as hero |
| 4 | Detail — primary | Fabric texture, print, embroidery, or hardware — the key selling point of this product | Macro, tight crop — 2–6 inch area depending on detail size | Single raking key at 20–30 degrees from left; no fill | Neutral/blurred |
| 5 | Flat lay | Garment laid flat — collar up slightly to show neck opening, sleeves extended, garment fills 70% of frame | Overhead, centered | Even overhead diffused; dual softbox with diffusion panel overhead | Per-collection surface |
| 6 | On-body / scale | Garment worn — hands/partial model to show fit, drape, and proportion | Medium, waist-up or full-body depending on garment type | Per-collection lifestyle lighting | Per-collection location or background |
| 7 | Lifestyle in-use | Garment worn in a real SkyyRose context | Medium-wide, environmental | Per-collection | Per-collection location |

### Extended Shot List (single-product deep-dive — add to the 7-shot base)

| # | Shot | Description | Notes |
|---|------|-------------|-------|
| 8 | Detail — secondary | Second construction detail (e.g. tag, zipper, collar rib, hem stitch) | Specify exact framing + lighting per garment |
| 9 | Folded / packaged | Garment folded as shipped, with tissue or packaging visible | For email/unboxing content and Stories |
| 10 | Variant comparison | Two colorways side by side | Required if product has variants that differ visually |
| 11 | Collection group | Product alongside 1–2 other pieces from same collection | Collection page use, IG carousel |
| 12 | Close-up on-body detail | Zoom on a feature while worn — collar at neck, cuff at wrist, waist graphic | PDP gallery, social detail content |

---

## Section 6B: Brand Shot List Template

Use for lifestyle, editorial, campaign, founder, and BTS sessions.

### Hero Shots (3–5 shots per collection)

Primary images for campaign landing, homepage, IG feed anchors. Must be **lockup-ready** — clean negative space at top of frame. Collection name is never type-rendered in any hero.

| # | Description | Framing | Mood/Energy | Platform |
|---|-------------|---------|-------------|---------|
| H1 | Full look, talent stationary against primary location backdrop | Wide, centered, ample negative space above head for lockup overlay | Per-collection register — see Section 4 | IG Feed 4:5 / Website hero |
| H2 | Three-quarter turn, light catching garment construction detail | Medium, rule of thirds | Confident, unhurried | IG Feed 4:5 |
| H3 | Product hero — garment flat or draped on textured surface, no model | Overhead or 45-degree angle | Editorial, clean | Pinterest 2:3 |

### Lifestyle Shots (5–8 shots)

Product in real SkyyRose world — Oakland streets, community settings, authentic motion.

| # | Description | Framing | Mood | Platform |
|---|-------------|---------|------|---------|
| L1 | Subject walking toward camera in location | Medium-wide, motion, slight blur at edges | In motion, confident | IG Reel cover / TikTok |
| L2 | Subject in candid moment — checking phone, looking off-frame, adjusting piece | Medium, environmental | Real, earned | IG Feed |
| L3 | Environmental wide — subject small in a large Oakland location | Wide, subject off-center | The Town as backdrop | Website, editorial |
| L4 | Two subjects together (community frame) | Medium, both in frame | Brotherhood/sisterhood — not romance | Culture pillar |
| L5 | Subject from behind, walking away — garment back detail prominent | Medium, trailing | Directional, editorial | IG Feed / Pinterest |

### Detail Shots (3–5 shots)

Construction, craft, brand marks. Feed into product pipeline and social close-up gallery.

| # | Description | Framing | Lighting | Platform |
|---|-------------|---------|----------|---------|
| D1 | Fabric texture or embroidery under directional light | Macro, tight crop | Raking from left, no fill | Product page detail |
| D2 | Hardware, zipper pull, or label close-up | Macro, 30-degree angle | Directional, cool or warm per collection | Social close-up |
| D3 | Collar, hem, or seam construction detail | Macro, raking light from side to reveal texture | Raking, artisanal | PDP gallery |

### Founder / Story Shots (4–6 shots — when Corey is on set)

Corey Foster: earned, direct, Oakland-grounded. Every shot reads as real, not rehearsed.

| # | Description | Framing | Expression | Platform |
|---|-------------|---------|------------|---------|
| F1 | Direct eye contact, neutral or slight natural smile | Head and shoulders, clean or minimal background | Confident, founder energy | Press kit / About page |
| F2 | Corey in environment — doorway, loading dock, or Oakland street corner | Medium-wide, environmental | Purposeful, in his city | Brand Story pillar |
| F3 | Hands-on — holding product, adjusting tag, reviewing production piece | Medium, hands prominent | Working, intentional | BTS pillar |
| F4 | Candid laugh or off-guard natural moment | Medium, natural | Real, human | Community pillar |
| F5 | With Skyy Rose (daughter) — only when appropriate to the session | Wide enough to show relationship | Heritage, legacy | Brand Story / About |

**Founder AVOID:** Corey pointing at a whiteboard, arms crossed in boardroom pose, standing on private-jet stairs, posed "CEO" stock archetypes. Wrong register entirely.

### Behind-the-Scenes Shots (2–4 shots)

Authentic process content — captured during the shoot, not staged separately.

| # | Description | Framing | Usage |
|---|-------------|---------|-------|
| B1 | Behind the camera — DP or photographer working | Wide | Stories, TikTok |
| B2 | Rack of SkyyRose pieces backstage | Medium | Stories |
| B3 | Styling table — tags, accessories, brand packaging | Overhead | Stories / Pinterest |
| B4 | Corey reviewing shots on a monitor or phone on set | Medium | Brand Story / Stories |

---

## Section 7: Platform Image Requirements

Specify required crops per session. Every hero and lifestyle shot must deliver all applicable crops. Detail and macro shots: square (1:1) crop only.

| Destination | Format | Dimensions | File Size Cap | Notes |
|-------------|--------|-----------|--------------|-------|
| **WooCommerce PDP main** | Square | 2048×2048 px minimum | — | Product fills 75%+ of frame; sRGB ICC profile; consistent background across all PDP main images in a collection |
| **WooCommerce PDP gallery** | Square | 2048×2048 px | — | Gallery slots 2–5; consistent background preferred; WooCommerce generates thumbnails automatically via `woocommerce_gallery_thumbnail_size` (default 100×100) and `shop_catalog_image_size` after media upload |
| **Instagram Feed 4:5** | 4:5 portrait | 1080×1350 px | 8 MB | Primary format for product-on-body and lifestyle shots; dominant Instagram product presentation |
| **Instagram Feed square** | 1:1 | 1080×1080 px | 8 MB | Hero-front product shots; carousel slide use; grid consistency |
| **Instagram Story / Reel cover** | 9:16 | 1080×1920 px | 30 MB (video); 8 MB (image) | **Safe zone:** preserve ~250 px at top (UI chrome: profile, close) and ~350 px at bottom (CTA / swipe-up area) — keep subject and key product detail in the center 1080×1320 safe area |
| **Pinterest** | 2:3 | 1000×1500 px | 20 MB | Flat lay and editorial crops; link pins to WooCommerce product page; taller ratio gets more feed real estate |
| **Web hero banner** | 16:9 | 1920×1080 px (min 1280×720) | — | Website collection page hero and email header base crop |
| **Email header** | 3:1 | 1200×400 px | — | Crop from hero or lifestyle for Klaviyo campaigns; leave copy-safe space at center-right |

**sRGB delivery required** for all web/social destinations. Shoot in any color space; convert to sRGB ICC profile on export. Do not deliver P3 or AdobeRGB files to WooCommerce — colors will shift unpredictably in browsers that don't honor embedded profiles.

---

## Section 8: File Specs and Naming

### Delivery Specs

| Asset type | Format | Minimum resolution | Color profile | Retouching |
|-----------|--------|--------------------|---------------|-----------|
| Catalog originals | RAW (CR3/ARW/NEF) | Full camera resolution | As captured | None |
| PDP and social delivery | JPEG | 2048 px minimum on short side | sRGB ICC | Technical only — remove lint, sensor dust, fiber artifacts; preserve fabric texture; no heavy smoothing |
| Web-optimized | JPEG | 1200 px on long side | sRGB | Match hires grade |

**Per-collection color grade — no bleed between collections.** Black Rose: cool-neutral. Love Hurts: warm-dramatic. Signature: warm-golden. Kids Capsule: bright-neutral with warm bias. Grade must be consistent within a collection across the entire delivery — not shot-by-shot.

**Texture preservation is mandatory.** Do not smooth fabric weave, embroidery, or knit texture in retouching. The texture is the proof of quality.

### File Naming Convention

`{collection-slug}-{product-slug-or-shot-type}-{shot-descriptor}-{sequence}-{aspect}.jpg`

All lowercase. Hyphens only. No spaces. No underscores.

| Element | Format | Example values |
|---------|--------|---------------|
| `collection-slug` | lowercase kebab | `black-rose`, `love-hurts`, `signature`, `kids-capsule` |
| `product-slug` (product sessions) | lowercase kebab from product name | `crewneck`, `bomber`, `tee` |
| `shot-type` (brand sessions) | category keyword | `hero`, `lifestyle`, `detail`, `founder`, `bts` |
| `shot-descriptor` | brief descriptor | `front`, `angle`, `back`, `embroidery`, `flat-lay`, `walking`, `direct` |
| `sequence` | zero-padded two digits | `01`, `02`, `03` |
| `aspect` | ratio notation | `square`, `4x5`, `9x16`, `2x3`, `16x9`, `3x1` |

**Product session examples:**
- `black-rose-crewneck-hero-front-01-square.jpg`
- `black-rose-crewneck-detail-embroidery-04-square.jpg`
- `black-rose-crewneck-flat-lay-05-2x3.jpg`
- `signature-bomber-on-body-scale-06-4x5.jpg`

**Brand session examples:**
- `black-rose-hero-lockup-ready-01-4x5.jpg`
- `signature-lifestyle-walking-03-9x16.jpg`
- `founder-direct-corey-02-square.jpg`
- `love-hurts-bts-wardrobe-rack-01-square.jpg`

### Delivery Folder Structure

Organize delivery drive by: `{collection-slug} / {shot-category} / {files}`

Example:
```
black-rose/
  hero/
  lifestyle/
  detail/
  founder/
  bts/
signature/
  hero/
  lifestyle/
  detail/
```

---

## Section 9: Styling and AVOID List

### Mandatory Styling Direction per Session Type

**Product sessions — garment is the protagonist:**
- No competing props; surfaces serve the garment, not vice versa
- Per-collection background and surface (see Section 4)
- Human elements: flat lay (no talent), or hands/partial only unless full-body scale shot is required
- No external branding visible — no non-SkyyRose hangtags, labels, logos in frame

**Brand sessions — Oakland as identity:**
- Location anchors the brand DNA — Oakland-first before any other setting
- Corey in environment reads as real; studio isolation is acceptable only for hero lockup shots that will receive composited location backgrounds
- Community framing (two or more subjects) reads as brand culture, not fashion editorial

### Universal AVOID List (all sessions)

| Anti-pattern | Why it's wrong |
|-------------|---------------|
| White background for Black Rose or Love Hurts | Destroys collection visual identity; white = Kids Capsule or Signature (light variants only) |
| Type-rendered collection name in any frame | Lockup composited by Elite Studio — burning it in photo makes it permanently uncorrectable |
| European luxury-house aesthetic | Wrong brand DNA — Bottega warmth, Rick Owens void, Hedi Slimane skinny polish, Acne Scandinavian sterility are all off-register |
| Warm grading on Black Rose shots | Reads Signature; cross-collection lighting confusion destroys catalog visual identity |
| Cool grading on Signature or Love Hurts shots | Reads Black Rose |
| SKU references in the brief | Photographers don't know SKU system; product names prevent set confusion and have caused conflations historically |
| Invented product details (embroidery that doesn't exist, colorways not in catalog) | Resolve against catalog CSV + dossier only |
| Valentine's clichés on Love Hurts | Florals, soft-focus romance, hearts — wrong register; Love Hurts is street passion, not romance novel |
| Staged founder poses | Boardroom, whiteboard, jet stairs, crossed-arms CEO pose — real Corey beats posed Corey |
| European location signifiers | Parisian cobblestones, whitewashed studio with linen drapes, vineyard — Oakland is the anchor |
| More than 30 shots scheduled for a half-day session | Rushed shots are unusable; flag and recommend splitting |
| Warm golden props on Black Rose | Silver hardware only; gold reads Signature |
| Shiny or glossy outerwear on Black Rose | Matte fabrics define the collection aesthetic |
| Dramatic moody lighting on Kids Capsule | Bright, even, warm-natural is the register |
| Any brief without an explicit AVOID list | Photographers unfamiliar with SkyyRose default to their own vocabulary; the AVOID list is the correction mechanism |

**California Model Release note:** Any recognizable person appearing in commercial photography for SkyyRose (advertising, WooCommerce PDP, social campaigns) requires a written model release under California Civil Code § 3344, which prohibits commercial use of a person's likeness without prior consent. Obtain signed releases from all recognizable talent — including Corey and Skyy Rose — before any commercial publication. Confirm release forms on the pre-shoot checklist.

---

## Section 10: Elite Studio Pipeline Handoff

All delivered photography assets flow into `skyyrose/elite_studio` for:
1. WooCommerce media library upload and product image assignment
2. Social pipeline compositing (lockup overlays, crop variants, platform packaging)
3. 3D garment pipeline integration (reference images for Meshy/TRELLIS/Tripo mesh generation)
4. WooCommerce thumbnail regeneration (`regenerate-thumbnails` is triggered post-upload to rebuild `shop_catalog_image_size` and `woocommerce_gallery_thumbnail_size` from the 2048px source)

**Delivery instructions for the photographer:**
- Deliver all assets to the designated Elite Studio intake folder (confirm location at brief handoff)
- Organize by collection → shot category (see folder structure in Section 8)
- Deliver RAW originals + hires JPEG + web JPEG in the same session folder
- Do NOT burn the collection name text into any frame — the lockup asset from `assets/images/hero-overlays/` (BR/LH/SIG) or `assets/images/logos/` (Kids) is composited at the Elite Studio stage for all hero and Reel-cover frames that carry a collection name title treatment
- Include color-graded versions and raw versions; Elite Studio may re-grade for 3D pipeline reference use cases

**STOP-AND-SHOW gate:** WooCommerce media uploads, product image assignments, and live catalog updates require explicit confirmation per the STOP-AND-SHOW protocol before execution. Do not upload or assign without showing the manifest first.

---

## Section 11: Anti-Patterns

- **Never apply warm color grading to Black Rose or Love Hurts shots.** Collection identity lives in the color grade. A warm shift accidentally applied to Black Rose makes it read Signature — and that error propagates through every crop and social post derived from that image.
- **Never type-render the collection name in the photograph.** The lockup PNG from `assets/images/hero-overlays/` is the collection name. Burning text in photo makes it uncorrectable downstream; it blocks the entire lockup-compositing step at Elite Studio.
- **Never pull European luxury-house product photography aesthetics.** No Bottega-style hand-draped fabric in soft Venetian light, no Rick Owens negative-space minimalism, no Acne Studio sterile Scandinavian white. The Five only: Kith, Oaklandish, Culture Kings, Fear of God, Palm Angels.
- **Never reference the product by SKU in the brief.** The brief goes to photographers; SKU-first causes set confusion and has caused product conflations in past sessions.
- **Never invent product details.** If a selling point or feature isn't confirmed in the catalog CSV or a dossier, it doesn't appear in the brief.
- **Never skip the on-body/scale shot for apparel.** Even if this session is flat-lay-only due to no available talent, note the gap explicitly in the brief so the PDP is not launched without it. Schedule a follow-up; don't silently omit it.
- **Never submit a brief without an AVOID list.** The AVOID list is the single most effective tool for preventing a photographer unfamiliar with SkyyRose from defaulting to a Fashion Nova, Zara, or H&M product-photo aesthetic.
- **Never cross background and lighting direction between collections in a single mixed session** without a deliberate, full set change. Shoot all Black Rose shots consecutively, then change the set completely before Signature.
- **Never deliver product images with visible non-SkyyRose branding, pricing tags, or external labels.** Check every frame before delivery approval.
- **Never schedule more than 30 shots for a half-day session.** Flag and recommend splitting; rushed shots waste the session budget and photographer's time.
- **Never stage Corey in "successful founder" archetypes** — boardroom, whiteboard pointer, jet stairs, arms-crossed power pose. Real and Oakland-grounded beats every stock archetype.
- **Never use the European luxury-house location vocabulary** — Parisian cobblestones, whitewashed studio with linen drapes, vineyard or winery settings. Oakland is the anchor. There is no substitute.

---

## Section 12: Recovery

**Photographer defaults to white background for all shots:**
Catch this at brief review, not on shoot day. Include per-collection background direction prominently in the brief header — not buried in a table. Send one reference image for the exact background type before the session. A visual reference overrides a paragraph of description every time.

**Dark fabric disappears into dark background (Black Rose):**
Add edge lighting — a strobe or LED strip from directly above or slightly behind the garment to create a thin separation rim. Adjust; do not switch backgrounds. White backgrounds for Black Rose are not a solution.

**Macro detail shots look flat — no visible texture:**
Key light angle is wrong. Move it lower and more to the side. Raking light must be at 20–30 degrees maximum, not 45 or above. If shooting with natural light, reposition the product to catch a sharper angle from the window edge.

**Garment has multiple colorways and time is short:**
Shoot the hero front for all colorways first — same setup, swap the garment, do not move lights. Then add angle/back/detail shots for the primary colorway in depth. WooCommerce catalog requires a hero-front for each variant; everything else is additive.

**Brief handed to a photographer who has never shot streetwear:**
Add five reference images from The Five (one each: Kith, Oaklandish, Culture Kings, Fear of God, Palm Angels) to the physical brief packet. Visual references override written direction.

**Delivered shots have wrong color grade:**
Return to photographer with the collection color direction from Section 4 before requesting a reshoot. Most grading errors are correctable in post — full reshoot is last resort and requires a clear fault-of-brief determination.

**Shot list exceeds 30 for half-day:**
Protect hero and lifestyle shots first. Cut BTS last (it can be captured opportunistically during any part of the shoot). If a full category must be cut, cut Detail last — detail shots can be captured tabletop with the product alone in a second, shorter session.

**Hero shot needs lockup composite but collection name was burned into the photo:**
Do not attempt removal in post. Use a non-lockup lifestyle shot as the interim hero and schedule a clean reshoot of the lockup-ready frame. Add "no in-frame text" as a standing rule on all future session briefs.

**Location falls through on shoot day:**
Have one backup Oakland location pre-scouted per session. Black Rose: any concrete wall or industrial alley. Love Hurts: red-brick wall or dark urban corridor. Signature: any rooftop with Bay Area horizon or sunlit exterior. Kids Capsule: any neighborhood park. Never substitute a neutral studio without explicitly adjusting the brief's visual direction and notifying Elite Studio that the background grade will need to be applied in post.

**Delivered shots look wrong (wrong collection mood):**
Before requesting a rebrief, check color grading first — a warm-grade error is the most common cause. A Black Rose session graded warm reads Signature. Correct in post; request reshoot only if the lighting setup itself was wrong (wrong background, wrong key-light angle).

**Model release was not obtained before publication:**
Pull the image from all commercial channels immediately. Obtain a signed release under California Civil Code § 3344 before any republication. Do not attempt to publish commercially without a signed release from any recognizable individual in the frame.

---

## Artifact Specification

This skill produces a single photographer-ready brief document with this structure:

```
# SkyyRose Photography Brief — [Collection] [Session Type]

## Session Overview
(Collection, session type, purpose, date, location, talent, platforms, scope)

## Visual Direction
(Aesthetic register, palette hex values, lighting per shot type, backgrounds,
styling notes, references from The Five, AVOID list — per-collection)

## Shot List
(Tables by category: Product 7-shot catalog / Extended / Hero / Lifestyle /
Detail / Founder / BTS — with description, framing, lighting, background, destination)

## Platform Image Requirements
(WooCommerce PDP, IG 4:5 / 1:1, Story/Reel 9:16 with safe zones,
Pinterest 2:3, web hero 16:9, email 3:1 — dimensions and file size caps)

## Styling Notes
(Props, surfaces, human elements, AVOID list)

## File Specs and Naming
(RAW + hires JPEG + web JPEG, sRGB delivery, per-collection grade,
naming convention with examples, folder structure)

## Elite Studio Pipeline Notes
(Intake folder, lockup compositing note, STOP-AND-SHOW gate on WC uploads)
```

---

## Example Brief

**Request:** "Product photography brief for the Black Rose Crewneck. WooCommerce PDP + IG Feed. No model — flat lay and detail only for this session."

---

# SkyyRose Photography Brief — Black Rose Crewneck, Product Session

**Product:** Black Rose Crewneck
**Collection:** Black Rose
**Variants:** [Resolve against catalog CSV before shoot — do not invent colorways]
**Key selling points:** [Resolve from per-SKU dossier — chest embroidery/graphic, premium cotton construction, Black Rose detailing as confirmed in dossier]
**Session type:** Product — 7-shot catalog, flat lay and detail focus (no model this session)
**Platforms:** WooCommerce PDP, Instagram Feed (4:5 and 1:1), Pinterest (2:3)
**Gap note:** On-body/scale shot (Shot 6) and Lifestyle in-use (Shot 7) not captured this session. PDP must not go live without these — schedule a follow-up before launch.

---

### Platform Image Requirements

| Destination | Dimensions | Format | Notes |
|-------------|-----------|--------|-------|
| WooCommerce PDP main | 2048×2048 px minimum | JPEG, sRGB | Product centered, consistent dark background |
| WooCommerce PDP gallery | 2048×2048 px | JPEG, sRGB | Slots 2–5; match main background |
| Instagram Feed 4:5 | 1080×1350 px | JPEG, max 8 MB | Detail and flat-lay crops |
| Instagram Feed 1:1 | 1080×1080 px | JPEG, max 8 MB | Hero-front square crop |
| Pinterest 2:3 | 1000×1500 px | JPEG, max 20 MB | Flat lay, link to WC product page |

---

### Visual Direction — Black Rose

**Background (hero/flat lay):** Matte black seamless or dark concrete surface (#0A0A0A)
**Background (detail):** Neutral dark surface — garment fills the frame
**Lighting (hero/flat lay):** Dual softbox at 45 degrees each side; edge light from above to separate black crewneck from black ground; white fill card below for shadow detail without hot spots
**Lighting (detail macros):** Single raking key at 20–30 degrees from left — no fill; shadow defines embroidery, weave, or print texture. Flat overhead is not acceptable for detail shots.
**Color temperature:** Cool-neutral throughout. No warm grade.
**Styling:** The crewneck is the sole subject. Dark slate or concrete surface only. No props. No linen, no wood, no warm-toned textures.
**AVOID:** White backgrounds; warm or golden color grading; props that soften the aesthetic; overhead flash that flattens embroidery texture; stock flat-lay arrangements with scattered accessories.

---

### Shot List

| # | Shot Type | Description | Framing | Lighting | Background |
|---|-----------|-------------|---------|----------|------------|
| 1 | Hero front | Crewneck centered, chest graphic/embroidery front-facing, crew neck visible | Straight-on; product fills 75%; camera slightly above horizontal | Dual softbox 45°, edge light above, fill card below | Matte black seamless |
| 2 | Hero angle | 3/4 view from left showing sleeve seam, shoulder shape, body width | 30° angle, medium | Dual softbox, slight shadow right | Matte black seamless |
| 3 | Back view | Full reverse — rear construction, back hem, any back brand mark | Straight-on, match hero front framing exactly | Match hero front | Matte black seamless |
| 4 | Detail — primary | Chest embroidery or screen-print — thread quality, placement, line definition | Macro, tight crop (4–6 inch area) | Single raking key at 20–30° from left; no fill | Dark surface, blurred |
| 5 | Detail — fabric texture | Fabric weave or knit structure on torso | Macro, 2–3 inch area | Raking light at low angle from left | Dark surface, blurred |
| 6 | Flat lay — full garment | Crewneck laid flat; collar up slightly; sleeves extended; garment fills 70% of frame | Overhead, centered | Even overhead diffused; dual softbox with diffusion panel overhead | Dark concrete or matte black surface |
| 7 | Detail — label/tag | Interior brand label — visible and legible | Macro; fabric pulled slightly to expose label at 30° angle | Soft single key from above | Dark fabric as background |

---

### Styling Notes

**Props:** None. Black Rose product photography uses the garment as the sole subject.
**Surfaces:** Matte black seamless (hero shots 1–3, 6). Dark concrete or slate (flat lay and detail shots 4–5, 7).
**Human elements:** None for this session.
**AVOID:**
- Shiny or reflective surfaces that produce hot spots on dark matte fabric
- Warm or golden color grade — this is Black Rose, not Signature
- Props that soften the aesthetic (candles, foliage, coffee mugs, scattered accessories)
- Overhead flash that flattens embroidery texture — raking light is mandatory for shots 4 and 5
- Stock-photo flat-lay arrangements with props scattered around the garment

---

### File Naming

Pattern: `black-rose-crewneck-{shot-descriptor}-{seq}-{aspect}.jpg`

Examples:
- `black-rose-crewneck-hero-front-01-square.jpg`
- `black-rose-crewneck-hero-front-01-4x5.jpg`
- `black-rose-crewneck-detail-embroidery-04-square.jpg`
- `black-rose-crewneck-flat-lay-06-2x3.jpg`

Delivery folder: `black-rose / crewneck / hero`, `black-rose / crewneck / detail`, `black-rose / crewneck / flat-lay`

---

### Deliverables

- RAW originals + hires JPEG (minimum 2048 px short side) + web JPEG (1200 px long side)
- Color grade: cool-neutral, consistent across all Black Rose shots in this session
- Retouching: lint, sensor dust, fiber artifacts removed; fabric texture preserved — no heavy smoothing
- Crops per hero and flat-lay shot: 1:1 square, 4:5, 2:3
- Delivery via Drive folder (organized above)

### Elite Studio Pipeline Notes

Deliver all assets to `skyyrose/elite_studio` intake folder. Do **not** burn "Black Rose" collection name text into any frame — the brand-script lockup from `assets/images/hero-overlays/` is composited at the Elite Studio stage.

WooCommerce upload and product image assignment requires STOP-AND-SHOW confirmation before execution.
