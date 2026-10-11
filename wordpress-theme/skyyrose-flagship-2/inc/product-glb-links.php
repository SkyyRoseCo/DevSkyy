<?php
/**
 * Read-only adapter for the exact Stream 2 preorder identity contract. No hooks or cart writes.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

/**
 * $catalog is an owner-generated get_product projection, never request data.
 * $registry_sha256 is the owner's full current registry digest, not its 16-char display prefix.
 * Runtime adopter supplies both from its certified build and re-resolves every open/retry.
 *
 * @throws Exception When identity, selection or availability is invalid.
 */
function skyyrose2_glb_native_product_link( $product_id, $variation_id, $selection, $expected_sku, $catalog, $registry_sha256, $expected_promise = null ) {
	if ( ! is_int( $product_id ) || $product_id < 1 || ! is_int( $variation_id ) || $variation_id < 0 || ! is_array( $selection ) || ! is_array( $catalog ) || ! is_string( $expected_sku ) || ! preg_match( '/^[a-z0-9]+(?:-[a-z0-9]+)*$/D', $expected_sku ) || ! is_string( $registry_sha256 ) || ! preg_match( '/^[a-f0-9]{64}$/D', $registry_sha256 ) || ! isset( $catalog[ $expected_sku ]['collection'] ) ) {
		throw new Exception( 'Unknown native product mapping.' );
	}
	$parent = wc_get_product( $product_id );
	$chosen = $variation_id ? wc_get_product( $variation_id ) : $parent;
	if ( ! $parent || ! $chosen || $parent->get_sku() !== $expected_sku || (int) wc_get_product_id_by_sku( $expected_sku ) !== $product_id || 'publish' !== $parent->get_status() || ! $parent->is_visible() ) {
		throw new Exception( 'Stale native product mapping.' );
	}
	$terms = wp_get_post_terms( $product_id, 'product_cat', array( 'fields' => 'slugs' ) );
	if ( is_wp_error( $terms ) || ! in_array( $catalog[ $expected_sku ]['collection'], $terms, true ) ) {
		throw new Exception( 'Product collection mapping changed.' );
	}
	if ( $variation_id ) {
		if ( ! $parent->is_type( 'variable' ) || ! $chosen->is_type( 'variation' ) || (int) $chosen->get_parent_id() !== $product_id || 'publish' !== $chosen->get_status() || ! $chosen->variation_is_active() ) {
			throw new Exception( 'Stale native variation mapping.' );
		}
		$attributes = $chosen->get_variation_attributes();
		$keys       = array_keys( $attributes );
		$selected   = array_keys( $selection );
		sort( $keys );
		sort( $selected );
		if ( $keys !== $selected ) {
			throw new Exception( 'Choose every native variation attribute.' );
		}
		$options = $parent->get_variation_attributes();
		foreach ( $attributes as $key => $value ) {
			$allowed = $options[ substr( $key, 10 ) ] ?? array();
			if ( ! is_string( $selection[ $key ] ) || '' === $selection[ $key ] || ( ! in_array( $selection[ $key ], $allowed, true ) && ! in_array( $selection[ $key ], array_map( 'sanitize_title', $allowed ), true ) ) || ( '' !== $value && $selection[ $key ] !== $value ) ) {
				throw new Exception( 'Native variation selection changed.' );
			}
		}
	} elseif ( ! $parent->is_type( 'simple' ) || $selection ) {
		throw new Exception( 'Choose a native variation on the product page.' );
	}
	if ( ! $chosen->is_purchasable() || ! $chosen->is_in_stock() ) {
		throw new Exception( 'This product selection is unavailable.' );
	}
	// Mandatory owner module, version-pinned at the handoff. It validates parent identity
	// and malformed preorder dates/allocation; it does not reserve or add anything.
	$config = skyyrose2_preorder_config( $product_id, $variation_id, $selection );
	if ( $config['is_preorder'] && null !== $config['available'] && $config['available'] < 1 ) {
		throw new Exception( 'This pre-order selection is unavailable.' );
	}
	if ( null !== $expected_promise && ! skyyrose2_preorder_promise_matches( $expected_promise, $config ) ) {
		throw new Exception( 'The native product promise changed.' );
	}
	return array(
		'sku'             => $expected_sku,
		'native_sku'      => $config['sku'],
		'product_id'      => $product_id,
		'variation_id'    => $variation_id,
		'attributes'      => $config['attributes'],
		'url'             => $variation_id ? $chosen->get_permalink( array( 'variation' => $config['attributes'] ) ) : $chosen->get_permalink(),
		'name'            => $chosen->get_name(),
		'available'       => true,
		'registry_sha256' => $registry_sha256,
	);
}
