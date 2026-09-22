const fs = require('node:fs'),
  path = require('node:path'),
  assert = require('node:assert/strict');
const { requireQa } = require('./runtime.cjs');
const { chromium } = requireQa('playwright');
const root = path.resolve(__dirname, '../../..'),
  out = path.join(root, '.artifacts/v2-cinematic-finalization-20260906/skyy');
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--use-angle=metal', '--enable-gpu'] });
  try {
    for (const width of [390, 1440]) {
      const page = await browser.newPage({ viewport: { width, height: 900 }, deviceScaleFactor: 1.5 });
      await page.addInitScript(() => {
        document.addEventListener('skyy:3d-visible', () => {
          if (!window.__firstSkyyFrame) {
            const c = document.getElementById('skyy-3d-canvas');
            window.__firstSkyyFrame = {
              png: c.toDataURL(),
              state: { ...document.getElementById('skyyrose-mascot').dataset },
              at: performance.now(),
            };
            window.__skyyPhases = [];
            new MutationObserver(() => {
              const phase = document.getElementById('skyyrose-mascot').dataset.actionPhase;
              if (phase && window.__skyyPhases.at(-1) !== phase) window.__skyyPhases.push(phase);
            }).observe(document.getElementById('skyyrose-mascot'), {
              attributes: true,
              attributeFilter: ['data-action-phase'],
            });
          }
        });
      });
      await page.goto((process.env.V2_BASE_URL || 'http://127.0.0.1:18416') + '/shop/', { waitUntil: 'load' });
      await page.locator('#skyyrose-mascot-recall').click();
      await page.waitForFunction(() => window.__firstSkyyFrame, null, { timeout: 45000 });
      await page.waitForFunction(
        () => window.__skyyPhases?.includes('turning') && window.__skyyPhases?.includes('idle'),
        null,
        { timeout: 20000 }
      );
      const evidence = await page.evaluate(() => ({ ...window.__firstSkyyFrame, phases: window.__skyyPhases }));
      assert(evidence.phases.includes('walking-in'));
      assert(evidence.phases.includes('turning'));
      assert(evidence.phases.includes('idle'));
      fs.writeFileSync(
        path.join(out, `first-stable-frame-${width}.png`),
        Buffer.from(evidence.png.split(',')[1], 'base64')
      );
      delete evidence.png;
      const sizes = await page.evaluate(() => {
        const image = document.querySelector('#skyyrose-mascot .skyyrose-mascot__image'),
          canvas = document.getElementById('skyy-3d-canvas');
        return {
          image: image.getBoundingClientRect().toJSON(),
          canvas: canvas.getBoundingClientRect().toJSON(),
          profile: window.skyyRoseMascot3D.getProfile(),
        };
      });
      assert(Math.abs(sizes.image.width - sizes.canvas.width) < 0.1);
      assert(Math.abs(sizes.image.height - sizes.canvas.height) < 0.1);
      assert(sizes.profile.firstStableFrameMs > 0);
      // Exercise a real preference change while the rig is moving, then inspect the
      // very next reveal synchronously before the new walk can advance.
      await page.evaluate(() => document.dispatchEvent(new CustomEvent('skyy:walking-in')));
      await page.waitForFunction(
        () =>
          Math.abs(
            parseFloat(document.getElementById('skyyrose-mascot').style.getPropertyValue('--skyy-entry-shift'))
          ) > 3
      );
      await page.emulateMedia({ reducedMotion: 'reduce' });
      await page.waitForFunction(() => document.getElementById('skyyrose-mascot').dataset.presence === 'reduced');
      await page.evaluate(() => {
        document.addEventListener(
          'skyy:3d-visible',
          () => {
            const stage = document.getElementById('skyyrose-mascot');
            window.__resumeSkyy = {
              shift: stage.style.getPropertyValue('--skyy-entry-shift'),
              canvas: document.getElementById('skyy-3d-canvas').getBoundingClientRect().toJSON(),
              poster: stage.querySelector('img').getBoundingClientRect().toJSON(),
            };
          },
          { once: true }
        );
      });
      await page.emulateMedia({ reducedMotion: 'no-preference' });
      await page.waitForFunction(() => window.__resumeSkyy);
      const resumed = await page.evaluate(() => window.__resumeSkyy);
      assert.equal(resumed.shift, '0px');
      assert(Math.abs(resumed.canvas.x - resumed.poster.x) < 0.1);
      fs.writeFileSync(
        path.join(out, `continuity-${width}.json`),
        JSON.stringify({ first: evidence, resumed, ...sizes }, null, 2)
      );
      await page.close();
    }
  } finally {
    await browser.close();
  }
})().catch(e => {
  console.error(e);
  process.exitCode = 1;
});
