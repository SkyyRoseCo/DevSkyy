'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

test('ordinary unit verification excludes the opt-in Kids browser runner', () => {
  const files = fs.readdirSync(__dirname);
  const discovered = files.filter(name => /^test-.*\.cjs$/.test(name));
  assert(files.includes('run-kids-arrival-browser.cjs'));
  assert(!discovered.includes('test-kids-arrival-browser.cjs'));
  const pkg = JSON.parse(fs.readFileSync(path.join(__dirname, '../../wordpress-theme/skyyrose-flagship-2/package.json'), 'utf8'));
  assert(pkg.scripts.verify.includes('node --test ../../tools/v2-runtime/test-*.cjs'));
  assert(!pkg.scripts.verify.includes('run-kids-arrival-browser.cjs'));
  assert.equal(pkg.scripts['qualify:kids-arrival'], 'node ../../tools/v2-runtime/run-kids-arrival-browser.cjs');
});
