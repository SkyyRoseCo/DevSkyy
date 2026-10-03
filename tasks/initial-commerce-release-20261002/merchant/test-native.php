<?php
/** Synthetic native Woo fixture only; does not execute production runner or contact external services. */
if (!defined('WP_CLI') || !WP_CLI || get_option('home') !== 'http://127.0.0.1:18362' || WC_VERSION !== '11.1.2' || !defined('DB_ENGINE') || DB_ENGINE !== 'sqlite') { throw new RuntimeException('ISOLATED_FIXTURE_ONLY'); }
$source = file_get_contents(dirname(__DIR__) . '/merchant_remediation.php');
eval(substr($source, 5, strpos($source, '$cfg =') - 5));
global $journal, $assertions;
$journal = tmpfile();
WC()->initialize_session(); WC()->customer = new WC_Customer(0, true); WC()->cart = new WC_Cart(); WC()->cart->empty_cart();
$assertions = array();
function merchant_test($condition, $label) { global $assertions; sr_assert($condition, 'TEST_' . $label); $assertions[] = $label; }
function synthetic_product($suffix) {
    $p = new WC_Product_Simple(); $p->set_name('Synthetic LH006 merchant ' . $suffix); $p->set_sku('synthetic-merchant-' . $suffix . '-' . wp_generate_uuid4());
    $p->set_status('publish'); $p->set_regular_price('95'); $p->set_manage_stock(false); $p->set_stock_quantity(null); $p->set_stock_status('instock'); $p->set_backorders('no');
    $size = new WC_Product_Attribute(); $size->set_name('Size'); $size->set_options(array('One Size')); $size->set_visible(true); $size->set_variation(false); $p->set_attributes(array('size'=>$size));
    $p->update_meta_data('_is_preorder', '0'); $p->save(); return $p;
}
$p = synthetic_product('success'); $id = $p->get_id(); $before = sr_state($id);
$key = WC()->cart->add_to_cart($id, 1); merchant_test((bool)$key, 'old_simple_cart_add');
$session = new WC_Cart_Session(WC()->cart); $session->set_session(); $old_cart = WC()->session->get('cart');
$order = new WC_Order(); $item = new WC_Order_Item_Product(); $item->set_product($p); $item->set_quantity(1); $item->set_subtotal('95'); $item->set_total('95'); $order->add_item($item); $order->save();
$old_order = json_encode(wc_get_order($order->get_id())->get_data());
$sizes = array('S','M','L','XL','2XL','3XL'); $operation = wp_generate_uuid4();
$after = sr_convert($id, $before, $sizes, $operation);
merchant_test(wc_get_product($id)->is_type('variable') && count($after['children']) === 6, 'six_native_variations');
merchant_test($after['price'] === '95' && !$after['manage_stock'] && $after['stock_quantity'] === null, 'native_parent_price_inventory_preserved');
foreach ($after['children'] as $child_id) {
    $v = wc_get_product($child_id); merchant_test(in_array($v->get_attribute('size'), $sizes, true) && $v->get_price() === '95' && !$v->get_manage_stock() && $v->get_stock_quantity() === null && $v->get_stock_status() === 'instock' && $v->get_backorders() === 'no', 'child_size_price_inventory_' . $v->get_attribute('size'));
}
WC()->session->set('cart', $old_cart); WC()->cart = new WC_Cart(); $session = new WC_Cart_Session(WC()->cart); $session->get_cart_from_session();
merchant_test(!isset(WC()->cart->get_cart()[$key]), 'old_simple_cart_requires_reselection');
merchant_test(count(wc_get_notices()) > 0, 'old_cart_has_native_customer_notice');
merchant_test(WC()->cart->add_to_cart($id, 1) === false, 'missing_size_rejected');
foreach ($sizes as $size) {
    WC()->cart->empty_cart(); wc_clear_notices(); $child_id = 0;
    foreach ($after['children'] as $cid) { if (wc_get_product($cid)->get_attribute('size') === $size) { $child_id = $cid; } }
    $key = WC()->cart->add_to_cart($id, 1, $child_id, array('attribute_size'=>$size));
    merchant_test((bool)$key && WC()->cart->get_cart()[$key]['variation_id'] === $child_id && WC()->cart->get_cart()[$key]['data']->get_price() === '95', 'native_size_cart_' . $size);
}
merchant_test(json_encode(wc_get_order($order->get_id())->get_data()) === $old_order, 'historical_synthetic_order_unchanged');
// Fail on the third child save: native rollback must leave a simple product and no children.
$failure = synthetic_product('rollback'); $fid = $failure->get_id(); $fbefore = sr_state($fid); $seen = 0;
$inject = function($v) use ($fid, &$seen) { if ($v instanceof WC_Product_Variation && $v->get_parent_id() === $fid && ++$seen === 3) { throw new RuntimeException('SYNTHETIC_CHILD_FAILURE'); } };
add_action('woocommerce_before_product_object_save', $inject);
$failed = false; try { sr_convert($fid, $fbefore, $sizes, wp_generate_uuid4()); } catch (Throwable $e) { $failed = $e->getMessage() === 'SYNTHETIC_CHILD_FAILURE'; }
remove_action('woocommerce_before_product_object_save', $inject);
merchant_test($failed, 'injected_failure_observed');
clean_post_cache($fid); wc_delete_product_transients($fid); wp_cache_flush();
merchant_test(wc_get_product($fid)->is_type('simple') && empty(sr_state($fid)['children']), 'native_transaction_rollback_no_partial_children');
merchant_test(json_encode(sr_state($fid)) === json_encode($fbefore), 'rollback_exact_preimage');
$guarded = false; try { sr_convert($fid, $fbefore, array('One Size'), wp_generate_uuid4()); } catch (Throwable $e) { $guarded = $e->getMessage() === 'CANONICAL_SIZE_SCOPE'; }
merchant_test($guarded && empty(sr_state($fid)['children']), 'invalid_sizes_rejected_before_mutation');
$drifted = $fbefore; $drifted['price'] = '94'; $guarded = false;
try { sr_convert($fid, $drifted, $sizes, wp_generate_uuid4()); } catch (Throwable $e) { $guarded = $e->getMessage() === 'LH006_FOREIGN_DRIFT'; }
merchant_test($guarded && wc_get_product($fid)->is_type('simple'), 'foreign_preimage_rejected');
// Committed recovery: child drift and new order references must refuse the entire restore.
$child_states=array(); foreach($after['children'] as $cid) { $child_states[$cid]=sr_child_state($cid); }
$cid=reset($after['children']); $v=wc_get_product($cid); $v->set_regular_price('96'); $v->save(); $guarded=false;
try { sr_restore($id,$before,$after,$operation,'variable',$child_states); } catch(Throwable $e) { $guarded=$e->getMessage()==='RESTORE_CHILD_FOREIGN_DRIFT'; }
merchant_test($guarded && wc_get_product($id)->is_type('variable'), 'committed_restore_refuses_child_foreign_drift');
$v->set_regular_price('95'); $v->save(); $child_states[$cid]=sr_child_state($cid);
$order2=new WC_Order(); $item2=new WC_Order_Item_Product(); $item2->set_product($v); $item2->set_quantity(1); $item2->set_total('95'); $order2->add_item($item2); $order2->save(); $guarded=false;
try { sr_restore($id,$before,$after,$operation,'variable',$child_states); } catch(Throwable $e) { $guarded=$e->getMessage()==='RESTORE_NEW_ORDER_REFERENCES'; }
merchant_test($guarded && wc_get_product($id)->is_type('variable'), 'committed_restore_refuses_new_child_order_reference');
$order2->remove_item($item2->get_id()); $order2->save(); $item2->delete(true); $order2->delete(true); $restored=sr_restore($id,$before,$after,$operation,'variable',$child_states);
merchant_test(wc_get_product($id)->is_type('simple') && empty($restored['children']) && $restored['price']==='95', 'committed_restore_simple_owned_children_only');
sr_preserved($before,$restored,array('date_modified')); merchant_test(true,'committed_restore_preimage_fields');
// Native media upload failure and product assignment failure preserve product preimages.
require_once ABSPATH.'wp-admin/includes/file.php'; require_once ABSPATH.'wp-admin/includes/media.php'; require_once ABSPATH.'wp-admin/includes/image.php';
$ip=synthetic_product('image'); $iid=$ip->get_id(); $ibefore=sr_state($iid);
$bad=media_handle_sideload(array('name'=>'synthetic-failed.webp','tmp_name'=>'/tmp/does-not-exist-skyyrose'),$iid);
merchant_test(is_wp_error($bad) && json_encode(sr_state($iid))===json_encode($ibefore),'native_upload_failure_preserves_product');
$front=dirname(__DIR__,3).'/wordpress-theme/skyyrose-flagship-2/assets/approved-card-fronts/kids-001-onmodel.webp'; $sha=hash_file('sha256',$front); $tmp=wp_tempnam('synthetic-approved.webp'); copy($front,$tmp);
$aid=media_handle_sideload(array('name'=>'synthetic-existing-approved.webp','tmp_name'=>$tmp),$iid); merchant_test(!is_wp_error($aid),'native_existing_image_import');
$iop=wp_generate_uuid4(); update_post_meta($aid,'_skyyrose_merchant_operation',$iop);
$inject_image=function($p) use($iid) { if($p->get_id()===$iid) { throw new RuntimeException('SYNTHETIC_IMAGE_ASSIGNMENT_FAILURE'); } };
add_action('woocommerce_before_product_object_save',$inject_image); $failed=false;
try { sr_assign_image($iid,$ibefore,$aid,$sha); } catch(Throwable $e) { $failed=$e->getMessage()==='SYNTHETIC_IMAGE_ASSIGNMENT_FAILURE'; }
remove_action('woocommerce_before_product_object_save',$inject_image); wp_cache_flush();
merchant_test($failed && json_encode(sr_state($iid))===json_encode($ibefore),'assignment_failure_preserves_product_retains_attachment');
$iafter=sr_assign_image($iid,$ibefore,$aid,$sha); merchant_test((int)$iafter['image_id']===$aid,'native_image_assignment');
$foreign=$iafter; $foreign['price']='94'; $guarded=false;
try { sr_restore($iid,$ibefore,$foreign,$iop,'image'); } catch(Throwable $e) { $guarded=$e->getMessage()==='RESTORE_FOREIGN_DRIFT'; }
merchant_test($guarded && (int)wc_get_product($iid)->get_image_id()===$aid,'image_restore_refuses_foreign_drift');
$irestored=sr_restore($iid,$ibefore,$iafter,$iop,'image');
merchant_test($irestored['image_id']===$ibefore['image_id'] && get_post($aid)!==null,'image_restore_original_attachment_retained');
// Test the runner's actual process-scoped filters directly without making requests.
$guard_start=strpos($source,'// Isolate only product webhooks'); $guard_end=strpos($source,'// These native product tables');
global $sr_download_url; eval(substr($source,$guard_start,$guard_end-$guard_start));
global $wp_filter;
$callbacks=$wp_filter['woocommerce_webhook_should_deliver']->callbacks[PHP_INT_MAX]; $callback=end($callbacks)['function'];
$webhook=new WC_Webhook(); $webhook->set_topic('product.updated'); merchant_test($callback(true,$webhook)===false,'product_webhook_suppressed');
$webhook->set_topic('order.updated'); merchant_test($callback(true,$webhook)===true && $callback(false,$webhook)===false,'order_webhook_permission_preserved');
$callbacks=$wp_filter['pre_http_request']->callbacks[PHP_INT_MAX]; $callback=end($callbacks)['function'];
$sr_download_url='https://staging-7e48-skyyrose.wpcomstaging.com/wp-content/themes/skyyrose-flagship-2/assets/approved-card-fronts/kids-001-onmodel.webp';
merchant_test($callback(false,array('method'=>'GET'),$sr_download_url)===false,'exact_active_image_get_allowed');
merchant_test(is_wp_error($callback(false,array('method'=>'POST'),$sr_download_url)) && is_wp_error($callback(false,array('method'=>'GET'),'https://example.invalid/')),'non_image_or_post_http_blocked');
$callbacks=$wp_filter['http_request_args']->callbacks[PHP_INT_MAX]; $callback=end($callbacks)['function'];
merchant_test($callback(array('redirection'=>5),$sr_download_url)['redirection']===0,'image_redirects_disabled');
$sr_download_url=null; merchant_test(is_wp_error($wp_filter['pre_http_request']->callbacks[PHP_INT_MAX][array_key_last($wp_filter['pre_http_request']->callbacks[PHP_INT_MAX])]['function'](false,array('method'=>'GET'),'https://example.invalid/')),'http_closed_between_downloads');
fclose($journal);
echo wp_json_encode(array('status'=>'PASS','assertions'=>count($assertions),'checks'=>$assertions,'home'=>get_option('home'),'wp'=>get_bloginfo('version'),'woo'=>WC_VERSION,'db'=>DB_ENGINE,'production_runner_executed'=>false,'external_http'=>'BLOCKED_BY_FIXTURE_MU','production_innodb_gate'=>'NOT_RUN'), JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
