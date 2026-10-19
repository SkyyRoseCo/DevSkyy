'use strict';
// Synthetic private-model module adapter; never enables or loads a mascot.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const theme = path.resolve(__dirname, '../../wordpress-theme/skyyrose-flagship-2');
test('private mascot module tuple consumes shared core and keeps model loaders private', async () => {
  const source = fs.readFileSync(path.join(theme, 'assets/js/skyy-3d.js'), 'utf8');
  const start = source.indexOf('var dependency;');
  const end = source.indexOf('function lightMode()', start);
  assert.ok(start > 0 && end > start);
  assert.doesNotMatch(source.slice(start, end), /window\.skyyRoseLoadThree\s*=/);
  const core = { identity: 'shared-core-synthetic-control' };
  const gltf = { GLTFLoader: class SyntheticGLTF {} };
  const draco = { DRACOLoader: class SyntheticDRACO {} };
  let coreCalls = 0; const imports = [];
  const context = { window: { skyyRoseThreeCore: { load() { coreCalls += 1; return Promise.resolve([core]); } } }, config: { moduleBase: 'http://fixture.invalid/assets/js/lib/three-r170/' }, local: value => value, limited: value => value, mockImport: async url => { imports.push(url); return url.endsWith('GLTFLoader.js') ? gltf : draco; } };
  // Only the native import mechanism is adapted; the exact private resolver runs.
  vm.runInNewContext(source.slice(start, end).replaceAll('import(', 'mockImport('), context);
  const first = await context.loadThree(); const second = await context.loadThree();
  assert.equal(first, second); assert.equal(coreCalls, 1);
  assert.equal(first[0], core); assert.equal(first[1], gltf); assert.equal(first[2], draco);
  assert.equal(imports.length, 2); assert.ok(imports.every(url => /(?:GLTFLoader|DRACOLoader)\.js$/.test(url)));
});
