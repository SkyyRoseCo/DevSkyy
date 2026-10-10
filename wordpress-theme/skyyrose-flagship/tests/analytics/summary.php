<?php
/** Offline legacy summary/dashboard fixture; authentication N/A. */
define( 'ABSPATH', __DIR__ );
define( 'ARRAY_A', 'ARRAY_A' );
function add_action( ...$args ) {}
function wp_create_nonce( $value ) { return 'fixture'; }
function esc_html( $value ) { return htmlspecialchars( (string) $value ); }
function esc_html__( $value, $domain ) { return $value; }
function __( $value, $domain ) { return $value; }
function esc_html_e( $value, $domain ) { echo esc_html( $value ); }
function esc_attr_e( $value, $domain ) { echo esc_html( $value ); }
function esc_attr( $value ) { return esc_html( $value ); }
function absint( $value ) { return abs( (int) $value ); }
function wp_json_encode( $value ) { return json_encode( $value ); }
function number_format_i18n( $value ) { return number_format( $value ); }
$wpdb = new class {
	public $prefix = 'fixture_';
	public function prepare( $sql, ...$values ) { return $sql; }
	public function get_var( $sql ) {
		if ( str_contains( $sql, 'visitor_hash' ) ) { throw new RuntimeException( 'Legacy identities must not imply visitor coverage' ); }
		return 12;
	}
	public function get_results( ...$args ) { return array(); }
};
require dirname( __DIR__, 2 ) . '/inc/experience-analyzer.php';
$summary = skyyrose_see_get_summary();
if ( 12 !== $summary['total_events'] || null !== $summary['unique_visitors'] || 'unavailable' !== $summary['unique_visitors_status'] || ! $summary['unique_visitors_evidence'] ) {
	throw new RuntimeException( 'Summary must preserve observed engagement and unavailable visitors' );
}
ob_start();
require dirname( __DIR__, 2 ) . '/inc/admin-experience-dashboard.php';
$html = ob_get_clean();
if ( ! preg_match( '/stat-value">Unavailable<\/span>\s*<span[^>]+>Unique Visitors/', $html ) ) {
	throw new RuntimeException( 'Admin must display unavailable visitor count, not zero' );
}
echo "PASS: 2 legacy summary/dashboard checks (offline; authentication N/A).\n";
