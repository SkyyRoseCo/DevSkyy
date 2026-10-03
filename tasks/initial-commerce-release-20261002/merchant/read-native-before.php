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
sr_assert(get_option('home') === 'https://skyyrose.co', 'WRONG_TARGET');
$rows = array(); foreach (array(9879,9955,9956) as $id) { $r=sr_state($id); $r['runtime_type']=wc_get_product($id)->get_type(); $rows[]=$r; }
global $wpdb; $tables=array(); foreach(array($wpdb->posts,$wpdb->postmeta,$wpdb->options,$wpdb->terms,$wpdb->term_taxonomy,$wpdb->term_relationships,$wpdb->prefix.'wc_product_meta_lookup') as $table) { $t=$wpdb->get_row($wpdb->prepare('SHOW TABLE STATUS WHERE Name=%s',$table)); $tables[]=array('name'=>$table,'engine'=>$t?$t->Engine:null); }
$media=array(); foreach(array(9955,9956) as $id) { $aid=wc_get_product($id)->get_image_id(); $file=$aid?get_attached_file($aid):null; $media[]=array('product_id'=>$id,'attachment_id'=>$aid,'url'=>$aid?wp_get_attachment_url($aid):null,'sha256'=>$file&&is_file($file)?hash_file('sha256',$file):null,'operation'=>$aid?get_post_meta($aid,'_skyyrose_merchant_operation',true):null); }
echo wp_json_encode(array('home'=>get_option('home'),'stylesheet'=>get_option('stylesheet'),'recorded_utc'=>gmdate('c'),'wp'=>get_bloginfo('version'),'woo'=>WC_VERSION,'products'=>$rows,'tables'=>$tables,'media'=>$media),JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES);
