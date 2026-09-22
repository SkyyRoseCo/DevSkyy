<?php
/** Current approved scene chapters with native scroll and real Woo destinations. @package SkyyRoseFlagship2 */
defined( 'ABSPATH' ) || exit;
$scene_slug = $args['slug'];
$scene_collection = $args['collection'];
$scene_chapters = skyyrose2_collection_commerce_scenes( $scene_slug );
if ( ! $scene_chapters ) { return; }
?>
<section class="sr2-recovered-worlds" data-recovery-rail aria-labelledby="sr2-recovered-worlds-title">
	<header class="sr2-world-section-head"><div><p class="sr2-world-index"><?php esc_html_e( 'Scroll World', 'skyyrose-flagship-2' ); ?></p><h2 id="sr2-recovered-worlds-title" data-sr2-type-motion="collection"><span class="screen-reader-text"><?php echo esc_html( $scene_collection['name'] ); ?>: </span><?php echo esc_html( $scene_collection['world_heading'] ); ?></h2><p><?php echo esc_html( $scene_collection['world_intro'] ); ?></p></div><div class="sr2-recovery-controls" hidden><button type="button" data-recovery-prev aria-label="<?php esc_attr_e( 'Previous chapter', 'skyyrose-flagship-2' ); ?>">←</button><span data-recovery-count aria-live="polite"></span><button type="button" data-recovery-next aria-label="<?php esc_attr_e( 'Next chapter', 'skyyrose-flagship-2' ); ?>">→</button></div></header>
	<div class="sr2-recovered-worlds__rail" data-recovery-track tabindex="0" aria-label="<?php esc_attr_e( 'Collection story chapters', 'skyyrose-flagship-2' ); ?>">
	<?php foreach ( $scene_chapters as $scene_index => $scene_chapter ) : ?>
		<?php if ( ! empty( $scene_chapter['hero_composed'] ) ) : ?>
			<?php get_template_part( 'template-parts/commerce/hero-composed-scene', null, array( 'scene' => $scene_chapter, 'collection' => $scene_slug, 'index' => $scene_index ) ); ?>

		<?php endif; ?>
	<?php endforeach; ?>
	</div>
</section>
