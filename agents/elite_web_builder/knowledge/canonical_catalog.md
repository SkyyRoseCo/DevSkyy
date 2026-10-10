# Canonical Catalog — Elite Web Builder Reference

**Single source of truth:** `wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv`

This file used to duplicate the SKU table as a static reference. **That table drifted** within one session and caused a wasted paid render run on 2026-04-19 (kids-001 was listed here as "Purple/Pink" while the CSV said "Red/Black"). The duplicate was removed; now every agent reads the CSV on demand.

## How agents read the catalog

**Python agents (preferred):**
```python
from skyyrose.core.catalog_loader import read_catalog_rows, CATALOG_CSV
rows = read_catalog_rows()                 # list[dict[str, str]]
black_rose = [r for r in rows if r["collection"] == "black-rose"]
```

**Elite Studio:**
```python
from skyyrose.elite_studio.catalog import Catalog
cat = Catalog.load()
p = cat.require("br-010")      # raises if SKU not in CSV
print(p.name, p.branding_spec, p.is_preorder)
```

**Nano Banana imagery pipeline:**
```python
from nano_banana.catalog import load_catalog
catalog = load_catalog()       # dict keyed by SKU
```

**PHP (WordPress theme):**
```php
$product = skyyrose_get_product('sg-015');          // single SKU
$all     = skyyrose_get_product_catalog();          // full array, wp_cache-backed
$url     = skyyrose_product_url('lh-005');
$price   = skyyrose_format_price($product);
```

## CSV schema (21 columns — keep all four readers in sync if schema changes)

`sku, name, price, collection, description, badge, image, front_model_image, back_image, back_model_image, sizes, color, edition_size, published, is_preorder, branding_spec, render_output_slug, render_source_override, render_back_source_override, render_is_tech_flat, render_is_accessory`

Booleans use `1` / `0`. Image paths are theme-relative (e.g. `assets/images/products/br-001-crewneck.png`). The `render_*_override` columns are bare filenames — overrides for the Nano Banana pipeline.

## Retired SKU codes (DO NOT resurrect in production code)

`lh-001`, `br-d01..d04`, `sg-d01..d04`, `sg-008`, `sg-010`, `sg-004`. Archived references in `docs/`, `.planning/`, `.ralph/`, test fixtures are fine; anything in `inc/*.php`, `frontend/app/`, `wordpress-theme/*.php`, or `template-parts/` must match a live SKU from the CSV.

To find stale references:
```bash
grep -rEn "lh-001|sg-008|sg-010|sg-004|sg-d0[1-4]|br-d0[1-4]" \
    --include="*.php" --include="*.tsx" --include="*.ts" \
    wordpress-theme/skyyrose-flagship/ frontend/app/
```

## Retired catalog source files (deleted 2026-04-19)

All of these are gone and must NOT be resurrected: `assets/product-masters/catalog.yaml`, `assets/product-masters/manifest.json`, `scripts/generate_catalog.py`, `scripts/sync_manifest_from_catalog.py`, `data/product-catalog.csv`.

## Brand copy rules

- **Only tagline:** ``
- **Retired tagline (NEVER use):** `Where Love Meets Luxury`
- **Brand name:** SkyyRose (one word in product copy). "Skyy Rose" only when referring to the founder's daughter by name.
- **Founder:** Corey Foster.

## Collections

Four live collection slugs. Names, accents, and product membership are all in the CSV — query it.

| Slug | Display Name | Accent |
|------|-------------|--------|
| `black-rose` | Black Rose | `#C0C0C0` silver |
| `love-hurts` | Love Hurts | `#DC143C` crimson |
| `signature` | Signature | `#D4AF37` gold (accent) + `#B76E79` rose gold (primary brand) |
| `kids-capsule` | Kids Capsule | `#A8D8EA` sky (intentional palette silo) |
