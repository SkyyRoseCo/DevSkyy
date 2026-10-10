<?php
/** Isolated regression checks; no WordPress database, network, orders or writes. */
define( 'ABSPATH', __DIR__ );
define( 'OBJECT', 'OBJECT' );
function add_action( ...$args ) {}
function add_filter( ...$args ) {}
function wp_strip_all_tags( $text ) { return strip_tags( $text ); }
function esc_attr( $text ) { return htmlspecialchars( $text, ENT_QUOTES, 'UTF-8' ); }
function get_page_by_path( $path, ...$args ) { return $GLOBALS['pages'][ $path ] ?? null; }
function get_permalink( $id ) { return 'https://staging.example/' . $id . '/'; }
function home_url() { return 'https://staging.example'; }
function wp_parse_url( $url, $component ) { return parse_url( $url, $component ); }
require dirname( __DIR__, 2 ) . '/wordpress-theme/skyyrose-flagship-2/inc/launch-readiness.php';
function check( $condition, $label ) { if ( ! $condition ) { throw new RuntimeException( $label ); } echo "PASS $label\n"; }
foreach ( skyyrose2_legacy_collection_routes() as $slug => $target ) {
	$GLOBALS['pages'][ $target ] = (object) array( 'ID' => $target, 'post_status' => 'publish', 'post_password' => '' );
	$post = (object) array( 'post_type' => 'page', 'post_name' => $slug );
	check( skyyrose2_retired_content_target( $post ) === 'https://staging.example/' . $target . '/', 'Exact legacy alias: ' . $slug );
	check( skyyrose2_canonical_collection_menu_links( array( 'href' => 'https://staging.example/' . $slug . '/' ) )['href'] === 'https://staging.example/' . $target . '/', 'Menu repair: ' . $slug );
}
check( skyyrose2_legacy_collection_routes() === array( 'collection-black-rose' => 'collections/black-rose', 'collection-love-hurts' => 'collections/love-hurts', 'collection-signature' => 'collections/signature' ), 'Legacy route guard remains bounded to the three retired aliases' );
check( '' === skyyrose2_retired_content_target( (object) array( 'post_type' => 'page', 'post_name' => 'experience-signature' ) ), 'Working experience route preserved' );
$external = array( 'href' => 'https://another.example/collection-signature/' );
check( skyyrose2_canonical_collection_menu_links( $external ) === $external, 'External menu destination preserved' );
$GLOBALS['pages']['collections/signature']->post_status = 'draft';
check( '' === skyyrose2_retired_content_target( (object) array( 'post_type' => 'page', 'post_name' => 'collection-signature' ) ), 'Draft destination fails closed' );
$GLOBALS['pages']['journal'] = (object) array( 'ID' => 'journal', 'post_status' => 'publish', 'post_password' => '' );
$demo = (object) array( 'post_type' => 'post', 'post_name' => 'hello-world', 'post_title' => 'Hello world!', 'post_content' => '/* luxury-design-system.css */' );
check( skyyrose2_retired_content_target( $demo ) === 'https://staging.example/journal/', 'Verified sample retires to Journal' );
$demo->post_content = 'A genuine replacement story.';
check( '' === skyyrose2_retired_content_target( $demo ), 'Rewritten non-demo content is not silently retired' );
$input = '<!-- wp:heading --><h1 id="policy">Privacy Policy</h1><p>Policy wording stays unchanged.</p>';
$output = skyyrose2_strip_redundant_content_title( $input, 'Privacy Policy' );
check( false === strpos( $output, '<h1' ) && str_contains( $output, 'id="policy"' ) && str_contains( $output, '<p>Policy wording stays unchanged.</p>' ), 'Duplicate removed with policy wording and anchor intact' );
$input = '<h2>Other heading</h2><p>Copy</p>';
check( skyyrose2_strip_redundant_content_title( $input, 'Page title' ) === $input, 'Nonmatching heading preserved' );
$input = '<p>Important introduction.</p><h1>Page title</h1>';
check( skyyrose2_strip_redundant_content_title( $input, 'Page title' ) === $input, 'Non-leading heading preserved' );
$input = '<h1>Care &amp; Fit</h1><p>Copy</p>';
check( skyyrose2_strip_redundant_content_title( $input, 'Care & Fit' ) === '<p>Copy</p>', 'Entity-equivalent title matched' );
