const http = require('node:http');

/** A forward proxy with one permitted HTTP origin; HTTPS CONNECT is denied. */
async function createOriginProxy(base) {
  const allowed = new URL(base);
  if (allowed.protocol !== 'http:' || allowed.hostname !== '127.0.0.1' || allowed.username || allowed.password) {
    throw new Error('Proxy target must be a local HTTP 127.0.0.1 origin.');
  }
  const blocked = [];
  const upstreamRequests = new Set();
  const clientSockets = new Set();
  let allowedRequests = 0;
  const server = http.createServer((request, response) => {
    let target;
    try {
      target = new URL(request.url);
    } catch {
      /* Origin-form/invalid requests are denied. */
    }
    if (!target || target.origin !== allowed.origin || target.username || target.password) {
      blocked.push({ method: request.method, url: request.url });
      response.writeHead(403, { 'content-type': 'text/plain', connection: 'close' });
      response.end('Origin blocked by local verification proxy.');
      return;
    }
    const headers = { ...request.headers, host: allowed.host, connection: 'close' };
    delete headers['proxy-authorization'];
    delete headers['proxy-connection'];
    allowedRequests++;
    const upstream = http.request(
      {
        hostname: allowed.hostname,
        port: allowed.port || 80,
        path: target.pathname + target.search,
        method: request.method,
        headers,
      },
      result => {
        // A fixture can reset after sending headers. Do not turn a truncated
        // response into a successful end or leave IncomingMessage errors unowned.
        result.on('error', () => response.destroy());
        if (response.destroyed) {
          result.destroy();
          return;
        }
        response.writeHead(result.statusCode, result.headers);
        result.pipe(response);
      }
    );
    upstreamRequests.add(upstream);
    upstream.once('close', () => upstreamRequests.delete(upstream));
    upstream.on('error', () => {
      if (response.destroyed) return;
      if (response.headersSent) response.destroy();
      else {
        response.writeHead(502);
        response.end();
      }
    });
    request.on('error', () => upstream.destroy());
    response.on('error', () => upstream.destroy());
    request.on('aborted', () => upstream.destroy());
    // A completed incoming request does not emit aborted when its client leaves.
    // Close the outgoing request when the downstream response loses its owner.
    response.once('close', () => upstream.destroy());
    request.pipe(upstream);
  });
  server.on('connection', socket => {
    // CONNECT/UPGRADE detach sockets from the HTTP parser. Chrome may reset a
    // denied background connection after reading 403, so retain error ownership
    // for the full socket lifetime, including those detached paths.
    clientSockets.add(socket);
    socket.on('error', () => socket.destroy());
    socket.once('close', () => clientSockets.delete(socket));
  });
  server.on('connect', (request, socket) => {
    blocked.push({ method: 'CONNECT', url: request.url });
    socket.end('HTTP/1.1 403 Forbidden\r\nConnection: close\r\n\r\n');
  });
  server.on('upgrade', (request, socket) => {
    blocked.push({ method: 'UPGRADE', url: request.url });
    socket.end('HTTP/1.1 403 Forbidden\r\nConnection: close\r\n\r\n');
  });
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', resolve);
  });
  return {
    url: 'http://127.0.0.1:' + server.address().port,
    blocked,
    get allowedRequests() {
      return allowedRequests;
    },
    close: async () => {
      // server.closeAllConnections only closes inbound sockets. Explicitly stop
      // outgoing requests too, including fixtures that never send a response.
      const outgoingClosed = Promise.all(
        [...upstreamRequests].map(
          upstream =>
            new Promise(resolve => {
              upstream.once('close', resolve);
              upstream.destroy();
            })
        )
      );
      const incomingClosed = new Promise((resolve, reject) => {
        server.close(error => (error ? reject(error) : resolve()));
        server.closeAllConnections();
        // closeAllConnections deliberately excludes upgraded/CONNECT sockets.
        for (const socket of clientSockets) socket.destroy();
      });
      await Promise.all([outgoingClosed, incomingClosed]);
    },
  };
}

module.exports = { createOriginProxy };
