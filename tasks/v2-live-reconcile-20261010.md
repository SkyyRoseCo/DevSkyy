# V2 live ↔ main reconciliation — 2026-10-10

Worktree `/Users/theceo/DevSkyy-capture-live`, branch `capture/live-v2-20261010`.
Theme `wordpress-theme/skyyrose-flagship-2`. No git index/ref writes were made;
every change below is an unstaged working-tree edit.

## The merge base was wrong, and what that implies

- `07bff115a` sets the theme folder to `a662e707d`'s tree. `a662e707d` is a
  Codex branch commit (`codex/integration-release-20261001`), **not** an ancestor
  of `origin/main`. The real common ancestor is
  `git merge-base a662e707d origin/main` = **`7892b797d`** `[repo]`.
- Since `7892b797d`, main touched only **18 theme files + 4 adds** (commits
  `6e1ec9b9b` express-checkout dedupe, `8d762775d` 2.5.1 release) `[repo]`.
- With `a662` as base, git read every Codex-only file as "main deleted it" and
  every Codex edit as "main reverted it": 19 live files were staged as deleted
  (`product-glb*`, `woocommerce-compat.php`, `home-experience*`,
  `home-art-direction*`, `house-motion*`, `jersey-gallery.php`, two house
  images) and 14 of the 16 auto-merged `M ` files were byte-identical to MAIN
  (`front-page.php`, `footer.php`, `product-card.php`, `theme.js`, `skyy-3d.js`,
  `home.contract.json`, `home.min.css`, `editorial-collection/journal.php`,
  `hero-composed-scene.php`, `product-hero.php` …) — live's work silently
  reverted `[repro: blob-hash compare]`.
- Resolution rule applied instead: **result = LIVE tree (806 files) + main's
  real delta three-way-merged against `7892b797d`** + the non-deployed tooling
  the deploy never ships (restored from `a662`, see below) + main's 4 new files.
  Live is treated as the deployed truth; `[repro]` the Codex worktree
  `/Users/theceo/.codex/worktrees/card-gap-integration/DevSkyy` differs from
  live in 25 files, so it was used only as a classification reference and as
  the source of 3 tooling files that live's runtime needs (verified by running
  them).

## Per-file decisions (every file that is not byte-identical to live)

Live files (9 differ from live `3d19bd48f`; the other 797 are live bytes):

| File | Decision |
| --- | --- |
| `functions.php` | 3-way vs `7892b797d`: clean. Live body + `SKYYROSE2_VERSION` → `2.5.1`. Live already requires `inc/express-checkout.php` (one require). phpcbf then reformatted 69 lines (whitespace/structure only; 45→32 pre-existing PHPCS errors remain in live Codex code: I18n translators comments, short ternaries, Yoda, nonce/sanitize sniffs — not introduced here). |
| `inc/express-checkout.php` | **main's** (#1017 + review fixes): priority-agnostic removal by Stripe object identity, WooPay eligibility, `woocommerce_pay_order_before_payment`. Live's 43-line earlier version dropped. `scripts/test-express-checkout.php`: PASS 37 checks. PHPCS 0. |
| `inc/seo-indexing.php` | 3-way: 1 conflict. Kept **both**: live's `$media['front']['src']` preference for the product social image (with main's alignment) and all of main's #1035 work (pagination canonicals w/ archive args, Jetpack per-post noindex, image-sitemap parent check, native-sitemap gate, no-tagline, Jetpack metadata off). Replaced live's one short ternary (`?: ''`) with an explicit ternary so PHPCS is 0 errors. |
| `package.json` | 3-way: clean. Live `verify` + `jsdom` devDep + main's `2.5.1`. |
| `npm-shrinkwrap.json` | 3-way: clean. Live's jsdom tree + main's `2.5.1`. |
| `style.css`, `readme.txt`, `CHANGELOG.md` | live == base → main's (2.5.1 header / Stable tag / changelog entry). |
| `languages/skyyrose-flagship-2.pot` | regenerated with `scripts/build-pot.py` (652 singular, 1 plural). Delta vs live's catalog is line-number refs + one msgid (`"%s pre-order pieces"`, `v2-preorder.php:127`) that live's catalog had missed — live's .pot was already stale against live's templates. |

Previously-conflicted files that are now **live bytes** (main had no change
since the true base, so the "conflict" was an artifact of the wrong base):
`assets/css/content-page(.min).css`, `assets/css/home-page(.min).css`,
`data/approved-card-fronts.json`, `data/product-presentation-registry.json`,
`inc/approved-card-fronts.php`, `inc/pdp-media-delivery.php`,
`inc/performance.php`, `template-parts/home/editorial-film.php`,
`template-parts/home/editorial-hero.php`,
`woocommerce/single-product/product-image.php`. Same for the 16 auto-merged
files except `CHANGELOG.md`, `npm-shrinkwrap.json`, `readme.txt`, `style.css`.
The 19 staged deletions are restored to live bytes.

Non-deployed tooling (not in the live tree because the deploy ships only
`release: true` files; 75 files):

| File(s) | Decision |
| --- | --- |
| 62 files | main's bytes (== `a662` for all but `CLAUDE.md`, `tests/analytics/README.md`, and the 3 adds `scripts/test-express-checkout.php`, `scripts/validate-sitemap.py`, `scripts/test-validate-sitemap.py`). |
| `scripts/build-critical-css.mjs`, `scripts/test-critical-rendering.php` | `a662` (Codex-evolved; main unchanged since base). `check:assets` reproduces live's `home.min.css` byte-for-byte with this script; `test-critical-rendering.php` PASS. |
| `scripts/build-product-presentation-registry.py` | `a662`. The Codex worktree's newer generator imports `skyyrose.core.card_annotations` / `media_usage`, which do not exist on main. Neither version reproduces live's `data/product-presentation-registry.json` (see "Unverified / open"). |
| `scripts/validate-collection-hero-motion.py`, `scripts/test-collection-hero-motion.py` | `a662` (main's validator lacks `validate_home_journal`, which the Codex test needs). Both fail on this branch — see open items. |
| `scripts/test-seo-indexing.php` | 3-way: base `7892b797d`, ours = Codex worktree, theirs = main. 3 conflicts resolved as union (context keys incl. main's `native_sitemaps`; Codex's full stub block; Codex's imagery-gate block then main's Jetpack-noindex assertions, main's duplicate rejected-media assertion dropped). Removed main's static `is_single()/is_archive()` stubs in favour of Codex's context-driven ones; made the `skyyrose2_media_url` stub null-safe because main's new assertions call `skyyrose2_seo_resolved_context()` before the Codex URL fixture is assigned. PASS (both PASS lines). |
| `scripts/test-performance.php` | Codex worktree version (tests live's `front`-media PDP preload) + 4 stubs live's `inc/performance.php` needs (`skyyrose2_media_uri`, `is_admin`, `is_customize_preview`, `is_preview`). The `a662` and Codex versions both failed without the stubs (`Call to undefined function is_admin()`). PASS. |
| `tests/analytics/rendered-card.php` | Codex worktree version (adds opt-in legacy-frame assertions for live's `product-card.php`). Exit 0. |

## Judgment calls

1. Treated the lead's base as wrong and re-derived the merge from `7892b797d`.
   The end state matches the brief (every live-only feature preserved; all six
   main changes preserved) but the index the lead sees still reflects the old
   merge: commit with `git add -A wordpress-theme/skyyrose-flagship-2
   tools/v2-source-certification tasks/`.
2. `inc/express-checkout.php` = main's reviewed logic (per brief). Live's only
   caller is the single `require_once` in `functions.php`; no live test existed.
3. `inc/seo-indexing.php` keeps live's "exact PDP front wins over attachment"
   image rule on top of main's SEO fix — both behaviours survive.
4. phpcbf was run on the four PHP files this merge authored (`functions.php`,
   `inc/seo-indexing.php`, `inc/express-checkout.php`,
   `scripts/test-seo-indexing.php`) plus `scripts/test-performance.php`; the
   other 797 live files keep their exact live bytes (no formatter pass).
5. Certification: kept main's tooling (`package.py`, `check-*.py`), extended
   the JSONs only. New runtime PHP introduced by this merge was **added** to
   `runtime-php-baseline.json` (8 entries) so the gate covers it.
6. Every file present on live is `release: true` in the boundary — live is the
   deployed set by definition. Eight entries that inherited a non-release or
   contradictory label were reclassified with an explicit live-deployment
   reason (see below).

## Certification changes (`tools/v2-source-certification/`)

- `package-boundary.json`: 684 → **881** files (+197, −0). Classification
  source: 180 by main sibling (same directory + extension), 17 by the Codex
  worktree's boundary. Reclassified to RUNTIME SOURCE/MEDIA `release:true`
  with reason "Present in the live skyyrose.co deployment captured 2026-10-10
  (3d19bd48f); runtime reads it, so it ships.": `data/v2-canonical-media.json`,
  `data/v2-media-eligibility.json`, `data/v2-product-media-index.json`,
  `data/v2-required-media-roles.json`, `assets/editorial-source-fronts/
  {br-006,lh-004,sg-009}-front.webp`. `scripts/test-collection-hero-motion.py`
  → BUILD TOOLING `release:false` (as `scripts/test-validate-sitemap.py`).
  Pin: `7ac027321ce32651` → `bfdd7f508f05df1b`.
- `runtime-php-baseline.json`: 77 → 85 entries; 32 changed (old → new, 16 chars):

```
footer.php                                  0c5d72a8fb11b72f -> 3a21b807edb38de6
front-page.php                              76b502c07294e504 -> 45d9a5289ec39a25
functions.php                               1a30b4380f3730af -> 9aeea9bd1f702b07
inc/approved-card-fronts.php                b8152869e4b0c4b0 -> 64d247522897ff86
inc/card-garment-highlight.php              (new)            -> c4982a810c4197d3
inc/express-checkout.php                    (new)            -> 5f8496b0c7c35c66
inc/frame-delivery.php                      1c54edfc18e8a70b -> 8cfca52d7b12b734
inc/launch-readiness.php                    5ce5a813ad166303 -> b753741a791d3d29
inc/pdp-media-delivery.php                  359ec0d85b88371a -> 3225b5c4a990eb36
inc/performance.php                         13e596bde76031a6 -> 9d7ee4b82297347d
inc/product-glb-links.php                   (new)            -> 5e6896e6f07f51b1
inc/product-glb.php                         (new)            -> b99338b2a87155b5
inc/seo-indexing.php                        559b6a99d41ad96a -> b9c022ed913ba104
inc/v2-media-eligibility.php                (new)            -> d16ed05f341bcc1e
inc/woocommerce-compat.php                  (new)            -> 98fb6726e5704a5a
scripts/test-performance.php                11784d036c9a06f2 -> fd8080a3d91c2efe
scripts/test-seo-indexing.php               6df7a0e0a72d1639 -> 01d262fdafa1c592
template-parts/collections/arrival.php      943c0986462f795d -> f3cdbf1023059000
template-parts/collections/editorial.php    (new)            -> a51251053a582c15
template-parts/collections/world.php        c9836d1c9725bd8a -> 31906755bba5b841
template-parts/commerce/hero-composed-scene.php a0af556b79dd3507 -> 6b27d6adbc67ad4b
template-parts/commerce/jersey-gallery.php  (new)            -> 806265cbaffa0818
template-parts/commerce/product-card.php    3b2100f09f512015 -> a6c2b8b75379bb6f
template-parts/commerce/product-hero.php    b20abda3349f1b62 -> b6b2085dc8b2796e
template-parts/home/editorial-collection.php 72f00945ff87bb75 -> 248f2a752611cf46
template-parts/home/editorial-film.php      891c0aa25ed392bb -> a74b565a58ad6e96
template-parts/home/editorial-hero.php      4655bcb9573b2507 -> ad0d48970a5c899f
template-parts/home/editorial-journal.php   3d8507eb2483a714 -> 179725797ee2e224
template-parts/home/kids-capsule-reveal.php 3d4bbdf3ec3d742e -> 05e413de6c97f6bc
template-parts/immersive/world.php          1a4a06cc328426ab -> a31678d349084227
template-parts/v2-preorder.php              9e9f80e1388f9f84 -> 8c8f4a9dcbb87c5d
woocommerce/single-product/product-image.php 7185622650ec5859 -> 676c924215fb91cd
```

- `build-inputs.json` `input_hashes`: 11 of 59 pins changed; `current_registry_sha256`
  unchanged (`351a6bbe80face17…`, product registry untouched):

```
tools/v2-source-certification/package-boundary.json        7ac027321ce32651 -> bfdd7f508f05df1b
tools/v2-source-certification/runtime-php-baseline.json    616c3598e63dba3b -> 3c6d0876121a03c3
…/assets/css/critical/home.contract.json                   e636ec832079cb3c -> b92a0b4c5d758bb4
…/assets/js/theme.js                                       54fb02117e03aa1c -> a355cb4ae8195a62
…/data/approved-card-fronts.json                           c9a35409c5af2fac -> ae74591c92d43418
…/data/collection-hero-motion.json                         c6d99877bff4f1d9 -> 9b80a7914b2692c1
…/data/opening-product-media.json                          6de9889f180edf3b -> 15c259ee029db764
…/npm-shrinkwrap.json                                      10677478c055e1c2 -> c4b15fa2a205215f
…/package.json                                             e6c05de19fd61337 -> 48059bfc4e4dccf4
…/scripts/build-critical-css.mjs                           76b0c2b77f124847 -> 8b4f933553010729
…/scripts/build-product-presentation-registry.py           b16bfd6a65f58f61 -> c0563e46dfddef92
```

- `generated-outputs.json` untouched: live ships 8 minified files it does not
  enumerate (`cookie-consent.min.css`, `home-art-direction.min.css`,
  `home-experience.min.css`, `product-glb.min.css`, `experience-analyzer.min.js`,
  `home-experience.min.js`, `house-motion.min.js`, `three.module.min.js`). No
  gate reads that list; flagged for the certification owner.

## Gate results (this session, worktree)

- Conflict markers in theme + certification dir: **0**.
- `php -l` on all 101 theme PHP files: 0 failures.
- PHPCS (theme `phpcs.xml`): `inc/express-checkout.php` 0/0,
  `inc/seo-indexing.php` 0 errors, `functions.php` 32 errors / 6 warnings (all
  pre-existing in live's Codex code; 13 fixed by phpcbf), `scripts/test-seo-indexing.php`
  78 errors (main's own version has 58; tooling), `scripts/test-performance.php` 38.
- `scripts/test-*.php`: seo-indexing PASS, performance PASS, critical-rendering
  OK, global-shell-contract PASS, page-service-template PASS, prelaunch-safety
  PASS, express-checkout PASS (37 checks). **test-marketplace-registry.php
  FAIL** (see open items).
- `scripts/test-*.py`: test-validate-sitemap 8/8 OK. **test-collection-hero-motion
  2 errors** (see open items).
- `tests/analytics`: consent.test.cjs 29/29, relay.php 36 checks PASS,
  bootstrap.php 13 PASS, rendered-card.php exit 0. `sync-analytics.py --check`
  could not run (repo-root `node_modules/prettier` absent in this worktree).
- `npm run check:assets`: "Verified 25 CSS and 17 JS assets" + critical
  `home.min.css` 13580 bytes — live's minified files reproduce byte-for-byte
  with the pinned toolchain (node 22.23.3, `npm ci` from the live shrinkwrap).
- `python3 scripts/build-pot.py --check`: current (652/1).
- `check-current-scenes.py`: PASS. `package.py`: "Validated 772 runtime package
  entries". Hash replica: every `build-inputs` pin and every baseline entry
  matches disk.
- `check-integrity.py`: fails on toolchain pin (`node 22.23.2` pinned,
  `22.23.3` installed) before any content check — environment, same on main.

## Unverified / open (lead or founder call)

1. **`data/product-presentation-registry.json` (live) is bound to a product
   registry digest `2b280537…`; the current `logo-registry.json` is
   `351a6bbe…`** `[repo]`. `check:registry` is therefore stale with any
   generator, and live's own `data/opening-product-media.json`
   (`product_sot_sha256 4ccfbe18…`) fails live's
   `skyyrose2_validate_product_card_media_contract()` against it. At runtime
   `functions.php:1668` then empties the opening-media manifest `[repo,
   inferred runtime]`. This is live-as-deployed; fixing it means regenerating a
   product-fact projection against the current registry, which is outside this
   merge. `test-marketplace-registry.php` fails for the same reason.
2. `scripts/validate-collection-hero-motion.py` (a662) expects the pre-Oct-8
   hero masters; live's `data/collection-hero-motion.json` binds the
   `cinema-20261008` sources → "signature is not bound to its approved hero
   master". The validator predates the live feature; `verify-marketplace.sh`
   (and thus `npm run verify`) stops here and at `check:registry`.
3. `scripts/test-collection-hero-motion.py` + validator read
   `get_product(sku)["images"]["card_front"]`, a Codex-core field that main's
   `skyyrose.core.product` does not expose → KeyError.
4. Live's `package.json` `verify` references `tools/v2-runtime/
   test-commerce-page-assets.php`, `test-card-garment-highlight.php`,
   `test-collection-image-preservation.php`, which exist only untracked in the
   Codex worktree (outside the theme; not brought in).
5. `npm ci` was run inside the worktree theme dir (gitignored `node_modules/`,
   44 packages); `package.py` left gitignored `dist/`. Both are regenerable;
   left in place for the lead's own verification run.
