<?php
/** Worker for real process/connection loss tests on the private fixture only. */
if ( ! defined( 'WP_CLI' ) || ! WP_CLI || ! defined( 'SKYYROSE_RELEASE_SYNTHETIC_FIXTURE' ) || ! SKYYROSE_RELEASE_SYNTHETIC_FIXTURE || DB_NAME !== 'sr_release_fixture' || get_option( 'home' ) !== 'http://127.0.0.1:18362' ) {
	throw new RuntimeException( 'Private release fixture required.' );
}
require_once dirname( __DIR__, 4 ) . '/tools/v2-runtime/variation-migration-core.php';
$file = getenv( 'SR_MIGRATION_CASE_FILE' );
$mode = $args[0] ?? '';
if ( ! $file || ! str_starts_with( $file, dirname( __DIR__, 4 ) . '/.artifacts/release-gates-20261019/runtime-official/process/' ) ) {
	throw new RuntimeException( 'Bounded fixture case path required.' );
}
try {
	if ( 'prepare' === $mode ) {
		$product = new WC_Product_Simple();
		$product->set_name( 'Synthetic process-loss control' );
		$product->set_sku( 'synthetic-process-' . wp_generate_uuid4() );
		$product->set_status( 'publish' );
		$product->set_regular_price( '80' );
		$product->set_virtual( true );
		$product->save();
		$row = array( 'id' => $product->get_id(), 'sku' => $product->get_sku(), 'classification' => 'SIZE REQUIRED', 'canonical_sizes' => array( '2T', '3T', '4T', '5', '6', '7' ), 'registry_sha256' => hash_file( 'sha256', dirname( __DIR__, 4 ) . '/logo-registry.json' ) );
		$migration = new SkyyRose_Size_Migration( $row );
		$dry = $migration->run( array( 'mode' => 'dry-run' ) );
		$order = new WC_Order();
		$order->add_product( $product, 1 );
		$order->save();
		$data = array( 'row' => $row, 'expected_sha256' => $dry['snapshot_sha256'], 'ordinary_order_id' => $order->get_id() );
		file_put_contents( $file, wp_json_encode( $data ) );
		chmod( $file, 0600 );
		echo wp_json_encode( array( 'ok' => true, 'id' => $product->get_id() ) );
		return;
	}
	$data = json_decode( file_get_contents( $file ), true );
	$migration = new SkyyRose_Size_Migration( $data['row'] );
	if ( 'probe' === $mode ) {
		$result = $migration->run( array( 'mode' => 'reconcile' ) );
		$errors = new WP_Error();
		skyyrose2_preorder_validate_order_payment( wc_get_order( $data['ordinary_order_id'] ), $errors );
		echo wp_json_encode( array( 'ok' => true, 'state' => $result['journal']['state'] ?? null, 'snapshot_sha256' => $result['snapshot_sha256'], 'children' => array_keys( $result['snapshot']['runtime_children'] ), 'ordinary_payment_blocked' => $errors->has_errors(), 'writer_token' => $result['journal']['writer_token'] ?? null ) );
		return;
	}
	if ( 'hold' === $mode ) {
		add_action( 'skyyrose_size_migration_checkpoint', static function ( $step ) use ( $file ) {
			if ( 'after-parent' !== $step ) { return; }
			file_put_contents( $file . '.checkpoint', wp_json_encode( array( 'connection_id' => (int) $GLOBALS['wpdb']->get_var( 'SELECT CONNECTION_ID()' ), 'pid' => getmypid() ) ) );
			$deadline = microtime( true ) + 45;
			while ( ! file_exists( $file . '.release' ) ) {
				if ( microtime( true ) >= $deadline ) { throw new RuntimeException( 'Synthetic checkpoint timed out.' ); }
				usleep( 100000 );
			}
		}, 10, 1 );
	}
	if ( 'orphan' === $mode ) {
		add_action( 'save_post_product_variation', static function ( $id, $post ) use ( $data ) {
			if ( (int) $post->post_parent === $data['row']['id'] ) { throw new RuntimeException( 'Synthetic interruption inside first child save.' ); }
		}, 10, 2 );
	}
	$config = array( 'mode' => 'resume' === $mode ? 'resume' : 'apply', 'expected_sha256' => $data['expected_sha256'] );
	if ( 'resume' === $mode ) {
		$config['expected_current_sha256'] = $migration->run( array( 'mode' => 'reconcile' ) )['snapshot_sha256'];
	}
	$result = $migration->run( $config );
	echo wp_json_encode( array( 'ok' => true, 'changed' => $result['changed'], 'state' => $result['journal']['state'] ?? null, 'children' => $result['variation_ids'] ?? array() ) );
} catch ( Throwable $error ) {
	echo wp_json_encode( array( 'ok' => false, 'error' => $error->getMessage() ) );
	exit( 3 );
}
