<?php
/**
 * FastAPI Client — Bridge to devskyy.app Dashboard
 *
 * HTTP client for the DevSkyy FastAPI backend (main_enterprise.py).
 * Provides ML-powered features: product recommendations, analytics relay,
 * narrative analysis. Degrades gracefully when the backend is unavailable.
 *
 * Connection flow: WordPress theme <-> FastAPI backend <-> devskyy.app dashboard
 *
 * @package SkyyRose_Flagship
 * @since   6.5.0
 */

defined( 'ABSPATH' ) || exit;

/**
 * Resolve the FastAPI backend URL from settings or environment.
 *
 * Priority: option > SEE_FASTAPI_URL env > DEVSKYY_API_URL env > default
 *
 * @return string Base URL (no trailing slash).
 */
function skyyrose_see_get_fastapi_url(): string {
	$url = skyyrose_see_get_option( 'fastapi_url', '' );

	if ( empty( $url ) ) {
		$url = getenv( 'SEE_FASTAPI_URL' ) ?: '';
	}
	if ( empty( $url ) ) {
		$url = getenv( 'DEVSKYY_API_URL' ) ?: '';
	}
	if ( empty( $url ) ) {
		$url = 'http://localhost:8000';
	}

	return rtrim( $url, '/' );
}

/**
 * Hosts the theme may make backend HTTP requests to. The FastAPI backend URL
 * and the MCP URL are admin-settable but must only ever point at known DevSkyy
 * infrastructure; restricting the host to this allowlist (whose DNS we control)
 * is the PRIMARY SSRF defense and defeats DNS-rebinding — a rebindable attacker
 * domain can never be one of these, so a validate-then-refetch TOCTOU cannot
 * point the actual connection at an internal address. Extend via the filter for
 * a custom backend deployment.
 *
 * @return string[] Lowercase host names.
 */
function skyyrose_see_allowed_backend_hosts(): array {
	return apply_filters(
		'skyyrose_see_allowed_backend_hosts',
		array(
			'api.devskyy.app',         // custom domain — REST backend + /mcp mount.
			'devskyy-backend.fly.dev', // REST backend Fly app.
			'devskyy-api.fly.dev',     // MCP Fly app.
			'localhost',               // local dev only (loopback still range-gated below).
			'127.0.0.1',
		)
	);
}

/**
 * Validate a URL is safe for HTTP requests.
 *
 * Only http/https schemes, and the host MUST be on the DevSkyy backend
 * allowlist (primary SSRF/DNS-rebind defense). Private/reserved IP ranges,
 * localhost aliases, and cloud-metadata endpoints are additionally blocked as
 * defense-in-depth.
 *
 * @param string $url URL to validate.
 * @return bool True if safe.
 */
function skyyrose_see_is_safe_url( string $url ): bool {
	$parsed = wp_parse_url( $url );
	if ( ! $parsed || empty( $parsed['host'] ) ) {
		return false;
	}

	$scheme = strtolower( $parsed['scheme'] ?? '' );
	if ( 'http' !== $scheme && 'https' !== $scheme ) {
		return false;
	}

	$host = strtolower( trim( $parsed['host'], '[]' ) );

	// Primary defense: the host must be known DevSkyy infrastructure. This runs
	// BEFORE any DNS resolution, so a rebindable attacker domain is refused
	// outright and the check-time/connect-time TOCTOU window is closed by
	// construction (the connection can only target an allowlisted host whose DNS
	// we control). The range filtering below is retained as defense-in-depth.
	if ( ! in_array( $host, skyyrose_see_allowed_backend_hosts(), true ) ) {
		return false;
	}

	// Resolve to a target IP. Critically: if the host is ALREADY an IP literal
	// (v4 or v6), use it directly — gethostbyname() returns a literal unchanged,
	// and the previous `$ip !== $host` guard then SKIPPED the range check
	// entirely, letting http://10.0.0.1/, http://127.0.0.1/, http://[::1]/ etc.
	// pass. Now the private+reserved-range filter runs unconditionally.
	if ( filter_var( $host, FILTER_VALIDATE_IP ) ) {
		$ip = $host;
	} else {
		$ip = gethostbyname( $host ); // IPv4 resolution; returns $host on failure.
		if ( $ip === $host ) {
			// Unresolvable (or IPv6-only host gethostbyname can't handle) — fail
			// closed rather than allow an unvalidated destination.
			return false;
		}
	}

	// Allow loopback in local development only.
	if ( str_starts_with( $ip, '127.' ) && wp_get_environment_type() === 'local' ) {
		return true;
	}

	// Always apply private + reserved range filtering, for both IPv4 and IPv6.
	// NO_PRIV_RANGE covers RFC 1918; NO_RES_RANGE covers loopback, link-local
	// (169.254/16 — the cloud-metadata range), multicast, and IPv6 equivalents.
	if ( ! filter_var( $ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE ) ) {
		return false;
	}

	return true;
}

/**
 * Check if the FastAPI backend is reachable.
 *
 * Result is cached in a transient scoped to the backend URL.
 *
 * @return bool
 */
function skyyrose_see_fastapi_is_available(): bool {
	$base_url  = skyyrose_see_get_fastapi_url();
	$cache_key = 'skyyrose_see_api_' . md5( $base_url );

	$cached = get_transient( $cache_key );
	if ( false !== $cached ) {
		return (bool) $cached;
	}

	$response = wp_remote_get(
		$base_url . '/health',
		array(
			'timeout'   => 3,
			'sslverify' => apply_filters( 'skyyrose_fastapi_sslverify', true ),
		)
	);

	$available = ! is_wp_error( $response )
		&& 200 === wp_remote_retrieve_response_code( $response );

	set_transient( $cache_key, $available ? 1 : 0, 5 * MINUTE_IN_SECONDS );

	return $available;
}

/*
--------------------------------------------------------------
 * HTTP Request Helpers
 *--------------------------------------------------------------*/

/**
 * Make a POST request to the FastAPI backend.
 *
 * @param string $endpoint    API endpoint path (e.g. '/api/v1/analytics/events').
 * @param array  $body        Request body.
 * @param bool   $non_blocking Fire-and-forget mode (1s timeout, non-blocking).
 * @return array|null Parsed response or null on failure.
 */
function skyyrose_see_fastapi_post( string $endpoint, array $body, bool $non_blocking = false ): ?array {
	$base_url = skyyrose_see_get_fastapi_url();
	$url      = $base_url . $endpoint;

	if ( ! skyyrose_see_is_safe_url( $url ) ) {
		return null;
	}

	$response = wp_remote_post(
		$url,
		array(
			'timeout'   => $non_blocking ? 1 : 10,
			'blocking'  => ! $non_blocking,
			'sslverify' => apply_filters( 'skyyrose_fastapi_sslverify', true ),
			'headers'   => array( 'Content-Type' => 'application/json' ),
			'body'      => wp_json_encode( $body ),
		)
	);

	if ( $non_blocking ) {
		return null;
	}

	return skyyrose_see_parse_api_response( $response );
}

/**
 * Make a GET request to the FastAPI backend.
 *
 * @param string $endpoint API endpoint path.
 * @param array  $params   Query parameters.
 * @return array|null Parsed response or null on failure.
 */
function skyyrose_see_fastapi_get( string $endpoint, array $params = array() ): ?array {
	$base_url = skyyrose_see_get_fastapi_url();
	$url      = $base_url . $endpoint;

	if ( $params ) {
		$url .= '?' . http_build_query( $params );
	}

	if ( ! skyyrose_see_is_safe_url( $url ) ) {
		return null;
	}

	$response = wp_remote_get(
		$url,
		array(
			'timeout'   => 10,
			'sslverify' => apply_filters( 'skyyrose_fastapi_sslverify', true ),
		)
	);

	return skyyrose_see_parse_api_response( $response );
}

/**
 * Parse a wp_remote response into an array.
 *
 * @param array|WP_Error $response wp_remote_* response.
 * @return array|null Decoded JSON or null on failure.
 */
function skyyrose_see_parse_api_response( $response ): ?array {
	if ( is_wp_error( $response ) ) {
		return null;
	}

	$code = wp_remote_retrieve_response_code( $response );
	if ( $code < 200 || $code >= 300 ) {
		return null;
	}

	$body = wp_remote_retrieve_body( $response );
	$data = json_decode( $body, true );

	return is_array( $data ) ? $data : null;
}

/*
--------------------------------------------------------------
 * High-Level API Methods
 *--------------------------------------------------------------*/

/**
 * Resolve a private, explicit site/environment analytics binding.
 * Nothing from this binding is localized into browser scripts.
 *
 * @return array|null Binding, or null while configuration is incomplete.
 */
function skyyrose_see_analytics_binding(): ?array {
	$binding = array();
	foreach ( array( 'site_id', 'environment', 'secret' ) as $key ) {
		$name            = 'SKYYROSE_ANALYTICS_' . strtoupper( $key );
		$binding[ $key ] = defined( $name ) ? constant( $name ) : getenv( $name );
	}
	if ( ! is_string( $binding['site_id'] ) || ! preg_match( '/^[A-Za-z0-9_-]{1,80}$/', $binding['site_id'] )
		|| ! in_array( $binding['environment'], array( 'staging', 'production', 'test' ), true )
		|| ! is_string( $binding['secret'] ) || strlen( $binding['secret'] ) < 32 ) {
		return null;
	}
	return $binding;
}

/**
 * Sign exact JSON bytes and await a durable backend acknowledgement.
 *
 * @param array $events Validated versioned events.
 * @return array|null Validated durable acknowledgement, or null on failure.
 */
function skyyrose_see_relay_analytics( array $events ): ?array {
	$binding = skyyrose_see_analytics_binding();
	$url     = skyyrose_see_get_fastapi_url() . '/api/v1/analytics/ingest';
	if ( null === $binding || ! $events || ! skyyrose_see_is_safe_url( $url ) ) {
		return null;
	}
	// HMAC credentials must never traverse HTTP outside a local test fixture.
	if ( 'https' !== wp_parse_url( $url, PHP_URL_SCHEME ) && 'local' !== wp_get_environment_type() ) {
		return null;
	}
	$body = wp_json_encode(
		array(
			'schema_version' => 1,
			'site_id'        => $binding['site_id'],
			'environment'    => $binding['environment'],
			'consent'        => 'accepted',
			'sent_at'        => gmdate( 'Y-m-d\TH:i:s\Z' ),
			'events'         => $events,
		)
	);
	if ( ! is_string( $body ) || strlen( $body ) > 65536 ) {
		return null; }
	$timestamp = (string) time();
	$response  = wp_remote_post(
		$url,
		array(
			'timeout'     => 10,
			'blocking'    => true,
			'redirection' => 0,
			'sslverify'   => true,
			'headers'     => array(
				'Content-Type'                   => 'application/json',
				'X-SkyyRose-Analytics-Timestamp' => $timestamp,
				'X-SkyyRose-Analytics-Signature' => hash_hmac( 'sha256', $timestamp . '.' . $body, $binding['secret'] ),
			),
			'body'        => $body,
		)
	);
	if ( is_wp_error( $response ) || 200 !== wp_remote_retrieve_response_code( $response ) ) {
		return null;
	}
	$ack = skyyrose_see_parse_api_response( $response );
	$ids = array_column( $events, 'event_id' );
	if ( ! is_array( $ack ) || 'accepted' !== ( $ack['status'] ?? '' )
		|| ( $ack['site_id'] ?? '' ) !== $binding['site_id'] || ( $ack['environment'] ?? '' ) !== $binding['environment']
		|| ( $ack['event_ids'] ?? null ) !== $ids || ! is_int( $ack['accepted'] ?? null ) || ! is_int( $ack['duplicates'] ?? null )
		|| $ack['accepted'] < 0 || $ack['duplicates'] < 0 || count( $events ) !== $ack['accepted'] + $ack['duplicates'] ) {
		return null;
	}
	return $ack;
}

/**
 * Get ML-powered product recommendations.
 *
 * @param string $visitor_hash Anonymous visitor hash.
 * @param array  $context      Collection affinity, recent products, etc.
 * @return array|null Recommendations or null.
 */
function skyyrose_see_get_recommendations( string $visitor_hash, array $context = array() ): ?array {
	if ( ! skyyrose_see_fastapi_is_available() ) {
		return null;
	}

	$cache_key = 'skyyrose_see_recs_' . md5( $visitor_hash . wp_json_encode( $context ) );
	$cached    = get_transient( $cache_key );
	if ( false !== $cached && is_array( $cached ) ) {
		return $cached;
	}

	$response = skyyrose_see_fastapi_post(
		'/api/v1/ml/predict/customer_segmentation',
		array(
			'visitor_hash' => sanitize_text_field( $visitor_hash ),
			'context'      => $context,
		)
	);

	if ( $response ) {
		set_transient( $cache_key, $response, HOUR_IN_SECONDS );
	}

	return $response;
}

/**
 * Submit a design narrative for AI analysis.
 *
 * @param string $narrative The narrative text.
 * @return array|null AI-generated module configurations or null.
 */
function skyyrose_see_analyze_narrative( string $narrative ): ?array {
	if ( ! skyyrose_see_fastapi_is_available() ) {
		return null;
	}

	return skyyrose_see_fastapi_post(
		'/api/v1/marketing/analyze',
		array(
			'narrative' => sanitize_textarea_field( $narrative ),
			'source'    => 'skyyrose-theme',
		)
	);
}
