const fs = require('node:fs'),
  path = require('node:path'),
  assert = require('node:assert/strict');
const { requireQa } = require('./runtime.cjs');
const { chromium } = requireQa('playwright');
const out = path.resolve(__dirname, '../../../.artifacts/v2-readiness-20260906/skyy');
(async () => {
  const b = await chromium.launch({ args: ['--use-angle=metal', '--enable-gpu'] });
  const rows = [];
  try {
    for (const mode of ['context-loss', 'permanent-pagehide']) {
      const p = await b.newPage({ viewport: { width: 390, height: 844 } }),
        errors = [];
      p.on('pageerror', e => errors.push(e.message));
      await p.addInitScript(mode => {
        window.__fault = null;
        const original = window.scheduler.yield.bind(window.scheduler);
        window.scheduler.yield = function () {
          if (!window.__fault && window.skyyRoseMascot3D?.getRenderState().phase === 'shader-prepare') {
            window.__fault = { mode, at: performance.now() };
            if (mode === 'context-loss') {
              const gl = document.getElementById('skyy-3d-canvas').getContext('webgl2');
              const extension = gl.getExtension('WEBGL_lose_context');
              if (!extension) throw new Error('Context-loss extension unavailable');
              extension.loseContext();
            } else window.dispatchEvent(new PageTransitionEvent('pagehide', { persisted: false }));
            return new Promise(resolve => setTimeout(resolve, 100));
          }
          return original();
        };
      }, mode);
      await p.goto('http://127.0.0.1:18416/shop/', { waitUntil: 'load' });
      await p.locator('#skyyrose-mascot-recall').click();
      await p.waitForFunction(() => !!window.__fault, null, { timeout: 30000 });
      await p.waitForTimeout(350);
      const state = await p.evaluate(() => ({
        fault: window.__fault,
        render: window.skyyRoseMascot3D.getRenderState(),
        ready: window.skyyRoseMascot3D.isReady(),
        failure: window.skyyRoseMascot3D.getFailureReason(),
        dataset: { ...document.getElementById('skyyrose-mascot').dataset },
      }));
      assert.equal(state.ready, false);
      assert.equal(state.render.running, false);
      assert.equal(errors.length, 0);
      if (mode === 'context-loss') {
        assert.equal(state.failure, 'webgl-context-lost');
        assert.equal(state.dataset.renderer, 'static');
        await p.locator('#skyy-ask-input').fill('shipping');
        await p.locator('#skyy-ask-form button[type=submit]').click();
        assert(
          await p
            .locator('#skyy-conversation')
            .innerText()
            .then(s => /shipping/i.test(s))
        );
      }
      rows.push({
        mode,
        ...state,
        errors,
        method:
          mode === 'context-loss'
            ? 'Actual WEBGL_lose_context during owned shader yield'
            : 'Synthetic non-persisted pagehide during owned shader yield',
      });
      await p.screenshot({ path: path.join(out, mode + '-shader.png') });
      await p.close();
    }
  } finally {
    await b.close();
    fs.writeFileSync(path.join(out, 'shader-lifecycle.json'), JSON.stringify({ rows }, null, 2));
  }
})().catch(e => {
  console.error(e);
  process.exitCode = 1;
});
