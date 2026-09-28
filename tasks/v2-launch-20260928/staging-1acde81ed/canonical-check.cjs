/** Canonical public URL check: no candidate query strings or cache bypass. */
const { chromium } = require('../../../node_modules/playwright');
const fs = require('node:fs/promises');
const path = require('node:path');
const base = 'https://staging-7e48-skyyrose.wpcomstaging.com';
const out = path.join(__dirname, 'artifacts');
const routes = [
  { name: 'homepage', path: '/', hero: '.sr2-house-arrival__art img', media: '.sr2-house-arrival__art' },
  {
    name: 'preorder',
    path: '/pre-order/',
    hero: '.sr2-reserve-arrival .sr2-arrival__media img',
    media: '.sr2-reserve-arrival .sr2-arrival__media',
  },
  { name: 'br004', path: '/product/br-004/' },
];
const cacheFields = [
  'cache-control',
  'age',
  'x-ac',
  'x-cache',
  'cf-cache-status',
  'last-modified',
  'etag',
  'vary',
  'server',
];
(async () => {
  await fs.mkdir(out, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const results = [];
  try {
    for (const viewport of [
      { name: 'desktop', width: 1440, height: 900 },
      { name: 'mobile', width: 390, height: 844 },
    ]) {
      const context = await browser.newContext({
        viewport: { width: viewport.width, height: viewport.height },
        reducedMotion: 'reduce',
      });
      const page = await context.newPage();
      for (const route of routes) {
        const item = { candidate: '1acde81ed', viewport: viewport.name, path: route.path, pageErrors: [] };
        page.on('pageerror', error => item.pageErrors.push(error.message));
        try {
          const response = await page.goto(base + route.path, { waitUntil: 'load', timeout: 45000 });
          item.http = response.status();
          item.url = page.url();
          item.headers = Object.fromEntries(cacheFields.map(field => [field, response.headers()[field] ?? null]));
          item.mascotNodes = await page
            .locator('#skyyrose-mascot, #skyyrose-mascot-recall, #skyy-ask-dialog, #skyy-hero-stage')
            .count();
          item.title = await page.title();
          if (route.hero) {
            const image = page.locator(route.hero);
            item.heroPresent = (await image.count()) === 1;
            if (item.heroPresent) {
              await image.evaluate(element => element.decode());
              item.heroSrc = await image.evaluate(element => element.currentSrc);
              item.heroWidth = await image.evaluate(element => element.naturalWidth);
              item.geometry = await page.evaluate(media => {
                const header = document.querySelector('[data-site-header]');
                const art = document.querySelector(media);
                const image = art?.querySelector('img');
                return {
                  headerBottom: header?.getBoundingClientRect().bottom ?? null,
                  mediaTop: art?.getBoundingClientRect().top ?? null,
                  mediaBottom: art?.getBoundingClientRect().bottom ?? null,
                  imageHeight: image?.getBoundingClientRect().height ?? null,
                  objectFit: image && getComputedStyle(image).objectFit,
                  objectPosition: image && getComputedStyle(image).objectPosition,
                };
              }, route.media);
              await page.screenshot({
                path: path.join(out, 'canonical-' + viewport.name + '-' + route.name + '.png'),
                animations: 'disabled',
              });
            }
          }
          item.status =
            item.http === 200 &&
            item.mascotNodes === 0 &&
            (!route.hero ||
              (item.heroPresent &&
                item.heroSrc.includes('house-monument-20260928.webp') &&
                (viewport.name !== 'mobile' || item.geometry.mediaTop >= item.geometry.headerBottom - 1)))
              ? 'PASS'
              : 'FAIL';
        } catch (error) {
          item.status = 'FAIL';
          item.failure = String(error.stack || error).slice(0, 3000);
        }
        results.push(item);
      }
      await context.close();
    }
  } finally {
    await browser.close();
  }
  await fs.writeFile(path.join(out, 'canonical-results.json'), JSON.stringify(results, null, 2));
  results.forEach(item => console.log(JSON.stringify(item)));
  if (results.some(item => item.status !== 'PASS')) process.exitCode = 1;
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
