<?php
define('ABSPATH','/'); define('SKYYROSE2_DIR',getcwd().'/wordpress-theme/skyyrose-flagship-2');define('SKYYROSE2_URI','https://example.test/theme');
function add_action(...$a){}function add_filter(...$a){}function sanitize_title($x){return $x;}function absint($x){return abs((int)$x);}
require SKYYROSE2_DIR.'/inc/v2-media-eligibility.php';
$s=file_get_contents(SKYYROSE2_DIR.'/functions.php');$start=strpos($s,'function skyyrose2_collection_hero_motion(');$end=strpos($s,"\n}\n",$start)+3;eval(substr($s,$start,$end-$start));
$n=0;function ck($v,$m){global $n;if(!$v)throw new Exception($m);$n++;}
foreach(['signature','black-rose','love-hurts'] as $k){
 $cinema=skyyrose2_collection_cinema($k);ck(!empty($cinema['poster'])&&count($cinema['motion'])===2,'resolve '.$k);
 foreach(['hero.mp4','hero.webm','poster.webp'] as $f){
  $rel='assets/video/collection-heroes/approved/'.$k.'/cinema-20261008/'.$f;$r=skyyrose2_media_inventory()['assets'][$rel];
  ck(skyyrose2_media_record_allowed($rel,$r),'allow');
  ck(!skyyrose2_media_record_allowed($rel,$r,'card_front'),'card role forbidden');
  ck(!skyyrose2_media_record_allowed($rel,$r,'','lh-004'),'sku forbidden');
  $bad=$r;$bad['sha256']=str_repeat('0',64);ck(!skyyrose2_media_record_allowed($rel,$bad),'hash drift');
  $bad=$r;$bad['authorization']['sha256']=str_repeat('0',64);ck(!skyyrose2_media_record_allowed($rel,$bad),'receipt drift');
  $bad=$r;$bad['collections']='signature';ck(!skyyrose2_media_record_allowed($rel,$bad),'malformed collection');
  $bad=$r;$bad['collections']=['kids-capsule'];ck(!skyyrose2_media_record_allowed($rel,$bad),'wrong collection');
  $tag=$f==='poster.webp'?'<img src="'.SKYYROSE2_URI.'/'.$rel.'">':'<source data-src="'.SKYYROSE2_URI.'/'.$rel.'">';
  ck(str_contains(skyyrose2_media_filter_html($tag),$rel),'survives buffer');
 }
}
echo "PASS $n cinema boundary assertions\n";
