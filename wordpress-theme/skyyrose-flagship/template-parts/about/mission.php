<?php
/**
 * About page — Mission Banner.
 *
 * Called via get_template_part( 'template-parts/about/mission', null, $args ).
 *
 * @param array $args {
 *     @type array $allowed_inline wp_kses whitelist for em/strong/br.
 * }
 *
 * @package SkyyRose
 * @since   6.5.0
 */

defined( 'ABSPATH' ) || exit;

$allowed_inline = $args['allowed_inline'] ?? array();
?>

<!-- Mission Banner -->
<section class="abt-mission" aria-label="<?php esc_attr_e( 'Our Mission', 'skyyrose' ); ?>">
	<div>
		<p class="abt-chapter__label" style="text-align:center;margin-bottom:24px">
			<?php esc_html_e( 'The Mission', 'skyyrose' ); ?>
		</p>
		<h2 class="abt-mission__tagline rv rv-clip-up">
			<?php echo wp_kses( __( '', 'skyyrose' ), $allowed_inline ); ?>
		</h2>
		<p class="abt-mission__sub rv rv-blur">
			<?php esc_html_e( 'Four Collections, A Bloodline, and the Heir to the Throne.', 'skyyrose' ); ?>
		</p>
		<a href="<?php echo esc_url( home_url( '/pre-order/' ) ); ?>" class="abt-mission__cta magnetic btn-sweep">
			<?php esc_html_e( 'Shop the Collection', 'skyyrose' ); ?>
		</a>
	</div>
</section>
