/** Browser acceptance for the deployed 1acde81ed candidate. Never submits checkout. */
const { chromium } = require('../../../node_modules/playwright');
const { createHash } = require('node:crypto');
const fs = require('node:fs/promises');
const path = require('node:path');

const base = 'https://staging-7e48-skyyrose.wpcomstaging.com';
const out = path.join(__dirname, 'artifacts');
const monument = path.resolve(
  __dirname,
  '../../../wordpress-theme/skyyrose-flagship-2/assets/images/house-monument-20260928.webp'
);
const cssFiles = ['home-art-direction.min.css', 'content-page.min.css'];
const viewports = [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'mobile', width: 390, height: 844 },
];

const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const visibleBroken = page =>
  page.locator('img').evaluateAll(images =>
    images
      .filter(image => {
        const rect = image.getBoundingClientRect();
        return (
          rect.width > 0 &&
          rect.height > 0 &&
          rect.bottom > 0 &&
          rect.top < innerHeight &&
          image.complete &&
          image.naturalWidth === 0
        );
      })
      .map(image => image.currentSrc || image.src)
  );
const overflow = page =>
  page.evaluate(() => ({
    viewport: innerWidth,
    scrollWidth: document.documentElement.scrollWidth,
    overflowPx: Math.max(0, document.documentElement.scrollWidth - innerWidth),
  }));
const mascot = page =>
  page.locator('#skyyrose-mascot, #skyyrose-mascot-recall, #skyy-ask-dialog, #skyy-hero-stage').count();
const capture = (page, name) =>
  page.screenshot({ path: path.join(out, name + '.png'), fullPage: true, animations: 'disabled' });

(async () => {
  await fs.mkdir(out, { recursive: true });
  const localHash = sha(await fs.readFile(monument));
  const localCssHashes = Object.fromEntries(
    await Promise.all(
      cssFiles.map(async file => [
        file,
        sha(
          await fs.readFile(path.resolve(__dirname, '../../../wordpress-theme/skyyrose-flagship-2/assets/css', file))
        ),
      ])
    )
  );
  const browser = await chromium.launch({ headless: true });
  const results = [];
  try {
    for (const viewport of viewports) {
      const fresh = route =>
        base + route + (route.includes('?') ? '&' : '?') + 'v2accept=1acde81ed-' + viewport.name + '-' + Date.now();
      const context = await browser.newContext({
        viewport: { width: viewport.width, height: viewport.height },
        reducedMotion: 'reduce',
      });
      const page = await context.newPage();
      const result = {
        candidate: '1acde81ed',
        viewport,
        localMonumentSha256: localHash,
        css: {},
        responses: {},
        pageErrors: [],
        requestFailures: [],
        brokenImages: {},
        overflow: {},
        mascotCount: {},
        homepage: {},
        preorder: {},
        product: {},
        cart: {},
        checkout: {},
      };
      page.on('pageerror', error => result.pageErrors.push(error.message));
      page.on('requestfailed', request => {
        if (request.url().startsWith(base))
          result.requestFailures.push(request.url().slice(base.length) + ': ' + request.failure()?.errorText);
      });
      try {
        for (const file of cssFiles) {
          const cssResponse = await context.request.get(
            base + '/wp-content/themes/skyyrose-flagship-2/assets/css/' + file + '?v2accept=1acde81ed-' + Date.now(),
            { timeout: 30000 }
          );
          result.css[file] = {
            http: cssResponse.status(),
            localSha256: localCssHashes[file],
            servedSha256: sha(await cssResponse.body()),
          };
          result.css[file].byteMatch = result.css[file].localSha256 === result.css[file].servedSha256;
        }
        let response = await page.goto(fresh('/'), { waitUntil: 'load', timeout: 45000 });
        result.responses.homepage = response.status();
        const hero = page.locator('.sr2-house-arrival__art img');
        await hero.waitFor({ timeout: 20000 });
        await hero.evaluate(image => image.decode());
        const heroSrc = await hero.getAttribute('src');
        result.homepage.heroSrc = heroSrc;
        result.homepage.heroSize = await hero.evaluate(image => ({
          width: image.naturalWidth,
          height: image.naturalHeight,
        }));
        const heroResponse = await context.request.get(new URL(heroSrc, base).href, { timeout: 30000 });
        result.homepage.heroHttp = heroResponse.status();
        result.homepage.servedMonumentSha256 = sha(await heroResponse.body());
        result.homepage.monumentByteMatch = result.homepage.servedMonumentSha256 === localHash;
        result.homepage.heading = (await page.locator('.sr2-house-arrival h1').innerText()).trim();
        result.homepage.framing = await page.evaluate(() => {
          const rect = selector => {
            const element = document.querySelector(selector);
            if (!element) return null;
            const { top, bottom, left, right, width, height } = element.getBoundingClientRect();
            return { top, bottom, left, right, width, height };
          };
          const image = document.querySelector('.sr2-house-arrival__art img');
          return {
            header: rect('[data-site-header]'),
            arrival: rect('.sr2-house-arrival'),
            art: rect('.sr2-house-arrival__art'),
            image: rect('.sr2-house-arrival__art img'),
            objectFit: image && getComputedStyle(image).objectFit,
            objectPosition: image && getComputedStyle(image).objectPosition,
          };
        });
        result.mascotCount.homepage = await mascot(page);
        result.overflow.homepage = await overflow(page);
        result.brokenImages.homepageTop = await visibleBroken(page);
        await page.screenshot({ path: path.join(out, viewport.name + '-homepage-top.png'), animations: 'disabled' });
        await capture(page, viewport.name + '-homepage');
        const gallery = page.locator('[data-jersey-gallery]').first();
        result.homepage.jerseySlides = await gallery.locator('.sr2-jersey-experience__slide').count();
        result.homepage.firstJerseyLink = await gallery
          .locator('.sr2-jersey-experience__slide a')
          .first()
          .getAttribute('href');
        await gallery.scrollIntoViewIfNeeded();
        await gallery
          .locator('.sr2-jersey-experience__slide img')
          .first()
          .evaluate(image => image.decode());
        result.homepage.firstJerseyImage = await gallery
          .locator('.sr2-jersey-experience__slide img')
          .first()
          .evaluate(image => ({ src: image.currentSrc, width: image.naturalWidth }));
        const controls = gallery.locator('[data-jersey-controls]');
        result.homepage.jerseyControlsVisible = await controls.isVisible();
        result.homepage.jerseyPositionBefore = (await gallery.locator('[data-jersey-position]').innerText()).trim();
        await gallery.locator('[data-jersey-next]').click();
        await page.waitForTimeout(350);
        result.homepage.jerseyPositionAfter = (await gallery.locator('[data-jersey-position]').innerText()).trim();
        result.brokenImages.jersey = await visibleBroken(page);
        await page.screenshot({ path: path.join(out, viewport.name + '-jersey.png'), animations: 'disabled' });

        response = await page.goto(fresh('/pre-order/'), { waitUntil: 'load', timeout: 45000 });
        result.responses.preorder = response.status();
        const reserveHero = page.locator('.sr2-reserve-arrival img').first();
        await reserveHero.waitFor({ timeout: 20000 });
        await reserveHero.evaluate(image => image.decode());
        result.preorder.heroSize = await reserveHero.evaluate(image => ({
          width: image.naturalWidth,
          height: image.naturalHeight,
        }));
        result.preorder.heroSrc = await reserveHero.getAttribute('src');
        result.preorder.heading = (await page.locator('.sr2-reserve-arrival h1').innerText()).trim();
        result.preorder.framing = await page.evaluate(() => {
          const rect = selector => {
            const element = document.querySelector(selector);
            if (!element) return null;
            const { top, bottom, left, right, width, height } = element.getBoundingClientRect();
            return { top, bottom, left, right, width, height };
          };
          const image = document.querySelector('.sr2-reserve-arrival img');
          return {
            header: rect('[data-site-header]'),
            arrival: rect('.sr2-reserve-arrival'),
            media: rect('.sr2-reserve-arrival .sr2-arrival__media'),
            image: rect('.sr2-reserve-arrival img'),
            objectFit: image && getComputedStyle(image).objectFit,
            objectPosition: image && getComputedStyle(image).objectPosition,
          };
        });
        result.preorder.processVisible = (await page.locator('#reserve-process').count()) === 1;
        result.preorder.productCards = await page.locator('#reserve .sr2-c-editorial-card').count();
        result.preorder.firstCard = await page
          .locator('#reserve .sr2-c-editorial-card')
          .first()
          .innerText()
          .catch(() => '');
        result.preorder.firstCardLink = await page
          .locator('#reserve .sr2-c-editorial-card .sr2-c-editorial-card__title a')
          .first()
          .getAttribute('href')
          .catch(() => null);
        result.mascotCount.preorder = await mascot(page);
        result.overflow.preorder = await overflow(page);
        result.brokenImages.preorderTop = await visibleBroken(page);
        await page.screenshot({ path: path.join(out, viewport.name + '-preorder-top.png'), animations: 'disabled' });
        await capture(page, viewport.name + '-preorder');
        if (result.preorder.firstCardLink) {
          response = await page.goto(new URL(result.preorder.firstCardLink, base).href, {
            waitUntil: 'load',
            timeout: 45000,
          });
          result.preorder.firstCardPdpHttp = response.status();
          result.preorder.firstCardPdpHeading = (await page.locator('h1.product_title').innerText()).trim();
          result.preorder.firstCardName = await page.locator('h1.product_title').innerText();
          result.preorder.firstCardConsistent = result.preorder.firstCard.includes(result.preorder.firstCardPdpHeading);
        }

        response = await page.goto(fresh('/product/br-004/'), { waitUntil: 'load', timeout: 45000 });
        result.responses.product = response.status();
        result.product.title = await page.title();
        result.product.heading = (await page.locator('h1.product_title').innerText()).trim();
        await page.locator('form.variations_form select[name="attribute_size"]').selectOption('M');
        await page.waitForFunction(() => !!document.querySelector('input.variation_id')?.value, null, {
          timeout: 20000,
        });
        result.product.variationId = await page.locator('input.variation_id').inputValue();
        result.product.beforeReadyState = await page
          .locator('form.variations_form')
          .getAttribute('data-sr2-variation-state');
        await page.waitForFunction(
          () => document.querySelector('form.variations_form')?.dataset.sr2VariationState === 'valid',
          null,
          { timeout: 20000 }
        );
        result.product.readyState = await page.locator('form.variations_form').getAttribute('data-sr2-variation-state');
        result.mascotCount.product = await mascot(page);
        result.overflow.product = await overflow(page);
        result.brokenImages.product = await visibleBroken(page);
        await capture(page, viewport.name + '-pdp');
        await page.locator('button.single_add_to_cart_button').click();
        await page.locator('.woocommerce-message').first().waitFor({ timeout: 20000 });
        result.product.addNotice = (await page.locator('.woocommerce-message').first().innerText()).slice(0, 300);
        result.product.cartCookiePresent = (await context.cookies()).some(
          cookie => cookie.name === 'woocommerce_items_in_cart'
        );
        response = await page.goto(base + '/cart/', { waitUntil: 'commit', timeout: 45000 });
        await page.locator('.woocommerce-cart-form .cart_item').first().waitFor({ timeout: 20000 });
        result.responses.cart = response.status();
        result.cart.lines = await page.locator('.woocommerce-cart-form .cart_item').count();
        result.cart.text = (await page.locator('main').innerText()).slice(0, 2200);
        result.mascotCount.cart = await mascot(page);
        result.overflow.cart = await overflow(page);
        result.brokenImages.cart = await visibleBroken(page);
        await capture(page, viewport.name + '-cart');
        response = await page.goto(base + '/checkout/', { waitUntil: 'domcontentloaded', timeout: 45000 });
        result.responses.checkout = response.status();
        result.checkout.lines = await page.locator('.woocommerce-checkout-review-order-table .cart_item').count();
        result.checkout.paymentMethods = await page
          .locator('.wc_payment_method input[name="payment_method"]')
          .evaluateAll(inputs => inputs.map(input => input.value));
        result.checkout.totalText = (await page.locator('.woocommerce-checkout-review-order-table').innerText()).slice(
          0,
          1000
        );
        result.checkout.placeOrderVisible = await page
          .locator('#place_order')
          .isVisible()
          .catch(() => false);
        result.mascotCount.checkout = await mascot(page);
        result.overflow.checkout = await overflow(page);
        result.brokenImages.checkout = await visibleBroken(page);
        await capture(page, viewport.name + '-checkout');
        const required = ['homepage', 'preorder', 'product', 'cart', 'checkout'];
        const noOverflow = Object.values(result.overflow).every(value => value.overflowPx <= 1);
        const noBroken = Object.values(result.brokenImages).every(value => value.length === 0);
        result.mobileHeroClearance =
          viewport.name !== 'mobile' ||
          [result.homepage.framing.art, result.preorder.framing.media].every(
            media => media.top >= result.homepage.framing.header.bottom - 1
          );
        result.status =
          required.every(route => result.responses[route] === 200) &&
          Object.values(result.css).every(value => value.http === 200 && value.byteMatch) &&
          result.homepage.monumentByteMatch &&
          result.homepage.jerseySlides >= 2 &&
          result.homepage.jerseyPositionBefore !== result.homepage.jerseyPositionAfter &&
          result.preorder.productCards > 0 &&
          result.preorder.firstCardPdpHttp === 200 &&
          result.preorder.firstCardConsistent &&
          result.product.variationId &&
          result.product.readyState === 'valid' &&
          result.product.addNotice &&
          result.product.cartCookiePresent &&
          result.cart.lines > 0 &&
          result.checkout.lines > 0 &&
          noOverflow &&
          noBroken &&
          result.mobileHeroClearance &&
          Object.values(result.mascotCount).every(value => value === 0)
            ? 'PASS_TO_CHECKOUT'
            : 'FAIL';
      } catch (error) {
        result.status = 'FAIL';
        result.failure = String(error.stack || error).slice(0, 4000);
      }
      results.push(result);
      await context.close();
    }
  } finally {
    await browser.close();
    await fs.writeFile(path.join(out, 'results.json'), JSON.stringify(results, null, 2));
  }
  results.forEach(result =>
    console.log(
      JSON.stringify({
        viewport: result.viewport.name,
        status: result.status,
        responses: result.responses,
        css: result.css,
        monumentByteMatch: result.homepage.monumentByteMatch,
        mobileHeroClearance: result.mobileHeroClearance,
        heroMediaTop: result.homepage.framing?.art?.top,
        reserveMediaTop: result.preorder.framing?.media?.top,
        jerseySlides: result.homepage.jerseySlides,
        jerseyPositionAfter: result.homepage.jerseyPositionAfter,
        productCards: result.preorder.productCards,
        cartLines: result.cart.lines,
        checkoutLines: result.checkout.lines,
        overflow: result.overflow,
        brokenImages: result.brokenImages,
        pageErrors: result.pageErrors,
        requestFailures: result.requestFailures,
        failure: result.failure,
      })
    )
  );
  if (results.some(result => result.status !== 'PASS_TO_CHECKOUT')) process.exitCode = 1;
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
