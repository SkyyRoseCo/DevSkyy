# Nano Banana 2 — SkyyRose AI Image Pipeline

**Last updated:** 2026-04-05

Product imagery generation using the official Google `google-genai` SDK. Clean modular rebuild with correct Gemini model IDs, multi-engine provider routing, and vision-based QA.

---

## What It Does

Generates three types of product images for every SKU in the catalog:

| View | Output filename pattern | Purpose |
|------|------------------------|---------|
| `front` | `{slug}-front-model.webp` | Ghost-mannequin front view for product cards |
| `back` | `{slug}-back-model.webp` | Ghost-mannequin back view |
| `branding` | `{slug}-branding.webp` | Lifestyle editorial shot with model wearing the piece |

Source images (tech flats, real product photos) are read from the catalog and sent as references so the AI preserves exact colors, text, logos, and design details.

---

## Models (Nano Banana family)

| Model ID | Name | Use case |
|----------|------|----------|
| `gemini-2.5-flash-image` | Nano Banana (fast) | Default — high-volume, low-latency generation |
| `gemini-3-pro-image-preview` | Nano Banana Pro | `--pro` flag — better text rendering, complex instructions, higher fidelity |
| `gemini-2.5-flash` | Flash text model | Vision QA (compares generated vs source, returns JSON verdict) |

All generated images include a **SynthID watermark** per Google's responsible AI policy.

---

## Architecture

```
scripts/
├── nano-banana-run.py              # Entry point — calls cli.main()
└── nano_banana/                    # Package
    ├── __init__.py
    ├── client.py                   # API client factories (Google, OpenAI, Together)
    ├── catalog.py                  # CSV loader, source image resolution
    ├── generate.py                 # Gemini, FLUX, GPT-Image generation functions
    ├── composite.py                # Logo compositing (real branding → AI shots)
    ├── qa.py                       # Vision QA with structured JSON output
    ├── prompts.py                  # All prompt templates + LOGO_TREATMENTS (single source of truth)
    ├── utils.py                    # Image preprocessing, quality gate, WebP conversion
    └── cli.py                      # Argparse CLI with subcommands
```

Each file is under 300 lines. No circular imports. Clean separation.

---

## Setup

```bash
# 1. Create isolated venv (keeps imagery deps out of main project venv)
python3 -m venv .venv-imagery
source .venv-imagery/bin/activate

# 2. Install dependencies
pip install -r requirements-imagery.txt

# 3. Configure API keys
cat > .env.hf <<EOF
GOOGLE_API_KEY=your-gemini-key-here
OPENAI_API_KEY=your-openai-key-here    # optional, for GPT-Image + vision QA
TOGETHER_API_KEY=your-together-key     # optional, for FLUX.2
FAL_KEY=your-fal-key                   # optional
EOF
```

Get a Google API key at https://aistudio.google.com/apikey — **enable billing** for image generation (free tier has zero quota for `gemini-2.5-flash-image`).

---

## CLI Reference

### `dry-run` — preview what would be generated

```bash
python scripts/nano-banana-run.py dry-run
python scripts/nano-banana-run.py dry-run --sku br-001 --step front
```

Shows the product list, which have source images, which are missing.

### `generate` — produce images

```bash
# Single product, all 3 views, fast model
python scripts/nano-banana-run.py generate --sku br-001

# All products, front view only, with Nano Banana Pro
python scripts/nano-banana-run.py generate --step front --pro

# Everything, all views, with vision QA retries
python scripts/nano-banana-run.py generate --step all --pro --qa

# Force FLUX engine for tech-flat SKUs
python scripts/nano-banana-run.py generate --engine auto
```

**Flags:**
- `--sku <id>` — single SKU (e.g. `br-001`)
- `--step {front,back,branding,all,front_back}` — which views to generate
- `--engine {gemini,flux,gpt-image,auto}` — provider (default: `gemini`)
- `--pro` — use `gemini-3-pro-image-preview` instead of fast model
- `--model <id>` — override model ID manually
- `--qa` — run vision QA after generation, retry on failures
- `--free` — use free FLUX tier (lower quality)

### `composite` — fix logos on existing AI renders

```bash
python scripts/nano-banana-run.py composite --sku br-001
python scripts/nano-banana-run.py composite --step composite_all --pro
```

Takes an existing AI render + the real product photo, asks Gemini to fix the logo/branding to match the real product while keeping the composition.

---

## Provider Routing

| Engine | Model | When to use |
|--------|-------|-------------|
| `gemini` (default) | `gemini-2.5-flash-image` | Reference-based generation, best overall |
| `gemini --pro` | `gemini-3-pro-image-preview` | When text rendering matters (jerseys, logos with words) |
| `flux` | `FLUX.2-pro` via Together | Tech flats → photorealistic conversion (no reference image needed) |
| `gpt-image` | `gpt-image-1.5` | Alternative with strong text rendering |
| `auto` | Routes FLUX for tech-flat SKUs, Gemini for everything else | Mixed catalog |

---

## Quality Gate

Generated images must pass minimum file size thresholds:
- **15 KB** — for `gemini-2.5-flash-image` output
- **50 KB+** typical for `gemini-3-pro-image-preview` output

Below threshold = reject, retry up to 3 times. See `nano_banana/utils.py:MIN_FILE_SIZE_KB`.

---

## Troubleshooting

### 429 RESOURCE_EXHAUSTED
**Cause:** Free tier quota exhausted for `gemini-2.5-flash-image`.
**Fix:** Enable billing on Google AI Studio (https://aistudio.google.com/apikey). Image gen is ~$0.04 per image.

### 403 PERMISSION_DENIED — "Generative Language API has not been used"
**Cause:** API key belongs to a GCP project where the API isn't enabled.
**Fix:** Visit the URL in the error message and click "Enable".

### Generated image is wrong garment type
**Cause:** Model hallucinating (e.g. rendering a crewneck as a jacket).
**Fix:** Use `--pro` flag for higher fidelity. Pass `--qa` to auto-retry on failures.

### "No source image" for many SKUs
**Cause:** Source files missing from `wordpress-theme/skyyrose-flagship/assets/images/products/`.
**Fix:** Add the techflats referenced in `data/product-catalog.csv` `render_source_override` column.

---

## Source of Truth

| Data | File |
|------|------|
| Product catalog (SKUs, names, prices, source images) | `data/product-catalog.csv` |
| Logo treatments (per-SKU branding descriptions) | `scripts/nano_banana/prompts.py` (`LOGO_TREATMENTS` dict) |
| Prompt templates (front/back/branding/composite) | `scripts/nano_banana/prompts.py` |
| Brand prompts per collection | `scripts/nano_banana/prompts.py` (`BRANDING_TEMPLATES`) |
| Model IDs | `scripts/nano_banana/generate.py` (`GEMINI_FAST`, `GEMINI_PRO`) |

---

## Related Files

- `requirements-imagery.txt` — Python deps for `.venv-imagery`
- `.env.hf` — API keys (gitignored)
- Output directory: `wordpress-theme/skyyrose-flagship/assets/images/products/`
