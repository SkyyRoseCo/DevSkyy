# AI Photo Generation Pipeline — SkyyRose Elite Production Studio

> Generate fashion model images wearing EXACT product assets, then embed into WordPress theme

## Pipeline Overview

```
SOURCE PHOTOS → VISION ANALYSIS → PROMPT RESOLUTION → IMAGE GENERATION → QUALITY CHECK → OPTIMIZE → EMBED IN THEME
```

Every generated image must show a model wearing the **exact real product** — correct garment type, correct branding technique, correct logo placement, correct colors. The vision system analyzes actual product photos to enforce this.

## Source Assets

- **Location:** `skyyrose/assets/images/source-products/{collection}/`
- **Naming:** `{id}-{product}-{view}.{ext}` (e.g., `br-001-crewneck-front.png`)
- **Collections:** `black-rose/`, `love-hurts/`, `signature/`, `kids-capsule/`
- **Total:** 100+ reference photos across 28 products

## Product Catalog

**Single source of truth:** `wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv`

Read the CSV for SKU, name, price, collection, branding_spec, and image paths. Previous versions of this doc kept a hardcoded SKU table that drifted out of sync with the CSV (e.g., kids-001 was listed here as "Purple/Pink" when the CSV said "Red/Black" — caused a wasted paid render run on 2026-04-19).

### How to read it for image generation

```python
from skyyrose.core.catalog_loader import read_catalog_rows
rows = read_catalog_rows()
for r in rows:
    sku          = r["sku"]
    name         = r["name"]                # canonical WordPress product name
    collection   = r["collection"]
    branding     = r["branding_spec"]        # logo technique + placement specs
    src_override = r.get("render_source_override") or ""  # for front
    back_src     = r.get("render_back_source_override") or ""
```

Or from nano_banana/elite_studio: `from nano_banana.catalog import load_catalog` / `from skyyrose.elite_studio.catalog import Catalog`.

### Never hardcode SKU lists

Do NOT rename, abbreviate, or duplicate product names in prompts, overrides, or doc tables. The CSV is the only canonical source.

## Product Override System (Accuracy Enforcement)

- **Location:** `skyyrose/assets/data/prompts/overrides/{sku}.json`
- **28 override files** — one per product, ML-verified

### Critical Override Fields
```
garmentTypeLock    — "CREWNECK SWEATSHIRT — NOT jersey/hoodie/jacket"
brandingTech       — logo technique (embroidered/silicone/printed/sublimation/embossed)
logoFingerprint    — ML-verified: location, size, technique, color per logo element
modelPose          — How the model should stand/pose
setting            — Scene description matching collection mood
```

### Branding Technique Distribution (ML-Verified)
- **Embroidered** (11): Thread-stitched, raised texture
- **Silicone** (5): 3D cut-out appliqué, slight gloss
- **Printed** (4): Screen print, dye-printed graphics
- **Embroidered patch** (3): Separate woven/embroidered patch applied
- **Woven label patch** (2): Integrated label tag
- **Sublimation** (1): Dye-printed into fabric
- **Laser-engraved leather** (1): Recessed into leather material
- **Embossed** (1): Tonal relief into fabric surface

**CRITICAL:** The `logoFingerprint` from ML Flash vision is the source of truth. Do NOT guess techniques from marketing copy.

## Prompt Engine (Accuracy-First Resolution)

- **File:** `skyyrose/build/prompt-engine.js`
- **Resolution order:** Accuracy blocks injected FIRST
  1. Load template (fashion-model.json / skyy-pose.json / scene.json / ad-creative.json)
  2. Load collection DNA (from prompt-config.json)
  3. Load product override ({sku}.json)
  4. Inject BRANDING BLOCK (brandingTech → technique enforcement)
  5. Inject FINGERPRINT BLOCK (logoFingerprint → exact logo specs)
  6. Inject GARMENT LOCK BLOCK (garmentTypeLock → prevent garment confusion)
  7. Inject FLASH ANALYSIS BLOCK (vision Stage 1 specs)
  8. Apply collection DNA substitutions
  9. Return final prompt

## Generation Entry Points

### Fashion Model Images (Primary — for product pages)
```bash
node skyyrose/build/generate-fashion-models.js              # All 28 products
node skyyrose/build/generate-fashion-models.js br-001       # Single product
node skyyrose/build/generate-fashion-models.js br-001 br-002 lh-001  # Multiple
```
- **Provider:** Gemini 2.5 Flash Image (primary), DALL-E 3 (fallback)
- **Output:** `skyyrose/assets/images/products/{sku}/{sku}-model-{view}.jpg`
- **Views:** front, back (2 per product = 56 total)

### Skyy Character Poses (retired)
`skyyrose/build/generate-skyy-poses.js` was deleted 2026-09-18: it carried its own
hard-coded 21-SKU product list instead of reading the product registry. New
renders are gpt-image-2 via `scripts/oai_render` (paid — founder approval per call).

### Scene Backgrounds (For immersive 3D experiences)
```bash
node skyyrose/build/generate-scenes-gemini.js               # All collection scenes
```
- **Provider:** Gemini 2.5 Flash Image
- **Output:** `skyyrose/assets/images/scenes/ai-generated/{collection}-{room}.webp`
- **Scenes:** 7 immersive room backgrounds

### Ad Creative Images (For social media)
```bash
node skyyrose/build/prompt-studio.js generate-ad {sku} {platform}
```
- **Platforms:** instagram, tiktok, launch-banner
- **Output:** Collection-scoped with platform-specific voice

### Full Orchestrator (Python — multi-provider with quality verification)
```bash
cd skyyrose
python skyyrose_elite_studio.py produce br-001              # Single product
python skyyrose_elite_studio.py produce br-001 --view back  # Back view
python skyyrose_elite_studio.py batch --collection black-rose  # Collection
python skyyrose_elite_studio.py batch --all                 # All 28 products
python skyyrose_elite_studio.py audit br-001                # Vision-only analysis
python skyyrose_elite_studio.py status                      # Inventory check
```
- **Pipeline:** VisionPipeline → GenerationPipeline → QualityPipeline
- **Auto-regeneration:** Up to 3 attempts on quality failure
- **Rate limiting:** 8s delay between products to avoid 429s

## Image Optimization

```bash
node skyyrose/build/optimize-images.js                      # Sharp WebP + JPEG
```
- Outputs: WebP primary, JPEG fallback
- Sizes: 480px, 768px, 1024px, 2048px (responsive srcset)
- Quality: 85% JPEG, 80% WebP

## Output Inventory (Current Status)

| Asset Type | Count | Status |
|------------|-------|--------|
| Fashion model photos | ~204 files across 28 SKU folders | Generated |
| Scene backgrounds | 7 immersive rooms | Generated |
| Product overrides | 28 files (all products) | Complete, ML-fingerprinted |
| Garment analyses | 20+ detailed specs | Generated |
| Skyy poses | 0 of 84 | **NOT YET GENERATED** |
| Ad creatives | 0 | **NOT YET GENERATED** |

## Collection DNA (Mood & Styling)

| Collection | Accent | Setting | Mood |
|------------|--------|---------|------|
| BLACK ROSE | #B76E79 rose gold | Gothic gardens, cathedrals, moonlit terraces | Mysterious editorial, gothic luxury |
| LOVE HURTS | #8B0000 crimson | Baroque theaters, candlelit chambers, castle ruins | Bold passionate, street-heat |
| SIGNATURE | #D4AF37 gold | Minimalist runways, penthouses, marble galleries | High fashion prestige, Bay Area pride |
| KIDS CAPSULE | #FF6B9D pink | Bright studio, playground luxury | Joyful luxury, aspirational |

## Quality Verification (Auto in Elite Studio)

- **Dual verifier:** Claude Sonnet + Gemini Flash
- **Checks:** logo_accuracy, garment_accuracy, photo_quality
- **Decision:** PASS → save, WARN → flag for review, FAIL → regenerate
- **Logo accuracy = #1 priority** — must match exact brandingTech from fingerprint

## WordPress Theme Integration

### Where Generated Images Go in Theme
| Image Type | Theme Location | Used In |
|------------|---------------|---------|
| Fashion model (front) | Collection landing page hero + lookbook grid | `template-collection-*.php` |
| Fashion model (back) | Lookbook grid secondary images | `template-collection-*.php` |
| Fashion model (both) | Product detail modals, hover gallery | Product cards |
| Scene backgrounds | Immersive 3D experience backdrop | `template-immersive-*.php` |
| Collection logos | Hero sections, header, footer | `header.php`, all templates |
| Ad creatives | Marketing banners, homepage hero | `front-page.php` |

### Image Embedding Pattern (WordPress)
```php
<!-- Responsive AI model image with WebP + JPEG fallback -->
<picture>
    <source srcset="<?php echo get_template_directory_uri(); ?>/assets/images/products/br-001/br-001-model-front.webp" type="image/webp">
    <img
        src="<?php echo get_template_directory_uri(); ?>/assets/images/products/br-001/br-001-model-front.jpg"
        alt="<?php echo esc_attr($product_name); ?> - Model wearing Black Rose Crewneck"
        width="1024" height="1536"
        loading="lazy"
        class="lookbook-image"
    >
</picture>
```

### Lookbook Grid Pattern (3 images per collection)
```
┌──────────────┬──────────────┐
│              │   Model 2    │
│   Model 1    ├──────────────┤
│   (large)    │   Model 3    │
│              │              │
└──────────────┴──────────────┘
```

## CRITICAL RULES

1. **EXACT PRODUCTS ONLY** — Generated models must wear the real SkyyRose garments, not generic clothing
2. **FINGERPRINT IS TRUTH** — Use logoFingerprint from overrides, not marketing descriptions
3. **GARMENT LOCK** — If override says "CREWNECK" do NOT generate a hoodie or jacket
4. **BRANDING TECHNIQUE** — If fingerprint says "silicone" do NOT render as embroidered
5. **COLLECTION MOOD** — Black Rose is gothic, Love Hurts is dramatic, Signature is elevated, Kids is joyful
6. **RATE LIMITS** — 8s delay between products, exponential backoff on 429s
7. **QUALITY GATE** — Every image passes dual-provider quality check before use in theme
8. **RESPONSIVE** — All images must be optimized to WebP + JPEG in 4 responsive sizes
9. **ALT TEXT** — Every image gets descriptive alt text (product name + model description)
10. **NO AI ARTIFACTS** — If quality check detects distorted hands, extra fingers, or garbled text → regenerate
