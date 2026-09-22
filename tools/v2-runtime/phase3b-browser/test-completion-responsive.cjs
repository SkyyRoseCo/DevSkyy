/** Full-width route reflow and accessible-page evidence for the V2 completion candidate. */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { requireQa: q, base, out } = require('./runtime.cjs');
const { beginRun } = require('./run-evidence.cjs');
const engineName = process.env.V2_BROWSER || 'chromium';
assert(['chromium', 'webkit', 'firefox'].includes(engineName));
const target = path.join(out, `completion-responsive-${engineName}.json`);
const run = beginRun(target);
const evidence = {
  rows: [],
  failures: [],
  scope: 'Local synthetic fixture; no account, mail, checkout submission or orders',
};
const routes = {
  home: '/',
  signature: '/collections/signature/',
  'black-rose': '/collections/black-rose/',
  'love-hurts': '/collections/love-hurts/',
  kids: '/collections/kids-capsule/',
  pdp: '/product/sg-005/',
  shop: '/shop/',
  search: '/?s=SG-005',
  'empty-search': '/?s=zzunmatchedjourneyprobe',
  collections: '/collections/',
  about: '/about/',
  contact: '/contact/',
  preorder: '/pre-order/',
  service: '/shipping-returns/',
  cart: '/cart/',
  account: '/my-account/',
  missing: '/sr2-deliberately-missing-route/',
};
(async () => {
  const browser = await q('playwright')[engineName].launch();
  evidence.engine = engineName;
  const widths = engineName !== 'chromium' ? [390, 1440] : [320, 360, 375, 390, 414, 768, 1024, 1440];
  try {
    for (const width of widths) {
      const context = await browser.newContext({
        viewport: { width, height: width < 768 ? 844 : 1000 },
        reducedMotion: 'reduce',
        hasTouch: width < 768,
      });
      await context.route('**/*', route =>
        new URL(route.request().url()).origin === base ? route.continue() : route.abort()
      );
      const page = await context.newPage();
      let errors = [],
        httpErrors = [];
      page.on('pageerror', error => errors.push(error.message));
      page.on('response', response => {
        if (response.status() >= 400 && response.request().resourceType() !== 'document')
          httpErrors.push({ url: response.url(), status: response.status() });
      });
      for (const [name, route] of Object.entries(routes)) {
        errors = [];
        httpErrors = [];
        const response = await page.goto(base + route);
        await page.evaluate(() => document.fonts.ready);
        const state = await page.evaluate(() => ({
          width: innerWidth,
          scrollWidth: document.documentElement.scrollWidth,
          h1: [...document.querySelectorAll('main h1')].map(el => ({
            text: el.textContent.trim(),
            top: el.getBoundingClientRect().top,
            bottom: el.getBoundingClientRect().bottom,
          })),
          main: !!document.querySelector('main'),
          errorText: /Fatal error|Uncaught (?:Error|Exception)|Warning: (?:Undefined|require|include)/.test(
            document.body.innerText
          ),
          missingImages: [...document.querySelectorAll('main img')]
            .filter(img => img.complete && img.currentSrc && !img.naturalWidth)
            .map(img => img.currentSrc),
        }));
        let violations = [];
        if ([390, 1440].includes(width)) {
          const result = await new (q('@axe-core/playwright').default)({ page })
            .withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'])
            .analyze();
          violations = result.violations.map(v => ({
            id: v.id,
            impact: v.impact,
            nodes: v.nodes.map(n => ({ target: n.target, summary: n.failureSummary })),
          }));
        }
        const screenshot = `completion-${engineName}-${name}-${width}.png`;
        await page.screenshot({ path: path.join(out, screenshot), animations: 'disabled' });
        const row = {
          name,
          width,
          url: page.url(),
          status: response.status(),
          state,
          errors: [...errors],
          httpErrors: [...httpErrors],
          violations,
          screenshot,
        };
        const expectedStatus = name === 'missing' ? 404 : 200;
        if (
          row.status !== expectedStatus ||
          !state.main ||
          state.h1.length !== 1 ||
          state.scrollWidth > width ||
          state.errorText ||
          state.missingImages.length ||
          row.errors.length ||
          row.httpErrors.length ||
          violations.length
        )
          evidence.failures.push(row);
        evidence.rows.push(row);
        fs.writeFileSync(path.join(out, `completion-${engineName}-progress.json`), JSON.stringify(evidence, null, 2));
        console.log(name, width, evidence.failures.includes(row) ? 'FAIL' : 'ok');
      }
      await context.close();
    }
    assert.equal(evidence.rows.length, widths.length * Object.keys(routes).length);
    assert.equal(evidence.failures.length, 0, 'Route defects recorded in evidence');
    run.pass(evidence);
  } finally {
    await browser.close();
  }
})().catch(error => {
  run.fail(error, evidence);
  console.error(error);
  process.exitCode = 1;
});
