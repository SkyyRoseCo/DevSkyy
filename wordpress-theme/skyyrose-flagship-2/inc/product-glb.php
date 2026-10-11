<?php
/**
 * Registry-bound, optional product GLB enhancement. Native commerce stays available.
 *
 * @package SkyyRoseFlagship2
 */

defined( 'ABSPATH' ) || exit;

/** Return only the build projection of registry-owned acceptance bindings. */
function skyyrose2_glb_manifest() {
	$registry = skyyrose2_presentation_registry();
	$manifest = $registry['glb_runtime'] ?? array();
	$digest   = $registry['product_registry_sha256'] ?? '';
	if ( ! is_string( $digest ) || ! preg_match( '/^[a-f0-9]{64}$/D', $digest ) || 'skyyrose.accepted-glb-runtime.v1' !== ( $manifest['schema'] ?? '' ) || $digest !== ( $manifest['registry_sha256'] ?? '' ) || true !== ( $manifest['publication_authorized'] ?? false ) || empty( $manifest['entries'] ) || ! is_array( $manifest['entries'] ) ) {
		return array();
	}
	foreach ( $manifest['entries'] as $entry ) {
		if ( ! is_array( $entry ) || ! isset( $registry['products'][ $entry['sku'] ?? '' ] ) || $digest !== ( $entry['registry_sha256'] ?? '' ) || true !== ( $entry['publication_authorized'] ?? false ) || 'PASS' !== ( $entry['qc_binding'] ?? '' ) || 'PASS' !== ( $entry['product_fidelity'] ?? '' ) || 'FOUNDER_APPROVED' !== ( $entry['creative_approval'] ?? '' ) || 'PASS' !== ( $entry['license'] ?? '' ) || 'PASS' !== ( $entry['runtime_budget'] ?? '' ) || empty( $entry['approval_id'] ) ) {
			return array();
		}
	}
	return $manifest;
}

/** Resolve canonical IDs on the server on every open/retry; no cart writes. */
function skyyrose2_glb_resolve( $request ) {
	if ( ! function_exists( 'wc_get_product_id_by_sku' ) ) {
		return new WP_Error( 'glb_unavailable', __( 'Product view unavailable.', 'skyyrose-flagship-2' ), array( 'status' => 409 ) );
	}
	$registry = skyyrose2_presentation_registry();
	$sku      = $request->get_param( 'sku' );
	try {
		$product = skyyrose2_glb_native_product_link(
			(int) wc_get_product_id_by_sku( $sku ),
			(int) $request->get_param( 'variation_id' ),
			$request->get_param( 'attributes' ),
			$sku,
			$registry['products'] ?? array(),
			$registry['product_registry_sha256'] ?? ''
		);
	} catch ( Exception $error ) {
		return new WP_Error( 'glb_selection_changed', __( 'Review the current product selection.', 'skyyrose-flagship-2' ), array( 'status' => 409 ) );
	}
	$response = new WP_REST_Response( $product );
	$response->header( 'Cache-Control', 'no-store' );
	return $response;
}

/** Public read-only product identity route; request data never supplies the catalog. */
function skyyrose2_glb_routes() {
	register_rest_route(
		'skyyrose/v1',
		'/product-view',
		array(
			'methods'             => 'POST',
			'callback'            => 'skyyrose2_glb_resolve',
			'permission_callback' => '__return_true',
			'args'               => array(
				'sku'          => array( 'required' => true, 'type' => 'string', 'pattern' => '^[a-z0-9]+(?:-[a-z0-9]+)*$' ),
				'variation_id' => array( 'type' => 'integer', 'minimum' => 0, 'default' => 0 ),
				'attributes'   => array( 'type' => 'object', 'default' => array() ),
			),
		)
	);
}
add_action( 'rest_api_init', 'skyyrose2_glb_routes' );

/** Render no empty stage and download no renderer when there is no accepted asset. */
function skyyrose2_glb_product_view() {
	global $product;
	$manifest = skyyrose2_glb_manifest();
	if ( ! $product || ! $manifest ) {
		return;
	}
	$sku     = $product->get_sku();
	$entries = array_values( array_filter( $manifest['entries'], static function ( $entry ) use ( $sku ) { return $sku === $entry['sku']; } ) );
	if ( ! $entries ) {
		return;
	}
	$config = array(
		'sku'         => $sku,
		'productId'   => $product->get_id(),
		'registrySha' => $manifest['registry_sha256'],
		'manifest'    => array_merge( $manifest, array( 'entries' => $entries ) ),
		'endpoint'    => rest_url( 'skyyrose/v1/product-view' ),
		'vendorBase'  => SKYYROSE2_URI . '/assets/js/lib/three-r170/',
	);
	wp_enqueue_script_module( 'skyyrose2-product-glb', SKYYROSE2_URI . '/assets/js/product-glb-init.mjs', array(), skyyrose2_asset_version( '/assets/js/product-glb-init.mjs' ) );
	wp_enqueue_style( 'skyyrose2-product-glb', SKYYROSE2_URI . '/assets/css/product-glb.min.css', array(), skyyrose2_asset_version( '/assets/css/product-glb.min.css' ) );
	?>
	<section data-product-glb data-config="<?php echo esc_attr( wp_json_encode( $config ) ); ?>" aria-label="<?php esc_attr_e( 'Product view', 'skyyrose-flagship-2' ); ?>">
		<a href="<?php echo esc_url( $product->get_permalink() ); ?>"><?php esc_html_e( 'Product details', 'skyyrose-flagship-2' ); ?></a>
		<button type="button" data-viewer-open="<?php echo esc_attr( $sku ); ?>" hidden><?php esc_html_e( 'Explore in 3D', 'skyyrose-flagship-2' ); ?></button>
		<p data-viewer-status role="status" aria-live="polite"><?php esc_html_e( 'Choose a product option to explore its available views.', 'skyyrose-flagship-2' ); ?></p>
		<div data-viewer-stage tabindex="0" aria-label="<?php esc_attr_e( 'Interactive product view. Use arrow keys to rotate.', 'skyyrose-flagship-2' ); ?>" hidden></div>
		<button type="button" data-viewer-retry hidden><?php esc_html_e( 'Retry', 'skyyrose-flagship-2' ); ?></button>
		<button type="button" data-viewer-reset disabled><?php esc_html_e( 'Reset view', 'skyyrose-flagship-2' ); ?></button>
		<button type="button" data-viewer-back><?php esc_html_e( 'Back to product', 'skyyrose-flagship-2' ); ?></button>
	</section>
	<?php
}
add_action( 'woocommerce_single_product_summary', 'skyyrose2_glb_product_view', 35 );
