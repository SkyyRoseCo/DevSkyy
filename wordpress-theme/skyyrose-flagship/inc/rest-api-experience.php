<?php
/**
 * Experience Engine REST API
 *
 * Endpoints under the skyyrose/v1 namespace for analytics ingestion,
 * summary retrieval, personalization recommendations, and design
 * narrative management.
 *
 * Public endpoints (analytics, personalization) require no auth but
 * are rate-limited. Admin endpoints require manage_options capability.
 *
 * @package SkyyRose_Flagship
 * @since   6.5.0
 */

defined( 'ABSPATH' ) || exit;

add_action( 'rest_api_init', 'skyyrose_see_register_rest_routes' );

/**
 * Public anti-spam token retained for compatibility with cached theme pages.
 *
 * Not a secret in the auth sense — it ships in page HTML via an inline
 * script — but it removes the bare __return_true from a write route
 * (spec Definition of Done) and raises the bar against blind endpoint
 * spam beyond the per-IP rate limit.
 *
 * @since 1.10.2
 * @return string
 */
function skyyrose_see_analytics_key(): string {
	$key = get_option( 'skyyrose_see_analytics_key', '' );
	if ( ! is_string( $key ) || '' === $key ) {
		$key = wp_generate_password( 32, false, false );
		add_option( 'skyyrose_see_analytics_key', $key, '', true );
	}
	return $key;
}

/**
 * Require explicit consent in both the request and first-party consent cookie.
 *
 * @since 1.10.2
 * @param WP_REST_Request $request Request object.
 * @return true|WP_Error
 */
function skyyrose_see_rest_events_permission( WP_REST_Request $request ) {
	if ( 'accepted' !== sanitize_text_field( wp_unslash( $_COOKIE['skyyrose_cookie_consent'] ?? '' ) ) || 'accepted' !== $request->get_param( 'consent' ) ) {
		return new WP_Error( 'analytics_consent_required', esc_html__( 'Analytics consent is required.', 'skyyrose' ), array( 'status' => 403 ) );
	}
	$provided = (string) $request->get_param( 'k' );
	if ( '' !== $provided && hash_equals( skyyrose_see_analytics_key(), $provided ) ) {
		return true;
	}

	return new WP_Error(
		'rest_forbidden',
		esc_html__( 'Invalid analytics key.', 'skyyrose' ),
		array( 'status' => 401 )
	);
}

/**
 * Register all Experience Engine REST routes.
 */
function skyyrose_see_register_rest_routes(): void {
	$namespace = 'skyyrose/v1';

	// POST /analytics/events — Public, anonymous event ingestion.
	register_rest_route(
		$namespace,
		'/analytics/events',
		array(
			array(
				'methods'             => WP_REST_Server::CREATABLE,
				'callback'            => 'skyyrose_see_rest_receive_events',
				'permission_callback' => 'skyyrose_see_rest_events_permission',
				'args'                => array(
					'events'         => array(
						'required'          => true,
						'validate_callback' => function ( $param ) {
							return is_array( $param ) && count( $param ) >= 1 && count( $param ) <= 50;
						},
						'sanitize_callback' => function ( $param ) {
							return $param;
						},
					),
					'consent'        => array(
						'required'          => true,
						'validate_callback' => function ( $param ) {
							return 'accepted' === $param;
						},
					),
					'schema_version' => array(
						'required'          => true,
						'validate_callback' => function ( $param ) {
							return 1 === $param;
						},
					),
				),
			),
		)
	);

	// GET /analytics/summary — Admin-only dashboard data.
	register_rest_route(
		$namespace,
		'/analytics/summary',
		array(
			array(
				'methods'             => WP_REST_Server::READABLE,
				'callback'            => 'skyyrose_see_rest_get_summary',
				'permission_callback' => 'skyyrose_see_rest_admin_check',
				'args'                => array(
					'days' => array(
						'default'           => 30,
						'validate_callback' => function ( $param ) {
							return is_numeric( $param ) && $param >= 1 && $param <= 90;
						},
						'sanitize_callback' => 'absint',
					),
				),
			),
		)
	);

	// GET /personalization/{hash} — Public, product recommendations.
	register_rest_route(
		$namespace,
		'/personalization/(?P<hash>[a-f0-9]{8,64})',
		array(
			array(
				'methods'             => WP_REST_Server::READABLE,
				'callback'            => 'skyyrose_see_rest_get_recommendations',
				'permission_callback' => 'skyyrose_see_rest_consent_permission',
				'args'                => array(
					'hash'       => array(
						'required'          => true,
						'sanitize_callback' => 'sanitize_text_field',
					),
					'collection' => array(
						'default'           => '',
						// Restrict to the canonical collection slugs so an
						// attacker can't mint unbounded distinct transient cache
						// keys (storage-growth vector) by varying this value.
						// Empty = "no collection filter". Slugs resolve via the
						// SOT (skyyrose_get_collection), not a hardcoded list.
						'validate_callback' => function ( $param ) {
							return '' === $param
								|| ( function_exists( 'skyyrose_get_collection' ) && null !== skyyrose_get_collection( (string) $param ) );
						},
						'sanitize_callback' => 'sanitize_text_field',
					),
					'limit'      => array(
						'default'           => 8,
						'validate_callback' => function ( $param ) {
							return is_numeric( $param ) && $param >= 1 && $param <= 20;
						},
						'sanitize_callback' => 'absint',
					),
				),
			),
		)
	);

	// POST /settings/narrative — Admin-only, submit design narrative.
	register_rest_route(
		$namespace,
		'/settings/narrative',
		array(
			array(
				'methods'             => WP_REST_Server::CREATABLE,
				'callback'            => 'skyyrose_see_rest_submit_narrative',
				'permission_callback' => 'skyyrose_see_rest_admin_check',
				'args'                => array(
					'description' => array(
						'required'          => true,
						'sanitize_callback' => 'sanitize_textarea_field',
					),
					'target'      => array(
						'default'           => 'all',
						'sanitize_callback' => 'sanitize_text_field',
					),
					'config'      => array(
						'default'           => array(),
						'validate_callback' => function ( $param ) {
							return is_array( $param );
						},
					),
					'priority'    => array(
						'default'           => 5,
						'validate_callback' => function ( $param ) {
							return is_numeric( $param ) && $param >= 1 && $param <= 10;
						},
						'sanitize_callback' => 'absint',
					),
				),
			),
		)
	);

	// GET /settings — Admin-only, current settings + module status.
	register_rest_route(
		$namespace,
		'/settings',
		array(
			array(
				'methods'             => WP_REST_Server::READABLE,
				'callback'            => 'skyyrose_see_rest_get_settings',
				'permission_callback' => 'skyyrose_see_rest_admin_check',
			),
			array(
				'methods'             => WP_REST_Server::EDITABLE,
				'callback'            => 'skyyrose_see_rest_update_settings',
				'permission_callback' => 'skyyrose_see_rest_admin_check',
			),
		)
	);
}

/*
--------------------------------------------------------------
 * Permission Callbacks
 *--------------------------------------------------------------*/

/**
 * Permission callback: restrict admin-only REST endpoints to users with
 * `manage_options` capability.
 *
 * @return bool True if current user can manage options.
 */
function skyyrose_see_rest_admin_check(): bool {
	return current_user_can( 'manage_options' );
}

/*
--------------------------------------------------------------
 * Route Handlers
 *--------------------------------------------------------------*/

/**
 * Receive and store behavioral events.
 */
function skyyrose_see_rest_receive_events( WP_REST_Request $request ): WP_REST_Response {
	// Repeat consent at the mutation boundary, including direct internal calls.
	if ( 'accepted' !== sanitize_text_field( wp_unslash( $_COOKIE['skyyrose_cookie_consent'] ?? '' ) ) || 'accepted' !== $request->get_param( 'consent' ) ) {
		return new WP_REST_Response(
			array(
				'status' => 'rejected',
				'error'  => 'consent_required',
			),
			403
		);
	}
	$ip         = sanitize_text_field( wp_unslash( $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0' ) );
	$rate_key   = 'skyyrose_see_rate_' . md5( $ip );
	$rate_count = (int) get_transient( $rate_key );
	if ( $rate_count >= 10 ) {
		return new WP_REST_Response(
			array(
				'status' => 'unavailable',
				'error'  => 'rate_limited',
			),
			429
		);
	}
	set_transient( $rate_key, $rate_count + 1, MINUTE_IN_SECONDS );
	$raw = $request->get_param( 'events' );
	if ( 1 !== $request->get_param( 'schema_version' ) || ! is_array( $raw ) || count( $raw ) < 1 || count( $raw ) > 50 ) {
		return new WP_REST_Response(
			array(
				'status' => 'rejected',
				'error'  => 'invalid_events',
			),
			422
		);
	}
	$events = skyyrose_see_sanitize_events( $raw );
	if ( count( $events ) !== count( $raw ) ) {
		return new WP_REST_Response(
			array(
				'status' => 'rejected',
				'error'  => 'invalid_events',
			),
			422
		);
	}
	$ack = function_exists( 'skyyrose_see_relay_analytics' ) ? skyyrose_see_relay_analytics( $events ) : null;
	if ( null === $ack ) {
		return new WP_REST_Response(
			array(
				'status' => 'unavailable',
				'error'  => 'analytics_unavailable',
			),
			503
		);
	}
	// Existing WP counters are an engagement projection, separate from the
	// durable backend ledger. Duplicate-only retries never inflate this view.
	$projection = array();
	if ( 0 === $ack['duplicates'] && function_exists( 'skyyrose_see_store_events' ) ) {
		foreach ( $events as $event ) {
			$projection[] = array(
				'type'       => 'engagement_' . $event['event_type'],
				'target'     => $event['target'] ?? '',
				'pageType'   => $event['page_type'],
				'collection' => $event['collection'] ?? '',
				'value'      => 0,
				'ts'         => strtotime( $event['occurred_at'] ) * 1000,
			);
		}
	}
	$ack['engagement_projection_stored'] = $projection ? skyyrose_see_store_events( $projection, '' ) : 0;
	return new WP_REST_Response( $ack, 200 );
}

/**
 * Public personalization reads still require an explicit first-party choice.
 *
 * @return true|WP_Error Permission result.
 */
function skyyrose_see_rest_consent_permission() {
	return 'accepted' === sanitize_text_field( wp_unslash( $_COOKIE['skyyrose_cookie_consent'] ?? '' ) )
		? true : new WP_Error( 'consent_required', esc_html__( 'Consent is required.', 'skyyrose' ), array( 'status' => 403 ) );
}

/**
 * Validate the versioned relay fields without silently changing event identity.
 * A single invalid event rejects its whole batch; the backend validates again.
 *
 * @param array $events Browser event batch.
 * @return array Validated events, or empty on any invalid field.
 */
function skyyrose_see_sanitize_events( array $events ): array {
	$types      = array( 'page_view', 'collection_view', 'product_view', 'product_click', 'add_to_cart', 'remove_from_cart', 'begin_checkout', 'lookbook_view', 'hotspot_click', 'search', 'size_guide_open', 'newsletter_signup', 'scroll_depth', 'next_world' );
	$pages      = array( 'home', 'collection', 'product', 'shop', 'cart', 'checkout', 'lookbook', 'immersive', 'search', 'other' );
	$keys       = array( 'event_id', 'session_id', 'event_type', 'occurred_at', 'page_type', 'collection', 'target', 'value', 'properties', 'synthetic' );
	$properties = array( 'action', 'depth', 'sku', 'product_id', 'quantity', 'position', 'scene', 'direction', 'source', 'variant', 'route', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_content' );
	$ids        = array();
	foreach ( $events as $event ) {
		if ( ! is_array( $event ) || array_diff( array_keys( $event ), $keys ) ) {
			return array();
		}
		foreach ( array( 'event_id', 'session_id', 'event_type', 'occurred_at', 'page_type' ) as $required ) {
			if ( ! isset( $event[ $required ] ) || ! is_string( $event[ $required ] ) ) {
				return array();
			}
		}
		if ( ! preg_match( '/^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/', $event['event_id'] )
			|| isset( $ids[ $event['event_id'] ] )
			|| ! preg_match( '/^[A-Za-z0-9_-]{16,100}$/', $event['session_id'] )
			|| ! in_array( $event['event_type'], $types, true )
			|| ! in_array( $event['page_type'], $pages, true )
			|| ! preg_match( '/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$/', $event['occurred_at'] )
			|| false === strtotime( $event['occurred_at'] )
			|| gmdate( 'Y-m-d\TH:i:s', strtotime( $event['occurred_at'] ) ) !== substr( $event['occurred_at'], 0, 19 )
			|| strtotime( $event['occurred_at'] ) < time() - DAY_IN_SECONDS
			|| strtotime( $event['occurred_at'] ) > time() + 60 ) {
			return array();
		}
		$ids[ $event['event_id'] ] = true;
		foreach ( array( 'collection', 'target' ) as $key ) {
			if ( isset( $event[ $key ] ) && ( ! is_string( $event[ $key ] ) || ! preg_match( '/^[A-Za-z0-9_\/.-]{1,160}$/', $event[ $key ] ) || ( 'collection' === $key && strlen( $event[ $key ] ) > 100 ) ) ) {
				return array();
			}
		}
		if ( isset( $event['value'] ) && ( ( ! is_int( $event['value'] ) && ! is_float( $event['value'] ) ) || ! is_finite( (float) $event['value'] ) || $event['value'] < 0 || $event['value'] > 1000000 ) ) {
			return array();
		}
		if ( array_key_exists( 'synthetic', $event ) && ! is_bool( $event['synthetic'] ) ) {
			return array();
		}
		if ( array_key_exists( 'properties', $event ) ) {
			if ( ! is_array( $event['properties'] ) || array_diff( array_keys( $event['properties'] ), $properties ) ) {
				return array();
			}
			foreach ( $event['properties'] as $value ) {
				if ( is_string( $value ) ) {
					if ( ! preg_match( '/^[A-Za-z0-9_\/.-]{1,160}$/', $value ) ) {
						return array();
					}
				} elseif ( ( ! is_int( $value ) && ! is_float( $value ) ) || ! is_finite( (float) $value ) || $value < 0 || $value > 1000000 ) {
					return array();
				}
			}
		}
	}
	return array_values( $events );
}

/**
 * Return analytics summary for the admin dashboard.
 */
function skyyrose_see_rest_get_summary( WP_REST_Request $request ): WP_REST_Response {
	$days = $request->get_param( 'days' );

	// Guard: skyyrose_see_get_summary() defined in experience-analyzer.php which
	// is WooCommerce-gated; return an empty summary rather than a fatal error.
	if ( ! function_exists( 'skyyrose_see_get_summary' ) ) {
		return new WP_REST_Response( array(), 200 );
	}

	$summary = skyyrose_see_get_summary( $days );

	return new WP_REST_Response( $summary, 200 );
}

/**
 * Get personalized product recommendations.
 */
function skyyrose_see_rest_get_recommendations( WP_REST_Request $request ): WP_REST_Response {
	if ( true !== skyyrose_see_rest_consent_permission() ) {
		return new WP_REST_Response( array( 'error' => 'consent_required' ), 403 );
	}
	// Rate limit: 30/min per IP. This public endpoint triggers an upstream ML
	// call and writes a transient per request — without a throttle a single
	// client drives unbounded backend load and cache growth.
	$ip         = sanitize_text_field( wp_unslash( $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0' ) );
	$rate_key   = 'skyyrose_see_recs_rate_' . md5( $ip );
	$rate_count = (int) get_transient( $rate_key );
	if ( $rate_count >= 30 ) {
		return new WP_REST_Response( array( 'error' => 'Rate limited' ), 429 );
	}
	set_transient( $rate_key, $rate_count + 1, MINUTE_IN_SECONDS );

	$hash       = $request->get_param( 'hash' );
	$collection = $request->get_param( 'collection' );
	$limit      = $request->get_param( 'limit' );

	// Cache scoped to hash + collection only. The Referer header was previously
	// mixed into the key — attacker-controlled and unbounded, so a randomized
	// Referer per request exploded transient/object-cache storage. Removed.
	$cache_key = 'skyyrose_see_recs_' . md5( $hash . '|' . $collection );
	$cached    = get_transient( $cache_key );

	if ( false !== $cached && is_array( $cached ) ) {
		return new WP_REST_Response( $cached, 200 );
	}

	// Try ML recommendations from FastAPI.
	$ml_recs = skyyrose_see_get_recommendations(
		$hash,
		array(
			'collection' => $collection,
			'limit'      => $limit,
		)
	);

	if ( $ml_recs && ! empty( $ml_recs['products'] ) ) {
		// Validate all product URLs.
		$ml_recs['products'] = skyyrose_see_validate_product_urls( $ml_recs['products'] );
		$ml_recs['source']   = 'ml';
		set_transient( $cache_key, $ml_recs, HOUR_IN_SECONDS );
		return new WP_REST_Response( $ml_recs, 200 );
	}

	// Fallback: local product catalog recommendations.
	$local_recs = skyyrose_see_local_recommendations( $collection, $limit );
	$response   = array(
		'products' => $local_recs,
		'source'   => 'local',
	);
	set_transient( $cache_key, $response, 30 * MINUTE_IN_SECONDS );

	return new WP_REST_Response( $response, 200 );
}

/**
 * Submit a design narrative directive.
 */
function skyyrose_see_rest_submit_narrative( WP_REST_Request $request ): WP_REST_Response {
	$directive = array(
		'id'          => wp_generate_uuid4(),
		'description' => $request->get_param( 'description' ),
		'target'      => $request->get_param( 'target' ),
		'config'      => $request->get_param( 'config' ),
		'priority'    => $request->get_param( 'priority' ),
	);

	// If FastAPI is available, ask AI to analyze the narrative.
	$ai_config = skyyrose_see_analyze_narrative( $directive['description'] );
	if ( $ai_config && ! empty( $ai_config['config'] ) && is_array( $ai_config['config'] ) ) {
		$directive['config']    = array_merge( (array) $directive['config'], $ai_config['config'] );
		$directive['ai_source'] = true;
	}

	$result = skyyrose_see_process_narrative( $directive );
	$status = 'accepted' === $result['status'] ? 201 : 409;

	return new WP_REST_Response( $result, $status );
}

/**
 * Get current settings and module status.
 */
function skyyrose_see_rest_get_settings( WP_REST_Request $request ): WP_REST_Response {
	$settings = get_option( 'skyyrose_see_settings', array() );
	if ( ! is_array( $settings ) ) {
		$settings = array();
	}

	$settings['version']           = SKYYROSE_SEE_VERSION;
	$settings['active_modules']    = skyyrose_see_get_active_modules();
	$settings['fastapi_available'] = skyyrose_see_fastapi_is_available();

	return new WP_REST_Response( $settings, 200 );
}

/**
 * Update settings.
 */
function skyyrose_see_rest_update_settings( WP_REST_Request $request ): WP_REST_Response {
	$body = $request->get_json_params();

	// Whitelist allowed keys.
	$allowed = array(
		'module_performance_guardian',
		'module_experience_analyzer',
		'module_brand_atmosphere',
		'module_smart_showcase',
		'module_micro_interactions',
		'module_personalization',
		'fastapi_url',
	);

	$update = array();
	foreach ( $allowed as $key ) {
		if ( array_key_exists( $key, $body ) ) {
			$update[ $key ] = $body[ $key ];
		}
	}

	if ( ! empty( $update ) ) {
		skyyrose_see_update_options( $update );
	}

	return new WP_REST_Response( array( 'updated' => array_keys( $update ) ), 200 );
}

/*
--------------------------------------------------------------
 * Helpers
 *--------------------------------------------------------------*/

/**
 * Validate product URLs — only allow http/https schemes.
 *
 * @param array $products Array of product data.
 * @return array Products with validated URLs.
 */
function skyyrose_see_validate_product_urls( array $products ): array {
	return array_map(
		function ( $product ) {
			if ( ! is_array( $product ) ) {
					return $product;
			}
			foreach ( array( 'permalink', 'image', 'url' ) as $url_field ) {
				if ( ! empty( $product[ $url_field ] ) ) {
					$url    = $product[ $url_field ];
					$scheme = wp_parse_url( $url, PHP_URL_SCHEME );
					if ( 'http' !== $scheme && 'https' !== $scheme ) {
						$product[ $url_field ] = '';
					}
				}
			}
			return $product;
		},
		$products
	);
}

/**
 * Get local product recommendations from the catalog.
 *
 * @param string $collection Preferred collection slug.
 * @param int    $limit      Number of products to return.
 * @return array Product data for the curated section.
 */
function skyyrose_see_local_recommendations( string $collection, int $limit = 8 ): array {
	if ( ! function_exists( 'skyyrose_get_product_catalog' ) ) {
		return array();
	}

	$catalog  = skyyrose_get_product_catalog();
	$products = array();

	// Prefer products from the specified collection.
	foreach ( $catalog as $sku => $product ) {
		$prod_collection = $product['collection'] ?? '';
		if ( $collection && $prod_collection === $collection ) {
			$products[] = array(
				'sku'        => $sku,
				'name'       => $product['name'] ?? '',
				'price'      => $product['price'] ?? '',
				'collection' => $prod_collection,
				'permalink'  => home_url( '/product/' . sanitize_title( $product['name'] ?? $sku ) . '/' ),
				'image'      => $product['image'] ?? '',
			);
		}
		if ( count( $products ) >= $limit ) {
			break;
		}
	}

	// Fill remaining slots from other collections.
	if ( count( $products ) < $limit ) {
		foreach ( $catalog as $sku => $product ) {
			if ( count( $products ) >= $limit ) {
				break;
			}
			$prod_collection = $product['collection'] ?? '';
			if ( $collection && $prod_collection === $collection ) {
				continue; // Already included.
			}
			$products[] = array(
				'sku'        => $sku,
				'name'       => $product['name'] ?? '',
				'price'      => $product['price'] ?? '',
				'collection' => $prod_collection,
				'permalink'  => home_url( '/product/' . sanitize_title( $product['name'] ?? $sku ) . '/' ),
				'image'      => $product['image'] ?? '',
			);
		}
	}

	return $products;
}
