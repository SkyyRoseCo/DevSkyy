'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const http = require('node:http');
const { execFileSync } = require('node:child_process');
const sha = value => crypto.createHash('sha256').update(value).digest('hex');
function verifyProfile(profile, pid) {
  assert.equal(profile.pid, pid);
  assert.equal(profile.sapi, 'cli-server');
  assert.deepEqual(profile.xdebug_modes, []);
  assert.equal(profile.opcache_enabled, true);
  for (const [key, expected] of Object.entries({ 'opcache.validate_timestamps': '1', 'opcache.revalidate_freq': '0', 'opcache.revalidate_path': '1', 'realpath_cache_size': '0' })) assert.equal(profile.settings[key], expected, key);
}
async function prove(output) {
  const repo = path.resolve(__dirname, '../../..');
  const state = path.join(repo, '.artifacts/v2-delivery-20260906/php-origin');
  const receipt = { status: 'RUNNING', runId: crypto.randomUUID(), startedAt: new Date().toISOString() };
  const write = () => { fs.mkdirSync(path.dirname(output), { recursive: true }); fs.writeFileSync(output, JSON.stringify(receipt, null, 2) + '\n'); };
  write();
  let diagnostic;
  let diagnosticCreated = false;
  try {
    execFileSync(path.join(__dirname, 'php-origin.sh'), ['status']);
    const fixture = fs.realpathSync(fs.readFileSync(path.join(state, 'fixture'), 'utf8').trim());
    assert.ok(fixture.startsWith(repo + '/.artifacts/') && fixture.endsWith('/wordpress'));
    assert.ok(fs.existsSync(path.join(fixture, 'wp-content/mu-plugins/local-isolation.php')));
    const pid = Number(fs.readFileSync(path.join(state, 'pid'), 'utf8'));
    const token = crypto.randomBytes(32).toString('hex');
    diagnostic = path.join(fixture, 'wp-content/mu-plugins/v2-worker-proof-' + receipt.runId + '.php');
    // Base64 safely quotes this known local path in PHP without shell interpolation.
    const fixture64 = Buffer.from(fixture).toString('base64');
    const code = `<?php
if (!defined('ABSPATH') || realpath(ABSPATH) !== base64_decode('${fixture64}') || ($_SERVER['HTTP_HOST'] ?? '') !== '127.0.0.1:18308' || ($_SERVER['SERVER_PORT'] ?? '') != '18309' || !hash_equals('${token}', $_SERVER['HTTP_X_V2_WORKER_PROOF'] ?? '')) { return; }
$status = opcache_get_status(false);
$settings = [];
foreach (['opcache.validate_timestamps','opcache.revalidate_freq','opcache.revalidate_path','realpath_cache_size','opcache.enable','opcache.enable_cli','opcache.use_cwd','opcache.save_comments','opcache.enable_file_override','opcache.jit'] as $key) { $settings[$key] = ini_get($key); }
header('Content-Type: application/json'); header('Cache-Control: no-store');
echo json_encode(['pid'=>getmypid(),'sapi'=>PHP_SAPI,'php'=>PHP_VERSION,'xdebug_modes'=>function_exists('xdebug_info') ? xdebug_info('mode') : [],'opcache_version'=>phpversion('Zend OPcache'),'xdebug_version'=>phpversion('xdebug'),'opcache_enabled'=>$status['opcache_enabled'] ?? false,'cached_scripts'=>$status['opcache_statistics']['num_cached_scripts'] ?? 0,'settings'=>$settings,'ini_file'=>php_ini_loaded_file()]); exit;
`;
    fs.writeFileSync(diagnostic, code, { flag: 'wx' });
    diagnosticCreated = true;
    const profile = await new Promise((resolve, reject) => {
      const req = http.get({ hostname: '127.0.0.1', port: 18309, path: '/', headers: { Host: '127.0.0.1:18308', 'X-V2-Worker-Proof': token } }, res => {
        let body = '';
        res.on('data', chunk => { body += chunk; if (body.length > 16384) res.destroy(new Error('Bounded worker proof exceeded')); });
        res.on('error', reject);
        res.on('end', () => { try { assert.equal(res.statusCode, 200); resolve(JSON.parse(body)); } catch (error) { reject(error); } });
      });
      req.setTimeout(10000, () => req.destroy(new Error('Worker proof timed out')));
      req.on('error', reject);
    });
    verifyProfile(profile, pid);
    const binary = fs.readFileSync(path.join(state, 'binary'), 'utf8').trim();
    const router = fs.readFileSync(path.join(state, 'router'), 'utf8').trim();
    receipt.profile = profile;
    receipt.binary = { path: binary, sha256: sha(fs.readFileSync(binary)), version: execFileSync(binary, ['-v'], { env: { ...process.env, XDEBUG_MODE: 'off' }, encoding: 'utf8' }).trim() };
    receipt.fixture = fixture;
    receipt.router = { path: router, sha256: sha(fs.readFileSync(router)) };
    receipt.iniSha256 = sha(fs.readFileSync(profile.ini_file));
    receipt.launcherSha256 = sha(fs.readFileSync(path.join(__dirname, 'php-origin.sh')));
    receipt.processIdentity = fs.readFileSync(path.join(state, 'identity'), 'utf8').trim();
    receipt.environmentOverride = { XDEBUG_MODE: 'off' };
    receipt.status = 'PASS';
  } catch (error) { receipt.status = 'FAIL'; receipt.error = error.stack; throw error; }
  finally {
    if (diagnosticCreated && fs.existsSync(diagnostic)) fs.unlinkSync(diagnostic);
    receipt.diagnosticRemoved = !diagnostic || !fs.existsSync(diagnostic);
    receipt.finishedAt = new Date().toISOString();
    write();
  }
  return receipt;
}
module.exports = { verifyProfile, prove };
if (require.main === module) {
  assert.ok(process.argv[2], 'Pass a unique artifact receipt path');
  prove(path.resolve(process.argv[2])).then(receipt => console.log(receipt.status, receipt.profile.php)).catch(error => { console.error(error.message); process.exitCode = 1; });
}
