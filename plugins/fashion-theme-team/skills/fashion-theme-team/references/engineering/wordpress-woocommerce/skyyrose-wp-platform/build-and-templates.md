# Build, Templates, and Blocks — the Machinery Behind Four Collections

Load when: the task touches templates, patterns, blocks, the `.min` build pipeline, or enqueue/template routing in the SkyyRose theme (routed from `overview.md`).

Provenance: embedded from the DevSkyy skill `skyyrose-wp-platform` (`reference/build-and-templates.md`); source hash, license, and every adaptation are recorded in [`../index.md`](../index.md).

`wp-block-development`, `wp-block-themes`, `wordpress-plugin-core`, `wordpress-router`,
`wp-performance`, and `wp-plugin-development` covered this as generic theme mechanics. On this
theme, the templates below aren't interchangeable page shells — each one carries a specific
collection's identity (Signature's gold city-tour energy, Black Rose's gothic armor, Love
Hurts' romantic-castle intensity, Kids Capsule's rose-gold warmth), so the routing and build
discipline that keeps them from bleeding into each other matters as much as the code itself.

## Template inventory (verify against the live tree, don't assume this list is exhaustive)

- `front-page.php` — Three.js portals (3 collection rings + particles)
- `template-collection-{signature,black-rose,love-hurts,kids-capsule}.php` — collection pages
- `template-landing-{black-rose,love-hurts,signature}.php` — conversion landing pages
- `template-preorder-gateway.php` — pre-order flow with collection selector
- `template-immersive-{signature,black-rose,love-hurts,kids-capsule}.php` — 3D experiences (see `threejs-immersive.md`)
- `template-about.php` — brand story + timeline
- `template-elementor-canvas.php` / `template-elementor-fullwidth.php` — builder templates

Template routing and slug detection is centralized in `inc/enqueue.php` -- when adding a new
template, register it there, not by scattering `wp_enqueue_script` calls across the template
file itself.

## The `.min` build pipeline — the #1 recurring mistake on this theme

`inc/enqueue.php` sets `$use_min = ! SCRIPT_DEBUG`. Production always serves `.min`. This
means:

1. Editing a source `.css`/`.js` file and deploying does **nothing** live until you rebuild.
2. The rebuild command is `node scripts/build-css.js && node scripts/build-js.js` — run from
   `<theme-workspace>/` (the parent of `<theme-root>`), not the theme subdirectory.
3. Verify the _`.min` output_, not the source — `grep` the new content into the `.min` file
   directly, or byte-size-diff it, after every rebuild. Confirming the source changed and
   stopping there is not verification; it's the exact mistake this note exists to prevent.

## Builder detection

`inc/builders/detection.php` exposes `skyyrose_active_builder()` and
`skyyrose_builder_owns_template()`. Templates need to check builder ownership before rendering
their own markup, or a builder-edited page (Elementor canvas/fullwidth) can get double-rendered
content from both the builder and the theme template.

## Patterns and product cards

- `inc/patterns.php` registers block patterns for all four collections.
- `template-parts/product-card-holo.php` + `assets/js/product-card-holo.js` +
  `assets/css/product-card-holo.css` — the holographic glass card system with magnetic tilt.
  Any change here needs the `.min` rebuild step above before it's visible live.

## PHP conventions specific to this theme

- Escape output: `esc_html()`, `esc_attr()`, `esc_url()`, `wp_kses_post()` — every echo of
  user- or catalog-derived data.
- Sanitize input: `sanitize_text_field()`, `absint()`.
- `$wpdb->prepare()` always — never string-concatenate untrusted input into a query.
- Nonce + capability checks on every write action (ajax handlers, REST callbacks).
- REST routes resolve via `index.php?rest_route=`, not `/wp-json/` — a WordPress.com hosting
  constraint, not a stylistic choice; using `/wp-json/` directly will 404 or misroute here.

## Domain-specific verification

- **PHP syntax/style**: `php -l <file>` per changed file, then
  `vendor/bin/phpcs --standard=.phpcs.xml -s .` from the theme root (composer must be
  installed first: `composer install`; Host repo (DevSkyy): composer is at
  `~/.local/bin/composer`). Auto-fix candidates:
  `vendor/bin/phpcbf --standard=.phpcs.xml .`
- **Template registration didn't break the two-array trap**: `<theme-root>/CLAUDE.md`
  documents a two-array template-registration gotcha in `enqueue.php` specifically — re-read
  it before touching template registration, don't re-derive from scratch.
- **`.min` actually rebuilt**: see the build pipeline section above — this is the check most
  likely to be skipped under time pressure; don't skip it.
- **Live effect confirmed**: cache-busted `curl -s "https://skyyrose.co/PATH?cb=$(date +%s)"`
  for HTML/headers, Playwright/Chrome DevTools MCP screenshot for anything visual — per the
  project's standing rule, after any skyyrose.co change, both desktop and mobile. (Getting the
  change onto skyyrose.co is outside plugin scope — the Fashion Theme Team builds and reviews
  candidates only; production deploys belong to the host repo's STOP-AND-SHOW approval process.)
