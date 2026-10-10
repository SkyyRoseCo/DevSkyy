<?php
/**
 * Product archive: native Woo purchase spread.
 *
 * This keeps the canonical WooCommerce hook sequence intact so extensions,
 * product types, variation forms, stock state, and Product structured data
 * continue to use server-authoritative behavior. Gallery left (sticky at 64em),
 * buy column right, tabs and related pieces below.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

$hero_product           = isset( $args['product'] ) && is_a( $args['product'], 'WC_Product' ) ? $args['product'] : null;
$hero_presentation      = isset( $args['presentation'] ) ? sanitize_html_class( $args['presentation'] ) : 'house';
$hero_presentation_name = isset( $args['presentation_name'] ) ? (string) $args['presentation_name'] : __( 'SkyyRose', 'skyyrose-flagship-2' );
$hero_collection        = isset( $args['collection'] ) ? sanitize_title( (string) $args['collection'] ) : '';
$hero_collection_data   = isset( $args['collection_data'] ) && is_array( $args['collection_data'] ) ? $args['collection_data'] : null;

if ( ! $hero_product ) {
	return;
}

do_action( 'woocommerce_before_single_product' );

if ( post_password_required() ) {
	echo get_the_password_form(); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- Core-generated password form.
	return;
}

// Hold the clean parent permission through visible, default and variation galleries.
$previous_media_context                 = $GLOBALS['skyyrose2_pdp_media_context'] ?? null;
$GLOBALS['skyyrose2_pdp_media_context'] = skyyrose2_pdp_capture_media_context( $hero_product );
try {
	$commerce_media     = $GLOBALS['skyyrose2_pdp_media_context']['media'];
	$verified_image_ids = $commerce_media['ids'];
	$gallery_count      = count( $verified_image_ids );
	$has_verified_media = ! empty( $verified_image_ids );
	// The region's accessible name counts what it renders: verified views, or the one approved styling view.
	$styling_view       = $has_verified_media ? null : skyyrose2_approved_pdp_styling_view_front( $hero_product );
	$published_views    = $gallery_count + ( $styling_view ? 1 : 0 );
	$stock_state        = $hero_product->is_in_stock() ? 'available' : 'unavailable';
	$portal_kicker      = $hero_collection_data && ! empty( $hero_collection_data['kicker'] ) ? $hero_collection_data['kicker'] : '';
	$portal_story       = $hero_collection_data && ! empty( $hero_collection_data['card_story'] ) ? $hero_collection_data['card_story'] : '';
	$product_type       = $hero_product->get_type();
	$purchasable        = $hero_product->is_purchasable() ? 'true' : 'false';
	$related_heading    = 'house' === $hero_presentation
	? __( 'More from the house', 'skyyrose-flagship-2' )
	/* translators: %s: collection or presentation name, e.g. Black Rose. */
	: sprintf( __( 'More from %s', 'skyyrose-flagship-2' ), $hero_presentation_name );
	?>
<div
	id="product-<?php the_ID(); ?>"
	<?php wc_product_class( 'sr2-pdp-product sr2-pdp-product--editorial', $hero_product ); ?>
	data-presentation="<?php echo esc_attr( $hero_presentation ); ?>"
	<?php echo $hero_collection ? 'data-collection="' . esc_attr( $hero_collection ) . '"' : ''; ?>
	data-product-type="<?php echo esc_attr( $product_type ); ?>"
	data-purchasable="<?php echo esc_attr( $purchasable ); ?>"
	data-gallery-count="<?php echo esc_attr( (string) $gallery_count ); ?>"
	data-media-state="<?php echo esc_attr( $commerce_media['state'] ); ?>"
	data-availability="<?php echo esc_attr( $stock_state ); ?>"
>
	<div id="sr2-product-views" class="sr2-pdp-product__media" role="region" aria-label="<?php echo esc_attr( sprintf( _n( '%d published view', '%d published views', $published_views, 'skyyrose-flagship-2' ), $published_views ) ); ?>">
		<?php

		/**
		 * Hook: woocommerce_before_single_product_summary.
		 *
		 * @hooked woocommerce_show_product_sale_flash - 10
		 * @hooked woocommerce_show_product_images - 20
		 */
		$images_priority = has_action( 'woocommerce_before_single_product_summary', 'woocommerce_show_product_images' );
		if ( ! $has_verified_media && false !== $images_priority ) {
			remove_action( 'woocommerce_before_single_product_summary', 'woocommerce_show_product_images', $images_priority );
		}
		try {
			do_action( 'woocommerce_before_single_product_summary' );
		} finally {
			if ( ! $has_verified_media && false !== $images_priority ) {
				add_action( 'woocommerce_before_single_product_summary', 'woocommerce_show_product_images', $images_priority );
			}
		}

		?>
		<?php if ( ! $has_verified_media ) : ?>
			<?php if ( ! $styling_view || ! skyyrose2_render_approved_pdp_styling_front( $styling_view['sku'], $styling_view['front'], $styling_view['src'], $styling_view['width'], $styling_view['height'], $styling_view['sizes'] ) ) : ?>
<div class="sr2-pdp-product__media-missing" role="status">
				<?php esc_html_e( 'Product imagery is currently unavailable.', 'skyyrose-flagship-2' ); ?>
			</div>
<?php endif; ?>
		<?php endif; ?>
	</div>

	<div id="sr2-product-purchase" class="summary entry-summary sr2-pdp-product__summary">
		<p class="sr2-eyebrow sr2-pdp-product__collection"><?php echo esc_html( $hero_presentation_name ); ?></p>

		<?php
		/**
		 * Hook: woocommerce_single_product_summary.
		 *
		 * Preserves title, rating, price, excerpt, every product-type add-to-cart
		 * form, product meta, sharing, and WooCommerce Product structured data.
		 */
		// BEGIN SR2_NATIVE_SUMMARY: preserve extension order and render the native excerpt once after purchase.
		$excerpt_priority = has_action( 'woocommerce_single_product_summary', 'woocommerce_template_single_excerpt' );
		if ( false !== $excerpt_priority ) {
			remove_action( 'woocommerce_single_product_summary', 'woocommerce_template_single_excerpt', $excerpt_priority );
		}
		try {
			do_action( 'woocommerce_single_product_summary' );
			echo '<p class="sr2-pdp-status" role="status" aria-live="polite" data-sr2-pdp-status></p>';
			if ( false !== $excerpt_priority ) {
				woocommerce_template_single_excerpt();
			}
		} finally {
			if ( false !== $excerpt_priority ) {
				add_action( 'woocommerce_single_product_summary', 'woocommerce_template_single_excerpt', $excerpt_priority );
			}
		}
		// END SR2_NATIVE_SUMMARY
		?>
		<div class="sr2-pdp-support">
			<nav class="sr2-pdp-support__links" aria-label="<?php esc_attr_e( 'Product support', 'skyyrose-flagship-2' ); ?>">
				<a class="sr2-editorial-link" href="<?php echo esc_url( skyyrose2_marketplace_page_url( 'size-guide' ) ); ?>" data-size-guide-open aria-haspopup="dialog" aria-controls="sr2-size-guide-dialog"><?php esc_html_e( 'Fit + size guide', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">→</span></a>
				<a class="sr2-editorial-link" href="<?php echo esc_url( skyyrose2_marketplace_page_url( 'shipping-returns' ) ); ?>"><?php esc_html_e( 'Shipping + Returns', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">→</span></a>
			</nav>
			<?php if ( skyyrose2_is_preorder_product( $hero_product ) ) : ?>
				<div class="sr2-pdp-order-note" role="note"><strong><?php esc_html_e( 'Pre-order edition', 'skyyrose-flagship-2' ); ?></strong><p><?php esc_html_e( 'Orders use standard checkout. This label does not reserve stock or defer payment. Contact Client Services for shipping estimates before ordering.', 'skyyrose-flagship-2' ); ?></p></div>
			<?php endif; ?>
			<?php if ( $portal_story ) : ?>
				<aside class="sr2-pdp-product__house-note" data-sr2-type-motion="editorial"><span><?php echo esc_html( $portal_kicker ?: __( 'House note', 'skyyrose-flagship-2' ) ); ?></span><p><?php echo esc_html( $portal_story ); ?></p></aside>
			<?php endif; ?>
		</div>
	</div>

	<div id="sr2-product-details" class="sr2-pdp-product__after-summary">
		<?php
		/**
		 * Hook: woocommerce_after_single_product_summary.
		 *
		 * Preserves tabs, upsells, and related products. Only the related
		 * heading is renamed for this render; the native loop is untouched.
		 */
		$related_heading_filter = static function () use ( $related_heading ) {
			return $related_heading;
		};
		add_filter( 'woocommerce_product_related_products_heading', $related_heading_filter, 20 );
	try {
		do_action( 'woocommerce_after_single_product_summary' );
	} finally {
		remove_filter( 'woocommerce_product_related_products_heading', $related_heading_filter, 20 );
	}
	?>
	</div>
</div>
	<?php
	do_action( 'woocommerce_after_single_product' );
} finally {
	if ( null === $previous_media_context ) {
		unset( $GLOBALS['skyyrose2_pdp_media_context'] );
	} else {
		$GLOBALS['skyyrose2_pdp_media_context'] = $previous_media_context;
	}
}
?>
