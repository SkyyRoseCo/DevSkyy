<?php
/**
 * WooCommerce Pre-Order & Referral System
 *
 * Pre-order meta fields, cart/order snapshots, allocation validation,
 * front-end notices, button text overrides, and referral credit logic.
 *
 * Split from inc/woocommerce.php for maintainability.
 *
 * @package SkyyRose
 * @since   6.3.0
 */

// Prevent direct access.
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/*
--------------------------------------------------------------
 * Pre-Order Meta Fields
 *--------------------------------------------------------------*/

/**
 * Register the pre-order meta box on product edit screens.
 *
 * Adds fields for: pre-order status, edition size, available quantity,
 * and expected ship date.
 *
 * @since 3.10.0
 * @return void
 */
function skyyrose_add_preorder_meta_box() {
	add_meta_box(
		'skyyrose_preorder_settings',
		esc_html__( 'Pre-Order Settings', 'skyyrose' ),
		'skyyrose_preorder_meta_box_callback',
		'product',
		'side',
		'high'
	);
}
add_action( 'add_meta_boxes', 'skyyrose_add_preorder_meta_box' );

/**
 * Render the pre-order meta box UI.
 *
 * @since 3.10.0
 *
 * @param WP_Post $post Current post object.
 * @return void
 */
function skyyrose_preorder_meta_box_callback( $post ) {

	wp_nonce_field( 'skyyrose_preorder_nonce', 'skyyrose_preorder_nonce' );

	$is_preorder  = get_post_meta( $post->ID, '_is_preorder', true );
	$edition_size = get_post_meta( $post->ID, '_preorder_edition_size', true );
	$available    = get_post_meta( $post->ID, '_preorder_available', true );
	$ship_date    = get_post_meta( $post->ID, '_preorder_ship_date', true );
	?>
	<p>
		<label>
			<input type="checkbox" name="skyyrose_is_preorder" value="1" <?php checked( $is_preorder, '1' ); ?> />
			<?php esc_html_e( 'This is a pre-order product', 'skyyrose' ); ?>
		</label>
	</p>
	<p>
		<label for="skyyrose_edition_size"><?php esc_html_e( 'Edition Size', 'skyyrose' ); ?></label>
		<input type="number" id="skyyrose_edition_size" name="skyyrose_edition_size" value="<?php echo esc_attr( $edition_size ); ?>" min="1" style="width:100%;" placeholder="e.g. 250" />
	</p>
	<p>
		<label for="skyyrose_preorder_available"><?php esc_html_e( 'Available Remaining', 'skyyrose' ); ?></label>
		<input type="number" id="skyyrose_preorder_available" name="skyyrose_preorder_available" value="<?php echo esc_attr( $available ); ?>" min="0" style="width:100%;" />
	</p>
	<p>
		<label for="skyyrose_ship_date"><?php esc_html_e( 'Expected Ship Date', 'skyyrose' ); ?></label>
		<input type="date" id="skyyrose_ship_date" name="skyyrose_ship_date" value="<?php echo esc_attr( $ship_date ); ?>" style="width:100%;" />
	</p>
	<?php
}

/**
 * Save pre-order meta box data.
 *
 * @since 3.10.0
 *
 * @param int $post_id Post ID.
 * @return void
 */
function skyyrose_save_preorder_meta( $post_id ) {

	if ( ! isset( $_POST['skyyrose_preorder_nonce'] ) ) {
		return;
	}

	if ( ! wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST['skyyrose_preorder_nonce'] ) ), 'skyyrose_preorder_nonce' ) ) {
		return;
	}

	if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) {
		return;
	}

	if ( ! current_user_can( 'edit_post', $post_id ) ) {
		return;
	}

	// Pre-order checkbox.
	$is_preorder = isset( $_POST['skyyrose_is_preorder'] ) ? '1' : '0';
	update_post_meta( $post_id, '_is_preorder', $is_preorder );

	// Edition size.
	if ( isset( $_POST['skyyrose_edition_size'] ) ) {
		$edition = absint( wp_unslash( $_POST['skyyrose_edition_size'] ) );
		update_post_meta( $post_id, '_preorder_edition_size', $edition );
	}

	// Available remaining.
	if ( isset( $_POST['skyyrose_preorder_available'] ) ) {
		$available = absint( wp_unslash( $_POST['skyyrose_preorder_available'] ) );
		update_post_meta( $post_id, '_preorder_available', $available );
	}

	// Expected ship date — validate YYYY-MM-DD format.
	if ( isset( $_POST['skyyrose_ship_date'] ) ) {
		$date = sanitize_text_field( wp_unslash( $_POST['skyyrose_ship_date'] ) );
		if ( ! preg_match( '/^\d{4}-\d{2}-\d{2}$/', $date ) || false === strtotime( $date ) ) {
			$date = '';
		}
		update_post_meta( $post_id, '_preorder_ship_date', $date );
	}
}
add_action( 'save_post_product', 'skyyrose_save_preorder_meta' );

/**
 * Resolve a product or variation's effective pre-order configuration.
 *
 * Variation meta overrides parent meta only when the variation explicitly
 * owns that meta key. This lets a variation inherit the parent commercial
 * promise while still supporting variation-specific allocation or dates.
 * The deprecated `_preorder_price` field is intentionally excluded: native
 * WooCommerce product pricing is the sole transaction-price authority.
 *
 * @since 6.4.0
 *
 * @param WC_Product|int $product_or_id Product object or product ID.
 * @param int            $variation_id  Optional variation ID.
 * @return array{
 *     is_preorder: bool,
 *     product_id: int,
 *     variation_id: int,
 *     configuration_source_id: int,
 *     allocation_source_id: int,
 *     edition_size: int|null,
 *     available: int|null,
 *     expected_ship_date: string
 * }
 */
function skyyrose_get_effective_preorder_config( $product_or_id, $variation_id = 0 ) {
	$requested_product = null;

	if ( $variation_id ) {
		$requested_product = wc_get_product( absint( $variation_id ) );
	} elseif ( $product_or_id instanceof WC_Product ) {
		$requested_product = $product_or_id;
	} else {
		$requested_product = wc_get_product( absint( $product_or_id ) );
	}

	$empty_config = array(
		'is_preorder'             => false,
		'product_id'              => 0,
		'variation_id'            => 0,
		'configuration_source_id' => 0,
		'allocation_source_id'    => 0,
		'edition_size'            => null,
		'available'               => null,
		'expected_ship_date'      => '',
	);

	if ( ! $requested_product instanceof WC_Product ) {
		return $empty_config;
	}

	$is_variation = $requested_product->is_type( 'variation' );
	$parent_id    = $is_variation ? absint( $requested_product->get_parent_id() ) : 0;
	$parent       = $parent_id ? wc_get_product( $parent_id ) : null;
	$candidates   = array( $requested_product );

	if ( $parent instanceof WC_Product ) {
		$candidates[] = $parent;
	}

	$resolved = array();
	$sources  = array();
	$keys     = array( '_is_preorder', '_preorder_edition_size', '_preorder_available', '_preorder_ship_date' );

	foreach ( $keys as $key ) {
		foreach ( $candidates as $candidate ) {
			if ( ! $candidate->meta_exists( $key ) ) {
				continue;
			}

			$resolved[ $key ] = $candidate->get_meta( $key, true );
			$sources[ $key ]  = absint( $candidate->get_id() );
			break;
		}
	}

	$product_id              = $is_variation ? $parent_id : absint( $requested_product->get_id() );
	$configuration_source_id = $sources['_is_preorder'] ?? $product_id;
	$allocation_source_id    = $sources['_preorder_available'] ?? $configuration_source_id;
	$edition_size_raw        = $resolved['_preorder_edition_size'] ?? '';
	$available_raw           = $resolved['_preorder_available'] ?? '';
	$ship_date               = (string) ( $resolved['_preorder_ship_date'] ?? '' );

	if ( '' !== $ship_date && ( ! preg_match( '/^\d{4}-\d{2}-\d{2}$/', $ship_date ) || false === strtotime( $ship_date ) ) ) {
		$ship_date = '';
	}

	return array(
		'is_preorder'             => '1' === (string) ( $resolved['_is_preorder'] ?? '0' ),
		'product_id'              => $product_id,
		'variation_id'            => $is_variation ? absint( $requested_product->get_id() ) : 0,
		'configuration_source_id' => absint( $configuration_source_id ),
		'allocation_source_id'    => absint( $allocation_source_id ),
		'edition_size'            => '' === $edition_size_raw ? null : absint( $edition_size_raw ),
		'available'               => '' === $available_raw ? null : absint( $available_raw ),
		'expected_ship_date'      => $ship_date,
	);
}

/**
 * Check if a product is a pre-order item.
 *
 * @since 3.10.0
 *
 * @param int $product_id Product ID.
 * @return bool True if the product has pre-order status.
 */
function skyyrose_is_preorder( $product_id ) {
	$config = skyyrose_get_effective_preorder_config( $product_id );
	return $config['is_preorder'];
}

/**
 * Create the versioned commercial-promise snapshot stored with a cart item.
 *
 * @since 6.4.0
 *
 * @param array $config Effective pre-order configuration.
 * @return array<string, bool|int|string|null>
 */
function skyyrose_create_preorder_snapshot( $config ) {
	return array(
		'schema'                   => 'skyyrose.preorder-commercial-promise',
		'schema_version'           => 1,
		'is_preorder'              => true,
		'product_id'               => absint( $config['product_id'] ?? 0 ),
		'variation_id'             => absint( $config['variation_id'] ?? 0 ),
		'configuration_source_id'  => absint( $config['configuration_source_id'] ?? 0 ),
		'allocation_source_id'     => absint( $config['allocation_source_id'] ?? 0 ),
		'edition_size'             => isset( $config['edition_size'] ) ? absint( $config['edition_size'] ) : null,
		'available_at_add_to_cart' => isset( $config['available'] ) ? absint( $config['available'] ) : null,
		'expected_ship_date'       => (string) ( $config['expected_ship_date'] ?? '' ),
	);
}

/**
 * Snapshot a pre-order promise when an item is added to the cart.
 *
 * @since 6.4.0
 *
 * @param array $cart_item_data Existing cart item data.
 * @param int   $product_id     Product ID.
 * @param int   $variation_id   Variation ID.
 * @param int   $quantity       Requested quantity.
 * @return array Modified cart item data.
 */
function skyyrose_add_preorder_cart_item_snapshot( $cart_item_data, $product_id, $variation_id, $quantity ) {
	$config = skyyrose_get_effective_preorder_config( $product_id, $variation_id );

	if ( ! $config['is_preorder'] ) {
		return $cart_item_data;
	}

	// Allocation is enforced by WooCommerce's add-to-cart validation hook below.
	// This filter must remain side-effect free because integrations may call
	// WC_Cart::add_to_cart() from AJAX handlers without exception handling.
	$cart_item_data['skyyrose_preorder_snapshot'] = skyyrose_create_preorder_snapshot( $config );
	return $cart_item_data;
}
add_filter( 'woocommerce_add_cart_item_data', 'skyyrose_add_preorder_cart_item_snapshot', 10, 4 );

/**
 * Hydrate pre-deployment cart sessions with a commercial-promise snapshot.
 *
 * Persistent WooCommerce sessions created before snapshot support do not carry
 * the new cart-item field. Capture the effective promise when such a session is
 * restored so checkout display and order-line history remain interpretable.
 * Existing snapshots are never replaced.
 *
 * @since 6.4.1
 *
 * @param array  $cart_item     Restored cart item.
 * @param array  $session_values Stored session values.
 * @param string $cart_item_key Cart item key.
 * @return array Restored cart item.
 */
function skyyrose_hydrate_preorder_cart_item_snapshot( $cart_item, $session_values, $cart_item_key ) {
	if ( isset( $cart_item['skyyrose_preorder_snapshot'] ) ) {
		return $cart_item;
	}

	$config = skyyrose_get_effective_preorder_config(
		absint( $cart_item['product_id'] ?? $session_values['product_id'] ?? 0 ),
		absint( $cart_item['variation_id'] ?? $session_values['variation_id'] ?? 0 )
	);

	if ( $config['is_preorder'] ) {
		$cart_item['skyyrose_preorder_snapshot'] = skyyrose_create_preorder_snapshot( $config );
	}

	return $cart_item;
}
add_filter( 'woocommerce_get_cart_item_from_session', 'skyyrose_hydrate_preorder_cart_item_snapshot', 10, 3 );

/**
 * Add the snapshotted promise to cart and checkout line-item displays.
 *
 * @since 6.4.0
 *
 * @param array $item_data Existing display data.
 * @param array $cart_item Cart item data.
 * @return array Modified display data.
 */
function skyyrose_display_preorder_cart_item_data( $item_data, $cart_item ) {
	$snapshot = $cart_item['skyyrose_preorder_snapshot'] ?? null;

	if ( ! is_array( $snapshot ) || empty( $snapshot['is_preorder'] ) ) {
		return $item_data;
	}

	$item_data[] = array(
		'key'   => esc_html__( 'Pre-Order', 'skyyrose' ),
		'value' => esc_html__( 'Yes', 'skyyrose' ),
	);

	if ( ! empty( $snapshot['expected_ship_date'] ) ) {
		$item_data[] = array(
			'key'   => esc_html__( 'Expected ship date', 'skyyrose' ),
			'value' => esc_html( date_i18n( 'F j, Y', strtotime( $snapshot['expected_ship_date'] ) ) ),
		);
	}

	return $item_data;
}
add_filter( 'woocommerce_get_item_data', 'skyyrose_display_preorder_cart_item_data', 10, 2 );

/**
 * Persist a cart snapshot into the WooCommerce order line item.
 *
 * @since 6.4.0
 *
 * @param WC_Order_Item_Product $item          Order line item.
 * @param string                $cart_item_key Cart item key.
 * @param array                 $values        Cart item values.
 * @param WC_Order              $order         Order object.
 * @return void
 */
function skyyrose_persist_preorder_order_item_snapshot( $item, $cart_item_key, $values, $order ) {
	$snapshot = $values['skyyrose_preorder_snapshot'] ?? null;

	// Defensive fallback for carts created before this feature was deployed or
	// restored through integrations that bypass the standard session filter.
	if ( ! is_array( $snapshot ) ) {
		$config = skyyrose_get_effective_preorder_config(
			absint( $values['product_id'] ?? 0 ),
			absint( $values['variation_id'] ?? 0 )
		);
		$snapshot = $config['is_preorder'] ? skyyrose_create_preorder_snapshot( $config ) : null;
	}

	if ( ! is_array( $snapshot ) || empty( $snapshot['is_preorder'] ) ) {
		return;
	}

	$item->add_meta_data( '_skyyrose_preorder_snapshot', $snapshot, true );
	$item->add_meta_data( '_skyyrose_preorder_schema', (string) $snapshot['schema'], true );
	$item->add_meta_data( '_skyyrose_preorder_schema_version', (string) absint( $snapshot['schema_version'] ), true );
}
add_action( 'woocommerce_checkout_create_order_line_item', 'skyyrose_persist_preorder_order_item_snapshot', 10, 4 );

/**
 * Count pre-orders in the cart which consume one allocation source.
 *
 * @since 6.4.0
 *
 * @param int    $allocation_source_id Allocation-owning product ID.
 * @param string $excluded_cart_key    Optional cart item key to exclude.
 * @return int Quantity already in the cart.
 */
function skyyrose_get_cart_preorder_quantity( $allocation_source_id, $excluded_cart_key = '' ) {
	$quantity = 0;

	foreach ( WC()->cart->get_cart() as $cart_item_key => $cart_item ) {
		if ( $excluded_cart_key === $cart_item_key ) {
			continue;
		}

		$config = skyyrose_get_effective_preorder_config(
			absint( $cart_item['product_id'] ?? 0 ),
			absint( $cart_item['variation_id'] ?? 0 )
		);

		if ( ! $config['is_preorder'] ) {
			continue;
		}

		if ( absint( $config['allocation_source_id'] ) === absint( $allocation_source_id ) ) {
			$quantity += absint( $cart_item['quantity'] ?? 0 );
		}
	}

	return $quantity;
}

/**
 * Validate a requested quantity against current pre-order allocation.
 *
 * This is validation only. Allocation is deliberately not decremented until
 * the store decides whether native WooCommerce stock or `_preorder_available`
 * owns inventory accounting.
 *
 * @since 6.4.0
 *
 * @param bool   $passed            Existing validation result.
 * @param int    $product_id        Product ID.
 * @param int    $quantity          Requested quantity.
 * @param int    $variation_id      Variation ID.
 * @param array  $variation         Variation attributes.
 * @param array  $cart_item_data    Cart item data.
 * @param string $excluded_cart_key Optional cart key excluded from totals.
 * @return bool Validation result.
 */
function skyyrose_validate_preorder_allocation( $passed, $product_id, $quantity, $variation_id = 0, $variation = array(), $cart_item_data = array(), $excluded_cart_key = '' ) {
	if ( ! $passed ) {
		return false;
	}

	$config = skyyrose_get_effective_preorder_config( $product_id, $variation_id );
	if ( ! $config['is_preorder'] || null === $config['available'] ) {
		return true;
	}

	$requested_total = absint( $quantity ) + skyyrose_get_cart_preorder_quantity( $config['allocation_source_id'], $excluded_cart_key );
	if ( $requested_total <= $config['available'] ) {
		return true;
	}

	wc_add_notice(
		sprintf(
			/* translators: %d is the remaining pre-order allocation. */
			esc_html__( 'Only %d pre-order item(s) remain available.', 'skyyrose' ),
			$config['available']
		),
		'error'
	);

	return false;
}
add_filter( 'woocommerce_add_to_cart_validation', 'skyyrose_validate_preorder_allocation', 10, 6 );

/**
 * Validate allocation when a customer updates a cart line quantity.
 *
 * @since 6.4.0
 *
 * @param bool   $passed        Existing validation result.
 * @param string $cart_item_key Cart item key.
 * @param array  $values        Cart item values.
 * @param int    $quantity      Requested replacement quantity.
 * @return bool Validation result.
 */
function skyyrose_validate_preorder_cart_update( $passed, $cart_item_key, $values, $quantity ) {
	return skyyrose_validate_preorder_allocation(
		$passed,
		absint( $values['product_id'] ?? 0 ),
		$quantity,
		absint( $values['variation_id'] ?? 0 ),
		(array) ( $values['variation'] ?? array() ),
		$values,
		$cart_item_key
	);
}
add_filter( 'woocommerce_update_cart_validation', 'skyyrose_validate_preorder_cart_update', 10, 4 );

/**
 * Revalidate all allocation totals before checkout creates an order.
 *
 * @since 6.4.0
 * @return void
 */
function skyyrose_validate_preorder_cart_allocations() {
	$validated_sources = array();

	foreach ( WC()->cart->get_cart() as $cart_item ) {
		$config = skyyrose_get_effective_preorder_config(
			absint( $cart_item['product_id'] ?? 0 ),
			absint( $cart_item['variation_id'] ?? 0 )
		);

		if ( ! $config['is_preorder'] || null === $config['available'] || isset( $validated_sources[ $config['allocation_source_id'] ] ) ) {
			continue;
		}

		$validated_sources[ $config['allocation_source_id'] ] = true;
		$current_quantity                                     = skyyrose_get_cart_preorder_quantity( $config['allocation_source_id'] );

		if ( $current_quantity > $config['available'] ) {
			wc_add_notice(
				sprintf(
					/* translators: %d is the remaining pre-order allocation. */
					esc_html__( 'Only %d pre-order item(s) remain available. Please update your cart.', 'skyyrose' ),
					$config['available']
				),
				'error'
			);
		}
	}
}
add_action( 'woocommerce_check_cart_items', 'skyyrose_validate_preorder_cart_allocations' );

/**
 * Display pre-order badge and edition info on single product pages.
 *
 * @since 3.10.0
 * @return void
 */
function skyyrose_preorder_single_product_notice() {
	global $product;

	if ( ! $product || ! skyyrose_is_preorder( $product->get_id() ) ) {
		return;
	}

	$config       = skyyrose_get_effective_preorder_config( $product );
	$edition_size = $config['edition_size'];
	$available    = $config['available'];
	$ship_date    = $config['expected_ship_date'];

	echo '<div class="skyyrose-preorder-notice">';
	echo '<span class="skyyrose-preorder-notice__badge">' . esc_html__( 'Pre-Order', 'skyyrose' ) . '</span>';

	if ( $edition_size ) {
		echo '<div class="skyyrose-preorder-notice__detail">' . esc_html__( 'Limited Edition', 'skyyrose' ) . ' — <strong>' . esc_html( (string) $edition_size ) . ' ' . esc_html__( 'pieces', 'skyyrose' ) . '</strong>';
		if ( $available ) {
			echo ' · <strong>' . esc_html( (string) $available ) . ' ' . esc_html__( 'remaining', 'skyyrose' ) . '</strong>';
		}
		echo '</div>';
	}

	if ( $ship_date ) {
		echo '<div class="skyyrose-preorder-notice__ship-date">' . esc_html__( 'Expected Ship Date:', 'skyyrose' ) . ' ' . esc_html( date_i18n( 'F j, Y', strtotime( $ship_date ) ) ) . '</div>';
	}

	echo '</div>';
}
add_action( 'woocommerce_single_product_summary', 'skyyrose_preorder_single_product_notice', 6 );

/**
 * Replace "Add to Cart" text with "Pre-Order Now" for pre-order products.
 *
 * @since 3.10.0
 *
 * @param string     $text    Default button text.
 * @param WC_Product $product Product object.
 * @return string Modified button text.
 */
function skyyrose_preorder_button_text( $text, $product ) {
	if ( skyyrose_is_preorder( $product->get_id() ) ) {
		return esc_html__( 'Pre-Order Now', 'skyyrose' );
	}
	return $text;
}
add_filter( 'woocommerce_product_single_add_to_cart_text', 'skyyrose_preorder_button_text', 10, 2 );
add_filter( 'woocommerce_product_add_to_cart_text', 'skyyrose_preorder_button_text', 10, 2 );

/**
 * Replace $0.00 price display with "Pre-Order" label for pre-order products.
 *
 * When a WooCommerce product is marked as pre-order but has a $0 regular price,
 * the default price_html shows "$0.00" which confuses customers. This filter
 * replaces it with a "Pre-Order" label. Native WooCommerce product price
 * remains the only transaction and price-display authority.
 *
 * @since 4.3.0
 *
 * @param string     $price_html Default price HTML from WooCommerce.
 * @param WC_Product $product    Product object.
 * @return string Modified price HTML.
 */
function skyyrose_preorder_price_html( $price_html, $product ) {
	if ( ! skyyrose_is_preorder( $product->get_id() ) ) {
		return $price_html;
	}

	$regular_price = (float) $product->get_price();

	// If the product has a real price (> 0), keep WC's formatted output.
	if ( $regular_price > 0 ) {
		return $price_html;
	}

	return '<span class="woocommerce-Price-amount amount">'
		. esc_html__( 'Pre-Order', 'skyyrose' )
		. '</span>';
}
add_filter( 'woocommerce_get_price_html', 'skyyrose_preorder_price_html', 10, 2 );

/*
--------------------------------------------------------------
 * Referral Credit — award $10 on completed order
 *--------------------------------------------------------------*/

/**
 * Credit the referrer when a completed order uses their referral coupon.
 *
 * Checks each coupon code on the order against the SKYY prefix pattern,
 * looks up the coupon owner, prevents self-referral, increments
 * _skyyrose_referral_count and _skyyrose_referral_earned on the referrer's
 * user meta, and awards the Founding Ambassador badge to the first 100
 * successful referrers. Idempotent: no-ops if already credited.
 *
 * @since 5.0.0
 *
 * @param int $order_id WooCommerce order ID.
 * @return void
 */
function skyyrose_woo_credit_referrer( $order_id ) {

	$order = wc_get_order( absint( $order_id ) );
	if ( ! $order ) {
		return;
	}

	// Idempotency guard — do not double-credit.
	if ( $order->get_meta( '_skyyrose_referral_credited', true ) ) {
		return;
	}

	foreach ( $order->get_coupon_codes() as $coupon_code ) {

		// Only process SKYY-prefixed referral coupons.
		if ( 0 !== stripos( $coupon_code, 'SKYY' ) ) {
			continue;
		}

		$coupon = new WC_Coupon( $coupon_code );
		if ( ! $coupon->get_id() ) {
			continue;
		}

		$owner_email = get_post_meta( $coupon->get_id(), '_skyyrose_referral_owner_email', true );
		if ( ! is_email( $owner_email ) ) {
			continue;
		}

		// Prevent self-referral.
		if ( strtolower( $owner_email ) === strtolower( $order->get_billing_email() ) ) {
			continue;
		}

		$referrer = get_user_by( 'email', $owner_email );
		if ( ! $referrer ) {
			continue;
		}

		// Increment referral stats.
		$count  = (int) get_user_meta( $referrer->ID, '_skyyrose_referral_count', true );
		$earned = (float) get_user_meta( $referrer->ID, '_skyyrose_referral_earned', true );

		update_user_meta( $referrer->ID, '_skyyrose_referral_count', $count + 1 );
		update_user_meta( $referrer->ID, '_skyyrose_referral_earned', round( $earned + 10.0, 2 ) );

		// Founding Ambassador badge — first 100 referrers with a confirmed conversion.
		if ( ! get_user_meta( $referrer->ID, '_skyyrose_founding_ambassador', true ) ) {
			$total_founders = (int) get_option( 'skyyrose_founding_ambassador_count', 0 );
			if ( $total_founders < 100 ) {
				update_user_meta( $referrer->ID, '_skyyrose_founding_ambassador', 1 );
				update_option( 'skyyrose_founding_ambassador_count', $total_founders + 1 );
			}
		}

		// Mark order as credited to prevent duplicate processing.
		$order->update_meta_data( '_skyyrose_referral_credited', '1' );
		$order->update_meta_data( '_skyyrose_referral_code_used', sanitize_text_field( $coupon_code ) );
		$order->save();

		/**
		 * Fires after a referral is successfully credited.
		 *
		 * Integrations can hook here to send notification emails or
		 * add store credit via third-party reward plugins.
		 *
		 * @since 5.0.0
		 *
		 * @param int   $referrer_id WP user ID of the referrer.
		 * @param int   $order_id    WooCommerce order ID that triggered the credit.
		 * @param float $credit      Credit amount in USD (10.00).
		 */
		do_action( 'skyyrose_referral_credited', $referrer->ID, $order_id, 10.0 );

		break; // One referral credit per order maximum.
	}
}
add_action( 'woocommerce_order_status_completed', 'skyyrose_woo_credit_referrer' );
