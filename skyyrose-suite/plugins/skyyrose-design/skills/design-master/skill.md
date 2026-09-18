---
name: design-master
description: >
  SkyyRose gpt-image-2 prompt composer. Given a SKU (or freeform request),
  collection, presentation mode, and view, assembles a production-ready
  gpt-image-2 edit-mode prompt in the exact grammar of scripts/oai_render/prompt.py
  and emits the gpt-image-2 output contract JSON. Never fires a paid render
  without the STOP-AND-SHOW manifest and explicit "y" from the user.
---

# design-master — SkyyRose gpt-image-2 Prompt Composer

## Purpose

design-master is the **prompt-composition skill** for the SkyyRose gpt-image-2
product render pipeline. Given an input (SKU or freeform garment description),
a collection, a presentation mode, and a view, it:

1. Reads the product dossier (for SKU-based requests).
2. Queries the element library to select lighting, background, and fidelity
   fragments appropriate to the collection and mode.
3. Assembles a prompt that mirrors the exact section order in
   `scripts/oai_render/prompt.py` — the canonical render pipeline.
4. Emits the **gpt-image-2 output contract JSON** defined in
   `references/element-schema.md`.
5. Shows the STOP-AND-SHOW cost manifest and waits for explicit "y" before
   setting `ready_to_render: true`.

design-master never calls the OpenAI API directly. It produces the contract
JSON that a downstream runner (e.g., `scripts/oai_render/run.py`) consumes.

---

## When to Use

- "Build the render prompt for br-004, ghost, front."
- "Give me a gpt-image-2 prompt for the Love Hurts Bomber, on-model, back."
- "Design a product shot for the Signature Sherpa, flatlay."
- Any time a SkyyRose product image needs a production-quality prompt before
  reaching the paid API.

Do NOT use design-master for:
- Non-SkyyRose brand imagery (use a generic image prompt skill).
- Requesting direct API execution without the STOP-AND-SHOW gate.
- Pair (two-garment) prompts — use `build_pair_prompt()` in prompt.py directly;
  that path has its own `PAIR_NEGATIVE_GUARDRAILS`.

---

## Input Parameters

| Parameter | Type | Required | Values | Default |
|-----------|------|----------|--------|---------|
| `sku` | string | one of sku/request | e.g. `br-004` | — |
| `request` | string | one of sku/request | freeform garment description | — |
| `collection` | string | yes | `black-rose`, `love-hurts`, `signature`, `kids-capsule` | — |
| `mode` | string | no | `ghost`, `on-model`, `flatlay` | `ghost` |
| `view` | string | no | `front`, `back` | `front` |
| `template_id` | string | no | id from `references/skyyrose-templates.json` | — |

When `template_id` is supplied, its pre-filled fields serve as defaults;
per-call parameters override them.

---

## Data Sources

### 1. Product Dossier (SKU-based requests)

Dossiers live at:
```
wordpress-theme/skyyrose-flagship/data/dossiers/<slug>.md
```
Each dossier has YAML frontmatter:
```yaml
sku: br-004
name: BLACK Rose Hoodie
collection: black-rose
logo_reference: data/brand-logos/three-rose-cluster.md
reference_image: data/product-references/br-004-hoodie-real-front.jpeg
```
And zone-structured body prose (garment type lock, Branding by placement,
Negative guardrails, Scene direction).

design-master reads:
- `reference_image` → populates `reference_images[]` in the output contract.
- Full dossier body → injected verbatim as the EXACT PRODUCT SPEC block
  (after stripping the Scene direction section, which is overridden by the
  PRESENTATION/VIEW directives).
- `name`, `sku`, `collection` → the PRODUCT line.

### 2. Element Library

Query the seed library at `~/.claude/skills/universal-learner/references/skyyrose-seed-elements.json` (the universal-learner corpus — this file does not exist locally under design-master) using:
- `collection_tags` matching the request's collection.
- `mode_tags` matching the requested mode.
- `grammatical_position` matching the section you need (lighting, background,
  fidelity, etc.).

Filter out any element with a non-empty `brand_canon.violation_flags` array.
Select elements ranked by `brand_alignment` (desc), then `gpt_image2_compatibility`
(desc), then `reusability_score` (desc).

For standard pipeline renders the BASE_PROCEDURE (from prompt.py) is used
verbatim — element queries are most useful for editorial/campaign one-offs where
the seed elements add collection-specific atmosphere not in the base procedure.

### 3. Founder Corrections

`get_product(sku)["corrections"]` (from `skyyrose.core.product`) — each line is `{text, authority}`; `FOUNDER_VERBATIM` lines are the founder's review-board notes, `AGENT_ADDED` lines were added by a render-QC review and yield to the founder's spec. Read for any SKU before finalising the assembled prompt; inject corrections into the EXACT PRODUCT SPEC block. When the SKU key is absent, the corrections array is treated as empty.

### 4. Template Presets

`references/skyyrose-templates.json` holds 5 named presets. Each is a partial
output-contract object. Merge a preset with per-call inputs (call wins on
conflict) to speed up repeated render types.

---

## Assembly Procedure

Mirror the section order in `scripts/oai_render/prompt.py:build_prompt()` exactly.
Deviation from this order causes gpt-image-2 to weight sections incorrectly.

```
BASE_PROCEDURE block:
  Line 1: "Produce a single, photorealistic luxury e-commerce product photograph of ONE garment."
  Line 2: FRAMING: vertical 4:5 portrait, garment centered, full garment in frame with even margins.
  Line 3: PRESENTATION block (filled from mode)
  Line 4: VIEW directive (filled from view)
  Line 5: LIGHTING: soft, even studio light, gentle directional key, subtle natural drop shadow.
  Line 6: BACKGROUND (ghost/flatlay → clean studio; on-model → COLLECTION_SCENE)
  Line 7: FIDELITY: reproduce the garment EXACTLY as shown in the reference images...
  Line 8: MATERIAL: render the true surface texture named in the spec...
  Line 9: PHOTOREALISM: some references are FLAT vector technical drawings...
  Line 10: CONSISTENCY: identical catalog styling across every product in the same presentation style.

[blank line]

PRODUCT: <name> (SKU <sku>) — <Collection Title> collection.

[blank line]

REFERENCE IMAGES — provided in this exact order; "image 1" is the first image attached...:
  image 1 — <label for reference_images[0]>
  image 2 — <label for reference_images[1]>   (if present)

[blank line]

EXACT PRODUCT SPEC — CONSTRUCTION AND MATERIALS ONLY ...:
<dossier body, scene-direction section stripped, injection-sanitized>

[blank line]

PRESENTATION OVERRIDE: use the PRESENTATION + VIEW lines at the top for framing/pose;
IGNORE any conflicting pose, setting, or scene direction in the spec above...

[blank line]

FOUNDER CORRECTIONS — (if corrections_for(sku) is non-empty):
  - [ghost] <correction line>

[blank line]  (if corrections present)

CRITICAL — SPORT PATCH FIDELITY: (only for jersey SKUs with is_patch=true, front view)

[blank line]  (if patch block present)

NEGATIVE_GUARDRAILS:
DO NOT add text, watermarks, mockup labels, size tags, price tags, multiple garments,
collage panels, or any branding not physically present on the garment. DO NOT crop out any
part of the garment or its graphics.
BRANDING IS EXHAUSTIVE: the references and spec show EVERY logo and graphic this garment
carries. If a panel shows no logo in its reference, render that panel with NO logo...
OUTPUT FORMAT: one single full-bleed photograph [the entire frame is ONE continuous photo].
No reference sheet. No multiple panels. No collage. No grid. No split-screen.
```

### PRESENTATION blocks (verbatim from prompt.py)

**ghost:**
```
PRESENTATION: clean ghost-mannequin / invisible-form — the garment holds its 3D shape
with NO visible person, no hanger, no mannequin. Exactly ONE garment — never a flat
multi-panel technical diagram or multiple views in one frame.
```

**on-model:**
```
PRESENTATION: worn by a single full-body fashion model, natural confident pose, neutral
expression, professional styling. Exactly ONE garment / one look — never a flat diagram
or multiple views in one frame.
```

**flatlay:**
```
PRESENTATION: the single garment laid flat, top-down, neatly arranged on a seamless
surface. Exactly ONE garment — never a multi-panel technical diagram.
```

### VIEW directives (verbatim from prompt.py)

**front:**
```
VIEW: render the FRONT of the garment, front-facing. Any BACK tech-flat reference is
construction-only — do NOT render a back view or a second panel; output a single FRONT view.
```

**back:**
```
VIEW: render the BACK of the garment, rear-facing — camera positioned directly behind
the garment, centered. Use the BACK tech-flat reference as the authority for everything
on the back panel. Do NOT mirror or replicate the front [the back has its own distinct
layout — render that layout]. Any FRONT tech-flat reference is construction-only — do
NOT render a front view or a second panel; output a single BACK view.
```

### BACKGROUND rules

- `ghost` → `BACKGROUND: seamless, uncluttered neutral light-grey studio backdrop — no props,
  no text, no scene, no logos other than those physically on the garment. Clean product-card aesthetic.`
- `flatlay` → same clean studio backdrop as ghost.
- `on-model` → `BACKGROUND / SCENE: <COLLECTION_SCENE>. The model is photographed within
  this environment; keep the garment sharp, correctly lit, and fully unobstructed — the scene
  is atmosphere, never covering or recoloring the product.`

### COLLECTION_SCENES (verbatim from prompt.py)

| Collection | Scene |
|------------|-------|
| `black-rose` | the Bay Bridge silhouetted behind, shot from the Oakland shore at blue hour, framed by a moody black-rose garden — dark romantic luxury, dramatic low light, roses in deep shadow |
| `love-hurts` | a darkly romantic Beauty-and-the-Beast setting seen from the Beast's point of view — a candlelit gothic château interior, ornate and brooding, shadow-heavy, emotionally intense |
| `signature` | the Golden Gate Bridge and Bay Area skyline at golden hour — confident West-Coast street-luxury energy, warm sunlight, effortless swag |
| `kids-capsule` | a regal throne room, 'the heir to the throne' — opulent gold-and-velvet palace setting, playful young-royalty grandeur, warm cinematic light |

There is **no generic fallback** for on-model. If a collection is not in the table above,
raise an error rather than inventing a scene.

### Injection sanitization rules

Before injecting any dossier body text, drop lines that match any of these patterns
(they trigger multi-panel collage output in gpt-image-2):
- `multiple (views?|angles?|panels?)`
- `reference sheet`
- `(shown|seen|viewed|photographed) from`
- `views? (of|from)` / `angles?:`
- `(available|comes) in` / `also available` / `(styled|paired|worn) with`
- `split-screen` / `collage` / `grid of`

Also drop lines containing more than one view-noun mention (front/back/side/rear/detail/
three-quarter). A single positional mention ("graphic on the front of the garment") is
legitimate placement spec and must survive. Strip the Scene direction section from dossier
bodies before injection (pose/setting governed by PRESENTATION+VIEW directives, not dossier prose).

The API call (executed downstream by the runner, not by design-master) is:
```python
client.images.edit(
    model="gpt-image-2",
    image=[<reference_image_bytes>, ...],   # at least one required
    prompt=<assembled_prompt_string>,
    size="1024x1536",
    quality="high",
    background="auto",
    n=1
)
```

There is NO `negative_prompt` field and NO `seed` field in the gpt-image-2 API.
Negatives are baked into the prompt as `DO NOT ...` sentences in the NEGATIVE_GUARDRAILS block.

---

## Structured JSON Output (gpt-image-2 Output Contract)

See `references/element-schema.md` for the full field definitions.
design-master emits one of these per render request:

```json
{
  "sku": "br-004",
  "collection": "black-rose",
  "mode": "ghost",
  "view": "front",
  "presentation_block": "PRESENTATION: clean ghost-mannequin / invisible-form ...",
  "view_directive": "VIEW: render the FRONT of the garment, front-facing ...",
  "background": "BACKGROUND: seamless, uncluttered neutral light-grey studio backdrop ...",
  "product_line": "PRODUCT: BLACK Rose Hoodie (SKU br-004) — Black Rose collection.",
  "reference_images": [
    "data/product-references/br-004-hoodie-real-front.jpeg"
  ],
  "reference_labels": [
    "image 1 — front reference photograph of the real manufactured BLACK Rose Hoodie (br-004-hoodie-real-front.jpeg)"
  ],
  "dossier_spec_path": "wordpress-theme/skyyrose-flagship/data/dossiers/black-rose-hoodie.md",
  "negative_guardrails": "DO NOT add text, watermarks, mockup labels, size tags, price tags, multiple garments, collage panels, or any branding not physically present on the garment ...",
  "is_patch": false,
  "founder_corrections": [],
  "size": "1024x1536",
  "quality": "high",
  "background_api": "auto",
  "estimated_cost_usd": 0.06,
  "ready_to_render": false
}
```

`ready_to_render` is always `false` in design-master output. The downstream
runner sets it to `true` only after the user confirms the STOP-AND-SHOW manifest.

### Size defaults

| Use | size | notes |
|-----|------|-------|
| Product card / PDP (default) | `1024x1536` | 4:5 portrait, matches BASE_PROCEDURE framing |
| Square social tile | `1024x1024` | override when explicitly requested |
| Landscape banner | `1536x1024` | override when explicitly requested |

Always state the size in the output contract so the runner does not have to infer it.

---

## STOP-AND-SHOW Cost Manifest

Before any render can proceed, design-master prints this manifest and waits
for explicit `y` or `yes`. This gate is non-negotiable — it applies even in
batch runs.

```
STOP — Confirm before proceeding:

Action  : gpt-image-2 edit render
SKU     : br-004 — BLACK Rose Hoodie
Source  : data/product-references/br-004-hoodie-real-front.jpeg
Mode    : ghost / front
Size    : 1024x1536 (quality: high)
Cost    : ~$0.06  (1 render × ~$0.04–0.08 per image)

Proceed? [y/N]
```

Only after `y` does `ready_to_render` flip to `true` in the contract.

Cost estimate guidance:
- gpt-image-2 edit, quality high, 1024x1536: approximately $0.04–0.08 per image.
- Batch of N renders: show `N × ~$0.06 = ~$X.XX` in the manifest.
- When cost is unknown (custom size), show `~$0.08 (upper bound)` and note the uncertainty.

---

## Worked Example — br-004 Black Rose Hoodie, ghost, front

**Input:**
```
sku: br-004
collection: black-rose
mode: ghost
view: front
```

**Step 1 — Read dossier frontmatter:**
```yaml
sku: br-004
name: BLACK Rose Hoodie
collection: black-rose
reference_image: data/product-references/br-004-hoodie-real-front.jpeg
```

**Step 2 — Determine blocks:**
- mode = `ghost` → clean studio background
- view = `front` → front VIEW directive
- is_patch = false (pullover hoodie, not a jersey)
- founder corrections: `get_product("br-004")["corrections"]` (list of `{text, authority}`; empty when the SKU has none)

**Step 3 — Assembled prompt (abridged):**
```
Produce a single, photorealistic luxury e-commerce product photograph of ONE garment.
FRAMING: vertical 4:5 portrait, garment centered, full garment in frame with even margins.
PRESENTATION: clean ghost-mannequin / invisible-form — the garment holds its 3D shape
with NO visible person, no hanger, no mannequin. Exactly ONE garment — never a flat
multi-panel technical diagram or multiple views in one frame.
VIEW: render the FRONT of the garment, front-facing. Any BACK tech-flat reference is
construction-only — do NOT render a back view or a second panel; output a single FRONT view.
LIGHTING: soft, even studio light, gentle directional key, subtle natural drop shadow.
BACKGROUND: seamless, uncluttered neutral light-grey studio backdrop — no props, no text,
no scene, no logos other than those physically on the garment. Clean product-card aesthetic.
FIDELITY: reproduce the garment EXACTLY as shown in the reference images — silhouette,
fabric, color, every graphic, logo, embroidery, label, and sport patch in its exact position
and size. Do NOT invent, omit, resize, recolor, duplicate, or reposition any element.
MATERIAL: render the true surface texture named in the spec — satin must read glossy and
light-catching, sherpa must show visible pile, nylon must look smooth and technical, fleece
must look soft and matte. A garment rendered in the wrong material is an invalid result.
PHOTOREALISM: some references are FLAT vector technical drawings (tech flats). They define
construction and graphics ONLY — the output must be a fully photorealistic photograph of the
real manufactured garment: dimensional fabric with natural drape, real seams, real texture,
true studio lighting. A flat, illustrated, or vector-styled output is an invalid result.
CONSISTENCY: identical catalog styling across every product in the same presentation style.

PRODUCT: BLACK Rose Hoodie (SKU br-004) — Black Rose collection.

REFERENCE IMAGES — provided in this exact order; "image 1" is the first image attached,
"image 2" the second, and so on:
  image 1 — front reference photograph of the real manufactured BLACK Rose Hoodie
    (br-004-hoodie-real-front.jpeg)

EXACT PRODUCT SPEC — CONSTRUCTION AND MATERIALS ONLY (replicate the physical garment
details — fabric, colorway, graphics, logos, patches, labels — precisely; pose, scene,
framing, and layout are governed ONLY by the PRESENTATION and VIEW directives above):
[dossier body injected verbatim — scene-direction section stripped]

PRESENTATION OVERRIDE: use the PRESENTATION + VIEW lines at the top for framing/pose;
IGNORE any conflicting pose, setting, or scene direction in the spec above. The spec
governs WHAT is on the garment, not how it is photographed.

DO NOT add text, watermarks, mockup labels, size tags, price tags, multiple garments,
collage panels, or any branding not physically present on the garment. DO NOT crop out any
part of the garment or its graphics.
BRANDING IS EXHAUSTIVE: the references and spec show EVERY logo and graphic this garment
carries. If a panel (for example the back) shows no logo in its reference, render that panel
with NO logo — a blank panel is correct; an added logo is an invalid result.
OUTPUT FORMAT: one single full-bleed photograph [the entire frame is ONE continuous
photo]. No reference sheet. No multiple panels. No collage. No grid. No split-screen.
```

**Step 4 — Output contract:**
```json
{
  "sku": "br-004",
  "collection": "black-rose",
  "mode": "ghost",
  "view": "front",
  "presentation_block": "PRESENTATION: clean ghost-mannequin / invisible-form ...",
  "view_directive": "VIEW: render the FRONT of the garment, front-facing ...",
  "background": "BACKGROUND: seamless, uncluttered neutral light-grey studio backdrop ...",
  "product_line": "PRODUCT: BLACK Rose Hoodie (SKU br-004) — Black Rose collection.",
  "reference_images": ["data/product-references/br-004-hoodie-real-front.jpeg"],
  "reference_labels": [
    "image 1 — front reference photograph of the real manufactured BLACK Rose Hoodie (br-004-hoodie-real-front.jpeg)"
  ],
  "dossier_spec_path": "wordpress-theme/skyyrose-flagship/data/dossiers/black-rose-hoodie.md",
  "negative_guardrails": "DO NOT add text, watermarks ...",
  "is_patch": false,
  "founder_corrections": [],
  "size": "1024x1536",
  "quality": "high",
  "background_api": "auto",
  "estimated_cost_usd": 0.06,
  "ready_to_render": false
}
```

**Step 5 — STOP-AND-SHOW manifest (print, wait for y):**
```
STOP — Confirm before proceeding:

Action  : gpt-image-2 edit render
SKU     : br-004 — BLACK Rose Hoodie
Source  : data/product-references/br-004-hoodie-real-front.jpeg
Mode    : ghost / front
Size    : 1024x1536 (quality: high)
Cost    : ~$0.06

Proceed? [y/N]
```

---

## Brand Canon Guard

design-master applies the canon guard from `references/element-schema.md`
before accepting any element into a prompt.

**Affirm** (raise `brand_alignment`): concrete/urban/Oakland, streetwear,
luxury-athletic, sport-heritage, cinematic-desaturated, monogram-editorial.

**Block** (non-empty `violation_flags` → element rejected):
- European-luxury-house lineage — full enumeration in `references/element-schema.md`
  under "Brand-canon validation". Any element evoking that editorial register is rejected.
- pastel/preppy palette.
- minimalist-corporate (cold white + Swiss grid aesthetic).
- cartoon / illustrated / vector-styled output.
- mannequin-seams visible.
- stock-photo lighting (ring-flash beauty dish, flat commercial).

The Five style anchors (affirmed references for on-model/campaign):
**Kith, Oaklandish, Culture Kings, Fear of God, Palm Angels.**
These inform atmosphere and model-styling choices. They are never cited verbatim
in a prompt — they shape the selection of lighting, background, and fidelity elements.

---

## Schema Reference

`references/element-schema.md` — shared contract between universal-learner (writer)
and design-master (reader). Copied verbatim from
`/Users/theceo/.claude/skills/universal-learner/references/element-schema.md`.
Do not modify the copy here; sync from source when the contract updates.

`references/skyyrose-templates.json` — 5 named render presets.

`references/luxury-element-taxonomy.md` — 40+ luxury-fashion vocabulary terms
grouped by grammatical position, tagged by collection and mode.
