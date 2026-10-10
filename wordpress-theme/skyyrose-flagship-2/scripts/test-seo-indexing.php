<?php
/**
 * Dependency-free contract tests for inc/seo-indexing.php.
 *
 * Run: php scripts/test-seo-indexing.php
 */

define( 'ABSPATH', __DIR__ . '/' );

$skyyrose2_test_actions = array();
$skyyrose2_test_filters = array();
$skyyrose2_test_removed = array();
$skyyrose2_test_context = array(
	'environment'     => 'production',
	'home'            => 'https://skyyrose.co/',
	'preview'         => false,
	'search'          => false,
	'cart'            => false,
	'checkout'        => false,
	'account'         => false,
	'page'            => false,
	'not_found'       => false,
	'singular'        => false,
	'post_type'       => 'product',
	'single'          => false,
	'canonical'       => '',
	'native_sitemaps' => true,
);

class SkyyRose2_Test_Sitemap_Server {
	public function sitemaps_enabled() {
		global $skyyrose2_test_context;
		return $skyyrose2_test_context['native_sitemaps'];
	}
}
function wp_sitemaps_get_server() {
	return new SkyyRose2_Test_Sitemap_Server();
}
function is_home() {
	return false;
}
function is_category() {
	return false;
}
function is_tag() {
	return false;
}
function is_tax() {
	return false;
}
function is_post_type_archive() {
	return false;
}
function post_type_exists( $post_type ) {
	return 'product' === $post_type;
}
function get_pagenum_link( $paged, $escape = true ) {
	global $skyyrose2_test_context;
	$skyyrose2_test_context['pagenum_escape_arg'] = $escape;
	$link = $skyyrose2_test_context['pagenum_link'] ?? 'https://skyyrose.co/shop/page/' . $paged . '/?cb=123&utm_source=x';
	return $escape ? str_replace( '&', '&#038;', $link ) : $link;
}

class Jetpack_SEO_Posts {
	public static $noindex = array();
	public static function get_post_noindex_setting( $post_id ) {
		return ! empty( self::$noindex[ $post_id ] );
	}
}

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
	return $skyyrose2_test_context['singular'] && ( ! $post_type || $post_type === $skyyrose2_test_context['post_type'] );
}
function is_single() {
	return $GLOBALS['skyyrose2_test_context']['single']; }
function is_archive() {
	return false; }
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
	return array(
		'cart'      => 10,
		'checkout'  => 11,
		'myaccount' => 12,
	)[ $page_key ] ?? -1;
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
		array(
			'hook'     => 'after_setup_theme',
			'callback' => 'skyyrose2_seo_indexing_bootstrap',
			'priority' => 99,
		),
		$skyyrose2_test_actions,
		true
	),
	'Adapter must bootstrap after the theme has registered legacy hooks.'
);

skyyrose2_seo_indexing_bootstrap();
skyyrose2_test_assert(
	in_array(
		array(
			'hook'     => 'wp_head',
			'callback' => 'skyyrose2_seo_head',
			'priority' => 4,
		),
		$skyyrose2_test_removed,
		true
	),
	'Legacy social metadata hook was not removed.'
);
skyyrose2_test_assert(
	in_array(
		array(
			'hook'     => 'wp_head',
			'callback' => 'skyyrose2_schema_head',
			'priority' => 5,
		),
		$skyyrose2_test_removed,
		true
	),
	'Legacy schema hook was not removed.'
);
skyyrose2_test_assert(
	in_array(
		array(
			'hook'          => 'wp_sitemaps_posts_query_args',
			'callback'      => 'skyyrose2_seo_sitemap_query_args',
			'priority'      => 20,
			'accepted_args' => 1,
		),
		$skyyrose2_test_filters,
		true
	),
	'Native sitemap exclusion filter was not registered.'
);

$skyyrose2_test_context['environment'] = 'local';
skyyrose2_test_assert( skyyrose2_seo_is_nonproduction_request(), 'Local environment must fail closed.' );
$robots = skyyrose2_seo_robots(
	array(
		'index'  => true,
		'follow' => true,
	)
);
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
$skyyrose2_test_context['native_sitemaps'] = false;
skyyrose2_test_assert( 'User-agent: *' === skyyrose2_seo_robots_txt( 'User-agent: *', true ), 'robots.txt must not advertise /wp-sitemap.xml while native sitemaps are disabled (Jetpack serves /sitemap.xml).' );
$skyyrose2_test_context['native_sitemaps'] = true;
$robots_with_generator                     = "User-agent: *\nSitemap: https://skyyrose.co/sitemap.xml";
skyyrose2_test_assert( $robots_with_generator === skyyrose2_seo_robots_txt( $robots_with_generator, true ), 'A second sitemap generator must never be advertised.' );
$sitemap_args = skyyrose2_seo_sitemap_query_args( array( 'post__not_in' => array( 9 ) ), 'page' );
skyyrose2_test_assert( array( 9, 10, 11, 12, 13 ) === $sitemap_args['post__not_in'], 'Native sitemap must preserve exclusions and omit transactional pages.' );
$sitemap_args = skyyrose2_seo_sitemap_query_args( array(), 'post' );
skyyrose2_test_assert( array( 10, 11, 12, 13 ) === $sitemap_args['post__not_in'], 'Excluded records apply to every native sitemap post type.' );
skyyrose2_test_assert( false === skyyrose2_seo_sitemap_provider( (object) array(), 'users' ) && is_object( skyyrose2_seo_sitemap_provider( (object) array(), 'posts' ) ), 'Native users sitemap must be dropped; other providers untouched.' );
skyyrose2_test_assert( array( 'post', 'page', 'product' ) === skyyrose2_seo_jetpack_sitemap_post_types( array( 'post', 'page' ) ), 'Jetpack sitemap must list WooCommerce products.' );
skyyrose2_test_assert( skyyrose2_seo_jetpack_sitemap_skip( false, (object) array( 'ID' => 11 ) ), 'Jetpack sitemap must skip the checkout page.' );
skyyrose2_test_assert( ! skyyrose2_seo_jetpack_sitemap_skip( false, (object) array( 'ID' => 42 ) ), 'Jetpack sitemap must keep public records.' );
skyyrose2_test_assert( skyyrose2_seo_jetpack_sitemap_skip( true, (object) array( 'ID' => 42 ) ), 'Jetpack skip decisions already made are preserved.' );
skyyrose2_test_assert(
	skyyrose2_seo_jetpack_sitemap_image_skip(
		false,
		(object) array(
			'ID'          => 900,
			'post_parent' => 11,
		)
	),
	'Image sitemap must skip images attached to the checkout page.'
);
skyyrose2_test_assert(
	! skyyrose2_seo_jetpack_sitemap_image_skip(
		false,
		(object) array(
			'ID'          => 11,
			'post_parent' => 42,
		)
	),
	'Image sitemap must test the parent, not the attachment ID.'
);
skyyrose2_test_assert(
	! skyyrose2_seo_jetpack_sitemap_image_skip(
		false,
		(object) array(
			'ID'          => 901,
			'post_parent' => 0,
		)
	),
	'Unattached images are kept.'
);
skyyrose2_test_assert(
	skyyrose2_seo_jetpack_sitemap_image_skip(
		true,
		(object) array(
			'ID'          => 902,
			'post_parent' => 42,
		)
	),
	'Earlier image skip decisions are preserved.'
);
skyyrose2_test_assert( false === skyyrose2_seo_jetpack_metadata_enabled( true ), 'Jetpack Open Graph / SEO meta tags must be silent while the theme renders metadata.' );
skyyrose2_test_assert( 'https://skyyrose.co/shop/page/2/' === skyyrose2_seo_pagenum_url( 2 ), 'Paginated canonical must drop request query parameters.' );
$skyyrose2_test_context['pagenum_link'] = 'https://skyyrose.co/?paged=3&cb=9';
skyyrose2_test_assert( 'https://skyyrose.co/?paged=3' === skyyrose2_seo_pagenum_url( 3 ), 'Plain-permalink pagination must keep only the paged parameter.' );
skyyrose2_test_assert( false === $skyyrose2_test_context['pagenum_escape_arg'], 'Pagination canonical must request the unescaped pagenum link.' );
$skyyrose2_test_context['pagenum_link'] = 'https://skyyrose.co/?post_type=product&paged=3';
skyyrose2_test_assert( 'https://skyyrose.co/?post_type=product&paged=3' === skyyrose2_seo_pagenum_url( 3 ), 'Plain-permalink product archive must keep post_type and paged.' );
$skyyrose2_test_context['pagenum_link'] = 'https://skyyrose.co/?cat=7&paged=2';
skyyrose2_test_assert( 'https://skyyrose.co/?cat=7&paged=2' === skyyrose2_seo_pagenum_url( 2 ), 'Plain-permalink category archive must keep cat and paged.' );
$skyyrose2_test_context['pagenum_link'] = 'https://skyyrose.co/?utm_source=x&cat=7&cb=9&paged=2';
skyyrose2_test_assert( 'https://skyyrose.co/?cat=7&paged=2' === skyyrose2_seo_pagenum_url( 2 ), 'Tracking and cache-buster parameters must be dropped beside archive parameters.' );
$skyyrose2_test_context['pagenum_link'] = 'https://skyyrose.co/?post_type=product&utm_campaign=a&paged=3';
skyyrose2_test_assert( 'https://skyyrose.co/?post_type=product&paged=3' === skyyrose2_seo_pagenum_url( 3 ), 'An extra utm parameter must not reach the canonical.' );
$skyyrose2_test_context['pagenum_link'] = 'https://skyyrose.co/?utm_source=x&paged=4';
skyyrose2_test_assert( 'https://skyyrose.co/?paged=4' === skyyrose2_seo_pagenum_url( 4 ), 'Escaped-separator hazard: paged must survive beside another parameter.' );
unset( $skyyrose2_test_context['pagenum_link'] );
$image_filter = array_values( array_filter( $skyyrose2_test_filters, static fn( $f ) => 'jetpack_sitemap_image_skip_post' === $f['hook'] ) );
skyyrose2_test_assert( 'skyyrose2_seo_jetpack_sitemap_image_skip' === $image_filter[0]['callback'], 'Image sitemap must use its own parent-checking callback.' );
foreach ( array( 'wp_sitemaps_add_provider', 'jetpack_sitemap_post_types', 'jetpack_sitemap_skip_post', 'jetpack_sitemap_image_skip_post', 'jetpack_enable_open_graph', 'jetpack_seo_meta_tags_enabled', 'jetpack_seo_custom_titles' ) as $hook ) {
	skyyrose2_test_assert( in_array( $hook, array_column( $skyyrose2_test_filters, 'hook' ), true ), "Filter {$hook} was not registered." );
}
skyyrose2_test_assert( '' === skyyrose2_seo_resolved_context()['description'], 'The WordPress tagline must never become a meta description (no tagline is authorised).' );
skyyrose2_test_assert( ! str_contains( file_get_contents( dirname( __DIR__ ) . '/inc/seo-indexing.php' ), "get_bloginfo( 'description' )" ), 'Adapter must not read the tagline option.' );

$skyyrose2_test_context['search'] = true;
$robots                           = skyyrose2_seo_robots( array( 'index' => true ) );
skyyrose2_test_assert( isset( $robots['noindex'], $robots['follow'] ) && ! isset( $robots['index'] ), 'Search routes must be noindex,follow.' );
$skyyrose2_test_context['search'] = false;
$skyyrose2_test_context['cart']   = true;
$robots                           = skyyrose2_seo_robots(
	array(
		'index'  => true,
		'follow' => true,
	)
);
skyyrose2_test_assert( isset( $robots['noindex'], $robots['nofollow'] ), 'Cart must be noindex,nofollow.' );
skyyrose2_test_assert( array() === skyyrose2_seo_schema_graph(), 'Transactional routes must not emit schema.' );
$skyyrose2_test_context['cart']      = false;
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

$theme_source   = file_get_contents( dirname( __DIR__ ) . '/functions.php' );
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
$collisions     = array_intersect( $function_names( $theme_source ), $function_names( $source ) );
skyyrose2_test_assert( array() === array_values( $collisions ), 'Adapter redeclares active theme functions: ' . implode( ', ', $collisions ) );

// The active SEO adapter must use the same permitted primary as the PDP.
function get_bloginfo( $key ) {
	return 'SkyyRose'; }
function apply_filters( $name, $value ) {
	if ( 'skyyrose2_seo_context' === $name && isset( $GLOBALS['sr2_seo_image_override'] ) ) {
		$value['image'] = $GLOBALS['sr2_seo_image_override']; }
	return $value;
}
// Explicit offline URL eligibility fixture. No prefix-wide or allow-all bypass.
$GLOBALS['sr2_seo_allowed_urls'] = array(
	'https://example.test/77.webp',
	'https://example.test/v2/current-sku-front.webp',
	'https://skyyrose.co/wp-content/themes/skyyrose-flagship-2/assets/test/current-article.webp',
);
function skyyrose2_media_url( $url ) {
	return is_string( $url ) && in_array( $url, $GLOBALS['sr2_seo_allowed_urls'] ?? array(), true ) ? $url : ''; }
function esc_attr( $value ) {
	return htmlspecialchars( (string) $value, ENT_QUOTES, 'UTF-8' ); }
function esc_url( $value ) {
	return esc_attr( $value ); }
function get_locale() {
	return 'en_US'; }
function get_the_title( $id = null ) {
	return 'Authored journal title'; }
function get_the_excerpt() {
	return 'Authored journal copy retained verbatim.'; }
function get_the_content() {
	return get_the_excerpt(); }
function get_the_post_thumbnail_url( $id, $size ) {
	return $GLOBALS['sr2_seo_post_thumbnail'] ?? ''; }
function get_the_date( $format ) {
	return '2026-10-02T00:00:00+00:00'; }
function get_the_modified_date( $format ) {
	return '2026-10-02T01:00:00+00:00'; }
function get_the_author() {
	return 'Fixture author'; }
function get_post_ancestors( $id ) {
	return array(); }
function get_theme_mod( $key ) {
	return 0; }
function trailingslashit( $url ) {
	return rtrim( $url, '/' ) . '/'; }
function wp_json_encode( $value, $flags = 0 ) {
	return json_encode( $value, $flags ); }
function __( $value, $domain ) {
	return $value; }
function wp_trim_words( $value, $count, $more ) {
	return implode( ' ', array_slice( explode( ' ', $value ), 0, $count ) ); }
function skyyrose2_sot_asset_uri( $path ) {
	return 'https://skyyrose.co/wp-content/themes/skyyrose-flagship-2/assets/sot/' . $path; }
$skyyrose2_test_context['page'] = true;
$faq_entries                    = skyyrose2_seo_faq_entries();
skyyrose2_test_assert(
	array(
		array(
			'question' => 'Merchant size question?',
			'answer'   => 'Merchant size answer.',
		),
	) === $faq_entries,
	'FAQ schema must reflect visible merchant content, never bundled defaults.'
);
$skyyrose2_test_context['page'] = false;
function wc_get_product( $id ) {
	return new class() {
		public function get_name() {
			return 'Test garment'; }
		public function get_short_description() {
			return 'Authoritative product copy.'; }
		public function get_description() {
				return ''; }
		public function get_image_id() {
				throw new RuntimeException( 'Raw attachment bypassed resolver' ); }
	}; }
function skyyrose2_product_commerce_media( $product ) {
	return $GLOBALS['sr2_seo_test_media']; }
function wp_get_attachment_image_url( $id, $size ) {
	return 'https://example.test/' . $id . '.webp'; }
$skyyrose2_test_context['singular'] = true;
$GLOBALS['sr2_seo_test_media']      = array(
	'state' => 'editorial',
	'ids'   => array( 77 ),
);
skyyrose2_test_assert( 'https://example.test/77.webp' === skyyrose2_seo_resolved_context()['image'], 'SEO must use the resolved product image.' );
$GLOBALS['sr2_seo_test_media'] = array(
	'state' => 'v2-original',
	'ids'   => array( 77 ),
	'front' => array( 'src' => 'https://example.test/v2/current-sku-front.webp' ),
);
$product_context               = skyyrose2_seo_resolved_context();
skyyrose2_test_assert( $GLOBALS['sr2_seo_test_media']['front']['src'] === $product_context['image'], 'Current exact PDP lead must win over assigned attachment social preview.' );
skyyrose2_test_assert( 'Test garment | SkyyRose' === $product_context['title'] && 'Authoritative product copy.' === $product_context['description'] && 'product' === $product_context['type'], 'Replacing imagery must preserve native product copy and metadata type.' );
$GLOBALS['sr2_seo_test_media']['ids'] = array();
skyyrose2_test_assert( $GLOBALS['sr2_seo_test_media']['front']['src'] === skyyrose2_seo_resolved_context()['image'], 'Theme-local social preview must work without a fabricated attachment ID.' );
$GLOBALS['sr2_seo_test_media'] = array(
	'state' => 'rejected',
	'ids'   => array(),
);
skyyrose2_test_assert( '' === skyyrose2_seo_resolved_context()['image'], 'Rejected media cannot return through social metadata.' );

// Execute both maintained and compatibility emitters. The active adapter owns
// production output; the old hooks still cannot expose assigned V1 thumbnails.
$legacy_start = strpos( $theme_source, 'function skyyrose2_seo_context()' );
$legacy_end   = strpos( $theme_source, 'function skyyrose2_cart_fragment(', $legacy_start );
if ( false === $legacy_start || false === $legacy_end ) {
	throw new RuntimeException( 'Legacy SEO extraction failed' ); }
eval( substr( $theme_source, $legacy_start, $legacy_end - $legacy_start ) );
$skyyrose2_test_context['post_type'] = 'post';
$skyyrose2_test_context['single']    = true;
$approved_article                    = $GLOBALS['sr2_seo_allowed_urls'][2];
$legacy_article                      = 'https://skyyrose.co/wp-content/uploads/v1-editorial.jpg';
$unregistered_v2                     = 'https://skyyrose.co/wp-content/themes/skyyrose-flagship-2/assets/test/unreviewed-article.webp';
foreach ( array( $legacy_article, $unregistered_v2, $approved_article ) as $thumbnail ) {
	$GLOBALS['sr2_seo_post_thumbnail'] = $thumbnail;
	$expected                          = $thumbnail === $approved_article ? $thumbnail : '';
	foreach ( array( 'skyyrose2_seo_resolved_context', 'skyyrose2_seo_context' ) as $context_reader ) {
		$article_context = $context_reader();
		skyyrose2_test_assert( $expected === $article_context['image'], 'Article social context must permit only the explicitly registered V2 thumbnail: ' . $context_reader );
		skyyrose2_test_assert( 'Authored journal title | SkyyRose' === $article_context['title'] && get_the_excerpt() === $article_context['description'] && 'article' === $article_context['type'], 'Image rejection must preserve authored journal copy and metadata type.' );
	}
	foreach ( array( 'skyyrose2_seo_render_meta', 'skyyrose2_seo_head' ) as $meta_renderer ) {
		ob_start();
		$meta_renderer();
		$meta = ob_get_clean();
		skyyrose2_test_assert( ! str_contains( $meta, $legacy_article ) && ! str_contains( $meta, $unregistered_v2 ), 'Emitted social metadata must exclude V1 and unregistered V2 thumbnails.' );
		skyyrose2_test_assert( (bool) $expected === str_contains( $meta, 'property="og:image"' ), 'Open Graph image must follow the explicit URL gate.' );
		skyyrose2_test_assert( str_contains( $meta, 'name="twitter:card" content="' . ( $expected ? 'summary_large_image' : 'summary' ) . '"' ), 'Twitter card type must follow actual eligible imagery.' );
		if ( 'skyyrose2_seo_render_meta' === $meta_renderer ) {
			skyyrose2_test_assert( (bool) $expected === str_contains( $meta, 'name="twitter:image"' ), 'Twitter image must follow the same explicit URL gate.' ); }
		skyyrose2_test_assert( str_contains( $meta, 'content="' . get_the_excerpt() . '"' ), 'Emitted metadata preserves authored article copy when imagery is withheld.' );
		if ( $expected ) {
			skyyrose2_test_assert( str_contains( $meta, 'content="' . $approved_article . '"' ), 'Registered V2 thumbnail must reach emitted metadata.' ); }
	}
	foreach ( array( 'skyyrose2_seo_render_schema', 'skyyrose2_schema_head' ) as $schema_renderer ) {
		ob_start();
		$schema_renderer();
		$schema_html = ob_get_clean();
		if ( ! preg_match( '#<script type="application/ld\+json">(.*?)</script>#s', $schema_html, $json ) ) {
			throw new RuntimeException( 'Missing parseable Article JSON-LD' ); }
		$schema   = json_decode( $json[1], true, 512, JSON_THROW_ON_ERROR );
		$nodes    = $schema['@graph'] ?? array( $schema );
		$articles = array_values( array_filter( $nodes, static fn( $node ) => 'Article' === ( $node['@type'] ?? '' ) ) );
		skyyrose2_test_assert( 1 === count( $articles ), 'Each schema renderer emits exactly one Article.' );
		$article = $articles[0];
		skyyrose2_test_assert( ( $article['image'] ?? '' ) === $expected, 'Article JSON-LD image must follow the explicit V2 URL gate.' );
		skyyrose2_test_assert( get_the_title() === $article['headline'] && get_the_author() === $article['author']['name'] && get_the_date( DATE_W3C ) === $article['datePublished'], 'Gating Article imagery must preserve native authorship, headline and publication date.' );
		skyyrose2_test_assert( ! str_contains( $schema_html, $legacy_article ) && ! str_contains( $schema_html, $unregistered_v2 ), 'Serialized JSON-LD must not contain rejected image URLs.' );
	}
}
// The final context gate runs after extension filters, preventing a URL injected
// by another callback from reopening rejected assigned imagery.
$GLOBALS['sr2_seo_post_thumbnail'] = $approved_article;
foreach ( array( $legacy_article, $unregistered_v2, $approved_article ) as $override ) {
	$GLOBALS['sr2_seo_image_override'] = $override;
	$expected                          = $override === $approved_article ? $override : '';
	skyyrose2_test_assert( $expected === skyyrose2_seo_resolved_context()['image'], 'Filtered context image must still pass exact URL eligibility.' );
	ob_start();
	skyyrose2_seo_render_meta();
	$meta = ob_get_clean();
	skyyrose2_test_assert( ! str_contains( $meta, $legacy_article ) && ! str_contains( $meta, $unregistered_v2 ), 'Filtered social metadata must exclude rejected URLs.' );
}
unset( $GLOBALS['sr2_seo_image_override'] );
$skyyrose2_test_context['single']    = false;
$skyyrose2_test_context['post_type'] = 'product';
$skyyrose2_test_context['singular']  = true;
Jetpack_SEO_Posts::$noindex          = array( 42 => true );
$robots                              = skyyrose2_seo_robots( array( 'index' => true ) );
skyyrose2_test_assert( isset( $robots['noindex'] ) && ! isset( $robots['index'] ) && ! isset( $robots['max-image-preview'] ), 'A record the merchant marked noindex in Jetpack SEO Tools must keep its noindex.' );
Jetpack_SEO_Posts::$noindex = array( 7 => true );
$robots                     = skyyrose2_seo_robots( array( 'index' => true ) );
skyyrose2_test_assert( ! isset( $robots['noindex'] ) && 'large' === $robots['max-image-preview'], 'Other records stay indexable.' );
Jetpack_SEO_Posts::$noindex         = array( 42 => true );
$skyyrose2_test_context['singular'] = false;
$robots                             = skyyrose2_seo_robots( array( 'index' => true ) );
skyyrose2_test_assert( ! isset( $robots['noindex'] ), 'Jetpack per-post noindex applies only to singular requests.' );
Jetpack_SEO_Posts::$noindex = array();
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
echo "PASS offline exact-URL imagery gate: registered V2 social and Article JSON-LD retained; assigned V1, unregistered V2 and filtered legacy URLs withheld by active and compatibility emitters.\n";
