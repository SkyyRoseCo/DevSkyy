'use strict';
// Offline diagnostic fixture reconciliation. No browser, service or network activity.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const { pin, sources } = require('./netlog.cjs');
const ROOT = path.resolve(__dirname, '../../..');
const BASE = path.join(ROOT, '.artifacts/release-gates-20261019/gate4-private-collector-netlog');
const ORIGIN = 'http://127.0.0.1:18488';
const PATHS = ['/probe', '/redirect', '/data', '/sw.js', '/worker-data'];
let PHASE = 'INPUT';
function load(p) { return JSON.parse(fs.readFileSync(p)); }
function lines(text) { assert.equal(typeof text, 'string'); return text.replace(/\r\n$/, '').replace(/\r\n$/, '').split('\r\n'); }
function header(rows, name) { return rows.filter(row => row.slice(0, row.indexOf(':')).toLowerCase() === name.toLowerCase()).map(row => row.slice(row.indexOf(':') + 1).trim()); }
function rawHeaders(rows) { assert.ok(Array.isArray(rows) && rows.length % 2 === 0); const out = []; for (let i = 0; i < rows.length; i += 2) out.push(rows[i] + ': ' + rows[i + 1]); return out; }
function parse(text) { assert.ok(Buffer.byteLength(text) <= 16 * 1024 * 1024); return JSON.parse(text); }
function reconcile(log, server) {
  assert.equal(log.constants.logFormatVersion, 1);
  // This headless-shell log has no clientInfo version; bind runtime through the
  // execution-recorded CDP version and closed-file hash in main, never invent it.
  assert.deepEqual(log.constants.clientInfo, {});
  const E = log.constants.logEventTypes; const P = log.constants.logEventPhase;
  const jobPairs = ['FIRST_PARTY_SETS_METADATA', 'NETWORK_DELEGATE_BEFORE_START_TRANSACTION', 'HTTP_CACHE_GET_BACKEND', 'HTTP_CACHE_OPEN_OR_CREATE_ENTRY', 'HTTP_CACHE_ADD_TO_ENTRY', 'HTTP_STREAM_REQUEST', 'URL_REQUEST_DELEGATE_CONNECTED', 'HTTP_TRANSACTION_SEND_REQUEST', 'HTTP_TRANSACTION_READ_HEADERS', 'HTTP_STREAM_PARSER_READ_HEADERS', 'HTTP_CACHE_WRITE_INFO', 'NETWORK_DELEGATE_HEADERS_RECEIVED'];
  const pairs = new Set([...jobPairs, 'NETWORK_DELEGATE_BEFORE_URL_REQUEST', 'URL_REQUEST_DELEGATE_RECEIVED_REDIRECT', 'HTTP_TRANSACTION_READ_BODY']);
  const jobSingles = ['COMPUTED_PRIVACY_MODE', 'HTTP_STREAM_JOB_CONTROLLER_BOUND', 'HTTP_STREAM_REQUEST_BOUND_TO_JOB', 'LOCAL_NETWORK_ACCESS_CHECK', 'COOKIE_INCLUSION_STATUS'];
  const specialPairs = ['CORS_REQUEST', 'REQUEST_ALIVE', 'URL_REQUEST_START_JOB', 'URL_REQUEST_DELEGATE_RESPONSE_STARTED'];
  const specialSingles = ['CHECK_CORS_PREFLIGHT_REQUIRED', 'HTTP_TRANSACTION_SEND_REQUEST_HEADERS', 'HTTP_TRANSACTION_READ_RESPONSE_HEADERS', 'URL_REQUEST_REDIRECTED', 'URL_REQUEST_JOB_FILTERED_BYTES_READ', 'TRANSPORT_SECURITY_STATE_SHOULD_UPGRADE_TO_SSL'];
  const names = new Map([...pairs, ...jobSingles, ...specialPairs, ...specialSingles].map(name => { assert.ok(Number.isSafeInteger(E[name])); return [E[name], name]; }));
  for (const name of ['CORS_REQUEST', 'CHECK_CORS_PREFLIGHT_REQUIRED', 'REQUEST_ALIVE', 'URL_REQUEST_START_JOB', 'HTTP_TRANSACTION_SEND_REQUEST_HEADERS', 'HTTP_TRANSACTION_READ_RESPONSE_HEADERS', 'URL_REQUEST_REDIRECTED', 'URL_REQUEST_DELEGATE_RESPONSE_STARTED', 'URL_REQUEST_JOB_FILTERED_BYTES_READ', 'FAILED', 'CANCELLED']) assert.ok(Number.isSafeInteger(E[name]));
  assert.deepEqual(P, { PHASE_BEGIN: 1, PHASE_END: 2, PHASE_NONE: 0 });
  assert.equal(server.length, 5);
  const expected = new Map();
  for (const [i, row] of server.entries()) {
    assert.equal(row.sequence, i + 1); assert.equal(row.method, 'GET'); assert.equal(row.finished, true);
    const url = new URL(row.url); assert.equal(url.origin, ORIGIN); assert.ok(PATHS.includes(url.pathname)); assert.equal(url.search, '');
    assert.ok(!expected.has(row.url)); expected.set(row.url, row);
  }
  assert.deepEqual([...expected.keys()].map(url => new URL(url).pathname).sort(), [...PATHS].sort());
  const groups = new Map();
  for (const row of log.events) {
    if (row.source.type !== log.constants.logSourceType.URL_REQUEST) continue;
    assert.ok(Number.isSafeInteger(row.source.id) && row.source.id > 0);
    assert.equal(typeof row.time, 'string'); assert.match(row.time, /^[0-9]+$/);
    if (!groups.has(row.source.id)) groups.set(row.source.id, []); groups.get(row.source.id).push(row);
  }
  const observed = new Map(); const chains = [];
  for (const [id, rows] of groups) {
    let alive = false; let aliveEnded = false; let open; let previousTime = -1n; const hops = []; let delegateState = 0; let bodyBytes = 0; let corsState = 0; let preflight = false; const pendingPairs = new Set(); let admission = 0; let transportCheck = 0; let bodyReads = 0;
    for (const row of rows) {
      const name = names.get(row.type); assert.ok(name, 'Unsupported URL_REQUEST event type');
      assert.ok((pairs.has(name) || specialPairs.includes(name) ? [1, 2] : [0]).includes(row.phase), 'Unsupported event phase');
      assert.ok(BigInt(row.time) >= previousTime); previousTime = BigInt(row.time);
      assert.ok(row.type !== E.FAILED && row.type !== E.CANCELLED);
      if (Object.hasOwn(row.params || {}, 'net_error')) assert.equal(row.params.net_error, 0);
      if (row.type === E.CORS_REQUEST) {
        if (row.phase === P.PHASE_BEGIN) { assert.ok(!corsState && !alive && !aliveEnded); corsState = 1; }
        else { assert.equal(row.phase, P.PHASE_END); assert.ok(corsState === 1 && alive && !open && !pendingPairs.size && delegateState === 2 && hops.length && bodyReads === 2); corsState = 2; }
        continue;
      }
      if (row.type === E.CHECK_CORS_PREFLIGHT_REQUIRED) { assert.equal(row.phase, P.PHASE_NONE); assert.ok(corsState === 1 && !alive && !aliveEnded && !preflight); preflight = true; continue; }
      if (row.type === E.REQUEST_ALIVE) {
        if (row.phase === P.PHASE_BEGIN) { assert.ok(corsState === 1 && preflight && !alive && !aliveEnded); alive = true; assert.equal(row.params.url, rows.find(r => r.type === E.URL_REQUEST_START_JOB && r.phase === P.PHASE_BEGIN)?.params.url); }
        else { assert.equal(row.phase, P.PHASE_END); assert.ok(corsState === 2 && alive && !open && delegateState === 2 && hops.length); alive = false; aliveEnded = true; }
        continue;
      }
      assert.ok(alive && !aliveEnded && corsState === 1);
      if (pairs.has(name)) {
        if (name === 'NETWORK_DELEGATE_BEFORE_URL_REQUEST') assert.ok(!open && !delegateState && !transportCheck);
        else if (name === 'HTTP_TRANSACTION_READ_BODY') assert.ok(!open && delegateState === 2);
        else assert.ok(open && !delegateState);
        if (row.phase === 1) { assert.ok(!pendingPairs.has(name)); pendingPairs.add(name); }
        else { assert.ok(pendingPairs.has(name)); pendingPairs.delete(name); if (name === 'NETWORK_DELEGATE_BEFORE_URL_REQUEST') admission++; else if (name === 'HTTP_TRANSACTION_READ_BODY') bodyReads++; else open.pairs[name] = (open.pairs[name] || 0) + 1; }
        continue;
      }
      if (name === 'TRANSPORT_SECURITY_STATE_SHOULD_UPGRADE_TO_SSL') { assert.ok(!open && admission === 1 && !transportCheck && !pendingPairs.size); transportCheck++; continue; }
      if (jobSingles.includes(name)) { assert.ok(open && !delegateState); open.singles[name] = (open.singles[name] || 0) + 1; continue; }
      if (row.type === E.URL_REQUEST_START_JOB) {
        if (row.phase === P.PHASE_BEGIN) {
          assert.ok(!open && !delegateState && !bodyBytes && !pendingPairs.size && admission === 1 && transportCheck === 1); admission = 0; transportCheck = 0; const params = row.params; assert.equal(params.method, 'GET'); assert.ok(expected.has(params.url));
          if (hops.length) assert.equal(hops.at(-1).redirect, params.url);
          open = { url: params.url, method: params.method, sent: null, response: null, redirect: null, pairs: {}, singles: {} };
        } else { assert.equal(row.phase, P.PHASE_END); assert.ok(open?.sent && open?.response && !pendingPairs.size); for (const pair of jobPairs) assert.equal(open.pairs[pair], 1); assert.equal(open.pairs.URL_REQUEST_DELEGATE_RECEIVED_REDIRECT || 0, open.redirect ? 1 : 0); for (const single of jobSingles) assert.equal(open.singles[single], single === 'COOKIE_INCLUSION_STATUS' ? 2 : 1); hops.push(open); open = null; }
      } else if (row.type === E.HTTP_TRANSACTION_SEND_REQUEST_HEADERS) {
        assert.equal(row.phase, P.PHASE_NONE); assert.ok(open && !open.sent && pendingPairs.has('HTTP_TRANSACTION_SEND_REQUEST')); const serverRow = expected.get(open.url);
        assert.equal(row.params.line, 'GET ' + new URL(open.url).pathname + ' HTTP/1.1\r\n');
        assert.deepEqual(row.params.headers, rawHeaders(serverRow.rawHeaders)); open.sent = row.params.headers;
      } else if (row.type === E.HTTP_TRANSACTION_READ_RESPONSE_HEADERS) {
        assert.equal(row.phase, P.PHASE_NONE); assert.ok(open?.sent && !open.response && pendingPairs.has('HTTP_TRANSACTION_READ_HEADERS') && !pendingPairs.has('HTTP_STREAM_PARSER_READ_HEADERS') && open.pairs.HTTP_STREAM_PARSER_READ_HEADERS === 1);
        const serverRow = expected.get(open.url); assert.deepEqual(row.params.headers, lines(serverRow.emitted_header_text));
        assert.match(row.params.headers[0], new RegExp('^HTTP/1\\.1 ' + serverRow.status + ' ')); open.response = row.params.headers;
      } else if (row.type === E.URL_REQUEST_REDIRECTED) {
        assert.equal(row.phase, P.PHASE_NONE); assert.ok(open?.response && !open.redirect); assert.equal(expected.get(open.url).status, 302);
        const location = header(open.response, 'location'); assert.equal(location.length, 1);
        open.redirect = new URL(location[0], open.url).href; assert.equal(row.params.location, open.redirect);
      } else if (row.type === E.URL_REQUEST_DELEGATE_RESPONSE_STARTED) {
        assert.ok(!open && hops.length && !hops.at(-1).redirect);
        if (row.phase === P.PHASE_BEGIN) { assert.equal(delegateState, 0); delegateState = 1; }
        else { assert.equal(row.phase, P.PHASE_END); assert.equal(delegateState, 1); delegateState = 2; }
      } else if (row.type === E.URL_REQUEST_JOB_FILTERED_BYTES_READ) {
        assert.ok(delegateState === 2 && !open && !pendingPairs.size && bodyReads === 1 && hops.length && !hops.at(-1).redirect); assert.equal(row.phase, P.PHASE_NONE); assert.ok(Number.isSafeInteger(row.params.byte_count) && row.params.byte_count >= 0); bodyBytes += row.params.byte_count;
      }
    }
    assert.ok(aliveEnded && !alive && !open && hops.length && corsState === 2 && preflight); assert.equal(delegateState, 2);
    const last = hops.at(-1); assert.equal(last.redirect, null); const length = header(last.response, 'content-length'); assert.equal(length.length, 1); assert.match(length[0], /^[0-9]+$/); assert.equal(bodyBytes, Number(length[0]));
    for (const hop of hops) { assert.ok(!observed.has(hop.url)); observed.set(hop.url, { id, ...hop }); }
    chains.push({ source_id: id, paths: hops.map(hop => new URL(hop.url).pathname), closed_lifetime: true, final_filtered_body_bytes: bodyBytes });
  }
  assert.equal(groups.size, 4); assert.deepEqual([...observed.keys()].sort(), [...expected.keys()].sort());
  const cookies = header(observed.get(ORIGIN + '/probe').response, 'set-cookie'); assert.equal(cookies.length, 2); assert.ok(cookies.some(value => /Expires=.*,/i.test(value)));
  const workerCookie = header(observed.get(ORIGIN + '/sw.js').sent, 'cookie'); assert.equal(workerCookie.length, 1);
  assert.deepEqual(workerCookie, header(rawHeaders(expected.get(ORIGIN + '/sw.js').rawHeaders), 'cookie'));
  for (const cookie of cookies) assert.ok(workerCookie[0].split('; ').includes(cookie.split(';')[0]));
  return { status: 'OBSERVED_FIVE_HTTP_HOPS_IN_FOUR_CLOSED_LOGICAL_REQUESTS', server_requests: server.length, netlog_http_hops: observed.size, logical_request_sources: groups.size, initial_service_worker_request: 'OBSERVED_WITH_EXACT_SENT_COOKIE', response_repeated_cookies: cookies.length, repeated_cookie_expires_comma: true, chains, limits: ['Exact synthetic HTTP/1 identity/uncompressed fixture only; Content-Length/filtered-byte agreement is not general body capture proof', 'Diagnostic logging schema is not a production completeness interface; global capture, policy and sanitation UNKNOWN'] };
}
function controls(log, server) {
  const E = log.constants.logEventTypes; const sw = log.events.find(row => row.type === E.URL_REQUEST_START_JOB && row.phase === 1 && row.params.url === ORIGIN + '/sw.js').source.id;
  const main = log.events.find(row => row.type === E.URL_REQUEST_START_JOB && row.phase === 1 && row.params.url === ORIGIN + '/probe').source.id;
  const result = [];
  for (const mutation of ['missing-initial-sw', 'duplicate-logical-request', 'response-cookie-changed', 'request-cookie-missing', 'request-cookie-changed', 'missing-lifetime-end', 'redirect-changed', 'reversed-delegate', 'missing-delegate-end', 'body-before-delegate', 'unknown-event', 'invalid-phase', 'missing-intermediate-end', 'truncated-json']) {
    const value = structuredClone(log);
    if (mutation === 'missing-initial-sw') value.events = value.events.filter(row => row.source.id !== sw);
    if (mutation === 'duplicate-logical-request') { const extra = structuredClone(value.events.filter(row => row.source.id === sw)); for (const row of extra) row.source.id = 1000000; value.events.push(...extra); }
    if (mutation === 'response-cookie-changed') value.events.find(row => row.source.id === main && row.type === E.HTTP_TRANSACTION_READ_RESPONSE_HEADERS).params.headers = value.events.find(row => row.source.id === main && row.type === E.HTTP_TRANSACTION_READ_RESPONSE_HEADERS).params.headers.map(row => /^set-cookie:/i.test(row) ? row + '-ALTERED' : row);
    if (mutation.startsWith('request-cookie-')) { const row = value.events.find(row => row.source.id === sw && row.type === E.HTTP_TRANSACTION_SEND_REQUEST_HEADERS); row.params.headers = mutation === 'request-cookie-missing' ? row.params.headers.filter(line => !/^cookie:/i.test(line)) : row.params.headers.map(line => /^cookie:/i.test(line) ? line + '-ALTERED' : line); }
    if (mutation === 'missing-lifetime-end') value.events = value.events.filter(row => !(row.source.id === sw && row.type === E.REQUEST_ALIVE && row.phase === 2));
    if (mutation === 'redirect-changed') value.events.find(row => row.type === E.URL_REQUEST_REDIRECTED).params.location += '-ALTERED';
    if (mutation === 'reversed-delegate') for (const row of value.events.filter(row => row.source.id === sw && row.type === E.URL_REQUEST_DELEGATE_RESPONSE_STARTED)) row.phase = row.phase === 1 ? 2 : 1;
    if (mutation === 'missing-delegate-end') value.events = value.events.filter(row => !(row.source.id === sw && row.type === E.URL_REQUEST_DELEGATE_RESPONSE_STARTED && row.phase === 2));
    if (mutation === 'body-before-delegate') { const at = value.events.findIndex(row => row.source.id === sw && row.type === E.URL_REQUEST_JOB_FILTERED_BYTES_READ); const [body] = value.events.splice(at, 1); const before = value.events.findIndex(row => row.source.id === sw && row.type === E.URL_REQUEST_DELEGATE_RESPONSE_STARTED && row.phase === 1); body.time = value.events[before].time; value.events.splice(before, 0, body); }
    if (mutation === 'unknown-event') { const at = value.events.findIndex(row => row.source.id === sw && row.type === E.URL_REQUEST_START_JOB && row.phase === 1); const extra = structuredClone(value.events[at]); extra.type = 999999; value.events.splice(at + 1, 0, extra); }
    if (mutation === 'invalid-phase') value.events.find(row => row.source.id === sw && row.type === E.HTTP_TRANSACTION_READ_BODY).phase = 7;
    if (mutation === 'missing-intermediate-end') value.events = value.events.filter(row => !(row.source.id === sw && row.type === E.HTTP_CACHE_GET_BACKEND && row.phase === 2));
    assert.throws(() => mutation === 'truncated-json' ? parse(JSON.stringify(value).slice(0, -1)) : reconcile(value, server));
    result.push({ mutation, status: 'PASS_REFUSED_MODIFIED_RETAINED_OBSERVATION' });
  }
  return result;
}
function main() {
  const sourceAtStart = pin(__filename);
  const offlineCommit = execFileSync('/usr/bin/git', ['rev-parse', 'HEAD'], { cwd: ROOT, encoding: 'utf8', timeout: 5000 }).trim();
  assert.deepEqual(execFileSync('/usr/bin/git', ['show', offlineCommit + ':' + path.relative(ROOT, __filename)], { cwd: ROOT, timeout: 5000 }), fs.readFileSync(__filename));
  const id = process.argv[2]; assert.match(id || '', /^[0-9]{13}$/);
  const folder = path.join(BASE, 'probe-' + id); const capture = load(path.join(folder, 'results.json')); const worker = load(path.join(folder, 'worker-results.json'));
  const inputs = Object.fromEntries(['results.json', 'worker-results.json', 'netlog.json', 'server-requests.json', 'raw-cdp.json', 'source-at-start.json', 'binaries-at-start.json'].map(name => [path.relative(ROOT, path.join(folder, name)), pin(path.join(folder, name))]));
  assert.equal(capture.status, 'PASS_PRIVATE_DIAGNOSTIC_CAPTURE_ONLY'); assert.equal(capture.terminal.code, 0); assert.ok(capture.group_cleanup.stopped && capture.fixture_closed); assert.deepEqual(capture.group_cleanup.errors, []);
  assert.equal(worker.status, capture.status); assert.equal(worker.browser_terminal.code, 0); assert.ok(worker.browser_stdio_closed && worker.pipe_closed && !worker.setup_tasks_pending && !worker.attachment_error); assert.deepEqual(worker.cleanup_errors, []);
  assert.equal(worker.version.product, 'HeadlessChrome/153.0.8010.12'); assert.equal(worker.version.revision, '@971a7443b0c9b0a9b2860529b33331b76077ec62');
  assert.deepEqual(capture.source_start, sources()); assert.deepEqual(capture.source_start, capture.source_end); assert.deepEqual(worker.source_start, capture.source_start); assert.deepEqual(worker.source_end, capture.source_start);
  assert.deepEqual(capture.binaries_start, capture.binaries_end); assert.deepEqual(worker.binaries_start, capture.binaries_start); assert.deepEqual(worker.binaries_end, capture.binaries_start);
  for (const [name, expected] of Object.entries(worker.launch)) if (name === 'executable') assert.deepEqual(pin(expected), capture.binaries_start.chromium);
  assert.deepEqual(pin(worker.launch.node.path), capture.binaries_start.node);
  assert.deepEqual(pin(path.join(folder, 'netlog.json')), worker.netlog_closed_file); assert.deepEqual(capture.closed_netlog, worker.netlog_closed_file);
  PHASE = 'RECONCILE';
  const text = fs.readFileSync(path.join(folder, 'netlog.json'), 'utf8'); const log = parse(text); const server = load(path.join(folder, 'server-requests.json'));
  if (process.argv[3] === '--negative-cookie') log.events.find(row => row.type === log.constants.logEventTypes.HTTP_TRANSACTION_READ_RESPONSE_HEADERS && row.params.headers.some(line => /^set-cookie:/i.test(line))).params.headers.push('Set-Cookie: PRIVATE_NEGATIVE_SENTINEL=DO_NOT_PROJECT');
  const observed = reconcile(log, server); const negatives = controls(log, server);
  const cdp = load(path.join(folder, 'raw-cdp.json')).journal.filter(row => row.kind === 'received' && row.message?.method === 'Network.requestWillBeSent').map(row => row.message.params.request.url);
  const missing = server.filter(row => !cdp.includes(row.url)).map(row => new URL(row.url).pathname); assert.deepEqual(missing, ['/sw.js']); assert.equal(cdp.length, 4);
  const out = path.join(BASE, 'review-' + id + '-' + Date.now()); fs.mkdirSync(out, { mode: 0o700 });
  assert.deepEqual(pin(__filename), sourceAtStart);
  assert.equal(execFileSync('/usr/bin/git', ['rev-parse', 'HEAD'], { cwd: ROOT, encoding: 'utf8', timeout: 5000 }).trim(), offlineCommit);
  const report = { schema: 'skyyrose.private-netlog-diagnostic-review.v1', status: 'PASS_BOUNDED_DIAGNOSTIC_RECONCILIATION_ONLY', authentication: 'NOT_APPLICABLE', capture_source_commit: capture.source_commit, offline_source_commit: offlineCommit, offline_source: { path: path.relative(ROOT, __filename), ...pin(__filename) }, input_pins: inputs, observed, cdp: { requests: cdp.length, missing_paths: missing, verdict: 'TARGET_CDP_INITIAL_SCRIPT_GAP_RETAINED' }, controls: negatives, completeness: 'UNKNOWN_DIAGNOSTIC_FIXTURE_ONLY', policy: 'UNKNOWN_NO_ACCEPTANCE_CONTRACT', sanitation: 'UNKNOWN_RAW_REMAINS_PRIVATE', cleanup: 'PASS_OWNED_PROCESSES_STOPPED' };
  for (const [name, expected] of Object.entries(inputs)) assert.deepEqual(pin(path.join(ROOT, name)), expected);
  fs.writeFileSync(path.join(out, 'results.json'), JSON.stringify(report, null, 2) + '\n', { flag: 'wx', mode: 0o600 });
  console.log(JSON.stringify({ status: report.status, folder: out })); return report;
}
if (require.main === module) { try { main(); } catch (error) { const id = /^[0-9]{13}$/.test(process.argv[2] || '') ? process.argv[2] : 'invalid'; const file = path.join(BASE, 'offline-failure-' + id + '-' + Date.now() + '.json'); try { fs.writeFileSync(file, JSON.stringify({ phase: PHASE, type: error.name, stack: error.stack }) + '\n', { flag: 'wx', mode: 0o600 }); } catch {} console.error(JSON.stringify({ status: 'FAIL_OFFLINE_DIAGNOSTIC_REVIEW', code: PHASE })); process.exitCode = 1; } }
module.exports = { reconcile, controls, parse, header };
