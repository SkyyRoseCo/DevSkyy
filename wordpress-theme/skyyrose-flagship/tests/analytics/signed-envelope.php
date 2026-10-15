<?php
/** Emit a request signed by the real theme relay against offline WP stubs. */
define( 'SKYYROSE_ANALYTICS_FIXTURE_HELPERS_ONLY', true );
require __DIR__ . '/relay.php';
// Fixed fixture-only credentials; never reads a developer's account secrets.
putenv( 'SKYYROSE_ANALYTICS_SITE_ID=fixture-site' );
putenv( 'SKYYROSE_ANALYTICS_ENVIRONMENT=test' );
putenv( 'SKYYROSE_ANALYTICS_SECRET=fixture-only-private-signing-secret-00001' );
$GLOBALS['mode'] = 'good';
$GLOBALS['remote_calls'] = 0;
$events = array(
	array(
		'event_id' => '00000000-0000-4000-8000-000000000001',
		'session_id' => 'fixture-session-0001',
		'event_type' => 'product_click',
		'occurred_at' => gmdate( 'Y-m-d\TH:i:s\Z' ),
		'page_type' => 'collection',
		'target' => 'fixture-001',
		'properties' => array( 'action' => 'buy' ),
		'synthetic' => false,
	),
);
if ( isset( $argv[1] ) ) {
	$events = json_decode( file_get_contents( $argv[1] ), true, 32, JSON_THROW_ON_ERROR );
}
if ( ! is_array( $events ) || count( skyyrose_see_sanitize_events( $events ) ) !== count( $events ) || ! skyyrose_see_relay_analytics( $events ) ) {
	fwrite( STDERR, "Fixture relay signing failed.\n" ); exit( 1 );
}
$options = $GLOBALS['last_request']['options'];
echo json_encode( array( 'body' => $options['body'], 'headers' => $options['headers'] ), JSON_THROW_ON_ERROR ), "\n";
