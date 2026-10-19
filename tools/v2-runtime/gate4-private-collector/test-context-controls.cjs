'use strict';
// Ownership controls only; no browser and no external network activity.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const cp = require('node:child_process');
const { Frames, processes, profileCensus, validateSpawn, closeBrowserGroup } = require('./context-ownership.cjs');
const { cleanGroup } = require('./capability.cjs');
const { pin, sources } = require('./context.cjs');
const ROOT = path.resolve(__dirname, '../../..');
const NODE = path.join(ROOT, '.artifacts/release-gates-20261019/toolchain/node-v22.23.2-darwin-arm64/bin/node');
const BASE = path.join(ROOT, '.artifacts/release-gates-20261019/gate4-private-collector-context');
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
async function main() {
  assert.equal(fs.realpathSync(process.execPath), fs.realpathSync(NODE)); fs.mkdirSync(BASE, { recursive: true, mode: 0o700 }); const folder = path.join(BASE, 'controls-' + Date.now()); fs.mkdirSync(folder, { mode: 0o700 }); fs.mkdirSync(path.join(folder, 'tmp'), { mode: 0o700 });
  const report = { status: 'INCOMPLETE', authentication: 'NOT_APPLICABLE', source_start: sources(), controls: [], cleanup: [] }; const groups = []; let failed;
  try {
    for (const kind of ['missing-registration', 'truncated-registration', 'malformed-registration', 'oversized-registration']) {
      const frames = new Frames(() => {});
      assert.throws(() => { if (kind === 'truncated-registration') frames.feed(Buffer.from('{"kind":')); if (kind === 'malformed-registration') frames.feed(Buffer.from('!\n')); if (kind === 'oversized-registration') frames.feed(Buffer.alloc(131073, 65)); frames.close(); });
      report.controls.push({ kind, status: 'PASS_REFUSED_MOCK_OWNERSHIP_FRAME' });
    }
    let registered = false; const duplicate = new Frames(() => { assert.ok(!registered); registered = true; }); assert.throws(() => duplicate.feed(Buffer.from('{}\n{}\n'))); report.controls.push({ kind: 'duplicate-registration', status: 'PASS_REFUSED_MOCK_OWNERSHIP_FRAME' });
    const profile = path.join(folder, 'tmp', 'positive-profile'); fs.mkdirSync(profile);
    const args = ['-e', 'setInterval(()=>{},1000)', '--', '--user-data-dir=' + profile, '--remote-debugging-pipe'];
    const child = cp.spawn(NODE, args, { detached: true, stdio: 'ignore' }); groups.push(child.pid);
    child.on('error', error => { failed ||= error; }); await sleep(100);
    const record = { kind: 'browser-spawn', token: 'synthetic-token', pid: child.pid, executable: NODE, profile, args };
    const ownership = validateSpawn(record, folder, NODE, process.pid, 'synthetic-token');
    report.controls.push({ kind: 'actual-separate-process-group-registration', status: 'PASS_ACTUAL_NODE_PROCESS_ONLY', pid: child.pid, group: child.pid });
    for (const mutation of ['wrong-executable', 'wrong-pid', 'wrong-token', 'outside-profile']) {
      const altered = structuredClone(record);
      if (mutation === 'wrong-executable') altered.executable = '/unowned';
      if (mutation === 'wrong-pid') altered.pid = process.pid;
      if (mutation === 'wrong-token') altered.token = 'foreign';
      if (mutation === 'outside-profile') { const outside = path.join(folder, 'outside'); fs.mkdirSync(outside); altered.profile = outside; altered.args = altered.args.map(arg => arg.startsWith('--user-data-dir=') ? '--user-data-dir=' + outside : arg); }
      assert.throws(() => validateSpawn(altered, folder, NODE, process.pid, 'synthetic-token')); report.controls.push({ kind: mutation, status: 'PASS_REFUSED_MUTATED_PROCESS_REGISTRATION' });
    }
    await assert.rejects(closeBrowserGroup({ ...ownership, birth: 'wrong' }, folder, NODE)); report.controls.push({ kind: 'process-identity-drift-no-signal', status: 'PASS_REFUSED_MOCK_BIRTH_DRIFT' }); assert.ok(processes().some(row => row.pid === child.pid));
    const closed = await closeBrowserGroup(ownership, folder, NODE); assert.ok(closed.stopped && closed.errors.includes('Owned group required SIGTERM')); report.cleanup.push({ kind: 'intentional-node-control-intervention', ...closed }); groups.splice(groups.indexOf(child.pid), 1);
    const gap = path.join(folder, 'gap'); fs.mkdirSync(gap); const code = "const fs=require('fs'),cp=require('child_process'),p=process.argv[1];const c=cp.spawn(process.execPath,['-e','setInterval(()=>{},1000)',p],{detached:true,stdio:'ignore'});fs.writeFileSync(p+'/spawned.json',JSON.stringify({pid:c.pid}));process.exit(41)";
    const worker = cp.spawn('/usr/bin/sandbox-exec', ['-p', '(version 1)(allow default)(deny network*)', NODE, '-e', code, gap], { detached: true, stdio: 'ignore' }); groups.push(worker.pid);
    const terminal = await new Promise((resolve, reject) => { const timer = setTimeout(() => reject(Error('Gap worker deadline')), 5000); worker.once('error', reject); worker.once('close', code => { clearTimeout(timer); resolve(code); }); }); assert.equal(terminal, 41);
    const orphan = JSON.parse(fs.readFileSync(path.join(gap, 'spawned.json'))); groups.push(orphan.pid);
    const census = profileCensus(gap, NODE); assert.ok(census.some(row => row.pid === orphan.pid && row.group === orphan.pid));
    const recovered = await cleanGroup({ pid: orphan.pid }, gap); assert.ok(recovered.stopped && recovered.errors.includes('Owned group required SIGTERM')); report.cleanup.push({ kind: 'spawn-registration-gap-intervention', ...recovered }); groups.splice(groups.indexOf(orphan.pid), 1);
    const stoppedWorker = await cleanGroup(worker, gap); assert.ok(stoppedWorker.stopped && !stoppedWorker.errors.length); groups.splice(groups.indexOf(worker.pid), 1); assert.deepEqual(profileCensus(gap, NODE), []);
    report.controls.push({ kind: 'actual-worker-exit-before-registration-with-separate-child', status: 'PASS_ACTUAL_NODE_CENSUS_RECOVERY_ONLY', terminal, child_group_stopped: true });
    assert.ok(!failed); report.status = 'PASS_BOUNDED_OWNERSHIP_CONTROLS_NO_BROWSER';
  } catch (e) { report.status = 'FAIL_OWNERSHIP_CONTROLS'; report.failure = { type: e.name, message: e.message }; process.exitCode = 1; }
  finally {
    for (const group of groups) { try { report.cleanup.push(await cleanGroup({ pid: group }, folder)); } catch (e) { report.cleanup.push({ stopped: false, error: e.name }); process.exitCode = 1; } }
    try { for (const group of new Set(profileCensus(folder, NODE).map(row => row.group))) { const leader = processes().find(row => row.pid === group); assert.ok(leader && leader.command.includes(folder) && leader.command.includes(NODE)); report.cleanup.push(await cleanGroup({ pid: group }, folder)); } assert.deepEqual(profileCensus(folder, NODE), []); } catch (e) { report.status = 'FAIL_CONTROL_CLEANUP'; report.cleanup.push({ stopped: false, error: e.name }); process.exitCode = 1; }
    report.source_end = sources(); if (JSON.stringify(report.source_end) !== JSON.stringify(report.source_start)) { report.status = 'FAIL_SOURCE_IDENTITY'; process.exitCode = 1; }
    fs.writeFileSync(path.join(folder, 'results.json'), JSON.stringify(report, null, 2) + '\n', { flag: 'wx', mode: 0o600 }); console.log(JSON.stringify({ status: report.status, folder, control_source: pin(__filename) }));
  }
}
main().catch(e => { console.error(JSON.stringify({ status: 'FAIL_OWNERSHIP_CONTROL_ENTRY', error_type: e.name })); process.exitCode = 1; });
