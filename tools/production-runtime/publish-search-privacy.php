<?php
/** Atomic, journal-bound publisher. Invoke wp eval-file with base64 JSON envelope. */
const SKYYROSE_PUBLISH_SOURCE_SHA = 'afc2f6d8a4ae6280de28b6c1306564cc86053acc713c52e5ab0b5717b3ef58f2';
const SKYYROSE_PUBLISH_NAME = 'skyyrose-search-tracking-privacy.php';

function skyyrose_publish_require( bool $condition, string $code ): void {
	if ( ! $condition ) {
		throw new RuntimeException( $code );
	}
}

function skyyrose_publish_guard( array $facts ): void {
	$expected = array(
		'home' => 'https://skyyrose.co', 'wordpress' => '7.1.2', 'php' => '8.4.26',
		'woocommerce' => '11.1.2', 'jetpack' => '16.3-a.7', 'search' => true,
		'stats' => false, 'woocommerce_analytics' => false, 'attribution' => 'no',
		'instant_sha' => 'dfb3d25ce5b2a6a5902ea5d484ccaabdeadfcfa49526ffe7ef3cbbb46cf0cfbe',
		'helper_sha' => '7dc0ea8761230bff4b5759c36288971ac9beb95c5a3b918c4df0383cb7bd1155',
	);
	foreach ( $expected as $key => $value ) {
		skyyrose_publish_require( isset( $facts[ $key ] ) && $facts[ $key ] === $value, 'TARGET_REFUSED' );
	}
	skyyrose_publish_require( in_array( $facts['stylesheet'] ?? '', array( 'skyyrose-flagship', 'skyyrose-flagship-2' ), true ), 'TARGET_REFUSED' );
}

function skyyrose_publish_facts(): array {
	global $wp_version;
	$base = '/wordpress/plugins/jetpack/16.3-a.7/jetpack_vendor/automattic/jetpack-search/src/';
	return array(
		'home' => get_option( 'home' ), 'stylesheet' => get_option( 'stylesheet' ),
		'wordpress' => $wp_version, 'php' => PHP_VERSION,
		'woocommerce' => defined( 'WC_VERSION' ) ? WC_VERSION : null,
		'jetpack' => defined( 'JETPACK__VERSION' ) ? JETPACK__VERSION : null,
		'search' => class_exists( 'Jetpack' ) && Jetpack::is_module_active( 'search' ),
		'stats' => class_exists( 'Jetpack' ) ? Jetpack::is_module_active( 'stats' ) : null,
		'woocommerce_analytics' => class_exists( 'Jetpack' ) ? Jetpack::is_module_active( 'woocommerce-analytics' ) : null,
		'attribution' => get_option( 'woocommerce_feature_order_attribution_enabled' ),
		'instant_sha' => @hash_file( 'sha256', $base . 'instant-search/class-instant-search.php' ),
		'helper_sha' => @hash_file( 'sha256', $base . 'class-helper.php' ),
	);
}

function skyyrose_publish_directory( string $directory, bool $write = true ): void {
	skyyrose_publish_require( str_starts_with( $directory, '/' ) && realpath( $directory ) === $directory, 'DIRECTORY_REFUSED' );
	$current = '';
	foreach ( explode( '/', trim( $directory, '/' ) ) as $part ) {
		$current .= '/' . $part;
		skyyrose_publish_require( ! is_link( $current ), 'DIRECTORY_REFUSED' );
	}
	skyyrose_publish_require( is_dir( $directory ) && ( ! $write || is_writable( $directory ) ), 'DIRECTORY_REFUSED' );
}

function skyyrose_publish_input( array $input, string $directory ): array {
	$mode = $input['mode'] ?? '';
	skyyrose_publish_require( in_array( $mode, array( 'APPLY', 'READONLYRECONCILE', 'ROLLBACK' ), true ), 'INPUT_REFUSED' );
	$journal_raw = base64_decode( $input['journal_base64'] ?? '', true );
	$journal_sha = $input['journal_sha256'] ?? '';
	skyyrose_publish_require( is_string( $journal_raw ) && preg_match( '/\A[a-f0-9]{64}\z/', $journal_sha ) === 1 && hash_equals( $journal_sha, hash( 'sha256', $journal_raw ) ), 'JOURNAL_REFUSED' );
	$journal = json_decode( $journal_raw, true, 32, JSON_THROW_ON_ERROR );
	$opid = $input['operation_id'] ?? '';
	skyyrose_publish_require( is_string( $opid ) && preg_match( '/\A[a-zA-Z0-9_-]{8,80}\z/', $opid ) === 1, 'JOURNAL_REFUSED' );
	$expected = array(
		'operation_id' => $opid, 'target_home' => 'https://skyyrose.co',
		'final_path' => $directory . '/' . SKYYROSE_PUBLISH_NAME,
		'preimage' => 'ABSENT', 'source_sha256' => SKYYROSE_PUBLISH_SOURCE_SHA,
		'status' => 'DISPATCH_PENDING',
	);
	foreach ( $expected as $key => $value ) {
		skyyrose_publish_require( is_array( $journal ) && ( $journal[ $key ] ?? null ) === $value, 'JOURNAL_REFUSED' );
	}
	$content = base64_decode( $input['source_base64'] ?? '', true );
	skyyrose_publish_require( is_string( $content ) && hash_equals( SKYYROSE_PUBLISH_SOURCE_SHA, hash( 'sha256', $content ) ), 'SOURCE_REFUSED' );
	return array( 'mode' => $mode, 'opid' => $opid, 'content' => $content, 'journal_sha' => $journal_sha, 'final' => $expected['final_path'] );
}

/** Complete stream writes, including partial fwrite results, then fsync. */
function skyyrose_publish_write( $stream, string $content ): void {
	$offset = 0;
	while ( $offset < strlen( $content ) ) {
		$count = @fwrite( $stream, substr( $content, $offset ) );
		skyyrose_publish_require( is_int( $count ) && $count > 0, 'WRITE_REFUSED' );
		$offset += $count;
	}
	skyyrose_publish_require( @fflush( $stream ) && @fsync( $stream ), 'SYNC_REFUSED' );
}

function skyyrose_publish_sync_directory( string $directory ): void {
	$stream = @fopen( $directory, 'r' );
	skyyrose_publish_require( is_resource( $stream ), 'SYNC_REFUSED' );
	try {
		skyyrose_publish_require( @fsync( $stream ), 'SYNC_REFUSED' );
	} finally {
		fclose( $stream );
	}
}

function skyyrose_publish_marker( array $plan, string $directory, bool $create ): string {
	$path = $directory . '/.skyyrose-search-privacy-' . $plan['opid'] . '.receipt';
	$bytes = json_encode( array( 'operation_id' => $plan['opid'], 'journal_sha256' => $plan['journal_sha'], 'final_path' => $plan['final'], 'source_sha256' => SKYYROSE_PUBLISH_SOURCE_SHA ), JSON_THROW_ON_ERROR );
	if ( $create ) {
		$stream = @fopen( $path, 'x+b' );
		skyyrose_publish_require( is_resource( $stream ), 'OWNERSHIP_REFUSED' );
		try {
			skyyrose_publish_write( $stream, $bytes );
		} finally {
			fclose( $stream );
		}
		skyyrose_publish_sync_directory( $directory );
	} else {
		skyyrose_publish_require( ! is_link( $path ) && is_file( $path ) && @file_get_contents( $path ) === $bytes, 'OWNERSHIP_REFUSED' );
	}
	return $path;
}

function skyyrose_publish_anchor( array $plan, string $directory ): string {
    return $directory . '/.skyyrose-search-privacy-' . $plan['opid'] . '.pending';
}

function skyyrose_publish_ownership( array $plan, string $directory ): string {
    $final = $plan['final'];
    clearstatcache();
    if ( ! file_exists( $final ) && ! is_link( $final ) ) { return 'FINAL_ABSENT_NOW'; }
    $anchor = skyyrose_publish_anchor( $plan, $directory );
    if ( is_link( $final ) || ! is_file( $final ) || @hash_file( 'sha256', $final ) !== SKYYROSE_PUBLISH_SOURCE_SHA ) { return 'FOREIGN_OR_CHANGED_FINAL'; }
    if ( is_link( $anchor ) || ! is_file( $anchor ) ) { return 'OWNERSHIP_UNKNOWN'; }
    $left = @stat( $anchor );
    $right = @stat( $final );
    if ( ! is_array( $left ) || ! is_array( $right ) ) { return 'OWNERSHIP_UNKNOWN'; }
    if ( $left['dev'] !== $right['dev'] || $left['ino'] !== $right['ino'] || @hash_file( 'sha256', $anchor ) !== SKYYROSE_PUBLISH_SOURCE_SHA ) { return 'FOREIGN_OR_CHANGED_FINAL'; }
    return 'OWNED_SOURCE_PRESENT';
}

function skyyrose_publish_owned_file( array $plan, string $directory ): void {
    skyyrose_publish_require( skyyrose_publish_ownership( $plan, $directory ) === 'OWNED_SOURCE_PRESENT', 'FINAL_REFUSED' );
}

function skyyrose_publish_reconcile( array $plan, string $directory ): string {
    if ( skyyrose_publish_ownership( $plan, $directory ) === 'FINAL_ABSENT_NOW' ) { return 'FINAL_ABSENT_NOW'; }
    try { skyyrose_publish_marker( $plan, $directory, false ); }
    catch ( RuntimeException $error ) { return 'OWNERSHIP_UNKNOWN'; }
    return skyyrose_publish_ownership( $plan, $directory );
}

function skyyrose_publish_rollback( array $plan, string $directory ): void {
    skyyrose_publish_marker( $plan, $directory, false );
    skyyrose_publish_owned_file( $plan, $directory );
    skyyrose_publish_require( @unlink( $plan['final'] ), 'ROLLBACK_REFUSED' );
    skyyrose_publish_sync_directory( $directory );
}

function skyyrose_publish_apply( array $plan, string $directory ): void {
	skyyrose_publish_require( ! file_exists( $plan['final'] ) && ! is_link( $plan['final'] ), 'FINAL_REFUSED' );
	skyyrose_publish_marker( $plan, $directory, true );
	$temp = skyyrose_publish_anchor( $plan, $directory );
	$retain_anchor = false;
	$stream = @fopen( $temp, 'x+b' );
	skyyrose_publish_require( is_resource( $stream ), 'TEMP_REFUSED' );
	try {
		skyyrose_publish_write( $stream, $plan['content'] );
		fclose( $stream );
		$stream = null;
		skyyrose_publish_require( @hash_file( 'sha256', $temp ) === SKYYROSE_PUBLISH_SOURCE_SHA, 'SOURCE_REFUSED' );
		$output = array();
		$status = 1;
		exec( escapeshellarg( PHP_BINARY ) . ' -n -l ' . escapeshellarg( $temp ) . ' 2>&1', $output, $status );
		skyyrose_publish_require( 0 === $status, 'SYNTAX_REFUSED' );
		$retain_anchor = true;
		skyyrose_publish_sync_directory( $directory );
		skyyrose_publish_require( @link( $temp, $plan['final'] ), 'LINK_REFUSED' );
		skyyrose_publish_sync_directory( $directory );
		skyyrose_publish_owned_file( $plan, $directory );
	} finally {
		if ( is_resource( $stream ) ) {
			fclose( $stream );
		}
		if ( ! $retain_anchor ) { @unlink( $temp ); }
	}
}

function skyyrose_publish_run( array $input ): array {
    $directory = WPMU_PLUGIN_DIR;
    $write = ( $input['mode'] ?? '' ) !== 'READONLYRECONCILE';
    skyyrose_publish_directory( $directory, $write );
    $plan = skyyrose_publish_input( $input, $directory );
    $facts = skyyrose_publish_facts();
    skyyrose_publish_require( $facts['home'] === 'https://skyyrose.co', 'TARGET_REFUSED' );
    $drift = false;
    try { skyyrose_publish_guard( $facts ); } catch ( RuntimeException $error ) { $drift = true; }
    if ( 'READONLYRECONCILE' === $plan['mode'] ) {
        return array( 'status' => skyyrose_publish_reconcile( $plan, $directory ), 'operation_id' => $plan['opid'], 'runtime_drift' => $drift );
    }
    if ( 'APPLY' === $plan['mode'] ) { skyyrose_publish_guard( $facts ); }
    $lock = @fopen( $directory . '/.skyyrose-search-privacy.publish.lock', 'c+b' );
    skyyrose_publish_require( is_resource( $lock ), 'LOCK_REFUSED' );
    try {
        skyyrose_publish_require( flock( $lock, LOCK_EX | LOCK_NB ), 'LOCK_REFUSED' );
        if ( 'APPLY' === $plan['mode'] ) {
            skyyrose_publish_guard( skyyrose_publish_facts() );
            skyyrose_publish_apply( $plan, $directory );
            return array( 'status' => 'PUBLISHED', 'operation_id' => $plan['opid'], 'source_sha256' => SKYYROSE_PUBLISH_SOURCE_SHA );
        }
        skyyrose_publish_require( get_option( 'home' ) === 'https://skyyrose.co', 'TARGET_REFUSED' );
        skyyrose_publish_rollback( $plan, $directory );
        return array( 'status' => 'ROLLED_BACK', 'operation_id' => $plan['opid'], 'runtime_drift' => $drift );
    } finally { fclose( $lock ); }
}

if ( ! defined( 'SKYYROSE_PUBLISH_TEST_IMPORT' ) ) {
	try {
		$input = json_decode( base64_decode( $args[0] ?? '', true ), true, 32, JSON_THROW_ON_ERROR );
		skyyrose_publish_require( is_array( $input ), 'INPUT_REFUSED' );
		echo json_encode( skyyrose_publish_run( $input ), JSON_THROW_ON_ERROR ) . "\n";
	} catch ( Throwable $error ) {
		$codes = array( 'TARGET_REFUSED', 'DIRECTORY_REFUSED', 'INPUT_REFUSED', 'JOURNAL_REFUSED', 'SOURCE_REFUSED', 'WRITE_REFUSED', 'SYNC_REFUSED', 'OWNERSHIP_REFUSED', 'FINAL_REFUSED', 'TEMP_REFUSED', 'SYNTAX_REFUSED', 'LINK_REFUSED', 'ROLLBACK_REFUSED', 'LOCK_REFUSED' );
		$code = in_array( $error->getMessage(), $codes, true ) ? $error->getMessage() : 'LOCAL_EXECUTION_REFUSED';
		echo json_encode( array( 'status' => 'STOPPED', 'code' => $code ) ) . "\n";
		exit( 1 );
	}
}
