<?php
/** Render the real override without persisting orders or calling gateways. */
define('ABSPATH', __DIR__);
function esc_html_e($s,$d=''){echo htmlspecialchars($s);}
function __($s,$d=''){return $s;}
function esc_html__($s,$d=''){return $s;}
function esc_html($s){return htmlspecialchars((string)$s);}
function esc_url($s){return htmlspecialchars($s);}
function wp_kses_post($s){return $s;}
function wc_format_datetime($d){return '2026-09-05';}
function do_action($hook,...$args){$GLOBALS['calls'][]=$hook;}
function wc_get_template($template,$args=[]){$GLOBALS['templates'][]=$template;}
class TestOrder {
 public function __construct(public string $status){}
 public function has_status($s){return in_array($this->status,(array)$s,true);}
 public function get_status(){return $this->status;}
 public function get_id(){return 0;}
 public function get_order_number(){return 'TEST';}
 public function get_payment_method(){return 'test_gateway';}
 public function get_checkout_payment_url(){return '/order-pay/test';}
 public function get_date_created(){return null;}
 public function get_formatted_order_total(){return '$25.00';}
 public function has_downloadable_item(){return false;}
 public function is_download_permitted(){return false;}
}
$expected=['failed'=>'Payment was not completed','pending'=>'Payment is pending','on-hold'=>'Your order is on hold','processing'=>'Your order is being processed','completed'=>'Your order is complete','cancelled'=>'Your order was cancelled','refunded'=>'Your order is marked refunded'];
foreach($expected as $status=>$copy){
 $order=new TestOrder($status);$calls=[];$templates=[];ob_start();include __DIR__.'/../../wordpress-theme/skyyrose-flagship-2/woocommerce/checkout/thankyou.php';$html=ob_get_clean();
 if(!str_contains($html,$copy)||str_contains($html,'Nothing was charged'))throw new RuntimeException('Incorrect payment assurance: '.$status);
 foreach(['woocommerce_before_thankyou','woocommerce_thankyou_test_gateway','woocommerce_thankyou'] as $hook){if(count(array_keys($calls,$hook,true))!==1)throw new RuntimeException('Hook count: '.$status.' '.$hook);}
 if(in_array('order/order-details.php',$templates,true))throw new RuntimeException('Duplicate native order details');
 if(in_array($status,['failed','pending'],true)!==str_contains($html,'/order-pay/test'))throw new RuntimeException('Retry boundary: '.$status);
}
echo "PASS seven order states, native gateway hooks once, no duplicate details or charge assurance\n";
