# Data Codemap

<!-- Generated: 2026-07-06 | Files scanned: alembic/versions (3), database/models (2), wordpress-theme data/ (5 subdirs), skyyrose/core (13 files) | Token estimate: ~600 -->

## Canonical product data (SOT) — registered in SOT.md at repo root

| Source | Location | Role |
|---|---|---|
| Catalog | `wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv` (root symlink `skyyrose-catalog.csv`) | Single product manifest — SKU, price, collection, metadata. Never invent SKUs. |
| Dossiers | `wordpress-theme/skyyrose-flagship/data/dossiers/*.md` | Per-SKU, founder-authored narrative (never ML-drafted); `_template.md` defines the schema |
| Collection identity | `wordpress-theme/skyyrose-flagship/data/logo-registry.json` → `collections.<slug>` | Canon seed (palette, fonts, story). `design-tokens.css` / `sot.json` / `index.html` are **generated from it** — edit the registry entry only, never the generated files |
| Brand/logos | `wordpress-theme/skyyrose-flagship/data/{brand,brand-logos,product-references}/` | Supporting brand assets |

## Imagery resolution (SOT-only, front-first)

| Layer | Location | Role |
|---|---|---|
| Resolver | `skyyrose/core/sot_images.py` | `resolve_image()` — the only sanctioned per-SKU image lookup |
| Manifest | `data/sot-images.json` | Generated (`make sot-manifest`); front-first (on-model render before flat packshot); header states "DO NOT EDIT" |
| Asset hub | `assets/hub/` (+ `HUB-SPEC.md`, `_verify/`, `collections/`, `site/`) | Verified-imagery source of truth for non-per-SKU visuals |
| Product manifest | `assets/products/manifest.json` | Per-product asset tracking |
| Supporting modules | `skyyrose/core/` | `catalog_loader.py`, `catalog_dedup.py`, `dossier_loader.py`, `dossier_schema.py`, `asset_manifest.py`, `paths.py` (single path authority), `clip_embedder.py`/`dino_embedder.py` (embeddings), `hashing.py`, `review.py` |

## Application database (SQLAlchemy + Alembic)

`database/db.py` — engine/session. `database/models/` — `tenant.py`, `tenant_user.py` (multi-tenancy; only 2 model files currently tracked in this package — most domain models live inline elsewhere, e.g. `agents/models.py`). Migrations in `alembic/versions/`: `001_baseline_schema.py` (baseline schema), `002_add_brand_assets.py`, `003_add_analytics_tables.py`. Env config: `alembic/env.py` (async support). Seeding: `database/seed_admin.py`, `database/seed_catalog.py`.

## Rule

Never fork or introduce a second copy of a SOT source. Product imagery must resolve through `sot_images.resolve_image()` on every surface (WP, dashboard, MCP, pipelines, agents) — never a hardcoded `assets/images/products/...` literal. Guard test: `tests/test_sot_no_adhoc_imagery.py`.

## Related codemaps

[wordpress.md](wordpress.md) (theme consumer of the catalog and collection identity) · [backend.md](backend.md) (`database/` wiring) · [architecture.md](architecture.md)
