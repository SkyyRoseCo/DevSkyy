<?php
/**
 * Storefront homepage.
 *
 * Uses collection data and catalog resolvers already trusted by collection
 * pages. No product image path derives from a filename guess.
 *
 * @package SkyyRose
 * @since 2.2.4
 */

defined( 'ABSPATH' ) || exit;

$collections = function_exists( 'skyyrose_home_rooms' ) ? skyyrose_home_rooms() : array();
$shop_url    = function_exists( 'wc_get_page_permalink' ) ? wc_get_page_permalink( 'shop' ) : home_url( '/shop/' );
$preorder    = home_url( '/pre-order/' );
?>
<main id="primary" class="site-main sr-home" role="main" tabindex="-1">
	<section class="sr-home__hero" aria-labelledby="sr-home-title">
		<div class="sr-home__hero-media" aria-hidden="true">
			<picture>
				<source srcset="<?php echo esc_url( SKYYROSE_ASSETS_URI . '/images/hero/home-hero-poster-720w.webp?v=' . SKYYROSE_VERSION ); ?>" type="image/webp">
				<img src="<?php echo esc_url( SKYYROSE_ASSETS_URI . '/images/hero/home-hero-poster-720w.jpg?v=' . SKYYROSE_VERSION ); ?>" alt="" width="720" height="1280" fetchpriority="high" decoding="sync">
			</picture>
		</div>
		<div class="sr-home__hero-wash" aria-hidden="true"></div>
		<div class="sr-home__hero-content">
			<p class="sr-home__eyebrow"><?php esc_html_e( 'Oakland, California · Est. 2020', 'skyyrose' ); ?></p>
			<h1 id="sr-home-title" class="sr-home__title"><?php esc_html_e( 'SkyyRose', 'skyyrose' ); ?></h1>
			<p class="sr-home__lede"><?php esc_html_e( 'Limited-edition streetwear rooted in The Town. Built by a father. Named after a daughter.', 'skyyrose' ); ?></p>
			<div class="sr-home__actions">
				<a class="sr-home__button sr-home__button--solid" href="<?php echo esc_url( $shop_url ); ?>"><?php esc_html_e( 'Shop New Arrivals', 'skyyrose' ); ?></a>
				<a class="sr-home__button sr-home__button--line" href="#collections"><?php esc_html_e( 'Enter Collections', 'skyyrose' ); ?></a>
			</div>
		</div>
	</section>

	<section id="collections" class="sr-home__collections" aria-labelledby="sr-home-collections-title">
		<div class="sr-home__section-head">
			<p class="sr-home__eyebrow"><?php esc_html_e( 'Choose Your World', 'skyyrose' ); ?></p>
			<h2 id="sr-home-collections-title"><?php esc_html_e( 'Four collections. Four points of view.', 'skyyrose' ); ?></h2>
			<p><?php esc_html_e( 'Walk into a collection, shop its pieces, then stay for its world.', 'skyyrose' ); ?></p>
		</div>

		<div class="sr-home__collection-rail" role="region" aria-label="<?php esc_attr_e( 'Collection worlds. Scroll horizontally to explore.', 'skyyrose' ); ?>" tabindex="0">
			<?php foreach ( $collections as $index => $collection ) : ?>
				<article class="sr-home__collection" data-collection="<?php echo esc_attr( $collection['slug'] ); ?>">
					<a class="sr-home__collection-frame" href="<?php echo esc_url( $collection['href'] ); ?>">
						<?php if ( ! empty( $collection['still'] ) ) : ?>
							<img src="<?php echo esc_url( $collection['still'] ); ?>" alt="<?php echo esc_attr( $collection['label'] ); ?>" width="1920" height="1080" loading="<?php echo 0 === $index ? 'eager' : 'lazy'; ?>" decoding="async">
						<?php endif; ?>
						<span class="sr-home__collection-shade" aria-hidden="true"></span>
						<span class="sr-home__collection-index"><?php echo esc_html( sprintf( '%02d', $index + 1 ) ); ?></span>
						<span class="sr-home__collection-copy">
							<strong><?php echo esc_html( $collection['label'] ); ?></strong>
							<span><?php echo esc_html( $collection['poetic'] ); ?></span>
							<em><?php esc_html_e( 'Shop Collection', 'skyyrose' ); ?> <span aria-hidden="true">→</span></em>
						</span>
					</a>
				</article>
			<?php endforeach; ?>
		</div>
		<p class="sr-home__rail-note" aria-hidden="true"><?php esc_html_e( 'Scroll to move through worlds', 'skyyrose' ); ?> <span>→</span></p>
	</section>

	<?php
	get_template_part(
		'template-parts/product-grid',
		null,
		array(
			'featured'      => true,
			'limit'         => 6,
			'heading'       => __( 'Pieces In Rotation', 'skyyrose' ),
			'subheading'    => __( 'Verified pieces from across the house.', 'skyyrose' ),
			'section_id'    => 'new-arrivals',
			'section_class' => 'sr-home__products',
			'reveal_class'  => '',
		)
	);
	?>

	<section class="sr-home__preorder" aria-labelledby="sr-home-preorder-title">
		<div class="sr-home__preorder-mark" aria-hidden="true">
			<img src="<?php echo esc_url( SKYYROSE_ASSETS_URI . '/branding/sr-primary-hero.webp?v=' . SKYYROSE_VERSION ); ?>" alt="" width="1024" height="1024" loading="lazy" decoding="async">
		</div>
		<div class="sr-home__preorder-copy">
			<p class="sr-home__eyebrow"><?php esc_html_e( 'Reserve Future Pieces', 'skyyrose' ); ?></p>
			<h2 id="sr-home-preorder-title"><?php esc_html_e( 'Pre-order is its own room.', 'skyyrose' ); ?></h2>
			<p><?php esc_html_e( 'No noise. No manufactured countdown. Choose collection, choose piece, reserve your place.', 'skyyrose' ); ?></p>
			<a class="sr-home__button sr-home__button--line" href="<?php echo esc_url( $preorder ); ?>"><?php esc_html_e( 'Enter Pre-Order', 'skyyrose' ); ?></a>
		</div>
	</section>

	<section class="sr-home__origin" aria-labelledby="sr-home-origin-title">
		<img src="<?php echo esc_url( SKYYROSE_ASSETS_URI . '/images/homepage-story-founder.webp?v=' . SKYYROSE_VERSION ); ?>" alt="SkyyRose founder in Oakland" width="1200" height="1600" loading="lazy" decoding="async">
		<div>
			<p class="sr-home__eyebrow"><?php esc_html_e( 'Founder Story', 'skyyrose' ); ?></p>
			<h2 id="sr-home-origin-title"><?php esc_html_e( 'Built by a father. Named after a daughter.', 'skyyrose' ); ?></h2>
			<a href="<?php echo esc_url( home_url( '/about/' ) ); ?>"><?php esc_html_e( 'Meet SkyyRose', 'skyyrose' ); ?> <span aria-hidden="true">→</span></a>
		</div>
	</section>
</main>
