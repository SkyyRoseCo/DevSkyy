<?php
/**
 * Dependency-free contract tests for inc/seo-indexing.php.
 *
 * Run: php scripts/test-seo-indexing.php
 */

define( 'ABSPATH', __DIR__ . '/' );

$skyyrose2_test_actions  = array();
$skyyrose2_test_filters  = array();
$skyyrose2_test_removed  = array();
$skyyrose2_test_context  = array(
	'environment'   => 'production',
	'home'          => 'https://skyyrose.co/',
	'preview'       => false,
	'search'        => false,
	'cart'          => false,
	'checkout'      => false,
	'account'       => false,
	'page'          => false,
	'not_found'     => false,
	'singular'      => false,
	'canonical'     => '',
);

class WP_Post {
	public $ID;
	public function __construct( $post_id ) {
		$this->ID = $post_id;
	}
}

function add_action( $hook, $callback, $priority = 10 ) {
	global $skyyrose2_test_actions;
	$skyyrose2_test_actions[] = compact( 'hook', 'callback', 'priority' );
}
function add_filter( $hook, $callback, $priority = 10, $accepted_args = 1 ) {
	global $skyyrose2_test_filters;
	$skyyrose2_test_filters[] = compact( 'hook', 'callback', 'priority', 'accepted_args' );
}
function remove_action( $hook, $callback, $priority = 10 ) {
	global $skyyrose2_test_removed;
	$skyyrose2_test_removed[] = compact( 'hook', 'callback', 'priority' );
}
function wp_get_environment_type() {
	global $skyyrose2_test_context;
	return $skyyrose2_test_context['environment'];
}
function home_url( $path = '' ) {
	global $skyyrose2_test_context;
	return rtrim( $skyyrose2_test_context['home'], '/' ) . '/' . ltrim( $path, '/' );
}
function wp_parse_url( $url, $component = -1 ) {
	return parse_url( $url, $component );
}
function sanitize_text_field( $value ) {
	return trim( strip_tags( $value ) );
}
function wp_unslash( $value ) {
	return stripslashes( $value );
}
function is_preview() {
	global $skyyrose2_test_context;
	return $skyyrose2_test_context['preview'];
}
function is_search() {
	global $skyyrose2_test_context;
	return $skyyrose2_test_context['search'];
}
function is_cart() {
	global $skyyrose2_test_context;
	return $skyyrose2_test_context['cart'];
}
function is_checkout() {
	global $skyyrose2_test_context;
	return $skyyrose2_test_context['checkout'];
}
function is_account_page() {
	global $skyyrose2_test_context;
	return $skyyrose2_test_context['account'];
}
function is_404() {
	global $skyyrose2_test_context;
	return $skyyrose2_test_context['not_found'];
}
function is_singular( $post_type = '' ) {
	global $skyyrose2_test_context;
	return $skyyrose2_test_context['singular'];
}
function is_front_page() {
	return false;
}
function is_page() {
	global $skyyrose2_test_context;
	return $skyyrose2_test_context['page'];
}
function sanitize_title( $value ) {
	return strtolower( trim( preg_replace( '/[^a-z0-9]+/i', '-', $value ), '-' ) );
}
function get_post_field( $field, $post_id ) {
	if ( 'post_name' === $field ) {
		return 'faq';
	}
	if ( 'post_content' === $field ) {
		return '<details><summary>Merchant size question?</summary><p>Merchant size answer.</p></details>';
	}
	return '';
}
function skyyrose2_marketplace_pages() {
	return array(
		'faq' => array(
			'content' => '<!-- wp:heading --><h2 class="wp-block-heading">Canonical size question?</h2><!-- /wp:heading --><!-- wp:paragraph --><p>Canonical registry answer.</p><!-- /wp:paragraph -->',
		),
	);
}
function get_query_var( $key ) {
	return 0;
}
function get_queried_object_id() {
	return 42;
}
function wp_get_canonical_url( $post_id ) {
	global $skyyrose2_test_context;
	return $skyyrose2_test_context['canonical'];
}
function get_permalink( $post_id = 0 ) {
	return 'https://skyyrose.co/story/';
}
function wp_strip_all_tags( $value ) {
	return strip_tags( $value );
}
function strip_shortcodes( $value ) {
	return preg_replace( '/\[[^\]]+\]/', '', $value );
}
function esc_url_raw( $value ) {
	return filter_var( $value, FILTER_SANITIZE_URL );
}
function wc_get_page_id( $page_key ) {
	return array( 'cart' => 10, 'checkout' => 11, 'myaccount' => 12 )[ $page_key ] ?? -1;
}
function get_page_by_path( $path ) {
	return 'wishlist' === $path ? new WP_Post( 13 ) : null;
}

require dirname( __DIR__ ) . '/inc/seo-indexing.php';

$skyyrose2_test_failures = array();
function skyyrose2_test_assert( $condition, $message ) {
	global $skyyrose2_test_failures;
	if ( ! $condition ) {
		$skyyrose2_test_failures[] = $message;
	}
}

skyyrose2_test_assert(
	in_array(
		array( 'hook' => 'after_setup_theme', 'callback' => 'skyyrose2_seo_indexing_bootstrap', 'priority' => 99 ),
		$skyyrose2_test_actions,
		true
	),
	'Adapter must bootstrap after the theme has registered legacy hooks.'
);

skyyrose2_seo_indexing_bootstrap();
skyyrose2_test_assert(
	in_array( array( 'hook' => 'wp_head', 'callback' => 'skyyrose2_seo_head', 'priority' => 4 ), $skyyrose2_test_removed, true ),
	'Legacy social metadata hook was not removed.'
);
skyyrose2_test_assert(
	in_array( array( 'hook' => 'wp_head', 'callback' => 'skyyrose2_schema_head', 'priority' => 5 ), $skyyrose2_test_removed, true ),
	'Legacy schema hook was not removed.'
);
skyyrose2_test_assert(
	in_array( array( 'hook' => 'wp_sitemaps_posts_query_args', 'callback' => 'skyyrose2_seo_sitemap_query_args', 'priority' => 20, 'accepted_args' => 2 ), $skyyrose2_test_filters, true ),
	'Native sitemap exclusion filter was not registered.'
);

$skyyrose2_test_context['environment'] = 'local';
skyyrose2_test_assert( skyyrose2_seo_is_nonproduction_request(), 'Local environment must fail closed.' );
$robots = skyyrose2_seo_robots( array( 'index' => true, 'follow' => true ) );
skyyrose2_test_assert( isset( $robots['noindex'], $robots['nofollow'] ) && ! isset( $robots['index'], $robots['follow'] ), 'Local robots directives must be noindex,nofollow.' );
$headers = skyyrose2_seo_headers( array() );
skyyrose2_test_assert( 'noindex, nofollow, noarchive' === ( $headers['X-Robots-Tag'] ?? '' ), 'Local responses need an X-Robots-Tag safeguard.' );
skyyrose2_test_assert( 'User-agent: *' === skyyrose2_seo_robots_txt( 'User-agent: *', true ), 'Local robots.txt must not advertise a sitemap.' );

$skyyrose2_test_context['environment'] = 'production';
$skyyrose2_test_context['home']        = 'https://skyyrose.co/';
$_SERVER['HTTP_HOST']                  = 'skyyrose.co';
skyyrose2_test_assert( ! skyyrose2_seo_is_nonproduction_request(), 'Public production hostname was incorrectly treated as preview.' );
$robots = skyyrose2_seo_robots( array() );
skyyrose2_test_assert( 'large' === ( $robots['max-image-preview'] ?? '' ) && ! isset( $robots['noindex'] ), 'Public routes must remain indexable and allow large previews.' );
skyyrose2_test_assert( str_contains( skyyrose2_seo_robots_txt( 'User-agent: *', true ), 'Sitemap: https://skyyrose.co/wp-sitemap.xml' ), 'Public robots.txt must advertise the native sitemap.' );
$sitemap_args = skyyrose2_seo_sitemap_query_args( array( 'post__not_in' => array( 9 ) ), 'page' );
skyyrose2_test_assert( array( 9, 10, 11, 12, 13 ) === $sitemap_args['post__not_in'], 'Native sitemap must preserve exclusions and omit transactional pages.' );

$skyyrose2_test_context['search'] = true;
$robots = skyyrose2_seo_robots( array( 'index' => true ) );
skyyrose2_test_assert( isset( $robots['noindex'], $robots['follow'] ) && ! isset( $robots['index'] ), 'Search routes must be noindex,follow.' );
$skyyrose2_test_context['search'] = false;
$skyyrose2_test_context['cart']   = true;
$robots = skyyrose2_seo_robots( array( 'index' => true, 'follow' => true ) );
skyyrose2_test_assert( isset( $robots['noindex'], $robots['nofollow'] ), 'Cart must be noindex,nofollow.' );
skyyrose2_test_assert( array() === skyyrose2_seo_schema_graph(), 'Transactional routes must not emit schema.' );
$skyyrose2_test_context['cart'] = false;
$skyyrose2_test_context['singular']  = true;
$skyyrose2_test_context['canonical'] = 'https://skyyrose.co/story/2/';
skyyrose2_test_assert( 'https://skyyrose.co/story/2/' === skyyrose2_seo_canonical_url(), 'Singular canonical must preserve WordPress multipage routing.' );
$skyyrose2_test_context['singular'] = false;

$excerpt = skyyrose2_seo_excerpt( '<p>Actual   authored [shortcode] text.</p>', 158 );
skyyrose2_test_assert( 'Actual authored text.' === $excerpt, 'Metadata text normalization changed authored copy incorrectly.' );

$source = file_get_contents( dirname( __DIR__ ) . '/inc/seo-indexing.php' );
skyyrose2_test_assert( 0 === preg_match( "/'@type'\s*=>\s*'Product'/", $source ), 'Theme adapter must never emit Product schema.' );
skyyrose2_test_assert( str_contains( $source, "defined( 'AIOSEO_VERSION' )" ), 'AIOSEO ownership detection is missing.' );
skyyrose2_test_assert( str_contains( $source, "'FAQPage'" ), 'FAQ schema contract is missing.' );
skyyrose2_test_assert( str_contains( $source, "'CollectionPage'" ), 'Collection schema contract is missing.' );

$theme_source = file_get_contents( dirname( __DIR__ ) . '/functions.php' );
$function_names = static function ( $php_source ) {
	$names  = array();
	$tokens = token_get_all( $php_source );
	$count  = count( $tokens );
	for ( $index = 0; $index < $count; $index++ ) {
		if ( is_array( $tokens[ $index ] ) && T_FUNCTION === $tokens[ $index ][0] ) {
			for ( $cursor = $index + 1; $cursor < $count; $cursor++ ) {
				if ( is_array( $tokens[ $cursor ] ) && T_STRING === $tokens[ $cursor ][0] ) {
					$names[] = $tokens[ $cursor ][1];
					break;
				}
				if ( '(' === $tokens[ $cursor ] ) {
					break;
				}
			}
		}
	}
	return $names;
};
$collisions = array_intersect( $function_names( $theme_source ), $function_names( $source ) );
skyyrose2_test_assert( array() === array_values( $collisions ), 'Adapter redeclares active theme functions: ' . implode( ', ', $collisions ) );

// The active SEO adapter must use the same permitted primary as the PDP.
function get_bloginfo( $key ) { return 'SkyyRose'; }
function apply_filters( $name, $value ) { return $value; }
$skyyrose2_test_context['page'] = true;
$faq_entries = skyyrose2_seo_faq_entries();
skyyrose2_test_assert(
	array( array( 'question' => 'Merchant size question?', 'answer' => 'Merchant size answer.' ) ) === $faq_entries,
	'FAQ schema must reflect visible merchant content, never bundled defaults.'
);
$skyyrose2_test_context['page'] = false;
function wc_get_product( $id ) { return new class {
	public function get_name() { return 'Test garment'; }
	public function get_short_description() { return 'Authoritative product copy.'; }
	public function get_description() { return ''; }
	public function get_image_id() { throw new RuntimeException( 'Raw attachment bypassed resolver' ); }
}; }
function skyyrose2_product_commerce_media( $product ) { return $GLOBALS['sr2_seo_test_media']; }
function wp_get_attachment_image_url( $id, $size ) { return 'https://example.test/' . $id . '.webp'; }
$skyyrose2_test_context['singular'] = true;
$GLOBALS['sr2_seo_test_media'] = array( 'state' => 'editorial', 'ids' => array( 77 ) );
skyyrose2_test_assert( 'https://example.test/77.webp' === skyyrose2_seo_resolved_context()['image'], 'SEO must use the resolved product image.' );
$GLOBALS['sr2_seo_test_media'] = array( 'state' => 'rejected', 'ids' => array() );
skyyrose2_test_assert( '' === skyyrose2_seo_resolved_context()['image'], 'Rejected media cannot return through social metadata.' );
$skyyrose2_test_context['singular'] = false;
define( 'AIOSEO_VERSION', 'test' );
skyyrose2_test_assert( skyyrose2_seo_has_authority_plugin(), 'Supported SEO plugins must become the sole metadata/schema authority.' );
skyyrose2_test_assert( 'User-agent: *' === skyyrose2_seo_robots_txt( 'User-agent: *', true ), 'Theme must defer sitemap advertising to the active SEO plugin.' );
skyyrose2_test_assert( array() === skyyrose2_seo_schema_graph(), 'Theme schema must be silent under an authority plugin.' );
ob_start();
skyyrose2_seo_render_meta();
skyyrose2_seo_render_schema();
skyyrose2_test_assert( '' === ob_get_clean(), 'Theme head output must be silent under an authority plugin.' );

if ( $skyyrose2_test_failures ) {
	fwrite( STDERR, "FAIL SEO/indexing contract\n- " . implode( "\n- ", $skyyrose2_test_failures ) . "\n" );
	exit( 1 );
}

echo "PASS SEO/indexing contract: preview fail-closed, public sitemap/indexing, transactional/search noindex, legacy hook replacement, and Woo Product ownership.\n";
