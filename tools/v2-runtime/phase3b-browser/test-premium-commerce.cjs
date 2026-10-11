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
const highlightFixture = `<style>.sr2-c-editorial-card { position:relative; } [data-card-image-error] { position:static; } .highlight-media { display:block; width:40vw; height:300px; border:2px solid; padding:12px; box-sizing:border-box; } .highlight-media img { width:100%; height:100%; padding:10px; border:1px solid; box-sizing:border-box; }</style><article id="highlight-card" class="sr2-c-editorial-card" data-garment-highlight="reviewed"><a class="sr2-c-editorial-card__media highlight-media" href="/product/jacket"><img class="sr2-c-editorial-card__product-image" src="/poster-0.svg"><svg class="sr2-c-editorial-card__garment-overlay" data-garment-overlay viewBox="0 0 20 10" preserveAspectRatio="none" aria-hidden="true" hidden><path class="sr2-c-editorial-card__garment-veil" fill-rule="evenodd" d="M0 0 L20 0 L20 10 L0 10 Z M5 2 L15 2 L15 8 L5 8 Z"/></svg></a><button data-garment-toggle class="sr2-c-editorial-card__highlight-toggle" aria-pressed="false" hidden>Highlight item</button><p data-garment-identity class="sr2-c-editorial-card__highlight-identity">Item highlighted: The Jacket</p></article>`;
const premiumCss = fs.readFileSync(
  path.resolve(__dirname, '../../../wordpress-theme/skyyrose-flagship-2/assets/css/premium-commerce.css'),
  'utf8'
);
async function run(action) {
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage();
    await page.route('http://premium.test/**', r =>
      r.fulfill({ contentType: 'text/html', body: fixture + highlightFixture })
    );
    await page.route('**/*.svg', r =>
      r.request().url().includes('broken')
        ? r.abort()
        : r.fulfill({
            contentType: 'image/svg+xml',
            body: '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="10"><rect width="20" height="10" fill="black"/></svg>',
          })
    );
    await page.goto('http://premium.test');
    await page.addStyleTag({ content: premiumCss });
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

test('reviewed garment tracks contain-fit content box, hover, focus and persistent touch toggle without replacing PDP links', () =>
  run(async page => {
    const card = page.locator('#highlight-card');
    await page.waitForFunction(() => document.querySelector('#highlight-card').dataset.garmentReady === 'true');
    const bounds = () =>
      page.evaluate(() => {
        const card = document.querySelector('#highlight-card');
        const image = card.querySelector('img').getBoundingClientRect();
        const overlay = card.querySelector('svg').getBoundingClientRect();
        return {
          width: overlay.width,
          height: overlay.height,
          imageWidth: image.width,
          centerX: overlay.x + overlay.width / 2 - image.x - image.width / 2,
          centerY: overlay.y + overlay.height / 2 - image.y - image.height / 2,
        };
      });
    let geometry = await bounds();
    assert.ok(Math.abs(geometry.width / geometry.height - 2) < 0.01, JSON.stringify(geometry));
    assert.ok(Math.abs(geometry.centerX) < 0.1 && Math.abs(geometry.centerY) < 0.1);
    assert.ok(geometry.width <= geometry.imageWidth - 22);
    const restingHeight = await card.evaluate(el => el.getBoundingClientRect().height);
    await card.locator('a').hover();
    await page.waitForFunction(() => getComputedStyle(document.querySelector('#highlight-card svg')).opacity === '1');
    assert.equal(await card.locator('[data-garment-identity]').isVisible(), true);
    assert.equal(await card.evaluate(el => el.getBoundingClientRect().height), restingHeight);
    await card.locator('a').focus();
    await page.mouse.move(0, 0);
    assert.equal(await card.locator('[data-garment-identity]').isVisible(), true);
    await card.locator('button').click();
    assert.equal(await card.locator('button').getAttribute('aria-pressed'), 'true');
    await page.evaluate(() => document.activeElement.blur());
    await page.mouse.move(0, 0);
    assert.equal(await card.getAttribute('data-garment-active'), 'true');
    await page.setViewportSize({ width: 390, height: 844 });
    await page.waitForFunction(() => document.querySelector('#highlight-card svg').getBoundingClientRect().width < 200);
    geometry = await bounds();
    assert.ok(Math.abs(geometry.width / geometry.height - 2) < 0.01, JSON.stringify(geometry));
    assert.ok(Math.abs(geometry.centerX) < 0.1 && Math.abs(geometry.centerY) < 0.1);
    await card.locator('button').click();
    assert.equal(await card.locator('button').getAttribute('aria-pressed'), 'false');
    assert.equal(await card.getAttribute('data-garment-active'), null);
    await card.locator('a').click();
    assert.match(page.url(), /product\/jacket$/);
  }));
test('broken highlighted image resets persistence and hides the control; reduced motion and forced colors retain clear textual identity', () =>
  run(async page => {
    const card = page.locator('#highlight-card');
    await page.waitForFunction(() => document.querySelector('#highlight-card').dataset.garmentReady === 'true');
    await card.locator('button').click();
    await page.emulateMedia({ reducedMotion: 'reduce' });
    assert.equal(await card.locator('svg').evaluate(el => getComputedStyle(el).transitionDuration), '0s');
    await page.emulateMedia({ forcedColors: 'active' });
    assert.equal(await card.locator('svg').isVisible(), false);
    assert.equal(await card.locator('[data-garment-identity]').isVisible(), true);
    await card.locator('img').evaluate(el => {
      el.src = '/broken.svg';
    });
    await page.waitForFunction(() => document.querySelector('#highlight-card').dataset.imageState === 'error');
    assert.equal(await card.locator('button').isVisible(), false);
    assert.equal(await card.locator('button').isDisabled(), true);
    assert.equal(await card.locator('button').getAttribute('aria-pressed'), 'false');
    assert.equal(await card.getAttribute('data-garment-active'), null);
    assert.equal(await card.getAttribute('data-garment-ready'), null);
    assert.equal(await card.locator('a').getAttribute('href'), '/product/jacket');
  }));

test('touch off releases retained focus while keyboard focus keeps the reviewed garment identifiable', () =>
  run(async page => {
    const card = page.locator('#highlight-card');
    await page.waitForFunction(() => document.querySelector('#highlight-card').dataset.garmentReady === 'true');
    await card.locator('button').evaluate(el => {
      el.dispatchEvent(new PointerEvent('pointerdown', { pointerType: 'touch' }));
      el.focus();
      el.click();
    });
    assert.equal(await card.locator('button').getAttribute('aria-pressed'), 'true');
    await card.locator('button').evaluate(el => {
      el.dispatchEvent(new PointerEvent('pointerdown', { pointerType: 'touch' }));
      el.focus();
      el.click();
    });
    assert.equal(await card.locator('button').getAttribute('aria-pressed'), 'false');
    assert.equal(await card.locator('button').evaluate(el => document.activeElement === el), false);
    assert.equal(await card.getAttribute('data-garment-active'), null);
    await card.locator('button').focus();
    assert.equal(await card.locator('[data-garment-identity]').isVisible(), true);
    await page.keyboard.press('Enter');
    assert.equal(await card.locator('button').getAttribute('aria-pressed'), 'true');
    assert.equal(await card.locator('button').evaluate(el => document.activeElement === el), true);
  }));

test('actual PHP card union leaves overlapping garment pixels clear and veils only outside regions and per-polygon holes', () =>
  run(async page => {
    const { execFileSync } = require('node:child_process');
    const markup = execFileSync('php', [path.resolve(__dirname, '../test-card-garment-highlight.php')], {
      env: { ...process.env, V2_GARMENT_RENDER_FIXTURE: '1' },
      encoding: 'utf8',
    });
    const pixels = await page.evaluate(async markup => {
      const host = document.createElement('div');
      host.innerHTML = markup;
      const svg = host.querySelector('svg');
      svg.removeAttribute('hidden');
      svg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
      svg.setAttribute('width', '1024');
      svg.setAttribute('height', '1536');
      svg.querySelector('.sr2-c-editorial-card__garment-veil').setAttribute('fill', 'rgba(0,0,0,0.56)');
      svg.querySelectorAll('.sr2-c-editorial-card__garment-contour').forEach(el => el.remove());
      const image = new Image();
      image.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(new XMLSerializer().serializeToString(svg));
      await image.decode();
      const canvas = document.createElement('canvas');
      canvas.width = 1024;
      canvas.height = 1536;
      const context = canvas.getContext('2d');
      context.fillStyle = 'white';
      context.fillRect(0, 0, 1024, 1536);
      context.drawImage(image, 0, 0);
      const pixel = (x, y) => Array.from(context.getImageData(x, y, 1, 1).data);
      return {
        outer: pixel(150, 150),
        overlap: pixel(850, 250),
        secondOnly: pixel(950, 250),
        hole: pixel(400, 400),
        outside: pixel(20, 20),
        viewBox: svg.getAttribute('viewBox'),
      };
    }, markup);
    assert.deepEqual(pixels.outer, [255, 255, 255, 255]);
    assert.deepEqual(pixels.overlap, [255, 255, 255, 255]);
    assert.deepEqual(pixels.secondOnly, [255, 255, 255, 255]);
    assert.ok(pixels.hole[0] >= 110 && pixels.hole[0] <= 114);
    assert.deepEqual(pixels.hole, pixels.outside);
    assert.equal(pixels.viewBox, '0 0 1024 1536');
  }));

test('canceled touch followed by keyboard off keeps focus and clears stale pointer provenance', () =>
  run(async page => {
    const card = page.locator('#highlight-card');
    await page.waitForFunction(() => document.querySelector('#highlight-card').dataset.garmentReady === 'true');
    const toggle = card.locator('button');
    await toggle.focus();
    await page.keyboard.press('Enter');
    assert.equal(await toggle.getAttribute('aria-pressed'), 'true');
    await toggle.evaluate(el => {
      el.dispatchEvent(new PointerEvent('pointerdown', { pointerType: 'touch' }));
      el.dispatchEvent(new PointerEvent('pointercancel', { pointerType: 'touch' }));
    });
    await page.keyboard.press('Enter');
    assert.equal(await toggle.getAttribute('aria-pressed'), 'false');
    assert.equal(await card.getAttribute('data-garment-active'), null);
    assert.equal(await toggle.evaluate(el => document.activeElement === el), true);
    assert.equal(await card.locator('[data-garment-identity]').isVisible(), true);
    // Keyboard provenance must also win when a touch pointerdown was superseded
    // without a pointercancel reaching this control.
    await page.keyboard.press('Enter');
    await toggle.evaluate(el => el.dispatchEvent(new PointerEvent('pointerdown', { pointerType: 'touch' })));
    await page.keyboard.press('Space');
    assert.equal(await toggle.getAttribute('aria-pressed'), 'false');
    assert.equal(await toggle.evaluate(el => document.activeElement === el), true);
  }));
