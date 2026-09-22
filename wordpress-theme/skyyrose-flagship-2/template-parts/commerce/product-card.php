<?php
/**
 * Canonical Living Archive commerce card.
 *
 * Arguments: product (WC_Product), index (zero-based editorial order), variant
 * (standard|feature|compact), heading_level (2|3|4), media_priority (lazy|eager|high),
 * sizes (optional responsive image slot contract owned by the rendering module).
 * Eager priority requires explicit intent in the first two native archive cards.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

global $product;

$card_product = isset( $args['product'] ) && is_a( $args['product'], 'WC_Product' ) ? $args['product'] : $product;
$card_index   = isset( $args['index'] ) ? max( 0, (int) $args['index'] ) : 0;
if ( ! $card_product || ! $card_product->is_visible() ) {
	return;
}

// Native Woo actions read this global. Editorial modules must not leak another
// product into those actions, even if an extension throws while rendering.
$previous_global_product = $product;
$product                 = $card_product;
try {
	$product_id      = $card_product->get_id();
	$product_url     = $card_product->get_permalink();
	$product_name    = $card_product->get_name();
	$product_sku     = $card_product->get_sku();
	$collections     = skyyrose2_collections();
	$record          = skyyrose2_product_presentation( $card_product );
	$collection      = isset( $record['collection'] ) ? sanitize_title( $record['collection'] ) : '';
	$presentation    = 'jersey-series' === ( $record['presentation'] ?? '' ) ? 'jersey-series' : $collection;
	$collection_name = 'jersey-series' === $presentation
		? __( 'Jersey Series', 'skyyrose-flagship-2' )
		: ( $collections[ $collection ]['name'] ?? __( 'SkyyRose', 'skyyrose-flagship-2' ) );
	$frame           = $collections[ $collection ]['portal_statue'] ?? array();
	$frame_uri       = ! empty( $frame['small'] ) ? skyyrose2_sot_asset_uri( $frame['small'] ) : '';
	$variant         = in_array( $args['variant'] ?? '', array( 'standard', 'feature', 'compact' ), true ) ? $args['variant'] : 'standard';
	$is_archive      = ( function_exists( 'is_shop' ) && is_shop() ) || ( function_exists( 'is_product_taxonomy' ) && is_product_taxonomy() );
	$heading_level   = isset( $args['heading_level'] ) && in_array( (int) $args['heading_level'], array( 2, 3, 4 ), true )
		? (int) $args['heading_level'] : ( $is_archive ? 2 : 3 );
	$heading_tag     = 'h' . $heading_level;
	$priority_intent = $args['media_priority'] ?? 'lazy';
	$native_archive  = $is_archive && function_exists( 'is_main_query' ) && is_main_query()
		&& function_exists( 'wc_get_loop_prop' ) && ! wc_get_loop_prop( 'name' );
	// Match the owning archive grid: one card per row through 479px, then
	// two/three/four columns. The outer 4vw gutters are clamped and the inner
	// shell/gaps contribute 3/4/5rem at their respective column counts.
	$default_sizes = $native_archive
		? '(max-width: 29.99em) calc(100vw - 4rem), (max-width: 47.99em) calc((100vw - clamp(2rem, 8vw, 9rem) - 3rem) / 2), (max-width: 74.99em) calc((100vw - clamp(2rem, 8vw, 9rem) - 4rem) / 3), (max-width: 95.75em) calc((100vw - clamp(2rem, 8vw, 9rem) - 5rem) / 4), 360px'
		: '(max-width: 47.99em) calc(100vw - 2rem), (max-width: 74.99em) calc((100vw - 5rem) / 2), 480px';
	$image_sizes   = isset( $args['sizes'] ) && is_string( $args['sizes'] ) && '' !== trim( $args['sizes'] ) ? $args['sizes'] : $default_sizes;
	$frame_delivery = $native_archive && $frame_uri && function_exists( 'skyyrose2_archive_frame_delivery' ) ? skyyrose2_archive_frame_delivery( $collection ) : array();
	$is_eager       = $native_archive && $card_index < 2 && in_array( $priority_intent, array( 'eager', 'high' ), true );
	$loading        = $is_eager ? 'eager' : 'lazy';
	$fetchpriority  = $is_eager && 0 === $card_index && 'high' === $priority_intent ? 'high' : 'auto';

	// Approved card-front authority is independent of opening-editorial approval.
	// When that front is absent, only the Phase 2 resolver may authorize a Woo
	// attachment. A raw Woo assignment cannot bypass an explicit rejection.
	$front              = skyyrose2_approved_card_front( $card_product );
	$commerce_media     = $front ? array() : skyyrose2_product_commerce_media( $card_product );
	$image_id           = $front ? 0 : (int) ( $commerce_media['ids'][0] ?? 0 );
	$media_source       = $front ? 'approved-card-front' : ( $commerce_media['state'] ?? 'missing' );
	$media_state        = $front || $image_id ? 'ready' : ( 'rejected' === $media_source ? 'rejected' : 'missing' );
	$quick_view_image   = $front ? $front['src'] : ( $image_id ? wp_get_attachment_image_url( $image_id, 'woocommerce_single' ) : '' );
	$price_html         = $card_product->get_price_html();
	$stock_html         = function_exists( 'wc_get_stock_html' ) ? wc_get_stock_html( $card_product ) : '';
	$stock_state        = $card_product->is_in_stock() ? 'available' : 'unavailable';
	$native_stock_label = trim( wp_strip_all_tags( $stock_html ) );
	$stock_label        = '' !== $native_stock_label ? $native_stock_label : ( $card_product->is_in_stock() ? __( 'Available', 'skyyrose-flagship-2' ) : __( 'Unavailable', 'skyyrose-flagship-2' ) );
	$quick_view_excerpt = wp_trim_words( wp_strip_all_tags( $card_product->get_short_description() ), 26, '…' );
	$image_attrs        = array(
		'class'         => 'sr2-c-editorial-card__product-image',
		'loading'       => $loading,
		'fetchpriority' => $fetchpriority,
		'decoding'      => 'async',
		'sizes'         => $image_sizes,
	);
	?>
<article class="sr2-c-editorial-card" data-card-direction="living-archive" data-preorder="<?php echo function_exists( 'skyyrose2_is_preorder_product' ) && skyyrose2_is_preorder_product( $card_product ) ? 'true' : 'false'; ?>" data-sale="<?php echo method_exists( $card_product, 'is_on_sale' ) && $card_product->is_on_sale() ? 'true' : 'false'; ?>" data-card-variant="<?php echo esc_attr( $variant ); ?>" data-card-crop="full" data-card-frame="<?php echo $frame_uri ? 'v2-statue' : 'archive'; ?>" data-presentation="<?php echo esc_attr( $presentation ?: 'house' ); ?>" data-collection="<?php echo esc_attr( $collection ?: 'house' ); ?>" data-product-type="<?php echo esc_attr( $card_product->get_type() ); ?>" data-purchasable="<?php echo $card_product->is_purchasable() ? 'true' : 'false'; ?>" data-availability="<?php echo esc_attr( $stock_state ); ?>" data-media-state="<?php echo esc_attr( $media_state ); ?>" data-media-source="<?php echo esc_attr( $media_source ); ?>">
	<a class="sr2-c-editorial-card__media" href="<?php echo esc_url( $product_url ); ?>" aria-label="<?php echo esc_attr( sprintf( __( 'View %s', 'skyyrose-flagship-2' ), $product_name ) ); ?>">
		<span class="sr2-c-editorial-card__photo-window">
		<?php if ( $front ) : ?>
			<img class="sr2-c-editorial-card__product-image" src="<?php echo esc_url( $front['card_src'] ?? $front['src'] ); ?>"
			<?php
			if ( ! empty( $front['srcset'] ) ) :
				?>
				srcset="<?php echo esc_attr( $front['srcset'] ); ?>" sizes="<?php echo esc_attr( $image_sizes ); ?>"<?php endif; ?> alt="<?php echo esc_attr( $front['alt'] ); ?>" width="<?php echo esc_attr( (string) ( $front['card_width'] ?? $front['width'] ) ); ?>" height="<?php echo esc_attr( (string) ( $front['card_height'] ?? $front['height'] ) ); ?>" loading="<?php echo esc_attr( $loading ); ?>" fetchpriority="<?php echo esc_attr( $fetchpriority ); ?>" decoding="async">
		<?php elseif ( $image_id ) : ?>
			<?php echo wp_kses_post( wp_get_attachment_image( $image_id, 'woocommerce_thumbnail', false, $image_attrs ) ); ?>
		<?php else : ?>
			<span class="sr2-c-editorial-card__media-unavailable"><?php esc_html_e( 'Product image unavailable', 'skyyrose-flagship-2' ); ?></span>
		<?php endif; ?>
		<?php if ( $front || $image_id ) : ?>
			<span class="sr2-c-editorial-card__media-unavailable" data-card-image-error hidden><?php esc_html_e( 'Product image unavailable', 'skyyrose-flagship-2' ); ?></span>
		<?php endif; ?>
		</span>
		<?php if ( $frame_uri ) : ?>
			<img class="sr2-c-editorial-card__frame" src="<?php echo esc_url( $frame_uri ); ?>"
			<?php
			if ( $frame_delivery ) :
				?>
				srcset="<?php echo esc_attr( $frame_delivery['srcset'] ); ?>" sizes="<?php echo esc_attr( $frame_delivery['sizes'] ); ?>"<?php endif; ?> alt="" aria-hidden="true" width="<?php echo absint( $frame['width'] ); ?>" height="<?php echo absint( $frame['height'] ); ?>" loading="<?php echo esc_attr( $loading ); ?>" fetchpriority="<?php echo esc_attr( $fetchpriority ); ?>" decoding="async">
			<span class="sr2-c-editorial-card__frame-label" aria-hidden="true"><span class="sr2-c-editorial-card__inscription"><?php echo esc_html( $collection_name ); ?></span></span>
		<?php endif; ?>
	</a>
	<div class="sr2-c-editorial-card__body">
		<div class="sr2-c-editorial-card__nameplate">
			<span class="sr2-c-editorial-card__index" aria-hidden="true"><?php echo esc_html( sprintf( '%02d', $card_index + 1 ) ); ?></span>
			<p class="sr2-c-editorial-card__collection"><?php echo esc_html( $collection_name ); ?></p>
		</div>
		<?php if ( $product_sku ) : ?>
			<p class="sr2-c-editorial-card__reference"><span class="screen-reader-text"><?php esc_html_e( 'SKU:', 'skyyrose-flagship-2' ); ?></span><?php echo esc_html( strtoupper( $product_sku ) ); ?></p>
		<?php endif; ?>
		<<?php echo tag_escape( $heading_tag ); ?> class="woocommerce-loop-product__title sr2-c-editorial-card__title"><a href="<?php echo esc_url( $product_url ); ?>"><?php echo esc_html( $product_name ); ?></a></<?php echo tag_escape( $heading_tag ); ?>>
		<div class="sr2-c-editorial-card__commerce">
			<?php if ( $price_html ) : ?>
				<p class="price sr2-c-editorial-card__price"><span class="screen-reader-text"><?php esc_html_e( 'Price:', 'skyyrose-flagship-2' ); ?></span><?php echo wp_kses_post( $price_html ); ?></p>
			<?php endif; ?>
			<div class="sr2-c-editorial-card__availability" data-state="<?php echo esc_attr( $stock_state ); ?>">
				<?php
				if ( $stock_html ) :
					?>
					<?php echo wp_kses_post( $stock_html ); ?>
					<?php
else :
	?>
					<span><?php echo esc_html( $stock_label ); ?></span><?php endif; ?>
			</div>
		</div>
		<?php if ( function_exists( 'skyyrose2_is_preorder_product' ) && skyyrose2_is_preorder_product( $card_product ) ) : ?>
			<p class="sr2-c-editorial-card__edition"><?php esc_html_e( 'Pre-order edition', 'skyyrose-flagship-2' ); ?></p>
		<?php endif; ?>
		<div class="sr2-c-editorial-card__actions">
			<?php
			if ( function_exists( 'woocommerce_template_loop_add_to_cart' ) ) :
				?>
				<?php woocommerce_template_loop_add_to_cart(); ?><?php endif; ?>
			<a class="sr2-c-editorial-card__quick-view" href="<?php echo esc_url( $product_url ); ?>" data-quick-view aria-haspopup="dialog" aria-controls="sr2-quick-view-dialog" aria-expanded="false" data-quick-view-name="<?php echo esc_attr( $product_name ); ?>" data-quick-view-collection="<?php echo esc_attr( $collection_name ); ?>" data-quick-view-price="<?php echo esc_attr( wp_strip_all_tags( $price_html ) ); ?>" data-quick-view-availability="<?php echo esc_attr( $stock_label ); ?>" data-quick-view-excerpt="<?php echo esc_attr( $quick_view_excerpt ); ?>" data-quick-view-image="<?php echo esc_url( $quick_view_image ); ?>" data-quick-view-url="<?php echo esc_url( $product_url ); ?>" aria-label="<?php echo esc_attr( sprintf( __( 'Quick view %s', 'skyyrose-flagship-2' ), $product_name ) ); ?>"><?php esc_html_e( 'Quick view', 'skyyrose-flagship-2' ); ?></a>
		</div>
		<p class="sr2-c-editorial-card__feedback" data-card-cart-feedback role="status" aria-live="polite" hidden data-added="<?php echo esc_attr( __( 'Added to your bag.', 'skyyrose-flagship-2' ) ); ?>" data-failed="<?php echo esc_attr( __( 'This piece could not be added. Open the product to try again.', 'skyyrose-flagship-2' ) ); ?>"></p>
	</div>
</article>
	<?php
} finally {
	$product = $previous_global_product;
}
