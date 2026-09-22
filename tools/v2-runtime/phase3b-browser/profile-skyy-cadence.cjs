const fs = require('node:fs'),
  path = require('node:path');
const { requireQa } = require('./runtime.cjs');
const { chromium } = requireQa('playwright');
const out = path.resolve(__dirname, '../../../.artifacts/v2-readiness-20260906/skyy');
(async () => {
  const b = await chromium.launch({ args: ['--use-angle=metal', '--enable-gpu'] });
  const rows = [];
  try {
    for (const mode of ['before', 'current']) {
      const p = await b.newPage({ viewport: { width: 390, height: 844 } });
      await p.goto('http://127.0.0.1:' + (mode === 'before' ? 18423 : 18416) + '/shop/', { waitUntil: 'load' });
      await p.locator('#skyyrose-mascot-recall').click();
      await p.waitForFunction(() => window.skyyRoseMascot3D?.getCurrentAction() === 'Skyy_Walk', null, {
        timeout: 30000,
      });
      await p.waitForFunction(() => window.skyyRoseMascot3D.getCurrentAction() === 'Skyy_Idle');
      await p.evaluate(() => window.skyyRoseMascot3D.resetFrameProfile());
      await p.waitForTimeout(3000);
      const idle = await p.evaluate(() => window.skyyRoseMascot3D.getProfile());
      await p.locator('#skyy-ask-input').fill('shipping');
      await p.locator('#skyy-ask-form button[type=submit]').click();
      await p.evaluate(() => window.skyyRoseMascot3D.resetFrameProfile());
      await p.waitForTimeout(1800);
      const active = await p.evaluate(() => window.skyyRoseMascot3D.getProfile());
      rows.push({ mode, idle, active });
      await p.close();
    }
  } finally {
    await b.close();
    fs.writeFileSync(
      path.join(out, 'cadence-before-after.json'),
      JSON.stringify(
        {
          method:
            'Serial Metal Chromium390x844, actual idle3s and shipping talk1.8s after real walk, fresh baseline/current contexts; CPU submission not GPU execution.',
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
