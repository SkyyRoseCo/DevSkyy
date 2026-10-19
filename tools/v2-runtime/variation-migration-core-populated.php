<?php
/**
 * Prospective private core successor: native deferred writes settle inside its own writer fence.
 * Frozen core c6ab47 remains unchanged; this candidate is not adopted into d953.
 *
 * Product CRUD is deliberately not wrapped in a transaction that could erase
 * the incomplete-operation guard. An interrupted operation stays unavailable
 * until an explicitly reviewed reconciliation/resume finishes. No order data
 * is queried and no child is automatically deleted.
 */

defined( 'ABSPATH' ) || exit;

final class SkyyRose_Fenced_Size_Migration {
	private $sync_barriers = array();
	/** Complete scoped native rows; a failed read never becomes a valid digest. */
	public static function raw( $id ) {
		global $wpdb;
		$children = $wpdb->get_col( $wpdb->prepare( "SELECT ID FROM {$wpdb->posts} WHERE post_parent=%d AND post_type='product_variation' ORDER BY ID", $id ) );
		if ( $wpdb->last_error ) { throw new RuntimeException( 'Raw child inventory read failed.' ); }
		$list = implode( ',', array_merge( array( (int) $id ), array_map( 'intval', $children ) ) );
		$queries = array(
			'posts' => "SELECT * FROM {$wpdb->posts} WHERE ID IN ($list) ORDER BY ID",
			'meta' => "SELECT * FROM {$wpdb->postmeta} WHERE post_id IN ($list) ORDER BY meta_id",
			'lookup' => "SELECT * FROM {$wpdb->prefix}wc_product_meta_lookup WHERE product_id IN ($list) ORDER BY product_id",
			'relationships' => "SELECT * FROM {$wpdb->term_relationships} WHERE object_id IN ($list) ORDER BY object_id,term_taxonomy_id",
			'taxonomies' => "SELECT DISTINCT tt.* FROM {$wpdb->term_taxonomy} tt JOIN {$wpdb->term_relationships} tr ON tr.term_taxonomy_id=tt.term_taxonomy_id WHERE tr.object_id IN ($list) ORDER BY tt.term_taxonomy_id",
			'terms' => "SELECT DISTINCT t.* FROM {$wpdb->terms} t JOIN {$wpdb->term_taxonomy} tt ON tt.term_id=t.term_id JOIN {$wpdb->term_relationships} tr ON tr.term_taxonomy_id=tt.term_taxonomy_id WHERE tr.object_id IN ($list) ORDER BY t.term_id",
		);
		$out = array();
		foreach ( $queries as $name => $query ) {
			$out[ $name ] = $wpdb->get_results( $query, ARRAY_A );
			if ( $wpdb->last_error || ! is_array( $out[ $name ] ) ) { throw new RuntimeException( 'Raw native surface read failed: ' . $name ); }
		}
		return $out;
	}


	private $id;
	private $row;
	private $option;
	private $lock;
	private $raw;
	private $journal;
	private $token;
	private $plan_hash;

	public function __construct( array $row ) {
        $run = getenv( 'SR_POPULATED_RUN' );
        if ( ! is_string( $run ) || ! preg_match( '/^[0-9]{19}$/D', $run ) ) { throw new RuntimeException( 'Exact populated run required.' ); }
        $fixture = dirname( __DIR__, 2 ) . '/.artifacts/release-gates-20261019/gate4-populated/run-' . $run . '/wordpress';
        if ( ! defined('WP_CLI') || ! WP_CLI || ! defined('SKYYROSE_RELEASE_SYNTHETIC_FIXTURE') || ! SKYYROSE_RELEASE_SYNTHETIC_FIXTURE || DB_NAME !== 'sr_release_fixture' || realpath(ABSPATH) !== realpath($fixture) || $GLOBALS['wpdb']->get_var('SELECT @@socket') !== ( '/tmp/sr-g4-pop-' . substr( $run, -12 ) . '.sock' ) || ! str_starts_with($row['sku'] ?? '', 'synthetic-gate4-') ) { throw new RuntimeException('Prospective private core successor only; production/staging unsupported.'); }

		$this->row = $row;
		$this->id = (int) ( $row['id'] ?? 0 );
		$sizes = $row['canonical_sizes'] ?? array();
		if ( ! $this->id || ! is_string( $row['sku'] ?? null ) || '' === $row['sku'] || 'SIZE REQUIRED' !== ( $row['classification'] ?? '' ) || ! is_array( $sizes ) || count( $sizes ) < 2 || count( array_unique( $sizes, SORT_STRING ) ) !== count( $sizes ) || array_filter( $sizes, static fn( $v ) => ! is_string( $v ) || '' === trim( $v ) ) ) {
			throw new RuntimeException( 'An explicit reviewed parent and distinct size plan is required.' );
		}
		$root = dirname( __DIR__, 2 );
		if ( ! is_string( $row['registry_sha256'] ?? null ) || ! hash_equals( hash_file( 'sha256', $root . '/logo-registry.json' ), $row['registry_sha256'] ) ) {
			throw new RuntimeException( 'The current registry digest is required.' );
		}
		$reader_hash = hash_file( 'sha256', $root . '/skyyrose/core/product.py' );
		$synthetic = defined( 'WP_CLI' ) && WP_CLI && defined( 'SKYYROSE_RELEASE_SYNTHETIC_FIXTURE' ) && SKYYROSE_RELEASE_SYNTHETIC_FIXTURE && defined( 'DB_NAME' ) && DB_NAME === 'sr_release_fixture' && get_option( 'home' ) === 'http://127.0.0.1:18362' && str_starts_with( $row['sku'], 'synthetic-' );
		if ( ! $synthetic ) {
			if ( ! is_string( $row['reader_sha256'] ?? null ) || ! hash_equals( $reader_hash, $row['reader_sha256'] ) || ! defined( 'WP_CLI' ) || ! WP_CLI ) {
				throw new RuntimeException( 'A current canonical reader binding and CLI are required.' );
			}
			$python = file_exists( $root . '/.venv-release/bin/python' ) ? $root . '/.venv-release/bin/python' : 'python3';
			$process = proc_open( array( $python, '-m', 'skyyrose.core.product', $row['sku'] ), array( 0 => array( 'pipe', 'r' ), 1 => array( 'pipe', 'w' ), 2 => array( 'pipe', 'w' ) ), $pipes, $root );
			if ( ! is_resource( $process ) ) { throw new RuntimeException( 'Canonical reader could not run.' ); }
			fclose( $pipes[0] );
			$payload = stream_get_contents( $pipes[1] );
			fclose( $pipes[1] );
			stream_get_contents( $pipes[2] );
			fclose( $pipes[2] );
			$exit = proc_close( $process );
			$canonical = json_decode( $payload, true );
			if ( 0 !== $exit || ! is_array( $canonical ) || $row['sku'] !== ( $canonical['sku'] ?? null ) || ! is_string( $canonical['catalog']['sizes'] ?? null ) || explode( '|', $canonical['catalog']['sizes'] ) !== $sizes || ! hash_equals( hash_file( 'sha256', $root . '/logo-registry.json' ), $row['registry_sha256'] ) || ! hash_equals( hash_file( 'sha256', $root . '/skyyrose/core/product.py' ), $reader_hash ) ) {
				throw new RuntimeException( 'Plan differs from the current canonical product reader.' );
			}
		}
		$this->option = 'skyyrose_v2_phase2_variations_' . $this->id;
		$this->lock = 'sr_size_' . substr( hash( 'sha256', get_current_blog_id() . '|' . $GLOBALS['wpdb']->prefix . '|' . $this->id ), 0, 48 );
		$this->plan_hash = hash( 'sha256', wp_json_encode( array( $this->id, $row['sku'], $sizes, $row['registry_sha256'], $reader_hash ) ) );
	}

	/** Fresh durable state; bypass persistent option caches. */
	private function read() {
		global $wpdb;
		$this->raw = $wpdb->get_var( $wpdb->prepare( "SELECT option_value FROM {$wpdb->options} WHERE option_name=%s", $this->option ) );
		if ( $wpdb->last_error ) {
			throw new RuntimeException( 'Cannot verify the durable migration journal.' );
		}
		$this->journal = null === $this->raw ? null : maybe_unserialize( $this->raw );
		if ( null !== $this->journal && ( ! is_array( $this->journal ) || 'skyyrose.size-migration.v1' !== ( $this->journal['schema'] ?? '' ) ) ) {
			throw new RuntimeException( 'Unknown migration journal; manual reconciliation is required.' );
		}
		return $this->journal;
	}

	/** A reconnect loses GET_LOCK; never continue with an unfenced connection. */
	private function fence() {
		global $wpdb;
		$this->read();
		$owns = $wpdb->get_var( $wpdb->prepare( 'SELECT IS_USED_LOCK(%s) = CONNECTION_ID()', $this->lock ) );
		if ( '1' !== (string) $owns || ! hash_equals( $this->token, (string) ( $this->journal['writer_token'] ?? '' ) ) || 'IN_PROGRESS' !== ( $this->journal['state'] ?? '' ) ) {
			throw new RuntimeException( 'Migration writer lost its durable fence.' );
		}
	}

	/** Compare-and-swap every transition; never overwrite another writer. */
	private function persist( array $next ) {
		global $wpdb;
		$next['revision'] = (int) ( $this->journal['revision'] ?? 0 ) + 1;
		$next['updated_utc'] = gmdate( 'Y-m-d\TH:i:s\Z' );
		$serialized = maybe_serialize( $next );
		if ( null === $this->raw ) {
			$ok = add_option( $this->option, $next, '', false );
		} else {
			$ok = 1 === $wpdb->query( $wpdb->prepare( "UPDATE {$wpdb->options} SET option_value=%s WHERE option_name=%s AND option_value=%s", $serialized, $this->option, $this->raw ) );
		}
		if ( ! $ok ) {
			throw new RuntimeException( 'Durable journal transition failed; the purchase guard remains closed.' );
		}
		wp_cache_delete( $this->option, 'options' );
		wp_cache_delete( 'notoptions', 'options' );
		$this->raw = $serialized;
		$this->journal = $next;
	}

	private static function normalize( $value ) {
		if ( $value instanceof DateTimeInterface ) {
			return $value->format( 'c' );
		}
		if ( is_object( $value ) && method_exists( $value, 'get_data' ) ) {
			$value = $value->get_data();
		}
		if ( is_array( $value ) ) {
			$value = array_map( array( self::class, 'normalize' ), $value );
			if ( ! array_is_list( $value ) ) {
				ksort( $value );
			}
		}
		return $value;
	}

	public function snapshot() {
		global $wpdb;
		clean_post_cache( $this->id );
		wp_cache_delete( $this->id, 'post_meta' );
		$product = wc_get_product( $this->id );
		if ( ! $product || $product->get_sku( 'edit' ) !== $this->row['sku'] ) {
			throw new RuntimeException( 'Native parent identity mismatch.' );
		}
		$data = self::normalize( $product->get_data() );
		$data['runtime_type'] = $product->get_type();
		$data['runtime_children'] = array();
		$children = $wpdb->get_col( $wpdb->prepare( "SELECT ID FROM {$wpdb->posts} WHERE post_type='product_variation' AND post_parent=%d ORDER BY ID", $this->id ) );
		if ( $wpdb->last_error ) {
			throw new RuntimeException( 'Cannot verify the complete child inventory.' );
		}
		foreach ( $children as $id ) {
			clean_post_cache( $id );
			wp_cache_delete( $id, 'post_meta' );
			$child = new WC_Product_Variation( $id );
			$data['runtime_children'][ $id ] = self::normalize( $child->get_data() );
		}
		ksort( $data['runtime_children'] );
		return $data;
	}

	public static function digest( $value ) {
		return hash( 'sha256', wp_json_encode( self::normalize( $value ) ) );
	}

	private function before_save( $operation ) {
		$this->fence();
		$next = $this->journal;
		$next['attempt'] = $operation;
		$this->persist( $next );
		$this->fence();
	}

	private function protected_parent( array $current, array $before, $allow_intermediate_stock = false ) {
		foreach ( array_keys( $before ) as $field ) {
			// WooCommerce clears parent price fields when children own pricing.
			// Effective price and complete child schedules are checked at readback.
			if ( in_array( $field, array( 'runtime_type', 'runtime_children', 'attributes', 'regular_price', 'sale_price', 'price', 'date_modified', 'date_modified_gmt' ), true ) ) {
				continue;
			}
			// A native unmanaged variable parent has no available children during
			// conversion. Admit only this recorded transient state, never at final
			// completion; syncing fully verified children must restore the baseline.
			if ( 'stock_status' === $field && $allow_intermediate_stock && false === $before['manage_stock'] && 'instock' === $before['stock_status'] && 'outofstock' === $current['stock_status'] && 'variable' === $current['runtime_type'] ) {
				continue;
			}
			if ( $current[ $field ] !== $before[ $field ] ) {
				throw new RuntimeException( 'Protected parent field changed: ' . $field );
			}
		}
		$original = $before['attributes'];
		$actual = $current['attributes'];
		unset( $original['size'], $actual['size'] );
		if ( $original !== $actual ) {
			throw new RuntimeException( 'An unrelated parent attribute changed.' );
		}
	}

	private function child_matches( $child, $size, array $before ) {
		if ( (int) $child->get_parent_id() !== $this->id || array( 'size' => $size ) !== $child->get_attributes() || $this->plan_hash !== $child->get_meta( '_skyyrose_size_migration_plan', true ) || $child->get_sku( 'edit' ) !== '' || 'publish' !== $child->get_status() || false !== $child->get_manage_stock( 'edit' ) ) {
			return false;
		}
		foreach ( $child->get_meta_data() as $meta ) {
			if ( '_skyyrose_size_migration_plan' !== $meta->get_data()['key'] ) {
				return false;
			}
		}
		foreach ( array( 'regular_price', 'sale_price', 'price', 'tax_status', 'tax_class', 'shipping_class_id', 'weight', 'length', 'width', 'height', 'virtual', 'downloadable', 'stock_status', 'backorders', 'date_on_sale_from', 'date_on_sale_to' ) as $field ) {
			if ( self::normalize( $child->{'get_' . $field}( 'edit' ) ) !== $before[ $field ] ) {
				return false;
			}
		}
		return true;
	}

	private function verify_size_attribute() {
		$parent = new WC_Product_Variable( $this->id );
		$attribute = $parent->get_attributes()['size'] ?? null;
		if ( ! $attribute || 0 !== $attribute->get_id() || 'Size' !== $attribute->get_name() || $attribute->get_options() !== $this->row['canonical_sizes'] || ! $attribute->get_variation() || ! $attribute->get_visible() || $parent->get_default_attributes() ) {
			throw new RuntimeException( 'Parent size attributes conflict with the reviewed plan.' );
		}
	}

    private function install_sync_control() {
        remove_action('shutdown', array('WC_Post_Data','do_deferred_product_sync'),10);
        if (!empty($GLOBALS['wc_deferred_product_sync'])) {
            $GLOBALS['wc_deferred_product_sync']=array();
            throw new RuntimeException('Pre-existing deferred work is outside this one-parent process.');
        }
        foreach (array('woocommerce_after_product_object_save','woocommerce_variable_product_sync') as $tag) {
            $this->sync_barriers[$tag]=array($this,'sync_boundary');
            add_action($tag,$this->sync_barriers[$tag],PHP_INT_MAX,1);
        }
        add_action('skyyrose_size_migration_checkpoint',array($this,'flush_checkpoint'),PHP_INT_MAX,2);
    }

    public function sync_boundary($target) {
        $id=is_object($target) && method_exists($target,'get_id') ? $target->get_id() : (int)$target;
        if ((int)$id !== $this->id) { return; }
        $this->fence();
        $tag=current_filter(); $callbacks=$GLOBALS['wp_filter'][$tag]->callbacks;
        $priority=array_key_last($callbacks); $last=end($callbacks[$priority]);
        if ($priority !== PHP_INT_MAX || $last['function'] !== $this->sync_barriers[$tag]) { throw new RuntimeException('Native sync barrier is no longer last.'); }
        if (!empty($GLOBALS['wc_deferred_product_sync'])) { throw new RuntimeException('Late native sync queue refused before COMPLETE.'); }
    }

    public function flush_checkpoint($step,$id) {
        if ($step !== 'after-child' || (int)$id !== $this->id) { return; }
        $this->fence();
        $queue=wp_parse_id_list($GLOBALS['wc_deferred_product_sync'] ?? array()); $GLOBALS['wc_deferred_product_sync']=array();
        if (array_diff($queue,array($this->id))) { throw new RuntimeException('Foreign deferred parent refused before synchronization.'); }
        if (in_array($this->id,$queue,true)) { WC_Post_Data::deferred_product_sync($this->id); }
        $this->fence();
        if (!empty($GLOBALS['wc_deferred_product_sync'])) { throw new RuntimeException('Reentrant deferred work refused.'); }
    }

	public function run( array $config ) {
		global $wpdb;
		$mode = $config['mode'] ?? 'dry-run';
		if ( ! in_array( $mode, array( 'dry-run', 'reconcile', 'apply', 'resume', 'rollback-dry-run' ), true ) ) {
			throw new RuntimeException( 'Unsupported mode. Automatic child deletion/rollback is disabled.' );
		}
		$result = array( 'mode' => $mode, 'id' => $this->id, 'changed' => false, 'order_records_read' => false, 'automatic_rollback_supported' => false );
        if ( in_array($mode,array('dry-run','reconcile','rollback-dry-run'),true) ) {
            $this->read(); $current=$this->snapshot();
            return array_merge($result,array('snapshot'=>$current,'snapshot_sha256'=>self::digest($current),'journal'=>$this->journal));
        }
		remove_action('shutdown', array('WC_Post_Data','do_deferred_product_sync'),10);
		if (!empty($GLOBALS['wc_deferred_product_sync'])) { $GLOBALS['wc_deferred_product_sync']=array(); throw new RuntimeException('Pre-existing deferred work is outside this one-parent process.'); }
		do_action( 'skyyrose_size_migration_checkpoint', 'before-lock', $this->id );
		if ( '1' !== (string) $wpdb->get_var( 'SELECT @@autocommit' ) || '0' !== (string) $wpdb->get_var( 'SELECT @@in_transaction' ) || $wpdb->last_error ) {
			throw new RuntimeException( 'An independently durable journal requires autocommit and no enclosing transaction.' );
		}
		foreach ( array( $wpdb->posts, $wpdb->postmeta, $wpdb->options, $wpdb->terms, $wpdb->term_taxonomy, $wpdb->term_relationships, $wpdb->prefix . 'wc_product_meta_lookup' ) as $table ) {
			$status = $wpdb->get_row( $wpdb->prepare( 'SHOW TABLE STATUS WHERE Name=%s', $table ) );
			if ( ! $status || 'InnoDB' !== $status->Engine ) {
				throw new RuntimeException( 'Durable InnoDB table required: ' . $table );
			}
		}
		// wpdb can otherwise silently reconnect and replay a failed write after
		// its connection-scoped advisory lock has disappeared. Pin the known
		// native implementation and disable that retry for the entire operation,
		// including CRUD callers holding a reference to this same wpdb object.
		if ( 'wpdb' !== get_class( $wpdb ) ) {
			throw new RuntimeException( 'A custom database drop-in requires separate fencing qualification.' );
		}
		$retry_property = new ReflectionProperty( 'wpdb', 'reconnect_retries' );
		$previous_retries = $retry_property->getValue( $wpdb );
		$retry_property->setValue( $wpdb, 0 );
		if ( '1' !== (string) $wpdb->get_var( $wpdb->prepare( 'SELECT GET_LOCK(%s, 0)', $this->lock ) ) ) {
			$retry_property->setValue( $wpdb, $previous_retries );
			throw new RuntimeException( 'Another size-migration writer is active.' );
		}
		$operation_failed = false;
		try {
			$this->install_sync_control();
			$this->read();
			if ( $this->journal && $this->plan_hash !== ( $this->journal['plan_sha256'] ?? '' ) ) {
				throw new RuntimeException( 'Stored migration plan differs.' );
			}
			if ( $this->journal && 'COMPLETE' === $this->journal['state'] ) {
                if (($this->journal['completion_protocol'] ?? '') !== 'skyyrose.fenced-native-sync.v1') { throw new RuntimeException('Older COMPLETE journal has no successor qualification; inspect without adoption.'); }
                $verified = $this->journal;
                $this->token = bin2hex(random_bytes(24));
                $claim = $verified; $claim['state']='IN_PROGRESS'; $claim['writer_token']=$this->token;
                $claim['completion_quarantined']=true;
                $claim['attempt']=array('kind'=>'revalidate-completion');
                $this->persist($claim);
                $this->fence();
                $current=$this->snapshot();
                $raw_sha256=self::digest(self::raw($this->id));
                if (self::digest($current) !== $verified['after_sha256'] || !is_string($verified['after_raw_sha256'] ?? null) || !hash_equals($verified['after_raw_sha256'],$raw_sha256)) { throw new RuntimeException('Completed raw receipt missing or native state drifted; quarantined for investigation.'); }
                if (!empty($GLOBALS['wc_deferred_product_sync'])) { throw new RuntimeException('Deferred work during completion revalidation.'); }
                $this->fence();
                $complete=$this->journal; $complete['state']='COMPLETE'; unset($complete['attempt'],$complete['completion_quarantined']);
                $this->persist($complete);
                return array_merge($result,array('snapshot'=>$current,'snapshot_sha256'=>self::digest($current),'journal'=>$this->journal,'variation_ids'=>$this->journal['variation_ids'],'fenced_raw_sha256'=>$raw_sha256,'fixture_native_fence_verified'=>true));
            }

			if ( ! empty( $this->journal['completion_quarantined'] ) ) { throw new RuntimeException( 'Quarantined completion requires manual investigation; fresh approval cannot legitimize drift.' ); }
			$current=$this->snapshot();
			$result=array_merge($result,array('snapshot'=>$current,'snapshot_sha256'=>self::digest($current),'journal'=>$this->journal));
			$this->token = bin2hex( random_bytes( 24 ) );
			if ( ! $this->journal ) {
				if ( 'apply' !== $mode || 'simple' !== $current['runtime_type'] || $current['runtime_children'] || ! hash_equals( self::digest( $current ), (string) ( $config['expected_sha256'] ?? '' ) ) || $current['downloadable'] || $current['default_attributes'] ) {
					throw new RuntimeException( 'Reviewed simple preimage required; downloads need a separate conversion contract.' );
				}
				$this->persist( array( 'schema' => 'skyyrose.size-migration.v1', 'state' => 'IN_PROGRESS', 'writer_token' => $this->token, 'parent_id' => $this->id, 'sku' => $this->row['sku'], 'registry_sha256' => $this->row['registry_sha256'], 'reader_sha256' => hash_file( 'sha256', dirname( __DIR__, 2 ) . '/skyyrose/core/product.py' ), 'plan_sha256' => $this->plan_hash, 'canonical_sizes' => $this->row['canonical_sizes'], 'before' => $current, 'before_sha256' => self::digest( $current ), 'cutoff_utc' => gmdate( 'Y-m-d\TH:i:s\Z' ), 'variation_ids' => array() ) );
			} else {
				if ( 'resume' !== $mode || ! in_array( $this->journal['state'], array( 'IN_PROGRESS', 'FAILED' ), true ) || ! hash_equals( self::digest( $current ), (string) ( $config['expected_current_sha256'] ?? '' ) ) ) {
					throw new RuntimeException( 'Incomplete operation requires reviewed fresh reconciliation and explicit resume.' );
				}
				// Owning GET_LOCK proves the previous DB executor no longer owns it;
				// elapsed time alone never permits takeover.
				$next = $this->journal;
				$next['writer_token'] = $this->token;
				$next['state'] = 'IN_PROGRESS';
				$this->persist( $next );
			}
			$before = $this->journal['before'];
			$this->protected_parent( $current, $before, isset( $this->journal['parent_transition_stock_status'] ) && $this->journal['parent_transition_stock_status'] === $current['stock_status'] );
			if ( 'simple' === $current['runtime_type'] ) {
				$this->before_save( array( 'kind' => 'parent-conversion' ) );
				$parent = new WC_Product_Variable( $this->id );
				$attributes = $parent->get_attributes();
				$size = new WC_Product_Attribute();
				$size->set_name( 'Size' );
				$size->set_options( $this->row['canonical_sizes'] );
				$size->set_visible( true );
				$size->set_variation( true );
				$attributes['size'] = $size;
				$parent->set_attributes( $attributes );
				$parent->set_default_attributes( array() );
				$parent->save();
				$transition = $this->snapshot();
				$this->protected_parent( $transition, $before, true );
				$this->fence();
				$next = $this->journal;
				$next['parent_transition_stock_status'] = $transition['stock_status'];
				$next['parent_transition_sha256'] = self::digest( $transition );
				$this->persist( $next );
				do_action( 'skyyrose_size_migration_checkpoint', 'after-parent', $this->id );
			} elseif ( 'variable' !== $current['runtime_type'] ) {
				throw new RuntimeException( 'Unexpected parent type during recovery.' );
			}
			$this->verify_size_attribute();
			$found = array();
			foreach ( array_keys( $this->snapshot()['runtime_children'] ) as $id ) {
				$child = new WC_Product_Variation( $id );
				$size = $child->get_attributes()['size'] ?? null;
				if ( ! in_array( $size, $this->row['canonical_sizes'], true ) || isset( $found[ $size ] ) || ! $this->child_matches( $child, $size, $before ) ) {
					throw new RuntimeException( 'Unexpected, duplicated, unowned or drifted child; manual reconciliation required.' );
				}
				$found[ $size ] = $id;
			}
			foreach ( $this->row['canonical_sizes'] as $size ) {
				if ( isset( $found[ $size ] ) ) {
					continue;
				}
				$this->before_save( array( 'kind' => 'create-child', 'size' => $size, 'known_ids' => array_values( $found ) ) );
				$child = new WC_Product_Variation();
				$child->set_parent_id( $this->id );
				$child->set_status( 'publish' );
				$child->set_attributes( array( 'size' => $size ) );
				$child->set_manage_stock( false );
				foreach ( array( 'regular_price', 'sale_price', 'price', 'tax_status', 'tax_class', 'shipping_class_id', 'weight', 'length', 'width', 'height', 'virtual', 'downloadable', 'stock_status', 'backorders', 'date_on_sale_from', 'date_on_sale_to' ) as $field ) {
					$child->{'set_' . $field}( $before[ $field ] );
				}
				$child->update_meta_data( '_skyyrose_size_migration_plan', $this->plan_hash );
				$child->save();
				$found[ $size ] = $child->get_id();
				do_action( 'skyyrose_size_migration_checkpoint', 'after-child', $this->id );
			}
			$this->before_save( array( 'kind' => 'sync-and-readback' ) );
			WC_Product_Variable::sync( $this->id );
			$after = $this->snapshot();
			$this->protected_parent( $after, $before );
			$this->verify_size_attribute();
			if ( count( $after['runtime_children'] ) !== count( $found ) || $after['price'] !== $before['price'] ) {
				throw new RuntimeException( 'Final native count or effective price mismatch.' );
			}
			foreach ( $this->row['canonical_sizes'] as $size ) {
				$id = $found[ $size ];
				if ( ! $this->child_matches( new WC_Product_Variation( $id ), $size, $before ) ) {
					throw new RuntimeException( 'Final exact child readback failed.' );
				}
			}
			$this->fence();
			$next = $this->journal;
			if (!empty($GLOBALS['wc_deferred_product_sync'])) { throw new RuntimeException('Deferred work remains before COMPLETE.'); }
			$raw_sha256=self::digest(self::raw($this->id));
			$this->fence();
			if ( ! empty( $GLOBALS['wc_deferred_product_sync'] ) ) { throw new RuntimeException( 'Deferred work appeared during final readback.' ); }
			$next['state'] = 'COMPLETE';
			$next['variation_ids'] = array_values( $found );
			$next['after_sha256'] = self::digest( $after );
			$next['after_raw_sha256'] = $raw_sha256;
			$next['completion_protocol'] = 'skyyrose.fenced-native-sync.v1';
			unset( $next['attempt'] );
			$this->persist( $next );
			return array_merge( $result, array( 'changed' => true, 'before_snapshot' => $result['snapshot'], 'before_snapshot_sha256' => $result['snapshot_sha256'], 'snapshot' => $after, 'snapshot_sha256' => $next['after_sha256'], 'journal' => $next, 'variation_ids' => array_values( $found ), 'after_sha256' => $next['after_sha256'], 'fenced_raw_sha256' => $raw_sha256, 'fixture_native_fence_verified' => true ) );
		} catch ( Throwable $error ) {
			$operation_failed = true;
			$GLOBALS['wc_deferred_product_sync'] = array();
			// If the DB is unavailable, the earlier IN_PROGRESS record remains.
			try {
				$this->fence();
				$next = $this->journal;
				$next['state'] = 'FAILED';
				$this->persist( $next );
			} catch ( Throwable $ignored ) {
				// Never clear or synthesize a completed journal after uncertainty.
			}
			throw $error;
		} finally {
			$GLOBALS['wc_deferred_product_sync']=array();
			remove_action('skyyrose_size_migration_checkpoint',array($this,'flush_checkpoint'),PHP_INT_MAX);
			foreach($this->sync_barriers as $tag=>$callback) { remove_action($tag,$callback,PHP_INT_MAX); }
			$release=$wpdb->get_var( $wpdb->prepare( 'SELECT RELEASE_LOCK(%s)', $this->lock ) );
			$release_error = $wpdb->last_error;
			$remaining=$wpdb->get_var($wpdb->prepare('SELECT IS_USED_LOCK(%s)=CONNECTION_ID()',$this->lock));
			$remaining_error = $wpdb->last_error;
			$retry_property->setValue( $wpdb, $previous_retries );
			if ( ! $operation_failed && ( $release_error || $remaining_error || '1' !== (string)$release || '1' === (string)$remaining ) ) { throw new RuntimeException('Native lock release could not be verified; no successful execution receipt.'); }
		}
	}
}
