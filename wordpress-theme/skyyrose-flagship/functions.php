<?php
/**
 * SkyyRose Theme Functions
 *
 * Main bootstrap file. Defines theme constants and loads modular inc/ files.
 * All heavy logic is delegated to individual inc/ modules for maintainability.
 *
 * @package SkyyRose
 * @since   1.0.0
 */

// Prevent direct access.
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/*
--------------------------------------------------------------
 * Theme Constants
 *--------------------------------------------------------------*/
define( 'SKYYROSE_VERSION', '2.2.4' );
define( 'SKYYROSE_DIR', get_template_directory() );
define( 'SKYYROSE_URI', get_template_directory_uri() );

// Legacy aliases for backward compatibility with existing templates.
define( 'SKYYROSE_THEME_DIR', SKYYROSE_DIR );
define( 'SKYYROSE_THEME_URI', SKYYROSE_URI );
define( 'SKYYROSE_ASSETS_URI', SKYYROSE_URI . '/assets' );

/*
--------------------------------------------------------------
 * Coming-Soon (Veil) Mode
 *
 * When true, inc/maintenance.php routes every public request to
 * template-coming-soon.php and responds HTTP 503. Logged-in editors
 * + admin + AJAX + REST + assets bypass automatically. Flip to false
 * and redeploy to lift the veil.
 *--------------------------------------------------------------*/
if ( ! defined( 'SKYYROSE_COMING_SOON_MODE' ) ) {
	define( 'SKYYROSE_COMING_SOON_MODE', false );
}

/*
--------------------------------------------------------------
 * Disable WordPress.com CSS/JS Concatenation
 *
 * WordPress.com's concatenation service (_jb_static) can cause
 * MIME type errors and 404s. Disable it to serve files directly.
 *--------------------------------------------------------------*/
if ( ! defined( 'CONCATENATE_SCRIPTS' ) ) {
	define( 'CONCATENATE_SCRIPTS', false ); // phpcs:ignore WordPress.NamingConventions.PrefixAllGlobals.NonPrefixedConstantFound -- WP core constant.
}
$GLOBALS['concatenate_scripts'] = false;

/*
--------------------------------------------------------------
 * Core Includes (always loaded)
 *--------------------------------------------------------------*/
$skyyrose_core_includes = array(
	// SoT constants generated from assets/brand/brand.yaml — load FIRST so every
	// downstream include can reference SKYYROSE_BRAND_TAGLINE, SKYYROSE_COLOR_*,
	// skyyrose_brand_collections(), skyyrose_json_ld_organization(), etc.
	'/inc/brand.generated.php',
	'/inc/redirects.php',
	'/inc/theme-setup.php',
	'/inc/brand-colors.php',
	'/inc/collections-config.php',
	// Hook-free 3D model URL policy + viewer enqueue; consumed by
	// enqueue-templates.php and (when WooCommerce is active) woocommerce.php.
	'/inc/product-3d-model.php',
	'/inc/enqueue.php',
	'/inc/enqueue-templates.php',
	'/inc/enqueue-performance.php',
	'/inc/enqueue-phases.php',
	'/inc/customizer.php',
	'/inc/mascot-config.php',
	'/inc/template-functions.php',
	'/inc/storefront-data.php',
	'/inc/page-upgrades.php',
	'/inc/security.php',
	'/inc/accessibility-fix.php',
	'/inc/accessibility-seo.php',
	'/inc/seo.php',
	'/inc/ajax-handlers.php',
	'/inc/collection-content.php',
	'/inc/collection-sot-reader.php',
	'/inc/experience-rooms.php',
	'/inc/collections-world.php',
	'/inc/product-catalog.php',
	// Homepage v3 act data — depends on collections-config, collections-world
	// and product-catalog above, so it loads after all three.
	'/inc/homepage-data.php',
	'/inc/product-catalog-display.php',
	'/inc/v7-cards.php',
	'/inc/immersive-product-adapter.php',
	'/inc/product-taxonomy.php',
	'/inc/facebook-sdk.php',
	'/inc/maintenance.php',
	'/inc/menu-setup.php',
	'/inc/theme-activation-setup.php',
	'/inc/klaviyo-integration.php',
	'/inc/experience-engine.php',
	'/inc/fastapi-client.php',
	'/inc/mcp-bridge.php',
	'/inc/rest-api-experience.php',
	'/inc/personalization.php',
	'/inc/performance-guardian.php',
	'/inc/image-placements.php',
	'/inc/performance.php',
	'/inc/performance-cli.php',
	'/inc/patterns.php',
	'/inc/fashion-chrome.php',
	'/inc/marketplace-compat.php',
	// Customer enhancements: fit notes metabox, drop block customizer, sticky ATC helper.
	// Loaded in core (not WC-only) so the Customizer section registers on all pages.
	'/inc/customer-enhancements.php',
);

foreach ( $skyyrose_core_includes as $skyyrose_file ) {
	$skyyrose_filepath = SKYYROSE_DIR . $skyyrose_file;
	if ( file_exists( $skyyrose_filepath ) ) {
		require_once $skyyrose_filepath;
	}
}

/*
--------------------------------------------------------------
 * WooCommerce Includes (loaded only when WooCommerce is active)
 *--------------------------------------------------------------*/
if ( class_exists( 'WooCommerce' ) ) {
	$skyyrose_woo_includes = array(
		'/inc/woocommerce.php',
		'/inc/woocommerce-preorder.php',
		'/inc/skyyrose-product-meta.php',
		'/inc/wc-product-functions.php',
		'/inc/immersive-ajax.php',
		'/inc/wishlist-functions.php',
		'/inc/class-wishlist-widget.php',
		'/inc/experience-analyzer.php',
		'/inc/woocommerce-kids-capsule.php',
		'/inc/rest-kids-capsule.php',
	);

	foreach ( $skyyrose_woo_includes as $skyyrose_file ) {
		$skyyrose_filepath = SKYYROSE_DIR . $skyyrose_file;
		if ( file_exists( $skyyrose_filepath ) ) {
			require_once $skyyrose_filepath;
		}
	}
}

/*
--------------------------------------------------------------
 * Page Builder Includes
 *--------------------------------------------------------------*/
require_once SKYYROSE_DIR . '/inc/builders/detection.php';
require_once SKYYROSE_DIR . '/inc/builders/shared.php';

// Elementor — preserve same hook timing as the original loading.
add_action(
	'elementor/loaded',
	function () {
		$files = array(
			'/inc/builders/elementor.php',
			'/inc/builders/elementor-compat.php',
		);
		foreach ( $files as $file ) {
			$path = SKYYROSE_DIR . $file;
			if ( file_exists( $path ) ) {
				require_once $path;
			}
		}
	}
);

// Divi, Beaver Builder, Bricks — self-guarded stubs.
$skyyrose_builder_stubs = array(
	'/inc/builders/divi.php',
	'/inc/builders/beaver-builder.php',
	'/inc/builders/bricks.php',
);
foreach ( $skyyrose_builder_stubs as $skyyrose_stub ) {
	$path = SKYYROSE_DIR . $skyyrose_stub;
	if ( file_exists( $path ) ) {
		require_once $path;
	}
}

/* Admin includes and brand styles removed in v5.2.0 — dead code cleanup. */

/* Mascot reinstated in v1.9.0 — Skyy 3D character host (inc/mascot-config.php). */
