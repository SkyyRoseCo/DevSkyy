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
