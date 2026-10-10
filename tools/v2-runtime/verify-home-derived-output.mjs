/**
 * Derived-output parity for a deployed Home route.
 *
 * Filesystem parity (the theme bytes on the server) does not prove that the
 * page a browser receives is built from those bytes: optimizer-generated
 * critical CSS, concatenated bundles and cached HTML are derived outputs with
 * their own lifecycles. This script fetches the live Home HTML cache-busted
 * and checks, against the local theme tree:
 *
 *   1. the theme's own inline critical contract is present and byte-identical
 *      to assets/css/critical/home.min.css (placeholder resolved);
 *   2. the inline hero bootstrap is present, ignored by Boost's deferral, and
 *      byte-identical to assets/js/visual-recovery.min.js;
 *   3. directly served theme CSS/JS files match the local build (sha256);
 *   4. the first-view class set in the delivered DOM is covered by the inline
 *      contract (and reports what any optimizer-generated critical block
 *      covers, as information, never as a gate);
 *   5. the delivered script order places the bootstrap before the classic
 *      body script chain;
 *   6. every first-view font face the contract declares is preloaded with
 *      the identical href (a differing href downloads the face twice).
 *
 * Usage: node tools/v2-runtime/verify-home-derived-output.mjs --base=https://host [--theme=path] [--json=out.json]
 * Exit 1 on any parity failure.
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';

const args = Object.fromEntries(process.argv.slice(2).map((a) => { const m = a.match(/^--([^=]+)(?:=(.*))?$/); return m ? [m[1], m[2] ?? true] : [a, true]; }));
const base = String(args.base || '').replace(/\/$/, '');
if (!base) { console.error('--base=https://host is required'); process.exit(2); }
const themeDir = path.resolve(String(args.theme || 'wordpress-theme/skyyrose-flagship-2'));
const themeUri = `${base}/wp-content/themes/${path.basename(themeDir)}`;
const sha = (buffer) => crypto.createHash('sha256').update(buffer).digest('hex');
const fetchText = async (url) => { const r = await fetch(url, { headers: { 'user-agent': 'Mozilla/5.0 (Macintosh) Chrome/128 skyyrose-derived-output' } }); return { status: r.status, headers: Object.fromEntries(r.headers), body: Buffer.from(await r.arrayBuffer()) }; };

const failures = [];
const report = { base, checkedAt: new Date().toISOString() };
const cb = Date.now();
const home = await fetchText(`${base}/?cb=${cb}`);
const html = home.body.toString('utf8');
report.document = { status: home.status, bytes: home.body.length, server: home.headers.server, cache: home.headers['x-ac'] || home.headers['x-cache'] || null };
if (home.status !== 200) failures.push(`Home returned HTTP ${home.status}`);
const headEnd = html.indexOf('</head>');

// 1. Theme critical contract.
const localCritical = (await fs.readFile(path.join(themeDir, 'assets/css/critical/home.min.css'), 'utf8')).trim().replaceAll('__SKYYROSE2_ASSETS__', `${themeUri}/assets`);
const criticalMatch = html.match(/<style id="skyyrose2-critical-home">([\s\S]*?)<\/style>/);
report.themeCritical = { present: Boolean(criticalMatch), bytes: criticalMatch ? criticalMatch[1].length : 0, inHead: criticalMatch ? html.indexOf(criticalMatch[0]) < headEnd : false, matchesLocal: criticalMatch ? criticalMatch[1].trim() === localCritical : false };
if (!report.themeCritical.present) failures.push('theme critical contract missing from Home');
else if (!report.themeCritical.matchesLocal) failures.push('theme critical contract differs from the local build');
else if (!report.themeCritical.inHead) failures.push('theme critical contract is not in <head>');

// 2. Inline hero bootstrap.
const localController = (await fs.readFile(path.join(themeDir, 'assets/js/visual-recovery.min.js'), 'utf8')).trim();
const bootstrapMatch = html.match(/<script([^>]*id="skyyrose2-visual-recovery-early"[^>]*)>([\s\S]*?)<\/script>/);
const heroEnd = html.indexOf('</section>', html.indexOf('id="sr2-archive-arrival"'));
report.heroBootstrap = { present: Boolean(bootstrapMatch), boostIgnore: bootstrapMatch ? /data-jetpack-boost="ignore"/.test(bootstrapMatch[1]) : false, matchesLocal: bootstrapMatch ? bootstrapMatch[2].trim() === localController : false, afterHero: bootstrapMatch ? html.indexOf(bootstrapMatch[0]) > heroEnd && html.indexOf(bootstrapMatch[0]) - heroEnd < 200 : false, footerCopies: (html.match(/visual-recovery\.min\.js/g) || []).length };
if (!report.heroBootstrap.present) failures.push('inline hero bootstrap missing');
else { if (!report.heroBootstrap.boostIgnore) failures.push('inline hero bootstrap lacks data-jetpack-boost="ignore"'); if (!report.heroBootstrap.matchesLocal) failures.push('inline hero bootstrap differs from the local controller'); if (!report.heroBootstrap.afterHero) failures.push('inline hero bootstrap is not directly after the hero'); }
if (report.heroBootstrap.footerCopies > 0) failures.push('a footer copy of the hero controller is still delivered on Home');

// 3. Served theme files match local build.
const files = ['assets/css/design-tokens.min.css', 'assets/css/theme.min.css', 'assets/css/global-shell.min.css', 'assets/css/home-page.min.css', 'assets/css/controls.min.css', 'assets/css/visual-recovery.min.css', 'assets/css/collection-world.min.css', 'assets/css/mascot.min.css', 'assets/js/theme.min.js', 'assets/js/visual-recovery.min.js', 'assets/js/mascot-loader.min.js', 'assets/css/critical/home.min.css'];
report.files = [];
for (const file of files) {
  const local = sha(await fs.readFile(path.join(themeDir, file)));
  const served = await fetchText(`${themeUri}/${file}?cb=${cb}`);
  const remote = served.status === 200 ? sha(served.body) : null;
  report.files.push({ file, status: served.status, match: local === remote });
  if (local !== remote) failures.push(`served ${file} does not match the local build (HTTP ${served.status})`);
}

// 4. First-view coverage in the delivered DOM.
const firstView = html.slice(html.indexOf('<header'), heroEnd);
const classes = new Set();
for (const m of firstView.matchAll(/class="([^"]*)"/g)) for (const c of m[1].split(/\s+/)) if (/^(sr2|skyyrose)-/.test(c)) classes.add(c);
const navStart = firstView.indexOf('<nav id="sr2-menu"'); const navEnd = firstView.indexOf('</nav>', navStart);
const navClasses = new Set(); if (navStart !== -1) for (const m of firstView.slice(navStart, navEnd).matchAll(/class="([^"]*)"/g)) for (const c of m[1].split(/\s+/)) navClasses.add(c);
const covered = (css, c) => new RegExp(`\\.${c.replace(/[-]/g, '\\-')}(?![A-Za-z0-9_-])`).test(css);
const contractCss = criticalMatch ? criticalMatch[1] : '';
const boostMatch = html.match(/<style id="jetpack-boost-critical-css">([\s\S]*?)<\/style>/);
const boostCss = boostMatch ? boostMatch[1] : '';
const allowUnstyled = new Set(['sr2-header__bag-count', 'sr2-control--secondary', 'sr2-shell-links']);
const uncovered = [...classes].filter((c) => !navClasses.has(c) && !allowUnstyled.has(c) && !covered(contractCss, c));
report.coverage = { firstViewClasses: classes.size, uncoveredByContract: uncovered, boost: { present: Boolean(boostMatch), bytes: boostCss.length, uncovered: [...classes].filter((c) => !navClasses.has(c) && !covered(boostCss, c)).length } };
if (uncovered.length > 0) failures.push(`first-view classes not covered by the theme contract: ${uncovered.join(' ')}`);

// 5. Delivered script order.
const scripts = [...html.matchAll(/<script\b([^>]*)>/gi)].map((m, i) => ({ i, attrs: m[1], src: (m[1].match(/\ssrc=["']([^"']+)/) || [])[1] || '', id: (m[1].match(/\sid=["']([^"']+)/) || [])[1] || '' }));
const bootstrapIndex = scripts.findIndex((s) => s.id === 'skyyrose2-visual-recovery-early');
const headScripts = scripts.filter((s) => html.indexOf(`<script${s.attrs}>`) < headEnd && s.src).map((s) => s.src.split('/').pop());
// The hero bootstrap must precede every classic body script it used to wait behind.
const laterChain = /jquery-migrate|underscore|wp-util|add-to-cart-variation|_jb_static|theme\.min\.js|jquery(\.min)?\.js/;
const firstChainIndex = scripts.findIndex((s) => laterChain.test(s.src) && html.indexOf(`<script${s.attrs}>`) > headEnd);
report.scriptOrder = { bootstrapIndex, firstBodyChainIndex: firstChainIndex, headScripts, bootstrapBeforeBodyChain: bootstrapIndex !== -1 && (firstChainIndex === -1 || bootstrapIndex < firstChainIndex) };
if (!report.scriptOrder.bootstrapBeforeBodyChain) failures.push('hero bootstrap is not delivered before the classic body script chain');

// 6. First-view font preloads equal the inline @font-face URLs.
const faceUrls = [...contractCss.matchAll(/@font-face\{[^}]*?src:url\(["']?([^"')]+)["']?\)/g)].map((m) => m[1]).filter((u) => /archivo-latin|hanken-grotesk-latin|anton-latin|cinzel-latin/.test(u));
const preloadLinks = [...html.slice(0, headEnd).matchAll(/<link\b([^>]*rel=["']preload["'][^>]*)>/gi)].map((m) => m[1]);
const fontPreloads = preloadLinks.filter((a) => /as=["']font["']/.test(a)).map((a) => ({ href: (a.match(/href=["']([^"']+)/) || [])[1] || '', crossorigin: /crossorigin/.test(a) }));
report.fontPreloads = { expected: faceUrls, present: fontPreloads };
for (const url of faceUrls) { const hit = fontPreloads.find((p) => p.href === url); if (!hit) failures.push(`first-view font is not preloaded with its @font-face href: ${url}`); else if (!hit.crossorigin) failures.push(`font preload lacks crossorigin: ${url}`); }

report.failures = failures;
if (args.json) await fs.writeFile(String(args.json), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2));
if (failures.length > 0) { console.error(`\nDERIVED OUTPUT PARITY: FAIL (${failures.length})`); process.exit(1); }
console.log('\nDERIVED OUTPUT PARITY: PASS');
