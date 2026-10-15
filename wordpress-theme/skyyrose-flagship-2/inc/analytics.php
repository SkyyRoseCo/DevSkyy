<?php
/**
 * Consent-gated V2 engagement transport. No visitor identity or purchase inference.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;
require_once __DIR__ . '/analytics-protocol.php';

/** Explicit server configuration only; no browser credential or default host. */
function skyyrose2_analytics_get_fastapi_url(): string {
	$url = defined( 'SKYYROSE_ANALYTICS_API_URL' ) ? SKYYROSE_ANALYTICS_API_URL : getenv( 'SKYYROSE_ANALYTICS_API_URL' );
	return is_string( $url ) ? rtrim( $url, '/' ) : '';
}

function skyyrose2_analytics_routes(): void {
	register_rest_route(
		'skyyrose/v1',
		'/analytics/events',
		array(
			'methods'             => 'POST',
			'callback'            => 'skyyrose2_analytics_rest_receive_events',
			'permission_callback' => 'skyyrose2_analytics_rest_events_permission',
		)
	);
}
add_action( 'rest_api_init', 'skyyrose2_analytics_routes' );

function skyyrose2_analytics_assets(): void {
	$suffix = skyyrose2_asset_suffix();
	$css    = '/assets/css/cookie-consent' . $suffix . '.css';
	$js     = '/assets/js/experience-analyzer' . $suffix . '.js';
	wp_enqueue_style( 'skyyrose-cookie-consent', SKYYROSE2_URI . $css, array(), skyyrose2_asset_version( $css ) );
	wp_enqueue_script(
		'skyyrose2-analytics',
		SKYYROSE2_URI . $js,
		array(),
		skyyrose2_asset_version( $js ),
		array(
			'strategy'  => 'defer',
			'in_footer' => true,
		)
	);
	wp_add_inline_script(
		'skyyrose2-analytics',
		'window.skyyroseSEE = ' . wp_json_encode(
			array(
				'key'      => skyyrose2_analytics_analytics_key(),
				'endpoint' => rest_url( 'skyyrose/v1/analytics/events' ),
			)
		) . ';',
		'before'
	);
}
add_action( 'wp_enqueue_scripts', 'skyyrose2_analytics_assets', 25 );

function skyyrose2_analytics_banner(): void {
	get_template_part( 'template-parts/cookie-consent' );
}
add_action( 'wp_footer', 'skyyrose2_analytics_banner', 5 );
