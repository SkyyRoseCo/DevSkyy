<?php
/**
 * About page — Mission Banner.
 *
 * Called via get_template_part( 'template-parts/about/mission', null, $args ).
 *
 * @package SkyyRose
 * @since   6.5.0
 */

defined( 'ABSPATH' ) || exit;
?>

<!-- Mission Banner -->
<section class="abt-mission" aria-label="<?php esc_attr_e( 'Our Mission', 'skyyrose' ); ?>">
	<div>
		<p class="abt-chapter__label" style="text-align:center;margin-bottom:24px">
			<?php esc_html_e( 'The Mission', 'skyyrose' ); ?>
		</p>
		<p class="abt-mission__sub rv rv-blur">
			<?php esc_html_e( 'Four Collections, A Bloodline, and the Heir to the Throne.', 'skyyrose' ); ?>
		</p>
		<a href="<?php echo esc_url( home_url( '/pre-order/' ) ); ?>" class="abt-mission__cta magnetic btn-sweep">
			<?php esc_html_e( 'Shop the Collection', 'skyyrose' ); ?>
		</a>
	</div>
</section>
