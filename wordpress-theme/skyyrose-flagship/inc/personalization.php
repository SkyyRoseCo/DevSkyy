<?php
/**
 * Personalization — Curated For You
 *
 * Phase 4 of the SkyyRose Experience Engine.
 *
 * Manages the visitor hash cookie that anchors all behavioral tracking to a
 * single anonymous visitor across sessions. Localizes the hash and REST base
 * URL for personalization.js. The JS module calls the REST endpoint to fetch
 * recommendations, then injects the "Curated For You" grid into the page.
 *
 * @package SkyyRose_Flagship
 * @since   6.4.0
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

// ---------------------------------------------------------------------------
// Visitor hash management
// ---------------------------------------------------------------------------

/**
 * Read a previously consented visitor cookie without creating one.
 *
 * The hash is 16 hex characters (64-bit) — enough to uniquely identify a
 * browser session without storing any personally identifiable information.
 * Identifier creation is performed by consent-gated JavaScript only.
 *
 * @return string Hex visitor hash.
 */
function skyyrose_see_get_visitor_hash(): string {
	// A server-rendered page must never mint an identifier before consent.
	if ( 'accepted' !== sanitize_text_field( wp_unslash( $_COOKIE['skyyrose_cookie_consent'] ?? '' ) ) ) {
		return '';
	}
	$candidate = sanitize_text_field( wp_unslash( $_COOKIE['skyy_visitor'] ?? '' ) );
	return preg_match( '/^[a-f0-9]{16,64}$/', $candidate ) ? $candidate : '';
}

// ---------------------------------------------------------------------------
// JS localization
// ---------------------------------------------------------------------------

/**
 * Localize visitor data for personalization.js.
 *
 * Runs at priority 45 so the skyyrose-personalization handle is already
 * registered (enqueued at priority 42 in skyyrose_enqueue_phase4_assets).
 */
function skyyrose_pg_localize_personalization(): void {
	if ( ! function_exists( 'skyyrose_see_is_module_active' ) ) {
		return;
	}
	if ( ! skyyrose_see_is_module_active( 'personalization' ) ) {
		return;
	}

	// Resolve current collection from page template slug.
	$collection = '';
	if ( is_page() ) {
		$tpl_map    = array(
			'template-collection-black-rose.php'   => 'black-rose',
			'template-collection-love-hurts.php'   => 'love-hurts',
			'template-collection-signature.php'    => 'signature',
			'template-collection-kids-capsule.php' => 'kids-capsule',
		);
		$collection = $tpl_map[ get_page_template_slug() ] ?? '';
	}

	wp_localize_script(
		'skyyrose-personalization',
		'SkyyCurated',
		array(
			'collection' => $collection,
			'restBase'   => '/?rest_route=/skyyrose/v1',
			'restNonce'  => wp_create_nonce( 'wp_rest' ),
			'limit'      => 4,
		)
	);
}
add_action( 'wp_enqueue_scripts', 'skyyrose_pg_localize_personalization', 45 );
