# SkyyRose Theme — scoped context

**Commercial marketplace theme — this is the V1 theme.**
**Theme Name:** SkyyRose | **Text Domain:** `skyyrose` | **@package:** SkyyRose
The v2 theme ("SkyyRose Flagship 2", text domain `skyyrose-flagship-2`, `SKYYROSE2_VERSION`) lives in `../skyyrose-flagship-2/` with its own `CLAUDE.md`, `package.json` and deploy wrappers (`scripts/deploy-staging.sh` / `deploy-production.sh`). skyyrose.co and staging serve the Flagship 2 lineage `[live 2026-09-18]`; this V1 tree is not the deploy target.

Per-file map + token sizes: `.wolf/anatomy.md`. Directory layout is derivable via `ls`/`find` —
not duplicated here.

## Theme architecture

SkyyRose is a classic PHP theme with `theme.json` design settings and Gutenberg
block patterns. It deliberately does not ship `/templates/index.html`; adding
that file converts WordPress routing to a block theme and bypasses the mature
PHP storefront hierarchy.

| Surface | Source of truth | Why |
|---------|-----------------|-----|
| Homepage | `front-page.php` | **No** `front-page.html` — classic keeps cinematic homepage |
| Immersive / landing / Elementor | `template-*.php` | PHP Template Name still wins when assigned |
| Generic page / single / archive / search / 404 | `*.php` | Classic template hierarchy |
| Collection pages | `template-collection-*.php` | Canonical PHP collection shells |
| Header / footer (PHP views) | `header.php`, `footer.php` | Full navbar, cart, newsletter, mascot mount |
| WooCommerce | `woocommerce/*.php` | Classic WooCommerce overrides |

**Do not add** `/templates/index.html` or block template files without a full
cutover plan for the storefront, WooCommerce, header, footer, and custom pages.

**PHPCS compliance:**
- `.phpcs.xml` in theme root — WordPress standard, `skyyrose` prefix
- Run: `cd wordpress-theme/skyyrose-flagship && vendor/bin/phpcs --standard=.phpcs.xml -s .`
- Auto-fix: `vendor/bin/phpcbf --standard=.phpcs.xml .`
- Composer must be installed first: `~/.local/bin/composer install`

## WordPress Rules

- **Theme serves `.min` in production** (`$use_min = ! SCRIPT_DEBUG`). After ANY CSS/JS edit, rebuild with `node scripts/build-css.js && node scripts/build-js.js` or the change is inert live. Re-verify the `.min` output, not just the source.
- Extend via hooks (actions/filters), never modify core
- API: `index.php?rest_route=` NOT `/wp-json/`
- Escape output: `esc_html()`, `esc_attr()`, `esc_url()`, `wp_kses_post()`
- Sanitize input: `sanitize_text_field()`, `absint()`
- Always `$wpdb->prepare()` — never concatenate untrusted input
- Nonce + capability checks on all write actions
- No `innerHTML` in JS — use `createElement` + `textContent`

The gotchas below trip fresh sessions.

## Build commands run from `wordpress-theme/` (the PARENT), not here

There is NO `package.json` in `skyyrose-flagship/` — it lives at `wordpress-theme/package.json`. From `wordpress-theme/`:
`npm run build` (CSS+JS) · `npm run build:css` · `npm run build:js` · `npm run rebuild` (clean+build) · `npm run watch:build`.
From inside `skyyrose-flagship/` you can still run the raw scripts: `node scripts/build-css.js` / `node scripts/build-js.js`.

## Adding a template = TWO edits in `inc/enqueue.php` (or CSS loads wrong, silently)

1. `$template_map` in `skyyrose_get_current_template_slug()` (~`enqueue.php:426`) — maps `template-*.php` filename → slug string.
2. `$template_styles` in `skyyrose_enqueue_template_styles()` (~`enqueue.php:485`) — maps slug → CSS file (a JS section mirrors this).
Then create the source CSS/JS and run `npm run build` to emit `.min`. Miss either array → new template gets wrong CSS or none.

## Brand constants — use them, never hardcode

Color constants (`SKYYROSE_COLOR_ROSE_GOLD` / `_GOLD` / `_CRIMSON` / `_SILVER`) are defined in committed `inc/brand-colors.php`. `functions.php` ALSO includes `inc/brand.generated.php` (loaded first) — that file is **generated from `assets/brand/brand.yaml` at build and is NOT committed** (you won't see it in a fresh checkout); it supplies `SKYYROSE_BRAND_TAGLINE` + helpers like `skyyrose_brand_collections()`. NEVER hardcode a hex value or the tagline in PHP — reference the constants.

## Skyy mascot (3D site host) — v1.9.0

- `assets/models/skyy.glb` is **draco-compressed** — `skyy-3d.js` MUST keep its DRACOLoader wiring (`setDRACOLoader` + `DRACO_DECODER_PATH`) or the load fails silently and she never appears. The decoder path is `SKYYROSE_ASSETS_URI_3D() + '/js/lib/draco/'` (skyy-3d.js:29), derived from `assetsUri` and **independent of `MODEL_URL`** — so `MODEL_URL` safely carries a `?ver=SKYYROSE_VERSION` cache-bust (enqueue.php) without affecting the decoder. Decoders live in `assets/js/lib/draco/`; CSP needs `'wasm-unsafe-eval'` (inc/security.php).
- Clip contract: lowercase `idle`/`walk` required, `wave`/`point`/`talk`/`joy` optional. mascot.js emits `skyy:*` CustomEvents; skyy-3d.js maps them to clips by name.
- Gate: `skyyrose_mascot_is_enabled()` (inc/mascot-config.php) — Customizer theme_mod `skyyrose_mascot_enabled`, **live by default**, but an explicit stored `false` in the DB overrides code defaults (bit us on first deploy).
- Mounts ONLY via footer.php (front-page.php uses `get_footer()`); checkout excluded.
- `window.SKYY_3D_CONFIG` IS emitted by `inc/enqueue.php` (~447) whenever a GLB URL resolves (`modelUrl` + `walkSide`); the hardcoded theme-path fallbacks in skyy-3d.js only cover the localize-missing edge case.
- **Mascot body v7 = the Love Hurts Girl** (2026-07-12, founder-directed): `assets/models/skyy.glb` now carries the in-house-rigged girl (25-joint rig, geodesic-capsule skin weights, hand-authored walk + breathing idle; source rig in the mascot worktree / PR #736). Clips shipped: `idle` (3s breath loop) + `walk` (1s cycle) — `wave/point/talk/joy` intentionally absent, they fall back to idle via `playFirstAvailable`. Same filename → all loader/ver-busting/CSP wiring unchanged.

## Kill-switch awareness

`SKYYROSE_COMING_SOON_MODE` (`functions.php:~39`) — `true` makes all public traffic see HTTP 503. Default `false`; don't toggle without intent. `CONCATENATE_SCRIPTS = false` (`functions.php:~50`) is an intentional override for WP.com MIME/concat errors — don't "fix" it.
