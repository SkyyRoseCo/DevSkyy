const fs = require('fs'),
  path = require('path'),
  assert = require('assert/strict');
const { requireQa: q, base, out, validateSurface } = require('./runtime.cjs');
const { beginRun } = require('./run-evidence.cjs');
const run = beginRun(path.join(out, 'final-page-inventory.json'));
(async () => {
  const { chromium } = q('playwright');
  const b = await chromium.launch();
  const rows = [];
  try {
    for (const width of [390, 1440])
      for (const [name, route] of [
        ['home', '/'],
        ['shop', '/shop/'],
        ['pdp', '/product/sg-005/'],
        ['signature', '/collections/signature/'],
        ['black-rose', '/collections/black-rose/'],
        ['love-hurts', '/collections/love-hurts/'],
        ['kids', '/collections/kids-capsule/'],
      ]) {
        const c = await b.newContext({
          viewport: { width, height: width === 390 ? 844 : 1000 },
          reducedMotion: 'reduce',
        });
        await c.route('**/*', r => (new URL(r.request().url()).origin === base ? r.continue() : r.abort()));
        const p = await c.newPage();
        const errors = [],
          failures = [];
        p.on('pageerror', e => errors.push(e.message));
        p.on('response', r => {
          if (r.status() >= 400) failures.push({ url: r.url(), status: r.status() });
        });
        const res = await p.goto(base + route);
        assert.equal(res.status(), 200);
        await p.evaluate(() => document.fonts.ready);
        await p.waitForFunction(() =>
          [...document.images]
            .filter(i => {
              const r = i.getBoundingClientRect();
              return r.width && r.height && r.top < innerHeight && r.bottom > 0;
            })
            .every(i => i.complete && i.naturalWidth)
        );
        await p.waitForTimeout(1200);
        const metrics = await p.evaluate(() => {
          const imgs = [...document.querySelectorAll('main img')].map(i => {
            const r = i.getBoundingClientRect(),
              s = i.currentSrc || i.src,
              e = performance.getEntriesByName(s).at(-1);
            return {
              src: s,
              srcset: i.srcset,
              sizes: i.sizes,
              loading: i.loading,
              priority: i.fetchPriority,
              width: i.width,
              height: i.height,
              naturalWidth: i.naturalWidth,
              naturalHeight: i.naturalHeight,
              aboveFold: r.width > 0 && r.height > 0 && r.top < innerHeight && r.bottom > 0,
              bytes: e?.decodedBodySize || 0,
            };
          });
          const resources = performance.getEntriesByType('resource').map(e => ({
            url: e.name,
            bytes: e.decodedBodySize,
            transfer: e.transferSize,
            type: e.initiatorType,
            duration: e.duration,
          }));
          const kinds = { images: 0, css: 0, js: 0, fonts: 0, other: 0 };
          for (const r of resources) {
            const path = new URL(r.url).pathname;
            const k = /\.(webp|png|jpe?g|svg|avif)$/.test(path)
              ? 'images'
              : /\.css$/.test(path)
                ? 'css'
                : /\.js$/.test(path)
                  ? 'js'
                  : /\.(woff2?|ttf|otf)$/.test(path)
                    ? 'fonts'
                    : 'other';
            kinds[k] += r.bytes;
          }
          return {
            h1: document.querySelector('main h1')?.textContent,
            overflow: document.documentElement.scrollWidth - innerWidth,
            images: imgs,
            eager: imgs.filter(i => i.loading !== 'lazy').length,
            lazy: imgs.filter(i => i.loading === 'lazy').length,
            largestRequestedImage: imgs.reduce((a, i) => (i.bytes > (a?.bytes || 0) ? i : a), null),
            resources,
            bytes: kinds,
            styles: [...document.querySelectorAll('link[rel=stylesheet]')].map(l => l.href),
            scripts: [...document.scripts].filter(s => s.src).map(s => s.src),
          };
        });
        rows.push({
          name,
          route,
          width,
          cache: 'fresh browser context per page',
          measurement: 'initial load plus1200ms, no scroll, reduced motion',
          errors,
          failures,
          ...metrics,
        });
        await c.close();
      }
    console.log(
      rows.map(r => ({
        name: r.name,
        width: r.width,
        bytes: r.bytes,
        errors: r.errors.length,
        failures: r.failures.length,
        overflow: r.overflow,
      }))
    );
  } finally {
    await b.close();
  }
  run.pass({ rows });
})().catch(e => {
  run.fail(e);
  console.error(e);
  process.exitCode = 1;
});
