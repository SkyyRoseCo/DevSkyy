'use strict';
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const cp = require('node:child_process');
const { processes } = require('./context-ownership.cjs');
const { cleanGroup } = require('./capability.cjs');
const PYTHON = '/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/bin/python3.14';
const PYTHON_SHA = '87d4df53fd91304be5bac391fb204643c36b7df2023c04a0953bcbc7d4fdf634';
const PYTHON_IMAGE = '/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python';
const PYTHON_IMAGE_SHA = 'e89d60f8ccee9db684801330198797723db2ac378cd53e5cfe523128feb76599';
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
const sha = body => crypto.createHash('sha256').update(body).digest('hex');
function image(pid) {
  assert.ok(Number.isSafeInteger(pid) && pid > 1); assert.equal(sha(fs.readFileSync(PYTHON)), PYTHON_SHA); assert.equal(sha(fs.readFileSync(PYTHON_IMAGE)), PYTHON_IMAGE_SHA);
  // ABI matches the retained macOS SDK libproc.h proc_pidpath declaration.
  const script = "import ctypes,sys; l=ctypes.CDLL('/usr/lib/libproc.dylib'); f=l.proc_pidpath; f.argtypes=[ctypes.c_int,ctypes.c_void_p,ctypes.c_uint32]; f.restype=ctypes.c_int; b=ctypes.create_string_buffer(4096); n=f(int(sys.argv[1]),b,4096); sys.exit(1) if n<=0 else print(b.value.decode())";
  return cp.execFileSync(PYTHON, ['-I', '-c', script, String(pid)], { encoding: 'utf8', timeout: 5000, stdio: ['ignore', 'pipe', 'pipe'] }).trim();
}
function readRegular(file, limit) {
  const fd = fs.openSync(file, fs.constants.O_RDONLY | fs.constants.O_NOFOLLOW | fs.constants.O_NONBLOCK);
  try {
    const before = fs.fstatSync(fd, { bigint: true });
    assert.ok(before.isFile() && (before.mode & 0o777n) === 0o600n && before.uid === BigInt(process.getuid()) && before.size <= BigInt(limit));
    const body = Buffer.alloc(limit + 1); const size = fs.readSync(fd, body, 0, body.length, 0);
    const after = fs.fstatSync(fd, { bigint: true }); const current = fs.lstatSync(file, { bigint: true });
    const identity = value => [value.dev, value.ino, value.size, value.mtimeNs].map(String);
    assert.deepEqual(identity(before), identity(after)); assert.deepEqual(identity(before), identity(current));
    assert.ok(current.isFile() && !current.isSymbolicLink() && BigInt(size) === before.size && size <= limit);
    return body.subarray(0, size);
  } finally { fs.closeSync(fd); }
}
function pythonJSON(value) {
  if (Array.isArray(value)) return '[' + value.map(pythonJSON).join(', ') + ']';
  if (value && typeof value === 'object') return '{' + Object.entries(value).map(([key, row]) => pythonJSON(key) + ': ' + pythonJSON(row)).join(', ') + '}';
  return JSON.stringify(value).replace(/[\u007f-\uffff]/g, char => '\\u' + char.charCodeAt(0).toString(16).padStart(4, '0'));
}
function inspectBroker(folder, launcher, target, targetSHA, parentPid, nonce, spawned) {
  assert.equal(fs.realpathSync(folder), folder); assert.equal(fs.statSync(folder).mode & 0o777, 0o700);
  const file = path.join(folder, 'broker-registration.json'); const raw = readRegular(file, 65536); const row = JSON.parse(raw);
  assert.equal(raw.toString(), pythonJSON(row) + '\n', 'Noncanonical/duplicate registration fields');
  assert.deepEqual(Object.keys(row).sort(), ['args', 'environment_sha256', 'group', 'kind', 'launcher_sha256', 'nonce', 'parent', 'pid', 'pipes', 'profile', 'target', 'target_sha256'].sort());
  assert.equal(row.kind, 'pre-exec-registration'); assert.equal(row.nonce, nonce); assert.equal(row.target, target); assert.equal(row.target_sha256, targetSHA);
  assert.equal(sha(fs.readFileSync(target)), targetSHA); assert.equal(row.launcher_sha256, sha(fs.readFileSync(launcher)));
  assert.ok(Number.isSafeInteger(row.pid) && row.pid > 1 && row.group === row.pid && row.parent === parentPid);
  assert.match(row.environment_sha256, /^[a-f0-9]{64}$/); assert.ok(Array.isArray(row.args) && row.args.every(arg => typeof arg === 'string'));
  assert.equal(fs.realpathSync(row.profile), row.profile); assert.ok(row.profile.startsWith(fs.realpathSync(path.join(folder, 'tmp')) + path.sep));
  assert.deepEqual(row.args.filter(arg => arg.startsWith('--user-data-dir=')), ['--user-data-dir=' + row.profile]); assert.ok(row.args.includes('--remote-debugging-pipe'));
  assert.deepEqual(Object.keys(row.pipes).sort(), ['3', '4']);
  for (const pipe of Object.values(row.pipes)) { assert.deepEqual(Object.keys(pipe).sort(), ['device', 'inheritable', 'inode', 'type']); assert.ok(pipe.inheritable && [4096, 49152].includes(pipe.type) && Number.isSafeInteger(pipe.device) && Number.isSafeInteger(pipe.inode)); }
  assert.ok(spawned && spawned.kind === 'browser-spawn' && spawned.token === nonce && spawned.pid === row.pid && spawned.executable === launcher && spawned.profile === row.profile); assert.deepEqual(spawned.args, row.args);
  const current = processes().find(item => item.pid === row.pid);
  assert.ok(current && current.group === row.pid && current.parent === parentPid && current.command.includes(launcher) && current.command.includes(row.profile));
  assert.equal(image(row.pid), PYTHON_IMAGE);
  return { ...row, birth: current.birth, broker_command: current.command, registration_sha256: sha(raw), launcher, image_before: PYTHON_IMAGE };
}
function acknowledge(record, folder) {
  assert.equal(sha(readRegular(path.join(folder, 'broker-registration.json'), 65536)), record.registration_sha256);
  const body = Buffer.from(JSON.stringify({ kind: 'pre-exec-ack', nonce: record.nonce, pid: record.pid, group: record.group, registration_sha256: record.registration_sha256 }) + '\n');
  const pending = path.join(folder, 'broker-ack.partial'); const file = path.join(folder, 'broker-ack.json'); const fd = fs.openSync(pending, 'wx', 0o600);
  try { fs.writeFileSync(fd, body); fs.fsyncSync(fd); } finally { fs.closeSync(fd); }
  fs.linkSync(pending, file); fs.unlinkSync(pending);
}
async function takeover(record, timeout = 10000) {
  const end = Date.now() + timeout;
  while (Date.now() < end) {
    const current = processes().find(item => item.pid === record.pid); assert.ok(current && current.group === record.group && current.birth === record.birth, 'Registered process identity lost before takeover');
    const executable = image(record.pid);
    if (executable === record.target) { assert.ok(current.command.includes(record.profile)); assert.equal(sha(fs.readFileSync(record.target)), record.target_sha256); return { pid: record.pid, group: current.group, birth: current.birth, image: executable, command: current.command }; }
    assert.equal(executable, record.image_before, 'Unexpected image after registration'); await pause(20);
  }
  throw Error('Pinned executable takeover deadline');
}
async function closeRegistered(record, folder) {
  const current = processes().find(item => item.pid === record.pid);
  if (current) { assert.equal(current.group, record.group); assert.equal(current.birth, record.birth); assert.ok([record.image_before, record.target].includes(image(record.pid)), 'Owned image drift'); }
  // Registration predates ACK. A missing leader does not discard its known group.
  return cleanGroup({ pid: record.pid }, folder);
}
async function closeAll(records, folder, closer = closeRegistered) {
  const results = []; const errors = [];
  for (const record of records) { try { results.push({ pid: record.pid, ...await closer(record, folder) }); } catch (error) { errors.push({ pid: record.pid, error: error.message }); } }
  return { results, errors };
}
function observeTerminal(child) {
  // Resolve typed outcomes immediately; a spawn error must never become an
  // unhandled rejection while the caller is still polling registration.
  return new Promise(resolve => { child.once('error', error => resolve({ code: null, signal: null, spawn_error: error.code || error.name })); child.once('close', (code, signal) => resolve({ code, signal })); });
}
async function stopWorkerAndCloseUnacked(worker, folder, launcher, target, allowUnacked) {
  const result = { worker: null, brokers: [], errors: [], final_census: [] };
  try { result.worker = worker ? await cleanGroup(worker, folder) : { stopped: true, errors: [] }; } catch (error) { result.errors.push(error.message); }
  // Quiesce the spawner first. A census before this point can miss a detached
  // broker launched during the worker's shutdown grace interval.
  if (allowUnacked) {
    try {
      assert.ok(result.worker?.stopped, 'Worker did not quiesce before broker census');
      assert.ok(!fs.existsSync(path.join(folder, 'broker-ack.json')), 'Unregistered target ACK exists');
      const candidates = processes().filter(row => row.command.includes(launcher) && row.command.includes(folder));
      for (const row of candidates) {
        try { assert.equal(row.group, row.pid); assert.equal(image(row.pid), PYTHON_IMAGE); result.brokers.push({ pid: row.pid, ...await cleanGroup({ pid: row.pid }, folder) }); }
        catch (error) { result.errors.push(error.message); }
      }
    } catch (error) { result.errors.push(error.message); }
  }
  try { result.final_census = processes().filter(row => row.command.includes(folder) && (row.command.includes(launcher) || row.command.includes(target))); assert.deepEqual(result.final_census, []); }
  catch (error) { result.errors.push(error.message); }
  return result;
}
module.exports = { PYTHON, PYTHON_SHA, PYTHON_IMAGE, PYTHON_IMAGE_SHA, image, readRegular, pythonJSON, inspectBroker, acknowledge, takeover, closeRegistered, closeAll, observeTerminal, stopWorkerAndCloseUnacked };
