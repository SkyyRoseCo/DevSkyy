'use strict';
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '../../..');
const base = 'http://127.0.0.1:18362';
const run = process.env.SR_RELEASE_RUN || '';
assert.match(run, /^(?:[a-z0-9-]+)?$/);
const evidence = path.join(root, 'tasks/release-gates-20261019', run, 'evidence');
const fixture = JSON.parse(fs.readFileSync(path.join(root, 'tasks/release-gates-20261019/evidence/native-browser-fixture.json')));
const primary = JSON.parse(fs.readFileSync(path.join(evidence, 'browser-ten-routes/results.json')));
assert.equal(fixture.home, base);
assert.equal(primary.status, 'PASS_PRIMARY_TECHNICAL_CASES');
const out = path.join(evidence, 'browser-destinations');
fs.mkdirSync(out, { recursive: true });
const targets = new Map();
for (const item of primary.cases) for (const link of item.native_product_links) {
  const target = Object.entries(fixture.products).find(([, product]) => product.url === link.href);
  assert.ok(target);
  if (!targets.has(target[0])) targets.set(target[0], { sku: target[0], product: target[1], source_route: item.route.path, href: link.href });
}
assert.ok(targets.size > 0);
const report = { classification: 'REPRODUCED_LOCAL_NATIVE', authentication: 'NOT_APPLICABLE', primary_sha256: crypto.createHash('sha256').update(fs.readFileSync(path.join(evidence, 'browser-ten-routes/results.json'))).digest('hex'), expected_unique_destinations: targets.size, cases: [], mutations: 'NONE; read-only product pages and native option selection' };
(async () => {
  const browser = await chromium.launch();
  report.browser = await browser.version();
  try {
    const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, reducedMotion: 'reduce' });
    await context.route('**/*', route => new URL(route.request().url()).origin === base ? route.continue() : route.abort('blockedbyclient'));
    for (const target of targets.values()) {
      const item = { ...target, status: 'FAIL' };
      const page = await context.newPage();
      try {
        await page.goto(base + target.source_route, { waitUntil: 'load' });
        const decline = page.locator('#skyyrose-cookie-decline');
        if (await decline.isVisible()) await decline.tap();
        const targetLink = page.locator(`main a[href="${target.href}"]`).first();
        assert.ok(await targetLink.count() > 0);
        const [response] = await Promise.all([page.waitForNavigation({ waitUntil: 'load' }), targetLink.tap()]);
        await page.waitForURL(target.product.url, { waitUntil: 'load' });
        await page.waitForFunction(sku => document.querySelector('main .sku')?.textContent === sku, target.sku);
        // Chromium may activate a prefetched document without a new navigation
        // response event. Keep that fact explicit and read back actual HTTP too.
        item.navigation_response_status = response ? response.status() : null;
        const readback = await context.request.get(target.product.url);
        assert.equal(readback.status(), 200);
        assert.equal(readback.url(), target.product.url);
        assert.equal(page.url(), target.product.url);
        item.destination_http_status = readback.status(); item.effective_url = page.url();
        assert.equal(await page.locator('main .sku').textContent(), target.sku);
        assert.equal(await page.locator('main').getAttribute('data-collection'), target.product.collection);
        const variable = Object.keys(target.product.children).length > 0;
        if (variable) {
          const form = page.locator('form.variations_form');
          assert.equal(Number(await form.getAttribute('data-product_id')), target.product.id);
          assert.equal(Number(await form.locator('input[name="product_id"]').getAttribute('value')), target.product.id);
          const size = Object.keys(target.product.children)[0];
          await form.locator('select[name="attribute_size"]').selectOption(size);
          await page.waitForFunction(({ id }) => Number(document.querySelector('input[name="variation_id"]')?.value) === id, { id: target.product.children[size] });
          item.selected_native_child = { size, id: Number(await form.locator('input[name="variation_id"]').inputValue()) };
        } else {
          assert.equal(Number(await page.locator('main button[name="add-to-cart"]').getAttribute('value')), target.product.id);
        }
        item.native_id = target.product.id;
        await page.screenshot({ path: path.join(out, target.sku + '.png'), fullPage: false });
        item.status = 'PASS';
      } catch (error) { item.error = error.message; }
      finally { await page.close(); report.cases.push(item); fs.writeFileSync(path.join(out, 'results.json'), JSON.stringify(report, null, 2) + '\n'); console.log(item.status, target.sku, item.error || ''); }
    }
    await context.close();
  } finally { await browser.close(); }
  report.status = report.cases.length === targets.size && report.cases.every(item => item.status === 'PASS') ? 'PASS' : 'FAIL';
  fs.writeFileSync(path.join(out, 'results.json'), JSON.stringify(report, null, 2) + '\n');
  process.exitCode = report.status === 'PASS' ? 0 : 1;
})().catch(error => { console.error(error); process.exitCode = 1; });
