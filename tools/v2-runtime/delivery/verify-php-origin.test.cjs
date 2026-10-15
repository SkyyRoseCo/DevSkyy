'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { verifyProfile } = require('./verify-php-origin.cjs');
const valid = () => ({ pid: 123, sapi: 'cli-server', xdebug_modes: [], opcache_enabled: true, settings: { 'opcache.validate_timestamps': '1', 'opcache.revalidate_freq': '0', 'opcache.revalidate_path': '1', 'realpath_cache_size': '0' } });
test('same-worker profile rejects coverage, stale timestamp policies and mismatched ownership', () => {
  verifyProfile(valid(), 123);
  for (const change of [p => { p.pid = 124; }, p => { p.xdebug_modes = ['coverage']; }, p => { p.opcache_enabled = false; }, p => { p.settings['opcache.revalidate_freq'] = '2'; }, p => { p.settings['opcache.validate_timestamps'] = '0'; }, p => { p.settings.realpath_cache_size = '4096K'; }]) {
    const profile = valid(); change(profile); assert.throws(() => verifyProfile(profile, 123));
  }
});
