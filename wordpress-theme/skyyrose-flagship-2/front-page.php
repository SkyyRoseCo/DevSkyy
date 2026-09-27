<?php
/**
 * Front Page — House of Roses.
 *
 * The approved V2 composition is a house journey, not a generic product grid:
 * three opening worlds, verified on-model filmstrip, collection-owned product
 * portals, the Kids Capsule Royal Procession, a truthful featured-product
 * threshold, and the Jersey Series Skyy Rose Tour reveal. WooCommerce remains the sole
 * authority for product, price, stock, variation, cart, and checkout state.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

$shop_url    = function_exists( 'wc_get_page_permalink' ) ? wc_get_page_permalink( 'shop' ) : home_url( '/shop/' );
$collections = skyyrose2_collections();
$hero_models = array(
	array(
		'slug'  => 'signature',
		'label' => __( 'Signature', 'skyyrose-flagship-2' ),
		'sku'   => 'SG-005',
		'href'  => skyyrose2_collection_url( 'signature' ),
		'image' => skyyrose2_sot_asset_uri( 'images/home/on-model/signature-sg-005.webp' ),
	),
	array(
		'slug'  => 'black-rose',
		'label' => __( 'Black Rose', 'skyyrose-flagship-2' ),
		'sku'   => 'BR-004',
		'href'  => skyyrose2_collection_url( 'black-rose' ),
		'image' => skyyrose2_sot_asset_uri( 'images/home/on-model/black-rose-br-004.webp' ),
	),
	array(
		'slug'  => 'love-hurts',
		'label' => __( 'Love Hurts', 'skyyrose-flagship-2' ),
		'sku'   => 'LH-004',
		'href'  => skyyrose2_collection_url( 'love-hurts' ),
		'image' => skyyrose2_sot_asset_uri( 'images/home/on-model/love-hurts-lh-004.webp' ),
	),
);
$opening_cast = array(
	'signature'  => skyyrose2_get_products_by_skus( array( 'sg-005' ), 'signature' )['sg-005'] ?? null,
	'black-rose' => skyyrose2_get_products_by_skus( array( 'br-004' ), 'black-rose' )['br-004'] ?? null,
	'love-hurts' => skyyrose2_get_products_by_skus( array( 'lh-004' ), 'love-hurts' )['lh-004'] ?? null,
);
$kids_cast        = skyyrose2_get_products_by_skus( array( 'kids-001', 'kids-002' ), 'kids-capsule' );
$featured_product = $opening_cast['signature'];

get_header();
?>
<main id="primary" class="site-main sr-house" role="main" tabindex="-1">
	<section class="sr-house-hero" aria-labelledby="sr-house-title">
		<div class="sr-house-hero__scene" aria-hidden="true">
			<picture>
				<source media="(max-width: 47.99em)" srcset="<?php echo esc_url( skyyrose2_sot_asset_uri( 'images/hero/responsive/black-rose-bay-bridge-monuments-v4-640w.webp' ) ); ?>">
				<source media="(max-width: 74.99em)" srcset="<?php echo esc_url( skyyrose2_sot_asset_uri( 'images/hero/responsive/black-rose-bay-bridge-monuments-v4-1024w.webp' ) ); ?>">
				<img src="<?php echo esc_url( skyyrose2_sot_asset_uri( 'images/hero/responsive/black-rose-bay-bridge-monuments-v4-1440w.webp' ) ); ?>" alt="" width="1440" height="810" fetchpriority="high" decoding="sync">
			</picture>
			<video muted playsinline preload="none" poster="<?php echo esc_url( skyyrose2_sot_asset_uri( 'images/hero/responsive/black-rose-bay-bridge-monuments-v4-1440w.webp' ) ); ?>" data-hero-video aria-hidden="true">
				<source data-src="<?php echo esc_url( SKYYROSE2_URI . '/assets/video/skyyrose-tour-around-the-bay.webm' ); ?>" type="video/webm">
				<source data-src="<?php echo esc_url( SKYYROSE2_URI . '/assets/video/skyyrose-tour-around-the-bay.mp4' ); ?>" type="video/mp4">
			</video>
		</div>
		<div class="sr-house-hero__atmosphere" aria-hidden="true"><span class="sr-house-hero__clouds"></span><span class="sr-house-hero__bridge-lights"></span><span class="sr-house-hero__scanline"></span></div>
		<div class="sr-house-hero__veil" aria-hidden="true"></div>
		<div class="sr-house-hero__copy">
			<p class="sr-house-hero__location"><?php esc_html_e( 'Oakland, California', 'skyyrose-flagship-2' ); ?></p>
			<h1 id="sr-house-title" data-hero-headline><?php esc_html_e( 'SkyyRose', 'skyyrose-flagship-2' ); ?></h1>
			<p><?php esc_html_e( 'A house built by a father, named after a daughter, and rooted in The Town.', 'skyyrose-flagship-2' ); ?></p>
			<div class="sr-house-hero__actions">
				<a class="sr-home__button sr-home__button--solid" href="#collections"><?php esc_html_e( 'Choose your world', 'skyyrose-flagship-2' ); ?></a>
				<a class="sr-home__button sr-home__button--line" href="<?php echo esc_url( $shop_url ); ?>"><?php esc_html_e( 'Shop the house', 'skyyrose-flagship-2' ); ?></a>
			</div>
		</div>
		<nav class="sr-house-hero__worlds" aria-label="<?php esc_attr_e( 'Opening collection worlds', 'skyyrose-flagship-2' ); ?>">
			<?php foreach ( $hero_models as $index => $model ) : ?>
				<a href="<?php echo esc_url( $model['href'] ); ?>"><span><?php echo esc_html( sprintf( '%02d', $index + 1 ) ); ?></span><b><?php echo esc_html( $model['label'] ); ?></b></a>
			<?php endforeach; ?>
		</nav>
	</section>

	<section class="sr-house-filmstrip" aria-labelledby="sr-house-filmstrip-title">
		<header class="screen-reader-text"><h2 id="sr-house-filmstrip-title"><?php esc_html_e( 'The opening collection filmstrip', 'skyyrose-flagship-2' ); ?></h2></header>
		<div class="sr-home__hero-model-loop" data-home-model-loop data-loop-state="running" aria-label="<?php esc_attr_e( 'Verified on-model looks from the three opening SkyyRose collection worlds', 'skyyrose-flagship-2' ); ?>">
			<div class="sr-home__hero-model-track">
				<?php for ( $pass = 0; $pass < 2; $pass++ ) : ?>
					<?php foreach ( $hero_models as $index => $model ) : ?>
						<?php if ( 0 === $pass ) : ?><a class="sr-home__hero-model-card" data-collection="<?php echo esc_attr( $model['slug'] ); ?>" href="<?php echo esc_url( $model['href'] ); ?>"><?php else : ?><span class="sr-home__hero-model-card" data-collection="<?php echo esc_attr( $model['slug'] ); ?>" data-loop-copy="true" aria-hidden="true"><?php endif; ?>
							<span class="sr-home__hero-model-portrait"><img src="<?php echo esc_url( $model['image'] ); ?>" alt="<?php echo 0 === $pass ? esc_attr( sprintf( __( '%s collection on-model look', 'skyyrose-flagship-2' ), $model['label'] ) ) : ''; ?>" width="1024" height="1536" loading="<?php echo 0 === $pass && 0 === $index ? 'eager' : 'lazy'; ?>" decoding="async"></span>
							<span class="sr-home__hero-model-caption"><b><?php echo esc_html( sprintf( '%02d · %s', $index + 1, $model['label'] ) ); ?></b><small><?php echo esc_html( $model['sku'] ); ?> · <?php esc_html_e( 'Enter the world', 'skyyrose-flagship-2' ); ?></small></span>
						<?php if ( 0 === $pass ) : ?></a><?php else : ?></span><?php endif; ?>
					<?php endforeach; ?>
				<?php endfor; ?>
			</div>
			<button class="sr-home__hero-model-toggle" type="button" data-home-model-toggle aria-pressed="false"><?php esc_html_e( 'Pause rotation', 'skyyrose-flagship-2' ); ?></button>
		</div>
	</section>

	<section id="collections" class="sr-house-portals" aria-labelledby="sr-house-portals-title">
		<header class="sr-house-section-head">
			<p><?php esc_html_e( 'Enter a world. Claim your story.', 'skyyrose-flagship-2' ); ?></p>
			<h2 id="sr-house-portals-title"><?php esc_html_e( 'The opening three.', 'skyyrose-flagship-2' ); ?></h2>
		</header>
		<div class="sr2-products sr-house-portals__grid">
			<?php $portal_index = 0; ?>
			<?php foreach ( $opening_cast as $product ) : ?>
				<?php if ( $product ) : ?><?php skyyrose2_render_product_loop_card( $product, $portal_index++ ); ?><?php endif; ?>
			<?php endforeach; ?>
		</div>
	</section>

	<?php
	get_template_part(
		'template-parts/home/kids-capsule-reveal',
		null,
		array(
			'collection' => $collections['kids-capsule'],
			'products'   => $kids_cast,
		)
	);
	?>

	<section class="sr-house-heir-product" aria-labelledby="sr-house-heir-product-title">
		<header class="sr-house-section-head">
			<p><?php esc_html_e( 'Chapter 04 · The Heir', 'skyyrose-flagship-2' ); ?></p>
			<h2 id="sr-house-heir-product-title"><?php esc_html_e( 'Her first uniform.', 'skyyrose-flagship-2' ); ?></h2>
		</header>
		<div class="sr2-products sr-house-heir-product__grid">
			<?php if ( ! empty( $kids_cast['kids-001'] ) ) : ?><?php skyyrose2_render_product_loop_card( $kids_cast['kids-001'], 0 ); ?><?php endif; ?>
			<?php if ( ! empty( $kids_cast['kids-002'] ) ) : ?><?php skyyrose2_render_product_loop_card( $kids_cast['kids-002'], 1 ); ?><?php endif; ?>
		</div>
	</section>

	<?php if ( $featured_product ) : ?>
		<?php
		$featured_image_id = $featured_product->get_image_id();
		$featured_gallery  = method_exists( $featured_product, 'get_gallery_image_ids' ) ? array_slice( $featured_product->get_gallery_image_ids(), 0, 2 ) : array();
		?>
		<section class="sr-house-featured" aria-labelledby="sr-house-featured-title" data-presentation="signature">
			<p class="sr-house-featured__vertical" aria-hidden="true"><?php esc_html_e( 'Signature', 'skyyrose-flagship-2' ); ?></p>
			<div class="sr-house-featured__hero">
				<?php if ( $featured_image_id ) : ?><?php echo wp_kses_post( wp_get_attachment_image( $featured_image_id, 'woocommerce_single', false, array( 'loading' => 'lazy', 'decoding' => 'async' ) ) ); ?><?php endif; ?>
			</div>
			<div class="sr-house-featured__summary">
				<p><?php esc_html_e( 'Signature · Oakland, iconic, timeless.', 'skyyrose-flagship-2' ); ?></p>
				<h2 id="sr-house-featured-title"><?php echo esc_html( $featured_product->get_name() ); ?></h2>
				<div class="sr-house-featured__price"><span><?php esc_html_e( 'Live price', 'skyyrose-flagship-2' ); ?></span><?php echo wp_kses_post( $featured_product->get_price_html() ); ?></div>
				<p class="sr-house-featured__availability"><?php echo esc_html( $featured_product->is_in_stock() ? __( 'Published and available', 'skyyrose-flagship-2' ) : __( 'Currently unavailable', 'skyyrose-flagship-2' ) ); ?></p>
				<p><?php esc_html_e( 'Choose size and confirm current fulfillment on the product page.', 'skyyrose-flagship-2' ); ?></p>
				<a class="sr-home__button sr-home__button--line" href="<?php echo esc_url( $featured_product->get_permalink() ); ?>"><?php esc_html_e( 'Enter the product scene', 'skyyrose-flagship-2' ); ?> ↗</a>
			</div>
			<div class="sr-house-featured__details">
				<?php foreach ( $featured_gallery as $gallery_id ) : ?><?php echo wp_kses_post( wp_get_attachment_image( $gallery_id, 'woocommerce_thumbnail', false, array( 'loading' => 'lazy', 'decoding' => 'async' ) ) ); ?><?php endforeach; ?>
			</div>
		</section>
	<?php endif; ?>

	<?php skyyrose2_render_black_rose_jersey_series( false ); ?>

	<section class="sr-house-confidence" aria-labelledby="sr-house-confidence-title">
		<h2 id="sr-house-confidence-title"><?php esc_html_e( 'Pre-order with confidence', 'skyyrose-flagship-2' ); ?></h2>
		<div>
			<article><span aria-hidden="true">01</span><h3><?php esc_html_e( 'Secure yours', 'skyyrose-flagship-2' ); ?></h3><p><?php esc_html_e( 'Reserve a published piece through the protected WooCommerce checkout.', 'skyyrose-flagship-2' ); ?></p></article>
			<article><span aria-hidden="true">02</span><h3><?php esc_html_e( 'Built to deliver', 'skyyrose-flagship-2' ); ?></h3><p><?php esc_html_e( 'See the current fulfillment expectation before you place the order.', 'skyyrose-flagship-2' ); ?></p></article>
			<article><span aria-hidden="true">03</span><h3><?php esc_html_e( 'Track the chapter', 'skyyrose-flagship-2' ); ?></h3><p><?php esc_html_e( 'Order updates remain attached to the order and customer account.', 'skyyrose-flagship-2' ); ?></p></article>
			<article><span aria-hidden="true">04</span><h3><?php esc_html_e( 'House support', 'skyyrose-flagship-2' ); ?></h3><p><?php esc_html_e( 'Fit, shipping, and service guidance stay available before and after checkout.', 'skyyrose-flagship-2' ); ?></p></article>
		</div>
	</section>

	<section class="sr-house-legacy" aria-labelledby="sr-house-legacy-title">
		<img src="<?php echo esc_url( skyyrose2_sot_asset_uri( 'images/about/skyy-rose-founder-hero.webp' ) ); ?>" alt="<?php esc_attr_e( 'Skyy Rose wearing an original SkyyRose look', 'skyyrose-flagship-2' ); ?>" width="726" height="1089" loading="lazy" decoding="async">
		<div>
			<p><?php esc_html_e( 'The architect and his why', 'skyyrose-flagship-2' ); ?></p>
			<h2 id="sr-house-legacy-title"><?php esc_html_e( 'A legacy in bloom.', 'skyyrose-flagship-2' ); ?></h2>
			<p><?php esc_html_e( 'SkyyRose is more than a brand—it is a promise. To my daughter. To our city. To every soul that believes in turning pain into purpose and dreams into reality.', 'skyyrose-flagship-2' ); ?></p>
			<a href="<?php echo esc_url( home_url( '/about/' ) ); ?>"><?php esc_html_e( 'Read the house story', 'skyyrose-flagship-2' ); ?> <span aria-hidden="true">→</span></a>
		</div>
	</section>
</main>
<?php get_footer(); ?>
