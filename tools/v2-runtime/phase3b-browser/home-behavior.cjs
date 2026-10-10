/** Local Living Archive navigation and canonical-card integration; no cart writes. */
const assert = require('node:assert/strict');
const path = require('node:path');
const { requireQa, base, out } = require('./runtime.cjs');
const { beginRun } = require('./run-evidence.cjs');
const run = beginRun(path.join(out, 'home-behavior.json'));
const rows = [];
const routes = ['/', '/shop/', '/product/sg-005/', '/collections/signature/',
  '/collections/black-rose/', '/collections/love-hurts/', '/collections/kids-capsule/'];

(async () => {
  const { chromium } = requireQa('playwright');
  const { default: AxeBuilder } = requireQa('@axe-core/playwright');
  const browser = await chromium.launch();
  try {
    for (const javaScriptEnabled of [true, false]) {
      const context = await browser.newContext({ javaScriptEnabled, reducedMotion: 'reduce',
        viewport: { width: 390, height: 844 } });
      await context.route('**/*', r => new URL(r.request().url()).origin === base ? r.continue() : r.abort());
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', e => errors.push(e.message));
      const response = await page.goto(base + '/');
      assert.equal(response.status(), 200);
      assert.equal(await page.locator('main h1').count(), 1);
      const acts = await page.locator('main.sr2-archive [data-archive-act]').evaluateAll(es => es.map(e => e.id));
      assert.deepEqual(acts, ['arrival', 'worlds', 'oakland', 'artifact', 'heir', 'town-line', 'legacy', 'continue'].map(a => 'sr2-archive-' + a));
      assert.equal(await page.locator('main video, main [data-horizontal-rail], main [data-home-model-loop]').count(), 0);
      const cards = page.locator('main .sr2-c-editorial-card');
      assert.equal(await cards.count(), 3, 'Fixture must resolve SG-005 and both Kids pieces');
      const skus = await cards.locator('.sr2-c-editorial-card__reference').allTextContents();
      assert.deepEqual(skus.map(s => s.replace('SKU:', '').trim()), ['SG-005', 'KIDS-001', 'KIDS-002']);
      assert(await cards.evaluateAll(es => es.every(e => e.dataset.mediaSource === 'approved-card-front')));
      assert(await cards.locator('img').evaluateAll(es => es.every(e => e.loading === 'lazy' && e.fetchPriority !== 'high')));
      const high = await page.locator('main img[fetchpriority="high"]').count();
      assert.equal(high, 1);
      const scripts = await page.locator('script[src]').evaluateAll(es => es.map(e => e.src));
      assert(!scripts.some(s => /house-of-roses-motion|kids-capsule-reveal|collection-scene-motion/.test(s)));
      const styles = await page.locator('link[rel="stylesheet"]').evaluateAll(es => es.map(e => e.href));
      assert(!styles.some(s => /legacy-home-page|legacy-world-components/.test(s)));
      const worlds = await page.locator('#sr2-archive-worlds a').evaluateAll(es => es.map(e => e.href));
      for (const slug of ['signature', 'black-rose', 'love-hurts', 'kids-capsule']) {
        assert(worlds.includes(base + '/collections/' + slug + '/'));
      }
      const continuation = await page.locator('#sr2-archive-continue a').evaluateAll(es => es.map(e => ({ text: e.textContent.trim(), url: e.href })));
      assert.equal(continuation.length, 5);
      for (const link of continuation) {
        assert.equal(new URL(link.url).origin, base);
        const result = await page.goto(link.url);
        assert.equal(result.status(), 200, link.text);
        assert.equal(new URL(page.url()).origin, base);
        assert.equal(await page.locator('main').count(), 1);
      }
      await page.goto(base + '/');
      const qv = page.locator('main [data-quick-view]').first();
      const target = await qv.getAttribute('href');
      if (!javaScriptEnabled) {
        await qv.click();
        assert.equal(page.url(), target, 'No-JS Quick View must navigate to its native PDP');
        assert.equal(await page.locator('form.variations_form').count(), 1);
      }
      assert.deepEqual(errors, []);
      rows.push({ mode: javaScriptEnabled ? 'js' : 'nojs', acts, skus, continuation, errors });
      await context.close();
    }

    for (const width of [390, 1440]) {
      const context = await browser.newContext({ viewport: { width, height: width === 390 ? 844 : 1000 }, reducedMotion: 'reduce' });
      await context.route('**/*', r => new URL(r.request().url()).origin === base ? r.continue() : r.abort());
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', e => errors.push(e.message));
      for (const route of routes) {
        assert.equal((await page.goto(base + route)).status(), 200);
        const trigger = page.locator('main [data-quick-view]').first();
        assert.equal(await trigger.count(), 1);
        const facts = await trigger.evaluate(e => ({ ...e.dataset }));
        await trigger.focus();
        await page.keyboard.press('Enter');
        const dialog = page.locator('#sr2-quick-view-dialog');
        await dialog.waitFor({ state: 'visible' });
        assert.equal(await page.locator('dialog[open]').count(), 1);
        for (const field of ['name', 'collection', 'price', 'availability']) {
          const key = 'quickView' + field[0].toUpperCase() + field.slice(1);
          assert.equal(await dialog.locator('[data-quick-view-' + field + ']').textContent(), facts[key]);
        }
        assert.equal(await dialog.locator('[data-quick-view-url]').getAttribute('href'), facts.quickViewUrl);
        await page.waitForFunction(() => {
          const image = document.querySelector('#sr2-quick-view-dialog [data-quick-view-image]');
          return image.complete && image.naturalWidth > 0;
        });
        assert.equal(await dialog.locator('[data-quick-view-image]').getAttribute('src'), facts.quickViewImage);
        await page.keyboard.press('Tab');
        assert(await dialog.evaluate(e => e.contains(document.activeElement)));
        const axe = await new AxeBuilder({ page }).include('#sr2-quick-view-dialog').withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze();
        assert.deepEqual(axe.violations.map(v => v.id), []);
        if (route === '/') await page.screenshot({ path: path.join(out, 'home-quick-view-' + width + '.png'), animations: 'disabled' });
        await page.keyboard.press('Escape');
        assert(await trigger.evaluate(e => e === document.activeElement));
        assert.equal(await page.locator('dialog[open]').count(), 0);
        assert.deepEqual(errors, []);
        rows.push({ route, width, quickView: 'PASS', keyboard: 'Enter/Tab/Escape/return focus', axe: 0 });
      }
      await context.close();
    }
    run.pass({ rows, scope: 'Local navigation and previews only; no cart, payment or order submission' });
    console.log('PASS Home eight acts, native continuation, no-JS fallback and canonical Quick View on seven surfaces');
  } finally {
    await browser.close();
  }
})().catch(error => { run.fail(error); console.error(error); process.exitCode = 1; });
