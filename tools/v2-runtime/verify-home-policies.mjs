/**
 * Home policy and commerce regression for the critical-rendering repair.
 *
 * Checks, against a running Home route, that the repair did not change any
 * user-facing policy: no-JS coherence, prefers-reduced-motion, Save-Data,
 * hidden-tab pause, pause/play control, poster-first continuity, the rotating
 * header mark, Ask Skyy making no 3D request on load, and the commerce
 * journey (Product Card → Quick View → size → native variation → Add to Bag,
 * Search, Bag, Menu).
 *
 * Usage: node tools/v2-runtime/verify-home-policies.mjs --base=http://host [--browser=chromium|webkit] [--json=out.json]
 * Exit 1 on any failed check.
 */
import { loadPlaywright } from './load-playwright.mjs';
import fs from 'node:fs';
const playwright = loadPlaywright();

const args = Object.fromEntries(process.argv.slice(2).map((a) => { const m = a.match(/^--([^=]+)(?:=(.*))?$/); return m ? [m[1], m[2] ?? true] : [a, true]; }));
const base = String(args.base || '').replace(/\/$/, '');
if (!base) { console.error('--base is required'); process.exit(2); }
const browserName = String(args.browser || 'chromium');
const checks = [];
const check = (name, ok, detail) => { checks.push({ name, ok: Boolean(ok), detail }); console.log(`${ok ? 'PASS' : 'FAIL'}  ${name}${detail ? '  — ' + (typeof detail === 'string' ? detail : JSON.stringify(detail)) : ''}`); };
const url = () => `${base}/?vp=${Date.now()}`;

const heroState = (page) => page.evaluate(() => {
  const el = document.querySelector('[data-recovery-hero]');
  const video = el?.querySelector('[data-recovery-hero-video]');
  const poster = el?.querySelector('img');
  const button = el?.querySelector('[data-recovery-motion-toggle]');
  const cs = (n) => (n ? getComputedStyle(n) : null);
  return {
    hasHero: Boolean(el), ready: el?.classList.contains('is-hero-video-ready') || false, motion: el?.dataset.recoveryMotion || null,
    video: video ? { paused: video.paused, currentSrc: video.currentSrc, readyState: video.readyState, hasSrc: Boolean(video.currentSrc), autoplayAttr: video.hasAttribute('autoplay'), playsinline: video.hasAttribute('playsinline'), muted: video.muted } : null,
    poster: poster ? { visible: cs(poster).visibility !== 'hidden' && cs(poster).display !== 'none' && Number(cs(poster).opacity) > 0, complete: poster.complete, w: poster.getBoundingClientRect().width } : null,
    button: button ? { hidden: button.hidden, text: button.textContent.trim(), pressed: button.getAttribute('aria-pressed') } : null,
    mark: (() => { const m = document.querySelector('.sr2-brand-media'); if (!m) return null; const r = m.getBoundingClientRect(); const v = m.querySelector('video'); const i = m.querySelector('img'); return { w: r.width, h: r.height, video: v ? { paused: v.paused, hasSrc: Boolean(v.currentSrc) } : null, img: i ? { complete: i.complete } : null }; })(),
    headerHeight: document.querySelector('.sr2-house-header')?.getBoundingClientRect().height || 0,
    askSkyy: (() => { const a = document.querySelector('#skyyrose-mascot-recall'); return a ? { visible: a.getBoundingClientRect().width > 0, text: a.textContent.trim().slice(0, 40) } : null; })(),
  };
});

const browser = await playwright[browserName].launch();
try {
  // 1. Baseline (JS on, motion allowed).
  {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, reducedMotion: 'no-preference' });
    const page = await ctx.newPage();
    const requests = [];
    page.on('request', (r) => requests.push(r.url()));
    await page.goto(url(), { waitUntil: 'load' });
    await page.waitForTimeout(2500);
    const s = await heroState(page);
    check('hero present with poster-first continuity', s.hasHero && s.poster && s.poster.complete, s.poster);
    check('video is muted + playsinline (autoplay policy)', s.video && s.video.muted && s.video.playsinline, s.video);
    // Some engines (Playwright WebKit, headless or headed) deny an unattended muted play(); the controller then keeps the
    // poster and offers "Play motion". Both paths are policy-correct; the checks follow whichever path the engine took.
    const denied = Boolean(s.button && s.button.pressed === 'true' && s.video && s.video.paused);
    if (denied) {
      check('engine denied unattended autoplay: poster stays, film hidden, Play control offered', !s.ready && s.poster.visible && !s.button.hidden && /play/i.test(s.button.text), { engine: browserName, button: s.button });
      await page.click('[data-recovery-motion-toggle]');
      await page.waitForTimeout(1200);
      const played = await heroState(page);
      check('Play control starts the film after denial (reveal after a frame)', played.video && !played.video.paused && played.ready && played.motion === 'running' && /pause/i.test(played.button.text), { motion: played.motion, ready: played.ready, text: played.button?.text });
      await page.click('[data-recovery-motion-toggle]');
      await page.waitForTimeout(300);
      const paused = await heroState(page);
      check('pause control pauses the film', paused.video && paused.video.paused && paused.motion === 'paused' && /play/i.test(paused.button.text), { motion: paused.motion, text: paused.button?.text });
      await page.click('[data-recovery-motion-toggle]');
      await page.waitForTimeout(600);
    } else {
      check('film reveals only after a frame (is-hero-video-ready + playing)', s.ready && s.video && !s.video.paused && s.video.readyState >= 2, { ready: s.ready, video: s.video });
      check('pause/play control visible when motion allowed', s.button && !s.button.hidden && /pause/i.test(s.button.text), s.button);
      await page.click('[data-recovery-motion-toggle]');
      await page.waitForTimeout(300);
      const paused = await heroState(page);
      check('pause control pauses the film', paused.video && paused.video.paused && paused.motion === 'paused' && /play/i.test(paused.button.text), { motion: paused.motion, text: paused.button?.text });
      await page.click('[data-recovery-motion-toggle]');
      await page.waitForTimeout(500);
    }
    const resumed = await heroState(page);
    check('play control resumes the film', resumed.video && !resumed.video.paused && resumed.motion === 'running', { motion: resumed.motion });
    check('rotating header mark has a stable container', s.mark && s.mark.w > 0 && s.mark.h > 0 && s.headerHeight > 0, s.mark);
    const rail = await page.evaluate(() => { const r = document.querySelector('#sr2-archive-worlds [data-recovery-rail]'); const c = r?.querySelector('.sr2-recovery-controls'); return r ? { controlsHidden: c ? c.hidden : null, count: r.querySelector('[data-recovery-count]')?.textContent.trim() || '', prevDisabled: r.querySelector('[data-recovery-prev]')?.disabled ?? null, nextDisabled: r.querySelector('[data-recovery-next]')?.disabled ?? null } : null; });
    check('collection rail bound by the inline controller (controls shown, count set, first item current)', rail && rail.controlsHidden === false && /^01 \/ 0[2-9]$/.test(rail.count) && rail.prevDisabled === true && rail.nextDisabled === false, rail);
    const markWasPlaying = Boolean(s.mark && s.mark.video && !s.mark.video.paused);
    const threeD = requests.filter((u) => /\.(glb|gltf|wasm|hdr|ktx2)(\?|$)|three|babylon|skyy-3d/i.test(u));
    check('Ask Skyy makes no 3D request on load', threeD.length === 0, threeD.slice(0, 5));
    check('Ask Skyy launcher present in header', s.askSkyy && s.askSkyy.visible, s.askSkyy);
    // Hidden tab → pause; visible → resume.
    await page.evaluate(() => { Object.defineProperty(document, 'hidden', { configurable: true, get: () => true }); document.dispatchEvent(new Event('visibilitychange')); });
    await page.waitForTimeout(300);
    const hidden = await heroState(page);
    check('hidden document pauses the film', hidden.video && hidden.video.paused && hidden.motion === 'paused', { motion: hidden.motion });
    check('hidden document pauses the rotating header mark', !markWasPlaying || (hidden.mark && hidden.mark.video && hidden.mark.video.paused), { markWasPlaying, mark: hidden.mark });
    await page.evaluate(() => { Object.defineProperty(document, 'hidden', { configurable: true, get: () => false }); document.dispatchEvent(new Event('visibilitychange')); });
    await page.waitForTimeout(600);
    const shown = await heroState(page);
    check('visible document resumes the film', shown.video && !shown.video.paused && shown.motion === 'running', { motion: shown.motion });
    check('visible document resumes the rotating header mark', !markWasPlaying || (shown.mark && shown.mark.video && !shown.mark.video.paused), { markWasPlaying, mark: shown.mark });
    await ctx.close();
  }
  // 2. prefers-reduced-motion: reduce → no film, poster stays, control hidden.
  {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, reducedMotion: 'reduce' });
    const page = await ctx.newPage();
    const media = [];
    page.on('request', (r) => { if (r.resourceType() === 'media' || /collection-heroes\/.*\.(webm|mp4)/.test(r.url())) media.push(r.url()); });
    await page.goto(url(), { waitUntil: 'load' });
    await page.waitForTimeout(2000);
    const s = await heroState(page);
    check('reduced motion: film not revealed, poster visible', !s.ready && s.poster && s.poster.visible && s.motion === 'paused', { ready: s.ready, motion: s.motion });
    check('reduced motion: pause/play control hidden', s.button && s.button.hidden, s.button);
    check('reduced motion: hero film not fetched', media.length === 0, media.slice(0, 3));
    await ctx.close();
  }
  // 3. Save-Data → same as reduced motion (controller reads navigator.connection.saveData).
  {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
    await ctx.addInitScript(() => { Object.defineProperty(navigator, 'connection', { configurable: true, get: () => ({ saveData: true, effectiveType: '3g', addEventListener() {} }) }); });
    const page = await ctx.newPage();
    const media = [];
    page.on('request', (r) => { if (r.resourceType() === 'media' || /collection-heroes\/.*\.(webm|mp4)/.test(r.url())) media.push(r.url()); });
    await page.goto(url(), { waitUntil: 'load' });
    await page.waitForTimeout(2000);
    const s = await heroState(page);
    check('Save-Data: film not revealed, control hidden', !s.ready && s.motion === 'paused' && s.button && s.button.hidden, { ready: s.ready, motion: s.motion, button: s.button });
    check('Save-Data: hero film not fetched', media.length === 0, media.slice(0, 3));
    await ctx.close();
  }
  // 4. No JavaScript → coherent styled first view from the inline contract, poster shown, no film.
  {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, javaScriptEnabled: false });
    const page = await ctx.newPage();
    const errors = [];
    page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
    await page.goto(url(), { waitUntil: 'load' });
    await page.waitForTimeout(1000);
    const s = await page.evaluate(() => {
      const hero = document.querySelector('.sr2-archive-scene'); const header = document.querySelector('.sr2-house-header'); const title = document.querySelector('.sr2-archive-scene h1'); const cta = document.querySelector('.sr2-archive-scene__actions a, .sr2-archive-scene__actions .sr2-control');
      const poster = document.querySelector('[data-recovery-hero] img'); const video = document.querySelector('[data-recovery-hero-video]');
      const rect = (n) => (n ? n.getBoundingClientRect() : null);
      return { header: rect(header)?.height, heroH: rect(hero)?.height, titleFont: title ? getComputedStyle(title).fontFamily : null, titleSize: title ? parseFloat(getComputedStyle(title).fontSize) : 0, cta: rect(cta)?.height, poster: poster ? { complete: poster.complete, w: rect(poster).width } : null, videoSrc: video ? video.currentSrc : null, noscriptMascot: Boolean(document.querySelector('#skyy-hero-stage noscript')), styles: document.querySelectorAll('link[rel=stylesheet]').length, inlineContract: Boolean(document.querySelector('#skyyrose2-critical-home')) };
    });
    check('no-JS: header, hero and CTA laid out from the inline contract', s.header > 40 && s.heroH > 400 && s.cta > 40 && s.inlineContract, s);
    check('no-JS: title set in the display face', /Archivo/.test(s.titleFont) && s.titleSize > 40, { font: s.titleFont, size: s.titleSize });
    check('no-JS: poster shown, no film source set', s.poster && s.poster.w > 0 && !s.videoSrc, { poster: s.poster, videoSrc: s.videoSrc });
    check('no-JS: no console errors', errors.length === 0, errors.slice(0, 3));
    await ctx.close();
  }
  // 5. Commerce: Product Card → Quick View → size → native variation → Add to Bag; Search; Bag; Menu.
  try {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
    const page = await ctx.newPage();
    const errors = [];
    page.on('pageerror', (e) => errors.push(String(e.message).slice(0, 160)));
    page.on('console', (m) => { if (m.type() === 'error' && !/favicon|Prefetch request denied: URL must be secure/.test(m.text())) errors.push(m.text().slice(0, 160)); });
    await page.goto(url(), { waitUntil: 'load' });
    await page.waitForTimeout(1500);
    const opener = page.locator('[data-quick-view]').first();
    check('product card exposes a Quick View opener', (await opener.count()) > 0);
    await opener.scrollIntoViewIfNeeded();
    await opener.click();
    const dialog = page.locator('#sr2-quick-view-dialog');
    await dialog.waitFor({ state: 'visible', timeout: 15000 }).catch(() => {});
    const form = dialog.locator('form.cart, form.variations_form');
    await form.first().waitFor({ state: 'visible', timeout: 15000 }).catch(() => {});
    check('Quick View opens with the native purchase form', await dialog.isVisible() && (await form.count()) > 0);
    const sizeSelect = form.locator('select[name^="attribute_"]').first();
    const hasSize = (await sizeSelect.count()) > 0;
    if (hasSize) {
      const options = await sizeSelect.locator('option').evaluateAll((o) => o.map((x) => x.value).filter(Boolean));
      await sizeSelect.selectOption(options[0]);
      await page.waitForTimeout(800);
      const variation = await form.evaluate((f) => ({ id: f.querySelector('input[name="variation_id"]')?.value || '', disabled: f.querySelector('.single_add_to_cart_button')?.classList.contains('disabled') || false, hidden: f.querySelector('.single_variation_wrap')?.style.display === 'none' }));
      check('size selection resolves a native variation (wc-add-to-cart-variation)', variation.id && variation.id !== '0' && !variation.disabled, variation);
    } else {
      check('purchase form is simple (no size attribute) — variation step not applicable', true);
    }
    const before = await page.locator('.sr2-header__bag span, .sr2-header__bag-count').first().textContent().catch(() => '');
    const [response] = await Promise.all([
      page.waitForResponse((r) => /add-to-cart|wc-ajax|\/cart\/|checkout/.test(r.url()) && r.request().method() === 'POST', { timeout: 20000 }).catch(() => null),
      form.locator('.single_add_to_cart_button').first().click(),
    ]);
    await page.waitForTimeout(2500);
    const bagAfter = await page.evaluate(() => ({ count: document.querySelector('.sr2-header__bag span, .sr2-header__bag-count')?.textContent.trim() || '', status: document.querySelector('[data-quick-view-status]')?.textContent.trim() || '', url: location.pathname, cartItems: document.querySelectorAll('.woocommerce-cart-form__cart-item, .wc-block-cart-items__row, .mini_cart_item').length }));
    check('Add to Bag completes (POST accepted, bag count or cart reflects the item)', Boolean(response) && (bagAfter.count !== before || bagAfter.cartItems > 0 || /bag|cart|added/i.test(bagAfter.status)), { post: response ? `${response.status()} ${response.url().slice(0, 80)}` : null, before, after: bagAfter });
    // Search: the opener lives in the header direct links (desktop) or inside the menu nav (mobile); it opens #sr2-search-dialog.
    await page.goto(url(), { waitUntil: 'load' });
    let opened = false;
    for (const opener of await page.locator('[data-search-open]').all()) { if (await opener.isVisible()) { await opener.click(); opened = true; break; } }
    if (!opened) { await page.locator('.sr2-header__menu').first().click(); await page.waitForTimeout(400); const inMenu = page.locator('#sr2-menu [data-search-open]').first(); if ((await inMenu.count()) > 0) { await inMenu.click(); opened = true; } }
    await page.waitForTimeout(500);
    const searchInput = page.locator('#sr2-global-search, input[type="search"], input[name="s"]').first();
    const hasSearch = opened && (await searchInput.count()) > 0 && (await searchInput.isVisible());
    if (hasSearch) { await searchInput.fill('hoodie'); await searchInput.press('Enter'); await page.waitForLoadState('load'); }
    const searchResult = hasSearch ? await page.evaluate(() => ({ url: location.search, results: document.querySelectorAll('.sr2-c-editorial-card, .product, article').length })) : { opened };
    check('Search opens its dialog and returns a results page', hasSearch && searchResult && /s=hoodie/.test(searchResult.url) && searchResult.results > 0, searchResult);
    // Bag
    await page.goto(url(), { waitUntil: 'load' });
    await page.locator('.sr2-header__bag').first().click();
    await page.waitForTimeout(1500);
    const bag = await page.evaluate(() => ({ url: location.pathname, dialogOpen: Boolean(document.querySelector('dialog[open], .sr2-bag[aria-hidden="false"], .sr2-bag.is-open')), cartForm: Boolean(document.querySelector('.woocommerce-cart-form, .wc-block-cart, .sr2-bag')) }));
    check('Bag opens (mini-bag or cart route)', bag.dialogOpen || /cart|bag/.test(bag.url) || bag.cartForm, bag);
    // Menu
    await page.goto(url(), { waitUntil: 'load' });
    await page.locator('.sr2-header__menu').first().click();
    await page.waitForTimeout(600);
    const menu = await page.evaluate(() => { const nav = document.querySelector('#sr2-menu'); const btn = document.querySelector('.sr2-header__menu'); return { expanded: btn?.getAttribute('aria-expanded'), visible: nav ? getComputedStyle(nav).visibility !== 'hidden' && getComputedStyle(nav).display !== 'none' && nav.getBoundingClientRect().width > 0 : false, links: nav ? nav.querySelectorAll('a').length : 0 }; });
    check('Menu opens with links', menu.expanded === 'true' && menu.visible && menu.links > 0, menu);
    check('commerce journey: no page/console errors', errors.length === 0, errors.slice(0, 4));
    await ctx.close();
  } catch (error) { check('commerce journey completed without a harness error', false, String(error.message).slice(0, 300)); }
} finally { await browser.close(); }
const failed = checks.filter((c) => !c.ok);
if (args.json) fs.writeFileSync(String(args.json), JSON.stringify({ base, browser: browserName, checkedAt: new Date().toISOString(), checks }, null, 2));
console.log(`\n${failed.length === 0 ? 'HOME POLICIES: PASS' : `HOME POLICIES: FAIL (${failed.length})`} — ${checks.length} checks`);
process.exit(failed.length === 0 ? 0 : 1);
