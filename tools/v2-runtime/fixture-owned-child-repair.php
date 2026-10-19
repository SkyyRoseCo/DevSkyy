<?php
/** Prospective owned-child repair rehearsal. PRIVATE SYNTHETIC FIXTURE ONLY. */
if ( ! defined( 'WP_CLI' ) || ! WP_CLI || ! defined( 'SKYYROSE_RELEASE_SYNTHETIC_FIXTURE' ) || ! SKYYROSE_RELEASE_SYNTHETIC_FIXTURE || DB_NAME !== 'sr_release_fixture' || get_option( 'home' ) !== 'http://127.0.0.1:18362' || get_stylesheet() !== 'skyyrose-flagship-2' || get_class( $GLOBALS['wpdb'] ) !== 'wpdb' || ! has_filter( 'pre_http_request' ) || ! has_filter( 'pre_wp_mail' ) || ! has_filter( 'woocommerce_webhook_should_deliver' ) ) {
	throw new RuntimeException( 'Private isolated native fixture required; production and staging unsupported.' );
}
require_once __DIR__ . '/variation-migration-core.php';
$root = dirname( __DIR__, 2 );
$directory = realpath( $root . '/.artifacts/release-gates-20261019/runtime-official/owned-repair' );
$file = getenv( 'SR_OWNED_REPAIR_CASE' );
if ( ! $directory || ! $file || realpath( dirname( $file ) ) !== $directory || ! preg_match( '/^[a-z0-9-]+\.json$/D', basename( $file ) ) ) { throw new RuntimeException( 'Bounded private case path required.' ); }
$mode = $args[0] ?? '';
add_action( 'woocommerce_after_product_object_save', static function( $product ) {
 $foreign = getenv( 'SR_OWNED_QUEUE_FOREIGN_PARENT' );
 if ( $foreign && $product instanceof WC_Product_Variable ) { wc_deferred_product_sync( (int) $foreign ); }
}, 10, 1 );
// This rehearsal drains native parent synchronization explicitly while fenced.
// Never leave deferred product writes to shutdown after a failure/lost lock.
remove_action( 'shutdown', array( 'WC_Post_Data', 'do_deferred_product_sync' ), 10 );
function sr_owned_flush_parent( $parent_id ) {
 global $wc_deferred_product_sync;
 $queued = wp_parse_id_list( $wc_deferred_product_sync ?? array() ); $wc_deferred_product_sync = array();
 if ( array_diff( $queued, array( $parent_id ) ) ) { throw new RuntimeException( 'Unexpected deferred parent outside the approved repair scope.' ); }
 if ( getenv( 'SR_OWNED_FORCE_SYNC_FAILURE' ) === '1' ) { throw new RuntimeException( 'Synthetic native parent synchronization failure before COMPLETE.' ); }
 if ( in_array( $parent_id, $queued, true ) ) { WC_Post_Data::deferred_product_sync( $parent_id ); }
 $reentrant = wp_parse_id_list( $wc_deferred_product_sync ?? array() ); $wc_deferred_product_sync = array();
 if ( $reentrant ) { throw new RuntimeException( 'Reentrant deferred parent queue refused before further synchronization.' ); }
}
function sr_owned_write_once( $file, $data ) {
	$handle = fopen( $file, 'x' );
	if ( ! $handle ) { throw new RuntimeException( 'Receipt already exists or cannot be persisted.' ); }
	chmod( $file, 0600 );
	$bytes = wp_json_encode( $data );
	try {
		if ( fwrite( $handle, $bytes ) !== strlen( $bytes ) || ! fflush( $handle ) || ! fsync( $handle ) ) { throw new RuntimeException( 'Durable receipt write failed.' ); }
	} finally { fclose( $handle ); }
	if ( file_get_contents( $file ) !== $bytes ) { throw new RuntimeException( 'Durable receipt readback failed.' ); }
}
function sr_owned_option( $name ) {
	global $wpdb;
	$raw = $wpdb->get_var( $wpdb->prepare( "SELECT option_value FROM {$wpdb->options} WHERE option_name=%s", $name ) );
	if ( $wpdb->last_error ) { throw new RuntimeException( 'Fresh journal read failed.' ); }
	return array( 'raw' => $raw, 'value' => null === $raw ? null : maybe_unserialize( $raw ) );
}
function sr_owned_raw_child( $id ) {
	global $wpdb;
	$post = $wpdb->get_row( $wpdb->prepare( "SELECT * FROM {$wpdb->posts} WHERE ID=%d", $id ), ARRAY_A );
	if ( $wpdb->last_error ) { throw new RuntimeException( 'Native post read failed.' ); }
	$meta = $wpdb->get_results( $wpdb->prepare( "SELECT meta_id,post_id,meta_key,meta_value FROM {$wpdb->postmeta} WHERE post_id=%d ORDER BY meta_id", $id ), ARRAY_A );
	if ( $wpdb->last_error ) { throw new RuntimeException( 'Native metadata read failed.' ); }
	return array( 'post' => $post, 'meta' => $meta );
}
function sr_owned_native( $ids ) {
 global $wpdb;
 $list = implode( ',', array_map( 'intval', $ids ) );
 $queries = array(
  'posts' => "SELECT * FROM {$wpdb->posts} WHERE ID IN ($list) ORDER BY ID",
  'postmeta' => "SELECT * FROM {$wpdb->postmeta} WHERE post_id IN ($list) ORDER BY meta_id",
  'relationships' => "SELECT * FROM {$wpdb->term_relationships} WHERE object_id IN ($list) ORDER BY object_id,term_taxonomy_id",
  'taxonomies' => "SELECT DISTINCT tt.* FROM {$wpdb->term_taxonomy} tt JOIN {$wpdb->term_relationships} tr ON tr.term_taxonomy_id=tt.term_taxonomy_id WHERE tr.object_id IN ($list) ORDER BY tt.term_taxonomy_id",
  'terms' => "SELECT DISTINCT t.* FROM {$wpdb->terms} t JOIN {$wpdb->term_taxonomy} tt ON tt.term_id=t.term_id JOIN {$wpdb->term_relationships} tr ON tr.term_taxonomy_id=tt.term_taxonomy_id WHERE tr.object_id IN ($list) ORDER BY t.term_id",
  'lookup' => "SELECT * FROM {$wpdb->prefix}wc_product_meta_lookup WHERE product_id IN ($list) ORDER BY product_id"
 );
 $out = array();
 foreach ( $queries as $key => $query ) { $out[$key] = $wpdb->get_results( $query, ARRAY_A ); if ( $wpdb->last_error ) { throw new RuntimeException( 'Raw scoped native surface read failed.' ); } }
 return $out;
}
function sr_owned_lock( $lock ) {
 global $wpdb;
 if ( '1' !== (string) $wpdb->get_var( 'SELECT @@autocommit' ) || '0' !== (string) $wpdb->get_var( 'SELECT @@in_transaction' ) ) { throw new RuntimeException( 'Independent durable autocommit required.' ); }
 foreach ( array( $wpdb->posts, $wpdb->postmeta, $wpdb->options, $wpdb->terms, $wpdb->term_taxonomy, $wpdb->term_relationships, $wpdb->prefix . 'wc_product_meta_lookup' ) as $table ) {
  $status = $wpdb->get_row( $wpdb->prepare( 'SHOW TABLE STATUS WHERE Name=%s', $table ) );
  if ( ! $status || $status->Engine !== 'InnoDB' ) { throw new RuntimeException( 'InnoDB durability required.' ); }
 }
 $retry = new ReflectionProperty( 'wpdb', 'reconnect_retries' ); $old = $retry->getValue( $wpdb ); $retry->setValue( $wpdb, 0 );
 if ( '1' !== (string) $wpdb->get_var( $wpdb->prepare( 'SELECT GET_LOCK(%s,0)', $lock ) ) ) { $retry->setValue( $wpdb, $old ); throw new RuntimeException( 'Another parent/repair executor owns the lock.' ); }
 return array( $retry, $old );
}
function sr_owned_state( $data ) {
	$migration = new SkyyRose_Size_Migration( $data['row'] );
	$current = $migration->run( array( 'mode' => 'reconcile' ) );
	$children = array();
	foreach ( array_keys( $current['snapshot']['runtime_children'] ) as $id ) { $children[ $id ] = sr_owned_raw_child( $id ); }
	return array( 'snapshot' => $current['snapshot'], 'migration' => sr_owned_option( 'skyyrose_v2_phase2_variations_' . $data['row']['id'] ), 'children' => $children, 'native' => sr_owned_native( array_merge( array( $data['row']['id'] ), array_keys( $children ) ) ), 'repair' => sr_owned_option( 'sr_fixture_owned_repair_' . $data['row']['id'] ) );
}
function sr_owned_cas( $name, $old, $next ) {
	global $wpdb;
	$previous = null === $old ? null : maybe_unserialize( $old );
	$next['revision'] = (int) ( $previous['revision'] ?? 0 ) + 1;
	$serialized = maybe_serialize( $next );
	$ok = null === $old ? add_option( $name, $next, '', false ) : 1 === $wpdb->query( $wpdb->prepare( "UPDATE {$wpdb->options} SET option_value=%s WHERE option_name=%s AND option_value=%s", $serialized, $name, $old ) );
	if ( ! $ok ) { throw new RuntimeException( 'Separate repair claim CAS failed.' ); }
	wp_cache_delete( $name, 'options' ); wp_cache_delete( 'notoptions', 'options' );
	if ( sr_owned_option( $name )['raw'] !== $serialized ) { throw new RuntimeException( 'Separate repair claim readback failed.' ); }
	return $serialized;
}
function sr_owned_fence( $lock, $name, $raw, $migration_hash, $parent_id ) {
 global $wpdb;
 if ( '1' !== (string) $wpdb->get_var( $wpdb->prepare( 'SELECT IS_USED_LOCK(%s)=CONNECTION_ID()', $lock ) ) || sr_owned_option( $name )['raw'] !== $raw || hash( 'sha256', sr_owned_option( 'skyyrose_v2_phase2_variations_' . $parent_id )['raw'] ) !== $migration_hash ) { throw new RuntimeException( 'Separate repair fence lost.' ); }
}
function sr_owned_validate_receipt( $data, $receipt, $state ) {
	$j = $state['migration']['value']; $original = $receipt['migration'];
	if ( $receipt['schema'] !== 'sr.fixture.insertion.v1' || $receipt['case_nonce'] !== $data['nonce'] || $receipt['row'] !== $data['row'] || $receipt['update'] !== false || $receipt['lock_owned'] !== true || $receipt['preinsert_children'] !== array() || $receipt['preinsert_snapshot_sha256'] !== $original['before_sha256'] || $receipt['helper_sha256'] !== hash_file( 'sha256', __FILE__ ) || ! $receipt['connection_id'] || ! $receipt['pid'] || $j['state'] !== 'FAILED' || $j['writer_token'] !== $original['writer_token'] || $j['revision'] !== $original['revision'] + 1 || $original['attempt']['kind'] !== 'create-child' || ! in_array( $original['attempt']['size'], $data['row']['canonical_sizes'], true ) || (int) $receipt['child']['post']['post_parent'] !== $data['row']['id'] || $receipt['child']['post']['post_type'] !== 'product_variation' || $receipt['child']['meta'] !== array() || isset( $original['before']['runtime_children'][ $receipt['child_id'] ] ) ) { throw new RuntimeException( 'Prospective insertion ownership proof invalid.' ); }
	$a = $j; $b = $original;
	foreach ( array( 'state', 'revision', 'updated_utc' ) as $key ) { unset( $a[ $key ], $b[ $key ] ); }
 if ( $state['snapshot']['runtime_type'] !== 'variable' || $state['snapshot']['default_attributes'] || ( $state['snapshot']['attributes']['size']['options'] ?? null ) !== $data['row']['canonical_sizes'] ) { throw new RuntimeException( 'Reviewed variable parent size plan changed.' ); }
 foreach ( $original['before'] as $field => $value ) {
  if ( in_array( $field, array( 'runtime_type', 'runtime_children', 'attributes', 'regular_price', 'sale_price', 'price', 'date_modified', 'date_modified_gmt' ), true ) ) { continue; }
  if ( $field === 'stock_status' && $original['before']['manage_stock'] === false && $value === 'instock' && $state['snapshot'][$field] === ( $j['parent_transition_stock_status'] ?? null ) ) { continue; }
  if ( $state['snapshot'][$field] !== $value ) { throw new RuntimeException( 'Protected parent preimage changed: ' . $field ); }
 }
 $old_attributes = $original['before']['attributes']; $new_attributes = $state['snapshot']['attributes']; unset( $old_attributes['size'], $new_attributes['size'] );
 if ( $old_attributes !== $new_attributes ) { throw new RuntimeException( 'Unrelated parent attribute drift.' ); }
	if ( $a !== $b || array_map( 'intval', array_keys( $state['children'] ) ) !== array( $receipt['child_id'] ) || ! hash_equals( $j['before_sha256'], SkyyRose_Size_Migration::digest( $j['before'] ) ) ) { throw new RuntimeException( 'Migration journal or complete child inventory differs.' ); }
}
try {
	if ( $mode === 'prepare' ) {
		$p = new WC_Product_Simple(); $p->set_name( 'Synthetic prospective owned repair' ); $p->set_sku( 'synthetic-owned-' . wp_generate_uuid4() ); $p->set_status( 'publish' ); $p->set_regular_price( '80' ); $p->set_virtual( true ); $p->save();
		$row = array( 'id' => $p->get_id(), 'sku' => $p->get_sku(), 'classification' => 'SIZE REQUIRED', 'canonical_sizes' => array( '2T', '3T', '4T', '5', '6', '7' ), 'registry_sha256' => hash_file( 'sha256', $root . '/logo-registry.json' ) );
		$dry = ( new SkyyRose_Size_Migration( $row ) )->run( array( 'mode' => 'dry-run' ) );
        $foreign_id = null;
        if ( getenv( 'SR_OWNED_CREATE_FOREIGN' ) === '1' ) { $foreign = new WC_Product_Simple(); $foreign->set_name('Synthetic foreign untouched control'); $foreign->set_sku('synthetic-foreign-' . wp_generate_uuid4()); $foreign->set_regular_price('21'); $foreign->save(); $foreign_id = $foreign->get_id(); }
		$order = new WC_Order(); $order->add_product( $p, 1 ); $order->save(); $order = new WC_Order( $order->get_id() );
		$data = array( 'row' => $row, 'nonce' => bin2hex( random_bytes( 24 ) ), 'expected_sha256' => $dry['snapshot_sha256'], 'foreign_id' => $foreign_id, 'order_id' => $order->get_id(), 'order_before' => array( 'total' => $order->get_total(), 'items' => array_map( static fn( $i ) => array( $i->get_id(), $i->get_product_id(), $i->get_variation_id(), $i->get_total() ), array_values( $order->get_items() ) ) ) );
		sr_owned_write_once( $file, $data ); echo wp_json_encode( array( 'ok' => true, 'parent_id' => $row['id'] ) ); return;
	}
	$data = json_decode( file_get_contents( $file ), true, 512, JSON_THROW_ON_ERROR );
	if ( ! str_starts_with( $data['row']['sku'], 'synthetic-owned-' ) ) { throw new RuntimeException( 'Only new prospective synthetic cases are supported.' ); }
	$parent_id = $data['row']['id'];
	$lock = 'sr_size_' . substr( hash( 'sha256', get_current_blog_id() . '|' . $GLOBALS['wpdb']->prefix . '|' . $parent_id ), 0, 48 );
    if ( in_array( $mode, array( 'approved-repair', 'approved-repair-resume', 'core-resume' ), true ) ) {
        $expected_guard = $mode === 'core-resume' ? 'IN_PROGRESS' : 'FAILED';
        $inject = static function( $target ) use ( $parent_id, $data ) {
            $id = $target instanceof WC_Product ? $target->get_id() : (int) $target;
            if ( $id !== $parent_id ) { return; }
            $j = sr_owned_option( 'skyyrose_v2_phase2_variations_' . $parent_id )['value'];
            if ( ( $j['attempt']['kind'] ?? '' ) === 'sync-and-readback' ) { wc_deferred_product_sync( getenv('SR_OWNED_FINAL_QUEUE_TARGET') === 'foreign' ? (int) $data['foreign_id'] : $parent_id ); }
        };
        if ( getenv('SR_OWNED_FINAL_QUEUE_STAGE') === 'save' ) { add_action('woocommerce_after_product_object_save', $inject, 20, 1); }
        if ( getenv('SR_OWNED_FINAL_QUEUE_STAGE') === 'legacy' ) { add_action('woocommerce_variable_product_sync', $inject, 20, 1); }
        $barriers = array();
        $assert = static function( $target ) use ( $parent_id, $lock, $expected_guard, &$barriers ) {
            global $wpdb, $wp_filter, $wc_deferred_product_sync;
            $id = $target instanceof WC_Product ? $target->get_id() : (int) $target;
            if ( $id !== $parent_id ) { return; }
            $tag = current_filter(); $callbacks = $wp_filter[$tag]->callbacks[PHP_INT_MAX] ?? array(); $last = end($callbacks);
            if ( ! $last || $last['function'] !== $barriers[$tag] || '1' !== (string) $wpdb->get_var($wpdb->prepare('SELECT IS_USED_LOCK(%s)=CONNECTION_ID()', $lock)) || sr_owned_option('skyyrose_v2_phase2_variations_'.$parent_id)['value']['state'] !== $expected_guard ) { throw new RuntimeException('Native parent sync boundary is not last/locked/incomplete.'); }
            if ( ! empty($wc_deferred_product_sync) ) { $wc_deferred_product_sync=array(); throw new RuntimeException('Late native parent queue refused before COMPLETE.'); }
        };
        foreach ( array('woocommerce_after_product_object_save','woocommerce_variable_product_sync') as $tag ) { $barriers[$tag]=$assert; add_action($tag,$assert,PHP_INT_MAX,1); }
        foreach ( $barriers as $tag => $callback ) { $callbacks=$GLOBALS['wp_filter'][$tag]->callbacks[PHP_INT_MAX]; $last=end($callbacks); if ($last['function']!==$callback) { throw new RuntimeException('Pinned fixture barrier not last at registration.'); } }
    }
	if ( $mode === 'capture' || $mode === 'unreceipted' ) {
		$pre = sr_owned_state( $data );
		if ( $pre['children'] || $pre['migration']['value'] ) { throw new RuntimeException( 'Clean prospective pre-insert inventory required.' ); }
		add_action( 'save_post_product_variation', static function ( $id, $post, $update ) use ( $data, $file, $mode, $lock, $pre ) {
			global $wpdb;
			if ( (int) $post->post_parent !== $data['row']['id'] ) { return; }
			if ( $update !== false ) { throw new RuntimeException( 'Update-hook impersonation refused.' ); }
			$j = sr_owned_option( 'skyyrose_v2_phase2_variations_' . $data['row']['id'] )['value'];
			$owns = '1' === (string) $wpdb->get_var( $wpdb->prepare( 'SELECT IS_USED_LOCK(%s)=CONNECTION_ID()', $lock ) );
			$ids = $wpdb->get_col( $wpdb->prepare( "SELECT ID FROM {$wpdb->posts} WHERE post_type='product_variation' AND post_parent=%d ORDER BY ID", $data['row']['id'] ) );
			if ( ! $owns || $j['state'] !== 'IN_PROGRESS' || $j['attempt']['kind'] !== 'create-child' || array_map( 'intval', $ids ) !== array( $id ) || $j['before']['runtime_children'] ) { throw new RuntimeException( 'Insertion context not uniquely owned.' ); }
			if ( $mode === 'capture' ) {
				$receipt = array( 'schema' => 'sr.fixture.insertion.v1', 'case_nonce' => $data['nonce'], 'row' => $data['row'], 'update' => $update, 'preinsert_children' => array_keys( $pre['children'] ), 'preinsert_snapshot_sha256' => SkyyRose_Size_Migration::digest( $pre['snapshot'] ), 'helper_sha256' => hash_file( 'sha256', __FILE__ ), 'child_id' => $id, 'child' => sr_owned_raw_child( $id ), 'native_at_insertion' => sr_owned_native( array( $data['row']['id'], $id ) ), 'migration' => $j, 'lock_owned' => $owns, 'connection_id' => (int) $wpdb->get_var( 'SELECT CONNECTION_ID()' ), 'pid' => getmypid() );
				sr_owned_write_once( $file . '.receipt', $receipt );
                if ( getenv( 'SR_OWNED_RECEIPT_READBACK_FAIL' ) === '1' ) { throw new RuntimeException( 'Synthetic receipt acknowledgment/readback failure.' ); }
                sr_owned_write_once( $file . '.receipt.verified', array( 'receipt_sha256' => hash_file( 'sha256', $file . '.receipt' ), 'case_nonce' => $data['nonce'] ) );
			}
			throw new RuntimeException( 'Synthetic interruption after observed insertion, before child metadata.' );
		}, 10, 3 );
		( new SkyyRose_Size_Migration( $data['row'] ) )->run( array( 'mode' => 'apply', 'expected_sha256' => $data['expected_sha256'] ) );
		throw new RuntimeException( 'Expected injected failure did not occur.' );
	}
	if ( $mode === 'inspect' ) {
		$s = sr_owned_state( $data ); $errors = new WP_Error(); $order = wc_get_order( $data['order_id'] ); skyyrose2_preorder_validate_order_payment( $order, $errors );
		$after = array( 'total' => $order->get_total(), 'items' => array_map( static fn( $i ) => array( $i->get_id(), $i->get_product_id(), $i->get_variation_id(), $i->get_total() ), array_values( $order->get_items() ) ) );
		echo wp_json_encode( array( 'ok' => true, 'state' => $s, 'preimage_sha256' => SkyyRose_Size_Migration::digest( $s ), 'snapshot_sha256' => SkyyRose_Size_Migration::digest( $s['snapshot'] ), 'payment_blocked' => $errors->has_errors(), 'order_identity_money_unchanged' => $after === $data['order_before'], 'receipt_sha256' => is_file( $file . '.receipt' ) ? hash_file( 'sha256', $file . '.receipt' ) : null ) ); return;
	}
	if ( $mode === 'core-resume' ) {
        global $wpdb;
        $approval = json_decode( file_get_contents( $file . '.resume-approval' ), true, 512, JSON_THROW_ON_ERROR );
        if ( getenv( 'SR_OWNED_RESUME_HOLD_BEFORE_LOCK' ) === '1' ) {
            sr_owned_write_once( $file . '.resume-hold', array( 'pid' => getmypid() ) ); $deadline = microtime(true) + 30;
            while ( ! file_exists( $file . '.resume-release' ) ) { if ( microtime(true) > $deadline ) { throw new RuntimeException( 'Synthetic resume hold expired.' ); } usleep(50000); }
        }
        list( $retry, $old_retries ) = sr_owned_lock( $lock );
        try {
            $fresh = sr_owned_state( $data );
            if ( ! hash_equals( SkyyRose_Size_Migration::digest( $fresh ), $approval['preimage_sha256'] ) || $fresh['repair']['value']['state'] !== 'REPAIRED_AWAITING_REVIEW' || hash( 'sha256', $fresh['repair']['raw'] ) !== $approval['repair_journal_sha256'] ) { throw new RuntimeException( 'Separately reviewed repaired readback required under lock before core resume.' ); }
            add_action( 'skyyrose_size_migration_checkpoint', static function( $step, $id ) use ( $parent_id, $lock, $fresh ) {
                global $wpdb;
                if ( $id !== $parent_id || $step !== 'after-child' ) { return; }
                if ( '1' !== (string) $wpdb->get_var( $wpdb->prepare( 'SELECT IS_USED_LOCK(%s)=CONNECTION_ID()', $lock ) ) ) { throw new RuntimeException( 'Resume parent lock lost before native sync.' ); }
                $j = sr_owned_option( 'skyyrose_v2_phase2_variations_' . $parent_id )['value'];
                if ( $j['state'] !== 'IN_PROGRESS' ) { throw new RuntimeException( 'Native sync must occur before COMPLETE.' ); }
                sr_owned_flush_parent( $parent_id );
            }, 10, 2 );
            $result = ( new SkyyRose_Size_Migration( $data['row'] ) )->run( array( 'mode' => 'resume', 'expected_sha256' => $data['expected_sha256'], 'expected_current_sha256' => $approval['snapshot_sha256'] ) );
            if ( ! empty( $GLOBALS['wc_deferred_product_sync'] ) ) { throw new RuntimeException( 'Unexpected queue after core completion; no post-COMPLETE synchronization permitted.' ); }
            $settled = ( new SkyyRose_Size_Migration( $data['row'] ) )->run( array( 'mode' => 'reconcile' ) );
            if ( $settled['snapshot_sha256'] !== $result['journal']['after_sha256'] ) { throw new RuntimeException( 'Core completed snapshot drifted during fenced native synchronization.' ); }
            $nested_owned = '1' === (string) $wpdb->get_var( $wpdb->prepare( 'SELECT IS_USED_LOCK(%s)=CONNECTION_ID()', $lock ) );
            if ( ! $nested_owned ) { throw new RuntimeException( 'Outer resume fence lost during nested core operation.' ); }
            $answer = array( 'ok' => true, 'state' => $result['journal']['state'], 'children' => $result['variation_ids'], 'outer_lock_retained_after_core_release' => $nested_owned, 'last_native_sync_barriers_verified' => true );
        } finally { $wpdb->get_var( $wpdb->prepare( 'SELECT RELEASE_LOCK(%s)', $lock ) ); $retry->setValue( $wpdb, $old_retries ); }
        $answer['lock_free_after_balanced_release'] = '1' === (string) $wpdb->get_var( $wpdb->prepare( 'SELECT IS_FREE_LOCK(%s)', $lock ) );
        if ( ! $answer['lock_free_after_balanced_release'] ) { throw new RuntimeException( 'Nested lock releases were unbalanced.' ); }
        echo wp_json_encode( $answer ); return;
    }

	if ( ! in_array( $mode, array( 'approved-repair', 'approved-repair-resume' ), true ) ) { throw new RuntimeException( 'Unknown explicit rehearsal mode.' ); }
	$approval = json_decode( file_get_contents( $file . '.approval' ), true, 512, JSON_THROW_ON_ERROR );
	if ( $approval['scope'] !== 'EXPLICIT_REVIEWED_SYNTHETIC_OWNED_CHILD_ONLY' || ! is_file( $file . '.receipt.verified' ) || ! is_file( $file . '.receipt' ) || ! hash_equals( hash_file( 'sha256', $file . '.receipt' ), $approval['receipt_sha256'] ) ) { throw new RuntimeException( 'Explicit reviewed insertion receipt required.' ); }
 $ack = json_decode( file_get_contents( $file . '.receipt.verified' ), true, 512, JSON_THROW_ON_ERROR );
 if ( $ack['receipt_sha256'] !== $approval['receipt_sha256'] || $ack['case_nonce'] !== $data['nonce'] ) { throw new RuntimeException( 'Prospective receipt acknowledgment mismatch.' ); }
	$receipt = json_decode( file_get_contents( $file . '.receipt' ), true, 512, JSON_THROW_ON_ERROR );
	global $wpdb;
	list( $retry, $old_retries ) = sr_owned_lock( $lock );
	try {
		$s = sr_owned_state( $data );
		if ( ! hash_equals( SkyyRose_Size_Migration::digest( $s ), $approval['preimage_sha256'] ) ) { throw new RuntimeException( 'Reviewed current raw preimage changed.' ); }
		sr_owned_validate_receipt( $data, $receipt, $s );
		$repair_name = 'sr_fixture_owned_repair_' . $parent_id; $prior = $s['repair']['value'];
		if ( ( ! $prior && $mode !== 'approved-repair' ) || ( $prior && ( $mode !== 'approved-repair-resume' || $prior['state'] !== 'IN_PROGRESS' || $prior['receipt_sha256'] !== $approval['receipt_sha256'] || $prior['migration_sha256'] !== hash( 'sha256', $s['migration']['raw'] ) ) ) ) { throw new RuntimeException( 'Separate incomplete repair requires fresh explicit review.' ); }
		$child_raw = $s['children'][ $receipt['child_id'] ];
		$known_raw = $prior['after_child'] ?? $receipt['child'];
		if ( $child_raw !== $known_raw || $s['native'] !== ( $prior['after_native'] ?? $receipt['native_at_insertion'] ) ) { throw new RuntimeException( 'Child changed outside recorded insertion/repair afterimage; manual investigation required.' ); }
		$claim = $prior ?: array( 'schema' => 'sr.fixture.repair.v1', 'state' => 'IN_PROGRESS', 'receipt_sha256' => $approval['receipt_sha256'], 'migration_sha256' => hash( 'sha256', $s['migration']['raw'] ), 'reviewed_preimage_sha256' => $approval['preimage_sha256'], 'child_id' => $receipt['child_id'] );
		$claim['token'] = bin2hex( random_bytes( 24 ) ); $claim['revision'] = ( $claim['revision'] ?? 0 ) + 1;
		$claim_raw = sr_owned_cas( $repair_name, $s['repair']['raw'], $claim );
		sr_owned_fence( $lock, $repair_name, $claim_raw, $claim['migration_sha256'], $parent_id );
		if ( ! isset( $claim['after_child'] ) ) {
			$claim['attempt'] = array( 'kind' => 'fill-proven-child', 'child_id' => $receipt['child_id'], 'size' => $receipt['migration']['attempt']['size'], 'before_child_sha256' => SkyyRose_Size_Migration::digest( $child_raw ) );
			$claim_raw = sr_owned_cas( $repair_name, $claim_raw, $claim );

			if ( getenv( 'SR_OWNED_REPAIR_HOLD' ) === '1' ) {
				sr_owned_write_once( $file . '.hold', array( 'connection_id' => (int) $wpdb->get_var( 'SELECT CONNECTION_ID()' ), 'pid' => getmypid() ) );
				$deadline = microtime( true ) + 30;
				while ( ! file_exists( $file . '.release' ) ) { if ( microtime( true ) > $deadline ) { throw new RuntimeException( 'Synthetic repair hold expired.' ); } usleep( 50000 ); }
			}
			sr_owned_fence( $lock, $repair_name, $claim_raw, $claim['migration_sha256'], $parent_id );
			$child = new WC_Product_Variation( $receipt['child_id'] ); $child->set_parent_id( $parent_id ); $child->set_status( 'publish' ); $child->set_attributes( array( 'size' => $receipt['migration']['attempt']['size'] ) ); $child->set_manage_stock( false );
			foreach ( array( 'regular_price', 'sale_price', 'price', 'tax_status', 'tax_class', 'shipping_class_id', 'weight', 'length', 'width', 'height', 'virtual', 'downloadable', 'stock_status', 'backorders', 'date_on_sale_from', 'date_on_sale_to' ) as $field ) { $child->{'set_' . $field}( $receipt['migration']['before'][ $field ] ); }
			$child->update_meta_data( '_skyyrose_size_migration_plan', $receipt['migration']['plan_sha256'] ); $child->save();
			sr_owned_fence( $lock, $repair_name, $claim_raw, $claim['migration_sha256'], $parent_id ); sr_owned_flush_parent( $parent_id ); sr_owned_fence( $lock, $repair_name, $claim_raw, $claim['migration_sha256'], $parent_id ); $claim['after_child'] = sr_owned_raw_child( $receipt['child_id'] ); $claim['after_native'] = sr_owned_native( array( $parent_id, $receipt['child_id'] ) ); $claim_raw = sr_owned_cas( $repair_name, $claim_raw, $claim );
			if ( getenv( 'SR_OWNED_REPAIR_STOP_AFTER_SAVE' ) === '1' ) { throw new RuntimeException( 'Synthetic interruption after durable repaired-child afterimage.' ); }
		}
		if ( sr_owned_option( 'skyyrose_v2_phase2_variations_' . $parent_id )['raw'] !== $s['migration']['raw'] ) { throw new RuntimeException( 'Migration guard changed during repair.' ); }
		sr_owned_fence( $lock, $repair_name, $claim_raw, $claim['migration_sha256'], $parent_id );
		$claim['state'] = 'REPAIRED_AWAITING_REVIEW'; sr_owned_cas( $repair_name, $claim_raw, $claim );
		echo wp_json_encode( array( 'ok' => true, 'migration_state' => 'FAILED', 'repair_state' => $claim['state'], 'child_id' => $receipt['child_id'], 'resume_automatically_called' => false, 'last_native_sync_barriers_verified' => true ) );
	} finally { $wpdb->get_var( $wpdb->prepare( 'SELECT RELEASE_LOCK(%s)', $lock ) ); $retry->setValue( $wpdb, $old_retries ); }
} catch ( Throwable $error ) { echo wp_json_encode( array( 'ok' => false, 'error' => $error->getMessage() ) ); exit( 3 ); }
