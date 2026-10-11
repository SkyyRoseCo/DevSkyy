# V2 release 2.5.3 certification lineage (2026-10-11)

**Scope:** the Jetpack image sitemap only. No product fact,
`logo-registry.json`, media inventory, or unrelated pin changed. The
certification entries below change only because shipped bytes changed
(`inc/seo-indexing.php`, its contract test, and the version triple).

## Live defect (`[live 2026-10-11]`, bare URL `https://skyyrose.co/image-sitemap-1.xml`)

Jetpack 16.3 (`Jetpack_Sitemap_Buffer_Image_XMLWriter`) served this file:

- 307 `<url>` entries for 285 unique `<loc>`s. 20 locs repeat: 19 product pages
  (`/product/br-001/` and `/product/br-003/` three times each) and the
  attachment page `/photoroom_20260201_143638/`. Jetpack emits one `<url>` per
  image attachment.
- Only 31 unique locs are product pages. The other **254 are attachment pages**
  (`/signature-collection-red-rose-beanie_depth-3/`,
  `/skyyrose-love-hurts-collection-fanni-2/`, `/woocommerce-placeholder/`, …).
  The brief's estimate was about 21. Jetpack falls back to
  `get_permalink( $attachment )` when the parent permalink is empty.
- **All 307 `<image:loc>` elements are empty.** Jetpack writes
  `wp_get_attachment_url()`. The theme's V2 media gate
  (`inc/v2-media-eligibility.php:251`, `skyyrose2_media_url` at `PHP_INT_MAX`)
  returns `''` for every URL outside the theme. It skips only non-AJAX admin
  requests, so it also runs during Jetpack's cron build. `validate-sitemap.py`
  does not inspect `<image:loc>`, so it never reported this.
  - Symptom: `[live]`. Code path: `[repo]`.
  - Gate behavior: `[repro]`. The gate file was loaded outside admin with
    stubbed hooks.
    - An uploads URL returned `''`.
    - `assets/v2-original/products/br-001.png` passed unchanged.

## Why one image per page, not grouping

Google allows up to 1,000 `<image:image>` per `<url>`, but Jetpack 16.3 cannot
emit more than one:

- Both buffer implementations build the XML from the item array's keys.
  `Jetpack_Sitemap_Buffer_XMLWriter::array_to_xml()` and the DOM fallback's
  `array_to_xml_string()` name each element after its key, and PHP array keys
  are unique.
- A list (`0`, `1`, …) under `url` would call `startElement( 0 )` or
  `createElement( '0' )`, which is not a valid element name.
- `jetpack_sitemap_image_sitemap_item` is the only hook on an image entry.
  `jetpack_print_sitemap` runs only on page sitemaps
  (`sitemap-builder.php:968`).
- Nothing filters the stored sitemap XML when it is served (`sitemaps.php`
  `callback_action_catch_sitemap_urls`).

Next best option: one entry per indexable parent page, carrying the image that
page actually shows. A product's other images remain on its PDP.

## What changed

- `inc/seo-indexing.php`
  - `skyyrose2_seo_image_sitemap_entry()` keeps an attachment only when all of
    these hold:
    - it has a parent;
    - the parent is a published `WP_Post` and not password-protected;
    - the parent's type is a sitemap type (post, page, product), never an
      attachment;
    - the parent is not in `skyyrose2_seo_sitemap_excluded_ids()`;
    - the parent is not Jetpack-noindex;
    - it is the parent's lowest-ID image attachment. This rule is stateless,
      which matters because Jetpack walks IDs ascending across cron batches;
    - the parent has an eligible image.
  - The image a product page shows is its PDP permitted primary,
    `skyyrose2_product_commerce_media()['front']['src']`, else its first gated
    ID. This is the same chain as the live `og:image` and Product schema
    (`assets/v2-original/products/br-001.png` on `/product/br-001/`, `[live]`).
    Any other page gets its gated attachment URL. The result passes
    `skyyrose2_media_url()` last, so the URL gate is never bypassed.
  - The skip filter (`jetpack_sitemap_image_skip_post`) now applies the full
    rule.
  - The new item filter (`jetpack_sitemap_image_sitemap_item`, priority 20, 2
    args) sets `<loc>` to the parent permalink and `<image:loc>` to the eligible
    image. It returns null (a Jetpack no-op) when there is no entry.
  - Both filters pass through unchanged while a supported SEO plugin is active.
- `scripts/test-seo-indexing.php` adds 21 image-sitemap assertions (24 in
  total). They use record, child and gated-URL fixtures, and cover registration
  and pass-through under `AIOSEO_VERSION`.
  - The old assertion "Unattached images are kept." encoded the defect. It is
    now "…is skipped". This is a required behavior change, not a weakened test.
  - The three other old image assertions still apply, with fixtures.
- Version 2.5.2 -> 2.5.3 in these files:
  - `functions.php`, `style.css`, `readme.txt`;
  - `package.json`, `npm-shrinkwrap.json` (root and package entry);
  - `tests/analytics/README.md`;
  - POT `Project-Id-Version`, via `npm run build:i18n`.
- CHANGELOG and readme 2.5.3 entries.

## Lineage

| Entry (file)                                  | Old sha256          | New sha256          | Why                                 |
| --------------------------------------------- | ------------------- | ------------------- | ----------------------------------- |
| baseline `functions.php`                      | `53e0ce58424a32e0…` | `dfb0b66d7e7f1c99…` | `SKYYROSE2_VERSION` 2.5.3 only.     |
| baseline `inc/seo-indexing.php`               | `13cd1cf4609e29b1…` | `99dea849348ec5b2…` | Image-sitemap entry rule + filter.  |
| baseline `scripts/test-seo-indexing.php`      | `ccdb9453f2181a12…` | `ebccda8c60f61959…` | Image-sitemap fixtures/assertions.  |
| input `runtime-php-baseline.json`             | `5411b4a6d8723dd2…` | `fea4cc5d1733e8f4…` | Follows the three baseline entries. |
| input `wordpress-theme/…/package.json`        | `5a6084e9ef8de3b8…` | `5c886030bc1c99e6…` | Version 2.5.3.                      |
| input `wordpress-theme/…/npm-shrinkwrap.json` | `12b1af5a8551af24…` | `87239ce441c1fa38…` | Version 2.5.3 (root and package).   |

`package-boundary.json` is unchanged: no file was added or removed.
`generated-outputs.json` pins no hashes for the POT.

## Evidence (this session)

- Toolchain: Node 22.23.2 (`~/.local/opt/node-v22.23.2-darwin-arm64`), npm
  10.9.8, Python 3.12.12.
- Fixtures: a fresh `prepare-native-fixture.py` fixture (7 hashes) and a
  hash-checked `V2_NATIVE_JS_FIXTURE` (2 hashes).
- Worktree: the sparse worktree needed `git sparse-checkout add assets/products`
  so `check-integrity.py` could read the bound garment artwork.
- `scripts/test-seo-indexing.php` RED: the final test file run against the base
  runtime (`HEAD` `b3fbdcc6a`) fails 15 assertions. A pass-through stub was
  added for the absent new function so the run reaches the assertions.
- GREEN: the same test passes on the changed runtime.
- PHPCS on `inc/seo-indexing.php`: 0 findings, same as base.
  - The test harness carries pre-existing stub violations.
  - The 10 auto-fixable spacing violations this change added were fixed with
    phpcbf on that file only, before re-pinning.
- `npm run lint:php`: exit 0.
- `npm run package:theme` (build + verify + package): exit 0, 0 `not ok`.
  Result: "Validated 773 runtime package entries; SHA-256 `fe3f01f39decdaa6…`".
  This was rerun after the prettier pass on `CHANGELOG.md`, which ships in the
  package. The tree is unchanged afterwards apart from this change.
- `pytest tests/test_v2_*.py tools/v2-source-certification`: 73 tests, 0
  failures, 0 errors, 0 skipped (junit).
- `python -m unittest discover -s tools/v2-source-certification`: OK.
- `scripts/sync_product_registry.py --check`: PASS.

## Not verified / open

- Nothing deployed. Production behavior after deploy is unverified.
- The read-only remote WP-CLI probe was denied by the session's permission
  classifier. Attachment parentage was therefore inferred from the public XML,
  not read from the database.
- **Attachment pages are indexable thin pages** (`[live]`, four probed:
  `/signature-collection-red-rose-beanie_depth-3/`,
  `/skyyrose-love-hurts-collection-fanni-2/`, `/photoroom_20260201_143638/`,
  `/woocommerce-placeholder/`).
  - Each returns 200 with robots `max-image-preview:large`, no noindex, a
    self-canonical, and the filename as title.
  - This change removes them from the image sitemap, but they stay crawlable.
  - Remedy (founder call, not done): disable attachment pages. In WordPress 6.4+
    that is the site option `wp_attachment_pages_enabled = 0`, which redirects
    to the file URL; check that redirect against the media gate first.
    Alternatively, add `noindex` for `is_attachment()` in
    `skyyrose2_seo_robots()`.
- After deploy, Jetpack rebuilds only on its own cron. The stored `jp_sitemap`
  rows keep serving today's XML until the next rebuild.
  - `JP_SITEMAP_INTERVAL` is 12 h. The 60 s value applies only under
    `JETPACK_DEV_DEBUG`.
  - Each cron run builds up to `JP_SITEMAP_UPDATE_SIZE` = 100 files
    (`update_sitemap()`). At this site's size the whole set should regenerate in
    a single run.
  - Another session today (Lane C row in `.wolf/memory.md`) observed the next
    Jetpack sitemap cron about 9 h out at 10:15.
- Post-deploy check against the bare URL, without `?cb`:
  - every `<loc>` is unique;
  - no `<image:loc>` is empty;
  - no `<loc>` is an attachment page. If nothing qualifies, Jetpack deletes the
    image sitemap and a 404 is the expected result.

---

# 2.5.3 Lane B: collection imagery and media cache keys

This lane was built on the Lane A branch `fix/v2-image-sitemap-20261011`
(`5adf98061`). Lane A then landed on `main` as squash `7971aa8fd` (#1068), so
the branch now merges `main` and targets it. The version stays 2.5.3. It ports
the remaining V2 collection-imagery gate from local-only commit `d0a014a33`
(`capture/codex-v2-card-gap-20261010`). The port takes only Codex's side of the
3-way diff against the true merge base `7892b797d`
(`git merge-base d0a014a33 5adf98061`). An earlier draft named `7ed2180b5`,
which was wrong. No product fact, `logo-registry.json`, presentation registry,
media inventory, usage grant or receipt changed.

## Live state before the change (`[live 2026-10-11]`, cache-busted HTML)

The current media gate strips these slots on production, so each one renders
empty:

- `/collections/black-rose/`: the origin-story `<picture>` has no image. It
  shows only the caption "Black Rose / Look 01".
- `/collections/`: all four chapter `<picture>` elements are empty, and the
  lockups are stripped.
- `/`: all four chapter figures are empty. The worlds rail has zero worlds.
- `/pre-order/`: there are zero merchandise scenes. The template's inventory
  scan required `merchandise_scene` in the record's own `roles`, and that role
  exists only through a founder usage grant.

## What changed

- `inc/v2-media-eligibility.php` takes the following from `d0a014a33`:
  - Role-not-in-record branch: a new role is admitted only when the unchanged
    original still passes its own review **and** an exact, hash-bound founder
    usage grant names that role.
  - New functions: `skyyrose2_media_usage_roles()`,
    `skyyrose2_media_effective_roles()`, `skyyrose2_collection_media()` (reads
    the registry's `collections.*.imagery` binding by sha and usage-adoption
    pointer; checks SKU, collection, preorder partition, pixel size and alt
    text) and `skyyrose2_collection_media_markup()` (an uncropped `<img>` with
    the rendition srcset).
  - `?v=<sha256>` cache key in `skyyrose2_media_uri()`. `skyyrose2_media_url()`
    normalizes to it, so stale `?v=` values are replaced.
  - Every srcset candidate, attachment `src`, variation `full_src` and CSS
    `url()` is rewritten to its keyed URL.
  - `skyyrose2_media_usage_document()` moved above its first caller, as in
    `d0a014a33`. The offline contract tests evaluate the gate only up to
    `skyyrose2_media_start_buffer()`.
  - Main's `house_art` comment is kept.
  - `skyyrose2_collection_hero_uri()` is not taken, because nothing here calls
    it.
- Consumers:
  - `approved-card-fronts.php` uses effective roles, and its renditions use
    `media_uri`.
  - `launch-readiness.php` admits a `FOUNDER_ACCEPTED` front via `path_allowed`
    for `pdp_on_model_front`.
  - `pdp-media-delivery.php` compares `media_url( attachment )` to the keyed
    front. Without this, the PDP front drops once URLs are keyed.
  - `performance.php` gains `skyyrose2_performance_collection_preload()` for the
    `/collections/` index only. Its href, imagesrcset and imagesizes equal the
    eager chapter image.
  - The collection-world route keeps its arrival preload, because the arrival is
    unchanged.
- Templates:
  - `collections/index.php`: `collection_hero` figures; the lockup `<h2>` is
    kept.
  - `collections/story.php`: `collection_story` replaces the retired lookbook.
  - `home/living-archive-worlds.php`: Signature and Black Rose heroes, and the
    Love Hurts story.
  - `v2-preorder.php`: `merchandise_scene` comes from the registry binding.
- CSS (`collection-world.css`, `content-page.css`): uncropped (`contain`) rules
  for the story image, the index chapters and the pre-order intro.
- Tests:
  - New `tools/v2-runtime/render-collection-imagery.php` (offline renderer) and
    `tools/v2-runtime/test-collection-imagery.php` (render contract).
  - `npm run verify` now also runs `test-v2-media-eligibility.php`,
    `test-media-usage.php`, `test-collection-imagery.php` and
    `test-preorder-collections.php`.
- Existing tests updated, each for a required behavior change. None was
  weakened:
  - `test-homepage-hero-gate.php`: the expected URL now carries `?v=<hero sha>`.
    This is stricter, because it is bound to the bytes.
  - `test-pdp-gallery.php`: there are 33 PDP fronts. 18 are reviewed PDP roles
    and 15 come from founder grants, and the test counts the grants exactly.
    - No real card-only SKU remains, so the card-only case became "br-003's PDP
      role exists only through its exact grant". A grant borrowed by another SKU
      is rejected. Rejected Woo attachments never enter the gallery.
  - `test-home-labels.php`: the stub dependency is now
    `skyyrose2_collection_media`, and the label assertions are unchanged.

## Not taken (kept main), with the reason

- Homepage chapter figures (`home/editorial-collection.php`):
  `scripts/validate-collection-hero-motion.py`, a gate inside `npm run build`,
  pins them to `skyyrose2_collection_hero_motion( $slug, $collection['hero'] )`.
  Taking Codex's version fails 3 of its tests, so it was reverted. These figures
  stay empty on production. Founder call.
- Header collection previews (`inc/global-shell.php`): the JS preview stage
  enlarges the thumbnail's `currentSrc` into a 1024×576 stage. With the `128px`
  sizes, that would show a 160–320w rendition at stage size. Founder call.
- Monument copy (`skyyrose2_collections()['line']`) and SEO `og:image` /
  `primaryImageOfPage` are not imagery rendering, and they belong to Lane A's
  file. The arrival, which they describe, is unchanged.

## Lineage

| Entry (file)                                             | Old sha256          | New sha256          |
| -------------------------------------------------------- | ------------------- | ------------------- |
| baseline `inc/approved-card-fronts.php`                  | `64d247522897ff86…` | `2d272ae096846f50…` |
| baseline `inc/launch-readiness.php`                      | `b753741a791d3d29…` | `aeffd7fdc34b988f…` |
| baseline `inc/pdp-media-delivery.php`                    | `3225b5c4a990eb36…` | `a5e871453a511e54…` |
| baseline `inc/performance.php`                           | `9d7ee4b82297347d…` | `56be7b798ac34885…` |
| baseline `inc/v2-media-eligibility.php`                  | `18b41121eeed9116…` | `f82fb4f17ef77be4…` |
| baseline `template-parts/collections/index.php`          | `805331e5e4b9d109…` | `dfd9ffc8ab897346…` |
| baseline `template-parts/collections/story.php`          | `a81db476080e7f16…` | `94bf267469981ec2…` |
| baseline `template-parts/home/living-archive-worlds.php` | `8df1b5628510b29b…` | `159bf8c43a25cc6a…` |
| baseline `template-parts/v2-preorder.php`                | `8c8f4a9dcbb87c5d…` | `5640e2431429e900…` |
| input `runtime-php-baseline.json`                        | `fea4cc5d1733e8f4…` | `6c2e3c47f5a0963c…` |
| input `wordpress-theme/…/package.json`                   | `5c886030bc1c99e6…` | `b8e48950499a9761…` |

This is an entry-only re-pin: no key was added or removed.
`package-boundary.json` and `generated-outputs.json` are unchanged, because no
theme file was added or removed and `generated-outputs.json` pins no hashes.

## Evidence (this session)

- RED, from the pristine Lane A tree (`git archive 5adf98061`):
  - `test-v2-media-eligibility.php` fails at line 35 ("Public image cache key is
    bound to the verified bytes").
  - `test-media-usage.php` fails at line 10 (undefined
    `skyyrose2_media_usage_roles()`).
  - `test-collection-imagery.php` fails 11 checks.
  - `test-v2-delivery-derivatives.php` fails ("Responsive card cache version
    matches its own derivative bytes").
- GREEN: all four pass on this branch. `test-media-usage.php` reports
  `pdp_on_model_front` 15, `collection_hero` 4, `collection_story` 4 and
  `merchandise_scene` 3. It now reports the negative checks it actually executes
  (148; see the round-2 section). The earlier "100" was a hard-coded literal.
- Toolchain: Node 22.23.2 (`~/.local/opt/node-v22.23.2-darwin-arm64`), npm
  10.9.x. The fixtures are a fresh `prepare-native-fixture.py` fixture (7
  hashes) and a `V2_NATIVE_JS_FIXTURE` whose 2 hashes match the pins. The
  worktree needed `git sparse-checkout add assets/products`.
- `npm run lint:php`: exit 0.
- `npm run package:theme`: exit 0, 0 `not ok`. Result: "Validated 773 runtime
  package entries; SHA-256 `0e3bbbc08c4365ea…`".
- `pytest tests/test_v2_*.py tools/v2-source-certification`: 73 tests, 0
  failures, 0 errors, 0 skipped (junit). `unittest discover`: OK.
- `scripts/sync_product_registry.py --check`: PASS.
- PHPCS on the changed theme files: every file is at or below base, except
  `inc/v2-media-eligibility.php`, which goes from 148/55 to 185/63.
  - That increase is the ported Codex code in the file's dense single-line house
    style.
  - phpcbf was not run, because it would reflow a pinned file.
- Rendering was checked offline and by eye (Playwright, 1440×900 and 390×844):
  - Every role image is uncropped: rendered aspect matches natural aspect within
    0.001, except the worlds rail, which letterboxes with `contain`.
  - No horizontal overflow.
  - br-004 hoodie, sg-009 sherpa, br-001 crewneck, lh-004 bomber and kids-002
    set were confirmed in their slots.

## Not verified / open

- Nothing was deployed.
- Jetpack Image CDN (Photon) drops the origin query string by default (`[docs]`
  `class-image-cdn-core.php`: `jetpack_photon_add_query_string_to_domain`
  defaults to false). The live homepage LCP image is rewritten by Jetpack Boost
  to `i0.wp.com/…/house-monument-20260928.webp?ssl=1` (`[live]`).
  - Photon-served copies therefore do not carry the cache key, and Photon caches
    them by path.
  - No bytes change under an existing path in this release, so nothing goes
    stale today.
- The usage grants and their authority name `target`
  `https://staging-7e48-skyyrose.wpcomstaging.com`.
  - The gate compares that string inside the grant documents, not the request
    host. The grants therefore also admit the roles on skyyrose.co.
  - Whether that target string should name production is the founder's call. No
    grant was edited.
- QC flag carried from the fidelity review: kids-002 `garment.features` says
  "lavender/light-pink hood", but the real photo and the slot show a deep-purple
  hood. This is a registry text discrepancy, not a slot defect. No registry edit
  was made.

## PR #1070 review response (Codex review of `fa5e872db`)

- **P1, repeated hashing (fixed).** `skyyrose2_media_sha256()` is now a
  request-scoped memo of the file sha256.
  - The memo is keyed by path plus the current stat identity (inode, size,
    mtime, ctime), and the stat is re-read on every call. Any write that changes
    the size or a timestamp is therefore hashed again.
  - The 7 `hash_file()` calls in the gate now go through it.
  - Offline `/collections/` render: 1.47 s became 0.16 s `[repro]`. The base,
    which renders no images, takes 0.07 s.
  - Limit: a rewrite with the same size inside the same second, during one
    request, is detected on the next request. The gate only decides which URLs
    to emit; nginx serves the bytes either way.
- **P2, preorder intro without a scene (fixed).** The two-column intro now
  applies only with `.sr2-reserve-edit__intro--scene`, which is emitted only
  when a scene rendered.
  - `test-preorder-collections.php` gained 2 assertions.
  - RED: on `25840c9db` the template fails "Only groups with a rendered scene
    take the two-column intro". GREEN: passes after the fix.
- **P1, grant `target` = staging (not changed; founder call).** The usage
  authority's antecedent scope is a staging update. Enforcing the target against
  the runtime host would turn every grant off on skyyrose.co. Keeping the
  current string comparison publishes the roles on production on the strength of
  a staging-scoped decision.
  - Which one ships is the founder's decision, and it gates this PR's production
    effect. No grant was edited.
- **P2, preload vs Photon (open; not reproduced).**
  - Live `/collections/` today shows no `i0.wp.com` image, only the preconnect
    `[live]`.
  - On the homepage, Jetpack Boost rewrote the LCP house art to Photon, while
    the theme preload stays at the origin `[live]`. That mismatch existed before
    this PR.
  - Whether Boost also rewrites the new eager `/collections/` image after deploy
    can only be checked after deploy. If it does, the preload would duplicate
    the fetch.
  - Remedy options are to drop the theme preload where Boost optimizes the LCP,
    or to emit the Photon URL. This is a post-deploy check.

## PR #1070 round 2: retarget to `main` and mechanical review fixes

- **Retarget.** #1068 (Lane A) landed on `main` as squash `7971aa8fd`. Its bytes
  for every Lane A file equal `5adf98061`. Merge commit `9def34d3a` merges
  `origin/main` (`132598443`) into this branch; it was a new merge commit, not a
  rebase or force-push. The only conflicts were Lane B's own additions
  (`CHANGELOG.md`, `readme.txt`, this file) and the two Lane B pins in
  `build-inputs.json`. Lane B's side was kept in each. After the merge, all 106
  `build-inputs.json` pins matched their bytes. The version triple stays 2.5.3.
- **3-way attribution, corrected base.** The true merge base is `7892b797d`. The
  three sides were base `7892b797d`, main `5adf98061` and Codex `d0a014a33`,
  compared with the port `25840c9db`. A line was a candidate revert if main
  added it after the base and the port lacks it.
  - **Theme code** (`approved-card-fronts.php`, `launch-readiness.php`,
    `pdp-media-delivery.php`, `v2-media-eligibility.php`, `v2-preorder.php`):
    every candidate sits inside a region Codex also rewrote, so it is a 3-way
    conflict that takes Codex's side. Main's guards survive in the new form:
    - `media_uri()` still calls `path_allowed()`;
    - the PDP file-hash check is kept;
    - the preorder inventory scan is replaced by the documented registry
      binding.
  - **Test code**: `test-pdp-gallery.php` is the only file where the port
    dropped main lines that Codex did not touch. That is the documented
    adaptation to the 15 `pdp_on_model_front` grants:
    - 18 PDP fronts became 18 + 15;
    - the card-only br-003 fixture became a grant-only fixture;
    - the rejected-attachment and cross-SKU negatives are kept.
  - `fa5e872db` and `85ed1207c` only route `hash_file()` through the memo.
    Neither reverts main.
  - The merge `9def34d3a` drops no line that main added to `package.json`,
    `ci.yml` or `sync_product_registry.py`.
  - **No main change was reverted.**
- **`test-v2-delivery-derivatives.php` in `npm run verify`.** It is wired into
  `package.json` next to `test-v2-media-eligibility.php` and
  `test-media-usage.php`. It ran inside `npm run package:theme`: "PASS 173
  actual delivery copies".
  - The input pin was re-pinned entry-only: `package.json` `6cee7ab2…` became
    `b8e48950…`.
  - `package-boundary.json` holds no hash for `package.json`, and
    `runtime-php-baseline.json` is unchanged.
- **`test-media-usage.php`**
  - It reports `negative_cases` from a counter that increments only after a
    negative check passes. The counter replaces the literal `22 * 4 + 12`.
    Without the new cases it counts 101, not 100.
  - New on-disk tamper cases run in a child PHP process. The gate root is a
    `define`, so it cannot be changed in the parent. The child runs against a
    temp copy of `data/v2-media-eligibility.json` and
    `data/v2-media-reviews/*.json`.
  - A positive control comes first: the pristine copy grants exactly the 26 real
    roles.
  - Grant cases: one adoption's `usage-01` grant gets a trailing byte, widened
    `roles`, and `target` moved to `https://skyyrose.co`. Each is rejected, and
    the other 21 adoptions are unaffected.
  - Authority cases: `usage-authority-20261006.json` gets a trailing byte and a
    production `target`. Each revokes all 22 adoptions.
  - The restored copy grants the real roles again.
  - Total: 148 executed negative checks. No real grant or receipt file was
    edited.
  - RED: a scratch clone with the grant `hash_equals` check removed from
    `skyyrose2_media_usage_document()` fails "Tampered grant (byte) rejected".
    On the same mutant, the previous test passes and prints "100". GREEN: the
    real gate passes.
- **Gates (this session).**
  - Node 22.23.2 and the main `.venv`.
  - Fresh fixtures: `prepare-native-fixture.py` (7 hashes) and a hash-checked
    `V2_NATIVE_JS_FIXTURE` (2 hashes).
  - `git sparse-checkout add assets/products`.
  - `npm run lint:php`: exit 0.
  - `npm run package:theme`: exit 0, 0 `not ok`. Result: "Validated 773 runtime
    package entries; SHA-256 `0e3bbbc08c4365ea…`", unchanged.
  - `pytest tests/test_v2_*.py tools/v2-source-certification`: 73 tests, 0
    failures, 0 errors, 0 skipped (junit).
  - `sync_product_registry.py --check`: PASS.
- The founder decision on grant `target` (staging versus production) is still
  open. It is not resolved here.
