<?php
/** Synthetic fixture adapter. Never package as a theme or production MU plugin. */
if ( ! defined( 'ABSPATH' ) || ! defined( 'SKYYROSE_V2_DELIVERY_FIXTURE' ) || true !== SKYYROSE_V2_DELIVERY_FIXTURE || '127.0.0.1:18308' !== ( $_SERVER['HTTP_HOST'] ?? '' ) ) {
	return;
}
add_filter( 'pre_option_home', static function () { return 'http://127.0.0.1:18308'; }, PHP_INT_MAX );
add_filter( 'pre_option_siteurl', static function () { return 'http://127.0.0.1:18308'; }, PHP_INT_MAX );

// Core can initialize WP_CONTENT_URL before MU plugins. Adapt only the known
// fixture authority through URL APIs, never arbitrary strings/HTML or DB data.
$skyyrose_v2_delivery_url = static function ( $url ) {
	return is_string( $url ) ? preg_replace( '#^http://127\.0\.0\.1:18303(?=/|\?|\#|$)#', 'http://127.0.0.1:18308', $url ) : $url;
};
foreach ( array( 'content_url', 'plugins_url', 'theme_root_uri', 'includes_url' ) as $skyyrose_v2_delivery_filter ) {
	add_filter( $skyyrose_v2_delivery_filter, $skyyrose_v2_delivery_url, PHP_INT_MAX );
}
add_filter( 'upload_dir', static function ( $uploads ) use ( $skyyrose_v2_delivery_url ) {
	foreach ( array( 'url', 'baseurl' ) as $key ) {
		if ( isset( $uploads[ $key ] ) ) {
			$uploads[ $key ] = $skyyrose_v2_delivery_url( $uploads[ $key ] );
		}
	}
	return $uploads;
}, PHP_INT_MAX );

// Proof requests hash this very response before Nginx encodes it. This is not
// enabled for Lighthouse/ordinary requests, and never compares two HTML nonces.
if ( '1' === ( $_SERVER['HTTP_X_V2_DELIVERY_PROOF'] ?? '' ) ) {
	ob_start( static function ( $body, $phase ) {
		if ( ( $phase & PHP_OUTPUT_HANDLER_FINAL ) && ! headers_sent() ) {
			header( 'X-V2-Fixture-Body-SHA256: ' . hash( 'sha256', $body ) );
		}
		return $body;
	} );
}
