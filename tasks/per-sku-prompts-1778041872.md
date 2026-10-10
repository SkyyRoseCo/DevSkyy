# Per-SKU Generator Prompts

Generated 2026-05-05 21:31:12

**Total SKUs:** 33
**Canonical dossier loaded:** 33/33
**Vision cache present:** 3/33

---

## br-001

**Vision cache:** present
**Inferred DNA:** garment=crewneck | fabric=Smooth, lustrous knit fabric with a satin-like sheen for the body and sleeves. T | graphic-type='embroidery' | graphic-colors=['#222222', '#666666', '#AAAAAA', '#FFFFFF', '#708070'] | branding-technique='embroidery'
**Engine route:** `gemini-pro` (gemini-3-pro-image-preview) — Complex fabric (Smooth, lustrous knit fabric with a satin-like sheen for the body and sleeves. The collar, cuffs, and hem are made of a matte, ribbed knit.) — Gemini Pro best at material physics
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=2397c → +Layer-3=2312c → +Layer-2=1492c → final=6201c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Crewneck sweatshirt — upper body only, round ribbed neckline, no hood, no buttons, no zipper, no front pocket. NOT a jersey. NOT a hoodie. NOT a jacket. NOT a t-shirt. NOT a tank top. Heavyweight cotton fleece, relaxed fit. **White ribbed neckband, white ribbed sleeve cuffs, white ribbed waist hem** (contrast white trim against the black body — same pattern as the matching joggers in the Black Rose set).

BRANDING — exactly what to render:
> Logo art canonical references:
> - Black Rose three-rose-cluster: `data/brand-logos/black-rose-logo.md`
> - SR monogram (gold lettermark): `data/brand-logos/sr-monogram.md`

### Front
- **front-chest** (~10in tall × proportional width): The Black Rose logo,
  **physically embossed/debossed into the fabric surface** as a tonal raised
  relief. The full art (three roses + stems + thorny vines + cloud) is impressed
  into the fabric — viewer sees the *shapes* in 3D relief but the colors are
  flattened to the base fabric color (no greyscale petals, no green stems, no
  white cloud — all tonal black-on-black). Subtle 3D texture visible only in
  directional/raking light. **Technique:** embossed. **Color:** tonal black-on-black.

### Back
- **back-neck** (small, ~2in wide, top-center just below the white-ribbed
  collar): The SR monogram (gold metallic art — see sr-monogram reference).
  Embroidered directly onto the jersey in gold-tone thread. **Technique:**
  embroidered. **Color:** gold-tone thread (preserves the gold-to-copper
  gradient from the canonical mark).

### Sleeves / Collar / Hem / Other
- **collar-outside / neckband**: White ribbed-knit neckband contrasting against
  the black body. **Technique:** stitched. **Color:** white.
- **left-cuff / right-cuff**: White ribbed-knit sleeve cuffs contrasting
  against the black body. **Technique:** stitched. **Color:** white.
- **hem**: White ribbed-knit waist hem contrasting against the black body.
  **Technique:** stitched. **Color:** white.
- **collar-inside** (~1.75in × 0.75in): Small woven brand label sewn into the
  inside back of the collar. **Technique:** woven-label. **Color:**
  brand-label colors (typically black with brand-color accents).

---

Study the reference image carefully. This is a relaxed n/a called "BLACK Rose Crewneck".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is Smooth, lustrous knit fabric with a satin-like sheen for the body and sleeves. The collar, cuffs, and hem are made of a matte, ribbed knit.. It has EXACTLY 1 graphic element(s):
  #1 "A detailed graphic featuring two stylized roses with leaves, emerging from a cloud or smoke-like base. The roses are depicted in shades of dark grey, mid-grey, and light grey with white highlights. The leaves are a muted greenish-grey. The base is composed of various shades of grey and white."
      WHERE: front chest center — LOCKED POSITION, do not move
      SIZE: approximately 9" H x 6" W — LOCKED SIZE, do not enlarge or shrink
      TECHNIQUE: embroidery
      FINISH: 3D dimensional, raised, textured embroidery
      COLORS: #222222, #666666, #AAAAAA, #FFFFFF, #708070, #555555, #BBBBBB

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  body: #000000 (satin)
  sleeves: #000000 (satin)
  trim: #FFFFFF (matte)

Construction:
  panels: Standard set-in sleeves with a single-panel body construction.
  seams: Standard flatlock seams, tonal stitching throughout.
  closures: None (pullover style).
  details: Ribbed crewneck collar, ribbed cuffs, and ribbed hem band. All ribbed sections are in a contrasting white color.

Render the garment floating on an invisible form (no model, no mannequin) with:
- Deep matte black (#0A0A0A) backdrop with subtle charcoal gradient
- Cool silver key light from upper-left, black fill, thin silver rim light creating metallic edge highlights
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 1 graphic element(s)
  - ONE graphic only — do NOT add a second logo, patch, or mark anywhere
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- NO printed graphics anywhere — not on chest, not on back, not on sleeves, not on hem.
- NO printed text — no "BLACK IS BEAUTIFUL" arched text, no other printed words.
- NO full-color rendering of the rose logo on the front chest — the front-chest
  logo is tonal embossed only. NO kelly-green stems visible. NO white-and-blue
  cloud color visible. NO greyscale rose petals visible. The embossing flattens
  all colors to the base fabric color.
- NO embroidered Black Rose logo on the front chest (the front is embossed,
  NOT embroidered — embroidery would render visible thread color).
- NO embroidered patches on the lower right front (this is NOT a baseball jersey).
- NO SR monogram on the front chest. NO SR monogram on the sleeves. NO SR
  monogram at the back-center. The SR monogram is at the back-neck only.
- NO embroidered roses on mid back (the back-CENTER is empty; the SR monogram
  sits at the back-neck only).
- NO baseball player graphics anywhere.
- NO sleeve patches, sleeve embroidery, sleeve printing — sleeves are clean.
- NO hem or side-seam decoration on the body fabric — the hem is plain ribbed
  knit (white), no logo, no text, no piping.
- NO chest text other than the embossed rose logo.
- NO contrasting-color logos on the body fabric beyond the back-neck SR monogram.
- NO silicone appliqué.
- NO heat-transfer vinyl.
- NO sublimated panels.
- NO black ribbed neckband (the rib trim is WHITE, not tonal black).
```

---

## br-002

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Standard garment — FLUX Pro best value (98% quality, 26% cost)
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1326c → +Layer-3=2383c → +Layer-2=1362c → final=5071c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Black jogger sweatpants — lower body only, elasticated waist with drawstring, tapered leg, ribbed ankle cuffs, side hand pockets, back pockets. **White ribbed waistband** at the top, **white ribbed ankle cuffs** at the bottom (contrast white trim against the black body — same pattern as the matching Black Rose Crewneck). NOT shorts. NOT straight-leg sweatpants. NOT cargo pants. NOT track pants with side stripes. NOT leggings. Heavyweight cotton-blend fleece, relaxed fit through the thigh.

BRANDING — exactly what to render:
> Logo art canonical references:
> - Black Rose three-rose-cluster: `data/brand-logos/black-rose-logo.md`
> - SR monogram (gold lettermark): `data/brand-logos/sr-monogram.md`

### Front
- **left-thigh** (~3in × 2in): The Black Rose logo as a **silicone-appliqué
  patch** — raised silicone fused to the fabric, with the **full multi-color
  art preserved**: greyscale rose petals (light grey to dark grey shading),
  bright kelly-green stems, dark-green thorny vines, white-and-light-blue
  cloud at the base. **Technique:** silicone-appliqué. **Color:** full
  multi-color art (NOT tonal, NOT monochrome).

### Back
- **right-thigh** (small, ~1.5in–2in wide, upper-back-right hip area —
  approximately mirroring the position of the front-left silicone patch
  but on the back): The SR monogram, embroidered directly onto the fabric
  in **gold-tone thread** (matching the gold-to-copper gradient of the
  canonical SR mark). **Technique:** embroidered. **Color:** gold-tone thread.

### Sleeves / Collar / Hem / Other
- **inside-waistband** (~1in × 0.5in): Woven size tag (showing the size
  designation, e.g., "M", "L", "XL"). **Technique:** woven-label. **Color:**
  brand-standard (typically black with white/printed size text).
- **waistband-rib**: White ribbed-knit waistband at the top of the joggers,
  contrasting against the black body. **Technique:** stitched. **Color:** white.
- **left-ankle-cuff / right-ankle-cuff**: White ribbed-knit cuffs at the
  ankle openings, contrasting against the black body. **Technique:** stitched.
  **Color:** white.
- **drawstring**: Flat **white** drawstring threaded through the waistband.
  No metal tips, no branded tips. **Technique:** stitched. **Color:** white.

---

Study the reference image carefully. This is a  called "BLACK Rose Joggers".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Deep matte black (#0A0A0A) backdrop with subtle charcoal gradient
- Cool silver key light from upper-left, black fill, thin silver rim light creating metallic edge highlights
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- NO logo on the right thigh on the FRONT — the silicone patch is on the
  LEFT thigh of the front view only. (The back-right hip carries a small
  embroidered SR monogram, distinct from the front silicone patch.)
- NO Black Rose silicone patch on the back — the back's only branding is
  the small gold SR monogram on the back-right hip.
- NO embroidered logos on the front of the joggers — the front-left thigh
  is silicone-appliqué, NOT embroidery.
- NO embossed/debossed decoration anywhere.
- NO printed graphics or printed text on the legs, hem, or waistband.
- NO contrast-color side stripes down the legs.
- NO back-pocket flap logos, no pocket trim branding.
- NO logo on the front of the ankle cuffs, no logo on the hem fabric.
- NO "BLACK ROSE" wordmark printed across the leg.
- NO sublimated panels, no heat-transfer vinyl, no puff-print decoration.
- NO black drawstring (the drawstring is WHITE — confirmed in set techflat).
- NO black waistband rib (the waistband rib is WHITE — confirmed).
- NO black ankle cuff rib (the ankle cuff rib is WHITE — confirmed).
- NO chest, sleeve, or upper-body decoration (this is a lower-body-only garment).
- NO tonal/monochrome silicone — the front patch IS in full multi-color
  (preserves the canonical logo's grey roses, kelly-green stems, white-blue cloud).
```

---

## br-003

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Standard garment — FLUX Pro best value (98% quality, 26% cost)
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1361c → +Layer-3=4173c → +Layer-2=1748c → final=7282c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Authentic-style baseball jersey — V-neck collar opening, button-front placket, short sleeves, straight even hem (no drop-tail). Solid BLACK base fabric. White piping/binding around V-neck collar, sleeve cuffs, and down both sides of the front placket. White buttons on the placket. NO player number on front. NO player number on back. NO player name on back. NO pinstripes. NOT a t-shirt. NOT a hoodie. NOT a basketball jersey. NOT a football jersey. Mid-weight knit jersey fabric. Solid black colorway (this is the Classic base; Oakland / Giants / White editions are separate SKUs br-003-oakland / br-003-giants / br-003-white).

BRANDING — exactly what to render:
> Logo art for "Black Rose logo" entries below is the canonical
> three-rose-cluster art at `data/brand-logos/black-rose-logo.md`.
> The "Authentic Collection patch" graphic is at
> `data/brand-logos/black-rose-authentic-collection-patch.md`.
> The "SR monogram" is the gold lettermark at
> `data/brand-logos/sr-monogram.md`.
> A reference techflat for the assembled product (front + back) is at
> `data/product-references/br-003-baseball-classic-techflat.jpeg`.

### Front
- **front-chest** (large, arched, ~9in wide): The phrase **"BLACK IS BEAUTIFUL"**
  as authentic tackle-twill lettering — pre-cut white fabric letters appliquéd
  onto the black jersey body in a baseball-script style with a subtle classic
  outline, arched across the upper-front-chest. **Technique:** tackle-twill.
  **Color:** white twill letters (no contrast satin-stitch edge — clean
  white-on-black).
- **front-left-hem / front-belly-lower-left** (~2in × 2.5in, near the bottom
  hem on the wearer's left hip): The Black Rose Authentic Collection patch —
  the rectangular yellow-and-white multi-element patch defined in the patch
  reference file (BLACK ROSE / MLB-style batter silhouette / AUTHENTIC banner /
  COLLECTION / red diamond divider / Members Only Yay Area Ca / SkyyRose
  Collection script / Made for Kings ang Queens). **Technique:**
  embroidered-patch (woven full-color patch sewn onto the jersey).

### Back
- **back-neck** (small, ~2in wide, top-center just below the collar yoke):
  The **SR monogram** (gold metallic art — see sr-monogram reference).
  Embroidered directly onto the jersey in gold-tone thread. **Technique:**
  embroidered. **Color:** gold-tone thread (preserves the gold-to-copper
  gradient from the canonical mark; NOT flat yellow, NOT silver).
- **back-center** (large, ~10in–12in tall, vertically centered between the
  yoke and the lower hem): The Black Rose logo (the canonical three-rose
  cluster on cloud — see logo_reference). Embroidered directly onto the jersey
  in **white thread on the black fabric**. The composition's shapes (three
  roses, stems, thorny vines, cloud) are preserved via the original art's
  outlines and inner detail; the multi-color palette is NOT preserved — this
  is a single-color white-thread embroidery rendering the silhouette and
  shape detail in white. **Technique:** embroidered. **Color:** white thread
  on black fabric.

### Sleeves / Collar / Hem / Other
- **collar / V-neck binding**: White contrast piping/binding around the
  V-neck collar opening (1/4in–3/8in wide). **Technique:** stitched.
  **Color:** white.
- **left-cuff / right-cuff binding**: White contrast piping around both
  sleeve cuff openings. **Technique:** stitched. **Color:** white.
- **front-placket binding**: White contrast piping running vertically down
  both sides of the front button placket. **Technique:** stitched. **Color:**
  white.
- **front-placket buttons** (~6 buttons, plain white, evenly spaced down the
  placket from the V-neck to the upper-belly). **Technique:** patch (sewn-on
  button hardware). **Color:** white.
- **collar-inside** (small, ~1.75in × 0.75in): Woven brand label sewn into
  the inside back of the collar. **Technique:** woven-label. **Color:**
  brand-label colors (typically black with brand-color accents).
  *(Standard apparel element — not visible in the flat techflat but expected.)*

---

Study the reference image carefully. This is a  called "BLACK is Beautiful Jersey Series: 0. Baseball Classic".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Deep matte black (#0A0A0A) backdrop with subtle charcoal gradient
- Cool silver key light from upper-left, black fill, thin silver rim light creating metallic edge highlights
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- NO player number on front-chest. NO player number on back-center. NO
  player number on sleeves. The "Black Is Beautiful" series carries no
  numbers at all on baseball jerseys.
- NO player name above the back-center logo.
- NO embossed or debossed decoration anywhere — branding is tackle-twill
  on the front, embroidered on the back, patch-sewn for the Authentic
  Collection mark.
- NO multi-color rendering of the back-center Black Rose logo — it is
  white-thread embroidery only. NO greyscale petals visible. NO kelly-green
  stems visible. NO white-and-blue cloud color visible — the cloud appears
  in white thread like the rest of the rose-cluster shape.
- NO Black Rose logo on the chest — the chest carries only the tackle-twill
  wordmark and the lower-left Authentic Collection patch.
- NO SR monogram on the back-center — the back-center carries the
  rose-cluster logo; the SR monogram is at the back-neck only.
- NO sleeve patches (no MLB patch, no NFL patch, no team patch on
  either sleeve in this Classic colorway).
- NO pinstripes on the body.
- NO contrast color other than white — no red, no gold, no orange anywhere
  on this Classic black colorway. (Red is the Giants; gold is the Oakland;
  white is the White edition — separate SKUs.)
- NO printed graphics or sublimated panels anywhere.
- NO heat-transfer vinyl.
- NO contrast-color satin-stitch edge around the tackle-twill letters
  (the letters are clean white-on-black with no red or gold border edge).
- NO logos at the hem on the right hip (only the lower-left has the
  Authentic Collection patch).
- NO chest-pocket or breast-pocket (this is a clean-front jersey — only
  the placket and tackle-twill wordmark).
```

---

## br-003-giants

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Standard garment — FLUX Pro best value (98% quality, 26% cost)
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1378c → +Layer-3=3397c → +Layer-2=1090c → final=5865c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Authentic-style baseball jersey — V-neck collar opening, button-front placket, short sleeves, straight even hem (no drop-tail). Solid BLACK base fabric with **bright orange** piping/binding around V-neck collar, sleeve cuffs, and down both sides of the front placket. **Black** buttons on the placket (matching the body, no contrast). NO player number on front. NO player number on back. NO player name on back. NO pinstripes. Mid-weight knit jersey. This is the GIANTS colorway (separate SKU from the Classic black-with-white-piping br-003).

BRANDING — exactly what to render:
> Logo art canonical references:
> - Black Rose three-rose-cluster: `data/brand-logos/black-rose-logo.md`
> - Authentic Collection patch:    `data/brand-logos/black-rose-authentic-collection-patch.md`
> - SR monogram:                   `data/brand-logos/sr-monogram.md`
> - Product techflat:              `data/product-references/br-003-giants-techflat.jpeg`
> - Real product photos:           `data/product-references/br-003-giants-real-front.jpeg`,
>                                  `data/product-references/br-003-giants-real-back.jpeg`

### Front
- **front-chest** (large, arched, ~9in wide): The phrase **"BLACK IS BEAUTIFUL"**
  as authentic tackle-twill lettering — pre-cut **bright orange** fabric letters
  appliquéd onto the black jersey body in a baseball-script style, arched across
  the upper-front-chest. **Technique:** tackle-twill. **Color:** bright orange
  twill (NO contrast satin-stitch edge — clean orange-on-black).
- **front-left-hem / front-belly-lower-left** (~2in × 2.5in): The Black Rose
  Authentic Collection patch (full multi-color: yellow field, navy text,
  white banner, red diamond divider, etc. — see patch reference). Sewn onto
  the lower-left hip. **Technique:** embroidered-patch.

### Back
- **back-neck** (small, ~2in wide): The SR monogram, embroidered directly
  onto the jersey in **orange-tone thread** (matching the colorway theme — the
  techflat and real product photo confirm an orange-toned rendering, distinct
  from the Classic's gold-tone). **Technique:** embroidered. **Color:** bright
  orange thread.
- **back-center** (~10in–12in tall): The Black Rose logo embroidered directly
  onto the jersey in **white thread on the black fabric** (same treatment as
  the Classic black colorway — single-color white-thread silhouette
  preserving the canonical art's shapes). **Technique:** embroidered.
  **Color:** white thread.

### Sleeves / Collar / Hem / Other
- **collar / V-neck binding**: Bright orange contrast piping/binding around
  the V-neck collar opening (1/4in–3/8in wide). **Technique:** stitched.
  **Color:** bright orange.
- **left-cuff / right-cuff binding**: Bright orange piping around both sleeve
  cuff openings. **Technique:** stitched. **Color:** bright orange.
- **front-placket binding**: Bright orange piping running vertically down both
  sides of the front button placket. **Technique:** stitched. **Color:**
  bright orange.
- **front-placket buttons** (~5–6 buttons, plain BLACK, evenly spaced):
  **Technique:** patch (sewn-on hardware). **Color:** black (NOT white).
- **collar-inside** (~1.75in × 0.75in): Woven brand label sewn into the
  inside back of the collar. **Technique:** woven-label.

---

Study the reference image carefully. This is a  called "BLACK is Beautiful Jersey Series: 0. Baseball Classic (Giants Edition)".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Deep matte black (#0A0A0A) backdrop with subtle charcoal gradient
- Cool silver key light from upper-left, black fill, thin silver rim light creating metallic edge highlights
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- NO player number, NO player name on front or back or sleeves.
- NO white piping (this colorway uses ORANGE piping — not white).
- NO white tackle-twill letters (the BIB wordmark is ORANGE — not white,
  not gold, not yellow).
- NO white buttons (this colorway uses BLACK buttons).
- NO gold-tone SR monogram (this colorway's monogram is in ORANGE thread —
  the gold version is on the Classic black br-003).
- NO multi-color back-rose embroidery — the back-center rose is white-thread
  silhouette only (NOT the canonical multi-color art).
- NO Black Rose logo on the chest — the chest carries only the tackle-twill
  wordmark and lower-left Authentic Collection patch.
- NO SR monogram on the back-center — back-center is the rose-cluster only.
- NO sleeve patches anywhere.
- NO pinstripes, NO embossed/debossed, NO sublimated panels, NO heat-transfer
  vinyl, NO printed graphics on the body.
- NO contrast colors other than orange — no green, no yellow, no red elsewhere.
- NO contrast satin-stitch edge around the tackle-twill letters.
```

---

## br-003-oakland

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Standard garment — FLUX Pro best value (98% quality, 26% cost)
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1379c → +Layer-3=3741c → +Layer-2=1296c → final=6416c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Authentic-style baseball jersey — V-neck collar opening, button-front placket, short sleeves, straight even hem (no drop-tail). Solid **dark forest green** base fabric with **gold/yellow** piping/binding around V-neck collar, sleeve cuffs, and down both sides of the front placket. Buttons match the body (green or yellow-tone, blending with the placket). NO player number on front or back. NO player name on back. NO pinstripes. Mid-weight knit jersey. This is the OAKLAND colorway (separate SKU from the Classic black br-003 / Giants br-003-giants / White br-003-white).

BRANDING — exactly what to render:
> Logo art canonical references:
> - Black Rose three-rose-cluster: `data/brand-logos/black-rose-logo.md`
> - Authentic Collection patch:    `data/brand-logos/black-rose-authentic-collection-patch.md`
> - SR monogram:                   `data/brand-logos/sr-monogram.md`
> - Product techflat:              `data/product-references/br-003-oakland-techflat.jpeg`

### Front
- **front-chest** (large, arched, ~9in wide): The phrase **"BLACK IS BEAUTIFUL"**
  as authentic tackle-twill lettering with a **gold satin-stitch edge**
  surrounding the letter faces. The contrast satin-stitch edge is integral
  to this colorway's look (vs. the Classic black which has no contrast edge).
  - **Letter faces — WHITE twill**, EXCEPT…
  - **The "A" in "BLACK" — BLACK twill** (the only black letter face, a
    deliberate stylistic accent that calls back to the Oakland Athletics'
    team-A identity).
  - **Satin-stitch edge — gold** around every letter (including the black A).
  - **Technique:** tackle-twill. **Color:** white twill faces (with one black
    "A") + gold satin-stitch edge.
- **front-left-hem / front-belly-lower-left** (~2in × 2.5in): The Black Rose
  Authentic Collection patch (full multi-color: yellow field, navy text,
  white banner, red diamond divider, etc. — see patch reference). Sewn onto
  the lower-left hip. **Technique:** embroidered-patch.

### Back
- **back-neck** (small, ~2in wide): The SR monogram, embroidered directly
  onto the jersey in **gold-tone thread** (matching the colorway theme — the
  SR mark renders in gold to match the gold satin-stitch edge and the gold
  piping). **Technique:** embroidered. **Color:** gold-tone thread.
- **back-center** (~10in–12in tall): The Black Rose logo embroidered directly
  onto the jersey. The roses, stems, and thorny vines are rendered in
  **white thread**; the cloud at the base of the cluster is rendered in
  **yellow/gold thread** (a colorway-specific accent — the cloud picks up
  the Oakland yellow palette while the rose-cluster stays white-thread).
  **Technique:** embroidered. **Color:** white thread on the rose-cluster +
  yellow/gold thread on the cloud at the base.

### Sleeves / Collar / Hem / Other
- **collar / V-neck binding**: Gold/yellow contrast piping/binding around the
  V-neck collar opening (1/4in–3/8in wide). **Technique:** stitched.
  **Color:** gold/yellow.
- **left-cuff / right-cuff binding**: Gold/yellow piping around both sleeve
  cuff openings. **Technique:** stitched. **Color:** gold/yellow.
- **front-placket binding**: Gold/yellow piping running vertically down both
  sides of the front button placket. **Technique:** stitched. **Color:**
  gold/yellow.
- **front-placket buttons** (~5–6 buttons, evenly spaced down the placket).
  **Technique:** patch (sewn-on hardware). **Color:** body-matching
  (green/yellow tone — blends with the placket).
- **collar-inside** (~1.75in × 0.75in): Woven brand label sewn into the
  inside back of the collar. **Technique:** woven-label.

---

Study the reference image carefully. This is a  called "BLACK is Beautiful Jersey Series: 0. Baseball Classic (Oakland Edition)".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Deep matte black (#0A0A0A) backdrop with subtle charcoal gradient
- Cool silver key light from upper-left, black fill, thin silver rim light creating metallic edge highlights
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- NO player number, NO player name on front, back, or sleeves.
- NO white piping (this colorway uses GOLD/YELLOW piping — not white).
- NO orange piping (that's the Giants colorway).
- NO black piping (that's the White edition).
- NO solid-yellow tackle-twill letters — letter FACES are WHITE (with one
  black "A"); only the satin-stitch EDGE is gold.
- NO uniform letter color — the "A" in "BLACK" is BLACK while every other
  letter is white. This is the colorway's signature detail.
- NO contrast satin edge OTHER than gold (no white edge, no red edge).
- NO gold thread on the rose-cluster — only the cloud is yellow/gold thread;
  the roses and stems are WHITE thread.
- NO multi-color rendering of the rose-cluster (kelly-green stems, etc.) —
  the cluster is white thread; the cloud is the only colorway accent in gold.
- NO orange or red anywhere on this colorway.
- NO Black Rose logo on the chest — the chest carries only the tackle-twill
  wordmark and the lower-left Authentic Collection patch.
- NO SR monogram on the back-center — that region is the rose-cluster only.
- NO sleeve patches anywhere on this jersey.
- NO pinstripes, NO embossed/debossed, NO sublimated panels, NO heat-transfer
  vinyl, NO printed graphics on the body.
```

---

## br-003-white

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Standard garment — FLUX Pro best value (98% quality, 26% cost)
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1377c → +Layer-3=3473c → +Layer-2=1341c → final=6191c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Authentic-style baseball jersey — V-neck collar opening, button-front placket, short sleeves, straight even hem (no drop-tail). Solid **white** base fabric with **black** piping/binding around V-neck collar, sleeve cuffs, and down both sides of the front placket. Black buttons on the placket. NO player number on front or back. NO player name on back. NO pinstripes. Mid-weight knit jersey. This is the WHITE colorway (separate SKU from Classic black br-003 / Giants br-003-giants / Oakland br-003-oakland).

BRANDING — exactly what to render:
> Logo art canonical references:
> - Black Rose three-rose-cluster: `data/brand-logos/black-rose-logo.md`
> - Authentic Collection patch:    `data/brand-logos/black-rose-authentic-collection-patch.md`
> - SR monogram:                   `data/brand-logos/sr-monogram.md`
> - Product techflat:              `data/product-references/br-003-white-techflat.jpeg`

### Front
- **front-chest** (large, arched, ~9in wide): The phrase **"BLACK IS BEAUTIFUL"**
  as authentic tackle-twill lettering — pre-cut **black** fabric letters
  appliquéd onto the white jersey body in a baseball-script style, arched
  across the upper-front-chest. **Technique:** tackle-twill. **Color:** black
  twill letters (the inverse colorway treatment of the Classic black; clean
  black-on-white with no contrast satin-stitch edge).
- **front-left-hem / front-belly-lower-left** (~2in × 2.5in): The Black Rose
  Authentic Collection patch (full multi-color — yellow field, navy text,
  white banner, red diamond divider, etc.). Sewn onto the lower-left hip.
  **Technique:** embroidered-patch.

### Back
- **back-neck** (small, ~2in wide): The SR monogram, embroidered directly
  onto the jersey in **black or dark-tone thread** (the gold-on-white would
  read poorly; the colorway uses black thread to maintain the high-contrast
  reading). **Technique:** embroidered. **Color:** black thread.
- **back-center** (~10in–12in tall): The Black Rose logo embroidered directly
  onto the jersey in **black thread on the white fabric** (the inverse
  treatment of the Classic black colorway's white-on-black). The composition's
  shapes (three roses, stems, thorny vines, cloud) are preserved via the
  original art's outlines and inner shading; on white background, the
  embroidered art may show greyscale shading more naturally — petals can
  carry darker fills, cloud renders lighter (grey-thread or stitch-density
  variation). **Technique:** embroidered. **Color:** primarily black thread
  with optional grey-thread shading on the cloud and lighter rose details.

### Sleeves / Collar / Hem / Other
- **collar / V-neck binding**: Black contrast piping/binding around the
  V-neck collar opening (1/4in–3/8in wide). **Technique:** stitched.
  **Color:** black.
- **left-cuff / right-cuff binding**: Black piping around both sleeve cuff
  openings. **Technique:** stitched. **Color:** black.
- **front-placket binding**: Black piping running vertically down both sides
  of the front button placket. **Technique:** stitched. **Color:** black.
- **front-placket buttons** (~5–6 buttons, plain BLACK or dark-tone, evenly
  spaced). **Technique:** patch (sewn-on hardware). **Color:** black.
- **collar-inside** (~1.75in × 0.75in): Woven brand label sewn into the
  inside back of the collar. **Technique:** woven-label.

---

Study the reference image carefully. This is a  called "BLACK is Beautiful Jersey Series: 0. Baseball Classic (White Edition)".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Deep matte black (#0A0A0A) backdrop with subtle charcoal gradient
- Cool silver key light from upper-left, black fill, thin silver rim light creating metallic edge highlights
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- NO player number, NO player name on front, back, or sleeves.
- NO white piping (this colorway uses BLACK piping — not white).
- NO orange piping (that's the Giants colorway).
- NO gold/yellow piping (that's the Oakland colorway).
- NO white tackle-twill letters (the BIB wordmark is BLACK on white — the
  inverse of the Classic colorway).
- NO white buttons (this colorway uses black buttons).
- NO gold-tone SR monogram (this colorway's monogram is in BLACK thread).
- NO Black Rose logo on the chest — the chest carries only the tackle-twill
  wordmark and the lower-left Authentic Collection patch.
- NO SR monogram on the back-center — back-center is the rose-cluster only.
- NO sleeve patches anywhere.
- NO contrast colors other than black on this colorway — no orange, no
  yellow, no red elsewhere on the body fabric.
- NO multi-color (kelly-green / blue / yellow) rendering of the back rose;
  this is a black-thread embroidery (with optional grey shading).
- NO contrast satin-stitch edge around the tackle-twill letters.
- NO pinstripes, NO embossed/debossed, NO sublimated panels, NO heat-transfer
  vinyl, NO printed graphics on the body.
- NO special "A" treatment (the colorway-specific black-A is Oakland's
  signature; on the White edition every letter is uniformly black).
```

---

## br-004

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Standard garment — FLUX Pro best value (98% quality, 26% cost)
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1325c → +Layer-3=2491c → +Layer-2=1230c → final=5046c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Black pullover hoodie — long sleeves, drawstring hood, kangaroo front pocket, ribbed cuffs at the wrists, ribbed waist hem at the bottom (all tonal black, no contrast white trim — distinct from the matching Black Rose Crewneck/Joggers set which use white ribbing). NOT a zip-up. NOT a half-zip. NOT a crewneck. NOT a t-shirt. Heavyweight cotton fleece.

BRANDING — exactly what to render:
> Logo art canonical reference:
> - Black Rose three-rose-cluster: `data/brand-logos/black-rose-logo.md`
> - Reference photo:                `data/product-references/br-004-hoodie-real-front.jpeg`

### Front
- **front-chest** (~5–6in tall, centered just above the kangaroo pocket):
  The Black Rose logo embroidered onto the hoodie. **Technique:**
  embroidered. **Color:** as rendered in the canonical logo + reference
  image (do NOT over-specify thread colorway in this dossier — the RAS
  pipeline reads the canonical logo art and the product reference photo
  for the thread treatment).

### Back
- (No decoration. Completely clean back. NO SR monogram on back-neck. NO
  rose on back-center. NO logos anywhere on the back.)

### Sleeves / Collar / Hem / Other
- **left-hip** (left side of the body, exact dimensions TBD): A small
  patch sits at the left hip / left side of the body. It is NOT on the
  sleeve (founder-confirmed 2026-09-21).
  Patch content, technique, and dimensions are **PARKED for later
  verification** — Corey will confirm the patch detail in a follow-up
  read-back. **Do not render this region with guessed content** —
  the RAS pipeline should treat the left-hip area as "small patch
  present, content unverified" and prompt for the verification before
  rendering this region in production.
- **left-sleeve**: clean, no decoration.
- **right-sleeve**: clean, no decoration.
- **kangaroo-pocket** (front): clean, no embroidery, no logo, no
  decoration on the pocket itself.
- **hood-drawstring**: tonal black flat drawstring (matches the body —
  NOT contrast-color white, NOT contrast-color rose-gold). Plain tips,
  no metal, no branded tip.
- **collar-inside / interior-back-collar** (~1.75in × 0.75in): Branded
  woven size tag (universal SkyyRose product rule — every product carries
  a branded woven size tag at this position). Shows the SKU's size
  designation. **Technique:** woven-label. **Color:** brand-standard
  (typically black with brand-color accents and white/printed size text).

---

Study the reference image carefully. This is a  called "BLACK Rose Hoodie".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Deep matte black (#0A0A0A) backdrop with subtle charcoal gradient
- Cool silver key light from upper-left, black fill, thin silver rim light creating metallic edge highlights
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- NO rose on the back. NO SR monogram on the back. The back is COMPLETELY
  clean black fabric.
- NO white ribbed trim on cuffs, hem, or hood — the Black Rose Hoodie
  uses TONAL BLACK ribbing throughout (the white ribbing is the
  Crewneck/Joggers signature, not the Hoodie).
- NO contrast-color drawstrings — they are tonal black, not white,
  not rose-gold, not gold.
- NO Black Rose logo on the back. NO Black Rose logo on the sleeves. NO
  Black Rose logo on the kangaroo pocket. The rose appears at the
  front-chest only.
- NO silicone-appliqué patch on the chest or anywhere else.
- NO embossed/debossed decoration on the body or hood.
- NO printed graphics, NO sublimated panels, NO heat-transfer vinyl,
  NO puff-print decoration.
- NO front-pocket branding — the kangaroo pocket fabric is clean.
- NO sleeve patch on either sleeve (the small patch is at the left hip /
  left side of the body, NOT the sleeve).
- NO contrasting hood lining (assume same black tonal — to be verified
  if a contrast lining exists, but default is uniform black).
- NO chest text or wordmark (the front rose is the only chest decoration).
- NO Authentic Collection patch (that patch is reserved for the jersey
  series, not the hoodie).
```

---

## br-005

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Standard garment — FLUX Pro best value (98% quality, 26% cost)
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1345c → +Layer-3=2901c → +Layer-2=1546c → final=5792c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Black PULLOVER hoodie — long sleeves, drawstring hood, kangaroo front pocket, ribbed cuffs at the wrists, ribbed waist hem at the bottom (tonal black ribbing, no contrast white trim). Constructed from a **lightweight polyester / jogger-feel fabric** (NOT heavyweight cotton fleece — distinct from the basic Black Rose Hoodie br-004 which is heavier cotton). NOT a zip-up. NOT a half-zip. NOT a crewneck. The "Signature Edition" identity comes from the elevated branding placement (chest + hip), the white drawstrings, and the sublimated-rose-print inner hood lining.

BRANDING — exactly what to render:
> Logo art canonical reference:
> - Black Rose three-rose-cluster: `data/brand-logos/black-rose-logo.md`
> - Reference photo:                `data/product-references/br-005-signature-hoodie-real.jpeg`

### Front
- **front-right-chest** (small, ~2–3in tall): The Black Rose logo as a
  **silicone cut-out patch** — silicone applied to the fabric in the
  shape of the canonical three-rose-cluster art (cut-out silicone shape
  rather than full-color silicone-appliqué). Tonal/monochrome treatment
  per the reference photo. **Technique:** silicone. **Color:** as rendered
  in the canonical logo + reference image (white/grey tonal).

### Back
- (No back-neck SR monogram, no back-center logo confirmed in this read-back —
  back details to be verified if Corey provides a back reference photo. Default:
  treat the back as clean unless confirmed otherwise.)

### Sleeves / Collar / Hem / Other
- **left-hip / left-side-body** (large, ~6–7in tall, on the wearer's
  LEFT side at the hip / lower-side-body area, NOT on the sleeve): The
  Black Rose logo embroidered onto the side of the hoodie body. Position
  is explicitly the side body at hip level — Corey emphasized "NOT
  SLEEVE." **Technique:** embroidered. **Color:** as rendered in the
  canonical logo + reference image.
- **hood-inside / inner-hood-lining**: GREY contrast lining inside the
  hood with the **Black Rose logo sublimated throughout** as a repeating /
  scattered pattern (the canonical three-rose-cluster art appears
  multiple times across the lining fabric, faded/tonal style consistent
  with sublimation dye). Visible only when the hood is laid open or worn
  down. **Technique:** sublimated. **Color:** light tonal print on grey
  lining fabric.
- **hood-drawstring**: WHITE flat drawstring threaded through the hood
  (contrast against the black body fabric). Plain tips, no metal,
  no branded tip. **Technique:** stitched. **Color:** white.
- **kangaroo-pocket** (front): clean, no embroidery, no logo on the
  pocket fabric.
- **collar-inside / interior-back-collar** (~1.75in × 0.75in): Branded
  woven size tag (universal SkyyRose product rule). **Technique:**
  woven-label.

---

Study the reference image carefully. This is a  called "BLACK Rose Hoodie — Signature Edition".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Deep matte black (#0A0A0A) backdrop with subtle charcoal gradient
- Cool silver key light from upper-left, black fill, thin silver rim light creating metallic edge highlights
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- NO logo on the LEFT chest — the silicone patch is at the right-chest
  position only.
- NO embroidered logo on either sleeve. Corey's explicit instruction:
  the side-body logo is NOT on the sleeve, it is on the BODY at the
  side-hip area.
- NO Black Rose logo on the right hip — the embroidered side-body logo
  is on the LEFT side at the hip, not the right.
- NO black drawstrings — the drawstrings are WHITE (signature detail of
  this edition).
- NO silicone-appliqué multi-color patch — the right-chest silicone is
  a tonal cut-out, not a full multi-color appliqué.
- NO printed graphics on the body fabric (the rose-pattern sublimation
  is on the INNER HOOD LINING only, not on the body fabric, sleeves, or
  pocket).
- NO sublimated Black Rose pattern on the body, sleeves, or pocket —
  only the inner hood lining carries the sublimated rose pattern.
- NO contrasting hem or cuff trim — the rib trim is tonal black on this
  edition.
- NO white ribbed hem or cuffs (those are br-001 Crewneck / br-002
  Joggers signature details, not the Signature Hoodie).
- NO Authentic Collection patch (that patch is reserved for the jersey
  series).
- NO embossed/debossed decoration on the body or hood fabric.
- NO chest text or wordmark on the front body fabric — branding is the
  silicone right-chest mark + the embroidered left-side body mark only.
- NO heavyweight cotton fleece texture — this hoodie is the lighter
  polyester / jogger-feel variant (distinct from br-004's cotton fleece).
```

---

## br-006

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Standard garment — FLUX Pro best value (98% quality, 26% cost)
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1332c → +Layer-3=4086c → +Layer-2=1687c → final=7105c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Black satin bomber-style hooded jacket — **lustrous black satin** exterior fabric, **plush black sherpa** interior lining (visible inside the body and inside the hood). Hooded (sherpa-lined hood). **Front closure is a ZIPPER underneath with a button-overlap storm-flap covering it** — the zipper runs the full center-front length, and a buttoned/snapped storm flap overlaps the zipper line for a clean satin front (this is a two-layer placket). **Side hand pockets with zipper closures** at the lower sides. Long sleeves with **black ribbed cuffs**. **Black ribbed bomber-style waistband** at the bottom hem. NOT a parka. NOT a denim jacket. NOT a fleece hoodie. NOT a windbreaker. NOT a leather jacket.

BRANDING — exactly what to render:
> Logo art canonical reference:
> - Black Rose three-rose-cluster: `data/brand-logos/black-rose-logo.md`
> - Reference photos:               `data/product-references/br-006-sherpa-jacket-real-front.jpeg`,
>                                   `data/product-references/br-006-sherpa-jacket-real-open.jpeg`,
>                                   `data/product-references/br-006-sherpa-jacket-real-closeup.jpeg`

### Front
- **front-left-chest** (small, ~3–4in tall): The Black Rose logo embroidered
  directly onto the satin. The full canonical art (three-rose cluster on
  cloud) is rendered in white-thread embroidery on the black satin fabric.
  **Technique:** embroidered. **Color:** as rendered in the canonical logo +
  reference image (white-thread silhouette preserving the canonical art's
  shape detail).

### Back
- **back-center** (~10in tall): The Black Rose logo embroidered directly
  onto the back of the jacket, centered on the back panel. Significantly
  larger than the front-left-chest mark — this is the signature
  back-piece of the jacket. **Technique:** embroidered. **Color:** as
  rendered in the canonical logo + reference image.

### Sleeves / Collar / Hem / Other
- **front-placket-zipper** (full center-front length): Black zipper
  running the entire length of the center-front from the V-opening at
  the collar down to the bottom of the ribbed waistband. The primary
  closure. **Technique:** patch (sewn-on hardware — zipper teeth).
  **Color:** black zipper teeth.
- **front-placket-storm-flap** (covering the zipper line): A black
  satin storm flap overlaps the zipper line, secured with **buttons /
  snaps** down the placket. The buttoned overlap creates a clean
  uninterrupted satin front when fully closed (the zipper is hidden
  underneath the flap). **Technique:** patch (sewn-on snap/button
  hardware). **Color:** black snaps/buttons on black satin.
- **front-placket-drawstring**: A flat black drawstring threaded down
  the inside of the placket area, hanging visibly from inside the hood
  toward the chest. **Technique:** stitched. **Color:** black.
- **side-hand-pockets** (left and right, lower-side): Slash-style hand
  pockets with **zipper closures** at the openings. **Technique:**
  patch (sewn-on hardware — zipper teeth). **Color:** black zipper teeth.
- **left-cuff / right-cuff**: Black ribbed-knit cuffs at the wrists
  (tonal black, contrasting with the satin sleeves). **Technique:**
  stitched. **Color:** black.
- **hem / waistband**: Black ribbed-knit bomber-style waistband at the
  bottom of the jacket. **Technique:** stitched. **Color:** black.
- **hood-inside / inner-hood-lining**: Black sherpa lining inside the
  hood (plush textured fabric, distinct from the satin exterior).
  **Technique:** stitched. **Color:** black sherpa.
- **body-inside / inner-body-lining**: Black sherpa lining inside the
  body of the jacket (visible when the front placket is open).
  **Technique:** stitched. **Color:** black sherpa.
- **collar-inside / interior-back-collar** (small woven label): Branded
  woven size tag (universal SkyyRose product rule). Visible as a small
  white-and-brand-color tag in the reference photos. **Technique:**
  woven-label.

---

Study the reference image carefully. This is a  called "BLACK Rose Sherpa Jacket".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Deep matte black (#0A0A0A) backdrop with subtle charcoal gradient
- Cool silver key light from upper-left, black fill, thin silver rim light creating metallic edge highlights
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- NO Black Rose logo on the front-RIGHT chest — the chest mark is on
  the wearer's LEFT only (per CSV: "Embroidered rose logo on left chest").
- NO Black Rose logo on the sleeves.
- NO snap-only front closure — the front IS a zipper underneath, with
  a buttoned/snapped storm flap overlapping it (NOT a snap-only design;
  NOT a zipper-only exposed-teeth design — the zipper is hidden under
  the snap-buttoned satin storm flap).
- NO SR monogram on the back-neck — there is NO back-neck logo of any
  kind on this jacket (distinct from the crewneck / jerseys which carry
  a back-neck SR monogram).
- NO logos on the back-yoke or upper back — the rose is centered on
  the mid-back panel only.
- NO contrast-color piping on the sleeves, body, or hood.
- NO white drawstrings — the placket-area drawstring is BLACK.
- NO white ribbed trim at cuffs or waistband — they are tonal black.
- NO fleece, NO cotton-fleece body fabric — this jacket is black SATIN
  with a sherpa interior, NOT cotton fleece.
- NO hood without sherpa lining — the hood interior IS sherpa-lined.
- NO Black Rose logo on the back-neck region between the hood and the
  back panel — the back rose is at back-center (mid-back), not at the
  back-neck.
- NO multi-color rendering of either rose — the canonical art is
  rendered in white-thread embroidery on the black satin.
- NO Authentic Collection patch (that patch is reserved for the jersey series).
- NO embossed/debossed decoration anywhere.
- NO printed graphics, NO sublimated panels (the inner hood lining is
  PLAIN black sherpa for this jacket — distinct from br-005's grey
  sublimated-rose inner hood).
```

---

## br-007

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Standard garment — FLUX Pro best value (98% quality, 26% cost)
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1349c → +Layer-3=6385c → +Layer-2=2294c → final=10028c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Knee-length (or just-above-knee) athletic basketball shorts — black mesh main body with white mesh side panels, white elasticated waistband with white drawstring, **two side hand pockets** (left and right — both with zipper closures) and **one back pocket** (also with zipper closure) — three zip pockets total. Black ribbed-binding hem with white contrast piping. Cross-collection collab combining Black Rose and Love Hurts visual systems on a single garment. NOT pants. NOT joggers. NOT short-shorts. NOT a swim trunk. NOT a track short.

BRANDING — exactly what to render:
> Logo art canonical references:
> - Black Rose three-rose-cluster: `data/brand-logos/black-rose-logo.md`
> - Love Hurts (wordmark + broken-heart-and-thorns lockup): `data/brand-logos/love-hurts-logo.md`
> - Reference photos: `data/product-references/br-007-shorts-real-front.jpeg`,
>                     `data/product-references/br-007-shorts-real-back.jpeg`,
>                     `data/product-references/br-007-shorts-techflat.jpeg`
>
> ### COLORWAY OVERRIDE — read this BEFORE rendering
>
> **Every logo on this product is converted to the shorts' tonal colorway
> — black, grey, white, and cream/peach.** The canonical reds (Love Hurts
> wordmark, red-roses-cluster), kelly-greens (stems), and white-and-blue
> clouds are ALL replaced with greyscale / cream tonal renderings on this
> garment. The cross-collection collab is signaled by *placement and
> wordmark*, not by the brands' canonical colors. When the RAS prompt
> attaches the canonical Love Hurts logo image and the canonical Black
> Rose logo image as references, the model must use them ONLY for shape
> / composition guidance — colors are remapped to the tonal palette
> below.
>
> Tonal palette for this product:
> - Body fabric: black mesh
> - Side panels: white mesh
> - Sublimated patterns: tonal grey on black
> - Embroidered logos: tonal grey / cream / dark grey on white mesh
> - Tackle-twill: white face with dark satin-stitch edge
> - Wordmark colors: cream / peach / light-pink (NOT red)
> - Back-center pentagon panel logo: dark grey on white

### Front
- **front-body** (entire black mesh field): The Black Rose three-rose-cluster
  art **sublimated as a small repeating pattern across the entire black mesh
  body fabric** — small tonal grey rose silhouettes scattered across the
  mesh like an all-over print. Subtle (almost camo-like) on black ground,
  visible in close-up but reads as textured field at distance. **Technique:**
  sublimated. **Color:** tonal grey on black mesh.
- **front-thigh-center** (large, arched, ~6–7in wide): The wordmark
  **"OAKLAND"** as authentic tackle-twill — pre-cut white twill letters
  appliquéd onto the body in classic baseball-script style with a contrast
  satin-stitch edge. **Technique:** tackle-twill. **Color:** white twill
  letter face with a dark satin-stitch edge.
- **front-right-thigh** (cursive script overlapping the OAKLAND wordmark):
  The "Love Hurts" wordmark in cursive script, rendered as a large
  sublimated/printed wordmark in **cream/peach/pink tonal color** on the
  black mesh. Spans the right thigh area, reading top-to-bottom as the
  cursive lettering descends. **Technique:** sublimated. **Color:**
  cream/peach/light-pink tonal.
- **left-mesh-side-panel** (small, on the white mesh side panel):
  The Black Rose three-rose-cluster art (canonical *shape* — three roses,
  thorny vines, cloud at base) stitched onto the white mesh **in tonal
  grey / dark thread only** (NOT canonical multi-color — this product
  remaps every logo into the tonal grey/white/cream palette per the
  COLORWAY OVERRIDE above). The cluster is recognizable by composition
  but NOT by color. **Technique:** embroidered. **Color:** tonal
  grey/dark thread on white mesh (no kelly-green stems, no white-and-
  blue cloud).
- **right-mesh-side-panel** (small, on the white mesh side panel):
  The "Love Hurts" wordmark (cursive script only — no broken heart in
  this position) stitched onto the white mesh. **Technique:** embroidered.
  **Color:** dark/contrast thread on white mesh.

### Back
- **back-body** (entire black mesh field): Same sublimated tonal grey
  rose-cluster pattern as the front-body (continuous across the garment).
  **Technique:** sublimated. **Color:** tonal grey on black mesh.
- **back-upper / back-yoke** (large cursive across the upper back):
  The "Love Hurts" wordmark in cursive script, rendered larger than the
  front-right version, in **cream/peach/light-pink tonal color** sublimated
  onto the back mesh. **Technique:** sublimated. **Color:** cream/peach/
  light-pink tonal.
- **back-center-lower** (pentagon-shaped white panel insert, ~6–7in across):
  A **white pentagon-star-shaped contrast fabric panel** sewn into the
  lower-back-center between the two leg openings. Inside the panel:
  the Love Hurts full lockup (broken-heart-and-thorns + "Love Hurts"
  wordmark — see logo_reference) printed/embroidered in dark grey on
  the white panel. **Technique:** patch (pentagonal contrast fabric) +
  embroidered (Love Hurts logo on the panel). **Color:** white panel +
  dark grey logo art.

### Sleeves / Collar / Hem / Other
- **waistband-rib**: White elasticated waistband at the top.
  **Technique:** stitched. **Color:** white.
- **drawstring**: White flat drawstring threaded through the waistband.
  **Technique:** stitched. **Color:** white.
- **left-side-pocket / right-side-pocket** (front-side hand pockets):
  Vertical hand pockets at both sides, **with zipper closures**.
  **Technique:** patch (sewn-on zipper hardware). **Color:** black
  zipper teeth (with white piping at the pocket edge).
- **back-pocket** (single, centered upper-back, with zipper):
  One zippered back pocket — visible as a horizontal welt opening
  with white piping at the welt edges. **Technique:** patch (sewn-on
  zipper hardware). **Color:** black zipper teeth (with white piping
  at the welt edges).
- **hem / leg-binding**: Black ribbed-knit binding at the leg openings
  with a thin white contrast piping accent. **Technique:** stitched.
  **Color:** black with white piping.
- **inside-waistband** (~1in × 0.5in): Branded woven size tag (universal
  SkyyRose product rule). **Technique:** woven-label.

---

Study the reference image carefully. This is a  called "BLACK Rose x Love Hurts Basketball Shorts".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Deep matte black (#0A0A0A) backdrop with subtle charcoal gradient
- Cool silver key light from upper-left, black fill, thin silver rim light creating metallic edge highlights
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- **NO canonical-color rendering of any logo on this garment.** Every
  logo on these shorts is converted to the shorts' tonal palette
  (black/grey/white/cream/peach). Specifically:
  - NO red roses anywhere — the body sublimation is the Black Rose
    three-rose-cluster in tonal grey-on-black, NOT the canonical
    multi-color or Love Hurts red-roses variant.
  - NO kelly-green stems on the left mesh side panel cluster — the
    embroidered cluster is rendered in tonal grey/dark thread only.
  - NO white-and-blue cloud color on any rose-cluster — clouds remap
    to plain white or tonal grey on this product.
  - NO bright red Love Hurts wordmark — the cursive script is rendered
    in cream/peach/light-pink tonal, NOT the canonical saturated red.
  - NO bright red broken-heart-and-thorns lockup on the back-center
    pentagon — the Love Hurts logo on the panel is rendered in dark
    grey on white, NOT in canonical red and brown vines.
- NO Black Rose three-rose-cluster on the right mesh side panel — the
  right side carries the Love Hurts wordmark only.
- NO Love Hurts wordmark on the left mesh side panel — the left side
  carries the Black Rose cluster only.
- NO multi-color rendering of the body sublimated rose pattern — it is
  tonal grey-on-black, NOT the full multi-color art.
- NO Black Rose logo at front-thigh-center — the front center carries
  the OAKLAND tackle-twill wordmark, not a rose.
- NO solid-color body — the body fabric carries the sublimated rose
  pattern (NOT a plain black field).
- NO front pockets visible from outside — the visible pockets are on
  the BACK only; the front is uninterrupted by pocket openings.
- NO black drawstrings — the drawstring is white.
- NO black waistband — the waistband is white.
- NO contrast satin-stitch edge other than dark on the OAKLAND letters.
- NO numbers anywhere — no player number, no jersey-style numerals.
- NO sleeve elements (this is a shorts garment, lower-body only — no
  upper-body decoration of any kind).
- NO Authentic Collection patch (that is reserved for the jersey series).
- NO sublimated pattern on the white mesh side panels — the side panels
  are clean white mesh with only the embroidered cluster (left) and
  wordmark (right) on top.
```

---

## br-008

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Standard garment — FLUX Pro best value (98% quality, 26% cost)
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1367c → +Layer-3=3867c → +Layer-2=1646c → final=6880c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Authentic-style football jersey — V-neck collar opening
with **black-and-white horizontal striped neckband**, short sleeves with a
**white triple-stripe band (three thin horizontal white stripes)** at each
cuff, straight even hem (no drop-tail), no laces, no shoulder-armor seam.
Solid **bright red** base fabric (San Francisco red colorway). Mid-weight
knit jersey fabric. Pullover construction — NO buttons, NO front placket. NOT
a t-shirt. NOT a hoodie. NOT a basketball tank. NOT a baseball jersey.
**PRE-ORDER product** — design renderings only; no real-product photography
exists yet.

BRANDING — exactly what to render:
> Logo art canonical references:
> - Black Rose three-rose-cluster: `data/brand-logos/black-rose-logo.md`
> - NFL Authentic Collection patch: `data/brand-logos/nfl-authentic-collection-patch.md`
> - Product design render:          `data/product-references/br-008-design-front.jpeg`
>
> ### COLORWAY OVERRIDE — read this BEFORE rendering
>
> The number-fill rose-cluster art is rendered in **tonal greyscale only**
> (black + white + grey shading + black ink outlines), NOT canonical
> multi-color. The cluster is recognizable by composition (three roses,
> thorny vines, cloud at base) but renders in greyscale-on-red so it reads
> cleanly inside the white-outlined number forms. NO red roses, NO kelly-green
> stems, NO white-and-blue clouds.

### Front
- **front-chest** (large, ~10in tall, vertically centered between the
  neckband and the lower belly): The number **"80"** rendered as
  large athletic-block digits — each digit has a **white outline edge** with
  the canonical Black Rose three-rose-cluster art (in tonal greyscale)
  filling the interior of both the "8" and the "0". The rose composition is
  preserved (three roses + thorny vines + cloud at base) but rendered in
  black/white/grey only. **Technique:** sublimated. **Color:** white outline
  + greyscale rose-cluster fill on red ground.
- **front-left-hem / front-belly-lower-left** (~2in × 2.5in, near the bottom
  hem on the wearer's left hip): The NFL Authentic Collection patch (yellow
  field + navy "BLACK ROSE / COLLECTION" + NFL shield + white "AUTHENTIC"
  banner + red diamond divider + greyscale rose-cluster + "Property Of /
  Black Is Beautiful Series / Skyy Rose Co" footer — see patch reference).
  Sewn onto the lower-left hip. **Technique:** embroidered-patch.

### Back
- **back-yoke / upper-back** (across the upper-back, arched, ~9–10in wide):
  The phrase **"BLACK IS BEAUTIFUL"** as authentic tackle-twill lettering,
  baseball-script style with subtle outlines, arched across the upper-back.
  Rendered in **black twill** on the red body. **Technique:** tackle-twill.
  **Color:** black twill letters on red ground (no contrast satin-stitch edge).
- **back-center** (large, ~12in tall, vertically centered between the
  upper-back wordmark and the lower hem): The number **"80"** rendered
  identically to the front — white outline + greyscale rose-cluster fill.
  **Technique:** sublimated. **Color:** white outline + greyscale
  rose-cluster fill.

### Sleeves / Collar / Hem / Other
- **collar / V-neck binding**: Black-and-white horizontal striped neckband
  (a ribbed band with alternating black and white stripes, ~1in wide). The V
  opening is shaped within this striped band. **Technique:** stitched.
  **Color:** alternating black + white.
- **left-cuff / right-cuff binding**: White triple-stripe (three thin
  horizontal white stripes spaced evenly) on each short sleeve cuff against
  the red body fabric. **Technique:** stitched. **Color:** white stripes on
  red.
- **collar-inside** (~1.75in × 0.75in): Branded woven size tag (universal
  SkyyRose product rule). **Technique:** woven-label.

---

Study the reference image carefully. This is a  called "BLACK is Beautiful Jersey Series: 1. SF Inspired (Football)".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Deep matte black (#0A0A0A) backdrop with subtle charcoal gradient
- Cool silver key light from upper-left, black fill, thin silver rim light creating metallic edge highlights
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- NO player NAME on back. NO last name. NO first name. NO nameplate above
  the back-center number — the upper back carries ONLY the "BLACK IS
  BEAUTIFUL" wordmark.
- NO numbers on sleeves — the sleeves are clean (only the white triple-stripe
  cuff treatment, no shoulder digit, no sleeve number).
- NO multi-color rendering of the rose-cluster fill inside the "80" — it is
  greyscale only. NO red roses, NO kelly-green stems, NO white-and-blue
  cloud color.
- NO solid-color "80" digits — the digits are NOT solid white; they have
  a white outline edge with rose-cluster art FILLING the interior.
- NO contrast satin-stitch edge around the "BLACK IS BEAUTIFUL" wordmark —
  it is clean black-twill-on-red.
- NO buttons, NO placket, NO V-neck contrast piping other than the striped
  neckband — this is a pullover construction.
- NO MLB Authentic Collection patch (that's the baseball series). NO NBA
  Authentic Collection patch. NO Hockey Championship patch — football only.
- NO embossed/debossed decoration anywhere.
- NO heat-transfer vinyl on the body.
- NO SR monogram on the back-neck — this colorway has no separate back-neck
  embroidered mark.
- NO standalone Black Rose rose-cluster on the back-center other than as
  digit fill — the rose-cluster appears ONLY inside the "80" digits, not as
  a separate composition.
- NO sleeve patches (no shoulder NFL patch, no league patch on the
  shoulders).
- NO sublimated panels other than the rose-fill inside the digits and the
  cuff stripes.
- NO pinstripes anywhere on the body.
- NO snap-front, NO zipper-front (this is a pullover).
```

---

## br-009

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Standard garment — FLUX Pro best value (98% quality, 26% cost)
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1368c → +Layer-3=3536c → +Layer-2=1031c → final=5935c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Authentic-style football jersey — V-neck collar opening
with **solid black neckband** (contrast against the white body), short sleeves
with a **black-and-white horizontal striped cuff band** at each cuff, straight
even hem. Solid **white** base fabric (Last Oakland Raiders-inspired road/away
colorway). Mid-weight knit jersey fabric. Pullover construction — NO buttons,
NO front placket. NOT a t-shirt. NOT a hoodie. NOT a basketball tank. NOT a
baseball jersey. **PRE-ORDER product** — design renderings only.

BRANDING — exactly what to render:
> Logo art canonical references:
> - Black Rose three-rose-cluster: `data/brand-logos/black-rose-logo.md`
> - NFL Authentic Collection patch: `data/brand-logos/nfl-authentic-collection-patch.md`
> - SR monogram (back-neck):       `data/brand-logos/sr-monogram.md`
> - Product design render:          `data/product-references/br-009-design-front.jpeg`
>
> ### COLORWAY OVERRIDE — read this BEFORE rendering
>
> The number-fill rose-cluster art is rendered in **tonal greyscale only**
> (black + white + grey shading + black ink outlines), NOT canonical
> multi-color. The SR monogram is rendered in **black thread** on this
> colorway (NOT canonical gold) — black-on-white reads cleanly where
> gold-on-white would not. NO red roses, NO kelly-green stems, NO
> white-and-blue cloud color.

### Front
- **front-chest** (large, ~10in tall, vertically centered): The number
  **"32"** rendered as athletic-block digits with a **black outline edge**
  and greyscale Black Rose three-rose-cluster art filling the interior of
  both digits. **Technique:** sublimated. **Color:** black outline +
  greyscale rose-cluster fill on white ground.
- **front-left-hem / front-belly-lower-left** (~2in × 2.5in): The NFL
  Authentic Collection patch sewn onto the lower-left hip. **Technique:**
  embroidered-patch.

### Back
- **back-neck** (small, ~2in wide, top-center just below the collar yoke):
  The SR monogram embroidered directly onto the jersey in **black thread**
  (instead of canonical gold — black-on-white for this colorway).
  **Technique:** embroidered. **Color:** black thread.
- **back-yoke / upper-back** (arched, ~9in wide): The phrase **"BLACK IS
  BEAUTIFUL"** in tackle-twill lettering, baseball-script style. Rendered in
  **black twill** on the white body. **Technique:** tackle-twill. **Color:**
  black twill letters on white ground.
- **back-center** (large, ~12in tall, vertically centered): The number
  **"32"** rendered identically to the front. **Technique:** sublimated.
  **Color:** black outline + greyscale rose-cluster fill.

### Sleeves
- **left-shoulder / right-shoulder** (small, ~3–4in tall, on each shoulder):
  A smaller version of the same "32" digit composition (greyscale rose-cluster
  fill with black outline) on each shoulder/sleeve area. **Technique:**
  sublimated. **Color:** black outline + greyscale rose-cluster fill.

### Collar / Hem / Other
- **collar / V-neck binding**: Solid black neckband (~1in wide). **Technique:**
  stitched. **Color:** black.
- **left-cuff / right-cuff binding**: Black-and-white horizontal striped band
  at each short sleeve cuff (alternating black and white stripes, ~1in tall
  total). **Technique:** stitched. **Color:** alternating black + white.
- **collar-inside** (~1.75in × 0.75in): Branded woven size tag (universal
  SkyyRose product rule). **Technique:** woven-label.

---

Study the reference image carefully. This is a  called "BLACK is Beautiful Jersey Series: 2. Last Oakland (Football)".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Deep matte black (#0A0A0A) backdrop with subtle charcoal gradient
- Cool silver key light from upper-left, black fill, thin silver rim light creating metallic edge highlights
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- NO player NAME on back. NO nameplate above the back number.
- NO multi-color rendering of the rose-cluster fill — greyscale only.
- NO red anywhere on this colorway (this is the Last Oakland white away —
  NO 49ers red, NO Giants orange).
- NO solid-color "32" digits — the digits have black outline + rose fill.
- NO MLB Authentic Collection patch (baseball series only).
- NO Hockey Championship patch.
- NO NBA Authentic Collection patch.
- NO embossed/debossed decoration.
- NO buttons, NO placket — pullover construction.
- NO standalone Black Rose three-rose-cluster art on the back-center other
  than as digit fill — the rose appears ONLY inside the digit fills.
- NO gold thread on the SR monogram — black thread for this colorway.
- NO sleeve PATCHES — the sleeves carry duplicate "32" numerals, not woven
  patches.
- NO printed graphics other than the rose-fill inside digits and the sleeve
  number duplicates.
- NO pinstripes.
- NO snap-front or zipper-front closure.
```

---

## br-010

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Standard garment — FLUX Pro best value (98% quality, 26% cost)
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1365c → +Layer-3=3809c → +Layer-2=1116c → final=6290c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Authentic-style basketball tank — sleeveless, round
neck with thin contrast binding, deep armhole openings (basketball-cut),
straight even hem. **White base body fabric with a sublimated all-over
rose-cluster pattern fading from clean white at the upper-chest into greyscale
silhouettes at the lower hem** — the bottom third of the jersey is a layered
grey-on-white rose-cluster pattern that wraps front and back continuously.
Mid-weight tank fabric. NO sleeves. NO numbers anywhere. NOT a t-shirt. NOT
a football jersey. NOT a baseball jersey. **PRE-ORDER product** — design
renderings only.

BRANDING — exactly what to render:
> Logo art canonical references:
> - Black Rose three-rose-cluster: `data/brand-logos/black-rose-logo.md`
> - NBA Authentic Collection patch: `data/brand-logos/nba-authentic-collection-patch.md`
> - SR monogram (back-neck):       `data/brand-logos/sr-monogram.md`
> - Product design render:          `data/product-references/br-010-design-front.jpeg`
>
> ### COLORWAY OVERRIDE — read this BEFORE rendering
>
> The fading rose-pattern at the lower body is rendered in **tonal grey on
> white** (NOT canonical multi-color). The center medallion's rose-cluster
> is also greyscale. Wordmarks ("THE BAY", "BLACK IS BEAUTIFUL") are
> rendered in **gold/yellow** color. The SR monogram renders in black
> thread on the white body for visibility (NOT canonical gold).

### Front
- **front-body sublimated pattern** (lower half / hem area): An all-over
  layered rose-cluster silhouette pattern (canonical roses + thorny vines +
  cloud composition repeated at large scale) that fades from clean white at
  the upper-chest into tonal greyscale silhouettes at the bottom hem. The
  pattern wraps continuously to the back. **Technique:** sublimated.
  **Color:** tonal grey rose-cluster silhouettes on white.
- **front-chest** (large, ~6–7in diameter, vertically centered on the upper
  chest): A circular medallion with a thin dark-grey ring border, **"THE BAY"**
  in gold/yellow serif lettering arched across the top of the ring, and the
  canonical Black Rose three-rose-cluster (greyscale) centered inside the
  circle. **Technique:** sublimated. **Color:** dark grey ring + gold "THE
  BAY" text + greyscale rose-cluster.
- **front-left-hem / front-belly-lower-left** (~2in × 2.5in, against the
  fading rose pattern): The NBA Authentic Collection patch sewn onto the
  lower-left hip. **Technique:** embroidered-patch.

### Back
- **back-neck** (small, ~2in wide): The SR monogram embroidered directly
  onto the jersey in **black thread** (NOT canonical gold — black-on-white
  for visibility). **Technique:** embroidered. **Color:** black thread.
- **back-upper-center** (stacked vertically on three lines, ~6in tall total):
  The phrase **"BLACK / IS / BEAUTIFUL"** stacked across three lines in
  gold/yellow serif lettering, centered on the upper back below the back-neck.
  **Technique:** sublimated. **Color:** gold/yellow.
- **back-body sublimated pattern**: The same fading rose-cluster silhouette
  pattern as the front, continuing from front to back, fading from clean white
  at the upper-back into tonal greyscale at the bottom hem. **Technique:**
  sublimated. **Color:** tonal grey on white.

### Collar / Hem / Other
- **collar / round-neck binding**: Thin contrast binding (~1/4in) around the
  round neck opening. **Technique:** stitched. **Color:** dark grey / black.
- **armhole binding**: Thin matching binding around each armhole opening.
  **Technique:** stitched. **Color:** dark grey / black.
- **collar-inside** (~1.75in × 0.75in): Branded woven size tag (universal
  SkyyRose product rule). **Technique:** woven-label.

---

Study the reference image carefully. This is a  called "BLACK is Beautiful Jersey Series: 3. The Bay (Basketball)".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Deep matte black (#0A0A0A) backdrop with subtle charcoal gradient
- Cool silver key light from upper-left, black fill, thin silver rim light creating metallic edge highlights
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- NO sleeves (this is a basketball tank — sleeveless).
- NO numbers anywhere — front, back, or shoulders.
- NO player name on back.
- NO multi-color rendering of the rose-pattern — greyscale on white only.
- NO red roses, NO kelly-green stems, NO blue clouds in the pattern (the
  rose-cluster is remapped to greyscale silhouettes).
- NO MLB Authentic Collection patch. NO NFL Authentic Collection patch. NO
  Hockey Championship patch — only the NBA patch on this jersey.
- NO solid-color base — the body has the sublimated fading pattern, not a
  plain white field.
- NO embossed/debossed decoration.
- NO tackle-twill anywhere — wordmarks are sublimated, not appliquéd.
- NO standalone embroidered Black Rose rose-cluster on the back-center —
  the rose-cluster appears as part of the sublimated all-over pattern + the
  front medallion only, not as a separate embroidered logo on the back.
- NO buttons, NO placket, NO zipper.
- NO sleeve patches (there are no sleeves to patch).
- NO heat-transfer vinyl other than the sublimated medallion + sublimated
  pattern.
```

---

## br-011

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Standard garment — FLUX Pro best value (98% quality, 26% cost)
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1362c → +Layer-3=4778c → +Layer-2=1411c → final=7551c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Hockey-style pullover hoodie with long sleeves and a
hood — round-neck pullover construction, hood with **bright teal/turquoise
inner lining** against a black hood exterior, long sleeves ending in a
layered striped cuff band, straight hem with a matching layered striped hem
band. Solid **black** base body fabric with **teal/turquoise (cyan)** accent
colorway. Mid-weight knit fabric, hockey-jersey-weight. NOT a basketball
tank. NOT a baseball jersey. NOT a football jersey. NOT a sherpa jacket
(distinct from br-006 which is a separate satin bomber). **PRE-ORDER product**
— design renderings only.

BRANDING — exactly what to render:
> Logo art canonical references:
> - Black Rose three-rose-cluster: `data/brand-logos/black-rose-logo.md`
> - Hockey Championship patch:     `data/brand-logos/hockey-championship-patch.md`
> - SR monogram (back-neck):       `data/brand-logos/sr-monogram.md`
> - Product design render:          `data/product-references/br-011-design-front.jpeg`
>
> ### COLORWAY OVERRIDE — read this BEFORE rendering
>
> All decoration on this jersey is rendered in the **teal/turquoise + black +
> white** colorway, NOT canonical multi-color. The Black Rose three-rose-cluster
> medallion uses **teal/cyan roses** (instead of greyscale or red), with
> black ink outlines and white highlights — a unique colorway treatment for
> this product. The number "0" follows the same teal-on-black palette. The
> SR monogram is rendered in **teal/cyan thread** (NOT canonical gold).

### Front
- **front-chest** (large, ~6–7in diameter, vertically centered on the upper
  chest): A circular medallion with a teal/cyan + white double-ring border,
  containing the canonical Black Rose three-rose-cluster art rendered in
  **teal/cyan** (with black ink outlines and white highlights). The roses,
  vines, and cloud are all preserved in shape but recolored to the cyan
  palette. **Technique:** sublimated. **Color:** teal/cyan rose-cluster +
  black + white on black ground.
- **front-shoulder-left / front-shoulder-right** (small, ~2in tall, on each
  shoulder): A small white-thread embroidered emblem of the rose-cluster
  silhouette outline (simplified single-color version). **Technique:**
  embroidered. **Color:** white thread on black.
- **front-collar-area / upper-center-collar** (small, ~1in wide, just below
  the hood opening at the V): A small black-and-white hockey-style league
  emblem (a stylized shield with hockey stick + puck details, woven flat).
  **Technique:** woven-label. **Color:** black + white.
- **front-left-hem / front-belly-lower-left** (~2in × 2.5in, against the
  striped hem band): The Hockey Championship patch (greyscale/silver palette
  patch — see hockey-championship-patch reference). Sewn onto the lower-left
  hip. **Technique:** embroidered-patch.

### Back
- **back-neck** (small, ~2in wide): The SR monogram embroidered directly
  onto the jersey in **teal/cyan thread** (matches the colorway palette).
  **Technique:** embroidered. **Color:** teal/cyan thread on black.
- **back-yoke / upper-back** (arched, ~9in wide): The phrase **"BLACK IS
  BEAUTIFUL"** in tackle-twill lettering, baseball-script style, arched across
  the upper back. Rendered in **teal/cyan twill** on the black body.
  **Technique:** tackle-twill. **Color:** teal/cyan twill letters on black
  ground.
- **back-center** (large, ~10in tall, vertically centered): The number
  **"0"** rendered with a **teal/cyan outline edge** and a teal-and-black
  rose-cluster art fill inside the digit form. **Technique:** sublimated.
  **Color:** teal/cyan outline + teal-and-black rose-cluster fill.

### Sleeves / Hood / Hem / Other
- **hood-exterior**: Black to match the body. **Technique:** stitched.
  **Color:** black.
- **hood-interior / hood-lining**: Bright teal/turquoise lining inside the
  hood (visible when the hood is laid back or worn down). **Technique:**
  stitched. **Color:** teal/turquoise.
- **left-cuff / right-cuff striped band**: Each long-sleeve cuff ends in a
  layered striped band — solid black at the top, then a teal stripe, then
  white, then a series of thin teal stripes / parallel teal lines descending
  toward the cuff edge. **Technique:** sublimated. **Color:** layered black
  + teal/cyan + white.
- **hem / waistband striped band**: The bottom hem of the body has the
  matching striped band — solid black above, teal stripe, white, then thin
  teal stripes wrapping front and back. **Technique:** sublimated. **Color:**
  layered black + teal + white.
- **collar-inside** (~1.75in × 0.75in): Branded woven size tag (universal
  SkyyRose product rule). **Technique:** woven-label.

---

Study the reference image carefully. This is a  called "BLACK is Beautiful Jersey Series: 4. The Rose (Hockey)".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Deep matte black (#0A0A0A) backdrop with subtle charcoal gradient
- Cool silver key light from upper-left, black fill, thin silver rim light creating metallic edge highlights
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- NO red anywhere — this is the teal/cyan colorway, NOT a red colorway.
- NO yellow / gold anywhere on this jersey (the colorway is black + teal +
  white only).
- NO multi-color canonical rose-cluster — the rose-cluster is recolored to
  teal/cyan + black + white. NO red roses. NO kelly-green stems. NO
  white-and-blue cloud color.
- NO solid-color "0" digit — the digit has teal outline + rose-cluster fill.
- NO MLB Authentic Collection patch. NO NFL Authentic Collection patch. NO
  NBA Authentic Collection patch — only the Hockey Championship patch.
- NO embossed/debossed decoration.
- NO buttons, NO placket, NO zipper — pullover construction.
- NO laces at the V-neck (this is a fashion hoodie, not a tied-collar hockey
  jersey).
- NO standalone embroidered Black Rose rose-cluster on the back-center other
  than as digit fill — the rose-cluster appears as fill inside the "0" digit
  + the front medallion + the small white shoulder emblems, NOT as a separate
  back-center embroidered logo.
- NO gold thread anywhere — the SR monogram and lettering are teal, not gold.
- NO solid teal hood exterior — the hood EXTERIOR is BLACK; only the
  INTERIOR LINING is teal.
- NO sublimated all-over body pattern — the body is solid black with the
  noted decorations only (distinct from br-010 which has the all-over fading
  rose pattern).
- NO pinstripes.
```

---

## br-012

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Standard garment — FLUX Pro best value (98% quality, 26% cost)
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1368c → +Layer-3=2889c → +Layer-2=1461c → final=5718c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Authentic-style baseball jersey — V-neck collar opening with gold/yellow piping, button-front placket with gold/yellow piping, short sleeves with gold/yellow cuff piping, straight even hem (no drop-tail). Solid **dark forest green** base fabric. Mid-weight knit jersey. NOT a t-shirt, NOT a hoodie, NOT a basketball tank, NOT a football jersey — see inherited dossier for full lock detail. **PRE-ORDER product**.

BRANDING — exactly what to render:
> **All branding regions, techniques, and colors are inherited verbatim from**
> `black-is-beautiful-jersey-series-0-baseball-classic-oakland.md`. The
> abbreviated entries below exist for schema validator coverage; treat the
> inherited dossier as authoritative if any line below appears to differ.

### Front
- **front-chest** (large, arched, ~9in wide): "BLACK IS BEAUTIFUL" tackle-twill — white twill letter faces, the "A" in "BLACK" rendered as black twill, gold satin-stitch edge around every letter. **Technique:** tackle-twill. **Color:** white twill faces + one black "A" + gold satin-stitch edge.
- **front-left-hem / front-belly-lower-left** (~2in × 2.5in): The Black Rose MLB Authentic Collection patch (yellow field, navy "BLACK ROSE / COLLECTION", MLB-style batter silhouette, white "AUTHENTIC" banner, red diamond divider, "Members Only / Yay Area, Ca", SkyyRose script logo, "Made for Kings ang Queens"). Sewn onto the lower-left hip. **Technique:** embroidered-patch.

### Back
- **back-neck** (small, ~2in wide): SR monogram embroidered directly onto the jersey in gold-tone thread (matches the colorway palette). **Technique:** embroidered. **Color:** gold-tone thread.
- **back-center** (~10in–12in tall, vertically centered): Black Rose three-rose-cluster embroidered — roses + stems + thorny vines rendered in white thread; cloud at the base of the cluster rendered in yellow/gold thread (colorway-specific accent). **Technique:** embroidered. **Color:** white thread on rose-cluster + yellow/gold thread on cloud.

### Sleeves / Collar / Hem / Other
- **collar / V-neck binding**: Gold/yellow contrast piping (~1/4in–3/8in wide) around the V-neck collar opening. **Technique:** stitched. **Color:** gold/yellow.
- **left-cuff / right-cuff binding**: Gold/yellow piping around both sleeve cuff openings. **Technique:** stitched. **Color:** gold/yellow.
- **front-placket binding**: Gold/yellow piping running vertically down both sides of the front button placket. **Technique:** stitched. **Color:** gold/yellow.
- **front-placket buttons** (~5–6 buttons, evenly spaced): body-matching buttons. **Technique:** patch. **Color:** body-tone (green/yellow).
- **collar-inside** (~1.75in × 0.75in): Branded woven size tag (universal SkyyRose product rule). **Technique:** woven-label.

---

Study the reference image carefully. This is a  called "BLACK is Beautiful Jersey Series: 5. Last Oakland (Baseball)".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Deep matte black (#0A0A0A) backdrop with subtle charcoal gradient
- Cool silver key light from upper-left, black fill, thin silver rim light creating metallic edge highlights
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- See the canonical `black-is-beautiful-jersey-series-0-baseball-classic-oakland.md` Negative section for the exhaustive list. Highlights below.
- NO player number, NO player name on front, back, or sleeves.
- NO white piping (this colorway uses gold/yellow piping only).
- NO orange piping (that's the Giants colorway).
- NO black piping (that's the White edition).
- NO solid-yellow tackle-twill letter faces — the faces are WHITE (with one black "A"); only the satin-stitch EDGE is gold.
- NO uniform letter color — the "A" in "BLACK" is BLACK while every other letter face is white. This is the colorway's signature detail.
- NO contrast satin edge other than gold (no white edge, no red edge).
- NO gold thread on the rose-cluster — only the cloud renders in gold thread; the roses + stems + vines are white thread.
- NO multi-color canonical rose-cluster (kelly-green stems, red roses, blue clouds) — the cluster is recolored to white-thread + gold-cloud only.
- NO red or orange anywhere on this colorway.
- NO Black Rose logo on the chest — the chest carries only the tackle-twill wordmark + the lower-left Authentic Collection patch.
- NO SR monogram on back-center — that region is the rose-cluster only.
- NO sleeve patches anywhere on this jersey.
- NO pinstripes. NO embossed/debossed. NO sublimated panels. NO heat-transfer vinyl. NO printed graphics on the body.
- NO chest-pocket or breast-pocket.
```

---

## kids-001

**Vision cache:** present
**Inferred DNA:** garment=set | fabric=Smooth fleece knit | graphic-type='screen print' | graphic-colors=['#FFFFFF'] | branding-technique='screen print'
**Engine route:** `gpt-image` (gpt-image-1.5) — Text/logo product (kids-001) — GPT Image has 96%+ text accuracy
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=3095c → +Layer-3=4853c → +Layer-2=1467c → final=9415c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Two-piece kids hoodie set — (1) pullover hoodie with kangaroo front pocket, drawstring hood, ribbed cuffs and hem, **angular geometric color-block construction** (red hood + diagonal black-and-white upper-body panels + red lower body), and (2) matching sweatpants in solid black with drawstring waist. NOT a zip-up jacket. NOT a single-piece garment. NOT an adult-sized SKU. Mid-weight cotton-fleece fabric. **Two-piece sold together as one SKU.**

BRANDING — exactly what to render:
> Logo art canonical references:
> - Black Rose three-rose-cluster: `data/brand-logos/black-rose-logo.md`
> - Authentic Collection patch:    `data/brand-logos/black-rose-authentic-collection-patch.md`
> - Product techflat:              `data/product-references/kids-001-techflat.jpeg`
> - Real product photo:            `data/product-references/kids-001-real-photo.jpeg`

### Hoodie — Front
- **front-body color-block** (entire front body): Angular geometric color-block construction — the body is divided into three colorway panels by diagonal seams. **Upper-left panel** (from top-left descending diagonally toward center): solid **black**. **Upper-right panel** (from top-right descending diagonally toward center): solid **white**. **Lower body** (from the diagonal meeting points down to the hem, including the kangaroo pocket area): solid **red**. The diagonals create an angular chevron pointing down toward the kangaroo pocket. **Technique:** stitched. **Color:** black + white + red.
- **front-left-chest** (small, ~2.5in tall, on the wearer's left chest, on the black panel): The Black Rose Authentic Collection patch (yellow field + navy "BLACK ROSE / COLLECTION" + MLB-style batter silhouette + white "AUTHENTIC" banner + red diamond divider + "Members Only / Yay Area, Ca" footer — see patch reference). **Technique:** embroidered-patch.
- **front-center-chest** (small, ~2in tall, just above the kangaroo pocket on the red lower body): The Black Rose three-rose-cluster, rendered in greyscale (NOT canonical multi-color). **Technique:** embroidered. **Color:** white + black thread on red.

### Hoodie — Back
- **back-body color-block**: Mirrors the front color-block construction — the back has the same angular black/white upper panels and red lower body, with the diagonals continuing from the front around to the back. **Technique:** stitched. **Color:** black + white + red.

### Hoodie — Sleeves / Hood / Hem / Other
- **left-sleeve**: Solid **black** to match the front-upper-left panel. **Technique:** stitched. **Color:** black.
- **right-sleeve**: Solid **white** to match the front-upper-right panel. **Technique:** stitched. **Color:** white.
- **left-sleeve patch / right-sleeve patch** (~2in diameter, centered on each upper sleeve / shoulder area): A small circular rose-cluster patch — Black Rose three-rose-cluster art rendered in greyscale on a circular patch backing with a contrast border ring. **Technique:** embroidered-patch.
- **hood**: Solid **red** (full hood, matching the red lower body). **Technique:** stitched. **Color:** red.
- **hood-drawstring**: White flat drawstring threaded through the hood. **Technique:** stitched. **Color:** white.
- **kangaroo-pocket**: Red front kangaroo pocket integrated into the lower-body red panel. No decoration on the pocket fabric.
- **left-cuff / right-cuff**: Ribbed-knit cuffs at the wrists, color-matching their respective sleeve. **Technique:** stitched. **Color:** body-tone.
- **hem / waistband**: Ribbed-knit waistband at the bottom, red to match the lower-body panel. **Technique:** stitched. **Color:** red.
- **collar-inside / size-tag** (~1.25in × 0.5in): Branded woven size tag (universal SkyyRose product rule, scaled for kids). **Technique:** woven-label.

### Sweatpants — Front
- **pants-body**: Solid **black** sweatpants. **Technique:** stitched. **Color:** black.
- **pants-front-center / waistband-center** (small, ~2in tall): A small Black Rose three-rose-cluster (greyscale) embroidered at the center-front near the waistband. **Technique:** embroidered. **Color:** white + black thread on black.
- **right-thigh** (small, ~2in tall): A small Black Rose three-rose-cluster (greyscale) accent on the wearer's right thigh. **Technique:** embroidered. **Color:** white + black thread on black.

### Sweatpants — Other
- **waistband-drawstring**: White flat drawstring at the waistband. **Technique:** stitched. **Color:** white.
- **left-pocket / right-pocket**: Slash-style hand pockets at both sides. **Technique:** stitched.
- **pants-cuffs**: Ribbed-knit ankle cuffs (or straight-leg open hem). **Technique:** stitched. **Color:** black.
- **pants-inside / waistband-tag**: Branded woven size tag. **Technique:** woven-label.

---

Study the reference image carefully. This is a relaxed set called "Kids Colorblock Hoodie Set — Red/Black".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is Smooth fleece knit. It has EXACTLY 2 graphic element(s):
  #1 "Stylized rose emblem with 'SkyyRose' text underneath, enclosed in a circular border with 'Oakland' and 'Luxury Streetwear' text."
      WHERE: hoodie front chest, center — LOCKED POSITION, do not move
      SIZE: approx. 4x4 inches — LOCKED SIZE, do not enlarge or shrink
      TECHNIQUE: screen print
      FINISH: flat
      COLORS: #FFFFFF
  #2 "Stylized rose emblem with 'SkyyRose' text underneath, enclosed in a circular border with 'Oakland' and 'Luxury Streetwear' text."
      WHERE: joggers left thigh — LOCKED POSITION, do not move
      SIZE: approx. 3x3 inches — LOCKED SIZE, do not enlarge or shrink
      TECHNIQUE: screen print
      FINISH: flat
      COLORS: #FFFFFF

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  hoodie front body upper left panel: #000000 (matte)
  hoodie front body lower right panel: #E02121 (matte)
  hoodie right sleeve and right shoulder panel: #FFFFFF (matte)
  hoodie left sleeve: #000000 (matte)
  hoodie hood: #E02121 (matte)
  hoodie ribbing (cuffs, hem): #000000 (matte)
  hoodie drawstrings: #000000 (matte)
  joggers body: #000000 (matte)
  joggers ribbing (cuffs): #000000 (matte)
  joggers drawstrings: #000000 (matte)

Construction:
  panels: Hoodie features a color-blocked design: the front body is diagonally split with an upper left black panel and a lower right red panel. A white panel extends from the right shoulder down the right sleeve. The left sleeve is solid black. The hood is red. Joggers are solid black throughout.
  seams: Standard visible flat seams throughout both garments. No contrast stitching.
  closures: Hoodie has a black drawstring closure for the hood. Joggers have a black drawstring closure for the elastic waistband.
  details: Hoodie includes a front kangaroo pocket, ribbed cuffs on both sleeves, and a ribbed hem. Joggers feature ribbed cuffs at the ankles and an elastic waistband with an external drawstring.

Render the garment floating on an invisible form (no model, no mannequin) with:
- Clean dark gray (#1C1C1C) with subtle warmth
- Bright but not flat — angled key light, soft fill, playful rim highlights
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 2 graphic element(s)
  - Exactly 2 graphics listed above — do NOT add extras
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- NO zip-up front (the hoodie is a pullover with a kangaroo pocket).
- NO solid red body — the body is angular color-block with black/white upper panels and a red lower body, NOT a solid red field.
- NO horizontal stripe blocking — the color-block panels are DIAGONAL, creating angular chevrons.
- NO matching sleeves — the LEFT sleeve is black, the RIGHT sleeve is white (mirror continuation from the body panels).
- NO colored drawstrings — drawstrings are WHITE on the hoodie + WHITE on the pants.
- NO decoration on the back-body — the back is a clean color-block panel with no logo placement.
- NO logos on the kangaroo pocket fabric — the pocket is clean red.
- NO Love Hurts logo on this product — this is a Black Rose / Kids Capsule product, NOT Love Hurts. The patches are the Black Rose Authentic Collection patch + Black Rose rose-cluster only.
- NO multi-color (canonical) rose-cluster — the rose-cluster is greyscale.
- NO NFL Authentic Collection patch. NO NBA Authentic Collection patch. NO Hockey Championship patch — this kids product uses the BLACK ROSE (MLB-style) Authentic Collection patch.
- NO chest text or wordmark on the front body fabric — only the patches.
- NO pinstripes anywhere.
- NO embossed/debossed decoration.
- NO color-block on the sweatpants — the pants are SOLID BLACK (color-block construction is on the HOODIE only).
- NO white or red pants for this colorway — pants are black.
```

---

## kids-002

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Standard garment — FLUX Pro best value (98% quality, 26% cost)
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1295c → +Layer-3=4645c → +Layer-2=1168c → final=7108c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Two-piece kids hoodie set — (1) pullover hoodie with kangaroo front pocket, drawstring hood, ribbed cuffs and hem, **angular geometric color-block construction** (lavender/light-pink hood + diagonal lavender-and-medium-purple upper-body panels + deep purple lower body), and (2) matching sweatpants in solid deep purple with drawstring waist. NOT a zip-up jacket. NOT a single-piece garment. NOT an adult-sized SKU. Mid-weight cotton-fleece fabric. **Two-piece sold together as one SKU.** Same construction as the Red/Black colorway (kids-001) but in a purple-monochrome palette.

BRANDING — exactly what to render:
> Logo art canonical references:
> - Black Rose three-rose-cluster: `data/brand-logos/black-rose-logo.md`
> - Authentic Collection patch:    `data/brand-logos/black-rose-authentic-collection-patch.md`
> - Product techflat:              `data/product-references/kids-002-techflat.jpeg`
> - Real product photo:            `data/product-references/kids-002-real-photo.jpeg`

### Hoodie — Front
- **front-body color-block** (entire front body): Angular geometric color-block construction with diagonal seams. **Upper-left panel** (descending from top-left toward center): **lavender / light pink-purple**. **Upper-right panel** (descending from top-right toward center): **medium purple**. **Lower body** (from the diagonal meeting points down to the hem, including the kangaroo pocket area): **deep / dark purple**. **Technique:** stitched. **Color:** lavender + medium purple + deep purple.
- **front-left-chest** (small, ~2.5in tall, on the lavender panel): The Black Rose Authentic Collection patch — same multi-color patch as kids-001 (yellow field + navy text + MLB-style silhouette + white "AUTHENTIC" banner + red diamond divider + Yay Area footer). **Technique:** embroidered-patch.
- **front-center-chest** (small, ~2in tall, just above the kangaroo pocket on the deep purple lower body): The Black Rose three-rose-cluster, rendered in greyscale (NOT canonical multi-color). **Technique:** embroidered. **Color:** white + black thread on deep purple.

### Hoodie — Back
- **back-body color-block**: Mirrors the front — the back has the same angular lavender/medium-purple upper panels and deep-purple lower body. **Technique:** stitched. **Color:** lavender + medium purple + deep purple.

### Hoodie — Sleeves / Hood / Hem / Other
- **left-sleeve**: Solid **lavender / light pink-purple** to match the front-upper-left panel. **Technique:** stitched. **Color:** lavender.
- **right-sleeve**: Solid **medium purple** to match the front-upper-right panel. **Technique:** stitched. **Color:** medium purple.
- **left-sleeve patch / right-sleeve patch** (~2in diameter): Small circular rose-cluster patch (greyscale on circular patch backing). **Technique:** embroidered-patch.
- **hood**: Solid **lavender / light pink-purple** (matching the upper-left panel). **Technique:** stitched. **Color:** lavender.
- **hood-drawstring**: White flat drawstring threaded through the hood. **Technique:** stitched. **Color:** white.
- **kangaroo-pocket**: Deep purple front kangaroo pocket integrated into the lower-body panel.
- **left-cuff / right-cuff**: Ribbed-knit cuffs, color-matching their sleeves. **Technique:** stitched.
- **hem / waistband**: Ribbed-knit waistband, deep purple to match the lower-body panel. **Technique:** stitched. **Color:** deep purple.
- **collar-inside / size-tag** (~1.25in × 0.5in): Branded woven size tag. **Technique:** woven-label.

### Sweatpants — Front
- **pants-body**: Solid **deep / dark purple** sweatpants (NOT black — see catalog-name note above). **Technique:** stitched. **Color:** deep purple.
- **pants-front-center / waistband-center** (small, ~2in tall): A small Black Rose three-rose-cluster (greyscale) embroidered at the center-front near the waistband. **Technique:** embroidered. **Color:** white + black thread on deep purple.
- **right-thigh** (small, ~2in tall): A small Black Rose three-rose-cluster (greyscale) accent on the wearer's right thigh. **Technique:** embroidered. **Color:** white + black thread on deep purple.

### Sweatpants — Other
- **waistband-drawstring**: White flat drawstring. **Technique:** stitched. **Color:** white.
- **left-pocket / right-pocket**: Slash-style hand pockets. **Technique:** stitched.
- **pants-cuffs**: Ribbed-knit ankle cuffs (or straight-leg open hem). **Technique:** stitched. **Color:** deep purple.
- **pants-inside / waistband-tag**: Branded woven size tag. **Technique:** woven-label.

---

Study the reference image carefully. This is a  called "Kids Colorblock Hoodie Set — Purple/Black".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Clean dark gray (#1C1C1C) with subtle warmth
- Bright but not flat — angled key light, soft fill, playful rim highlights
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- NO BLACK pants — pants are DEEP PURPLE despite the catalog name "Purple/Black" (the techflat and real photo both confirm purple, not black).
- NO red anywhere on this colorway — this is the all-purple sister set to kids-001 (Red/Black). NO red roses, NO red body panel, NO red kangaroo pocket.
- NO solid-color hoodie body — body is angular color-block, NOT a solid lavender or solid purple field.
- NO horizontal stripe blocking — color-block panels are DIAGONAL.
- NO matching sleeves — LEFT sleeve is lavender (light), RIGHT sleeve is medium purple.
- NO colored drawstrings — drawstrings are WHITE on hoodie + WHITE on pants.
- NO decoration on the back-body — back is a clean color-block panel.
- NO logos on the kangaroo pocket fabric.
- NO Love Hurts logo on this product.
- NO multi-color (canonical) rose-cluster — greyscale only.
- NO NFL / NBA / Hockey Championship patches — only the BLACK ROSE (MLB-style) Authentic Collection patch.
- NO chest text or wordmark on the front body fabric.
- NO pinstripes.
- NO embossed/debossed decoration.
- NO color-block on the sweatpants — pants are SOLID deep purple.
```

---

## lh-002

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Standard garment — FLUX Pro best value (98% quality, 26% cost)
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1345c → +Layer-3=4432c → +Layer-2=1554c → final=7331c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Athletic-fit jogger pants (slim through the leg, drawstring waist, ribbed or banded ankle cuffs). Mid-weight cotton-fleece fabric. **Available in two colorways under this single SKU**: (1) WHITE base with BLACK contrast side-panel running vertically down each side leg, and (2) BLACK base with WHITE contrast side-panel running vertically down each side leg. NOT pants. NOT shorts. NOT a track short. NOT a basketball jogger. The contrast side-panel is a vertical strip of contrast fabric inserted from waist to ankle on each side seam, NOT a stripe-applique.

BRANDING — exactly what to render:
> Logo art canonical references:
> - Love Hurts wordmark + heart-and-thorns lockup: `data/brand-logos/love-hurts-logo.md`
> - Red Roses Cloud Cluster (LH variant of rose-cluster): `data/brand-logos/red-roses-cloud-cluster.md`
> - Product techflat (both colorways side-by-side): `data/product-references/lh-002-techflat.jpeg`
>
> ### COLORWAY OPTIONS
>
> This SKU is offered in two mirror colorways:
> - **White colorway**: white body + black side-panel
> - **Black colorway**: black body + white side-panel
> Both share identical decoration placement and technique. When rendering, pick one colorway based on customer selection at checkout.

### Front
- **front-body** (entire front body — solid colorway field): Solid white (white colorway) or solid black (black colorway). **Technique:** stitched. **Color:** white OR black.
- **front-left-pocket** (vertical slash pocket at the left side of the upper hip): Slash-style hand pocket at the front left side, with vertical welt opening. **Technique:** stitched (sewn-on welt edges). **Color:** body-matching.
- **front-right-pocket** (vertical slash pocket at the right side of the upper hip): Slash-style hand pocket at the front right side, with vertical welt opening. **Technique:** stitched (sewn-on welt edges). **Color:** body-matching.
- **front-right-thigh** (small, ~2in tall, centered on the wearer's right thigh just below the hip): A small **red rose** decoration — a standalone red rose graphic (single bloom or small Love Hurts branded mini-icon, rendered in canonical Love Hurts red). **Technique:** embroidered. **Color:** red on body fabric.

### Back
- (No back-body decoration. The back is a clean panel with no embroidered logo or graphic.)

### Sleeves / Collar / Hem / Other
- **left-side-panel** (vertical contrast strip running from waistband to ankle on the left side seam): A contrast-fabric panel inserted along the left side seam — **black panel on the white colorway**, **white panel on the black colorway**. The panel is approximately 1.5in–2in wide and runs continuously from the waistband down to the ankle hem. **Technique:** stitched (contrast fabric panel sewn into the side seam). **Color:** mirror to body color.
- **right-side-panel** (vertical contrast strip running from waistband to ankle on the right side seam): A contrast-fabric panel inserted along the right side seam — **black panel on the white colorway**, **white panel on the black colorway**. The panel is approximately 1.5in–2in wide and runs continuously from the waistband down to the ankle hem. **Technique:** stitched (contrast fabric panel sewn into the side seam). **Color:** mirror to body color.
- **waistband**: Body-matching elasticated waistband with **white flat drawstring** threaded through both colorways. **Technique:** stitched. **Color:** waistband body-tone + white drawstring.
- **drawstring**: White flat drawstring on both colorways (the white drawstring is the canonical detail across both options). **Technique:** stitched. **Color:** white.
- **left-ankle-cuff** (ribbed-knit band at the left ankle hem): Ribbed-knit cuff at the left ankle in body-matching color (some variants may use a banded-elastic cuff instead of rib-knit). **Technique:** stitched. **Color:** body-tone.
- **right-ankle-cuff** (ribbed-knit band at the right ankle hem): Ribbed-knit cuff at the right ankle in body-matching color (some variants may use a banded-elastic cuff instead of rib-knit). **Technique:** stitched. **Color:** body-tone.
- **inside-waistband** (~1.25in × 0.5in, sewn into the inside front waistband): Branded woven size tag (universal SkyyRose product rule). **Technique:** woven-label. **Color:** white label, black lettering.

---

Study the reference image carefully. This is a  called "Love Hurts Joggers".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Rich black (#0A0A0A) backdrop with barely perceptible crimson warmth in the shadows
- Warm dramatic key light upper-left with subtle crimson gel, dark fill, strong rim light for edge separation
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- NO Love Hurts wordmark across the leg or thigh — the only Love-Hurts-coded mark on this product is the small red rose mini-icon at the right hip.
- NO heart-and-thorns lockup on the joggers — the canonical Love Hurts heart-and-thorns is a graphic for jacket / shorts / shirts, NOT these joggers.
- NO sublimated all-over rose pattern on the body — both colorways are SOLID body fabric (not sublimated).
- NO third colorway — only white-with-black-panel and black-with-white-panel options exist.
- NO contrast piping at the waistband or cuffs — only the side-seam panel is contrast.
- NO black drawstring in the white colorway — drawstring is WHITE on both colorways.
- NO horizontal stripe blocking — the contrast panel runs VERTICALLY along the side seam, top to bottom.
- NO Love Hurts canonical red rose-cluster (the multi-rose composition with cloud) on the joggers — the hip mark is a single small rose, NOT the full cluster.
- NO embossed/debossed decoration anywhere.
- NO printed all-over graphic on the body — body is solid.
- NO Black Rose three-rose-cluster on this product — this is a Love Hurts collection product. Black Rose marks (gothic greyscale) do NOT appear here.
- NO contrast satin-stitch on any decoration.
- NO zipper closures on the pockets — slash pockets are open-welt, not zippered.
- NO patch applications on the joggers — branding is embroidered, not patch-sewn.
- NO ankle taper that hits above the cuff — joggers terminate cleanly at the ribbed/banded cuff at ankle level.
```

---

## lh-003

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Standard garment — FLUX Pro best value (98% quality, 26% cost)
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1355c → +Layer-3=3346c → +Layer-2=1788c → final=6489c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Knee-length athletic basketball shorts — **white mesh body fabric** with **all-over sublimated red-roses-cluster pattern** repeating across the entire body, **black ribbed elasticated waistband** with **white flat drawstring**, **side hand pockets** with vertical welt openings, **black ribbed-binding hem with red contrast piping** along the leg openings. Knee-length cut. NOT pants. NOT joggers. NOT short-shorts. NOT a swim trunk. NOT a track short.

BRANDING — exactly what to render:
> Logo art canonical references:
> - Love Hurts logo (wordmark + heart-and-thorns): `data/brand-logos/love-hurts-logo.md`
> - Red Roses Cloud Cluster (the LH variant of the rose-cluster — red roses + green stems + white-and-blue cloud): `data/brand-logos/red-roses-cloud-cluster.md`
> - Product techflat: `data/product-references/lh-003-techflat.jpeg`

### Front
- **front-body** (entire white mesh field, front and back continuous): The canonical Red Roses Cloud Cluster art (three red roses + thorny green vines + white-and-blue cloud at base) sublimated as a small repeating pattern across the entire white mesh body, scattered evenly with the cloud pointing down. Each rose-cluster is rendered in canonical full color (saturated red roses, kelly-green stems, white-and-blue cloud) on the white ground. **Technique:** sublimated. **Color:** canonical multi-color red green white blue on white mesh.
- **front-right-thigh** (large, diagonal, ~6–7in tall): The "Love Hurts" wordmark in cursive script — large red script lettering sublimated on the right thigh, reading top-to-bottom diagonally as the cursive lettering descends. **Technique:** sublimated. **Color:** canonical Love Hurts red.
- **front-left-hem** (~2in × 2.5in, near the bottom hem on the wearer's left hip area): A small Love Hurts branded patch — a black-square patch with the "Love Hurts" wordmark in cursive red lettering. **Technique:** embroidered-patch. **Color:** red wordmark on black patch.

### Back
- **back-body** (entire white mesh field, continues from front): Same all-over Red Roses Cloud Cluster pattern as the front, continuing seamlessly. **Technique:** sublimated. **Color:** canonical multi-color on white mesh.

### Sleeves / Collar / Hem / Other
- **waistband** (~1.5in tall, top of shorts): Black ribbed-knit elasticated waistband. **Technique:** stitched. **Color:** black.
- **drawstring** (waistband-thread, ~24in long): White flat drawstring threaded through the waistband. **Technique:** stitched. **Color:** white.
- **left-pocket** (front-side hand pocket on wearer's left): Vertical hand pocket with welt opening. **Technique:** stitched. **Color:** white mesh body with subtle contrast welt.
- **right-pocket** (front-side hand pocket on wearer's right): Vertical hand pocket with welt opening. **Technique:** stitched. **Color:** white mesh body with subtle contrast welt.
- **leg-binding** (each leg opening, ~1in wide): Black ribbed-knit binding with a thin red contrast piping accent running along the binding edge. **Technique:** stitched. **Color:** black with red piping.
- **inside-waistband** (~1.5in × 0.5in, interior tag): Branded woven size tag. **Technique:** woven-label. **Color:** brand-label palette.

---

Study the reference image carefully. This is a  called "Love Hurts Basketball Shorts".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Rich black (#0A0A0A) backdrop with barely perceptible crimson warmth in the shadows
- Warm dramatic key light upper-left with subtle crimson gel, dark fill, strong rim light for edge separation
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- NO solid-color body — the entire body has the sublimated all-over rose-cluster pattern, NOT a plain white mesh field.
- NO greyscale rendering of the rose-cluster — this is the LOVE HURTS variant in **canonical full color** (red roses + green stems + white-and-blue cloud), NOT the Black Rose greyscale variant.
- NO Black Rose three-rose-cluster on this product — this is a Love Hurts product, the cluster is the **red-roses** variant only.
- NO black mesh body — body is WHITE mesh (distinct from br-007 BR×LH shorts which has black mesh).
- NO contrast color side-panels — body is uniform white mesh with the sublimated pattern; no white-mesh-vs-black-mesh side panel distinction (that's br-007).
- NO OAKLAND tackle-twill wordmark — that's br-007. This product has only the Love Hurts cursive wordmark.
- NO COLORWAY OVERRIDE — colors render in canonical Love Hurts palette, NOT remapped to greyscale or tonal.
- NO black drawstring — drawstring is WHITE.
- NO white waistband — waistband is BLACK ribbed.
- NO additional pockets on the back — only the two front side hand pockets exist.
- NO zipper closures on the pockets — pockets are open-welt, not zippered.
- NO heart-and-thorns lockup separately on the body — the heart-and-thorns canonical art is NOT placed on this product as a standalone graphic.
- NO sublimated pattern in greyscale — the all-over rose pattern is canonical multi-color.
- NO Love Hurts wordmark on the LEFT thigh — the cursive script is on the RIGHT thigh only.
- NO embossed/debossed decoration anywhere.
- NO sleeve elements (this is a shorts garment, lower-body only).
- NO numbers anywhere — no jersey numerals.
- NO Authentic Collection patch — that patch is reserved for the Black Rose jersey series.
```

---

## lh-004

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Standard garment — FLUX Pro best value (98% quality, 26% cost)
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1351c → +Layer-3=5255c → +Layer-2=1722c → final=8328c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Hooded varsity-bomber hybrid jacket — **white body fabric** with **black contrast raglan sleeves** (sleeves are a different color from the body, joining at a diagonal raglan seam from underarm to neck), **black hood**, **button-front placket** (snap or button-front closure running the full length of the center-front), **vertical slash hand pockets** at the lower sides with welt openings, **ribbed-knit cuffs and waistband with red+white+black striped accent banding**. The hood lining shows a small white-and-red rose-silhouette mini-pattern (visible when the hood is laid open or worn down). NOT a satin bomber. NOT a sherpa jacket. NOT a windbreaker. NOT a hoodie (it has button-front closure, not pullover construction).

BRANDING — exactly what to render:
> Logo art canonical references:
> - Love Hurts logo (wordmark + heart-and-thorns): `data/brand-logos/love-hurts-logo.md`
> - Red Roses Cloud Cluster (LH variant): `data/brand-logos/red-roses-cloud-cluster.md`
> - Product techflat: `data/product-references/lh-004-techflat.jpeg`

### Front
- **front-body** (entire white field, between the raglan sleeve seams and excluding the placket): Solid **white** fabric. **Technique:** stitched. **Color:** white.
- **front-left-chest** (~3–4in tall, upper left chest panel — "Love" half of the wordmark): The **"Love"** portion of the canonical "Love Hurts" cursive script wordmark — wearer's LEFT chest, placket separates it from "Hurts" on the right. Hand-drawn graffiti-cursive style (see logo reference). **Technique:** embroidered. **Color:** canonical Love Hurts red.
- **front-right-chest** (~3–4in tall, upper right chest panel — "Hurts" half of the wordmark): The **"Hurts"** portion of the canonical "Love Hurts" cursive script wordmark — wearer's RIGHT chest, placket separates it from "Love" on the left. Hand-drawn graffiti-cursive style (see logo reference). **Technique:** embroidered. **Color:** canonical Love Hurts red.
- **front-placket** (vertical center-front closure, full length): Button or snap front placket running from the V-opening at the collar to the bottom of the ribbed waistband. **Technique:** patch (sewn-on snap/button hardware). **Color:** body-tone snaps/buttons on white.
- **front-left-pocket** (vertical slash welt opening at the lower-left side of the body, just above the waistband): Slash hand pocket with vertical welt opening. **Technique:** stitched (welt-edge construction). **Color:** white body with subtle welt.
- **front-right-pocket** (vertical slash welt opening at the lower-right side of the body, just above the waistband): Slash hand pocket with vertical welt opening. **Technique:** stitched (welt-edge construction). **Color:** white body with subtle welt.

### Back
- **back-body** (large, ~10–12in tall, vertically centered on the back): The **canonical Love Hurts heart-and-thorns + roses lockup** — a bright red broken-heart-and-thorns illustration with **canonical red-roses-cluster art** wrapping around / accenting it. The composition fills most of the back upper-mid area. Rendered in canonical Love Hurts multi-color (red heart with dark cracks, brown/dark thorny vines, red rose petals, kelly-green stems). **Technique:** embroidered. **Color:** canonical Love Hurts multi-color (red + green + brown + black ink outlines).

### Sleeves / Hood / Hem / Other
- **left-sleeve** (solid black raglan, diagonal seam from underarm to neck on the left): Solid **black** fabric, different color from the white body. **Technique:** stitched. **Color:** black.
- **right-sleeve** (solid black raglan, diagonal seam from underarm to neck on the right): Solid **black** fabric, different color from the white body. **Technique:** stitched. **Color:** black.
- **left-cuff** (ribbed-knit striped band at the left sleeve cuff, ~3–4 stripes): Ribbed-knit band with alternating white + red + black stripes. **Technique:** stitched (striped rib-knit). **Color:** alternating white + red + black.
- **right-cuff** (ribbed-knit striped band at the right sleeve cuff, ~3–4 stripes): Ribbed-knit band with alternating white + red + black stripes. **Technique:** stitched (striped rib-knit). **Color:** alternating white + red + black.
- **waistband** (ribbed-knit striped band at the bottom hem, ~3–4 stripes, matching the cuff accent): The bottom hem of the body has a **ribbed-knit waistband with the same white + red + black striped accent** as the cuffs. **Technique:** stitched. **Color:** alternating white + red + black.
- **hood**: Solid **black** hood (matches the black raglan sleeves). **Technique:** stitched. **Color:** black.
- **hood-lining** (inner hood lining, visible when hood is laid back or worn down): A **white-and-red rose-silhouette pattern** sublimated inside the hood lining — small red rose silhouettes scattered across the white inner-lining fabric. **Technique:** sublimated. **Color:** small red rose silhouettes on white inner-lining.
- **collar-tag** (~1.75in × 0.75in, sewn at the interior back collar): Branded woven size tag (universal SkyyRose product rule). **Technique:** woven-label. **Color:** white label, black lettering.

---

Study the reference image carefully. This is a  called "Love Hurts Bomber Jacket".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Rich black (#0A0A0A) backdrop with barely perceptible crimson warmth in the shadows
- Warm dramatic key light upper-left with subtle crimson gel, dark fill, strong rim light for edge separation
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- NO Black Rose three-rose-cluster on this product — this is a Love Hurts product. The back graphic is the Love Hurts heart-and-thorns + canonical red roses, NOT the Black Rose greyscale cluster.
- NO greyscale rose rendering anywhere — all rose imagery is canonical Love Hurts multi-color (red + green + brown).
- NO single-color body — the body is WHITE with BLACK raglan sleeves and BLACK hood (three-color contrast: white body + black sleeves + black hood).
- NO non-raglan sleeve seam — the sleeves are RAGLAN cut (diagonal seam from underarm to neck), NOT set-in.
- NO satin or sherpa fabric — this is a cotton-blend bomber/varsity weight, NOT satin (that's br-006) or sherpa.
- NO zipper-front closure — the front is BUTTON or SNAP placket, NOT a zipper.
- NO solid-color cuffs/hem — the rib-knit cuffs and waistband have a STRIPED accent pattern (white + red + black), NOT solid black or solid white.
- NO sublimated all-over body pattern — the body is solid white, NOT sublimated.
- NO Love Hurts wordmark on the back — the back has the heart-and-thorns + roses graphic; the wordmark is on the front-chest only.
- NO heart-and-thorns on the front — the front has the cursive "Love" + "Hurts" wordmark only; the heart graphic is on the back.
- NO red drawstrings — there is no drawstring on this jacket (it's a button-front bomber, not a pullover hoodie).
- NO white sleeves — sleeves are black.
- NO contrast piping on the body or pockets.
- NO Authentic Collection patch — that patch is reserved for the Black Rose jersey series.
- NO embossed/debossed decoration anywhere.
- NO printed graphics on the body fabric — branding is embroidered.
- NO numbers anywhere.
```

---

## lh-005

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Accessory — FLUX Pro best value for simple items
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1337c → +Layer-3=3168c → +Layer-2=1624c → final=6129c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
A **black PU/faux-leather fanny pack (waist-belt bag / cross-body sling)** — small rectangular bag body in pebbled-textured black faux-leather, single front-pocket with a horizontal zipper closure, **adjustable black nylon webbing strap** with a **plastic quick-release buckle** (clip-on/clip-off side-release buckle), worn at the waist or across the chest. NOT a backpack. NOT a tote bag. NOT a duffel. NOT a wristlet. NOT a leather handbag. **A small accessory product** — distinct from the apparel pieces in the Love Hurts collection.

BRANDING — exactly what to render:
> Logo art canonical references:
> - Love Hurts logo (cursive script):  `data/brand-logos/love-hurts-logo.md` (only the cursive lettering style is referenced here — the full lockup with broken-heart is NOT on this bag)
> - Product real photo:                 `data/product-references/lh-005-fannie-photo.jpeg`
> - Product mockup:                     `data/product-references/lh-005-fannie-mockup.jpeg`

### Front
- **front-body** (the front face of the bag, ~6–8in wide): Solid **black pebbled faux-leather** fabric. **Technique:** stitched. **Color:** black.
- **front-pocket-zipper** (horizontal, across the front face below the bag's top edge): A black metal/plastic zipper running horizontally across the front face providing access to the front pocket. **Technique:** patch (sewn-on zipper hardware). **Color:** black zipper teeth and pull.
- **front-center-bottom** (~3–4in wide, centered on the lower front face below the zipper): The wordmark **"FANNIE"** in stylized white cursive script lettering, with a small **canonical Love Hurts red rose graphic** decoration to the immediate right of the wordmark (a single small red rose accent — similar in style to the small standalone rose accent used on lh-002 joggers). **Technique:** embroidered (wordmark in white thread + small red rose embroidered detail). **Color:** white "FANNIE" + small red rose accent.

### Back
- **back-body** (the panel against the wearer's body): Solid **black pebbled faux-leather**, no decoration. **Technique:** stitched. **Color:** black.
- **strap-attachment-points** (D-rings or stitched belt-loops at the upper-left and upper-right corners of the bag): Two D-rings or stitched belt-loops where the nylon strap attaches. **Technique:** patch (sewn-on hardware). **Color:** black.

### Strap / Hardware / Other
- **adjustable-strap**: Black nylon webbing strap, adjustable length via slider, with a **plastic quick-release side-release buckle** at one point so the strap can clip on and off. **Technique:** patch (sewn-on plastic buckle hardware) + stitched (webbing). **Color:** black webbing + black plastic buckle.
- **strap-buckle**: Plastic side-release clip buckle. **Technique:** patch (sewn-on plastic hardware). **Color:** black.
- **interior-tag** (~1in × 0.5in, sewn into the interior of the front pocket): Branded woven size tag (universal SkyyRose product rule, scaled for accessory). **Technique:** woven-label. **Color:** white label, black lettering.

---

Study the reference image carefully. This is a  called "The Fannie".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Rich black (#0A0A0A) backdrop with barely perceptible crimson warmth in the shadows
- Warm dramatic key light upper-left with subtle crimson gel, dark fill, strong rim light for edge separation
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- NO Love Hurts full lockup (wordmark + broken-heart-and-thorns) on the bag — only the "FANNIE" wordmark + a single small red rose accent appear. The full Love Hurts lockup is for jackets / shorts / shirts, NOT this small accessory.
- NO Black Rose three-rose-cluster on this product — this is a Love Hurts collection product.
- NO multi-color rose-cluster composition — the rose accent is a single small red rose graphic, NOT the full canonical multi-rose-on-cloud composition.
- NO patches on this bag — the wordmark + rose are EMBROIDERED directly into the front face, NOT sewn-on patches.
- NO Authentic Collection patch.
- NO greyscale wordmark — the "FANNIE" lettering is WHITE on the black faux-leather.
- NO red wordmark — the "FANNIE" letters are WHITE; the only red element is the small rose graphic accent next to the wordmark.
- NO additional pockets visible from outside other than the single front zipper-pocket. No back pocket. No side pockets.
- NO hardware in metal-gold or rose-gold finish — all hardware (buckle, zipper) is BLACK.
- NO contrast piping along any edge — the bag is uniformly black faux-leather with no contrast piping or trim.
- NO drawstring closure — closure is the front zipper only.
- NO embossed or debossed branding — the FANNIE wordmark is embroidered, NOT embossed into the faux-leather surface.
- NO real leather (this is **faux-leather / PU pebbled-finish**, not genuine leather).
- NO printed graphics — branding is embroidered.
- NO Skyy Rose Co script logo on this bag — the only branding is "FANNIE" + the small red rose accent.
```

---

## sg-001

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Standard garment — FLUX Pro best value (98% quality, 26% cost)
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1341c → +Layer-3=3248c → +Layer-2=1742c → final=6331c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Knee-length athletic basketball shorts — **white mesh ground fabric with an all-over sublimated photographic print of the Bay Bridge (San Francisco-Oakland Bay Bridge) in daytime / clear-blue-sky lighting**. The photo print shows the steel-cabled Bay Bridge crossing the water with the SF skyline visible in the background, blue sky overhead, and water reflections at the bottom hem. Standard basketball-shorts construction: black elasticated waistband at the top with **white drawstring**, vertical slash side hand pockets, knee-length cut, no leg-binding contrast piping. NOT pants. NOT joggers. NOT short-shorts. NOT a swim trunk. NOT a track short. NOT a basketball jersey. NOT the Stay Golden Shorts (that's sg-003 — Golden Gate Bridge sunset palette, separate SKU).

BRANDING — exactly what to render:
> Reference images:
> - Bridge Series shorts variants (Bay Bridge top + Stay Golden bottom): `data/product-references/sg-001-and-sg-003-bridge-shorts-variants.jpeg`
> - Bay Bridge shorts standalone techflat: `data/product-references/sg-001-day-bay-bridge-shorts.jpeg`

### Front
- **front-body** (entire body — front and back continuous): All-over sublimated photographic print of the **San Francisco-Oakland Bay Bridge in daytime daylight** — clear blue sky filling the upper third, the steel-truss Bay Bridge spanning across the middle (center-aligned, with the cantilever section visible), the SF skyline (downtown buildings) visible behind/beside the bridge, and water at the lower portion with reflections of the bridge. Photographic, hyper-realistic, NOT illustrated. The print wraps continuously front-to-back. **Technique:** sublimated. **Color:** photographic full-color (blue sky + grey-and-white bridge steel + tan/grey building skyline + blue water with reflections).

### Back
- **back-body** (entire field, continuation of front): Same Bay Bridge daytime photographic print continuing seamlessly from the front around to the back. **Technique:** sublimated. **Color:** photographic full-color, continuous wrap.

### Sleeves / Collar / Hem / Other
- **waistband** (~1.5in tall, top of shorts): Black elasticated waistband at the top. **Technique:** stitched. **Color:** black.
- **drawstring** (~24in long, threaded through waistband): White flat drawstring threaded through the waistband, hanging from the front center. **Technique:** stitched. **Color:** white.
- **left-pocket** (front-side hand pocket on wearer's left): Vertical slash hand pocket with welt opening. **Technique:** stitched. **Color:** body-matching (mesh shows the underlying photo print).
- **right-pocket** (front-side hand pocket on wearer's right): Vertical slash hand pocket with welt opening. **Technique:** stitched. **Color:** body-matching.
- **leg-hem** (each leg opening, clean hem): Plain finished hem at each leg opening — no contrast piping, no contrast binding, no rib-knit band. **Technique:** stitched. **Color:** body-matching.
- **inside-waistband** (~1.5in × 0.5in interior tag): Branded woven size tag (universal SkyyRose product rule). **Technique:** woven-label. **Color:** brand-label palette.

---

Study the reference image carefully. This is a  called "The Bridge Series 'The Bay Bridge' Shorts".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Warm charcoal (#1A1A1A) fading to deep black, hint of golden hour warmth
- Golden-warm key light upper-left, soft neutral fill, warm rim light creating a premium glow
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- NO Golden Gate Bridge in the print — this is the BAY BRIDGE (a steel-truss/cantilever bridge with the SF skyline behind it), NOT the Golden Gate (the orange suspension bridge between SF and Marin). The Golden Gate appears on sg-003 Stay Golden Shorts.
- NO sunset / twilight / orange palette — this is the DAYTIME Bay Bridge with blue sky. Sunset/sunrise palette belongs to sg-003.
- NO night-time Bay Bridge with city lights — this is the clear-day variant. (A night-Bay-Bridge alternate render exists in older asset directories but is NOT a current SKU.)
- NO illustrated / cartoon-rendered bridge — the print is a hyper-realistic photographic sublimation, not a stylized illustration.
- NO rose-cluster decoration anywhere on the body — the Bridge Series shorts carry the photographic print only, NO rose graphics layered on top of the body.
- NO Black Rose three-rose-cluster, NO Love Hurts canonical roses, NO SR monogram, NO Authentic Collection patch on these shorts. The Bridge Series is purely the bridge photograph as the brand identifier.
- NO black mesh body — body is WHITE mesh with the sublimated print on top (the print supplies all visible color).
- NO contrast color side-panels — body is uniform front-to-back.
- NO black drawstring — drawstring is WHITE.
- NO white waistband — waistband is BLACK.
- NO zipper closures on the pockets — open welt.
- NO additional pockets on the back — only two front side hand pockets.
- NO embossed/debossed decoration anywhere.
- NO rib-knit leg-binding — the leg opening is a clean stitched hem.
- NO numbers, NO wordmark, NO chest text — bridge photo print is the only graphic.
- NO sleeves (this is a shorts garment, lower-body only).
```

---

## sg-002

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Standard garment — FLUX Pro best value (98% quality, 26% cost)
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1337c → +Layer-3=3050c → +Layer-2=1241c → final=5628c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Classic crew-neck short-sleeve t-shirt — solid white cotton/cotton-blend body, set-in short sleeves, ribbed crew neck, straight even hem. Pairs in The Bridge Series with the Stay Golden Shorts (sg-003 Golden Gate sunset palette). NOT a tank. NOT a long-sleeve tee. NOT a hoodie. NOT a polo. NOT the Bay Bridge Shirt (that's sg-005 — blue rose-cluster decoration, separate SKU). **The Stay Golden colorway uses a PURPLE/VIOLET rose-cluster on the chest** (matching the purple-and-orange Golden Gate sunset palette).

BRANDING — exactly what to render:
> Logo art canonical references:
> - Black Rose three-rose-cluster (recolored to purple for this SKU): `data/brand-logos/black-rose-logo.md`
> - SR monogram (back-neck):                                          `data/brand-logos/sr-monogram.md`
> - Product techflat:                                                  `data/product-references/sg-002-stay-golden-shirt-techflat.jpeg`
>
> ### COLORWAY OVERRIDE — read this BEFORE rendering
>
> The chest rose-cluster is rendered in **PURPLE/VIOLET tonal colors** with
> dark grey/black ink outlines, sitting on a dark grey/black cloud at the
> base — NOT canonical multi-color and NOT canonical greyscale. The
> "Stay Golden" colorway uses a violet-on-white palette to harmonize with
> the matching Stay Golden Shorts (sg-003) sunset Golden Gate colorway.

### Front
- **front-left-chest** (small, ~3in tall, on the wearer's left chest): The canonical Black Rose three-rose-cluster art (three roses + thorny vines + cloud at base) rendered in **purple/violet tonal colors** — petals in saturated purple-and-violet shades with darker violet shading and black ink outlines, stems and vines in darker purple-grey, cloud at the base in dark grey/charcoal. NOT canonical multi-color. NOT canonical greyscale. **Technique:** sublimated. **Color:** purple-violet rose-cluster on white ground.

### Back
- **back-neck** (small, ~1.5in wide, top-center just below the collar): The SR monogram embroidered onto the jersey in **dark grey / black thread** (NOT canonical gold — black-on-white reads cleanly where gold-on-white would not on a casual tee). Rendered as the canonical SR cursive script. **Technique:** embroidered. **Color:** dark grey / black thread on white.

### Sleeves / Collar / Hem / Other
- **collar** (~0.5in wide ribbed crew neck): Standard ribbed crew-neck collar. **Technique:** stitched. **Color:** white.
- **left-sleeve** (short sleeve, plain hem): Short set-in sleeve, plain stitched hem at the cuff. **Technique:** stitched. **Color:** white.
- **right-sleeve** (short sleeve, plain hem): Mirror of left-sleeve. **Technique:** stitched. **Color:** white.
- **hem** (straight even bottom hem): Plain stitched bottom hem. **Technique:** stitched. **Color:** white.
- **collar-inside** (~1.5in × 0.5in interior tag): Branded woven size tag. **Technique:** woven-label. **Color:** brand-label palette.

---

Study the reference image carefully. This is a  called "The Bridge Series 'Stay Golden' Shirt".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Warm charcoal (#1A1A1A) fading to deep black, hint of golden hour warmth
- Golden-warm key light upper-left, soft neutral fill, warm rim light creating a premium glow
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- NO blue rose-cluster on the chest — this is the PURPLE/VIOLET Stay Golden colorway. Blue rose-cluster belongs to sg-005 Bay Bridge Shirt.
- NO canonical multi-color rose-cluster (red roses + green stems + white-and-blue cloud) — the cluster is recolored to violet on this SKU.
- NO canonical greyscale rose-cluster (Black Rose canonical) — recolored to violet.
- NO Bay Bridge / Golden Gate photo print on the body — the body is solid white. The bridge photo prints are on the matching shorts (sg-001, sg-003), NOT on this shirt.
- NO chest text or wordmark on the front body fabric — only the chest rose decoration.
- NO logo or graphic on the back body — only the small back-neck SR monogram.
- NO Authentic Collection patch — that patch is reserved for the Black Rose jersey series.
- NO Black Rose logo at front-center, front-right, or as a back-center large emblem — chest mark is small left-chest only.
- NO Love Hurts branding — this is a Signature collection product.
- NO sublimated all-over body pattern — body is solid white.
- NO contrast color sleeve cuffs or hem.
- NO embossed/debossed decoration.
- NO V-neck or henley placket — this is a crew-neck tee with no front opening.
```

---

## sg-003

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Standard garment — FLUX Pro best value (98% quality, 26% cost)
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1338c → +Layer-3=3379c → +Layer-2=1315c → final=6032c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Knee-length athletic basketball shorts — **white mesh ground fabric with an all-over sublimated photographic print of the Golden Gate Bridge at sunset / golden-hour twilight**. The photo print shows the iconic orange-red Golden Gate Bridge silhouetted against a purple-and-orange sunset sky, with light reflections rippling across the water at the lower portion. Standard basketball-shorts construction: black elasticated waistband at the top with **white drawstring**, vertical slash side hand pockets, knee-length cut, no leg-binding contrast piping. "Stay Golden" refers to the **Golden Gate Bridge at golden hour**. NOT pants. NOT joggers. NOT short-shorts. NOT a swim trunk. NOT a track short. NOT the Bay Bridge Shorts (that's sg-001 — daytime SF-Oakland Bay Bridge, separate SKU).

BRANDING — exactly what to render:
> Reference images:
> - Bridge Series shorts variants (Bay Bridge top + Stay Golden bottom): `data/product-references/sg-001-and-sg-003-bridge-shorts-variants.jpeg`
> - Stay Golden shorts standalone techflat: `data/product-references/sg-003-sunset-golden-gate-shorts.jpeg`

### Front
- **front-body** (entire body — front and back continuous): All-over sublimated photographic print of the **Golden Gate Bridge at sunset / golden-hour twilight** — purple-and-orange sky filling the upper third (deep purple-violet at top transitioning to orange near the horizon), the iconic **orange-red suspension Golden Gate Bridge** silhouetted across the middle (the bridge color reads orange-red against the dusk sky), and rippling water at the lower portion with **vertical light reflections** (orange + yellow + pink + white streaks running vertically downward) reflecting the city lights and bridge against the water. Photographic, hyper-realistic, NOT illustrated. The print wraps continuously front-to-back. **Technique:** sublimated. **Color:** photographic full-color (purple-violet + orange + red + yellow + pink reflections on dark water).

### Back
- **back-body** (entire field, continuation of front): Same Golden Gate sunset photographic print continuing seamlessly from the front around to the back. **Technique:** sublimated. **Color:** photographic full-color sunset, continuous wrap.

### Sleeves / Collar / Hem / Other
- **waistband** (~1.5in tall, top of shorts): Black elasticated waistband at the top (matching sg-001 construction). **Technique:** stitched. **Color:** black.
- **drawstring** (~24in long, threaded through waistband): White flat drawstring threaded through the waistband, hanging from the front center. **Technique:** stitched. **Color:** white.
- **left-pocket** (front-side hand pocket on wearer's left): Vertical slash hand pocket with welt opening. **Technique:** stitched. **Color:** body-matching.
- **right-pocket** (front-side hand pocket on wearer's right): Vertical slash hand pocket with welt opening. **Technique:** stitched. **Color:** body-matching.
- **leg-hem** (each leg opening, clean hem): Plain finished hem — no contrast piping, no rib-knit band. **Technique:** stitched. **Color:** body-matching.
- **inside-waistband** (~1.5in × 0.5in interior tag): Branded woven size tag (universal SkyyRose product rule). **Technique:** woven-label. **Color:** brand-label palette.

---

Study the reference image carefully. This is a  called "The Bridge Series 'Stay Golden' Shorts".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Warm charcoal (#1A1A1A) fading to deep black, hint of golden hour warmth
- Golden-warm key light upper-left, soft neutral fill, warm rim light creating a premium glow
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- NO Bay Bridge in the print — this is the GOLDEN GATE (orange-red suspension bridge between SF and Marin), NOT the Bay Bridge (steel-truss bridge between SF and Oakland with downtown skyline). The Bay Bridge appears on sg-001.
- NO daytime / clear-blue-sky palette — this is the SUNSET / GOLDEN HOUR variant with purple-and-orange sky. Daytime palette belongs to sg-001.
- NO illustrated / cartoon-rendered bridge — the print is a hyper-realistic photographic sublimation.
- NO SF skyline in the photo — the Golden Gate bridge spans water + Marin headlands, NOT downtown skyline. (The Bay Bridge image has the skyline; this one does not.)
- NO rose-cluster decoration anywhere on the body — Bridge Series carries photo-print only.
- NO Black Rose three-rose-cluster, NO Love Hurts canonical roses, NO SR monogram, NO Authentic Collection patch.
- NO black mesh body — body is WHITE mesh with the sublimated sunset print on top.
- NO contrast color side-panels.
- NO black drawstring — drawstring is WHITE.
- NO white waistband — waistband is BLACK.
- NO zipper closures on the pockets.
- NO additional back pockets.
- NO embossed/debossed decoration.
- NO rib-knit leg-binding — clean stitched hem.
- NO numbers, NO wordmark, NO chest text on the body.
- NO sleeves.
```

---

## sg-005

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Standard garment — FLUX Pro best value (98% quality, 26% cost)
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1340c → +Layer-3=2858c → +Layer-2=917c → final=5115c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Classic crew-neck short-sleeve t-shirt — solid white cotton/cotton-blend body, set-in short sleeves, ribbed crew neck, straight even hem. Pairs in The Bridge Series with the Bay Bridge Shorts (sg-001 daytime SF-Oakland Bay Bridge palette). NOT a tank. NOT a long-sleeve tee. NOT a hoodie. NOT a polo. NOT the Stay Golden Shirt (that's sg-002 — purple rose-cluster decoration, separate SKU). **The Bay Bridge colorway uses a BLUE/CYAN rose-cluster on the chest** (matching the daytime-blue Bay Bridge palette).

BRANDING — exactly what to render:
> Logo art canonical references:
> - Black Rose three-rose-cluster (recolored to blue for this SKU): `data/brand-logos/black-rose-logo.md`
> - SR monogram (back-neck):                                         `data/brand-logos/sr-monogram.md`
> - Product techflat:                                                 `data/product-references/sg-005-bay-bridge-shirt-techflat.jpeg`
>
> ### COLORWAY OVERRIDE — read this BEFORE rendering
>
> The chest rose-cluster is rendered in **BLUE/CYAN tonal colors** with
> dark grey/black ink outlines, sitting on a dark grey/black cloud at the
> base — NOT canonical multi-color and NOT canonical greyscale. The
> "Bay Bridge" colorway uses a blue-on-white palette to harmonize with
> the matching Bay Bridge Shorts (sg-001) daytime blue-sky colorway.

### Front
- **front-left-chest** (small, ~3in tall, on the wearer's left chest): The canonical Black Rose three-rose-cluster art (three roses + thorny vines + cloud at base) rendered in **blue/cyan tonal colors** — petals in saturated blue-and-cyan shades with darker navy-blue shading and black ink outlines, stems and vines in darker blue-grey, cloud at the base in dark grey/charcoal. NOT canonical multi-color. NOT canonical greyscale. **Technique:** sublimated. **Color:** blue-cyan rose-cluster on white ground.

### Back
- **back-neck** (small, ~1.5in wide, top-center just below the collar): The SR monogram embroidered onto the jersey in **dark grey / black thread** (NOT canonical gold). **Technique:** embroidered. **Color:** dark grey / black thread on white.

### Sleeves / Collar / Hem / Other
- **collar** (~0.5in wide ribbed crew neck): Standard ribbed crew-neck collar. **Technique:** stitched. **Color:** white.
- **left-sleeve** (short sleeve, plain hem): Short set-in sleeve. **Technique:** stitched. **Color:** white.
- **right-sleeve** (short sleeve, plain hem): Mirror of left. **Technique:** stitched. **Color:** white.
- **hem** (straight even bottom hem): Plain stitched bottom hem. **Technique:** stitched. **Color:** white.
- **collar-inside** (~1.5in × 0.5in interior tag): Branded woven size tag. **Technique:** woven-label. **Color:** brand-label palette.

---

Study the reference image carefully. This is a  called "The Bridge Series 'The Bay Bridge' Shirt".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Warm charcoal (#1A1A1A) fading to deep black, hint of golden hour warmth
- Golden-warm key light upper-left, soft neutral fill, warm rim light creating a premium glow
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- NO purple rose-cluster on the chest — this is the BLUE/CYAN Bay Bridge colorway. Purple rose-cluster belongs to sg-002 Stay Golden Shirt.
- NO canonical multi-color rose-cluster — the cluster is recolored to blue on this SKU.
- NO canonical greyscale rose-cluster — recolored to blue.
- NO Bay Bridge / Golden Gate photo print on the body — body is solid white. Bridge photo prints belong to the matching shorts.
- NO chest text or wordmark on the front body fabric — only the chest rose.
- NO logo on the back body — only the small back-neck SR monogram.
- NO Authentic Collection patch.
- NO Black Rose logo at front-center, front-right, or as a back-center large emblem.
- NO Love Hurts branding.
- NO sublimated all-over body pattern — body is solid white.
- NO contrast color sleeve cuffs or hem.
- NO embossed/debossed decoration.
- NO V-neck or henley placket.
```

---

## sg-006

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Standard garment — FLUX Pro best value (98% quality, 26% cost)
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1322c → +Layer-3=5510c → +Layer-2=1457c → final=8289c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Zip-up hoodie (full-length center-front zipper closure, NOT a pullover) — solid **white** body fabric with a **multi-color V-shape rainbow chevron color-block detail** at the upper chest fanning out toward the shoulders + matching V-shape rainbow chevron at each cuff and at the bottom hem waistband. **Pink** hood (solid pink/light pink hood — contrasting against the white body), drawstring at hood opening, slash hand pockets at the lower body, ribbed cuffs and waistband with the multi-color stripe pattern. Mid-weight cotton-fleece fabric. Pairs with the Mint & Lavender Sweatpants (sg-014) as a matching set. **Sold as the hoodie SKU only — the matching sweatpants are sg-014, separate SKU.** NOT a pullover. NOT a crewneck (that's sg-013 Mint & Lavender Crewneck — separate SKU). NOT a sherpa or windbreaker.

BRANDING — exactly what to render:
> Logo art canonical references:
> - SR monogram (back-neck cursive script): `data/brand-logos/sr-monogram.md`
> - Product techflat (hoodie + matching pants visible together):
>   `data/product-references/sg-006-and-sg-014-mint-lavender-set-techflat.jpeg`
>
> ### COLORWAY — Mint & Lavender chevron palette
>
> The "Mint & Lavender" colorway is a multi-color rainbow chevron stripe
> band consisting of (from outside-to-inside): **PINK + GREEN (mint) +
> LAVENDER (purple) + YELLOW** stripes arranged in a V/chevron formation.
> The catalog name "Mint & Lavender" refers to the mint-green and lavender
> stripes within the broader rainbow band — NOT to a solid mint or solid
> lavender body color. The body color is WHITE.

### Front
- **front-body** (entire white field, between the hood and the bottom hem): Solid **white** cotton-fleece body fabric. **Technique:** stitched. **Color:** white.
- **front-chevron** (large, V-shaped, ~10in wide, fanning from the upper chest outward toward both shoulders and up to the hood opening): Multi-color V-shape **rainbow chevron stripe color-block panel** — alternating pink + green + lavender + yellow stripes (~5–8 stripes total, each ~0.5–1in wide) arranged in a V/chevron pattern that meets at the center-front of the upper chest and fans up-and-out toward each shoulder. **Technique:** sublimated. **Color:** alternating pink + green + lavender + yellow stripes on white ground.
- **front-center-chest** (small, ~2in tall, just below the V-chevron meeting point on the white body field): A small **light pink rose-cluster** decoration — canonical rose-cluster art recolored to a pink-on-white tonal palette (light pink petals + dark pink-grey outlines). **Technique:** embroidered. **Color:** light pink + dark pink-grey thread on white.
- **front-zipper** (vertical center-front, full body length): Standard YKK-style center-front zipper running the full length of the body from the V-neck opening to the bottom of the ribbed waistband. **Technique:** patch (sewn-on zipper hardware). **Color:** body-tone (white teeth or near-white).
- **front-left-pocket** (vertical slash hand pocket at the lower-left body, with **pink contrast piping** along the welt edge): Slash hand pocket. **Technique:** stitched. **Color:** white body with pink piping accent.
- **front-right-pocket** (vertical slash hand pocket at the lower-right body, mirror of left): Slash hand pocket with pink contrast piping. **Technique:** stitched. **Color:** white body with pink piping.

### Back
- **back-neck** (small, ~1.5in wide, top-center just below the hood seam): The SR monogram embroidered onto the jersey in **dark grey / black cursive script**. **Technique:** embroidered. **Color:** dark grey / black thread on white.
- **back-body** (entire back field, between the hood seam and the waistband): Solid **white**, no decoration. **Technique:** stitched. **Color:** white.

### Sleeves / Hood / Hem / Other
- **hood** (full hood, ~10in tall when laid flat): Solid **pink / light pink** hood (contrast against the white body). **Technique:** stitched. **Color:** pink / light pink.
- **hood-drawstring**: White flat drawstring threaded through the hood opening. **Technique:** stitched. **Color:** white.
- **left-sleeve** (long sleeve): Solid **white** body, with a small V-shape rainbow chevron stripe panel at the upper-cuff area mirroring the front chevron. **Technique:** sublimated. **Color:** white body with chevron accent.
- **right-sleeve** (long sleeve): Mirror of left. **Technique:** sublimated. **Color:** white body with chevron accent.
- **left-cuff** (~1.5in tall ribbed cuff at wrist): Multi-color rainbow stripe band (alternating pink + green + lavender + yellow + pink stripes wrapping the cuff, ~5 stripes total). **Technique:** sublimated. **Color:** alternating pink + green + lavender + yellow.
- **right-cuff** (~1.5in tall ribbed cuff at wrist, mirror of left-cuff): Multi-color rainbow stripe band (alternating pink + green + lavender + yellow stripes wrapping the cuff, ~5 stripes total). **Technique:** sublimated. **Color:** alternating pink + green + lavender + yellow.
- **waistband** (~2in tall ribbed waistband at the bottom hem): Multi-color rainbow stripe band matching the cuff treatment, wrapping the body front-and-back at the hem. **Technique:** sublimated. **Color:** alternating pink + green + lavender + yellow.
- **collar-inside** (~1.5in × 0.5in interior tag): Branded woven size tag. **Technique:** woven-label. **Color:** brand-label palette.

---

Study the reference image carefully. This is a  called "Mint & Lavender Hoodie".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Warm charcoal (#1A1A1A) fading to deep black, hint of golden hour warmth
- Golden-warm key light upper-left, soft neutral fill, warm rim light creating a premium glow
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- NO pullover construction — this is a ZIP-UP hoodie with a full center-front zipper.
- NO solid mint or solid lavender body — the body is WHITE; the mint-green and lavender stripes are part of the multi-color chevron stripe band only.
- NO white hood — the hood is PINK / light pink (the only solid-pink major color block on the garment).
- NO single-color hood drawstring matching the hood — drawstring is WHITE on the pink hood.
- NO solid-color cuffs or waistband — cuffs and waistband carry the multi-color rainbow stripe band.
- NO contrast piping on the cuffs or waistband — those areas have the stripe band; only the slash pockets have pink piping.
- NO Black Rose three-rose-cluster as a chest emblem — the front-center chest rose is a small pink-tonal canonical rose-cluster (LIGHT PINK), not the canonical greyscale or canonical multi-color version.
- NO Love Hurts canonical roses (red multi-color cluster) — this is a Signature collection product with a pink-tonal rose treatment.
- NO Authentic Collection patch.
- NO Bridge Series photo print on the body.
- NO printed graphics other than the sublimated chevron stripes and small pink rose.
- NO half-zip placket — the zipper runs the FULL body length.
- NO embossed/debossed decoration.
- NO additional pockets on the back or on the sleeves — only the two front slash hand pockets.
- NO chest text or wordmark.
- NO contrast-color sleeve seam.
```

---

## sg-007

**Vision cache:** present
**Inferred DNA:** garment=beanie | fabric=Fine gauge ribbed knit, with a soft, matte finish. | graphic-type='silicone patch' | graphic-colors=['#2B2B2B', '#C82F3F', '#9E2531', '#4A6D4A', '#E0E0E0'] | branding-technique='Silicone patch with raised, multi-color graphic.'
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Accessory — FLUX Pro best value for simple items
**Registry template:** `accessory_front_v1`
**Prompt length:** Layer-0=1563c → +Layer-3=3057c → +Layer-2=897c → final=5517c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Classic cuffed knit beanie / cap — solid black ribbed knit fabric, single fold-up cuff at the base (~2.5–3in tall folded), rounded crown, snug head-fit. NOT a hat with a brim. NOT a baseball cap. NOT a pom-pom beanie. NOT a slouchy beanie. NOT a fitted-cap. **Sold across 4 decoration / colorway variants** that share the same base beanie but differ in the small rose graphic embroidered on the front face of the cuff. Mid-weight knit fabric.

BRANDING — exactly what to render:
> Logo art canonical references:
> - Black Rose three-rose-cluster (greyscale): `data/brand-logos/black-rose-logo.md`
> - Red Roses Cloud Cluster (LH multi-color):  `data/brand-logos/red-roses-cloud-cluster.md`
> - Product techflat (4 variants visible):     `data/product-references/sg-007-techflat.jpeg`
>
> ### COLORWAY / DECORATION VARIANTS
>
> All 4 variants share the same **black ribbed knit beanie** base. The only
> difference is the rose graphic embroidered on the front face of the cuff:
>
> - **Variant 1 — Purple/Violet rose-cluster** (small, ~1.5in tall): a
>   tonal purple-and-violet rendering of the canonical rose-cluster (three
>   roses + cloud at base + thorny vines), recolored to a purple-on-black
>   palette. **Color:** purple-violet on black.
> - **Variant 2 — White-outline rose-cluster** (small, ~1.5in tall): a
>   line-art white-thread version of the canonical rose-cluster — outlines
>   only, no fill. **Color:** white thread on black.
> - **Variant 3 — Small single red rose with cloud** (small, ~1in tall):
>   a single canonical red rose bloom (with thorny green stem and a small
>   white-and-blue cloud at the base) — minimal scale. **Color:**
>   canonical Love Hurts red + green + white-and-blue.
> - **Variant 4 — Red rose-cluster with cloud** (medium, ~2in tall):
>   the full canonical Red Roses Cloud Cluster (multiple red roses + thorny
>   green vines + white-and-blue cloud) — the larger Love Hurts canonical
>   composition. **Color:** canonical multi-color (red + green + white +
>   blue).
>
> Render the requested variant ONLY — do not place all four roses on a
> single beanie.

### Front
- **front-cuff** (small, ~1.5–2in tall, centered on the front face of the cuff fold): The selected variant's rose decoration (Variant 1, 2, 3, or 4 per the COLORWAY/DECORATION VARIANTS block above) embroidered into the cuff face. **Technique:** embroidered. **Color:** per selected variant.

### Back
- (Clean back — no decoration on the rear-cuff face or rear-crown.)

### Sleeves / Hood / Hem / Other
- **cuff** (~2.5–3in tall folded): Standard ribbed-knit cuff, folded up once. **Technique:** stitched. **Color:** black.
- **crown**: Rounded knit crown, no decoration. **Technique:** stitched. **Color:** black.
- **inside-cuff** (~1in × 0.5in interior tag): Branded woven size tag (universal SkyyRose product rule, scaled for accessory). **Technique:** woven-label. **Color:** brand-label palette.

---

ACCESSORY PRODUCT PHOTO — The Signature Beanie
Photorealistic product render of this relaxed beanie.

DETAILS:
  #1 "A detailed illustration of two blooming roses with a stem and leaves, emerging from a cloud-like base. The roses are red, the stem and leaves are green, and the base is white/light grey, all set against a dark grey/black rectangular patch."
      WHERE: Front cuff, positioned on the wearer's right side. — LOCKED POSITION, do not move
      SIZE: approximately 2.5 inches wide by 3 inches tall — LOCKED SIZE, do not enlarge or shrink
      TECHNIQUE: silicone patch
      FINISH: 3D dimensional, raised, matte finish on the silicone patch, with subtle glossy elements on the rose petals for texture.
      COLORS: #2B2B2B, #C82F3F, #9E2531, #4A6D4A, #E0E0E0
Colors:   body: #2C3A30 (matte)
  trim: #2C3A30 (matte)

PRESENTATION:
- Product only, slightly angled for dimension
- Warm charcoal (#1A1A1A) fading to deep black, hint of golden hour warmth
- Golden-warm key light upper-left, soft neutral fill, warm rim light creating a premium glow
- Tight framing — the accessory fills the frame

RULES:
  - This garment has EXACTLY 1 graphic element(s)
  - ONE graphic only — do NOT add a second logo, patch, or mark anywhere
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - Match the reference EXACTLY

DO NOT RENDER (authored canonical negatives):
- NO embroidery on the back / rear-cuff — the rose decoration is on the FRONT cuff face only.
- NO multi-color rose on Variants 1 or 2 — Variant 1 is purple-monochrome, Variant 2 is white-outline-only.
- NO mixing of variants — render only ONE rose decoration (the selected variant).
- NO contrast color on the beanie body — the body is solid black across all 4 variants.
- NO pom-pom on the crown.
- NO brim (this is a beanie, not a fitted cap or trucker hat).
- NO slouchy / oversize crown — the beanie is a snug fitted-knit silhouette.
- NO Authentic Collection patch on a beanie.
- NO SR monogram on the beanie (the SR mark is a back-neck embroidery on jerseys, not on accessories).
- NO printed graphics — branding is embroidered, not printed.
- NO contrast piping along the cuff edge.
- NO tag visible on the exterior (interior size-tag only).
```

---

## sg-009

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Standard garment — FLUX Pro best value (98% quality, 26% cost)
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1317c → +Layer-3=5044c → +Layer-2=1558c → final=7919c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Sherpa-lined zip-front jacket — solid **black** nylon-windbreaker-style exterior shell with full-length center-front zipper closure and a **white / cream sherpa fleece interior lining** that wraps the entire interior body, sleeves, and stand-up collar. Visible white-sherpa contrast at the front placket, sleeve cuffs, hem, and stand-up collar opening when the jacket is worn open. Two patch hand pockets at the lower body. Stand-up funnel-neck collar (NOT a hood). Small interior brand woven label at the back-neck. Mid-weight to outerwear weight. NOT a pullover. NOT a hoodie (no hood). NOT a sherpa-exterior coat (the sherpa is the INTERIOR lining; the exterior is smooth black nylon-style fabric). NOT a fully-reversible jacket (the rose-cluster embroidery is exterior-only, so it cannot be worn inside-out as a finished look). NOT a windbreaker set (this is the jacket alone, no matching pants).

BRANDING — exactly what to render:
> Logo art canonical references:
> - Red Roses Cloud Cluster (left-chest exterior embroidery): `data/brand-logos/red-roses-cloud-cluster.md`
> - SR monogram / brand woven label (interior back-neck): `data/brand-logos/sr-monogram.md`
> - Product reference exterior front (rose-cluster placement visible):
>   `data/product-references/sg-009-sherpa-front.jpeg`
> - Product reference interior detail (sherpa lining + brand label visible):
>   `data/product-references/sg-009-sherpa-interior.jpeg`

### Front
- **front-body** (entire black exterior field, between the stand-up collar and the bottom hem): Solid **black** nylon-style smooth shell fabric. **Technique:** stitched. **Color:** black.
- **front-left-chest** (~3in tall, on wearer's left chest, just right of the center-front zipper, ~4in below the stand-up collar): Canonical **Red Roses Cloud Cluster** logo embroidered onto the black exterior — three red roses with kelly-green stems and thorny vines, wrapping a small white-and-light-blue cumulus cloud at the base. Full-color thread embroidery. **Technique:** embroidered. **Color:** red petals + dark-red shading + kelly-green stems + white cloud + pale-blue cloud-shading thread on black.
- **front-zipper** (vertical center-front, full body length from stand-up collar opening to bottom hem): Standard center-front zipper running the full length of the body. **Technique:** patch. **Color:** body-tone hardware (black or near-black teeth).
- **front-left-pocket** (patch hand pocket at the lower-left body, ~6in × 5in, sewn-on patch construction with horizontal welt opening): Patch hand pocket. **Technique:** stitched. **Color:** black, matching the body.
- **front-right-pocket** (patch hand pocket at the lower-right body, mirror of left): Patch hand pocket. **Technique:** stitched. **Color:** black, matching the body.

### Back
- **back-body** (entire black exterior back field, between the stand-up collar seam and the bottom hem): Solid **black** nylon-style shell, no decoration. **Technique:** stitched. **Color:** black.
- **back-collar-inside** (small, ~1.5in × 0.5in interior tag at the back-neck, visible only when the collar is folded open): Branded **SR monogram** woven label — small rectangular woven brand label carrying the canonical SR cursive monogram. **Technique:** woven-label. **Color:** brand-label palette (black ground with white SR script, or matching brand label specification).

### Sleeves / Collar / Hem / Other
- **left-sleeve** (long sleeve, ~24in from shoulder seam to cuff): Solid **black** nylon-style shell exterior with white sherpa fleece interior lining. **Technique:** stitched. **Color:** black exterior with white-sherpa interior.
- **right-sleeve** (mirror of left): Solid black exterior with white sherpa interior lining. **Technique:** stitched. **Color:** black exterior with white-sherpa interior.
- **left-cuff** (~2in cuff at wrist, finished black-exterior cuff with the white sherpa lining peeking at the cuff opening): Black ribbed or finished cuff. **Technique:** stitched. **Color:** black with white-sherpa interior peek.
- **right-cuff** (mirror of left-cuff): Black finished cuff. **Technique:** stitched. **Color:** black with white-sherpa interior peek.
- **collar** (~2.5in tall stand-up funnel-neck collar around the entire neck opening): Black nylon-style exterior with white sherpa interior lining. **Technique:** stitched. **Color:** black exterior with white-sherpa interior.
- **hem** (~1in finished bottom hem along the entire bottom edge of the body): Clean finished hem on the black exterior with the white sherpa interior visible from below when the jacket is open. **Technique:** stitched. **Color:** black with white-sherpa interior.
- **interior-lining** (full-body interior lining covering the entire inside surface of the body and sleeves): Plush **white / cream sherpa fleece** lining throughout the interior. **Technique:** stitched. **Color:** white / cream sherpa fleece.

---

Study the reference image carefully. This is a  called "The Sherpa Jacket".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Warm charcoal (#1A1A1A) fading to deep black, hint of golden hour warmth
- Golden-warm key light upper-left, soft neutral fill, warm rim light creating a premium glow
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- NO hood — this is a STAND-UP COLLAR jacket, not a hoodie. There is no hood, no drawstring, no hood-lining seam.
- NO contrast-color exterior panels — the exterior is **entirely black** front, back, and sleeves. No white panels, no color-blocking, no rainbow chevron, no sublimated print.
- NO decoration on the back — the back exterior is plain solid black. The only back element is the small interior brand woven label at the back-neck.
- NO sherpa visible on the exterior — the sherpa is **interior lining only**. The exterior is smooth black nylon-style fabric. Do NOT render a sherpa-exterior coat.
- NO chevron stripes, no rainbow color-block, no V-shape stripe panels.
- NO Bridge Series photo print on the body.
- NO Authentic Collection patch (no NFL / NBA / Hockey patch).
- NO Black Rose greyscale rose-cluster — the chest rose is the canonical RED Roses Cloud Cluster (full-color red), not the greyscale variant.
- NO chest text or wordmark — the only chest decoration is the embroidered rose-cluster.
- NO additional pockets on the back, sleeves, or chest — only the two front patch hand pockets.
- NO decorative buttons — closure is the center-front zipper only.
- NO half-zip placket — the zipper runs the FULL body length from stand-up collar opening to bottom hem.
- NO drawstring or cordlock at the hem or collar.
- NO embossed or debossed decoration anywhere.
- NO printed graphics — all decoration is embroidered or woven.
- NO contrast piping anywhere (no pink piping, no colored piping).
```

---

## sg-011

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Standard garment — FLUX Pro best value (98% quality, 26% cost)
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1326c → +Layer-3=1188c → +Layer-2=883c → final=3397c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Classic crew-neck T-shirt, upper body only. NOT a crewneck sweatshirt, NOT a hoodie, NOT a jersey, NOT a long-sleeve. Short sleeves, ribbed crew neckline, no buttons, no hood, no kangaroo pocket. White 100% cotton construction.

BRANDING — exactly what to render:
> The SR monogram art is defined in `data/brand-logos/sr-monogram.md` and is identical across all products that reference it. Do NOT inline the monogram's visual description here — only the technique, region, dimensions, color/colorway, and any product-specific application notes.

### Front
- **front-left-chest** (~1.5in wide × ~1.5in tall): SR monogram (see logo_reference). Small, minimal placement. **Technique:** embroidered. **Color/Colorway:** white thread on white fabric — tonal, only visible under directional light where thread texture catches.

### Sleeves / Collar / Hem / Other
- **collar-inside** (back neck, ~1.5in wide × ~0.5in tall): SkyyRose woven brand label. **Technique:** woven-label. **Color/Colorway:** white/silver label with woven brand text on white ground.

---

Study the reference image carefully. This is a  called "Original Label Tee (White)".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Warm charcoal (#1A1A1A) fading to deep black, hint of golden hour warmth
- Golden-warm key light upper-left, soft neutral fill, warm rim light creating a premium glow
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- No back graphics of any kind — back is completely plain white fabric.
- No chest graphics larger than 2 inches — the only front decoration is the small left-chest SR monogram.
- No sleeve printing, embroidery, or decoration of any kind.
- No embossed or debossed relief on the chest — the technique is embroidery, not tonal impression.
- No contrasting colored thread — the front-left-chest embroidery is white-on-white tonal, not gold, black, or rose-gold.
- No graphic fills, no printed rose illustrations, no screen-printed text anywhere on the body.
- No front-right-chest decoration — the SR monogram is left-chest only.
- No puff-print, heat-transfer, or vinyl decoration.
- No visible label on the outside of the garment — only inside back collar.
- No large center-chest logo — this is a minimal label tee, not a graphic tee.
```

---

## sg-012

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Standard garment — FLUX Pro best value (98% quality, 26% cost)
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1327c → +Layer-3=1211c → +Layer-2=975c → final=3513c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Classic crew-neck T-shirt, upper body only. NOT a crewneck sweatshirt, NOT a hoodie, NOT a jersey, NOT a long-sleeve. Short sleeves, ribbed crew neckline, no buttons, no hood, no kangaroo pocket. Orchid (soft purple-pink) 100% cotton construction.

BRANDING — exactly what to render:
> The SR monogram art is defined in `data/brand-logos/sr-monogram.md` and is identical across all products that reference it. Do NOT inline the monogram's visual description here — only the technique, region, dimensions, color/colorway, and any product-specific application notes.

### Front
- **front-left-chest** (~1.5in wide × ~1.5in tall): SR monogram (see logo_reference). Small, minimal placement. **Technique:** embroidered. **Color/Colorway:** rose-gold thread on orchid fabric — warm metallic shimmer against the soft purple-pink base.

### Sleeves / Collar / Hem / Other
- **collar-inside** (back neck, ~1.5in wide × ~0.5in tall): SkyyRose woven brand label. **Technique:** woven-label. **Color/Colorway:** white/rose-gold label with woven brand text on orchid-compatible ground.

---

Study the reference image carefully. This is a  called "Original Label Tee (Orchid)".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Warm charcoal (#1A1A1A) fading to deep black, hint of golden hour warmth
- Golden-warm key light upper-left, soft neutral fill, warm rim light creating a premium glow
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- No back graphics of any kind — back is completely plain orchid fabric.
- No chest graphics larger than 2 inches — the only front decoration is the small left-chest SR monogram.
- No sleeve printing, embroidery, or decoration of any kind.
- No embossed or debossed relief on the chest — the technique is embroidery, not tonal impression.
- No white thread on this garment — the front-left-chest embroidery is rose-gold thread, not white or tonal.
- No graphic fills, no printed rose illustrations, no screen-printed text anywhere on the body.
- No front-right-chest decoration — the SR monogram is left-chest only.
- No puff-print, heat-transfer, or vinyl decoration.
- No visible label on the outside of the garment — only inside back collar.
- No large center-chest logo — this is a minimal label tee, not a graphic tee.
- No purple or lavender thread — thread color is rose-gold metallic only, not matching the orchid base.
```

---

## sg-013

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Standard garment — FLUX Pro best value (98% quality, 26% cost)
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1324c → +Layer-3=4628c → +Layer-2=1600c → final=7552c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Crew-neck pullover sweatshirt — solid **mint green / seafoam-green** body fabric throughout (front, back, sleeves) with **NO hood, NO zipper, NO color-blocking, NO chevron stripes, NO contrast panels**. Long sleeves, ribbed crew-neck, ribbed cuffs at wrists, ribbed waistband at hem (all in matching mint). Mid-weight cotton-fleece fabric. NOT a hoodie (no hood — this is the no-hood sibling of the Mint & Lavender Hoodie sg-006). NOT a zip-up (pullover construction, no zipper). NOT a chevron-rainbow garment (the sg-006 hoodie has rainbow chevron stripes; this crewneck does NOT — it is a clean solid-mint body with embroidered rose decoration only). NOT a tee (this is a heavier sweatshirt with ribbed cuffs/waistband). The matching mint sweatpants visible in the techflat are sold as a separate companion piece — this dossier covers ONLY the crewneck top.

BRANDING — exactly what to render:
> Logo art canonical references:
> - Canonical rose-cluster art (recolored to lavender / purple per COLORWAY OVERRIDE): `data/brand-logos/red-roses-cloud-cluster.md`
> - Product reference techflat (crewneck top + matching pants visible together):
>   `data/product-references/sg-013-mint-lavender-crewneck-set-techflat.jpeg`
>
> ### COLORWAY OVERRIDE — Lavender / Purple rose-cluster on mint ground
>
> The rose-cluster on the front chest and back-yoke uses the **canonical
> rose-cluster composition** (three roses, stems, thorny vines, cloud at
> base) but RECOLORED to a **LAVENDER / PURPLE** palette:
> - **Petals:** lavender / medium-purple / deep-purple gradient (NOT red,
>   NOT greyscale).
> - **Stems and leaves:** silver-grey or cool grey-purple (NOT kelly green).
> - **Cloud at base:** white-and-light-grey (matching the canonical cloud).
> - **Outlines:** dark purple-grey or black ink outlines.
>
> The catalog name "Mint & Lavender" describes BODY = mint green +
> ROSE-CLUSTER ART = lavender. The body is solid mint; the lavender accent
> is carried entirely by the rose-cluster embroidery on chest and back.

### Front
- **front-body** (entire mint field, between the crew-neck collar and the waistband): Solid **mint green / seafoam green** cotton-fleece body fabric. **Technique:** stitched. **Color:** mint green.
- **front-center-chest** (~5–6in tall, ~4in wide, centered on the chest just below the crew-neck opening): Large **lavender / purple rose-cluster embroidery** — canonical three-rose-cluster composition recolored to a lavender / purple palette per the COLORWAY OVERRIDE above (lavender petals + silver-grey stems and leaves + white-and-light-grey cloud at base + dark purple-grey outlines). Significant chest-emblem scale, the visual focal point of the front. **Technique:** embroidered. **Color:** lavender + medium-purple + deep-purple thread + silver-grey stem thread + white cloud thread on mint ground.

### Back
- **back-yoke** (~2in tall, ~1.5in wide, top-center back just below the crew-neck collar seam): Small lavender / purple rose-cluster embroidery — same canonical composition as the front-center-chest emblem but at miniature scale (single small accent emblem). **Technique:** embroidered. **Color:** lavender + medium-purple + silver-grey + white thread on mint ground.
- **back-body** (entire back field, between the crew-neck collar seam and the waistband): Solid **mint green**, no other decoration. **Technique:** stitched. **Color:** mint green.

### Sleeves / Collar / Hem / Other
- **left-sleeve** (long sleeve, ~24in from shoulder seam to cuff): Solid **mint green** cotton-fleece, no decoration. **Technique:** stitched. **Color:** mint green.
- **right-sleeve** (mirror of left): Solid mint green, no decoration. **Technique:** stitched. **Color:** mint green.
- **left-cuff** (~2in tall ribbed cuff at wrist): Solid mint-green ribbed cuff. **Technique:** stitched. **Color:** mint green.
- **right-cuff** (mirror of left-cuff): Solid mint-green ribbed cuff. **Technique:** stitched. **Color:** mint green.
- **collar** (~1in tall ribbed crew-neck collar around the entire neck opening): Solid mint-green ribbed crew-neck. **Technique:** stitched. **Color:** mint green.
- **waistband** (~2in tall ribbed waistband at the bottom hem): Solid mint-green ribbed waistband wrapping front-and-back. **Technique:** stitched. **Color:** mint green.
- **collar-inside** (~1.5in × 0.5in interior tag at the back-neck below the crew-neck seam): Branded woven size / composition label. **Technique:** woven-label. **Color:** brand-label palette.

---

Study the reference image carefully. This is a  called "Mint & Lavender Crewneck".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Warm charcoal (#1A1A1A) fading to deep black, hint of golden hour warmth
- Golden-warm key light upper-left, soft neutral fill, warm rim light creating a premium glow
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- NO hood — this is a CREWNECK, not a hoodie. The Mint & Lavender Hoodie (sg-006) is the hooded sibling; this is the no-hood variant.
- NO zipper — pullover construction, no closure.
- NO chevron rainbow stripes — the sg-006 hoodie has multi-color V-shape rainbow chevron stripes; this crewneck does NOT. The body is solid mint front and back.
- NO multi-color stripe band on cuffs, collar, or waistband — those are SOLID MINT to match the body. The sg-006 hoodie has multi-color stripe cuffs/waistband; this crewneck does NOT.
- NO white body — the body is solid MINT green. (The sg-006 hoodie body is white with mint as a stripe color; this crewneck is the inverse — solid mint body.)
- NO solid lavender body — body is MINT; lavender is the rose-cluster accent only.
- NO red rose-cluster — the rose-cluster is RECOLORED LAVENDER / PURPLE, not the canonical red.
- NO greyscale rose-cluster — the rose-cluster is RECOLORED LAVENDER / PURPLE, not the canonical Black Rose greyscale.
- NO Black Rose three-rose-cluster as a chest emblem (in greyscale) — the chest rose is the lavender-recolored canonical.
- NO Authentic Collection patch (no NFL / NBA / Hockey patch).
- NO Bridge Series photo print on the body.
- NO chest text or wordmark — the only chest decoration is the embroidered rose-cluster.
- NO embossed or debossed decoration.
- NO printed graphics — all decoration is embroidered.
- NO additional pockets — this is a clean pullover crewneck with no pockets.
- NO contrast piping anywhere.
- NO sleeve-stripe tape or contrast sleeve seam.
```

---

## sg-014

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Standard garment — FLUX Pro best value (98% quality, 26% cost)
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1326c → +Layer-3=3940c → +Layer-2=1070c → final=6336c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Athletic-cut full-length sweatpants — solid **white** body fabric with a **multi-color V-shape rainbow chevron color-block detail** at each upper-thigh / hip area + matching multi-color stripe band at the waistband and at each ankle cuff. White flat drawstring at the waistband, vertical slash hand pockets with **pink contrast piping**, slim athletic fit. Mid-weight cotton-fleece fabric. Pairs with the Mint & Lavender Hoodie (sg-006) as a matching set. **Sold as the sweatpants SKU only — the matching hoodie is sg-006, separate SKU.** NOT joggers (these are full-length sweatpants with the multi-color chevron, distinct from the simpler joggers in other SKUs). NOT shorts. NOT a track pant.

BRANDING — exactly what to render:
> Logo art canonical references:
> - Product techflat (hoodie + matching pants visible together):
>   `data/product-references/sg-006-and-sg-014-mint-lavender-set-techflat.jpeg`
>
> ### COLORWAY — Mint & Lavender chevron palette
>
> Same multi-color chevron palette as sg-006 hoodie: **PINK + GREEN
> (mint) + LAVENDER + YELLOW** stripes arranged in V/chevron formation.
> Body fabric is WHITE; the chevron is the accent decoration.

### Front
- **front-body** (entire white field, between waistband and ankle cuffs): Solid **white** cotton-fleece body fabric. **Technique:** stitched. **Color:** white.
- **front-thigh-chevron** (large, V-shaped, ~6–7in wide, on each upper-thigh / hip area): Multi-color V-shape **rainbow chevron stripe color-block panel** on each upper thigh — alternating pink + green + lavender + yellow stripes (~5–8 stripes total per panel) arranged in a V/chevron pattern. The two thigh panels mirror each other across the center-front. **Technique:** sublimated. **Color:** alternating pink + green + lavender + yellow stripes on white ground.
- **front-center-waistband** (small, ~2in tall, just below the waistband at the center-front): A small **light pink rose-cluster** decoration — canonical rose-cluster art recolored to a pink-on-white tonal palette (light pink petals + dark pink-grey outlines), matching the small rose on the sg-006 hoodie. **Technique:** embroidered. **Color:** light pink + dark pink-grey thread on white.
- **front-left-pocket** (vertical slash hand pocket on wearer's left, with **pink contrast piping** along the welt edge): Slash hand pocket. **Technique:** stitched. **Color:** white body with pink piping accent.
- **front-right-pocket** (vertical slash hand pocket on wearer's right, mirror of left): Slash hand pocket with pink contrast piping. **Technique:** stitched. **Color:** white body with pink piping.
- **drawstring** (~24in long, threaded through the waistband): White flat drawstring. **Technique:** stitched. **Color:** white.

### Back
- **back-body** (entire back field, waistband to ankle): Solid **white**, no decoration. **Technique:** stitched. **Color:** white.

### Sleeves / Hood / Hem / Other
- **waistband** (~2in tall ribbed waistband at the top): Multi-color rainbow stripe band matching the sg-006 hoodie waistband (alternating pink + green + lavender + yellow stripes wrapping front-and-back). **Technique:** sublimated. **Color:** alternating pink + green + lavender + yellow.
- **left-ankle-cuff** (~1.5in tall ribbed cuff at ankle): Multi-color rainbow stripe band (matching the sg-006 hoodie cuff treatment). **Technique:** sublimated. **Color:** alternating pink + green + lavender + yellow.
- **right-ankle-cuff** (~1.5in tall ribbed cuff at ankle, mirror of left-ankle-cuff): Multi-color rainbow stripe band (matching the sg-006 hoodie cuff treatment). **Technique:** sublimated. **Color:** alternating pink + green + lavender + yellow.
- **inside-waistband** (~1.5in × 0.5in interior tag): Branded woven size tag. **Technique:** woven-label. **Color:** brand-label palette.

---

Study the reference image carefully. This is a  called "Mint & Lavender Sweatpants".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Warm charcoal (#1A1A1A) fading to deep black, hint of golden hour warmth
- Golden-warm key light upper-left, soft neutral fill, warm rim light creating a premium glow
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- NO solid mint or solid lavender body — body is WHITE.
- NO solid-color stripe band — the band is multi-color rainbow chevron.
- NO black drawstring — drawstring is WHITE.
- NO contrast-color body — body is solid white front and back.
- NO chevron on the back — chevron decorations are on the FRONT thighs only.
- NO solid-color cuffs or waistband — those areas have the stripe band.
- NO contrast piping anywhere except on the slash pockets (pink piping).
- NO Black Rose three-rose-cluster as a thigh emblem — the front-center small rose is light pink tonal.
- NO Love Hurts canonical roses.
- NO Authentic Collection patch.
- NO Bridge Series photo print on the body.
- NO printed graphics other than the sublimated chevron stripes and small pink rose.
- NO embossed/debossed decoration.
- NO back pockets — only the two front slash hand pockets.
- NO zipper closures on the pockets — open welt slash pockets.
- NO ankle taper without a cuff — the pants terminate cleanly at the ribbed multi-color cuff at ankle level.
```

---

## sg-015

**Vision cache:** MISSING
**Inferred DNA:** (no vision cache — generator prompt would lack inferred DNA detail)
**Engine route:** `flux-pro` (fal-ai/flux-pro/v1.1) — Standard garment — FLUX Pro best value (98% quality, 26% cost)
**Registry template:** `front_v2_narrative`
**Prompt length:** Layer-0=1319c → +Layer-3=8892c → +Layer-2=2200c → final=12411c

### Final prompt sent to generator

```
CANONICAL DESIGN SPEC (authored truth — overrides any conflicting inferred description below):

GARMENT TYPE (must match exactly):
Two-piece matching set sold as a single SKU — **lightweight nylon zip-front hooded windbreaker JACKET + matching nylon track-style PANTS**. Both pieces are constructed from smooth lightweight **nylon windbreaker fabric** (NOT cotton-fleece — this is the lighter water-resistant sibling of the Mint & Lavender Hoodie set). Solid **white** body on both pieces with a **multi-color V-shape rainbow chevron color-block detail** at the upper chest (jacket) and at each upper-thigh (pants), **PINK contrast hood** on the jacket, **multi-color rainbow stripe bands** at the jacket cuffs / hem and the pants waistband / ankle cuffs. The jacket has a full-length center-front zipper. The pants have a white drawstring waistband and slash hand pockets. NOT cotton-fleece (this is the windbreaker variant, not the cousin sg-006 fleece hoodie + sg-014 fleece pants). NOT a single-piece SKU — this is sold as the matching JACKET + PANTS set together. NOT a fleece hoodie (different fabric, different weight, different construction). NOT solid black (catalog Color field reads "Black" but the techflat colorway is **WHITE body + PINK hood + multi-color rainbow chevron** — render the techflat colorway, not the catalog field).

BRANDING — exactly what to render:
> Logo art canonical references:
> - SR monogram (large back-yoke logo on the jacket): `data/brand-logos/sr-monogram.md`
> - Canonical rose-cluster art (recolored to pink per COLORWAY OVERRIDE — small chest accent): `data/brand-logos/red-roses-cloud-cluster.md`
> - Product reference techflat (jacket front-and-back + pants front-and-back, all four views visible):
>   `data/product-references/sg-015-windbreaker-set-techflat.jpeg`
>
> ### COLORWAY — Mint & Lavender chevron palette in nylon
>
> Same multi-color rainbow chevron palette as the sg-006 hoodie + sg-014
> sweatpants set: **PINK + GREEN + LAVENDER + YELLOW** stripes arranged
> in V/chevron formation. Body fabric is WHITE; the chevron is the accent.
> Hood is solid PINK (matching the sg-006 contrast hood). The small chest
> rose-cluster uses the canonical rose-cluster composition recolored to
> a **PINK** palette (matching the sg-006 small chest rose).
>
> ### CATALOG NOTE
>
> The CSV Color field for sg-015 reads "Black", but the techflat shows
> the WHITE colorway with rainbow chevron and pink hood. Render against
> the techflat (white + chevron + pink hood) — the catalog field is
> pending update. If a separate black colorway is later confirmed, that
> would be a sibling dossier with a `colorway` frontmatter override.

### Front
- **front-body-jacket** (entire white jacket field, between the hood seam and the bottom hem): Solid **white** nylon windbreaker shell fabric. **Technique:** stitched. **Color:** white.
- **front-chevron-jacket** (large V-shape, ~10in wide, fanning from the upper chest outward toward both shoulders and up to the hood opening): Multi-color **rainbow chevron stripe color-block panel** — alternating pink + green + lavender + yellow stripes (~5–8 stripes, each ~0.5–1in wide) arranged in a V/chevron formation that meets at the center-front upper-chest and fans up-and-out toward each shoulder. **Technique:** sublimated. **Color:** alternating pink + green + lavender + yellow on white ground.
- **front-center-chest-jacket** (small, ~2in tall, just below the V-chevron meeting point on the white body): Small **pink rose-cluster** decoration — canonical rose-cluster art recolored to a pink-on-white tonal palette (pink / coral petals + grey-pink outlines + white cloud) matching the small chest rose on the sg-006 hoodie. **Technique:** embroidered. **Color:** pink + coral + grey-pink thread on white.
- **front-zipper-jacket** (vertical center-front, full body length from hood opening to waistband hem): Standard center-front zipper running the full length of the jacket body. **Technique:** patch. **Color:** body-tone hardware (white or near-white teeth).
- **front-left-pocket-jacket** (vertical slash hand pocket at the lower-left jacket body, with **pink contrast piping** along the welt edge): Slash hand pocket. **Technique:** stitched. **Color:** white body with pink piping accent.
- **front-right-pocket-jacket** (vertical slash hand pocket at the lower-right jacket body, mirror of left): Slash hand pocket with pink contrast piping. **Technique:** stitched. **Color:** white body with pink piping.
- **front-body-pants** (entire white pants field, between the waistband and ankle cuffs): Solid **white** nylon windbreaker fabric. **Technique:** stitched. **Color:** white.
- **front-thigh-chevron-pants** (V-shape, ~6–7in wide, on each upper-thigh / hip area, mirroring across the center-front): Multi-color V-shape **rainbow chevron stripe color-block panel** on each upper thigh — alternating pink + green + lavender + yellow stripes arranged in V/chevron pattern. **Technique:** sublimated. **Color:** alternating pink + green + lavender + yellow on white ground.
- **front-left-pocket-pants** (vertical slash hand pocket on wearer's left thigh, with **pink contrast piping** along the welt edge): Slash hand pocket. **Technique:** stitched. **Color:** white body with pink piping.
- **front-right-pocket-pants** (vertical slash hand pocket on wearer's right thigh, mirror of left): Slash hand pocket with pink contrast piping. **Technique:** stitched. **Color:** white body with pink piping.
- **drawstring-pants** (~24in long, threaded through the pants waistband): White flat drawstring. **Technique:** stitched. **Color:** white.

### Back
- **back-yoke-jacket** (~5–6in tall, ~3–4in wide, centered on the upper back below the hood seam): Large **SR monogram** in cursive script — prominent back-yoke logo placement (significantly larger and more visible than the small back-neck SR on the sg-006 fleece hoodie). **Technique:** embroidered. **Color:** dark-grey / black / metallic thread on white ground.
- **back-body-jacket** (entire white back field, below the SR monogram and above the waistband): Solid **white**, no other decoration. **Technique:** stitched. **Color:** white.
- **back-body-pants** (entire white pants back field, between waistband and ankle cuffs): Solid **white**, no decoration. **Technique:** stitched. **Color:** white.

### Sleeves / Hood / Hem / Other
- **hood-jacket** (full hood with drawstring, ~10in tall when laid flat): Solid **pink / light pink** contrast hood. **Technique:** stitched. **Color:** pink / light pink.
- **hood-drawstring-jacket** (white flat drawstring threaded through the hood opening): White drawstring. **Technique:** stitched. **Color:** white.
- **left-sleeve-jacket** (long nylon sleeve): Solid white nylon body with a small V-shape rainbow chevron stripe panel at the upper-cuff / forearm area mirroring the front-chevron color story. **Technique:** sublimated. **Color:** white body with chevron accent.
- **right-sleeve-jacket** (mirror of left-sleeve): Solid white with chevron accent at the upper-cuff. **Technique:** sublimated. **Color:** white body with chevron accent.
- **left-cuff-jacket** (~1.5in tall ribbed cuff at wrist): Multi-color rainbow stripe band (alternating pink + green + lavender + yellow stripes wrapping the cuff). **Technique:** sublimated. **Color:** alternating pink + green + lavender + yellow.
- **right-cuff-jacket** (mirror of left-cuff-jacket): Multi-color rainbow stripe band. **Technique:** sublimated. **Color:** alternating pink + green + lavender + yellow.
- **waistband-jacket** (~2in tall ribbed band at the jacket bottom hem): Multi-color rainbow stripe band wrapping the jacket front-and-back at the hem. **Technique:** sublimated. **Color:** alternating pink + green + lavender + yellow.
- **waistband-pants** (~2in tall ribbed band at the pants top): Multi-color rainbow stripe band matching the jacket waistband (alternating pink + green + lavender + yellow stripes wrapping front-and-back). **Technique:** sublimated. **Color:** alternating pink + green + lavender + yellow.
- **left-ankle-cuff-pants** (~1.5in tall ribbed band at the left ankle): Multi-color rainbow stripe band matching the jacket cuff treatment. **Technique:** sublimated. **Color:** alternating pink + green + lavender + yellow.
- **right-ankle-cuff-pants** (mirror of left-ankle-cuff-pants): Multi-color rainbow stripe band. **Technique:** sublimated. **Color:** alternating pink + green + lavender + yellow.
- **collar-inside-jacket** (~1.5in × 0.5in interior tag at the back-neck of the jacket): Branded woven size / composition label. **Technique:** woven-label. **Color:** brand-label palette.
- **inside-waistband-pants** (~1.5in × 0.5in interior tag at the back-waistband of the pants): Branded woven size / composition label. **Technique:** woven-label. **Color:** brand-label palette.

---

Study the reference image carefully. This is a  called "The Windbreaker Set".

Your job: generate a photorealistic e-commerce product photo showing ONLY the front of this garment.

The garment is . It has EXACTLY 0 graphic element(s):
  NONE — this is a plain garment

These graphics are LOCKED — same size, same position, same colors as the reference. Do not move, resize, or duplicate them.

Color spec:
  Solid black (#000000)

Construction:


Render the garment floating on an invisible form (no model, no mannequin) with:
- Warm charcoal (#1A1A1A) fading to deep black, hint of golden hour warmth
- Golden-warm key light upper-left, soft neutral fill, warm rim light creating a premium glow
- Photorealistic fabric texture with natural 3D drape and shadow

CRITICAL NEGATIVE RULES:
  - This garment has EXACTLY 0 graphic element(s)
  - NO logos, NO text, NO patches, NO embroidery — completely blank
  - Do NOT change sizes — if spec says 4.5 inches, render 4.5 inches
  - Do NOT move positions — if spec says left chest, it stays left chest
  - Do NOT invent pockets, stripes, panels, or details not in the reference
  - Do NOT add team names, athlete names, sponsor logos, or league marks
  - FRONT VIEW ONLY — do not show the back
  - Match the reference EXACTLY — this is luxury fashion, accuracy is everything

DO NOT RENDER (authored canonical negatives):
- NO cotton-fleece — this is **NYLON WINDBREAKER fabric** (lightweight, smooth, water-resistant). The sg-006 hoodie + sg-014 sweatpants set is the cotton-fleece cousin; this set is the NYLON WINDBREAKER variant.
- NO solid black exterior — although the catalog Color field reads "Black", the techflat shows the **WHITE colorway with rainbow chevron and pink hood**. Render the techflat, not the catalog field.
- NO solid hood matching body — the hood is **PINK** contrast against the white body.
- NO single-color drawstring matching the hood — drawstring is WHITE on the pink hood.
- NO solid-color cuffs or waistbands — cuffs and waistbands carry the multi-color rainbow stripe band on BOTH the jacket and the pants.
- NO contrast piping on the cuffs or waistband — those areas have the rainbow stripe band; only the slash pockets carry pink piping.
- NO chevron on the back of the jacket or back of the pants — chevron decorations are on the FRONT only (front-chest jacket, front-thighs pants, sleeve forearm panels).
- NO Black Rose three-rose-cluster as a chest emblem (greyscale) — the front-center-chest-jacket rose is a small pink-tonal canonical rose-cluster.
- NO Love Hurts canonical RED rose-cluster — this Signature set uses the pink-recolored variant.
- NO Authentic Collection patch (no NFL / NBA / Hockey patch).
- NO Bridge Series photo print on either piece.
- NO embossed or debossed decoration.
- NO chest text or wordmark on the jacket front (the only front decoration is the chevron + small pink rose).
- NO printed graphics other than the sublimated chevron stripes and stripe bands.
- NO half-zip placket on the jacket — the zipper runs the FULL body length.
- NO additional pockets on the back of the jacket, pants, or sleeves — only the two front slash hand pockets per piece.
- NO sherpa lining (this is a windbreaker, not a sherpa-lined jacket — sg-009 is the sherpa-lined sibling).
- NO solid back yoke without the SR monogram — the back yoke MUST carry the large SR monogram embroidery (this is the main back-decoration distinguishing the windbreaker set from the sg-006 fleece hoodie which has only a small back-neck SR).
```

---

