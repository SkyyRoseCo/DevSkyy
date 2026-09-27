<?php
/**
 * Theme-local approved card fronts. WooCommerce attachments remain unchanged.
 *
 * @package SkyyRoseFlagship2
 */
defined( 'ABSPATH' ) || exit;

/** Resolve an approved front by exact SKU, falling back when unavailable. */
function skyyrose2_approved_card_front( $product ) {
	static $manifest = null;
	if ( ! $product || ! is_a( $product, 'WC_Product' ) ) {
		return array();
	}
	if ( null === $manifest ) {
		$path = SKYYROSE2_DIR . '/data/approved-card-fronts.json';
		$manifest = is_readable( $path ) ? json_decode( file_get_contents( $path ), true ) : array(); // phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents
	}
	if ( ! is_array( $manifest ) || 1 !== ( $manifest['schema_version'] ?? null ) ) {
		return array();
	}
	$sku = strtolower( trim( (string) $product->get_sku() ) );
	$front = $manifest['products'][ $sku ] ?? array();
	if ( ! is_array( $front ) || ! isset( $front['src'], $front['width'], $front['height'], $front['alt'] ) || ! is_string( $front['src'] ) || ! is_string( $front['alt'] ) ) {
		return array();
	}
	if ( ! preg_match( '#^assets/[a-zA-Z0-9_./-]+\.(?:webp|png|jpe?g)$#D', $front['src'] ) || false !== strpos( $front['src'], '..' ) || (int) $front['width'] < 1 || (int) $front['height'] < 1 ) {
		return array();
	}
	$asset = realpath( SKYYROSE2_DIR . '/' . $front['src'] );
	$root = realpath( SKYYROSE2_DIR . '/assets' );
	if ( ! $asset || ! $root || 0 !== strpos( $asset, $root . DIRECTORY_SEPARATOR ) || ! is_file( $asset ) || ! is_readable( $asset ) ) {
		return array();
	}
	$source_hash = $front['sha256'] ?? '';
	static $source_hashes = array();
	if ( ! array_key_exists( $asset, $source_hashes ) ) {
		$source_hashes[ $asset ] = hash_file( 'sha256', $asset ) ?: '';
	}
	$actual_hash = $source_hashes[ $asset ];
	if ( 'FOUNDER_APPROVED_V2_CARD' !== ( $front['scene_status'] ?? '' ) || ! is_string( $source_hash ) || ! preg_match( '/^[a-f0-9]{64}$/D', $source_hash ) || ! is_string( $actual_hash ) || ! hash_equals( $source_hash, $actual_hash ) ) {
		return array();
	}
	$result = array(
		'src' => SKYYROSE2_URI . '/' . $front['src'],
		'path' => $front['src'],
		'sha256' => $source_hash,
		'scene_status' => $front['scene_status'],
		'width' => (int) $front['width'],
		'height' => (int) $front['height'],
		'alt' => $front['alt'],
	);
	// Delivery copies inherit the exact accepted front; they never confer approval
	// on opening/editorial media or alter the original manifest and source pixels.
	static $renditions = null;
	if ( null === $renditions ) {
		$rendition_path = SKYYROSE2_DIR . '/assets/derived/card-fronts/manifest.json';
		$renditions = is_readable( $rendition_path ) ? json_decode( file_get_contents( $rendition_path ), true ) : array(); // phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents
	}
	$delivery = $renditions['products'][ $sku ] ?? array();
	if ( is_array( $delivery ) && is_array( $delivery['renditions'] ?? null ) && 'skyyrose.card-renditions.v1' === ( $renditions['schema'] ?? '' ) && ( $delivery['source_sha256'] ?? '' ) === ( $front['sha256'] ?? '' ) && ( $delivery['source'] ?? '' ) === $front['src'] ) {
		$result = array_merge( $result, skyyrose2_approved_card_front_renditions( $sku, $front, $delivery, $result['src'] ) );
	}
	return $result;
}

/** Resolve only derivative files whose bytes match their source manifest. */
function skyyrose2_approved_card_front_renditions( $sku, $front, $delivery, $original_url ) {
	$srcset = array();
	$resolved = array();
	static $rendition_hashes = array();
	foreach ( $delivery['renditions'] ?? array() as $rendition ) {
		if ( ! is_array( $rendition ) ) {
			continue;
		}
		$width = (int) ( $rendition['width'] ?? 0 );
		$relative = 'assets/derived/card-fronts/' . $sku . '-' . $width . 'w.webp';
		$expected_hash = (string) ( $rendition['sha256'] ?? '' );
		$path = SKYYROSE2_DIR . '/' . $relative;
		if ( ! in_array( $width, array( 320, 480, 768 ), true ) || (int) ( $rendition['height'] ?? 0 ) !== (int) round( $front['height'] * $width / $front['width'] ) || ( $rendition['src'] ?? '' ) !== $relative || ! preg_match( '/^[a-f0-9]{64}$/D', $expected_hash ) || ! is_file( $path ) || is_link( $path ) || ! is_readable( $path ) ) {
			continue;
		}
		if ( ! array_key_exists( $path, $rendition_hashes ) ) {
			$hash = hash_file( 'sha256', $path );
			$rendition_hashes[ $path ] = is_string( $hash ) ? $hash : '';
		}
		if ( ! hash_equals( $expected_hash, $rendition_hashes[ $path ] ) ) {
			continue;
		}
		$url = SKYYROSE2_URI . '/' . $relative;
		$srcset[] = $url . ' ' . $width . 'w';
		if ( 480 === $width ) {
			$resolved['card_src'] = $url;
			$resolved['card_width'] = $width;
			$resolved['card_height'] = (int) $rendition['height'];
		}
	}
	if ( $srcset ) {
		$srcset[] = $original_url . ' ' . $front['width'] . 'w';
		$resolved['srcset'] = implode( ', ', $srcset );
		$resolved['sizes'] = '(max-width: 47.99em) calc((100vw - 3rem) / 2), (max-width: 74.99em) calc((100vw - 5rem) / 3), 360px';
	}
	return $resolved;
}

/** Replace the WooCommerce primary in the reel, retaining other view order. */
function skyyrose2_card_front_reel_views( $image_ids, $primary_id, $front ) {
	$views = array();
	if ( $front ) {
		$views[] = array( 'front' => $front );
	}
	foreach ( $image_ids as $image_id ) {
		if ( $front && (int) $image_id === (int) $primary_id ) {
			continue;
		}
		$views[] = array( 'id' => $image_id );
	}
	return array_slice( $views, 0, 3 );
}
