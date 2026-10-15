<?php
/**
 * Local V2 template renderer.
 *
 * Preview-only: loads the actual V2 PHP route templates and theme assets without
 * WordPress or staging. WooCommerce records below are visual fixtures only; live
 * price, stock, variation, cart, payment, and journal data remain WordPress-owned.
 */
declare(strict_types=1);

$repo_dir  = realpath( __DIR__ . '/..' );
$theme_dir = realpath( __DIR__ . '/../wordpress-theme/skyyrose-flagship-2' );

/**
 * This renderer is deliberately narrower than WordPress. It is a local review
 * surface for one explicit V2 theme candidate, not a compatibility layer for
 * any old SkyyRose theme or an approximation of WooCommerce.
 *
 * @param int    $status HTTP response status.
 * @param string $title Short diagnostic title.
 * @param string $detail Human-readable local-review diagnostic.
 * @return never
 */
function sr2_preview_fail_closed( $status, $title, $detail ) {
	http_response_code( (int) $status );
	header( 'Content-Type: text/html; charset=UTF-8' );
	echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex"><title>' . htmlspecialchars( (string) $title, ENT_QUOTES, 'UTF-8' ) . '</title><style>body{margin:0;background:#100e0c;color:#f4eee8;font:16px/1.55 Georgia,serif}main{max-width:46rem;margin:12vh auto;padding:2rem;border:1px solid #8d6e43}p{max-width:65ch;color:#d8cec2}code{font:600 .82rem/1.5 ui-monospace,SFMono-Regular,monospace;color:#efc777}</style></head><body><main><p>LOCAL V2 TEMPLATE PREVIEW</p><h1>' . htmlspecialchars( (string) $title, ENT_QUOTES, 'UTF-8' ) . '</h1><p>' . htmlspecialchars( (string) $detail, ENT_QUOTES, 'UTF-8' ) . '</p></main></body></html>';
	exit;
}

/** @return array<string,mixed> */
function sr2_preview_read_json( $path ) {
	if ( ! is_readable( $path ) ) {
		return array();
	}
	$decoded = json_decode( (string) file_get_contents( $path ), true ); // phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents
	return is_array( $decoded ) ? $decoded : array();
}

/** @return string */
function sr2_preview_current_commit( $repo_dir ) {
	if ( ! function_exists( 'shell_exec' ) || ! $repo_dir ) {
		return '';
	}
	$commit = trim( (string) shell_exec( 'git -C ' . escapeshellarg( $repo_dir ) . ' rev-parse --verify HEAD 2>/dev/null' ) ); // phpcs:ignore WordPress.PHP.DiscouragedPHPFunctions.system_calls_shell_exec
	return preg_match( '/^[a-f0-9]{40}$/', $commit ) ? $commit : '';
}

/** @return array<string,string> */
function sr2_preview_theme_metadata( $theme_dir ) {
	$style = is_readable( $theme_dir . '/style.css' ) ? (string) file_get_contents( $theme_dir . '/style.css' ) : ''; // phpcs:ignore WordPress.WP.AlternativeFunctions.file_get_contents_file_get_contents
	preg_match( '/^Theme Name:\s*(.+)$/mi', $style, $name );
	preg_match( '/^Version:\s*(.+)$/mi', $style, $version );
	return array(
		'name'    => isset( $name[1] ) ? trim( $name[1] ) : '',
		'version' => isset( $version[1] ) ? trim( $version[1] ) : '',
	);
}

if ( ! $repo_dir || ! $theme_dir ) {
	sr2_preview_fail_closed( 500, 'V2 source unavailable', 'The local V2 source directory is missing. This preview will not substitute another theme.' );
}

$preview_handoff = sr2_preview_read_json( $repo_dir . '/.fashion-theme/codex-desktop-handoff.json' );
$preview_theme   = sr2_preview_theme_metadata( $theme_dir );
$preview_commit  = sr2_preview_current_commit( $repo_dir );
$preview_candidate = isset( $preview_handoff['candidate'] ) && is_array( $preview_handoff['candidate'] ) ? $preview_handoff['candidate'] : array();

if ( 'SkyyRose Flagship 2' !== ( $preview_theme['name'] ?? '' ) || empty( $preview_theme['version'] ) || empty( $preview_commit ) || empty( $preview_candidate['candidate_id'] ) || empty( $preview_candidate['branch'] ) ) {
	sr2_preview_fail_closed( 503, 'V2 candidate identity cannot be proven', 'The local renderer could not bind this request to the SkyyRose Flagship 2 source and its V2 handoff record. No legacy theme fallback is available.' );
}

$preview_identity = array(
	'candidate_id' => (string) $preview_candidate['candidate_id'],
	'branch'       => (string) $preview_candidate['branch'],
	'commit'       => $preview_commit,
	'theme'        => $preview_theme['name'] . ' ' . $preview_theme['version'],
);

define( 'ABSPATH', __DIR__ . '/' );
define( 'OBJECT', 'OBJECT' );
$requested_route = preg_replace( '/[^a-z0-9-]/i', '', $_GET['route'] ?? 'home' ) ?: 'home';
$route = $requested_route;
if ( 'preorder' === $route ) {
	header( 'Location: /tools/v2-theme-preview.php?route=pre-order', true, 308 );
	exit;
}
$preview_state = preg_replace( '/[^a-z-]/', '', $_GET['state'] ?? '' );
$preview_sku = strtolower( preg_replace( '/[^a-z0-9-]/i', '', $_GET['sku'] ?? 'sg-005' ) ) ?: 'sg-005';
// `skyy=1` renders the Skyy walk-on dock with its source runtime (mascot.css, loader, 3D config, a minimal guide).
$preview_skyy = '1' === ( $_GET['skyy'] ?? '' );
$preview_routes = array( 'home', 'collections', 'signature', 'black-rose', 'love-hurts', 'kids-capsule', 'immersive-signature', 'immersive-black-rose', 'immersive-love-hurts', 'immersive-kids-capsule', 'pre-order', 'about', 'contact', 'journal', 'wishlist', 'lookbook', 'faq', 'shipping-returns', 'returns-exchanges', 'size-guide', 'privacy-policy', 'terms-of-service', 'accessibility', 'cart', 'checkout', 'account', 'order-tracking', 'shop', 'product', '404' );
$preview_template_map = array(
	'home'                  => 'front-page.php',
	'collections'           => 'page.php',
	'signature'             => 'template-collection.php',
	'black-rose'            => 'template-collection.php',
	'love-hurts'            => 'template-collection.php',
	'kids-capsule'          => 'template-collection.php',
	'immersive-signature'   => 'template-immersive-signature.php',
	'immersive-black-rose'  => 'template-immersive-black-rose.php',
	'immersive-love-hurts'  => 'template-immersive-love-hurts.php',
	'immersive-kids-capsule'=> 'template-immersive-kids-capsule.php',
	'pre-order'             => 'page.php',
	'about'                 => 'page.php',
	'contact'               => 'page.php',
	'journal'               => 'index.php',
	'wishlist'              => 'page-wishlist.php',
	'lookbook'              => 'page-lookbook.php',
	'faq'                   => 'page.php',
	'shipping-returns'      => 'page.php',
	'returns-exchanges'     => 'page.php',
	'size-guide'            => 'page.php',
	'privacy-policy'        => 'page.php',
	'terms-of-service'      => 'page.php',
	'accessibility'         => 'page.php',
	'cart'                  => 'template-parts/v2-commerce-preview.php',
	'checkout'              => 'template-parts/v2-commerce-preview.php',
	'account'               => 'template-parts/v2-commerce-preview.php',
	'order-tracking'        => 'template-parts/v2-commerce-preview.php',
	'shop'                  => 'woocommerce/archive-product.php',
	'product'               => 'woocommerce/single-product.php',
	'404'                   => '404.php',
);
if ( ! in_array( $route, $preview_routes, true ) || ! isset( $preview_template_map[ $route ] ) ) {
	sr2_preview_fail_closed( 404, 'Unknown V2 preview route', sprintf( '“%s” is not a published V2 review route. The renderer does not redirect unknown URLs to the home page.', $requested_route ) );
}
if ( ! is_file( $theme_dir . '/' . $preview_template_map[ $route ] ) ) {
	sr2_preview_fail_closed( 503, 'Canonical V2 template missing', sprintf( 'The route “%s” is mapped to a current V2 template that is not present. The renderer will not load a legacy substitute.', $route ) );
}
$preview_posts = array();
$preview_cursor = 0;
$preview_loop = 0;

function __( $text ) { return $text; }
function esc_html__( $text ) { return htmlspecialchars( $text, ENT_QUOTES, 'UTF-8' ); }
function esc_attr__( $text ) { return htmlspecialchars( $text, ENT_QUOTES, 'UTF-8' ); }
function esc_html_e( $text ) { echo esc_html( $text ); }
function esc_attr_e( $text ) { echo esc_attr( $text ); }
function esc_html( $value ) { return htmlspecialchars( (string) $value, ENT_QUOTES, 'UTF-8' ); }
function esc_attr( $value ) { return htmlspecialchars( (string) $value, ENT_QUOTES, 'UTF-8' ); }
function esc_url( $value ) { return htmlspecialchars( (string) $value, ENT_QUOTES, 'UTF-8' ); }
function wp_kses_post( $value ) { return $value; }
function wp_strip_all_tags( $value ) { return trim( strip_tags( (string) $value ) ); }
function wp_trim_words( $text, $num_words = 55, $more = null ) {
	$words = preg_split( '/\s+/', trim( wp_strip_all_tags( $text ) ) );
	if ( count( $words ) <= (int) $num_words ) {
		return implode( ' ', $words );
	}
	return implode( ' ', array_slice( $words, 0, (int) $num_words ) ) . ( null === $more ? ' …' : $more );
}
function sanitize_title( $value ) { return strtolower( preg_replace( '/[^a-z0-9]+/', '-', trim( (string) $value ) ) ); }
function sanitize_key( $value ) { return sanitize_title( $value ); }
function sanitize_html_class( $value ) { return sanitize_title( $value ); }
function sanitize_email( $value ) { return filter_var( (string) $value, FILTER_SANITIZE_EMAIL ); }
function is_email( $value ) { return false !== filter_var( (string) $value, FILTER_VALIDATE_EMAIL ); }
function absint( $value ) { return abs( (int) $value ); }
function add_action() {}
function add_filter() {}
function has_nav_menu() { return false; }
function wp_enqueue_style() {}
function wp_enqueue_script() {}
function wp_generate_uuid4() { return 'preview-00000000-0000-4000-8000-000000000000'; }
function wp_json_encode( $value, $flags = 0 ) { return json_encode( $value, $flags ); }
function do_action( $hook ) {
	global $product, $preview_sku;
	if ( 'woocommerce_before_single_product_summary' === $hook && $product instanceof WC_Product ) {
		// The template removes woocommerce_show_product_images when no verified media exists; mirror that.
		if ( empty( $GLOBALS['skyyrose2_pdp_media_context']['media']['ids'] ) ) {
			return;
		}
		$main_id = $product->get_image_id();
		echo '<div class="woocommerce-product-gallery sr2-preview-gallery">';
		// Woo's wc_get_gallery_image_html() wraps the image in a link; the theme's gallery CSS targets that shape.
		echo '<figure class="woocommerce-product-gallery__wrapper"><div class="woocommerce-product-gallery__image"><a href="' . esc_url( wp_get_attachment_url( $main_id ) ) . '">' . wp_get_attachment_image( $main_id, 'full', false, array( 'class' => 'wp-post-image', 'fetchpriority' => 'high' ) ) . '</a></div></figure>';
		echo '<div class="sr2-preview-gallery__thumbs">';
		foreach ( $product->get_gallery_image_ids() as $gallery_id ) {
			echo wp_get_attachment_image( $gallery_id, 'thumbnail', false, array( 'class' => 'sr2-preview-gallery__thumb' ) );
		}
		echo '</div></div>';
	} elseif ( 'woocommerce_single_product_summary' === $hook && $product instanceof WC_Product ) {
		echo '<h1 class="product_title entry-title">' . esc_html( $product->get_name() ) . '</h1>';
		echo '<p class="price">' . wp_kses_post( $product->get_price_html() ) . '</p>';
		echo '<div class="woocommerce-product-details__short-description"><p>' . esc_html( $product->get_short_description() ) . '</p></div>';
		echo wp_kses_post( wc_get_stock_html( $product ) );
		echo '<form class="cart variations_form"><table class="variations"><tbody><tr><th><label for="preview-size">Size</label></th><td><select id="preview-size"><option>Choose a size</option><option>XS</option><option>S</option><option>M</option><option>L</option><option>XL</option><option>2XL</option></select></td></tr></tbody></table><div class="quantity"><label for="preview-qty">Quantity</label><input id="preview-qty" type="number" min="1" value="1"></div><button class="single_add_to_cart_button button alt" type="button">Secure this piece</button></form>';
		$collection_labels = array( 'signature' => 'Signature', 'black-rose' => 'Black Rose', 'love-hurts' => 'Love Hurts', 'kids-capsule' => 'Kids Capsule', 'jersey-series' => 'Jersey Series / Black Rose release' );
		$collection_terms  = wp_get_post_terms( $product->get_id(), 'product_cat', array( 'fields' => 'slugs' ) );
		$collection_slug   = $collection_terms[0] ?? 'signature';
		$collection_label   = $collection_labels[ $collection_slug ] ?? 'SkyyRose';
		echo '<div class="product_meta"><span class="sku_wrapper">SKU: <span class="sku">' . esc_html( strtoupper( $product->get_sku() ) ) . '</span></span><span class="posted_in">Collection: ' . esc_html( $collection_label ) . '</span></div>';
		echo '<ul class="sr2-preview-promises"><li>Limited archive release</li><li>Tracked delivery</li><li>Secure checkout</li></ul>';
	} elseif ( 'woocommerce_before_shop_loop' === $hook ) {
		global $preview_posts;
		echo '<p class="woocommerce-result-count" role="alert" aria-relevant="all">' . esc_html( sprintf( 'Showing all %d results', count( $preview_posts ) ) ) . '</p>';
		skyyrose2_shop_ordering();
	} elseif ( 'woocommerce_after_single_product_summary' === $hook ) {
		// Native tab markup (woocommerce_output_product_data_tabs) with fixture copy only.
		echo '<div class="woocommerce-tabs wc-tabs-wrapper"><ul class="tabs wc-tabs" role="tablist"><li class="description_tab active" role="presentation"><a href="#tab-description" role="tab">Description</a></li><li class="additional_information_tab" role="presentation"><a href="#tab-additional_information" role="tab">Additional information</a></li></ul>';
		echo '<div class="woocommerce-Tabs-panel woocommerce-Tabs-panel--description panel entry-content wc-tab" id="tab-description" role="tabpanel"><h2>Description</h2><p>Published construction, care, fit, shipping, and return details remain attached to the live WooCommerce product record.</p></div>';
		echo '<div class="woocommerce-Tabs-panel woocommerce-Tabs-panel--additional_information panel entry-content wc-tab" id="tab-additional_information" role="tabpanel" hidden><h2>Additional information</h2><table class="woocommerce-product-attributes shop_attributes"><tr><th>Fit</th><td>Size guidance and model measurements are published on the live product record.</td></tr><tr><th>Delivery</th><td>Real fulfillment status and preorder timing come from WooCommerce; never fabricated here.</td></tr></table></div></div>';
		// Related loop: the same native card, other fixture products with verified media, like woocommerce_output_related_products.
		$related = array_values( array_filter( wc_get_products(), static function ( $candidate ) use ( $product ) { return $candidate->get_id() !== $product->get_id() && preview_product_has_fixture_media( $candidate ); } ) );
		$related = array_slice( $related, 0, 4 );
		if ( $related ) {
			$previous_product = $product;
			echo '<section class="related products"><h2>More from the house</h2><ul class="products columns-4">';
			foreach ( $related as $related_product ) {
				$product = $related_product;
				wc_get_template_part( 'content', 'product' );
			}
			$product = $previous_product;
			echo '</ul></section>';
		}
	}
}
function apply_filters( $hook, $value = null ) { return func_num_args() > 1 ? $value : $hook; }
function is_wp_error() { return false; }
function get_template_directory() { global $theme_dir; return $theme_dir; }
function get_template_directory_uri() { return '/wordpress-theme/skyyrose-flagship-2'; }
function get_theme_file_uri( $path = '' ) { return get_template_directory_uri() . '/' . ltrim( $path, '/' ); }
function home_url( $path = '/' ) {
	$path = trim( $path, '/' );
	$routes = array(
		'collections/signature' => 'signature',
		'collections/black-rose' => 'black-rose',
		'collections/love-hurts' => 'love-hurts',
		'collections/kids-capsule' => 'kids-capsule',
		'worlds/signature' => 'immersive-signature',
		'worlds/black-rose' => 'immersive-black-rose',
		'worlds/love-hurts' => 'immersive-love-hurts',
		'worlds/kids-capsule' => 'immersive-kids-capsule',
	);
	return '/tools/v2-theme-preview.php?route=' . rawurlencode( $routes[ $path ] ?? ( $path ?: 'home' ) );
}
function add_query_arg( $args, $url = '' ) { return $url; }
function wp_verify_nonce() { return true; }
function wp_safe_redirect() { return true; }
function wp_get_referer() { return '/tools/v2-theme-preview.php?route=contact'; }
function wp_mail() { return true; }
function wp_die( $message ) { throw new RuntimeException( (string) $message ); }
function wp_generate_password( $length = 12 ) { return str_repeat( 'p', (int) $length ); }
function set_transient() { return true; }
function get_transient() { return false; }
function delete_transient() { return true; }
function wp_salt() { return 'preview-only-salt'; }
function sanitize_text_field( $value ) { return trim( strip_tags( (string) $value ) ); }
function sanitize_textarea_field( $value ) { return trim( strip_tags( (string) $value ) ); }
function wp_unslash( $value ) { return $value; }
function language_attributes() { echo 'lang="en-US"'; }
function bloginfo( $field ) { echo 'charset' === $field ? 'UTF-8' : 'SkyyRose'; }
function get_bloginfo( $field = '' ) { return 'name' === $field ? 'SkyyRose' : ''; }
function is_home() { global $route; return 'journal' === $route; }
function wp_get_document_title() { return get_the_title(); }
function body_class() {
	global $route, $preview_identity;
	echo 'class="sr2-preview woocommerce" data-preview-route="' . esc_attr( $route ) . '" data-preview-theme="' . esc_attr( $preview_identity['theme'] ) . '" data-preview-candidate="' . esc_attr( $preview_identity['candidate_id'] ) . '" data-preview-commit="' . esc_attr( $preview_identity['commit'] ) . '"';
}
function wp_body_open() {
	global $route, $preview_identity, $preview_template_map;
	echo '<aside class="sr2-preview-banner" aria-label="Local preview identity"><strong>LOCAL V2 REVIEW</strong><span>' . esc_html( $preview_identity['theme'] ) . ' · ' . esc_html( substr( $preview_identity['commit'], 0, 12 ) ) . '</span><span>route: ' . esc_html( $route ) . ' · template: ' . esc_html( $preview_template_map[ $route ] ) . '</span><span>fixture-only · no staging writes</span></aside>';
}
function wp_head() {
	global $route, $preview_identity, $preview_template_map;
	$title       = 'home' === $route ? 'SkyyRose — House of Roses' : 'SkyyRose — ' . ucwords( str_replace( '-', ' ', $route ) );
	$description = 'SkyyRose is an Oakland luxury streetwear house where every collection opens a distinct story world.';
	$immersive_css = 0 === strpos( $route, 'immersive-' ) ? '<link rel="stylesheet" href="/wordpress-theme/skyyrose-flagship-2/assets/css/immersive.css">' : '';
	// skyy=1: source mascot.css; the preview banner moves bottom-left so the dock at bottom-right stays visible in captures.
	$skyy_css = ! empty( $GLOBALS['preview_skyy'] ) && ! is_checkout() ? '<link rel="stylesheet" href="/wordpress-theme/skyyrose-flagship-2/assets/css/mascot.css"><style>.sr2-preview-banner{right:auto;left:12px;text-align:left}@media(max-width:640px){.sr2-preview-banner{right:auto;left:8px;max-width:32%}}</style>' : '';
	// Source sheets in the skyyrose2_assets() enqueue order so every route renders its real cascade:
	// theme → page sheets → controls, global-shell → visual-recovery → scene sheets → search-preview → premium-commerce → quick-view-commerce.
	$collection_routes = array( 'signature', 'black-rose', 'love-hurts', 'kids-capsule' );
	$page_sheets       = array();
	if ( 'about' === $route ) { $page_sheets[] = 'about-archive'; }
	// page-lookbook.php enqueues its own sheets in this order (collection-world, premium-commerce, hero-commerce-scenes, collection-scene-motion, lookbook).
	if ( 'lookbook' === $route ) { array_push( $page_sheets, 'collection-world', 'lookbook' ); }
	if ( ! in_array( $route, array_merge( array( 'home', 'shop', 'product', 'cart', 'checkout' ), $collection_routes ), true ) && 0 !== strpos( $route, 'immersive-' ) ) { array_push( $page_sheets, 'legacy-world-components', 'content-page' ); }
	if ( 'home' === $route ) { array_push( $page_sheets, 'collection-world', 'home-page' ); }
	if ( 'product' === $route ) { $page_sheets[] = 'product-page'; }
	if ( 'shop' === $route ) { $page_sheets[] = 'shop-page'; }
	if ( in_array( $route, $collection_routes, true ) ) { $page_sheets[] = 'collection-world'; }
	$route_sheets = array_merge( $page_sheets, array( 'controls', 'global-shell', 'visual-recovery' ) );
	if ( 'home' === $route || 'lookbook' === $route || in_array( $route, $collection_routes, true ) ) { array_push( $route_sheets, 'hero-commerce-scenes', 'collection-scene-motion' ); }
	if ( in_array( $route, array( 'signature', 'black-rose', 'love-hurts' ), true ) ) { $route_sheets[] = 'scene-handoff'; }
	if ( 'checkout' !== $route ) { array_push( $route_sheets, 'search-preview', 'premium-commerce' ); }
	if ( ! in_array( $route, array( 'cart', 'checkout', 'account' ), true ) ) { $route_sheets[] = 'quick-view-commerce'; }
	$route_css = '';
	foreach ( $route_sheets as $sheet ) { $route_css .= '<link rel="stylesheet" href="/wordpress-theme/skyyrose-flagship-2/assets/css/' . $sheet . '.css">'; }
	header( 'X-SkyyRose-Preview-Theme: ' . $preview_identity['theme'] );
	header( 'X-SkyyRose-Preview-Candidate: ' . $preview_identity['candidate_id'] );
	header( 'X-SkyyRose-Preview-Commit: ' . $preview_identity['commit'] );
	header( 'X-SkyyRose-Preview-Route: ' . $route );
	header( 'X-SkyyRose-Preview-Template: ' . $preview_template_map[ $route ] );
	echo '<title>' . esc_html( $title ) . '</title><meta name="description" content="' . esc_attr( $description ) . '"><meta name="robots" content="noindex,nofollow"><meta name="skyyrose-preview-theme" content="' . esc_attr( $preview_identity['theme'] ) . '"><meta name="skyyrose-preview-candidate" content="' . esc_attr( $preview_identity['candidate_id'] ) . '"><meta name="skyyrose-preview-commit" content="' . esc_attr( $preview_identity['commit'] ) . '"><meta name="skyyrose-preview-route" content="' . esc_attr( $route ) . '"><meta name="skyyrose-preview-template" content="' . esc_attr( $preview_template_map[ $route ] ) . '"><link rel="stylesheet" href="/wordpress-theme/skyyrose-flagship-2/assets/css/design-tokens.css"><link rel="stylesheet" href="/wordpress-theme/skyyrose-flagship-2/assets/css/theme.css">' . $route_css . $immersive_css . '<style>.sr2-preview-banner{position:fixed;z-index:1000;right:12px;bottom:12px;display:grid;gap:3px;padding:8px 10px;background:#e2b6a7;color:#100e0c;font:600 10px/1.2 sans-serif;letter-spacing:.06em;text-align:right;box-shadow:0 4px 16px rgba(0,0,0,.25)}.sr2-preview-banner strong{font-size:11px}.sr2-preview-gallery img{display:block;width:100%;height:auto}.sr2-preview-gallery__thumbs{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:8px}.sr2-preview-gallery__thumb{border:1px solid var(--sr2-line);aspect-ratio:1;object-fit:cover}.sr2-pdp-product--portal .quantity{display:grid;gap:4px;flex:0 0 7rem}.sr2-pdp-product--portal .quantity input{width:100%;min-height:48px}.sr2-pdp-product--portal .product_meta{display:grid;gap:6px;margin-top:24px;color:var(--sr2-muted);font:600 .7rem/1.4 var(--sr2-font-ui);letter-spacing:.08em;text-transform:uppercase}.sr2-preview-promises{display:grid;gap:7px;margin-top:24px;padding-left:1.2rem}.sr2-preview-tabs__grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px;margin-top:32px}@media(max-width:640px){.sr2-preview-banner{right:8px;left:8px;text-align:left}.sr2-preview-tabs__grid{grid-template-columns:1fr}}</style>' . $skyy_css;
}
/** Source Skyy runtime for the `skyy=1` preview flag: loader config, tiered GLB config and a minimal deterministic guide. */
function sr2_preview_skyy_footer() {
	if ( empty( $GLOBALS['preview_skyy'] ) || is_checkout() ) {
		return '';
	}
	$base   = '/wordpress-theme/skyyrose-flagship-2';
	$loader = array( 'mascotUrl' => $base . '/assets/js/mascot.js', 'skyy3dUrl' => $base . '/assets/js/skyy-3d.js' );
	$three  = array(
		'modelUrl'       => $base . '/assets/models/skyy-natural-desktop.glb',
		'mobileModelUrl' => $base . '/assets/models/skyy-natural-mobile.glb',
		'decoderPath'    => $base . '/assets/js/lib/draco/',
		'moduleBase'     => $base . '/assets/js/lib/three-r170/',
	);
	$guide  = array(
		'greeting' => 'Welcome to SkyyRose. I’m Skyy, your digital house guide. I can help you explore a collection or find a piece by name or SKU.',
		'pages'    => array(
			'shop'    => array( 'label' => 'Shop the house', 'url' => '/tools/v2-theme-preview.php?route=shop' ),
			'contact' => array( 'label' => 'Contact the house', 'url' => '/tools/v2-theme-preview.php?route=contact' ),
		),
		'products' => array(),
		'intents'  => array(
			array( 'id' => 'collections', 'label' => 'Explore the collections', 'patterns' => array( 'collections', 'collection' ), 'answer' => 'Signature, Black Rose, Love Hurts and the Kids Capsule each open their own world.', 'link' => '/tools/v2-theme-preview.php?route=collections' ),
			array( 'id' => 'shipping', 'label' => 'Shipping and returns', 'patterns' => array( 'shipping', 'returns' ), 'answer' => 'Read the current shipping and returns guidance.', 'link' => '/tools/v2-theme-preview.php?route=shipping-returns' ),
		),
	);
	$flags = JSON_UNESCAPED_SLASHES | JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT;
	return '<script>window.SKYY_LOADER_CONFIG = ' . json_encode( $loader, $flags ) . ';window.SKYY_3D_CONFIG = ' . json_encode( $three, $flags ) . ';window.SKYY_GUIDE_DATA = ' . json_encode( $guide, $flags ) . ';</script><script src="' . $base . '/assets/js/mascot-loader.js" defer></script>';
}
function wp_footer() {
	global $route;
	$immersive_js = 0 === strpos( $route, 'immersive-' ) ? '<script src="/wordpress-theme/skyyrose-flagship-2/assets/js/immersive.js" defer></script>' : '';
	$commerce_js  = 'checkout' === $route ? '' : '<script src="/wordpress-theme/skyyrose-flagship-2/assets/js/premium-commerce.js" defer></script>';
	$commerce_js .= in_array( $route, array( 'cart', 'checkout', 'account' ), true ) ? '' : '<script src="/wordpress-theme/skyyrose-flagship-2/assets/js/quick-view-commerce.js" defer></script>';
	echo '<script src="/wordpress-theme/skyyrose-flagship-2/assets/js/theme.js" defer></script><script src="/wordpress-theme/skyyrose-flagship-2/assets/js/house-of-roses-motion.js" defer></script><script src="/wordpress-theme/skyyrose-flagship-2/assets/js/kids-capsule-reveal.js" defer></script>' . $commerce_js . $immersive_js . sr2_preview_skyy_footer();
}
function get_header() { require get_template_directory() . '/header.php'; }
function get_footer() { require get_template_directory() . '/footer.php'; }
function get_template_part( $slug, $name = null, $args = array() ) {
	if ( 'template-parts/skyy-mascot' === $slug && empty( $GLOBALS['preview_skyy'] ) ) { return; }
	$file = get_template_directory() . '/' . $slug . ( $name ? '-' . $name : '' ) . '.php';
	if ( is_file( $file ) ) { require $file; }
}
function get_queried_object_id() { return 1; }
function get_the_ID() {
	global $product;
	return $product instanceof WC_Product ? $product->get_id() : 1;
}
function the_ID() { echo esc_attr( get_the_ID() ); }
function get_post_field( $field ) { global $route; return 'post_name' === $field ? $route : ''; }
function get_the_title() { global $route; return ucwords( str_replace( '-', ' ', $route ) ); }
function the_title() { echo esc_html( get_the_title() ); }
function get_the_content() { return ''; }
function the_content() {
	global $route;
	$service_copy = array(
		'faq'              => 'Answers on fit, pre-order timing, order support, and the path to Client Services.',
		'shipping-returns' => 'In-stock and pre-order fulfillment guidance, tracking expectations, and return-request steps.',
		'returns-exchanges' => 'Start a request with Client Services before shipping anything back. Eligibility, item condition, and replacement availability are confirmed case by case.',
		'size-guide'       => 'Measure a piece you own flat, compare the published measurements, and contact Client Services between sizes.',
		'privacy-policy'   => 'The store uses order, support, security, and requested communication data according to the published policy.',
		'terms-of-service' => 'Orders remain subject to acceptance, payment confirmation, availability, and the merchant terms.',
		'accessibility'    => 'SkyyRose works toward a WCAG 2.2 AA shopping experience with keyboard, contrast, and reduced-motion support.',
	);
	if ( isset( $service_copy[ $route ] ) ) {
		echo '<p>' . esc_html( $service_copy[ $route ] ) . '</p><p>Live policy copy is supplied by the WordPress page record after import.</p>';
		return;
	}
	echo '<p>Preview route content is rendered from this V2 template. WordPress supplies the live page record after staging deployment.</p>';
}
function have_posts() { global $preview_posts, $preview_cursor; return $preview_cursor < count( $preview_posts ); }
function the_post() { global $preview_posts, $preview_cursor, $product; $product = $preview_posts[ $preview_cursor++ ]; }
function is_account_page() { return false; }
// Native WooCommerce/WordPress conditionals the shop and product templates call directly.
function is_shop() { global $route; return 'shop' === $route; }
// The dock and its runtime stay off checkout exactly as production gates them (template-parts/skyy-mascot.php, functions.php).
function is_checkout() { global $route; return 'checkout' === $route; }
function is_cart() { global $route; return 'cart' === $route; }
function is_product() { global $route; return 'product' === $route; }
function is_product_taxonomy() { return false; }
function is_product_category() { return false; }
function is_product_tag() { return false; }
function is_singular( $post_types = '' ) { global $route; return 'product' === $route; }
function is_main_query() { return true; }
function is_user_logged_in() { return false; }
function is_admin() { return false; }
function is_customize_preview() { return false; }
function has_block() { return false; }
function wp_print_inline_script_tag( $javascript, $attributes = array() ) {
	$attribute_markup = '';
	foreach ( $attributes as $name => $value ) { $attribute_markup .= ' ' . preg_replace( '/[^a-z0-9-]/', '', strtolower( (string) $name ) ) . '="' . esc_attr( (string) $value ) . '"'; }
	echo '<script' . $attribute_markup . '>' . $javascript . '</script>';
}
function is_front_page() { global $route; return 'home' === $route; }
function untrailingslashit( $value ) { return rtrim( (string) $value, '/' ); }
function map_deep( $value, $callback ) { return is_array( $value ) ? array_map( static fn( $item ) => map_deep( $item, $callback ), $value ) : $callback( $value ); }
function tag_escape( $value ) { return strtolower( preg_replace( '/[^a-zA-Z0-9_:]/', '', (string) $value ) ); }
function has_action() { return false; }
function remove_action() {}
function remove_filter() {}
function url_to_postid() { return 0; }
function get_queried_object() { return null; }
function get_woocommerce_currency() { return 'USD'; }
function wc_query_string_form_fields() {}
function selected( $selected, $current = true, $display = true ) {
	$result = (string) $selected === (string) $current ? ' selected="selected"' : '';
	if ( $display ) { echo $result; }
	return $result;
}
/** Visual fixture terms for the archive collection filter; live terms are WordPress-owned. */
function get_terms( $args = array() ) {
	$terms = array();
	foreach ( array( 'signature' => 'Signature', 'black-rose' => 'Black Rose', 'love-hurts' => 'Love Hurts', 'kids-capsule' => 'Kids Capsule' ) as $slug => $name ) {
		$terms[] = (object) array( 'slug' => $slug, 'name' => $name, 'taxonomy' => 'product_cat', 'count' => 1 );
	}
	return $terms;
}
function get_option( $name ) { return 'admin_email' === $name ? 'hello@skyyrose.com' : ''; }
function wp_nonce_field() { echo '<input type="hidden" value="preview">'; }
function get_page_by_path() { return null; }
function get_permalink( $item = null ) {
	if ( $item instanceof WC_Product ) {
		return '/tools/v2-theme-preview.php?route=product&sku=' . rawurlencode( $item->get_sku() );
	}
	return '/tools/v2-theme-preview.php?route=' . ( $item ? 'product' : 'shop' );
}
function wc_get_page_permalink( $page ) {
	$routes = array( 'shop' => 'shop', 'cart' => 'cart', 'checkout' => 'checkout', 'myaccount' => 'account', 'order-tracking' => 'order-tracking' );
	return '/tools/v2-theme-preview.php?route=' . ( $routes[ $page ] ?? 'home' );
}
function wc_get_cart_url() { return wc_get_page_permalink( 'cart' ); }
function wc_get_checkout_url() { return wc_get_page_permalink( 'checkout' ); }
function wc_get_product_category_list( $id ) { return 'SkyyRose · Collection'; }
function wp_get_post_terms( $product_id = 0, $taxonomy = '', $args = array() ) {
	global $route, $preview_product;
	$fixture_terms = array( 1 => 'signature', 2 => 'black-rose', 3 => 'love-hurts', 4 => 'kids-capsule', 5 => 'kids-capsule' );
	if ( isset( $fixture_terms[ (int) $product_id ] ) ) { return array( $fixture_terms[ (int) $product_id ] ); }
	if ( 'product' === $route && $preview_product instanceof WC_Product && $preview_product->get_id() === (int) $product_id ) {
		$sku = strtolower( $preview_product->get_sku() );
		$jersey_ids = array( 103, 108, 109, 110, 111, 112, 114, 115 );
		return in_array( (int) $product_id, $jersey_ids, true ) || str_starts_with( $sku, 'br-' ) ? array( 'black-rose' ) : ( str_starts_with( $sku, 'lh-' ) ? array( 'love-hurts' ) : ( str_starts_with( $sku, 'kids-' ) ? array( 'kids-capsule' ) : array( 'signature' ) ) );
	}
	return in_array( $route, array( 'signature', 'black-rose', 'love-hurts', 'kids-capsule' ), true ) ? array( $route ) : array();
}
function preview_attachment_path( $id ) {
	$images = array(
		1   => 'images/products/preview/sg-005-front.webp',
		2   => 'images/products/preview/br-004-front.webp',
		3   => 'images/products/preview/lh-004-front.webp',
		4   => 'images/products/preview/kids-001-front.webp',
		7   => 'images/products/preview/kids-002-front.webp',
		102 => 'images/products/preview/sg-005-packshot.webp',
		201 => 'images/products/preview/br-004-back.webp',
		202 => 'images/products/preview/br-004-packshot.webp',
		301 => 'images/products/preview/lh-004-back.webp',
		302 => 'images/products/preview/lh-004-packshot.webp',
		401 => 'images/products/preview/kids-001-back.webp',
		402 => 'images/products/preview/kids-001-packshot.webp',
		701 => 'images/products/preview/kids-002-back.webp',
		702 => 'images/products/preview/kids-002-packshot.webp',
	);
	return $images[ (int) $id ] ?? '';
}
function wp_get_attachment_image( $id, $size = 'thumbnail', $icon = false, $attrs = array() ) {
	$path = preview_attachment_path( $id );
	if ( ! $path ) {
		return '';
	}
	// Mirror core: width/height from the real file so the fixture measures the same layout stability as WordPress.
	$meta  = wp_get_attachment_metadata( $id );
	$attrs = array_merge( array( 'class' => '', 'alt' => 'SkyyRose published product view', 'decoding' => 'async' ), (array) $attrs );
	if ( ! empty( $meta['width'] ) && ! empty( $meta['height'] ) ) {
		$attrs['width']  = (string) $meta['width'];
		$attrs['height'] = (string) $meta['height'];
	}
	$html = '<img src="' . esc_url( get_template_directory_uri() . '/assets/sot/' . $path ) . '"';
	foreach ( $attrs as $name => $value ) {
		if ( '' !== (string) $value && preg_match( '/^[a-z-]+$/', (string) $name ) ) {
			$html .= ' ' . $name . '="' . esc_attr( (string) $value ) . '"';
		}
	}
	return $html . '>';
}
function wp_get_attachment_image_url( $id, $size = 'thumbnail' ) {
	$path = preview_attachment_path( $id );
	return $path ? get_template_directory_uri() . '/assets/sot/' . $path : '';
}
/** Real pixel dimensions of the local fixture file; missing files stay non-images. */
function wp_get_attachment_metadata( $id ) {
	global $theme_dir;
	$path = preview_attachment_path( $id );
	$size = $path ? getimagesize( $theme_dir . '/assets/sot/' . $path ) : false;
	return $size ? array( 'width' => (int) $size[0], 'height' => (int) $size[1] ) : array();
}
function wp_attachment_is_image( $id ) { return (bool) preview_attachment_path( $id ); }
function wp_get_attachment_url( $id ) {
	$path = preview_attachment_path( $id );
	return $path ? get_template_directory_uri() . '/assets/sot/' . $path : '';
}
function woocommerce_page_title() { return 'Shop'; }
function woocommerce_catalog_ordering( $args = array() ) {
	echo '<form class="woocommerce-ordering" method="get"><label class="orderby-label" for="woocommerce-orderby">Shop order</label><select name="orderby" class="orderby" id="woocommerce-orderby"><option value="menu_order" selected="selected">Default sorting</option><option value="popularity">Sort by popularity</option><option value="date">Sort by latest</option><option value="price">Sort by price: low to high</option><option value="price-desc">Sort by price: high to low</option></select><input type="hidden" name="paged" value="1"></form>';
}
function woocommerce_product_loop() { return true; }
function woocommerce_product_loop_start() { echo '<ul class="products">'; }
function woocommerce_product_loop_end() { echo '</ul>'; }
function wc_get_template_part() { require get_template_directory() . '/woocommerce/content-product.php'; }
function wc_product_class( $class = '', $product = null ) { global $preview_loop; $preview_loop = (int) $preview_loop + 1; $type = $product instanceof WC_Product ? $product->get_type() : 'simple'; echo 'class="product type-product status-publish instock purchasable product-type-' . esc_attr( $type ) . ' ' . esc_attr( $class ) . '"'; }
function wc_get_loop_prop( $prop, $default = 0 ) { global $preview_posts, $preview_loop; if ( 'loop' === $prop ) { return (int) $preview_loop; } if ( 'total' === $prop ) { return is_array( $preview_posts ) ? count( $preview_posts ) : 0; } return $default; }
function wc_get_stock_html( $product ) { $row = $product instanceof WC_Product ? sr2_preview_catalog_row( $product->get_sku() ) : array(); return '1' === ( $row['is_preorder'] ?? '' ) ? '<p class="stock in-stock">Available for preorder</p>' : '<p class="stock in-stock">In stock</p>'; }
/** Registry projection (wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv) for names, prices and pre-order state; never a second source of product facts. */
function sr2_preview_catalog_row( $sku ) {
	static $rows = null;
	if ( null === $rows ) {
		$rows = array();
		$path = dirname( __DIR__ ) . '/wordpress-theme/skyyrose-flagship/data/skyyrose-catalog.csv';
		$handle = is_readable( $path ) ? fopen( $path, 'r' ) : false;
		if ( $handle ) {
			$header = fgetcsv( $handle );
			while ( $header && false !== ( $line = fgetcsv( $handle ) ) ) {
				if ( count( $line ) === count( $header ) ) { $row = array_combine( $header, $line ); $rows[ strtolower( $row['sku'] ) ] = $row; }
			}
			fclose( $handle );
		}
	}
	return $rows[ strtolower( (string) $sku ) ] ?? array();
}
function woocommerce_template_loop_add_to_cart() {
	global $product;
	$url = $product instanceof WC_Product ? get_permalink( $product ) : '/tools/v2-theme-preview.php?route=product&sku=sg-005';
	echo '<a class="button product_type_variable add_to_cart_button" href="' . esc_url( $url ) . '" aria-describedby="woocommerce_loop_add_to_cart_link_describedby_' . esc_attr( $product instanceof WC_Product ? $product->get_id() : 0 ) . '">Select options</a><span id="woocommerce_loop_add_to_cart_link_describedby_' . esc_attr( $product instanceof WC_Product ? $product->get_id() : 0 ) . '" class="screen-reader-text">This product has multiple variants. The options may be chosen on the product page</span>';
}
function post_password_required() { return false; }
function get_the_password_form() { return ''; }
function has_term( $term, $taxonomy = '', $post = null ) {
	global $product;
	$product_id = $post instanceof WC_Product ? $post->get_id() : ( is_numeric( $post ) ? (int) $post : ( $product instanceof WC_Product ? $product->get_id() : 0 ) );
	$requested  = is_array( $term ) ? array_map( 'sanitize_title', $term ) : array( sanitize_title( $term ) );
	return (bool) array_intersect( $requested, wp_get_post_terms( $product_id, $taxonomy, array( 'fields' => 'slugs' ) ) );
}
function _n( $single, $plural, $number ) { return 1 === (int) $number ? $single : $plural; }

class WC_Product {
	private $id; private $name; private $image; private $sku; private $gallery;
	public function __construct( $id, $name, $image, $sku = '', $gallery = array() ) { $this->id = $id; $row = sr2_preview_catalog_row( $sku ); $this->name = $row['name'] ?? $name; $this->image = $image; $this->sku = $sku ?: 'preview-' . $id; $this->gallery = $gallery; }
	public function get_id() { return $this->id; }
	public function get_name() { return $this->name; }
	public function get_image_id() { return $this->image; }
	public function get_gallery_image_ids() { return $this->gallery; }
	public function get_price_html() { $row = sr2_preview_catalog_row( $this->sku ); $price = isset( $row['price'] ) ? (float) $row['price'] : 128.0; return '<span class="woocommerce-Price-amount amount">$' . number_format( $price, 2 ) . '</span>'; }
	public function is_in_stock() { return true; }
	public function is_visible() { return true; }
	public function is_purchasable() { return true; }
	public function get_type() { return 'variable'; }
	public function get_sku() { return $this->sku; }
	public function get_status() { return 'publish'; }
	public function get_permalink() { return '/tools/v2-theme-preview.php?route=product&sku=' . rawurlencode( $this->sku ); }
	public function get_short_description() { return 'A limited SkyyRose archive piece rooted in Oakland and built to carry the Bay with you.'; }
}
function wc_get_products( $args = array() ) {
	$fixtures = array(
		new WC_Product( 1, 'Bay Bridge Shirt', 1, 'sg-005', array( 102 ) ),
		new WC_Product( 2, 'Black Rose Hoodie', 2, 'br-004', array( 201, 202 ) ),
		new WC_Product( 3, 'Love Hurts Bomber Jacket', 3, 'lh-004', array( 301, 302 ) ),
		new WC_Product( 4, 'Kids Colorblock Hoodie Set — Red/Black', 4, 'kids-001', array( 401, 402 ) ),
		new WC_Product( 5, 'Kids Colorblock Hoodie Set — Purple/Black', 7, 'kids-002', array( 701, 702 ) ),
	);
	$categories = isset( $args['category'] ) ? array_map( 'sanitize_title', (array) $args['category'] ) : array();
	if ( $categories ) {
		$fixtures = array_values(
			array_filter(
				$fixtures,
				static function ( $fixture ) use ( $categories ) {
					return (bool) array_intersect( $categories, wp_get_post_terms( $fixture->get_id(), 'product_cat', array( 'fields' => 'slugs' ) ) );
				}
			)
		);
	}
	$limit = isset( $args['limit'] ) ? (int) $args['limit'] : count( $fixtures );
	return $limit < 0 ? $fixtures : array_slice( $fixtures, 0, max( 0, $limit ) );
}
function preview_jersey_products() {
	return array(
		new WC_Product( 103, 'Baseball Classic Black', 0, 'br-003' ),
		new WC_Product( 108, 'SF Inspired Football', 0, 'br-008' ),
		new WC_Product( 109, 'Last Oakland Football', 0, 'br-009' ),
		new WC_Product( 110, 'The Bay Basketball', 0, 'br-010' ),
		new WC_Product( 111, 'The Rose Hockey', 0, 'br-011' ),
		new WC_Product( 112, 'Last Oakland Baseball', 0, 'br-012' ),
		new WC_Product( 114, 'Giants Baseball', 0, 'br-014' ),
		new WC_Product( 115, 'Baseball Classic White', 0, 'br-015' )
	);
}
function preview_product_for_sku( $sku ) {
	$wanted = strtolower( (string) $sku );
	foreach ( array_merge( wc_get_products(), preview_jersey_products() ) as $candidate ) {
		if ( strtolower( $candidate->get_sku() ) === $wanted ) {
			return $candidate;
		}
	}
	return null;
}
function preview_product_has_fixture_media( $product ) {
	return $product instanceof WC_Product && (bool) preview_attachment_path( $product->get_image_id() );
}
function wc_get_product( $id ) { foreach ( array_merge( wc_get_products(), preview_jersey_products() ) as $product ) { if ( $product->get_id() === (int) $id ) { return $product; } } return null; }
function wc_get_product_id_by_sku( $sku = '' ) { global $preview_state; if ( 'kids-missing-purple' === $preview_state && 'kids-002' === strtolower( (string) $sku ) ) { return 0; } foreach ( array_merge( wc_get_products(), preview_jersey_products() ) as $product ) { if ( strtolower( $product->get_sku() ) === strtolower( (string) $sku ) ) { return $product->get_id(); } } return 0; }

require $theme_dir . '/functions.php';

if ( 'shop' === $route ) {
	$preview_posts = wc_get_products();
} elseif ( 'product' === $route ) {
	$preview_product = preview_product_for_sku( $preview_sku );
	if ( ! $preview_product ) {
		sr2_preview_fail_closed( 404, 'Unknown V2 product fixture', sprintf( 'SKU “%s” has no local V2 fixture. It was not replaced with another product.', $preview_sku ) );
	}
	if ( ! preview_product_has_fixture_media( $preview_product ) ) {
		sr2_preview_fail_closed( 422, 'V2 product fixture media unavailable', sprintf( 'SKU “%s” has no verified local product-media fixture, so the renderer will not show a different garment or a generic image.', $preview_sku ) );
	}
	$preview_posts = array( $preview_product );
	$GLOBALS['preview_product'] = $preview_product;
} elseif ( 'journal' === $route ) {
	$preview_posts = array();
} elseif ( in_array( $route, array( 'collections', 'pre-order', 'about', 'contact', 'wishlist', 'faq', 'shipping-returns', 'returns-exchanges', 'size-guide', 'privacy-policy', 'terms-of-service', 'accessibility' ), true ) ) {
	// WordPress would populate The Loop for every Page route.  Give the real V2
	// page template one inert fixture so local previews render page content too.
	$preview_posts = array( (object) array( 'ID' => 1 ) );
}

// Every accepted route reaches one explicit current V2 template. There is no
// catch-all route and no legacy/V1 path: new V2 work either renders here or
// fails closed above with the candidate identity visible to the reviewer.
require $theme_dir . '/' . $preview_template_map[ $route ];
