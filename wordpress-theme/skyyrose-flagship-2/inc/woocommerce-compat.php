<?php
/**
 * Versioned commercial promises at native WooCommerce transaction boundaries.
 *
 * No price override, stock reservation, allocation decrement, or referral payout.
 * Load once from the V2 bootstrap. Product facts remain registry/Woo consumers.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

/**
 * Resolve product identity and inherited WooCommerce preorder metadata.
 *
 * @param int   $product_id Native parent or simple product ID.
 * @param int   $variation_id Native selected variation ID.
 * @param array $selection Native variation selection.
 * @throws Exception When the transaction fails validation.
 */
function skyyrose2_preorder_config( $product_id, $variation_id = 0, $selection = array() ) {
	$product = wc_get_product( $product_id );
	$chosen  = $variation_id ? wc_get_product( $variation_id ) : $product;
	if ( ! $product || ! $chosen || ( $variation_id && ( ! $chosen->is_type( 'variation' ) || (int) $chosen->get_parent_id() !== (int) $product_id ) ) || ( ! $variation_id && ! $product->is_type( 'simple' ) ) ) {
		throw new Exception( esc_html__( 'Choose a valid product and variation before adding it to your bag.', 'skyyrose-flagship-2' ) );
	}
	$values  = array();
	$sources = array();
	foreach ( array( '_is_preorder', '_preorder_edition_size', '_preorder_available', '_preorder_ship_date' ) as $key ) {
		foreach ( array( $chosen, $product ) as $candidate ) {
			if ( $candidate->meta_exists( $key ) ) {
				$values[ $key ]  = $candidate->get_meta( $key, true );
				$sources[ $key ] = $candidate->get_id();
				break;
			}
		}
	}
	$preorder = '1' === (string) ( $values['_is_preorder'] ?? '0' );
	// A registry-derived preorder label must receive the same transaction protection.
	if ( function_exists( 'skyyrose2_is_preorder_product' ) ) {
		$preorder = $preorder || skyyrose2_is_preorder_product( $product );
	}
	$available = $values['_preorder_available'] ?? '';
	$edition   = $values['_preorder_edition_size'] ?? '';
	if ( $preorder && '' !== $available && ! preg_match( '/^\d+$/D', (string) $available ) ) {
		throw new Exception( esc_html__( 'This pre-order availability needs review. Contact Client Services.', 'skyyrose-flagship-2' ) );
	}
	$date = (string) ( $values['_preorder_ship_date'] ?? '' );
	if ( '' !== $date ) {
		$parsed = DateTimeImmutable::createFromFormat( '!Y-m-d', $date );
		if ( ! $parsed || $parsed->format( 'Y-m-d' ) !== $date ) {
			throw new Exception( esc_html__( 'This pre-order shipping estimate needs review. Contact Client Services.', 'skyyrose-flagship-2' ) );
		}
	}
	$attributes = $variation_id ? $chosen->get_variation_attributes() : array();
	foreach ( $attributes as $key => $value ) {
		if ( '' === $value && isset( $selection[ $key ] ) ) {
			$attributes[ $key ] = (string) $selection[ $key ];
		}
	}
	ksort( $attributes );
	return array(
		'is_preorder'             => (bool) $preorder,
		'product_id'              => (int) $product_id,
		'variation_id'            => (int) $variation_id,
		'sku'                     => $chosen->get_sku(),
		'attributes'              => $attributes,
		'configuration_source_id' => (int) ( $sources['_is_preorder'] ?? $product_id ),
		'allocation_source_id'    => (int) ( $sources['_preorder_available'] ?? $product_id ),
		'edition_size'            => '' === $edition ? null : (string) $edition,
		'available'               => '' === $available ? null : (int) $available,
		'expected_ship_date'      => '' === $date ? null : $date,
	);
}

/**
 * Descriptive fields only; native WooCommerce prices/totals are never captured.
 *
 * @param array $config Effective preorder configuration.
 */
function skyyrose2_preorder_snapshot( $config ) {
	$snapshot = $config;
	unset( $snapshot['available'] );
	$snapshot['schema']                   = 'skyyrose.preorder-commercial-promise';
	$snapshot['schema_version']           = 2;
	$snapshot['capture_point']            = 'add_to_cart';
	$snapshot['available_at_add_to_cart'] = $config['available'];
	return $snapshot;
}

/**
 * Compare stable promise/identity fields; changing availability is revalidated.
 *
 * @param mixed $snapshot Recorded promise.
 * @param array $config Current configuration.
 */
function skyyrose2_preorder_promise_matches( $snapshot, $config ) {
	if ( ! is_array( $snapshot ) || 'skyyrose.preorder-commercial-promise' !== ( $snapshot['schema'] ?? '' ) || 2 !== ( $snapshot['schema_version'] ?? 0 ) ) {
		return false;
	}
	foreach ( array( 'is_preorder', 'product_id', 'variation_id', 'sku', 'attributes', 'configuration_source_id', 'allocation_source_id', 'edition_size', 'expected_ship_date' ) as $field ) {
		if ( ! array_key_exists( $field, $snapshot ) || $snapshot[ $field ] !== $config[ $field ] ) {
			return false;
		}
	}
	return true;
}

/**
 * Validate positive integral quantities and aggregate the current allocation pool.
 *
 * @param array        $config Current configuration.
 * @param mixed        $quantity Requested whole quantity.
 * @param WC_Cart|null $cart Current native cart.
 * @param string       $excluded_key Line replaced by quantity update.
 * @throws Exception When the transaction fails validation.
 */
function skyyrose2_preorder_validate_quantity( $config, $quantity, $cart, $excluded_key = '' ) {
	if ( ! is_numeric( $quantity ) || ! is_finite( (float) $quantity ) || (float) $quantity <= 0 || floor( (float) $quantity ) !== (float) $quantity ) {
		throw new Exception( esc_html__( 'Choose a positive whole number of items.', 'skyyrose-flagship-2' ) );
	}
	if ( ! $config['is_preorder'] || null === $config['available'] ) {
		return;
	}
	$total = (float) $quantity;
	foreach ( $cart ? $cart->get_cart() : array() as $key => $values ) {
		if ( $key === $excluded_key ) {
			continue;
		}
		$other = skyyrose2_preorder_config( $values['product_id'], $values['variation_id'] ?? 0 );
		if ( $other['is_preorder'] && $other['allocation_source_id'] === $config['allocation_source_id'] ) {
			$total += (float) $values['quantity'];
		}
	}
	if ( $total > $config['available'] ) {
		throw new Exception( esc_html__( 'Your bag exceeds the current pre-order availability. Review the quantity before checkout.', 'skyyrose-flagship-2' ) );
	}
}

/**
 * Core catches this Exception and returns false plus a notice (Woo 11.1.2).
 *
 * @param array $data Existing custom data.
 * @param int   $product_id Native product ID.
 * @param int   $variation_id Native variation ID.
 * @param mixed $quantity Requested quantity.
 */
function skyyrose2_preorder_add_cart_data( $data, $product_id, $variation_id, $quantity ) {
	$config = skyyrose2_preorder_config( $product_id, $variation_id );
	skyyrose2_preorder_validate_quantity( $config, $quantity, WC()->cart );
	// Caller-supplied metadata, including an order-again snapshot, has no authority.
	$data['skyyrose_preorder_snapshot'] = skyyrose2_preorder_snapshot( $config );
	return $data;
}
add_filter( 'woocommerce_add_cart_item_data', 'skyyrose2_preorder_add_cart_data', 10, 4 );

/**
 * Core has resolved and validated wildcard variation selections at this point.
 *
 * @param array $values Core-resolved cart line.
 */
function skyyrose2_preorder_finalize_cart_item( $values ) {
	$config                               = skyyrose2_preorder_config( $values['product_id'], $values['variation_id'] ?? 0, $values['variation'] ?? array() );
	$values['skyyrose_preorder_snapshot'] = skyyrose2_preorder_snapshot( $config );
	return $values;
}
add_filter( 'woocommerce_add_cart_item', 'skyyrose2_preorder_finalize_cart_item', 10, 1 );

/**
 * Request adapter; direct additions are independently checked inside core.
 *
 * @param bool  $passed Prior validation result.
 * @param int   $product_id Native product ID.
 * @param mixed $quantity Requested quantity.
 * @param int   $variation_id Native variation ID.
 */
function skyyrose2_preorder_add_validation( $passed, $product_id, $quantity, $variation_id = 0 ) {
	if ( ! $passed ) {
		return false;
	}
	try {
		$config = skyyrose2_preorder_config( $product_id, $variation_id );
		skyyrose2_preorder_validate_quantity( $config, $quantity, WC()->cart );
	} catch ( Exception $error ) {
		wc_add_notice( $error->getMessage(), 'error' );
		return false;
	}
	return true;
}
add_filter( 'woocommerce_add_to_cart_validation', 'skyyrose2_preorder_add_validation', 10, 4 );

/**
 * A zero update removes the item; negative/fractional replacements fail.
 *
 * @param bool   $passed Prior validation result.
 * @param string $key Cart line key.
 * @param array  $values Current cart line.
 * @param mixed  $quantity Replacement quantity.
 */
function skyyrose2_preorder_update_validation( $passed, $key, $values, $quantity ) {
	if ( ! $passed || ( is_numeric( $quantity ) && 0.0 === (float) $quantity ) ) {
		return $passed;
	}
	try {
		$config = skyyrose2_preorder_config( $values['product_id'], $values['variation_id'] ?? 0 );
		skyyrose2_preorder_validate_quantity( $config, $quantity, WC()->cart, $key );
	} catch ( Exception $error ) {
		wc_add_notice( $error->getMessage(), 'error' );
		return false;
	}
	return true;
}
add_filter( 'woocommerce_update_cart_validation', 'skyyrose2_preorder_update_validation', 10, 4 );

/**
 * Collect errors without changing a restored promise or rebuilding legacy history.
 *
 * @param WC_Cart|null $cart Current native cart.
 * @throws Exception When the transaction fails validation.
 */
function skyyrose2_preorder_cart_errors( $cart ) {
	$messages = array();
	foreach ( $cart ? $cart->get_cart() : array() as $key => $values ) {
		try {
			$config = skyyrose2_preorder_config( $values['product_id'], $values['variation_id'] ?? 0, $values['variation'] ?? array() );
			skyyrose2_preorder_validate_quantity( $config, $values['quantity'], $cart, $key );
			$snapshot = $values['skyyrose_preorder_snapshot'] ?? null;
			if ( ( $config['is_preorder'] || null !== $snapshot ) && ! skyyrose2_preorder_promise_matches( $snapshot, $config ) ) {
				throw new Exception( esc_html__( 'The product or pre-order promise in your bag needs review. Remove it, review the product page, and add it again before checkout.', 'skyyrose-flagship-2' ) );
			}
		} catch ( Exception $error ) {
			$messages[] = $error->getMessage();
		}
	}
	return array_unique( $messages );
}

/** Classic cart/checkout adapter. */
function skyyrose2_preorder_check_cart() {
	foreach ( skyyrose2_preorder_cart_errors( WC()->cart ) as $message ) {
		if ( ! wc_has_notice( $message, 'error' ) ) {
			wc_add_notice( $message, 'error' );
		}
	}
}
add_action( 'woocommerce_check_cart_items', 'skyyrose2_preorder_check_cart' );

/**
 * Store API adapter adds native structured validation errors.
 *
 * @param WP_Error $errors Native validation errors.
 * @param WC_Cart  $cart Native cart.
 */
function skyyrose2_preorder_store_cart_errors( $errors, $cart ) {
	foreach ( skyyrose2_preorder_cart_errors( $cart ) as $index => $message ) {
		$errors->add( 'skyyrose_preorder_' . $index, $message );
	}
}
add_action( 'woocommerce_store_api_cart_errors', 'skyyrose2_preorder_store_cart_errors', 10, 2 );

/**
 * Recheck the native cart immediately before new order creation.
 *
 * @throws Exception When a cart promise or allocation is invalid.
 */
function skyyrose2_preorder_validate_new_order() {
	$messages = skyyrose2_preorder_cart_errors( WC()->cart );
	if ( $messages ) {
		throw new Exception( esc_html( reset( $messages ) ) );
	}
}
add_action( 'woocommerce_checkout_create_order', 'skyyrose2_preorder_validate_new_order' );

/**
 * Existing-order payment has no cart. Validate recorded lines, never today's bag.
 *
 * @param WC_Order $order The pending order being paid.
 * @param WP_Error $errors Native payment validation errors.
 */
function skyyrose2_preorder_validate_order_payment( $order, $errors ) {
	$pools = array();
	foreach ( $order->get_items() as $item ) {
		$record = skyyrose2_preorder_read_item( $item );
		if ( 'recorded' !== $record['status'] || empty( $record['snapshot']['is_preorder'] ) ) {
			// Unknown historical promises stay unknown; native Woo validates stock.
			continue;
		}
		try {
			$config                = skyyrose2_preorder_config( $item->get_product_id(), $item->get_variation_id() );
			$config['is_preorder'] = true;
			$pool                  = $config['allocation_source_id'];
			$pools[ $pool ]        = ( $pools[ $pool ] ?? 0 ) + $item->get_quantity();
			skyyrose2_preorder_validate_quantity( $config, $pools[ $pool ], null );
		} catch ( Exception $error ) {
			$errors->add( 'skyyrose_preorder_order', $error->getMessage() );
		}
	}
}
add_action( 'woocommerce_checkout_validate_order_before_payment', 'skyyrose2_preorder_validate_order_payment', 10, 2 );

/**
 * Classic pay-for-order runs outside core's exception handler; emit notices.
 *
 * @param WC_Order $order Existing pending order.
 */
function skyyrose2_preorder_before_pay( $order ) {
	$errors = new WP_Error();
	skyyrose2_preorder_validate_order_payment( $order, $errors );
	foreach ( $errors->get_error_messages() as $message ) {
		wc_add_notice( $message, 'error' );
	}
}
add_action( 'woocommerce_before_pay_action', 'skyyrose2_preorder_before_pay' );

/**
 * Persist once via CRUD; Woo 11.1.2 classic and Store API share this item hook.
 *
 * @param WC_Order_Item_Product $item Native line item.
 * @param string                $key Native cart key.
 * @param array                 $values Native cart values.
 * @throws Exception When the transaction fails validation.
 */
function skyyrose2_preorder_persist_item( $item, $key, $values ) {
	if ( $item->get_id() || $item->meta_exists( '_skyyrose_preorder_snapshot' ) ) {
		return;
	}
	$config   = skyyrose2_preorder_config( $values['product_id'], $values['variation_id'] ?? 0, $values['variation'] ?? array() );
	$snapshot = $values['skyyrose_preorder_snapshot'] ?? null;
	if ( ! $config['is_preorder'] && null === $snapshot ) {
		return;
	}
	if ( ! skyyrose2_preorder_promise_matches( $snapshot, $config ) ) {
		throw new Exception( esc_html__( 'Review the product promise and add the item again before checkout.', 'skyyrose-flagship-2' ) );
	}
	$item->add_meta_data( '_skyyrose_preorder_snapshot', $snapshot, true );
	$item->add_meta_data( '_skyyrose_preorder_schema', $snapshot['schema'], true );
	$item->add_meta_data( '_skyyrose_preorder_schema_version', $snapshot['schema_version'], true );
}
add_action( 'woocommerce_checkout_create_order_line_item', 'skyyrose2_preorder_persist_item', 10, 3 );

/**
 * Deterministic historical reader; never reads current products or writes history.
 *
 * @param WC_Order_Item_Product $item Historical order item.
 */
function skyyrose2_preorder_read_item( $item ) {
	$snapshot = $item->get_meta( '_skyyrose_preorder_snapshot', true );
	if ( ! is_array( $snapshot ) ) {
		return array(
			'status'   => 'legacy_unknown',
			'snapshot' => null,
		);
	}
	$known = 'skyyrose.preorder-commercial-promise' === ( $snapshot['schema'] ?? '' ) && in_array( $snapshot['schema_version'] ?? null, array( 1, 2 ), true );
	return array(
		'status'   => $known ? 'recorded' : 'unsupported_schema',
		'snapshot' => $snapshot,
	);
}

/**
 * Display only recorded facts in native cart/checkout and order/email meta.
 *
 * @param array $data Native display entries.
 * @param array $values Cart line values.
 */
function skyyrose2_preorder_display_cart_data( $data, $values ) {
	$snapshot = $values['skyyrose_preorder_snapshot'] ?? null;
	if ( is_array( $snapshot ) && ! empty( $snapshot['is_preorder'] ) ) {
		$data[] = array(
			'key'   => __( 'Pre-Order', 'skyyrose-flagship-2' ),
			'value' => __( 'Yes', 'skyyrose-flagship-2' ),
		);
		if ( ! empty( $snapshot['expected_ship_date'] ) ) {
			$data[] = array(
				'key'   => __( 'Expected ship date', 'skyyrose-flagship-2' ),
				'value' => esc_html( $snapshot['expected_ship_date'] ),
			);
		}
	}
	return $data;
}
add_filter( 'woocommerce_get_item_data', 'skyyrose2_preorder_display_cart_data', 10, 2 );

/**
 * Add display entries without adding mutable public metadata to persisted items.
 *
 * @param array                 $formatted Native formatted metadata.
 * @param WC_Order_Item_Product $item Historical order item.
 */
function skyyrose2_preorder_display_order_meta( $formatted, $item ) {
	$record = skyyrose2_preorder_read_item( $item );
	if ( 'recorded' !== $record['status'] || empty( $record['snapshot']['is_preorder'] ) ) {
		return $formatted;
	}
	$entries = array( __( 'Pre-Order', 'skyyrose-flagship-2' ) => __( 'Yes', 'skyyrose-flagship-2' ) );
	if ( ! empty( $record['snapshot']['expected_ship_date'] ) ) {
		$entries[ __( 'Expected ship date', 'skyyrose-flagship-2' ) ] = $record['snapshot']['expected_ship_date'];
	}
	foreach ( $entries as $label => $value ) {
		$formatted[ 'skyyrose_' . sanitize_key( $label ) ] = (object) array(
			'key'           => $label,
			'value'         => $value,
			'display_key'   => esc_html( $label ),
			'display_value' => esc_html( $value ),
		);
	}
	return $formatted;
}
add_filter( 'woocommerce_order_item_get_formatted_meta_data', 'skyyrose2_preorder_display_order_meta', 10, 2 );

/**
 * Snapshot minimal referral attribution; no email/PII or financial reward writes.
 *
 * @param WC_Order $order Accepted native order.
 */
function skyyrose2_preorder_capture_referral( $order ) {
	if ( $order->meta_exists( '_skyyrose_referral_attribution' ) || $order->get_meta( '_skyyrose_referral_credited', true ) ) {
		return;
	}
	foreach ( $order->get_coupon_codes() as $code ) {
		if ( 0 !== stripos( $code, 'SKYY' ) ) {
			continue;
		}
		$coupon = new WC_Coupon( $code );
		$email  = $coupon->get_meta( '_skyyrose_referral_owner_email', true );
		$owner  = is_email( $email ) ? get_user_by( 'email', $email ) : false;
		if ( ! $coupon->get_id() || ! $owner || strtolower( $email ) === strtolower( $order->get_billing_email() ) || (int) $owner->ID === (int) $order->get_customer_id() ) {
			continue;
		}
		$order->update_meta_data(
			'_skyyrose_referral_attribution',
			array(
				'schema_version' => 1,
				'coupon_id'      => $coupon->get_id(),
				'referrer_id'    => (int) $owner->ID,
			)
		);
		$order->save();
		return;
	}
}
add_action( 'woocommerce_checkout_order_created', 'skyyrose2_preorder_capture_referral' );
add_action( 'woocommerce_store_api_checkout_order_processed', 'skyyrose2_preorder_capture_referral' );
