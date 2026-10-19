'use strict';
// Mock-only cleanup and identity controls; no browser or network activity.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { pin, terminateOwned, finalIdentity } = require('./netlog.cjs');
const errors = [];
terminateOwned({ kill() { throw Error('Synthetic termination exception'); } }, errors);
assert.deepEqual(errors, ['Owned browser termination failed: Error']);
let finalized = false;
try { terminateOwned({ kill() { throw Error('Synthetic termination exception'); } }, []); } finally { finalized = true; }
assert.equal(finalized, true);
const source = pin(path.join(__dirname, 'netlog.cjs'));
const identity = { node: source, chromium: source };
finalIdentity(identity, structuredClone(identity), source, structuredClone(source));
const controls = ['guarded-kill-throw-retains-finalization'];
for (const mutation of ['binary-pin-drift', 'closed-file-drift']) {
  const actual = structuredClone(identity); const file = structuredClone(source);
  if (mutation === 'binary-pin-drift') actual.chromium.sha256 = '0'.repeat(64); else file.bytes++;
  assert.throws(() => finalIdentity(identity, actual, source, file)); controls.push(mutation);
}
const root = path.resolve(__dirname, '../../..');
const base = path.join(root, '.artifacts/release-gates-20261019/gate4-private-collector-netlog');
fs.mkdirSync(base, { recursive: true, mode: 0o700 });
const file = path.join(base, 'source-controls-' + Date.now() + '.json');
fs.writeFileSync(file, JSON.stringify({ status: 'PASS_MOCK_ONLY_SOURCE_CONTROLS', authentication: 'NOT_APPLICABLE', source, controls, control_source: pin(__filename) }, null, 2) + '\n', { flag: 'wx', mode: 0o600 });
console.log(JSON.stringify({ status: 'PASS_MOCK_ONLY_SOURCE_CONTROLS', file }));
