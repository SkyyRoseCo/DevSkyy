/** Local before/after samples, not field Core Web Vitals or a launch certificate. */
import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import assert from 'node:assert/strict';
const label = process.argv[2];
assert(['baseline', 'candidate'].includes(label), 'Specify baseline or candidate');
const require = createRequire(path.resolve('.artifacts/v2-phase3-20260905/qa/package.json'));
const { chromium } = require('playwright');
const base = 'http://127.0.0.1:18303';
const browser = await chromium.launch({ headless: true });
const samples = [];
try {
 for (const width of [390, 1440]) for (const route of ['/', '/product/sg-005/']) for (let sample = 0; sample < 3; sample++) {
  const context = await browser.newContext({ viewport: { width, height: width === 390 ? 844 : 1000 } });
  await context.route('**/*', r => new URL(r.request().url()).origin === base ? r.continue() : r.abort());
  await context.addInitScript(() => {
   window.__shellPerf = { longTasks: [], lcp: [] };
   for (const [type, key] of [['longtask', 'longTasks'], ['largest-contentful-paint', 'lcp']]) {
    if (PerformanceObserver.supportedEntryTypes.includes(type)) new PerformanceObserver(list => window.__shellPerf[key].push(...list.getEntries().map(e => ({ start: e.startTime, duration: e.duration })))).observe({ type, buffered: true });
   }
  });
  const page = await context.newPage();
  const response = await page.goto(base + route, { waitUntil: 'load' });
  assert.equal(response.status(), 200);
  await page.waitForTimeout(3000); // Fixed observation window, identical for both sources.
  samples.push({ width, route, sample, ...await page.evaluate(() => ({
   ...window.__shellPerf,
   navigation: performance.getEntriesByType('navigation').map(e => ({ responseStart: e.responseStart, domContentLoaded: e.domContentLoadedEventEnd, load: e.loadEventEnd })),
   resources: performance.getEntriesByType('resource').filter(e => /\.(css|js|woff2)(\?|$)/.test(e.name)).map(e => ({ name: new URL(e.name).pathname, bytes: e.decodedBodySize })),
   visibleImages: [...document.images].filter(e => { const r = e.getBoundingClientRect(); return r.width && r.height && r.top < innerHeight && r.bottom > 0; }).map(e => ({ src: new URL(e.currentSrc || e.src).pathname, loaded: e.complete && e.naturalWidth > 0 }))
  })) });
  await context.close();
 }
 await fs.writeFile(path.resolve('.artifacts/v2-phase3-20260905/performance-' + label + '.json'), JSON.stringify({ label, limitations: 'Isolated localhost, synthetic fixture, unthrottled headless Chromium, three cold contexts per route/width, three-second post-load window. Not field performance.', samples }, null, 2));
} finally { await browser.close(); }
console.log(JSON.stringify({ label, samples: samples.length }));
