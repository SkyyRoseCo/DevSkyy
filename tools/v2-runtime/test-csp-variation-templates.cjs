const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const php = fs.readFileSync(path.resolve(__dirname, '../../wordpress-theme/skyyrose-flagship-2/inc/performance.php'), 'utf8');
const code = php.split("<<<'SKYYROSE_VARIATION_TEMPLATES'\n")[1].split('\nSKYYROSE_VARIATION_TEMPLATES;')[0];
function fixture(text) {
  const original = () => { throw Error('Dynamic compiler must not run'); };
  original.cache = {};
  const context = vm.createContext({ window: { wp: { template: original } }, document: { getElementById: () => ({ textContent: text }) } }, { codeGeneration: { strings: false, wasm: false } });
  vm.runInContext(code, context);
  assert.equal(context.window.wp.template, original);
  return original.cache;
}
test('native Woo HTML interpolates with dynamic compilation disabled', () => {
  const c = fixture('<div>{{{ data.variation.price_html }}}</div>');
  assert.equal(c['variation-template']({ variation: { price_html: '<span>$25</span>' } }), '<div><span>$25</span></div>');
});
test('escaped tokens are HTML escaped and localized unavailable markup survives', () => {
  assert.equal(fixture('{{ data.variation.variation_description }}')['variation-template']({ variation: { variation_description: '<b>&"\'' } }), '&lt;b&gt;&amp;&quot;&#39;');
  assert.equal(fixture('<p role="alert">Indisponible</p>')['unavailable-variation-template']({}), '<p role="alert">Indisponible</p>');
});
test('arbitrary expressions and unapproved fields fail closed', () => {
  for (const text of ['<# data.run() #>', '{{{ data.secret }}}', '{{{ data.variation.unknown }}}', '{{ data.variation.price_html }}}']) {
    assert.throws(() => fixture(text)['variation-template']({ variation: {} }), /Unsupported/);
  }
});
