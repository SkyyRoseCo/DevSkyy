<?php
/**
 * Locally authorized hero-world compositions. Candidate status is not approval.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

/**
 * Bind founder-authorized films without changing SKU or WooCommerce authority.
 *
 * @param array  $chapter Resolved commerce chapter.
 * @param string $collection Collection slug.
 * @return array
 */
function skyyrose2_apply_collection_scene_motion( $chapter, $collection ) {
	static $manifest = null;
	if ( null === $manifest ) {
		$file = SKYYROSE2_DIR . '/data/collection-scene-motion.json';
		$decoded = is_readable( $file ) ? json_decode( file_get_contents( $file ), true ) : null; // phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents
		$manifest = is_array( $decoded ) ? $decoded : array();
	}
	$id = (string) ( $chapter['scene_id'] ?? '' );
	$record = $manifest['scenes'][ $id ] ?? array();
	if ( empty( $record['founder_approved_visual'] ) || empty( $record['local_wiring_authorized'] ) || $collection !== ( $record['collection'] ?? '' ) ) {
		return $chapter;
	}
	foreach ( array( 'desktop', 'mobile', 'poster' ) as $key ) {
		$asset = (string) ( $record[ $key ] ?? '' );
		$prefix = 'poster' === $key ? array( 'motion/collection-scenes-k1/', 'generated-candidates/' ) : array( 'motion/collection-scenes-k1/' );
		$allowed = false;
		foreach ( $prefix as $start ) {
			$allowed = $allowed || 0 === strpos( $asset, $start );
		}
		if ( ! $allowed || false !== strpos( $asset, '..' ) || false !== strpos( $asset, '\\' ) || ! is_file( SKYYROSE2_DIR . '/assets/scroll-world/' . $asset ) ) {
			return $chapter;
		}
	}
	$composition = (array) ( $chapter['hero_composition'] ?? array() );
	$composition['variants'] = array();
	$composition['review_message'] = '';
	$chapter['hero_composed'] = true;
	$chapter['hero_composition'] = $composition;
	$chapter['scene_motion'] = $record;
	$chapter['image'] = $record['poster'];
	$chapter['source'] = 'scroll-world';
	$size = getimagesize( SKYYROSE2_DIR . '/assets/scroll-world/' . $record['poster'] );
	$chapter['width'] = $size ? absint( $size[0] ) : absint( $chapter['width'] ?? 1672 );
	$chapter['height'] = $size ? absint( $size[1] ) : absint( $chapter['height'] ?? 941 );
	$chapter['model_layers'] = array();
	$chapter['placeholder_active'] = false;
	$chapter['placeholder_state'] = '';
	$chapter['placeholder_role'] = '';
	$chapter['suppress_model_layers_for_placeholder'] = false;
	$chapter['generation_state'] = 'FOUNDER_APPROVED_MOTION_LOCAL_WIRING';
	return $chapter;
}


/**
 * Replace only the four explicitly authorized scene presentations.
 *
 * Existing SKU resolution and WooCommerce truth remain the commerce authority.
 * The old placeholder and narrative records are retained for rollback.
 *
 * @param array  $chapter Original scene contract.
 * @param string $collection Collection slug.
 * @return array
 */
function skyyrose2_apply_hero_commerce_scene( $chapter, $collection ) {
	static $manifest = null;
	if ( null === $manifest ) {
		$file = SKYYROSE2_DIR . '/data/hero-commerce-scenes-c1.json';
		$decoded = is_readable( $file ) ? json_decode( file_get_contents( $file ), true ) : null; // phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents
		$manifest = is_array( $decoded ) ? $decoded : array();
	}
	$id = (string) ( $chapter['scene_id'] ?? '' );
	$record = $manifest['scenes'][ $id ] ?? array();
	if ( empty( $record['local_wiring_authorized'] ) || $collection !== ( $record['collection'] ?? '' ) ) {
		return $chapter;
	}
	$asset = ltrim( (string) ( $record['asset'] ?? '' ), '/' );
	if ( ! $asset || false !== strpos( $asset, '..' ) || 0 !== strpos( $asset, 'generated-candidates/hero-commerce-c1/' ) || ! is_file( SKYYROSE2_DIR . '/assets/scroll-world/' . $asset ) ) {
		return $chapter;
	}
	$chapter['hero_composed'] = true;
	$chapter['hero_composition'] = $record;
	$chapter['image'] = $asset;
	$chapter['source'] = 'scroll-world';
	$chapter['width'] = absint( $record['width'] ?? 1672 );
	$chapter['height'] = absint( $record['height'] ?? 941 );
	$chapter['label'] = (string) ( $record['label'] ?? $chapter['label'] );
	$chapter['copy'] = (string) ( $record['copy'] ?? $chapter['copy'] );
	$chapter['direction'] = (string) ( $record['alt'] ?? $chapter['direction'] );
	$chapter['product_bindings'] = array_values( array_filter( array_map( 'sanitize_key', (array) $record['product_bindings'] ) ) );
	$chapter['model_layers'] = array(); // Already baked into the composition; never render twice.
	$chapter['placeholder_active'] = false;
	$chapter['placeholder_state'] = '';
	$chapter['placeholder_role'] = '';
	$chapter['suppress_model_layers_for_placeholder'] = false;
	$chapter['generation_state'] = 'LOCAL_WIRED_COMPOSITION_CANDIDATE_NEEDS_REVIEW';
	return $chapter;
}
