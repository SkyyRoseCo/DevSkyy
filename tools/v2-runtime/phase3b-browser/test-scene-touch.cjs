'use strict';
const fs = require('node:fs/promises'),
  path = require('node:path'),
  assert = require('node:assert/strict');
const { requireQa } = require('./runtime.cjs');
(async () => {
  const b = await requireQa('playwright').chromium.launch();
  const rows = [];
  try {
    for (const collection of ['signature', 'black-rose', 'love-hurts']) {
      const ctx = await b.newContext({ viewport: { width: 390, height: 900 }, hasTouch: true });
      const p = await ctx.newPage();
      await p.goto('http://127.0.0.1:18416/collections/' + collection + '/');
      for (const scene of await p.locator('[data-scene-id]').all()) {
        const id = await scene.getAttribute('data-scene-id');
        await scene.evaluate(el => el.scrollIntoView({ block: 'start', inline: 'start', behavior: 'instant' }));
        await p.waitForFunction(id => {
          const v = document.querySelector(`[data-scene-id="${id}"] video`);
          return !v.paused && v.currentTime > 0.3;
        }, id);
        const button = scene.locator('button');
        await button.tap();
        await p.waitForFunction(id => document.querySelector(`[data-scene-id="${id}"] video`).paused, id);
        await button.tap();
        await p.waitForFunction(id => !document.querySelector(`[data-scene-id="${id}"] video`).paused, id);
        await p.evaluate(() => {
          Object.defineProperty(document, 'hidden', { get: () => true, configurable: true });
          document.dispatchEvent(new Event('visibilitychange'));
        });
        assert.equal(await scene.getAttribute('data-scene-motion-state'), 'document-hidden');
        assert(await scene.locator('video').evaluate(v => v.paused));
        await p.evaluate(() => {
          delete document.hidden;
          document.dispatchEvent(new Event('visibilitychange'));
        });
        rows.push({ id, touchPauseResume: 'PASS', documentHiddenHandlerSimulation: 'PASS' });
      }
      await ctx.close();
    }
  } finally {
    await b.close();
    await fs.writeFile(
      path.resolve(
        __dirname,
        '../../../.artifacts/v2-cinematic-finalization-20260906/scenes/touch-document-hidden.json'
      ),
      JSON.stringify(rows, null, 2)
    );
    console.log(rows.length);
  }
})().catch(e => {
  console.error(e);
  process.exitCode = 1;
});
