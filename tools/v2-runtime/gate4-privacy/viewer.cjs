'use strict';
// Local pinned viewer validation; only sanitized archives are accepted.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { spawn } = require('node:child_process');
const { chromium } = require('../phase3b-browser/node_modules/playwright');
const { startTraceViewerServer } = require('../phase3b-browser/node_modules/playwright/node_modules/playwright-core/lib/server/trace/viewer/traceViewer.js');
const root = path.resolve(__dirname, '../../..');
const privateRoot = path.join(root, '.artifacts/release-gates-20261019/gate4-privacy');
const port = 18474;
const attempt = process.argv[2] === '--worker' ? process.argv[4] : String(Date.now());
assert.ok(/^\d+$/.test(attempt));
const binary = '/Users/theceo/Library/Caches/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-mac-arm64/chrome-headless-shell';
async function worker(run) {
  assert.ok(/^\d+$/.test(run));
  const receiptDir = path.join(privateRoot, run, 'viewer-' + attempt); fs.mkdirSync(receiptDir, { recursive: true });
  const browser = await chromium.launch({ headless: true, executablePath: binary });
  const results = [];
  try {
    for (const mode of ['clean','tainted']) {
      const trace = path.join(privateRoot, run, mode + '-accepted/trace.zip');
      const context = await browser.newContext(); const page = await context.newPage();
      const errors = []; page.on('pageerror', error => errors.push(error.message));
      const responses = [];
      page.on('response', response => { if (response.url().includes('/contexts?')) responses.push(response); });
      await page.goto('http://127.0.0.1:' + port + '/trace/index.html?trace=' + encodeURIComponent('file?path=' + encodeURIComponent(trace)));
      await page.waitForFunction(() => document.body.textContent.includes('Actions') && !document.body.textContent.includes('Loading trace'), { timeout: 15000 });
      await page.waitForTimeout(500);
      const body = await page.locator('body').innerText();
      fs.writeFileSync(path.join(receiptDir, mode + '-body.txt'), body);
      assert.ok(body.includes('goto') || body.includes('Navigate'));
      await page.getByText('Navigate to \"{url}\"', { exact: true }).click();
      await page.getByText('After', { exact: true }).first().click();
      let replayed = false;
      for (let i = 0; i < 30 && !replayed; i++) {
        for (const frame of page.frames().slice(1)) { try { if ((await frame.locator('body').innerText({ timeout: 500 })).includes('[redacted]')) replayed = true; } catch {} }
        if (!replayed) await page.waitForTimeout(100);
      }
      assert.ok(replayed, 'Actual snapshot iframe must replay redacted DOM');
      assert.equal(errors.length, 0, errors.join('\n'));
      assert.ok(responses.length > 0);
      const contexts = await responses[0].json();
      fs.writeFileSync(path.join(receiptDir, mode + '-contexts.json'), JSON.stringify(contexts, null, 2));
      assert.ok(Array.isArray(contexts) && contexts.length === 1 && contexts[0].actions.length > 0 && contexts[0].resources.length === 2);
      results.push({ mode, replayed_redacted_snapshot: true, actions: contexts[0].actions.length, resources: contexts[0].resources.length, status: 'OPENED_IN_PINNED_LOCAL_VIEWER', context_response: responses[0].status(), errors: 0, body_action_label: true });
      await context.close();
    }
  } finally { await browser.close(); }
  fs.writeFileSync(path.join(privateRoot, run, 'viewer-results.json'), JSON.stringify({ attempt, results }, null, 2));
}
async function supervisor(run) {
  assert.ok(/^\d+$/.test(run));
  const server = await startTraceViewerServer({ host: '127.0.0.1', port });
  assert.equal(new URL(server.urlPrefix()).port, String(port));
  try {
    const profile = `(version 1)(allow default)(deny network*)(allow network-outbound (remote tcp "localhost:${port}"))`;
    const receiptDir = path.join(privateRoot, run, 'viewer-' + attempt); fs.mkdirSync(receiptDir, { recursive: true });
    const output = fs.openSync(path.join(receiptDir, 'worker.txt'), 'w');
    await new Promise((resolve, reject) => {
      const child = spawn('/usr/bin/sandbox-exec', ['-p', profile, process.execPath, __filename, '--worker', run, attempt], { detached: true, stdio: ['ignore', output, output] });
      let failure;
      const kill = () => { if (child.pid) { try { process.kill(-child.pid, 'SIGKILL'); } catch (error) { if (error.code !== 'ESRCH') failure = error; } } };
      const timer = setTimeout(() => { failure = Error('Viewer timed out'); kill(); }, 60000);
      child.on('error', error => { failure = error; kill(); });
      child.on('close', code => { clearTimeout(timer); fs.closeSync(output); kill(); code === 0 && !failure ? resolve() : reject(failure || Error('Viewer worker failed ' + code)); });
    });
  } finally { await server.stop(); }
}
if (require.main === module) (process.argv[2] === '--worker' ? worker(process.argv[3]) : supervisor(process.argv[2])).catch(error => { console.error(error); process.exitCode = 1; });
