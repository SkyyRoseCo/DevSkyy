/**
 * Home critical-rendering + cinematic-startup measurement harness.
 *
 * Local lab samples, not field Core Web Vitals or a launch certificate.
 * Records, per viewport width and sample: CLS (with shift sources), FCP, LCP
 * candidates, first-paint and settled geometry of the first-view elements,
 * hero controller initialisation time, film request/TTFB/first composited
 * frame, the delivered script chain, font readiness, first-paint and settled
 * screenshots, and (sample 0) a startup recording.
 *
 * Usage:
 *   node tools/v2-runtime/measure-home-critical.mjs --base=http://127.0.0.1:18330 \
 *     --label=before --out=.artifacts/home-critical-20260907 [--widths=320,390,414,768,1440] \
 *     [--samples=3] [--browser=chromium|webkit] [--route=/] [--allow-external] [--settle=4000]
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import { loadPlaywright } from './load-playwright.mjs';

const args = Object.fromEntries(process.argv.slice(2).map((a) => {
  const m = a.match(/^--([^=]+)(?:=(.*))?$/);
  return m ? [m[1], m[2] ?? true] : [a, true];
}));
const base = String(args.base || 'http://127.0.0.1:18330').replace(/\/$/, '');
const label = String(args.label || 'sample');
const out = path.resolve(String(args.out || '.artifacts/home-critical'));
const widths = String(args.widths || '320,390,414,768,1440').split(',').map(Number);
const samples = Number(args.samples || 3);
const browserName = String(args.browser || 'chromium');
const route = String(args.route || '/');
const allowExternal = Boolean(args['allow-external']);
const settleMs = Number(args.settle || 4000);

const playwright = loadPlaywright();
const engine = playwright[browserName];
if (!engine) throw new Error(`Unknown browser ${browserName}`);

const WATCHED = {
  header: '[data-site-header]',
  brandMark: '.sr2-header__brand-mark',
  hero: '#sr2-archive-arrival',
  heroImage: '#sr2-archive-arrival .sr2-archive-scene__image img',
  title: '#sr2-archive-title',
  intro: '.sr2-archive-scene__intro',
  primaryCta: '.sr2-archive-scene__actions .sr2-control--primary',
  secondaryCta: '.sr2-archive-scene__actions .sr2-control--secondary',
  worlds: '.sr2-archive-scene__worlds',
  concierge: '#skyy-hero-stage',
  askSkyy: '#skyyrose-mascot-recall',
};

const initScript = ({ watched }) => {
  const T = () => performance.now();
  const rect = (el) => { const r = el.getBoundingClientRect(); return { x: +r.x.toFixed(1), y: +r.y.toFixed(1), w: +r.width.toFixed(1), h: +r.height.toFixed(1) }; };
  const describe = (node) => {
    if (!node || !node.tagName) return String(node);
    const id = node.id ? `#${node.id}` : '';
    const cls = node.classList && node.classList.length ? '.' + [...node.classList].slice(0, 3).join('.') : '';
    return `${node.tagName.toLowerCase()}${id}${cls}`;
  };
  const log = window.__homeCritical = { shifts: [], paint: [], lcp: [], longTasks: [], geometry: [], film: {}, controller: {}, fonts: {}, errors: [] };
  document.addEventListener('DOMContentLoaded', () => { log.domContentLoaded = +T().toFixed(1); });
  window.addEventListener('load', () => { log.load = +T().toFixed(1); });
  if (document.fonts) document.fonts.ready.then(() => { log.fonts.ready = +T().toFixed(1); });
  const observe = (type, fn) => {
    if (!('PerformanceObserver' in window) || !PerformanceObserver.supportedEntryTypes.includes(type)) return;
    new PerformanceObserver((list) => list.getEntries().forEach(fn)).observe({ type, buffered: true });
  };
  observe('layout-shift', (e) => log.shifts.push({
    t: +e.startTime.toFixed(1), value: +e.value.toFixed(5), hadRecentInput: e.hadRecentInput,
    sources: (e.sources || []).map((s) => ({ node: describe(s.node), from: s.previousRect && { y: s.previousRect.y, h: s.previousRect.height }, to: s.currentRect && { y: s.currentRect.y, h: s.currentRect.height } })).slice(0, 6),
  }));
  observe('paint', (e) => log.paint.push({ name: e.name, t: +e.startTime.toFixed(1) }));
  observe('largest-contentful-paint', (e) => log.lcp.push({ t: +e.startTime.toFixed(1), size: e.size, element: describe(e.element), url: e.url ? new URL(e.url, location.href).pathname : '' }));
  observe('longtask', (e) => log.longTasks.push({ t: +e.startTime.toFixed(1), d: +e.duration.toFixed(1) }));
  window.addEventListener('error', (e) => log.errors.push(String(e.message)));

  // Geometry timeline of first-view elements: one snapshot per animation frame
  // until 'load' + 1.5s. The first snapshot with a painted hero is the
  // first-paint geometry; the last is the settled geometry.
  let lastKey = '';
  const snap = () => {
    const g = {};
    for (const [k, sel] of Object.entries(watched)) { const el = document.querySelector(sel); if (el) g[k] = rect(el); }
    const key = JSON.stringify(g);
    if (key !== lastKey) { lastKey = key; log.geometry.push({ t: +T().toFixed(1), g }); }
  };
  let stop = false;
  const loop = () => { if (stop) return; snap(); requestAnimationFrame(loop); };
  requestAnimationFrame(loop);
  window.addEventListener('load', () => setTimeout(() => { stop = true; snap(); }, 1500));

  // Hero controller initialisation (the controller stamps documentElement).
  // The init script runs before <html> exists, so observe the document node.
  const checkRoot = () => {
    const root = document.documentElement; if (!root) return;
    if (root.dataset.recoveryInitialized && !log.controller.initialized) log.controller.initialized = +T().toFixed(1);
    if (root.classList.contains('sr2-motion-ready') && !log.controller.themeReady) log.controller.themeReady = +T().toFixed(1);
  };
  new MutationObserver(checkRoot).observe(document, { attributes: true, subtree: true, attributeFilter: ['data-recovery-initialized', 'class'] });

  // Film lifecycle.
  const hookVideo = (video) => {
    if (video.__hooked) return; video.__hooked = true;
    const f = log.film;
    for (const ev of ['loadstart', 'loadedmetadata', 'loadeddata', 'canplay', 'playing', 'pause', 'error']) video.addEventListener(ev, () => { if (!(ev in f)) f[ev] = +T().toFixed(1); });
    video.addEventListener('playing', () => {
      if (video.requestVideoFrameCallback) video.requestVideoFrameCallback((now, meta) => { if (!f.firstFrame) f.firstFrame = +T().toFixed(1); });
      else if (!f.firstFrame) f.firstFrame = +T().toFixed(1);
    }, { once: true });
    new MutationObserver(() => { if (video.currentSrc && !f.currentSrc) { f.currentSrc = new URL(video.currentSrc).pathname; f.srcAssigned = +T().toFixed(1); } }).observe(video, { attributes: true, childList: true, subtree: true });
  };
  const findVideo = () => { const v = document.querySelector('[data-recovery-hero-video]'); if (v) hookVideo(v); };
  new MutationObserver(findVideo).observe(document, { childList: true, subtree: true });
  document.addEventListener('DOMContentLoaded', findVideo);
};

const summarize = async (page) => page.evaluate((watched) => {
  const log = window.__homeCritical;
  const clsAll = log.shifts.reduce((a, s) => a + s.value, 0);
  const cls = log.shifts.filter((s) => !s.hadRecentInput).reduce((a, s) => a + s.value, 0);
  const fcp = log.paint.find((p) => p.name === 'first-contentful-paint')?.t ?? null;
  const lcp = log.lcp.length ? log.lcp[log.lcp.length - 1] : null;
  const nav = performance.getEntriesByType('navigation')[0];
  const res = performance.getEntriesByType('resource');
  const filmEntry = res.find((r) => /collection-heroes\/.*\.(webm|mp4)(\?|$)/.test(r.name));
  const film = {
    ...log.film,
    request: filmEntry ? { path: new URL(filmEntry.name).pathname, start: +filmEntry.startTime.toFixed(1), requestStart: +filmEntry.requestStart.toFixed(1), ttfb: +filmEntry.responseStart.toFixed(1), end: +filmEntry.responseEnd.toFixed(1), transfer: filmEntry.transferSize, decoded: filmEntry.decodedBodySize, protocol: filmEntry.nextHopProtocol } : null,
  };
  const scripts = [...document.scripts].map((s, i) => {
    const src = s.src ? new URL(s.src).pathname : '';
    const timing = s.src ? res.find((r) => r.name === s.src) : null;
    return { i, src: src || (s.type && s.type !== 'text/javascript' && s.type !== 'module' ? `(inline ${s.type})` : `(inline${s.id ? ' #' + s.id : ''})`), defer: s.defer, async: s.async, boostIgnore: s.dataset.jetpackBoost || '', start: timing ? +timing.startTime.toFixed(1) : null, end: timing ? +timing.responseEnd.toFixed(1) : null };
  });
  const styles = [...document.querySelectorAll('link[rel=stylesheet],style')].map((s) => ({ tag: s.tagName.toLowerCase(), id: s.id || '', media: s.media || '', href: s.href ? new URL(s.href).pathname + (s.href.includes('??') ? '??' : '') : '', bytes: s.tagName === 'STYLE' ? s.textContent.length : null }));
  const fontsLoaded = document.fonts ? [...document.fonts].filter((f) => f.status === 'loaded').map((f) => `${f.family} ${f.weight}`) : [];
  const fontRes = res.filter((r) => /\.woff2?(\?|$)/.test(r.name)).map((r) => ({ path: new URL(r.name).pathname, start: +r.startTime.toFixed(1), end: +r.responseEnd.toFixed(1) }));
  const title = document.querySelector(watched.title);
  const titleFont = title ? getComputedStyle(title).fontFamily : '';
  const first = log.geometry.find((s) => s.g.hero && s.g.hero.h > 0) || log.geometry[0];
  const settled = log.geometry[log.geometry.length - 1];
  const geometryDelta = {};
  if (first && settled) for (const k of Object.keys(settled.g)) {
    const a = first.g[k], b = settled.g[k];
    if (a && b) geometryDelta[k] = { firstPaint: a, settled: b, dy: +(b.y - a.y).toFixed(1), dh: +(b.h - a.h).toFixed(1) };
  }
  return {
    cls: +clsAll.toFixed(4), clsNoRecentInput: +cls.toFixed(4), fcp, lcp, ttfb: nav ? +nav.responseStart.toFixed(1) : null, domContentLoaded: log.domContentLoaded ?? null, load: log.load ?? null,
    controller: log.controller, film, shifts: log.shifts.slice(0, 12), longTasks: log.longTasks.length,
    geometryFirstPaintAt: first?.t ?? null, geometrySnapshots: log.geometry.length, geometryDelta,
    scripts, styles, fonts: { ready: log.fonts.ready ?? null, loaded: fontsLoaded, resources: fontRes, titleFontFamily: titleFont, titleUsesArchivo: document.fonts ? document.fonts.check('600 64px Archivo') : null },
    errors: log.errors,
  };
}, WATCHED);

await fs.mkdir(out, { recursive: true });
const browser = await engine.launch({ headless: true });
const results = [];
try {
  for (const width of widths) {
    for (let sample = 0; sample < samples; sample++) {
      const mobile = width <= 480;
      const height = mobile ? Math.round(width * 2.16) : width >= 1200 ? 900 : 1024;
      const dir = path.join(out, label, `${browserName}-${width}-s${sample}`);
      await fs.mkdir(dir, { recursive: true });
      const context = await browser.newContext({
        viewport: { width, height },
        deviceScaleFactor: mobile ? 3 : 1,
        isMobile: mobile && browserName === 'chromium',
        hasTouch: mobile,
        userAgent: mobile ? 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1' : undefined,
        recordVideo: sample === 0 ? { dir, size: { width: Math.min(width, 1440), height: Math.min(height, 900) } } : undefined,
      });
      if (!allowExternal) await context.route('**/*', (r) => new URL(r.request().url()).origin === base ? r.continue() : r.abort());
      await context.addInitScript(initScript, { watched: WATCHED });
      const page = await context.newPage();
      const responses = {};
      const consoleLog = [];
      page.on('console', (m) => { if (['error', 'warning'].includes(m.type())) consoleLog.push(`${m.type()}: ${m.text().slice(0, 300)}`); });
      page.on('pageerror', (e) => consoleLog.push(`pageerror: ${String(e.message).slice(0, 300)}`));
      page.on('requestfailed', (r) => consoleLog.push(`requestfailed: ${new URL(r.url()).pathname} ${r.failure()?.errorText || ''}`));
      let navStartEpoch = null;
      page.on('request', (req) => {
        const u = req.url();
        if (u.startsWith(`${base}${route}?${cb}`) && req.isNavigationRequest() && navStartEpoch === null) navStartEpoch = Date.now();
        if (/collection-heroes\/.*\.(webm|mp4)(\?|$)/.test(u) && !responses.filmRequest) responses.filmRequest = { url: new URL(u).pathname, sentAt: navStartEpoch === null ? null : Date.now() - navStartEpoch, request: req };
      });
      page.on('response', (resp) => {
        const u = resp.url();
        if (/collection-heroes\/.*\.(webm|mp4)(\?|$)/.test(u)) responses.film = { url: new URL(u).pathname, status: resp.status(), headers: resp.headers() };
        if (u === base + route || u === base + route + '?' + (page.__cb || '')) responses.document = { status: resp.status(), headers: resp.headers() };
      });
      const cb = `cb=${Date.now()}-${width}-${sample}`;
      page.__cb = cb;
      const t0 = Date.now();
      await page.goto(`${base}${route}?${cb}`, { waitUntil: 'commit' });
      // First-paint screenshot: as soon as FCP is observed.
      let firstPaintShotAt = null;
      try {
        await page.waitForFunction(() => window.__homeCritical && window.__homeCritical.paint.some((p) => p.name === 'first-contentful-paint'), null, { timeout: 15000 });
        firstPaintShotAt = Date.now() - t0;
        await page.screenshot({ path: path.join(dir, 'first-paint.png'), fullPage: false });
      } catch (e) { firstPaintShotAt = `no FCP within 15s: ${e.message.split('\n')[0]}`; }
      await page.waitForLoadState('load', { timeout: 60000 }).catch(() => {});
      await page.waitForTimeout(settleMs);
      await page.screenshot({ path: path.join(dir, 'settled.png'), fullPage: false });
      const summary = await summarize(page);
      if (responses.filmRequest) {
        const req = responses.filmRequest.request; const t = req.timing();
        const docTiming = (await (async () => { try { return await page.evaluate(() => performance.timeOrigin); } catch { return null; } })());
        summary.film.request = {
          path: responses.filmRequest.url, sentAt: responses.filmRequest.sentAt,
          start: docTiming && t.startTime > 0 ? +(t.startTime - docTiming).toFixed(1) : null,
          dns: t.domainLookupEnd >= 0 ? +(t.domainLookupEnd - t.domainLookupStart).toFixed(1) : null,
          connect: t.connectEnd >= 0 ? +(t.connectEnd - t.connectStart).toFixed(1) : null,
          ttfb: t.responseStart >= 0 ? +t.responseStart.toFixed(1) : null,
          responseEnd: t.responseEnd >= 0 ? +t.responseEnd.toFixed(1) : null,
          protocol: responses.film?.headers?.[':protocol'] || null,
        };
        delete responses.filmRequest.request;
      }
      summary.video = await page.evaluate(() => { const v = document.querySelector('[data-recovery-hero-video]'); return v ? { readyState: v.readyState, networkState: v.networkState, paused: v.paused, currentSrc: v.currentSrc ? new URL(v.currentSrc).pathname : '', error: v.error ? v.error.code : null, ready: v.closest('[data-recovery-hero]')?.classList.contains('is-hero-video-ready'), motion: v.closest('[data-recovery-hero]')?.dataset.recoveryMotion } : null; });
      summary.controller.finalInitialized = await page.evaluate(() => document.documentElement.dataset.recoveryInitialized || null);
      const raw = await (await context.request.get(`${base}${route}?raw-${cb}`)).text();
      const headEnd = raw.indexOf('</head>');
      summary.deliveredScripts = [...raw.matchAll(/<script\b([^>]*)>/gi)].map((m, i) => {
        const a = m[1]; const src = a.match(/\ssrc=["']([^"']+)/); const id = a.match(/\sid=["']([^"']+)/);
        return { i, where: m.index < headEnd ? 'head' : 'body', src: src ? new URL(src[1], base).pathname + (src[1].includes('??') ? '??' + src[1].split('??')[1].slice(0, 10) : '') : `(inline${id ? ' #' + id[1] : ''})`, attrs: ['defer', 'async', 'type="module"', 'data-jetpack-boost'].filter((k) => a.includes(k)).join(' ') };
      });
      summary.deliveredStyles = [...raw.matchAll(/<(link|style)\b([^>]*)>/gi)].filter((m) => m[1] === 'style' || /rel=["']stylesheet/.test(m[2])).map((m) => ({ tag: m[1], where: m.index < headEnd ? 'head' : 'body', id: (m[2].match(/\sid=["']([^"']+)/) || [])[1] || '', media: (m[2].match(/\smedia=["']([^"']+)/) || [])[1] || '', noscript: raw.lastIndexOf('<noscript>', m.index) > raw.lastIndexOf('</noscript>', m.index) }));
      const record = { label, browser: browserName, width, height, sample, url: `${base}${route}`, firstPaintShotAt, console: consoleLog.slice(0, 40), documentHeaders: responses.document?.headers || null, filmResponse: responses.film || null, ...summary };
      await fs.writeFile(path.join(dir, 'summary.json'), JSON.stringify(record, null, 2));
      results.push(record);
      const video = page.video();
      await context.close();
      if (video) { const p = await video.path(); await fs.rename(p, path.join(dir, 'startup.webm')).catch(() => {}); }
      console.log([label, browserName, width, `s${sample}`, `CLS=${record.cls}`, `FCP=${record.fcp}`, `LCP=${record.lcp?.t}(${record.lcp?.element})`, `ctrl=${record.controller.initialized ?? '-'}`, `film req=${record.film.request?.start ?? '-'} ttfb=${record.film.request?.ttfb ?? '-'} frame=${record.film.firstFrame ?? '-'}`].join('  '));
    }
  }
} finally { await browser.close(); }
await fs.writeFile(path.join(out, `${label}-${browserName}.json`), JSON.stringify({ base, route, label, browser: browserName, generatedAt: new Date().toISOString(), limitations: 'Lab samples in headless browsers on the local machine. Not field data.', results }, null, 2));
console.log(`wrote ${path.join(out, `${label}-${browserName}.json`)} (${results.length} samples)`);
