const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const http = require('node:http');
const net = require('node:net');
const { spawnSync } = require('node:child_process');
const { beginRun } = require('./run-evidence.cjs');
const { createOriginProxy } = require('./origin-proxy.cjs');

test('new run invalidates old PASS; failure and success carry current identity', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'v2-evidence-'));
  try {
    const output = path.join(dir, 'evidence.json');
    const read = file => JSON.parse(fs.readFileSync(file));
    fs.writeFileSync(output, JSON.stringify({ status: 'PASS', old: true }));
    const first = beginRun(output);
    const running = read(output);
    assert.equal(running.status, 'RUNNING');
    assert(!running.old);
    assert(running.startedAt && running.runId);
    first.fail(new Error('fixture missing'));
    assert.equal(read(output).status, 'FAIL');
    assert.equal(read(output).runId, running.runId);
    assert.match(read(output).error, /fixture missing/);
    const next = beginRun(output);
    assert.notEqual(read(output).runId, running.runId);
    next.pass([{ width: 390 }]);
    assert.deepEqual(read(output), [{ width: 390 }]);
    const sidecar = read(path.join(dir, 'evidence.run.json'));
    assert.equal(sidecar.status, 'PASS');
    assert(sidecar.finishedAt);
    const interrupted = beginRun(output);
    assert.equal(read(path.join(dir, 'evidence.run.json')).status, 'RUNNING');
    interrupted.fail(new Error('interrupted'));
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

const listen = server => new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const close = server =>
  new Promise(resolve => {
    server.close(resolve);
    server.closeAllConnections();
  });
const requestVia = (proxy, target) =>
  new Promise((resolve, reject) => {
    const request = http.request(proxy, { path: target }, response => {
      let body = '';
      response.on('data', chunk => {
        body += chunk;
      });
      response.on('end', () => resolve({ status: response.statusCode, body, location: response.headers.location }));
    });
    request.on('error', reject);
    request.end();
  });

test('missing QA installation invalidates every old receipt before any browser launch', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'v2-startup-'));
  try {
    for (const [file, args, receipt] of [
      ['capture-surface.cjs', ['startup', '/shop/'], 'startup-responsive.json'],
      ['static-surface.cjs', ['startup', '/shop/'], 'startup-static.json'],
      ['inventory-final.cjs', [], 'final-page-inventory.json'],
      ['test-collection-browser.cjs', [], 'collections-behavior.json'],
      ['test-shop-browser.cjs', [], 'shop-behavior.json'],
      ['pdp-behavior.cjs', [], 'pdp-behavior.json'],
      ['test-gallery-delivery.cjs', [], 'gallery-delivery.json'],
      ['run-lighthouse.cjs', ['startup'], 'lighthouse-startup-run.json'],
    ]) {
      const output = path.join(dir, receipt);
      fs.writeFileSync(output, JSON.stringify({ status: 'PASS', runId: 'previous' }));
      const result = spawnSync(process.execPath, [path.join(__dirname, file), ...args], {
        env: {
          ...process.env,
          V2_ARTIFACT_DIR: dir,
          V2_QA_PACKAGE: path.join(dir, 'missing-package.json'),
          V2_BASE_URL: 'http://127.0.0.1:1',
          V2_LH_CASE: '',
        },
        encoding: 'utf8',
        timeout: 5000,
      });
      assert.equal(result.status, 1, file);
      const value = JSON.parse(fs.readFileSync(output));
      assert.equal(value.status, 'FAIL', file);
      assert.notEqual(value.runId, 'previous', file);
      assert.match(value.error, /QA package is missing/, file);
    }
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test('origin proxy allows fixture; blocks other ports, literal IPs, redirects and CONNECT', async () => {
  let disallowedHits = 0;
  const other = http.createServer((request, response) => {
    disallowedHits++;
    response.end('must not reach');
  });
  await listen(other);
  const offOrigin = 'http://127.0.0.1:' + other.address().port;
  const fixture = http.createServer((request, response) => {
    if (request.url === '/redirect') {
      response.writeHead(302, { location: offOrigin + '/escaped' });
      response.end();
    } else response.end('fixture');
  });
  await listen(fixture);
  const base = 'http://127.0.0.1:' + fixture.address().port;
  const proxy = await createOriginProxy(base);
  try {
    assert.equal((await requestVia(proxy.url, base + '/')).body, 'fixture');
    assert.equal((await requestVia(proxy.url, offOrigin + '/')).status, 403);
    assert.equal((await requestVia(proxy.url, 'http://192.0.2.1/')).status, 403);
    assert.equal((await requestVia(proxy.url, 'https://example.invalid/')).status, 403);
    const redirect = await requestVia(proxy.url, base + '/redirect');
    assert.equal(redirect.status, 302);
    assert.equal((await requestVia(proxy.url, redirect.location)).status, 403);
    const connectStatus = await new Promise((resolve, reject) => {
      const request = http.request(proxy.url, { method: 'CONNECT', path: 'example.invalid:443' });
      request.on('connect', (response, socket) => {
        socket.destroy();
        resolve(response.statusCode);
      });
      request.on('error', reject);
      request.end();
    });
    assert.equal(connectStatus, 403);
    assert.equal(disallowedHits, 0);
    assert.equal(proxy.allowedRequests, 2, 'Only the fixture GET and redirect response should be allowed.');
    assert(proxy.blocked.length >= 5);
  } finally {
    await proxy.close();
    await close(fixture);
    await close(other);
  }
});

test('stalled upstream closes on proxy shutdown and after completed client disconnect', async () => {
  const bounded = async (promise, message) => {
    let timer;
    try {
      return await Promise.race([
        promise,
        new Promise((resolve, reject) => {
          timer = setTimeout(() => reject(new Error(message)), 2000);
        }),
      ]);
    } finally {
      clearTimeout(timer);
    }
  };
  for (const trigger of ['proxy-close', 'client-close']) {
    let reached;
    const requestCompleted = new Promise(resolve => {
      reached = resolve;
    });
    const fixture = http.createServer((request, response) => {
      // Consume the entire GET before hanging: request.aborted cannot clean up
      // this case because the proxy's incoming request has already completed.
      request.once('end', () => reached(request.socket));
      request.resume();
    });
    await listen(fixture);
    const base = 'http://127.0.0.1:' + fixture.address().port;
    const proxy = await createOriginProxy(base);
    let proxyClosed = false;
    const client = http.request(proxy.url, { path: base + '/hang' });
    client.on('error', () => {}); // Intentional disconnect/closed proxy socket.
    try {
      client.end();
      const fixtureSocket = await bounded(requestCompleted, 'Fixture did not receive complete request.');
      const upstreamClosed = new Promise(resolve => fixtureSocket.once('close', resolve));
      assert.equal(proxy.allowedRequests, 1);
      if (trigger === 'proxy-close') {
        await bounded(proxy.close(), 'Proxy shutdown hung with an outgoing request.');
        proxyClosed = true;
      } else client.destroy();
      await bounded(upstreamClosed, trigger + ' left the hanging outgoing fixture socket open.');
    } finally {
      client.destroy();
      if (!proxyClosed) await proxy.close();
      await close(fixture);
    }
  }
});

test(
  'denied CONNECT and UPGRADE sockets tolerate client resets without losing origin isolation',
  { timeout: 5000 },
  async () => {
    const fixture = http.createServer((request, response) => response.end('still available'));
    await listen(fixture);
    const base = 'http://127.0.0.1:' + fixture.address().port;
    const proxy = await createOriginProxy(base);
    try {
      for (const method of ['CONNECT', 'UPGRADE']) {
        for (let attempt = 0; attempt < 12; attempt++) {
          await new Promise((resolve, reject) => {
            const socket = net.connect(new URL(proxy.url).port, '127.0.0.1');
            socket.on('error', reject);
            socket.once('connect', () => {
              socket.write(
                method === 'CONNECT'
                  ? 'CONNECT example.invalid:443 HTTP/1.1\r\nHost: example.invalid:443\r\n\r\n'
                  : `GET ${base}/ HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: Upgrade\r\nUpgrade: websocket\r\n\r\n`
              );
            });
            socket.once('data', data => {
              assert.match(data.toString(), /^HTTP\/1\.1 403 /);
              // Send TCP RST rather than a normal FIN after the denied response.
              socket.resetAndDestroy();
            });
            socket.once('close', resolve);
          });
        }
      }
      assert.equal(proxy.blocked.filter(entry => entry.method === 'CONNECT').length, 12);
      assert.equal(proxy.blocked.filter(entry => entry.method === 'UPGRADE').length, 12);
      assert.equal(proxy.allowedRequests, 0);
      assert.equal((await requestVia(proxy.url, base + '/')).body, 'still available');
    } finally {
      await proxy.close();
      await close(fixture);
    }
  }
);

test('reset fixture response remains a failed truncated response and proxy survives', { timeout: 5000 }, async () => {
  const fixture = http.createServer((request, response) => {
    if (request.url === '/reset') {
      response.writeHead(200, { 'content-length': '1000' });
      response.write('partial');
      // Wait until the client has received the headers before resetting fixture.
    } else response.end('still available');
  });
  await listen(fixture);
  const base = 'http://127.0.0.1:' + fixture.address().port;
  const proxy = await createOriginProxy(base);
  try {
    const outcome = await new Promise((resolve, reject) => {
      const client = http.request(proxy.url, { path: base + '/reset' }, response => {
        response.once('data', () => fixture.closeAllConnections());
        response.once('end', () => reject(new Error('Truncated fixture response was reported as complete.')));
        response.once('error', error => resolve(error.code));
        response.resume();
      });
      client.once('error', reject);
      client.end();
    });
    assert.equal(outcome, 'ECONNRESET');
    assert.equal((await requestVia(proxy.url, base + '/')).body, 'still available');
  } finally {
    await proxy.close();
    await close(fixture);
  }
});
