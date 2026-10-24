<?php
/** Current V2 media identity gate. Generation and historical approval never imply display approval. */
defined( 'ABSPATH' ) || exit;

function skyyrose2_media_inventory() {
	static $inventory = null;
	if ( null === $inventory ) {
		$file      = SKYYROSE2_DIR . '/data/v2-media-eligibility.json';
		$data      = is_readable( $file ) ? json_decode( file_get_contents( $file ), true ) : null;
		$inventory = is_array( $data ) && 'skyyrose.v2.media-eligibility.v1' === ( $data['schema'] ?? '' ) ? $data : array();
	}
	return $inventory;
}

/** Validate immutable bytes, exact binding and independently recorded review. */
function skyyrose2_media_record_allowed( $relative, $record, $role = '', $sku = '' ) {
	if ( ! is_array( $record ) || ! preg_match( '#^(?:assets|images|data)/[A-Za-z0-9_./-]+$#D', $relative ) || false !== strpos( $relative, '..' ) ) {
		return false; }
	$file = realpath( SKYYROSE2_DIR . '/' . $relative );
	$root = realpath( SKYYROSE2_DIR );
	$hash = $record['sha256'] ?? '';
	if ( ! $file || ! $root || 0 !== strpos( $file, $root . DIRECTORY_SEPARATOR ) || is_link( SKYYROSE2_DIR . '/' . $relative ) || ! is_file( $file ) || ! is_string( $hash ) || ! preg_match( '/^[a-f0-9]{64}$/D', $hash ) || ! hash_equals( $hash, skyyrose2_media_sha256( $file ) ) ) {
		return false; }
	$kind = $record['kind'] ?? '';
	if ( ! is_array( $record['roles'] ?? null ) || empty( $record['roles'] ) || ( isset( $record['skus'] ) && ! is_array( $record['skus'] ) ) ) {
		return false; }
	$inventory = skyyrose2_media_inventory();
	if ( in_array( $hash, $inventory['disallowed_legacy_sha256'] ?? array(), true ) ) {
		return false; }
	if ( 'FOUNDER_DIRECTED_NATIVE_FILM' === ( $record['status'] ?? '' ) ) {
		return skyyrose2_native_kids_film_allowed( $relative, $record, $role, $sku ); }
	if ( 'FOUNDER_AUTHORIZED_COLLECTION_FILM' === ( $record['status'] ?? '' ) ) {
		return skyyrose2_founder_film_allowed( $relative, $record, $role, $sku ); }
	if ( 'DELIVERY_DERIVATIVE' === ( $record['status'] ?? '' ) ) {
		return skyyrose2_media_delivery_derivative_allowed( $relative, $record, $role, $sku ); }
	// A new use never rewrites the original card/scene decision. Validate that
	// original first, then the exact source-bound founder reuse grant.
	if ( $role && ! in_array( $role, $record['roles'], true ) ) {
		return 'photograph' === $kind && skyyrose2_media_record_allowed( $relative, $record, '', $sku ) && in_array( $role, skyyrose2_media_usage_roles( $relative, $record ), true );
	}
	if ( in_array( $kind, array( 'housemark', 'font', 'icon', 'house_art' ), true ) ) {
		$authority = SKYYROSE2_DIR . '/data/v2-canonical-media.json';
		if ( ! is_file( $authority ) || is_link( $authority ) || ! hash_equals( 'b4957a6f9210c6c906990a974e7f3f432cc4b2fe9d9ae94d09958e590c1a673e', skyyrose2_media_sha256( $authority ) ) ) {
			return false; }
		$canonical = json_decode( file_get_contents( $authority ), true );
		$exact     = $canonical['assets'][ $relative ] ?? null;
		// House art is the unchanged homepage hero only: no SKU, no collection, no
		// other role, and its own hash-bound restoration receipt.
		if ( 'house_art' === $kind ) {
			if ( $sku || array( 'homepage_hero' ) !== ( $record['roles'] ?? null ) || array() !== ( $record['skus'] ?? null ) || array() !== ( $record['collections'] ?? null ) ) {
				return false; }
			$restore = skyyrose2_media_usage_document( $record['restoration_receipt'] ?? null );
			if ( ! $restore || 'skyyrose.v2.site-art-restoration.v1' !== ( $restore['schema'] ?? '' ) || 'UNCHANGED_EXISTING_V2_HOMEPAGE_ART' !== ( $restore['scope'] ?? '' ) || array(
				'path'   => $relative,
				'sha256' => $hash,
			) !== ( $restore['source'] ?? null ) || 'wherr my homepage hero? my scenes?' !== ( $restore['user_request'] ?? '' ) || 'https://staging-7e48-skyyrose.wpcomstaging.com' !== ( $restore['target'] ?? '' ) ) {
				return false; }
		}
		return is_array( $exact ) && $exact == $record && ( ! $role || in_array( $role, $record['roles'], true ) );
	}
	if ( 'FOUNDER_ACCEPTED' === ( $record['status'] ?? '' ) ) {
		return skyyrose2_founder_card_allowed( $relative, $record, $role, $sku ); }
	if ( in_array( $hash, $inventory['disallowed_legacy_sha256'] ?? array(), true ) || 'photograph' !== $kind || 'INDEPENDENT_VISUAL_PASS' !== ( $record['status'] ?? '' ) || 'V2_ORIGINAL_20261002' !== ( $record['origin'] ?? '' ) || empty( $record['production_id'] ) || empty( $record['roles'] ) || ( $role && ! in_array( $role, $record['roles'], true ) ) || ( $sku && ! in_array( $sku, $record['skus'] ?? array(), true ) ) ) {
		return false; }
	$review = $record['review'] ?? array();
	if ( ! is_array( $review ) ) {
		return false; }
	if ( empty( $review['reviewer'] ) || empty( $record['producer'] ) || $review['reviewer'] === $record['producer'] || 'PASS' !== ( $review['verdict'] ?? '' ) || ! preg_match( '#^data/v2-media-reviews/[A-Za-z0-9_.-]+\.json$#D', $review['path'] ?? '' ) ) {
		return false; }
	$receipt      = SKYYROSE2_DIR . '/' . $review['path'];
	$receipt_real = realpath( $receipt );
	if ( ! $receipt_real || 0 !== strpos( $receipt_real, $root . DIRECTORY_SEPARATOR ) ) {
		return false; }
	if ( ! is_file( $receipt ) || is_link( $receipt ) || ! preg_match( '/^[a-f0-9]{64}$/D', $review['sha256'] ?? '' ) || ! hash_equals( $review['sha256'], skyyrose2_media_sha256( $receipt ) ) ) {
		return false; }
	$data = json_decode( file_get_contents( $receipt ), true );
	if ( ! is_array( $data ) ) {
		return false; }
	foreach ( array( 'roles', 'skus', 'collections' ) as $binding ) {
		if ( ! is_array( $record[ $binding ] ?? null ) || ! array_is_list( $record[ $binding ] ) || ! is_array( $data[ $binding ] ?? null ) || ! array_is_list( $data[ $binding ] ) || $record[ $binding ] !== $data[ $binding ] ) {
			return false; }
		foreach ( $record[ $binding ] as $value ) {
			if ( ! is_string( $value ) || '' === $value ) {
				return false; }
		}
	}
	foreach ( array( 'production_id', 'producer' ) as $binding ) {
		if ( ! is_string( $record[ $binding ] ?? null ) || '' === $record[ $binding ] || $record[ $binding ] !== ( $data[ $binding ] ?? null ) ) {
			return false; }
	}
	return is_array( $data ) && ( $data['asset_sha256'] ?? '' ) === $hash && ( $data['reviewer'] ?? '' ) === $review['reviewer'] && 'PASS' === ( $data['verdict'] ?? '' ) && true === ( $data['v2_originality_pass'] ?? false ) && true === ( $data['product_fidelity_pass'] ?? false );
}

/**
 * Request-scoped sha256 of a file. The gate hashes the same masters, renditions
 * and receipts for every srcset candidate and again at the HTML boundary; the
 * memo is keyed by the file's current stat identity (inode, size, mtime, ctime),
 * re-read on every call, so any write to the file is hashed afresh.
 */
function skyyrose2_media_sha256( $path ) {
	static $memo = array();
	clearstatcache( true, $path );
	$stat = @stat( $path ); // phpcs:ignore WordPress.PHP.NoSilencedErrors.Discouraged -- a missing file is an ordinary fail-closed result.
	if ( ! $stat ) {
		return false; }
	$key = $path . "\0" . $stat['ino'] . ':' . $stat['size'] . ':' . $stat['mtime'] . ':' . $stat['ctime'];
	if ( ! array_key_exists( $key, $memo ) ) {
		$memo[ $key ] = hash_file( 'sha256', $path ); }
	return $memo[ $key ];
}

/** A current, hash-bound owner decision grants only the exact card role. */
function skyyrose2_founder_card_allowed( $relative, $record, $role = '', $sku = '' ) {
	if ( 'photograph' !== ( $record['kind'] ?? '' ) || 'V2_ORIGINAL_20261002' !== ( $record['origin'] ?? '' ) || array( 'card_front' ) !== ( $record['roles'] ?? null ) || ( $role && 'card_front' !== $role ) || ! is_array( $record['skus'] ?? null ) || 1 !== count( $record['skus'] ) || ! is_array( $record['collections'] ?? null ) || 1 !== count( $record['collections'] ) || ( $sku && array( $sku ) !== $record['skus'] ) ) {
		return false; }
	$review = $record['review'] ?? array();
	if ( 'Corey' !== ( $review['reviewer'] ?? '' ) || 'ACCEPTED' !== ( $review['verdict'] ?? '' ) || ! preg_match( '#^data/v2-media-reviews/[A-Za-z0-9_.-]+\.json$#D', $review['path'] ?? '' ) ) {
		return false; }
	$file = SKYYROSE2_DIR . '/' . $review['path'];
	if ( ! is_file( $file ) || is_link( $file ) || ! is_string( $review['sha256'] ?? null ) || ! hash_equals( $review['sha256'], skyyrose2_media_sha256( $file ) ) ) {
		return false; }
	$data = json_decode( file_get_contents( $file ), true );
	if ( ! is_array( $data ) || 'skyyrose.founder-card-acceptance.v1' !== ( $data['schema'] ?? '' ) || 'Corey' !== ( $data['reviewer'] ?? '' ) || 'ACCEPTED' !== ( $data['verdict'] ?? '' ) || 'FOUNDER_CONFIRMED' !== ( $data['authority'] ?? '' ) || ( $data['asset_sha256'] ?? '' ) !== $record['sha256'] || empty( $data['decision_text'] ) || 'ALL 33 PRODUCTS. add them to their card NOW.' !== ( $data['placement_authorization'] ?? '' ) ) {
		return false; }
	foreach ( array( 'roles', 'skus', 'collections', 'producer', 'production_id' ) as $key ) {
		if ( ( $data[ $key ] ?? null ) !== ( $record[ $key ] ?? null ) ) {
			return false; }
	}
	$source = $data['decision_source'] ?? array();
	if ( ! preg_match( '#^data/v2-media-reviews/owner-[A-Za-z0-9_.-]+\.json$#D', $source['path'] ?? '' ) ) {
		return false; }
	$file = SKYYROSE2_DIR . '/' . $source['path'];
	if ( ! is_file( $file ) || is_link( $file ) || ! is_string( $source['sha256'] ?? null ) || ! hash_equals( $source['sha256'], skyyrose2_media_sha256( $file ) ) ) {
		return false; }
	$original = json_decode( file_get_contents( $file ), true );
	if ( ! is_array( $original ) || ( $original['decision_text'] ?? $original['decision_evidence']['verbatim'] ?? '' ) !== $data['decision_text'] ) {
		return false; }
	$schema = $original['schema'] ?? '';
	$status = $original['status'] ?? '';
	if ( 'skyyrose.creative.owner-decision.v1' === $schema ) {
		if ( ! in_array( $status, array( 'FOUNDER_ACCEPTED_CANDIDATES_QUARANTINED', 'FOUNDER_ACCEPTED_CANDIDATE_QUARANTINED' ), true ) ) {
			return false; }
	} elseif ( 'skyyrose.founder-accepted-image-candidate.v2' === $schema ) {
		if ( 'FOUNDER_ACCEPTED_CANDIDATE' !== $status || 'FOUNDER_CONFIRMED' !== ( $original['decision_evidence']['authority'] ?? '' ) ) {
			return false; }
	} else {
		return false; }
	$candidates = $original['candidates'] ?? array( $original['candidate'] ?? array() );
	if ( ! is_array( $candidates ) || ! array_is_list( $candidates ) ) {
		return false; }
	foreach ( $candidates as $candidate ) {
		if ( ! is_array( $candidate ) ) {
			continue; }
		$roles       = $candidate['roles'] ?? null;
		$valid_roles = is_array( $roles ) && array_is_list( $roles );
		if ( $valid_roles ) {
			foreach ( $roles as $candidate_role ) {
				if ( ! is_string( $candidate_role ) || '' === $candidate_role ) {
					$valid_roles = false;
					break; }
			}
		}
		$card_scope = ( $valid_roles && in_array( 'card_front', $roles, true ) ) || ( 'skyyrose.creative.owner-decision.v1' === $schema && 'FOUNDER_ACCEPTED_CANDIDATE_QUARANTINED' === $status && 'ACCEPTED_FOR_PRODUCT_CARD_VISUAL_REVIEW' === ( $original['decision'] ?? '' ) && null === $roles );
		if ( $card_scope && ( $candidate['sha256'] ?? '' ) === $record['sha256'] && ( $candidate['sku'] ?? $original['sku'] ?? '' ) === $record['skus'][0] ) {
			return true; }
	}
	return false;
}

/** Delivery copies inherit only their exact original's independently reviewed roles. */
function skyyrose2_media_delivery_derivative_allowed( $relative, $record, $role = '', $sku = '' ) {
	if ( 'photograph' !== ( $record['kind'] ?? '' ) || 'V2_ORIGINAL_20261002' !== ( $record['origin'] ?? '' ) || isset( $record['review'] ) ) {
		return false; }
	$source = $record['source_path'] ?? '';
	if ( ! is_string( $source ) || $source === $relative || 0 === strpos( $source, 'assets/derived/' ) ) {
		return false; }
	$master = skyyrose2_media_inventory()['assets'][ $source ] ?? null;
	if ( ! is_array( $master ) || 'photograph' !== ( $master['kind'] ?? '' ) || ! in_array( $master['status'] ?? '', array( 'INDEPENDENT_VISUAL_PASS', 'FOUNDER_ACCEPTED' ), true ) || ( $master['sha256'] ?? '' ) !== ( $record['source_sha256'] ?? '' ) || ! skyyrose2_media_record_allowed( $source, $master, $role, $sku ) ) {
		return false; }
	foreach ( array( 'roles', 'skus', 'collections' ) as $binding ) {
		if ( ! is_array( $record[ $binding ] ?? null ) || ! array_is_list( $record[ $binding ] ) || $record[ $binding ] !== ( $master[ $binding ] ?? null ) ) {
			return false; }
	}
	if ( 1 !== count( $record['skus'] ) || 1 !== count( $record['collections'] ) ) {
		return false; }
	$owner  = $record['skus'][0];
	$width  = $record['width'] ?? null;
	$height = $record['height'] ?? null;
	if ( ! is_string( $owner ) || ! preg_match( '/^[a-z0-9-]+$/D', $owner ) || ! is_int( $width ) || ! is_int( $height ) || $width < 1 || $height < 1 || 'assets/derived/card-fronts/' . $owner . '-' . $width . 'w.webp' !== $relative ) {
		return false; }
	$dimensions = getimagesize( SKYYROSE2_DIR . '/' . $relative );
	$original   = getimagesize( SKYYROSE2_DIR . '/' . $source );
	if ( ! $dimensions || ! $original || IMAGETYPE_WEBP !== $dimensions[2] || $dimensions[0] !== $width || $dimensions[1] !== $height || $width > $original[0] || ( ! in_array( $width, array( 160, 320, 480, 768, 1024, 1280, 1536 ), true ) && $width !== $original[0] ) || $height !== (int) round( $original[1] * $width / $original[0], 0, PHP_ROUND_HALF_EVEN ) ) {
		return false; }
	$delivery      = $record['delivery_manifest'] ?? null;
	$manifest_path = 'assets/derived/card-fronts/manifest.json';
	$manifest_file = SKYYROSE2_DIR . '/' . $manifest_path;
	if ( ! is_array( $delivery ) || $manifest_path !== ( $delivery['path'] ?? '' ) || ! is_file( $manifest_file ) || is_link( $manifest_file ) || ! is_string( $delivery['sha256'] ?? null ) || ! preg_match( '/^[a-f0-9]{64}$/D', $delivery['sha256'] ) || ! hash_equals( $delivery['sha256'], skyyrose2_media_sha256( $manifest_file ) ) ) {
		return false; }
	$manifest = json_decode( file_get_contents( $manifest_file ), true );
	$entry    = $manifest['products'][ $owner ] ?? null;
	if ( 'skyyrose.card-renditions.v1' !== ( $manifest['schema'] ?? '' ) || ! is_array( $entry ) || $source !== ( $entry['source'] ?? '' ) || $master['sha256'] !== ( $entry['source_sha256'] ?? '' ) || ( $entry['source_review'] ?? null ) != $master['review'] ) {
		return false; }
	foreach ( array( 'roles', 'skus', 'collections' ) as $binding ) {
		if ( ( $entry[ $binding ] ?? null ) !== $master[ $binding ] ) {
			return false; }
	}
	$encoding = $entry['encoding'] ?? array();
	if ( ! is_array( $encoding ) || ! is_array( $entry['renditions'] ?? null ) || ! array_is_list( $entry['renditions'] ) ) {
		return false; }
	$expected = array(
		'format'          => 'WEBP',
		'quality'         => 90,
		'method'          => 6,
		'resize'          => 'LANCZOS',
		'crop'            => false,
		'upscale'         => false,
		'pillow_version'  => '12.3.0',
		'libwebp_version' => '1.6.0',
		'builder_sha256'  => '5b9247ea80d593b87b1dd4bb15c02460fcb235d6dfc5d4fe8a1f8de8b98de791',
	);
	foreach ( $expected as $key => $value ) {
		if ( ( $encoding[ $key ] ?? null ) !== $value ) {
			return false; }
	}
	$matches = array();
	foreach ( $entry['renditions'] ?? array() as $rendition ) {
		if ( is_array( $rendition ) && ( $rendition['src'] ?? '' ) === $relative ) {
			$matches[] = $rendition; }
	}
	return 1 === count( $matches ) && ( $matches[0]['sha256'] ?? '' ) === $record['sha256'] && ( $matches[0]['width'] ?? null ) === $width && ( $matches[0]['height'] ?? null ) === $height;
}

function skyyrose2_media_path_allowed( $relative, $role = '', $sku = '' ) {
	$data = skyyrose2_media_inventory();
	return skyyrose2_media_record_allowed( $relative, $data['assets'][ $relative ] ?? null, $role, $sku );
}

/** Read a hash-bound receipt without following any aliases or escaping the theme. */
function skyyrose2_media_usage_document( $binding ) {
	if ( ! is_array( $binding ) || count( $binding ) !== 2 || ! isset( $binding['path'], $binding['sha256'] ) || ! is_string( $binding['path'] ) || ! preg_match( '#^data/v2-media-reviews/[A-Za-z0-9_.-]+\.json$#D', $binding['path'] ) || ! is_string( $binding['sha256'] ) || ! preg_match( '/^[a-f0-9]{64}$/D', $binding['sha256'] ) ) {
		return null; }
	$cursor = SKYYROSE2_DIR;
	foreach ( explode( '/', $binding['path'] ) as $part ) {
		$cursor .= '/' . $part;
		if ( is_link( $cursor ) ) {
			return null; }
	}
	$root = realpath( SKYYROSE2_DIR );
	$real = realpath( $cursor );
	if ( ! $root || ! $real || 0 !== strpos( $real, $root . DIRECTORY_SEPARATOR ) || ! is_file( $cursor ) || ! hash_equals( $binding['sha256'], skyyrose2_media_sha256( $cursor ) ) ) {
		return null; }
	$data = json_decode( file_get_contents( $cursor ), true );
	return is_array( $data ) ? $data : null;
}

/** Additional placement authority, distinct from independent visual acceptance. */
function skyyrose2_media_usage_roles( $relative, $record ) {
	if ( ! in_array( $record['status'] ?? '', array( 'INDEPENDENT_VISUAL_PASS', 'FOUNDER_ACCEPTED' ), true ) ) {
		return array(); }
	$grant  = skyyrose2_media_usage_document( skyyrose2_media_inventory()['usage_adoptions'][ $relative ] ?? null );
	$source = array(
		'path'   => $relative,
		'sha256' => $record['sha256'] ?? '',
		'review' => array(
			'path'   => $record['review']['path'] ?? '',
			'sha256' => $record['review']['sha256'] ?? '',
		),
	);
	if ( ! $grant || 'skyyrose.media-usage-adoption.v1' !== ( $grant['schema'] ?? '' ) || 'AUTHORIZED_REUSE' !== ( $grant['status'] ?? '' ) || 'FOUNDER_CONFIRMED' !== ( $grant['authority'] ?? '' ) || 'https://staging-7e48-skyyrose.wpcomstaging.com' !== ( $grant['target'] ?? '' ) || $source != ( $grant['source'] ?? null ) || ( $record['skus'] ?? null ) !== ( $grant['skus'] ?? null ) || ( $record['collections'] ?? null ) !== ( $grant['collections'] ?? null ) ) {
		return array(); }
	$roles = $grant['roles'] ?? null;
	if ( ! is_array( $roles ) || ! array_is_list( $roles ) || ! $roles || ! is_array( $record['skus'] ?? null ) || 1 !== count( $record['skus'] ) || ! is_array( $record['collections'] ?? null ) || 1 !== count( $record['collections'] ) ) {
		return array(); }
	foreach ( $roles as $value ) {
		if ( ! is_string( $value ) || ! in_array( $value, array( 'pdp_on_model_front', 'collection_hero', 'collection_story', 'merchandise_scene' ), true ) ) {
			return array(); }
	}
	if ( count( array_unique( $roles ) ) !== count( $roles ) ) {
		return array(); }
	$authority  = skyyrose2_media_usage_document( $grant['authorization'] ?? null );
	$assignment = array(
		'source'      => $source,
		'skus'        => $grant['skus'],
		'collections' => $grant['collections'],
		'roles'       => $roles,
	);
	if ( ! $authority || 'skyyrose.media-usage-authority.v1' !== ( $authority['schema'] ?? '' ) || 'FOUNDER_CONFIRMED' !== ( $authority['authority'] ?? '' ) || 'do it' !== ( $authority['decision_text'] ?? '' ) || 'REUSE_APPROVED_UNCHANGED_MEDIA' !== ( $authority['mode'] ?? '' ) || ( $authority['target'] ?? '' ) !== $grant['target'] || empty( $authority['antecedent_scope'] ) || $assignment != ( $authority['assignments'][ $relative ] ?? null ) ) {
		return array(); }
	return $roles;
}

/** Effective roles are derived; historical roles and receipts remain unchanged. */
function skyyrose2_media_effective_roles( $relative, $record = null ) {
	$record = $record ?? ( skyyrose2_media_inventory()['assets'][ $relative ] ?? null );
	if ( ! is_array( $record ) || ! skyyrose2_media_record_allowed( $relative, $record ) ) {
		return array(); }
	if ( 'DELIVERY_DERIVATIVE' === ( $record['status'] ?? '' ) ) {
		return skyyrose2_media_effective_roles( $record['source_path'] ); }
	return array_values( array_unique( array_merge( $record['roles'], skyyrose2_media_usage_roles( $relative, $record ) ) ) );
}

function skyyrose2_media_uri( $relative, $role = '', $sku = '' ) {
	if ( ! skyyrose2_media_path_allowed( $relative, $role, $sku ) ) {
		return ''; }
	// Bind the public cache key to the verified bytes, including unchanged paths
	// whose preceding image is still held by the host's long-lived edge cache.
	$record = skyyrose2_media_inventory()['assets'][ $relative ];
	return SKYYROSE2_URI . '/' . $relative . '?v=' . $record['sha256'];
}

/** Canonical collection placement, not a filename-selected or inherited hero. */
function skyyrose2_collection_media( $collection, $role ) {
	if ( ! in_array( $role, array( 'collection_hero', 'collection_story', 'merchandise_scene' ), true ) || ! function_exists( 'skyyrose2_presentation_registry' ) ) {
		return array(); }
	$registry = skyyrose2_presentation_registry();
	$binding  = $registry['collections'][ $collection ]['imagery'][ $role ] ?? null;
	if ( ! is_array( $binding ) || $role !== ( $binding['role'] ?? '' ) || empty( $binding['src'] ) || empty( $binding['sku'] ) ) {
		return array(); }
	$path      = $binding['src'];
	$sku       = $binding['sku'];
	$inventory = skyyrose2_media_inventory();
	$record    = $inventory['assets'][ $path ] ?? null;
	$product   = $registry['products'][ $sku ] ?? null;
	if ( ! is_array( $record ) || ! is_array( $product ) || array( $collection ) !== ( $record['collections'] ?? null ) || array( $sku ) !== ( $record['skus'] ?? null ) || $collection !== ( $product['collection'] ?? '' ) || ( $binding['sha256'] ?? '' ) !== ( $record['sha256'] ?? null ) || ( $binding['usage_adoption'] ?? null ) != ( $inventory['usage_adoptions'][ $path ] ?? null ) ) {
		return array(); }
	if ( 'merchandise_scene' === $role ? empty( $product['is_preorder'] ) : ! empty( $product['is_preorder'] ) ) {
		return array(); }
	$uri = skyyrose2_media_uri( $path, $role, $sku );
	if ( ! $uri ) {
		return array(); }
	$size = getimagesize( SKYYROSE2_DIR . '/' . $path );
	if ( ! $size || $size[0] !== ( $binding['width'] ?? null ) || $size[1] !== ( $binding['height'] ?? null ) || ! is_string( $binding['alt'] ?? null ) || '' === $binding['alt'] ) {
		return array(); }
	$image = array(
		'src'        => $uri,
		'path'       => $path,
		'sha256'     => $record['sha256'],
		'sku'        => $sku,
		'skus'       => array( $sku ),
		'collection' => $collection,
		'role'       => $role,
		'width'      => $size[0],
		'height'     => $size[1],
		'alt'        => $binding['alt'],
	);
	if ( 'assets/v2-original/products/' . $sku . '.png' === $path && function_exists( 'skyyrose2_approved_card_front_renditions' ) ) {
		$manifest = json_decode( file_get_contents( SKYYROSE2_DIR . '/assets/derived/card-fronts/manifest.json' ), true );
		$delivery = $manifest['products'][ $sku ] ?? array();
		if ( ( $delivery['source'] ?? '' ) !== $path || ( $delivery['source_sha256'] ?? '' ) !== $record['sha256'] ) {
			return array(); }
		$image = array_merge( $image, skyyrose2_approved_card_front_renditions( $sku, $image, $delivery, $uri, $role ) );
	}
	return $image;
}

/** Uncropped responsive image used by the collection story, index, home chapters and reserve. */
function skyyrose2_collection_media_markup( $image, $priority = 'lazy', $sizes = '(max-width: 47.99em) calc(100vw - 2rem), (max-width: 74.99em) 48vw, 560px' ) {
	if ( ! is_array( $image ) || empty( $image['src'] ) ) {
		return ''; }
	$src        = $image['display_src'] ?? $image['src'];
	$width      = $image['display_width'] ?? $image['width'];
	$height     = $image['display_height'] ?? $image['height'];
	$responsive = ! empty( $image['srcset'] ) ? ' srcset="' . esc_attr( $image['srcset'] ) . '" sizes="' . esc_attr( $sizes ) . '"' : '';
	return '<img data-media-role="' . esc_attr( $image['role'] ) . '" data-media-sku="' . esc_attr( $image['sku'] ) . '" src="' . esc_url( $src ) . '" width="' . esc_attr( $width ) . '" height="' . esc_attr( $height ) . '" alt="' . esc_attr( $image['alt'] ) . '"' . $responsive . ( 'eager' === $priority ? ' loading="eager" fetchpriority="high"' : ' loading="lazy"' ) . ' decoding="async">';
}

/** External attachments have no V2 byte/source binding and fail closed. */
function skyyrose2_media_url( $url ) {
	if ( ! is_string( $url ) || '' === $url ) {
		return ''; }
	if ( function_exists( 'is_admin' ) && is_admin() && ! ( function_exists( 'wp_doing_ajax' ) && wp_doing_ajax() ) ) {
		return $url; }
	$url    = html_entity_decode( $url, ENT_QUOTES, 'UTF-8' );
	$prefix = rtrim( SKYYROSE2_URI, '/' ) . '/';
	if ( 0 !== strpos( $url, $prefix ) ) {
		return ''; }
	$relative = rawurldecode( explode( '?', explode( '#', substr( $url, strlen( $prefix ) ) )[0] )[0] );
	return skyyrose2_media_uri( $relative );
}

/** A responsive family has one eligible original and identical reviewed bindings. */
function skyyrose2_media_family( $url ) {
	$url    = skyyrose2_media_url( $url );
	$prefix = rtrim( SKYYROSE2_URI, '/' ) . '/';
	if ( ! $url || 0 !== strpos( $url, $prefix ) ) {
		return null; }
	$relative = rawurldecode( explode( '?', explode( '#', substr( $url, strlen( $prefix ) ) )[0] )[0] );
	$record   = skyyrose2_media_inventory()['assets'][ $relative ] ?? null;
	if ( ! is_array( $record ) ) {
		return null; }
	$master = 'DELIVERY_DERIVATIVE' === ( $record['status'] ?? '' ) ? $record['source_path'] : $relative;
	return array(
		'master'      => $master,
		'kind'        => $record['kind'],
		'roles'       => skyyrose2_media_effective_roles( $master ),
		'skus'        => $record['skus'] ?? array(),
		'collections' => $record['collections'] ?? array(),
	);
}

/** Keep only width descriptors with real pixels from the primary image's family. */
function skyyrose2_media_srcset_value( $value, $primary ) {
	if ( ! is_string( $value ) || ! is_string( $primary ) ) {
		return ''; }
	$family = skyyrose2_media_family( $primary );
	if ( ! $family ) {
		return ''; }
	$allowed = array();
	foreach ( explode( ',', html_entity_decode( $value, ENT_QUOTES, 'UTF-8' ) ) as $candidate ) {
		if ( ! preg_match( '/^\s*(\S+)\s+([1-9][0-9]*)w\s*$/D', $candidate, $match ) || skyyrose2_media_family( $match[1] ) !== $family ) {
			continue; }
		$prefix     = rtrim( SKYYROSE2_URI, '/' ) . '/';
		$relative   = rawurldecode( explode( '?', explode( '#', substr( $match[1], strlen( $prefix ) ) )[0] )[0] );
		$dimensions = getimagesize( SKYYROSE2_DIR . '/' . $relative );
		$width      = (int) $match[2];
		if ( ! $dimensions || $width !== $dimensions[0] || isset( $allowed[ $width ] ) ) {
			continue; }
		$allowed[ $width ] = skyyrose2_media_uri( $relative ) . ' ' . $width . 'w';
	}
	return implode( ', ', $allowed );
}

function skyyrose2_media_srcset( $sources, $size_array = array(), $image_src = '' ) {
	if ( ! is_array( $sources ) ) {
		return false; }
	if ( function_exists( 'is_admin' ) && is_admin() && ! ( function_exists( 'wp_doing_ajax' ) && wp_doing_ajax() ) ) {
		return $sources; }
	$filtered = array_filter(
		$sources,
		static function ( $source ) use ( $image_src ) {
			return is_array( $source ) && 'w' === ( $source['descriptor'] ?? '' ) && is_int( $source['value'] ?? null ) && '' !== skyyrose2_media_srcset_value( ( $source['url'] ?? '' ) . ' ' . $source['value'] . 'w', $image_src );
		}
	);
	foreach ( $filtered as &$source ) {
		$source['url'] = skyyrose2_media_url( $source['url'] ); }
	unset( $source );
	return $filtered;
}

function skyyrose2_media_attachment_src( $image ) {
	if ( ! is_array( $image ) ) {
		return false; }
	$url = skyyrose2_media_url( $image[0] ?? '' );
	if ( ! $url ) {
		return false; }
	$image[0] = $url;
	return $image;
}

function skyyrose2_media_variation( $data, $product = null, $variation = null ) {
	if ( ! empty( $data['image'] ) ) {
		$primary  = skyyrose2_media_url( $data['image']['src'] ?? '' );
		$family   = skyyrose2_media_family( $primary );
		$expected = is_a( $variation, 'WC_Product_Variation' ) && function_exists( 'skyyrose2_approved_pdp_front' ) ? skyyrose2_approved_pdp_front( $variation ) : null;
		if ( ! $family || ! in_array( 'pdp_on_model_front', $family['roles'], true ) || ( null !== $expected && ( $expected['path'] ?? '' ) !== $family['master'] ) ) {
			$primary = ''; }
		foreach ( array( 'src', 'full_src', 'gallery_thumbnail_src', 'thumb_src', 'url' ) as $key ) {
			if ( isset( $data['image'][ $key ] ) ) {
				$data['image'][ $key ] = $primary && skyyrose2_media_family( $data['image'][ $key ] ) === $family ? skyyrose2_media_url( $data['image'][ $key ] ) : ''; }
		}
		$data['image']['srcset'] = $primary ? skyyrose2_media_srcset_value( $data['image']['srcset'] ?? '', $primary ) : '';
		if ( $primary ) {
			$data['image']['full_src'] = skyyrose2_media_uri( $family['master'] );
			$dimensions                = getimagesize( SKYYROSE2_DIR . '/' . $family['master'] );
			if ( $dimensions ) {
				$data['image']['full_src_w'] = $dimensions[0];
				$data['image']['full_src_h'] = $dimensions[1]; }
		}
		if ( empty( $data['image']['src'] ) ) {
			$data['image']               = array();
			$data['image_id']            = 0;
			$data['gallery_image_ids']   = array();
			$data['gallery_images_html'] = function_exists( 'skyyrose2_pdp_v2_gallery_markup' ) ? skyyrose2_pdp_v2_gallery_markup( array() ) : ''; } elseif ( isset( $data['gallery_images_html'] ) ) {
			$data['gallery_images_html'] = skyyrose2_media_filter_html( $data['gallery_images_html'], $family ); }
	}
	return $data;
}

/** Last HTML boundary covers raw template URLs and inline style/media data attributes. */
function skyyrose2_media_filter_html( $html, $expected_family = null ) {
	// PHP output buffers supply their integer phase here; only explicit family arrays bind a variation.
	$expected_family = is_array( $expected_family ) ? $expected_family : null;
	$html            = preg_replace_callback(
		'#<(?:img|source|video|link)\b[^>]*>#is',
		static function ( $tag ) use ( $expected_family ) {
			if ( 0 === stripos( $tag[0], '<link' ) && ! preg_match( '/\bas\s*=\s*["\'](?:image|video)["\']/i', $tag[0] ) ) {
				return $tag[0]; }
			$primary_attribute = 0 === stripos( $tag[0], '<link' ) ? 'href' : ( 0 === stripos( $tag[0], '<video' ) ? 'poster' : 'src' );
			$primary           = preg_match( '/\s' . $primary_attribute . '\s*=\s*(["\'])(.*?)\1/is', $tag[0], $match ) ? $match[2] : '';
			if ( $expected_family && skyyrose2_media_family( $primary ) !== $expected_family ) {
				$primary = ''; }
			$filtered = preg_replace_callback(
				'/\s(src|poster|data-[a-z-]*src|data-poster|data-brand-video|data-brand-animation|data-full|data-thumb|data-srcset|imagesrcset|srcset|href)\s*=\s*(["\'])(.*?)\2/is',
				static function ( $attr ) use ( $primary, $expected_family ) {
					$value = in_array( strtolower( $attr[1] ), array( 'srcset', 'imagesrcset', 'data-srcset' ), true ) ? skyyrose2_media_srcset_value( $attr[3], $primary ) : skyyrose2_media_url( $attr[3] );
					if ( $value && $expected_family && ! in_array( strtolower( $attr[1] ), array( 'srcset', 'imagesrcset', 'data-srcset' ), true ) && skyyrose2_media_family( $value ) !== $expected_family ) {
						$value = ''; }
					return $value ? ' ' . $attr[1] . '=' . $attr[2] . htmlspecialchars( $value, ENT_QUOTES, 'UTF-8' ) . $attr[2] : '';
				},
				$tag[0]
			);
			// A withheld source must not leave a broken image or a misleading alt
			// label in the storefront. Keep source/video handling independent.
			if ( 0 === stripos( $filtered, '<img' ) && ! preg_match( '/\ssrc\s*=\s*(["\'])[^"\']+\1/is', $filtered ) ) {
				return ''; }
			return $filtered;
		},
		$html
	);
	return preg_replace_callback(
		'/url\(\s*(["\']?)(.*?)\1\s*\)/i',
		static function ( $match ) use ( $expected_family ) {
			$path = parse_url( html_entity_decode( $match[2], ENT_QUOTES, 'UTF-8' ), PHP_URL_PATH );
			if ( ! is_string( $path ) || ! preg_match( '/\.(?:png|jpe?g|webp|gif|avif|svg|mp4|webm)(?:$)/i', $path ) ) {
				return $match[0]; }
			$url = skyyrose2_media_url( $match[2] );
			if ( $url && $expected_family && skyyrose2_media_family( $url ) !== $expected_family ) {
				$url = ''; }
			return $url ? 'url(' . $match[1] . $url . $match[1] . ')' : 'none';
		},
		$html
	);
}

function skyyrose2_media_start_buffer() {
	if ( ! is_admin() && ! ( function_exists( 'wp_doing_ajax' ) && wp_doing_ajax() ) ) {
		ob_start( 'skyyrose2_media_filter_html' ); }
}
add_action( 'template_redirect', 'skyyrose2_media_start_buffer', 0 );
add_filter( 'wp_get_attachment_url', 'skyyrose2_media_url', PHP_INT_MAX );
add_filter( 'wp_get_attachment_image_src', 'skyyrose2_media_attachment_src', PHP_INT_MAX );
add_filter( 'wp_calculate_image_srcset', 'skyyrose2_media_srcset', PHP_INT_MAX, 3 );
add_filter( 'woocommerce_available_variation', 'skyyrose2_media_variation', PHP_INT_MAX, 3 );
add_filter( 'woocommerce_cart_item_thumbnail', 'skyyrose2_media_filter_html', PHP_INT_MAX );
add_filter( 'post_thumbnail_html', 'skyyrose2_media_filter_html', PHP_INT_MAX );

/** Local native animation provenance; limited to the founder-directed Kids placements. */
function skyyrose2_native_kids_film_allowed( $relative, $record, $role = '', $sku = '' ) {
	$prefix = 'assets/video/collection-heroes/approved/kids-capsule/';
	if ( ! preg_match( '#^' . preg_quote( $prefix, '#' ) . '(runway-r9|runway-r10|runway-r11-8k|runway-r12-v8)/(hero\.(?:mp4|webm)|poster\.webp)$#D', $relative, $match ) ) {
		return false; }
	$prefix .= $match[1] . '/';
	if ( $sku || array() !== ( $record['skus'] ?? null ) || array( 'kids-capsule' ) !== ( $record['collections'] ?? null ) || ! in_array( $relative, array( $prefix . 'hero.mp4', $prefix . 'hero.webm', $prefix . 'poster.webp' ), true ) ) {
		return false; }
	$is_poster     = $relative === $prefix . 'poster.webp';
	$expected_role = $is_poster ? 'collection_hero_poster' : 'collection_hero_video';
	if ( ( $is_poster ? 'house_art' : 'video' ) !== ( $record['kind'] ?? '' ) || array( $expected_role ) !== ( $record['roles'] ?? null ) || ( $role && $role !== $expected_role ) ) {
		return false; }
	$receipt = skyyrose2_media_usage_document( $record['authorization'] ?? null );
	if ( ! $receipt || 'skyyrose.native-collection-film-integration.v1' !== ( $receipt['schema'] ?? '' ) || 'FOUNDER_CONFIRMED' !== ( $receipt['authority'] ?? '' ) || 'https://skyyrose.co' !== ( $receipt['target'] ?? '' ) || 'CONTROLLED_RENDER' !== ( $receipt['production_method'] ?? '' ) || array( 'homepage', 'kids-collection', 'navigation' ) !== ( $receipt['placements'] ?? null ) || ( 'runway-r12-v8' === $match[1] ? 'yes thats her. use this exact model for the animation and replace it on the homepage kids page and menu. keep the rise and zoom and preserve the rollback' : ( 'runway-r11-8k' === $match[1] ? 'i dont need comparisons. upload and configure the better model\\' : 'as you implement those fixes start getting this added to production wire it into the homepage and the kids page and the menu section' ) ) !== ( $receipt['decision_text'] ?? '' ) || 0 !== ( $receipt['paid_provider_calls'] ?? null ) ) {
		return false; }
	if ( 'runway-r11-8k' === $match[1] && ( '51ecea9238a5cc1f2443c28e52048028c9386c46b6755c491496bb05e462c9c6' !== ( $receipt['canonical_mascot_sha256'] ?? '' ) || '286abaab35c48a80806f0430965cce3ec555d1d5fd0c8067312f0456cbe5b647' !== ( $receipt['source_plate_sha256'] ?? '' ) ) ) {
		return false; }
	if ( 'runway-r12-v8' === $match[1] && ( '71f44f993f8eac6920111631479416ae9991c1c7195650b6e7b7c44170bb52ab' !== ( $receipt['canonical_mascot_sha256'] ?? '' ) || '286abaab35c48a80806f0430965cce3ec555d1d5fd0c8067312f0456cbe5b647' !== ( $receipt['source_plate_sha256'] ?? '' ) ) ) {
		return false; }
	$asset = $receipt['assets'][ $relative ] ?? null;
	return is_array( $asset ) && ( $asset['sha256'] ?? '' ) === ( $record['sha256'] ?? null ) && ( $asset['role'] ?? '' ) === $expected_role && preg_match( '/^[a-f0-9]{64}$/D', $receipt['native_master_sha256'] ?? '' );
}

/** Current founder film authorization, exact delivery bytes, no product-role reuse. */
function skyyrose2_founder_film_allowed( $relative, $record, $role = '', $sku = '' ) {
	$collections = $record['collections'] ?? array();
	if ( $sku || array() !== ( $record['skus'] ?? null ) || ! is_array( $collections ) || ! array_is_list( $collections ) || 1 !== count( $collections ) || ! in_array( $collections[0], array( 'signature', 'black-rose', 'love-hurts' ), true ) ) {
		return false; }
	$expected_role = 'video' === ( $record['kind'] ?? '' ) ? 'collection_hero_video' : 'collection_hero_poster';
	if ( ! in_array( $record['kind'] ?? '', array( 'video', 'photograph' ), true ) || array( $expected_role ) !== ( $record['roles'] ?? null ) || ( $role && $expected_role !== $role ) ) {
		return false; }
	if ( ! preg_match( '#^assets/video/collection-heroes/approved/' . preg_quote( $collections[0], '#' ) . '/cinema-20261008/(?:hero\.(?:mp4|webm)|poster\.webp)$#D', $relative ) ) {
		return false; }
	$receipt = skyyrose2_media_usage_document( $record['authorization'] ?? null );
	if ( ! $receipt || 'skyyrose.collection-film-authorization.v1' !== ( $receipt['schema'] ?? '' ) || 'FOUNDER_CONFIRMED' !== ( $receipt['authority'] ?? '' ) || 'wire them in. fix the imagery in production' !== ( $receipt['decision_text'] ?? '' ) || 'https://skyyrose.co' !== ( $receipt['target'] ?? '' ) || $collections[0] !== ( $receipt['collection'] ?? '' ) ) {
		return false; }
	if ( ( 'video' === $record['kind'] ) !== (bool) preg_match( '/\.(mp4|webm)$/D', $relative ) ) {
		return false; }
	$asset       = $receipt['assets'][ $relative ] ?? null;
	$source_hash = $receipt[ 'video' === $record['kind'] ? 'source_master_sha256' : 'poster_source_sha256' ] ?? '';
	return is_array( $asset ) && ( $asset['source_sha256'] ?? null ) === $source_hash && $asset['sha256'] === $record['sha256'] && $asset['role'] === $expected_role && preg_match( '/^[a-f0-9]{64}$/D', $asset['source_sha256'] ?? '' ) && ! empty( $receipt['provider_task'] );
}

/** Resolve the same approved film and poster through both delivery gates. */
function skyyrose2_collection_cinema( $slug, $poster_only = false ) {
	$path     = SKYYROSE2_DIR . '/data/collection-hero-motion.json';
	$manifest = is_file( $path ) ? json_decode( file_get_contents( $path ), true ) : array();
	$source   = $manifest['collections'][ $slug ]['source']['file'] ?? '';
	$poster   = skyyrose2_media_uri( $source, 'collection_hero_poster' );
	if ( ! $poster ) {
		return array(); }
	if ( $poster_only ) {
		return array(
			'poster' => $poster,
			'motion' => array(),
		); }
	$motion = skyyrose2_collection_hero_motion( $slug, $source );
	// A verified Kids poster remains usable even when a video fails its independent gate.
	return $motion || 'kids-capsule' === $slug ? array(
		'poster' => $poster,
		'motion' => $motion,
	) : array();
}
