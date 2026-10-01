<?php
/**
 * Permission boundary around the installed native gallery template.
 * Native Woo owns markup, lightbox, thumbnails and extension hooks.
 *
 * @package SkyyRoseFlagship2
 * @version 11.1.0
 */
defined( 'ABSPATH' ) || exit;
global $product;
$native_template = WC()->plugin_path() . '/templates/single-product/product-image.php';
$context         = skyyrose2_pdp_media_context( $product );
$front           = function_exists( 'skyyrose2_approved_card_front' ) ? skyyrose2_approved_card_front( $product ) : array();
$front_filter    = skyyrose2_pdp_card_front_filter( $front );
if ( ! $context ) {
	// Native variation AJAX generates an intermediate gallery before its data
	// filter. That filter re-renders under clean parent permission afterward.
	if ( skyyrose2_pdp_gallery_request() ) {
		return;
	}
	add_filter( 'woocommerce_single_product_image_thumbnail_html', $front_filter, 30, 2 );
	try {
		require $native_template;
	} finally {
		remove_filter( 'woocommerce_single_product_image_thumbnail_html', $front_filter, 30 );
	}
	return;
}
$permitted = array_map( 'intval', $context['media']['ids'] );
if ( ! $permitted || 'rejected' === $context['media']['state'] ) {
	// A hash-bound storefront front can still give this PDP its exact product
	// image when older Woo attachments are explicitly rejected.
	if ( $front ) {
		echo '<div class="woocommerce-product-gallery woocommerce-product-gallery--with-images" data-columns="1"><figure class="woocommerce-product-gallery__wrapper">';
		echo skyyrose2_pdp_card_front_markup( $front ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- helper escapes every attribute.
		echo '</figure></div>';
	}
	return;
}
$candidates = array_values( array_unique( array_filter( array_map( 'intval', array_merge( array( $product->get_image_id() ), $product->get_gallery_image_ids() ) ) ) ) );
// Default/reset snapshots retain the existing resolver's editorial order.
// Native caller-supplied variation galleries retain their own permitted order.
$candidates = $candidates === $context['original_ids'] ? $permitted : array_values( array_intersect( $candidates, $permitted ) );
if ( ! $candidates ) {
	return;
}
$owner_id   = $product->get_id();
$primary    = static function ( $value, $instance ) use ( $owner_id, $candidates ) {
	return $instance && $instance->get_id() === $owner_id ? $candidates[0] : $value;
};
$gallery    = static function ( $value, $instance ) use ( $owner_id, $candidates ) {
	return $instance && $instance->get_id() === $owner_id ? array_slice( $candidates, 1 ) : $value;
};
$attributes = static function ( $attr, $id, $size, $main ) use ( $product ) {
	return skyyrose2_pdp_gallery_attributes( $attr, $id, $main, $product );
};
// Woo 11.1 merges positioned video metadata outside the image getters. The
// current PDP resolver grants only image IDs; never promote this separate list.
$video_metadata         = static function ( $value, $object_id, $key, $single ) use ( $owner_id ) {
	return (int) $object_id === $owner_id && '_wc_video_gallery' === $key ? ( $single ? array( array() ) : array() ) : $value;
};
$video_product_metadata = static function ( $value, $instance ) use ( $owner_id ) {
	return $instance && $instance->get_id() === $owner_id ? array() : $value;
};
$approved_primary       = $front ? $front_filter : skyyrose2_pdp_approved_ghost_front_filter( $product );
add_filter( 'woocommerce_product_get_image_id', $primary, 20, 2 );
add_filter( 'woocommerce_product_get_gallery_image_ids', $gallery, 20, 2 );
add_filter( 'woocommerce_gallery_image_html_attachment_image_params', $attributes, 20, 4 );
add_filter( 'woocommerce_single_product_image_thumbnail_html', $approved_primary, 30, 2 );
add_filter( 'get_post_metadata', $video_metadata, 20, 4 );
add_filter( 'woocommerce_product_get__wc_video_gallery', $video_product_metadata, 20, 2 );
try {
	require $native_template;
} finally {
	remove_filter( 'woocommerce_product_get__wc_video_gallery', $video_product_metadata, 20 );
	remove_filter( 'get_post_metadata', $video_metadata, 20 );
	remove_filter( 'woocommerce_single_product_image_thumbnail_html', $approved_primary, 30 );
	remove_filter( 'woocommerce_gallery_image_html_attachment_image_params', $attributes, 20 );
	remove_filter( 'woocommerce_product_get_gallery_image_ids', $gallery, 20 );
	remove_filter( 'woocommerce_product_get_image_id', $primary, 20 );
}
