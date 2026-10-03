<?php
$expected='https://staging-7e48-skyyrose.wpcomstaging.com';
if(get_option('home')!==$expected || get_option('stylesheet')!=='skyyrose-flagship-2') {throw new RuntimeException('STAGING_IDENTITY_DRIFT');}
$root=get_stylesheet_directory(); $files=array();
$it=new RecursiveIteratorIterator(new RecursiveDirectoryIterator($root,FilesystemIterator::SKIP_DOTS));
foreach($it as $file) {if($file->isLink()) {throw new RuntimeException('UNQUALIFIED_SYMLINK');} if($file->isFile()) {$relative=substr($file->getPathname(),strlen($root)+1); $files[$relative]=array('sha256'=>hash_file('sha256',$file->getPathname()),'bytes'=>$file->getSize(),'mode'=>sprintf('%04o',$file->getPerms()&0777));}}
ksort($files); echo wp_json_encode(array('target'=>$expected,'stylesheet'=>get_option('stylesheet'),'version'=>wp_get_theme()->get('Version'),'utc'=>gmdate('c'),'files'=>$files,'count'=>count($files)),JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES);
