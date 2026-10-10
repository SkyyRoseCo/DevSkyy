const fs = require('node:fs/promises'),
  path = require('node:path'),
  assert = require('node:assert/strict');
const { requireQa: q, base, out, validateSurface } = require('./runtime.cjs');
const [label, route] = process.argv.slice(2);
validateSurface(label, route);

const { beginRun } = require('./run-evidence.cjs');
const run = beginRun(path.join(out, label + '-responsive.json'));
(async () => {
  const { default: AxeBuilder } = q('@axe-core/playwright');
  const { chromium } = q('playwright');
  const b = await chromium.launch();
  const rows = [];
  try {
    for (const width of [320, 360, 375, 390, 414, 768, 1024, 1280, 1440, 1728]) {
      const c = await b.newContext({ viewport: { width, height: width < 768 ? 844 : 1000 }, reducedMotion: 'reduce' });
      await c.route('**/*', r => (new URL(r.request().url()).origin === base ? r.continue() : r.abort()));
      const p = await c.newPage();
      const errors = [];
      p.on('pageerror', e => errors.push(e.message));
      const res = await p.goto(base + route);
      assert.equal(res.status(), 200);
      await p.evaluate(() => document.fonts.ready);
      await p.waitForFunction(() =>
        [...document.images]
          .filter(e => {
            const r = e.getBoundingClientRect();
            return r.width && r.height && r.top < innerHeight && r.bottom > 0;
          })
          .every(e => e.complete && e.naturalWidth)
      );
      const gallery = p.locator('.woocommerce-product-gallery');
      if (await gallery.count())
        await p.waitForFunction(
          () => getComputedStyle(document.querySelector('.woocommerce-product-gallery')).opacity === '1'
        );
      if (await p.locator('form.variations_form').count())
        await p.waitForFunction(() => {
          return document
            .querySelector('form.variations_form .single_add_to_cart_button')
            ?.classList.contains('wc-variation-selection-needed');
        });
      await p.screenshot({ path: path.join(out, `${label}-${width}.png`), animations: 'disabled' });
      if ([390, 1440].includes(width)) {
        await p.evaluate(async () => {
          for (let y = 0; y < document.documentElement.scrollHeight; y += 700) {
            scrollTo(0, y);
            await new Promise(r => setTimeout(r, 50));
          }
          scrollTo(0, 0);
          await Promise.all([...document.images].filter(i => i.currentSrc).map(i => i.decode().catch(() => {})));
        });
        await p.screenshot({
          path: path.join(out, `${label}-full-${width}.png`),
          fullPage: true,
          animations: 'disabled',
        });
      }
      const metrics = await p.evaluate(() => ({
        width: innerWidth,
        scrollWidth: document.documentElement.scrollWidth,
        h1: [...document.querySelectorAll('main h1')].map(e => e.textContent.trim()),
        cards: [...document.querySelectorAll('.sr2-c-editorial-card')].slice(0, 4).map(e => {
          const r = e.getBoundingClientRect();
          return { x: r.x, y: r.y, w: r.width, h: r.height, text: e.innerText };
        }),
        images: [...document.querySelectorAll('main img')].map(e => ({
          src: e.currentSrc,
          sizes: e.sizes,
          loading: e.loading,
          priority: e.fetchPriority,
          width: e.width,
          natural: e.naturalWidth,
        })),
      }));
      const axe = [390, 768, 1440].includes(width)
        ? await new AxeBuilder({ page: p })
            .include('main')
            .withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'])
            .analyze()
        : null;
      rows.push({
        ...metrics,
        errors,
        axe: axe?.violations.map(v => ({
          id: v.id,
          impact: v.impact,
          nodes: v.nodes.map(n => ({ target: n.target, summary: n.failureSummary })),
        })),
      });
      await c.close();
    }
    console.log(
      JSON.stringify(
        rows.map(r => ({ width: r.width, overflow: r.scrollWidth - r.width, axe: r.axe?.length, errors: r.errors }))
      )
    );
  } finally {
    await b.close();
  }
  run.pass(rows);
})().catch(e => {
  run.fail(e);
  console.error(e);
  process.exitCode = 1;
});
