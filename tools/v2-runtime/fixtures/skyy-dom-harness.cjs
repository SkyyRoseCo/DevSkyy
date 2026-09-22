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
  addEventListener(name, fn) {
    const list = this.listeners.get(name) || [];
    list.push(fn);
    this.listeners.set(name, list);
  }
  dispatchEvent(event) {
    (this.listeners.get(event.type) || []).forEach(fn => fn(event));
    return !event.defaultPrevented;
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
    this.hidden = false;
    this.isConnected = true;
    this.classList = { contains: () => false };
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
    return { top: 0, bottom: 240 };
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
function harness({ reduced = false, saveData = false, home = false } = {}) {
  const document = new Target();
  const ids = Object.fromEntries(
    [
      'skyy-ask-dialog',
      'skyyrose-mascot-recall',
      'skyyrose-mascot',
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
  document.body = new Element();
  document.head = new Element();
  document.activeElement = ids['skyyrose-mascot-recall'];
  document.querySelector = () => (ids['skyy-ask-dialog'].open ? ids['skyy-ask-dialog'] : null);
  document.hidden = false;
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
  const media = new Target();
  media.matches = reduced;
  const window = new Target();
  window.innerHeight = 844;
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
    ids['skyy-dialog-stage'].append(ids['skyyrose-mascot']);
    ids['skyy-ask-dialog'].tagName = 'dialog';
    ids['skyy-ask-dialog'].append(ids['skyy-dialog-stage']);
    ids['skyyrose-mascot'].append(ids['skyy-hero-chat'], ids['skyy-hero-dismiss'], ids['skyy-motion-toggle']);
  }
  const timers = new Map();
  let nextTimer = 0;
  const context = vm.createContext({
    window,
    document,
    location: new URL('http://localhost:8899/'),
    navigator: { connection: { saveData } },
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
    setTimeout: fn => {
      timers.set(++nextTimer, fn);
      return nextTimer;
    },
    clearTimeout: id => timers.delete(id),
    fetch: () => {
      throw new Error('Unexpected network');
    },
  });
  window.matchMedia = () => media;
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
  return {
    window,
    document,
    ids,
    sprite,
    timers,
    run,
    click,
    submit,
    context,
    media,
    intersect: visible => observers.forEach(observer => observer.callback([{ isIntersecting: visible }])),
  };
}

module.exports = { harness, Element };
