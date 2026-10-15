# SkyyRose Product Registry Authority

Load when: any phase reads, binds, renders, reviews, or corrects SkyyRose product
facts, SKU imagery, sizing, materials, graphics, or placements.

## Single editable source of truth

In the DevSkyy host repository, `logo-registry.json` at the repository root is a
symlink to `wordpress-theme/skyyrose-flagship/data/logo-registry.json`. This one
JSON file is the editable product source of truth.

- `products[sku]` records own commerce fields, garment color, available sizes and
  sizing references, fit, materials, features, the complete design
  specification, and image/source bindings.
- The logo and placement sections own graphics and decoration dimensions.
- Founder corrections are applied here first.

## Projections and consumers

`skyyrose-catalog.csv`, per-SKU dossiers, `data/sot-images.json`, theme PHP
catalog arrays, WooCommerce product data, prompts, local maps, and generated
manifests are compatibility projections or consumers. Never author product facts
in them. Image binaries keep their existing asset paths; the registry owns the
references to them.

- Read through ONE host entry point: `from skyyrose.core.product import
  get_product`. `get_product(sku)` returns the complete record in a single call
  — commerce fields, garment facts, the design specification, an image for every
  role, render sources, logos and placements, copy, founder-verbatim
  corrections, authority, and a `gaps` list naming anything absent. It fails
  closed: an unknown SKU raises and no fact is ever a silent blank. Non-Python
  callers run `python -m skyyrose.core.product <sku>` for the identical JSON.
- The narrow readers (`product_registry`, `catalog_loader`, `dossier_loader`,
  `sot_images`, `LogoRegistry`) remain for single-field needs. Reach for one
  only when you need exactly that field; never assemble a product picture by
  hand from several of them.
- Write catalog fields through the registry update API
  (`product_registry.update_catalog_fields`).
- After a direct JSON edit, run `python scripts/sync_product_registry.py`; run
  `python scripts/sync_product_registry.py --check` before handoff. Projection
  drift is a failure, not a warning.
- Listing the CSV or a dossier as an input is allowed only as a projection that
  passed the sync check. It never outranks the registry.
- Dossier reads resolve to `products[sku].dossier` inside the registry and come
  back on `get_product(sku)["dossier"]`. A standalone dossier file is a readable
  projection, never the declaring authority.
- A record's `gaps` list is the contract for absence: if a fact you need is
  named there, it does not exist yet. Ask the founder — never fill it in.

## Founder and maker authority

Corey is the founder and maker of the SkyyRose items. His product
specifications, founder-authored dossiers, supplied artwork identifications, and
direct corrections are authoritative for those products.

- Record his direct confirmation as `FOUNDER_CONFIRMED`.
- When an older registry value, dossier, generated record, or agent assumption
  conflicts with his latest explicit correction, update the conflicting record
  within task scope. Do not ask him to prove the correction again.
- Do not impose manufacturer, third-party, photographic, or independent
  verification on product facts he supplied, and never downgrade them to
  `NOT_MANUFACTURING_VERIFIED` or a similar status.
- Preserve his exact dimensions, ranges, artwork, and wording. A documented
  range or approximate notation is part of the specification.
- Verify that agent output and saved records match his instructions. Checking
  execution is not re-verifying the maker's knowledge of his own products.
- Ask only for a genuinely missing detail. Never invent an unstated measurement
  or alter unrelated product details.

## Delegation and other checkouts

- Pass the registry location and this authority rule to every delegated agent,
  review, and workflow that touches product, catalog, design, rendering, or QA.
- Before execution in another checkout, confirm it has the unified `products`
  schema and current founder corrections. Never substitute an older checkout's
  CSV or dossiers when its registry is stale.

## Known plugin gap

`product-fidelity-image-edits` authority receipts currently bind the `catalog`,
`sot_manifest`, and `dossier` projections (`scripts/fidelity_gate.py`). Binding
the registry itself is a receipt schema change that requires founder approval;
until then, a receipt is valid only when those projections passed the registry
sync check for the same candidate.
