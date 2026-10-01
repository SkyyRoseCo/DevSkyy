<?php
/**
 * Offline regression using captured WordPress 7.1.2 hook/dependency classes.
 *
 * Actual core: WP_Hook, plugin hooks, WP_Dependencies, _WP_Dependency,
 * WP_Scripts and its dependency resolution, done set and final tag filtering.
 * Stubs: target/request/Jetpack state, dequeue wrapper and HTML/URL rendering.
 * No WordPress bootstrap, database, HTTP, browser or authenticated execution.
 */

define( 'ABSPATH', __DIR__ . '/' );
$root = dirname( __DIR__, 2 );
$core = $argv[1] ?? $root . '/.artifacts/production-final-pass-20261001/wp-core';
$receipt_path = $argv[2] ?? $root . '/tasks/production-final-pass-20261001/evidence/wordpress-core-dependency-sources-with-sentinel.json';
$receipt = json_decode( file_get_contents( $receipt_path ), true, 512, JSON_THROW_ON_ERROR );
if ( '7.1.2' !== $receipt['version'] || 'https://skyyrose.co' !== $receipt['home'] ) {
	throw new RuntimeException( 'Unexpected core capture receipt identity.' );
}
$required = array(
	'class-wp-scripts.php', 'class-wp-dependencies.php', 'class-wp-dependency.php',
	'class-wp-hook.php', 'class-wp-filter-sentinel.php', 'plugin.php',
);
foreach ( $required as $name ) {
	$expected = $receipt['files'][ $name ]['sha256'] ?? '';
	if ( ! preg_match( '/^[a-f0-9]{64}$/D', $expected ) || ! is_file( $core . '/' . $name )
		|| ! hash_equals( $expected, hash_file( 'sha256', $core . '/' . $name ) ) ) {
		throw new RuntimeException( 'Missing or changed captured core file: ' . $name );
	}
}
$extension = __DIR__ . '/search-tracking-privacy.php';
if ( 'afc2f6d8a4ae6280de28b6c1306564cc86053acc713c52e5ab0b5717b3ef58f2' !== hash_file( 'sha256', $extension ) ) {
	throw new RuntimeException( 'Frozen extension identity mismatch.' );
}
require $core . '/plugin.php';
require $core . '/class-wp-dependency.php';
require $core . '/class-wp-dependencies.php';
require $core . '/class-wp-scripts.php';

// Environment/render stubs only; hooks and script dependency logic are core.
$GLOBALS['runtime_scope'] = array( 'home' => 'https://skyyrose.co', 'style' => 'skyyrose-flagship', 'active' => true, 'admin' => false );
class Jetpack {
	public static function is_module_active( string $module ): bool {
		return 'search' === $module && $GLOBALS['runtime_scope']['active'];
	}
}
function is_admin(): bool { return $GLOBALS['runtime_scope']['admin']; }
function wp_doing_ajax(): bool { return false; }
function wp_doing_cron(): bool { return false; }
function get_option( string $name ) { return $GLOBALS['runtime_scope'][ $name ]; }
function get_stylesheet(): string { return $GLOBALS['runtime_scope']['style']; }
function wp_dequeue_script( string $handle ): void { $GLOBALS['wp_scripts']->dequeue( $handle ); }
function esc_url_raw( string $url ): string { return $url; }
function wp_get_script_tag( array $attributes ): string {
	$tag = '<script';
	foreach ( $attributes as $name => $value ) {
		$tag .= ' ' . htmlspecialchars( $name, ENT_QUOTES ) . '="' . htmlspecialchars( (string) $value, ENT_QUOTES ) . '"';
	}
	return $tag . '></script>';
}
function runtime_expect( bool $condition, string $message ): void {
	if ( ! $condition ) {
		throw new RuntimeException( 'FAIL: ' . $message );
	}
	++$GLOBALS['runtime_assertions'];
}
function runtime_capture_scripts( WP_Scripts $scripts ): string {
	ob_start();
	$scripts->print_scripts();
	return ob_get_clean();
}
require $extension;
$GLOBALS['runtime_assertions'] = 0;
runtime_expect( $GLOBALS['wp_filter']['script_loader_tag'] instanceof WP_Hook, 'actual WP_Hook registered' );
$scenarios = array(
	'production-v1' => array(),
	'production-v2' => array( 'style' => 'skyyrose-flagship-2' ),
	'staging-v2' => array( 'home' => 'https://staging-7e48-skyyrose.wpcomstaging.com', 'style' => 'skyyrose-flagship-2' ),
	'inactive' => array( 'active' => false ),
	'wrong-target' => array( 'home' => 'https://example.invalid' ),
	'admin' => array( 'admin' => true ),
);
$baseline = $GLOBALS['runtime_scope'];
foreach ( $scenarios as $name => $overrides ) {
	$GLOBALS['runtime_scope'] = array_replace( $baseline, $overrides );
	$bounded = in_array( $name, array( 'production-v1', 'production-v2', 'staging-v2' ), true );
	runtime_expect( $bounded === apply_filters( 'jetpack_instant_search_disable_tracking', false ), $name . ': disable flag bounded' );
	runtime_expect( true === apply_filters( 'jetpack_instant_search_disable_tracking', true ), $name . ': incoming true preserved' );
	$scripts = new WP_Scripts();
	$GLOBALS['wp_scripts'] = $scripts;
	$scripts->default_version = '7.1.2';
	$scripts->add( 'wp-i18n', 'https://example.invalid/i18n.js', array(), null );
	$scripts->add( 'jp-search', 'https://example.invalid/search.js', array( 'wp-i18n' ), null );
	$scripts->add( 'jp-tracks', 'https://example.invalid/tracks.js', array(), null );
	$scripts->add( 'late-consumer', 'https://example.invalid/consumer.js', array( 'jp-tracks' ), null );
	$scripts->enqueue( array( 'jp-search', 'jp-tracks' ) );
	do_action( 'wp_enqueue_scripts' );
	do_action( 'wp_enqueue_scripts' );
	runtime_expect( ! $bounded === in_array( 'jp-tracks', $scripts->queue, true ), $name . ': enqueue removal idempotent' );
	$scripts->enqueue( 'jp-tracks' );
	do_action( 'wp_print_footer_scripts' );
	runtime_expect( ! $bounded === in_array( 'jp-tracks', $scripts->queue, true ), $name . ': footer removal' );
	// A block directly re-enqueues after removal; core also resolves a dependency.
	$scripts->enqueue( array( 'jp-tracks', 'late-consumer' ) );
	$output = runtime_capture_scripts( $scripts );
	runtime_expect( ! $bounded === str_contains( $output, 'id="jp-tracks-js"' ), $name . ': actual core final tracking tag' );
	foreach ( array( 'wp-i18n', 'jp-search', 'late-consumer' ) as $handle ) {
		runtime_expect( str_contains( $output, 'id="' . $handle . '-js"' ), $name . ': preserved ' . $handle );
	}
	runtime_expect( array( 'wp-i18n' ) === $scripts->registered['jp-search']->deps, $name . ': Search dependencies unchanged' );
	runtime_expect( isset( $scripts->registered['jp-tracks'] ), $name . ': tracking registration retained' );
	runtime_expect( array( 'wp-i18n', 'jp-search', 'jp-tracks', 'late-consumer' ) === $scripts->done, $name . ': actual dependency done order' );
	runtime_expect( '' === runtime_capture_scripts( $scripts ), $name . ': no duplicate printing' );
	// Resolve tracking exclusively as a dependency after dequeue, not direct queue.
	$scripts->done = array();
	$scripts->queue = array( 'jp-search', 'late-consumer', 'jp-tracks' );
	do_action( 'wp_enqueue_scripts' );
	if ( ! $bounded ) {
		$scripts->dequeue( 'jp-tracks' );
	}
	$output = runtime_capture_scripts( $scripts );
	runtime_expect( ! $bounded === str_contains( $output, 'id="jp-tracks-js"' ), $name . ': dependency-only tracking tag' );
	runtime_expect( str_contains( $output, 'id="jp-search-js"' ) && str_contains( $output, 'id="late-consumer-js"' ), $name . ': dependency consumers complete' );
	if ( 'production-v1' === $name ) {
		// Negative control: the disable flag and dequeue do not prevent late output.
		remove_filter( 'script_loader_tag', 'skyyrose_runtime_search_tracking_tag', PHP_INT_MAX );
		$scripts->done = array();
		$scripts->queue = array( 'jp-search', 'late-consumer' );
		runtime_expect( true === apply_filters( 'jetpack_instant_search_disable_tracking', false ), 'negative control retains disable flag' );
		runtime_expect( str_contains( runtime_capture_scripts( $scripts ), 'id="jp-tracks-js"' ), 'negative control proves dependency can print tracking' );
		add_filter( 'script_loader_tag', 'skyyrose_runtime_search_tracking_tag', PHP_INT_MAX, 2 );
		$scripts->done = array();
		runtime_expect( ! str_contains( runtime_capture_scripts( $scripts ), 'id="jp-tracks-js"' ), 'restored guard suppresses actual core output' );
	}
	echo 'PASS actual core scenario: ' . $name . "\n";
}
echo 'PASS ' . $GLOBALS['runtime_assertions'] . ' assertions; actual captured WordPress 7.1.2 hook/dependency classes; environment/render stubs; offline authentication not applicable' . "\n";
