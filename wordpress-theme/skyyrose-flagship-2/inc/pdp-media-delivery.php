<?php
/** Same-source PDP delivery; never grants media authority or changes attachments. */
defined( 'ABSPATH' ) || exit;

/** Limit the native AJAX presentation boundary to Woo's variation endpoint. */
function skyyrose2_pdp_gallery_request() {
	if ( function_exists( 'is_product' ) && is_product() ) {
		return true;
	}
	return function_exists( 'wp_doing_ajax' ) && wp_doing_ajax() && (
		'get_variation' === ( $_REQUEST['wc-ajax'] ?? '' ) ||
		'woocommerce_get_variation' === ( $_REQUEST['action'] ?? '' )
	);
}

/** Read the stable permission snapshot only for its owning parent product. */
function skyyrose2_pdp_media_context( $product ) {
	$context = $GLOBALS['skyyrose2_pdp_media_context'] ?? null;
	return is_a( $product, 'WC_Product' ) && is_array( $context ) && $context['product_id'] === $product->get_id() ? $context : null;
}

/** Capture before Woo's temporary gallery getters run; callers restore in finally. */
function skyyrose2_pdp_capture_media_context( $product ) {
	return array(
		'product_id' => $product->get_id(),
		'product' => $product,
		'media' => skyyrose2_product_commerce_media( $product ),
		'original_ids' => array_values( array_unique( array_filter( array_map( 'intval', array_merge( array( $product->get_image_id() ), $product->get_gallery_image_ids() ) ) ) ) ),
	);
}

/** Display-only attributes shared by every native gallery representation. */
function skyyrose2_pdp_gallery_attributes( $attributes, $attachment_id, $main_image, $product ) {
	$context = skyyrose2_pdp_media_context( $product );
	if ( ! $context || ! in_array( (int) $attachment_id, array_map( 'intval', $context['media']['ids'] ), true ) ) {
		return $attributes;
	}
	$attributes['loading'] = $main_image ? 'eager' : 'lazy';
	$attributes['fetchpriority'] = $main_image ? 'high' : 'auto';
	$attributes['decoding'] = 'async';
	$delivery = skyyrose2_pdp_media_delivery( $product, (int) $attachment_id );
	if ( $delivery ) {
		foreach ( array( 'src', 'srcset', 'sizes' ) as $key ) {
			$attributes[ $key ] = $delivery[ $key ];
		}
	}
	return $attributes;
}

/** Source-size hint for the PDP's contain-fit gallery at its real height. */
function skyyrose2_pdp_gallery_sizes( $width, $height ) {
	$width = (int) $width;
	$height = (int) $height;
	if ( $width < 1 || $height < 1 ) {
		return '';
	}
	$ratio = $width / $height;
	// Match the final PDP CSS overrides: 20rem–30rem at 52svh on mobile,
	// 28rem–44rem at 64svh on desktop. The gallery uses object-fit:contain,
	// so the encoded source slot is height × its own aspect ratio.
	return sprintf( '(max-width: 47.99rem) clamp(%dpx, %.4fsvh, %dpx), clamp(%dpx, %.4fsvh, %dpx)', (int) ceil( 320 * $ratio ), 52 * $ratio, (int) ceil( 480 * $ratio ), (int) ceil( 448 * $ratio ), 64 * $ratio, (int) ceil( 704 * $ratio ) );
}

/** Resolve an approved front only for that SKU's exact ghost primary. */
function skyyrose2_pdp_approved_ghost_front( $attachment_id, $product ) {
	if ( ! is_a( $product, 'WC_Product' ) || ! $attachment_id || ! function_exists( 'skyyrose2_approved_card_front' ) ) {
		return array();
	}
	$sku = sanitize_key( (string) $product->get_sku() );
	if ( ! $sku || (int) $attachment_id !== (int) $product->get_image_id() ) {
		return array();
	}
	$attachment_url = (string) wp_get_attachment_url( $attachment_id );
	$attachment_path = (string) parse_url( $attachment_url, PHP_URL_PATH );
	if ( ! $attachment_path || basename( $attachment_path ) !== $sku . '-ghost-front.webp' ) {
		return array();
	}
	$front = skyyrose2_approved_card_front( $product );
	if ( empty( $front['src'] ) || empty( $front['path'] ) || empty( $front['sha256'] ) || 'FOUNDER_APPROVED_V2_CARD' !== ( $front['scene_status'] ?? '' ) ) {
		return array();
	}
	$root = realpath( SKYYROSE2_DIR . '/assets' );
	$file = realpath( SKYYROSE2_DIR . '/' . $front['path'] );
	$actual_hash = $file && is_file( $file ) && is_readable( $file ) ? hash_file( 'sha256', $file ) : false;
	if ( ! $root || ! $file || 0 !== strpos( $file, $root . DIRECTORY_SEPARATOR ) || ! is_string( $actual_hash ) || ! hash_equals( $front['sha256'], $actual_hash ) ) {
		return array();
	}
	$src = $front['card_src'] ?? $front['src'];
	$width = (int) ( $front['card_width'] ?? $front['width'] ?? 0 );
	$height = (int) ( $front['card_height'] ?? $front['height'] ?? 0 );
	$full_width = (int) ( $front['width'] ?? 0 );
	$full_height = (int) ( $front['height'] ?? 0 );
	$sizes = skyyrose2_pdp_gallery_sizes( $full_width, $full_height );
	if ( ! $width || ! $height || ! $full_width || ! $full_height || ! $sizes ) {
		return array();
	}
	return array_merge( $front, array( 'pdp_src' => $src, 'pdp_width' => $width, 'pdp_height' => $height, 'pdp_sizes' => $sizes ) );
}

/** Replace only a matching ghost primary frame with its approved model front. */
function skyyrose2_pdp_approved_ghost_front_html( $html, $attachment_id, $product ) {
	$front = skyyrose2_pdp_approved_ghost_front( $attachment_id, $product );
	if ( ! $front ) {
		return $html;
	}
	return skyyrose2_pdp_approved_ghost_front_markup( $front );
}

/** Render a validated approved front, retaining the original if derivatives fail. */
function skyyrose2_pdp_approved_ghost_front_markup( $front ) {
	if ( ! is_array( $front ) || empty( $front['src'] ) || empty( $front['pdp_src'] ) || empty( $front['alt'] ) || empty( $front['pdp_width'] ) || empty( $front['pdp_height'] ) || empty( $front['width'] ) || empty( $front['height'] ) || empty( $front['pdp_sizes'] ) ) {
		return '';
	}
	$src = $front['pdp_src'];
	$width = $front['pdp_width'];
	$height = $front['pdp_height'];
	$full_width = (int) $front['width'];
	$full_height = (int) $front['height'];
	$alt = esc_attr( $front['alt'] );
	$full = esc_url( $front['src'] );
	$responsive = ! empty( $front['srcset'] ) ? ' srcset="' . esc_attr( $front['srcset'] ) . '" sizes="' . esc_attr( $front['pdp_sizes'] ) . '"' : '';
	return '<div data-thumb="' . esc_url( $src ) . '" data-thumb-alt="' . $alt . '" class="woocommerce-product-gallery__image"><a href="' . $full . '"><img width="' . $width . '" height="' . $height . '" src="' . esc_url( $src ) . '" class="wp-post-image" alt="' . $alt . '"' . $responsive . ' data-src="' . $full . '" data-large_image="' . $full . '" data-large_image_width="' . $full_width . '" data-large_image_height="' . $full_height . '" loading="eager" fetchpriority="high" decoding="async"></a></div>';
}

/** The first native gallery image receives the same primary substitution. */
function skyyrose2_pdp_approved_ghost_front_filter( $product ) {
	$rendered = false;
	return static function ( $html, $attachment_id ) use ( &$rendered, $product ) {
		if ( $rendered ) {
			return $html;
		}
		$approved = skyyrose2_pdp_approved_ghost_front_html( $html, $attachment_id, $product );
		if ( $approved !== $html ) {
			$rendered = true;
		}
		return $approved;
	};
}

/** Variation data must not swap an approved ghost primary back on screen. */
function skyyrose2_pdp_approved_ghost_front_variation_image( $image, $attachment_id, $product ) {
	$front = skyyrose2_pdp_approved_ghost_front( $attachment_id, $product );
	if ( ! $front || ! is_array( $image ) ) {
		return $image;
	}
	return skyyrose2_pdp_variation_image_from_approved_front( $image, $front );
}

/** Apply validated front data while explicitly clearing stale responsive attrs. */
function skyyrose2_pdp_variation_image_from_approved_front( $image, $front ) {
	if ( ! is_array( $image ) || ! is_array( $front ) ) {
		return $image;
	}
	$image['src'] = $front['pdp_src'];
	$image['src_w'] = $front['pdp_width'];
	$image['src_h'] = $front['pdp_height'];
	if ( ! empty( $front['srcset'] ) ) {
		$image['srcset'] = $front['srcset'];
		$image['sizes'] = $front['pdp_sizes'];
	} else {
		$image['srcset'] = '';
		$image['sizes'] = '';
	}
	$image['full_src'] = $front['src'];
	$image['full_src_w'] = (int) $front['width'];
	$image['full_src_h'] = (int) $front['height'];
	$image['gallery_thumbnail_src'] = $front['pdp_src'];
	$image['gallery_thumbnail_src_w'] = $front['pdp_width'];
	$image['gallery_thumbnail_src_h'] = $front['pdp_height'];
	$image['thumb_src'] = $front['pdp_src'];
	$image['thumb_src_w'] = $front['pdp_width'];
	$image['thumb_src_h'] = $front['pdp_height'];
	$image['alt'] = $front['alt'];
	return $image;
}

/** Hash a readable local file once per request. Remote wrappers are never read. */
function skyyrose2_pdp_delivery_file_hash( $path ) {
	static $hashes = array();
	if ( ! is_string( $path ) || false !== strpos( $path, '://' ) ) {
		return '';
	}
	$local = realpath( $path );
	if ( ! $local || ! is_file( $local ) || ! is_readable( $local ) ) {
		return '';
	}
	if ( ! isset( $hashes[ $local ] ) ) {
		$hashes[ $local ] = hash_file( 'sha256', $local ) ?: '';
	}
	return $hashes[ $local ];
}

/**
 * Return responsive display attributes only after native PDP permission and byte proof.
 *
 * The accepted front's sha256 identifies the rendition source. Its source_sha256
 * identifies an earlier production input and is deliberately not interchangeable.
 * The caller retains native attachment IDs, alt text, full/lightbox and thumbnails.
 */
function skyyrose2_pdp_media_delivery( $product, $attachment_id ) {
	if ( ! is_a( $product, 'WC_Product' ) || ! $attachment_id ) {
		return array();
	}
	$context = skyyrose2_pdp_media_context( $product );
	$media = $context ? $context['media'] : skyyrose2_product_commerce_media( $product );
	if ( ! in_array( $media['state'] ?? '', array( 'commerce', 'editorial' ), true ) || ! in_array( (int) $attachment_id, array_map( 'intval', $media['ids'] ?? array() ), true ) ) {
		return array();
	}
	static $accepted = null;
	static $derived = null;
	if ( null === $accepted ) {
		$accepted_path = SKYYROSE2_DIR . '/data/approved-card-fronts.json';
		$derived_path  = SKYYROSE2_DIR . '/assets/derived/card-fronts/manifest.json';
		$accepted = is_readable( $accepted_path ) ? json_decode( file_get_contents( $accepted_path ), true ) : array(); // phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents
		$derived  = is_readable( $derived_path ) ? json_decode( file_get_contents( $derived_path ), true ) : array(); // phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents
	}
	$sku = strtolower( trim( (string) $product->get_sku() ) );
	$front = $accepted['products'][ $sku ] ?? array();
	$record = $derived['products'][ $sku ] ?? array();
	if ( ! is_array( $front ) || ! is_array( $record ) ) {
		return array();
	}
	$hash = $front['sha256'] ?? '';
	if ( 1 !== ( $accepted['schema_version'] ?? null ) || 'skyyrose.card-renditions.v1' !== ( $derived['schema'] ?? '' ) || 'FOUNDER_APPROVED_V2_CARD' !== ( $front['scene_status'] ?? '' ) || ! is_string( $hash ) || ! preg_match( '/^[a-f0-9]{64}$/D', $hash ) || ! preg_match( '/^[a-z0-9-]+$/D', $sku ) || ! is_array( $record['renditions'] ?? null ) || ( $record['source_sha256'] ?? '' ) !== $hash || ( $record['source'] ?? '' ) !== ( $front['src'] ?? '' ) ) {
		return array();
	}
	// Unfiltered local attachment metadata avoids trusting an offload URL as proof.
	if ( skyyrose2_pdp_delivery_file_hash( get_attached_file( $attachment_id, true ) ) !== $hash ) {
		return array();
	}
	$width = (int) ( $front['width'] ?? 0 );
	$height = (int) ( $front['height'] ?? 0 );
	if ( $width < 1 || $height < 1 ) {
		return array();
	}
	$srcset = array();
	$result = array();
	$root = realpath( SKYYROSE2_DIR . '/assets/derived/card-fronts' );
	foreach ( $record['renditions'] as $rendition ) {
		if ( ! is_array( $rendition ) ) {
			continue;
		}
		$rw = (int) ( $rendition['width'] ?? 0 );
		$rh = (int) ( $rendition['height'] ?? 0 );
		$rhash = $rendition['sha256'] ?? '';
		if ( ! is_string( $rhash ) || ! preg_match( '/^[a-f0-9]{64}$/D', $rhash ) ) {
			continue;
		}
		$relative = 'assets/derived/card-fronts/' . $sku . '-' . $rw . 'w.webp';
		$file = SKYYROSE2_DIR . '/' . $relative;
		$local = realpath( $file );
		if ( ! in_array( $rw, array( 320, 480, 768 ), true ) || $rh !== (int) round( $height * $rw / $width ) || ( $rendition['src'] ?? '' ) !== $relative || ! $root || ! $local || 0 !== strpos( $local, $root . DIRECTORY_SEPARATOR ) || is_link( $file ) || skyyrose2_pdp_delivery_file_hash( $file ) !== ( $rendition['sha256'] ?? '' ) ) {
			continue;
		}
		$dimensions = getimagesize( $local );
		if ( ! $dimensions || $rw !== $dimensions[0] || $rh !== $dimensions[1] ) {
			continue;
		}
		$url = SKYYROSE2_URI . '/' . $relative;
		$srcset[ $rw ] = $url . ' ' . $rw . 'w';
		if ( 480 === $rw ) {
			$result = array( 'src' => $url, 'width' => $rw, 'height' => $rh );
		}
	}
	if ( ! $result || ! $srcset ) {
		return array();
	}
	ksort( $srcset );
	$result['srcset'] = implode( ', ', $srcset );
	// Object-fit:contain paints within the existing bounded gallery height. Size
	// selection follows those pixels rather than the wider empty gallery box.
	$result['sizes'] = skyyrose2_pdp_gallery_sizes( $width, $height );
	return $result;
}

/** Native variation JSON keeps original IDs, thumbnail and full/lightbox sources. */
function skyyrose2_pdp_variation_delivery( $data, $product, $variation ) {
	if ( ! is_a( $product, 'WC_Product' ) || ! is_a( $variation, 'WC_Product_Variation' ) || (int) $variation->get_parent_id() !== $product->get_id() || ( ! skyyrose2_pdp_media_context( $product ) && ! skyyrose2_pdp_gallery_request() ) ) {
		return $data;
	}
	$previous = $GLOBALS['skyyrose2_pdp_media_context'] ?? null;
	// Native get_available_variation has restored its getter overrides before
	// this filter runs, including the native AJAX get_variation path.
	$GLOBALS['skyyrose2_pdp_media_context'] = skyyrose2_pdp_media_context( $product ) ?: skyyrose2_pdp_capture_media_context( $product );
	try {
		$context = skyyrose2_pdp_media_context( $product );
		$permitted = array_map( 'intval', $context['media']['ids'] );
		if ( ! $permitted || 'rejected' === $context['media']['state'] ) {
			$data['image'] = array();
			$data['image_id'] = 0;
			$data['gallery_image_ids'] = array();
			$data['gallery_images_html'] = '';
			return $data;
		}
		$image_id = (int) ( $data['image_id'] ?? 0 );
		if ( $image_id && ! in_array( $image_id, $permitted, true ) ) {
			$data['image'] = array();
			$data['image_id'] = 0;
			$image_id = 0;
		}
		$approved_front_variation = false;
		if ( $image_id && ! empty( $data['image'] ) ) {
			$original_image = $data['image'];
			$data['image'] = skyyrose2_pdp_approved_ghost_front_variation_image( $data['image'], $image_id, $product );
			$approved_front_variation = $original_image !== $data['image'];
		}
		$candidates = array_values( array_unique( array_map( 'intval', $data['gallery_image_ids'] ?? array() ) ) );
		if ( $candidates ) {
			$data['gallery_image_ids'] = array_values( array_intersect( $candidates, $permitted ) );
			if ( $image_id && ! in_array( $image_id, $candidates, true ) ) {
				array_unshift( $candidates, $image_id );
			}
			$approved_primary = skyyrose2_pdp_approved_ghost_front_filter( $product );
			add_filter( 'woocommerce_single_product_image_thumbnail_html', $approved_primary, 30, 2 );
			try {
				$data['gallery_images_html'] = wc_get_product_gallery_html( $product, array_values( array_intersect( $candidates, $permitted ) ) );
			} finally {
				remove_filter( 'woocommerce_single_product_image_thumbnail_html', $approved_primary, 30 );
			}
		} else {
			$data['gallery_images_html'] = '';
		}
		$delivery = ! $approved_front_variation && ! empty( $data['image_id'] ) && ! empty( $data['image'] ) ? skyyrose2_pdp_media_delivery( $product, $image_id ) : array();
		if ( $delivery ) {
			foreach ( array( 'src', 'srcset', 'sizes' ) as $key ) {
				$data['image'][ $key ] = $delivery[ $key ];
			}
			$data['image']['src_w'] = $delivery['width'];
			$data['image']['src_h'] = $delivery['height'];
		}
		return $data;
	} finally {
		if ( null === $previous ) {
			unset( $GLOBALS['skyyrose2_pdp_media_context'] );
		} else {
			$GLOBALS['skyyrose2_pdp_media_context'] = $previous;
		}
	}
}
add_filter( 'woocommerce_available_variation', 'skyyrose2_pdp_variation_delivery', 40, 3 );

/** Full product detail remains available on demand through native PhotoSwipe. */
function skyyrose2_pdp_hover_zoom_enabled( $enabled ) {
	return function_exists( 'is_product' ) && is_product() ? false : $enabled;
}
add_filter( 'woocommerce_single_product_zoom_enabled', 'skyyrose2_pdp_hover_zoom_enabled' );
