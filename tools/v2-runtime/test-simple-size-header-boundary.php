<?php
/** Offline native-header-method control with illustrative cart/order stubs; no DB or HTTP. */
define( 'ABSPATH', __DIR__ . '/' );
$native = '/Users/theceo/.codex/worktrees/release-gates-20261019/DevSkyy/.artifacts/release-gates-20261019/gate4-populated/run-1792441452292547000/wordpress/wp-content/plugins/woocommerce/';
define( 'WC_ABSPATH', $native );
$pins = array(
	'src/StoreApi/Routes/RouteInterface.php' => '39760e59879c60a51919a87107b00a34f9a322a0ae21fc5bc025de17de2770ed',
	'src/StoreApi/Routes/V1/AbstractRoute.php' => '240bc7cf0abb3ec25b63ed5fe9c2017f16e87e58755fe9523f4fd3777a30bd28',
	'src/StoreApi/Utilities/DraftOrderTrait.php' => '7eaf37a8566e48ac7ddc8b6e591bf15a49ff5edc3b04ce59169415dada86da81',
	'src/StoreApi/Routes/V1/AbstractCartRoute.php' => '181673ff9520922aa4054fc8d5636c97321a6668317e2adf0040a1f769bb0387',
	'src/StoreApi/Exceptions/RouteException.php' => 'fbc89fb9ba3e95e193451e0a030bee38b615d7c26b2cada17988e0e505f112da',
);
foreach ( $pins as $relative => $digest ) {
	$path = $native . $relative;
	if ( ! is_file( $path ) || is_link( $path ) || hash_file( 'sha256', $path ) !== $digest ) { throw new RuntimeException( 'Pinned retained native class required.' ); }
	require_once $path;
}
function add_action( ...$unused ) {}
function add_filter( ...$unused ) {}
function do_action( ...$unused ) {}
function wp_create_nonce( $unused ) { return 'synthetic-offline'; }
function get_current_user_id() { return 0; }
function is_wp_error( $value ) { return $value instanceof WP_Error; }
function rest_ensure_response( $value ) { return $value; }
class WP_REST_Response {
	public $headers = array();
	public function header( $key, $value ) { $this->headers[ $key ] = $value; }
}
class WP_REST_Request {}
$wp_error = $native . '../../../wp-includes/class-wp-error.php';
$wp_error_sha = 'a9e971548bf6a1d93c821f980f530efba985c25d5d0b13d9b63e63b378a81a94';
if ( hash_file( 'sha256', $wp_error ) !== $wp_error_sha ) { throw new RuntimeException( 'Pinned native WP_Error required.' ); }
require $wp_error;
class WC_Cart {
	public static $nested = false;
	public function get_cart_hash() {
		if ( self::$nested ) { self::$nested = false; $this->get_cart_hash(); }
		return skyyrose2_simple_size_guard_api_draft( 'synthetic-hash' );
	}
}
class WC_Cart_Session {
	public static function are_updates_enabled_for_cart( $cart ) { return true; }
}
class WC_Order {
	public static $reads = 0;
	public function __construct( $id ) { ++self::$reads; throw new Exception( 'Illustrative saved-history refusal' ); }
}
$fixture = new class() {
	public $cart;
	public $session;
	public function __construct() {
		$this->cart = new WC_Cart();
		$this->session = new class() { public function get( $key, $default = null ) { return 1; } };
	}
	public function is_store_api_request() { return true; }
};
function WC() { return $GLOBALS['fixture']; }
require __DIR__ . '/../../wordpress-theme/skyyrose-flagship-2/inc/simple-product-sizes.php';
class SS_Native_Header_Control extends Automattic\WooCommerce\StoreApi\Routes\V1\AbstractCartRoute {
	public function __construct() {}
	public function get_path() { return '/synthetic-offline'; }
	public function get_args() { return array(); }
	protected function get_cart_token() { return 'synthetic-token'; }
	public function format() { return $this->add_response_headers( new WP_REST_Response() ); }
}
class SS_Override_Header_Control extends SS_Native_Header_Control {
	protected function add_response_headers( WP_REST_Response $response ) { WC()->cart->get_cart_hash(); return $response; }
}
function ss_expect( $value, $message ) { if ( ! $value ) { throw new RuntimeException( $message ); } }
$route = new SS_Native_Header_Control();
foreach ( array( 'before', 'after' ) as $phase ) {
	$before = WC_Order::$reads;
	$response = $route->format();
	ss_expect( 'synthetic-hash' === $response->headers['Cart-Hash'] && WC_Order::$reads === $before, 'Native formatting must only read unchanged hash.' );
	for ( $repeat = 0; $repeat < 2; ++$repeat ) {
		$refused = false;
		try { WC()->cart->get_cart_hash(); } catch ( Automattic\WooCommerce\StoreApi\Exceptions\RouteException $error ) {
			$refused = 'skyyrose_simple_size_saved_order' === $error->getErrorCode() && 409 === $error->getCode();
		}
		ss_expect( $refused, 'Every repeated functional call must still refuse.' );
	}
}
$refused = false;
try { ( new SS_Override_Header_Control() )->format(); } catch ( Automattic\WooCommerce\StoreApi\Exceptions\RouteException $error ) { $refused = true; }
ss_expect( $refused, 'A same-name override outside native source must not inherit the exemption.' );
$refused = false;
WC_Cart::$nested = true;
try { $route->format(); } catch ( Automattic\WooCommerce\StoreApi\Exceptions\RouteException $error ) { $refused = true; }
ss_expect( $refused, 'An outer header frame must not exempt a nested functional hash.' );

class SS_Route_Boundary_Control extends SS_Native_Header_Control {
	public $calls = 0;
	public $outcome;
	public $request;
	protected function load_cart_session( WP_REST_Request $request ) { ++$this->calls; $this->request = $request; }
	protected function requires_nonce( WP_REST_Request $request ) { return false; }
	protected function is_update_request( WP_REST_Request $request ) { return true; }
	protected function get_response_by_request_method( WP_REST_Request $request ) { return $this->outcome instanceof Throwable ? new WP_REST_Response() : $this->outcome; }
	protected function cart_updated( WP_REST_Request $request ) { if ( $this->outcome instanceof Throwable ) { throw $this->outcome; } }
}
class SS_Third_Party_Route_Control extends SS_Route_Boundary_Control {
	public function get_response( WP_REST_Request $request ) { throw new RuntimeException( 'Third-party override remains original' ); }
}
$controller = new SS_Route_Boundary_Control();
$permission_calls = 0;
$permission = static function() use ( &$permission_calls ) { ++$permission_calls; return false; };
$handler = array( 'callback' => array( $controller, 'get_response' ), 'permission_callback' => $permission, 'methods' => array( 'GET' => true ), 'args' => array( 'quantity' => array( 'type' => 'integer' ) ) );
$endpoints = array( '/wc/store/v1/checkout' => array( $handler ), '/wc/store/v1/cart/add-item' => array( $handler ), '/wc/store/v1/checkout-extra' => array( $handler ), '/unrelated/cart' => array( $handler ) );
$override = $handler; $override['callback'] = array( new SS_Third_Party_Route_Control(), 'get_response' );
$endpoints['/wc/store/v1/cart/third-party-control'] = array( $override );
$wrapped = skyyrose2_simple_size_store_route_boundary( $endpoints );
foreach ( array( '/wc/store/v1/checkout', '/wc/store/v1/cart/add-item' ) as $path ) {
	$expected = $handler; $expected['callback'] = $wrapped[ $path ][0]['callback'];
	ss_expect( $wrapped[ $path ][0] === $expected, 'Permission/method/argument metadata must be unchanged.' );
}
ss_expect( $wrapped['/unrelated/cart'] === $endpoints['/unrelated/cart'] && $wrapped['/wc/store/v1/checkout-extra'] === $endpoints['/wc/store/v1/checkout-extra'], 'Unrelated endpoints must remain byte-for-value unchanged.' );
ss_expect( $wrapped['/wc/store/v1/cart/third-party-control'] === $endpoints['/wc/store/v1/cart/third-party-control'], 'A third-party get_response override must remain original.' );
ss_expect( skyyrose2_simple_size_store_route_boundary( $wrapped ) === $wrapped, 'Already wrapped endpoints must not acquire another wrapper.' );
$callback = $wrapped['/wc/store/v1/checkout'][0]['callback'];
$request = new WP_REST_Request();
$normal = new WP_REST_Response(); $controller->outcome = $normal;
ss_expect( $callback( $request ) === $normal && 1 === $controller->calls && $controller->request === $request, 'Return the exact native response after one invocation.' );
$controller->outcome = new Automattic\WooCommerce\StoreApi\Exceptions\RouteException( 'skyyrose_simple_size_saved_order', 'Illustrative refusal', 409 );
$refusal = $callback( $request );
ss_expect( $refusal instanceof WP_Error && 'skyyrose_simple_size_saved_order' === $refusal->get_error_code() && array( 'status' => 409 ) === $refusal->get_error_data() && 2 === $controller->calls, 'Only the exact saved-history409 becomes a native WP_Error.' );
foreach ( array( new Automattic\WooCommerce\StoreApi\Exceptions\RouteException( 'other', 'Other', 409 ), new Automattic\WooCommerce\StoreApi\Exceptions\RouteException( 'skyyrose_simple_size_saved_order', 'Wrong status', 400 ), new RuntimeException( 'Unrelated failure' ) ) as $error ) {
	$before = $controller->calls; $controller->outcome = $error; $same = false;
	try { $callback( $request ); } catch ( Throwable $caught ) { $same = $caught === $error; }
	ss_expect( $same && $before + 1 === $controller->calls, 'Other exceptions must be rethrown unchanged without retry.' );
}
ss_expect( 0 === $permission_calls, 'The wrapper must not execute or bypass dispatch permission checks.' );
foreach ( $pins as $relative => $digest ) { ss_expect( hash_file( 'sha256', $native . $relative ) === $digest, 'Native source preservation failed.' ); }
ss_expect( hash_file( 'sha256', $wp_error ) === $wp_error_sha, 'Native WP_Error source preservation failed.' );
echo json_encode( array( 'status' => 'PASS_OFFLINE_NATIVE_HEADER_METHOD_AND_ROUTE_BOUNDARY_WITH_ILLUSTRATIVE_STUBS', 'authentication' => 'NOT_APPLICABLE_OFFLINE', 'source_pins' => $pins, 'wp_error_sha256' => $wp_error_sha, 'functional_refusals' => 4, 'override_refusal' => true, 'nested_functional_refusal' => true, 'callback_invocations' => $controller->calls, 'permission_callback_invocations' => $permission_calls, 'limits' => 'No actual REST/JSON409, native DB/order mutation, real authentication or installed-stack execution; fresh native qualification remains open.' ), JSON_THROW_ON_ERROR | JSON_PRETTY_PRINT ) . "\n";
