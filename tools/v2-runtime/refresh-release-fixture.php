<?php
/** Refresh derived URL bindings only; never creates or mutates product facts. */
if ( ! defined( 'WP_CLI' ) || ! WP_CLI || ! defined( 'SKYYROSE_RELEASE_SYNTHETIC_FIXTURE' ) || ! SKYYROSE_RELEASE_SYNTHETIC_FIXTURE || DB_NAME !== 'sr_release_fixture' || get_option( 'home' ) !== 'http://127.0.0.1:18362' ) {
	throw new RuntimeException( 'Private synthetic release fixture required.' );
}
$file = dirname( __DIR__, 2 ) . '/tasks/release-gates-20261019/evidence/native-browser-fixture.json';
$manifest = json_decode( file_get_contents( $file ), true, 512, JSON_THROW_ON_ERROR );
global $wp_rewrite;
$wp_rewrite->set_permalink_structure( '/%postname%/' );
flush_rewrite_rules( false );
foreach ( $manifest['products'] as $sku => &$binding ) {
	$product = wc_get_product( $binding['id'] );
	if ( ! $product || $product->get_sku() !== $sku || $product->get_meta( '_sr_release_synthetic' ) !== '1' ) {
		throw new RuntimeException( 'Synthetic native product identity changed.' );
	}
	$binding['url'] = get_permalink( $binding['id'] );
}
unset( $binding );
if ( '1' === getenv( 'SR_RELEASE_MATCH_PUBLISHED_ALIASES' ) ) {
	foreach ( $manifest['routes'] as &$route ) {
		if ( ! in_array( $route['kind'], array( 'world', 'directory' ), true ) ) { continue; }
		$slug = 'directory' === $route['kind'] ? 'experiences' : 'experience-' . $route['collection'];
		$original = get_post( $route['id'] );
		$alias = get_page_by_path( $slug );
		if ( ! $alias ) {
			$id = wp_insert_post( array( 'post_type' => 'page', 'post_status' => 'publish', 'post_name' => $slug, 'post_title' => $original->post_title, 'post_content' => $original->post_content ), true );
			if ( is_wp_error( $id ) ) { throw new RuntimeException( $id->get_error_message() ); }
			update_post_meta( $id, '_wp_page_template', $route['template'] );
		} else { $id = $alias->ID; }
		wp_update_post( array( 'ID' => $original->ID, 'post_status' => 'draft' ) );
		$route['id'] = $id;
		$route['path'] = '/' . $slug . '/';
	}
	unset( $route );
}
$directory = '<nav aria-label="Collection worlds"><ul>';
$directory_id = 0;
foreach ( $manifest['routes'] as $route ) {
	if ( get_post_type( $route['id'] ) !== 'page' || get_post_status( $route['id'] ) !== 'publish' || wp_parse_url( get_permalink( $route['id'] ), PHP_URL_PATH ) !== $route['path'] ) {
		throw new RuntimeException( 'Native route identity changed.' );
	}
	if ( $route['kind'] === 'world' ) {
		$directory .= '<li><a href="' . esc_url( get_permalink( $route['id'] ) ) . '">' . esc_html( get_the_title( $route['id'] ) ) . '</a></li>';
	} elseif ( $route['kind'] === 'directory' ) {
		$directory_id = $route['id'];
	}
}
if ( ! $directory_id ) { throw new RuntimeException( 'Missing synthetic directory.' ); }
wp_update_post( array( 'ID' => $directory_id, 'post_content' => $directory . '</ul></nav>' ) );
$manifest['woocommerce'] = WC_VERSION;
$manifest['wp'] = get_bloginfo( 'version' );
$manifest['url_readback_utc'] = gmdate( 'c' );
file_put_contents( $file, wp_json_encode( $manifest, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES ) . "\n" );
echo 'Refreshed native URLs for ' . count( $manifest['products'] ) . " verified synthetic products.\n";
