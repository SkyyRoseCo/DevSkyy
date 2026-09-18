<?php
/** Offline harness for the real theme output filter; no WordPress or network boot. */
define( 'ABSPATH', __DIR__ );
function add_action( ...$args ) {}
function esc_attr( $value ) {
	return htmlspecialchars( (string) $value, ENT_QUOTES, 'UTF-8' );
}
function esc_attr__( $value, $domain ) {
	return esc_attr( $value );
}
require $argv[1];
$filter = new SkyyRose_Accessibility_Fix();
echo $filter->process( file_get_contents( $argv[2] ) );
