<?php
/**
 * Dependency-free rendering contract tests for template-parts/pages/service.php.
 *
 * Run: php scripts/test-page-service-template.php
 */

define( 'ABSPATH', __DIR__ . '/' );

$skyyrose2_template_test_state = array(
	'title'          => 'Frequently asked questions',
	'post_content'   => '<p>Authored WordPress page content.</p>',
	'content_calls'  => 0,
	'filter_inputs'  => array(),
	'kses_inputs'    => array(),
	'home_url_inputs' => array(),
);

function esc_attr( $value ) {
	return htmlspecialchars( (string) $value, ENT_QUOTES, 'UTF-8' );
}
function esc_html( $value ) {
	return htmlspecialchars( (string) $value, ENT_QUOTES, 'UTF-8' );
}
function esc_url( $value ) {
	return htmlspecialchars( (string) $value, ENT_QUOTES, 'UTF-8' );
}
function __( $value ) {
	return $value;
}
function esc_html_e( $value ) {
	echo esc_html( $value );
}
function esc_attr_e( $value ) {
	echo esc_attr( $value );
}
function get_the_title() {
	global $skyyrose2_template_test_state;
	return $skyyrose2_template_test_state['title'];
}
function the_title() {
	echo esc_html( get_the_title() );
}
function the_content() {
	global $skyyrose2_template_test_state;
	++$skyyrose2_template_test_state['content_calls'];
	echo $skyyrose2_template_test_state['post_content'];
}
function apply_filters( $hook, $value ) {
	global $skyyrose2_template_test_state;
	$skyyrose2_template_test_state['filter_inputs'][] = array( $hook, $value );
	return '<div class="filtered">' . $value . '</div>';
}
function wp_kses_post( $value ) {
	global $skyyrose2_template_test_state;
	$skyyrose2_template_test_state['kses_inputs'][] = $value;
	return $value;
}
function home_url( $path = '' ) {
	global $skyyrose2_template_test_state;
	$skyyrose2_template_test_state['home_url_inputs'][] = $path;
	return 'https://skyyrose.co/' . ltrim( $path, '/' );
}

function skyyrose2_render_service_part( array $template_args ) {
	$args = $template_args;
	ob_start();
	require dirname( __DIR__ ) . '/template-parts/pages/service.php';
	return ob_get_clean();
}

$skyyrose2_template_test_failures = array();
function skyyrose2_template_test_assert( $condition, $message ) {
	global $skyyrose2_template_test_failures;
	if ( ! $condition ) {
		$skyyrose2_template_test_failures[] = $message;
	}
}

$canonical_faq = '<h2>Canonical size question?</h2><p>Canonical answer.</p>';
$faq_html      = skyyrose2_render_service_part(
	array(
		'slug'            => 'faq',
		'is_account'      => false,
		'is_service'      => true,
		'managed_content' => $canonical_faq,
	)
);
skyyrose2_template_test_assert( str_contains( $faq_html, 'class="sr2-generic-page sr2-c-service"' ), 'Service shell class changed.' );
skyyrose2_template_test_assert( str_contains( $faq_html, 'data-sr2-route="service"' ), 'Service route marker changed.' );
skyyrose2_template_test_assert( str_contains( $faq_html, '<header class="sr2-generic-head">' ) && str_contains( $faq_html, '<h1>Frequently asked questions</h1>' ), 'Generic heading semantics changed.' );
skyyrose2_template_test_assert( str_contains( $faq_html, '<div class="filtered">' . $canonical_faq . '</div>' ), 'Managed FAQ content no longer uses the content filter output.' );
skyyrose2_template_test_assert( array( array( 'the_content', $canonical_faq ) ) === $skyyrose2_template_test_state['filter_inputs'], 'Managed FAQ must pass the canonical content to the_content filter.' );
skyyrose2_template_test_assert( 0 === $skyyrose2_template_test_state['content_calls'], 'Managed FAQ must not fall back to stale page content.' );
skyyrose2_template_test_assert( 1 === count( $skyyrose2_template_test_state['kses_inputs'] ), 'Managed FAQ must retain wp_kses_post sanitization.' );
skyyrose2_template_test_assert( 5 === substr_count( $faq_html, 'https://skyyrose.co/' ), 'Service navigation must retain five absolute home_url destinations.' );
skyyrose2_template_test_assert( array( '/shipping-returns/', '/returns-exchanges/', '/size-guide/', '/faq/', '/contact/' ) === $skyyrose2_template_test_state['home_url_inputs'], 'Service-link route order changed.' );

$skyyrose2_template_test_state['content_calls'] = 0;
$skyyrose2_template_test_state['filter_inputs'] = array();
$skyyrose2_template_test_state['kses_inputs']   = array();
$page_html = skyyrose2_render_service_part(
	array(
		'slug'            => 'journal',
		'is_account'      => false,
		'is_service'      => false,
		'managed_content' => '',
	)
);
skyyrose2_template_test_assert( str_contains( $page_html, 'class="sr2-generic-page" data-sr2-route="page"' ), 'Generic fallback route changed.' );
skyyrose2_template_test_assert( str_contains( $page_html, $skyyrose2_template_test_state['post_content'] ), 'Generic fallback must render native page content.' );
skyyrose2_template_test_assert( 1 === $skyyrose2_template_test_state['content_calls'], 'Generic fallback must invoke the_content exactly once.' );
skyyrose2_template_test_assert( array() === $skyyrose2_template_test_state['filter_inputs'] && array() === $skyyrose2_template_test_state['kses_inputs'], 'Generic fallback must not apply the managed FAQ pipeline.' );
skyyrose2_template_test_assert( ! str_contains( $page_html, 'sr2-c-service__links' ), 'Non-service pages must not render service navigation.' );

$skyyrose2_template_test_state['content_calls']   = 0;
$skyyrose2_template_test_state['filter_inputs']   = array();
$skyyrose2_template_test_state['kses_inputs']     = array();
$skyyrose2_template_test_state['home_url_inputs'] = array();
$service_html = skyyrose2_render_service_part(
	array(
		'slug'            => 'size-guide',
		'is_account'      => false,
		'is_service'      => true,
		'managed_content' => '',
	)
);
skyyrose2_template_test_assert( str_contains( $service_html, 'class="sr2-generic-page sr2-c-service" data-sr2-route="service"' ), 'Non-FAQ service route or class changed.' );
skyyrose2_template_test_assert( str_contains( $service_html, $skyyrose2_template_test_state['post_content'] ), 'Non-FAQ service pages must render native page content.' );
skyyrose2_template_test_assert( 1 === $skyyrose2_template_test_state['content_calls'], 'Non-FAQ service pages must invoke the_content exactly once.' );
skyyrose2_template_test_assert( array() === $skyyrose2_template_test_state['filter_inputs'] && array() === $skyyrose2_template_test_state['kses_inputs'], 'Non-FAQ service pages must not apply the managed FAQ pipeline.' );
skyyrose2_template_test_assert( 5 === substr_count( $service_html, 'https://skyyrose.co/' ), 'Non-FAQ service pages must retain five service links.' );
skyyrose2_template_test_assert( array( '/shipping-returns/', '/returns-exchanges/', '/size-guide/', '/faq/', '/contact/' ) === $skyyrose2_template_test_state['home_url_inputs'], 'Non-FAQ service-link route order changed.' );

$skyyrose2_template_test_state['content_calls'] = 0;
$skyyrose2_template_test_state['filter_inputs'] = array();
$skyyrose2_template_test_state['kses_inputs']   = array();
$account_html = skyyrose2_render_service_part(
	array(
		'slug'            => 'my-account',
		'is_account'      => true,
		'is_service'      => false,
		'managed_content' => '',
	)
);
skyyrose2_template_test_assert( str_contains( $account_html, 'class="sr2-generic-page sr2-c-account" data-sr2-route="account"' ), 'Account shell route or class changed.' );
skyyrose2_template_test_assert( str_contains( $account_html, '<p class="sr2-eyebrow">Client account</p>' ), 'Account eyebrow changed.' );
skyyrose2_template_test_assert( str_contains( $account_html, $skyyrose2_template_test_state['post_content'] ), 'Account pages must render native Woo page content.' );
skyyrose2_template_test_assert( 1 === $skyyrose2_template_test_state['content_calls'], 'Account pages must invoke the_content exactly once.' );
skyyrose2_template_test_assert( array() === $skyyrose2_template_test_state['filter_inputs'] && array() === $skyyrose2_template_test_state['kses_inputs'], 'Account pages must not apply the managed FAQ pipeline.' );
skyyrose2_template_test_assert( ! str_contains( $account_html, 'sr2-c-service__links' ), 'Account pages must not render service navigation.' );

if ( $skyyrose2_template_test_failures ) {
	fwrite( STDERR, "FAIL\n- " . implode( "\n- ", $skyyrose2_template_test_failures ) . "\n" );
	exit( 1 );
}

echo "PASS: generic/service/account page template rendering contract preserved.\n";
