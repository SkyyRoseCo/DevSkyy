# V2 release 2.5.1 certification lineage (2026-10-10)

**Authority:** founder asked for "the most updated theme with everything fixed"
and approved the certification hash updates this release requires, scoped to the
entries below. No product fact, `logo-registry.json`, or unrelated pin changed.

## What changed

- Cherry-picked `f7454c86d` (SEO/sitemap/metadata ownership, no conflicts) onto
  main `6e1ec9b9b`; one whitespace alignment fix at `inc/seo-indexing.php:227`
  (PHPCS `Generic.Formatting.MultipleStatementAlignment`).
- Version 2.5.0 -> 2.5.1 in `functions.php` (`SKYYROSE2_VERSION`), `style.css`,
  `readme.txt` (Stable tag + changelog), `package.json`, `npm-shrinkwrap.json`
  (root + package entry), `tests/analytics/README.md`; `CHANGELOG.md` 2.5.1
  entry; POT `Project-Id-Version` regenerated.

## Lineage

| Entry (file)                                                                     | Old sha256          | New sha256          | Why                                                                                            |
| -------------------------------------------------------------------------------- | ------------------- | ------------------- | ---------------------------------------------------------------------------------------------- |
| `runtime-php-baseline.json` -> `functions.php`                                   | `45021080bb21fc43…` | `1a30b4380f3730af…` | `SKYYROSE2_VERSION` 2.5.0 -> 2.5.1; no other change.                                           |
| `runtime-php-baseline.json` -> `inc/seo-indexing.php`                            | `fe0fc6eeb1e38e2f…` | `8de740e0ccfce661…` | SEO/sitemap commit `f7454c86d` plus one alignment space (line 227).                            |
| `runtime-php-baseline.json` -> `scripts/test-seo-indexing.php`                   | `bcf214f2e8d061f3…` | `fe6829c6451c0d1c…` | Test extended by `f7454c86d`.                                                                  |
| `build-inputs.json` -> `…/package.json`                                          | `5905886312ef915b…` | `e6c05de19fd61337…` | Version 2.5.1.                                                                                 |
| `build-inputs.json` -> `…/npm-shrinkwrap.json`                                   | `d100a336592834b9…` | `10677478c055e1c2…` | Version 2.5.1 (root and package entry).                                                        |
| `build-inputs.json` -> `tools/v2-source-certification/package-boundary.json`     | `54cb88a38aaf0431…` | `d7896a6ed05c567b…` | Classifies `scripts/validate-sitemap.py` (BUILD TOOLING, release:false, like sibling scripts). |
| `build-inputs.json` -> `tools/v2-source-certification/runtime-php-baseline.json` | `1a8c89ac72ed6ec7…` | `c93844900e15e2d0…` | Follows the three baseline entries above (final value after the line-227 fix).                 |

`package-boundary.json` gained one entry; no other classification changed.
`generated-outputs.json` carries no hashes and no `.min` source changed.

## Evidence

- `check-current-scenes.py`: PASS; `package.py`: 581 runtime package entries
  (same count as 2.5.0; the new script is not released); every
  `build-inputs.json` input hash and `runtime-php-baseline.json` entry matches
  the tree.
- `npm run check:assets`, `build-pot.py --check`, `test-seo-indexing.php`,
  `test-express-checkout.php`: pass. PHPCS on `functions.php` and
  `inc/seo-indexing.php`: 0 errors, 0 warnings.

## Not verified

- `check-integrity.py` requires node exactly 22.23.2; the author machine has
  22.23.3, so it was not run. CI's `verify` job is authoritative.
- Nothing deployed; behavior on staging/production unverified.
