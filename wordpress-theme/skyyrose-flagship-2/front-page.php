<?php
/** Front Page — SkyyRose editorial house. @package SkyyRoseFlagship2 */
defined( 'ABSPATH' ) || exit;

$archive_collections = skyyrose2_collections();
$archive_hero_motion = skyyrose2_collection_hero_motion( 'black-rose', $archive_collections['black-rose']['hero'] );
$archive_shop        = skyyrose2_shop_url();
// Founder-approved V2 card fronts only. BR-002 and KIDS-002 stay out of curated card-front slots;
// founder-approved scroll-world scene casts (approved-scroll-world-scenes.json) are a separate mechanism.
$archive_product_map = array(
	'signature'    => array( 'sg-005' ),
	'black-rose'   => array( 'br-001', 'br-004' ),
	'love-hurts'   => array( 'lh-004' ),
	'kids-capsule' => array( 'kids-001' ),
);
$archive_products    = array();
foreach ( $archive_product_map as $archive_collection => $archive_skus ) {
	$archive_resolved = skyyrose2_get_products_by_skus( $archive_skus, $archive_collection );
	foreach ( $archive_skus as $archive_sku ) {
		if ( isset( $archive_resolved[ $archive_sku ] ) && is_a( $archive_resolved[ $archive_sku ], 'WC_Product' ) ) {
			$archive_products[ $archive_collection ][ $archive_sku ] = $archive_resolved[ $archive_sku ];
		}
	}
}
// The on-model film shows one worn look per world, in world order.
$archive_film_products = array();
foreach ( array(
	'sg-005'   => 'signature',
	'br-004'   => 'black-rose',
	'lh-004'   => 'love-hurts',
	'kids-001' => 'kids-capsule',
) as $archive_sku => $archive_collection ) {
	if ( isset( $archive_products[ $archive_collection ][ $archive_sku ] ) ) {
		$archive_film_products[ $archive_sku ] = $archive_products[ $archive_collection ][ $archive_sku ];
	}
}
get_header();
?>
<main id="primary" class="sr2-archive sr2-editorial-home" tabindex="-1">
	<div class="sr2-archive__inner">
		<?php
		if ( function_exists( 'wc_print_notices' ) ) :
			?>
			<div class="sr2-commerce-notices" aria-live="polite"><?php wc_print_notices(); ?></div><?php endif; ?>
		<?php get_template_part( 'template-parts/home/editorial-hero', null, array( 'collections' => $archive_collections, 'motion' => $archive_hero_motion, 'shop_url' => $archive_shop ) ); ?>
		<?php skyyrose2_print_hero_bootstrap(); ?>
		<?php get_template_part( 'template-parts/home/editorial-film', null, array( 'products' => $archive_film_products ) ); ?>
		<?php get_template_part( 'template-parts/home/editorial-collection', null, array( 'collections' => $archive_collections, 'products' => $archive_products ) ); ?>
		<section class="sr2-editorial-worlds sr2-band" aria-labelledby="sr2-editorial-worlds-title">
			<div class="sr2-band__head">
				<div><p class="sr2-eyebrow"><?php esc_html_e( 'House worlds', 'skyyrose-flagship-2' ); ?></p><h2 id="sr2-editorial-worlds-title" class="sr2-title-chapter"><?php esc_html_e( 'Enter the worlds.', 'skyyrose-flagship-2' ); ?></h2></div>
				<a class="sr2-editorial-link" href="<?php echo esc_url( skyyrose2_marketplace_page_url( 'collections' ) ); ?>"><?php esc_html_e( 'All collections', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">→</span></a>
			</div>
			<?php get_template_part( 'template-parts/home/living-archive-worlds', null, array( 'collections' => $archive_collections ) ); ?>
		</section>
		<?php get_template_part( 'template-parts/home/editorial-philosophy' ); ?>
		<?php get_template_part( 'template-parts/home/editorial-journal' ); ?>
	</div>
</main>
<?php get_footer(); ?>
