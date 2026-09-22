<?php
/** Native product eligibility and variation templates for Quick View. */
defined( 'ABSPATH' ) || exit;

function skyyrose2_quick_view_product_marker() {
	if ( ! function_exists( 'is_product' ) || ! is_product() || is_preview() ) {
		return;
	}
	$product = wc_get_product( get_queried_object_id() );
	if ( ! $product || 'publish' !== $product->get_status() || ! $product->is_visible() || post_password_required( $product->get_id() ) ) {
		return;
	}
	printf( '<meta name="sr2-quick-view-product" content="%s" data-product-type="%s">', esc_attr( $product->get_id() ), esc_attr( $product->get_type() ) );
}
add_action( 'wp_head', 'skyyrose2_quick_view_product_marker' );

function skyyrose2_quick_view_variation_templates() {
	// Native variable PDP prints these itself; simple PDP may have variable related cards.
	$product = function_exists( 'is_product' ) && is_product() ? wc_get_product( get_queried_object_id() ) : false;
	if ( $product && $product->is_type( 'variable' ) ) {
		return;
	}
	if ( wp_script_is( 'wc-add-to-cart-variation', 'enqueued' ) && function_exists( 'wc_get_template' ) ) {
		wc_get_template( 'single-product/add-to-cart/variation.php' );
	}
}
add_action( 'wp_footer', 'skyyrose2_quick_view_variation_templates', 19 );

/** Determine native runtime ownership from the final enqueue graph, including late plugins. */
function skyyrose2_quick_view_owns_variation_runtime() {
	$scripts = wp_scripts();
	$owner   = 'skyyrose2-quick-view-commerce';
	$target  = 'wc-add-to-cart-variation';
	// After-code executes immediately in WordPress and may call the native plugin.
	if ( ! empty( $scripts->registered[ $target ]->extra['after'] ) ) {
		return false;
	}
	if ( ! in_array( $owner, $scripts->queue, true ) ) {
		return false;
	}
	$requires_variation = static function ( $root ) use ( $scripts, $target ) {
		$pending = array( $root );
		$visited = array();
		while ( $pending ) {
			$handle = array_pop( $pending );
			if ( $target === $handle ) {
				return true;
			}
			if ( isset( $visited[ $handle ] ) ) {
				continue;
			}
			$visited[ $handle ] = true;
			foreach ( $scripts->registered[ $handle ]->deps ?? array() as $dependency ) {
				$pending[] = $dependency;
			}
		}
		return false;
	};
	if ( ! $requires_variation( $owner ) ) {
		return false;
	}
	foreach ( $scripts->queue as $handle ) {
		// Other roots are inspected in full, even if they depend on our owner.
		if ( $owner !== $handle && $requires_variation( $handle ) ) {
			return false;
		}
	}
	return true;
}

/** Defer only sources the browser's same-origin loader can use. */
function skyyrose2_quick_view_local_variation_source( $src ) {
	// Preserve the native tag for ambiguous URL syntax rather than reinterpret it.
	if ( ! is_string( $src ) || '' === $src || preg_match( '/[\\\\\x00-\x20]/', $src ) ) {
		return false;
	}
	$home   = wp_parse_url( home_url( '/' ) );
	$source = wp_parse_url( $src );
	if ( ! is_array( $home ) || ! is_array( $source ) || empty( $home['host'] ) || empty( $home['scheme'] ) || isset( $source['user'] ) || isset( $source['pass'] ) ) {
		return false;
	}
	$home_scheme = strtolower( $home['scheme'] );
	$scheme      = strtolower( $source['scheme'] ?? $home_scheme );
	$host        = strtolower( $source['host'] ?? $home['host'] );
	if ( ! in_array( $scheme, array( 'http', 'https' ), true ) || $scheme !== $home_scheme || $host !== strtolower( $home['host'] ) ) {
		return false;
	}
	$home_port = $home['port'] ?? ( 'https' === $home_scheme ? 443 : 80 );
	$port      = $source['port'] ?? ( isset( $source['host'] ) ? ( 'https' === $scheme ? 443 : 80 ) : $home_port );
	return $port === $home_port;
}

/** Keep the native variation runtime available, but request it only on intent off PDP. */
function skyyrose2_quick_view_defer_variation_script( $tag, $handle, $src ) {
	if ( 'wc-add-to-cart-variation' !== $handle || ( function_exists( 'is_product' ) && is_product() ) || ! class_exists( 'WP_HTML_Tag_Processor' ) ) {
		return $tag;
	}
	if ( ! apply_filters( 'skyyrose2_quick_view_lazy_variations_enabled', true ) || ! skyyrose2_quick_view_owns_variation_runtime() || ! skyyrose2_quick_view_local_variation_source( $src ) ) {
		return $tag;
	}
	$processor = new WP_HTML_Tag_Processor( $tag );
	while ( $processor->next_tag( 'SCRIPT' ) ) {
		if ( 'wc-add-to-cart-variation-js' !== $processor->get_attribute( 'id' ) ) {
			continue;
		}
		// Inline localization and wp-util dependencies retain their normal execution.
		$processor->set_attribute( 'data-sr2-variation-src', $src );
		$processor->set_attribute( 'type', 'text/plain' );
		$processor->remove_attribute( 'src' );
		return $processor->get_updated_html();
	}
	return $tag;
}
add_filter( 'script_loader_tag', 'skyyrose2_quick_view_defer_variation_script', 100, 3 );
