<?php
/** Offline projection concurrency harness. SQLite adapts the MySQL atomic upsert. */
define( 'ABSPATH', __DIR__ );
define( 'SKYYROSE_SEE_DB_VERSION', '1.1.0' );
function add_action( ...$args ) {}
function get_option( $key ) { return $GLOBALS['schema_ready'] ? SKYYROSE_SEE_DB_VERSION : '1.0.0'; }
function sanitize_text_field( $value ) { return $value; }
function current_time( $format ) { return gmdate( $format ); }
class ProjectionDB {
	public $prefix = '';
	public PDO $pdo;
	public function __construct( $path ) {
		$this->pdo = new PDO( 'sqlite:' . $path, null, null, array( PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION ) );
		$this->pdo->exec( 'PRAGMA busy_timeout=10000' );
	}
	public function prepare( $sql, ...$args ) { return array( $sql, $args ); }
	public function query( $query ) {
		list( $sql, $args ) = $query;
		// Only dialect translation; execute real competing atomic database writes.
		$sql = str_replace( 'ON DUPLICATE KEY UPDATE event_id = VALUES(event_id)', 'ON CONFLICT(event_id) DO NOTHING', $sql );
		$sql = preg_replace( '/%[sf]/', '?', $sql );
		$statement = $this->pdo->prepare( $sql );
		$statement->execute( $args );
		return $statement->rowCount();
	}
}
require dirname( __DIR__, 2 ) . '/inc/experience-analyzer.php';
$GLOBALS['schema_ready'] = true;
$worker = '--worker' === ( $argv[1] ?? '' );
$path = $worker ? $argv[2] : tempnam( sys_get_temp_dir(), 'sr-projection-' );
$wpdb = new ProjectionDB( $path );
$events = array();
foreach ( range( 1, 50 ) as $index ) {
	$events[] = array( 'event_id' => sprintf( '00000000-0000-4000-8000-%012d', $index ), 'occurred_at' => gmdate( 'Y-m-d\TH:i:s\Z' ), 'event_type' => 'product_click', 'target' => 'fixture', 'page_type' => 'product', 'collection' => 'fixture' );
}
if ( $worker ) {
	if ( null === skyyrose_see_project_acknowledged_events( $events, 'fixture-site', 'test' ) ) { exit( 1 ); }
	exit( 0 );
}
function check_projection( $condition, $message ) { if ( ! $condition ) { throw new RuntimeException( $message ); } }
$processes = array();
try {
	$wpdb->pdo->exec( "CREATE TABLE skyyrose_analytics (event_id TEXT NULL UNIQUE, event_date TEXT, event_type TEXT, event_target TEXT, page_type TEXT, collection_slug TEXT, event_count INTEGER, event_value REAL, visitor_hash TEXT)" );
	$wpdb->pdo->exec( "INSERT INTO skyyrose_analytics VALUES (NULL, '" . gmdate( 'Y-m-d' ) . "', 'engagement_product_click', 'fixture', 'product', 'fixture', 7, 0, '')" );
	$GLOBALS['schema_ready'] = false;
	check_projection( null === skyyrose_see_project_acknowledged_events( $events, 'fixture-site', 'test' ), 'Incomplete unique-index migration must refuse projection' );
	check_projection( 1 === (int) $wpdb->pdo->query( 'SELECT COUNT(*) FROM skyyrose_analytics' )->fetchColumn(), 'Schema failure must write nothing' );
	$GLOBALS['schema_ready'] = true;
	foreach ( range( 1, 2 ) as $ignored ) {
		$process = proc_open( array( PHP_BINARY, __FILE__, '--worker', $path ), array(), $pipes );
		if ( ! is_resource( $process ) ) { throw new RuntimeException( 'Failed to start projection worker' ); }
		$processes[] = $process;
	}
	foreach ( $processes as $process ) { check_projection( 0 === proc_close( $process ), 'Concurrent worker must finish' ); }
	$processes = array();
	check_projection( 50 === (int) $wpdb->pdo->query( 'SELECT COUNT(*) FROM skyyrose_analytics WHERE event_id IS NOT NULL' )->fetchColumn(), 'Concurrent duplicate projections must store exactly 50 event rows' );
	check_projection( 7 === (int) $wpdb->pdo->query( 'SELECT SUM(event_count) FROM skyyrose_analytics WHERE event_id IS NULL' )->fetchColumn(), 'Historical NULL aggregate must remain unchanged' );
	check_projection( 0 === skyyrose_see_project_acknowledged_events( $events, 'fixture-site', 'test' ), 'Repeat returns no newly stored rows' );
	skyyrose_see_store_events( array( array( 'type' => 'engagement_product_click', 'target' => 'fixture', 'pageType' => 'product', 'collection' => 'fixture', 'ts' => time() * 1000 ) ) );
	check_projection( 50 === (int) $wpdb->pdo->query( 'SELECT SUM(event_count) FROM skyyrose_analytics WHERE event_id IS NOT NULL' )->fetchColumn(), 'Legacy aggregate writes must not increment event-ID rows' );
	check_projection( 8 === (int) $wpdb->pdo->query( 'SELECT SUM(event_count) FROM skyyrose_analytics WHERE event_id IS NULL' )->fetchColumn(), 'Legacy counter still updates its own NULL row' );
	echo "PASS: projection readiness, concurrent duplicate insertion, retry and legacy isolation (offline SQLite dialect adapter; not live MySQL).\n";
} finally {
	foreach ( $processes as $process ) { proc_terminate( $process ); proc_close( $process ); }
	unset( $wpdb );
	unlink( $path );
}
