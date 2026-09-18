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

- **Single source of truth:** the product registry, `wordpress-theme/skyyrose-flagship/data/logo-registry.json`. Read a product with `from skyyrose.core.product import get_product` (or `python -m skyyrose.core.product <sku>`); absent facts are named in its `gaps` list.

### Canonical Product Name Mapping (USE THESE NAMES for WordPress)

**CRITICAL:** When uploading products to WordPress, ALWAYS use these exact names from the product mapper. Do NOT rename, abbreviate, or alter them.

#### BLACK ROSE Collection (8 products)
| SKU | WordPress Product Name |
|-----|----------------------|
| br-001 | BLACK Rose Crewneck |
| br-002 | BLACK Rose Joggers |
| br-003 | BLACK is Beautiful Jersey |
| br-004 | BLACK Rose Hoodie |
| br-005 | BLACK Rose Hoodie — Signature Edition |
| br-006 | BLACK Rose Sherpa Jacket |
| br-007 | BLACK Rose × Love Hurts Basketball Shorts |
| br-008 | Women's BLACK Rose Hooded Dress |

#### LOVE HURTS Collection (5 products)
| SKU | WordPress Product Name |
|-----|----------------------|
| lh-001 | The Fannie |
| lh-002 | Love Hurts Joggers |
| lh-003 | Love Hurts Basketball Shorts |
| lh-004 | Love Hurts Varsity Jacket |
| lh-005 | Love Hurts Bomber Jacket |

#### SIGNATURE Collection (14 products)
| SKU | WordPress Product Name |
|-----|----------------------|
| sg-001 | The Bay Set |
| sg-002 | Stay Golden Set |
| sg-003 | The Signature Tee |
| sg-004 | The Signature Tee — White |
| sg-005 | Stay Golden Tee |
| sg-006 | Mint & Lavender Hoodie |
| sg-007 | The Signature Beanie |
| sg-008 | The Signature Beanie |
| sg-009 | The Sherpa Jacket |
| sg-010 | The Bridge Series Shorts |
| sg-011 | The Signature Beanie — Grey |
| sg-012 | The Signature Beanie — Orange |
| sg-013 | Mint & Lavender Crewneck Set |
| sg-014 | Pastel Chevron Tracksuit Set |

#### KIDS CAPSULE Collection (2 products)
| SKU | WordPress Product Name |
|-----|----------------------|
| kids-001 | Kids Colorblock Hoodie Set — Purple/Pink |
| kids-002 | Kids Colorblock Hoodie Set — Black/Red/White |

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
