<?php
/** Offline behavioral regression: CSS removal stays limited to the public native home. */
define( 'ABSPATH', __DIR__ );
$flags = array( 'front' => true, 'admin' => false, 'logged_in' => false, 'customize' => false, 'preview' => false, 'opt_in' => false );
$removed = array();
$hooks = array();
function add_action( $hook, $callback, $priority = 10, $args = 1 ) { global $hooks; $hooks[] = array( $hook, $callback, $priority ); }
function add_filter( $hook, $callback, $priority = 10, $args = 1 ) {}
function is_admin() { global $flags; return $flags['admin']; }
function is_front_page() { global $flags; return $flags['front']; }
function is_user_logged_in() { global $flags; return $flags['logged_in']; }
function is_customize_preview() { global $flags; return $flags['customize']; }
function is_preview() { global $flags; return $flags['preview']; }
function apply_filters( $name, $value ) { global $flags; return 'skyyrose2_home_plugin_styles' === $name ? $flags['opt_in'] : $value; }
function wp_dequeue_style( $handle ) { global $removed; $removed[] = $handle; }
require dirname( __DIR__, 2 ) . '/wordpress-theme/skyyrose-flagship-2/inc/performance.php';
function check( $condition, $message ) { if ( ! $condition ) { throw new RuntimeException( $message ); } }
skyyrose2_performance_home_plugin_styles();
check( in_array( 'elementor-common', $removed, true ) && in_array( 'jetpack-block-podcast-episode', $removed, true ), 'Public home retains unused editor/block CSS' );
foreach ( array( 'jetpack-instant-search', 'jetpack-search-results-list-style', 'ea11y-skip-link', 'woocommerce-general', 'skyyrose2-theme', 'skyyrose2-home-page', 'skyyrose2-quick-view-commerce' ) as $protected ) {
	check( ! in_array( $protected, $removed, true ), 'Required style removed: ' . $protected );
}
foreach ( array( 'admin', 'logged_in', 'customize', 'preview', 'opt_in' ) as $flag ) {
	$flags[ $flag ] = true;
	$removed = array();
	skyyrose2_performance_home_plugin_styles();
	check( array() === $removed, 'Editor/plugin opt-in styles removed: ' . $flag );
	$flags[ $flag ] = false;
}
$flags['front'] = false;
$removed = array();
skyyrose2_performance_home_plugin_styles();
check( array() === $removed, 'Non-home content or commerce style removed' );
check( in_array( array( 'wp_print_styles', 'skyyrose2_performance_home_plugin_styles', 1 ), $hooks, true ), 'Cleanup must run before the combined stylesheet is printed' );
echo "PASS public-home CSS removal; search, accessibility, commerce, editors, previews and all other routes retained\n";
