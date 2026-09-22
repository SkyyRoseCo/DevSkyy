/* Isolated real-browser regression tests. Set V2_QA_PACKAGE to existing QA runtime. */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('./runtime.cjs').requireQa('playwright');
const code = fs.readFileSync(
  path.resolve(__dirname, '../../../wordpress-theme/skyyrose-flagship-2/assets/js/quick-view-commerce.js'),
  'utf8'
);
const shell = `<dialog id="sr2-quick-view-dialog"><div class="product"><p data-quick-view-price></p><p data-quick-view-availability></p><img data-quick-view-image src="/original.jpg" alt="Original"><p data-quick-view-status data-loading="Loading" data-ready="Ready" data-error="Open product"></p><div data-quick-view-purchase></div><a data-quick-view-url href="/product/a/">Open piece</a></div></dialog>`;
const product = (type = 'simple', extra = '') =>
  `<meta name="sr2-quick-view-product" content="42" data-product-type="${type}"><div id="product-42"><div class="summary"><p class="price">$25</p><p class="stock">In stock</p><form class="cart ${type === 'variable' ? 'variations_form' : ''}" action="/product/a/" method="post"><label for="quantity">Quantity</label><input id="quantity" name="quantity" value="1"><button name="add-to-cart" value="42">Add to bag</button>${extra}</form></div></div>`;
async function fixture(run) {
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage();
    await page.route('http://quick-view.test/**', r => r.fulfill({ contentType: 'text/html', body: shell }));
    await page.goto('http://quick-view.test/');
    await page.addScriptTag({ content: code });
    await run(page);
  } finally {
    await browser.close();
  }
}
async function open(page) {
  await page.evaluate(() => document.querySelector('dialog').showModal());
}
async function ready(page, message) {
  await page.waitForFunction(m => document.querySelector('[data-quick-view-status]').textContent === m, message);
}
test('native form, authoritative price, local POST, isolated label IDs, no duplicate initialization', () =>
  fixture(async page => {
    await page.route('**/product/a/', r => r.fulfill({ contentType: 'text/html', body: product() }));
    await page.addScriptTag({ content: code });
    await open(page);
    await ready(page, 'Ready');
    assert.equal(await page.locator('[data-quick-view-price]').textContent(), '$25');
    assert.equal(await page.locator('[data-quick-view-purchase] form').count(), 1);
    assert.equal(await page.locator('form').getAttribute('method'), 'post');
    const id = await page.locator('input').getAttribute('id');
    assert.equal(await page.locator('label').getAttribute('for'), id);
    const request = page.waitForRequest(r => r.method() === 'POST');
    await page.locator('button').click();
    assert.match((await request).postData(), /add-to-cart=42/);
  }));
test('ineligible, unsupported, scripted and cross-origin forms fail to PDP link', () =>
  fixture(async page => {
    for (const html of [
      product('grouped'),
      product().replace('sr2-quick-view-product', 'unpublished'),
      product('simple', '<script>window.pwned=1</script>'),
      product().replace('action="/product/a/"', 'action="https://evil.test/"'),
    ]) {
      await page.route('**/product/a/', r => r.fulfill({ contentType: 'text/html', body: html }));
      await open(page);
      await ready(page, 'Open product');
      assert.equal(await page.locator('form.cart').count(), 0);
      assert.equal(await page.evaluate(() => window.pwned), undefined);
      await page.evaluate(() => document.querySelector('dialog').close());
    }
  }));
test('closing aborts stale loading; reopening recovers; missing variation plugin falls back', () =>
  fixture(async page => {
    await page.route('**/product/a/', async r => {
      await new Promise(resolve => setTimeout(resolve, 150));
      await r.fulfill({ contentType: 'text/html', body: product() });
    });
    await open(page);
    await page.evaluate(() => document.querySelector('dialog').close());
    await page.waitForTimeout(200);
    assert.equal(await page.locator('form.cart').count(), 0);
    await page.unroute('**/product/a/');
    await page.route('**/product/a/', r => r.fulfill({ contentType: 'text/html', body: product('variable') }));
    await open(page);
    await ready(page, 'Open product');
  }));
test('native variation plugin initializes once and images stay inside dialog', () =>
  fixture(async page => {
    await page.evaluate(() => {
      document.body.insertAdjacentHTML('beforeend', '<img id="pdp-image" src="/untouched.jpg">');
      const events = {};
      window.events = events;
      window.jQuery = element => ({
        empty() {
          element.replaceChildren();
        },
        on(name, handler) {
          events[name] = handler;
          return this;
        },
        wc_variation_form() {
          window.calls = (window.calls || 0) + 1;
          events['found_variation.sr2QuickView']({}, { image: { src: '/variation.jpg', alt: 'Native variation' } });
        },
      });
      window.jQuery.fn = { wc_variation_form() {} };
    });
    await page.route('**/product/a/', r => r.fulfill({ contentType: 'text/html', body: product('variable') }));
    await open(page);
    await ready(page, 'Ready');
    assert.equal(await page.evaluate(() => window.calls), 1);
    assert.match(await page.locator('[data-quick-view-image]').getAttribute('src'), /variation.jpg$/);
    assert.equal(await page.locator('#pdp-image').getAttribute('src'), '/untouched.jpg');
    await page.evaluate(() => {
      window.oldEvents = { ...window.events };
      document.querySelector('dialog').close();
    });
    await open(page);
    await ready(page, 'Ready');
    await page.evaluate(() => {
      window.oldEvents['found_variation.sr2QuickView']({}, { image: { src: '/stale.jpg' } });
      window.oldEvents['reset_data.sr2QuickView']();
    });
    assert.match(await page.locator('[data-quick-view-image]').getAttribute('src'), /variation.jpg$/);
  }));

async function lazyFixture(page, source = '/native-variation.js') {
  await page.evaluate(src => {
    window.jQuery = element => ({
      empty() {
        element.replaceChildren();
      },
      on() {
        return this;
      },
      wc_variation_form() {
        window.calls = (window.calls || 0) + 1;
      },
    });
    window.jQuery.fn = {};
    const marker = document.createElement('script');
    marker.type = 'text/plain';
    marker.dataset.sr2VariationSrc = src;
    document.head.append(marker);
  }, source);
  await page.route('**/product/a/', r => r.fulfill({ contentType: 'text/html', body: product('variable') }));
}
test('native runtime loads on variable intent once and reopening reuses it', () =>
  fixture(async page => {
    let loads = 0;
    await lazyFixture(page);
    await page.route('**/native-variation.js', r => {
      loads += 1;
      return r.fulfill({
        contentType: 'application/javascript',
        body: 'window.jQuery.fn.wc_variation_form = function() {};',
      });
    });
    assert.equal(loads, 0);
    await open(page);
    await ready(page, 'Ready');
    assert.equal(loads, 1);
    await page.evaluate(() => document.querySelector('dialog').close());
    await open(page);
    await ready(page, 'Ready');
    assert.equal(loads, 1);
    assert.equal(await page.evaluate(() => window.calls), 2);
  }));
test('runtime failure falls back without repeated download', () =>
  fixture(async page => {
    let loads = 0;
    await lazyFixture(page);
    await page.route('**/native-variation.js', r => {
      loads += 1;
      return r.abort();
    });
    await open(page);
    await ready(page, 'Open product');
    await page.evaluate(() => document.querySelector('dialog').close());
    await open(page);
    await ready(page, 'Open product');
    assert.equal(loads, 1);
    assert.equal(await page.locator('form.cart').count(), 0);
  }));
test('closing while runtime loads does not insert a stale form', () =>
  fixture(async page => {
    let release;
    const waiting = new Promise(resolve => {
      release = resolve;
    });
    let requested;
    const started = new Promise(resolve => {
      requested = resolve;
    });
    await lazyFixture(page);
    await page.route('**/native-variation.js', async r => {
      requested();
      await waiting;
      await r.fulfill({
        contentType: 'application/javascript',
        body: 'window.jQuery.fn.wc_variation_form = function() {};',
      });
    });
    await open(page);
    await started;
    await page.evaluate(() => document.querySelector('dialog').close());
    release();
    await page.waitForFunction(() => !!window.jQuery.fn.wc_variation_form);
    assert.equal(await page.locator('form.cart').count(), 0);
    await open(page);
    await ready(page, 'Ready');
    assert.equal(await page.evaluate(() => window.calls), 1);
  }));

test('off-origin runtime marker never requests executable code', () =>
  fixture(async page => {
    let externalRequests = 0;
    await lazyFixture(page, 'https://external.test/variation.js');
    await page.route('https://external.test/**', r => {
      externalRequests += 1;
      return r.abort();
    });
    await open(page);
    await ready(page, 'Open product');
    assert.equal(externalRequests, 0);
    assert.equal(await page.locator('form.cart').count(), 0);
  }));
test('native submission becomes busy once and later extension cancellation restores it', () =>
  fixture(async page => {
    await page.route('**/product/a/', r => r.fulfill({ contentType: 'text/html', body: product() }));
    await open(page);
    await ready(page, 'Ready');
    const states = await page.evaluate(async () => {
      const form = document.querySelector('form.cart');
      const first = new Event('submit', { bubbles: true, cancelable: true });
      form.dispatchEvent(first);
      const second = new Event('submit', { bubbles: true, cancelable: true });
      form.dispatchEvent(second);
      const duplicateBlocked = second.defaultPrevented;
      delete form.dataset.submitting;
      const cancel = event => event.preventDefault();
      document.addEventListener('submit', cancel, { once: true });
      form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
      await Promise.resolve();
      return { duplicateBlocked, recovered: !form.dataset.submitting };
    });
    assert.equal(states.duplicateBlocked, true);
    assert.equal(states.recovered, true);
  }));
