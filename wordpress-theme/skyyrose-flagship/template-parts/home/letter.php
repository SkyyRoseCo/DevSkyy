<?php
/**
 * Homepage Act VII — the letter (Kids Capsule keepsake board).
 *
 * Kids Capsule's emotional entry; the rooms corridor is its commercial one.
 * A keepsake board rather than a sealed envelope: several artefacts on a
 * table, asymmetric and rotated. The note is legible on arrival — it is never
 * a payoff hidden behind an interaction — and the affordance is turning the
 * photograph over to read what is written on its back.
 *
 * The rigged child character walks on the board as a supporting visual. It is
 * NOT the site-wide host mascot (assets/js/mascot.js), and this is the only
 * 3D mount on the page — one WebGL context, one section, by design.
 *
 * The keepsake photograph resolves through the SOT image helper (kids-001
 * front, pixel-verified against the catalog row) — never a hardcoded uploads
 * path and never a stand-in frame from another shoot.
 *
 * @package SkyyRose
 * @since   1.13.0
 */

defined( 'ABSPATH' ) || exit;

$hp_kc_link = skyyrose_home_collection_url( 'kids-capsule' );
$hp_kc_shot = function_exists( 'skyyrose_sot_product_image_uri' )
	? skyyrose_sot_product_image_uri( 'kids-001', 'front' )
	: '';
$hp_kc_set  = ( '' !== $hp_kc_shot && function_exists( 'skyyrose_photon_srcset' ) )
	? skyyrose_photon_srcset( $hp_kc_shot, array( 320, 480, 768 ) )
	: '';
$hp_models  = SKYYROSE_ASSETS_URI . '/models';
?>
<section class="hp-letter" id="kids-capsule" data-collection="kids-capsule" aria-labelledby="hp-letter-t">
	<div class="hp-letter__inner">
		<header class="hp-letter__head">
			<p class="hp-letter__eyebrow"><?php esc_html_e( 'Capsule · IV · Heir Apparent', 'skyyrose' ); ?></p>
			<h2 class="hp-letter__title" id="hp-letter-t"><?php esc_html_e( 'The Kids Capsule', 'skyyrose' ); ?></h2>
		</header>

		<div class="hp-letter__board">

			<article class="hp-letter__obj hp-letter__note hp-paper">
				<span class="hp-letter__wax" aria-hidden="true">S</span>
				<p class="hp-letter__chapter"><?php esc_html_e( 'Chapter IV', 'skyyrose' ); ?></p>
				<p class="hp-letter__script"><?php esc_html_e( 'Dear future,', 'skyyrose' ); ?></p>
				<p class="hp-letter__line"><?php esc_html_e( 'You were born into the rose. Wear it lightly.', 'skyyrose' ); ?></p>
				<p class="hp-letter__sig"><?php esc_html_e( '— S.', 'skyyrose' ); ?></p>
			</article>

			<div class="hp-letter__obj hp-letter__photo">
				<span class="hp-letter__tape" aria-hidden="true"></span>
				<button class="hp-letter__flip" type="button" data-flip aria-pressed="false">
					<span class="hp-letter__face hp-paper">
						<span class="hp-letter__shot">
							<?php if ( '' !== $hp_kc_shot ) : ?>
								<img src="<?php echo esc_url( $hp_kc_shot ); ?>"
									<?php if ( '' !== $hp_kc_set ) : ?>
										srcset="<?php echo esc_attr( $hp_kc_set ); ?>"
										sizes="(max-width: 860px) 340px, 30vw"
									<?php endif; ?>
									alt="<?php esc_attr_e( 'Kids Capsule colorblock hoodie set worn on model', 'skyyrose' ); ?>"
									width="1024"
									height="1536"
									loading="lazy"
									decoding="async">
							<?php endif; ?>
						</span>
						<span class="hp-letter__caption"><?php esc_html_e( 'Born In The Town', 'skyyrose' ); ?></span>
					</span>
					<span class="hp-letter__face hp-letter__face--back hp-paper">
						<span class="hp-letter__hand">
							<?php
							echo wp_kses(
								__( 'A father’s promise.<br>A daughter’s name.', 'skyyrose' ),
								array( 'br' => array() )
							);
							?>
						</span>
						<span class="hp-letter__hand-sub"><?php esc_html_e( 'Oakland · Est. 2020', 'skyyrose' ); ?></span>
					</span>
				</button>
				<p class="hp-letter__turn" aria-hidden="true"><?php esc_html_e( 'turn it over', 'skyyrose' ); ?></p>
			</div>

			<?php
			/*
			 * The 3D character. Decorative: the section's meaning is carried by
			 * the note, the photograph and the CTA, all of which are readable
			 * without WebGL. kc-mascot.js hides the canvas outright when WebGL
			 * or the loader is unavailable — there is no static child-character
			 * still in the theme yet to reveal in its place (flagged gap), so
			 * the board simply closes up around the empty cell.
			 */
			?>
			<div class="hp-letter__mascot">
				<canvas id="skyy-kc-canvas"
					class="hp-kc-mascot"
					width="240"
					height="300"
					role="img"
					aria-label="<?php esc_attr_e( 'Kids Capsule character walking', 'skyyrose' ); ?>"
					data-model-desktop="<?php echo esc_url( $hp_models . '/skyy-child.glb?ver=' . SKYYROSE_VERSION ); ?>"
					data-model-mobile="<?php echo esc_url( $hp_models . '/skyy-child-mobile.glb?ver=' . SKYYROSE_VERSION ); ?>"></canvas>
				<p class="hp-letter__mascot-cap"><?php esc_html_e( 'Heir Apparent', 'skyyrose' ); ?></p>
			</div>

			<div class="hp-letter__obj hp-letter__stamp hp-paper">
				<img src="<?php echo esc_url( SKYYROSE_ASSETS_URI . '/branding/skyyrose-rose-icon.webp' ); ?>"
					alt=""
					aria-hidden="true"
					width="110"
					height="110"
					loading="lazy"
					decoding="async">
				<span class="hp-letter__stamp-label"><?php esc_html_e( 'Capsule IV', 'skyyrose' ); ?></span>
			</div>
		</div>

		<a class="hp-letter__cta" href="<?php echo esc_url( $hp_kc_link ); ?>">
			<?php esc_html_e( 'The Kids Capsule', 'skyyrose' ); ?> <span aria-hidden="true">→</span>
		</a>
	</div>
</section>
