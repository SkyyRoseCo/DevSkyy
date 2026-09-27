---
sku: REPLACE-WITH-SKU
name: Replace With Product Display Name
collection: black-rose
logo_reference: data/brand-logos/three-rose-cluster.md
---

<!--
SkyyRose Product Design Dossier
================================

Single source of truth for what is on this product. The 3D RAS pipeline reads
this file verbatim into the Gemini prompt and attaches the canonical brand
logo (per `logo_reference` above) as an additional image reference.

Authoring rules:
  1. Author from the actual physical product or canonical product photos.
  2. NO ML pre-fill — Gemini Flash hallucinates per-region detail.
  3. Be exhaustive on Front / Back / Sleeves / Collar / Hem / Other.
  4. The NEGATIVE section is a safety rail — list every conflation we want
     to prevent. Better to over-list than under-list.
  5. Two-eyes review required before commit (Corey confirms each line).

Allowed `collection` values:
  - black-rose
  - love-hurts
  - signature
  - kids-capsule

Allowed `logo_reference` values (one per dossier — the canonical brand logo
used on this product):
  - data/brand-logos/three-rose-cluster.md
  - data/brand-logos/love-hurts-logo.md       (TBD)
  - data/brand-logos/rose-gold-rose.md       (Signature first rose; only when on the product)
  - data/brand-logos/kids-capsule-logo.md     (TBD)

Product logo references must identify the marks actually used on that SKU.
Register the logo identity and its placement from product evidence; collection
membership alone never establishes a garment logo.

Allowed `technique` values (controlled vocabulary — case-sensitive):
  - embossed         (raised relief into fabric, tonal)
  - debossed         (recessed into fabric, tonal)
  - embroidered      (stitched thread, raised, contrasting color)
  - embroidered-patch (embroidered design on a separate fabric patch sewn on)
  - printed          (flat printed graphic — DTG, screen-print, vinyl)
  - screen-print     (flat ink layer, traditional silkscreen)
  - sublimated       (dye merged into fabric, no surface texture)
  - stitched         (decorative stitching, no thread image — e.g. binding)
  - patch            (sewn-on fabric patch, no embroidery — e.g., woven label)
  - woven-label      (small brand label woven on a fabric tag)
  - puff-print       (raised foam printed graphic)
  - heat-transfer    (vinyl applied with heat, smooth surface)
  - laser-engraved   (burned/etched into surface — leather, wood, etc.)
  - silicone         (raised silicone applied to fabric, single-color)
  - silicone-appliqué (raised silicone patch with multi-color art preserved)

Allowed `region` values (controlled vocabulary):
  - front-chest, front-left-chest, front-right-chest
  - front-belly, front-hem, front-pocket
  - back-upper, back-center, back-lower, back-yoke
  - left-sleeve, right-sleeve, left-cuff, right-cuff
  - collar-outside, collar-inside, neck-tape
  - hem, side-seam, left-thigh, right-thigh
  - hood-back, hood-inside, drawstring
  - hat-front, hat-side, hat-back
  - inside-waistband
-->

# Replace With Product Display Name

**Garment type lock:** Replace with one-line lock. Example for a crewneck:
"Crewneck sweatshirt, upper body only. NOT a jersey, NOT a hoodie, NOT a jacket.
Round neckline, no buttons, no hood." — every dossier MUST include both an
explicit garment type AND at least one "NOT a {…}" disambiguator.

## Branding — exactly what IS on this product

> The brand logo art for any "logo" entry is defined ONCE in
> `{logo_reference}` and is identical across all products. Do NOT inline the
> logo's visual description here — only the technique, region, dimensions,
> color/colorway, and any notes specific to how this product applies it.

### Front
- **front-chest** (~10in wide × ~3in tall): The brand logo (see logo_reference).
  **Technique:** embossed. **Color/Colorway:** tonal black-on-black.

### Back
- (List every back element with region + dimensions + technique + color.)
- (Delete this section heading if the product has no back decoration.)

### Sleeves / Collar / Hem / Other
- (Common: woven brand label inside back collar, or size tag in waistband.)
- (Delete this section heading if not applicable.)

## Negative — what is NOT on this product (DO NOT render)

- No printed text on chest.
- No embroidered patches anywhere.
- No back graphics (this is a clean back).
- No sleeve printing.
- (Add every conflation we want to prevent. Be specific. "No X on region Y.")

## Scene direction (optional — feeds the RAS prompt)

- **Pose:** Standing facing forward, three-quarter angle, one hand at side.
- **Setting:** Pure white studio backdrop, soft directional light, subtle drop shadow.
