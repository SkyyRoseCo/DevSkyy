<?php
/**
 * Collection-aware single product experience.
 *
 * Gallery left, buy column right, native tabs and related pieces below, then
 * one closing chapter for the piece's collection. The accent follows
 * data-collection on the page root.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

get_header();

while ( have_posts() ) :
	the_post();
	$product             = wc_get_product( get_the_ID() );
	$collections         = skyyrose2_collections();
	$presentation        = 'house';
	$presentation_name   = __( 'SkyyRose', 'skyyrose-flagship-2' );
	$presentation_record = $product ? skyyrose2_product_presentation( $product ) : array();
	$is_jersey           = 'jersey-series' === ( $presentation_record['presentation'] ?? '' );
	$active_slug         = isset( $presentation_record['collection'] ) ? sanitize_title( $presentation_record['collection'] ) : '';

	if ( $is_jersey ) {
		$presentation      = 'jersey-series';
		$presentation_name = __( 'Jersey Series', 'skyyrose-flagship-2' );
	} elseif ( $active_slug && isset( $collections[ $active_slug ] ) ) {
		$presentation      = $active_slug;
		$presentation_name = $collections[ $active_slug ]['name'];
	}

	$active_collection = $active_slug && isset( $collections[ $active_slug ] ) ? $collections[ $active_slug ] : null;
	$product_name      = $product ? $product->get_name() : get_the_title();
	?>
	<main id="primary" tabindex="-1" class="sr2-product-page sr2-product-page--editorial" data-presentation="<?php echo esc_attr( $presentation ); ?>"<?php echo $active_collection ? ' data-collection="' . esc_attr( $active_slug ) . '"' : ''; ?>>
		<nav class="sr2-product-crumb" aria-label="<?php esc_attr_e( 'Breadcrumb', 'skyyrose-flagship-2' ); ?>">
			<a href="<?php echo esc_url( wc_get_page_permalink( 'shop' ) ); ?>"><?php esc_html_e( 'Shop', 'skyyrose-flagship-2' ); ?></a><span aria-hidden="true">/</span>
			<?php
			if ( $active_collection ) :
				?>
				<a href="<?php echo esc_url( skyyrose2_collection_url( $active_slug ) ); ?>"><?php echo esc_html( $active_collection['name'] ); ?></a><span aria-hidden="true">/</span>
				<?php
elseif ( $is_jersey ) :
	?>
				<span><?php echo esc_html( $presentation_name ); ?></span><span aria-hidden="true">/</span><?php endif; ?>
			<span aria-current="page"><?php echo esc_html( $product_name ); ?></span>
		</nav>
		<section class="sr2-product-shell sr2-product-shell--editorial" aria-label="<?php echo esc_attr( sprintf( __( '%s purchase details', 'skyyrose-flagship-2' ), $product_name ) ); ?>">
			<?php
			get_template_part(
				'template-parts/commerce/product-hero',
				null,
				array(
					'product'           => $product,
					'presentation'      => $presentation,
					'presentation_name' => $presentation_name,
					'collection'        => $active_collection ? $active_slug : '',
					'collection_data'   => $active_collection,
				)
			);
			?>
		</section>
		<?php if ( $active_collection ) : ?>
			<?php $world_number = (int) array_search( $active_slug, array_keys( $collections ), true ) + 1; ?>
			<?php $world_presentation = skyyrose2_collection_presentation( $active_slug ); ?>
			<section class="sr2-chapter sr2-product-world sr2-product-world--editorial" data-collection="<?php echo esc_attr( $active_slug ); ?>" aria-labelledby="sr2-product-world-title">
				<figure class="sr2-chapter__scene" style="--sr2-focal-desktop: <?php echo esc_attr( $world_presentation['focal'] ?? '50% 50%' ); ?>; --sr2-focal-mobile: <?php echo esc_attr( $world_presentation['focal_mobile'] ?? $world_presentation['focal'] ?? '50% 50%' ); ?>;">
					<picture>
						<?php
						if ( ! empty( $active_collection['hero_mobile'] ) ) :
							?>
							<source media="(max-width: 47.99em)" srcset="<?php echo esc_url( skyyrose2_sot_asset_uri( $active_collection['hero_mobile'] ) ); ?>"><?php endif; ?>
						<?php
						if ( ! empty( $active_collection['hero_tablet'] ) ) :
							?>
							<source media="(max-width: 74.99em)" srcset="<?php echo esc_url( skyyrose2_sot_asset_uri( $active_collection['hero_tablet'] ) ); ?>"><?php endif; ?>
						<img src="<?php echo esc_url( skyyrose2_sot_asset_uri( $active_collection['hero'] ) ); ?>" alt="" width="1440" height="810" loading="lazy" decoding="async">
					</picture>
				</figure>
				<div class="sr2-chapter__band">
					<div class="sr2-chapter__copy">
						<p class="sr2-chapter__index sr2-eyebrow sr2-eyebrow--engraved"><?php echo esc_html( sprintf( '%02d / %s', $world_number, $active_collection['name'] ) ); ?></p>
						<h2 id="sr2-product-world-title" class="sr2-title-chapter"><?php echo esc_html( $active_collection['headline'] ); ?></h2>
						<p class="sr2-lede"><?php echo esc_html( $active_collection['manifesto'] ); ?></p>
						<a class="sr2-editorial-link" href="<?php echo esc_url( skyyrose2_collection_url( $active_slug ) ); ?>"><?php /* translators: %s: collection name, e.g. Black Rose. */ echo esc_html( sprintf( __( 'Enter %s', 'skyyrose-flagship-2' ), $active_collection['name'] ) ); ?><span aria-hidden="true">→</span></a>
					</div>
				</div>
			</section>
		<?php endif; ?>
	</main>
	<?php
endwhile;

get_footer();
