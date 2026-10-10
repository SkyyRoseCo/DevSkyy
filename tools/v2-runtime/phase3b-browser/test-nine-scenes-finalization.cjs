'use strict';
const fs = require('node:fs/promises');
const path = require('node:path');
const assert = require('node:assert/strict');
const { requireQa } = require('./runtime.cjs');
const root = path.resolve(__dirname, '../../..');
const out = path.join(root, '.artifacts/v2-cinematic-finalization-20260906/scenes');
const manifest = require(path.join(root, 'wordpress-theme/skyyrose-flagship-2/data/approved-scroll-world-scenes.json'));
const base = process.env.V2_SCENE_BASE || 'http://127.0.0.1:18416';
const phase = process.env.V2_SCENE_PHASE || 'current';
const groups = ['signature', 'black-rose', 'love-hurts'];
const wait = ms => new Promise(resolve => setTimeout(resolve, ms));
async function position(page, id) {
  await page.locator(`[data-scene-id="${id}"]`).evaluate(el => {
    const rail = el.closest('[data-recovery-track]');
    rail.scrollBy({ left: el.getBoundingClientRect().left - rail.getBoundingClientRect().left, behavior: 'instant' });
    window.scrollBy({ top: el.getBoundingClientRect().top - 108, behavior: 'instant' });
  });
  await page.waitForFunction(id => {
    const el = document.querySelector(`[data-scene-id="${id}"] img[src]`);
    return el && el.complete && el.naturalWidth > 0;
  }, id);
  await page
    .locator(`[data-scene-id="${id}"] img[src]`)
    .first()
    .evaluate(img => img.decode());
}
async function evidence(page, id) {
  return page.locator(`[data-scene-id="${id}"]`).evaluate(el => {
    const frame = el.querySelector('figure');
    const img = frame.querySelector('img[src]');
    const v = frame.querySelector('video');
    const box = frame.getBoundingClientRect();
    return {
      id: el.dataset.sceneId,
      state: el.dataset.sceneMotionState,
      image: img.currentSrc,
      imageLoaded: img.complete && img.naturalWidth > 0,
      posterOpacity: getComputedStyle(img).opacity,
      videoOpacity: getComputedStyle(v).opacity,
      videoSource: v.currentSrc,
      paused: v.paused,
      time: v.currentTime,
      readyState: v.readyState,
      videoFit: getComputedStyle(v).objectFit,
      frame: { width: box.width, height: box.height },
      heading: el.querySelector('h3').textContent,
      links: [...el.querySelectorAll('nav a')].map(a => ({ text: a.textContent.trim(), href: a.href })),
      toggle: el.querySelector('button').textContent,
      toggleHeight: el.querySelector('button').getBoundingClientRect().height,
      overflow: document.documentElement.scrollWidth > innerWidth,
    };
  });
}
(async () => {
  await fs.mkdir(out, { recursive: true });
  const browser = await requireQa('playwright').chromium.launch();
  const report = { phase, base, started: new Date().toISOString(), scenes: {}, errors: [] };
  try {
    // Matched visual references use identical poster state, dimensions and framing.
    for (const collection of groups)
      for (const width of [390, 1440]) {
        const context = await browser.newContext({ viewport: { width, height: 900 }, reducedMotion: 'reduce' });
        const page = await context.newPage();
        await page.goto(`${base}/collections/${collection}/`);
        for (const scene of Object.values(manifest.scenes).filter(s => s.collection === collection)) {
          const id = scene.scene_id.toLowerCase();
          await position(page, id);
          const data = await evidence(page, id);
          assert(data.imageLoaded && !data.overflow && data.links.length);
          await page.screenshot({ path: path.join(out, `${phase}-${id}-${width}-poster.png`) });
          (report.scenes[id] ||= { label: scene.label, collection, cases: [] }).cases.push({
            type: 'matched-poster',
            width,
            ...data,
            passed: true,
          });
        }
        await context.close();
      }
    if (phase === 'baseline') {
      report.status = 'PASS';
      return;
    }
    // Individual normal-motion recordings include scene arrival, progression, CTA and native shop handoff.
    for (const scene of Object.values(manifest.scenes))
      for (const width of [390, 1440]) {
        const id = scene.scene_id.toLowerCase();
        const context = await browser.newContext({
          viewport: { width, height: 900 },
          reducedMotion: 'no-preference',
          recordVideo: { dir: path.join(out, 'raw-recordings'), size: { width, height: 900 } },
        });
        const page = await context.newPage();
        page.on('pageerror', err => report.errors.push({ id, width, message: err.message }));
        const requests = [];
        page.on('request', request => {
          if (request.url().includes('/collection-scenes-k1/') && request.url().endsWith('.mp4'))
            requests.push(request.url());
        });
        await page.goto(`${base}/collections/${scene.collection}/`);
        const before = requests.slice();
        await position(page, id);
        await page.waitForFunction(id => {
          const v = document.querySelector(`[data-scene-id="${id}"] video`);
          return !v.paused && v.currentTime > 0.2;
        }, id);
        await wait(800);
        const initial = await evidence(page, id);
        assert.equal(initial.videoFit, 'contain');
        assert(!initial.overflow);
        assert(initial.toggleHeight >= 44);
        assert(
          initial.videoSource.endsWith(
            scene.required_runtime_assets.find(a => a.role === (width < 768 ? 'mobile' : 'desktop')).path
          )
        );
        await page.screenshot({ path: path.join(out, `current-${id}-${width}-motion.png`) });
        const toggle = page.locator(`[data-scene-id="${id}"] button`);
        await toggle.focus();
        await page.keyboard.press('Enter');
        assert.equal(await page.locator(`[data-scene-id="${id}"] video`).evaluate(v => v.paused), true);
        assert.equal((await evidence(page, id)).posterOpacity, '1');
        await position(page, id);
        await toggle.evaluate(el => el.click());
        await page.waitForFunction(id => !document.querySelector(`[data-scene-id="${id}"] video`).paused, id);
        const link = page.locator(`[data-scene-id="${id}"] nav a`).first();
        await link.focus();
        await wait(400);
        assert.match(await link.getAttribute('href'), /\/product\//);
        await page
          .locator('a[href$="#shop"]')
          .first()
          .evaluate(el => el.click());
        await page.waitForURL('**/#shop');
        await page.waitForFunction(() => document.querySelector('#shop').dataset.handoffState === 'active');
        await wait(500);
        report.scenes[id].cases.push({
          type: 'normal',
          width,
          initial,
          requestsBeforeArrival: before,
          sceneRequests: requests,
          keyboardPause: true,
          nativeHandoff: true,
          passed: true,
        });
        const video = page.video();
        await context.close();
        await video.saveAs(path.join(out, `${id}-${width}-arrival-progression-cta-handoff.webm`));
      }
    // Fallbacks and lifecycle are exercised independently for every scene.
    for (const mode of ['save-data', 'no-js', 'media-error', 'loading', 'lifecycle'])
      for (const collection of groups) {
        const context = await browser.newContext({
          viewport: { width: 390, height: 900 },
          javaScriptEnabled: mode !== 'no-js',
          reducedMotion: 'no-preference',
          hasTouch: true,
        });
        if (mode === 'save-data')
          await context.addInitScript(() =>
            Object.defineProperty(navigator, 'connection', { value: { saveData: true, addEventListener() {} } })
          );
        if (mode === 'media-error')
          await context.route('**/collection-scenes-k1/*.mp4', route => route.abort('failed'));
        let release;
        const held = new Promise(resolve => {
          release = resolve;
        });
        if (mode === 'loading')
          await context.route('**/collection-scenes-k1/*.mp4', async route => {
            await held;
            await route.abort().catch(() => {});
          });
        const page = await context.newPage();
        await page.goto(`${base}/collections/${collection}/`);
        const scenes = Object.values(manifest.scenes).filter(s => s.collection === collection);
        for (const scene of scenes) {
          const id = scene.scene_id.toLowerCase();
          await position(page, id);
          if (mode === 'media-error')
            await page.waitForFunction(id => document.querySelector(`[data-scene-id="${id}"] button`).disabled, id);
          if (mode === 'loading')
            await page.waitForFunction(
              id => document.querySelector(`[data-scene-id="${id}"]`).dataset.sceneMotionState === 'loading',
              id
            );
          if (mode === 'lifecycle') {
            await page.waitForFunction(id => !document.querySelector(`[data-scene-id="${id}"] video`).paused, id);
            await page.evaluate(() => window.dispatchEvent(new PageTransitionEvent('pagehide', { persisted: true })));
            assert.equal((await evidence(page, id)).state, 'suspended');
            assert.equal(
              await page.locator('video[data-collection-scene-motion]').evaluateAll(vs => vs.every(v => v.paused)),
              true
            );
            await page.evaluate(() => window.dispatchEvent(new PageTransitionEvent('pageshow', { persisted: true })));
            await position(page, id);
            await page.waitForFunction(id => !document.querySelector(`[data-scene-id="${id}"] video`).paused, id);
            await page.setViewportSize({ width: 900, height: 390 });
            await position(page, id);
            assert(!(await evidence(page, id)).overflow);
            await page.setViewportSize({ width: 390, height: 900 });
            await position(page, id);
          }
          const data = await evidence(page, id);
          assert(data.imageLoaded && !data.overflow);
          if (mode !== 'lifecycle') assert.equal(data.posterOpacity, '1');
          if (['save-data', 'no-js'].includes(mode)) assert.equal(data.videoSource, '');
          report.scenes[id].cases.push({ type: mode, ...data, passed: true });
          await page.screenshot({ path: path.join(out, `${id}-${mode}.png`) });
        }
        if (mode === 'lifecycle') {
          // Reverse and rapid changes retain decoded stills and at most one playing scene.
          for (const scene of [...scenes].reverse().concat(scenes)) {
            await position(page, scene.scene_id.toLowerCase());
            assert.equal(
              await page
                .locator('video[data-collection-scene-motion]')
                .evaluateAll(vs => vs.filter(v => !v.paused).length <= 1),
              true
            );
          }
          for (const scene of scenes)
            report.scenes[scene.scene_id.toLowerCase()].cases.push({ type: 'reverse-fast-scroll', passed: true });
        }
        release();
        await context.close();
      }
    assert.deepEqual(report.errors, []);
    report.status = 'PASS';
  } catch (error) {
    report.status = 'FAIL';
    report.failure = error.stack;
    process.exitCode = 1;
  } finally {
    await browser.close();
    report.finished = new Date().toISOString();
    await fs.writeFile(path.join(out, `${phase}-scene-matrix.json`), JSON.stringify(report, null, 2));
    console.log(
      JSON.stringify({ status: report.status, scenes: Object.keys(report.scenes).length, failure: report.failure })
    );
  }
})();
