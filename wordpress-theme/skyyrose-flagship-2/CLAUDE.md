# SkyyRose Flagship 2 — scoped context

**This is the V2 theme. Folder name `skyyrose-flagship-2` (never `-v2`).**
**Theme Name:** SkyyRose Flagship 2 | **Text Domain:** `skyyrose-flagship-2` | **PHPCS:** `phpcs.xml` (text domain `skyyrose-flagship-2`, prefix `skyyrose2`)

The V1 theme ("SkyyRose", text domain `skyyrose`, `SKYYROSE_VERSION`) is `../skyyrose-flagship/` with its
own `CLAUDE.md`; it builds from `wordpress-theme/package.json` and is not the deploy target. Nothing in
that folder's build or lint tooling applies here.

`[live 2026-09-18]`: skyyrose.co serves this lineage at v2.3.1 inside folder `skyyrose-flagship`;
staging https://staging-7e48-skyyrose.wpcomstaging.com serves folder `skyyrose-flagship-2` at v2.4.4
(`staging.skyyrose.co` does not resolve). After cutover production runs folder `skyyrose-flagship-2`.

## Version triple — `SKYYROSE2_VERSION`

Bump all three to one value before any deploy that changed shipped CSS/JS/PHP:

- `functions.php:10` — `define( 'SKYYROSE2_VERSION', … )`; asset `?ver=` is this constant plus a per-file
  content hash (`functions.php` ~173-177), so a stale constant still ships stale-cached assets.
- `style.css` — `Version:`
- `readme.txt` — `Stable tag:`

`CHANGELOG.md` records what each version shipped.

## Build commands run from THIS folder (own `package.json`, not the parent's)

```bash
cd wordpress-theme/skyyrose-flagship-2 && npm install   # devDependencies: clean-css, terser
npm run build            # build:registry + build:assets + build:i18n
npm run build:assets     # node scripts/build-assets.mjs — deterministic source → .min for assets/css + assets/js
npm run check:assets     # --check: every .min byte-identical to a fresh build (fails on drift)
npm run check:registry   # data/product-presentation-registry.json current
npm run check:i18n       # languages/ .pot current
npm run lint:php         # php -l on every .php
../skyyrose-flagship/vendor/bin/phpcs --standard=phpcs.xml -s .   # PHPCS with THIS theme's phpcs.xml; no vendor/ here — the V1 theme's composer install supplies the binary (.claude/hooks/phpcs-on-write.sh does this per edit)
npm run verify           # bash scripts/verify-marketplace.sh — php -l, jq on data/*.json, font provenance hashes
npm run verify:workspace # bash scripts/verify-v2-workspace.sh (--strict via verify:workspace:strict)
npm run package:theme    # bash scripts/package-theme.sh — build + verify + dist/skyyrose-flagship-2.zip
bash scripts/verify-v2-candidate.sh   # route/attestation gate (needs .fashion-theme/founder-rights-attestation-2026-08-26.json at repo root)
```

Production serves `.min` (`functions.php:127` switches on `SCRIPT_DEBUG`; map at `functions.php:137-139`).
After ANY edit under `assets/css/` or `assets/js/`, run `npm run build:assets` or the change is inert live;
`npm run check:assets` is the drift gate. Never edit a `.min` file directly.

`build:registry` (`scripts/build-product-presentation-registry.py`) reads
`wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv`, which is a generated projection of the ONE
product SOT `wordpress-theme/skyyrose-flagship/data/logo-registry.json` (read via
`from skyyrose.core.product import get_product`). Fix product facts in the registry, run
`python scripts/sync_product_registry.py`, then rebuild here — never edit the CSV or
`data/product-presentation-registry.json` by hand.

## Layout facts

- Classic PHP theme: `front-page.php`, `home.php`, `page.php`, `single.php`, `archive.php`, `search.php`,
  `404.php`, `page-wishlist.php`, `template-collection.php`, four `template-immersive-*.php`,
  `woocommerce/` overrides, `template-parts/`. Modules in `inc/`: `demo-import.php`, `marketplace.php`,
  `performance.php`, `presentation-registry.php`, `security.php`, `seo-indexing.php`, `starter-content.php`.
- Routes (from `README.md`): `/collections/<slug>/`, `/worlds/<slug>/`, `/pre-order/`, `/about/`,
  `/journal/`, `/wishlist/`, policy pages, WooCommerce shop/bag/checkout/account. `[live 2026-09-18]`:
  staging answers `/collections/signature/` 200 and 302s `/collection-signature/` to it; production
  (2.3.1) still answers the V1-style `/collection-signature/` and 404s `/collections/signature/`.
- Data: `data/product-presentation-registry.json` (generated), `data/font-provenance.json`,
  `data/image-optimization.json`, `data/opening-product-media.json`, `data/brand-asset-transparency.json`.
- WooCommerce is the sole authority for product, price, inventory, cart, checkout, order state; the demo
  importer (`inc/demo-import.php`) creates pages, never products.

## WordPress rules (same bar as V1)

- Extend via hooks, never modify core · escape output (`esc_html()`, `esc_attr()`, `esc_url()`,
  `wp_kses_post()`) · sanitize input · `$wpdb->prepare()` · nonce + capability on every write · no
  `innerHTML` in JS · text domain `skyyrose-flagship-2` on every i18n call (PHPCS `text_domain` in
  `phpcs.xml`; never the V1 theme's `.phpcs.xml`, whose domain is `skyyrose`).
- API: `index.php?rest_route=` NOT `/wp-json/`.

## Deploy — always STOP-AND-SHOW, always through the wrappers

**BLOCKED until PR #918 lands — both wrappers refuse a `skyyrose-flagship-2` source, `--dry-run`
included.** One-shot flags `--allow-new-theme-folder` / `--allow-theme-identity-change` replace exporting
`ALLOW_NEW_THEME_FOLDER` / `ALLOW_THEME_IDENTITY_CHANGE` (inherited exports are refused); the env file's
`SSH_USER` must be `<first label of the PUBLIC_URL host>.wordpress.com` and `.env.wordpress.staging` needs
`SFTP_HOST`/`SFTP_USER`/`SFTP_PASS` (absent locally `[repro 2026-09-19]`).

```bash
bash scripts/deploy-staging.sh [--dry-run]      # env .env.wordpress.staging → staging-7e48-skyyrose.wpcomstaging.com
bash scripts/deploy-production.sh [--dry-run]   # env .env.wordpress → skyyrose.co; refuses until WP_THEME_PATH names the -2 folder
```

`scripts/deploy-theme.sh` is the engine and refuses direct runs; its preflight `check_theme_identity`
refuses when the live theme's Name/Text Domain differs from this source. The engine does not yet support
deploying `skyyrose-flagship-2` (PR #918's V2 deploy changes are a follow-up). Cutover = deploy +
`wp theme activate skyyrose-flagship-2`, each its own STOP-AND-SHOW. Deploy is an atomic hot-swap:
production ends up with exactly this tree — anything the source lacks is deleted live.
`cd wordpress-theme && npm run deploy:staging[:dry]` / `deploy:production[:dry]` wrap the same two
scripts; `bash scripts/verify-deploy.sh --env-file <env>` verifies the routes afterwards.
