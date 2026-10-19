<?php
/** Canonical simple-product size customization; native price and pooled stock remain authoritative. */
defined( 'ABSPATH' ) || exit;

/** Consumer projection travels with V2; the inactive legacy theme is never read at runtime. */
function skyyrose2_simple_size_projection() {
	$path = SKYYROSE2_DIR . '/data/simple-product-sizes.json';
	$real = realpath( $path );
	$root = realpath( SKYYROSE2_DIR );
	if ( ! $real || ! $root || is_link( $path ) || ! is_file( $real ) || 0 !== strpos( $real, $root . DIRECTORY_SEPARATOR ) || filesize( $real ) > 1048576 ) {
		throw new Exception( __( 'Size options are temporarily unavailable. Please try again later.', 'skyyrose-flagship-2' ) );
	}
	try {
		$data = json_decode( file_get_contents( $real ), true, 64, JSON_THROW_ON_ERROR );
		$presentation = skyyrose2_presentation_registry();
		if ( ! is_array( $data ) || 'skyyrose.simple-product-sizes.v1' !== ( $data['schema'] ?? '' ) || ! is_array( $data['products'] ?? null ) || empty( $data['products'] ) ) { throw new Exception(); }
		foreach ( array( 'product_registry_sha256', 'source_reader_sha256', 'products_sha256' ) as $key ) {
			if ( ! is_string( $data[ $key ] ?? null ) || ! preg_match( '/^[a-f0-9]{64}$/D', $data[ $key ] ) ) { throw new Exception(); }
		}
		if ( ! hash_equals( $data['product_registry_sha256'], $presentation['product_registry_sha256'] ?? '' ) || ! hash_equals( $data['products_sha256'], hash( 'sha256', json_encode( $data['products'], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR ) ) ) ) { throw new Exception(); }
		foreach ( $data['products'] as $sku => $record ) {
			if ( ! is_string( $sku ) || ! preg_match( '/^[a-z0-9]+-[a-z0-9-]+$/D', $sku ) || ! is_array( $record ) || array( 'sizes' ) !== array_keys( $record ) || ! is_array( $record['sizes'] ) || ! array_is_list( $record['sizes'] ) || ! $record['sizes'] ) { throw new Exception(); }
			foreach ( $record['sizes'] as $size ) {
				if ( ! is_string( $size ) || '' === $size || strlen( $size ) > 256 || preg_match( '/[\x00-\x1f]/', $size ) ) { throw new Exception(); }
			}
			if ( count( array_unique( $record['sizes'], SORT_STRING ) ) !== count( $record['sizes'] ) ) { throw new Exception(); }
		}
		return $data;
	} catch ( Throwable $error ) {
		throw new Exception( __( 'Size options are temporarily unavailable. Please try again later.', 'skyyrose-flagship-2' ) );
	}
}

/** Explicit trusted inventory only. Never initialize or extend this state from a purchase request. */
function skyyrose2_simple_size_history_state() {
	global $wpdb;
	$raw = $wpdb->get_var( $wpdb->prepare( "SELECT option_value FROM {$wpdb->options} WHERE option_name=%s", 'skyyrose2_simple_size_history_v1' ) );
	$state = is_string( $raw ) && strlen( $raw ) <= 1048576 && ! $wpdb->last_error ? json_decode( $raw, true ) : null;
	if ( ! is_array( $state ) || 'skyyrose.simple-size-history.v1' !== ( $state['schema'] ?? '' ) || untrailingslashit( get_option( 'home' ) ) !== ( $state['site'] ?? null ) || 'skyyrose.simple-size-order.v1' !== ( $state['generation'] ?? '' ) || ! is_array( $state['legacy_orders'] ?? null ) ) {
		throw new Exception( __( 'Size options are temporarily unavailable. Please try again later.', 'skyyrose-flagship-2' ) );
	}
	foreach ( $state['legacy_orders'] as $id => $fingerprint ) {
		if ( ! preg_match( '/^[1-9][0-9]*$/D', (string) $id ) || ! is_string( $fingerprint ) || ! preg_match( '/^[a-f0-9]{64}$/D', $fingerprint ) ) {
			throw new Exception( __( 'Size options are temporarily unavailable. Please try again later.', 'skyyrose-flagship-2' ) );
		}
	}
	return $state;
}

/** Derive identity from the native product, never a client SKU or an inherited CSV. */
function skyyrose2_simple_size_choices( $product ) {
	if ( ! $product || ! $product->is_type( 'simple' ) ) { return null; }
	skyyrose2_simple_size_history_state();
	$projection = skyyrose2_simple_size_projection();
	$sku = $product->get_sku();
	if ( ! is_string( $sku ) || ! isset( $projection['products'][ $sku ] ) || $product->get_id() <= 0 ) {
		throw new Exception( __( 'Size options are temporarily unavailable. Please try again later.', 'skyyrose-flagship-2' ) );
	}
	return array( 'product_id' => (int) $product->get_id(), 'sku' => $sku, 'sizes' => $projection['products'][ $sku ]['sizes'] );
}

/** Exact strings survive cart hashing: no timestamp, registry digest or variation ID is invented. */
function skyyrose2_simple_size_selection( $product, $size ) {
	$choices = skyyrose2_simple_size_choices( $product );
	if ( ! $choices ) { return null; }
	if ( ! is_string( $size ) || ! in_array( $size, $choices['sizes'], true ) ) {
		throw new Exception( __( 'Choose a valid size on the product page before adding this item to your bag.', 'skyyrose-flagship-2' ) );
	}
	return array( 'schema' => 'skyyrose.simple-size-selection.v1', 'product_id' => $choices['product_id'], 'sku' => $choices['sku'], 'size' => $size );
}

/** Cart/session/quantity/checkout validation never repairs an unknown selection silently. */
function skyyrose2_simple_size_cart_selection( $values ) {
	$product = wc_get_product( $values['product_id'] ?? 0 );
	$record = $values['skyyrose_simple_size'] ?? null;
	if ( ! $product || ! $product->is_type( 'simple' ) || ! empty( $values['variation_id'] ) ) {
		if ( null !== $record ) { throw new Exception( __( 'Review this item and choose its size again on the product page.', 'skyyrose-flagship-2' ) ); }
		return null;
	}
	$expected = skyyrose2_simple_size_selection( $product, is_array( $record ) ? ( $record['size'] ?? null ) : null );
	if ( $record !== $expected ) { throw new Exception( __( 'Review this item and choose its size again on the product page.', 'skyyrose-flagship-2' ) ); }
	return $expected;
}

/** Complete, deterministic native line membership for provenance and new-order immutability. */
function skyyrose2_simple_size_meta_values( $object, $key ) {
	// WC_Data::get_meta($key, false) returns WC_Meta_Data objects, with retained keys.
	return array_values( array_map( static fn( $meta ) => $meta->get_data()['value'], $object->get_meta( $key, false, 'edit' ) ) );
}

function skyyrose2_simple_size_order_lines( $order, $with_size = false ) {
	$lines = array();
	foreach ( $order->get_items( 'line_item' ) as $item ) {
		$line = array( 'product_id' => (int) $item->get_product_id( 'edit' ), 'variation_id' => (int) $item->get_variation_id( 'edit' ), 'quantity' => $item->get_quantity( 'edit' ) );
		if ( $line['product_id'] <= 0 || ! is_numeric( $line['quantity'] ) || ! is_finite( (float) $line['quantity'] ) || (float) $line['quantity'] <= 0 || floor( (float) $line['quantity'] ) !== (float) $line['quantity'] ) { throw new Exception( __( 'This order needs review before payment.', 'skyyrose-flagship-2' ) ); }
		$line['quantity'] = (string) $line['quantity'];
		if ( $with_size && ! $line['variation_id'] ) {
			$records = skyyrose2_simple_size_meta_values( $item, '_skyyrose_simple_size_v1' );
			$visible = skyyrose2_simple_size_meta_values( $item, 'Size' );
			if ( 1 !== count( $records ) || 1 !== count( $visible ) || ! is_array( $records[0] ) || array( 'schema', 'product_id', 'sku', 'size' ) !== array_keys( $records[0] ) || 'skyyrose.simple-size-selection.v1' !== $records[0]['schema'] || $line['product_id'] !== $records[0]['product_id'] || ! is_string( $records[0]['sku'] ) || '' === $records[0]['sku'] || ! is_string( $records[0]['size'] ) || '' === $records[0]['size'] || $visible[0] !== $records[0]['size'] ) { throw new Exception( __( 'This order needs its saved size reviewed before payment.', 'skyyrose-flagship-2' ) ); }
			$line['selection'] = $records[0];
		} elseif ( $with_size && $item->meta_exists( '_skyyrose_simple_size_v1' ) ) {
			throw new Exception( __( 'Review the saved product option before payment.', 'skyyrose-flagship-2' ) );
		} elseif ( ! $with_size ) {
			$line['item_id'] = (int) $item->get_id();
			if ( $line['item_id'] <= 0 ) { throw new Exception( __( 'This order needs review before payment.', 'skyyrose-flagship-2' ) ); }
		}
		$lines[] = $line;
	}
	usort( $lines, static fn( $left, $right ) => strcmp( wp_json_encode( $left ), wp_json_encode( $right ) ) );
	return $lines;
}

/** Existing IDs, key, creation date and complete line membership are mandatory. */
function skyyrose2_simple_size_legacy_fingerprint( $order ) {
	$date = $order->get_date_created( 'edit' );
	$key = $order->get_order_key( 'edit' );
	if ( $order->get_id() <= 0 || ! $date || ! is_string( $key ) || '' === $key ) { throw new Exception( __( 'This order needs review before payment.', 'skyyrose-flagship-2' ) ); }
	return hash( 'sha256', wp_json_encode( array( 'id' => (int) $order->get_id(), 'key_sha256' => hash( 'sha256', $key ), 'created' => $date->getTimestamp(), 'lines' => skyyrose2_simple_size_order_lines( $order ) ) ) );
}

/** Persisted selections govern payment; current registry membership is intentionally not consulted. */
function skyyrose2_simple_size_validate_saved_order( $order ) {
	$lines = $order->get_items( 'line_item' );
	if ( ! $lines ) { throw new Exception( __( 'This order needs review before payment.', 'skyyrose-flagship-2' ) ); }
	$has_simple = false;
	foreach ( $lines as $item ) { $has_simple = $has_simple || ! $item->get_variation_id( 'edit' ); }
	$generations = skyyrose2_simple_size_meta_values( $order, '_skyyrose_simple_size_generation_v1' );
	if ( ! $has_simple && ! $generations ) { return; }
	$state = skyyrose2_simple_size_history_state();
	if ( ! $generations ) {
		// Absence of both fields is never historical provenance.
		$expected = $state['legacy_orders'][ $order->get_id() ] ?? null;
		if ( ! is_string( $expected ) || ! hash_equals( $expected, skyyrose2_simple_size_legacy_fingerprint( $order ) ) ) { throw new Exception( __( 'This order needs its saved size reviewed before payment.', 'skyyrose-flagship-2' ) ); }
		return;
	}
	$manifest = array( 'schema' => 'skyyrose.simple-size-order.v1', 'lines' => skyyrose2_simple_size_order_lines( $order, true ) );
	if ( 1 !== count( $generations ) || $generations[0] !== $manifest || ! $has_simple ) { throw new Exception( __( 'This order needs its saved size reviewed before payment.', 'skyyrose-flagship-2' ) ); }
}

/** Native form remains responsible for quantity, price, stock and submission. */
function skyyrose2_simple_size_render() {
	global $product;
	if ( ! $product || ! $product->is_type( 'simple' ) ) { return; }
	try {
		$choices = skyyrose2_simple_size_choices( $product );
		echo '<p class="form-row form-row-wide skyyrose2-simple-size"><label for="skyyrose-simple-size">' . esc_html__( 'Size', 'skyyrose-flagship-2' ) . ' <span aria-hidden="true">*</span></label><select id="skyyrose-simple-size" name="skyyrose_simple_size" required aria-required="true">';
		if ( 1 !== count( $choices['sizes'] ) ) { echo '<option value="">' . esc_html__( 'Choose size', 'skyyrose-flagship-2' ) . '</option>'; }
		foreach ( $choices['sizes'] as $size ) { echo '<option value="' . esc_attr( $size ) . '">' . esc_html( $size ) . '</option>'; }
		echo '</select></p>';
	} catch ( Exception $error ) {
		echo '<p class="woocommerce-info" role="status">' . esc_html( $error->getMessage() ) . '</p>';
	}
}
add_action( 'woocommerce_before_add_to_cart_button', 'skyyrose2_simple_size_render', 5 );

function skyyrose2_simple_size_purchasable( $purchasable, $product ) {
	if ( ! $purchasable || ! $product->is_type( 'simple' ) ) { return $purchasable; }
	try { skyyrose2_simple_size_choices( $product ); return $purchasable; }
	catch ( Exception $error ) { return false; }
}
add_filter( 'woocommerce_is_purchasable', 'skyyrose2_simple_size_purchasable', 20, 2 );

function skyyrose2_simple_size_unavailable() {
	global $product;
	if ( ! $product || ! $product->is_type( 'simple' ) ) { return; }
	try { skyyrose2_simple_size_choices( $product ); }
	catch ( Exception $error ) { echo '<p class="woocommerce-info" role="status">' . esc_html( $error->getMessage() ) . '</p>'; }
}
add_action( 'woocommerce_single_product_summary', 'skyyrose2_simple_size_unavailable', 29 );

/** Loops and quick-view links take customers to the selector, without AJAX adds. */
function skyyrose2_simple_size_loop_url( $url, $product ) { return $product->is_type( 'simple' ) ? $product->get_permalink() : $url; }
function skyyrose2_simple_size_loop_text( $text, $product ) { return $product->is_type( 'simple' ) ? __( 'Choose size', 'skyyrose-flagship-2' ) : $text; }
function skyyrose2_simple_size_supports( $supports, $feature, $product ) { return 'ajax_add_to_cart' === $feature && $product->is_type( 'simple' ) ? false : $supports; }
add_filter( 'woocommerce_product_add_to_cart_url', 'skyyrose2_simple_size_loop_url', 20, 2 );
add_filter( 'woocommerce_product_add_to_cart_text', 'skyyrose2_simple_size_loop_text', 20, 2 );
add_filter( 'woocommerce_product_supports', 'skyyrose2_simple_size_supports', 20, 3 );

// These wallet renderers do not submit the native custom selector. Bag/checkout wallets
// retain their native eligibility and run only after the ordinary cart validation.
function skyyrose2_simple_size_wallet_supported( $supported, $product ) { return $product && $product->is_type( 'simple' ) ? false : $supported; }
function skyyrose2_simple_size_hide_stripe_wallet( $hide, $post ) {
	$product = $post ? wc_get_product( $post->ID ) : null;
	return $hide || ( $product && $product->is_type( 'simple' ) );
}
add_filter( 'wcpay_payment_request_is_product_supported', 'skyyrose2_simple_size_wallet_supported', 20, 2 );
add_filter( 'wc_stripe_hide_payment_request_on_product_page', 'skyyrose2_simple_size_hide_stripe_wallet', 20, 2 );

/** Actual Store API ingress: accept only the namespaced string before cart hashing. */
function skyyrose2_simple_size_store_input( $data, $request ) {
	$extensions = $request->get_param( 'extensions' );
	$input = is_array( $extensions ) ? ( $extensions['skyyrose-simple-size'] ?? null ) : null;
	if ( null !== $input && ( ! is_array( $input ) || array( 'size' ) !== array_keys( $input ) || ! is_string( $input['size'] ) ) ) {
		throw new \Automattic\WooCommerce\StoreApi\Exceptions\RouteException( 'skyyrose_simple_size_input', __( 'Choose a valid size on the product page.', 'skyyrose-flagship-2' ), 400 );
	}
	$data['cart_item_data']['_skyyrose_size_input'] = array( 'size' => $input['size'] ?? null );
	return $data;
}
add_filter( 'woocommerce_store_api_add_to_cart_data', 'skyyrose2_simple_size_store_input', 5, 2 );

function skyyrose2_simple_size_add_cart_data( $data, $product_id, $variation_id = 0 ) {
	$product = wc_get_product( $product_id );
	$api = array_key_exists( '_skyyrose_size_input', $data );
	$size = $api ? $data['_skyyrose_size_input']['size'] : ( isset( $_POST['skyyrose_simple_size'] ) ? wp_unslash( $_POST['skyyrose_simple_size'] ) : null ); // phpcs:ignore WordPress.Security.NonceVerification.Missing -- Native Woo add-to-cart request validation.
	unset( $data['_skyyrose_size_input'], $data['skyyrose_simple_size'] );
	if ( $product && $product->is_type( 'simple' ) && ! $variation_id ) {
		try { $data['skyyrose_simple_size'] = skyyrose2_simple_size_selection( $product, $size ); }
		catch ( Exception $error ) {
			if ( $api ) { throw new \Automattic\WooCommerce\StoreApi\Exceptions\RouteException( 'skyyrose_simple_size_input', $error->getMessage(), 400 ); }
			throw $error;
		}
	} elseif ( null !== $size ) { throw new Exception( __( 'Review the selected product option.', 'skyyrose-flagship-2' ) ); }
	return $data;
}
add_filter( 'woocommerce_add_cart_item_data', 'skyyrose2_simple_size_add_cart_data', 5, 3 );

function skyyrose2_simple_size_display_cart( $data, $values ) {
	try {
		$selection = skyyrose2_simple_size_cart_selection( $values );
		if ( $selection ) { $data[] = array( 'key' => __( 'Size', 'skyyrose-flagship-2' ), 'value' => $selection['size'] ); }
	} catch ( Exception $error ) { $data[] = array( 'key' => __( 'Size', 'skyyrose-flagship-2' ), 'value' => __( 'Choose again on the product page', 'skyyrose-flagship-2' ) ); }
	return $data;
}
add_filter( 'woocommerce_get_item_data', 'skyyrose2_simple_size_display_cart', 5, 2 );

function skyyrose2_simple_size_cart_errors( $cart ) {
	$messages = array();
	if ( ! $cart ) { return $messages; }
	foreach ( $cart->get_cart() as $values ) {
		try { skyyrose2_simple_size_cart_selection( $values ); }
		catch ( Exception $error ) { $messages[] = $error->getMessage(); }
	}
	return array_values( array_unique( $messages ) );
}
function skyyrose2_simple_size_check_cart() {
	foreach ( skyyrose2_simple_size_cart_errors( WC()->cart ) as $message ) {
		if ( ! wc_has_notice( $message, 'error' ) ) { wc_add_notice( $message, 'error' ); }
	}
}
add_action( 'woocommerce_check_cart_items', 'skyyrose2_simple_size_check_cart', 5 );
function skyyrose2_simple_size_update_quantity( $passed, $key, $values ) {
	try { skyyrose2_simple_size_cart_selection( $values ); }
	catch ( Exception $error ) { wc_add_notice( $error->getMessage(), 'error' ); return false; }
	return $passed;
}
add_filter( 'woocommerce_update_cart_validation', 'skyyrose2_simple_size_update_quantity', 5, 3 );
/** Store API update-item and existing-line top-ups have their own pre-write hook. */
function skyyrose2_simple_size_store_quantity( $valid, $quantity, $product, $values ) {
	if ( is_wp_error( $valid ) ) { return $valid; }
	try { skyyrose2_simple_size_cart_selection( $values ); }
	catch ( Exception $error ) { return new WP_Error( 'skyyrose_simple_size_quantity', $error->getMessage() ); }
	return $valid;
}
add_filter( 'woocommerce_store_api_cart_item_quantity_validation', 'skyyrose2_simple_size_store_quantity', 5, 4 );

/** Persist separate size metadata; do not overwrite the preorder promise. */
function skyyrose2_simple_size_persist_item( $item, $key, $values ) {
	$selection = skyyrose2_simple_size_cart_selection( $values );
	if ( ! $selection ) { return; }
	if ( $item->get_id() || $item->meta_exists( '_skyyrose_simple_size_v1' ) || $item->meta_exists( 'Size' ) ) { throw new Exception( __( 'Review the saved size before checkout.', 'skyyrose-flagship-2' ) ); }
	$item->add_meta_data( '_skyyrose_simple_size_v1', $selection, true );
	$item->add_meta_data( 'Size', $selection['size'], true );
}
add_action( 'woocommerce_checkout_create_order_line_item', 'skyyrose2_simple_size_persist_item', 5, 3 );

/** Capture only on an explicit new-order event, never by missing marker inference. */
function skyyrose2_simple_size_stamp_new_order( $order ) {
	$messages = skyyrose2_simple_size_cart_errors( WC()->cart );
	if ( $messages ) { throw new Exception( reset( $messages ) ); }
	$lines = skyyrose2_simple_size_order_lines( $order, true );
	$has_simple = false;
	foreach ( $lines as $line ) { $has_simple = $has_simple || ! $line['variation_id']; }
	if ( ! $has_simple ) { return; }
	skyyrose2_simple_size_history_state();
	if ( $order->meta_exists( '_skyyrose_simple_size_generation_v1' ) ) { throw new Exception( __( 'Review the saved size before checkout.', 'skyyrose-flagship-2' ) ); }
	$order->add_meta_data( '_skyyrose_simple_size_generation_v1', array( 'schema' => 'skyyrose.simple-size-order.v1', 'lines' => $lines ), true );
}
function skyyrose2_simple_size_classic_order( $order ) {
	if ( $order->get_id() ) { skyyrose2_simple_size_validate_saved_order( $order ); }
	else { skyyrose2_simple_size_stamp_new_order( $order ); }
}
add_action( 'woocommerce_checkout_create_order', 'skyyrose2_simple_size_classic_order', 5 );
function skyyrose2_simple_size_api_new_order( $order ) {
	skyyrose2_simple_size_stamp_new_order( $order );
	$order->save();
}
add_action( 'woocommerce_store_api_checkout_order_created', 'skyyrose2_simple_size_api_new_order', 5 );

/** Refuse before Woo removes/rebuilds saved line items on resumed checkout. */
function skyyrose2_simple_size_resume_order( $order_id ) {
	$order = new WC_Order( $order_id );
	skyyrose2_simple_size_validate_saved_order( $order );
	foreach ( $order->get_items( 'line_item' ) as $item ) {
		if ( ! $item->get_variation_id( 'edit' ) && ! $order->meta_exists( '_skyyrose_simple_size_generation_v1' ) ) { throw new Exception( __( 'Start a new bag to choose sizes for this order.', 'skyyrose-flagship-2' ) ); }
	}
}
function skyyrose2_simple_size_classic_resume( $order_id ) {
	skyyrose2_simple_size_resume_order( $order_id );
	$order = new WC_Order( $order_id );
	foreach ( $order->get_items( 'line_item' ) as $item ) {
		if ( ! $item->get_variation_id( 'edit' ) ) {
			WC()->session->set( 'order_awaiting_payment', 0 );
			throw new Exception( __( 'Your saved order is unchanged. Use its payment link, or try checkout again to create a new order.', 'skyyrose-flagship-2' ) );
		}
	}
}
add_action( 'woocommerce_resume_order', 'skyyrose2_simple_size_classic_resume', 5 );

/** Order-again bypasses normal cart-data ingress. Explicitly request fresh selection. */
function skyyrose2_simple_size_order_again_data( $data, $item ) {
	$product = $item->get_product();
	if ( $product && $product->is_type( 'simple' ) ) { $data['_skyyrose_size_reselect'] = true; }
	return $data;
}
add_filter( 'woocommerce_order_again_cart_item_data', 'skyyrose2_simple_size_order_again_data', 5, 2 );
function skyyrose2_simple_size_order_again_validation( $passed, $product_id, $quantity, $variation_id = 0, $variation = array(), $data = array() ) {
	if ( empty( $data['_skyyrose_size_reselect'] ) ) { return $passed; }
	$product = wc_get_product( $product_id );
	if ( ! $product ) { return false; }
	wc_add_notice( sprintf( '%s <a href="%s">%s</a>', esc_html__( 'Choose a size again for this item.', 'skyyrose-flagship-2' ), esc_url( $product->get_permalink() ), esc_html__( 'Choose size', 'skyyrose-flagship-2' ) ), 'notice' );
	return false;
}
add_filter( 'woocommerce_add_to_cart_validation', 'skyyrose2_simple_size_order_again_validation', 5, 6 );

function skyyrose2_simple_size_store_errors( $errors, $cart ) {
	foreach ( skyyrose2_simple_size_cart_errors( $cart ) as $index => $message ) { $errors->add( 'skyyrose_simple_size_' . $index, $message ); }
}
add_action( 'woocommerce_store_api_cart_errors', 'skyyrose2_simple_size_store_errors', 5, 2 );

/** Woo reads the cart hash before deleting/rebuilding order lines, on GET/PATCH,
 * POST and cart synchronisation. Cart-errors alone runs too late on GET/PATCH.
 * Use the supplied hash so this check cannot recursively calculate a hash.
 */
function skyyrose2_simple_size_native_header_hash() {
	$class = 'Automattic\\WooCommerce\\StoreApi\\Routes\\V1\\AbstractCartRoute';
	if ( ! defined( 'WC_ABSPATH' ) || ! class_exists( $class ) ) { return false; }
	$method = new ReflectionMethod( $class, 'add_response_headers' );
	$source = realpath( WC_ABSPATH . 'src/StoreApi/Routes/V1/AbstractCartRoute.php' );
	if ( ! $source || $class !== $method->getDeclaringClass()->getName() || realpath( $method->getFileName() ) !== $source ) { return false; }
	$stack = debug_backtrace( DEBUG_BACKTRACE_IGNORE_ARGS | DEBUG_BACKTRACE_PROVIDE_OBJECT, 12 );
	foreach ( $stack as $index => $frame ) {
		if ( 'get_cart_hash' !== ( $frame['function'] ?? '' ) ) { continue; }
		$caller = $stack[ $index + 1 ] ?? array();
		if ( 'WC_Cart' === ( $frame['class'] ?? '' ) && 'get_cart_hash' === ( $frame['function'] ?? '' )
			&& $source === realpath( $frame['file'] ?? '' ) && ( $frame['line'] ?? 0 ) >= $method->getStartLine() && ( $frame['line'] ?? 0 ) <= $method->getEndLine()
			&& $class === ( $caller['class'] ?? '' ) && 'add_response_headers' === ( $caller['function'] ?? '' ) && ( $caller['object'] ?? null ) instanceof $class ) {
			return true;
		}
		// A native header ancestor cannot exempt a nested functional hash.
		return false;
	}
	return false;
}

function skyyrose2_simple_size_guard_api_draft( $hash ) {
	if ( ! WC()->is_store_api_request() || ! WC()->session ) { return $hash; }
	// Native formatting runs outside its RouteException catch. It only reads the
	// hash for a response header; every functional hash call still checks history.
	if ( skyyrose2_simple_size_native_header_hash() ) { return $hash; }
	$id = WC()->session->get( 'store_api_draft_order', 0 );
	if ( ! $id ) { return $hash; }
	try {
		$order = new WC_Order( $id );
		$affected = $order->meta_exists( '_skyyrose_simple_size_generation_v1' );
		foreach ( $order->get_items( 'line_item' ) as $item ) { $affected = $affected || ! $item->get_variation_id( 'edit' ); }
		if ( ! $affected ) { return $hash; }
		if ( ! $order->has_status( 'checkout-draft' ) && ! ( $order->needs_payment() && $order->has_cart_hash( $hash ) ) ) { return $hash; }
		skyyrose2_simple_size_resume_order( $id );
		if ( ! $order->has_cart_hash( $hash ) ) {
			// Detach only the session pointer, preserving the native order. Refuse this
			// request because core may already hold the old order in a local variable.
			WC()->session->set( 'store_api_draft_order', 0 );
			throw new Exception( __( 'Your bag changed. Please try checkout again.', 'skyyrose-flagship-2' ) );
		}
	} catch ( Exception $error ) {
		throw new \Automattic\WooCommerce\StoreApi\Exceptions\RouteException( 'skyyrose_simple_size_saved_order', $error->getMessage(), 409 );
	}
	return $hash;
}
add_filter( 'woocommerce_cart_hash', 'skyyrose2_simple_size_guard_api_draft', 5 );

/** Native cart synchronization also runs outside Woo's RouteException handler.
 * Preserve ordinary dispatch/permissions and catch only our saved-history refusal
 * around the original native callback, without retrying or bypassing any guard.
 */
function skyyrose2_simple_size_store_route_boundary( $endpoints ) {
	if ( ! defined( 'WC_ABSPATH' ) ) { return $endpoints; }
	$native = array(
		'Automattic\\WooCommerce\\StoreApi\\Routes\\V1\\AbstractCartRoute' => 'AbstractCartRoute.php',
		'Automattic\\WooCommerce\\StoreApi\\Routes\\V1\\Checkout' => 'Checkout.php',
	);
	foreach ( $endpoints as $route => &$handlers ) {
		if ( ! preg_match( '#^/wc/store/v[0-9]+/(?:cart(?:/|$)|checkout(?:/|$))#', $route ) || ! is_array( $handlers ) ) { continue; }
		foreach ( $handlers as &$handler ) {
			$callback = is_array( $handler ) ? ( $handler['callback'] ?? null ) : null;
			if ( ! is_array( $callback ) || 2 !== count( $callback ) || ! ( $callback[0] ?? null ) instanceof \Automattic\WooCommerce\StoreApi\Routes\V1\AbstractCartRoute || 'get_response' !== ( $callback[1] ?? null ) ) { continue; }
			$method = new ReflectionMethod( $callback[0], 'get_response' );
			$declaring = $method->getDeclaringClass()->getName();
			if ( ! isset( $native[ $declaring ] ) ) { continue; }
			$source = realpath( WC_ABSPATH . 'src/StoreApi/Routes/V1/' . $native[ $declaring ] );
			if ( ! $source || realpath( $method->getFileName() ) !== $source ) { continue; }
			$handler['callback'] = static function( $request ) use ( $callback ) {
				try { return call_user_func( $callback, $request ); }
				catch ( \Automattic\WooCommerce\StoreApi\Exceptions\RouteException $error ) {
					if ( 'skyyrose_simple_size_saved_order' !== $error->getErrorCode() || 409 !== $error->getCode() ) { throw $error; }
					return new WP_Error( $error->getErrorCode(), $error->getMessage(), array( 'status' => 409 ) );
				}
			};
		}
		unset( $handler );
	}
	unset( $handlers );
	return $endpoints;
}
add_filter( 'rest_endpoints', 'skyyrose2_simple_size_store_route_boundary', 20 );

/** Fresh persisted state is mandatory on both payment entry points. */
function skyyrose2_simple_size_payment( $order, $errors ) {
	try {
		if ( ! $order->get_id() || ! wc_get_order( $order->get_id() ) ) { throw new Exception( __( 'A saved order is required before payment.', 'skyyrose-flagship-2' ) ); }
		$fresh = new WC_Order( $order->get_id() );
		skyyrose2_simple_size_validate_saved_order( $fresh );
		if ( skyyrose2_simple_size_order_lines( $order ) !== skyyrose2_simple_size_order_lines( $fresh ) || skyyrose2_simple_size_meta_values( $order, '_skyyrose_simple_size_generation_v1' ) !== skyyrose2_simple_size_meta_values( $fresh, '_skyyrose_simple_size_generation_v1' ) ) { throw new Exception( __( 'Save and review this order before payment.', 'skyyrose-flagship-2' ) ); }
		if ( $fresh->meta_exists( '_skyyrose_simple_size_generation_v1' ) ) { skyyrose2_simple_size_validate_saved_order( $order ); }
	} catch ( Exception $error ) { $errors->add( 'skyyrose_simple_size_order', $error->getMessage() ); }
}
add_action( 'woocommerce_checkout_validate_order_before_payment', 'skyyrose2_simple_size_payment', 5, 2 );
/** Classic checkout does not fire Store API's before-payment validation hook.
 * This native event runs after order save and before process_order_payment.
 */
function skyyrose2_simple_size_classic_persisted_order( $id, $posted, $order ) {
	$errors = new WP_Error();
	skyyrose2_simple_size_payment( $order, $errors );
	if ( $errors->has_errors() ) { throw new Exception( $errors->get_error_message() ); }
}
add_action( 'woocommerce_checkout_order_processed', 'skyyrose2_simple_size_classic_persisted_order', 5, 3 );
function skyyrose2_simple_size_before_pay( $order ) {
	$errors = new WP_Error();
	skyyrose2_simple_size_payment( $order, $errors );
	foreach ( $errors->get_error_messages() as $message ) { wc_add_notice( $message, 'error' ); }
}
add_action( 'woocommerce_before_pay_action', 'skyyrose2_simple_size_before_pay', 5 );
