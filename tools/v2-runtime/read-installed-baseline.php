<?php
/** Authenticated, read-only installed inventory. No option/product/order writes. */
if ( ! defined( 'WP_CLI' ) || ! WP_CLI || get_option( 'home' ) !== 'https://skyyrose.co' ) {
	throw new RuntimeException( 'The authenticated intended installed site is required.' );
}
require_once ABSPATH . 'wp-admin/includes/plugin.php';
$result = array( 'schema' => 'skyyrose.installed-baseline.v1', 'classification' => 'AUTHENTICATED_LIVE_READ_ONLY', 'observed_utc' => gmdate( 'c' ), 'site' => get_option( 'home' ), 'wp_version' => get_bloginfo( 'version' ), 'php_version' => PHP_VERSION, 'db_version' => $GLOBALS['wpdb']->db_version(), 'stylesheet' => get_option( 'stylesheet' ), 'template' => get_option( 'template' ), 'storage_options' => array(), 'plugins' => array(), 'mu_plugins' => array(), 'drop_ins' => array(), 'code_hashes' => array(), 'routes' => array(), 'limits' => array( 'No order/customer rows or secrets exported', 'Managed platform files outside readable directories may be inaccessible', 'Code hashes and selected options are not a recoverable code/data backup', 'No restore or site mutation performed' ) );
foreach ( array( 'woocommerce_custom_orders_table_enabled', 'woocommerce_custom_orders_table_data_sync_enabled', 'permalink_structure', 'blog_public' ) as $name ) {
	$result['storage_options'][ $name ] = get_option( $name, null );
}
$active = get_option( 'active_plugins', array() );
foreach ( get_plugins() as $file => $plugin ) {
	$result['plugins'][ $file ] = array( 'version' => $plugin['Version'], 'active' => in_array( $file, $active, true ) );
}
foreach ( get_mu_plugins() as $file => $plugin ) { $result['mu_plugins'][ $file ] = array( 'version' => $plugin['Version'] ); }
foreach ( get_dropins() as $file => $plugin ) { $result['drop_ins'][ $file ] = array( 'version' => $plugin['Version'] ?? '' ); }
$directories = array( 'active-theme' => get_theme_root() . '/' . $result['stylesheet'], 'plugins' => WP_PLUGIN_DIR, 'mu-plugins' => WPMU_PLUGIN_DIR );
$count = 0;
foreach ( $directories as $prefix => $directory ) {
	if ( ! is_dir( $directory ) || ! is_readable( $directory ) ) { $result['unreadable_directories'][] = $prefix; continue; }
	$iterator = new RecursiveIteratorIterator( new RecursiveDirectoryIterator( $directory, FilesystemIterator::SKIP_DOTS ), RecursiveIteratorIterator::LEAVES_ONLY, RecursiveIteratorIterator::CATCH_GET_CHILD );
	foreach ( $iterator as $file ) {
		if ( ! $file->isFile() ) { continue; }
		if ( ++$count > 100000 ) { throw new RuntimeException( 'Bounded inventory limit exceeded.' ); }
		$relative = $prefix . '/' . substr( $file->getPathname(), strlen( $directory ) + 1 );
		$hash = is_readable( $file->getPathname() ) ? hash_file( 'sha256', $file->getPathname() ) : false;
		$result['code_hashes'][ $relative ] = $hash ? array( 'sha256' => $hash, 'bytes' => $file->getSize(), 'symlink' => $file->isLink() ) : array( 'unreadable' => true );
	}
}
foreach ( array_keys( $result['drop_ins'] ) as $file ) {
	$path = WP_CONTENT_DIR . '/' . $file;
	$result['code_hashes'][ 'drop-ins/' . $file ] = array( 'sha256' => is_readable( $path ) ? hash_file( 'sha256', $path ) : null, 'symlink' => is_link( $path ) );
}
foreach ( array( 'collections/signature', 'collections/black-rose', 'collections/love-hurts', 'collections/kids-capsule', 'worlds', 'experiences', 'size-guide', 'worlds/signature', 'worlds/black-rose', 'worlds/love-hurts', 'worlds/kids-capsule', 'experience-signature', 'experience-black-rose', 'experience-love-hurts', 'experience-kids-capsule' ) as $path ) {
	$page = get_page_by_path( $path );
	$result['routes'][ $path ] = $page ? array( 'id' => $page->ID, 'status' => $page->post_status, 'template' => get_post_meta( $page->ID, '_wp_page_template', true ), 'content_sha256' => hash( 'sha256', $page->post_content ), 'url' => get_permalink( $page->ID ) ) : null;
}
ksort( $result['code_hashes'] );
echo wp_json_encode( $result, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES );
