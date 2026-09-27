# SkyyRose Flagship 2 — scoped context

**Status: in staging. Will replace `skyyrose-flagship` (v1) on skyyrose.co when
approved.** **Theme Name:** SkyyRose Flagship 2 | **Text Domain:**
`skyyrose-flagship-2` **@package:** SkyyRoseFlagship2 | **Version constant:**
`SKYYROSE2_VERSION` (currently `2.4.4`)

Directory layout is derivable via `ls`/`find` — not duplicated here.

## Theme architecture

Classic PHP theme + `theme.json`. WooCommerce is the **sole authority** for
products, variations, price, inventory, cart, checkout, and payment state. The
theme never manufactures a product fallback or invents inventory.

| Surface           | Source of truth            | Notes                                               |
| ----------------- | -------------------------- | --------------------------------------------------- |
| Homepage          | `front-page.php`           | No `front-page.html` — keeps cinematic PHP routing  |
| Collection worlds | `template-collection.php`  | Shared shell; collection slug drives content        |
| Immersive worlds  | `template-immersive-*.php` | One per collection                                  |
| Generic pages     | `page.php`, `index.php`    | Classic hierarchy                                   |
| WooCommerce       | `woocommerce/*.php`        | Classic WC overrides — hooks only, never core edits |

**Do not** add `/templates/index.html` — it converts to a block theme and
bypasses every PHP template and WooCommerce override.

## PHP conventions

- Prefix: **`skyyrose2_`** — never use `skyyrose_` (that's the v1 theme)
- Namespace tag: `@package SkyyRoseFlagship2`
- ABSPATH guard on every file: `defined( 'ABSPATH' ) || exit;`
- Escape: `esc_html()` / `esc_attr()` / `esc_url()` / `wp_kses_post()`
- Sanitize: `sanitize_text_field()` / `absint()`
- Always `$wpdb->prepare()` — never concatenate untrusted input
- Nonce + capability check on every write action
- No `innerHTML` in JS — `createElement` + `textContent`

PHPCS standard: `phpcs.xml` in theme root. Run from this directory:

```bash
find . -name '*.php' -not -path './vendor/*' -print0 | xargs -0 -n1 php -l
```

## Build commands (run from THIS directory — has its own package.json)

Scripts live in this directory's `package.json` (`npm run` lists them): `npm ci`
(pinned via `npm-shrinkwrap.json`), `npm run build` (registry + assets + i18n →
`.min` siblings), `npm run verify` (full marketplace gate),
`npm run package:theme` (→ `dist/skyyrose-flagship-2.zip`).

**Parity checks (write nothing, exit 1 on drift):**

```bash
node scripts/build-assets.mjs --check
python3 scripts/build-product-presentation-registry.py --check
python3 scripts/build-pot.py --check
```

## Co-change rules (hard)

### 1. Source CSS/JS → .min rebuild (always)

`.min` siblings live next to every source file. After any CSS or JS edit:

```bash
node scripts/build-assets.mjs
```

Then verify: `node scripts/build-assets.mjs --check`

**Critical:** the global repo `.gitignore` excludes `*.min.css` and `*.min.js`.
Force-add every `.min` file:

```bash
git add -f assets/css/theme.min.css assets/js/theme.min.js
```

A clean checkout is NOT release-ready without the force-tracked `.min` files.

### 2. Version triple — same rule as v1, different constant

Any version bump must touch all three in one commit:

```
functions.php   ← SKYYROSE2_VERSION constant
style.css       ← Version: header
readme.txt      ← Stable tag
```

Commit: `chore(theme): bump version triple to X.Y.Z`

### 3. Generated data files — commit with their source

These four files are always rebuilt and committed when their inputs change:

| Generated file                            | Source / trigger                                 |
| ----------------------------------------- | ------------------------------------------------ |
| `data/product-presentation-registry.json` | `scripts/build-product-presentation-registry.py` |
| `data/font-provenance.json`               | Manually maintained; SHA256-locked per font      |
| `data/image-optimization.json`            | Manually maintained                              |
| `data/opening-product-media.json`         | Manually maintained                              |

### 4. Font changes → SHA256 update in data/font-provenance.json

`verify-marketplace.sh` checks every registered page font's `sha256` field. A
mismatch fails the gate. Update the hash whenever a font file changes.

## Asset authority

`assets/sot/` is **self-contained** — it does NOT pull from the repo-root
`sot-images.json` or `assets/products/`. All theme-local SOT assets live here:

```
assets/sot/
├── brand/          # lockup images, wordmarks
├── branding/       # collection branding assets
├── fonts/          # page typography (license-locked via font-provenance.json)
├── images/
│   ├── hero/       # full-bleed heroes; must have 640w, 1024w, 1440w webp ≤ 260KB each
│   └── logos/      # monogram, rose, cluster assets
└── video/          # editorial video

assets/approved-card-fronts/<sku>-onmodel.webp  # candidate-bound; needs SOT dossier
assets/card-scenes/<sku>-onmodel.webp           # editorial scene backgrounds
assets/scroll-world/                            # immersive world assets
assets/models/skyy-mascot.glb                   # Draco-compressed; keep DRACOLoader wiring
```

Hero derivative rule: every base hero must exist at **640w, 1024w, and 1440w**
webp; each file must be **≤ 260 KB**. `verify-marketplace.sh` enforces both.

Adding a card front: provide `assets/approved-card-fronts/<sku>-onmodel.webp`
AND update the matching SOT dossier. A filename alone is not proof of identity.

## Mascot (assets/models/skyy-mascot.glb)

- Draco-compressed — `skyy-3d.js` MUST keep its DRACOLoader wiring or the model
  fails silently
- Clips required: `idle`, `walk`; optional: `wave`, `point`, `talk`, `joy`
- `mascot.js` emits `skyy:*` CustomEvents; `skyy-3d.js` maps them to clips
- Mounts via `template-parts/skyy-mascot.php`; excluded from checkout pages

## inc/ module load order (functions.php)

```
inc/marketplace.php        ← demo importer (idempotent; never creates products)
inc/performance.php        ← resource hints, lazy loading, LCP preloads
inc/seo-indexing.php       ← structured data, OG/Twitter, canonical
inc/security.php           ← CSP, nonce, auth hardening
inc/demo-import.php        ← page/menu provisioning (admin; runs once)
inc/presentation-registry.php ← product-presentation adapter (no prices/stock)
```

The demo importer is idempotent: reuses existing page paths, never deletes
content, never overwrites merchant-authored pages, never replaces a populated
menu.

## Marketplace handoff gates (must all pass before dist/)

| Gate                | Command                                                     |
| ------------------- | ----------------------------------------------------------- |
| PHP syntax          | `npm run lint:php`                                          |
| JSON validity       | `jq empty` on all `data/*.json`                             |
| Font license SHA256 | `verify-marketplace.sh` (auto-checked)                      |
| Asset parity        | `node scripts/build-assets.mjs --check`                     |
| Registry freshness  | `build-product-presentation-registry.py --check`            |
| POT freshness       | `build-pot.py --check`                                      |
| Hero derivatives    | 3 breakpoints × every hero base, ≤ 260KB                    |
| Transparency        | `python3 scripts/verify-image-transparency.py <asset>`      |
| Viewport review     | 390, 768, 1440 px — visual + keyboard + screen-reader       |
| WooCommerce flows   | simple + variable products, cart, checkout failure/recovery |
| Lighthouse          | Performance + accessibility audit                           |

## Promotion path (staging → production)

V2 is packaged as a distributable ZIP and validated in staging before replacing
v1:

```
1. npm run package:theme          # build + verify → dist/skyyrose-flagship-2.zip
2. Upload ZIP to staging WP install; activate
3. Full QA pass (viewports, WC flows, Lighthouse, a11y)
4. Founder approval
5. STOP-AND-SHOW: deploy ZIP to skyyrose.co (replaces skyyrose-flagship)
6. Deactivate / archive skyyrose-flagship (v1)
```

**Deploy is STOP-AND-SHOW.** The promotion to skyyrose.co is irreversible from a
caching perspective — version bump must accompany every deploy so CDN cache
busts. Until the founder confirms approval and triggers the deploy, V2 only runs
in staging.

Once promoted, `SKYYROSE2_VERSION` becomes the cache-bust constant for all
enqueue calls on skyyrose.co — the same role `SKYYROSE_VERSION` plays in v1.

## What this theme is NOT (yet)

- Not live on skyyrose.co yet — currently in staging (v1 is still production)
- Not a product catalog — WooCommerce owns all product facts
- Not a media generator — all imagery requires candidate-bound SOT provenance
- No payment / tax / shipping config — merchant configures those independently

## Anti-patterns

- Using `skyyrose_` prefix in V2 PHP (that's v1 — they must not cross)
- Committing `.min` files without `git add -f` (global gitignore drops them
  silently)
- Running `npm run verify` before `npm run build` (stale assets fail the check)
- Adding a card front without a matching SOT dossier
- Hardcoding a product fallback or inventing inventory in PHP templates
- Editing WC core instead of using hooks and `woocommerce/*.php` overrides
