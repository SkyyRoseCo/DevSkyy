<?php
/** Offline WordPress/HMAC relay fixture. Authentication and live accounts: N/A. */
define( 'ABSPATH', __DIR__ );
define( 'MINUTE_IN_SECONDS', 60 );
define( 'DAY_IN_SECONDS', 86400 );
class WP_REST_Request {
	public function __construct( public array $params ) {}
	public function get_param( $key ) { return $this->params[ $key ] ?? null; }
}
class WP_REST_Response {
	public function __construct( public array $data, public int $status = 200 ) {}
}
class WP_Error { public function __construct( public string $code, public string $message = '', public array $data = array() ) {} }
function add_action( ...$args ) {}
function sanitize_text_field( $value ) { return is_scalar( $value ) ? (string) $value : ''; }
function wp_unslash( $value ) { return $value; }
function esc_html__( $value, $domain ) { return $value; }
function get_option( $name, $default = null ) { return 'skyyrose_see_analytics_key' === $name ? 'public-page-token' : $default; }
function skyyrose_see_get_option( $name, $default = null ) { return 'fastapi_url' === $name ? 'http://127.0.0.1:8089' : $default; }
function wp_get_environment_type() { return 'local'; }
function apply_filters( $name, $value ) { return $value; }
function wp_parse_url( $url, $component = -1 ) { return parse_url( $url, $component ); }
function wp_json_encode( $value ) { return json_encode( $value ); }
function get_transient( $key ) { return $GLOBALS['transients'][ $key ] ?? false; }
function set_transient( $key, $value, $ttl ) { $GLOBALS['transients'][ $key ] = $value; }
function wp_remote_retrieve_response_code( $response ) { return $response['code']; }
function wp_remote_retrieve_body( $response ) { return $response['body']; }
function is_wp_error( $value ) { return $value instanceof WP_Error; }
function skyyrose_see_store_events( $events, $hash ) { $GLOBALS['projection'] = $events; return count( $events ); }
function wp_remote_post( $url, $options ) {
	$GLOBALS['last_request'] = array( 'url' => $url, 'options' => $options );
	++$GLOBALS['remote_calls'];
	$payload = json_decode( $options['body'], true );
	$timestamp = $options['headers']['X-SkyyRose-Analytics-Timestamp'];
	$signature = $options['headers']['X-SkyyRose-Analytics-Signature'];
	$valid = hash_equals( hash_hmac( 'sha256', $timestamp . '.' . $options['body'], getenv( 'SKYYROSE_ANALYTICS_SECRET' ) ), $signature );
	if ( ! $valid || 'http_fail' === $GLOBALS['mode'] ) { return array( 'code' => 401, 'body' => '{}' ); }
	$data = array( 'status' => 'accepted', 'accepted' => count( $payload['events'] ), 'duplicates' => 0, 'event_ids' => array_column( $payload['events'], 'event_id' ), 'site_id' => $payload['site_id'], 'environment' => $payload['environment'] );
	switch ( $GLOBALS['mode'] ) {
		case 'wrong_ids': $data['event_ids'] = array( 'forged' ); break;
		case 'wrong_site': $data['site_id'] = 'another-site'; break;
		case 'wrong_env': $data['environment'] = 'production'; break;
		case 'wrong_count': $data['accepted'] = 0; break;
		case 'non_durable': $data['status'] = 'queued'; break;
		case 'duplicate': $data['duplicates'] = count( $payload['events'] ); $data['accepted'] = 0; break;
		case 'transport': return new WP_Error( 'offline' );
		case 'invalid_json': return array( 'code' => 200, 'body' => 'bad json' );
	}
	return array( 'code' => 'queued_status' === $GLOBALS['mode'] ? 202 : 200, 'body' => json_encode( $data ) );
}
require dirname( __DIR__, 2 ) . '/inc/fastapi-client.php';
require dirname( __DIR__, 2 ) . '/inc/rest-api-experience.php';
require dirname( __DIR__, 2 ) . '/inc/personalization.php';
if ( defined( 'SKYYROSE_ANALYTICS_FIXTURE_HELPERS_ONLY' ) ) { return; }
$checks = 0;
function check( bool $condition, string $name ): void {
	if ( ! $condition ) { fwrite( STDERR, "FAIL: {$name}\n" ); exit( 1 ); }
	++$GLOBALS['checks'];
}
putenv( 'SKYYROSE_ANALYTICS_SITE_ID=fixture-site' );
putenv( 'SKYYROSE_ANALYTICS_ENVIRONMENT=test' );
putenv( 'SKYYROSE_ANALYTICS_SECRET=fixture-only-private-signing-secret-00001' );
$event = array( 'event_id' => '00000000-0000-4000-8000-000000000001', 'session_id' => 'fixture-session-0001', 'event_type' => 'product_click', 'occurred_at' => gmdate( 'Y-m-d\TH:i:s\Z' ), 'page_type' => 'collection', 'target' => 'fixture-001', 'properties' => array( 'action' => 'buy' ), 'synthetic' => false );
$request = new WP_REST_Request( array( 'schema_version' => 1, 'consent' => 'accepted', 'events' => array( $event ), 'k' => 'public-page-token' ) );
$GLOBALS['mode'] = 'good';
$GLOBALS['remote_calls'] = 0;
$GLOBALS['transients'] = array();
check( '' === skyyrose_see_get_visitor_hash(), 'server does not mint visitor identifier before consent' );
check( skyyrose_see_rest_events_permission( $request ) instanceof WP_Error, 'request consent without cookie is denied' );
check( 403 === skyyrose_see_rest_receive_events( $request )->status, 'mutation boundary denies missing cookie' );
check( 0 === $GLOBALS['remote_calls'], 'denied request never reaches relay' );
$_COOKIE['skyyrose_cookie_consent'] = 'accepted';
check( true === skyyrose_see_rest_events_permission( $request ), 'accepted cookie/body/public token are permitted' );
check( '' === skyyrose_see_get_visitor_hash(), 'accepted page still does not mint server identifier' );
$response = skyyrose_see_rest_receive_events( $request );
check( 200 === $response->status && 'accepted' === $response->data['status'], 'durable signed ack is returned' );
$sent = $GLOBALS['last_request']['options'];
$body = json_decode( $sent['body'], true );
check( 'fixture-site' === $body['site_id'] && 'test' === $body['environment'] && 1 === $body['schema_version'], 'site/env are server bound' );
check( true === $sent['blocking'] && 0 === $sent['redirection'] && true === $sent['sslverify'], 'relay blocks for response, refuses redirects, verifies TLS' );
check( false === strpos( $sent['body'], getenv( 'SKYYROSE_ANALYTICS_SECRET' ) ), 'private secret never appears in JSON payload' );
$signature = $sent['headers']['X-SkyyRose-Analytics-Signature'];
$timestamp = $sent['headers']['X-SkyyRose-Analytics-Timestamp'];
check( hash_equals( $signature, hash_hmac( 'sha256', $timestamp . '.' . $sent['body'], getenv( 'SKYYROSE_ANALYTICS_SECRET' ) ) ), 'signature covers exact timestamp/raw JSON bytes' );
check( ! hash_equals( $signature, hash_hmac( 'sha256', $timestamp . '.' . $sent['body'] . ' ', getenv( 'SKYYROSE_ANALYTICS_SECRET' ) ) ), 'tampering even one body byte invalidates signature' );
check( 'engagement_product_click' === $GLOBALS['projection'][0]['type'] && 0 === $GLOBALS['projection'][0]['value'], 'local counters remain explicitly engagement only' );
foreach ( array( 'http_fail', 'transport', 'invalid_json', 'wrong_ids', 'wrong_site', 'wrong_env', 'wrong_count', 'non_durable', 'queued_status' ) as $mode ) {
	$GLOBALS['mode'] = $mode;
	$GLOBALS['transients'] = array();
	$GLOBALS['projection'] = array();
	$response = skyyrose_see_rest_receive_events( $request );
	check( 503 === $response->status && 'unavailable' === $response->data['status'] && ! $GLOBALS['projection'], $mode . ' refuses success and local projection' );
}
$GLOBALS['mode'] = 'duplicate';
$GLOBALS['transients'] = array();
$GLOBALS['projection'] = array();
$response = skyyrose_see_rest_receive_events( $request );
check( 200 === $response->status && 1 === $response->data['duplicates'] && ! $GLOBALS['projection'], 'retry ack does not inflate local projection' );
$GLOBALS['mode'] = 'good';
foreach ( array( 'event_type' => 'purchase', 'page_type' => '/arbitrary/path', 'session_id' => 'short', 'event_id' => 'arbitrary', 'occurred_at' => 'yesterday', 'properties' => array( 'email' => 'private@example.test' ), 'synthetic' => 'false', 'value' => -1 ) as $key => $value ) {
	$invalid = $event; $invalid[ $key ] = $value;
	check( array() === skyyrose_see_sanitize_events( array( $invalid ) ), 'reject invalid ' . $key );
}
check( array() === skyyrose_see_sanitize_events( array( $event, $event ) ), 'reject duplicate IDs within a batch' );
putenv( 'SKYYROSE_ANALYTICS_SECRET' );
check( null === skyyrose_see_relay_analytics( array( $event ) ), 'missing private binding fails closed' );
echo "PASS: {$checks} relay/consent checks (offline fixtures; authentication N/A).\n";
