<?php
/** Disposable native browser data, consumed from a pinned get_product projection. */
if ( ! defined( 'WP_CLI' ) || ! WP_CLI || ! defined( 'SKYYROSE_RELEASE_SYNTHETIC_FIXTURE' ) || ! SKYYROSE_RELEASE_SYNTHETIC_FIXTURE || DB_NAME !== 'sr_release_fixture' || get_option( 'home' ) !== 'http://127.0.0.1:18362' ) {
	throw new RuntimeException( 'Private synthetic release fixture required.' );
}
$root = dirname( __DIR__, 2 );
$projection = json_decode( file_get_contents( $root . '/.artifacts/release-gates-20261019/runtime-official/catalog-projection.json' ), true );
if ( ! $projection || hash_file( 'sha256', $root . '/logo-registry.json' ) !== $projection['registry_sha256'] || hash_file( 'sha256', $root . '/skyyrose/core/product.py' ) !== $projection['reader_sha256'] ) {
	throw new RuntimeException( 'Current registry/reader projection binding is required.' );
}
$bindings = array();
global $wp_rewrite;
$wp_rewrite->set_permalink_structure( '/%postname%/' );
flush_rewrite_rules( false );
foreach ( $projection['products'] as $record ) {
	$sku = $record['sku'];
	if ( wc_get_product_id_by_sku( $sku ) ) {
		throw new RuntimeException( 'Refusing to overwrite an existing canonical fixture SKU.' );
	}
	$sizes = $record['sizes'];
	$product = count( $sizes ) > 1 ? new WC_Product_Variable() : new WC_Product_Simple();
	$product->set_name( $record['name'] );
	$product->set_sku( $sku );
	$product->set_slug( $sku );
	$product->set_status( '1' === $record['published'] ? 'publish' : 'draft' );
	$product->set_manage_stock( false );
	$product->set_stock_status( 'instock' ); // Explicit synthetic availability, never live stock proof.
	$product->update_meta_data( '_is_preorder', $record['is_preorder'] );
	$product->update_meta_data( '_sr_release_synthetic', '1' );
	if ( count( $sizes ) > 1 ) {
		$size = new WC_Product_Attribute();
		$size->set_name( 'Size' );
		$size->set_options( $sizes );
		$size->set_visible( true );
		$size->set_variation( true );
		$product->set_attributes( array( $size ) );
	} else {
		$product->set_regular_price( $record['price'] );
	}
	$product->save();
	$term = term_exists( $record['collection'], 'product_cat' );
	if ( ! $term ) { $term = wp_insert_term( $record['collection'], 'product_cat', array( 'slug' => $record['collection'] ) ); }
	wp_set_object_terms( $product->get_id(), (int) $term['term_id'], 'product_cat' );
	$children = array();
	if ( count( $sizes ) > 1 ) {
		foreach ( $sizes as $value ) {
			$child = new WC_Product_Variation();
			$child->set_parent_id( $product->get_id() );
			$child->set_status( 'publish' );
			$child->set_attributes( array( 'size' => $value ) );
			$child->set_regular_price( $record['price'] );
			$child->set_manage_stock( false );
			$child->set_stock_status( 'instock' );
			$child->save();
			$children[ $value ] = $child->get_id();
		}
		WC_Product_Variable::sync( $product->get_id() );
	}
	$bindings[ $sku ] = array( 'id' => $product->get_id(), 'url' => get_permalink( $product->get_id() ), 'collection' => $record['collection'], 'children' => $children );
}

function sr_release_page( $slug, $title, $parent = 0, $template = 'default', $content = '' ) {
	$id = wp_insert_post( array( 'post_type' => 'page', 'post_status' => 'publish', 'post_name' => $slug, 'post_title' => $title, 'post_parent' => $parent, 'post_content' => $content ), true );
	if ( is_wp_error( $id ) ) { throw new RuntimeException( $id->get_error_message() ); }
	update_post_meta( $id, '_wp_page_template', $template );
	return $id;
}
$definitions = skyyrose2_marketplace_pages();
$collections = sr_release_page( 'collections', 'Collections', 0, 'template-collections.php' );
$worlds = sr_release_page( 'worlds', 'Worlds' );
$routes = array();
$directory = '<nav aria-label="Collection worlds"><ul>';
foreach ( array( 'signature', 'black-rose', 'love-hurts', 'kids-capsule' ) as $slug ) {
	$definition = $definitions[ $slug ];
	$id = sr_release_page( $slug, $definition['title'], $collections, $definition['template'] );
	$routes[] = array( 'logical_key' => $slug, 'path' => '/collections/' . $slug . '/', 'id' => $id, 'template' => $definition['template'], 'collection' => $slug, 'kind' => 'collection' );
	$definition = $definitions[ 'immersive-' . $slug ];
	$id = sr_release_page( $slug, $definition['title'], $worlds, $definition['template'] );
	$routes[] = array( 'logical_key' => 'immersive-' . $slug, 'path' => '/worlds/' . $slug . '/', 'id' => $id, 'template' => $definition['template'], 'collection' => $slug, 'kind' => 'world' );
	$directory .= '<li><a href="' . esc_url( get_permalink( $id ) ) . '">' . esc_html( $definition['title'] ) . '</a></li>';
}
$directory .= '</ul></nav>';
wp_update_post( array( 'ID' => $worlds, 'post_content' => $directory ) );
$routes[] = array( 'logical_key' => 'worlds', 'path' => '/worlds/', 'id' => $worlds, 'template' => 'default', 'kind' => 'directory' );
$guide = $definitions['size-guide'];
$id = sr_release_page( 'size-guide', $guide['title'], 0, $guide['template'], $guide['content'] );
$routes[] = array( 'logical_key' => 'size-guide', 'path' => '/size-guide/', 'id' => $id, 'template' => 'default', 'kind' => 'guide' );
foreach ( array( 'shop' => '', 'cart' => '[woocommerce_cart]', 'checkout' => '[woocommerce_checkout]', 'myaccount' => '[woocommerce_my_account]' ) as $slug => $content ) {
	$id = sr_release_page( $slug, ucfirst( $slug ), 0, 'default', $content );
	update_option( 'woocommerce_' . $slug . '_page_id', $id );
}
foreach ( $bindings as $sku => &$binding ) {
	if ( get_post_meta( $binding['id'], '_sr_release_synthetic', true ) !== '1' || wc_get_product( $binding['id'] )->get_sku() !== $sku ) {
		throw new RuntimeException( 'Synthetic native product identity changed.' );
	}
	$binding['url'] = get_permalink( $binding['id'] );
}
unset( $binding );
$manifest = array( 'schema' => 'skyyrose.synthetic-native-release-fixture.v1', 'home' => get_option( 'home' ), 'authentication' => 'NOT_APPLICABLE', 'wp' => get_bloginfo( 'version' ), 'woocommerce' => WC_VERSION, 'registry_sha256' => $projection['registry_sha256'], 'reader_sha256' => $projection['reader_sha256'], 'products' => $bindings, 'routes' => $routes, 'limits' => array( 'Synthetic unmanaged availability only', 'No live product/order state copied', 'No new asset acceptance', 'Local pages do not establish published production routes' ) );
file_put_contents( $root . '/tasks/release-gates-20261019/evidence/native-browser-fixture.json', wp_json_encode( $manifest, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES ) );
echo 'Seeded ' . count( $bindings ) . ' canonical fixture products and ' . count( $routes ) . " logical routes.\n";
