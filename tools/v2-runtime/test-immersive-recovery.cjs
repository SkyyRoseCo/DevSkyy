'use strict';

// Synthetic DOM timing controls. No assets are approved and no network is used.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { createRequire } = require('node:module');
const theme = path.resolve(__dirname, '../../wordpress-theme/skyyrose-flagship-2');
const { JSDOM } = createRequire(path.join(theme, 'package.json'))('jsdom');

function fixture(source, { poster = true, complete = false, width = 0, reduced = true, saveData = false, chapterComplete = false } = {}) {
  const dom = new JSDOM(`<main class="sr2-immersive" data-poster-state="${poster ? 'loading' : 'unavailable'}"><canvas class="sr2-immersive__canvas"></canvas><div class="sr2-immersive__poster">${poster ? '<img src="/synthetic-role-bound-hero.webp">' : ''}</div><p class="sr2-immersive__scene-status screen-reader-text"></p><article class="sr2-immersive__chapter"><div class="sr2-immersive__chapter-media"><img src="/synthetic-chapter.webp"><a class="sr2-immersive__hotspot" data-scene-product="true" data-sku="sg-005" style="--hotspot-x:50%;--hotspot-y:40%" href="/product/sg-005/"><span class="sr2-immersive__hotspot-copy"><small>Piece in this scene</small></span></a></div><div class="sr2-chapter__copy"></div></article><script class="sr2-immersive__config" type="application/json">{}</script></main>`, { url: 'http://127.0.0.1:18362/', runScripts: 'outside-only', pretendToBeVisual: true });
  const { window } = dom;
  window.matchMedia = () => ({ matches: reduced, addEventListener() {}, removeEventListener() {} });
  Object.defineProperty(window.navigator, 'connection', { value: { saveData } });
  window.requestAnimationFrame = () => 0;
  const image = window.document.querySelector('.sr2-immersive__poster img');
  const chapter = window.document.querySelector('.sr2-immersive__chapter-media img');
  let loadedWidth = width;
  if (image) {
    Object.defineProperty(image, 'complete', { get: () => complete });
    Object.defineProperty(image, 'naturalWidth', { get: () => loadedWidth });
  }
  Object.defineProperty(chapter, 'complete', { get: () => chapterComplete });
  Object.defineProperty(chapter, 'naturalWidth', { get: () => 0 });
  window.eval(source);
  return { window, image, chapter, root: window.document.querySelector('main'), status: window.document.querySelector('.sr2-immersive__scene-status'), load() { loadedWidth = 1200; image.dispatchEvent(new window.Event('load')); }, close() { window.close(); } };
}

for (const artifact of ['immersive.js', 'immersive.min.js']) {
  const source = fs.readFileSync(path.join(theme, 'assets/js', artifact), 'utf8');
  for (const options of [{ reduced: true }, { reduced: false }, { reduced: false, saveData: true }]) {
    test(`${artifact}: cached and later poster failures recover identically ${JSON.stringify(options)}`, () => {
      for (const cached of [true, false]) {
        const f = fixture(source, { ...options, complete: cached });
        try {
          if (!cached) f.image.dispatchEvent(new f.window.Event('error'));
          assert.equal(f.image.hidden, true);
          assert.equal(f.status.classList.contains('screen-reader-text'), false);
          assert.match(f.status.textContent, /unavailable/);
          assert.doesNotMatch(f.status.textContent, /is ready/);
        } finally { f.close(); }
      }
    });
  }
  test(`${artifact}: ready requires a loaded positive-size poster; absent remains unavailable`, () => {
    const f = fixture(source);
    try {
      assert.match(f.status.textContent, /Loading/);
      f.load();
      assert.match(f.status.textContent, /static story scene is ready/);
    } finally { f.close(); }
    const absent = fixture(source, { poster: false });
    try { assert.match(absent.status.textContent, /unavailable/); } finally { absent.close(); }
  });
  test(`${artifact}: failed chapter stays accessible without borrowing the hero role`, () => {
    for (const posterSucceeds of [true, false]) {
      const f = fixture(source);
      try {
        const before = f.chapter.getAttribute('src');
        f.chapter.dispatchEvent(new f.window.Event('error'));
        if (posterSucceeds) f.load(); else f.image.dispatchEvent(new f.window.Event('error'));
        assert.equal(f.chapter.hidden, true);
        assert.equal(f.chapter.getAttribute('src'), before);
        assert.match(f.chapter.nextElementSibling.textContent, /image unavailable/);
        const related = f.root.querySelector('.sr2-immersive__related-products a');
        assert.equal(related.getAttribute('href'), '/product/sg-005/');
        assert.equal(related.getAttribute('data-sku'), 'sg-005');
        assert.equal(related.hasAttribute('style'), false);
        assert.equal(related.hasAttribute('data-scene-product'), false);
        assert.match(related.textContent, /Explore collection piece/);
        assert.equal(f.root.querySelectorAll('.sr2-immersive__hotspot').length, 0);
      } finally { f.close(); }
    }
  });
  test(`${artifact}: cached failed chapter recovers before any later image event`, () => {
    const f = fixture(source, { chapterComplete: true });
    try {
      assert.equal(f.chapter.hidden, true);
      assert.match(f.chapter.nextElementSibling.textContent, /image unavailable/);
      assert.equal(f.chapter.getAttribute('src'), '/synthetic-chapter.webp');
      assert.equal(f.root.querySelectorAll('[data-scene-product]').length, 0);
      assert.equal(f.root.querySelector('.sr2-immersive__related-products a').hasAttribute('style'), false);
      f.load();
      assert.equal(f.chapter.hidden, true);
    } finally { f.close(); }
  });
}
