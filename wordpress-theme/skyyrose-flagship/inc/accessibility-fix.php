<?php
/**
 * SkyyRose Accessibility Fix (Theme Include)
 *
 * Fixes all Ally/WCAG accessibility and HTML validation errors site-wide.
 * Originally a standalone plugin; integrated into the theme as an inc/ module.
 *
 * Version: 3.0.0
 * Requires PHP: 7.4
 *
 * V3: ALL fixes applied via output buffer — no dependency on wp_head,
 * wp_body_open, or any theme hooks. Works on WordPress.com atomic.
 *
 * @package SkyyRose
 * @since   6.4.0
 */
defined( 'ABSPATH' ) || exit;

// Guard: skip if the standalone plugin already loaded this class.
if ( class_exists( 'SkyyRose_Accessibility_Fix' ) ) {
	return;
}

class SkyyRose_Accessibility_Fix {

	public function __construct() {
		add_action( 'template_redirect', array( $this, 'start_buffer' ) );
		add_action( 'wp_enqueue_scripts', array( $this, 'deduplicate_styles' ), 999 );
	}

	public function deduplicate_styles() {
		global $wp_styles;
		if ( ! $wp_styles || empty( $wp_styles->registered ) ) {
			return;
		}

		$seen  = array();
		$dupes = array();
		foreach ( $wp_styles->queue as $handle ) {
			if ( ! isset( $wp_styles->registered[ $handle ] ) ) {
				continue;
			}
			$src = $wp_styles->registered[ $handle ]->src;
			if ( ! $src ) {
				continue;
			}
			$clean = preg_replace( '/\?.*$/', '', $src );
			if ( isset( $seen[ $clean ] ) ) {
				$dupes[] = $handle;
			} else {
				$seen[ $clean ] = $handle;
			}
		}
		foreach ( $dupes as $h ) {
			wp_dequeue_style( $h );
			wp_deregister_style( $h );
		}
	}

	public function start_buffer() {
		ob_start( array( $this, 'process' ) );
	}

	public function process( $html ) {
		if ( empty( $html ) || strlen( $html ) < 200 ) {
			return $html;
		}

		// ══════════════════════════════════════════════
		// 1. INJECT SCREEN-READER-TEXT CSS
		// ══════════════════════════════════════════════
		// header.php renders the canonical skip-link (.skip-link → #content).
		// Do not inject a second one — duplicate skip links confuse AT.
		// Keep the .screen-reader-text utility class for use across templates.
		$css = '<style id="skyyrose-a11y-fix-v3">'
			. '.screen-reader-text{position:absolute!important;width:1px!important;height:1px!important;padding:0!important;margin:-1px!important;overflow:hidden!important;clip:rect(0,0,0,0)!important;white-space:nowrap!important;border:0!important}'
			. '</style>';

		$html = str_replace( '</head>', $css . "\n</head>", $html );

		// ══════════════════════════════════════════════
		// 2. BUTTONS: add type="button"
		// ══════════════════════════════════════════════
		$html = preg_replace_callback(
			'/<button\b((?:(?!type\s*=)[^>])*)>/is',
			function ( $m ) {
				return '<button type="button"' . $m[1] . '>'; },
			$html
		);

		// ══════════════════════════════════════════════
		// 3. DEDUPLICATE ALL IDs (whitespace-safe)
		// ══════════════════════════════════════════════
		$seen_ids = array();
		$html     = preg_replace_callback(
			'/(\s)id="([^"]+)"/',
			function ( $m ) use ( &$seen_ids ) {
				$id = $m[2];
				if ( ! isset( $seen_ids[ $id ] ) ) {
					$seen_ids[ $id ] = 1;
					return $m[0]; }
				$seen_ids[ $id ]++;
				return $m[1] . 'id="' . $id . '--' . $seen_ids[ $id ] . '"';
			},
			$html
		);

		// ══════════════════════════════════════════════
		// 4. EMPTY HEADINGS (multiline-safe)
		// ══════════════════════════════════════════════
		$html = preg_replace(
			'/<h3(\s[^>]*class="col-modal__name"[^>]*)>\s*<\/h3>/is',
			'<h3$1 aria-hidden="true"><span class="screen-reader-text">Product Details</span></h3>',
			$html
		);
		$html = preg_replace(
			'/<(h[2-6])(\s[^>]*class="jp-carousel[^"]*"[^>]*)>\s*<\/\1>/is',
			'<$1$2 aria-hidden="true"><span class="screen-reader-text">Media</span></$1>',
			$html
		);

		// ══════════════════════════════════════════════
		// 5. aria-hidden FOCUSABLE: add tabindex="-1"
		// ══════════════════════════════════════════════
		$html = preg_replace_callback(
			'/<(a|button|input)\b([^>]*?)aria-hidden\s*=\s*"true"([^>]*)>/is',
			function ( $m ) {
				if ( stripos( $m[2] . $m[3], 'tabindex=' ) !== false ) {
					return $m[0];
				}
				return '<' . $m[1] . $m[2] . 'aria-hidden="true" tabindex="-1"' . $m[3] . '>';
			},
			$html
		);

		// ══════════════════════════════════════════════
		// 6. EMPTY LINKS: add aria-label
		// ══════════════════════════════════════════════
		$html = preg_replace_callback(
			'/<a\b([^>]*?)>\s*<\/a>/is',
			function ( $m ) {
				if ( stripos( $m[1], 'aria-label' ) !== false ) {
					return $m[0];
				}
				preg_match( '/href="([^"]*)"/', $m[1], $h );
				$href  = isset( $h[1] ) ? $h[1] : '';
				$label = 'Link';
				if ( strpos( $href, 'cart' ) !== false ) {
					$label = 'View cart';
				} elseif ( strpos( $href, 'wishlist' ) !== false ) {
					$label = 'View wishlist';
				} elseif ( strpos( $href, 'account' ) !== false ) {
					$label = 'My account';
				} elseif ( strpos( $href, 'shop' ) !== false ) {
					$label = 'Shop';
				}
				return '<a' . $m[1] . ' aria-label="' . esc_attr( $label ) . '"></a>';
			},
			$html
		);

		// ══════════════════════════════════════════════
		// 7. UNLABELED RADIO INPUTS (multiline-safe)
		// ══════════════════════════════════════════════
		$html = preg_replace_callback(
			'/<input\b([^>]*?)type\s*=\s*"radio"([^>]*?)>/is',
			function ( $m ) {
				$combined = $m[1] . $m[2];
				if ( stripos( $combined, 'aria-label' ) !== false ) {
					return $m[0];
				}
				if ( preg_match( '/\bid\s*=\s*"/', $combined ) ) {
					return $m[0];
				}
				preg_match( '/value\s*=\s*"([^"]*)"/', $combined, $v );
				$val = isset( $v[1] ) ? $v[1] : 'Option';
				return '<input aria-label="' . esc_attr( $val ) . '"' . $m[1] . 'type="radio"' . $m[2] . '>';
			},
			$html
		);

		// ══════════════════════════════════════════════
		// Legacy search overlays predate header.php's explicit label and input ID.
		// Preserve current labels; repair only the old, unbound overlay input.
		$html = preg_replace_callback(
			'/<input\b((?:"[^"]*"|\'[^\']*\'|[^\'">])*)>/is',
			function ( $m ) {
				preg_match_all(
					'/(?:^|\s)([a-z_:][a-z0-9_:.-]*)(?:\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s"\'=<>`]+)))?/i',
					$m[1],
					$matches,
					PREG_SET_ORDER | PREG_UNMATCHED_AS_NULL
				);
				$attributes = array();
				foreach ( $matches as $attribute ) {
					$attributes[ strtolower( $attribute[1] ) ] = $attribute[2] ?? $attribute[3] ?? $attribute[4] ?? '';
				}
				$classes = preg_split( '/\s+/', trim( $attributes['class'] ?? '' ) );
				if ( ! in_array( 'search-overlay__input', $classes, true )
					|| isset( $attributes['id'] ) || isset( $attributes['aria-label'] ) || isset( $attributes['aria-labelledby'] ) ) {
					return $m[0];
				}
				return '<input aria-label="' . esc_attr__( 'Search the collection', 'skyyrose' ) . '"' . $m[1] . '>';
			},
			$html
		);

		// 8. LAZY LOAD below-fold images
		// ══════════════════════════════════════════════
		$html = preg_replace_callback(
			'/<img\b([^>]*?)>/is',
			function ( $m ) {
				if ( stripos( $m[1], 'loading=' ) !== false ) {
					return $m[0];
				}
				if ( preg_match( '/class="[^"]*(?:hero|logo|brand|monogram)/i', $m[1] ) ) {
					return $m[0];
				}
				return '<img loading="lazy"' . $m[1] . '>';
			},
			$html
		);

		// ══════════════════════════════════════════════
		// 9. LOVE HURTS $0 PRICING
		// ══════════════════════════════════════════════
		if ( strpos( $html, 'data-collection="love-hurts"' ) !== false ) {
			$js   = '<script>(function(){var m=document.querySelectorAll(".col-hero__meta span");'
				. 'if(m[1]&&m[1].textContent.indexOf("$0")!==-1){m[1].textContent="Pre-Order";m[1].style.color="#DC143C";}'
				. 'var c=document.querySelector(".col-catalog__count");'
				. 'if(c&&c.textContent.indexOf("$0")!==-1)c.textContent=c.textContent.replace(/\\$0\\s*[\\u2014\\u2013-]\\s*\\$0/,"Pre-Order Pricing");'
				. '})();</script>';
			$html = str_replace( '</body>', $js . "\n</body>", $html );
		}

		return $html;
	}
}

// /preorder/ → /pre-order/ redirect lives in inc/redirects.php
// (skyyrose_preorder_slug_redirect on template_redirect priority 1) — it
// preserves query strings (UTM, etc.). Keep one source of truth.

new SkyyRose_Accessibility_Fix();
