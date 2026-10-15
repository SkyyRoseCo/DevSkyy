/**
 * Cold film-delivery sampling for the Home hero (platform-owned variable).
 *
 * Every sample uses a fresh browser context (empty HTTP cache) and lets the
 * page request the film naturally, so the numbers describe what a first-time
 * visitor's browser sees: request start relative to navigation, DNS, connect,
 * TLS, time to first byte, transfer end, CDN headers, protocol, and the video
 * element's loadstart → canplay → playing → first painted frame sequence.
 * The CDN cache header is recorded, never trusted: a HIT still has to be
 * transferred, and a MISS is what a cold edge serves.
 *
 * Usage: node tools/v2-runtime/measure-film-delivery.mjs --base=https://host [--samples=6] [--widths=390,1440] [--browser=chromium] [--json=out.json]
 */
import fs from 'node:fs';
import { loadPlaywright } from './load-playwright.mjs';
const playwright = loadPlaywright();

const args = Object.fromEntries(process.argv.slice(2).map((a) => { const m = a.match(/^--([^=]+)(?:=(.*))?$/); return m ? [m[1], m[2] ?? true] : [a, true]; }));
const base = String(args.base || '').replace(/\/$/, '');
if (!base) { console.error('--base is required'); process.exit(2); }
const samples = Number(args.samples || 6);
const widths = String(args.widths || '390,1440').split(',').map(Number);
const browserName = String(args.browser || 'chromium');
const FILM = /collection-heroes\/.*\.(webm|mp4)(\?|$)/;

const init = () => {
  const log = { events: {} };
  window.__film = log;
  const T = () => +performance.now().toFixed(1);
  const hook = (video) => {
    if (video.__hooked) return; video.__hooked = true;
    for (const ev of ['loadstart', 'loadedmetadata', 'canplay', 'playing', 'error']) video.addEventListener(ev, () => { if (!(ev in log.events)) log.events[ev] = T(); });
    video.addEventListener('playing', () => { if (video.requestVideoFrameCallback) video.requestVideoFrameCallback(() => { log.events.firstFrame = T(); }); else log.events.firstFrame = T(); }, { once: true });
  };
  const find = () => { const v = document.querySelector('[data-recovery-hero-video]'); if (v) hook(v); };
  new MutationObserver(find).observe(document, { childList: true, subtree: true });
  document.addEventListener('DOMContentLoaded', find);
};

const browser = await playwright[browserName].launch();
const rows = [];
for (const width of widths) {
  const height = width < 768 ? Math.round(width * 2.16) : 900;
  for (let i = 0; i < samples; i += 1) {
    const context = await browser.newContext({ viewport: { width, height }, deviceScaleFactor: width < 768 ? 3 : 1, hasTouch: width < 768, isMobile: width < 768 && browserName === 'chromium' });
    await context.addInitScript(init);
    const page = await context.newPage();
    let navStart = null; let filmReq = null; let filmResp = null;
    page.on('request', (r) => { if (r.isNavigationRequest() && navStart === null) navStart = Date.now(); if (FILM.test(r.url()) && !filmReq) filmReq = { request: r, sentAt: Date.now() }; });
    page.on('response', (r) => { if (FILM.test(r.url()) && !filmResp) filmResp = r; });
    const t0 = Date.now();
    await page.goto(`${base}/?film=${Date.now()}-${width}-${i}`, { waitUntil: 'load' }).catch(() => {});
    await page.waitForTimeout(6000);
    const events = await page.evaluate(() => window.__film?.events || {}).catch(() => ({}));
    const row = { width, sample: i, filmRequested: Boolean(filmReq) };
    if (filmReq) {
      const t = filmReq.request.timing();
      const h = filmResp ? filmResp.headers() : {};
      row.requestStartMs = filmReq.sentAt - (navStart ?? t0);
      row.dns = t.domainLookupEnd >= 0 ? +(t.domainLookupEnd - t.domainLookupStart).toFixed(1) : null;
      row.connect = t.connectEnd >= 0 ? +(t.connectEnd - t.connectStart).toFixed(1) : null;
      row.tls = t.secureConnectionStart >= 0 && t.connectEnd >= 0 ? +(t.connectEnd - t.secureConnectionStart).toFixed(1) : null;
      row.ttfb = t.responseStart >= 0 ? +t.responseStart.toFixed(1) : null;
      row.responseEnd = t.responseEnd >= 0 ? +t.responseEnd.toFixed(1) : null;
      row.status = filmResp ? filmResp.status() : null;
      row.bytes = h['content-length'] ? Number(h['content-length']) : null;
      row.contentRange = h['content-range'] || null;
      row.cdn = { xac: h['x-ac'] || null, xcache: h['x-cache'] || null, age: h['age'] || null, cacheControl: h['cache-control'] || null, cf: h['cf-cache-status'] || null };
      row.protocol = null;
      try { const sd = await filmResp?.securityDetails(); row.tlsProtocol = sd?.protocol || null; } catch { row.tlsProtocol = null; }
      try { const sa = await filmResp?.serverAddr(); row.server = sa ? `${sa.ipAddress}:${sa.port}` : null; } catch { row.server = null; }
      row.events = events;
    }
    rows.push(row);
    console.log(JSON.stringify(row));
    await context.close();
  }
}
await browser.close();
const stat = (key, w) => { const v = rows.filter((r) => r.width === w).map((r) => (key.includes('.') ? key.split('.').reduce((o, k) => o?.[k], r) : r[key])).filter((x) => typeof x === 'number'); if (!v.length) return null; const s = [...v].sort((a, b) => a - b); return { median: s[Math.floor(s.length / 2)], min: s[0], max: s[s.length - 1], n: s.length }; };
const summary = {};
for (const w of widths) summary[w] = Object.fromEntries(['requestStartMs', 'dns', 'connect', 'tls', 'ttfb', 'responseEnd', 'events.loadstart', 'events.canplay', 'events.playing', 'events.firstFrame'].map((k) => [k, stat(k, w)]));
const out = { base, browser: browserName, samples, generatedAt: new Date().toISOString(), rows, summary, note: 'Cold = fresh browser context per sample (empty HTTP cache); CDN headers recorded, not trusted.' };
if (args.json) fs.writeFileSync(String(args.json), JSON.stringify(out, null, 2));
console.log(JSON.stringify(summary, null, 2));
