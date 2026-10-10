// Explicit local browser pilot, intentionally outside the unit-test wildcard.
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const { requireQa, base, out } = require('./runtime.cjs');

(async () => {
  const browser = await requireQa('playwright').chromium.launch();
  const report = { scope: 'Signature, Black Rose, Love Hurts', tests: [], errors: [] };
  try {
    const cases = ['signature', 'black-rose', 'love-hurts']
      .flatMap(collection =>
        [390, 1440].flatMap(width => ['motion', 'reduced'].map(mode => ({ collection, width, mode })))
      )
      .concat(['save-data', 'no-js'].map(mode => ({ collection: 'signature', width: 1024, mode })));
    for (const { collection, width, mode } of cases) {
      const context = await browser.newContext({
        viewport: { width, height: 900 },
        reducedMotion: mode === 'reduced' ? 'reduce' : 'no-preference',
        javaScriptEnabled: mode !== 'no-js',
      });
      await context.route('**/*', route =>
        new URL(route.request().url()).origin === base ? route.continue() : route.abort()
      );
      await context.addInitScript(() => {
        window.handoffAnimationCount = 0;
        const animate = Element.prototype.animate;
        Element.prototype.animate = function (...args) {
          if (this.closest('[data-scene-handoff]')) window.handoffAnimationCount++;
          return animate.apply(this, args);
        };
      });
      if (mode === 'save-data')
        await context.addInitScript(() => {
          Object.defineProperty(navigator, 'connection', { value: { saveData: true, addEventListener() {} } });
        });
      const page = await context.newPage();
      page.on('pageerror', error => report.errors.push(error.message));
      await page.goto(base + '/collections/' + collection + '/#shop');
      const shop = page.locator('#shop');
      await shop.waitFor();
      assert.equal(await shop.getAttribute('data-scene-handoff'), collection);
      assert(await shop.locator('h2').isVisible());
      assert((await shop.locator('.sr2-c-editorial-card').count()) > 0);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
      if (mode !== 'no-js') {
        const expected = mode === 'motion' ? 'active' : 'static';
        await page.waitForFunction(state => document.querySelector('#shop').dataset.handoffState === state, expected);
        assert.equal(await page.evaluate(() => window.handoffAnimationCount), mode === 'motion' ? 2 : 0);
        const image = page.locator('#shop img').first();
        await image.waitFor();
        const style = await shop
          .locator('header')
          .evaluate(el => ({ opacity: getComputedStyle(el).opacity, transform: getComputedStyle(el).transform }));
        assert.equal(style.opacity, '1');
        assert.equal(style.transform, 'none');
        if (mode === 'motion') {
          // Re-executing the served module must neither initialize twice nor replay arrival.
          const script = await page.locator('script[src*="scene-handoff"]').getAttribute('src');
          assert(script, 'Core collection route must enqueue the module');
          await page.addScriptTag({ url: script });
          assert.equal(await shop.getAttribute('data-handoff-state'), 'active');
          assert.equal(await shop.evaluate(el => el.getAnimations({ subtree: true }).length), 0);
          // Browser-native same-document history remains owned by the browser.
          await page.evaluate(() => {
            location.hash = '';
          });
          // Removing a fragment need not change the viewport in every document.
          await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
          await page.waitForFunction(() => document.querySelector('#shop').dataset.handoffState === 'exit');
          await page.locator('a[href$="#shop"]').first().click();
          await page.waitForURL('**/#shop');
          await page.waitForFunction(() => document.querySelector('#shop').dataset.handoffState === 'active');
          await page.goBack();
          assert.equal(new URL(page.url()).hash, '');
          await page.goForward();
          assert.equal(new URL(page.url()).hash, '#shop');
          // Explicit lifecycle event simulation; this does not claim browser BFcache eligibility.
          await page.evaluate(() => window.dispatchEvent(new PageTransitionEvent('pagehide', { persisted: true })));
          assert.equal(await shop.getAttribute('data-handoff-state'), 'suspended');
          assert.equal(await shop.evaluate(el => el.getAnimations({ subtree: true }).length), 0);
          await page.evaluate(() => window.dispatchEvent(new PageTransitionEvent('pageshow', { persisted: true })));
          await page.waitForFunction(() => document.querySelector('#shop').dataset.handoffState === 'active');
          await page.screenshot({ path: path.join(out, collection + '-shop-' + width + '-' + mode + '.png') });
          await page.emulateMedia({ reducedMotion: 'reduce' });
          await page.waitForFunction(() => document.querySelector('#shop').dataset.handoffState === 'static');
        }
      } else {
        assert.equal(await shop.getAttribute('data-handoff-initialized'), null);
      }
      if (mode !== 'motion')
        await page.screenshot({ path: path.join(out, collection + '-shop-' + width + '-' + mode + '.png') });
      report.tests.push({ collection, width, mode, nativeContentVisible: true, overflow: false, passed: true });
      await context.close();
    }
    const page = await browser.newPage();
    await page.goto(base + '/collections/kids-capsule/');
    assert.equal(await page.locator('[data-scene-handoff]').count(), 0);
    assert.equal(await page.locator('script[src*="scene-handoff"]').count(), 0);
    report.tests.push({ mode: 'other-collection-scope', passed: true });
    assert.deepEqual(report.errors, []);
    report.status = 'PASS';
  } catch (error) {
    report.status = 'FAIL';
    report.failure = error.stack;
    process.exitCode = 1;
  } finally {
    await browser.close();
    await fs.writeFile(path.join(out, 'scene-handoff-browser.json'), JSON.stringify(report, null, 2) + '\n');
    console.log(JSON.stringify(report, null, 2));
  }
})();
