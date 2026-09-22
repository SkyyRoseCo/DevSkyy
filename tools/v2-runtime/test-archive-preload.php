<?php
/** Native archive hints must follow the resolved query without consuming it. */
define( 'ABSPATH', __DIR__ );
define( 'SKYYROSE2_DIR', dirname( __DIR__, 2 ) . '/wordpress-theme/skyyrose-flagship-2' );
function add_action() {}
function add_filter() {}
function is_front_page() { return false; }
function is_shop() { return $GLOBALS['route'] === 'shop'; }
function is_product_taxonomy() { return $GLOBALS['route'] === 'category'; }
function is_product_category() { return is_product_taxonomy(); }
function is_admin() { return $GLOBALS['admin'] ?? false; }
function wp_doing_ajax() { return false; }
function is_feed() { return false; }
function is_embed() { return false; }
function has_filter() { return $GLOBALS['visibility_filter'] ?? false; }
function has_action() { return $GLOBALS['loop_action'] ?? false; }
function get_option() { return $GLOBALS['display'] ?? ''; }
function get_term_meta() { return $GLOBALS['term_display'] ?? ''; }
function get_queried_object_id() { return 42; }
function sanitize_title( $value ) { return $value; }
function wp_parse_url( $url, $component ) { return parse_url( $url, $component ); }
function skyyrose2_sot_asset_uri( $path ) { return 'https://example.test/assets/sot/' . $path; }
function skyyrose2_collections() {
	return array( 'signature' => array( 'portal_statue' => array( 'small' => 'images/product-card-portals/signature-portal-statue-640w.webp' ) ) );
}
class WP_Post {
	public $post_type = 'product';
	public function __construct( public $ID ) {}
}
class WP_Query {
	public $current_post = -1;
	public $post_count = 2;
	public $posts;
	public $main = true;
	public $wc_query = 'product_query';
	public function __construct() { $this->posts = array( new WP_Post( 1 ), new WP_Post( 2 ) ); }
	public function get( $key ) { return $this->$key; }
	public function is_main_query() { return $this->main; }
}
class WC_Product {
	public function __construct( public $ID ) {}
	public function is_visible() { return ! in_array( $this->ID, $GLOBALS['hidden'] ?? array(), true ); }
}
function wc_get_product( $id ) { $GLOBALS['hydrated'][] = $id; return new WC_Product( $id ); }
function skyyrose2_product_presentation( $product ) { return array( 'collection' => $GLOBALS['collections'][ $product->ID ] ?? 'signature' ); }
require SKYYROSE2_DIR . '/inc/performance.php';
function reset_case() {
	foreach ( array( 'admin', 'visibility_filter', 'loop_action', 'display', 'term_display', 'hidden', 'collections', 'woocommerce_loop' ) as $key ) { unset( $GLOBALS[ $key ] ); }
	$GLOBALS['route'] = 'shop';
	$GLOBALS['wp_query'] = new WP_Query();
	$GLOBALS['wp_the_query'] = $GLOBALS['wp_query'];
	$GLOBALS['hydrated'] = array();
}
function check( $condition, $message ) { if ( ! $condition ) { throw new RuntimeException( $message ); } }
reset_case();
$before = serialize( $GLOBALS['wp_query'] );
$hint = skyyrose2_performance_route_preloads();
check( count( $hint ) === 1 && str_ends_with( $hint[0]['href'], 'signature-portal-statue-640w.webp' ) && $hint[0]['fetchpriority'] === 'high', 'Exact first frame hint' );
check( serialize( $GLOBALS['wp_query'] ) === $before && ! isset( $GLOBALS['woocommerce_loop'] ) && $GLOBALS['hydrated'] === array( 1 ), 'No cursor, loop or selection mutation' );
check( count( skyyrose2_performance_preload_resources( $hint ) ) === 1, 'Native hint deduplication' );
reset_case();
$GLOBALS['hidden'] = array( 1 );
check( ! empty( skyyrose2_performance_archive_frame_preload() ) && $GLOBALS['hydrated'] === array( 1, 2 ), 'Invisible products skipped in resolved order' );
reset_case();
$GLOBALS['wp_query']->posts = array( new WP_Post( 2 ), new WP_Post( 1 ) );
$GLOBALS['collections'][2] = 'unknown';
check( skyyrose2_performance_archive_frame_preload() === array() && $GLOBALS['hydrated'] === array( 2 ), 'Unknown first visible product cannot borrow later frame' );
$cases = array(
	'admin' => function() { $GLOBALS['admin'] = true; },
	'visibility extension' => function() { $GLOBALS['visibility_filter'] = true; },
	'loop extension' => function() { $GLOBALS['loop_action'] = true; },
	'secondary query' => function() { $GLOBALS['wp_the_query'] = new WP_Query(); },
	'nonmain query' => function() { $GLOBALS['wp_query']->main = false; },
	'noncommerce query' => function() { $GLOBALS['wp_query']->wc_query = ''; },
	'consumed query' => function() { $GLOBALS['wp_query']->current_post = 0; },
	'empty query' => function() { $GLOBALS['wp_query']->post_count = 0; },
	'invalid post' => function() { $GLOBALS['wp_query']->posts = array( 2 ); },
	'named loop' => function() { $GLOBALS['woocommerce_loop'] = array( 'name' => 'related' ); },
	'shortcode loop' => function() { $GLOBALS['woocommerce_loop'] = array( 'is_shortcode' => true ); },
	'consumed loop' => function() { $GLOBALS['woocommerce_loop'] = array( 'loop' => 1 ); },
	'empty loop' => function() { $GLOBALS['woocommerce_loop'] = array( 'total' => 0 ); },
	'category display' => function() { $GLOBALS['display'] = 'subcategories'; },
	'mixed display' => function() { $GLOBALS['route'] = 'category'; $GLOBALS['term_display'] = 'both'; },
);
foreach ( $cases as $name => $setup ) {
	reset_case(); $setup();
	check( skyyrose2_performance_archive_frame_preload() === array(), $name . ' must omit hint' );
	check( $GLOBALS['hydrated'] === array(), $name . ' must not hydrate products' );
}
reset_case();
$GLOBALS['route'] = 'category';
check( ! empty( skyyrose2_performance_archive_frame_preload() ), 'Product-only taxonomy allowed' );
reset_case();
$GLOBALS['hidden'] = array( 1, 2 );
check( skyyrose2_performance_archive_frame_preload() === array(), 'All invisible gives no hint' );
echo "PASS native archive preload order, nonmutation, deduplication and 15 exclusion cases\n";
