const { spawn } = require('node:child_process');
const path = require('node:path');
const fs = require('node:fs');
const os = require('node:os');
const net = require('node:net');
const assert = require('node:assert/strict');
const { requireQa, base, out, validateLabel } = require('./runtime.cjs');
const { createOriginProxy } = require('./origin-proxy.cjs');
const { beginRun } = require('./run-evidence.cjs');
if (process.argv[2]) validateLabel(process.argv[2]);
const cases = [
  ['home-mobile', '/', false],
  ['home-desktop', '/', true],
  ['pdp-mobile', '/product/sg-005/', false],
  ['pdp-desktop', '/product/sg-005/', true],
  ['shop-mobile', '/shop/', false],
  ['shop-desktop', '/shop/', true],
  ['collection-mobile', '/collections/signature/', false],
  ['collection-desktop', '/collections/signature/', true],
  ['cart-mobile', '/cart/', false],
  ['cart-desktop', '/cart/', true],
  ['checkout-mobile', '/checkout/', false],
  ['checkout-desktop', '/checkout/', true],
];
const prefix = 'lighthouse-' + (process.argv[2] ? process.argv[2] + '-' : '');
const run = beginRun(path.join(out, prefix + 'run.json'));
(async () => {
  if (process.env.V2_LH_CASE && !cases.some(([name]) => name === process.env.V2_LH_CASE)) {
    throw new Error('Unknown V2_LH_CASE: ' + process.env.V2_LH_CASE);
  }
  const selectedCases = process.env.V2_LH_CASES?.split(',');
  if (selectedCases?.some(selected => !cases.some(([name]) => name === selected)))
    throw new Error('Unknown V2_LH_CASES');
  const chrome = requireQa('playwright').chromium.executablePath();
  const cli = requireQa.resolve('lighthouse/cli/index.js');
  const proxy = await createOriginProxy(base);
  const completed = [];
  const proxyTraffic = [];
  try {
    // Await each process: the proxy stays responsive, and cases stay serial.
    for (const [name, route, desktop] of cases) {
      if (process.env.V2_LH_CASE && name !== process.env.V2_LH_CASE) continue;
      if (selectedCases && !selectedCases.includes(name)) continue;
      const allowedBefore = proxy.allowedRequests;
      const chromeFlags = [
        '--headless',
        '--no-sandbox',
        '--disable-gpu',
        '--disable-quic',
        '--host-resolver-rules="MAP * ~NOTFOUND, EXCLUDE 127.0.0.1"',
        '--proxy-server=' + proxy.url,
        '--proxy-bypass-list=<-loopback>',
      ].join(' ');
      const args = [
        cli,
        base + route,
        '--quiet',
        '--output=json',
        '--output=html',
        '--save-assets',
        '--output-path=' + path.join(out, prefix + name),
        '--only-categories=performance,accessibility,best-practices,seo',
        '--blocked-url-patterns=https://*',
        '--chrome-flags=' + chromeFlags,
        ...(desktop ? ['--preset=desktop'] : []),
        '--screenEmulation.width=' + (desktop ? 1440 : 390),
        '--screenEmulation.height=' + (desktop ? 1000 : 844),
        '--screenEmulation.deviceScaleFactor=1',
        '--screenEmulation.mobile=' + (desktop ? 'false' : 'true'),
      ];
      let cartContext;
      let cartProfile;
      try {
        if (name.startsWith('cart-') || name.startsWith('checkout-')) {
          // Seed only our ephemeral synthetic cart, then let Lighthouse reuse the
          // native cookie jar. No session cookie is written into report headers.
          const listener = net.createServer();
          await new Promise(resolve => listener.listen(0, '127.0.0.1', resolve));
          const port = listener.address().port;
          await new Promise(resolve => listener.close(resolve));
          cartProfile = fs.mkdtempSync(path.join(os.tmpdir(), 'sr2-lighthouse-cart-'));
          cartContext = await requireQa('playwright').chromium.launchPersistentContext(cartProfile, {
            headless: true,
            args: [
              '--remote-debugging-port=' + port,
              '--disable-gpu',
              '--disable-quic',
              '--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1',
              '--proxy-server=' + proxy.url,
              '--proxy-bypass-list=<-loopback>',
            ],
          });
          const page = await cartContext.newPage();
          await page.goto(base + '/product/sg-005/');
          await page.locator('select[name="attribute_size"]').selectOption('M');
          await page.locator('.woocommerce-variation-add-to-cart-enabled').waitFor();
          await Promise.all([page.waitForNavigation(), page.locator('button.single_add_to_cart_button').click()]);
          assert(await page.locator('.woocommerce-message').count(), 'Synthetic cart seed did not confirm');
          for (const tab of cartContext.pages()) await tab.close();
          args.push('--port=' + port, '--disable-storage-reset');
        }
        await new Promise((resolve, reject) => {
          const child = spawn(process.execPath, args, {
            stdio: 'inherit',
            env: { ...process.env, CHROME_PATH: chrome },
            timeout: 180000,
          });
          child.once('error', reject);
          child.once('close', (status, signal) =>
            status === 0 ? resolve() : reject(new Error(name + ' Lighthouse failed: ' + (signal || status)))
          );
        });
        const report = JSON.parse(fs.readFileSync(path.join(out, prefix + name + '.report.json'), 'utf8'));
        assert.equal(
          new URL(report.finalDisplayedUrl || report.finalUrl).pathname,
          route,
          'Lighthouse route redirected; cannot certify the requested route'
        );
      } finally {
        if (cartContext) await cartContext.close();
        if (cartProfile) fs.rmSync(cartProfile, { recursive: true, force: true });
      }
      const allowedRequests = proxy.allowedRequests - allowedBefore;
      assert(allowedRequests > 0, name + ' produced no allowed proxy traffic; Chromium proxy use is unverified.');
      proxyTraffic.push({ name, allowedRequests });
      completed.push(name);
      console.log(name + ' complete');
    }
  } finally {
    await proxy.close();
  }
  run.pass({
    completed,
    network: {
      policy: 'HTTP requests restricted to exact local fixture origin',
      origin: base,
      allowedRequests: proxy.allowedRequests,
      cases: proxyTraffic,
      blocked: proxy.blocked,
    },
  });
})().catch(error => {
  run.fail(error);
  console.error(error);
  process.exitCode = 1;
});
