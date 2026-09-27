/* Agent E browser verification of the Skyy walk-on dock (fixture, swiftshader WebGL). */
const { chromium } = require('/Users/theceo/DevSkyy/node_modules/playwright');
const fs = require('node:fs');
const path = require('node:path');

const EVID = '/Users/theceo/.codex/worktrees/v2-home-layout-repair/DevSkyy/tasks/v2-whole-site-rework-20260922/evidence/skyy';
const FRAMES = path.join(EVID, 'frames');
const BASE = 'http://127.0.0.1:8794/tools/v2-theme-preview.php';
const ARGS = ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'];
const results = { startedAt: new Date().toISOString(), scenarios: {} };
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

fs.mkdirSync(FRAMES, { recursive: true });

async function instrument(context) {
  await context.addInitScript(() => {
    window.__skyy = { events: [], t0: performance.now() };
    const names = [
      'walking-in', 'idle', 'show', 'hidden', 'loading', 'prepare', 'wave', 'joy', 'exit', 'speaking',
      'action-complete', '3d-ready', '3d-visible', '3d-fallback', '3d-loading', 'thinking',
    ];
    names.forEach(name =>
      document.addEventListener('skyy:' + name, () => {
        window.__skyy.events.push({ name, at: Math.round(performance.now() - window.__skyy.t0) });
      })
    );
  });
}

async function openPage(contextOptions, label) {
  const context = await browser.newContext(contextOptions);
  await instrument(context);
  const page = await context.newPage();
  const record = { label, pageErrors: [], consoleErrors: [], failedRequests: [], requests: [] };
  page.on('pageerror', error => record.pageErrors.push(String(error)));
  page.on('console', message => {
    if (message.type() === 'error') record.consoleErrors.push(message.text());
  });
  page.on('requestfailed', request => record.failedRequests.push(request.url() + ' :: ' + (request.failure() || {}).errorText));
  page.on('request', request => record.requests.push(request.url()));
  return { context, page, record };
}

const probe = () => ({
  stage: (() => {
    const stage = document.getElementById('skyyrose-mascot');
    if (!stage) return null;
    const rect = stage.getBoundingClientRect();
    return {
      hidden: stage.hidden,
      parent: stage.parentElement && stage.parentElement.id,
      state: stage.dataset.state,
      presence: stage.dataset.presence,
      renderer: stage.dataset.renderer,
      visibility: stage.dataset.visibility,
      rigTier: stage.dataset.rigTier,
      actionPhase: stage.dataset.actionPhase,
      shift: stage.style.getPropertyValue('--skyy-entry-shift'),
      rect: { x: Math.round(rect.left), y: Math.round(rect.top), w: Math.round(rect.width), h: Math.round(rect.height) },
    };
  })(),
  character: (() => {
    const el = document.getElementById('skyyrose-mascot-trigger');
    if (!el) return null;
    const rect = el.getBoundingClientRect();
    return { x: Math.round(rect.left), y: Math.round(rect.top), w: Math.round(rect.width), h: Math.round(rect.height) };
  })(),
  portrait: (() => {
    const img = document.querySelector('#skyyrose-mascot .skyyrose-mascot__image');
    if (!img) return null;
    const rect = img.getBoundingClientRect();
    return {
      complete: img.complete,
      naturalWidth: img.naturalWidth,
      opacity: getComputedStyle(img).opacity,
      display: getComputedStyle(img).display,
      inViewport: rect.bottom <= innerHeight && rect.right <= innerWidth && rect.top >= 0 && rect.width > 0,
    };
  })(),
  canvas: (() => {
    const canvas = document.getElementById('skyy-3d-canvas');
    if (!canvas) return null;
    const rect = canvas.getBoundingClientRect();
    return { hidden: canvas.hidden, opacity: getComputedStyle(canvas).opacity, display: getComputedStyle(canvas).display, x: Math.round(rect.left), w: Math.round(rect.width), h: Math.round(rect.height) };
  })(),
  dock: (() => {
    const dock = document.getElementById('skyy-hero-stage');
    if (!dock) return null;
    const rect = dock.getBoundingClientRect();
    const style = getComputedStyle(dock);
    return { position: style.position, zIndex: style.zIndex, visibility: style.visibility, right: Math.round(innerWidth - rect.right), bottom: Math.round(innerHeight - rect.bottom), x: Math.round(rect.left), y: Math.round(rect.top), w: Math.round(rect.width), h: Math.round(rect.height) };
  })(),
  header: (() => {
    const header = document.querySelector('.sr2-header, [data-site-header]');
    if (!header) return null;
    const rect = header.getBoundingClientRect();
    return { bottom: Math.round(rect.bottom), zIndex: getComputedStyle(header).zIndex };
  })(),
  recall: (() => {
    const recall = document.getElementById('skyyrose-mascot-recall');
    if (!recall) return null;
    const rect = recall.getBoundingClientRect();
    const style = getComputedStyle(recall);
    return { hidden: recall.hidden, display: style.display, position: style.position, visibility: style.visibility, w: Math.round(rect.width), h: Math.round(rect.height), right: Math.round(innerWidth - rect.right), bottom: Math.round(innerHeight - rect.bottom), text: recall.textContent.trim().replace(/\s+/g, ' ') };
  })(),
  buttons: [...document.querySelectorAll('#skyy-hero-stage button')].map(button => {
    const rect = button.getBoundingClientRect();
    const style = getComputedStyle(button);
    return { id: button.id, hidden: button.hidden, w: Math.round(rect.width), h: Math.round(rect.height), font: style.fontFamily.split(',')[0], size: style.fontSize, weight: style.fontWeight, transform: style.textTransform, border: style.borderTopColor };
  }),
  dialogOpen: (() => {
    const dialog = document.getElementById('skyy-ask-dialog');
    return dialog ? dialog.open : null;
  })(),
  active: document.activeElement && (document.activeElement.id || document.activeElement.tagName),
  session: (() => {
    try {
      return { dismissed: sessionStorage.getItem('skyy:dismissed'), entries: sessionStorage.getItem('skyy:entries') };
    } catch (_) {
      return null;
    }
  })(),
  rig: window.skyyRoseMascot3D
    ? { ready: window.skyyRoseMascot3D.isReady(), action: window.skyyRoseMascot3D.getCurrentAction(), tier: window.skyyRoseMascot3D.getRigTier(), render: window.skyyRoseMascot3D.getRenderState(), failure: window.skyyRoseMascot3D.getFailureReason() }
    : null,
  events: (window.__skyy || {}).events,
  status: (document.getElementById('skyy-presence-status') || {}).textContent,
});

async function waitFor(page, predicate, timeout, label) {
  const started = Date.now();
  let last;
  while (Date.now() - started < timeout) {
    last = await page.evaluate(probe);
    if (predicate(last)) return { ok: true, ms: Date.now() - started, probe: last };
    await sleep(120);
  }
  return { ok: false, ms: Date.now() - started, probe: last, label };
}

function dockClip(p, viewport) {
  const rect = p.stage && !p.stage.hidden ? p.stage.rect : p.dock;
  const x = Math.max(0, rect.x - 340);
  const y = Math.max(0, rect.y - 24);
  return { x, y, width: viewport.width - x, height: Math.min(viewport.height - y, rect.h + 48) };
}

let browser;

async function desktopFlow() {
  const viewport = { width: 1440, height: 900 };
  const { context, page, record } = await openPage({ viewport, deviceScaleFactor: 1 }, 'about-1440');
  const t0 = Date.now();
  await page.goto(`${BASE}?route=about&skyy=1`, { waitUntil: 'load' });
  record.loadMs = Date.now() - t0;
  // 1. Portrait immediately in the dock (mascot.js reparents on load).
  const mounted = await waitFor(page, p => p.stage && p.stage.parent === 'skyy-hero-stage', 5000, 'mounted');
  record.mounted = mounted;
  await page.screenshot({ path: path.join(EVID, 'about-1440-portrait.png') });
  await page.screenshot({ path: path.join(EVID, 'about-1440.png'), fullPage: true });
  // 2. Auto walk-in: rig live after ~4.5 s + load.
  const live = await waitFor(page, p => p.stage && p.stage.presence === 'live' && p.stage.renderer === '3d', 45000, 'live');
  record.live = { ok: live.ok, msAfterLoad: live.ms, probe: live.probe };
  // 3. Frames through the walk-in and the wave.
  const frames = [];
  const frameStart = Date.now();
  let index = 0;
  while (Date.now() - frameStart < 6500 && index < 14) {
    const p = await page.evaluate(probe);
    const file = `about-1440-frame-${String(index).padStart(2, '0')}.png`;
    await page.screenshot({ path: path.join(FRAMES, file), clip: dockClip(p, viewport) });
    frames.push({ file, at: Date.now() - frameStart, action: p.rig && p.rig.action, phase: p.stage.actionPhase, shift: p.stage.shift, canvasX: p.canvas && p.canvas.x, facing: null });
    index++;
    await sleep(320);
  }
  record.frames = frames;
  const settled = await waitFor(page, p => (p.events || []).some(e => e.name === 'action-complete'), 15000, 'action-complete');
  record.settled = { ok: settled.ok, events: settled.probe.events, action: settled.probe.rig && settled.probe.rig.action, phase: settled.probe.stage.actionPhase };
  await page.screenshot({ path: path.join(EVID, 'about-1440-live.png') });
  record.liveProbe = await page.evaluate(probe);
  // 4. Model request tier.
  record.modelRequests = record.requests.filter(url => /\.glb/.test(url));
  // 5. Ask Skyy → dialog; Escape → closes, focus returns.
  await page.click('#skyy-hero-chat');
  const opened = await waitFor(page, p => p.dialogOpen === true, 3000, 'dialog-open');
  record.dialog = { opened: opened.ok, stageParent: opened.probe.stage.parent, active: opened.probe.active, state: opened.probe.stage.state };
  await sleep(700);
  await page.screenshot({ path: path.join(EVID, 'about-1440-dialog.png') });
  await page.keyboard.press('Escape');
  const closed = await waitFor(page, p => p.dialogOpen === false && p.stage.parent === 'skyy-hero-stage', 4000, 'dialog-closed');
  record.dialog.closed = closed.ok;
  record.dialog.focusAfterClose = closed.probe.active;
  record.dialog.stageAfterClose = closed.probe.stage;
  // 6. Dismiss → stage hidden, recall shown, session memory, focus on recall.
  await page.click('#skyy-hero-dismiss');
  const dismissed = await waitFor(page, p => p.stage.hidden === true && p.recall && p.recall.hidden === false, 3000, 'dismissed');
  record.dismiss = { ok: dismissed.ok, stage: dismissed.probe.stage, recall: dismissed.probe.recall, session: dismissed.probe.session, active: dismissed.probe.active, rigRunning: dismissed.probe.rig && dismissed.probe.rig.render.running };
  await page.screenshot({ path: path.join(EVID, 'about-1440-dismissed.png') });
  // 7. Reload keeps her dismissed.
  await page.reload({ waitUntil: 'load' });
  await sleep(6000);
  const afterReload = await page.evaluate(probe);
  record.reload = { stage: afterReload.stage, recall: afterReload.recall, session: afterReload.session, modelRequestsAfterReload: record.requests.filter(url => /\.glb/.test(url)).length };
  // 8. Recall → clears dismissal, opens dialog; Escape → she stays in the dock.
  await page.click('#skyyrose-mascot-recall');
  const recalled = await waitFor(page, p => p.dialogOpen === true, 3000, 'recalled');
  record.recall = { opened: recalled.ok, session: recalled.probe.session, recallHidden: recalled.probe.recall.hidden };
  await page.keyboard.press('Escape');
  const backInDock = await waitFor(page, p => p.dialogOpen === false && p.stage.parent === 'skyy-hero-stage' && p.stage.hidden === false, 4000, 'back-in-dock');
  record.recall.backInDock = backInDock.ok;
  record.recall.afterClose = { stage: backInDock.probe.stage, recall: backInDock.probe.recall, active: backInDock.probe.active };
  await sleep(1500);
  await page.screenshot({ path: path.join(EVID, 'about-1440-recalled.png') });
  // 9. Render calls while hidden: emulate document.hidden for 2 s.
  const liveAgain = await waitFor(page, p => p.stage.renderer === '3d' && p.rig && p.rig.render.running, 20000, 'live-again');
  record.hiddenTest = { liveAgain: liveAgain.ok };
  if (liveAgain.ok) {
    const before = await page.evaluate(() => {
      Object.defineProperty(document, 'hidden', { configurable: true, get: () => true });
      document.dispatchEvent(new Event('visibilitychange'));
      return window.skyyRoseMascot3D.getRenderState().frames;
    });
    await sleep(2000);
    const after = await page.evaluate(() => window.skyyRoseMascot3D.getRenderState());
    await page.evaluate(() => {
      Object.defineProperty(document, 'hidden', { configurable: true, get: () => false });
      document.dispatchEvent(new Event('visibilitychange'));
    });
    await sleep(1200);
    const resumed = await page.evaluate(() => window.skyyRoseMascot3D.getRenderState());
    record.hiddenTest = { liveAgain: true, framesBefore: before, framesAfter2sHidden: after.frames, runningWhileHidden: after.running, renderCallsWhileHidden: after.frames - before, framesAfterResume: resumed.frames, runningAfterResume: resumed.running };
  }
  // 10. Pause control visible once 3D is ready.
  record.pause = await page.evaluate(() => {
    const toggle = document.getElementById('skyy-motion-toggle');
    return { hidden: toggle.hidden, text: toggle.textContent, pressed: toggle.getAttribute('aria-pressed') };
  });
  record.finalProbe = await page.evaluate(probe);
  results.scenarios['about-1440'] = record;
  await context.close();
}

async function mobileFlow() {
  const viewport = { width: 390, height: 844 };
  const { context, page, record } = await openPage({ viewport, deviceScaleFactor: 2, isMobile: true, hasTouch: true }, 'home-390');
  await page.goto(`${BASE}?route=home&skyy=1`, { waitUntil: 'load' });
  const mounted = await waitFor(page, p => p.stage && p.stage.parent === 'skyy-hero-stage', 5000, 'mounted');
  record.mounted = mounted.probe;
  await page.screenshot({ path: path.join(EVID, 'home-390-portrait.png') });
  const live = await waitFor(page, p => p.stage && p.stage.presence === 'live' && p.stage.renderer === '3d', 45000, 'live');
  record.live = { ok: live.ok, msAfterLoad: live.ms, probe: live.probe };
  const frames = [];
  const frameStart = Date.now();
  let index = 0;
  while (Date.now() - frameStart < 5500 && index < 10) {
    const p = await page.evaluate(probe);
    const file = `home-390-frame-${String(index).padStart(2, '0')}.png`;
    await page.screenshot({ path: path.join(FRAMES, file), clip: dockClip(p, viewport) });
    frames.push({ file, at: Date.now() - frameStart, action: p.rig && p.rig.action, phase: p.stage.actionPhase, shift: p.stage.shift, canvasX: p.canvas && p.canvas.x });
    index++;
    await sleep(320);
  }
  record.frames = frames;
  const settled = await waitFor(page, p => (p.events || []).some(e => e.name === 'action-complete'), 15000, 'action-complete');
  record.settled = { ok: settled.ok, events: settled.probe.events };
  await page.screenshot({ path: path.join(EVID, 'home-390-live.png') });
  await page.screenshot({ path: path.join(EVID, 'home-390.png'), fullPage: true });
  record.liveProbe = await page.evaluate(probe);
  record.modelRequests = record.requests.filter(url => /\.glb/.test(url));
  await page.tap('#skyy-hero-chat');
  const opened = await waitFor(page, p => p.dialogOpen === true, 3000, 'dialog-open');
  record.dialog = { opened: opened.ok, active: opened.probe.active };
  await sleep(600);
  await page.screenshot({ path: path.join(EVID, 'home-390-dialog.png') });
  await page.keyboard.press('Escape');
  const closed = await waitFor(page, p => p.dialogOpen === false && p.stage.parent === 'skyy-hero-stage', 4000, 'closed');
  record.dialog.closed = closed.ok;
  record.dialog.focusAfterClose = closed.probe.active;
  results.scenarios['home-390'] = record;
  await context.close();
}

async function reducedFlow() {
  const viewport = { width: 1440, height: 900 };
  const { context, page, record } = await openPage({ viewport, deviceScaleFactor: 1, reducedMotion: 'reduce' }, 'signature-1440-reduced');
  await page.goto(`${BASE}?route=signature&skyy=1`, { waitUntil: 'load' });
  await sleep(9000);
  record.probe = await page.evaluate(probe);
  record.modelRequests = record.requests.filter(url => /\.glb/.test(url));
  record.threeRequests = record.requests.filter(url => /three-r170|skyy-3d\.js|draco/.test(url));
  await page.screenshot({ path: path.join(EVID, 'signature-1440-reduced.png') });
  await page.screenshot({ path: path.join(EVID, 'signature-1440-reduced-full.png'), fullPage: true });
  results.scenarios['signature-1440-reduced'] = record;
  await context.close();
}

async function signatureFlow() {
  const viewport = { width: 1440, height: 900 };
  const { context, page, record } = await openPage({ viewport, deviceScaleFactor: 1 }, 'signature-1440');
  await page.goto(`${BASE}?route=signature&skyy=1`, { waitUntil: 'load' });
  const live = await waitFor(page, p => p.stage && p.stage.presence === 'live' && p.stage.renderer === '3d', 45000, 'live');
  record.live = { ok: live.ok, msAfterLoad: live.ms };
  const settled = await waitFor(page, p => (p.events || []).some(e => e.name === 'action-complete'), 15000, 'action-complete');
  record.settled = { ok: settled.ok, events: settled.probe.events };
  record.probe = await page.evaluate(probe);
  record.modelRequests = record.requests.filter(url => /\.glb/.test(url));
  await page.screenshot({ path: path.join(EVID, 'signature-1440-live.png') });
  await page.screenshot({ path: path.join(EVID, 'signature-1440.png'), fullPage: true });
  results.scenarios['signature-1440'] = record;
  await context.close();
}

(async () => {
  browser = await chromium.launch({ args: ARGS });
  try {
    await desktopFlow();
    await mobileFlow();
    await reducedFlow();
    await signatureFlow();
  } catch (error) {
    results.fatal = String(error && error.stack || error);
  } finally {
    await browser.close();
  }
  results.finishedAt = new Date().toISOString();
  fs.writeFileSync(path.join(EVID, 'verify-results.json'), JSON.stringify(results, null, 2));
  console.log(JSON.stringify(results, null, 2));
})();
