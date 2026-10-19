'use strict';
// Offline structural projection only; raw observations remain private.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const { execFileSync, spawnSync } = require('node:child_process');
let PHASE = 'INITIAL_INPUT';
const ROOT = path.resolve(__dirname, '../../..');
const ORIGINS = new Set(['http://127.0.0.1:18484', 'https://127.0.0.1:18486']);
const PATHS = new Set(['/probe', '/frame', '/popup', '/worker.js', '/shared.js', '/sw.js', '/redirect', '/data']);
function pin(p) { const b = fs.readFileSync(p); return { sha256: crypto.createHash('sha256').update(b).digest('hex'), bytes: b.length }; }
function hash(s) { return crypto.createHash('sha256').update(s).digest('hex'); }
function load(p) { return JSON.parse(fs.readFileSync(p)); }
function requestCounts(server, journal) {
  assert.ok(Array.isArray(server) && server.length && Array.isArray(journal) && journal.length);
  const expected = new Map(); const observed = new Map();
  const increment = (map, method, url) => { assert.equal(typeof method, 'string'); const u = new URL(url); assert.ok(ORIGINS.has(u.origin)); const key = JSON.stringify([method, url]); map.set(key, (map.get(key) || 0) + 1); };
  for (const [i, row] of server.entries()) { assert.equal(row.sequence, i + 1); increment(expected, row.method, row.url); }
  for (const row of journal) {
    const m = row.message;
    if (row.kind === 'received' && m?.method === 'Network.requestWillBeSent') increment(observed, m.params.request.method, m.params.request.url);
  }
  const difference = (a, b) => [...a].filter(([key, count]) => count > (b.get(key) || 0)).map(([key, count]) => {
    const [method, url] = JSON.parse(key); const u = new URL(url);
    return { method: method === 'GET' ? 'GET' : 'OPAQUE_METHOD_' + hash(method).slice(0, 8), path: PATHS.has(u.pathname) ? u.pathname : 'OPAQUE_PATH_' + hash(u.pathname).slice(0, 8), count: count - (b.get(key) || 0) };
  });
  return { fixture_server_requests: server.length, cdp_request_events: [...observed.values()].reduce((a, b) => a + b, 0), missing_from_cdp: difference(expected, observed), extra_in_cdp: difference(observed, expected), verdict: 'UNKNOWN_REQUEST_RECONCILIATION_IS_NOT_COMPLETENESS' };
}
function cookieLines(text) { assert.equal(typeof text, 'string'); return text.split(/\r?\n/).filter(line => /^set-cookie:/i.test(line)).map(line => line.slice(line.indexOf(':') + 1).trim()); }
function main() {
  const id = process.argv[2]; assert.match(id || '', /^[0-9]{13}$/);
  const controlled = process.argv[3] === '--controlled-negative';
  const folder = path.join(ROOT, '.artifacts/release-gates-20261019/gate4-private-collector', (controlled ? 'review-control-' : 'probe-') + id);
  const capture = load(path.join(folder, 'results.json')); const worker = load(path.join(folder, 'worker-results.json'));
  assert.equal(capture.status, 'PASS_PRIVATE_CAPABILITY_EXECUTION_ONLY'); assert.equal(capture.terminal.code, 0);
  assert.equal(capture.group_cleanup.stopped, true); assert.deepEqual(capture.group_cleanup.errors, []);
  assert.equal(worker.owned_browser_stopped, true); assert.equal(worker.browser_stdio_closed, true); assert.deepEqual(worker.cleanup_errors, []);
  assert.deepEqual(capture.source, capture.source_end); assert.deepEqual(capture.source, worker.source_start); assert.deepEqual(capture.source, worker.source_end);
  for (const [relative, expected] of Object.entries(capture.source)) assert.deepEqual(pin(path.join(ROOT, relative)), expected);
  PHASE = 'RAW_INPUT_PARSE';
  const raw = load(path.join(folder, 'raw-capabilities.json')); const server = load(path.join(folder, 'server-requests.json'));
  const network = requestCounts(server, raw.journal);
  const probe = server.find(row => new URL(row.url).pathname === '/probe'); assert.ok(probe);
  const main = raw.journal.find(row => row.kind === 'received' && row.message?.method === 'Network.requestWillBeSent' && row.message.params.request.url === probe.url);
  assert.ok(main);
  const extras = raw.journal.filter(row => row.kind === 'received' && row.message?.method === 'Network.responseReceivedExtraInfo' && row.message.sessionId === main.message.sessionId && row.message.params.requestId === main.message.params.requestId);
  assert.equal(extras.length, 1);
  PHASE = 'COOKIE_BINDING_CHECK';
  const fixtureCookies = cookieLines(probe.emittedHeaderText); const cdpCookies = cookieLines(extras[0].message.params.headersText);
  assert.equal(fixtureCookies.length, 2); assert.deepEqual(cdpCookies, fixtureCookies);
  assert.ok(fixtureCookies.some(value => /Expires=.*,/i.test(value)));
  const controls = [];
  const reduced = raw.journal.filter(row => row !== main);
  assert.ok(requestCounts(server, reduced).missing_from_cdp.some(row => row.path === '/probe'));
  controls.push({ name: 'dropped retained request detected against independent server ledger', status: 'PASS_MODIFIED_RETAINED_CONTROL' });
  assert.ok(requestCounts(server, [...raw.journal, main]).extra_in_cdp.some(row => row.path === '/probe'));
  controls.push({ name: 'extra retained request detected', status: 'PASS_MODIFIED_RETAINED_CONTROL' });
  assert.throws(() => requestCounts([], raw.journal)); controls.push({ name: 'empty server ledger refuses', status: 'PASS_MODIFIED_RETAINED_CONTROL' });
  assert.notDeepEqual(cookieLines(extras[0].message.params.headersText.replace(/^set-cookie:.*\r?\n/im, '')), fixtureCookies);
  controls.push({ name: 'lost repeated Set-Cookie detected without comma splitting', status: 'PASS_MODIFIED_RETAINED_CONTROL' });
  assert.equal(controlled, false, 'Negative fixture unexpectedly reached export');
  PHASE = 'STRUCTURAL_EXPORT';
  const output = path.join(ROOT, 'tasks/release-gates-20261019/gate4-private-collector', 'probe-' + id); fs.mkdirSync(output);
  const inputs = ['results.json', 'worker-results.json', 'raw-capabilities.json', 'server-requests.json', 'source-at-parent-start.json', 'containment.sb', 'fixture.crt', 'worker.txt', 'browser-stderr.txt'];
  const result = { schema: 'skyyrose.private-capability-observation.v1', status: 'OBSERVED_BOUNDED_CAPABILITIES_CAPTURE_GATE_UNKNOWN', authentication: 'NOT_APPLICABLE', capture_source: capture.source_commit, offline_source: execFileSync('/usr/bin/git', ['rev-parse', 'HEAD'], { cwd: ROOT, encoding: 'utf8' }).trim(), runtime: { node: worker.launch.node, chromium: worker.version, protocol_reference: capture.protocol_reference }, containment: worker.denial, cleanup: { process_group_stopped: true, browser_stdio_and_pipe_closed: true, errors: [] }, capabilities: { target_count: raw.targets.length, target_types: worker.target_types, target_early_setup: worker.target_coverage, cross_origin_frame: worker.cross_origin_frame, out_of_process_frame: worker.out_of_process_frame, frame_storage_key_count: worker.frame_storage.length, successful_method_count: raw.operations.filter(row => row.status === 'METHOD_SUCCEEDED').length, terminal_storage_pages: raw.operations.filter(row => row.status === 'OBSERVED_TERMINAL_PAGE').length, context_cookies_after: worker.cookies_after.cookies.length, repeated_response_cookie_count: cdpCookies.length, repeated_cookie_attributes_match_fixture: true, expires_comma_preserved: true }, network, capture_completeness: 'UNKNOWN', data_knowledge: 'OBSERVED_FIXTURE_CAPABILITIES_ONLY', sanitation: 'STRUCTURAL_ALLOWLIST_PROJECTION_ONLY_NOT_ARBITRARY_SECRET_SANITATION', policy: 'UNKNOWN_NO_REAL_ACCEPTANCE_CONTRACT', controls, source_pins: { [path.relative(ROOT, __filename)]: pin(__filename), ...capture.source }, input_pins: Object.fromEntries(inputs.map(name => { const p = path.join(folder, name); return [path.relative(ROOT, p), pin(p)]; })), limits: ['Service-worker main-script request remains missing from CDP despite successful early target setup; alternate capture feasibility is required before40cases', 'No complete redirect-hop/header/session/target-lifecycle classifier, lost-event proof or eight historical UNKNOWN regressions qualified here', 'Storage reads observe fixture frame keys/terminal pages only; arbitrary types, cache bodies, worker quiescence, snapshot races and partition coverage remain UNKNOWN', 'Raw data stay private; structural projection is not arbitrary-secret sanitation, browser fidelity or installed/live privacy qualification', 'Explicit Chromium153 differs from prior nested Playwright1.58.2 recommended runtime; raw pipe executes no Playwright library; protocol1.63 is a separate pinned reference', 'Native shared-cache/transitive runtime bytes not fully qualified; no full installed parity', 'No live conversion/deployment/configuration/acquisition/provider authority granted'] };
  fs.writeFileSync(path.join(output, 'results.json'), JSON.stringify(result, null, 2) + '\n', { flag: 'wx' });
  console.log(JSON.stringify({ status: result.status, output, network, controls: controls.length }));
}
function failureControls(id) {
  assert.match(id || '', /^[0-9]{13}$/);
  const base = path.join(ROOT, '.artifacts/release-gates-20261019/gate4-private-collector');
  const original = path.join(base, 'probe-' + id);
  const marker = 'SYNTHETIC_FAILURE_VALUE_MUST_STAY_PRIVATE';
  const controls = [];
  for (const [index, name] of ['cookie-mismatch', 'malformed-json'].entries()) {
    const controlId = String(Date.now() + index); const folder = path.join(base, 'review-control-' + controlId); fs.mkdirSync(folder, { mode: 0o700 });
    for (const file of ['results.json', 'worker-results.json', 'raw-capabilities.json', 'server-requests.json']) fs.copyFileSync(path.join(original, file), path.join(folder, file));
    if (name === 'malformed-json') fs.writeFileSync(path.join(folder, 'raw-capabilities.json'), '{"private":"' + marker + '"');
    else {
      const rawPath = path.join(folder, 'raw-capabilities.json'); const raw = load(rawPath);
      const row = raw.journal.find(event => event.kind === 'received' && event.message?.method === 'Network.responseReceivedExtraInfo' && /set-cookie:/i.test(event.message.params.headersText || ''));
      assert.ok(row); row.message.params.headersText = row.message.params.headersText.replace(/(set-cookie:)[^\r\n]+/i, '$1 synthetic=' + marker);
      fs.writeFileSync(rawPath, JSON.stringify(raw));
    }
    const terminal = spawnSync(process.execPath, [__filename, controlId, '--controlled-negative'], { encoding: 'utf8', timeout: 10000, maxBuffer: 1024 * 1024 });
    assert.equal(terminal.status, 1); assert.equal(terminal.stdout.includes(marker) || terminal.stderr.includes(marker), false);
    assert.equal(terminal.stdout.includes('SYNTHETIC_PRIVATE_CAPABILITY_MARKER') || terminal.stderr.includes('SYNTHETIC_PRIVATE_CAPABILITY_MARKER'), false);
    const redactedLine = terminal.stderr.split('\n').find(line => line.startsWith('{\"status\":\"FAIL_OFFLINE_CAPABILITY_REVIEW\"'));
    assert.ok(redactedLine); const redacted = JSON.parse(redactedLine);
    assert.equal(redacted.status, 'FAIL_OFFLINE_CAPABILITY_REVIEW'); assert.equal(redacted.phase, name === 'cookie-mismatch' ? 'COOKIE_BINDING_CHECK' : 'RAW_INPUT_PARSE');
    controls.push({ name, status: 'PASS_ACTUAL_REDACTED_CLI_FAILURE', stderr: redacted, private_control_path: path.relative(ROOT, folder) });
  }
  const output = path.join(base, 'offline-controls-' + Date.now() + '.json');
  fs.writeFileSync(output, JSON.stringify({ status: 'PASS_REDACTED_FAILURE_CONTROLS', authentication: 'NOT_APPLICABLE', source: pin(__filename), controls }, null, 2) + '\n', { flag: 'wx', mode: 0o600 });
  console.log(JSON.stringify({ status: 'PASS_REDACTED_FAILURE_CONTROLS', controls: controls.length, output }));
}
if (require.main === module) {
  try { process.argv[2] === '--failure-controls' ? failureControls(process.argv[3]) : main(); }
  catch (error) {
    const code = { status: 'FAIL_OFFLINE_CAPABILITY_REVIEW', phase: PHASE, reason: 'INPUT_VALIDATION_FAILED', error_sha256: hash(String(error.stack || error)) };
    try { fs.writeFileSync(path.join(ROOT, '.artifacts/release-gates-20261019/gate4-private-collector', 'offline-review-failure-' + Date.now() + '.json'), JSON.stringify({ redacted: code, private_details: String(error.stack || error) }, null, 2) + '\n', { flag: 'wx', mode: 0o600 }); } catch {}
    console.error(JSON.stringify(code)); process.exitCode = 1;
  }
}
module.exports = { requestCounts, cookieLines };
