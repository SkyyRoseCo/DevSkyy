<?php
/** Offline V2 standalone bootstrap/config fixture. Authentication N/A. */
define( 'ABSPATH', __DIR__ );
define( 'SKYYROSE2_URI', 'https://fixture.test/theme' );
function add_action( $hook, $callback, $priority = 10 ) {
	$GLOBALS['hooks'][ $hook ] = $callback; }
function register_rest_route( $namespace, $route, $args ) {
	$GLOBALS['route'] = array( $namespace, $route, $args ); }
function skyyrose2_asset_suffix() {
	return $GLOBALS['suffix']; }
function skyyrose2_asset_version( $path ) {
	return hash_file( 'sha256', dirname( __DIR__, 2 ) . $path ); }
function wp_enqueue_style( $handle, $src, $deps, $version ) {
	$GLOBALS['style'] = compact( 'handle', 'src', 'version' ); }
function wp_enqueue_script( $handle, $src, $deps, $version, $args ) {
	$GLOBALS['script'] = compact( 'handle', 'src', 'version', 'args' ); }
function wp_add_inline_script( $handle, $code, $position ) {
	$GLOBALS['inline'] = $code; }
function rest_url( $route ) {
	return 'https://fixture.test/store/wp-json/' . $route; }
function get_option( $key, $default = null ) {
	return 'fixture-public-key'; }
function wp_json_encode( $value ) {
	return json_encode( $value ); }
function get_template_part( $name ) {
	$GLOBALS['template'] = $name; }
require dirname( __DIR__, 2 ) . '/inc/analytics.php';
$count = 0;
function check_bootstrap( $condition, $message ) {
	++$GLOBALS['count'];
	if ( ! $condition ) {
		throw new RuntimeException( $message ); } }
check_bootstrap( isset( $GLOBALS['hooks']['rest_api_init'], $GLOBALS['hooks']['wp_enqueue_scripts'], $GLOBALS['hooks']['wp_footer'] ), 'All standalone hooks registered' );
$GLOBALS['hooks']['rest_api_init']();
check_bootstrap( 'POST' === $GLOBALS['route'][2]['methods'] && is_callable( $GLOBALS['route'][2]['permission_callback'] ) && is_callable( $GLOBALS['route'][2]['callback'] ), 'Authenticated-consent route wired' );
$GLOBALS['hooks']['wp_footer']();
check_bootstrap( 'template-parts/cookie-consent' === $GLOBALS['template'], 'Actual banner wired' );
putenv( 'SKYYROSE_ANALYTICS_API_URL' );
check_bootstrap( '' === skyyrose2_analytics_get_fastapi_url(), 'No implicit backend destination' );
putenv( 'SKYYROSE_ANALYTICS_API_URL=https://api.devskyy.app/' );
check_bootstrap( 'https://api.devskyy.app' === skyyrose2_analytics_get_fastapi_url(), 'Explicit backend configuration read' );
putenv( 'SKYYROSE_ANALYTICS_SITE_ID=fixture-site' );
putenv( 'SKYYROSE_ANALYTICS_ENVIRONMENT=test' );
putenv( 'SKYYROSE_ANALYTICS_SECRET=fixture-private-secret-not-for-browser-0123' );
foreach ( array( '', '.min' ) as $suffix ) {
	$GLOBALS['suffix'] = $suffix;
	skyyrose2_analytics_assets();
	check_bootstrap( str_ends_with( $GLOBALS['script']['src'], '/experience-analyzer' . $suffix . '.js' ), 'Selected JS variant enqueued' );
	check_bootstrap( str_ends_with( $GLOBALS['style']['src'], '/cookie-consent' . $suffix . '.css' ), 'Selected CSS variant enqueued' );
	check_bootstrap( hash_file( 'sha256', dirname( __DIR__, 2 ) . '/assets/js/experience-analyzer' . $suffix . '.js' ) === $GLOBALS['script']['version'], 'Selected bytes control cache key' );
	check_bootstrap( str_contains( str_replace( '\\/', '/', $GLOBALS['inline'] ), '/store/wp-json/skyyrose/v1/analytics/events' ) && ! str_contains( $GLOBALS['inline'], getenv( 'SKYYROSE_ANALYTICS_SECRET' ) ) && str_contains( $GLOBALS['inline'], 'fixture-public-key' ), 'Only public page token localized' );
}
echo "PASS: {$count} V2 standalone bootstrap checks (offline; authentication N/A).\n";
