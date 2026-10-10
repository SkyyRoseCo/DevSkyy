# assets/products/source-photos/

Raw source photography, organized by collection slug: `black-rose/`,
`signature/`, `love-hurts/`, `kids/`, `pre-order/`, `brand-assets/`. This
guidance covers all of them — the per-collection subdirs don't need their own.

## What goes here & where it flows

- **Naming:** `{sku}-{variant}.{ext}` — e.g. `br-001-front.jpg`,
  `br-001-back.jpg`. Use the real SKU from the catalog CSV; never invent one.
- These are SOURCE files — NOT served directly by the theme and NOT committed to
  WooCommerce.
- **After adding/changing files, run `make sot-manifest`** to regenerate the SOT
  image manifest. Every surface resolves a SKU's image through
  `skyyrose.core.sot_images.resolve_image()` (`skyyrose/core/sot_images.py`) —
  front-first — never a hardcoded path.

## Fidelity gate (mandatory)

Before any render job or site surface references a photo here, **vision-verify
the pixels** — the actual garment must match that SKU per the catalog/dossier,
not just the filename. Filenames lie; wrong-garment imagery is the #1 recurring
defect. Eyes-on or don't ship. See root CLAUDE.md "Product-image fidelity
gate" + `docs/brand/sot-imagery-policy.md`.
