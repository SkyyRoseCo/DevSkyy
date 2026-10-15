'use strict';
/** Build a byte-identical public-only snapshot; never mount native PHP/JSON. */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const REPO = path.resolve(__dirname, '../../..');
const AREAS = [
  { key: 'core-js', relative: 'wp-includes/js', url: '/wp-includes/js/', destination: '/srv/v2-core-js' },
  { key: 'core-css', relative: 'wp-includes/css', url: '/wp-includes/css/', destination: '/srv/v2-core-css' },
  { key: 'core-fonts', relative: 'wp-includes/fonts', url: '/wp-includes/fonts/', destination: '/srv/v2-core-fonts' },
  { key: 'woo-assets', relative: 'wp-content/plugins/woocommerce/assets', url: '/wp-content/plugins/woocommerce/assets/', destination: '/srv/v2-woo-assets' },
];
const PUBLIC = /\.(?:css|js|wasm|png|jpg|jpeg|webp|avif|svg|gif|ico|woff2?|ttf|eot|otf)$/;
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
function noLinks(file) {
  for (let item = file; ; item = path.dirname(item)) {
    try { assert.equal(fs.lstatSync(item).isSymbolicLink(), false, 'Symlink path: ' + item); }
    catch (error) { if (error.code !== 'ENOENT') throw error; }
    if (path.dirname(item) === item) break;
  }
}
function publicPath(relative) {
  return relative.split('/').every(part => /^[A-Za-z0-9_][A-Za-z0-9_.,-]*$/.test(part)) && PUBLIC.test(relative);
}
function fixtureRoot(value) {
  assert.ok(value, 'V2_WP_FIXTURE is required');
  const root = fs.realpathSync(value);
  assert.ok(root.includes(path.sep + '.artifacts' + path.sep), 'Only the existing isolated artifact fixture is allowed');
  for (const file of ['wp-load.php', 'wp-content/mu-plugins/local-isolation.php']) assert.ok(fs.statSync(path.join(root, file)).isFile(), 'Missing fixture guard: ' + file);
  return root;
}
function matchingFixture(expected, workerFixture) {
  const fixture = fixtureRoot(expected);
  assert.equal(fixture, fs.realpathSync(workerFixture), 'Native asset fixture must equal the owned PHP worker fixture');
  return fixture;
}
function prepareForWorker(expected, workerFixture, storage) {
  // Validate before prepare() can create any snapshot directory or receipt.
  return prepare(matchingFixture(expected, workerFixture), storage);
}
function versions(fixture) {
  noLinks(path.join(fixture, 'wp-includes/version.php'));
  noLinks(path.join(fixture, 'wp-content/plugins/woocommerce/woocommerce.php'));
  const core = fs.readFileSync(path.join(fixture, 'wp-includes/version.php'));
  const woo = fs.readFileSync(path.join(fixture, 'wp-content/plugins/woocommerce/woocommerce.php'));
  const wordpress = core.toString().match(/\$wp_version\s*=\s*'([^']+)'/)?.[1];
  const woocommerce = woo.toString().match(/^[ \t*]*Version:\s*(\S+)/m)?.[1];
  assert.ok(wordpress && woocommerce, 'Expected official installed version headers');
  return { wordpress, woocommerce, coreVersionFileSha256: sha(core), wooBootstrapSha256: sha(woo) };
}
function census(fixture) {
  const rows = [];
  for (const area of AREAS) {
    const source = path.join(fixture, area.relative);
    noLinks(source);
    function walk(directory) {
      for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
        const file = path.join(directory, entry.name);
        assert.equal(entry.isSymbolicLink(), false, 'Native asset symlink: ' + file);
        if (entry.isDirectory()) walk(file);
        else if (entry.isFile()) {
          const relative = path.relative(source, file).split(path.sep).join('/');
          if (!publicPath(relative)) continue;
          const bytes = fs.readFileSync(file);
          rows.push({ area: area.key, path: relative, bytes: bytes.length, sha256: sha(bytes) });
        }
      }
    }
    walk(source);
  }
  return rows.sort((a, b) => (a.area + '/' + a.path).localeCompare(b.area + '/' + b.path));
}
function publicDirectory(root, directory) {
  const relative = path.relative(root, directory);
  assert.ok(relative === '' || (!relative.startsWith('..') && !path.isAbsolute(relative)), 'Directory must belong to the new snapshot');
  fs.mkdirSync(directory, { recursive: true });
  // chmod only our freshly generated tree, never the fixture or storage parent.
  for (let item = directory; ; item = path.dirname(item)) {
    fs.chmodSync(item, 0o755);
    if (item === root) break;
  }
}
function verifySnapshot(manifest) {
  noLinks(manifest.snapshot);
  assert.equal(fs.statSync(manifest.snapshot).mode & 0o777, 0o755, 'Snapshot directory permissions must be 0755');
  for (const area of AREAS) {
    const root = path.join(manifest.snapshot, area.key);
    noLinks(root);
    const expected = manifest.files.filter(row => row.area === area.key);
    const actual = [];
    function walk(directory) {
      assert.equal(fs.statSync(directory).mode & 0o777, 0o755, 'Snapshot directory permissions must be 0755');
      for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
        const file = path.join(directory, entry.name);
        assert.equal(entry.isSymbolicLink(), false, 'Snapshot symlink');
        if (entry.isDirectory()) walk(file);
        else {
          const relative = path.relative(root, file).split(path.sep).join('/');
          assert.ok(entry.isFile() && publicPath(relative), 'Non-public snapshot file');
          assert.equal(fs.statSync(file).mode & 0o777, 0o644, 'Snapshot file permissions must be 0644');
          actual.push(relative);
        }
      }
    }
    walk(root);
    assert.deepEqual(actual.sort(), expected.map(row => row.path).sort(), 'Snapshot file set drift');
    for (const row of expected) {
      const bytes = fs.readFileSync(path.join(root, row.path));
      assert.equal(bytes.length, row.bytes);
      assert.equal(sha(bytes), row.sha256, 'Snapshot content drift');
    }
  }
}
function prepare(value, storage = path.join(REPO, '.artifacts/v2-delivery-20260906/native-static')) {
  const fixture = fixtureRoot(value);
  noLinks(storage);
  const files = census(fixture);
  assert.ok(AREAS.every(area => files.some(row => row.area === area.key)), 'Every native public area must contain files');
  const sourceVersions = versions(fixture);
  const identity = sha(JSON.stringify({ fixture, sourceVersions, files }));
  const snapshot = path.join(storage, identity);
  const manifest = { schema: 'skyyrose.native-static.v1', fixture, snapshot, identity, sourceVersions, areas: AREAS, files };
  fs.mkdirSync(storage, { recursive: true });
  if (!fs.existsSync(snapshot)) {
    const temporary = fs.mkdtempSync(path.join(storage, '.prepare-'));
    try {
      fs.chmodSync(temporary, 0o755);
      for (const area of AREAS) publicDirectory(temporary, path.join(temporary, area.key));
      for (const row of files) {
        const area = AREAS.find(item => item.key === row.area);
        const source = path.join(fixture, area.relative, row.path);
        noLinks(source);
        const bytes = fs.readFileSync(source);
        assert.equal(sha(bytes), row.sha256, 'Source changed during snapshot');
        const target = path.join(temporary, row.area, row.path);
        publicDirectory(temporary, path.dirname(target));
        fs.writeFileSync(target, bytes, { flag: 'wx', mode: 0o644 });
        fs.chmodSync(target, 0o644);
      }
      noLinks(snapshot);
      fs.renameSync(temporary, snapshot);
    } finally { if (fs.existsSync(temporary)) fs.rmSync(temporary, { recursive: true }); }
  }
  verifySnapshot(manifest);
  // Receipt is outside the mounted directories, never available through HTTP.
  const receipt = snapshot + '.json';
  noLinks(receipt);
  const payload = JSON.stringify(manifest, null, 2) + '\n';
  if (fs.existsSync(receipt)) assert.equal(fs.readFileSync(receipt, 'utf8'), payload, 'Snapshot receipt drift');
  else fs.writeFileSync(receipt, payload, { flag: 'wx' });
  return manifest;
}
module.exports = { AREAS, publicPath, fixtureRoot, matchingFixture, prepareForWorker, versions, census, verifySnapshot, prepare, sha };
if (require.main === module) {
  const state = path.join(REPO, '.artifacts/v2-delivery-20260906/php-origin/fixture');
  const workerFixture = fs.readFileSync(state, 'utf8').trim();
  const manifest = prepareForWorker(process.env.V2_WP_FIXTURE, workerFixture);
  process.stdout.write(manifest.snapshot + '\n');
}
