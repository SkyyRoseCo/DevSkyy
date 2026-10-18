#!/usr/bin/env node
// Build-time/local inspection only: deployed routes consume the sanitized snapshot.
import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { homedir } from 'node:os';

const frontend = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const god = process.env.GOD_MODE_SOURCE_ROOT || join(homedir(), 'Developer/god-mode-x');
const fashion = process.env.FASHION_TEAM_SOURCE_ROOT || join(homedir(), 'plugins/fashion-theme-team');
const destination = join(frontend, 'app/admin/god-mode/registry.generated.json');
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const read = path => JSON.parse(readFileSync(path, 'utf8'));
if (process.argv.includes('--check-build') && (!existsSync(god) || !existsSync(fashion))) {
  const snapshot = read(destination);
  const vendor = resolve(frontend, '../plugins/fashion-theme-team');
  const manifestRelative = 'skills/fashion-theme-team/references/skyyrose-skill-migration.json';
  const manifest = read(join(vendor, manifestRelative));
  if (snapshot.schemaVersion !== 1 || !Number.isFinite(Date.parse(snapshot.generatedAt)) || !snapshot.skills.length) throw new Error('Missing or invalid GOD MODE snapshot.');
  if (hash(readFileSync(join(vendor, manifestRelative))) !== snapshot.generation.sourceHashes.migration || hash(readFileSync(join(vendor, '.codex-plugin/plugin.json'))) !== snapshot.generation.sourceHashes.fashionManifest) throw new Error('Bundled Fashion source changed since GOD MODE snapshot. Refresh the snapshot at its canonical source.');
  if (manifest.skills.length !== snapshot.skills.length) throw new Error('Snapshot skill inventory drift.');
  for (const skill of manifest.skills) {
    const bound = snapshot.skills.find(entry => entry.id === skill.id);
    if (!bound || bound.sha256 !== skill.sha256 || hash(readFileSync(checkedRelative(vendor, skill.target))) !== bound.sha256) throw new Error('Bundled migrated skill source drift.');
    verifySkillResources(vendor, skill);
  }
  process.stdout.write('PASS: bundled Fashion snapshot bindings; external GOD MODE freshness unavailable on this build host.\n');
  process.exit(0);
}
const skillDirectories = root => readdirSync(join(root, 'skills')).filter(name => existsSync(join(root, 'skills', name, 'SKILL.md'))).sort();
const plugin = root => read(join(root, '.codex-plugin/plugin.json'));
const godPlugin = plugin(god);
const fashionPlugin = plugin(fashion);
const migrationRelative = 'skills/fashion-theme-team/references/skyyrose-skill-migration.json';
const migrationPath = join(fashion, migrationRelative);
if (!existsSync(migrationPath)) throw new Error('Run the governed Fashion skill migration before generating its dashboard projection.');
const migration = read(migrationPath);
if (migration.schema_version !== 1 || !Array.isArray(migration.skills) || migration.skills.length === 0) throw new Error('Invalid migration contract.');

function checkedRelative(root, relative) {
  if (typeof relative !== 'string') throw new Error('Missing relative skill source.');
  const path = resolve(root, relative);
  if (!path.startsWith(`${resolve(root)}${sep}`)) throw new Error('Skill source escapes its package.');
  return path;
}

function verifySkillResources(root, skill) {
  for (const [relative, expected] of Object.entries(skill.files || {})) {
    const path = checkedRelative(dirname(checkedRelative(root, skill.target)), relative);
    if (hash(readFileSync(path)) !== expected) throw new Error(`Migrated skill resource drift for ${skill.id}.`);
  }
}

function skillDescription(path) {
  const body = readFileSync(path, 'utf8');
  const front = body.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!front) throw new Error('Skill lacks frontmatter.');
  const lines = front[1].split(/\r?\n/);
  const start = lines.findIndex(line => line.startsWith('description:'));
  if (start < 0) throw new Error('Skill lacks description.');
  const parts = [lines[start].slice(12).trim()];
  for (let i = start + 1; i < lines.length && /^\s+/.test(lines[i]); i++) parts.push(lines[i].trim());
  return parts.join(' ').replace(/^["'>|\s]+|["'\s]+$/g, '').slice(0, 800);
}

const skills = migration.skills.map(skill => {
  const path = checkedRelative(fashion, skill.target);
  const actualHash = hash(readFileSync(path));
  if (actualHash !== skill.sha256) throw new Error(`Migration source drift for ${skill.id}; refresh its contract first.`);
  verifySkillResources(fashion, skill);
  return { id: skill.id, name: skill.id, description: skillDescription(path), category: 'SkyyRose', source: `Fashion Theme Team / ${skill.target}`, sha256: actualHash, status: skill.status };
});
const registryPath = join(god, 'tools/tool-registry.json');
const registry = read(registryPath);
if (registry.schema_version !== 1 || !Array.isArray(registry.entries)) throw new Error('Invalid GOD MODE tool registry.');
const tools = registry.entries.map(entry => ({ id: entry.id, name: entry.id, description: entry.capability, kind: entry.scope, scope: entry.scope === 'HOST_ONLY' ? 'Host connection required' : 'Local workstation tool', status: entry.qualification }));

// Compare actual source and installed package files. These observations do not
// claim a running conversation has reloaded, or a deployed service is connected.
function compareFiles(sourceRoot, targetRoot, relativePaths) {
  return existsSync(targetRoot) && relativePaths.every(relative => {
    const source = join(sourceRoot, relative);
    const target = join(targetRoot, relative);
    return existsSync(target) && hash(readFileSync(source)) === hash(readFileSync(target));
  });
}
function filesUnder(root, prefix) {
  return readdirSync(join(root, prefix), { withFileTypes: true }).flatMap(entry => {
    if (['__pycache__', '.pytest_cache', '.ruff_cache', 'node_modules', '.DS_Store'].includes(entry.name)) return [];
    const relative = join(prefix, entry.name);
    return entry.isDirectory() ? filesUnder(root, relative) : entry.isFile() ? [relative] : [];
  });
}
const godFiles = ['.codex-plugin/plugin.json', ...filesUnder(god, 'skills'), ...filesUnder(god, 'tools')];
const fashionFiles = ['.codex-plugin/plugin.json', ...filesUnder(fashion, 'skills')];
const codexGod = join(homedir(), '.codex/plugins/cache/personal', godPlugin.name, godPlugin.version);
const codexFashion = join(homedir(), '.codex/plugins/cache/personal/fashion-theme-team', fashionPlugin.version);
const synchronization = [
  { target: 'GOD MODE · Codex', status: compareFiles(god, codexGod, godFiles) ? 'MATCH' : 'DRIFT_OR_MISSING', checkedAt: null, detail: `${godFiles.length} selected skill/tool/manifest source files compared with the installed package; conversation reload is separate.` },
  { target: 'Fashion Theme Team · project', status: compareFiles(fashion, resolve(frontend, '../plugins/fashion-theme-team'), fashionFiles) ? 'MATCH' : 'DRIFT_OR_MISSING', checkedAt: null, detail: `${fashionFiles.length} selected skill/manifest source files compared with the project distribution.` },
  { target: 'Fashion Theme Team · Codex', status: compareFiles(fashion, codexFashion, fashionFiles) ? 'MATCH' : 'DRIFT_OR_MISSING', checkedAt: null, detail: `${fashionFiles.length} selected skill/manifest source files compared with the installed distribution.` },
];
const workflow = [
  ['intake', 'Mission and owner direction', 'GOD MODE', 'Scope and permissions'],
  ['route', 'Assign the Fashion Theme Team', 'GOD MODE', 'Current project and canonical package'],
  ['source', 'Resolve canon and exact products', 'Fashion Theme Team', 'SOT and get_product'],
  ['specialists', 'Apply migrated specialist skills', 'Fashion Theme Team', 'Workflow before production'],
  ['review', 'Independent review and evidence', 'Independent reviewer', 'Product, scene and technical checks'],
  ['acceptance', 'Owner acceptance and release', 'Corey', 'Separate production and publication authority'],
].map(([id, label, owner, gate]) => ({ id, label, owner, gate }));
const projection = {
  schemaVersion: 1,
  generatedAt: '',
  generation: { command: 'npm run sync:god-mode', sourceRevision: null, sourceHashes: { godModeManifest: hash(readFileSync(join(god, '.codex-plugin/plugin.json'))), fashionManifest: hash(readFileSync(join(fashion, '.codex-plugin/plugin.json'))), migration: hash(readFileSync(migrationPath)), toolRegistry: hash(readFileSync(registryPath)) } },
  orchestrator: { name: 'GOD MODE', version: godPlugin.version, status: 'SOURCE_SNAPSHOT', skillCount: skillDirectories(god).length, mcpToolCount: tools.filter(tool => tool.kind === 'LOCAL').length, cliVersion: readFileSync(join(god, 'agent-harness/cli_anything/godmodex/__init__.py'), 'utf8').match(/__version__\s*=\s*['"]([^'"]+)/)?.[1] || 'Unrecorded' },
  team: { name: 'Fashion Theme Team', version: fashionPlugin.version, controller: 'GOD MODE', skillCount: skillDirectories(fashion).length },
  skills, tools, workflow, synchronization,
  limitations: ['Live runtime connection and allowed actions are established only by the authenticated execution panel above; this catalog is a source snapshot.', 'The workstation runtime provides source-audit, campaign-readiness and fashion-verification. LLM specialist execution and creative-provider dispatch remain unqualified.', 'No generation, provider spending, publishing or deployment is authorized by this source snapshot.', 'Current film production holds and exact-artwork review requirements remain in force.', 'The campaign OODA operational overlay remains project-bound; its canonical entrypoint belongs to Fashion Theme Team.', 'Synchronization is a build-time file comparison, not proof of a running worker or refreshed host conversation.'],
};
if (tools.some(tool => !['LOCAL', 'HOST_ONLY'].includes(tool.kind))) throw new Error('Unknown tool scope.');
const serialized = JSON.stringify(projection);
if (['/Users/', '/private/', '/tmp/', 'file://', '.env', 'access_token', 'api_key'].some(value => serialized.includes(value))) throw new Error('Dashboard projection contains private source details.');
const old = existsSync(destination) ? read(destination) : null;
const comparable = value => JSON.stringify({ ...value, generatedAt: '' });
if (process.argv.includes('--check') || process.argv.includes('--check-build')) {
  if (!old || comparable(old) !== comparable(projection)) throw new Error('GOD MODE dashboard projection is stale. Run npm run sync:god-mode.');
  process.stdout.write(`PASS: ${skills.length} migrated skills, ${tools.length} tool references; current source bindings match.\n`);
} else {
  projection.generatedAt = old && comparable(old) === comparable(projection) ? old.generatedAt : new Date().toISOString();
  mkdirSync(dirname(destination), { recursive: true });
  writeFileSync(destination, `${JSON.stringify(projection, null, 2)}\n`);
  process.stdout.write(`Wrote GOD MODE dashboard projection: ${skills.length} migrated skills, ${tools.length} tool references.\n`);
}
