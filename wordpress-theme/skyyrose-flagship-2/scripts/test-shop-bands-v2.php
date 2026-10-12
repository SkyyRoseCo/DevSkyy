<?php
/**
 * Behaviour contract for the founder-chosen v2 Cinema Bands Shop.
 *
 * Founder ruling 2026-10-11: the unfiltered /shop/ is grouped per collection in
 * house order, every card reachable, no pagination on that view; filtered views
 * (collection, stock, price) keep the existing grid and pagination unchanged.
 * Runs the real inc/shop-archive.php, inc/performance.php preload,
 * woocommerce/archive-product.php, the bands template part and content-product.php
 * against WordPress/WooCommerce stubs. No database, network or file writes.
 *
 * @package SkyyRoseFlagship2
 */

define( 'ABSPATH', __DIR__ . '/' );
define( 'SKYYROSE2_DIR', dirname( __DIR__ ) );
define( 'SKYYROSE2_URI', 'https://example.test/wp-content/themes/skyyrose-flagship-2' );
set_error_handler( static function ( $severity, $message, $file, $line ) { throw new ErrorException( $message, 0, $severity, $file, $line ); } );

$GLOBALS['sr2b_hooks'] = array();
function add_action( $hook, $callback, $priority = 10, $accepted_args = 1 ) { $GLOBALS['sr2b_hooks'][] = array( $hook, $callback, $priority, $accepted_args ); }
function add_filter( $hook, $callback, $priority = 10, $accepted_args = 1 ) { $GLOBALS['sr2b_hooks'][] = array( $hook, $callback, $priority, $accepted_args ); }
function remove_action() {}
function check( $condition, $message ) { if ( ! $condition ) { throw new RuntimeException( $message ); } }

// --- WordPress / WooCommerce stubs --------------------------------------------------
function __( $text, $domain = '' ) { return $text; }
function _n( $single, $plural, $number, $domain = '' ) { return 1 === (int) $number ? $single : $plural; }
function esc_html( $text ) { return htmlspecialchars( (string) $text, ENT_QUOTES, 'UTF-8' ); }
function esc_attr( $text ) { return esc_html( $text ); }
function esc_url( $url ) { return esc_html( $url ); }
function esc_html__( $text, $domain = '' ) { return esc_html( $text ); }
function esc_html_e( $text, $domain = '' ) { echo esc_html( $text ); }
function esc_attr_e( $text, $domain = '' ) { echo esc_attr( $text ); }
function selected( $a, $b ) { echo $a === $b ? ' selected' : ''; }
function is_admin() { return ! empty( $GLOBALS['sr2b']['admin'] ); }
function wp_doing_ajax() { return ! empty( $GLOBALS['sr2b']['ajax'] ); }
function is_feed() { return false; }
function is_embed() { return false; }
function is_shop() { return $GLOBALS['wp_query']->is_post_type_archive( 'product' ); }
function is_product_taxonomy() { return $GLOBALS['wp_query']->is_tax(); }
function is_product_category() { return false; }
function is_product() { return false; }
function is_main_query() { return $GLOBALS['wp_query']->is_main_query(); }
function get_queried_object() { return null; }
function get_queried_object_id() { return 0; }
function get_option( $name, $default = '' ) { return $default; }
function get_term_meta() { return ''; }
function has_filter() { return false; }
function has_action() { return false; }
function apply_filters( $name, $value ) { return $value; }
function do_action( $name ) { $GLOBALS['sr2b_actions'][] = $name; }
function wc_get_page_id( $page ) { return 20; }
function wc_get_page_permalink( $page ) { return 'https://example.test/shop/'; }
function get_terms( $args ) { return array( (object) array( 'slug' => 'signature', 'name' => 'Signature' ), (object) array( 'slug' => 'black-rose', 'name' => 'Black Rose' ), (object) array( 'slug' => 'love-hurts', 'name' => 'Love Hurts' ), (object) array( 'slug' => 'kids-capsule', 'name' => 'Kids Capsule' ) ); }
function is_wp_error( $value ) { return false; }
function wp_unslash( $value ) { return is_array( $value ) ? array_map( 'wp_unslash', $value ) : stripslashes( (string) $value ); }
function sanitize_text_field( $value ) { return strip_tags( (string) $value ); }
function sanitize_title( $value ) { return strtolower( trim( preg_replace( '/[^a-z0-9]+/i', '-', (string) $value ), '-' ) ); }
function sanitize_key( $value ) { return strtolower( preg_replace( '/[^a-z0-9_\-]/i', '', (string) $value ) ); }
function map_deep( $value, $callback ) { return is_array( $value ) ? array_map( static fn( $item ) => map_deep( $item, $callback ), $value ) : $callback( $value ); }
function add_query_arg( $args, $url ) { return $url . ( $args ? '?' . http_build_query( $args ) : '' ); }
function wp_parse_url( $url, $component = -1 ) { return parse_url( $url, $component ); }
function get_query_var( $key ) { return 'paged' === $key ? (int) ( $GLOBALS['sr2b']['paged'] ?? 0 ) : ''; }
class Sr2b_Redirect extends Exception {
	public function __construct( public $url, public $status ) { parent::__construct( 'redirect' ); }
}
function wp_safe_redirect( $url, $status ) { throw new Sr2b_Redirect( $url, $status ); }
function woocommerce_page_title( $echo ) { return 'Shop'; }
function get_woocommerce_currency() { return 'USD'; }
function wc_query_string_form_fields() {}
function get_header() {}
function get_footer() {}
function skyyrose2_collection_url( $slug ) { return 'https://example.test/collections/' . $slug . '/'; }
function skyyrose2_is_transaction_preorder_product( $product ) { return false; }
function woocommerce_product_loop() { return (bool) $GLOBALS['wp_query']->posts; }
function wc_get_loop_prop( $key, $default = '' ) { return $GLOBALS['woocommerce_loop'][ $key ] ?? $default; }
function wc_set_loop_prop( $key, $value ) { $GLOBALS['woocommerce_loop'][ $key ] = $value; }
function woocommerce_product_loop_start() { wc_set_loop_prop( 'loop', 0 ); echo '<ul class="products columns-4">'; }
function woocommerce_product_loop_end() { echo '</ul>'; }
function wc_product_class( $class, $product ) { wc_set_loop_prop( 'loop', (int) wc_get_loop_prop( 'loop', 0 ) + 1 ); echo 'class="' . esc_attr( $class ) . '"'; }
function wc_get_template_part( $slug, $name ) { require SKYYROSE2_DIR . '/woocommerce/content-product.php'; }
function get_template_part( $slug, $name = null, $args = array() ) {
	if ( 'template-parts/shop/collection-bands-v2' === $slug ) {
		$GLOBALS['sr2b_band_args'] = $args;
		require SKYYROSE2_DIR . '/template-parts/shop/collection-bands-v2.php';
		return;
	}
	check( 'template-parts/commerce/product-card' === $slug, 'Only the native card partial renders pieces' );
	$GLOBALS['sr2b_cards'][] = array( 'sku' => $args['product']->get_sku(), 'index' => $args['index'], 'priority' => $args['media_priority'], 'sizes' => $args['sizes'], 'heading_level' => $args['heading_level'] ?? null );
	echo '<article data-sku="' . esc_attr( $args['product']->get_sku() ) . '"></article>';
}
function get_post( $id ) { return new WP_Post( $id ); }
function setup_postdata( $post ) {}
function wp_reset_postdata() {}
function get_the_ID() { return $GLOBALS['post']->ID; }
function have_posts() { return $GLOBALS['wp_query']->current_post + 1 < count( $GLOBALS['wp_query']->posts ); }
function the_post() { $query = $GLOBALS['wp_query']; ++$query->current_post; $GLOBALS['post'] = $query->posts[ $query->current_post ]; $GLOBALS['product'] = wc_get_product( $GLOBALS['post']->ID ); } // WC hooks wc_setup_product_data() on the_post.
function skyyrose2_media_uri( $relative, $role = '' ) {
	// The real gate is covered by tools/v2-runtime/test-collection-cinema-delivery.php;
	// here a granted film is one whose approved file ships with the theme.
	if ( ! empty( $GLOBALS['sr2b']['withhold'] ) && 'collection_hero_poster' === $role ) { return ''; }
	return is_file( SKYYROSE2_DIR . '/' . $relative ) ? SKYYROSE2_URI . '/' . $relative : '';
}
function skyyrose2_approved_card_front( $product ) {
	$sku = $product->get_sku();
	return array( 'src' => SKYYROSE2_URI . "/assets/v2/{$sku}.webp", 'card_src' => SKYYROSE2_URI . "/assets/derived/card-fronts/{$sku}-640w.webp", 'srcset' => SKYYROSE2_URI . "/assets/derived/card-fronts/{$sku}-640w.webp 640w" );
}
// Identifier-only fixture: SKU → collection binding, no product facts.
$GLOBALS['sr2b_catalog'] = array( 1 => array( 'br-001', 'black-rose' ), 2 => array( 'sg-013', 'signature' ), 3 => array( 'lh-002', 'love-hurts' ), 4 => array( 'kids-001', 'kids-capsule' ), 5 => array( 'xx-001', '' ), 6 => array( 'sg-002', 'signature' ), 7 => array( 'br-002', 'black-rose' ), 8 => array( 'lh-003', 'love-hurts' ), 9 => array( 'sg-003', 'Signature' ) );
function skyyrose2_product_presentation( $product ) {
	$collection = $GLOBALS['sr2b_catalog'][ $product->get_id() ][1] ?? '';
	return '' === $collection ? array() : array( 'collection' => $collection );
}
class WP_Post {
	public $post_type = 'product';
	public function __construct( public $ID ) {}
}
class WC_Product {
	public function __construct( public $id ) {}
	public function get_id() { return $this->id; }
	public function get_sku() { return $GLOBALS['sr2b_catalog'][ $this->id ][0]; }
	public function is_visible() { return true; }
}
function wc_get_product( $id ) { return isset( $GLOBALS['sr2b_catalog'][ $id ] ) ? new WC_Product( $id ) : false; }
class WP_Query {
	public $main = true;
	public $archive = true;
	public $search = false;
	public $tax = false;
	public $feed = false;
	public $current_post = -1;
	public $post_count = 0;
	public $posts = array();
	public $vars = array( 'wc_query' => 'product_query' );
	public function is_main_query() { return $this->main; }
	public function is_post_type_archive( $type = '' ) { return $this->archive && ( '' === $type || 'product' === $type ); }
	public function is_search() { return $this->search; }
	public function is_tax( $taxonomy = '' ) { return $this->tax; }
	public function is_feed() { return $this->feed; }
	public function get( $key, $default = '' ) { return $this->vars[ $key ] ?? $default; }
	public function set( $key, $value ) { $this->vars[ $key ] = $value; }
}

// Real house collections from functions.php, extracted without loading the theme bootstrap.
$functions = file_get_contents( SKYYROSE2_DIR . '/functions.php' );
preg_match( "/define\( 'SKYYROSE2_VERSION', '([0-9.]+)' \);/", $functions, $theme_version );
define( 'SKYYROSE2_VERSION', $theme_version[1] );
$start     = strpos( $functions, 'function skyyrose2_collections() {' );
eval( substr( $functions, $start, strpos( $functions, "\n}\n", $start ) + 3 - $start ) ); // phpcs:ignore Squiz.PHP.Eval.Discouraged
require SKYYROSE2_DIR . '/inc/shop-archive.php';
require SKYYROSE2_DIR . '/inc/performance.php';
check( array( 'signature', 'black-rose', 'love-hurts', 'kids-capsule' ) === array_keys( skyyrose2_collections() ), 'House order is signature, black-rose, love-hurts, kids-capsule' );

function sr2b_reset( $get = array(), $ids = array( 1, 2, 3, 4, 5, 6, 7, 8, 9 ) ) {
	$_GET                        = $get;
	$GLOBALS['sr2b']             = array();
	$GLOBALS['sr2b_cards']       = array();
	$GLOBALS['sr2b_actions']     = array();
	$GLOBALS['sr2b_band_args']   = null;
	$GLOBALS['woocommerce_loop'] = array();
	$GLOBALS['post']             = null;
	$GLOBALS['product']          = null;
	$query                       = new WP_Query();
	$query->posts                = array_map( static fn( $id ) => new WP_Post( $id ), $ids );
	$query->post_count           = count( $query->posts );
	$GLOBALS['wp_query']         = $query;
	$GLOBALS['wp_the_query']     = $query;
	return $query;
}
function sr2b_hook( $hook, $callback ) {
	foreach ( $GLOBALS['sr2b_hooks'] as $registered ) {
		if ( $registered[0] === $hook && $registered[1] === $callback ) { return $registered; }
	}
	return null;
}
function sr2b_render() {
	ob_start();
	require SKYYROSE2_DIR . '/woocommerce/archive-product.php';
	return ob_get_clean();
}

// 1. Predicate: only the unfiltered main product archive, ordering alone allowed.
sr2b_reset();
check( skyyrose2_shop_bands_v2_active(), 'Unfiltered main Shop archive is the grouped view' );
foreach ( array( array( 'orderby' => 'price-desc' ), array( 'orderby' => 'date', 'utm_source' => 'x' ), array( 'stock_status' => 'bogus' ), array( 'min_price' => 'NaN' ), array( 'filter_size' => '' ) ) as $get ) {
	sr2b_reset( $get );
	check( skyyrose2_shop_bands_v2_active(), 'Ordering, tracking and invalid (ignored) filter values do not disable bands: ' . http_build_query( $get ) );
}
$filters = array( 'product_cat' => 'signature', 'stock_status' => 'instock', 'min_price' => '0', 'max_price' => '125' );
$keys    = array_keys( $filters );
for ( $mask = 1; $mask < 16; $mask++ ) {
	$get = array( 'orderby' => 'price' );
	foreach ( $keys as $bit => $key ) {
		if ( $mask & ( 1 << $bit ) ) { $get[ $key ] = $filters[ $key ]; }
	}
	sr2b_reset( $get );
	check( ! skyyrose2_shop_bands_v2_active(), 'Every collection/stock/price filter combination keeps the grid: ' . http_build_query( $get ) );
}
foreach ( array( array( 'filter_size' => 'm' ), array( 'filter_color' => array( 'red' ) ), array( 'rating_filter' => '4' ) ) as $get ) {
	sr2b_reset( $get );
	check( ! skyyrose2_shop_bands_v2_active(), 'Woo layered-nav/rating filters keep the grid: ' . json_encode( $get ) );
}
$contexts = array(
	'search'          => static function ( $q ) { $q->search = true; },
	'taxonomy'        => static function ( $q ) { $q->tax = true; $q->archive = false; },
	'tax on archive'  => static function ( $q ) { $q->tax = true; },
	'secondary query' => static function ( $q ) { $q->main = false; },
	'other archive'   => static function ( $q ) { $q->archive = false; },
	'feed'            => static function ( $q ) { $q->feed = true; },
	'admin'           => static function ( $q ) { $GLOBALS['sr2b']['admin'] = true; },
	'ajax'            => static function ( $q ) { $GLOBALS['sr2b']['ajax'] = true; },
);
foreach ( $contexts as $name => $setup ) {
	$query = sr2b_reset();
	$setup( $query );
	check( ! skyyrose2_shop_bands_v2_active(), "Not grouped: {$name}" );
	check( ! skyyrose2_shop_bands_v2_active( $query ), "Not grouped with explicit query: {$name}" );
}

// 2. Query args: one page on the grouped view only, after Woo's own pre_get_posts (10).
check( array( 'pre_get_posts', 'skyyrose2_shop_bands_v2_query', 30, 1 ) === sr2b_hook( 'pre_get_posts', 'skyyrose2_shop_bands_v2_query' ), 'Per-page override runs after WC_Query::pre_get_posts at 10' );
$query = sr2b_reset( array( 'orderby' => 'price' ) );
$query->set( 'posts_per_page', 16 ); // What Woo's loop_shop_per_page wrote at priority 10.
skyyrose2_shop_bands_v2_query( $query );
check( -1 === $query->get( 'posts_per_page' ), 'Grouped view requests every published piece (WP sets nopaging for -1)' );
foreach ( array( array( 'min_price' => '0' ), array( 'product_cat' => 'signature' ), array( 'stock_status' => 'instock' ) ) as $get ) {
	$query = sr2b_reset( $get );
	$query->set( 'posts_per_page', 16 );
	skyyrose2_shop_bands_v2_query( $query );
	check( 16 === $query->get( 'posts_per_page' ), 'Filtered views keep native per-page and pagination' );
}
$query = sr2b_reset();
$query->search = true;
$query->set( 'posts_per_page', 24 );
skyyrose2_shop_bands_v2_query( $query );
check( 24 === $query->get( 'posts_per_page' ), 'Search keeps its bounded page' );

// 3. 301: stale /shop/page/N/ on the grouped view; filtered paged URLs untouched.
check( array( 'template_redirect', 'skyyrose2_shop_bands_v2_redirect', 5, 1 ) === sr2b_hook( 'template_redirect', 'skyyrose2_shop_bands_v2_redirect' ), 'Redirect runs before redirect_canonical (10)' );
foreach ( array( array( array(), 'https://example.test/shop/' ), array( array( 'orderby' => 'price', 'utm_source' => 'mail' ), 'https://example.test/shop/?orderby=price&utm_source=mail' ), array( array( 'paged' => '3', 'orderby' => 'date', 'add-to-cart' => '9', '_wpnonce' => 'n' ), 'https://example.test/shop/?orderby=date' ) ) as $case ) {
	sr2b_reset( $case[0] );
	$GLOBALS['sr2b']['paged'] = 3;
	try {
		skyyrose2_shop_bands_v2_redirect();
		check( false, 'Paged grouped view must redirect' );
	} catch ( Sr2b_Redirect $redirect ) {
		check( 301 === $redirect->status && $case[1] === $redirect->url, 'Paged grouped view 301s to the Shop with non-filter args kept: ' . $redirect->url );
	}
}
foreach ( array( 0, 1 ) as $paged ) {
	sr2b_reset();
	$GLOBALS['sr2b']['paged'] = $paged;
	skyyrose2_shop_bands_v2_redirect();
}
foreach ( array( array( 'min_price' => '0' ), array( 'product_cat' => 'signature' ), array( 'stock_status' => 'outofstock' ), array( 'filter_size' => 'm' ) ) as $get ) {
	sr2b_reset( $get );
	$GLOBALS['sr2b']['paged'] = 2;
	skyyrose2_shop_bands_v2_redirect(); // Would throw if it redirected.
}
$query = sr2b_reset();
$query->search = true;
$GLOBALS['sr2b']['paged'] = 2;
skyyrose2_shop_bands_v2_redirect();

// 4. House order on the main query, and the preload matches the first eager card.
check( array( 'the_posts', 'skyyrose2_shop_bands_v2_house_order', 20, 2 ) === sr2b_hook( 'the_posts', 'skyyrose2_shop_bands_v2_house_order' ), 'House order runs after Woo the_posts handlers (10)' );
$query = sr2b_reset();
$sku   = static fn( $posts ) => array_map( static fn( $post ) => $GLOBALS['sr2b_catalog'][ $post->ID ][0], $posts );
check( 'br-001' === $sku( $query->posts )[0], 'Fixture starts in native (menu_order) order with br-001 first' );
$before_hint = skyyrose2_performance_archive_front_preload();
check( str_ends_with( $before_hint['href'], 'br-001-640w.webp' ), 'Without house order the preload would name br-001 (the defect)' );
$query->posts = skyyrose2_shop_bands_v2_house_order( $query->posts, $query );
check( array( 'sg-013', 'sg-002', 'sg-003', 'br-001', 'br-002', 'lh-002', 'lh-003', 'kids-001', 'xx-001' ) === $sku( $query->posts ), 'Stable house order: collections in house order, native order kept inside each, ungrouped last' );
$hint = skyyrose2_performance_archive_front_preload();
check( str_ends_with( $hint['href'], 'sg-013-640w.webp' ) && 'high' === $hint['fetchpriority'] && skyyrose2_shop_card_sizes() === $hint['imagesizes'], 'Preload names the first band\'s first piece' );
$html  = sr2b_render();
check( 0 === wc_get_loop_prop( 'sr2_card_heading_level', 0 ), 'The band heading level is reset after the bands render' );
$args  = $GLOBALS['sr2b_band_args'];
$cards = $GLOBALS['sr2b_cards'];
$acts  = $GLOBALS['sr2b_actions'];
$first = $cards[0];
check( 'sg-013' === $first['sku'] && 0 === $first['index'] && 'high' === $first['priority'] && skyyrose2_shop_card_sizes() === $first['sizes'], 'First rendered card is the preloaded, eager, high-priority piece' );
check( 1 === count( array_filter( $cards, static fn( $card ) => 'high' === $card['priority'] ) ), 'Exactly one eager card across all bands' );
check( str_ends_with( skyyrose2_approved_card_front( wc_get_product( 2 ) )['card_src'], basename( $hint['href'] ) ), 'Hint href is the first card\'s approved front' );
foreach ( array( array( 'min_price' => '0' ), array( 'product_cat' => 'black-rose' ) ) as $get ) {
	$filtered        = sr2b_reset( $get );
	$native          = $filtered->posts;
	check( $native === skyyrose2_shop_bands_v2_house_order( $native, $filtered ), 'Filtered views keep the native query order' );
}
$secondary       = sr2b_reset();
$secondary->main = false;
check( $secondary->posts === skyyrose2_shop_bands_v2_house_order( $secondary->posts, $secondary ), 'Secondary queries are never reordered' );

// 5. Grouping: bands in house order, every piece reachable, ungrouped band, Kids type-led.
check( array( 'signature', 'black-rose', 'love-hurts', 'kids-capsule' ) === array_keys( $args['groups'] ), 'Groups follow house order' );
check( array( 'xx-001' ) === array_map( static fn( $p ) => $p->get_sku(), $args['ungrouped'] ), 'A piece outside the four collections is ungrouped, not dropped' );
check( 9 === count( $cards ) && array( 'sg-013', 'sg-002', 'sg-003', 'br-001', 'br-002', 'lh-002', 'lh-003', 'kids-001', 'xx-001' ) === array_column( $cards, 'sku' ), 'Every piece renders once, in band order' );
check( range( 0, 8 ) === array_column( $cards, 'index' ), 'One continuous native loop across bands' );
check( array_fill( 0, 9, 3 ) === array_column( $cards, 'heading_level' ), 'Grouped cards nest at h3 under their band h2 (WCAG 1.3.1)' );
preg_match_all( '/data-sr2bv2-band data-collection="([a-z-]+)" data-film="([a-z]+)"/', $html, $bands, PREG_SET_ORDER );
check( array( 'signature:cinema', 'black-rose:cinema', 'love-hurts:cinema', 'kids-capsule:type', 'house:type' ) === array_map( static fn( $b ) => $b[1] . ':' . $b[2], $bands ), 'Three film bands, Kids Capsule type-led, final house band' );
check( str_contains( $html, 'cinema-20261008/poster.webp' ) && str_contains( $html, 'data-src="' . SKYYROSE2_URI . '/assets/video/collection-heroes/approved/signature/cinema-20261008/hero.webm"' ), 'Film poster and data-src motion come through the media gate' );
check( ! str_contains( $html, 'kids-capsule/cinema-20261008' ), 'Kids Capsule requests no film' );
check( ! str_contains( $html, 'sr2-shop-world-note' ) && ! str_contains( $html, 'columns-4' ), 'Grouped view replaces the grid; no world note' );
check( in_array( 'woocommerce_after_shop_loop', $acts, true ) && ! in_array( 'woocommerce_no_products_found', $acts, true ), 'Grouped view keeps the native after-loop hook' );
check( 1 === substr_count( $html, '<h1 ' ) && str_contains( $html, 'All pieces' ), 'Arrival band is unchanged' );
// Film withheld by the media gate: every band falls back to the type-led header.
sr2b_reset();
$GLOBALS['sr2b']['withhold'] = true;
$withheld = sr2b_render();
check( 0 === substr_count( $withheld, 'data-film="cinema"' ) && ! str_contains( $withheld, '<video' ), 'Withheld films render the designed type-led bands' );
// Ungrouped fallback alone: pieces with no collection still render.
sr2b_reset( array(), array( 5 ) );
$only_house = sr2b_render();
check( str_contains( $only_house, 'data-collection="house"' ) && array( 'xx-001' ) === array_column( $GLOBALS['sr2b_cards'], 'sku' ), 'A catalog of only uncollected pieces is still reachable' );
check( 4 === substr_count( $only_house, 'sr2-bands-v2__quiet' ), 'Empty house collections keep their designed quiet state' );

// 6. Filtered views: the existing grid, world note at piece 8, native pagination hook.
sr2b_reset( array( 'min_price' => '0' ) );
$GLOBALS['woocommerce_loop']['total'] = 9;
$grid = sr2b_render();
check( ! str_contains( $grid, 'data-sr2bv2' ) && str_contains( $grid, 'columns-4' ) && 9 === count( $GLOBALS['sr2b_cards'] ), 'Filtered view renders the native grid' );
check( 'br-001' === $GLOBALS['sr2b_cards'][0]['sku'] && 'high' === $GLOBALS['sr2b_cards'][0]['priority'], 'Filtered grid keeps native order and its first eager card' );
check( array_fill( 0, 9, null ) === array_column( $GLOBALS['sr2b_cards'], 'heading_level' ), 'Filtered grid passes no heading level, so cards keep the archive h2 under the h1' );
$note = '<li class="sr2-shop-world-note"';
check( 1 === substr_count( $grid, $note ) && strpos( $grid, $note ) > strpos( $grid, 'data-sku="lh-003"' ) && strpos( $grid, $note ) < strpos( $grid, 'data-sku="sg-003"' ), 'World note stays before piece 9 (after piece 8)' );
check( str_contains( $grid, 'data-collection="black-rose"' ), 'World note names the first piece\'s world' );
check( in_array( 'woocommerce_after_shop_loop', $GLOBALS['sr2b_actions'], true ), 'Filtered grid keeps native pagination hook' );

// 7. Empty branch: unchanged no-results state on both views.
foreach ( array( array(), array( 'min_price' => '999999' ) ) as $get ) {
	sr2b_reset( $get, array() );
	$empty = sr2b_render();
	check( str_contains( $empty, 'sr2-shop-archive__empty' ) && str_contains( $empty, 'View all pieces' ) && ! str_contains( $empty, 'data-sr2bv2' ) && in_array( 'woocommerce_no_products_found', $GLOBALS['sr2b_actions'], true ), 'Empty results keep the native empty branch' );
}

// 8. Enqueue: own callback at priority 20, grouped view only, outside the small-style inliner.
foreach ( array( 'skyyrose2_asset_suffix', 'skyyrose2_asset_version', 'skyyrose2_shop_bands_v2_assets' ) as $name ) {
	$start = strpos( $functions, "function {$name}() {" );
	$start = false === $start ? strpos( $functions, "function {$name}( " ) : $start;
	check( false !== $start, "functions.php defines {$name}" );
	eval( substr( $functions, $start, strpos( $functions, "\n}\n", $start ) + 3 - $start ) ); // phpcs:ignore Squiz.PHP.Eval.Discouraged
}
check( 1 === substr_count( $functions, "add_action( 'wp_enqueue_scripts', 'skyyrose2_shop_bands_v2_assets', 20 );" ) && 1 === substr_count( $functions, "add_action( 'wp_enqueue_scripts', 'skyyrose2_assets' );" ), 'Bands enqueue in their own callback at 20, after skyyrose2_assets (10, mascot included)' );
function wp_enqueue_style( $handle, $src, $deps, $ver ) { $GLOBALS['sr2b_enqueued'][ $handle ] = compact( 'src', 'deps', 'ver' ); }
function wp_enqueue_script( $handle, $src, $deps, $ver, $footer ) { $GLOBALS['sr2b_enqueued'][ $handle . ':js' ] = compact( 'src', 'deps', 'ver', 'footer' ); }
$GLOBALS['sr2b_enqueued'] = array();
sr2b_reset( array( 'orderby' => 'price' ) );
skyyrose2_shop_bands_v2_assets();
$suffix = skyyrose2_asset_suffix();
$style  = $GLOBALS['sr2b_enqueued']['skyyrose2-shop-bands-v2'] ?? array();
$script = $GLOBALS['sr2b_enqueued']['skyyrose2-shop-bands-v2:js'] ?? array();
check( SKYYROSE2_URI . "/assets/css/shop-bands-v2{$suffix}.css" === ( $style['src'] ?? '' ) && array( 'skyyrose2-shop-page' ) === $style['deps'] && skyyrose2_asset_version( "/assets/css/shop-bands-v2{$suffix}.css" ) === $style['ver'], 'Stylesheet follows shop-page with the content-hash asset version' );
check( SKYYROSE2_URI . "/assets/js/shop-bands-v2{$suffix}.js" === ( $script['src'] ?? '' ) && array() === $script['deps'] && true === $script['footer'] && skyyrose2_asset_version( "/assets/js/shop-bands-v2{$suffix}.js" ) === $script['ver'], 'Controller loads in the footer with the content-hash asset version' );
check( str_starts_with( $style['ver'], SKYYROSE2_VERSION . '-' ) || SKYYROSE2_VERSION === $style['ver'], 'Asset version carries the theme version' );
foreach ( array( array( 'min_price' => '0' ), array( 'product_cat' => 'signature' ) ) as $get ) {
	$GLOBALS['sr2b_enqueued'] = array();
	sr2b_reset( $get );
	skyyrose2_shop_bands_v2_assets();
	check( array() === $GLOBALS['sr2b_enqueued'], 'Filtered views do not load the bands assets' );
}
$performance = file_get_contents( SKYYROSE2_DIR . '/inc/performance.php' );
$inliner     = substr( $performance, strpos( $performance, 'function skyyrose2_performance_inline_small_styles()' ), 2400 );
check( str_contains( $inliner, "'shop-page'               => 'shop-page'," ) && ! str_contains( $inliner, 'shop-bands' ), 'Bands stylesheet is not in the small-style inline list' );

// 9. REST is immutable; test it last in this process.
define( 'REST_REQUEST', true );
$query = sr2b_reset();
$query->set( 'posts_per_page', 16 );
skyyrose2_shop_bands_v2_query( $query );
check( ! skyyrose2_shop_bands_v2_active() && 16 === $query->get( 'posts_per_page' ), 'REST requests are never grouped' );
echo "PASS Shop cinema bands: predicate (15 filter combinations, layered nav, search, tax, admin, ajax, REST), one-page query, 301, house order, preload match, enqueue, grouping, ungrouped and withheld fallbacks, filtered grid and empty branch\n";
