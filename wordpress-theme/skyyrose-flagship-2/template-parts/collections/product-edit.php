<?php
/** A bounded editorial grid using the single native commerce card. @package SkyyRoseFlagship2 */
defined( 'ABSPATH' ) || exit;
$edit_products = $args['products'] ?? array();
$edit_offset   = max( 0, (int) ( $args['offset'] ?? 0 ) );
$edit_is_pair  = 2 === count( $edit_products );
$edit_is_single = 1 === count( $edit_products );
// Below 360px the full portrait paints at 187px within its 280px-high frame;
// otherwise two tracks up to 1024px, then four within a 1500px shell.
$edit_sizes = '(max-width: 22.49em) 187px, (max-width: 63.99em) calc((100vw - 3rem) / 2), (max-width: 95.75em) calc((100vw - 5rem) / 4), 363px';
if ( $edit_is_pair ) {
	// Two portraits share a centered 760px edit with one 16px gutter.
	$edit_sizes = '(max-width: 22.49em) 187px, (max-width: 49.5em) calc((100vw - 3rem) / 2), 372px';
}
if ( $edit_is_single ) {
	$edit_sizes = '(max-width: 22.49em) 187px, (max-width: 28.25em) calc(100vw - 2rem), 420px';
}
?>
<div class="sr2-world-products<?php echo $edit_is_pair ? ' sr2-world-products--pair' : ''; ?><?php echo $edit_is_single ? ' sr2-world-products--single' : ''; ?>">
	<?php foreach ( $edit_products as $edit_index => $edit_product ) : ?>
		<?php get_template_part( 'template-parts/commerce/product-card', null, array(
			'product'        => $edit_product,
			'index'          => $edit_offset + $edit_index,
			'heading_level'  => 3,
			'variant'        => 'standard',
			'media_priority' => 'lazy',
			'sizes'          => $edit_sizes,
		) ); ?>
	<?php endforeach; ?>
</div>
