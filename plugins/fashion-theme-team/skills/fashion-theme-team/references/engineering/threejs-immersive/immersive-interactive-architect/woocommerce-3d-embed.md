# WooCommerce 3D Product Embed Patterns — Immersive Interactive Architect Reference

Load when: embedding a `<model-viewer>` 3D product viewer on a WooCommerce PDP: GLB loading, AR quick-look, WordPress enqueue, lazy-load on scroll.

Provenance: embedded copy of `host repo (DevSkyy) .claude/skills/immersive-interactive-architect/references/woocommerce-3d-embed.md`; verbatim except the adaptations recorded in [index.md](../index.md).

Embedding a 3D product viewer on a WooCommerce PDP (Product Detail Page) via the
`<model-viewer>` web component. Covers GLB loading, AR quick-look, WordPress enqueue
patterns, and lazy-load on scroll.

---

## 1. model-viewer Overview

`<model-viewer>` is a Google-maintained web component that handles:
- GLB/GLTF rendering via WebGL (Three.js internally)
- AR quick-look on iOS (USDZ) and scene-viewer on Android
- WebXR AR on Chrome (Android)
- Built-in camera controls, auto-rotate, environment lighting
- No Three.js setup required — drop-in HTML

---

## 2. WordPress Enqueue Pattern

**Product source of truth.** The single editable product source of truth is `logo-registry.json` (DevSkyy: root symlink to `<theme-root>/data/logo-registry.json`). Its `products[sku]` records own commerce fields and image/source bindings. CSV, dossiers, and `sot-images.json` manifests are generated projections or consumers, read through sanctioned readers and never authored. Corey, the founder and maker, is authoritative on his own product specs: `FOUNDER_CONFIRMED`, with no third-party verification demanded. 3D product models must be the correct garment for the SKU. Never present a hallucinated or never-made product. 3D model bindings are not yet a registry field; adding one is a registry schema change that requires founder approval. Until then the `_product_3d_glb_url` / `_product_3d_usdz_url` post meta read below is host-managed, must reference the correct garment for the SKU, and never outranks `logo-registry.json`.

**Never load `<model-viewer>` on every page** — it's a large script (~350KB).
Gate it to single product pages only, and only when the product has a 3D asset.

```php
// <theme-root>/inc/woocommerce.php (or <theme-root>/inc/enqueue.php)

/**
 * Enqueue model-viewer only on single product pages that have a 3D asset.
 *
 * @return void
 */
function skyyrose_enqueue_model_viewer(): void {
    if ( ! is_singular( 'product' ) ) {
        return;
    }

    global $post;
    $glb_url = get_post_meta( $post->ID, '_product_3d_glb_url', true );

    if ( empty( $glb_url ) ) {
        return; // No 3D asset for this product — skip
    }

    // model-viewer as a module (type=module is required by the spec)
    wp_enqueue_script(
        'skyyrose-model-viewer',
        'https://ajax.googleapis.com/ajax/libs/model-viewer/3.3.0/model-viewer.min.js',
        [],
        '3.3.0',
        [ 'strategy' => 'defer', 'in_footer' => true ]
    );

    // Pass product data to JS
    wp_localize_script(
        'skyyrose-model-viewer',
        'SKYYROSE_PRODUCT_3D',
        [
            'glbUrl'   => esc_url( $glb_url ),
            'usdzUrl'  => esc_url( get_post_meta( $post->ID, '_product_3d_usdz_url', true ) ),
            'poster'   => esc_url( get_the_post_thumbnail_url( $post->ID, 'large' ) ),
            'productId'=> $post->ID,
        ]
    );
}
add_action( 'wp_enqueue_scripts', 'skyyrose_enqueue_model_viewer' );
```

> Note: `wp_enqueue_script` with `strategy => defer` requires WordPress 6.3+.
> On older installations, use `wp_register_script` and enqueue in `wp_footer`.

---

## 3. Single Product Template Integration

WooCommerce's single product layout hooks let us inject the viewer without modifying
core template files.

```php
// <theme-root>/inc/woocommerce.php

/**
 * Inject model-viewer above the product images on single product pages.
 *
 * @return void
 */
function skyyrose_inject_3d_viewer(): void {
    global $post;
    $glb_url = get_post_meta( $post->ID, '_product_3d_glb_url', true );
    if ( empty( $glb_url ) ) {
        return;
    }
    get_template_part( 'template-parts/product/3d-viewer' );
}
add_action( 'woocommerce_before_single_product_summary', 'skyyrose_inject_3d_viewer', 5 );
```

---

## 4. Template Part — <theme-root>/template-parts/product/3d-viewer.php

```php
<?php
/**
 * 3D product viewer template part.
 * Requires SKYYROSE_PRODUCT_3D JS object to be localized (see enqueue.php).
 *
 * @package SkyyRose
 */

defined( 'ABSPATH' ) || exit;

global $post;
$glb_url  = esc_url( get_post_meta( $post->ID, '_product_3d_glb_url', true ) );
$usdz_url = esc_url( get_post_meta( $post->ID, '_product_3d_usdz_url', true ) );
$poster   = esc_url( get_the_post_thumbnail_url( $post->ID, 'large' ) );

if ( empty( $glb_url ) ) {
    return;
}
?>

<div class="sr-3d-viewer-wrap" data-product-id="<?php echo esc_attr( $post->ID ); ?>">

    <model-viewer
        id="sr-model-viewer"
        src="<?php echo esc_url( $glb_url ); ?>"
        <?php if ( $usdz_url ) : ?>
        ios-src="<?php echo esc_url( $usdz_url ); ?>"
        <?php endif; ?>
        poster="<?php echo $poster; ?>"
        alt="<?php echo esc_attr( get_the_title() ); ?> — interactive 3D product view"
        shadow-intensity="0.8"
        environment-image="neutral"
        exposure="1.0"
        camera-controls
        auto-rotate
        auto-rotate-delay="3000"
        rotation-per-second="20deg"
        ar
        ar-modes="webxr scene-viewer quick-look"
        ar-scale="fixed"
        loading="lazy"
        reveal="interaction"
        style="width:100%;height:500px;background:var(--skyyrose-bg,#0A0A0A);border-radius:8px;"
    >
        <!-- AR button — only shown when AR is available on device -->
        <button slot="ar-button" class="sr-ar-btn btn-sweep">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
            View in Your Space
        </button>

        <!-- Progress bar during GLB load -->
        <div slot="progress-bar" class="sr-3d-progress">
            <div class="sr-3d-progress__fill"></div>
        </div>

        <!-- Fallback when WebGL is unavailable -->
        <div slot="error">
            <?php
            $thumb = get_the_post_thumbnail( $post->ID, 'large', [ 'alt' => esc_attr( get_the_title() ) ] );
            echo wp_kses_post( $thumb );
            ?>
            <p class="sr-3d-error-msg"><?php esc_html_e( '3D viewer requires WebGL. Your browser may not support it.', 'skyyrose' ); ?></p>
        </div>
    </model-viewer>

    <!-- View switcher: toggle between 3D and standard photos -->
    <div class="sr-viewer-tabs" role="tablist" aria-label="<?php esc_attr_e( 'Product view options', 'skyyrose' ); ?>">
        <button role="tab" aria-selected="true"  class="sr-viewer-tab is-active" data-view="3d">3D View</button>
        <button role="tab" aria-selected="false" class="sr-viewer-tab"           data-view="photos">Photos</button>
    </div>

</div>
```

---

## 5. AR Attribute Reference

```html
<!-- Essential AR attributes -->
<model-viewer
  src="product.glb"
  ios-src="product.usdz"        <!-- iOS AR Quick Look (USDZ required) -->

  ar                             <!-- enables AR button when supported -->
  ar-modes="webxr scene-viewer quick-look"
  <!-- Preference order:
       1. webxr      = Chrome Android 81+ (full AR, best)
       2. scene-viewer = Android native Google scene viewer
       3. quick-look   = iOS Safari AR (requires USDZ) -->

  ar-scale="fixed"               <!-- don't let user resize in AR; 'auto' = resizable -->
  ar-placement="floor"           <!-- 'floor' or 'wall' placement hint -->

  xr-environment                 <!-- use real-world lighting in AR (iOS) -->
>
```

**USDZ generation**: Convert GLB → USDZ via `usd_from_gltf` (Apple Reality Converter,
free) or the Blender USD exporter. Store alongside GLB and set both product meta fields (host-managed; 3D bindings are not yet a registry field).

---

## 6. Lazy-Load on Scroll (IntersectionObserver)

`loading="lazy"` on `<model-viewer>` defers the GLB fetch until the component is
visible. For additional control (e.g., only load after user interaction), use an
IntersectionObserver to swap a data-src:

```javascript
// Lazy-load: only inject src when viewer scrolls into viewport
document.addEventListener('DOMContentLoaded', () => {
  const viewer = document.getElementById('sr-model-viewer');
  if (!viewer) return;

  const glbUrl = viewer.dataset.src; // use data-src to defer
  if (!glbUrl) return;

  const observer = new IntersectionObserver(
    ([entry]) => {
      if (!entry.isIntersecting) return;
      viewer.setAttribute('src', glbUrl);
      observer.disconnect();
    },
    { rootMargin: '200px 0px', threshold: 0 } // load 200px before entering viewport
  );
  observer.observe(viewer);
});
```

PHP template change for deferred loading:
```php
<!-- Replace src= with data-src= and add loading sentinel -->
<model-viewer
    id="sr-model-viewer"
    data-src="<?php echo $glb_url; ?>"
    src=""
    poster="<?php echo $poster; ?>"
    <!-- ... other attrs ... -->
>
```

---

## 7. model-viewer JavaScript API

```javascript
const viewer = document.getElementById('sr-model-viewer');

// Wait for model to finish loading
viewer.addEventListener('load', () => {
  console.log('GLB loaded — model ready');

  // Switch camera angle programmatically
  viewer.cameraOrbit = '45deg 75deg 3m'; // azimuth, polar, radius
  viewer.cameraTarget = '0m 0.5m 0m';   // look at torso center
});

// Monitor AR status
viewer.addEventListener('ar-status', (e) => {
  if (e.detail.status === 'session-started') {
    skyyToast('Viewing in AR', 'success', 3000); // SkyyRose global toast
  }
  if (e.detail.status === 'failed') {
    skyyToast('AR unavailable on this device', 'info', 3000);
  }
});

// Variant switching: swap GLB src when user picks a colorway
document.querySelectorAll('.sr-variant-swatch').forEach((swatch) => {
  swatch.addEventListener('click', () => {
    const newSrc = swatch.dataset.glbUrl;
    if (newSrc && newSrc !== viewer.src) {
      viewer.src = newSrc;
      // Update poster to matching colorway thumbnail
      viewer.poster = swatch.dataset.thumbnail || '';
    }
  });
});
```

---

## 8. WooCommerce Product Meta Fields (PHP)

Register the custom meta fields so they appear in the product edit screen. These fields are host-managed until the registry gains a 3D binding field (see section 2); an admin edit here never outranks `logo-registry.json` product facts:

```php
/**
 * Add 3D asset URL fields to the WooCommerce product General tab.
 *
 * @return void
 */
function skyyrose_add_3d_product_fields(): void {
    echo '<div class="options_group">';

    woocommerce_wp_text_input( [
        'id'          => '_product_3d_glb_url',
        'label'       => __( '3D Model (GLB URL)', 'skyyrose' ),
        'placeholder' => 'https://cdn.skyyrose.co/models/product.glb',
        'desc_tip'    => true,
        'description' => __( 'Self-hosted GLB file. HTTPS required. Recommended: ≤ 5MB for mobile.', 'skyyrose' ),
    ] );

    woocommerce_wp_text_input( [
        'id'          => '_product_3d_usdz_url',
        'label'       => __( '3D Model iOS AR (USDZ URL)', 'skyyrose' ),
        'placeholder' => 'https://cdn.skyyrose.co/models/product.usdz',
        'desc_tip'    => true,
        'description' => __( 'iOS AR Quick Look requires USDZ. Convert from GLB via Apple Reality Converter.', 'skyyrose' ),
    ] );

    echo '</div>';
}
add_action( 'woocommerce_product_options_general_product_data', 'skyyrose_add_3d_product_fields' );

/**
 * Save the 3D asset meta fields.
 *
 * @param int $post_id Product post ID.
 * @return void
 */
function skyyrose_save_3d_product_fields( int $post_id ): void {
    $glb  = isset( $_POST['_product_3d_glb_url'] )  ? esc_url_raw( sanitize_text_field( wp_unslash( $_POST['_product_3d_glb_url'] ) ) )  : '';
    $usdz = isset( $_POST['_product_3d_usdz_url'] ) ? esc_url_raw( sanitize_text_field( wp_unslash( $_POST['_product_3d_usdz_url'] ) ) ) : '';

    update_post_meta( $post_id, '_product_3d_glb_url',  $glb );
    update_post_meta( $post_id, '_product_3d_usdz_url', $usdz );
}
add_action( 'woocommerce_process_product_meta', 'skyyrose_save_3d_product_fields' );
```

---

## 9. CSS — Viewer Styling

```css
/* sr-3d-viewer-wrap lives above the WooCommerce product gallery */
.sr-3d-viewer-wrap {
    position: relative;
    width: 100%;
    border-radius: 8px;
    overflow: hidden;
    background: var(--skyyrose-bg, #0A0A0A);
}

/* AR button — matches SkyyRose btn-sweep style */
.sr-ar-btn {
    position: absolute;
    bottom: 16px;
    right: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 20px;
    background: var(--skyyrose-accent, #B76E79);
    color: #fff;
    border: none;
    border-radius: 4px;
    font-family: var(--skyyrose-font-ui, 'Anton', sans-serif);
    font-size: 0.875rem;
    letter-spacing: 0.08em;
    cursor: pointer;
    transition: opacity 0.2s ease;
}
.sr-ar-btn:hover { opacity: 0.85; }

/* Progress bar during GLB load */
.sr-3d-progress {
    width: 100%;
    height: 3px;
    background: rgba(255,255,255,0.1);
    position: absolute;
    bottom: 0;
}
.sr-3d-progress__fill {
    height: 100%;
    background: var(--skyyrose-accent, #B76E79);
    width: 0%;
    transition: width 0.3s ease;
}

/* Tab switcher */
.sr-viewer-tabs {
    display: flex;
    gap: 0;
    border-top: 1px solid rgba(255,255,255,0.1);
}
.sr-viewer-tab {
    flex: 1;
    padding: 10px;
    background: transparent;
    color: rgba(255,255,255,0.5);
    border: none;
    font-family: var(--skyyrose-font-ui, 'Anton', sans-serif);
    font-size: 0.8rem;
    letter-spacing: 0.1em;
    cursor: pointer;
    transition: color 0.2s, border-bottom 0.2s;
    border-bottom: 2px solid transparent;
}
.sr-viewer-tab.is-active {
    color: var(--skyyrose-accent, #B76E79);
    border-bottom-color: var(--skyyrose-accent, #B76E79);
}

@media (max-width: 768px) {
    model-viewer { height: 360px !important; }
    .sr-ar-btn   { bottom: 12px; right: 12px; padding: 8px 14px; }
}
```

---

## 10. GLB Asset Guidelines

| Spec              | Target         | Hard Max  |
|-------------------|----------------|-----------|
| File size         | < 3MB          | 8MB       |
| Triangle count    | < 30k          | 80k       |
| Textures          | 1024×1024 each | 2048×2048 |
| Texture format    | KTX2 / Basis   | WebP OK   |
| Animations        | Baked to clips | No rigs   |

- Use `gltf-transform optimize` (CLI) to compress geometry + textures before upload. Uploading the asset is outside plugin scope — the Fashion Theme Team builds and reviews candidates only; production deploys, live WooCommerce/media writes, and paid calls belong to the host repo's STOP-AND-SHOW approval process.
- Draco compression reduces file size 60-70% with no visual loss.
  - Host-repo gotcha (DevSkyy mascot rig): Draco corrupted skinned meshes. For skinned or animated characters use meshopt + quantize instead, and consumers must call `setMeshoptDecoder`. Draco stays fine for static meshes.
- Always supply a `poster` image — shown during GLB load; keeps perceived performance high.
