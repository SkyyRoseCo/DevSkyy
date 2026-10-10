<?php
/** Offline integration contracts; no authentication or network required. */
define( 'ABSPATH', __DIR__ );
define( 'OBJECT', 'OBJECT' );
function add_action( ...$args ) {}
function add_filter( ...$args ) {}
function is_admin() { return $GLOBALS['admin'] ?? false; }
function is_preview() { return false; }
function is_feed() { return false; }
function wp_doing_ajax() { return false; }
function wp_get_environment_type() { return 'staging'; }
function absint( $value ) { return abs( (int) $value ); }
function get_post_field( $field, $id ) { return 9711 === $id ? 'faq' : 'custom-policy'; }
function get_page_by_path( $path, $output, $type ) { return $GLOBALS['pages'][ $path ] ?? null; }
function get_permalink( $id ) { return $GLOBALS['permalinks'][ $id ] ?? '/privacy-policy/'; }
function home_url() { return 'https://theme.test/'; }
function wp_parse_url( $url, $component = -1 ) { return parse_url( $url, $component ); }
function wp_unslash( $value ) { return $value; }
function sanitize_text_field( $value ) { return trim( strip_tags( (string) $value ) ); }
function add_query_arg( $args, $url ) { return $url . ( false === strpos( $url, '?' ) ? '?' : '&' ) . http_build_query( $args ); }
function wp_safe_redirect( $location, $status, $label ) { $GLOBALS['redirect'] = array( $location, $status, $label ); return false; }
function esc_url( $value ) { return (string) $value; }
function esc_html__( $value, $domain ) { return $value; }
require __DIR__ . '/../../wordpress-theme/skyyrose-flagship-2/inc/launch-readiness.php';
function check( $condition, $label ) { if ( ! $condition ) { throw new RuntimeException( $label ); } echo "PASS $label\n"; }
$GLOBALS['pages']['privacy-policy'] = (object) array( 'ID' => 9717, 'post_status' => 'publish', 'post_password' => '' );
$GLOBALS['permalinks'][9717] = '/privacy-policy/';
check( '/privacy-policy/' === skyyrose2_storefront_privacy_url( '/faq/', 9711 ), 'Known wrong privacy assignment resolves to published policy' );
check( '/custom-policy/' === skyyrose2_storefront_privacy_url( '/custom-policy/', 123 ), 'Custom privacy assignment is preserved' );
$GLOBALS['pages']['privacy-policy']->post_status = 'draft';
check( '/faq/' === skyyrose2_storefront_privacy_url( '/faq/', 9711 ), 'Draft policy is never exposed' );
$GLOBALS['pages']['privacy-policy']->post_status = 'publish';
$GLOBALS['pages']['privacy-policy']->post_password = 'private';
check( '/faq/' === skyyrose2_storefront_privacy_url( '/faq/', 9711 ), 'Password-protected policy is never exposed' );
$GLOBALS['pages']['hello-world'] = (object) array( 'ID' => 7, 'post_title' => 'Hello world!' );
class Readiness_Query {
	public $values = array( 'post__not_in' => array( 4 ), 'post_type' => '' );
	public function is_main_query() { return true; }
	public function is_home() { return true; }
	public function is_search() { return false; }
	public function get( $key ) { return $this->values[ $key ] ?? null; }
	public function set( $key, $value ) { $this->values[ $key ] = $value; }
}
$query = new Readiness_Query();
skyyrose2_exclude_default_journal_sample( $query );
check( array( 4, 7 ) === $query->get( 'post__not_in' ), 'Only stock sample is excluded; previous exclusions preserved' );
$query = new Readiness_Query(); $query->values['post_type'] = 'product';
skyyrose2_exclude_default_journal_sample( $query );
check( array( 4 ) === $query->get( 'post__not_in' ), 'Product queries remain untouched' );
$GLOBALS['admin'] = true; $query = new Readiness_Query();
skyyrose2_exclude_default_journal_sample( $query );
check( array( 4 ) === $query->get( 'post__not_in' ), 'Admin queries remain untouched' );

$expected_routes = array(
	'experiences'             => 'worlds',
	'experience-signature'    => 'worlds/signature',
	'experience-black-rose'   => 'worlds/black-rose',
	'experience-love-hurts'   => 'worlds/love-hurts',
	'experience-kids-capsule' => 'worlds/kids-capsule',
	'collections-world'       => 'collections',
	'landing-signature'       => 'collections/signature',
	'landing-black-rose'      => 'collections/black-rose',
	'landing-love-hurts'      => 'collections/love-hurts',
	'landing-kids-capsule'    => 'collections/kids-capsule',
	'collection-kids-capsule' => 'collections/kids-capsule',
);
check( $expected_routes === skyyrose2_retired_v2_page_routes(), 'Every retired V2 page route has one canonical destination' );

$GLOBALS['admin'] = false;
$GLOBALS['pages']['collections/signature'] = (object) array( 'ID' => 981, 'post_status' => 'publish', 'post_password' => '' );
$GLOBALS['permalinks'][981] = '/collections/signature/';
$atts = skyyrose2_canonical_collection_menu_links( array( 'href' => 'https://theme.test/landing-signature/' ) );
check( '/collections/signature/' === $atts['href'], 'Retired internal menu links resolve to their canonical collection' );
$GLOBALS['pages']['collections/signature']->post_status = 'draft';
$atts = skyyrose2_canonical_collection_menu_links( array( 'href' => '/landing-signature/' ) );
check( '/landing-signature/' === $atts['href'], 'Draft canonical targets leave legacy internal links untouched' );
$GLOBALS['pages']['collections/signature']->post_status = 'publish';

$GLOBALS['pages']['collections/kids-capsule'] = (object) array( 'ID' => 982, 'post_status' => 'publish', 'post_password' => '' );
$GLOBALS['permalinks'][982] = '/collections/kids-capsule/';
$footer_args = (object) array( 'menu_class' => 'menu-footer-shop' );
$footer_items = skyyrose2_restore_footer_kids_capsule_link( '<li>Pre-Order</li>', $footer_args );
check( false !== strpos( $footer_items, '/collections/kids-capsule/' ), 'Footer restores the canonical Kids Capsule collection link' );

$_SERVER['REQUEST_METHOD'] = 'GET';
$_SERVER['REQUEST_URI'] = '/landing-signature/?utm_source=launch&utm_campaign=soft-launch';
$_GET = array( 'utm_source' => 'launch', 'utm_campaign' => 'soft-launch' );
$GLOBALS['redirect'] = null;
skyyrose2_redirect_retired_collection_alias_request();
check( array( '/collections/signature/?utm_source=launch&utm_campaign=soft-launch', 302, 'SkyyRose V2' ) === $GLOBALS['redirect'], 'Retired aliases preserve UTM attribution on staging redirects' );
$GLOBALS['pages']['collections/signature']->post_status = 'draft';
$GLOBALS['redirect'] = null;
skyyrose2_redirect_retired_collection_alias_request();
check( null === $GLOBALS['redirect'], 'Draft canonical targets fail closed without a redirect' );
