<?php
/** Verify native loop timing and eager policy independently of card rendering. */
define( 'ABSPATH', __DIR__ );
class WC_Product { public function is_visible() { return true; } }
$product = new WC_Product();
$GLOBALS['loop'] = 0;
$GLOBALS['loop_name'] = '';
function wc_get_loop_prop( $name ) { return 'loop' === $name ? $GLOBALS['loop'] : $GLOBALS['loop_name']; }
function is_shop() { return true; }
function is_product_taxonomy() { return false; }
function is_product() { return false; }
function skyyrose2_shop_card_sizes() { return 'native-archive-slot'; }
function wc_product_class( $class, $product ) { ++$GLOBALS['loop']; }
function get_template_part( $path, $name, $args ) { $GLOBALS['captured'] = $args; }
function verify_priority( $index, $name, $expected ) {
	$GLOBALS['loop'] = $index; $GLOBALS['loop_name'] = $name;
	ob_start(); require dirname( __DIR__, 2 ) . '/wordpress-theme/skyyrose-flagship-2/woocommerce/content-product.php'; ob_end_clean();
	$args = $GLOBALS['captured'];
	if ( $args['index'] !== $index || $args['media_priority'] !== $expected ) { throw new RuntimeException( 'Wrong native priority or post-increment index' ); }
}
verify_priority( 0, '', 'high' );
verify_priority( 1, '', 'lazy' );
verify_priority( 2, '', 'lazy' );
verify_priority( 0, 'related', 'lazy' );
echo "PASS native first-card priority and secondary-loop isolation\n";
