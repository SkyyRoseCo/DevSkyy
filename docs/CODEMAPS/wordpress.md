# WordPress Theme Codemap

<!-- Generated: 2026-07-06 | Files scanned: wordpress-theme/skyyrose-flagship root (~30 templates) + inc/ (35 files) + inc/builders/ (7) | Token estimate: ~650 -->

**Production theme:** `wordpress-theme/skyyrose-flagship/` — live at skyyrose.co. Theme Name: SkyyRose, text domain `skyyrose`.

## Template map

| Template | Purpose |
|---|---|
| `front-page.php` | Homepage — Three.js portals (3 collection rings + particles) |
| `template-collection-{signature,black-rose,love-hurts,kids-capsule}.php` | Collection pages (thin — delegate to `collection-content.php`) |
| `template-immersive-{signature,black-rose,love-hurts,kids-capsule}.php` | 3D immersive experiences |
| `template-landing-{signature,black-rose,love-hurts,kids-capsule}.php` | Conversion landing pages |
| `template-preorder-gateway.php` | Pre-order flow, collection selector |
| `template-about.php` | Brand story + timeline |
| `template-elementor-{canvas,fullwidth,editorial}.php` | Builder passthrough templates |
| `template-{contact,faq,coming-soon,experiences,shipping-returns}.php` | Support pages |
| `404.php`, `search.php`, `archive.php`, `single.php`, `page.php` | WP core template overrides |

## inc/ — 35 modules

Enqueue/build: `enqueue.php` (36K — all CSS/JS loading + template-slug detection), `enqueue-performance.php`, `enqueue-phases.php`. Security: `security.php` (CSP, rate limiting, ABSPATH guards). Commerce: `woocommerce.php`, `woocommerce-preorder.php`, `woocommerce-kids-capsule.php`, `wc-product-functions.php`, `product-catalog.php`(+`-display.php`), `skyyrose-product-meta.php`, `wishlist-functions.php`+`class-wishlist-widget.php`. SEO/perf: `seo.php` (40K), `accessibility-seo.php`, `accessibility-fix.php`, `performance.php` (29K)+`performance-guardian.php`. Content: `collection-content.php`, `collection-sot-reader.php`, `collections-config.php`, `patterns.php`, `product-taxonomy.php`. Integrations: `klaviyo-integration.php`, `facebook-sdk.php`, `mcp-bridge.php`, `fastapi-client.php`, `rest-api-experience.php`, `rest-kids-capsule.php`. Experience engine: `experience-engine.php`, `experience-analyzer.php`, `immersive-ajax.php`, `immersive-product-adapter.php`, `mascot-config.php`. Admin/setup: `admin-experience-dashboard.php`, `customizer.php`, `theme-activation-setup.php`, `theme-setup.php`, `menu-setup.php`, `ajax-handlers.php`, `redirects.php`, `personalization.php`, `v7-cards.php`, `maintenance.php`, `image-placements.php`.

## inc/builders/ — page-builder detection

`detection.php` — `skyyrose_active_builder()` + `skyyrose_builder_owns_template()`. Adapters: `elementor.php`(+`elementor-compat.php`), `beaver-builder.php`, `bricks.php`, `divi.php`, `shared.php`.

## Build discipline — MANDATORY

Theme serves `.min` files in production (`$use_min = ! SCRIPT_DEBUG`). Every CSS/JS edit requires: `node scripts/build-css.js && node scripts/build-js.js`, then re-verify the `.min` output (not just the source) — an unrebuilt change is inert live.

## Deploy

`bash scripts/deploy-theme.sh` (`.env.wordpress`; SSH key `~/.ssh/skyyrose-deploy`; server `sftp.wp.com`). PHPCS: `vendor/bin/phpcs --standard=.phpcs.xml -s .` (WordPress standard, `skyyrose` prefix); auto-fix via `phpcbf`.

## Conventions

Extend via hooks (actions/filters) — never modify WP core. REST calls use `index.php?rest_route=`, not `/wp-json/` (401s on WP.com otherwise). Escape output (`esc_html`/`esc_attr`/`esc_url`/`wp_kses_post`), sanitize input (`sanitize_text_field`/`absint`), always `$wpdb->prepare()`, nonce + capability checks on writes.

## Related codemaps

[data.md](data.md) (catalog CSV + registry collection identity + SOT imagery consumed by this theme) · [architecture.md](architecture.md) · [dependencies.md](dependencies.md)
