/** Official Woo 11.1 native DOM regression. Offline; no site, provider or image approval. */
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { execFileSync } = require('node:child_process');
const { createRequire } = require('node:module');
const { JSDOM } = createRequire(path.resolve(__dirname, '../../wordpress-theme/skyyrose-flagship-2/package.json'))('jsdom');
// Native sources remain external. Fetch the exact official URLs below into V2_NATIVE_JS_FIXTURE.
const nativeFiles = {
  'add-to-cart-variation.js': { sha: 'e901d7dd32a89f3bdbaefcd7589949c35176cc58b5b307be07bdbe579db7cdc9', source: 'https://raw.githubusercontent.com/woocommerce/woocommerce/11.1.0/plugins/woocommerce/client/legacy/js/frontend/add-to-cart-variation.js' },
  'jquery.js': { sha: '78a85aca2f0b110c29e0d2b137e09f0a1fb7a8e554b499f740d6744dc8962cfe', source: 'https://code.jquery.com/jquery-3.7.1.js' },
};
function nativeSource(file) {
  const directory = process.env.V2_NATIVE_JS_FIXTURE;
  assert.ok(directory, 'UNVERIFIED: V2_NATIVE_JS_FIXTURE must identify the external pinned native JS fixture');
  const bytes = fs.readFileSync(path.join(directory, file));
  assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), nativeFiles[file].sha, `Native dependency hash: ${file}`);
  return bytes.toString('utf8');
}
test('native Woo switches exact SKU, removes denied variation photo, permits size-only and resets safely', () => {
  const payload = JSON.parse(execFileSync('php', [path.join(__dirname, 'test-v2-product-media.php'), '--native-json'], { encoding: 'utf8' }));
  for (const initial of ['default', 'empty_default']) {
    const dom = new JSDOM(`<div class="product">${payload[initial]}<form class="variations_form" data-product_id="1"><template class="wc-product-gallery-default-template">${payload[initial]}</template><input name="quantity" value="2"><input name="variation_id" value="102"><button type="submit">Add to cart</button></form></div>`, { url: 'https://example.test/', runScripts: 'outside-only' });
    try {
      dom.window.eval(nativeSource('jquery.js'));
      dom.window.eval(nativeSource('add-to-cart-variation.js'));
      const $ = dom.window.jQuery;
      const $form = $('.variations_form');
      const urls = () => Array.from($('.product > .woocommerce-product-gallery img').map((i, image) => image.getAttribute('src')).get());
      const commerce = () => Array.from($form.find('input,button').map((i, element) => element.outerHTML).get());
      const before = commerce();
      const original = urls();
      $form.wc_variations_image_update(payload.payloads.distinct);
      assert.deepEqual(urls(), [payload.payloads.distinct.image.src], 'Distinct approved SKU replaces complete gallery');
      for (const denied of ['denied', 'unknown']) {
        $form.wc_variations_image_update(payload.payloads[denied]);
        assert.deepEqual(urls(), [], 'Denied selected variation cannot show previous or default parent');
        assert.equal($('.product > .woocommerce-product-gallery [role="status"]').length, 1);
        $form.wc_variations_image_update(payload.payloads.distinct);
      }
      $form.wc_variations_image_update(payload.payloads.size);
      assert.deepEqual(urls(), [payload.payloads.size.image.src], 'Explicit size-only variation uses approved parent SKU');
      $form.wc_variations_image_update(false);
      assert.deepEqual(urls(), original, 'Reset restores exact original approved or unavailable default');
      assert.deepEqual(commerce(), before, 'Image switches leave purchase fields untouched');
      assert.equal($('.product > .woocommerce-product-gallery').length, 1);
    } finally { dom.window.close(); }
  }
});
