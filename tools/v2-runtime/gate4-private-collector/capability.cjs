'use strict';
// Capability probe only. Raw observations stay in a new private synthetic root.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const http = require('node:http');
const https = require('node:https');
const net = require('node:net');
const dgram = require('node:dgram');
const assert = require('node:assert/strict');
const { spawn, spawnSync } = require('node:child_process');
const { Pipe } = require('./pipe.cjs');
const ROOT = path.resolve(__dirname, '../../..');
const BASE = path.join(ROOT, '.artifacts/release-gates-20261019/gate4-private-collector');
const NODE = path.join(ROOT, '.artifacts/release-gates-20261019/toolchain/node-v22.23.2-darwin-arm64/bin/node');
const CHROME = '/Users/theceo/Library/Caches/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-mac-arm64/chrome-headless-shell';
const HTTP = 'http://127.0.0.1:18484';
const HTTPS = 'https://127.0.0.1:18486';
const MARKER = 'SYNTHETIC_PRIVATE_CAPABILITY_MARKER';
function pin(file) { const bytes = fs.readFileSync(file); return { sha256: crypto.createHash('sha256').update(bytes).digest('hex'), bytes: bytes.length }; }
function sourceClosure() {
  return Object.fromEntries([
    path.join(__dirname, 'capability.cjs'), path.join(__dirname, 'pipe.cjs'), path.join(__dirname, 'test-controls.cjs'),
    path.join(ROOT, 'tools/v2-runtime/phase3b-browser/node_modules/playwright-core/types/protocol.d.ts'),
    path.join(ROOT, 'tasks/release-gates-20261019/gate4-private-collector/PLAN.md'),
  ].map(file => [path.relative(ROOT, file), pin(file)]));
}
function save(file, value) { fs.writeFileSync(file, JSON.stringify(value, null, 2) + '\n', { flag: 'wx', mode: 0o600 }); }
function checked(exe, args, options = {}) { const result = spawnSync(exe, args, { ...options, maxBuffer: 1024 * 1024, timeout: 10000 }); assert.equal(result.status, 0, exe + ' failed'); return result.stdout; }
async function denial() {
  const tcp = await new Promise(resolve => { const s = net.connect({ host: '192.0.2.1', port: 443 }); s.once('error', error => resolve(error.code)); s.setTimeout(2000, () => { s.destroy(); resolve('TIMEOUT'); }); s.once('connect', () => { s.destroy(); resolve('CONNECTED'); }); });
  const udp = await new Promise(resolve => { const s = dgram.createSocket('udp4'); s.once('error', error => { try { s.close(); } catch {} resolve(error.code); }); s.send(Buffer.from('synthetic'), 443, '192.0.2.1', error => { s.close(); resolve(error?.code || 'SENT'); }); });
  const other = await new Promise(resolve => { const s = net.connect({ host: '127.0.0.1', port: 18485 }); s.once('error', error => resolve(error.code)); s.setTimeout(2000, () => { s.destroy(); resolve('TIMEOUT'); }); s.once('connect', () => { s.destroy(); resolve('CONNECTED'); }); });
  const inherited = checked(process.execPath, ['-e', "require('net').connect({host:'192.0.2.1',port:443}).once('error',e=>{console.log(e.code);process.exit(e.code==='EPERM'?0:1)})"], { encoding: 'utf8' }).trim();
  assert.deepEqual([tcp, udp, other, inherited], ['EPERM', 'EPERM', 'EPERM', 'EPERM']);
  return { tcp, udp, unrelated_loopback: other, inherited_child_tcp: inherited };
}
function fixture(request, response, ledger, origin) {
  ledger.push({ sequence: ledger.length + 1, epoch: Date.now(), method: request.method, url: origin + request.url, rawHeaders: request.rawHeaders });
  response.setHeader('Cache-Control', 'no-store');
  response.setHeader('Content-Type', 'text/javascript');
  const url = new URL(request.url, origin);
  if (url.pathname === '/redirect') { response.writeHead(302, { Location: '/data?redirected=1' }); response.end(); return; }
  if (url.pathname === '/data') { response.end('synthetic data'); return; }
  if (url.pathname === '/worker.js') { response.end("fetch('/data?dedicated=1');postMessage('dedicated-ready');"); return; }
  if (url.pathname === '/shared.js') { response.end("onconnect=e=>{fetch('/data?shared=1');e.ports[0].postMessage('shared-ready')};"); return; }
  if (url.pathname === '/sw.js') { response.setHeader('Service-Worker-Allowed', '/'); response.end("self.addEventListener('install',e=>e.waitUntil(caches.open('synthetic-worker-cache').then(c=>c.put('/cached',new Response('" + MARKER + "'))).then(()=>self.skipWaiting())));self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));"); return; }
  response.setHeader('Content-Type', 'text/html');
  if (url.pathname === '/frame' || url.pathname === '/popup') { response.end('<!doctype html><title>synthetic child</title><script>localStorage.setItem("child","' + MARKER + '");fetch("/data?child=' + url.pathname.slice(1) + '")</script><p>synthetic child</p>'); return; }
  response.setHeader('Set-Cookie', ['synthetic_a=' + MARKER + '; Path=/; SameSite=Lax', 'synthetic_b=two; Expires=Thu, 31 Dec 2037 23:59:59 GMT; Path=/; SameSite=Lax']);
  response.setHeader('X-Synthetic-Multi', ['first', 'second']);
  response.end(`<!doctype html><title>synthetic capability</title><link rel="icon" href="data:,"><p data-marker="${MARKER}">${MARKER}</p><script>
  window.fixtureState={};(async()=>{localStorage.setItem('local','${MARKER}');sessionStorage.setItem('session','${MARKER}');
  await new Promise((ok,bad)=>{const r=indexedDB.open('synthetic-db',1);r.onupgradeneeded=()=>r.result.createObjectStore('items');r.onerror=bad;r.onsuccess=()=>{const db=r.result;const t=db.transaction('items','readwrite');t.objectStore('items').put('${MARKER}','key');t.oncomplete=()=>{db.close();ok()};t.onerror=bad}});
  await caches.open('synthetic-page-cache').then(c=>c.put('/page-cached',new Response('${MARKER}')));
  await fetch('/redirect');const frame=document.createElement('iframe');frame.src='${HTTPS}/frame';document.body.append(frame);
  const worker=new Worker('/worker.js');const shared=new SharedWorker('/shared.js');shared.port.start();window.workers=[worker,shared];
  window.popup=open('/popup','synthetic-popup');await navigator.serviceWorker.register('/sw.js');await navigator.serviceWorker.ready;window.fixtureState.ready=true;
  })().catch(e=>{window.fixtureState.error=String(e)})</script>`);
}
async function worker(folder, spki) {
  const journal = []; const targets = []; const operations = []; const raw = { journal, targets, operations };
  const result = { status: 'INCOMPLETE', authentication: 'NOT_APPLICABLE', policy: 'UNKNOWN_NO_ACCEPTANCE_CONTRACT', limits: ['Capability execution only; not 40-route/profile collector qualification', 'HTTP/1 only; HTTP/2/QUIC UNKNOWN', 'Atomic cross-target boundary, worker quiescence, partitioned storage and races UNKNOWN', 'No sanitation or arbitrary-secret-removal qualification'] };
  let child; let transport; let exited = false; let exitSignal;
  const attempt = async (label, method, params, session) => { try { const value = await transport.send(method, params, session); operations.push({ label, method, session, status: 'METHOD_SUCCEEDED', value }); return value; } catch (error) { operations.push({ label, method, session, status: 'UNKNOWN_METHOD_FAILED', error: error.message }); return null; } };
  try {
    result.source_start = sourceClosure();
    assert.deepEqual(result.source_start, JSON.parse(fs.readFileSync(path.join(folder, 'source-at-parent-start.json'))));
    result.denial = await denial();
    assert.equal(pin(process.execPath).sha256, '18e387c90ab8a8400183e8bdd396376e1e875b91b4c874b894dcade7b35bf572');
    assert.equal(pin(CHROME).sha256, 'a0bfe7b4da4787b66058477d696cd1d09065d25f06a548947722b9af77ee8282');
    const args = ['--headless', '--no-sandbox', '--remote-debugging-pipe', '--no-startup-window', '--no-first-run', '--disable-background-networking', '--disable-component-update', '--disable-sync', '--disable-default-apps', '--no-default-browser-check', '--disable-popup-blocking', '--user-data-dir=' + path.join(folder, 'profile'), '--ignore-certificate-errors-spki-list=' + spki];
    result.launch = { executable: CHROME, args, node: { path: process.execPath, version: process.version, ...pin(process.execPath) }, browser_pin: pin(CHROME) };
    const log = fs.openSync(path.join(folder, 'browser-stderr.txt'), 'wx', 0o600);
    child = spawn(CHROME, args, { stdio: ['ignore', 'ignore', log, 'pipe', 'pipe'] }); fs.closeSync(log);
    child.once('exit', (code, signal) => { exited = true; exitSignal = { code, signal }; });
    child.once('error', error => { result.browser_spawn_error = error.message; });
    transport = new Pipe(child, journal);
    result.version = await transport.send('Browser.getVersion');
    result.startup_targets = await transport.send('Target.getTargets');
    assert.equal(result.startup_targets.targetInfos.length, 0, 'Unexpected startup target');
    const sessions = new Map(); const targetOwners = new Map(); const pendingAttach = new Set(); let attachmentFailure = null;
    transport.on('event', event => {
      if (event.method !== 'Target.attachedToTarget') return;
      const info = event.params; const row = { session: info.sessionId, parentSession: event.sessionId || null, info: info.targetInfo, paused: info.waitingForDebugger, attachedAtSequence: journal.length, enabled: false, resumed: false }; targets.push(row); sessions.set(info.sessionId, row);
      if (targetOwners.has(info.targetInfo.targetId)) { row.verdict = 'UNKNOWN_DUPLICATE_TARGET_OWNERSHIP_NOT_RESUMED'; attachmentFailure ||= Error('Duplicate target ownership'); result.attachment_error = attachmentFailure.message; return; }
      targetOwners.set(info.targetInfo.targetId, info.sessionId);
      const task = (async () => {
        const filter = [{ type: 'browser', exclude: true }, { type: 'tab', exclude: true }, { type: 'service_worker', exclude: true }, { type: 'shared_worker', exclude: true }, {}];
        row.recursive = Boolean(await attempt('recursive-autoattach', 'Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: true, flatten: true, filter }, info.sessionId));
        const [runtime, network] = await Promise.all([
          attempt('before-resume-runtime', 'Runtime.enable', {}, info.sessionId),
          attempt('before-resume-network', 'Network.enable', {}, info.sessionId),
        ]);
        row.network = network !== null; row.runtime = runtime !== null;
        row.page = !['page', 'iframe'].includes(info.targetInfo.type) || Boolean(await attempt('before-resume-page', 'Page.enable', {}, info.sessionId));
        row.enabled = row.recursive && row.network && row.runtime && row.page;
        if (!row.enabled) { row.verdict = 'UNKNOWN_REQUIRED_SETUP_FAILED_NOT_RESUMED'; throw Error('Required target setup failed: ' + info.targetInfo.type); }
        row.resumeResult = await attempt('explicit-resume', 'Runtime.runIfWaitingForDebugger', {}, info.sessionId); row.resumed = row.resumeResult !== null; row.resumedAtSequence = journal.length;
        if (!row.resumed) throw Error('Target resume failed');
      })(); pendingAttach.add(task); task.finally(() => pendingAttach.delete(task)).catch(error => { attachmentFailure ||= error; result.attachment_error = error.message; });
    });
    await transport.send('Target.setDiscoverTargets', { discover: true });
    await transport.send('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: true, flatten: true });
    const context = await transport.send('Target.createBrowserContext', { disposeOnDetach: true });
    result.cookies_before = await transport.send('Storage.getCookies', { browserContextId: context.browserContextId }); assert.equal(result.cookies_before.cookies.length, 0);
    const created = await transport.send('Target.createTarget', { url: 'about:blank', browserContextId: context.browserContextId });
    const deadline = Date.now() + 30000;
    while (!targets.some(t => t.info.targetId === created.targetId && t.resumed)) { if (transport.failure) throw transport.failure; if (attachmentFailure) throw attachmentFailure; assert.ok(Date.now() < deadline, 'Initial target attachment deadline'); await new Promise(resolve => setTimeout(resolve, 20)); }
    const main = targets.find(t => t.info.targetId === created.targetId);
    await transport.send('Page.enable', {}, main.session);
    result.navigation = await transport.send('Page.navigate', { url: HTTP + '/probe' }, main.session);
    while (true) {
      if (transport.failure) throw transport.failure;
      if (attachmentFailure) throw attachmentFailure;
      const state = await transport.send('Runtime.evaluate', { expression: 'JSON.stringify(window.fixtureState||{})', returnByValue: true }, main.session);
      const value = JSON.parse(state.result.value || '{}'); if (value.error) throw Error(value.error); if (value.ready) break;
      assert.ok(Date.now() < deadline, 'Fixture ready deadline'); await new Promise(resolve => setTimeout(resolve, 50));
    }
    await new Promise(resolve => setTimeout(resolve, 2000));
    await Promise.all([...pendingAttach]);
    result.cutoff = { epoch: Date.now(), sequence: journal.length, atomic: false, completeness: 'UNKNOWN_NOT_ATOMIC' };
    result.raw_dom_before_projection = await transport.send('Runtime.evaluate', { expression: 'document.documentElement.outerHTML', returnByValue: true }, main.session);
    result.cookies_after = await transport.send('Storage.getCookies', { browserContextId: context.browserContextId });
    for (const row of targets.filter(t => ['page', 'iframe'].includes(t.info.type))) {
      await attempt('frame-tree', 'Page.getFrameTree', {}, row.session);
      for (const origin of [HTTP, HTTPS]) {
        for (const isLocalStorage of [true, false]) await attempt('raw-dom-storage', 'DOMStorage.getDOMStorageItems', { storageId: { securityOrigin: origin, isLocalStorage } }, row.session);
        const dbs = await attempt('idb-names', 'IndexedDB.requestDatabaseNames', { securityOrigin: origin }, row.session);
        for (const databaseName of dbs?.databaseNames || []) {
          const db = await attempt('idb-schema', 'IndexedDB.requestDatabase', { securityOrigin: origin, databaseName }, row.session);
          for (const store of db?.databaseWithObjectStores?.objectStores || []) await attempt('idb-page', 'IndexedDB.requestData', { securityOrigin: origin, databaseName, objectStoreName: store.name, indexName: '', skipCount: 0, pageSize: 100 }, row.session);
        }
        const caches = await attempt('cache-names', 'CacheStorage.requestCacheNames', { securityOrigin: origin }, row.session);
        for (const cache of caches?.caches || []) await attempt('cache-page', 'CacheStorage.requestEntries', { cacheId: cache.cacheId, skipCount: 0, pageSize: 100 }, row.session);
      }
    }
    result.final_targets = await transport.send('Target.getTargets');
    result.target_types = [...new Set(targets.map(t => t.info.type))].sort();
    result.expected_target_types = ['page', 'worker', 'shared_worker', 'service_worker'];
    result.frame_observations = journal.filter(event => event.kind === 'received' && event.message?.method === 'Page.frameNavigated').map(event => ({ session: event.message.sessionId, frame: event.message.params.frame }));
    result.cross_origin_frame = result.frame_observations.some(event => event.frame.url === HTTPS + '/frame') ? 'OBSERVED_FRAME_NAVIGATION_ONLY_STORAGE_EXECUTION_UNQUALIFIED' : 'UNKNOWN_FRAME_NOT_OBSERVED';
    result.out_of_process_frame = result.target_types.includes('iframe') ? 'OBSERVED_TARGET_ONLY_NOT_FULL_QUALIFICATION' : 'UNKNOWN_NOT_EXERCISED';
    result.target_coverage = result.expected_target_types.every(t => result.target_types.includes(t)) && targets.every(t => t.paused && t.recursive && t.enabled && t.resumed) ? 'OBSERVED_REQUIRED_TYPES_EARLY_ENABLED' : 'UNKNOWN_UNSUPPORTED_OR_MISSING_TARGET';
    result.status = 'PASS_PRIVATE_CAPABILITY_EXECUTION_ONLY';
    assert.equal(transport.failure, null);
    await transport.send('Target.disposeBrowserContext', { browserContextId: context.browserContextId });
  } catch (error) { result.status = 'FAIL_CAPABILITY_EXECUTION'; result.failure = { type: error.name, message: error.message }; process.exitCode = 1; }
  finally {
    result.cleanup_errors = [];
    if (transport && !exited) { try { transport.expectClose(); await transport.send('Browser.close'); } catch (error) { result.cleanup_errors.push(error.message); } }
    const end = Date.now() + 5000; while (child && !exited && Date.now() < end) await new Promise(resolve => setTimeout(resolve, 25));
    if (child && !exited) { try { child.kill('SIGKILL'); } catch (error) { result.cleanup_errors.push(error.message); } result.cleanup_errors.push('Owned browser required SIGKILL'); const killedEnd = Date.now() + 3000; while (!exited && Date.now() < killedEnd) await new Promise(resolve => setTimeout(resolve, 25)); }
    result.browser_exit = exitSignal || null; result.owned_browser_stopped = !child || exited;
    if (!result.owned_browser_stopped || result.cleanup_errors.length) { result.status = 'FAIL_CAPABILITY_CLEANUP'; process.exitCode = 1; }
    if (transport?.failure) { result.status = result.cleanup_errors.length ? 'FAIL_CAPABILITY_CLEANUP' : 'FAIL_CAPABILITY_EXECUTION'; result.transport_failure = transport.failure.message; process.exitCode = 1; }
    try { result.source_end = sourceClosure(); assert.deepEqual(result.source_end, result.source_start); } catch (error) { result.status = 'FAIL_SOURCE_IDENTITY'; result.source_identity_failure = error.message; process.exitCode = 1; }
    result.cleanup_status = result.owned_browser_stopped && !result.cleanup_errors.length ? 'OBSERVED_LEADER_STOPPED_PARENT_GROUP_VERIFICATION_REQUIRED' : 'FAIL_CLEANUP';
    save(path.join(folder, 'raw-capabilities.json'), raw); save(path.join(folder, 'worker-results.json'), result);
  }
}
function groupCensus(group) {
  const text = checked('/bin/ps', ['-axo', 'pid=,ppid=,pgid=,command='], { encoding: 'utf8' });
  return text.split('\n').filter(Boolean).map(line => {
    const match = line.trim().match(/^(\d+)\s+(\d+)\s+(\d+)\s+(.*)$/);
    assert.ok(match, 'Unparseable process census');
    return { pid: Number(match[1]), parent: Number(match[2]), group: Number(match[3]), command: match[4] };
  }).filter(row => row.group === group);
}
async function cleanGroup(child, folder) {
  const errors = []; const observations = []; let stopped = false;
  if (!child?.pid) return { stopped: false, errors: ['Worker group identity unavailable'], observations };
  const census = () => { const rows = groupCensus(child.pid); observations.push({ epoch: Date.now(), rows }); return rows; };
  const signal = name => {
    const rows = census(); const leader = rows.find(row => row.pid === child.pid);
    if (leader && !leader.command.includes(folder)) throw Error('Owned group leader identity changed');
    if (rows.length) { try { process.kill(-child.pid, name); } catch (error) { if (error.code !== 'ESRCH') throw error; } }
  };
  try {
    let end = Date.now() + 3000;
    while (census().length && Date.now() < end) await new Promise(resolve => setTimeout(resolve, 100));
    if (census().length) { errors.push('Owned group required SIGTERM'); signal('SIGTERM'); }
    end = Date.now() + 3000;
    while (census().length && Date.now() < end) await new Promise(resolve => setTimeout(resolve, 100));
    if (census().length) { errors.push('Owned group required SIGKILL'); signal('SIGKILL'); }
    end = Date.now() + 3000;
    while (census().length && Date.now() < end) await new Promise(resolve => setTimeout(resolve, 100));
    stopped = census().length === 0;
    if (!stopped) errors.push('Owned group survivors remain');
  } catch (error) { errors.push(error.message); }
  return { stopped, errors, observations };
}
async function main(control = null) {
  if (process.argv[2] === '--worker') { const folder = path.resolve(process.argv[3]); assert.equal(path.dirname(folder), BASE); assert.match(path.basename(folder), /^probe-[0-9]+$/); return worker(folder, process.argv[4]); }
  assert.equal(fs.realpathSync(process.execPath), fs.realpathSync(NODE));
  fs.mkdirSync(BASE, { recursive: true, mode: 0o700 }); const folder = path.join(BASE, 'probe-' + Date.now()); fs.mkdirSync(folder, { mode: 0o700 });
  const summary = { status: 'INCOMPLETE', authentication: 'NOT_APPLICABLE', policy: 'UNKNOWN', folder };
  const key = path.join(folder, 'fixture.key'); const cert = path.join(folder, 'fixture.crt');
  const ledger = []; const servers = []; const sockets = new Set(); let child;
  try {
    if (control === 'synthetic-preflight-failure') throw Error('Synthetic certificate preflight failure');
    summary.source = sourceClosure();
    summary.source_commit = checked('/usr/bin/git', ['rev-parse', 'HEAD'], { cwd: ROOT, encoding: 'utf8' }).trim();
    save(path.join(folder, 'source-at-parent-start.json'), summary.source);
    checked('/usr/bin/openssl', ['req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-keyout', key, '-out', cert, '-days', '1', '-subj', '/CN=localhost', '-addext', 'subjectAltName=IP:127.0.0.1,DNS:localhost']); fs.chmodSync(key, 0o600);
    const pub = checked('/usr/bin/openssl', ['x509', '-in', cert, '-pubkey', '-noout']); const der = checked('/usr/bin/openssl', ['pkey', '-pubin', '-outform', 'DER'], { input: pub }); const spki = crypto.createHash('sha256').update(der).digest('base64');
    summary.certificate = pin(cert); summary.certificate_spki = spki;
    servers.push(http.createServer((q, s) => fixture(q, s, ledger, HTTP)));
    servers.push(https.createServer({ key: fs.readFileSync(key), cert: fs.readFileSync(cert), ALPNProtocols: ['http/1.1'] }, (q, s) => fixture(q, s, ledger, HTTPS)));
    for (const server of servers) server.on('connection', socket => { sockets.add(socket); socket.once('close', () => sockets.delete(socket)); });
    for (const [i, server] of servers.entries()) await new Promise((resolve, reject) => { server.once('error', reject); server.listen(i ? 18486 : 18484, '127.0.0.1', resolve); });
    const profile = '(version 1)(allow default)(deny network*)(allow network-outbound (remote tcp "localhost:18484"))(allow network-outbound (remote tcp "localhost:18486"))'; fs.writeFileSync(path.join(folder, 'containment.sb'), profile, { flag: 'wx', mode: 0o600 });
    const log = fs.openSync(path.join(folder, 'worker.txt'), 'wx', 0o600);
    child = spawn('/usr/bin/sandbox-exec', ['-p', profile, NODE, __filename, '--worker', folder, spki], { detached: true, stdio: ['ignore', log, log] }); fs.closeSync(log);
    summary.owned_worker_pid = child.pid;
    const terminal = await new Promise((resolve, reject) => { const timer = setTimeout(() => { reject(Error('Owned capability worker deadline')); }, 90000); child.once('error', error => { clearTimeout(timer); reject(error); }); child.once('close', (code, signal) => { clearTimeout(timer); resolve({ code, signal }); }); });
    summary.terminal = terminal;
    summary.worker = JSON.parse(fs.readFileSync(path.join(folder, 'worker-results.json')));
    summary.status = terminal.code === 0 ? 'PASS_PRIVATE_CAPABILITY_EXECUTION_ONLY' : 'FAIL_PRIVATE_CAPABILITY';
    if (terminal.code !== 0) process.exitCode = 1;
  } catch (error) { summary.status = 'FAIL_PRIVATE_CAPABILITY'; summary.failure = error.message; process.exitCode = 1; }
  finally {
    summary.group_cleanup = child ? await cleanGroup(child, folder) : { stopped: true, errors: [], observations: [] };
    if (summary.source) { try { summary.source_end = sourceClosure(); assert.deepEqual(summary.source_end, summary.source); if (summary.worker) { assert.deepEqual(summary.worker.source_start, summary.source); assert.deepEqual(summary.worker.source_end, summary.source); } } catch (error) { summary.status = 'FAIL_SOURCE_IDENTITY'; summary.source_identity_failure = error.message; process.exitCode = 1; } }
    if (!summary.group_cleanup.stopped || summary.group_cleanup.errors.length || summary.worker?.cleanup_status === 'FAIL_CLEANUP') { summary.status = 'FAIL_PRIVATE_CAPABILITY_CLEANUP'; process.exitCode = 1; }
    for (const socket of sockets) socket.destroy();
    await Promise.all(servers.map(server => new Promise(resolve => server.listening ? server.close(resolve) : resolve())));
    save(path.join(folder, 'server-requests.json'), ledger); save(path.join(folder, 'results.json'), summary); console.log(JSON.stringify({ status: summary.status, folder }));
  }
  return summary;
}
if (require.main === module) main().catch(error => { console.error(error); process.exitCode = 1; });
module.exports = { cleanGroup, groupCensus, main };
