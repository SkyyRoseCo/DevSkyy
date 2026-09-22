<?php
/**
 * Shared static collection composition. Each world enters after its own review.
 * Narrative and scene authority remain in the existing collection definition;
 * this bounded edit consumes live products through the canonical commerce card.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

$world_slug        = $args['slug'] ?? '';
$world_collection  = $args['collection'] ?? array();
$world_collections = $args['collections'] ?? array();
// Presentation only: these fields describe existing monuments and composition,
// never product facts, prices, availability, or new media approval.
$world_presentations = array(
	'signature' => array(
		'composition' => 'origin',
		'ordinal'     => '01',
		'location'    => __( 'Golden Gate', 'skyyrose-flagship-2' ),
		'arrival_alt' => __( 'Bronze SkyyRose signature and SR rose monuments beside the Golden Gate Bridge.', 'skyyrose-flagship-2' ),
		'next_slug'   => 'black-rose',
	),
	'black-rose' => array(
		'composition' => 'nocturne',
		'ordinal'     => '02',
		'location'    => __( 'Bay Bridge', 'skyyrose-flagship-2' ),
		'arrival_alt' => __( 'Silver Black Rose lettering and a star-and-rose monument face the Bay Bridge beneath a full moon.', 'skyyrose-flagship-2' ),
		'next_slug'   => 'love-hurts',
	),
	'love-hurts' => array(
		'composition' => 'devotion',
		'ordinal'     => '03',
		'location'    => __( 'The rose aisle', 'skyyrose-flagship-2' ),
		'arrival_alt' => __( 'Crimson Love Hurts lettering and a rose-and-heart star frame a cathedral aisle, with a cloaked figure facing a rose under glass.', 'skyyrose-flagship-2' ),
		'next_slug'   => 'kids-capsule',
	),
	'kids-capsule' => array(
		'composition' => 'inheritance',
		'ordinal'     => '04',
		'location'    => __( 'The heir’s room', 'skyyrose-flagship-2' ),
		'arrival_alt' => __( 'The Skyy mascot sits on a gold-trimmed throne beneath The Heir lettering, with Next Up at its base.', 'skyyrose-flagship-2' ),
		'next_slug'   => 'signature',
	),
);
$world_presentation = $world_presentations[ $world_slug ] ?? array();
if ( ! $world_presentation || empty( $world_collection['name'] ) ) {
	return;
}
$world_products = array_values( array_filter( skyyrose2_get_products( 12, $world_slug ), static function ( $item ) {
	return is_a( $item, 'WC_Product' ) && $item->is_visible();
} ) );
$world_shop_url = add_query_arg( 'product_cat', $world_slug, skyyrose2_shop_url() );
$world_args     = array( 'slug' => $world_slug, 'collection' => $world_collection, 'presentation' => $world_presentation );
?>
<main id="primary" class="sr2-collection-world" data-collection="<?php echo esc_attr( $world_slug ); ?>" data-composition="<?php echo esc_attr( $world_presentation['composition'] ); ?>">
	<div class="sr2-collection-world__inner">
		<?php if ( function_exists( 'wc_print_notices' ) ) : ?>
			<div class="sr2-commerce-notices" aria-live="polite"><?php wc_print_notices(); ?></div>
		<?php endif; ?>
		<?php get_template_part( 'template-parts/collections/arrival', null, $world_args ); ?>
		<?php get_template_part( 'template-parts/collections/scroll-world', null, $world_args ); ?>
		<section id="shop" class="sr2-world-edit"<?php if ( in_array( $world_slug, array( 'signature', 'black-rose', 'love-hurts' ), true ) ) : ?> data-scene-handoff="<?php echo esc_attr( $world_slug ); ?>"<?php endif; ?> aria-labelledby="sr2-world-edit-title" tabindex="-1">
			<header class="sr2-world-section-head">
				<p class="sr2-world-index"><?php echo esc_html( $world_collection['shop_kicker'] ); ?></p>
				<h2 id="sr2-world-edit-title"><?php echo esc_html( $world_collection['shop_heading'] ); ?></h2>
			</header>
			<?php if ( $world_products ) : ?>
				<?php get_template_part( 'template-parts/collections/product-edit', null, array( 'products' => array_slice( $world_products, 0, 4 ), 'offset' => 0 ) ); ?>
			<?php else : ?>
				<p class="sr2-world-empty"><?php esc_html_e( 'No pieces are currently listed in this edit.', 'skyyrose-flagship-2' ); ?></p>
				<a class="sr2-world-text-link" href="<?php echo esc_url( skyyrose2_shop_url() ); ?>"><?php esc_html_e( 'Browse the Shop', 'skyyrose-flagship-2' ); ?> <span aria-hidden="true">↗</span></a>
			<?php endif; ?>
		</section>
		<?php get_template_part( 'template-parts/collections/story', null, $world_args ); ?>
		<?php if ( count( $world_products ) > 4 ) : ?>
			<section class="sr2-world-edit sr2-world-edit--continuation" aria-labelledby="sr2-world-continuation-title">
				<header class="sr2-world-section-head">
					<p class="sr2-world-index"><?php echo esc_html( $world_collection['name'] ); ?></p>
					<h2 id="sr2-world-continuation-title"><?php echo esc_html( $world_collection['invitation_title'] ); ?></h2>
				</header>
				<?php get_template_part( 'template-parts/collections/product-edit', null, array( 'products' => array_slice( $world_products, 4 ), 'offset' => 4 ) ); ?>
			</section>
		<?php endif; ?>
		<div class="sr2-world-shop-link">
			<p><?php echo esc_html( $world_collection['invitation'] ); ?></p>
			<a class="sr2-control sr2-control--secondary" href="<?php echo esc_url( $world_shop_url ); ?>"><?php echo esc_html( sprintf( __( 'View all %s', 'skyyrose-flagship-2' ), $world_collection['name'] ) ); ?> <span aria-hidden="true">↗</span></a>
		</div>
		<?php if ( 'black-rose' === $world_slug ) : ?>
			<?php get_template_part( 'template-parts/commerce/town-line' ); ?>
		<?php endif; ?>
		<?php get_template_part( 'template-parts/collections/next-world', null, array( 'slug' => $world_slug, 'collections' => $world_collections, 'next_slug' => $world_presentation['next_slug'] ) ); ?>
	</div>
</main>
