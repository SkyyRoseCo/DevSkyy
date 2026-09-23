/** Synthetic DOM contract harness; no browser/GPU claims. */
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const theme = path.resolve(__dirname, '../../../wordpress-theme/skyyrose-flagship-2');
const source = name => fs.readFileSync(path.join(theme, 'assets/js', name), 'utf8');
class Target {
  constructor() {
    this.listeners = new Map();
  }
  addEventListener(name, fn, options) {
    const list = this.listeners.get(name) || [];
    list.push(options && options.once ? { fn, once: true } : fn);
    this.listeners.set(name, list);
  }
  dispatchEvent(event) {
    const list = this.listeners.get(event.type) || [];
    list.slice().forEach(entry => {
      if (typeof entry === 'function') entry(event);
      else {
        list.splice(list.indexOf(entry), 1);
        entry.fn(event);
      }
    });
    return !event.defaultPrevented;
  }
}
class ClassList {
  constructor() {
    this.set = new Set();
  }
  contains(name) {
    return this.set.has(name);
  }
  add(name) {
    this.set.add(name);
  }
  remove(name) {
    this.set.delete(name);
  }
}
class Element extends Target {
  constructor(tag = 'div') {
    super();
    this.tagName = tag;
    this.children = [];
    this.attributes = {};
    this.dataset = {};
    this.style = {};
    this.value = '';
    this._hidden = false;
    this.isConnected = true;
    this.classList = new ClassList();
  }
  get hidden() {
    return this._hidden;
  }
  /** Browsers blur a focused element that stops rendering (focus fixup) — the harness mirrors that. */
  set hidden(value) {
    this._hidden = !!value;
    if (this._hidden && this.document && this.document.activeElement === this) this.document.activeElement = this.document.body;
  }
  append(...items) {
    items.forEach(item => {
      if (item.parent) item.remove();
      item.parent = this;
      item.isConnected = true;
      this.children.push(item);
    });
  }
  appendChild(item) {
    this.append(item);
  }
  remove() {
    if (this.parent) this.parent.children.splice(this.parent.children.indexOf(this), 1);
    this.isConnected = false;
  }
  replaceWith(item) {
    this.replacement = item;
    this.remove();
  }
  cloneNode() {
    const item = new Element(this.tagName);
    item.attributes = { ...this.attributes };
    item.document = this.document;
    item.href = this.href;
    item.hidden = this.hidden;
    return item;
  }
  setAttribute(name, value) {
    this.attributes[name] = value;
  }
  getAttribute(name) {
    return this.attributes[name];
  }
  removeAttribute(name) {
    delete this.attributes[name];
    if (name === 'hidden') this.hidden = false;
  }
  get firstElementChild() {
    return this.children[0];
  }
  get parentElement() {
    return this.parent;
  }
  contains(target) {
    return target === this || this.children.some(child => child.contains(target));
  }
  getBoundingClientRect() {
    return { top: 0, bottom: 240, left: 1256, width: 160, height: 248 };
  }
  getClientRects() {
    for (let node = this; node; node = node.parentElement) {
      if (node.hidden || (node.tagName === 'dialog' && !node.open)) return [];
    }
    return [this.getBoundingClientRect()];
  }
  focus() {
    if (this.getClientRects().length) this.document.activeElement = this;
  }
}
/**
 * @param {object} [options]
 * @param {boolean} [options.reduced] prefers-reduced-motion: reduce
 * @param {boolean} [options.saveData] navigator.connection.saveData
 * @param {boolean} [options.home] mount the dock host and its controls
 * @param {boolean} [options.narrow] (max-width: 47.99em) matches
 * @param {number} [options.deviceMemory] navigator.deviceMemory
 * @param {object} [options.session] initial sessionStorage entries
 * @param {boolean} [options.sessionThrows] every sessionStorage access throws (private mode)
 */
function harness({
  reduced = false,
  saveData = false,
  home = false,
  narrow = false,
  deviceMemory,
  session = {},
  sessionThrows = false,
} = {}) {
  const document = new Target();
  const ids = Object.fromEntries(
    [
      'skyy-ask-dialog',
      'skyyrose-mascot-recall',
      'skyyrose-mascot',
      'skyyrose-mascot-trigger',
      'skyy-conversation',
      'skyy-ask-form',
      'skyy-ask-input',
      'skyy-motion-toggle',
      'skyy-ask-cancel',
      'skyy-ask-minimize',
      'skyy-chips',
      'skyy-3d-canvas',
      'skyy-presence-status',
    ].map(id => [id, new Element()])
  );
  if (home)
    ['skyy-hero-stage', 'skyy-dialog-stage', 'skyy-hero-chat', 'skyy-hero-dismiss'].forEach(id => {
      ids[id] = new Element();
    });
  document.getElementById = id => ids[id];
  document.createElement = tag => {
    const el = new Element(tag);
    el.document = document;
    return el;
  };
  document.body = new Element('body');
  document.head = new Element('head');
  document.activeElement = ids['skyyrose-mascot-recall'];
  document.querySelector = () => (ids['skyy-ask-dialog'].open ? ids['skyy-ask-dialog'] : null);
  document.querySelectorAll = () => [];
  document.hidden = false;
  document.readyState = 'loading';
  ids['skyy-ask-dialog'].contains = target =>
    Object.entries(ids).some(([id, el]) => id !== 'skyyrose-mascot-recall' && el === target);
  Object.values(ids).forEach(el => {
    el.document = document;
  });
  ids['skyy-ask-dialog'].showModal = function () {
    this.open = true;
  };
  ids['skyy-ask-dialog'].close = function () {
    this.open = false;
    this.dispatchEvent({ type: 'close' });
  };
  ids['skyyrose-mascot'].dataset.state = 'hidden';
  ids['skyy-presence-status'].dataset = {
    static: 'Your house guide.',
    loading: 'Skyy is joining you…',
    live: 'Your house guide.',
    reduced: 'Motion off',
    saving: 'Data-saving mode',
    failed: 'Motion unavailable. You can still ask Skyy.',
  };
  const sprite = new Element('img');
  ids['skyyrose-mascot'].querySelector = () => sprite;
  ids['skyy-3d-canvas'].getContext = () => null;
  ids['skyyrose-mascot-recall'].href = 'http://localhost:8899/contact/';
  ids['skyyrose-mascot-recall'].tagName = 'a';
  const media = new Target();
  media.matches = reduced;
  const narrowMedia = new Target();
  narrowMedia.matches = narrow;
  const window = new Target();
  window.innerHeight = 844;
  window.innerWidth = narrow ? 390 : 1440;
  const storage = new Map(Object.entries(session));
  window.sessionStorage = {
    getItem(key) {
      if (sessionThrows) throw new Error('SecurityError');
      return storage.has(key) ? storage.get(key) : null;
    },
    setItem(key, value) {
      if (sessionThrows) throw new Error('SecurityError');
      storage.set(key, String(value));
    },
    removeItem(key) {
      if (sessionThrows) throw new Error('SecurityError');
      storage.delete(key);
    },
  };
  const observers = [];
  class IntersectionObserver {
    constructor(callback) {
      this.callback = callback;
      observers.push(this);
    }
    observe() {}
  }
  if (home) {
    window.IntersectionObserver = IntersectionObserver;
    ids['skyyrose-mascot-recall'].hidden = true; // Markup ships the recall hidden until a dismissal.
    ids['skyy-dialog-stage'].append(ids['skyyrose-mascot']);
    ids['skyy-ask-dialog'].tagName = 'dialog';
    ids['skyy-ask-dialog'].append(ids['skyy-dialog-stage']);
    ids['skyyrose-mascot'].append(
      ids['skyyrose-mascot-trigger'],
      ids['skyy-hero-chat'],
      ids['skyy-hero-dismiss'],
      ids['skyy-motion-toggle']
    );
  }
  const timers = new Map();
  const delays = new Map();
  let nextTimer = 0;
  const navigator = { connection: { saveData } };
  if (deviceMemory !== undefined) navigator.deviceMemory = deviceMemory;
  const context = vm.createContext({
    window,
    document,
    location: new URL('http://localhost:8899/'),
    navigator,
    URL,
    Promise,
    Set,
    Object,
    AbortController,
    IntersectionObserver,
    Event,
    CustomEvent: class {
      constructor(type, init = {}) {
        this.type = type;
        this.detail = init.detail;
      }
    },
    setTimeout: (fn, delay) => {
      timers.set(++nextTimer, fn);
      delays.set(nextTimer, delay);
      return nextTimer;
    },
    clearTimeout: id => {
      timers.delete(id);
      delays.delete(id);
    },
    fetch: () => {
      throw new Error('Unexpected network');
    },
  });
  window.matchMedia = query => (/max-width/.test(query) ? narrowMedia : media);
  function run(name) {
    vm.runInContext(source(name), context, { filename: name });
  }
  function click(el, modifiers = {}) {
    const e = {
      type: 'click',
      button: 0,
      defaultPrevented: false,
      preventDefault() {
        this.defaultPrevented = true;
      },
      ...modifiers,
    };
    el.dispatchEvent(e);
    return e;
  }
  function submit(value) {
    ids['skyy-ask-input'].value = value;
    ids['skyy-ask-form'].dispatchEvent({ type: 'submit', preventDefault() {} });
  }
  /** Run every timer scheduled with exactly this delay (in scheduling order). */
  function fireTimers(delay) {
    let fired = 0;
    for (const [id, fn] of [...timers.entries()]) {
      if (delays.get(id) !== delay) continue;
      timers.delete(id);
      delays.delete(id);
      fn();
      fired++;
    }
    return fired;
  }
  return {
    window,
    document,
    ids,
    sprite,
    timers,
    delays,
    session: storage,
    fireTimers,
    run,
    click,
    submit,
    context,
    media,
    narrowMedia,
    intersect: visible => observers.forEach(observer => observer.callback([{ isIntersecting: visible }])),
  };
}

module.exports = { harness, Element };
