<?php
/** Guarded size-conversion entry; production conversion is not supported. */
$config = $skyyrose_migration ?? array();
$fixture = defined( 'WP_CLI' ) && WP_CLI && defined( 'SKYYROSE_RELEASE_SYNTHETIC_FIXTURE' ) && SKYYROSE_RELEASE_SYNTHETIC_FIXTURE && 'http://127.0.0.1:18362' === get_option( 'home' ) && 'sr_release_fixture' === DB_NAME;
$staging = 'https://staging-7e48-skyyrose.wpcomstaging.com' === home_url();
if ( ! defined( 'ABSPATH' ) || ! function_exists( 'wc_get_product' ) || ! ( $fixture || $staging ) || 'skyyrose-flagship-2' !== get_stylesheet() ) {
	throw new RuntimeException( 'Explicit synthetic fixture or reviewed staging V2 required; production is unsupported.' );
}
add_filter( 'woocommerce_webhook_should_deliver', '__return_false', PHP_INT_MAX );
add_filter( 'pre_wp_mail', '__return_true', PHP_INT_MAX );
add_filter( 'pre_http_request', static fn() => new WP_Error( 'skyyrose_size_migration_isolation', 'Outbound HTTP disabled for this migration process.' ), PHP_INT_MAX );
require_once __DIR__ . '/variation-migration-core.php';
$migration = new SkyyRose_Size_Migration( $config['product'] ?? array() );
echo wp_json_encode( $migration->run( $config ), JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES );
