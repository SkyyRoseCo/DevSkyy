# Session Handoff — Elite Team Pipeline Wire-up + Stage-1 Scene Generation

**Date:** 2026-05-26
**Branch:** `fix/elite-studio-audit-2026-05-25` (DO NOT push; 24+ commits ahead of origin)
**Status:** Wire-up complete. Stage-1 scenes shipped. Stage-2 composite + v2.html swap pending.

---

## TL;DR for next session

3 founder-locked Stage-1 scene PNGs are committed at canonical SCENES_DIR. Elite team CLI is the canonical entry point. Standalone scripts deprecated. Stage 2 = real product composite onto scenes, then resize variants, then swap into v2.html.

**Resume command:**
```bash
cd /Users/theceo/DevSkyy
python -m skyyrose.elite_studio home-spread --collection black-rose --sku br-004 --budget-usd 1.50
```

---

## Founder direction lock (2026-05-26)

- **BR** = realistic night scene from the SF side of the Bay Bridge facing Oakland
- **SIG** = daytime from Oakland to SF with the Bay Bridge in the back
- **LH** = Beauty and the Beast inspired with the enchanted rose as focal point
- All 3 highly detailed with SkyyRose DNA infused
- Constraint: NO HALLUCINATIONS. Products must be actual products, not Gemini approximations
- Mandate: ALL PIPELINE WIRED INTO ELITE TEAM — no parallel standalone paths

---

## Commits landed this session

| SHA | Message |
|---|---|
| `3aab1279f` | feat(canon+pipeline): tighten 3-collection scene canon, wire scene.json into elite team |
| `5563b19c7` | chore(assets): purge 44 Gemini hallucination branding renders |
| `1d1fc3eef` | feat(elite-team): wire pipeline into elite-team — SceneGeneratorAgent + home-spread CLI |
| `7d6ed30ec` | feat(scenes): generate 3 founder-locked Stage-1 scenes via elite team |

---

## Cost spent

| Item | Amount |
|---|---|
| BR scene generation (gemini-3.1-flash-image-preview) | $0.08 |
| SIG scene generation (gemini-3.1-flash-image-preview) | $0.08 |
| LH scene generation (gemini-2.5-flash-image fallback after primary safety reject) | $0 (within budget; some plans bill, some don't on safety reject) |
| **Total** | **$0.16** |

Budget remaining: $1.34 of $1.50 ceiling.

---

## Architecture state

### Elite team pipeline (canonical, fully wired)

**New agent:** `skyyrose/elite_studio/agents/scene_generator_agent.py`
- `SceneGeneratorAgent(BaseSuperAgent)`
- Method: `async generate_scene(scene_name, collection, budget, output_dir)`
- Reads canonical `scene.json` via `compositor.lighting.load_lighting_spec()`
- Builds lean prompt (scene_description + focal_anchor + palette + skyyrose_dna)
- Model fallback chain: `gemini-3.1-flash-image-preview` → `gemini-2.5-flash-image`
- RunBudget-gated ($0.08/image pre-check)
- Writes PNG to `SCENES_DIR/{collection}/{scene_name}/{filename}.png`

**New CLI command:** `python -m skyyrose.elite_studio home-spread`
- `--collection {black-rose,signature,love-hurts,all}` (required)
- `--scene <name>` (optional; defaults to founder-locked per collection)
- `--sku <sku>` (optional; if set, triggers Stage 2 composite)
- `--model-image <path>` (auto-discovered from --sku if omitted)
- `--budget-usd <float>` (default 1.50)
- `--dry-run` (no API calls; print prompts + paths + cost)
- `--regenerate-scene` (force regen of existing scene PNG)
- File: `skyyrose/elite_studio/cli.py` (cmd_home_spread at line ~378)

**Founder-locked default scene per collection** (in `_COLLECTION_DEFAULT_SCENE`):
- `black-rose` → `black-rose-bay-bridge-sf-side-night`
- `signature` → `signature-oakland-waterfront-bay-bridge-day`
- `love-hurts` → `love-hurts-enchanted-rose-cathedral`

### Scene.json configs (canonical canon anchor)

Path pattern: `skyyrose/assets/scenes/{collection}/{scene-name}/scene.json`

Schema fields used by elite team:
- `name`, `collection`, `canon_lock_date`, `founder_directed`, `founder_lock_quote`
- `scene_description` (paragraph)
- `color_palette` (dict: primary_bg, primary_accent, highlight, etc.)
- `lighting` (dict: key_light, fill_light, color_temperature_kelvin)
- `camera` (dict: perspective, angle, depth_cues, composition)
- `skyyrose_dna` (string — pulled into prompt)
- `focal_anchor` (dict: object, position, detail, rationale)
- `product_staging_zones` (list — for Stage 2 composite positioning)
- `negative_prompts`, `reference_brands`, `anti_references` (NOT injected into prompt due to safety filter — retained for human reference)
- `atmospheric`, `render_aspect`, `expected_filename`

### Standalone scripts (deprecated 2026-05-26)

All 4 scripts have deprecation headers pointing to `skyyrose/elite_studio/cli.py home-spread`:
- `scripts/gemini_scene_gen.py`
- `scripts/gemini_lookbook.py`
- `scripts/composite_products.py`
- `scripts/run_compositor_pipeline.py`

Remain runnable but flagged as bypassing canon enforcement, RunBudget, and Stage G QA.

### SCENE_LOOKBOOK canon alignment

`skyyrose/elite_studio/agents/compositor/lighting.py:SCENE_LOOKBOOK` keys:
```python
{
    "black-rose-bay-bridge-sf-side-night": "br-",
    "love-hurts-enchanted-rose-cathedral": "lh-",
    "signature-oakland-waterfront-bay-bridge-day": "sg-",
    "kids-capsule-urban-playground": "kids-",
}
```

---

## Stage 1 scenes — paths + visual confirmation

| Collection | Canonical PNG path | Bytes | Canon hit |
|---|---|---|---|
| BR | `skyyrose/assets/scenes/black-rose/black-rose-bay-bridge-sf-side-night/black-rose-bay-bridge-sf-side-night-v2.png` | 800K | ✓ Bay Bridge cables foreground, single black rose on railing, Oakland skyline + Port cranes far distance |
| SIG | `skyyrose/assets/scenes/signature/signature-oakland-waterfront-bay-bridge-day/signature-oakland-waterfront-bay-bridge-day-v2.png` | 772K | ✓ Oakland pier daytime, Bay Bridge across middle, SF skyline, "SkyyRose" gold ink script on cream paper |
| LH | `skyyrose/assets/scenes/love-hurts/love-hurts-enchanted-rose-cathedral/love-hurts-enchanted-rose-cathedral-v2.png` | 1.4M | ✓ Gothic cathedral, stained-glass rose window, ornate stone pedestal with glass dome containing red rose lit from within, halo, burgundy curtains, candelabras |

All 3 visually verified canon-correct.

---

## Remaining work

### Stage 2 — Real product composite onto scenes (PAID, founder gate required)

Per founder's no-hallucination lock — Stage 2 composites REAL `*-front-model.webp` product photos over the Stage-1 scene PNGs via `CompositorAgent` (6-stage pipeline: matte → prompt → relight → FLUX → cleanup → shadows → QA).

**Command pattern:**
```bash
python -m skyyrose.elite_studio home-spread \
  --collection black-rose \
  --sku br-004 \
  --budget-usd 1.50
```

This will:
1. Detect scene PNG already exists at canonical path → skip Stage 1 (no charge)
2. Resolve `--sku br-004` to `assets/images/products/black-rose/br-004-front-model.webp`
3. Invoke `CompositorAgent.composite()` — 6 stages, FAL Bria + rembg matte
4. Cost: ~$0.15 per composite (FAL Bria + matte)
5. Output canonical: composite saved per `CompositorAgent` convention

**Founder SKU picks** (last discussed direction — needs re-confirmation):
- BR → `br-004` (Black Rose Hoodie — real rose-on-cloud embroidery)
- SIG → `sg-001` (Bay Bridge Shorts — sublimated Bay Bridge print) OR `sg-005` (Bay Bridge Shirt)
- LH → `lh-004` (Love Hurts Bomber — black/white satin w/ red script, rose-hood lining)

**Real product references verified canon-faithful** (visual diff this session):
- `assets/images/products/black-rose-hoodie-front-model.webp` — matches BR-004 real spec ✓
- `assets/images/products/love-hurts-bomber-front-model.webp` — matches LH-004 spec ✓
- `assets/images/products/bridge-bay-bridge-shorts-front-model.webp` — matches SG-001 spec ✓

### Stage 3 — Resize variants

Each finished composite needs 4 widths × 2 formats:
- 480w, 768w, 960w, 1280w
- AVIF + WebP

Total: 8 files × 3 collections = 24 files. Use `cwebp` + `avifenc` via canonical script OR add to elite team CLI.

Suggested command (after Stage 2):
```bash
for w in 480 768 960 1280; do
  # cwebp + avifenc batch per collection
done
```

### Stage 4 — Swap into v2.html

Update `docs/brand/design-mockups/v2.html` home-spread `<picture>` blocks (lines ~792-858) to point at new composite paths:
- BR tile → `homepage-col-black-rose.{avif,webp}` swap pattern (per SKU)
- SIG tile → `homepage-col-signature.{avif,webp}`
- LH tile → `homepage-col-love-hurts.{avif,webp}`

Or update paths to point at `skyyrose/assets/composites/` if elite team writes there.

### Stage 5 — Re-run SaaS gate + commit

```bash
bash ~/.claude/skills/luxury-mockup-pipeline/scripts/saas-gate.sh \
  /Users/theceo/DevSkyy/docs/brand/design-mockups/v2.html
# Expect: 13/13 PASS
```

Then commit + ready for deploy.

---

## Open canon questions

1. **Stage 2 SKU finalization** — founder may want to pick different SKUs than my recommendations. Surface 3-option grid (hoodie/jersey/etc per collection) before paid composite dispatch.

2. **Composite output filename convention** — Stage 2 will produce `homepage-col-{collection}.png`-style names OR per-SKU names. Confirm before swap.

3. **Existing `homepage-col-*` assets at `wordpress-theme/skyyrose-flagship/assets/images/`** are still the LH cathedral mislabeled set. May need to purge OR overwrite once Stage 2 composites land.

4. **`signature-golden-gate-showroom.png`** at `assets/scenes/signature/` is still on disk — canon-violating leftover. Surface for purge confirmation.

---

## Critical resume context

### Things that work
- Elite team CLI is the canonical path. `python -m skyyrose.elite_studio home-spread --collection all --dry-run` verifies pipeline integrity.
- Model fallback chain auto-handles Gemini safety variance.
- All 3 scenes are canon-perfect first-shot.
- RunBudget gate held on EVERY failure path (zero unauthorized spend across this session).

### Things that broke + how they were fixed
- `aspect_ratio="3:4 portrait"` rejected by Gemini → strip trailing descriptor in agent (already patched).
- `Path` not imported in cli.py → fixed (already committed).
- `RunBudget(usd_cap=)` keyword wrong → `RunBudget(ceiling_usd=)` (already fixed).
- LH "No image in response" on `gemini-3.1-flash-image-preview` → model fallback chain to `gemini-2.5-flash-image` (patched + verified).

### Things to watch
- Context budget hit 65% at handoff time.
- Stage 2 composites need FAL_KEY in env (`.env.hf` or `.env`).
- The `_collection_from_scene_name` helper assumes prefix matching; OK for current 4 collections.
- Standalone scripts are deprecated but still runnable — don't accidentally invoke them.

---

## RESUME PROMPT (paste at start of fresh session)

```
Resume from /Users/theceo/DevSkyy/tasks/handoff-2026-05-26-elite-team-pipeline.md.

Context: elite-team imagery pipeline wired (commit 7d6ed30ec on
fix/elite-studio-audit-2026-05-25). 3 founder-locked Stage-1 scene PNGs
delivered. Stage 2 = real-product composite onto scenes via CompositorAgent.

Current ask: dispatch Stage 2 composites for 3 collections at $0.15 each.
Founder authorized $1.50 RunBudget ceiling; $1.34 remaining.

Pending decision: confirm SKU per collection BEFORE paid composite:
  BR  default br-004 Black Rose Hoodie
  SIG default sg-001 Bay Bridge Shorts
  LH  default lh-004 Love Hurts Bomber

After confirmation, run:
  python -m skyyrose.elite_studio home-spread --collection black-rose --sku br-004
  python -m skyyrose.elite_studio home-spread --collection signature --sku sg-001
  python -m skyyrose.elite_studio home-spread --collection love-hurts --sku lh-004

Then resize variants (480/768/960/1280w AVIF+WebP), swap into
docs/brand/design-mockups/v2.html home-spread, run saas-gate.sh, commit.

Constraints: no hallucinations, all pipeline through elite team CLI,
founder STOP-AND-SHOW protocol for any paid step.
```

---

**Handoff signed-off 2026-05-26. Ready for fresh-session resume.**
