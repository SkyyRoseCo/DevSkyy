const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { JSDOM } = require('jsdom');
const code = fs.readFileSync(path.resolve(__dirname, '../../wordpress-theme/skyyrose-flagship-2/assets/js/home-experience.js'), 'utf8');
async function fixture({ reduced = false, saveData = false, reject = false } = {}) {
  const dom = new JSDOM('<div data-home-motion><img><video><source data-src="film.mp4"></video><button data-home-motion-toggle hidden>Play motion</button></div>', { runScripts: 'outside-only', pretendToBeVisual: true });
  const w = dom.window;
  w.matchMedia = () => ({ matches: reduced, addEventListener() {} });
  Object.defineProperty(w.navigator, 'connection', { value: { saveData } });
  let intersect;
  w.IntersectionObserver = class {
    constructor(callback) { intersect = callback; }
    observe() {}
  };
  const video = w.document.querySelector('video');
  let paused = true;
  Object.defineProperty(video, 'paused', { get: () => paused });
  video.load = () => {};
  video.play = () => {
    if (reject) return Promise.reject(new Error('Blocked'));
    paused = false;
    video.dispatchEvent(new w.Event('playing'));
    return Promise.resolve();
  };
  video.pause = () => { paused = true; video.dispatchEvent(new w.Event('pause')); };
  w.eval(code);
  intersect([{ isIntersecting: true }]);
  await Promise.resolve();
  return { dom, video, root: w.document.querySelector('[data-home-motion]'), button: w.document.querySelector('button'), intersect };
}
(async () => {
  for (const policy of [{ reduced: true }, { saveData: true }]) {
    const f = await fixture(policy);
    assert.equal(f.video.querySelector('source').hasAttribute('src'), false, 'restricted connection or motion preference leaves sources unloaded');
    assert.equal(f.root.classList.contains('is-playing'), false);
    f.button.click();
    await Promise.resolve();
    assert.equal(f.video.paused, false, 'explicit playback remains accessible');
    f.dom.window.close();
  }
  const normal = await fixture();
  assert.equal(normal.root.classList.contains('is-playing'), true);
  normal.button.click();
  assert.equal(normal.video.paused, true);
  normal.intersect([{ isIntersecting: false }]);
  normal.intersect([{ isIntersecting: true }]);
  assert.equal(normal.video.paused, true, 'manual pause survives viewport re-entry');
  normal.dom.window.close();
  const blocked = await fixture({ reject: true });
  await Promise.resolve();
  assert.equal(blocked.root.classList.contains('is-playing'), false, 'blocked playback cannot obscure the poster');
  assert.equal(blocked.button.hidden, false);
  blocked.dom.window.close();
  console.log('Homepage film behavior: PASS');
})().catch(error => { console.error(error); process.exitCode = 1; });
