const { test } = require('node:test');
const assert = require('node:assert/strict');
const { fixture } = require('./test-shell-overlays.cjs');

test('menu owns focus, preserves prior inert state and restores Escape focus', () => {
  const f = fixture();
  f.button.emit('click');
  assert.equal(f.main.inert, true);
  assert.equal(f.doc.activeElement, f.first);
  assert(f.body.classList.contains('sr2-nav-open'));
  f.last.focus();
  let prevented = false;
  f.doc.emit('keydown', { key: 'Tab', shiftKey: false, preventDefault() { prevented = true; } });
  assert(prevented);
  assert.equal(f.doc.activeElement, f.button);
  f.doc.emit('keydown', { key: 'Escape', preventDefault() {} });
  assert.equal(f.main.inert, false);
  assert.equal(f.footer.inert, true);
  assert.equal(f.doc.activeElement, f.button);
});

test('opening a native dialog closes menu and other dialog without patching native APIs', () => {
  const f = fixture();
  const nativeShowModal = f.dialogs[1].showModal;
  f.button.emit('click');
  f.dialogs[0].showModal();
  f.dialogs[1].showModal();
  assert.equal(f.dialogs[0].open, false);
  assert.equal(f.main.inert, false);
  assert.equal(f.button.getAttribute('aria-expanded'), 'false');
  assert.equal(f.dialogs[1].showModal, nativeShowModal);
});
