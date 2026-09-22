/** Separate diagnostic A-E. Instrumentation never changes shipped source. */
const fs = require('node:fs'),
  path = require('node:path');
const { requireQa } = require('./runtime.cjs');
const { chromium } = requireQa('playwright');
const root = path.resolve(__dirname, '../../..'),
  out = path.join(root, '.artifacts/v2-cinematic-finalization-20260906/skyy');
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--use-angle=metal', '--enable-gpu'] });
  const rows = [];
  try {
    for (const mode of ['A-disabled-diagnostic', 'B-static', 'C-loading', 'D-idle', 'E-conversation']) {
      const context = await browser.newContext({ viewport: { width: 390, height: 844 } }),
        page = await context.newPage();
      let release;
      await page.addInitScript(() => {
        window.__skyyPerf = { lcp: [], longTasks: [] };
        new PerformanceObserver(l =>
          l.getEntries().forEach(e =>
            window.__skyyPerf.lcp.push({
              at: e.startTime,
              element: e.element?.tagName,
              id: e.element?.id,
              size: e.size,
            })
          )
        ).observe({ type: 'largest-contentful-paint', buffered: true });
        new PerformanceObserver(l =>
          l.getEntries().forEach(e => window.__skyyPerf.longTasks.push({ at: e.startTime, duration: e.duration }))
        ).observe({ type: 'longtask', buffered: true });
      });
      if (mode.startsWith('A'))
        await page.route('**/mascot-loader.min.js*', r =>
          r.fulfill({ contentType: 'application/javascript', body: '/* diagnostic only: character disabled */' })
        );
      if (mode.startsWith('B'))
        await page.route('**/skyy-3d.min.js*', r =>
          r.fulfill({
            contentType: 'application/javascript',
            body: "document.getElementById('skyyrose-mascot').dataset.presence='static';",
          })
        );
      if (mode.startsWith('C'))
        await page.route('**/skyy-mascot.glb*', async r => {
          await new Promise(resolve => (release = resolve));
          await r.abort('failed').catch(() => {});
        });
      await page.goto((process.env.V2_BASE_URL || 'http://127.0.0.1:18416') + '/', { waitUntil: 'load' });
      // The LCP sample precedes interaction/scroll, so character-intent doesn't truncate the observer before its baseline window.
      await page.waitForTimeout(3500);
      const initial = await page.evaluate(() => ({
        ...window.__skyyPerf,
        modelRequests: performance.getEntriesByType('resource').filter(e => e.name.includes('skyy-mascot.glb')).length,
      }));
      if (!mode.startsWith('A')) await page.locator('#skyy-hero-stage').scrollIntoViewIfNeeded();
      if (['C-loading', 'D-idle', 'E-conversation'].includes(mode))
        await page.locator('#skyyrose-mascot-trigger').hover();
      if (['D-idle', 'E-conversation'].includes(mode)) {
        await page.waitForFunction(() => window.skyyRoseMascot3D?.isReady(), null, { timeout: 45000 });
        await page.waitForFunction(
          () =>
            window.skyyRoseMascot3D.getCurrentAction() === 'Skyy_Idle' &&
            document.getElementById('skyyrose-mascot').dataset.actionPhase === 'idle',
          null,
          { timeout: 20000 }
        );
        if (mode.startsWith('E')) {
          await page.locator('#skyy-hero-chat').click();
          await page.locator('#skyy-ask-input').fill('shipping');
          await page.locator('#skyy-ask-form button[type=submit]').click();
        }
        await page.evaluate(() => window.skyyRoseMascot3D.resetFrameProfile());
      }
      await page.waitForTimeout(mode.startsWith('E') ? 1800 : 3500);
      const sample = await page.evaluate(() => ({
        initialLcp: window.__skyyPerf.lcp,
        profile: window.skyyRoseMascot3D?.getProfile(),
        state: { ...document.getElementById('skyyrose-mascot').dataset },
        resources: performance
          .getEntriesByType('resource')
          .filter(e => /mascot|skyy-3d|skyy-runtime-poster|three-r170|draco/.test(e.name))
          .map(e => ({ url: e.name, transfer: e.transferSize, encoded: e.encodedBodySize, duration: e.duration })),
        longTasks: window.__skyyPerf.longTasks,
      }));
      await page.screenshot({ path: path.join(out, mode + '.png') });
      rows.push({ mode, initial, ...sample });
      fs.writeFileSync(
        path.join(out, 'runtime-profile.json'),
        JSON.stringify(
          {
            method:
              'Serial fresh Chromium contexts,390x844,unthrottled local fixture,ANGLE Metal on desktop host; not a physical mobile device. LCP observed3.5s before scroll and explicit character hover; not Lighthouse. Render-callCPU timings are not GPU execution times. A/B/C are diagnostic request overrides, never shipping toggles.',
            rows,
          },
          null,
          2
        )
      );
      if (release) release();
      await context.close();
      console.log(mode);
    }
  } finally {
    await browser.close();
  }
})().catch(e => {
  console.error(e);
  process.exitCode = 1;
});
