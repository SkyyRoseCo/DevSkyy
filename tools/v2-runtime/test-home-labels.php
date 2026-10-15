<?php
define('ABSPATH', __DIR__);
function skyyrose2_collections() { return ['signature'=>['name'=>'Signature'],'black-rose'=>['name'=>'Black Rose'],'love-hurts'=>['name'=>'Love Hurts']]; }
// The worlds rail renders each world's registry collection imagery (2.5.3).
function skyyrose2_collection_media($slug, $role) { return ['src'=>'/fixture/'.$slug.'.webp','width'=>100,'height'=>150,'role'=>$role,'sku'=>'fixture','alt'=>$slug]; }
function skyyrose2_collection_media_markup($image, ...$args) { return '<img src="'.esc_url($image['src']).'" alt="">'; }
function skyyrose2_collection_url($slug) { return '/collections/'.$slug.'/'; }
function get_template_part(...$args) {}
function absint($n) { return abs((int)$n); }
function __($s,...$args) { return $s; }
function esc_attr($s) { return htmlspecialchars($s,ENT_QUOTES); }
function esc_html($s) { return htmlspecialchars($s,ENT_QUOTES); }
function esc_url($s) { return $s; }
function esc_attr_e($s,...$args) { echo esc_attr($s); }
function esc_html_e($s,...$args) { echo esc_html($s); }
set_error_handler(function($n,$s){throw new RuntimeException($s);});
foreach ([[],['collections'=>['signature'=>[]]],['collections'=>['signature'=>['name'=>'Custom & House']]]] as $args) {
 ob_start(); include dirname(__DIR__, 2).'/wordpress-theme/skyyrose-flagship-2/template-parts/home/living-archive-worlds.php'; $html=ob_get_clean();
 foreach (['Enter '.($args['collections']['signature']['name']??'Signature'),'Enter Black Rose','Enter Love Hurts'] as $label) { if(!str_contains($html,esc_html($label)))throw new RuntimeException('Missing label: '.$label); }
}
echo "PASS omitted/partial collection labels and explicit escaped names\n";
