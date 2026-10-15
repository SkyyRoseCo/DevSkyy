const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.resolve(__dirname, '../../wordpress-theme/skyyrose-flagship-2/assets/js/theme.js'), 'utf8');
const start = source.indexOf('  /* WooCommerce owns variation resolution');
const end = source.indexOf('  /* End native commerce adapter. */', start);
assert(start >= 0 && end > start, 'Native commerce adapter boundaries must exist');
const code = source.slice(start, end);
function fixture() {
  const events = {};
  const status = { dataset: {}, textContent: '' };
  const input = { value: '0' };
  const form = { dataset: {}, matches: () => true, querySelector: () => input, addEventListener: (name, callback) => { events[name] = callback; } };
  const attributes = {};
  const button = { dataset: {}, textContent: 'Add to cart', disabled: false, classList: { contains: () => false }, closest: () => form,
    getAttribute: (name) => attributes[name], setAttribute: (name, value) => { attributes[name] = value; }, removeAttribute: (name) => { delete attributes[name]; } };
  const jquery = () => ({ each: (callback) => callback.call(form), on: (names, callback) => names.split(' ').forEach(name => { events[name] = callback; }) });
  vm.runInNewContext(code, { document: { body: {}, querySelector: () => status, querySelectorAll: () => [button] }, window: { jQuery: jquery, addEventListener: (name, callback) => { events[name] = callback; } } });
  return { events, status, input, form, button };
}
test('found event alone never promises a completed native selection', () => {
  const f = fixture();
  f.events.found_variation?.({}, { variation_id: 123, is_in_stock: true, is_purchasable: true });
  assert.notEqual(f.form.dataset.sr2VariationState, 'valid');
});
test('shown variation must match the real hidden native ID', () => {
  const f = fixture();
  f.events.show_variation({}, { variation_id: 123, is_in_stock: true, is_purchasable: true }, true);
  assert.notEqual(f.form.dataset.sr2VariationState, 'valid');
  f.input.value = '123';
  f.events.show_variation({}, { variation_id: 123, is_in_stock: true, is_purchasable: true }, true);
  assert.equal(f.form.dataset.sr2VariationState, 'valid');
  f.events.show_variation({}, { variation_id: 123, is_in_stock: false, is_purchasable: true }, false);
  assert.equal(f.form.dataset.sr2VariationState, 'unavailable');
});
test('zero-ID and repeated submits are blocked without generating an ID', () => {
  const f = fixture();
  let blocked = 0;
  const event = { defaultPrevented: false, preventDefault() { blocked++; } };
  f.events.submit(event);
  assert.equal(blocked, 1);
  assert.equal(f.input.value, '0');
  f.input.value = '123';
  f.events.submit(event);
  assert.equal(blocked, 1);
  f.events.submit(event);
  assert.equal(blocked, 2);
  f.events.pageshow();
  assert.equal(f.button.getAttribute('aria-busy'), undefined);
});
