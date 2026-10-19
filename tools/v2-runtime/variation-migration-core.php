<?php
/**
 * Durable, single-writer size conversion. Loaded only by the guarded CLI entry.
 *
 * Product CRUD is deliberately not wrapped in a transaction that could erase
 * the incomplete-operation guard. An interrupted operation stays unavailable
 * until an explicitly reviewed reconciliation/resume finishes. No order data
 * is queried and no child is automatically deleted.
 */

defined( 'ABSPATH' ) || exit;

final class SkyyRose_Size_Migration {

	private $id;
	private $row;
	private $option;
	private $lock;
	private $raw;
	private $journal;
	private $token;
	private $plan_hash;

	public function __construct( array $row ) {
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

	public function run( array $config ) {
		global $wpdb;
		$mode = $config['mode'] ?? 'dry-run';
		if ( ! in_array( $mode, array( 'dry-run', 'reconcile', 'apply', 'resume', 'rollback-dry-run' ), true ) ) {
			throw new RuntimeException( 'Unsupported mode. Automatic child deletion/rollback is disabled.' );
		}
		$this->read();
		$current = $this->snapshot();
		$result = array( 'mode' => $mode, 'id' => $this->id, 'snapshot' => $current, 'snapshot_sha256' => self::digest( $current ), 'journal' => $this->journal, 'changed' => false, 'order_records_read' => false, 'automatic_rollback_supported' => false );
		if ( in_array( $mode, array( 'dry-run', 'reconcile', 'rollback-dry-run' ), true ) ) {
			return $result;
		}
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
		try {
			$this->read();
			$current = $this->snapshot();
			if ( $this->journal && $this->plan_hash !== ( $this->journal['plan_sha256'] ?? '' ) ) {
				throw new RuntimeException( 'Stored migration plan differs.' );
			}
			if ( $this->journal && 'COMPLETE' === $this->journal['state'] ) {
				if ( self::digest( $current ) !== $this->journal['after_sha256'] ) {
					throw new RuntimeException( 'Completed product or children drifted; inspect without overwriting.' );
				}
				return array_merge( $result, array( 'snapshot' => $current, 'snapshot_sha256' => self::digest( $current ), 'journal' => $this->journal, 'variation_ids' => $this->journal['variation_ids'] ) );
			}
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
			$next['state'] = 'COMPLETE';
			$next['variation_ids'] = array_values( $found );
			$next['after_sha256'] = self::digest( $after );
			unset( $next['attempt'] );
			$this->persist( $next );
			return array_merge( $result, array( 'changed' => true, 'before_snapshot' => $result['snapshot'], 'before_snapshot_sha256' => $result['snapshot_sha256'], 'snapshot' => $after, 'snapshot_sha256' => $next['after_sha256'], 'journal' => $next, 'variation_ids' => array_values( $found ), 'after_sha256' => $next['after_sha256'] ) );
		} catch ( Throwable $error ) {
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
			$wpdb->get_var( $wpdb->prepare( 'SELECT RELEASE_LOCK(%s)', $this->lock ) );
			$retry_property->setValue( $wpdb, $previous_retries );
		}
	}
}
