const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const { createRequire } = require('node:module');
const theme = path.resolve(__dirname, '../../wordpress-theme/skyyrose-flagship-2');
const { JSDOM } = createRequire(path.join(theme, 'package.json'))('jsdom');

for (const asset of ['premium-commerce.js', 'premium-commerce.min.js']) {
  test(`${asset}: a missing preview image keeps navigation usable`, async () => {
    const dom = new JSDOM(`<button data-sr2-menu aria-expanded="false"></button>
      <nav class="sr2-house-nav__collections"><div class="sr2-house-nav__previews">
      <article class="sr2-house-nav__preview-entry"><a href="/collections/signature/">
      <span>Signature</span></a><button hidden>Preview</button></article></div></nav>`,
      { runScripts: 'outside-only', url: 'https://example.test/' });
    const { window } = dom;
    const errors = [];
    const rejected = error => errors.push(error);
    process.on('unhandledRejection', rejected);
    try {
      window.eval(fs.readFileSync(path.join(theme, 'assets/js', asset), 'utf8'));
      window.document.querySelector('[data-sr2-menu]').setAttribute('aria-expanded', 'true');
      await new Promise(resolve => setTimeout(resolve, 20));
      const stage = window.document.querySelector('#sr2-nav-preview-stage');
      assert.equal(errors.length, 0);
      assert.equal(stage.dataset.state, 'unavailable');
      assert.equal(stage.hasAttribute('aria-busy'), false);
      assert.equal(stage.querySelector('img').hidden, true);
      assert.equal(stage.querySelector('figcaption').textContent, 'Signature');
      assert.equal(window.document.querySelector('a').pathname, '/collections/signature/');
    } finally {
      process.removeListener('unhandledRejection', rejected);
      window.close();
    }
  });
}
