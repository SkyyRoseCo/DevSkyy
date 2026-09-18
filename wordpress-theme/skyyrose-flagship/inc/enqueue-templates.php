<?php
/**
 * Template Asset Routing
 *
 * Template slug detection and conditional CSS/JS loading.
 *
 * @package SkyyRose
 * @since   7.2.0
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Determine the current page template slug.
 *
 * Returns a normalized identifier that can be used for conditional enqueue.
 * Checks page template files, WooCommerce conditionals, and front-page.
 *
 * @since  3.0.0
 * @return string Template identifier slug (e.g., 'front-page', 'collection', 'about').
 */
function skyyrose_get_current_template_slug() {
	static $slug = null;
	if ( null !== $slug ) {
		return $slug;
	}

	$page_template = get_page_template_slug();

	if ( is_front_page() ) {
		$slug = 'front-page';
	} elseif ( is_404() ) {
		$slug = '404';
	} elseif ( 'size-guide' === get_query_var( 'skyyrose_virtual' ) ) {
		$slug = 'size-guide';
	} elseif ( is_page( 'collections' ) ) {
		// /collections/ index — page-collections.php via template hierarchy (WS2).
		$slug = 'collections-index';
	} elseif ( function_exists( 'is_product' ) && is_product() ) {
		$slug = 'single-product';
	} elseif ( function_exists( 'is_cart' ) && is_cart() ) {
		$slug = 'cart';
	} elseif ( function_exists( 'is_checkout' ) && is_checkout() ) {
		$slug = 'checkout';
	} elseif ( function_exists( 'is_account_page' ) && is_account_page() ) {
		$slug = 'account';
	} elseif ( function_exists( 'is_shop' ) && ( is_shop() || is_product_category() || is_product_tag() ) ) {
		$slug = 'shop-archive';
	} elseif ( ! empty( $page_template ) ) {
		$template_map = array(
			'template-collection-black-rose.php'   => 'collection-standalone',
			'template-collection-love-hurts.php'   => 'collection-standalone',
			'template-collection-signature.php'    => 'collection-standalone',
			'template-collection-kids-capsule.php' => ( function_exists( 'skyyrose_kc_is_launch_mode' ) && skyyrose_kc_is_launch_mode() ) ? 'kc-launch' : 'collection-standalone',
			'template-about.php'                   => 'about',
			'template-contact.php'                 => 'contact',
			'template-preorder-gateway.php'        => 'preorder-gateway',
			'template-faq.php'                     => 'faq',
			'template-shipping-returns.php'        => 'shipping-returns',
			'template-policy.php'                  => 'policy',
			'template-landing-black-rose.php'      => 'landing',
			'template-landing-love-hurts.php'      => 'landing',
			'template-landing-signature.php'       => 'landing',
			'template-landing-kids-capsule.php'    => 'landing',
			'template-collections-world.php'       => 'collections-world',
			'template-elementor-editorial.php'     => 'elementor-editorial',
			'template-elementor-canvas.php'        => 'elementor-canvas',
		);
		$slug         = isset( $template_map[ $page_template ] ) ? $template_map[ $page_template ] : null;
	}

	if ( null === $slug ) {
		if ( is_single() ) {
			$slug = 'single';
		} elseif ( is_search() ) {
			$slug = 'search';
		} elseif ( is_home() || is_archive() ) {
			$slug = 'blog';
		} elseif ( is_page() ) {
			$slug = 'page';
		} else {
			$slug = 'default';
		}
	}

	return $slug;
}

/**
 * Conditionally enqueue template-specific CSS.
 *
 * Only loads the stylesheet that matches the current page template.
 *
 * @since 3.0.0
 * @return void
 */
function skyyrose_enqueue_template_styles() {

	$slug         = skyyrose_get_current_template_slug();
	$base_css_uri = SKYYROSE_ASSETS_URI . '/css';
	$base_css_dir = SKYYROSE_DIR . '/assets/css';
	$global_deps  = array( 'skyyrose-design-tokens' );
	$use_min      = ! defined( 'SCRIPT_DEBUG' ) || ! SCRIPT_DEBUG;

	$template_styles = array(
		'front-page'          => 'storefront-home.css',
		'single-product'      => 'single-product.css',
		'cart'                => 'woocommerce.css',
		'checkout'            => 'woocommerce.css',
		'account'             => 'woocommerce.css',
		'shop-archive'        => 'woocommerce.css',
		'about'               => 'about.css',
		'contact'             => 'contact.css',
		'preorder-gateway'    => 'preorder-gateway.css',
		'404'                 => '404.css',
		'search'              => 'search-results.css',
		'faq'                 => 'info-pages.css',
		'shipping-returns'    => 'info-pages.css',
		'size-guide'          => 'info-pages.css',
		'policy'              => 'info-pages.css',
		'collections-index'   => 'collections-index.css',
		'landing'             => 'landing-scrollytell.css',
		'collections-world'   => 'scroll-world.css',
		'elementor-editorial' => 'landing-pages.css',
		'single'              => 'generic-pages.css',
		'blog'                => 'generic-pages.css',
		'page'                => 'generic-pages.css',
		'kc-launch'           => 'kids-capsule.css',
	);

	/*
	 * WooCommerce bundles: cart/checkout/account each load base
	 * woocommerce.css + one page-specific sheet, always together — bundled
	 * per slug (base first, same order the dependency chain produces) under
	 * the existing 'skyyrose-template-woocommerce' handle, so the script-side
	 * wp_script_is/localize in inc/woocommerce.php matches unchanged.
	 * shop-archive keeps the plain base sheet via the map below.
	 */
	$wc_bundles     = array(
		'cart'     => 'wc-cart',
		'checkout' => 'wc-checkout',
		'account'  => 'wc-account',
	);
	$wc_bundle_used = false;
	if ( isset( $wc_bundles[ $slug ] ) && $use_min
		&& file_exists( $base_css_dir . '/bundles/' . $wc_bundles[ $slug ] . '.min.css' ) ) {
		wp_enqueue_style(
			'skyyrose-template-woocommerce',
			$base_css_uri . '/bundles/' . $wc_bundles[ $slug ] . '.min.css',
			$global_deps,
			SKYYROSE_VERSION
		);
		$wc_bundle_used = true;
	}

	if ( ! $wc_bundle_used && isset( $template_styles[ $slug ] ) ) {
		$css_file = $template_styles[ $slug ];
		$handle   = 'skyyrose-template-' . sanitize_title( pathinfo( $css_file, PATHINFO_FILENAME ) );
		$min_file = str_replace( '.css', '.min.css', $css_file );

		// Prefer minified version in production.
		if ( $use_min && file_exists( $base_css_dir . '/' . $min_file ) ) {
			$css_file = $min_file;
		}

		if ( file_exists( $base_css_dir . '/' . $css_file ) ) {
			wp_enqueue_style(
				$handle,
				$base_css_uri . '/' . $css_file,
				$global_deps,
				SKYYROSE_VERSION
			);
		}
	}

	// Scroll-pinned brand-narrative styles — collection + landing templates.
	if ( in_array( $slug, array( 'collection-standalone', 'landing' ), true ) ) {
		$pin_css = $use_min && file_exists( $base_css_dir . '/pin-narrative.min.css' )
			? 'pin-narrative.min.css' : 'pin-narrative.css';
		if ( file_exists( $base_css_dir . '/' . $pin_css ) ) {
			wp_enqueue_style(
				'skyyrose-pin-narrative',
				$base_css_uri . '/' . $pin_css,
				array( 'skyyrose-design-tokens' ),
				SKYYROSE_VERSION
			);
		}
	}

	// Sticky-image feature scroll — collection pages (feature-scroll.php part).
	if ( 'collection-standalone' === $slug ) {
		$featscroll_css = $use_min && file_exists( $base_css_dir . '/collection-feature-scroll.min.css' )
			? 'collection-feature-scroll.min.css' : 'collection-feature-scroll.css';
		if ( file_exists( $base_css_dir . '/' . $featscroll_css ) ) {
			wp_enqueue_style(
				'skyyrose-collection-feature-scroll',
				$base_css_uri . '/' . $featscroll_css,
				array( 'skyyrose-design-tokens' ),
				SKYYROSE_VERSION
			);
		}
	}

	// Embedded experience layer (WS3): collection pages render the immersive
	// scene as their opening layer, so they need immersive.css too. The handle
	// uses the stable immersive handle so the scenes dependency below remains valid.
	if ( 'collection-standalone' === $slug ) {
		$immersive_css = $use_min && file_exists( $base_css_dir . '/immersive.min.css' )
			? 'immersive.min.css' : 'immersive.css';
		if ( file_exists( $base_css_dir . '/' . $immersive_css ) ) {
			wp_enqueue_style(
				'skyyrose-template-immersive',
				$base_css_uri . '/' . $immersive_css,
				$global_deps,
				SKYYROSE_VERSION
			);
		}
	}

	// Immersive scene images — overlays, tab bar, cinematic toggle, particles.
	if ( 'collection-standalone' === $slug ) {
		$scenes_file = $use_min && file_exists( $base_css_dir . '/immersive-scenes.min.css' )
			? 'immersive-scenes.min.css' : 'immersive-scenes.css';
		if ( file_exists( $base_css_dir . '/' . $scenes_file ) ) {
			wp_enqueue_style(
				'skyyrose-immersive-scenes',
				$base_css_uri . '/' . $scenes_file,
				array( 'skyyrose-template-immersive' ),
				SKYYROSE_VERSION
			);
		}
	}

	// Customer Enhancements — Fit Notes (PDP), Drop Block (homepage), Sticky ATC (editorial PDP).
	// Both slugs render CE components; no other templates use this stylesheet.
	if ( in_array( $slug, array( 'single-product', 'front-page' ), true ) ) {
		$ce_css = $use_min && file_exists( $base_css_dir . '/customer-enhancements.min.css' )
			? 'customer-enhancements.min.css' : 'customer-enhancements.css';
		if ( file_exists( $base_css_dir . '/' . $ce_css ) ) {
			wp_enqueue_style(
				'skyyrose-customer-enhancements',
				$base_css_uri . '/' . $ce_css,
				array( 'skyyrose-design-tokens' ),
				SKYYROSE_VERSION
			);
		}
	}

	if ( 'front-page' === $slug ) {
		/*
		 * LCP: the homepage-v3 hero is a portrait <video> whose poster frame is
		 * the paint. A poster attribute is NOT preload-scanner discoverable, so
		 * without this the browser only requests it after CSS + layout.
		 *
		 * PAIRING CONTRACT with template-parts/home/hero.php: the same file,
		 * assets/images/hero/home-hero-poster-720w.webp, byte-for-byte the same
		 * URL string, and no imagesizes (the poster is a single fixed asset, not
		 * a srcset) — any drift and the browser fetches a second candidate.
		 *
		 * The v2 preloads that used to live here (homepage-hero-bg + the br-006
		 * hero-strip frame) are retired with the elements they paired with;
		 * neither asset appears on the v3 page.
		 */
		add_action(
			'wp_head',
			function () {
				$poster = SKYYROSE_ASSETS_URI . '/images/hero/home-hero-poster-720w.webp';
				echo '<link rel="preload" as="image" href="' . esc_url( $poster ) . '" type="image/webp" fetchpriority="high">' . "\n"; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
			},
			2
		);
	}

	// Collections World LCP: the bare-canvas template has no server-rendered <img> —
	// the engine injects the hero poster via JS — so preload scene 1's still at high
	// priority, else first paint waits on script fetch->parse->exec before the image
	// is even requested.
	if ( 'collections-world' === $slug && function_exists( 'skyyrose_get_collections_world_config' ) ) {
		$sw_cfg  = skyyrose_get_collections_world_config();
		$sw_hero = isset( $sw_cfg['sections'][0]['still'] ) ? $sw_cfg['sections'][0]['still'] : '';
		if ( $sw_hero ) {
			// Match the engine's <img srcset> exactly (same Photon URLs + 100vw
			// sizes) or the preload and the element fetch different files and the
			// LCP double-downloads. Flat webp preload only when Photon is unusable.
			// No type= on the srcset branch — Photon may transcode for the client.
			$sw_set = isset( $sw_cfg['sections'][0]['stillSet'] ) ? $sw_cfg['sections'][0]['stillSet'] : '';
			add_action(
				'wp_head',
				function () use ( $sw_hero, $sw_set ) {
					if ( '' !== $sw_set ) {
						echo '<link rel="preload" as="image" imagesrcset="' . esc_attr( $sw_set ) . '" imagesizes="100vw" fetchpriority="high">' . "\n"; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
					} else {
						echo '<link rel="preload" as="image" href="' . esc_url( $sw_hero ) . '" type="image/webp" fetchpriority="high">' . "\n"; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
					}
				},
				2
			);
		}
	}

	// Unified collection page CSS + cross-collection View Transitions choreography.
	if ( 'collection-standalone' === $slug ) {
		skyyrose_enqueue_collection_styles( $base_css_dir, $base_css_uri, $use_min, $global_deps );
	}

	// Product grid bento layout — landing pages, preorder gateway, and
	// collection pages (their shared product-grid part renders
	// .product-grid__items, which lays out as full-width stacked blocks
	// without this stylesheet — bug-112).
	if ( in_array( $slug, array( 'front-page', 'landing', 'elementor-editorial', 'preorder-gateway', 'collection-standalone' ), true ) ) {
		$grid_css = $use_min && file_exists( $base_css_dir . '/product-grid.min.css' )
			? 'product-grid.min.css' : 'product-grid.css';
		if ( file_exists( $base_css_dir . '/' . $grid_css ) ) {
			wp_enqueue_style(
				'skyyrose-product-grid',
				$base_css_uri . '/' . $grid_css,
				array( 'skyyrose-design-tokens' ),
				SKYYROSE_VERSION
			);
		}
	}

	// WooCommerce page-specific CSS (loaded ON TOP of the base woocommerce.css).
	$woo_page_styles = array(
		// single-product.css is the primary stylesheet (replaces woocommerce-single.css).
		'cart'     => 'woocommerce-cart.css',
		'checkout' => 'woocommerce-checkout.css',
		'account'  => 'woocommerce-account.css',
	);

	if ( ! $wc_bundle_used && isset( $woo_page_styles[ $slug ] ) ) {
		$woo_file   = $woo_page_styles[ $slug ];
		$woo_handle = 'skyyrose-' . sanitize_title( pathinfo( $woo_file, PATHINFO_FILENAME ) );
		$woo_min    = str_replace( '.css', '.min.css', $woo_file );

		// Prefer minified version in production.
		if ( $use_min && file_exists( $base_css_dir . '/' . $woo_min ) ) {
			$woo_file = $woo_min;
		}

		if ( file_exists( $base_css_dir . '/' . $woo_file ) ) {
			wp_enqueue_style(
				$woo_handle,
				$base_css_uri . '/' . $woo_file,
				array( 'skyyrose-template-woocommerce' ),
				SKYYROSE_VERSION
			);
		}
	}
}

/**
 * Conditionally enqueue template-specific JS.
 *
 * Only loads the script that matches the current page template.
 *
 * @since 3.0.0
 * @return void
 */
function skyyrose_enqueue_template_scripts() {

	$slug         = skyyrose_get_current_template_slug();
	$base_js_uri  = SKYYROSE_ASSETS_URI . '/js';
	$base_js_dir  = SKYYROSE_DIR . '/assets/js';
	$base_css_uri = SKYYROSE_ASSETS_URI . '/css';
	$base_css_dir = SKYYROSE_DIR . '/assets/css';
	$use_min      = ! defined( 'SCRIPT_DEBUG' ) || ! SCRIPT_DEBUG;

	// Luxury cursor — dot follower (desktop only, self-disables on touch/mobile).
	// CURS-03: pages that also load the immersive-core 3D engine (preorder-gateway,
	// collection-standalone — see the immersive-core in_array() below) hide the
	// cursor so it doesn't compete with the scene. These are the successors to the
	// four template-immersive-*.php rooms retired in 2.2.2.
	// Also skip wherever luxury-cursor.css is skipped: the script builds a .cursor-label
	// span, which without its stylesheet renders as stray visible text in the page flow.
	$hides_cursor_for_scene = in_array( $slug, array( 'preorder-gateway', 'collection-standalone' ), true );
	if ( ! skyyrose_slug_skips_optional_assets( $slug ) && ! $hides_cursor_for_scene ) {
		$cursor_file = $use_min && file_exists( $base_js_dir . '/luxury-cursor.min.js' ) ? 'luxury-cursor.min.js' : 'luxury-cursor.js';
		if ( file_exists( $base_js_dir . '/' . $cursor_file ) ) {
			wp_enqueue_script(
				'skyyrose-luxury-cursor',
				$base_js_uri . '/' . $cursor_file,
				array(),
				SKYYROSE_VERSION,
				true
			);
		}
	}

	// Landing pages JS — split scrollytell (IntersectionObserver scroll-sync, no GSAP).
	if ( 'landing' === $slug ) {
		$lp_js = $use_min && file_exists( $base_js_dir . '/landing-scrollytell.min.js' )
			? 'landing-scrollytell.min.js' : 'landing-scrollytell.js';
		if ( file_exists( $base_js_dir . '/' . $lp_js ) ) {
			wp_enqueue_script(
				'skyyrose-landing-scrollytell',
				$base_js_uri . '/' . $lp_js,
				array(),
				SKYYROSE_VERSION,
				true
			);
			wp_localize_script(
				'skyyrose-landing-scrollytell',
				'skyyRoseData',
				array(
					'ajaxUrl' => admin_url( 'admin-ajax.php' ),
					'nonce'   => wp_create_nonce( 'skyyrose_newsletter' ),
				)
			);
		}
	}

	// Collections World — full-bleed scroll-scrubbed camera fly-through.
	// Vanilla engine (no GSAP); config from skyyrose_get_collections_world_config().
	if ( 'collections-world' === $slug ) {
		$sw_js = $use_min && file_exists( $base_js_dir . '/scroll-world.min.js' )
			? 'scroll-world.min.js' : 'scroll-world.js';
		if ( file_exists( $base_js_dir . '/' . $sw_js ) ) {
			wp_enqueue_script(
				'skyyrose-scroll-world',
				$base_js_uri . '/' . $sw_js,
				array(),
				SKYYROSE_VERSION,
				array(
					'strategy'  => 'defer',
					'in_footer' => true,
				)
			);
			if ( function_exists( 'skyyrose_get_collections_world_config' ) ) {
				// wp_localize_script() coerces every TOP-LEVEL scalar to a string
				// (diveScroll 1.4 -> "1.4"), which corrupts the engine's scroll math and
				// freezes the fly-through. wp_add_inline_script() + wp_json_encode()
				// preserves native numeric/boolean types.
				wp_add_inline_script(
					'skyyrose-scroll-world',
					'window.SKYY_SCROLL_WORLD_CONFIG = ' . wp_json_encode(
						skyyrose_get_collections_world_config(),
						JSON_HEX_TAG | JSON_UNESCAPED_SLASHES
					) . ';',
					'before'
				);
			}
		}
	}

	// Elementor editorial templates keep the legacy landing-pages layout + JS.
	if ( 'elementor-editorial' === $slug ) {
		$lp_legacy_js = $use_min && file_exists( $base_js_dir . '/landing-pages.min.js' )
			? 'landing-pages.min.js' : 'landing-pages.js';
		if ( file_exists( $base_js_dir . '/' . $lp_legacy_js ) ) {
			wp_enqueue_script(
				'skyyrose-landing-pages',
				$base_js_uri . '/' . $lp_legacy_js,
				array(),
				SKYYROSE_VERSION,
				true
			);
		}
	}

	// Collection pages JS — IntersectionObserver scroll-reveal (no GSAP dependency).
	if ( 'collection-standalone' === $slug ) {
		$col_js = $use_min && file_exists( $base_js_dir . '/collection-pages.min.js' )
			? 'collection-pages.min.js' : 'collection-pages.js';
		if ( file_exists( $base_js_dir . '/' . $col_js ) ) {
			wp_enqueue_script(
				'skyyrose-collection-pages',
				$base_js_uri . '/' . $col_js,
				array(),
				SKYYROSE_VERSION,
				true
			);
			wp_localize_script(
				'skyyrose-collection-pages',
				'skyyRoseNewsletter',
				array(
					'ajaxUrl' => admin_url( 'admin-ajax.php' ),
					'nonce'   => wp_create_nonce( 'skyyrose_newsletter' ),
				)
			);
		}

		// Collection motion identity JS — Black Rose tilt/glare, Love Hurts
		// ink drops, Kids Capsule bounce field + add-to-cart confetti.
		// Vanilla and self-gating (reduced-motion / touch); deferred so its
		// evaluation stays out of the FCP→LCP window (Wave 7b doctrine).
		$motion_js = $use_min && file_exists( $base_js_dir . '/collection-motion.min.js' )
			? 'collection-motion.min.js' : 'collection-motion.js';
		if ( file_exists( $base_js_dir . '/' . $motion_js ) ) {
			wp_enqueue_script(
				'skyyrose-collection-motion',
				$base_js_uri . '/' . $motion_js,
				array(),
				SKYYROSE_VERSION,
				array(
					'strategy'  => 'defer',
					'in_footer' => true,
				)
			);
		}
	}

	// GSAP — self-hosted from assets/js/lib/ so animations don't depend on
	// Cloudflare CDN reachability. Loaded on pages that use scroll animations
	// (NOT collection pages — they use IntersectionObserver).
	// 'about' removed in 1.5.8: about.js uses prefers-reduced-motion query only,
	// no gsap/ScrollTrigger API calls (audit: grep returns 0 hits). Was shipping
	// 114KB of dead lib bytes to every About visitor.
	// collection-standalone removed (Wave 7b): on collection pages gsap +
	// ScrollTrigger + the engines are injected post-load / on-interaction by
	// collection-motion-loader.js — their eval was the dominant col-hero
	// render delay (round-6). Everything they power is below the 100vh hero.
	$gsap_slugs = array( 'preorder-gateway', 'kc-launch' );
	if ( in_array( $slug, $gsap_slugs, true ) ) {
		wp_enqueue_script( 'skyyrose-gsap', SKYYROSE_ASSETS_URI . '/js/lib/gsap.min.js', array(), '3.12.2', true );
	}

	// ScrollTrigger — only on slugs whose scripts call the ScrollTrigger API.
	// Immersive rooms animate via gsap.timeline/fromTo/set only (immersive-core.js
	// + immersive.js, 0 ScrollTrigger refs), so shipping ScrollTrigger there was
	// ~40KB of dead main-thread parse during the scene intro. preorder-gateway.js
	// (5 refs), kids-capsule-launch.js (3 refs), and collection-feature-scroll.js
	// (sticky feature section) genuinely use it.
	$gsap_st_slugs = array( 'preorder-gateway', 'kc-launch' );
	if ( in_array( $slug, $gsap_st_slugs, true ) ) {
		wp_enqueue_script( 'skyyrose-gsap-st', SKYYROSE_ASSETS_URI . '/js/lib/ScrollTrigger.min.js', array( 'skyyrose-gsap' ), '3.12.2', true );
	}

	// Sticky-image feature scroll (collection pages) — moved into the
	// collection-motion-loader chain (Wave 7b) so its evaluation joins gsap/
	// ScrollTrigger outside the FCP→LCP window. The section it drives is
	// below the 100vh hero; the script self-inits on injection.

	// Phase 2 — Lenis smooth-scroll lib: preorder gateway only.
	// Immersive rooms are 100vh/overflow:hidden (nothing to scroll) — no dead bytes.
	// Enqueued before the immersive-core block so window.Lenis is defined when
	// initLenis() runs. cf. CURS-03 lesson: slug-gated to avoid waste on other templates.
	if ( 'preorder-gateway' === $slug && file_exists( $base_js_dir . '/lib/lenis.min.js' ) ) {
		wp_enqueue_script(
			'skyyrose-lenis',
			$base_js_uri . '/lib/lenis.min.js',
			array(),    // Lenis itself has no WP deps.
			'1.3.23',
			true
		);
	}

	// Phase 1+2 — Immersive Core: scene intro, lockup, dust canvas, Lenis init, warp.
	// Loaded on: immersive rooms (4×) + preorder gateway + collection pages
	// (embedded experience layer, WS3).
	if ( in_array( $slug, array( 'preorder-gateway', 'collection-standalone' ), true ) ) {
		$ic_css = $use_min && file_exists( $base_css_dir . '/system/immersive-core.min.css' )
			? 'system/immersive-core.min.css' : 'system/immersive-core.css';
		if ( file_exists( $base_css_dir . '/' . $ic_css ) ) {
			wp_enqueue_style(
				'skyyrose-immersive-core',
				$base_css_uri . '/' . $ic_css,
				array( 'skyyrose-design-tokens' ),
				SKYYROSE_VERSION
			);
		}

		// On preorder, add lenis as a dep so WP prints it before immersive-core.
		// On immersive rooms lenis is not enqueued — omit it from deps there.
		// On collection pages the JS ships via collection-motion-loader instead
		// (Wave 7b) — the embedded scene is below the hero, so its engine may
		// not evaluate inside the FCP→LCP window. CSS above still enqueues
		// (async-swapped for collection by skyyrose_async_noncritical_styles).
		if ( 'collection-standalone' !== $slug ) {
			$ic_js_deps = array( 'skyyrose-gsap' );
			if ( wp_script_is( 'skyyrose-lenis', 'enqueued' ) ) {
				$ic_js_deps[] = 'skyyrose-lenis';
			}

			$ic_js = $use_min && file_exists( $base_js_dir . '/system/immersive-core.min.js' )
				? 'system/immersive-core.min.js' : 'system/immersive-core.js';
			if ( file_exists( $base_js_dir . '/' . $ic_js ) ) {
				wp_enqueue_script(
					'skyyrose-immersive-core',
					$base_js_uri . '/' . $ic_js,
					// GSAP core + optional lenis dep (preorder only).
					// immersive-core uses gsap.timeline/fromTo/set, not ScrollTrigger API.
					$ic_js_deps,
					SKYYROSE_VERSION,
					true
				);
			}
		}
	}

	/*
	 * No 'front-page' entry: front-page.php inlines homepage-v3(.min).js and
	 * kc-mascot(.min).js itself, because the host's page-optimize plugin strips
	 * separately enqueued homepage scripts. The v2 map still listed
	 * the retired homepage script here alongside that inline block, so it shipped
	 * the same file twice — fixed with the v3 cutover.
	 */
	$template_scripts = array(
		'single-product'   => 'single-product.js',
		'cart'             => 'woocommerce.js',
		'checkout'         => 'woocommerce.js',
		'contact'          => 'contact.js',
		'preorder-gateway' => 'preorder-gateway.js',
		'about'            => 'about.js',
		'kc-launch'        => 'kids-capsule-launch.js',
	);

	if ( isset( $template_scripts[ $slug ] ) ) {
		$js_file = $template_scripts[ $slug ];
		$handle  = 'skyyrose-template-' . sanitize_title( pathinfo( $js_file, PATHINFO_FILENAME ) );

		// WooCommerce + single-product JS depend on jQuery for cart/gallery interactions.
		$wc_js_files = array( 'woocommerce.js', 'single-product.js' );
		$js_deps     = in_array( $js_file, $wc_js_files, true ) ? array( 'jquery', 'wc-add-to-cart-variation' ) : array();

		// Prefer minified version in production.
		$min_file = str_replace( '.js', '.min.js', $js_file );
		if ( $use_min && file_exists( $base_js_dir . '/' . $min_file ) ) {
			$js_file = $min_file;
		}

		if ( file_exists( $base_js_dir . '/' . $js_file ) ) {
			wp_enqueue_script(
				$handle,
				$base_js_uri . '/' . $js_file,
				$js_deps,
				SKYYROSE_VERSION,
				true
			);
		}

		// Localize preorder gateway with WooCommerce cart sync data.
		if ( 'preorder-gateway' === $slug && wp_script_is( $handle, 'enqueued' ) ) {
			wp_localize_script(
				$handle,
				'skyyRoseGateway',
				array(
					'ajaxUrl'     => admin_url( 'admin-ajax.php' ),
					'nonce'       => wp_create_nonce( 'skyyrose-immersive-nonce' ),
					'wcActive'    => class_exists( 'WooCommerce' ),
					'checkoutUrl' => function_exists( 'wc_get_checkout_url' ) ? wc_get_checkout_url() : home_url( '/checkout/' ),
					'cartUrl'     => function_exists( 'wc_get_cart_url' ) ? wc_get_cart_url() : home_url( '/cart/' ),
					'i18n'        => array(
						'item'  => __( 'item', 'skyyrose' ),
						'items' => __( 'items', 'skyyrose' ),
					),
				)
			);
		}

		// "Complete the Look" cross-sell removed 2026-05-27 per founder canon.
		// Enqueue, template, function, and hook all retired in the same commit.

	}

	/*
	 * PDP 3D viewer (WS3): early-in-head path for the theme's own product
	 * template. skyyrose_woocommerce_3d_model_button() enqueues the same
	 * script (idempotently) right before it prints, which also covers product
	 * views this slug check never sees — [product_page] shortcodes and any
	 * woocommerce_single_product_summary render. Policy + enqueue live in
	 * inc/product-3d-model.php; nothing 3D is fetched before the first click.
	 */
	if ( 'single-product' === $slug && is_singular( 'product' )
		&& '' !== skyyrose_get_product_3d_model_url( get_queried_object_id() ) ) {
		skyyrose_enqueue_product_3d_viewer();
	}

	// Embedded experience layer (WS3): collection pages ship gsap +
	// ScrollTrigger + immersive-core + feature-scroll + immersive engine +
	// WC bridge via collection-motion-loader.js (Wave 7b) — injected in order
	// on first interaction or 8s after load, so their ~2.9s evaluation
	// (round-6 bootup-time) cannot land inside the FCP→LCP window. All chain
	// scripts self-init when readyState is already complete.
	if ( 'collection-standalone' === $slug ) {
		$motion_loader = $use_min && file_exists( $base_js_dir . '/collection-motion-loader.min.js' )
			? 'collection-motion-loader.min.js' : 'collection-motion-loader.js';
		if ( file_exists( $base_js_dir . '/' . $motion_loader ) ) {
			wp_enqueue_script(
				'skyyrose-collection-motion-loader',
				$base_js_uri . '/' . $motion_loader,
				array(),
				SKYYROSE_VERSION,
				array(
					'strategy'  => 'defer',
					'in_footer' => true,
				)
			);

			// Ordered chain — gsap must precede ScrollTrigger, which must
			// precede the engines. Explicit ?ver params: these URLs bypass
			// wp_enqueue_script, so without them Batcache/CDN would pin
			// stale copies across version bumps (round-6 lesson).
			$motion_chain   = array();
			$motion_chain[] = add_query_arg( 'ver', '3.12.2', SKYYROSE_ASSETS_URI . '/js/lib/gsap.min.js' );
			$motion_chain[] = add_query_arg( 'ver', '3.12.2', SKYYROSE_ASSETS_URI . '/js/lib/ScrollTrigger.min.js' );

			$ic_chain_js = $use_min && file_exists( $base_js_dir . '/system/immersive-core.min.js' )
				? 'system/immersive-core.min.js' : 'system/immersive-core.js';
			if ( file_exists( $base_js_dir . '/' . $ic_chain_js ) ) {
				$motion_chain[] = add_query_arg( 'ver', SKYYROSE_VERSION, $base_js_uri . '/' . $ic_chain_js );
			}

			$featscroll_js = $use_min && file_exists( $base_js_dir . '/collection-feature-scroll.min.js' )
				? 'collection-feature-scroll.min.js' : 'collection-feature-scroll.js';
			if ( file_exists( $base_js_dir . '/' . $featscroll_js ) ) {
				$motion_chain[] = add_query_arg( 'ver', SKYYROSE_VERSION, $base_js_uri . '/' . $featscroll_js );
			}

			$immersive_js = $use_min && file_exists( $base_js_dir . '/immersive.min.js' )
				? 'immersive.min.js' : 'immersive.js';
			if ( file_exists( $base_js_dir . '/' . $immersive_js ) ) {
				$motion_chain[] = add_query_arg( 'ver', SKYYROSE_VERSION, $base_js_uri . '/' . $immersive_js );
			}

			$bridge_file = $use_min && file_exists( $base_js_dir . '/immersive-wc-bridge.min.js' )
				? 'immersive-wc-bridge.min.js' : 'immersive-wc-bridge.js';
			if ( file_exists( $base_js_dir . '/' . $bridge_file ) ) {
				$motion_chain[] = add_query_arg( 'ver', SKYYROSE_VERSION, $base_js_uri . '/' . $bridge_file );
			}

			wp_localize_script(
				'skyyrose-collection-motion-loader',
				'SKYY_MOTION_CONFIG',
				array( 'scripts' => $motion_chain )
			);

			// immersive.js + the WC bridge read this shared runtime payload.
			wp_localize_script(
				'skyyrose-collection-motion-loader',
				'skyyRoseImmersive',
				array(
					'ajaxUrl'  => admin_url( 'admin-ajax.php' ),
					'nonce'    => wp_create_nonce( 'skyyrose-immersive-nonce' ),
					'wcActive' => class_exists( 'WooCommerce' ),
					'cartUrl'  => function_exists( 'wc_get_cart_url' ) ? wc_get_cart_url() : home_url( '/cart/' ),
				)
			);
		}
	}

	// WooCommerce AJAX add-to-cart on custom (non-WC-native) templates.
	// WC_Frontend_Scripts::register_scripts() always registers 'wc-add-to-cart'
	// on every frontend pageload, but WooCommerce only ENQUEUES it sitewide when
	// the "Enable AJAX add to cart" setting is on — enqueue never depends on page
	// type. Our custom templates render .ajax_add_to_cart buttons (Reserve on
	// preorder-gateway, Quick Add on v7 cards via product-grid.php) outside any
	// WooCommerce-native page, so the click would just follow the PDP fallback
	// href with JS enabled and no AJAX add. Enqueuing the already-registered
	// handle here is enough: WC's own localize_printed_scripts() (wp_print_scripts
	// / wp_print_footer_scripts, priority 5) attaches wc_add_to_cart_params to any
	// handle it finds enqueued at print time, regardless of who enqueued it.
	$ajax_add_to_cart_slugs = array( 'front-page', 'collection-standalone', 'preorder-gateway' );
	if ( class_exists( 'WooCommerce' ) && in_array( $slug, $ajax_add_to_cart_slugs, true ) && wp_script_is( 'wc-add-to-cart', 'registered' ) ) {
		wp_enqueue_script( 'wc-add-to-cart' );
	}

	// Holo product cards — loaded on collection pages, shop archives, and WC loop.
	// NOTE: This must be OUTSIDE the $template_scripts check above.
	if ( in_array( $slug, array( 'collection-standalone', 'front-page', 'shop-archive', 'preorder-gateway', 'search', 'landing', 'elementor-editorial', 'single-product' ), true ) ) {
			$holo_css_file = $use_min && file_exists( $base_css_dir . '/product-card-holo.min.css' )
				? 'product-card-holo.min.css' : 'product-card-holo.css';
		if ( file_exists( $base_css_dir . '/' . $holo_css_file ) ) {
			wp_enqueue_style(
				'skyyrose-product-card-holo',
				$base_css_uri . '/' . $holo_css_file,
				array( 'skyyrose-design-tokens' ),
				SKYYROSE_VERSION
			);
		}
			$holo_js_file = $use_min && file_exists( $base_js_dir . '/product-card-holo.min.js' )
				? 'product-card-holo.min.js' : 'product-card-holo.js';
		if ( file_exists( $base_js_dir . '/' . $holo_js_file ) ) {
			wp_enqueue_script(
				'skyyrose-product-card-holo',
				$base_js_uri . '/' . $holo_js_file,
				array(),
				SKYYROSE_VERSION,
				true
			);
		}
	}
}


add_action( 'wp_enqueue_scripts', 'skyyrose_enqueue_template_styles', 20 );
add_action( 'wp_enqueue_scripts', 'skyyrose_enqueue_template_scripts', 20 );
