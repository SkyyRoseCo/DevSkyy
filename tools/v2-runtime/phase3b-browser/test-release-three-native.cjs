'use strict';
// Native approved Three core/scene execution; no injected THREE or renderer.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '../../..');
const base = 'http://127.0.0.1:18362';
const fixtureFile = path.join(root, 'tasks/release-gates-20261019/evidence/native-browser-fixture.json');
const fixture = JSON.parse(fs.readFileSync(fixtureFile));
assert.equal(fixture.home, base);
const theme = path.join(root, 'wordpress-theme/skyyrose-flagship-2');
const out = path.join(root, 'tasks/release-gates-20261019/successor-three/evidence/native-three');
fs.mkdirSync(out, { recursive: true });
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const pins = Object.fromEntries(['functions.php', 'template-parts/immersive/world.php', 'assets/js/three-core-loader.js', 'assets/js/three-core-loader.min.js', 'assets/js/immersive.js', 'assets/js/immersive.min.js', 'assets/js/skyy-3d.js', 'assets/js/skyy-3d.min.js', 'assets/js/lib/three-r170/three.module.min.js'].map(file => [file, sha(fs.readFileSync(path.join(theme, file)))]));
const report = { classification: 'REPRODUCED_LOCAL_NATIVE_THREE', authentication: 'NOT_APPLICABLE', driver_sha256: sha(fs.readFileSync(__filename)), fixture_sha256: sha(fs.readFileSync(fixtureFile)), source_pins: pins, browser_args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'], ignored_default_args: ['--disable-back-forward-cache'], runtime: { wp: fixture.wp, woo: fixture.woocommerce }, cases: [], faults: [], limits: ['Software WebGL; not physical-device GPU/performance qualification', 'Optional atmosphere is separate from full immersive creative acceptance', 'Existing approved assets only; no positive original chapter admission or product GLB acceptance'] };
const corePath = '/assets/js/lib/three-r170/three.module.min.js';
const forbidden = url => /\/assets\/js\/(?:skyy-3d|mascot)[^/]*\.js|\/assets\/models\/|\/draco\/|GLTFLoader\.js|DRACOLoader\.js|\.glb(?:\?|$)/.test(url);
async function ready(page) {
  await page.waitForFunction(() => document.querySelector('main.sr2-immersive')?.dataset.sceneState === 'three-ready' && document.querySelector('.sr2-immersive__canvas')?.skyyRoseRenderedFrames >= 2, undefined, { timeout: 15000 });
}
async function counters(page) { return page.locator('main.sr2-immersive').evaluate(el => ({ state: el.dataset.sceneState, boots: Number(el.dataset.sceneBoots || 0), resumes: Number(el.dataset.sceneResumes || 0), frames: el.querySelector('canvas').skyyRoseRenderedFrames || 0, hidden: el.querySelector('canvas').hidden, disposed: el.querySelector('canvas').dataset.sceneDisposed === 'true' })); }
async function dimensions(page) {
  const actual = await page.locator('.sr2-immersive__canvas').evaluate(canvas => {
    const gl = canvas.getContext('webgl2');
    return { cssWidth: canvas.clientWidth, cssHeight: canvas.clientHeight, width: canvas.width, height: canvas.height, bufferWidth: gl.drawingBufferWidth, bufferHeight: gl.drawingBufferHeight, dpr: Math.min(devicePixelRatio || 1, 1.75), display: getComputedStyle(canvas).display, hidden: canvas.hidden, cameraAspect: canvas.skyyRoseCameraAspect };
  });
  assert.ok(actual.cssWidth > 1 && actual.cssHeight > 1);
  assert.ok(Math.abs(actual.cameraAspect - actual.cssWidth / actual.cssHeight) < 0.00001, 'camera projection matches visible containing block');
  assert.notEqual(actual.display, 'none'); assert.equal(actual.hidden, false);
  for (const [buffer, css] of [['width', 'cssWidth'], ['height', 'cssHeight'], ['bufferWidth', 'cssWidth'], ['bufferHeight', 'cssHeight']]) assert.ok(Math.abs(actual[buffer] - Math.floor(actual[css] * actual.dpr)) <= 1, 'initial/resumed drawing buffer matches displayed CSS extent: ' + JSON.stringify(actual));
  return actual;
}
async function observe(context) {
  const page = await context.newPage(); const requests = []; const errors = []; const responses = [];
  page.on('request', request => requests.push(request.url())); page.on('pageerror', error => errors.push(error.message));
  page.on('response', response => { const p = new URL(response.url()).pathname; if (p.endsWith('/three-core-loader.min.js') || p.endsWith('/immersive.min.js') || p.endsWith(corePath)) responses.push(response.body().then(body => ({ path: p, sha256: sha(body) }))); });
  return { page, requests, errors, responses };
}
async function network(context, intercept) { await context.route('**/*', async route => { if (new URL(route.request().url()).origin !== base) return route.abort('blockedbyclient'); if (intercept && await intercept(route)) return; return route.continue(); }); }
function assertResponses(items) {
  for (const file of ['assets/js/three-core-loader.min.js', 'assets/js/immersive.min.js', 'assets/js/lib/three-r170/three.module.min.js']) assert.ok(items.some(item => item.path.endsWith('/' + file) && item.sha256 === pins[file]), 'served bytes match ' + file);
}
(async () => {
  const browser = await chromium.launch({ args: report.browser_args, ignoreDefaultArgs: report.ignored_default_args }); report.browser = await browser.version();
  try {
    for (const profile of [{ name: 'desktop', width: 1440, height: 900 }, { name: 'mobile', width: 390, height: 844, mobile: true }]) {
      for (const route of fixture.routes.filter(item => item.kind === 'world')) {
        const context = await browser.newContext({ viewport: { width: profile.width, height: profile.height }, isMobile: Boolean(profile.mobile), hasTouch: Boolean(profile.mobile), reducedMotion: 'no-preference' });
        await network(context); const observed = await observe(context); const { page, requests, errors, responses } = observed;
        const item = { profile: profile.name, route: route.path, status: 'FAIL' };
        try {
          const response = await page.goto(base + route.path, { waitUntil: 'load' }); assert.equal(response.status(), 200); await ready(page);
          const before = await counters(page); await page.waitForFunction(value => document.querySelector('.sr2-immersive__canvas').skyyRoseRenderedFrames > value, before.frames);
          item.initial = await counters(page); assert.equal(item.initial.boots, 1); assert.equal(item.initial.hidden, false);
          item.initial_dimensions = await dimensions(page);
          await page.screenshot({ path: path.join(out, profile.name + '-' + route.collection + '-initial.png') });
          const coreRequests = requests.filter(url => new URL(url).pathname.endsWith(corePath)); assert.equal(coreRequests.length, 1); assert.equal(new URL(coreRequests[0]).search, '');
          assert.equal(await page.evaluate(async () => { const values = await Promise.all(Array.from({ length: 8 }, () => window.skyyRoseThreeCore.load())); return values.every(value => value[0] === window.THREE); }), true);
          await page.evaluate(() => { document.dispatchEvent(new Event('three-ready')); window.dispatchEvent(new Event('three-ready')); }); assert.equal((await counters(page)).boots, 1);
          await page.goto(base + '/shop/', { waitUntil: 'load' }); await page.goBack({ waitUntil: 'load' }); await page.waitForURL(base + route.path); await ready(page); item.history_return = await counters(page); item.history_dimensions = await dimensions(page); assert.equal(item.history_return.boots, 1); assert.equal(item.history_return.disposed, false);
          const historyFrames = item.history_return.frames; await page.waitForFunction(value => document.querySelector('.sr2-immersive__canvas').skyyRoseRenderedFrames > value, historyFrames);
          await page.goForward({ waitUntil: 'load' }); await page.waitForURL(base + '/shop/'); await page.goBack({ waitUntil: 'load' }); await page.waitForURL(base + route.path); await ready(page);
          await page.reload({ waitUntil: 'load' }); await ready(page); assert.equal((await counters(page)).boots, 1);
          item.requests = requests; assert.deepEqual(requests.filter(forbidden), []); assert.deepEqual(errors, []);
          item.served = await Promise.all(responses); assertResponses(item.served);
          await page.screenshot({ path: path.join(out, profile.name + '-' + route.collection + '.png') }); item.status = 'PASS';
        } catch (error) { item.error = error.message; item.requests = requests; item.errors = errors; }
        finally { await context.close(); report.cases.push(item); fs.writeFileSync(path.join(out, 'results.json'), JSON.stringify(report, null, 2) + '\n'); console.log(item.status, profile.name, route.path, item.error || ''); }
      }
    }
    for (const fault of ['reduced-motion', 'save-data', 'core-missing', 'timeout-then-late-core', 'pagehide-then-late-core', 'motion-change-then-late-core', 'save-data-change-then-late-core', 'persisted-page-pause-resume', 'persisted-before-first-frame-timeout', 'persisted-before-first-frame-success', 'poster-success-before-first-frame', 'poster-success-after-scene-failure', 'matching-initial-buffer', 'late-poster-error', 'context-loss', 'checkout']) {
      const context = await browser.newContext({ viewport: fault === 'matching-initial-buffer' ? { width: 1280, height: 720 } : { width: 390, height: 844 }, reducedMotion: fault === 'reduced-motion' ? 'reduce' : 'no-preference' });
      if (fault === 'save-data') await context.addInitScript(() => Object.defineProperty(navigator, 'connection', { value: { saveData: true } }));
      if (fault === 'save-data-change-then-late-core') await context.addInitScript(() => { const connection = new EventTarget(); window.srSyntheticSaveData = false; Object.defineProperty(connection, 'saveData', { get: () => window.srSyntheticSaveData }); Object.defineProperty(navigator, 'connection', { value: connection }); });
      if (fault === 'poster-success-before-first-frame' || fault.startsWith('persisted-before-first-frame')) await context.addInitScript(() => {
        const native = window.requestAnimationFrame.bind(window);
        window.srReleaseFrames = false; window.srHeldFrames = [];
        window.requestAnimationFrame = callback => native(time => { if (window.srReleaseFrames) callback(time); else window.srHeldFrames.push(callback); });
        window.srResumeFrames = () => { window.srReleaseFrames = true; window.srHeldFrames.splice(0).forEach(callback => native(callback)); };
      });
      if (fault === 'poster-success-after-scene-failure') await context.addInitScript(() => {
        const native = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function(type, ...args) { return this.classList.contains('sr2-immersive__canvas') && type.startsWith('webgl') ? null : native.call(this, type, ...args); };
      });
      let posterSource;
      let release; let requested; const gate = new Promise(resolve => { release = resolve; }); const seen = new Promise(resolve => { requested = resolve; });
      await network(context, async route => {
        const url = new URL(route.request().url());
        if (['poster-success-before-first-frame', 'poster-success-after-scene-failure', 'matching-initial-buffer'].includes(fault) && route.request().resourceType() === 'document') {
          const response = await route.fetch();
          let html = await response.text();
          if (fault === 'matching-initial-buffer') { html = html.replace('</head>', '<style>.sr2-immersive__entry{min-height:0!important;height:720px!important}</style></head>'); await route.fulfill({ response, body: html }); return true; }
          html = html.replace(/(<div class="sr2-immersive__poster[^>]*>)([\s\S]*?)(<\/div>)/, (_, start, middle, end) => {
            posterSource = new URL(middle.match(/src="([^"]*)"/)[1].replaceAll('&amp;', '&'), base).href;
            return start + middle.replace(/src="[^"]*"/, 'src="/synthetic-delayed-poster.webp"').replace(/srcset="[^"]*"/, '') + end;
          });
          await route.fulfill({ response, body: html }); return true;
        }
        if (['poster-success-before-first-frame', 'poster-success-after-scene-failure'].includes(fault) && url.pathname === '/synthetic-delayed-poster.webp') {
          await gate; await route.fulfill({ response: await route.fetch({ url: posterSource }) }); return true;
        }
        if (!url.pathname.endsWith(corePath)) return false;
        requested();
        if (fault === 'core-missing') { await route.fulfill({ status: 503, contentType: 'text/javascript', body: '/* Synthetic dependency failure */' }); return true; }
        if (fault.includes('then-late-core')) { await gate; await route.continue(); return true; }
        return false;
      });
      const { page, requests, errors, responses } = await observe(context); const item = { fault, status: 'FAIL' };
      try {
        if (fault === 'checkout') {
          const simple = Object.values(fixture.products).find(product => !Object.keys(product.children).length);
          assert.ok(simple);
          const cart = await context.request.get(base + '/?add-to-cart=' + simple.id);
          assert.ok(cart.status() < 400, 'synthetic native cart prerequisite');
        }
        await page.goto(base + (fault === 'checkout' ? '/checkout/' : fixture.routes.find(route => route.kind === 'world').path), { waitUntil: ['poster-success-before-first-frame', 'poster-success-after-scene-failure'].includes(fault) ? 'commit' : 'load' });
        if (fault.includes('then-late-core')) {
          await Promise.race([seen, new Promise((_, reject) => setTimeout(() => reject(new Error('Core request not observed')), 15000))]);
          if (fault === 'timeout-then-late-core') await page.waitForFunction(() => document.querySelector('main').dataset.sceneState === 'three-unavailable', undefined, { timeout: 12000 });
          if (fault === 'pagehide-then-late-core') await page.evaluate(() => window.dispatchEvent(new PageTransitionEvent('pagehide', { persisted: false })));
          if (fault === 'motion-change-then-late-core') await page.emulateMedia({ reducedMotion: 'reduce' });
          if (fault === 'save-data-change-then-late-core') await page.evaluate(() => { window.srSyntheticSaveData = true; navigator.connection.dispatchEvent(new Event('change')); });
          release(); await page.waitForTimeout(500); item.after = await counters(page); assert.equal(item.after.boots, 0); assert.equal(item.after.frames, 0); assert.notEqual(item.after.state, 'three-ready');
        } else if (fault === 'persisted-page-pause-resume') {
          await ready(page);
          await page.evaluate(() => window.dispatchEvent(new PageTransitionEvent('pagehide', { persisted: true })));
          const paused = await counters(page); await page.waitForTimeout(250); assert.equal((await counters(page)).frames, paused.frames);
          await page.evaluate(() => window.dispatchEvent(new PageTransitionEvent('pageshow', { persisted: true })));
          await ready(page); item.after = await counters(page); item.dimensions = await dimensions(page); assert.equal(item.after.resumes, 1); assert.equal(item.after.boots, 1); assert.equal(item.after.disposed, false);
          item.event_scope = 'Synthetic persisted lifecycle events on actual native renderer; real back/forward is separately exercised';
        } else if (fault.startsWith('persisted-before-first-frame')) {
          await page.waitForFunction(() => document.querySelector('main')?.dataset.sceneState === 'three-rendering', undefined, { polling: 50 });
          assert.equal((await counters(page)).frames, 0);
          await page.evaluate(() => { window.dispatchEvent(new PageTransitionEvent('pagehide', { persisted: true })); window.dispatchEvent(new PageTransitionEvent('pageshow', { persisted: true })); });
          if (fault.endsWith('timeout')) {
            await page.waitForFunction(() => document.querySelector('main').dataset.sceneState === 'three-timeout', undefined, { polling: 50, timeout: 12000 });
            item.after = await counters(page); assert.equal(item.after.boots, 1); assert.equal(item.after.frames, 0); assert.equal(item.after.disposed, true); assert.equal(item.after.hidden, true);
            await page.evaluate(() => window.srResumeFrames()); await page.waitForTimeout(100); assert.equal((await counters(page)).frames, 0);
          } else {
            await page.evaluate(() => window.srResumeFrames()); await ready(page); item.after = await counters(page); item.dimensions = await dimensions(page); assert.equal(item.after.boots, 1); assert.equal(item.after.resumes, 1); assert.equal(item.after.disposed, false);
          }
          item.event_scope = 'Synthetic persisted lifecycle and withheld-first-RAF timing on actual native renderer';
        } else if (fault === 'poster-success-before-first-frame') {
          await page.waitForFunction(() => document.querySelector('main')?.dataset.sceneState === 'three-rendering', undefined, { polling: 50 });
          assert.equal((await counters(page)).frames, 0);
          release();
          await page.waitForFunction(() => document.querySelector('main').dataset.posterState === 'ready', undefined, { polling: 50 });
          assert.equal((await counters(page)).state, 'three-rendering');
          await page.evaluate(() => window.srResumeFrames()); await ready(page);
          item.after = await counters(page); item.dimensions = await dimensions(page);
          assert.equal(item.after.boots, 1); assert.equal(item.after.hidden, false);
          await page.waitForFunction(value => document.querySelector('.sr2-immersive__canvas').skyyRoseRenderedFrames > value, item.after.frames);
          item.timing_scope = 'Synthetic successful poster delivery and RAF timing; native approved image bytes, Three core, renderer and context';
        } else if (fault === 'poster-success-after-scene-failure') {
          await page.waitForFunction(() => document.querySelector('main')?.dataset.sceneState === 'scene-error');
          release(); await page.waitForFunction(() => document.querySelector('main').dataset.posterState === 'ready');
          await page.waitForFunction(() => document.querySelector('.sr2-immersive__scene-status').textContent.includes('static story scene is ready'));
          item.after = await counters(page); assert.equal(item.after.frames, 0); assert.equal(item.after.hidden, true); assert.notEqual(item.after.state, 'three-ready');
          assert.deepEqual(errors, []);
          item.timing_scope = 'Synthetic failed canvas context acquisition and delayed successful approved poster; actual core and attempted native renderer';
        } else if (fault === 'matching-initial-buffer') {
          await ready(page); item.dimensions = await dimensions(page);
          assert.equal(item.dimensions.width, 1280); assert.equal(item.dimensions.height, 720); assert.equal(item.dimensions.cameraAspect, 1280 / 720);
          item.fixture_scope = 'Synthetic entry CSS fixes initial containing block to existing HTML1280x720 buffer; native core/camera/renderer';
        } else if (fault === 'late-poster-error') {
          await ready(page); await page.locator('.sr2-immersive__poster img').evaluate(image => { image.removeAttribute('srcset'); image.src = '/synthetic-private-missing-poster.webp'; });
          await page.waitForFunction(() => document.querySelector('main').dataset.posterState === 'unavailable');
          const stopped = await counters(page); await page.waitForTimeout(250); item.after = await counters(page); assert.equal(item.after.frames, stopped.frames); assert.equal(item.after.hidden, true); assert.equal(item.after.disposed, true);
        } else if (fault === 'context-loss') {
          await ready(page); await page.evaluate(() => document.querySelector('.sr2-immersive__canvas').getContext('webgl2').getExtension('WEBGL_lose_context').loseContext());
          await page.waitForFunction(() => document.querySelector('main').dataset.sceneState === 'webgl-context-lost'); const stopped = await counters(page); await page.waitForTimeout(250); item.after = await counters(page); assert.equal(item.after.frames, stopped.frames); assert.equal(item.after.hidden, true); assert.equal(item.after.disposed, true);
        } else if (fault === 'core-missing') { await page.waitForFunction(() => document.querySelector('main').dataset.sceneState === 'three-unavailable'); assert.equal((await counters(page)).boots, 0); }
        else {
          await page.waitForTimeout(150);
          assert.equal(requests.filter(url => new URL(url).pathname.endsWith(corePath)).length, 0);
          if (fault === 'checkout') { assert.equal(new URL(page.url()).pathname, '/checkout/'); assert.equal(requests.filter(url => /three-core-loader|immersive\.min\.js/.test(url)).length, 0); }
          else assert.equal((await counters(page)).boots, 0);
        }
        assert.deepEqual(requests.filter(forbidden), []); assert.deepEqual(errors, []); item.requests = requests; item.errors = errors; item.served = await Promise.all(responses); item.status = 'PASS';
      } catch (error) { item.error = error.message; item.requests = requests; item.errors = errors; }
      finally { release(); await context.unrouteAll({ behavior: 'wait' }); await context.close(); report.faults.push(item); fs.writeFileSync(path.join(out, 'results.json'), JSON.stringify(report, null, 2) + '\n'); console.log(item.status, fault, item.error || ''); }
    }
  } finally { await browser.close(); }
  report.status = report.cases.length === 8 && report.cases.every(item => item.status === 'PASS') && report.faults.length === 16 && report.faults.every(item => item.status === 'PASS') ? 'PASS' : 'FAIL';
  fs.writeFileSync(path.join(out, 'results.json'), JSON.stringify(report, null, 2) + '\n'); process.exitCode = report.status === 'PASS' ? 0 : 1;
})().catch(error => { console.error(error); process.exitCode = 1; });
