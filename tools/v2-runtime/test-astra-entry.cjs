'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const theme = path.resolve(__dirname, '../../wordpress-theme/skyyrose-flagship-2');
const read = file => fs.readFileSync(path.join(theme, file), 'utf8');

test('valid card images keep their error label hidden in delivered CSS', () => {
  for (const file of ['visual-recovery.css', 'visual-recovery.min.css']) {
    const css = read('assets/css/' + file);
    assert.match(css, /\.sr2-c-editorial-card__media-unavailable\[hidden\]\s*\{\s*display:\s*none\s*;?\s*\}/);
  }
});

test('immersive recovery binds editorial media, never product images', () => {
  const listeners = [];
  const editorial = { dataset: {}, addEventListener: (event, handler) => listeners.push(handler) };
  const product = { dataset: {}, src: '/exact-sku.webp', alt: 'Exact garment' };
  const poster = { src: '/world.webp' };
  const root = {
    querySelectorAll(selector) {
      assert.equal(selector, '.sr2-immersive__chapter-media > img');
      return [editorial];
    },
  };
  const source = read('assets/js/immersive.js');
  const start = source.indexOf('function recoverImage(');
  const end = source.indexOf('function updateProgress()', start);
  assert.ok(start > 0 && end > start);
  vm.runInNewContext(source.slice(start, end), { root, poster });
  listeners[0]();
  assert.equal(editorial.src, '/world.webp');
  assert.equal(product.src, '/exact-sku.webp');
  assert.equal(product.alt, 'Exact garment');
});

test('immersive shell has the shared skip target and immediate native commerce', () => {
  const source = read('template-parts/immersive/world.php');
  assert.match(source, /<main id="primary" tabindex="-1"/);
  const entry = source.slice(
    source.indexOf('sr2-immersive__entry-copy'),
    source.indexOf('sr2-immersive__scene-status')
  );
  assert.match(entry, /skyyrose2_collection_url\( \$collection_slug \)/);
  assert.match(entry, /Shop collection/);
  assert.match(entry, /href="#chapter-/);
});

test('Kids keeps both world and shopping entries plus its editorial story', () => {
  // 2.5.0 arrival: one primary action to the shop band, one quiet link into the chapters
  // (#world); the immersive world entry moved to the last chapter, the story keeps its own part.
  const arrival = read('template-parts/collections/arrival.php');
  assert.match(arrival, /class="sr2-control sr2-control--primary" href="#shop"/);
  assert.match(arrival, /\$arrival\['hero_cta'\]/);
  assert.match(arrival, /class="sr2-editorial-link" href="#world"/);
  assert.match(arrival, /\$arrival\['world_cta'\]/);
  const chapters = read('template-parts/collections/chapters.php');
  assert.match(chapters, /id="world"/);
  assert.match(chapters, /skyyrose2_immersive_url\( \$chapter_slug \)/);
  const world = read('template-parts/collections/world.php');
  assert.match(world, /<section id="shop"/);
  assert.match(world, /get_template_part\( 'template-parts\/collections\/story'/);
});
