<?php
/**
 * Homepage Act I — masthead poster hero.
 *
 * Three layers: the monumental word behind, the brand-mark marquee (which IS
 * the collection navigation) crossing at mid-height, and the portrait film in
 * front. Founder canon: the 720x1280 clip is centred and CONTAINED, never
 * cover-cropped — a crop cuts off the outfit that is the point of the shot.
 * The video is sized from its own 9/16 aspect ratio in homepage-v3.css, which
 * makes a crop structurally impossible rather than merely discouraged.
 *
 * The clip carries no autoplay attribute on purpose: homepage-v3.js boots it
 * at load + 2.5s or on the first gesture (the pattern proved on the pre-order
 * gateway), so the fetch never competes with the LCP paint. The poster is an
 * identical frame and is what the wp_head preload targets.
 *
 * @package SkyyRose
 * @since   1.13.0
 */

defined( 'ABSPATH' ) || exit;

$hp_assets  = SKYYROSE_ASSETS_URI;
$hp_poster  = $hp_assets . '/images/hero/home-hero-poster-720w.webp';
$hp_nav     = skyyrose_home_collection_nav();
$hp_lockups = skyyrose_home_marquee_marks();
?>
<section class="hp-hero" aria-label="<?php esc_attr_e( 'SkyyRose', 'skyyrose' ); ?>">

	<div class="hp-hero__poster">
		<p class="hp-hero__word" aria-hidden="true">SKYY<b>ROSE</b></p>

		<?php
		/*
		 * The marks are navigation, not decoration, so the first pass is not
		 * aria-hidden. The second pass exists only to make translateX(-50%)
		 * loop seamlessly and is hidden from AT and from the tab order.
		 */
		?>
		<nav class="hp-hero__marquee" aria-label="<?php esc_attr_e( 'Collections', 'skyyrose' ); ?>">
			<div class="hp-hero__track">
				<?php for ( $hp_pass = 0; $hp_pass < 2; $hp_pass++ ) : ?>
					<?php foreach ( $hp_lockups as $hp_mark ) : ?>
						<?php
						$hp_dup     = ( 1 === $hp_pass );
						$hp_tag     = $hp_dup ? 'span' : 'a';
						$hp_srcset  = ( ! empty( $hp_mark['src'] ) && function_exists( 'skyyrose_photon_srcset' ) )
							? skyyrose_photon_srcset( $hp_mark['src'], array( 96, 160, 256 ) )
							: '';
						$hp_classes = 'hp-mark';
						if ( ! empty( $hp_mark['invert'] ) ) {
							$hp_classes .= ' hp-mark--inv';
						}
						if ( ! empty( $hp_mark['wide'] ) ) {
							$hp_classes .= ' hp-mark--wide';
						}
						?>
						<<?php echo esc_html( $hp_tag ); ?>
							<?php if ( ! $hp_dup ) : ?>
								href="<?php echo esc_url( $hp_mark['href'] ); ?>"
								aria-label="<?php echo esc_attr( $hp_mark['label'] ); ?>"
							<?php else : ?>
								aria-hidden="true"
							<?php endif; ?>
						>
							<?php if ( empty( $hp_mark['src'] ) ) : ?>
								<?php // Kids Capsule has no lockup asset — set in its own script (flagged gap). ?>
								<span class="hp-mark-kc"><?php echo esc_html( $hp_mark['label'] ); ?></span>
							<?php else : ?>
								<img class="<?php echo esc_attr( $hp_classes ); ?>"
									src="<?php echo esc_url( $hp_mark['src'] ); ?>"
									<?php if ( '' !== $hp_srcset ) : ?>
										srcset="<?php echo esc_attr( $hp_srcset ); ?>"
										sizes="<?php echo esc_attr( (string) ( (int) $hp_mark['height'] * 3 ) ); ?>px"
									<?php endif; ?>
									style="--mark-h:<?php echo esc_attr( (string) (int) $hp_mark['height'] ); ?>px"
									alt=""
									decoding="async"
									fetchpriority="low">
							<?php endif; ?>
						</<?php echo esc_html( $hp_tag ); ?>>
					<?php endforeach; ?>
				<?php endfor; ?>
			</div>
		</nav>

		<video class="hp-hero__video"
			poster="<?php echo esc_url( $hp_poster ); ?>"
			width="720"
			height="1280"
			muted
			loop
			playsinline
			preload="none"
			aria-label="<?php esc_attr_e( 'SkyyRose hero film', 'skyyrose' ); ?>">
			<source src="<?php echo esc_url( $hp_assets . '/video/home-hero.webm' ); ?>" type="video/webm">
			<source src="<?php echo esc_url( $hp_assets . '/video/home-hero.mp4' ); ?>" type="video/mp4">
		</video>

		<h1 class="hp-hero__tag">
			<?php esc_html_e( 'SkyyRose', 'skyyrose' ); ?>
		</h1>

		<a class="hp-hero__world" href="<?php echo esc_url( home_url( '/collections-world/' ) ); ?>">
			<span><?php esc_html_e( 'Enter Scroll World', 'skyyrose' ); ?></span>
			<i aria-hidden="true">&rarr;</i>
		</a>
	</div>

	<?php
	/*
	 * The static, touch-usable form of the same navigation. All four are set
	 * in type here — the marks live in the marquee above, so hanging an image
	 * on one cell alone would be the opposite of consistent.
	 */
	?>
	<div class="hp-hero__nav">
		<?php foreach ( $hp_nav as $hp_item ) : ?>
			<a href="<?php echo esc_url( $hp_item['href'] ); ?>">
				<b class="n-<?php echo esc_attr( $hp_item['abbr'] ); ?>"><?php echo esc_html( $hp_item['label'] ); ?></b>
				<i><?php echo esc_html( $hp_item['kicker'] ); ?></i>
			</a>
		<?php endforeach; ?>
	</div>
</section>
