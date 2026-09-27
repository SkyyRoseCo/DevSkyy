<?php
if (home_url()!=='https://staging-7e48-skyyrose.wpcomstaging.com'){throw new Exception('Wrong environment');}
$root=get_stylesheet_directory().'/woocommerce/';$results=[];
foreach(new RecursiveIteratorIterator(new RecursiveDirectoryIterator($root,FilesystemIterator::SKIP_DOTS)) as $file){if($file->getExtension()!=='php')continue;$rel=substr($file->getPathname(),strlen($root));$native=WC()->plugin_path().'/templates/'.$rel;$own=file_get_contents($file->getPathname());$core=is_file($native)?file_get_contents($native):'';preg_match('/@version\s+(\S+)/',$own,$a);preg_match('/@version\s+(\S+)/',$core,$b);$results[]=['template'=>$rel,'override_version'=>$a[1]??null,'core_version'=>$b[1]??null,'core_exists'=>is_file($native)];}
echo wp_json_encode(['home'=>home_url(),'woocommerce'=>WC_VERSION,'templates'=>$results],JSON_PRETTY_PRINT);
