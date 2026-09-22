'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const zlib = require('node:zlib');
const { AREAS, publicPath, prepare, verifySnapshot } = require('./native-assets.cjs');
const { nativeMountProof, nativeResponse } = require('./verify.cjs');
function fixture(t) {
  const root = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), 'v2-native-static-')));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const wp = path.join(root, '.artifacts/wordpress');
  function put(relative, bytes) {
    const file = path.join(wp, relative);
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, bytes);
  }
  put('wp-load.php', '<?php');
  put('wp-content/mu-plugins/local-isolation.php', '<?php');
  put('wp-includes/version.php', "<?php $wp_version = '7.1';");
  put('wp-content/plugins/woocommerce/woocommerce.php', '<?php\n * Version: 11.1.0\n');
  for (const area of AREAS) {
    put(area.relative + '/public.js', 'window.fixture = 1;\n'.repeat(30));
    put(area.relative + '/index.php', '<?php private');
    put(area.relative + '/private.json', '{"private":true}');
    put(area.relative + '/.hidden.js', 'hidden');
  }
  put('wp-includes/fonts/dashicons.woff2', Buffer.from([0, 1, 2, 3]));
  return { wp, storage: path.join(root, 'snapshots'), put };
}
test('public allowlist excludes executables/private/ambiguous paths and supports actual comma font name', () => {
  for (const name of ['nested/app.min.js', 'font/Inter-VariableFont_slnt,wght.woff2', 'dashicons.ttf', 'image.svg']) assert.ok(publicPath(name));
  for (const name of ['index.php', 'private.json', 'app.js.map', '../app.js', '.private.js', 'x/.private/app.js', 'a%2fapp.js', 'a\\app.js']) assert.equal(publicPath(name), false, name);
});
test('snapshot is deterministic exact bytes, contains no PHP/JSON and has readable mount permissions', t => {
  const f = fixture(t);
  const manifest = prepare(f.wp, f.storage);
  assert.deepEqual(prepare(f.wp, f.storage), manifest);
  assert.equal(manifest.sourceVersions.wordpress, '7.1');
  assert.equal(manifest.sourceVersions.woocommerce, '11.1.0');
  assert.equal(fs.statSync(manifest.snapshot).mode & 0o777, 0o755);
  for (const area of AREAS) {
    assert.equal(fs.existsSync(path.join(manifest.snapshot, area.key, 'index.php')), false);
    assert.equal(fs.existsSync(path.join(manifest.snapshot, area.key, 'private.json')), false);
    assert.deepEqual(fs.readFileSync(path.join(manifest.snapshot, area.key, 'public.js')), fs.readFileSync(path.join(f.wp, area.relative, 'public.js')));
  }
  assert.doesNotThrow(() => verifySnapshot(manifest));
});
test('source/snapshot/dangling output symlinks are rejected', t => {
  const f = fixture(t);
  fs.symlinkSync(path.join(f.wp, 'wp-load.php'), path.join(f.wp, AREAS[0].relative, 'escape.js'));
  assert.throws(() => prepare(f.wp, f.storage), /symlink/i);
  fs.unlinkSync(path.join(f.wp, AREAS[0].relative, 'escape.js'));
  const manifest = prepare(f.wp, f.storage);
  fs.symlinkSync('/nonexistent-private-target', path.join(manifest.snapshot, AREAS[0].key, 'escape.js'));
  assert.throws(() => prepare(f.wp, f.storage), /symlink/i);
});
test('mount proof binds every copied source byte, all four destinations, read-only and no extra mounts', t => {
  const f = fixture(t);
  const manifest = prepare(f.wp, f.storage);
  const container = { Mounts: AREAS.map(area => ({ Destination: area.destination, Source: path.join(manifest.snapshot, area.key), RW: false })) };
  assert.equal(nativeMountProof(container, f.wp, f.storage).mounts.length, 4);
  container.Mounts[0].RW = true;
  assert.throws(() => nativeMountProof(container, f.wp, f.storage), /read-only/);
  container.Mounts[0].RW = false;
  container.Mounts.push({ Destination: '/private', Source: f.wp, RW: false });
  assert.throws(() => nativeMountProof(container, f.wp, f.storage), /Unexpected/);
  container.Mounts.pop();
  f.put(AREAS[0].relative + '/public.js', 'changed');
  assert.throws(() => nativeMountProof(container, f.wp, f.storage), /current fixture/);
});
test('HTTP native proof rejects status/MIME/gzip/source mismatch and accepts exact identity/gzip', () => {
  const source = Buffer.from('window.exactNative = true;\n'.repeat(100));
  const headers = { 'content-type': 'application/javascript', 'content-encoding': 'gzip', vary: 'Accept-Encoding' };
  const response = { status: 200, headers, wire: zlib.gzipSync(source) };
  assert.doesNotThrow(() => nativeResponse(response, source, /javascript/, 'gzip'));
  assert.doesNotThrow(() => nativeResponse({ status: 200, headers: { 'content-type': 'text/javascript' }, wire: source }, source, /javascript/, 'identity'));
  assert.throws(() => nativeResponse({ ...response, status: 504 }, source, /javascript/, 'gzip'));
  assert.throws(() => nativeResponse(response, Buffer.from('drift'), /javascript/, 'gzip'));
  assert.throws(() => nativeResponse(response, source, /text\/css/, 'gzip'));
  assert.throws(() => nativeResponse({ ...response, headers: { ...headers, vary: '' } }, source, /javascript/, 'gzip'));
});

test('mismatched worker fixture fails before snapshot mutation; canonical aliases match', t => {
  const { matchingFixture, prepareForWorker } = require('./native-assets.cjs');
  const first = fixture(t);
  const second = fixture(t);
  assert.throws(() => matchingFixture(second.wp, first.wp), /owned PHP worker/);
  assert.throws(() => prepareForWorker(second.wp, first.wp, second.storage), /owned PHP worker/);
  assert.equal(fs.existsSync(second.storage), false, 'Mismatch must not create snapshot storage');
  const alias = path.join(path.dirname(first.wp), 'wordpress-alias');
  fs.symlinkSync(first.wp, alias);
  assert.equal(matchingFixture(alias, first.wp), fs.realpathSync(first.wp));
});

test('restrictive umask produces traversable generated trees and tampered permissions fail closed', t => {
  const f = fixture(t);
  f.put('wp-includes/js/nested/deeper/public.js', 'window.nested = true;');
  const sourceDirectory = path.join(f.wp, 'wp-includes/js/nested');
  fs.chmodSync(sourceDirectory, 0o700);
  const previous = process.umask(0o077);
  let manifest;
  try { manifest = prepare(f.wp, f.storage); }
  finally { process.umask(previous); }
  assert.equal(fs.statSync(sourceDirectory).mode & 0o777, 0o700, 'Source directory permissions must remain unchanged');
  for (const relative of ['core-js', 'core-js/nested', 'core-js/nested/deeper']) assert.equal(fs.statSync(path.join(manifest.snapshot, relative)).mode & 0o777, 0o755);
  const directory = path.join(manifest.snapshot, 'core-js/nested');
  fs.chmodSync(directory, 0o700);
  assert.throws(() => prepare(f.wp, f.storage), /directory permissions/);
  assert.equal(fs.statSync(directory).mode & 0o777, 0o700, 'Existing snapshot drift is rejected, never silently repaired');
  fs.chmodSync(directory, 0o755);
  const file = path.join(directory, 'deeper/public.js');
  fs.chmodSync(file, 0o600);
  assert.throws(() => verifySnapshot(manifest), /file permissions/);
});
