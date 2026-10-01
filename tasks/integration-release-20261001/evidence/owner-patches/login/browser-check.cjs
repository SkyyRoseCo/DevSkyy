/** Actual NextAuth SDK and login UI, local synthetic fixture only. */
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require(path.resolve(__dirname, '../../frontend/node_modules/@playwright/test'));
(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 375, height: 844 } });
  const page = await context.newPage();
  const origin = 'http://127.0.0.1:18081';
  const result = { mode: 'LOCAL_SYNTHETIC_REAL_NEXTAUTH_SDK', provider_calls: 0, cases: [] };
  let release;
  const pending = new Promise(resolve => { release = resolve; });
  let callbacks = 0;
  let callbackObserved;
  const firstCallback = new Promise(resolve => { callbackObserved = resolve; });
  result.requests = [];
  page.on("response", response => result.requests.push({ path: new URL(response.url()).pathname, status: response.status() }));
  await context.route('**/*', route => {
    if (!['127.0.0.1', 'localhost'].includes(new URL(route.request().url()).hostname)) return route.abort();
    return route.continue();
  });
  await page.route('**/api/auth/callback/credentials', async route => {
    callbacks++;
    if (callbacks === 1) {
      callbackObserved();
      await pending;
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ url: origin + '/admin' }) });
    } else await route.continue();
  });
  try {
    await page.clock.install();
    await page.goto(origin + '/login');
    await page.waitForFunction(() => document.querySelector('input[name="_csrf"]')?.value);
    await page.getByLabel('Email', { exact: true }).fill('owner@example.test');
    await page.getByLabel('Password', { exact: true }).fill('SyntheticPassword123!');
    await page.getByRole('button', { name: 'Sign in', exact: true }).click();
    await Promise.race([firstCallback, new Promise((_, reject) => setTimeout(() => reject(new Error('Callback observation timed out')), 10000))]);
    if (callbacks !== 1) throw new Error('Stalled NextAuth callback was not reached');
    await page.clock.fastForward(30001);
    await page.getByText('Login request timed out. Please try again.', { exact: true }).waitFor();
    if (!(await page.getByRole('button', { name: 'Sign in', exact: true }).isEnabled())) throw new Error('Retry remains disabled');
    const access = await page.evaluate(() => localStorage.getItem('access_token'));
    if (access !== null || !page.url().endsWith('/login')) throw new Error('Timed-out attempt published tokens or navigated');
    const screenshot = '/Users/theceo/.codex/visualizations/2026/10/01/01a0f644-19f5-78c0-926f-f6fc9f9417be/login-deadline-timeout.png';
    await page.screenshot({ path: screenshot });
    result.cases.push({ requirement: 'successful legacy token + stalled actual NextAuth SDK callback', timeoutMessage: true, retryEnabled: true, tokensAbsent: true, route: '/login', screenshot });
    await page.getByRole('button', { name: 'Sign in', exact: true }).click();
    await page.waitForURL('**/admin');
    release();
    await page.waitForTimeout(200);
    const after = await page.evaluate(() => localStorage.getItem('access_token'));
    if (after !== 'synthetic-owner-token') throw new Error('Retry legacy token missing');
    result.cases.push({ requirement: 'retry succeeds; first callback released', callbacks, routeVerifiedBeforeRelease: '/admin', applicationToken: 'SYNTHETIC_EXPECTED', lateSDKCompletion: 'NOT_DETERMINISTICALLY_QUALIFIED', cookieOrdering: 'NOT_QUALIFIED' });
    result.status = 'PASS_APPLICATION_DEADLINE_AND_RETRY';
  } catch (error) {
    result.status = 'FAIL'; result.error = error.message;
    result.visibleError = await page.getByTestId('error-message').textContent().catch(() => null);
    process.exitCode = 1;
  } finally {
    release();
    fs.writeFileSync(path.join(__dirname, 'evidence/browser.json'), JSON.stringify(result, null, 2) + '\n');
    await browser.close();
    console.log(JSON.stringify({ status: result.status, error: result.error, cases: result.cases.length }));
  }
})();
