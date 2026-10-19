'use strict';
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const { cleanGroup } = require('./capability.cjs');
function processes() {
  return execFileSync('/bin/ps', ['-axo', 'pid=,ppid=,pgid=,lstart=,command='], { encoding: 'utf8', timeout: 5000 }).split('\n').filter(Boolean).map(line => {
    const match = line.trim().match(/^(\d+)\s+(\d+)\s+(\d+)\s+(\S+\s+\S+\s+\d+\s+\S+\s+\d+)\s+(.*)$/);
    assert.ok(match, 'Unparseable process identity');
    return { pid: Number(match[1]), parent: Number(match[2]), group: Number(match[3]), birth: match[4].replace(/\s+/g, ' '), command: match[5] };
  });
}
function profileCensus(folder, executable) { return processes().filter(row => row.command.includes(folder) && row.command.includes(executable)); }
class Frames {
  constructor(consume) { this.consume = consume; this.buffer = ''; this.count = 0; this.failed = null; }
  feed(chunk) {
    assert.ok(!this.failed);
    try {
      this.buffer += chunk.toString('utf8'); assert.ok(Buffer.byteLength(this.buffer) <= 131072);
      let at;
      while ((at = this.buffer.indexOf('\n')) >= 0) {
        const frame = this.buffer.slice(0, at); this.buffer = this.buffer.slice(at + 1); assert.ok(frame.length && Buffer.byteLength(frame) <= 65536); assert.ok(++this.count <= 4); this.consume(JSON.parse(frame));
      }
    } catch (error) { this.failed = error; throw error; }
  }
  close(required = true) { assert.ok(!this.failed && !this.buffer.length && (!required || this.count > 0), 'Missing/truncated ownership channel'); }
}
function validateSpawn(record, folder, executable, workerPid, token) {
  assert.equal(record.kind, 'browser-spawn'); assert.equal(record.token, token); assert.equal(record.executable, executable);
  assert.ok(Number.isSafeInteger(record.pid) && record.pid > 1 && record.pid !== workerPid);
  assert.ok(Array.isArray(record.args) && record.args.every(value => typeof value === 'string'));
  const profile = record.args.filter(value => value.startsWith('--user-data-dir=')); assert.equal(profile.length, 1);
  assert.equal(record.profile, profile[0].slice('--user-data-dir='.length));
  const temp = fs.realpathSync(path.join(folder, 'tmp'));
  const actual = fs.realpathSync(record.profile); assert.ok(actual.startsWith(temp + path.sep));
  assert.ok(record.args.includes('--remote-debugging-pipe'));
  const current = processes().find(row => row.pid === record.pid);
  assert.ok(current && current.group === record.pid && current.parent === workerPid);
  assert.ok(current.command.includes(executable) && current.command.includes(record.profile));
  return { ...record, birth: current.birth, process_command: current.command };
}
async function closeBrowserGroup(record, folder, executable) {
  const current = processes().find(row => row.pid === record.pid);
  if (current) assert.ok(current.group === record.pid && current.birth === record.birth && current.command.includes(executable) && current.command.includes(record.profile), 'Browser identity drift');
  return cleanGroup({ pid: record.pid }, folder);
}
module.exports = { Frames, processes, profileCensus, validateSpawn, closeBrowserGroup };
