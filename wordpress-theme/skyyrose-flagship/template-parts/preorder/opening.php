<?php
/**
 * Pre-order opening experience.
 *
 * @package SkyyRose
 * @since   7.2.0
 */

defined( 'ABSPATH' ) || exit;

$po_assets = isset( $args['assets'] ) ? (string) $args['assets'] : SKYYROSE_ASSETS_URI;
$po_ver    = isset( $args['version'] ) ? (string) $args['version'] : SKYYROSE_VERSION;
?>
	<!-- ══════════════════════════════════════════════════════════════════
		01 · CINEMATIC VIDEO HERO
		══════════════════════════════════════════════════════════════════ -->
	<section class="po-hero" aria-label="<?php esc_attr_e( 'Reserve your piece', 'skyyrose' ); ?>">
		<?php
		// Founder canon (2026-07-19): the hero IS the uploaded video, framed to
		// show the ENTIRE outfit (he's wearing the brand — br-006 Bomber Sherpa,
		// rose back-embroidery). Source is portrait 720x1280, so desktop uses
		// object-fit:contain over a blurred backdrop (preorder-gateway.css) —
		// cover would crop the outfit. Poster = an actual video frame (40s,
		// back-rose shot), so autoplay-blocked / low-power / reduced-motion
		// visitors still see the brand footage, never an unrelated still.
		?>
		<div class="po-hero__media" aria-hidden="true" style="--po-hero-poster: url('<?php echo esc_url( $po_assets . '/images/hero/preorder-video-poster-720w.webp?v=' . $po_ver ); ?>')">
			<?php
			/*
			 * No autoplay/poster attrs, preload=none: the 3.5MB webm fetched
			 * inside the LCP window (round-7 mobile: poster load time up to
			 * 2.8s from link contention), and the poster attr double-fetched
			 * the frame as JPG next to the picture layer's webp. The
			 * .po-hero__poster <picture> behind the video paints the identical
			 * frame, and preorder-gateway.js initHeroVideo() starts playback
			 * at window load (or first interaction, whichever comes first) —
			 * the hero still plays the founder video, it just stops taxing
			 * first paint. Founder canon (video plays, full outfit visible)
			 * unchanged.
			 */
			?>
			<video class="po-hero__video"
				muted loop playsinline preload="none">
				<source src="<?php echo esc_url( $po_assets . '/video/preorder-hero.webm?v=' . $po_ver ); ?>" type="video/webm">
				<source src="<?php echo esc_url( $po_assets . '/video/preorder-hero.mp4?v=' . $po_ver ); ?>" type="video/mp4">
			</video>
			<picture class="po-hero__poster" aria-hidden="true">
				<source
					srcset="<?php echo esc_url( $po_assets . '/images/hero/preorder-video-poster-480w.webp?v=' . $po_ver ); ?> 480w,
							<?php echo esc_url( $po_assets . '/images/hero/preorder-video-poster-720w.webp?v=' . $po_ver ); ?> 720w"
					sizes="100vw"
					type="image/webp">
				<img src="<?php echo esc_url( $po_assets . '/images/hero/preorder-video-poster-720w.jpg?v=' . $po_ver ); ?>"
					alt="" width="720" height="1280" loading="eager" fetchpriority="high">
			</picture>
			<div class="po-hero__overlay" aria-hidden="true"></div>
		</div>

		<div class="po-hero__content">
			<?php
			// The hero is the first mobile viewport and the lockup is the LCP
			// element — no po-rv reveal classes here: the hidden resting state
			// stalls LCP behind the deferred JS queue (the PDP 24.9s bug class).
			// Below-fold sections keep reveals. Wave 5.
			?>
			<p class="po-hero__eyebrow"><?php esc_html_e( 'Exclusive Access', 'skyyrose' ); ?></p>

			<?php
			// Hero lockup renders ≤600px (width attr; ~92vw on mobile) but shipped
			// the full-size 93KB AVIF. Photon width variants via the webp; avif
			// <source> suppressed while Photon answers (it serves webp).
			$po_h_srcset = function_exists( 'skyyrose_photon_srcset' )
				? skyyrose_photon_srcset( $po_assets . '/images/hero-overlays/sig-brand-skyy-rose-gold.webp', array( 360, 600, 960 ) )
				: '';
			$po_h_sizes  = '(max-width: 640px) 92vw, 600px';
			?>
			<picture class="po-hero__lockup">
				<?php if ( '' !== $po_h_srcset ) : ?>
					<source srcset="<?php echo esc_attr( $po_h_srcset ); ?>" sizes="<?php echo esc_attr( $po_h_sizes ); ?>" type="image/webp">
				<?php else : ?>
					<source srcset="<?php echo esc_url( $po_assets . '/images/hero-overlays/sig-brand-skyy-rose-gold.avif?v=' . $po_ver ); ?>" type="image/avif">
					<source srcset="<?php echo esc_url( $po_assets . '/images/hero-overlays/sig-brand-skyy-rose-gold.webp?v=' . $po_ver ); ?>" type="image/webp">
				<?php endif; ?>
				<img src="<?php echo esc_url( $po_assets . '/images/hero-overlays/sig-brand-skyy-rose-gold.png?v=' . $po_ver ); ?>"
					<?php if ( '' !== $po_h_srcset ) : ?>
						srcset="<?php echo esc_attr( $po_h_srcset ); ?>"
						sizes="<?php echo esc_attr( $po_h_sizes ); ?>"
					<?php endif; ?>
					alt="<?php esc_attr_e( 'Skyy Rose', 'skyyrose' ); ?>"
					width="600" height="200" loading="eager">
			</picture>

			<p class="po-hero__body">
				<?php esc_html_e( 'Secure your pieces before they drop. ', 'skyyrose' ); ?>
			</p>

			<div class="po-hero__actions">
				<a class="po-btn po-btn--primary" href="#po-gateway">
					<?php esc_html_e( 'Browse Collections', 'skyyrose' ); ?>
				</a>
				<a class="po-btn po-btn--ghost" href="#po-products">
					<?php esc_html_e( 'View All Pieces', 'skyyrose' ); ?>
				</a>
			</div>
		</div>

		<div class="po-hero__scroll-hint" aria-hidden="true">
			<span class="po-hero__scroll-line"></span>
			<span class="po-hero__scroll-label"><?php esc_html_e( 'Scroll', 'skyyrose' ); ?></span>
		</div>
	</section>

	<!-- ══════════════════════════════════════════════════════════════════
		02 · MARQUEE STRIP
		══════════════════════════════════════════════════════════════════ -->
	<div class="po-marquee" aria-hidden="true">
		<div class="po-marquee__track">
			<?php
			/* Items cloned by JS for seamless loop */
			$po_marquee_items = array(
				esc_html__( '', 'skyyrose' ),
				esc_html__( 'Limited Edition', 'skyyrose' ),
				esc_html__( 'Reserve Now', 'skyyrose' ),
				esc_html__( 'Skyy Rose', 'skyyrose' ),
				esc_html__( 'Concrete Culture', 'skyyrose' ),
				esc_html__( 'Pre-Order Open', 'skyyrose' ),
			);
			foreach ( $po_marquee_items as $po_item ) :
				?>
				<span class="po-marquee__item">
					<picture class="po-marquee__icon">
						<source srcset="<?php echo esc_url( $po_assets . '/images/logos/sr-monogram-gold.avif?v=' . $po_ver ); ?>" type="image/avif">
						<source srcset="<?php echo esc_url( $po_assets . '/images/logos/sr-monogram-gold.webp?v=' . $po_ver ); ?>" type="image/webp">
						<img src="<?php echo esc_url( $po_assets . '/images/logos/sr-monogram-gold.jpeg?v=' . $po_ver ); ?>"
							alt="" width="24" height="24" loading="lazy">
					</picture>
					<?php echo esc_html( $po_item ); ?>
				</span>
			<?php endforeach; ?>
		</div>
	</div>
