'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { privateIPv4, parseLookup, resolveOrigin, originProof } = require('./origin-ipv4.cjs');
const records = (host, ip = '192.168.65.254') => `${ip} STREAM ${host}\n${ip} DGRAM\n${ip} RAW\n`;

test('only canonical private IPv4 addresses are accepted', () => {
  for (const ip of ['10.2.3.4', '172.16.0.2', '172.31.255.2', '192.168.65.254']) assert.equal(privateIPv4(ip), ip);
  for (const ip of ['127.0.0.1', '169.254.1.2', '8.8.8.8', '172.32.0.1', '172.15.1.2', '0.0.0.0', 'fdc4:f303:9324::254', '::ffff:192.168.65.254', '192.168.065.254', '192.168.1.256', '192.168.1.2;echo bad']) assert.throws(() => privateIPv4(ip));
});
test('getent permits repeated socket records but rejects empty, ambiguous and malformed DNS', () => {
  assert.equal(parseLookup(records('host.docker.internal'), 'host.docker.internal'), '192.168.65.254');
  for (const output of ['', '  ', records('other.host'), records('host.docker.internal') + '10.0.0.1 STREAM\n', '192.168.65.254 UNKNOWN', '192.168.65.254 STREAM host.docker.internal extra', 'fdc4:f303:9324::254 STREAM']) assert.throws(() => parseLookup(output, 'host.docker.internal'));
});
test('startup performs one pinned unprivileged mountless AF_INET lookup and propagates failure', () => {
  const image = 'nginx@sha256:' + 'a'.repeat(64);
  let count = 0;
  const execute = (binary, args, options) => {
    count++;
    assert.equal(binary, 'docker');
    assert.deepEqual(args, ['run', '--rm', '--read-only', '--user', '101:101', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--entrypoint', 'getent', image, 'ahostsv4', 'host.docker.internal']);
    assert.equal(options.timeout, 15000);
    return records('host.docker.internal');
  };
  assert.equal(resolveOrigin(image, execute), '192.168.65.254');
  assert.equal(count, 1);
  assert.throws(() => resolveOrigin('nginx:latest', execute));
  assert.throws(() => resolveOrigin(image, () => { throw new Error('DNS unavailable'); }), /DNS unavailable/);
});
test('live proof binds the sole alias override to IPv4 and all-address lookups', () => {
  const container = { HostConfig: { ExtraHosts: ['v2-php-origin:192.168.65.254'] } };
  const good = records('v2-php-origin');
  assert.equal(originProof(container, good, good).address, '192.168.65.254');
  for (const extras of [null, [], ['other:192.168.65.254'], ['v2-php-origin:192.168.65.254', 'other:10.0.0.1'], ['v2-php-origin:8.8.8.8'], ['v2-php-origin:fdc4::1']]) assert.throws(() => originProof({ HostConfig: { ExtraHosts: extras } }, good, good));
  assert.throws(() => originProof(container, records('v2-php-origin', '10.0.0.1'), good));
  assert.throws(() => originProof(container, good, good + 'fdc4:f303:9324::254 STREAM\n'));
});
