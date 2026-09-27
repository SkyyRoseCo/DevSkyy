# Marketplace Template and Section Map

Scope: a source inventory for the SkyyRose V2 marketplace-ready theme path.
This is an architecture map, not a marketplace-certification claim and not a
release-time scaffold. It preserves the current theme’s native WooCommerce,
Scroll World, immersive, motion, and verified-media behavior.

## Current Template Hierarchy

| Route or surface | Current owner | Existing reusable sections | Source/commerce authority | Marketplace preparation state |
|---|---|---|---|---|
| Home / Living Archive | `front-page.php` | `home/living-archive-worlds`, `collections/product-edit`, `commerce/town-line`, shared mascot and dialogs | Collection contract and native product-card renderer | Strong section composition; the arrival shell remains intentionally route-owned. |
| Collections index | `page.php` `collections` branch | Collection rail plus native product cards | `skyyrose2_render_collection_rail()`, product-card renderer | Needs an extracted `pages/collections-index.php` to remove inline route markup. |
| Collection world | `template-collection.php` | `collections/world`, `arrival`, `scroll-world`, `story`, `next-world`, `product-edit`, composed scenes | Collection/presentation registry and product resolver | Strong reusable hierarchy. Preserve all Scroll World and scene hooks. |
| Immersive worlds | `template-immersive-*.php` | `immersive/world`, composed scenes | Collection and scene contracts | Strong shared entry point; world-specific templates are small adapters. |
| Shop archive | `woocommerce/archive-product.php` | Woo `content-product` → `commerce/product-card` | Native Woo query and product-card renderer | Strong native entry point; preserve filters/order/result count as Woo-owned. |
| Product detail | `woocommerce/single-product.php` | `commerce/product-hero`, native gallery override | Native Woo hooks, approved-card fronts, PDP media delivery | Strong reusable product shell. Keep variations, purchase controls, and gallery native. |
| Cart / checkout / thank-you | Woo templates | `woocommerce/cart/cart.php`, `checkout/form-checkout.php`, `checkout/thankyou.php` | WooCommerce templates and checkout truth contract | Native commerce ownership is appropriate; do not replace with decorative sections. |
| About | `page.php` adapter → `v2-about.php` | `v2-about`, commerce preview | Presentation registry and SOT asset resolver | Already sectionized; next work is naming internal sections only if a real reuse case appears. |
| Pre-order | `page.php` adapter → `v2-preorder.php` | `v2-preorder`, product-card renderer | Presentation registry and Woo product cards | Already sectionized. |
| Contact | inline `page.php` branch | None; hero, direct channel, form, service links are inline | Contact handler, nonce, WordPress options | Candidate for a single `pages/contact.php` extraction after launch. |
| FAQ / service pages | `page.php` adapter → `pages/service.php` | Generic head, managed FAQ content, service links | `skyyrose2_marketplace_pages()`, `the_content`, SEO FAQ adapter | First extraction implemented with a rendering contract test. |
| Account | generic `page.php` branch | None | Native Woo/My Account | Keep native content; generic page wrapper can be shared. |
| Journal | `home.php`, `index.php`, `single.php`, `journal-press-fallback.php` | Journal fallback section | Native posts/query | Good fallback reuse; journal list/card template extraction can follow a real editorial variant. |
| Lookbook | `page-lookbook.php` | `commerce/hero-composed-scene`, `collections/product-edit` | Scene and product resolvers | Good composed-page pattern; retain route orchestration. |
| Wishlist / search / 404 | dedicated root templates | Shared cards/dialogs/shell | Native query and Woo state | Dedicated behavior should remain thin route owners. |
| Global shell | `header.php`, `footer.php`, `inc/global-shell.php` | Nav, footer, mascot, quick view, size guide, search dialog | Shared route registry and SOT assets | Reusable and appropriately centralized. |

## Section Ownership Contract

| Section family | Owns | Must not absorb |
|---|---|---|
| `template-parts/pages/` proposed | Page shell, hero/head, composed static sections, ARIA landmarks | Product facts, Woo queries, checkout/purchase controls, provider/media selection. |
| `template-parts/collections/` | Collection narrative, scene sequencing, next-world links, product-edit placement | Product records and scene asset assertions. |
| `template-parts/commerce/` | Native card/PDP/search/quick-view/size-guide rendering | Collection-specific copy or page layout decisions. |
| `woocommerce/` | Woo templates, form controls, notices, variation and checkout behavior | Presentation registry writes or non-native replacement flows. |
| `inc/presentation-registry.php` | Canonical page composition inputs and maintained FAQ content | HTML output and product-data duplication. |
| `inc/seo-indexing.php` | Page metadata and FAQPage schema from the same maintained FAQ content | Visible page markup ownership. |

## Bounded Extraction Plan

1. **Implemented:** `page.php` now passes only `slug`, `is_account`,
   `is_service`, and `managed_content` to `template-parts/pages/service.php`.
   The page part retains the generic header, `the_content()` fallback,
   `apply_filters( 'the_content', $managed_content )`, `wp_kses_post()`, and
   escaped `home_url()`/`esc_url()` service links. The router keeps the `<main>`
   landmark and all route dispatch. `scripts/test-page-service-template.php`
   renders managed FAQ, generic fallback, and account cases to protect that
   boundary.

2. Extract `template-parts/pages/contact.php` from the contact branch only
   after service extraction is contract-tested. Pass a prepared, sanitized
   email/link/result object from `page.php`; the part should render it without
   reading request state or changing nonce/contact-handler behavior.

3. Extract `template-parts/pages/collections-index.php` from the collections
   branch. Keep the collection rail and product-card calls in the page part,
   with presentation inputs passed in from the router. Do not duplicate
   collection imagery or text outside existing registry/SOT readers.

4. Add focused template contract tests before every extraction: rendered
   landmarks, heading ID/`aria-labelledby` pairing, managed FAQ visible/schema
   parity, service-link destinations, and absence of Woo checkout/account
   behavior changes. Re-run existing SEO, marketplace-registry, performance,
   critical-rendering, archive-bundle, cart, checkout-truth, and product-media
   checks.

## Current Gaps and Guardrails

- `page.php` currently combines collections, contact, cart/checkout dispatch,
  FAQ/service/account wrapper logic, and generic fallback in one route file.
  This is the principal maintainability gap.
- The FAQ branch is coupled to the SEO adapter through the maintained content
  from `skyyrose2_marketplace_pages()`. A template extraction must preserve the
  exact source and sanitization sequence; it cannot use stale post content or
  a copied FAQ array.
- Contact is a valid sectionization target only when its nonce, honeypot,
  contact result states, and escaped admin-email link remain behaviorally
  identical.
- No empty section files are created by this map. A section exists only after
  it has a concrete caller, input contract, semantic markup, responsive CSS,
  and route-level verification.
- The current implementation provides a strong foundation for marketplace
  packaging but has not been certified against any external marketplace’s
  review process. Certification requires a separate packaging, licensing,
  accessibility, demo-import, and reviewer-environment validation pass.

## Recommended File Ownership for the First Extraction

| File | Owner / review responsibility | Reason |
|---|---|---|
| `page.php` | Router maintainer plus SEO reviewer | Reduce only route dispatch after the extracted part proves parity. |
| `template-parts/pages/service.php` | Theme template owner | Owns semantic generic/service shell and service-links rendering. |
| `inc/seo-indexing.php` | SEO owner | Verify FAQPage schema continues to read the exact visible managed FAQ source. |
| `scripts/test-page-service-template.php` | Contract-test owner | Renders FAQ, generic, and account variants to preserve managed-content, fallback, route, and service-link contracts. |
| `assets/css/theme.css` | CSS owner | Retain shared generic/service alignment and touch-target rules; no route-specific cascade forks. |
