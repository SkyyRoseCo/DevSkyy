const fs = require('node:fs'),
  path = require('node:path'),
  assert = require('node:assert/strict');
const { requireQa } = require('./runtime.cjs');
const { chromium } = requireQa('playwright');
const out = path.resolve(__dirname, '../../../.artifacts/v2-cinematic-finalization-20260906/skyy');
(async () => {
  const b = await chromium.launch({ args: ['--use-angle=metal', '--enable-gpu'] });
  const rows = [];
  try {
    for (const mode of ['hover', 'tap', 'focus']) {
      const context = await b.newContext({
          viewport: { width: mode === 'hover' ? 1440 : 390, height: 844 },
          hasTouch: mode === 'tap',
        }),
        p = await context.newPage();
      let requests = [];
      p.on('request', r => {
        if (/skyy-mascot\.glb|skyy-3d\.min\.js|three-r170|draco/.test(r.url())) requests.push(r.url());
      });
      await p.goto((process.env.V2_BASE_URL || 'http://127.0.0.1:18416') + '/', { waitUntil: 'load' });
      await p.waitForFunction(() => window.skyyRoseConcierge);
      await p.waitForTimeout(mode === 'hover' ? 10000 : 1000);
      assert.equal(requests.length, 0, 'No optional3D resources before character intent');
      const before = await p.evaluate(() => ({ ...document.getElementById('skyyrose-mascot').dataset }));
      assert.equal(before.renderer, 'static');
      if (mode === 'hover') await p.locator('#skyyrose-mascot-trigger').hover();
      if (mode === 'tap') await p.locator('#skyyrose-mascot-trigger').tap();
      if (mode === 'focus') await p.locator('#skyy-hero-chat').focus();
      await p.waitForFunction(() => window.skyyRoseMascot3D?.isReady(), null, { timeout: 30000 });
      assert.equal(requests.filter(url => url.includes('skyy-mascot.glb')).length, 1);
      rows.push({
        mode,
        before,
        observationMs: mode === 'hover' ? 10000 : 1000,
        optionalRequestsBefore: 0,
        requestsAfter: requests,
        profile: await p.evaluate(() => window.skyyRoseMascot3D.getProfile()),
      });
      await context.close();
    }
  } finally {
    await b.close();
    fs.writeFileSync(
      path.join(out, 'intent-gate.json'),
      JSON.stringify(
        {
          method:
            'Actual Metal browser pointer hover, touchscreen tap and keyboard focus; no shipping diagnostic disable flag.',
          rows,
        },
        null,
        2
      )
    );
  }
})().catch(e => {
  console.error(e);
  process.exitCode = 1;
});
