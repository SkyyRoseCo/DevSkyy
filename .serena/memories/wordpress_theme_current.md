# WordPress Theme — Current State

**Theme**: `skyyrose-flagship` (v3.2.0)
**Location**: `wordpress-theme/skyyrose-flagship/`
**Brand Tagline**: "" (ONLY tagline — "Where Love Meets Luxury" is RETIRED)

## Theme Structure

### Templates (12)
- `template-collection-black-rose.php`, `template-collection-love-hurts.php`, `template-collection-signature.php`, `template-collection-kids-capsule.php`
- `template-immersive-black-rose.php`, `template-immersive-love-hurts.php`, `template-immersive-signature.php`
- `template-homepage-luxury.php`, `template-preorder-gateway.php`
- `template-about.php`, `template-contact.php`, `template-love-hurts.php`

### Page Templates
- `front-page.php`, `header.php`, `footer.php`, `index.php`, `page-wishlist.php`

### inc/ Modules (25)
Key: `enqueue.php`, `enqueue-brand-styles.php`, `enqueue-engines.php`, `elementor.php`, `woocommerce.php`, `product-catalog.php`, `product-import.php`, `product-taxonomy.php`, `security.php`, `seo.php`, `accessibility-seo.php`, `theme-setup.php`, `menu-setup.php`, `customizer.php`, `template-functions.php`, `ajax-handlers.php`, `immersive-ajax.php`, `branded-content.php`, `wishlist-functions.php`, `deployment-checklist.php`, `facebook-sdk.php`, `class-wishlist-widget.php`

### Assets
- `assets/css/` — 31 CSS files
- `assets/js/` — 24 JS files
- `assets/images/products/` — 26 product photos
- `assets/images/scenes/` — 13 collection scene images

## Three.js Collection Experiences
Located at `src/collections/`:
- `BlackRoseExperience.ts`, `LoveHurtsExperience.ts`, `SignatureExperience.ts`
- `BaseCollectionExperience.ts`, `ShowroomExperience.ts`, `RunwayExperience.ts`
- `HotspotManager.ts`, `ARTryOnViewer.ts`, `WebXRARViewer.ts`
- `WooCommerceProductLoader.ts`, `EnvironmentTransition.ts`

## Brand Colors
- Primary: #B76E79 (Rose Gold)
- Black Rose: #1a1a1a, #8b0000
- Love Hurts: #dc143c, #722F37
- Signature: #d4af37 (Gold), #8b7355 (Bronze)

## Collections
- **Black Rose**: Gothic elegance, dark luxury
- **Love Hurts**: Beauty & the Beast (Beast's perspective), passionate
- **Signature**: Oakland/SF tribute, urban sophistication
- **Kids Capsule**: Children's collection

## CRITICAL RULES
- ONLY `skyyrose-flagship` exists — no other themes
- Use Serena MCP for all WordPress file operations
- Context7 BEFORE any WordPress/Elementor/WooCommerce code
