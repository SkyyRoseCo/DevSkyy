# SkyyRose — Collections Scroll-World (spec + prompt-pack)

**Technique:** scroll-scrubbed continuous camera fly-through (Higgsfield pre-rendered).
**Structure:** ONE page, 5 scenes, Architecture **A** (continuous forward take — grounded/realistic, no connectors).
**Art direction:** gothic-noir cinematic **realism** (photoreal-architectural, full-bleed, dark).
**Target:** skyyrose.co WordPress template (deploy-gated). **Mobile:** desktop + mobile beta.

Camera: forward-only. 5 scenes → 5 legs (leg 0 = opening dive into SIG; legs 1–4 = traverse into BR/LH/KC/Finale). No `--end-image`, no connectors.

---

## Brand kit (from canon — no interview needed)

| Token | Hex | Role in this build |
|-------|-----|--------------------|
| Dark | `#0A0A0A` | Scene **background** (full-bleed, reads premium) |
| Rose Gold | `#B76E79` | Global **accent** (nav, CTA, KC) |
| Gold | `#D4AF37` | Signature accent |
| Silver | `#C0C0C0` | Black Rose accent |
| Crimson | `#DC143C` | Love Hurts accent |

Tone: cinematic · luxury · gothic-noir · concrete-luxe. Lineage: Fear of God / Palm Angels / Culture Kings — **never** European heritage houses.

---

## STYLE PREAMBLE (byte-identical in every scene-still prompt)

> Ultra-photorealistic cinematic architectural photography, full-bleed, no floating island, no miniature. A single cohesive luxury space rendered in a high-contrast gothic-noir grade: deep shadows, moody filmic volumetric light, polished concrete and rose-gold metal, editorial dark-luxury-fashion quality (Fear of God / Palm Angels lineage, never European heritage). Cohesive palette across the whole world: rose gold #B76E79, gold #D4AF37, silver #C0C0C0, crimson #DC143C on a near-black #0A0A0A ground. Shallow depth of field, no people, absolutely no text, no letters, no numbers, no logos, centered composition with headroom.

Per-scene `Subject:` line leans that collection's accent. Aspect `3:2`, `--resolution 2k --quality high`, model `gpt_image_2`.

---

## Scenes (subject + copy for the engine)

### 1 — Signature (HERO)  · accent gold `#D4AF37`  · focal = Bay Area, HEAVY OAKLAND
- **Subject:** `A luxury Signature showroom high above the water — floor-to-ceiling glass framing the OAKLAND skyline and Bay at dusk: the Tribune Tower, Lake Merritt necklace-of-lights, the Port of Oakland container cranes, Bay Bridge, a moored yacht (The Town / Oakland, NOT San Francisco, NOT Golden Gate). Polished concrete floor, gold-veined marble plinth at center holding a single draped garment form, brushed-gold fixtures, one shaft of gold-hour light. Focal point: the Oakland city view + gold-lit plinth, centered.`
- Reference: steer HARD to Oakland landmarks (Tribune Tower, port cranes, Lake Merritt) — AI defaults to Golden Gate/SF unless forced. Optionally feed an Oakland reference photo via `media_import_url`.
- eyebrow: `THE SIGNATURE` · title: `` · body: `Oakland-born luxury, cut in gold and earned on the block.` · tags: `Signature`, `Gold`
- (Section 1 title = site hero line.)

### 2 — Black Rose  · accent silver `#C0C0C0`  · focal = THE BLACK ROSE + star emblem
- **Subject:** `A gothic rooftop garden at night above the Oakland skyline — silver moonlight, concrete parapets, wrought iron. At center, a single perfect BLACK ROSE in bloom (deep obsidian petals, silver-edged), and behind/around it the Black Rose collection emblem: a black rose inside a silver-outlined five-point star on a black heart base. The beauty of Black rendered as armor. Focal point: the black rose + star emblem, centered.`
- Reference: founder-supplied collection logo `/Users/theceo/Downloads/OpenAI Playground 2026-07-10 at 18.29.09.png` (black rose in silver star on heart base) — feed via `media_import_url`/`media_upload` so the emblem matches canon exactly. Eyes-on the source before use.
- eyebrow: `BLACK ROSE` · title: `Armor For The Ones Who Stood` · body: `Silver-edged armor for anyone the concrete already made stand up.` · tags: `Black Rose`, `Armor`
- Canon: armor / "you already stood up" / "concrete answering back". (No other collection's voice.)

### 3 — Love Hurts  · accent crimson `#DC143C`  · focal = THE ENCHANTED ROSE
- **Subject:** `A candlelit cathedral rose chamber — towering crimson stained glass, deep-red roses spilling over dark stone, wax candlelight. At center, THE ENCHANTED ROSE: a single crimson rose suspended under a glass cloche/bell jar, one petal drifting, glowing from within (Beauty-and-the-Beast enchanted rose motif). Romantic-dark, reverent. Focal point: the enchanted rose under glass, centered.`
- Reference: reuse existing on-brand assets `assets/scenes/love-hurts/love-hurts-enchanted-rose.webp` (+ `love-hurts-beast-room.webp`) via `media_import_url`/`media_upload` — exact look, zero drift. Eyes-on before use.
- eyebrow: `LOVE HURTS` · title: `The Bloodline That Raised Me` · body: `Crimson and thorn — the love that scarred you is the love that made you.` · tags: `Love Hurts`, `Crimson`
- Canon: "the bloodline that raised me" = **Love Hurts ONLY** (locked here, never borrowed).

### 4 — Kids Capsule  · accent rose gold `#B76E79`  · focal = THE MASCOT (full-body walk-in)
- **Subject:** `A brighter capsule set — the same concrete-luxe world lifted into soft rose-gold light, gentle warm fill, playful but still luxury, cleaner shadows. At center, THE SKYYROSE MASCOT (the Love Hurts Girl, site host) in a FULL-BODY walk-in pose, mid-stride entering frame toward camera, exactly as she appears on the live site. Focal point: the mascot, full body, centered.`
- Reference (MANDATORY): condition on canonical mascot `assets/images/mascot/skyy-canonical-v2.png` via `media_import_url`/`media_upload` — the mascot is a LOCKED character; blind prompt would invent a different girl. Eyes-on `skyy-canonical-v2.png` first; eyes-on the OUTPUT to confirm it matches canon before it ships (product-image-fidelity gate).
- eyebrow: `KIDS CAPSULE` · title: `The Next Generation, Suited` · body: `The same concrete-luxe, cut for the ones coming up.` · tags: `Kids Capsule`, `Rose Gold`

### 5 — Finale / CTA  · accent rose gold `#B76E79`
- **Subject:** `Near-black space, a single polished concrete pedestal holding one hero garment silhouette under a tight rose-gold spotlight, faint rose-gold monogram glow behind (no readable text), volumetric haze, the whole world dissolving to #0A0A0A around it. Focal point: the spotlit hero silhouette, centered.`
- eyebrow: `THE SKYY ROSE COLLECTION` · title: `Enter The Collections` · body: `Four cinematic worlds, one house built from Oakland concrete.` · **cta:** `Shop the Collections` → `/collections/` · tags: (none)

---

## Leg prompts (Architecture A — motion-handoff contract clauses in **bold**, keep verbatim)

`--start-image`: leg 0 = SIG still; legs 1–4 = previous leg's ACTUAL last frame (ffmpeg-extracted). **No `--end-image`.** Params (seedance_2_0): `--mode std --resolution 1080p --aspect_ratio 16:9 --duration 8`.

- **Leg 0 (dive → Signature):** `Single continuous cinematic camera move, no cuts. Begin high and far outside the glass tower at dusk. The camera glides forward THROUGH the floor-to-ceiling glass into the Signature showroom, sweeping toward the gold-lit marble plinth at center. **In the final second, settle back into a slow, steady forward glide toward the far doorway.** [STYLE tail: gothic-noir realism, concrete + rose-gold, palette #0A0A0A/#B76E79/#D4AF37/#C0C0C0/#DC143C]. Smooth, graceful, slow motion, subtle parallax. No text, no captions.`
- **Leg 1 (Signature → Black Rose):** `Single continuous cinematic camera move, no cuts. **Continue the same slow, steady forward glide.** Rising smoothly as the full scale of the gothic rooftop garden reveals below — black roses and silver moonlight over the Oakland skyline — moving toward the armored center form. **In the final second, settle back into a slow, steady forward glide toward the cathedral doorway ahead.** [STYLE tail…]. Smooth, graceful, slow motion, subtle parallax. No text, no captions.`
- **Leg 2 (Black Rose → Love Hurts):** `Single continuous cinematic camera move, no cuts. **Continue the same slow, steady forward glide.** Tracking low and level alongside the deep-red rose beds, foreground thorns sliding past in parallax, into the candlelit cathedral rose chamber toward the crimson altar form. **In the final second, settle back into a slow, steady forward glide toward the next opening.** [STYLE tail…]. Smooth, graceful, slow motion, subtle parallax. No text, no captions.`
- **Leg 3 (Love Hurts → Kids Capsule):** `Single continuous cinematic camera move, no cuts. **Continue the same slow, steady forward glide.** Pushing in close to a single hanging crimson rose until it nearly fills the frame, then easing gently back out as the world lifts into soft rose-gold light and the brighter capsule set opens, moving toward the rose-gold pedestal. **In the final second, settle back into a slow, steady forward glide toward the light ahead.** [STYLE tail…]. Smooth, graceful, slow motion, subtle parallax. No text, no captions.`
- **Leg 4 (Kids Capsule → Finale):** `Single continuous cinematic camera move, no cuts. **Continue the same slow, steady forward glide.** Climbing in a gentle arc as the set falls away to near-black space, then swooping down toward a single spotlit hero garment silhouette on a concrete pedestal under rose-gold light. **In the final second, settle to a slow, steady forward drift holding on the hero silhouette.** [STYLE tail…]. Smooth, graceful, slow motion, subtle parallax. No text, no captions.`

After EACH leg renders: extract its last frame and eyeball it — must read as a calm forward-glide frame (no sideways blur / half-orbit) before rendering the next. A bad handoff frame poisons every later leg.

---

## Generation manifest (what the paid step will cost)

| Item | Model | Count | Notes |
|------|-------|-------|-------|
| Scene stills | `gpt_image_2` | **5** | 3:2, 2k, high |
| Camera legs (video) | `seedance_2_0` | **5** | 1080p, 8s, forward-only |
| Re-roll budget | seedance / kling3_0 | **~3–5** | dark interiors trip Seedance NSFW filter; kling3_0 fallback |
| Mobile encodes | ffmpeg (local) | 0 paid | 720p `-m.mp4` per clip — **no Higgsfield cost** |

**Base = 5 image + 5 video gens.** Exact **$ / credits pending** — needs `higgsfield workspace list` after auth (that's the STOP-AND-SHOW cost line before any gen fires).

---

## Pipeline order (after auth + cost approval)

1. Generate 5 stills concurrently (detached) → review as one cohesive world.
2. Render leg 0 from SIG still → extract last frame → leg 1 → … → leg 4 (SEQUENTIAL, arch A).
3. Encode all 5 clips: `libx264 -crf 20 -g 8 +faststart -an`, native 1080p, `unsharp`.
4. Mobile: 720p `-g 4 -crf 23` `-m.mp4` siblings.
5. Assemble `scrub-engine.js` config (5 sections + copy above + `clipMobile`) → port into a skyyrose.co template (`page-collections.php` or new `template-collections-world.php`).
6. QA seams (headless before/after each seam) + mobile QA (throttled, iOS priming) + reduced-motion.
7. Deploy to skyyrose.co — **STOP-AND-SHOW** (production).

Paid gates: (a) generation spend, (b) production deploy. Both require explicit `y`.
