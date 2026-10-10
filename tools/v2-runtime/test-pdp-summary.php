<?php
/** Execute the actual template boundary against a hook registry, including failures. */
$source = file_get_contents( __DIR__ . '/../../wordpress-theme/skyyrose-flagship-2/template-parts/commerce/product-hero.php' );
$start  = strpos( $source, '// BEGIN SR2_NATIVE_SUMMARY:' );
$end    = strpos( $source, '// END SR2_NATIVE_SUMMARY', $start );
if ( false === $start || false === $end ) {
	throw new RuntimeException( 'Native summary boundary was not found.' );
}
$boundary = substr( $source, $start, $end - $start );

function add_action( $hook, $callback, $priority = 10 ) {
	$GLOBALS['callbacks'][ $hook ][ $priority ][ $callback ] = $callback;
}
function has_action( $hook, $callback ) {
	$priorities = $GLOBALS['callbacks'][ $hook ] ?? array();
	ksort( $priorities );
	foreach ( $priorities as $priority => $callbacks ) {
		if ( isset( $callbacks[ $callback ] ) ) {
			return $priority;
		}
	}
	return false;
}
function remove_action( $hook, $callback, $priority = 10 ) {
	unset( $GLOBALS['callbacks'][ $hook ][ $priority ][ $callback ] );
}
function do_action( $hook ) {
	$priorities = $GLOBALS['callbacks'][ $hook ] ?? array();
	ksort( $priorities );
	foreach ( $priorities as $callbacks ) {
		foreach ( $callbacks as $callback ) {
			$callback();
		}
	}
}
function fixture_title() {
	$GLOBALS['rendered'][] = 'title';
}
function fixture_form() {
	$GLOBALS['rendered'][] = 'native-form';
	if ( $GLOBALS['throw_from'] === 'form' ) {
		throw new RuntimeException( 'form failure' );
	}
}
function fixture_extension() {
	$GLOBALS['rendered'][] = 'extension-link';
}
function woocommerce_template_single_excerpt() {
	$GLOBALS['rendered'][] = 'excerpt-link';
	if ( $GLOBALS['throw_from'] === 'excerpt' ) {
		throw new RuntimeException( 'excerpt failure' );
	}
}
function setup_fixture( $excerpt_priority, $throw_from = '' ) {
	$GLOBALS['callbacks']  = array();
	$GLOBALS['rendered']   = array();
	$GLOBALS['throw_from'] = $throw_from;
	add_action( 'woocommerce_single_product_summary', 'fixture_title', 5 );
	add_action( 'woocommerce_single_product_summary', 'fixture_form', 30 );
	add_action( 'woocommerce_single_product_summary', 'fixture_extension', 40 );
	if ( false !== $excerpt_priority ) {
		add_action( 'woocommerce_single_product_summary', 'woocommerce_template_single_excerpt', $excerpt_priority );
	}
}
function verify( $condition, $message ) {
	if ( ! $condition ) {
		throw new RuntimeException( $message );
	}
}
function render_boundary( $boundary ) {
	ob_start();
	try {
		eval( $boundary );
		return ob_get_contents();
	} finally {
		ob_end_clean();
	}
}
foreach ( array( 0, 20, 27 ) as $priority ) {
	setup_fixture( $priority );
	$markup = render_boundary( $boundary );
	verify( 1 === substr_count( $markup, 'data-sr2-pdp-status' ), 'Summary must contain exactly one native status region.' );
	verify( array( 'title', 'native-form', 'extension-link', 'excerpt-link' ) === $GLOBALS['rendered'], 'Purchase, extension and excerpt must render once in matching DOM order.' );
	verify( $priority === has_action( 'woocommerce_single_product_summary', 'woocommerce_template_single_excerpt' ), 'Exact original excerpt priority was not restored.' );
	verify( 40 === has_action( 'woocommerce_single_product_summary', 'fixture_extension' ), 'Extension registration changed.' );
}
setup_fixture( false );
render_boundary( $boundary );
verify( array( 'title', 'native-form', 'extension-link' ) === $GLOBALS['rendered'], 'Disabled native excerpt must remain absent.' );
verify( false === has_action( 'woocommerce_single_product_summary', 'woocommerce_template_single_excerpt' ), 'Disabled callback was incorrectly registered.' );
foreach ( array( 'form', 'excerpt' ) as $failure ) {
	setup_fixture( 27, $failure );
	$caught = false;
	try {
		render_boundary( $boundary );
	} catch ( RuntimeException $error ) {
		$caught = $error->getMessage() === $failure . ' failure';
	}
	verify( $caught, 'Original callback failure must propagate.' );
	verify( 27 === has_action( 'woocommerce_single_product_summary', 'woocommerce_template_single_excerpt' ), 'Exception failed to restore the native excerpt registration.' );
	verify( 30 === has_action( 'woocommerce_single_product_summary', 'fixture_form' ), 'Native form registration changed.' );
}
echo "PASS native PDP excerpt once-only placement, disabled callback, extension order and exception restoration\n";
