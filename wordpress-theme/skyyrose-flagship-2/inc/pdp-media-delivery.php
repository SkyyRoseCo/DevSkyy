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
		'product_id'   => $product->get_id(),
		'product'      => $product,
		'media'        => skyyrose2_product_commerce_media( $product ),
		'original_ids' => array_values( array_unique( array_filter( array_map( 'intval', array_merge( array( $product->get_image_id() ), $product->get_gallery_image_ids() ) ) ) ) ),
	);
}

/** Display-only attributes shared by every native gallery representation. */
function skyyrose2_pdp_gallery_attributes( $attributes, $attachment_id, $main_image, $product ) {
	$context = skyyrose2_pdp_media_context( $product );
	if ( ! $context || ! in_array( (int) $attachment_id, array_map( 'intval', $context['media']['ids'] ), true ) ) {
		return $attributes;
	}
	$attributes['loading']       = $main_image ? 'eager' : 'lazy';
	$attributes['fetchpriority'] = $main_image ? 'high' : 'auto';
	$attributes['decoding']      = 'async';
	$delivery                    = skyyrose2_pdp_media_delivery( $product, (int) $attachment_id );
	if ( $delivery ) {
		foreach ( array( 'src', 'srcset', 'sizes' ) as $key ) {
			$attributes[ $key ] = $delivery[ $key ];
		}
	}
	return $attributes;
}

/** Source-size hint for the PDP's contain-fit gallery at its real height. */
function skyyrose2_pdp_gallery_sizes( $width, $height ) {
	$width  = (int) $width;
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

/** Compatibility caller: only the current exact PDP lead can replace a primary. */
function skyyrose2_pdp_approved_ghost_front( $attachment_id, $product ) {
	if ( ! is_a( $product, 'WC_Product' ) || ! $attachment_id || (int) $attachment_id !== (int) $product->get_image_id() ) { return array(); }
	$front = skyyrose2_approved_pdp_front( $product );
	if ( ! $front || wp_get_attachment_url( $attachment_id ) !== $front['src'] ) { return array(); }
	$front['pdp_src'] = $front['card_src'] ?? $front['src'];
	$front['pdp_width'] = $front['card_width'] ?? $front['width'];
	$front['pdp_height'] = $front['card_height'] ?? $front['height'];
	$front['pdp_sizes'] = skyyrose2_pdp_gallery_sizes( $front['width'], $front['height'] );
	return $front;
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
	$src         = $front['pdp_src'];
	$width       = $front['pdp_width'];
	$height      = $front['pdp_height'];
	$full_width  = (int) $front['width'];
	$full_height = (int) $front['height'];
	$alt         = esc_attr( $front['alt'] );
	$full        = esc_url( $front['src'] );
	$responsive  = ! empty( $front['srcset'] ) ? ' srcset="' . esc_attr( $front['srcset'] ) . '" sizes="' . esc_attr( $front['pdp_sizes'] ) . '"' : '';
	return '<div data-thumb="' . esc_url( $src ) . '" data-thumb-alt="' . $alt . '" class="woocommerce-product-gallery__image"><a href="' . $full . '"><img width="' . $width . '" height="' . $height . '" src="' . esc_url( $src ) . '" class="wp-post-image" alt="' . $alt . '"' . $responsive . ' data-src="' . $full . '" data-large_image="' . $full . '" data-large_image_width="' . $full_width . '" data-large_image_height="' . $full_height . '" loading="eager" fetchpriority="high" decoding="async"></a></div>';
}

/** Build the first native PDP frame from the same exact front as product cards. */
function skyyrose2_pdp_card_front_markup( $front ) {
	if ( ! is_array( $front ) || empty( $front['src'] ) ) {
		return '';
	}
	$front['pdp_src']    = $front['display_src'] ?? $front['card_src'] ?? $front['src'];
	$front['pdp_width']  = (int) ( $front['display_width'] ?? $front['card_width'] ?? $front['width'] );
	$front['pdp_height'] = (int) ( $front['display_height'] ?? $front['card_height'] ?? $front['height'] );
	$front['pdp_sizes']  = skyyrose2_pdp_gallery_sizes( $front['width'], $front['height'] );
	return skyyrose2_pdp_approved_ghost_front_markup( $front );
}

/** Native Woo variation replacement requires a complete gallery, including gaps. */
function skyyrose2_pdp_v2_gallery_markup( $front ) {
	$frame = skyyrose2_pdp_card_front_markup( $front );
	$state = $frame ? 'with-images' : 'without-images';
	$content = $frame ?: '<div class="sr2-pdp-product__media-missing" role="status">' . esc_html__( 'Product imagery is currently unavailable.', 'skyyrose-flagship-2' ) . '</div>';
	return '<div class="woocommerce-product-gallery woocommerce-product-gallery--' . $state . ' images" data-columns="1"><figure class="woocommerce-product-gallery__wrapper">' . $content . '</figure></div>';
}

/** Replace only the first native gallery frame; keep native hooks and later views. */
function skyyrose2_pdp_card_front_filter( $front ) {
	$rendered = false;
	return static function ( $html ) use ( $front, &$rendered ) {
		if ( $rendered || ! $front ) {
			return $html;
		}
		$replacement = skyyrose2_pdp_card_front_markup( $front );
		if ( $replacement ) {
			$rendered = true;
			return $replacement;
		}
		return $html;
	};
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
	$image['src']   = $front['pdp_src'];
	$image['src_w'] = $front['pdp_width'];
	$image['src_h'] = $front['pdp_height'];
	if ( ! empty( $front['srcset'] ) ) {
		$image['srcset'] = $front['srcset'];
		$image['sizes']  = $front['pdp_sizes'];
	} else {
		$image['srcset'] = '';
		$image['sizes']  = '';
	}
	$image['full_src']                = $front['src'];
	$image['full_src_w']              = (int) $front['width'];
	$image['full_src_h']              = (int) $front['height'];
	$image['gallery_thumbnail_src']   = $front['pdp_src'];
	$image['gallery_thumbnail_src_w'] = $front['pdp_width'];
	$image['gallery_thumbnail_src_h'] = $front['pdp_height'];
	$image['thumb_src']               = $front['pdp_src'];
	$image['thumb_src_w']             = $front['pdp_width'];
	$image['thumb_src_h']             = $front['pdp_height'];
	$image['alt']                     = $front['alt'];
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

/** Same current role-bound PDP lead, retaining native attachment and full-view fields. */
function skyyrose2_pdp_media_delivery( $product, $attachment_id ) {
	if ( ! is_a( $product, 'WC_Product' ) || ! $attachment_id ) { return array(); }
	$context = skyyrose2_pdp_media_context( $product );
	$media = $context ? $context['media'] : skyyrose2_product_commerce_media( $product );
	if ( ! in_array( (int) $attachment_id, array_map( 'intval', $media['ids'] ?? array() ), true ) ) { return array(); }
	$front = skyyrose2_approved_pdp_front( $product );
	if ( ! $front || wp_get_attachment_url( $attachment_id ) !== $front['src'] || skyyrose2_pdp_delivery_file_hash( get_attached_file( $attachment_id, true ) ) !== $front['sha256'] ) { return array(); }
	return array(
		'src' => $front['card_src'] ?? $front['src'],
		'width' => $front['card_width'] ?? $front['width'],
		'height' => $front['card_height'] ?? $front['height'],
		'srcset' => $front['srcset'] ?? '',
		'sizes' => skyyrose2_pdp_gallery_sizes( $front['width'], $front['height'] ),
	);
}

/** Native variation purchase fields stay intact; imagery follows the selected SKU. */
function skyyrose2_pdp_variation_delivery( $data, $product, $variation ) {
	if ( ! is_a( $product, 'WC_Product' ) || ! is_a( $variation, 'WC_Product_Variation' ) || (int) $variation->get_parent_id() !== $product->get_id() || ( ! skyyrose2_pdp_media_context( $product ) && ! skyyrose2_pdp_gallery_request() ) ) {
		return $data;
	}
	// A complete gallery is necessary: empty native image payloads reset to
	// the parent's default image, which may represent a different variation.
	$front = skyyrose2_approved_pdp_front( $variation );
	$data['image_id'] = 0;
	$data['gallery_image_ids'] = array();
	$data['gallery_images_html'] = skyyrose2_pdp_v2_gallery_markup( $front );
	if ( ! $front ) { $data['image'] = array(); return $data; }
	$front['pdp_src'] = $front['display_src'] ?? $front['card_src'] ?? $front['src'];
	$front['pdp_width'] = $front['display_width'] ?? $front['card_width'] ?? $front['width'];
	$front['pdp_height'] = $front['display_height'] ?? $front['card_height'] ?? $front['height'];
	$front['pdp_sizes'] = skyyrose2_pdp_gallery_sizes( $front['width'], $front['height'] );
	$data['image'] = skyyrose2_pdp_variation_image_from_approved_front( array(), $front );
	return $data;
}
add_filter( 'woocommerce_available_variation', 'skyyrose2_pdp_variation_delivery', 40, 3 );

/** Full product detail remains available on demand through native PhotoSwipe. */
function skyyrose2_pdp_hover_zoom_enabled( $enabled ) {
	return function_exists( 'is_product' ) && is_product() ? false : $enabled;
}
add_filter( 'woocommerce_single_product_zoom_enabled', 'skyyrose2_pdp_hover_zoom_enabled' );
