<?php
/**
 * SkyyRose Flagship 2 theme foundation.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

define( 'SKYYROSE2_VERSION', '2.4.4' );
define( 'SKYYROSE2_DIR', get_template_directory() );
define( 'SKYYROSE2_URI', get_template_directory_uri() );

/* Fresh-install, demo-import, and editor integration. */
require_once SKYYROSE2_DIR . '/inc/marketplace.php';
require_once SKYYROSE2_DIR . '/inc/performance.php';
require_once SKYYROSE2_DIR . '/inc/frame-delivery.php';
require_once SKYYROSE2_DIR . '/inc/archive-style-bundle.php';
require_once SKYYROSE2_DIR . '/inc/seo-indexing.php';
require_once SKYYROSE2_DIR . '/inc/security.php';
require_once SKYYROSE2_DIR . '/inc/approved-card-fronts.php';
require_once SKYYROSE2_DIR . '/inc/pdp-media-delivery.php';
require_once SKYYROSE2_DIR . '/inc/hero-commerce-scenes.php';
require_once SKYYROSE2_DIR . '/inc/global-shell.php';
require_once SKYYROSE2_DIR . '/inc/shop-archive.php';
require_once SKYYROSE2_DIR . '/inc/quick-view-commerce.php';
require_once SKYYROSE2_DIR . '/inc/critical-rendering.php';

/**
 * Resolve a theme-bundled, SOT-approved asset.
 *
 * @param string $path Path beneath assets/sot.
 * @return string
 */
function skyyrose2_sot_asset_uri( $path ) {
	return SKYYROSE2_URI . '/assets/sot/' . ltrim( $path, '/' );
}

/**
 * Resolve an exact snapshot from the current Scroll World sequence.
 *
 * @param string $path Snapshot filename.
 * @return string
 */
function skyyrose2_scroll_world_asset_uri( $path ) {
	return SKYYROSE2_URI . '/assets/scroll-world/' . ltrim( $path, '/' );
}

/**
 * Resolve the dedicated immersive story page for a collection.
 *
 * @param string $collection Collection slug.
 * @return string
 */
function skyyrose2_immersive_url( $collection ) {
	$collection = sanitize_title( $collection );
	if ( ! in_array( $collection, array( 'signature', 'black-rose', 'love-hurts', 'kids-capsule' ), true ) ) {
		return skyyrose2_marketplace_page_url( 'worlds' );
	}
	return skyyrose2_marketplace_page_url( 'immersive-' . $collection );
}

/**
 * Resolve collection world imagery from its declared source, never from a
 * filename guess. Scroll World files and V2 SOT files have distinct roots.
 *
 * @param array<string,mixed> $scene Declared collection world scene.
 * @return string
 */
function skyyrose2_collection_scene_uri( $scene ) {
	if ( empty( $scene['image'] ) ) {
		return '';
	}
	return isset( $scene['source'] ) && 'scroll-world' === $scene['source'] ? skyyrose2_scroll_world_asset_uri( $scene['image'] ) : skyyrose2_sot_asset_uri( $scene['image'] );
}

/**
 * Return hash-verified founder-selected V2 placeholder media.
 *
 * Placeholders are deliberately separate from final scene approval. An invalid
 * or stale placeholder record is ignored and the approved plate remains the
 * runtime fallback.
 *
 * @return array<string,array<string,mixed>>
 */
function skyyrose2_founder_scene_placeholders() {
	static $placeholders = null;
	if ( null !== $placeholders ) {
		return $placeholders;
	}

	$path     = SKYYROSE2_DIR . '/data/founder-selected-theme-placeholders-v1.json';
	$contents = is_readable( $path ) ? file_get_contents( $path ) : false; // phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents
	$decoded  = $contents ? json_decode( $contents, true ) : null;
	if (
		! is_array( $decoded ) ||
		'skyyrose.v2.founder-selected-theme-placeholders.v1' !== ( $decoded['schema'] ?? '' ) ||
		! is_array( $decoded['scene_placeholders'] ?? null )
	) {
		$placeholders = array();
		return $placeholders;
	}

	$placeholders = array();
	foreach ( $decoded['scene_placeholders'] as $scene_id => $placeholder ) {
		$asset = ltrim( (string) ( $placeholder['asset'] ?? '' ), '/' );
		$hash  = (string) ( $placeholder['sha256'] ?? '' );
		$file  = $asset ? SKYYROSE2_DIR . '/assets/scroll-world/' . $asset : '';
		$actual_hash = $file && is_file( $file ) ? hash_file( 'sha256', $file ) : '';
		if (
			'FOUNDER_SELECTED_PLACEHOLDER' !== ( $placeholder['state'] ?? '' ) ||
			! $asset ||
			! $hash ||
			! is_string( $actual_hash ) ||
			! hash_equals( $hash, $actual_hash )
		) {
			continue;
		}

		$placeholder['asset'] = $asset;
		$placeholders[ sanitize_key( strtolower( (string) $scene_id ) ) ] = $placeholder;
	}

	return $placeholders;
}

/**
 * Return the founder-approved commerce-scene contract for one collection.
 *
 * The JSON contract is the single runtime owner of scene IDs, plate assets,
 * exact SKU casts, model layers, approval state, and CTA language. A malformed
 * or unapproved contract fails closed to the legacy narrative worlds.
 *
 * @param string $collection Collection slug.
 * @return array<int,array<string,mixed>>
 */
function skyyrose2_collection_commerce_scenes( $collection ) {
	static $contract = null;

	if ( null === $contract ) {
		$path     = SKYYROSE2_DIR . '/data/scene-narrative-blueprints.json';
		$contents = is_readable( $path ) ? file_get_contents( $path ) : false;
		$decoded  = $contents ? json_decode( $contents, true ) : null;
		$contract = is_array( $decoded ) ? $decoded : array();
	}

	$collection = sanitize_title( $collection );
	$chapters   = $contract['collections'][ $collection ]['commerce_scene_chapters'] ?? array();
	if ( empty( $chapters ) || ! is_array( $chapters ) ) {
		return array();
	}

	$scenes       = array();
	$placeholders = skyyrose2_founder_scene_placeholders();
	foreach ( $chapters as $chapter ) {
		$plate_state = (string) ( $chapter['plate_approval_state'] ?? '' );
		if ( empty( $chapter['scene_id'] ) || empty( $chapter['plate_asset'] ) || 0 !== strpos( $plate_state, 'FOUNDER_APPROVED' ) ) {
			return array();
		}

		$scene_key   = sanitize_key( strtolower( (string) $chapter['scene_id'] ) );
		$placeholder = $placeholders[ $scene_key ] ?? array();
		$use_placeholder = ! empty( $placeholder ) && $collection === sanitize_title( $placeholder['collection'] ?? '' );

		$chapter['image']  = $use_placeholder ? $placeholder['asset'] : $chapter['plate_asset'];
		$chapter['source'] = 'scroll-world';
		$chapter['width']  = absint( $use_placeholder ? ( $placeholder['dimensions'][0] ?? 1672 ) : ( $chapter['plate_dimensions'][0] ?? 1672 ) );
		$chapter['height'] = absint( $use_placeholder ? ( $placeholder['dimensions'][1] ?? 941 ) : ( $chapter['plate_dimensions'][1] ?? 941 ) );
		$chapter['placeholder_active'] = $use_placeholder;
		$chapter['placeholder_state']  = $use_placeholder ? (string) $placeholder['state'] : '';
		$chapter['placeholder_role']   = $use_placeholder ? (string) ( $placeholder['role'] ?? '' ) : '';
		$chapter['suppress_model_layers_for_placeholder'] = $use_placeholder && ! empty( $placeholder['suppress_model_layers'] );
		$chapter = skyyrose2_apply_hero_commerce_scene( $chapter, $collection );
		$chapter = skyyrose2_apply_collection_scene_motion( $chapter, $collection );
		if ( ! skyyrose2_approved_scroll_world_scene( $chapter, $collection ) ) { continue; }
		$scenes[]          = $chapter;
	}

	return $scenes;
}

/** Fail closed outside the exact final scene set; authority is not inferred from file presence. */
function skyyrose2_approved_scroll_world_scene( $scene, $collection ) {
	static $approved = null;
	if ( null === $approved ) {
		$path = SKYYROSE2_DIR . '/data/approved-scroll-world-scenes.json';
		$decoded = is_readable( $path ) ? json_decode( file_get_contents( $path ), true ) : array(); // phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents
		$approved = is_array( $decoded ) && 1 === ( $decoded['schema_version'] ?? 0 ) ? ( $decoded['scenes'] ?? array() ) : array();
	}
	$record = $approved[ $scene['scene_id'] ?? '' ] ?? array();
	if ( 'APPROVED FINAL — IMPLEMENT' !== ( $record['approval_status'] ?? '' ) || $collection !== ( $record['collection'] ?? '' ) || ! empty( $scene['model_layers'] ) || ! empty( $scene['hero_composition']['variants'] ) ) { return false; }
	$assets = array();
	foreach ( $record['required_runtime_assets'] ?? array() as $asset ) { $assets[ $asset['role'] ] = $asset['path']; }
	foreach ( array( 'poster' => $scene['image'] ?? '', 'desktop' => $scene['scene_motion']['desktop'] ?? '', 'mobile' => $scene['scene_motion']['mobile'] ?? '' ) as $role => $path ) {
		if ( ! $path || ( 'assets/scroll-world/' . $path ) !== ( $assets[ $role ] ?? '' ) ) { return false; }
	}
	return array_values( $scene['product_bindings'] ?? array() ) === array_values( $record['cta']['product_bindings'] ?? array() );
}

/**
 * Resolve every exact product slot in a founder commerce scene.
 *
 * Missing products remain explicit slots. Nothing is substituted and an
 * incomplete cast cannot masquerade as a complete look or set.
 *
 * @param array<string,mixed> $scene Scene contract.
 * @param string              $collection Required collection slug.
 * @return array{state:string,slots:array<int,array<string,mixed>>,missing:array<int,string>}
 */
function skyyrose2_resolve_commerce_scene_products( $scene, $collection ) {
	$skus     = array_values( array_filter( array_map( 'sanitize_key', (array) ( $scene['product_bindings'] ?? array() ) ) ) );
	$resolved = skyyrose2_get_products_by_skus( $skus, $collection );
	$slots    = array();
	$missing  = array();

	foreach ( $skus as $sku ) {
		$product = $resolved[ $sku ] ?? false;
		$state   = $product ? 'ready' : 'unavailable';
		if ( $product && ( ! $product->is_purchasable() || ! $product->is_in_stock() ) ) {
			$state = 'currently_unavailable';
		}
		if ( ! $product ) {
			$missing[] = $sku;
		}
		$slots[] = array(
			'sku'     => $sku,
			'state'   => $state,
			'product' => $product,
		);
	}

	$state = empty( $missing ) ? 'ready' : ( count( $missing ) === count( $skus ) ? 'unavailable' : 'partial' );
	return array(
		'state'   => $state,
		'slots'   => $slots,
		'missing' => $missing,
	);
}

/**
 * Return truthful scene-action copy from the live WooCommerce product state.
 *
 * @param WC_Product $product WooCommerce product.
 * @param bool       $preorder_requested Scene requires preorder language.
 * @return string
 */
function skyyrose2_scene_product_action_label( $product, $preorder_requested = false ) {
	$name         = $product->get_name();
	$presentation = skyyrose2_product_presentation( $product );
	$is_preorder  = $preorder_requested && ! empty( $presentation['is_preorder'] );

	if ( ! $product->is_purchasable() || ! $product->is_in_stock() ) {
		return sprintf( __( 'View %s — currently unavailable', 'skyyrose-flagship-2' ), $name );
	}
	if ( $is_preorder && method_exists( $product, 'is_type' ) && $product->is_type( 'variable' ) ) {
		return sprintf( __( 'Choose options for %s', 'skyyrose-flagship-2' ), $name );
	}
	if ( $is_preorder ) {
		return sprintf( __( 'View %s', 'skyyrose-flagship-2' ), $name );
	}
	return sprintf( __( 'View %s', 'skyyrose-flagship-2' ), $name );
}

/** Theme supports and navigation slots. */
function skyyrose2_setup() {
	load_theme_textdomain( 'skyyrose-flagship-2', SKYYROSE2_DIR . '/languages' );
	add_theme_support( 'title-tag' );
	add_theme_support( 'post-thumbnails' );
	add_theme_support( 'responsive-embeds' );
	add_theme_support( 'align-wide' );
	add_theme_support(
		'html5',
		array( 'search-form', 'comment-form', 'comment-list', 'gallery', 'caption', 'style', 'script' )
	);
	add_theme_support( 'custom-logo', array( 'height' => 80, 'width' => 320, 'flex-height' => true, 'flex-width' => true ) );
	add_theme_support( 'woocommerce' );
	add_theme_support( 'wc-product-gallery-zoom' );
	add_theme_support( 'wc-product-gallery-lightbox' );
	add_theme_support( 'wc-product-gallery-slider' );
	register_nav_menus(
		array(
			'primary' => __( 'Primary Menu', 'skyyrose-flagship-2' ),
			'footer'  => __( 'Footer Client Services', 'skyyrose-flagship-2' ),
			'footer-house' => __( 'Footer House Directory', 'skyyrose-flagship-2' ),
		)
	);
}
add_action( 'after_setup_theme', 'skyyrose2_setup' );

/** Load self-hosted design system and progressive interactions. */
function skyyrose2_asset_suffix() {
	if ( defined( 'SCRIPT_DEBUG' ) && SCRIPT_DEBUG ) {
		return '';
	}

	/*
	 * Never enqueue a stale release bundle. The authored source remains the
	 * candidate authority until every core minified asset is present and newer
	 * than its source counterpart.
	 */
	$source_assets = array(
		'/assets/css/design-tokens.css' => '/assets/css/design-tokens.min.css',
		'/assets/css/theme.css'         => '/assets/css/theme.min.css',
		'/assets/js/theme.js'           => '/assets/js/theme.min.js',
	);
	foreach ( $source_assets as $source => $minified ) {
		$source_path   = SKYYROSE2_DIR . $source;
		$minified_path = SKYYROSE2_DIR . $minified;
		if ( ! file_exists( $minified_path ) || filemtime( $minified_path ) < filemtime( $source_path ) ) {
			return '';
		}
	}

	return '.min';
}

/**
 * Return a content-addressed version for a theme asset.
 *
 * A release number alone cannot invalidate a browser or edge cache when the
 * file changes between two V2 candidate builds. Hash the exact served asset so
 * an approved change always receives a new URL while unchanged files retain a
 * warm cache. The result is memoized for the duration of the request.
 *
 * @param string $relative_path Path beneath the theme directory.
 * @return string
 */
function skyyrose2_asset_version( $relative_path ) {
	static $versions = array();

	$relative_path = '/' . ltrim( (string) $relative_path, '/' );
	if ( isset( $versions[ $relative_path ] ) ) {
		return $versions[ $relative_path ];
	}

	$path = SKYYROSE2_DIR . $relative_path;
	if ( ! is_readable( $path ) ) {
		return SKYYROSE2_VERSION;
	}

	$hash = hash_file( 'sha256', $path );
	$versions[ $relative_path ] = $hash ? SKYYROSE2_VERSION . '-' . substr( $hash, 0, 12 ) : SKYYROSE2_VERSION;

	return $versions[ $relative_path ];
}

function skyyrose2_assets() {
	$suffix = skyyrose2_asset_suffix();
	$collection_slug = skyyrose2_collection_page_slug();
	$is_editorial_collection = skyyrose2_collection_world_enabled( $collection_slug );
	$tokens_asset = '/assets/css/design-tokens' . $suffix . '.css';
	$theme_asset  = '/assets/css/theme' . $suffix . '.css';
	$theme_script = '/assets/js/theme' . $suffix . '.js';
	$mascot_style = '/assets/css/mascot' . $suffix . '.css';
	$loader_script = '/assets/js/mascot-loader' . $suffix . '.js';
	$mascot_script = '/assets/js/mascot' . $suffix . '.js';
	$three_script  = '/assets/js/skyy-3d' . $suffix . '.js';

	wp_enqueue_style( 'skyyrose2-tokens', SKYYROSE2_URI . $tokens_asset, array(), skyyrose2_asset_version( $tokens_asset ) );
	wp_enqueue_style( 'skyyrose2-theme', SKYYROSE2_URI . $theme_asset, array( 'skyyrose2-tokens' ), skyyrose2_asset_version( $theme_asset ) );
	// Page composition stays off unrelated routes; controls and shell stay shared.
	$page_styles = array();
	if ( is_page( 'about' ) ) {
		$page_styles[] = 'about-archive';
		$about_script = '/assets/js/about-archive' . $suffix . '.js';
		wp_enqueue_script( 'skyyrose2-about-archive', SKYYROSE2_URI . $about_script, array(), skyyrose2_asset_version( $about_script ), true );
	}
	if ( ! is_front_page() && ! $is_editorial_collection && ! ( function_exists( 'is_product' ) && is_product() ) && ! ( function_exists( 'is_shop' ) && ( is_shop() || is_product_taxonomy() ) ) && ! ( function_exists( 'is_cart' ) && ( is_cart() || is_checkout() ) ) ) {
		$page_styles[] = 'legacy-world-components';
		$page_styles[] = 'content-page';
	}
	if ( is_front_page() ) {
		$page_styles[] = 'collection-world';
		$page_styles[] = 'home-page';
	}
	if ( function_exists( 'is_product' ) && is_product() ) {
		$page_styles[] = 'product-page';
	}
	if ( function_exists( 'is_shop' ) && ( is_shop() || is_product_taxonomy() ) ) {
		$page_styles[] = 'shop-page';
	}
	if ( $is_editorial_collection ) {
		$page_styles[] = 'collection-world';
	}
	foreach ( $page_styles as $page_style ) {
		$asset = '/assets/css/' . $page_style . $suffix . '.css';
		wp_enqueue_style( 'skyyrose2-' . $page_style, SKYYROSE2_URI . $asset, array( 'skyyrose2-theme' ), skyyrose2_asset_version( $asset ) );
	}
	foreach ( array( 'controls', 'global-shell' ) as $component ) {
		$asset = '/assets/css/' . $component . $suffix . '.css';
		wp_enqueue_style( 'skyyrose2-' . $component, SKYYROSE2_URI . $asset, array( 'skyyrose2-theme' ), skyyrose2_asset_version( $asset ) );
	}
	// Paid card framing is shared; cinematic controllers load only on their routes.
	$recovery_style = '/assets/css/visual-recovery' . $suffix . '.css';
	wp_enqueue_style( 'skyyrose2-visual-recovery', SKYYROSE2_URI . $recovery_style, array( 'skyyrose2-theme' ), skyyrose2_asset_version( $recovery_style ) );
	if ( is_front_page() || $is_editorial_collection ) {
		$recovery_script = '/assets/js/visual-recovery' . $suffix . '.js';
		// Home prints this controller inline right after the hero (inc/critical-rendering.php);
		// registering it keeps dependent handles valid without a second footer copy.
		if ( skyyrose2_hero_bootstrap_inline() ) {
			wp_register_script( 'skyyrose2-visual-recovery', false, array(), skyyrose2_asset_version( $recovery_script ), true );
		} else {
			wp_enqueue_script( 'skyyrose2-visual-recovery', SKYYROSE2_URI . $recovery_script, array(), skyyrose2_asset_version( $recovery_script ), true );
		}
		foreach ( array( 'hero-commerce-scenes', 'collection-scene-motion' ) as $scene_component ) {
			$scene_asset = '/assets/css/' . $scene_component . $suffix . '.css';
			wp_enqueue_style( 'skyyrose2-' . $scene_component, SKYYROSE2_URI . $scene_asset, array( 'skyyrose2-visual-recovery' ), skyyrose2_asset_version( $scene_asset ) );
		}
		$scene_asset = '/assets/js/collection-scene-motion' . $suffix . '.js';
		wp_enqueue_script( 'skyyrose2-collection-scene-motion', SKYYROSE2_URI . $scene_asset, array(), skyyrose2_asset_version( $scene_asset ), true );
		if ( in_array( $collection_slug, array( 'signature', 'black-rose', 'love-hurts' ), true ) ) {
			$handoff_script = '/assets/js/scene-handoff' . $suffix . '.js';
			$handoff_style  = '/assets/css/scene-handoff' . $suffix . '.css';
			wp_enqueue_script( 'skyyrose2-scene-handoff', SKYYROSE2_URI . $handoff_script, array( 'skyyrose2-visual-recovery' ), skyyrose2_asset_version( $handoff_script ), true );
			wp_enqueue_style( 'skyyrose2-scene-handoff', SKYYROSE2_URI . $handoff_style, array( 'skyyrose2-collection-world' ), skyyrose2_asset_version( $handoff_style ) );
		}
	}
	if ( class_exists( 'WooCommerce' ) && ! is_checkout() ) { wp_enqueue_script( 'wc-cart-fragments' ); }
	wp_enqueue_script( 'skyyrose2-theme', SKYYROSE2_URI . $theme_script, class_exists( 'WooCommerce' ) && ! is_checkout() ? array( 'wc-cart-fragments', 'wc-add-to-cart' ) : array(), skyyrose2_asset_version( $theme_script ), true );
	// Search previews enhance the native GET form using current server results.
	if ( ! ( function_exists( 'is_checkout' ) && is_checkout() ) ) {
		$search_script = '/assets/js/search-preview' . $suffix . '.js';
		$search_style  = '/assets/css/search-preview' . $suffix . '.css';
		wp_enqueue_script( 'skyyrose2-search-preview', SKYYROSE2_URI . $search_script, array( 'skyyrose2-theme' ), skyyrose2_asset_version( $search_script ), true );
		wp_enqueue_style( 'skyyrose2-search-preview', SKYYROSE2_URI . $search_style, array( 'skyyrose2-global-shell' ), skyyrose2_asset_version( $search_style ) );
		$premium_script = '/assets/js/premium-commerce' . $suffix . '.js';
		$premium_style  = '/assets/css/premium-commerce' . $suffix . '.css';
		wp_enqueue_script( 'skyyrose2-premium-commerce', SKYYROSE2_URI . $premium_script, array( 'skyyrose2-theme' ), skyyrose2_asset_version( $premium_script ), true );
		wp_enqueue_style( 'skyyrose2-premium-commerce', SKYYROSE2_URI . $premium_style, array( 'skyyrose2-global-shell' ), skyyrose2_asset_version( $premium_style ) );
	}
	// Reuse native variation resolution only on routes that can render cards.
	if ( class_exists( 'WooCommerce' ) && ! is_cart() && ! is_checkout() && ! is_account_page() ) {
		$purchase_script = '/assets/js/quick-view-commerce' . $suffix . '.js';
		$purchase_style  = '/assets/css/quick-view-commerce' . $suffix . '.css';
		wp_enqueue_script( 'skyyrose2-quick-view-commerce', SKYYROSE2_URI . $purchase_script, array( 'skyyrose2-theme', 'wc-add-to-cart-variation' ), skyyrose2_asset_version( $purchase_script ), true );
		wp_enqueue_style( 'skyyrose2-quick-view-commerce', SKYYROSE2_URI . $purchase_style, array( 'skyyrose2-controls' ), skyyrose2_asset_version( $purchase_style ) );
	}
	if ( ( ! $is_editorial_collection && ( $collection_slug || is_page_template( 'template-collection.php' ) ) ) || is_page_template( array( 'template-immersive-black-rose.php', 'template-immersive-love-hurts.php', 'template-immersive-signature.php' ) ) ) {
		$scene_base_style = '/assets/css/hero-commerce-scenes' . $suffix . '.css';
		$scene_style = '/assets/css/collection-scene-motion' . $suffix . '.css';
		$scene_script = '/assets/js/collection-scene-motion' . $suffix . '.js';
		wp_enqueue_style( 'skyyrose2-hero-commerce-scenes', SKYYROSE2_URI . $scene_base_style, array( 'skyyrose2-theme' ), skyyrose2_asset_version( $scene_base_style ) );
		wp_enqueue_style( 'skyyrose2-collection-scene-motion', SKYYROSE2_URI . $scene_style, array( 'skyyrose2-hero-commerce-scenes' ), skyyrose2_asset_version( $scene_style ) );
		wp_enqueue_script( 'skyyrose2-collection-scene-motion', SKYYROSE2_URI . $scene_script, array(), skyyrose2_asset_version( $scene_script ), true );
	}
	// The event-only watchdog restores approved stills if this one external
	// controller fails. WordPress's inline-script API retains the CSP nonce hook.
	if ( wp_script_is( 'skyyrose2-collection-scene-motion', 'enqueued' ) ) {
		wp_add_inline_script( 'skyyrose2-collection-scene-motion', <<<'JS'
(function () {
  var controllerId = 'skyyrose2-collection-scene-motion-js';
  function restore() {
    document.removeEventListener('load', loaded, true);
    document.removeEventListener('error', failed, true);
    if (window.skyyroseSceneMotionReady) return;
    document.querySelectorAll('[data-scene-poster]').forEach(function (poster) {
      if (poster.dataset.srcset) poster.srcset = poster.dataset.srcset;
      if (poster.dataset.src) poster.src = poster.dataset.src;
      var frame = poster.closest('.sr2-hero-commerce__frame');
      if (frame) frame.classList.remove('is-motion-ready');
    });
    document.documentElement.dataset.sceneControllerFallback = 'still';
  }
  function afterDocument() {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', restore, { once: true });
    else restore();
  }
  function loaded(event) {
    if (event.target && event.target.id === controllerId) afterDocument();
  }
  function failed(event) {
    if (event.target && event.target.id === controllerId) afterDocument();
  }
  document.addEventListener('load', loaded, true);
  document.addEventListener('error', failed, true);
})();
JS
		, 'before' );
	}
	// Editorial collection and reservation pages render native Woo loop actions
	// outside WooCommerce's archive template. Load the same client runtime here
	// so an eligible simple product gets the normal AJAX confirmation, fragments,
	// and updated bag count; the anchor URL remains the no-JS cart fallback.
	if (
		function_exists( 'is_woocommerce' ) &&
		(
			$collection_slug || is_page_template( 'template-collection.php' ) ||
			is_page_template( 'template-preorder.php' ) ||
			is_page_template( 'template-parts/v2-preorder.php' )
		)
	) {
		wp_enqueue_script( 'wc-add-to-cart' );
		wp_enqueue_script( 'wc-cart-fragments' );
	}
	if ( ! ( function_exists( 'is_checkout' ) && is_checkout() ) ) {
		wp_enqueue_style( 'skyyrose2-mascot', SKYYROSE2_URI . $mascot_style, array( 'skyyrose2-tokens' ), skyyrose2_asset_version( $mascot_style ) );
		wp_enqueue_script( 'skyyrose2-mascot-loader', SKYYROSE2_URI . $loader_script, array(), skyyrose2_asset_version( $loader_script ), true );
		wp_localize_script(
			'skyyrose2-mascot-loader',
			'SKYY_LOADER_CONFIG',
			array(
				'mascotUrl' => add_query_arg( 'ver', skyyrose2_asset_version( $mascot_script ), SKYYROSE2_URI . $mascot_script ),
				'skyy3dUrl' => add_query_arg( 'ver', skyyrose2_asset_version( $three_script ), SKYYROSE2_URI . $three_script ),
			)
		);
		wp_localize_script(
			'skyyrose2-mascot-loader',
			'SKYY_3D_CONFIG',
			array(
				'modelUrl'       => add_query_arg( 'ver', skyyrose2_asset_version( '/assets/models/skyy-natural-desktop.glb' ), SKYYROSE2_URI . '/assets/models/skyy-natural-desktop.glb' ),
				'mobileModelUrl' => add_query_arg( 'ver', skyyrose2_asset_version( '/assets/models/skyy-natural-mobile.glb' ), SKYYROSE2_URI . '/assets/models/skyy-natural-mobile.glb' ),
				'decoderPath'    => SKYYROSE2_URI . '/assets/js/lib/draco/',
				'moduleBase'     => SKYYROSE2_URI . '/assets/js/lib/three-r170/',
			)
		);
		wp_localize_script( 'skyyrose2-mascot-loader', 'SKYY_GUIDE_DATA', skyyrose2_concierge_guide() );
	}
}
add_action( 'wp_enqueue_scripts', 'skyyrose2_assets' );

/** Read-only concierge destinations and product discovery; Woo owns all sale facts. */
function skyyrose2_concierge_guide() {
	$contact = skyyrose2_marketplace_page_url( 'contact' );
	$shop = skyyrose2_shop_url();
	$guide = array(
		'greeting' => __( 'Welcome to SkyyRose. I’m Skyy, your digital house guide. This house is a father’s promise to his daughter, rooted in Oakland. I can help you explore a collection or find a piece by name or SKU.', 'skyyrose-flagship-2' ),
		'pages' => array(
			'shop' => array( 'label' => __( 'Shop the house', 'skyyrose-flagship-2' ), 'url' => $shop ),
			'contact' => array( 'label' => __( 'Contact the house', 'skyyrose-flagship-2' ), 'url' => $contact ),
		),
		'intents' => array(
			array( 'id' => 'sizing', 'patterns' => array( 'size', 'sizing', 'fit', 'measurements' ), 'answer' => __( 'Open the piece you’re considering to see its current size options and product details. If you need fit advice, contact the house with the product name or SKU.', 'skyyrose-flagship-2' ), 'link' => $contact, 'label' => __( 'Ask about fit', 'skyyrose-flagship-2' ) ),
			array( 'id' => 'shipping', 'patterns' => array( 'shipping', 'delivery', 'returns', 'order' ), 'answer' => __( 'Shipping and purchase details depend on your order. Please contact the house for help with delivery, returns or an existing order.', 'skyyrose-flagship-2' ), 'link' => $contact, 'label' => __( 'Contact the house', 'skyyrose-flagship-2' ) ),
			array( 'id' => 'legacy', 'patterns' => array( 'skyy', 'daughter', 'father', 'heir', 'story' ), 'answer' => __( 'SkyyRose is named after Skyy Rose, the founder’s daughter. The Heir carries that story forward: family, inheritance and a future built with care.', 'skyyrose-flagship-2' ), 'link' => skyyrose2_collection_url( 'kids-capsule' ), 'label' => __( 'Explore The Heir', 'skyyrose-flagship-2' ) ),
		),
		'products' => array(),
		'suggestions' => array( 'signature', 'black-rose', 'love-hurts', 'legacy', 'sizing' ),
	);
	foreach ( skyyrose2_collections() as $slug => $collection ) {
		$guide['intents'][] = array( 'id' => $slug, 'patterns' => array( $collection['name'], str_replace( '-', ' ', $slug ) ), 'answer' => $collection['headline'], 'link' => skyyrose2_collection_url( $slug ), 'label' => sprintf( __( 'Explore %s', 'skyyrose-flagship-2' ), $collection['name'] ) );
	}
	if ( function_exists( 'wc_get_products' ) ) {
		foreach ( wc_get_products( array( 'status' => 'publish', 'limit' => 100, 'orderby' => 'title', 'order' => 'ASC' ) ) as $item ) {
			if ( ! $item->is_visible() || post_password_required( $item->get_id() ) ) { continue; }
			$record = skyyrose2_product_presentation( $item );
			$guide['products'][] = array( 'name' => wp_strip_all_tags( $item->get_name() ), 'sku' => $item->get_sku(), 'url' => $item->get_permalink(), 'collection' => str_replace( '-', ' ', $record['collection'] ?? '' ) );
		}
	}
	return $guide;
}

/**
 * Supply route-aware metadata when an SEO plugin is not the active authority.
 * Core continues to own canonical URLs; WooCommerce continues to own product facts.
 */
function skyyrose2_seo_context() {
	$context = array(
		'title'       => get_bloginfo( 'name' ),
		'description' => __( 'SkyyRose is independent luxury streetwear from Oakland, California.', 'skyyrose-flagship-2' ),
		'image'       => skyyrose2_sot_asset_uri( 'branding/hero/flagship-house-runway-gpt2.webp' ),
		'type'        => 'website',
	);

	if ( is_front_page() ) {
		$context['title']       = __( 'SkyyRose', 'skyyrose-flagship-2' );
		$context['description'] = __( 'Enter SkyyRose: Oakland-rooted luxury streetwear, living collection worlds, limited pieces, and the stories behind the house.', 'skyyrose-flagship-2' );
	} elseif ( is_singular( 'product' ) && function_exists( 'wc_get_product' ) ) {
		$product = wc_get_product( get_queried_object_id() );
		if ( $product ) {
			$context['title']       = $product->get_name() . ' | ' . get_bloginfo( 'name' );
			$context['description'] = wp_strip_all_tags( $product->get_short_description() ?: $product->get_name() . ' · ' . __( 'SkyyRose collection piece.', 'skyyrose-flagship-2' ) );
			$media                 = skyyrose2_product_commerce_media( $product );
			$context['image']       = ! empty( $media['ids'] ) ? wp_get_attachment_image_url( $media['ids'][0], 'full' ) : '';
			$context['type']        = 'product';
		}
	} elseif ( is_single() ) {
		$context['title']       = get_the_title() . ' | ' . get_bloginfo( 'name' );
		$context['description'] = wp_trim_words( wp_strip_all_tags( get_the_excerpt() ?: get_the_content() ), 30, '' );
		$context['image']       = get_the_post_thumbnail_url( get_queried_object_id(), 'full' ) ?: $context['image'];
		$context['type']        = 'article';
	} elseif ( is_page() ) {
		$page_slug = sanitize_title( get_post_field( 'post_name', get_queried_object_id() ) );
		$worlds    = skyyrose2_collections();
		if ( isset( $worlds[ $page_slug ] ) ) {
			$world             = $worlds[ $page_slug ];
			$context['title']       = $world['name'] . ' | SkyyRose';
			$context['description'] = wp_strip_all_tags( $world['line'] . ' ' . $world['manifesto'] );
			$context['image']       = skyyrose2_sot_asset_uri( $world['hero'] );
		} else {
			$context['title']       = get_the_title() . ' | ' . get_bloginfo( 'name' );
			$context['description'] = wp_trim_words( wp_strip_all_tags( get_the_excerpt() ?: get_the_content() ), 30, '' ) ?: $context['description'];
			$context['image']       = get_the_post_thumbnail_url( get_queried_object_id(), 'full' ) ?: $context['image'];
		}
	} elseif ( is_search() ) {
		$context['title']       = sprintf( __( 'Search “%s” | SkyyRose', 'skyyrose-flagship-2' ), get_search_query() );
		$context['description'] = __( 'Search SkyyRose products, collections, and journal stories.', 'skyyrose-flagship-2' );
	}

	return $context;
}

function skyyrose2_seo_head() {
	if ( defined( 'WPSEO_VERSION' ) || defined( 'RANK_MATH_VERSION' ) || defined( 'THE_SEO_FRAMEWORK_VERSION' ) ) {
		return;
	}
	$context = skyyrose2_seo_context();
	if ( empty( $context['description'] ) ) {
		return;
	}
	?>
	<meta name="description" content="<?php echo esc_attr( $context['description'] ); ?>">
	<meta property="og:type" content="<?php echo esc_attr( $context['type'] ); ?>">
	<meta property="og:title" content="<?php echo esc_attr( $context['title'] ); ?>">
	<meta property="og:description" content="<?php echo esc_attr( $context['description'] ); ?>">
	<meta property="og:url" content="<?php echo esc_url( is_singular() ? get_permalink() : home_url( add_query_arg( array(), $GLOBALS['wp']->request ?? '' ) ) ); ?>">
	<?php if ( ! empty( $context['image'] ) ) : ?><meta property="og:image" content="<?php echo esc_url( $context['image'] ); ?>"><?php endif; ?>
	<meta name="twitter:card" content="<?php echo empty( $context['image'] ) ? 'summary' : 'summary_large_image'; ?>">
	<?php
}
add_action( 'wp_head', 'skyyrose2_seo_head', 4 );

/**
 * Render schema facts owned by the theme.
 *
 * WooCommerce remains the single Product-schema authority.  The theme only
 * emits editorial schema; independently rebuilding a Product entity here
 * creates duplicate offers and inventory facts on product pages.
 */
function skyyrose2_schema_head() {
	if ( defined( 'WPSEO_VERSION' ) || defined( 'RANK_MATH_VERSION' ) || defined( 'THE_SEO_FRAMEWORK_VERSION' ) ) {
		return;
	}
	$schema = array();
	if ( is_single() && ! is_singular( 'product' ) ) {
		$schema = array(
			'@context'         => 'https://schema.org',
			'@type'            => 'Article',
			'headline'         => get_the_title(),
			'datePublished'    => get_the_date( DATE_W3C ),
			'dateModified'     => get_the_modified_date( DATE_W3C ),
			'mainEntityOfPage' => get_permalink(),
			'image'            => get_the_post_thumbnail_url( get_queried_object_id(), 'full' ) ?: null,
			'author'           => array( '@type' => 'Person', 'name' => get_the_author() ),
			'publisher'        => array( '@type' => 'Organization', 'name' => get_bloginfo( 'name' ) ),
		);
	}
	if ( $schema ) {
		echo '<script type="application/ld+json">' . wp_json_encode( $schema, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE ) . '</script>';
	}
}
add_action( 'wp_head', 'skyyrose2_schema_head', 5 );

/** Keep the visible bag count synchronized with WooCommerce add-to-cart fragments. */
function skyyrose2_cart_fragment( $fragments ) {
	ob_start();
	?><span class="sr2-header__bag-count" aria-live="polite" aria-atomic="true" aria-label="<?php echo esc_attr( sprintf( __( '%d items in bag', 'skyyrose-flagship-2' ), skyyrose2_cart_count() ) ); ?>"><?php echo esc_html( skyyrose2_cart_count() ); ?></span><?php
	$fragments['.sr2-header__bag-count'] = ob_get_clean();
	return $fragments;
}
add_filter( 'woocommerce_add_to_cart_fragments', 'skyyrose2_cart_fragment' );

/** Store a one-time contact result and return its opaque browser token. */
function skyyrose2_contact_result_token( $status ) {
	$token = wp_generate_password( 24, false, false );
	set_transient( 'skyyrose2_contact_' . hash( 'sha256', $token ), sanitize_key( $status ), 5 * MINUTE_IN_SECONDS );
	return $token;
}

/** Return and consume the trusted contact result for this request. */
function skyyrose2_contact_result() {
	$token = isset( $_GET['contact_result'] ) ? sanitize_text_field( wp_unslash( $_GET['contact_result'] ) ) : '';
	if ( ! $token ) {
		return '';
	}
	$key    = 'skyyrose2_contact_' . hash( 'sha256', $token );
	$status = get_transient( $key );
	delete_transient( $key );
	return is_string( $status ) ? sanitize_key( $status ) : '';
}

/** Redirect back to Contact with a server-issued, one-time result. */
function skyyrose2_contact_redirect( $status ) {
	wp_safe_redirect(
		add_query_arg(
			'contact_result',
			rawurlencode( skyyrose2_contact_result_token( $status ) ),
			home_url( '/contact/' )
		)
	);
	exit;
}

/** Stable privacy-preserving throttle key; client-controlled headers cannot reset it. */
function skyyrose2_contact_rate_key() {
	return 'skyyrose2_contact_rate_' . hash_hmac( 'sha256', (string) ( $_SERVER['REMOTE_ADDR'] ?? '' ), wp_salt( 'nonce' ) );
}

/** Handle client-service messages without exposing raw mail endpoints. */
function skyyrose2_contact_form_submit() {
	if ( 'POST' !== ( $_SERVER['REQUEST_METHOD'] ?? '' ) || empty( $_POST['skyyrose2_contact_submit'] ) ) {
		return;
	}
	if ( ! isset( $_POST['skyyrose2_contact_nonce'] ) || ! wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST['skyyrose2_contact_nonce'] ) ), 'skyyrose2_contact' ) ) {
		wp_die( esc_html__( 'Security check failed.', 'skyyrose-flagship-2' ), '', array( 'response' => 403 ) );
	}
	if ( ! empty( $_POST['contact_website'] ) ) {
		skyyrose2_contact_redirect( 'received' );
	}
	$rate_key = skyyrose2_contact_rate_key();
	if ( get_transient( $rate_key ) ) {
		skyyrose2_contact_redirect( 'rate-limited' );
	}
	$name    = sanitize_text_field( wp_unslash( $_POST['contact_name'] ?? '' ) );
	$email   = sanitize_email( wp_unslash( $_POST['contact_email'] ?? '' ) );
	$subject = sanitize_text_field( wp_unslash( $_POST['contact_subject'] ?? 'Client inquiry' ) );
	$message = sanitize_textarea_field( wp_unslash( $_POST['contact_message'] ?? '' ) );
	$consent = ! empty( $_POST['contact_privacy'] );
	if ( ! $name || ! is_email( $email ) || ! $message || ! $consent || mb_strlen( $name ) > 120 || mb_strlen( $subject ) > 160 || mb_strlen( $message ) > 5000 ) {
		skyyrose2_contact_redirect( 'invalid' );
	}
	set_transient( $rate_key, 1, MINUTE_IN_SECONDS );
	$sent = wp_mail( get_option( 'admin_email' ), '[SkyyRose] ' . $subject, "Name: {$name}\nEmail: {$email}\n\n{$message}", array( 'Reply-To: ' . $email ) );
	skyyrose2_contact_redirect( $sent ? 'received' : 'delivery-error' );
}
add_action( 'init', 'skyyrose2_contact_form_submit' );

/**
 * Canonical collection presentation data derived from each generated SOT view.
 *
 * Product truth still comes from WooCommerce. This map owns narrative and
 * verified non-product visual assignments only.
 *
 * @return array<string,array<string,mixed>>
 */
function skyyrose2_collections() {
	return array(
		'signature'    => array(
			'name'       => __( 'Signature', 'skyyrose-flagship-2' ),
			'kicker'     => __( 'The House, Signed', 'skyyrose-flagship-2' ),
			'headline'   => __( 'The Bay is where the signature begins.', 'skyyrose-flagship-2' ),
			'line'       => __( 'A bronze signature answers the SR monogram across Golden Gate light. Oakland made the name; the water carries it forward.', 'skyyrose-flagship-2' ),
			'manifesto'  => __( 'Signature is the first promise of the house: build something worthy of a daughter, rooted in The Town, and finished with enough intention to travel far beyond it.', 'skyyrose-flagship-2' ),
			'world_heading' => __( 'Cross the water. Find the origin.', 'skyyrose-flagship-2' ),
			'world_intro' => __( 'Follow the two monuments from Golden Gate light back to Oakland—where a private mark became a house code.', 'skyyrose-flagship-2' ),
			'shop_kicker' => __( 'The Signature Edit', 'skyyrose-flagship-2' ),
			'shop_heading' => __( 'Carry the first mark forward.', 'skyyrose-flagship-2' ),
			'shop_intro' => __( 'The monument sets the mood. The clothes are gender-neutral by design: choose the shape, size, and story that feel like yours. Each published piece below holds the live product, price, and availability decision.', 'skyyrose-flagship-2' ),
			'card_story' => __( 'Oakland origin, carried without a label. The first mark is made for the person who reaches for it.', 'skyyrose-flagship-2' ),
			'hero_cta' => __( 'Shop Signature', 'skyyrose-flagship-2' ),
			'world_cta' => __( 'Cross into the story', 'skyyrose-flagship-2' ),
			'invitation_title' => __( 'Make the origin yours.', 'skyyrose-flagship-2' ),
			'invitation' => __( 'Choose the piece that carries your name with the same calm certainty.', 'skyyrose-flagship-2' ),
			'invitation_cta' => __( 'Choose Signature', 'skyyrose-flagship-2' ),
			'hero'       => 'images/hero/responsive/signature-golden-gate-monuments-v2-1440w.webp',
			'hero_tablet' => 'images/hero/responsive/signature-golden-gate-monuments-v2-1024w.webp',
			'hero_mobile' => 'images/hero/responsive/signature-golden-gate-monuments-v2-640w.webp',
			'portrait'   => 'scene-1-signature.webp',
			'portrait_source' => 'scroll-world',
			'lockup'     => 'images/lockups/signature-lockup.webp',
			'artifact'   => 'images/logos/sr-monogram-rose-gold.webp',
			'portal_statue' => array(
				'src'    => 'images/product-card-portals/signature-portal-statue-970w.webp',
				'small'  => 'images/product-card-portals/signature-portal-statue-640w.webp',
				'width'  => 970,
				'height' => 1621,
			),
			'atmosphere' => 'images/logos/rose-gold-rose.webp',
			'lookbook'   => 'images/lookbook/lb-rose-hoodie-beanie-960w.webp',
			'lookbook_mobile' => 'images/lookbook/lb-rose-hoodie-beanie-480w.webp',
			'world'      => array(
				array( 'image' => 'images/immersive/scene-signature-golden-gate.webp', 'label' => __( 'Golden Gate Salon', 'skyyrose-flagship-2' ), 'copy' => __( 'Gold light turns the bridge into a threshold: one side holds the signature, the other holds the rose.', 'skyyrose-flagship-2' ) ),
				array( 'image' => 'branding/hero/signature-golden-gate-yacht-1280w.webp', 'label' => __( 'Bay Atelier', 'skyyrose-flagship-2' ), 'copy' => __( 'The water is not a backdrop. It is the distance the house was built to cross.', 'skyyrose-flagship-2' ) ),
				array( 'image' => 'images/immersive/scene-signature-oakland-atelier-gpt2.webp', 'label' => __( 'The First Atelier', 'skyyrose-flagship-2' ), 'copy' => __( 'Back in Oakland, the polish has a source: work, faith, and the decision to make a name mean something.', 'skyyrose-flagship-2' ) ),
			),
		),
		'black-rose'   => array(
			'name'       => __( 'Black Rose', 'skyyrose-flagship-2' ),
			'kicker'     => __( 'Beauty Without Permission', 'skyyrose-flagship-2' ),
			'headline'   => __( 'Bloom under a Bay Bridge moon.', 'skyyrose-flagship-2' ),
			'line'       => __( 'The Black Rose name holds one side of the room. Its star-and-rose monument holds the other. Between them: the Bay after dark.', 'skyyrose-flagship-2' ),
			'manifesto'  => __( 'Black is not absence. It is depth, protection, and elegance with its guard up. The rose survives because it knows its own value—and never asks a shadow for permission to bloom.', 'skyyrose-flagship-2' ),
			'world_heading' => __( 'Enter after dark.', 'skyyrose-flagship-2' ),
			'world_intro' => __( 'Move from the monument room into a moonlit Oakland court, where every black surface keeps its own light.', 'skyyrose-flagship-2' ),
			'shop_kicker' => __( 'Black Rose / Night Edition', 'skyyrose-flagship-2' ),
			'shop_heading' => __( 'Wear the protection beautifully.', 'skyyrose-flagship-2' ),
			'shop_intro' => __( 'The world is the armor. These pieces are designed gender-neutral, with room for each wearer to make the silhouette their own. WooCommerce remains the authority for each current piece, its price, size, and availability.', 'skyyrose-flagship-2' ),
			'card_story' => __( 'Protection, polish, and enough room to define the fit yourself. The rose does not ask permission to take up space.', 'skyyrose-flagship-2' ),
			'hero_cta' => __( 'Shop Black Rose', 'skyyrose-flagship-2' ),
			'world_cta' => __( 'Enter the moon court', 'skyyrose-flagship-2' ),
			'invitation_title' => __( 'Keep your light protected.', 'skyyrose-flagship-2' ),
			'invitation' => __( 'Choose the piece that lets you show up fully without giving the room all of you.', 'skyyrose-flagship-2' ),
			'invitation_cta' => __( 'Choose Black Rose', 'skyyrose-flagship-2' ),
			// Founder-directed Bay Bridge two-monument salon. Lake Merritt remains an approved alternate.
			'hero'       => 'images/hero/responsive/black-rose-bay-bridge-monuments-v4-1440w.webp',
			'hero_tablet' => 'images/hero/responsive/black-rose-bay-bridge-monuments-v4-1024w.webp',
			'hero_mobile' => 'images/hero/responsive/black-rose-bay-bridge-monuments-v4-640w.webp',
			'portrait'   => 'scene-2-black-rose.webp',
			'portrait_source' => 'scroll-world',
			'lockup'     => 'images/lockups/black-rose-lockup.webp',
			'artifact'   => 'images/lockups/black-rose-star-graphic.webp',
			'portal_statue' => array(
				'src'    => 'images/product-card-portals/black-rose-portal-statue-970w.webp',
				'small'  => 'images/product-card-portals/black-rose-portal-statue-640w.webp',
				'width'  => 971,
				'height' => 1619,
			),
			'atmosphere' => 'images/logos/black-roses-cloud-cluster.webp',
			'lookbook'   => 'images/lookbook/lb-black-rose-football-960w.webp',
			'lookbook_mobile' => 'images/lookbook/lb-black-rose-football-480w.webp',
			'world'      => array(
				array( 'image' => 'scene-2-black-rose.webp', 'source' => 'scroll-world', 'label' => __( 'Forbidden Garden', 'skyyrose-flagship-2' ), 'copy' => __( 'The flower appears where it was never expected to. That is the point.', 'skyyrose-flagship-2' ) ),
				array( 'image' => 'branding/hero/forbidden-midnight-1280w.webp', 'label' => __( 'Midnight House', 'skyyrose-flagship-2' ), 'copy' => __( 'Concrete, chrome, black petals: a house built for quiet strength, not quietness.', 'skyyrose-flagship-2' ) ),
				array( 'image' => 'images/immersive/scene-black-rose-moon-court-gpt2.webp', 'label' => __( 'The Silver Moon Court', 'skyyrose-flagship-2' ), 'copy' => __( 'Under a hard moon, beauty is neither hidden nor explained. It simply holds the court.', 'skyyrose-flagship-2' ) ),
			),
		),
		'love-hurts'   => array(
			'name'       => __( 'Love Hurts', 'skyyrose-flagship-2' ),
			'kicker'     => __( 'The Beast Speaks', 'skyyrose-flagship-2' ),
			'headline'   => __( 'Every wound protects a rose.', 'skyyrose-flagship-2' ),
			'line'       => __( 'Love Hurts stands in scarlet script opposite the cracked-heart star. Down the aisle, the Beast faces the rose he could not forget.', 'skyyrose-flagship-2' ),
			'manifesto'  => __( 'Love Hurts is the part of the story told from the other side of the door: not a fairytale ending, but the distance between damage and devotion. What cracked still protects what mattered.', 'skyyrose-flagship-2' ),
			'world_heading' => __( 'Walk the aisle without looking away.', 'skyyrose-flagship-2' ),
			'world_intro' => __( 'Crimson glass, black thorns, a back-turned Beast, and one rose under glass. This is the story before the ending.', 'skyyrose-flagship-2' ),
			'shop_kicker' => __( 'Love Hurts / The Rose Remains', 'skyyrose-flagship-2' ),
			'shop_heading' => __( 'Take the mark with you.', 'skyyrose-flagship-2' ),
			'shop_intro' => __( 'The story is a frame, never a substitute for the garment. Love Hurts is gender-neutral by design—softness, armor, and fit are yours to define. Current details, sizes, prices, and availability are shown on every published piece.', 'skyyrose-flagship-2' ),
			'card_story' => __( 'Softness and armor live in the same piece. Wear the story your own way; the rose belongs to no one type of body.', 'skyyrose-flagship-2' ),
			'hero_cta' => __( 'Shop Love Hurts', 'skyyrose-flagship-2' ),
			'world_cta' => __( 'Walk the aisle', 'skyyrose-flagship-2' ),
			'invitation_title' => __( 'Keep what mattered.', 'skyyrose-flagship-2' ),
			'invitation' => __( 'Choose the piece that holds the tenderness and the edge in the same hand.', 'skyyrose-flagship-2' ),
			'invitation_cta' => __( 'Choose Love Hurts', 'skyyrose-flagship-2' ),
			// Founder-directed cathedral monuments. V1 Beauty and the Beast remains a world chapter below.
			'hero'       => 'images/hero/responsive/love-hurts-rose-aisle-monuments-v3-1440w.webp',
			'hero_tablet' => 'images/hero/responsive/love-hurts-rose-aisle-monuments-v3-1024w.webp',
			'hero_mobile' => 'images/hero/responsive/love-hurts-rose-aisle-monuments-v3-640w.webp',
			'portrait'   => 'scene-3-love-hurts.webp',
			'portrait_source' => 'scroll-world',
			'lockup'     => 'images/lockups/love-hurts-lockup.webp',
			'artifact'   => 'images/lockups/love-hurts-star-heart-graphic.webp',
			'portal_statue' => array(
				'src'    => 'images/product-card-portals/love-hurts-portal-statue-970w.webp',
				'small'  => 'images/product-card-portals/love-hurts-portal-statue-640w.webp',
				'width'  => 968,
				'height' => 1625,
			),
			'atmosphere' => 'images/logos/heart-rose-composite.webp',
			// V1's original 960px editorial frame is the visual baseline V2 must exceed.
			'lookbook'   => 'images/lookbook/lb-love-hurts-varsity-960w.webp',
			'lookbook_mobile' => 'images/lookbook/lb-love-hurts-varsity-480w.webp',
			'world'      => array(
				array( 'image' => 'images/immersive/scene-love-hurts-cathedral.webp', 'label' => __( 'Cathedral of Thorns', 'skyyrose-flagship-2' ), 'copy' => __( 'The room makes space for rage, reverence, and a red rose no one gets to touch.', 'skyyrose-flagship-2' ) ),
				array( 'image' => 'branding/hero/beauty-and-beast-1280w.webp', 'label' => __( 'The Beast’s Chamber', 'skyyrose-flagship-2' ), 'copy' => __( 'He faces the chamber with his back to us. The rose—not a throne—holds the room.', 'skyyrose-flagship-2' ) ),
				array( 'image' => 'images/immersive/scene-love-hurts-cracked-rose-gpt2.webp', 'label' => __( 'The Protected Wound', 'skyyrose-flagship-2' ), 'copy' => __( 'A cracked heart is not empty. It is evidence that something stayed worth guarding.', 'skyyrose-flagship-2' ) ),
			),
		),
		'kids-capsule' => array(
			'name'       => __( 'Kids Capsule', 'skyyrose-flagship-2' ),
			'kicker'     => __( 'The Heir', 'skyyrose-flagship-2' ),
			'headline'   => __( 'The throne is already hers.', 'skyyrose-flagship-2' ),
			'line'       => __( 'The Skyy mascot sits front and center, not waiting to inherit the house—already imagining what she will build inside it.', 'skyyrose-flagship-2' ),
			'manifesto'  => __( 'Kids Capsule is not a smaller version of the house. It is the first room built for the next generation: confidence, imagination, and enough space to picture themselves at the center of the story.', 'skyyrose-flagship-2' ),
			'world_heading' => __( 'Enter the heir’s room.', 'skyyrose-flagship-2' ),
			'world_intro' => __( 'The throne comes first. Then the playroom, the runway, and every big idea still waiting for its name.', 'skyyrose-flagship-2' ),
			'shop_kicker' => __( 'Kids Capsule / The Heir Edit', 'skyyrose-flagship-2' ),
			'shop_heading' => __( 'Dress the next chapter.', 'skyyrose-flagship-2' ),
			'shop_intro' => __( 'Explore the published Kids Capsule pieces below. Built for expression without a script, every piece makes room for play, confidence, and personality. Product pages provide the current price, availability, size, and care information.', 'skyyrose-flagship-2' ),
			'card_story' => __( 'Built for imagination before anyone hands out roles. The next chapter belongs to whoever is ready to write it.', 'skyyrose-flagship-2' ),
			'hero_cta' => __( 'Shop Kids Capsule', 'skyyrose-flagship-2' ),
			'world_cta' => __( 'Enter her world', 'skyyrose-flagship-2' ),
			'invitation_title' => __( 'Give imagination a place at the table.', 'skyyrose-flagship-2' ),
			'invitation' => __( 'Choose the piece that lets the next generation arrive as themselves—before anyone tells them to play small.', 'skyyrose-flagship-2' ),
			'invitation_cta' => __( 'Choose Kids Capsule', 'skyyrose-flagship-2' ),
			'hero'       => 'images/hero/responsive/kids-capsule-heir-throne-v3-1440w.webp',
			'hero_tablet' => 'images/hero/responsive/kids-capsule-heir-throne-v3-1024w.webp',
			'hero_mobile' => 'images/hero/responsive/kids-capsule-heir-throne-v3-640w.webp',
			'portrait'   => 'scene-4-kids-capsule.webp',
			'portrait_source' => 'scroll-world',
			'lockup'     => 'images/logos/sr-monogram-rose-gold.webp',
			'artifact'   => 'images/mascot/skyy-canonical-v2.png',
			'portal_statue' => array(
				'src'    => 'images/product-card-portals/kids-capsule-portal-statue-970w.webp',
				'small'  => 'images/product-card-portals/kids-capsule-portal-statue-640w.webp',
				'width'  => 971,
				'height' => 1619,
			),
			'atmosphere' => 'images/logos/sr-monogram-rose-gold.webp',
			// Preserve V1's full editorial frame for an honest Kids Capsule baseline.
			'lookbook'   => 'images/lookbook/lb-kid-black-rose-960w.webp',
			'lookbook_mobile' => 'images/lookbook/lb-kid-black-rose-480w.webp',
			'world'      => array(
				array( 'image' => 'images/immersive/scene-kids-capsule-playroom.webp', 'label' => __( 'After-Dark Playroom', 'skyyrose-flagship-2' ), 'copy' => __( 'A room where imagination is treated like an heirloom, not an interruption.', 'skyyrose-flagship-2' ) ),
				array( 'image' => 'images/immersive/scene-kids-capsule-runway.webp', 'label' => __( 'First Runway', 'skyyrose-flagship-2' ), 'copy' => __( 'No borrowed confidence. Just the first walk into a story that already has room for them.', 'skyyrose-flagship-2' ) ),
				array( 'image' => 'images/immersive/scene-kids-capsule-heir-runway-gpt2.webp', 'label' => __( 'The Heir’s Salon', 'skyyrose-flagship-2' ), 'copy' => __( 'The house does not hand down a script. It hands down the room to write one.', 'skyyrose-flagship-2' ) ),
			),
		),
	);
}

/**
 * Return only founder-approved, hash-verified motion for a collection hero.
 *
 * @param string $slug Collection slug.
 * @param string $responsive_hero Configured responsive hero path.
 * @return array<string,string>
 */
function skyyrose2_collection_hero_motion( $slug, $responsive_hero ) {
	static $manifest = null;
	if ( null === $manifest ) {
		$path     = SKYYROSE2_DIR . '/data/collection-hero-motion.json';
		$decoded  = is_readable( $path ) ? json_decode( file_get_contents( $path ), true ) : array(); // phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents
		$manifest = is_array( $decoded ) && 'skyyrose.v2.collection-hero-motion.v1' === ( $decoded['schema'] ?? '' ) ? $decoded : array();
	}

	$slug       = sanitize_title( $slug );
	$collection = isset( $manifest['collections'][ $slug ] ) && is_array( $manifest['collections'][ $slug ] ) ? $manifest['collections'][ $slug ] : array();
	$source     = isset( $collection['source'] ) && is_array( $collection['source'] ) ? $collection['source'] : array();
	$ai_motion  = isset( $collection['ai_motion'] ) && is_array( $collection['ai_motion'] ) ? $collection['ai_motion'] : array();
	$expected_source = preg_replace( '#^images/hero/responsive/(.+)-1440w\.webp$#', 'assets/sot/images/hero/$1.webp', (string) $responsive_hero );
	$source_file     = isset( $source['file'] ) ? (string) $source['file'] : '';
	$source_hash     = isset( $source['sha256'] ) ? (string) $source['sha256'] : '';
	$source_path     = $source_file ? SKYYROSE2_DIR . '/' . $source_file : '';
	$actual_source_hash = $source_path && is_file( $source_path ) ? hash_file( 'sha256', $source_path ) : '';
	if (
		'founder_approved' !== ( $ai_motion['status'] ?? '' ) ||
		! $expected_source ||
		! hash_equals( $expected_source, $source_file ) ||
		! $source_path ||
		! $source_hash ||
		! is_string( $actual_source_hash ) ||
		! hash_equals( $source_hash, $actual_source_hash )
	) {
		return array();
	}

	$max_bytes = isset( $manifest['runtime']['performance']['max_web_asset_bytes'] ) ? absint( $manifest['runtime']['performance']['max_web_asset_bytes'] ) : 0;
	$web       = isset( $ai_motion['web'] ) && is_array( $ai_motion['web'] ) ? $ai_motion['web'] : array();
	$approved_root = 'assets/video/collection-heroes/approved/' . $slug . '/';
	$motion        = array();
	foreach ( $web as $asset ) {
		$file = isset( $asset['file'] ) ? ltrim( (string) $asset['file'], '/' ) : '';
		$hash = isset( $asset['sha256'] ) ? (string) $asset['sha256'] : '';
		$path = $file ? SKYYROSE2_DIR . '/' . $file : '';
		$extension = strtolower( pathinfo( $file, PATHINFO_EXTENSION ) );
		$actual_hash = $path && is_file( $path ) ? hash_file( 'sha256', $path ) : '';
		if (
			! in_array( $extension, array( 'mp4', 'webm' ), true ) ||
			0 !== strpos( $file, $approved_root ) ||
			false !== strpos( $file, '..' ) ||
			! $path ||
			! $hash ||
			! is_string( $actual_hash ) ||
			! hash_equals( $hash, $actual_hash ) ||
			! $max_bytes ||
			filesize( $path ) > $max_bytes
		) {
			return array();
		}
		$motion[ $extension ] = SKYYROSE2_URI . '/' . $file;
	}

	return isset( $motion['mp4'], $motion['webm'] ) && 2 === count( $motion ) ? $motion : array();
}

/**
 * Return the canonical press corpus used by About and Journal fallbacks.
 *
 * These are source records, not invented editorial posts. A live WordPress
 * post always takes precedence in the Journal; this fallback keeps the four
 * founder-approved V1 articles discoverable on a fresh install.
 *
 * @return array<int,array<string,string>>
 */
function skyyrose2_press_features() {
	return array(
		array(
			'source'  => 'Maxim',
			'date'    => 'February 15, 2023',
			'title'   => '14 Game-Changing Entrepreneurs To Watch In 2023',
			'excerpt' => "Corey Foster is an innovative entrepreneur and artist who has created a truly unique clothing line. The Skyy Rose Collection blends fashion with streetwear, creating high quality and beautiful designs people can't help but admire.",
			'url'     => 'https://www.maxim.com/partner/14-game-changing-entrepreneurs-to-watch-in-2023/',
		),
		array(
			'source'  => 'San Francisco Post',
			'date'    => 'August 23, 2024',
			'title'   => "From Oakland's Streets to Fashion Heights",
			'excerpt' => 'The Skyy Rose Collection, a trailblazing gender-neutral clothing brand, is redefining fashion in the Bay Area and beyond. Established by Corey Foster, a single father with a dream, this Oakland-based brand embodies resilience, creativity, and the power of turning adversity into a catalyst for success.',
			'url'     => 'https://sanfranciscopost.com/the-skyy-rose-collection-from-oaklands-streets-to-fashion-heights/',
		),
		array(
			'source'  => 'Best of Best Review',
			'date'    => 'August 20, 2024',
			'title'   => 'Best Bay Area Clothing Line Award 2024',
			'excerpt' => "The Skyy Rose Collection has been honored with the prestigious Best Bay Area Clothing Line Award 2024 by Best of Best Review. This recognition underscores the brand's exceptional contribution to the fashion industry, particularly in the realm of high-end, gender-neutral clothing that transcends age and gender boundaries.",
			'url'     => 'https://bestofbestreview.com/awards/the-skyy-rose-collection-best-bay-area-clothing-line-award-2024',
		),
		array(
			'source'  => 'CEO Weekly',
			'date'    => 'October 22, 2024',
			'title'   => 'The Unyielding Journey of a Single Father and Entrepreneur',
			'excerpt' => 'Despite facing numerous setbacks, such as failed website attempts and deceitful manufacturers that promised much yet delivered little, this indomitable spirit refused to be quenched. The Skyy Rose Collection represents hope, hard work, and the relentless spirit of never giving up.',
			'url'     => 'https://ceoweekly.com/the-unyielding-journey-of-a-single-father-and-entrepreneur/',
		),
	);
}

/**
 * Build the collection monument reel shown inside the global header.
 *
 * Each founder-approved collection hero remains one continuous room containing
 * its typographic and graphic monuments. This avoids duplicating a scene to
 * simulate an unapproved eight-frame set or treating a transparent lockup as a
 * finished statue photograph.
 *
 * @return array<int,array<string,string>>
 */
function skyyrose2_header_world_frames() {
	$frames = array();
	foreach ( skyyrose2_collections() as $slug => $collection ) {
		$combined_labels = array(
			'signature'    => __( 'Signature typography and SR monogram monuments', 'skyyrose-flagship-2' ),
			'black-rose'   => __( 'Black Rose typography and star-and-rose monuments', 'skyyrose-flagship-2' ),
			'love-hurts'   => __( 'Love Hurts graffiti and cracked-heart monuments', 'skyyrose-flagship-2' ),
			'kids-capsule' => __( 'Skyy, the heir, on her throne', 'skyyrose-flagship-2' ),
		);
		$frames[] = array(
			'collection' => $slug,
			'name'       => $collection['name'],
			'label'      => isset( $combined_labels[ $slug ] ) ? $combined_labels[ $slug ] : $collection['name'],
			'image'      => skyyrose2_sot_asset_uri( $collection['hero'] ),
			'url'        => skyyrose2_collection_url( $slug ),
		);
	}
	return $frames;
}

/**
 * Resolve a theme-owned page from the imported hierarchy before falling back
 * to the documented route. This keeps runtime links aligned with the actual
 * page binding instead of assuming a hard-coded permalink shape.
 *
 * @param string $page_key Marketplace page registry key.
 * @return string
 */
function skyyrose2_marketplace_page_url( $page_key ) {
	$pages = function_exists( 'skyyrose2_marketplace_pages' ) ? skyyrose2_marketplace_pages() : array();
	$key   = sanitize_key( $page_key );
	$page  = isset( $pages[ $key ] ) && is_array( $pages[ $key ] ) ? $pages[ $key ] : array();
	$path  = ! empty( $page['path'] ) ? trim( (string) $page['path'], '/' ) : '';

	if ( $path && function_exists( 'get_page_by_path' ) ) {
		$resolved = get_page_by_path( $path, OBJECT, 'page' );
		if ( $resolved instanceof WP_Post ) {
			return get_permalink( $resolved );
		}
	}

	return $path ? home_url( '/' . $path . '/' ) : home_url( '/' );
}

/**
 * Resolve the WooCommerce shop using its configured page first. A fallback
 * remains available during initial setup before that page exists.
 *
 * @return string
 */
function skyyrose2_shop_url() {
	if ( function_exists( 'wc_get_page_permalink' ) ) {
		$url = wc_get_page_permalink( 'shop' );
		if ( is_string( $url ) && '' !== $url ) {
			return $url;
		}
	}
	return home_url( '/shop/' );
}

/** @param string $slug Collection slug. @return string */
function skyyrose2_collection_url( $slug ) {
	$slug = sanitize_title( $slug );
	if ( ! array_key_exists( $slug, skyyrose2_collections() ) ) {
		return skyyrose2_marketplace_page_url( 'collections' );
	}
	return skyyrose2_marketplace_page_url( $slug );
}

/** @return int Live cart count without assuming WooCommerce is active. */
function skyyrose2_cart_count() {
	return function_exists( 'WC' ) && WC()->cart ? WC()->cart->get_cart_contents_count() : 0;
}

/**
 * Return the product-SOT-derived V2 product-presentation registry.
 *
 * The JSON artifact is generated by scripts/build-product-presentation-registry.py
 * from data/product-sot.json plus the explicit Jersey Series supplement.
 * It intentionally contains no Woo IDs, prices, stock, or media bytes: those
 * remain live WooCommerce/SOT authorities.
 *
 * @return array<string,mixed>
 */
function skyyrose2_presentation_registry() {
	static $registry = null;
	if ( null !== $registry ) {
		return $registry;
	}

	$path = SKYYROSE2_DIR . '/data/product-presentation-registry.json';
	if ( ! is_readable( $path ) ) {
		$registry = array();
		return $registry;
	}

	$decoded  = json_decode( file_get_contents( $path ), true ); // phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents
	$registry = is_array( $decoded ) ? $decoded : array();
	return $registry;
}

/** @param WC_Product $product @return array<string,mixed> */
function skyyrose2_product_presentation( $product ) {
	$sku      = $product && method_exists( $product, 'get_sku' ) ? sanitize_key( $product->get_sku() ) : '';
	$registry = skyyrose2_presentation_registry();
	$records  = isset( $registry['products'] ) && is_array( $registry['products'] ) ? $registry['products'] : array();
	return $sku && isset( $records[ $sku ] ) && is_array( $records[ $sku ] ) ? $records[ $sku ] : array();
}

/**
 * Compare the published WooCommerce SKU surface with the presentation SOT.
 *
 * The presentation registry intentionally does not own WooCommerce facts, but
 * a missing record must be visible to an operator instead of disappearing from
 * an editorial rail without explanation. This report is admin-only and is
 * cached for the current request so storefront rendering stays fail-closed.
 *
 * @return array{missing:array<int,string>,extra:array<int,string>}
 */
function skyyrose2_registry_reconciliation_report() {
	static $report = null;
	if ( null !== $report ) {
		return $report;
	}

	$report = array(
		'missing'             => array(),
		'extra'               => array(),
		'collection_mismatch' => array(),
	);
	if ( ! function_exists( 'wc_get_products' ) ) {
		return $report;
	}

	$registry = skyyrose2_presentation_registry();
	$records  = isset( $registry['products'] ) && is_array( $registry['products'] ) ? $registry['products'] : array();
	$live     = array();
	$products = wc_get_products(
		array(
			'limit'   => -1,
			'status'  => 'publish',
			'orderby' => 'ID',
			'order'   => 'ASC',
		)
	);
	foreach ( $products as $product ) {
		if ( ! is_object( $product ) || ! method_exists( $product, 'get_sku' ) ) {
			continue;
		}
		$sku = sanitize_key( $product->get_sku() );
		if ( $sku ) {
			$live[ $sku ] = true;
			$record       = isset( $records[ $sku ] ) && is_array( $records[ $sku ] ) ? $records[ $sku ] : array();
			$expected     = ! empty( $record['collection'] ) ? sanitize_title( $record['collection'] ) : '';
			if ( $expected && function_exists( 'has_term' ) && ! has_term( $expected, 'product_cat', $product->get_id() ) ) {
				$report['collection_mismatch'][] = sprintf( '%s (registry: %s)', $sku, $expected );
			}
		}
	}

	$registry_skus = array_fill_keys( array_map( 'sanitize_key', array_keys( $records ) ), true );
	$report['missing'] = array_values( array_diff( array_keys( $live ), array_keys( $registry_skus ) ) );
	$report['extra']   = array_values( array_diff( array_keys( $registry_skus ), array_keys( $live ) ) );
	sort( $report['missing'] );
	sort( $report['extra'] );
	sort( $report['collection_mismatch'] );
	return $report;
}

/** Surface catalog drift to administrators without changing storefront output. */
function skyyrose2_registry_reconciliation_notice() {
	if ( ! is_admin() || ! current_user_can( 'manage_woocommerce' ) ) {
		return;
	}
	$report = skyyrose2_registry_reconciliation_report();
	if ( empty( $report['missing'] ) && empty( $report['extra'] ) && empty( $report['collection_mismatch'] ) ) {
		return;
	}
	$parts = array();
	if ( ! empty( $report['missing'] ) ) {
		$parts[] = sprintf( __( 'published WooCommerce SKUs missing from the V2 presentation registry: %s', 'skyyrose-flagship-2' ), implode( ', ', $report['missing'] ) );
	}
	if ( ! empty( $report['extra'] ) ) {
		$parts[] = sprintf( __( 'registry SKUs not currently published in WooCommerce: %s', 'skyyrose-flagship-2' ), implode( ', ', $report['extra'] ) );
	}
	if ( ! empty( $report['collection_mismatch'] ) ) {
		$parts[] = sprintf( __( 'products whose WooCommerce collection category disagrees with the V2 registry: %s', 'skyyrose-flagship-2' ), implode( ', ', $report['collection_mismatch'] ) );
	}
	printf( '<div class="notice notice-warning"><p><strong>%s</strong> %s</p></div>', esc_html__( 'SkyyRose V2 catalog drift detected.', 'skyyrose-flagship-2' ), esc_html( implode( ' ', $parts ) ) );
}
add_action( 'admin_notices', 'skyyrose2_registry_reconciliation_notice' );

/** @param WC_Product $product @return bool */
function skyyrose2_is_preorder_product( $product ) {
	$presentation = skyyrose2_product_presentation( $product );
	return ! empty( $presentation['is_preorder'] );
}

/**
 * Query published products for reusable marketplace sections.
 *
 * @param int    $limit Product limit.
 * @param string $collection Product category slug.
 * @param bool   $featured Featured-only query.
 * @return array<int,WC_Product>
 */
function skyyrose2_get_products( $limit = 6, $collection = '', $featured = false ) {
	if ( ! function_exists( 'wc_get_products' ) ) {
		return array();
	}
	$args = array(
		/*
		 * A narrow query can be filled by Jersey Series products before the
		 * presentation guard excludes them from the core Black Rose rail.
		 * Resolve against the full published collection, then apply the display
		 * limit after registry/presentation isolation has succeeded.
		 */
		'limit'   => -1,
		'status'  => 'publish',
		'orderby' => 'date',
		'order'   => 'DESC',
	);
	if ( $collection && 'pre-order' !== $collection ) {
		$args['category'] = array( sanitize_title( $collection ) );
	}
	if ( $featured ) {
		$args['featured'] = true;
	}
	$products = wc_get_products( $args );
	$filtered = array();
	foreach ( $products as $product ) {
		$presentation = skyyrose2_product_presentation( $product );
		if ( empty( $presentation ) ) {
			continue;
		}
		if ( $collection && 'pre-order' !== $collection && sanitize_title( $presentation['collection'] ?? '' ) !== sanitize_title( $collection ) ) {
			continue;
		}
		if ( 'pre-order' === $collection && empty( $presentation['is_preorder'] ) ) {
			continue;
		}
		if ( 'black-rose' === $collection && 'jersey-series' === ( $presentation['presentation'] ?? '' ) ) {
			continue;
		}
		$filtered[] = $product;
		if ( count( $filtered ) >= absint( $limit ) ) {
			break;
		}
	}
	return $filtered;
}

/**
 * Resolve the garment proof assigned to a Scroll World chapter.
 *
 * A chapter remains scenic, but it must also carry a real item from its own
 * collection. The product image, name, price, and availability stay WooCommerce
 * authoritative; Jersey Series remains isolated from the core Black Rose rail.
 *
 * @param string $collection Collection slug.
 * @param int    $chapter Chapter index.
 * @return WC_Product|false
 */
function skyyrose2_collection_scene_product( $collection, $chapter = 0 ) {
	$products = skyyrose2_get_products( 12, $collection );
	if ( empty( $products ) ) {
		return false;
	}
	$index = absint( $chapter ) % count( $products );
	return $products[ $index ] ?? false;
}

/**
 * Resolve a fixed product cast by exact SKU and collection membership.
 *
 * This is deliberately stricter than a product query: Royal Procession roles
 * must never swap, approximate, or inherit a product from another collection.
 * WooCommerce remains the authority for publication, visibility, price,
 * availability, variations, and the product URL.
 *
 * @param array<int,string> $skus Exact SKU identifiers in required order.
 * @param string            $required_collection Required product-category slug.
 * @return array<string,WC_Product> Products keyed by normalized SKU.
 */
function skyyrose2_get_products_by_skus( $skus, $required_collection ) {
	if ( ! function_exists( 'wc_get_product_id_by_sku' ) || ! function_exists( 'wc_get_product' ) ) {
		return array();
	}

	$required_collection = sanitize_title( $required_collection );
	$products            = array();
	foreach ( array_unique( array_map( 'sanitize_key', $skus ) ) as $sku ) {
		$product_id = absint( wc_get_product_id_by_sku( $sku ) );
		$product    = $product_id ? wc_get_product( $product_id ) : false;
		if ( ! $product || ! $product->is_visible() ) {
			continue;
		}
		if ( function_exists( 'get_post_status' ) && 'publish' !== get_post_status( $product_id ) ) {
			continue;
		}

		$collection_slugs = wp_get_post_terms( $product_id, 'product_cat', array( 'fields' => 'slugs' ) );
		if ( is_wp_error( $collection_slugs ) || ! in_array( $required_collection, $collection_slugs, true ) ) {
			continue;
		}
		$presentation = skyyrose2_product_presentation( $product );
		if ( empty( $presentation ) || sanitize_title( $presentation['collection'] ?? '' ) !== $required_collection ) {
			continue;
		}

		$resolved_sku = sanitize_key( $product->get_sku() );
		if ( $resolved_sku !== $sku ) {
			continue;
		}
		$products[ $sku ] = $product;
	}

	return $products;
}

/**
 * Render product cards with WooCommerce as product truth.
 *
 * @param int    $limit Product limit.
 * @param string $collection Category slug.
 * @param bool   $featured Featured-only query.
 */
function skyyrose2_product_cards( $limit = 6, $collection = '', $featured = false ) {
	$products = skyyrose2_get_products( $limit, $collection, $featured );
	if ( empty( $products ) && $featured ) {
		$products = skyyrose2_get_products( $limit, $collection, false );
	}
	if ( empty( $products ) ) {
		echo '<p class="sr2-empty">' . esc_html__( 'Next pieces entering the world soon.', 'skyyrose-flagship-2' ) . '</p>';
		return;
	}
	?>
	<div class="sr2-products sr2-products--prototype">
		<?php foreach ( $products as $index => $product ) : ?>
			<?php skyyrose2_render_product_loop_card( $product, $index ); ?>
		<?php endforeach; ?>
	</div>
	<?php
}

/**
 * Return the declared collection-world frames used by an individual product
 * reel. The frames are environment/art direction only; WooCommerce product
 * media remains the garment proof and transaction authority.
 *
 * @param array<string,mixed>|null $collection_data Current collection data.
 * @return array<int,array<string,string>>
 */
function skyyrose2_product_card_reel_frames( $collection_data ) {
	if ( empty( $collection_data['world'] ) || ! is_array( $collection_data['world'] ) ) {
		return array();
	}

	$frames = array();
	foreach ( array_slice( $collection_data['world'], 0, 3 ) as $scene ) {
		$uri = skyyrose2_collection_scene_uri( $scene );
		if ( ! $uri ) {
			continue;
		}
		$frames[] = array(
			'uri'   => $uri,
			'label' => isset( $scene['label'] ) ? $scene['label'] : '',
			'copy'  => isset( $scene['copy'] ) ? $scene['copy'] : '',
		);
	}
	return $frames;
}

/**
 * Return WooCommerce gallery IDs that are safe to treat as garment views.
 *
 * The preview harness can attach a collection scene as a secondary fixture so
 * the editorial backdrop remains visible. It is never a product view. Live
 * WooCommerce galleries remain authoritative; this narrow path guard only
 * prevents known scene/branding buckets from entering the product reel.
 *
 * @param WC_Product $product Current WooCommerce product.
 * @return array<int,int>
 */
function skyyrose2_product_view_image_ids( $product ) {
	if ( ! $product || ! is_a( $product, 'WC_Product' ) ) {
		return array();
	}

	$ids = array();
	if ( method_exists( $product, 'get_image_id' ) ) {
		$ids[] = absint( $product->get_image_id() );
	}
	if ( method_exists( $product, 'get_gallery_image_ids' ) ) {
		$ids = array_merge( $ids, array_map( 'absint', (array) $product->get_gallery_image_ids() ) );
	}

	$ids = array_values( array_unique( array_filter( $ids ) ) );
	$primary = $ids ? array_shift( $ids ) : 0;
	$views   = $primary ? array( $primary ) : array();
	foreach ( $ids as $id ) {
		$url = function_exists( 'wp_get_attachment_url' ) ? (string) wp_get_attachment_url( $id ) : '';
		if ( ! $url || preg_match( '#/(?:scene|hero|immersive|branding|scroll-world)(?:/|[-_])#i', $url ) ) {
			continue;
		}
		$views[] = $id;
	}

	return array_slice( array_values( array_unique( $views ) ), 0, 3 );
}

/**
 * Load the approved, collection-owned opening product-media manifest.
 *
 * The manifest is deliberately separate from the presentation registry: it
 * attests to visual roles, while WooCommerce remains the authority for the
 * attachment IDs attached to a live product. A card can only use an image
 * when both sources agree.
 *
 * @return array<string,mixed>
 */
function skyyrose2_product_card_media_manifest() {
	static $manifest = null;
	if ( null !== $manifest ) {
		return $manifest;
	}

	$path = SKYYROSE2_DIR . '/data/opening-product-media.json';
	if ( ! is_readable( $path ) ) {
		$manifest = array();
		return $manifest;
	}

	$decoded  = json_decode( file_get_contents( $path ), true ); // phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents
	$manifest = is_array( $decoded ) ? $decoded : array();
	$registry = skyyrose2_presentation_registry();
	if ( ! skyyrose2_validate_product_card_media_contract( $manifest, $registry ) ) {
		$manifest = array();
	}
	return $manifest;
}

/**
 * Return only attachment IDs that are both in the product gallery and named
 * in the approved SOT media manifest, ordered for a portal card.
 *
 * Product cards must lead with an on-model front view. Falling back to a
 * WooCommerce thumbnail, a collection scene, or a generic placeholder makes
 * a product look approved when its garment proof is not. If the on-model
 * proof cannot be reconciled, this intentionally returns an empty array.
 *
 * @param WC_Product $product Current WooCommerce product.
 * @return array<int,array{id:int,role:string}>
 */
function skyyrose2_product_verified_card_media( $product ) {
	if ( ! $product || ! is_a( $product, 'WC_Product' ) ) {
		return array();
	}

	$sku      = method_exists( $product, 'get_sku' ) ? sanitize_key( $product->get_sku() ) : '';
	$manifest = skyyrose2_product_card_media_manifest();
	$records  = isset( $manifest['products'] ) && is_array( $manifest['products'] ) ? $manifest['products'] : array();
	$record   = $sku && isset( $records[ $sku ] ) && is_array( $records[ $sku ] ) ? $records[ $sku ] : array();
	$views    = isset( $record['views'] ) && is_array( $record['views'] ) ? $record['views'] : array();
	if ( empty( $views ) || ! function_exists( 'wp_get_attachment_url' ) ) {
		return array();
	}

	$attachment_ids = array();
	if ( method_exists( $product, 'get_image_id' ) ) {
		$attachment_ids[] = absint( $product->get_image_id() );
	}
	if ( method_exists( $product, 'get_gallery_image_ids' ) ) {
		$attachment_ids = array_merge( $attachment_ids, array_map( 'absint', (array) $product->get_gallery_image_ids() ) );
	}
	$attachment_ids = array_values( array_unique( array_filter( $attachment_ids ) ) );
	if ( empty( $attachment_ids ) ) {
		return array();
	}

	$attachment_paths = array();
	foreach ( $attachment_ids as $attachment_id ) {
		$url  = (string) wp_get_attachment_url( $attachment_id );
		$path = (string) parse_url( $url, PHP_URL_PATH );
		if ( $path ) {
			$attachment_paths[ $attachment_id ] = basename( $path );
		}
	}

	$allowed_roles = array( 'on_model_front', 'on_model_back', 'mannequin_front', 'mannequin_back', 'render_3d', 'packshot' );
	$matched       = array();
	foreach ( $views as $view ) {
		$role = isset( $view['role'] ) ? strtolower( (string) $view['role'] ) : '';
		$role = preg_replace( '/[^a-z0-9_]/', '', $role );
		if ( ! in_array( $role, $allowed_roles, true ) || isset( $matched[ $role ] ) ) {
			continue;
		}

		$expected_paths = array_filter(
			array(
				isset( $view['source'] ) ? (string) $view['source'] : '',
				isset( $view['derivative'] ) ? (string) $view['derivative'] : '',
			)
		);
		$expected_files = array_map( 'basename', $expected_paths );
		foreach ( $attachment_paths as $attachment_id => $attachment_file ) {
			if ( in_array( $attachment_file, $expected_files, true ) ) {
				$matched[ $role ] = array(
					'id'   => (int) $attachment_id,
					'role' => $role,
				);
				break;
			}
		}
	}

	if ( empty( $matched['on_model_front'] ) ) {
		return array();
	}

	$ordered_roles = array( 'on_model_front', 'on_model_back', 'mannequin_front', 'mannequin_back', 'render_3d', 'packshot' );
	$ordered       = array();
	$used_ids      = array();
	foreach ( $ordered_roles as $role ) {
		if ( empty( $matched[ $role ] ) || isset( $used_ids[ $matched[ $role ]['id'] ] ) ) {
			continue;
		}
		$ordered[]                           = $matched[ $role ];
		$used_ids[ $matched[ $role ]['id'] ] = true;
	}

	return array_slice( $ordered, 0, 3 );
}

/** Resolve PDP commerce attachments without promoting opening-media states. */
function skyyrose2_product_commerce_media( $product ) {
	$empty = array( 'state' => 'missing', 'ids' => array() );
	if ( ! $product || ! is_a( $product, 'WC_Product' ) ) {
		return $empty;
	}
	$manifest = skyyrose2_product_card_media_manifest();
	if ( empty( $manifest['products'] ) ) {
		return $empty;
	}
	$sku = sanitize_key( $product->get_sku() );
	$record = $manifest['products'][ $sku ] ?? array();
	// A Woo assignment is not permission to reuse explicitly rejected imagery.
	if ( 'REJECTED_AUTHENTICITY' === ( $record['status'] ?? '' ) ) {
		return array( 'state' => 'rejected', 'ids' => array() );
	}
	$editorial = skyyrose2_product_verified_card_media( $product );
	$valid = static function ( $id ) {
		$metadata = $id ? wp_get_attachment_metadata( $id ) : array();
		return $id && wp_attachment_is_image( $id ) && wp_get_attachment_url( $id ) && ! empty( $metadata['width'] ) && ! empty( $metadata['height'] );
	};
	$editorial_ids = array_values( array_unique( array_filter( array_map( 'absint', array_column( $editorial, 'id' ) ), $valid ) ) );
	if ( $editorial_ids ) {
		return array( 'state' => 'editorial', 'ids' => $editorial_ids );
	}
	$ids = array_merge( array( $product->get_image_id() ), $product->get_gallery_image_ids() );
	$ids = array_values( array_unique( array_filter( array_map( 'absint', $ids ), $valid ) ) );
	return array( 'state' => $ids ? 'commerce' : 'missing', 'ids' => $ids );
}

/** Keep Product schema imagery aligned with the PDP's permitted primary. */
function skyyrose2_product_commerce_schema_image( $markup, $product ) {
	$media = skyyrose2_product_commerce_media( $product );
	if ( $media['ids'] ) {
		$markup['image'] = wp_get_attachment_url( $media['ids'][0] );
	} else {
		unset( $markup['image'] );
	}
	return $markup;
}
add_filter( 'woocommerce_structured_data_product', 'skyyrose2_product_commerce_schema_image', 30, 2 );

/** Do not reintroduce rejected PDP imagery through a variation's image update. */
function skyyrose2_product_commerce_variation_image( $data, $product, $variation ) {
	$media = skyyrose2_product_commerce_media( $product );
	if ( 'rejected' === $media['state'] ) {
		$data['image'] = array();
		$data['image_id'] = 0;
		$data['gallery_image_ids'] = array();
		$data['gallery_images_html'] = '';
	}
	return $data;
}
add_filter( 'woocommerce_available_variation', 'skyyrose2_product_commerce_variation_image', 30, 3 );

/**
 * Render the shared, collection-aware WooCommerce loop card.
 *
 * @param WC_Product $product Current WooCommerce product.
 * @param int        $index Product loop position.
 */
function skyyrose2_render_product_loop_card( $product, $index = 0 ) {
	if ( ! $product || ! is_a( $product, 'WC_Product' ) || ! $product->is_visible() ) {
		return;
	}

	get_template_part(
		'template-parts/commerce/product-card',
		null,
		array(
			'product' => $product,
			'index'   => max( 0, (int) $index ),
		)
	);
}

/**
 * Render the numbered Jersey Series as its own house chapter.
 *
 * The visual reveal is editorial; all names, media, prices and availability
 * continue to resolve from the current WooCommerce products.
 */
function skyyrose2_render_black_rose_jersey_series( $show_product_grid = true ) {
	if ( ! function_exists( 'wc_get_product' ) || ! function_exists( 'wc_get_product_id_by_sku' ) ) {
		return;
	}

	$registry = skyyrose2_presentation_registry();
	$series   = isset( $registry['products'] ) && is_array( $registry['products'] ) ? $registry['products'] : array();
	$pieces = array();

	foreach ( $series as $sku => $chapter_data ) {
		if ( 'jersey-series' !== ( $chapter_data['presentation'] ?? '' ) ) {
			continue;
		}
		$product_id = wc_get_product_id_by_sku( $sku );
		$product    = $product_id ? wc_get_product( $product_id ) : false;
		if ( $product ) {
			$pieces[] = array(
				'sku'     => $sku,
				'chapter' => $product->get_name(),
				'order'   => absint( $chapter_data['series_order'] ?? 0 ),
				'product' => $product,
			);
		}
	}

	if ( empty( $pieces ) ) {
		return;
	}

	usort(
		$pieces,
		static function ( $first, $second ) {
			return $first['order'] <=> $second['order'];
		}
	);
	?>
	<section class="sr2-jersey-reveal" aria-labelledby="sr2-jersey-series-title" data-presentation="jersey-series">
		<div class="sr2-jersey-reveal__head">
			<p class="sr2-eyebrow"><?php esc_html_e( 'Jersey Series / The Town Line', 'skyyrose-flagship-2' ); ?></p>
			<h2 id="sr2-jersey-series-title"><?php esc_html_e( 'Every number carries the tour.', 'skyyrose-flagship-2' ); ?></h2>
			<p><?php esc_html_e( 'Oakland is the origin. San Francisco, The Bay, and San Jose become chapters on The Town Line: SkyyRose’s fictional house journey. Every price, size, and availability decision stays on the live product page.', 'skyyrose-flagship-2' ); ?></p>
		</div>
		<div class="sr2-house-film" data-house-film data-house-film-scroll-world data-scroll-world-pinned data-media-status="founder-review-candidate">
			<div class="sr2-house-film__stage" data-scroll-world-stage>
				<div class="sr2-house-film__media">
				<video width="1672" height="941" muted playsinline preload="none" poster="<?php echo esc_url( SKYYROSE2_URI . '/assets/sot/images/hero/jersey-series-town-line-train-v1.webp' ); ?>" data-house-film-video aria-label="<?php esc_attr_e( 'The Town Line Jersey Series previsualization', 'skyyrose-flagship-2' ); ?>">
					<source data-src="<?php echo esc_url( SKYYROSE2_URI . '/assets/video/skyyrose-tour-around-the-bay.webm' ); ?>" type="video/webm">
					<source data-src="<?php echo esc_url( SKYYROSE2_URI . '/assets/video/skyyrose-tour-around-the-bay.mp4' ); ?>" type="video/mp4">
				</video>
				<div class="sr2-house-film__controls">
					<button type="button" data-house-film-toggle><?php esc_html_e( 'Play film', 'skyyrose-flagship-2' ); ?></button>
					<button type="button" data-house-film-sound hidden><?php esc_html_e( 'Turn sound on', 'skyyrose-flagship-2' ); ?></button>
					<span class="screen-reader-text" aria-live="polite" data-house-film-status></span>
				</div>
				</div>
				<nav class="sr2-house-film__chapters" aria-label="<?php esc_attr_e( 'Jersey Series film chapters', 'skyyrose-flagship-2' ); ?>">
					<?php foreach ( $pieces as $piece_index => $piece ) : ?>
						<a href="<?php echo esc_url( get_permalink( $piece['product']->get_id() ) ); ?>" data-house-film-chapter data-start="<?php echo esc_attr( (string) ( $piece_index * 2.6 ) ); ?>"><span><?php echo esc_html( strtoupper( $piece['sku'] ) ); ?></span><strong><?php echo esc_html( $piece['chapter'] ); ?></strong></a>
					<?php endforeach; ?>
				</nav>
			</div>
			<p class="sr2-house-film__transcript"><?php esc_html_e( 'Visual transcript: a fictional SkyyRose Town Line train moves through Oakland’s Black, White, and two Last Oakland jerseys; San Francisco’s football, Giants, and basketball looks; then San Jose hockey. This previsualization is not product-media approval.', 'skyyrose-flagship-2' ); ?></p>
		</div>
		<?php if ( $show_product_grid ) : ?>
			<div class="sr2-jersey-reveal__grid">
				<?php foreach ( $pieces as $piece_index => $piece ) : ?>
					<?php skyyrose2_render_product_loop_card( $piece['product'], $piece_index ); ?>
				<?php endforeach; ?>
		</div>
		<?php endif; ?>
	</section>
	<?php
}

/** Render collection runway with accessible native horizontal scroll. */
function skyyrose2_render_collection_rail() {
	$collections = skyyrose2_collections();
	?>
	<section class="sr2-worlds" aria-labelledby="sr2-worlds-title" data-horizontal-world>
		<header class="sr2-section-head sr2-section-head--split">
			<div><p><?php esc_html_e( 'Choose Your World', 'skyyrose-flagship-2' ); ?></p><h2 id="sr2-worlds-title"><?php esc_html_e( 'Four stories. One house.', 'skyyrose-flagship-2' ); ?></h2></div>
			<div class="sr2-rail-controls"><button type="button" data-rail-prev aria-label="<?php esc_attr_e( 'Previous collection', 'skyyrose-flagship-2' ); ?>">←</button><span data-rail-count>01 / 04</span><button type="button" data-rail-next aria-label="<?php esc_attr_e( 'Next collection', 'skyyrose-flagship-2' ); ?>">→</button></div>
		</header>
		<div class="sr2-worlds__stage" data-scroll-world-stage>
		<div class="sr2-worlds__rail" tabindex="0" aria-label="<?php esc_attr_e( 'Collection worlds. Scroll horizontally.', 'skyyrose-flagship-2' ); ?>" data-horizontal-rail>
			<?php foreach ( $collections as $index => $collection ) : ?>
				<?php
				if ( isset( $collection['portrait_source'] ) && 'scroll-world' === $collection['portrait_source'] ) {
					$portrait_uri = skyyrose2_scroll_world_asset_uri( $collection['portrait'] );
				} else {
					$portrait_uri = skyyrose2_sot_asset_uri( $collection['portrait'] );
				}
				?>
				<a class="sr2-world" data-collection="<?php echo esc_attr( $index ); ?>" href="<?php echo esc_url( skyyrose2_collection_url( $index ) ); ?>">
					<img src="<?php echo esc_url( $portrait_uri ); ?>" alt="" width="1920" height="1275" loading="<?php echo 0 === array_search( $index, array_keys( $collections ), true ) ? 'eager' : 'lazy'; ?>" decoding="async">
					<span class="sr2-world__shade" aria-hidden="true"></span>
					<span class="sr2-world__copy"><small><?php echo esc_html( sprintf( '%02d · %s', array_search( $index, array_keys( $collections ), true ) + 1, $collection['kicker'] ) ); ?></small><strong><?php echo esc_html( $collection['name'] ); ?></strong><em><?php echo esc_html( $collection['line'] ); ?></em><b><?php esc_html_e( 'Enter world', 'skyyrose-flagship-2' ); ?> <span aria-hidden="true">↗</span></b></span>
				</a>
			<?php endforeach; ?>
		</div>
		<div class="sr2-rail-progress" aria-hidden="true"><span data-rail-progress></span></div>
		</div>
	</section>
	<?php
}

/** Explicit rollout boundary shared by template and asset consumers. */
function skyyrose2_collection_world_enabled( $slug ) {
	return in_array( $slug, array( 'signature', 'black-rose', 'love-hurts', 'kids-capsule' ), true );
}

/** Matching responsive delivery for the static collection arrival and its preload. */
function skyyrose2_collection_arrival_media( $collection ) {
	return array(
		'src' => skyyrose2_sot_asset_uri( $collection['hero'] ),
		'srcset' => implode( ', ', array( skyyrose2_sot_asset_uri( $collection['hero_mobile'] ) . ' 640w', skyyrose2_sot_asset_uri( $collection['hero_tablet'] ) . ' 1024w', skyyrose2_sot_asset_uri( $collection['hero'] ) . ' 1440w' ) ),
		'sizes' => '100vw',
	);
}

/** One exact collection-route predicate shared by templates and asset delivery. */
function skyyrose2_collection_page_slug() {
	if ( ! is_page() ) {
		return '';
	}
	$id = get_queried_object_id();
	$slug = sanitize_title( get_post_field( 'post_name', $id ) );
	if ( ! array_key_exists( $slug, skyyrose2_collections() ) ) {
		return '';
	}
	if ( is_page_template( 'template-collection.php' ) ) {
		return $slug;
	}
	return function_exists( 'get_page_uri' ) && 'collections/' . $slug === trim( (string) get_page_uri( $id ), '/' ) ? $slug : '';
}

/** Route collection child pages without manual template assignment. */
function skyyrose2_collection_template( $template ) {
	if ( skyyrose2_collection_page_slug() ) {
		$collection_template = SKYYROSE2_DIR . '/template-collection.php';
		if ( file_exists( $collection_template ) ) {
			return $collection_template;
		}
	}
	return $template;
}
add_filter( 'template_include', 'skyyrose2_collection_template', 20 );

/** Keep custom Woo wrappers structurally clean. */
function skyyrose2_woocommerce_wrappers() {
	remove_action( 'woocommerce_before_main_content', 'woocommerce_output_content_wrapper', 10 );
	remove_action( 'woocommerce_after_main_content', 'woocommerce_output_content_wrapper_end', 10 );
}
add_action( 'wp', 'skyyrose2_woocommerce_wrappers' );

/** Exact-SKU fallback used by the approved editorial card renderer. */
function skyyrose2_product_media_fallback( $product ) {
	if ( ! $product || ! is_a( $product, 'WC_Product' ) || ! method_exists( $product, 'get_sku' ) ) {
		return array();
	}

	$fallbacks = array(
		'kids-001' => array( 'path' => 'images/products/kids-001-product-proof-400.webp', 'width' => 400, 'height' => 600 ),
		'kids-002' => array( 'path' => 'images/products/kids-002-product-proof-400.webp', 'width' => 400, 'height' => 400 ),
	);
	$sku       = sanitize_key( $product->get_sku() );
	$fallback  = $fallbacks[ $sku ] ?? null;
	if ( ! is_array( $fallback ) || empty( $fallback['path'] ) || ! file_exists( SKYYROSE2_DIR . '/assets/sot/' . $fallback['path'] ) ) {
		return array();
	}

	return array(
		'src'    => skyyrose2_sot_asset_uri( $fallback['path'] ),
		'width'  => (int) $fallback['width'],
		'height' => (int) $fallback['height'],
		'alt'    => $product->get_name(),
	);
}


/** Bound native public search while retaining WordPress pagination and filters. */
function skyyrose2_bound_search_query( $query ) {
	if ( is_admin() || ! $query->is_main_query() || ! $query->is_search() ) {
		return;
	}
	$query->set( 'posts_per_page', 24 );
	if ( ! $query->get( 'post_type' ) ) {
		$query->set( 'post_type', array( 'product', 'post', 'page' ) );
	}
}
add_action( 'pre_get_posts', 'skyyrose2_bound_search_query' );

/** Each native result belongs to exactly one public content group. */
function skyyrose2_search_result_group( $type, $slug ) {
	if ( 'product' === $type ) {
		return 'products';
	}
	if ( 'post' === $type ) {
		return 'stories';
	}
	if ( 'page' === $type ) {
		return array_key_exists( $slug, skyyrose2_collections() ) ? 'collections' : 'pages';
	}
	return '';
}
