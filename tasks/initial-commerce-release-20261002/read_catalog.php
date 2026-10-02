<?php
/** Read-only Woo catalog/configuration evidence. Never reads orders or gateway secrets. */
$expected_home = getenv('SR_EXPECTED_HOME');
if (!in_array($expected_home, ['https://staging-7e48-skyyrose.wpcomstaging.com', 'https://skyyrose.co'], true) || get_option('home') !== $expected_home) {
    throw new RuntimeException('TARGET_IDENTITY_MISMATCH');
}
$ids = get_posts(['post_type' => ['product', 'product_variation'], 'post_status' => ['publish', 'draft', 'private', 'pending'], 'numberposts' => -1, 'fields' => 'ids', 'orderby' => 'ID', 'order' => 'ASC']);
$records = [];
foreach ($ids as $id) {
    $product = wc_get_product($id);
    if (!$product) { throw new RuntimeException('PRODUCT_UNREADABLE'); }
    $attributes = [];
    foreach ($product->get_attributes() as $key => $attribute) {
        $attributes[$key] = is_object($attribute) ? ['name' => $attribute->get_name(), 'options' => $attribute->is_taxonomy() ? wc_get_product_terms($id, $attribute->get_name(), ['fields' => 'names']) : $attribute->get_options(), 'variation' => $attribute->get_variation(), 'visible' => $attribute->get_visible()] : $attribute;
    }
    $metadata = [];
    foreach (['_is_preorder', '_preorder_edition_size', '_preorder_available', '_preorder_ship_date'] as $key) { $metadata[$key] = get_post_meta($id, $key, true); }
    $images = [];
    foreach (array_unique(array_filter(array_merge([$product->get_image_id()], $product->get_gallery_image_ids()))) as $attachment_id) {
        $images[] = ['id' => $attachment_id, 'url' => wp_get_attachment_url($attachment_id)];
    }
    $records[] = ['id' => $id, 'parent_id' => $product->get_parent_id(), 'sku' => $product->get_sku(), 'name' => $product->get_name(), 'status' => $product->get_status(), 'type' => $product->get_type(), 'url' => get_permalink($id), 'price' => $product->get_price(), 'regular_price' => $product->get_regular_price(), 'sale_price' => $product->get_sale_price(), 'manage_stock' => $product->get_manage_stock(), 'stock_quantity' => $product->get_stock_quantity(), 'stock_status' => $product->get_stock_status(), 'backorders' => $product->get_backorders(), 'purchasable' => $product->is_purchasable(), 'attributes' => $attributes, 'images' => $images, 'preorder' => $metadata];
}
$gateways = [];
foreach (WC()->payment_gateways()->payment_gateways() as $id => $gateway) {
    $gateways[] = ['id' => $id, 'enabled' => $gateway->enabled, 'testmode' => $gateway->get_option('testmode', 'not_exposed')];
}
echo json_encode(['recorded_at_utc' => gmdate('c'), 'home' => get_option('home'), 'stylesheet' => get_option('stylesheet'), 'currency' => get_woocommerce_currency(), 'records' => $records, 'gateways' => $gateways, 'scope' => 'product configuration and safe gateway flags only; no orders, customers, secrets, or mutations'], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
