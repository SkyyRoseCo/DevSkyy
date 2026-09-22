'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const zlib = require('node:zlib');
const { localUrl, decode, resourceUrls } = require('./verify.cjs');
test('exact authority guard rejects remote, protocol-relative, other ports and credentials', () => {
  assert.equal(localUrl('/shop/').origin, 'http://127.0.0.1:18308');
  for (const url of ['https://example.com/', '//example.com/', 'http://127.0.0.1:18303/', 'http://user@127.0.0.1:18308/', 'http://127.0.0.1.evil.test:18308/']) assert.throws(() => localUrl(url));
});
test('gzip decoding preserves exact bytes and rejects corrupt/unexpected encodings', () => {
  const bytes = Buffer.from('Exact CSS/JS/HTML bytes\0é—\n'.repeat(40));
  assert.deepEqual(decode(zlib.gzipSync(bytes), 'gzip'), bytes);
  assert.deepEqual(decode(bytes), bytes);
  assert.throws(() => decode(Buffer.from('broken'), 'gzip'));
  assert.throws(() => decode(bytes, 'br'));
});
test('resource census rejects bypasses including srcset and dormant source URLs', () => {
  const html = Array.from({ length: 6 }, (_, i) => `<img src="/asset-${i}.webp">`).join('');
  assert.equal(resourceUrls(html).length, 6);
  for (const bad of ['<source srcset="http://127.0.0.1:18303/a.webp 640w">', '<script src="https://example.com/a.js"></script>', '<video poster="//remote.test/p.webp">']) assert.throws(() => resourceUrls(html + bad));
  assert.throws(() => resourceUrls(''));
});
test('native checkout redirects require a real local Location and errors fail', () => {
  const { htmlStatus } = require('./verify.cjs');
  const headers = { 'content-type': 'text/html' };
  assert.equal(htmlStatus('/checkout/', { status: 200, headers }), false);
  assert.equal(htmlStatus('/checkout/', { status: 302, headers: { ...headers, location: '/cart/' } }), true);
  for (const status of [404, 500]) assert.throws(() => htmlStatus('/checkout/', { status, headers }));
  for (const location of [undefined, '', ' ', 'https://example.com/']) assert.throws(() => htmlStatus('/checkout/', { status: 302, headers: { ...headers, location } }));
});
test('ordinary uninstrumented response must be successful compressed HTML', () => {
  const { ordinaryResponse } = require('./verify.cjs');
  const html = Array.from({ length: 6 }, (_, i) => `<img src="/asset-${i}.webp">`).join('');
  const good = { status: 200, headers: { 'content-type': 'text/html; charset=UTF-8', 'content-encoding': 'gzip', vary: 'Accept-Encoding' }, wire: zlib.gzipSync(html) };
  assert.doesNotThrow(() => ordinaryResponse(good));
  assert.throws(() => ordinaryResponse({ ...good, status: 500 }));
  for (const key of ['content-type', 'content-encoding', 'vary']) {
    const headers = { ...good.headers }; delete headers[key];
    assert.throws(() => ordinaryResponse({ ...good, headers }));
  }
  assert.throws(() => ordinaryResponse({ ...good, headers: { ...good.headers, 'x-v2-fixture-body-sha256': 'unexpected' } }));
});
test('range proof rejects whole-body 200, shifted bytes, wrong totals and encoded media', () => {
  const { rangeProof } = require('./verify.cjs');
  const source = Buffer.from('0123456789abcdef');
  const good = { status: 206, headers: { 'content-range': 'bytes 0-3/16', 'content-length': '4' }, wire: source.subarray(0, 4) };
  assert.doesNotThrow(() => rangeProof(good, source, 0, 3));
  assert.throws(() => rangeProof({ ...good, status: 200 }, source, 0, 3));
  assert.throws(() => rangeProof({ ...good, wire: source.subarray(1, 5) }, source, 0, 3));
  assert.throws(() => rangeProof({ ...good, headers: { ...good.headers, 'content-range': 'bytes 0-3/20' } }, source, 0, 3));
  assert.throws(() => rangeProof({ ...good, headers: { ...good.headers, 'content-encoding': 'gzip' } }, source, 0, 3));
});
test('asset inventory rejects symlink traversal instead of resolving private bytes', () => {
  const fs = require('node:fs'); const os = require('node:os'); const path = require('node:path');
  const { assetInventory } = require('./verify.cjs');
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'v2-delivery-inventory-'));
  try {
    fs.writeFileSync(path.join(directory, 'public.css'), 'body{}');
    assert.equal(assetInventory(directory).length, 1);
    fs.symlinkSync(path.join(directory, 'public.css'), path.join(directory, 'linked.css'));
    assert.throws(() => assetInventory(directory), /symlink/);
  } finally { fs.rmSync(directory, { recursive: true, force: true }); }
});
