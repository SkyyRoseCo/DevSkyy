'use strict';
// Diagnostic feasibility only. All raw headers and browser traces stay private.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const http = require('node:http');
const net = require('node:net');
const dgram = require('node:dgram');
const assert = require('node:assert/strict');
const { spawn, spawnSync } = require('node:child_process');
const { Pipe } = require('./pipe.cjs');
const { cleanGroup, trackSetup } = require('./capability.cjs');
const ROOT = path.resolve(__dirname, '../../..');
const BASE = path.join(ROOT, '.artifacts/release-gates-20261019/gate4-private-collector-netlog');
const NODE = path.join(ROOT, '.artifacts/release-gates-20261019/toolchain/node-v22.23.2-darwin-arm64/bin/node');
const CHROME = '/Users/theceo/Library/Caches/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-mac-arm64/chrome-headless-shell';
const ORIGIN = 'http://127.0.0.1:18488';
const LIMIT = 16 * 1024 * 1024;
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
function pin(file) { const b = fs.readFileSync(file); return { sha256: crypto.createHash('sha256').update(b).digest('hex'), bytes: b.length }; }
function save(file, value) { fs.writeFileSync(file, JSON.stringify(value, null, 2) + '\n', { flag: 'wx', mode: 0o600 }); }
function sources() { return Object.fromEntries(['tools/v2-runtime/gate4-private-collector/netlog.cjs', 'tools/v2-runtime/gate4-private-collector/test-netlog-controls.cjs', 'tools/v2-runtime/gate4-private-collector/pipe.cjs', 'tools/v2-runtime/gate4-private-collector/capability.cjs', 'tasks/release-gates-20261019/gate4-private-collector-netlog/PLAN.md'].map(p => [p, pin(path.join(ROOT, p))])); }
function binaries() { return { node: pin(NODE), chromium: pin(CHROME) }; }
function terminateOwned(child, errors) { try { child.kill('SIGKILL'); } catch (error) { errors.push('Owned browser termination failed: ' + error.name); } }
function finalIdentity(expected, actual, closedFile, actualFile) { assert.deepEqual(actual, expected); assert.deepEqual(actualFile, closedFile); }
async function deny() {
  const tcp = address => new Promise(resolve => { const s = net.connect(address); s.once('error', e => resolve(e.code)); s.setTimeout(2000, () => { s.destroy(); resolve('TIMEOUT'); }); s.once('connect', () => { s.destroy(); resolve('CONNECTED'); }); });
  const udp = await new Promise(resolve => { const s = dgram.createSocket('udp4'); s.once('error', e => { try { s.close(); } catch {} resolve(e.code); }); s.send(Buffer.from('synthetic'), 443, '192.0.2.1', e => { s.close(); resolve(e?.code || 'SENT'); }); });
  const child = spawnSync(NODE, ['-e', "require('net').connect({host:'192.0.2.1',port:443}).once('error',e=>{console.log(e.code);process.exit(e.code==='EPERM'?0:1)})"], { encoding: 'utf8', timeout: 5000 });
  const observed = [await tcp({ host: '192.0.2.1', port: 443 }), udp, await tcp({ host: '127.0.0.1', port: 18489 }), child.stdout.trim()];
  assert.equal(child.status, 0); assert.deepEqual(observed, ['EPERM', 'EPERM', 'EPERM', 'EPERM']); return observed;
}
async function worker(folder) {
  const report = { status: 'INCOMPLETE', policy: 'UNKNOWN', authentication: 'NOT_APPLICABLE', cleanup_errors: [] };
  const journal = []; const targets = []; const pending = new Set(); let attachmentError;
  let child; let pipe; let closed = false; let terminal; let monitor; let budgetError;
  const file = path.join(folder, 'netlog.json');
  try {
    report.source_start = sources(); assert.deepEqual(report.source_start, JSON.parse(fs.readFileSync(path.join(folder, 'source-at-start.json'))));
    report.binaries_start = binaries(); assert.deepEqual(report.binaries_start, JSON.parse(fs.readFileSync(path.join(folder, 'binaries-at-start.json'))));
    report.denial = await deny();
    assert.equal(pin(NODE).sha256, '18e387c90ab8a8400183e8bdd396376e1e875b91b4c874b894dcade7b35bf572');
    assert.equal(pin(CHROME).sha256, 'a0bfe7b4da4787b66058477d696cd1d09065d25f06a548947722b9af77ee8282');
    const args = ['--headless', '--no-sandbox', '--remote-debugging-pipe', '--no-startup-window', '--no-first-run', '--disable-background-networking', '--disable-component-update', '--disable-sync', '--disable-default-apps', '--no-default-browser-check', '--user-data-dir=' + path.join(folder, 'profile'), '--log-net-log=' + file, '--net-log-capture-mode=IncludeSensitive'];
    report.launch = { executable: CHROME, args, node: { path: NODE, version: process.version, ...pin(NODE) }, browser: pin(CHROME) };
    const log = fs.openSync(path.join(folder, 'browser-stderr.txt'), 'wx', 0o600);
    child = spawn(CHROME, args, { stdio: ['ignore', 'ignore', log, 'pipe', 'pipe'] }); fs.closeSync(log);
    child.once('close', (code, signal) => { closed = true; terminal = { code, signal }; });
    child.once('error', e => { budgetError ||= e; });
    pipe = new Pipe(child, journal);
    monitor = setInterval(() => { try { if (fs.existsSync(file) && fs.statSync(file).size > LIMIT) { budgetError ||= Error('NetLog byte budget exceeded'); pipe.fail(budgetError); } } catch (e) { budgetError ||= e; pipe.fail(e); } }, 50);
    report.version = await pipe.send('Browser.getVersion');
    assert.deepEqual((await pipe.send('Target.getTargets')).targetInfos, []);
    const owners = new Set();
    pipe.on('event', event => {
      if (event.method !== 'Target.attachedToTarget') return;
      const info = event.params;
      const row = { session: info.sessionId, parent: event.sessionId || null, target: info.targetInfo, paused: info.waitingForDebugger, attached_sequence: journal.length };
      targets.push(row);
      const task = (async () => {
        assert.ok(row.paused && !owners.has(row.target.targetId)); owners.add(row.target.targetId);
        const filter = [{ type: 'browser', exclude: true }, { type: 'tab', exclude: true }, { type: 'service_worker', exclude: true }, { type: 'shared_worker', exclude: true }, {}];
        await pipe.send('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: true, flatten: true, filter }, row.session);
        await Promise.all([pipe.send('Runtime.enable', {}, row.session), pipe.send('Network.enable', {}, row.session)]);
        if (row.target.type === 'page') await pipe.send('Page.enable', {}, row.session);
        row.enabled_sequence = journal.length;
        await pipe.send('Runtime.runIfWaitingForDebugger', {}, row.session); row.resumed_sequence = journal.length;
      })();
      trackSetup(task, pending, error => { attachmentError ||= error; });
    });
    await pipe.send('Target.setDiscoverTargets', { discover: true });
    await pipe.send('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: true, flatten: true });
    const context = await pipe.send('Target.createBrowserContext', { disposeOnDetach: true });
    report.cookies_before = await pipe.send('Storage.getCookies', { browserContextId: context.browserContextId }); assert.deepEqual(report.cookies_before.cookies, []);
    const created = await pipe.send('Target.createTarget', { url: 'about:blank', browserContextId: context.browserContextId });
    const deadline = Date.now() + 30000;
    const check = () => { if (attachmentError || budgetError || pipe.failure) throw attachmentError || budgetError || pipe.failure; assert.ok(Date.now() < deadline, 'Synthetic fixture deadline'); };
    while (!targets.some(row => row.target.targetId === created.targetId && row.resumed_sequence)) { check(); await sleep(20); }
    const main = targets.find(row => row.target.targetId === created.targetId);
    report.navigation = await pipe.send('Page.navigate', { url: ORIGIN + '/probe' }, main.session);
    while (true) {
      check(); const observed = await pipe.send('Runtime.evaluate', { expression: 'JSON.stringify(window.fixtureState||{})', returnByValue: true }, main.session);
      const value = JSON.parse(observed.result.value || '{}'); if (value.error) throw Error(value.error); if (value.ready) break; await sleep(50);
    }
    await Promise.all([...pending]); check();
    assert.equal(targets.filter(row => row.target.type === 'service_worker').length, 1);
    report.cookies_after = await pipe.send('Storage.getCookies', { browserContextId: context.browserContextId });
    report.fixture_ready = true;
    await pipe.send('Target.disposeBrowserContext', { browserContextId: context.browserContextId });
    report.status = 'PASS_PRIVATE_DIAGNOSTIC_CAPTURE_ONLY';
  } catch (error) { report.status = 'FAIL_DIAGNOSTIC_CAPTURE'; report.failure = { type: error.name, message: error.message }; process.exitCode = 1; }
  finally {
    if (pipe && child && !closed) { try { pipe.expectClose(); await pipe.send('Browser.close'); } catch (e) { report.cleanup_errors.push(e.message); } }
    let end = Date.now() + 5000; while (child && !closed && Date.now() < end) await sleep(25);
    if (child && !closed) { terminateOwned(child, report.cleanup_errors); report.cleanup_errors.push('Owned browser required SIGKILL'); end = Date.now() + 3000; while (!closed && Date.now() < end) await sleep(25); }
    await Promise.allSettled([...pending]);
    if (monitor) clearInterval(monitor);
    report.browser_terminal = terminal || null; report.browser_stdio_closed = closed;
    report.pipe_closed = Boolean(pipe?.closed && !pipe.buffer.length && !pipe.failure && !pipe.pending.size);
    report.setup_tasks_pending = pending.size; report.attachment_error = attachmentError?.message || null;
    if (budgetError) report.budget_error = budgetError.message;
    try { assert.ok(!budgetError && !attachmentError && !pending.size && closed && report.pipe_closed && !report.cleanup_errors.length); assert.equal(terminal.code, 0); assert.ok(fs.statSync(file).size <= LIMIT); report.netlog_closed_file = pin(file); } catch (e) { report.status = 'FAIL_DIAGNOSTIC_CLEANUP_OR_BOUNDARY'; report.cleanup_errors.push(e.message); process.exitCode = 1; }
    try { report.source_end = sources(); assert.deepEqual(report.source_end, report.source_start); report.binaries_end = binaries(); assert.deepEqual(report.binaries_end, report.binaries_start); } catch (e) { report.status = 'FAIL_SOURCE_IDENTITY'; process.exitCode = 1; }
    save(path.join(folder, 'raw-cdp.json'), { journal, targets }); save(path.join(folder, 'worker-results.json'), report);
  }
}
function fixture(request, response, ledger, failures) {
  if (ledger.length >= 49) { failures.push('Server request budget exceeded'); response.writeHead(503); response.end(); return; }
  const row = { sequence: ledger.length + 1, method: request.method, url: ORIGIN + request.url, rawHeaders: request.rawHeaders }; ledger.push(row);
  response.once('finish', () => { row.status = response.statusCode; row.emitted_header_text = response._header; row.finished = true; });
  response.setHeader('Cache-Control', 'no-store');
  const url = new URL(request.url, ORIGIN);
  if (url.pathname === '/sw.js') { response.setHeader('Content-Type', 'text/javascript'); response.end("self.addEventListener('install',e=>e.waitUntil(fetch('/worker-data').then(r=>r.text()).then(()=>self.skipWaiting())));self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));"); return; }
  if (url.pathname === '/redirect') { response.writeHead(302, { Location: '/data' }); response.end(); return; }
  if (['/data', '/worker-data'].includes(url.pathname)) { response.end('synthetic-response'); return; }
  if (url.pathname !== '/probe') { failures.push('Unexpected fixture path'); response.writeHead(404); response.end(); return; }
  response.setHeader('Set-Cookie', ['synthetic_a=PRIVATE_NETLOG_MARKER; Path=/; SameSite=Lax', 'synthetic_b=two; Expires=Thu, 31 Dec 2037 23:59:59 GMT; Path=/; SameSite=Lax']);
  response.setHeader('X-Synthetic-Multi', ['first', 'second']); response.setHeader('Content-Type', 'text/html');
  response.end('<!doctype html><link rel="icon" href="data:,"><script>window.fixtureState={};(async()=>{await fetch("/redirect").then(r=>r.text());await navigator.serviceWorker.register("/sw.js");await navigator.serviceWorker.ready;window.fixtureState.ready=true})().catch(e=>window.fixtureState.error=String(e))</script><p>synthetic diagnostic</p>');
}
async function main() {
  if (process.argv[2] === '--worker') { const folder = path.resolve(process.argv[3]); assert.equal(path.dirname(folder), BASE); assert.match(path.basename(folder), /^probe-[0-9]{13}$/); return worker(folder); }
  assert.equal(fs.realpathSync(process.execPath), fs.realpathSync(NODE));
  fs.mkdirSync(BASE, { recursive: true, mode: 0o700 }); const folder = path.join(BASE, 'probe-' + Date.now()); fs.mkdirSync(folder, { mode: 0o700 });
  const report = { status: 'INCOMPLETE', authentication: 'NOT_APPLICABLE', policy: 'UNKNOWN', folder, limits: ['Diagnostic synthetic HTTP/1 fixture only; no global network completeness, storage, sanitation or policy qualification', 'No live site/account/configuration/conversion/deployment/provider action'] };
  const ledger = []; const failures = []; const sockets = new Set(); let server; let child;
  try {
    report.source_start = sources(); save(path.join(folder, 'source-at-start.json'), report.source_start);
    report.binaries_start = binaries(); save(path.join(folder, 'binaries-at-start.json'), report.binaries_start);
    const head = spawnSync('/usr/bin/git', ['rev-parse', 'HEAD'], { cwd: ROOT, encoding: 'utf8', timeout: 5000 }); assert.equal(head.status, 0); report.source_commit = head.stdout.trim();
    server = http.createServer((q, s) => fixture(q, s, ledger, failures)); server.on('connection', s => { sockets.add(s); s.once('close', () => sockets.delete(s)); });
    await new Promise((resolve, reject) => { server.once('error', reject); server.listen(18488, '127.0.0.1', resolve); });
    const profile = '(version 1)(allow default)(deny network*)(allow network-outbound (remote tcp "localhost:18488"))'; fs.writeFileSync(path.join(folder, 'containment.sb'), profile, { flag: 'wx', mode: 0o600 });
    const log = fs.openSync(path.join(folder, 'worker.txt'), 'wx', 0o600);
    child = spawn('/usr/bin/sandbox-exec', ['-p', profile, NODE, __filename, '--worker', folder], { detached: true, stdio: ['ignore', log, log] }); fs.closeSync(log); report.owned_worker_pid = child.pid;
    report.terminal = await new Promise((resolve, reject) => { const timer = setTimeout(() => reject(Error('Diagnostic worker deadline')), 90000); child.once('error', e => { clearTimeout(timer); reject(e); }); child.once('close', (code, signal) => { clearTimeout(timer); resolve({ code, signal }); }); });
    report.worker = JSON.parse(fs.readFileSync(path.join(folder, 'worker-results.json')));
    assert.equal(report.terminal.code, 0); assert.equal(report.worker.status, 'PASS_PRIVATE_DIAGNOSTIC_CAPTURE_ONLY'); assert.deepEqual(failures, []);
    assert.equal(ledger.length, 5); assert.ok(ledger.every(row => row.finished));
    report.status = 'PASS_PRIVATE_DIAGNOSTIC_CAPTURE_ONLY';
  } catch (error) { report.status = 'FAIL_PRIVATE_DIAGNOSTIC_CAPTURE'; report.failure = { type: error.name, message: error.message }; process.exitCode = 1; }
  finally {
    report.group_cleanup = child ? await cleanGroup(child, folder) : { stopped: true, errors: [], observations: [] };
    for (const socket of sockets) socket.destroy(); if (server) await new Promise(resolve => server.listening ? server.close(resolve) : resolve());
    report.fixture_failures = failures; report.fixture_closed = !server?.listening;
    try {
      report.source_end = sources(); assert.deepEqual(report.source_end, report.source_start);
      assert.ok(report.group_cleanup.stopped && !report.group_cleanup.errors.length && report.fixture_closed); assert.deepEqual(failures, []);
      if (report.worker) {
        assert.deepEqual(report.worker.source_start, report.source_start); assert.deepEqual(report.worker.source_end, report.source_start);
        assert.deepEqual(report.worker.binaries_start, report.binaries_start); assert.deepEqual(report.worker.binaries_end, report.binaries_start);
        report.binaries_end = binaries(); report.closed_netlog = pin(path.join(folder, 'netlog.json'));
        finalIdentity(report.binaries_start, report.binaries_end, report.worker.netlog_closed_file, report.closed_netlog);
      } else throw Error('Worker final identity absent');
    } catch (e) { report.status = 'FAIL_DIAGNOSTIC_FINAL_BOUNDARY'; process.exitCode = 1; }
    save(path.join(folder, 'server-requests.json'), ledger); save(path.join(folder, 'results.json'), report);
    console.log(JSON.stringify({ status: report.status, folder }));
  }
}
if (require.main === module) main().catch(error => { console.error(JSON.stringify({ status: 'FAIL_DIAGNOSTIC_ENTRY', error_type: error.name })); process.exitCode = 1; });
module.exports = { pin, sources, terminateOwned, finalIdentity };
