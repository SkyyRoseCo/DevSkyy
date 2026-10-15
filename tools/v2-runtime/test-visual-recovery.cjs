/** Execute the actual hero controller; no browser, media decoder, or network required. */
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(
  path.resolve(__dirname, '../../wordpress-theme/skyyrose-flagship-2/assets/js/visual-recovery.js'),
  'utf8'
);
const deferred = () => {
  let resolve, reject;
  const promise = new Promise((yes, no) => {
    resolve = yes;
    reject = no;
  });
  return { promise, resolve, reject };
};
const flush = () => new Promise(resolve => setImmediate(resolve));
class Target {
  constructor() {
    this.listeners = new Map();
  }
  addEventListener(name, callback) {
    if (!this.listeners.has(name)) this.listeners.set(name, []);
    this.listeners.get(name).push(callback);
  }
  emit(name, data = {}) {
    (this.listeners.get(name) || []).forEach(callback => callback(data));
  }
}
function fixture({
  reduced = false,
  saveData = false,
  decodeSupported = true,
  pendingPlay = false,
  stableFrame = false,
  currentSrc = '/responsive-640.webp',
  naturalWidth = 640,
  imageMissing = false,
} = {}) {
  const imageDecode = deferred();
  const playback = deferred();
  const preferences = Object.assign(new Target(), { matches: reduced });
  const connection = Object.assign(new Target(), { saveData });
  const button = Object.assign(new Target(), { hidden: true, setAttribute() {} });
  const selected = ['/approved-hero.webm', '/approved-hero.mp4'].map(src =>
    Object.assign(new Target(), { dataset: { src } })
  );
  const calls = { load: 0, play: 0, pause: 0, posters: [] };
  let posterUrl;
  const video = Object.assign(new Target(), {
    paused: true,
    querySelectorAll: () => selected,
    load() {
      calls.load++;
    },
    play() {
      calls.play++;
      if (pendingPlay)
        return playback.promise.then(() => {
          video.paused = false;
        });
      video.paused = false;
      return Promise.resolve();
    },
    pause() {
      calls.pause++;
      video.paused = true;
    },
  });
  let frameCallback;
  if (stableFrame)
    video.requestVideoFrameCallback = callback => {
      frameCallback = callback;
    };
  Object.defineProperty(video, 'poster', {
    get: () => posterUrl,
    set: value => {
      posterUrl = value;
      calls.posters.push(value);
    },
  });
  const image = Object.assign(new Target(), {
    currentSrc,
    naturalWidth,
    src: '/desktop-fallback.webp',
    complete: false,
  });
  if (decodeSupported) image.decode = () => imageDecode.promise;
  const classes = new Set();
  const hero = {
    dataset: {},
    classList: { add: value => classes.add(value), remove: value => classes.delete(value) },
    querySelector: selector =>
      ({
        '[data-recovery-motion-toggle]': button,
        '[data-recovery-hero-video]': video,
        img: imageMissing ? null : image,
      })[selector],
  };
  const document = Object.assign(new Target(), {
    hidden: false,
    documentElement: { dataset: {} },
    querySelectorAll: selector => (selector === '[data-recovery-hero]' ? [hero] : []),
  });
  let observer;
  class Observer {
    constructor(callback) {
      this.callback = callback;
      this.observed = new Set();
      observer = this;
    }
    observe(element) {
      this.observed.add(element);
    }
    disconnect() {
      this.observed.clear();
    }
  }
  const window = Object.assign(new Target(), { IntersectionObserver: Observer });
  const runtime = {
    window,
    document,
    navigator: { connection },
    matchMedia: () => preferences,
    IntersectionObserver: Observer,
    // A fixed delay is not part of the poster-decode contract.
    setTimeout() {
      throw new Error('Unexpected fixed hero delay');
    },
  };
  const runAgain = () =>
    vm.runInNewContext(source, runtime, {
      filename: 'visual-recovery.js',
      codeGeneration: { strings: false, wasm: false },
    });
  runAgain();
  return {
    imageDecode,
    playback,
    image,
    video,
    selected,
    calls,
    button,
    hero,
    document,
    window,
    classes,
    runAgain,
    presentFrame: () => frameCallback?.(),
    preferences,
    connection,
    observer,
    intersect(visible) {
      observer.callback([{ target: hero, isIntersecting: visible }]);
    },
  };
}

test('visible hero defers video source assignment/load/play until actual responsive decode settles', async () => {
  const f = fixture();
  f.intersect(true);
  assert.equal(f.calls.load, 0);
  assert.equal(f.calls.play, 0);
  assert(f.selected.every(item => item.src === undefined));
  f.image.currentSrc = '/responsive-1440.webp';
  f.imageDecode.resolve();
  await flush();
  assert.equal(f.video.poster, '/responsive-1440.webp');
  assert.equal(f.calls.load, 1);
  assert.equal(f.calls.play, 1);
  assert.deepEqual(
    f.selected.map(item => item.src),
    ['/approved-hero.webm', '/approved-hero.mp4']
  );
  f.intersect(true);
  assert.equal(f.calls.load, 1);
  assert.equal(f.calls.play, 1);
});

test('decoded but offscreen hero waits for viewport visibility without a fixed delay', async () => {
  const f = fixture();
  f.imageDecode.resolve();
  await flush();
  assert.equal(f.calls.load, 0);
  assert.equal(f.video.poster, '/responsive-640.webp');
  f.intersect(true);
  await flush();
  assert.equal(f.calls.load, 1);
  assert.equal(f.calls.play, 1);
});

test('reduced motion and Save-Data prevent media loads both initially and while decode is pending', async () => {
  for (const kind of ['reduced', 'saveData']) {
    for (const initially of [true, false]) {
      const f = fixture({ [kind]: initially });
      f.intersect(true);
      const target = kind === 'reduced' ? f.preferences : f.connection;
      const key = kind === 'reduced' ? 'matches' : 'saveData';
      target[key] = true;
      target.emit('change');
      f.imageDecode.resolve();
      await flush();
      assert.equal(f.calls.load, 0, `${kind}: no initial video request`);
      assert.equal(f.calls.play, 0);
      assert(f.selected.every(item => item.src === undefined));
      assert.equal(f.button.hidden, true);
      target[key] = false;
      target.emit('change');
      await flush();
      assert.equal(f.calls.load, 1, `${kind}: motion remains available when allowed`);
      assert.equal(f.button.hidden, false);
    }
  }
});

test('decode completion during pagehide cannot fetch or play; pageshow restores observer and motion', async () => {
  const f = fixture();
  f.intersect(true);
  f.window.emit('pagehide', { persisted: true });
  f.imageDecode.resolve();
  await flush();
  assert.equal(f.calls.load, 0);
  assert.equal(f.observer.observed.size, 0);
  f.window.emit('pageshow', { persisted: true });
  await flush();
  assert.equal(f.observer.observed.has(f.hero), true);
  assert.equal(f.calls.load, 1);
  assert.equal(f.calls.play, 1);
});

test('failed or unsupported image decode does not permanently disable otherwise available hero motion', async () => {
  for (const decodeSupported of [true, false]) {
    const f = fixture({ decodeSupported });
    f.intersect(true);
    if (decodeSupported) f.imageDecode.reject(new Error('Image decode failed'));
    await flush();
    assert.equal(f.calls.load, 1);
    assert.equal(f.calls.play, 1);
    assert.equal(f.video.poster, '/responsive-640.webp');
  }
});

test('user pause while decode is pending prevents loading and late play cannot revive a hidden hero', async () => {
  const f = fixture({ pendingPlay: true });
  f.intersect(true);
  f.button.emit('click');
  f.imageDecode.resolve();
  await flush();
  assert.equal(f.calls.load, 0);
  f.button.emit('click');
  assert.equal(f.calls.play, 1);
  f.document.hidden = true;
  f.document.emit('visibilitychange');
  f.playback.resolve();
  await flush();
  assert.equal(f.video.paused, true);
  assert.equal(f.calls.load, 1);
});

test('selected native poster is published before decode without fetching offscreen motion', async () => {
  const f = fixture({ pendingPlay: true });
  assert.equal(f.video.poster, '/responsive-640.webp');
  assert.equal(f.classes.has('is-hero-poster-ready'), true);
  assert.equal(f.calls.load, 0);
  assert.deepEqual(f.calls.posters, ['/responsive-640.webp']);
  f.imageDecode.resolve();
  await flush();
  assert.equal(f.video.poster, f.image.currentSrc);
  assert.deepEqual(f.calls.posters, ['/responsive-640.webp'], 'Decode completion must not republish the same poster');
  assert.equal(f.classes.has('is-hero-poster-ready'), true);
  assert.equal(f.calls.load, 0);
  f.intersect(true);
  assert.equal(f.calls.load, 1);
  assert.equal(f.calls.play, 1);
  assert.equal(f.classes.has('is-hero-video-ready'), false);
});

test('broken poster never covers the image fallback and video failure clears both layers', async () => {
  const broken = fixture();
  broken.image.naturalWidth = 0;
  broken.imageDecode.reject(new Error('Broken image'));
  await flush();
  assert.equal(broken.classes.has('is-hero-poster-ready'), false);
  const good = fixture();
  good.imageDecode.resolve();
  await flush();
  good.intersect(true);
  good.video.emit('playing');
  assert.equal(good.classes.has('is-hero-poster-ready'), true);
  assert.equal(good.classes.has('is-hero-video-ready'), true);
  good.video.emit('error');
  assert.equal(good.classes.has('is-hero-poster-ready'), false);
  assert.equal(good.classes.has('is-hero-video-ready'), false);
});

test('missing selected source never fetches desktop fallback; image load publishes before decode', async () => {
  const f = fixture({ currentSrc: '', naturalWidth: 0 });
  f.intersect(true);
  assert.equal(f.video.poster, undefined);
  assert.equal(f.classes.has('is-hero-poster-ready'), false);
  assert.equal(f.calls.load, 0);
  f.image.currentSrc = '/selected-mobile.webp';
  f.image.naturalWidth = 640;
  f.image.emit('load');
  assert.equal(f.video.poster, '/selected-mobile.webp');
  assert.equal(f.classes.has('is-hero-poster-ready'), true);
  assert.equal(f.calls.load, 0, 'Image load must not bypass pending decode gate');
  f.imageDecode.resolve();
  await flush();
  assert.equal(f.calls.load, 1);
  assert.deepEqual(f.calls.posters, ['/selected-mobile.webp']);
});
test('pending image bytes and image error keep picture fallback; video can still recover motion', async () => {
  const f = fixture({ naturalWidth: 0 });
  f.intersect(true);
  assert.equal(f.video.poster, undefined, 'Pending bytes must not create a second poster request');
  assert.equal(f.classes.has('is-hero-poster-ready'), false);
  assert.equal(f.calls.load, 0);
  f.image.emit('error');
  f.imageDecode.reject(new Error('Image unavailable'));
  await flush();
  assert.equal(f.classes.has('is-hero-poster-ready'), false);
  assert.equal(f.calls.load, 1);
  assert.equal(f.calls.play, 1);
  f.video.emit('playing');
  assert.equal(f.classes.has('is-hero-video-ready'), true);
});
test('missing image never selects an invented poster and retains native video availability', async () => {
  const f = fixture({ imageMissing: true });
  f.intersect(true);
  await flush();
  assert.equal(f.video.poster, undefined);
  assert.equal(f.classes.has('is-hero-poster-ready'), false);
  assert.equal(f.calls.load, 1);
});

test('autoplay rejection keeps the early poster and offers a user-driven retry', async () => {
  const f = fixture({ pendingPlay: true });
  f.intersect(true);
  f.imageDecode.resolve();
  await flush();
  f.playback.reject(Object.assign(new Error('Gesture required'), { name: 'NotAllowedError' }));
  await flush();
  assert.equal(f.calls.play, 1);
  assert.equal(f.classes.has('is-hero-poster-ready'), true);
  assert.equal(f.button.textContent, 'Play motion');
  assert.equal(f.hero.dataset.recoveryMotion, 'paused');
});

test('first activated source error preserves native fallback and subsequent playing', async () => {
  const f = fixture({ pendingPlay: true });
  // Errors before activation cannot poison later native source selection.
  f.selected[1].emit('error');
  f.intersect(true);
  f.imageDecode.resolve();
  await flush();
  f.selected[0].emit('error');
  f.selected[0].emit('error');
  assert.equal(f.classes.has('is-hero-poster-ready'), true);
  assert.equal(f.calls.pause, 0, 'WebM failure must not stop native MP4 fallback');
  f.playback.resolve();
  await flush();
  f.video.emit('playing');
  assert.equal(f.classes.has('is-hero-video-ready'), true);
  assert.equal(f.video.paused, false);
  assert.equal(f.calls.load, 1);
});

test('all activated source errors clean up a pending play without a video-level error', async () => {
  const f = fixture({ pendingPlay: true });
  f.intersect(true);
  f.imageDecode.resolve();
  await flush();
  f.selected[0].emit('error');
  f.selected[1].emit('error');
  assert.equal(f.classes.has('is-hero-poster-ready'), false);
  assert.equal(f.classes.has('is-hero-video-ready'), false);
  assert.equal(f.video.paused, true);
  assert.equal(f.calls.pause, 1);
  // Neither a late promise settlement nor a late playing event may revive it.
  f.playback.resolve();
  await flush();
  f.video.emit('playing');
  f.intersect(false);
  f.intersect(true);
  f.button.emit('click');
  f.button.emit('click');
  assert.equal(f.video.paused, true);
  assert.equal(f.classes.has('is-hero-video-ready'), false);
  assert.equal(f.classes.has('is-hero-poster-ready'), false);
  assert.equal(f.calls.play, 1);
  assert.equal(f.calls.load, 1);
});

test('hero reveals only a stable frame and rejects a late frame after suspension', async () => {
  const f = fixture({ stableFrame: true });
  f.intersect(true);
  f.imageDecode.resolve();
  await flush();
  f.video.emit('playing');
  assert.equal(f.classes.has('is-hero-video-ready'), false);
  f.presentFrame();
  assert.equal(f.classes.has('is-hero-video-ready'), true);
  f.preferences.matches = true;
  f.preferences.emit('change');
  assert.equal(f.classes.has('is-hero-video-ready'), false);
  f.preferences.matches = false;
  f.preferences.emit('change');
  await flush();
  f.video.emit('playing');
  f.window.emit('pagehide');
  f.presentFrame();
  assert.equal(f.classes.has('is-hero-video-ready'), false);
});

test('repeated hero bootstrap does not register a second controller', () => {
  const f = fixture();
  const count = f.document.listeners.get('visibilitychange').length;
  f.runAgain();
  assert.equal(f.document.listeners.get('visibilitychange').length, count);
});
