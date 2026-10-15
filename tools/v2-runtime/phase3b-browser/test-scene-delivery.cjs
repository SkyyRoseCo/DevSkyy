'use strict';
const fs = require('node:fs/promises'),
  path = require('node:path'),
  assert = require('node:assert/strict');
const { requireQa } = require('./runtime.cjs');
const out = path.resolve(__dirname, '../../../.artifacts/v2-cinematic-finalization-20260906/scenes');
(async () => {
  const browser = await requireQa('playwright').chromium.launch();
  const results = [];
  try {
    for (const port of [18417, 18416])
      for (const route of ['/', '/collections/signature/', '/collections/black-rose/', '/collections/love-hurts/']) {
        const c = await browser.newContext({ viewport: { width: 390, height: 900 } });
        const p = await c.newPage();
        await p.goto(`http://127.0.0.1:${port}${route}`);
        await p.waitForTimeout(800);
        const r = await p.evaluate(() => ({
          posters: [...document.querySelectorAll('.sr2-hero-commerce__frame>img')].map(img => ({
            src: img.getAttribute('src'),
            deferred: img.dataset.src,
            loaded: img.complete && img.naturalWidth > 0,
          })),
          videos: [...document.querySelectorAll('[data-collection-scene-motion]')].map(v => v.getAttribute('src')),
          resources: performance
            .getEntriesByType('resource')
            .filter(r => /collection-scenes-k1|hero-commerce-c1|derived\/approved-scenes/.test(r.name))
            .map(r => ({
              name: r.name,
              transfer: r.transferSize,
              bytes: r.encodedBodySize,
              start: r.startTime,
              duration: r.duration,
            })),
        }));
        if (port === 18416) {
          assert(r.videos.every(v => !v));
          assert(r.posters.filter(p => p.src).length <= 1);
        }
        results.push({ port, route, ...r });
        await c.close();
      }
    await fs.writeFile(
      path.join(out, 'scene-delivery-before-current.json'),
      JSON.stringify({ status: 'PASS', results }, null, 2)
    );
    console.log(
      results.map(r => ({
        port: r.port,
        route: r.route,
        posters: r.resources.filter(x => !x.name.endsWith('.mp4')).length,
        bytes: r.resources.reduce((n, r) => n + r.bytes, 0),
      }))
    );
  } finally {
    await browser.close();
  }
})().catch(e => {
  console.error(e);
  process.exitCode = 1;
});
