'use strict';
// Synthetic loopback-only successor; raw bytes never enter the accepted packet.
const fs = require('node:fs');
const crypto = require('node:crypto');
const path = require('node:path');
const assert = require('node:assert/strict');
const net = require('node:net');
const dgram = require('node:dgram');
const { spawnSync } = require('node:child_process');
const { chromium } = require('../phase3b-browser/node_modules/playwright');
const { classifyRow } = require('../phase3b-browser/network-evidence.cjs');
const VERSION = require('../phase3b-browser/node_modules/playwright/package.json').version;
const MARKER = 'SYNTHETIC_GATE4_PRIVATE_01a0f768';
const PORT = 18472;
const ROOT = path.resolve(__dirname, '../../..');
const PRIVATE = path.join(ROOT, '.artifacts/release-gates-20261019/gate4-privacy');
const KINDS = ['requestWillBeSent', 'requestWillBeSentExtraInfo', 'responseReceived', 'responseReceivedExtraInfo', 'loadingFinished', 'loadingFailed'];

function reduce(journal) {
  assert.equal(journal.schema, 'skyyrose.private-cdp-journal.v1');
  const violations = [];
  if (journal.closed !== true || journal.truncated !== false || journal.unexpectedTarget !== false || !Number.isSafeInteger(journal.traceEndSequence) || journal.traceEndSequence < 0 || !Array.isArray(journal.events)) violations.push('capture-lifecycle');
  if (!Array.isArray(journal.events)) return { schema: 'skyyrose.privacy-network.v1', complete: false, violations, policy: 'UNKNOWN', rows: [] };
  if (journal.traceEndSequence !== journal.events.length) violations.push('terminal-count-mismatch');
  const groups = new Map();
  journal.events.forEach((event, i) => {
    if (event.seq !== i + 1 || !KINDS.includes(event.kind) || event.session !== 'main') violations.push('event-loss-or-unsupported');
    if (event.seq > journal.traceEndSequence) violations.push('event-after-trace-end');
    if (!event.value || typeof event.value.requestId !== 'string') { violations.push('missing-request-identity'); return; }
    const key = event.session + ':' + event.value.requestId;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(event);
  });
  const rows = [...groups.values()].map((events, i) => {
    const get = kind => events.filter(event => event.kind === kind).map(event => event.value);
    const request = get('requestWillBeSent'); const extra = get('requestWillBeSentExtraInfo');
    const response = get('responseReceived'); const rextra = get('responseReceivedExtraInfo');
    const finished = get('loadingFinished'); const failed = get('loadingFailed');
    const info = response[0]?.response;
    const responseValid = info && typeof info === 'object' && !Array.isArray(info) && typeof info.url === 'string' && Number.isInteger(info.status) && typeof info.mimeType === 'string' && ['fromDiskCache','fromPrefetchCache','fromServiceWorker'].every(key => !(key in info) || typeof info[key] === 'boolean');
    const metadata = responseValid ? info : {};
    const row = { schema: 'skyyrose.network-row.v1', capture_complete: journal.closed === true && violations.length === 0 && Boolean(responseValid), truncated: journal.truncated, redirects_complete: request.length === 1 && !request[0].redirectResponse, request_count: request.length, finished_count: finished.length, failed_count: failed.length, response_count: response.length, request_extra_count: extra.length, response_extra_count: rextra.length, has_response_extra: response[0]?.hasExtraInfo, from_disk_cache: metadata.fromDiskCache === true, from_prefetch_cache: metadata.fromPrefetchCache === true, from_service_worker: metadata.fromServiceWorker === true, router_present: Boolean(metadata.serviceWorkerRouterInfo), request_headers: extra[0]?.headers };
    const classified = classifyRow(row);
    const headers = rextra[0]?.headers;
    const keys = headers && typeof headers === 'object' && !Array.isArray(headers) ? Object.keys(headers).filter(key => key.toLowerCase() === 'set-cookie') : [];
    const responseCookies = rextra.length !== 1 || !headers || Array.isArray(headers) || typeof headers !== 'object' || Object.values(headers).some(value => typeof value !== 'string') || keys.length > 1 || keys.some(key => typeof headers[key] !== 'string' || !headers[key].trim()) ? 'UNKNOWN' : keys.length ? 'PRESENT' : 'ABSENT';
    return { id: 'request-' + (i + 1), ...classified, response_cookie_presence: responseCookies, counts: { request: request.length, request_extra: extra.length, response: response.length, response_extra: rextra.length, finished: finished.length, failed: failed.length } };
  });
  const complete = rows.length > 0 && violations.length === 0 && rows.every(row => row.disposition === 'CAPTURED_REQUEST_HEADERS' && row.response_cookie_presence !== 'UNKNOWN');
  return { schema: 'skyyrose.privacy-network.v1', complete, violations: [...new Set(violations)], policy: !complete ? 'UNKNOWN' : rows.some(row => row.cookie_presence !== 'ABSENT' || row.response_cookie_presence !== 'ABSENT') ? 'FAIL_FORBIDDEN_COOKIES' : 'PASS_NO_COOKIES', rows };
}

async function probeDenial() {
  const tcp = await new Promise(resolve => { const s = net.connect({ host: '192.0.2.1', port: 443 }); s.on('error', error => resolve(error.code)); s.setTimeout(2000, () => { s.destroy(); resolve('TIMEOUT'); }); s.on('connect', () => { s.destroy(); resolve('CONNECTED'); }); });
  const udp = await new Promise(resolve => { const s = dgram.createSocket('udp4'); s.once('error', error => { try { s.close(); } catch {} resolve(error.code); }); s.send(Buffer.from('synthetic'), 443, '192.0.2.1', error => { s.close(); resolve(error?.code || 'SENT'); }); });
  const child = spawnSync(process.execPath, ['-e', "require('node:net').connect({host:'192.0.2.1',port:443}).on('error',e=>{console.log(e.code);process.exit(e.code==='EPERM'?0:1)})"], { timeout: 3000, encoding: 'utf8' });
  assert.equal(tcp, 'EPERM'); assert.equal(udp, 'EPERM'); assert.equal(child.status, 0);
  const childUdp = spawnSync(process.execPath, ['-e', "const s=require('node:dgram').createSocket('udp4');s.on('error',e=>{console.log(e.code);process.exit(e.code==='EPERM'?0:1)});s.send(Buffer.from('synthetic'),443,'192.0.2.1',e=>{if(e){console.log(e.code);process.exit(e.code==='EPERM'?0:1)}process.exit(1)})"], { timeout: 3000, encoding: 'utf8' });
  const otherLoopback = await new Promise(resolve => { const s = net.connect({ host: '127.0.0.1', port: PORT + 1 }); s.on('error', error => resolve(error.code)); s.on('connect', () => { s.destroy(); resolve('CONNECTED'); }); });
  assert.equal(childUdp.status, 0); assert.equal(otherLoopback, 'EPERM');
  return { tcp, udp, inherited_child_tcp: child.stdout.trim(), inherited_child_udp: childUdp.stdout.trim(), other_loopback: otherLoopback };
}

async function capture(mode, run) {
  assert.equal(VERSION, '1.58.2'); assert.ok(['clean', 'tainted', 'cancelled'].includes(mode));
  assert.ok(/^\d+$/.test(run));
  const destination = path.join(PRIVATE, run, mode); fs.mkdirSync(destination, { recursive: true, mode: 0o700 });
  const denial = await probeDenial();
  const browser = await chromium.launch({ headless: true, executablePath: '/Users/theceo/Library/Caches/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-mac-arm64/chrome-headless-shell' });
  const journal = { schema: 'skyyrose.private-cdp-journal.v1', closed: false, truncated: false, unexpectedTarget: false, traceEndSequence: 0, events: [] };
  let context;
  try {
    context = await browser.newContext({ viewport: { width: 800, height: 600 }, serviceWorkers: 'block' });
    await context.tracing.start({ snapshots: true, screenshots: false, sources: false });
    const page = await context.newPage();
    context.on('page', other => { if (other !== page) journal.unexpectedTarget = true; });
    page.on('worker', () => { journal.unexpectedTarget = true; });
    const logs = []; page.on('console', message => logs.push({ kind: 'console', text: message.text() }));
    page.on('pageerror', error => logs.push({ kind: 'pageerror', text: error.message }));
    const cdp = await context.newCDPSession(page);
    for (const kind of KINDS) cdp.on('Network.' + kind, value => journal.events.push({ seq: journal.events.length + 1, session: 'main', kind, value }));
    await cdp.send('Network.enable'); await cdp.send('Network.setCacheDisabled', { cacheDisabled: true });
    if (mode === 'tainted') await context.addCookies([{ name: 'synthetic_session', value: MARKER, url: 'http://127.0.0.1:' + PORT }]);
    await page.goto('http://127.0.0.1:' + PORT + '/' + mode + (mode === 'tainted' ? '?nonce=' + MARKER : ''), { waitUntil: 'load' });
    await page.waitForFunction(() => window.fixtureReady === true);
    await page.waitForTimeout(300);
    const logsAtStorage = logs.length;
    if (mode === 'tainted') await page.evaluate(value => console.warn(value), MARKER);
    // Replace the document before freezing script execution and taking final storage.
    await page.evaluate(() => { document.documentElement.innerHTML = '<head><style>*{margin:0!important;padding:0!important;border:0!important}html,body{width:100vw!important;height:100vh!important;overflow:hidden!important;background:rgb(128,128,128)!important}</style></head><body></body>'; });
    await cdp.send('Emulation.setScriptExecutionDisabled', { value: true });
    const origin = 'http://127.0.0.1:' + PORT;
    const cookies = await cdp.send('Network.getCookies', { urls: [origin] });
    const local = await cdp.send('DOMStorage.getDOMStorageItems', { storageId: { securityOrigin: origin, isLocalStorage: true } });
    const session = await cdp.send('DOMStorage.getDOMStorageItems', { storageId: { securityOrigin: origin, isLocalStorage: false } });
    const storage = { cookies: cookies.cookies, local: local.entries, session: session.entries, scope: 'Observed single-origin cookies/localStorage/sessionStorage; IndexedDB/cache storage excluded' };
    fs.writeFileSync(path.join(destination, 'raw-storage.json'), JSON.stringify(storage));
    await page.screenshot({ path: path.join(destination, 'masked.png'), mask: [page.locator('html')], maskColor: '#808080', animations: 'disabled' });
    await context.tracing.stop({ path: path.join(destination, 'raw-trace.zip') });
    journal.traceEndSequence = journal.events.length;
    await context.close(); context = null;
    journal.closed = true;
    await new Promise(resolve => setImmediate(resolve));
    fs.writeFileSync(path.join(destination, 'raw-network.json'), JSON.stringify(journal));
    fs.writeFileSync(path.join(destination, 'raw-log.json'), JSON.stringify(logs));
    const rawPins = Object.fromEntries(['raw-trace.zip','raw-network.json','raw-log.json','raw-storage.json','masked.png'].map(name => [name, crypto.createHash('sha256').update(fs.readFileSync(path.join(destination,name))).digest('hex')]));
    const projection = reduce(journal);
    fs.writeFileSync(path.join(destination, 'network.json'), JSON.stringify(projection, null, 2));
    fs.writeFileSync(path.join(destination, 'capture.json'), JSON.stringify({ schema: 'skyyrose.synthetic-capture.v1', mode, raw_pins: rawPins, playwright: VERSION, browser: browser.version(), denial, event_count: journal.events.length, traceEndSequence: journal.traceEndSequence, closed: journal.closed, logs: logs.length, storage_cookie_count: storage.cookies.length, local_storage_count: storage.local.length, session_storage_count: storage.session.length, late_log_count: logs.length - logsAtStorage }, null, 2));
  } finally { if (context) await context.close(); await browser.close(); }
}

if (require.main === module) {
  if (process.argv[2] === '--reduce') { const file = path.resolve(process.argv[3]); assert.ok(file.startsWith(PRIVATE + path.sep)); console.log(JSON.stringify(reduce(JSON.parse(fs.readFileSync(file))))); }
  else capture(process.argv[2], process.argv[3]).catch(error => { console.error(error); process.exitCode = 1; });
}
module.exports = { reduce, MARKER, PORT, KINDS };
