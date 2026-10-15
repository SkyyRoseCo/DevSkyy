<?php
/**
 * Homepage Act VIII — the close.
 *
 * One centred voice: the monogram plate is the object, one sentence is the
 * argument, and the email field is set INSIDE that sentence as an underlined
 * blank you fill in. Capture is unambiguously the primary affordance; the
 * service promise is demoted to a hairline footnote rail.
 *
 * Honesty contract: the status line ships EMPTY, and homepage-v3.js paints
 * success ONLY after admin-ajax.php answers success. The previous build
 * showed "Welcome to the movement" without ever sending a request, because
 * the AJAX config object it looked for was never localized anywhere in the
 * theme — the endpoint and nonce now travel on the form itself.
 *
 * The copyright line lives in the canonical site footer, not here.
 *
 * @package SkyyRose
 * @since   1.13.0
 */

defined( 'ABSPATH' ) || exit;
?>
<section class="hp-close" id="community" aria-labelledby="hp-close-h">
	<div class="hp-close__inner">

		<div class="hp-close__plate">
			<img src="<?php echo esc_url( SKYYROSE_ASSETS_URI . '/branding/skyyrose-monogram.webp' ); ?>"
				alt="<?php esc_attr_e( 'SkyyRose monogram', 'skyyrose' ); ?>"
				width="2048"
				height="2048"
				loading="lazy"
				decoding="async">
		</div>

		<p class="hp-close__eyebrow"><?php esc_html_e( 'Join the Movement', 'skyyrose' ); ?></p>
		<h2 class="hp-close__statement" id="hp-close-h">
			<?php esc_html_e( 'For The Real Ones', 'skyyrose' ); ?>
		</h2>
		<p class="hp-close__desc"><?php esc_html_e( 'Early access to drops. Behind-the-scenes from Oakland. Stories that matter. No spam, just substance.', 'skyyrose' ); ?></p>

		<form class="hp-close__form"
			data-capture
			novalidate
			aria-label="<?php esc_attr_e( 'Newsletter signup', 'skyyrose' ); ?>"
			data-ajax-url="<?php echo esc_url( admin_url( 'admin-ajax.php' ) ); ?>"
			data-nonce="<?php echo esc_attr( wp_create_nonce( 'skyyrose_newsletter' ) ); ?>"
			data-msg-empty="<?php esc_attr_e( 'Enter an email address to join.', 'skyyrose' ); ?>"
			data-msg-invalid="<?php esc_attr_e( 'That address does not look right.', 'skyyrose' ); ?>"
			data-msg-sending="<?php esc_attr_e( 'Sending…', 'skyyrose' ); ?>"
			data-msg-ok="<?php esc_attr_e( 'You’re on the list.', 'skyyrose' ); ?>"
			data-msg-fail="<?php esc_attr_e( 'That didn’t go through. Try again in a moment.', 'skyyrose' ); ?>"
			data-msg-offline="<?php esc_attr_e( 'We couldn’t reach the server. Check your connection and try again.', 'skyyrose' ); ?>">
			<div class="hp-close__line">
				<span><?php esc_html_e( 'Send it to', 'skyyrose' ); ?></span>
				<label class="hp-sr" for="hp-close-email"><?php esc_html_e( 'Email address', 'skyyrose' ); ?></label>
				<input class="hp-close__input"
					id="hp-close-email"
					type="email"
					name="email"
					autocomplete="email"
					placeholder="<?php esc_attr_e( 'your email address', 'skyyrose' ); ?>"
					required>
				<button class="hp-close__go" type="submit" aria-label="<?php esc_attr_e( 'Join', 'skyyrose' ); ?>">&rarr;</button>
			</div>
			<p class="hp-close__status" role="status" aria-live="polite" data-status></p>
			<p class="hp-close__note"><?php esc_html_e( 'Free to join · Unsubscribe anytime · Oakland love only', 'skyyrose' ); ?></p>
		</form>

		<?php // Fit Guide stays a <button> (it opens the size-guide modal); the other three navigate. ?>
		<nav class="hp-close__services" aria-label="<?php esc_attr_e( 'SkyyRose Service Promise', 'skyyrose' ); ?>">
			<a class="hp-close__svc" href="<?php echo esc_url( home_url( '/shipping-returns/' ) ); ?>">
				<?php esc_html_e( 'Clear Shipping', 'skyyrose' ); ?>
				<small><?php esc_html_e( 'Delivery and return expectations before checkout.', 'skyyrose' ); ?></small>
			</a>
			<button class="hp-close__svc" type="button" data-open-size-guide>
				<?php esc_html_e( 'Fit Guide', 'skyyrose' ); ?>
				<small><?php esc_html_e( 'Measure once, shop every drop with more confidence.', 'skyyrose' ); ?></small>
			</button>
			<a class="hp-close__svc" href="<?php echo esc_url( home_url( '/wishlist/' ) ); ?>">
				<?php esc_html_e( 'Wishlist Flow', 'skyyrose' ); ?>
				<small><?php esc_html_e( 'Save looks before small runs disappear.', 'skyyrose' ); ?></small>
			</a>
			<a class="hp-close__svc" href="<?php echo esc_url( home_url( '/contact/' ) ); ?>">
				<?php esc_html_e( 'Concierge Contact', 'skyyrose' ); ?>
				<small><?php esc_html_e( 'Questions, press, styling, and collaboration routes.', 'skyyrose' ); ?></small>
			</a>
		</nav>

		<p class="hp-close__scarcity"><?php esc_html_e( 'Limited Edition. Individually Numbered. Never Restocked.', 'skyyrose' ); ?></p>
	</div>
</section>
