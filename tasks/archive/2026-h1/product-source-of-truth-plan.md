# Product Source-of-Truth — Build Plan (2026-06-01)

**Goal:** make the founder's flatlays/techflats the canonical source of truth for product imagery, per-SKU, so every downstream pipeline (ghost-mannequin generation, catalog, PDP) reads ONE place. Replaces the scattered/mislabeled status quo.

## Founder schema (each product must have)
- `flatlays/` — overhead flat-lay photography (preferred source)
- `techflats/` — **front + back, separated** (fallback when no flatlay)
- `logos/` — the logo/patch assets applied to that product
- **spec** — fabric, materials, logo placements, description, colorway

## Located sources (verified 2026-06-01)
- **Flatlays:** `skyyrose-photo-scan/flat-lays/` — 176 raw JPEGs, UUID-named, NO mapping. MIXED (real flatlays + logos + spec sheets + model shots + dupes). Indexed FL001–FL176 (contact sheets in /tmp/sheets/flatlays-*.jpg).
- **Techflats:** `skyyrose-photo-scan/tech-flats/` — 275 raw, UUID-named (TF001–TF275). PLUS clean organized set `assets/techflats/split/{collection}/` (front/back per garment, named) + `assets/techflats/{collection}/` (patches/logos).
- **Logos/patches:** `assets/techflats/{collection}/patch-*.jpg`, `brand-script-logotype`, `hero-overlays/*.png`.
- **Spec:** already largely exists in dossiers (`data/dossiers/{slug}.md`, accessed via `skyyrose_get_product_dossier($sku)` → `branding_block`, fabric, placements) + catalog CSV (`branding_spec`, `garment_type_lock`, `color`).

## Proposed canonical structure
```
assets/product-source/{sku}/
  flatlay/   front.jpg  back.jpg  [detail-*.jpg]
  techflat/  front.jpg  back.jpg
  logos/     {patch/logo files for this product}.png
  spec.json  { collection, garment_type, fabric, materials,
               colorway, logo_placements[], description, source_provenance }
assets/product-source/INDEX.json   # sku -> all paths + original UUID provenance  ← SOURCE OF TRUTH
```
Raw scans are NEVER moved — folders get COPIES; INDEX.json records the origin UUID for traceability.

## Phases
1. **Map** UUID → SKU + angle (front/back) for flat-lays + tech-flats. Highest-risk step (mis-map = lh-005 redux). Human-confirmed.
2. **Assemble** per-SKU folders (copy chosen images; pull logos from techflats/{collection}; never mutate raws).
3. **Spec** — generate spec.json per SKU from dossier + catalog; founder fills fabric/placement gaps.
4. **Manifest** INDEX.json + wire catalog/pipeline to read from product-source as canonical.
5. THEN ghost-mannequin generation reads from product-source (flatlay→else techflat).

## Open decisions (need founder)
- D1: structure + location above OK? (`assets/product-source/`)
- D2: `skyyrose-photo-scan` the right flatlay source, or cleaner flatlays elsewhere?
- D3: mapping labor — I draft map from sheets→you correct / you map directly / AI-vision agents in parallel?
