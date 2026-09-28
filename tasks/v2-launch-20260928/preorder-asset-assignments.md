# V2 pre-order asset assignments

Surface: `/pre-order/`, rendered by `wordpress-theme/skyyrose-flagship-2/page.php` and `template-parts/v2-preorder.php`.

| Role | Assigned source | Served by | Evidence |
| --- | --- | --- | --- |
| Arrival scene | `wordpress-theme/skyyrose-flagship-2/assets/images/house-monument-20260928.webp` | The same local WebP in the `/pre-order/` template and route-specific preload | Founder-directed, garment-free SkyyRose monument at the Bay Bridge. The file is present and was visually inspected at 1672 × 941. This editorial image is assigned only to the gateway arrival. |
| Product fronts | The single editable root `logo-registry.json` (`products[sku]` image/source bindings) | `skyyrose2_approved_card_front()` in the shared Woo product card, with its existing commerce media fallback | The gateway passes each live Woo product to `template-parts/commerce/product-card.php` with `frame => false`; that resolver decides at runtime whether a front is eligible and shows an unavailable state when none is. This log makes no product image approval claim. |
| Product identity and order controls | Root registry projected into V2 presentation records, joined to live Woo products | `skyyrose2_get_products( 100, 'pre-order' )`, product card, product detail page, Woo bag and checkout | Registry identifies the eligible preorder SKUs; Woo remains authoritative for published state, price, stock, variation selection, cart, and checkout. |

The previous Black Rose salon scene included composite jersey depictions without source-bound SKU and patch verification, so it is no longer assigned to the house-wide gateway. The product card source must remain SKU specific. All jerseys include the founder-confirmed patch; any media that obscures or contradicts that detail needs catalog/media reconciliation before use. The gateway adds no invented shipping dates, stock allocations, or payment terms.

Checks on 2026-09-28: `python3 scripts/sync_product_registry.py --check` passed; `php tools/v2-runtime/test-preorder-gateway.php` and `php tools/v2-runtime/test-product-card.php` passed; `php scripts/test-performance.php`, `npm run build:assets`, and `npm run check:assets` passed in the V2 theme. These are local checks, not staging purchase evidence.

Layout-only screenshots: `preorder-layout-preview-390x844.png` and `preorder-layout-preview-1440x900.png` were rendered at those viewports with local Chrome from the real template and CSS. The synthetic fixture supplied an empty Woo product list, so these screenshots verify hero, type, responsive crop, and no horizontal overflow; they do not verify live cards or checkout. The 390px render places a 367px artwork block above a 449px copy block, loads the 1672px monument, and measured `scrollWidth <= innerWidth`.
