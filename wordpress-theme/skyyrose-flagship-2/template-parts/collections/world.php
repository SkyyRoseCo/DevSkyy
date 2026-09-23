<?php
/**
 * Collection world: Arrival → Chapters → Scroll World → Edit → Story → Colophon.
 *
 * Narrative and scene authority remain in skyyrose2_collections(); this
 * composition consumes live products through the canonical commerce card.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

$world_slug        = $args['slug'] ?? '';
$world_collection  = $args['collection'] ?? array();
$world_collections = $args['collections'] ?? array();
// Presentation (ordinal, focal points, lockup geometry) is shared through inc/collection-presentation.php.
$world_presentation  = skyyrose2_collection_presentation( $world_slug );
if ( ! $world_presentation || empty( $world_collection['name'] ) ) {
	return;
}
$world_products       = array_values(
	array_filter(
		skyyrose2_get_products( 12, $world_slug ),
		static function ( $item ) {
			return is_a( $item, 'WC_Product' ) && $item->is_visible();
		}
	)
);
$world_shop_url       = add_query_arg( 'product_cat', $world_slug, skyyrose2_shop_url() );
$world_scene_chapters = skyyrose2_collection_commerce_scenes( $world_slug );
$world_args           = array(
	'slug'            => $world_slug,
	'collection'      => $world_collection,
	'presentation'    => $world_presentation,
	// Without an approved Scroll World the founder's world statement opens chapter 01 instead.
	'world_statement' => empty( $world_scene_chapters ),
);
?>
<main id="primary" class="sr2-collection-world" data-collection="<?php echo esc_attr( $world_slug ); ?>" data-composition="<?php echo esc_attr( $world_presentation['composition'] ); ?>">
	<?php if ( function_exists( 'wc_print_notices' ) ) : ?>
		<div class="sr2-commerce-notices" aria-live="polite"><?php wc_print_notices(); ?></div>
	<?php endif; ?>
	<?php get_template_part( 'template-parts/collections/arrival', null, $world_args ); ?>
	<?php get_template_part( 'template-parts/collections/chapters', null, $world_args ); ?>
	<?php get_template_part( 'template-parts/collections/scroll-world', null, $world_args ); ?>
	<section id="shop" class="sr2-band sr2-world-edit"
	<?php
	if ( in_array( $world_slug, array( 'signature', 'black-rose', 'love-hurts' ), true ) ) :
		?>
		data-scene-handoff="<?php echo esc_attr( $world_slug ); ?>"<?php endif; ?> aria-labelledby="sr2-world-edit-title" tabindex="-1">
		<div class="sr2-band__head sr2-world-section-head">
			<div>
				<p class="sr2-eyebrow"><?php echo esc_html( $world_collection['shop_kicker'] ); ?></p>
				<h2 id="sr2-world-edit-title" class="sr2-title-chapter"><?php echo esc_html( $world_collection['shop_heading'] ); ?></h2>
				<p class="sr2-lede"><?php echo esc_html( $world_collection['shop_intro'] ); ?></p>
			</div>
			<a class="sr2-editorial-link" href="<?php echo esc_url( $world_shop_url ); ?>"><?php echo esc_html( sprintf( __( 'View all %s', 'skyyrose-flagship-2' ), $world_collection['name'] ) ); ?><span aria-hidden="true">↗</span></a>
		</div>
		<?php if ( $world_products ) : ?>
			<?php
			get_template_part(
				'template-parts/collections/product-edit',
				null,
				array(
					'products' => $world_products,
					'offset'   => 0,
				)
			);
			?>
		<?php else : ?>
			<div class="sr2-world-empty">
				<p class="sr2-lede"><?php esc_html_e( 'No pieces are currently listed in this edit.', 'skyyrose-flagship-2' ); ?></p>
				<a class="sr2-editorial-link" href="<?php echo esc_url( skyyrose2_shop_url() ); ?>"><?php esc_html_e( 'Browse the Shop', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">↗</span></a>
			</div>
		<?php endif; ?>
	</section>
	<?php get_template_part( 'template-parts/collections/story', null, $world_args ); ?>
	<?php if ( 'black-rose' === $world_slug ) : ?>
		<?php get_template_part( 'template-parts/commerce/town-line' ); ?>
	<?php endif; ?>
	<?php
	get_template_part(
		'template-parts/collections/next-world',
		null,
		array(
			'slug'        => $world_slug,
			'collections' => $world_collections,
			'next_slug'   => $world_presentation['next_slug'],
		)
	);
	?>
</main>
