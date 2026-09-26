<?php
/**
 * Lightweight WordPress function stubs for PHPUnit.
 *
 * No external packages required. Replaces WP_Mock for pure-PHP modules
 * that have no database or HTTP dependencies.
 *
 * @package SkyyRose
 */

// Constants.
defined( 'HOUR_IN_SECONDS' ) || define( 'HOUR_IN_SECONDS', 3600 );

// ---------------------------------------------------------------------------
// Sanitization
// ---------------------------------------------------------------------------

if ( ! function_exists( 'sanitize_key' ) ) {
	function sanitize_key( $key ) {
		return preg_replace( '/[^a-z0-9_\-]/', '', strtolower( trim( (string) $key ) ) );
	}
}

if ( ! function_exists( 'sanitize_text_field' ) ) {
	function sanitize_text_field( $str ) {
		return trim( strip_tags( (string) $str ) );
	}
}

if ( ! function_exists( 'sanitize_file_name' ) ) {
	function sanitize_file_name( $filename ) {
		$filename = (string) $filename;
		$filename = preg_replace( '/[^a-zA-Z0-9\.\-_]/', '-', $filename );
		return trim( $filename, '-' );
	}
}

if ( ! function_exists( 'sanitize_title' ) ) {
	function sanitize_title( $title ) {
		$title = strtolower( strip_tags( (string) $title ) );
		$title = preg_replace( '/[^a-z0-9\-]/', '-', $title );
		$title = preg_replace( '/-+/', '-', $title );
		return trim( $title, '-' );
	}
}

if ( ! function_exists( 'absint' ) ) {
	function absint( $value ) {
		return abs( (int) $value );
	}
}

if ( ! function_exists( 'wp_unslash' ) ) {
	function wp_unslash( $value ) {
		return $value;
	}
}

// ---------------------------------------------------------------------------
// Escaping
// ---------------------------------------------------------------------------

if ( ! function_exists( 'esc_html__' ) ) {
	function esc_html__( $text, $domain = '' ) {
		return htmlspecialchars( (string) $text, ENT_QUOTES, 'UTF-8' );
	}
}

if ( ! function_exists( 'esc_html' ) ) {
	function esc_html( $text ) {
		return htmlspecialchars( (string) $text, ENT_QUOTES, 'UTF-8' );
	}
}

if ( ! function_exists( 'esc_attr' ) ) {
	function esc_attr( $text ) {
		return htmlspecialchars( (string) $text, ENT_QUOTES, 'UTF-8' );
	}
}

// ---------------------------------------------------------------------------
// Translation
// ---------------------------------------------------------------------------

if ( ! function_exists( '__' ) ) {
	function __( $text, $domain = '' ) {
		return (string) $text;
	}
}

if ( ! function_exists( '_e' ) ) {
	function _e( $text, $domain = '' ) {
		echo (string) $text;
	}
}

// ---------------------------------------------------------------------------
// URL helpers
// ---------------------------------------------------------------------------

if ( ! function_exists( 'home_url' ) ) {
	function home_url( $path = '' ) {
		return 'https://skyyrose.co' . $path;
	}
}

if ( ! function_exists( 'get_theme_file_path' ) ) {
	function get_theme_file_path( $file = '' ) {
		return SKYYROSE_DIR . '/' . ltrim( $file, '/' );
	}
}

if ( ! function_exists( 'get_theme_file_uri' ) ) {
	function get_theme_file_uri( $file = '' ) {
		return 'https://theme.test/' . ltrim( $file, '/' );
	}
}

if ( ! function_exists( 'get_template_directory_uri' ) ) {
	function get_template_directory_uri() {
		return 'https://theme.test/wp-content/themes/skyyrose-flagship';
	}
}

if ( ! function_exists( 'get_template_directory' ) ) {
	function get_template_directory() {
		return SKYYROSE_DIR;
	}
}

if ( ! function_exists( 'wp_get_upload_dir' ) ) {
	function wp_get_upload_dir() {
		return array(
			'baseurl' => 'https://theme.test/wp-content/uploads',
			'basedir' => sys_get_temp_dir() . '/skyyrose-test-uploads',
		);
	}
}

if ( ! function_exists( 'trailingslashit' ) ) {
	function trailingslashit( $string ) {
		return rtrim( (string) $string, '/\\' ) . '/';
	}
}

// ---------------------------------------------------------------------------
// Object cache (no-op in tests — forces CSV re-parse via static $catalog)
// ---------------------------------------------------------------------------

if ( ! function_exists( 'wp_cache_get' ) ) {
	function wp_cache_get( $key, $group = '', $force = false, &$found = null ) {
		$found = false;
		return false;
	}
}

if ( ! function_exists( 'wp_cache_set' ) ) {
	function wp_cache_set( $key, $data, $group = '', $expire = 0 ) {
		return true;
	}
}

// ---------------------------------------------------------------------------
// Hooks (no-op — tests exercise return values, not side effects)
// ---------------------------------------------------------------------------

if ( ! function_exists( 'add_action' ) ) {
	function add_action( $hook, $callback, $priority = 10, $accepted_args = 1 ) {
		return true;
	}
}

if ( ! function_exists( 'add_filter' ) ) {
	function add_filter( $hook, $callback, $priority = 10, $accepted_args = 1 ) {
		return true;
	}
}

if ( ! function_exists( 'do_action' ) ) {
	function do_action( $hook, ...$args ) {
		return null;
	}
}

// ---------------------------------------------------------------------------
// Metadata and identity stores used by WooCommerce pre-order tests.
// ---------------------------------------------------------------------------

if ( ! function_exists( 'get_post_meta' ) ) {
	function get_post_meta( $post_id, $key, $single = false ) {
		return $GLOBALS['skyyrose_test_post_meta'][ (int) $post_id ][ $key ] ?? '';
	}
}

if ( ! function_exists( 'update_post_meta' ) ) {
	function update_post_meta( $post_id, $key, $value ) {
		$GLOBALS['skyyrose_test_post_meta'][ (int) $post_id ][ $key ] = $value;
		return true;
	}
}

if ( ! function_exists( 'get_user_meta' ) ) {
	function get_user_meta( $user_id, $key, $single = false ) {
		return $GLOBALS['skyyrose_test_user_meta'][ (int) $user_id ][ $key ] ?? '';
	}
}

if ( ! function_exists( 'update_user_meta' ) ) {
	function update_user_meta( $user_id, $key, $value ) {
		$GLOBALS['skyyrose_test_user_meta'][ (int) $user_id ][ $key ] = $value;
		return true;
	}
}

if ( ! function_exists( 'get_user_by' ) ) {
	function get_user_by( $field, $value ) {
		return $GLOBALS['skyyrose_test_users'][ strtolower( (string) $value ) ] ?? false;
	}
}

if ( ! function_exists( 'is_email' ) ) {
	function is_email( $email ) {
		return false !== filter_var( $email, FILTER_VALIDATE_EMAIL );
	}
}

if ( ! function_exists( 'get_option' ) ) {
	function get_option( $key, $default = false ) {
		return $GLOBALS['skyyrose_test_options'][ $key ] ?? $default;
	}
}

if ( ! function_exists( 'update_option' ) ) {
	function update_option( $key, $value ) {
		$GLOBALS['skyyrose_test_options'][ $key ] = $value;
		return true;
	}
}

// ---------------------------------------------------------------------------
// Transients (in-memory store for display-cache tests)
// ---------------------------------------------------------------------------

if ( ! function_exists( 'get_transient' ) ) {
	function get_transient( $transient ) {
		return false;
	}
}

if ( ! function_exists( 'set_transient' ) ) {
	function set_transient( $transient, $value, $expiration = 0 ) {
		return true;
	}
}

if ( ! function_exists( 'delete_transient' ) ) {
	function delete_transient( $transient ) {
		return true;
	}
}
