'use strict';
// Harmless Python/Node ownership controls. No Chromium or network execution.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const cp = require('node:child_process');
const { processes } = require('./context-ownership.cjs');
const { PYTHON, image, inspectBroker, acknowledge, takeover, closeRegistered, closeAll } = require('./context-broker.cjs');
const { cleanGroup } = require('./capability.cjs');
const { pin, sources, LAUNCHER, NODE } = require('./context.cjs');
const ROOT = path.resolve(__dirname, '../../..');
const BASE = path.join(ROOT, '.artifacts/release-gates-20261019/gate4-private-collector-context');
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
function save(file, data) { fs.writeFileSync(file, JSON.stringify(data, null, 2) + '\n', { flag: 'wx', mode: 0o600 }); }
async function until(test, ms = 5000) { const end = Date.now() + ms; while (Date.now() < end) { if (test()) return; await pause(10); } throw Error('Control deadline'); }
const targetCode = `const fs=require('fs'),cp=require('child_process');const f=process.env.SR_CONTEXT_FOLDER;const identity=fd=>{const s=fs.fstatSync(fd);return {device:s.dev,inode:s.ino,type:s.mode&61440}};fs.writeSync(3,JSON.stringify({kind:'synthetic-ready',pid:process.pid,pipes:{3:identity(3),4:identity(4)}})+'\n');const input=fs.readFileSync(4,'utf8');let child=null;if(process.env.SR_CONTROL_LEADER_EXIT==='yes'){const c=cp.spawn(process.execPath,['-e','setInterval(()=>{},1000)'],{detached:false,stdio:'ignore',env:{PATH:'/usr/bin:/bin'}});child=c.pid;c.unref()}fs.writeFileSync(f+'/target-proof.json',JSON.stringify({pid:process.pid,input,child}),{flag:'wx',mode:384});process.exit(child?41:0)`;
async function main() {
  assert.equal(fs.realpathSync(process.execPath), fs.realpathSync(NODE)); fs.mkdirSync(BASE, { recursive: true, mode: 0o700 }); const root = path.join(BASE, 'broker-controls-' + Date.now()); fs.mkdirSync(root, { mode: 0o700 });
  const report = { status: 'INCOMPLETE', authentication: 'NOT_APPLICABLE', no_browser_or_network: true, source_start: sources(), runtime_start: { node: pin(NODE), python: pin(PYTHON) }, controls: [], cleanup: [] }; const owned = [];
  const begin = async (label, options = {}) => {
    const folder = path.join(root, label); fs.mkdirSync(folder, { mode: 0o700 }); fs.mkdirSync(path.join(folder, 'tmp'), { mode: 0o700 }); const profile = path.join(folder, 'tmp', 'profile'); fs.mkdirSync(profile, { mode: 0o700 });
    const nonce = crypto.randomUUID(); const target = options.target || NODE; const targetSHA = pin(target).sha256; const args = ['-e', targetCode, '--', '--user-data-dir=' + profile, '--remote-debugging-pipe'];
    if (options.stale) save(path.join(folder, 'broker-ack.json'), { kind: 'stale', nonce: 'foreign' });
    // Invoke the exact no-fork run function with a harmless target; main's fixed
    // Chromium binding is deliberately never invoked by these controls.
    const code = "import importlib.util,pathlib,sys; p=sys.argv[1]; s=importlib.util.spec_from_file_location('owned_broker',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); m.run(pathlib.Path(sys.argv[2]),sys.argv[3],pathlib.Path(sys.argv[4]),sys.argv[5],sys.argv[6:],deadline=5)";
    const output = fs.openSync(path.join(folder, 'process.txt'), 'wx', 0o600);
    const child = cp.spawn(PYTHON, ['-I', '-c', code, LAUNCHER, target, targetSHA, folder, nonce, ...args], { detached: true, env: { PATH: '/usr/bin:/bin', LANG: 'C', SR_CONTEXT_FOLDER: folder, SR_CONTROL_LEADER_EXIT: options.leaderExit ? 'yes' : 'no' }, stdio: ['ignore', output, output, 'pipe', 'pipe'] }); fs.closeSync(output);
    const entry = { child, folder, nonce, target, targetSHA, args, profile, record: null, terminal: null, frames: '', released: false }; owned.push(entry);
    child.stdio[3].on('data', data => { entry.frames += data; assert.ok(Buffer.byteLength(entry.frames) < 65536); }); child.stdio[4].on('error', () => {});
    entry.done = new Promise((resolve, reject) => { child.once('error', reject); child.once('close', (code, signal) => { entry.terminal = { code, signal }; resolve(entry.terminal); }); });
    entry.spawned = { kind: 'browser-spawn', token: nonce, pid: child.pid, executable: LAUNCHER, profile, args };
    if (!options.stale) { await until(() => fs.existsSync(path.join(folder, 'broker-registration.json')) || entry.terminal); assert.ok(!entry.terminal, 'Broker stopped before registration'); }
    return entry;
  };
  const register = entry => { entry.record = inspectBroker(entry.folder, LAUNCHER, entry.target, entry.targetSHA, process.pid, entry.nonce, entry.spawned); return entry.record; };
  const ackValue = entry => ({ kind: 'pre-exec-ack', nonce: entry.nonce, pid: entry.child.pid, group: entry.child.pid, registration_sha256: entry.record.registration_sha256 });
  const rejectCase = async (label, mutate, options = {}) => {
    const entry = await begin(label, options); if (!options.stale) register(entry); if (mutate) await mutate(entry); const terminal = await entry.done;
    assert.notEqual(terminal.code, 0); assert.ok(!fs.existsSync(path.join(entry.folder, 'target-proof.json'))); assert.equal(entry.frames, '');
    const closed = entry.record ? await closeRegistered(entry.record, entry.folder) : await cleanGroup(entry.child, entry.folder); assert.ok(closed.stopped && !closed.errors.length); entry.cleaned = true;
    report.controls.push({ label, status: 'PASS_ACTUAL_HARMLESS_BROKER_REFUSED_NO_TARGET_EXEC', terminal });
  };
  try {
    await rejectCase('missing-ack', null);
    await rejectCase('stale-ack', null, { stale: true });
    await rejectCase('wrong-nonce', entry => save(path.join(entry.folder, 'broker-ack.json'), { ...ackValue(entry), nonce: crypto.randomUUID() }));
    await rejectCase('truncated-ack', entry => fs.writeFileSync(path.join(entry.folder, 'broker-ack.json'), '{', { flag: 'wx', mode: 0o600 }));
    await rejectCase('oversized-ack', entry => fs.writeFileSync(path.join(entry.folder, 'broker-ack.json'), Buffer.alloc(4097, 65), { flag: 'wx', mode: 0o600 }));
    await rejectCase('fifo-ack', entry => cp.execFileSync(PYTHON, ['-I', '-c', 'import os,sys;os.mkfifo(sys.argv[1],0o600)', path.join(entry.folder, 'broker-ack.json')], { timeout: 3000 }));
    await rejectCase('symlink-ack', entry => { const file = path.join(entry.folder, 'other'); save(file, ackValue(entry)); fs.symlinkSync(file, path.join(entry.folder, 'broker-ack.json')); });
    await rejectCase('duplicate-ack-field', entry => fs.writeFileSync(path.join(entry.folder, 'broker-ack.json'), JSON.stringify(ackValue(entry)).replace('{', '{"nonce":"foreign",') + '\n', { flag: 'wx', mode: 0o600 }));
    await rejectCase('registration-tamper', entry => { const file = path.join(entry.folder, 'broker-registration.json'); const row = JSON.parse(fs.readFileSync(file)); row.environment_sha256 = 'f'.repeat(64); fs.writeFileSync(file, JSON.stringify(row) + '\n'); save(path.join(entry.folder, 'broker-ack.json'), { ...ackValue(entry), registration_sha256: pin(file).sha256 }); });
    const malformed = await begin('missing-passive-registration'); assert.throws(() => inspectBroker(malformed.folder, LAUNCHER, NODE, pin(NODE).sha256, process.pid, malformed.nonce, null)); await malformed.done; assert.equal(malformed.frames, ''); assert.ok(!fs.existsSync(path.join(malformed.folder, 'target-proof.json'))); malformed.record = null; const absent = await cleanGroup(malformed.child, malformed.folder); assert.ok(absent.stopped && !absent.errors.length); malformed.cleaned = true; report.controls.push({ label: 'missing-passive-registration', status: 'PASS_NO_ACK_NO_TARGET_EXEC' });
    const privateTarget = path.join(root, 'private-target'); fs.writeFileSync(privateTarget, '#!/bin/sh\nexit 0\n', { flag: 'wx', mode: 0o600 });
    await rejectCase('failed-exec-after-registration', entry => { entry.released = true; acknowledge(entry.record, entry.folder); }, { target: privateTarget });
    await rejectCase('target-pin-drift', entry => { fs.writeFileSync(privateTarget, 'changed executable bytes'); entry.released = true; acknowledge(entry.record, entry.folder); }, { target: privateTarget });
    const positive = await begin('pipe-preservation'); const record = register(positive); positive.released = true; acknowledge(record, positive.folder); positive.takeover = await takeover(record); await until(() => positive.frames.includes('\n'));
    const frame = JSON.parse(positive.frames.trim()); assert.equal(frame.pid, record.pid); for (const fd of ['3', '4']) { const { inheritable, ...expected } = record.pipes[fd]; assert.equal(inheritable, true); assert.deepEqual(frame.pipes[fd], expected); }
    positive.child.stdio[4].end('synthetic-cdp-pipe-preserved'); assert.equal((await positive.done).code, 0); const proof = JSON.parse(fs.readFileSync(path.join(positive.folder, 'target-proof.json'))); assert.equal(proof.input, 'synthetic-cdp-pipe-preserved'); assert.equal(proof.pid, record.pid); const positiveClosed = await closeRegistered(record, positive.folder); assert.ok(positiveClosed.stopped && !positiveClosed.errors.length); positive.cleaned = true; report.controls.push({ label: 'actual-same-pid-group-image-and-fd3-fd4-exec-preservation', status: 'PASS_HARMLESS_NODE_EXEC_ONLY', record, takeover: positive.takeover, proof });
    const leader = await begin('leader-exit-profileless-descendant', { leaderExit: true }); register(leader); leader.released = true; acknowledge(leader.record, leader.folder); await takeover(leader.record); leader.child.stdio[4].end('exit-leader'); assert.equal((await leader.done).code, 41);
    const orphan = JSON.parse(fs.readFileSync(path.join(leader.folder, 'target-proof.json'))); const survivor = processes().find(row => row.pid === orphan.child); assert.ok(survivor && survivor.group === leader.record.group && !survivor.command.includes(leader.folder) && !survivor.command.includes('--user-data-dir'));
    const recovered = await closeRegistered(leader.record, leader.folder); assert.ok(recovered.stopped && recovered.errors.includes('Owned group required SIGTERM')); leader.cleaned = true; report.cleanup.push(recovered); report.controls.push({ label: 'registered-leader-exit-with-profileless-samegroup-descendant', status: 'PASS_ACTUAL_PRODUCTION_CLOSE_REGISTERED_PATH', survivor });
    const first = await begin('independent-cleanup-first'); register(first); first.released = true; acknowledge(first.record, first.folder); await takeover(first.record); const second = await begin('independent-cleanup-second'); register(second); second.released = true; acknowledge(second.record, second.folder); await takeover(second.record);
    const attempted = []; const batch = await closeAll([first.record, second.record], root, async (row, folder) => { attempted.push(row.pid); if (row.pid === first.record.pid) throw Error('Synthetic first cleanup failure'); return closeRegistered(row, folder); }); assert.deepEqual(attempted, [first.record.pid, second.record.pid]); assert.equal(batch.errors.length, 1); assert.ok(batch.results[0].stopped && batch.results[0].errors.includes('Owned group required SIGTERM')); second.cleaned = true; const firstClosed = await closeRegistered(first.record, first.folder); assert.ok(firstClosed.stopped); first.cleaned = true; report.cleanup.push(batch, firstClosed); report.controls.push({ label: 'earlier-group-cleanup-error-does-not-suppress-later-group', status: 'PASS_ACTUAL_CLOSE_ALL_INDEPENDENCE' });
    report.status = 'PASS_HARMLESS_PRE_EXEC_OWNERSHIP_CONTROLS_ONLY';
  } catch (error) { report.status = 'FAIL_HARMLESS_BROKER_CONTROLS'; report.failure = { type: error.name, message: error.message }; process.exitCode = 1; }
  finally {
    for (const entry of owned.filter(row => !row.cleaned)) {
      try { if (!entry.record) { const current = processes().find(row => row.pid === entry.child.pid); if (current) assert.ok(current.group === current.pid && current.command.includes(entry.folder) && image(current.pid) === fs.realpathSync(PYTHON)); }
        const closed = entry.record ? await closeRegistered(entry.record, entry.folder) : await cleanGroup(entry.child, entry.folder); report.cleanup.push(closed); assert.ok(closed.stopped); }
      catch (error) { report.cleanup.push({ stopped: false, error: error.message }); report.status = 'FAIL_CONTROL_CLEANUP'; process.exitCode = 1; }
    }
    try { report.source_end = sources(); report.runtime_end = { node: pin(NODE), python: pin(PYTHON) }; assert.deepEqual(report.source_end, report.source_start); assert.deepEqual(report.runtime_end, report.runtime_start); assert.ok(!processes().some(row => row.command.includes(root)), 'Owned control process survived'); } catch (error) { report.status = 'FAIL_CONTROL_FINAL_BOUNDARY'; report.final_error = error.message; process.exitCode = 1; } save(path.join(root, 'results.json'), report); console.log(JSON.stringify({ status: report.status, folder: root }));
  }
}
main().catch(error => { console.error(JSON.stringify({ status: 'FAIL_BROKER_CONTROL_ENTRY', error_type: error.name })); process.exitCode = 1; });
