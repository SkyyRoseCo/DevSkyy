<?php
/**
 * Template Name: Coming Soon (Veil)
 *
 * Standalone holding page rendered during the coming-soon window. NOT
 * loaded via get_header() / get_footer() — every byte is controlled
 * here so the page ships in a single request with sub-second LCP.
 *
 * Loaded by inc/maintenance.php as a template_redirect intercept when
 * SKYYROSE_COMING_SOON_MODE is true. Also assignable as a Page Template
 * via the WP admin if needed for a permanent /coming-soon/ slug.
 *
 * Design notes (frontend-design skill v2, Register C — Expressive Brand):
 *   - Brand canon palette: deep black #0A0A0A, cream #F5E6D3, rose gold
 *     #B76E79, gold #D4AF37. No blue, no neon, no glassmorphism, no grain.
 *   - Typography: Cinzel display (brand), Hanken Grotesk body,
 *     Anton eyebrow. All self-hosted via the theme fonts dir.
 *   - Motion: ONE entrance — opacity + 12px translateY, 700ms cinematic.
 *     Respects prefers-reduced-motion.
 *   - Hierarchy through size + space, not boxes and shadows.
 *
 * @package SkyyRose
 * @since   1.4.0
 */

defined( 'ABSPATH' ) || exit;

$skyyrose_title       = __( 'The next collection is coming.', 'skyyrose' );
$skyyrose_eyebrow     = __( 'Skyy Rose — Studio Notice', 'skyyrose' );
$skyyrose_tagline     = defined( 'SKYYROSE_BRAND_TAGLINE' ) ? SKYYROSE_BRAND_TAGLINE : '';
$skyyrose_body_intro  = __( 'We are reworking the floor. The story stays the same — what you wear should say something. New collection, new chapters, same Oakland blood.', 'skyyrose' );
$skyyrose_signup_lead = __( 'Be the first to know when we open the doors.', 'skyyrose' );
$skyyrose_fonts_uri   = SKYYROSE_ASSETS_URI . '/fonts';
$skyyrose_logo_uri    = SKYYROSE_ASSETS_URI . '/branding/skyyrose-monogram.webp';
$skyyrose_logo_path   = SKYYROSE_DIR . '/assets/branding/skyyrose-monogram.webp';
$skyyrose_nonce       = wp_create_nonce( 'skyyrose_newsletter' );
$skyyrose_ajax_url    = admin_url( 'admin-ajax.php' );
?><!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
	<meta charset="<?php bloginfo( 'charset' ); ?>">
	<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
	<meta name="robots" content="noindex, follow">
	<title><?php echo esc_html( sprintf( '%s — %s', $skyyrose_title, get_bloginfo( 'name' ) ) ); ?></title>
	<meta name="description" content="<?php echo esc_attr( $skyyrose_body_intro ); ?>">
	<link rel="canonical" href="<?php echo esc_url( home_url( '/' ) ); ?>">
	<meta name="theme-color" content="#0A0A0A">
	<meta property="og:type" content="website">
	<meta property="og:title" content="<?php echo esc_attr( $skyyrose_title ); ?>">
	<meta property="og:description" content="<?php echo esc_attr( $skyyrose_tagline ); ?>">
	<meta property="og:site_name" content="<?php echo esc_attr( get_bloginfo( 'name' ) ); ?>">
	<meta property="og:url" content="<?php echo esc_url( home_url( '/' ) ); ?>">

	<link rel="preload" as="font" type="font/woff2" href="<?php echo esc_url( $skyyrose_fonts_uri . '/cinzel-latin.woff2' ); ?>" crossorigin>
	<link rel="preload" as="font" type="font/woff2" href="<?php echo esc_url( $skyyrose_fonts_uri . '/hanken-grotesk-latin.woff2' ); ?>" crossorigin>
	<link rel="preload" as="font" type="font/woff2" href="<?php echo esc_url( $skyyrose_fonts_uri . '/anton-latin.woff2' ); ?>" crossorigin>

	<style id="skyyrose-coming-soon-css">
		@font-face {
			font-family: 'Cinzel';
			src: url('<?php echo esc_url( $skyyrose_fonts_uri . '/cinzel-latin.woff2' ); ?>') format('woff2');
			font-weight: 400 900; font-style: normal; font-display: swap;
		}
		@font-face {
			font-family: 'Hanken Grotesk';
			src: url('<?php echo esc_url( $skyyrose_fonts_uri . '/hanken-grotesk-latin.woff2' ); ?>') format('woff2');
			font-weight: 300 700; font-style: normal; font-display: swap;
		}
		@font-face {
			font-family: 'Anton';
			src: url('<?php echo esc_url( $skyyrose_fonts_uri . '/anton-latin.woff2' ); ?>') format('woff2');
			font-weight: 400; font-style: normal; font-display: swap;
		}

		:root {
			--c-bg:        #0A0A0A;
			--c-bg-deep:   #060606;
			--c-ink:       #F5E6D3;
			--c-ink-soft:  rgba(245, 230, 211, 0.62);
			--c-ink-faint: rgba(245, 230, 211, 0.55);
			--c-rose-gold: #B76E79;
			--c-gold:      #D4AF37;
			--c-rule:      rgba(245, 230, 211, 0.12);
			--ff-display:  'Cinzel', 'Archivo', system-ui, sans-serif;
			--ff-body:     'Hanken Grotesk', system-ui, sans-serif;
			--ff-ui:       'Anton', 'Helvetica Neue', system-ui, sans-serif;
			--ease:        cubic-bezier(0.16, 1, 0.3, 1);
		}

		*, *::before, *::after { box-sizing: border-box; }
		html { -webkit-text-size-adjust: 100%; }
		body {
			margin: 0;
			min-height: 100dvh;
			background: var(--c-bg);
			color: var(--c-ink);
			font-family: var(--ff-body);
			font-size: 1.0625rem;
			line-height: 1.65;
			font-weight: 400;
			-webkit-font-smoothing: antialiased;
			-moz-osx-font-smoothing: grayscale;
			display: flex;
			flex-direction: column;
		}
		a { color: inherit; text-decoration: none; }
		:focus-visible { outline: 2px solid var(--c-rose-gold); outline-offset: 3px; }

		.cs-shell {
			flex: 1;
			display: grid;
			grid-template-rows: auto 1fr auto;
			padding:
				calc(1.5rem + env(safe-area-inset-top))
				clamp(1.5rem, 5vw, 3.5rem)
				calc(1.5rem + env(safe-area-inset-bottom));
			max-width: 1280px;
			width: 100%;
			margin: 0 auto;
		}

		.cs-mast {
			display: flex;
			align-items: center;
			justify-content: space-between;
			gap: 1rem;
			padding-bottom: clamp(2rem, 6vw, 4rem);
		}
		.cs-mast__mark {
			display: inline-flex;
			align-items: center;
			gap: 0.75rem;
		}
		.cs-mast__mark img {
			height: clamp(28px, 4vw, 36px);
			width: auto;
			display: block;
		}
		.cs-mast__eyebrow {
			font-family: var(--ff-ui);
			font-size: 0.72rem;
			letter-spacing: 0.32em;
			text-transform: uppercase;
			color: var(--c-ink-faint);
		}
		.cs-mast__status {
			display: inline-flex;
			align-items: center;
			gap: 0.55rem;
			font-family: var(--ff-ui);
			font-size: 0.72rem;
			letter-spacing: 0.32em;
			text-transform: uppercase;
			color: var(--c-ink-faint);
		}
		.cs-mast__pulse {
			width: 6px; height: 6px; border-radius: 50%;
			background: var(--c-rose-gold);
			box-shadow: 0 0 0 0 rgba(183, 110, 121, 0.55);
			animation: cs-pulse 2.4s infinite var(--ease);
		}
		@keyframes cs-pulse {
			0%, 70%, 100% { box-shadow: 0 0 0 0 rgba(183, 110, 121, 0.45); }
			40%           { box-shadow: 0 0 0 12px rgba(183, 110, 121, 0); }
		}

		.cs-stage {
			display: grid;
			grid-template-columns: 1fr;
			gap: clamp(2.5rem, 6vw, 5rem);
			align-content: center;
			padding: clamp(2rem, 6vw, 4rem) 0;
		}
		@media (min-width: 920px) {
			.cs-stage {
				grid-template-columns: minmax(0, 1.35fr) minmax(0, 1fr);
				align-items: center;
			}
		}

		.cs-headline {
			margin: 0;
			font-family: var(--ff-display);
			font-weight: 700;
			letter-spacing: -0.005em;
			line-height: 1.02;
			font-size: clamp(2.75rem, 8.5vw, 6.25rem);
			text-transform: uppercase;
			color: var(--c-ink);
		}
		.cs-headline__break { display: block; }
		.cs-headline__accent {
			display: block;
			color: var(--c-rose-gold);
			font-style: italic;
			font-family: 'Hanken Grotesk', system-ui, sans-serif;
			font-weight: 400;
			text-transform: none;
			letter-spacing: 0;
			font-size: clamp(1.4rem, 3.2vw, 2.1rem);
			margin-top: clamp(1.25rem, 2vw, 1.75rem);
			max-width: 22ch;
		}
		.cs-rule {
			width: clamp(48px, 6vw, 96px);
			height: 1px;
			background: var(--c-gold);
			margin: clamp(2rem, 4vw, 3rem) 0;
			border: 0;
		}
		.cs-lede {
			font-size: clamp(1rem, 1.4vw, 1.15rem);
			line-height: 1.75;
			color: var(--c-ink-soft);
			max-width: 52ch;
			margin: 0;
		}

		.cs-signup {
			display: flex;
			flex-direction: column;
			gap: 1.25rem;
			border-top: 1px solid var(--c-rule);
			padding-top: clamp(2rem, 4vw, 2.75rem);
		}
		@media (min-width: 920px) {
			.cs-signup {
				border-top: 0;
				border-left: 1px solid var(--c-rule);
				padding-top: 0;
				padding-left: clamp(2rem, 4vw, 3rem);
			}
		}
		.cs-signup__eyebrow {
			font-family: var(--ff-ui);
			font-size: 0.78rem;
			letter-spacing: 0.36em;
			text-transform: uppercase;
			color: var(--c-gold);
			margin: 0;
		}
		.cs-signup__lede {
			font-size: 1rem;
			line-height: 1.6;
			color: var(--c-ink-soft);
			margin: 0;
			max-width: 36ch;
		}
		.cs-form {
			display: flex;
			align-items: stretch;
			gap: 0;
			border-bottom: 1px solid var(--c-rose-gold);
			padding-bottom: 0.45rem;
			max-width: 420px;
		}
		.cs-form__input {
			flex: 1;
			min-width: 0;
			background: transparent;
			border: 0;
			color: var(--c-ink);
			font-family: var(--ff-body);
			font-size: 1rem;
			padding: 0.65rem 0;
			outline: none;
			min-height: 44px;
		}
		.cs-form__input::placeholder {
			color: var(--c-ink-faint);
			font-style: italic;
		}
		.cs-form__submit {
			background: transparent;
			border: 0;
			color: var(--c-ink);
			font-family: var(--ff-ui);
			font-size: 0.85rem;
			letter-spacing: 0.32em;
			text-transform: uppercase;
			padding: 0.65rem 0 0.65rem 1rem;
			cursor: pointer;
			transition: color 240ms var(--ease);
			min-height: 44px;
			min-width: 44px;
		}
		.cs-form__submit:hover { color: var(--c-rose-gold); }
		.cs-form__submit:disabled { opacity: 0.4; cursor: progress; }
		.cs-form__message {
			min-height: 1.2em;
			font-family: var(--ff-ui);
			font-size: 0.78rem;
			letter-spacing: 0.18em;
			text-transform: uppercase;
			color: var(--c-ink-soft);
		}
		.cs-form__message[data-state="success"] { color: var(--c-gold); }
		.cs-form__message[data-state="error"]   { color: var(--c-rose-gold); }

		.cs-foot {
			display: flex;
			flex-wrap: wrap;
			gap: 0.75rem 2rem;
			align-items: baseline;
			justify-content: space-between;
			padding-top: clamp(2rem, 4vw, 3rem);
			border-top: 1px solid var(--c-rule);
		}
		.cs-foot__col {
			font-family: var(--ff-ui);
			font-size: 0.72rem;
			letter-spacing: 0.32em;
			text-transform: uppercase;
			color: var(--c-ink-faint);
		}
		.cs-foot__link {
			color: var(--c-ink-soft);
			border-bottom: 1px solid transparent;
			transition: color 240ms var(--ease), border-color 240ms var(--ease);
		}
		.cs-foot__link:hover {
			color: var(--c-rose-gold);
			border-color: var(--c-rose-gold);
		}

		.cs-reveal { opacity: 0; transform: translateY(12px); transition: opacity 700ms var(--ease), transform 700ms var(--ease); }
		.cs-reveal[data-delay="1"] { transition-delay: 120ms; }
		.cs-reveal[data-delay="2"] { transition-delay: 220ms; }
		.cs-reveal[data-delay="3"] { transition-delay: 320ms; }
		.cs-reveal[data-delay="4"] { transition-delay: 440ms; }
		.cs-reveal.is-in { opacity: 1; transform: none; }

		@media (prefers-reduced-motion: reduce) {
			.cs-reveal, .cs-reveal[data-delay] { opacity: 1; transform: none; transition: none; }
			.cs-mast__pulse { animation: none; box-shadow: 0 0 0 4px rgba(183, 110, 121, 0.2); }
		}

		.screen-reader-text {
			border: 0; clip: rect(1px, 1px, 1px, 1px); clip-path: inset(50%);
			height: 1px; margin: -1px; overflow: hidden; padding: 0; position: absolute;
			width: 1px; word-wrap: normal !important;
		}
		.skip-link {
			position: absolute;
			top: -100%;
			left: 50%;
			transform: translateX(-50%);
			z-index: 10000;
			padding: 14px 32px;
			background: var(--c-rose-gold);
			color: #fff;
			font-family: var(--ff-ui);
			font-size: 0.75rem;
			font-weight: 600;
			letter-spacing: 0.18em;
			text-transform: uppercase;
			text-decoration: none;
			border: 1px solid var(--c-gold);
			border-top: none;
			border-radius: 0 0 2px 2px;
			transition: top 0.25s var(--ease);
		}
		.skip-link:focus {
			top: 0;
			outline: 2px solid var(--c-gold);
			outline-offset: 3px;
		}
	</style>
</head>
<body class="skyyrose-coming-soon">

	<a class="skip-link" href="#cs-main">
		<?php esc_html_e( 'Skip to main content', 'skyyrose' ); ?>
	</a>

	<div class="cs-shell">

		<header class="cs-mast" aria-label="<?php esc_attr_e( 'Studio masthead', 'skyyrose' ); ?>">
			<a class="cs-mast__mark cs-reveal" href="<?php echo esc_url( home_url( '/' ) ); ?>" aria-label="<?php echo esc_attr( sprintf( '%s — home', get_bloginfo( 'name' ) ) ); ?>">
				<?php if ( file_exists( $skyyrose_logo_path ) ) : ?>
					<img src="<?php echo esc_url( $skyyrose_logo_uri ); ?>" alt="" width="36" height="36" decoding="async" loading="eager">
				<?php endif; ?>
				<span class="cs-mast__eyebrow"><?php echo esc_html( $skyyrose_eyebrow ); ?></span>
			</a>
			<span class="cs-mast__status cs-reveal" data-delay="1" aria-hidden="true">
				<span class="cs-mast__pulse"></span>
				<?php esc_html_e( 'Studio active', 'skyyrose' ); ?>
			</span>
		</header>

		<main id="cs-main" class="cs-stage" role="main" tabindex="-1">

			<div class="cs-stage__left">
				<h1 class="cs-headline cs-reveal" data-delay="1">
					<span class="cs-headline__break"><?php esc_html_e( 'The next', 'skyyrose' ); ?></span>
					<span class="cs-headline__break"><?php esc_html_e( 'chapter is', 'skyyrose' ); ?></span>
					<span class="cs-headline__break"><?php esc_html_e( 'on the loom.', 'skyyrose' ); ?></span>
					<span class="cs-headline__accent"><?php echo esc_html( $skyyrose_tagline ); ?></span>
				</h1>
				<hr class="cs-rule cs-reveal" data-delay="2">
				<p class="cs-lede cs-reveal" data-delay="2">
					<?php echo esc_html( $skyyrose_body_intro ); ?>
				</p>
			</div>

			<aside class="cs-signup cs-reveal" data-delay="3" aria-label="<?php esc_attr_e( 'Newsletter signup', 'skyyrose' ); ?>">
				<p class="cs-signup__eyebrow"><?php esc_html_e( 'On the list', 'skyyrose' ); ?></p>
				<p class="cs-signup__lede"><?php echo esc_html( $skyyrose_signup_lead ); ?></p>
				<form class="cs-form" id="cs-form" novalidate>
					<label class="screen-reader-text" for="cs-email"><?php esc_html_e( 'Email address', 'skyyrose' ); ?></label>
					<input
						class="cs-form__input"
						id="cs-email"
						type="email"
						name="email"
						autocomplete="email"
						required
						placeholder="<?php esc_attr_e( 'your@email.com', 'skyyrose' ); ?>"
						aria-describedby="cs-form-msg"
					>
					<input type="hidden" name="skyyrose_newsletter_nonce" value="<?php echo esc_attr( $skyyrose_nonce ); ?>">
					<input type="hidden" name="action" value="skyyrose_newsletter_subscribe">
					<input type="hidden" name="source" value="coming-soon">
					<button class="cs-form__submit" type="submit">
						<?php esc_html_e( 'Submit', 'skyyrose' ); ?>
					</button>
				</form>
				<p class="cs-form__message" id="cs-form-msg" role="status" aria-live="polite"></p>
			</aside>

		</main>

		<footer class="cs-foot" role="contentinfo">
			<span class="cs-foot__col cs-reveal" data-delay="4">
				<?php
				echo esc_html(
					sprintf(
						/* translators: 1: current year 2: site name */
						__( '© %1$s %2$s', 'skyyrose' ),
						gmdate( 'Y' ),
						get_bloginfo( 'name' )
					)
				);
				?>
			</span>
			<span class="cs-foot__col cs-reveal" data-delay="4">
				<?php esc_html_e( 'Oakland, California — Est. 2020', 'skyyrose' ); ?>
			</span>
			<span class="cs-foot__col cs-reveal" data-delay="4">
				<a class="cs-foot__link" href="https://instagram.com/skyyrose.co" rel="noopener noreferrer" target="_blank">
					<?php esc_html_e( 'Instagram', 'skyyrose' ); ?>
				</a>
			</span>
		</footer>

	</div>

	<script>
		(function () {
			'use strict';
			document.documentElement.classList.add('js');

			var ajaxUrl = <?php echo wp_json_encode( esc_url_raw( $skyyrose_ajax_url ) ); ?>;
			var form = document.getElementById('cs-form');
			var msg  = document.getElementById('cs-form-msg');
			var input = document.getElementById('cs-email');

			// Entrance reveal — one frame after load, gated by reduced-motion media query.
			var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
			var els = document.querySelectorAll('.cs-reveal');
			if (reduced) {
				els.forEach(function (el) { el.classList.add('is-in'); });
			} else {
				requestAnimationFrame(function () {
					requestAnimationFrame(function () {
						els.forEach(function (el) { el.classList.add('is-in'); });
					});
				});
			}

			if (!form) { return; }

			function setMessage(text, state) {
				msg.textContent = text;
				if (state) { msg.setAttribute('data-state', state); }
				else       { msg.removeAttribute('data-state'); }
			}

			form.addEventListener('submit', function (ev) {
				ev.preventDefault();
				var email = (input.value || '').trim();
				if (!email || email.indexOf('@') === -1 || email.indexOf('.') === -1) {
					setMessage('Enter a valid email.', 'error');
					return;
				}
				var btn = form.querySelector('.cs-form__submit');
				if (btn) { btn.disabled = true; }
				setMessage('Sending…', null);

				var data = new FormData(form);
				fetch(ajaxUrl, { method: 'POST', credentials: 'same-origin', body: data })
					.then(function (res) { return res.json().catch(function () { return { success: false, data: { message: 'Network error.' } }; }); })
					.then(function (json) {
						if (json && json.success) {
							form.style.display = 'none';
							setMessage('You’re on the list. We’ll be in touch when the doors open.', 'success');
						} else {
							var m = (json && json.data && json.data.message) ? json.data.message : 'Something went wrong. Try again.';
							setMessage(m, 'error');
							if (btn) { btn.disabled = false; }
						}
					})
					.catch(function () {
						setMessage('Network error. Try again.', 'error');
						if (btn) { btn.disabled = false; }
					});
			});
		})();
	</script>

</body>
</html>
