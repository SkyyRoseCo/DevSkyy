/** Current mobile composition and keyboard evidence; human review owns visual verdicts. */
const fs = require('node:fs'),
  path = require('node:path'),
  assert = require('node:assert/strict');
const { requireQa, base, out } = require('./runtime.cjs');
const rows = [];
(async () => {
  const browser = await requireQa('playwright').chromium.launch();
  try {
    for (const width of [320, 390, 414, 768]) {
      const context = await browser.newContext({
        viewport: { width, height: 900 },
        reducedMotion: 'reduce',
        hasTouch: true,
      });
      await context.route('**/*', r => (new URL(r.request().url()).origin === base ? r.continue() : r.abort()));
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', e => errors.push(e.message));
      const capture = async name => {
        await page.evaluate(() => document.fonts.ready);
        await page.evaluate(() =>
          Promise.all(
            [...document.images]
              .filter(
                i => i.currentSrc && i.getBoundingClientRect().top < innerHeight && i.getBoundingClientRect().bottom > 0
              )
              .map(i => i.decode().catch(() => {}))
          )
        );
        await page.screenshot({ path: path.join(out, `${name}-${width}.png`), animations: 'disabled' });
        const state = await page.evaluate(() => ({
          width: innerWidth,
          scrollWidth: document.documentElement.scrollWidth,
          headings: [...document.querySelectorAll('main h1,main h2,main h3')].map(e => ({
            tag: e.tagName,
            text: e.textContent.trim(),
          })),
          focus: document.activeElement?.outerHTML.slice(0, 300),
        }));
        assert(state.scrollWidth <= width);
        rows.push({ name, width, state, errors: [...errors] });
      };
      for (const collection of ['signature', 'black-rose', 'love-hurts']) {
        await page.goto(`${base}/collections/${collection}/`);
        for (const scene of await page.locator('[data-scene-id]').all()) {
          const id = await scene.getAttribute('data-scene-id');
          await scene.evaluate(el => {
            const rail = el.closest('[data-recovery-track]');
            rail.scrollBy({
              left: el.getBoundingClientRect().left - rail.getBoundingClientRect().left,
              behavior: 'instant',
            });
            window.scrollBy({ top: el.getBoundingClientRect().top - 108, behavior: 'instant' });
          });
          await scene
            .locator('img[src]')
            .first()
            .evaluate(i => i.decode());
          await capture(id);
        }
        await page.locator('#shop').scrollIntoViewIfNeeded();
        await capture(collection + '-handoff');
      }
      await page.goto(base + '/shop/');
      await capture('shop');
      const opener = page.locator('[data-quick-view]').first();
      await opener.focus();
      await page.keyboard.press('Enter');
      const qv = page.locator('#sr2-quick-view-dialog');
      await qv.locator('form.cart').waitFor();
      await capture('quick-view');
      for (let i = 0; i < 16; i++) {
        await page.keyboard.press('Tab');
        assert(await qv.evaluate(d => d.contains(document.activeElement)));
      }
      await page.keyboard.press('Escape');
      assert(await opener.evaluate(e => e === document.activeElement));
      if (!(await page.locator('[data-search-open]').first().isVisible()))
        await page.locator('[data-sr2-menu]').click();
      const search = page.locator('[data-search-open]:visible').first();
      await search.focus();
      await page.keyboard.press('Enter');
      await page.locator('[data-search-input]').fill('SG-005');
      await page.locator('[data-search-preview-results] a').first().waitFor();
      await capture('search');
      for (let i = 0; i < 12; i++) {
        await page.keyboard.press('Tab');
        assert(await page.locator('#sr2-search-dialog').evaluate(d => d.contains(document.activeElement)));
      }
      await page.locator('[data-search-input]').fill('zzunmatchedjourneyprobe');
      await page.waitForFunction(
        () =>
          document.querySelector('[data-search-preview] [role=status]').textContent ===
          document.querySelector('[data-search-preview]').dataset.empty
      );
      await capture('search-empty');
      await page.keyboard.press('Escape');
      await page.goto(base + '/product/sg-005/');
      await capture('pdp');
      await page.locator('select[name="attribute_size"]').selectOption('M');
      await page.locator('.woocommerce-variation-add-to-cart-enabled').waitFor();
      await Promise.all([page.waitForNavigation(), page.locator('button.single_add_to_cart_button').click()]);
      if (!(await page.locator('[data-bag-open]').first().isVisible())) await page.locator('[data-sr2-menu]').click();
      const bag = page.locator('[data-bag-open]:visible').first();
      await bag.focus();
      await page.keyboard.press('Enter');
      await page.locator('#sr2-bag-dialog[open]').waitFor();
      await capture('bag');
      for (let i = 0; i < 12; i++) {
        await page.keyboard.press('Tab');
        assert(await page.locator('#sr2-bag-dialog').evaluate(d => d.contains(document.activeElement)));
      }
      await page.keyboard.press('Escape');
      assert(await bag.evaluate(e => e === document.activeElement));
      assert.equal(errors.length, 0);
      await context.close();
    }
    fs.writeFileSync(
      path.join(out, 'mobile-art.json'),
      JSON.stringify(
        {
          status: 'PASS',
          scope:
            'Reduced motion; emulated touch and keyboard. No browser UI zoom, screen reader, payment or physical phone certification.',
          rows,
        },
        null,
        2
      )
    );
  } finally {
    await browser.close();
  }
})().catch(e => {
  fs.writeFileSync(path.join(out, 'mobile-art-failure.json'), JSON.stringify({ error: e.stack, rows }, null, 2));
  console.error(e);
  process.exitCode = 1;
});
