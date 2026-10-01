<?php
/** Offline hook and script-dependency regression harness. Authentication: N/A. */

define( 'ABSPATH', __DIR__ . '/' );
$case = $argv[1] ?? 'public';
if ( in_array( $case, array( 'cli', 'rest' ), true ) ) {
	define( 'cli' === $case ? 'WP_CLI' : 'REST_REQUEST', true );
}
$GLOBALS['scope'] = array(
	'home'       => 'other-home' === $case ? 'https://example.invalid' : 'https://skyyrose.co',
	'stylesheet' => 'other-theme' === $case ? 'twentytwentyfive' : 'skyyrose-flagship',
	'active'     => 'inactive' !== $case,
);
if ( 'staging' === $case || 'staging-v1' === $case ) {
	$GLOBALS['scope']['home'] = 'https://staging-7e48-skyyrose.wpcomstaging.com';
	$GLOBALS['scope']['stylesheet'] = 'staging' === $case ? 'skyyrose-flagship-2' : 'skyyrose-flagship';
}
if ( 'production-v2' === $case ) {
	$GLOBALS['scope']['stylesheet'] = 'skyyrose-flagship-2';
}
if ( 'no-jetpack' !== $case ) {
	class Jetpack {
		public static function is_module_active( string $module ): bool {
			return 'search' === $module && $GLOBALS['scope']['active'];
		}
	}
}
function is_admin(): bool { return 'admin' === $GLOBALS['case']; }
function wp_doing_ajax(): bool { return 'ajax' === $GLOBALS['case']; }
function wp_doing_cron(): bool { return 'cron' === $GLOBALS['case']; }
function get_option( string $name ) { return $GLOBALS['scope'][ $name ]; }
function get_stylesheet(): string { return $GLOBALS['scope']['stylesheet']; }
$GLOBALS['case'] = $case;
$GLOBALS['hooks'] = array();
function add_filter( string $hook, callable $callback, int $priority = 10, int $args = 1 ): void {
	$GLOBALS['hooks'][ $hook ][ $priority ][ $callback ] = $args;
}
function add_action( string $hook, callable $callback, int $priority = 10, int $args = 1 ): void {
	add_filter( $hook, $callback, $priority, $args );
}
function apply_filters( string $hook, $value, ...$args ) {
	$priorities = $GLOBALS['hooks'][ $hook ] ?? array();
	ksort( $priorities );
	foreach ( $priorities as $callbacks ) {
		foreach ( $callbacks as $callback => $accepted ) {
			$value = $callback( ...array_slice( array_merge( array( $value ), $args ), 0, $accepted ) );
		}
	}
	return $value;
}
function do_action( string $hook ): void {
	$priorities = $GLOBALS['hooks'][ $hook ] ?? array();
	ksort( $priorities );
	foreach ( $priorities as $callbacks ) {
		foreach ( $callbacks as $callback => $accepted ) {
			$callback();
		}
	}
}

/** Model WP_Scripts queue removal, recursive dependency resolution and done set. */
class WP_Scripts {
	public array $registered = array();
	public array $queue = array();
	public array $done = array();
	public function register( string $handle, array $dependencies ): void {
		$this->registered[ $handle ] = $dependencies;
	}
	public function enqueue( string $handle ): void {
		if ( ! in_array( $handle, $this->queue, true ) ) {
			$this->queue[] = $handle;
		}
	}
	public function dequeue( string $handle ): void {
		$this->queue = array_values( array_diff( $this->queue, array( $handle ) ) );
	}
	public function print_handle( string $handle ): string {
		if ( in_array( $handle, $this->done, true ) ) {
			return '';
		}
		$output = '';
		foreach ( $this->registered[ $handle ] as $dependency ) {
			$output .= $this->print_handle( $dependency );
		}
		$this->done[] = $handle;
		return $output . apply_filters( 'script_loader_tag', '<script id="' . $handle . '"></script>', $handle );
	}
	public function print_queue(): string {
		$output = '';
		foreach ( $this->queue as $handle ) {
			$output .= $this->print_handle( $handle );
		}
		return $output;
	}
}
$GLOBALS['scripts'] = new WP_Scripts();
function wp_dequeue_script( string $handle ): void { $GLOBALS['scripts']->dequeue( $handle ); }
$assertions = 0;
function expect( bool $condition, string $message ): void {
	if ( ! $condition ) {
		throw new RuntimeException( 'FAIL: ' . $GLOBALS['case'] . ': ' . $message );
	}
	++$GLOBALS['assertions'];
}
require __DIR__ . '/search-tracking-privacy.php';
// Each hook owns exactly one named callback; repeated dispatch is tested below.
foreach ( $GLOBALS['hooks'] as $priorities ) {
	expect( 1 === count( $priorities[ PHP_INT_MAX ] ), 'one callback per late hook' );
}
$bounded = in_array( $case, array( 'public', 'production-v2', 'staging' ), true );
expect( $bounded === skyyrose_runtime_search_privacy_applies(), 'strict request scope' );
expect( $bounded === apply_filters( 'jetpack_instant_search_disable_tracking', false ), 'incoming false preserved outside target' );
expect( true === apply_filters( 'jetpack_instant_search_disable_tracking', true ), 'incoming true always preserved' );
expect( '<script>other</script>' === apply_filters( 'script_loader_tag', '<script>other</script>', 'security-script' ), 'other script tag unchanged' );
$scripts = $GLOBALS['scripts'];
$scripts->register( 'wp-i18n', array() );
$scripts->register( 'jetpack-instant-search', array( 'wp-i18n' ) );
$scripts->register( 'jp-tracks', array() );
$scripts->register( 'late-consumer', array( 'jp-tracks' ) );
$scripts->enqueue( 'jetpack-instant-search' );
$scripts->enqueue( 'jp-tracks' );
do_action( 'wp_enqueue_scripts' );
do_action( 'wp_enqueue_scripts' );
expect( ! $bounded === in_array( 'jp-tracks', $scripts->queue, true ), 'idempotent enqueue removal only in scope' );
expect( isset( $scripts->registered['jp-tracks'] ), 'tracking registration preserved' );
$scripts->enqueue( 'jp-tracks' );
do_action( 'wp_print_footer_scripts' );
expect( ! $bounded === in_array( 'jp-tracks', $scripts->queue, true ), 'late footer queue removal' );
// A block enqueues after both dequeue hooks, and another script requires Tracks.
$scripts->enqueue( 'jp-tracks' );
$scripts->enqueue( 'late-consumer' );
$output = $scripts->print_queue();
expect( ! $bounded === str_contains( $output, 'id="jp-tracks"' ), 'tag filter handles late enqueue and dependency requeue' );
foreach ( array( 'wp-i18n', 'jetpack-instant-search', 'late-consumer' ) as $handle ) {
	expect( str_contains( $output, 'id="' . $handle . '"' ), $handle . ' still prints' );
}
expect( array( 'wp-i18n' ) === $scripts->registered['jetpack-instant-search'], 'Search dependencies unchanged' );
expect( in_array( 'jp-tracks', $scripts->done, true ), 'dependency completes without tracking output' );
expect( '' === $scripts->print_queue(), 'done set prevents duplicate printing' );
echo 'PASS ' . $case . ': ' . $assertions . " assertions; offline authentication not applicable\n";
