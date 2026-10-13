<?php
/**
 * Dependency-free contract tests for inc/cinematic-chapters.php.
 *
 * Run: php scripts/test-cinematic-chapters.php
 */

define( 'ABSPATH', __DIR__ . '/' );
$GLOBALS['sr2_tpl'] = false;

function __( $v ) { return $v; }
function esc_html( $v ) { return htmlspecialchars( (string) $v, ENT_QUOTES, 'UTF-8' ); }
function esc_attr( $v ) { return htmlspecialchars( (string) $v, ENT_QUOTES, 'UTF-8' ); }
function esc_url( $v ) { return htmlspecialchars( (string) $v, ENT_QUOTES, 'UTF-8' ); }
function esc_url_raw( $v ) { return (string) $v; }
function esc_attr_e( $v ) { echo esc_attr( $v ); }
function sanitize_key( $v ) { return preg_replace( '/[^a-z0-9_\-]/', '', strtolower( (string) $v ) ); }
function absint( $v ) { return abs( (int) $v ); }
function wp_json_encode( $v ) { return json_encode( $v ); }
function wp_parse_args( $a, $d ) { return array_merge( $d, (array) $a ); }
function add_action() {}
function apply_filters( $h, $v ) { return $v; }
function is_page_template( $t ) { return $GLOBALS['sr2_tpl']; }
function skyyrose2_immersive_url( $s ) { return 'https://example.test/worlds/' . $s . '/'; }

require __DIR__ . '/../inc/cinematic-chapters.php';

$fail = 0;
function check( $ok, $label ) {
	global $fail;
	echo ( $ok ? 'PASS ' : 'FAIL ' ) . $label . "\n";
	$fail += $ok ? 0 : 1;
}

$chapters = skyyrose2_chapters();
check( 4 === count( $chapters ), 'four chapters' );
check( array( 'I', 'II', 'III', 'IV' ) === array_column( $chapters, 'numeral' ), 'story order I-IV' );
check( 'play' === $chapters[3]['verb'] && 'kids-capsule' === $chapters[3]['slug'], 'chapter IV is play' );
check( array( '#d4af37', '#c0c0c0', '#eb4666', '#b76e79' ) === array_column( $chapters, 'accent' ), 'locked collection accents' );
foreach ( $chapters as $c ) {
	check( 1 === preg_match( '/^\d{1,3} \d{1,3} \d{1,3}$/', $c['rgb'] ), 'rgb is space-separated (valid in rgb(<r g b> / a)): ' . $c['slug'] );
}
check( ! skyyrose2_chapters_enabled(), 'chapters off by default' );
$GLOBALS['sr2_tpl'] = true;
check( skyyrose2_chapters_enabled(), 'chapters on for prologue template' );

ob_start();
skyyrose2_render_story_thread( 'black-rose' );
$thread = ob_get_clean();
check( 4 === substr_count( $thread, 'data-chapter-link' ), 'thread links all chapters' );
check( 1 === substr_count( $thread, 'aria-current="page"' ), 'thread marks exactly one current chapter' );

$slot = skyyrose2_media_slot( array( 'image' => 'https://e.test/a.webp', 'alt' => 'x"y', 'sku' => 'br-001' ) );
check( false !== strpos( $slot, 'data-tier="image"' ) && false !== strpos( $slot, 'alt="x&quot;y"' ), 'slot: image tier, escaped alt' );
$slot = skyyrose2_media_slot( array( 'image' => '', 'model' => array( 'glb' => 'https://e.test/m.glb' ) ) );
check( false !== strpos( $slot, 'data-tier="model"' ) && false === strpos( $slot, '<img' ), 'slot: model tier, no img when image unauthorised' );

exit( $fail ? 1 : 0 );
