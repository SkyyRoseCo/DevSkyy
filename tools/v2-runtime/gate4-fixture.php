<?php
/** Isolated gate-4 native qualification worker. No production/staging entry. */
$sr_gate4_root = dirname( __DIR__, 2 );
$sr_gate4_dir = $sr_gate4_root . '/.artifacts/release-gates-20261019/gate4-local';
if ( ! defined( 'WP_CLI' ) || ! WP_CLI || ! defined( 'SKYYROSE_RELEASE_SYNTHETIC_FIXTURE' ) || ! SKYYROSE_RELEASE_SYNTHETIC_FIXTURE || DB_NAME !== 'sr_release_fixture' || realpath( ABSPATH ) !== realpath( $sr_gate4_dir . '/wordpress' ) || get_option( 'home' ) !== 'http://127.0.0.1:18362' || $GLOBALS['wpdb']->get_var( 'SELECT @@socket' ) !== '/tmp/sr-gate4-01a0f768.sock' ) {
	throw new RuntimeException( 'Exact disposable gate-4 fixture required.' );
}
require_once __DIR__ . '/variation-migration-core.php';
$sr_gate4_file = getenv( 'SR_GATE4_CASE' );
if ( ! $sr_gate4_file || realpath( dirname( $sr_gate4_file ) ) !== realpath( $sr_gate4_dir ) || ! preg_match( '/^case-[a-z0-9-]+\.json$/D', basename( $sr_gate4_file ) ) ) {
	throw new RuntimeException( 'Bounded synthetic case required.' );
}
$sr_gate4_mode = $args[0] ?? '';
require_once __DIR__ . '/variation-migration-core-next.php';
function sr_gate4_raw( $id ) { return SkyyRose_Fenced_Size_Migration::raw( $id ); }

try {
	if ( $sr_gate4_mode === 'prepare' ) {
		$product = new WC_Product_Simple();
		$product->set_name( 'Synthetic gate4 standalone qualification' );
		$product->set_sku( 'synthetic-gate4-' . wp_generate_uuid4() );
		$product->set_status( 'publish' );
		$product->set_regular_price( '80' );
		$product->set_virtual( true );
		$product->save();
		$row = array( 'id' => $product->get_id(), 'sku' => $product->get_sku(), 'classification' => 'SIZE REQUIRED', 'canonical_sizes' => array( '2T', '3T', '4T', '5', '6', '7' ), 'registry_sha256' => hash_file( 'sha256', $sr_gate4_root . '/logo-registry.json' ) );
		$migration = new SkyyRose_Size_Migration( $row );
		$dry = $migration->run( array( 'mode' => 'dry-run' ) );
		$foreign = new WC_Product_Variable();
		$foreign->set_name( 'Synthetic unrelated native parent' );
		$foreign->save();
		$order = new WC_Order(); $order->add_product( $product, 1 ); $order->calculate_totals(); $order->save();
		file_put_contents( $sr_gate4_file, wp_json_encode( array( 'row' => $row, 'expected_sha256' => $dry['snapshot_sha256'], 'foreign_id' => $foreign->get_id(), 'order_id' => $order->get_id() ) ) );
		chmod( $sr_gate4_file, 0600 );
		echo wp_json_encode( array( 'ok' => true, 'id' => $row['id'] ) );
		return;
	}
	$data = json_decode( file_get_contents( $sr_gate4_file ), true );
	$id = (int) $data['row']['id'];
	if ( $sr_gate4_mode === 'inspect-guard' ) {
		$journal = get_option( 'skyyrose_v2_phase2_variations_' . $id );
		$errors = new WP_Error(); skyyrose2_preorder_validate_order_payment( new WC_Order( $data['order_id'] ), $errors );
		echo wp_json_encode( array( 'ok' => true, 'state' => $journal['state'], 'quarantined' => ! empty( $journal['completion_quarantined'] ), 'native_payment_blocked' => $errors->has_errors(), 'raw_sha256' => SkyyRose_Size_Migration::digest( sr_gate4_raw( $id ) ) ) ); return;
	}
	if ( str_starts_with( $sr_gate4_mode, 'control-' ) ) {
		$name = 'skyyrose_v2_phase2_variations_' . $id;
		$journal = get_option( $name );
		if ( $sr_gate4_mode === 'control-missing-raw' ) { unset( $journal['after_raw_sha256'] ); update_option( $name, $journal, false ); }
		elseif ( $sr_gate4_mode === 'control-old-complete' ) { unset( $journal['completion_protocol'], $journal['after_raw_sha256'] ); update_option( $name, $journal, false ); }
		elseif ( $sr_gate4_mode === 'control-raw-drift' ) { $GLOBALS['wpdb']->update( $GLOBALS['wpdb']->prefix . 'wc_product_meta_lookup', array( 'stock_quantity' => 99 ), array( 'product_id' => $id ) ); }
		elseif ( $sr_gate4_mode === 'control-parent-drift' ) { update_post_meta( $id, '_sku', 'synthetic-gate4-unexplained-drift' ); }
		else { throw new RuntimeException( 'Unknown synthetic control.' ); }
		echo wp_json_encode( array( 'ok' => true ) ); return;
	}
	$migration = new SkyyRose_Size_Migration( $data['row'] );
	if ( getenv( 'SR_GATE4_FENCED' ) === '1' && $sr_gate4_mode !== 'inspect' ) {
		require_once __DIR__ . '/variation-migration-core-next.php';
		$migration = new SkyyRose_Fenced_Size_Migration( $data['row'] );
	}
	if ( $sr_gate4_mode === 'inspect' ) {
		$result = $migration->run( array( 'mode' => 'reconcile' ) );
		$raw = sr_gate4_raw( $id );
		$errors = new WP_Error();
		if ( ! empty( $data['order_id'] ) ) { skyyrose2_preorder_validate_order_payment( new WC_Order( $data['order_id'] ), $errors ); }
		file_put_contents( $sr_gate4_file . '.raw-inspect.json', wp_json_encode( $raw ) );
		echo wp_json_encode( array( 'ok' => true, 'state' => $result['journal']['state'] ?? null, 'digest' => $result['snapshot_sha256'], 'recorded_after' => $result['journal']['after_sha256'] ?? null, 'raw_sha256' => SkyyRose_Size_Migration::digest( $raw ), 'children' => array_keys( $result['snapshot']['runtime_children'] ), 'native_payment_blocked' => $errors->has_errors(), 'foreign_raw_sha256' => SkyyRose_Size_Migration::digest( array_intersect_key( sr_gate4_raw( $data['foreign_id'] ?? $id ), array_flip( array( 'posts', 'meta', 'lookup', 'relationships' ) ) ) ) ) );
		return;
	}
	$lock = 'sr_size_' . substr( hash( 'sha256', get_current_blog_id() . '|' . $GLOBALS['wpdb']->prefix . '|' . $id ), 0, 48 );
	$phase = 'core';
	$invocation = getenv( 'SR_GATE4_INVOCATION' ) ?: 'development';
	if ( ! preg_match( '/^[a-z0-9-]+$/D', $invocation ) ) { throw new RuntimeException( 'Bounded invocation required.' ); }
	$audit = $sr_gate4_file . '.audit-' . $sr_gate4_mode . '-' . $invocation . '.jsonl';
	if ( file_exists( $audit ) ) { throw new RuntimeException( 'Never overwrite a native lifecycle audit.' ); }
	function sr_gate4_audit( $path, $row ) {
		$handle = fopen( $path, 'ab' );
		if ( ! $handle ) { throw new RuntimeException( 'Cannot open native lifecycle audit.' ); }
		try { $bytes = wp_json_encode( $row ) . "\n"; if ( fwrite( $handle, $bytes ) !== strlen( $bytes ) || ! fflush( $handle ) || ! fsync( $handle ) ) { throw new RuntimeException( 'Cannot durably record native lifecycle.' ); } } finally { fclose( $handle ); }
	}
	sr_gate4_audit( $audit, array( 'event' => 'BEGIN', 'mode' => $sr_gate4_mode, 'parent_id' => $id ) );
	register_shutdown_function( static function () use ( $audit ) { sr_gate4_audit( $audit, array( 'event' => 'PROCESS_SHUTDOWN_END', 'native_deferred_callback_registered' => has_action( 'shutdown', array( 'WC_Post_Data', 'do_deferred_product_sync' ) ) !== false ) ); } );
	$raw_failure_injected = false;
	$raw_read_index = 0;
	if ( getenv( 'SR_GATE4_RAW_READ_FAILURE' ) || getenv( 'SR_GATE4_RELEASE_FAILURE' ) ) { $GLOBALS['wpdb']->suppress_errors( true ); }
	add_filter( 'query', static function ( $sql ) use ( $id, $lock, &$phase, $audit, &$raw_failure_injected, &$raw_read_index ) {
		global $wpdb;
		if ( getenv( 'SR_GATE4_SNAPSHOT_FAILURE' ) === '1' && ! $raw_failure_injected && str_starts_with( $sql, 'SELECT ID FROM ' . $wpdb->posts . " WHERE post_type='product_variation'" ) ) { $raw_failure_injected = true; $wpdb->suppress_errors( true ); return 'SELECT ID FROM sr_forced_missing_snapshot_surface'; }
		if ( preg_match( '/^SELECT \* FROM [a-zA-Z0-9_]+ WHERE [a-zA-Z0-9_]+ IN \(/', $sql ) ) { ++$raw_read_index; }
		if ( (int) getenv( 'SR_GATE4_RAW_READ_FAILURE' ) === $raw_read_index && $raw_read_index > 0 && ! $raw_failure_injected ) {
			$raw_failure_injected = true;
			return 'SELECT * FROM sr_forced_missing_raw_surface';
		}
		$release_failure = getenv( 'SR_GATE4_RELEASE_FAILURE' );
		if ( ! $raw_failure_injected && ( ( $release_failure === 'release' && str_starts_with( $sql, 'SELECT RELEASE_LOCK(' ) ) || ( $release_failure === 'ownership' && str_starts_with( $sql, 'SELECT IS_USED_LOCK(' ) && ( get_option( 'skyyrose_v2_phase2_variations_' . $id )['state'] ?? '' ) === 'COMPLETE' ) ) ) {
			$raw_failure_injected = true;
			return 'SELECT * FROM sr_forced_release_read_failure';
		}
		if ( preg_match( '/^\s*(INSERT|UPDATE|DELETE|REPLACE)\b/i', $sql, $match ) ) {
			// Direct native reads avoid recursively invoking this observation filter.
			$owned = mysqli_fetch_row( mysqli_query( $wpdb->dbh, "SELECT IS_USED_LOCK('" . $lock . "')=CONNECTION_ID()" ) )[0];
			$raw = mysqli_fetch_row( mysqli_query( $wpdb->dbh, "SELECT option_value FROM {$wpdb->options} WHERE option_name='skyyrose_v2_phase2_variations_" . $id . "'" ) );
			$journal = $raw ? maybe_unserialize( $raw[0] ) : null;
			preg_match( '/^\s*(?:INSERT\s+(?:IGNORE\s+)?INTO|REPLACE\s+INTO|UPDATE|DELETE\s+FROM)\s+`?([a-zA-Z0-9_]+)/i', $sql, $table );
			sr_gate4_audit( $audit, array( 'event' => 'WRITE_ATTEMPT', 'phase' => $phase, 'verb' => strtoupper( $match[1] ), 'table' => $table[1] ?? 'unknown', 'migration_journal' => str_contains( $sql, 'skyyrose_v2_phase2_variations_' ), 'sql_sha256' => hash( 'sha256', $sql ), 'lock_owned' => $owned === '1', 'state_before_query' => $journal['state'] ?? null, 'observation' => 'PRE_EXECUTION_WRITE_ATTEMPT' ) );
		}
		return $sql;
	} );
	add_action( 'shutdown', static function () use ( &$phase ) { $phase = 'shutdown'; }, 0 );
	$inject = getenv( 'SR_GATE4_QUEUE_STAGE' );
	$target = getenv( 'SR_GATE4_QUEUE_TARGET' ) === 'foreign' ? (int) $data['foreign_id'] : $id;
	if ( $inject === 'initial' ) { wc_deferred_product_sync( $target ); }
	if ( in_array( $inject, array( 'save', 'legacy' ), true ) ) {
		add_action( $inject === 'save' ? 'woocommerce_after_product_object_save' : 'woocommerce_variable_product_sync', static function ( $product ) use ( $id, $target ) {
			$object_id = is_object( $product ) ? $product->get_id() : (int) $product;
			$journal = get_option( 'skyyrose_v2_phase2_variations_' . $id );
			if ( (int) $object_id === $id && ( $journal['attempt']['kind'] ?? '' ) === 'sync-and-readback' ) { wc_deferred_product_sync( $target ); }
		}, 20 );
	}
	if ( $inject === 'reentrant' ) {
		add_action( 'woocommerce_after_product_object_save', static function ( $product ) use ( $id, $target ) { if ( $product->get_id() === $id && $product instanceof WC_Product_Variable && ! empty( get_option( 'skyyrose_v2_phase2_variations_' . $id )['attempt']['size'] ) ) { wc_deferred_product_sync( $target ); } }, 20 );
	}
	if ( getenv( 'SR_GATE4_FAIL_AFTER_CHILD' ) === '1' ) {
		add_action( 'skyyrose_size_migration_checkpoint', static function ( $step ) { if ( $step === 'after-child' ) { throw new RuntimeException( 'Synthetic standalone after-child interruption.' ); } } );
	}
	if ( getenv( 'SR_GATE4_HOLD_AFTER_CHILD' ) === '1' ) {
		add_action( 'skyyrose_size_migration_checkpoint', static function ( $step ) use ( $sr_gate4_file ) {
			if ( $step !== 'after-child' ) { return; }
			file_put_contents( $sr_gate4_file . '.hold', wp_json_encode( array( 'connection_id' => (int) $GLOBALS['wpdb']->get_var( 'SELECT CONNECTION_ID()' ), 'pid' => getmypid() ) ) );
			$deadline = microtime( true ) + 40;
			while ( ! file_exists( $sr_gate4_file . '.release' ) ) {
				if ( microtime( true ) >= $deadline ) { throw new RuntimeException( 'Synthetic held worker timeout.' ); }
				usleep( 100000 );
			}
		}, 20 );
	}
	$config = array( 'mode' => $sr_gate4_mode === 'resume' ? 'resume' : 'apply', 'expected_sha256' => $data['expected_sha256'] );
	if ( $sr_gate4_mode === 'resume' ) { $config['expected_current_sha256'] = $migration->run( array( 'mode' => 'reconcile' ) )['snapshot_sha256']; }
	$result = $migration->run( $config );
	$phase = 'after-core';
	$raw = sr_gate4_raw( $id );
	file_put_contents( $sr_gate4_file . '.raw-return.json', wp_json_encode( $raw ) );
	echo wp_json_encode( array( 'ok' => true, 'state' => $result['journal']['state'], 'digest' => $result['snapshot_sha256'], 'raw_sha256' => SkyyRose_Size_Migration::digest( $raw ), 'queued_parents' => $GLOBALS['wc_deferred_product_sync'] ?? array(), 'lock_owned_after_return' => (string) $GLOBALS['wpdb']->get_var( $GLOBALS['wpdb']->prepare( 'SELECT IS_USED_LOCK(%s)=CONNECTION_ID()', $lock ) ) === '1', 'outer_fence_verified' => $result['fixture_native_fence_verified'] ?? false, 'fenced_raw_sha256' => $result['fenced_raw_sha256'] ?? null ) );
} catch ( Throwable $error ) {
	$phase = 'after-failure';
	if ( isset( $id ) ) { file_put_contents( $sr_gate4_file . '.raw-return.json', wp_json_encode( sr_gate4_raw( $id ) ) ); }
	echo wp_json_encode( array( 'ok' => false, 'error' => $error->getMessage(), 'queued_parents' => $GLOBALS['wc_deferred_product_sync'] ?? array() ) );
	exit( 3 );
}
