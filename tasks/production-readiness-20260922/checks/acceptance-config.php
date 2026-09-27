<?php
if(home_url()!=='https://staging-7e48-skyyrose.wpcomstaging.com'||wp_get_environment_type()!=='staging'){throw new Exception('Wrong environment');}
$s=get_option('woocommerce_stripe_settings',[]);
$keys=[];foreach(['test_publishable_key','test_secret_key','test_webhook_secret'] as $k){$keys[$k]=!empty($s[$k]);}
echo wp_json_encode(['home'=>home_url(),'environment'=>wp_get_environment_type(),'stripe_enabled'=>$s['enabled']??'no','stripe_testmode'=>$s['testmode']??'unknown','test_key_fields_present'=>$keys,'allowed_countries_mode'=>get_option('woocommerce_allowed_countries'),'specific_allowed_countries'=>get_option('woocommerce_specific_allowed_countries'),'shipping_countries_mode'=>get_option('woocommerce_ship_to_countries'),'specific_shipping_countries'=>get_option('woocommerce_specific_ship_to_countries'),'taxes_enabled'=>get_option('woocommerce_calc_taxes'),'automated_tax_setting'=>get_option('wc_connect_taxes_enabled','unset')],JSON_PRETTY_PRINT);
