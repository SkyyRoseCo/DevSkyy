/** Prevent a no-JS fallback flash while deferred scripts are still downloading. */
import { createRequire } from 'node:module';
import path from 'node:path';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const require = createRequire(path.resolve('.artifacts/v2-phase3-20260905/qa/package.json'));
const { chromium } = require('playwright');
const base = 'http://127.0.0.1:18303';
const browser = await chromium.launch();
const evidence = {};
let releaseScript;
try {
 const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
 await context.route('**/*', r => new URL(r.request().url()).origin === base ? r.continue() : r.abort());
 const pending = new Promise(resolve => { releaseScript = resolve; });
 await context.route('**/theme.min.js*', async r => { await pending; await r.continue(); });
 const page = await context.newPage();
 await page.goto(base, { waitUntil: 'commit' });
 await page.locator('[data-sr2-nav]').waitFor({ state: 'attached' });
 await page.waitForFunction(() => [...document.styleSheets].some(s => s.href?.includes('global-shell.min.css')));
 evidence.deferred = await page.locator('[data-sr2-nav]').evaluate(e => ({ visibility: getComputedStyle(e).visibility, position: getComputedStyle(e).position, scripting: matchMedia('(scripting: enabled)').matches, initialized: document.documentElement.classList.contains('sr2-motion-ready') }));
 assert(evidence.deferred.scripting && !evidence.deferred.initialized);
 assert.equal(evidence.deferred.visibility, 'hidden');
 assert.equal(evidence.deferred.position, 'fixed');
 releaseScript();
 await page.waitForLoadState('load');
 await page.locator('[data-sr2-menu]').click();
 assert(await page.locator('[data-sr2-nav]').isVisible());
 await context.close();
 const nojs = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 390, height: 844 } });
 await nojs.route('**/*', r => new URL(r.request().url()).origin === base ? r.continue() : r.abort());
 const plain = await nojs.newPage();
 await plain.goto(base);
 assert(await plain.locator('[data-sr2-nav]').isVisible());
 assert.equal(await plain.locator('[data-sr2-nav]').evaluate(e => getComputedStyle(e).position), 'static');
 evidence.noJavaScript = 'visible in-flow navigation';
 await nojs.close();
 evidence.status = 'PASS';
} catch (error) { evidence.status = 'FAIL'; evidence.error = error.stack; throw error; }
finally { releaseScript?.(); await fs.writeFile('.artifacts/v2-phase3-20260905/startup-browser.json', JSON.stringify(evidence, null, 2)); await browser.close(); }
console.log(JSON.stringify(evidence));
