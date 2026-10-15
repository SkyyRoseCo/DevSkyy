/** Local, read-only cinematic integration verification. No cart/order/payment writes. */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { requireQa, base, out } = require('./runtime.cjs');
const { beginRun } = require('./run-evidence.cjs');
const run = beginRun(path.join(out, 'cinematic-integration.json'));
const rows = [];
const theme = path.resolve(__dirname, '../../../wordpress-theme/skyyrose-flagship-2');
const approved = JSON.parse(fs.readFileSync(path.join(theme, 'data/approved-scroll-world-scenes.json'))).scenes;
const slugs = ['signature', 'black-rose', 'love-hurts', 'kids-capsule'];
const screenshots = [];
const sceneIDs = [];
const productURLs = [];
const shopProductURLs = [];
const townLinks = [];

(async () => {
  const { chromium } = requireQa('playwright');
  const browser = await chromium.launch({ args: ['--use-angle=metal', '--enable-gpu'] });
  async function context(options = {}, fault = '') {
    const c = await browser.newContext({ viewport: { width: 390, height: 844 }, ...options });
    if (fault === 'save-data')
      await c.addInitScript(() => Object.defineProperty(navigator.connection, 'saveData', { get: () => true }));
    await c.route('**/*', route => {
      const url = new URL(route.request().url());
      if (url.origin !== base) return route.abort();
      if (fault === 'video-failure' && /\.mp4(?:$|\?)/.test(url.href)) return route.fulfill({ status: 404, body: '' });
      return route.continue();
    });
    const p = await c.newPage();
    p.setDefaultTimeout(15000);
    const errors = [],
      videos = [];
    p.on('pageerror', error => errors.push(error.message));
    p.on('request', request => {
      if (/\.mp4(?:$|\?)/.test(request.url())) videos.push(request.url());
    });
    return { c, p, errors, videos };
  }
  async function navigate(p, route) {
    assert.equal(new URL(route, base).origin, base);
    const response = await p.goto(new URL(route, base).href);
    assert.equal(response.status(), 200, route);
    assert.equal(new URL(p.url()).origin, base);
  }
  async function shot(p, name) {
    const target = path.join(out, name);
    await p.screenshot({ path: target });
    screenshots.push(name);
  }
  async function railKeyboard(p) {
    const track = p.locator('[data-recovery-track]').first();
    if (!(await track.count())) return null;
    await track.scrollIntoViewIfNeeded();
    await track.focus();
    const rail = track.locator('xpath=ancestor::*[@data-recovery-rail][1]');
    const total = await track.locator(':scope > *').count();
    const count = rail.locator('[data-recovery-count]');
    for (const [key, expected] of [
      ['End', total],
      ['Home', 1],
      ['ArrowRight', 2],
      ['ArrowLeft', 1],
    ]) {
      await p.keyboard.press(key);
      await p.waitForFunction(
        ({ expected, total }) =>
          document.querySelector('[data-recovery-count]').textContent ===
          `${String(expected).padStart(2, '0')} / ${String(total).padStart(2, '0')}`,
        { expected, total }
      );
      assert.equal(await track.evaluate(el => document.activeElement === el), true);
    }
    return { total, finalCount: await count.textContent(), keys: 'End/Home/ArrowRight/ArrowLeft' };
  }
  async function quickView(p, card) {
    const trigger = card.locator('[data-quick-view]');
    const facts = await trigger.evaluate(el => ({ ...el.dataset }));
    await trigger.focus();
    await p.keyboard.press('Enter');
    const dialog = p.locator('#sr2-quick-view-dialog');
    await dialog.waitFor({ state: 'visible' });
    for (const field of ['name', 'collection', 'price', 'availability']) {
      assert.equal(
        await dialog.locator(`[data-quick-view-${field}]`).textContent(),
        facts['quickView' + field[0].toUpperCase() + field.slice(1)]
      );
    }
    assert.equal(await dialog.locator('[data-quick-view-url]').getAttribute('href'), facts.quickViewUrl);
    const image = dialog.locator('[data-quick-view-image]');
    await image.evaluate(el => el.decode());
    assert.equal(await image.getAttribute('src'), facts.quickViewImage);
    await p.keyboard.press('Escape');
    await dialog.waitFor({ state: 'hidden' });
    assert(await trigger.evaluate(el => document.activeElement === el));
    return facts.quickViewName;
  }
  try {
    // Every accepted collection card and Quick View, with fresh reduced-motion pages.
    const { c, p, errors, videos } = await context({ reducedMotion: 'reduce' });
    for (const slug of slugs) {
      await navigate(p, '/collections/' + slug + '/');
      const scenes = await p
        .locator('[data-scene-id]')
        .evaluateAll(elements => elements.map(el => el.dataset.sceneId.toUpperCase()));
      assert.equal(scenes.length, slug === 'kids-capsule' ? 0 : 3, slug);
      for (const id of scenes) {
        assert.equal(approved[id]?.collection, slug);
        sceneIDs.push(id);
      }
      if (slug === 'black-rose') {
        const links = await p
          .locator('.sr2-town-line__directory a')
          .evaluateAll(elements =>
            elements.map(el => ({ sku: el.querySelector('.sr2-town-line__sku').textContent.trim(), url: el.href }))
          );
        assert.equal(links.length, 8, 'Preserved Town Line native directory');
        for (const link of links) {
          assert.equal(new URL(link.url).origin, base);
          const response = await c.request.get(link.url, { maxRedirects: 0 });
          assert.equal(response.status(), 200);
          assert.equal(new URL(response.url()).origin, base);
          townLinks.push(link);
        }
      }
      const keyboard = await railKeyboard(p);
      const cards = p.locator('main .sr2-c-editorial-card');
      const collectionCards = [];
      for (let index = 0; index < (await cards.count()); index++) {
        const card = cards.nth(index);
        await card.scrollIntoViewIfNeeded();
        await card.locator('img').evaluateAll(images => Promise.all(images.map(image => image.decode())));
        const details = await card.evaluate(el => {
          const image = el.querySelector('.sr2-c-editorial-card__product-image');
          const frame = el.querySelector('.sr2-c-editorial-card__frame');
          const window = el.querySelector('.sr2-c-editorial-card__photo-window');
          const css = getComputedStyle(image),
            rect = image.getBoundingClientRect(),
            bounds = window.getBoundingClientRect();
          return {
            id: el.querySelector('.sr2-c-editorial-card__title a').href,
            mediaSource: el.dataset.mediaSource,
            src: image.currentSrc,
            width: image.naturalWidth,
            fit: css.objectFit,
            transform: css.transform,
            containedBox: rect.width <= bounds.width + 1 && rect.height <= bounds.height + 1,
            frameBackground: getComputedStyle(frame).backgroundColor,
            url: el.querySelector('.sr2-c-editorial-card__title a').href,
          };
        });
        assert.equal(details.mediaSource, 'approved-card-front');
        assert(details.width > 0);
        assert.equal(new URL(details.src).origin, base);
        assert.equal(new URL(details.url).origin, base);
        assert.equal(details.fit, 'contain');
        assert.equal(details.transform, 'none');
        assert(details.containedBox);
        assert(
          ['transparent', 'rgba(0, 0, 0, 0)'].includes(details.frameBackground),
          'Opaque frame background: ' + details.id
        );
        const response = await c.request.get(details.url, { maxRedirects: 0 });
        assert.equal(new URL(response.url()).origin, base);
        assert.equal(response.status(), 200);
        details.quickView = await quickView(p, card);
        productURLs.push(details.id);
        collectionCards.push(details);
      }
      assert.deepEqual(errors, []);
      assert.equal(videos.length, 0, 'Reduced-motion page requested video');
      rows.push({ kind: 'collection', slug, scenes, keyboard, cards: collectionCards, videoRequests: 0 });
      console.log('Verified collection', slug, collectionCards.length);
    }
    rows.push({
      kind: 'inventory-count',
      expectedAcceptedCardFronts: 33,
      renderedCollectionCards: productURLs.length,
      uniqueRenderedCards: new Set(productURLs).size,
    });
    assert.deepEqual([...sceneIDs].sort(), Object.keys(approved).sort());
    assert.equal(new Set(sceneIDs).size, 9);
    // Twenty-five core collection cards plus eight preserved Town Line directory links.
    // All thirty-three products must additionally pass full card/Quick View checks in native Shop pagination.
    let shopRoute = '/shop/';
    const visited = new Set();
    while (shopRoute) {
      assert(!visited.has(shopRoute) && visited.size < 6, 'Native pagination must advance within a bounded catalog');
      visited.add(shopRoute);
      await navigate(p, shopRoute);
      const cards = p.locator('main .sr2-c-editorial-card');
      for (const card of await cards.all()) {
        await card.scrollIntoViewIfNeeded();
        const image = card.locator('.sr2-c-editorial-card__product-image');
        await image.evaluate(el => el.decode());
        const media = await image.evaluate(el => ({
          src: el.currentSrc,
          width: el.naturalWidth,
          fit: getComputedStyle(el).objectFit,
          transform: getComputedStyle(el).transform,
        }));
        assert(media.width > 0);
        assert.equal(new URL(media.src).origin, base);
        assert.equal(media.fit, 'contain');
        assert.equal(media.transform, 'none');
        assert.equal(await card.getAttribute('data-media-source'), 'approved-card-front');
        assert.equal(
          await card.locator('.sr2-c-editorial-card__frame').evaluate(el => getComputedStyle(el).backgroundColor),
          'rgba(0, 0, 0, 0)'
        );
        await quickView(p, card);
        shopProductURLs.push(await card.locator('.sr2-c-editorial-card__title a').getAttribute('href'));
      }
      const next = p.locator('.woocommerce-pagination a.next');
      shopRoute = (await next.count()) ? await next.getAttribute('href') : null;
    }
    rows.push({
      kind: 'shop-all-products',
      pages: [...visited],
      productURLs: shopProductURLs,
      acceptedMedia: true,
      contained: true,
      transparentFrames: true,
      keyboardQuickView: true,
    });
    rows.push({ kind: 'town-line-preservation', links: townLinks });
    await c.close();

    // Actual motion and geometry; scene controls must sit outside the artwork.
    for (const width of [390, 768, 1440]) {
      const { c, p, errors } = await context({ viewport: { width, height: width === 390 ? 844 : 1000 } });
      for (const slug of slugs.slice(0, 3)) {
        await navigate(p, '/collections/' + slug + '/');
        const scenes = p.locator('[data-scene-id]');
        for (let i = 0; i < 3; i++) {
          const scene = scenes.nth(i);
          const frame = scene.locator('.sr2-hero-commerce__frame');
          await frame.scrollIntoViewIfNeeded();
          await frame.locator('img').evaluate(el => el.decode());
          const video = scene.locator('[data-collection-scene-motion]');
          await video.waitFor({ state: 'attached' });
          const button = scene.locator('[data-scene-motion-toggle]');
          const mediaRect = await frame.boundingBox(),
            controlRect = await button.boundingBox();
          assert(
            controlRect && mediaRect && controlRect.y >= mediaRect.y + mediaRect.height - 1,
            'Control overlays scene art'
          );
          await p.waitForFunction(
            id => {
              const v = document.querySelector(`[data-scene-id="${id}"] video`);
              return v && !v.paused && v.readyState >= 2;
            },
            await scene.getAttribute('data-scene-id')
          );
          const first = await video.evaluate(el => el.currentTime);
          await p.waitForTimeout(200);
          assert((await video.evaluate(el => el.currentTime)) > first);
          await button.click();
          assert.equal(await video.evaluate(el => el.paused), true);
          await button.click();
          await p.waitForFunction(
            id => !document.querySelector(`[data-scene-id="${id}"] video`).paused,
            await scene.getAttribute('data-scene-id')
          );
          rows.push({
            kind: 'scene-motion',
            width,
            slug,
            id: await scene.getAttribute('data-scene-id'),
            controlsOutsideArt: true,
            pausePlay: true,
          });
        }
      }
      assert.deepEqual(errors, []);
      await c.close();
      console.log('Verified scene motion', width);
    }

    for (const fault of ['save-data', 'video-failure']) {
      const { c, p, errors, videos } = await context({}, fault);
      await navigate(p, '/collections/signature/');
      const scene = p.locator('[data-scene-id]').first();
      await scene.locator('.sr2-hero-commerce__frame').scrollIntoViewIfNeeded();
      await scene.locator('img').evaluate(el => el.decode());
      if (fault === 'save-data') {
        await p.waitForTimeout(400);
        assert.equal(videos.length, 0);
      } else
        await p.waitForFunction(() => document.querySelector('[data-scene-id] [data-scene-motion-toggle]').disabled);
      assert.equal(await scene.locator('img').evaluate(el => el.complete && el.naturalWidth > 0), true);
      assert.deepEqual(errors, []);
      rows.push({ kind: fault, poster: 'loaded', videoRequests: videos.length });
      await c.close();
    }

    // Native navigation and purchase destinations remain without JavaScript.
    {
      const { c, p, videos } = await context({ javaScriptEnabled: false });
      await navigate(p, '/');
      assert.match((await p.locator('main h1').innerText()).replace(/\s+/g, ' ').trim(), /^Skyy Rose$/i);
      const native = p.locator('main a[href$="/collections/signature/"]').first();
      await native.click();
      assert.equal(new URL(p.url()).pathname, '/collections/signature/');
      const qv = p.locator('main [data-quick-view]').first(),
        href = await qv.getAttribute('href');
      await qv.click();
      assert.equal(p.url(), href);
      assert.equal(videos.length, 0);
      rows.push({ kind: 'nojs', collection: '/collections/signature/', product: href, videoRequests: 0 });
      await c.close();
    }

    // Shared shell, header fit and final enlarged mobile Skyy.
    for (const width of [320, 390, 768, 1440]) {
      const { c, p, errors } = await context({
        reducedMotion: 'reduce',
        viewport: { width, height: width === 320 || width === 390 ? 844 : 1000 },
      });
      await navigate(p, '/');
      const header = await p.locator('.sr2-house-header').evaluate(el => {
        const invite = el.querySelector('#skyyrose-mascot-recall');
        const bag = el.querySelector('[data-bag-open]');
        const a = invite.getBoundingClientRect(),
          b = bag.getBoundingClientRect(),
          h = el.getBoundingClientRect();
        return {
          overflow: document.documentElement.scrollWidth > innerWidth,
          position: getComputedStyle(invite).position,
          invite: a.toJSON(),
          bag: b.toJSON(),
          header: h.toJSON(),
          overlap: a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top,
        };
      });
      assert.equal(header.position, 'static');
      assert.equal(header.overlap, false);
      assert.equal(header.overflow, false);
      assert(header.invite.bottom <= header.header.bottom + 1);
      if (width !== 320) {
        await p.locator('[data-sr2-menu]').click();
        await p.waitForFunction(() => document.body.classList.contains('sr2-nav-open'));
        await shot(p, `D-navigation-${width}.png`);
        const search = p.locator('[data-sr2-nav] [data-search-open]');
        await search.click();
        const searchDialog = p.locator('dialog[open]');
        await searchDialog.waitFor({ state: 'visible' });
        await shot(p, `D-search-${width}.png`);
        await p.keyboard.press('Escape');
        await p.locator('[data-bag-open]').click();
        await p.locator('#sr2-bag-dialog').waitFor({ state: 'visible' });
        await shot(p, `D-bag-${width}.png`);
        await p.keyboard.press('Escape');
      }
      assert.deepEqual(errors, []);
      rows.push({ kind: 'header-shell', width, header });
      await c.close();
    }
    {
      const { c, p } = await context();
      await navigate(p, '/');
      await p.locator('#skyyrose-mascot-recall').click();
      await p.waitForFunction(() => window.skyyRoseMascot3D?.isReady(), {}, { timeout: 25000 });
      await p.locator('#skyy-motion-toggle').click();
      const size = await p.locator('.skyyrose-mascot__character').boundingBox();
      assert(size.width >= 119 && size.height >= 184);
      await shot(p, 'cinematic-integration-skyy-390.png');
      rows.push({ kind: 'skyy', width: 390, real3d: true, stage: size });
      await c.close();
    }
    assert.equal(productURLs.length, 25, 'Core collection rails intentionally exclude Town Line jerseys');
    assert.equal(new Set(productURLs).size, 25);
    assert.equal(townLinks.length, 8);
    assert.equal(shopProductURLs.length, 33);
    assert.equal(new Set(shopProductURLs).size, 33);
    assert(productURLs.every(id => shopProductURLs.includes(id)));
    assert(townLinks.every(link => shopProductURLs.includes(link.url)));
    run.pass({
      rows,
      screenshots,
      uniqueCollectionCards: new Set(productURLs).size,
      uniqueShopCards: new Set(shopProductURLs).size,
      preservedTownLineLinks: townLinks.length,
      uniqueApprovedScenes: new Set(sceneIDs).size,
      scope:
        'Local navigation and media only; no order, payment or cart mutations. Performance is not measured during concurrent build work.',
    });
    console.log('PASS cinematic integration');
  } finally {
    await browser.close();
  }
})().catch(error => {
  run.fail(error, { rows, screenshots });
  console.error(error);
  process.exitCode = 1;
});
