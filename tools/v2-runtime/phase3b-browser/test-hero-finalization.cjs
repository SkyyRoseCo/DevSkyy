/** Matched approved hero frames, plus current mobile art-direction evidence. */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { requireQa, base, out, validateLabel } = require('./runtime.cjs');
const label = process.argv[2] || 'current';
validateLabel(label);
const widths = (process.env.V2_HERO_WIDTHS || '320,390,414,768,1440').split(',').map(Number);
assert(widths.every(n => Number.isInteger(n) && n >= 320 && n <= 1728));
const routes = {
  home: '/',
  signature: '/collections/signature/',
  'black-rose': '/collections/black-rose/',
  'love-hurts': '/collections/love-hurts/',
  kids: '/collections/kids-capsule/',
};
(async () => {
  const engine = process.env.V2_BROWSER || 'chromium';
  assert(['chromium', 'firefox', 'webkit'].includes(engine));
  const browser = await requireQa('playwright')[engine].launch();
  const rows = [];
  try {
    for (const width of widths)
      for (const [name, route] of Object.entries(routes)) {
        const context = await browser.newContext({
          viewport: { width, height: 900 },
          reducedMotion: 'no-preference',
          hasTouch: width < 768,
        });
        await context.route('**/*', r => (new URL(r.request().url()).origin === base ? r.continue() : r.abort()));
        const page = await context.newPage();
        const errors = [],
          mediaErrors = [];
        page.on('pageerror', e => errors.push(e.message));
        page.on('response', r => {
          if (/\.(webm|mp4)(\?|$)/.test(r.url()) && r.status() >= 400)
            mediaErrors.push({ url: r.url(), status: r.status() });
        });
        await page.goto(base + route);
        await page.evaluate(() => document.fonts.ready);
        const hero = page.locator('[data-recovery-hero]').first();
        const film = hero.locator('video');
        await film.waitFor({ state: 'attached' });
        await page.waitForFunction(() => {
          const v = document.querySelector('[data-recovery-hero] video');
          return v.readyState >= 2 && v.currentTime > 0.1 && Number(getComputedStyle(v).opacity) > 0.99;
        });
        const captureFrame = await film.evaluate(
          v =>
            new Promise((resolve, reject) => {
              // The local no-Range fixture cannot reliably seek. Observe an actual
              // presented frame near one second, then freeze without changing time.
              let callback;
              const deadline = setTimeout(() => {
                v.cancelVideoFrameCallback(callback);
                reject(new Error('No matching presented frame within20seconds'));
              }, 20000);
              let previous = v.currentTime;
              let waitForLoop = previous > 1.05;
              const sample = (now, metadata) => {
                if (metadata.mediaTime < previous) waitForLoop = false;
                previous = metadata.mediaTime;
                if (!waitForLoop && metadata.mediaTime >= 1 && metadata.mediaTime <= 1.06) {
                  v.pause();
                  clearTimeout(deadline);
                  requestAnimationFrame(() =>
                    requestAnimationFrame(() =>
                      resolve({
                        method: 'actual playback then pause; no seek',
                        mediaTime: metadata.mediaTime,
                        presentedFrames: metadata.presentedFrames,
                        pausedTime: v.currentTime,
                      })
                    )
                  );
                } else {
                  if (metadata.mediaTime > 1.06) waitForLoop = true;
                  callback = v.requestVideoFrameCallback(sample);
                }
              };
              callback = v.requestVideoFrameCallback(sample);
            })
        );
        const state = await hero.evaluate(el => ({
          readyClass: el.classList.contains('is-hero-video-ready'),
          text: el.innerText,
          bounds: el.getBoundingClientRect().toJSON(),
          video: [...el.querySelectorAll('video')].map(v => ({
            source: v.currentSrc,
            time: v.currentTime,
            readyState: v.readyState,
            width: v.videoWidth,
            height: v.videoHeight,
            fit: getComputedStyle(v).objectFit,
            position: getComputedStyle(v).objectPosition,
            opacity: getComputedStyle(v).opacity,
          })),
          controls: [...el.querySelectorAll('a,button')].map(e => ({
            text: e.textContent.trim(),
            bounds: e.getBoundingClientRect().toJSON(),
          })),
          overflow: document.documentElement.scrollWidth > innerWidth,
        }));
        fs.writeFileSync(
          path.join(out, 'last-hero-state.json'),
          JSON.stringify({ name, width, captureFrame, state }, null, 2)
        );
        assert(state.readyClass);
        assert(
          state.video.every(
            v => v.readyState >= 2 && Number(v.opacity) > 0.99 && Math.abs(v.time - captureFrame.mediaTime) < 0.15
          )
        );
        assert(!state.overflow);
        assert.equal(errors.length, 0);
        assert.equal(mediaErrors.length, 0);
        const screenshot = `${label}-hero-${name}-${width}.png`;
        await page.screenshot({ path: path.join(out, screenshot) });
        rows.push({ name, width, captureFrame, state, errors, mediaErrors, screenshot });
        fs.writeFileSync(
          path.join(out, `${label}-heroes.json`),
          JSON.stringify({ status: 'IN_PROGRESS', rows }, null, 2)
        );
        await context.close();
      }
    fs.writeFileSync(
      path.join(out, `${label}-heroes.json`),
      JSON.stringify(
        {
          status: 'PASS',
          scope:
            'Actual presented frames at 1.00–1.06s, then direct video pause; no seeking. Visual verdict requires eyes-on review; not loop-seam or real-device certification.',
          rows,
        },
        null,
        2
      )
    );
    console.log(`${rows.length} hero captures passed`);
  } finally {
    await browser.close();
  }
})().catch(e => {
  console.error(e);
  process.exitCode = 1;
});
