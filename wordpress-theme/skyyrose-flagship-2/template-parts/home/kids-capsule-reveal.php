<?php
/**
 * Homepage Chapter 04 — Kids Capsule Royal Procession.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

$collection     = isset( $args['collection'] ) && is_array( $args['collection'] ) ? $args['collection'] : array();
$products       = isset( $args['products'] ) && is_array( $args['products'] ) ? $args['products'] : array();
$red            = $products['kids-001'] ?? null;
$purple         = $products['kids-002'] ?? null;
$collection_url = skyyrose2_collection_url( 'kids-capsule' );
$world_url      = skyyrose2_immersive_url( 'kids-capsule' );

/**
 * Render a Woo-authoritative guardian proof block.
 *
 * @param WC_Product|null $product WooCommerce product, or null when fail-closed.
 * @param string          $sku Exact guardian SKU.
 * @param string          $role Human-readable role.
 */
$render_guardian_proof = static function ( $product, $sku, $role ) {
	$approved_front = skyyrose2_approved_card_front( $product );
	?>
	<div class="sr-kids-procession__proof" data-sku="<?php echo esc_attr( $sku ); ?>" data-product-state="<?php echo $product ? 'resolved' : 'unavailable'; ?>">
		<div class="sr-kids-procession__proof-media">
			<?php if ( $approved_front ) : ?>
				<img src="<?php echo esc_url( $approved_front['src'] ); ?>" alt="<?php echo esc_attr( $approved_front['alt'] ); ?>" width="<?php echo esc_attr( (string) $approved_front['width'] ); ?>" height="<?php echo esc_attr( (string) $approved_front['height'] ); ?>" loading="lazy" decoding="async">
			<?php elseif ( $product && $product->get_image_id() ) : ?>
				<?php
				echo wp_kses_post(
					wp_get_attachment_image(
						$product->get_image_id(),
						'woocommerce_thumbnail',
						false,
						array(
							'loading'  => 'lazy',
							'decoding' => 'async',
						)
					)
				);
				?>
			<?php else : ?>
				<span aria-hidden="true">SR</span>
			<?php endif; ?>
		</div>
		<div class="sr-kids-procession__proof-copy">
			<p><?php echo esc_html( $role ); ?> · <?php echo esc_html( strtoupper( $sku ) ); ?></p>
			<?php if ( $product ) : ?>
				<h4><a href="<?php echo esc_url( $product->get_permalink() ); ?>"><?php echo esc_html( $product->get_name() ); ?></a></h4>
				<div class="sr-kids-procession__commerce">
					<span class="sr-kids-procession__price"><span class="screen-reader-text"><?php esc_html_e( 'Current price:', 'skyyrose-flagship-2' ); ?></span><?php echo wp_kses_post( $product->get_price_html() ); ?></span>
					<span class="sr-kids-procession__availability" data-stock-state="<?php echo $product->is_in_stock() ? 'available' : 'unavailable'; ?>"><?php echo esc_html( $product->is_in_stock() ? __( 'Available', 'skyyrose-flagship-2' ) : __( 'Currently unavailable', 'skyyrose-flagship-2' ) ); ?></span>
				</div>
				<a class="sr-kids-procession__product-link" href="<?php echo esc_url( $product->get_permalink() ); ?>"><?php echo esc_html( sprintf( __( 'See the %s set', 'skyyrose-flagship-2' ), strtolower( $role ) ) ); ?> <span aria-hidden="true">↗</span></a>
			<?php else : ?>
				<h4><?php esc_html_e( 'Guardian product proof unavailable', 'skyyrose-flagship-2' ); ?></h4>
				<p class="sr-kids-procession__fallback-copy"><?php esc_html_e( 'Enter the Kids Capsule collection for currently published pieces.', 'skyyrose-flagship-2' ); ?></p>
			<?php endif; ?>
		</div>
	</div>
	<?php
};
?>
<section id="kids-capsule-reveal" class="sr-kids-procession" aria-labelledby="kids-capsule-reveal-title" data-house-royal-procession data-feature-id="kids-royal-procession-v1" data-active-chapter="invitation">
	<header class="sr-kids-procession__header">
		<div>
			<p class="sr-kids-procession__chapter-mark"><?php esc_html_e( 'Chapter 04 · Kids Capsule', 'skyyrose-flagship-2' ); ?></p>
			<h2 id="kids-capsule-reveal-title"><?php esc_html_e( 'A fourth world has been waiting.', 'skyyrose-flagship-2' ); ?></h2>
		</div>
		<p><?php esc_html_e( 'The house changes hands. Follow the procession from invitation, to guardians, to the heir already seated at the center of her story.', 'skyyrose-flagship-2' ); ?></p>
	</header>

	<div class="sr-kids-procession__viewport" data-procession-viewport role="region" aria-label="<?php esc_attr_e( 'Kids Capsule Royal Procession. Three chapters.', 'skyyrose-flagship-2' ); ?>" tabindex="0">
		<div class="sr-kids-procession__track">
			<article id="kids-procession-invitation" class="sr-kids-procession__panel sr-kids-procession__panel--invitation" data-procession-chapter="invitation" aria-labelledby="kids-procession-invitation-title">
				<div class="sr-kids-procession__scene">
					<img src="<?php echo esc_url( skyyrose2_sot_asset_uri( 'images/immersive/scene-kids-capsule-playroom.webp' ) ); ?>" alt="<?php esc_attr_e( 'Rose-gold doors opening into the Kids Capsule playroom', 'skyyrose-flagship-2' ); ?>" width="1280" height="720" loading="lazy" decoding="async">
					<span class="sr-kids-procession__scene-shade" aria-hidden="true"></span>
				</div>
				<div class="sr-kids-procession__panel-copy">
					<p>01 · <?php esc_html_e( 'The Invitation', 'skyyrose-flagship-2' ); ?></p>
					<h3 id="kids-procession-invitation-title"><?php esc_html_e( 'The doors open for her.', 'skyyrose-flagship-2' ); ?></h3>
					<p><?php esc_html_e( 'Not a smaller room. Not a borrowed story. A first world built at her scale, with enough space for every idea she has not named yet.', 'skyyrose-flagship-2' ); ?></p>
				</div>
			</article>

			<article id="kids-procession-guardians" class="sr-kids-procession__panel sr-kids-procession__panel--guardians" data-procession-chapter="guardians" aria-labelledby="kids-procession-guardians-title">
				<div class="sr-kids-procession__guardians" aria-label="<?php esc_attr_e( 'The red and purple Kids Capsule guardians', 'skyyrose-flagship-2' ); ?>">
					<figure class="sr-kids-procession__guardian sr-kids-procession__guardian--red">
						<img src="<?php echo esc_url( skyyrose2_sot_asset_uri( 'images/home/on-model/kids-capsule-mascot-red-guard.webp' ) ); ?>" alt="<?php esc_attr_e( 'Skyy mascot wearing the red, black, and white Kids Capsule colorblock hoodie and jogger set in Oakland', 'skyyrose-flagship-2' ); ?>" width="752" height="1344" loading="lazy" decoding="async">
						<figcaption><?php esc_html_e( 'Red Guard · KIDS-001', 'skyyrose-flagship-2' ); ?></figcaption>
					</figure>
					<figure class="sr-kids-procession__guardian sr-kids-procession__guardian--purple">
						<img src="<?php echo esc_url( skyyrose2_sot_asset_uri( 'images/home/on-model/kids-capsule-mascot-purple-guard.webp' ) ); ?>" alt="<?php esc_attr_e( 'Skyy mascot wearing the purple, lavender, and black Kids Capsule colorblock hoodie and jogger set in Oakland', 'skyyrose-flagship-2' ); ?>" width="752" height="1344" loading="lazy" decoding="async">
						<figcaption><?php esc_html_e( 'Purple Guard · KIDS-002', 'skyyrose-flagship-2' ); ?></figcaption>
					</figure>
				</div>
				<div class="sr-kids-procession__panel-copy sr-kids-procession__panel-copy--guardians">
					<p>02 · <?php esc_html_e( 'The Guardians', 'skyyrose-flagship-2' ); ?></p>
					<h3 id="kids-procession-guardians-title"><?php esc_html_e( 'Color becomes the uniform of imagination.', 'skyyrose-flagship-2' ); ?></h3>
					<p><?php esc_html_e( 'Red arrives with energy. Purple arrives with possibility. Both sets protect room to move, play, and decide who they want to be next.', 'skyyrose-flagship-2' ); ?></p>
					<div class="sr-kids-procession__proofs">
						<?php $render_guardian_proof( $red, 'kids-001', __( 'Red Guard', 'skyyrose-flagship-2' ) ); ?>
						<?php $render_guardian_proof( $purple, 'kids-002', __( 'Purple Guard', 'skyyrose-flagship-2' ) ); ?>
					</div>
				</div>
			</article>

			<article id="kids-procession-heir" class="sr-kids-procession__panel sr-kids-procession__panel--heir" data-procession-chapter="heir" aria-labelledby="kids-procession-heir-title">
				<div class="sr-kids-procession__scene">
					<img src="<?php echo esc_url( skyyrose2_sot_asset_uri( 'images/hero/kids-capsule-heir-throne-v3.webp' ) ); ?>" alt="<?php esc_attr_e( 'The full-color SkyyRose heir seated front and center on her black-and-gold throne monument', 'skyyrose-flagship-2' ); ?>" width="1672" height="941" loading="lazy" decoding="async">
					<span class="sr-kids-procession__scene-shade" aria-hidden="true"></span>
				</div>
				<div class="sr-kids-procession__panel-copy">
					<p>03 · <?php esc_html_e( 'The Heir', 'skyyrose-flagship-2' ); ?></p>
					<h3 id="kids-procession-heir-title"><?php echo esc_html( $collection['headline'] ?? __( 'The throne is already hers.', 'skyyrose-flagship-2' ) ); ?></h3>
					<p><?php echo esc_html( $collection['manifesto'] ?? __( 'The next chapter belongs to the imagination brave enough to write it.', 'skyyrose-flagship-2' ) ); ?></p>
					<a class="sr-kids-procession__world-link" href="<?php echo esc_url( $world_url ); ?>"><?php esc_html_e( 'Enter her world', 'skyyrose-flagship-2' ); ?> <span aria-hidden="true">↗</span></a>
				</div>
			</article>
		</div>
	</div>

	<footer class="sr-kids-procession__controls" aria-label="<?php esc_attr_e( 'Royal Procession controls', 'skyyrose-flagship-2' ); ?>">
		<button type="button" data-procession-previous disabled><span aria-hidden="true">←</span> <?php esc_html_e( 'Previous chapter', 'skyyrose-flagship-2' ); ?></button>
		<p aria-live="polite" aria-atomic="true"><span data-procession-current>1</span> / 3 · <span data-procession-label><?php esc_html_e( 'The Invitation', 'skyyrose-flagship-2' ); ?></span></p>
		<button type="button" data-procession-next><?php esc_html_e( 'Next chapter', 'skyyrose-flagship-2' ); ?> <span aria-hidden="true">→</span></button>
	</footer>

	<p class="sr2-actions sr-kids-procession__collection-cta">
		<a class="sr-kids-procession__world-link" href="<?php echo esc_url( $collection_url ); ?>"><?php esc_html_e( 'Shop the full Kids Capsule collection', 'skyyrose-flagship-2' ); ?> <span aria-hidden="true">↗</span></a>
		<a class="sr-kids-procession__world-link" href="<?php echo esc_url( $world_url ); ?>"><?php esc_html_e( 'Enter the Kids world', 'skyyrose-flagship-2' ); ?> <span aria-hidden="true">→</span></a>
	</p>
</section>
