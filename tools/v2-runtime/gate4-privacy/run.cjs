'use strict';
const fs = require('node:fs');
const crypto = require('node:crypto');
const path = require('node:path');
const http = require('node:http');
const { spawn } = require('node:child_process');
const { MARKER, PORT } = require('./collector.cjs');
const root = path.resolve(__dirname, '../../..');
const run = process.env.SR_PRIVACY_RUN || String(Date.now());
if (!/^\d+$/.test(run)) throw Error('Synthetic run ID required');
const out = path.join(root, '.artifacts/release-gates-20261019/gate4-privacy', run);
fs.mkdirSync(out, { recursive: true, mode: 0o700 });
const sourcePins = Object.fromEntries(fs.readdirSync(__dirname).filter(name => name.endsWith('.cjs') || name.endsWith('.py')).sort().map(name => [name, crypto.createHash('sha256').update(fs.readFileSync(path.join(__dirname,name))).digest('hex')]));
fs.writeFileSync(path.join(out, 'source-pins-at-capture-start.json'), JSON.stringify(sourcePins,null,2));
const hanging = new Set();
const server = http.createServer((request, response) => {
  response.setHeader('Cache-Control', 'no-store');
  if (request.url.startsWith('/hang')) { hanging.add(response); response.on('close', () => hanging.delete(response)); return; }
  if (request.url.startsWith('/data')) { response.setHeader('Content-Type', 'application/json'); response.end(JSON.stringify({ private: request.url.includes('tainted') ? MARKER : 'public' })); return; }
  const tainted = request.url.startsWith('/tainted'); const cancelled = request.url.startsWith('/cancelled');
  if (tainted) response.setHeader('Set-Cookie', 'synthetic_response=' + MARKER + '; Path=/; SameSite=Lax');
  const value = tainted ? MARKER : 'public';
  response.setHeader('Content-Type', 'text/html');
  response.end(`<!doctype html><html><head><link rel="icon" href="data:,"></head><body style="margin:0;width:800px;height:600px"><input value="${value}"><textarea>${value}</textarea><a href="/?private=${value}">Private</a><script nonce="${value}">const v=${JSON.stringify(value)};${tainted ? 'localStorage.setItem(v,btoa(v));sessionStorage.setItem(v,encodeURIComponent(v));console.error(v);setTimeout(()=>{throw Error(v)},20);' : ''}fetch('/data?mode=${tainted ? 'tainted' : 'clean'}').then(r=>r.json()).then(()=>{window.fixtureReady=true;});${cancelled ? "fetch('/hang').catch(()=>{});" : ''}</script></body></html>`);
});
(async () => {
  await new Promise((resolve, reject) => { server.once('error', reject); server.listen(PORT, '127.0.0.1', resolve); });
  try {
    for (const mode of ['clean', 'tainted', 'cancelled']) {
      const profile = `(version 1)(allow default)(deny network*)(allow network-outbound (remote tcp "localhost:${PORT}"))`;
      fs.writeFileSync(path.join(out, 'containment.sb'), profile);
      await new Promise((resolve, reject) => {
        const receipt = fs.openSync(path.join(out, mode + '-worker.txt'), 'w');
        let failure;
        const child = spawn('/usr/bin/sandbox-exec', ['-p', profile, process.execPath, path.join(__dirname, 'collector.cjs'), mode, run], { detached: true, stdio: ['ignore', receipt, receipt] });
        const kill = () => { if (child.pid) { try { process.kill(-child.pid, 'SIGKILL'); } catch (error) { if (error.code !== 'ESRCH') failure = error; } } };
        const timeout = setTimeout(() => { failure = Error('Capture timed out'); kill(); }, 60000);
        child.on('error', error => { failure = error; kill(); });
        child.on('close', code => { clearTimeout(timeout); fs.closeSync(receipt); kill(); code === 0 && !failure ? resolve() : reject(failure || Error(mode + ' worker exit ' + code)); });
      });
    }
    console.log(JSON.stringify({ run, private_output: out }));
  } finally { for (const response of hanging) response.destroy(); await new Promise(resolve => server.close(resolve)); }
})().catch(error => { console.error(error); process.exitCode = 1; });
