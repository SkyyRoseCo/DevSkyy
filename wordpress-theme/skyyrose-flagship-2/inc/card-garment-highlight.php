<?php
/**
 * Source-bound, reviewed garment regions. This helper never invents a mask.
 *
 * Projection: record.garment_highlight = {sku, status: INDEPENDENT_VISUAL_PASS,
 * source: {path, sha256, width, height}, review: {evidence_sha256,
 * geometry_sha256}, polygons: [{outer: [[integer x, integer y], ...],
 * holes: [[[integer x, integer y], ...], ...]}]}.
 * Coordinates are native source pixels; rings omit a repeated closing point.
 * Outer regions are unioned and may overlap/touch; each polygon owns its holes.
 * Geometry digest: each ring is Mx y Lx y ... Z; join rings by one space,
 * then polygon paths by a newline, without a trailing newline, SHA-256 UTF-8.
 * Review evidence is verified by the authoring gate; runtime verifies its typed
 * binding and geometry digest, exact SKU/front/dimensions and local source bytes.
 * No annotation, invalid geometry or changed source means ordinary commerce.
 *
 * @package SkyyRoseFlagship2
 */
defined( 'ABSPATH' ) || exit;

/** Unique document-local IDs prevent masks leaking across repeated SKU cards. */
function skyyrose2_card_highlight_id() {
	static $sequence = 0;
	return function_exists( 'wp_unique_id' ) ? wp_unique_id( 'sr2-garment-' ) : 'sr2-garment-' . ++$sequence;
}

/** Orientation of three integer pixel points. */
function skyyrose2_highlight_cross( $a, $b, $c ) {
	return ( $b[0] - $a[0] ) * ( $c[1] - $a[1] ) - ( $b[1] - $a[1] ) * ( $c[0] - $a[0] );
}

/** Closed segment intersection, including touching and collinear edges. */
function skyyrose2_highlight_segments_intersect( $a, $b, $c, $d ) {
	if ( max( $a[0], $b[0] ) < min( $c[0], $d[0] ) || max( $c[0], $d[0] ) < min( $a[0], $b[0] ) || max( $a[1], $b[1] ) < min( $c[1], $d[1] ) || max( $c[1], $d[1] ) < min( $a[1], $b[1] ) ) {
		return false;
	}
	$ab_c = skyyrose2_highlight_cross( $a, $b, $c );
	$ab_d = skyyrose2_highlight_cross( $a, $b, $d );
	$cd_a = skyyrose2_highlight_cross( $c, $d, $a );
	$cd_b = skyyrose2_highlight_cross( $c, $d, $b );
	return ( ( $ab_c <= 0 && $ab_d >= 0 ) || ( $ab_c >= 0 && $ab_d <= 0 ) ) && ( ( $cd_a <= 0 && $cd_b >= 0 ) || ( $cd_a >= 0 && $cd_b <= 0 ) );
}

/** Strictly bounded, simple nonzero-area ring. */
function skyyrose2_highlight_valid_ring( $ring, $width, $height ) {
	if ( ! is_array( $ring ) || ! array_is_list( $ring ) || count( $ring ) < 3 || count( $ring ) > 256 ) {
		return false;
	}
	$seen = array();
	foreach ( $ring as $point ) {
		if ( ! is_array( $point ) || ! array_is_list( $point ) || 2 !== count( $point ) || ! is_int( $point[0] ) || ! is_int( $point[1] ) || $point[0] < 0 || $point[1] < 0 || $point[0] > $width || $point[1] > $height ) {
			return false;
		}
		$key = $point[0] . ',' . $point[1];
		if ( isset( $seen[ $key ] ) ) {
			return false;
		}
		$seen[ $key ] = true;
	}
	$count = count( $ring );
	$area  = 0;
	for ( $i = 0; $i < $count; $i++ ) {
		$next = ( $i + 1 ) % $count;
		$area += $ring[ $i ][0] * $ring[ $next ][1] - $ring[ $next ][0] * $ring[ $i ][1];
		// Adjacent collinear reversals create overlapping edges.
		$after = ( $i + 2 ) % $count;
		if ( 0 === skyyrose2_highlight_cross( $ring[ $i ], $ring[ $next ], $ring[ $after ] ) && ( $ring[ $next ][0] - $ring[ $i ][0] ) * ( $ring[ $after ][0] - $ring[ $next ][0] ) + ( $ring[ $next ][1] - $ring[ $i ][1] ) * ( $ring[ $after ][1] - $ring[ $next ][1] ) <= 0 ) {
			return false;
		}
		for ( $j = $i + 1; $j < $count; $j++ ) {
			if ( $j === $next || ( 0 === $i && $j === $count - 1 ) ) {
				continue;
			}
			if ( skyyrose2_highlight_segments_intersect( $ring[ $i ], $ring[ $next ], $ring[ $j ], $ring[ ( $j + 1 ) % $count ] ) ) {
				return false;
			}
		}
	}
	return 0 !== $area;
}

/** Point-in-ring; callers have already rejected touching/intersecting rings. */
function skyyrose2_highlight_inside( $point, $ring ) {
	$inside = false;
	$count  = count( $ring );
	for ( $i = 0, $j = $count - 1; $i < $count; $j = $i++ ) {
		$a = $ring[ $i ];
		$b = $ring[ $j ];
		if ( ( $a[1] > $point[1] ) !== ( $b[1] > $point[1] ) && $point[0] < ( $b[0] - $a[0] ) * ( $point[1] - $a[1] ) / ( $b[1] - $a[1] ) + $a[0] ) {
			$inside = ! $inside;
		}
	}
	return $inside;
}

/** No two rings may cross or touch. */
function skyyrose2_highlight_rings_intersect( $first, $second ) {
	foreach ( $first as $i => $point ) {
		foreach ( $second as $j => $other ) {
			if ( skyyrose2_highlight_segments_intersect( $point, $first[ ( $i + 1 ) % count( $first ) ], $other, $second[ ( $j + 1 ) % count( $second ) ] ) ) {
				return true;
			}
		}
	}
	return false;
}

/** Serialize validated integer points, never caller-supplied SVG. */
function skyyrose2_highlight_ring_path( $ring ) {
	return 'M' . implode( ' L', array_map( static fn( $point ) => $point[0] . ' ' . $point[1], $ring ) ) . ' Z';
}

/** Resolve the optional projection against the independently accepted current front. */
function skyyrose2_card_garment_highlight( $record, $front, $sku ) {
	$annotation = $record['garment_highlight'] ?? null;
	if ( ! is_array( $annotation ) || ! is_array( $front ) || ! $front || ( $annotation['sku'] ?? null ) !== $sku || 'INDEPENDENT_VISUAL_PASS' !== ( $annotation['status'] ?? null ) || 'BLOCKED_PRODUCT_MISMATCH' === ( $front['current_fidelity_status'] ?? null ) ) {
		return null;
	}
	$source = $annotation['source'] ?? null;
	$review = $annotation['review'] ?? null;
	if ( ! is_array( $source ) || ! is_array( $review ) ) {
		return null;
	}
	foreach ( array( 'path', 'sha256', 'width', 'height' ) as $key ) {
		if ( ! isset( $source[ $key ], $front[ $key ] ) || $source[ $key ] !== $front[ $key ] ) {
			return null;
		}
	}
	if ( ! is_int( $source['width'] ) || ! is_int( $source['height'] ) || $source['width'] < 1 || $source['height'] < 1 || $source['width'] > 16384 || $source['height'] > 16384 || ! is_string( $source['path'] ) || ! preg_match( '#^assets/[a-zA-Z0-9_./-]+\.(?:webp|png|jpe?g)$#D', $source['path'] ) || false !== strpos( $source['path'], '..' ) ) {
		return null;
	}
	foreach ( array( $source['sha256'], $review['geometry_sha256'] ?? null, $review['evidence_sha256'] ?? null ) as $digest ) {
		if ( ! is_string( $digest ) || ! preg_match( '/^[a-f0-9]{64}$/D', $digest ) ) {
			return null;
		}
	}
	$path = realpath( SKYYROSE2_DIR . '/' . $source['path'] );
	$root = realpath( SKYYROSE2_DIR . '/assets' );
	if ( ! $path || ! $root || 0 !== strpos( $path, $root . DIRECTORY_SEPARATOR ) || ! is_file( $path ) || ! is_readable( $path ) || ! hash_equals( $source['sha256'], hash_file( 'sha256', $path ) ?: '' ) ) {
		return null;
	}
	$dimensions = getimagesize( $path );
	if ( ! $dimensions || $dimensions[0] !== $source['width'] || $dimensions[1] !== $source['height'] ) {
		return null;
	}
	$polygons = $annotation['polygons'] ?? null;
	if ( ! is_array( $polygons ) || ! array_is_list( $polygons ) || ! $polygons || count( $polygons ) > 16 ) {
		return null;
	}
	$paths  = array();
	$total_points = 0;
	$total_rings = 0;
	foreach ( $polygons as $polygon ) {
		if ( ! is_array( $polygon ) || ! skyyrose2_highlight_valid_ring( $polygon['outer'] ?? null, $source['width'], $source['height'] ) || ! is_array( $polygon['holes'] ?? null ) || ! array_is_list( $polygon['holes'] ) || count( $polygon['holes'] ) > 16 ) {
			return null;
		}
		$total_points += count( $polygon['outer'] );
		$total_rings += 1 + count( $polygon['holes'] );
		foreach ( $polygon['holes'] as $candidate_hole ) {
			if ( ! is_array( $candidate_hole ) ) { return null; }
			$total_points += count( $candidate_hole );
		}
		if ( $total_points > 2048 || $total_rings > 64 ) { return null; }
		$outer = $polygon['outer'];
		$rings    = array( skyyrose2_highlight_ring_path( $outer ) );
		$holes    = array();
		foreach ( $polygon['holes'] as $hole ) {
			if ( ! skyyrose2_highlight_valid_ring( $hole, $source['width'], $source['height'] ) || skyyrose2_highlight_rings_intersect( $outer, $hole ) || ! skyyrose2_highlight_inside( $hole[0], $outer ) ) {
				return null;
			}
			foreach ( $holes as $prior ) {
				if ( skyyrose2_highlight_rings_intersect( $hole, $prior ) || skyyrose2_highlight_inside( $hole[0], $prior ) || skyyrose2_highlight_inside( $prior[0], $hole ) ) {
					return null;
				}
			}
			$holes[] = $hole;
			$rings[] = skyyrose2_highlight_ring_path( $hole );
		}
		$paths[] = implode( ' ', $rings );
	}
	if ( ! hash_equals( $review['geometry_sha256'], hash( 'sha256', implode( "\n", $paths ) ) ) ) {
		return null;
	}
	return array( 'width' => $source['width'], 'height' => $source['height'], 'paths' => $paths );
}
