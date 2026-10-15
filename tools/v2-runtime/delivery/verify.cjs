'use strict';
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const zlib = require('node:zlib');
const { execFileSync } = require('node:child_process');
const BASE = 'http://127.0.0.1:18308';
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');

function localUrl(input) {
  const url = new URL(input, BASE);
  assert.equal(url.origin, BASE, 'Verification never requests another origin');
  assert.equal(url.username + url.password, '', 'Credentials are forbidden');
  return url;
}
function decode(body, encoding) {
  assert.ok(!encoding || encoding === 'gzip', 'Only negotiated gzip/identity is supported');
  return encoding ? zlib.gunzipSync(body) : body;
}
function request(input, encoding = 'identity', proof = true, options = {}) {
  const url = localUrl(input);
  return new Promise((resolve, reject) => {
    const requestPath = options.rawPath || url.pathname + url.search;
    assert.ok(requestPath.startsWith('/') && !/[\r\n]/.test(requestPath));
    const req = http.request({ hostname: url.hostname, port: url.port, path: requestPath, method: options.method || 'GET', headers: { 'Accept-Encoding': encoding, ...(proof ? { 'X-V2-Delivery-Proof': '1' } : {}), ...(options.headers || {}) } }, res => {
      const chunks = [];
      let length = 0;
      res.on('data', chunk => {
        length += chunk.length;
        if (length > 20 * 1024 * 1024) res.destroy(new Error('Response exceeds bounded proof limit'));
        else chunks.push(chunk);
      });
      res.on('error', reject);
      res.on('end', () => resolve({ status: res.statusCode, headers: res.headers, wire: Buffer.concat(chunks) }));
    });
    req.setTimeout(15000, () => req.destroy(new Error('Local proof request timed out')));
    req.on('error', reject);
    req.end();
  });
}
function rangeProof(response, source, start, end) {
  assert.equal(response.status, 206);
  assert.equal(response.headers['content-range'], `bytes ${start}-${end}/${source.length}`);
  assert.equal(response.headers['content-encoding'], undefined, 'Media ranges must retain byte identity');
  assert.equal(Number(response.headers['content-length']), end - start + 1);
  assert.deepEqual(response.wire, source.subarray(start, end + 1));
}
function assetInventory(root) {
  const rows = [];
  function walk(directory) {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
      const file = path.join(directory, entry.name);
      assert.equal(entry.isSymbolicLink(), false, 'Public asset mount contains a symlink: ' + file);
      if (entry.isDirectory()) walk(file);
      else if (entry.isFile()) rows.push({ path: path.relative(root, file), bytes: fs.statSync(file).size });
    }
  }
  walk(root);
  return rows.sort((a, b) => a.path.localeCompare(b.path));
}
function nativeMountProof(container, fixture, storage) {
  const native = require('./native-assets.cjs');
  const source = native.fixtureRoot(fixture);
  const first = container.Mounts.find(mount => mount.Destination === native.AREAS[0].destination);
  assert.ok(first, 'Native public static mount is required');
  const snapshot = path.dirname(first.Source);
  assert.equal(path.dirname(snapshot), storage, 'Native snapshot must use owned artifact storage');
  const manifest = JSON.parse(fs.readFileSync(snapshot + '.json'));
  assert.equal(manifest.schema, 'skyyrose.native-static.v1');
  assert.equal(manifest.fixture, source);
  assert.equal(manifest.snapshot, snapshot);
  assert.deepEqual(manifest.areas, native.AREAS);
  assert.deepEqual(manifest.sourceVersions, native.versions(source));
  assert.deepEqual(manifest.files, native.census(source), 'Every copied native byte must match the current fixture');
  assert.equal(manifest.identity, sha(JSON.stringify({ fixture: source, sourceVersions: manifest.sourceVersions, files: manifest.files })));
  assert.equal(path.basename(snapshot), manifest.identity);
  native.verifySnapshot(manifest);
  const mounts = native.AREAS.map(area => {
    const mount = container.Mounts.find(item => item.Destination === area.destination);
    assert.ok(mount, 'Missing native mount: ' + area.key);
    assert.equal(mount.RW, false, 'Native mount must be read-only');
    assert.equal(mount.Source, path.join(snapshot, area.key), 'Exact native snapshot mount identity');
    return { fixtureSource: path.join(source, area.relative), snapshotSource: mount.Source, destination: mount.Destination, writable: mount.RW, files: manifest.files.filter(file => file.area === area.key).length };
  });
  const allowed = new Set(['/srv/v2-assets', '/etc/nginx/nginx.conf', '/tmp', ...native.AREAS.map(area => area.destination)]);
  assert.ok(container.Mounts.every(mount => allowed.has(mount.Destination)), 'Unexpected additional mounted filesystem');
  return { sourceVersions: manifest.sourceVersions, manifestSha256: sha(fs.readFileSync(snapshot + '.json')), identity: manifest.identity, mounts, files: manifest.files };
}
function nativeResponse(response, source, mime, encoding) {
  assert.equal(response.status, 200);
  assert.match(response.headers['content-type'] || '', mime);
  assert.equal(response.headers['content-encoding'] || 'identity', encoding);
  const decoded = decode(response.wire, response.headers['content-encoding']);
  assert.deepEqual(decoded, source, 'Native static decoded bytes differ from fixture');
  if (encoding === 'gzip') {
    assert.match(response.headers.vary || '', /Accept-Encoding/i);
    assert.ok(response.wire.length < source.length);
  }
  return { status: response.status, mime: response.headers['content-type'], encoding, wireBytes: response.wire.length, decodedBytes: decoded.length, sourceSha256: sha(source), decodedSha256: sha(decoded) };
}
function resourceUrls(html) {
  const urls = [];
  for (const match of html.matchAll(/<(script|img|source|video|link)\b[^>]*>/gi)) {
    const tag = match[0];
    if (match[1].toLowerCase() === 'link' && !/\brel\s*=\s*["'](?:stylesheet|preload|modulepreload|icon|apple-touch-icon)["']/i.test(tag)) continue;
    for (const attr of tag.matchAll(/\b(src|href|poster|srcset|imagesrcset)\s*=\s*(["'])(.*?)\2/gi)) {
      const values = /srcset$/i.test(attr[1]) ? attr[3].split(',').map(v => v.trim().split(/\s+/)[0]) : [attr[3]];
      for (const raw of values) {
        const value = raw.replace(/&amp;/g, '&');
        if (!value || /^(data|blob):/i.test(value)) continue;
        urls.push(localUrl(value).href);
      }
    }
  }
  assert.ok(urls.length > 5, 'Resource census must inspect actual page resources');
  assert.ok(!html.includes('http://127.0.0.1:18303'), 'Raw fixture URLs bypass delivery');
  return [...new Set(urls)];
}
function htmlStatus(route, response) {
  const redirect = [301, 302, 303, 307, 308].includes(response.status);
  if (route === '/v2-delivery-deliberately-missing/') assert.equal(response.status, 404);
  else if (route === '/checkout/') assert.ok(response.status === 200 || redirect, 'Checkout must render or redirect, never error');
  else assert.equal(response.status, 200);
  if (redirect) {
    assert.ok(typeof response.headers.location === 'string' && response.headers.location.trim(), 'Redirect requires a nonempty Location');
    localUrl(response.headers.location);
  }
  assert.match(response.headers['content-type'] || '', /text\/html/);
  return redirect;
}
function ordinaryResponse(response) {
  assert.equal(response.status, 200, 'Ordinary Home must succeed');
  assert.match(response.headers['content-type'] || '', /text\/html/);
  assert.equal(response.headers['content-encoding'], 'gzip');
  assert.match(response.headers.vary || '', /Accept-Encoding/i);
  assert.equal(response.headers['x-v2-fixture-body-sha256'], undefined, 'Normal/Lighthouse responses must not enable diagnostic buffering');
  resourceUrls(decode(response.wire, response.headers['content-encoding']).toString());
}
async function verify(output) {
  const repo = path.resolve(__dirname, '../../..');
  const theme = path.join(repo, 'wordpress-theme/skyyrose-flagship-2');
  let assets;
  const receipt = { status: 'RUNNING', runId: crypto.randomUUID(), startedAt: new Date().toISOString(), origin: BASE, scope: 'SYNTHETIC_HTTP_DELIVERY_ONLY', rows: [] };
  const write = () => {
    fs.mkdirSync(path.dirname(output), { recursive: true });
    fs.writeFileSync(output, JSON.stringify(receipt, null, 2) + '\n');
  };
  write();
  try {
    const nativeAssets = require('./native-assets.cjs');
    const workerFixture = fs.readFileSync(path.join(repo, '.artifacts/v2-delivery-20260906/php-origin/fixture'), 'utf8').trim();
    const fixture = nativeAssets.matchingFixture(process.env.V2_WP_FIXTURE, workerFixture);
    receipt.phpOrigin = await require('./verify-php-origin.cjs').prove(output.replace(/\.json$/, '') + '.php-origin.json');
    nativeAssets.matchingFixture(fixture, receipt.phpOrigin.fixture);
    assets = fs.realpathSync(process.env.V2_DELIVERY_ASSETS || path.join(theme, 'assets'));
    receipt.head = execFileSync('git', ['rev-parse', 'HEAD'], { cwd: repo, encoding: 'utf8' }).trim();
    receipt.nginxImage = fs.readFileSync(path.join(__dirname, 'image.txt'), 'utf8').trim();
    receipt.nginxConfigSha256 = sha(fs.readFileSync(path.join(__dirname, 'nginx.conf')));
    receipt.adapterSha256 = sha(fs.readFileSync(path.join(__dirname, 'fixture-origin.php')));
    const containerName = 'skyyrose-v2-delivery-18308';
    const container = JSON.parse(execFileSync('docker', ['inspect', containerName], { encoding: 'utf8' }))[0];
    assert.equal(container.State.Running, true, 'Gateway must be running');
    assert.equal(container.Config.Image, receipt.nginxImage, 'Live image must match pinned image');
    assert.equal(container.HostConfig.ReadonlyRootfs, true);
    const lookup = database => execFileSync('docker', ['exec', containerName, 'getent', database, 'v2-php-origin'], { encoding: 'utf8', timeout: 15000, maxBuffer: 65536 });
    receipt.originAddress = require('./origin-ipv4.cjs').originProof(container, lookup('ahostsv4'), lookup('ahosts'));
    receipt.originAddress.resolverSha256 = sha(fs.readFileSync(path.join(__dirname, 'origin-ipv4.cjs')));

    assert.deepEqual(container.HostConfig.PortBindings, { '8080/tcp': [{ HostIp: '127.0.0.1', HostPort: '18308' }] });
    const assetMount = container.Mounts.find(mount => mount.Destination === '/srv/v2-assets');
    assert.ok(assetMount, 'Direct public asset mount is required');
    assert.equal(assetMount.RW, false, 'Public assets must be read-only');
    assert.equal(fs.realpathSync(assetMount.Source), assets, 'Mounted assets must match expected theme source');
    receipt.nativeStatic = nativeMountProof(container, fixture, path.join(repo, '.artifacts/v2-delivery-20260906/native-static'));
    const inventory = assetInventory(assets);
    receipt.assetMount = { source: assets, destination: assetMount.Destination, writable: assetMount.RW, files: inventory.length, symlinks: 0, inventorySha256: sha(JSON.stringify(inventory)) };
    assert.ok(fs.statSync(path.join(__dirname, 'nginx.conf')).mtimeMs <= Date.parse(container.State.StartedAt), 'Config changed after startup: restart before parity proof');
    const resolvedConfig = execFileSync('docker', ['exec', containerName, 'nginx', '-T'], { encoding: 'utf8' });
    assert.ok(resolvedConfig.includes(fs.readFileSync(path.join(__dirname, 'nginx.conf'), 'utf8')), 'Live nginx -T must contain exact intended config');
    const configArtifact = output.replace(/\.json$/, '') + '.nginx-T.txt';
    fs.writeFileSync(configArtifact, resolvedConfig);
    receipt.liveGateway = { containerId: container.Id, imageId: container.Image, configuredImage: container.Config.Image, startedAt: container.State.StartedAt, portBindings: container.HostConfig.PortBindings, resolvedConfigSha256: sha(resolvedConfig), resolvedConfigArtifact: configArtifact };
    for (const asset of ['assets/css/theme.min.css', 'assets/js/theme.min.js']) {
      const source = fs.readFileSync(path.join(assets, asset.replace(/^assets\//, '')));
      for (const encoding of ['identity', 'gzip']) {
        const response = await request('/wp-content/themes/skyyrose-flagship-2/' + asset, encoding);
        assert.equal(response.status, 200);
        assert.match(response.headers['content-type'], asset.endsWith('.css') ? /text\/css/ : /javascript/);
        assert.equal(response.headers['content-encoding'] || 'identity', encoding);
        const body = decode(response.wire, response.headers['content-encoding']);
        assert.equal(sha(body), sha(source), 'Decoded asset must equal the source on disk');
        if (encoding === 'gzip') {
          assert.match(response.headers.vary || '', /Accept-Encoding/i);
          assert.ok(response.wire.length < body.length);
        }
        receipt.rows.push({ asset, encoding, status: response.status, mime: response.headers['content-type'], wireBytes: response.wire.length, decodedBytes: body.length, sourceSha256: sha(source), decodedSha256: sha(body) });
      }
    }
    const nativeCases = [
      ['wp-includes/js/jquery/jquery.min.js', /javascript/, true],
      ['wp-includes/css/dist/block-library/common.min.css', /text\/css/, true],
      ['wp-includes/fonts/dashicons.woff2', /font\/woff2/, false],
      ['wp-content/plugins/woocommerce/assets/js/js-cookie/js.cookie.min.js', /javascript/, true],
      ['wp-content/plugins/woocommerce/assets/css/woocommerce-layout.css', /text\/css/, true],
      ['wp-content/plugins/woocommerce/assets/fonts/WooCommerce.woff2', /font\/woff2/, false],
    ];
    for (const [file, mime, compressible] of nativeCases) {
      const source = fs.readFileSync(path.join(fixture, file));
      for (const encoding of compressible ? ['identity', 'gzip'] : ['identity']) {
        const response = await request('/' + file, encoding, false);
        receipt.rows.push({ nativeAsset: file, ...nativeResponse(response, source, mime, encoding) });
      }
      const head = await request('/' + file, 'identity', false, { method: 'HEAD' });
      assert.equal(head.status, 200); assert.match(head.headers['content-type'], mime);
      assert.equal(Number(head.headers['content-length']), source.length); assert.equal(head.wire.length, 0);
      const partial = await request('/' + file, 'identity', false, { headers: { Range: 'bytes=0-31' } });
      rangeProof(partial, source, 0, 31);
      const outside = await request('/' + file, 'identity', false, { headers: { Range: `bytes=${source.length}-` } });
      assert.equal(outside.status, 416); assert.equal(outside.headers['content-range'], `bytes */${source.length}`);
      const forbidden = await request('/' + file, 'identity', false, { method: 'POST' });
      assert.equal(forbidden.status, 403);
    }
    const mediaAsset = 'video/collection-heroes/approved/black-rose/web/black-rose-authentic-motion-v3-a1.webm';
    const mediaUrl = '/wp-content/themes/skyyrose-flagship-2/assets/' + mediaAsset;
    const media = fs.readFileSync(path.join(assets, mediaAsset));
    const whole = await request(mediaUrl, 'identity', false);
    assert.equal(whole.status, 200);
    assert.equal(whole.headers['content-type'], 'video/webm');
    assert.equal(sha(whole.wire), sha(media));
    const ranges = [];
    for (const [header, start, end] of [['bytes=0-1023', 0, 1023], ['bytes=-32', media.length - 32, media.length - 1]]) {
      const response = await request(mediaUrl, 'gzip', false, { headers: { Range: header } });
      rangeProof(response, media, start, end);
      ranges.push({ request: header, status: response.status, contentRange: response.headers['content-range'], decodedSha256: sha(response.wire), sourceSliceSha256: sha(media.subarray(start, end + 1)) });
    }
    const outside = await request(mediaUrl, 'identity', false, { headers: { Range: `bytes=${media.length}-` } });
    assert.equal(outside.status, 416);
    assert.equal(outside.headers['content-range'], `bytes */${media.length}`);
    const typed = [
      [mediaAsset, 'video/webm'],
      ['sot/fonts/hanken-grotesk-latin.woff2', 'font/woff2'],
      [inventory.find(file => file.path.endsWith('.wasm'))?.path, 'application/wasm'],
      [inventory.find(file => file.path.endsWith('.glb'))?.path, 'model/gltf-binary'],
    ];
    for (const [file, mime] of typed) {
      assert.ok(file, 'Required native media fixture is missing');
      const response = await request('/wp-content/themes/skyyrose-flagship-2/assets/' + file, 'identity', false, { method: 'HEAD' });
      assert.equal(response.status, 200);
      assert.equal(response.headers['content-type'], mime);
      assert.equal(Number(response.headers['content-length']), fs.statSync(path.join(assets, file)).size);
      assert.equal(response.wire.length, 0, 'HEAD must not transfer the file body');
    }
    const blockedPaths = [
      '/wp-content/themes/skyyrose-flagship-2/assets/../functions.php',
      '/wp-content/themes/skyyrose-flagship-2/assets/%2e%2e/functions.php',
      '/wp-content/themes/skyyrose-flagship-2/assets/%252e%252e/functions.php',
      '/wp-content/themes/skyyrose-flagship-2/assets/.env',
      '/wp-content/themes/skyyrose-flagship-2/assets/lib/private.php',
      '/wp-content/themes/skyyrose-flagship-2/assets/',
      ...inventory.filter(file => /\.(json|md|txt)$/i.test(file.path)).map(file => '/wp-content/themes/skyyrose-flagship-2/assets/' + file.path),
    ];
    for (const area of require('./native-assets.cjs').AREAS) {
      for (const suffix of ['index.php', 'private.json', '.env', '', '../private.php', '%2e%2e/private.php', '%252e%252e/private.php', 'file.js.map']) blockedPaths.push(area.url + suffix);
    }
    for (const rawPath of blockedPaths) {
      const response = await request('/', 'identity', false, { rawPath });
      assert.ok([400, 403, 404].includes(response.status), 'Private/ambiguous path was not blocked: ' + rawPath);
    }
    const deniedMethod = await request(mediaUrl, 'identity', false, { method: 'POST' });
    assert.equal(deniedMethod.status, 403);
    receipt.staticProof = { asset: mediaAsset, sourceSha256: sha(media), wholeResponseSha256: sha(whole.wire), ranges, unsatisfiableStatus: outside.status, headMimeCases: typed, deniedPaths: blockedPaths, deniedMethodStatus: deniedMethod.status };
    for (const route of ['/', '/shop/', '/product/sg-005/', '/cart/', '/checkout/', '/my-account/', '/v2-delivery-deliberately-missing/']) {
      for (const encoding of ['identity', 'gzip']) {
        const response = await request(route, encoding);
        // Empty checkout may redirect to cart. Preserve and inspect, never follow.
        const redirect = htmlStatus(route, response);
        const body = decode(response.wire, response.headers['content-encoding']);
        assert.equal(response.headers['x-v2-fixture-body-sha256'], sha(body), 'Hash must match this SAME upstream response, not another nonce-bearing request');
        if (!redirect && response.status === 200) {
          assert.equal(response.headers['content-encoding'] || 'identity', encoding);
          if (encoding === 'gzip') assert.match(response.headers.vary || '', /Accept-Encoding/i);
        }
        const resources = redirect ? [] : resourceUrls(body.toString());
        receipt.rows.push({ route, encoding, status: response.status, mime: response.headers['content-type'], location: response.headers.location, cacheControl: response.headers['cache-control'] || null, wireBytes: response.wire.length, decodedBytes: body.length, upstreamSha256: response.headers['x-v2-fixture-body-sha256'], decodedSha256: sha(body), resources, redirectFollowed: false });
      }
    }
    const native = require('./native-assets.cjs');
    const observed = [...new Set(receipt.rows.flatMap(row => row.resources || []))];
    receipt.nativeStatic.observedResourceCoverage = observed.flatMap(url => {
      const pathname = decodeURIComponent(new URL(url).pathname);
      const area = native.AREAS.find(item => pathname.startsWith(item.url));
      if (!area) return [];
      const relative = pathname.slice(area.url.length);
      const file = receipt.nativeStatic.files.find(item => item.area === area.key && item.path === relative);
      assert.ok(file, 'Observed native frontend asset is not in the verified static snapshot: ' + pathname);
      return [{ url, area: area.key, sourceSha256: file.sha256 }];
    });
    assert.ok(receipt.nativeStatic.observedResourceCoverage.length >= 5, 'Native frontend resource coverage must include current emitted scripts/styles');
    const ordinary = await request('/', 'gzip', false);
    ordinaryResponse(ordinary);
    receipt.diagnosticHeaderAbsentOnOrdinaryRequest = true;
    receipt.status = 'PASS';
  } catch (error) {
    receipt.status = 'FAIL';
    receipt.error = error.stack;
    throw error;
  } finally {
    receipt.completedAt = new Date().toISOString();
    write();
  }
  return receipt;
}
module.exports = { nativeMountProof, nativeResponse, localUrl, decode, resourceUrls, htmlStatus, ordinaryResponse, rangeProof, assetInventory, request, verify };
if (require.main === module) {
  const output = process.argv[2];
  if (!output) throw new Error('Pass a unique artifact receipt path; previous evidence should be retained.');
  verify(path.resolve(output)).then(r => console.log(r.status, r.rows.length, 'response proofs')).catch(error => { console.error(error.message); process.exitCode = 1; });
}
