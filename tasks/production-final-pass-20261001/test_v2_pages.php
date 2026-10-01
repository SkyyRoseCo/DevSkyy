<?php
/** Offline WordPress CRUD model/fault tests; not authenticated WordPress evidence. */
define('SR_V2_PAGES_TEST',true); define('ARRAY_A','ARRAY_A');
define('EMPTY_TRASH_DAYS', (($argv[1] ?? '') === 'retention-zero') ? 0 : 30);
require __DIR__ . '/apply_v2_pages.php';
$posts=[]; $metadata=[]; $next=100; $writes=0; $fault=''; $home='https://skyyrose.co'; $style='skyyrose-flagship'; $theme_root_override=null;
function get_option($key) { global $home,$style; return $key === 'home' ? $home : $style; }
function get_theme_root() { global $theme_root_override; return $theme_root_override ?? dirname(__DIR__,2) . '/wordpress-theme'; }
function get_post($id,$format=null) { global $posts; return $posts[$id] ?? null; }
function get_post_status($id) { return get_post($id)['post_status'] ?? false; }
function get_post_meta($id,$key=null,$single=false) { global $metadata; if ($key === null) { return $metadata[$id] ?? []; } $v=$metadata[$id][$key] ?? []; return $single ? ($v[0] ?? '') : $v; }
function get_posts($args) { global $posts; return array_map(fn($p)=>(object)$p,array_values(array_filter($posts,fn($p)=>is_array($args['post_status']) ? in_array($p['post_status'],$args['post_status'],true) : $p['post_status']===$args['post_status']))); }
function get_page_uri($id) { $p=get_post($id); return ($p['post_parent'] ? get_page_uri($p['post_parent']) . '/' : '') . $p['post_name']; }
function is_wp_error($x) { return false; }
function wp_insert_post($data,$error=false) { global $posts,$metadata,$next,$writes,$fault; $writes++; $id=$next++; $meta=$data['meta_input']; unset($data['meta_input']); $posts[$id]=['ID'=>$id,...$data,'post_modified_gmt'=>'2026-10-01 00:00:00']; foreach($meta as $k=>$v){$metadata[$id][$k]=[$v];} if($fault==='insert'){throw new RuntimeException('transport secret should not be emitted');} return $id; }
function wp_update_post($data,$error=false) { global $posts,$writes,$fault; $writes++; $id=$data['ID']; $posts[$id]=array_merge($posts[$id],$data); if($fault==='publish'){throw new RuntimeException('secret');} return $id; }
function wp_trash_post($id) { global $posts,$writes; $writes++; $posts[$id]['post_status']='trash'; return (object)$posts[$id]; }
$assertions=0;
function assert_ok($condition,$message) { global $assertions; $assertions++; if(!$condition){throw new RuntimeException('ASSERT:' . $message);} }
function refuses($callback,$code) { try{$callback();}catch(RuntimeException $e){assert_ok($e->getMessage()===$code,$code . ' actual=' . $e->getMessage());return;}throw new RuntimeException('Expected refusal:' . $code); }
function reset_fixture() {
    global $posts,$metadata,$next,$writes,$fault,$home,$style,$theme_root_override;
    $posts=[];$metadata=[];$next=100;$writes=0;$fault='';$home='https://skyyrose.co';$style='skyyrose-flagship';$theme_root_override=null;
    foreach(['collections','pre-order','contact','shipping-returns','cart','checkout'] as $i=>$path){$id=$i+1;$posts[$id]=['ID'=>$id,'post_type'=>'page','post_status'=>'publish','post_name'=>$path,'post_title'=>$path,'post_parent'=>0,'post_content'=>'MERCHANT CONTENT','post_modified_gmt'=>'2026-10-01 00:00:00'];$metadata[$id]=['_wp_page_template'=>['skyyrose-canvas.php'],'unrelated'=>['retain']];}
    $inventory=sr_v2_page_inventory(SR_V2_PAGE_PATHS);
    $script=__DIR__ . '/plan_v2_pages.py';
    $input=tempnam(sys_get_temp_dir(),'sr-page-inventory-'); file_put_contents($input,json_encode($inventory));
    $output=$input . '.plan';
    $command='python3 ' . escapeshellarg($script) . ' ' . escapeshellarg($input) . ' ' . escapeshellarg($output) . ' --operation fixture';
    exec($command,$lines,$status);assert_ok($status===0,'planner fixture');
    $bytes=file_get_contents($output);unlink($input);unlink($output);
    return [json_decode($bytes,true),hash('sha256',$bytes)];
}
if (($argv[1] ?? '') === 'retention-zero') {
    // Separate process represents retention changing after a previously prepared set.
    [$plan,$sha]=reset_fixture();
    $dir=sys_get_temp_dir() . '/sr-retention-zero-' . bin2hex(random_bytes(6));mkdir($dir,0700);$journal=$dir . '/journal.json';
    $j=['schema'=>1,'home'=>$plan['home'],'operation'=>$plan['operation'],'plan_sha256'=>$sha,'status'=>'PREPARED','entries'=>[]];
    foreach($plan['changes'] as $c){$id=$next++;$parent=$c['parent_path']==='' ? 0 : ($j['entries'][$c['parent_path']]['id'] ?? $plan['existing_guards'][$c['parent_path']]['ID']);$posts[$id]=['ID'=>$id,'post_type'=>'page','post_status'=>'draft','post_name'=>basename($c['path']),'post_title'=>$c['title'],'post_content'=>$c['content'],'post_parent'=>$parent,'post_modified_gmt'=>'2026-10-01 00:00:00'];$metadata[$id]=['_wp_page_template'=>[$c['template']],SR_V2_PAGE_MARKER=>[$sha . ':fixture']];$j['entries'][$c['path']]=['id'=>$id,'created'=>true,'before'=>null,'state'=>'CONFIRMED','after'=>sr_v2_page_sha(sr_v2_page_snapshot($id))];}
    sr_v2_page_save($journal,$j,true);file_put_contents($journal . '.lock','');$before=[$posts,$metadata];
    refuses(fn()=>sr_v2_page_run($plan,$sha,'prepare',$dir . '/new.json'),'TRASH_RETENTION_REQUIRED');
    $style='skyyrose-flagship-2';refuses(fn()=>sr_v2_page_run($plan,$sha,'publish',$journal),'TRASH_RETENTION_REQUIRED');
    refuses(fn()=>sr_v2_page_run($plan,$sha,'rollback',$journal),'TRASH_RETENTION_REQUIRED');
    assert_ok($writes===0 && [$posts,$metadata]===$before && count($j['entries'])===10,'zero retention preserves whole ten-page set without WP writes');
    $r=sr_v2_page_run($plan,$sha,'reconcile',$journal);assert_ok($r['drift']['trash_retention']==='DISABLED_OR_INVALID' && $writes===0,'readonly reports disabled retention');
    foreach(glob($dir . '/*') as $file){unlink($file);}rmdir($dir);
    echo "PASS: zero-retention subprocess {$assertions} assertions; prepare/publish/rollback refused before any WordPress mutation; ten-page set retained; readonly observation available.\n";exit(0);
}
$dir=sys_get_temp_dir() . '/sr-v2-pages-' . bin2hex(random_bytes(6));mkdir($dir,0700);
[$plan,$sha]=reset_fixture(); $journal=$dir . '/success.json'; $before=[$posts,$metadata];
$result=sr_v2_page_run($plan,$sha,'prepare',$journal);assert_ok($result['status']==='PREPARED' && $writes===10,'ten drafts');
foreach(array_slice($posts,6,null,true) as $id=>$p){assert_ok($p['post_status']==='draft','no public V1 empty pages');assert_ok(sr_v2_page_owned($id,$sha . ':fixture'),'marker bound');}
foreach($before[0] as $id=>$p){assert_ok($posts[$id]===$p && $metadata[$id]===$before[1][$id],'existing unchanged');}
refuses(fn()=>sr_v2_page_run($plan,$sha,'publish',$journal),'THEME_PHASE');
$style='skyyrose-flagship-2';$result=sr_v2_page_run($plan,$sha,'publish',$journal);assert_ok($result['status']==='PUBLISHED' && $writes===20,'publish ten only');
assert_ok(count(array_filter(sr_v2_page_run($plan,$sha,'reconcile',$journal)['states'],fn($s)=>$s==='CONFIRMED'))===10,'fresh read-only confirmed');
$count=$writes;sr_v2_page_run($plan,$sha,'reconcile',$journal);assert_ok($writes===$count,'reconcile no writes');
refuses(fn()=>sr_v2_page_run($plan,$sha,'publish',$journal),'NO_WRITE_RETRY');
$metadata[100]['foreign']=['edit'];refuses(fn()=>sr_v2_page_run($plan,$sha,'rollback',$journal),'FOREIGN_EDIT_OR_UNKNOWN');
assert_ok($posts[100]['post_status']==='publish' && $writes===20,'foreign edited set entirely retained');
// New independent fixture: successful rollback trashes, never force-deletes.
[$plan,$sha]=reset_fixture();$journal=$dir . '/rollback.json';sr_v2_page_run($plan,$sha,'prepare',$journal);$style='skyyrose-flagship-2';sr_v2_page_run($plan,$sha,'publish',$journal);$result=sr_v2_page_run($plan,$sha,'rollback',$journal);assert_ok($result['status']==='ROLLED_BACK' && count($posts)===16,'created IDs retained in trash');
foreach(array_slice($posts,6,null,true) as $p){assert_ok($p['post_status']==='trash','safe trash');}
assert_ok(count(array_filter(sr_v2_page_run($plan,$sha,'reconcile',$journal)['states'],fn($s)=>$s==='ROLLED_BACK_CONFIRMED'))===10,'readonly safe rollback reconciled');
[$plan,$sha]=reset_fixture();$home='https://wrong.example';refuses(fn()=>sr_v2_page_run($plan,$sha,'prepare',$dir . '/target.json'),'TARGET_DRIFT');assert_ok($writes===0,'wrong target no mutation');
[$plan,$sha]=reset_fixture();$plan['source_hashes']['page.php']=str_repeat('0',64);refuses(fn()=>sr_v2_page_run($plan,$sha,'prepare',$dir . '/source.json'),'INSTALLED_SOURCE_MISMATCH');assert_ok($writes===0,'source no mutation');
[$plan,$sha]=reset_fixture();unset($plan['source_hashes']['template-collection.php']);refuses(fn()=>sr_v2_page_run($plan,$sha,'prepare',$dir . '/missing-template.json'),'SOURCE_BINDING');assert_ok($writes===0,'missing template pin before writes');
[$plan,$sha]=reset_fixture();$posts[1]['post_content']='merchant changed';refuses(fn()=>sr_v2_page_run($plan,$sha,'prepare',$dir . '/drift.json'),'EXISTING_PAGE_DRIFT');assert_ok($writes===0,'merchant edit preserved');
[$plan,$sha]=reset_fixture();$plan['changes'][]=$plan['changes'][0];refuses(fn()=>sr_v2_page_run($plan,$sha,'prepare',$dir . '/duplicate.json'),'PATH_ALLOWLIST');
[$plan,$sha]=reset_fixture();$posts[99]=array_merge($posts[1],['ID'=>99]);refuses(fn()=>sr_v2_page_run($plan,$sha,'prepare',$dir . '/duplicate-path.json'),'DUPLICATE_PATH');
[$plan,$sha]=reset_fixture();$posts[99]=array_merge($posts[1],['ID'=>99,'post_name'=>'worlds__trashed','post_status'=>'trash']);$metadata[99]=['_wp_desired_post_slug'=>['worlds']];refuses(fn()=>sr_v2_page_run($plan,$sha,'prepare',$dir . '/trash.json'),'TRASH_PATH_CONFLICT');
[$plan,$sha]=reset_fixture();$posts[99]=array_merge($posts[1],['ID'=>99,'post_name'=>'worlds-2']);refuses(fn()=>sr_v2_page_run($plan,$sha,'prepare',$dir . '/suffix.json'),'SUFFIXED_PATH_CONFLICT');
[$plan,$sha]=reset_fixture();$plan['changes'][4]['content']='invented';refuses(fn()=>sr_v2_page_run($plan,$sha,'prepare',$dir . '/copy.json'),'WORLD_BODY_BINDING');
[$plan,$sha]=reset_fixture();$journal=$dir . '/claimed.json';file_put_contents($journal,'already claimed');refuses(fn()=>sr_v2_page_run($plan,$sha,'prepare',$journal),'JOURNAL_EXISTS');assert_ok($writes===0,'prewrite journal claim failure');
[$plan,$sha]=reset_fixture();$journal=$dir . '/unknown.json';$fault='insert';refuses(fn()=>sr_v2_page_run($plan,$sha,'prepare',$journal),'UNKNOWN_READ_ONLY_RECONCILE_REQUIRED');assert_ok($writes===1,'one ambiguous insert only');$fault='';refuses(fn()=>sr_v2_page_run($plan,$sha,'publish',$journal),'THEME_PHASE');$style='skyyrose-flagship-2';refuses(fn()=>sr_v2_page_run($plan,$sha,'publish',$journal),'NO_WRITE_RETRY');$count=$writes;$r=sr_v2_page_run($plan,$sha,'reconcile',$journal);assert_ok($writes===$count && $r['states']['collections/signature']==='CONFLICT_OR_UNKNOWN','unknown read-only no retry');
[$plan,$sha]=reset_fixture();$journal=$dir . '/journal-binding.json';sr_v2_page_run($plan,$sha,'prepare',$journal);$count=$writes;refuses(fn()=>sr_v2_page_run($plan,str_repeat('f',64),'reconcile',$journal),'JOURNAL_BINDING');assert_ok($writes===$count,'wrong journal binding no writes');
[$plan,$sha]=reset_fixture();$journal=$dir . '/unknown-publish.json';sr_v2_page_run($plan,$sha,'prepare',$journal);$style='skyyrose-flagship-2';$fault='publish';refuses(fn()=>sr_v2_page_run($plan,$sha,'publish',$journal),'UNKNOWN_READ_ONLY_RECONCILE_REQUIRED');$count=$writes;$fault='';refuses(fn()=>sr_v2_page_run($plan,$sha,'publish',$journal),'NO_WRITE_RETRY');$r=sr_v2_page_run($plan,$sha,'reconcile',$journal);assert_ok($writes===$count && $r['observed']['collections/signature']['post_status']==='publish' && $r['states']['collections/signature']==='CONFLICT_OR_UNKNOWN','ambiguous publish readonly observed');
// Recovery remains available after unrelated merchant/theme/source changes.
[$plan,$sha]=reset_fixture();$journal=$dir . '/recovery.json';sr_v2_page_run($plan,$sha,'prepare',$journal);$style='skyyrose-flagship-2';sr_v2_page_run($plan,$sha,'publish',$journal);
$posts[1]['post_content']='NEW MERCHANT EDIT';$metadata[2]['merchant']=['NEW'];$preserve=[$posts[1],$metadata[2]];$style='replacement-after-rollback';$theme_root_override=$dir . '/missing-theme';
$before_journal=file_get_contents($journal);$before_lock=fileperms($journal . '.lock') & 0777;chmod($journal . '.lock',0440);chmod($dir,0550);$count=$writes;
$r=sr_v2_page_run($plan,$sha,'reconcile',$journal);
assert_ok($r['drift']['existing_pages']['collections']==='DRIFT' && $r['drift']['source']['page.php']==='DRIFT_OR_MISSING' && $r['drift']['stylesheet']==='replacement-after-rollback','reconcile reports unrelated drift');
assert_ok($writes===$count && file_get_contents($journal)===$before_journal && (fileperms($journal . '.lock') & 0777)===0440,'readonly no journal/lock mutation or writable directory needed');
chmod($dir,0700);chmod($journal . '.lock',$before_lock);
$r=sr_v2_page_run($plan,$sha,'rollback',$journal);assert_ok($r['status']==='ROLLED_BACK','owned cleanup despite unrelated drift');
assert_ok([$posts[1],$metadata[2]]===$preserve,'merchant edits survive cleanup');
foreach(array_slice($posts,6,null,true) as $p){assert_ok($p['post_status']==='trash','drift cleanup only our pages');}
// A changed OWNED page remains a refusal even when unrelated source checks are relaxed.
[$plan,$sha]=reset_fixture();$journal=$dir . '/owned-conflict.json';sr_v2_page_run($plan,$sha,'prepare',$journal);$posts[100]['post_content']='foreign edit';$theme_root_override=$dir . '/missing-theme';$style='other-theme';$count=$writes;
$r=sr_v2_page_run($plan,$sha,'reconcile',$journal);assert_ok($r['states']['collections/signature']==='CONFLICT_OR_UNKNOWN','owned edit visible');
refuses(fn()=>sr_v2_page_run($plan,$sha,'rollback',$journal),'FOREIGN_EDIT_OR_UNKNOWN');assert_ok($writes===$count && $posts[100]['post_content']==='foreign edit','owned edit refuses all cleanup');
// Read-only reconciliation never creates a missing lock.
unlink($journal . '.lock');refuses(fn()=>sr_v2_page_run($plan,$sha,'reconcile',$journal),'JOURNAL_BUSY');assert_ok(!file_exists($journal . '.lock'),'readonly missing lock remains absent');
$retention_command=escapeshellarg(PHP_BINARY) . ' ' . escapeshellarg(__FILE__) . ' retention-zero';
exec($retention_command,$retention_output,$retention_status);assert_ok($retention_status===0,'separate zero-retention regression');echo implode("\n",$retention_output) . "\n";
// Clean up only this disposable offline fixture directory, never remote pages.
foreach(glob($dir . '/*') as $file){unlink($file);}rmdir($dir);
echo "PASS: {$assertions} assertions; guarded draft/publish, preserved existing pages, read-only reconcile, safe trash rollback, target/source/duplicate/copy/durability/unknown/foreign-edit refusals (offline WP model).\n";
