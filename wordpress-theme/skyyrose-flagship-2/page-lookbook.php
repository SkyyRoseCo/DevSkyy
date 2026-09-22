<?php
/**
 * Template Name: SkyyRose Lookbook
 * Shoppable scene chapters with native product and collection destinations.
 * @package SkyyRoseFlagship2
 */
defined( 'ABSPATH' ) || exit;
$lookbook_collections = skyyrose2_collections();
$lookbook_cast = array( 'signature' => 'sg-005', 'black-rose' => 'br-001', 'love-hurts' => 'lh-003', 'kids-capsule' => 'kids-002' );
$lookbook_suffix = defined( 'SCRIPT_DEBUG' ) && SCRIPT_DEBUG ? '' : '.min';
foreach ( array( 'collection-world', 'premium-commerce', 'hero-commerce-scenes', 'collection-scene-motion', 'lookbook' ) as $lookbook_style ) {
	$lookbook_asset = '/assets/css/' . $lookbook_style . $lookbook_suffix . '.css';
	wp_enqueue_style( 'skyyrose2-' . $lookbook_style, SKYYROSE2_URI . $lookbook_asset, array( 'skyyrose2-theme' ), skyyrose2_asset_version( $lookbook_asset ) );
}
$lookbook_motion_script = '/assets/js/visual-recovery' . $lookbook_suffix . '.js';
wp_enqueue_script( 'skyyrose2-visual-recovery', SKYYROSE2_URI . $lookbook_motion_script, array(), skyyrose2_asset_version( $lookbook_motion_script ), true );
$lookbook_scene_script = '/assets/js/collection-scene-motion' . $lookbook_suffix . '.js';
wp_enqueue_script( 'skyyrose2-collection-scene-motion', SKYYROSE2_URI . $lookbook_scene_script, array(), skyyrose2_asset_version( $lookbook_scene_script ), true );
get_header();
?>
<main id="primary" class="sr2-lookbook" tabindex="-1">
	<header class="sr2-lookbook__cover">
		<p class="sr2-lookbook__folio"><span><?php esc_html_e( 'SkyyRose / Oakland, California', 'skyyrose-flagship-2' ); ?></span><span><?php esc_html_e( 'The house lookbook', 'skyyrose-flagship-2' ); ?></span></p>
		<h1><?php esc_html_e( 'Four worlds.', 'skyyrose-flagship-2' ); ?><br><em><?php esc_html_e( 'One house.', 'skyyrose-flagship-2' ); ?></em></h1>
		<div class="sr2-lookbook__cover-note"><p><?php esc_html_e( 'A house built by a father, named after a daughter, and rooted in The Town.', 'skyyrose-flagship-2' ); ?></p><a class="sr2-lookbook__link" href="<?php echo esc_url( skyyrose2_shop_url() ); ?>"><?php esc_html_e( 'Shop the house', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">↗</span></a></div>
		<nav class="sr2-lookbook__index" aria-label="<?php esc_attr_e( 'Lookbook chapters', 'skyyrose-flagship-2' ); ?>">
			<?php $lookbook_index = 0; foreach ( $lookbook_cast as $lookbook_slug => $lookbook_sku ) : ?>
				<a href="#lookbook-<?php echo esc_attr( $lookbook_slug ); ?>"><span><?php echo esc_html( sprintf( '%02d', ++$lookbook_index ) ); ?></span><?php echo esc_html( $lookbook_collections[ $lookbook_slug ]['name'] ); ?></a>
			<?php endforeach; ?>
		</nav>
	</header>
	<?php $lookbook_index = 0; foreach ( $lookbook_cast as $lookbook_slug => $lookbook_sku ) : ?>
		<?php
		$lookbook_collection = $lookbook_collections[ $lookbook_slug ];
		$lookbook_scenes = array_values( array_filter( skyyrose2_collection_commerce_scenes( $lookbook_slug ), static function ( $scene ) {
			return ! empty( $scene['hero_composed'] );
		} ) );
		// A collection edit is not evidence of garments appearing in its hero film.
		$lookbook_products = $lookbook_scenes ? array() : skyyrose2_get_products_by_skus( array( $lookbook_sku ), $lookbook_slug );
		$lookbook_motion = skyyrose2_collection_hero_motion( $lookbook_slug, $lookbook_collection['hero'] );
		?>
		<section id="lookbook-<?php echo esc_attr( $lookbook_slug ); ?>" class="sr2-lookbook__chapter" data-collection="<?php echo esc_attr( $lookbook_slug ); ?>" aria-labelledby="lookbook-title-<?php echo esc_attr( $lookbook_slug ); ?>" tabindex="-1">
			<header class="sr2-lookbook__chapter-head"><span class="sr2-lookbook__number" aria-hidden="true"><?php echo esc_html( sprintf( '%02d', ++$lookbook_index ) ); ?></span><div><p class="sr2-lookbook__eyebrow"><?php echo esc_html( $lookbook_collection['kicker'] ); ?></p><h2 id="lookbook-title-<?php echo esc_attr( $lookbook_slug ); ?>"><?php echo esc_html( $lookbook_collection['name'] ); ?></h2></div><p><?php echo esc_html( $lookbook_collection['headline'] ); ?></p></header>
			<?php if ( $lookbook_scenes ) : ?>
				<p class="sr2-lookbook__shopping-note"><?php esc_html_e( 'Shop the looks. Each scene connects to the exact pieces in its cast.', 'skyyrose-flagship-2' ); ?></p>
				<nav class="sr2-lookbook__scene-index" aria-label="<?php echo esc_attr( sprintf( __( '%s looks', 'skyyrose-flagship-2' ), $lookbook_collection['name'] ) ); ?>">
					<?php foreach ( $lookbook_scenes as $lookbook_scene_index => $lookbook_scene ) : ?>
						<a href="#lookbook-scene-<?php echo esc_attr( sanitize_html_class( strtolower( $lookbook_scene['scene_id'] ) ) ); ?>"><span><?php echo esc_html( sprintf( '%02d', $lookbook_scene_index + 1 ) ); ?></span><?php echo esc_html( $lookbook_scene['label'] ); ?></a>
					<?php endforeach; ?>
				</nav>
				<div class="sr2-lookbook__looks">
					<?php foreach ( $lookbook_scenes as $lookbook_scene_index => $lookbook_scene ) : ?>
						<div class="sr2-lookbook__look" id="lookbook-scene-<?php echo esc_attr( sanitize_html_class( strtolower( $lookbook_scene['scene_id'] ) ) ); ?>" tabindex="-1">
							<?php get_template_part( 'template-parts/commerce/hero-composed-scene', null, array( 'scene' => $lookbook_scene, 'collection' => $lookbook_slug, 'index' => $lookbook_scene_index ) ); ?>
						</div>
					<?php endforeach; ?>
				</div>
				<details class="sr2-lookbook__atmosphere"><summary><?php esc_html_e( 'Watch the collection film', 'skyyrose-flagship-2' ); ?></summary>
			<?php endif; ?>
			<figure class="sr2-lookbook__scene"><div class="sr2-lookbook__motion" data-recovery-hero><img src="<?php echo esc_url( skyyrose2_sot_asset_uri( $lookbook_collection['hero'] ) ); ?>" srcset="<?php echo esc_url( skyyrose2_sot_asset_uri( $lookbook_collection['hero_mobile'] ) ); ?> 640w, <?php echo esc_url( skyyrose2_sot_asset_uri( $lookbook_collection['hero_tablet'] ) ); ?> 1024w, <?php echo esc_url( skyyrose2_sot_asset_uri( $lookbook_collection['hero'] ) ); ?> 1440w" sizes="(max-width: 47.99em) calc(100vw - 2rem), calc(100vw - 6rem)" width="1440" height="810" alt="<?php echo esc_attr( sprintf( __( '%s collection world', 'skyyrose-flagship-2' ), $lookbook_collection['name'] ) ); ?>" loading="lazy" decoding="async"><?php if ( $lookbook_motion ) : ?><video data-recovery-hero-video muted loop playsinline preload="none" aria-hidden="true"><source data-src="<?php echo esc_url( $lookbook_motion['webm'] ); ?>" type="video/webm"><source data-src="<?php echo esc_url( $lookbook_motion['mp4'] ); ?>" type="video/mp4"></video><button class="sr2-recovery-motion-toggle" type="button" data-recovery-motion-toggle hidden><?php esc_html_e( 'Pause motion', 'skyyrose-flagship-2' ); ?></button><?php endif; ?></div><figcaption><span><?php echo esc_html( $lookbook_collection['name'] ); ?></span><span><?php esc_html_e( 'The world behind the wardrobe', 'skyyrose-flagship-2' ); ?></span></figcaption></figure>
			<?php if ( $lookbook_scenes ) : ?></details><?php endif; ?>
			<div class="sr2-lookbook__edit<?php echo $lookbook_scenes ? ' sr2-lookbook__edit--story' : ''; ?>"><div class="sr2-lookbook__story"><p class="sr2-lookbook__eyebrow"><?php esc_html_e( 'The collection story', 'skyyrose-flagship-2' ); ?></p><h3><?php echo esc_html( $lookbook_collection['shop_heading'] ); ?></h3><p><?php echo esc_html( $lookbook_collection['manifesto'] ); ?></p><div class="sr2-lookbook__destinations"><a class="sr2-lookbook__link" href="<?php echo esc_url( skyyrose2_collection_url( $lookbook_slug ) ); ?>"><?php esc_html_e( 'Shop collection', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">↗</span></a><a class="sr2-lookbook__link" href="<?php echo esc_url( skyyrose2_immersive_url( $lookbook_slug ) ); ?>"><?php esc_html_e( 'Explore world', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">↗</span></a></div></div>
			<?php if ( ! $lookbook_scenes ) : ?><div class="sr2-lookbook__product">
				<p class="sr2-lookbook__eyebrow"><?php esc_html_e( 'Collection edit', 'skyyrose-flagship-2' ); ?></p>
				<?php if ( $lookbook_products ) : ?>
					<?php get_template_part( 'template-parts/collections/product-edit', null, array( 'products' => array_values( $lookbook_products ) ) ); ?>
				<?php else : ?>
					<p><?php esc_html_e( 'Explore the collection for the current edit.', 'skyyrose-flagship-2' ); ?></p>
				<?php endif; ?>
			</div><?php endif; ?></div>
		</section>
	<?php endforeach; ?>
	<footer class="sr2-lookbook__closing"><p class="sr2-lookbook__eyebrow"><?php esc_html_e( 'Rooted in Oakland', 'skyyrose-flagship-2' ); ?></p><h2><?php esc_html_e( 'A legacy in bloom.', 'skyyrose-flagship-2' ); ?></h2><a class="sr2-lookbook__link" href="<?php echo esc_url( skyyrose2_shop_url() ); ?>"><?php esc_html_e( 'Find your chapter', 'skyyrose-flagship-2' ); ?><span aria-hidden="true">↗</span></a></footer>
</main>
<?php get_footer(); ?>
