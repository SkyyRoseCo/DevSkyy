'use strict';

// Native local response fault injection. No production request or asset grant.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '../../..');
const base = 'http://127.0.0.1:18362';
const run = process.env.SR_RELEASE_RUN || '';
assert.match(run, /^(?:[a-z0-9-]+)?$/);
const out = path.join(root, 'tasks/release-gates-20261019', run, 'evidence/browser-faults');
const fixture = JSON.parse(fs.readFileSync(path.join(root, 'tasks/release-gates-20261019/evidence/native-browser-fixture.json')));
const worldPath = fixture.routes.find(r => r.kind === 'world' && r.collection === 'signature').path;
fs.mkdirSync(out, { recursive: true });
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const report = { classification: 'REPRODUCED_LOCAL_NATIVE_WITH_SYNTHETIC_FAULTS', authentication: 'NOT_APPLICABLE', driver_sha256: sha(fs.readFileSync(__filename)), fixture_sha256: sha(fs.readFileSync(path.join(root, 'tasks/release-gates-20261019/evidence/native-browser-fixture.json'))), runtime: { wp: fixture.wp, woo: fixture.woocommerce }, source_pins: Object.fromEntries(['functions.php', 'assets/js/three-core-loader.js', 'assets/js/three-core-loader.min.js', 'assets/js/lib/three-r170/three.module.min.js', 'assets/css/immersive.css', 'assets/css/immersive.min.css', 'assets/js/immersive.js', 'assets/js/immersive.min.js', 'template-parts/immersive/world.php'].map(p => [p, sha(fs.readFileSync(path.join(root, 'wordpress-theme/skyyrose-flagship-2', p)))])), cases: [], creative_acceptance: 'NOT_GRANTED' };
const controls = ['poster-error-before-script', 'poster-error-after-script', 'chapter-error-before-script', 'chapter-error-after-script', 'chapter-error-while-poster-loading', 'chapter-absent', 'delayed-poster-success', 'storage-denied', 'save-data', 'webgl-unavailable', 'renderer-error', 'javascript-disabled'];
async function until(page, predicate) {
  await page.waitForFunction(predicate, undefined, { timeout: 15000 });
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  report.browser = await browser.version();
  try {
    for (const control of controls) {
      const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, reducedMotion: ['webgl-unavailable', 'renderer-error', 'save-data'].includes(control) ? 'no-preference' : 'reduce', javaScriptEnabled: control !== 'javascript-disabled' });
      const item = { control, status: 'FAIL', errors: [], blocked_external_origins: [] };
      const page = await context.newPage();
      const scriptBodies = [];
      page.on('response', response => { if (new URL(response.url()).pathname.endsWith('/assets/js/immersive.min.js')) scriptBodies.push(response.body().then(sha)); });
      page.on('pageerror', error => item.errors.push(error.message));
      let releaseImage;
      let releaseScript;
      const imageGate = new Promise(resolve => { releaseImage = resolve; });
      const scriptGate = new Promise(resolve => { releaseScript = resolve; });
      if (control === 'storage-denied') await context.addInitScript(() => {
        for (const name of ['localStorage', 'sessionStorage']) Object.defineProperty(window, name, { get() { throw new DOMException('Synthetic storage denial', 'SecurityError'); } });
      });
      if (control === 'save-data') await context.addInitScript(() => Object.defineProperty(navigator, 'connection', { value: { saveData: true } }));
      if (['webgl-unavailable', 'renderer-error'].includes(control)) await context.addInitScript(({ rendererError }) => {
        const native = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function(type, ...args) { return type.startsWith('webgl') ? (rendererError ? {} : null) : native.call(this, type, ...args); };
        if (rendererError) window.THREE = { Scene: class { constructor() { throw new Error('Synthetic renderer initialization failure'); } } };
      }, { rendererError: control === 'renderer-error' });
      await context.route('**/*', async route => {
        const url = new URL(route.request().url());
        if (url.origin !== base) { item.blocked_external_origins.push(url.origin); return route.abort('blockedbyclient'); }
        if (url.pathname === '/synthetic-failed-poster.webp') {
          if (control === 'poster-error-after-script') await imageGate;
          return route.fulfill({ status: 404, contentType: 'text/plain', body: 'Synthetic missing image' });
        }
        if (url.pathname === '/synthetic-failed-chapter.webp') { if (control === 'chapter-error-after-script') await imageGate; return route.fulfill({ status: 404, contentType: 'text/plain', body: 'Synthetic missing chapter' }); }
        if (route.request().resourceType() === 'document' && url.pathname === worldPath && (control.startsWith('poster-error') || control.startsWith('chapter-'))) {
          const response = await route.fetch();
          let html = await response.text();
          if (control.startsWith('poster-error')) html = html.replace(/(<div class="sr2-immersive__poster[^>]*>)([\s\S]*?)(<\/div>)/, (_, start, middle, end) => start + middle.replace(/src="[^"]*"/, 'src="/synthetic-failed-poster.webp"').replace(/srcset="[^"]*"/, '') + end);
          if (control.startsWith('chapter-error')) html = html.replace(/(<div class="sr2-immersive__chapter-media[^>]*>)([\s\S]*?)(<\/div>)/, (_, start, middle, end) => start + middle.replace(/src="[^"]*"/, 'src="/synthetic-failed-chapter.webp"').replace(/srcset="[^"]*"/, '').replace(/loading="lazy"/, 'loading="eager"') + `<a class="sr2-immersive__hotspot" data-scene-product="true" data-sku="sg-005" style="--hotspot-x:45%;--hotspot-y:55%" href="${fixture.products['sg-005'].url}"><span class="sr2-immersive__hotspot-copy"><small>Piece in this scene</small></span></a>` + end);
          if (control === 'chapter-absent') html = html.replace(/(<div class="sr2-immersive__chapter-media[^>]*>)([\s\S]*?)(<\/div>)/, (_, start, middle, end) => start + middle.replace(/<img\b[^>]*>/, '<p class="sr2-immersive__image-unavailable">Scene imagery is unavailable.</p>') + end);
          return route.fulfill({ response, body: html });
        }
        if (url.pathname.endsWith('/assets/js/immersive.min.js') && ['poster-error-before-script', 'chapter-error-before-script'].includes(control)) await scriptGate;
        if (route.request().resourceType() === 'image' && ['chapter-error-while-poster-loading', 'delayed-poster-success'].includes(control) && url.pathname.includes('sg-') && !url.pathname.includes('synthetic')) await imageGate;
        return route.continue();
      });
      await context.tracing.start({ screenshots: true, snapshots: true, sources: false });
      try {
        await page.goto(base + worldPath, { waitUntil: 'commit' });
        await page.locator('main.sr2-immersive').waitFor({ state: 'attached' });
        if (control === 'poster-error-before-script') {
          await until(page, () => { const image = document.querySelector('.sr2-immersive__poster img'); return image && image.complete && image.naturalWidth === 0; });
          item.failure_completed_before_script = true;
          releaseScript();
        }
        if (control === 'poster-error-after-script') {
          await until(page, () => document.querySelector('.sr2-immersive').dataset.sceneState === 'reduced-motion');
          releaseImage();
        }
        if (control === 'chapter-error-before-script') {
          await until(page, () => { const image = document.querySelector('.sr2-immersive__chapter-media > img'); return image && image.complete && image.naturalWidth === 0; });
          item.failure_completed_before_script = true; releaseScript();
        }
        if (control === 'chapter-error-after-script') {
          await until(page, () => document.querySelector('.sr2-immersive').dataset.sceneState === 'reduced-motion');
          releaseImage();
        }
        if (control === 'chapter-error-while-poster-loading') {
          await until(page, () => Boolean(document.querySelector('.sr2-immersive__image-unavailable')));
          item.chapter_failed_before_poster_ready = await page.locator('main').getAttribute('data-poster-state') !== 'ready';
          assert.equal(item.chapter_failed_before_poster_ready, true);
          releaseImage();
        }
        if (control === 'delayed-poster-success') {
          await until(page, () => document.querySelector('.sr2-immersive').dataset.sceneState === 'reduced-motion');
          assert.match(await page.locator('.sr2-immersive__scene-status').textContent(), /Loading/);
          item.no_false_ready_before_image = true;
          releaseImage();
        }
        await page.waitForLoadState('load');
        if (control.startsWith('poster-error')) {
          await until(page, () => document.querySelector('.sr2-immersive').dataset.posterState === 'unavailable');
          assert.equal(await page.locator('.sr2-immersive__poster img').evaluate(image => image.hidden), true);
          assert.equal(await page.locator('.sr2-immersive__scene-status').evaluate(el => el.classList.contains('screen-reader-text')), false);
          assert.match(await page.locator('.sr2-immersive__scene-status').textContent(), /unavailable/);
        } else if (control !== 'javascript-disabled') {
          await until(page, () => document.querySelector('.sr2-immersive').dataset.posterState === 'ready');
          assert.equal(await page.locator('main').evaluate(el => el.classList.contains('is-motion-ready')), false);
          assert.match(await page.locator('.sr2-immersive__scene-status').textContent(), /static story scene is ready/);
        }
        if (control.startsWith('chapter-error')) {
          assert.match(await page.locator('.sr2-immersive__image-unavailable').first().textContent(), /image unavailable/);
          assert.equal(await page.locator('[data-scene-product]').count(), 0);
          const demoted = page.locator('.sr2-immersive__related-products a[data-sku="sg-005"]').first();
          assert.equal(await demoted.getAttribute('style'), null);
          assert.equal(await demoted.getAttribute('href'), fixture.products['sg-005'].url);
          assert.doesNotMatch(await page.locator('main').textContent(), /Piece in this scene/);
        }
        if (control === 'chapter-absent') { assert.equal(await page.locator('[data-scene-product]').count(), 0); assert.doesNotMatch(await page.locator('main').textContent(), /Piece in this scene/); }
        assert.ok(await page.locator('.sr2-immersive__chapter').count() > 0);
        assert.ok(await page.locator('main a[href*="/product/"]').count() > 0);
        const decline = page.locator('#skyyrose-cookie-decline');
        if (await decline.isVisible() && control !== 'javascript-disabled') await decline.tap();
        const link = page.locator('.sr2-immersive__chapter-nav a').first();
        await link.scrollIntoViewIfNeeded();
        await link.tap();
        assert.match(new URL(page.url()).hash, /^#chapter-/);
        assert.deepEqual(item.errors, []);
        item.runtime_script_hashes = [...new Set(await Promise.all(scriptBodies))];
        assert.deepEqual(item.runtime_script_hashes, control === 'javascript-disabled' ? [] : [report.source_pins['assets/js/immersive.min.js']]);
        item.scene_state = await page.locator('main').getAttribute('data-scene-state');
        item.poster_state = await page.locator('main').getAttribute('data-poster-state');
        await page.screenshot({ path: path.join(out, control + '.png'), fullPage: true });
        item.status = 'PASS';
      } catch (error) {
        item.error = error.message;
        await page.screenshot({ path: path.join(out, control + '-failure.png'), fullPage: true }).catch(() => {});
      } finally {
        releaseImage(); releaseScript();
        await context.tracing.stop({ path: path.join(out, control + '.zip') });
        await context.close();
        report.cases.push(item);
        fs.writeFileSync(path.join(out, 'results.json'), JSON.stringify(report, null, 2) + '\n');
        console.log(item.status, control, item.error || '');
      }
    }
  } finally { await browser.close(); }
  report.status = report.cases.length === controls.length && report.cases.every(c => c.status === 'PASS') ? 'PASS' : 'FAIL';
  fs.writeFileSync(path.join(out, 'results.json'), JSON.stringify(report, null, 2) + '\n');
  process.exitCode = report.status === 'PASS' ? 0 : 1;
})().catch(error => { console.error(error); process.exitCode = 1; });
