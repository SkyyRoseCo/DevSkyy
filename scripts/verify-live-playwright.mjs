#!/usr/bin/env node
/**
 * verify-live-playwright.mjs — JS-runtime-aware deep post-deploy verify.
 *
 * The deploy script's verify_live() checks HTTP 200 + size + PHP-error markers,
 * and Scrapling checks DOM structure — but NONE of them see a JavaScript
 * pageerror or a broken animation lifecycle. v1.5.21 deployed "green" while a
 * black-flash intro, a dead title, and a site-wide scroll-reveal break were all
 * live. This gate closes that hole: it loads each surface in a real browser,
 * counts pageerrors (minus an allowlist of known pre-existing noise), and runs
 * per-surface DOM lifecycle assertions. Non-zero exit lets the deploy's existing
 * auto_rollback() restore the previous theme.
 *
 * Usage:
 *   PW_VERIFY_SPEC_FILE=/path/to/spec.json node scripts/verify-live-playwright.mjs
 *   PW_VERIFY_SPEC='{...json...}'            node scripts/verify-live-playwright.mjs
 *   node scripts/verify-live-playwright.mjs /path/to/spec.json
 *
 * Spec shape:
 *   {
 *     "allowErrorPatterns": ["Unexpected token '<'", "grainy-gradients"],
 *     "maxPageErrors": 0,
 *     "surfaces": [
 *       { "name": "immersive-signature",
 *         "url": "https://skyyrose.co/experience-signature/",
 *         "waitMs": 9000,
 *         "evals": [
 *           { "desc": "intro overlay tears down", "expr": "!document.querySelector('.ic-overlay')" },
 *           { "desc": "room title revealed", "expr": "(()=>{const l=document.querySelector('.scene-title-overlay .scene-lockup');return !!l && getComputedStyle(l).opacity==='1';})()" }
 *         ]
 *       }
 *     ]
 *   }
 *
 * Exit codes: 0 = all surfaces pass; 1 = at least one surface failed
 * (pageerror over budget or an eval returned falsy); 3 = environment problem
 * (playwright/browser missing) — caller decides whether 3 blocks (default: warn).
 */

import { createRequire } from 'module';
import { readFileSync } from 'fs';
import { execFileSync } from 'child_process';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

// Playwright lives in frontend/node_modules. Linked worktrees (the deploy runs
// from one) usually have no node_modules, so after this checkout's frontend/
// fall back to the main checkout's — the parent of the shared git directory.
function mainCheckoutFrontend() {
  try {
    const common = execFileSync('git', ['rev-parse', '--path-format=absolute', '--git-common-dir'], {
      cwd: fileURLToPath(new URL('.', import.meta.url)),
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'ignore'],
    }).trim();
    return join(dirname(common), 'frontend') + '/';
  } catch {
    return null;
  }
}

const FRONTEND_CANDIDATES = process.env.PW_FRONTEND_ROOT
  ? [process.env.PW_FRONTEND_ROOT]
  : [...new Set([fileURLToPath(new URL('../frontend/', import.meta.url)), mainCheckoutFrontend()].filter(Boolean))];

function loadSpec() {
  const fileArg = process.argv[2] || process.env.PW_VERIFY_SPEC_FILE;
  if (fileArg) return JSON.parse(readFileSync(fileArg, 'utf8'));
  if (process.env.PW_VERIFY_SPEC) return JSON.parse(process.env.PW_VERIFY_SPEC);
  throw new Error('No spec: set PW_VERIFY_SPEC_FILE, PW_VERIFY_SPEC, or pass a spec path as argv[1].');
}

function cacheBust(url) {
  const sep = url.includes('?') ? '&' : '?';
  // Fixed-but-unique-per-run buster; Math.random is unavailable in some
  // sandboxes, so derive from time + pid which always vary between runs.
  return `${url}${sep}pwcb=${Date.now()}-${process.pid}`;
}

let chromium;
for (const root of FRONTEND_CANDIDATES) {
  try {
    ({ chromium } = createRequire(root)('playwright'));
    break;
  } catch {
    // Try the next candidate root.
  }
}
if (!chromium) {
  console.error(`[pw-verify] playwright not resolvable from ${FRONTEND_CANDIDATES.join(' or ')}`);
  process.exit(3);
}

const spec = loadSpec();
const allow = (spec.allowErrorPatterns || []).map((p) => new RegExp(p));
const maxErrors = spec.maxPageErrors ?? 0;
const surfaces = spec.surfaces || [];
if (!surfaces.length) {
  console.error('[pw-verify] spec has no surfaces');
  process.exit(1);
}

let browser;
try {
  browser = await chromium.launch();
} catch (e) {
  console.error(`[pw-verify] browser launch failed (run: npx playwright install chromium): ${e.message}`);
  process.exit(3);
}

let failed = 0;
const report = [];

for (const s of surfaces) {
  const ctx = await browser.newContext({
    viewport: { width: s.width || 1280, height: s.height || 800 },
    reducedMotion: 'no-preference',
  });
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', (e) => errs.push(e.message));
  page.on('console', (m) => { if (m.type() === 'error') errs.push(`[console] ${m.text()}`); });

  let surfaceFail = false;
  const detail = [];
  try {
    await page.goto(cacheBust(s.url), { waitUntil: 'domcontentloaded', timeout: s.gotoTimeoutMs || 60000 });
    if (s.waitMs) await page.waitForTimeout(s.waitMs);

    const newErrs = errs.filter((m) => !allow.some((re) => re.test(m)));
    if (newErrs.length > maxErrors) {
      surfaceFail = true;
      detail.push(`pageerrors ${newErrs.length} > budget ${maxErrors}: ${newErrs.slice(0, 4).join(' || ')}`);
    }

    for (const ev of s.evals || []) {
      let ok = false, val;
      try { val = await page.evaluate(`(()=>(${ev.expr}))()`); ok = !!val; }
      catch (e) { val = `eval-threw: ${e.message}`; ok = false; }
      if (!ok) { surfaceFail = true; detail.push(`FAIL "${ev.desc}" → ${JSON.stringify(val)}`); }
    }
  } catch (e) {
    surfaceFail = true;
    detail.push(`navigation/error: ${e.message}`);
  }
  await ctx.close();

  if (surfaceFail) failed++;
  report.push(`${surfaceFail ? '✗' : '✓'} ${s.name} (${s.url})${detail.length ? '\n    ' + detail.join('\n    ') : ''}`);
}

await browser.close();

console.log('[pw-verify] surfaces:\n' + report.join('\n'));
if (failed) {
  console.error(`[pw-verify] FAILED: ${failed}/${surfaces.length} surface(s) regressed`);
  process.exit(1);
}
console.log(`[pw-verify] PASS: ${surfaces.length}/${surfaces.length} surfaces clean`);
process.exit(0);
