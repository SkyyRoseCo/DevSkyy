<?php
defined( 'ABSPATH' ) || exit;
/**
 * The template for displaying the footer
 *
 * 5-column grid footer with brand column, navigation columns,
 * newsletter signup bar, and copyright.
 *
 * @package SkyyRose
 * @since 2.0.0
 */

?>

	</div><!-- #content -->

	<footer id="colophon" class="site-footer" role="contentinfo">

		<?php get_template_part( 'template-parts/footer-cro' ); ?>

		<!-- Newsletter Signup Bar -->
		<div class="footer-newsletter rv-clip-up">
			<div class="footer-newsletter__container">
				<div class="footer-newsletter__content">
					<h3 class="footer-newsletter__title rv-split-word">
						<?php esc_html_e( 'Join the Inner Circle', 'skyyrose' ); ?>
					</h3>
					<p class="footer-newsletter__text">
						<?php esc_html_e( 'Exclusive drops, early access, and luxury delivered to your inbox.', 'skyyrose' ); ?>
					</p>
				</div>
				<form class="footer-newsletter__form" action="<?php echo esc_url( admin_url( 'admin-ajax.php' ) ); ?>" method="post" aria-label="<?php esc_attr_e( 'Newsletter signup', 'skyyrose' ); ?>">
					<?php wp_nonce_field( 'skyyrose_newsletter', 'skyyrose_newsletter_nonce' ); ?>
					<input type="hidden" name="action" value="skyyrose_newsletter_subscribe">
					<div class="footer-newsletter__input-group">
						<label for="footer-newsletter-email" class="screen-reader-text">
							<?php esc_html_e( 'Email address', 'skyyrose' ); ?>
						</label>
						<input
							type="email"
							id="footer-newsletter-email"
							name="email"
							class="footer-newsletter__input"
							placeholder="<?php esc_attr_e( 'Enter your email', 'skyyrose' ); ?>"
							required
							autocomplete="email"
						>
						<button type="submit" class="footer-newsletter__submit btn-sweep btn-press" name="skyyrose_newsletter_submit">
							<?php esc_html_e( 'Subscribe', 'skyyrose' ); ?>
							<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">
								<path d="M5 12h14"/>
								<path d="m12 5 7 7-7 7"/>
							</svg>
						</button>
					</div>
					<p class="footer-newsletter__status" role="status" aria-live="polite"></p>
				</form>
			</div>
		</div>

		<!-- 5-Column Footer Grid -->
		<div class="footer-grid rv-clip-up">
			<div class="footer-grid__container stagger-grid">

				<!-- Column 1: Brand (2fr) -->
				<div class="footer-grid__col footer-grid__col--brand">
					<a href="<?php echo esc_url( home_url( '/' ) ); ?>" class="footer-brand__logo-link" rel="home">
						<img
							src="<?php echo esc_url( SKYYROSE_ASSETS_URI . '/branding/skyyrose-monogram-footer.webp?v=' . SKYYROSE_VERSION ); ?>"
							alt="<?php esc_attr_e( 'SkyyRose', 'skyyrose' ); ?>"
							class="footer-brand__monogram"
							width="60"
							height="60"
							loading="lazy"
						>
						<span class="footer-brand__text navbar__gradient-text"><?php esc_html_e( 'SKYY ROSE', 'skyyrose' ); ?></span>
					</a>
					<p class="footer-brand__description">
						<?php esc_html_e( 'Oakland luxury streetwear. Gender-neutral, limited edition pieces — built by a father, named after a daughter.', 'skyyrose' ); ?>
					</p>
					<nav class="footer-brand__social" aria-label="<?php esc_attr_e( 'Social Media Links', 'skyyrose' ); ?>">
						<?php
						$social_icons = array(
							'instagram' => '<path d="M7.8 2h8.4C19.4 2 22 4.6 22 7.8v8.4a5.8 5.8 0 0 1-5.8 5.8H7.8C4.6 22 2 19.4 2 16.2V7.8A5.8 5.8 0 0 1 7.8 2Z"/><circle cx="12" cy="12" r="3.5"/><circle cx="17.5" cy="6.5" r="0.5" fill="currentColor"/>',
							'tiktok'    => '<path d="M9 12a4 4 0 1 0 4 4V4a5 5 0 0 0 5 5"/>',
							'twitter'   => '<path d="M4 4l11.733 16h4.267l-11.733 -16z"/><path d="M4 20l6.768 -6.768m2.46 -2.46l6.772 -6.772"/>',
							'facebook'  => '<path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>',
						);
						$social_links = skyyrose_get_social_links();

						foreach ( $social_icons as $platform => $icon ) :
							if ( ! isset( $social_links[ $platform ] ) ) {
								continue;
							}
							$data = $social_links[ $platform ];
							?>
							<a
								href="<?php echo esc_url( $data['url'] ); ?>"
								class="footer-brand__social-link footer-brand__social-link--<?php echo esc_attr( $platform ); ?>"
								aria-label="<?php echo esc_attr( $data['label'] ); ?>"
								target="_blank"
								rel="noopener noreferrer"
							>
								<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">
									<?php
									echo wp_kses(
										$icon,
										array(
											'path'     => array(
												'd'    => true,
												'fill' => true,
											),
											'circle'   => array(
												'cx'   => true,
												'cy'   => true,
												'r'    => true,
												'fill' => true,
											),
											'polyline' => array(
												'points' => true,
											),
											'line'     => array(
												'x1' => true,
												'y1' => true,
												'x2' => true,
												'y2' => true,
											),
											'rect'     => array(
												'x'      => true,
												'y'      => true,
												'width'  => true,
												'height' => true,
												'fill'   => true,
											),
										)
									);
									?>
								</svg>
							</a>
						<?php endforeach; ?>
					</nav>
				</div>

				<!-- Column 2: Shop (1fr) -->
				<div class="footer-grid__col footer-grid__col--shop">
					<h4 class="footer-grid__heading"><?php esc_html_e( 'Shop', 'skyyrose' ); ?></h4>
					<ul class="footer-grid__list">
						<?php
						// Collections are derived from the canonical catalog CSV so
						// adding/removing a collection automatically flows to the footer.
						$footer_collections = array();
						if ( function_exists( 'skyyrose_get_product_catalog' ) ) {
							$footer_catalog = skyyrose_get_product_catalog();
							foreach ( $footer_catalog as $footer_product ) {
								$footer_slug = $footer_product['collection'] ?? '';
								if ( $footer_slug && ! isset( $footer_collections[ $footer_slug ] ) ) {
									$footer_collections[ $footer_slug ] = ucwords( str_replace( '-', ' ', $footer_slug ) );
								}
							}
						}
						foreach ( $footer_collections as $footer_slug => $footer_label ) :
							?>
							<li>
								<a href="<?php echo esc_url( home_url( '/collections/' . $footer_slug . '/' ) ); ?>">
									<?php echo esc_html( $footer_label ); ?>
								</a>
							</li>
						<?php endforeach; ?>
						<li><a href="<?php echo esc_url( home_url( '/pre-order/' ) ); ?>"><?php esc_html_e( 'Pre-Order', 'skyyrose' ); ?></a></li>
						<?php if ( class_exists( 'WooCommerce' ) ) : ?>
							<li><a href="<?php echo esc_url( wc_get_page_permalink( 'shop' ) ); ?>"><?php esc_html_e( 'All Products', 'skyyrose' ); ?></a></li>
						<?php endif; ?>
					</ul>
				</div>

				<!-- Column 3: Help (1fr) -->
				<div class="footer-grid__col footer-grid__col--help">
					<h4 class="footer-grid__heading"><?php esc_html_e( 'Help', 'skyyrose' ); ?></h4>
					<ul class="footer-grid__list">
						<li><a href="<?php echo esc_url( home_url( '/contact/' ) ); ?>"><?php esc_html_e( 'Reach Out', 'skyyrose' ); ?></a></li>
						<li><a href="<?php echo esc_url( home_url( '/faq/' ) ); ?>"><?php esc_html_e( 'FAQ', 'skyyrose' ); ?></a></li>
						<li><a href="<?php echo esc_url( home_url( '/shipping-returns/' ) ); ?>"><?php esc_html_e( 'Shipping & Returns', 'skyyrose' ); ?></a></li>
						<li><a href="<?php echo esc_url( home_url( '/track-order/' ) ); ?>"><?php esc_html_e( 'Track Order', 'skyyrose' ); ?></a></li>
						<li><a href="<?php echo esc_url( home_url( '/size-guide/' ) ); ?>"><?php esc_html_e( 'Size Guide', 'skyyrose' ); ?></a></li>
						<li><a href="<?php echo esc_url( home_url( '/faq/' ) ); ?>"><?php esc_html_e( 'Care Instructions', 'skyyrose' ); ?></a></li>
					</ul>
				</div>

				<!-- Column 4: Legal (1fr) -->
				<div class="footer-grid__col footer-grid__col--legal">
					<h4 class="footer-grid__heading"><?php esc_html_e( 'Legal', 'skyyrose' ); ?></h4>
					<ul class="footer-grid__list">
						<li><a href="<?php echo esc_url( home_url( '/privacy-policy/' ) ); ?>"><?php esc_html_e( 'Privacy Policy', 'skyyrose' ); ?></a></li>
						<li><a href="<?php echo esc_url( home_url( '/terms-of-service/' ) ); ?>"><?php esc_html_e( 'Terms of Service', 'skyyrose' ); ?></a></li>
						<li><a href="<?php echo esc_url( home_url( '/refund-policy/' ) ); ?>"><?php esc_html_e( 'Refund Policy', 'skyyrose' ); ?></a></li>
						<li><a href="<?php echo esc_url( home_url( '/accessibility/' ) ); ?>"><?php esc_html_e( 'Accessibility', 'skyyrose' ); ?></a></li>
						<li><a href="<?php echo esc_url( home_url( '/cookie-policy/' ) ); ?>"><?php esc_html_e( 'Cookie Policy', 'skyyrose' ); ?></a></li>
					</ul>
				</div>

				<!-- Column 5: Social / Connect (1fr) -->
				<div class="footer-grid__col footer-grid__col--social">
					<h4 class="footer-grid__heading"><?php esc_html_e( 'Connect', 'skyyrose' ); ?></h4>
					<ul class="footer-grid__list">
						<?php
						$connect_links = $social_links;
						foreach ( $connect_links as $data ) :
							?>
							<li>
								<a href="<?php echo esc_url( $data['url'] ); ?>" target="_blank" rel="noopener noreferrer">
									<?php echo esc_html( $data['label'] ); ?>
								</a>
							</li>
						<?php endforeach; ?>
					</ul>
				</div>

			</div><!-- .footer-grid__container -->
		</div><!-- .footer-grid -->

		<!-- Copyright Bar -->
		<div class="footer-copyright">
			<div class="footer-copyright__container">
				<p class="footer-copyright__text">
					<?php
					echo '&copy; ' . esc_html( gmdate( 'Y' ) ) . ' ' . esc_html__( 'The Skyy Rose Collection LLC. All rights reserved.', 'skyyrose' );
					?>
				</p>
				<?php if ( has_nav_menu( 'footer' ) ) : ?>
					<nav class="footer-copyright__nav" aria-label="<?php esc_attr_e( 'Footer Legal Navigation', 'skyyrose' ); ?>">
						<?php
						wp_nav_menu(
							array(
								'theme_location' => 'footer',
								'menu_id'        => 'footer-legal-menu',
								'menu_class'     => 'footer-copyright__menu',
								'container'      => '',
								'depth'          => 1,
								'fallback_cb'    => 'skyyrose_nav_fallback',
							)
						);
						?>
					</nav>
				<?php endif; ?>
			</div>
		</div><!-- .footer-copyright -->

		<?php
		// Mobile bottom nav is position:fixed chrome; it lives INSIDE the
		// footer landmark so nothing visible renders after </footer>
		// (structural remediation WS4 DOM acceptance).
		get_template_part( 'template-parts/mobile-bottom-nav' );
		?>
	</footer><!-- #colophon -->
</div><!-- #page -->

<?php get_template_part( 'template-parts/size-guide-modal' ); ?>
<?php get_template_part( 'template-parts/cookie-consent' ); ?>
<?php
// Skyy mascot — reinstated v1.9.0 with finalized character art. Gated on the
// Customizer kill switch (live by default), checkout always excluded.
if ( skyyrose_mascot_is_enabled() && ! ( function_exists( 'is_checkout' ) && is_checkout() ) ) {
	get_template_part( 'template-parts/skyy-mascot' );
}
?>

<!-- Toast Notification Container -->
<div id="toast-container" class="toast-container" aria-live="polite" aria-atomic="true"></div>

<!-- Luxury Cursor elements created dynamically by luxury-cursor.js -->

<!-- Scroll Progress Indicator -->
<div class="sr-scroll-progress" aria-hidden="true">
	<div class="sr-scroll-progress__bar"></div>
</div>

<!-- Back to Top -->
<button class="sr-back-to-top" aria-label="<?php esc_attr_e( 'Back to top', 'skyyrose' ); ?>" type="button">
	<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">
		<polyline points="18 15 12 9 6 15"/>
	</svg>
</button>

<?php wp_footer(); ?>

</body>
</html>
