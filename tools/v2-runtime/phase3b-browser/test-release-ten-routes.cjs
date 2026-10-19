'use strict';

// Local native WordPress/WooCommerce gate. Never accepts an external origin.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '../../..');
const base = 'http://127.0.0.1:18362';
const smoke = process.argv.includes('--smoke');
const fixture = JSON.parse(fs.readFileSync(path.join(root, 'tasks/release-gates-20261019/evidence/native-browser-fixture.json')));
assert.equal(fixture.home, base);
assert.equal(fixture.routes.length, 10);
assert.equal(new Set(Object.values(fixture.products).map(p => p.url)).size, Object.keys(fixture.products).length, 'native product URLs must be unique');
for (const product of Object.values(fixture.products)) assert.equal(new URL(product.url).origin, base);
const out = path.join(root, 'tasks/release-gates-20261019/evidence', smoke ? 'browser-smoke' : 'browser-ten-routes');
fs.mkdirSync(out, { recursive: true });
const sha = data => crypto.createHash('sha256').update(data).digest('hex');
const theme = path.join(root, 'wordpress-theme/skyyrose-flagship-2');
const sourcePins = Object.fromEntries(['assets/js/immersive.js', 'assets/js/immersive.min.js', 'template-parts/immersive/world.php', 'data/v2-media-eligibility.json'].map(p => [p, sha(fs.readFileSync(path.join(theme, p)))]));
const profiles = smoke ? [{ name: 'desktop-reduced', width: 1440, height: 900, reducedMotion: 'reduce' }] : [
  { name: 'desktop-full', width: 1440, height: 900, reducedMotion: 'no-preference' },
  { name: 'desktop-reduced', width: 1440, height: 900, reducedMotion: 'reduce' },
  { name: 'mobile-full', width: 390, height: 844, reducedMotion: 'no-preference', mobile: true },
  { name: 'mobile-reduced', width: 390, height: 844, reducedMotion: 'reduce', mobile: true },
];
const routes = smoke ? fixture.routes.filter(r => ['signature', 'immersive-signature'].includes(r.logical_key)) : fixture.routes;
const report = { classification: 'REPRODUCED_LOCAL_NATIVE', authentication: 'NOT_APPLICABLE', scope: 'Synthetic isolated core + WooCommerce; no production, creative, or third-party plugin acceptance', started_utc: new Date().toISOString(), commit: execFileSync('git', ['rev-parse', 'HEAD'], { cwd: root, encoding: 'utf8' }).trim(), dirty_diff_sha256: sha(execFileSync('git', ['diff', '--binary'], { cwd: root })), source_pins: sourcePins, fixture_sha256: sha(fs.readFileSync(path.join(root, 'tasks/release-gates-20261019/evidence/native-browser-fixture.json'))), cases: [], faults: [] };
report.runtime = { wp: fixture.wp, woo: fixture.woocommerce };
report.driver_sha256 = sha(fs.readFileSync(__filename));
report.fixture_driver_hashes = Object.fromEntries(['tools/v2-runtime/seed-release-fixture.php', 'tools/v2-runtime/refresh-release-fixture.php'].map(p => [p, sha(fs.readFileSync(path.join(root, p)))]));

async function dismissConsent(page) {
  const button = page.locator('#skyyrose-cookie-decline');
  if (await button.isVisible()) await button.click();
}

async function assertMenu(page, mobile) {
  const button = page.locator('button[data-sr2-menu]');
  if (!await button.isVisible()) {
    assert.equal(Boolean(mobile), false, 'mobile navigation control must be available');
    await page.keyboard.press('Tab');
    return;
  }
  if (mobile) await button.tap(); else await button.click();
  assert.equal(await button.getAttribute('aria-expanded'), 'true');
  await page.keyboard.press('Escape');
  assert.equal(await button.getAttribute('aria-expanded'), 'false');
  assert.equal(await button.evaluate(el => el === document.activeElement), true);
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  report.browser = await browser.version();
  try {
    for (const profile of profiles) {
      const context = await browser.newContext({ viewport: { width: profile.width, height: profile.height }, reducedMotion: profile.reducedMotion, isMobile: Boolean(profile.mobile), hasTouch: Boolean(profile.mobile) });
      const blocked = [];
      await context.route('**/*', route => {
        if (new URL(route.request().url()).origin === base) return route.continue();
        blocked.push(new URL(route.request().url()).origin);
        return route.abort('blockedbyclient');
      });
      for (const route of routes) {
        const label = `${profile.name}-${route.logical_key}`;
        const item = { label, route, profile, status: 'FAIL', page_errors: [] };
        const page = await context.newPage();
        page.on('pageerror', error => item.page_errors.push(error.message));
        const scriptBodies = [];
        page.on('response', response => {
          if (new URL(response.url()).pathname.endsWith('/assets/js/immersive.min.js')) scriptBodies.push(response.body().then(body => sha(body)));
        });
        await context.tracing.start({ screenshots: true, snapshots: true, sources: false });
        try {
          const response = await page.goto(base + route.path, { waitUntil: 'load', timeout: 30000 });
          assert.equal(response.status(), 200);
          assert.equal(new URL(page.url()).pathname, route.path);
          item.effective_url = page.url();
          item.template = response.headers()['x-sr-fixture-template'];
          assert.equal(item.template, route.template === 'default' ? 'page.php' : route.template);
          await dismissConsent(page);
          await page.waitForTimeout(150);
          assert.equal(await page.locator('main').count() > 0, true);
          assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), true, 'no horizontal page overflow');
          if (route.kind === 'world') {
            const world = page.locator('main.sr2-immersive');
            assert.equal(await world.getAttribute('data-collection'), route.collection);
            const poster = world.locator('.sr2-immersive__poster img');
            if (await poster.count()) {
              await poster.evaluate(image => image.decode());
              assert.equal(await poster.getAttribute('data-media-role'), 'collection_hero');
              const sku = await poster.getAttribute('data-media-sku');
              assert.equal(fixture.products[sku].collection, route.collection);
              item.hero = { sku, src: await poster.getAttribute('src'), loaded: true };
            } else {
              assert.match(await world.locator('.sr2-immersive__scene-status').textContent(), /unavailable/);
              item.hero = { status: 'UNAVAILABLE_HONEST_FALLBACK' };
            }
            item.scene_state = await world.getAttribute('data-scene-state');
            item.chapter_fidelity = await world.locator('article.sr2-immersive__chapter').evaluateAll(chapters => chapters.map(chapter => ({ original_available: chapter.dataset.originalSceneAvailable, image_sku: chapter.querySelector('.sr2-immersive__chapter-media > img')?.dataset.mediaSku || null, scene_claims: [...chapter.querySelectorAll('[data-scene-product]')].map(a => ({ sku: a.dataset.sku, style: a.getAttribute('style') })), related: [...chapter.querySelectorAll('.sr2-immersive__related-products a')].map(a => ({ sku: a.dataset.sku, href: a.href, style: a.getAttribute('style'), text: a.textContent })) })));
            for (const chapter of item.chapter_fidelity) {
              if (chapter.original_available === 'false') assert.deepEqual(chapter.scene_claims, [], 'fallback pixels never inherit original scene-SKU claims');
              for (const link of chapter.related) { assert.equal(link.style, null); assert.doesNotMatch(link.text, /Piece in this scene/); }
            }
            assert.deepEqual([...new Set(await Promise.all(scriptBodies))], [sourcePins['assets/js/immersive.min.js']], 'runtime-selected rebuilt script matches exact tested bytes');
          }
          const links = await page.locator('main a[href*="/product/"]').evaluateAll(nodes => nodes.filter(n => n.getClientRects().length).map(n => ({ href: n.href, sku: n.dataset.sku || n.closest('[data-sku]')?.dataset.sku || null })));
          item.native_product_links = links;
          if (['collection', 'world'].includes(route.kind)) assert.ok(links.length > 0, 'product-bearing route has visible native product CTAs');
          for (const link of links) {
            assert.equal(new URL(link.href).origin, base);
            const product = Object.entries(fixture.products).find(([, p]) => new URL(p.url).pathname === new URL(link.href).pathname);
            assert.ok(product, `visible product CTA resolves a fixture native canonical identity: ${link.href}`);
            if (link.sku) assert.equal(link.sku, product[0]);
            if (route.collection) assert.equal(product[1].collection, route.collection);
          }
          await assertMenu(page, profile.mobile);
          await page.reload({ waitUntil: 'load' });
          await page.goto(base + '/shop/', { waitUntil: 'load' });
          await page.goBack({ waitUntil: 'load' });
          assert.equal(new URL(page.url()).pathname, route.path);
          await page.goForward({ waitUntil: 'load' });
          assert.equal(new URL(page.url()).pathname, '/shop/');
          await page.goBack({ waitUntil: 'load' });
          assert.equal(new URL(page.url()).pathname, route.path);
          await dismissConsent(page);
          await page.screenshot({ path: path.join(out, `${label}.png`), fullPage: true });
          assert.deepEqual(item.page_errors, []);
          item.status = 'PASS';
        } catch (error) {
          item.error = error.message;
          await page.screenshot({ path: path.join(out, `${label}-failure.png`), fullPage: true }).catch(() => {});
        } finally {
          await context.tracing.stop({ path: path.join(out, `${label}.zip`) });
          await page.close();
          report.cases.push(item);
          fs.writeFileSync(path.join(out, 'results.json'), JSON.stringify(report, null, 2) + '\n');
          console.log(item.status, label, item.error || '');
        }
      }
      report.blocked_external_origins = [...new Set([...(report.blocked_external_origins || []), ...blocked])];
      await context.close();
    }
  } finally { await browser.close(); }
  report.finished_utc = new Date().toISOString();
  report.status = report.cases.length === routes.length * profiles.length && report.cases.every(c => c.status === 'PASS') ? 'PASS_PRIMARY_TECHNICAL_CASES' : 'FAIL';
  report.creative_acceptance = 'NOT_GRANTED';
  fs.writeFileSync(path.join(out, 'results.json'), JSON.stringify(report, null, 2) + '\n');
  process.exitCode = report.status === 'FAIL' ? 1 : 0;
})().catch(error => { report.fatal = error.message; report.status = 'BLOCKED'; fs.writeFileSync(path.join(out, 'results.json'), JSON.stringify(report, null, 2) + '\n'); console.error(error.message); process.exitCode = 1; });
