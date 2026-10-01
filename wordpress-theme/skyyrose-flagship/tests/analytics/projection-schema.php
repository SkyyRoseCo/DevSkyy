<?php
/** Offline schema-upgrade contract fixture; does not execute a live migration. */
$root = sys_get_temp_dir() . '/sr-schema-' . bin2hex( random_bytes( 8 ) );
mkdir( $root . '/wp-admin/includes', 0700, true );
file_put_contents( $root . '/wp-admin/includes/upgrade.php', '<?php' );
define( 'ABSPATH', $root . '/' );
define( 'ARRAY_A', 'ARRAY_A' );
function add_action( ...$args ) {}
function get_option( $key ) { return $GLOBALS['version'] ?? '1.0.0'; }
function update_option( $key, $value ) { $GLOBALS['version'] = $value; }
function dbDelta( $sql ) { $GLOBALS['ddl'] = $sql; ++$GLOBALS['schema_calls']; }
$wpdb = new class {
	public $prefix = 'fixture_';
	public function get_charset_collate() { return ''; }
	public function prepare( $sql, ...$args ) { return $sql; }
	public function get_results( $sql, $format ) { return $GLOBALS['indexes']; }
	public function get_row( $sql, $format ) { return $GLOBALS['collection']; }
};
require dirname( __DIR__, 2 ) . '/inc/experience-engine.php';
function check_schema( $condition, $message ) { if ( ! $condition ) { throw new RuntimeException( $message ); } }
try {
	$GLOBALS['schema_calls'] = 0;
	$valid = array( 'Non_unique' => 0, 'Column_name' => 'event_id', 'Sub_part' => null );
	$GLOBALS['collection'] = array( 'Type' => 'varchar(100)' );
	foreach ( array( null, array(), array( array_merge( $valid, array( 'Non_unique' => 1 ) ) ), array( array_merge( $valid, array( 'Column_name' => 'event_date' ) ) ), array( $valid, $valid ), array( array_merge( $valid, array( 'Sub_part' => 32 ) ) ) ) as $indexes ) {
		$GLOBALS['indexes'] = $indexes;
		skyyrose_see_create_tables();
		check_schema( ! isset( $GLOBALS['version'] ), 'Missing, composite, prefix or wrong unique index must not advance schema version' );
	}
	$GLOBALS['indexes'] = array( $valid );
	$GLOBALS['collection'] = array( 'Type' => 'varchar(50)' );
	skyyrose_see_create_tables();
	check_schema( ! isset( $GLOBALS['version'] ), 'Failed collection widening must not advance schema version' );
	$GLOBALS['collection'] = array( 'Type' => 'varchar(100)' );
	skyyrose_see_create_tables();
	check_schema( SKYYROSE_SEE_DB_VERSION === $GLOBALS['version'], 'Verified unique index enables projection' );
	check_schema( str_contains( $GLOBALS['ddl'], 'event_id CHAR(64) DEFAULT NULL' ) && str_contains( $GLOBALS['ddl'], 'UNIQUE KEY idx_event_id (event_id)' ), 'Nullable unique key preserves existing aggregate rows' );
	check_schema( str_contains( $GLOBALS['ddl'], 'collection_slug VARCHAR(100)' ), 'Schema accommodates complete accepted collection field' );
	skyyrose_see_create_tables();
	check_schema( 8 === $GLOBALS['schema_calls'], 'Current schema does not rerun upgrade' );
	echo "PASS: 11 schema readiness/nullable uniqueness checks (offline DDL fixture; no live migration).\n";
} finally {
	unlink( $root . '/wp-admin/includes/upgrade.php' );
	rmdir( $root . '/wp-admin/includes' );
	rmdir( $root . '/wp-admin' );
	rmdir( $root );
}
