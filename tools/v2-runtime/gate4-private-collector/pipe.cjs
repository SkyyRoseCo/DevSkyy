'use strict';
const { EventEmitter } = require('node:events');
class Pipe extends EventEmitter {
  constructor(child, journal) {
    super(); this.child = child; this.journal = journal; this.pending = new Map();
    this.next = 0; this.buffer = Buffer.alloc(0); this.closed = false; this.failure = null; this.closing = false;
    child.stdio[4].on('data', data => this.consume(data));
    child.stdio[4].on('end', () => { this.closed = true; if (!this.closing || this.pending.size || this.buffer.length) this.fail(Error('Unexpected or truncated pipe EOF')); });
    child.stdio[4].on('error', error => this.fail(error));
    child.stdio[3].on('error', error => this.fail(error));
    child.once('exit', () => { if (!this.closing) this.fail(Error('Unexpected browser exit')); });
  }
  expectClose() { this.closing = true; }
  fail(error) {
    this.failure ||= error; this.journal.push({ kind: 'transport-failure', message: error.message });
    for (const pending of this.pending.values()) { clearTimeout(pending.timer); pending.reject(error); }
    this.pending.clear();
  }
  consume(data) {
    try {
      this.buffer = Buffer.concat([this.buffer, data]);
      if (this.buffer.length > 16 * 1024 * 1024) throw Error('Pipe buffer exceeded');
      let at;
      while ((at = this.buffer.indexOf(0)) >= 0) {
        const chunk = this.buffer.subarray(0, at); this.buffer = this.buffer.subarray(at + 1);
        if (!chunk.length || chunk.length > 8 * 1024 * 1024) throw Error('Invalid pipe frame length');
        const message = JSON.parse(chunk.toString('utf8'));
        if (this.journal.length >= 20000) throw Error('Journal budget exceeded');
        this.journal.push({ kind: 'received', sequence: this.journal.length + 1, epoch: Date.now(), message });
        if (Object.hasOwn(message, 'id')) {
          const pending = this.pending.get(message.id);
          if (!pending || pending.session !== message.sessionId) throw Error('Unknown or mismatched response identity');
          this.pending.delete(message.id); clearTimeout(pending.timer);
          message.error ? pending.reject(Object.assign(Error(message.error.message), { protocol: message.error })) : pending.resolve(message.result || {});
        } else {
          if (typeof message.method !== 'string') throw Error('Malformed protocol event');
          this.emit('event', message);
        }
      }
    } catch (error) { this.fail(error); }
  }
  send(method, params = {}, sessionId) {
    if (this.failure || this.closed) return Promise.reject(this.failure || Error('Pipe closed'));
    if (this.pending.size >= 128) return Promise.reject(Error('Pending command budget exceeded'));
    const id = ++this.next; const message = { id, method, params, ...(sessionId ? { sessionId } : {}) };
    this.journal.push({ kind: 'sent', sequence: this.journal.length + 1, epoch: Date.now(), message });
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => this.fail(Error('Protocol command deadline: ' + method)), 10000);
      this.pending.set(id, { resolve, reject, timer, session: sessionId });
      this.child.stdio[3].write(JSON.stringify(message) + '\0', error => { if (error) this.fail(error); });
    });
  }
}
module.exports = { Pipe };
