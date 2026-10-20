<?php
/** Exact approved production uses; intended recipient is not installed-site attestation. */
defined( 'ABSPATH' ) || exit;

function skyyrose2_production_media_file( $relative, $digest ) {
	if ( ! is_string( $relative ) || ! preg_match( '#^(?:assets|data)/[A-Za-z0-9_./-]+$#D', $relative ) || in_array( '..', explode( '/', $relative ), true ) || ! is_string( $digest ) || ! preg_match( '/^[a-f0-9]{64}$/D', $digest ) || is_link( SKYYROSE2_DIR ) ) { return false; }
	$file = SKYYROSE2_DIR;
	foreach ( explode( '/', $relative ) as $part ) { $file .= '/' . $part; if ( is_link( $file ) ) { return false; } }
	return is_file( $file ) && hash_equals( $digest, skyyrose2_media_sha256( $file ) );
}

function skyyrose2_production_media_authority( $inventory, $target = 'https://skyyrose.co', $site_id = '238510894' ) {
	$doc = skyyrose2_media_usage_document( $inventory['production_media_authority'] ?? null );
	if ( ! $doc || 'https://skyyrose.co' !== $target || '238510894' !== $site_id || 'skyyrose.production-media-authority.v1' !== ( $doc['schema'] ?? '' ) || 'FOUNDER_CONFIRMED' !== ( $doc['authority'] ?? '' ) || 'Corey' !== ( $doc['principal'] ?? '' ) || 'all of them are approved' !== ( $doc['decision_text'] ?? '' ) || 'Sentinel_a6f502418ee48191a8bcccc21a97916d' !== ( $doc['message_id'] ?? '' ) || '9b0f55aa5cfb61f222602a7908436c28be688b4fdc504f542567a4e1011e1717' !== ( $doc['approval_receipt_sha256'] ?? '' ) || $target !== ( $doc['target'] ?? '' ) || $site_id !== ( $doc['expected_site_id'] ?? '' ) || true !== ( $doc['media_use_authorized'] ?? null ) || false !== ( $doc['deployment_authorized'] ?? null ) || array( 'masters' => 22, 'delivery_files' => 113, 'role_memberships' => 53 ) != ( $doc['scope'] ?? null ) || array( array( 'asset' => 'assets/v2-original/scenes/lh-004-back-hood-l2.webp', 'role' => 'collection_scene_back' ) ) != ( $doc['excluded_roles'] ?? null ) ) { return null; }
	$masters = $doc['masters'] ?? null;
	if ( ! is_array( $masters ) || 22 !== count( $masters ) ) { return null; }
	$files = array_fill_keys( array_keys( $masters ), true ); $memberships = 0;
	foreach ( $masters as $relative => $entry ) {
		if ( ! is_string( $relative ) || ! is_array( $entry ) ) { return null; }
		$record = $inventory['assets'][ $relative ] ?? array();
		foreach ( array( 'sha256', 'skus', 'collections' ) as $key ) { if ( ( $entry[ $key ] ?? null ) !== ( $record[ $key ] ?? null ) ) { return null; } }
		$review = array( 'path' => $record['review']['path'] ?? null, 'sha256' => $record['review']['sha256'] ?? null );
		if ( $review != ( $entry['review'] ?? null ) || ! is_array( $entry['skus'] ?? null ) || 1 !== count( $entry['skus'] ) || ! is_array( $entry['collections'] ?? null ) || 1 !== count( $entry['collections'] ) ) { return null; }
		$roles = $entry['roles'] ?? null; $delivery = $entry['delivery_files'] ?? null;
		if ( ! is_array( $roles ) || ! array_is_list( $roles ) || ! $roles || ! is_array( $delivery ) || ! array_is_list( $delivery ) || 'APPROVED_AS_PRESENTED_IN_22_IMAGE_SAFARI_GALLERY' !== ( $entry['creative_treatment'] ?? '' ) ) { return null; }
		foreach ( $roles as $role ) { if ( ! is_string( $role ) || ! in_array( $role, array( 'card_front', 'pdp_on_model_front', 'collection_hero', 'collection_story', 'merchandise_scene' ), true ) ) { return null; } }
		if ( count( array_unique( $roles ) ) !== count( $roles ) ) { return null; }
		$memberships += count( $roles );
		foreach ( $delivery as $item ) {
			if ( ! is_array( $item ) || count( $item ) !== 2 || ! isset( $item['path'], $item['sha256'] ) || ! is_string( $item['path'] ) || isset( $files[ $item['path'] ] ) ) { return null; }
			$child = $inventory['assets'][ $item['path'] ] ?? array();
			if ( ( $child['sha256'] ?? null ) !== $item['sha256'] || ( $child['source_path'] ?? null ) !== $relative || ( $child['source_sha256'] ?? null ) !== $entry['sha256'] || ( $child['skus'] ?? null ) !== $entry['skus'] || ( $child['collections'] ?? null ) !== $entry['collections'] ) { return null; }
			$files[ $item['path'] ] = true;
		}
	}
	return 135 === count( $files ) && 53 === $memberships ? $doc : null;
}

/** Null is outside this approval. Empty roles refuse missing/altered governed authority. */
function skyyrose2_production_media_roles( $relative, $record, $inventory, $target = 'https://skyyrose.co', $site_id = '238510894' ) {
	$doc = skyyrose2_production_media_authority( $inventory, $target, $site_id );
	if ( ! $doc || $record != ( $inventory['assets'][ $relative ] ?? null ) ) { return array(); }
	$master = isset( $doc['masters'][ $relative ] ) ? $relative : ( $record['source_path'] ?? null );
	if ( ! is_string( $master ) || ! isset( $doc['masters'][ $master ] ) ) { return null; }
	$entry = $doc['masters'][ $master ]; $files = array( $master => $entry['sha256'] );
	foreach ( $entry['delivery_files'] as $item ) { $files[ $item['path'] ] = $item['sha256']; }
	if ( ! isset( $files[ $relative ] ) || ( $record['sha256'] ?? '' ) !== $files[ $relative ] || ! skyyrose2_production_media_file( $relative, $files[ $relative ] ) || ! skyyrose2_production_media_file( $master, $entry['sha256'] ) || ! skyyrose2_media_usage_document( $entry['review'] ) ) { return array(); }
	return $entry['roles'];
}
