'use strict';
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const http = require('node:http');
const { execFileSync } = require('node:child_process');
const { chromium } = require('playwright');
const { classifyRow, evidenceProjection } = require('./network-evidence.cjs');
const root = path.resolve(__dirname, '../../..');
const { inertSnapshot } = require(path.join(root, 'tasks/release-gates-20261019/offline-v1/inert-snapshot.cjs'));
const out = path.join(root, 'tasks/release-gates-20261019/evidence/v1-offline-successor');
const temporary = path.join(root, '.artifacts/release-gates-20261019/v1-synthetic-raw-control.zip');
fs.mkdirSync(out, { recursive: true });
const report = { classification: 'REPRODUCED_OFFLINE_SUCCESSOR_CONTROLS', authentication: 'NOT_APPLICABLE', original_collector_repaired: false, original_checkpoint_status: 'FAIL', live_attempts: 0, limits: ['The original consumed collector/full capture packet is unavailable', 'No live runtime privacy acceptance or retry authority', 'Projection is a structural privacy artifact, not a Playwright trace viewer archive'], controls: [] };
const marker = 'SYNTHETIC_PRIVATE_VALUE_01a0f768';
const complete = { schema: 'skyyrose.network-row.v1', capture_complete: true, truncated: false, redirects_complete: true, request_count: 1, finished_count: 1, failed_count: 0, response_count: 1, request_extra_count: 1, response_extra_count: 1, has_response_extra: true, from_disk_cache: false, from_prefetch_cache: false, from_service_worker: false, router_present: false, request_headers: {} };
for (const [label, row] of [
  ['missing request extra', { ...complete, request_extra_count: 0 }], ['missing terminal', { ...complete, finished_count: 0 }], ['truncated', { ...complete, truncated: true }], ['unsupported redirect', { ...complete, request_count: 2 }], ['prefetch', { ...complete, from_prefetch_cache: true }], ['service worker', { ...complete, from_service_worker: true }], ['missing capture closure', { ...complete, capture_complete: undefined }], ['ambiguous headers', { ...complete, request_headers: { Cookie: 'a=b', cookie: 'a=c' } }],
]) { assert.equal(classifyRow(row).disposition, 'UNKNOWN'); report.controls.push({ label, status: 'PASS_FAIL_CLOSED' }); }
assert.equal(classifyRow(complete).cookie_presence, 'ABSENT');
assert.equal(classifyRow({ ...complete, request_headers: { Cookie: 'synthetic_session=' + marker } }).cookie_presence, 'PRESENT');
const retained = JSON.parse(fs.readFileSync(path.join(root, 'tasks/release-gates-20261019/offline-v1/capture-replay.json')));
for (const profile of retained.profiles) for (const row of profile.unsupported_rows) assert.equal(classifyRow(row).disposition, 'UNKNOWN');
report.retained_unsupported_rows_still_unknown = retained.profiles.reduce((sum, profile) => sum + profile.unsupported_rows.length, 0);

(async () => {
  const server = http.createServer((request, response) => { response.setHeader('Content-Type', 'text/html'); response.end(`<input value="${marker}"><textarea>${marker}</textarea><a href="/?token=${marker}">Link</a><script nonce="${marker}">setTimeout(()=>{throw new Error('${marker}')},10)</script>`); });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = 'http://127.0.0.1:' + server.address().port;
  const browser = await chromium.launch();
  try {
    const context = await browser.newContext();
    await context.addCookies([{ name: 'synthetic_session', value: marker, url: base }]);
    const page = await context.newPage();
    const rawErrors = [];
    page.on('pageerror', error => rawErrors.push(error.message));
    const cdp = await context.newCDPSession(page);
    const extras = []; const responses = []; const finished = []; const failed = []; const responseExtras = [];
    cdp.on('Network.requestWillBeSentExtraInfo', value => extras.push(value));
    cdp.on('Network.responseReceived', value => responses.push(value));
    cdp.on('Network.responseReceivedExtraInfo', value => responseExtras.push(value));
    cdp.on('Network.loadingFinished', value => finished.push(value));
    cdp.on('Network.loadingFailed', value => failed.push(value));
    await cdp.send('Network.enable');
    await context.tracing.start({ snapshots: true, screenshots: true });
    await page.goto(base + '/?nonce=' + marker);
    await page.waitForTimeout(100);
    const html = await page.evaluate(inertSnapshot);
    assert.equal(html.includes(marker), false);
    assert.ok(rawErrors.some(error => error.includes(marker)));
    const extra = extras.find(event => Object.entries(event.headers).some(([key, value]) => key.toLowerCase() === 'cookie' && value.includes(marker)));
    assert.ok(extra, 'real browser request-extra headers contain synthetic cookie marker');
    const id = extra.requestId;
    const response = responses.find(event => event.requestId === id);
    const row = { ...complete, request_headers: extra.headers, request_extra_count: extras.filter(event => event.requestId === id).length, response_count: responses.filter(event => event.requestId === id).length, response_extra_count: responseExtras.filter(event => event.requestId === id).length, finished_count: finished.filter(event => event.requestId === id).length, failed_count: failed.filter(event => event.requestId === id).length, has_response_extra: response.hasExtraInfo, from_disk_cache: response.response.fromDiskCache === true, from_prefetch_cache: response.response.fromPrefetchCache === true, from_service_worker: response.response.fromServiceWorker === true, router_present: Boolean(response.response.serviceWorkerRouterInfo) };
    await context.tracing.stop({ path: temporary });
    assert.ok(execFileSync('/usr/bin/unzip', ['-p', temporary], { maxBuffer: 16 * 1024 * 1024 }).includes(Buffer.from(marker)), 'negative control: actual raw trace leaks marker even though returned HTML is redacted');
    const projected = evidenceProjection([row], rawErrors.length);
    assert.equal(projected.rows[0].cookie_presence, 'PRESENT');
    fs.writeFileSync(path.join(out, 'persisted-trace.json'), JSON.stringify(projected, null, 2) + '\n');
    fs.writeFileSync(path.join(out, 'persisted-log.json'), JSON.stringify({ error_count: rawErrors.length, message_text_retained: false }) + '\n');
    fs.writeFileSync(path.join(out, 'snapshot.html'), html);
    for (const name of ['persisted-trace.json', 'persisted-log.json', 'snapshot.html']) assert.equal(fs.readFileSync(path.join(out, name)).includes(Buffer.from(marker)), false);
    report.controls.push({ label: 'real browser cookie/error/input/query/nonce markers absent from persisted projected trace, log and inert HTML', status: 'PASS', negative_control_raw_trace_contained_marker: true, unsafe_raw_control_removed: true });
    await context.close();
  } finally { await browser.close(); await new Promise(resolve => server.close(resolve)); if (fs.existsSync(temporary)) fs.unlinkSync(temporary); }
  report.status = 'PASS_OFFLINE_CONTROLS_ONLY';
  fs.writeFileSync(path.join(out, 'results.json'), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify(report));
})().catch(error => { console.error(error); process.exitCode = 1; });
