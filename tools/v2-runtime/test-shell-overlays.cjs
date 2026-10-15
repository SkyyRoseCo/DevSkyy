const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(__dirname + '/../../wordpress-theme/skyyrose-flagship-2/assets/js/theme.js', 'utf8');

function fixture() {
  const makeEvents = () => ({ handlers: {}, addEventListener(name, callback) { (this.handlers[name] ||= []).push(callback); }, emit(name, event = {}) { event.target ||= this; for (const callback of this.handlers[name] || []) callback(event); } });
  const doc = { ...makeEvents(), activeElement: null };
  const element = (tag, id) => {
    const classes = new Set();
    const styles = new Map();
    const el = { ...makeEvents(), tag, id, children: [], parentElement: null, attrs: {}, inert: false, isConnected: true, open: false,
      classList: { add: v => classes.add(v), remove: v => classes.delete(v), contains: v => classes.has(v), toggle(v, on) { on ? classes.add(v) : classes.delete(v); } },
      style: { getPropertyValue: k => styles.get(k)?.value || '', getPropertyPriority: k => styles.get(k)?.priority || '', setProperty(k, value, priority = '') { styles.set(k, { value, priority }); }, removeProperty(k) { styles.delete(k); } },
      setAttribute(k, v) { this.attrs[k] = v; }, getAttribute(k) { return this.attrs[k]; },
      append(child) { this.children.push(child); child.parentElement = this; return child; },
      contains(other) { return this === other || this.children.some(child => child.contains(other)); },
      matches(selector) { return selector.split(',').map(v => v.trim()).some(v => v === tag || (v === 'dialog[open]' && tag === 'dialog' && this.open)); },
      closest(selector) { if (selector === '[inert]' && this.inert) return this; return this.parentElement?.closest(selector) || null; },
      getClientRects() { return this.hidden ? [] : [1]; },
      focus() { if (!this.closest('[inert]')) { doc.activeElement = this; doc.emit('focusin', { target: this }); } },
      querySelectorAll(selector) { const all = this.children.flatMap(child => [child, ...child.querySelectorAll('*')]); if (selector === '*') return all; if (selector === 'a') return all.filter(x => x.tag === 'a'); return all.filter(x => ['a', 'button', 'input'].includes(x.tag)); },
      querySelector(selector) { return this.querySelectorAll(selector)[0] || null; },
    };
    if (tag === 'dialog') { el.showModal = () => { el.emit('beforetoggle', { newState: 'open' }); el.open = true; el.querySelector('input,button')?.focus(); }; el.close = () => { el.open = false; }; }
    return el;
  };
  const root = element('html', 'root'), body = root.append(element('body', 'body'));
  const header = body.append(element('header', 'header'));
  const button = header.append(element('button', 'menuButton'));
  const menu = header.append(element('nav', 'menu'));
  const first = menu.append(element('a', 'first')), last = menu.append(element('a', 'last'));
  const main = body.append(element('main', 'main'));
  const opener = main.append(element('button', 'opener'));
  const footer = body.append(element('footer', 'footer')); footer.inert = true;
  const dialogs = [body.append(element('dialog', 'search')), main.append(element('dialog', 'guide'))];
  dialogs.forEach(dialog => dialog.append(element('input', dialog.id + 'input')));
  root.clientWidth = 1425;
  let observerCallback;
  class MutationObserver {
    constructor(callback) { observerCallback = callback; }
    observe() {}
  }
  const win = { ...makeEvents(), MutationObserver, innerWidth: 1440, scrollX: 0, scrollY: 430,
    matchMedia: () => ({ matches: false }), scrollTo(x, y) { this.scrollX = x; this.scrollY = y; },
  };
  Object.assign(doc, { body, documentElement: root, querySelector: selector => ({ '[data-site-header]': header, '[data-sr2-menu]': button, '[data-sr2-nav]': menu }[selector] || null), querySelectorAll: selector => selector === 'dialog' ? dialogs : selector === 'dialog[open]' ? dialogs.filter(d => d.open) : [] });
  body.style.setProperty('padding-right', '7px', 'important');
  body.style.setProperty('top', '3px');
  root.style.setProperty('scroll-behavior', 'smooth');
  const context = { document: doc, window: win, MutationObserver, navigator: {}, getComputedStyle: el => ({ visibility: 'visible', paddingRight: el.style.getPropertyValue('padding-right') }), expose: null };
  vm.createContext(context);
  const start = source.indexOf('  const root ='); const end = source.indexOf('  if (header) {');
  assert(start > 0 && end > start);
  vm.runInContext(source.slice(start, end) + '\nexpose = overlays;', context, { codeGeneration: { strings: false, wasm: false } });
  return { doc, win, root, body, header, button, menu, first, last, main, footer, opener, dialogs, manager: context.expose, flushMutations: () => observerCallback() };
}
module.exports = { fixture };

if (require.main === module) {
  test('navigation isolates background, traps Tab, and restores original inert on Escape', () => {
    const f = fixture(); f.button.emit('click');
    assert.equal(f.main.inert, true); assert.equal(f.doc.activeElement, f.first);
    f.last.focus(); let prevented = false;
    f.doc.emit('keydown', { key: 'Tab', preventDefault() { prevented = true; } });
    assert(prevented); assert.equal(f.doc.activeElement, f.button);
    f.doc.emit('keydown', { key: 'Escape', preventDefault() {} });
    assert.equal(f.main.inert, false); assert.equal(f.footer.inert, true); assert.equal(f.doc.activeElement, f.button);
  });
  test('desktop compensation and mobile body locking restore exact styles and scroll', () => {
    for (const width of [390, 1440]) {
      const f = fixture(); f.win.innerWidth = width; f.root.clientWidth = width === 390 ? 390 : 1425;
      f.manager.openDialog(f.dialogs[0], f.opener);
      assert.equal(f.body.style.getPropertyValue('position'), 'fixed');
      assert.equal(f.body.style.getPropertyValue('top'), '-430px');
      assert.equal(f.body.style.getPropertyValue('padding-right'), width === 390 ? '7px' : '22px');
      f.win.scrollY = 0; f.manager.close();
      assert.equal(f.win.scrollY, 430); assert.equal(f.body.style.getPropertyValue('position'), '');
      assert.equal(f.body.style.getPropertyValue('top'), '3px'); assert.equal(f.body.style.getPropertyPriority('padding-right'), 'important');
      assert.equal(f.root.style.getPropertyValue('scroll-behavior'), 'smooth'); assert.equal(f.doc.activeElement, f.opener);
    }
  });
  test('external native dialog replaces menu, then nested dialog keeps its ancestors usable', () => {
    const f = fixture(); f.button.emit('click'); f.dialogs[0].showModal();
    assert.equal(f.button.getAttribute('aria-expanded'), 'false');
    f.dialogs[1].showModal();
    assert.equal(f.dialogs[0].open, false); assert.equal(f.main.inert, false); assert.equal(f.opener.inert, true);
    assert.equal(f.dialogs[1].inert, false); assert.equal(f.header.inert, true);
    f.manager.close(); assert.equal(f.opener.inert, false); assert.equal(f.header.inert, false); assert.equal(f.footer.inert, true);
  });
  test('rapid close/reopen ignores delayed native close event', () => {
    const f = fixture(); const d = f.dialogs[0];
    for (let n = 0; n < 10; n++) { f.manager.openDialog(d, f.opener); f.manager.close(); }
    f.manager.openDialog(d, f.opener); d.emit('close');
    assert.equal(f.manager.isOpen(), true); assert.equal(f.body.style.getPropertyValue('position'), 'fixed');
    d.close(); d.emit('close'); assert.equal(f.manager.isOpen(), false); assert.equal(f.body.style.getPropertyValue('position'), '');
  });
  test('resize preserves lock and pagehide/pageshow clear all stale state', () => {
    const f = fixture(); f.button.emit('click'); f.first.hidden = true; f.win.emit('resize');
    assert.equal(f.doc.activeElement, f.button); assert.equal(f.manager.isOpen(), true);
    f.win.emit('pagehide'); f.win.emit('pageshow');
    assert.equal(f.manager.isOpen(), false); assert.equal(f.body.classList.contains('sr2-nav-open'), false);
    assert.equal(f.body.classList.contains('sr2-overlay-open'), false); assert.equal(f.main.inert, false); assert.equal(f.win.scrollY, 430);
  });
  test('fragment removal repairs detached focus without stealing valid dialog field focus', () => {
    const f = fixture(); const dialog = f.dialogs[0];
    f.manager.openDialog(dialog, f.opener);
    const field = dialog.children[0]; field.focus();
    f.flushMutations(); assert.equal(f.doc.activeElement, field);
    // Removing the focused native remove control moves focus to BODY without
    // emitting focusin; the observer must re-enter the still-open dialog.
    f.doc.activeElement = f.body;
    f.flushMutations(); assert.equal(f.doc.activeElement, field);
    assert.equal(f.manager.isOpen(), true);
  });
  test('topmost Escape is consumed before restored focus reaches guide handlers', () => {
    const f = fixture(); f.manager.openDialog(f.dialogs[0], f.opener);
    let stopped = false;
    f.doc.emit('keydown', { key: 'Escape', preventDefault() {}, stopImmediatePropagation() { stopped = true; } });
    assert(stopped); assert.equal(f.doc.activeElement, f.opener);
    assert.equal(f.manager.isOpen(), false);
  });
  test('bag announcement relays only native confirmed removal message for its own control', () => {
    const events = {}; let callback;
    const status = { textContent: 'previous' };
    const control = {};
    const bag = { open: true, querySelector: () => status, contains: el => el === control, addEventListener: (name, fn) => { events[name] = fn; } };
    const context = { document: { querySelector: () => bag }, body: {}, window: { jQuery: () => ({ on: (_name, fn) => { callback = fn; } }) } };
    const begin = source.indexOf('  const bagDialog =');
    const end = source.indexOf('  if (finePointer && !reducedMotion)', begin);
    vm.runInNewContext(source.slice(begin, end), context);
    const click = () => events.click({ target: { closest: () => control } });
    click(); assert.equal(status.textContent, '');
    callback({}, {}, 'hash', { 0: {}, data: () => 'wrong button' });
    assert.equal(status.textContent, '');
    callback({}, {}, 'hash', { 0: control, data: key => key === 'success_message' ? 'Oakland Jersey has been removed from your cart.' : null });
    assert.equal(status.textContent, 'Oakland Jersey has been removed from your cart.');
    click(); callback({}, {}, 'hash', { 0: control, data: () => undefined });
    assert.equal(status.textContent, '');
    click(); bag.open = false; callback({}, {}, 'hash', { 0: control, data: () => 'late message' });
    assert.equal(status.textContent, ''); events.close();
  });
  test('visible opener returns immediately and an unavailable opener uses the safe fallback', () => {
    const f = fixture();
    f.manager.openDialog(f.dialogs[0], f.opener);
    f.manager.close(); assert.equal(f.doc.activeElement, f.opener);
    f.manager.openDialog(f.dialogs[0], f.opener); f.opener.hidden = true;
    f.manager.close(); assert.equal(f.doc.activeElement, f.button);
  });
  test('unsupported or failing native modal retains navigation fallback and releases state', () => {
    const f = fixture(); assert.equal(f.manager.openDialog({}, f.opener), false);
    f.dialogs[0].showModal = () => { throw new Error('unavailable'); };
    assert.equal(f.manager.openDialog(f.dialogs[0], f.opener), false);
    assert.equal(f.body.style.getPropertyValue('position'), ''); assert.equal(f.main.inert, false);
  });
}
