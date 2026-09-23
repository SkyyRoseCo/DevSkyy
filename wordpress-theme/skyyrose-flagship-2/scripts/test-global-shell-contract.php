<?php
/** Source contract for the reference masthead and compact footer. */

$source = file_get_contents( dirname( __DIR__ ) . '/inc/global-shell.php' );
if ( false === $source ) {
	fwrite( STDERR, "Unable to read global shell.\n" );
	exit( 1 );
}

$required = array(
	'skyyrose2_masthead_links',
	"__( 'Shop', 'skyyrose-flagship-2' )",
	"__( 'Collections', 'skyyrose-flagship-2' )",
	"__( 'Journal', 'skyyrose-flagship-2' )",
	"__( 'About', 'skyyrose-flagship-2' )",
	'data-brand-video=',
	'data-brand-animation=',
	'data-brand-animation-mode="viewport"',
	"SkyyRose",
	'data-search-open',
	'data-bag-open',
	'data-sr2-menu',
	'aria-controls="sr2-menu"',
	"wc_get_page_permalink( 'myaccount' )",
	'data-nav-preview-toggle',
	"'footer-house'",
	"'footer-services'",
	"'privacy-policy'",
	"'terms-of-service'",
	"'accessibility'",
);

foreach ( $required as $needle ) {
	if ( false === strpos( $source, $needle ) ) {
		fwrite( STDERR, "Missing shell contract: {$needle}\n" );
		exit( 1 );
	}
}

// Founder direction 2026-09-22: the masthead and menu carry no mascot. Skyy walks
// onto the page from the footer-mounted dock and owns the only recall control.
if ( false !== strpos( $source, 'skyyrose-mascot' ) ) {
	fwrite( STDERR, "The header must not carry the mascot; the dock in template-parts/skyy-mascot.php owns it.\n" );
	exit( 1 );
}
$mascot = file_get_contents( dirname( __DIR__ ) . '/template-parts/skyy-mascot.php' );
if ( false === $mascot ) {
	fwrite( STDERR, "Unable to read the mascot template.\n" );
	exit( 1 );
}
foreach (
	array(
		'id="skyy-hero-stage" class="skyy-dock"',
		'data-skyy-dock',
		'aria-controls="skyy-ask-dialog"',
		'id="skyy-hero-chat"',
		'id="skyy-hero-dismiss"',
		'id="skyy-motion-toggle"',
		'id="skyy-presence-status"',
		'id="skyyrose-mascot-trigger"',
		'class="skyyrose-mascot__recall skyy-dock__recall"',
		'aria-haspopup="dialog" aria-expanded="false" hidden',
		'is_checkout()',
	) as $needle
) {
	if ( false === strpos( $mascot, $needle ) ) {
		fwrite( STDERR, "Missing walk-on dock contract: {$needle}\n" );
		exit( 1 );
	}
}
if ( 1 !== substr_count( $mascot, 'id="skyyrose-mascot-recall"' ) ) {
	fwrite( STDERR, "Ask Skyy recall ID must appear exactly once, in the dock.\n" );
	exit( 1 );
}
// The dock runtime CSS must pin her bottom-right and keep the recall hidden until a dismissal.
$mascot_css = file_get_contents( dirname( __DIR__ ) . '/assets/css/mascot.css' );
if ( false === $mascot_css ) {
	fwrite( STDERR, "Unable to read mascot.css.\n" );
	exit( 1 );
}
foreach ( array( '#skyy-hero-stage.skyy-dock {', 'position: fixed; right: var(--sr2-dock-offset); bottom: var(--sr2-dock-offset); z-index: var(--sr2-layer-guide);', 'body #skyyrose-mascot-recall[hidden] { display: none !important; }', 'body:has(dialog[open]) #skyy-hero-stage.skyy-dock', '--skyy-entry-shift' ) as $needle ) {
	if ( false === strpos( $mascot_css, $needle ) ) {
		fwrite( STDERR, "Missing dock CSS contract: {$needle}\n" );
		exit( 1 );
	}
}

if ( false === strpos( $source, '<details><summary>' ) ) {
	fwrite( STDERR, "Compact footer disclosures are missing.\n" );
	exit( 1 );
}

echo "Global shell contract passed.\n";
