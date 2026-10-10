<?php
/** Staging-only, one-product-at-a-time native variation migration. */
if ( ! defined( 'ABSPATH' ) || ! function_exists( 'wc_get_product' ) ||
	'https://staging-7e48-skyyrose.wpcomstaging.com' !== home_url() ||
	'skyyrose-flagship-2' !== get_stylesheet() ) {
	throw new RuntimeException( 'Staging V2 WooCommerce required.' );
}
function skyyrose2_runtime_snapshot( $product ) {
	$data = $product->get_data();
	foreach ( $data['attributes'] as $key => $attribute ) {
		$data['attributes'][ $key ] = $attribute->get_data();
	}
	foreach ( $data['meta_data'] as $key => $meta ) {
		$data['meta_data'][ $key ] = $meta->get_data();
	}
	foreach ( $data as $key => $value ) {
		if ( $value instanceof WC_DateTime ) {
			$data[ $key ] = $value->date( 'c' );
		}
	}
	$data['runtime_type'] = $product->get_type();
	$data['runtime_children'] = $product->get_children();
	return $data;
}
function skyyrose2_runtime_attributes( $data ) {
	$attributes = array();
	foreach ( $data as $key => $value ) {
		$attribute = new WC_Product_Attribute();
		foreach ( array( 'id', 'name', 'options', 'position', 'visible', 'variation' ) as $field ) {
			$attribute->{'set_' . $field}( $value[ $field ] );
		}
		$attributes[ $key ] = $attribute;
	}
	return $attributes;
}
function skyyrose2_runtime_refs( $ids ) {
	global $wpdb;
	$count = 0;
	foreach ( $ids as $id ) {
		$count += (int) $wpdb->get_var( $wpdb->prepare(
			"SELECT COUNT(*) FROM {$wpdb->prefix}woocommerce_order_itemmeta WHERE meta_key IN ('_product_id','_variation_id') AND meta_value=%s", (string) $id
		) );
	}
	return $count;
}
$config = $skyyrose_migration ?? array();
$mode = $config['mode'] ?? 'dry-run';
if ( ! in_array( $mode, array( 'dry-run', 'apply', 'rollback', 'rollback-dry-run' ), true ) ) {
	throw new RuntimeException( 'Invalid mode.' );
}
$row = $config['product'] ?? array();
if ( empty( $row['id'] ) || empty( $row['sku'] ) || empty( $row['canonical_sizes'] ) || 'SIZE REQUIRED' !== ( $row['classification'] ?? '' ) ) {
	throw new RuntimeException( 'Reviewed size-required product plan required.' );
}
$id = (int) $row['id'];
$product = wc_get_product( $id );
if ( ! $product || strtolower( $product->get_sku() ) !== $row['sku'] ) {
	throw new RuntimeException( 'Product identity mismatch.' );
}
$sizes = $row['canonical_sizes'];
if ( count( $sizes ) < 2 || count( $sizes ) !== count( array_unique( $sizes ) ) ) {
	throw new RuntimeException( 'Explicit distinct size options required.' );
}
$before = skyyrose2_runtime_snapshot( $product );
$before_hash = hash( 'sha256', wp_json_encode( $before ) );
$option = 'skyyrose_v2_phase2_variations_' . $id;
$journal = get_option( $option, false );
$plan_hash = hash( 'sha256', wp_json_encode( array( $id, $row['sku'], $sizes ) ) );
$result = array( 'mode' => $mode, 'id' => $id, 'sku' => $row['sku'], 'snapshot' => $before, 'snapshot_sha256' => $before_hash, 'order_reference_count' => skyyrose2_runtime_refs( array( $id ) ), 'planned_sizes' => $sizes, 'changed' => false );
if ( 'dry-run' === $mode ) {
	echo wp_json_encode( $result, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES );
	return;
}
if ( $journal && $journal['plan_sha256'] !== $plan_hash ) {
	throw new RuntimeException( 'Stored migration plan differs.' );
}
if ( $journal && 'apply' === $mode ) {
	if ( $before_hash !== $journal['after_sha256'] ) {
		throw new RuntimeException( 'Migrated product changed; inspect before retry.' );
	}
	$result['variation_ids'] = $journal['variation_ids'];
	echo wp_json_encode( $result, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES );
	return;
}
if ( 'rollback' === $mode || 'rollback-dry-run' === $mode ) {
	if ( ! $journal || $before_hash !== $journal['after_sha256'] || skyyrose2_runtime_refs( array_merge( array( $id ), $journal['variation_ids'] ) ) ) {
		throw new RuntimeException( 'Rollback blocked by drift, missing journal or order references.' );
	}
	if ( 'rollback-dry-run' === $mode ) {
		$result['restore'] = $journal['before'];
		$result['remove_variation_ids'] = $journal['variation_ids'];
		echo wp_json_encode( $result, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES );
		return;
	}
} elseif ( $before_hash !== ( $config['expected_sha256'] ?? '' ) || ! $product->is_type( 'simple' ) || $product->get_children() ) {
	throw new RuntimeException( 'Unreviewed preimage, unexpected type or existing variations.' );
}
// Prevent these staging product events from being queued for external webhooks.
// WC_Webhook::process checks this filter BEFORE scheduling delivery.
add_filter( 'woocommerce_webhook_should_deliver', function ( $deliver, $webhook ) {
	return str_starts_with( $webhook->get_topic(), 'product.' ) ? false : $deliver;
}, PHP_INT_MAX, 2 );
// Bound immediate third-party HTTP side effects to this migration process.
add_filter( 'pre_http_request', function () {
	return new WP_Error( 'skyyrose_staging_migration_isolation', 'Outbound HTTP disabled for staging migration process.' );
}, PHP_INT_MAX );
global $wpdb;
// Refuse transaction-dependent migration on nontransactional tables.
foreach ( array( $wpdb->posts, $wpdb->postmeta, $wpdb->options, $wpdb->terms, $wpdb->term_taxonomy, $wpdb->term_relationships, $wpdb->prefix . 'wc_product_meta_lookup' ) as $table ) {
	$status = $wpdb->get_row( $wpdb->prepare( 'SHOW TABLE STATUS WHERE Name=%s', $table ) );
	if ( ! $status || 'InnoDB' !== $status->Engine ) {
		throw new RuntimeException( 'Transactional table required: ' . $table );
	}
}
wc_transaction_query( 'start' );
try {
	if ( 'rollback' === $mode ) {
		foreach ( $journal['variation_ids'] as $variation_id ) {
			$variation = wc_get_product( $variation_id );
			if ( ! $variation || $variation->get_parent_id() !== $id ) {
				throw new RuntimeException( 'Variation ownership changed.' );
			}
			$variation->delete( true );
		}
		$restore = $journal['before'];
		$simple = new WC_Product_Simple( $id );
		$simple->set_attributes( skyyrose2_runtime_attributes( $restore['attributes'] ) );
		$simple->set_default_attributes( $restore['default_attributes'] );
		foreach ( array( 'regular_price', 'sale_price', 'price', 'manage_stock', 'stock_quantity', 'stock_status', 'backorders' ) as $field ) {
			$simple->{'set_' . $field}( $restore[ $field ] );
		}
		$simple->save();
		delete_option( $option );
		$result['restored_type'] = 'simple';
	} else {
		$variable = new WC_Product_Variable( $id );
		$attributes = $variable->get_attributes();
		$size = new WC_Product_Attribute();
		$size->set_name( 'Size' );
		$size->set_options( $sizes );
		$size->set_visible( true );
		$size->set_variation( true );
		$attributes['size'] = $size;
		$variable->set_attributes( $attributes );
		$variable->set_default_attributes( array() );
		$variable->save();
		$created = array();
		foreach ( $sizes as $size_value ) {
			$variation = new WC_Product_Variation();
			$variation->set_parent_id( $id );
			$variation->set_status( 'publish' );
			$variation->set_attributes( array( 'size' => $size_value ) );
			$variation->set_regular_price( $before['regular_price'] );
			$variation->set_sale_price( $before['sale_price'] );
			$variation->set_date_on_sale_from( $product->get_date_on_sale_from() );
			$variation->set_date_on_sale_to( $product->get_date_on_sale_to() );
			$variation->set_price( $before['price'] );
			$variation->set_manage_stock( false );
			$variation->set_stock_status( $before['stock_status'] );
			$variation->set_backorders( $before['backorders'] );
			$variation->set_virtual( $before['virtual'] );
			$variation->set_downloadable( $before['downloadable'] );
			$variation->save();
			$created[] = $variation->get_id();
		}
		WC_Product_Variable::sync( $id );
		wc_delete_product_transients( $id );
		clean_post_cache( $id );
		$after_product = new WC_Product_Variable( $id );
		$after = skyyrose2_runtime_snapshot( $after_product );
		foreach ( array( 'id', 'sku', 'slug', 'status', 'price', 'manage_stock', 'stock_quantity', 'stock_status', 'backorders', 'image_id', 'gallery_image_ids', 'category_ids' ) as $field ) {
			if ( $after[ $field ] !== $before[ $field ] ) {
				throw new RuntimeException( 'Protected field changed: ' . $field );
			}
		}
		// Woo stores regular/sale prices on children and clears parent copies.
		foreach ( $created as $index => $variation_id ) {
			$child = new WC_Product_Variation( $variation_id );
			if ( $child->get_regular_price() !== $before['regular_price'] || $child->get_sale_price() !== $before['sale_price'] || $child->get_price() !== $before['price'] || $child->get_attributes() !== array( 'size' => $sizes[ $index ] ) ) {
				throw new RuntimeException( 'Child price or size mismatch.' );
			}
		}
		if ( count( $after_product->get_children() ) !== count( $sizes ) ) {
			throw new RuntimeException( 'Variation count mismatch.' );
		}
		$journal = array( 'plan_sha256' => $plan_hash, 'before' => $before, 'before_sha256' => $before_hash, 'after_sha256' => hash( 'sha256', wp_json_encode( $after ) ), 'variation_ids' => $created );
		if ( ! add_option( $option, $journal, '', false ) ) {
			throw new RuntimeException( 'Migration journal collision.' );
		}
		$result['variation_ids'] = $created;
		$result['after_sha256'] = $journal['after_sha256'];
	}
	wc_transaction_query( 'commit' );
	$result['changed'] = true;
} catch ( Throwable $error ) {
	wc_transaction_query( 'rollback' );
	clean_post_cache( $id );
	wc_delete_product_transients( $id );
	throw $error;
}
echo wp_json_encode( $result, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES );
