<?php
/**
 * SkyyRose Single Product Page — Impeccable Refinement
 *
 * Technical Garment Lock + Techflat-First Visuals.
 *
 * Fully custom PDP — intentionally replaces WooCommerce core's single-product
 * structure (no woocommerce_single_product_summary hook scaffold). @version is
 * tracked against core single-product.php (last core change: 1.6.4) so the
 * WooCommerce status scanner does not flag this deliberate override as outdated.
 *
 * @package SkyyRose
 * @version 1.6.4
 */

defined( 'ABSPATH' ) || exit;

get_header( 'shop' );

do_action( 'woocommerce_before_main_content' );

while ( have_posts() ) :
	the_post();

	global $product;
	if ( ! is_a( $product, 'WC_Product' ) ) {
		continue;
	}

	$collection = skyyrose_get_product_collection();
	$config     = skyyrose_get_collection( $collection );
	$meta       = skyyrose_get_product_meta();
	$sku        = $product->get_sku();

	// skyyrose_get_product_meta() backfills 'made_in' to 'USA' when the
	// postmeta is unset, so $meta['made_in'] is never empty. Check the raw
	// postmeta directly so the spec row only renders for products that
	// actually have _skyyrose_made_in set.
	$has_made_in = '' !== get_post_meta( $product->get_id(), '_skyyrose_made_in', true );

	// Technical Garment Lock logic.
	$catalog_entry = function_exists( 'skyyrose_get_product' ) ? skyyrose_get_product( $sku ) : null;

	// Editorial PDP: if dossier data exists, render 7-chapter scroll layout.
	$dossier       = function_exists( 'skyyrose_get_product_dossier' ) ? skyyrose_get_product_dossier( $sku ) : null;
	$has_editorial = $dossier && ! empty( $dossier['has_editorial_content'] );

	if ( $has_editorial ) :
		get_template_part(
			'template-parts/product-detail-editorial',
			null,
			array(
				'product'       => $product,
				'catalog_entry' => $catalog_entry,
				'dossier'       => $dossier,
				'collection'    => $collection,
				'config'        => $config,
				'meta'          => $meta,
			)
		);
	else :
		$techflat_url = $catalog_entry ? skyyrose_product_image_uri( $catalog_entry['image'] ?? '' ) : '';
		$main_image   = wp_get_attachment_url( absint( $product->get_image_id() ) );
		$price_html   = $product->get_price_html();
		$stock_status = $product->get_stock_status();
		$description  = ! empty( $catalog_entry['description'] )
			? $catalog_entry['description']
			: wp_strip_all_tags( $product->get_short_description() );
		?>

		<main id="product-<?php the_ID(); ?>" <?php wc_product_class( 'sr-product', $product ); ?> data-collection="<?php echo esc_attr( $collection ); ?>">

			<section class="sr-hero">
				<div class="sr-container sr-hero-grid">

					<?php
					// Gallery + info columns are the first mobile viewport and the
					// gallery image is the LCP element — no reveal classes here:
					// the hidden resting state stalls LCP behind the deferred JS
					// queue (the 24.9s render-delay bug, fix-log Wave 1). Wave 5.
					?>
					<!-- Gallery Column -->
					<div class="sr-gallery">
						<div class="sr-gallery-main">
							<?php
							$hero_img = $techflat_url ? $techflat_url : $main_image;
							if ( $hero_img ) :
								?>
								<img
									src="<?php echo esc_url( $hero_img ); ?>"
									class="sr-gallery-img"
									id="srMainImg"
									alt="<?php echo esc_attr( get_the_title() ); ?>"
									width="640"
									height="800"
									loading="eager"
									decoding="async"
									fetchpriority="high">
							<?php endif; ?>
						</div>

						<div class="sr-gallery-thumbs">
							<?php if ( $techflat_url ) : ?>
								<button type="button" class="sr-thumb sr-thumb-active" data-img="<?php echo esc_url( $techflat_url ); ?>">
									<img src="<?php echo esc_url( $techflat_url ); ?>" alt="<?php esc_attr_e( 'Technical Blueprint', 'skyyrose' ); ?>">
								</button>
							<?php endif; ?>
							<?php if ( $main_image ) : ?>
								<button type="button" class="sr-thumb <?php echo $techflat_url ? '' : 'sr-thumb-active'; ?>" data-img="<?php echo esc_url( $main_image ); ?>">
									<img src="<?php echo esc_url( $main_image ); ?>" alt="<?php esc_attr_e( 'Model View', 'skyyrose' ); ?>">
								</button>
							<?php endif; ?>
						</div>

						<?php
						// "View in 3D" sits with the photos (founder decision, WS3). Prints
						// only when _product_3d_model holds a valid same-origin GLB; the
						// gallery itself is untouched.
						skyyrose_woocommerce_3d_model_button();
						?>
					</div>

					<!-- Info Column -->
					<div class="sr-info">
						<div class="sr-info-inner">
							<p class="sr-info-collection"><?php echo esc_html( $config['label'] ); ?> COLLECTION</p>
							<h1 class="sr-info-name"><?php the_title(); ?></h1>
							<div class="sr-info-price"><?php echo wp_kses_post( $price_html ); ?></div>

							<?php if ( $description ) : ?>
								<p class="sr-info-desc"><?php echo esc_html( $description ); ?></p>
							<?php endif; ?>

							<div class="sr-info-specs">
								<div class="sr-spec">
									<span class="sr-spec-label"><?php esc_html_e( 'GARMENT TYPE', 'skyyrose' ); ?></span>
									<span class="sr-spec-value"><?php echo esc_html( strtoupper( $catalog_entry['garment_type_lock'] ?? 'GARMENT' ) ); ?></span>
								</div>
								<div class="sr-spec">
									<span class="sr-spec-label"><?php esc_html_e( 'SKU', 'skyyrose' ); ?></span>
									<span class="sr-spec-value"><?php echo esc_html( $sku ); ?></span>
								</div>
								<?php if ( ! empty( $meta['material'] ) ) : ?>
								<div class="sr-spec">
									<span class="sr-spec-label"><?php esc_html_e( 'MATERIAL', 'skyyrose' ); ?></span>
									<span class="sr-spec-value"><?php echo esc_html( $meta['material'] ); ?></span>
								</div>
								<?php endif; ?>
								<?php if ( ! empty( $meta['fit'] ) ) : ?>
								<div class="sr-spec">
									<span class="sr-spec-label"><?php esc_html_e( 'FIT', 'skyyrose' ); ?></span>
									<span class="sr-spec-value"><?php echo esc_html( $meta['fit'] ); ?></span>
								</div>
								<?php endif; ?>
								<?php if ( $has_made_in ) : ?>
								<div class="sr-spec">
									<span class="sr-spec-label"><?php esc_html_e( 'MADE IN', 'skyyrose' ); ?></span>
									<span class="sr-spec-value"><?php echo esc_html( strtoupper( $meta['made_in'] ) ); ?></span>
								</div>
								<?php endif; ?>
							</div>

							<button type="button" class="sr-size-guide-link sr-info-size-guide" data-open-size-guide>
								<?php esc_html_e( 'Size Guide', 'skyyrose' ); ?>
							</button>

							<div class="sr-atc-wrap magnetic btn-sweep">
								<?php woocommerce_template_single_add_to_cart(); ?>
							</div>

							<div class="sr-stock">
								<span class="sr-stock-dot"></span>
								<?php
								echo 'instock' === $stock_status
									? esc_html__( 'In Stock — Ready to Ship', 'skyyrose' )
									: esc_html__( 'Pre-Order', 'skyyrose' );
								?>
							</div>
							<?php
							if ( function_exists( 'skyyrose_render_fit_block' ) ) {
								skyyrose_render_fit_block( $product->get_id() );
							}
							?>
						</div>
					</div>
				</div>
			</section>
		</main>
	<?php endif; ?>
	<?php
endwhile;

get_footer( 'shop' );
