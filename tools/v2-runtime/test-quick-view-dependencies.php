<?php
/** Focused final-enqueue graph regressions; no WordPress installation required. */
define( 'ABSPATH', __DIR__ );
function add_action( ...$args ) {}
function add_filter( ...$args ) {}
function wp_scripts() { return $GLOBALS['scripts']; }
function home_url( $path = '/' ) { return 'https://shop.test' . $path; }
function wp_parse_url( $url ) { return parse_url( $url ); }
function is_product() { return $GLOBALS['pdp']; }
function apply_filters( $hook, $value ) {
	if ( 'skyyrose2_quick_view_lazy_variations_enabled' !== $hook ) { throw new RuntimeException( 'Unexpected filter' ); }
	return $GLOBALS['enabled'];
}
// Only tag transformation is stubbed. The actual production graph and filter run below.
class WP_HTML_Tag_Processor {
	private bool $visited = false;
	private array $attributes = array( 'id' => 'wc-add-to-cart-variation-js', 'src' => '/native.js' );
	public function __construct( $tag ) {}
	public function next_tag( $tag ) { if ( $this->visited ) { return false; } $this->visited = true; return true; }
	public function get_attribute( $key ) { return $this->attributes[ $key ] ?? null; }
	public function set_attribute( $key, $value ) { $this->attributes[ $key ] = $value; }
	public function remove_attribute( $key ) { unset( $this->attributes[ $key ] ); }
	public function get_updated_html() { return json_encode( $this->attributes ); }
}
require __DIR__ . '/../../wordpress-theme/skyyrose-flagship-2/inc/quick-view-commerce.php';
function check_qv_graph( $queue, $dependencies, $defer, $label, $enabled = true, $pdp = false, $src = '/native.js', $after = array() ) {
	$GLOBALS['scripts'] = (object) array( 'queue' => $queue, 'registered' => array() );
	$GLOBALS['enabled'] = $enabled;
	$GLOBALS['pdp'] = $pdp;
	foreach ( $dependencies as $handle => $deps ) {
		$GLOBALS['scripts']->registered[ $handle ] = (object) array( 'deps' => $deps );
	}
	$GLOBALS['scripts']->registered['wc-add-to-cart-variation'] ??= (object) array( 'deps' => array() );
	$GLOBALS['scripts']->registered['wc-add-to-cart-variation']->extra = array( 'after' => $after );
	$original = '<script id="wc-add-to-cart-variation-js" src="/native.js"></script>';
	$result = skyyrose2_quick_view_defer_variation_script( $original, 'wc-add-to-cart-variation', $src );
	if ( $defer ) {
		$attributes = json_decode( $result, true );
		if ( isset( $attributes['src'] ) || 'text/plain' !== ( $attributes['type'] ?? null ) || $src !== ( $attributes['data-sr2-variation-src'] ?? null ) ) {
			throw new RuntimeException( $label . ': expected inert deferred tag' );
		}
	} elseif ( $original !== $result ) {
		throw new RuntimeException( $label . ': native script must remain unchanged' );
	}
	echo "PASS: $label\n";
}
$qv = 'skyyrose2-quick-view-commerce';
$wc = 'wc-add-to-cart-variation';
$base = array( $qv => array( 'theme', $wc ), $wc => array( 'jquery', 'wp-util' ), 'theme' => array() );
check_qv_graph( array( $qv ), $base, true, 'Quick View sole ownership defers' );
check_qv_graph( array( $qv, $wc ), $base, false, 'Direct native enqueue preserves execution' );
check_qv_graph( array( $qv, 'extension' ), $base + array( 'extension' => array( 'shared' ), 'shared' => array( $wc ) ), false, 'Transitive extension dependency preserves execution' );
check_qv_graph( array( $qv, 'extension' ), $base + array( 'extension' => array( $qv ) ), false, 'Extension consuming Quick View dependency preserves execution' );
check_qv_graph( array( $qv, 'extension' ), $base + array( 'extension' => array( 'leaf', 'path-a', 'path-b' ), 'path-a' => array( 'shared' ), 'path-b' => array( 'shared', $wc ), 'shared' => array() ), false, 'Multiple dependency paths are inspected' );
check_qv_graph( array( $qv, 'extension' ), $base + array( 'extension' => array( 'cycle' ), 'cycle' => array( 'extension' ) ), true, 'Unrelated dependency cycles terminate and allow deferral' );
check_qv_graph( array( $qv, 'extension' ), $base + array( 'extension' => array( 'cycle' ), 'cycle' => array( 'extension', $wc ) ), false, 'Cycle reaching native runtime preserves execution' );
check_qv_graph( array( $wc ), $base, false, 'Absent Quick View owner preserves execution' );
check_qv_graph( array( $qv ), array( $qv => array( 'theme' ) ), false, 'Owner without native dependency preserves execution' );
check_qv_graph( array( $qv ), $base, false, 'Extension opt-out preserves execution', false );
check_qv_graph( array( $qv ), $base, false, 'PDP always preserves native execution', true, true );

check_qv_graph( array( $qv ), $base, false, 'Native after-code preserves eager execution', true, false, '/native.js', array( 'jQuery.fn.wc_variation_form();' ) );
check_qv_graph( array( $qv ), $base, false, 'CDN host preserves eager execution', true, false, 'https://cdn.test/native.js' );
check_qv_graph( array( $qv ), $base, false, 'Foreign port preserves eager execution', true, false, 'https://shop.test:444/native.js' );
check_qv_graph( array( $qv ), $base, false, 'Foreign scheme preserves eager execution', true, false, 'http://shop.test/native.js' );
check_qv_graph( array( $qv ), $base, true, 'Relative same-origin script can defer', true, false, 'assets/native.js' );
check_qv_graph( array( $qv ), $base, true, 'Absolute same-origin default port can defer', true, false, 'https://shop.test:443/native.js' );
check_qv_graph( array( $qv ), $base, true, 'Protocol-relative same-origin script can defer', true, false, '//shop.test/native.js' );
check_qv_graph( array( $qv ), $base, false, 'Protocol-relative CDN preserves eager execution', true, false, '//cdn.test/native.js' );
