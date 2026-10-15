const fs = require('node:fs'),
  path = require('node:path'),
  assert = require('node:assert/strict');
const { requireQa } = require('./runtime.cjs');
const pw = requireQa('playwright');
const out = path.resolve(__dirname, '../../../.artifacts/v2-cinematic-finalization-20260906/skyy');
(async () => {
  const rows = [];
  for (const name of ['firefox', 'webkit']) {
    const browser = await pw[name].launch();
    try {
      const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
      const errors = [];
      page.on('pageerror', e => errors.push(e.message));
      await page.goto((process.env.V2_BASE_URL || 'http://127.0.0.1:18416') + '/shop/', { waitUntil: 'load' });
      await page.locator('#skyyrose-mascot-recall').click();
      await page.waitForFunction(() => document.getElementById('skyy-ask-dialog').open);
      await page.waitForFunction(
        () =>
          window.skyyRoseMascot3D?.isReady() ||
          document.getElementById('skyyrose-mascot').dataset.presence === 'failed',
        null,
        { timeout: 30000 }
      );
      if (await page.locator('#skyy-motion-toggle').isVisible()) await page.locator('#skyy-motion-toggle').click();
      await page.locator('#skyy-ask-input').fill('SG-005');
      await page.locator('#skyy-ask-form button[type=submit]').click();
      assert((await page.locator('#skyy-conversation a').count()) > 0);
      for (let i = 0; i < 10; i++) {
        await page.keyboard.press('Tab');
        assert(await page.evaluate(() => document.getElementById('skyy-ask-dialog').contains(document.activeElement)));
      }
      await page.screenshot({ path: path.join(out, `engine-${name}.png`) });
      const state = await page.evaluate(() => ({
        ready: window.skyyRoseMascot3D?.isReady(),
        failure: window.skyyRoseMascot3D?.getFailureReason(),
        profile: window.skyyRoseMascot3D?.getProfile?.(),
        presence: document.getElementById('skyyrose-mascot').dataset.presence,
      }));
      await page.keyboard.press('Escape');
      await page.waitForFunction(() => !document.getElementById('skyy-ask-dialog').open);
      assert.equal(errors.length, 0);
      rows.push({ engine: name, ...state, errors, keyboardSteps: 10, escape: 'PASS' });
    } finally {
      await browser.close();
      fs.writeFileSync(path.join(out, 'cross-engine.json'), JSON.stringify(rows, null, 2));
    }
  }
})().catch(e => {
  console.error(e);
  process.exitCode = 1;
});
