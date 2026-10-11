/* Actual local V2 templates across screen sizes; no live commerce/release claim. */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const { chromium } = require('./runtime.cjs').requireQa('playwright');
const root = path.resolve(__dirname, '../../..');
const output = path.join(root, 'tasks/v2-creative-review/v2-imagery-reset-20261002/v2-card-placement-review-20261006/imagery-optimization-20261006');
const base = process.env.V2_BASE_URL || 'http://127.0.0.1:18336';
const route = '/' + path.relative(root, output).split(path.sep).join('/');
const matrix = [ [390, 1], [390, 2], [390, 3], [768, 1], [768, 2], [1440, 1], [1440, 2] ];

async function observe(browser, filename, width, dpr, capture = false) {
  const page = await browser.newPage({ viewport: { width, height: 980 }, deviceScaleFactor: dpr });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  try {
    await page.goto(base + route + '/' + filename);
    await page.locator('article[data-sku] img.sr2-c-editorial-card__product-image').evaluateAll(images => Promise.all(images.map(async image => { image.loading = 'eager'; await image.decode(); })));
    const cards = await page.locator('article[data-sku]').evaluateAll(articles => articles.map(article => {
      const image = article.querySelector('img.sr2-c-editorial-card__product-image');
      return { sku: article.dataset.sku, listing: article.closest('[data-listing]')?.dataset.listing, collection: article.dataset.collection, current_src: image.currentSrc, slot_width: image.getBoundingClientRect().width, source_width: Number(image.currentSrc.match(/-(\d+)w\.webp$/)?.[1] || image.getAttribute('width')), complete: image.complete && image.naturalWidth > 0 };
    }));
    assert.equal(cards.length, 33);
    assert.equal(new Set(cards.map(card => card.sku)).size, 33);
    assert.equal(cards.filter(card => card.listing === 'standard').length, 18);
    assert.equal(cards.filter(card => card.listing === 'pre-order').length, 15);
    assert.ok(cards.every(card => card.complete));
    for (const card of cards) {
      const url = new URL(card.current_src);
      const file = path.join(root, decodeURIComponent(url.pathname));
      assert.ok(url.origin === base && fs.existsSync(file));
      card.encoded_bytes = fs.statSync(file).size;
      if (filename !== 'baseline-before.html') {
        assert.match(card.current_src, new RegExp('/' + card.sku + '-\\d+w\\.webp$'));
        const original = fs.statSync(path.join(root, 'wordpress-theme/skyyrose-flagship-2/assets/v2-original/products', card.sku + '.png')).size;
        assert.ok(card.encoded_bytes < original);
      }
    }
    assert.deepEqual(errors, []);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1);
    assert.equal(overflow, false, 'No horizontal overflow');
    const contexts = [];
    if (filename === 'contexts.html') {
      const images = page.locator('#imagery-contexts img');
      await images.evaluateAll(rows => Promise.all(rows.map(async image => { image.loading = 'eager'; await image.decode(); })));
      contexts.push(...await images.evaluateAll(rows => rows.map(image => ({ surface: image.closest('.sr2-editorial-film') ? 'home-film' : image.closest('.sr2-fashion-editorial') ? 'collection-editorial' : image.closest('.sr-kids-procession__proof') ? 'kids-proof' : image.classList.contains('sr2-immersive__hotspot-image') ? 'immersive-hotspot' : image.closest('#imagery-pdp') ? 'pdp' : image.closest('#imagery-thumbnails') ? 'thumbnail' : 'other', current_src: image.currentSrc, slot_width: image.getBoundingClientRect().width, source_width: Number(image.currentSrc.match(/-(\d+)w\.webp$/)?.[1]), complete: image.complete && image.naturalWidth > 0 }))));
      for (const context of contexts) { assert.equal(context.complete, true); assert.match(context.current_src, /-\d+w\.webp$/); }
      assert.ok(contexts.some(row => row.surface === 'pdp'));
      assert.ok(contexts.some(row => row.surface === 'kids-proof'));
      assert.ok(contexts.some(row => row.surface === 'immersive-hotspot'));
      if (capture) {
        fs.mkdirSync(path.join(output, 'screenshots'), { recursive: true });
        await page.locator('#love-hurts').screenshot({ path: path.join(output, 'screenshots', 'love-hurts-' + width + '.png') });
        await page.locator('#imagery-contexts').screenshot({ path: path.join(output, 'screenshots', 'contexts-' + width + '.png') });
      }
    }
    return { width, dpr, cards, contexts, encoded_card_bytes: cards.reduce((sum, card) => sum + card.encoded_bytes, 0), errors, overflow };
  } finally { await page.close(); }
}

(async () => {
  fs.writeFileSync(path.join(output, 'contexts.html'), execFileSync('php', ['tools/v2-runtime/render-imagery-contexts.php'], { cwd: root }));
  const browser = await chromium.launch({ headless: true });
  try {
    const rows = [];
    for (const [width, dpr] of matrix) {
      const before = await observe(browser, 'baseline-before.html', width, dpr);
      const after = await observe(browser, 'contexts.html', width, dpr, dpr === 1);
      rows.push({ ...after, previous_encoded_card_bytes: before.encoded_card_bytes, saved_encoded_card_bytes: before.encoded_card_bytes - after.encoded_card_bytes });
    }
    const report = { status: 'PASS', scope: 'LOCAL_REAL_TEMPLATE_WITH_OFFLINE_COMMERCE_FIXTURES', authentication: 'NOT_APPLICABLE', rendered_cells: 33 * matrix.length, viewports: rows };
    fs.writeFileSync(path.join(output, 'browser-delivery.json'), JSON.stringify(report, null, 2) + '\n');
    process.stdout.write('PASS 33 exact cards and current imagery consumers at 390/768/1440, DPR 1/2 plus phone DPR3; WebP only, decoded, no overflow/errors\n');
  } finally { await browser.close(); }
})().catch(error => { process.stderr.write(error.stack + '\n'); process.exit(1); });
