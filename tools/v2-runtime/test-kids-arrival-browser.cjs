/** Real template/media gate and built assets in an offline browser component fixture. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const crypto = require('node:crypto');
const { execFileSync } = require('node:child_process');
const { createRequire } = require('node:module');

const root = path.resolve(__dirname, '../..');
const git = (...args) => execFileSync('/usr/bin/git', args, { cwd: root, encoding: 'utf8' }).trim();
assert.equal(git('status', '--porcelain', '--ignore-submodules=all'), '', 'Commit source/build/test candidate before browser execution');
const theme = path.join(root, 'wordpress-theme/skyyrose-flagship-2');
const fixtureRoot = fs.realpathSync(process.env.KIDS_FIXTURE_ROOT);
const out = path.resolve(process.env.KIDS_ARTIFACT_DIR);
assert(fixtureRoot.startsWith(path.join(root, '.artifacts/') + path.sep) || fixtureRoot.startsWith(path.join(root, '.artifacts/')));
assert(out.startsWith(path.join(root, '.artifacts/')) && !fs.existsSync(out));
const requireQa = createRequire(process.env.KIDS_QA_PACKAGE);
const { chromium } = requireQa('playwright-core');
const chrome = fs.realpathSync(process.env.KIDS_CHROME);
const php = fs.realpathSync(process.env.KIDS_PHP);
const sha = value => crypto.createHash('sha256').update(value).digest('hex');
const pin = file => ({ path: file, sha256: sha(fs.readFileSync(file)), bytes: fs.statSync(file).size });
const prefix = '/wp-content/themes/skyyrose-flagship-2/';
const binding = JSON.parse(fs.readFileSync(path.join(theme, 'data/product-presentation-registry.json'))).collections['kids-capsule'].imagery.collection_hero;
const renders = {};
for (const mode of ['admitted', 'withheld']) {
  const sourceTheme = mode === 'withheld' ? path.join(fixtureRoot, 'withheld') : theme;
  renders[mode] = execFileSync(php, [path.join(__dirname, 'render-collection-imagery.php'), 'kids-capsule', sourceTheme, '--arrival-only'], { encoding: 'utf8', maxBuffer: 2 ** 20, timeout: 15000 });
}
assert(renders.admitted.includes('data-media-state="admitted"'));
assert(renders.withheld.includes('data-media-state="unavailable"'));
assert(!/<(?:img|video|source|link)\b/.test(renders.withheld));
fs.mkdirSync(out, { recursive: true, mode: 0o700 });
const report = {
  status: 'RUNNING',
  scope: 'OFFLINE_RENDERED_COMPONENT_ONLY_WP_WOO_REQUEST_LAYER_STUBBED_NO_NATIVE_SESSION_OR_INSTALLED_STACK_PROOF',
  sourceCommit: git('rev-parse', 'HEAD'),
  sourceTree: git('rev-parse', 'HEAD^{tree}'),
  harness: pin(__filename),
  renderer: pin(path.join(__dirname, 'render-collection-imagery.php')),
  playwright: pin(requireQa.resolve('playwright-core/package.json')),
  binaries: [pin(chrome), pin(php), pin(process.execPath)],
  sources: ['assets/css/theme.min.css', 'assets/js/visual-recovery.min.js', 'template-parts/collections/arrival.php', 'template-parts/collections/arrival-product.php', 'inc/performance.php'].map(file => pin(path.join(theme, file))),
  fixtures: pin(path.join(fixtureRoot, 'preparation.json')),
  cases: [],
  cleanup: [],
  limits: ['Page request interception is not process-wide network containment', 'Offline rendered component; no native WordPress/WooCommerce session, installed-stack or privacy-collector qualification'],
  authentication: 'NOT_APPLICABLE_OFFLINE_NO_CREDENTIALS',
};
const save = () => fs.writeFileSync(path.join(out, 'results.json'), JSON.stringify(report, null, 2) + '\n', { mode: 0o600 });
const bounded = async (action, milliseconds = 5000) => {
  let timer;
  try {
    return await Promise.race([Promise.resolve().then(action), new Promise((_, reject) => { timer = setTimeout(() => reject(new Error('Cleanup deadline exceeded')), milliseconds); })]);
  } finally { clearTimeout(timer); }
};
const cleanup = async (label, action) => {
  try { await bounded(action); report.cleanup.push({ label, status: 'PASS' }); return true; }
  catch (error) { report.cleanup.push({ label, status: 'FAIL', error: error.stack }); return false; }
};
const mime = { '.css': 'text/css', '.js': 'text/javascript', '.webp': 'image/webp', '.png': 'image/png', '.woff2': 'font/woff2' };
let base;
const server = http.createServer((request, response) => {
  try {
    assert(request.method === 'GET');
    const url = new URL(request.url, base);
    if (url.pathname.startsWith('/fixture/')) {
      const scenario = url.pathname.slice('/fixture/'.length);
      assert(['admitted', 'withheld', 'early-error', 'late-error'].includes(scenario));
      let html = renders[scenario === 'withheld' ? 'withheld' : 'admitted'].replaceAll('https://skyyrose.co', base);
      const styles = ['design-tokens', 'theme', 'controls', 'visual-recovery', 'collection-world'].map(name => `<link rel="stylesheet" href="${prefix}assets/css/${name}.min.css">`).join('');
      const controller = `<script src="${prefix}assets/js/visual-recovery.min.js"></script>`;
      html = html.replace('</head>', `<meta name="viewport" content="width=device-width, initial-scale=1">${styles}</head>`);
      html = html.replace('</body>', `${controller}</body>`);
      response.writeHead(200, { 'Content-Type': 'text/html', 'Cache-Control': 'no-store' });
      response.end(html);
      return;
    }
    assert(url.pathname.startsWith(prefix));
    const relative = decodeURIComponent(url.pathname.slice(prefix.length));
    const file = fs.realpathSync(path.join(theme, relative));
    assert(file.startsWith(theme + path.sep) && fs.statSync(file).isFile());
    const type = mime[path.extname(file)];
    assert(type);
    response.writeHead(200, { 'Content-Type': type, 'Cache-Control': 'no-store' });
    fs.createReadStream(file).on('error', () => response.destroy()).pipe(response);
  } catch {
    response.writeHead(404);
    response.end();
  }
});

(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  base = `http://127.0.0.1:${server.address().port}`;
  let browser;
  let browserServer;
  try {
    browserServer = await chromium.launchServer({ executablePath: chrome, headless: true, host: '127.0.0.1', port: 0, timeout: 15000 });
    browser = await chromium.connect(browserServer.wsEndpoint(), { timeout: 15000 });
    for (const scenario of ['admitted', 'withheld', 'early-error', 'late-error']) {
      for (const width of [1440, 390]) {
        for (const reducedMotion of ['no-preference', 'reduce']) {
          const context = await browser.newContext({ viewport: { width, height: width === 1440 ? 900 : 844 }, reducedMotion });
          const row = { scenario, width, reducedMotion, status: 'RUNNING', requests: [] };
          let releaseController;
          const controllerGate = new Promise(resolve => { releaseController = resolve; });
          try {
            await context.route('**/*', async route => {
              const request = route.request();
              row.requests.push(request.url());
              if (new URL(request.url()).origin !== base) return route.abort();
              if (scenario === 'early-error' && request.resourceType() === 'image') return route.fulfill({ status: 404, body: '' });
              if (scenario === 'early-error' && new URL(request.url()).pathname.endsWith('/visual-recovery.min.js')) await controllerGate;
              return route.continue();
            });
            const page = await context.newPage();
            const navigation = page.goto(base + '/fixture/' + scenario, { waitUntil: 'load' }).then(() => null, error => error);
            if (scenario === 'early-error') {
              // Hold the footer's parser-blocking controller until native image
              // failure is observed. Its initialization must therefore see the
              // already-failed image while the document is still parsing.
              await page.waitForFunction(() => {
                const image = document.querySelector('[data-product-arrival-media] img');
                return image?.complete && !image.naturalWidth && document.readyState === 'loading';
              });
              row.failureBeforeController = await page.evaluate(() => ({ state: document.readyState, complete: document.querySelector('[data-product-arrival-media] img').complete, naturalWidth: document.querySelector('[data-product-arrival-media] img').naturalWidth, controllerInitialized: !!document.documentElement.dataset.recoveryInitialized }));
              assert.equal(row.failureBeforeController.controllerInitialized, false);
              releaseController();
            }
            const navigationError = await navigation;
            if (navigationError) throw navigationError;
            const heading = page.locator('h1');
            await heading.waitFor({ state: 'visible' });
            assert.equal(await heading.textContent(), 'Kids Capsule');
            await page.evaluate(() => document.fonts.ready);
            const image = page.locator('[data-product-arrival-media] img');
            if (['admitted', 'late-error'].includes(scenario)) {
              await image.evaluate(element => element.decode());
              row.decoded = await image.evaluate(element => ({ src: element.currentSrc, width: element.naturalWidth, height: element.naturalHeight, alt: element.alt, role: element.dataset.mediaRole, sku: element.dataset.mediaSku, fit: getComputedStyle(element).objectFit }));
              assert.equal(row.decoded.role, 'collection_hero');
              assert.equal(row.decoded.sku, 'kids-002');
              assert.equal(row.decoded.alt, binding.alt);
              assert.equal(row.decoded.fit, 'contain');
              const url = new URL(row.decoded.src);
              const file = path.join(theme, decodeURIComponent(url.pathname.slice(prefix.length)));
              assert.equal(sha(fs.readFileSync(file)), url.searchParams.get('v'));
              if (scenario === 'late-error') await image.evaluate(element => { element.srcset = ''; element.src = '/synthetic-missing-product.webp'; });
            }
            const missing = scenario !== 'admitted';
            if (missing) await page.waitForFunction(() => document.querySelector('[data-product-arrival]').dataset.mediaState === 'unavailable');
            row.layout = await page.evaluate(() => {
              const arrival = document.querySelector('[data-product-arrival]');
              const title = arrival.querySelector('h1');
              const media = arrival.querySelector('img');
              const rect = media?.getBoundingClientRect();
              const style = media && getComputedStyle(media);
              return { width: innerWidth, height: innerHeight, scrollWidth: document.documentElement.scrollWidth, arrivalHeight: arrival.getBoundingClientRect().height, headingHeight: title.getBoundingClientRect().height, state: arrival.dataset.mediaState, actions: [...arrival.querySelectorAll('a')].map(a => ({ href: a.getAttribute('href'), height: a.getBoundingClientRect().height })), mediaVisible: !!rect && rect.width > 0 && rect.height > 0 && style.visibility === 'visible' && Number(style.opacity) > 0 };
            });
            assert(row.layout.scrollWidth <= width && row.layout.headingHeight > 20);
            if (!missing) assert(row.layout.state === 'admitted' && row.layout.mediaVisible, 'Admitted image must have visible nonzero geometry');
            assert(row.layout.actions.length === 2 && row.layout.actions.every(action => action.height >= 40));
            assert.equal(await page.locator('video, [data-recovery-motion-toggle]').count(), 0);
            if (missing) assert(!row.layout.mediaVisible && row.layout.arrivalHeight < row.layout.height * 0.85);
            assert(!row.requests.some(url => /throne|lockup|skyy-canonical|\.(?:webm|mp4|glb)(?:\?|$)/.test(url)));
            const screenshot = path.join(out, `${scenario}-${width}-${reducedMotion}.png`);
            await page.screenshot({ path: screenshot, fullPage: true, animations: 'disabled' });
            row.screenshot = pin(screenshot);
            row.status = 'PASS_COMPONENT_ASSERTIONS_VISUAL_REVIEW_PENDING';
          } catch (error) {
            row.status = 'FAIL';
            row.error = error.stack;
            throw error;
          } finally {
            releaseController();
            report.cases.push(row);
            const closed = await cleanup(`context:${scenario}:${width}:${reducedMotion}`, () => context.close());
            save();
            console.log(row.status, scenario, width, reducedMotion);
            if (!closed) throw new Error('Context cleanup failed; retained case result remains unchanged');
          }
        }
      }
    }
    report.status = 'PASS_COMPONENT_ASSERTIONS_VISUAL_REVIEW_PENDING';
    assert.equal(git('rev-parse', 'HEAD'), report.sourceCommit);
    assert.equal(git('status', '--porcelain', '--ignore-submodules=all'), '');
    assert(report.sources.every(value => pin(value.path).sha256 === value.sha256));
  } finally {
    if (browser) await cleanup('browser-connection', () => browser.close());
    if (browserServer) {
      const closed = await cleanup('browser-server', () => browserServer.close());
      if (!closed) await cleanup('owned-browser-server-kill', () => browserServer.kill());
      await cleanup('owned-browser-child-exit', () => {
        const child = browserServer.process();
        report.browserChild = { pid: child.pid, exitCode: child.exitCode, signalCode: child.signalCode };
        assert(child.exitCode !== null || child.signalCode !== null, 'Owned browser child has no terminal state');
      });
    }
    await cleanup('fixture-http-server', () => {
      server.closeAllConnections();
      return new Promise((resolve, reject) => server.close(error => error ? reject(error) : resolve()));
    });
    if (report.cleanup.some(row => row.status === 'FAIL')) {
      report.status = 'FAIL_CLEANUP'; process.exitCode = 1;
      // A failed public close/kill is an unresolved cleanup failure, never a
      // process-absence claim. Do not let its remaining transport hang this test.
      setTimeout(() => process.exit(1), 1000).unref();
    }
    save();
  }
})().catch(error => { if (!report.status.startsWith('FAIL')) report.status = 'FAIL'; report.error = error.stack; save(); console.error(error); process.exitCode = 1; });
