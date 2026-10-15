'use strict';
const assert = require('node:assert/strict'),
  fs = require('node:fs/promises'),
  path = require('node:path');
const { requireQa } = require('./runtime.cjs');
(async () => {
  const browser = await requireQa('playwright').chromium.launch();
  const rows = [];
  try {
    for (const mode of ['normal', 'network-failure', 'initialization-failure'])
      for (const route of ['/', '/collections/signature/', '/collections/black-rose/', '/collections/love-hurts/']) {
        const context = await browser.newContext({ viewport: { width: 390, height: 900 }, reducedMotion: 'reduce' });
        if (mode !== 'normal')
          await context.route('**/collection-scene-motion*.js*', r =>
            mode === 'network-failure'
              ? r.abort('failed')
              : r.fulfill({
                  contentType: 'application/javascript',
                  body: 'throw new Error("Injected scene initialization failure");',
                })
          );
        const page = await context.newPage();
        const response = await page.goto('http://127.0.0.1:18416' + route);
        const nonce = await page.locator('#skyyrose2-collection-scene-motion-js-before').evaluate(el => el.nonce);
        const csp = response.headers()['content-security-policy'] || '';
        assert(
          nonce ? csp.includes("'nonce-" + nonce + "'") : /script-src[^;]*'unsafe-inline'/.test(csp),
          'Watchdog must be permitted by the existing CSP'
        );
        if (mode === 'normal') {
          await page.waitForFunction(() => window.skyyroseSceneMotionReady === true);
          assert.equal(await page.locator('html').getAttribute('data-scene-controller-fallback'), null);
          assert(
            (await page.locator('[data-scene-poster][src]').count()) <= 1,
            'Normal scene preparation remains scoped'
          );
        } else {
          await page.waitForFunction(() => document.documentElement.dataset.sceneControllerFallback === 'still');
          await page.locator('[data-scene-poster]').evaluateAll(imgs => Promise.all(imgs.map(img => img.decode())));
          assert(
            await page
              .locator('[data-scene-poster]')
              .evaluateAll(
                imgs =>
                  imgs.length === 3 &&
                  imgs.every(
                    img => img.src === img.dataset.src && img.naturalWidth > 0 && getComputedStyle(img).opacity === '1'
                  )
              )
          );
          assert(
            await page
              .locator('[data-collection-scene-motion]')
              .evaluateAll(vs => vs.every(v => !v.getAttribute('src'))),
            'Fallback must never start video'
          );
        }
        rows.push({ mode, route, noncePresent: Boolean(nonce), cspAllowsInline: true, passed: true });
        await context.close();
      }
    await fs.writeFile(
      path.resolve(__dirname, '../../../.artifacts/v2-cinematic-finalization-20260906/scenes/controller-failure.json'),
      JSON.stringify({ status: 'PASS', rows }, null, 2)
    );
    console.log('PASS ' + rows.length);
  } finally {
    await browser.close();
  }
})().catch(e => {
  console.error(e);
  process.exitCode = 1;
});
