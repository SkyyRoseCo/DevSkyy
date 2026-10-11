# V2 release 2.5.2 certification lineage (2026-10-11)

**Authority:** founder ruling 2026-10-10: "homepage hero should be the same hero
still on staging". That still is `assets/images/house-monument-20260928.webp`,
sha256 `05e9890ba85971569b7a422b892e3db3d51ae53ac6efb6bdd2d55f85c7859811`. The
founder approved fixing the hero; the certification entries below change only
because shipped bytes change. No product fact, `logo-registry.json`, or
unrelated pin changed.

## Root cause

`template-parts/home/editorial-hero.php` renders the hero only when
`skyyrose2_media_uri( 'assets/images/house-monument-20260928.webp' )` is
non-empty. On main `fe2b48098` it returned `''` for two reasons:

1. `skyyrose2_media_record_allowed()` routed only `housemark|font|icon` through
   the canonical-exact-bytes path. The hero's eligibility record is
   `kind: house_art`, so it fell through to the photograph branch and failed.
2. The record's `restoration_receipt`
   (`data/v2-media-reviews/homepage-art-restoration-20261006.json`) was not
   present on main, and `data/v2-canonical-media.json` had no hero entry.

## What changed

Ported from local commit `d0a014a33` (`capture/codex-v2-card-gap-20261010`). The
merge base `7892b797d` predates both versions of the gate file, so the 3-way
diff reduces to main versus Codex. Only the hero path was taken:

- `inc/v2-media-eligibility.php`: `house_art` joins the canonical kinds; the
  canonical pin moves `b791146c…` -> `b4957a6f…`; the `house_art` block requires
  roles exactly `["homepage_hero"]`, no SKU argument, empty `skus` and
  `collections`, and a hash-bound restoration receipt whose schema, scope,
  source path+sha, founder request text and staging target all match.
  `skyyrose2_media_usage_document()` already existed on main and is reused.
- `data/v2-canonical-media.json` and the receipt: byte-identical to `d0a014a33`
  (`b4957a6f…`, `b9f29c5e…`).
- `tools/v2-source-certification/package.py`: same pin, plus a
  `house_art_restored()` mirror of the PHP checks (fail-closed parity).
- Not taken: the `?v=<sha>` cache-key rewrite, usage-adoption roles, effective
  roles and the collection media helpers. No main template calls them; they
  change every media URL and are a separate decision.
- Version 2.5.1 -> 2.5.2 (`functions.php`, `style.css`, `readme.txt`,
  `package.json`, `npm-shrinkwrap.json`, `tests/analytics/README.md`), CHANGELOG
  entry, POT `Project-Id-Version` regenerated.
- `tools/v2-runtime/test-homepage-hero-gate.php` added and wired into
  `npm run verify`.

## Lineage

| Entry (file)                                  | Old sha256          | New sha256          | Why                                                     |
| --------------------------------------------- | ------------------- | ------------------- | ------------------------------------------------------- |
| baseline `functions.php`                      | `9aeea9bd1f702b07…` | `53e0ce58424a32e0…` | `SKYYROSE2_VERSION` 2.5.1 -> 2.5.2 only.                |
| baseline `inc/v2-media-eligibility.php`       | `d16ed05f341bcc1e…` | `18b41121eeed9116…` | `house_art` branch + canonical pin.                     |
| input `runtime-php-baseline.json`             | `3c6d0876121a03c3…` | `0c4b3b9d1e047068…` | Follows the two baseline entries.                       |
| input `package-boundary.json`                 | `25fd7d8619a98375…` | `bb931d68e0d2da5a…` | Classifies the receipt (RUNTIME SOURCE, release: true). |
| input `package.py`                            | `4c1b0c85b1045857…` | `d9d31432547dba0c…` | Canonical pin + `house_art` mirror.                     |
| input `wordpress-theme/…/package.json`        | `38c8848ef30f63af…` | `5a6084e9ef8de3b8…` | Version 2.5.2 + hero test in `verify`.                  |
| input `wordpress-theme/…/npm-shrinkwrap.json` | `c4b15fa2a205215f…` | `12b1af5a8551af24…` | Version 2.5.2 (root and package entry).                 |

`package-boundary.json` gained one entry; no other classification changed. The
hero webp was already `release: true`.

## Evidence (this session)

- Node 22.23.2, npm 10.9.8, Python 3.12.12; fresh `prepare-native-fixture.py`
  fixture; hash-checked native JS fixture.
- `npm run package:theme` (build + verify + package): exit 0, 773 runtime
  package entries; tree unchanged afterwards apart from this change.
- `test-homepage-hero-gate.php`: RED on main (2 of 12 modes fail: the hero is
  not admitted and the receipt is missing), GREEN after (12 of 12).
- `python -m unittest discover -s tools/v2-source-certification`: 23 OK.
  `pytest tests/test_v2_*.py tools/v2-source-certification`: 73 passed.
  `scripts/sync_product_registry.py --check`: PASS.
- `test-v2-media-eligibility.php` and `test-media-usage.php` came in with #1051
  but are not in `verify`. They fail identically before and after this change
  (line 35 `?v=` cache key; line 10 undefined `skyyrose2_media_usage_roles`),
  because they target the unported Codex helpers.

## Not verified

- Nothing deployed. Production and staging behavior after deploy is unverified.

## Follow-up: robots.txt news sitemap (2026-10-11, same 2.5.2)

**Authority:** founder asked to stop advertising Jetpack's news sitemap.
`[live 2026-10-11]` robots.txt listed both `sitemap.xml` and `news-sitemap.xml`
(Jetpack 16.3 `callback_action_do_robotstxt`); the news sitemap held only the
homepage with no `<news:news>` tags.

- `inc/seo-indexing.php`: `skyyrose2_seo_jetpack_news_sitemap_in_robots()`
  returns false unless a supported SEO plugin is active (then passes through);
  registered on `jetpack_news_sitemap_include_in_robotstxt` at priority 20 in
  `skyyrose2_seo_indexing_bootstrap()`. The main sitemap line is unchanged.
- `scripts/test-seo-indexing.php`: asserts registration, `false` without an
  authority plugin and pass-through with one. RED before the runtime change (3
  failures), GREEN after.

| Entry                                    | Old sha256          | New sha256          | Why                                  |
| ---------------------------------------- | ------------------- | ------------------- | ------------------------------------ |
| baseline `inc/seo-indexing.php`          | `b9c022ed913ba104…` | `13cd1cf4609e29b1…` | News-sitemap robots.txt filter.      |
| baseline `scripts/test-seo-indexing.php` | `01d262fdafa1c592…` | `ccdb9453f2181a12…` | Registration and pass-through cases. |
| input `runtime-php-baseline.json`        | `0c4b3b9d1e047068…` | `5411b4a6d8723dd2…` | Follows the two entries above.       |

Version stays 2.5.2; CHANGELOG and readme 2.5.2 entries gained one line each.
