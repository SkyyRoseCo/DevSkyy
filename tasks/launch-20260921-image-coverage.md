# Staging product image red-team audit

Date: 2026-09-21

## Scope and evidence

Audited the active staging URL `https://staging-7e48-skyyrose.wpcomstaging.com` and its matching V2 source checkout at `/Users/theceo/.codex/worktrees/abe0/DevSkyy` (HEAD `2c7644772`). The live WooCommerce Store API and published product pages return 33 products. Product identity in the current repository was read through `from skyyrose.core.product import get_product`; no registry changes were made.

The V2 approved card-front manifest contains 33 product/SKU bindings. For every entry, its local source exists and its SHA-256 matches the manifest. All 33 entries are marked `FOUNDER_APPROVED_V2_CARD`, and their alt text identifies a front-on-model view. A contact sheet was visually inspected: every image shows a person wearing the garment/set, rather than a flatlay or isolated ghost/mannequin product. Staging shop cards display the SKU-matched alt text and responsive `srcset` variants (320w, 480w, 768w, 1024w). The 33 public product permalinks were fetched successfully.

The mobile viewport was not changed during this audit. The root agent separately observed the 390px shop cards with BR-003 and BR-014 model images loaded; this audit's full pixel review used the source contact sheet and desktop browser rendering. It does not claim a completed visual crop check for every SKU at every mobile breakpoint.

## Findings

- **Shop cards: 33/33 have a source-verified, pixel-confirmed on-model front.** No product is represented by a back-only or flatlay in the active card-front manifest.
- **PDP primary gallery before the source patch: 28/33 displayed an on-model front as their first view. Five open on a ghost primary image:** BR-002, BR-005, KIDS-002, LH-003 and SG-014. The Store API/PDP source filenames for those first views are `br-002-ghost-front.webp`, `br-005-ghost-front.webp`, `kids-002-ghost-front.webp`, `lh-003-ghost-front.webp` and `sg-014-ghost-front.webp`. Each corresponding SKU already has a matching approved V2 model-front source.
- The working root product SOT also binds three `front_model_image` roles to ghost sources, even though `role_asset` evaluates true. Exact JSON pointers are `products.br-002.images.front_model_image`, `products.br-005.images.front_model_image`, and `products.kids-002.images.front_model_image` in `wordpress-theme/skyyrose-flagship/data/logo-registry.json`. Similarly named root theme images were inspected and are ghost/mannequin shots, so they are not safe replacements. The verified human-model candidates currently live in the V2 theme's approved-front manifest and assets.
- The native PDP gallery should retain all remaining Woo views, lightbox/zoom and thumbnail behavior when replacing the ghost primary. No change to the Woo product record or gallery attachment order is needed to accomplish that display repair.

## Source repair prepared

The active V2 source now detects a ghost primary only when the attachment's exact basename is `<current SKU>-ghost-front.webp`, then resolves that SKU through the existing `skyyrose2_approved_card_front()` manifest resolver. Replacement is refused unless the entry is founder-approved, its file stays inside the theme assets directory, and the source bytes match the manifest SHA-256. The gallery's first frame uses the approved responsive image (`srcset` plus `sizes`) and matching full-size lightbox/zoom URL; all remaining native gallery items pass through unchanged.

Changed source paths in the abe0 worktree:

- `wordpress-theme/skyyrose-flagship-2/inc/approved-card-fronts.php`
- `wordpress-theme/skyyrose-flagship-2/inc/pdp-media-delivery.php`
- `wordpress-theme/skyyrose-flagship-2/woocommerce/single-product/product-image.php`
- `tools/v2-runtime/test-pdp-gallery.php`
- `tools/v2-runtime/test-pdp-approved-fronts.php`

The source repair is prepared in the worktree and has not been deployed to staging. Root remains the integration owner; after the source is integrated, retest the five PDP galleries on desktop and mobile and confirm each retains its other views.

## Validation

- **PASS:** `php tools/v2-runtime/test-pdp-approved-fronts.php` — 33 source hashes/statuses/alt roles, the exact five ghost replacements, and wrong-SKU/non-ghost preservation.
- **PASS:** PHP syntax lint for all five changed PHP files.
- **Not run to completion:** `php tools/v2-runtime/test-pdp-gallery.php` requires a pinned WordPress 7.1 / WooCommerce 11.1.0 fixture via `V2_WP_FIXTURE`; that fixture is unavailable in this environment. The existing suite was extended with native-gallery assertions for all five cases, including retention of other views.
- **Still required after integration:** browser proof against the updated staging build, checking all five PDP first frames, remaining gallery thumbnails/lightbox, and mobile crops. No deploy, upload, or media generation was performed.
