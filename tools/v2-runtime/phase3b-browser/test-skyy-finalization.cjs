/** Actual local browser state/visual evidence; software WebGL is labeled explicitly. */
const fs = require('node:fs'),
  path = require('node:path'),
  assert = require('node:assert/strict');
const { requireQa } = require('./runtime.cjs');
const { chromium } = requireQa('playwright');
const root = path.resolve(__dirname, '../../..'),
  out = path.join(root, '.artifacts/v2-cinematic-finalization-20260906/skyy');
const rows = [];
const base = process.env.V2_BASE_URL || 'http://127.0.0.1:18416';
const flags = ['--use-angle=metal', '--enable-gpu'];
async function state(page) {
  return page.evaluate(() => ({
    dataset: { ...document.getElementById('skyyrose-mascot').dataset },
    profile: window.skyyRoseMascot3D?.getProfile?.(),
    render: window.skyyRoseMascot3D?.getRenderState(),
    action: window.skyyRoseMascot3D?.getCurrentAction(),
    motion: window.skyyRoseMascot3D?.getMotionEvidence(),
    failure: window.skyyRoseMascot3D?.getFailureReason(),
    dialog: document.getElementById('skyy-ask-dialog').open,
  }));
}
async function shot(page, name) {
  await page.screenshot({ path: path.join(out, name + '.png') });
}
(async () => {
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ headless: true, args: flags });
  try {
    for (const source of process.env.SKYY_SKIP_JOURNEYS
      ? []
      : process.env.SKYY_SOURCE
        ? [process.env.SKYY_SOURCE]
        : ['before', 'current'])
      for (const width of process.env.SKYY_WIDTH ? [+process.env.SKYY_WIDTH] : [390, 1440]) {
        const prefix = `${source}-${width}`,
          context = await browser.newContext({
            viewport: { width, height: 900 },
            hasTouch: width < 768,
            recordVideo: { dir: out, size: { width, height: 900 } },
          });
        const page = await context.newPage(),
          errors = [];
        page.on('pageerror', e => errors.push(e.message));
        await page.addInitScript(() => {
          window.__skyyEvents = [];
          for (const name of [
            '3d-loading',
            '3d-ready',
            '3d-visible',
            'walking-in',
            'idle',
            'wave',
            'joy',
            'speaking',
            'hidden',
            'thinking',
            'listening',
          ])
            document.addEventListener('skyy:' + name, () => window.__skyyEvents.push({ name, at: performance.now() }));
        });
        await page.goto(
          (source === 'before' ? process.env.SKYY_BASELINE_URL || 'http://127.0.0.1:18417' : base) + '/',
          { waitUntil: 'load' }
        );
        await page.locator('#skyy-hero-stage').scrollIntoViewIfNeeded();
        await shot(page, prefix + '-static');
        if (source === 'current') {
          if (width < 768) await page.locator('#skyyrose-mascot-trigger').tap();
          else await page.locator('#skyyrose-mascot-trigger').hover();
        }
        await page.waitForFunction(() => window.skyyRoseMascot3D?.isReady(), null, { timeout: 45000 });
        await shot(page, prefix + '-walk');
        await page.waitForFunction(
          current =>
            window.skyyRoseMascot3D?.getCurrentAction() === 'Skyy_Idle' &&
            (!current || document.getElementById('skyyrose-mascot').dataset.actionPhase === 'idle'),
          source === 'current',
          { timeout: 30000 }
        );
        await shot(page, prefix + '-idle');
        rows.push({ source, width, state: 'idle', ...(await state(page)), errors });
        if (source === 'current') {
          await page.evaluate(() => window.scrollTo({ top: document.body.scrollHeight, behavior: 'instant' }));
          await page.waitForFunction(
            () =>
              document.getElementById('skyyrose-mascot').dataset.visibility === 'offscreen' &&
              !window.skyyRoseMascot3D.getRenderState().running
          );
          const off = await state(page);
          await page.waitForTimeout(150);
          assert.equal(off.render.frames, (await state(page)).render.frames);
          rows.push({ source, width, state: 'offscreen', ...off });
          await page.locator('#skyy-hero-stage').scrollIntoViewIfNeeded();
          await page.waitForTimeout(150);
          await page.evaluate(() => {
            Object.defineProperty(document, 'hidden', { configurable: true, value: true });
            document.dispatchEvent(new Event('visibilitychange'));
          });
          const hidden = await state(page);
          await page.waitForTimeout(150);
          assert.equal(hidden.render.frames, (await state(page)).render.frames);
          rows.push({
            source,
            width,
            state: 'document-hidden',
            method: 'Synthetic visibility event against real initialized renderer',
            ...hidden,
          });
          await page.evaluate(() => {
            delete document.hidden;
            document.dispatchEvent(new Event('visibilitychange'));
          });
        }
        await page.locator('#skyy-hero-chat').click();
        await page.waitForTimeout(500);
        await shot(page, prefix + '-chat');
        await page.locator('#skyy-ask-input').fill('hello Skyy');
        if (source === 'current') rows.push({ source, width, state: 'listening', ...(await state(page)) });
        await page.locator('#skyy-ask-form button[type=submit]').click();
        await page.waitForTimeout(300);
        await shot(page, prefix + '-greeting');
        await page.locator('#skyy-ask-input').fill('shipping');
        await page.locator('#skyy-ask-form button[type=submit]').click();
        await page.waitForTimeout(300);
        await shot(page, prefix + '-talking');
        if (source === 'current') {
          await page.locator('#skyy-ask-input').fill('SG-005');
          await page.locator('#skyy-ask-form button[type=submit]').click();
          await shot(page, prefix + '-gesture');
          for (let key = 0; key < 14; key++) {
            await page.keyboard.press('Tab');
            assert(
              await page.evaluate(() => document.getElementById('skyy-ask-dialog').contains(document.activeElement))
            );
          }
        }
        await page.locator('#skyy-motion-toggle').click();
        const paused = await state(page);
        await page.waitForTimeout(180);
        const later = await state(page);
        assert.equal(paused.render.frames, later.render.frames);
        await shot(page, prefix + '-paused');
        if (source === 'current') {
          rows.push({ source, width, state: 'paused', ...later });
          await page.locator('#skyy-ask-minimize').click();
          await page.waitForFunction(
            () => document.getElementById('skyyrose-mascot').dataset.chat === 'minimized',
            null,
            { timeout: 5000 }
          );
          assert.equal((await state(page)).dataset.chat, 'minimized');
          await shot(page, prefix + '-minimized');
          await page.locator('#skyyrose-mascot-recall').click();
          await page.waitForTimeout(100);
        }
        await page.locator('#skyy-ask-cancel').click();
        await page.waitForTimeout(550);
        await page.locator('#skyy-hero-dismiss').click();
        assert(await page.locator('#skyyrose-mascot').isHidden());
        await shot(page, prefix + '-dismissed');
        rows.push({ source, width, state: 'journey', events: await page.evaluate(() => window.__skyyEvents), errors });
        const video = page.video();
        await context.close();
        await video.saveAs(path.join(out, prefix + '-review.webm'));
        await video.delete();
      }
    for (const mode of process.env.SKYY_SKIP_FALLBACK
      ? []
      : ['reduced', 'save-data', 'webgl-failure', 'model-failure', 'chat-failure']) {
      const context = await browser.newContext({
          viewport: { width: 390, height: 844 },
          reducedMotion: mode === 'reduced' ? 'reduce' : 'no-preference',
        }),
        page = await context.newPage();
      if (mode === 'save-data')
        await page.addInitScript(() =>
          Object.defineProperty(navigator, 'connection', { value: { saveData: true, addEventListener() {} } })
        );
      if (mode === 'webgl-failure')
        await page.addInitScript(() => {
          const original = HTMLCanvasElement.prototype.getContext;
          HTMLCanvasElement.prototype.getContext = function (type, ...args) {
            return type === 'webgl2' ? null : original.call(this, type, ...args);
          };
        });
      if (mode === 'model-failure') await page.route('**/skyy-mascot.glb*', r => r.abort('failed'));
      let modelRequests = 0;
      page.on('request', r => {
        if (r.url().includes('skyy-mascot.glb')) modelRequests++;
      });
      await page.goto(base + '/shop/', { waitUntil: 'load' });
      if (mode === 'chat-failure')
        await page.evaluate(() => {
          window.SKYY_GUIDE_DATA = {};
        });
      await page.locator('#skyyrose-mascot-recall').click();
      await page.waitForFunction(() => document.getElementById('skyy-ask-dialog').open, null, { timeout: 30000 });
      if (['webgl-failure', 'model-failure'].includes(mode))
        await page.waitForFunction(() => !!window.skyyRoseMascot3D?.getFailureReason(), null, { timeout: 30000 });
      if (mode === 'chat-failure') {
        await page.locator('#skyy-ask-input').fill('SG-005');
        await page.locator('#skyy-ask-form button[type=submit]').click();
        assert.equal((await state(page)).dataset.conversation, 'chat-failure');
      }
      await page.waitForTimeout(500);
      await shot(page, mode);
      rows.push({ mode, modelRequests, ...(await state(page)) });
      if (['reduced', 'save-data', 'webgl-failure'].includes(mode)) assert.equal(modelRequests, 0);
      assert(await page.locator('#skyy-ask-input').isVisible());
      await context.close();
    }
  } finally {
    await browser.close();
    fs.writeFileSync(
      path.join(out, `state-matrix-${process.env.SKYY_SOURCE || 'all'}-${process.env.SKYY_WIDTH || 'all'}.json`),
      JSON.stringify(
        { renderer: 'Chromium ANGLE Metal on this desktop host; no physical mobile device claim', rows },
        null,
        2
      )
    );
  }
  console.log(JSON.stringify({ rows: rows.length, status: 'PASS' }));
})().catch(e => {
  console.error(e);
  process.exitCode = 1;
});
