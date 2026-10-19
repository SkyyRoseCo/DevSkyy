const { test } = require('node:test');
const assert = require('node:assert/strict');
const { chromium } = require('../v2-runtime/phase3b-browser/runtime.cjs').requireQa('playwright');
const { inertSnapshot } = require('./inert-snapshot.cjs');

test('repeated inert snapshots retain privacy and cause no requests, errors, upgrades or live mutations', async () => {
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage();
    const requests = [];
    const errors = [];
    page.on('request', request => requests.push(request.url()));
    page.on('pageerror', error => errors.push(error.message));
    await page.route('**/*', route => route.fulfill({ contentType: 'image/svg+xml', body: '<svg xmlns="http://www.w3.org/2000/svg"/>' }));
    await page.setContent(`<input value="private-input"><textarea>private-note</textarea><a href="http://snapshot.test/item?token=private-token#private-hash">Item</a><img src="http://snapshot.test/image?private-query" onload="window.loaded=(window.loaded||0)+1"><x-snapshot></x-snapshot><script>window.upgrades=0;customElements.define('x-snapshot',class extends HTMLElement{constructor(){super();window.upgrades++}})</script>`);
    await page.waitForFunction(() => window.loaded === 1);
    await page.evaluate(() => { document.documentElement.setAttribute('onload', 'window.rootLoaded=1'); document.documentElement.setAttribute('data-token', 'private-root-token'); });
    const before = await page.evaluate(() => ({ html: document.documentElement.outerHTML, loaded: window.loaded, upgrades: window.upgrades }));
    const requestCount = requests.length;
    const errorCount = errors.length;
    for (let i = 0; i < 5; i++) {
      const snapshot = await page.evaluate(inertSnapshot);
      assert.ok(snapshot.startsWith('<!doctype html>'));
      assert.ok(snapshot.includes('[REDACTED]'));
      assert.ok(snapshot.includes('[INLINE SCRIPT REDACTED]'));
      assert.ok(!/private-input|private-note|private-token|private-query|private-hash|private-root-token|onload=/.test(snapshot));
    }
    // Complete another event-loop turn so image events cannot hide behind evaluate completion.
    await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
    assert.equal(requests.length, requestCount);
    assert.equal(errors.length, errorCount);
    assert.deepEqual(await page.evaluate(() => ({ html: document.documentElement.outerHTML, loaded: window.loaded, upgrades: window.upgrades })), before);
    await page.evaluate(() => setTimeout(() => { throw new Error('genuine-page-error'); }, 0));
    await page.waitForFunction(() => true);
    for (let i = 0; i < 5 && !errors.includes('genuine-page-error'); i++) await page.evaluate(() => new Promise(resolve => requestAnimationFrame(resolve)));
    assert.ok(errors.includes('genuine-page-error'), 'genuine errors remain observable');
  } finally {
    await browser.close();
  }
});

test('retained legacy sanitizer reproduces HANDLER observer errors on an isolated image fixture', async () => {
  const legacy = require('../../tasks/initial-commerce-release-20261002/offline-diagnosis/legacy-sanitizer.json');
  assert.equal(legacy.source_sha256, '61298598e8787678eccd7b301dd0982c5a1340ac9178c9ede258a207371e64eb');
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage();
    const requests = [];
    const errors = [];
    page.on('request', request => requests.push(request.url()));
    page.on('pageerror', error => errors.push(error.message));
    await page.route('**/*', route => route.fulfill({ contentType: 'image/svg+xml', body: '<svg xmlns="http://www.w3.org/2000/svg"/>' }));
    await page.setContent('<img src="http://snapshot.test/item?secret=fixture" onload="window.loaded=1">');
    await page.waitForFunction(() => window.loaded === 1);
    const before = await page.content();
    const requestCount = requests.length;
    const snapshot = await page.evaluate(`(${legacy.DOM_SANITIZER})()`);
    assert.ok(snapshot.includes('[INLINE HANDLER REDACTED]'));
    for (let i = 0; i < 10 && !errors.some(error => error.includes('HANDLER')); i++) await page.evaluate(() => new Promise(resolve => requestAnimationFrame(resolve)));
    assert.ok(errors.some(error => error.includes('HANDLER')), JSON.stringify(errors));
    assert.ok(requests.length > requestCount, 'legacy active-document clone initiated an extra image request');
    assert.equal(await page.content(), before, 'live DOM stayed unchanged; error came from observation side effect');
  } finally {
    await browser.close();
  }
});
