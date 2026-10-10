<?php
/** Hash-bound responsive copies of the approved card frames. */
defined( 'ABSPATH' ) || exit;

/**
 * Offer a small native archive frame while retaining the existing 640w source.
 * Above the small single-column layout, retain the original delivery choice.
 *
 * @param string $collection Canonical collection slug.
 * @return array<string,string>
 */
function skyyrose2_archive_frame_delivery( $collection ) {
	if ( ! in_array( $collection, array( 'signature', 'black-rose', 'love-hurts', 'kids-capsule' ), true ) ) {
		return array();
	}
	static $cache = array();
	if ( array_key_exists( $collection, $cache ) ) {
		return $cache[ $collection ];
	}
	$cache[ $collection ] = array();
	$relative = 'assets/derived/card-frames/' . $collection . '-384w.webp';
	$source = 'assets/sot/images/product-card-portals/' . $collection . '-portal-statue-640w.webp';
	$collections = skyyrose2_collections();
	if ( ( $collections[ $collection ]['portal_statue']['small'] ?? '' ) !== substr( $source, strlen( 'assets/sot/' ) ) ) {
		return array();
	}
	$root = realpath( SKYYROSE2_DIR . '/assets/derived/card-frames' );
	$manifest = SKYYROSE2_DIR . '/assets/derived/card-frames/manifest.json';
	$file = SKYYROSE2_DIR . '/' . $relative;
	$original = SKYYROSE2_DIR . '/' . $source;
	foreach ( array( $manifest, $file, $original ) as $path ) {
		for ( $component = $path; $component !== SKYYROSE2_DIR; $component = dirname( $component ) ) {
			if ( is_link( $component ) || dirname( $component ) === $component ) {
				return array();
			}
		}
		if ( ! is_readable( $path ) ) {
			return array();
		}
	}
	if ( ! $root || realpath( dirname( $file ) ) !== $root || is_link( dirname( $file ) ) ) {
		return array();
	}
	$data = json_decode( file_get_contents( $manifest ), true ); // phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents
	$record = $data['collections'][ $collection ] ?? array();
	$rendition = $record['rendition'] ?? array();
	if ( 'skyyrose.frame-delivery.v1' !== ( $data['schema'] ?? '' ) || ( $record['source'] ?? '' ) !== $source || ( $rendition['src'] ?? '' ) !== $relative || 384 !== ( $rendition['width'] ?? 0 ) || hash_file( 'sha256', $original ) !== ( $record['source_sha256'] ?? '' ) || hash_file( 'sha256', $file ) !== ( $rendition['sha256'] ?? '' ) ) {
		return array();
	}
	$dimensions = getimagesize( $file );
	$source_dimensions = getimagesize( $original );
	if ( ! $dimensions || ! $source_dimensions || IMAGETYPE_WEBP !== $dimensions[2] || IMAGETYPE_WEBP !== $source_dimensions[2] || 640 !== $source_dimensions[0] || 384 !== $dimensions[0] || $dimensions[1] !== (int) round( $source_dimensions[1] * 384 / 640 ) || $dimensions[1] !== ( $rendition['height'] ?? 0 ) ) {
		return array();
	}
	// An optional closer-width source never removes the validated 384w choice.
	// The parent directory and original authority were checked above.
	$narrow = $record['narrow_rendition'] ?? array();
	$narrow_relative = 'assets/derived/card-frames/' . $collection . '-360w.webp';
	$narrow_file = SKYYROSE2_DIR . '/' . $narrow_relative;
	$narrow_srcset = '';
	if ( is_array( $narrow ) && ( $narrow['src'] ?? null ) === $narrow_relative && 360 === ( $narrow['width'] ?? null ) && ! is_link( $narrow_file ) && is_readable( $narrow_file ) && hash_file( 'sha256', $narrow_file ) === ( $narrow['sha256'] ?? null ) ) {
		$narrow_dimensions = getimagesize( $narrow_file );
		if ( $narrow_dimensions && IMAGETYPE_WEBP === $narrow_dimensions[2] && 360 === $narrow_dimensions[0] && $narrow_dimensions[1] === (int) round( $source_dimensions[1] * 360 / 640 ) && $narrow_dimensions[1] === ( $narrow['height'] ?? null ) ) {
			$narrow_srcset = SKYYROSE2_URI . '/' . $narrow_relative . ' 360w, ';
		}
	}
	$cache[ $collection ] = array(
		'srcset' => $narrow_srcset . SKYYROSE2_URI . '/' . $relative . ' 384w, ' . skyyrose2_sot_asset_uri( substr( $source, strlen( 'assets/sot/' ) ) ) . ' 640w',
		'sizes' => '(max-width: 29.99em) calc(100vw - 2rem), 640px',
	);
	return $cache[ $collection ];
}
