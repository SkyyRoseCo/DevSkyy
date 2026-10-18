import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { cpSync, mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const directory = dirname(fileURLToPath(import.meta.url));
function fixture() {
  const root = mkdtempSync(join(tmpdir(), 'god-mode-projection-'));
  const frontend = join(root, 'frontend');
  const god = join(root, 'god');
  const fashion = join(root, 'fashion');
  const write = (path, value) => { mkdirSync(dirname(path), { recursive: true }); writeFileSync(path, typeof value === 'string' ? value : JSON.stringify(value)); };
  const skill = '---\nname: skyyrose-test\ndescription: Source-bound offline example\n---\n# Example\n';
  write(join(god, '.codex-plugin/plugin.json'), { name: 'projection-test-not-installed', version: 'test' });
  write(join(god, 'skills/control/SKILL.md'), skill);
  write(join(god, 'agent-harness/cli_anything/godmodex/__init__.py'), '__version__ = "test"\n');
  write(join(god, 'tools/tool-registry.json'), { schema_version: 1, entries: [{ id: 'test', capability: 'Local inspection', scope: 'LOCAL', qualification: 'SOURCE_ONLY' }] });
  write(join(fashion, '.codex-plugin/plugin.json'), { name: 'fashion-theme-team', version: 'projection-test' });
  write(join(fashion, 'skills/skyyrose-test/SKILL.md'), skill);
  const migrationPath = join(fashion, 'skills/fashion-theme-team/references/skyyrose-skill-migration.json');
  const migration = { schema_version: 1, skills: [{ id: 'skyyrose-test', target: 'skills/skyyrose-test/SKILL.md', sha256: createHash('sha256').update(skill).digest('hex'), status: 'MIGRATED' }] };
  write(migrationPath, migration);
  mkdirSync(join(frontend, 'scripts'), { recursive: true });
  cpSync(join(directory, 'sync-god-mode.mjs'), join(frontend, 'scripts/sync-god-mode.mjs'));
  const run = (...args) => spawnSync(process.execPath, [join(frontend, 'scripts/sync-god-mode.mjs'), ...args], { encoding: 'utf8', env: { ...process.env, GOD_MODE_SOURCE_ROOT: god, FASHION_TEAM_SOURCE_ROOT: fashion } });
  const portableRun = () => spawnSync(process.execPath, [join(frontend, 'scripts/sync-god-mode.mjs'), '--check-build'], { encoding: 'utf8', env: { ...process.env, GOD_MODE_SOURCE_ROOT: join(root, 'unavailable-god'), FASHION_TEAM_SOURCE_ROOT: join(root, 'unavailable-fashion') } });
  return { root, frontend, god, fashion, run, portableRun, write, migration, migrationPath };
}

test('projection is deterministic, sanitized and detects stale source bindings', () => {
  const f = fixture();
  try {
    assert.equal(f.run().status, 0);
    const output = join(f.frontend, 'app/admin/god-mode/registry.generated.json');
    const first = readFileSync(output, 'utf8');
    assert.equal(f.run('--check').status, 0);
    assert.equal(f.run().status, 0);
    assert.equal(readFileSync(output, 'utf8'), first);
    assert.ok(!first.includes(f.root));
    f.write(join(f.fashion, 'skills/skyyrose-test/SKILL.md'), 'changed');
    assert.notEqual(f.run('--check').status, 0);
    assert.equal(readFileSync(output, 'utf8'), first);
  } finally { rmSync(f.root, { recursive: true, force: true }); }
});

test('migration sources cannot escape the package', () => {
  const f = fixture();
  try {
    f.migration.skills[0].target = '../outside/SKILL.md';
    f.write(f.migrationPath, f.migration);
    const result = f.run();
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /escapes its package/);
  } finally { rmSync(f.root, { recursive: true, force: true }); }
});

test('unknown execution scopes fail closed', () => {
  const f = fixture();
  try {
    f.write(join(f.god, 'tools/tool-registry.json'), { schema_version: 1, entries: [{ id: 'test', capability: 'Local inspection', scope: 'REMOTE_EXECUTOR', qualification: 'SOURCE_ONLY' }] });
    assert.notEqual(f.run().status, 0);
  } finally { rmSync(f.root, { recursive: true, force: true }); }
});

test('portable build validates bundled sources and discloses upstream freshness limit', () => {
  const f = fixture();
  try {
    assert.equal(f.run().status, 0);
    const vendor = join(f.root, 'plugins/fashion-theme-team');
    cpSync(f.fashion, vendor, { recursive: true });
    const valid = f.portableRun();
    assert.equal(valid.status, 0, valid.stderr);
    assert.match(valid.stdout, /freshness unavailable/);
    f.write(join(vendor, 'skills/skyyrose-test/SKILL.md'), 'changed');
    assert.notEqual(f.portableRun().status, 0);
  } finally { rmSync(f.root, { recursive: true, force: true }); }
});
