<?php
/** Four-piece commerce edit. Cards retain native Woo prices, stock, quick view, and add-to-bag behavior. */
defined( 'ABSPATH' ) || exit;

$products = is_array( $args['products'] ?? null ) ? array_values( $args['products'] ) : array();
?>
<section class="sr2-editorial-products" aria-label="<?php esc_attr_e( 'Featured SkyyRose pieces', 'skyyrose-flagship-2' ); ?>">
	<?php if ( $products ) : ?><div class="sr2-editorial-products__grid"><?php foreach ( $products as $index => $product ) : ?><?php get_template_part( 'template-parts/commerce/product-card', null, array( 'product' => $product, 'index' => $index, 'heading_level' => 3, 'variant' => 'compact', 'media_priority' => 'lazy', 'sizes' => '(max-width: 22.49em) calc(100vw - 2rem), (max-width: 47.99em) calc((100vw - 3rem) / 2), (max-width: 74.99em) calc((100vw - 5rem) / 2), calc((100vw - 10rem) / 4)' ) ); ?><?php endforeach; ?></div><?php else : ?><p class="sr2-archive-empty"><?php esc_html_e( 'Explore the shop for current pieces.', 'skyyrose-flagship-2' ); ?></p><?php endif; ?>
</section>
