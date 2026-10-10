const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { harness, Element } = require('./fixtures/skyy-dom-harness.cjs');
for (const moved of [false, true])
  test(`delayed guide exit ${moved ? 'does not steal changed focus' : 'returns guide focus'}`, () => {
    const h = harness();
    h.run('mascot.js');
    h.window.skyyRoseConcierge.open();
    h.ids['skyyrose-mascot'].dataset.renderer = '3d';
    h.click(h.ids['skyy-ask-cancel']);
    const other = new Element('input');
    if (moved) h.document.activeElement = other;
    [...h.timers.values()].at(-1)();
    assert.equal(h.ids['skyy-ask-dialog'].open, false);
    assert.equal(h.document.activeElement, moved ? other : h.ids['skyyrose-mascot-recall']);
  });

const themeSource = fs.readFileSync(
  __dirname + '/../../wordpress-theme/skyyrose-flagship-2/assets/js/theme.js',
  'utf8'
);
function sizeGuideFixture({ supported = true, opens = true } = {}) {
  let click,
    openCount = 0;
  const trigger = {
    addEventListener(name, callback) {
      if (name === 'click') click = callback;
    },
  };
  const dialog = { addEventListener() {} };
  if (supported) dialog.showModal = () => {};
  const context = {
    document: { querySelector: () => dialog, querySelectorAll: () => [trigger] },
    overlays: {
      openDialog(actual, opener) {
        assert.equal(actual, dialog);
        assert.equal(opener, trigger);
        openCount++;
        return opens;
      },
      close() {},
    },
  };
  const start = themeSource.indexOf('  const sizeGuide =');
  const end = themeSource.indexOf('  /* Native links and GET search', start);
  assert(start >= 0 && end > start);
  vm.runInNewContext(themeSource.slice(start, end), context, { codeGeneration: { strings: false, wasm: false } });
  return {
    hasClick: () => typeof click === 'function',
    openCount: () => openCount,
    click(overrides = {}) {
      let prevented = false;
      click?.({
        button: 0,
        metaKey: false,
        ctrlKey: false,
        shiftKey: false,
        altKey: false,
        preventDefault() {
          prevented = true;
        },
        ...overrides,
      });
      return prevented;
    },
  };
}
test('size-guide ordinary and keyboard-generated primary click opens the coordinated dialog', () => {
  const f = sizeGuideFixture();
  assert.equal(f.click({ detail: 0 }), true);
  assert.equal(f.openCount(), 1);
});
test('size-guide modified and nonprimary navigation keeps the native anchor behavior', () => {
  for (const gesture of [
    { button: 1 },
    { button: 2 },
    { metaKey: true },
    { ctrlKey: true },
    { shiftKey: true },
    { altKey: true },
  ]) {
    const f = sizeGuideFixture();
    assert.equal(f.click(gesture), false);
    assert.equal(f.openCount(), 0);
  }
});
test('size-guide unsupported or failed modal leaves the native link available', () => {
  const unsupported = sizeGuideFixture({ supported: false });
  assert.equal(unsupported.hasClick(), false);
  const failed = sizeGuideFixture({ opens: false });
  assert.equal(failed.click(), false);
  assert.equal(failed.openCount(), 1);
});
