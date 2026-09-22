<?php
/** Standalone contract tests for inc/performance.php. */

define( 'ABSPATH', __DIR__ . '/' );
define( 'SKYYROSE2_DIR', dirname( __DIR__ ) );
define( 'SKYYROSE2_URI', 'https://example.test/wp-content/themes/skyyrose-flagship-2' );

$GLOBALS['sr2_hooks']       = array();
$GLOBALS['sr2_route']       = array( 'front' => false, 'page' => false, 'single' => false, 'singular' => '' );
$GLOBALS['sr2_templates']   = array();
$GLOBALS['sr2_styles']      = array();
$GLOBALS['sr2_scripts']     = array();
$GLOBALS['sr2_strategies']  = array();
$GLOBALS['sr2_post_slug']   = '';
$GLOBALS['sr2_wp_style_registry'] = (object) array( 'queue' => array(), 'registered' => array() );

function add_action( $hook, $callback, $priority = 10, $accepted_args = 1 ) {
	$GLOBALS['sr2_hooks'][] = compact( 'hook', 'callback', 'priority', 'accepted_args' );
}
function add_filter( $hook, $callback, $priority = 10, $accepted_args = 1 ) {
	$GLOBALS['sr2_hooks'][] = compact( 'hook', 'callback', 'priority', 'accepted_args' );
}
function remove_action() {}
function remove_filter() {}
function apply_filters( $hook, $value ) { return $GLOBALS['sr2_filter_values'][ $hook ] ?? $value; }
function is_front_page() { return $GLOBALS['sr2_route']['front']; }
function is_shop() { return $GLOBALS['sr2_archive'] ?? false; }
function is_product_taxonomy() { return $GLOBALS['sr2_taxonomy'] ?? false; }
function is_page() { return $GLOBALS['sr2_route']['page']; }
function is_single() { return $GLOBALS['sr2_route']['single']; }
function is_singular( $type = '' ) { return $type ? $GLOBALS['sr2_route']['singular'] === $type : (bool) $GLOBALS['sr2_route']['singular']; }
function is_page_template( $templates ) { return (bool) array_intersect( (array) $templates, $GLOBALS['sr2_templates'] ); }
function skyyrose2_collection_page_slug() { return $GLOBALS['sr2_inferred_collection'] ?? ''; }
function is_user_logged_in() { return false; }
function wp_dequeue_style( $handle ) { $GLOBALS['sr2_styles'][] = $handle; }
function wp_dequeue_script( $handle ) { $GLOBALS['sr2_scripts'][] = $handle; }
function wp_script_add_data( $handle, $key, $value ) { $GLOBALS['sr2_strategies'][ $handle ][ $key ] = $value; }
function wp_styles() { return $GLOBALS['sr2_wp_style_registry']; }
function wp_style_add_data( $handle, $key, $value ) { $GLOBALS['sr2_wp_style_registry']->registered[ $handle ]->extra[ $key ] = $value; }
function wp_parse_url( $url, $component = -1 ) { return parse_url( $url, $component ); }
function sanitize_title( $value ) { return strtolower( trim( preg_replace( '/[^a-z0-9]+/i', '-', $value ), '-' ) ); }
function get_post_field() { return $GLOBALS['sr2_post_slug']; }
function get_queried_object_id() { return 123; }
function wp_get_attachment_metadata() { return array( 'width' => 1200, 'height' => 1500 ); }
function skyyrose2_sot_asset_uri( $path ) { return SKYYROSE2_URI . '/assets/sot/' . ltrim( $path, '/' ); }
function skyyrose2_collections() {
	return array(
		'signature' => array(
			'hero'        => 'images/hero/responsive/signature-golden-gate-monuments-v2-1440w.webp',
			'hero_tablet' => 'images/hero/responsive/signature-golden-gate-monuments-v2-1024w.webp',
			'hero_mobile' => 'images/hero/responsive/signature-golden-gate-monuments-v2-640w.webp',
		),
	);
}

$source = file_get_contents( dirname( __DIR__ ) . '/functions.php' );
$start = strpos( $source, '/** Explicit rollout boundary shared by template and asset consumers.' );
$end = strpos( $source, '/** One exact collection-route predicate', $start );
if ( false === $start || false === $end ) { throw new Exception( 'Missing arrival media contract' ); }
eval( substr( $source, $start, $end - $start ) );
require dirname( __DIR__ ) . '/inc/performance.php';

function sr2_assert( $condition, $message ) {
	if ( ! $condition ) {
		fwrite( STDERR, "FAIL: {$message}\n" );
		exit( 1 );
	}
}

$registered = array_column( $GLOBALS['sr2_hooks'], 'callback' );
sr2_assert( in_array( 'skyyrose2_performance_preload_resources', $registered, true ), 'preload filter is registered' );
sr2_assert( in_array( 'skyyrose2_performance_defer_scripts', $registered, true ), 'defer policy is registered' );
sr2_assert( ! in_array( 'skyyrose2_performance_defer_homepage_jquery', $registered, true ), 'theme does not request an unsafe homepage-only core strategy' );

$GLOBALS['sr2_route']['front'] = true;
$front                         = skyyrose2_performance_route_preloads();
sr2_assert( 3 === count( $front ), 'front page has three art-directed records' );
sr2_assert( 3 === count( array_unique( array_column( $front, 'media' ) ) ), 'front page media queries are mutually distinct' );
sr2_assert(
	3 === count(
		array_filter(
			$front,
			static function ( $item ) {
				return 'high' === $item['fetchpriority'];
			}
		)
	),
	'each active hero candidate is high priority'
);
foreach ( $front as $resource ) {
	$local = str_replace( SKYYROSE2_URI, SKYYROSE2_DIR, $resource['href'] );
	sr2_assert( is_readable( $local ), 'every front-page preload exists locally' );
}

$deduplicated = skyyrose2_performance_preload_resources( array( $front[0] ) );
sr2_assert( 3 === count( $deduplicated ), 'an existing hero href is not duplicated' );

$GLOBALS['sr2_route']['front'] = false;
$GLOBALS['sr2_templates']      = array( 'template-collection.php' );
$GLOBALS['sr2_post_slug']      = 'signature';
$collection                    = skyyrose2_performance_route_preloads();
sr2_assert( 1 === count( $collection ) && ! empty( $collection[0]['imagesrcset'] ), 'static Signature uses one matching responsive preload' );
sr2_assert( $collection[0]['imagesizes'] === skyyrose2_collection_arrival_media( skyyrose2_collections()['signature'] )['sizes'], 'image and preload share exact slot contract' );
$GLOBALS['sr2_templates'] = array();
$GLOBALS['sr2_inferred_collection'] = 'signature';
sr2_assert( $collection === skyyrose2_performance_route_preloads(), 'automatic collection route has identical matching hero hints' );
$GLOBALS['sr2_inferred_collection'] = '';
$GLOBALS['sr2_templates'] = array( 'template-collection.php' );

$attachment = (object) array( 'ID' => 9 );
$attributes = skyyrose2_performance_image_attributes(
	array( 'fetchpriority' => 'high', 'loading' => 'lazy', 'srcset' => 'one.webp 1200w' ),
	$attachment
);
sr2_assert( ! isset( $attributes['loading'] ), 'high-priority image is not lazy' );
sr2_assert( 1200 === $attributes['width'] && 1500 === $attributes['height'], 'attachment dimensions are restored' );
sr2_assert( isset( $attributes['sizes'] ), 'responsive attachment receives sizes fallback' );

$GLOBALS['sr2_styles']  = array();
$GLOBALS['sr2_scripts'] = array();
skyyrose2_performance_dequeue_unused_assets();
sr2_assert( in_array( 'wp-block-library', $GLOBALS['sr2_styles'], true ), 'governed route removes block CSS' );
sr2_assert( in_array( 'wp-embed', $GLOBALS['sr2_scripts'], true ), 'governed route removes wp-embed' );

$GLOBALS['sr2_templates']      = array();
$GLOBALS['sr2_route']['page'] = true;
$GLOBALS['sr2_styles']         = array();
$GLOBALS['sr2_scripts']        = array();
skyyrose2_performance_dequeue_unused_assets();
sr2_assert( ! in_array( 'wp-block-library', $GLOBALS['sr2_styles'], true ), 'ordinary content retains block CSS' );
sr2_assert( ! in_array( 'wp-embed', $GLOBALS['sr2_scripts'], true ), 'ordinary content retains wp-embed' );

skyyrose2_performance_defer_scripts();
sr2_assert( 'defer' === $GLOBALS['sr2_strategies']['skyyrose2-theme']['strategy'], 'theme runtime is deferred' );
sr2_assert( 'defer' === $GLOBALS['sr2_strategies']['skyyrose2-immersive']['strategy'], 'late immersive runtime is deferred' );
sr2_assert( ! isset( $GLOBALS['sr2_strategies']['wc-add-to-cart'] ), 'WooCommerce purchase scripts are untouched' );

// Editorial delivery may not remove native styles from transaction/content
// routes or the separately retained immersive templates. Verify the opt-in too.
foreach ( array( 'home', 'signature', 'black-rose', 'love-hurts', 'kids-capsule', 'shop', 'product', 'cart', 'checkout', 'account', 'content', 'immersive' ) as $route ) {
	$GLOBALS['sr2_route']['front'] = 'home' === $route;
	$GLOBALS['sr2_inferred_collection'] = in_array( $route, array( 'signature', 'black-rose', 'love-hurts', 'kids-capsule' ), true ) ? $route : '';
	$GLOBALS['sr2_templates'] = 'immersive' === $route ? array( 'template-immersive-signature.php' ) : array();
	foreach ( array( false, true ) as $native_required ) {
		$GLOBALS['sr2_filter_values']['skyyrose2_editorial_native_woo_styles'] = $native_required;
		$GLOBALS['sr2_styles'] = array();
		skyyrose2_performance_dequeue_unused_assets();
		$expected = ! $native_required && ( 'home' === $route || (bool) $GLOBALS['sr2_inferred_collection'] );
		foreach ( array( 'woocommerce-general', 'woocommerce-layout', 'woocommerce-smallscreen' ) as $handle ) {
			sr2_assert( $expected === in_array( $handle, $GLOBALS['sr2_styles'], true ), 'native Woo CSS boundary: ' . $route . ' / ' . $handle );
		}
	}
}
$GLOBALS['sr2_filter_values'] = array();
$GLOBALS['sr2_templates'] = array();

// Theme archive grid replaces only Woo layout; native forms/notices remain.
$GLOBALS['sr2_route']['front'] = false;
$GLOBALS['sr2_inferred_collection'] = '';
foreach ( array( 'shop', 'taxonomy' ) as $archive ) {
	$GLOBALS['sr2_archive'] = 'shop' === $archive;
	$GLOBALS['sr2_taxonomy'] = 'taxonomy' === $archive;
	foreach ( array( false, true ) as $native_required ) {
		$GLOBALS['sr2_filter_values']['skyyrose2_archive_native_woo_layout'] = $native_required;
		$GLOBALS['sr2_styles'] = array();
		skyyrose2_performance_dequeue_unused_assets();
		sr2_assert( ! in_array( 'woocommerce-general', $GLOBALS['sr2_styles'], true ), 'archive retains native controls and notices' );
		foreach ( array( 'woocommerce-layout', 'woocommerce-smallscreen' ) as $handle ) {
			sr2_assert( ! $native_required === in_array( $handle, $GLOBALS['sr2_styles'], true ), 'archive layout opt-in: ' . $archive . ' / ' . $handle );
		}
	}
}
$GLOBALS['sr2_archive'] = false;
$GLOBALS['sr2_taxonomy'] = false;
$GLOBALS['sr2_filter_values'] = array();
$GLOBALS['sr2_inferred_collection'] = '';

foreach ( array( false, true ) as $is_front ) {
	$GLOBALS['sr2_route']['front'] = $is_front;
	$GLOBALS['sr2_strategies'] = array();
	foreach ( $GLOBALS['sr2_hooks'] as $hook ) {
		if ( 'wp_enqueue_scripts' === $hook['hook'] ) {
			call_user_func( $hook['callback'] );
		}
	}
	foreach ( array( 'jquery', 'jquery-core', 'jquery-migrate', 'jquery-blockui', 'wc-add-to-cart' ) as $handle ) {
		sr2_assert( ! isset( $GLOBALS['sr2_strategies'][ $handle ] ), 'plugin dependency strategies remain WordPress-owned: ' . $handle );
	}
	sr2_assert( 'defer' === $GLOBALS['sr2_strategies']['skyyrose2-theme']['strategy'], 'theme optimization remains active on every route' );
}

// Product preload may never bypass rejected/editorial resolver authority.
function wc_get_product( $id ) { return (object) array( 'id' => $id ); }
function skyyrose2_product_commerce_media( $product ) { return $GLOBALS['sr2_test_media']; }
function wp_get_attachment_image_src( $id, $size ) { return array( 'https://example.test/media/' . $id . '.webp', 640, 960 ); }
function wp_get_attachment_image_srcset( $id, $size ) { return false; }
$GLOBALS['sr2_route'] = array( 'front' => false, 'page' => false, 'single' => false, 'singular' => 'product' );
$GLOBALS['sr2_templates'] = array();
$GLOBALS['sr2_test_media'] = array( 'state' => 'editorial', 'ids' => array( 77, 78 ) );
$resolved_preload = skyyrose2_performance_route_preloads();
sr2_assert( 1 === count( $resolved_preload ) && str_contains( $resolved_preload[0]['href'], '/77.webp' ), 'PDP preload uses resolved primary, not arbitrary native attachment' );
$GLOBALS['sr2_test_media'] = array( 'state' => 'rejected', 'ids' => array() );
sr2_assert( array() === skyyrose2_performance_route_preloads(), 'Rejected PDP has no product image preload' );
$GLOBALS['sr2_test_media'] = array( 'state' => 'missing', 'ids' => array() );
sr2_assert( array() === skyyrose2_performance_route_preloads(), 'Missing PDP has no fictional preload' );

// Core owns the inline budget, cascade and URL normalization. Only exact small
// theme files may opt in; external replacements and media variants remain links.
$style_cases = array(
	'skyyrose2-tokens' => array( 'design-tokens.min.css', 'all', array() ),
	'skyyrose2-theme' => array( 'theme.min.css', 'all', array() ),
	'skyyrose2-controls' => array( 'controls.min.css', 'print', array() ),
	'skyyrose2-global-shell' => array( 'global-shell.min.css', 'all', array( 'rtl' => 'replace' ) ),
	'skyyrose2-visual-recovery' => array( 'visual-recovery.min.css', 'all', array( 'after' => array( '.extension { color: red; }' ) ) ),
	'woocommerce-general' => array( 'design-tokens.min.css', 'all', array() ),
);
foreach ( $style_cases as $handle => $case ) {
	$GLOBALS['sr2_wp_style_registry']->queue[] = $handle;
	$GLOBALS['sr2_wp_style_registry']->registered[ $handle ] = (object) array( 'src' => SKYYROSE2_URI . '/assets/css/' . $case[0], 'args' => $case[1], 'extra' => $case[2] );
}
skyyrose2_performance_inline_small_styles();
$styles = $GLOBALS['sr2_wp_style_registry']->registered;
sr2_assert( SKYYROSE2_DIR . '/assets/css/design-tokens.min.css' === $styles['skyyrose2-tokens']->extra['path'], 'exact small tokens opt into native inline delivery' );
sr2_assert( isset( $styles['skyyrose2-visual-recovery']->extra['path'] ) && array( '.extension { color: red; }' ) === $styles['skyyrose2-visual-recovery']->extra['after'], 'attached extension CSS remains intact and after its source' );
foreach ( array( 'skyyrose2-theme', 'skyyrose2-controls', 'skyyrose2-global-shell', 'woocommerce-general' ) as $handle ) {
	sr2_assert( ! isset( $styles[ $handle ]->extra['path'] ), 'large, alternate-media, RTL and plugin styles remain external: ' . $handle );
}
$styles['skyyrose2-theme']->src = SKYYROSE2_URI . '/assets/css/archive-theme.min.css';
skyyrose2_performance_inline_small_styles();
sr2_assert( SKYYROSE2_DIR . '/assets/css/archive-theme.min.css' === ( $styles['skyyrose2-theme']->extra['path'] ?? '' ), 'exact bounded archive projection is offered to Core without changing its total budget' );
unset( $styles['skyyrose2-theme']->extra['path'] );
$styles['skyyrose2-theme']->src = SKYYROSE2_URI . '/assets/css/theme.min.css';
unset( $styles['skyyrose2-tokens']->extra['path'] );
$styles['skyyrose2-tokens']->src = 'https://cdn.example.test/replaced.css';
skyyrose2_performance_inline_small_styles();
sr2_assert( ! isset( $styles['skyyrose2-tokens']->extra['path'] ), 'an extension-replaced URL is not bypassed by a local path' );
$styles['skyyrose2-tokens']->src = SKYYROSE2_URI . '/assets/css/design-tokens.min.css';
$GLOBALS['sr2_filter_values']['skyyrose2_inline_small_styles'] = false;
skyyrose2_performance_inline_small_styles();
sr2_assert( ! isset( $styles['skyyrose2-tokens']->extra['path'] ), 'deployment opt-out preserves normal external delivery' );
sr2_assert( ! in_array( 'styles_inline_size_limit', array_column( $GLOBALS['sr2_hooks'], 'hook' ), true ), 'theme does not enlarge or replace the native total inline budget' );
fwrite( STDOUT, "PASS performance contract\n" );
