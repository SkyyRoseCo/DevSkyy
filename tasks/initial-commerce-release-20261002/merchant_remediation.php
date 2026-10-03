<?php
/** One-shot native Woo remediation. Requires explicit merchant authority and exact before-state. */
function sr_assert($condition, $message) { if (!$condition) { throw new RuntimeException($message); } }
function sr_state($id) {
    $p = wc_get_product($id);
    sr_assert($p, 'MISSING_PRODUCT');
    $r = $p->get_data(); unset($r['meta_data']);
    $r['attributes'] = array(); foreach ($p->get_attributes() as $key => $a) { $r['attributes'][$key] = $a->get_data(); }
    $r['children'] = get_children(array('post_parent' => $id, 'post_type' => 'product_variation', 'post_status' => 'any', 'fields' => 'ids'));
    $r['native_meta'] = array();
    foreach (array('_product_attributes', '_default_attributes', '_price', '_regular_price', '_sale_price', '_is_preorder', '_preorder_edition_size', '_preorder_available', '_preorder_ship_date', '_thumbnail_id') as $key) {
        $r['native_meta'][$key] = array('exists' => metadata_exists('post', $id, $key), 'value' => get_post_meta($id, $key, true));
    }
    return $r;
}
function sr_preserved($before, $after, $allowed) {
    foreach ($before as $field => $value) {
        if (in_array($field, $allowed, true)) { continue; }
        sr_assert(json_encode($after[$field]) === json_encode($value), 'PROTECTED_FIELD_DRIFT_' . $field);
    }
}
function sr_child_state($id) {
    $p=wc_get_product($id); sr_assert($p && $p->is_type('variation'), 'MISSING_NATIVE_CHILD');
    $r=$p->get_data(); unset($r['meta_data']); $r['operation']=$p->get_meta('_skyyrose_merchant_operation'); return $r;
}
function sr_convert($id, $before, $sizes, $operation) {
    sr_assert($sizes === array('S', 'M', 'L', 'XL', '2XL', '3XL'), 'CANONICAL_SIZE_SCOPE');
    sr_assert(json_encode(sr_state($id)) === json_encode($before), 'LH006_FOREIGN_DRIFT');
    sr_record(array('state' => 'LH006_VARIABLE_CONVERSION_INTENT', 'product_id' => $id, 'sizes' => $sizes, 'price' => $before['price'], 'stock_ownership' => 'EXISTING_UNMANAGED_UNCHANGED'));
    global $wpdb;
    sr_assert($wpdb->query('START TRANSACTION') !== false, 'TRANSACTION_START_FAILED');
    try {
        $p = new WC_Product_Variable($id);
        $attributes = $p->get_attributes();
        $size_attribute = new WC_Product_Attribute();
        foreach (array('id', 'name', 'position', 'visible') as $field) { $size_attribute->{'set_' . $field}($before['attributes']['size'][$field]); }
        $size_attribute->set_options($sizes); $size_attribute->set_variation(true); $attributes['size'] = $size_attribute;
        $p->set_attributes($attributes); $p->set_default_attributes(array()); $p->save();
        $created = array();
        foreach ($sizes as $size) {
            $v = new WC_Product_Variation(); $v->set_parent_id($id); $v->set_attributes(array('size' => $size));
            $v->set_regular_price($before['regular_price']); $v->set_sale_price($before['sale_price']); $v->set_price($before['price']);
            $v->set_manage_stock(false); $v->set_stock_quantity(null); $v->set_stock_status($before['stock_status']); $v->set_backorders($before['backorders']);
            $v->set_virtual($before['virtual']); $v->set_downloadable($before['downloadable']);
            $v->set_status('publish'); $v->update_meta_data('_skyyrose_merchant_operation', $operation); $v->save();
            $created[$size] = $v->get_id();
            sr_record(array('state' => 'VARIATION_CREATED_UNCOMMITTED', 'id' => $v->get_id(), 'parent_id' => $id, 'size' => $size));
        }
        WC_Product_Variable::sync($id); wc_delete_product_transients($id); clean_post_cache($id);
        $after = sr_state($id);
        sr_preserved($before, $after, array('date_modified', 'attributes', 'default_attributes', 'children', 'regular_price', 'sale_price', 'native_meta'));
        foreach ($before['native_meta'] as $key => $value) {
            if (in_array($key, array('_product_attributes', '_default_attributes', '_regular_price', '_sale_price'), true)) { continue; }
            sr_assert($after['native_meta'][$key] === $value, 'NATIVE_META_DRIFT_' . $key);
        }
        sr_assert(count($after['children']) === 6 && wc_get_product($id)->is_type('variable'), 'CONVERSION_INCOMPLETE');
        sr_assert($after['attributes']['size']['options'] === $sizes && $after['attributes']['size']['variation'] === true, 'PARENT_SIZE_DRIFT');
        foreach ($created as $size => $child_id) {
            $v = new WC_Product_Variation($child_id);
            sr_assert($v->get_parent_id() === $id && $v->get_attributes() === array('size' => $size), 'CHILD_SIZE_DRIFT');
            sr_assert($v->get_price() === $before['price'] && $v->get_regular_price() === $before['regular_price'] && $v->get_sale_price() === $before['sale_price'], 'CHILD_PRICE_DRIFT');
            sr_assert($v->get_manage_stock() === false && $v->get_stock_quantity() === null && $v->get_stock_status() === $before['stock_status'] && $v->get_backorders() === $before['backorders'] && $v->get_status() === 'publish', 'CHILD_INVENTORY_DRIFT');
            sr_assert($v->get_meta('_skyyrose_merchant_operation') === $operation, 'CHILD_OWNERSHIP_DRIFT');
        }
        $child_states=array(); foreach($created as $child_id) { $child_states[$child_id]=sr_child_state($child_id); }
        sr_record(array('state' => 'LH006_COMMIT_INTENT', 'product_id' => $id, 'variation_ids' => $created, 'after' => $after, 'child_states'=>$child_states));
        sr_assert($wpdb->query('COMMIT') !== false, 'TRANSACTION_COMMIT_UNCERTAIN');
        clean_post_cache($id); wc_delete_product_transients($id);
        sr_record(array('state' => 'LH006_COMMITTED', 'product_id' => $id, 'variation_ids' => $created));
        return $after;
    } catch (Throwable $error) {
        $wpdb->query('ROLLBACK'); clean_post_cache($id); wc_delete_product_transients($id);
        sr_record(array('state' => 'LH006_STOP_RECONCILE_REQUIRED', 'error' => $error->getMessage(), 'product_id' => $id));
        throw $error;
    }
}
function sr_assign_image($id, $before, $attachment, $sha256) {
    sr_assert(hash_file('sha256', get_attached_file($attachment)) === $sha256, 'UPLOADED_IMAGE_HASH_DRIFT');
    sr_assert(json_encode(sr_state($id)) === json_encode($before), 'PRODUCT_FOREIGN_DRIFT');
    sr_record(array('state' => 'IMAGE_ASSIGNMENT_INTENT', 'product_id' => $id, 'old_image_id' => $before['image_id'], 'new_image_id' => $attachment));
    $p = wc_get_product($id); $p->set_image_id($attachment); $p->save();
    $after = sr_state($id); sr_preserved($before, $after, array('date_modified', 'image_id', 'native_meta'));
    foreach ($before['native_meta'] as $key => $value) { if ($key !== '_thumbnail_id') { sr_assert($after['native_meta'][$key] === $value, 'NATIVE_META_DRIFT_' . $key); } }
    sr_assert($after['image_id'] == $attachment, 'IMAGE_ASSIGNMENT_FAILED');
    clean_post_cache($id); wc_delete_product_transients($id);
    sr_record(array('state' => 'IMAGE_ASSIGNED', 'product_id' => $id, 'attachment_id' => $attachment, 'sha256' => $sha256, 'after' => $after));
    return $after;
}
function sr_restore($id, $before, $expected_after, $operation, $mode, $expected_children = array()) {
    sr_assert(in_array($mode, array('image', 'variable'), true), 'RESTORE_MODE');
    sr_assert(json_encode(sr_state($id)) === json_encode($expected_after), 'RESTORE_FOREIGN_DRIFT');
    if ($mode === 'image') {
        $attachment = (int) $expected_after['image_id'];
        sr_assert(get_post_meta($attachment, '_skyyrose_merchant_operation', true) === $operation, 'RESTORE_IMAGE_OWNERSHIP');
        sr_record(array('state'=>'IMAGE_RESTORE_INTENT','product_id'=>$id,'original_image_id'=>$before['image_id'],'retained_attachment_id'=>$attachment));
        $p=wc_get_product($id); $p->set_image_id($before['image_id']); $p->save();
        $restored=sr_state($id); sr_preserved($before, $restored, array('date_modified'));
        clean_post_cache($id); wc_delete_product_transients($id);
        sr_record(array('state'=>'IMAGE_RESTORED_ATTACHMENT_RETAINED','product_id'=>$id,'after'=>$restored));
        return $restored;
    }
    global $wpdb;
    foreach ($expected_after['children'] as $child_id) {
        $v=wc_get_product($child_id);
        sr_assert($v && $v->get_parent_id() === $id && $v->get_meta('_skyyrose_merchant_operation') === $operation, 'RESTORE_CHILD_OWNERSHIP');
        sr_assert(isset($expected_children[$child_id]) && json_encode(sr_child_state($child_id)) === json_encode($expected_children[$child_id]), 'RESTORE_CHILD_FOREIGN_DRIFT');
        $refs=(int)$wpdb->get_var($wpdb->prepare("SELECT COUNT(*) FROM {$wpdb->prefix}woocommerce_order_itemmeta WHERE meta_key IN ('_product_id','_variation_id') AND meta_value=%s", (string)$child_id));
        sr_assert($refs === 0, 'RESTORE_NEW_ORDER_REFERENCES');
    }
    sr_record(array('state'=>'VARIABLE_RESTORE_INTENT','product_id'=>$id,'remove_owned_children'=>$expected_after['children']));
    sr_assert($wpdb->query('START TRANSACTION') !== false, 'RESTORE_TRANSACTION_START');
    try {
        foreach ($expected_after['children'] as $child_id) { wc_get_product($child_id)->delete(true); }
        $p=new WC_Product_Simple($id); $attributes=array();
        foreach ($before['attributes'] as $key=>$data) {
            $a=new WC_Product_Attribute(); foreach(array('id','name','options','position','visible','variation') as $field) { $a->{'set_'.$field}($data[$field]); } $attributes[$key]=$a;
        }
        $p->set_attributes($attributes); $p->set_default_attributes($before['default_attributes']);
        foreach(array('regular_price','sale_price','price','manage_stock','stock_quantity','stock_status','backorders') as $field) { $p->{'set_'.$field}($before[$field]); }
        $p->save(); clean_post_cache($id); wc_delete_product_transients($id); $restored=sr_state($id);
        sr_preserved($before,$restored,array('date_modified'));
        sr_record(array('state'=>'VARIABLE_RESTORE_COMMIT_INTENT','product_id'=>$id,'after'=>$restored));
        sr_assert($wpdb->query('COMMIT') !== false, 'RESTORE_COMMIT_UNCERTAIN');
        clean_post_cache($id); wc_delete_product_transients($id);
        sr_record(array('state'=>'VARIABLE_RESTORED','product_id'=>$id)); return $restored;
    } catch(Throwable $error) { $wpdb->query('ROLLBACK'); clean_post_cache($id); wc_delete_product_transients($id); throw $error; }
}
function sr_record($row) {
    global $journal;
    $payload = json_encode($row, JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR) . "\n";
    sr_assert(fwrite($journal, $payload) === strlen($payload) && fflush($journal) && fsync($journal), 'JOURNAL_DURABILITY_FAILURE');
    echo $payload;
}
global $journal, $sr_download_url;
$cfg = json_decode(base64_decode(getenv('SKYYROSE_COMMERCE_INPUT')), true, 512, JSON_THROW_ON_ERROR);
sr_assert(get_option('home') === 'https://skyyrose.co', 'WRONG_TARGET');
sr_assert(get_option('stylesheet') === 'skyyrose-flagship', 'ACTIVE_THEME_DRIFT');
sr_assert(preg_match('/^[a-f0-9-]{36}$/D', $cfg['operation']), 'INVALID_OPERATION');
sr_assert(in_array($cfg['mode'], array('images-only', 'lh006-only'), true), 'INVALID_MODE');
$expected = array(9879 => 'lh-006', 9955 => 'kids-001', 9956 => 'kids-002');
$before = array(); foreach ($cfg['before']['products'] as $row) { $before[$row['id']] = $row; }
sr_assert(array_keys($before) === array_keys($expected), 'BEFORE_SCOPE');
foreach ($expected as $id => $sku) {
    $p = wc_get_product($id);
    sr_assert($p && $p->get_sku() === $sku && $p->is_type('simple'), 'PRODUCT_IDENTITY_OR_TYPE_DRIFT');
    sr_assert(json_encode(sr_state($id)) === json_encode($before[$id]), 'BEFORE_STATE_DRIFT_' . $sku);
    sr_assert(!$p->get_manage_stock() && $p->get_stock_quantity() === null && $p->get_stock_status() === 'instock', 'INVENTORY_PRECONDITION');
    sr_assert(empty($before[$id]['children']), 'EXISTING_VARIATIONS');
}
sr_assert($before[9879]['price'] === '95' && $before[9879]['sale_price'] === '' && $before[9879]['native_meta']['_is_preorder']['value'] === '0', 'LH006_COMMERCIAL_PRECONDITION');
sr_assert(array_keys($cfg['images']) === array('kids-001', 'kids-002'), 'IMAGE_SCOPE');
sr_assert($cfg['sizes'] === array('S', 'M', 'L', 'XL', '2XL', '3XL'), 'CANONICAL_SIZE_SCOPE');
$image_hashes = array('kids-001' => 'c6bd2ddd555c4359c302eebb051d5fbad4d34bec0b324b44f3447831f3ec9c9a', 'kids-002' => '88c0ca36b22a95ce1ee7969b50b4e256718ffda584027dfd97e219605aa3e51b');
foreach ($cfg['images'] as $sku => $image) {
    sr_assert($image['url'] === 'https://staging-7e48-skyyrose.wpcomstaging.com/wp-content/themes/skyyrose-flagship-2/assets/approved-card-fronts/' . $sku . '-onmodel.webp' && $image['sha256'] === $image_hashes[$sku], 'UNREVIEWED_IMAGE');
}
// Isolate only product webhooks in this process; leave order/payment hooks intact.
add_filter('woocommerce_webhook_should_deliver', function($deliver, $webhook) { return str_starts_with($webhook->get_topic(), 'product.') ? false : $deliver; }, PHP_INT_MAX, 2);
$sr_download_url = null;
add_filter('pre_http_request', function($pre, $args, $url) {
    global $sr_download_url;
    return $sr_download_url === $url && strtoupper($args['method'] ?? 'GET') === 'GET' ? $pre : new WP_Error('sr_merchant_isolation', 'Outbound HTTP blocked during merchant correction.');
}, PHP_INT_MAX, 3);
add_filter('http_request_args', function($args, $url) {
    global $sr_download_url; if ($sr_download_url === $url) { $args['redirection'] = 0; } return $args;
}, PHP_INT_MAX, 2);
// These native product tables must support rollback before any conversion.
if ($cfg['mode'] === 'lh006-only') {
    global $wpdb;
    foreach (array($wpdb->posts, $wpdb->postmeta, $wpdb->options, $wpdb->terms, $wpdb->term_taxonomy, $wpdb->term_relationships, $wpdb->prefix . 'wc_product_meta_lookup') as $table) {
        $status = $wpdb->get_row($wpdb->prepare('SHOW TABLE STATUS WHERE Name=%s', $table));
        sr_assert($status && $status->Engine === 'InnoDB', 'TRANSACTIONAL_TABLE_REQUIRED_' . $table);
    }
}
$journal_path = sys_get_temp_dir() . '/skyyrose-commerce-' . $cfg['operation'] . '.jsonl';
$previous_umask = umask(0077); $journal = fopen($journal_path, 'x'); umask($previous_umask);
sr_assert($journal !== false, 'OPERATION_ALREADY_CLAIMED');
clearstatcache(true, $journal_path); sr_assert((fileperms($journal_path) & 0777) === 0600, 'JOURNAL_PERMISSIONS');
sr_record(array('state' => 'BEFORE_CAPTURED', 'mode' => $cfg['mode'], 'operation' => $cfg['operation'], 'journal' => $journal_path, 'home' => get_option('home'), 'products' => $before));
try {
    if ($cfg['mode'] === 'images-only') {
        require_once ABSPATH . 'wp-admin/includes/file.php'; require_once ABSPATH . 'wp-admin/includes/media.php'; require_once ABSPATH . 'wp-admin/includes/image.php';
        foreach (array(9955 => 'kids-001', 9956 => 'kids-002') as $id => $sku) {
            $image = $cfg['images'][$sku];
            sr_record(array('state' => 'IMAGE_IMPORT_INTENT', 'product_id' => $id, 'source' => $image));
            $sr_download_url = $image['url']; $tmp = download_url($image['url'], 60); $sr_download_url = null;
            sr_assert(!is_wp_error($tmp), 'IMAGE_DOWNLOAD_FAILED');
            sr_assert(hash_file('sha256', $tmp) === $image['sha256'], 'SOURCE_IMAGE_HASH_DRIFT');
            $attachment = media_handle_sideload(array('name' => $sku . '-approved-front-' . $cfg['operation'] . '.webp', 'tmp_name' => $tmp), $id, wc_get_product($id)->get_name() . ' — existing approved front');
            sr_assert(!is_wp_error($attachment), 'IMAGE_IMPORT_FAILED');
            update_post_meta($attachment, '_skyyrose_merchant_operation', $cfg['operation']);
            sr_record(array('state' => 'ATTACHMENT_CREATED', 'product_id' => $id, 'attachment_id' => $attachment));
            sr_assign_image($id, $before[$id], $attachment, $image['sha256']);
        }
        sr_assert(json_encode(sr_state(9879)) === json_encode($before[9879]), 'LH006_UNEXPECTED_CHANGE');
    } else { sr_convert(9879, $before[9879], $cfg['sizes'], $cfg['operation']); }
    $after = array(); foreach ($expected as $id => $sku) { $after[$id] = sr_state($id); }
    sr_record(array('state' => 'REMEDIATION_APPLIED_SEPARATE_READBACK_REQUIRED', 'mode' => $cfg['mode'], 'operation' => $cfg['operation'], 'products' => $after));
} catch (Throwable $error) {
    sr_record(array('state' => 'FAILED_OR_PARTIAL_STOP_NO_RETRY', 'error' => $error->getMessage(), 'operation' => $cfg['operation'])); throw $error;
} finally { fclose($journal); }
