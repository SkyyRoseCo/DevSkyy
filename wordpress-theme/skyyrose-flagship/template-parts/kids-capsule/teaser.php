<?php
/**
 * Kids Capsule — Launch Mode Teaser
 *
 * Full-viewport teaser with countdown, waitlist, and brand story.
 * Displayed when Customizer "skyyrose_kc_mode" is set to "launch".
 *
 * Sections:
 *   1. Hero — KC Night canvas with aurora gradient wordmark
 *   2. Reveal Statement — "Named after a daughter. Made for yours."
 *   3. Countdown Timer — reads skyyrose_kc_launch_date theme mod
 *   4. Parent-Child Preview — editorial silhouettes with KC palette
 *   5. Waitlist Form — Klaviyo email capture
 *   6. Brand Anchor — founder tribute
 *
 * @package SkyyRose
 * @since   6.5.0
 */

defined( 'ABSPATH' ) || exit;

$launch_date = get_theme_mod( 'skyyrose_kc_launch_date', '' );
$assets_uri  = defined( 'SKYYROSE_ASSETS_URI' ) ? SKYYROSE_ASSETS_URI : '';
?>

<div class="kc-teaser" data-collection="kids-capsule">

	<?php
	/*
	--------------------------------------------------------------
	 * 1. Hero — KC Night Canvas
	 *--------------------------------------------------------------*/
	?>
	<section class="kc-teaser__hero" id="kc-hero" aria-label="<?php esc_attr_e( 'Kids Capsule Coming Soon', 'skyyrose' ); ?>">
		<div class="kc-teaser__hero-bg" aria-hidden="true"></div>
		<div class="kc-teaser__hero-content">
			<span class="kc-teaser__badge"><?php esc_html_e( 'Coming Soon', 'skyyrose' ); ?></span>
			<h1 class="kc-teaser__wordmark"><?php esc_html_e( 'Kids Capsule', 'skyyrose' ); ?></h1>
			<p class="kc-teaser__tagline"><?php esc_html_e( 'Luxury runs in the family.', 'skyyrose' ); ?></p>
		</div>
		<div class="kc-teaser__scroll" aria-hidden="true">
			<span><?php esc_html_e( 'Scroll', 'skyyrose' ); ?></span>
			<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<polyline points="6 9 12 15 18 9"></polyline>
			</svg>
		</div>
	</section>

	<?php
	/*
	--------------------------------------------------------------
	 * 2. Reveal Statement
	 *--------------------------------------------------------------*/
	?>
	<section class="kc-teaser__reveal col-reveal" aria-label="<?php esc_attr_e( 'Collection Story', 'skyyrose' ); ?>">
		<div class="kc-teaser__reveal-inner">
			<blockquote class="kc-teaser__quote">
				<p class="kc-teaser__quote-text rv-split-word">
					<?php esc_html_e( 'Named after a daughter. Made for yours.', 'skyyrose' ); ?>
				</p>
			</blockquote>
			<p class="kc-teaser__reveal-sub rv-blur">
				<?php esc_html_e( 'Mini versions of our signature pieces, designed for the youngest trendsetters who inherit their style from the best.', 'skyyrose' ); ?>
			</p>
		</div>
	</section>

	<?php
	/*
	--------------------------------------------------------------
	 * 3. Countdown Timer
	 *--------------------------------------------------------------*/
	?>
	<?php if ( $launch_date ) : ?>
	<section class="kc-teaser__countdown col-reveal" id="kc-countdown" aria-label="<?php esc_attr_e( 'Launch Countdown', 'skyyrose' ); ?>">
		<h2 class="kc-teaser__section-title"><?php esc_html_e( 'Launching In', 'skyyrose' ); ?></h2>
		<div class="kc-countdown" data-countdown="<?php echo esc_attr( $launch_date ); ?>">
			<div class="kc-countdown__unit">
				<span class="kc-countdown__num" data-cd="d">00</span>
				<span class="kc-countdown__label"><?php esc_html_e( 'Days', 'skyyrose' ); ?></span>
			</div>
			<span class="kc-countdown__sep" aria-hidden="true">:</span>
			<div class="kc-countdown__unit">
				<span class="kc-countdown__num" data-cd="h">00</span>
				<span class="kc-countdown__label"><?php esc_html_e( 'Hours', 'skyyrose' ); ?></span>
			</div>
			<span class="kc-countdown__sep" aria-hidden="true">:</span>
			<div class="kc-countdown__unit">
				<span class="kc-countdown__num" data-cd="m">00</span>
				<span class="kc-countdown__label"><?php esc_html_e( 'Min', 'skyyrose' ); ?></span>
			</div>
			<span class="kc-countdown__sep" aria-hidden="true">:</span>
			<div class="kc-countdown__unit">
				<span class="kc-countdown__num" data-cd="s">00</span>
				<span class="kc-countdown__label"><?php esc_html_e( 'Sec', 'skyyrose' ); ?></span>
			</div>
		</div>
	</section>
	<?php endif; ?>

	<?php
	/*
	--------------------------------------------------------------
	 * 4. Parent-Child Preview
	 *--------------------------------------------------------------*/
	?>
	<section class="kc-teaser__preview col-reveal" aria-label="<?php esc_attr_e( 'Collection Preview', 'skyyrose' ); ?>">
		<div class="kc-teaser__preview-inner">
			<h2 class="kc-teaser__section-title rv-clip-up"><?php esc_html_e( 'Match With Your Mini', 'skyyrose' ); ?></h2>
			<p class="kc-teaser__preview-text rv-blur">
				<?php esc_html_e( 'Every Kids Capsule piece is designed to complement an adult style from our core collections. Dress alike without the cringe — luxury twinning, elevated.', 'skyyrose' ); ?>
			</p>
			<div class="kc-teaser__silhouettes" aria-hidden="true">
				<div class="kc-teaser__silhouette kc-teaser__silhouette--adult">
					<div class="kc-teaser__silhouette-placeholder"></div>
					<span class="kc-teaser__silhouette-label"><?php esc_html_e( 'Parent', 'skyyrose' ); ?></span>
				</div>
				<div class="kc-teaser__silhouette kc-teaser__silhouette--child">
					<div class="kc-teaser__silhouette-placeholder"></div>
					<span class="kc-teaser__silhouette-label"><?php esc_html_e( 'Mini', 'skyyrose' ); ?></span>
				</div>
			</div>
		</div>
	</section>

	<?php
	/*
	--------------------------------------------------------------
	 * 5. Waitlist Form — Klaviyo
	 *--------------------------------------------------------------*/
	?>
	<section class="kc-teaser__waitlist col-reveal" id="kc-waitlist" aria-label="<?php esc_attr_e( 'Join the Waitlist', 'skyyrose' ); ?>">
		<div class="kc-teaser__waitlist-inner">
			<h2 class="kc-teaser__section-title"><?php esc_html_e( 'Be the First to Know', 'skyyrose' ); ?></h2>
			<p class="kc-teaser__waitlist-text">
				<?php esc_html_e( 'Join the Kids Capsule waitlist for early access, first-look previews, and first dibs on every drop.', 'skyyrose' ); ?>
			</p>
			<form class="kc-waitlist-form" id="kc-waitlist-form" method="post" action="">
				<?php wp_nonce_field( 'skyyrose_newsletter', 'skyyrose_newsletter_nonce' ); ?>
				<input type="hidden" name="action" value="skyyrose_newsletter_subscribe" />
				<input type="hidden" name="list" value="kids_capsule" />
				<div class="kc-waitlist-form__row">
					<label for="kc-email" class="screen-reader-text"><?php esc_html_e( 'Email address', 'skyyrose' ); ?></label>
					<input type="email"
						id="kc-email"
						name="email"
						required
						autocomplete="email"
						placeholder="<?php esc_attr_e( 'your@email.com', 'skyyrose' ); ?>"
						class="kc-waitlist-form__input" />
					<button type="submit" class="kc-waitlist-form__btn">
						<?php esc_html_e( 'Join the Waitlist', 'skyyrose' ); ?>
					</button>
				</div>
				<div class="kc-waitlist-form__status" role="status" aria-live="polite"></div>
			</form>
		</div>
	</section>

	<?php
	/*
	--------------------------------------------------------------
	 * 6. Brand Anchor
	 *--------------------------------------------------------------*/
	?>
	<section class="kc-teaser__anchor col-reveal" aria-label="<?php esc_attr_e( 'Brand Story', 'skyyrose' ); ?>">
		<div class="kc-teaser__anchor-inner">
			<blockquote class="kc-teaser__anchor-quote">
				<p class="kc-teaser__anchor-text rv-split-word">
					<?php esc_html_e( 'Corey built this brand for Skyy Rose. This collection is hers.', 'skyyrose' ); ?>
				</p>
			</blockquote>
		</div>
	</section>

</div>
