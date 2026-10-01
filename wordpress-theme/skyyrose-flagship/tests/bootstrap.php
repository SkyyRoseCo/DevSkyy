<?php
/**
 * PHPUnit bootstrap — WordPress theme unit tests.
 *
 * Defines the minimal constants required by the theme's ABSPATH guard and
 * loads WP function stubs + the three testable inc/ modules.
 *
 * @package SkyyRose
 */

// Theme root (one directory above tests/).
define( 'ABSPATH', dirname( __DIR__ ) . '/' ); // phpcs:ignore WordPress.NamingConventions.PrefixAllGlobals.NonPrefixedConstantFound -- WP core constant stub required by theme ABSPATH guards.
define( 'SKYYROSE_DIR', dirname( __DIR__ ) );
define( 'SKYYROSE_VERSION', '1.1.1' );
define( 'SKYYROSE_ASSETS_URI', 'https://theme.test/assets' );

require_once __DIR__ . '/stubs/wp-stubs.php';

// This is an isolated unit harness, not a WordPress integration bootstrap.
// Fail with a diagnostic instead of risking fatal redeclarations if a runner
// preloads WooCommerce before these deliberately API-shaped test doubles.
if ( class_exists( 'WC_Product', false ) || function_exists( 'wc_get_product' ) ) {
	throw new RuntimeException( 'WooCommerce must not be preloaded for the isolated theme unit suite.' );
}
require_once __DIR__ . '/stubs/woocommerce-stubs.php';

require_once SKYYROSE_DIR . '/inc/brand-colors.php';
require_once SKYYROSE_DIR . '/inc/collections-config.php';
require_once SKYYROSE_DIR . '/inc/product-catalog.php';
require_once SKYYROSE_DIR . '/inc/product-catalog-display.php';
require_once SKYYROSE_DIR . '/inc/performance.php';
require_once SKYYROSE_DIR . '/inc/performance-cli.php';
require_once SKYYROSE_DIR . '/inc/woocommerce-preorder.php';
