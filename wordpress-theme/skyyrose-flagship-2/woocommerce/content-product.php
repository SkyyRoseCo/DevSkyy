<?php
/**
 * Native WooCommerce loop card: the garment alone on its tile.
 *
 * Product, price, availability, media, and purchase behavior remain owned by
 * WooCommerce. Grids pass frame => false; the paid portal frame stays available
 * to the archive test and founder-directed uses through the same partial.
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
	// Related grid: one track under 48em, then 2/3/4 tracks inside the 1500px product shell.
	$card_sizes = '(max-width: 47.99em) calc(100vw - 2 * clamp(1rem, 4vw, 4rem)), (max-width: 63.99em) calc((100vw - 2 * clamp(1rem, 4vw, 4rem) - clamp(1rem, 2vw, 2rem)) / 2), (max-width: 89.99em) calc((100vw - 2 * clamp(1rem, 4vw, 4rem) - 2 * clamp(1rem, 2vw, 2rem)) / 3), (max-width: 93.75em) calc((100vw - 8rem - 3 * clamp(1rem, 2vw, 2rem)) / 4), 319px';
}
?>
<li <?php wc_product_class( 'sr2-c-product-card-wrap sr2-c-product-card-wrap--archive', $product ); ?>>
	<?php
	get_template_part(
		'template-parts/commerce/product-card',
		null,
		array(
			'product'        => $product,
			'index'          => $loop_index,
			'sizes'          => $card_sizes,
			'frame'          => false,
			'media_priority' => ( is_shop() || is_product_taxonomy() ) && ! wc_get_loop_prop( 'name' ) && 0 === $loop_index ? 'high' : 'lazy',
		)
	);
	?>
</li>
