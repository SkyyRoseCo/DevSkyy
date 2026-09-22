'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { INPUTS, project, classifySelector, safe, build } = require('./build-archive-style-bundle.cjs');
function fixture(t) {
  const root = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), 'archive-projection-')));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  fs.writeFileSync(path.join(root, 'theme.css'), '.shared{color:red}.sr2-cart{color:blue}.shared{color:green}');
  fs.writeFileSync(path.join(root, 'theme.min.css'), '.shared{color:red}.sr2-cart{color:blue}.shared{color:green}');
  for (const name of INPUTS) fs.writeFileSync(path.join(root, name + '.min.css'), '.' + name + '{background:url(../image.webp)}');
  return root;
}
test('only positive explicit route owners classify; broad/shared/negative selectors remain', () => {
  for (const selector of ['body', '*', '.woocommerce .button', ':not(.sr2-cart)', 'body:has(.sr2-cart)', '.sr2-search-dialog', '.sr2-cartoon', '.sr2-c-action', '.sr2-quick-view', '.sr2-size-guide-dialog']) assert.equal(classifySelector(selector), null, selector);
  for (const selector of ['.sr2-cart__item img', '.sr2-search__result', '.sr2-story h2', '.woocommerce div.product .summary']) assert.ok(classifySelector(selector), selector);
});
test('mixed selector rules, relative URLs, wrappers and all keyframes survive unchanged in order', () => {
  const source = '.shared{color:red}@media(max-width:600px){.sr2-cart{color:blue}.sr2-cart,.sr2-quick-view{color:gold}.shared{background:url(../sot/test.webp)}}@keyframes legacy{to{opacity:0}}.shared{color:green}';
  const result = project(source);
  assert.equal(result.classification.filter(row => row.disposition.startsWith('EXCLUDE')).length, 1);
  assert.match(result.css, /\.sr2-cart,\.sr2-quick-view/);
  assert.match(result.css, /@media/);
  assert.match(result.css, /@keyframes legacy/);
  assert.match(result.css, /url\(\.\.\/sot\/test.webp\)/);
  assert.ok(result.css.indexOf('color:red') < result.css.indexOf('color:gold'));
  assert.ok(result.css.indexOf('color:gold') < result.css.indexOf('color:green'));
});
test('deterministic manifest, complete classification, untouched originals, check never writes', t => {
  const root = fixture(t);
  const source = fs.readFileSync(path.join(root, 'theme.css'));
  const original = fs.readFileSync(path.join(root, 'theme.min.css'));
  const first = build({ root });
  assert.equal(first.classification.length, 3);
  assert.deepEqual(build({ root }), first);
  const stamp = fs.statSync(path.join(root, 'archive-theme.min.css')).mtimeMs;
  build({ root, check: true });
  assert.equal(fs.statSync(path.join(root, 'archive-theme.min.css')).mtimeMs, stamp);
  assert.deepEqual(fs.readFileSync(path.join(root, 'theme.css')), source);
  assert.deepEqual(fs.readFileSync(path.join(root, 'theme.min.css')), original);
});
test('missing/stale output check fails without creating or repairing files', t => {
  const root = fixture(t);
  assert.throws(() => build({ root, check: true }), /Stale/);
  assert.equal(fs.readdirSync(root).length, 8);
  build({ root });
  fs.appendFileSync(path.join(root, 'theme.css'), '.changed{}');
  assert.throws(() => build({ root, check: true }), /Stale/);
});
test('reject source/output symlinks, traversal and malformed CSS', t => {
  const root = fixture(t);
  assert.throws(() => safe(root, '../outside'), /Unsafe/);
  fs.symlinkSync(path.join(root, 'theme.css'), path.join(root, 'archive-theme.min.css'));
  assert.throws(() => build({ root }), /Symlink/);
  fs.unlinkSync(path.join(root, 'archive-theme.min.css'));
  fs.unlinkSync(path.join(root, 'theme.min.css'));
  fs.symlinkSync(path.join(root, 'theme.css'), path.join(root, 'theme.min.css'));
  assert.throws(() => build({ root }), /Symlink/);
  assert.throws(() => project('.bad{color:'), /Unclosed/);
});

test('input-only receipt binds six exact originals and never generates companion CSS', t => {
  const root = fixture(t);
  const before = INPUTS.map(name => fs.readFileSync(path.join(root, name + '.min.css')));
  build({ root });
  const receipt = JSON.parse(fs.readFileSync(path.join(root, 'archive-style-inputs.json')));
  assert.equal(receipt.schema, 'skyyrose.archive-style-inputs.v1');
  assert.deepEqual(receipt.sources.map(row => row.file), INPUTS.map(name => name + '.min.css'));
  INPUTS.forEach((name, index) => assert.deepEqual(fs.readFileSync(path.join(root, name + '.min.css')), before[index]));
  assert.equal(fs.existsSync(path.join(root, 'archive-companion.min.css')), false);
  assert.equal('output' in receipt, false);
  fs.appendFileSync(path.join(root, 'controls.min.css'), '.extension{}');
  assert.throws(() => build({ root, check: true }), /Stale/);
});
test('input receipt rejects missing or symlinked token authority without writing', t => {
  const root = fixture(t);
  fs.unlinkSync(path.join(root, 'design-tokens.min.css'));
  assert.throws(() => build({ root }), /ENOENT/);
  assert.equal(fs.existsSync(path.join(root, 'archive-theme.min.css')), false);
  fs.symlinkSync(path.join(root, 'controls.min.css'), path.join(root, 'design-tokens.min.css'));
  assert.throws(() => build({ root }), /Symlink/);
});
