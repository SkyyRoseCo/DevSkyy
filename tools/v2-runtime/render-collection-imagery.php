<?php
/**
 * Offline render of the V2 collection-imagery surfaces: /collections/black-rose/
 * (arrival + origin story), /collections/ (index chapters), the homepage chapters
 * and worlds rail, the header collection previews, and each route's image preload.
 *
 * Real theme templates and the real media gate run against real bytes; only the
 * WordPress/WooCommerce request layer is stubbed. Every page is passed through
 * skyyrose2_media_filter_html(), the same output-buffer boundary production uses.
 * Product cards, prices and stock are live WooCommerce facts and are not rendered.
 *
 * Usage: php render-collection-imagery.php <home|black-rose|collections> [theme-dir]
 */
$page  = $argv[1] ?? 'black-rose';
$theme = realpath( $argv[2] ?? dirname( __DIR__, 2 ) . '/wordpress-theme/skyyrose-flagship-2' );
define( 'ABSPATH', $theme . '/' );
define( 'OBJECT', 'OBJECT' );
define( 'SKYYROSE2_DIR', $theme );
define( 'SKYYROSE2_URI', 'https://skyyrose.co/wp-content/themes/skyyrose-flagship-2' );
$GLOBALS['render_route'] = $page;

function add_action( ...$args ) {} function add_filter( ...$args ) {} function remove_action( ...$args ) {}
function apply_filters( $hook, $value, ...$args ) { return $value; }
function __( $text, $domain = '' ) { return $text; }
function _x( $text, $context = '', $domain = '' ) { return $text; }
function esc_html( $value ) { return htmlspecialchars( (string) $value, ENT_QUOTES, 'UTF-8' ); }
function esc_attr( $value ) { return esc_html( $value ); }
function esc_url( $value ) { return esc_html( $value ); }
function esc_html__( $value, $domain = '' ) { return esc_html( $value ); }
function esc_attr__( $value, $domain = '' ) { return esc_attr( $value ); }
function esc_html_e( $value, $domain = '' ) { echo esc_html( $value ); }
function esc_attr_e( $value, $domain = '' ) { echo esc_attr( $value ); }
function sanitize_title( $value ) { return strtolower( trim( preg_replace( '/[^A-Za-z0-9_-]+/', '-', (string) $value ), '-' ) ); }
function sanitize_key( $value ) { return preg_replace( '/[^a-z0-9_-]/', '', strtolower( (string) $value ) ); }
function sanitize_html_class( $value ) { return sanitize_key( $value ); }
function absint( $value ) { return abs( (int) $value ); }
function wp_strip_all_tags( $value ) { return strip_tags( (string) $value ); }
function wp_json_encode( $value, $flags = 0 ) { return json_encode( $value, $flags ); }
function wp_parse_url( $url, $component = -1 ) { return parse_url( $url, $component ); }
function trailingslashit( $value ) { return rtrim( $value, '/' ) . '/'; }
function home_url( $path = '' ) { return 'https://skyyrose.co' . $path; }
function get_page_by_path( ...$args ) { return null; }
function get_permalink( ...$args ) { return ''; }
function add_query_arg( $key, $value, $url ) { return $url . '?' . rawurlencode( $key ) . '=' . rawurlencode( $value ); }
function is_admin() { return false; } function wp_doing_ajax() { return false; }
function is_user_logged_in() { return false; } function is_customize_preview() { return false; } function is_preview() { return false; }
function is_front_page() { return 'home' === $GLOBALS['render_route']; }
function is_page_template( $template = '' ) { return 'black-rose' === $GLOBALS['render_route'] && ( '' === $template || 'template-collection.php' === $template ); }
function is_page() { return 'home' !== $GLOBALS['render_route']; }
function is_singular( ...$args ) { return false; } function is_single() { return false; }
function is_shop() { return false; } function is_product_taxonomy() { return false; }
function get_queried_object_id() { return 1; }
function get_post_field( $field, $id ) { return 'home' === $GLOBALS['render_route'] ? '' : $GLOBALS['render_route']; }
function get_template_part( $slug, $name = null, $args = array() ) {
	$file = SKYYROSE2_DIR . '/' . $slug . '.php';
	if ( is_file( $file ) ) { ( static function () use ( $file, $args ) { include $file; } )(); }
}

// Load the production media gate directly, then every other top-level theme
// function by declaration only (no hooks run, nothing executes at load time).
require SKYYROSE2_DIR . '/inc/v2-media-eligibility.php';
$render_sources = array_merge( array( SKYYROSE2_DIR . '/functions.php' ), glob( SKYYROSE2_DIR . '/inc/*.php' ) );
foreach ( $render_sources as $render_source ) {
	$tokens = token_get_all( file_get_contents( $render_source ) );
	$count  = count( $tokens );
	$depth  = 0;
	for ( $i = 0; $i < $count; $i++ ) {
		$token = $tokens[ $i ];
		if ( is_array( $token ) && T_FUNCTION === $token[0] && 0 === $depth ) {
			$j = $i + 1;
			while ( $j < $count && is_array( $tokens[ $j ] ) && T_WHITESPACE === $tokens[ $j ][0] ) { ++$j; }
			if ( ! is_array( $tokens[ $j ] ) || T_STRING !== $tokens[ $j ][0] ) { continue; }
			$name = $tokens[ $j ][1];
			$code = '';
			$level = 0;
			$opened = false;
			for ( $k = $i; $k < $count; $k++ ) {
				$piece = is_array( $tokens[ $k ] ) ? $tokens[ $k ][1] : $tokens[ $k ];
				$code .= $piece;
				if ( '{' === $piece || ( is_array( $tokens[ $k ] ) && in_array( $tokens[ $k ][0], array( T_CURLY_OPEN, T_DOLLAR_OPEN_CURLY_BRACES ), true ) ) ) { ++$level; $opened = true; }
				if ( '}' === $piece ) { --$level; if ( $opened && 0 === $level ) { break; } }
			}
			if ( ! function_exists( $name ) ) { eval( $code ); }
			$i = $k;
			continue;
		}
		if ( '{' === $token || ( is_array( $token ) && in_array( $token[0], array( T_CURLY_OPEN, T_DOLLAR_OPEN_CURLY_BRACES ), true ) ) ) { ++$depth; }
		if ( '}' === $token ) { --$depth; }
	}
}

$collections = skyyrose2_collections();
ob_start();
echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>render ' . esc_html( $page ) . '</title>';
foreach ( skyyrose2_performance_route_preloads() as $preload ) {
	echo "\n<link rel=\"preload\"";
	foreach ( $preload as $key => $value ) { echo ' ' . esc_attr( $key ) . '="' . esc_attr( $value ) . '"'; }
	echo '>';
}
echo "\n</head><body>\n";
if ( 'black-rose' === $page ) {
	$world_args = array( 'slug' => 'black-rose', 'collection' => $collections['black-rose'], 'presentation' => skyyrose2_collection_presentation( 'black-rose' ), 'products' => array(), 'shop_url' => '/shop/', 'pieces_anchor' => '#world', 'world_statement' => true );
	echo '<main id="primary" class="sr2-collection-world" data-collection="black-rose">';
	get_template_part( 'template-parts/collections/arrival', null, $world_args );
	echo "\n<!-- editorial, scroll-world and the product edit are WooCommerce-owned and not rendered offline -->\n";
	get_template_part( 'template-parts/collections/story', null, $world_args );
	echo '</main>';
} elseif ( 'collections' === $page ) {
	echo '<main id="primary">';
	get_template_part( 'template-parts/collections/index' );
	echo '</main>';
} else {
	echo '<main id="primary" class="sr2-archive sr2-editorial-home">';
	get_template_part( 'template-parts/home/editorial-hero', null, array( 'collections' => $collections, 'shop_url' => '/shop/' ) );
	get_template_part( 'template-parts/home/editorial-collection', null, array( 'collections' => $collections, 'products' => array() ) );
	echo '<section class="sr2-editorial-worlds sr2-band">';
	get_template_part( 'template-parts/home/living-archive-worlds', null, array( 'collections' => $collections ) );
	echo '</section></main>';
}
echo "\n<nav class=\"sr2-house-nav__previews\" data-render-fragment=\"header collection previews\">\n";
$header_source = file_get_contents( SKYYROSE2_DIR . '/inc/global-shell.php' );
if ( preg_match( '#<\?php foreach \( skyyrose2_collections\(\) as \$slug => \$collection \) : \?>(.*?)<\?php endforeach; \?>#s', $header_source, $preview_loop ) ) {
	foreach ( $collections as $slug => $collection ) { eval( '?>' . $preview_loop[1] . '<?php ' ); }
}
echo "</nav>\n</body></html>\n";
echo skyyrose2_media_filter_html( ob_get_clean() );
