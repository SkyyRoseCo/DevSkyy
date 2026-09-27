# Ecommerce Photography — Knowledge Base

Source of truth for `ECOMMERCE_PHOTOGRAPHY_SPEC`. The Python class `skyyrose.elite_studio.fashion.photography.PhotographyDirector` holds the canonical style definitions; this doc layers in platform-specific image specs, fabric behavior rules, and commercial composition standards that the Director class does not encode.

> "" Every shot must earn that tagline — the product is hero, the lighting is honest, the retouch is invisible.

---

## 1. Platform image specifications (non-negotiable)

| Platform | Min dimensions | Aspect | Background | Color | Format | Notes |
|---|---|---|---|---|---|---|
| **Amazon** (apparel) | 2000×2000 | 1:1 | Pure white `#FFFFFF` | sRGB | JPEG | ≥85% frame fill, no props, no mannequin visible, no watermark. Invisible-ghost or on-model both allowed. |
| **Shopify** (OS 2.0) | 2048×2048 | 1:1 primary; 4:5 mobile | White or transparent PNG for flat-lay | sRGB | JPEG/WebP | ≤20MB per image, first image sets product card crop. |
| **Vogue / editorial** | 3000×4000 | 4:5 vertical, 3:2 landscape | Environment-specific | ProPhoto RGB acceptable for print | TIFF (print) / JPEG (web) | 300dpi for print; grain and texture preserved. |
| **Meta (IG/FB feed)** | 1080×1350 | 4:5 | Any | sRGB | JPEG | CTA-safe zone: outer 250px margin. |
| **TikTok / Reels hero** | 1080×1920 | 9:16 | Any | sRGB | JPEG/WebP | Safe zone mid-70% for captions. |
| **WordPress product card** | 1200×1500 | 4:5 | Match brand | sRGB | WebP primary, JPEG fallback | Matches `skyyrose-flagship/assets/images/products/` convention `{sku}-{view}-render.webp`. |

All images ship sRGB unless the downstream workflow is explicitly print-bound. Never upload Adobe RGB to a web surface — the hue shift is visible.

---

## 2. The 5 canonical photography styles

Defined by `PhotographyDirector` in `skyyrose/elite_studio/fashion/photography.py`. Always reference this class for lighting, background, camera, post-processing, and fabric notes — do not duplicate its contents in prompts.

| Style | Use case | Collection fit | Director style key |
|---|---|---|---|
| `ecommerce` | Product card, Amazon, Shopify main image | All | `"ecommerce"` |
| `editorial` | Campaign hero, lookbook cover, magazine | Black Rose, Love Hurts | `"editorial"` |
| `lookbook` | Lookbook spreads, landing-page heroes | Signature | `"lookbook"` |
| `lifestyle` | Social ads, TikTok, UGC-feel | Kids Capsule, all | `"lifestyle"` |
| `flat-lay` | Accessories, detail shots, brand tissue | All | `"flat-lay"` |

The Director's `recommend_style(garment_type, collection)` method handles style selection — use it over heuristics.

---

## 3. Commercial composition rules

### Front product shot (primary)
- Straight-on, eye-level to garment center
- Garment fills ~80% of frame vertically
- 5–10% negative space top and bottom
- No tilt, no Dutch angle, no foreshortening
- Symmetrical unless asymmetry is a design feature (draping, deconstructed hems)

### Back shot
- Same framing as front
- Branding (logos, embroidery, team numbers) must be legible and centered
- "Black Is Beautiful" jersey back: alternating rose/plain fill must be correct per SKU (see memory — BR front left=rose, right=plain; back reversed)

### Flat-lay
- 90° overhead, perfectly parallel
- Fabric arranged to show face (not reverse) unless reverse is the feature
- Sleeves, hood, hem arranged with intention — never bunched
- Accessories (beanie, fanny pack) stylized against collection-appropriate surface

### Lifestyle / on-model
- Rule of thirds with face or brand detail at intersection
- Natural posture — no "catalog pose" stiffness
- Environment must reflect collection lens: BR = Oakland/night, LH = moody interiors, SG = SF/golden hour, KC = joyful real-world

### Zoom crops (required per SKU)
- Fabric texture at 1:1
- Stitch/hem detail
- Neck tag / inside label (for trust signal)
- Any embellishment (patches, embroidery, foil prints)

---

## 4. Fabric-specific rules (critical — overrides generic prompts)

Use `PhotographyDirector.get_fabric_lighting_notes(fabric)` to pull canonical notes. Cross-reference this table when prompting:

| Fabric | Lighting cue | Common failure | Fix |
|---|---|---|---|
| **Satin / silk** | 45° key creates specular band; matte reverse dulls | Over-reduced highlights → reads plastic | Preserve highlight, blur slightly, keep edge detail |
| **Sherpa / fleece** | Overhead soft fills nap texture | Flat rendering → reads cheap | Side-light secondary to lift pile |
| **Mesh** | Backlight for halo; underlight kills pattern | Solid render instead of translucent | Force transparency with layer blending |
| **Leather** | Single directional key; grain catches light | Blown-out specular → plastic look | Polarizer filter in prompt; bring highlights down |
| **French terry / jersey** | Even soft lighting; movement shows drape | Over-smoothing → kills loop texture | Preserve grain; 1:1 crop must show wales |
| **Lace / openwork** | Strong backlight reveals pattern | Flat render → solid panel | Backlight + contrast boost; translucent layer |
| **Denim** | Hard light shows weave; soft light shows wash | Either extreme kills one dimension | Two-zone light: hard across, soft fill |
| **Metallic foil / print** | Angled light creates sparkle path | Dull render → reads matte | Specific angle prompt; preserve speckle |

---

## 5. Color-grade brand tokens (per collection)

Apply as a final post-processing pass. Pull RGB/hex from `theme.json` — never invent colors.

| Collection | Primary accent | Shadow tone | Highlight tone | Grade target |
|---|---|---|---|---|
| **Black Rose** | Silver `#C0C0C0` | Deep cool neutral (+5 cyan, −3 mag) | Pure silver spec | Desaturated, film-grain, deep shadows |
| **Love Hurts** | Crimson `#DC143C` | Warm crimson wash | Gold highlight spill | Warm crimson tones, high contrast |
| **Signature** | Rose Gold `#B76E79` + Gold `#D4AF37` | Warm neutral | Soft gold glow | Golden warm grade, soft highlight lift |
| **Kids Capsule** | Pink `#FFB6C1` + Lavender `#E6E6FA` | Airy neutral | Bright clean | Light, saturated, joyful, Instagram-clean |

---

## 6. QA rubric — product identity, legibility, placement

Every render passes or fails on three gates. Score 0–100 per gate; `min(all three) ≥ 80` is the pass bar. This rubric is what `quality_agent.py` enforces in the Elite Studio pipeline.

### Gate 1 — Product identity
- Garment type matches CSV `name` (hockey jersey ≠ baseball jersey)
- Color matches CSV `color` within ΔE < 3
- Silhouette matches reference image
- Collection-appropriate styling

### Gate 2 — Legibility
- All text spelled correctly (brand names, team numbers, taglines)
- Logos present and oriented correctly
- No compression artifacts on key details
- No AI-typical glitches (extra fingers, warped eyes, melted zippers)

### Gate 3 — Placement
- Branding placed per `branding_spec` CSV column
- Patches, embroidery, foil prints on correct panels
- Labels / tags visible where required
- Background matches style rubric

**Automatic reject:** any product-identity miss. No retry budget consumed — the issue is upstream (reference image or prompt), not in generation.

---

## 7. Handoff contract (from `ECOMMERCE_PHOTOGRAPHY_SPEC`)

When this agent hands off to `IMAGERY_SPEC` (the pipeline orchestrator), it passes a structured brief:

```json
{
  "sku": "br-011",
  "style": "ecommerce",
  "views": ["front", "back", "detail-fabric", "detail-branding"],
  "aspect_ratios": ["1:1", "4:5"],
  "platforms": ["amazon", "shopify", "wordpress"],
  "color_grade_target": "black-rose",
  "fabric_rules": ["satin:preserve-highlight", "mesh:translucent"],
  "qa_threshold": 80,
  "max_cost_usd": 0.50
}
```

The Imagery orchestrator takes this brief and routes it through the Elite Studio pipeline (vision → prompt enrichment → generator → compositor → color correction → upscaling → QA).

---

## 8. Anti-patterns (do not do)

- Upload Adobe RGB to web — always convert to sRGB first
- Use JPEG for any image with transparency requirements
- Over-sharpen — it kills fabric texture
- Over-smooth faces/skin — reads AI-typical
- Liquify body proportions — SkyyRose models are real people, not Ozempic cartoons
- Invent background props ("subtle fabric draped nearby") unless the style calls for it
- Let AI add watermarks, timestamps, or camera UI overlays
- Ship a render with `qa_score < 80` on any of the three gates
- Mix aspect ratios within a single SKU's image set (platform-appropriate sets, yes; inconsistent within a set, no)

---

## 9. Files this agent reads / writes

**Reads (never writes):**
- `wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv` — canonical catalog
- `skyyrose/elite_studio/fashion/photography.py` — style definitions
- `wordpress-theme/skyyrose-flagship/assets/images/products/*.png|*.jpg|*.jpeg` — reference photos

**Writes (via Imagery pipeline handoff):**
- `wordpress-theme/skyyrose-flagship/assets/images/products/{sku}-{view}-render.webp`
- `logs/imagery/preflight-<ts>.md` — preflight report per batch
- `logs/imagery/qa-<ts>.json` — QA gate results per SKU

**Never touches:** any generated renders directly — all writes go through the pipeline's `save_render` node for atomic promotion.
