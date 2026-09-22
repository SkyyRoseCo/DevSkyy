const fs = require('node:fs');
const path = require('node:path');
const { createRequire } = require('node:module');

const repoRoot = path.resolve(__dirname, '../../..');
const requestedBase = process.env.V2_BASE_URL || 'http://127.0.0.1:18303';
const url = new URL(requestedBase);
if (
  url.protocol !== 'http:' ||
  url.hostname !== '127.0.0.1' ||
  url.username ||
  url.password ||
  url.pathname !== '/' ||
  url.search ||
  url.hash
) {
  throw new Error('V2_BASE_URL must be a local http://127.0.0.1:<port> origin.');
}
const base = url.origin;
const out = path.resolve(process.env.V2_ARTIFACT_DIR || path.join(repoRoot, '.artifacts/v2-phase3b-20260905'));
fs.mkdirSync(out, { recursive: true });
const qaPackage = process.env.V2_QA_PACKAGE
  ? path.resolve(process.env.V2_QA_PACKAGE)
  : path.join(__dirname, 'package.json');
const dependencyRequire = createRequire(qaPackage);
function requireQa(id) {
  if (!fs.existsSync(qaPackage)) {
    throw new Error(
      'QA package is missing. Install this directory or set V2_QA_PACKAGE to an installed QA package.json.'
    );
  }
  return dependencyRequire(id);
}
requireQa.resolve = id => dependencyRequire.resolve(id);

function validateLabel(label) {
  if (!label || !/^[a-zA-Z0-9][a-zA-Z0-9._-]*$/.test(label)) {
    throw new Error(
      'Artifact label must contain only letters, digits, dots, underscores or hyphens and start with a letter or digit.'
    );
  }
}
function validateSurface(label, route) {
  validateLabel(label);
  if (!route || !route.startsWith('/') || new URL(route, base).origin !== base) {
    throw new Error('A local route beginning with / is required.');
  }
}

module.exports = { requireQa, base, out, validateLabel, validateSurface };
