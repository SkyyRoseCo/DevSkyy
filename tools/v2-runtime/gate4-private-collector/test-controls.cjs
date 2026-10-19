'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { EventEmitter } = require('node:events');
const { PassThrough } = require('node:stream');
const { spawn } = require('node:child_process');
const { Pipe } = require('./pipe.cjs');
const { cleanGroup, groupCensus, main, requireAttachments, finalAttachmentVerdict, finalTransportVerdict, trackSetup, objectStoreParams, advancePage } = require('./capability.cjs');
const ROOT = path.resolve(__dirname, '../../..');
const out = path.join(ROOT, '.artifacts/release-gates-20261019/gate4-private-collector', 'controls-' + Date.now());
fs.mkdirSync(out, { recursive: true, mode: 0o700 });
const sourcePins = () => Object.fromEntries(['pipe.cjs', 'capability.cjs', 'test-controls.cjs'].map(name => [name, crypto.createHash('sha256').update(fs.readFileSync(path.join(__dirname, name))).digest('hex')]));
const sourceStart = sourcePins();
const report = { status: 'INCOMPLETE', authentication: 'NOT_APPLICABLE', scope: 'Mock transport and actual synthetic owned-process/preflight controls; no browser or website qualification', controls: [] };
function fake() { const child = new EventEmitter(); child.stdio = [null, null, null, new PassThrough(), new PassThrough()]; return child; }
function control(name, action) { action(); report.controls.push({ name, status: 'PASS' }); }
async function groupControl(name, code, waitForExit) {
  const child = spawn(process.execPath, ['-e', code, out], { detached: true, stdio: 'ignore' });
  try {
    await new Promise((resolve, reject) => { child.once('spawn', resolve); child.once('error', reject); });
    if (waitForExit) await new Promise(resolve => child.once('exit', resolve));
    else await new Promise(resolve => setTimeout(resolve, 100));
    const before = groupCensus(child.pid); const result = await cleanGroup(child, out);
    assert.equal(result.stopped, true); assert.equal(groupCensus(child.pid).length, 0);
    if (name !== 'ordinary empty group') { assert.ok(before.length); assert.ok(result.errors.includes('Owned group required SIGTERM')); }
    else assert.deepEqual(result.errors, []);
    report.controls.push({ name, status: 'PASS_ACTUAL_SYNTHETIC_GROUP_OBSERVATION', before, result });
  } finally {
    const remaining = groupCensus(child.pid);
    if (remaining.length) { try { process.kill(-child.pid, 'SIGKILL'); } catch (error) { if (error.code !== 'ESRCH') throw error; } }
  }
}
(async () => {
  try {
    control('unexpected EOF between commands fails', () => { const child = fake(); const pipe = new Pipe(child, []); child.stdio[4].emit('end'); assert.match(pipe.failure.message, /Unexpected/); });
    control('unexpected browser exit between commands fails', () => { const child = fake(); const pipe = new Pipe(child, []); child.emit('exit', 1); assert.match(pipe.failure.message, /Unexpected browser/); });
    control('intentional clean EOF allowed', () => { const child = fake(); const pipe = new Pipe(child, []); pipe.expectClose(); child.stdio[4].emit('end'); assert.equal(pipe.failure, null); });
    control('malformed frame fails', () => { const pipe = new Pipe(fake(), []); pipe.consume(Buffer.from('{bad}\0')); assert.ok(pipe.failure); });
    control('unknown response identity fails', () => { const pipe = new Pipe(fake(), []); pipe.consume(Buffer.from('{"id":999,"result":{}}\0')); assert.match(pipe.failure.message, /Unknown/); });
    control('truncated intentional EOF fails', () => { const child = fake(); const pipe = new Pipe(child, []); pipe.expectClose(); pipe.consume(Buffer.from('{')); child.stdio[4].emit('end'); assert.ok(pipe.failure); });
    control('oversize pipe fails closed', () => { const pipe = new Pipe(fake(), []); pipe.consume(Buffer.alloc(16 * 1024 * 1024 + 1, 65)); assert.ok(pipe.failure); });
    const late = {}; let dependentCapture = false; await Promise.resolve().then(() => { late.attachment_error = 'synthetic late setup rejection'; });
    assert.throws(() => { requireAttachments(late); dependentCapture = true; }, /Attachment boundary/); assert.equal(dependentCapture, false);
    report.controls.push({ name: 'late setup rejection after readiness aborts dependent capture', status: 'PASS_MOCK_BOUNDARY_CONTROL' });
    const shutdownRace = { status: 'PASS_PRIVATE_CAPABILITY_EXECUTION_ONLY' };
    await new Promise(resolve => setTimeout(() => { shutdownRace.attachment_error = 'synthetic setup rejection during browser close'; resolve(); }, 5));
    assert.equal(finalAttachmentVerdict(shutdownRace, 0), false); assert.equal(shutdownRace.status, 'FAIL_CAPABILITY_EXECUTION');
    report.controls.push({ name: 'cleanup-time setup rejection prevents final PASS', status: 'PASS_MOCK_FINALIZATION_RACE_CONTROL' });
    const pending = new Set(); const actualOrdering = { status: 'PASS_PRIVATE_CAPABILITY_EXECUTION_ONLY' };
    trackSetup(Promise.reject(Error('synthetic setup race')), pending, error => { actualOrdering.attachment_error = error.message; });
    await Promise.allSettled([...pending]);
    assert.equal(pending.size, 0); assert.equal(actualOrdering.attachment_error, 'synthetic setup race'); assert.equal(finalAttachmentVerdict(actualOrdering, pending.size), false);
    report.controls.push({ name: 'actual handled-promise catch precedes set removal and final gate', status: 'PASS_MOCK_PROMISE_ORDER_CONTROL' });
    control('object store request omits index and uses exactly storageKey', () => { const p = objectStoreParams('http://synthetic/', 'db', 'items', 0); assert.equal(Object.hasOwn(p, 'indexName'), false); assert.equal(Object.hasOwn(p, 'securityOrigin'), false); assert.equal(Object.hasOwn(p, 'storageBucket'), false); assert.equal(p.storageKey, 'http://synthetic/'); });
    control('storage zero progress fails', () => { assert.throws(() => advancePage({ count: 0, pages: 0, done: false }, { objectStoreDataEntries: [], hasMore: true }, 'idb')); });
    control('cache changing count fails', () => { const state = { count: 0, pages: 0, done: false }; advancePage(state, { cacheDataEntries: [{}], returnCount: 2 }, 'cache'); assert.throws(() => advancePage(state, { cacheDataEntries: [{}], returnCount: 3 }, 'cache')); });
    control('storage terminal page observed', () => { assert.equal(advancePage({ count: 0, pages: 0, done: false }, { objectStoreDataEntries: [{}], hasMore: false }, 'idb'), true); });
    control('storage page budget fails closed', () => { assert.throws(() => advancePage({ count: 1000, pages: 10, done: false }, { objectStoreDataEntries: [{}], hasMore: true }, 'idb')); });
    control('exit before pipe closure cannot pass transport verdict', () => { const p = new Pipe(fake(), []); p.expectClose(); const state = { status: 'PASS_PRIVATE_CAPABILITY_EXECUTION_ONLY' }; assert.equal(finalTransportVerdict(state, p, false), false); assert.equal(state.status, 'FAIL_CAPABILITY_TRANSPORT'); });
    const grandchildCode = "setTimeout(()=>{require('fs').writeSync(4,Buffer.from([123,98,97,100,125,0]))},150)";
    const lateCode = "require('child_process').spawn(process.execPath,['-e'," + JSON.stringify(grandchildCode) + "],{stdio:['ignore','ignore','ignore','ignore',4]}).unref()";
    const lateChild = spawn(process.execPath, ['-e', lateCode], { stdio: ['ignore', 'ignore', 'ignore', 'pipe', 'pipe'] });
    const latePipe = new Pipe(lateChild, []); latePipe.expectClose();
    await new Promise(resolve => lateChild.once('close', resolve));
    assert.ok(latePipe.failure); const lateResult = { status: 'PASS_PRIVATE_CAPABILITY_EXECUTION_ONLY' }; assert.equal(finalTransportVerdict(lateResult, latePipe, true), false);
    report.controls.push({ name: 'actual child exit then descendant late malformed pipe frame fails', status: 'PASS_ACTUAL_SYNTHETIC_PIPE_DRAIN_CONTROL' });
    await groupControl('ordinary empty group' , '', true);
    await groupControl('early leader exit with descendant', "require('child_process').spawn(process.execPath,['-e','setInterval(()=>{},1000)'],{stdio:'ignore'}).unref()", true);
    await groupControl('timeout-style live owned group', 'setInterval(()=>{},1000)', false);
    const preflight = await main('synthetic-preflight-failure');
    assert.equal(preflight.status, 'FAIL_PRIVATE_CAPABILITY'); assert.match(preflight.failure, /Synthetic certificate/); assert.equal(preflight.group_cleanup.stopped, true);
    process.exitCode = 0;
    report.controls.push({ name: 'preflight failure retained structured receipt', status: 'PASS_ACTUAL_CONTROL', receipt: path.join(preflight.folder, 'results.json') });
    report.status = 'PASS_BOUNDED_SOURCE_CONTROLS';
  } catch (error) { report.status = 'FAIL_SOURCE_CONTROLS'; report.failure = error.message; process.exitCode = 1; }
  finally {
    report.source_start = sourceStart; report.sources = sourcePins();
    if (JSON.stringify(report.sources) !== JSON.stringify(sourceStart)) { report.status = 'FAIL_CONTROL_SOURCE_DRIFT'; process.exitCode = 1; }
    fs.writeFileSync(path.join(out, 'results.json'), JSON.stringify(report, null, 2) + '\n', { flag: 'wx', mode: 0o600 }); console.log(JSON.stringify({ status: report.status, controls: report.controls.length, out }));
  }
})();
