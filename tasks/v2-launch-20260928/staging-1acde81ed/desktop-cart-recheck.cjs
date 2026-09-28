const { chromium } = require('../../../node_modules/playwright');
const fs = require('node:fs/promises');
const path = require('node:path');
const base = 'https://staging-7e48-skyyrose.wpcomstaging.com';
(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' });
  const page = await context.newPage();
  const result = { candidate: '1acde81ed', viewport: 'desktop', pageErrors: [], responses: {} };
  page.on('pageerror', error => result.pageErrors.push(error.message));
  try {
    const product = await page.goto(base + '/product/br-004/?cartrecheck=1acde81ed-' + Date.now(), {
      waitUntil: 'load',
      timeout: 45000,
    });
    result.responses.product = product.status();
    await page.locator('form.variations_form select[name="attribute_size"]').selectOption('M');
    await page.waitForFunction(() => !!document.querySelector('input.variation_id')?.value, null, { timeout: 20000 });
    result.variationId = await page.locator('input.variation_id').inputValue();
    result.beforeWaitState = await page.locator('form.variations_form').getAttribute('data-sr2-variation-state');
    await page.waitForFunction(
      () => document.querySelector('form.variations_form')?.dataset.sr2VariationState === 'valid',
      null,
      { timeout: 20000 }
    );
    result.readyState = await page.locator('form.variations_form').getAttribute('data-sr2-variation-state');
    result.buttonBeforeClick = await page
      .locator('button.single_add_to_cart_button')
      .evaluate(button => ({
        disabled: button.disabled,
        classes: button.className,
        busy: button.getAttribute('aria-busy'),
      }));
    await page.locator('button.single_add_to_cart_button').click();
    await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
    result.afterAddUrl = page.url();
    result.notices = await page.locator('.woocommerce-message, .woocommerce-error').allInnerTexts();
    result.cookieNames = (await context.cookies()).map(cookie => cookie.name);
    const cart = await page.goto(base + '/cart/?cartrecheck=1acde81ed-' + Date.now(), {
      waitUntil: 'load',
      timeout: 45000,
    });
    result.responses.cart = cart.status();
    result.cartUrl = page.url();
    result.cartLines = await page.locator('.woocommerce-cart-form .cart_item').count();
    result.cartText = (await page.locator('main').innerText()).slice(0, 1500);
    await page.screenshot({ path: path.join(__dirname, 'artifacts', 'desktop-cart-recheck.png'), fullPage: true });
    if (result.cartLines) {
      const checkout = await page.goto(base + '/checkout/?cartrecheck=1acde81ed-' + Date.now(), {
        waitUntil: 'load',
        timeout: 45000,
      });
      result.responses.checkout = checkout.status();
      result.checkoutLines = await page.locator('.woocommerce-checkout-review-order-table .cart_item').count();
      result.total = (await page.locator('.woocommerce-checkout-review-order-table').innerText()).slice(0, 500);
      await page.screenshot({
        path: path.join(__dirname, 'artifacts', 'desktop-checkout-recheck.png'),
        fullPage: true,
      });
    }
  } finally {
    await browser.close();
  }
  await fs.writeFile(path.join(__dirname, 'artifacts', 'desktop-cart-recheck.json'), JSON.stringify(result, null, 2));
  console.log(JSON.stringify(result));
  if (!result.cartLines || !result.checkoutLines) process.exitCode = 1;
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
