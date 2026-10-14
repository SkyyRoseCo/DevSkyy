<?php
/**
 * Runtime contract: theme-generated links never point at a page that is not
 * published. Pulls the real function bodies out of source, so it cannot drift
 * from what ships.
 *
 * Run: php scripts/test-dead-links.php
 */

define( 'ABSPATH', __DIR__ . '/' );
define( 'OBJECT', 'OBJECT' );

class WP_Post {
	public $post_status;
	public $post_password = '';
	public $ID;
	public function __construct( $id, $status ) {
		$this->ID          = $id;
		$this->post_status = $status;
	}
}

$GLOBALS['sr2_pages'] = array(); // path => WP_Post.

function home_url( $path = '' ) {
	return 'https://t.test' . $path;
}
function sanitize_key( $v ) {
	return strtolower( preg_replace( '/[^a-z0-9_\-]/i', '', (string) $v ) );
}
function get_page_by_path( $path ) {
	return $GLOBALS['sr2_pages'][ trim( $path, '/' ) ] ?? null;
}
function get_permalink( $post ) {
	return 'https://t.test/?p=' . $post->ID;
}
function __( $v ) {
	return $v;
}
function skyyrose2_marketplace_pages() {
	return array(
		'journal'                => array( 'path' => 'journal' ),
		'returns-exchanges'      => array( 'path' => 'returns-exchanges' ),
		'worlds'                 => array( 'path' => 'worlds' ),
		'immersive-signature'    => array( 'path' => 'worlds/signature' ),
		'immersive-black-rose'   => array( 'path' => 'worlds/black-rose' ),
		'immersive-love-hurts'   => array( 'path' => 'worlds/love-hurts' ),
		'immersive-kids-capsule' => array( 'path' => 'worlds/kids-capsule' ),
		'about'                  => array( 'path' => 'about' ),
	);
}
function skyyrose2_shop_url() {
	return 'https://t.test/shop/';
}

/** Evaluate named top-level functions out of a source file. */
function sr2_load( $file, array $names ) {
	$src = file_get_contents( dirname( __DIR__ ) . '/' . $file );
	foreach ( $names as $name ) {
		if ( ! preg_match( '/^function ' . preg_quote( $name, '/' ) . '\(.*?^}\n/ms', $src, $m ) ) {
			fwrite( STDERR, "Cannot extract {$name} from {$file}\n" );
			exit( 1 );
		}
		eval( $m[0] ); // phpcs:ignore Squiz.PHP.Eval.Discouraged -- test harness loads shipped source.
	}
}
sr2_load( 'functions.php', array( 'skyyrose2_published_page_permalink', 'skyyrose2_marketplace_page_stand_ins', 'skyyrose2_marketplace_page_live_url', 'skyyrose2_marketplace_page_url' ) );
sr2_load( 'inc/global-shell.php', array( 'skyyrose2_live_links', 'skyyrose2_house_links', 'skyyrose2_masthead_links' ) );

$fail = 0;
function sr2_assert( $ok, $msg ) {
	global $fail;
	if ( ! $ok ) {
		fwrite( STDERR, "FAIL: {$msg}\n" );
		$fail++;
	}
}

// Live site shape: experience-* + shipping-returns + about published; worlds/* draft; journal absent.
$GLOBALS['sr2_pages'] = array(
	'about'                   => new WP_Post( 1, 'publish' ),
	'shipping-returns'        => new WP_Post( 2, 'publish' ),
	'experiences'             => new WP_Post( 3, 'publish' ),
	'experience-signature'    => new WP_Post( 4, 'publish' ),
	'experience-black-rose'   => new WP_Post( 5, 'publish' ),
	'experience-love-hurts'   => new WP_Post( 6, 'publish' ),
	'experience-kids-capsule' => new WP_Post( 7, 'publish' ),
	'worlds/signature'        => new WP_Post( 10432, 'draft' ),
	'worlds/black-rose'       => new WP_Post( 10433, 'draft' ),
	'worlds/love-hurts'       => new WP_Post( 10434, 'draft' ),
);

// 1. A draft registry page never becomes a ?page_id= link; the live scene serves instead.
sr2_assert( 'https://t.test/?p=5' === skyyrose2_marketplace_page_url( 'immersive-black-rose' ), 'draft worlds/black-rose must stand in with experience-black-rose' );
sr2_assert( 'https://t.test/?p=7' === skyyrose2_marketplace_page_url( 'immersive-kids-capsule' ), 'absent worlds/kids-capsule must stand in with experience-kids-capsule' );
sr2_assert( 'https://t.test/?p=3' === skyyrose2_marketplace_page_url( 'worlds' ), 'absent worlds hub stands in with experiences' );
sr2_assert( 'https://t.test/?p=1' === skyyrose2_marketplace_page_url( 'about' ), 'a published page keeps its own permalink' );

// 2. Once the founder publishes the registry page it wins over the stand-in.
$GLOBALS['sr2_pages']['worlds/black-rose'] = new WP_Post( 10433, 'publish' );
sr2_assert( 'https://t.test/?p=10433' === skyyrose2_marketplace_page_url( 'immersive-black-rose' ), 'published worlds/black-rose beats the stand-in' );
$GLOBALS['sr2_pages']['worlds/black-rose'] = new WP_Post( 10433, 'draft' );

// 3. Password-protected stand-ins are not used.
$GLOBALS['sr2_pages']['experience-signature']->post_password = 'x';
sr2_assert( '' === skyyrose2_marketplace_page_live_url( 'immersive-signature' ), 'protected stand-in is not a live URL' );
$GLOBALS['sr2_pages']['experience-signature']->post_password = '';

// 4. Journal has no live page: no live URL, and it leaves both navs; the documented route is kept for the importer.
sr2_assert( '' === skyyrose2_marketplace_page_live_url( 'journal' ), 'journal has no live URL while unpublished' );
sr2_assert( 'https://t.test/journal/' === skyyrose2_marketplace_page_url( 'journal' ), 'documented route fallback stays for importer/setup' );
$house = array_keys( skyyrose2_house_links() );
$mast  = array_keys( skyyrose2_masthead_links() );
sr2_assert( ! in_array( 'Journal', $house, true ) && ! in_array( 'Journal', $mast, true ), 'Journal must not be linked while unpublished' );
sr2_assert( ! in_array( 'Lookbook', $house, true ), 'Lookbook must not be linked while unpublished' );
sr2_assert( in_array( 'Shop', $house, true ) && in_array( 'Shop', $mast, true ), 'Shop stays' );

// 5. Publishing the page brings the entry back.
$GLOBALS['sr2_pages']['journal']  = new WP_Post( 20, 'publish' );
$GLOBALS['sr2_pages']['lookbook'] = new WP_Post( 21, 'publish' );
$house = skyyrose2_house_links();
sr2_assert( isset( $house['Journal'] ) && 'https://t.test/?p=20' === $house['Journal'], 'published Journal returns to the house nav' );
sr2_assert( isset( $house['Lookbook'] ) && 'https://t.test/?p=21' === $house['Lookbook'], 'published Lookbook returns to the house nav' );

// 6. No two nav entries share a URL.
$urls = array_values( skyyrose2_house_links() );
sr2_assert( count( $urls ) === count( array_unique( $urls ) ), 'house nav has no duplicate destinations' );

if ( $fail ) {
	exit( 1 );
}
echo "Dead-link contract passed.\n";
