const fs = require('node:fs/promises'),
  path = require('node:path'),
  assert = require('node:assert/strict');
const { requireQa: q, base, out, validateSurface } = require('./runtime.cjs');
const { beginRun } = require('./run-evidence.cjs');
const evidence = { tests: [], errors: [] };
const run = beginRun(path.join(out, 'shop-behavior.json'));
(async () => {
  const { default: AxeBuilder } = q('@axe-core/playwright');
  const { chromium } = q('playwright');
  const b = await chromium.launch();
  try {
    for (const js of [true, false]) {
      const c = await b.newContext({ javaScriptEnabled: js, viewport: { width: 390, height: 844 } });
      await c.route('**/*', r => (new URL(r.request().url()).origin === base ? r.continue() : r.abort()));
      const p = await c.newPage();
      p.on('pageerror', e => evidence.errors.push(e.message));
      await p.goto(base + '/shop/');
      await p.locator('summary').filter({ hasText: 'Filters' }).click();
      await p.locator('#sr2-shop-category').selectOption('signature');
      await p.locator('#sr2-shop-max').fill('30');
      await p.getByRole('button', { name: 'Apply filters', exact: true }).click();
      await p.waitForURL('**/*max_price=30*');
      assert.match(await p.locator('main').innerText(), /Signature/);
      const cards = await p.locator('.sr2-c-editorial-card').allTextContents();
      assert(cards.length > 0);
      assert(cards.every(s => s.includes('Signature')));
      await p.reload();
      assert.equal(await p.locator('#sr2-shop-max').inputValue(), '30');
      const sort = p.locator('.woocommerce-ordering select');
      if (js) {
        await Promise.all([p.waitForURL('**/*orderby=price-desc*'), sort.selectOption('price-desc')]);
      } else {
        await sort.selectOption('price-desc');
        await p.getByRole('button', { name: 'Sort', exact: true }).click();
        await p.waitForURL('**/*orderby=price-desc*');
      }
      assert.equal(new URL(p.url()).searchParams.get('max_price'), '30');
      await p.goBack();
      assert.equal(await p.locator('#sr2-shop-max').inputValue(), '30');
      await p.goForward();
      assert.equal(await p.locator('.woocommerce-ordering select').inputValue(), 'price-desc');
      await p.goto(base + '/shop/?min_price=999999&stock_status=instock');
      assert.equal(await p.locator('.sr2-c-editorial-card').count(), 0);
      assert(await p.getByRole('link', { name: 'View all pieces', exact: true }).isVisible());
      await Promise.all([
        p.waitForURL(base + '/shop/'),
        p.getByRole('link', { name: 'View all pieces', exact: true }).click(),
      ]);
      await p.locator('.sr2-c-editorial-card').first().waitFor();
      assert((await p.locator('.sr2-c-editorial-card').count()) > 0);
      await Promise.all([p.waitForURL(/page\/2|paged=2/), p.locator('.woocommerce-pagination a.next').click()]);
      await p.locator('.sr2-c-editorial-card').first().waitFor();
      assert.match(p.url(), /page\/2|paged=2/);
      assert((await p.locator('.sr2-c-editorial-card').count()) > 0);
      await p.goto(base + '/shop/?product_cat[]=signature&min_price[]=1&stock_status[]=instock');
      assert.equal(await p.locator('main h1').count(), 1);
      assert(!/Fatal error|Warning:|Notice:/.test(await p.locator('body').innerText()));
      await p.goto(base + '/product-category/signature/');
      assert.equal(await p.locator('#sr2-shop-category').inputValue(), 'signature');
      evidence.tests.push({
        js,
        filterCount: cards.length,
        refresh: true,
        sort: true,
        history: true,
        empty: true,
        pagination: true,
        malformed: true,
        taxonomy: true,
      });
      if (js) {
        await p.locator('summary').filter({ hasText: 'Filters' }).focus();
        await p.keyboard.press('Enter');
        assert((await p.locator('.sr2-shop-filters').getAttribute('open')) !== null);
        const a = await new AxeBuilder({ page: p })
          .include('main')
          .withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'])
          .analyze();
        evidence.filterAxe = a.violations.map(v => ({ id: v.id, nodes: v.nodes.map(n => n.target) }));
        await p.screenshot({ path: path.join(out, 'shop-filter-390.png') });
      }
      await c.close();
    }
    assert.equal(evidence.errors.length, 0);
    assert.equal(evidence.filterAxe.length, 0, JSON.stringify(evidence.filterAxe));
    evidence.status = 'PASS';
  } catch (e) {
    evidence.status = 'FAIL';
    evidence.error = e.stack;
    throw e;
  } finally {
    await b.close();
  }
  run.pass(evidence);
})().catch(e => {
  run.fail(e, evidence);
  console.error(e);
  process.exitCode = 1;
});
