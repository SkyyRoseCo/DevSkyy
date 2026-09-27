<?php
if ( home_url() !== 'https://staging-7e48-skyyrose.wpcomstaging.com' ) { throw new Exception('Wrong environment'); }
$gateways=[];
foreach(WC()->payment_gateways()->payment_gateways() as $id=>$g){$gateways[$id]=['enabled'=>$g->enabled,'testmode'=>$g->get_option('testmode','unknown')];}
$zones=[];
foreach(array_merge([['id'=>0]],array_values(WC_Shipping_Zones::get_zones())) as $z){$zone=new WC_Shipping_Zone($z['id']);$methods=[];foreach($zone->get_shipping_methods(true) as $m){$methods[]=['id'=>$m->id,'title'=>$m->title,'cost'=>$m->get_option('cost'),'minimum'=>$m->get_option('min_amount')];}$zones[]=['id'=>$zone->get_id(),'name'=>$zone->get_zone_name(),'methods'=>$methods];}
global $wpdb;
echo wp_json_encode(['home'=>home_url(),'environment'=>wp_get_environment_type(),'theme'=>get_stylesheet(),'php'=>PHP_VERSION,'woocommerce'=>WC_VERSION,'gateways'=>$gateways,'shipping'=>$zones,'tax_enabled'=>get_option('woocommerce_calc_taxes'),'tax_rate_count'=>(int)$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->prefix}woocommerce_tax_rates"),'checkout_page_id'=>wc_get_page_id('checkout'),'cart_page_id'=>wc_get_page_id('cart'),'currency'=>get_woocommerce_currency()],JSON_PRETTY_PRINT);
