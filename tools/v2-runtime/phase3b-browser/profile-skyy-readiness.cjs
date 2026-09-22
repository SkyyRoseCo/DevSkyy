const fs = require('node:fs'),
  path = require('node:path'),
  assert = require('node:assert/strict');
const { requireQa } = require('./runtime.cjs');
const { chromium } = requireQa('playwright');
const out = path.resolve(__dirname, '../../../.artifacts/v2-readiness-20260906/skyy');
(async () => {
  const browser = await chromium.launch({ args: ['--use-angle=metal', '--enable-gpu'] });
  const rows = [];
  try {
    for (const mode of (process.env.SKYY_PROFILE_MODES || 'before,current').split(','))
      for (let sample = 0; sample < Number(process.env.SKYY_PROFILE_SAMPLES || 2); sample++) {
        const c = await browser.newContext({ viewport: { width: 390, height: 844 } }),
          p = await c.newPage();
        await p.addInitScript(() => {
          window.__long = [];
          window.__cpuStages = [];
          document.addEventListener(
            'three-ready',
            () => {
              for (const name of ['computeBoundingBox', 'computeBoundingSphere']) {
                const proto = window.THREE.SkinnedMesh.prototype,
                  original = proto[name];
                proto[name] = function (...args) {
                  const at = performance.now();
                  try {
                    return original.apply(this, args);
                  } finally {
                    window.__cpuStages.push({ name, at, duration: performance.now() - at });
                  }
                };
              }
              const gl = document.getElementById('skyy-3d-canvas').getContext('webgl2');
              if (gl)
                for (const name of [
                  'bufferData',
                  'texImage2D',
                  'texSubImage2D',
                  'compileShader',
                  'linkProgram',
                  'drawElements',
                ]) {
                  const original = gl[name];
                  gl[name] = function (...args) {
                    const at = performance.now();
                    try {
                      return original.apply(this, args);
                    } finally {
                      const duration = performance.now() - at;
                      if (duration > 0.1) window.__cpuStages.push({ name, at, duration });
                    }
                  };
                }
            },
            { once: true }
          );
          new PerformanceObserver(l =>
            l.getEntries().forEach(e => window.__long.push({ at: e.startTime, duration: e.duration }))
          ).observe({ type: 'longtask', buffered: true });
          document.addEventListener('skyy:3d-visible', () => {
            window.__first = document.getElementById('skyy-3d-canvas').toDataURL();
          });
        });
        await p.goto('http://127.0.0.1:' + (mode === 'before' ? 18423 : 18416) + '/shop/', { waitUntil: 'load' });
        await p.waitForTimeout(500);
        await p.locator('#skyyrose-mascot-recall').click();
        await p.waitForFunction(() => window.skyyRoseMascot3D?.isReady(), null, { timeout: 45000 });
        await p.waitForTimeout(100);
        const first = await p.evaluate(() => window.__first);
        assert(first);
        fs.writeFileSync(path.join(out, `${mode}-${sample}-first.png`), Buffer.from(first.split(',')[1], 'base64'));
        await p.waitForFunction(() => window.skyyRoseMascot3D.getCurrentAction() === 'Skyy_Walk', null, {
          timeout: 15000,
        });
        await p.waitForFunction(() => window.skyyRoseMascot3D.getCurrentAction() === 'Skyy_Idle', null, {
          timeout: 15000,
        });
        await p.locator('#skyy-ask-input').fill('shipping');
        await p.locator('#skyy-ask-form button[type=submit]').click();
        await p.waitForTimeout(500);
        const row = await p.evaluate(() => ({
          profile: window.skyyRoseMascot3D.getProfile(),
          cpuStages: window.__cpuStages,
          longTasks: window.__long,
          state: { ...document.getElementById('skyyrose-mascot').dataset },
          resources: performance
            .getEntriesByType('resource')
            .filter(e => /skyy-mascot.glb|three.module|draco|GLTFLoader/.test(e.name))
            .map(e => ({ url: e.name, bytes: e.encodedBodySize, duration: e.duration })),
        }));
        assert.equal(row.resources.filter(r => r.url.includes('skyy-mascot.glb')).length, 1);
        assert.equal(row.state.conversation, 'talking');
        rows.push({ mode, sample, ...row });
        await p.screenshot({ path: path.join(out, `${mode}-${sample}-chat.png`) });
        await c.close();
        console.log(mode, sample);
        fs.writeFileSync(
          path.join(out, process.env.SKYY_PROFILE_FILE || 'runtime-before-after.json'),
          JSON.stringify(
            {
              method:
                'Serial fresh Metal Chromium, 390x844 desktop host, frozen baseline18423/current18416, actual Ask invitation. First visible canvas captured synchronously; CPU submission is not GPU execution.',
              rows,
            },
            null,
            2
          )
        );
      }
  } finally {
    await browser.close();
  }
})().catch(e => {
  console.error(e);
  process.exitCode = 1;
});
