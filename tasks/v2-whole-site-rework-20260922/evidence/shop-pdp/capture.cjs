// Agent C evidence capture: shop + PDP routes at 1440x900 and 390x844, fullPage, with the commerce journey.
const { chromium } = require('/Users/theceo/DevSkyy/node_modules/playwright');
const fs = require('fs');
const dir = __dirname;
const base = 'http://127.0.0.1:8792/tools/v2-theme-preview.php';
const routes = [
  ['shop', 'route=shop'],
  ['product-br-004', 'route=product&sku=br-004'],
  ['product-sg-005', 'route=product&sku=sg-005'],
  ['product-lh-004', 'route=product&sku=lh-004'],
  ['product-kids-001', 'route=product&sku=kids-001'],
  ['product-br-003', 'route=product&sku=br-003'],
];
const results = [];
(async () => {
  const browser = await chromium.launch({ headless: true });
  for (const [width, height] of [[1440, 900], [390, 844]]) {
    const context = await browser.newContext({ viewport: { width, height }, deviceScaleFactor: 1 });
    for (const [name, query] of routes) {
      const page = await context.newPage();
      const errors = [], consoleErrors = [], failed = [], bad = [];
      page.on('pageerror', (e) => errors.push(e.message));
      page.on('console', (m) => { if (m.type() === 'error') consoleErrors.push(m.text()); });
      page.on('requestfailed', (r) => failed.push({ url: r.url(), error: r.failure()?.errorText }));
      page.on('response', (r) => { if (r.status() >= 400) bad.push({ url: r.url(), status: r.status() }); });
      const resp = await page.goto(`${base}?${query}`, { waitUntil: 'networkidle', timeout: 45000 });
      // Scroll through the document so native lazy images (related cards, closing scene) actually load before the capture.
      await page.evaluate(async () => { for (let y = 0; y < document.documentElement.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise((r) => setTimeout(r, 90)); } window.scrollTo(0, 0); });
      await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
      // Bounded wait: a lazy image that never entered the viewport must not hang the capture.
      await page.evaluate(() => Promise.race([Promise.all([...document.images].filter((i) => !i.complete).map((i) => new Promise((r) => { i.addEventListener('load', r, { once: true }); i.addEventListener('error', r, { once: true }); }))), new Promise((r) => setTimeout(r, 4000))]));
      await page.waitForTimeout(400);
      const info = await page.evaluate(() => ({
        title: document.title,
        h1: [...document.querySelectorAll('h1')].map((x) => x.textContent.trim()),
        overflow: document.documentElement.scrollWidth > window.innerWidth,
        scrollWidth: document.documentElement.scrollWidth,
        cards: document.querySelectorAll('.sr2-c-editorial-card').length,
        framedCards: document.querySelectorAll('.sr2-c-editorial-card[data-card-frame="v2-statue"]').length,
        frameImgs: document.querySelectorAll('.sr2-c-editorial-card__frame').length,
        dataCollection: document.querySelector('main')?.getAttribute('data-collection'),
        gridColumns: (() => { const g = document.querySelector('ul.products'); return g ? getComputedStyle(g).gridTemplateColumns.split(' ').length : 0; })(),
        fonts: [...new Set([...document.querySelectorAll('h1, h2, .sr2-c-editorial-card__title, .price, .sr2-eyebrow')].map((e) => getComputedStyle(e).fontFamily.split(',')[0]))],
        brokenImages: [...document.images].filter((i) => i.complete && i.naturalWidth === 0).map((i) => i.currentSrc || i.src),
        sticky: (() => { const m = document.querySelector('.sr2-pdp-product__media'); return m ? getComputedStyle(m).position : null; })(),
      }));
      const file = `${dir}/${name}-${width}.png`;
      await page.screenshot({ path: file, fullPage: true });
      results.push({ route: query, width, status: resp.status(), ...info, errors, consoleErrors, failed, bad });
      console.log(width, name, resp.status(), `cards=${info.cards} framed=${info.framedCards} cols=${info.gridColumns} overflow=${info.overflow}`, `errors=${errors.length} console=${consoleErrors.length} failed=${failed.length} bad=${bad.length}`);
      await page.close();
    }
    await context.close();
  }

  // Journey at 1440: open quick view from a shop card; choose a variation, open size guide, and record buy-column tab order on the PDP.
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const journey = { errors: [] };
  const page = await context.newPage();
  page.on('pageerror', (e) => journey.errors.push(e.message));
  await page.goto(`${base}?route=shop`, { waitUntil: 'networkidle' });
  const trigger = page.locator('.sr2-c-editorial-card [data-quick-view]').first();
  await trigger.click();
  await page.waitForTimeout(700);
  journey.quickView = await page.evaluate(() => {
    const d = document.getElementById('sr2-quick-view-dialog');
    return { open: d?.open, name: d?.querySelector('[data-quick-view-name]')?.textContent.trim(), price: d?.querySelector('[data-quick-view-price]')?.textContent.trim(), availability: d?.querySelector('[data-quick-view-availability]')?.textContent.trim(), image: d?.querySelector('[data-quick-view-image]')?.getAttribute('src'), status: d?.querySelector('[data-quick-view-status]')?.textContent.trim(), activeElement: document.activeElement?.getAttribute('aria-label') || document.activeElement?.textContent.trim().slice(0, 40), openerExpanded: document.querySelector('.sr2-c-editorial-card [data-quick-view][aria-expanded="true"]') !== null };
  });
  await page.screenshot({ path: `${dir}/shop-quick-view-1440.png` });
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);
  journey.quickViewClosed = await page.evaluate(() => ({ open: document.getElementById('sr2-quick-view-dialog')?.open, focusReturned: document.activeElement?.hasAttribute('data-quick-view') }));

  await page.goto(`${base}?route=product&sku=br-004`, { waitUntil: 'networkidle' });
  await page.selectOption('#preview-size', 'M');
  journey.variation = await page.evaluate(() => ({ selected: document.querySelector('#preview-size')?.value }));
  // Tab through the buy column from the collection eyebrow onward.
  await page.evaluate(() => document.querySelector('#sr2-product-purchase')?.previousElementSibling?.querySelector('a, img')?.focus?.());
  const order = [];
  const summary = await page.$('#sr2-product-purchase');
  const first = await summary.$('a, button, input, select, [tabindex]:not([tabindex="-1"])');
  await first.focus();
  for (let i = 0; i < 9; i++) {
    order.push(await page.evaluate(() => { const a = document.activeElement; return `${a.tagName.toLowerCase()}${a.id ? '#' + a.id : ''}${a.className ? '.' + String(a.className).trim().split(/\s+/).slice(0, 2).join('.') : ''} "${(a.getAttribute('aria-label') || a.textContent || a.value || '').trim().slice(0, 32)}"`; }));
    await page.keyboard.press('Tab');
  }
  journey.buyColumnTabOrder = order;
  await page.locator('[data-size-guide-open]').click();
  await page.waitForTimeout(600);
  journey.sizeGuide = await page.evaluate(() => { const d = document.getElementById('sr2-size-guide-dialog'); return { open: d?.open, activeElement: document.activeElement?.getAttribute('aria-label') || document.activeElement?.textContent.trim().slice(0, 40), steps: d?.querySelectorAll('.sr2-size-guide-dialog__steps li').length }; });
  await page.screenshot({ path: `${dir}/product-br-004-size-guide-1440.png` });
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);
  journey.sizeGuideClosed = await page.evaluate(() => ({ open: document.getElementById('sr2-size-guide-dialog')?.open, focusReturned: document.activeElement?.hasAttribute('data-size-guide-open') }));
  // Mobile quick view too.
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(`${base}?route=shop`, { waitUntil: 'networkidle' });
  await page.locator('.sr2-c-editorial-card [data-quick-view]').first().click();
  await page.waitForTimeout(600);
  await page.screenshot({ path: `${dir}/shop-quick-view-390.png` });
  journey.quickViewMobileOpen = await page.evaluate(() => document.getElementById('sr2-quick-view-dialog')?.open);
  await page.close(); await context.close();
  fs.writeFileSync(`${dir}/browser-results.json`, JSON.stringify({ captured: new Date().toISOString(), results, journey }, null, 2));
  console.log(JSON.stringify(journey, null, 2));
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
