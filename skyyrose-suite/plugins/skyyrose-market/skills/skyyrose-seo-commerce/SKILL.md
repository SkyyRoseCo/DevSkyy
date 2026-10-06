---
name: skyyrose-seo-commerce
description: "WooCommerce SEO system for SkyyRose. Keyword strategy, product page optimization, collection SEO, schema markup with PHP code, technical SEO checklist, and site architecture. Use when optimizing skyyrose.co for search engines or auditing SEO performance."
allowed-tools: Read Write Edit Glob Grep Bash
---

# SkyyRose E-Commerce SEO System

## Brand Canon (Enforce Always)

- Tagline: No tagline is authorised (founder decision 2026-10-06).
- Collections and their voices:
  - **Black Rose** — armor / concrete / "you already stood up" / silver `#C0C0C0`
  - **Love Hurts** — bloodline / "bloodline that raised me" / crimson `#DC143C`
  - **Signature** — stay golden / Bay Area everyday luxury / gold `#D4AF37`
  - **Kids Capsule** — little royalty / rose gold `#B76E79`
- Never cross-attribute collection voices (e.g., "bloodline" = Love Hurts ONLY)
- Products referenced by NAME, never by SKU; resolved from catalog CSV + per-SKU dossier
- Visual references: Kith, Oaklandish, Culture Kings, Fear of God, Palm Angels — NEVER European luxury houses
- Collection names in heroes = lockup PNG assets, never type-rendered
- **No cross-sell / no related products on PDP / no urgency timers** (see §Internal Linking)
- Oakland anchor; "Bay Area" mentions acceptable, Bay Bridge = Oakland context
- STOP-AND-SHOW on paid spend, Klaviyo sends, WooCommerce writes, media uploads

---

## When to Use This Skill

- Optimizing WooCommerce product pages for search
- Writing SEO meta titles and descriptions
- Adding schema markup (JSON-LD) to the WordPress theme
- Auditing site SEO health
- Planning keyword strategy for luxury streetwear
- Building internal linking architecture
- Optimizing collection/category pages
- Diagnosing and recovering from ranking drops

---

## Keyword Strategy

### Brand Keywords (Protect)
| Keyword | Search Intent | Priority |
|---------|--------------|----------|
| skyyrose | Brand search | Must own #1 |
| skyy rose collection | Brand search | Must own #1 |
| skyyrose clothing | Brand + category | Must own #1 |

### Category Keywords (Target)
| Keyword | Volume Est. | Difficulty | Target Page |
|---------|-----------|-----------|-------------|
| luxury streetwear | High | High | Homepage / About |
| Black-owned clothing brand | Medium | Medium | About page |
| Oakland streetwear | Low-Medium | Low | Homepage / Collections |
| Bay Area clothing brand | Medium | Medium | About page |
| limited edition streetwear | Medium | Medium | Shop / Collections |
| Black-owned streetwear | Medium | Low | About / Collections |
| luxury hoodies men | Medium | High | Black Rose Collection |
| streetwear jerseys | Medium | Medium | Black Rose Collection |
| designer joggers | Medium | High | Signature Collection |

### Long-Tail Keywords (Content + Product Pages)
- "Black-owned luxury hoodie brand"
- "limited edition streetwear Oakland"
- "Bay Area designer clothing"
- "premium streetwear pre-order"
- "luxury streetwear for kids"
- "Oakland fashion brand founded by single dad"
- "heavyweight french terry hoodie"
- "limited edition basketball jersey Black-owned"

### Local SEO Keywords
- "clothing brand Oakland CA"
- "streetwear brand San Francisco Bay Area"
- "Black-owned business Oakland"
- "fashion brand San Leandro CA"

---

## WooCommerce Product SEO

### Product Title Formula
```
[Primary Keyword] — [Brand] [Differentiator]
```
Examples:
- "Black Rose Heavyweight Hoodie — SkyyRose Limited Edition"
- "Bay Bridge Premium Shorts — SkyyRose Bridge Series"
- "Love Hurts Varsity Jacket — SkyyRose Full-Grain Leather"

### Short Description (WooCommerce excerpt)
- 150-200 characters
- Primary keyword in first sentence
- Benefit-first, then feature
- End with differentiator (limited, Oakland-made, etc.)

### Long Description Structure
```
[SEO-rich opening paragraph — primary keyword + brand story hook]

[Product story — cultural reference, design intent — use collection voice, never cross-attribute]

[Construction details with secondary keywords]
- Material and weight
- Stitching and hardware
- Design elements

[Fit guide with keywords]

[Pre-order / availability — no urgency timers; factual availability only]

[CTA]
```

### Image Alt Text Formula
```
[Product name] [view] — [one detail] | SkyyRose [Collection]
```
Examples:
- "Black Rose Hoodie front view — embroidered script heavyweight French terry | SkyyRose Black Rose Collection"
- "Bay Bridge Shorts lifestyle — gold hardware on Oakland waterfront | SkyyRose Signature"

### URL Slug Best Practices
- `/product/black-rose-hoodie/` NOT `/product/br-004/`
- Include primary keyword
- No filler words (a, the, and)
- Hyphens between words
- Lowercase only

### Yoast / RankMath Configuration
```
SEO Title: [Product Name] — [Key Feature] | SkyyRose
Meta Description: [Benefit] + [key feature] + [differentiator]. [CTA]. [155 chars max]
Focus Keyword: [primary keyword for this product]
```

### WooCommerce SEO Meta via REST API (`meta_data`)
WC REST API v3 (`POST /wp-json/wc/v3/products/{id}`) accepts a `meta_data` array for arbitrary meta writes. Use this to push Yoast/RankMath SEO fields programmatically:

```json
{
  "meta_data": [
    { "key": "_yoast_wpseo_title",    "value": "Black Rose Heavyweight Hoodie — SkyyRose" },
    { "key": "_yoast_wpseo_metadesc", "value": "Oakland-made heavyweight hoodie..." },
    { "key": "_yoast_wpseo_focuskw",  "value": "luxury streetwear hoodie" },
    { "key": "rank_math_title",       "value": "Black Rose Heavyweight Hoodie — SkyyRose" },
    { "key": "rank_math_description", "value": "Oakland-made heavyweight hoodie..." }
  ]
}
```

The `stock_status` field values from WC REST API v3 are: `instock`, `outofstock`, `onbackorder`. These map to schema.org availability URIs (see §Schema Markup below).

---

## Collection Page SEO

### Per-Collection Optimization

**Black Rose Collection:**
```
H1: Black Rose Collection — Limited Edition Oakland Streetwear
Meta Title: Black Rose Collection — Dark Luxury Streetwear | SkyyRose (56 chars)
Meta Desc: Limited edition streetwear from Oakland. Heavyweight hoodies, collector jerseys, statement pieces. Pre-order from SkyyRose Black Rose. (134 chars)
Focus: "limited edition streetwear", "Oakland streetwear"
Voice: armor / concrete / silver — "you already stood up"
```

**Love Hurts Collection:**
```
H1: Love Hurts Collection — Streetwear That Speaks
Meta Title: Love Hurts Collection — Luxury Streetwear | SkyyRose (52 chars)
Meta Desc: Raw emotion turned wearable. Varsity jackets, joggers, and shorts from SkyyRose Love Hurts. Limited pre-order runs. (115 chars)
Focus: "luxury streetwear collection", "varsity jacket streetwear"
Voice: bloodline / crimson — "bloodline that raised me" (Love Hurts ONLY)
```

**Signature Collection:**
```
H1: Signature Collection — Bay Area Everyday Luxury
Meta Title: Signature Collection — Bay Area Luxury Streetwear | SkyyRose (58 chars)
Meta Desc: Golden hour in cotton. Bay Area-inspired hoodies, shorts, and tees from SkyyRose Signature. Premium essentials, limited runs. (124 chars)
Focus: "Bay Area clothing", "luxury streetwear essentials"
Voice: stay golden / gold — everyday elevation
```

**Kids Capsule:**
```
H1: Kids Capsule — Little Royalty by SkyyRose
Meta Title: Kids Streetwear — SkyyRose Kids Capsule Collection (50 chars)
Meta Desc: Luxury streetwear for kids. Matching sets and elevated essentials. Black-owned, designed in Oakland. Shop SkyyRose Kids. (114 chars)
Focus: "kids streetwear", "Black-owned kids clothing"
Voice: little royalty / rose gold — never borrow from other collection voices
```

---

## Schema Markup (JSON-LD for WordPress)

> **Verified from schema.org v30.0 + WooCommerce REST API v3 docs**
>
> JSON-LD is Google's preferred structured data format. All `availability` values MUST use full schema.org URIs (e.g., `https://schema.org/InStock`), not bare strings.
>
> Availability URI mapping from WC `stock_status`:
> - `instock` → `https://schema.org/InStock`
> - `outofstock` → `https://schema.org/OutOfStock`
> - `onbackorder` → `https://schema.org/BackOrder`
> - WC pre-order meta flag → `https://schema.org/PreOrder`
>
> Other valid availability URIs: `https://schema.org/SoldOut`, `https://schema.org/LimitedAvailability`, `https://schema.org/Discontinued`.

### Product Schema + ItemPage Wrapper (corrected — `inc/seo.php`)

The original schema hardcoded `PreOrder` for all products regardless of stock status. **That was wrong.** The corrected version gates on the WC pre-order meta key first, then maps from `stock_status`.

```php
/**
 * Enhanced Product Schema for SkyyRose WooCommerce.
 *
 * Wraps Product in ItemPage (Google-preferred for PDPs).
 * Availability gated: pre-order meta → PreOrder, else WC stock_status map.
 * Adds AggregateRating for star-snippet eligibility (requires review_count > 0).
 * Adds gtin field when populated on product.
 *
 * @link https://schema.org/Product
 * @link https://schema.org/ItemPage
 */
add_action( 'wp_head', 'skyyrose_product_schema' );
function skyyrose_product_schema() {
    if ( ! is_product() ) {
        return;
    }

    global $product;
    if ( ! $product instanceof WC_Product ) {
        return;
    }

    // --- Availability: gate on pre-order meta first, then stock_status ---
    $preorder_meta = $product->get_meta( '_skyyrose_preorder' ); // custom meta key
    if ( ! $preorder_meta ) {
        // Also support WooCommerce Pre-Orders plugin meta key.
        $preorder_meta = $product->get_meta( '_wc_pre_orders_enabled' );
    }

    if ( $preorder_meta && 'yes' === $preorder_meta ) {
        $availability = 'https://schema.org/PreOrder';
    } else {
        $stock_map = array(
            'instock'     => 'https://schema.org/InStock',
            'outofstock'  => 'https://schema.org/OutOfStock',
            'onbackorder' => 'https://schema.org/BackOrder',
        );
        $wc_stock   = $product->get_stock_status(); // returns 'instock'|'outofstock'|'onbackorder'
        $availability = $stock_map[ $wc_stock ] ?? 'https://schema.org/OutOfStock';
    }

    // --- Core product fields ---
    $product_schema = array(
        '@type'       => 'Product',
        '@id'         => get_permalink() . '#product',
        'name'        => $product->get_name(),
        'description' => wp_strip_all_tags( $product->get_short_description() ),
        'image'       => wp_get_attachment_url( $product->get_image_id() ),
        'url'         => get_permalink(),
        'sku'         => $product->get_sku(),
        'brand'       => array(
            '@type' => 'Brand',
            'name'  => 'SkyyRose',
        ),
        'offers'      => array(
            '@type'         => 'Offer',
            'price'         => $product->get_price(),
            'priceCurrency' => 'USD',
            'url'           => get_permalink(),
            'availability'  => $availability,
            'itemCondition' => 'https://schema.org/NewCondition',
            'seller'        => array(
                '@type'  => 'Organization',
                '@id'    => 'https://skyyrose.co/#organization',
                'name'   => 'The Skyy Rose Collection LLC',
                'url'    => 'https://skyyrose.co',
            ),
        ),
    );

    // Optional: gtin (Global Trade Item Number) — populate via product meta if available.
    $gtin = $product->get_meta( '_gtin' );
    if ( $gtin ) {
        $product_schema['gtin'] = $gtin;
    }

    // AggregateRating — required for star snippet eligibility in Google SERPs.
    if ( $product->get_review_count() > 0 ) {
        $product_schema['aggregateRating'] = array(
            '@type'       => 'AggregateRating',
            'ratingValue' => (float) $product->get_average_rating(),
            'reviewCount' => (int) $product->get_review_count(),
            'worstRating' => 1,
            'bestRating'  => 5,
        );
    }

    // ItemPage wrapper — signals this is a product detail page to Google.
    $schema = array(
        '@context'   => 'https://schema.org',
        '@type'      => 'ItemPage',
        '@id'        => get_permalink() . '#itempage',
        'url'        => get_permalink(),
        'name'       => $product->get_name() . ' | SkyyRose',
        'mainEntity' => $product_schema,
    );

    echo '<script type="application/ld+json">'
        . wp_json_encode( $schema, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_HEX_TAG )
        . '</script>' . "\n";
}
```

**Key corrections from previous version:**
1. Was: `'availability' => $product->is_in_stock() ? 'https://schema.org/PreOrder' : 'https://schema.org/SoldOut'` — wrong in two ways: (a) hardcoded PreOrder for all in-stock items, (b) used SoldOut instead of OutOfStock for standard OOS. Fixed above.
2. Was missing `ItemPage` wrapper — now present.
3. Was missing `@id` anchors for cross-entity linking.
4. Was missing `worstRating`/`bestRating` on `AggregateRating` (required for star snippet eligibility).
5. Was missing `gtin` field.

---

### Organization Schema (site-wide, homepage only — `inc/seo.php`)

The Organization schema requires `@id` (a stable IRI acting as the canonical identifier for the Knowledge Graph) and `logo` as an `ImageObject` (not a bare URL string) for Google's Knowledge Panel eligibility. The `sameAs` array with brand social URLs signals entity equivalence and strengthens the Knowledge Graph entry.

```php
/**
 * Organization Schema for SkyyRose — emitted on homepage only.
 *
 * @id is a stable IRI used as canonical entity identifier across all pages.
 * logo must be ImageObject for Knowledge Panel eligibility.
 * sameAs strengthens Knowledge Graph entity resolution.
 *
 * @link https://schema.org/Organization
 */
add_action( 'wp_head', 'skyyrose_org_schema' );
function skyyrose_org_schema() {
    if ( ! is_front_page() ) {
        return;
    }

    $logo_url = get_template_directory_uri() . '/assets/images/branding/skyyrose-logo.png';

    $schema = array(
        '@context'    => 'https://schema.org',
        '@type'       => 'Organization',
        '@id'         => 'https://skyyrose.co/#organization',
        'name'        => 'The Skyy Rose Collection',
        'url'         => 'https://skyyrose.co',
        'logo'        => array(
            '@type'  => 'ImageObject',
            '@id'    => 'https://skyyrose.co/#logo',
            'url'    => $logo_url,
            'width'  => 512,
            'height' => 512,
        ),
        'image'       => array( '@id' => 'https://skyyrose.co/#logo' ),
        'description' => 'Luxury streetwear brand from Oakland, California.',
        'founder'     => array(
            '@type' => 'Person',
            'name'  => 'Corey Foster',
        ),
        'address'     => array(
            '@type'           => 'PostalAddress',
            'addressLocality' => 'Oakland',
            'addressRegion'   => 'CA',
            'addressCountry'  => 'US',
        ),
        'sameAs'      => array(
            'https://instagram.com/theskyyrosecollection',
            'https://tiktok.com/@skyyrose',
            'https://x.com/skyyrose',
        ),
    );

    echo '<script type="application/ld+json">'
        . wp_json_encode( $schema, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_HEX_TAG )
        . '</script>' . "\n";
}
```

**Key additions from previous version:**
1. Added `@id` — required for Knowledge Graph entity resolution; referenced by `offeredBy` in Offer schema.
2. Changed `logo` from bare URL string to `ImageObject` with `width`/`height` — required for Knowledge Panel eligibility.
3. Added `slogan` with verbatim tagline.

---

### ItemList Schema — Collection / Category Pages (Google product-carousel eligibility)

Product carousels in Google SERPs require an `ItemList` schema on collection/category pages, with each `ListItem` pointing to a product's URL. Without this, collection pages cannot appear in product carousel rich results.

```php
/**
 * ItemList Schema for SkyyRose collection / category pages.
 *
 * Emits on WooCommerce product category archives and custom collection templates.
 * Each ListItem must have a unique `url` pointing to the canonical product page.
 * Required for Google product-carousel eligibility.
 *
 * @link https://schema.org/ItemList
 */
add_action( 'wp_head', 'skyyrose_itemlist_schema' );
function skyyrose_itemlist_schema() {
    if ( ! is_product_category() && ! skyyrose_is_collection_page() ) {
        return;
    }

    // Fetch products for the current collection/category.
    if ( is_product_category() ) {
        $term = get_queried_object();
        $args = array(
            'post_type'      => 'product',
            'posts_per_page' => 50,
            'post_status'    => 'publish',
            'tax_query'      => array(
                array(
                    'taxonomy' => 'product_cat',
                    'field'    => 'term_id',
                    'terms'    => $term->term_id,
                ),
            ),
        );
    } else {
        // Custom collection template: pull by collection slug stored in body class / template.
        $collection_slug = skyyrose_get_current_template_slug(); // e.g. 'black-rose'
        $args = array(
            'post_type'      => 'product',
            'posts_per_page' => 50,
            'post_status'    => 'publish',
            'tax_query'      => array(
                array(
                    'taxonomy' => 'product_cat',
                    'field'    => 'slug',
                    'terms'    => $collection_slug,
                ),
            ),
        );
    }

    $loop = new WP_Query( $args );

    if ( ! $loop->have_posts() ) {
        return;
    }

    $items    = array();
    $position = 1;

    while ( $loop->have_posts() ) {
        $loop->the_post();
        $wc_product = wc_get_product( get_the_ID() );
        if ( ! $wc_product ) {
            continue;
        }

        $items[] = array(
            '@type'    => 'ListItem',
            'position' => $position++,
            'url'      => get_permalink(),
            'name'     => $wc_product->get_name(),
            'image'    => wp_get_attachment_url( $wc_product->get_image_id() ),
        );
    }
    wp_reset_postdata();

    if ( empty( $items ) ) {
        return;
    }

    $page_name = is_product_category()
        ? single_term_title( '', false )
        : get_the_title();

    $schema = array(
        '@context'        => 'https://schema.org',
        '@type'           => 'ItemList',
        'name'            => $page_name . ' | SkyyRose',
        'url'             => get_permalink() ?: get_term_link( get_queried_object() ),
        'itemListElement' => $items,
    );

    echo '<script type="application/ld+json">'
        . wp_json_encode( $schema, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_HEX_TAG )
        . '</script>' . "\n";
}

/**
 * Returns true when the current page is a SkyyRose custom collection template.
 * Checks for template-collection-*.php and template-landing-*.php.
 */
function skyyrose_is_collection_page() {
    if ( ! is_page() ) {
        return false;
    }
    $template = get_page_template_slug();
    return (bool) preg_match( '/template-(collection|landing)-/', $template );
}
```

---

### BreadcrumbList Schema

```php
/**
 * BreadcrumbList Schema for SkyyRose — emitted on all pages except homepage.
 *
 * @link https://schema.org/BreadcrumbList
 */
add_action( 'wp_head', 'skyyrose_breadcrumb_schema' );
function skyyrose_breadcrumb_schema() {
    if ( is_front_page() ) {
        return;
    }

    $items   = array();
    $items[] = array(
        '@type'    => 'ListItem',
        'position' => 1,
        'name'     => 'Home',
        'item'     => home_url( '/' ),
    );

    if ( is_product_category() ) {
        $term    = get_queried_object();
        $items[] = array(
            '@type'    => 'ListItem',
            'position' => 2,
            'name'     => 'Shop',
            'item'     => get_permalink( wc_get_page_id( 'shop' ) ),
        );
        $items[] = array(
            '@type'    => 'ListItem',
            'position' => 3,
            'name'     => $term->name,
            'item'     => get_term_link( $term ),
        );
    } elseif ( is_product() ) {
        global $product;
        $terms = get_the_terms( $product->get_id(), 'product_cat' );
        if ( $terms && ! is_wp_error( $terms ) ) {
            $items[] = array(
                '@type'    => 'ListItem',
                'position' => 2,
                'name'     => $terms[0]->name,
                'item'     => get_term_link( $terms[0] ),
            );
        }
        $items[] = array(
            '@type'    => 'ListItem',
            'position' => count( $items ) + 1,
            'name'     => $product->get_name(),
            'item'     => get_permalink(),
        );
    } elseif ( is_page() ) {
        $items[] = array(
            '@type'    => 'ListItem',
            'position' => 2,
            'name'     => get_the_title(),
            'item'     => get_permalink(),
        );
    }

    if ( count( $items ) < 2 ) {
        return; // Don't emit a breadcrumb with only Home.
    }

    $schema = array(
        '@context'        => 'https://schema.org',
        '@type'           => 'BreadcrumbList',
        'itemListElement' => $items,
    );

    echo '<script type="application/ld+json">'
        . wp_json_encode( $schema, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_HEX_TAG )
        . '</script>' . "\n";
}
```

---

## Technical SEO Checklist

### Core Web Vitals Targets
| Metric | Target | How to Check | Notes |
|--------|--------|-------------|-------|
| LCP (Largest Contentful Paint) | < 2.5s | PageSpeed Insights | Hero image → `fetchpriority="high"` + `<picture>` |
| INP (Interaction to Next Paint) | < 200ms | PageSpeed Insights | **Replaced FID as Core Web Vital in March 2024** |
| CLS (Cumulative Layout Shift) | < 0.1 | PageSpeed Insights | Explicit width/height on all images |

> **INP replaced FID (First Input Delay) as an official Core Web Vital in March 2024.** Any audit or tool output still referencing FID as a CWV is outdated. INP measures the full end-to-end latency of all interactions, not just the first one. Target < 200ms (good), < 500ms (needs improvement).

### Image Optimization
- [ ] All product images served as WebP (use `<picture>` with JPEG fallback)
- [ ] Lazy loading on below-fold images (`loading="lazy"`)
- [ ] `fetchpriority="high"` on the LCP hero image (do NOT lazy-load it)
- [ ] Explicit `width`/`height` attributes to prevent CLS
- [ ] Max file size: 200KB for product images, 500KB for hero banners
- [ ] Alt text on every image (use formula in §WooCommerce Product SEO)

### Sitemap & Indexing
- [ ] XML sitemap at `/sitemap.xml` (Yoast or RankMath generates this)
- [ ] Products, collections, and pages all in sitemap
- [ ] `robots.txt` blocks: `/cart/`, `/checkout/`, `/my-account/`, `/wp-admin/`
- [ ] No `noindex` on product or collection pages
- [ ] Submit sitemap to Google Search Console

### Canonical URLs
- [ ] Each product has a single canonical URL
- [ ] Variant pages (size, color) point canonical to main product
- [ ] Pre-order products use same URL when they transition to in-stock
- [ ] No duplicate content between collection pages and shop page

#### WooCommerce Canonical Handling: Paged + Filter URLs

WooCommerce generates paginated URLs (`?paged=2`) and filter URLs (`?pa_color=black`, `?orderby=price`) that create duplicate content. Handle them explicitly:

```php
/**
 * Canonical tag handling for WooCommerce paged and filter URLs.
 *
 * Paged shop/category pages: canonical points to page 1 (the root URL).
 * Filter URLs (?pa_color=, ?orderby=, ?min_price=): canonical strips filter params.
 *
 * Add to inc/seo.php — fires before Yoast/RankMath output (priority 1).
 */
add_action( 'wp_head', 'skyyrose_wc_canonical', 1 );
function skyyrose_wc_canonical() {
    if ( ! is_woocommerce() && ! is_shop() && ! is_product_category() ) {
        return;
    }

    // Strip known WC filter/sort params to get the canonical base URL.
    $filter_params = array(
        'paged', 'page', 'orderby', 'min_price', 'max_price',
        'rating_filter', 'product_cat', 'product_tag',
    );

    // Also strip any attribute filter params: pa_* (e.g., pa_color, pa_size).
    $current_url  = home_url( add_query_arg( null, null ) );
    $parsed       = wp_parse_url( $current_url );
    $query_string = $parsed['query'] ?? '';
    parse_str( $query_string, $query_vars );

    $is_filtered = false;
    foreach ( array_keys( $query_vars ) as $key ) {
        if ( in_array( $key, $filter_params, true ) || str_starts_with( $key, 'pa_' ) ) {
            $is_filtered = true;
            unset( $query_vars[ $key ] );
        }
    }

    if ( ! $is_filtered ) {
        return; // Let Yoast/RankMath handle the unmodified URL.
    }

    $canonical_path = $parsed['path'] ?? '/';
    $canonical_qs   = http_build_query( $query_vars );
    $canonical_url  = home_url( $canonical_path . ( $canonical_qs ? '?' . $canonical_qs : '' ) );

    // Output rel=canonical before Yoast/RankMath so they can detect and defer.
    printf( '<link rel="canonical" href="%s" />' . "\n", esc_url( $canonical_url ) );
}
```

**Also add to `robots.txt` (via Yoast SEO settings → Tools → File editor):**
```
Disallow: /*?orderby=
Disallow: /*?min_price=
Disallow: /*?max_price=
Disallow: /*?rating_filter=
```

> Do NOT disallow `?pa_color=` globally — these can be indexable if they represent meaningful filtered pages (e.g., a Black Rose colorway). Handle per-collection via canonical instead of blanket disallow.

### Mobile-First
- [ ] All pages pass Google Mobile-Friendly Test
- [ ] Touch targets >= 48px
- [ ] No horizontal scrolling on any page
- [ ] Font size >= 16px on mobile
- [ ] Product images swipeable on mobile gallery

### Page Speed
- [ ] Critical CSS inlined in `<head>`
- [ ] JavaScript deferred (`defer` attribute)
- [ ] Third-party scripts (analytics, chat) loaded async
- [ ] Font preloading for Archivo, Hanken Grotesk, Anton, Cinzel (self-hosted woff2 only — zero Google Fonts CDN)
- [ ] CDN cache headers set correctly (bump `SKYYROSE_VERSION` for busting)
- [ ] `.min.css` / `.min.js` served in production (`$use_min = !SCRIPT_DEBUG`) — every CSS/JS edit must rebuild via `scripts/build-css.js` + `build-js.js` or the fix is inert

---

## Site Architecture

### URL Hierarchy
```
skyyrose.co/
├── /shop/                          (all products)
├── /collections/black-rose/        (collection page)
├── /collections/love-hurts/
├── /collections/signature/
├── /collections/kids-capsule/
├── /product/black-rose-hoodie/     (individual product)
├── /product/bay-bridge-shorts/
├── /about/                         (brand story)
├── /preorder/                      (pre-order gateway)
└── /blog/                          (content marketing)
```

### Internal Linking Rules

1. Every product page links to its collection page
2. Every collection page links to all its products
3. Collection pages may cross-link to related collections (collection-to-collection is allowed)
4. Blog posts link to relevant products and collections
5. About page links to all collections
6. Pre-order gateway links to active pre-order products

**CRITICAL — Founder Canon: NO cross-sell / NO related products on PDPs**
- Do NOT show related products, upsell grids, or "Complete the Look" widgets on product detail pages
- The garment is the protagonist; no competing calls-to-action on PDP
- `add_action('woocommerce_single_product_summary', 'skyyrose_complete_the_look', 50)` is intentionally commented out in `inc/woocommerce.php`
- Collection-to-collection linking (e.g., Black Rose → Love Hurts via nav or collection pages) is fine; per-product cross-sell on PDP is not
- No urgency timers ("Only 3 left!") anywhere on the site

---

## SEO Audit Workflow

### Monthly Audit Checklist
1. **Search Console check:** crawl errors, index coverage, manual actions
2. **Keyword rankings:** track top 20 keywords, note movement
3. **Page speed:** run PageSpeed Insights on homepage + top 5 product pages
4. **Broken links:** scan with Screaming Frog or similar
5. **Content freshness:** update any product descriptions changed by new drops
6. **Schema validation:** test with Google Rich Results Test
7. **Mobile check:** spot-check 3 pages on actual phone
8. **Competitor check:** search top 5 keywords, note who's ranking
9. **INP check:** verify all key interactions < 200ms (replaced FID — use CrUX data in Search Console)

### Priority Fix Matrix
| Issue | Impact | Urgency | Fix First? |
|-------|--------|---------|-----------|
| Missing meta titles/descriptions | High | High | Yes |
| Missing product alt text | Medium | Medium | Yes |
| Slow page speed (>3s LCP) | High | High | Yes |
| INP > 200ms | High | High | Yes (Core Web Vital since Mar 2024) |
| Missing schema markup | Medium | Medium | After basics |
| Broken internal links | Medium | High | Yes |
| Thin product descriptions (<100 words) | Medium | Medium | Batch fix |
| Missing canonical tags | High | Medium | Yes |
| No XML sitemap submission | High | High | Yes |
| Filter/paged URLs without canonical | High | Medium | Yes |

### Audit Tool Notes (Verified Gotchas)

- **WebFetch strips `<script>` tags** — NEVER use WebFetch to audit JSON-LD, OpenGraph `<script>` blocks, or any inline JS. Use `curl -s URL | grep 'application/ld+json'` instead. WebFetch-based audits will falsely report zero structured data.
- **WP.com Batcache serves stale HTML for ~minutes after cache flush** — Always cache-bust post-deploy with `curl -s "https://skyyrose.co/?cb=$(date +%s)"`.
- **Multi-agent audit P0 false-positive rate ~25%** — Audit findings are starting points, not truth. Verify against live state with curl + grep before drafting fixes.

---

## Recovery Section

### Ranking Drop Response Protocol

1. **Check Search Console immediately** — identify which URLs dropped and when. Compare to deploy dates.
2. **Check for manual actions** — `Search Console → Security & Manual Actions`. Manual action = human reviewer found a policy violation.
3. **Check Core Web Vitals report** — CWV degradation correlates with ranking drops, especially on mobile. Verify INP (< 200ms), LCP (< 2.5s), CLS (< 0.1).
4. **Check for accidental `noindex`** — a theme update or Yoast misconfiguration can silently noindex product pages. Verify with `curl -s https://skyyrose.co/product/[slug]/ | grep 'noindex'`.
5. **Check canonical tags** — if a deploy changed URL structure without 301 redirects, Google may have switched to a different canonical. `curl -s URL | grep 'canonical'`.
6. **Validate schema** — broken JSON-LD causes Google to drop rich snippets. Test with [Google Rich Results Test](https://search.google.com/test/rich-results). Fix PHP syntax errors in `inc/seo.php`.
7. **Check index coverage** — `Search Console → Pages` for excluded/error URLs.
8. **Verify sitemap** — `curl -s https://skyyrose.co/sitemap.xml | grep '<loc>'` confirms product pages are in the sitemap.

### Common Recovery Scenarios

**Scenario: Star snippets disappeared**
- AggregateRating missing `worstRating`/`bestRating` → add both fields (1 / 5)
- Review count is 0 → star snippets require at least 1 review
- Schema validation error in `inc/seo.php` → test with Rich Results Test

**Scenario: Product pages dropped from index**
- Check `robots.txt` — WooCommerce can expose `/product/` to noindex via misconfiguration
- Check Yoast SEO → Search Appearance → Products — ensure `noindex` is NOT set
- Check for trailing slash inconsistency — canonical URL must match sitemap URL exactly

**Scenario: Collection pages not appearing in product carousels**
- `ItemList` schema missing → add `skyyrose_itemlist_schema()` (see §Schema Markup)
- `ItemList` items missing `url` → each ListItem requires a canonical product URL
- Validate with Rich Results Test → look for "Product carousel" eligibility

**Scenario: Site dropped from Knowledge Panel**
- Organization `@id` missing or changed → ensure `https://skyyrose.co/#organization` is stable
- `logo` as bare URL string instead of `ImageObject` → fix `skyyrose_org_schema()` (see above)
- `sameAs` social URLs outdated → verify Instagram/TikTok/X handles are current

**Scenario: Paged/filter URLs indexed as duplicate content**
- Missing canonical on `?paged=2`, `?orderby=`, `?pa_color=` URLs → add `skyyrose_wc_canonical()` (see §Canonical URLs)
- Add filter params to `robots.txt` Disallow (except meaningful attribute filters)

---

## Anti-Patterns

- **DO NOT** keyword-stuff product titles — "Luxury Hoodie Black Rose Hoodie Oakland Streetwear Hoodie" is spam
- **DO NOT** use the same meta description on multiple pages — each page needs unique meta
- **DO NOT** block CSS/JS in robots.txt — Googlebot needs to render pages
- **DO NOT** use JavaScript-only content for product descriptions — crawlers may miss it
- **DO NOT** ignore Search Console warnings — they indicate real indexing problems
- **DO NOT** change URLs without 301 redirects — broken links kill SEO equity
- **DO NOT** rely solely on Yoast green lights — Yoast checks basics, not strategy
- **DO NOT** hardcode `availability => PreOrder` for all products — gate on pre-order meta + stock_status map
- **DO NOT** use bare availability strings like `"InStock"` — always use full URIs: `"https://schema.org/InStock"`
- **DO NOT** omit `@id` from Organization schema — required for Knowledge Graph
- **DO NOT** use a bare URL string for `logo` in Organization — must be `ImageObject`
- **DO NOT** omit `ItemList` schema from collection pages — required for product carousel eligibility
- **DO NOT** add related products, upsell widgets, or cross-sell sections to product detail pages — violates founder canon
- **DO NOT** use urgency timers ("Only X left!") anywhere on the site — violates brand canon
- **DO NOT** use FID as a Core Web Vital target — it was replaced by INP in March 2024
- **DO NOT** audit structured data with WebFetch — it strips `<script>` tags; use `curl` + `grep`
- **DO NOT** cross-attribute collection voices — "bloodline that raised me" belongs to Love Hurts only
