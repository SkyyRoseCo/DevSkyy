const fs = require('fs'),
  path = require('path'),
  assert = require('assert/strict');
const { requireQa: q, base, out, validateSurface } = require('./runtime.cjs');
const { beginRun } = require('./run-evidence.cjs');
const receipt = { states: [], errors: [] };
const run = beginRun(path.join(out, 'gallery-delivery.json'));
(async () => {
  const { chromium } = q('playwright');
  const b = await chromium.launch();
  try {
    for (const [sku, id, rejected] of [
      ['sg-005', 179, false],
      ['br-003', null, true],
    ]) {
      const c = await b.newContext({ viewport: { width: 390, height: 844 }, reducedMotion: 'reduce' });
      await c.route('**/*', r => (new URL(r.request().url()).origin === base ? r.continue() : r.abort()));
      const p = await c.newPage();
      const requests = [];
      p.on('request', r => {
        if (r.resourceType() === 'image') requests.push(r.url());
      });
      p.on('pageerror', e => receipt.errors.push(e.message));
      await p.goto(base + '/product/' + sku + '/');
      await p.waitForFunction(() =>
        document
          .querySelector('form.variations_form .single_add_to_cart_button')
          ?.classList.contains('wc-variation-selection-needed')
      );
      const initial = await p.evaluate(() => {
        const f = document.querySelector('form.variations_form'),
          t = f.querySelector('template.wc-product-gallery-default-template');
        return {
          productId: f.dataset.product_id,
          template: t?.innerHTML || '',
          cache: window.wc_variation_gallery_defaults?.[f.dataset.product_id] || '',
          variations: JSON.parse(f.dataset.product_variations),
          gallery: [...document.querySelectorAll('.sr2-pdp-product__media img')].map(i => ({
            src: i.currentSrc,
            full: i.dataset.large_image,
          })),
        };
      });
      if (rejected) {
        assert.equal(initial.gallery.length, 0);
        for (const html of [
          initial.template,
          initial.cache,
          ...initial.variations.map(v => v.gallery_images_html || ''),
        ])
          assert(!/<img\b/i.test(html), 'Rejected image embedded in reset/variation template');
      } else {
        for (const html of [initial.template, initial.cache]) {
          assert.match(html, /derived\/card-fronts\/sg-005-/);
          assert.match(html, /data-large_image=.*uploads/);
        }
        assert.equal(initial.gallery.length, 1);
        assert.match(initial.gallery[0].src, /derived\/card-fronts\/sg-005-/);
      }
      const selected = [];
      for (const action of ['M', '', 'M']) {
        await p.getByRole('combobox', { name: 'Size', exact: true }).selectOption(action);
        if (action) {
          await p.waitForFunction(
            () => !document.querySelector('.single_add_to_cart_button').classList.contains('disabled')
          );
        } else {
          await p.waitForFunction(() =>
            document.querySelector('.single_add_to_cart_button').classList.contains('disabled')
          );
        }
        if (!rejected) {
          await p.waitForFunction(() => {
            const i = document.querySelector('.sr2-pdp-product__media .wp-post-image');
            return i?.complete && i.naturalWidth > 0;
          });
          await p.locator('.sr2-pdp-product__media .wp-post-image').evaluate(i => i.decode());
          const image = await p.locator('.sr2-pdp-product__media .wp-post-image').evaluate(i => ({
            src: i.currentSrc,
            full: i.dataset.large_image,
            box: i.getBoundingClientRect().toJSON(),
          }));
          assert.match(image.src, /derived\/card-fronts\/sg-005-/);
          assert(image.box.width > 100 && image.box.height > 200);
          selected.push({ action, image, variation: await p.locator('input.variation_id').inputValue() });
        } else {
          assert.equal(await p.locator('.sr2-pdp-product__media img').count(), 0);
        }
      }
      if (!rejected) {
        await p.screenshot({ path: path.join(out, 'pdp-delivery-selected-390.png') });
        await p.locator('.woocommerce-product-gallery__image > a').first().click();
        await p.locator('.pswp--open').waitFor();
        await p.keyboard.press('Escape');
        await p.locator('.pswp--open').waitFor({ state: 'hidden' });
      } else assert(!requests.some(u => /uploads.*br-003/.test(u)), 'Rejected attachment requested');
      const ajax = await c.request.post(base + '/?wc-ajax=get_variation', {
        maxRedirects: 0,
        form: { product_id: initial.productId, attribute_size: 'M' },
      });
      assert.equal(new URL(ajax.url()).origin, base, 'Variation response must stay on the exact local origin.');
      assert.equal(ajax.status(), 200);
      const variation = await ajax.json();
      assert(variation.variation_id);
      if (rejected) {
        assert.equal(variation.image_id, 0);
        assert.equal(variation.gallery_images_html, '');
      } else {
        assert.match(variation.image.src, /derived\/card-fronts\/sg-005-/);
        if (variation.gallery_images_html) assert.match(variation.gallery_images_html, /derived\/card-fronts\/sg-005-/);
      }
      receipt.states.push({
        sku,
        productId: initial.productId,
        rejected,
        selected,
        defaultTemplatePermitted: true,
        inlineDefaultPermitted: true,
        ajaxVariation: variation.variation_id,
        ajaxImage: variation.image?.src || null,
        initialImage: initial.gallery[0] || null,
        requests,
      });
      await c.close();
    }
    assert.equal(receipt.errors.length, 0);
    receipt.status = 'PASS';
  } catch (e) {
    receipt.status = 'FAIL';
    receipt.error = e.stack;
    throw e;
  } finally {
    await b.close();
  }
  run.pass(receipt);
})().catch(e => {
  run.fail(e, receipt);
  console.error(e);
  process.exitCode = 1;
});
