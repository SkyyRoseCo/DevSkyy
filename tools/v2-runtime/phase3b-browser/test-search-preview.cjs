/* Browser regression: real DOM/template parsing with intercepted native search. */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const { chromium } = require('./runtime.cjs').requireQa('playwright');
const source = fs.readFileSync(
  path.join(__dirname, '../../../wordpress-theme/skyyrose-flagship-2/assets/js/search-preview.js'),
  'utf8'
);
const fixture = `<dialog id="sr2-search-dialog"><form class="sr2-search-dialog__form" action="/" method="get"><input name="s" data-search-input><button>Search</button></form><div data-search-preview hidden data-idle="Type more" data-loading="Loading" data-empty="Empty" data-error="Error" data-count="%d preview results"><p role="status"></p><ul data-search-preview-results></ul></div></dialog>`;
const results = title =>
  `<main class="sr2-search"><section data-search-group="products"><header class="sr2-section-head"><h2>Products</h2></header><article class="sr2-c-editorial-card"><p class="sr2-c-editorial-card__collection">Black Rose</p><h3 class="sr2-c-editorial-card__title"><a href="javascript:alert(1)">Unsafe</a><a href="https://other.test/product">External</a><a href="/product/one">${title}</a></h3></article><img src="/do-not-load.jpg"><script>window.unsafe=true</script></section></main>`;

test('native search preview debounce, actual markup, safe links, empty/error, abort, focus and GET fallback', async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage();
    let requests = [];
    await page.route('**/*', async route => {
      const url = new URL(route.request().url());
      if (!url.searchParams.has('s')) return route.fulfill({ contentType: 'text/html', body: fixture });
      const query = url.searchParams.get('s');
      requests.push(query);
      if (query === 'error') return route.fulfill({ status: 500, body: 'Unavailable' });
      if (query === 'old') await new Promise(resolve => setTimeout(resolve, 650));
      const body =
        query === 'empty'
          ? '<main class="sr2-search"><section class="sr2-search__empty"></section></main>'
          : query === 'many'
            ? `<main class="sr2-search"><section data-search-group="pages"><header class="sr2-section-head"><h2>Pages</h2></header>${Array.from({ length: 9 }, (_, i) => `<article class="sr2-search__result"><h2><a href="/page/${i}">Title ${i}</a></h2></article>`).join('')}<article class="sr2-search__result"><h2><a href="javascript:alert(1)">Bad</a></h2></article></section></main>`
            : results(query === 'safe' ? '&lt;img src=x onerror=alert(1)&gt;' : query);
      await route.fulfill({ contentType: 'text/html', body }).catch(() => {});
    });
    await page.goto('http://search.test');
    const media = [];
    page.on('request', request => {
      if (request.url().includes('do-not-load')) media.push(request.url());
    });
    await page.addScriptTag({ content: source });
    await page.evaluate(() => document.querySelector('dialog').showModal());
    const input = page.locator('input');
    const status = page.locator('[role=status]');
    const links = page.locator('[data-search-preview-results] a');
    await input.fill('a');
    await page.waitForTimeout(330);
    assert.equal(requests.length, 0);
    await input.fill('first');
    await page.waitForTimeout(80);
    await input.fill('safe');
    await page.waitForFunction(() => document.querySelector('[role=status]').textContent === '1 preview results');
    assert.deepEqual(requests, ['safe']);
    assert.equal(await links.first().textContent(), '<img src=x onerror=alert(1)>Products · Black Rose');
    assert.equal(await page.evaluate(() => document.activeElement.matches('input')), true);
    assert.equal(await page.evaluate(() => !!window.unsafe), false);
    assert.deepEqual(media, []);
    await input.press('Tab');
    await page.keyboard.press('Tab');
    assert.equal(await page.evaluate(() => document.activeElement.matches('[data-search-preview-results] a')), true);
    await input.fill('many');
    await page.waitForFunction(() => document.querySelectorAll('[data-search-preview-results] a').length === 6);
    assert.equal(await status.textContent(), '6 preview results');
    await input.fill('old');
    await page.waitForTimeout(320);
    assert.equal(await status.textContent(), 'Loading');
    await input.fill('new');
    await page.waitForFunction(
      () => document.querySelector('[data-search-preview-results] a')?.textContent === 'newProducts · Black Rose'
    );
    await page.waitForTimeout(400);
    assert.equal(await links.first().textContent(), 'newProducts · Black Rose');
    await input.fill('empty');
    await page.waitForFunction(() => document.querySelector('[role=status]').textContent === 'Empty');
    assert.equal(await links.count(), 0);
    await input.fill('error');
    await page.waitForFunction(() => document.querySelector('[role=status]').textContent === 'Error');
    await input.fill('old');
    await page.waitForTimeout(320);
    await page.evaluate(() => document.querySelector('dialog').close());
    await page.waitForTimeout(700);
    assert.equal(await links.count(), 0);
    assert.equal(await status.textContent(), 'Type more');
    await page.evaluate(() => document.querySelector('dialog').showModal());
    await input.fill('fallback');
    await Promise.all([page.waitForURL('**/?s=fallback'), input.press('Enter')]);
    assert.equal(new URL(page.url()).searchParams.get('s'), 'fallback');
  } finally {
    await browser.close();
  }
});
