# V2 runtime-PHP baseline update: express checkout (2026-10-09)

**Authority:** founder-approved in session (PR #1017), scoped to the entries
below.

## Lineage

| File                                                                                   | Old sha256          | New sha256          | Why                                                                                                                                    |
| -------------------------------------------------------------------------------------- | ------------------- | ------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `wordpress-theme/skyyrose-flagship-2/functions.php` (in `runtime-php-baseline.json`)   | `40b14fd7cbeca559…` | `45021080bb21fc43…` | One added line: `require_once SKYYROSE2_DIR . '/inc/express-checkout.php';` after the `security.php` require. No other change.         |
| `tools/v2-source-certification/runtime-php-baseline.json` (pin in `build-inputs.json`) | `08df4e075b5e86aa…` | `1a8c89ac72ed6ec7…` | Follows the entry above.                                                                                                               |
| `tools/v2-source-certification/package-boundary.json` (pin in `build-inputs.json`)     | `c1e5eb65ffb4a574…` | `54cb88a38aaf0431…` | Classifies `inc/express-checkout.php` (RUNTIME SOURCE, release) and `scripts/test-express-checkout.php` (BUILD TOOLING, not released). |

## Regression evidence

- `php wordpress-theme/skyyrose-flagship-2/scripts/test-express-checkout.php` →
  `PASS: 37 renderer and fallback checks; no payment settings or gateway filters changed.`
  (Also runs in CI's WordPress Theme job.)
- `inc/express-checkout.php` only calls `remove_action()` for callbacks bound to
  the Stripe express-checkout instance when WooPayments/WooPay renders its own
  row; it reads no input, outputs nothing, and changes no settings. Inert
  without WooCommerce, Stripe, or WooPayments.
- `tools/v2-source-certification/package.py` validates 581 runtime package
  entries; every `runtime-php-baseline.json` entry and all 59
  `build-inputs.json` input hashes match the tree.

## Not verified

- Behaviour against the real Stripe/WooPayments plugins on staging/production.
  Merging deploys nothing; a theme deploy is a separate founder-approved step.
