# Immersive Hub — Dedicated Hero Master Prompts (Midjourney) · v2

**Purpose:** one dedicated cinematic hero master per collection for the `/experiences/` full-bleed blocks (placement `experience-hero`). v2 (2026-06-17) = imagery-team concepts (4 photography-directors) + Brand Guardian pass. Replaces v1's ornate-ballroom interim look.

## The 4 scene concepts
| Collection | Concept | One line |
|---|---|---|
| Signature | **4 AM on the Ledge** | The night the brand was born — Oakland rooftop, gold rose on concrete, Bay Bridge burning in the haze. |
| Black Rose | **Concrete Refusal** | A black rose forced through a crack in a West Oakland I-880 pillar — silver-rimmed, rain-wet, refusing the dark. |
| Love Hurts | **The Beast at the Threshold** | A rain-slick Oakland alley — the Beast's gate ajar, only the snapped crimson rose left burning. |
| Kids Capsule | **The City Is the Throne** | A child, back to camera, faces the Oakland skyline at dusk — the city built for them is the inheritance. |

## Generation spec (every prompt)
- `--ar 16:9 --v 7 --style raw` · master 2560×1440; export WebP+AVIF + the srcset ladder (640·1024·1536·2048·2560w) into `assets/branding/hero/`.
- **Composition law (these are BACKGROUNDS for a centered lockup):** center third = calm negative space, focal subject in lower/side thirds, edges fall to a dark vignette so the overlaid lockup reads.
- **Brand register (LOCKED):** Kith / Oaklandish / Culture Kings / Fear of God / Palm Angels. Oakland/Bay concrete luxury. NEVER European luxury-house / baroque ballroom / fairytale castle. **No blue/navy anywhere** (founder ban).

---

## ① SIGNATURE — "4 AM on the Ledge"  (gold #D4AF37 + rose-gold #B76E79)
```
Oakland rooftop concrete parapet at 4 AM, single metallic rose-gold rose resting on the ledge lower-left third, long warm shadow across raw aggregate concrete toward camera, distant Bay Bridge cables glowing amber-gold in warm predawn haze lower-right third, open gradient sky filling center and upper two-thirds transitioning from deep gold #D4AF37 at horizon to near-black #0A0A0A overhead, dust motes and faint fog drift across bridge cables, luxury streetwear editorial, cinematic anamorphic wide, warm-golden grade throughout, no model no people, calm empty sky center for overlaid title, dark vignette toward all four edges heaviest at top-center, Fear of God x Oaklandish x Kith editorial mood, photographic, ultra-detailed, 8k --ar 16:9 --style raw --v 7 --no text, watermark, logo, people, figures, silhouettes, ornate baroque ballroom, fairytale castle, European luxury interior, chandelier, marble columns, cold blue tones, blue, navy, silver grade, beach, surfboard, tech-minimalism, white studio
```

## ② BLACK ROSE — "Concrete Refusal"  (black #0A0A0A + silver #C0C0C0)
```
Rain-slick West Oakland freeway underpass at 2am, monolithic I-880 concrete support column scarred with decades of graffiti ghosts filling the entire left third of the frame from floor to top edge, a single black rose with silver-chrome petal edges growing through a crack at the column base in the lower-left third, hard silver key light raking at 25 degrees from camera-left catching only the petal rims and casting a thin liquid-silver reflection stripe across wet dark asphalt, Port of Oakland container crane silhouettes barely resolved through cold fog at far right edge, vast dark open negative space in the upper center and center-right of frame for a title overlay, deep atmospheric void ceiling, monochrome — black #0A0A0A dominates every surface silver #C0C0C0 only on rose petal rims and asphalt reflection, cool moonlight, zero color cast zero warmth zero blue, heavy radial vignette darkest at upper corners, brutalist streetwear-luxury editorial, cinematic anamorphic, Fear of God x Oaklandish mood, ultra-detailed, 8k --ar 16:9 --v 7 --style raw --no text watermark logo people blue navy warm color grading gold tones red tones baroque ballroom fairytale castle warm color interior decor ornate architecture cartoon stock photo
```

## ③ LOVE HURTS — "The Beast at the Threshold"  (crimson #DC143C / #9B0F2E)
```
Rain-slick East Oakland industrial alley at deep night, wide cinematic anamorphic shot, raw red-brick wall right third glistening with moisture, corrugated iron gate left third slightly ajar revealing pure darkness beyond, a single deep-crimson rose resting snapped on wet black asphalt at lower center, rose petals luminous and intact against the dark ground, crimson neon bleed off-screen left casting hard red fill across wet brick and asphalt reflection pools, color palette blood-crimson #DC143C and deep shadow-crimson #9B0F2E against near-black #0A0A0A, calm open dark negative space in the center-vertical third of frame for title overlay, heavy vignette pulling to near-black at all four corners, no people, no faces, presence felt only through the open gate, Fear of God cinematic stillness meets Palm Angels street-luxe detail meets Culture Kings drop-moment tension, Oakland civic grit, luxury streetwear editorial, photographic, ultra-detailed, 8k --ar 16:9 --style raw --v 7 --no text, watermark, logo, ornate baroque ballroom, fairytale castle, gilded interior, chandeliers, Valentine florals, soft-focus romance, pink, purple, blue, navy, European fashion editorial, cartoon, people, faces
```

## ④ KIDS CAPSULE — "The City Is the Throne"  (rose-gold #B76E79 + gold #D4AF37 + indigo #1A1228)
```
A child in a dark red-black colorblock luxury hoodie stands at the edge of a raw concrete rooftop parapet in Oakland at magic-hour dusk, back three-quarters to camera, facing the city skyline, posture unhurried and grounded, a neatly folded purple-black colorblock hoodie resting on the concrete ledge beside them, directional warm rose-gold sunlight from camera-right catching the child's far shoulder and pooling on the rough concrete surface, Oakland downtown skyline glowing amber-gold at building faces, Port of Oakland crane silhouettes far left, Bay Bridge string-light arc low on the right horizon, sky grading from deep warm gold #D4AF37 at the horizon through rose-amber #B76E79 haze into deep indigo #1A1228 at the zenith, entire upper sky as calm empty negative space for an overlaid title, no text no logo no watermark, child occupies lower-left third frame, folded garment anchors lower-right, concrete parapet as horizontal ground line, natural dark vignette at left and right edges from sky depth, cinematic anamorphic 16:9, luxury streetwear editorial, Kith Kids x Oaklandish x Fear of God photographic mood, ultra-detailed, 8k --ar 16:9 --style raw --v 7 --no text, watermark, logo, crown, throne chair, throne, tiny crown, cartoon, pastel, blue, navy, ornate baroque ballroom, fairytale castle, creepy, child facing camera, staring at camera, soft focus, saccharine, generic stock photo, European luxury house aesthetic, white background, floral props
```

---

## After generation — drop-in procedure
1. Save each master to `wordpress-theme/skyyrose-flagship/assets/branding/hero/<slug>-hero-2560w.webp` (+ avif) and the ladder `-640/-1024/-1536/-2048/-2560w`.
2. Set `imagery.hero` in each registry entry, `data/logo-registry.json` → `collections.<slug>`, to `branding/hero/<slug>-hero`.
3. Re-run the SOT build + `verify-collection-sot.py` (the min-2560 gate passes once masters exist).
4. The `experience-hero` placement auto-engages the srcset; re-render the hub. Each block now its own canon scene; the gold Signature lockup pops on the darker master.
