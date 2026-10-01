<?php
/** Offline publisher fault tests; authentication and remote execution not applicable. */
define( 'SKYYROSE_PUBLISH_TEST_IMPORT', true );
require __DIR__ . '/publish-search-privacy.php';
$checks = 0;
function check( bool $value ): void {
	global $checks;
	++$checks;
	if ( ! $value ) { throw new RuntimeException( 'TEST_FAILED' ); }
}
function refused( callable $call, string $code ): void {
	try { $call(); } catch ( RuntimeException $error ) { check( $error->getMessage() === $code ); return; }
	throw new RuntimeException( 'EXPECTED_REFUSAL' );
}
function envelope( string $dir, string $opid = 'offline-op-0001' ): array {
	$content = file_get_contents( __DIR__ . '/search-tracking-privacy.php' );
	$journal = json_encode( array( 'operation_id' => $opid, 'target_home' => 'https://skyyrose.co', 'final_path' => $dir . '/' . SKYYROSE_PUBLISH_NAME, 'preimage' => 'ABSENT', 'source_sha256' => SKYYROSE_PUBLISH_SOURCE_SHA, 'status' => 'DISPATCH_PENDING' ) );
	return array( 'mode' => 'APPLY', 'source_base64' => base64_encode( $content ), 'operation_id' => $opid, 'journal_base64' => base64_encode( $journal ), 'journal_sha256' => hash( 'sha256', $journal ) );
}
/** Reproduced short-write stream: fsync is unsupported, so publication must refuse. */
class PublisherShortStream {
    public $context;
    public static string $bytes = '';
    public function stream_open( string $path, string $mode, int $options, ?string &$opened_path ): bool { return true; }
    public function stream_write( string $data ): int { $part = substr( $data, 0, 3 ); self::$bytes .= $part; return strlen( $part ); }
    public function stream_flush(): bool { return true; }
    public function stream_stat(): array { return array(); }
}
stream_wrapper_register( 'publishshort', PublisherShortStream::class );
$short = fopen( 'publishshort://offline', 'wb' );
refused( fn() => skyyrose_publish_write( $short, 'complete-content' ), 'SYNC_REFUSED' );
check( PublisherShortStream::$bytes === 'complete-content' );
fclose( $short );
stream_wrapper_unregister( 'publishshort' );
$dir = realpath( sys_get_temp_dir() ) . '/skyyrose-publisher-test-' . bin2hex( random_bytes( 8 ) );
mkdir( $dir );
define( 'WPMU_PLUGIN_DIR', $dir );
$wp_version = 'drifted';
function get_option( string $key ) { return $key === 'home' ? 'https://skyyrose.co' : 'drifted'; }
class Jetpack { public static function is_module_active( string $module ): bool { return false; } }
try {
	skyyrose_publish_directory( $dir );
	$read_only = fopen( __FILE__, 'rb' );
	refused( fn() => skyyrose_publish_write( $read_only, 'refused' ), 'WRITE_REFUSED' );
	fclose( $read_only );
	$input = envelope( $dir );
	$plan = skyyrose_publish_input( $input, $dir );
	check( skyyrose_publish_reconcile( $plan, $dir ) === 'FINAL_ABSENT_NOW' );
	refused( fn() => skyyrose_publish_run( $input ), 'TARGET_REFUSED' );
	check( ! file_exists( $dir . '/.skyyrose-search-privacy.publish.lock' ) );
	check( $plan['final'] === $dir . '/' . SKYYROSE_PUBLISH_NAME );
	refused( fn() => skyyrose_publish_input( array_replace( $input, array( 'journal_base64' => '' ) ), $dir ), 'JOURNAL_REFUSED' );
	refused( fn() => skyyrose_publish_input( array_replace( $input, array( 'journal_sha256' => str_repeat( '0', 64 ) ) ), $dir ), 'JOURNAL_REFUSED' );
	refused( fn() => skyyrose_publish_input( array_replace( $input, array( 'source_base64' => base64_encode( '<?php foreign;' ) ) ), $dir ), 'SOURCE_REFUSED' );
	refused( fn() => skyyrose_publish_marker( $plan, $dir, false ), 'OWNERSHIP_REFUSED' );
	file_put_contents( $plan['final'], 'foreign' );
	refused( fn() => skyyrose_publish_apply( $plan, $dir ), 'FINAL_REFUSED' );
	check( file_get_contents( $plan['final'] ) === 'foreign' );
	unlink( $plan['final'] );
	skyyrose_publish_apply( $plan, $dir );
	skyyrose_publish_owned_file( $plan, $dir );
	check( hash_file( 'sha256', $plan['final'] ) === SKYYROSE_PUBLISH_SOURCE_SHA );
	skyyrose_publish_marker( $plan, $dir, false );
	check( skyyrose_publish_run( array_replace( $input, array( 'mode' => 'READONLYRECONCILE' ) ) )['runtime_drift'] === true );
	check( skyyrose_publish_reconcile( $plan, $dir ) === 'OWNED_SOURCE_PRESENT' );
	refused( fn() => skyyrose_publish_apply( $plan, $dir ), 'FINAL_REFUSED' );
	check( is_file( skyyrose_publish_anchor( $plan, $dir ) ) );
	refused( fn() => skyyrose_publish_marker( array_replace( $plan, array( 'journal_sha' => str_repeat( '0', 64 ) ) ), $dir, false ), 'OWNERSHIP_REFUSED' );
	file_put_contents( $plan['final'], 'foreign replacement' );
	refused( fn() => skyyrose_publish_rollback( $plan, $dir ), 'FINAL_REFUSED' );
	check( file_get_contents( $plan['final'] ) === 'foreign replacement' );
	unlink( $plan['final'] );
	symlink( __FILE__, $plan['final'] );
	refused( fn() => skyyrose_publish_owned_file( $plan, $dir ), 'FINAL_REFUSED' );
	unlink( $plan['final'] );
	$alias = $dir . '-alias';
	symlink( $dir, $alias );
	refused( fn() => skyyrose_publish_directory( $alias ), 'DIRECTORY_REFUSED' );
	unlink( $alias );
	refused( fn() => skyyrose_publish_apply( $plan, $dir ), 'OWNERSHIP_REFUSED' );
	check( ! file_exists( $plan['final'] ) );
	$base = array( 'home' => 'https://skyyrose.co', 'stylesheet' => 'skyyrose-flagship', 'wordpress' => '7.1.2', 'php' => '8.4.26', 'woocommerce' => '11.1.2', 'jetpack' => '16.3-a.7', 'search' => true, 'stats' => false, 'woocommerce_analytics' => false, 'attribution' => 'no', 'instant_sha' => 'dfb3d25ce5b2a6a5902ea5d484ccaabdeadfcfa49526ffe7ef3cbbb46cf0cfbe', 'helper_sha' => '7dc0ea8761230bff4b5759c36288971ac9beb95c5a3b918c4df0383cb7bd1155' );
	skyyrose_publish_guard( $base );
	foreach ( $base as $key => $value ) {
		refused( fn() => skyyrose_publish_guard( array_replace( $base, array( $key => 'wrong' ) ) ), 'TARGET_REFUSED' );
	}
	skyyrose_publish_guard( array_replace( $base, array( 'stylesheet' => 'skyyrose-flagship-2' ) ) );
	$rollback = skyyrose_publish_input( envelope( $dir, 'offline-rollback-0003' ), $dir );
	skyyrose_publish_apply( $rollback, $dir );
	$rollback_input = envelope( $dir, 'offline-rollback-0003' );
	$result = skyyrose_publish_run( array_replace( $rollback_input, array( 'mode' => 'ROLLBACK' ) ) );
	check( $result['runtime_drift'] === true );
	check( skyyrose_publish_reconcile( $rollback, $dir ) === 'FINAL_ABSENT_NOW' );
	check( ! file_exists( $rollback['final'] ) );
	// Reproduced race: another writer creates final while target PHP syntax is checked.
	if ( function_exists( 'pcntl_fork' ) ) {
		$race = skyyrose_publish_input( envelope( $dir, 'offline-race-0002' ), $dir );
		$pid = pcntl_fork();
		if ( 0 === $pid ) {
			for ( $i = 0; $i < 10000; ++$i ) {
				if ( glob( $dir . '/.skyyrose-search-privacy-offline-race-0002.pending' ) ) {
					file_put_contents( $race['final'], file_get_contents( __DIR__ . '/search-tracking-privacy.php' ) );
					exit( 0 );
				}
				usleep( 100 );
			}
			exit( 2 );
		}
		refused( fn() => skyyrose_publish_apply( $race, $dir ), 'LINK_REFUSED' );
		pcntl_waitpid( $pid, $status );
		check( pcntl_wexitstatus( $status ) === 0 );
		check( hash_file( 'sha256', $race['final'] ) === SKYYROSE_PUBLISH_SOURCE_SHA );
		check( skyyrose_publish_reconcile( $race, $dir ) === 'FOREIGN_OR_CHANGED_FINAL' );
		refused( fn() => skyyrose_publish_rollback( $race, $dir ), 'FINAL_REFUSED' );
		check( is_file( $race['final'] ) );
		check( is_file( skyyrose_publish_anchor( $race, $dir ) ) );
	}
	echo json_encode( array( 'status' => 'PASS', 'checks' => $checks, 'race_test' => function_exists( 'pcntl_fork' ), 'authentication' => 'NOT_APPLICABLE_OFFLINE' ) ) . "\n";
} finally {
	foreach ( scandir( $dir ) as $file ) {
		if ( '.' !== $file && '..' !== $file ) { unlink( $dir . '/' . $file ); }
	}
	rmdir( $dir );
}
