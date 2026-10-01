<?php
/** Page-only guarded CRUD. Load via wp eval-file with plan, expected SHA, phase, journal. */
const SR_V2_PAGE_PATHS = ['collections','collections/signature','collections/black-rose','collections/love-hurts','collections/kids-capsule','worlds','worlds/signature','worlds/black-rose','worlds/love-hurts','worlds/kids-capsule','size-guide','pre-order','contact','shipping-returns','cart','checkout'];
const SR_V2_NEW_PATHS = ['collections/signature','collections/black-rose','collections/love-hurts','collections/kids-capsule','worlds','worlds/signature','worlds/black-rose','worlds/love-hurts','worlds/kids-capsule','size-guide'];
const SR_V2_PAGE_MARKER = '_skyyrose2_release_page';
function sr_v2_page_fail($code) { throw new RuntimeException($code); }
function sr_v2_page_snapshot($id) {
    $p = get_post($id, ARRAY_A);
    if (!$p || $p['post_type'] !== 'page') { sr_v2_page_fail('PAGE_IDENTITY'); }
    $meta = get_post_meta($id); ksort($meta);
    return ['post' => $p, 'meta' => $meta];
}
function sr_v2_page_sha($snapshot) { return hash('sha256', json_encode($snapshot, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE)); }
function sr_v2_page_inventory($paths) {
    $result = array_fill_keys($paths, null); $all = [];
    $statuses = function_exists('get_post_stati') ? array_values(get_post_stati()) : ['publish','future','draft','pending','private','trash','auto-draft','inherit'];
    foreach (get_posts(['post_type'=>'page','post_status'=>$statuses,'numberposts'=>-1,'suppress_filters'=>true]) as $post) {
        $path = trim(get_page_uri($post->ID), '/');
        $parent = $post->post_parent ? trim(get_page_uri($post->post_parent), '/') . '/' : '';
        $desired = get_post_meta($post->ID,'_wp_desired_post_slug',true);
        $all[] = ['ID'=>(int)$post->ID,'path'=>$path,'post_name'=>$post->post_name,'post_parent'=>(int)$post->post_parent,'post_status'=>$post->post_status,'trashed_slug'=>$desired];
        $original = $parent . ($desired !== '' ? $desired : preg_replace('/__trashed(?:-[0-9]+)?$/D','',$post->post_name));
        if ($post->post_status === 'trash' && (array_key_exists($path,$result) || array_key_exists($original,$result))) { sr_v2_page_fail('TRASH_PATH_CONFLICT'); }
        // Never accept WordPress's automatic slug suffix as a successful new route.
        foreach ($paths as $expected) { if (preg_match('~^' . preg_quote($expected,'~') . '-[0-9]+$~D',$path)) { sr_v2_page_fail('SUFFIXED_PATH_CONFLICT'); } }
        if (!array_key_exists($path, $result)) { continue; }
        if ($result[$path] !== null) { sr_v2_page_fail('DUPLICATE_PATH'); }
        $snapshot = sr_v2_page_snapshot($post->ID);
        $result[$path] = ['ID'=>(int)$post->ID,'path'=>$path,'post_type'=>$post->post_type,'post_status'=>$post->post_status,'snapshot_sha256'=>sr_v2_page_sha($snapshot),'template_values'=>$snapshot['meta']['_wp_page_template'] ?? []];
    }
    return ['home'=>get_option('home'),'stylesheet'=>get_option('stylesheet'),'pages'=>$result,'all_page_paths'=>$all];
}
function sr_v2_page_validate($plan) {
    if (($plan['schema'] ?? null) !== 1 || ($plan['home'] ?? '') !== 'https://skyyrose.co' || !preg_match('/^[a-zA-Z0-9_-]{1,80}$/D', $plan['operation'] ?? '') || ($plan['source_sha'] ?? '') !== '299f694702ac2dcc61a0f30aa34e4b3ef12f9118' || ($plan['zip_sha256'] ?? '') !== '47c485f0001434b7dd52f572812df02e3e103631902a16e86f92ffea407b5a16') { sr_v2_page_fail('PLAN_BINDING'); }
    $paths = array_column($plan['changes'] ?? [], 'path');
    if ($paths !== SR_V2_NEW_PATHS) { sr_v2_page_fail('PATH_ALLOWLIST'); }
    $ids = [];
    foreach ($plan['changes'] as $c) {
        $slug = basename($c['path']);
        $template = str_starts_with($c['path'], 'collections/') ? 'template-collection.php' : (str_starts_with($c['path'], 'worlds/') ? 'template-immersive-' . $slug . '.php' : 'default');
        if (($c['template'] ?? '') !== $template || ($c['parent_path'] ?? null) !== (dirname($c['path']) === '.' ? '' : dirname($c['path'])) || !is_string($c['title'] ?? null) || !array_key_exists('before',$c)) { sr_v2_page_fail('PAGE_DEFINITION'); }
        if ($c['before'] !== null || !is_string($c['content'] ?? null)) { sr_v2_page_fail('ABSENT_PAGE_INVALID'); }
        if ($c['path'] === 'worlds' && (($plan['worlds_body_sha256'] ?? '') !== '2a62b0f0f49633e63dd37c40d5075d9a54047b5c9c63c0c438e72cad194d5ab5' || hash('sha256',$c['content']) !== $plan['worlds_body_sha256'])) { sr_v2_page_fail('WORLD_BODY_BINDING'); }
        if ($c['path'] === 'size-guide' && hash('sha256',$c['content']) !== '62fa2ac6eda70f5d8119753ae2a62c3b1353c9ec01619741f03215d147d1dd4f') { sr_v2_page_fail('SIZE_GUIDE_SOURCE_BINDING'); }
        if (!in_array($c['path'],['worlds','size-guide'],true) && $c['content'] !== '') { sr_v2_page_fail('UNREVIEWED_COPY'); }
    }
    $guards = array_values(array_diff(SR_V2_PAGE_PATHS,SR_V2_NEW_PATHS));
    if (array_keys($plan['existing_guards'] ?? []) !== $guards) { sr_v2_page_fail('EXISTING_GUARDS_REQUIRED'); }
    foreach ($plan['existing_guards'] as $path=>$before) {
        if (!is_array($before) || ($before['path'] ?? '') !== $path || !is_int($before['ID'] ?? null) || $before['ID'] < 1 || isset($ids[$before['ID']]) || ($before['post_type'] ?? '') !== 'page' || ($before['post_status'] ?? '') !== 'publish' || !preg_match('/^[a-f0-9]{64}$/D',$before['snapshot_sha256'] ?? '')) { sr_v2_page_fail('PREIMAGE_INVALID'); }
        $ids[$before['ID']] = true;
    }
    foreach ($plan['source_hashes'] ?? [] as $file=>$hash) {
        if (!preg_match('~^(page\.php|inc/presentation-registry\.php|template-(collection|immersive-(signature|black-rose|love-hurts|kids-capsule))\.php)$~D',$file) || !preg_match('/^[a-f0-9]{64}$/D',$hash)) { sr_v2_page_fail('SOURCE_BINDING'); }
    }
    foreach (array_merge(['inc/presentation-registry.php','page.php'], ['template-collection.php','template-immersive-signature.php','template-immersive-black-rose.php','template-immersive-love-hurts.php','template-immersive-kids-capsule.php']) as $file) { if (!isset($plan['source_hashes'][$file])) { sr_v2_page_fail('SOURCE_BINDING'); } }
}
function sr_v2_page_guard($plan, $phase) {
    if (get_option('home') !== $plan['home']) { sr_v2_page_fail('TARGET_DRIFT'); }
    $retention = defined('EMPTY_TRASH_DAYS') && is_int(EMPTY_TRASH_DAYS) && EMPTY_TRASH_DAYS > 0;
    if ($phase !== 'reconcile' && !$retention) { sr_v2_page_fail('TRASH_RETENTION_REQUIRED'); }
    $strict = in_array($phase,['prepare','publish'],true);
    $style = get_option('stylesheet');
    $drift = ['stylesheet'=>$style,'trash_retention'=>$retention ? 'ENABLED' : 'DISABLED_OR_INVALID','source'=>[],'existing_pages'=>[]];
    if ($strict && (($phase === 'prepare' && $style !== 'skyyrose-flagship') || ($phase === 'publish' && $style !== 'skyyrose-flagship-2'))) { sr_v2_page_fail('THEME_PHASE'); }
    try {
        $inventory = sr_v2_page_inventory(array_keys($plan['existing_guards']))['pages'];
        foreach ($plan['existing_guards'] as $path=>$before) {
            $same = $inventory[$path] === $before;
            $drift['existing_pages'][$path] = $same ? 'UNCHANGED' : 'DRIFT';
            if ($strict && !$same) { sr_v2_page_fail('EXISTING_PAGE_DRIFT'); }
        }
    } catch (RuntimeException $e) {
        if ($strict) { throw $e; }
        $drift['existing_pages'] = ['inventory'=>'CONFLICT'];
    }
    $theme = get_theme_root() . '/skyyrose-flagship-2';
    foreach ($plan['source_hashes'] as $file=>$hash) {
        $same = is_file($theme . '/' . $file) && hash_equals($hash, hash_file('sha256',$theme . '/' . $file));
        $drift['source'][$file] = $same ? 'UNCHANGED' : 'DRIFT_OR_MISSING';
        if ($strict && !$same) { sr_v2_page_fail('INSTALLED_SOURCE_MISMATCH'); }
    }
    return $drift;
}
function sr_v2_page_save($file, $journal, $exclusive=false) {
    $data = json_encode($journal, JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE) . "\n";
    if ($exclusive) {
        $claim = @fopen($file,'x');
        if (!$claim) { sr_v2_page_fail('JOURNAL_EXISTS'); }
        chmod($file,0600); fclose($claim);
    }
    $temp = $file . '.tmp-' . bin2hex(random_bytes(8));
    $handle = @fopen($temp,'x');
    if (!$handle) { sr_v2_page_fail('JOURNAL_OPEN'); }
    chmod($temp,0600);
    if (fwrite($handle,$data) !== strlen($data) || !fflush($handle) || !fsync($handle)) { fclose($handle); sr_v2_page_fail('JOURNAL_DURABILITY'); }
    fclose($handle);
    if (!rename($temp,$file)) { sr_v2_page_fail('JOURNAL_RENAME'); }
    $directory = fopen(dirname($file),'r');
    if (!$directory || !fsync($directory)) { if ($directory) { fclose($directory); } sr_v2_page_fail('JOURNAL_DIRECTORY_DURABILITY'); }
    fclose($directory);
}
function sr_v2_page_read($file, $sha, $plan) {
    $j = json_decode(file_get_contents($file), true);
    if (!is_array($j) || ($j['plan_sha256'] ?? '') !== $sha || ($j['operation'] ?? '') !== $plan['operation'] || ($j['home'] ?? '') !== $plan['home']) { sr_v2_page_fail('JOURNAL_BINDING'); }
    return $j;
}
function sr_v2_page_owned($id, $marker) { return get_post_meta($id,SR_V2_PAGE_MARKER,true) === $marker; }
function sr_v2_page_run_locked($plan, $sha, $phase, $journal_file) {
    sr_v2_page_validate($plan);
    if (!in_array($phase,['prepare','publish','reconcile','rollback'],true)) { sr_v2_page_fail('PHASE_INVALID'); }
    $drift = sr_v2_page_guard($plan,$phase);
    $marker = $sha . ':' . $plan['operation'];
    if ($phase === 'prepare') {
        $inventory = sr_v2_page_inventory(SR_V2_PAGE_PATHS)['pages'];
        foreach ($plan['changes'] as $c) { if ($inventory[$c['path']] !== $c['before']) { sr_v2_page_fail('PREIMAGE_DRIFT'); } }
        $j = ['schema'=>1,'home'=>$plan['home'],'operation'=>$plan['operation'],'plan_sha256'=>$sha,'status'=>'PREPARING','entries'=>[]];
        sr_v2_page_save($journal_file,$j,true);
    } else { $j = sr_v2_page_read($journal_file,$sha,$plan); }
    if ($phase === 'reconcile') {
        $result = []; $observed = [];
        foreach ($plan['changes'] as $c) {
            $entry = $j['entries'][$c['path']] ?? null;
            if ($entry && isset($entry['id']) && get_post($entry['id'])) {
                $snapshot = sr_v2_page_snapshot($entry['id']);
                $current = ['ID'=>$entry['id'],'post_status'=>get_post_status($entry['id']),'snapshot_sha256'=>sr_v2_page_sha($snapshot)];
            } else { $current = sr_v2_page_inventory([$c['path']])['pages'][$c['path']]; }
            $observed[$c['path']] = $current === null ? null : ['id'=>$current['ID'],'post_status'=>$current['post_status'],'owned'=>sr_v2_page_owned($current['ID'],$marker),'snapshot_sha256'=>$current['snapshot_sha256']];
            $result[$c['path']] = $current === null ? 'ABSENT' : ($entry && isset($entry['after']) && $current['ID'] === $entry['id'] && sr_v2_page_sha(sr_v2_page_snapshot($entry['id'])) === $entry['after'] ? ($current['post_status'] === 'trash' ? 'ROLLED_BACK_CONFIRMED' : 'CONFIRMED') : ($c['before'] !== null && $current === $c['before'] ? 'OLD' : 'CONFLICT_OR_UNKNOWN'));
        }
        return ['status'=>'READ_ONLY','journal_status'=>$j['status'],'states'=>$result,'observed'=>$observed,'drift'=>$drift];
    }
    if ($phase === 'publish' && ($j['status'] ?? '') !== 'PREPARED') { sr_v2_page_fail('NO_WRITE_RETRY'); }
    if ($phase === 'rollback' && !in_array($j['status'] ?? '', ['PREPARED','PUBLISHED','UNKNOWN'],true)) { sr_v2_page_fail('ROLLBACK_STATE'); }
    if ($phase === 'publish' || $phase === 'rollback') {
        // Reject the whole set before the first mutation if any page is uncertain or edited.
        foreach ($plan['changes'] as $c) {
            $entry = $j['entries'][$c['path']] ?? null;
            if ($phase === 'rollback' && !$entry) { continue; }
            if (!$entry || !isset($entry['after'],$entry['id']) || !($entry['created'] ?? false) || sr_v2_page_sha(sr_v2_page_snapshot($entry['id'])) !== $entry['after'] || !sr_v2_page_owned($entry['id'],$marker)) { sr_v2_page_fail('FOREIGN_EDIT_OR_UNKNOWN'); }
        }
    }
    $changes = $phase === 'rollback' ? array_reverse($plan['changes']) : $plan['changes'];
    foreach ($changes as $c) {
        $path = $c['path']; $entry = $j['entries'][$path] ?? null;
        if ($phase === 'rollback' && !$entry) { continue; }
        try {
            sr_v2_page_guard($plan,$phase);
            if ($phase !== 'prepare') {
                if (!$entry || !isset($entry['after']) || sr_v2_page_sha(sr_v2_page_snapshot($entry['id'])) !== $entry['after'] || ($entry['created'] && !sr_v2_page_owned($entry['id'],$marker))) { sr_v2_page_fail('FOREIGN_EDIT_OR_UNKNOWN'); }
            }
            $parent_id = $c['parent_path'] === '' ? 0 : ($j['entries'][$c['parent_path']]['id'] ?? ($plan['existing_guards'][$c['parent_path']]['ID'] ?? 0));
            if ($c['parent_path'] !== '' && !$parent_id) { sr_v2_page_fail('PARENT_MISSING'); }
            $j['entries'][$path] = array_merge($entry ?? [],['state'=>'DISPATCHED','phase'=>$phase]);
            sr_v2_page_save($journal_file,$j); // Must be durable BEFORE every mutation.
            if ($phase === 'prepare') {
                if (sr_v2_page_inventory([$path])['pages'][$path] !== null) { sr_v2_page_fail('PATH_RACE'); }
                $id = wp_insert_post(['post_type'=>'page','post_status'=>'draft','post_name'=>basename($path),'post_title'=>$c['title'],'post_content'=>$c['content'],'post_parent'=>$parent_id,'meta_input'=>['_wp_page_template'=>$c['template'],SR_V2_PAGE_MARKER=>$marker]],true);
                if (is_wp_error($id) || !$id) { sr_v2_page_fail('INSERT_UNKNOWN'); }
                $j['entries'][$path] = ['id'=>(int)$id,'created'=>true,'before'=>null,'state'=>'CONFIRMED'];
                if (!sr_v2_page_owned($id,$marker) || get_page_uri($id) !== $path || get_post_status($id) !== 'draft' || get_post($id,ARRAY_A)['post_content'] !== $c['content'] || get_post($id,ARRAY_A)['post_title'] !== $c['title'] || get_post_meta($id,'_wp_page_template',true) !== $c['template'] || (int)get_post($id,ARRAY_A)['post_parent'] !== $parent_id) { sr_v2_page_fail('INSERT_READBACK'); }
            } elseif ($phase === 'publish') {
                $id = $entry['id'];
                $result = wp_update_post(['ID'=>$id,'post_status'=>'publish'],true); if (is_wp_error($result) || !$result) { sr_v2_page_fail('PUBLISH_UNKNOWN'); }
                if (get_post_status($id) !== 'publish' || get_page_uri($id) !== $path || get_post_meta($id,'_wp_page_template',true) !== $c['template'] || get_post($id,ARRAY_A)['post_content'] !== $c['content'] || get_post($id,ARRAY_A)['post_title'] !== $c['title']) { sr_v2_page_fail('PUBLISH_READBACK'); }
                $j['entries'][$path]['state'] = 'CONFIRMED';
            } else {
                $id = $entry['id'];
                if (!wp_trash_post($id)) { sr_v2_page_fail('TRASH_UNKNOWN'); }
                if (get_post_status($id) !== 'trash') { sr_v2_page_fail('ROLLBACK_READBACK'); }
                $j['entries'][$path]['state'] = 'ROLLED_BACK';
            }
            $id = $j['entries'][$path]['id'];
            $j['entries'][$path]['after'] = sr_v2_page_sha(sr_v2_page_snapshot($id));
            sr_v2_page_save($journal_file,$j);
        } catch (Throwable $e) {
            $j['status'] = 'UNKNOWN';
            try { sr_v2_page_save($journal_file,$j); } catch (Throwable $ignored) { /* Original durable DISPATCHED record remains; read-only reconciliation required. */ }
            sr_v2_page_fail('UNKNOWN_READ_ONLY_RECONCILE_REQUIRED');
        }
    }
    $j['status'] = ['prepare'=>'PREPARED','publish'=>'PUBLISHED','rollback'=>'ROLLED_BACK'][$phase];
    sr_v2_page_save($journal_file,$j);
    return ['status'=>$j['status'],'count'=>count($j['entries']),'plan_sha256'=>$sha,'drift'=>$drift];
}
function sr_v2_page_run($plan, $sha, $phase, $journal_file) {
    // One nonblocking lock covers the complete operation, including reconciliation.
    if (is_link($journal_file) || is_link($journal_file . '.lock')) { sr_v2_page_fail('JOURNAL_SYMLINK'); }
    $read_only = $phase === 'reconcile';
    $lock = @fopen($journal_file . '.lock',$read_only ? 'r' : 'c');
    if (!$lock || !flock($lock,($read_only ? LOCK_SH : LOCK_EX)|LOCK_NB)) { if ($lock) { fclose($lock); } sr_v2_page_fail('JOURNAL_BUSY'); }
    if (!$read_only) { chmod($journal_file . '.lock',0600); }
    try { return sr_v2_page_run_locked($plan,$sha,$phase,$journal_file); }
    finally { flock($lock,LOCK_UN); fclose($lock); }
}
if (!defined('SR_V2_PAGES_TEST') && isset($args)) {
    try {
        if (count($args) === 1 && $args[0] === 'inventory') { echo json_encode(sr_v2_page_inventory(SR_V2_PAGE_PATHS),JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE) . "\n"; }
        else {
            if (count($args) !== 4 || !preg_match('/^[a-f0-9]{64}$/D',$args[1])) { sr_v2_page_fail('CLI_ARGUMENTS'); }
            $bytes = file_get_contents($args[0]);
            if (!hash_equals($args[1],hash('sha256',$bytes))) { sr_v2_page_fail('PLAN_SHA_MISMATCH'); }
            echo json_encode(sr_v2_page_run(json_decode($bytes,true),$args[1],$args[2],$args[3]),JSON_UNESCAPED_SLASHES) . "\n";
        }
    } catch (Throwable $e) { echo json_encode(['status'=>'REFUSED_OR_UNKNOWN','code'=>preg_match('/^[A-Z0-9_]+$/D',$e->getMessage()) ? $e->getMessage() : 'SANITIZED_FAILURE']) . "\n"; exit(1); }
}
