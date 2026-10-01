# WordPress storefront codemap

**Last updated:** 2026-10-01. **Source inspected:**
`a662e707d698a687d7d1d2efed3975b9aa7325b9`. **Entry points:** V1/V2
`functions.php`, V2 `inc/marketplace.php`, `inc/woocommerce-compat.php`.

This focused map is derived from the current theme bootstrap, source tree,
package manifests, and production cutover sources. Production currently runs V1;
existing staging runs the reviewed V2 candidate. Use
[production status](../PRODUCTION_STATUS.md) for dated actual target evidence.
This update does not revalidate the entire codemap library.

## Architecture and authority

```text
logo-registry.json (one editable unified products registry)
  -> skyyrose.core.product.get_product / compatibility projections
  -> V1 catalog reader / V2 presentation registry
  -> collection/card/PDP presentation and approved media bindings

Native WordPress + WooCommerce
  -> actual pages/options and product IDs/types/prices
  -> V2 native commerce adapter + preorder promise hooks
  -> native cart/checkout/orders/payment behavior

Reviewed V2 ZIP + separate Search MU + ten-page plan
  -> guarded installation and owned drafts
  -> actual V1 Search checkpoint
  -> guarded core activation, publication, readback
  -> actual V2 browser acceptance + independent review
```

Root [logo-registry.json](../../logo-registry.json) resolves to the original
theme's
[registry](../../wordpress-theme/skyyrose-flagship/data/logo-registry.json).
CSV/dossier/SOT manifests and the V2 presentation registry are consumers or
projections. Complete readers use [get_product](../../skyyrose/core/product.py);
unknown SKUs raise and missing facts appear in `gaps`. Corey's latest maker
specifications remain `FOUNDER_CONFIRMED`. Native WooCommerce runtime remains
the owner of actual store configuration and transactional behavior.

## Themes and key modules

| Source                                                                                                                                                                                                                                                                  | Purpose and relationships                                                                                                       |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| [V1 functions.php](../../wordpress-theme/skyyrose-flagship/functions.php)                                                                                                                                                                                               | Original currently active theme; loads its `inc/` modules and native hooks                                                      |
| [V1 product-catalog.php](../../wordpress-theme/skyyrose-flagship/inc/product-catalog.php)                                                                                                                                                                               | Compatibility catalog consumer; authored corrections originate in the unified registry                                          |
| [V2 functions.php](../../wordpress-theme/skyyrose-flagship-2/functions.php)                                                                                                                                                                                             | Theme 2.5.0 bootstrap; loads marketplace, delivery, commerce, analytics, GLB modules; mascot enablement currently returns false |
| [V2 marketplace.php](../../wordpress-theme/skyyrose-flagship-2/inc/marketplace.php)                                                                                                                                                                                     | Theme setup, page resolution, editor/fresh-install integration; shared production cutover uses guarded owned-page operations    |
| [V2 presentation-registry.php](../../wordpress-theme/skyyrose-flagship-2/inc/presentation-registry.php)                                                                                                                                                                 | Read-only consumer of the generated presentation data                                                                           |
| [V2 woocommerce-compat.php](../../wordpress-theme/skyyrose-flagship-2/inc/woocommerce-compat.php)                                                                                                                                                                       | Versioned preorder promises at native cart/checkout/order transaction boundaries; no price override or reservation              |
| [V2 approved-card-fronts.php](../../wordpress-theme/skyyrose-flagship-2/inc/approved-card-fronts.php) and [pdp-media-delivery.php](../../wordpress-theme/skyyrose-flagship-2/inc/pdp-media-delivery.php)                                                                | Registry-bound approved card/PDP delivery                                                                                       |
| [V2 collection-presentation.php](../../wordpress-theme/skyyrose-flagship-2/inc/collection-presentation.php) and [hero-commerce-scenes.php](../../wordpress-theme/skyyrose-flagship-2/inc/hero-commerce-scenes.php)                                                      | Collection-native presentation and current approved scene consumers                                                             |
| [V2 analytics.php](../../wordpress-theme/skyyrose-flagship-2/inc/analytics.php) and [analytics-protocol.php](../../wordpress-theme/skyyrose-flagship-2/inc/analytics-protocol.php)                                                                                      | Owned consent/analytics integration and protocol; live delivery qualification is separate                                       |
| [V2 product-glb.php](../../wordpress-theme/skyyrose-flagship-2/inc/product-glb.php) and [product-glb-links.php](../../wordpress-theme/skyyrose-flagship-2/inc/product-glb-links.php)                                                                                    | Guarded product-viewer bindings; accepted GLB/license/room/device gates remain separate                                         |
| [V2 global-shell.php](../../wordpress-theme/skyyrose-flagship-2/inc/global-shell.php), [critical-rendering.php](../../wordpress-theme/skyyrose-flagship-2/inc/critical-rendering.php), [performance.php](../../wordpress-theme/skyyrose-flagship-2/inc/performance.php) | Shell, enqueue/preload, critical CSS, and performance delivery                                                                  |

## V2 template map

Paths below are relative to `wordpress-theme/skyyrose-flagship-2/`.

| Entry or family                                                                                                              | Role                                                                                                 |
| ---------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `front-page.php`, `template-parts/home/`                                                                                     | Homepage and collection/editorial navigation                                                         |
| `template-collection.php`, `template-parts/collections/`                                                                     | Collections root, collection pages, native product links and presentation, and next-world navigation |
| `template-immersive-{signature,black-rose,love-hurts,kids-capsule}.php`, `template-parts/immersive/world.php`                | Four immersive storytelling routes                                                                   |
| `woocommerce/archive-product.php`, `woocommerce/content-product.php`, `template-parts/commerce/product-card.php`             | Shop archive and native product cards                                                                |
| `woocommerce/single-product.php`, `woocommerce/single-product/product-image.php`, `template-parts/commerce/product-hero.php` | Native PDP and approved media presentation                                                           |
| `woocommerce/cart/cart.php`, `woocommerce/checkout/form-checkout.php`                                                        | Native cart and checkout overrides                                                                   |
| `search.php`, `template-parts/commerce/search-dialog.php`                                                                    | Search results and header dialog                                                                     |
| `template-parts/commerce/size-guide-dialog.php`, `template-parts/pages/service.php`                                          | Size guide and service page presentation                                                             |
| `template-parts/cookie-consent.php`, `template-parts/v2-preorder.php`                                                        | Consent controls and preorder presentation                                                           |
| `page.php`, `home.php`, `single.php`, `archive.php`                                                                          | WordPress page/journal/archive hierarchy                                                             |

## Build and verification

V2 owns its
[package.json](../../wordpress-theme/skyyrose-flagship-2/package.json) and
tracked `npm-shrinkwrap.json`. It requires Node.js 22+, npm 9+; theme headers
require WordPress 6.8+ and PHP 8.2+. Run from the V2 directory:

```bash
npm ci
npm run build
npm run check:assets
npm run lint:php
npm run verify
npm run package:theme
```

The build checks pinned source integrity before rebuilding scene posters,
tokens, presentation registry, card/font/frame delivery, JS/CSS assets, archive
bundles, and translation output. Verification combines integrity/asset/scene
checks with PHP/Node/Python runtime contract tests. Edit source first, rebuild
affected tracked `.min` outputs, and inspect generated diffs. The current
cutover consumes the already reviewed exact ZIP; a fresh build does not replace
that binding.

V1 validation is owned by
[wordpress-theme/package.json](../../wordpress-theme/package.json)
(`npm run verify:full` from `wordpress-theme/`). Root/dashboard test scripts are
independent and do not validate either theme's deployment.

## Release operations and data flow

The
[frozen cutover manifest](../../tasks/production-final-pass-20261001/cutover-candidate-manifest.json)
binds the 599-member V2 ZIP, separate
[Search privacy extension](../../tools/production-runtime/search-tracking-privacy.php),
[publisher](../../tools/production-runtime/publish-search-privacy.php), and
[ten-page operator](../../tasks/production-final-pass-20261001/apply_v2_pages.php).
The final reviewed procedure supplements the manifest's historical sequence:
Search/privacy/cache qualification on active V1 precedes V2 activation.

Readback preserves the 33 published simple products/current IDs/native prices,
full-payment checkout, unmanaged quantities, null shipping-date promises, and
existing merchant/WooCommerce pages/options. No staging DB synchronization,
product import, variation/inventory change, paid generation, unaccepted GLBs,
mascot activation, or other-service deployment is part of the cutover.

Unknown outcomes stop mutation for read-only reconciliation and guarded owned
recovery. Production acceptance requires actual deployed bytes/configuration,
Search/PDP/native cart/remove/Undo/checkout rendering, six consent profiles, and
independent evidence review. See [RUNBOOK.md](../RUNBOOK.md) and
[WORDPRESS_CONFIGURATION_STATUS.md](../WORDPRESS_CONFIGURATION_STATUS.md).

## Related areas

[Product authority](../../SOT.md) ·
[Integration adoption](../../tasks/integration-release-20261001/adoption-manifest.json)
· [Architecture codemap](architecture.md) · [Data codemap](data.md) ·
[External dependencies](dependencies.md)

Older related codemaps retain their own timestamps and may describe superseded
product or deployment assumptions; this focused map does not promote them to a
current release receipt.
