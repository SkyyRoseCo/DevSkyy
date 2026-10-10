const fs = require('fs'),
  path = require('path'),
  assert = require('assert/strict');
const { requireQa: q, base, out, validateSurface } = require('./runtime.cjs');
const worlds = process.argv.slice(2);
if (!worlds.length) worlds.push('signature');
const { beginRun } = require('./run-evidence.cjs');
const run = beginRun(path.join(out, 'collections-behavior.json'));
(async () => {
  const { chromium } = q('playwright');
  const b = await chromium.launch();
  const receipt = [];
  try {
    for (const slug of worlds) {
      for (const js of [true, false]) {
        const c = await b.newContext({
          javaScriptEnabled: js,
          viewport: { width: 390, height: 844 },
          reducedMotion: 'reduce',
        });
        await c.route('**/*', r => (new URL(r.request().url()).origin === base ? r.continue() : r.abort()));
        const p = await c.newPage();
        const errors = [];
        p.on('pageerror', e => errors.push(e.message));
        await p.goto(base + '/collections/' + slug + '/');
        const main = p.locator('main');
        assert.equal(await main.getAttribute('data-collection'), slug);
        assert.equal(await main.locator('h1').count(), 1);
        assert.equal(await main.locator('video,[data-horizontal-world],[data-scroll-world-pinned]').count(), 0);
        const ids = await main
          .locator('.sr2-c-editorial-card')
          .evaluateAll(a =>
            a.map(e => ({ id: e.dataset.productId, name: e.innerText, loading: e.querySelector('img')?.loading }))
          );
        assert(ids.length > 0);
        assert(ids.every(i => i.loading === 'lazy'));
        await main.locator('a[href="#shop"]').click();
        if (js) {
          await p.waitForFunction(
            () =>
              document.querySelector('#shop').getBoundingClientRect().top >= 0 &&
              document.querySelector('#shop').getBoundingClientRect().top < innerHeight
          );
        }
        assert.match(p.url(), /#shop$/);
        const card = main.locator('.sr2-c-editorial-card').first();
        const product = await card.locator('a').first().getAttribute('href');
        await card.locator('a').first().click();
        await p.waitForURL('**/product/**');
        assert.equal(new URL(p.url()).pathname, new URL(product).pathname);
        await p.goBack();
        await p.reload();
        assert.equal(await p.locator('main').getAttribute('data-collection'), slug);
        await p.locator('.sr2-world-shop-link a').click();
        await p.waitForURL('**/shop/**');
        assert.equal(new URL(p.url()).searchParams.get('product_cat'), slug);
        assert.equal(errors.length, 0);
        receipt.push({
          slug,
          js,
          cards: ids.length,
          anchor: true,
          productLink: true,
          backReload: true,
          nativeCategory: true,
          errors,
        });
        await c.close();
      }
    }
  } finally {
    await b.close();
  }
  run.pass({ cases: receipt });
})().catch(e => {
  run.fail(e);
  console.error(e);
  process.exitCode = 1;
});
