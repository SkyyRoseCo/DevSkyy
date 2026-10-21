<?php
/** Destructive controls ONLY for the guarded, disposable native synthetic fixture. */
ss_assert_identity( true );
function ss_upgrade_lab() {
	global $wpdb, $wp_filter;
	$names = array( 'skyyrose2_simple_size_history_v1', 'skyyrose2_simple_size_upgrade_v1' );
	$read = static fn( $name ) => $wpdb->get_var( $wpdb->prepare( "SELECT option_value FROM {$wpdb->options} WHERE option_name=%s", $name ) );
	$before = array_map( $read, $names );
	if ( ! is_string( $before[0] ) || ! is_string( $before[1] ) ) { throw new RuntimeException( 'Complete seeded upgrade required.' ); }
	$clear = static function() use ( $names ) { foreach ( $names as $name ) { delete_option( $name ); } };
	$restore = static function() use ( $names, $before, $clear ) { $clear(); foreach ( $names as $i => $name ) { add_option( $name, $before[ $i ], '', false ); } };
	$checks = array();
	$id = (int) get_option( 'ss_legacy_id' );
	$old = ss_order_data( ss_owned_order( $id ) );
	try {
		foreach ( array( 'woocommerce_order_get_items', 'get_order_item_metadata', 'woocommerce_get_order_item_classname', 'woocommerce_stock_amount' ) as $hook ) {
			$clear(); $callback = static fn( $value ) => $value;
			add_filter( $hook, $callback, 999 );
			try { $ok = skyyrose2_simple_size_upgrade(); } finally { remove_filter( $hook, $callback, 999 ); }
			if ( $ok || null !== $read( $names[0] ) || null !== $read( $names[1] ) ) { throw new RuntimeException( 'Unsupported interpretation was admitted.' ); }
			$checks[] = 'REFUSE_UNQUALIFIED_' . $hook;
		}
		$tax_callbacks = array(
			array( array( 'Stripe\\StripeTaxForWooCommerce\\WordPress\\Hooks', 'filter_woocommerce_get_order_item_classname' ), 5, 2 ),
			array( array( 'Stripe\\StripeTaxForWooCommerce\\WooCommerce\\Hook_Handlers\\Order_Tax_Calculation', 'get_order_item_classname' ), 100, 4 ),
		);
		$had_class_hook = array_key_exists( 'woocommerce_get_order_item_classname', $wp_filter );
		$original_class_hook = $wp_filter['woocommerce_get_order_item_classname'] ?? null;
		if ( $had_class_hook ) { $wp_filter['woocommerce_get_order_item_classname'] = clone $original_class_hook; }
		foreach ( $tax_callbacks as $entry ) {
			if ( ! class_exists( $entry[0][0] ) ) { throw new RuntimeException( 'Retained native tax callback unavailable.' ); }
			add_filter( 'woocommerce_get_order_item_classname', $entry[0], $entry[1], $entry[2] );
		}
		try {
			$clear();
			if ( ! skyyrose2_simple_size_upgrade() || $read( $names[0] ) !== $before[0] ) { throw new RuntimeException( 'Source-qualified tax callbacks changed the product baseline.' ); }
			$checks[] = 'EXACT_RETAINED_TAX_CALLBACK_CHAIN_PRESERVES_PRODUCT_BASELINE';
		} finally {
			if ( $had_class_hook ) { $wp_filter['woocommerce_get_order_item_classname'] = $original_class_hook; }
			else { unset( $wp_filter['woocommerce_get_order_item_classname'] ); }
		}
		$clear();
		$fail = static fn( $sql ) => str_starts_with( $sql, "INSERT INTO {$wpdb->options} (option_name,option_value,autoload) VALUES" ) ? 'SELECT 1' : $sql;
		add_filter( 'query', $fail, 999 );
		try { $ok = skyyrose2_simple_size_upgrade(); } finally { remove_filter( 'query', $fail, 999 ); }
		if ( $ok || null !== $read( $names[0] ) || null !== $read( $names[1] ) ) { throw new RuntimeException( 'Failed transaction published partial authority.' ); }
		$checks[] = 'FAILED_ATOMIC_PUBLISH_LEAVES_NO_PARTIAL_STATE';
		if ( ! skyyrose2_simple_size_upgrade() || $read( $names[0] ) !== $before[0] ) { throw new RuntimeException( 'Interrupted migration did not recover exact baseline.' ); }
		$checks[] = 'RETRY_PUBLISHES_ORIGINAL_IMMUTABLE_NATIVE_BASELINE';
		$secondary = new mysqli( 'localhost', 'root', '', DB_NAME, 0, substr( DB_HOST, 10 ) );
		try {
			$clear(); $inserted = false;
			$race = static function( $sql ) use ( $wpdb, $secondary, $names, $before, &$inserted ) {
				if ( ! $inserted && str_starts_with( $sql, "INSERT INTO {$wpdb->options} (option_name,option_value,autoload) VALUES" ) ) {
					$inserted = true;
					$secondary->query( $wpdb->prepare( "INSERT INTO {$wpdb->options} (option_name,option_value,autoload) VALUES (%s,%s,'off'),(%s,%s,'off')", $names[0], $before[0], $names[1], $before[1] ) );
				}
				return $sql;
			};
			add_filter( 'query', $race, 999 );
			try { $ok = skyyrose2_simple_size_upgrade(); } finally { remove_filter( 'query', $race, 999 ); }
			if ( ! $ok || ! $inserted || array_map( $read, $names ) !== $before ) { throw new RuntimeException( 'Concurrent loser did not read exact committed winner.' ); }
			$checks[] = 'TWO_DATABASE_SESSIONS_CONVERGE_ON_ONE_COMPLETE_BASELINE';
			$item_id = (int) $old['items'][0]['id'];
			$qty = $wpdb->get_row( $wpdb->prepare( "SELECT meta_id,meta_value FROM {$wpdb->prefix}woocommerce_order_itemmeta WHERE order_item_id=%d AND meta_key='_qty'", $item_id ), ARRAY_A );
			if ( ! $qty || '1' !== $qty['meta_value'] ) { throw new RuntimeException( 'Exact owned quantity required.' ); }
			$clear(); $changed = false;
			$drift = static function( $sql ) use ( $wpdb, $secondary, $qty, &$changed ) {
				if ( ! $changed && preg_match( '/^SELECT o\.(?:id|ID) AS id,o\./', $sql ) ) {
					$changed = true;
					$secondary->query( $wpdb->prepare( "UPDATE {$wpdb->prefix}woocommerce_order_itemmeta SET meta_value='2' WHERE meta_id=%d", $qty['meta_id'] ) );
				}
				return $sql;
			};
			add_filter( 'query', $drift, 999 );
			try {
				$ok = skyyrose2_simple_size_upgrade();
				$seen = $wpdb->get_var( $wpdb->prepare( "SELECT meta_value FROM {$wpdb->prefix}woocommerce_order_itemmeta WHERE meta_id=%d", $qty['meta_id'] ) );
				if ( ! $ok || ! $changed || '2' !== $seen || $read( $names[0] ) !== $before[0] ) { throw new RuntimeException( 'Concurrent edit replaced the immutable snapshot.' ); }
			} finally { remove_filter( 'query', $drift, 999 ); $wpdb->update( $wpdb->prefix . 'woocommerce_order_itemmeta', array( 'meta_value' => $qty['meta_value'] ), array( 'meta_id' => $qty['meta_id'] ) ); }
			$checks[] = 'CONCURRENT_ORDER_EDIT_CANNOT_BECOME_BASELINE';
		} finally { $secondary->close(); }
		// An existing independent marker forbids rebaselining after missing/corrupt history.
		delete_option( $names[0] ); add_option( $names[0], '{corrupt', '', false );
		if ( ! skyyrose2_simple_size_upgrade() || $read( $names[0] ) !== '{corrupt' ) { throw new RuntimeException( 'Corrupt history was replaced.' ); }
		$checks[] = 'CORRUPT_HISTORY_UNCHANGED_BOUNDARY_RETAINED';
		$restore();
		foreach ( array( array(), null, 42, true, 'not-a-digest' ) as $bad ) {
			$boundary = json_decode( $before[1], true ); $boundary['history_sha256'] = $bad;
			delete_option( $names[1] ); add_option( $names[1], wp_json_encode( $boundary ), '', false );
			if ( skyyrose2_simple_size_upgrade_boundary() || skyyrose2_simple_size_upgrade() ) { throw new RuntimeException( 'Malformed boundary accepted or rebuilt.' ); }
		}
		$checks[] = 'MALFORMED_BOUNDARY_TYPES_REFUSED_WITHOUT_FATAL_OR_REPAIR';
		$restore();
		$hpos = 'hpos' === SR_SIMPLE_SIZE_STORAGE;
		$key_table = $hpos ? $wpdb->prefix . 'wc_order_operational_data' : $wpdb->postmeta;
		$key_where = $hpos ? array( 'order_id' => $id ) : array( 'post_id' => $id, 'meta_key' => '_order_key' );
		$key_column = $hpos ? 'order_key' : 'meta_value';
		$clear(); $wpdb->update( $key_table, array( $key_column => str_repeat( 'k', 23 ) ), $key_where );
		try { if ( skyyrose2_simple_size_upgrade() || null !== $read( $names[0] ) ) { throw new RuntimeException( 'Noncanonical order key was admitted.' ); } }
		finally { $wpdb->update( $key_table, array( $key_column => $old['key'] ), $key_where ); $restore(); }
		$checks[] = 'NONCANONICAL_23_BYTE_KEY_REFUSED_NATIVE_22_BYTE_KEY_PRESERVED';
		// Native checkout-draft is deliberately absent from wc_get_order_statuses().
		$draft = new WC_Order(); $draft->set_status( 'checkout-draft' ); $draft->add_meta_data( '_ss_owner', basename( SR_SIMPLE_SIZE_FIXTURE_ROOT ), true ); $draft->add_meta_data( '_skyyrose_simple_size_generation_v1', array( 'synthetic' => true ), true ); $draft->save();
		$clear();
		if ( skyyrose2_simple_size_upgrade() || null !== $read( $names[0] ) ) { throw new RuntimeException( 'Marked draft was reclassified as history.' ); }
		$draft->delete( true );
		$checks[] = 'MARKED_CHECKOUT_DRAFT_PREVENTS_REBASELINING';
		$restore();
		// Poisoned shared order caches must not affect or be populated by raw snapshot reads.
		$poison = array( 'synthetic-poison' => 'not-native-order-data' );
		wp_cache_set( 'order-items-' . $id, $poison, 'orders' );
		$wpdb->query( 'SET TRANSACTION ISOLATION LEVEL REPEATABLE READ' );
		$wpdb->query( 'START TRANSACTION WITH CONSISTENT SNAPSHOT' );
		try { $map = skyyrose2_simple_size_snapshot( 'hpos' === SR_SIMPLE_SIZE_STORAGE ); } finally { $wpdb->query( 'ROLLBACK' ); }
		if ( ( $map[ $id ] ?? null ) !== json_decode( $before[0], true )['legacy_orders'][ $id ] || wp_cache_get( 'order-items-' . $id, 'orders' ) !== $poison ) { throw new RuntimeException( 'Snapshot touched shared order cache.' ); }
		wp_cache_delete( 'order-items-' . $id, 'orders' );
		$checks[] = 'SNAPSHOT_IGNORES_AND_PRESERVES_POISONED_SHARED_ORDER_CACHE';
		if ( ss_order_data( ss_owned_order( $id ) ) !== $old ) { throw new RuntimeException( 'Upgrade lab changed legacy order.' ); }
		return array( 'status' => 'PASS_NATIVE_UPGRADE_LAB', 'checks' => $checks, 'legacy_order_unchanged' => true );
	} finally { wp_cache_delete( 'order-items-' . $id, 'orders' ); $restore(); }
}
