'use strict';
// Separate executors on the explicitly isolated fixture; never a remote DB.
const fs = require('node:fs');
const path = require('node:path');
const { spawn, spawnSync } = require('node:child_process');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '../../..');
const fixture = path.join(root, '.artifacts/release-gates-20261019/runtime-official/wordpress');
const processDir = path.join(root, '.artifacts/release-gates-20261019/runtime-official/process');
const out = path.join(root, 'tasks/release-gates-20261019/evidence/process-recovery-woo-11.2.1');
fs.mkdirSync(processDir, { recursive: true }); fs.mkdirSync(out, { recursive: true });
const worker = path.join(root, 'wordpress-theme/skyyrose-flagship-2/tests/commerce/migration-process.php');
const args = mode => ['-d', 'error_reporting=24575', '/opt/homebrew/bin/wp', '--path=' + fixture, 'eval-file', worker, mode];
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
function run(file, mode, expected = 0) {
  const result = spawnSync('php', args(mode), { cwd: root, env: { ...process.env, SR_MIGRATION_CASE_FILE: file }, encoding: 'utf8' });
  fs.writeFileSync(path.join(out, path.basename(file) + '-' + mode + '.txt'), result.stdout + result.stderr);
  assert.equal(result.status, expected, result.stderr || result.stdout);
  return JSON.parse(result.stdout);
}
async function hold(file) {
  const output = fs.openSync(path.join(out, path.basename(file) + '-old-writer.txt'), 'w');
  const child = spawn('php', args('hold'), { cwd: root, env: { ...process.env, SR_MIGRATION_CASE_FILE: file }, stdio: ['ignore', output, output] });
  fs.closeSync(output);
  const done = new Promise(resolve => child.on('close', (code, signal) => resolve({ code, signal })));
  const deadline = Date.now() + 20000;
  while (!fs.existsSync(file + '.checkpoint')) { assert.ok(Date.now() < deadline, 'old writer reached checkpoint'); await delay(50); }
  return { child, done, checkpoint: JSON.parse(fs.readFileSync(file + '.checkpoint')) };
}
(async () => {
  const mutationLock = path.join(fixture, '.sr-release-mutation-lock');
  fs.mkdirSync(mutationLock);
  try {
  const results = [];
  for (const mode of ['process-kill', 'connection-loss']) {
    const file = path.join(processDir, `${Date.now()}-${mode}.json`);
    run(file, 'prepare');
    const old = await hold(file);
    assert.equal(run(file, 'apply', 3).ok, false);
    const before = run(file, 'probe');
    assert.equal(before.state, 'IN_PROGRESS'); assert.equal(before.ordinary_payment_blocked, true); assert.deepEqual(before.children, []);
    if (mode === 'process-kill') { old.child.kill('SIGKILL'); await old.done; }
    else {
      const killed = spawnSync('/opt/homebrew/bin/mariadb', ['--no-defaults', '--socket=/tmp/sr-release-01a0f768.sock', '-uroot', '-e', `KILL CONNECTION ${Number(old.checkpoint.connection_id)}`], { encoding: 'utf8' });
      assert.equal(killed.status, 0, killed.stderr);
    }
    const successor = run(file, 'resume');
    assert.equal(successor.state, 'COMPLETE'); assert.equal(successor.children.length, 6);
    const stable = run(file, 'probe');
    if (mode === 'connection-loss') { fs.writeFileSync(file + '.release', 'release'); await old.done; }
    const after = run(file, 'probe');
    assert.equal(after.snapshot_sha256, stable.snapshot_sha256); assert.equal(after.writer_token, stable.writer_token);
    results.push({ case: mode, status: 'PASS', loser_denied: true, fresh_incomplete_guard: true, unknown_history_payment_blocked: true, successor_children: successor.children.length, stale_writer_no_further_mutation: true, old_writer_exit: await old.done });
  }
  const file = path.join(processDir, `${Date.now()}-inside-child-save.json`);
  run(file, 'prepare'); assert.equal(run(file, 'orphan', 3).ok, false);
  const orphan = run(file, 'probe'); assert.equal(orphan.state, 'FAILED'); assert.equal(orphan.children.length, 1); assert.equal(orphan.ordinary_payment_blocked, true);
  assert.equal(run(file, 'resume', 3).ok, false);
  const after = run(file, 'probe'); assert.equal(after.snapshot_sha256, orphan.snapshot_sha256);
  results.push({ case: 'inside-child-save', status: 'PASS_FAIL_CLOSED_MANUAL_REPAIR_REQUIRED', guard_retained: true, orphan_not_adopted_or_deleted: true });
  fs.writeFileSync(path.join(out, 'results.json'), JSON.stringify({ classification: 'REPRODUCED_LOCAL_NATIVE', authentication: 'NOT_APPLICABLE', status: 'PASS', results }, null, 2) + '\n');
  console.log(JSON.stringify(results));
  } finally { fs.rmdirSync(mutationLock); }
})().catch(error => { console.error(error); process.exitCode = 1; });
