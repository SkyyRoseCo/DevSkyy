const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('./runtime.cjs').requireQa('playwright');
const source = fs.readFileSync(
  path.resolve(__dirname, '../../../wordpress-theme/skyyrose-flagship-2/assets/js/premium-commerce.js'),
  'utf8'
);
const fixture = `<button data-sr2-menu aria-expanded="false">Menu</button><div class="sr2-house-nav__collections"><div class="sr2-house-nav__previews">${['Black Rose', 'Love Hurts'].map((name, index) => `<div class="sr2-house-nav__preview-entry"><a href="/collection/${index}"><img src="/poster-${index}.svg"><span>${name}</span></a><button data-nav-preview-toggle aria-pressed="false" hidden>Preview ${name}</button></div>`).join('')}</div></div><article class="sr2-c-editorial-card"><img class="sr2-c-editorial-card__product-image" src="/broken.svg"><span data-card-image-error hidden>Product image unavailable</span></article>`;
async function run(action) {
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage();
    await page.route('http://premium.test/**', r => r.fulfill({ contentType: 'text/html', body: fixture }));
    await page.route('**/*.svg', r =>
      r.request().url().includes('broken')
        ? r.abort()
        : r.fulfill({
            contentType: 'image/svg+xml',
            body: '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="10"><rect width="20" height="10" fill="black"/></svg>',
          })
    );
    await page.goto('http://premium.test');
    await page.addScriptTag({ content: source });
    await action(page);
  } finally {
    await browser.close();
  }
}
test('poster previews follow menu, focus and explicit touch button without hijacking links', () =>
  run(async page => {
    await page.evaluate(() => document.querySelector('[data-sr2-menu]').setAttribute('aria-expanded', 'true'));
    await page.waitForFunction(() => document.querySelector('figcaption').textContent === 'Black Rose');
    await page.locator('.sr2-house-nav__preview-entry a').nth(1).focus();
    await page.waitForFunction(() => document.querySelector('figcaption').textContent === 'Love Hurts');
    await page.locator('[data-nav-preview-toggle]').first().click();
    await page.waitForFunction(() => document.querySelector('figcaption').textContent === 'Black Rose');
    assert.equal(await page.locator('[data-nav-preview-toggle]').first().getAttribute('aria-pressed'), 'true');
    await page.locator('.sr2-house-nav__preview-entry a').nth(1).click();
    assert.match(page.url(), /collection\/1$/);
  }));
test('image failure is honest, preview errors retain destinations and initialization is singular', () =>
  run(async page => {
    await page.waitForFunction(() => document.querySelector('article').dataset.imageState === 'error');
    assert.equal(await page.locator('[data-card-image-error]').isVisible(), true);
    await page.addScriptTag({ content: source });
    assert.equal(await page.locator('#sr2-nav-preview-stage').count(), 1);
    await page.route('**/poster-1.svg', r => r.abort());
    await page.evaluate(
      () => (document.querySelectorAll('.sr2-house-nav__preview-entry img')[1].src = '/poster-1.svg?failure=1')
    );
    await page.route('**/poster-1.svg?failure=1', r => r.abort());
    await page.locator('[data-nav-preview-toggle]').nth(1).click();
    await page.waitForFunction(() => document.querySelector('figure').dataset.state === 'error');
    assert.equal(await page.locator('figcaption').textContent(), 'Love Hurts');
    assert.equal(await page.locator('.sr2-house-nav__preview-entry a').nth(1).getAttribute('href'), '/collection/1');
  }));
test('native card request tracking isolates concurrent errors and clears only originating busy state', () =>
  run(async page => {
    const result = await page.evaluate(async code => {
      const handlers = {};
      window.jQuery = () => ({
        on(names, handler) {
          handlers[names] = handler;
          return this;
        },
      });
      document.documentElement.removeAttribute('data-sr2-premium-initialized');
      const script = document.createElement('script');
      script.textContent = code;
      document.head.append(script);
      // Exercise actual handlers with distinct native event records; no product/cart mutation is invented.
      const cards = [1, 2].map(id => {
        const c = document.createElement('article');
        c.className = 'sr2-c-editorial-card';
        c.innerHTML = `<button class="loading" aria-busy="true" data-product_id="${id}">Add</button><p data-card-cart-feedback data-added="Added" data-failed="Try the product" hidden></p>`;
        document.body.append(c);
        return c;
      });
      const buttons = cards.map(c => c.querySelector('button'));
      const first = {},
        second = {},
        unrelated = {};
      handlers['adding_to_cart.sr2Premium']({}, [buttons[0]], { product_id: 1 });
      handlers['adding_to_cart.sr2Premium']({}, [buttons[1]], { product_id: 2 });
      handlers['ajaxSend.sr2Premium']({}, first, { url: '/?wc-ajax=add_to_cart', data: 'product_id=1' });
      handlers['ajaxSend.sr2Premium']({}, second, { url: '/?wc-ajax=add_to_cart', data: 'product_id=2' });
      handlers['ajaxSend.sr2Premium']({}, unrelated, { url: '/?wc-ajax=unrelated', data: 'product_id=2' });
      handlers['ajaxError.sr2Premium']({}, unrelated);
      const unrelatedSafe = cards.every(c => c.dataset.cartState === 'loading');
      handlers['ajaxError.sr2Premium']({}, second);
      const exact =
        cards[0].dataset.cartState === 'loading' &&
        cards[1].dataset.cartState === 'error' &&
        buttons[0].classList.contains('loading') &&
        !buttons[1].classList.contains('loading') &&
        !buttons[1].hasAttribute('aria-busy');
      handlers['added_to_cart.sr2Premium']({}, {}, '', [buttons[0]]);
      return {
        unrelatedSafe,
        exact,
        success: cards[0].dataset.cartState === 'success',
        errorText: cards[1].querySelector('p').textContent,
      };
    }, source);
    assert.equal(result.unrelatedSafe, true);
    assert.equal(result.exact, true);
    assert.equal(result.success, true);
    assert.equal(result.errorText, 'Try the product');
  }));
