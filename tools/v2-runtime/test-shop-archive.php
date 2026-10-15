<?php
/** Query-boundary regression for the actual native Shop module; no database writes. */
define( 'ABSPATH', __DIR__ );
set_error_handler( static function ( $severity, $message, $file, $line ) { throw new ErrorException( $message, 0, $severity, $file, $line ); } );
function add_action( ...$args ) { $GLOBALS['registered_actions'][] = $args; }
function add_filter( ...$args ) { $GLOBALS['registered_filters'][] = $args; }
function remove_action( ...$args ) { $GLOBALS['removed_actions'][] = $args; }
function check_shop( $condition, $message ) { if ( ! $condition ) { throw new RuntimeException( $message ); } }
require __DIR__ . '/../../wordpress-theme/skyyrose-flagship-2/inc/shop-archive.php';

// Conditional declarations below do not exist yet: exercise plugin deactivation.
check_shop( ! function_exists( 'wc_get_page_id' ), 'Inactive-plugin fixture must have no Woo functions' );
$ordinary_request = array( 'page_id' => '41' );
$_GET = array( 'min_price' => array( 'bad' ) );
check_shop( $ordinary_request === skyyrose2_shop_request_vars( $ordinary_request ), 'Without Woo, ordinary requests must be unchanged' );
skyyrose2_shop_hooks();
check_shop( empty( $GLOBALS['removed_actions'] ), 'Without Woo, no native callbacks may be removed' );

if ( ! function_exists( 'wc_get_page_id' ) ) {
	function wc_get_page_id( $page ) { return 20; }
	function wc_get_page_permalink( $page ) { return 'https://example.test/shop/'; }
	function is_admin() { return $GLOBALS['shop_admin']; }
	function wp_doing_ajax() { return $GLOBALS['shop_ajax']; }
	function is_shop() { return $GLOBALS['shop_route']; }
	function is_product_taxonomy() { return (bool) $GLOBALS['shop_term']; }
	function is_product_category() { return $GLOBALS['shop_term'] && 'product_cat' === $GLOBALS['shop_term']->taxonomy; }
	function get_queried_object() { return $GLOBALS['shop_term']; }
	function get_taxonomy( $name ) { return (object) array( 'query_var' => $name ); }
	function get_object_taxonomies( $post_type ) { return array( 'product_cat', 'product_tag', 'pa_size' ); }
	function get_page_uri( $page ) { return 'shop'; }
	function get_terms( $args ) { return $GLOBALS['shop_terms']; }
	function is_wp_error( $value ) { return $value instanceof WP_Error; }
	function wp_unslash( $value ) { return is_array( $value ) ? array_map( 'wp_unslash', $value ) : stripslashes( $value ); }
	function sanitize_text_field( $value ) { return strip_tags( $value ); }
	function map_deep( $value, $callback ) { return is_array( $value ) ? array_map( static fn( $item ) => map_deep( $item, $callback ), $value ) : $callback( $value ); }
	function apply_filters( $name, $value ) { if ( 'woocommerce_catalog_orderby' === $name ) { $value['extension-order'] = 'Extension order'; } return $value; }
	function add_query_arg( $args, $url ) { return $url . ( $args ? '?' . http_build_query( $args ) : '' ); }
	function esc_html__( $text, $domain ) { return htmlspecialchars( $text, ENT_QUOTES, 'UTF-8' ); }
	function woocommerce_catalog_ordering( $attributes ) { check_shop( true === $attributes['useLabel'], 'Native sorting needs its visible label' ); echo '<form class="woocommerce-ordering" method="get"><select name="orderby"><option>Native option</option></select><input type="hidden" name="product_cat" value="signature"></form>'; }
}
class WP_Error {}
class WP_Term {
	public function __construct( public $slug, public $name, public $taxonomy = 'product_cat', public $count = 1 ) {}
}
class Shop_Test_Query {
	public $main = true;
	public $archive = true;
	public $tax = false;
	public $values = array();
	public function is_main_query() { return $this->main; }
	public function is_post_type_archive( $type ) { return $this->archive && 'product' === $type; }
	public function is_tax( $taxonomies ) { return $this->tax && in_array( 'product_cat', $taxonomies, true ); }
	public function get( $key ) { return $this->values[ $key ] ?? null; }
	public function set( $key, $value ) { $this->values[ $key ] = $value; }
}
$GLOBALS['shop_admin'] = false;
$GLOBALS['shop_ajax'] = false;
$GLOBALS['shop_route'] = true;
$GLOBALS['shop_term'] = null;
$GLOBALS['shop_terms'] = array( new WP_Term( 'signature', 'Signature' ), new WP_Term( 'black-rose', 'Black Rose' ), new WP_Term( 'empty-category', 'Empty category', 'product_cat', 0 ) );

$valid = array( 'product_cat' => 'signature', 'stock_status' => 'onbackorder', 'min_price' => '0', 'max_price' => '125.50', 'orderby' => 'price-desc' );
check_shop( $valid === skyyrose2_shop_filter_state( $valid ), 'Valid native filter state and zero minimum must be preserved exactly' );
check_shop( 'extension-order' === skyyrose2_shop_filter_state( array( 'orderby' => 'extension-order' ) )['orderby'], 'Preserve installed Woo ordering extensions' );
check_shop( 'empty-category' === skyyrose2_shop_filter_state( array( 'product_cat' => 'empty-category' ) )['product_cat'], 'Real empty category remains a legitimate native empty-result state' );
check_shop( 'signature' === skyyrose2_shop_filter_state( array( 'product_cat' => 'parent/signature' ) )['product_cat'], 'Native hierarchical category paths select their actual terminal term' );
foreach ( array( null, 'bad', 42, true, new stdClass() ) as $input ) {
	check_shop( ! array_filter( skyyrose2_shop_filter_state( $input ) ), 'Hostile nonscalar form container must not reach Woo filters' );
}
foreach ( array( array( 'bad' ), new stdClass(), true, 22, null, '<script>alert(1)</script>', 'instock OR 1=1', '-10', 'INF', 'NaN', '1e300', '1,000', '2.0x', '999999999999999999999' ) as $bad ) {
	$state = skyyrose2_shop_filter_state( array_fill_keys( array_keys( $valid ), $bad ) );
	check_shop( ! array_filter( $state ), 'Reject malformed scalars/arrays/objects for every owned dimension' );
}
$reversed = skyyrose2_shop_filter_state( array( 'min_price' => '100', 'max_price' => '10' ) );
check_shop( '100' === $reversed['min_price'] && '10' === $reversed['max_price'], 'Do not silently swap a user range; native Woo owns the empty result' );

$_GET = $valid + array( 's' => 'rose', 'filter_size' => 'm', 'query_type_size' => 'or' );
$vars = skyyrose2_shop_request_vars( array( 'post_type' => 'product', 'product_cat' => 'signature' ) );
check_shop( 'signature' === $vars['product_cat'] && 'rose' === $_GET['s'] && 'or' === $_GET['query_type_size'], 'Valid request preserves native category/search/attribute conditions' );
$_GET = array( 'product_cat' => array( 'signature' ), 'stock_status' => array( 'instock' ), 'min_price' => array( '0' ), 'max_price' => 'NaN', 'orderby' => array( 'price' ), 'filter_size' => 'm' );
$vars = skyyrose2_shop_request_vars( array( 'post_type' => 'product', 'product_cat' => array( 'signature' ) ) );
check_shop( array( 'post_type' => 'product' ) === $vars && array( 'filter_size' => 'm' ) === $_GET, 'Malformed arrays cleared before WP taxonomy/Woo price parsing; unrelated fields preserved' );
foreach ( array( 'parent/signature', 'unknown-category', 'parent/unknown-child' ) as $native_category ) {
	$_GET = array();
	$native_vars = array( 'product_cat' => $native_category );
	check_shop( $native_vars === skyyrose2_shop_request_vars( $native_vars ), 'Preserve native category path and unknown-term 404 routing' );
	$_GET = array( 'product_cat' => $native_category );
	check_shop( $native_vars === skyyrose2_shop_request_vars( $native_vars ) && $native_category === $_GET['product_cat'], 'GET category routing also remains native' );
}
foreach ( array( array( 'page_id' => '20' ), array( 'pagename' => 'shop' ), array( 'product_tag' => 'rose' ), array( 'taxonomy' => 'pa_size' ) ) as $route ) {
	$_GET = array( 'min_price' => array( 'bad' ) );
	skyyrose2_shop_request_vars( $route );
	check_shop( ! isset( $_GET['min_price'] ), 'Native pretty/plain archive routes sanitize malformed owned filters' );
}
foreach ( array( array( 'pagename' => 'about' ), array( 'post_type' => 'product', 'product' => 'jersey' ), array( 'post_type' => 'product', 'p' => '41' ) ) as $route ) {
	$_GET = array( 'min_price' => array( 'bad' ) );
	check_shop( $route === skyyrose2_shop_request_vars( $route ) && isset( $_GET['min_price'] ), 'Unrelated/single-product requests stay untouched' );
}

$original_meta = array( 'relation' => 'OR', 'extension_first' => array( 'key' => '_custom', 'value' => 'x' ), array( 'relation' => 'AND', array( 'key' => '_other', 'value' => 'y' ) ) );
$original_tax = array( 'relation' => 'AND', array( 'taxonomy' => 'product_visibility', 'terms' => array( 8 ), 'operator' => 'NOT IN' ), array( 'taxonomy' => 'product_cat', 'terms' => array( 2 ) ) );
foreach ( array( 'instock', 'outofstock', 'onbackorder' ) as $stock ) {
	$_GET = array( 'stock_status' => $stock );
	$query = new Shop_Test_Query();
	$query->values = array( 'meta_query' => $original_meta, 'tax_query' => $original_tax, 'post__in' => array( 4, 5 ) );
	skyyrose2_shop_stock_query( $query );
	$expected = array( 'relation' => 'AND', $original_meta, array( 'key' => '_stock_status', 'value' => $stock, 'compare' => '=' ) );
	check_shop( $expected === $query->get( 'meta_query' ), 'Stock constraint must AND-wrap intact nested/named OR conditions' );
	check_shop( $original_tax === $query->get( 'tax_query' ) && array( 4, 5 ) === $query->get( 'post__in' ), 'Preserve native tax, visibility, and product inclusion conditions' );
}
foreach ( array( 'secondary', 'other-route', 'admin', 'ajax', 'invalid' ) as $scenario ) {
	$_GET = array( 'stock_status' => 'instock' );
	$query = new Shop_Test_Query();
	$query->values = array( 'meta_query' => $original_meta, 'tax_query' => $original_tax );
	if ( 'secondary' === $scenario ) { $query->main = false; }
	if ( 'other-route' === $scenario ) { $query->archive = false; }
	if ( 'admin' === $scenario ) { $GLOBALS['shop_admin'] = true; }
	if ( 'ajax' === $scenario ) { $GLOBALS['shop_ajax'] = true; }
	if ( 'invalid' === $scenario ) { $_GET['stock_status'] = array( 'instock' ); }
	skyyrose2_shop_stock_query( $query );
	check_shop( $original_meta === $query->get( 'meta_query' ), 'Stock must not affect ' . $scenario );
	$GLOBALS['shop_admin'] = false;
	$GLOBALS['shop_ajax'] = false;
}
$query = new Shop_Test_Query();
$query->archive = false;
$query->tax = true;
$_GET = array( 'stock_status' => 'instock' );
skyyrose2_shop_stock_query( $query );
check_shop( 'instock' === $query->get( 'meta_query' )[0]['value'], 'Main native product taxonomy supports stock selection' );

$_GET = array( 'product_cat' => 'black-rose', 'orderby' => 'price-desc', 's' => 'rose jersey', 'filter_size' => 'm', 'filter_nested' => array( 'x' => 'y' ), 'paged' => '3', 'add-to-cart' => '41', '_wpnonce' => 'secret' );
$url = skyyrose2_shop_category_url( 'signature' );
parse_str( parse_url( $url, PHP_URL_QUERY ), $url_args );
check_shop( 'signature' === $url_args['product_cat'] && 'price-desc' === $url_args['orderby'] && 'rose jersey' === $url_args['s'] && 'm' === $url_args['filter_size'] && array( 'x' => 'y' ) === $url_args['filter_nested'], 'Collection URL preserves ordering/search/layered filter state' );
check_shop( ! isset( $url_args['paged'], $url_args['add-to-cart'], $url_args['_wpnonce'] ), 'New category resets pagination and drops transaction parameters' );
parse_str( parse_url( skyyrose2_shop_category_url( '' ), PHP_URL_QUERY ), $all_args );
check_shop( ! isset( $all_args['product_cat'] ) && 'price-desc' === $all_args['orderby'], 'All pieces clears only category, preserving order' );
$GLOBALS['shop_term'] = new WP_Term( 'gift', 'Gift', 'product_tag' );
check_shop( 'gift' === skyyrose2_shop_query_args()['product_tag'], 'Pretty taxonomy context survives GET form/collection navigation' );
$GLOBALS['shop_term'] = new WP_Term( 'signature', 'Signature' );
check_shop( 'signature' === skyyrose2_shop_current_state()['product_cat'], 'Pretty product-category route is the selected filter state' );
$GLOBALS['shop_term'] = null;

ob_start();
skyyrose2_shop_ordering();
$form = ob_get_clean();
check_shop( 1 === substr_count( $form, 'type="submit"' ) && str_contains( $form, 'Native option' ) && str_contains( $form, 'name="product_cat"' ), 'Native sorting stays intact with one genuine no-JS submit' );
skyyrose2_shop_hooks();
check_shop( array( 'woocommerce_before_shop_loop', 'woocommerce_catalog_ordering', 30 ) === end( $GLOBALS['removed_actions'] ), 'Only replace the native ordering presentation hook' );
check_shop( str_contains( skyyrose2_shop_card_sizes(), '22.49em' ) && str_contains( skyyrose2_shop_card_sizes(), '363px' ), 'Responsive image slots include narrow one-column and bounded desktop grid' );

// REST guards are immutable and therefore tested last in this isolated process.
define( 'REST_REQUEST', true );
$_GET = array( 'stock_status' => 'instock', 'min_price' => array( 'bad' ) );
$query = new Shop_Test_Query();
$query->values['meta_query'] = $original_meta;
skyyrose2_shop_stock_query( $query );
check_shop( $original_meta === $query->get( 'meta_query' ), 'No stock filtering in REST' );
$vars = array( 'post_type' => 'product' );
check_shop( $vars === skyyrose2_shop_request_vars( $vars ) && is_array( $_GET['min_price'] ), 'No request normalization in REST' );
echo "PASS Shop native query boundaries, hostile inputs, inactive Woo, URL state, empty categories, stock AND grouping and no-JS sorting\n";
