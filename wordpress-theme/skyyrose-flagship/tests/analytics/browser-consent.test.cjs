/** Rendered theme banner in a local browser fixture; live authentication N/A. */
const assert = require('node:assert/strict');
const { test } = require('node:test');
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const { chromium } = require('playwright');
const theme = path.resolve(__dirname, '../..');
const banner = execFileSync(
  'php',
  [
    '-r',
    `define('ABSPATH', '${theme}'); function home_url($p) {return $p;} function esc_url($v) {return $v;} function esc_attr_e($v,$d) {echo $v;} function esc_html_e($v,$d) {echo $v;} function esc_html__($v,$d) {return $v;} include '${theme}/template-parts/cookie-consent.php';`,
  ],
  { encoding: 'utf8' }
);
const css = fs.readFileSync(path.join(theme, 'assets/css/cookie-consent.css'), 'utf8');
const analyzer = fs.readFileSync(path.join(theme, 'assets/js/experience-analyzer.min.js'), 'utf8');
const renderedCard = require('./rendered-card.cjs')();
const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><style>${css}</style></head><body><main><h1>Consent fixture</h1><button id="outside">Page control</button>${renderedCard}</main>${banner}<script>window.skyyroseSEE={key:'public-token'};</script><script>${analyzer}</script></body></html>`;
for (const viewport of [
  { width: 1280, height: 800 },
  { width: 375, height: 812 },
]) {
  test(`rendered banner at ${viewport.width}px supports accept/revoke and keyboard controls`, async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage({ viewport });
    const errors = [];
    const requests = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.route('https://fixture.test/**', async route => {
      if (route.request().method() === 'POST') {
        const body = route.request().postDataJSON();
        requests.push(body);
        return route.fulfill({
          contentType: 'application/json',
          body: JSON.stringify({
            status: 'accepted',
            accepted: body.events.length,
            duplicates: 0,
            event_ids: body.events.map(e => e.event_id),
          }),
        });
      }
      return route.fulfill({ contentType: 'text/html', body: html });
    });
    try {
      await page.goto('https://fixture.test/collections/fixture/');
      const dialog = page.locator('#skyyrose-cookie-consent');
      await dialog.waitFor({ state: 'visible' });
      await page.waitForFunction(() => document.activeElement.id === 'skyyrose-cookie-accept');
      assert.equal(await page.evaluate(() => localStorage.getItem('skyy_vh')), null);
      assert.equal(await page.evaluate(() => localStorage.getItem('skyy_analytics_session')), null);
      assert.equal(requests.length, 0);
      await page.screenshot({ path: `/tmp/e2e-theme-consent-${viewport.width}.png`, fullPage: true });
      await page.locator('#skyyrose-cookie-decline').focus();
      await page.keyboard.press('Tab');
      assert.equal(await page.evaluate(() => document.activeElement.className), 'cookie-consent__link');
      await page.keyboard.press('Escape');
      assert.equal(await page.evaluate(() => localStorage.getItem('skyyrose_cookie_consent')), 'declined');
      await page.evaluate(() => document.dispatchEvent(new CustomEvent('skyyrose:consent-open')));
      await page.locator('#skyyrose-cookie-accept').click();
      assert.match(
        await page.evaluate(() => JSON.parse(localStorage.getItem('skyy_analytics_session')).id),
        /^[a-f0-9]{32}$/
      );
      assert.equal(await page.evaluate(() => localStorage.getItem('skyy_vh')), null);
      await page.locator('.holo__buy').click();
      await page.evaluate(() => window.dispatchEvent(new Event('pagehide')));
      await page.waitForFunction(() =>
        document.querySelector('#skyyrose-cookie-consent').classList.contains('cookie-consent--hidden')
      );
      await page.waitForTimeout(100);
      assert.equal(requests.length, 1);
      assert.ok(requests[0].events.some(event => event.event_type === 'product_click'));
      assert.ok(
        requests[0].events.some(
          event =>
            event.event_type === 'product_click' && event.target === 'fixture-001' && event.collection === 'fixture'
        )
      );
      assert.ok(requests[0].events.filter(event => event.event_type === 'product_view').length <= 1);
      assert.equal(
        requests[0].events.some(event => event.event_type === 'add_to_cart'),
        false
      );
      await page.evaluate(() => document.dispatchEvent(new CustomEvent('skyyrose:consent-revoke')));
      assert.equal(await page.evaluate(() => localStorage.getItem('skyy_vh')), null);
      assert.equal(await page.evaluate(() => localStorage.getItem('skyy_analytics_session')), null);
      await page.locator('.holo__buy').click();
      await page.evaluate(() => window.dispatchEvent(new Event('pagehide')));
      await page.waitForTimeout(100);
      assert.equal(requests.length, 1);
      assert.deepEqual(errors, []);
    } finally {
      await browser.close();
    }
  });
}
