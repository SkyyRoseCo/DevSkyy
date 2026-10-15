<?php
/**
 * Enqueue Scripts & Styles
 *
 * Handles all CSS and JS enqueue logic with conditional loading per template.
 * Global assets load on every page; template-specific assets load only where needed.
 *
 * @package SkyyRose
 * @since   3.0.0
 */

// Prevent direct access.
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Enqueue self-hosted fonts (all brand typography).
 *
 * GDPR-compliant: zero external requests to Google Fonts.
 * 5 universal families + 4 collection scripts served locally from assets/fonts/ as woff2.
 * Universal: Inter, Archivo, Cinzel, Hanken Grotesk, Anton.
 * Collection scripts: SkyyRose Black Rose Script, SkyyRose Love Hurts Graffiti,
 * Pinyon Script, Grand Hotel.
 *
 * @since 3.2.1
 * @updated 4.1.0 — self-hosted all Google Fonts families
 * @return void
 */
function skyyrose_enqueue_local_fonts() {
	wp_enqueue_style(
		'skyyrose-fonts',
		SKYYROSE_ASSETS_URI . '/css/fonts.css',
		array(),
		SKYYROSE_VERSION
	);
}

/**
 * Whether a template slug skips the optional asset bundles (size guide, luxury
 * cursor, skeleton).
 *
 * Single source of truth for BOTH the style and script enqueues. These bundles are
 * CSS+JS pairs: shipping the JS without its stylesheet renders unstyled artifacts
 * (the luxury cursor's label span rendered as stray body text on every slug listed
 * here), so the two must be gated identically. Keeping the list in one function is
 * what prevents them drifting apart again.
 *
 * @since 1.12.9
 * @param string $slug Template slug from skyyrose_get_current_template_slug().
 * @return bool True when the slug should skip optional assets.
 */
function skyyrose_slug_skips_optional_assets( $slug ) {
	// Cart / checkout / 404 / search / blog / single never trigger these features,
	// so shipping their assets is dead bytes. v1.5.12 audit.
	return in_array(
		$slug,
		array( 'cart', 'checkout', 'blog', 'single', '404', 'search', 'default' ),
		true
	);
}

/**
 * Enqueue global styles that load on every page.
 *
 * @since 3.0.0
 * @return void
 */
function skyyrose_enqueue_global_styles() {

	$base_uri = SKYYROSE_ASSETS_URI . '/css';
	$base_dir = SKYYROSE_DIR . '/assets/css';
	$use_min  = ! defined( 'SCRIPT_DEBUG' ) || ! SCRIPT_DEBUG;

	// Main theme stylesheet (style.css with WordPress header). Serve the built
	// style.min.css when current (26.3K → 18.3K; round-3 flagged the raw file
	// render-blocking on 9 pages). Freshness-guarded: a .min older than its
	// source falls back to style.css, so a deploy-without-rebuild can never
	// ship stale rules (style.css carried a P0 syntax fix in Wave 1).
	$style_uri = get_stylesheet_uri();
	$style_min = SKYYROSE_DIR . '/style.min.css';
	if ( $use_min && file_exists( $style_min )
		&& filemtime( $style_min ) >= filemtime( SKYYROSE_DIR . '/style.css' ) ) {
		$style_uri = SKYYROSE_URI . '/style.min.css';
	}
	wp_enqueue_style(
		'skyyrose-style',
		$style_uri,
		array(),
		SKYYROSE_VERSION
	);

	/*
	 * Build-time bundles (production): bundles/core.min.css is the six
	 * always-render-blocking globals concatenated in this exact enqueue order
	 * (main, design-tokens, components, system/animations, header,
	 * mobile-bottom-nav — see scripts/bundles.config.js).
	 * NOT WordPress runtime concat — CONCATENATE_SCRIPTS stays false (WP.com
	 * MIME constraint); these are static files emitted by build-css.js.
	 *
	 * The bundle keeps the 'skyyrose-main' handle so the fetchpriority=high
	 * critical-handle filter in enqueue-performance.php matches unchanged.
	 * Absorbed handles are re-registered as enqueued src-false aliases so
	 * every dependency ($global_deps on design-tokens, premium-animations on
	 * animations) and every wp_add_inline_style target (customizer +
	 * performance-guardian attach to design-tokens) keeps printing. Alias
	 * inline CSS prints after the whole bundle instead of mid-cascade; proven
	 * safe 2026-07-29 — the emitted custom properties/selectors are disjoint
	 * from everything that moved (see bundles.config.js header).
	 *
	 * SCRIPT_DEBUG or a missing bundle falls through to the individual
	 * per-file enqueues below — the debuggable dev path is unchanged.
	 */
	$css_bundled = $use_min && file_exists( $base_dir . '/bundles/core.min.css' );
	if ( $css_bundled ) {
		wp_enqueue_style(
			'skyyrose-main',
			$base_uri . '/bundles/core.min.css',
			array( 'skyyrose-style', 'skyyrose-fonts' ),
			SKYYROSE_VERSION
		);
		$core_aliases = array(
			'skyyrose-design-tokens',
			'skyyrose-components',
			'skyyrose-animations',
			'skyyrose-header',
			'skyyrose-mobile-nav',
		);
		foreach ( $core_aliases as $core_alias ) {
			wp_register_style( $core_alias, false, array( 'skyyrose-main' ), SKYYROSE_VERSION );
			wp_enqueue_style( $core_alias );
		}
	}

	if ( ! $css_bundled ) {
		// Elite Web Builder global styles: font vars, grain overlay, sr-container.
		$main_file = $use_min && file_exists( $base_dir . '/main.min.css' ) ? 'main.min.css' : 'main.css';
		if ( file_exists( $base_dir . '/' . $main_file ) ) {
			wp_enqueue_style(
				'skyyrose-main',
				$base_uri . '/' . $main_file,
				array( 'skyyrose-style', 'skyyrose-fonts' ),
				SKYYROSE_VERSION
			);
		}

		// Design tokens: CSS custom properties for colors, spacing, typography.
		$tokens_file = $use_min && file_exists( $base_dir . '/design-tokens.min.css' ) ? 'design-tokens.min.css' : 'design-tokens.css';
		wp_enqueue_style(
			'skyyrose-design-tokens',
			$base_uri . '/' . $tokens_file,
			array( 'skyyrose-style' ),
			SKYYROSE_VERSION
		);

		// Components: reusable component styles (buttons, cards, forms, etc.).
		$comp_file = $use_min && file_exists( $base_dir . '/components.min.css' ) ? 'components.min.css' : 'components.css';
		if ( file_exists( $base_dir . '/' . $comp_file ) ) {
			wp_enqueue_style(
				'skyyrose-components',
				$base_uri . '/' . $comp_file,
				array( 'skyyrose-design-tokens' ),
				SKYYROSE_VERSION
			);
		}

		// Animations: unified scroll-reveal system (.rv, .rv-left, .rv-right, .rv-scale).
		$anim_file = $use_min && file_exists( $base_dir . '/system/animations.min.css' ) ? 'system/animations.min.css' : 'system/animations.css';
		if ( file_exists( $base_dir . '/' . $anim_file ) ) {
			wp_enqueue_style(
				'skyyrose-animations',
				$base_uri . '/' . $anim_file,
				array( 'skyyrose-design-tokens' ),
				SKYYROSE_VERSION
			);
		}
	}

	// Premium animations: clip-path reveals, split-text, stagger, magnetic, parallax.
	// Conditionally loaded — skip on lightweight pages where the extra CSS is wasted
	// (cart, checkout, blog, search, 404, generic pages, contact).
	// Loaded on: front-page, about, immersive, preorder-gateway, collection pages,
	// single-product, shop-archive (footer uses stagger-grid + rv-clip-up).
	$prem_anim = $use_min && file_exists( $base_dir . '/system/animations-premium.min.css' )
		? 'system/animations-premium.min.css' : 'system/animations-premium.css';
	if ( file_exists( $base_dir . '/' . $prem_anim ) ) {
		$prem_slug = skyyrose_get_current_template_slug();
		// collections-world: bare-canvas template — every element is engine-built
		// sw-* DOM, none of the premium utility classes exist there.
		$prem_skip    = array( 'cart', 'checkout', 'blog', 'single', 'page', 'contact', '404', 'default', 'collections-world' );
		$skip_premium = in_array( $prem_slug, $prem_skip, true );
		if ( ! $skip_premium ) {
			wp_enqueue_style(
				'skyyrose-animations-premium',
				$base_uri . '/' . $prem_anim,
				array( 'skyyrose-animations' ),
				SKYYROSE_VERSION
			);
		}
	}

	// Commercial polish is now enqueued at priority 25 via
	// skyyrose_enqueue_commercial_polish() to guarantee it loads AFTER
	// all template-specific stylesheets (priority 20).

	// Header: navbar, search overlay, mobile menu, dropdowns.
	// (In the core bundle when $css_bundled.)
	if ( ! $css_bundled ) {
		$header_file = $use_min && file_exists( $base_dir . '/header.min.css' ) ? 'header.min.css' : 'header.css';
		if ( file_exists( $base_dir . '/' . $header_file ) ) {
			wp_enqueue_style(
				'skyyrose-header',
				$base_uri . '/' . $header_file,
				array( 'skyyrose-design-tokens' ),
				SKYYROSE_VERSION
			);
		}
	}

	// Footer + Footer CRO: both unconditional, async-swapped together on tall
	// slugs (enqueue-performance.php) — bundled as bundles/footer.min.css
	// under the existing 'skyyrose-footer' handle so the async-handle entry
	// matches unchanged. The footer-cro alias keeps the in-part
	// wp_print_styles fallback (template-parts/footer-cro.php) a no-op.
	// The head enqueue itself is the Wave-1 CLS fix: the part is included
	// unconditionally from footer.php, so its styles belong in the head.
	$footer_bundle = $base_dir . '/bundles/footer.min.css';
	if ( $use_min && file_exists( $footer_bundle ) ) {
		wp_enqueue_style(
			'skyyrose-footer',
			$base_uri . '/bundles/footer.min.css',
			array( 'skyyrose-design-tokens' ),
			SKYYROSE_VERSION
		);
		wp_register_style( 'skyyrose-footer-cro', false, array( 'skyyrose-footer' ), SKYYROSE_VERSION );
		wp_enqueue_style( 'skyyrose-footer-cro' );
	} else {
		// Footer: newsletter bar, grid columns, copyright bar, brand column.
		$footer_file = $use_min && file_exists( $base_dir . '/footer.min.css' ) ? 'footer.min.css' : 'footer.css';
		if ( file_exists( $base_dir . '/' . $footer_file ) ) {
			wp_enqueue_style(
				'skyyrose-footer',
				$base_uri . '/' . $footer_file,
				array( 'skyyrose-design-tokens' ),
				SKYYROSE_VERSION
			);
		}

		$fcro_css_file = $use_min && file_exists( $base_dir . '/footer-cro.min.css' ) ? 'footer-cro.min.css' : 'footer-cro.css';
		if ( file_exists( $base_dir . '/' . $fcro_css_file ) ) {
			wp_enqueue_style(
				'skyyrose-footer-cro',
				$base_uri . '/' . $fcro_css_file,
				array( 'skyyrose-design-tokens' ),
				SKYYROSE_VERSION
			);
		}
	}

	// Mobile bottom navigation bar (hidden via CSS on desktop ≥769px).
	// (In the core bundle when $css_bundled.)
	if ( ! $css_bundled ) {
		$mobnav_file = $use_min && file_exists( $base_dir . '/mobile-bottom-nav.min.css' ) ? 'mobile-bottom-nav.min.css' : 'mobile-bottom-nav.css';
		if ( file_exists( $base_dir . '/' . $mobnav_file ) ) {
			wp_enqueue_style(
				'skyyrose-mobile-nav',
				$base_uri . '/' . $mobnav_file,
				array( 'skyyrose-design-tokens' ),
				SKYYROSE_VERSION
			);
		}
	}

	// Cookie consent banner (GDPR).
	$cookie_file = $use_min && file_exists( $base_dir . '/cookie-consent.min.css' ) ? 'cookie-consent.min.css' : 'cookie-consent.css';
	if ( file_exists( $base_dir . '/' . $cookie_file ) ) {
		wp_enqueue_style(
			'skyyrose-cookie-consent',
			$base_uri . '/' . $cookie_file,
			array(),
			SKYYROSE_VERSION
		);
	}

	// Lightweight slugs skip optional CSS bundles (size guide, luxury cursor,
	// skeleton). Cart / checkout / 404 / search / blog / single never trigger
	// these features, so shipping their CSS is dead bytes. v1.5.12 audit.
	$skip_optional_css = skyyrose_slug_skips_optional_assets( skyyrose_get_current_template_slug() );

	// Size guide modal + luxury cursor: same skip-slug gate, both always
	// async-swapped — bundled as bundles/optional-ui.min.css under the
	// existing 'skyyrose-size-guide' handle so the async-handle entry matches.
	$optional_bundle = $base_dir . '/bundles/optional-ui.min.css';
	if ( ! $skip_optional_css && $use_min && file_exists( $optional_bundle ) ) {
		wp_enqueue_style(
			'skyyrose-size-guide',
			$base_uri . '/bundles/optional-ui.min.css',
			array(),
			SKYYROSE_VERSION
		);
	} elseif ( ! $skip_optional_css ) {
		// Size guide modal (trigger via [data-open-size-guide] or .js-size-guide-trigger).
		$size_guide_file = $use_min && file_exists( $base_dir . '/size-guide.min.css' ) ? 'size-guide.min.css' : 'size-guide.css';
		if ( file_exists( $base_dir . '/' . $size_guide_file ) ) {
			wp_enqueue_style(
				'skyyrose-size-guide',
				$base_uri . '/' . $size_guide_file,
				array(),
				SKYYROSE_VERSION
			);
		}

		// Luxury cursor — dot follower (desktop only, CSS hidden on touch/mobile).
		$cursor_css_file = $use_min && file_exists( $base_dir . '/luxury-cursor.min.css' ) ? 'luxury-cursor.min.css' : 'luxury-cursor.css';
		if ( file_exists( $base_dir . '/' . $cursor_css_file ) ) {
			wp_enqueue_style(
				'skyyrose-luxury-cursor',
				$base_uri . '/' . $cursor_css_file,
				array(),
				SKYYROSE_VERSION
			);
		}
	}

	// Skeleton loading states — shimmer placeholders for images and cards.
	$skeleton_file = $use_min && file_exists( $base_dir . '/skeleton.min.css' ) ? 'skeleton.min.css' : 'skeleton.css';
	if ( ! $skip_optional_css && file_exists( $base_dir . '/' . $skeleton_file ) ) {
		wp_enqueue_style(
			'skyyrose-skeleton',
			$base_uri . '/' . $skeleton_file,
			array(),
			SKYYROSE_VERSION
		);
	}

	// Skyy mascot CSS — gated on the Customizer kill switch (live by default,
	// see skyyrose_mascot_is_enabled()) and excluded from checkout. Degrades
	// to a 2D sprite when no GLB is configured/shipped.
	$mascot_enabled = skyyrose_mascot_is_enabled()
		&& ! ( function_exists( 'is_checkout' ) && is_checkout() );
	if ( $mascot_enabled ) {
		// Same kill-switch gate, skyy-walk depends on mascot — bundled as
		// bundles/mascot.min.css under the existing 'skyyrose-mascot' handle
		// (async-handle entry on tall slugs matches unchanged).
		$mascot_bundle = $base_dir . '/bundles/mascot.min.css';
		if ( $use_min && file_exists( $mascot_bundle ) ) {
			wp_enqueue_style(
				'skyyrose-mascot',
				$base_uri . '/bundles/mascot.min.css',
				array( 'skyyrose-design-tokens' ),
				SKYYROSE_VERSION
			);
			wp_register_style( 'skyyrose-skyy-walk', false, array( 'skyyrose-mascot' ), SKYYROSE_VERSION );
			wp_enqueue_style( 'skyyrose-skyy-walk' );
		} else {
			$mascot_css_file = $use_min && file_exists( $base_dir . '/mascot.min.css' ) ? 'mascot.min.css' : 'mascot.css';
			if ( file_exists( $base_dir . '/' . $mascot_css_file ) ) {
				wp_enqueue_style(
					'skyyrose-mascot',
					$base_uri . '/' . $mascot_css_file,
					array( 'skyyrose-design-tokens' ),
					SKYYROSE_VERSION
				);
			}

			$skyy_walk_css_file = $use_min && file_exists( $base_dir . '/skyy-walk.min.css' ) ? 'skyy-walk.min.css' : 'skyy-walk.css';
			if ( file_exists( $base_dir . '/' . $skyy_walk_css_file ) ) {
				wp_enqueue_style(
					'skyyrose-skyy-walk',
					$base_uri . '/' . $skyy_walk_css_file,
					array( 'skyyrose-mascot' ),
					SKYYROSE_VERSION
				);
			}
		}
	}

	// Agency-Tier Visuals enqueue removed (census-deleted 2026-07-29, zero
	// consumers, agency-tier-visuals.css + .min twin no longer exist) — this
	// block previously relied on file_exists() to silently no-op rather than
	// being removed outright (same dead-enqueue class as bug-312).

	// hero-cinematic.css enqueue removed (perf wave 2026-07-19); the orphaned
	// files (css + template-parts/hero-cinematic.php) were census-deleted
	// 2026-07-29. The part had zero get_template_part
	// callers — every template renders its own hero — so the sheet was a dead
	// render-blocking request on all non-lightweight pages. If a template ever
	// adopts the part, re-enqueue the stylesheet gated to that template's slug.
}

/**
 * Enqueue global scripts that load on every page.
 *
 * @since 3.0.0
 * @return void
 */
function skyyrose_enqueue_global_scripts() {

	$js_uri  = SKYYROSE_ASSETS_URI . '/js';
	$js_dir  = SKYYROSE_DIR . '/assets/js';
	$css_uri = SKYYROSE_ASSETS_URI . '/css';
	$css_dir = SKYYROSE_DIR . '/assets/css';
	$use_min = ! defined( 'SCRIPT_DEBUG' ) || ! SCRIPT_DEBUG;

	// Lightweight slugs (cart/checkout/404/search) don't trigger premium
	// animations. Skip Motion One + premium-interactions to save ~60KB parse.
	// v1.5.12 audit. Same skip list as global_styles.
	$skip_premium_js = in_array(
		skyyrose_get_current_template_slug(),
		array( 'cart', 'checkout', 'blog', 'single', '404', 'search', 'default', 'collections-world' ),
		true
	);

	/*
	 * Build-time JS core bundle: navigation + toast + footer-cro +
	 * page-transitions — all unconditional, all defer + in_footer,
	 * independent IIFEs concatenated in enqueue order
	 * (scripts/bundles.config.js). Enqueued under the existing
	 * 'skyyrose-navigation' handle so skyyrose_localize_scripts() keeps
	 * attaching skyyRoseData to it unchanged. The footer-cro alias
	 * (src-false, enqueued) carries its skyyRoseFooterCro localization —
	 * inline config always executes before deferred scripts, so the bundle
	 * reads it exactly as the standalone file did.
	 * SCRIPT_DEBUG / missing bundle falls through to per-file enqueues.
	 */
	$js_bundled = $use_min && file_exists( $js_dir . '/bundles/core.min.js' );
	if ( $js_bundled ) {
		wp_enqueue_script(
			'skyyrose-navigation',
			$js_uri . '/bundles/core.min.js',
			array(),
			SKYYROSE_VERSION,
			array(
				'strategy'  => 'defer',
				'in_footer' => true,
			)
		);

		wp_register_script( 'skyyrose-footer-cro', false, array( 'skyyrose-navigation' ), SKYYROSE_VERSION, true );
		wp_enqueue_script( 'skyyrose-footer-cro' );
		wp_localize_script(
			'skyyrose-footer-cro',
			'skyyRoseFooterCro',
			array(
				'networkError' => __( 'Connection problem — please try again.', 'skyyrose' ),
			)
		);
	}

	if ( ! $js_bundled ) {
		// Navigation script (hamburger toggle, keyboard nav, dropdowns).
		$nav_file = $use_min && file_exists( $js_dir . '/navigation.min.js' ) ? 'navigation.min.js' : 'navigation.js';
		if ( file_exists( $js_dir . '/' . $nav_file ) ) {
			wp_enqueue_script(
				'skyyrose-navigation',
				$js_uri . '/' . $nav_file,
				array(),
				SKYYROSE_VERSION,
				array(
					'strategy'  => 'defer',
					'in_footer' => true,
				)
			);
		}

		// Toast notification utility (global, used by wishlist, add-to-cart, newsletter).
		$toast_file = $use_min && file_exists( $js_dir . '/toast.min.js' ) ? 'toast.min.js' : 'toast.js';
		if ( file_exists( $js_dir . '/' . $toast_file ) ) {
			wp_enqueue_script(
				'skyyrose-toast',
				$js_uri . '/' . $toast_file,
				array(),
				SKYYROSE_VERSION,
				array(
					'strategy'  => 'defer',
					'in_footer' => true,
				)
			);
		}

		// Footer CRO — FAQ accordion + animated newsletter capture.
		$fcro_file = $use_min && file_exists( $js_dir . '/footer-cro.min.js' ) ? 'footer-cro.min.js' : 'footer-cro.js';
		if ( file_exists( $js_dir . '/' . $fcro_file ) ) {
			wp_enqueue_script(
				'skyyrose-footer-cro',
				$js_uri . '/' . $fcro_file,
				array(),
				SKYYROSE_VERSION,
				array(
					'strategy'  => 'defer',
					'in_footer' => true,
				)
			);

			// The only client-originated newsletter string; server responses
			// arrive already localized from skyyrose_ajax_newsletter_subscribe().
			wp_localize_script(
				'skyyrose-footer-cro',
				'skyyRoseFooterCro',
				array(
					'networkError' => __( 'Connection problem — please try again.', 'skyyrose' ),
				)
			);
		}
	}

	// Motion One — vanilla JS animation library (same author as Framer Motion).
	// Self-hosted from assets/js/lib/ to eliminate jsDelivr CDN supply-chain risk.
	// Exposes window.Motion with animate(), scroll(), inView(), timeline().
	// Loaded with `defer` strategy: parsed in parallel with HTML, executed after
	// DOMContentLoaded. premium-interactions.js depends on it and self-defers.
	// v1.5.12: skip on lightweight slugs (cart/checkout/404/search) — saves ~65KB.
	if ( ! $skip_premium_js ) {
		wp_enqueue_script(
			'motion-one',
			SKYYROSE_ASSETS_URI . '/js/lib/motion.min.js',
			array(),
			'11',
			array(
				'strategy'  => 'defer',
				'in_footer' => true,
			)
		);

		// Premium interactions: parallax, split-text, magnetic, stagger, scroll-fade.
		$prem_js = $use_min && file_exists( $js_dir . '/premium-interactions.min.js' )
			? 'premium-interactions.min.js' : 'premium-interactions.js';
		if ( file_exists( $js_dir . '/' . $prem_js ) ) {
			wp_enqueue_script(
				'skyyrose-premium-interactions',
				$js_uri . '/' . $prem_js,
				array( 'motion-one' ),
				SKYYROSE_VERSION,
				array(
					'strategy'  => 'defer',
					'in_footer' => true,
				)
			);
		}
	}

	// Page transitions + skeleton screens + scarcity bars.
	// (In the JS core bundle when $js_bundled.)
	if ( ! $js_bundled ) {
		$pt_file = $use_min && file_exists( $js_dir . '/page-transitions.min.js' )
			? 'page-transitions.min.js' : 'page-transitions.js';
		if ( file_exists( $js_dir . '/' . $pt_file ) ) {
			wp_enqueue_script(
				'skyyrose-page-transitions',
				$js_uri . '/' . $pt_file,
				array(),
				SKYYROSE_VERSION,
				array(
					'strategy'  => 'defer',
					'in_footer' => true,
				)
			);
		}
	}

	// Comment reply script (WordPress built-in).
	if ( is_singular() && comments_open() && get_option( 'thread_comments' ) ) {
		wp_enqueue_script( 'comment-reply' );
	}

	// Skyy mascot JS — gated on the same kill switch as the CSS above. Loaded
	// via a tiny post-load idle bootstrap (mascot-loader.js) so the character
	// bundle never costs LCP/CLS/TBT budget: it only fetches mascot.min.js
	// (and skyy-3d.min.js, when a GLB is configured) after the window load
	// event + a genuine idle slot, or first interaction — whichever comes
	// first. Save-Data visitors get the 2D sprite path (mascot.js only).
	$mascot_js_enabled = skyyrose_mascot_is_enabled()
		&& ! ( function_exists( 'is_checkout' ) && is_checkout() );
	if ( $mascot_js_enabled ) {
		$loader_file = $use_min && file_exists( $js_dir . '/mascot-loader.min.js' ) ? 'mascot-loader.min.js' : 'mascot-loader.js';
		$mascot_file = $use_min && file_exists( $js_dir . '/mascot.min.js' ) ? 'mascot.min.js' : 'mascot.js';

		if ( file_exists( $js_dir . '/' . $loader_file ) && file_exists( $js_dir . '/' . $mascot_file ) ) {
			wp_enqueue_script(
				'skyyrose-mascot-loader',
				$js_uri . '/' . $loader_file,
				array(),
				SKYYROSE_VERSION,
				array(
					'strategy'  => 'defer',
					'in_footer' => true,
				)
			);

			$glb_url   = skyyrose_get_skyy_glb_url();
			$skyy3d_js = null;
			if ( ! empty( $glb_url ) ) {
				$skyy3d_file = $use_min && file_exists( $js_dir . '/skyy-3d.min.js' ) ? 'skyy-3d.min.js' : 'skyy-3d.js';
				if ( file_exists( $js_dir . '/' . $skyy3d_file ) ) {
					$skyy3d_js = add_query_arg( 'ver', SKYYROSE_VERSION, $js_uri . '/' . $skyy3d_file );
				}
			}

			// mascot.js / skyy-3d.js are injected client-side by the loader,
			// outside wp_enqueue_script — they get no automatic ?ver=. Without
			// an explicit ver param a CDN/Batcache keeps serving stale copies
			// after every SKYYROSE_VERSION bump.
			wp_localize_script(
				'skyyrose-mascot-loader',
				'SKYY_LOADER_CONFIG',
				array(
					'mascotUrl' => add_query_arg( 'ver', SKYYROSE_VERSION, $js_uri . '/' . $mascot_file ),
					'skyy3dUrl' => $skyy3d_js,
				)
			);

			$skyy_context = skyyrose_get_skyy_context();
			wp_localize_script(
				'skyyrose-mascot-loader',
				'SKYY_MASCOT_CONFIG',
				array(
					'pageTip'    => skyyrose_get_skyy_page_tip(),
					'llmEnabled' => (bool) get_theme_mod( 'skyyrose_mascot_llm_enabled', true ),
					'guideUrl'   => esc_url_raw( SKYYROSE_URI . '/data/site-guide.json' ),
				)
			);

			if ( $skyy3d_js ) {
				wp_localize_script(
					'skyyrose-mascot-loader',
					'SKYY_3D_CONFIG',
					array(
						// Cache-bust the GLB on version bump so a swapped skyy.glb is not
						// masked by the WP.com edge cache (the model URL is otherwise
						// unversioned). Safe: the Draco decoder path is DRACO_DECODER_PATH
						// (derived from assetsUri in skyy-3d.js), independent of MODEL_URL.
						'modelUrl' => esc_url_raw( add_query_arg( 'ver', SKYYROSE_VERSION, $glb_url ) ),
						'walkSide' => skyyrose_get_skyy_walk_side( $skyy_context ),
					)
				);
			}
		}
	}
}

/**
 * Localize script data for AJAX URLs, nonces, and theme URIs.
 *
 * @since 3.0.0
 * @return void
 */
function skyyrose_localize_scripts() {

	// navigation.js is always enqueued (see skyyrose_scripts); fall back to
	// jquery only as a last resort to ensure skyyRoseData is always available.
	$handle = 'skyyrose-navigation';
	if ( ! wp_script_is( $handle, 'enqueued' ) ) {
		wp_enqueue_script( 'jquery' );
		$handle = 'jquery';
	}

	wp_localize_script(
		$handle,
		'skyyRoseData',
		array(
			'ajaxUrl'   => admin_url( 'admin-ajax.php' ),
			'nonce'     => wp_create_nonce( 'skyyrose-nonce' ),
			'themeUri'  => SKYYROSE_URI,
			'assetsUri' => SKYYROSE_ASSETS_URI,
		)
	);
}

// Hook registration. Priority order: 5 fonts → 10 globals → 15 localize → 20 templates.
// Phase 2/3/4 + commercial polish (priorities 25/30/40/42) live in inc/enqueue-phases.php.
add_action( 'wp_enqueue_scripts', 'skyyrose_enqueue_local_fonts', 5 );
add_action( 'wp_enqueue_scripts', 'skyyrose_enqueue_global_styles', 10 );
add_action( 'wp_enqueue_scripts', 'skyyrose_enqueue_global_scripts', 10 );
add_action( 'wp_enqueue_scripts', 'skyyrose_localize_scripts', 15 );
// Note: skyyrose_admin_scripts() removed — assets/css/admin.css and
// assets/js/admin.js never existed, so this hook was a no-op on every
// wp-admin page load. (audit 2026-06-28)
