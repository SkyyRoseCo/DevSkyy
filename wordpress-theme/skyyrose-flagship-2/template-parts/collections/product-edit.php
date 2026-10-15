<?php
/**
 * Garment-led edit grid using the single native commerce card, unframed.
 *
 * @package SkyyRoseFlagship2
 */
defined( 'ABSPATH' ) || exit;
$edit_products = $args['products'] ?? array();
$edit_offset   = max( 0, (int) ( $args['offset'] ?? 0 ) );
// One column to 767px, two to 1023px, three to 1439px, then four inside the page padding.
$edit_sizes = '(max-width: 47.99em) calc(100vw - 2rem), (max-width: 63.99em) calc((100vw - 4rem) / 2), (max-width: 89.99em) calc((100vw - 10rem) / 3), 300px';
?>
<div class="sr2-world-products" data-count="<?php echo esc_attr( (string) count( $edit_products ) ); ?>">
	<?php foreach ( $edit_products as $edit_index => $edit_product ) : ?>
		<?php get_template_part( 'template-parts/commerce/product-card', null, array(
			'product'        => $edit_product,
			'index'          => $edit_offset + $edit_index,
			'heading_level'  => 3,
			'variant'        => 'standard',
			'media_priority' => 'lazy',
			'frame'          => false,
			'sizes'          => $edit_sizes,
		) ); ?>
	<?php endforeach; ?>
</div>
