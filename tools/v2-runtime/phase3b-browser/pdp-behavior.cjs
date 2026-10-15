const fs = require('fs'),
  path = require('path'),
  assert = require('assert/strict');
const { requireQa: q, base, out, validateSurface } = require('./runtime.cjs');
const { beginRun } = require('./run-evidence.cjs');
const evidence = { states: [], errors: [] };
const run = beginRun(path.join(out, 'pdp-behavior.json'));
(async () => {
  const { chromium } = q('playwright');
  const b = await chromium.launch();
  try {
    const c = await b.newContext({ viewport: { width: 390, height: 844 }, reducedMotion: 'reduce' });
    await c.route('**/*', r => (new URL(r.request().url()).origin === base ? r.continue() : r.abort()));
    const p = await c.newPage();
    p.on('pageerror', e => evidence.errors.push(e.message));
    await p.goto(base + '/shop/?product_cat=signature&max_price=30&orderby=price');
    const card = p
      .locator('.sr2-c-editorial-card')
      .filter({ has: p.locator('a[href$="/product/sg-005/"]') })
      .first();
    await Promise.all([p.waitForURL('**/product/sg-005/'), card.locator('a').first().click()]);
    await p.waitForFunction(() => document.querySelector('.single_add_to_cart_button')?.classList.contains('disabled'));
    assert.equal(await p.locator('select[name="attribute_size"]').inputValue(), '');
    await p.locator('.woocommerce-product-gallery__image > a').first().click();
    await p.locator('.pswp.pswp--open').waitFor();
    await p.keyboard.press('Escape');
    await p.locator('.pswp.pswp--open').waitFor({ state: 'hidden' });
    const guide = p.locator('[data-size-guide-open]');
    await guide.click();
    assert.equal(await p.locator('dialog[open]').count(), 1);
    await p.keyboard.press('Escape');
    assert(await guide.evaluate(e => e === document.activeElement));
    await p.getByRole('combobox', { name: 'Size', exact: true }).selectOption('M');
    await p.waitForFunction(
      () => !document.querySelector('.single_add_to_cart_button')?.classList.contains('disabled')
    );
    const variation = await p.locator('input.variation_id').inputValue();
    assert.equal(variation, '182');
    await p.waitForFunction(() => {
      const i = document.querySelector('.woocommerce-product-gallery__image img');
      return (
        i &&
        i.complete &&
        i.naturalWidth &&
        getComputedStyle(document.querySelector('.woocommerce-product-gallery')).opacity === '1'
      );
    });
    await p
      .locator('.woocommerce-product-gallery__image img')
      .first()
      .evaluate(i => i.decode());
    await p.screenshot({ path: path.join(out, 'pdp-selected-390.png') });
    await p.getByRole('button', { name: 'Add to cart', exact: true }).click();
    await p.waitForLoadState('load');
    await p.locator('[data-bag-open]').click();
    await p.locator('#sr2-bag-dialog .woocommerce-mini-cart-item').waitFor();
    assert.match(await p.locator('#sr2-bag-dialog').innerText(), /1 × \$25.00/);
    await p.getByRole('link', { name: 'View Bag', exact: true }).click();
    await p.waitForLoadState('load');
    assert.equal(await p.locator('input.qty').inputValue(), '1');
    assert.match(await p.locator('main').innerText(), /\$25.00/);
    await p.goto(base + '/checkout/');
    assert.match(await p.locator('#order_review').innerText(), /25.00/);
    evidence.journey = {
      start: 'Shop category/price/sort URL',
      sku: 'sg-005',
      size: 'M',
      variation,
      quantity: 1,
      unitPrice: 25,
      subtotal: 25,
      paymentSubmitted: false,
      galleryLightbox: true,
      fitFocusRestored: true,
    };
    for (const sku of ['sg-005', 'br-006', 'br-003', 'br-002']) {
      await p.goto(base + '/product/' + sku + '/');
      const state = await p.locator('.sr2-pdp-product').getAttribute('data-media-state');
      const imgs = await p.locator('.sr2-pdp-product__media img').count();
      if (sku === 'br-003') {
        assert.equal(state, 'rejected');
        assert.equal(imgs, 0);
        assert.equal(await p.locator('link[rel=preload][as=image]').count(), 0);
      } else assert(imgs > 0);
      await p.screenshot({ path: path.join(out, 'pdp-state-' + sku + '-390.png') });
      evidence.states.push({ sku, state, images: imgs });
    }
    await c.close();
    assert.equal(evidence.errors.length, 0);
    evidence.status = 'PASS';
  } catch (e) {
    evidence.status = 'FAIL';
    evidence.error = e.stack;
    throw e;
  } finally {
    await b.close();
  }
  run.pass(evidence);
})().catch(e => {
  run.fail(e, evidence);
  console.error(e);
  process.exitCode = 1;
});
