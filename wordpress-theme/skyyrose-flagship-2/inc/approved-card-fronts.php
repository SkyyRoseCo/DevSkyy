<?php
/**
 * Theme-local approved card fronts. WooCommerce attachments remain unchanged.
 *
 * @package SkyyRoseFlagship2
 */
defined( 'ABSPATH' ) || exit;

/** Resolve the display identity without inheriting a different variation SKU. */
function skyyrose2_product_media_identity( $product ) {
	if ( ! is_a( $product, 'WC_Product' ) ) { return null; }
	// Edit context avoids Woo's view getter silently inheriting a parent SKU.
	$sku = strtolower( trim( (string) $product->get_sku( 'edit' ) ) );
	if ( is_a( $product, 'WC_Product_Variation' ) && function_exists( 'wc_get_product' ) ) {
		$parent = wc_get_product( $product->get_parent_id() );
		if ( ! is_a( $parent, 'WC_Product' ) ) { return null; }
		$parent_sku = strtolower( trim( (string) $parent->get_sku( 'edit' ) ) );
		if ( '' === $sku || $sku === $parent_sku ) {
			$attributes = $product->get_variation_attributes();
			if ( ! is_array( $attributes ) || ! $attributes ) { return null; }
			foreach ( $attributes as $attribute => $value ) {
				if ( ! in_array( $attribute, array( 'attribute_size', 'attribute_pa_size' ), true ) || ! is_string( $value ) ) { return null; }
			}
			return $parent;
		}
	}
	return preg_match( '/^[a-z0-9-]+$/D', $sku ) ? $product : null;
}

/**
 * One SKU/role consumer of the current V2 eligibility inventory.
 * This function reads approved delivery records; it grants no approval and never
 * consults inherited card manifests, filename guesses or Woo media assignments.
 */
function skyyrose2_product_media_front( $product, $role ) {
	$product = skyyrose2_product_media_identity( $product );
	if ( ! $product || ! in_array( $role, array( 'card_front', 'pdp_on_model_front' ), true ) ) { return array(); }
	$sku = strtolower( trim( (string) $product->get_sku( 'edit' ) ) );
	$presentation = skyyrose2_product_presentation( $product );
	$collection = $presentation['collection'] ?? '';
	if ( ! is_string( $collection ) || '' === $collection ) { return array(); }
	// Generated directly from logo-registry.json; inventory alone cannot select a
	// superseded photograph after the maker's current SKU binding has changed.
	static $canonical_fronts = null;
	if ( null === $canonical_fronts ) {
		$source = SKYYROSE2_DIR . '/data/approved-card-fronts.json';
		$canonical_fronts = is_readable( $source ) && ! is_link( $source ) ? json_decode( file_get_contents( $source ), true ) : array();
	}
	$current = 1 === ( $canonical_fronts['schema_version'] ?? null ) ? ( $canonical_fronts['products'][ $sku ] ?? array() ) : array();
	if ( ! is_array( $current ) || ( $current['src'] ?? '' ) !== 'assets/v2-original/products/' . $sku . '.png' || ( $current['source_sha256'] ?? '' ) !== ( $current['sha256'] ?? null ) || ! preg_match( '/^[a-f0-9]{64}$/D', $current['sha256'] ?? '' ) ) { return array(); }
	$matches = array();
	foreach ( (array) ( skyyrose2_media_inventory()['assets'] ?? array() ) as $path => $record ) {
		if ( 0 === strpos( $path, 'assets/derived/card-fronts/' ) || ! is_array( $record ) || 'photograph' !== ( $record['kind'] ?? '' ) || array( $sku ) !== ( $record['skus'] ?? null ) || array( $collection ) !== ( $record['collections'] ?? null ) || ! is_array( $record['roles'] ?? null ) || ! in_array( $role, $record['roles'], true ) ) { continue; }
		$uri = skyyrose2_media_uri( $path, $role, $sku );
		if ( ! $uri ) { continue; }
		$dimensions = getimagesize( SKYYROSE2_DIR . '/' . $path );
		if ( ! $dimensions || $dimensions[0] !== ( $current['width'] ?? null ) || $dimensions[1] !== ( $current['height'] ?? null ) ) { continue; }
		$matches[] = array(
			'src' => $uri, 'path' => $path, 'sha256' => $record['sha256'],
			'width' => (int) $dimensions[0], 'height' => (int) $dimensions[1],
			'alt' => $product->get_name(), 'sku' => $sku, 'roles' => $record['roles'],
			'collections' => $record['collections'], 'status' => $record['status'],
		);
	}
	// Competing assignments are an explicit delivery gap, not an arbitrary choice.
	if ( 1 !== count( $matches ) ) { return array(); }
	$front = $matches[0];
	$record = skyyrose2_media_inventory()['assets'][ $front['path'] ];
	if ( $front['path'] !== $current['src'] || $front['sha256'] !== $current['sha256'] || $front['status'] !== ( $current['current_fidelity_status'] ?? '' ) || ( $record['review'] ?? null ) != ( $current['review'] ?? array() ) ) { return array(); }
	static $renditions = null;
	if ( null === $renditions ) {
		$path = SKYYROSE2_DIR . '/assets/derived/card-fronts/manifest.json';
		$renditions = is_readable( $path ) ? json_decode( file_get_contents( $path ), true ) : array();
	}
	$delivery = $renditions['products'][ $sku ] ?? array();
	if ( 'skyyrose.card-renditions.v1' === ( $renditions['schema'] ?? '' ) && is_array( $delivery ) && is_array( $delivery['renditions'] ?? null ) && ( $delivery['source_sha256'] ?? '' ) === $front['sha256'] && ( $delivery['source'] ?? '' ) === $front['path'] ) {
		$front = array_merge( $front, skyyrose2_approved_card_front_renditions( $sku, $front, $delivery, $front['src'], $role ) );
	}
	return $front;
}

/** Same exact independently eligible SKU front for every collection's cards. */
function skyyrose2_approved_card_front( $product ) {
	return skyyrose2_product_media_front( $product, 'card_front' );
}

/** PDP approval is explicit, even when its pixels are the same card master. */
function skyyrose2_approved_pdp_front( $product ) {
	return skyyrose2_product_media_front( $product, 'pdp_on_model_front' );
}

/** Woo's image API covers classic cart, mini-cart and order thumbnails. */
function skyyrose2_product_v2_thumbnail( $html, $product, $size = 'woocommerce_thumbnail', $attributes = array() ) {
	if ( function_exists( 'is_admin' ) && is_admin() && ! ( function_exists( 'wp_doing_ajax' ) && wp_doing_ajax() ) ) { return $html; }
	$front = skyyrose2_approved_card_front( $product );
	if ( ! $front ) { return ''; }
	$src = $front['thumbnail_src'] ?? $front['card_src'] ?? $front['src'];
	$width = $front['thumbnail_width'] ?? $front['card_width'] ?? $front['width'];
	$height = $front['thumbnail_height'] ?? $front['card_height'] ?? $front['height'];
	$class = is_array( $attributes ) && is_string( $attributes['class'] ?? null ) ? $attributes['class'] : 'attachment-woocommerce_thumbnail size-woocommerce_thumbnail';
	$responsive = ! empty( $front['srcset'] ) ? ' srcset="' . esc_attr( $front['srcset'] ) . '" sizes="96px"' : '';
	return '<img src="' . esc_url( $src ) . '" width="' . esc_attr( $width ) . '" height="' . esc_attr( $height ) . '" alt="' . esc_attr( $front['alt'] ) . '" class="' . esc_attr( $class ) . '"' . $responsive . ' loading="lazy" decoding="async">';
}
add_filter( 'woocommerce_product_get_image', 'skyyrose2_product_v2_thumbnail', 90, 4 );

/** Store API image arrays drive block-cart/product thumbnails independently of get_image(). */
function skyyrose2_store_api_v2_images( $response, $server, $request ) {
	if ( ! is_a( $response, 'WP_REST_Response' ) || ! is_object( $request ) || ! method_exists( $request, 'get_route' ) || ! preg_match( '#^/wc/store/v[0-9]+/(?:products(?:/[0-9]+)?|cart(?:/.*)?)$#D', $request->get_route() ) ) { return $response; }
	$replace = static function ( $item ) {
		if ( ! is_array( $item ) || ! isset( $item['id'] ) || ! array_key_exists( 'images', $item ) ) { return $item; }
		$product = wc_get_product( (int) $item['id'] );
		$front = skyyrose2_approved_card_front( $product );
		$item['images'] = $front ? array( array( 'id' => 0, 'src' => $front['display_src'] ?? $front['card_src'] ?? $front['src'], 'thumbnail' => $front['thumbnail_src'] ?? $front['card_src'] ?? $front['src'], 'srcset' => $front['srcset'] ?? '', 'sizes' => $front['sizes'] ?? '', 'name' => $product->get_name(), 'alt' => $front['alt'] ) ) : array();
		return $item;
	};
	$data = $response->get_data();
	if ( ! is_array( $data ) ) { return $response; }
	if ( isset( $data['items'] ) && is_array( $data['items'] ) ) {
		$data['items'] = array_map( $replace, $data['items'] );
	} elseif ( array_is_list( $data ) ) {
		$data = array_map( $replace, $data );
	} else {
		$data = $replace( $data );
	}
	$response->set_data( $data );
	return $response;
}
add_filter( 'rest_post_dispatch', 'skyyrose2_store_api_v2_images', 90, 3 );

/** Resolve only derivative files whose bytes match their source manifest. */
function skyyrose2_approved_card_front_renditions( $sku, $front, $delivery, $original_url, $role = 'card_front' ) {
	$srcset                  = array();
	$resolved                = array();
	static $rendition_hashes = array();
	foreach ( $delivery['renditions'] ?? array() as $rendition ) {
		if ( ! is_array( $rendition ) ) {
			continue;
		}
		$width         = (int) ( $rendition['width'] ?? 0 );
		$relative      = 'assets/derived/card-fronts/' . $sku . '-' . $width . 'w.webp';
		$expected_hash = (string) ( $rendition['sha256'] ?? '' );
		$path          = SKYYROSE2_DIR . '/' . $relative;
		if ( $width > $front['width'] || ( ! in_array( $width, array( 160, 320, 480, 768, 1024, 1280, 1536 ), true ) && $width !== $front['width'] ) || (int) ( $rendition['height'] ?? 0 ) !== (int) round( $front['height'] * $width / $front['width'] ) || ( $rendition['src'] ?? '' ) !== $relative || ! preg_match( '/^[a-f0-9]{64}$/D', $expected_hash ) || ! is_file( $path ) || is_link( $path ) || ! is_readable( $path ) ) {
			continue;
		}
		if ( ! array_key_exists( $path, $rendition_hashes ) ) {
			$hash                      = hash_file( 'sha256', $path );
			$rendition_hashes[ $path ] = is_string( $hash ) ? $hash : '';
		}
		if ( ! hash_equals( $expected_hash, $rendition_hashes[ $path ] ) ) {
			continue;
		}
		$dimensions = getimagesize( $path );
		if ( ! $dimensions || $dimensions[0] !== $width || $dimensions[1] !== (int) $rendition['height'] ) { continue; }
		if ( ! skyyrose2_media_path_allowed( $relative, $role, $sku ) ) { continue; }
		$url      = SKYYROSE2_URI . '/' . $relative;
		$srcset[] = $url . ' ' . $width . 'w';
		if ( 160 === $width ) {
			$resolved['thumbnail_src'] = $url;
			$resolved['thumbnail_width'] = $width;
			$resolved['thumbnail_height'] = (int) $rendition['height'];
		}
		if ( 768 === $width ) {
			$resolved['display_src'] = $url;
			$resolved['display_width'] = $width;
			$resolved['display_height'] = (int) $rendition['height'];
		}
		if ( 480 === $width ) {
			$resolved['card_src']    = $url;
			$resolved['card_width']  = $width;
			$resolved['card_height'] = (int) $rendition['height'];
		}
	}
	if ( $srcset ) {
		$resolved['srcset'] = implode( ', ', $srcset );
		$resolved['sizes']  = '(max-width: 47.99em) calc((100vw - 3rem) / 2), (max-width: 74.99em) calc((100vw - 5rem) / 3), 360px';
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
