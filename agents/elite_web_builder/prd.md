Build the SkyyRose Flagship WordPress theme — a marketplace-ready luxury streetwear e-commerce theme for WordPress.com Atomic with WooCommerce.

## Design Philosophy (MANDATORY — applies to ALL visual output)
Every page, component, and interaction must follow these principles:
- Landing pages and marketing content: MAXIMIZE emotional impact and "wow factor". Design should make someone stop scrolling and say "whoa". Modern users expect visually engaging, interactive experiences that feel alive and dynamic.
- Default to contemporary cutting-edge design: dark modes, glassmorphism, micro-animations, 3D elements, bold typography, vibrant gradients. Static designs are the EXCEPTION, not the rule.
- Include thoughtful animations on EVERYTHING: hover effects, scroll reveals, entrance transitions, pulsing accents, parallax, spring physics. Even subtle movements dramatically improve engagement.
- When faced with design decisions, lean BOLD and UNEXPECTED over safe and conventional: vibrant colors over muted, dynamic layouts over traditional grids, expressive typography over conservative, immersive effects over minimal.
- Push boundaries with advanced CSS (custom properties, clamp(), container queries, :has(), scroll-driven animations), complex keyframe animations, and creative JavaScript interactions. The goal is PREMIUM and CUTTING-EDGE.
- Complex interactive features (immersive scenes, Three.js if ever used): prioritize smooth frame rates, responsive controls, efficient rendering, stable interactions.
- Accessibility is NON-NEGOTIABLE: proper contrast, semantic markup, keyboard nav, ARIA labels, focus indicators — but make accessibility beautiful, not an afterthought.
- Create fully functional working implementations, not placeholders.

## Site Identity
- Brand: The Skyy Rose Collection
- URL: https://skyyrose.co
- Platform: WordPress.com Atomic (SSH/SFTP, custom PHP, full plugin access)
- Theme: skyyrose-flagship
- WooCommerce: Full integration (products, cart, checkout, payment)
- Tagline: "Oakland Luxury Streetwear"

## Marketplace-Ready Theme Requirements
This theme must be structured as a PROFESSIONAL commercial-grade WordPress theme:
- Complete theme.json for Full Site Editing (colors, fonts, spacing, layout presets)
- Proper functions.php with conditional asset loading per template
- Organized file structure: assets/css/, assets/js/, assets/images/, woocommerce/
- WordPress Customizer integration for brand colors and logo
- Child-theme compatible (no hardcoded paths)
- Translation-ready with __() and esc_html__() wrappers
- Screenshot.png (1200x900) showing the dark luxury design
- style.css header with theme metadata (name, version, author, description, tags)
- README.txt with setup instructions, requirements, changelog
- GPL-2.0+ license compatible

## Design System Requirements
- MANDATORY dark theme: #0A0A0A page background (NOT white), #111111 card backgrounds
- Glass morphism: rgba(17,17,17,0.95) with backdrop-filter: blur(20px) for panels
- Fonts: Hanken Grotesk (body/UI) + Archivo (display/headings) + Anton (UI caps) + Cinzel (engraved-caps accent); Inter = fallback only — self-hosted woff2 ONLY (assets/fonts/ + theme.json Font Library / assets/css/fonts.css; NO Google Fonts CDN, no @import, no preconnect)
  - Do NOT use Montserrat, Playfair Display, Cormorant Garamond, Bebas Neue, or system defaults
- Film grain SVG overlay at 3% opacity on ALL pages (luxury texture effect)
- Official collection colors (OWNER-CONFIRMED, do not change):
  - BLACK ROSE: Black #000000, White #FFFFFF, Metallic Silver #C0C0C0
  - LOVE HURTS: Red #FF0000, Crimson #DC143C, Black #000000, White #FFFFFF
  - SIGNATURE: Rose Gold #B76E79 (PRIMARY brand color), Gold #D4AF37
  - KIDS CAPSULE: Pink #FFB6C1, Lavender #E6E6FA
- CSS custom properties in :root for ALL design tokens (colors, fonts, spacing, transitions)
- Responsive breakpoints: 1200px (tablet landscape), 768px (tablet), 480px (mobile)
- Spacing scale: xs 0.5rem, sm 1rem, md 1.5rem, lg 2rem, xl 3rem, 2xl 4rem
- Transitions: smooth (0.3s ease), spring (0.6s cubic-bezier(0.16, 1, 0.3, 1))

## Pages to Build (9 from static HTML reference + 2 new)
Static HTML designs in wp-playground/SKyyRose Flagship/Flagship static/ are the CANONICAL design reference. Every PHP template must faithfully reproduce these designs.

1. front-page.php — Hero (100vh, floating orbs, gradient headline) + collections showcase (3 cards 600px tall) + featured products (4-card grid) + brand story (2-col) + newsletter
2. template-collection-black-rose.php — Floating roses animation, 12 products (br-001..012, full Jersey Series 0–5), gothic garden mood, metallic silver accent
3. template-collection-love-hurts.php — 15 floating hearts, 4 products (lh-002, lh-003, lh-004, lh-005), passionate drama mood, crimson accent, pulsing collection badge
4. template-collection-signature.php — Art deco overlay, 12 products (sg-001/002/003/005/006/007/009/011/012/013/014/015), elevated luxury mood, rose gold accent, pulsing gold ring (600px)
5. template-collection-kids-capsule.php — Pink/lavender theme, 2 products (kids-001, kids-002), playful rounded cards, joyful voice (NEW — no static reference, derive from other collections)
6. woocommerce/single-product.php — Sticky gallery (main + 4 thumbs) + product info panel + color/size selectors + quantity + accordions (Details, Sizing, Shipping) + related 4-grid
7. template-about.php — Hero + story sections (alternating grid) + timeline (2019-2024) + values (4 cards) + founder section
8. template-contact.php — Contact info + form (name, email, subject, message) + FAQ accordion (5)
9. woocommerce/cart/cart.php — Dark luxury cart with 150px item images + sticky order summary (400px)
10. woocommerce/checkout/form-checkout.php — 4-step progress (Cart > Info > Payment > Confirm) + multi-step form + sticky order summary (420px)
11. 404.php — Dark bg, "404" in Archivo with gold gradient, collection quick links, CTA (NEW)

## Shared Components
- Header: Fixed dark navbar rgba(10,10,10,0.95) + blur(20px), SR Monogram logo (48px), gradient text "SKYY ROSE", nav links + icon buttons (search, account, cart with count badge), mobile hamburger slide-in from right
- Footer: 5-column grid (2fr 1fr 1fr 1fr 1fr) — Brand/Shop/Help/Legal/Social, newsletter signup bar, copyright, stacks to single column on mobile
- Product Card: #111 bg, 3:4 aspect image, hover: translateY(-8px) + shadow, quick actions overlay (wishlist, quickview, add-to-cart), name (Hanken Grotesk 600), price in collection accent color
- Toast Notifications: fixed bottom-right, slide-in, dark glass, auto-dismiss 3s

## drakerelated.com-Style Product Display & Immersive Scenes
The ENTIRE product browsing experience follows the drakerelated.com interaction pattern — Drake's official lifestyle site that uses room-based exploration with hotspot beacons.

### Immersive Pages (3 scenes — image-based, NOT Three.js/WebGL)
- template-immersive-black-rose.php — "The Garden": Gothic garden, wrought-iron racks, roses, cathedral backdrop, 5 products visible IN the scene on racks/mannequins/benches
- template-immersive-love-hurts.php — "The Ballroom": Baroque ballroom + candlelit manor (2 scene views), chandeliers, rose petals, 5 products on chairs/mannequins/pedestals
- template-immersive-signature.php — "The Runway" (MULTI-ROOM, 3 scenes):
  Room 1 "The Runway" — Bay Bridge glass venue, garment racks, 5 products
  Room 2 "The Showroom" — Grand hall, display cases, 5 products
  Room 3 "The Fitting Room" — Intimate dressing area, mirrors, 4 beanies on stands/shelves
  Arrow/swipe navigation between rooms with 0.6s crossfade transitions

### drakerelated.com Interaction Pattern (CRITICAL)
- Full-screen scene IMAGE as viewport backdrop (object-fit: cover, responsive)
- Products physically VISIBLE in the scene image (on racks, mannequins, furniture, shelves) — NOT abstract dots on a generic background
- Hotspot beacons: 32px pulsing circles with collection accent border, positioned via percentage-based coordinates (e.g., left: 34.2%; top: 48.7%) — responsive across all screens
- Hotspot click = DUAL action: (1) glassmorphism slide-up panel with product thumbnail, name, price, sizes, add-to-cart, (2) "View Details" link to collection or product page
- Hotspots are <a> tags wrapping beacons for SEO crawlability + keyboard navigation
- Room-to-room navigation arrows at screen edges (Signature has 3 rooms)
- Smooth crossfade transitions between scenes (not hard cuts)
- Minimal UI overlay — scene image is the star, UI is glass/transparent
- Vignette overlay: radial-gradient(ellipse at center, transparent 35%, rgba(2,0,4,0.8))
- Film grain + collection tab bar (fixed bottom) on all immersive pages

## Pre-Order Gateway Page
- template-preorder-gateway.php — Glassmorphism design, ultra-dark (#020004) background
- Loading screen with SR Monogram (breathe animation) + progress bar
- Collection tabs: All | Black Rose | Love Hurts | Signature (fixed bottom, accent per tab)
- Product grid: auto-fill minmax(180px, 1fr)
- Product modal: 360° preview area, sizes, add-to-cart + wishlist
- Cart sidebar: slide-in from right (400px), items list, total, checkout button
- Sign-in panel: slide-in from right (420px), email/password, member perks list
- Exclusive member banner with early access CTA

## AI Fashion Model Photography Integration
ALL product images are AI-generated fashion model photos showing real models wearing the EXACT SkyyRose products with correct branding techniques (embroidered, silicone, printed, etc.)

### Image Pipeline
- Generated via: Gemini 2.5 Flash Image (primary), DALL-E 3 (fallback)
- Output structure: products/{sku}/{sku}-model-{view}.jpg (front + back per product)
- 204+ fashion model photos across 28 SKU folders (ALREADY GENERATED)
- Each image verified by dual AI vision (Claude Sonnet + Gemini Flash) for logo accuracy
- Branding techniques ML-verified per product (28 override files with logoFingerprint)

### WordPress Image Embedding (MANDATORY pattern)
```php
<picture>
  <source srcset="products/{sku}/{sku}-model-front.webp" type="image/webp">
  <img src="products/{sku}/{sku}-model-front.jpg"
       alt="{Product Name} — Model wearing {garment type}"
       width="1024" height="1536" loading="lazy" class="product-image">
</picture>
```
- All images: WebP primary + JPEG fallback via <picture> element
- Responsive srcset: 480px, 768px, 1024px, 2048px sizes
- Alt text format: "{Canonical Product Name} — Model wearing {garment type}"
- Lazy loading on all images below the fold

### Where AI Model Photos Appear
| Image Type | Template | Placement |
|-----------|----------|-----------|
| Fashion model (front) | Collection landing pages, product hero, lookbook grid | Primary product image |
| Fashion model (back) | Single product thumbnails, lookbook secondary | Hover/alternate view |
| Scene backgrounds | Immersive pages | Full-screen backdrop with hotspots |
| Collection logos | Hero sections, header, footer, watermarks | Brand identity |
| Ad creatives | Homepage hero, marketing banners | Promotional sections |

## Technical Requirements
- WordPress PHP templates with proper hooks (wp_enqueue_scripts, wp_head, wp_footer)
- WooCommerce template overrides in woocommerce/ subdirectory
- Functions.php with conditional asset loading per template (immersive CSS/JS only on immersive pages)
- theme.json for Full Site Editing support (colors, fonts, spacing, layout)
- WCAG 2.2 AA accessibility: 4.5:1 contrast ratios, keyboard navigation, ARIA landmarks, skip-to-content link, focus indicators, alt text on all images, form labels
- Lighthouse > 80 mobile: critical CSS inlined, images lazy-loaded, WebP with JPEG fallback, deferred non-critical JS, font-display: swap
- SEO: schema.org Product markup (name, price, image, availability), meta tags, Open Graph, Twitter Cards, canonical URLs, structured breadcrumbs
- Security: CSP headers, XML-RPC disabled, no inline scripts where possible, input sanitization, nonce verification on forms, esc_html/esc_attr on all output

## Logo Assets (already optimized in branding/optimized/)
- SR Monogram: header (48px), footer (64px), loading screen (120px breathe animation), favicon set (16-512px)
- Collection logos: collection hero sections, immersive page watermarks (bottom-right, 8% opacity)
- 5 sizes: favicon (64px), icon (200px), nav (400px), hero (1024px), og (1200px)
- Dual format: PNG (transparency) + WebP (performance)
- Logo placement map: header=SR Monogram, footer=SR Monogram + text, favicon=SR Monogram, collection hero=collection-specific logo centered above heading, product cards=NO logo

## Products (30 total, 4 collections)

**Authoritative source:** `wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv` — read through the PHP loader (`skyyrose_get_product_catalog()`) or the Python loader (`scripts.nano_banana.catalog.load_catalog()`). Full SKU table with branding specs, prices, pre-order flags, and image paths lives in `knowledge/canonical_catalog.md`.

### BLACK ROSE (12)
br-001 BLACK Rose Crewneck · br-002 BLACK Rose Joggers · br-003 BLACK is Beautiful Jersey Series: 0. Baseball Classic · br-004 BLACK Rose Hoodie · br-005 BLACK Rose Hoodie — Signature Edition · br-006 BLACK Rose Sherpa Jacket · br-007 BLACK Rose × Love Hurts Basketball Shorts · br-008 Jersey Series: 1. SF Inspired (Football) · br-009 Jersey Series: 2. Last Oakland (Football) · br-010 Jersey Series: 3. The Bay (Basketball) · br-011 Jersey Series: 4. The Rose (Hockey) · br-012 Jersey Series: 5. Last Oakland (Baseball)

### LOVE HURTS (4)
lh-002 Love Hurts Joggers · lh-003 Love Hurts Basketball Shorts · lh-004 Love Hurts Bomber Jacket · lh-005 The Fannie

### SIGNATURE (12)
sg-001 Bridge Series 'The Bay Bridge' Shorts · sg-002 Bridge Series 'Stay Golden' Shirt · sg-003 Bridge Series 'Stay Golden' Shorts · sg-005 Bridge Series 'The Bay Bridge' Shirt · sg-006 Mint & Lavender Hoodie · sg-007 The Signature Beanie · sg-009 The Sherpa Jacket · sg-011 Original Label Tee (White) · sg-012 Original Label Tee (Orchid) · sg-013 Mint & Lavender Crewneck · sg-014 Mint & Lavender Sweatpants · sg-015 The Windbreaker Set

### KIDS CAPSULE (2)
kids-001 Kids Colorblock Hoodie Set — Red/Black · kids-002 Kids Colorblock Hoodie Set — Purple/Black

### Retired SKU codes (DO NOT resurrect)
`lh-001` (renumbered to lh-005), legacy `lh-005 Love Hurts Windbreaker` (erased), `sg-004 Signature Hoodie`, `sg-008`, `sg-010`, `br-d01..d04`, `sg-d01..d04`.
