<?php
/**
 * Collection-aware single product experience.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

get_header();

while ( have_posts() ) :
	the_post();
	$product      = wc_get_product( get_the_ID() );
	$collections = skyyrose2_collections();
	$active_slug  = '';
	$presentation = 'house';
	$presentation_name = __( 'SkyyRose', 'skyyrose-flagship-2' );
	$presentation_record = $product ? skyyrose2_product_presentation( $product ) : array();
	$is_jersey     = 'jersey-series' === ( $presentation_record['presentation'] ?? '' );

	$active_slug = isset( $presentation_record['collection'] ) ? sanitize_title( $presentation_record['collection'] ) : '';

	if ( $is_jersey ) {
		$presentation      = 'jersey-series';
		$presentation_name = __( 'Jersey Series', 'skyyrose-flagship-2' );
	} elseif ( $active_slug && isset( $collections[ $active_slug ] ) ) {
		$presentation      = $active_slug;
		$presentation_name = $collections[ $active_slug ]['name'];
	}

	$active_collection = $active_slug && isset( $collections[ $active_slug ] ) ? $collections[ $active_slug ] : null;
	?>
	<main id="primary" class="sr2-product-page sr2-product-page--editorial" data-presentation="<?php echo esc_attr( $presentation ); ?>"<?php echo $active_slug ? ' data-collection="' . esc_attr( $active_slug ) . '"' : ''; ?>>
		<nav class="sr2-product-crumb" aria-label="<?php esc_attr_e( 'Breadcrumb', 'skyyrose-flagship-2' ); ?>">
			<a href="<?php echo esc_url( wc_get_page_permalink( 'shop' ) ); ?>"><?php esc_html_e( 'Shop', 'skyyrose-flagship-2' ); ?></a><span aria-hidden="true">/</span>
			<?php if ( $active_collection ) : ?><a href="<?php echo esc_url( skyyrose2_collection_url( $active_slug ) ); ?>"><?php echo esc_html( $active_collection['name'] ); ?></a><span aria-hidden="true">/</span><?php elseif ( $is_jersey ) : ?><span><?php echo esc_html( $presentation_name ); ?></span><span aria-hidden="true">/</span><?php endif; ?>
			<span aria-current="page"><?php echo esc_html( $product ? $product->get_name() : get_the_title() ); ?></span>
		</nav>
		<section class="sr2-product-shell sr2-product-shell--editorial" aria-label="<?php echo esc_attr( sprintf( __( '%s purchase details', 'skyyrose-flagship-2' ), $product ? $product->get_name() : get_the_title() ) ); ?>">
			<?php
			get_template_part(
				'template-parts/commerce/product-hero',
				null,
				array(
					'product'           => $product,
					'presentation'      => $presentation,
					'presentation_name' => $presentation_name,
					'collection_data'   => $active_collection,
				)
			);
			?>
		</section>
		<?php if ( $active_collection ) : ?>
			<aside class="sr2-product-world sr2-product-world--editorial" aria-label="<?php echo esc_attr( sprintf( __( 'About %s', 'skyyrose-flagship-2' ), $active_collection['name'] ) ); ?>">
				<div><p class="sr2-eyebrow"><?php echo esc_html( $active_collection['kicker'] ); ?></p><h2><?php echo esc_html( $active_collection['headline'] ); ?></h2><p><?php echo esc_html( $active_collection['manifesto'] ); ?></p><a class="sr2-text-link" href="<?php echo esc_url( skyyrose2_collection_url( $active_slug ) ); ?>"><?php esc_html_e( 'Enter full collection', 'skyyrose-flagship-2' ); ?> ↗</a></div>
				<picture>
					<?php if ( ! empty( $active_collection['hero_mobile'] ) ) : ?><source media="(max-width: 48rem)" srcset="<?php echo esc_url( skyyrose2_sot_asset_uri( $active_collection['hero_mobile'] ) ); ?>"><?php endif; ?>
					<img src="<?php echo esc_url( skyyrose2_sot_asset_uri( $active_collection['hero_tablet'] ?? $active_collection['hero'] ) ); ?>" alt="" width="1024" height="576" loading="lazy" decoding="async">
				</picture>
			</aside>
		<?php endif; ?>
	</main>
	<?php
endwhile;

get_footer();
