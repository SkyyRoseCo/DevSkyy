'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const net = require('node:net');
const { execFileSync } = require('node:child_process');
const ALIAS = 'v2-php-origin';
const DOCKER_HOST = 'host.docker.internal';

function privateIPv4(value) {
  assert.equal(net.isIP(value), 4, 'Origin must be a canonical IPv4 address');
  const parts = value.split('.').map(Number);
  assert.ok(parts[0] === 10 || (parts[0] === 172 && parts[1] >= 16 && parts[1] <= 31) ||
    (parts[0] === 192 && parts[1] === 168), 'Origin must be an RFC1918 private IPv4 address');
  return value;
}

function parseLookup(output, hostname) {
  assert.equal(typeof output, 'string');
  const lines = output.trim().split('\n');
  const addresses = new Set();
  for (const line of lines) {
    const fields = line.trim().split(/\s+/);
    assert.ok(fields.length === 2 || fields.length === 3, 'Malformed getent address record');
    assert.ok(['STREAM', 'DGRAM', 'RAW'].includes(fields[1]), 'Unexpected getent socket type');
    if (fields.length === 3) assert.equal(fields[2], hostname, 'Unexpected getent canonical hostname');
    addresses.add(privateIPv4(fields[0]));
  }
  assert.equal(addresses.size, 1, 'Origin lookup must resolve one unique private IPv4 address');
  return [...addresses][0];
}

function resolveOrigin(image, execute = execFileSync) {
  assert.match(image, /^nginx@sha256:[a-f0-9]{64}$/, 'Use the existing pinned official Nginx image');
  const output = execute('docker', ['run', '--rm', '--read-only', '--user', '101:101',
    '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
    '--entrypoint', 'getent', image, 'ahostsv4', DOCKER_HOST],
  { encoding: 'utf8', timeout: 15000, maxBuffer: 65536 });
  return parseLookup(output, DOCKER_HOST);
}

function originProof(container, ipv4Output, allOutput) {
  const overrides = container.HostConfig.ExtraHosts;
  assert.ok(Array.isArray(overrides) && overrides.length === 1, 'Exactly one owned host override is required');
  const match = new RegExp(`^${ALIAS}:([0-9.]+)$`).exec(overrides[0]);
  assert.ok(match, 'Unexpected origin host override');
  const address = privateIPv4(match[1]);
  assert.equal(parseLookup(ipv4Output, ALIAS), address, 'AF_INET alias differs from container override');
  assert.equal(parseLookup(allOutput, ALIAS), address, 'Alias includes an unexpected address family or address');
  return { alias: ALIAS, address, extraHosts: overrides, ahostsv4: ipv4Output, ahosts: allOutput };
}

if (require.main === module) {
  try {
    const image = fs.readFileSync(path.join(__dirname, 'image.txt'), 'utf8').trim();
    process.stdout.write(resolveOrigin(image) + '\n');
  } catch (error) { console.error(error.message); process.exitCode = 1; }
}
module.exports = { ALIAS, DOCKER_HOST, privateIPv4, parseLookup, resolveOrigin, originProof };
