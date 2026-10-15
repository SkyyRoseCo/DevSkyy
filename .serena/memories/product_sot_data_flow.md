# Product facts: where they live and how to read them

Verified 2026-10-14 against `main` (`skyyrose/core/product.py`, `dossier_loader.py`,
`catalog_loader.py`). Canonical wording is in `SOT.md` and root `CLAUDE.md`; this file
only records the direction of data flow.

## Direction (one-way)

```
founder correction / registry update API
        |
        v
wordpress-theme/skyyrose-flagship/data/logo-registry.json   <- THE SOT (root symlink: logo-registry.json)
        |  read by
        v
skyyrose.core.product.get_product(sku)                      <- THE read entry point (a reader, not a store)
        |  consumed by
        v
agents, pipelines, renders, ads, content, API, themes

projections / side files (never edited, never a source):
  skyyrose-catalog.csv, dossiers/*.md, sot-images.json
  -> rebuilt by `python scripts/sync_product_registry.py`; drift checked by `--check`
  (`product-content.json` is likewise not a source: `get_product` names it as a file
  NOT to read.)
```

## Answer to "does the SOT get its product info from get_product?"

No. The registry JSON is the source; `get_product` gets everything from it. The
dependency arrow points registry -> get_product -> consumers, never back.

- `get_product` calls `load_registry()["products"]`; its dossier section comes from
  `load_dossier()`, which by default projects the registry's own `dossier` entry
  (`project_registry_dossier`), not a dossier file on disk.
- `read_catalog_rows()` resolves to `catalog_rows()` (the registry) for the default CSV path.
- Explicit external CSV/dossier directories are import fixtures only.

## What "one entry point" does and does not mean today

- Narrow readers (`catalog_loader`, `dossier_loader`, `product_registry`, `sot_images`,
  `LogoRegistry`) read the SAME registry, so using one does not fork truth — but it is
  not the single entry point, and each returns a partial view with no `gaps` list.
- AST census of git-tracked `*.py` on `main` (2026-10-14, non-test, outside
  `skyyrose/core/`): 24 files import from `skyyrose.core.product`; 55 import a narrow
  reader without it; 44 name a registry/CSV/`sot-images.json`/`product-content.json`
  path literal without it (sets overlap). Generators and validators such as
  `scripts/sync_catalog_downstream.py`, `scripts/validate_catalog_consistency.py`, and
  `wordpress-theme/skyyrose-flagship/data/build-collection-sot.py` legitimately touch
  the files directly. Treat the rest as migration candidates, not as proven defects.
- For a new consumer: call `get_product(sku)`; read `["gaps"]`; never fill a gap yourself.
- For a catalog write: use the registry update API, then `sync_product_registry.py`.

## Do not

- Do not cache a product fact from this file, a CSV, or a dossier — call `get_product`.
- Do not write a founder statement about a garment straight into a garment field; it
  goes into the SKU's dossier first (see CLAUDE.md).
