<?php
/**
 * Staging-only native account content migration, invoked through wp eval.
 * Caller supplies $skyyrose_migration: mode, expected_sha256, and rollback_content
 * (rollback only). Dry-run is the default and records the exact preimage.
 */
if ( ! defined( 'ABSPATH' ) || ! function_exists( 'wc_get_page_id' ) ) {
	throw new RuntimeException( 'WordPress and WooCommerce are required.' );
}
if ( 'https://staging-7e48-skyyrose.wpcomstaging.com' !== home_url() || 'skyyrose-flagship-2' !== get_stylesheet() ) {
	throw new RuntimeException( 'Staging V2 environment required.' );
}
$skyyrose_migration = $skyyrose_migration ?? array();
$mode = $skyyrose_migration['mode'] ?? 'dry-run';
if ( ! in_array( $mode, array( 'dry-run', 'apply', 'rollback' ), true ) ) {
	throw new RuntimeException( 'Invalid migration mode.' );
}
$id   = wc_get_page_id( 'myaccount' );
$page = get_post( $id );
if ( ! $page || 'page' !== $page->post_type || 'publish' !== $page->post_status ) {
	throw new RuntimeException( 'Configured account page must exist and be published.' );
}
$before = $page->post_content;
$target = '[woocommerce_my_account]';
if ( 'rollback' === $mode ) {
	if ( ! isset( $skyyrose_migration['rollback_content'] ) || ! is_string( $skyyrose_migration['rollback_content'] ) ) {
		throw new RuntimeException( 'Exact rollback content is required.' );
	}
	$target = $skyyrose_migration['rollback_content'];
}
$record = array(
	'mode' => $mode,
	'page_id' => $id,
	'page_slug' => $page->post_name,
	'template' => get_post_meta( $id, '_wp_page_template', true ),
	'before_content' => $before,
	'before_sha256' => hash( 'sha256', $before ),
	'target_content' => $target,
	'target_sha256' => hash( 'sha256', $target ),
	'changed' => false,
);
if ( 'dry-run' !== $mode && $before !== $target ) {
	if ( ! isset( $skyyrose_migration['expected_sha256'] ) || ! hash_equals( $record['before_sha256'], $skyyrose_migration['expected_sha256'] ) ) {
		throw new RuntimeException( 'Content drift or missing reviewed preimage hash.' );
	}
	$result = wp_update_post( wp_slash( array( 'ID' => $id, 'post_content' => $target ) ), true );
	if ( is_wp_error( $result ) ) {
		throw new RuntimeException( $result->get_error_message() );
	}
	clean_post_cache( $id );
	if ( get_post( $id )->post_content !== $target ) {
		throw new RuntimeException( 'Content verification failed; inspect before retrying.' );
	}
	$record['changed'] = true;
}
echo wp_json_encode( $record, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES );
