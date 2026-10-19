'use strict';
// Public API capability only. Raw records remain inside a new private fixture.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const http = require('node:http');
const cp = require('node:child_process');
const { Frames, processes, profileCensus } = require('./context-ownership.cjs');
const { PYTHON, PYTHON_SHA, PYTHON_IMAGE, PYTHON_IMAGE_SHA, inspectBroker, acknowledge, takeover, closeAll, observeTerminal, stopWorkerAndCloseUnacked } = require('./context-broker.cjs');
const { cleanGroup, trackSetup } = require('./capability.cjs');
const ROOT = path.resolve(__dirname, '../../..');
const BASE = path.join(ROOT, '.artifacts/release-gates-20261019/gate4-private-collector-context');
const NODE = path.join(ROOT, '.artifacts/release-gates-20261019/toolchain/node-v22.23.2-darwin-arm64/bin/node');
const CHROME = '/Users/theceo/Library/Caches/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-mac-arm64/chrome-headless-shell';
const LAUNCHER = path.join(__dirname, 'context-launcher.py');
const PACKAGE = path.join(ROOT, 'tools/v2-runtime/phase3b-browser/node_modules/playwright-core');
const ORIGIN = 'http://127.0.0.1:18488';
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
function pin(file) { const body = fs.readFileSync(file); return { sha256: crypto.createHash('sha256').update(body).digest('hex'), bytes: body.length }; }
function save(file, value) { fs.writeFileSync(file, JSON.stringify(value, null, 2) + '\n', { flag: 'wx', mode: 0o600 }); }
function sources() { return Object.fromEntries(['tools/v2-runtime/gate4-private-collector/context.cjs', 'tools/v2-runtime/gate4-private-collector/context-ownership.cjs', 'tools/v2-runtime/gate4-private-collector/context-broker.cjs', 'tools/v2-runtime/gate4-private-collector/context-launcher.py', 'tools/v2-runtime/gate4-private-collector/test-context-broker.cjs', 'tools/v2-runtime/gate4-private-collector/test-context-controls.cjs', 'tools/v2-runtime/gate4-private-collector/capability.cjs', 'tools/v2-runtime/gate4-private-collector/pipe.cjs', 'tasks/release-gates-20261019/gate4-private-collector-context/PLAN.md'].map(name => [name, pin(path.join(ROOT, name))])); }
function packageTree() {
  const result = {}; const walk = folder => { for (const entry of fs.readdirSync(folder, { withFileTypes: true })) { const file = path.join(folder, entry.name); assert.ok(!entry.isSymbolicLink()); if (entry.isDirectory()) walk(file); else { assert.ok(entry.isFile()); result[path.relative(PACKAGE, file)] = { ...pin(file), mode: fs.statSync(file).mode & 0o777 }; } } }; walk(PACKAGE); return result;
}
async function bounded(task, ms = 10000) { let timer; try { return await Promise.race([task, new Promise((_, reject) => { timer = setTimeout(() => reject(Error('Bounded operation deadline')), ms); })]); } finally { clearTimeout(timer); } }
async function denial() {
  const script = "const n=require('net'),d=require('dgram');const t=(h,p)=>new Promise(r=>{const s=n.connect({host:h,port:p});s.once('error',e=>r(e.code));s.setTimeout(1500,()=>{s.destroy();r('TIMEOUT')});s.once('connect',()=>{s.destroy();r('CONNECTED')})});(async()=>{const u=await new Promise(r=>{const s=d.createSocket('udp4');s.send(Buffer.from('synthetic'),443,'192.0.2.1',e=>{s.close();r(e?.code||'SENT')})});console.log(JSON.stringify([await t('192.0.2.1',443),u,await t('127.0.0.1',18489)]))})()";
  const result = cp.spawnSync(NODE, ['-e', script], { encoding: 'utf8', timeout: 10000 }); assert.equal(result.status, 0); const value = JSON.parse(result.stdout); assert.deepEqual(value, ['EPERM', 'EPERM', 'EPERM']); return { inherited_child_tcp_udp_unrelated_loopback: value };
}
async function worker(folder, token) {
  const report = { status: 'INCOMPLETE', authentication: 'NOT_APPLICABLE', completeness: 'UNKNOWN', cleanup_errors: [], handler_errors: [] };
  let browser; let context; let child; let childClosed = false; let terminal; let registration; let registrationError; let ackStream; let ackTimer; let ackClosed = false; let ackSeen = false;
  const pending = new Set(); const requests = new Map(); const ids = new WeakMap(); const events = []; const workers = [];
  const originalSpawn = cp.spawn; let ackResolve; let ackReject;
  const get = request => { if (!ids.has(request)) { assert.ok(requests.size < 50); const id = requests.size + 1; ids.set(request, id); requests.set(id, { request, row: { id } }); } return requests.get(ids.get(request)).row; };
  const event = row => { assert.ok(events.length < 300); events.push(row); };
  const headers = rows => { assert.ok(Array.isArray(rows) && rows.length <= 100 && Buffer.byteLength(JSON.stringify(rows)) <= 65536); assert.ok(rows.every(row => typeof row.name === 'string' && typeof row.value === 'string')); return rows; };
  const task = promise => trackSetup(bounded(promise), pending, error => report.handler_errors.push(error.message));
  try {
    report.source_start = sources(); assert.deepEqual(report.source_start, JSON.parse(fs.readFileSync(path.join(folder, 'source-at-start.json'))));
    report.package_start = pin(path.join(folder, 'package-at-start.json')); assert.deepEqual(packageTree(), JSON.parse(fs.readFileSync(path.join(folder, 'package-at-start.json'))));
    report.denial = await denial();
    assert.equal(process.env.PLAYWRIGHT_DISABLE_SERVICE_WORKER_NETWORK, undefined);
    assert.equal(process.env.NODE_OPTIONS, undefined);
    const ackFrames = new Frames(record => { assert.ok(!ackSeen); assert.equal(record.kind, 'browser-ack'); assert.equal(record.token, token); assert.equal(record.pid, child.pid); ackSeen = true; });
    ackStream = fs.createReadStream(null, { fd: 4, autoClose: false }); ackStream.on('data', chunk => { try { ackFrames.feed(chunk); } catch (e) { registrationError ||= e; ackReject?.(e); } }); ackStream.on('error', e => { registrationError ||= e; ackReject?.(e); });
    ackStream.on('end', () => { try { ackFrames.close(); assert.ok(ackSeen); ackClosed = true; clearTimeout(ackTimer); ackResolve(true); } catch (e) { registrationError ||= e; ackReject?.(e); } });
    cp.spawn = function(command, args, options) {
      assert.equal(command, LAUNCHER); assert.ok(!child && options.detached === true);
      const profiles = args.filter(arg => arg.startsWith('--user-data-dir=')); assert.equal(profiles.length, 1); const profile = profiles[0].slice('--user-data-dir='.length); assert.ok(fs.realpathSync(profile).startsWith(fs.realpathSync(path.join(folder, 'tmp')) + path.sep));
      child = originalSpawn.call(this, command, args, options);
      child.once('close', (code, signal) => { childClosed = true; terminal = { code, signal }; }); child.once('error', e => { registrationError ||= e; });
      registration = new Promise((resolve, reject) => { ackResolve = resolve; ackReject = reject; ackTimer = setTimeout(() => reject(Error('Browser ownership acknowledgement deadline')), 10000); }).catch(e => { registrationError ||= e; return false; });
      const frame = JSON.stringify({ kind: 'browser-spawn', token, pid: child.pid, executable: command, profile, args }); assert.ok(Buffer.byteLength(frame) < 65536); fs.writeSync(3, frame + '\n');
      report.spawn = { pid: child.pid, profile, args, executable: command }; return child;
    };
    const pw = require(PACKAGE); assert.equal(JSON.parse(fs.readFileSync(path.join(PACKAGE, 'package.json'))).version, '1.63.0');
    browser = await pw.chromium.launch({ executablePath: LAUNCHER, headless: true, timeout: 30000, handleSIGINT: false, handleSIGTERM: false, handleSIGHUP: false });
    assert.ok(registration && await registration && ackClosed && !registrationError); report.parent_ownership_acknowledged_before_context = true;
    report.browser_version = browser.version(); assert.equal(report.browser_version, '153.0.8010.12');
    context = await browser.newContext({ serviceWorkers: 'allow' }); assert.deepEqual(await context.cookies(), []);
    context.on('request', request => { try { const row = get(request); assert.ok(!row.seen); row.seen = true; row.url = request.url(); row.method = request.method(); row.worker = request.serviceWorker()?.url() || null; event({ kind: 'request', id: row.id, epoch: Date.now() }); task(request.headersArray().then(value => { row.request_headers = headers(value); })); } catch (e) { report.handler_errors.push(e.message); } });
    context.on('response', response => { try { const row = get(response.request()); assert.ok(!row.response); row.response = { status: response.status(), from_service_worker: response.fromServiceWorker() }; event({ kind: 'response', id: row.id, epoch: Date.now() }); task(response.headersArray().then(value => { row.response.headers = headers(value); })); } catch (e) { report.handler_errors.push(e.message); } });
    context.on('requestfinished', request => { try { const row = get(request); if (row.terminal) report.handler_errors.push('Duplicate terminal'); row.terminal = 'finished'; event({ kind: 'finished', id: row.id, epoch: Date.now() }); } catch (e) { report.handler_errors.push(e.message); } });
    context.on('requestfailed', request => { try { const row = get(request); if (row.terminal) report.handler_errors.push('Duplicate terminal'); row.terminal = 'failed'; row.failure = request.failure(); event({ kind: 'failed', id: row.id, epoch: Date.now() }); } catch (e) { report.handler_errors.push(e.message); } });
    context.on('serviceworker', worker => { try { assert.ok(workers.length < 4); workers.push({ url: worker.url(), epoch: Date.now() }); } catch (e) { report.handler_errors.push(e.message); } });
    const page = await context.newPage(); await page.goto(ORIGIN + '/probe', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForFunction(() => window.fixtureState?.ready || window.fixtureState?.error, null, { timeout: 30000 });
    assert.equal(await page.evaluate(() => window.fixtureState.error || null), null);
    await pause(2000); await Promise.all([...pending]); assert.deepEqual(report.handler_errors, []);
    for (const { request, row } of requests.values()) { row.redirected_from = request.redirectedFrom() ? get(request.redirectedFrom()).id : null; row.redirected_to = request.redirectedTo() ? get(request.redirectedTo()).id : null; }
    report.cookies_after = await context.cookies(); report.fixture_ready = true; await context.close(); context = null;
    report.status = 'PASS_PRIVATE_PUBLIC_API_EXECUTION_ONLY';
  } catch (error) { report.status = 'FAIL_PUBLIC_API_CAPTURE'; report.failure = { type: error.name, message: error.message }; process.exitCode = 1; }
  finally {
    cp.spawn = originalSpawn;
    if (browser) { try { await bounded(browser.close(), 15000); } catch (e) { report.cleanup_errors.push(e.message); } }
    let end = Date.now() + 5000; while (child && !childClosed && Date.now() < end) await pause(25);
    await Promise.allSettled([...pending]); clearTimeout(ackTimer); ackStream?.destroy();
    report.browser_child_closed = childClosed; report.browser_terminal = terminal || null; report.registration_error = registrationError?.message || null; report.pending_header_tasks = pending.size;
    try {
      assert.ok(child && childClosed && terminal.code === 0 && ackClosed && !pending.size && !registrationError); assert.deepEqual(report.cleanup_errors, []); assert.deepEqual(report.handler_errors, []);
      report.source_end = sources(); assert.deepEqual(report.source_end, report.source_start); assert.deepEqual(packageTree(), JSON.parse(fs.readFileSync(path.join(folder, 'package-at-start.json'))));
      report.loaded_modules = Object.keys(require.cache).map(file => { assert.ok(file.startsWith(PACKAGE + path.sep) || Object.hasOwn(report.source_start, path.relative(ROOT, file))); return { path: path.relative(ROOT, file), ...pin(file) }; });
    } catch (e) { report.status = 'FAIL_PUBLIC_API_FINAL_BOUNDARY'; report.final_error = e.message; process.exitCode = 1; }
    const raw = { requests: [...requests.values()].map(value => value.row), events, service_workers: workers }; assert.ok(Buffer.byteLength(JSON.stringify(raw)) < 16 * 1024 * 1024); save(path.join(folder, 'raw-context.json'), raw); save(path.join(folder, 'worker-results.json'), report);
  }
}
function fixture(request, response, ledger, failures) {
  if (ledger.length >= 20) { failures.push('Request budget exceeded'); response.writeHead(503); response.end(); return; }
  const row = { sequence: ledger.length + 1, method: request.method, url: ORIGIN + request.url, rawHeaders: request.rawHeaders }; ledger.push(row); response.once('finish', () => { row.status = response.statusCode; row.headers = response._header; row.finished = true; }); response.setHeader('Cache-Control', 'no-store');
  const url = new URL(request.url, ORIGIN);
  if (url.pathname === '/sw.js') { response.setHeader('Content-Type', 'text/javascript'); response.end("self.addEventListener('install',e=>e.waitUntil(fetch('/worker-data').then(r=>r.text()).then(()=>self.skipWaiting())));self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));"); return; }
  if (url.pathname === '/redirect') { response.writeHead(302, { Location: '/data' }); response.end(); return; }
  if (['/data', '/worker-data'].includes(url.pathname)) { response.end('synthetic-response'); return; }
  if (url.pathname !== '/probe') { failures.push('Unexpected path'); response.writeHead(404); response.end(); return; }
  response.setHeader('Set-Cookie', ['synthetic_a=PRIVATE_CONTEXT_MARKER; Path=/; SameSite=Lax', 'synthetic_b=two; Expires=Thu, 31 Dec 2037 23:59:59 GMT; Path=/; SameSite=Lax']); response.setHeader('Content-Type', 'text/html'); response.end('<!doctype html><link rel="icon" href="data:,"><script>window.fixtureState={};(async()=>{await fetch("/redirect").then(r=>r.text());await navigator.serviceWorker.register("/sw.js");await navigator.serviceWorker.ready;window.fixtureState.ready=true})().catch(e=>window.fixtureState.error=String(e))</script>');
}
async function main() {
  throw new Error('Public API probe held: pre-exec ownership integration and controls remain unqualified');
  if (process.argv[2] === '--worker') { const folder = path.resolve(process.argv[3]); assert.equal(path.dirname(folder), BASE); assert.match(path.basename(folder), /^probe-[0-9]{13}$/); return worker(folder, process.argv[4]); }
  assert.equal(fs.realpathSync(process.execPath), fs.realpathSync(NODE));
  fs.mkdirSync(BASE, { recursive: true, mode: 0o700 }); const folder = path.join(BASE, 'probe-' + Date.now()); fs.mkdirSync(folder, { mode: 0o700 }); fs.mkdirSync(path.join(folder, 'tmp'), { mode: 0o700 });
  const token = crypto.randomUUID(); const report = { status: 'INCOMPLETE', authentication: 'NOT_APPLICABLE', completeness: 'UNKNOWN', policy: 'UNKNOWN', folder, ownership_errors: [] };
  const ledger = []; const failures = []; const sockets = new Set(); let server; let child; let registration; let spawned; let terminalOutcome; let ownershipClosed = false; const records = [];
  const frames = new Frames(record => { assert.ok(!spawned); assert.equal(record.kind, 'browser-spawn'); assert.equal(record.token, token); assert.equal(record.executable, LAUNCHER); spawned = record; });
  try {
    report.source_start = sources(); save(path.join(folder, 'source-at-start.json'), report.source_start); save(path.join(folder, 'package-at-start.json'), packageTree()); report.package_index = pin(path.join(folder, 'package-at-start.json')); report.runtime = { node: pin(NODE), chromium: pin(CHROME), python: pin(PYTHON), pythonImage: pin(PYTHON_IMAGE) };
    assert.equal(report.runtime.python.sha256, PYTHON_SHA); assert.equal(report.runtime.pythonImage.sha256, PYTHON_IMAGE_SHA); assert.equal(report.runtime.node.sha256, '18e387c90ab8a8400183e8bdd396376e1e875b91b4c874b894dcade7b35bf572'); assert.equal(report.runtime.chromium.sha256, 'a0bfe7b4da4787b66058477d696cd1d09065d25f06a548947722b9af77ee8282');
    report.source_commit = cp.execFileSync('/usr/bin/git', ['rev-parse', 'HEAD'], { cwd: ROOT, encoding: 'utf8' }).trim();
    server = http.createServer((q, s) => fixture(q, s, ledger, failures)); server.on('connection', s => { sockets.add(s); s.once('close', () => sockets.delete(s)); }); await new Promise((resolve, reject) => { server.once('error', reject); server.listen(18488, '127.0.0.1', resolve); });
    const profile = '(version 1)(allow default)(deny network*)(allow network-outbound (remote tcp "localhost:18488"))'; fs.writeFileSync(path.join(folder, 'containment.sb'), profile, { flag: 'wx', mode: 0o600 });
    const env = { ...process.env, TMPDIR: path.join(folder, 'tmp'), SR_CONTEXT_FOLDER: folder, SR_CONTEXT_NONCE: token }; const removed = []; for (const name of Object.keys(env)) if (/^(?:PW_|PWDEBUG$|PLAYWRIGHT_|NODE_OPTIONS$|NODE_PATH$|DYLD_|LD_PRELOAD$|PYTHONPATH$|PYTHONHOME$|HTTP_PROXY$|HTTPS_PROXY$|ALL_PROXY$|NO_PROXY$)/i.test(name)) { delete env[name]; removed.push(name); } report.removed_environment_names = removed.map(name => /^[A-Z][A-Z0-9_]*$/.test(name) ? name : 'OPAQUE_KEY_' + crypto.createHash('sha256').update(name).digest('hex').slice(0, 12));
    const log = fs.openSync(path.join(folder, 'worker.txt'), 'wx', 0o600); child = cp.spawn('/usr/bin/sandbox-exec', ['-p', profile, NODE, __filename, '--worker', folder, token], { detached: true, env, stdio: ['ignore', log, log, 'pipe', 'pipe'] }); fs.closeSync(log); report.worker_pid = child.pid;
    child.stdio[3].on('data', chunk => { try { frames.feed(chunk); } catch (e) { report.ownership_errors.push(e.message); } }); child.stdio[3].on('end', () => { ownershipClosed = true; try { frames.close(); } catch (e) { report.ownership_errors.push(e.message); } }); child.stdio[3].on('error', e => report.ownership_errors.push(e.message)); child.stdio[4].on('error', e => report.ownership_errors.push(e.message));
    const terminal = observeTerminal(child).then(value => { terminalOutcome = value; return value; });
    const registrationEnd = Date.now() + 15000;
    while (!registration && Date.now() < registrationEnd) {
      assert.deepEqual(report.ownership_errors, []); assert.ok(!terminalOutcome, terminalOutcome?.spawn_error || 'Worker exited before ownership registration');
      if (spawned && fs.existsSync(path.join(folder, 'broker-registration.json'))) registration = inspectBroker(folder, LAUNCHER, CHROME, report.runtime.chromium.sha256, child.pid, token, spawned);
      else await pause(20);
    }
    assert.ok(registration, 'Pre-exec registration missing');
    records.push(registration); // Retain the owned group BEFORE permitting target exec.
    acknowledge(registration, folder);
    report.executable_takeover = await takeover(registration);
    child.stdio[4].end(JSON.stringify({ kind: 'browser-ack', token, pid: registration.pid }) + '\n');
    report.terminal = await bounded(terminal, 120000);
    report.worker = JSON.parse(fs.readFileSync(path.join(folder, 'worker-results.json'))); assert.equal(report.terminal.code, 0); assert.equal(report.worker.status, 'PASS_PRIVATE_PUBLIC_API_EXECUTION_ONLY'); assert.ok(registration && ownershipClosed); assert.deepEqual(report.ownership_errors, []); assert.equal(ledger.length, 5); assert.ok(ledger.every(row => row.finished)); assert.deepEqual(failures, []);
    report.status = 'PASS_PRIVATE_PUBLIC_API_EXECUTION_ONLY';
  } catch (e) { report.status = 'FAIL_PRIVATE_PUBLIC_API_PROBE'; report.failure = { type: e.name, message: e.message }; process.exitCode = 1; }
  finally {
    report.cleanup_errors = []; report.browser_groups = [];
    const closed = await closeAll(records, folder); report.browser_groups.push(...closed.results); report.cleanup_errors.push(...closed.errors.map(row => row.error));
    const quiesced = await stopWorkerAndCloseUnacked(child, folder, LAUNCHER, CHROME, !registration);
    report.worker_group = quiesced.worker; report.browser_groups.push(...quiesced.brokers); report.cleanup_errors.push(...quiesced.errors); report.final_launcher_and_browser_census = quiesced.final_census;
    try { report.final_profile_census = profileCensus(folder, CHROME); assert.deepEqual(report.final_profile_census, []); assert.ok(report.worker_group.stopped && !report.worker_group.errors.length); assert.ok(report.browser_groups.every(row => row.stopped && !row.errors.length)); assert.deepEqual(report.ownership_errors, []); assert.deepEqual(report.cleanup_errors, []); } catch (e) { report.cleanup_errors.push(e.message); report.status = 'FAIL_PUBLIC_API_OWNERSHIP_CLEANUP'; process.exitCode = 1; }
    for (const socket of sockets) socket.destroy(); if (server) await new Promise(resolve => server.listening ? server.close(resolve) : resolve()); report.fixture_closed = !server?.listening;
    try { report.source_end = sources(); assert.deepEqual(report.source_end, report.source_start); assert.deepEqual(packageTree(), JSON.parse(fs.readFileSync(path.join(folder, 'package-at-start.json')))); assert.deepEqual(pin(NODE), report.runtime.node); assert.deepEqual(pin(CHROME), report.runtime.chromium); assert.deepEqual(pin(PYTHON), report.runtime.python); assert.deepEqual(pin(PYTHON_IMAGE), report.runtime.pythonImage); } catch (e) { report.status = 'FAIL_PUBLIC_API_SOURCE_IDENTITY'; process.exitCode = 1; }
    save(path.join(folder, 'ownership-records.json'), records); save(path.join(folder, 'server-requests.json'), ledger); save(path.join(folder, 'results.json'), report); console.log(JSON.stringify({ status: report.status, folder }));
  }
}
if (require.main === module) main().catch(e => { console.error(JSON.stringify({ status: 'FAIL_PUBLIC_API_ENTRY', error_type: e.name })); process.exitCode = 1; });
module.exports = { main, pin, sources, packageTree, LAUNCHER, NODE, CHROME };
