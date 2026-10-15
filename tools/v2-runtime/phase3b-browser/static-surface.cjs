const fs = require('node:fs/promises'),
  path = require('node:path'),
  assert = require('node:assert/strict');
const { requireQa: q, base, out, validateSurface } = require('./runtime.cjs');
const [label, route] = process.argv.slice(2);
validateSurface(label, route);
const { beginRun } = require('./run-evidence.cjs');
const run = beginRun(path.join(out, label + '-static.json'));
(async () => {
  const { chromium } = q('playwright');
  const b = await chromium.launch();
  const rows = [];
  try {
    for (const mode of ['delayed', 'nojs'])
      for (const width of [390, 1440]) {
        const c = await b.newContext({
          javaScriptEnabled: mode !== 'nojs',
          reducedMotion: 'reduce',
          viewport: { width, height: width < 768 ? 844 : 1000 },
        });
        let release;
        const gate = new Promise(r => (release = r));
        await c.route('**/*', async r => {
          if (new URL(r.request().url()).origin !== base) return r.abort();
          if (
            mode === 'delayed' &&
            r.request().resourceType() === 'script' &&
            r.request().url().includes('/themes/skyyrose-flagship-2/assets/js/')
          )
            await gate;
          return r.continue();
        });
        const p = await c.newPage();
        await p.goto(base + route, { waitUntil: 'commit' });
        await p.locator('main h1').waitFor();
        await p.evaluate(() => document.fonts.ready);
        await p.waitForFunction(() =>
          [...document.querySelectorAll('main img')]
            .filter(e => {
              const r = e.getBoundingClientRect();
              return r.width && r.height && r.top < innerHeight && r.bottom > 0;
            })
            .every(e => e.complete && e.naturalWidth)
        );
        const before = await p.evaluate(() => ({
          scrollWidth: document.documentElement.scrollWidth,
          mainHeight: document.querySelector('main').offsetHeight,
          galleryOpacity: document.querySelector('.woocommerce-product-gallery')
            ? getComputedStyle(document.querySelector('.woocommerce-product-gallery')).opacity
            : null,
          images: [...document.querySelectorAll('main img')]
            .filter(e => e.getBoundingClientRect().top < innerHeight)
            .map(e => ({ src: e.currentSrc, width: e.width, height: e.height })),
        }));
        await p.screenshot({ path: path.join(out, `${label}-${mode}-${width}.png`), animations: 'disabled' });
        // The accepted no-JS shell expands its directory above main. Preserve
        // that initial frame, then separately prove the page itself is visible.
        if (mode === 'nojs') {
          await p.locator('main').scrollIntoViewIfNeeded();
          await p.evaluate(() => document.querySelector('main').scrollIntoView({ block: 'start' }));
          await p.waitForFunction(() => [...document.querySelectorAll('main img')]
            .filter(e => { const r = e.getBoundingClientRect(); return r.width && r.height && r.top < innerHeight && r.bottom > 0; })
            .every(e => e.complete && e.naturalWidth));
          await p.screenshot({ path: path.join(out, `${label}-nojs-main-${width}.png`), animations: 'disabled' });
        }
        release();
        await p.waitForLoadState('load');
        const after = await p.locator('main').evaluate(e => e.offsetHeight);
        rows.push({ mode, width, before, afterHeight: after });
        await c.close();
      }
    console.log(label + ' static evidence saved');
  } finally {
    await b.close();
  }
  run.pass(rows);
})().catch(e => {
  run.fail(e);
  console.error(e);
  process.exitCode = 1;
});
