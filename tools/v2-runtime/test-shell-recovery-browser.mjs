/** Native bag loading/error fallback in the disposable localhost fixture only. */
import { createRequire } from 'node:module';
import path from 'node:path';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const require = createRequire(path.resolve('.artifacts/v2-phase3-20260905/qa/package.json'));
const { chromium } = require('playwright');
const base = 'http://127.0.0.1:18303';
const out = '.artifacts/v2-phase3-20260905';
const browser = await chromium.launch();
const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
await context.route('**/*', r => new URL(r.request().url()).origin === base ? r.continue() : r.abort());
const page = await context.newPage();
const evidence = { intentionalFault: '503 on native remove_from_cart AJAX; native nonce-bearing GET fallback remains available', paymentSubmitted: false };
try {
 await page.goto(base + '/product/sg-005/');
 await page.getByRole('combobox', { name: 'Size', exact: true }).selectOption('M');
 await Promise.all([page.waitForNavigation(), page.getByRole('button', { name: 'Add to cart', exact: true }).click()]);
 await page.locator('[data-bag-open]').click();
 await page.locator('#sr2-bag-dialog .woocommerce-mini-cart-item img').evaluate(e => e.decode());
 const remove = page.locator('#sr2-bag-dialog .remove');
 evidence.fallbackPath = new URL(await remove.getAttribute('href')).pathname;
 let failRequest;
 const pending = new Promise(resolve => { failRequest = resolve; });
 await page.route('**/*wc-ajax=remove_from_cart*', async route => {
  await pending;
  await route.fulfill({ status: 503, contentType: 'application/json', body: '{"error":"isolated fault injection"}' });
 });
 await remove.click();
 await page.locator('#sr2-bag-dialog .blockOverlay').first().waitFor({ state: 'visible' });
 assert.equal(await page.locator('#sr2-bag-dialog .woocommerce-mini-cart-item').count(), 1);
 assert.equal(await page.locator('[data-bag-status]').textContent(), '');
 evidence.pendingPreservesItemAndNoSuccess = true;
 await page.screenshot({ path: out + '/final-bag-loading-390.png', animations: 'disabled' });
 const navigation = page.waitForNavigation();
 failRequest();
 await navigation;
 // Woo may return to its original referrer after the nonce-bearing GET succeeds.
 await page.locator('.woocommerce-message').filter({hasText:'removed'}).waitFor();
 evidence.nativeRecoveryPath = new URL(page.url()).pathname;
 assert.equal(await page.evaluate(() => document.body.style.position), '');
 assert.equal(await page.locator('.sr2-header__bag-count').textContent(), '0');
 await page.goto(base + '/cart/');await page.locator('.cart-empty').waitFor();assert.equal(await page.locator('main h1').count(),1);
 evidence.nativeGetFallback = { path: evidence.nativeRecoveryPath, emptyCartVerifiedAt: '/cart/', empty: true, unlocked: true };
 await page.screenshot({ path: out + '/final-bag-error-recovery-390.png', animations: 'disabled' });
 // Text-resize probe supplements the full 320px layout matrix; it is not browser zoom certification.
 await page.goto(base);
 await page.evaluate(() => document.documentElement.style.fontSize = '200%');
 await page.locator('[data-sr2-menu]').click();
 evidence.textResize = await page.evaluate(() => ({ width: innerWidth, scroll: document.documentElement.scrollWidth, navScroll: document.querySelector('[data-sr2-nav]').scrollWidth, navClient: document.querySelector('[data-sr2-nav]').clientWidth }));
 assert.equal(evidence.textResize.width, evidence.textResize.scroll);
 assert(evidence.textResize.navScroll <= evidence.textResize.navClient + 1);
 await page.screenshot({ path: out + '/final-text-resize-390.png', animations: 'disabled' });
 evidence.status = 'PASS';
} catch (error) { evidence.status = 'FAIL'; evidence.error = error.stack; evidence.failurePath = new URL(page.url()).pathname; evidence.failureText = await page.locator('main').innerText().catch(()=>'unavailable'); await page.screenshot({path:out+'/recovery-failure.png'}).catch(()=>{}); throw error; }
finally { await fs.writeFile(out + '/recovery-browser.json', JSON.stringify(evidence, null, 2)); await browser.close(); }
console.log(JSON.stringify(evidence));
