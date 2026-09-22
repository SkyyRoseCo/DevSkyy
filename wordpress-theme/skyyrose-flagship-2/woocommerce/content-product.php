<?php
/**
 * House of Roses WooCommerce loop card.
 *
 * Product, price, availability, media, and purchase behavior remain owned by
 * WooCommerce. The theme contributes only the collection portal composition.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

global $product;

if ( ! is_a( $product, 'WC_Product' ) || ! $product->is_visible() ) {
	return;
}

// Only the first archive card is an explicit eager candidate. Native lazy
// loading lets the browser schedule other visible and nearby grid cards.
// wc_product_class() advances the native loop counter below; read it first.
$loop_index = max( 0, (int) wc_get_loop_prop( 'loop' ) );
$card_sizes = ( is_shop() || is_product_taxonomy() ) && ! wc_get_loop_prop( 'name' ) ? skyyrose2_shop_card_sizes() : '';
if ( is_product() && in_array( wc_get_loop_prop( 'name' ), array( 'related', 'up-sells' ), true ) ) {
	$card_sizes = '(max-width: 47.99em) calc((100vw - 2 * clamp(16px, 4vw, 64px) - 16px) / 2), (max-width: 79.99em) calc((100vw - 2 * clamp(16px, 4vw, 64px) - 32px) / 3), (max-width: 93.75em) calc((100vw - 128px - 48px) / 4), 331px';
}
?>
<li <?php wc_product_class( 'sr2-c-product-card-wrap sr2-c-product-card-wrap--portal', $product ); ?>>
	<?php
	get_template_part(
		'template-parts/commerce/product-card',
		null,
		array(
			'product' => $product,
			'index'   => $loop_index,
			'sizes'   => $card_sizes,
			'media_priority' => ( is_shop() || is_product_taxonomy() ) && ! wc_get_loop_prop( 'name' ) && 0 === $loop_index ? 'high' : 'lazy',
		)
	);
	?>
</li>
