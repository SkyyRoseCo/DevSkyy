<?php
/** Front Page — SkyyRose editorial house. @package SkyyRoseFlagship2 */
defined( 'ABSPATH' ) || exit;

$archive_collections = skyyrose2_collections();
$archive_hero_motion = skyyrose2_collection_hero_motion( 'black-rose', $archive_collections['black-rose']['hero'] );
$archive_shop        = skyyrose2_shop_url();
$archive_product_map = array(
	'signature'     => array( 'sg-005' ),
	'black-rose'    => array( 'br-001', 'br-004' ),
	'love-hurts'    => array( 'lh-004' ),
);
$archive_products = array();
foreach ( $archive_product_map as $archive_collection => $archive_skus ) {
	$archive_resolved = skyyrose2_get_products_by_skus( $archive_skus, $archive_collection );
	foreach ( $archive_skus as $archive_sku ) {
		if ( isset( $archive_resolved[ $archive_sku ] ) ) {
			$archive_products[] = $archive_resolved[ $archive_sku ];
		}
	}
}
$archive_hero_skus     = array( 'sg-005', 'br-004', 'lh-004' );
$archive_hero_products = array();
foreach ( $archive_products as $archive_product ) {
	if ( ! is_a( $archive_product, 'WC_Product' ) ) {
		continue;
	}
	$archive_sku = strtolower( trim( (string) $archive_product->get_sku() ) );
	if ( in_array( $archive_sku, $archive_hero_skus, true ) ) {
		$archive_hero_products[ $archive_sku ] = $archive_product;
	}
}
get_header();
?>
<main id="primary" class="sr2-archive sr2-editorial-home" tabindex="-1">
	<div class="sr2-archive__inner">
		<?php if ( function_exists( 'wc_print_notices' ) ) : ?><div class="sr2-commerce-notices" aria-live="polite"><?php wc_print_notices(); ?></div><?php endif; ?>
		<?php get_template_part( 'template-parts/home/editorial-hero', null, array( 'collections' => $archive_collections, 'motion' => $archive_hero_motion, 'shop_url' => $archive_shop, 'products' => $archive_hero_products ) ); ?>
		<?php skyyrose2_print_hero_bootstrap(); ?>
		<?php get_template_part( 'template-parts/home/editorial-collection', null, array( 'collections' => $archive_collections ) ); ?>
		<?php get_template_part( 'template-parts/home/editorial-product-edit', null, array( 'products' => $archive_products ) ); ?>
		<?php get_template_part( 'template-parts/home/editorial-philosophy' ); ?>
		<?php get_template_part( 'template-parts/home/editorial-journal' ); ?>
		<details class="sr2-editorial-worlds"><summary><span class="sr2-world-index"><?php esc_html_e( 'House worlds', 'skyyrose-flagship-2' ); ?></span><span><?php esc_html_e( 'Explore the four worlds', 'skyyrose-flagship-2' ); ?></span><span aria-hidden="true">+</span></summary><div class="sr2-editorial-worlds__content"><?php get_template_part( 'template-parts/home/living-archive-worlds', null, array( 'collections' => $archive_collections ) ); ?></div></details>
	</div>
</main>
<?php get_footer(); ?>
