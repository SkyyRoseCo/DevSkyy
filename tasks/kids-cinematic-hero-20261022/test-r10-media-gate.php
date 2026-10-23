<?php
define('ABSPATH',__DIR__.'/');define('SKYYROSE2_DIR',realpath($argv[1]));define('SKYYROSE2_MEDIA_AUTHORING',true);
function add_action(...$a){} function add_filter(...$a){}
require SKYYROSE2_DIR.'/inc/v2-media-eligibility.php';
$inventory=skyyrose2_media_inventory();$results=[];
foreach(['hero.mp4','hero.webm','poster.webp'] as $name){$path='assets/video/collection-heroes/approved/kids-capsule/runway-r10/'.$name;$r=$inventory['assets'][$path];$role=$r['roles'][0];
$tests=['valid'=>skyyrose2_media_record_allowed($path,$r,$role),'product_role_refused'=>!skyyrose2_media_record_allowed($path,$r,'card_front'),'product_sku_refused'=>!skyyrose2_media_record_allowed($path,$r,$role,'kids-001')];
$x=$r;$x['sha256']=str_repeat('0',64);$tests['record_hash_drift_refused']=!skyyrose2_media_record_allowed($path,$x,$role);
$x=$r;$x['authorization']['sha256']=str_repeat('0',64);$tests['receipt_hash_drift_refused']=!skyyrose2_media_record_allowed($path,$x,$role);
$x=$r;$x['roles'][]='card_front';$tests['additional_role_refused']=!skyyrose2_media_record_allowed($path,$x,$role);
$x=$r;$x['collections']=['signature'];$tests['collection_drift_refused']=!skyyrose2_media_record_allowed($path,$x,$role);
$results[$name]=$tests;if(in_array(false,$tests,true))throw new RuntimeException('Gate case failed');}
echo json_encode(['scope'=>'OFFLINE_SOURCE_GATE_NO_AUTHENTICATION','status'=>'PASS','cases'=>$results],JSON_PRETTY_PRINT);
