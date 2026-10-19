'use strict';
// Explicit prospective synthetic reconciliation. Never production/staging.
const fs = require('node:fs'); const path = require('node:path'); const crypto = require('node:crypto');
const assert = require('node:assert/strict'); const { spawnSync, spawn } = require('node:child_process');
const root = path.resolve(__dirname, '../../..'); const fixture = path.join(root, '.artifacts/release-gates-20261019/runtime-official/wordpress');
const dir = path.join(root, '.artifacts/release-gates-20261019/runtime-official/owned-repair'); fs.mkdirSync(dir, { recursive: true });
const out = path.join(root, 'tasks/release-gates-20261019/owned-repair/evidence'); fs.mkdirSync(out, { recursive: true });
const worker = path.join(root, 'tools/v2-runtime/fixture-owned-child-repair.php'); const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const args = mode => ['-d', 'error_reporting=24575', '/opt/homebrew/bin/wp', '--path=' + fixture, 'eval-file', worker, mode];
const report = { classification: 'REPRODUCED_PROSPECTIVE_PRIVATE_FIXTURE_REPAIR_ONLY', authentication: 'NOT_APPLICABLE', delivered_runtime_source: 'd953e51ee9e01448fe6b04960d5958d8ac424954', delivered_evidence: 'aa0652dc4269e3c79b86d939e7b630783a63a148', source_pins: Object.fromEntries([worker, __filename, path.join(root, 'tools/v2-runtime/variation-migration-core.php'), path.join(root, 'wordpress-theme/skyyrose-flagship-2/inc/woocommerce-compat.php')].map(p => [path.relative(root, p), sha(fs.readFileSync(p))])), cases: [], limits: ['Prospective instrumented synthetic operation only; old unreceipted orphan never repaired', 'No general production/staging recovery implementation or conversion authority', 'Unexplained native drift or unrecorded partial repair remains manual investigation', 'No child deletion, order rewrite or automatic repair-to-resume transition', 'Driver supplies simulated explicit review approval envelopes; not independent human approval of each receipt'] };
const runID = Date.now(); report.run_id = runID;
let serial = 0;
function run(file, mode, expected = 0, extra = {}) {
  const result = spawnSync('php', args(mode), { cwd: root, env: { ...process.env, SR_OWNED_REPAIR_CASE: file, ...extra }, encoding: 'utf8' });
  fs.writeFileSync(path.join(out, path.basename(file) + '-' + (++serial) + '-' + mode + '.txt'), result.stdout + result.stderr);
  assert.equal(result.status, expected, result.stdout + result.stderr);
  const data = JSON.parse(result.stdout); assert.equal(data.ok, expected === 0); return data;
}
const inspect = file => run(file, 'inspect');
function approval(file, observed = inspect(file)) {
  const bytes = fs.existsSync(file + '.receipt') ? fs.readFileSync(file + '.receipt') : Buffer.from('absent');
  fs.writeFileSync(file + '.approval', JSON.stringify({ scope: 'EXPLICIT_REVIEWED_SYNTHETIC_OWNED_CHILD_ONLY', receipt_sha256: sha(bytes), preimage_sha256: observed.preimage_sha256 }), { mode: 0o600 }); return observed;
}
function mutate(file, code) {
  const guard = "if (!defined('SKYYROSE_RELEASE_SYNTHETIC_FIXTURE') || !SKYYROSE_RELEASE_SYNTHETIC_FIXTURE || DB_NAME!=='sr_release_fixture' || get_option('home')!=='http://127.0.0.1:18362') throw new RuntimeException('fixture only'); $d=json_decode(file_get_contents(getenv('SR_OWNED_REPAIR_CASE')),true); $id=(int)$d['row']['id'];";
  const result = spawnSync('php', ['-d', 'error_reporting=24575', '/opt/homebrew/bin/wp', '--path=' + fixture, 'eval', guard + code], { cwd: root, env: { ...process.env, SR_OWNED_REPAIR_CASE: file }, encoding: 'utf8' }); assert.equal(result.status, 0, result.stdout + result.stderr);
}
function fresh(label, mode = 'capture', extra = {}) {
  const file = path.join(dir, Date.now() + '-' + label + '.json'); run(file, 'prepare', 0, extra); run(file, mode, 3, extra);
  const current = inspect(file); assert.equal(current.state.migration.value.state, 'FAILED'); assert.equal(Object.keys(current.state.children).length, 1); assert.equal(current.payment_blocked, true); assert.equal(current.order_identity_money_unchanged, true); return file;
}
function refused(label, file, before = inspect(file), mode = 'approved-repair') {
  const failure = run(file, mode, 3); const after = inspect(file); assert.equal(after.preimage_sha256, before.preimage_sha256); assert.equal(after.payment_blocked, true);
  report.cases.push({ label, status: 'PASS_REFUSED_WITHOUT_MUTATION', reason: failure.error });
}
function receiptEdit(file, fn) {
  const receipt = JSON.parse(fs.readFileSync(file + '.receipt')); fn(receipt); fs.writeFileSync(file + '.receipt', JSON.stringify(receipt));
  fs.writeFileSync(file + '.receipt.verified', JSON.stringify({ receipt_sha256: sha(fs.readFileSync(file + '.receipt')), case_nonce: receipt.case_nonce }));
}
function separatelyResume(label, file) {
  const current = inspect(file); assert.equal(current.state.migration.value.state, 'FAILED'); assert.equal(current.state.repair.value.state, 'REPAIRED_AWAITING_REVIEW'); assert.equal(current.payment_blocked, true);
  fs.writeFileSync(file + '.resume-approval', JSON.stringify({ snapshot_sha256: current.snapshot_sha256, preimage_sha256: current.preimage_sha256, repair_journal_sha256: sha(Buffer.from(current.state.repair.raw)) }), { mode: 0o600 });
  const completed = run(file, 'core-resume'); assert.equal(completed.state, 'COMPLETE'); assert.equal(completed.children.length, 6); assert.equal(completed.outer_lock_retained_after_core_release, true); assert.equal(completed.lock_free_after_balanced_release, true); assert.equal(completed.last_native_sync_barriers_verified, true);
  assert.ok(completed.children.includes(Object.values(current.state.children)[0].post.ID * 1), 'same proven child retained, not deleted/replaced');
  const after = inspect(file); assert.equal(after.order_identity_money_unchanged, true);
  report.cases.push({ label, status: 'PASS_EXPLICIT_REPAIR_REVIEW_SEPARATE_RESUME', children: 6, original_child_retained: true, order_identity_money_unchanged: true });
}
(async () => {
  const lock = path.join(fixture, '.sr-release-mutation-lock'); fs.mkdirSync(lock);
  try {
    let file = fresh('unreceipted', 'unreceipted'); approval(file); refused('unreceipted orphan stays refused', file);
    file = fresh('readback-failure', 'capture', { SR_OWNED_RECEIPT_READBACK_FAIL: '1' }); approval(file); refused('unacknowledged receipt readback failure', file);
    file = path.join(dir, Date.now() + '-persistence-failure.json'); run(file, 'prepare'); fs.writeFileSync(file + '.receipt', 'pre-existing unavailable receipt'); run(file, 'capture', 3); approval(file); refused('exclusive receipt persistence failure', file);
    for (const [label, change] of [['forged-update-flag', r => { r.update = true; }], ['wrong-parent', r => { r.child.post.post_parent = String(Number(r.child.post.post_parent) + 1); }], ['wrong-child-id', r => { r.child_id += 1; }]]) {
      file = fresh(label); receiptEdit(file, change); approval(file); refused(label, file);
    }
    file = fresh('wrong-receipt-sha'); approval(file); const bad = JSON.parse(fs.readFileSync(file + '.approval')); bad.receipt_sha256 = '0'.repeat(64); fs.writeFileSync(file + '.approval', JSON.stringify(bad)); refused('wrong approved receipt digest', file);
    file = fresh('stale-preimage'); approval(file); mutate(file, "global $wpdb;$child=(int)$wpdb->get_var($wpdb->prepare(\"SELECT ID FROM {$wpdb->posts} WHERE post_parent=%d AND post_type='product_variation'\",$id));wp_update_post(array('ID'=>$child,'post_title'=>'Synthetic drift'));" );
    refused('stale reviewed native preimage', file);
    file = fresh('child-drift'); mutate(file, "global $wpdb;$child=(int)$wpdb->get_var($wpdb->prepare(\"SELECT ID FROM {$wpdb->posts} WHERE post_parent=%d AND post_type='product_variation'\",$id));wp_update_post(array('ID'=>$child,'post_title'=>'Unexplained drift'));" ); approval(file); refused('fresh approval cannot legitimize unexplained child drift', file);
    file = fresh('journal-drift'); mutate(file, "$name='skyyrose_v2_phase2_variations_'.$id;$j=get_option($name);$j['unexpected']='synthetic drift';update_option($name,$j,false);" ); approval(file); refused('migration journal drift with unchanged product rows', file);
    file = fresh('second-orphan'); mutate(file, "$v=new WC_Product_Variation();$v->set_parent_id($id);$v->save();" ); approval(file); refused('unexpected second orphan', file);
    file = fresh('raw-parent-meta-drift'); mutate(file, "add_post_meta($id,'_price','unexpected duplicate',false);" ); approval(file); refused('raw-only parent metadata drift', file);
    file = fresh('raw-lookup-drift'); mutate(file, "global $wpdb;$wpdb->update($wpdb->prefix.'wc_product_meta_lookup',array('stock_quantity'=>99),array('product_id'=>$id));" ); approval(file); refused('raw-only product lookup drift', file);
    file = fresh('explicit-success'); approval(file); const repaired = run(file, 'approved-repair'); assert.equal(repaired.migration_state, 'FAILED'); assert.equal(repaired.resume_automatically_called, false); separatelyResume('reviewed owned child completion', file);
    for (const race of ['repair-journal', 'raw-lookup']) {
      file = fresh('resume-race-' + race); approval(file); run(file, 'approved-repair'); const current = inspect(file);
      fs.writeFileSync(file + '.resume-approval', JSON.stringify({ snapshot_sha256: current.snapshot_sha256, preimage_sha256: current.preimage_sha256, repair_journal_sha256: sha(Buffer.from(current.state.repair.raw)) }));
      const fd = fs.openSync(path.join(out, 'resume-race-' + race + '-' + runID + '.txt'), 'w'); const active = spawn('php', args('core-resume'), { cwd: root, env: { ...process.env, SR_OWNED_REPAIR_CASE: file, SR_OWNED_RESUME_HOLD_BEFORE_LOCK: '1' }, stdio: ['ignore', fd, fd] }); fs.closeSync(fd);
      const finished = new Promise(resolve => active.on('close', code => resolve(code))); const end = Date.now() + 15000; while (!fs.existsSync(file + '.resume-hold')) { assert.ok(Date.now() < end); await new Promise(resolve => setTimeout(resolve, 50)); }
      mutate(file, race === 'repair-journal' ? "$name='sr_fixture_owned_repair_'.$id;$j=get_option($name);$j['unexpected']='intervening';update_option($name,$j,false);" : "global $wpdb;$wpdb->update($wpdb->prefix.'wc_product_meta_lookup',array('stock_quantity'=>88),array('product_id'=>$id));");
      const drifted = inspect(file); fs.writeFileSync(file + '.resume-release', 'release'); assert.equal(await finished, 3); assert.equal(inspect(file).preimage_sha256, drifted.preimage_sha256); assert.equal(inspect(file).payment_blocked, true);
      report.cases.push({ label: 'resume lock-time review rejects intervening ' + race + ' drift', status: 'PASS_REFUSED_WITHOUT_MUTATION' });
    }
    file = fresh('foreign-sync', 'capture', { SR_OWNED_CREATE_FOREIGN: '1' }); approval(file);
    const foreignID = JSON.parse(fs.readFileSync(file)).foreign_id;
    const foreignRead = () => spawnSync('php', ['-d', 'error_reporting=24575', '/opt/homebrew/bin/wp', '--path=' + fixture, 'eval', "$id=" + Number(foreignID) + ";global $wpdb;echo wp_json_encode(array($wpdb->get_row($wpdb->prepare(\"SELECT * FROM {$wpdb->posts} WHERE ID=%d\",$id),ARRAY_A),$wpdb->get_results($wpdb->prepare(\"SELECT * FROM {$wpdb->postmeta} WHERE post_id=%d ORDER BY meta_id\",$id),ARRAY_A),$wpdb->get_row($wpdb->prepare(\"SELECT * FROM {$wpdb->prefix}wc_product_meta_lookup WHERE product_id=%d\",$id),ARRAY_A)));"], { cwd: root, encoding: 'utf8' });
    const foreignBefore = foreignRead(); assert.equal(foreignBefore.status, 0); run(file, 'approved-repair', 3, { SR_OWNED_QUEUE_FOREIGN_PARENT: String(foreignID) }); assert.equal(foreignRead().stdout, foreignBefore.stdout); assert.equal(inspect(file).payment_blocked, true);
    report.cases.push({ label: 'reentrant foreign parent queue refused before foreign product mutation', status: 'PASS', foreign_native_rows_unchanged: true });
    file = fresh('core-sync-failure'); approval(file); run(file, 'approved-repair'); const syncBefore = inspect(file);
    fs.writeFileSync(file + '.resume-approval', JSON.stringify({ snapshot_sha256: syncBefore.snapshot_sha256, preimage_sha256: syncBefore.preimage_sha256, repair_journal_sha256: sha(Buffer.from(syncBefore.state.repair.raw)) }));
    run(file, 'core-resume', 3, { SR_OWNED_FORCE_SYNC_FAILURE: '1' }); const syncFailed = inspect(file); assert.equal(syncFailed.state.migration.value.state, 'FAILED'); assert.equal(syncFailed.payment_blocked, true);
    report.cases.push({ label: 'native sync failure occurs before COMPLETE and retains migration guard', status: 'PASS' }); separatelyResume('fresh reviewed core resume after native sync failure', file);
    for (const stage of ['save', 'legacy']) for (const target of ['same', 'foreign']) {
      file = fresh('final-' + stage + '-' + target, 'capture', { SR_OWNED_CREATE_FOREIGN: '1' }); approval(file); run(file, 'approved-repair'); const current = inspect(file);
      const foreignID = JSON.parse(fs.readFileSync(file)).foreign_id;
      const foreignRead = () => spawnSync('php', ['-d', 'error_reporting=24575', '/opt/homebrew/bin/wp', '--path=' + fixture, 'eval', "$id=" + Number(foreignID) + ";global $wpdb;echo wp_json_encode(array($wpdb->get_row($wpdb->prepare(\"SELECT * FROM {$wpdb->posts} WHERE ID=%d\",$id),ARRAY_A),$wpdb->get_results($wpdb->prepare(\"SELECT * FROM {$wpdb->postmeta} WHERE post_id=%d ORDER BY meta_id\",$id),ARRAY_A),$wpdb->get_row($wpdb->prepare(\"SELECT * FROM {$wpdb->prefix}wc_product_meta_lookup WHERE product_id=%d\",$id),ARRAY_A)));"], { cwd: root, encoding: 'utf8' });
      const untouched = foreignRead(); assert.equal(untouched.status, 0);
      fs.writeFileSync(file + '.resume-approval', JSON.stringify({ snapshot_sha256: current.snapshot_sha256, preimage_sha256: current.preimage_sha256, repair_journal_sha256: sha(Buffer.from(current.state.repair.raw)) }));
      run(file, 'core-resume', 3, { SR_OWNED_FINAL_QUEUE_STAGE: stage, SR_OWNED_FINAL_QUEUE_TARGET: target }); const failed = inspect(file); assert.equal(failed.state.migration.value.state, 'FAILED'); assert.equal(failed.payment_blocked, true); assert.equal(foreignRead().stdout, untouched.stdout);
      report.cases.push({ label: 'final sync-and-readback ' + stage + ' hook queues ' + target + ' parent before COMPLETE', status: 'PASS_REFUSED_GUARD_RETAINED', foreign_native_rows_unchanged: true });
      separatelyResume('fresh reviewed resume after final ' + stage + '-' + target + ' queue refusal', file);
    }
    file = fresh('repair-interruption'); approval(file); run(file, 'approved-repair', 3, { SR_OWNED_REPAIR_STOP_AFTER_SAVE: '1' }); const interrupted = inspect(file); assert.equal(interrupted.payment_blocked, true); assert.equal(interrupted.state.repair.value.state, 'IN_PROGRESS');
    approval(file); refused('ordinary repair retry cannot take over incomplete claim', file, inspect(file));
    approval(file); run(file, 'approved-repair-resume'); separatelyResume('durable repaired afterimage requires fresh review before resume', file);
    file = fresh('competing-connection'); approval(file);
    const log = fs.openSync(path.join(out, 'held-repair-' + runID + '.txt'), 'w'); const child = spawn('php', args('approved-repair'), { cwd: root, env: { ...process.env, SR_OWNED_REPAIR_CASE: file, SR_OWNED_REPAIR_HOLD: '1' }, stdio: ['ignore', log, log] }); fs.closeSync(log);
    const done = new Promise(resolve => child.on('close', (code, signal) => resolve({ code, signal }))); const deadline = Date.now() + 20000;
    while (!fs.existsSync(file + '.hold')) { assert.ok(Date.now() < deadline); await new Promise(resolve => setTimeout(resolve, 50)); }
    approval(file); refused('competing repair executor denied', file);
    const held = JSON.parse(fs.readFileSync(file + '.hold')); const killed = spawnSync('/opt/homebrew/bin/mariadb', ['--no-defaults', '--socket=/tmp/sr-release-01a0f768.sock', '-uroot', '-e', 'KILL CONNECTION ' + Number(held.connection_id)], { encoding: 'utf8' }); assert.equal(killed.status, 0, killed.stderr);
    approval(file); run(file, 'approved-repair-resume'); const stable = inspect(file); fs.writeFileSync(file + '.release', 'release'); const dead = await done; assert.ok([1, 3].includes(dead.code), 'lost native connection exits nonzero'); assert.equal(inspect(file).preimage_sha256, stable.preimage_sha256);
    report.cases.push({ label: 'lost connection stale repair executor cannot mutate after reviewed takeover', status: 'PASS' }); separatelyResume('separate reviewed resume after repair connection loss', file);
    assert.equal(report.cases.length, 32);
    report.status = 'PASS_PROSPECTIVE_FIXTURE_ONLY';
  } finally { fs.rmdirSync(lock); fs.writeFileSync(path.join(out, 'results.json'), JSON.stringify(report, null, 2) + '\n'); }
  console.log(JSON.stringify({ status: report.status, cases: report.cases.length }));
})().catch(error => { console.error(error); process.exitCode = 1; });
