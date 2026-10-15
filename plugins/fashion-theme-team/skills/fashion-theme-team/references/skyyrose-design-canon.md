# SkyyRose Design Canon

This is the motherbase default. Repository evidence and founder-approved canon
override recommendations. Unknown facts remain unknown.

## Brand posture

- The garment is the protagonist; interface decoration supports product truth.
- The experience is emotionally expressive, culturally aware, premium, and
  editorial without obstructing purchase decisions.
- Each collection has a distinct emotional world while sharing one governed
  commerce and design-system foundation.
- Use strong typographic contrast, deliberate asymmetry, meaningful negative
  space, tactile image sequencing, and restrained interaction.
- Collection accents are intentional and sparse. Do not wash every surface in
  one fashionable color.

## Brand identity

Host repo (DevSkyy): `CLAUDE.md` § 6 Brand, `docs/brand/visual-references.md`,
`docs/brand/collection-stories.md`,
`wordpress-theme/skyyrose-flagship/data/brand/typography.json`.

- Visual references — The Five, locked by the founder 2026-05-25: Kith,
  Oaklandish, Culture Kings, Fear of God, Palm Angels. European luxury-house
  lineage (museum / vault / cathedral aesthetic) is locked out; SkyyRose is
  American luxury streetwear with Oakland civic-pride and Black-owned heritage
  (`docs/brand/visual-references.md`).
- The former brand slogan is retired and must not be reproduced or paraphrased.
  No tagline is currently authorized. Use `SkyyRose` only as a brand-name
  fallback where a structured nonempty value is required.
- Tokens: Rose Gold `#B76E79` (global accent, Kids Capsule), Dark `#0A0A0A`
  (background), Silver `#C0C0C0` (Black Rose), Crimson `#DC143C` (Love Hurts),
  Gold `#D4AF37` (Signature). Contrast is a brand constraint, not just an a11y
  one: crimson `#DC143C` on `#0A0A0A` is below WCAG AA for body text, so use it
  for fills, borders, and glows and use `--color-text-muted` for de-emphasised
  text; never low-alpha white as a "muted" shorthand.
- Typography roles: Archivo (display/hero, `font-variation-settings 'wdth' 125`),
  Hanken Grotesk (body/UI), Anton (drop/UI accent), Cinzel (engraved caps), Inter
  (fallback). Per-collection name scripts: SkyyRose Black Rose Script (BR),
  SkyyRose Love Hurts Graffiti (LH), Pinyon Script (SIG), Grand Hotel (KC).
  Self-hosted woff2, zero CDN. SOT = `data/brand/typography.json`.
- Cut 2026-07-10, do not reintroduce: Playfair Display, Cormorant Garamond,
  Bebas Neue, Yellowtail.
- Hero titles = collection lockup IMAGES, never type-rendered. Fonts apply to
  interior surfaces only; the lockup is the collection name. Host repo (DevSkyy):
  the canonical files are each collection's `lockup.ref` in
  `data/collections/<slug>/identity.json` (founder decision 2026-09-17); Kids
  Capsule has no lockup yet and none may be substituted for it.
- "Bay Area" is allowed; Oakland-first ("The Town") is preferred in
  brand-authored primary copy.
- No urgency timers; scarcity is stated as fact, never as a ticking clock.

## Non-negotiables

- Product facts and media bindings originate from the single product registry
  (`logo-registry.json`, see `product-registry-authority.md`); the catalog CSV,
  dossiers, and image manifests are projections of it. Founder corrections are
  `FOUNDER_CONFIRMED` and land in the registry first. Verify pixels eyes-on per
  SKU; filenames are not evidence.
- No stock imagery, filler copy, invented scarcity, fake social proof, empty
  primary routes, placeholder states, or unlicensed assets.
- Mobile receives its own art direction, crop, pacing, density, and interaction
  substitutions rather than a compressed desktop layout.
- Motion communicates hierarchy, continuity, feedback, or product detail. It
  never delays access to shopping actions and always has a reduced-motion
  substitution.
- Creative generation remains review-only until founder approval. Paid calls,
  uploads, publishing, and deployment require explicit authority.

## Anti-slop exclusions

Reject centered-everything compositions, interchangeable serif-plus-sans
luxury, purple/blue default gradients, gradient text, uniform rounded card
grids, gratuitous glass effects, arbitrary glow, repetitive hero/product-grid
templates, generic stock models, decorative scroll hijacking, and animation
without product or narrative purpose.
