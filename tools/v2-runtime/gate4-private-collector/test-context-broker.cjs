'use strict';
// Harmless Python/Node ownership controls. No Chromium or network execution.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const cp = require('node:child_process');
const { processes } = require('./context-ownership.cjs');
const { PYTHON, PYTHON_SHA, PYTHON_IMAGE, PYTHON_IMAGE_SHA, readRegular, inspectBroker, acknowledge, takeover, closeRegistered, closeAll, observeTerminal, stopWorkerAndCloseUnacked } = require('./context-broker.cjs');
const { cleanGroup } = require('./capability.cjs');
const { pin, sources, LAUNCHER, NODE } = require('./context.cjs');
const ROOT = path.resolve(__dirname, '../../..');
const BASE = path.join(ROOT, '.artifacts/release-gates-20261019/gate4-private-collector-context');
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
function save(file, data) { fs.writeFileSync(file, JSON.stringify(data, null, 2) + '\n', { flag: 'wx', mode: 0o600 }); }
async function until(test, ms = 5000) { const end = Date.now() + ms; while (Date.now() < end) { if (test()) return; await pause(10); } throw Error('Control deadline'); }
const targetCode = String.raw`const fs=require('fs'),cp=require('child_process');const f=process.env.SR_CONTEXT_FOLDER;const identity=fd=>{const s=fs.fstatSync(fd,{bigint:true});return {device:BigInt.asIntN(32,s.dev).toString(),raw_device_signed:s.dev.toString(),inode:s.ino.toString(),type:Number(s.mode&61440n)}};fs.writeSync(3,JSON.stringify({kind:'synthetic-ready',pid:process.pid,pipes:{3:identity(3),4:identity(4)}})+'\n');const input=fs.readFileSync(4,'utf8');let child=null;if(process.env.SR_CONTROL_LEADER_EXIT==='yes'){const c=cp.spawn(process.execPath,['-e','setInterval(()=>{},1000)'],{detached:false,stdio:'ignore',env:{PATH:'/usr/bin:/bin'}});child=c.pid;c.unref()}fs.writeFileSync(f+'/target-proof.json',JSON.stringify({pid:process.pid,input,child}),{flag:'wx',mode:384});process.exit(child?41:0)`;
const brokerRunner = String.raw`import pathlib,sys,types,hashlib,json,os,traceback
p=pathlib.Path(sys.argv[1]); body=p.read_bytes(); source_sha=hashlib.sha256(body).hexdigest()
if source_sha != sys.argv[6]: raise ValueError('Broker source pin mismatch')
m=types.ModuleType('owned_broker'); m.__file__=str(p)
exec(compile(body,str(p),'exec'),m.__dict__)
try:
 m.run(pathlib.Path(sys.argv[2]),sys.argv[3],pathlib.Path(sys.argv[4]),sys.argv[5],sys.argv[8:],deadline=float(sys.argv[7]))
except Exception as error:
 leaf=traceback.extract_tb(error.__traceback__)[-1]
 value={'status':'REFUSED_BEFORE_TARGET_EXEC','exception_type':type(error).__name__,'message':str(error),'errno':getattr(error,'errno',None),'leaf_file':leaf.filename,'leaf_function':leaf.name,'leaf_line':leaf.lineno,'source_sha256':source_sha}
 fd=os.open(pathlib.Path(sys.argv[4])/'broker-refusal.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'w') as stream: stream.write(json.dumps(value)+'\n')
 sys.exit(71)
`;
function preservedPipes(record, frame) {
  assert.equal(frame.pid, record.pid); assert.deepEqual(Object.keys(frame.pipes).sort(), ['3', '4']);
  for (const fd of ['3', '4']) {
    const { inheritable, ...expected } = record.pipes[fd]; const { raw_device_signed, ...actual } = frame.pipes[fd];
    assert.equal(inheritable, true); assert.match(raw_device_signed, /^-?(?:0|[1-9][0-9]*)$/);
    assert.equal(BigInt(raw_device_signed).toString(), raw_device_signed); assert.ok(BigInt(raw_device_signed) >= -(1n << 63n) && BigInt(raw_device_signed) < (1n << 63n));
    assert.match(expected.device, /^-?(?:0|[1-9][0-9]*)$/); assert.equal(BigInt(expected.device).toString(), expected.device); assert.ok(BigInt(expected.device) >= -(1n << 31n) && BigInt(expected.device) < (1n << 31n));
    assert.equal(raw_device_signed, expected.device); assert.deepEqual(actual, expected);
  }
}
async function main() {
  new (require('node:vm').Script)(targetCode, { filename: 'harmless-node-target.js' });
  assert.equal(fs.realpathSync(process.execPath), fs.realpathSync(NODE)); fs.mkdirSync(BASE, { recursive: true, mode: 0o700 }); const root = path.join(BASE, 'broker-controls-' + Date.now()); fs.mkdirSync(root, { mode: 0o700 });
  const report = { status: 'INCOMPLETE', authentication: 'NOT_APPLICABLE', no_browser_or_network: true, source_start: sources(), runtime_start: { node: pin(NODE), python: pin(PYTHON), pythonImage: pin(PYTHON_IMAGE) }, controls: [], cleanup: [] }; const owned = [];
  assert.equal(report.runtime_start.node.sha256, '18e387c90ab8a8400183e8bdd396376e1e875b91b4c874b894dcade7b35bf572'); assert.equal(report.runtime_start.python.sha256, PYTHON_SHA); assert.equal(report.runtime_start.pythonImage.sha256, PYTHON_IMAGE_SHA);
  report.abi_inputs = Object.fromEntries(['/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/include/sys/_types.h', path.join(ROOT, '.artifacts/release-gates-20261019/toolchain/node-v22.23.2-darwin-arm64/include/node/uv.h')].map(file => [file, pin(file)]));
  report.abi = { darwin_dev_t: 'SIGNED_INT32', libuv_st_dev_and_st_ino: 'UNSIGNED_INT64', node_stats_bigint_backing: 'SIGNED_INT64', representation: 'CANONICAL_SIGNED_DECIMAL_RAW_NODE_EQUALS_PYTHON_DEVICE_BEFORE_NORMALIZATION', inode_limit: 'EXACT_OBSERVED_NONNEGATIVE_NODE_SIGNED64_RANGE_ONLY' };
  const nodeSources = { 'node_file.h': '4d61c44826f0d6d25068b9f5006f2566bef6f0c72a21fcb24633e74e354ff99b', 'node_file-inl.h': '156324a5920721a29576e2a4fa72db791652e64f5cbf1f93b83f907aaeb3cb24' };
  report.abi_source_urls = {};
  for (const [name, expected] of Object.entries(nodeSources)) { const file = path.join(ROOT, '.artifacts/release-gates-20261019/node-stat-source/v22.23.2', name); report.abi_inputs[file] = pin(file); assert.equal(report.abi_inputs[file].sha256, expected); report.abi_source_urls[name] = 'https://raw.githubusercontent.com/nodejs/node/v22.23.2/src/' + name; }
  const begin = async (label, options = {}) => {
    const folder = path.join(root, label); fs.mkdirSync(folder, { mode: 0o700 }); fs.mkdirSync(path.join(folder, 'tmp'), { mode: 0o700 }); const profile = path.join(folder, 'tmp', 'profile'); fs.mkdirSync(profile, { mode: 0o700 });
    const nonce = crypto.randomUUID(); const target = options.target || NODE; const targetSHA = pin(target).sha256; const args = ['-e', targetCode, '--', '--user-data-dir=' + profile, '--remote-debugging-pipe'];
    if (options.stale) save(path.join(folder, 'broker-ack.json'), { kind: 'stale', nonce: 'foreign' });
    // Invoke the exact no-fork run function with a harmless target; main's fixed
    // Chromium binding is deliberately never invoked by these controls.
    const output = fs.openSync(path.join(folder, 'process.txt'), 'wx', 0o600);
    const child = cp.spawn(PYTHON, ['-I', '-c', brokerRunner, LAUNCHER, target, targetSHA, folder, nonce, pin(LAUNCHER).sha256, '5', ...args], { detached: true, env: { PATH: '/usr/bin:/bin', LANG: 'C', SR_CONTEXT_FOLDER: folder, SR_CONTROL_LEADER_EXIT: options.leaderExit ? 'yes' : 'no' }, stdio: ['ignore', output, output, 'pipe', 'pipe'] }); fs.closeSync(output);
    const entry = { child, folder, nonce, target, targetSHA, args, profile, record: null, terminal: null, frames: '', released: false }; owned.push(entry);
    child.stdio[3].on('data', data => { entry.frames += data; assert.ok(Buffer.byteLength(entry.frames) < 65536); }); child.stdio[4].on('error', () => {});
    entry.done = observeTerminal(child).then(value => { entry.terminal = value; return value; });
    entry.spawned = { kind: 'browser-spawn', token: nonce, pid: child.pid, executable: LAUNCHER, profile, args };
    if (!options.stale) { await until(() => fs.existsSync(path.join(folder, 'broker-registration.json')) || entry.terminal); assert.ok(!entry.terminal, 'Broker stopped before registration'); }
    return entry;
  };
  const register = entry => { entry.record = inspectBroker(entry.folder, LAUNCHER, entry.target, entry.targetSHA, process.pid, entry.nonce, entry.spawned); return entry.record; };
  const ackValue = entry => ({ kind: 'pre-exec-ack', nonce: entry.nonce, pid: entry.child.pid, group: entry.child.pid, registration_sha256: entry.record.registration_sha256 });
  const rejectCase = async (label, mutate, options = {}) => {
    const entry = await begin(label, options); if (!options.stale && !options.skipRegister) register(entry); if (mutate) await mutate(entry); const terminal = await entry.done;
    assert.equal(terminal.code, 71); assert.ok(!fs.existsSync(path.join(entry.folder, 'target-proof.json'))); assert.equal(entry.frames, '');
    const refusal = JSON.parse(readRegular(path.join(entry.folder, 'broker-refusal.json'), 16384)); assert.equal(refusal.status, 'REFUSED_BEFORE_TARGET_EXEC'); assert.equal(refusal.source_sha256, pin(LAUNCHER).sha256); assert.equal(refusal.leaf_file, LAUNCHER);
    const expectations = {
      'missing-ack': ['TimeoutError', 'Pre-exec ownership acknowledgement deadline', 'run'], 'stale-ack': ['ValueError', 'Stale ownership state', 'run'], 'wrong-nonce': ['ValueError', 'Ownership acknowledgement mismatch', 'run'], 'truncated-ack': ['ValueError', 'Incomplete ownership acknowledgement', 'run'], 'oversized-ack': ['ValueError', 'Invalid ownership record file', 'read_regular'], 'fifo-ack': ['ValueError', 'Invalid ownership record file', 'read_regular'], 'symlink-ack': ['OSError', null, 'read_regular', 62], 'duplicate-ack-field': ['ValueError', 'Duplicate ownership field', 'object_pairs'], 'registration-tamper': ['ValueError', 'Ownership registration changed after publication', 'run'], 'failed-exec-after-registration': ['PermissionError', null, 'run', 13], 'target-pin-drift': ['ValueError', 'Executable changed before exec', 'run']
    };
    const expected = expectations[label] || ['TimeoutError', 'Pre-exec ownership acknowledgement deadline', 'run']; assert.equal(refusal.exception_type, expected[0]); if (expected[1]) assert.equal(refusal.message, expected[1]); assert.equal(refusal.leaf_function, expected[2]); assert.equal(refusal.errno, expected[3] ?? null);
    const closed = entry.record ? await closeRegistered(entry.record, entry.folder) : await cleanGroup(entry.child, entry.folder); assert.ok(closed.stopped && !closed.errors.length); entry.cleaned = true;
    report.controls.push({ label, status: 'PASS_SOURCE_BOUND_EXPECTED_PRE_EXEC_REFUSAL', terminal, refusal });
  };
  try {
    const positive = await begin('pipe-preservation'); const record = register(positive); positive.released = true; acknowledge(record, positive.folder); positive.takeover = await takeover(record); await until(() => positive.frames.includes('\n'));
    const frame = JSON.parse(positive.frames.trim()); preservedPipes(record, frame);
    positive.child.stdio[4].end('synthetic-cdp-pipe-preserved'); assert.equal((await positive.done).code, 0); const proof = JSON.parse(fs.readFileSync(path.join(positive.folder, 'target-proof.json'))); assert.equal(proof.input, 'synthetic-cdp-pipe-preserved'); assert.equal(proof.pid, record.pid); const positiveClosed = await closeRegistered(record, positive.folder); assert.ok(positiveClosed.stopped && !positiveClosed.errors.length); positive.cleaned = true; report.controls.push({ label: 'actual-same-pid-group-image-and-fd3-fd4-exec-preservation', status: 'PASS_HARMLESS_NODE_EXEC_ONLY', record, takeover: positive.takeover, proof });
    for (const mutation of ['inode', 'type', 'raw-device', 'canonical-device', 'rounded-device-number']) { const altered = structuredClone(frame); const pipe = altered.pipes['3']; if (mutation === 'inode') pipe.inode = (BigInt(pipe.inode) + 1n).toString(); if (mutation === 'type') pipe.type = 0; if (mutation === 'raw-device') pipe.raw_device_signed = (BigInt(pipe.raw_device_signed) ^ 1n).toString(); if (mutation === 'canonical-device') pipe.device = (BigInt(pipe.device) + 1n).toString(); if (mutation === 'rounded-device-number') pipe.device = Number(BigInt.asUintN(64, BigInt(pipe.raw_device_signed))); assert.throws(() => preservedPipes(record, altered)); report.controls.push({ label: 'modified-preserved-pipe-' + mutation, status: 'PASS_REFUSED_MODIFIED_RETAINED_PIPE_FRAME_ONLY' }); }
    await rejectCase('missing-ack', null);
    await rejectCase('stale-ack', null, { stale: true });
    await rejectCase('wrong-nonce', entry => save(path.join(entry.folder, 'broker-ack.json'), { ...ackValue(entry), nonce: crypto.randomUUID() }));
    await rejectCase('truncated-ack', entry => fs.writeFileSync(path.join(entry.folder, 'broker-ack.json'), '{', { flag: 'wx', mode: 0o600 }));
    await rejectCase('oversized-ack', entry => fs.writeFileSync(path.join(entry.folder, 'broker-ack.json'), Buffer.alloc(4097, 65), { flag: 'wx', mode: 0o600 }));
    await rejectCase('fifo-ack', entry => cp.execFileSync(PYTHON, ['-I', '-c', 'import os,sys;os.mkfifo(sys.argv[1],0o600)', path.join(entry.folder, 'broker-ack.json')], { timeout: 3000 }));
    await rejectCase('symlink-ack', entry => { const file = path.join(entry.folder, 'other'); save(file, ackValue(entry)); fs.symlinkSync(file, path.join(entry.folder, 'broker-ack.json')); });
    await rejectCase('duplicate-ack-field', entry => fs.writeFileSync(path.join(entry.folder, 'broker-ack.json'), JSON.stringify(ackValue(entry)).replace('{', '{"nonce":"foreign",') + '\n', { flag: 'wx', mode: 0o600 }));
    await rejectCase('registration-tamper', entry => { const file = path.join(entry.folder, 'broker-registration.json'); const row = JSON.parse(fs.readFileSync(file)); row.environment_sha256 = 'f'.repeat(64); fs.writeFileSync(file, JSON.stringify(row) + '\n'); save(path.join(entry.folder, 'broker-ack.json'), { ...ackValue(entry), registration_sha256: pin(file).sha256 }); });
    for (const label of ['truncated-registration', 'oversized-registration', 'duplicate-registration-field']) {
      await rejectCase(label, entry => { const file = path.join(entry.folder, 'broker-registration.json'); const raw = fs.readFileSync(file, 'utf8'); fs.writeFileSync(file, label === 'truncated-registration' ? '{' : label === 'oversized-registration' ? Buffer.alloc(65537, 65) : raw.replace('{', '{"nonce":"foreign",')); assert.throws(() => inspectBroker(entry.folder, LAUNCHER, NODE, pin(NODE).sha256, process.pid, entry.nonce, entry.spawned)); });
    }
    await rejectCase('missing-passive-registration', entry => assert.throws(() => inspectBroker(entry.folder, LAUNCHER, NODE, pin(NODE).sha256, process.pid, entry.nonce, null)), { skipRegister: true });
    const privateTarget = path.join(root, 'private-target'); fs.writeFileSync(privateTarget, '#!/bin/sh\nexit 0\n', { flag: 'wx', mode: 0o600 });
    await rejectCase('failed-exec-after-registration', entry => { entry.released = true; acknowledge(entry.record, entry.folder); }, { target: privateTarget });
    await rejectCase('target-pin-drift', entry => { fs.writeFileSync(privateTarget, 'changed executable bytes'); entry.released = true; acknowledge(entry.record, entry.folder); }, { target: privateTarget });
    const leader = await begin('leader-exit-profileless-descendant', { leaderExit: true }); register(leader); leader.released = true; acknowledge(leader.record, leader.folder); await takeover(leader.record); leader.child.stdio[4].end('exit-leader'); assert.equal((await leader.done).code, 41);
    const orphan = JSON.parse(fs.readFileSync(path.join(leader.folder, 'target-proof.json'))); const survivor = processes().find(row => row.pid === orphan.child); assert.ok(survivor && survivor.group === leader.record.group && !survivor.command.includes(leader.folder) && !survivor.command.includes('--user-data-dir'));
    const recovered = await closeRegistered(leader.record, leader.folder); assert.ok(recovered.stopped && recovered.errors.includes('Owned group required SIGTERM')); leader.cleaned = true; report.cleanup.push(recovered); report.controls.push({ label: 'registered-leader-exit-with-profileless-samegroup-descendant', status: 'PASS_ACTUAL_PRODUCTION_CLOSE_REGISTERED_PATH', survivor });
    const first = await begin('independent-cleanup-first'); register(first); first.released = true; acknowledge(first.record, first.folder); await takeover(first.record); const second = await begin('independent-cleanup-second'); register(second); second.released = true; acknowledge(second.record, second.folder); await takeover(second.record);
    const attempted = []; const batch = await closeAll([first.record, second.record], root, async (row, folder) => { attempted.push(row.pid); if (row.pid === first.record.pid) throw Error('Synthetic first cleanup failure'); return closeRegistered(row, folder); }); assert.deepEqual(attempted, [first.record.pid, second.record.pid]); assert.equal(batch.errors.length, 1); assert.ok(batch.results[0].stopped && batch.results[0].errors.includes('Owned group required SIGTERM')); second.cleaned = true; const firstClosed = await closeRegistered(first.record, first.folder); assert.ok(firstClosed.stopped); first.cleaned = true; report.cleanup.push(batch, firstClosed); report.controls.push({ label: 'earlier-group-cleanup-error-does-not-suppress-later-group', status: 'PASS_ACTUAL_CLOSE_ALL_INDEPENDENCE' });
    const early = path.join(root, 'early-child-error'); fs.mkdirSync(early, { mode: 0o700 }); const missing = cp.spawn(path.join(early, 'missing-executable'), [], { detached: true, stdio: 'ignore' }); const immediate = observeTerminal(missing); await pause(100); const errorOutcome = await immediate; assert.equal(errorOutcome.spawn_error, 'ENOENT'); assert.equal(errorOutcome.code, null);
    const earlyCleanup = await stopWorkerAndCloseUnacked(missing, early, LAUNCHER, NODE, true); assert.equal(earlyCleanup.worker.stopped, false); assert.ok(earlyCleanup.errors.length); assert.deepEqual(earlyCleanup.final_census, []); save(path.join(early, 'failure-receipt.json'), { status: 'FAIL_WORKER_SPAWN_EXPECTED_CONTROL', terminal: errorOutcome, cleanup_attempted: true, cleanup: earlyCleanup }); report.controls.push({ label: 'early-child-error-is-handled-before-registration-poll-with-failure-receipt', status: 'PASS_ACTUAL_ENOENT_NO_UNHANDLED_REJECTION' });
    const delayed = path.join(root, 'delayed-worker-abort'); fs.mkdirSync(delayed, { mode: 0o700 }); fs.mkdirSync(path.join(delayed, 'tmp'), { mode: 0o700 }); const delayedProfile = path.join(delayed, 'tmp', 'profile'); fs.mkdirSync(delayedProfile, { mode: 0o700 });
    const config = { folder: delayed, python: PYTHON, args: ['-I', '-c', brokerRunner, LAUNCHER, NODE, pin(NODE).sha256, delayed, crypto.randomUUID(), pin(LAUNCHER).sha256, '30', '-e', targetCode, '--', '--user-data-dir=' + delayedProfile, '--remote-debugging-pipe'] };
    const workerCode = "const fs=require('fs'),cp=require('child_process'),c=JSON.parse(process.argv[1]);setTimeout(()=>{const p=cp.spawn(c.python,c.args,{detached:true,env:{PATH:'/usr/bin:/bin',SR_CONTEXT_FOLDER:c.folder},stdio:['ignore','ignore','ignore','pipe','pipe']});fs.writeFileSync(c.folder+'/worker-spawned.json',JSON.stringify({pid:p.pid}),{flag:'wx',mode:384})},150);setInterval(()=>{},1000)";
    const delayedWorker = cp.spawn(NODE, ['-e', workerCode, JSON.stringify(config)], { detached: true, stdio: 'ignore' }); const delayedTerminal = observeTerminal(delayedWorker); const delayedEntry = { child: delayedWorker, folder: delayed, record: null }; owned.push(delayedEntry);
    const ordered = await stopWorkerAndCloseUnacked(delayedWorker, delayed, LAUNCHER, NODE, true); await delayedTerminal; assert.ok(ordered.worker.stopped && ordered.worker.errors.includes('Owned group required SIGTERM')); assert.equal(ordered.brokers.length, 1); assert.ok(ordered.brokers[0].stopped && ordered.brokers[0].errors.includes('Owned group required SIGTERM')); assert.deepEqual(ordered.errors, []); assert.deepEqual(ordered.final_census, []); assert.equal(ordered.brokers[0].pid, JSON.parse(fs.readFileSync(path.join(delayed, 'worker-spawned.json'))).pid); assert.ok(!fs.existsSync(path.join(delayed, 'target-proof.json'))); delayedEntry.cleaned = true; report.cleanup.push(ordered); report.controls.push({ label: 'delayed-detached-broker-during-worker-grace-is-cleaned-after-worker-stop', status: 'PASS_ACTUAL_PRODUCTION_ORDERED_CLEANUP_NO_TARGET_EXEC' });
    report.status = 'PASS_HARMLESS_PRE_EXEC_OWNERSHIP_CONTROLS_ONLY';
  } catch (error) { report.status = 'FAIL_HARMLESS_BROKER_CONTROLS'; report.failure = { type: error.name, message: error.message }; process.exitCode = 1; }
  finally {
    for (const entry of owned.filter(row => !row.cleaned)) {
      try {
        const closed = entry.record ? await closeRegistered(entry.record, entry.folder) : await stopWorkerAndCloseUnacked(entry.child, entry.folder, LAUNCHER, NODE, true); report.cleanup.push(closed); assert.ok(entry.record ? closed.stopped : closed.worker.stopped && !closed.errors.length); }
      catch (error) { report.cleanup.push({ stopped: false, error: error.message }); report.status = 'FAIL_CONTROL_CLEANUP'; process.exitCode = 1; }
    }
    try { report.source_end = sources(); report.runtime_end = { node: pin(NODE), python: pin(PYTHON), pythonImage: pin(PYTHON_IMAGE) }; assert.deepEqual(report.source_end, report.source_start); assert.deepEqual(report.runtime_end, report.runtime_start); for (const [file, expected] of Object.entries(report.abi_inputs)) assert.deepEqual(pin(file), expected); assert.ok(!processes().some(row => row.command.includes(root)), 'Owned control process survived'); } catch (error) { report.status = 'FAIL_CONTROL_FINAL_BOUNDARY'; report.final_error = error.message; process.exitCode = 1; } save(path.join(root, 'results.json'), report); console.log(JSON.stringify({ status: report.status, folder: root }));
  }
}
main().catch(error => { console.error(JSON.stringify({ status: 'FAIL_BROKER_CONTROL_ENTRY', error_type: error.name })); process.exitCode = 1; });
