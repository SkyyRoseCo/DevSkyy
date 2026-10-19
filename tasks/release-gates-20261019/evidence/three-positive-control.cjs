'use strict';
// Optional native Three layer probe using real software WebGL, no source override.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { chromium } = require('../../../tools/v2-runtime/phase3b-browser/node_modules/playwright');
const root = path.resolve(__dirname, '../../..');
const fixture = JSON.parse(fs.readFileSync(path.join(__dirname, 'native-browser-fixture.json')));
const base = 'http://127.0.0.1:18362';
if (fixture.home !== base) throw new Error('Private loopback fixture required');
const args = ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'];
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const report = { classification: 'REPRODUCED_LOCAL_NATIVE_OPTIONAL_LAYER_PROBE', authentication: 'NOT_APPLICABLE', driver_sha256: sha(fs.readFileSync(__filename)), fixture_sha256: sha(fs.readFileSync(path.join(__dirname, 'native-browser-fixture.json'))), browser_args: args, source_override: false, cases: [], creative_acceptance: false, limits: ['Software WebGL is not physical-device GPU qualification', 'Optional atmosphere does not establish full immersive creative acceptance', 'No original chapter media admission or product GLB acceptance is changed'] };
(async () => {
  const browser = await chromium.launch({ args }); report.browser = await browser.version();
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: 'no-preference' });
    await context.route('**/*', route => new URL(route.request().url()).origin === base ? route.continue() : route.abort('blockedbyclient'));
    for (const route of fixture.routes.filter(item => item.kind === 'world')) {
      const page = await context.newPage(); const item = { path: route.path, errors: [] };
      page.on('pageerror', error => item.errors.push(error.message));
      const scripts = []; page.on('response', response => { if (new URL(response.url()).pathname.endsWith('/assets/js/immersive.min.js')) scripts.push(response.body().then(sha)); });
      try {
        const response = await page.goto(base + route.path, { waitUntil: 'load' }); item.http_status = response.status();
        await page.waitForFunction(() => ['three-ready', 'three-timeout', 'webgl-unavailable', 'scene-error'].includes(document.querySelector('main.sr2-immersive')?.dataset.sceneState), undefined, { timeout: 16000 }).catch(() => {});
        item.state = await page.locator('main.sr2-immersive').getAttribute('data-scene-state');
        item.motion_class = await page.locator('main.sr2-immersive').evaluate(el => el.classList.contains('is-motion-ready'));
        item.canvas_hidden = await page.locator('.sr2-immersive__canvas').evaluate(el => el.hidden);
        item.script_hashes = [...new Set(await Promise.all(scripts))];
        item.status = item.http_status === 200 && item.state === 'three-ready' && item.motion_class && !item.canvas_hidden && !item.errors.length ? 'PASS_OPTIONAL_THREE_LAYER' : 'NOT_ESTABLISHED';
      } catch (error) { item.status = 'NOT_ESTABLISHED'; item.error = error.message; }
      finally { await page.close(); report.cases.push(item); }
    }
    await context.close();
  } finally { await browser.close(); }
  report.status = report.cases.length === 4 && report.cases.every(item => item.status === 'PASS_OPTIONAL_THREE_LAYER') ? 'PASS_OPTIONAL_THREE_LAYER' : 'NOT_ESTABLISHED';
  fs.writeFileSync(path.join(__dirname, 'three-positive-control.json'), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify(report));
})().catch(error => { console.error(error); process.exitCode = 1; });
