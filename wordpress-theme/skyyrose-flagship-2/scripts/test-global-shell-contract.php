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
	'id="skyyrose-mascot-recall"',
	'aria-controls="skyy-ask-dialog"',
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

if ( 1 !== substr_count( $source, 'id="skyyrose-mascot-recall"' ) ) {
	fwrite( STDERR, "Ask Skyy recall ID must remain unique.\n" );
	exit( 1 );
}

if ( false === strpos( $source, '<details><summary>' ) ) {
	fwrite( STDERR, "Compact footer disclosures are missing.\n" );
	exit( 1 );
}

echo "Global shell contract passed.\n";
